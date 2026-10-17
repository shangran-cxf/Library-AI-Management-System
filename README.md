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

## 架构说明

采用**分层架构 + MVC 思想**，依赖方向只能由外向内：

```
表现层 routers/（FastAPI Controller）
  → 应用服务层 services/（组织用例、事务边界、返回 DTO）
    → 领域层 domain/（实体、枚举、BorrowPolicy / FineRule 策略）
      ← 持久化层 repositories/（SQLAlchemy 实现）
```

- Controller 只接收请求 / 返回统一响应，不含业务规则，也不直接访问 Repository。
- 借阅数量 / 期限集中在 `domain/services.py::BorrowPolicyService`；
  超期费率集中在 `domain/services.py::FineRuleService`。
- 统一响应结构：`{ "code": 200/400/403/404/500, "message": "...", "data": {...} }`。

## 目录结构

```
Library-AI-Management-System/
  specs/                 # 全部规格文档与 UML 图（实验一、实验二）
  src/
    main.py              # 应用入口（装配路由、统一响应、全局异常处理）
    database.py          # 引擎 / 会话 / 建表 / 默认规则种子
    deps.py              # 依赖注入（请求级会话）
    response.py          # 统一响应结构
    security.py          # 角色权限校验（Librarian / SystemAdmin）
    domain/              # 领域层：models（实体）、enums、services（策略）
    repositories/        # 持久化层：各 Repository
    services/            # 应用服务层：各用例服务
    routers/             # 表现层：FastAPI 路由
    schemas/             # DTO（Pydantic）
    exceptions/          # 自定义异常层次
  tests/                 # pytest 自动化测试
  homework/              # 扩展作业（续借 + 图书评论评分，独立 FastAPI 服务，端口 8001）
  requirements.txt
  pytest.ini
  README.md
  .gitignore
```

## 启动方式

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

启动后访问 `http://127.0.0.1:8000/docs` 查看交互式 API 文档。

## 测试方式

```bash
pytest -v
```

当前共 38 个测试（含策略单元测试与接口集成测试），全部通过。

## 核心用例

| 用例 | 说明 |
|---|---|
| UC-101 办理借书 | 图书管理员代理；校验借阅证、数量、超期、副本可借 |
| UC-102 办理还书 | 图书管理员代理；恢复副本、超期生成罚款 |
| UC-110 计算超期罚款 | 被还书包含；按借出物类型费率计算 |
| UC-004 预约图书 | 读者预约，按创建时间排队，禁止重复预约 |
| UC-201 办理借阅证 | 系统管理员办理，证号唯一、一读者一证 |
| UC-205/207 标题与副本维护 | 系统管理员维护，ISBN / 条码唯一 |

## 核心 API

| 方法 | 路径 | 权限 |
|---|---|---|
| POST | `/api/readers` | 公开 |
| GET | `/api/books` | 公开 |
| POST | `/api/admin/borrow-cards` | SystemAdmin |
| POST | `/api/admin/book-titles` | SystemAdmin |
| POST | `/api/admin/library-items` | SystemAdmin |
| PUT | `/api/admin/borrow-policies`、`/api/admin/fine-rules` | SystemAdmin |
| POST | `/api/circulation/borrow` | Librarian |
| POST | `/api/circulation/return` | Librarian |
| GET | `/api/readers/{reader_id}/loans` | 本人 / Librarian |
| POST | `/api/reservations` | 读者 |

完整字段与错误码见 [specs/14-api-spec.md](specs/14-api-spec.md)。

## UML 文档说明

- `specs/04-use-case-model.puml`：用例图
- `specs/06-domain-class-diagram.puml`：领域类图
- `specs/08-package-diagram.puml`：包图
- `specs/10~12-*.puml`：办理借书 / 办理还书 / 预约图书顺序图

均以 PlantUML 文本格式纳入 Git 管理，可用 PlantUML 或 VS Code 插件渲染。

## Agent 使用说明

本项目按 `specs/constitution.md` 约束使用 AI Agent 辅助开发，遵循
"Specs 优先 → Agent 起草 → 人类确认 → 冻结 baseline → Agent 实现 → 测试闭环"
的流程。历次 Agent 使用记录见 [specs/19-ai-usage-log.md](specs/19-ai-usage-log.md)。

## 扩展作业

[homework/library-hw-system-stu-impl](homework/library-hw-system-stu-impl) 是独立的对话式图书管理系统扩展作业：
在后端新增「续借」与「图书评论评分」两个能力，并同步更新 `.codebuddy` 下的 Agent / Skill 提示词。

- 实现说明：[homework/library-hw-system-stu-impl/README.md](homework/library-hw-system-stu-impl/README.md)
- 接口 curl 实测：[接口测试记录.md](homework/library-hw-system-stu-impl/接口测试记录.md)
- 运行方式：`cd homework/library-hw-system-stu-impl/backend` → `python main.py`（端口 8001）

## 实验阶段

- **实验一**：应用系统的架构设计（需求 → 用例 → 领域模型 → 架构 → 数据库设计）
- **实验二**：应用系统的详细设计（详细设计 → 顺序图 → API → 测试计划 → 代码实现）

## 当前进度

- [x] 建立项目骨架与 Git 仓库
- [x] 实验一：架构设计与 Spec 建模（baseline：`experiment1-specs-baseline-v1`）
- [x] 实验二 Spec：详细设计 / 顺序图 / API / 测试计划 / 任务拆解（baseline：`experiment2-specs-baseline-v1`）
- [x] 实验二实现：分层代码 + 38 项自动化测试全绿
- [x] 扩展作业：续借 + 图书评论评分（15 项测试通过，已并入 `homework/`）


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
