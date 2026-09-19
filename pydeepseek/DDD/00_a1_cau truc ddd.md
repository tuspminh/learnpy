**Domain-Driven Design (DDD)** là một phương pháp thiết kế phần mềm tập trung vào việc mô hình hóa nghiệp vụ (domain) phức tạp. Cấu trúc DDD thường được chia thành **4 lớp chính** (Layered Architecture) và các **building blocks** đi kèm.

---

## 1. Kiến trúc phân lớp (Layered Architecture)

```
┌─────────────────────────────────────┐
│   Presentation / UI Layer           │  ← Controllers, ViewModels
├─────────────────────────────────────┤
│   Application Layer                 │  ← Use Cases, App Services
├─────────────────────────────────────┤
│   Domain Layer (trái tim)           │  ← Entities, Value Objects,
│                                     │     Aggregates, Domain Events
├─────────────────────────────────────┤
│   Infrastructure Layer              │  ← DB, Message Queue, Email...
└─────────────────────────────────────┘
```

### 🔹 Presentation Layer
- Tiếp nhận request từ người dùng (REST API, GraphQL, UI).
- Không chứa logic nghiệp vụ.
- Chuyển đổi dữ liệu → gọi Application Layer.

### 🔹 Application Layer
- Điều phối (orchestration) các use case.
- Không chứa business rule cốt lõi.
- Chứa: **Application Services**, **DTOs**, **Command/Query Handlers** (CQRS).

### 🔹 Domain Layer (quan trọng nhất)
- Chứa toàn bộ logic nghiệp vụ.
- Không phụ thuộc vào framework, DB, hay UI.
- Là nơi áp dụng **Ubiquitous Language**.

### 🔹 Infrastructure Layer
- Triển khai kỹ thuật: Repository impl, ORM, HTTP client, message broker…
- Phụ thuộc vào Domain (thông qua interface).

---

## 2. Building Blocks của DDD

| Block | Mô tả |
|---|---|
| **Entity** | Có identity (ID) riêng, vòng đời dài |
| **Value Object** | Bất biến, không có ID, so sánh bằng giá trị |
| **Aggregate** | Nhóm Entity/VO có **Aggregate Root** kiểm soát |
| **Aggregate Root** | Cổng vào duy nhất của Aggregate, đảm bảo invariant |
| **Domain Event** | Sự kiện nghiệp vụ đã xảy ra (OrderPlaced, PaymentReceived) |
| **Domain Service** | Logic nghiệp vụ không thuộc Entity/VO nào |
| **Repository** | Truy xuất Aggregate (interface ở Domain, impl ở Infra) |
| **Factory** | Tạo phức tạp cho Aggregate/Entity |
| **Specification** | Biểu diễn rule nghiệp vụ có thể kết hợp |

---

## 3. Cấu trúc thư mục tham khảo (ví dụ Java/.NET)

```
src/
├── Domain/
│   ├── Entities/
│   ├── ValueObjects/
│   ├── Aggregates/
│   ├── Events/
│   ├── Services/
│   ├── Repositories/       (interface)
│   └── Exceptions/
│
├── Application/
│   ├── Commands/
│   ├── Queries/
│   ├── Handlers/
│   ├── DTOs/
│   └── Services/
│
├── Infrastructure/
│   ├── Persistence/
│   │   ├── Repositories/   (impl)
│   │   └── DbContext/
│   ├── Messaging/
│   └── ExternalServices/
│
└── Presentation/
    ├── Controllers/
    └── ViewModels/
```

---

## 4. Nguyên tắc quan trọng

1. **Ubiquitous Language** – Dùng chung ngôn ngữ giữa dev và business.
2. **Dependency Rule** – Domain không phụ thuộc lớp ngoài; các lớp ngoài phụ thuộc Domain.
3. **Bounded Context** – Chia hệ thống lớn thành nhiều context độc lập.
4. **Aggregate nhỏ** – Mỗi aggregate chỉ chứa những gì cần đảm bảo consistency.
5. **Repository chỉ cho Aggregate Root** – Không expose repository cho Entity con.

---

## 5. Khi nào nên dùng DDD?

✅ **Nên dùng:**
- Domain phức tạp, nhiều business rule.
- Hệ thống lớn, nhiều team.
- Cần mô hình hóa chính xác nghiệp vụ.

❌ **Không nên dùng:**
- CRUD đơn giản, ít logic.
- Dự án nhỏ, deadline gấp.
- Domain không rõ ràng, thay đổi liên tục.

---

Bạn muốn mình đi sâu vào phần nào? Ví dụ:
- **Code mẫu** (C#/Java/TypeScript) cho một Aggregate cụ thể?
- **CQRS + Event Sourcing** kết hợp DDD?
- **So sánh** DDD với Clean Architecture / Hexagonal?