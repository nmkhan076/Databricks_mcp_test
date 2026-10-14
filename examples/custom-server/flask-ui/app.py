
import asyncio
import json
import os
import traceback

from flask import Flask, render_template, request
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

app = Flask(__name__)

MCP_URL = os.getenv(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp/"
)


async def fetch_drug(drug_name):
    async with streamable_http_client(MCP_URL) as (
        read_stream,
        write_stream
    ):
        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                "get_drug_label",
                {"drug_name": drug_name}
            )

            if result.is_error:
                raise RuntimeError(
                    str(result.content)
                )

            # Your MCP server returns TextContent
            if result.structured_content is not None:
                data = result.structured_content
            else:
                text_blocks = [
                    block.text
                    for block in result.content
                    if block.type == "text"
                ]

                if not text_blocks:
                    raise ValueError(
                        "MCP returned no text response"
                    )

                data = json.loads(text_blocks[0])

            if not isinstance(data, dict):
                raise ValueError(
                    "Expected a JSON object from MCP"
                )

            return data


@app.route("/", methods=["GET", "POST"])
def home():
    drug_data = None
    error = None
    drug_name = ""

    if request.method == "POST":
        drug_name = request.form.get(
            "drug_name", ""
        ).strip()

        if not drug_name:
            error = "Please enter a drug name."
        else:
            try:
                drug_data = asyncio.run(
                    fetch_drug(drug_name)
                )

                if not drug_data.get("success", False):
                    error = drug_data.get(
                        "error",
                        "Drug information unavailable."
                    )
                    drug_data = None

            except Exception:
                traceback.print_exc()
                error = (
                    "Unable to retrieve drug information. "
                    "Check the Flask terminal for details."
                )

    return render_template(
        "index.html",
        drug_data=drug_data,
        drug_name=drug_name,
        error=error
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
