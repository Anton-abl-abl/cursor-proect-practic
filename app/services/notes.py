import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Note
from app.schemas import NoteCreate, NoteUpdate
from app.services.analysis import analyze


def list_notes(session: Session, query: str) -> list[Note]:
    stmt = select(Note).order_by(Note.created_at.desc(), Note.id.desc())
    needle = query.strip().casefold()
    if needle:
        stmt = stmt.where(Note.search_text.contains(needle))
    return list(session.scalars(stmt).all())


def get_note(session: Session, note_id: int) -> Note | None:
    return session.scalars(select(Note).where(Note.id == note_id)).first()


def create_note(session: Session, payload: NoteCreate) -> Note:
    note = Note(title=payload.title, body=payload.body)
    _fill_derived(note, payload.title, payload.body)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def update_note(session: Session, note: Note, payload: NoteUpdate) -> Note:
    _fill_derived(note, payload.title, payload.body)
    session.commit()
    session.refresh(note)
    return note


def delete_note(session: Session, note: Note) -> None:
    session.delete(note)
    session.commit()


def _fill_derived(note: Note, title: str, body: str) -> None:
    result = analyze(title, body)
    note.title = title
    note.body = body
    note.summary = result.summary
    note.keywords = json.dumps(result.keywords, ensure_ascii=False)
    note.tags = json.dumps(result.tags, ensure_ascii=False)
    note.key_points = json.dumps(result.key_points, ensure_ascii=False)
    note.search_text = f"{title}\n{body}".casefold()
