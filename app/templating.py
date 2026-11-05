from datetime import datetime
from pathlib import Path

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _format_dt(value: datetime) -> str:
    return value.strftime("%d.%m.%Y %H:%M")


templates.env.filters["format_dt"] = _format_dt
