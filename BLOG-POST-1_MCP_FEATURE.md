# Why LLMs That Rely on Plaintext Inputs Violate Modern Privacy Principles
### The Case for Privacy-Preserving AI Pipelines Using Anonymisation and Re-identification Orchestration

**Author:** Stuart Paton  
**Date:** May 2025

---

## Abstract

As large language models (LLMs) become integral to knowledge work, legal review, healthcare, and internal enterprise automation, they increasingly interface with sensitive, personally identifiable data. Yet most LLMs operate under an implicit assumption: the input text they receive is raw, unredacted, and trusted. This assumption places LLM workflows in direct conflict with core principles of modern data protection laws such as GDPR, CCPA, and the AI Act. This article makes the case that **plain text input to LLMs is no longer viable**, and introduces a structured response: **privacy-first orchestration layers that anonymise before enrichment and re-identify only when necessary**.

---

## 1. The Plaintext Assumption Is a Privacy Risk

Most public and enterprise LLMs—from GPT-4 to Claude—expect prompt inputs in unencrypted, unredacted text. While this may simplify UX, it contradicts privacy best practices. Consider the following real-world examples:

- A legal analyst uploads a contract for summarization. Names, addresses, and salary details are sent to OpenAI’s API.
- A healthcare researcher uses an LLM to rewrite clinical notes. Diagnoses, patient names, and dates of birth are exposed.
- A recruiter uses an LLM to rank candidates based on resumes. Ethnic names, universities, and disability disclosures are included.

In all cases, **personal data which includes personally identifiable information (PII) is shared in plain text** with a third-party processor, often without any anonymisation or user consent.

---

## 2. Violations of Privacy Principles

The plaintext input model conflicts with the following foundational principles:

### 2.1 Data Minimisation
Only data strictly necessary for processing should be used. Yet plaintext inputs often include superfluous identifiers—names, locations, references—irrelevant to the task at hand.

### 2.2 Purpose Limitation
LLMs are general-purpose systems. They can’t enforce or audit the specific legal purpose under which data is processed. This ambiguity creates compliance risk.

### 2.3 Security of Processing
Plaintext data is transmitted to cloud-based models, often without guarantees of encryption at rest, access control, or deletion timelines.

### 2.4 Auditability and Accountability
Once data enters an LLM, tracing what happened to it—whether it was stored, inferred upon, or leaked via token prediction—is nearly impossible.

### 2.5 Consent and Transparency
In most scenarios, data subjects are unaware their information is being processed by an LLM. This violates informed consent obligations under GDPR and ethical AI frameworks.

---

## 3. The Technical Debt of Naïve Prompting

Developers are increasingly wrapping LLMs into products without treating them as **data processors** with privacy obligations. This creates technical debt in areas like:

- Consent management  
- Data residency  
- Privacy impact assessments (DPIAs)  
- Breach response (how do you notify someone whose data was leaked through inference?)

As adoption scales, these shortcuts become liabilities—not just legal, but reputational and ethical.

---

## 4. A New Model: Privacy-First LLM Orchestration

The solution isn’t to avoid LLMs—it’s to redesign the pipeline around **privacy-enhancing technologies (PETs)**.

We propose a three-stage model:

### Stage A: Anonymisation
- Apply Named Entity Recognition (NER) via SpaCy, Presidio, or HuggingFace models  
- Replace PII with consistent, reversible UUID mappings  
- Encrypt the mapping table per session  

### Stage B: Enrichment
- Run prompts through the LLM with anonymised text  
- Capture outputs without ever exposing sensitive data  
- Optionally chain multi-step GPT calls with token-safe placeholders  

### Stage C: Re-identification
- Reinsert PII based on session keys and mapping files  
- Ensure the process is auditable, reversible, and bounded by retention policy  

This model aligns with **Privacy by Design**, minimizes risk, and allows LLM workflows to meet enterprise and legal standards.

---

## 5. MCP: A Reference Implementation

The [MCP (Master Control Program)](https://github.com/patons02/pd-anonymiser) is an open-source orchestration layer implementing the above pattern. Built using FastAPI, Docker, and Python-native privacy tools, it allows you to:

- Anonymise PDF/DOCX/JSON data before LLM use  
- Interact with GPT models using secure streaming APIs  
- Reidentify only when authorised, with encrypted mapping layers  
- Log every step for audit and compliance  
- Mimic the ChatGPT UX via a self-hosted interface  

---

## 6. A Call to Action for Privacy Engineers and AI Builders

The LLM revolution is here—but unless we build it **ethically and responsibly**, we’ll be forced to retroactively patch trust into a system designed without it.

If you're developing LLM-based products in:
- Legal tech  
- Healthcare  
- HR tech  
- Enterprise internal tooling  

…it’s no longer sufficient to assume plaintext prompts are acceptable.

### Instead, treat LLMs as part of a sensitive data pipeline. Wrap them in PETs. Audit their outputs. Respect the data.

---

## Get Involved

We're building `MCP` as a foundation for this future. If you're a:

- Privacy engineer  
- LLM prompt designer  
- Compliance lead  
- Security-conscious developer  

…we invite you to contribute. Fork the repo. Run the demos. Help shape privacy-first AI.

> [GitHub Repo](https://github.com/patons02/pd-anonymiser)  
> [Contact](mailto:stu@stuartpaton.dev)

---

## References

- GDPR (Article 5, 6, 32)  
- CCPA §1798.100–1798.199  
- ENISA Guidelines on Privacy by Design  
- OpenAI Privacy Policy  
- NIST AI Risk Management Framework