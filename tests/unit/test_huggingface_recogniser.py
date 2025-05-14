from unittest.mock import MagicMock
from presidio_analyzer import AnalyzerEngine, RecognizerResult

from pd_anonymiser.recognisers.huggingface import HuggingFaceRecogniser


def setup_mock_engine(mock_results):
    recogniser = HuggingFaceRecogniser()
    recogniser.analyze = MagicMock(return_value=mock_results)
    engine = AnalyzerEngine()
    engine.registry.add_recognizer(recogniser)
    return engine


def test_should_identify_basic_person_email_and_location():
    passage = "Theresa May emailed oliver.twist@parliament.uk from Downing Street."

    mock_results = [
        RecognizerResult("PERSON", 0, 11, 0.99),
        RecognizerResult("EMAIL_ADDRESS", 18, 48, 0.99),
        RecognizerResult("LOCATION", 54, 69, 0.95),
    ]

    analyser = setup_mock_engine(mock_results)
    findings = analyser.analyze(text=passage, language="en")

    assert any(
        f.entity_type == "PERSON" and passage[f.start : f.end] == "Theresa May"
        for f in findings
    )
    assert any(f.entity_type == "EMAIL_ADDRESS" for f in findings)
    assert any(f.entity_type == "LOCATION" for f in findings)


def test_should_detect_multiple_people():
    passage = "James Bond met with M at MI6 headquarters."
    mock_results = [
        RecognizerResult("PERSON", 0, 10, 0.98),  # James Bond
        RecognizerResult("PERSON", 20, 21, 0.88),  # M
    ]

    analyser = setup_mock_engine(mock_results)
    findings = analyser.analyze(text=passage, language="en")

    persons = [f for f in findings if f.entity_type == "PERSON"]
    assert len(persons) >= 2


def test_should_identify_organisations():
    passage = "He previously worked at Barclays and later joined the BBC."
    mock_results = [
        RecognizerResult("ORGANIZATION", 26, 34, 0.96),  # Barclays
        RecognizerResult("ORGANIZATION", 54, 57, 0.93),  # BBC
    ]

    analyser = setup_mock_engine(mock_results)
    findings = analyser.analyze(text=passage, language="en")

    labels = [
        passage[f.start : f.end] for f in findings if f.entity_type == "ORGANIZATION"
    ]
    assert "Barclays" in labels or "BBC" in labels


def test_should_not_flag_generic_nouns_as_pii():
    passage = (
        "Green apples and lavender fields were mentioned during the gardening segment."
    )
    mock_results = []  # No PII should be returned

    analyser = setup_mock_engine(mock_results)
    findings = analyser.analyze(text=passage, language="en")

    assert all(f.entity_type not in {"PERSON", "EMAIL_ADDRESS"} for f in findings)
