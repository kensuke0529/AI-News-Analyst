# AI News Analyst - MVP Summary

**Last Updated:** October 6, 2025  
**Version:** 1.0  

---

## Executive Summary

The AI News Analyst is an intelligent question-answering system that combines Retrieval-Augmented Generation (RAG) with Wikipedia search to provide comprehensive answers about both current events and general knowledge. Built using LangGraph for workflow orchestration, the system intelligently routes user queries to the appropriate knowledge source—either a real-time news database or Wikipedia—and generates contextually relevant responses using GPT-4o-mini.

**Current Performance Metrics:**
- **Routing Accuracy:** 100% (all 20 test cases route correctly)
- **Average Relevancy Score:** 6.7/10
- **Average Correctness Score:** 6.25/10
- **Average Response Time:** 13.42 seconds per query

The MVP successfully demonstrates the core functionality of intelligent routing and dual-source retrieval, though response quality and accuracy require optimization to meet production standards.

---

## Architecture Overview

### System Components

The application follows a modular architecture with clear separation of concerns:

1. **Workflow Orchestration Layer** (`src/workflow/`)
   - LangGraph-based state machine managing the complete query lifecycle
   - Intelligent routing logic using GPT-4o-mini
   - Conditional workflow execution based on routing decisions

2. **Data Source Layer** (`src/data_sources/`)
   - **Techmeme RSS Parser:** Fetches and processes tech news from Techmeme
   - **Wikipedia Integration:** Provides access to general knowledge via Wikipedia API

3. **RAG Layer** (`src/rag/`)
   - ChromaDB vector database for news article embeddings
   - OpenAI embeddings (text-embedding-3-small model)
   - Similarity-based retrieval with k=3 top results

4. **Evaluation Framework** (`evaluate.py`, `test.py`)
   - Automated testing on 20 curated test cases
   - GPT-4o as LLM judge for quality assessment
   - Comprehensive metrics tracking and reporting

### Technology Stack

**Core Technologies:**
- **LangChain/LangGraph:** Workflow orchestration and RAG implementation
- **OpenAI GPT-4o-mini:** Query routing and response generation
- **OpenAI GPT-4o:** Evaluation and judging
- **ChromaDB:** Vector database for news embeddings
- **BeautifulSoup:** HTML parsing from RSS feeds
- **Python 3.8+:** Primary development language

**Dependencies:**
- langchain, langchain-openai, langchain-community, langchain-chroma
- langgraph
- chromadb
- requests, beautifulsoup4
- python-dotenv

---

## System Flow

### Complete Request Lifecycle
```
User Query
    ↓
┌─────────────────────────┐
│   Router Node           │
│  (GPT-4o-mini decides)  │
└─────────┬───────────────┘
          │
          ├──→ "rag" (Recent News)        ├──→ "wiki" (General Knowledge)
          │                               │
   ┌──────▼──────────┐            ┌──────▼──────────┐
   │ RAG Processing  │            │ Wiki Processing │
   │ Node            │            │ Node            │
   ├─────────────────┤            ├─────────────────┤
   │1. Fetch RSS     │            │1. Query Wikipedia│
   │2. Embed docs    │            │   API            │
   │3. Vector search │            │2. Return article │
   │4. Retrieve k=3  │            │   content        │
   └──────┬──────────┘            └──────┬──────────┘
          │                               │
          └───────────┬───────────────────┘
                      ↓
              ┌───────────────┐
              │ Writing Node  │
              │ (GPT-4o-mini) │
              ├───────────────┤
              │ Synthesize    │
              │ final response│
              └───────┬───────┘
                      ↓
                  Response
```

### Detailed Flow Description

1. **Query Reception:** User submits a question via CLI or programmatic interface

2. **Intelligent Routing:**
   - Router node invokes GPT-4o-mini with specialized routing prompt
   - LLM analyzes query intent and determines if it requires recent news (RAG) or general knowledge (Wikipedia)
   - Returns binary decision: "rag" or "wiki"

3. **Data Retrieval - RAG Path:**
   - Fetches latest articles from Techmeme RSS feed
   - Parses and cleans HTML content
   - Chunks articles (100 chars, 10 char overlap)
   - Generates embeddings using OpenAI text-embedding-3-small
   - Stores/updates ChromaDB vector database (avoiding duplicates)
   - Performs similarity search to retrieve top 3 relevant chunks
   - Returns concatenated document context

4. **Data Retrieval - Wikipedia Path:**
   - Queries Wikipedia API with user's question
   - Retrieves comprehensive article content
   - Returns formatted Wikipedia text

5. **Response Generation:**
   - Writing node receives user query + retrieved context (RAG or Wiki)
   - GPT-4o-mini synthesizes comprehensive response
   - Integrates context information with natural language generation
   - Returns final answer to user

6. **State Management:**
   - LangGraph maintains state throughout workflow
   - State includes: prompt, rag_doc, wiki_doc, route_choice, response
   - Enables tracking and debugging of entire request lifecycle

---

## Current Implementation Status

### Completed Features

1. **Core Workflow:**
   - LangGraph state machine fully operational
   - Conditional routing based on LLM decision
   - Clean separation between RAG and Wikipedia paths

2. **RAG Pipeline:**
   - Techmeme RSS feed integration
   - Automatic article fetching and parsing
   - Vector embedding with OpenAI embeddings
   - ChromaDB persistence with duplicate detection
   - Similarity-based retrieval

3. **Wikipedia Integration:**
   - LangChain Wikipedia tool integration
   - Automatic article retrieval
   - Clean text extraction

4. **CLI Interface:**
   - Interactive command-line interface
   - Continuous query loop
   - Error handling and graceful exits

5. **Evaluation Framework:**
   - 20 curated test cases (10 RAG, 10 Wiki)
   - Automated routing accuracy measurement
   - LLM-as-judge for relevance and correctness scoring
   - Performance timing metrics
   - Category-based breakdown analysis
   - JSON result export for tracking improvements

### Current Performance Analysis

**Evaluation Results (20 Test Cases, October 6, 2025):**

#### Overall Metrics
- **Total Execution Time:** 268.39 seconds (4.5 minutes)
- **Average Time per Query:** 13.42 seconds
- **Range:** 7.37s (fastest) - 21.30s (slowest)

#### Quality Metrics
- **Routing Accuracy:** 100% (20/20 correct)
  - All queries correctly routed to RAG or Wikipedia
  - Router demonstrates strong intent classification

- **Relevancy Score:** 6.7/10 (Average)
  - Wiki queries: 9.3/10 (Excellent)
  - RAG queries: 4.0/10 (Needs Improvement)
  - **Gap Analysis:** 5.3 point difference indicates RAG context quality issues

- **Correctness Score:** 6.25/10 (Average)
  - Wiki queries: 9.5/10 (Excellent)
  - RAG queries: 3.0/10 (Poor)
  - **Gap Analysis:** 6.5 point difference - critical issue with RAG fact accuracy

#### Performance by Category

**General Knowledge (Wikipedia - 10 examples):**
- Routing Accuracy: 100%
- Avg Relevancy: 9.3/10 ✅
- Avg Correctness: 9.5/10 ✅
- Avg Time: 15.02s
- **Status:** Excellent performance, production-ready

**Recent News Categories (RAG - 10 examples):**

1. **Recent Funding (4 examples):**
   - Routing Accuracy: 100%
   - Avg Relevancy: 2.25/10 ❌
   - Avg Correctness: 1.75/10 ❌
   - Avg Time: 9.37s
   - **Issue:** Retrieving wrong companies/incorrect funding amounts

2. **Recent Business (3 examples):**
   - Routing Accuracy: 100%
   - Avg Relevancy: 4.67/10 ⚠️
   - Avg Correctness: 4.0/10 ⚠️
   - Avg Time: 11.81s
   - **Issue:** Partial information, missing key details

3. **Recent M&A (2 examples):**
   - Routing Accuracy: 100%
   - Avg Relevancy: 1.0/10 ❌
   - Avg Correctness: 1.0/10 ❌
   - Avg Time: 8.42s
   - **Issue:** Complete misses on acquisition targets

4. **Recent Market (1 example):**
   - Routing: Correct
   - Relevancy: 9.0/10 ✅
   - Correctness: 4.0/10 ⚠️
   - **Issue:** Good context but factual inaccuracies

5. **Recent Regulation (1 example):**
   - Routing: Correct
   - Relevancy: 4.0/10 ⚠️
   - Correctness: 4.0/10 ⚠️
   - **Issue:** Generic response, missing specific details

### Critical Issues Identified

1. **RAG Retrieval Quality (P0 - Critical):**
   - Vector search returning irrelevant or outdated articles
   - Wrong company names in funding queries (e.g., retrieved French Heidi Health instead of Melbourne-based)
   - Missing specific deals and acquisitions entirely
   - **Root Cause:** Small chunk size (100 chars) losing semantic context

2. **Response Hallucination (P0 - Critical):**
   - LLM generating plausible but incorrect information when context is weak
   - Filling gaps with fabricated details
   - **Root Cause:** Insufficient grounding in retrieved context

3. **Data Freshness (P1 - High):**
   - Techmeme RSS may not contain all test case information
   - No verification of article age or relevance
   - **Root Cause:** Single data source limitation

4. **Performance Bottleneck (P2 - Medium):**
   - 13.42s average response time (target: <10s)
   - Wikipedia queries averaging 15s (slower than RAG at 11.6s)
   - **Root Cause:** Sequential API calls without optimization

5. **Evaluation Metric Bug (P3 - Low):**
   - Summary shows 0.0% routing accuracy despite individual results showing 100%
   - **Root Cause:** Potential aggregation logic error in evaluate.py


