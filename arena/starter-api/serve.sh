#!/usr/bin/env bash
# FastAPI на :8000 с hot-reload.
cd "$(dirname "$0")"
echo "→ http://localhost:8000  (docs: /docs)"
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
