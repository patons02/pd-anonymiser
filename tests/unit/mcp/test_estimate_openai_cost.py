import pytest
import os
import sys

# Ensure the 'src' directory is on the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pd_anonymiser_mcp.estimate_openai_cost as cost_module


def test_get_pricing_exact():
    pricing = cost_module.get_pricing("gpt-3.5-turbo")
    assert pricing == {"prompt": 0.0005, "completion": 0.0015}


def test_get_pricing_prefix():
    # Should match longest-prefix first
    pricing = cost_module.get_pricing("gpt-3.5-turbo-16k-custom")
    assert pricing == {"prompt": 0.003, "completion": 0.004}


def test_get_pricing_unknown():
    with pytest.raises(ValueError):
        cost_module.get_pricing("unknown-model")


def test_estimate_cost():
    # 1000 prompt tokens at $0.0005 + 2000 completion tokens at $0.0015 = 0.0005 + 0.003 = 0.0035
    cost = cost_module.estimate_cost(1000, 2000, "gpt-3.5-turbo")
    assert cost == pytest.approx(0.0035)


def test_count_tokens_whitespace_fallback(monkeypatch):
    # Force fallback by removing tiktoken
    monkeypatch.setattr(cost_module, "tiktoken", None)
    text = "hello world test"
    # Expect whitespace splitting
    assert cost_module.count_tokens(text, model="any-model") == 3
