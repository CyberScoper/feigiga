#!/usr/bin/env python3
"""FastAPI стартер для арены. Поднимает /api/* с CORS = *."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Vibe Arena API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunIn(BaseModel):
    input: str

class RunOut(BaseModel):
    input: str
    length: int
    reversed: str

@app.get("/")
def health():
    return {"ok": True, "service": "vibe-arena-api"}

@app.post("/api/run", response_model=RunOut)
def run(payload: RunIn):
    s = payload.input
    return RunOut(input=s, length=len(s), reversed=s[::-1])

# === ниже добавляй свои эндпоинты ===

# @app.get("/api/items")
# def list_items():
#     return [{"id": 1, "name": "first"}]
