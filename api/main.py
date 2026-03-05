from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import datetime
import os

from database.database import Base, engine

from .routes import auth, chat, documents, users


# adding logging
# adding logging
now = datetime.datetime.now()

date_folder = now.strftime('%m_%d_%Y')        # 01_20_2026
time_folder = now.strftime('%H_%M_%S')        # 14_30_45

logs_dir = os.path.join(os.getcwd(), "Logs", date_folder, time_folder)
os.makedirs(logs_dir, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_dir, "app.log")

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    print("Starting up...")
    Base.metadata.create_all(bind=engine)   # create tables if they don't exist
    yield

    # shutdown code
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)
# uvicorn api.main:app --reload        for local testing

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

