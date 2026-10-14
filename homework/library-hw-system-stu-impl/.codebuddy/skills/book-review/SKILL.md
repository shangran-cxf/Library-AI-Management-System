---
name: book-review
description: 图书评论与评分技能。由 orchestrator-agent 按需调用（评论/评分/书评类意图），提供评论接口参考。
metadata:
  version: "1.0"
  api-base: "http://localhost:8001"
---

> 说明：本 skill 不在用户输入时自动触发，而是由 `orchestrator-agent`（评论/评分/书评类意图）按需调用；本类操作与"找书"性质相近，走 `use_skill` 模式，不委派 circulation-agent。

## 后端真实 API 映射
基址 `http://localhost:8001`，统一返回 `{code, message, data}`。
| 能力 | 方法 | 路径 | 请求体 / 参数 |
|------|------|------|--------------|
| 发表评论 | POST | `/api/books/{book_id}/reviews` | `{user_id, rating, comment}`，返回 `review_id` |
| 查看评论 | GET | `/api/books/{book_id}/reviews` | 路径参数，返回 `average_rating`、`total`、`reviews[]` |
| 解析 book_id | GET | `/api/books/search` | `keyword`（query），见 `book-search` skill |

## Input
- action: string（必需）- 操作类型：add（写评论） / list（看评论）
- book_id: integer（写评论时必需；看评论时从书名解析）
- user_id: integer（写评论时必需）- 评论人用户ID
- rating: integer（写评论时必需）- 评分 1-5
- comment: string（可选）- 评论内容
- keyword: string（可选）- 书名关键词，用于解析 book_id

## Output
- 写评论：`review_id`、`book_title`、`rating`、`comment`
- 看评论：`average_rating`（平均评分）、`total`（评论数）、`reviews[]`（评论列表）

## Procedure
### 场景一：写评论
1. 若只知道书名，先调 `book-search` 的 `GET /api/books/search?keyword=书名` 拿到 `book_id`
2. 调用写评论 API：
   ```python
   import httpx
   response = httpx.post(
       "http://localhost:8001/api/books/{book_id}/reviews",
       json={"user_id": user_id, "rating": rating, "comment": comment}
   )
   result = response.json()
   ```
3. 成功（`code == 200`）：回复 "已成功为《{book_title}》评分 {rating} 分并保存评论。"
4. 失败（`code == 400`）：把 `message` 原样透传（如"评分必须在 1-5 之间"）

### 场景二：查看评论
1. 若只知道书名，先解析 `book_id`
2. 调用查看评论 API：
   ```python
   response = httpx.get("http://localhost:8001/api/books/{book_id}/reviews")
   result = response.json()
   ```
3. 按以下格式整理：
   ```
   《{book_title}》平均评分：{average_rating}（共 {total} 条评论）
   - {username}：{rating} 分 — {comment}
   ```

## Acceptance Criteria
- 评分必须在 1-5 之间，超范围必须由后端拒绝并原样提示用户
- 平均评分字段名必须使用后端返回的 `average_rating`，前后端保持一致
- 只知书名时必须先解析 `book_id`，不可凭空构造
