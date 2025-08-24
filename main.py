from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database.db import init_db, destroy_db
from .routes.users import users_router
from .models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()
    yield
    destroy_db()


app = FastAPI(lifespan = lifespan)

app.include_router(users_router, prefix="/v1", tags=["users"])

@app.get("/")
async def root():

    return {
        "message": "Hello, World!"
    }
