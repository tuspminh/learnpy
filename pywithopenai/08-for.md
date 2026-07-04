Khóa học Python từ Cơ bản đến Chuyên gia

Buổi 8: Làm chủ vòng lặp for từ cơ bản đến nâng cao

Mục tiêu buổi học

Sau buổi học này, bạn sẽ:

* Hiểu bản chất của vòng lặp for trong Python.
* Phân biệt for và while.
* Thành thạo range().
* Duyệt chuỗi, list, tuple, set, dictionary.
* Thành thạo enumerate(), zip(), reversed(), sorted().
* Hiểu giao thức Iterable và Iterator.
* Biết cách viết vòng lặp theo phong cách Pythonic.
* Áp dụng vào các bài toán thực tế.

---

# 1. for là gì?

Rất nhiều người mới học nghĩ rằng:

for là vòng lặp chạy từ 1 đến n.

Điều này không đúng.

Bản chất của for trong Python là:

Lặp qua từng phần tử của một đối tượng có thể lặp (Iterable).

Ví dụ:
'''
for item in iterable:
    ...
'''
Không phải:
'''
for(i=0;i<n;i++)
'''
như trong C hoặc Java.

Đây là một điểm khác biệt rất lớn của Python.

---

# 2. Iterable là gì?

Một Iterable là đối tượng có thể được duyệt từng phần tử.

Ví dụ:

text = "Python"

Python sẽ lấy lần lượt:
'''
P
↓
y
↓
t
↓
h
↓
o
↓
n
'''
⸻

Ví dụ với list:

numbers = [10, 20, 30]

Python sẽ lấy:

10
↓
20
↓
30

⸻

3. Ví dụ đầu tiên

for number in [10, 20, 30]:
    print(number)

Kết quả

10
20
30

⸻

4. range()

Đây là thứ được dùng nhiều nhất.

range(start, stop, step)

⸻

Chỉ có stop

for i in range(5):
    print(i)

Kết quả

0
1
2
3
4

Lưu ý

Không có số 5.

⸻

Có start

for i in range(1, 6):
    print(i)
1
2
3
4
5

⸻

Có step

for i in range(2, 11, 2):
    print(i)
2
4
6
8
10

⸻

Đếm ngược

for i in range(10, 0, -1):
    print(i)
10
9
8
...
1

⸻

5. range() thực chất là gì?

Nhiều người tưởng:

range(1000000000)

tạo ra một danh sách khổng lồ.

Không phải.

r = range(1000000000)

Nó chỉ tạo một đối tượng range, sinh giá trị khi cần (lazy evaluation).

Ví dụ:

print(range(5))

Kết quả:

range(0, 5)

Nếu muốn chuyển thành danh sách:

print(list(range(5)))
[0, 1, 2, 3, 4]

⸻

6. Duyệt chuỗi

text = "Python"
for ch in text:
    print(ch)

Kết quả

P
y
t
h
o
n

⸻

7. Duyệt List

fruits = ["Táo", "Cam", "Xoài"]
for fruit in fruits:
    print(fruit)

⸻

8. Duyệt Tuple

point = (10, 20)
for value in point:
    print(value)

⸻

9. Duyệt Set

numbers = {3, 1, 2}
for number in numbers:
    print(number)

Lưu ý:

Set không đảm bảo thứ tự.

⸻

10. Duyệt Dictionary

student = {
    "name": "An",
    "age": 20,
    "major": "CNTT"
}

Chỉ lấy key

for key in student:
    print(key)

⸻

Lấy value

for value in student.values():
    print(value)

⸻

Lấy cả key và value

for key, value in student.items():
    print(key, value)

Kết quả

name An
age 20
major CNTT

Đây là cách được sử dụng nhiều nhất khi làm việc với từ điển.

⸻

11. enumerate()

Rất quan trọng.

Thông thường

fruits = ["Táo", "Cam", "Xoài"]
index = 0
for fruit in fruits:
    print(index, fruit)
    index += 1

Pythonic

for index, fruit in enumerate(fruits):
    print(index, fruit)

Kết quả

0 Táo
1 Cam
2 Xoài

Có thể bắt đầu từ 1:

for index, fruit in enumerate(fruits, start=1):
    print(index, fruit)

⸻

12. zip()

Ghép nhiều iterable lại với nhau.

names = ["An", "Bình", "Lan"]
scores = [8.5, 7.0, 9.0]
for name, score in zip(names, scores):
    print(name, score)

Kết quả

An 8.5
Bình 7.0
Lan 9.0

Ứng dụng:

* Ghép tên và điểm.
* Ghép sản phẩm và giá.
* Ghép từ vựng và nghĩa.
* Ghép câu hỏi và đáp án.

⸻

13. reversed()

for i in reversed(range(5)):
    print(i)

Kết quả

4
3
2
1
0

⸻

14. sorted()

numbers = [5, 1, 9, 3]
for n in sorted(numbers):
    print(n)
1
3
5
9

Sắp xếp giảm dần:

for n in sorted(numbers, reverse=True):
    print(n)

⸻

15. break

for i in range(10):
    if i == 5:
        break
    print(i)

⸻

16. continue

for i in range(6):
    if i == 3:
        continue
    print(i)

Kết quả

0
1
2
4
5

⸻

17. for...else

Ít người biết.

for i in range(3):
    print(i)
else:
    print("Hoàn thành.")

Nếu có break:

for i in range(5):
    if i == 3:
        break
else:
    print("Done")

else sẽ không chạy.

Điều này tương tự while...else mà bạn đã học ở buổi trước.

⸻

18. Vòng lặp lồng nhau

for i in range(3):
    for j in range(3):
        print(i, j)

Kết quả

0 0
0 1
0 2
1 0
...

Ứng dụng:

* Ma trận.
* Bảng cửu chương.
* Xử lý ảnh.
* Game 2D.
* Sudoku.

⸻

19. Hiểu về Iterator

Khi viết:

for x in [10, 20, 30]:
    print(x)

Python thực hiện gần giống như:

it = iter([10, 20, 30])
while True:
    try:
        x = next(it)
        print(x)
    except StopIteration:
        break

Điều này giải thích vì sao rất nhiều đối tượng trong Python đều có thể dùng với for.

⸻

20. So sánh for và while

for	while
Biết dữ liệu cần duyệt	✔️
Duyệt list, tuple, dict	✔️
Duyệt file	✔️
Đếm bằng range()	✔️
Chưa biết số lần lặp	
Chờ nhập dữ liệu	
Chờ kết nối mạng	
Server chạy liên tục	

⸻

21. Pythonic

Không nên:

numbers = [10, 20, 30]
for i in range(len(numbers)):
    print(numbers[i])

Nên:

for number in numbers:
    print(number)

Nếu cần chỉ số:

for index, number in enumerate(numbers):
    print(index, number)

Đây là cách viết được khuyến nghị trong hầu hết các dự án Python.

⸻

22. Ví dụ thực tế

Tính tổng đơn hàng

prices = [120000, 50000, 75000]
total = 0
for price in prices:
    total += price
print(f"Tổng tiền: {total:,} VNĐ")

⸻

Tìm sản phẩm đắt nhất

prices = [120000, 50000, 75000]
max_price = prices[0]
for price in prices:
    if price > max_price:
        max_price = price
print(f"Giá cao nhất: {max_price:,} VNĐ")

⸻

Đếm số nguyên âm trong câu

text = "Python Programming"
count = 0
for ch in text.lower():
    if ch in "aeiou":
        count += 1
print("Số nguyên âm:", count)

⸻

23. Những lỗi phổ biến

Lỗi 1: Quên dùng items() khi duyệt dictionary

Sai:

for key, value in student:
    ...

Đúng:

for key, value in student.items():
    ...

⸻

Lỗi 2: Lạm dụng range(len(...))

Chỉ dùng khi thực sự cần truy cập theo chỉ số.

⸻

Lỗi 3: Thay đổi danh sách khi đang duyệt

Sai:

numbers = [1, 2, 3, 4]
for n in numbers:
    if n % 2 == 0:
        numbers.remove(n)

Điều này có thể khiến bạn bỏ sót phần tử hoặc gây lỗi logic. Ta sẽ học các cách xử lý an toàn hơn ở các buổi về danh sách.

⸻

24. Bài tập thực hành

Bài 1

In các số từ 1 đến 100.

⸻

Bài 2

In các số chẵn từ 2 đến 50.

⸻

Bài 3

Tính tổng các số từ 1 đến 100.

⸻

Bài 4

In bảng cửu chương từ 2 đến 9.

Gợi ý: Dùng vòng lặp lồng nhau.

⸻

Bài 5

Cho danh sách:

scores = [8.5, 7.0, 9.5, 6.0, 8.0]

* Tính điểm trung bình.
* Tìm điểm cao nhất.
* Tìm điểm thấp nhất.

(Hãy thử tự làm trước, sau đó ở buổi về hàm dựng sẵn như sum(), max(), min(), chúng ta sẽ so sánh các cách.)

⸻

Bài 6

Cho dictionary:

student = {
    "name": "An",
    "age": 20,
    "major": "CNTT"
}

In toàn bộ khóa và giá trị.

⸻

Bài 7

Cho hai danh sách:

subjects = ["Toán", "Văn", "Anh"]
scores = [8.5, 7.0, 9.0]

Dùng zip() để in:

Toán: 8.5
Văn: 7.0
Anh: 9.0

⸻

Mini Project: Hệ thống quản lý điểm sinh viên

Viết chương trình:

1. Tạo danh sách tên sinh viên.
2. Tạo danh sách điểm tương ứng.
3. Dùng zip() để in bảng điểm.
4. Tính:
    * Điểm trung bình.
    * Điểm cao nhất.
    * Điểm thấp nhất.
5. Dùng enumerate() để đánh số thứ tự.

Ví dụ:

=============================
DANH SÁCH ĐIỂM
=============================
1. An    : 8.5
2. Bình  : 7.0
3. Lan   : 9.0
-----------------------------
Điểm TB      : 8.17
Cao nhất     : 9.0
Thấp nhất    : 7.0
=============================

⸻

Tổng kết buổi 8

Bạn đã học được:

* ✅ Bản chất của for.
* ✅ Khái niệm Iterable và Iterator.
* ✅ range() và cơ chế hoạt động.
* ✅ Duyệt chuỗi, list, tuple, set, dictionary.
* ✅ enumerate().
* ✅ zip().
* ✅ reversed().
* ✅ sorted().
* ✅ break, continue, for...else.
* ✅ Vòng lặp lồng nhau.
* ✅ Phong cách viết Pythonic.

⸻

Góc lập trình viên chuyên nghiệp

Trong các dự án Python thực tế, for là vòng lặp được sử dụng nhiều nhất vì phần lớn công việc là xử lý tập dữ liệu: đọc file, duyệt kết quả truy vấn cơ sở dữ liệu, xử lý JSON, API, danh sách người dùng hoặc bản ghi.

Một nguyên tắc quan trọng là:

* Ưu tiên duyệt trực tiếp phần tử (for item in items) khi không cần chỉ số.
* Dùng enumerate() khi cần cả chỉ số và phần tử.
* Dùng zip() khi cần xử lý song song nhiều tập dữ liệu.

Điều này giúp mã nguồn ngắn gọn, dễ đọc và đúng với phong cách Python.

Chuẩn bị cho Buổi 9

Ở buổi tiếp theo, chúng ta sẽ học hàm (Functions) – một trong những nền tảng quan trọng nhất của lập trình. Bạn sẽ học cách định nghĩa hàm, tham số, giá trị trả về, phạm vi biến (scope), *args, **kwargs, type hints và cách thiết kế các hàm chuyên nghiệp theo chuẩn Python hiện đại. Đây là bước chuyển từ “viết script” sang “viết phần mềm”.