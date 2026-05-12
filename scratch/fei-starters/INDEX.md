# fei-starters — заготовки под финал Master of VibeCoding

Цель: за 75 минут не писать boilerplate. В день X — `cp -r <starter>/ ~/work/` и пилить домен.

## 1. `claude-api-stream/` — FastAPI + SSE-стриминг к Claude
- `main.py` — POST `/chat` проксирует в Claude (модель `claude-sonnet-4-6`), SSE
- `index.html` — vanilla JS UI с KaTeX для формул
- Запуск: `cd claude-api-stream && ANTHROPIC_API_KEY=sk-... uvicorn main:app --reload`
- Открыть: http://127.0.0.1:8000/

## 2. `aladin-scraper/` — расписание FEI → JSON / .ics
- `parse.py` — парсер таблиц aladin (BeautifulSoup), знает словацкие дни недели
- `sample.html` — фикстура для офлайн-теста
- Запуск (офлайн): `cd aladin-scraper && python3 parse.py sample.html --ics out.ics`
- Запуск (live): `python3 parse.py 2bc_API_4` (если URL вернётся)

## 3. `rag-min/` — мини-RAG на SQLite FTS5 (без векторных БД)
- `ingest.py` — URL PDF → pdftotext → чанки 800 символов → FTS5
- `query.py` — BM25 top-5 → Claude с цитатами `[1] [2]`
- Запуск: `cd rag-min && python3 ingest.py` (дефолтные KMAT-PDF), потом `python3 query.py "co je determinant matice"`
- Без `ANTHROPIC_API_KEY` — печатает только найденные чанки

## 4. `onboarding-quest/` — Bun + Hono сервер для первокурсников FEI
- `server.ts` — POST `/plan`, GET `/calendar.ics`, харкод цен (ISIC 24€, TransCard 3.08€, IDS BK 29.10€)
- `index.html` — форма + рендер timeline
- Запуск: `cd onboarding-quest && bun install && bun run dev`
- Открыть: http://127.0.0.1:3000/

## 5. `pitch-template.md` — каркас 60-секундного питча
HOOK 15s → DEMO 30s → TECH 10s → ASK 5s. Чеклист и anti-patterns.

## Перед стартом — что проверить за 30 секунд
```
echo $ANTHROPIC_API_KEY | head -c 12       # ключ есть
which bun python3 uvicorn pdftotext        # все тулзы
ls /mnt/extra/vibe/scratch/fei-starters/   # стартеры на месте
```
