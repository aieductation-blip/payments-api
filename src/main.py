from fastapi import FastAPI
from src import routes
from src.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Payments API"}