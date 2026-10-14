import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():

    url = "http://127.0.0.1:8000/mcp/"

    async with streamable_http_client(url) as (
        read_stream,
        write_stream,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            # Connect to the MCP server
            await session.initialize()

            # Ask the server what tools it has
            tools = await session.list_tools()

            print("\nAVAILABLE TOOLS:")
            for tool in tools.tools:
                print("-", tool.name)

            # Actually use your OpenFDA tool
            result = await session.call_tool(
                "get_drug_label",
                {
                    "drug_name": "OxyContin"
                }
            )

            print("\nOPENFDA RESULT:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())