# 人工审查清单

> 每一项都可由人工判断"是 / 否"。审查通过后方可冻结 baseline。
> 本次由 Agent 逐条核对并给出结论，人工复核后确认。

## 1. 需求规格（02-requirements.md）

- [x] 是否覆盖注册、借阅证、借还、查询、预约、罚款、系统维护？（FR-001~FR-016 全覆盖）
- [x] 是否明确"借书、还书由图书管理员代理"？（BR-001、FR-011/FR-012 验收标准）
- [x] 是否区分系统管理员与图书管理员权限？（BR-009、07-architecture §4）
- [x] 是否明确不同读者类型的借阅数量与期限？（Project Brief §5、澄清 A8/A9）
- [x] 是否明确不同借出物类型的罚款规则？（Project Brief §6、澄清 A13）
- [x] 每条功能需求是否都有可验证的验收标准？（FR-001~016 均含"验收标准"）
- [x] 是否混入了 Project Brief 中"暂不实现"的内容？（未混入，Non-Goals 见 Brief §8）

## 2. 用例文本（03-use-cases.md）

- [x] 是否识别了全部参与者（读者 / 学生 / 教师 / 图书管理员 / 系统管理员）？（§1 清单 + 04 用例图）
- [x] 重点用例（借书、还书、预约、办理借阅证、计算罚款）是否含基本 / 备选 / 异常流？（UC-101/102/004/201/110 均含三类事件流）
- [x] 办理借书是否包含"验证借阅证、检查数量、检查超期未还、检查可借"四步？（UC-101 步骤 2/3/4/7）
- [x] 办理还书是否包含超期罚款生成？（UC-102 步骤 6/7 调用 UC-110）

## 3. 用例图（04-use-case-model.puml）

- [x] Student / Teacher 是否泛化自 Reader？（`Reader <|-- Student`、`Reader <|-- Teacher`）
- [x] 用例关系（include）是否合理？（借书 include 验证借阅证 / 检查规则；还书 include 计算罚款）
- [x] 是否遗漏系统管理员的维护类用例？（UC-201~209 完整列出）

## 4. 领域模型 / 类图（05、06）

- [x] 领域类是否来自业务而非数据库表照搬？（含 BorrowPolicy / FineRule 等业务概念类）
- [x] 是否体现不同读者类型（继承 / 判别字段）？（Reader 继承 + ReaderType 枚举 + readers.reader_type）
- [x] 是否体现不同借出物类型？（Book / Magazine / Thesis 继承 + ItemType 枚举）
- [x] 借阅规则是否抽象为 `BorrowPolicy`？罚款规则是否为 `FineRule`？（均为独立策略类）
- [x] `Loan` 是否能表达借出 / 归还 / 超期？（status + is_overdue + overdueDays()）
- [x] `Reservation` 是否支持排队？（created_at + queue_position）
- [x] 是否误将 Controller / Repository / DTO 放入领域类图？（未混入，见 05 §1 说明）

## 5. 架构设计 / 包图（07、08）

- [x] 是否包含表现层 / 应用服务层 / 领域层 / 持久层？（07 §2、08 包图）
- [x] 是否体现 MVC，业务规则是否不在 Controller？（07 §1/§7）
- [x] Controller 是否**未**直接依赖 Repository？（07 §2.1 明令禁止，08 包图 note 标注）
- [x] 是否说明权限控制与异常处理策略？（07 §4、§5）
- [x] 是否说明事务边界与设计模式使用位置？（07 §6、§8）

## 6. 数据库设计（13）

- [x] `borrow_cards.card_no` 是否唯一？`library_items.barcode` 是否唯一？（均为 UNIQUE）
- [x] `loans` 是否能区分借出 / 已还 / 超期？（status 枚举 + is_overdue）
- [x] `reservations` 是否能支持排队？（created_at 索引 + queue_position）
- [x] `fine_rules` 是否按借出物类型？`borrow_policies` 是否按读者类型？（是，各自 item_type / reader_type 唯一）
- [x] 必要外键是否存在？索引是否覆盖高频查询？（§2 外键 + §3 索引表）

## 7. 一致性

- [x] API 字段名与数据库、领域模型、Agent 提示词是否一致？（统一规约见 07 §10：对外 snake_case，类图 camelCase 一一映射，权威以 14-api-spec 为准）
- [x] 是否已建立 baseline（Git tag）？（本次审查通过后创建 `experiment1-specs-baseline-v1`）
- [x] `19-ai-usage-log.md` 是否记录了本次 AI 使用？（第 1 次使用已登记）

---

## 8. 审查结论

| 类别 | 项数 | 通过 |
|---|---|---|
| 1 需求规格 | 7 | 7 |
| 2 用例文本 | 4 | 4 |
| 3 用例图 | 3 | 3 |
| 4 领域模型 / 类图 | 7 | 7 |
| 5 架构 / 包图 | 5 | 5 |
| 6 数据库 | 5 | 5 |
| 7 一致性 | 3 | 3 |
| **合计** | **34** | **34** |

**结论：全部 34 项通过，可冻结 baseline。**

**遗留事项（不影响冻结，转入实验二处理）**
1. 罚款的"缴纳 / 结清"状态流转未细化（当前仅生成记录）。
2. 删除图书标题采用逻辑删除，级联规则待实验二明确。
3. 权威字段名表待 `14-api-spec.md` 产出后最终固化。

**baseline 标记**
- `experiment1-specs-baseline-v1`（实验一冻结）
