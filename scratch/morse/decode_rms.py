#!/usr/bin/env python3
"""Декод морзянки из WAV через скользящее RMS."""
import numpy as np
from scipy.io import wavfile

PATH = "/mnt/extra/vibe/scratch/morse/morsei.wav"

MORSE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z",
    "-----": "0", ".----": "1", "..---": "2", "...--": "3", "....-": "4",
    ".....": "5", "-....": "6", "--...": "7", "---..": "8", "----.": "9",
}


def main():
    sr, data = wavfile.read(PATH)
    print(f"sr={sr}, len={len(data)}, dtype={data.dtype}")
    if data.dtype == np.uint8:
        data = data.astype(np.int32) - 128
    else:
        data = data.astype(np.int32)
    if data.ndim > 1:
        data = data[:, 0]

    # Скользящее RMS окном ~50 ms
    win = int(0.05 * sr)  # ~552
    x2 = data.astype(np.float64) ** 2
    # быстрое скользящее среднее через cumsum
    csum = np.cumsum(np.insert(x2, 0, 0.0))
    env = np.sqrt((csum[win:] - csum[:-win]) / win)

    print(f"env stats: min={env.min():.2f} max={env.max():.2f} mean={env.mean():.2f} median={np.median(env):.2f}")

    thr = (env.max() + env.min()) / 2 * 0.5  # половина от середины
    # Лучше: порог = 0.3 * max
    thr = 0.3 * env.max()
    print(f"threshold={thr:.2f}")

    on = env > thr
    # длительности run-length
    diff = np.diff(on.astype(np.int8))
    edges_up = np.where(diff == 1)[0] + 1
    edges_dn = np.where(diff == -1)[0] + 1
    # склеим в последовательность сегментов
    segs = []  # (state, start, end)
    pos = 0
    state = on[0]
    for i in range(1, len(on)):
        if on[i] != state:
            segs.append((state, pos, i))
            pos = i
            state = on[i]
    segs.append((state, pos, len(on)))

    # длительности в мс
    durs_on = []
    durs_off = []
    seg_ms = []
    for s, a, b in segs:
        ms = (b - a) * 1000.0 / sr
        seg_ms.append((bool(s), ms))
        if s:
            durs_on.append(ms)
        else:
            durs_off.append(ms)

    print("\n--- on durations (ms) ---")
    print([round(x, 1) for x in durs_on])
    print("\n--- off durations (ms) ---")
    print([round(x, 1) for x in durs_off])

    # отбросим короткие шумовые on
    on_clean = [d for d in durs_on if d > 20]
    dot = np.percentile(on_clean, 25)  # 1-й квартиль
    print(f"\nestimated dot duration: {dot:.1f} ms")
    print(f"3*dot = {3*dot:.1f} ms")
    print(f"7*dot = {7*dot:.1f} ms")

    # Дискриминатор: on > 2*dot -> dash, else dot
    # off > 5*dot -> word gap, off > 2*dot -> letter gap, else intra-letter
    def decode(dot_dur, dash_thr_mult=2.0, letter_thr_mult=2.0, word_thr_mult=5.0):
        morse_str = ""
        for s, ms in seg_ms:
            if ms < 15 and not s:  # глитч
                continue
            if s:
                if ms > dash_thr_mult * dot_dur:
                    morse_str += "-"
                else:
                    morse_str += "."
            else:
                if ms > word_thr_mult * dot_dur:
                    morse_str += " / "
                elif ms > letter_thr_mult * dot_dur:
                    morse_str += " "
                # иначе intra-letter, ничего
        # убрать ведущие пробелы/слэши
        morse_str = morse_str.strip().strip("/").strip()
        return morse_str

    morse = decode(dot)
    print(f"\nmorse: {morse}")

    def to_text(m):
        words = m.split(" / ")
        out = []
        for w in words:
            letters = w.split()
            txt = ""
            for L in letters:
                txt += MORSE.get(L, f"?{L}?")
            out.append(txt)
        return " ".join(out)

    text = to_text(morse)
    print(f"text: {text}")

    # Если есть '?' — переберём пороги
    if "?" in text:
        print("\n--- пробуем разные пороги ---")
        best = None
        for dash_mult in [1.5, 1.7, 1.8, 2.0, 2.2, 2.5]:
            for letter_mult in [1.5, 1.8, 2.0, 2.5, 3.0]:
                for word_mult in [4.0, 5.0, 6.0, 7.0]:
                    if word_mult <= letter_mult:
                        continue
                    m = decode(dot, dash_mult, letter_mult, word_mult)
                    t = to_text(m)
                    if "?" not in t and len(t) > 2:
                        print(f"dash>{dash_mult} letter>{letter_mult} word>{word_mult}: {t}  | {m}")
                        if best is None:
                            best = (t, m, dash_mult, letter_mult, word_mult)
        if best:
            print(f"\nBEST: {best[0]}  (morse: {best[1]})")
            text = best[0]
            morse = best[1]

    print(f"\n=== FINAL ===")
    print(f"morse: {morse}")
    print(f"text (lower): {text.lower()}")


if __name__ == "__main__":
    main()
