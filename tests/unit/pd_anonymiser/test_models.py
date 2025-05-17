import pytest
from presidio_analyzer import AnalyzerEngine

from pd_anonymiser.models import model_registry, register_models
from pd_anonymiser.recognisers.huggingface import HuggingFaceRecogniser
from pd_anonymiser.recognisers.spacy import SpacyNERRecogniser


def test_model_registry_keys_present():
    expected_keys = {
        "en_core_web_trf",
        "dslim/bert-base-NER",
        "StanfordAIMI/stanford-deidentifier-base",
    }
    assert expected_keys.issubset(model_registry.keys())


def test_model_registry_values_types():
    for recogniser in model_registry.values():
        assert isinstance(recogniser, (HuggingFaceRecogniser, SpacyNERRecogniser))


def test_register_single_model(monkeypatch):
    engine = AnalyzerEngine()
    model_name = "en_core_web_trf"

    # Ensure no recognizers are present initially
    engine.registry.recognizers = []

    register_models(engine, model_name)

    entity_types = engine.get_supported_entities("en")
    assert "PERSON" in entity_types or "EMAIL_ADDRESS" in entity_types


def test_register_all_models(monkeypatch):
    engine = AnalyzerEngine()
    engine.registry.recognizers = []

    register_models(engine, "all")

    supported = engine.get_supported_entities("en")
    # Some common entities expected from both SpaCy and HF
    assert any(
        entity in supported for entity in ["PERSON", "EMAIL_ADDRESS", "LOCATION"]
    )


def test_register_invalid_model_raises():
    engine = AnalyzerEngine()

    with pytest.raises(ValueError, match="Unknown model type: invalid_model"):
        register_models(engine, "invalid_model")
