# Giai đoạn 1 – Python Foundation

# Buổi 20. Mini Project – Hệ thống Quản lý Sinh viên (Student Management System)

> Đây là buổi cuối của Giai đoạn 1. Mục tiêu không phải học thêm kiến thức mới mà **tổng hợp tất cả những gì đã học** để xây dựng một chương trình hoàn chỉnh.

Sau buổi này, bạn sẽ thấy cách các kiến thức như **Function, List, Dictionary, Lambda, Comprehension và Exception** kết hợp với nhau trong một ứng dụng thực tế.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Biết cách chia chương trình thành nhiều hàm.
* Biết cách quản lý dữ liệu bằng `list` và `dict`.
* Biết xây dựng menu.
* Biết xử lý lỗi nhập liệu.
* Biết sắp xếp và tìm kiếm dữ liệu.
* Viết chương trình theo chuẩn PEP 8.

---

# Chức năng của chương trình

Chương trình quản lý sinh viên sẽ có các chức năng:

```
=========================
STUDENT MANAGEMENT SYSTEM
=========================

1. Thêm sinh viên
2. Hiển thị danh sách
3. Tìm sinh viên
4. Cập nhật điểm
5. Xóa sinh viên
6. Sắp xếp theo điểm
7. Thống kê
8. Thoát
```

---

# Thiết kế dữ liệu

Mỗi sinh viên là một Dictionary.

Ví dụ:

```python
student = {"id": 1, "name": "An", "age": 20, "score": 8.5}
```

Toàn bộ dữ liệu:

```python
students = [
    {"id": 1, "name": "An", "age": 20, "score": 8.5},
    {"id": 2, "name": "Lan", "age": 21, "score": 9},
]
```

---

# Kiến trúc chương trình

```
main()
│
├── show_menu()
├── add_student()
├── display_students()
├── find_student()
├── update_score()
├── delete_student()
├── sort_students()
├── statistics()
└── input_number()
```

Mỗi hàm chỉ thực hiện **một nhiệm vụ duy nhất**.

---

# Mã nguồn hoàn chỉnh

```python
students = []


def show_menu():
    print("\n" + "=" * 35)
    print(" STUDENT MANAGEMENT SYSTEM")
    print("=" * 35)
    print("1. Thêm sinh viên")
    print("2. Hiển thị danh sách")
    print("3. Tìm sinh viên")
    print("4. Cập nhật điểm")
    print("5. Xóa sinh viên")
    print("6. Sắp xếp theo điểm")
    print("7. Thống kê")
    print("0. Thoát")


def input_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Vui lòng nhập số nguyên!")


def input_float(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Vui lòng nhập số!")


def find_student_by_id(student_id):
    for student in students:
        if student["id"] == student_id:
            return student
    return None


def add_student():
    print("\n--- Thêm sinh viên ---")

    student_id = input_int("ID: ")

    if find_student_by_id(student_id):
        print("ID đã tồn tại.")
        return

    name = input("Tên: ")
    age = input_int("Tuổi: ")

    while True:
        score = input_float("Điểm: ")
        if 0 <= score <= 10:
            break
        print("Điểm phải từ 0 đến 10.")

    student = {"id": student_id, "name": name, "age": age, "score": score}

    students.append(student)

    print("Đã thêm thành công.")


def display_students():
    print("\n===== DANH SÁCH =====")

    if not students:
        print("Chưa có dữ liệu.")
        return

    print(f"{'ID':<5}{'Tên':<20}{'Tuổi':<8}{'Điểm'}")

    for s in students:
        print(f"{s['id']:<5}{s['name']:<20}{s['age']:<8}{s['score']:.2f}")


def find_student():
    student_id = input_int("Nhập ID: ")

    student = find_student_by_id(student_id)

    if student:
        print(student)
    else:
        print("Không tìm thấy.")


def update_score():
    student_id = input_int("ID: ")

    student = find_student_by_id(student_id)

    if student is None:
        print("Không tồn tại.")
        return

    while True:
        score = input_float("Điểm mới: ")
        if 0 <= score <= 10:
            student["score"] = score
            break
        print("Điểm không hợp lệ.")

    print("Đã cập nhật.")


def delete_student():
    student_id = input_int("ID: ")

    student = find_student_by_id(student_id)

    if student:
        students.remove(student)
        print("Đã xóa.")
    else:
        print("Không tìm thấy.")


def sort_students():
    students.sort(key=lambda student: student["score"], reverse=True)

    print("Đã sắp xếp.")


def statistics():
    if not students:
        print("Không có dữ liệu.")
        return

    scores = [s["score"] for s in students]

    average = sum(scores) / len(scores)

    highest = max(students, key=lambda s: s["score"])

    lowest = min(students, key=lambda s: s["score"])

    print(f"Điểm TB: {average:.2f}")
    print(f"Cao nhất: {highest['name']} ({highest['score']})")

    print(f"Thấp nhất: {lowest['name']} ({lowest['score']})")


def main():

    while True:
        show_menu()

        choice = input("Chọn: ")

        if choice == "1":
            add_student()

        elif choice == "2":
            display_students()

        elif choice == "3":
            find_student()

        elif choice == "4":
            update_score()

        elif choice == "5":
            delete_student()

        elif choice == "6":
            sort_students()

        elif choice == "7":
            statistics()

        elif choice == "0":
            print("Tạm biệt!")
            break

        else:
            print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
```

---

# Kiến thức đã sử dụng

## Function

```python
def add_student():
```

Mỗi chức năng là một hàm riêng.

---

## List

```python
students = []
```

Lưu nhiều sinh viên.

---

## Dictionary

```python
student = {"id": 1, "name": "An"}
```

Mỗi sinh viên là một Dictionary.

---

## Lambda

```python
students.sort(key=lambda s: s["score"])
```

Sắp xếp theo điểm.

---

## List Comprehension

```python
scores = [s["score"] for s in students]
```

Lấy danh sách điểm.

---

## Exception

```python
try:
    return int(input())
except ValueError:
    ...
```

Xử lý nhập sai dữ liệu.

---

## Điều kiện

```python
if score < 0:
```

---

## Vòng lặp

```python
while True:
```

---

# Những điểm còn hạn chế

Chương trình hiện tại:

* Chưa lưu dữ liệu ra tệp.
* Chưa dùng lớp (`class`).
* Chưa dùng module.
* Chưa có giao diện.
* Chưa kết nối cơ sở dữ liệu.

Điều này là bình thường vì bạn mới hoàn thành Giai đoạn Foundation.

---

# Hướng cải tiến (sau khi học Intermediate)

Phiên bản 2:

```
student_management/
│
├── main.py
├── models.py
├── services.py
├── storage.py
└── utils.py
```

Sau đó:

```
SQLite
      ↓
Repository Pattern
      ↓
MVC
      ↓
Clean Architecture
      ↓
DDD
```

Đây chính là lộ trình mà chúng ta sẽ học ở các giai đoạn sau.

---

# Bài tập mở rộng

## Bài 1

Thêm chức năng:

```
Tìm theo tên
```

---

## Bài 2

Thêm:

```
Xếp loại

>=9  Xuất sắc
>=8  Giỏi
>=6.5 Khá
>=5 Trung bình
<5 Yếu
```

---

## Bài 3

Thêm chức năng:

```
Lưu dữ liệu ra file JSON
```

*(Sau này sẽ học chính thức ở giai đoạn Intermediate.)*

---

## Bài 4

Thêm chức năng:

```
Đọc dữ liệu từ file JSON
```

---

## Bài 5

Hiển thị bảng đẹp hơn:

```
+----+------------+------+-------+
| ID | Tên        | Tuổi | Điểm  |
+----+------------+------+-------+
| 1  | An         | 20   | 8.50  |
| 2  | Lan        | 21   | 9.00  |
+----+------------+------+-------+
```

---

# Tổng kết Giai đoạn 1 – Python Foundation

🎉 Chúc mừng! Bạn đã hoàn thành **20 buổi học** của Giai đoạn 1.

Bạn đã nắm được:

* ✅ Cú pháp Python cơ bản.
* ✅ Kiểu dữ liệu chuẩn.
* ✅ Điều kiện và vòng lặp.
* ✅ Hàm và phạm vi biến.
* ✅ Lambda.
* ✅ List/Dict Comprehension.
* ✅ Exception.
* ✅ Xây dựng chương trình có cấu trúc.

## Đánh giá năng lực sau Giai đoạn 1

Sau khi hoàn thành đầy đủ và thực hành tốt các bài tập, bạn có thể:

* Viết các chương trình Python từ vài trăm dòng mã.
* Giải quyết các bài toán thuật toán cơ bản.
* Đọc và hiểu phần lớn mã Python ở mức cơ bản.
* Xây dựng các ứng dụng CLI đơn giản.
* Sẵn sàng bước sang **Giai đoạn 2 – Python Intermediate**, nơi bạn sẽ học các chủ đề như Module & Package, File I/O, OOP, Iterator, Generator, Decorator, Context Manager, Typing, Async Programming và nhiều kỹ thuật chuyên nghiệp khác.
