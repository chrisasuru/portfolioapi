from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db import init_db
from .routes.users import users_router
from .models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()
    yield


app = FastAPI(lifespan = lifespan)

app.include_router(users_router, prefix="/v1", tags=["users"])

@app.get("/")
async def root():

    return {
        "message": "Hello, World!"
    }
