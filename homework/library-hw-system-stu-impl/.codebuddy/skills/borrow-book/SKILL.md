---
name: borrow-book
description: 借阅图书技能。由 circulation-agent 在 orchestrator-agent 委派下调用，提供借阅接口参考。
metadata:
  version: "1.1"
  api-base: "http://localhost:8001"
---

> 说明：本 skill 不在用户输入时自动触发；借书意图由 `orchestrator-agent` 委派 `circulation-agent` 执行，circulation-agent 需解析参数时参考本 skill。

## 后端真实 API 映射
基址 `http://localhost:8001`，统一返回 `{code, message, data}`。
本表为速查摘要，字段完整定义以 `circulation-agent` 的 API 映射表为准；两者冲突时以后者为准。
| 能力 | 方法 | 路径 | 请求体 / 参数 |
|------|------|------|--------------|
| 用户信息 | GET | `/api/users/{user_id}` | 路径参数，返回 `user_id`/`username`/`role`/`max_borrow`；不存在时 `code=404` |
| 查配额 | GET | `/api/borrow/check-quota/{user_id}` | 路径参数，返回 `current_borrowed`/`max_borrow`/`remaining`/`has_overdue`/`overdue_count` |
| 图书详情 | GET | `/api/books/{book_id}` | 路径参数，返回 `available_copies`/`status` |
| 借阅 | POST | `/api/borrow` | `{user_id, book_id}`，返回 `record_id`/`book_title`/`borrow_date`/`due_date`/`remaining_quota` |

## Input
- user_id: integer（必需）- 用户ID
- book_id: integer（必需）- 图书ID
- username: string（必需）- 用户名（用于验证）

## Output
- 借阅结果，包含：是否成功、图书名称、借阅日期、应还日期

## Procedure
### 第1步：用户身份验证
```python
import httpx
# 调用用户查询API
response = httpx.get(f"http://localhost:8001/api/users/{user_id}")
user_data = response.json()

if user_data["code"] != 200:
    返回："用户不存在，请检查用户ID"
```

### 第2步：检查借阅配额
```python
# 调用配额检查API
response = httpx.get(f"http://localhost:8001/api/borrow/check-quota/{user_id}")
quota_data = response.json()

if quota_data["data"]["remaining"] <= 0:
    返回："您的借阅已满（{current_borrowed}/{max_borrow}），请先归还图书再借阅"

if quota_data["data"]["has_overdue"]:
    返回："您有{overdue_count}本图书超期未还，请先归还"
```

### 第3步：检查图书状态
```python
# 调用图书详情API
response = httpx.get(f"http://localhost:8001/api/books/{book_id}")
book_data = response.json()

if book_data["data"]["available_copies"] <= 0:
    返回："《{title}》已全部借出，您可以预约"
```

### 第4步：执行借阅操作
```python
# 调用借阅API
response = httpx.post(
    "http://localhost:8001/api/borrow",
    json={"user_id": user_id, "book_id": book_id}
)
result = response.json()
```

### 第5步：判断响应码并返回结果
- `code == 200`：返回借阅成功信息，包含 `data.book_title`、`data.borrow_date`、`data.due_date`
- `code == 400`：把 `message` 原样透传给用户（如"借阅已满（3/3），请先归还图书"、"图书已全部借出"）
- `code == 500`：返回"系统繁忙，请稍后重试"

## Acceptance Criteria
- 每一步必须调用对应的 API，不可直接操作数据库
- 任何步骤失败都必须给出明确的错误信息
- 借阅成功后必须向用户确认借阅信息
- 如果用户只说了书名没说具体哪本，必须先用搜索 Skill 让用户选择
