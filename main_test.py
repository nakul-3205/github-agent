import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from llm import ask_llm

load_dotenv()

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = "code_chunks"


def get_all_chunks():
    """Fetch every chunk's payload from Qdrant, needed for BM25."""
    all_points = []
    next_offset = None
    while True:
        points, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=256,
            offset=next_offset,
            with_payload=True,
        )
        all_points.extend(points)
        if next_offset is None:
            break
    return all_points


def semantic_search(query, top_k=10):
    query_vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    )
    return [(point.payload, point.score) for point in results.points]


def keyword_search(query, top_k=10):
    all_points = get_all_chunks()
    corpus = [point.payload["code"] for point in all_points]
    tokenized_corpus = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(zip(all_points, scores), key=lambda x: x[1], reverse=True)
    return [(point.payload, score) for point, score in ranked[:top_k]]


def reciprocal_rank_fusion(semantic_results, keyword_results, k=60):
    """Merge two ranked lists into one, using Reciprocal Rank Fusion."""
    scores = {}
    chunk_lookup = {}

    for rank, (payload, _) in enumerate(semantic_results):
        key = (payload["file"], payload["function"])
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        chunk_lookup[key] = payload

    for rank, (payload, _) in enumerate(keyword_results):
        key = (payload["file"], payload["function"])
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        chunk_lookup[key] = payload

    ranked_keys = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {**chunk_lookup[key], "score": round(score, 4)}
        for key, score in ranked_keys
    ]


def search(query, top_k=3):
    semantic_results = semantic_search(query, top_k=10)
    keyword_results = keyword_search(query, top_k=10)
    fused = reciprocal_rank_fusion(semantic_results, keyword_results)
    return fused[:top_k]


if __name__ == "__main__":
    question = input("Ask something about the code: ")
    chunks = search(question, top_k=5)
    answer = ask_llm(question, chunks)
    print("\n--- Answer ---")
    print(answer)