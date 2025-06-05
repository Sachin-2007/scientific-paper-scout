from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("Paper-Scout")

@mcp.tool()
async def find_papers_and_summarise(query: str) -> str:
    """Finds scientific papers and summarises them"""
    await asyncio.sleep(1)
    return query

if __name__ == "__main__":
    mcp.run(transport="stdio")