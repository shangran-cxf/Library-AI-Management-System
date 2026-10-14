"""CardController：办理 / 删除借阅证。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..response import ok
from ..schemas import IssueCardRequest
from ..services.card_service import CardService

router = APIRouter(prefix="/api/admin", tags=["card"])


@router.post("/borrow-cards")
def issue_card(req: IssueCardRequest, db: Session = Depends(get_db)):
    return ok(CardService(db).issue(req.reader_id, req.expire_date, req.admin_id))


@router.delete("/borrow-cards/{card_no}")
def delete_card(
    card_no: str, admin_id: int = Query(...), db: Session = Depends(get_db)
):
    return ok(CardService(db).delete(card_no, admin_id))
