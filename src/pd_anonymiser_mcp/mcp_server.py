import logging
import os
from contextlib import asynccontextmanager

import openai
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import BaseModel

from pd_anonymiser_mcp.estimate_openai_cost import count_tokens, estimate_cost
from pd_anonymiser.anonymiser import AnonymisationResult, anonymise_text
from pd_anonymiser.reidentifier import reidentify_text

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mcp_server")


app = FastAPI()


# Lifespan context to handle startup and shutdown events
@asynccontextmanager
async def lifespan():
    # Startup logic
    logger.info("Application startup initiated")
    openai.api_key = "12345"
    yield
    # Shutdown logic (if needed)
    logger.info("Application shutdown complete")


class ChatRequest(BaseModel):
    text: str


class ChatResponse(BaseModel):
    original_text: str
    anonymised_text: str
    gpt_response: str
    reidentified_response: str


class ErrorResponse(BaseModel):
    error: str
    original_text: str
    anonymised_text: str


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}, 200: {"model": ChatResponse}},
)
async def chat(request: ChatRequest):
    logger.info("Anonymising input...")
    anonymised_input: AnonymisationResult = anonymise_text(
        request.text, allow_reidentification=True
    )
    logger.info("Input anonymised...")

    try:
        logger.info("Sending prompt to OpenAI API...")
        client = OpenAI()
        response = openai.responses.create(
            model="gpt-4o", input=[{"role": "user", "content": anonymised_input.text}]
        )
        gpt_reply = response["choices"][0]["message"]["content"]
        logger.info("Received response from OpenAI API...")
    except Exception as e:
        logger.error(f"Exception logged from OpenAI API. Error {e.args}")
        err = ErrorResponse(
            error=f"OpenAI API call failed: {e}",
            original_text=request.text,
            anonymised_text=anonymised_input.text,
        )
        return JSONResponse(status_code=500, content=err.model_dump())

    logger.info(
        "Re-identifying OpenAI response using map from original anonymisation..."
    )
    reidentified_text = reidentify_text(
        gpt_reply, anonymised_input.session_id, anonymised_input.key
    )

    logger.info("Sending response to client. Status code: 200")
    return ChatResponse(
        original_text=request.text,
        anonymised_text=anonymised_input.text,
        gpt_response=gpt_reply,
        reidentified_response=reidentified_text,
    )


class CostEstimatorRequest(BaseModel):
    prompt: str
    model: str
    max_completion_tokens: int


class CostEstimatorResponse(BaseModel):
    prompt_token_count: int
    cost: float


@app.post(
    "/open-ai-cost",
    response_model=CostEstimatorResponse,
    responses={200: {"model": CostEstimatorResponse}},
)
async def estimate_openai_api_cost(request: CostEstimatorRequest):
    prompt_token_count = count_tokens(request.prompt, request.model)
    return CostEstimatorResponse(
        cost=estimate_cost(
            prompt_token_count, request.max_completion_tokens, request.model
        ),
        prompt_token_count=prompt_token_count,
    )
