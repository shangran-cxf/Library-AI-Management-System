# AI 使用记录

> 每次使用 Agent 生成 specs、UML、代码或测试，都在此登记。

---

## 第 1 次使用

### 使用工具

Trae（AI 编码 Agent）

### 使用阶段

实验一 · 架构设计与 Spec 建模

### 使用任务

根据《软件设计与体系结构》实验资源与指导书，生成实验一全套 Specs：
项目简报、澄清问题、开发宪法、需求规格、用例文本与用例图、领域模型与类图、架构设计与包图、数据库设计、风险分析与审查清单。

### 输入 Prompt 摘要

要求 Agent 以图书管理系统为例，按 Spec-Driven 流程依次生成 `specs/00`~`specs/19`，
采用 Python FastAPI 技术栈，遵守分层架构、MVC、业务规则集中、UML-as-Spec 等约束；
不编造需求，数值规则（借阅数量 / 期限 / 费率）以指导书与澄清回答为准。

### Agent 生成 / 修改文件

- specs/00-project-brief.md
- specs/01-clarifying-questions.md
- specs/constitution.md
- specs/02-requirements.md
- specs/03-use-cases.md
- specs/04-use-case-model.puml
- specs/05-domain-model.md
- specs/06-domain-class-diagram.puml
- specs/07-architecture.md
- specs/08-package-diagram.puml
- specs/13-database-design.md
- specs/17-risk-analysis.md
- specs/18-review-checklist.md

### 测试结果

本阶段为文档建模，暂无可执行测试。

### 人工审查结果

已对照 `18-review-checklist.md` 逐条审查，**34/34 项通过**（详见该文件 §8 审查结论）。
遗留 3 项（罚款结清状态、标题删除级联、权威字段名）转入实验二处理。

### Git 提交

- `docs: 生成实验一 Specs`
- `docs: 补齐命名一致性规约与审查结论`

### 冻结

`experiment1-specs-baseline-v1`

---

## 第 2 次使用

### 使用工具

Trae（AI 编码 Agent）

### 使用阶段

实验二 · 详细设计建模

### 使用任务

根据实验一已冻结的 baseline 与实验二指导书，生成详细设计 Specs：
详细设计模型、办理借书 / 办理还书 / 预约图书顺序图、API 接口规范、测试计划、任务拆解。

### 输入 Prompt 摘要

要求 Agent 以用例为单元给出 Controller / Application Service / Domain Service / Entity /
Repository / DTO / 异常 / 事务边界的详细设计；生成三个关键用例的 PlantUML 顺序图；
产出 REST API 规范（含权限与成功 / 失败场景，并固化权威字段名表）；
产出以 TC 编号的测试计划与可执行的 tasks.md；技术栈 Python FastAPI。

### Agent 生成 / 修改文件

- specs/09-design-model.md
- specs/10-sequence-borrow-book.puml
- specs/11-sequence-return-book.puml
- specs/12-sequence-reserve-book.puml
- specs/14-api-spec.md
- specs/15-test-plan.md
- specs/16-tasks.md

### 测试结果

本阶段为文档建模，暂无可执行测试。已按实验二审查要点自检：
顺序图与用例一致、API 覆盖核心用例、测试计划覆盖异常流程、业务规则位于正确分层、
体现 Strategy / Repository / Service Layer 等模式、与数据库设计一致。

### 人工审查结果

逐条自检通过；用户确认后冻结实验二 Spec baseline。遗留字段名以 `14-api-spec.md` 为准。

### Git 提交

- `docs: 生成实验二详细设计模型 09-design-model`
- `docs: 生成办理借书顺序图 10-sequence-borrow-book`
- `docs: 生成办理还书顺序图 11-sequence-return-book`
- `docs: 生成预约图书顺序图 12-sequence-reserve-book`
- `docs: 生成 API 接口规范 14-api-spec`
- `docs: 生成测试计划 15-test-plan`
- `docs: 生成实现任务拆解 16-tasks`

### 冻结

`experiment2-specs-baseline-v1`

---

## 第 3 次使用

### 使用工具

Trae（AI 编码 Agent）

### 使用阶段

实验二 · 代码实现与测试

### 使用任务

按 `16-tasks.md` 顺序实现分层代码与自动化测试：初始化项目结构、领域实体、Repository、
借阅规则策略、罚款规则策略、读者与借阅证管理、图书标题与馆藏管理、借书、还书、预约、
查询借阅、管理员维护与权限，并补齐测试与 README。

### 输入 Prompt 摘要

要求 Agent 严格按冻结的 specs 实现，不得修改 specs；分层架构（routers / services / domain /
repositories），借阅数量与期限集中在 BorrowPolicyService、费率集中在 FineRuleService；
统一响应 `{code,message,data}`；pytest + httpx 覆盖借书 / 还书 / 预约 / 超期罚款 / 权限失败。

### Agent 修改文件

- src/main.py、src/database.py、src/response.py、src/security.py、src/deps.py
- src/domain/（enums.py、models.py、services.py）
- src/repositories/（reader_repo、card_repo、admin_repo、catalog_repo、circulation_repo、
  reservation_repo、policy_repo）
- src/services/（reader_service、card_service、catalog_service、fine_service、
  circulation_service、reservation_service、admin_service、policy_service）
- src/routers/（reader_router、card_router、catalog_router、circulation_router、
  reservation_router、admin_router）
- src/schemas/（requests.py）、src/exceptions/（__init__.py）
- tests/（conftest.py、test_policy、test_reader_card、test_catalog、test_circulation、
  test_reservation、test_admin）
- requirements.txt、pytest.ini、README.md

### 测试结果

`pytest` 共 38 项测试全部通过（策略单元测试 + 接口集成测试）。

### 人工审查结果

实现过程中发现并修正两处问题：
① 借阅数量统计方法应位于 `ReaderRepository.count_borrowing`（与 `09-design-model.md` 一致），
初次误置于 `LoanRepository`，已改正；
② 角色权限基于请求携带的 ID 判断，测试种子数据需保证管理员 ID 与读者 ID 不重叠，已显式指定。
上述修正均只改代码，未改动已冻结 specs。

### Git 提交

- `feat: 实现分层架构与领域实体、仓储、策略`
- `feat: 实现借书/还书/预约/查询/管理用例`
- `test: 补充策略与接口测试`
- `docs: 更新 README`

