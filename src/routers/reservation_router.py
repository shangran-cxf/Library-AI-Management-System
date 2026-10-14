"""ReservationController：预约图书。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..response import ok
from ..schemas import ReservationRequest
from ..services.reservation_service import ReservationService

router = APIRouter(prefix="/api", tags=["reservation"])


@router.post("/reservations")
def reserve(req: ReservationRequest, db: Session = Depends(get_db)):
    return ok(ReservationService(db).reserve(req.reader_id, req.title_id))
