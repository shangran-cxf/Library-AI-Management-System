"""集成测试：图书标题与馆藏副本（TC-021 ~ TC-024）。"""


def test_add_title_success(client, seed):
    resp = client.post(
        "/api/admin/book-titles",
        json={
            "title": "操作系统",
            "author": "汤小丹",
            "isbn": "9787302000002",
            "category": "计算机",
            "item_type": "CHINESE_BOOK",
            "admin_id": seed["admin_id"],
        },
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["title_id"] is not None
    assert body["data"]["available_count"] == 0


def test_add_title_duplicate_isbn(client, seed):
    resp = client.post(
        "/api/admin/book-titles",
        json={
            "title": "数据结构（重印）",
            "author": "严蔚敏",
            "isbn": seed["isbn"],
            "item_type": "CHINESE_BOOK",
            "admin_id": seed["admin_id"],
        },
    )
    body = resp.json()
    assert body["code"] == 400
    assert "ISBN" in body["message"]


def test_add_item_success(client, seed):
    resp = client.post(
        "/api/admin/library-items",
        json={
            "title_id": seed["title_id"],
            "barcode": "BC0009",
            "location": "A区3架",
            "admin_id": seed["admin_id"],
        },
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["status"] == "AVAILABLE"
    assert body["data"]["item_type"] == "CHINESE_BOOK"


def test_add_item_duplicate_barcode(client, seed):
    resp = client.post(
        "/api/admin/library-items",
        json={
            "title_id": seed["title_id"],
            "barcode": seed["barcodes"][0],
            "admin_id": seed["admin_id"],
        },
    )
    body = resp.json()
    assert body["code"] == 400
    assert "条码" in body["message"]


def test_search_books(client, seed):
    resp = client.get("/api/books", params={"keyword": "数据"})
    body = resp.json()
    assert body["code"] == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["available_count"] == 2
