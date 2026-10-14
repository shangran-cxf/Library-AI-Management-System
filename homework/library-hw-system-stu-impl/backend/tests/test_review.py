"""任务二：图书评论与评分接口测试。"""


def _add_review(client, book_id, user_id, rating, comment=None):
    return client.post(
        f"/api/books/{book_id}/reviews",
        json={"user_id": user_id, "rating": rating, "comment": comment},
    )


def test_add_review_success(client, seed):
    resp = _add_review(client, seed["book_id"], seed["user_id"], 5, "太好看了")
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["review_id"] is not None
    assert body["data"]["rating"] == 5
    assert body["data"]["comment"] == "太好看了"
    assert body["data"]["book_title"] == "三体"


def test_add_review_rating_too_high(client, seed):
    body = _add_review(client, seed["book_id"], seed["user_id"], 6).json()
    assert body["code"] == 400
    assert "1-5" in body["message"]


def test_add_review_rating_too_low(client, seed):
    body = _add_review(client, seed["book_id"], seed["user_id"], 0).json()
    assert body["code"] == 400
    assert "1-5" in body["message"]


def test_add_review_book_not_found(client, seed):
    body = _add_review(client, 999999, seed["user_id"], 4).json()
    assert body["code"] == 400
    assert "图书不存在" in body["message"]


def test_add_review_user_not_found(client, seed):
    body = _add_review(client, seed["book_id"], 999999, 4).json()
    assert body["code"] == 400
    assert "用户不存在" in body["message"]


def test_list_reviews_empty(client, seed):
    resp = client.get(f"/api/books/{seed['book_id']}/reviews")
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["total"] == 0
    assert body["data"]["average_rating"] == 0
    assert body["data"]["reviews"] == []


def test_list_reviews_average(client, seed):
    _add_review(client, seed["book_id"], seed["user_id"], 5, "很棒")
    _add_review(client, seed["book_id"], seed["other_user_id"], 4, "不错")
    body = client.get(f"/api/books/{seed['book_id']}/reviews").json()
    assert body["code"] == 200
    assert body["data"]["total"] == 2
    assert body["data"]["average_rating"] == 4.5
    assert len(body["data"]["reviews"]) == 2
    # 评论列表应包含用户名与评分
    ratings = sorted(r["rating"] for r in body["data"]["reviews"])
    assert ratings == [4, 5]


def test_list_reviews_average_rounding(client, seed):
    _add_review(client, seed["book_id"], seed["user_id"], 5)
    _add_review(client, seed["book_id"], seed["other_user_id"], 4)
    _add_review(client, seed["book_id"], seed["user_id"], 4)
    body = client.get(f"/api/books/{seed['book_id']}/reviews").json()
    # (5+4+4)/3 = 4.333... → 4.3
    assert body["data"]["average_rating"] == 4.3


def test_list_reviews_book_not_found(client, seed):
    resp = client.get("/api/books/999999/reviews")
    assert resp.json()["code"] == 404
