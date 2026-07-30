Version:0.9 StartHTML:00000097 EndHTML:00081019 StartFragment:00000131 EndFragment:00080983 

# Làm chủ Cơ sở dữ liệu quan hệ (Relational Database)

# Buổi 4: Foreign Key - Referential Integrity - CASCADE - SET NULL - RESTRICT - NO ACTION

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu bản chất của Foreign Key. 
>   * Hiểu Referential Integrity (toàn vẹn tham chiếu). 
>   * Biết cách liên kết các bảng đúng chuẩn. 
>   * Hiểu khi nào dùng CASCADE, RESTRICT, SET NULL, SET DEFAULT và NO ACTION. 
>   * Biết những lỗi thiết kế Foreign Key phổ biến. 
>   * Thực hành với SQLite và Python. 
> 


* * *

# Phần 1. Ôn lại

Buổi trước chúng ta học:
    
    
    Primary Key
    
    ↓
    
    Định danh duy nhất

Ví dụ

## Students

id| name  
---|---  
1| An  
2| Bình  
3| Cường  
  
Ở đây
    
    
    id
    
    ↓
    
    Primary Key

* * *

# Phần 2. Tại sao cần Foreign Key?

Giả sử có bảng:

## Orders

id| customer_id  
---|---  
1| 10  
  
Nhưng bảng Customer chỉ có

id| name  
---|---  
1| An  
2| Bình  
  
Customer số **10 không tồn tại.**

Điều này gọi là:
    
    
    Dữ liệu mồ côi
    (Orphan Data)

Database phải ngăn chuyện này.

* * *

# Foreign Key ra đời

Foreign Key dùng để đảm bảo:

> Giá trị ở bảng con **phải tồn tại** ở bảng cha.

Ví dụ
    
    
    Customer
    
    ↓
    
    Order

Order chỉ được phép tham chiếu tới Customer đã tồn tại.

* * *

# Phần 3. Foreign Key là gì?

Foreign Key (FK)

Là cột dùng để tham chiếu tới Primary Key của bảng khác.

Ví dụ

## Customers

id| name  
---|---  
1| An  
2| Bình  
  
## Orders

id| customer_id  
---|---  
1| 1  
2| 2  
  
Ở đây
    
    
    Orders.customer_id
    
    ↓
    
    Customers.id

Đó là Foreign Key.

* * *

# Minh họa
    
    
    +------------------+
    | Customers        |
    +------------------+
    | id (PK)          |
    | name             |
    +------------------+
    
            ▲
            │
            │
    +------------------+
    | Orders           |
    +------------------+
    | id               |
    | customer_id (FK) |
    | total            |
    +------------------+

* * *

# Phần 4. Parent Table và Child Table

Có hai khái niệm rất quan trọng.

## Parent Table
    
    
    Customers

## Child Table
    
    
    Orders

Vì:
    
    
    Orders
    
    ↓
    
    tham chiếu
    
    ↓
    
    Customers

* * *

Ví dụ khác
    
    
    Classes
    
    ↓
    
    Students

Students là Child.

Classes là Parent.

* * *

# Phần 5. Referential Integrity

Đây là một trong những khái niệm quan trọng nhất của Database.

Referential Integrity có nghĩa là:

> Mọi Foreign Key phải tham chiếu tới một Primary Key hợp lệ.

Ví dụ đúng

Customers

id  
---  
1  
2  
  
Orders

customer_id  
---  
1  
2  
  
✔ hợp lệ

* * *

Ví dụ sai

Customers

id  
---  
1  
2  
  
Orders

customer_id  
---  
5  
  
❌ Không hợp lệ.

Database sẽ báo lỗi.

* * *

# Phần 6. Tạo Foreign Key bằng SQL

SQLite
    
    
    CREATE TABLE customers(
        id INTEGER PRIMARY KEY,
        name TEXT
    );
    
    CREATE TABLE orders(
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        total REAL,
    
        FOREIGN KEY(customer_id)
        REFERENCES customers(id)
    );

Giải thích
    
    
    orders.customer_id
    
    ↓
    
    references
    
    ↓
    
    customers.id

* * *

# Phần 7. Thử thêm dữ liệu

Customers
    
    
    INSERT INTO customers
    VALUES(1,'An');

Orders
    
    
    INSERT INTO orders
    VALUES(1,1,500);

✔ Thành công.

* * *

Nếu
    
    
    INSERT INTO orders
    VALUES(2,10,900);

Kết quả
    
    
    FOREIGN KEY constraint failed

Vì Customer số 10 không tồn tại.

* * *

# Phần 8. Tại sao cần ON DELETE?

Giả sử

Customers

id  
---  
1  
  
Orders

customer_id  
---  
1  
  
Bây giờ
    
    
    DELETE FROM customers
    WHERE id=1;

Điều gì xảy ra?

Order sẽ tham chiếu tới khách hàng không tồn tại.

Đó là dữ liệu mồ côi.

Database phải xử lý.

* * *

# Phần 9. ON DELETE CASCADE

CASCADE nghĩa là:

Cha bị xóa

↓

Con cũng bị xóa.

Ví dụ

Customer
    
    
    An

Có
    
    
    3 Orders

Xóa Customer

↓

3 Orders cũng mất.

* * *

SQL
    
    
    FOREIGN KEY(customer_id)
    REFERENCES customers(id)
    ON DELETE CASCADE

* * *

Ví dụ

Customers

id  
---  
1  
  
Orders

id| customer_id  
---|---  
1| 1  
2| 1  
3| 1  
  
Sau
    
    
    DELETE FROM customers
    WHERE id=1;

Customers

Trống.

Orders

Cũng trống.

* * *

## Khi nào dùng CASCADE?

Nên dùng khi dữ liệu con **không có ý nghĩa nếu thiếu dữ liệu cha**.

Ví dụ:

  * Giỏ hàng → Chi tiết giỏ hàng. 
  * Đơn hàng → Dòng chi tiết đơn hàng. 
  * Bài viết nháp → Ảnh đính kèm tạm. 



**Cân nhắc:** Với dữ liệu nghiệp vụ quan trọng (ví dụ đơn hàng đã hoàn tất), xóa dây chuyền có thể gây mất dữ liệu lịch sử.

* * *

# Phần 10. ON DELETE RESTRICT

RESTRICT

Có nghĩa là:

Không cho xóa.

Ví dụ

Customer

↓

Có Order

↓

Không được xóa.

SQL
    
    
    FOREIGN KEY(customer_id)
    REFERENCES customers(id)
    ON DELETE RESTRICT

Nếu
    
    
    DELETE FROM customers
    WHERE id=1;

Kết quả
    
    
    Error

* * *

## Khi nào dùng RESTRICT?

Rất phổ biến trong:

  * Hệ thống ngân hàng. 
  * Hóa đơn. 
  * Kế toán. 
  * Quản lý kho. 
  * Dữ liệu cần lưu vết lâu dài. 



* * *

# Phần 11. ON DELETE SET NULL

Nếu xóa cha

↓

Foreign Key

↓

NULL

Ví dụ

Orders

customer_id  
---  
1  
  
Sau khi xóa Customer

Orders

customer_id  
---  
NULL  
  
SQL
    
    
    FOREIGN KEY(customer_id)
    REFERENCES customers(id)
    ON DELETE SET NULL

Lưu ý:
    
    
    customer_id

**phải cho phép NULL**.

* * *

## Khi nào dùng?

Ví dụ:

  * Nhân viên nghỉ việc nhưng vẫn muốn giữ lịch sử công việc. 
  * Người kiểm duyệt tài liệu bị xóa khỏi hệ thống nhưng tài liệu vẫn tồn tại. 



* * *

# Phần 12. ON DELETE NO ACTION

Đây là lựa chọn mặc định của nhiều hệ quản trị CSDL.

Nó sẽ từ chối thao tác nếu thao tác đó làm vi phạm ràng buộc khóa ngoại.

Trong SQLite, `NO ACTION` và `RESTRICT` thường cho kết quả giống nhau trong các tình huống đơn giản, nhưng ở một số hệ quản trị khác và trong các giao dịch phức tạp, thời điểm kiểm tra ràng buộc có thể khác.

* * *

# Phần 13. ON UPDATE

Foreign Key không chỉ xử lý DELETE.

Còn xử lý UPDATE.

Ví dụ
    
    
    Customer.id
    
    1
    
    ↓
    
    5

Order sẽ thế nào?

Có nhiều lựa chọn:
    
    
    CASCADE
    
    ↓
    
    Order.customer_id
    
    1
    
    ↓
    
    5

SQL
    
    
    FOREIGN KEY(customer_id)
    REFERENCES customers(id)
    ON UPDATE CASCADE

* * *

# Phần 14. Minh họa toàn bộ
    
    
                    DELETE
    
    Parent -----------------> Child
    
    CASCADE  ---------> Xóa luôn
    
    RESTRICT ---------> Báo lỗi
    
    NO ACTION --------> Báo lỗi (trong hầu hết trường hợp)
    
    SET NULL ---------> FK = NULL
    
    SET DEFAULT -----> FK = giá trị mặc định

* * *

# Phần 15. Ví dụ thực tế: Shopee
    
    
    Customers
    
    ↓
    
    Orders
    
    ↓
    
    OrderDetails
    
    ↓
    
    Products

Thông thường:

  * Customer → Orders: thường **RESTRICT** hoặc không xóa vật lý (soft delete). 
  * Orders → OrderDetails: thường **CASCADE** nếu đơn hàng bị xóa trong giai đoạn nháp. 
  * Product → OrderDetails: thường **RESTRICT** , vì không nên mất lịch sử giao dịch. 



* * *

# Phần 16. Thực hành với Python và SQLite

> **Lưu ý:** Trong SQLite, ràng buộc khóa ngoại **không được bật mặc định**. Cần bật bằng:
    
    
    import sqlite3
    
    conn = sqlite3.connect("shop.db")
    conn.execute("PRAGMA foreign_keys = ON")
    
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        total REAL,
    
        FOREIGN KEY(customer_id)
        REFERENCES customers(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
    )
    """)
    
    cur.execute("INSERT INTO customers VALUES(1,'An')")
    cur.execute("INSERT INTO orders VALUES(1,1,500000)")
    
    conn.commit()
    conn.close()

* * *

# Phần 17. Những sai lầm phổ biến

## Sai lầm 1

Không tạo Foreign Key.

Hậu quả:

  * Dữ liệu mồ côi. 
  * Mất tính toàn vẹn. 
  * Khó kiểm soát lỗi. 



* * *

## Sai lầm 2

Lạm dụng `ON DELETE CASCADE`.

Có thể vô tình xóa hàng nghìn hoặc hàng triệu bản ghi liên quan.

* * *

## Sai lầm 3

Tham chiếu tới cột không phải Primary Key hoặc không có ràng buộc `UNIQUE`.

Khóa ngoại phải tham chiếu tới một khóa ứng viên hợp lệ (thường là `PRIMARY KEY` hoặc `UNIQUE`).

* * *

## Sai lầm 4

Quên bật `PRAGMA foreign_keys = ON` khi dùng SQLite.

Khi đó SQLite sẽ không kiểm tra ràng buộc khóa ngoại và dữ liệu sai vẫn có thể được chèn vào.

* * *

# Tổng kết buổi 4

Hôm nay bạn đã học:

  * Foreign Key là gì. 
  * Parent Table và Child Table. 
  * Referential Integrity. 
  * Cách tạo khóa ngoại. 
  * `ON DELETE CASCADE`. 
  * `ON DELETE RESTRICT`. 
  * `ON DELETE SET NULL`. 
  * `ON DELETE NO ACTION`. 
  * `ON UPDATE CASCADE`. 
  * Thực hành với SQLite và Python. 
  * Những lỗi thiết kế thường gặp. 



Đây là nền tảng để xây dựng các cơ sở dữ liệu có tính nhất quán và đáng tin cậy.

* * *

# Bài tập thực hành

## Bài 1

Tạo hai bảng:

  * `departments`
  * `employees`



Yêu cầu:

  * Một phòng ban có nhiều nhân viên. 
  * `employees.department_id` là Foreign Key. 
  * Thử chèn một nhân viên có `department_id` không tồn tại và quan sát lỗi. 



* * *

## Bài 2

Tạo hai bảng:

  * `authors`
  * `books`



Thiết lập:
    
    
    ON DELETE SET NULL

Sau đó:

  1. Thêm dữ liệu. 
  2. Xóa một tác giả. 
  3. Quan sát giá trị `author_id` trong bảng `books`. 



* * *

## Bài 3

Tạo ba bảng:

  * `customers`
  * `orders`
  * `order_details`



Thiết kế khóa ngoại phù hợp và giải thích vì sao bạn chọn:

  * `CASCADE`
  * `RESTRICT`
  * `SET NULL`



cho từng mối quan hệ.

* * *

## Bài 4 (Nâng cao)

Thiết kế mô hình khóa ngoại cho một **ứng dụng học ngoại ngữ** (tương tự Duolingo hoặc HelloChinese) với các bảng:

  * `users`
  * `courses`
  * `lessons`
  * `vocabularies`
  * `questions`
  * `user_progress`



Hãy xác định:

  1. Các khóa ngoại giữa các bảng. 
  2. Hành vi `ON DELETE` và `ON UPDATE` phù hợp cho từng khóa ngoại. 
  3. Giải thích lý do lựa chọn dựa trên yêu cầu nghiệp vụ. 



* * *

## Chuẩn bị cho buổi 5

Ở buổi tiếp theo, chúng ta sẽ học **ERD (Entity Relationship Diagram)** một cách chuyên sâu:

  * Ký pháp Crow's Foot. 
  * Cardinality (1-1, 1-N, N-N). 
  * Optional và Mandatory Relationship. 
  * Cách đọc và vẽ ERD theo chuẩn doanh nghiệp. 
  * Thiết kế ERD hoàn chỉnh cho các hệ thống như quản lý trường học, thư viện, thương mại điện tử và mạng xã hội.

