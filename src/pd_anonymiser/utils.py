import json
from pathlib import Path

from cryptography.fernet import Fernet

DATA_DIR = Path("sessions")
DATA_DIR.mkdir(exist_ok=True)


def generate_key():
    return Fernet.generate_key()


def save_encrypted_json(data: dict, session_id: str, key: bytes):
    f = Fernet(key)
    serialisable = {f"{k[0]}|||{k[1]}": v for k, v in data.items()}
    token = f.encrypt(json.dumps(serialisable).encode())

    out_path = DATA_DIR / f"{session_id}.enc"

    with open(out_path, "wb") as f_out:
        f_out.write(token)


def load_encrypted_json(session_id: str, key: bytes) -> dict:
    f = Fernet(key)
    in_path = DATA_DIR / f"{session_id}.enc"

    with open(in_path, "rb") as f_in:
        encrypted = f_in.read()

    decrypted = f.decrypt(encrypted)
    raw_map = json.loads(decrypted)
    return {tuple(k.split("|||")): v for k, v in raw_map.items()}
