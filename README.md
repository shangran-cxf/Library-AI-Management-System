# Library-AI-Management-System

《软件设计与体系结构》课程实验项目 —— AI 时代的图书管理系统。

## 项目简介

本项目采用 **Spec-Driven（规格驱动）+ AI Agent 辅助** 的开发方式，完成图书管理系统的
架构设计与详细设计。核心流程为：

```
人类提供目标与约束
  → Agent 辅助提出澄清问题、生成规格 / UML / 架构 / 数据库 / 测试
  → 人类审查并冻结 Specs Baseline
  → Agent 按任务实现代码
  → 自动化测试验证
  → 人工审查 Git diff 并提交
```

## 技术栈

- 语言 / 框架：Python 3.10+ / FastAPI
- 数据库：SQLite（SQLAlchemy）
- 测试：pytest + httpx
- 建模：PlantUML / Mermaid（UML-as-Spec）
- 版本管理：Git + GitHub

## 目录结构

```
Library-AI-Management-System/
  specs/          # 全部规格文档与 UML 图（实验一、实验二）
  src/            # 源代码（实验二实现阶段）
  tests/          # 自动化测试
  README.md
  .gitignore
```

## specs 目录说明

| 文件 | 作用 |
|---|---|
| 00-project-brief.md | 项目背景与约束 |
| 01-clarifying-questions.md | 需求澄清问题及回答 |
| 02-requirements.md | 功能 / 非功能需求 |
| 03-use-cases.md | 用例文本 |
| 04-use-case-model.puml | 用例图 |
| 05-domain-model.md | 领域模型 |
| 06-domain-class-diagram.puml | 领域类图 |
| 07-architecture.md | 架构设计 |
| 08-package-diagram.puml | 包图 |
| 09-design-model.md | 详细设计 |
| 10~12-*.puml | 借书 / 还书 / 预约顺序图 |
| 13-database-design.md | 数据库设计 |
| 14-api-spec.md | API 接口规范 |
| 15-test-plan.md | 测试计划 |
| 16-tasks.md | 任务拆解 |
| 17-risk-analysis.md | 风险分析 |
| 18-review-checklist.md | 人工审查清单 |
| 19-ai-usage-log.md | AI 使用记录 |
| constitution.md | 开发宪法（Agent 行为约束） |

## 实验阶段

- **实验一**：应用系统的架构设计（需求 → 用例 → 领域模型 → 架构 → 数据库设计）
- **实验二**：应用系统的详细设计（详细设计 → 顺序图 → API → 测试计划 → 代码实现）

## 当前进度

- [x] 建立项目骨架与 Git 仓库
- [ ] 实验一：架构设计与 Spec 建模
- [ ] 实验二：详细设计与 Agent 实现
