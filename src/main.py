from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.authentication.router import router as auth_router
from src.course.router import router as course_router
from src.course.utils import retreive_orginzer_data_from_db
from src.dependencies import SessionMaker
from src.exceptions import GlobalException
from src.instructor.router import router as instructor_router
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
    await retreive_orginzer_data_from_db()


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
