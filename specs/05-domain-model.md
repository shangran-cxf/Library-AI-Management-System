# 领域模型

> 来源：`02-requirements.md`、`03-use-cases.md`。本模型只描述业务概念，不含 Controller / Repository / DTO 等设计类。

## 1. 领域类分类

| 类别 | 类 |
|---|---|
| 实体 Entity | Reader、StudentReader、TeacherReader、BorrowCard、Librarian、SystemAdmin、BookTitle、LibraryItem、Book、Magazine、Thesis、Loan、Reservation、FineRecord |
| 值对象 Value Object | ReaderType（枚举）、ItemType（枚举）、LoanStatus（枚举）、ReservationStatus（枚举）、Money |
| 策略 / 服务 Strategy | BorrowPolicy、FineRule |

## 2. 核心领域类

### 2.1 Reader（读者，抽象实体）

| 项 | 内容 |
|---|---|
| 职责 | 表示可借阅的读者，承载身份与借阅状态 |
| 关键属性 | `readerId`、`name`、`department`、`readerType`、`account` |
| 关键行为 | `borrowLimit()`、`borrowDays()`、`hasOverdue()`、`currentLoanCount()` |
| 约束 | 每个 Reader 最多一张有效 BorrowCard |
| 关系 | 泛化父类；1—1 BorrowCard；1—* Loan；1—* Reservation |

- `StudentReader`：专科生 / 本科生 / 研究生 / 博士生，`readerType` 取对应枚举值。
- `TeacherReader`：教师，借阅额度最高。

### 2.2 BorrowCard（借阅证，实体）

| 项 | 内容 |
|---|---|
| 职责 | 读者的借阅凭证 |
| 关键属性 | `cardNo`（唯一）、`readerId`、`issueDate`、`expireDate`、`status` |
| 关键行为 | `isValid()` |
| 约束 | `cardNo` 唯一；同一读者仅一张有效证 |
| 关系 | 1—1 Reader |

### 2.3 Librarian / SystemAdmin（实体）

| 类 | 职责 | 关键属性 |
|---|---|---|
| Librarian | 代理办理借书、还书、查询 | `librarianId`、`name`、`account` |
| SystemAdmin | 系统维护 | `adminId`、`name`、`account` |

### 2.4 BookTitle（图书标题，实体）

| 项 | 内容 |
|---|---|
| 职责 | 描述一种图书的元数据，与具体副本分离 |
| 关键属性 | `titleId`、`title`、`author`、`isbn`（唯一）、`publisher`、`category`、`itemType` |
| 关键行为 | `availableItemCount()` |
| 关系 | 1—* LibraryItem；1—* Reservation |

### 2.5 LibraryItem（馆藏副本，抽象实体）

| 项 | 内容 |
|---|---|
| 职责 | 表示可实际借出的馆藏副本 |
| 关键属性 | `itemId`、`barcode`（唯一）、`titleId`、`status`（AVAILABLE / BORROWED / RESERVED / REMOVED）、`location` |
| 关键行为 | `isAvailable()`、`markBorrowed()`、`markAvailable()` |
| 关系 | 泛化父类；*—1 BookTitle；1—* Loan |

- `Book`（图书）、`Magazine`（杂志）、`Thesis`（论文）：`LibraryItem` 的具体类型，决定 `itemType` 与罚款费率。

### 2.6 Loan（借阅记录，实体）

| 项 | 内容 |
|---|---|
| 职责 | 记录一次借出与归还 |
| 关键属性 | `loanId`、`readerId`、`itemId`、`borrowDate`、`dueDate`、`returnDate`、`status`、`isOverdue` |
| 关键行为 | `isReturned()`、`isOverdue()`、`overdueDays()` |
| 关系 | *—1 Reader；*—1 LibraryItem；1—* FineRecord |

### 2.7 Reservation（预约，实体）

| 项 | 内容 |
|---|---|
| 职责 | 表示读者对某图书标题的预约排队 |
| 关键属性 | `reservationId`、`readerId`、`titleId`、`createdAt`、`status`、`queuePosition` |
| 关键行为 | `isActive()` |
| 约束 | 同一读者对同一标题仅一个有效预约；按 `createdAt` 排队 |
| 关系 | *—1 Reader；*—1 BookTitle |

### 2.8 BorrowPolicy（借阅规则策略）

| 项 | 内容 |
|---|---|
| 职责 | 按读者类型给出借阅数量与期限 |
| 关键行为 | `getMaxBorrowCount(readerType)`、`getBorrowDays(readerType)`、`canBorrow(reader, currentLoans)` |
| 说明 | 策略对象，规则集中于此，不得散落在界面层 |

### 2.9 FineRule（罚款规则策略）

| 项 | 内容 |
|---|---|
| 职责 | 按借出物类型给出超期费率 |
| 关键行为 | `getRate(itemType)`、`calculateFine(itemType, overdueDays)` |
| 约束 | `overdueDays <= 0` 时罚款为 0 |

### 2.10 FineRecord（罚款记录，实体）

| 项 | 内容 |
|---|---|
| 职责 | 记录一次罚款结果 |
| 关键属性 | `fineId`、`loanId`、`readerId`、`itemType`、`overdueDays`、`amount`、`createdAt`、`status` |
| 关系 | *—1 Loan |

## 3. 关键约束汇总

- 借书、还书由 Librarian 代理，读者不直接操作（BR-001）。
- 借阅数量 / 期限由 `BorrowPolicy` 决定（BR-003、BR-004）。
- 超期未还禁止借书（BR-005）。
- 罚款费率由 `FineRule` 决定（BR-007）。
- 预约按 `createdAt` 排队（BR-008）。
