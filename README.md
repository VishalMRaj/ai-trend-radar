# AI Trend Radar 📡

A personal, automated system that monitors AI/agentic architecture developments weekly, deduplicates and scores them against an editable work profile, and produces a short, digestible static HTML report.

## Architecture

This project is built using a lightweight pipeline orchestrated entirely in Python:
- **Connectors:** Plugabble modules (`arXiv`, `RSS`, `GitHub Trending`) normalize inputs into a common `Item` schema.
- **Pipeline:** Built with **LangGraph**, it executes four main nodes:
  - **Dedup:** Embedding-based deduplication against previously seen items to avoid noise.
  - **Classify:** LLM-based categorization of each item (`architecture-pattern`, `tooling`, `research`, `product-launch`).
  - **Score:** Embedding similarity matching against keywords defined in `config/profile.yaml`.
  - **Summarize:** LLM-based plain-language paraphrased summary (never verbatim).
- **Storage:** Simple `SQLite` instance (`items.db`) for tracking state between runs. Swappable via `ItemStore` interface.
- **Delivery:** Renders the highest-scoring items into a static HTML page saved to `output/`.

## Running Locally

1. Create a virtual environment and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure LLM Provider:
   - This project uses Google Vertex AI (Gemini) by default. Ensure your environment has valid Application Default Credentials or the `GOOGLE_APPLICATION_CREDENTIALS` environment variable set.
   - For fallback scenarios, modify `src/main.py` or `.env` configuration.
3. Configure your profile and sources:
   - Edit `config/profile.yaml` with keywords most relevant to you.
   - Edit `config/sources.yaml` to adjust arXiv categories or RSS feeds.
4. Run the pipeline:
   ```bash
   export PYTHONPATH=$(pwd)
   python src/main.py
   ```
5. View your digest:
   Open the generated HTML file located in `output/` in any web browser.

## Open Decisions & Trade-offs

- **Scheduler:** Defaults to GitHub Actions (zero infra, free) for V1. It runs weekly and commits the resulting HTML digest to the repository. The alternative GCP path (Cloud Scheduler + Cloud Run) can easily be adopted later by containerizing `main.py` and pushing to Artifact Registry.
- **LLM Provider:** Uses Vertex AI/Gemini since it matches existing GCP stacks. It degrades gracefully to a Fake LLM if credentials are not found (useful for testing logic).
- **Vector Store:** Deduplication and scoring use in-memory Numpy-based cosine similarity instead of a dedicated vector database, keeping the infrastructure requirements at zero for initial item volumes. SQLite handles raw data persistence.

## Testing
Run unit tests with pytest:
```bash
pytest tests/
```
