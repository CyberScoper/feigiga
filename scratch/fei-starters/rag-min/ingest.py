#!/usr/bin/env python3
# Минимальный ingest: URL -> PDF -> pdftotext -> чанки 800 -> SQLite FTS5
import sys, os, sqlite3, subprocess, tempfile, argparse
import requests

CHUNK = 800
DB = os.environ.get("RAG_DB", "rag.sqlite")

DEFAULT_URLS = [
    # KMAT FEI STU — публично доступные PDF (Matematika 1)
    "https://matika.fei.stuba.sk/KMAT/Matematika1?action=AttachFile&do=get&target=determinanty.pdf",
    "https://matika.fei.stuba.sk/KMAT/Matematika1?action=AttachFile&do=get&target=matice1.pdf",
    "https://matika.fei.stuba.sk/KMAT/Matematika1?action=AttachFile&do=get&target=polynomy.pdf",
]

def init_db(conn):
    conn.executescript("""
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(source, idx, text, tokenize='unicode61');
    """)

def pdf_to_text(pdf_path):
    out = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, check=True)
    return out.stdout.decode("utf-8", errors="replace")

def chunk_text(t, n=CHUNK):
    t = " ".join(t.split())
    for i in range(0, len(t), n):
        yield i // n, t[i:i+n]

def ingest_url(conn, url):
    print(f"[+] {url}", file=sys.stderr)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(r.content); path = f.name
    try:
        text = pdf_to_text(path)
    finally:
        os.unlink(path)
    conn.execute("DELETE FROM chunks WHERE source = ?", (url,))
    rows = list(chunk_text(text))
    conn.executemany("INSERT INTO chunks(source, idx, text) VALUES (?,?,?)",
                     [(url, i, c) for i, c in rows])
    conn.commit()
    print(f"    {len(rows)} чанков", file=sys.stderr)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*", help="URLs PDF; пусто = дефолтный список KMAT")
    args = ap.parse_args()
    urls = args.urls or DEFAULT_URLS
    conn = sqlite3.connect(DB)
    init_db(conn)
    for u in urls:
        try:
            ingest_url(conn, u)
        except Exception as e:
            print(f"    [ошибка] {e}", file=sys.stderr)
    n, = conn.execute("SELECT count(*) FROM chunks").fetchone()
    print(f"всего в БД: {n} чанков → {DB}")

if __name__ == "__main__":
    main()
