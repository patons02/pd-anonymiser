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
	python -m spacy download en_core_web_trf
	python -c "from transformers import pipeline; pipeline('ner', model='dslim/bert-base-NER')"
	python -c "from transformers import pipeline; pipeline('ner', model='StanfordAIMI/stanford-deidentifier-base')"

test:
	pytest --cov=pd_anonymiser --cov-report=html

format:
	black .

clean:
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type d -name '*.egg-info' -exec rm -r {} +
	find . -type d -name 'htmlcov' -exec rm -r {} +
	find . -type d -name 'sessions' -exec rm -r {} +
	find . -type f -name '.coverage' -exec rm {} +

run-example:
	python sample/reidentification.py
	python sample/no_reidentification.py
