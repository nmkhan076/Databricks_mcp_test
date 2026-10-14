
import asyncio
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
        read_stream, write_stream
    ):
        async with ClientSession(
            read_stream, write_stream
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                "get_drug_label",
                {"drug_name": drug_name}
            )

            if result.isError:
                raise RuntimeError(str(result.content))

            if result.structuredContent:
                return result.structuredContent

            import json
            return json.loads(result.content[0].text)


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
            except Exception as exc:
                error = str(exc)
                traceback.print_exc()
                # error = str(error)
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
