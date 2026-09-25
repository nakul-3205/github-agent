import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from parser import parse_file

load_dotenv()

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = "code_chunks"

def setup_collection():
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

def embed_and_store(chunks):
    points = []
    for i, chunk in enumerate(chunks):
        vector = model.encode(chunk["code"]).tolist()
        points.append(
            PointStruct(
                id=i,
                vector=vector,
                payload=chunk,
            )
        )
    client.upsert(collection_name=COLLECTION_NAME, points=points)


def index_chunks(chunks):
    setup_collection()
    embed_and_store(chunks)
    return len(chunks)


if __name__ == "__main__":
    setup_collection()
    chunks = parse_file("sample.py")
    embed_and_store(chunks)
    print(f"Stored {len(chunks)} chunks in Qdrant.")