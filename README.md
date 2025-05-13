# pd-anonymiser

A privacy-focused text anonymisation and re-identification tool built on [Microsoft Presidio](https://github.com/microsoft/presidio), with support for:

- Named Entity Recognition using Hugging Face or SpaCy
- Inline pseudonym replacement (e.g., `Theresa May` → `Person A`)
- Encrypted, session-based reversible mapping
- Tuned for UK English and realistic examples

---

## 🚀 Quick Start

### 1. Clone and set up environment

```bash
git clone https://github.com/your-user/pd-anonymiser.git
cd pd-anonymiser

# Python 3.10 recommended
python3.10 -m venv .venv
source .venv/bin/activate

make install-dev
make download-models
````

---

### 2. Run the example

```bash
python -m example
```

Expected output:

```text
Original Text:
Theresa May met with Boris Johnson...

Anonymised Text (both):
Person A met with Person B...

Session Info:
{'session_id': '...', 'key': '...'}

Reidentified Text:
Theresa May met with Boris Johnson...
```

---

## 🔧 Features

* Choose models:

  * `model="hf"`: Hugging Face (`dslim/bert-base-NER`)
  * `model="spacy"`: SpaCy (`en_core_web_lg`)
  * `model="both"`: Combine both recognisers

* Toggle pseudonym behaviour:

  * `use_reusable_tags=True`: Person A, Location B, etc.
  * `use_reusable_tags=False`: UUID-based replacements

* Fully reversible:

  * Returns encrypted `key` and `session_id`
  * Use `reidentify_text()` with both to reverse substitutions

---

## 📁 Project Structure

```bash
.
├── example.py                # End-to-end usage example
├── sessions/                # Encrypted session mappings (auto-created)
├── src/
│   └── pd_anonymiser/
│       ├── anonymiser.py    # Main anonymisation pipeline
│       ├── reidentifier.py  # Re-identification using secure mapping
│       ├── utils.py         # Key generation, encryption helpers
│       └── recognisers/
│           ├── huggingface.py
│           └── spacy.py
├── tests/                   # Pytest tests
├── Makefile
└── README.md
```

---

## 🧪 Running tests

```bash
make test
```

---

## 🔐 Security model

* All mappings are stored encrypted using a per-session Fernet key.
* Pseudonyms are not persisted in plaintext.
* Re-identification only possible with possession of both `session_id` and `key`.

---

## 📦 Dependencies

* `presidio-analyzer`, `presidio-anonymizer`
* `transformers`, `spacy`, `cryptography`
* See `pyproject.toml` and `requirements-dev.txt` for full list.

---

## ✨ Future ideas

* Streamlit UI for drag-and-drop document redaction
* PDF/Docx support via PyMuPDF or python-docx
* Named entity deduplication across recognisers

---

## 👤 Maintainer

**Stuart Paton** — [stuartpaton.dev](https://www.stuartpaton.dev)

---
