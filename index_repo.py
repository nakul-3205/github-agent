from cloner import clone_repo, cleanup_repo
from parser import parse_repo
from embedder import index_chunks

repo_url = "https://github.com/karpathy/micrograd"

print("Cloning repo...")
path = clone_repo(repo_url)

print("Parsing repo...")
chunks = parse_repo(path)
print(f"Found {len(chunks)} chunks.")

print("Embedding and storing in Qdrant...")
count = index_chunks(chunks)
print(f"Stored {count} chunks in Qdrant.")

cleanup_repo(path)
print("Done. Temp folder cleaned up.")