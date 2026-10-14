"""任务一：续借接口测试。"""
from datetime import datetime


def test_renew_success_default_30_days(client, seed):
    resp = client.post("/api/renew", json={"record_id": seed["borrowing_record_id"]})
    body = resp.json()
    assert body["code"] == 200
    # 原应还 2026-07-20，默认延长 30 天 → 2026-08-19
    assert body["data"]["old_due_date"] == "2026-07-20"
    assert body["data"]["new_due_date"] == "2026-08-19"
    assert body["data"]["extend_days"] == 30
    assert body["data"]["book_title"] == "三体"
    assert "2026-08-19" in body["message"]


def test_renew_success_custom_days(client, seed):
    resp = client.post(
        "/api/renew",
        json={"record_id": seed["borrowing_record_id"], "extend_days": 7},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["new_due_date"] == "2026-07-27"
    assert body["data"]["extend_days"] == 7


def test_renew_returned_record_rejected(client, seed):
    resp = client.post("/api/renew", json={"record_id": seed["returned_record_id"]})
    body = resp.json()
    assert body["code"] == 400
    assert "已归还" in body["message"]


def test_renew_record_not_found(client, seed):
    resp = client.post("/api/renew", json={"record_id": 999999})
    body = resp.json()
    assert body["code"] == 400
    assert "不存在" in body["message"]


def test_renew_invalid_extend_days(client, seed):
    resp = client.post(
        "/api/renew",
        json={"record_id": seed["borrowing_record_id"], "extend_days": 0},
    )
    body = resp.json()
    assert body["code"] == 400
    assert "正整数" in body["message"]


def test_renew_persists_new_due_date(client, seed):
    """续借后再查借阅记录，应还日期应为新值。"""
    client.post("/api/renew", json={"record_id": seed["borrowing_record_id"], "extend_days": 10})
    resp = client.get(f"/api/borrow/records/{seed['user_id']}", params={"status": "borrowing"})
    records = resp.json()["data"]["records"]
    target = [r for r in records if r["record_id"] == seed["borrowing_record_id"]][0]
    assert target["due_date"] == "2026-07-30"
