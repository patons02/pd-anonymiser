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

# Install all dependencies (prod + dev)
make install-dev

# Download models (once)
make download-models
````
---

## Core Library Usage

```python
from pd_anonymiser.anonymiser import anonymise_text
from pd_anonymiser.reidentifier import reidentify_text

# Anonymise input text (returns anonymisedText, sessionId, key)
result = anonymise_text(
    "Alice from Acme Corp emailed Bob at 5pm.",
    allow_reidentification=True
)
print(result.text, result.session_id, result.key)

# Re-identify the text using the session map
original = reidentify_text(
    result.text,
    result.session_id,
    result.key
)
print(original)
```

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
---

### 💻 MCP Server

The MCP server implements the Model Context Protocol for three-step pipelines:

1. **Anonymisation** (resource)
2. **ChatGPT call** via OpenAI (tool)
3. **Re-identification** (resource)

It also provides a composite tool, `anonymisedChat`, that bundles all three steps in one call.

### Launch the MCP Server

```bash
python src/pd_anonymiser_mcp/server.py
```

By default, it listens on **[http://0.0.0.0:9000](http://0.0.0.0:9000)** with JSON-RPC over HTTP.

### Resources (JSON-RPC `invoke`)

* **Anonymisation**

  ```text
  mcp://pd-anonymiser/anonymisation?text={text}&allow_reidentification={allow_reidentification}
  ```

  Returns `{ anonymisedText, sessionId, key }`.

* **Re-identification**

  ```text
  mcp://pd-anonymiser/reidentification?text={text}&session_id={session_id}&key={key}
  ```

  Returns `{ text }`.

### Tools

* **anonymisedChat**: full pipeline in one call

  * Params: `{ text, model? }`
  * Returns: `{ text }` (final, re-identified reply)

### Prompt Template

* **anonymisePrompt**: instructs the assistant to follow user instructions while anonymising any personal data in both input and output.

### Example: curl-based Pipeline

```bash
# 1) Anonymise input
curl -s localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{
      "jsonrpc":"2.0",
      "method":"invoke",
      "params":{
        "toolId":"mcp://pd-anonymiser/anonymisation",
        "params":{"text":"Hello, I’m Stuart from London.","allow_reidentification":true}
      },
      "id":1
    }' | jq

# 2) Chat anonymised (composite)
curl -s localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{
      "jsonrpc":"2.0",
      "method":"invoke",
      "params":{
        "toolId":"mcp://pd-anonymiser/anonymisedChat",
        "params":{"text":"Hello, I’m Stuart from London.","model":"gpt-4"}
      },
      "id":2
    }' | jq

# 3) Re-identification (if needed separately)
curl -s localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{
      "jsonrpc":"2.0",
      "method":"invoke",
      "params":{
        "toolId":"mcp://pd-anonymiser/reidentification",
        "params":{"text":"...anonymised reply...","session_id":"...","key":"..."}
      },
      "id":3
    }' | jq
```

---

## Pricing Estimator Server

Uses [tiktoken](https://github.com/openai/tiktoken) for token counting.
Pricing lives in `src/pd_anonymiser_mcp/estimate_openai_cost.py` with server `src/pd_anonymiser_mcp/cost_estimation_server.py`.

The server can be run via:
```commandline
 uvicorn src.pd_anonymiser_mcp.cost_estimation_server:app --reload
```
---

### POST `/cost-estimator/open-ai`

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
├── BLOG-POST-1_MCP_FEATURE.md     # Design notes for MCP integration
├── Makefile                      # Helpers: install-dev, test, download-models
├── sample/
│   ├── reidentification.py       # Example with re-identification
│   └── no_reidentification.py    # Example with UUID-only anonymisation
├── src/
│   ├── pd_anonymiser/            # Core library
│   │   ├── anonymiser.py         # NER-based anonymisation logic
│   │   ├── reidentifier.py       # Session-based reverse mapping
│   │   ├── models.py             # Model registry
│   │   ├── utils.py              # Fernet encryption, session storage
│   │   └── recognisers/
│   │       ├── huggingface.py
│   │       └── spacy.py
│   └── pd_anonymiser_mcp/        # MCP server implementation
│       └── server.py             # FastMCP JSON-RPC server
├── tests/
│   ├── unit/                     # Unit tests (anonymiser + cost estimator)
│   └── integration/              # Integration tests (end-to-end)
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── setup.py
└── README.md                     # ← this file
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



