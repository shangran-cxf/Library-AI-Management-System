# 架构设计

> 来源：`02-requirements.md`、`05-domain-model.md`、`constitution.md`

## 1. 架构风格

采用**分层架构** + **MVC 思想**，技术栈为 Python 3.10+ / FastAPI + SQLAlchemy + SQLite。
依赖方向只能由外向内：表现层 → 应用服务层 → 领域层，基础设施层实现领域层定义的接口。

## 2. 分层职责

### 2.1 表现层 Presentation / Controller

- 载体：FastAPI `APIRouter`（`routers/`）。
- 职责：接收 HTTP 请求、参数校验、调用应用服务、返回统一响应。
- **禁止**：不得编写业务规则，不得直接访问 Repository。

### 2.2 应用服务层 Application Service

- 载体：`services/`。
- 职责：组织用例流程、编排领域对象、管理事务边界、返回 DTO。
- 例如 `CirculationService.borrow()` 依次完成验证借阅证、检查规则、检查超期、创建 Loan。

### 2.3 领域层 Domain

- 载体：`domain/`（实体、值对象、策略）。
- 职责：承载核心业务规则与不变式。
- 内容：`Reader`、`BorrowCard`、`BookTitle`、`LibraryItem`、`Loan`、`Reservation`、
  `BorrowPolicy`（策略）、`FineRule`（策略）。

### 2.4 基础设施 / 持久化层 Infrastructure / Persistence

- 载体：`repositories/`、`database.py`。
- 职责：实现持久化（SQLAlchemy），提供 Repository 实现类。
- **注意**：Controller 不得直接依赖本层；本层实现领域层所需的接口。

### 2.5 测试层 Test

- 载体：`tests/`。
- 职责：pytest + httpx 完成单元测试与集成测试。

## 3. 模块划分

| 模块 | 职责 | 主要用例 |
|---|---|---|
| reader | 读者注册与账号 | UC-001 |
| card | 借阅证办理 / 删除 | UC-201、UC-202 |
| catalog | 图书标题与馆藏副本维护、查询 | UC-002、UC-205~208 |
| circulation | 借书、还书、查询借阅 | UC-101~103、UC-110 |
| reservation | 预约与排队 | UC-004 |
| fine | 罚款规则与记录 | UC-110 |
| admin | 管理员维护与规则维护 | UC-203~204、UC-209 |

## 4. 权限控制策略

- 通过请求携带的操作者身份（`reader_id` / `librarian_id` / `admin_id`）判断角色。
- 借书、还书：要求 Librarian 角色。
- 系统维护类（借阅证、管理员、图书、标题、规则）：要求 SystemAdmin 角色。
- 普通读者只能查询本人信息与发起预约。
- 越权请求统一返回业务错误。

## 5. 异常处理策略

| 异常类型 | 场景 | 处理 |
|---|---|---|
| ValidationError | 参数非法 | 返回 400 业务错误 |
| NotFoundError | 读者 / 图书 / 借阅记录不存在 | 返回 400/404 |
| BusinessRuleError | 借阅证无效、超数量、超期未还、图书不可借 | 返回 400，附明确原因 |
| PermissionDeniedError | 越权操作 | 返回 403 |
| 系统异常 | 未预期错误 | 事务回滚，返回 500 |

统一响应结构：`{ "code": 200/400/403/500, "message": "...", "data": {...} }`。

## 6. 事务边界

- 事务边界设在**应用服务层**方法级别。
- 一次借书 / 还书 / 预约 = 一个事务单元；失败即回滚（副本状态与借阅记录保持一致）。

## 7. 业务规则位置

| 规则 | 归属组件 |
|---|---|
| 最大借阅数量、借阅期限 | `BorrowPolicy`（领域策略） |
| 超期罚金费率 | `FineRule`（领域策略） |
| 借阅证有效性 | `BorrowCard.isValid()` |
| 预约排队 | `ReservationService` |

## 8. 使用的设计模式

| 模式 | 使用位置 |
|---|---|
| Strategy | `BorrowPolicy`、`FineRule`（不同读者/借出物类型可替换） |
| Factory | 创建不同类型 Reader / LibraryItem |
| Repository | 领域对象持久化 |
| Service Layer | 组织用例流程（application services） |
| DTO | 隔离表现层与领域层 |
| MVC | 分离路由、服务与领域模型 |

## 9. 推荐代码目录

```
Library-AI-Management-System/
  src/
    main.py            # 应用入口
    database.py        # 引擎 / 会话
    routers/           # 表现层（Controller）
    services/          # 应用服务层
    domain/            # 领域层（实体 + 策略）
    repositories/      # 持久化层
    schemas/           # DTO (Pydantic)
    exceptions/        # 自定义异常
  tests/               # 测试层
```

## 10. 命名与字段一致性规约

为满足"API 字段名与数据库、领域模型、Agent 提示词一致"的要求，统一约定：

| 载体 | 命名风格 | 示例 |
|---|---|---|
| 数据库列名（spec 13） | snake_case | `reader_id`、`card_no`、`borrow_date` |
| API / JSON 字段（spec 14，**权威**） | snake_case | `reader_id`、`book_id`、`code`、`due_date` |
| Agent 提示词 / 文档 | snake_case | 同上 |
| UML 类图属性（spec 05、06） | camelCase（类图惯例） | `readerId`、`cardNo`、`borrowDate` |

- 映射规则：**camelCase ↔ snake_case 一一对应**（`borrowDate` ↔ `borrow_date`），不省略、不起别名。
- **权威来源**：穿过 API 边界的字段名一律以 `14-api-spec.md`（实验二产出）为准，数据库列名与之保持一致。
- 禁止同一概念出现两种对外写法（如 `userId` 与 `user_id` 混用）。
