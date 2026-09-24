# Codebase Chat — RAG for Code

Chat with any GitHub repository using natural language.

Paste a repository URL and ask questions like:

- "How does backpropagation work in this project?"
- "What does the Neuron class do?"
- "Where is the training loop implemented?"

Codebase Chat provides accurate, plain-English answers grounded in the actual source code instead of generating hallucinated explanations.

---

## 🚀 Features

- 🔍 **Chat with any GitHub repository**
- 🧠 **RAG-based code understanding pipeline**
- 🌳 **AST-based intelligent code chunking**
- 🔎 **Hybrid retrieval (Vector Search + BM25)**
- ⚡ **FastAPI backend architecture**
- 💾 **Qdrant Cloud vector database**
- 🤖 **Gemini-powered grounded answers**
- 📊 **Retrieval evaluation pipeline**
- 📌 **Source code references with similarity scores**

---

# How It Works

The system follows a complete Retrieval-Augmented Generation (RAG) pipeline:

```
GitHub Repository
        |
        ↓
Clone Repository
        |
        ↓
AST Code Parser
        |
        ↓
Code Chunk Generation
        |
        ↓
Embedding Generation
        |
        ↓
Qdrant Vector Storage
        |
        ↓
Hybrid Retrieval
        |
        ↓
Gemini LLM
        |
        ↓
Grounded Answer + Source References
```

---

# RAG Pipeline

## 1. Clone

Downloads the target GitHub repository locally using GitPython.

---

## 2. Parse

The repository is analyzed using Python's built-in `ast` module.

Instead of splitting code by characters or fixed line length, the system extracts meaningful programming structures:

- Functions
- Methods
- Classes
- File paths
- Line numbers

Each chunk represents a complete logical code unit.

---

## 3. Embed

Each code chunk is converted into vector embeddings using:

**BAAI/bge-small-en-v1.5**

Advantages:

- Free
- Locally runnable
- Optimized for semantic similarity search

---

## 4. Store

Code chunks and embeddings are stored in:

**Qdrant Cloud**

Qdrant enables fast similarity search over large codebases.

---

## 5. Retrieve

The system uses **hybrid search** instead of only semantic search.

It combines:

### Semantic Search

Uses vector embeddings to understand conceptual similarity.

Example:

> "Where is gradient calculation happening?"

can retrieve:

```python
backward()
```

even without exact keyword matching.


### BM25 Keyword Search

Finds exact matches:

- Function names
- Variable names
- Class names
- File names


### Reciprocal Rank Fusion (RRF)

The results from both retrieval methods are combined using RRF to improve accuracy.

---

## 6. Answer Generation

Retrieved code chunks are passed to:

**Google Gemini**

The LLM only receives relevant retrieved context.

It does not access the entire repository.

This helps:

- Reduce hallucination
- Maintain accuracy
- Handle large repositories

---

# Architecture

The application uses a backend/frontend separated architecture.

```
                 Streamlit UI
                      |
                      |
                      ↓
                FastAPI Backend
                      |
        --------------------------------
        |              |               |
        ↓              ↓               ↓
   AST Parser     Retriever        Gemini
        |              |
        ↓              ↓
   Code Chunks     Qdrant Cloud
                    +
                   BM25
```

---

# Backend API

## Load Repository

```
POST /load
```

Responsibilities:

- Clone repository
- Parse source files
- Generate embeddings
- Store vectors


## Chat

```
POST /chat
```

Responsibilities:

- Convert question into embedding
- Perform hybrid retrieval
- Generate grounded response

---

# Why AST-Based Chunking?

Traditional text splitting:

```
Every 500 characters
Every 100 lines
```

can break code logic.

Example:

```python
if condition:
    process_data()

return result
```

A naive splitter may separate the condition from its return statement.

AST parsing guarantees:

- Complete functions
- Complete methods
- Meaningful semantic units

This creates better embeddings and improves retrieval quality.

---

# Why Hybrid Search?

Semantic search understands meaning but may miss exact identifiers.

Example:

Question:

```
Where is the Neuron class defined?
```

Keyword search can directly find:

```
class Neuron:
```

Semantic search understands:

```
forward propagation
gradient calculation
backward pass
```

Combining both gives stronger code retrieval.

---

# Evaluation

A dedicated evaluation pipeline measures retrieval performance.

Run:

```bash
python eval.py
```

Results:

| Metric | Score |
|--------|-------|
| Hit Rate @5 | 100% |
| Recall @5 | 90% |
| Precision @5 | 32.7% |
| F1 @5 | 0.457 |
| Mean Reciprocal Rank | 0.480 |
| Hallucination Rate | 0% |

### Hallucination Check

The evaluation verifies:

- Generated answers reference existing code
- No fake functions are mentioned
- No invented variables/classes are produced

---

# Tech Stack

| Component | Technology |
|----------|------------|
| Backend API | FastAPI |
| Frontend | Streamlit |
| Language | Python |
| Code Parsing | Python AST |
| Repository Cloning | GitPython |
| Embeddings | BAAI/bge-small-en-v1.5 |
| Semantic Search | Sentence Transformers |
| Keyword Search | BM25 |
| Vector Database | Qdrant Cloud |
| LLM | Google Gemini |
| Evaluation | Custom RAG Evaluation Pipeline |

---

# Installation

Clone repository:

```bash
git clone https://github.com/Sahil9914/codebase-chat.git

cd codebase-chat
```

Create virtual environment:

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Setup

Create `.env` file:

```
GEMINI_API_KEY=your_api_key_here

QDRANT_URL=your_qdrant_url

QDRANT_API_KEY=your_qdrant_key
```

---

# Running the Application

## Start Backend

```bash
uvicorn main:app --reload
```

Backend runs on:

```
http://localhost:8000
```

---

## Start Frontend

Open another terminal:

```bash
streamlit run app.py
```

---

# Usage

1. Open the Streamlit application
2. Paste a GitHub repository URL

Example:

```
https://github.com/karpathy/micrograd
```

3. Click:

```
Load Repo
```

The system will:

- Clone repository
- Parse code
- Generate embeddings
- Store vectors


4. Ask questions:

Example:

```
Explain how backpropagation works.
```

The response includes:

- Natural language explanation
- Retrieved source files
- Similarity scores
- Relevant code snippets

---

# Design Decisions

## Function-Level Chunking

Functions are used as the smallest retrieval unit.

Why?

Class-level chunks contain multiple unrelated methods, reducing search precision.

Each function receives its own embedding while class information is stored as metadata.

---

## Local Embeddings Instead of API Embeddings

Advantages:

- No embedding API cost
- Faster development
- Better privacy
- Fully controlled pipeline

---

## Gemini Only for Generation

Gemini is responsible only for:

- Understanding retrieved context
- Generating explanations

It never receives the entire repository.

---

## Qdrant Cloud Instead of Local Database

Benefits:

- No local database management
- Scalable storage
- Deployment ready

---

# Future Improvements

- Support multiple programming languages
- Add repository-level dependency graphs
- Add code execution sandbox
- Add GitHub authentication
- Add conversational memory
- Improve reranking with cross-encoder models

---

# Author

**Sahil Chalotra**

GitHub: https://github.com/Sahil9914

LinkedIn: [https://linkedin.com/](https://www.linkedin.com/in/sahilchalotra/)
"# github-agent" 
