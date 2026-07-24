# SocialPulse 🚀

**SocialPulse** is a data collection, NLP analysis, and API platform built to fetch, process, analyze, and serve insights on Hacker News stories in real time. 

It combines asynchronous ETL data collection, dual VADER & RoBERTa sentiment analysis, vector embeddings storage in PostgreSQL (`pgvector`), ML score predictions, and a high-performance RESTful API powered by FastAPI.

---

## 🌟 Key Features

- **⚡ Async Data Collection**: High-speed asynchronous fetching of Hacker News stories using `aiohttp` & `requests`.
- **🤖 Dual-Model Sentiment Analysis**:
  - Fast rule-based sentiment scoring via **VADER**.
  - Deep transformer-based sentiment classification using **RoBERTa** (`twitter-roberta-base-sentiment-latest`).
- **🗄️ Multi-Storage Architecture**:
  - Raw & processed data stored in **CSV** and compressed **Parquet** format.
  - Relational & vector database storage using **PostgreSQL** with **pgvector** support (768-dimensional embeddings).
- **📊 Network Analysis & Predictor**:
  - Interactive social network graph generation with `PyVis` and `NetworkX` (not smoothly integrated yet, in test stage right now).
  - Machine Learning score prediction pipelines using `XGBoost` & `scikit-learn`.
- **🔌 RESTful API**: Built with **FastAPI** to serve story feeds, aggregated stats, daily rankings, sentiment trends, and trigger collection workflows.

---

## 🏗 Project Architecture

```
socialpulse/
├── analysis/           # Sentiment analysis, EDA, graph visualizations, and ML predictor
│   ├── eda.py          # Data exploration and statistics
│   ├── graph.py        # PyVis network graph generator
│   ├── predictor.py    # XGBoost / Scikit-Learn score models
│   └── sentiment.py    # VADER & RoBERTa sentiment engines
├── api/                # FastAPI application
│   ├── main.py         # REST endpoints & middleware
│   └── schemas.py      # Pydantic response models
├── collector/          # Data collection clients
│   └── hn_client.py    # Asynchronous Hacker News Firebase API client
├── storage/            # Data cleaning and persistence handlers
│   ├── cleaner.py      # Data cleaning pipeline
│   ├── database.py     # SQLAlchemy connection engine
│   ├── db_store.py     # PostgreSQL & pgvector storage logic
│   └── store.py        # CSV & Parquet file saving utilities
├── tests/              # Automated pytest test suite
│   ├── test_analyse_sentiment.py
│   └── test_hn_client.py
├── data/               # Raw and processed storage directories
├── config.py           # Configuration parameters
├── init.sql            # Database schema with pgvector initialization
├── docker-compose.yml  # PostgreSQL & API multi-container setup
├── Dockerfile          # Container specification for SocialPulse API
├── pyproject.toml      # Project metadata & dependencies (uv / pip)
└── main.py             # CLI runner for collection & processing ETL
```

---

## 🛠️ Requirements & Prerequisites

- **Python**: `>= 3.14` (or standard `Python 3.10+`)
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) or standard `pip`
- **Database**: PostgreSQL 15+ with `pgvector` extension (or Docker)

---

## 🚀 Quick Start

### 1. Clone the Repository & Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using standard Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r pyproject.toml
```

### 2. Environment Setup

Copy `.env.example` to `.env` and configure your database settings:
```bash
cp .env.example .env
```

Default configuration:
```env
DB_URL=postgresql://postgres:postgres@localhost:5433/socialpulse
```

### 3. Launch Database Service

Run PostgreSQL with `pgvector` using Docker Compose:
```bash
docker compose up db -d
```

---

## 💻 Usage

### Run ETL Pipeline via CLI

To collect top stories from Hacker News, process them, analyze sentiment, and store them into Parquet & PostgreSQL:

```bash
uv run main.py
```

### Start the FastAPI Server

```bash
uv run uvicorn api.main:app --reload
```

Once running, access the API endpoints and interactive documentation:
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/stories` | List top stories with optional sentiment filter (`positive`, `negative`, `neutral`) |
| `GET` | `/stories/{id}` | Get details of a specific story |
| `GET` | `/trends/sentiment` | Fetch daily average sentiment trends over a specified period |
| `GET` | `/stats` | Aggregate system metrics (total stories, top story, active author) |
| `GET` | `/stories/rankings` | Daily top N story rankings |
| `GET` | `/collect` | Trigger live Hacker News data collection |
| `GET` | `/reprocess` | Run RoBERTa model reprocessing on unanalyzed stories |
| `GET` | `/enrich` | Compute and store vector embeddings for stories |

---

## 🐳 Docker Deployment

To build and launch the full stack (PostgreSQL + FastAPI server) in Docker:

```bash
docker compose up --build -d
```

The API will be available at `http://localhost:8000`.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
