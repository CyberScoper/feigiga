#!/usr/bin/env python3
"""Собрать 2 QR из 8 фрагментов: побитовый OR в группах по 4."""
import itertools
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

QR_DIR = Path("/mnt/extra/vibe/scratch/qr")
TMP = Path("/tmp")
FILES = ["QR01.png", "QR02.png", "QR04.png", "QR08.png",
         "QR11.png", "QR12.png", "QR36.png", "QR43.png"]


def load_bin(name):
    """Загрузить как grayscale, бинаризовать (порог 128). True = чёрный модуль."""
    img = Image.open(QR_DIR / name).convert("L")
    arr = np.array(img)
    return arr < 128  # чёрные пиксели True


def to_png(mask, path):
    """mask: True=чёрный. Сохранить PNG."""
    out = np.where(mask, 0, 255).astype(np.uint8)
    Image.fromarray(out, mode="L").save(path)


def decode(path):
    """zbarimg → строка содержимого или None."""
    res = subprocess.run(
        ["zbarimg", "--quiet", "--raw", str(path)],
        capture_output=True, text=True
    )
    if res.returncode == 0:
        return res.stdout.strip()
    return None


def main():
    frags = {f: load_bin(f) for f in FILES}
    for f, m in frags.items():
        print(f"{f}: чёрных пикселей = {m.sum()}")

    # Перебор разбиений на 4+4 (35 уникальных)
    indices = list(range(8))
    seen = set()
    tries = 0
    for combo in itertools.combinations(indices, 4):
        other = tuple(i for i in indices if i not in combo)
        key = frozenset([combo, other])
        if key in seen:
            continue
        seen.add(key)
        tries += 1

        g1 = [FILES[i] for i in combo]
        g2 = [FILES[i] for i in other]

        or1 = np.zeros_like(frags[FILES[0]])
        for f in g1:
            or1 |= frags[f]
        or2 = np.zeros_like(frags[FILES[0]])
        for f in g2:
            or2 |= frags[f]

        p1 = TMP / "qr_g1.png"
        p2 = TMP / "qr_g2.png"
        to_png(or1, p1)
        to_png(or2, p2)

        d1 = decode(p1)
        d2 = decode(p2)

        if d1 and d2:
            print(f"\n=== УСПЕХ на попытке {tries} ===")
            print(f"Группа 1: {g1}")
            print(f"  декодировано: {d1!r}")
            print(f"Группа 2: {g2}")
            print(f"  декодировано: {d2!r}")
            try:
                n1 = int(d1.strip())
                n2 = int(d2.strip())
                print(f"\nСумма: {n1} + {n2} = {n1 + n2}")
            except ValueError:
                # Может быть число внутри строки
                import re
                m1 = re.findall(r"-?\d+", d1)
                m2 = re.findall(r"-?\d+", d2)
                print(f"числа в строках: {m1} / {m2}")
                if m1 and m2:
                    n1 = int(m1[0]); n2 = int(m2[0])
                    print(f"Сумма: {n1} + {n2} = {n1 + n2}")
            # Сохранить финальные картинки рядом с фрагментами
            to_png(or1, QR_DIR / "FINAL_QR_A.png")
            to_png(or2, QR_DIR / "FINAL_QR_B.png")
            return 0

    print(f"\nПеребрано {tries} разбиений — ни одно не декодировалось обоими zbarimg.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
