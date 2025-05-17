"""
estimate_openai_cost.py

An API to estimate the cost of an OpenAI API call.
Supports:
 - All major OpenAI chat models with up-to-date pricing.
 - Automatic token counting for prompt text via tiktoken (fallback to whitespace splitting).
"""

import tiktoken

# Pricing per 1K tokens (USD)
PRICING = {
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
    "gpt-3.5-turbo-instruct": {"prompt": 0.0015, "completion": 0.002},
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    "gpt-4o": {"prompt": 0.005, "completion": 0.02},
    "gpt-4o-mini": {"prompt": 0.0006, "completion": 0.0024},
}


def get_pricing(model: str):
    """Return pricing entry for a given model, allowing suffix-based matching."""
    if model in PRICING:
        return PRICING[model]
    for base in sorted(PRICING, key=len, reverse=True):
        if model.startswith(base):
            return PRICING[base]
    raise ValueError(f"Unknown model: {model}")


def estimate_cost(
    prompt_tokens: int, completion_tokens: int, model: str = "gpt-3.5-turbo"
) -> float:
    """Estimate cost in USD for an OpenAI API call."""
    prices = get_pricing(model)
    return (prompt_tokens / 1000) * prices["prompt"] + (
        completion_tokens / 1000
    ) * prices["completion"]


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text for the specified model. Fallback to whitespace splitting."""
    if tiktoken:
        try:
            enc = tiktoken.encoding_for_model(model)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    else:
        return len(text.split())
