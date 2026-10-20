from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from api.appliances import router as appliances_router
from api.users import router as users_router

app = FastAPI(
    title="Electrical Appliances EMF API",
    description="API для системы оценки ЭМП от бытовых приборов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(appliances_router)
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
