import asyncio
from fastmcp import Client
import json

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables

MCP_SERVER_BASE_URL = os.environ.get('MCP_SERVER_BASE_URL', '')


async def get_mcp_client():
    return Client(MCP_SERVER_BASE_URL + "/mcp")


async def main():
    client = await get_mcp_client()
    await client_inside(client)
    await run_tools(client)
    await run_recourses(client)
    await run_prompts(client)


async def run_tools(client: Client):
    async with client:
        companies = await client.call_tool("companies", {"country": ""})
        if not companies:
            return
        company_list = json.loads(companies[0].text)
        print(company_list)

        models = await client.call_tool("models", {"company_list": company_list})
        if not models:
            return
        model_list = json.loads(models[0].text)
        print(model_list)


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
            print(prompts.messages[0].content.text)


async def client_inside(client: Client):
    async with client:
        print(f"tools {await client.list_tools()}\n")
        print(f"resource {await client.list_resources()}\n")
        print(f"templates {await client.list_resource_templates()}\n")
        print(f"prompts {await client.list_prompts()}\n")

        functions = [attr for attr in dir(client) if callable(getattr(client, attr)) and not attr.startswith("_")]
        print(f"Client has {len(functions)} functions:")
        for func in functions:
            print("-", func)


if __name__ == "__main__":
    asyncio.run(main())
