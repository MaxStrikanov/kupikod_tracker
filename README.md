# Kupikod integrations tracker

Сервис для поиска рекламных интеграций Kupikod у блогеров (VK first).

## Запуск (Docker)

```bash
docker-compose up --build
```

API будет на `http://localhost:8000/docs`.

Нужны переменные окружения:

- `VK_TOKEN` — access_token VK с правами `wall,offline`

## Основные endpoints

- `POST /bloggers/` — создать блогера
- `GET /bloggers/` — список блогеров
- `POST /integrations/kupikod/scan/{blogger_id}` — спарсить посты блогера (VK API)
- `GET /integrations/kupikod` — последние найденные интеграции

## Фоновый сбор

Celery-воркер `worker` использует задачу:

- `scan_all_bloggers_kupikod` — пройти по всем блогерам и найти интеграции Kupikod
```
docker-compose exec worker celery -A app.tasks.celery_app call app.tasks.scan_all_bloggers_kupikod
```
