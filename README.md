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

The repo ships an MCP server **and** a sample client.

### 1  Launch the server

```bash
python src/pd_anonymiser_mcp/server.py            \
  --transport streamable-http --host 0.0.0.0 --port 9000 --path /mcp
```

> By default it exposes **JSON‑RPC over HTTP** at [http://localhost:9000/mcp](http://localhost:9000/mcp).

#### 📑 What the server exposes

| Type       | Name                                  | URI / behaviour                                                                                                                                                     |
| ---------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *resource* | **anonymisation**                     | `mcp://pd-anonymiser/anonymisation?text={text}&allow_reidentification={allow_reidentification}` → returns `{ anonymised_text, session_id, key }`                    |
| *resource* | **reidentification**                  | `mcp://pd-anonymiser/reidentification?text={text}&session_id={session_id}&key={key}` → returns `{ reidentified_text }`                                              |
| *tool*     | **execute‑prompt‑with‑anonymisation** | Takes raw `text`, internally *(1)* anonymises it, *(2)* calls the **client’s LLM** via `ctx.sample()`, *(3)* returns `{ llm_response_anonymised, session_id, key }` |
| *prompt*   | **anonymisePrompt**                   | Prompt template that forces any assistant to strip personal data in both input & output                                                                             |



### Launch the MCP Server

```bash
python src/pd_anonymiser_mcp/server.py
```

By default, it listens on **[http://0.0.0.0:9000](http://0.0.0.0:9000)** with JSON-RPC over HTTP.

### 👾 Use in VSCode *Agent Mode*

1. Install **GitHub Copilot Chat** extension.
2. In the *Chat* panel choose **Agent** mode → *Tools* ➜ **Add MCP Server** → URL `http://localhost:9000/mcp`.
3. Enable `pd-anonymiser.*` tools and experiment interactively: anonymise → chat → re‑identify, all inside VSCode.


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
│   └── pd_anonymiser_mcp/               # MCP server implementation
│       ├── cost_estimation_server.py    # FastAPI server to check OpenAI API cost
│       ├── estimate_openai_cost.py      # cost estimator for OpenAI API's 
│       ├── client.py                    # MCP client example
│       └── server.py                    # FastMCP JSON-RPC server
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