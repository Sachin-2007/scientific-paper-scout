import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List

async def stream_response(session: aiohttp.ClientSession, message: str, max_results: int = 3) -> None:
    """Stream the response from the API and handle different message types."""
    try:
        async with session.post(
            "http://localhost:8000/stream",
            json={"message": message, "max_results": max_results}
        ) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return

            # Store titles and summaries for later printing
            titles: List[Dict[str, str]] = []
            summaries: List[str] = []

            async for line in response.content:
                if not line.strip():
                    continue
                    
                try:
                    data = json.loads(line)
                    message_type = data.get("type")
                    
                    if message_type == "status":
                        print(f"\nStatus: {data['status']}")
                    elif message_type == "titles":
                        titles = data["papers"]
                        print("\nFound papers:")
                        for i, paper in enumerate(titles, 1):
                            print(f"{i}. {paper['title']}")
                    elif message_type == "summaries":
                        summaries = data["summaries"]
                        print("\nSummaries:")
                        for i, (title, summary) in enumerate(zip(titles, summaries), 1):
                            print(f"\nPaper {i}: {title['title']}")
                            print("-" * 80)
                            print(summary)
                            print("-" * 80)
                    elif message_type == "message":
                        print(f"\n{data['message']}")
                    elif message_type == "error":
                        print(f"\nError: {data['message']}")
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {line}")
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    
    except aiohttp.ClientError as e:
        print(f"Connection error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

async def main():
    """Main function to handle user input and stream responses."""
    print("Welcome to PaperScout!")
    print("---------------------")
    
    while True:
        # Get query from user
        query = input("\nEnter your research query (or 'quit' to exit): ").strip()
        if query.lower() == 'quit':
            break
            
        if not query:
            print("Please enter a valid query.")
            continue
            
        # Get max results from user
        while True:
            try:
                max_results = input("Enter number of papers to process (default: 3): ").strip()
                if not max_results:
                    max_results = 3
                    break
                max_results = int(max_results)
                if max_results < 1:
                    print("Please enter a number greater than 0.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")
        
        print(f"\nProcessing query: {query}")
        print(f"Max results: {max_results}")
        print("\nProcessing...")

        async with aiohttp.ClientSession() as session:
            await stream_response(session, query, max_results)
            
        print("\n---------------------")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!") 