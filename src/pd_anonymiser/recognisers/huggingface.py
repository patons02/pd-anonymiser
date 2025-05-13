from typing import List

from presidio_analyzer import EntityRecognizer, RecognizerResult
from transformers import pipeline

DEFAULT_ENTITY_MAPPING = {
    "PER": "PERSON",
    "PERSON": "PERSON",
    "LOC": "LOCATION",
    "LOCATION": "LOCATION",
    "ORG": "ORGANIZATION",
    "ORGANIZATION": "ORGANIZATION",
    "EMAIL": "EMAIL_ADDRESS",
    "PHONE": "PHONE_NUMBER",
    "DATE": "DATE_TIME",
}


class HuggingFaceRecogniser(EntityRecognizer):
    def __init__(
        self, model_name="dslim/bert-base-NER", entity_mapping=None, device=-1
    ):
        self.model_name = model_name
        self.device = device
        self.entity_mapping = entity_mapping or DEFAULT_ENTITY_MAPPING
        self.ner_pipeline = pipeline(
            task="ner", model=model_name, aggregation_strategy="simple", device=device
        )
        self.supported_entities = list(set(self.entity_mapping.values()))
        super().__init__(self.supported_entities)

    def load(self):
        pass  # Already loaded

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts=None
    ) -> List[RecognizerResult]:
        if not any(ent in self.supported_entities for ent in entities):
            return []

        results = []
        predictions = self.ner_pipeline(text)

        for pred in predictions:
            raw_label = pred["entity_group"].upper()
            mapped_label = self.entity_mapping.get(raw_label)

            if mapped_label in entities:
                results.append(
                    RecognizerResult(
                        entity_type=mapped_label,
                        start=pred["start"],
                        end=pred["end"],
                        score=pred["score"],
                        analysis_explanation=None,
                    )
                )

        return results
