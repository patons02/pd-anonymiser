import tempfile
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from pd_anonymiser.utils import generate_key, save_encrypted_json, load_encrypted_json


@pytest.fixture
def temp_session_dir(monkeypatch):
    """Creates a temporary sessions/ directory and patches DATA_DIR."""
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    monkeypatch.setattr("pd_anonymiser.utils.DATA_DIR", temp_path)
    return temp_path, temp_dir


def test_generate_key_is_valid():
    key = generate_key()
    assert isinstance(key, bytes)
    # Should be usable with Fernet
    f = Fernet(key)
    token = f.encrypt(b"test")
    decrypted = f.decrypt(token)
    assert decrypted == b"test"


def test_encrypted_json_roundtrip(temp_session_dir):
    session_path, _ = temp_session_dir
    test_key = generate_key()
    test_session_id = "test-session"
    test_data = {
        ("PERSON", "Alice Smith"): "Person A",
        ("EMAIL_ADDRESS", "alice@example.com"): "Email A",
    }

    save_encrypted_json(test_data, test_session_id, test_key)
    out_file = session_path / f"{test_session_id}.enc"
    assert out_file.exists()

    loaded = load_encrypted_json(test_session_id, test_key)
    assert loaded == test_data


def test_decryption_fails_with_wrong_key(temp_session_dir):
    session_path, _ = temp_session_dir
    correct_key = generate_key()
    wrong_key = generate_key()
    session_id = "fail-key"
    data = {("EMAIL_ADDRESS", "wrong@example.com"): "Email B"}

    save_encrypted_json(data, session_id, correct_key)

    with pytest.raises(Exception):
        load_encrypted_json(session_id, wrong_key)
