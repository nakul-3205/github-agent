from fastapi import FastAPI
from pydantic import BaseModel
from cloner import clone_repo, cleanup_repo
from parser import parse_repo
from embedder import index_chunks
from main_test import search
from llm import ask_llm

app = FastAPI()

class LoadRequest(BaseModel):
    github_url: str

class ChatRequest(BaseModel):
    question: str

@app.post("/load")
def load_repo(req: LoadRequest):
    path = clone_repo(req.github_url)
    chunks = parse_repo(path)
    count = index_chunks(chunks)
    cleanup_repo(path)
    return {"status": "indexed", "chunks": count}

@app.post("/chat")
def chat(req: ChatRequest):
    chunks = search(req.question, top_k=5)
    answer = ask_llm(req.question, chunks)
    return {"answer": answer, "sources": chunks}