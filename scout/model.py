from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import SystemMessage
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

model_name = os.getenv("LLM_MODEL")
if os.getenv("LLM_API_KEY") is not None:
    if os.getenv("LLM_PROVIDER") == "openai":
        os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")
    elif os.getenv("LLM_PROVIDER") == "anthropic":
        os.environ["ANTHROPIC_API_KEY"] = os.getenv("LLM_API_KEY")
    elif os.getenv("LLM_PROVIDER") == "google":
        os.environ["GEMINI_API_KEY"] = os.getenv("LLM_API_KEY")
    elif os.getenv("LLM_PROVIDER") == "azure":
        os.environ["AZURE_API_KEY"] = os.getenv("LLM_API_KEY")
    elif os.getenv("LLM_PROVIDER") == "groq":
        os.environ["GROQ_API_KEY"] = os.getenv("LLM_API_KEY")

    model = ChatLiteLLM(model=os.getenv("MODEL_NAME"))
else:
    raise ValueError("LLM_API_KEY is not set")

server_params = StdioServerParameters(
    command="python",
    args=["./mcp_servers/scout_server.py"],
)

async def get_llm_response(messages):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            llm = model.bind_tools(tools)
            messages.insert(0, SystemMessage(content="You are a helpful assistant that can find scientific papers and summarise them."))
            response = await llm.ainvoke(messages)
            
            tool = None
            if response.tool_calls:
                tool_call = response.tool_calls[0]
                print(f"Tool call: {tool_call['name']} with args: {tool_call['args']}")
                selected_tool = {"find_papers_and_summarise": tools[0]}[tool_call["name"].lower()]
                tool_msg = await selected_tool.ainvoke(tool_call)
                tool = {
                    "name": tool_call["name"],
                    "args": tool_call["args"]
                }
                return response.content, tool
            
            return response.content, None

if __name__ == "__main__":
    print(asyncio.run(get_llm_response()))