import base64
import re

from pd_anonymiser.utils import load_encrypted_json


def reidentify_text(anonymised_text: str, session_id: str, encoded_key: str) -> str:
    key = base64.urlsafe_b64decode(encoded_key.encode())
    pseudonym_map = load_encrypted_json(session_id, key)

    reverse_map = {v: k[1] for k, v in pseudonym_map.items()}

    # Replace longest pseudonyms first
    for pseudonym in sorted(reverse_map, key=lambda x: -len(x)):
        anonymised_text = re.sub(rf'\b{re.escape(pseudonym)}\b', reverse_map[pseudonym], anonymised_text)

    return anonymised_text