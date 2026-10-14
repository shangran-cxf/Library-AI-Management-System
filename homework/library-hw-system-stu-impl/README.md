# 图书管理系统 · 学生扩展任务实现说明

> 本目录基于基础版代码 `library-hw-system-stu` 复制而来，在其上完成了**任务一：续借**与**任务二：图书评论与评分**两个扩展功能。
> 本目录仅包含我方的实现，未改动原始基础版代码。

## 一、改动清单

| 层 | 文件 | 改动 |
|---|---|---|
| 数据模型 | `backend/app/models.py` | 新增 `Review` 评论表；为 `User` / `Book` 增加 `reviews` 关联 |
| 接口 | `backend/app/routes.py` | 新增续借端点、评论发表/查询端点；新增 `RenewRequest` / `ReviewRequest` DTO |
| 流通执行者 | `.codebuddy/agents/circulation-agent/SKILL.md` | 补充"续借"职责、API 映射行、调用流程、错误处理 |
| 主编排 | `.codebuddy/agents/orchestrator-agent/SKILL.md` | trigger 与路由规则加入"续借""评论/评分"意图 |
| 参考技能 | `.codebuddy/skills/renew-book/SKILL.md` | 新增：续借接口契约说明书 |
| 参考技能 | `.codebuddy/skills/book-review/SKILL.md` | 新增：评论接口契约说明书 |
| 测试 | `backend/tests/` | 新增 pytest 测试（续借 + 评论），并附 curl 实测脚本 |

## 二、任务一：续借

### 接口

| 方法 | 路径 | 请求体 | 返回 |
|---|---|---|---|
| POST | `/api/renew` | `{record_id, extend_days}`（`extend_days` 可选，默认 30） | `{record_id, book_title, old_due_date, new_due_date, extend_days}` |

### 业务规则
- 仅 `status == "borrowing"`（在借）的记录可续借；已归还的记录返回 `code=400 "该记录已归还，无法续借"`。
- 记录不存在返回 `code=400 "借阅记录不存在"`。
- 延长天数必须为正整数，否则返回 `code=400`。
- 新应还日期字段统一命名为 **`new_due_date`**（后端返回 = Agent 提示词引用，保持一致）。

### 挂接位置（架构分工）
续借属**流通业务**，由 `orchestrator-agent` 委派 `circulation-agent` 执行：先查在借记录拿到 `record_id`，再调 `/api/renew`。参数细节参考 `.codebuddy/skills/renew-book/SKILL.md`。

## 三、任务二：图书评论与评分

### 数据模型
`reviews` 表：`id` / `book_id` / `user_id` / `rating`(1-5) / `comment` / `created_at`。

### 接口

| 方法 | 路径 | 请求体 / 参数 | 返回 |
|---|---|---|---|
| POST | `/api/books/{book_id}/reviews` | `{user_id, rating, comment}` | `{review_id, book_id, book_title, user_id, username, rating, comment, created_at}` |
| GET | `/api/books/{book_id}/reviews` | 路径参数 | `{book_id, book_title, average_rating, total, reviews[]}` |

### 业务规则
- 评分必须在 1-5 之间，越界返回 `code=400 "评分必须在 1-5 之间"`（后端拒绝）。
- 图书 / 用户不存在分别返回业务错误。
- 平均评分由后端计算，字段名为 **`average_rating`**，保留 1 位小数；无评论时为 `0`。

### 挂接位置（架构分工）
评论属**图书内容操作**，与"找书"性质相近，由 `orchestrator-agent` 直接 `use_skill("book-review")` 调用，**不**交给 `circulation-agent`。

## 四、运行与验证

```powershell
cd backend
python main.py          # 启动服务，监听 http://localhost:8001
python -m pytest -q     # 运行自动化测试
```

- 自动化测试：`backend/tests/`（`test_renew.py`、`test_review.py`），共 15 项，全部通过。
- 接口 curl 实测：见 [接口测试记录.md](接口测试记录.md)，由 `backend/tests/run_curl_tests.ps1` 实际调用生成。

### pytest 结果

```
15 passed
```

## 五、对话演示（按 Agent 提示词推演，接口返回为真实结果）

> 说明：以下为按本项目 Agent/Skill 提示词路由规则推演的对话流程，括号内标注的 API 调用与返回均来自上方真实 curl 实测记录。

### 演示一：续借
```
用户：把我借的《三体》续借一下
编排：识别为"续借"意图 → 委派 circulation-agent
circulation-agent：
  1) GET /api/borrow/records/1?status=borrowing  → 命中 record_id=1（《三体》）
  2) POST /api/renew {record_id:1}               → new_due_date = 2026-08-19
回复：续借成功！新的应还日期为 2026-08-19。
```

### 演示二：写评论
```
用户：给《三体》打 5 分，写句评论：太好看了
编排：识别为"评论评分"意图 → use_skill("book-review")
book-review：
  1) GET /api/books/search?keyword=三体           → book_id=1
  2) POST /api/books/1/reviews {user_id:1,rating:5,comment:"太好看了"}
回复：已成功为《三体》评分 5 分并保存评论。
```

### 演示三：查看评论
```
用户：看看《三体》的评论
编排：识别为"查看评论"意图 → use_skill("book-review")
book-review：GET /api/books/1/reviews → average_rating=4.5, total=2
回复：《三体》平均评分：4.5（共 2 条评论）
     - zhangsan：5 分 — 太好看了
     - lisi：4 分 — 不错，值得一读
```
