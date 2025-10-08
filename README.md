# AI News Analyst

An intelligent news analysis system that combines Retrieval-Augmented Generation (RAG) with Wikipedia search to provide comprehensive answers about current events and general knowledge.

## 🏗️ Project Structure

```
AI-News-Analyst/
├── src/                          # Source code
│   ├── data_sources/            # Data source modules
│   │   ├── techmeme_rss_parser.py    # Techmeme RSS feed parser
│   │   └── wikipedia_search.py       # Wikipedia search functionality
│   ├── rag/                     # RAG (Retrieval-Augmented Generation)
│   │   └── vector_store_manager.py   # Vector database management
│   ├── workflow/               # Workflow orchestration
│   │   └── news_analysis_workflow.py # Main LangGraph workflow
│   └── utils/                   # Utility functions
│       └── config.py            # Configuration settings
├── data/                        # Data storage
│   ├── vector_db/              # ChromaDB vector database
│   └── outputs/                # Generated outputs & results
├── notebooks/                   # Testing files
│   └── notebook_testing.ipynb  # Jupyter notebook for testing
├── docs/                        # Documentation
├── main.py                      # Main CLI entry point
├── evaluate.py                  # Evaluation script
├── test.py                      # Evaluation functions
├── EVALUATION.md               # Evaluation guide
└── README.md                    # This file
```

## 🚀 Features

- **Smart Routing**: Automatically determines whether to use RAG for recent news or Wikipedia for general knowledge
- **RAG Integration**: Retrieves and analyzes recent news from Techmeme RSS feeds
- **Wikipedia Search**: Accesses general knowledge and historical information
- **Vector Database**: Uses ChromaDB for efficient document storage and retrieval
- **LangGraph Workflow**: Orchestrates the entire analysis process

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## 🎯 Usage

### Web Interface (Recommended)

Run the simple web UI:
```bash
python app.py
```

Then open your browser to `http://localhost:7860`

### Command Line Interface

Run the main application:
```bash
python main.py
```

### Programmatic Usage

```python
from src.workflow.news_analysis_workflow import run_news_analysis

# Analyze a question
result = run_news_analysis("What are the latest developments in AI?")
print(result)
```

## 🔧 Components

### Data Sources
- **Techmeme RSS Parser** (`src/data_sources/techmeme_rss_parser.py`): Fetches and processes news from Techmeme RSS feeds
- **Wikipedia Search** (`src/data_sources/wikipedia_search.py`): Provides access to Wikipedia knowledge

### RAG System
- **Vector Store Manager** (`src/rag/vector_store_manager.py`): Manages ChromaDB vector database for news embeddings

### Workflow
- **News Analysis Workflow** (`src/workflow/news_analysis_workflow.py`): Main LangGraph workflow that orchestrates the entire process
- **Route Decision** (`src/workflow/route_decision.py`): Determines whether to use RAG or Wikipedia based on the query

## 🧪 Testing & Evaluation

Evaluate the system on the test dataset (20 examples):

```bash
# Run full evaluation on all 20 examples
python evaluate.py

# Run on a subset for faster testing
python evaluate.py --num-examples 5

# Save results for comparison
python evaluate.py --output data/outputs/baseline_v1.json
```

Compare performance across different runs:



## 📊 Data Flow

1. **User Input**: User asks a question
2. **Routing**: System determines if question is about recent news or general knowledge
3. **Data Retrieval**: 
   - For news: Retrieves relevant articles from vector database
   - For general knowledge: Searches Wikipedia
4. **Analysis**: LLM processes the retrieved information
5. **Response**: Returns comprehensive answer

