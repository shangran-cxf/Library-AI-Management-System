"""CirculationController：借书、还书、查询借阅信息。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..response import ok
from ..schemas import BorrowRequest, ReturnRequest
from ..services.circulation_service import CirculationService

router = APIRouter(prefix="/api", tags=["circulation"])


@router.post("/circulation/borrow")
def borrow(req: BorrowRequest, db: Session = Depends(get_db)):
    return ok(CirculationService(db).borrow(req.card_no, req.barcode, req.librarian_id))


@router.post("/circulation/return")
def return_book(req: ReturnRequest, db: Session = Depends(get_db)):
    return ok(CirculationService(db).return_book(req.barcode, req.librarian_id))


@router.get("/readers/{reader_id}/loans")
def list_loans(
    reader_id: int,
    operator_type: str = Query(...),
    operator_id: int = Query(...),
    db: Session = Depends(get_db),
):
    return ok(CirculationService(db).query_loans(reader_id, operator_type, operator_id))
