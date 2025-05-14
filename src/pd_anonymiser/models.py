from pd_anonymiser.recognisers.huggingface import HuggingFaceRecogniser
from pd_anonymiser.recognisers.spacy import SpacyNERRecogniser
from presidio_analyzer import AnalyzerEngine

model_registry = dict()
model_registry.update(
    {
        "en_core_web_trf": SpacyNERRecogniser(model_name="en_core_web_trf"),
        "dslim/bert-base-NER": HuggingFaceRecogniser(model_name="dslim/bert-base-NER"),
        "StanfordAIMI/stanford-deidentifier-base": HuggingFaceRecogniser(
            model_name="StanfordAIMI/stanford-deidentifier-base"
        ),
    }
)


def register_models(analyser: AnalyzerEngine, model: str) -> None:
    if model == "all":
        recognisers = model_registry.values()
    else:
        try:
            recognisers = [model_registry[model]]
        except KeyError:
            raise ValueError(f"Unknown model type: {model}")

    for recogniser in recognisers:
        analyser.registry.add_recognizer(recogniser)
