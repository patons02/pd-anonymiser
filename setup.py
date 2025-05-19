from setuptools import setup, find_packages

setup(
    name="pd-anonymiser",
    version="0.1.0",
    description="Personal Data Anonymisation and Re-identification with Presidio + Hugging Face",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "presidio-analyzer",
        "presidio-anonymizer",
        "spacy",
        "transformers",
        "cryptography",
        "fastapi",
        "openai",
        "uvicorn",
        "tiktoken",
        "fastmcp",
    ],
    extras_require={"dev": ["pytest", "pytest-cov", "black", "pip-tools"]},
    python_requires=">=3.10",
)
