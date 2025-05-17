import base64
import pytest
from unittest.mock import patch

from pd_anonymiser.reidentifier import reidentify_text

# Sample pseudonym map for mocking
mock_pseudonym_map = {
    ("PERSON", "Alice"): "Person A",
    ("PERSON", "Bob"): "Person B",
    ("ORGANIZATION", "Acme Corp"): "Company A",
    ("LOCATION", "Cambridge"): "Location A",
}

encoded_key = base64.urlsafe_b64encode(b"test_key_12345678901234567890").decode()


@patch("pd_anonymiser.reidentifier.load_encrypted_json")
def test_reidentify_basic_substitution(mock_loader):
    mock_loader.return_value = mock_pseudonym_map

    anon_text = "Person A met with Person B at Company A in Location A."
    result = reidentify_text(anon_text, "dummy-session-id", encoded_key)

    expected = "Alice met with Bob at Acme Corp in Cambridge."
    assert result == expected


@patch("pd_anonymiser.reidentifier.load_encrypted_json")
def test_reidentify_longest_first(mock_loader):
    # Ensure it replaces 'Person AB' before 'Person A'
    long_map = {
        ("PERSON", "Alice Bob"): "Person AB",
        ("PERSON", "Alice"): "Person A",
    }
    mock_loader.return_value = long_map

    anon_text = "Person AB and Person A were present."
    result = reidentify_text(anon_text, "dummy-session-id", encoded_key)

    expected = "Alice Bob and Alice were present."
    assert result == expected


@patch("pd_anonymiser.reidentifier.load_encrypted_json")
def test_show_map_output(mock_loader, capsys):
    mock_loader.return_value = {
        ("PERSON", "Alice"): "Person A",
    }

    anon_text = "Person A went shopping."
    _ = reidentify_text(
        anon_text, "dummy", base64.urlsafe_b64encode(b"key").decode(), show_map=True
    )

    captured = capsys.readouterr()
    assert "Reverse map" in captured.out
    assert "'Alice'" in captured.out


@patch("pd_anonymiser.reidentifier.load_encrypted_json")
def test_missing_key_gracefully_replaces_nothing(mock_loader):
    mock_loader.return_value = {}

    anon_text = "Something totally unrelated."
    result = reidentify_text(anon_text, "dummy", encoded_key)

    assert result == anon_text
