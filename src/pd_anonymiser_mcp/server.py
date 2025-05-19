import argparse

from fastmcp import FastMCP, Context
from fastmcp.utilities.logging import get_logger
from openai import OpenAI

from pd_anonymiser.anonymiser import AnonymisationResult, anonymise_text
from pd_anonymiser import reidentifier as reid

logger = get_logger(__name__)

reid_mcp_server = FastMCP(
    "pd-anonymiser", description="Anonymise → ChatGPT → Reidentify pipeline"
)

openai_tool = OpenAI(api_key="12345")

@reid_mcp_server.resource(
    name="anonymisation",
    description="Raw text → anonymised text + mapping",
    uri="mcp://pd-anonymiser/anonymisation?text={text}&allow_reidentification={allow_reidentification}",
)
def anonymisation_resource(text: str, allow_reidentification: bool = True) -> dict:
    result: AnonymisationResult = anonymise_text(
        text, allow_reidentification=allow_reidentification
    )

    return {
        "anonymised_text": result.text,
        "session_id": result.session_id,
        "key": result.key,
    }


@reid_mcp_server.resource(
    name="reidentification",
    description="Anonymised text + session info → real text",
    uri="mcp://pd-anonymiser/reidentification?text={text}&session_id={session_id}&key={key}",
)
def reidentification_resource(text: str, session_id: str, key: str) -> dict:
    return {"reidentified_text": reid.reidentify_text(text, session_id, key)}


@reid_mcp_server.tool("execute-prompt-with-anonymisation")
async def redact_and_summarise(text: str, ctx: Context) -> dict:
    anon: AnonymisationResult = anonymise_text(text)

    llm_response = await ctx.sample(
        messages=[
            "Run this prompt. Validate and verify every output 3 times before responding. Don't stop until your task is complete.",
            anon.text
        ],
        temperature=0.5,
        max_tokens=150,
    )

    return {
        "llm_response_anonymised": llm_response,
        "session_id": anon.session_id,
        "key": anon.key
    }

# --- Prompt Template (optional) ----------------------------------------------------
@reid_mcp_server.prompt(
    name="anonymisePrompt",
    description="Run the user's request but anonymise any personal data in the input and output",
)
def anonymise_prompt(text: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": "You are a helpful assistant that executes the user's instructions. Always anonymise any personal or sensitive data in both the input and your response.",
        },
        {"role": "user", "content": text},
    ]

# --- Run the server ---------------------------------------------------------------- ----------------------------------------------------------------
def run_server_with_args(args):
    transport = args.transport
    if transport == "stdio":
        reid_mcp_server.run(transport="stdio")
    else:
        reid_mcp_server.run(
            transport=transport,
            host=args.host,
            port=args.port,
            path=args.path
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the PD-Anonymiser MCP server (anonymise → ChatGPT → re-identify)",
        epilog="Example: python server.py --transport streamable-http --host 0.0.0.0 --port 8000"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="streamable-http",
        help=(
            "Which MCP transport to use. "
            "`stdio` for stdin/stdout; "
            "`streamable-http` for HTTP JSON-RPC; "
            "`sse` for server-sent events."
        ),
        metavar="TRANSPORT"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host or interface to bind the HTTP server on",
        metavar="HOST"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Port number for the HTTP server",
        metavar="PORT"
    )

    parser.add_argument(
        "--path",
        default = "/mcp",
        help = "HTTP URL prefix for JSON-RPC endpoints (e.g. /mcp)",
        metavar = "PATH"
   )

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    run_server_with_args(args)

if __name__ == "__main__":
    main()
