#!/usr/bin/env python3
# Парсер расписаний aladin.fei.stuba.sk → JSON / .ics
# Aladin верстает таблицу: tr с днями, td с предметами; формат hh:mm-hh:mm.
# Если URL отдает HTML с table.rozvrh — парсим, иначе пытаемся универсальный fallback.

import sys, re, json, argparse
from datetime import datetime, timedelta, time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

DAYS_SK = {
    "pondelok": 0, "po": 0,
    "utorok": 1, "ut": 1,
    "streda": 2, "st": 2,
    "stvrtok": 3, "štvrtok": 3, "št": 3, "stv": 3,
    "piatok": 4, "pi": 4,
    "sobota": 5, "so": 5,
    "nedela": 6, "nedeľa": 6, "ne": 6,
}

TYPES_SK = {"P": "prednáška", "C": "cvičenie", "L": "laboratórium", "S": "seminár"}

TIME_RE = re.compile(r"(\d{1,2})[:.](\d{2})\s*[-–]\s*(\d{1,2})[:.](\d{2})")

def fetch(target):
    if target.startswith("http://") or target.startswith("https://"):
        r = requests.get(target, timeout=20, headers={"User-Agent": "fei-starter/1.0"})
        r.raise_for_status()
        return r.text
    # локальный файл / относительный путь типа 2bc_API_4 → пробуем aladin
    if not target.endswith(".html") and "/" not in target:
        url = f"https://aladin.fei.stuba.sk/rozvrh/{target}.html"
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and "<table" in r.text.lower():
            return r.text
    with open(target, encoding="utf-8") as f:
        return f.read()

def detect_day(text):
    t = text.strip().lower()
    for k, v in DAYS_SK.items():
        if t.startswith(k):
            return v
    return None

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    events = []
    current_day = None

    # Ищем таблицу rozvrh либо просто все ячейки в порядке
    for tr in soup.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        # Первая ячейка часто содержит день недели
        first = cells[0].get_text(" ", strip=True)
        d = detect_day(first)
        if d is not None:
            current_day = d
            cells_for_data = cells[1:]
        else:
            cells_for_data = cells

        for cell in cells_for_data:
            txt = cell.get_text(" ", strip=True)
            if not txt:
                continue
            m = TIME_RE.search(txt)
            if not m:
                continue
            sh, sm, eh, em = map(int, m.groups())
            rest = (txt[:m.start()] + " " + txt[m.end():]).strip()
            # Эвристика: «PREDMET (typ) miestnost - prednasajuci»
            parts = re.split(r"\s+", rest)
            subject = parts[0] if parts else ""
            typ = ""
            room = ""
            teacher = ""
            mt = re.search(r"\((P|C|L|S)\)", rest)
            if mt:
                typ = TYPES_SK.get(mt.group(1), mt.group(1))
            mr = re.search(r"\b([A-Z]{1,3}-?\d{2,4}[a-zA-Z]?)\b", rest)
            if mr:
                room = mr.group(1)
            mtch = re.search(r"(doc|prof|Mgr|Ing|RNDr|PhD|Dr)\.[^,;]*", rest)
            if mtch:
                teacher = mtch.group(0).strip()

            events.append({
                "day": current_day if current_day is not None else 0,
                "start": f"{sh:02d}:{sm:02d}",
                "end": f"{eh:02d}:{em:02d}",
                "subject": subject,
                "room": room,
                "type": typ,
                "teacher": teacher,
                "raw": txt,
            })
    return events

def to_ics(events, semester_start, weeks, out_path):
    from ics import Calendar, Event
    cal = Calendar()
    base = datetime.fromisoformat(semester_start)
    for w in range(weeks):
        for e in events:
            sh, sm = map(int, e["start"].split(":"))
            eh, em = map(int, e["end"].split(":"))
            d = base + timedelta(days=e["day"] + w * 7)
            ev = Event()
            ev.name = f"{e['subject']} ({e['type']})" if e["type"] else e["subject"]
            ev.begin = datetime.combine(d.date(), time(sh, sm))
            ev.end = datetime.combine(d.date(), time(eh, em))
            ev.location = e["room"]
            ev.description = e.get("raw", "")
            cal.events.add(ev)
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="код расписания (2bc_API_4), URL или путь к локальному HTML")
    ap.add_argument("--ics", help="путь для .ics; если задан — сгенерировать календарь")
    ap.add_argument("--start", default="2025-09-22", help="понедельник 1-й недели семестра, ISO date")
    ap.add_argument("--weeks", type=int, default=13, help="кол-во недель")
    args = ap.parse_args()

    html = fetch(args.target)
    events = parse(html)
    print(json.dumps(events, ensure_ascii=False, indent=2))
    print(f"\n# событий: {len(events)}", file=sys.stderr)
    if args.ics:
        to_ics(events, args.start, args.weeks, args.ics)
        print(f"# .ics записан в {args.ics}", file=sys.stderr)

if __name__ == "__main__":
    main()
