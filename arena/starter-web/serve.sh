#!/usr/bin/env bash
# Запуск статики на :3000. Никаких зависимостей — питон уже на машине.
cd "$(dirname "$0")"
echo "→ http://localhost:3000"
exec python3 -m http.server 3000
