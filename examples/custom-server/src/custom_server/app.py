import requests
from pathlib import Path
from mcp.server.mcpserver import MCPServer as FastMCP
from fastapi import FastAPI
from fastapi.responses import FileResponse
from requests.exceptions import RequestException

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
    """Retrieve FDA labeling information by drug brand name."""

    url = "https://api.fda.gov/drug/label.json"

    params = {
        "search": f'openfda.brand_name:"{drug_name.strip()}"',
        "limit": 1
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        print("OpenFDA URL:", response.url)
        print("Status code:", response.status_code)

        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return {
                "success": False,
                "error": "No drug labeling records found."
            }

        label = results[0]
        openfda = label.get("openfda", {})

        return {
            "success": True,
            "brand_name": openfda.get("brand_name", []),
            "generic_name": openfda.get("generic_name", []),
            "manufacturer": openfda.get(
                "manufacturer_name", []
            ),
            "boxed_warning": label.get(
                "boxed_warning", []
            ),
            "warnings": label.get("warnings", []),
            "adverse_reactions": label.get(
                "adverse_reactions", []
            )
        }

    except RequestException as exc:
        return {
            "success": False,
            "error": f"OpenFDA request failed: {exc}"
        }

    except ValueError as exc:
        return {
            "success": False,
            "error": f"Invalid JSON response: {exc}"
        }

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
