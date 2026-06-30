import duckdb
import numpy as np
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_PATH = REPO_ROOT / "data" / "debates.parquet"
EMBEDDINGS_PATH = REPO_ROOT / "data" / "test_embeddings.npy"
IDS_PATH = REPO_ROOT / "data" / "test_embedding_ids.npy"


def load_sample(n=500, seed=42):
    """Sample speech_id + text without loading the full corpus into memory."""
    con = duckdb.connect()
    query = f"""
        SELECT speech_id, text
        FROM '{DATA_PATH}'
        WHERE LENGTH(text) > 0
        USING SAMPLE {n} (reservoir, {seed})
    """
    return con.execute(query).df()


def fetch_text_by_ids(speech_ids):
    """Look up text for a known set of speech_ids, without loading the full corpus."""
    con = duckdb.connect()
    ids = [int(i) for i in speech_ids]
    query = f"""
        SELECT speech_id, text
        FROM '{DATA_PATH}'
        WHERE speech_id IN (SELECT * FROM UNNEST(?))
    """
    return con.execute(query, [ids]).df()


def embed_speeches(df, model):
    texts = df['text'].tolist()
    vectors = model.encode(texts, show_progress_bar=True)
    return df['speech_id'].to_numpy(), vectors


def save_embeddings(speech_ids, vectors):
    np.save(IDS_PATH, speech_ids)
    np.save(EMBEDDINGS_PATH, vectors)


def load_embeddings():
    speech_ids = np.load(IDS_PATH)
    vectors = np.load(EMBEDDINGS_PATH)
    return speech_ids, vectors


def search(query, model, speech_ids, vectors, top_k=5):
    query_vec = model.encode([query])[0]
    norms = np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vec)
    sims = (vectors @ query_vec) / norms
    top_idx = np.argsort(sims)[::-1][:top_k]
    top_ids = [speech_ids[i] for i in top_idx]

    text_df = fetch_text_by_ids(top_ids)
    text_lookup = dict(zip(text_df['speech_id'], text_df['text']))

    results = []
    for idx in top_idx:
        sid = speech_ids[idx]
        results.append((sid, sims[idx], text_lookup.get(sid, "")))
    return results


if __name__ == "__main__":
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

    if EMBEDDINGS_PATH.exists() and IDS_PATH.exists():
        speech_ids, vectors = load_embeddings()
    else:
        df = load_sample(n=1000)
        speech_ids, vectors = embed_speeches(df, model)
        save_embeddings(speech_ids, vectors)

    query = "climate change and renewable energy"
    results = search(query, model, speech_ids, vectors, top_k=5)

    for sid, score, text in results:
        print(f"\n[{sid}] score={score:.3f}")
        print(text[:300])