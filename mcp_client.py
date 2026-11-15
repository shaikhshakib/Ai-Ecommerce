import asyncio
import os
import sys

from mcp import Client, StdioServerParameters

async def main():
    server_params = StdioServerParameters(
        command = sys.executable,
        args = ["mcp_server.py"],
        cwd = os.path.dirname(os.path.abspath(__file__))
    )

    async with Client(server_params) as client:

        print("\nConnected to CELESTE ROSE MCP Server!")
    
        result = await client.list_tools()

        # STEP 3: Execute an MCP tool
        result = await client.call_tool(
            "check_jewellery_stock",
            {
                "product_id": 17,
                "requested_quantity": 2
            }
        )

        print("\nMCP Tool Execution Result:")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())