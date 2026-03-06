from fastapi import APIRouter

from app.api.routes import contacts, events, items, login, notes, private, tags, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(tags.router)
api_router.include_router(contacts.router)
api_router.include_router(events.router)
api_router.include_router(notes.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
