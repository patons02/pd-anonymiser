import pytest
from pd_anonymiser.recognisers.spacy import SpacyNERRecogniser
from presidio_analyzer import AnalyzerEngine

@pytest.fixture
def recogniser():
    return SpacyNERRecogniser(model_name="en_core_web_lg")

@pytest.fixture
def analyser_with_spacy(recogniser):
    engine = AnalyzerEngine()
    engine.registry.add_recognizer(recogniser)
    return engine

def test_detects_common_pd(analyser_with_spacy):
    text = "David Attenborough lives in Richmond, London. His email is david@bbc.co.uk."
    results = analyser_with_spacy.analyze(text=text, language="en")

    assert any(r.entity_type == "PERSON" and text[r.start:r.end] == "David Attenborough" for r in results)
    assert any(r.entity_type == "LOCATION" and "London" in text[r.start:r.end] for r in results)
    assert any(r.entity_type == "EMAIL_ADDRESS" for r in results)

def test_no_false_positives_on_non_pii(analyser_with_spacy):
    text = "The rain in Manchester falls mainly on Tuesday mornings. Pigeons were unaffected."
    results = analyser_with_spacy.analyze(text=text, language="en")

    for result in results:
        assert result.entity_type in {"LOCATION", "DATE_TIME"}

def test_should_recognise_people_date_and_place(analyser_with_spacy):
    passage = "Emma Thompson met with Boris Johnson at Parliament on 23rd April."
    results = analyser_with_spacy.analyze(text=passage, language="en")

    recognised_spans = {passage[r.start:r.end]: r.entity_type for r in results}

    # Expectation: "Emma Thompson" and "Boris Johnson" should be picked up
    assert any("Emma" in span or "Thompson" in span for span in recognised_spans)
    assert any("Boris" in span or "Johnson" in span for span in recognised_spans)
    assert any("23rd" in span or "April" in span for span in recognised_spans)

    # Parliament may or may not be recognised — if it is, it should be a named entity
    if not any("Parliament" in span for span in recognised_spans):
        print("Warning: 'Parliament' was not recognised as a named entity.")

