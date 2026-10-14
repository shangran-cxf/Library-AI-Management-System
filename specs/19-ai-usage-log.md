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

（待填）

### 使用阶段

（待填）

### 使用任务

（待填）

### 输入 Prompt 摘要

（待填）

### Agent 修改文件

（待填）

### 测试结果

（待填）

### 人工审查结果

（待填）

### Git 提交

（待填）
