import asyncio
from fastmcp import Client
import json
from fastmcp.client.auth import BearerAuth
import os
from dotenv import load_dotenv
from fastmcp.client.transports import StreamableHttpTransport

load_dotenv()

MCP_SERVER_BASE_URL = os.environ.get('MCP_SERVER_BASE_URL', 'http://localhost:9000')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')


async def run_tools(client: Client):
    async with client:
        companies = await client.call_tool("companies", {"country": ""})
        if not companies:
            return
        company_list = json.loads(companies[0].text)
        print(f"Company list: {company_list}")

        models = await client.call_tool("models", {"company_list": company_list})
        if not models:
            return
        model_list = json.loads(models[0].text)
        print(f"Model list: {model_list}")


async def run_recourses(client: Client):
    async with client:
        greeting_resource = await client.read_resource("resource://greeting")
        if len(greeting_resource) == 0:
            return
        print(greeting_resource[0].text)

        weather_resource = await client.read_resource("weather://dhaka/current")
        if len(weather_resource) == 0:
            return
        print(weather_resource[0].text)


async def run_prompts(client: Client):
    async with client:
        prompts = await client.get_prompt("ask_about_topic", arguments={"topic": "What is the weather like?"})

        if prompts is not None and len(prompts.messages) > 0:
            print(f"prompt {prompts.messages[0].content.text}")


async def client_inside(client: Client):
    async with client:
        print(f"-----tools-----\n {await client.list_tools()}\n")
        print(f"-----resource-----\n {await client.list_resources()}\n")
        print(f"-----templates-----\n {await client.list_resource_templates()}\n")
        print(f"-----prompts-----\n {await client.list_prompts()}\n")

        functions = [attr for attr in dir(client) if callable(getattr(client, attr)) and not attr.startswith("_")]
        print(f"Client has {len(functions)} functions:")
        for func in functions:
            print("-", func)


async def get_mcp_client():
    """Create MCP client with proper error handling"""
    try:
        # auth = BearerAuth(token=AUTH_TOKEN)
        # return Client(MCP_SERVER_BASE_URL + "/mcp", auth=auth)

        transport = StreamableHttpTransport(
            url=MCP_SERVER_BASE_URL + "/mcp",
            headers={"X-API-Key": "your-secret-key"}
        )

        async with Client(transport) as client:
            return client

    except Exception as e:
        print(f"Error creating client: {e}")
        raise


async def test_connection():
    """Test basic connection before running full client"""
    try:
        client = await get_mcp_client()
        async with client:
            print("✅ Connection successful!")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def main():
    print(f"Connecting to: {MCP_SERVER_BASE_URL}")

    # Test connection first
    if not await test_connection():
        print("Connection test failed. Please check:")
        print("1. Is your MCP server running?")
        print("2. Is the URL correct?")
        print("3. Is the token valid and not expired?")
        return

    # If connection works, run your full client
    client = await get_mcp_client()
    await client_inside(client)
    await run_tools(client)
    await run_recourses(client)
    await run_prompts(client)


if __name__ == "__main__":
    asyncio.run(main())
