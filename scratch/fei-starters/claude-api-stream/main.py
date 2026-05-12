# FastAPI прокси к Claude API со streaming через SSE
import os, json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import httpx

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-6"
ENDPOINT = "https://api.anthropic.com/v1/messages"

app = FastAPI()

@app.get("/")
def root():
    return FileResponse("index.html")

@app.post("/chat")
async def chat(req: Request):
    if not API_KEY:
        raise HTTPException(500, "ANTHROPIC_API_KEY не задан в окружении")
    body = await req.json()
    user_msg = body.get("message", "").strip()
    system = body.get("system", "Ты лаконичный помощник. Используй LaTeX в $...$ для формул.")
    history = body.get("history", [])
    if not user_msg:
        raise HTTPException(400, "пустое message")

    payload = {
        "model": MODEL,
        "max_tokens": 1024,
        "system": system,
        "stream": True,
        "messages": history + [{"role": "user", "content": user_msg}],
    }
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    async def gen():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", ENDPOINT, json=payload, headers=headers) as r:
                if r.status_code != 200:
                    err = await r.aread()
                    yield f"data: {json.dumps({'error': err.decode('utf-8', 'replace')})}\n\n"
                    return
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            evt = json.loads(data)
                        except Exception:
                            continue
                        if evt.get("type") == "content_block_delta":
                            delta = evt.get("delta", {}).get("text", "")
                            if delta:
                                yield f"data: {json.dumps({'delta': delta})}\n\n"
                        elif evt.get("type") == "message_stop":
                            yield "data: [DONE]\n\n"
                            return

    return StreamingResponse(gen(), media_type="text/event-stream")
