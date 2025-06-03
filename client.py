import asyncio
from fastmcp import Client
import json

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables

MCP_SERVER_BASE_URL = os.environ.get('MCP_SERVER_BASE_URL', '')


async def main():
    client = Client(MCP_SERVER_BASE_URL + "/mcp")

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


if __name__ == "__main__":
    asyncio.run(main())
