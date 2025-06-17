from typing import List, Dict, Any
from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair


# Generate RSA key pair (for development/testing only)
key_pair = RSAKeyPair.generate()

# Create bearer auth provider
auth = BearerAuthProvider(
    public_key=key_pair.public_key,
    audience="My MCP Server"
    )


# Initialize the MCP server
mcp = FastMCP(name="My MCP Server",auth=auth)

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
    return {"status": "ok"}


@mcp.tool()
def companies(country: str) -> list:
    return ac_companies.get(country, ac_companies["others"])


@mcp.tool()
def models(company_list: List[str]) -> List[Dict[str, Any]]:
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


if __name__ == "__main__":
    token = key_pair.create_token(audience="My MCP Server",expires_in_seconds=3600000)
    print(f"Bearer token for testing: {token}")

    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)
