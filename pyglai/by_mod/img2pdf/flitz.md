Để chuyển đổi cả file PDF (tất cả các trang) thành ảnh JPG, PyMuPDF (fitz) là lựa chọn tối ưu nhất vì nó xử lý rất nhanh, không lỗi font và không yêu cầu cài đặt thêm công cụ phụ trợ (như Poppler).

Dưới đây là đoạn mã nguồn đầy đủ giúp bạn chuyển đổi toàn bộ các trang trong file PDF sang JPG, có kèm cấu hình tăng độ phân giải (DPI) để ảnh đầu ra sắc nét, không bị mờ chữ.

## 1\. Cài đặt thư viện

Chạy lệnh sau trong terminal hoặc command prompt:
    
    
    pip install PyMuPDF
    

## 2\. Mã nguồn chuyển đổi toàn bộ file

Đoạn code này sẽ tự động đếm tổng số trang và lưu từng trang thành một file JPG riêng biệt:
    
    
    import fitz  # Thư viện PyMuPDF
    
    # 1. Đường dẫn file PDF đầu vào
    pdf_path = "document.pdf"
    
    # 2. Mở tài liệu PDF
    doc = fitz.open(pdf_path)
    
    # 3. Thiết lập độ nét (DPI). 300 DPI là tiêu chuẩn cho ảnh sắc nét
    zoom = 300 / 72  # 72 là DPI mặc định của PDF
    matrix = fitz.Matrix(zoom, zoom)
    
    print(f"Bắt đầu chuyển đổi... Tổng số trang: {len(doc)}")
    
    # 4. Lặp qua từng trang và lưu thành file JPG
    for i, page in enumerate(doc):
      # Áp dụng độ nét matrix vào trang
      pix = page.get_pixmap(matrix=matrix)
    
      # Đặt tên file theo số trang (ví dụ: trang_1.jpg, trang_2.jpg)
      output_name = f"trang_{i + 1}.jpg"
    
      # Lưu file dưới định dạng JPG
      pix.save(output_name)
      print(f" Đã lưu: {output_name}")
    
    print(" Hoàn thành chuyển đổi toàn bộ file!")
    

## Các tùy chỉnh thêm nếu bạn cần:

  * Tạo thư mục riêng: Nếu file PDF có hàng trăm trang, bạn nên dùng thư viện `os` để tạo một thư mục mới và lưu ảnh vào đó cho gọn gàng.
  * Nén dung lượng: Bạn có thể giảm thông số `zoom` xuống (ví dụ thành `150 / 72`) nếu muốn file ảnh nhẹ hơn và chuyển đổi nhanh hơn nữa.



Nếu bạn cần hỗ trợ tự động tạo thư mục lưu ảnh theo tên file PDF hoặc muốn ghép tất cả các trang thành một file ảnh dài duy nhất, hãy cho tôi biết nhé!