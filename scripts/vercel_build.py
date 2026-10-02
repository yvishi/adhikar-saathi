"""Vercel build step: bake the multilingual search model and card index into the function bundle.

The runtime file system is read-only, so both must exist before deploy. Never fails the build:
if anything goes wrong the app falls back to keyword (BM25) search on its own.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> None:
    try:
        from fastembed import TextEmbedding

        from app.backend import retrieval

        TextEmbedding(retrieval.MODEL_NAME, cache_dir=str(retrieval.MODEL_DIR))
        mode = retrieval.Retriever().mode
        print(f"[vercel_build] search model ready, retriever mode: {mode}")
    except Exception as e:  # keep the deploy alive; BM25 fallback still works
        print(f"[vercel_build] WARNING: search model not baked ({e}); app will use keyword search.")


if __name__ == "__main__":
    main()
