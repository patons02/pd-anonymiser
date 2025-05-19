import asyncio
import sys
from contextlib import AsyncExitStack
from typing import Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect(self, server_script: str):
        params = StdioServerParameters(command="python", args=[server_script], env=None)
        # start stdio transport and MCP session
        transport = await self.exit_stack.enter_async_context(stdio_client(params))
        stdio_read, stdio_write = transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio_read, stdio_write)
        )

        # negotiate capabilities
        await self.session.initialize()
        tools = (await self.session.list_tools()).tools
        print("Connected to server with resources/tools:", [t.name for t in tools])

    async def chat(self, text: str, model: str = "gpt-4") -> str:
        """
        Runs: anonymisation → LLM → re-identification, in one go
        via the 'chatAnonymised' tool.
        """
        # call the composite tool
        result = await self.session.call_tool(
            "anonymisedChat", {"text": text, "model": model}
        )
        return result.content

    async def close(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py path/to/server.py")
        sys.exit(1)

    server_path = sys.argv[1]
    client = MCPClient()
    try:
        await client.connect(server_path)
        print("\nType a message (or 'quit'):\n")
        while True:
            user = input("> ").strip()
            if user.lower() in ("quit", "exit"):
                break
            reply = await client.chat(user)
            print("\nReply:", reply, "\n")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
