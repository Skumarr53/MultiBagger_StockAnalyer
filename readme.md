

## 🟩 **Full, Cleaned-up README Content**

# AI Stock Picker

**Production-grade pipeline for identifying multi-bagger small-cap stocks in India using LLMs, sentiment analysis, and financial screening.**

---

## ⚙️ Project Structure


```
ai\_stock\_picker/
├── config/           # Hydra + Pydantic config files & models
├── data\_ingestion/   # Forum scraping, financial APIs
├── preprocessing/    # Text cleaning and normalization
├── summarization/    # LLM-based summarization
├── sentiment\_analysis/ # Sentiment scoring
├── financial\_data/   # Fetch and parse company fundamentals
├── screening\_ml/     # Rule-based + ML-driven screening
├── knowledge\_graph/  # Neo4j knowledge graph builder
├── rag\_pipeline/     # Vector store and RAG answer generator
├── dashboard/        # Streamlit app
├── utils/            # Logging, error handling, helpers
├── tests/            # Unit and integration tests
├── orchestrator.py   # Pipeline integration (root for CLI use)
├── Dockerfile        # Multi-env, CPU/GPU ready
├── requirements.txt  # (Explicit pins, modern, for uv/pip)
├── pyproject.toml    # Poetry + PEP 621 dependency management
├── .env.template     # Environment variable template
└── .github/workflows/ci.yml # CI/CD pipeline

```

---

## 🚀 Setup Instructions

1. **Clone & create environment:**
```bash
   git clone <your_repo_url>
   cd ai_stock_picker
   python3 -m venv .venv
   source .venv/bin/activate
   pip install uv poetry
   uv pip install -r requirements.txt
   # or: poetry install --extras cpu    # For GPU: poetry install --extras gpu
```

2. **Install external tools:**

   * [spaCy models](https://spacy.io/usage/models): `python -m spacy download en_core_web_sm`
   * [Neo4j](https://neo4j.com/download/) (local or cloud instance)

3. **Configure your environment:**

   * Copy `.env.template` to `.env` and fill in all keys/secrets.
   * Update `config/config.yaml` for pipeline options, API keys, and scraping parameters.
   * Edit `config/logging.yaml` for logging setup.

---

## 🐳 Docker (CPU/GPU)

* **CPU (default):**

  ```bash
  docker build -t ai-stock-picker .
  docker run -p 8501:8501 --env-file .env ai-stock-picker
  ```
* **GPU:**

  * Uncomment the `FROM nvidia/cuda:...` and `faiss-gpu`/`torch` lines in Dockerfile.
  * Make sure you have NVIDIA runtime (nvidia-docker2).

  ```bash
  docker build -t ai-stock-picker-gpu .
  docker run --gpus all -p 8501:8501 --env-file .env ai-stock-picker-gpu
  ```
* **CMDs:**

  * By default runs Streamlit dashboard (`dashboard/app.py`).
  * For end-to-end batch run: change Dockerfile `CMD` to `["python", "orchestrator.py"]`

---

## ▶️ Running the Pipeline

Full refresh:

```bash
python orchestrator.py
```

Or use Docker with the `CMD` switch above.

---

## 🖥️ Dashboard

Launch locally:

```bash
streamlit run dashboard/app.py
```

Or via Docker (as above).

---

## 🏗️ CI/CD Pipeline

* Config in `.github/workflows/ci.yml`
* **Runs:**

  * `uv` and `poetry` installs
  * Automated tests, lint, type and format checks on push/PR

---

## 📦 Advanced Dependency Management

* All dependencies pinned in `requirements.txt` for reproducibility.
* `pyproject.toml` manages extras:

  * CPU (default): `poetry install --extras cpu`
  * GPU (for CUDA): `poetry install --extras gpu`
* Use uv, poetry, or pip as preferred.

---

## 📊 Architecture Diagram

```
[Forum/API Scrapers]   [Financial APIs]     [Scheduler (cron/Airflow)]
        |                      |                        |
        |-------->[Preprocessing/Text Cleaning]<---------|
        |                      |
  [Summarization]       [Financial Parsing]
        |                      |
     [Sentiment]           [Screening]
        |                      |
        |------->[Knowledge Graph]<-----------|
        |                                     |
   [RAG Vector DB]<---------------------------|
        |                                     |
     [Streamlit Dashboard UI]<----------------|
```

---

## 🧑‍💻 Usage Pattern

* **Customize config:** Point to forum category, set API keys.
* **Plug in more companies:** Update symbols in orchestrator.
* **Model upgrades:** Swap Hugging Face models in `summarizer.py`, `sentiment.py`.
* **Scale up:** Extend orchestrator, parallelize, add alerts or analytics.
* **Visualize:** Use dashboard for insights.

---

## 🏆 Best Practices Used

* Modular, maintainable, type-annotated code.
* Logging and error handling everywhere.
* Configurable, ready for CI/CD, containerization, and cloud deployment.

---

## 🔐 Secrets Management

* Use `.env.template` (copy to `.env`) for all secrets/API keys.
* **Never commit `.env` to source control.**
* For production, use cloud secret managers (AWS Secrets Manager, GCP Secret Manager, etc.).

---

For module details or custom deployment, see module-level docstrings or raise an issue in the repo,.


