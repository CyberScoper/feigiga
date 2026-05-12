# RPVS-Detective — план

## Что это
Веб-приложение, которое индексирует словацкий **Register partnerov verejného sektora**
(`rpvs.gov.sk`) и даёт «расследовательский» интерфейс: поиск персоны/компании →
граф связей (партнёр ↔ конечный бенефициар ↔ публичный деятель ↔ оправнённая особа).

## Источник данных
OData v4, без авторизации:
```
https://rpvs.gov.sk/OpenData/$metadata
https://rpvs.gov.sk/OpenData/Partneri?$expand=PartneriVerejnehoSektora,KonecniUzivateliaVyhod,VerejniFunkcionari,OpravneneOsoby
```
- Страница = 20 записей, пагинация через `@odata.nextLink` (`$skip=20`).
- `$top` запрещён (limit 0).
- `$expand` РАБОТАЕТ — даёт партнёра + всех связанных в одной выдаче.

## Доменная модель (упрощённо)
| Сущность | Что | Ключевые поля |
|---|---|---|
| **Partner** | «вкладка» реестра | Id, CisloVlozky |
| **PartnerVerejnehoSektora (PVS)** | компания/физлицо, получатель денег от государства | Meno/Priezvisko или ObchodneMeno+Ico, FormaOsoby |
| **KonecnyUzivatelVyhod (KÚV)** | конечный бенефициар (всегда физлицо) | Meno+Priezvisko+DatumNarodenia, JeVerejnyCinitel |
| **VerejnyFunkcionar (VF)** | публичный деятель, связанный с партнёром | Meno+Priezvisko |
| **OpravnenaOsoba (OO)** | юрист-верификатор | ObchodneMeno+Ico |

Все эти сущности привязаны к **Partner.Id** через NavigationProperty.

## Критичные user stories
1. **«Я ввёл фамилию политика → покажи все компании»** — поиск по KÚV/VF имени → партнёры → PVS-компании.
2. **«Я ввёл IČO → покажи бенефициаров»** — обратное направление.
3. **«Покажи граф этой ячейки реестра»** — узлы и рёбра вокруг Partner Id для визуализации.
4. (опционально) **«AI-резюме рисков»** — Claude получает структурированную сводку и пишет 3 буллета.

## Архитектура

```
┌──────────────┐   $expand    ┌──────────────┐
│ rpvs.gov.sk  │─────────────►│  ingest.py   │──► SQLite (rpvs.db)
└──────────────┘   pagination └──────────────┘
                                                │
                              ┌─────────────────▼──────────────────┐
                              │  FastAPI (server.py)               │
                              │   GET /search?q=...                │
                              │   GET /partner/{id}                │
                              │   GET /partner/{id}/graph (JSON)   │
                              │   POST /summary/{id}  (Claude opt) │
                              └─────────────────┬──────────────────┘
                                                │
                                          ┌─────▼─────┐
                                          │ index.html│  cytoscape.js
                                          └───────────┘
```

## SQLite-схема
- `partners(id PK, cislo_vlozky)`
- `companies(id PK, partner_id FK, role TEXT[pvs/oo], ico, obchodne_meno, forma_osoby, platnost_od, platnost_do)`
- `persons(id PK, partner_id FK, role TEXT[kuv/vf], meno, priezvisko, datum_narodenia, je_verejny_cinitel, platnost_od, platnost_do)`
- FTS5 виртуальные таблицы `persons_fts`, `companies_fts` для поиска.
- Индексы: `partner_id`, `ico`, `priezvisko`.

## Этапы (под 75-минутный финал)

| # | Задача | Время | Артефакт |
|---|---|---|---|
| 0 | Скелет: `schema.sql`, `requirements.txt` | 5 | ✅ |
| 1 | `ingest.py` с пагинацией + батч-инсертом | 15 | `rpvs.db` |
| 2 | `server.py` — `/search`, `/partner/{id}`, `/graph`, `/healthz`, `/stats` | 20 | API ready |
| 3 | `index.html` — поиск + cytoscape граф + детали | 20 | UI ready |
| 4 | AI-резюме `/summary/{id}` через `claude` CLI / Anthropic API | 10 | wow-фича |
| 5 | Полировка, питч | 5 | demo-ready |

## Риски
- Ingest всех ~50K партнёров за раз = десятки тысяч HTTP-вызовов → долго. **Митигация**: `--limit` для демо (1000-5000 записей хватит для wow), индекс готовится оффлайн заранее.
- Rate-limit на портале — пока не наблюдается, но будем держать `httpx.AsyncClient` с `Semaphore(8)`.
- Без `ANTHROPIC_API_KEY` AI-фича выключается, но граф+поиск работают.
