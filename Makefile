.PHONY: setup test lint smoke ingest eval dev

setup:
	uv sync --extra dev
	uv run python scripts/install_paths.py

fetch-corpus:
	bash scripts/fetch_corpus.sh

test:
	uv run pytest -q

lint:
	uv run ruff check .

# One real Token Factory call per tier; prints model, tokens and cost. Requires NEBIUS_API_KEY in .env.
smoke:
	uv run python scripts/smoke.py

ingest:
	uv run python -m antidote_retrieval.ingest --manifest data/manifest.yaml --out data/index

eval:
	uv run python -m antidote_eval.run --out eval/results

dev:
	uv run uvicorn antidote_api.main:app --reload --port 8000
