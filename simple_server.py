from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import List, Dict, Any
import json

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print("APIKeyMiddleware dispatch")
        api_key = request.headers.get("X-API-Key")

        if api_key != "your-secret-key":
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized"}
            )

        return await call_next(request)


# Create FastMCP server
mcp = FastMCP(name="MyServer")


@mcp.tool
def hello(name: str) -> str:
    """
    Hello world
    """
    return f"Hello, {name}!"


ac_companies = {
    "bd": ["Walton"],
    "others": ["Samsung", "Gree"]
}
ac_models = {
    "Walton": ["Walton 1", "Walton 2"],
    "Samsung": ["Samsung 1", "Samsung 2"],
    "Gree": ["Gree 1", "Gree 2"]
}


@mcp.tool()
def ping() -> dict:
    """
    Check server is running or not
    """
    return {"status": "ok"}


@mcp.tool()
def companies(country: str) -> list[str] | str:
    """
    Args:
        country (str): The country name or code (e.g., "bd" or "bangladesh").

    Returns:
        list: A list of AC company names for the specified country.
    """
    normalized_query = country.lower()
    if normalized_query in ["bd", "bangladesh"]:
        return json.dumps(ac_companies["bd"])
    else:
        return json.dumps(ac_companies.get(normalized_query, ac_companies["others"]))


@mcp.tool()
def models(company_list: List[str]) -> List[Dict[str, Any]]:
    """
    Returns a list of model for selected company
    """
    if len(company_list) == 0:
        return []
    response = []
    for company in company_list:
        response.append({"company": company, "models": ac_models.get(company, [])})
    return response


@mcp.resource("weather://{city}/current")
def get_weather(city: str) -> dict:
    return {
        "city": city.capitalize(),
        "temperature": 22,
        "condition": "Sunny",
        "unit": "celsius"
    }


@mcp.resource("resource://greeting")
def get_greeting() -> str:
    return "Hello from FastMCP Resources!"


@mcp.prompt()
def ask_about_topic(topic: str) -> str:
    return f"Can you please explain the concept of '{topic}'"


# # Add middleware directly to FastMCP
# custom_middleware = [
#     Middleware(APIKeyMiddleware),
# ]

if __name__ == "__main__":
    # Run FastMCP directly with middleware
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=9000,
        # middleware=custom_middleware
    )
