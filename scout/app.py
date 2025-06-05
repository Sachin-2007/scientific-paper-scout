from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator, Dict
from pydantic import BaseModel
import asyncio
import json
import time
import logging
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from model import get_llm_response
from scraper import PaperScraper
from summariser import Summariser

# Configure logging with timestamps and detailed format
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler for INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(console_formatter)

# Create file handler for ERROR and above
file_handler = logging.FileHandler('paperscout.log')
file_handler.setLevel(logging.ERROR)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StreamRequest(BaseModel):
    message: str
    max_results: int = 3

scraper = PaperScraper()
summariser = Summariser()

async def generate_responses(message: str, max_results: int) -> AsyncGenerator[str, None]:
    start_time = time.time()
    logger.info(f"Starting new request - Query: {message}, Max results: {max_results}")
    
    try:
        messages = []
        messages.append(HumanMessage(content=message))
        
        # LLM Tool Call
        logger.info("Initiating LLM tool call")
        llm_start = time.time()
        response, tool = await get_llm_response(messages)
        llm_time = time.time() - llm_start
        logger.info(f"LLM tool call completed in {llm_time:.2f}s")
        
        if tool is not None:
            # Get paper metadata
            yield json.dumps({
                "type": "status",
                "status": "Searching arXiv..."
            }) + "\n"
            
            try:
                # arXiv Search
                logger.info(f"Starting arXiv search with query: {tool['args']['query']}")
                metadata_start = time.time()
                papers = scraper.get_metadata(tool["args"]["query"], max_results)
                metadata_time = time.time() - metadata_start
                logger.info(f"arXiv search completed - Found {len(papers)} papers in {metadata_time:.2f}s")
                
                yield json.dumps({
                    "type": "status",
                    "status": f"Searching arXiv... [{metadata_time:.2f}s]"
                }) + "\n"
                
                # Stream all titles at once
                yield json.dumps({
                    "type": "titles",
                    "papers": [{"title": paper["title"], "url": paper["pdf_url"]} for paper in papers]
                }) + "\n"
                
                # Process and stream summaries
                yield json.dumps({
                    "type": "status",
                    "status": "Downloading and parsing PDFs..."
                }) + "\n"
                
                try:
                    # PDF Processing
                    logger.info("Starting PDF download and parsing")
                    parse_start = time.time()
                    tasks = [scraper.download_and_parse(paper) for paper in papers]
                    parsed = await asyncio.gather(*tasks)
                    parse_time = time.time() - parse_start
                    logger.info(f"PDF processing completed in {parse_time:.2f}s")
                    
                    yield json.dumps({
                        "type": "status",
                        "status": f"Downloading and parsing PDFs... [{parse_time:.2f}s]"
                    }) + "\n"
                    
                    yield json.dumps({
                        "type": "status",
                        "status": "Generating summaries..."
                    }) + "\n"
                    
                    try:
                        # Summary Generation
                        logger.info("Starting summary generation")
                        summary_start = time.time()
                        summarised = await summariser.summarise(parsed)
                        summary_time = time.time() - summary_start
                        logger.info(f"Summary generation completed in {summary_time:.2f}s")
                        
                        yield json.dumps({
                            "type": "status",
                            "status": f"Generating summaries... [{summary_time:.2f}s]"
                        }) + "\n"
                        
                        yield json.dumps({
                            "type": "summaries",
                            "summaries": summarised
                        }) + "\n"
                        
                        # Log total processing time
                        total_time = time.time() - start_time
                        logger.info(f"Request completed successfully in {total_time:.2f}s")
                        
                    except Exception as e:
                        logger.error(f"Error in summary generation: {str(e)}", exc_info=True)
                        yield json.dumps({
                            "type": "error",
                            "message": f"Error generating summaries: {str(e)}"
                        }) + "\n"
                except Exception as e:
                    logger.error(f"Error in PDF processing: {str(e)}", exc_info=True)
                    yield json.dumps({
                        "type": "error",
                        "message": f"Error processing PDFs: {str(e)}"
                    }) + "\n"
            except Exception as e:
                logger.error(f"Error in arXiv search: {str(e)}", exc_info=True)
                yield json.dumps({
                    "type": "error",
                    "message": f"Error searching arXiv: {str(e)}"
                }) + "\n"
        else:
            messages.append(AIMessage(content=response))
            yield json.dumps({
                "type": "message",
                "message": response
            }) + "\n"
            
    except Exception as e:
        logger.error(f"Unexpected error in request processing: {str(e)}", exc_info=True)
        yield json.dumps({
            "type": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }) + "\n"

@app.post("/stream")
async def stream_response(request: StreamRequest):
    try:
        logger.info(f"Received new stream request - Query: {request.message}, Max results: {request.max_results}")
        return StreamingResponse(
            generate_responses(request.message, request.max_results),
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error in stream endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting PaperScout server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
