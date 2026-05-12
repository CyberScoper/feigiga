#!/usr/bin/env python3
# BM25 top-5 → Claude. Используется тот же rag.sqlite, что создал ingest.py
import os, sys, sqlite3, json, argparse
import httpx

DB = os.environ.get("RAG_DB", "rag.sqlite")
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-6"

def search(conn, q, k=5):
    # FTS5 тяжело относится к спецсимволам — экранируем фразой
    safe = q.replace('"', '""')
    rows = conn.execute(
        "SELECT source, idx, text, bm25(chunks) AS s FROM chunks WHERE chunks MATCH ? ORDER BY s LIMIT ?",
        (f'"{safe}"', k)
    ).fetchall()
    if not rows:
        # fallback: разбиваем запрос на токены через OR
        toks = [t for t in q.split() if len(t) > 2]
        if not toks:
            return []
        expr = " OR ".join(f'"{t}"' for t in toks)
        rows = conn.execute(
            "SELECT source, idx, text, bm25(chunks) AS s FROM chunks WHERE chunks MATCH ? ORDER BY s LIMIT ?",
            (expr, k)
        ).fetchall()
    return rows

def ask_claude(question, ctx_blocks):
    if not API_KEY:
        print("ANTHROPIC_API_KEY не задан — печатаю только контекст", file=sys.stderr)
        for i, b in enumerate(ctx_blocks, 1):
            print(f"\n--- [{i}] {b['source']} #{b['idx']} ---\n{b['text']}")
        return
    ctx = "\n\n".join(f"[{i+1}] {b['text']}" for i, b in enumerate(ctx_blocks))
    sys_prompt = ("Odpovedaj stručne na základe poskytnutého kontextu. "
                  "Cituj zdroje ako [1], [2]. Ak v kontexte odpoveď nie je, povedz to.")
    payload = {
        "model": MODEL, "max_tokens": 800,
        "system": sys_prompt,
        "messages": [{"role": "user",
                      "content": f"KONTEXT:\n{ctx}\n\nOTÁZKA: {question}"}],
    }
    r = httpx.post("https://api.anthropic.com/v1/messages", json=payload, timeout=120,
                   headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01"})
    r.raise_for_status()
    data = r.json()
    print(data["content"][0]["text"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="+")
    ap.add_argument("-k", type=int, default=5)
    args = ap.parse_args()
    q = " ".join(args.question)
    conn = sqlite3.connect(DB)
    rows = search(conn, q, args.k)
    if not rows:
        print("ничего не нашёл в базе", file=sys.stderr); sys.exit(1)
    blocks = [{"source": s, "idx": i, "text": t} for s, i, t, _ in rows]
    print(f"# top-{len(blocks)} чанков:", file=sys.stderr)
    for i, b in enumerate(blocks, 1):
        print(f"  [{i}] {b['source'].split('target=')[-1]} #{b['idx']}", file=sys.stderr)
    ask_claude(q, blocks)

if __name__ == "__main__":
    main()
