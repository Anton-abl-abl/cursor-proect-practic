# Заметки

Учебное веб-приложение: заметки хранятся локально в SQLite, краткое содержание и ключевые слова считаются на вашей машине.

## Запуск

Нужен Python 3.11 или новее.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Откройте http://127.0.0.1:8000
