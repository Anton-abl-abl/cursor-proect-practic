from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import NoteCreate, NoteUpdate, validation_messages
from app.services import notes as notes_service
from app.templating import templates

router = APIRouter()


def _not_found(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "notes/not_found.html",
        status_code=404,
    )


def _form_page(
    request: Request,
    *,
    mode: str,
    title_value: str,
    body_value: str,
    errors: list[str],
    note_id: int | None = None,
    status_code: int = 200,
) -> Response:
    return templates.TemplateResponse(
        request,
        "notes/form.html",
        {
            "mode": mode,
            "title_value": title_value,
            "body_value": body_value,
            "errors": errors,
            "note_id": note_id,
        },
        status_code=status_code,
    )


@router.get("/", name="note_list")
def list_notes(request: Request, q: str = "", db: Session = Depends(get_db)) -> Response:
    notes = notes_service.list_notes(db, q)
    return templates.TemplateResponse(
        request,
        "notes/list.html",
        {"notes": notes, "query": q},
    )


@router.get("/notes/new", name="note_new")
def new_note(request: Request) -> Response:
    return _form_page(request, mode="create", title_value="", body_value="", errors=[])


@router.post("/notes", name="note_create")
def create_note(
    request: Request,
    title: Annotated[str, Form()] = "",
    body: Annotated[str, Form()] = "",
    db: Session = Depends(get_db),
) -> Response:
    try:
        payload = NoteCreate(title=title, body=body)
    except ValidationError as exc:
        return _form_page(
            request,
            mode="create",
            title_value=title,
            body_value=body,
            errors=validation_messages(exc),
            status_code=400,
        )
    note = notes_service.create_note(db, payload)
    return RedirectResponse(
        url=request.url_for("note_detail", note_id=note.id),
        status_code=303,
    )


@router.get("/notes/{note_id}", name="note_detail")
def note_detail(request: Request, note_id: int, db: Session = Depends(get_db)) -> Response:
    note = notes_service.get_note(db, note_id)
    if note is None:
        return _not_found(request)
    return templates.TemplateResponse(request, "notes/detail.html", {"note": note})


@router.get("/notes/{note_id}/edit", name="note_edit")
def edit_note(request: Request, note_id: int, db: Session = Depends(get_db)) -> Response:
    note = notes_service.get_note(db, note_id)
    if note is None:
        return _not_found(request)
    return _form_page(
        request,
        mode="edit",
        title_value=note.title,
        body_value=note.body,
        errors=[],
        note_id=note.id,
    )


@router.post("/notes/{note_id}", name="note_update")
def update_note(
    request: Request,
    note_id: int,
    title: Annotated[str, Form()] = "",
    body: Annotated[str, Form()] = "",
    db: Session = Depends(get_db),
) -> Response:
    note = notes_service.get_note(db, note_id)
    if note is None:
        return _not_found(request)
    try:
        payload = NoteUpdate(title=title, body=body)
    except ValidationError as exc:
        return _form_page(
            request,
            mode="edit",
            title_value=title,
            body_value=body,
            errors=validation_messages(exc),
            note_id=note_id,
            status_code=400,
        )
    notes_service.update_note(db, note, payload)
    return RedirectResponse(
        url=request.url_for("note_detail", note_id=note_id),
        status_code=303,
    )


@router.post("/notes/{note_id}/delete", name="note_delete")
def delete_note(request: Request, note_id: int, db: Session = Depends(get_db)) -> Response:
    note = notes_service.get_note(db, note_id)
    if note is None:
        return _not_found(request)
    notes_service.delete_note(db, note)
    return RedirectResponse(url=request.url_for("note_list"), status_code=303)
