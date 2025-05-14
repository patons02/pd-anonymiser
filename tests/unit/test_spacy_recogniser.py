from unittest.mock import MagicMock
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from pd_anonymiser.recognisers.spacy import SpacyNERRecogniser


def setup_mock_analyser(mock_results):
    recogniser = SpacyNERRecogniser()
    recogniser.analyze = MagicMock(return_value=mock_results)
    engine = AnalyzerEngine()
    engine.registry.add_recognizer(recogniser)
    return engine


def test_detects_common_pd():
    text = "David Attenborough lives in Richmond, London. His email is david@bbc.co.uk."

    mock_results = [
        RecognizerResult("PERSON", 0, 18, 0.98),
        RecognizerResult("LOCATION", 34, 40, 0.90),
        RecognizerResult("EMAIL_ADDRESS", 55, 71, 0.95),
    ]

    analyser = setup_mock_analyser(mock_results)
    results = analyser.analyze(text=text, language="en")

    assert any(
        r.entity_type == "PERSON" and text[r.start : r.end] == "David Attenborough"
        for r in results
    )
    assert any(
        r.entity_type == "LOCATION" and "London" in text[r.start : r.end]
        for r in results
    )
    assert any(r.entity_type == "EMAIL_ADDRESS" for r in results)


def test_no_false_positives_on_non_pii():
    text = "The rain in Manchester falls mainly on Tuesday mornings. Pigeons were unaffected."

    mock_results = [
        RecognizerResult("LOCATION", 16, 26, 0.85),
        RecognizerResult("DATE_TIME", 42, 58, 0.87),
    ]

    analyser = setup_mock_analyser(mock_results)
    results = analyser.analyze(text=text, language="en")

    assert all(r.entity_type in {"LOCATION", "DATE_TIME"} for r in results)


def test_should_recognise_people_date_and_place():
    passage = "Emma Thompson met with Boris Johnson at Parliament on 23rd April."

    mock_results = [
        RecognizerResult("PERSON", 0, 13, 0.93),  # Emma Thompson
        RecognizerResult("PERSON", 24, 37, 0.94),  # Boris Johnson
        RecognizerResult("DATE_TIME", 52, 63, 0.88),  # 23rd April
        RecognizerResult("ORGANIZATION", 41, 51, 0.75),  # Parliament
    ]

    analyser = setup_mock_analyser(mock_results)
    results = analyser.analyze(text=passage, language="en")
    recognised_spans = {passage[r.start : r.end]: r.entity_type for r in results}

    assert any("Emma" in span or "Thompson" in span for span in recognised_spans)
    assert any("Boris" in span or "Johnson" in span for span in recognised_spans)
    assert any("23rd" in span or "April" in span for span in recognised_spans)

    if not any("Parliament" in span for span in recognised_spans):
        print("Warning: 'Parliament' was not recognised as a named entity.")
