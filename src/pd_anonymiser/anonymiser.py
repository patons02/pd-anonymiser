import base64
import uuid
from pathlib import Path

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from collections import defaultdict

from pd_anonymiser.recognisers.huggingface import HuggingFaceRecogniser
from pd_anonymiser.recognisers.spacy import SpacyNERRecogniser
from pd_anonymiser.utils import generate_key, save_encrypted_json

# Path for session data
DATA_DIR = Path("sessions")
DATA_DIR.mkdir(exist_ok=True)

# Pseudonym formatting
DEFAULT_MAPPING = {
    "PERSON": "Person",
    "LOCATION": "Location",
    "EMAIL_ADDRESS": "Email",
    "PHONE_NUMBER": "Phone",
    "ORGANIZATION": "Company",
    "DATE_TIME": "Date"
}


def generate_session_id():
    return str(uuid.uuid4())

def anonymise_text(text, language="en", use_reusable_tags=True, model="both"):
    analyser = AnalyzerEngine()
    _add_selected_model_to_registry(analyser, model)

    anonymiser = AnonymizerEngine()

    # Detect entities
    results = analyser.analyze(text, language)

    entity_counters = defaultdict(int)
    pseudonyms = {}

    # Generate pseudonyms
    for r in results:
        entity_type = r.entity_type
        original = text[r.start:r.end]
        key = (entity_type, original)

        if key in pseudonyms:
            pseudonym_value = pseudonyms[key]
        else:
            entity_counters[entity_type] += 1
            if use_reusable_tags:
                label = DEFAULT_MAPPING.get(entity_type, entity_type)
                pseudonym_value = f"{label} {chr(64 + entity_counters[entity_type])}"
            else:
                pseudonym_value = str(uuid.uuid4())
            pseudonyms[key] = pseudonym_value

        # Attach dynamic replacement
        r.operator = OperatorConfig("replace", {"new_value": pseudonym_value})

    if not results:
        return {
            "anonymised_text": text,
            "session_id": None,
            "key": None
        }

    # Generate session id and save encrypted map
    session_id = generate_session_id()
    key = generate_key()
    if key is None:
        raise ValueError("Encryption key generation failed.")

    save_encrypted_json(pseudonyms, session_id, key)

    # Apply anonymisation
    result = anonymiser.anonymize(text=text, analyzer_results=results, operators=None)

    return {
        "anonymised_text": result.text,
        "session_id": session_id,
        "key": base64.urlsafe_b64encode(key).decode()
    }


def _add_selected_model_to_registry(analyser, model):
    if model == "spacy":
        analyser.registry.add_recognizer(SpacyNERRecogniser(model_name="en_core_web_lg"))
    elif model == "hf":
        analyser.registry.add_recognizer(HuggingFaceRecogniser(model_name="dslim/bert-base-NER"))
    elif model == "both":
        analyser.registry.add_recognizer(SpacyNERRecogniser(model_name="en_core_web_lg"))
        analyser.registry.add_recognizer(HuggingFaceRecogniser(model_name="dslim/bert-base-NER"))
    else:
        raise ValueError(f"Unknown model type: {model}")