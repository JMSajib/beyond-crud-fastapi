from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.db.main import init_db


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting .....")
    await init_db()
    yield
    print("server has been stopped")


version = "v1"
app = FastAPI(
    title="Book Project",
    description="REST API for a book review web service",
    version=version,
    lifespan=life_span,
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
