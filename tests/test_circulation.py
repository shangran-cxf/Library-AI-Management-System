"""集成测试：借书、还书、超期罚款与查询借阅（TC-006 ~ TC-017）。"""
from datetime import datetime, timedelta

from src.domain.enums import LoanStatus
from src.domain.models import Loan


def _borrow(client, seed, card_no=None, barcode=None, librarian_id=None):
    return client.post(
        "/api/circulation/borrow",
        json={
            "card_no": card_no or seed["card_no"],
            "barcode": barcode or seed["barcodes"][0],
            "librarian_id": librarian_id or seed["librarian_id"],
        },
    )


def test_borrow_success(client, seed):
    resp = _borrow(client, seed)
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["loan_id"] is not None
    assert body["data"]["status"] == "BORROWING"
    borrow_date = datetime.fromisoformat(body["data"]["borrow_date"])
    due_date = datetime.fromisoformat(body["data"]["due_date"])
    assert (due_date - borrow_date).days == 30  # 本科生 30 天


def test_borrow_card_invalid(client, seed):
    resp = _borrow(client, seed, card_no="CARD9999999999")
    body = resp.json()
    assert body["code"] == 400
    assert "借阅证无效" in body["message"]


def test_borrow_exceed_limit(client, seed, db):
    # 本科生上限 5；直接构造 5 条在借记录
    for i in range(5):
        db.add(
            Loan(
                reader_id=seed["reader_id"],
                item_id=seed["item_ids"][0],
                borrow_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                status=LoanStatus.BORROWING.value,
            )
        )
    db.commit()
    resp = _borrow(client, seed)
    body = resp.json()
    assert body["code"] == 400
    assert "借阅已满" in body["message"]


def test_borrow_overdue_blocks(client, seed, db):
    db.add(
        Loan(
            reader_id=seed["reader_id"],
            item_id=seed["item_ids"][0],
            borrow_date=datetime.now() - timedelta(days=60),
            due_date=datetime.now() - timedelta(days=30),
            status=LoanStatus.BORROWING.value,
        )
    )
    db.commit()
    resp = _borrow(client, seed, barcode=seed["barcodes"][1])
    body = resp.json()
    assert body["code"] == 400
    assert "超期" in body["message"]


def test_borrow_item_not_available(client, seed, db):
    from src.domain.models import LibraryItem

    item = db.get(LibraryItem, seed["item_ids"][0])
    item.markBorrowed()
    db.commit()
    resp = _borrow(client, seed)
    body = resp.json()
    assert body["code"] == 400
    assert "不可借" in body["message"]


def test_borrow_permission_denied(client, seed):
    resp = _borrow(client, seed, librarian_id=seed["reader_id"])
    assert resp.json()["code"] == 403


def test_return_success(client, seed):
    _borrow(client, seed)
    resp = client.post(
        "/api/circulation/return",
        json={"barcode": seed["barcodes"][0], "librarian_id": seed["librarian_id"]},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["overdue_days"] == 0
    assert body["data"]["fine_amount"] == 0.0


def test_return_not_our_book(client, seed):
    resp = client.post(
        "/api/circulation/return",
        json={"barcode": "NOTEXIST", "librarian_id": seed["librarian_id"]},
    )
    body = resp.json()
    assert body["code"] == 404
    assert "非本馆藏书" in body["message"]


def test_return_no_loan(client, seed):
    resp = client.post(
        "/api/circulation/return",
        json={"barcode": seed["barcodes"][0], "librarian_id": seed["librarian_id"]},
    )
    body = resp.json()
    assert body["code"] == 404
    assert "未找到借阅记录" in body["message"]


def test_return_overdue_generates_fine(client, seed, db):
    # 构造一条已超期 10 天的在借记录（中文图书 0.1 元/天 → 1.00 元）
    db.add(
        Loan(
            reader_id=seed["reader_id"],
            item_id=seed["item_ids"][0],
            borrow_date=datetime.now() - timedelta(days=40),
            due_date=datetime.now() - timedelta(days=10),
            status=LoanStatus.BORROWING.value,
        )
    )
    db.commit()
    resp = client.post(
        "/api/circulation/return",
        json={"barcode": seed["barcodes"][0], "librarian_id": seed["librarian_id"]},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["overdue_days"] == 10
    assert body["data"]["fine_amount"] == 1.0
    assert body["data"]["fine_id"] is not None


def test_query_loans_self(client, seed):
    _borrow(client, seed)
    resp = client.get(
        f"/api/readers/{seed['reader_id']}/loans",
        params={"operator_type": "reader", "operator_id": seed["reader_id"]},
    )
    body = resp.json()
    assert body["code"] == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["title"] == "数据结构"


def test_query_loans_other_denied(client, seed):
    resp = client.get(
        f"/api/readers/{seed['reader2_id']}/loans",
        params={"operator_type": "reader", "operator_id": seed["reader_id"]},
    )
    assert resp.json()["code"] == 403


def test_query_loans_by_librarian(client, seed):
    resp = client.get(
        f"/api/readers/{seed['reader_id']}/loans",
        params={"operator_type": "librarian", "operator_id": seed["librarian_id"]},
    )
    assert resp.json()["code"] == 200
