from fastapi import FastAPI
from app.api.routes import api_router

app = FastAPI(title="Sales Analytics API", version="0.1.0")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
	return {"message": "Sales Analytics API is running"}
