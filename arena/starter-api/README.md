# starter-api — FastAPI прототип

Минимальный FastAPI с CORS наружу. Hot-reload включён.

## Запуск

```bash
./serve.sh
# → http://localhost:8000
# → http://localhost:8000/docs   (Swagger, можно тыкать прямо там)
```

## Что менять

- `RunIn`/`RunOut` — модели запроса/ответа
- функция `run` — твоя логика
- добавь `@app.get/post(...)` для новых эндпоинтов

## Связь с фронтом

`starter-web/index.html` уже умеет звать `POST http://localhost:8000/api/run`. Раскомментируй `fetch` в `run()`.
