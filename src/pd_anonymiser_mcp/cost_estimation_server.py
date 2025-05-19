import logging
import os
from contextlib import asynccontextmanager

import openai
from fastapi import FastAPI
from pydantic import BaseModel

from pd_anonymiser_mcp.estimate_openai_cost import count_tokens, estimate_cost

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


class CostEstimatorRequest(BaseModel):
    prompt: str
    model: str
    max_completion_tokens: int


class CostEstimatorResponse(BaseModel):
    prompt_token_count: int
    cost: float


@app.post(
    "/cost-estimation/open-ai",
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
