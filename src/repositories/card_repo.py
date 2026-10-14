"""BorrowCardRepository：借阅证持久化。"""
from ..domain.enums import CardStatus
from ..domain.models import BorrowCard


class BorrowCardRepository:
    def __init__(self, session):
        self.session = session

    def get_by_card_no(self, card_no: str):
        return self.session.query(BorrowCard).filter_by(card_no=card_no).first()

    def get_active_by_reader(self, reader_id: int):
        return (
            self.session.query(BorrowCard)
            .filter_by(reader_id=reader_id, status=CardStatus.ACTIVE.value)
            .first()
        )

    def save(self, card: BorrowCard) -> BorrowCard:
        self.session.add(card)
        self.session.flush()
        return card

    def next_card_serial(self, year: int) -> int:
        prefix = f"CARD{year}"
        count = (
            self.session.query(BorrowCard)
            .filter(BorrowCard.card_no.like(f"{prefix}%"))
            .count()
        )
        return count + 1
