#!/usr/bin/env python3
"""Собираем 2 QR-кода v2 (25x25) из 8 фрагментов-квадрантов 13x13.

Каждый фрагмент 500x500 содержит 13x13 модулей (модуль ≈ 38.46 px).
Полный QR = 25x25, фрагменты перекрываются на 1 модуль (12+12+1=25).

Квадранты:
    QR01, QR02 -> TL (0,0)-(12,12)   (finder top-left @ (0,0))
    QR04, QR08 -> BL (12,0)-(24,12)  (finder bottom-left @ (18,0))
    QR12, QR36 -> TR (0,12)-(12,24)  (finder top-right @ (0,18))
    QR11, QR43 -> BR (12,12)-(24,24) (alignment pattern @ (16,16))

2 QR = по одному файлу из каждой пары. 2^4=16 комбинаций, ищем непересекающиеся.
"""
import itertools
import os
import re
import subprocess

import numpy as np
from PIL import Image

QR_DIR = "/mnt/extra/vibe/scratch/qr"

QUAD_OFFSETS = {
    "tl": (0, 0),
    "bl": (12, 0),
    "tr": (0, 12),
    "br": (12, 12),
}
GROUPS = {
    "tl": ["QR01.png", "QR02.png"],
    "bl": ["QR04.png", "QR08.png"],
    "tr": ["QR12.png", "QR36.png"],
    "br": ["QR11.png", "QR43.png"],
}


def load_binary(path):
    img = Image.open(path).convert("L")
    return (np.array(img) < 128).astype(np.uint8)


def to_grid13(a):
    """500x500 -> 13x13 с шагом 500/13."""
    g = np.zeros((13, 13), dtype=np.uint8)
    for i in range(13):
        for j in range(13):
            y = int(i * 500 / 13 + 500 / 26)
            x = int(j * 500 / 13 + 500 / 26)
            g[i, j] = a[y, x]
    return g


def assemble(quad_files):
    full = np.zeros((25, 25), dtype=np.uint8)
    for q, fname in quad_files.items():
        a = load_binary(os.path.join(QR_DIR, fname))
        g = to_grid13(a)
        oy, ox = QUAD_OFFSETS[q]
        full[oy:oy + 13, ox:ox + 13] = g
    return full


def render_qr(grid, path, scale=20, border=4):
    size = grid.shape[0]
    full = np.ones((size + 2 * border, size + 2 * border), dtype=np.uint8)
    full[border:border + size, border:border + size] = 1 - grid
    img = full.repeat(scale, 0).repeat(scale, 1) * 255
    Image.fromarray(img.astype(np.uint8), "L").save(path)


def decode(path):
    try:
        r = subprocess.run(
            ["zbarimg", "--quiet", "--raw", path],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def main():
    results = []
    for tl, bl, tr, br in itertools.product(GROUPS["tl"], GROUPS["bl"],
                                            GROUPS["tr"], GROUPS["br"]):
        quad_files = {"tl": tl, "bl": bl, "tr": tr, "br": br}
        full = assemble(quad_files)
        path = "/tmp/asm.png"
        render_qr(full, path)
        txt = decode(path)
        print(f"({tl},{bl},{tr},{br}) -> {txt!r}")
        if txt:
            results.append(((tl, bl, tr, br), txt, full.copy()))

    print(f"\nДекодировано: {len(results)} вариантов")

    # Ищем 2 непересекающихся
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            s1 = set(results[i][0])
            s2 = set(results[j][0])
            if s1.isdisjoint(s2):
                print(f"\n>>> РЕШЕНИЕ <<<")
                print(f"QR #1 = {results[i][0]} -> {results[i][1]!r}")
                print(f"QR #2 = {results[j][0]} -> {results[j][1]!r}")
                # Сохраним
                render_qr(results[i][2], os.path.join(QR_DIR, "solved_qr1.png"))
                render_qr(results[j][2], os.path.join(QR_DIR, "solved_qr2.png"))
                nums1 = [int(x) for x in re.findall(r"\d+", results[i][1])]
                nums2 = [int(x) for x in re.findall(r"\d+", results[j][1])]
                print(f"Числа QR#1: {nums1}, сумма={sum(nums1)}")
                print(f"Числа QR#2: {nums2}, сумма={sum(nums2)}")
                total = sum(nums1) + sum(nums2)
                print(f"\nИТОГО: {total}")
                return

    if not results:
        print("Ничего не декодировалось. Сохраняем debug.")
        quad_files = {"tl": "QR01.png", "bl": "QR04.png",
                      "tr": "QR12.png", "br": "QR11.png"}
        full = assemble(quad_files)
        render_qr(full, os.path.join(QR_DIR, "debug.png"))
        for r in full:
            print("".join("#" if v else "." for v in r))


if __name__ == "__main__":
    main()
