from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database.db import init_db, destroy_db
from .routes.users import user_router
from .routes.blog.posts import blog_post_router
from .routes.blog.tags import blog_tag_router
from .routes.auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()
    yield
    destroy_db()


app = FastAPI(lifespan = lifespan)


origins = [
    "http://localhost:5173",  # Vite dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, tags=["users"])
app.include_router(blog_post_router, tags=["blog_posts"])
app.include_router(auth_router, tags = ["auth"])
app.include_router(blog_tag_router, tags = ["tags"])

@app.get("/")
async def root():

    return {
        "message": "Hello, World!"
    }
