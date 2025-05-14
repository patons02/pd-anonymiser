import base64
import uuid
import pd_anonymiser.models as model_registry
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from collections import defaultdict
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from pd_anonymiser.utils import generate_key, save_encrypted_json


DATA_DIR = Path("sessions")
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_MAPPING = {
    "PERSON": "Person",
    "LOCATION": "Location",
    "EMAIL_ADDRESS": "Email",
    "PHONE_NUMBER": "Phone",
    "ORGANIZATION": "Company",
    "DATE_TIME": "Date",
}


@dataclass
class AnonymisationResult:
    text: str
    session_id: Optional[str]
    key: Optional[str]


def anonymise_text(
    text: str,
    language: str = "en",
    use_reusable_tags: bool = True,
    model: str = "both",
    allow_reidentification: bool = False,
) -> AnonymisationResult:
    analyser = AnalyzerEngine()
    model_registry.register_models(analyser, model)

    results = analyser.analyze(text=text, language=language)
    if not results:
        return AnonymisationResult(text=text, session_id=None, key=None)

    pseudonyms = _generate_pseudonyms(results, text, use_reusable_tags)
    _attach_replacements(results, pseudonyms, text)

    session_id = str(uuid.uuid4())
    key = generate_key()
    if not key:
        raise ValueError("Encryption key generation failed.")

    save_encrypted_json(pseudonyms, session_id, key)

    if allow_reidentification:
        anonymised_text = _apply_manual_replacements(text, results)
    else:
        anonymised_text = (
            AnonymizerEngine().anonymize(text=text, analyzer_results=results).text
        )

    return AnonymisationResult(
        text=anonymised_text,
        session_id=session_id,
        key=base64.urlsafe_b64encode(key).decode(),
    )


def _generate_pseudonyms(
    results: List[RecognizerResult], text: str, use_reusable: bool
) -> dict:
    entity_counters = defaultdict(int)
    pseudonyms = {}

    for r in results:
        entity_type = r.entity_type
        original = text[r.start : r.end]
        key = (entity_type, original)

        if key not in pseudonyms:
            entity_counters[entity_type] += 1
            pseudonym = (
                f"{DEFAULT_MAPPING.get(entity_type, entity_type)} {chr(64 + entity_counters[entity_type])}"
                if use_reusable
                else str(uuid.uuid4())
            )
            pseudonyms[key] = pseudonym

    return pseudonyms


def _attach_replacements(
    results: List[RecognizerResult], pseudonyms: dict, text: str
) -> None:
    for r in results:
        original = text[r.start : r.end]
        key = (r.entity_type, original)
        if key not in pseudonyms:
            raise ValueError(f"No pseudonym found for {key}")
        r.operator = OperatorConfig("replace", {"new_value": pseudonyms[key]})


def _apply_manual_replacements(text: str, results: List[RecognizerResult]) -> str:
    for r in sorted(results, key=lambda r: -r.start):
        replacement = r.operator.params["new_value"]
        text = text[: r.start] + replacement + text[r.end :]
    return text
