#!/usr/bin/env python3
"""RPVS Detective — FastAPI бэк. Отдаёт поиск, детали партнёра и JSON-граф для cytoscape."""
from __future__ import annotations
import os, sqlite3, subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse

ROOT = Path(__file__).parent
DB = ROOT / "rpvs.db"
INDEX = ROOT / "index.html"

app = FastAPI(title="RPVS Detective")


def db() -> sqlite3.Connection:
    if not DB.exists():
        raise HTTPException(503, "rpvs.db ещё не создан — запусти ingest.py")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def index() -> FileResponse:
    return FileResponse(INDEX)


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "db": DB.exists()}


@app.get("/stats")
def stats() -> dict:
    with db() as c:
        return {
            "partners":  c.execute("SELECT COUNT(*) FROM partners").fetchone()[0],
            "persons":   c.execute("SELECT COUNT(*) FROM persons").fetchone()[0],
            "companies": c.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
            "verejni_cinitelia": c.execute(
                "SELECT COUNT(*) FROM persons WHERE je_verejny_cinitel=1"
            ).fetchone()[0],
        }


def _fts_query(q: str) -> str:
    """Превращает 'Janko Hraško' в 'Janko* OR Hraško*' — толерантно к регистру и склонениям."""
    parts = [p.strip() for p in q.replace('"', "").split() if p.strip()]
    return " OR ".join(f"{p}*" for p in parts) or '""'


@app.get("/search")
def search(q: str = Query(..., min_length=2), limit: int = 25) -> dict:
    fts = _fts_query(q)
    with db() as c:
        persons = [dict(r) for r in c.execute(
            "SELECT p.id, p.partner_id, p.role, p.meno, p.priezvisko, "
            "       p.datum_narodenia, p.je_verejny_cinitel "
            "FROM persons_fts f JOIN persons p ON p.id = f.rowid "
            "WHERE persons_fts MATCH ? "
            "ORDER BY p.je_verejny_cinitel DESC, p.priezvisko "
            "LIMIT ?", (fts, limit)
        )]
        companies = [dict(r) for r in c.execute(
            "SELECT c.id, c.partner_id, c.role, c.ico, c.obchodne_meno, c.forma_osoby "
            "FROM companies_fts f JOIN companies c ON c.id = f.rowid "
            "WHERE companies_fts MATCH ? "
            "ORDER BY c.obchodne_meno "
            "LIMIT ?", (fts, limit)
        )]
    return {"q": q, "persons": persons, "companies": companies}


@app.get("/partner/{partner_id}")
def partner(partner_id: int) -> dict:
    with db() as c:
        row = c.execute(
            "SELECT id, cislo_vlozky FROM partners WHERE id=?", (partner_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"partner {partner_id} not found")
        persons = [dict(r) for r in c.execute(
            "SELECT id, role, meno, priezvisko, datum_narodenia, je_verejny_cinitel, "
            "       titul_pred, titul_za, platnost_od, platnost_do "
            "FROM persons WHERE partner_id=? ORDER BY role, priezvisko",
            (partner_id,)
        )]
        companies = [dict(r) for r in c.execute(
            "SELECT id, role, ico, obchodne_meno, forma_osoby, platnost_od, platnost_do "
            "FROM companies WHERE partner_id=? ORDER BY role",
            (partner_id,)
        )]
    return {"partner": dict(row), "persons": persons, "companies": companies}


@app.get("/partner/{partner_id}/graph")
def partner_graph(partner_id: int, depth: int = Query(1, ge=1, le=2)) -> dict:
    """JSON для cytoscape: nodes + edges. depth=1 — одна ячейка, depth=2 — соседи через
    общую персону (та же фамилия/имя/дата рождения) или общий IČO."""
    with db() as c:
        seed = c.execute("SELECT 1 FROM partners WHERE id=?", (partner_id,)).fetchone()
        if not seed:
            raise HTTPException(404)

        partner_ids = {partner_id}
        if depth >= 2:
            for r in c.execute(
                "SELECT DISTINCT p2.partner_id "
                "FROM persons p1 JOIN persons p2 "
                "  ON p1.priezvisko = p2.priezvisko "
                " AND COALESCE(p1.meno,'') = COALESCE(p2.meno,'') "
                " AND COALESCE(p1.datum_narodenia,'') = COALESCE(p2.datum_narodenia,'') "
                "WHERE p1.partner_id = ? AND p2.partner_id != ?",
                (partner_id, partner_id)
            ):
                partner_ids.add(r[0])
            for r in c.execute(
                "SELECT DISTINCT c2.partner_id "
                "FROM companies c1 JOIN companies c2 ON c1.ico = c2.ico AND c1.ico IS NOT NULL "
                "WHERE c1.partner_id = ? AND c2.partner_id != ?",
                (partner_id, partner_id)
            ):
                partner_ids.add(r[0])

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        seen_nodes: set[str] = set()

        def add_node(nid: str, label: str, kind: str, **extra) -> None:
            if nid in seen_nodes:
                return
            seen_nodes.add(nid)
            nodes.append({"data": {"id": nid, "label": label, "kind": kind, **extra}})

        for pid in partner_ids:
            add_node(f"P:{pid}", f"Vložka #{pid}", "partner")

            for r in c.execute(
                "SELECT id, role, meno, priezvisko, datum_narodenia, je_verejny_cinitel "
                "FROM persons WHERE partner_id=?", (pid,)
            ):
                label = " ".join(x for x in [r["meno"], r["priezvisko"]] if x) or f"#{r['id']}"
                nid = f"PE:{r['priezvisko']}|{r['meno']}|{r['datum_narodenia'] or ''}"
                add_node(nid, label, "person",
                         role=r["role"], cinitel=bool(r["je_verejny_cinitel"]))
                edges.append({"data": {
                    "id": f"E:{nid}->P:{pid}:{r['role']}",
                    "source": nid, "target": f"P:{pid}", "role": r["role"],
                }})

            for r in c.execute(
                "SELECT id, role, ico, obchodne_meno, forma_osoby "
                "FROM companies WHERE partner_id=?", (pid,)
            ):
                nid = f"C:{r['ico'] or ('id'+str(r['id']))}"
                add_node(nid, r["obchodne_meno"] or f"IČO {r['ico']}", "company",
                         role=r["role"], ico=r["ico"], forma=r["forma_osoby"])
                edges.append({"data": {
                    "id": f"E:{nid}->P:{pid}:{r['role']}",
                    "source": nid, "target": f"P:{pid}", "role": r["role"],
                }})

    return {"nodes": nodes, "edges": edges, "partners": sorted(partner_ids)}


@app.post("/summary/{partner_id}")
def summary(partner_id: int) -> dict:
    """AI-резюме рисков. Использует claude CLI если доступен, иначе ANTHROPIC_API_KEY через httpx.
    Если ничего нет — возвращает структурированную сводку без LLM."""
    detail = partner(partner_id)
    sketch = _format_for_llm(detail)

    cli_path = _find_claude_cli()
    if cli_path:
        try:
            out = subprocess.run(
                [cli_path, "--print", "--model", "claude-sonnet-4-6", _RISK_PROMPT + "\n\n" + sketch],
                capture_output=True, text=True, timeout=45,
            )
            if out.returncode == 0 and out.stdout.strip():
                return {"source": "claude-cli", "summary": out.stdout.strip(), "context": sketch}
        except Exception as e:
            return {"source": "claude-cli-error", "error": str(e), "context": sketch}

    return {"source": "no-llm", "summary": "(LLM не настроен — возвращён структурный sketch)", "context": sketch}


_RISK_PROMPT = (
    "Ty si analytik anti-korupčného žurnalizmu na Slovensku. "
    "Pozri si nasledujúci výpis z Registra partnerov verejného sektora a napíš 3 odrážky:\n"
    "1) Hlavná štruktúra (kto je partner, kto KÚV, kto sú verejní funkcionári)\n"
    "2) Možné rizikové signály (politicky exponované osoby, krátka platnosť, neúplné údaje)\n"
    "3) Čo by si overil ďalej (jeden konkrétny krok)\n"
    "Odpovedaj po slovensky, vecne, bez špekulácií. Ak údaje chýbajú, povedz to priamo."
)


def _find_claude_cli() -> str | None:
    for p in ("/root/.local/bin/claude", "/usr/local/bin/claude", "/usr/bin/claude"):
        if Path(p).exists():
            return p
    return None


def _format_for_llm(d: dict) -> str:
    p = d["partner"]
    lines = [f"Partner ID={p['id']}, vložka č. {p['cislo_vlozky']}", "", "PVS / OO (subjekty):"]
    for c in d["companies"]:
        lines.append(f"  - [{c['role']}] {c['obchodne_meno']} (IČO={c['ico']}, "
                     f"{c['forma_osoby']}), platnosť {c['platnost_od']} → {c['platnost_do']}")
    lines += ["", "KÚV / VF (osoby):"]
    for pe in d["persons"]:
        flag = " ⚠️verejný činiteľ" if pe["je_verejny_cinitel"] else ""
        lines.append(f"  - [{pe['role']}] {pe['titul_pred'] or ''} {pe['meno'] or ''} "
                     f"{pe['priezvisko'] or ''}{flag}, dátum nar.: {pe['datum_narodenia'] or '?'}")
    return "\n".join(lines)
