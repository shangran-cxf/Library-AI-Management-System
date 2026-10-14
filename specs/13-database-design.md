# 数据库设计

> 来源：`05-domain-model.md`、`07-architecture.md`。数据库为 SQLite（SQLAlchemy）。

## 1. 持久化类 → 关系表

| 领域类 | 表名 |
|---|---|
| Reader / StudentReader / TeacherReader | `readers` |
| BorrowCard | `borrow_cards` |
| Librarian | `librarians` |
| SystemAdmin | `system_admins` |
| BookTitle | `book_titles` |
| LibraryItem / Book / Magazine / Thesis | `library_items` |
| Loan | `loans` |
| Reservation | `reservations` |
| BorrowPolicy | `borrow_policies` |
| FineRule | `fine_rules` |
| FineRecord | `fine_records` |

## 2. 表结构

### 2.1 readers

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| reader_id | INTEGER | 否 | PK | 自增 | 读者 ID |
| name | VARCHAR(50) | 否 | | | 姓名 |
| department | VARCHAR(100) | 是 | | | 院系 / 单位 |
| reader_type | VARCHAR(20) | 否 | 索引 | | 判别字段：JUNIOR/UNDERGRADUATE/GRADUATE/DOCTOR/TEACHER |
| account | VARCHAR(50) | 否 | UNIQUE | | 登录账号 |
| password | VARCHAR(100) | 是 | | | 密码（第一阶段可明文/哈希） |
| created_at | DATETIME | 是 | | now | 创建时间 |

### 2.2 borrow_cards

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| card_id | INTEGER | 否 | PK | 自增 | 借阅证 ID |
| card_no | VARCHAR(20) | 否 | **UNIQUE** | | 借阅证号 CARD+年份+6位序号 |
| reader_id | INTEGER | 否 | FK→readers.reader_id, **UNIQUE** | | 关联读者（一读者一证） |
| issue_date | DATE | 是 | | | 办理日期 |
| expire_date | DATE | 是 | | | 有效期 |
| status | VARCHAR(10) | 否 | | ACTIVE | ACTIVE / INACTIVE |

### 2.3 librarians

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| librarian_id | INTEGER | 否 | PK | 自增 | 管理员 ID |
| name | VARCHAR(50) | 否 | | | 姓名 |
| account | VARCHAR(50) | 否 | UNIQUE | | 登录账号 |
| password | VARCHAR(100) | 是 | | | 密码 |
| created_at | DATETIME | 是 | | now | 创建时间 |

### 2.4 system_admins

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| admin_id | INTEGER | 否 | PK | 自增 | 系统管理员 ID |
| name | VARCHAR(50) | 否 | | | 姓名 |
| account | VARCHAR(50) | 否 | UNIQUE | | 登录账号 |
| password | VARCHAR(100) | 是 | | | 密码 |
| created_at | DATETIME | 是 | | now | 创建时间 |

### 2.5 book_titles

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| title_id | INTEGER | 否 | PK | 自增 | 标题 ID |
| title | VARCHAR(200) | 否 | 索引 | | 题名 |
| author | VARCHAR(100) | 否 | 索引 | | 作者 |
| isbn | VARCHAR(20) | 否 | UNIQUE | | ISBN |
| publisher | VARCHAR(100) | 是 | | | 出版社 |
| category | VARCHAR(50) | 是 | | | 分类 |
| item_type | VARCHAR(20) | 否 | | | 借出物类型枚举 |
| created_at | DATETIME | 是 | | now | 创建时间 |

### 2.6 library_items

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| item_id | INTEGER | 否 | PK | 自增 | 副本 ID |
| barcode | VARCHAR(30) | 否 | **UNIQUE** | | 馆藏条码 |
| title_id | INTEGER | 否 | FK→book_titles.title_id | | 所属标题 |
| item_type | VARCHAR(20) | 否 | | | 判别字段：BOOK/MAGAZINE/THESIS |
| status | VARCHAR(20) | 否 | 索引 | AVAILABLE | AVAILABLE/BORROWED/RESERVED/REMOVED |
| location | VARCHAR(50) | 是 | | | 馆藏位置 |
| created_at | DATETIME | 是 | | now | 创建时间 |

### 2.7 loans

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| loan_id | INTEGER | 否 | PK | 自增 | 借阅记录 ID |
| reader_id | INTEGER | 否 | FK→readers.reader_id | | 借阅人 |
| item_id | INTEGER | 否 | FK→library_items.item_id | | 借出副本 |
| borrow_date | DATETIME | 否 | | now | 借出日期 |
| due_date | DATETIME | 否 | | | 应还日期（按读者类型计算） |
| return_date | DATETIME | 是 | | NULL | 归还日期 |
| status | VARCHAR(20) | 否 | 索引 | BORROWING | BORROWING/RETURNED/OVERDUE |
| is_overdue | BOOLEAN | 否 | | 0 | 是否超期 |

### 2.8 reservations

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| reservation_id | INTEGER | 否 | PK | 自增 | 预约 ID |
| reader_id | INTEGER | 否 | FK→readers.reader_id | | 预约人 |
| title_id | INTEGER | 否 | FK→book_titles.title_id | | 预约标题 |
| created_at | DATETIME | 否 | 索引 | now | 创建时间（排队依据） |
| status | VARCHAR(20) | 否 | | ACTIVE | ACTIVE/FULFILLED/CANCELLED |
| queue_position | INTEGER | 是 | | | 排队序号 |

### 2.9 borrow_policies

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| policy_id | INTEGER | 否 | PK | 自增 | 规则 ID |
| reader_type | VARCHAR(20) | 否 | UNIQUE | | 读者类型 |
| max_borrow_count | INTEGER | 否 | | | 最大借阅数量 |
| borrow_days | INTEGER | 否 | | | 借阅期限（天） |

### 2.10 fine_rules

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| rule_id | INTEGER | 否 | PK | 自增 | 规则 ID |
| item_type | VARCHAR(20) | 否 | UNIQUE | | 借出物类型 |
| rate_per_day | DECIMAL(6,2) | 否 | | | 超期费率（元/天） |

### 2.11 fine_records

| 字段 | 类型 | 空 | 键 / 约束 | 默认 | 说明 |
|---|---|---|---|---|---|
| fine_id | INTEGER | 否 | PK | 自增 | 罚款记录 ID |
| loan_id | INTEGER | 否 | FK→loans.loan_id | | 关联借阅记录 |
| reader_id | INTEGER | 否 | FK→readers.reader_id | | 读者 |
| item_type | VARCHAR(20) | 否 | | | 借出物类型 |
| overdue_days | INTEGER | 否 | | | 超期天数 |
| amount | DECIMAL(8,2) | 否 | | | 罚金 |
| created_at | DATETIME | 是 | | now | 生成时间 |
| status | VARCHAR(20) | 否 | | UNPAID | UNPAID/PAID |

## 3. 索引设计

| 表 | 索引 | 目的 |
|---|---|---|
| readers | UNIQUE(account) | 账号唯一 |
| borrowers_cards | UNIQUE(card_no)、UNIQUE(reader_id) | 证号唯一、一读者一证 |
| book_titles | UNIQUE(isbn)、INDEX(title, author) | ISBN 唯一、检索 |
| library_items | UNIQUE(barcode)、INDEX(status) | 条码唯一、按状态检索 |
| loans | INDEX(reader_id, status) | 查询读者在借记录 |
| reservations | INDEX(title_id, status, created_at) | 预约排队 |
| fine_records | INDEX(reader_id) | 查询读者罚款 |

## 4. 继承映射策略

采用**单表继承 + 判别字段**：

- `readers.reader_type` 区分 StudentReader / TeacherReader。
- `library_items.item_type` 区分 Book / Magazine / Thesis。

理由：结构简单、查询高效，符合课程实验复杂度；避免多表 JOIN 带来的额外复杂度。

## 5. 业务规则在数据层的体现

- 借阅数量 / 期限由 `borrow_policies` 驱动。
- 罚金费率由 `fine_rules` 驱动。
- 超期状态由 `loans.is_overdue` 与 `status` 表达。
- 预约排队由 `reservations.created_at` 排序。
