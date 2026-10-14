# 详细设计模型

> 来源：`02-requirements.md`、`03-use-cases.md`、`05-domain-model.md`、`07-architecture.md`、`13-database-design.md`。
> 本文件以用例为基本单元，说明每个用例由哪些设计类协作完成，并给出 DTO、Repository 接口、Service 方法签名与异常类型。

## 1. 设计类分层归属

| 层 | 设计类 | 载体目录 |
|---|---|---|
| 表现层 Controller | `ReaderController`、`CardController`、`CatalogController`、`CirculationController`、`ReservationController`、`AdminController` | `src/routers/` |
| 应用服务层 Service | `ReaderService`、`CardService`、`CatalogService`、`CirculationService`、`ReservationService`、`FineService`、`AdminService`、`PolicyService` | `src/services/` |
| 领域层 Domain | 实体 `Reader`/`BorrowCard`/`BookTitle`/`LibraryItem`/`Loan`/`Reservation`/`FineRecord`；策略 `BorrowPolicy`、`FineRule`；领域服务 `BorrowPolicyService`、`FineRuleService` | `src/domain/` |
| 持久化层 Repository | `ReaderRepository`、`BorrowCardRepository`、`LibrarianRepository`、`SystemAdminRepository`、`BookTitleRepository`、`LibraryItemRepository`、`LoanRepository`、`ReservationRepository`、`FineRecordRepository`、`BorrowPolicyRepository`、`FineRuleRepository` | `src/repositories/` |
| DTO | Pydantic 请求 / 响应模型 | `src/schemas/` |
| 异常 | 自定义异常层次 | `src/exceptions/` |

命名约定沿用 `07-architecture.md` §10：对外契约（API / DB）用 snake_case，领域类属性用 camelCase。

---

## 2. 通用设计组件

### 2.1 异常类型层次（`src/exceptions/`）

| 异常类 | 基类 | 对应 HTTP code | 触发场景 |
|---|---|---|---|
| `LibraryError` | Exception | — | 业务异常基类，携带 `code` / `message` |
| `ValidationParamError` | LibraryError | 400 | 参数非法 |
| `NotFoundError` | LibraryError | 404 | 读者 / 图书 / 借阅记录 / 标题不存在 |
| `BusinessRuleError` | LibraryError | 400 | 违反业务规则，附明确原因 |
| `CardInvalidError` | BusinessRuleError | 400 | 借阅证不存在或已失效 |
| `BorrowLimitExceededError` | BusinessRuleError | 400 | 超过最大借阅数量 |
| `OverdueBooksError` | BusinessRuleError | 400 | 存在超期未还图书 |
| `ItemNotAvailableError` | BusinessRuleError | 400 | 副本不存在或状态非 AVAILABLE |
| `DuplicateError` | BusinessRuleError | 400 | ISBN / barcode / 账号 / 重复预约冲突 |
| `PermissionDeniedError` | LibraryError | 403 | 越权操作 |

统一响应结构：`{ "code": 200/400/403/404/500, "message": "..." , "data": {...} }`（由全局异常处理器生成）。

### 2.2 Repository 接口（领域层定义的持久化契约）

> 接口只负责持久化，不含业务判断。

| 接口 | 关键方法签名 |
|---|---|
| `ReaderRepository` | `get_by_id(reader_id) -> Reader \| None`；`get_by_account(account) -> Reader \| None`；`save(reader) -> Reader`；`count_borrowing(reader_id) -> int` |
| `BorrowCardRepository` | `get_by_card_no(card_no) -> BorrowCard \| None`；`get_active_by_reader(reader_id) -> BorrowCard \| None`；`save(card) -> BorrowCard`；`next_card_serial(year: int) -> int` |
| `LibrarianRepository` | `get_by_id(librarian_id) -> Librarian \| None`；`save(librarian) -> Librarian`；`delete(librarian_id) -> None` |
| `SystemAdminRepository` | `get_by_id(admin_id) -> SystemAdmin \| None`；`save(admin) -> SystemAdmin`；`delete(admin_id) -> None` |
| `BookTitleRepository` | `get_by_id(title_id) -> BookTitle \| None`；`get_by_isbn(isbn) -> BookTitle \| None`；`save(title) -> BookTitle`；`search(keyword) -> list[BookTitle]`；`soft_delete(title_id) -> None` |
| `LibraryItemRepository` | `get_by_barcode(barcode) -> LibraryItem \| None`；`get_by_id(item_id) -> LibraryItem \| None`；`count_available(title_id) -> int`；`save(item) -> LibraryItem`；`delete(item_id) -> None` |
| `LoanRepository` | `get_active_by_item(item_id) -> Loan \| None`；`get_by_id(loan_id) -> Loan \| None`；`list_by_reader(reader_id) -> list[Loan]`；`has_overdue(reader_id) -> bool`；`save(loan) -> Loan` |
| `ReservationRepository` | `get_active(reader_id, title_id) -> Reservation \| None`；`list_queue(title_id) -> list[Reservation]`；`save(reservation) -> Reservation` |
| `FineRecordRepository` | `save(fine) -> FineRecord`；`list_by_reader(reader_id) -> list[FineRecord]` |
| `BorrowPolicyRepository` | `get_by_reader_type(reader_type) -> BorrowPolicy \| None`；`list_all() -> list[BorrowPolicy]`；`save(policy) -> BorrowPolicy` |
| `FineRuleRepository` | `get_by_item_type(item_type) -> FineRule \| None`；`list_all() -> list[FineRule]`；`save(rule) -> FineRule` |

### 2.3 领域服务

| 领域服务 | 职责 | 方法签名 |
|---|---|---|
| `BorrowPolicyService` | 封装 `BorrowPolicy` 策略，读取读者类型规则并判断可借 | `get_max_borrow_count(reader_type) -> int`；`get_borrow_days(reader_type) -> int`；`calc_due_date(reader_type, borrow_date) -> datetime`；`can_borrow(reader, current_count) -> bool` |
| `FineRuleService` | 封装 `FineRule` 策略，读取借出物费率并计算罚金 | `get_rate(item_type) -> Decimal`；`calculate(item_type, overdue_days) -> Decimal`；`overdue_days(due_date, return_date) -> int` |

### 2.4 主要 DTO（`src/schemas/`，字段 snake_case）

| DTO | 字段 | 用途 |
|---|---|---|
| `ReaderRegisterRequest` | `name`,`department`,`reader_type`,`account`,`password` | 注册请求 |
| `ReaderResponse` | `reader_id`,`name`,`department`,`reader_type`,`account` | 读者响应 |
| `IssueCardRequest` | `reader_id`,`expire_date` | 办理借阅证 |
| `BorrowCardResponse` | `card_id`,`card_no`,`reader_id`,`issue_date`,`expire_date`,`status` | 借阅证响应 |
| `BorrowRequest` | `card_no`,`barcode`,`librarian_id` | 借书请求 |
| `BorrowResponse` | `loan_id`,`reader_id`,`item_id`,`barcode`,`borrow_date`,`due_date`,`status` | 借书响应 |
| `ReturnRequest` | `barcode`,`librarian_id` | 还书请求 |
| `ReturnResponse` | `loan_id`,`return_date`,`overdue_days`,`fine_amount`,`fine_id` | 还书响应 |
| `ReservationRequest` | `reader_id`,`title_id` | 预约请求 |
| `ReservationResponse` | `reservation_id`,`reader_id`,`title_id`,`created_at`,`status`,`queue_position` | 预约响应 |
| `LoanQueryResponse` | `loan_id`,`item_id`,`title`,`borrow_date`,`due_date`,`return_date`,`status`,`is_overdue` | 借阅信息 |
| `BookTitleRequest` | `title`,`author`,`isbn`,`publisher`,`category`,`item_type` | 添加标题 |
| `LibraryItemRequest` | `title_id`,`barcode`,`location` | 添加副本 |
| `BorrowPolicyRequest` | `reader_type`,`max_borrow_count`,`borrow_days` | 维护借阅规则 |
| `FineRuleRequest` | `item_type`,`rate_per_day` | 维护罚款规则 |

---

## 3. 用例详细设计

### UC-101 办理借书

| 项 | 内容 |
|---|---|
| Controller 入口 | `CirculationController.borrow(borrow_req: BorrowRequest)` → `POST /api/circulation/borrow` |
| Application Service | `CirculationService.borrow(card_no, barcode, librarian_id) -> BorrowResponse` |
| Domain Service | `BorrowPolicyService.can_borrow()`、`BorrowPolicyService.calc_due_date()` |
| Entity / Aggregate | 聚合根 `Loan`；涉及 `BorrowCard`、`Reader`、`LibraryItem` |
| Repository | `LibrarianRepository`、`BorrowCardRepository`、`ReaderRepository`、`LoanRepository`、`LibraryItemRepository` |
| DTO | 入 `BorrowRequest`；出 `BorrowResponse` |
| 异常 | `PermissionDeniedError`（非图书管理员）、`CardInvalidError`、`BorrowLimitExceededError`、`OverdueBooksError`、`ItemNotAvailableError` |
| 事务边界 | `CirculationService.borrow()` 方法级：创建 `Loan` + 更新副本状态 + 计数，失败整体回滚 |

流程要点：①校验操作者为 Librarian；②按 `card_no` 取借阅证并 `isValid()`；③`ReaderRepository.count_borrowing` 与 `BorrowPolicyService.get_max_borrow_count` 比较；④`LoanRepository.has_overdue` 检查超期未还；⑤`get_by_barcode` 取副本并 `isAvailable()`；⑥创建 `Loan`，`due_date = borrow_date + get_borrow_days`；⑦副本 `markBorrowed()` 置 `BORROWED`。

### UC-102 办理还书

| 项 | 内容 |
|---|---|
| Controller 入口 | `CirculationController.return_book(return_req: ReturnRequest)` → `POST /api/circulation/return` |
| Application Service | `CirculationService.return_book(barcode, librarian_id) -> ReturnResponse` |
| Domain Service | `FineService.calculate_and_record(loan, return_date)`（内部用 `FineRuleService`） |
| Entity / Aggregate | `Loan`、`LibraryItem`、`FineRecord` |
| Repository | `LibrarianRepository`、`LibraryItemRepository`、`LoanRepository`、`FineRecordRepository` |
| DTO | 入 `ReturnRequest`；出 `ReturnResponse` |
| 异常 | `PermissionDeniedError`、`NotFoundError`（非本馆藏书 / 无未归还记录） |
| 事务边界 | `CirculationService.return_book()` 方法级：更新 `Loan` + 更新副本 + 生成 `FineRecord` 同一事务 |

流程要点：①校验 Librarian；②`get_by_barcode` 校验本馆藏书（否则 `NotFoundError`）；③`get_active_by_item` 取未归还 `Loan`（否则 `NotFoundError`）；④置 `return_date`、状态 `RETURNED`；⑤副本 `markAvailable()`；⑥`overdue_days > 0` 时调用 `FineService` 生成 `FineRecord`（否则罚金 0 不生成）。

### UC-110 计算超期罚款（`<<include>>`）

| 项 | 内容 |
|---|---|
| 触发者 | 由 `CirculationService.return_book()` 调用，无独立 Controller |
| Application Service | `FineService.calculate_and_record(loan: Loan, return_date: datetime) -> FineRecord \| None` |
| Domain Service | `FineRuleService.overdue_days()`、`FineRuleService.get_rate()`、`FineRuleService.calculate()` |
| Entity / Aggregate | `FineRecord`（聚合根）；读取 `Loan` |
| Repository | `FineRuleRepository`、`FineRecordRepository` |
| DTO | 出参合并进 `ReturnResponse`（`overdue_days`、`fine_amount`、`fine_id`） |
| 异常 | 无独立异常；费率缺失时按 `BusinessRuleError` 处理 |
| 事务边界 | 与 UC-102 同一事务 |

流程要点：①`overdue_days = return_date - due_date`；②`<= 0` 返回 `None`；③`get_rate(item_type)` 取费率；④`amount = overdue_days × rate`；⑤生成 `FineRecord`（`status = UNPAID`）。

### UC-004 预约图书

| 项 | 内容 |
|---|---|
| Controller 入口 | `ReservationController.create(req: ReservationRequest)` → `POST /api/reservations` |
| Application Service | `ReservationService.reserve(reader_id, title_id) -> ReservationResponse` |
| Domain Service | —（排队逻辑在 `ReservationService` 内，按 `created_at` 排序） |
| Entity / Aggregate | `Reservation`（聚合根）；涉及 `Reader`、`BookTitle` |
| Repository | `ReaderRepository`、`BookTitleRepository`、`ReservationRepository` |
| DTO | 入 `ReservationRequest`；出 `ReservationResponse` |
| 异常 | `NotFoundError`（读者 / 标题不存在）、`DuplicateError`（重复预约） |
| 事务边界 | `ReservationService.reserve()` 方法级 |

流程要点：①`ReaderRepository.get_by_id`；②`BookTitleRepository.get_by_id`；③`get_active(reader_id, title_id)` 判重复；④创建 `Reservation`（`created_at=now`, `status=ACTIVE`）；⑤`list_queue` 计算 `queue_position`。

### UC-103 / UC-003 查询借阅信息

| 项 | 内容 |
|---|---|
| Controller 入口 | `CirculationController.list_loans(...)` → `GET /api/readers/{reader_id}/loans` |
| Application Service | `CirculationService.query_loans(reader_id, operator_type, operator_id) -> list[LoanQueryResponse]` |
| Domain Service | — |
| Entity / Aggregate | `Loan`（只读） |
| Repository | `ReaderRepository`、`LoanRepository`、`LibraryItemRepository`、`BookTitleRepository` |
| DTO | 出 `LoanQueryResponse` |
| 异常 | `NotFoundError`（读者不存在）、`PermissionDeniedError`（读者查询他人） |
| 事务边界 | 只读，无事务 |

规则：读者只能查本人；图书管理员可查任意读者。返回当前借阅、历史借阅与超期状态。

### UC-201 办理借阅证

| 项 | 内容 |
|---|---|
| Controller 入口 | `CardController.issue(req: IssueCardRequest, admin_id)` → `POST /api/admin/borrow-cards` |
| Application Service | `CardService.issue(reader_id, expire_date, admin_id) -> BorrowCardResponse` |
| Domain Service | — |
| Entity / Aggregate | `BorrowCard`（聚合根）；涉及 `Reader` |
| Repository | `SystemAdminRepository`、`ReaderRepository`、`BorrowCardRepository` |
| DTO | 入 `IssueCardRequest`；出 `BorrowCardResponse` |
| 异常 | `PermissionDeniedError`（非系统管理员）、`NotFoundError`（读者不存在）、`DuplicateError`（已有有效证） |
| 事务边界 | `CardService.issue()` 方法级 |

流程要点：①校验 SystemAdmin；②`ReaderRepository.get_by_id`；③`get_active_by_reader` 判已有证；④`card_no = f"CARD{year}{serial:06d}"`（`next_card_serial`）；⑤保存。

### UC-205 添加图书标题信息

| 项 | 内容 |
|---|---|
| Controller 入口 | `CatalogController.add_title(req: BookTitleRequest, admin_id)` → `POST /api/admin/book-titles` |
| Application Service | `CatalogService.add_title(req, admin_id) -> BookTitleResponse` |
| Domain Service | — |
| Entity / Aggregate | `BookTitle`（聚合根） |
| Repository | `SystemAdminRepository`、`BookTitleRepository` |
| DTO | 入 `BookTitleRequest`；出 `BookTitleResponse`（`title_id` 等） |
| 异常 | `PermissionDeniedError`、`DuplicateError`（ISBN 重复） |
| 事务边界 | `CatalogService.add_title()` 方法级 |

### UC-207 添加馆藏副本

| 项 | 内容 |
|---|---|
| Controller 入口 | `CatalogController.add_item(req: LibraryItemRequest, admin_id)` → `POST /api/admin/library-items` |
| Application Service | `CatalogService.add_item(req, admin_id) -> LibraryItemResponse` |
| Domain Service | — |
| Entity / Aggregate | `LibraryItem` 子类（`Book`/`Magazine`/`Thesis`，由 `item_type` 判别）；涉及 `BookTitle` |
| Repository | `SystemAdminRepository`、`BookTitleRepository`、`LibraryItemRepository` |
| DTO | 入 `LibraryItemRequest`；出 `LibraryItemResponse` |
| 异常 | `PermissionDeniedError`、`NotFoundError`（标题不存在）、`DuplicateError`（barcode 重复） |
| 事务边界 | `CatalogService.add_item()` 方法级 |

规则：副本默认 `status = AVAILABLE`，`item_type` 继承标题。

### UC-209 维护借阅规则和罚款规则

| 项 | 内容 |
|---|---|
| Controller 入口 | `AdminController.upsert_policy/upsert_fine_rule(...)` → `PUT /api/admin/borrow-policies`、`PUT /api/admin/fine-rules` |
| Application Service | `PolicyService.upsert_borrow_policy(req, admin_id)`、`PolicyService.upsert_fine_rule(req, admin_id)` |
| Domain Service | `BorrowPolicyService` / `FineRuleService`（读取最新规则） |
| Entity / Aggregate | `BorrowPolicy`、`FineRule` |
| Repository | `SystemAdminRepository`、`BorrowPolicyRepository`、`FineRuleRepository` |
| DTO | `BorrowPolicyRequest`、`FineRuleRequest` |
| 异常 | `PermissionDeniedError`、`ValidationParamError` |
| 事务边界 | 各 upsert 方法级 |

---

## 4. 设计模式使用位置

| 模式 | 使用位置 | 说明 |
|---|---|---|
| Strategy | `BorrowPolicy`、`FineRule`（领域策略）+ `BorrowPolicyService`/`FineRuleService` | 不同读者类型 / 借出物类型规则可替换，规则集中不散落 |
| Factory | `LibraryItemFactory.create(item_type, ...)`、`ReaderFactory.create(reader_type, ...)` | 按判别字段创建具体子类 |
| Repository | `src/repositories/*` | 隔离持久化，Controller 不直接依赖 |
| Service Layer | `src/services/*` | 组织用例流程、管理事务边界、返回 DTO |
| DTO | `src/schemas/*` | 隔离表现层与领域层 |
| MVC | `routers/` + `services/` + `domain/` | 分离路由、服务与领域模型 |
| Dependency Injection | `deps.py`（FastAPI `Depends`） | 注入 Session 与各 Repository / Service |

---

## 5. 事务边界与一致性

- 事务边界统一设在**应用服务层公有方法**上，一次用例 = 一个事务单元。
- 借书：`Loan` 创建与 `LibraryItem` 状态更新必须同时成功，否则回滚。
- 还书：`Loan` 状态更新、`LibraryItem` 状态恢复、`FineRecord` 生成同一事务。
- 预约：创建 `Reservation` 与计算 `queue_position` 同一事务。
- 只读查询（查询借阅信息、查询图书）不开启写事务。

## 6. 与数据库设计的一致性

- Repository 方法直接映射 `13-database-design.md` 的表与外键约束。
- 继承采用单表 + 判别字段：`readers.reader_type`、`library_items.item_type`。
- 唯一约束（`card_no`、`isbn`、`barcode`、`account`）在 Repository 层前置校验 + 数据库唯一索引双重保障。
