#!/usr/bin/env python3
"""Тащит данные из rpvs.gov.sk OData → SQLite. Пагинация по @odata.nextLink."""
from __future__ import annotations
import argparse, asyncio, sqlite3, sys, time
from pathlib import Path
import httpx

ROOT = Path(__file__).parent
DB = ROOT / "rpvs.db"
SCHEMA = ROOT / "schema.sql"

START = (
    "https://rpvs.gov.sk/OpenData/Partneri"
    "?$format=json"
    "&$expand=PartneriVerejnehoSektora,KonecniUzivateliaVyhod,VerejniFunkcionari,OpravneneOsoby"
)


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA.read_text())
    return conn


def upsert_partner(conn: sqlite3.Connection, p: dict) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO partners (id, cislo_vlozky) VALUES (?, ?)",
        (p["Id"], p["CisloVlozky"]),
    )
    pid = p["Id"]

    # Чистим старые связи перед перезаписью (на случай повторного ingest)
    conn.execute("DELETE FROM companies WHERE partner_id = ?", (pid,))
    conn.execute("DELETE FROM persons   WHERE partner_id = ?", (pid,))

    for pvs in p.get("PartneriVerejnehoSektora") or []:
        conn.execute(
            "INSERT OR REPLACE INTO companies "
            "(id, partner_id, role, ico, obchodne_meno, forma_osoby, platnost_od, platnost_do) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                pvs["Id"], pid, "pvs",
                pvs.get("Ico"),
                pvs.get("ObchodneMeno") or _person_label(pvs),
                pvs.get("FormaOsoby"),
                pvs.get("PlatnostOd"), pvs.get("PlatnostDo"),
            ),
        )

    for oo in p.get("OpravneneOsoby") or []:
        conn.execute(
            "INSERT OR REPLACE INTO companies "
            "(id, partner_id, role, ico, obchodne_meno, forma_osoby, platnost_od, platnost_do) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                oo["Id"], pid, "oo",
                oo.get("Ico"),
                oo.get("ObchodneMeno") or _person_label(oo),
                oo.get("FormaOsoby"),
                oo.get("PlatnostOd"), oo.get("PlatnostDo"),
            ),
        )

    for kuv in p.get("KonecniUzivateliaVyhod") or []:
        conn.execute(
            "INSERT OR REPLACE INTO persons "
            "(id, partner_id, role, meno, priezvisko, datum_narodenia, je_verejny_cinitel, "
            " titul_pred, titul_za, platnost_od, platnost_do) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                kuv["Id"], pid, "kuv",
                kuv.get("Meno"), kuv.get("Priezvisko"),
                kuv.get("DatumNarodenia"),
                1 if kuv.get("JeVerejnyCinitel") else 0,
                kuv.get("TitulPred"), kuv.get("TitulZa"),
                kuv.get("PlatnostOd"), kuv.get("PlatnostDo"),
            ),
        )

    for vf in p.get("VerejniFunkcionari") or []:
        conn.execute(
            "INSERT OR REPLACE INTO persons "
            "(id, partner_id, role, meno, priezvisko, datum_narodenia, je_verejny_cinitel, "
            " titul_pred, titul_za, platnost_od, platnost_do) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                vf["Id"], pid, "vf",
                vf.get("Meno"), vf.get("Priezvisko"),
                vf.get("DatumNarodenia"),
                1,  # сам по себе verejny funkcionar
                vf.get("TitulPred"), vf.get("TitulZa"),
                vf.get("PlatnostOd"), vf.get("PlatnostDo"),
            ),
        )


def _person_label(rec: dict) -> str | None:
    parts = [rec.get("TitulPred"), rec.get("Meno"), rec.get("Priezvisko"), rec.get("TitulZa")]
    s = " ".join(p for p in parts if p)
    return s or None


async def run(limit: int | None, resume: bool) -> None:
    conn = init_db()

    url = START
    if resume:
        row = conn.execute(
            "SELECT value FROM ingest_meta WHERE key='next_url'"
        ).fetchone()
        if row and row[0]:
            url = row[0]
            print(f"resume from {url[:90]}…", file=sys.stderr)

    pulled = 0
    t0 = time.time()
    async with httpx.AsyncClient(timeout=30.0, headers={"Accept": "application/json"}) as cli:
        while url:
            r = await cli.get(url)
            r.raise_for_status()
            data = r.json()
            batch = data.get("value", [])

            with conn:  # транзакция на батч
                for p in batch:
                    upsert_partner(conn, p)

            pulled += len(batch)
            url = data.get("@odata.nextLink")
            conn.execute(
                "INSERT OR REPLACE INTO ingest_meta(key,value) VALUES('next_url',?)",
                (url or "",),
            )
            conn.commit()

            print(
                f"  + {len(batch):3d}  total={pulled:6d}  rate={pulled/max(time.time()-t0,1):.0f}/s",
                file=sys.stderr,
            )

            if limit and pulled >= limit:
                print(f"reached --limit {limit}, stop", file=sys.stderr)
                break

    print(f"done. partners={pulled}, db={DB}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="Остановиться после N партнёров (для дев-режима)")
    ap.add_argument("--resume", action="store_true",
                    help="Продолжить с сохранённого @odata.nextLink")
    args = ap.parse_args()
    asyncio.run(run(args.limit, args.resume))


if __name__ == "__main__":
    main()
