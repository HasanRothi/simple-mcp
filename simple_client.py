import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import os
import json


MCP_SERVER_BASE_URL = os.environ.get('MCP_SERVER_BASE_URL', 'http://localhost:9000')


class MCPClientManager:
    def __init__(self):
        self.transport = StreamableHttpTransport(
            url=MCP_SERVER_BASE_URL + "/mcp",
            headers={"X-API-Key": "your-secret-key"}
        )
        # keep_alive=True by default - maintains session between contexts
        self.client = Client(self.transport)

    async def get_client(self):
        """Get the client instance - ready to use in async with block"""
        return self.client

    async def close(self):
        """Manually close the client session if needed"""
        await self.client.close()


# Global instance
mcp_manager = MCPClientManager()


async def get_mcp_client():
    """Helper function to get the client"""
    return await mcp_manager.get_client()


async def get_mcp_tools():
    client = await get_mcp_client()
    async with client:
        return await client.list_tools()


async def call_mcp_tool(name: str, args):
    client = await get_mcp_client()
    async with client:
        return await client.call_tool(name, args)


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


async def do_something_with_mcp():
    client = await get_mcp_client()

    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")

        if any(tool.name == "hello" for tool in tools):
            result = await client.call_tool("hello", {"name": "World"})
            print(f"Result: {result[0].text}")

        await client_inside(client)
        await run_tools(client)
        await run_recourses(client)
        await run_prompts(client)


if __name__ == "__main__":
    asyncio.run(do_something_with_mcp())
