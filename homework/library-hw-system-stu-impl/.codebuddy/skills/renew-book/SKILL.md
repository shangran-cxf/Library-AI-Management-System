---
name: renew-book
description: 续借图书技能。由 circulation-agent 在 orchestrator-agent 委派下调用，提供续借接口参考。
metadata:
  version: "1.0"
  api-base: "http://localhost:8001"
---

> 说明：本 skill 不在用户输入时自动触发；续借意图由 `orchestrator-agent` 委派 `circulation-agent` 执行，circulation-agent 需解析参数时参考本 skill。

## 后端真实 API 映射
基址 `http://localhost:8001`，统一返回 `{code, message, data}`。
| 能力 | 方法 | 路径 | 请求体 / 参数 |
|------|------|------|--------------|
| 查在借记录 | GET | `/api/borrow/records/{user_id}?status=borrowing` | 路径参数 + `status`，返回 `records[].record_id` / `due_date` |
| 续借 | POST | `/api/renew` | `{record_id, extend_days}`，返回 `new_due_date` |

## Input
- user_id: integer（必需）- 用户ID（用于定位在借记录）
- record_id: integer（必需）- 借阅记录ID
- extend_days: integer（可选，默认 30）- 延长天数

## Output
- 续借结果，包含：书名 `book_title`、原应还日期 `old_due_date`、新应还日期 `new_due_date`、延长天数 `extend_days`

## Procedure
### 第1步：查询用户当前在借记录，定位 record_id
```python
import httpx
# 只取在借（borrowing）记录
response = httpx.get(f"http://localhost:8001/api/borrow/records/{user_id}?status=borrowing")
records_data = response.json()
# 按书名匹配用户想续借的那本，取出对应 record_id
# 若匹配到多条，先让用户确认是哪一本
# 若无匹配，返回："该图书不在借阅中，无需续借"
```

### 第2步：执行续借
```python
# 调用续借API（用户未指定天数时默认 30）
response = httpx.post(
    "http://localhost:8001/api/renew",
    json={"record_id": record_id, "extend_days": extend_days}
)
result = response.json()
```

### 第3步：返回结果
- 成功（`code == 200`）：回复 "续借成功！新的应还日期为 {result['data']['new_due_date']}。"
- 失败（`code == 400`）：把 `message` 原样透传给用户（如"该记录已归还，无法续借"）

## Acceptance Criteria
- 必须先查在借记录拿到 `record_id`，不可凭空构造
- 仅 `status == "borrowing"` 的记录可续借；已归还的记录后端会返回业务错误，需原样提示
- 返回给用户的"新应还日期"必须取自后端字段 `new_due_date`，字段名前后端保持一致
