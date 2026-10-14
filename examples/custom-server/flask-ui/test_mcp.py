
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    url = "http://127.0.0.1:8000/mcp/"

    async with streamable_http_client(url) as (
        read,
        write,
    ):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("AVAILABLE TOOLS:")
            for tool in tools.tools:
                print(tool.name)

            result = await session.call_tool(
                "add",
                {"a": 5, "b": 3}
            )

            print("ADD RESULT:", result)


if __name__ == "__main__":
    asyncio.run(main())
