"""ReaderController：读者注册。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..response import ok
from ..schemas import ReaderRegisterRequest
from ..services.reader_service import ReaderService

router = APIRouter(prefix="/api", tags=["reader"])


@router.post("/readers")
def register_reader(req: ReaderRegisterRequest, db: Session = Depends(get_db)):
    return ok(ReaderService(db).register(req))
