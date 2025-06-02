import asyncio
from fastmcp import Client
import json


async def main():
    # Initialize the client with the path to the server script
    client = Client("http://127.0.0.1:9000/mcp")
    async with client:
        # Call the 'greet' tool with a parameter
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
