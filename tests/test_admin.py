"""集成测试：管理员维护与权限（TC-025、TC-026）。"""


def test_reader_cannot_add_title(client, seed):
    resp = client.post(
        "/api/admin/book-titles",
        json={
            "title": "非法标题",
            "author": "某人",
            "isbn": "9787000000001",
            "item_type": "CHINESE_BOOK",
            "admin_id": seed["reader_id"],  # 读者冒充管理员
        },
    )
    assert resp.json()["code"] == 403


def test_add_librarian_success(client, seed):
    resp = client.post(
        "/api/admin/librarians",
        json={
            "name": "新管理员",
            "account": "lib2",
            "password": "lib123",
            "admin_id": seed["admin_id"],
        },
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["librarian_id"] is not None


def test_add_librarian_denied(client, seed):
    resp = client.post(
        "/api/admin/librarians",
        json={
            "name": "非法管理员",
            "account": "lib3",
            "admin_id": seed["librarian_id"],
        },
    )
    assert resp.json()["code"] == 403


def test_update_borrow_policy_effective(client, seed):
    # 把本科生借阅期限改为 7 天
    resp = client.put(
        "/api/admin/borrow-policies",
        json={
            "reader_type": "UNDERGRADUATE",
            "max_borrow_count": 5,
            "borrow_days": 7,
            "admin_id": seed["admin_id"],
        },
    )
    assert resp.json()["code"] == 200

    from datetime import datetime

    body = client.post(
        "/api/circulation/borrow",
        json={
            "card_no": seed["card_no"],
            "barcode": seed["barcodes"][0],
            "librarian_id": seed["librarian_id"],
        },
    ).json()
    borrow_date = datetime.fromisoformat(body["data"]["borrow_date"])
    due_date = datetime.fromisoformat(body["data"]["due_date"])
    assert (due_date - borrow_date).days == 7


def test_update_fine_rule_effective(client, seed, db):
    resp = client.put(
        "/api/admin/fine-rules",
        json={
            "item_type": "CHINESE_BOOK",
            "rate_per_day": 0.5,
            "admin_id": seed["admin_id"],
        },
    )
    assert resp.json()["code"] == 200

    from datetime import datetime, timedelta

    from src.domain.enums import LoanStatus
    from src.domain.models import Loan

    db.add(
        Loan(
            reader_id=seed["reader_id"],
            item_id=seed["item_ids"][0],
            borrow_date=datetime.now() - timedelta(days=20),
            due_date=datetime.now() - timedelta(days=10),
            status=LoanStatus.BORROWING.value,
        )
    )
    db.commit()

    body = client.post(
        "/api/circulation/return",
        json={"barcode": seed["barcodes"][0], "librarian_id": seed["librarian_id"]},
    ).json()
    assert body["data"]["fine_amount"] == 5.0  # 10 天 × 0.5


def test_delete_librarian(client, seed):
    resp = client.delete(
        f"/api/admin/librarians/{seed['librarian_id']}",
        params={"admin_id": seed["admin_id"]},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["deleted"] is True


def test_health(client):
    resp = client.get("/health")
    assert resp.json()["code"] == 200
