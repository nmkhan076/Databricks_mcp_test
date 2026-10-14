import requests
from pathlib import Path
from mcp.server.mcpserver import MCPServer as FastMCP
from fastapi import FastAPI
from fastapi.responses import FileResponse

STATIC_DIR = Path(__file__).parent / "static"

# Create an MCP server
mcp = FastMCP("Custom MCP Server on Databricks Apps")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
@mcp.tool()
def echo(msg: str) -> str:
    return msg
@mcp.tool()
def get_drug_label(drug_name: str) -> dict:
    """
    Retrieve FDA drug labeling information from openFDA
    for a given drug brand name.
    """

    url = "https://api.fda.gov/drug/label.json"

    params = {
        "search": f'openfda.brand_name:"{drug_name}"',
        "limit": 1,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


mcp_app = mcp.streamable_http_app()


app = FastAPI(
    lifespan=lambda _: mcp.session_manager.run(),
)


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/", mcp_app)
