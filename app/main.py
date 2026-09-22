import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import expenses, summary

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spend Tracker")
app.include_router(expenses.router)
app.include_router(summary.router)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
