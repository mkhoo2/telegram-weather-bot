## Running locally

```code
uvicorn main:app --reload
```

Run ngrok to expose url for telegram hook
```code
ngrok http 8000 
```

Set the url to telegram hook
```code
https://api.telegram.org/botYOUR_TOKEN/setWebhook?url=<url>
```

Run local postgres using docker
```code
docker run --name postgres-local \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=weather_bot \
  -p 5432:5432 \
  -d postgres:18
```

env file
```code
TELEGRAM_BOT_TOKEN=<token>
DATABASE_URL=<url>
```