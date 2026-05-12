#!/usr/bin/env python3
"""Декодер морзянки через envelope detection."""
import numpy as np
from scipy.io import wavfile
from collections import Counter

WAV = "/mnt/extra/vibe/scratch/morse/morsei.wav"

MORSE = {
    ".-":"A","-...":"B","-.-.":"C","-..":"D",".":"E","..-.":"F",
    "--.":"G","....":"H","..":"I",".---":"J","-.-":"K",".-..":"L",
    "--":"M","-.":"N","---":"O",".--.":"P","--.-":"Q",".-.":"R",
    "...":"S","-":"T","..-":"U","...-":"V",".--":"W","-..-":"X",
    "-.--":"Y","--..":"Z",
    "-----":"0",".----":"1","..---":"2","...--":"3","....-":"4",
    ".....":"5","-....":"6","--...":"7","---..":"8","----.":"9",
}

def main():
    sr, data = wavfile.read(WAV)
    print(f"sr={sr}, dtype={data.dtype}, samples={len(data)}, sec={len(data)/sr:.2f}")
    if data.dtype == np.uint8:
        sig = data.astype(np.float32) - 128.0
    else:
        sig = data.astype(np.float32)
    if sig.ndim > 1:
        sig = sig.mean(axis=1)

    # Envelope: abs + moving average ~20ms
    env = np.abs(sig)
    win = int(0.02 * sr)  # 20ms
    kernel = np.ones(win) / win
    smooth = np.convolve(env, kernel, mode="same")

    # Порог = max/3
    thr = smooth.max() / 3.0
    print(f"smooth max={smooth.max():.1f}, thr={thr:.1f}")

    on = smooth > thr

    # Извлечь runs (длительности on/off в samples)
    runs = []  # (state, length)
    cur = on[0]
    cnt = 0
    for v in on:
        if v == cur:
            cnt += 1
        else:
            runs.append((bool(cur), cnt))
            cur = v
            cnt = 1
    runs.append((bool(cur), cnt))

    # Отрезать ведущую/хвостовую тишину
    while runs and not runs[0][0]:
        runs.pop(0)
    while runs and not runs[-1][0]:
        runs.pop()

    ons = [l for s, l in runs if s]
    offs = [l for s, l in runs if not s]
    ms = lambda x: 1000.0 * x / sr

    print(f"ons count={len(ons)}, offs={len(offs)}")
    print(f"ons (ms) sample: {sorted(set(round(ms(o),1) for o in ons))[:20]}")
    print(f"offs(ms) sample: {sorted(set(round(ms(o),1) for o in offs))[:20]}")

    # Кластеризация on: dot/dash. Порог между min и max.
    on_med = np.median(ons)
    dot_med = np.median([o for o in ons if o < on_med * 1.2])
    dash_med = np.median([o for o in ons if o > on_med * 0.9])
    # Если медианы близки — все одного типа, попробуем mid
    on_thr = (min(ons) + max(ons)) / 2.0
    dots = [o for o in ons if o < on_thr]
    dashes = [o for o in ons if o >= on_thr]
    dot_med = np.median(dots) if dots else 0
    dash_med = np.median(dashes) if dashes else 0
    print(f"dot median = {ms(dot_med):.1f} ms ({dot_med} samp)")
    print(f"dash median = {ms(dash_med):.1f} ms ({dash_med} samp)")

    # Off: 3 кластера 1:3:7
    # Простейше: пороги по дотовой единице
    unit = dot_med
    intra_thr = unit * 2     # < 2u -> intra-letter
    word_thr = unit * 5      # > 5u -> inter-word
    print(f"unit={ms(unit):.1f}ms, intra<{ms(intra_thr):.1f}, word>{ms(word_thr):.1f}")

    # Сборка кода
    code_chars = []
    # Идём по runs в порядке
    for s, l in runs:
        if s:
            code_chars.append("." if l < on_thr else "-")
        else:
            if l < intra_thr:
                pass  # intra-letter, ничего
            elif l < word_thr:
                code_chars.append(" ")
            else:
                code_chars.append(" / ")
    raw = "".join(code_chars)
    print(f"RAW: {raw}")

    # Декод
    words = raw.split(" / ")
    out = []
    for w in words:
        letters = w.split(" ")
        decoded = "".join(MORSE.get(l, f"?{l}?") for l in letters if l)
        out.append(decoded)
    text = " ".join(out).lower()
    print(f"DECODED: {text}")

if __name__ == "__main__":
    main()
