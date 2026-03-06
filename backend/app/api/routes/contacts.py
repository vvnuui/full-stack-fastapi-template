import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.crud import create_contact
from app.models import (
    Contact,
    ContactCreate,
    ContactPublic,
    ContactsPublic,
    ContactUpdate,
    Message,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=ContactsPublic)
def read_contacts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
) -> Any:
    """
    Retrieve contacts.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Contact)
        count = session.exec(count_statement).one()
        statement = (
            select(Contact)
            .order_by(col(Contact.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        contacts = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Contact)
            .where(Contact.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Contact)
            .where(Contact.owner_id == current_user.id)
            .order_by(col(Contact.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        contacts = session.exec(statement).all()

    return ContactsPublic(data=contacts, count=count)


@router.get("/{id}", response_model=ContactPublic)
def read_contact(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get contact by ID.
    """
    contact = session.get(Contact, id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if not current_user.is_superuser and (contact.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return contact


@router.post("/", response_model=ContactPublic)
def create_contact_route(
    *, session: SessionDep, current_user: CurrentUser, contact_in: ContactCreate
) -> Any:
    """
    Create new contact.
    """
    contact = create_contact(
        session=session, contact_in=contact_in, owner_id=current_user.id
    )
    return contact


@router.put("/{id}", response_model=ContactPublic)
def update_contact(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    contact_in: ContactUpdate,
) -> Any:
    """
    Update a contact.
    """
    contact = session.get(Contact, id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if not current_user.is_superuser and (contact.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = contact_in.model_dump(exclude_unset=True)
    contact.sqlmodel_update(update_dict)
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@router.delete("/{id}")
def delete_contact(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a contact.
    """
    contact = session.get(Contact, id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if not current_user.is_superuser and (contact.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(contact)
    session.commit()
    return Message(message="Contact deleted successfully")
