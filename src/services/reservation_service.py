"""ReservationService：预约图书与排队。"""
from datetime import datetime

from ..domain.enums import ReservationStatus
from ..domain.models import Reservation
from ..exceptions import DuplicateError, NotFoundError
from ..repositories import BookTitleRepository, ReaderRepository, ReservationRepository


class ReservationService:
    def __init__(self, session):
        self.session = session
        self.reader_repo = ReaderRepository(session)
        self.title_repo = BookTitleRepository(session)
        self.res_repo = ReservationRepository(session)

    def reserve(self, reader_id: int, title_id: int) -> dict:
        reader = self.reader_repo.get_by_id(reader_id)
        if reader is None:
            raise NotFoundError("读者不存在")
        title = self.title_repo.get_by_id(title_id)
        if title is None:
            raise NotFoundError("图书标题不存在")
        if self.res_repo.get_active(reader_id, title_id) is not None:
            raise DuplicateError("您已预约过该书")

        reservation = Reservation(
            reader_id=reader_id,
            title_id=title_id,
            created_at=datetime.now(),
            status=ReservationStatus.ACTIVE.value,
        )
        self.res_repo.save(reservation)

        queue = self.res_repo.list_queue(title_id)
        position = len(queue)
        for index, item in enumerate(queue):
            if item.reservation_id == reservation.reservation_id:
                position = index + 1
                break
        reservation.queue_position = position

        data = {
            "reservation_id": reservation.reservation_id,
            "reader_id": reservation.reader_id,
            "title_id": reservation.title_id,
            "created_at": reservation.created_at,
            "status": reservation.status,
            "queue_position": reservation.queue_position,
        }
        self.session.commit()
        return data
