import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.crud import create_tag
from app.models import Message, Tag, TagCreate, TagPublic, TagsPublic, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=TagsPublic)
def read_tags(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve tags.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Tag)
        count = session.exec(count_statement).one()
        statement = (
            select(Tag)
            .order_by(col(Tag.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        tags = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Tag)
            .where(Tag.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Tag)
            .where(Tag.owner_id == current_user.id)
            .order_by(col(Tag.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        tags = session.exec(statement).all()

    return TagsPublic(data=tags, count=count)


@router.get("/{id}", response_model=TagPublic)
def read_tag(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get tag by ID.
    """
    tag = session.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if not current_user.is_superuser and (tag.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return tag


@router.post("/", response_model=TagPublic)
def create_tag_route(
    *, session: SessionDep, current_user: CurrentUser, tag_in: TagCreate
) -> Any:
    """
    Create new tag.
    """
    tag = create_tag(session=session, tag_in=tag_in, owner_id=current_user.id)
    return tag


@router.put("/{id}", response_model=TagPublic)
def update_tag(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    tag_in: TagUpdate,
) -> Any:
    """
    Update a tag.
    """
    tag = session.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if not current_user.is_superuser and (tag.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = tag_in.model_dump(exclude_unset=True)
    tag.sqlmodel_update(update_dict)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{id}")
def delete_tag(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a tag.
    """
    tag = session.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if not current_user.is_superuser and (tag.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(tag)
    session.commit()
    return Message(message="Tag deleted successfully")
