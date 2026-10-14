"""集成测试：读者注册与借阅证（TC-001 ~ TC-005）。"""


def test_register_reader_success(client):
    resp = client.post(
        "/api/readers",
        json={
            "name": "赵六",
            "department": "数学",
            "reader_type": "GRADUATE",
            "account": "zhaoliu",
            "password": "123456",
        },
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["reader_id"] is not None
    assert body["data"]["reader_type"] == "GRADUATE"


def test_register_reader_duplicate(client, seed):
    resp = client.post(
        "/api/readers",
        json={
            "name": "张三副本",
            "reader_type": "UNDERGRADUATE",
            "account": "zhangsan",
            "password": "123456",
        },
    )
    body = resp.json()
    assert body["code"] == 400
    assert "已存在" in body["message"]


def test_issue_card_success(client, seed):
    resp = client.post(
        "/api/admin/borrow-cards",
        json={"reader_id": seed["reader2_id"], "admin_id": seed["admin_id"]},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["card_no"].startswith("CARD")
    assert len(body["data"]["card_no"]) == 14  # CARD + 4位年份 + 6位序号


def test_issue_card_reader_not_found(client, seed):
    resp = client.post(
        "/api/admin/borrow-cards",
        json={"reader_id": 999999, "admin_id": seed["admin_id"]},
    )
    assert resp.json()["code"] == 404


def test_issue_card_duplicate(client, seed):
    resp = client.post(
        "/api/admin/borrow-cards",
        json={"reader_id": seed["reader_id"], "admin_id": seed["admin_id"]},
    )
    body = resp.json()
    assert body["code"] == 400
    assert "已有借阅证" in body["message"]
