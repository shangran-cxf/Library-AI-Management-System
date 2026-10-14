"""CardService：办理 / 删除借阅证。"""
from datetime import date

from ..domain.enums import CardStatus
from ..domain.models import BorrowCard
from ..exceptions import DuplicateError, NotFoundError
from ..repositories import BorrowCardRepository, ReaderRepository
from ..security import require_admin


class CardService:
    def __init__(self, session):
        self.session = session
        self.card_repo = BorrowCardRepository(session)
        self.reader_repo = ReaderRepository(session)

    def issue(self, reader_id: int, expire_date, admin_id: int) -> dict:
        require_admin(self.session, admin_id)

        reader = self.reader_repo.get_by_id(reader_id)
        if reader is None:
            raise NotFoundError("读者不存在")
        if self.card_repo.get_active_by_reader(reader_id) is not None:
            raise DuplicateError("该读者已有借阅证")

        year = date.today().year
        serial = self.card_repo.next_card_serial(year)
        card_no = f"CARD{year}{serial:06d}"
        card = BorrowCard(
            card_no=card_no,
            reader_id=reader_id,
            issue_date=date.today(),
            expire_date=expire_date,
            status=CardStatus.ACTIVE.value,
        )
        self.card_repo.save(card)
        data = {
            "card_id": card.card_id,
            "card_no": card.card_no,
            "reader_id": card.reader_id,
            "issue_date": card.issue_date,
            "expire_date": card.expire_date,
            "status": card.status,
        }
        self.session.commit()
        return data

    def delete(self, card_no: str, admin_id: int) -> dict:
        require_admin(self.session, admin_id)

        card = self.card_repo.get_by_card_no(card_no)
        if card is None:
            raise NotFoundError("借阅证不存在")
        card.status = CardStatus.INACTIVE.value
        self.card_repo.save(card)
        self.session.commit()
        return {"card_no": card.card_no, "status": card.status}
