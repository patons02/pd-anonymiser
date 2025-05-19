import asyncio
import json
import os
import sys

import openai
from dotenv import load_dotenv

from fastmcp import Client
from fastmcp.client.logging import LogMessage
from mcp import SamplingMessage
from mcp.client.streamable_http import RequestContext
from openai.types.evals.create_eval_completions_run_data_source import SamplingParams

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

async def sampling_handler(
    messages: list[SamplingMessage],
    params:   SamplingParams,
    ctx:      RequestContext,
) -> str:
    # Convert MCP messages → OpenAI format
    chat_messages = [
        {"role": m.role, "content": m.content.text}
        for m in messages
    ]

    response = await openai.ChatCompletion.acreate(
        model       = "gpt-4o-mini",
        messages    = chat_messages,
        max_tokens  = params.maxTokens  or 100,
        n           = 1,
    )
    return response.choices[0].message.content

async def log_handler(params: LogMessage):
    print(f"[Server Log - {params.level.upper()}] {params.logger or 'default'}: {params.data}")


async def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <SERVER_URL_OR_SCRIPT> <TEXT_TO_ANONYMISE>")
        print('  e.g. python client.py http://localhost:9000/mcp "Alice from Acme Corp emailed Bob yesterday."')
        sys.exit(1)

    client = Client(sys.argv[1], log_handler=log_handler)

    async with client:
        # anonymisation
        anonymisation_uri = f"mcp://pd-anonymiser/anonymisation?text={sys.argv[2]}&allow_reidentification=True"
        anon_result = await client.read_resource(anonymisation_uri)
        anonymisation_result = json.loads(anon_result[0].text)
        print(anonymisation_result)


        # reidentification
        reid_uri = f"mcp://pd-anonymiser/reidentification?text={anonymisation_result['anonymised_text']}&session_id={anonymisation_result['session_id']}&key={anonymisation_result['key']}"
        reid_result = await client.read_resource(reid_uri)
        print(json.loads(reid_result[0].text))

if __name__ == '__main__':
    asyncio.run(main())