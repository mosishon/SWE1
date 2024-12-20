from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.authentication.router import router as auth_router
from src.course.router import router as course_router
from src.dependencies import SessionMaker
from src.exceptions import GlobalException
from src.instructor.router import router as instructor_router
from src.student.models import Student
from src.student.router import router as student_router

app = FastAPI(debug=True)


@app.exception_handler(GlobalException)
async def unicorn_exception_handler(request: Request, exc: GlobalException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.model.model_dump(),
    )


origins = [
    "*",
]


@app.get("/test")
async def test(maker: SessionMaker):
    async with maker.begin() as session:
        res = await session.execute(
            select(Student).options(selectinload(Student.reserved_courses))
        )
        for student in res.unique().scalars().all():
            print(student.reserved_courses)


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
app.include_router(course_router)
