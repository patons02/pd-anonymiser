from typing import List

import spacy
from presidio_analyzer import EntityRecognizer, RecognizerResult

DEFAULT_ENTITY_MAPPING = {
    "PERSON": "PERSON",
    "LOC": "LOCATION",
    "GPE": "LOCATION",
    "ORG": "ORGANIZATION",
    "DATE": "DATE_TIME",
    "EMAIL": "EMAIL_ADDRESS"
}

class SpacyNERRecogniser(EntityRecognizer):
    def __init__(self, model_name="en_core_web_lg", entity_mapping=None):
        self._model_name = model_name
        self._entity_mapping = entity_mapping or DEFAULT_ENTITY_MAPPING
        self._nlp = spacy.load(model_name)
        self.supported_entities = list(set(self._entity_mapping.values()))
        super().__init__(self.supported_entities)

    def load(self):
        pass # Already loaded

    def analyze(self, text, entities, nlp_artifacts=None) -> List[RecognizerResult]:
        if not any(ent in self.supported_entities for ent in entities):
            return []

        results = []
        doc = self._nlp(text)

        for ent in doc.ents:
            spacy_label = ent.label_.upper()
            mapped_label = self._entity_mapping.get(spacy_label)

            if mapped_label in entities:
                results.append(RecognizerResult(
                    entity_type = mapped_label,
                    start = ent.start_char,
                    end = ent.end_char,
                    score=0.85, #SpaCy doesn't provide confidence by default
                    analysis_explanation=None
                ))

        return results
