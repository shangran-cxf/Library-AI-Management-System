# 实现任务拆解

> 来源：全部 specs（`constitution.md`、`02`、`03`、`05`、`07`、`09`、`13`、`14`、`15`）。
> 每个任务粒度适合编码 Agent 一次完成。**实现阶段严禁修改任何 specs 文件**（baseline 已冻结）；若发现规格问题，须先提出并请求人工确认。

## 通用约束

- 技术栈：Python 3.10+ / FastAPI + SQLAlchemy + SQLite + Pydantic；测试 pytest + httpx。
- 目录结构见 `07-architecture.md` §9。
- 允许修改范围：仅 `src/`、`tests/`、`README.md`（TASK-013 后）。
- 不允许修改：`specs/` 下任何文件。
- 每个任务完成后必须运行 `pytest`（至少运行本任务相关测试），并提交一次 Git commit。

---

## TASK-001 初始化项目结构

| 项 | 内容 |
|---|---|
| 任务目标 | 搭建分层目录骨架与应用入口 |
| 输入规格 | `07-architecture.md` §9、`constitution.md` §5/§12 |
| 允许修改文件 | `src/main.py`、`src/database.py`、`src/__init__.py`、`src/{routers,services,domain,repositories,schemas,exceptions}/__init__.py`、`tests/__init__.py`、`tests/conftest.py`、`requirements.txt` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | 建立 `main.py`（FastAPI 应用 + 统一响应与全局异常处理注册）、`database.py`（引擎 / Session / `Base`）；各层空包；不实现业务逻辑 |
| 验收标准 | `uvicorn src.main:app` 可启动；`pytest` 可运行（0 用例通过） |
| 建议测试 | 冒烟测试：`GET /` 或 `/health` 返回 `{code:200}` |

## TASK-002 实现领域实体与枚举

| 项 | 内容 |
|---|---|
| 任务目标 | 实现领域实体、值对象与枚举 |
| 输入规格 | `05-domain-model.md`、`13-database-design.md` |
| 允许修改文件 | `src/domain/models.py`、`src/domain/enums.py`、`src/domain/policies.py` |
| 不允许修改文件 | `specs/*`、`src/routers/*` |
| 实现要求 | SQLAlchemy 模型：`Reader`（含子类型判别）、`BorrowCard`、`Librarian`、`SystemAdmin`、`BookTitle`、`LibraryItem`（`Book`/`Magazine`/`Thesis` 判别）、`Loan`、`Reservation`、`FineRecord`、`BorrowPolicy`、`FineRule`；枚举 `ReaderType`、`ItemType`、`LoanStatus`、`ReservationStatus`、`CardStatus`、`FineStatus`；实体行为 `isValid()`、`isAvailable()`、`markBorrowed()`、`markAvailable()`、`overdueDays()` 等 |
| 验收标准 | 11 张表可按 `13` 建表；唯一约束（`card_no`/`isbn`/`barcode`/`account`）存在 |
| 建议测试 | 建表 + 唯一约束单元测试 |

## TASK-003 实现 Repository 层

| 项 | 内容 |
|---|---|
| 任务目标 | 实现各 Repository，封装持久化 |
| 输入规格 | `09-design-model.md` §2.2、`13-database-design.md` |
| 允许修改文件 | `src/repositories/*.py` |
| 不允许修改文件 | `specs/*`、`src/services/*` |
| 实现要求 | 按 §2.2 方法签名实现 11 个 Repository；只做持久化，不含业务判断 |
| 验收标准 | 各方法可正确读写；无业务规则混入 |
| 建议测试 | Repository CRUD 单元测试 |

## TASK-004 实现借阅规则策略

| 项 | 内容 |
|---|---|
| 任务目标 | 实现 `BorrowPolicyService`（Strategy） |
| 输入规格 | `09-design-model.md` §2.3、`02-requirements.md` BR-003/BR-004 |
| 允许修改文件 | `src/domain/policies.py`、`src/services/policy_service.py` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | `get_max_borrow_count`、`get_borrow_days`、`calc_due_date`、`can_borrow`；支持全部 5 类读者类型；规则从 `borrow_policies` 读取 |
| 验收标准 | 专科3/本科5/研究生10/博士15/教师20；30/30/60/90/90 |
| 建议测试 | TC-027（单元） |

## TASK-005 实现罚款规则策略

| 项 | 内容 |
|---|---|
| 任务目标 | 实现 `FineRuleService`（Strategy） |
| 输入规格 | `09-design-model.md` §2.3、`02-requirements.md` BR-007 |
| 允许修改文件 | `src/domain/policies.py`、`src/services/fine_service.py` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | `get_rate`、`calculate`、`overdue_days`；支持 5 类借出物；`overdue_days<=0` 罚款为 0 |
| 验收标准 | 中文图书0.1/外文图书0.2/中文杂志0.1/外文杂志0.2/论文0.5 |
| 建议测试 | TC-028（单元） |

## TASK-006 实现读者与借阅证管理

| 项 | 内容 |
|---|---|
| 任务目标 | 实现 `ReaderService`、`CardService` 及对应路由 |
| 输入规格 | `03-use-cases.md` UC-001/201/202、`14-api-spec.md` API-01/03/04 |
| 允许修改文件 | `src/services/reader_service.py`、`src/services/card_service.py`、`src/routers/reader_router.py`、`src/routers/card_router.py`、`src/schemas/*` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | 注册（账号唯一）；办理借阅证（SystemAdmin 权限、读者存在、一读者一证、`card_no` 唯一）；删除借阅证（置 INACTIVE） |
| 验收标准 | 见 `14-api-spec.md` 对应成功 / 失败场景 |
| 建议测试 | TC-001 ~ TC-005 |

## TASK-007 实现图书标题与馆藏管理

| 项 | 内容 |
|---|---|
| 任务目标 | 实现 `CatalogService` 及对应路由 |
| 输入规格 | `03-use-cases.md` UC-002/205~208、`14-api-spec.md` API-02/07~10 |
| 允许修改文件 | `src/services/catalog_service.py`、`src/routers/catalog_router.py`、`src/schemas/*` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | 查询图书（返回可借数量）；添加标题（ISBN 唯一）；删除标题（无未归还副本/预约时逻辑删除）；添加副本（barcode 唯一、默认 AVAILABLE）；删除副本（AVAILABLE 才可删） |
| 验收标准 | 见 `14-api-spec.md` API-07~10 |
| 建议测试 | TC-021 ~ TC-024 |

## TASK-008 实现办理借书

| 项 | 内容 |
|---|---|
| 任务目标 | 实现 `CirculationService.borrow` 与路由 |
| 输入规格 | `03-use-cases.md` UC-101、`10-sequence-borrow-book.puml`、`09-design-model.md` §3 |
| 允许修改文件 | `src/services/circulation_service.py`、`src/routers/circulation_router.py`、`src/schemas/*` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | Librarian 权限；验证借阅证有效；`BorrowPolicyService` 检查数量；检查超期未还；验证副本可借；创建 `Loan`、`due_date`；副本置 `BORROWED`；事务原子性 |
| 验收标准 | 见 `14-api-spec.md` API-13 |
| 建议测试 | TC-006 ~ TC-010 |

## TASK-009 实现办理还书

| 项 | 内容 |
|---|---|
| 任务目标 | 实现 `CirculationService.return_book`、`FineService` 与路由 |
| 输入规格 | `03-use-cases.md` UC-102/110、`11-sequence-return-book.puml`、`09-design-model.md` §3 |
| 允许修改文件 | `src/services/circulation_service.py`、`src/services/fine_service.py`、`src/routers/circulation_router.py`、`src/schemas/*` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | Librarian 权限；验证本馆藏书；查找未归还 `Loan`；置 `RETURNED`；副本恢复 `AVAILABLE`；超期调用 `FineService` 生成 `FineRecord` |
| 验收标准 | 见 `14-api-spec.md` API-14 |
| 建议测试 | TC-011 ~ TC-014 |

## TASK-010 实现预约图书

| 项 | 内容 |
|---|---|
| 任务目标 | 实现 `ReservationService` 与路由 |
| 输入规格 | `03-use-cases.md` UC-004、`12-sequence-reserve-book.puml`、`09-design-model.md` §3 |
| 允许修改文件 | `src/services/reservation_service.py`、`src/routers/reservation_router.py`、`src/schemas/*` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | 读者存在；标题存在；禁止重复预约同一标题有效预约；按 `created_at` 排队计算 `queue_position` |
| 验收标准 | 见 `14-api-spec.md` API-16 |
| 建议测试 | TC-018 ~ TC-020 |

## TASK-011 实现借阅信息查询

| 项 | 内容 |
|---|---|
| 任务目标 | 实现查询借阅信息 |
| 输入规格 | `03-use-cases.md` UC-003/103、`14-api-spec.md` API-15 |
| 允许修改文件 | `src/services/circulation_service.py`、`src/routers/circulation_router.py`、`src/schemas/*` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | 读者只能查本人；图书管理员可查任意读者；返回当前 / 历史借阅与超期状态 |
| 验收标准 | 见 `14-api-spec.md` API-15 |
| 建议测试 | TC-015 ~ TC-017 |

## TASK-012 实现管理员维护与权限

| 项 | 内容 |
|---|---|
| 任务目标 | 实现管理员 / 规则维护与统一权限校验 |
| 输入规格 | `03-use-cases.md` UC-203/204/209、`14-api-spec.md` API-05/06/11/12 |
| 允许修改文件 | `src/services/admin_service.py`、`src/services/policy_service.py`、`src/routers/admin_router.py`、`src/exceptions/*`、`src/deps.py` |
| 不允许修改文件 | `specs/*` |
| 实现要求 | 添加 / 删除图书管理员；维护借阅规则与罚款规则；统一 `PermissionDeniedError` 处理（403）；异常处理器输出统一响应 |
| 验收标准 | 普通读者调用管理接口返回 `403`；规则更新后新借阅 / 罚款按新规则 |
| 建议测试 | TC-025、TC-026 |

## TASK-013 完善测试与文档

| 项 | 内容 |
|---|---|
| 任务目标 | 补齐测试覆盖并生成 README |
| 输入规格 | `15-test-plan.md`、`README` 要求 |
| 允许修改文件 | `tests/*`、`README.md` |
| 不允许修改文件 | `specs/*`、`src/`（如需修改须先说明理由） |
| 实现要求 | 对照 `15-test-plan.md` 检查覆盖，补全未覆盖用例；生成 README（项目简介、技术栈、架构、目录、启动、测试、核心用例、核心 API、UML 说明、Agent 使用说明） |
| 验收标准 | `pytest` 全绿；README 与实际功能一致，不编造 |
| 建议测试 | 全量 `pytest -v` |

---

## 任务依赖与顺序

```
TASK-001 → TASK-002 → TASK-003 → {TASK-004, TASK-005}
                                   ↓
              TASK-006 → TASK-007 → TASK-008 → TASK-009 → TASK-010 → TASK-011 → TASK-012 → TASK-013
```

- TASK-004 与 TASK-005 可并行。
- TASK-008 依赖 TASK-004；TASK-009 依赖 TASK-005。
- 每完成一个任务提交一次，commit message 使用 `complete TASK-00X <描述>`。
