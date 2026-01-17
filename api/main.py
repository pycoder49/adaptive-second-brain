from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.database import Base, engine

from .routes import auth, chat, documents, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    print("Starting up...")
    Base.metadata.create_all(bind=engine)   # create tables if they don't exist
    yield

    # shutdown code
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)
# uvircorn api.main:app --reload

# defining CORS origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routing paths
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(users.router)


# root path
@app.get("/")
async def root():
    return {"message": "Welcome to the Adaptive Second Brain API!"}
