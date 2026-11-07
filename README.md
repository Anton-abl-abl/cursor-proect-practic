# Заметки

Учебное веб-приложение: краткое содержание и ключевые слова считаются на вашей машине. Заметки лежат в локальном SQLite, а если задан `DATABASE_URL` — в Postgres на Supabase.

## Запуск

Нужен Python 3.11 или новее.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Откройте http://127.0.0.1:8000

## Supabase

1. В [Supabase](https://supabase.com) создайте проект и сохраните пароль базы.
2. Откройте **Project Settings → Database → Connection string** и скопируйте **Session pooler** (порт `5432`).
3. Скопируйте `.env.example` в `.env` и вставьте строку в `DATABASE_URL`.
4. Запустите приложение ещё раз. Таблица `notes` создастся сама.

Без файла `.env` приложение работает с локальным `data/notes.db`. Старые заметки из этого файла в Supabase сами не переносятся.
