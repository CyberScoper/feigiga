#!/usr/bin/env python3
"""Заготовка для парсинга данных. Копируй нужный кусок, не запускай целиком."""

import sys, json, csv, re
from pathlib import Path

# === JSON ===
# data = json.load(open("file.json"))
# data = json.loads(open("file.json","rb").read().decode("utf-8-sig"))  # с BOM
# for item in data["items"]:
#     ...

# === JSONL ===
# for line in open("file.jsonl"):
#     row = json.loads(line)
#     ...

# === CSV ===
# with open("file.csv", newline="", encoding="utf-8") as f:
#     reader = csv.DictReader(f)        # если есть header
#     # reader = csv.reader(f)          # если нет
#     for row in reader:
#         ...

# === CSV с нестандартным разделителем ===
# reader = csv.DictReader(f, delimiter=";", quotechar='"')

# === HTTP + JSON ===
# import httpx
# r = httpx.get("https://api.example.com/v1/items", headers={"Authorization":"Bearer X"})
# r.raise_for_status()
# data = r.json()

# === HTTP с пагинацией ===
# import httpx
# items, url = [], "https://api.example.com/v1/items?page=1"
# while url:
#     r = httpx.get(url); r.raise_for_status()
#     j = r.json()
#     items += j["items"]
#     url = j.get("next")

# === HTML scraping (без bs4 на быстром старте) ===
# import re, httpx
# html = httpx.get(url).text
# titles = re.findall(r'<h2[^>]*>(.+?)</h2>', html, re.S)

# === bs4 если нужно (pip install beautifulsoup4) ===
# from bs4 import BeautifulSoup
# soup = BeautifulSoup(html, "html.parser")
# for a in soup.select("a.product"):
#     print(a.get_text(strip=True), a["href"])

# === XML ===
# import xml.etree.ElementTree as ET
# root = ET.parse("file.xml").getroot()
# for it in root.iter("item"):
#     print(it.findtext("name"), it.get("id"))

# === декодеры на скорую руку ===
# import base64
# base64.b64decode(s + "=" * (-len(s) % 4))
# bytes.fromhex(s)
# s.encode("rot13")            # py3: codecs.decode(s, "rot_13")
# import codecs; codecs.decode(s, "rot_13")

# === поиск email/url/numbers в тексте ===
# re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
# re.findall(r'https?://[^\s"<>]+', text)
# re.findall(r'-?\d+(?:\.\d+)?', text)

# === sqlite (часто быстрее, чем парсить руками огромный CSV) ===
# import sqlite3
# con = sqlite3.connect(":memory:")
# con.executescript("CREATE TABLE t (a, b, c);")
# rows = [(1,2,3), (4,5,6)]
# con.executemany("INSERT INTO t VALUES (?,?,?)", rows)
# for r in con.execute("SELECT a, sum(b) FROM t GROUP BY a"): print(r)

if __name__ == "__main__":
    print(__doc__)
    print("Стартовая шпаргалка. Открой файл и скопируй нужный блок.")
