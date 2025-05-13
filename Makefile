.PHONY: activate-venv install install-dev freeze download-models test lint clean build-docker run-docker

create-venv:
	python3.10 -m venv .venv

activate-venv:
	source .venv/bin/activate

install:
	pip install -e .

install-dev: install
	pip install -e .[dev]

freeze:
	pip uninstall -y pii-anonymizer || true
	pip install . && pip freeze > requirements.txt
	pip uninstall -y pii-anonymizer || true
	pip install .[dev] && pip freeze > requirements-dev.txt

download-models:
	python -m spacy download en_core_web_lg
	python -m spacy download es_core_news_lg
	python -c "from transformers import pipeline; pipeline('ner', model='dslim/bert-base-NER')"

test:
	pytest --cov=pd_anonymiser --cov-report=html

format:
	black .

clean:
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type d -name '*.egg-info' -exec rm -r {} +

run-example:
	python -m example.py
