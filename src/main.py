from fastapi import FastAPI

from src.authentication.router import router as auth_router
from src.instructor.router import router as instructor_router

app = FastAPI(debug=True)
app.include_router(auth_router)
app.include_router(instructor_router)
