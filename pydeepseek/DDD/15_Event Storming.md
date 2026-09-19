# 📖 Bài 15: Event Storming — Khám phá domain cùng business

> Đây là bài **thực tế nhất** của cả lộ trình. Không code, không framework — chỉ có **giấy, bút, sticky notes, và con người**. Event Storming là kỹ thuật **khám phá domain** cùng business, biến kiến thức **trong đầu chuyên gia** thành **bản đồ sự kiện** trên tường. Nếu bạn chỉ học được 1 kỹ thuật từ khóa DDD này, hãy học cái này.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Event Storming** là gì và tại sao nó là **kỹ thuật mạnh nhất** của DDD.
2. Biết **ai tham gia**, **chuẩn bị gì**, **bao lâu**.
3. Nắm **3 cấp độ**: Big Picture, Process Level, Design Level.
4. Biết **9 loại sticky notes** và cách dùng.
5. Biết **quy trình chạy workshop** từ A→Z.
6. Áp dụng vào **1 domain thực tế** (ví dụ đặt vé xem phim).
7. Biết **các lỗi thường gặp** khi chạy Event Storming.
8. Làm bài tập thực hành có chấm điểm.

---

## 1. Event Storming là gì?

### 1.1. Định nghĩa

> **Event Storming** là một **workshop** khám phá domain, trong đó **tất cả các bên liên quan** (business, dev, QA, product) cùng nhau **dán sticky notes** lên tường để mô hình hóa **dòng chảy sự kiện** trong nghiệp vụ.

Được sáng tạo bởi **Alberto Brandolini** năm 2012.

### 1.2. Trực giác

Hãy tưởng tượng bạn cần xây một **thành phố**.

**Cách 1 (Sai):** Architect ngồi một mình, vẽ bản đồ, rồi đưa cho đội xây dựng. Kết quả: xây xong, dân không thích, đường không khớp với nhu cầu.

**Cách 2 (Đúng — Event Storming):** Tất cả các bên (dân, kiến trúc sư, kỹ sư, cảnh sát, bác sĩ, giáo viên) cùng ngồi lại, dán giấy lên tường, vẽ thành phố **cùng nhau**. Kết quả: ai cũng hiểu, ai cũng có tiếng nói.

Event Storming = Cách 2.

### 1.3. Tại sao hiệu quả?

| Lý do | Giải thích |
|---|---|
| **Phá bỏ silo** | Business + Dev + QA ngồi cùng |
| **Trực quan** | Sticky notes dễ hiểu hơn tài liệu |
| **Nhanh** | Trong 1-2 ngày hiểu domain mà đọc spec mất vài tuần |
| **Toàn diện** | Nhìn thấy flow end-to-end |
| **Phát hiện gap** | Chỗ nào chưa hiểu → lộ ra ngay |
| **Đồng thuận** | Mọi người cùng xây, cùng hiểu |

### 1.4. Ai sáng tạo?

**Alberto Brandolini** — người Ý, DDD practitioner. Năm 2012, ông chạy workshop đầu tiên cho một dự án, và nhận ra rằng **dán giấy** hiệu quả hơn mọi công cụ vẽ UML.

Ngày nay, Event Storming được dùng rộng rãi ở các công ty lớn: Netflix, Uber, Spotify.

---

## 2. Ai tham gia? Chuẩn bị gì?

### 2.1. Người tham gia

| Vai trò | Vai trò trong workshop |
|---|---|
| **Domain Expert** | Người hiểu nghiệp vụ nhất (không nhất thiết là manager) |
| **Business Analyst** | Cầu nối giữa business và dev |
| **Developer** | Người sẽ implement |
| **QA/Tester** | Người sẽ test |
| **Product Owner** | Người quyết định ưu tiên |
| **Facilitator** | Người điều phối (rất quan trọng!) |
| **Scribe** | Người ghi chú lại (nếu cần) |

**Số lượng lý tưởng:** 5-10 người. Nhiều hơn → loạn. Ít hơn → thiếu góc nhìn.

### 2.2. Chuẩn bị

**Vật dụng:**

- **Tường dài** — càng dài càng tốt (5-10 mét).
- **Giấy A0** dán lên tường làm nền.
- **Sticky notes** nhiều màu: vàng, cam, hồng, xanh, tím, đỏ, xanh lá.
- **Bút marker** đen, đỏ, xanh.
- **Băng keo**, kéo.
- **Nước uống, snack** (workshop dài).

**Không gian:**

- Phòng rộng, có tường trống.
- Không có bàn chắn giữa người và tường.
- Ghế di động hoặc đứng tự do.

**Thời gian:**

- **Big Picture:** 2-4 giờ.
- **Process Level:** 1-2 ngày.
- **Design Level:** 1-2 ngày.

**Tần suất:** 1-2 lần cho mỗi dự án. Không cần lặp lại liên tục.

### 2.3. Vai trò Facilitator

Đây là **vai trò quan trọng nhất**.

**Trách nhiệm:**

- Giữ workshop **đúng hướng**.
- Khuyến khích **mọi người** nói (không để 1 người dominate).
- **Không đưa ý kiến** của bản thân.
- Ghi lại **câu hỏi mở** (chưa trả lời được).
- Quản lý **thời gian**.
- Xử lý **conflict** giữa các bên.

**Facilitator tốt = workshop thành công.**

---

## 3. Chín loại sticky notes

Đây là **bộ từ vựng** của Event Storming. Mỗi màu = 1 loại khái niệm.

| # | Màu | Tên | Ý nghĩa | Ví dụ |
|---|---|---|---|---|
| 1 | 🟧 Cam | **Domain Event** | Chuyện đã xảy ra | `Order Placed` |
| 2 | 🟦 Xanh dương | **Command** | Hành động gây event | `Place Order` |
| 3 | 🟨 Vàng | **Aggregate** | Đối tượng xử lý command | `Order` |
| 4 | 🟪 Tím | **Policy** | "Khi X thì Y" | "Khi Order Placed → Reserve Stock" |
| 5 | 🟩 Xanh lá | **Read Model** | Dữ liệu cần để ra quyết định | `Order Summary` |
| 6 | 🟫 Nâu | **Actor** | Người/hệ thống gây command | `Customer`, `Admin` |
| 7 | 🟥 Đỏ | **Hotspot** | Vấn đề, mâu thuẫn, câu hỏi | "Không rõ rule giảm giá" |
| 8 | ⬜ Trắng | **External System** | Hệ thống ngoài | `Payment Gateway` |
| 9 | 🟦 Xanh dương nhạt | **User** | End user | (thường gộp với Actor) |

**Quy tắc vàng:**

> **Domain Event (cam) là xương sống.** Bắt đầu từ đó. Các loại khác gắn vào sau.

---

## 4. Ba cấp độ Event Storming

Event Storming có **3 cấp độ**, từ vĩ mô đến vi mô.

### 4.1. Big Picture — Bức tranh lớn

**Mục tiêu:** Hiểu **toàn cảnh** nghiệp vụ, không đi vào chi tiết.

**Đối tượng:** Cả business + dev + QA.

**Thời gian:** 2-4 giờ.

**Chỉ dùng:**

- 🟧 Domain Event (cam)
- 🟥 Hotspot (đỏ)
- 🟪 Policy (tím)
- 🟫 Actor (nâu)

**Output:** Dòng chảy sự kiện từ đầu đến cuối, các hotspot cần giải quyết.

**Quy trình:**

1. **Chaotic Exploration** (30 phút): Mọi người viết **mọi event** nghĩ ra, dán lung tung lên tường.
2. **Timeline** (60 phút): Sắp xếp theo **thứ tự thời gian** từ trái sang phải.
3. **Enforce the Story** (30 phút): Kiểm tra logic, phát hiện gap.
4. **Identify Boundaries** (30 phút): Xác định Bounded Context sơ bộ.
5. **Review Hotspots** (30 phút): Xem lại các điểm chưa rõ.

### 4.2. Process Level — Cấp quy trình

**Mục tiêu:** Hiểu **chi tiết** từng process.

**Đối tượng:** Ít người hơn, tập trung vào 1 process.

**Thời gian:** 1-2 ngày.

**Thêm:**

- 🟦 Command (xanh)
- 🟩 Read Model (xanh lá)
- ⬜ External System (trắng)

**Output:** Process hoàn chỉnh với command, read model, policy.

**Quy trình:**

1. Chọn **1 process** (ví dụ: Place Order).
2. Xác định **Command → Aggregate → Event**.
3. Thêm **Read Model** cần để ra quyết định.
4. Thêm **Policy** ("Khi X thì Y").
5. Xác định **External System**.

### 4.3. Design Level — Cấp thiết kế

**Mục tiêu:** Chuẩn bị **implement**.

**Đối tượng:** Chủ yếu dev.

**Thời gian:** 1-2 ngày.

**Thêm:**

- 🟨 Aggregate (vàng)
- Chi tiết field, invariant, API.

**Output:** Thiết kế chi tiết Aggregate, Repository, API.

**Quy trình:**

1. Với mỗi Aggregate, xác định:
   - **Invariant** cần bảo vệ.
   - **Command** nào được chấp nhận.
   - **Event** nào được phát.
2. Vẽ **interface** giữa các Aggregate.
3. Xác định **Repository** cần.
4. Xác định **event bus** cần.

> 💡 **Lưu ý:** Đừng đi thẳng vào Design Level. **Luôn bắt đầu từ Big Picture.**

---

## 5. Quy trình chạy Event Storming

Đây là **quy trình chi tiết** cho 1 buổi Big Picture (phổ biến nhất).

### 5.1. Chuẩn bị phòng (30 phút trước)

- Dán giấy A0 lên tường (5-10m).
- Đặt sticky notes ở giữa phòng.
- Bút marker cho mọi người.
- Nước uống.

### 5.2. Giới thiệu (15 phút)

Facilitator:

- Giải thích **mục tiêu**.
- Giải thích **9 loại notes** (chỉ giới thiệu cam, đỏ, tím, nâu).
- Đặt **luật chơi:**
  - Không có ý kiến sai.
  - Viết to, rõ.
  - Không tranh luận dài — có hotspot thì dán đỏ.
  - Mọi người đều viết.

### 5.3. Chaotic Exploration (30-45 phút)

- Mọi người viết **mọi event** nghĩ ra (🟧 cam).
- Dán **lung tung** lên tường.
- **Chưa cần sắp xếp.**
- Facilitator **không can thiệp**, chỉ nhắc mọi người viết nhiều.
- Mục tiêu: **càng nhiều càng tốt** (100-200 notes).

**Ví dụ event trong domain đặt vé:**

- `Movie Added`
- `Screening Scheduled`
- `Ticket Reserved`
- `Payment Completed`
- `Ticket Issued`
- `Screening Cancelled`
- `Refund Processed`
- ...

### 5.4. Timeline (60-90 phút)

- Cả nhóm **sắp xếp** events theo thời gian.
- Từ **trái** (sự kiện đầu) sang **phải** (sự kiện cuối).
- **Bắt đầu** với events rõ ràng nhất.
- **Dán** lại lên tường theo hàng ngang.
- Facilitator hỏi: "Event này xảy ra trước hay sau event kia?"

**Output:** 1 hàng dài events theo timeline.

### 5.5. Enforce the Story (30-45 phút)

- Đi từ **trái sang phải**, kể lại câu chuyện.
- Hỏi: "Điều gì xảy ra tiếp theo?"
- **Phát hiện gap:** "Chỗ này không có event nào?"
- **Thêm** event còn thiếu.
- **Xóa** event dư thừa.

**Ví dụ:**

> "Screening Scheduled → Ticket Reserved → ... → Payment Completed? À, chỗ này có event gì khi user chưa thanh toán trong 15 phút? → `Reservation Expired`."

### 5.6. Identify Pivotal Events (30 phút)

**Pivotal Event** = sự kiện **quan trọng** chia flow thành các phase.

Đánh dấu bằng **sticky lớn** hoặc **đánh dấu đặc biệt**.

**Ví dụ trong đặt vé:**

- `Ticket Reserved` — pivotal, bắt đầu quá trình giữ chỗ.
- `Payment Completed` — pivotal, chốt đơn.
- `Ticket Issued` — pivotal, hoàn tất.

**Insight:** Pivotal events thường trở thành **Aggregate** hoặc **Bounded Context** boundary.

### 5.7. Add Actors (20 phút)

- 🟫 Actor (nâu): ai gây ra command/event?
- Dán lên trên events liên quan.
- **Ví dụ:**
  - `Customer` → `Ticket Reserved`.
  - `Admin` → `Screening Scheduled`.
  - `System` → `Reservation Expired`.

### 5.8. Add Policies (30 phút)

- 🟪 Policy (tím): "Khi X thì Y".
- Dán **giữa 2 events**.
- **Ví dụ:**
  - "Khi `Payment Completed` → gửi email xác nhận".
  - "Khi `Reservation Expired` → release ghế".
  - "Khi `Screening Cancelled` → hoàn tiền".

### 5.9. Add Hotspots (20 phút)

- 🟥 Hotspot (đỏ): vấn đề, câu hỏi, mâu thuẫn.
- Facilitator **ghi lại** trong "parking lot".
- **Không giải quyết ngay** — để sau.
- **Ví dụ:**
  - "Không rõ policy hoàn tiền khi cancel vé" (business chưa quyết).
  - "Ghế đặt nhưng không thanh toán — có giữ không?" (cần rule).
  - "Nếu 2 người cùng đặt 1 ghế thì sao?" (concurrency).

### 5.10. Identify Bounded Contexts (30 phút)

- Vẽ **đường thẳng đứng** phân chia events thành các nhóm.
- Mỗi nhóm ≈ 1 Bounded Context.
- **Ví dụ:**
  - `Movies`, `Cinemas`, `Showtimes` → **Catalog Context**.
  - `Ticket Reserved`, `Payment Completed` → **Booking Context**.
  - `Refund Processed` → **Payment Context**.
  - `Email Sent` → **Notification Context**.

### 5.11. Review & Wrap-up (30 phút)

- Đọc lại **toàn bộ câu chuyện**.
- Xem lại **hotspots**.
- Xác định **next steps**:
  - Hotspots nào cần giải quyết?
  - Context nào cần vẽ chi tiết hơn?
  - Ai chịu trách nhiệm gì?
- Chụp **ảnh** bức tường.

---

## 6. Ví dụ đầy đủ: Đặt vé xem phim

Hãy tưởng tượng chúng ta chạy Event Storming cho hệ thống đặt vé xem phim.

### 6.1. Chaotic Exploration (120 events)

Một số events mọi người viết ra:

- Movie Added, Movie Updated, Movie Removed
- Cinema Added, Room Added, Seat Created
- Screening Scheduled, Screening Cancelled, Screening Started
- Customer Registered, Customer Logged In
- Ticket Reserved, Ticket Hold Expired, Ticket Released
- Payment Initiated, Payment Completed, Payment Failed
- Ticket Issued, Ticket Cancelled, Ticket Refunded
- Email Sent, SMS Sent, Push Notification Sent
- CheckIn Completed, Movie Started, Movie Ended

### 6.2. Timeline

```
Movie Added → Cinema Added → Room Added → Seat Created
    → Screening Scheduled → Customer Registered → Ticket Reserved
    → Payment Initiated → Payment Completed → Ticket Issued
    → CheckIn Completed → Movie Started → Movie Ended
```

### 6.3. Pivotal Events

- **`Screening Scheduled`** — phim sẵn sàng để đặt vé.
- **`Ticket Reserved`** — khách giữ ghế (15 phút).
- **`Payment Completed`** — thanh toán thành công, chốt đơn.
- **`Ticket Issued`** — vé được phát hành.
- **`CheckIn Completed`** — khách đã vào rạp.

### 6.4. Actors

- **Admin** → Movie Added, Screening Scheduled.
- **Customer** → Ticket Reserved, Payment Initiated.
- **System** → Ticket Hold Expired, Ticket Released.
- **Payment Gateway** (external) → Payment Completed, Payment Failed.
- **Staff** → CheckIn Completed.

### 6.5. Policies

- "Khi `Ticket Reserved` → set timer 15 phút".
- "Khi `Ticket Hold Expired` → release ghế".
- "Khi `Payment Completed` → issue ticket".
- "Khi `Payment Failed` → release ghế sau 5 phút".
- "Khi `Ticket Issued` → gửi email".
- "Khi `Screening Cancelled` → refund tất cả tickets".

### 6.6. Hotspots

- 🟥 "Nếu khách đặt 2 ghế cùng lúc bởi 2 browser, chuyện gì xảy ra?" — cần concurrency rule.
- 🟥 "Payment fail thì khách có bị mất phí không?" — business chưa quyết.
- 🟥 "Khách có thể cancel sau khi Ticket Issued không?" — cần policy.
- 🟥 "Refund mất bao lâu?" — SLA chưa rõ.
- 🟥 "Có cho đặt ghế VIP không?" — feature chưa có.

### 6.7. Bounded Contexts

Sau khi vẽ đường phân chia:

```
┌───────────────┬──────────────┬──────────────┬───────────────┐
│   Catalog     │   Booking    │   Payment    │ Notification  │
├───────────────┼──────────────┼──────────────┼───────────────┤
│ Movie Added   │ Ticket       │ Payment      │ Email Sent    │
│ Cinema Added  │   Reserved   │   Initiated  │ SMS Sent      │
│ Screening     │ Ticket Hold  │ Payment      │ Push Sent     │
│   Scheduled   │   Expired    │   Completed  │               │
│               │ Ticket       │ Payment      │               │
│               │   Issued     │   Failed     │               │
│               │ Ticket       │ Refund       │               │
│               │   Cancelled  │   Processed  │               │
└───────────────┴──────────────┴──────────────┴───────────────┘
```

### 6.8. Output cuối cùng

**Câu chuyện hoàn chỉnh:**

> Admin thêm phim (`Movie Added`). Hệ thống tạo rạp, phòng, ghế. Admin lên lịch chiếu (`Screening Scheduled`). Khách đăng ký (`Customer Registered`), chọn ghế, giữ chỗ (`Ticket Reserved`). Hệ thống set timer 15 phút. Khách thanh toán (`Payment Initiated` → `Payment Completed`). Hệ thống phát hành vé (`Ticket Issued`) và gửi email. Khách đến rạp, staff check-in (`CheckIn Completed`).

**Nếu khách không thanh toán 15 phút** → `Ticket Hold Expired` → release ghế.
**Nếu thanh toán fail** → `Payment Failed` → release ghế sau 5 phút.
**Nếu admin cancel suất chiếu** → `Screening Cancelled` → refund tất cả.

---

## 7. Ví dụ thực tế: Workshop 1 ngày

### 7.1. Timeline buổi workshop

| Thời gian | Hoạt động | Output |
|---|---|---|
| 8:30 - 9:00 | Setup + Giới thiệu | Mọi người hiểu mục tiêu |
| 9:00 - 10:00 | Chaotic Exploration | 100-200 events thô |
| 10:00 - 10:15 | Nghỉ | — |
| 10:15 - 12:00 | Timeline | Events theo thứ tự |
| 12:00 - 13:00 | Ăn trưa | — |
| 13:00 - 14:00 | Enforce Story | Câu chuyện hoàn chỉnh |
| 14:00 - 15:00 | Pivotal + Actor + Policy | Context rõ |
| 15:00 - 15:15 | Nghỉ | — |
| 15:15 - 16:00 | Hotspots + Boundaries | Context Map sơ bộ |
| 16:00 - 16:30 | Review + Wrap-up | Next steps |

### 7.2. Ai làm gì?

**Facilitator:**

- Đặt câu hỏi mở.
- Đảm bảo mọi người tham gia.
- Ghi hotspot.
- Giữ thời gian.

**Domain Expert:**

- Kể câu chuyện.
- Trả lời câu hỏi.
- Xác nhận event đúng/sai.

**Developer:**

- Viết event (đôi khi không biết tên đúng).
- Đặt câu hỏi kỹ thuật.
- Bắt đầu nghĩ về Aggregate.

**QA:**

- Đặt câu hỏi edge case.
- Phát hiện gap.
- Bắt đầu nghĩ về test case.

**Product Owner:**

- Quyết định ưu tiên.
- Trả lời câu hỏi business.
- Xác định scope.

---

## 8. Tám lỗi thường gặp khi chạy Event Storming

### ❌ Lỗi 1: Không có Domain Expert

**Triệu chứng:** Workshop chỉ có dev, business không đến.

**Hậu quả:** Dev đoán mò, output sai.

**Fix:** Đảm bảo có ít nhất 1 domain expert. Nếu không có, **hoãn workshop**.

### ❌ Lỗi 2: Không có Facilitator

**Triệu chứng:** 1 người dominate, người khác im lặng.

**Hậu quả:** Workshop thành buổi thuyết trình.

**Fix:** Facilitator riêng, không phải dev trưởng nhóm.

### ❌ Lỗi 3: Đi thẳng vào Design Level

**Triệu chứng:** Bắt đầu với "Aggregate là gì?" thay vì "Event nào xảy ra?"

**Hậu quả:** Bỏ qua context, thiết kế sai.

**Fix:** Luôn bắt đầu Big Picture.

### ❌ Lỗi 4: Không dùng sticky note

**Triệu chứng:** Dùng bảng trắng, phần mềm vẽ.

**Hậu quả:** Mất tính vật lý, mất collaboration.

**Fix:** Bắt buộc sticky + tường.

### ❌ Lỗi 5: Tranh luận quá lâu

**Triệu chứng:** 2 người tranh luận 30 phút về 1 event.

**Hậu quả:** Workshop chậm, mất năng lượng.

**Fix:** Dán hotspot đỏ, "parking lot", tiếp tục.

### ❌ Lỗi 6: Cố giải quyết hotspot ngay

**Triệu chứng:** Dừng workshop để giải quyết mâu thuẫn.

**Hậu quả:** Không hoàn thành Big Picture.

**Fix:** Ghi hotspot, giải quyết sau workshop.

### ❌ Lỗi 7: Không chụp ảnh

**Triệu chứng:** Xong workshop, không có record.

**Hậu quả:** Mất output, phải làm lại.

**Fix:** Chụp ảnh từng phần, note lại context, viết summary.

### ❌ Lỗi 8: Chỉ làm 1 lần

**Triệu chứng:** Event Storming chỉ chạy 1 lần cho cả dự án.

**Hậu quả:** Domain thay đổi → không ai update.

**Fix:** Chạy lại khi có thay đổi lớn (mỗi 3-6 tháng).

---

## 9. Áp dụng vào Python: Từ Event Storming đến code

Event Storming **trực tiếp** map sang code.

### 9.1. Mapping

| Sticky note | Code tương ứng |
|---|---|
| 🟧 Domain Event | `@dataclass(frozen=True) class OrderPlaced(DomainEvent)` |
| 🟦 Command | `@dataclass(frozen=True) class PlaceOrderCommand` |
| 🟨 Aggregate | `@dataclass(eq=False) class Order` |
| 🟪 Policy | Event handler |
| 🟩 Read Model | DTO / Query |
| 🟫 Actor | (không có code) |

### 9.2. Ví dụ: Đặt vé xem phim

**Event Storming output:**

```
Actor: Customer
  │
  │ Command: Reserve Ticket
  ▼
Aggregate: Booking
  │
  │ Event: TicketReserved
  ▼
Policy: "Khi Ticket Reserved → set timer 15 phút"
  │
  │ Command: Expire Hold
  ▼
Event: TicketHoldExpired
```

**Code Python:**

```python
# domain/model/booking.py
@dataclass(eq=False)
class Booking:
    """Aggregate từ Event Storming."""
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)   # type: ignore
    screening_id: UUID = field(default=None)   # type: ignore
    seats: list[Seat] = field(default_factory=list)
    _status: BookingStatus = BookingStatus.DRAFT
    _hold_expires_at: datetime | None = None
    _events: list = field(default_factory=list, repr=False)

    @classmethod
    def reserve(
        cls,
        customer_id: UUID,
        screening_id: UUID,
        seats: list[Seat],
    ) -> "Booking":
        if not seats:
            raise NoSeatsSelected()
        if len(seats) > 8:
            raise TooManySeats()

        booking = cls(
            customer_id=customer_id,
            screening_id=screening_id,
            seats=seats,
            _status=BookingStatus.RESERVED,
            _hold_expires_at=datetime.now() + timedelta(minutes=15),
        )
        booking._events.append(
            TicketReserved(
                booking_id=booking.id,
                customer_id=customer_id,
                screening_id=screening_id,
                seat_ids=[s.id for s in seats],
                expires_at=booking._hold_expires_at,
            )
        )
        return booking

    def expire_hold(self) -> None:
        if self._status != BookingStatus.RESERVED:
            raise InvalidOperation()
        if not self._is_hold_expired():
            raise HoldNotExpired()
        self._status = BookingStatus.EXPIRED
        self._events.append(
            TicketHoldExpired(booking_id=self.id)
        )

    def confirm_payment(self, payment: Money) -> None:
        if self._status != BookingStatus.RESERVED:
            raise BookingNotReserved()
        if self._is_hold_expired():
            raise BookingExpired()
        self._status = BookingStatus.PAID
        self._events.append(
            PaymentCompleted(
                booking_id=self.id,
                amount=payment,
            )
        )

    def _is_hold_expired(self) -> bool:
        return (
            self._hold_expires_at is not None
            and datetime.now() > self._hold_expires_at
        )


# application/commands/reserve_ticket.py
@dataclass(frozen=True)
class ReserveTicketCommand:
    customer_id: UUID
    screening_id: UUID
    seat_ids: list[UUID]


class ReserveTicketHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: ReserveTicketCommand) -> UUID:
        with self._uow:
            screening = self._uow.screenings.find_by_id(cmd.screening_id)
            if not screening:
                raise ScreeningNotFound()

            for seat_id in cmd.seat_ids:
                if screening.is_seat_taken(seat_id):
                    raise SeatAlreadyTaken(seat_id)

            seats = [screening.get_seat(sid) for sid in cmd.seat_ids]
            booking = Booking.reserve(
                customer_id=cmd.customer_id,
                screening_id=cmd.screening_id,
                seats=seats,
            )

            self._uow.bookings.save(booking)
            self._uow.commit()
        return booking.id


# application/handlers/on_ticket_reserved.py
class ScheduleHoldExpiry:
    """Policy: Khi Ticket Reserved → schedule expire."""

    def __init__(self, scheduler) -> None:
        self._scheduler = scheduler

    def handle(self, event: TicketReserved) -> None:
        self._scheduler.schedule(
            task="expire_hold",
            args={"booking_id": event.booking_id},
            at=event.expires_at,
        )
```

**Điểm mấu chốt:** Mỗi sticky note trở thành **1 class/function** trong code. **Không có gì bị mất.**

### 9.3. Lợi ích

- **Business hiểu code** — vì code dùng cùng ngôn ngữ.
- **Dev hiểu business** — vì đã tham gia workshop.
- **Không đoán mò** — rule được business confirm.
- **Test case rõ** — mỗi event = 1 test case.

---

## 10. Biến thể: Software Design Level

Sau khi có Big Picture và Process Level, có thể chạy **Software Design Level** (còn gọi là **Aggregate Design Canvas**).

### 10.1. Mục tiêu

Thiết kế chi tiết **Aggregate** cho từng Bounded Context.

### 10.2. Canvas cho mỗi Aggregate

```
┌──────────────────────────────────────────────────────────┐
│  Aggregate: Order                                        │
├──────────────────────────────────────────────────────────┤
│  Commands:          │  Events:                           │
│  - Place Order      │  - Order Placed                    │
│  - Cancel Order     │  - Order Shipped                   │
│  - Ship Order       │  - Order Cancelled                 │
├─────────────────────┼────────────────────────────────────┤
│  Invariants:        │  Actors:                           │
│  - Max 100 lines    │  - Customer                        │
│  - Total = sum      │  - Admin                           │
│  - Not empty when   │                                    │
│    placed           │                                    │
├─────────────────────┼────────────────────────────────────┤
│  Read Models:       │  External Systems:                 │
│  - Order Summary    │  - Payment Gateway                 │
│  - Order Detail     │  - Shipping Provider               │
└─────────────────────┴────────────────────────────────────┘
```

### 10.3. Ví dụ

```python
# Từ canvas → code

@dataclass(eq=False)
class Order:
    # Commands → methods
    def place(self) -> None: ...
    def cancel(self, reason: str) -> None: ...
    def ship(self, tracking: str) -> None: ...

    # Events → phát ra
    # Invariants → validate
    # Read models → DTO
    # External systems → Ports
```

---

## 11. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Event Storming trên giấy

Chọn domain: **"Quản lý thư viện"**.

Yêu cầu:

1. Viết **30-50 events** trên giấy (sticky note thật hoặc dùng Excel).
2. Sắp xếp theo timeline.
3. Xác định **3-5 pivotal events**.
4. Thêm **actors**, **policies**.
5. Liệt kê **5 hotspots**.

Viết ra file Markdown:

- Danh sách events.
- Câu chuyện hoàn chỉnh.
- Hotspots.

### 🟡 Bài tập 2 (trung bình): Process Level cho 1 process

Chọn 1 process trong domain **"Đặt hàng"**:

**Place Order Process**

Yêu cầu:

1. Viết **Commands** (xanh).
2. Viết **Events** (cam).
3. Xác định **Aggregates** (vàng).
4. Thêm **Read Models** (xanh lá).
5. Thêm **Policies** (tím).
6. Vẽ sơ đồ:
   ```
   Actor → Command → Aggregate → Event → Policy → Command → ...
   ```

Viết ra file Markdown với sơ đồ Mermaid.

### 🔴 Bài tập 3 (khó): Full Event Storming → Code

Chọn domain: **"Đặt vé máy bay"**.

Yêu cầu:

1. **Big Picture:** 100+ events, timeline, pivotal, hotspots.
2. **Process Level:** chi tiết 2-3 process (Search Flight, Book Flight, Cancel Booking).
3. **Design Level:** Aggregate canvas cho 3-4 aggregates.
4. **Code Python:** implement 3-4 aggregates với đầy đủ:
   - Commands
   - Events
   - Invariants
   - Domain Services (nếu cần)
5. **Test:** ít nhất 25 test.

Viết ra:
- File `event-storming.md` chứa toàn bộ output.
- Project Python với cấu trúc DDD.
- Test suite.

---

## 12. Checklist sau bài 15

Trước khi sang bài 16, bạn phải tự tin trả lời:

- [ ] Event Storming là gì? Ai sáng tạo?
- [ ] Ai nên tham gia workshop?
- [ ] 9 loại sticky notes là gì?
- [ ] 3 cấp độ Event Storming?
- [ ] Quy trình chạy Big Picture?
- [ ] Pivotal Event là gì?
- [ ] Hotspot là gì? Xử lý thế nào?
- [ ] Vai trò Facilitator?
- [ ] 8 lỗi thường gặp?
- [ ] Mapping giữa sticky note và code Python?
- [ ] Software Design Level là gì?

Nếu trả lời được hết, bạn đã sẵn sàng bài 16.

---

## 13. Tóm tắt bài 15

| Điểm | Nội dung |
|---|---|
| **Event Storming** | Workshop khám phá domain bằng sticky notes |
| **Ai sáng tạo** | Alberto Brandolini (2012) |
| **Ai tham gia** | Domain Expert + Dev + QA + BA + PO + Facilitator |
| **9 loại notes** | Event (cam), Command (xanh), Aggregate (vàng), Policy (tím), Read Model (xanh lá), Actor (nâu), Hotspot (đỏ), External (trắng) |
| **3 cấp độ** | Big Picture, Process Level, Design Level |
| **Quy trình** | Chaotic → Timeline → Enforce → Pivotal → Actor → Policy → Hotspot → Boundary |
| **Pivotal Event** | Chia flow thành phase, thường = Aggregate boundary |
| **Hotspot** | Vấn đề, câu hỏi — ghi lại, không giải quyết ngay |
| **Facilitator** | Quan trọng nhất — điều phối, không đưa ý kiến |
| **Mapping code** | Mỗi note → 1 class/function Python |
| **8 lỗi** | Không expert, không facilitator, design sớm, không sticky, tranh luận, giải quyết hotspot, không ảnh, làm 1 lần |

**Câu thần chú:** *"Dán giấy lên tường, mọi người cùng kể chuyện, business và dev hiểu nhau."*

---

## 14. Chuẩn bị cho bài 16

Bài tiếp theo: **Chiến lược chọn Bounded Context — Khi nào tách, khi nào gộp**.

Chuẩn bị:
- Đọc lại bài 4 (Bounded Context) và bài 14 (Context Map).
- Nghĩ về **1 hệ thống lớn** bạn đang làm.
- Sẽ bàn: các tiêu chí tách/gộp, Conway's Law, team topology, Core Domain chart, và trade-offs giữa monolith vs microservices.

Đây là bài **chiến lược** cuối cùng của Level 4 — bạn sẽ học cách **quyết định kiến trúc tổ chức**.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 16** (Chiến lược chọn Bounded Context) ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Mô phỏng Event Storming** cho domain bạn đang làm — bạn cho tôi domain, tôi sẽ dẫn dắt từng bước như facilitator.
5. **Đào sâu** một phần: Process Modeling, Aggregate Design Canvas, collaboration patterns.

Nói tôi biết bạn muốn gì nhé.