import logging
from pprint import pprint

from pd_anonymiser.anonymiser import anonymise_text
from pd_anonymiser.reidentifier import reidentify_text

import os

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"
logging.disable(logging.CRITICAL)


TEXT_TO_ANONYMISE = """
    Theresa May met with Boris Johnson at Downing Street.
    She emailed oliver.twist@parliament.uk before attending a meeting at Barclays HQ.
    """


def sample(text_to_anonymise=TEXT_TO_ANONYMISE, selected_model="both"):
    print("Text to anonymise:\n", text_to_anonymise)

    result = anonymise_text(
        text=text_to_anonymise,
        language="en",
        use_reusable_tags=True,
        model=selected_model,
        allow_reidentification=False,
    )

    print(f"\nAnonymised Text ({selected_model}):\n", result.text)
    print("\nSession Info:")
    pprint({"session_id": result.session_id, "key": result.key})

    # ----------------------------
    # Re-identify
    # ----------------------------
    reidentified_text = reidentify_text(
        anonymised_text=result.text,
        session_id=result.session_id,
        encoded_key=result.key,
    )

    print("\nReidentified Text:\n", reidentified_text)


def run_samples():
    print("===================================\n")
    print("=    SAMPLE: No Reidentification  =\n")
    print("===================================\n")

    print("===========================\n")
    print("=    HUGGING FACE MODEL:  =\n")
    print("=    dslim/bert-base-NER  =\n")
    print("===========================\n")
    sample(selected_model="dslim/bert-base-NER")

    print("===============================================\n")
    print("=             HUGGING FACE MODEL:             =\n")
    print("=    StanfordAIMI/stanford-deidentifier-base  =\n")
    print("===============================================\n")
    sample(selected_model="StanfordAIMI/stanford-deidentifier-base")

    print("\n\n")
    print("===========================\n")
    print("=        SpaCy MODEL:     =\n")
    print("=       en_core_web_trf   =\n")
    print("===========================\n")
    sample(selected_model="en_core_web_trf")

    print("\n\n")
    print("=============================================\n")
    print("=             All models combined:          =\n")
    print("=               en_core_web_trf             =\n")
    print("=             dslim/bert-base-NER           =\n")
    print("=  StanfordAIMI/stanford-deidentifier-base  =\n")
    print("=============================================\n")
    sample(selected_model="all")


if __name__ == "__main__":
    run_samples()
