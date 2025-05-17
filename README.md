# pd-anonymiser

A privacy-focused tool to **anonymise** and optionally **re-identify** personal data using Microsoft Presidio. 

Supports NER with Hugging Face and SpaCy transformer models, pseudonym mapping, and encrypted reversible transformations.

---

## 🚀 Quick Start

```bash
git clone https://github.com/your-org/pd-anonymiser.git
cd pd-anonymiser

# Create and activate Python 3.10 virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install all dependencies (dev included)
make install-dev

# Download models (once)
make download-models
````

---

## 🧪 Run Examples

### 🔐 With Re-identification

```bash
python sample/reidentification.py
```

### 🔒 Without Re-identification (e.g. irreversible UUIDs)

```bash
python sample/no_reidentification.py
```

### 💻 MCP Server

Start the FastAPI-based MCP server to expose REST endpoints:

```bash
uvicorn src.mcp.mcp_server:app --reload
```

---

## MCP Server Endpoints

### POST `/chat`

1. **Anonymises** the input text
2. **Calls** OpenAI with the anonymised prompt
3. **Re-identifies** the model’s response

**Request**

```json
{
  "text": "John Smith works at OpenAI and lives in London."
}
```

**Response (200)**

```json
{
  "original_text":       "John Smith works at OpenAI and lives in London.",
  "anonymised_text":     "Person A works at Company A and lives in Location A.",
  "gpt_response":        "…model’s reply…",
  "reidentified_response":"John Smith works at OpenAI and lives in London."
}
```

---

### POST `/open-ai-cost`

Estimates the USD cost of an OpenAI API call.

**Request**

```json
{
  "prompt":                "Hello world",
  "model":                 "gpt-4",
  "max_completion_tokens": 100
}
```

**Response (200)**

```json
{
  "prompt_token_count":  3,
  "cost":                0.0123
}
```

---

## 🧠 Supported Models

* 🤗 `dslim/bert-base-NER` (Hugging Face Transformers)
* 🎓 `StanfordAIMI/stanford-deidentifier-base` (Hugging Face Transformers)
* 🧬 `en_core_web_trf` (SpaCy transformer pipeline)

You can choose one with:

```python
anonymise_text(..., model="dslim/bert-base-NER")                      # https://huggingface.co/dslim/bert-base-NER
anonymise_text(..., model="StanfordAIMI/stanford-deidentifier-base")  # https://huggingface.co/StanfordAIMI/stanford-deidentifier-base
anonymise_text(..., model="en_core_web_trf")                          # https://spacy.io/models/en#en_core_web_trf
anonymise_text(..., model="all")                                      # Combine all above models
```

---

## Pricing Estimator

Uses [tiktoken](https://github.com/openai/tiktoken) for token counting.
Pricing lives in `src/mcp/estimate_openai_cost.py`.

---

## 💼 Key Features

- Combine multiple recognisers
- `OperatorConfig` injection for anonymisation
- Reusable tag pseudonyms (e.g. `Person A`, `Company B`)
- Optional irreversible UUID redaction
- Re-identification with Fernet-encrypted session-based mappings
- Designed for English (UK), but extensible
- Built-in FastAPI MCP server for text-based integrations


---

## 🧱 Project Structure

```
pd-anonymiser/
├── sample/
│   ├── reidentification.py         # Example with re-identification
│   └── no_reidentification.py      # Example with irreversible redaction
├── src/pd_anonymiser/
│   ├── pd_anonymiser/
│   │   ├── anonymiser.py               # Core logic (SpaCy + HF)
│   │   ├── reidentifier.py             # Reverse mapping logic
│   │   ├── models.py                   # Model registry
│   │   ├── utils.py                    # Fernet, session storage
│   │   └── recognisers/
│   │       ├── huggingface.py
│   │       └── spacy.py
│   └── mcp/
│       └── mcp_server.py
├── sessions/                       # Encrypted session data (auto-generated)
├── tests/
│    ├── unit/                      # Unit tests
│    └── integration/               # Integration tests
├── Makefile                        # Setup & CI helper
├── setup.py
└── README.md
```

---

## 📦 Development Tasks

```bash
make install-dev        # Editable install with dev deps
make test               # Run pytest with coverage
make freeze             # Generate requirements.txt and dev.txt
make download-models    # Pull transformer-based SpaCy model
```

---

## 🔐 Re-identification Flow

1. During anonymisation, a **Fernet key + session ID** are generated
2. A **JSON pseudonym map** is encrypted and saved in `sessions/`
3. To re-identify, call:

```python
reidentify_text(anonymised_text, session_id, encoded_key)
```

---

## ✅ Example Output

```text
Original Text:
Theresa May met with Boris Johnson at Downing Street...

Anonymised:
Person A met with Person B at Location A...

Reidentified:
Theresa May met with Boris Johnson at Downing Street...
```

---

## 🧰 Requirements

* Python 3.10
* `presidio-analyzer`, `presidio-anonymizer`
* `transformers`, `spacy`, `cryptography`
* `fastapi`, `uvicorn`, `openai`, `tiktoken`
* Various Spacy and Hugging Face models (download via `make download-models`)
* Dev: `pytest`, `pytest-cov`, `pip-tools`

---

## 👤 Maintainer

Built and maintained by [@patons02](https://github.com/patons02)

---

## 🪪 License

MIT License. See [LICENSE.md](https://github.com/patons02/pd-anonymiser/blob/main/LICENSE.md)

---