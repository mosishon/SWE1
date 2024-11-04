from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.authentication.router import router as auth_router
from src.instructor.router import router as instructor_router
from src.student.router import router as student_router

app = FastAPI(debug=True)
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(instructor_router)
app.include_router(student_router)
