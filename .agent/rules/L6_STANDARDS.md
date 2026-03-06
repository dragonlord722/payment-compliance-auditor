---
trigger: always_on
---

# L6 Applied AI Development Rules

## Context
I am an L6 Software Engineer with a background in Payments. We are building a high-scale "Payment Compliance Auditor." Efficiency and reliability are paramount.

## Architecture Standards
- **Async First:** Use `async/await` for all FastAPI endpoints and LLM calls.
- **Strict Typing:** Use Pydantic V2 for all data models. No `Any` types.
- **Modularity:** Separate "Inference Logic," "Retriever Logic," and "API Routes."
- **Production-Ready RAG:** - Always use `RecursiveCharacterTextSplitter` for chunking.
    - Implement a "Hybrid Search" strategy (SQL + Vector).
- **Cost Awareness:** - Implement an "LLM Router" pattern.
    - Default to `Gemini-3-Flash` for classification and `Gemini-3-Pro` for reasoning.

## Evaluation & Testing
- **No Manual Verification:** Do not ask me to "check if it works." 
- **Promptfoo Integration:** Every new feature must include a corresponding `promptfoo` test case in `/evals/config.yaml`.
- **Golden Dataset:** Maintain a `golden_dataset.json` for regression testing.

## Communication Style
- **Minimalist Outputs:** Do not explain basic Python concepts. 
- **Plan First:** For complex tasks, generate a "Plan Artifact" before writing code.
- **Quota Preservation:** Avoid redundant file reads. If you've read a file once in a session, assume you know its content unless I say it changed.