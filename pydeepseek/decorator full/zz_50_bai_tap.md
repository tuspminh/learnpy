Dưới đây là **50 bài tập lập trình Python về chủ đề Decorator**, được phân chia theo 5 cấp độ từ cơ bản đến nâng cao. Mỗi bài tập đều có yêu cầu cụ thể để bạn tự thực hành.

---

## 📘 CẤP ĐỘ 1: CƠ BẢN (Bài 1–10)

1. **Decorator in ra thời gian**  
   Viết decorator `timing` in ra thời gian thực thi của hàm.

2. **Decorator in ra tên hàm**  
   Viết decorator `log_function_name` in ra tên hàm mỗi khi nó được gọi.

3. **Decorator in ra tham số**  
   Viết decorator `log_arguments` in ra các tham số được truyền vào hàm.

4. **Decorator chuyển kết quả thành chữ hoa**  
   Viết decorator `uppercase` biến kết quả trả về của hàm thành chữ hoa.

5. **Decorator nhân đôi kết quả**  
   Viết decorator `double_return` nhân đôi giá trị trả về của hàm.

6. **Decorator bình phương kết quả**  
   Viết decorator `square_result` trả về bình phương của kết quả hàm.

7. **Decorator in ra dòng phân cách**  
   Viết decorator `separator` in ra 30 dấu `=` trước và sau khi gọi hàm.

8. **Decorator kiểm tra kiểu dữ liệu trả về**  
   Viết decorator `ensure_string` đảm bảo hàm trả về kiểu `str`, nếu không thì chuyển thành chuỗi.

9. **Decorator bỏ qua lỗi**  
   Viết decorator `ignore_error` bỏ qua mọi lỗi và in ra thông báo lỗi thay vì dừng chương trình.

10. **Decorator in ra thông báo bắt đầu và kết thúc**  
    Viết decorator `start_end` in ra "Bắt đầu..." và "Kết thúc..." khi gọi hàm.

---

## 📗 CẤP ĐỘ 2: DECORATOR CÓ THAM SỐ (Bài 11–20)

11. **Decorator lặp lại N lần**  
    Viết decorator `repeat(n)` để gọi hàm `n` lần.

12. **Decorator in ra N dòng phân cách**  
    Viết decorator `separator_n(n)` in ra `n` dấu `=` trước và sau khi gọi hàm.

13. **Decorator thời gian chờ**  
    Viết decorator `delay(seconds)` chờ `seconds` giây trước khi gọi hàm.

14. **Decorator in ra kết quả với tiền tố**  
    Viết decorator `prefix(prefix_str)` thêm tiền tố vào kết quả trả về.

15. **Decorator kiểm tra điều kiện**  
    Viết decorator `condition(predicate)` chỉ gọi hàm nếu `predicate` trả về `True`.

16. **Decorator lọc kết quả**  
    Viết decorator `filter_result(func_filter)` áp dụng hàm lọc lên kết quả trả về.

17. **Decorator chuyển đổi đơn vị**  
    Viết decorator `unit(scale)` nhân kết quả với `scale`.

18. **Decorator ghi log ra file**  
    Viết decorator `log_to_file(filename)` ghi thông tin gọi hàm vào file.

19. **Decorator retry**  
    Viết decorator `retry(times)` thử lại hàm `times` lần nếu có lỗi.

20. **Decorator validate**  
    Viết decorator `validate(validator)` kiểm tra tham số đầu vào bằng hàm `validator`.

---

## 📙 CẤP ĐỘ 3: DECORATOR LỒNG NHAU & KẾT HỢP (Bài 21–30)

21. **Kết hợp 2 decorator**  
    Áp dụng cả `timing` và `log_arguments` cho một hàm.

22. **Decorator chuyển đổi kiểu dữ liệu đầu vào**  
    Viết decorator `cast_types` tự động ép kiểu tham số theo annotation.

23. **Decorator cache đơn giản**  
    Viết decorator `cache` lưu kết quả của hàm với tham số giống nhau.

24. **Decorator đếm số lần gọi**  
    Viết decorator `count_calls` đếm số lần hàm được gọi.

25. **Decorator reset biến đếm**  
    Viết decorator `reset_counter` cho phép reset số lần gọi.

26. **Decorator in ra thời gian chi tiết**  
    In ra cả thời gian bắt đầu, kết thúc và thời gian thực thi.

27. **Decorator ghi log cấu trúc JSON**  
    Ghi log thành chuỗi JSON vào file.

28. **Decorator kiểm tra quyền**  
    Viết decorator `permission(role)` kiểm tra role trước khi gọi hàm.

29. **Decorator giới hạn tốc độ**  
    Viết decorator `rate_limit(max_calls, period)` giới hạn số lần gọi trong khoảng thời gian.

30. **Decorator thông báo qua email (mô phỏng)**  
    Gửi thông báo mô phỏng khi hàm chạy lâu hơn ngưỡng.

---

## 📒 CẤP ĐỘ 4: CLASS-BASED DECORATOR (Bài 31–40)

31. **Class decorator cơ bản**  
    Viết class `MyDecorator` in ra tên hàm khi gọi.

32. **Class decorator có tham số**  
    Viết class `RepeatDecorator(n)` để lặp hàm `n` lần.

33. **Class decorator đếm số lần gọi**  
    Viết class `CallCounter` có thuộc tính `count`.

34. **Class decorator lưu kết quả vào danh sách**  
    Lưu tất cả kết quả trả về vào một danh sách.

35. **Class decorator kiểm tra tham số**  
    Kiểm tra tham số đầu vào có phải số nguyên không.

36. **Class decorator tự động in ra docstring**  
    In ra `__doc__` của hàm trước khi gọi.

37. **Class decorator chuyển đổi kết quả thành tuple**  
    Luôn trả về kết quả dạng tuple.

38. **Class decorator với `__call__`**  
    Ghi log mỗi lần gọi hàm qua `__call__`.

39. **Class decorator lưu trạng thái**  
    Lưu trạng thái (state) giữa các lần gọi.

40. **Class decorator hỗ trợ cả hàm và phương thức**  
    Viết class decorator hoạt động được với cả hàm thông thường và phương thức của class.

---

## 📕 CẤP ĐỘ 5: NÂNG CAO – ỨNG DỤNG THỰC TẾ (Bài 41–50)

41. **Decorator kiểm tra kiểu dữ liệu đầu vào (type checking)**  
    Dùng annotation để kiểm tra kiểu tham số.

42. **Decorator memoization (cache nâng cao)**  
    Cache có giới hạn kích thước (LRU cache).

43. **Decorator pipeline**  
    Cho phép xâu chuỗi nhiều decorator theo thứ tự.

44. **Decorator async support**  
    Viết decorator hỗ trợ cả hàm đồng bộ và bất đồng bộ.

45. **Decorator singleton**  
    Đảm bảo class chỉ có một instance duy nhất.

46. **Decorator debug chi tiết**  
    In ra local variables, stack trace khi có lỗi.

47. **Decorator kiểm tra hiệu năng**  
    In ra báo cáo hiệu năng chi tiết: CPU time, memory usage (mô phỏng).

48. **Decorator gọi API khi có lỗi**  
    Gọi một API giả định khi hàm gặp lỗi.

49. **Decorator tự động thử lại với backoff**  
    Thử lại hàm với thời gian chờ tăng dần (exponential backoff).

50. **Decorator chuyển đổi dữ liệu đầu vào/đầu ra theo schema**  
    Dùng Pydantic hoặc dataclass để validate dữ liệu (mô phỏng).

---

## 💡 Gợi ý cách học:

- Mỗi bài nên viết **ít nhất 2–3 ví dụ sử dụng**.
- Kết hợp kiểm tra với `functools.wraps` để giữ nguyên metadata của hàm.
- Thử nghiệm với cả hàm thông thường và phương thức trong class.

Chúc bạn học tốt! Nếu bạn cần lời giải chi tiết cho bài nào, mình sẵn sàng hỗ trợ!