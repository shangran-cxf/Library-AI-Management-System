# API 接口规范

> 来源：`02-requirements.md`、`03-use-cases.md`、`09-design-model.md`、`13-database-design.md`。
> 采用 REST API（Python FastAPI）。**本文件是 API 边界字段名的权威来源**，所有字段一律 snake_case，数据库列名与之一致。

## 1. 通用约定

- 基础路径：`/api`
- 请求 / 响应体：`application/json; charset=utf-8`
- 统一响应结构：

```json
{ "code": 200, "message": "success", "data": {} }
```

- `code` 取值：`200` 成功；`400` 业务错误；`403` 权限不足；`404` 资源不存在；`500` 系统错误。
- 权限通过请求体中的操作者标识字段传递：`reader_id`、`librarian_id`、`admin_id`。

### 1.1 权威字段名表（snake_case）

| 概念 | API / DB 字段名 | UML 属性名 |
|---|---|---|
| 读者 ID | `reader_id` | `readerId` |
| 读者类型 | `reader_type` | `readerType` |
| 借阅证号 | `card_no` | `cardNo` |
| 借阅证 ID | `card_id` | `cardId` |
| 办理日期 | `issue_date` | `issueDate` |
| 有效期 | `expire_date` | `expireDate` |
| 图书管理员 ID | `librarian_id` | `librarianId` |
| 系统管理员 ID | `admin_id` | `adminId` |
| 标题 ID | `title_id` | `titleId` |
| 馆藏副本 ID | `item_id` | `itemId` |
| 馆藏条码 | `barcode` | `barcode` |
| 借出物类型 | `item_type` | `itemType` |
| 借阅记录 ID | `loan_id` | `loanId` |
| 借出日期 | `borrow_date` | `borrowDate` |
| 应还日期 | `due_date` | `dueDate` |
| 归还日期 | `return_date` | `returnDate` |
| 是否超期 | `is_overdue` | `isOverdue` |
| 预约 ID | `reservation_id` | `reservationId` |
| 预约创建时间 | `created_at` | `createdAt` |
| 排队序号 | `queue_position` | `queuePosition` |
| 罚款 ID | `fine_id` | `fineId` |
| 罚款金额 | `amount` | `amount` |
| 超期天数 | `overdue_days` | `overdueDays` |
| 超期费率 | `rate_per_day` | `ratePerDay` |
| 最大借阅数量 | `max_borrow_count` | `maxBorrowCount` |
| 借阅期限 | `borrow_days` | `borrowDays` |

---

## 2. 接口清单

| 编号 | 方法 | 路径 | 用例 | 权限 |
|---|---|---|---|---|
| API-01 | POST | `/api/readers` | UC-001 注册账号 | 公开 |
| API-02 | GET | `/api/books` | UC-002 查询图书 | 公开 |
| API-03 | POST | `/api/admin/borrow-cards` | UC-201 办理借阅证 | SystemAdmin |
| API-04 | DELETE | `/api/admin/borrow-cards/{card_no}` | UC-202 删除借阅证 | SystemAdmin |
| API-05 | POST | `/api/admin/librarians` | UC-203 添加图书管理员 | SystemAdmin |
| API-06 | DELETE | `/api/admin/librarians/{librarian_id}` | UC-204 删除图书管理员 | SystemAdmin |
| API-07 | POST | `/api/admin/book-titles` | UC-205 添加图书标题 | SystemAdmin |
| API-08 | DELETE | `/api/admin/book-titles/{title_id}` | UC-206 删除图书标题 | SystemAdmin |
| API-09 | POST | `/api/admin/library-items` | UC-207 添加馆藏副本 | SystemAdmin |
| API-10 | DELETE | `/api/admin/library-items/{item_id}` | UC-208 删除馆藏副本 | SystemAdmin |
| API-11 | PUT | `/api/admin/borrow-policies` | UC-209 维护借阅规则 | SystemAdmin |
| API-12 | PUT | `/api/admin/fine-rules` | UC-209 维护罚款规则 | SystemAdmin |
| API-13 | POST | `/api/circulation/borrow` | UC-101 办理借书 | Librarian |
| API-14 | POST | `/api/circulation/return` | UC-102 办理还书 | Librarian |
| API-15 | GET | `/api/readers/{reader_id}/loans` | UC-003/103 查询借阅信息 | 本人 / Librarian |
| API-16 | POST | `/api/reservations` | UC-004 预约图书 | 读者 |

---

## 3. 接口详细定义

### API-01 注册读者

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/readers` |
| 请求参数 | `name`,`department`,`reader_type`,`account`,`password` |
| 响应结果 | `code=200`，`data`: `{reader_id, name, department, reader_type, account}` |
| 权限要求 | 公开 |
| 成功场景 | 账号唯一，创建读者成功，返回 `reader_id` |
| 失败场景 | 账号重复 → `code=400 "账号已存在"`；`reader_type` 非法 → `400` |

对应服务：`ReaderService.register(req) -> ReaderResponse`。

### API-02 查询图书

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `GET /api/books?keyword=&category=` |
| 请求参数 | 查询串 `keyword`（题名 / 作者 / ISBN）、`category` |
| 响应结果 | `data`: `[{title_id, title, author, isbn, publisher, category, item_type, available_count}]` |
| 权限要求 | 公开 |
| 成功场景 | 返回匹配标题及在馆可借数量 |
| 失败场景 | 无匹配返回空列表（非错误） |

对应服务：`CatalogService.search(keyword, category) -> list[BookTitleResponse]`。

### API-03 办理借阅证

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/admin/borrow-cards` |
| 请求参数 | `reader_id`,`expire_date`,`admin_id` |
| 响应结果 | `data`: `{card_id, card_no, reader_id, issue_date, expire_date, status}` |
| 权限要求 | SystemAdmin |
| 成功场景 | 生成唯一 `card_no`（`CARD+年份+6位序号`） |
| 失败场景 | 非管理员 → `403`；读者不存在 → `404`；已有有效证 → `400 "该读者已有借阅证"` |

对应服务：`CardService.issue(reader_id, expire_date, admin_id) -> BorrowCardResponse`。

### API-04 删除借阅证

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `DELETE /api/admin/borrow-cards/{card_no}` |
| 请求参数 | `admin_id`（查询串或请求体） |
| 响应结果 | `code=200`，`message="已失效"` |
| 权限要求 | SystemAdmin |
| 成功场景 | 借阅证置为 `INACTIVE` |
| 失败场景 | 非管理员 → `403`；不存在 → `404` |

### API-05 添加图书管理员 / API-06 删除图书管理员

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/admin/librarians`；`DELETE /api/admin/librarians/{librarian_id}` |
| 请求参数 | 添加：`name`,`account`,`password`,`admin_id` |
| 响应结果 | `data`: `{librarian_id, name, account}` |
| 权限要求 | SystemAdmin |
| 成功场景 | 创建 / 删除成功 |
| 失败场景 | 非管理员 → `403`；删除不存在 → `404` |

### API-07 添加图书标题

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/admin/book-titles` |
| 请求参数 | `title`,`author`,`isbn`,`publisher`,`category`,`item_type`,`admin_id` |
| 响应结果 | `data`: `{title_id, title, author, isbn, item_type}` |
| 权限要求 | SystemAdmin |
| 成功场景 | 创建成功，返回 `title_id` |
| 失败场景 | 非管理员 → `403`；ISBN 重复 → `400 "ISBN 重复"` |

对应服务：`CatalogService.add_title(req, admin_id) -> BookTitleResponse`。

### API-08 删除图书标题

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `DELETE /api/admin/book-titles/{title_id}` |
| 请求参数 | `admin_id` |
| 响应结果 | `code=200` |
| 权限要求 | SystemAdmin |
| 成功场景 | 无未归还副本 / 有效预约时逻辑删除 |
| 失败场景 | 存在未归还副本或有效预约 → `400`；不存在 → `404` |

### API-09 添加馆藏副本

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/admin/library-items` |
| 请求参数 | `title_id`,`barcode`,`location`,`admin_id` |
| 响应结果 | `data`: `{item_id, barcode, title_id, item_type, status, location}` |
| 权限要求 | SystemAdmin |
| 成功场景 | 条码唯一，默认 `status=AVAILABLE` |
| 失败场景 | 非管理员 → `403`；标题不存在 → `404`；条码重复 → `400 "条码重复"` |

对应服务：`CatalogService.add_item(req, admin_id) -> LibraryItemResponse`。

### API-10 删除馆藏副本

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `DELETE /api/admin/library-items/{item_id}` |
| 请求参数 | `admin_id` |
| 响应结果 | `code=200` |
| 权限要求 | SystemAdmin |
| 成功场景 | 状态为 AVAILABLE 时可删除 |
| 失败场景 | 借出 / 预约中 → `400 "副本不可删除"`；不存在 → `404` |

### API-11 维护借阅规则

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `PUT /api/admin/borrow-policies` |
| 请求参数 | `reader_type`,`max_borrow_count`,`borrow_days`,`admin_id` |
| 响应结果 | `data`: `{reader_type, max_borrow_count, borrow_days}` |
| 权限要求 | SystemAdmin |
| 成功场景 | 新增或更新规则 |
| 失败场景 | 非管理员 → `403`；数值非法 → `400` |

### API-12 维护罚款规则

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `PUT /api/admin/fine-rules` |
| 请求参数 | `item_type`,`rate_per_day`,`admin_id` |
| 响应结果 | `data`: `{item_type, rate_per_day}` |
| 权限要求 | SystemAdmin |
| 成功场景 | 新增或更新费率 |
| 失败场景 | 非管理员 → `403`；费率非法 → `400` |

### API-13 办理借书

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/circulation/borrow` |
| 请求参数 | `card_no`,`barcode`,`librarian_id` |
| 响应结果 | `data`: `{loan_id, reader_id, item_id, barcode, borrow_date, due_date, status}` |
| 权限要求 | Librarian |
| 成功场景 | 生成 `Loan`，副本置 `BORROWED`，`due_date` 按读者类型计算 |
| 失败场景 | 非图书管理员 → `403`；借阅证无效 → `400 "借阅证无效"`；超过数量 → `400 "借阅已满"`；超期未还 → `400 "请先归还超期图书"`；图书不可借 → `400 "图书不可借"` |

对应服务：`CirculationService.borrow(card_no, barcode, librarian_id) -> BorrowResponse`。

### API-14 办理还书

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/circulation/return` |
| 请求参数 | `barcode`,`librarian_id` |
| 响应结果 | `data`: `{loan_id, return_date, overdue_days, fine_amount, fine_id}` |
| 权限要求 | Librarian |
| 成功场景 | `Loan` 置 `RETURNED`，副本恢复 `AVAILABLE`，超期生成 `FineRecord` |
| 失败场景 | 非图书管理员 → `403`；非本馆藏书 → `400 "非本馆藏书"`；未找到借阅记录 → `400 "未找到借阅记录"` |

对应服务：`CirculationService.return_book(barcode, librarian_id) -> ReturnResponse`。

### API-15 查询借阅信息

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `GET /api/readers/{reader_id}/loans?operator_type=&operator_id=` |
| 请求参数 | 路径 `reader_id`；查询串 `operator_type`(reader/librarian)、`operator_id` |
| 响应结果 | `data`: `[{loan_id, item_id, title, borrow_date, due_date, return_date, status, is_overdue}]` |
| 权限要求 | 读者本人或 Librarian |
| 成功场景 | 返回当前 / 历史借阅与超期状态 |
| 失败场景 | 读者查询他人 → `403`；读者不存在 → `404` |

对应服务：`CirculationService.query_loans(reader_id, operator_type, operator_id) -> list[LoanQueryResponse]`。

### API-16 预约图书

| 项 | 内容 |
|---|---|
| 方法 / 路径 | `POST /api/reservations` |
| 请求参数 | `reader_id`,`title_id` |
| 响应结果 | `data`: `{reservation_id, reader_id, title_id, created_at, status, queue_position}` |
| 权限要求 | 读者 |
| 成功场景 | 生成 `Reservation`（`ACTIVE`），返回排队序号 |
| 失败场景 | 读者不存在 → `404`；标题不存在 → `404`；重复预约 → `400 "您已预约过该书"` |

对应服务：`ReservationService.reserve(reader_id, title_id) -> ReservationResponse`。

---

## 4. 错误响应示例

```json
{ "code": 400, "message": "借阅已满", "data": null }
{ "code": 403, "message": "无权限执行该操作", "data": null }
{ "code": 404, "message": "未找到借阅记录", "data": null }
```
