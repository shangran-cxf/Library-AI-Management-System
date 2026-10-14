"""应用入口：装配 FastAPI、统一响应与全局异常处理。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .database import init_db
from .exceptions import LibraryError
from .response import fail, ok
from .routers import (
    admin_router,
    card_router,
    catalog_router,
    circulation_router,
    reader_router,
    reservation_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Library AI Management System", version="1.0.0", lifespan=lifespan)


@app.exception_handler(LibraryError)
async def library_error_handler(request: Request, exc: LibraryError):
    return JSONResponse(status_code=exc.code, content=fail(exc.code, exc.message))


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content=fail(400, "参数非法"))


@app.get("/")
@app.get("/health")
def health():
    return ok({"status": "up"})


app.include_router(reader_router.router)
app.include_router(card_router.router)
app.include_router(catalog_router.router)
app.include_router(circulation_router.router)
app.include_router(reservation_router.router)
app.include_router(admin_router.router)
