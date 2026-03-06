# Payment Compliance & Policy Auditor Specification

## Overview
A high-scale, production-grade system for auditing payment transactions against strict compliance policies. Designed for efficiency, reliability, and cost-awareness, this project employs an agentic stateful flow to process structured constraints and unstructured policy data.

## Architecture Standards

### 1. Modularity
The application follows a strictly modular architecture:
- **API Routes (`/src/api`)**: Asynchronous FastAPI endpoints managing HTTP lifecycles. All endpoints strictly utilize `async`/`await`.
- **Inference Logic (`/src/inference`)**: Orchestration of the agentic workflows and LLM routing using `LangGraph`.
- **Retriever Logic (`/src/retrieval`)**: Handles fetching constraints and policies using a Hybrid Search approach.

### 2. Typing
- All inbound requests, outbound responses, internal state schemas, and database mappings are defined purely via `Pydantic V2`. We do not use `Any` typings.

### 3. Asynchronous Pattern
- All APIs, database drivers (`aiosqlite`/`asyncpg`), LLM calls (`langchain-google-genai`), and Vector searches use `async`/`await` for maximum scalability without blocking the event loop.

## Core Components

### 1. Hybrid Search (Retrieval)
Our retrieval step combines two mechanisms to fulfill "Production-Ready RAG":
- **SQL Data (Deterministic)**: Querying strict rules, thresholds, amounts, and limits (e.g., $10,000 daily transfer limits) via standard SQL relations. 
- **Vector Database (Semantic)**: Querying nuanced compliance policy documents (e.g., restricted entities, AML descriptions, or subjective risk patterns).
  - **Tooling**: Pinecone via the standard Python client.
  - **Chunking Strategy**: All ingested policy text is processed via `RecursiveCharacterTextSplitter`.

### 2. Orchestration & LLM Router (Inference)
The core auditing engine is implemented as a state-machine using LangGraph:
- **State Definition**: Tracks the incoming transaction, retrieved policies, extracted flags, and final verdict.
- **Model Router Pattern**:
  - `Gemini-3-Flash`: Responsible for fast, inexpensive operations. It categorizes the transaction intent, performs binary classification (e.g., identifying standard transfer versus a complex/high-risk one), and selects which retrieval tools to fire.
  - `Gemini-3-Pro`: Responsible for complex, deep reasoning. Analyzes the outputs of the hybrid search, evaluates nuanced policies, and acts as the strict final auditor.

### 3. Frontend & Human-in-the-Loop
An operational dashboard created with `Streamlit` allows a human reviewer to:
- Monitor the flow logs.
- Override borderline compliance flags (Human-in-the-Loop).

## Evaluation & Testing Setup

### LLM-as-a-Judge (Promptfoo Integration)
All new features are assessed via Promptfoo integration located in `/evals/config.yaml`.
**Criteria**:
- The promptfoo suite implements an "LLM-as-a-Judge" rubric.
- It asserts whether our system accurately categorizes the payload, correctly queries the hybrid store, and produces an explanation supported *solely* by retrieved context.

### Regression Testing
A `golden_dataset.json` contains historic verified query-response pairs across multiple edge cases (Over-limits, sanctions matches, etc.). The promptfoo evals run constantly against this golden dataset to detect regressions.
