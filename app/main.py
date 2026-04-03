from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, users, records, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Backend")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)