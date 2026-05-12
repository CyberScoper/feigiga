#!/usr/bin/env python3
"""Декодер морзянки через FFT на 1000 Гц."""
import numpy as np
from scipy.io import wavfile

MORSE = {
    '.-':'a','-...':'b','-.-.':'c','-..':'d','.':'e','..-.':'f','--.':'g',
    '....':'h','..':'i','.---':'j','-.-':'k','.-..':'l','--':'m','-.':'n',
    '---':'o','.--.':'p','--.-':'q','.-.':'r','...':'s','-':'t','..-':'u',
    '...-':'v','.--':'w','-..-':'x','-.--':'y','--..':'z',
    '-----':'0','.----':'1','..---':'2','...--':'3','....-':'4',
    '.....':'5','-....':'6','--...':'7','---..':'8','----.':'9',
}

sr, data = wavfile.read('/mnt/extra/vibe/scratch/morse/morsei.wav')
print(f"sr={sr}, samples={len(data)}, dtype={data.dtype}")
if data.dtype == np.uint8:
    x = data.astype(np.float32) - 128.0
else:
    x = data.astype(np.float32)
if x.ndim > 1:
    x = x[:, 0]
duration = len(x) / sr
print(f"duration = {duration:.3f} s")

# Окно ~10 мс
win = 110
hop = win  # без перекрытия
n_frames = (len(x) - win) // hop + 1
freqs = np.fft.rfftfreq(win, 1/sr)
bin_idx = int(np.argmin(np.abs(freqs - 1000)))
print(f"bin freq = {freqs[bin_idx]:.1f} Hz (idx={bin_idx})")

energy = np.zeros(n_frames)
for i in range(n_frames):
    w = x[i*hop:i*hop+win]
    spec = np.abs(np.fft.rfft(w * np.hanning(win)))
    energy[i] = spec[bin_idx]

# Порог: посредине между min и max, или по медиане
thr = (energy.max() + energy.min()) / 2
# Альтернативно: thr = np.median(energy) * 2
print(f"energy min={energy.min():.1f} max={energy.max():.1f} median={np.median(energy):.1f} thr={thr:.1f}")

binary = (energy > thr).astype(int)

# Run-length encoding
runs = []
cur = binary[0]
cnt = 1
for b in binary[1:]:
    if b == cur:
        cnt += 1
    else:
        runs.append((cur, cnt))
        cur = b
        cnt = 1
runs.append((cur, cnt))

# Отбрасываем ведущий/хвостовой off
if runs and runs[0][0] == 0:
    runs = runs[1:]
if runs and runs[-1][0] == 0:
    runs = runs[:-1]

ons = [c for s, c in runs if s == 1]
offs = [c for s, c in runs if s == 0]
print(f"runs total={len(runs)}, ons={len(ons)}, offs={len(offs)}")
print(f"on durations percentiles: 10={np.percentile(ons,10):.1f} 25={np.percentile(ons,25):.1f} 50={np.median(ons):.1f} 75={np.percentile(ons,75):.1f} 90={np.percentile(ons,90):.1f}")
print(f"on unique-ish: min={min(ons)} max={max(ons)}")
if offs:
    print(f"off percentiles: 10={np.percentile(offs,10):.1f} 25={np.percentile(offs,25):.1f} 50={np.median(offs):.1f} 75={np.percentile(offs,75):.1f} 90={np.percentile(offs,90):.1f}")
    print(f"off min={min(offs)} max={max(offs)}")

# Кластеризация on: dot vs dash. Граница ~ середина между min и max или 2*медиана коротких
on_thr = (min(ons) + max(ons)) / 2
# Для off: 3 класса. Границы примерно на kx и 3x от dit
# dit (короткий on) ~ min(ons)
dit = np.percentile(ons, 25)
print(f"dit~{dit:.1f}, on_thr={on_thr:.1f}")

# Для off используем кластеризацию по соотношениям 1:3:7
# dit≈unit (короткий on). Границы: 2*unit и 5*unit
unit = dit  # длительность точки = 1 unit
off_thr_letter = 2 * unit  # между intra (1u) и inter-letter (3u)
off_thr_word = 5 * unit    # между inter-letter (3u) и inter-word (7u)
# Если dit оказался слишком мал из-за хвоста окон, скорректируем по off min
off_unit = min(offs)  # минимальный off = intra-letter gap = 1u
off_thr_letter = 2 * off_unit
off_thr_word = 5 * off_unit
print(f"off_thr_letter={off_thr_letter:.1f}, off_thr_word={off_thr_word:.1f}")

# Собираем морзе
morse = ''
for s, c in runs:
    if s == 1:
        morse += '.' if c < on_thr else '-'
    else:
        if c < off_thr_letter:
            pass  # внутри буквы
        elif c < off_thr_word:
            morse += ' '
        else:
            morse += '   '

print(f"\nRaw morse:\n{morse}")

# Декодируем
words = morse.split('   ')
decoded = []
for w in words:
    letters = w.split(' ')
    s = ''.join(MORSE.get(l, '?') for l in letters if l)
    decoded.append(s)
result = ' '.join(decoded)
print(f"\nDecoded: {result}")
