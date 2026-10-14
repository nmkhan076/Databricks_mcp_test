
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

            # result = await session.call_tool(
            #     "add",
            #     {"a": 5, "b": 3}
            # )
            #
            # print("ADD RESULT:", result)
            print("Calling get_drug_label...")

            try:
                result = await session.call_tool(
                    "get_drug_label",
                    {"drug_name": "OxyContin"}
                )

                print("MCP ERROR:", result.is_error)
                print("STRUCTURED RESULT:", result.structured_content)
                print("CONTENT:", result.content)

            except Exception as exc:
                print("TOOL CALL FAILED")
                print("Exception type:", type(exc).__name__)
                print("Exception message:", str(exc))
                raise

if __name__ == "__main__":
    asyncio.run(main())
