from pydantic import BaseModel, ValidationError, field_validator

TITLE_MAX = 200
BODY_MAX = 20_000


class NoteCreate(BaseModel):
    title: str
    body: str

    @field_validator("title")
    @classmethod
    def check_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Укажите заголовок")
        if len(cleaned) > TITLE_MAX:
            raise ValueError("Заголовок не длиннее 200 символов")
        return cleaned

    @field_validator("body")
    @classmethod
    def check_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Напишите текст заметки")
        if len(cleaned) > BODY_MAX:
            raise ValueError("Текст не длиннее 20 000 символов")
        return cleaned


class NoteUpdate(NoteCreate):
    pass


def validation_messages(exc: ValidationError) -> list[str]:
    messages: list[str] = []
    for error in exc.errors():
        message = str(error["msg"])
        prefix = "Value error, "
        if message.startswith(prefix):
            message = message.removeprefix(prefix)
        messages.append(message)
    return messages
