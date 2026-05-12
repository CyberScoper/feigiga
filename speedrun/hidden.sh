#!/usr/bin/env bash
# Тулкит для задач "найди скрытый ответ".
# Usage: ./hidden.sh <file>
#   или копируй нужный кусок руками.

set -u
F="${1:-}"

if [ -z "$F" ]; then
  cat <<'EOF'
hidden.sh — sweep файла на предмет скрытого контента.

Usage: ./hidden.sh <file>

Что делает:
  1. file — что это вообще такое
  2. wc / size
  3. strings (ASCII + UTF-16)
  4. hex головы (магические байты)
  5. ищет base64-подобные строки
  6. ищет EXIF / metadata (если установлен exiftool)
  7. unzip-проверка (вдруг это zip без расширения)
  8. PNG/JPEG: tail-данные после конца картинки
EOF
  exit 0
fi

if [ ! -f "$F" ]; then
  echo "no such file: $F" >&2
  exit 1
fi

echo "=== file ==="
file "$F"

echo
echo "=== size ==="
wc -c "$F"
ls -lh "$F"

echo
echo "=== hex head (64 bytes) ==="
xxd "$F" | head -4

echo
echo "=== hex tail (64 bytes) ==="
xxd "$F" | tail -4

echo
echo "=== ASCII strings (>=8 chars, top 50) ==="
strings -n 8 "$F" | head -50

echo
echo "=== UTF-16 strings (>=6 chars, top 20) ==="
strings -e l -n 6 "$F" | head -20

echo
echo "=== подозрительно похожее на base64 (>=20 chars) ==="
strings -n 20 "$F" | grep -E '^[A-Za-z0-9+/=]{20,}$' | head -10

echo
echo "=== EXIF / metadata ==="
if command -v exiftool >/dev/null; then
  exiftool "$F" 2>/dev/null | head -30
else
  echo "(exiftool не установлен; apt-get install -y libimage-exiftool-perl)"
fi

echo
echo "=== tail после магического конца (PNG: IEND, JPEG: FFD9) ==="
python3 - "$F" <<'PY'
import sys
p = sys.argv[1]
data = open(p,"rb").read()
# PNG
i = data.find(b"IEND\xaeB`\x82")
if i != -1 and i+8 < len(data):
    extra = data[i+8:]
    print(f"PNG: после IEND ещё {len(extra)} байт")
    print("  hex:", extra[:64].hex())
    print("  txt:", extra[:64])
# JPEG
i = data.rfind(b"\xff\xd9")
if i != -1 and i+2 < len(data):
    extra = data[i+2:]
    print(f"JPEG: после FFD9 ещё {len(extra)} байт")
    print("  hex:", extra[:64].hex())
    print("  txt:", extra[:64])
# ZIP внутри файла
i = data.find(b"PK\x03\x04")
if i > 0:
    print(f"ZIP-сигнатура (PK\\x03\\x04) на смещении {i} — попробуй unzip")
PY

echo
echo "=== попытка как zip ==="
unzip -l "$F" 2>/dev/null | head -20 || echo "(не zip)"

echo
echo "=== быстрые декоды первой подозрительной base64-строки ==="
B64=$(strings -n 24 "$F" | grep -Em1 '^[A-Za-z0-9+/=]{24,}$' || true)
if [ -n "$B64" ]; then
  echo "candidate: ${B64:0:60}..."
  echo "$B64" | base64 -d 2>/dev/null | xxd | head -4 || echo "(не base64)"
fi
