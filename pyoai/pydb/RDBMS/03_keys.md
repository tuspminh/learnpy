Version:0.9 StartHTML:00000097 EndHTML:00053699 StartFragment:00000131 EndFragment:00053663 

# Làm chủ Cơ sở dữ liệu quan hệ (Relational Database)

# Buổi 3: Khóa (Keys) trong Cơ sở dữ liệu – Primary Key, Candidate Key, Alternate Key, Composite Key, Surrogate Key, Natural Key

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu vì sao mọi bảng đều cần khóa. 
>   * Phân biệt các loại khóa trong cơ sở dữ liệu. 
>   * Biết khi nào nên dùng khóa tự nhiên và khóa thay thế. 
>   * Thiết kế khóa đúng theo chuẩn doanh nghiệp. 
>   * Tránh các lỗi thiết kế phổ biến của người mới. 
> 


* * *

# Phần 1. Tại sao cần khóa (Key)?

Hãy tưởng tượng bạn có bảng `students`:

name| age  
---|---  
Nguyễn Văn A| 20  
Nguyễn Văn A| 21  
Trần Văn B| 19  
  
Nếu muốn sửa thông tin của **Nguyễn Văn A** , bạn sẽ sửa dòng nào?

Không thể xác định chính xác vì tên có thể trùng.

Đây là lý do cần **Key** để định danh duy nhất mỗi bản ghi.

* * *

# Phần 2. Key là gì?

**Key** là một hoặc nhiều cột dùng để:

  * Định danh duy nhất một bản ghi. 
  * Liên kết giữa các bảng. 
  * Đảm bảo tính toàn vẹn dữ liệu. 
  * Tăng hiệu quả truy vấn (kết hợp với Index). 



Ví dụ:

id| name| age  
---|---|---  
1| Nguyễn Văn A| 20  
2| Nguyễn Văn A| 21  
3| Trần Văn B| 19  
  
Ở đây:

  * `id` là khóa. 
  * Hai người có thể cùng tên nhưng không thể cùng `id`. 



* * *

# Phần 3. Primary Key (PK)

**Primary Key** là khóa chính của bảng.

Một bảng chỉ có **một Primary Key** (nhưng khóa này có thể gồm nhiều cột).

Đặc điểm:

  * Không được trùng. 
  * Không được NULL. 
  * Dùng để định danh duy nhất. 



Ví dụ:
    
    
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER
    );

Dữ liệu hợp lệ:

id| name  
---|---  
1| An  
2| Bình  
3| Cường  
  
Không hợp lệ:

id| name  
---|---  
1| An  
1| Bình  
  
Lỗi vì `id` bị trùng.

* * *

# Phần 4. Candidate Key

Một bảng có thể có **nhiều cột** đủ khả năng định danh duy nhất.

Các cột đó gọi là **Candidate Key**.

Ví dụ bảng người dùng:

id| username| email  
---|---|---  
1| an123| an@gmail.com  
2| binh88| binh@gmail.com  
  
Các cột sau đều là Candidate Key:

  * id 
  * username 
  * email 



Vì mỗi cột đều duy nhất.

Sau đó ta chọn **một** Candidate Key làm Primary Key.

Ví dụ:
    
    
    Candidate Keys
    
    id
    
    username
    
    email
    
    ↓
    
    Chọn
    
    ↓
    
    Primary Key = id

* * *

# Phần 5. Alternate Key

Các Candidate Key **không được chọn** làm Primary Key gọi là **Alternate Key**.

Ví dụ:

Candidate Keys:

  * id 
  * username 
  * email 



Chọn:
    
    
    Primary Key
    
    ↓
    
    id

Thì:
    
    
    Alternate Keys
    
    username
    
    email

Trong SQL, các Alternate Key thường được triển khai bằng ràng buộc `UNIQUE`.

Ví dụ:
    
    
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE
    );

* * *

# Phần 6. Composite Key (Khóa ghép)

Có những trường hợp **một cột không đủ để định danh** , phải kết hợp nhiều cột.

Ví dụ bảng đăng ký môn học:

student_id| subject_id  
---|---  
1| 101  
1| 102  
2| 101  
  
Ở đây:

  * `student_id` không duy nhất. 
  * `subject_id` cũng không duy nhất. 
  * Nhưng cặp (`student_id`, `subject_id`) là duy nhất. 



Primary Key:
    
    
    PRIMARY KEY(student_id, subject_id)

Đây gọi là **Composite Key**.

* * *

# Phần 7. Natural Key

Natural Key là khóa có sẵn trong thực tế.

Ví dụ:

  * Số CCCD 
  * ISBN của sách 
  * Mã số thuế 
  * Biển số xe (tùy nghiệp vụ) 



Ví dụ:

citizen_id| full_name  
---|---  
079123456789| Nguyễn Văn A  
  
`citizen_id` là Natural Key.

### Ưu điểm

  * Có ý nghĩa nghiệp vụ. 
  * Không cần tạo thêm mã. 



### Nhược điểm

  * Có thể thay đổi theo quy định. 
  * Có thể dài. 
  * Không phải lúc nào cũng tồn tại ngay từ đầu. 



* * *

# Phần 8. Surrogate Key

Surrogate Key là khóa **được hệ thống tạo ra** , không mang ý nghĩa nghiệp vụ.

Ví dụ:

id| citizen_id| name  
---|---|---  
1| 079123456789| Nguyễn Văn A  
2| 079987654321| Trần Văn B  
  
`id` là Surrogate Key.

Thường dùng:

  * AUTO_INCREMENT 
  * IDENTITY 
  * SEQUENCE 
  * UUID 



Ví dụ SQLite:
    
    
    id INTEGER PRIMARY KEY AUTOINCREMENT

Ví dụ PostgreSQL:
    
    
    id BIGSERIAL PRIMARY KEY

Hoặc:
    
    
    id UUID PRIMARY KEY

* * *

# Phần 9. So sánh Natural Key và Surrogate Key

Tiêu chí| Natural Key| Surrogate Key  
---|---|---  
Có ý nghĩa nghiệp vụ| ✔| ✘  
Có thể thay đổi| Có thể| Không nên  
Ngắn gọn| Không phải lúc nào| Thường có  
Hiệu quả Join| Thấp hơn nếu khóa dài| Cao hơn  
Phổ biến trong doanh nghiệp| Ít hơn| Rất phổ biến  
  
**Khuyến nghị:**

Trong hầu hết các hệ thống hiện đại:

  * Dùng **Surrogate Key** làm Primary Key. 
  * Dùng **Natural Key** với ràng buộc `UNIQUE` nếu cần đảm bảo tính duy nhất theo nghiệp vụ. 



* * *

# Phần 10. Ví dụ thực tế: Hệ thống bán hàng

Bảng `customers`:

id| customer_code| email| full_name  
---|---|---|---  
1| KH0001| an@gmail.com| Nguyễn Văn An  
2| KH0002| binh@gmail.com| Trần Bình  
  
  * `id`: Surrogate Key, Primary Key. 
  * `customer_code`: Natural/Candidate Key. 
  * `email`: Candidate Key. 
  * `customer_code` và `email` nên có ràng buộc `UNIQUE`. 



* * *

# Phần 11. Thiết kế SQL
    
    
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_code TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT UNIQUE
    );

Giải thích:

  * `id`: định danh nội bộ. 
  * `customer_code`: mã khách hàng theo nghiệp vụ. 
  * `email`: không được trùng. 
  * `phone`: nếu mỗi số điện thoại chỉ thuộc một khách hàng thì cũng nên `UNIQUE`. 



* * *

# Phần 12. Thực hành với Python
    
    
    import sqlite3
    
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)
    
    customers = [
        ("KH001", "Nguyễn Văn A", "a@gmail.com"),
        ("KH002", "Trần Văn B", "b@gmail.com"),
        ("KH003", "Lê Văn C", "c@gmail.com")
    ]
    
    cursor.executemany("""
    INSERT INTO customers (customer_code, full_name, email)
    VALUES (?, ?, ?)
    """, customers)
    
    conn.commit()
    
    cursor.execute("SELECT * FROM customers")
    
    for row in cursor.fetchall():
        print(row)
    
    conn.close()

Kết quả:
    
    
    (1, 'KH001', 'Nguyễn Văn A', 'a@gmail.com')
    (2, 'KH002', 'Trần Văn B', 'b@gmail.com')
    (3, 'KH003', 'Lê Văn C', 'c@gmail.com')

* * *

# Phần 13. Những sai lầm phổ biến

## Sai lầm 1: Dùng tên làm Primary Key
    
    
    PRIMARY KEY(name)

❌ Sai vì tên có thể trùng.

* * *

## Sai lầm 2: Dùng email làm Primary Key

Email có thể thay đổi khi người dùng đổi địa chỉ email.

* * *

## Sai lầm 3: Không khai báo Primary Key

Không có khóa chính sẽ gây khó khăn cho việc cập nhật, xóa, liên kết bảng và sử dụng ORM.

* * *

## Sai lầm 4: Dùng Composite Key ở mọi nơi

Composite Key rất hữu ích trong các bảng liên kết (junction table), nhưng nếu lạm dụng sẽ khiến câu lệnh `JOIN`, khóa ngoại và ORM trở nên phức tạp.

* * *

# Tổng kết buổi 3

Bạn đã học được:

  * Vai trò của Key trong cơ sở dữ liệu. 
  * Primary Key và các yêu cầu của nó. 
  * Candidate Key và cách lựa chọn. 
  * Alternate Key và cách triển khai bằng `UNIQUE`. 
  * Composite Key và các trường hợp sử dụng. 
  * Natural Key và Surrogate Key. 
  * Thực hành tạo bảng với các loại khóa bằng SQL và Python. 
  * Những lỗi thiết kế khóa thường gặp và cách tránh. 



* * *

# Bài tập thực hành

## Bài 1

Thiết kế bảng `students` gồm:

  * `id` (Primary Key, AUTOINCREMENT) 
  * `student_code` (UNIQUE) 
  * `email` (UNIQUE) 
  * `full_name`
  * `birthday`



Sau đó chèn 10 sinh viên.

* * *

## Bài 2

Thiết kế bảng `subjects` gồm:

  * `id`
  * `subject_code` (UNIQUE) 
  * `subject_name`
  * `credits`



* * *

## Bài 3

Thiết kế bảng `enrollments` sử dụng **Composite Key** gồm:

  * `student_id`
  * `subject_id`
  * `enroll_date`



Trong đó khóa chính là `(student_id, subject_id)`.

* * *

## Bài 4 (Nâng cao)

Thiết kế cơ sở dữ liệu cho một **ứng dụng học ngoại ngữ** :

  * Xác định Primary Key, Candidate Key và Alternate Key cho các bảng: 
    * `users`
    * `courses`
    * `lessons`
    * `vocabularies`
    * `learning_progress`



Giải thích vì sao bạn chọn **Surrogate Key** hay **Natural Key** cho từng bảng.

* * *

## Chuẩn bị cho buổi 4

Ở buổi tiếp theo, chúng ta sẽ học **Foreign Key** – nền tảng của cơ sở dữ liệu quan hệ. Bạn sẽ hiểu cách các bảng được liên kết với nhau, cách đảm bảo **Referential Integrity** , cũng như các hành vi như `CASCADE`, `SET NULL`, `RESTRICT` và `NO ACTION` thông qua nhiều ví dụ thực tế và bài tập chuyên sâu.

