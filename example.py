from pprint import pprint

from pd_anonymiser.anonymiser import anonymise_text
from pd_anonymiser.reidentifier import reidentify_text

TEXT_TO_ANONYMISE = """
    Theresa May met with Boris Johnson at Downing Street.
    She emailed oliver.twist@parliament.uk before attending a meeting at Barclays HQ.
    """


def example_hf_model():
    example(TEXT_TO_ANONYMISE, "hf")


def example_spacy_model():
    example(TEXT_TO_ANONYMISE, "spacy")


def example_both_models():
    example(TEXT_TO_ANONYMISE, "both")


def example(text_to_anonymise, selected_model="both"):
    print("Text to anonymise:\n", text_to_anonymise)

    result = anonymise_text(
        text=text_to_anonymise,
        language="en",
        use_reusable_tags=True,
        model=selected_model,
    )

    print(f"\nAnonymised Text ({selected_model}):\n", result["anonymised_text"])
    print("\nSession Info:")
    pprint({"session_id": result["session_id"], "key": result["key"]})

    # ----------------------------
    # Re-identify
    # ----------------------------
    reidentified_text = reidentify_text(
        anonymised_text=result["anonymised_text"],
        session_id=result["session_id"],
        encoded_key=result["key"],
    )

    print("\nReidentified Text:\n", reidentified_text)


def run_examples():
    print("===========================\n")
    print("=    HUGGING FACE MODEL:  =\n")
    print("=    dslim/bert-base-NER  =\n")
    print("===========================\n")
    print("\n\n")
    example_hf_model()

    print("\n\n")
    print("===========================\n")
    print("=        SpaCy MODEL:     =\n")
    print("=       en_core_web_lg    =\n")
    print("===========================\n")
    print("\n\n")
    example_spacy_model()

    print("\n\n")
    print("===========================\n")
    print("=  Both models combined:  =\n")
    print("=     en_core_web_lg      =\n")
    print("=  dslim/bert-base-NER    =\n")
    print("===========================\n")
    print("\n\n")
    example_spacy_model()


if __name__ == "__main__":
    run_examples()
