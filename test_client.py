import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Tools list karo
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Tool call test
            result = await session.call_tool("add", {"a": 15, "b": 27})
            print("\nadd(15, 27) =", result.content)

            result = await session.call_tool("multiply", {"a": 6, "b": 7})
            print("multiply(6, 7) =", result.content)

            result = await session.call_tool("greet", {"name": "Bhai"})
            print("greet =", result.content)

if __name__ == "__main__":
    asyncio.run(main())
