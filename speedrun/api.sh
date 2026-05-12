#!/usr/bin/env bash
# Шпаргалка curl/HTTP. Не запускать целиком, копируй нужный кусок.

# === GET простой ===
curl -sS https://api.example.com/v1/items | jq .

# === GET с headers и токеном ===
curl -sS \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" \
  "https://api.example.com/v1/items?limit=100&page=1" | jq .

# === POST JSON ===
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"vibe","ok":true}' \
  https://api.example.com/v1/items

# === видеть все headers (статус, redirect, rate-limit) ===
curl -sS -i https://api.example.com/v1/items | head -30

# === только headers ===
curl -sSI https://api.example.com/v1/items

# === следовать redirect-ам и тайминг ===
curl -sSL -w "\n--- %{http_code} %{time_total}s %{size_download}b ---\n" \
  https://api.example.com/v1/items -o /dev/null

# === скачать файл, сохранить имя с сервера ===
curl -sSLOJ https://example.com/path/file

# === дёрнуть через прокси (если нужен SOCKS) ===
# curl --socks5 127.0.0.1:1080 https://...

# === пагинация: цикл, пока есть next ===
url="https://api.example.com/v1/items?page=1"
while [ -n "$url" ] && [ "$url" != "null" ]; do
  resp=$(curl -sS "$url")
  echo "$resp" | jq '.items[]'
  url=$(echo "$resp" | jq -r '.next // empty')
done

# === если jq нет, ставь на лету ===
# apt-get install -y jq
# или python -c "import sys,json;print(json.load(sys.stdin))"

# === послать форму (urlencoded) ===
curl -sS -X POST \
  --data-urlencode "user=vibe" \
  --data-urlencode "pass=secret" \
  https://example.com/login

# === multipart upload ===
curl -sS -X POST \
  -F "file=@/path/to/image.png" \
  -F "title=hello" \
  https://example.com/upload

# === keep cookies между запросами ===
curl -c cookies.txt -b cookies.txt https://example.com/login -d 'u=x&p=y'
curl -b cookies.txt https://example.com/me

# === видеть ровно то, что отправляешь (debug request) ===
curl -v https://api.example.com/ 2>&1 | grep '^>'
