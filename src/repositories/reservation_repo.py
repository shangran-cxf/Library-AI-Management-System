"""ReservationRepository：预约持久化。"""
from ..domain.enums import ReservationStatus
from ..domain.models import Reservation


class ReservationRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, reservation_id: int):
        return self.session.get(Reservation, reservation_id)

    def get_active(self, reader_id: int, title_id: int):
        return (
            self.session.query(Reservation)
            .filter_by(
                reader_id=reader_id,
                title_id=title_id,
                status=ReservationStatus.ACTIVE.value,
            )
            .first()
        )

    def count_active_by_title(self, title_id: int) -> int:
        return (
            self.session.query(Reservation)
            .filter_by(title_id=title_id, status=ReservationStatus.ACTIVE.value)
            .count()
        )

    def list_queue(self, title_id: int):
        return (
            self.session.query(Reservation)
            .filter_by(title_id=title_id, status=ReservationStatus.ACTIVE.value)
            .order_by(Reservation.created_at.asc(), Reservation.reservation_id.asc())
            .all()
        )

    def save(self, reservation: Reservation) -> Reservation:
        self.session.add(reservation)
        self.session.flush()
        return reservation
