import sys

from fastmcp import FastMCP
from openai import OpenAI

from pd_anonymiser.anonymiser import AnonymisationResult, anonymise_text
from pd_anonymiser import reidentifier as reid

reid_mcp_server = FastMCP("pd-anonymiser", description="Anonymise → ChatGPT → Reidentify pipeline")
openai_tool = OpenAI(api_key="12345")

@reid_mcp_server.resource(
    name="anonymisation",
    description="Raw text → anonymised text + mapping",
    uri="mcp://pd-anonymiser/anonymisation?text={text}&allow_reidentification={allow_reidentification}"
)
def anonymisation_resource(text: str, allow_reidentification: bool = True) -> dict:
    result: AnonymisationResult = anonymise_text(
        text, allow_reidentification=allow_reidentification
    )

    return {
        "anonymised_text": result.text,
        "session_id": result.session_id,
        "key": result.key
    }

@reid_mcp_server.resource(
    name="reidentification",
    description="Anonymised text + session info → real text",
    uri="mcp://pd-anonymiser/reidentification?text={text}&session_id={session_id}&key={key}"
)
def reidentification_resource(text: str, session_id: str, key: str) -> dict:
    return {"reidentified_text": reid.reidentify_text(text, session_id, key)}

@reid_mcp_server.tool(
    name="anonymisedChat",
    description="Anonymise text, call ChatGPT, then re-identify"
)
def anonymisedChat(text: str, model: str = "gpt-4") -> dict:
    """
    Full pipeline in one call: anonymise input, send to ChatGPT, re-identify output.
    """
    # 1) Anonymise
    anon = anonymisation_resource(text)
    # 2) Call OpenAI API on anonymised text
    try:
        response = openai_tool.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": anon["anonymisedText"]}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}\n\n")
        print(f"In order to continue, I am binding the anonymised text against the reply param. Reply is None due to error.")
        reply = anon["anonymised_text"]
        print("Continuing anyway...")


    # 3) Re-identify the response
    reid_out = reidentification_resource(
        reply,
        anon["session_id"],
        anon["key"]
    )
    return {"text": reid_out["reidentified_text"]}

# --- Prompt Template (optional) ----------------------------------------------------
@reid_mcp_server.prompt(
    name="anonymisePrompt",
    description="Run the user's request but anonymise any personal data in the input and output"
)
def anonymise_prompt(text: str) -> list[dict]:
    return [
        {"role": "system", "content": "You are a helpful assistant that executes the user's instructions. Always anonymise any personal or sensitive data in both the input and your response."},
        {"role": "user",   "content": text}
    ]

# --- Run the server ---------------------------------------------------------------- ----------------------------------------------------------------
if __name__ == "__main__":
    # reid_mcp_server.run(
    #     transport="streamable-http",
    #     host="0.0.0.0",
    #     port=9000
    # )
    reid_mcp_server.run("stdio")