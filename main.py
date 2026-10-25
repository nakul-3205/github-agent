from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from cloner import clone_repo, cleanup_repo
from parser import parse_repo
from embedder import index_chunks
from main_test import search
from llm import ask_llm
from auth_utils import register_user, authenticate_user, decode_token

app = FastAPI()

class LoadRequest(BaseModel):
    github_url: str

class ChatRequest(BaseModel):
    question: str

class AuthRequest(BaseModel):
    username: str
    password: str


def require_auth(authorization: str = Header(default="")):
    """FastAPI dependency: validates 'Bearer <token>' header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    data = decode_token(authorization.removeprefix("Bearer ").strip())
    if data is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return data


@app.post("/auth/register")
def register(req: AuthRequest):
    ok, message = register_user(req.username, req.password)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"status": "created"}


@app.post("/auth/login")
def login(req: AuthRequest):
    ok, result = authenticate_user(req.username, req.password)
    if not ok:
        raise HTTPException(status_code=401, detail=result)
    return {"status": "ok", "token": result}


@app.get("/auth/me")
def me(user: dict = Depends(require_auth)):
    return {"username": user["username"]}


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