## Bài 1: Kiến thức nền tảng về NoSQL & MongoDB

---

### 1. So sánh SQL (Relational) và NoSQL (MongoDB)

Cơ sở dữ liệu quan hệ (SQL) lưu trữ dữ liệu dưới dạng bảng cố định với các hàng và cột. Ngược lại, MongoDB là một hệ quản trị cơ sở dữ liệu NoSQL dạng **Document-oriented** (hướng tài liệu), lưu trữ dữ liệu linh hoạt dưới dạng các bản ghi tương tự JSON.

| Khái niệm trong SQL | Khái niệm trong MongoDB | Mô tả |
| --- | --- | --- |
| **Database** | **Database** | Nơi chứa các tập hợp dữ liệu |
| **Table** (Bảng) | **Collection** | Tập hợp các tài liệu (Document) có liên quan |
| **Row** (Dòng/Bản ghi) | **Document** | Một đối tượng dữ liệu đơn lẻ (Dạng JSON/BSON) |
| **Column** (Cột) | **Field** (Trường) | Cặp `Khóa: Giá trị` nằm bên trong Document |
| **Primary Key** | **`_id` Field** | Khóa chính duy nhất đại diện cho mỗi Document |

---

### 2. Định dạng JSON và BSON

Mặc dù thao tác truy vấn trong Python sử dụng cú pháp giống `dictionary` (tương tự JSON), MongoDB lại lưu trữ dữ liệu bên dưới đĩa cứng dưới dạng **BSON** (Binary JSON).

* **BSON là gì?** BSON là bản mã hóa nhị phân của JSON, giúp máy tính duyệt và truy vấn dữ liệu nhanh hơn.
* **Điểm vượt trội của BSON:** BSON hỗ trợ nhiều kiểu dữ liệu mà JSON thuần không có, chẳng hạn như `Date`, `ObjectId`, `Int32`, `Int64`, `Decimal128`, và `Binary data`.

```json
{
  "_id": "64f1a2b3c4e5f6a7b8c9d0e1",
  "ten": "Nguyễn Văn A",
  "tuoi": 25,
  "ngay_tao": "2026-09-02T08:00:00Z",
  "kynang": ["Python", "MongoDB"]
}

```

---

### 3. Cài đặt môi trường làm việc

Để thực hành, bạn cần chuẩn bị server MongoDB và công cụ quản lý giao diện:

1. **Chạy MongoDB Server (Một trong hai cách):**
* **Cục bộ (Local):** Tải và cài đặt **MongoDB Community Server** miễn phí từ trang chủ MongoDB.
* **Đám mây (Cloud):** Đăng ký tài khoản miễn phí trên **MongoDB Atlas** để lấy chuỗi kết nối (`connection string`).


2. **Công cụ giao diện (GUI):** Tải và cài đặt **MongoDB Compass** để trực quan hóa dữ liệu, trực tiếp xem các Database, Collection và Document mà bạn thao tác qua Python.

---