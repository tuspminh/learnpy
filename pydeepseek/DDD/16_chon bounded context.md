# 📖 Bài 16: Chiến lược chọn Bounded Context — Khi nào tách, khi nào gộp

> Đây là **bài cuối của Level 4** — và là bài **chiến lược nhất** của cả lộ trình. Bạn đã biết Bounded Context là gì (bài 4), vẽ Context Map (bài 14), chạy Event Storming (bài 15). Giờ câu hỏi khó nhất: **Khi nào nên tách? Khi nào nên gộp? Bao nhiêu context là đủ?** Bài này sẽ trả lời — và dạy bạn cách tránh **2 cái bẫy chết người**: tách quá nhiều (microservices loạn) và gộp quá nhiều (monolith không maintain được).

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **chiến lược chọn Bounded Context** là gì.
2. Nắm **7 tiêu chí tách context** và **6 tiêu chí gộp**.
3. Hiểu **Core Domain Chart** — phân loại context.
4. Hiểu **Conway's Law** và **team topology**.
5. Biết **3 mô hình triển khai**: monolith, modular monolith, microservices.
6. Biết **khi nào tách**, **khi nào gộp**, **khi nào chưa**.
7. Biết **chi phí thật** của việc tách context.
8. Tránh được **8 anti-pattern** chiến lược.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Chiến lược chọn Bounded Context là gì?

### 1.1. Định nghĩa

> **Chiến lược chọn Bounded Context** là quá trình **quyết định** hệ thống nên có bao nhiêu context, ranh giới ở đâu, và triển khai thế nào (monolith, modular monolith, microservices).

### 1.2. Trực giác

Hãy tưởng tượng bạn quản lý **một thành phố**.

- Bạn có thể để thành phố **không có quận** (monolith).
- Bạn có thể chia thành **quận hành chính** (modular monolith).
- Bạn có thể chia thành **thành phố tự trị** (microservices).

**Câu hỏi:** Chia thế nào cho **vừa đủ**?

- Chia quá nhỏ → nhiều thủ tục, giao thông phức tạp.
- Chia quá lớn → quản lý khó, dân không được phục vụ tốt.
- **Chia vừa đủ** → hiệu quả.

Đó là chiến lược chọn Bounded Context.

### 1.3. Tại sao khó?

**Vì mọi lựa chọn đều có trade-off:**

| Tách | Gộp |
|---|---|
| Độc lập deploy | Deploy dễ |
| Team tự chủ | Không cần coordination |
| Scale độc lập | Không cần network |
| Công nghệ riêng | Không có distributed transaction |
| **Nhưng:** phức tạp, network, eventual consistency | **Nhưng:** coupling, bottleneck, khó scale |

**Không có câu trả lời đúng cho mọi dự án.** Chiến lược phụ thuộc vào: team size, domain complexity, tuổi thọ dự án, yêu cầu scale.

---

## 2. Bảy tiêu chí tách Context

Đây là **7 dấu hiệu** nên tách thành context riêng.

### 2.1. Cùng từ, nghĩa khác

Nếu 2 nhóm dùng cùng từ nhưng hiểu khác → **tách**.

**Ví dụ:**

- Sales nói "Customer" = người mua hàng.
- Support nói "Customer" = người có ticket.
- Shipping nói "Customer" = người nhận hàng.

→ 3 nghĩa khác nhau → có thể tách thành 3 context.

### 2.2. Team ownership khác nhau

Nếu 2 team sở hữu 2 phần → **tách**.

**Lý do:** Team A không nên chờ Team B deploy.

**Ví dụ:**

- Team Catalog (5 người) ở Hà Nội.
- Team Order (3 người) ở Sài Gòn.

→ Tách để 2 team độc lập.

### 2.3. Tốc độ thay đổi khác nhau

Nếu 2 phần thay đổi với tốc độ **rất khác nhau** → **tách**.

**Ví dụ:**

- Catalog đổi 10 lần/ngày (thêm sản phẩm, sửa giá).
- Billing đổi 1 lần/tháng (rule thuế ổn định).

→ Tách để code chậm không kéo code nhanh chậm lại.

### 2.4. Yêu cầu phi chức năng khác nhau

Nếu 2 phần có **yêu cầu khác nhau** về performance, availability, security → **tách**.

**Ví dụ:**

- Payment cần **ACID**, **PCI-DSS**, **high security**.
- Analytics cần **throughput cao**, **eventual consistency**.

→ Tách để mỗi bên chọn công nghệ phù hợp.

### 2.5. Domain complexity khác nhau

Nếu phần này **phức tạp**, phần kia **đơn giản** → có thể tách.

**Ví dụ:**

- Pricing phức tạp (nhiều rule, promo, tax).
- Notification đơn giản (gửi email/SMS).

→ Tách để tập trung nguồn lực vào phần phức tạp.

### 2.6. Bounded Context tự nhiên

Khi Event Storming, bạn thấy **đường phân chia tự nhiên** → tách.

**Ví dụ:**

- Events của Movies, Cinemas, Showtimes → Catalog.
- Events của Ticket Reserved, Payment Completed → Booking.

→ 2 context tự nhiên.

### 2.7. Có thể eventual consistent

Nếu 2 phần có thể **eventual consistent** (không cần ACID ngay) → có thể tách.

**Ví dụ:**

- Order placed → Analytics có thể update sau vài giây.
- Order placed → Email có thể gửi sau vài giây.

→ Tách, sync qua event.

### 2.8. Bảng tóm tắt

| Tiêu chí | Dấu hiệu |
|---|---|
| Cùng từ khác nghĩa | 2 team dùng từ khác nhau |
| Team ownership | Team A ≠ Team B |
| Tốc độ thay đổi | 10x khác biệt |
| Yêu cầu phi chức năng | ACID vs eventual |
| Domain complexity | Phức tạp vs đơn giản |
| Natural boundary | Event Storming chỉ ra |
| Có thể eventual consistent | Không cần ACID ngay |

---

## 3. Sáu tiêu chí gộp Context

Đây là **6 dấu hiệu** KHÔNG nên tách — nên gộp.

### 3.1. Cần ACID xuyên suốt

Nếu 2 phần cần **transaction ACID** → **gộp**.

**Ví dụ:**

- Chuyển tiền giữa 2 tài khoản phải atomic.
- Nếu tách → cần distributed transaction → phức tạp.

→ Gộp `Account` và `Transaction` vào cùng context.

### 3.2. Team quá nhỏ

Nếu team < 5 người → **gộp**.

**Lý do:** Tách quá nhiều context → mỗi người phải làm nhiều việc → không hiệu quả.

**Quy tắc ngón tay:**

- 1-3 người → 1 context.
- 4-8 người → 1-2 context.
- 9-15 người → 2-4 context.
- 16+ người → 4+ context.

### 3.3. Domain chưa rõ ràng

Nếu **chính business còn chưa hiểu rule** → **gộp**.

**Lý do:** Tách sớm khi chưa hiểu → sai boundary → refactor đau.

**Quy tắc:** Đợi đến khi hiểu rõ rồi hãy tách.

### 3.4. Tuổi thọ dự án ngắn

Nếu dự án < 1 năm → **gộp**.

**Lý do:** Chi phí tách (network, deploy, ops) không đáng cho dự án ngắn.

### 3.5. Không có yêu cầu scale

Nếu hệ thống chỉ phục vụ **vài trăm user** → **gộp**.

**Lý do:** Microservices chỉ đáng khi cần scale lớn.

### 3.6. Đội ngũ chưa có kinh nghiệm distributed system

Nếu team **chưa từng làm microservices** → **gộp**.

**Lý do:** Microservices có **rất nhiều cạm bẫy**: network failure, distributed tracing, eventual consistency, deployment phức tạp.

### 3.7. Bảng tóm tắt

| Tiêu chí | Dấu hiệu |
|---|---|
| Cần ACID | Transaction xuyên suốt |
| Team nhỏ | < 5 người |
| Domain chưa rõ | Business chưa hiểu rule |
| Dự án ngắn | < 1 năm |
| Không cần scale | Vài trăm user |
| Team chưa có kinh nghiệm | Chưa làm distributed |

---

## 4. Core Domain Chart

Đây là **công cụ phân loại** context theo **giá trị nghiệp vụ**.

### 4.1. Ba loại domain

| Loại | Đặc điểm | Đầu tư |
|---|---|---|
| **Core Domain** | Nghiệp vụ **cốt lõi**, tạo lợi thế cạnh tranh | **Nhiều nhất** |
| **Supporting Domain** | Hỗ trợ core, nhưng không phải USP | Vừa |
| **Generic Domain** | Ai cũng có, không đặc biệt | Ít — mua/outsource |

### 4.2. Sơ đồ

```
        Giá trị cao
             ▲
             │
    ┌────────┴────────┐
    │                 │
    │  CORE           │  ← Đầu tư nhiều
    │  DOMAIN         │     Team giỏi
    │                 │     DDD kỹ
    ├─────────────────┤
    │                 │
    │  SUPPORTING     │  ← Vừa
    │  DOMAIN         │     Team nội bộ
    │                 │     DDD vừa
    ├─────────────────┤
    │                 │
    │  GENERIC        │  ← Ít
    │  DOMAIN         │     Mua/outsource
    │                 │     Không DDD
    └─────────────────┘
             │
             ▼
        Giá trị thấp
```

### 4.3. Ví dụ: Ngân hàng

| Context | Loại | Lý do |
|---|---|---|
| **Account** | Core | Quản lý tài khoản là nghiệp vụ chính |
| **Transaction** | Core | Giao dịch là USP |
| **Loan** | Core | Cho vay là sản phẩm chính |
| **Card** | Supporting | Thẻ hỗ trợ core |
| **Customer** | Supporting | KYC cần thiết |
| **Fraud** | Supporting | Phát hiện gian lận |
| **Notification** | Generic | Gửi email/SMS ai cũng làm |
| **Reporting** | Generic | Báo cáo ai cũng cần |

### 4.4. Ví dụ: E-commerce

| Context | Loại | Lý do |
|---|---|---|
| **Catalog** | Core | Sản phẩm là trái tim |
| **Order** | Core | Đơn hàng là nghiệp vụ chính |
| **Pricing** | Core | Giá là yếu tố cạnh tranh |
| **Payment** | Supporting | Cần nhưng có thể dùng Stripe |
| **Shipping** | Supporting | Cần nhưng có thể dùng GHN |
| **Inventory** | Supporting | Quản lý kho |
| **Analytics** | Generic | Google Analytics |
| **Notification** | Generic | SendGrid/Twilio |

### 4.5. Chiến lược theo loại

**Core Domain:**

- Team giỏi nhất.
- Áp dụng DDD đầy đủ.
- Đầu tư nhiều thời gian.
- Tự build.

**Supporting Domain:**

- Team vừa.
- Áp dụng DDD vừa phải.
- Có thể mua một phần.
- Tự build hoặc dùng SaaS.

**Generic Domain:**

- Team nhỏ hoặc outsource.
- **Không cần DDD.**
- Mua, dùng SaaS.
- **Không tốn nguồn lực.**

### 4.6. Quy tắc ngón tay

> **Đừng dùng team giỏi cho Generic Domain.**
>
> **Đừng dùng SaaS cho Core Domain.**
>
> Nếu bạn là công ty vận tải, **logistics là Core** — đừng outsource. Nhưng **payment có thể mua Stripe**.
>
> Nếu bạn là công ty fintech, **payment là Core** — tự build. Nhưng **notification có thể mua**.

---

## 5. Conway's Law và Team Topology

### 5.1. Conway's Law

> **"Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure."**
>
> — Melvin Conway, 1967

**Ý nghĩa:** Kiến trúc hệ thống **phản ánh** cấu trúc tổ chức.

**Ví dụ:**

- Công ty có 4 team: Frontend, Backend, DBA, QA → hệ thống sẽ có 4 layer.
- Công ty có 3 team: Catalog, Order, Payment → hệ thống sẽ có 3 service.

**Ứng dụng:** Muốn hệ thống có 3 context? Tổ chức 3 team.

### 5.2. Inverse Conway Maneuver

> **Thay đổi cấu trúc team để có kiến trúc mong muốn.**

**Ví dụ:**

- Muốn hệ thống microservices?
- Tổ chức team theo context.
- Team tự chủ → tự nhiên hệ thống tách ra.

**Ngược lại:**

- Muốn monolith?
- Tổ chức team theo chức năng.
- Hoặc 1 team lớn.

### 5.3. Team Topology — 4 loại team

**1. Stream-aligned team**

- Team **end-to-end** sở hữu 1 stream công việc.
- Ví dụ: Team Order sở hữu toàn bộ Order context.
- **Đây là team chính.**

**2. Platform team**

- Cung cấp **platform** cho các team khác.
- Ví dụ: Team Infra cung cấp CI/CD, logging, monitoring.
- Giảm cognitive load cho stream-aligned.

**3. Enabling team**

- Giúp stream-aligned **nâng cao năng lực**.
- Ví dụ: Team DDD coach giúp các team khác.
- Tạm thời, không permanent.

**4. Complicated-subsystem team**

- Sở hữu subsystem **phức tạp**.
- Ví dụ: Team ML/AI, team Video Encoding.
- Cần chuyên môn sâu.

### 5.4. Áp dụng vào DDD

| Team | Context |
|---|---|
| Stream-aligned | 1-2 Bounded Context |
| Platform | Shared infrastructure |
| Enabling | DDD coaching |
| Complicated-subsystem | Core Domain phức tạp |

**Quy tắc:** **Mỗi Bounded Context = 1 team.** Không share team giữa 2 context.

---

## 6. Ba mô hình triển khai

### 6.1. Monolith

**Đặc điểm:**

- 1 codebase.
- 1 database.
- 1 deployment.
- Không có network giữa các module.

**Ưu điểm:**

- **Đơn giản** nhất.
- Không có distributed transaction.
- Không có network failure.
- Deploy 1 lần.
- Debug dễ.

**Nhược điểm:**

- Coupling cao.
- Khó scale độc lập.
- Deploy chậm khi code lớn.
- Khó cho nhiều team.

**Khi nào dùng:**

- Team < 5 người.
- Dự án < 1 năm.
- Domain chưa rõ.
- Không cần scale.

**Ví dụ:**

```
shop/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

**Tất cả trong 1 process, 1 DB.**

### 6.2. Modular Monolith

**Đặc điểm:**

- 1 codebase.
- 1 database.
- 1 deployment.
- **Nhưng có module rõ ràng.**

**Ưu điểm:**

- Tất cả ưu điểm của monolith.
- **Module boundary rõ** — dễ tách sau.
- **Không cần network.**
- **Không cần distributed transaction.**

**Nhược điểm:**

- Vẫn là 1 deployment.
- Không scale độc lập.
- Cần **kỷ luật** để giữ boundary.

**Khi nào dùng:**

- **Khuyến nghị cho 90% dự án.**
- Team 5-20 người.
- Domain rõ nhưng chưa cần microservices.
- Muốn "microservices readiness".

**Ví dụ:**

```
shop/
├── shared/
├── catalog/          # module 1
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
├── order/            # module 2
├── payment/          # module 3
└── bootstrap.py
```

**Enforce bằng `import-linter`:**

```toml
[[tool.importlinter.contracts]]
name = "Catalog độc lập"
type = "forbidden"
source_modules = ["shop.order", "shop.payment"]
forbidden_modules = ["shop.catalog.domain"]
```

**Khi cần tách → chỉ cần extract module ra service mới.**

### 6.3. Microservices

**Đặc điểm:**

- **Nhiều codebase.**
- **Nhiều database.**
- **Nhiều deployment.**
- Network giữa các service.

**Ưu điểm:**

- Team **hoàn toàn độc lập**.
- Scale **độc lập**.
- Công nghệ **riêng** cho mỗi service.
- Fault isolation.

**Nhược điểm:**

- **Phức tạp cực cao.**
- Distributed transaction.
- Network failure.
- Eventual consistency.
- Distributed tracing.
- Deployment phức tạp.
- Debug khó.

**Khi nào dùng:**

- **Chỉ khi thực sự cần.**
- Team > 20 người.
- Domain rõ ràng.
- Cần scale cực lớn.
- Team có **kinh nghiệm distributed system**.

**Ví dụ:**

```
catalog-service/     # repo 1
├── src/
├── Dockerfile
└── k8s/

order-service/       # repo 2
├── src/
├── Dockerfile
└── k8s/

payment-service/     # repo 3
├── src/
├── Dockerfile
└── k8s/
```

### 6.4. Bảng so sánh

| Tiêu chí | Monolith | Modular Monolith | Microservices |
|---|---|---|---|
| **Codebase** | 1 | 1 | N |
| **Database** | 1 | 1 | N |
| **Deployment** | 1 | 1 | N |
| **Network** | Không | Không | Có |
| **Team** | 1-5 | 5-20 | 20+ |
| **Complexity** | Thấp | Vừa | Cao |
| **Scale** | Vertical | Vertical | Horizontal |
| **Transaction** | ACID | ACID | Distributed |
| **Testing** | Dễ | Vừa | Khó |
| **Deploy** | Nhanh | Nhanh | Phức tạp |
| **Phù hợp** | MVP | 90% dự án | Big tech |

### 6.5. Khuyến nghị

> **Bắt đầu với Modular Monolith.**
>
> **Chỉ tách Microservices khi:**
> - Có **vấn đề cụ thể** cần giải quyết.
> - Team đã **đủ lớn** (>20 người).
> - Team có **kinh nghiệm** distributed system.
> - Có **hạ tầng** (Kubernetes, service mesh, observability).
>
> **Đừng tách vì "nghe nói microservices tốt".**

---

## 7. Chi phí thật của việc tách Context

Nhiều người **không nhận ra** chi phí thật. Đây là những gì bạn **mất** khi tách.

### 7.1. Network latency

**Monolith:**

```python
product = product_repo.find_by_id(product_id)   # 1ms
```

**Microservices:**

```python
product = http_client.get(f"http://catalog/products/{product_id}")   # 50-500ms
```

**→ Chậm 50-500 lần.**

### 7.2. Failure handling

**Monolith:** `find_by_id` không bao giờ fail (trừ DB sập).

**Microservices:** Network có thể fail, timeout, retry.

**→ Cần:** Circuit breaker, retry, timeout, fallback.

### 7.3. Distributed transaction

**Monolith:**

```python
with uow:
    account.withdraw(money)
    target.deposit(money)
    uow.commit()   # Atomic
```

**Microservices:** Cần Saga pattern:

```python
# Step 1: Withdraw (có thể fail)
# Step 2: Nếu fail → compensate step 1
# Step 3: Deposit (có thể fail)
# Step 4: Nếu fail → compensate step 2, 1
```

**→ Phức tạp hơn nhiều.**

### 7.4. Eventual consistency

**Monolith:** Sau khi save, query thấy ngay.

**Microservices:** Sau khi save, read model có thể chưa update.

**→ Cần handle UI**.

### 7.5. Observability

**Monolith:** 1 log file, 1 stack trace.

**Microservices:** Distributed tracing (Jaeger), centralized logging (ELK).

**→ Cần hạ tầng.**

### 7.6. Testing

**Monolith:** Unit test + integration test.

**Microservices:** + Contract test + E2E test + Chaos test.

**→ Nhiều loại test hơn.**

### 7.7. Deployment

**Monolith:** `git push` → CI/CD → deploy.

**Microservices:** Kubernetes, service mesh, rolling deployment, blue-green.

**→ Cần DevOps team.**

### 7.8. Bảng tóm tắt

| Khía cạnh | Monolith | Microservices |
|---|---|---|
| **Latency** | 1ms | 50-500ms |
| **Failure** | Hiếm | Thường |
| **Transaction** | ACID | Saga |
| **Consistency** | Strong | Eventual |
| **Observability** | Đơn giản | Distributed tracing |
| **Testing** | 2 loại | 4 loại |
| **Deploy** | Đơn giản | K8s + mesh |

---

## 8. Tám anti-pattern chiến lược

### ❌ Anti-pattern 1: Tách Microservices quá sớm

```python
# Startup 3 người, tách 10 services
# → 10 deployment, 10 DB, 10 CI/CD
# → Không ai làm được feature
```

**Fix:** Bắt đầu Modular Monolith.

### ❌ Anti-pattern 2: Distributed Monolith

```
Service A gọi Service B
Service B gọi Service C
Service C gọi Service A
```

**Vấn đề:** Microservices nhưng coupling chặt như monolith. Còn tệ hơn vì có network.

**Fix:** Xác định dependency direction rõ. Dùng event.

### ❌ Anti-pattern 3: Shared Database

```
Service A ─┐
           ├─→ Shared DB
Service B ─┘
```

**Vấn đề:** Coupling qua DB. Không thể tách thật.

**Fix:** Mỗi service có DB riêng.

### ❌ Anti-pattern 4: 1 team cho 5 context

**Vấn đề:** Team 5 người quản 5 context → context nào cũng nửa vời.

**Fix:** Gộp lại. 1 team = 1-2 context.

### ❌ Anti-pattern 5: Tách theo technical layer

```
user-service     # tất cả user logic
product-service  # tất cả product logic
order-service    # tất cả order logic
```

**Vấn đề:** Đây là **layer tách**, không phải **business tách**. Mọi feature đều cần sửa 3 service.

**Fix:** Tách theo **business capability**.

### ❌ Anti-pattern 6: Tách vì "nghe nói tốt"

**Vấn đề:** Không có vấn đề cụ thể cần giải quyết.

**Fix:** Chỉ tách khi có **lý do cụ thể** (team scale, performance, deployment).

### ❌ Anti-pattern 7: Gộp quá nhiều

```
everything-service/
├── user
├── product
├── order
├── payment
├── shipping
├── notification
├── analytics
└── ... (100 modules)
```

**Vấn đề:** 1 team 50 người quản monolith 1 triệu dòng.

**Fix:** Tách thành Modular Monolith với boundary rõ.

### ❌ Anti-pattern 8: Không có boundary

```
shop/
├── models.py     # 100 classes
├── services.py   # 500 functions
├── routes.py     # 200 routes
└── utils.py
```

**Vấn đề:** Không có module. Mọi thứ import mọi thứ.

**Fix:** Tách thành module với `import-linter`.

---

## 9. Quy trình quyết định

Đây là **quy trình** để quyết định tách/gộp.

### 9.1. Câu hỏi 1: Có mấy team?

```
1-3 team → Monolith
4-10 team → Modular Monolith
10+ team → Cân nhắc Microservices
```

### 9.2. Câu hỏi 2: Cần ACID xuyên suốt?

```
Có → Gộp (trong cùng context)
Không → Có thể tách
```

### 9.3. Câu hỏi 3: Cần scale độc lập?

```
Có → Tách
Không → Gộp
```

### 9.4. Câu hỏi 4: Team có kinh nghiệm distributed?

```
Có → Có thể Microservices
Không → Modular Monolith
```

### 9.5. Câu hỏi 5: Dự án bao lâu?

```
< 1 năm → Monolith
1-3 năm → Modular Monolith
> 3 năm → Cân nhắc Microservices
```

### 9.6. Sơ đồ quyết định

```
Bắt đầu
   │
   ▼
Team < 5 người?
   ├── Có → Monolith
   └── Không
        │
        ▼
   Cần ACID xuyên suốt?
        ├── Có → Gộp các module liên quan
        └── Không
             │
             ▼
        Team > 20 người?
             ├── Không → Modular Monolith
             └── Có
                  │
                  ▼
             Có kinh nghiệm distributed?
                  ├── Không → Modular Monolith
                  └── Có → Microservices
```

---

## 10. Ví dụ thực tế: 3 công ty

### 10.1. Startup 3 người — Monolith

**Tình huống:** 3 founder, MVP, 6 tháng.

**Quyết định:** Monolith.

**Lý do:**

- Team nhỏ.
- Cần ra nhanh.
- Chưa biết domain.
- Không cần scale.

**Cấu trúc:**

```
app/
├── models.py
├── services.py
└── routes.py
```

### 10.2. Công ty 30 người — Modular Monolith

**Tình huống:** 30 người, 5 team, 3 năm, e-commerce.

**Quyết định:** Modular Monolith.

**Lý do:**

- Team vừa.
- Domain rõ.
- Chưa cần scale cực lớn.
- Muốn "microservices readiness".

**Cấu trúc:**

```
shop/
├── shared/
├── catalog/          # team 1
├── order/            # team 2
├── payment/          # team 3
├── shipping/         # team 4
└── notification/     # team 5
```

**Enforce bằng `import-linter`.**

**Khi cần** → extract module ra service riêng.

### 10.3. Big tech 200 người — Microservices

**Tình huống:** 200 người, 20 team, 10 năm, scale 10 triệu user.

**Quyết định:** Microservices.

**Lý do:**

- Team lớn.
- Cần scale cực lớn.
- Có kinh nghiệm distributed.
- Có hạ tầng.

**Cấu trúc:**

```
catalog-service/     # repo 1
order-service/       # repo 2
payment-service/     # repo 3
shipping-service/    # repo 4
...
```

**Mỗi service:**

- Docker.
- Kubernetes.
- CI/CD riêng.
- DB riêng.
- Observability riêng.

---

## 11. Ví dụ tổng hợp: Từ Monolith → Modular Monolith → Microservices

### 11.1. Giai đoạn 1: Monolith (năm 1)

```
shop/
├── models.py
├── services.py
└── routes.py
```

**Team:** 5 người.

### 11.2. Giai đoạn 2: Modular Monolith (năm 2)

```
shop/
├── shared/
├── catalog/
├── order/
├── payment/
└── notification/
```

**Team:** 15 người, 3 team.

**Enforce boundary bằng `import-linter`.**

### 11.3. Giai đoạn 3: Extract 1 service (năm 3)

**Khi nào?** Khi Catalog cần scale độc lập, hoặc team Catalog muốn deploy độc lập.

```
catalog-service/     # repo mới, extract từ shop/catalog
shop/                # còn lại
├── shared/
├── order/
├── payment/
└── notification/
```

**Giao tiếp:** Order gọi Catalog qua HTTP hoặc event.

### 11.4. Giai đoạn 4: Full Microservices (năm 5)

Khi **thực sự cần**:

```
catalog-service/
order-service/
payment-service/
shipping-service/
notification-service/
```

**Team:** 50+ người.

---

## 12. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Phân loại Core/Supporting/Generic

Cho hệ thống **"ứng dụng giao đồ ăn"** với các context:

- Restaurant (nhà hàng)
- Menu (thực đơn)
- Order (đơn hàng)
- Delivery (giao hàng)
- Payment (thanh toán)
- Driver (tài xế)
- Rating (đánh giá)
- Notification (thông báo)

Yêu cầu:

1. Phân loại mỗi context thành Core/Supporting/Generic.
2. Giải thích lý do.
3. Đề xuất chiến lược đầu tư cho mỗi loại.

### 🟡 Bài tập 2 (trung bình): Quyết định tách/gộp

Cho hệ thống **"quản lý trường học"** với các module hiện tại:

- Student (học sinh)
- Teacher (giáo viên)
- Class (lớp học)
- Grade (điểm)
- Attendance (điểm danh)
- Tuition (học phí)
- Notification (thông báo)

**Bối cảnh:**

- Team 8 người.
- Dự án 2 năm.
- 5000 học sinh.
- Cần ACID cho tuition.

Yêu cầu:

1. Quyết định tách/gộp từng module.
2. Đề xuất mô hình triển khai (Monolith / Modular Monolith / Microservices).
3. Vẽ sơ đồ cấu trúc.
4. Giải thích trade-off.

### 🔴 Bài tập 3 (khó): Chiến lược cho Startup → Scale

Bạn là CTO của một startup fintech:

- **Năm 1:** 5 người, MVP, 1000 user.
- **Năm 3:** 30 người, 100k user.
- **Năm 5:** 200 người, 10 triệu user.

Yêu cầu:

1. Đề xuất mô hình triển khai cho **mỗi năm**.
2. Khi nào tách service đầu tiên? Service nào?
3. Khi nào full microservices?
4. Vẽ sơ đồ cấu trúc cho mỗi giai đoạn.
5. Giải thích tại sao **không** tách sớm.
6. Viết 1 file `strategy.md` với:
   - Timeline.
   - Trigger events (khi nào tách).
   - Risks.
   - Team topology.

Bonus: Đọc case study của **Shopify** (modular monolith) và **Amazon** (microservices) — so sánh.

---

## 13. Checklist sau bài 16

Trước khi sang Level 5, bạn phải tự tin trả lời:

- [ ] Chiến lược chọn Bounded Context là gì?
- [ ] 7 tiêu chí tách context?
- [ ] 6 tiêu chí gộp context?
- [ ] Core/Supporting/Generic Domain — khác nhau thế nào?
- [ ] Chiến lược đầu tư cho mỗi loại domain?
- [ ] Conway's Law là gì? Áp dụng thế nào?
- [ ] Team topology — 4 loại team?
- [ ] Monolith vs Modular Monolith vs Microservices?
- [ ] Khi nào dùng mô hình nào?
- [ ] Chi phí thật của việc tách context?
- [ ] 8 anti-pattern chiến lược?
- [ ] Quy trình quyết định tách/gộp?

Nếu trả lời được hết, bạn đã hoàn thành Level 4 và sẵn sàng cho Level 5.

---

## 14. Tóm tắt bài 16

| Điểm | Nội dung |
|---|---|
| **Chiến lược** | Quyết định tách/gộp context |
| **7 tiêu chí tách** | Cùng từ khác nghĩa, team khác, tốc độ, NFR, complexity, boundary, eventual |
| **6 tiêu chí gộp** | ACID, team nhỏ, domain chưa rõ, dự án ngắn, không scale, team chưa có KN |
| **Core Domain** | Nghiệp vụ cốt lõi, đầu tư nhiều |
| **Supporting** | Hỗ trợ, đầu tư vừa |
| **Generic** | Mua/outsource, không DDD |
| **Conway's Law** | Kiến trúc phản ánh tổ chức |
| **Team Topology** | Stream-aligned, Platform, Enabling, Complicated-subsystem |
| **Monolith** | 1 codebase, 1 DB, đơn giản |
| **Modular Monolith** | 1 codebase, module rõ — **khuyến nghị 90%** |
| **Microservices** | N codebase, N DB, phức tạp |
| **Chi phí tách** | Network, failure, distributed tx, eventual, observability |
| **8 anti-pattern** | Tách sớm, distributed monolith, shared DB, 1 team 5 context, tách theo layer, tách vì "nghe nói", gộp quá nhiều, không boundary |

**Câu thần chú:** *"Bắt đầu đơn giản. Tách khi có lý do cụ thể. Modular Monolith là mặc định tốt nhất."*

---

## 15. Chúc mừng — Bạn đã hoàn thành Level 4!

Level 4 gồm 3 bài:

- **Bài 14:** Context Mapping — quan hệ giữa các context.
- **Bài 15:** Event Storming — khám phá domain cùng business.
- **Bài 16:** Chiến lược chọn Bounded Context — tách/gộp.

Giờ bạn đã có đủ công cụ **strategic DDD** để thiết kế **hệ thống lớn**.

---

## 16. Chuẩn bị cho Level 5 — Chuyên sâu

Level 5 gồm 2 bài:

- **Bài 17:** Event Sourcing — lưu state dưới dạng chuỗi event.
- **Bài 18:** DDD + FastAPI + SQLAlchemy — project hoàn chỉnh.

Level 5 là **chuyên sâu** — dành cho ai muốn hiểu sâu và áp dụng thực tế.

Chuẩn bị:

- Đọc lại bài 8 (Domain Event).
- Nghĩ về **audit log** — bạn có cần không?
- Sẽ bàn: Event Sourcing là gì, Event Store, replay, snapshot, và khi nào dùng.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 17** (Event Sourcing) — bắt đầu Level 5.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: Team Topology, Conway's Law, case study Shopify/Amazon.
5. **Tư vấn chiến lược** cho hệ thống của bạn — nếu bạn mô tả hệ thống, tôi sẽ đề xuất.

Nói tôi biết bạn muốn gì nhé.