"""集成测试：预约图书（TC-018 ~ TC-020）。"""


def test_reserve_success(client, seed):
    resp = client.post(
        "/api/reservations",
        json={"reader_id": seed["reader_id"], "title_id": seed["title_id"]},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["status"] == "ACTIVE"
    assert body["data"]["queue_position"] == 1


def test_reserve_queue_order(client, seed):
    client.post(
        "/api/reservations",
        json={"reader_id": seed["reader_id"], "title_id": seed["title_id"]},
    )
    resp = client.post(
        "/api/reservations",
        json={"reader_id": seed["reader2_id"], "title_id": seed["title_id"]},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["queue_position"] == 2


def test_reserve_duplicate(client, seed):
    payload = {"reader_id": seed["reader_id"], "title_id": seed["title_id"]}
    client.post("/api/reservations", json=payload)
    resp = client.post("/api/reservations", json=payload)
    body = resp.json()
    assert body["code"] == 400
    assert "已预约过" in body["message"]


def test_reserve_reader_not_found(client, seed):
    resp = client.post(
        "/api/reservations",
        json={"reader_id": 999999, "title_id": seed["title_id"]},
    )
    assert resp.json()["code"] == 404


def test_reserve_title_not_found(client, seed):
    resp = client.post(
        "/api/reservations",
        json={"reader_id": seed["reader_id"], "title_id": 999999},
    )
    assert resp.json()["code"] == 404
