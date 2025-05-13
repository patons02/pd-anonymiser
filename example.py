from pprint import pprint

from pd_anonymiser.anonymiser import anonymise_text
from pd_anonymiser.reidentifier import reidentify_text

# ----------------------------
# Sample input text
# ----------------------------
original_text = """
Theresa May met with Boris Johnson at Downing Street.
She emailed oliver.twist@parliament.uk before attending a meeting at Barclays HQ.
"""

print("Original Text:\n", original_text)

# ----------------------------
# Anonymise text
# Choose model: "hf", "spacy", or "both"
# ----------------------------
selected_model = "both"

result = anonymise_text(
    text=original_text,
    language="en",
    use_reusable_tags=True,
    model=selected_model
)

print(f"\nAnonymised Text ({selected_model}):\n", result["anonymised_text"])
print("\nSession Info:")
pprint({
    "session_id": result["session_id"],
    "key": result["key"]
})

# ----------------------------
# Re-identify
# ----------------------------
reidentified_text = reidentify_text(
    anonymised_text=result["anonymised_text"],
    session_id=result["session_id"],
    encoded_key=result["key"]
)

print("\nReidentified Text:\n", reidentified_text)
