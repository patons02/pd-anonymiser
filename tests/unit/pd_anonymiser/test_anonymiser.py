import base64
import re
import pytest
from unittest.mock import patch, MagicMock

from pd_anonymiser.anonymiser import (
    anonymise_text,
    _generate_pseudonyms,
    _attach_replacements,
    _apply_manual_replacements,
    AnonymisationResult,
)
from presidio_analyzer import RecognizerResult


SAMPLE_TEXT = "Alice Smith emailed bob@example.com from Acme Corp in London."


@patch("pd_anonymiser.anonymiser.AnalyzerEngine")
@patch("pd_anonymiser.anonymiser.save_encrypted_json")
def test_anonymise_text_basic(mock_save, mock_analyzer):
    mock_result = RecognizerResult(entity_type="PERSON", start=0, end=11, score=0.99)
    mock_result.operator = None
    mock_analyzer.return_value.analyze.return_value = [mock_result]

    with patch("pd_anonymiser.anonymiser.model_registry.register_models"):
        result = anonymise_text(SAMPLE_TEXT, model="hf", allow_reidentification=True)

    assert isinstance(result, AnonymisationResult)
    assert "Person" in result.text  # pseudonym pattern "Person A"


def test_generate_pseudonyms_reusable():
    results = [
        RecognizerResult("PERSON", 0, 5, 0.9),
        RecognizerResult("PERSON", 6, 10, 0.9),
    ]
    text = "Alice Bob"
    pseudonyms = _generate_pseudonyms(results, text, use_reusable=True)

    assert pseudonyms[(results[0].entity_type, "Alice")].startswith("Person")
    assert pseudonyms[(results[1].entity_type, "Bob")].startswith("Person")


def test_generate_pseudonyms_non_reusable():
    email = "someone@email.com"
    results = [RecognizerResult("EMAIL_ADDRESS", 0, len(email), 0.9)]
    text = email
    pseudonyms = _generate_pseudonyms(results, text, use_reusable=False)

    val = pseudonyms[("EMAIL_ADDRESS", email)]
    assert re.match(r"[a-f0-9\-]{36}", val)  # UUID format


def test_attach_replacements_success():
    r = RecognizerResult("PERSON", 0, 5, 0.85)
    results = [r]
    text = "Alice"
    pseudonyms = {("PERSON", "Alice"): "Person A"}

    _attach_replacements(results, pseudonyms, text)
    assert r.operator.params["new_value"] == "Person A"


def test_attach_replacements_fails_on_missing_key():
    r = RecognizerResult("PERSON", 0, 5, 0.85)
    results = [r]
    text = "Alice"
    pseudonyms = {}  # empty

    with pytest.raises(ValueError, match="No pseudonym found"):
        _attach_replacements(results, pseudonyms, text)


def test_apply_manual_replacements_order():
    r1 = RecognizerResult("PERSON", 0, 5, 0.9)
    r1.operator = MagicMock()
    r1.operator.params = {"new_value": "X"}

    r2 = RecognizerResult("PERSON", 6, 11, 0.9)
    r2.operator = MagicMock()
    r2.operator.params = {"new_value": "Y"}

    result = _apply_manual_replacements("Alice Smith", [r1, r2])
    assert result == "X Y"
