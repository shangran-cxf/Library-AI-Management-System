# 图书管理系统开发宪法（constitution.md）

> 本文件约束 Agent 在生成 specs、UML、代码与测试时的行为。任何与本宪法冲突的输出都无效。

## 1. Specs 优先原则

任何代码实现前，必须先完成需求、用例、领域模型、架构、数据库、测试和任务拆解文档。
没有对应规格的功能一律不实现。

## 2. Agent 起草，人类确认原则

Agent 可以生成规格初稿，但所有规格必须经过人工审查后才能作为实现依据。
Agent 不得假设自己拥有对业务规则的最终解释权。

## 3. UML-as-Spec 原则

用例图、类图、包图、顺序图必须使用 **PlantUML 或 Mermaid 文本格式**保存到 `specs/` 目录，
纳入 Git 管理，不得只在图形工具中保留二进制图。

## 4. Baseline 原则

Specs 审查通过后必须建立 baseline（打 Git tag）。实现阶段 Agent **不得擅自修改 specs**。
若实现中发现规格问题，须先提出并请求人类确认，再修订 specs。

## 5. 分层架构原则

系统必须采用分层架构，至少包含：

- 表现层 / 控制层（Controller）
- 应用服务层（Application Service）
- 领域层（Domain）
- 基础设施 / 持久化层（Infrastructure / Persistence）

依赖方向只能由外向内，Controller 不得直接依赖 Repository。

## 6. MVC 原则

Web 层应遵循 MVC 或类似分离思想，**不得把业务规则写入 Controller**。

## 7. 权限原则

图书管理员、系统管理员与读者的权限必须区分。
借书、还书只能由图书管理员代理；系统维护类操作只能由系统管理员执行。

## 8. 业务规则集中原则

借阅数量、借阅期限、超期罚款等规则必须集中在 `BorrowPolicy`（策略）或 `FineRule`（策略）
或对应 Service 中实现，不得散落在界面层或 Controller。

## 9. 测试闭环原则

核心用例必须有自动化测试，至少覆盖借书、还书、预约、超期罚款和权限失败场景。
每次实现后必须运行测试。

## 10. Git 审查原则

Agent 修改代码后，学生必须查看 `git diff`，再决定是否提交。
提交信息应体现按任务逐步开发的过程。

## 11. AI 使用记录原则

每次使用 Agent 生成 specs、UML、代码或测试，都必须记录在 `19-ai-usage-log.md` 中，
包含使用任务、输入 Prompt 摘要、Agent 修改文件、测试结果与人工审查结果。

## 12. 技术栈约定

- 语言 / 框架：Python 3.10+ / FastAPI
- 持久化：SQLAlchemy + SQLite
- 校验：Pydantic
- 测试：pytest + httpx
- 建模：PlantUML（UML-as-Spec）

## 13. 命名与接口一致原则

凡是穿过 API 边界的字段名（如 `reader_id`、`book_id`、`code`、`due_date`）必须在
后端实现、API 规范、Agent 提示词中保持完全一致。
