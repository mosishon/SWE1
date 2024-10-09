from fastapi import FastAPI

from src.authentication.router import router

app = FastAPI(debug=True)
app.include_router(router)
