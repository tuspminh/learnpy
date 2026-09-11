Thư viện `pypdf` là công cụ thuần Python (pure-Python) phổ biến nhất để xử lý PDF nhờ ưu điểm nhẹ, không cần cài đặt thêm công cụ phụ thuộc và chạy rất nhanh.

Dưới đây là chi tiết các tính năng cốt lõi của `pypdf` từ cơ bản đến nâng cao.

* * *

## 1\. Trích xuất Text và Metadata (Thông tin file)

Đây là tính năng bạn vừa sử dụng, nhưng bạn có thể lấy thêm nhiều thông tin chi tiết hơn của file PDF.
    
    
    from pypdf import PdfReader
    
    reader = PdfReader("tai_lieu.pdf")
    
    # 1. Lấy số lượng trang
    num_pages = len(reader.pages)
    
    # 2. Lấy thông tin Metadata (Tác giả, tiêu đề, phần mềm tạo...)
    meta = reader.metadata
    print(f"Tiêu đề: {meta.title}")
    print(f"Tác giả: {meta.author}")
    print(f"Phần mềm tạo: {meta.creator}")
    
    # 3. Trích xuất text từ một trang cụ thể (Ví dụ: Trang đầu tiên)
    page = reader.pages[0]
    text = page.extract_text()
    

## 2\. Cắt và Gộp file PDF (Split & Merge)

`pypdf` cung cấp class `PdfMerger` để gộp nhiều file và cho phép lập chỉ mục để cắt file dễ dàng.

## Gộp nhiều file PDF thành một:
    
    
    from pypdf import PdfMerger
    
    merger = PdfMerger()
    
    # Thêm toàn bộ file vào danh sách gộp
    merger.append("file1.pdf")
    merger.append("file2.pdf")
    
    # Hoặc chèn file 3 vào vị trí trang số 2 của file tổng
    merger.merge(2, "file3.pdf")
    
    merger.write("file_tong_hop.pdf")
    merger.close()
    

## Cắt file PDF (Chỉ lấy một số trang nhất định):
    
    
    from pypdf import PdfReader, PdfWriter
    
    reader = PdfReader("file_goc.pdf")
    writer = PdfWriter()
    
    # Chỉ lấy trang 1, trang 3 và trang 5 (Lưu ý: Python đếm từ 0)
    trang_can_lay = [0, 2, 4]
    
    for index in trang_can_lay:
        writer.add_page(reader.pages[index])
    
    with open("file_da_cat.pdf", "wb") as f:
        writer.write(f)
    

## 3\. Xoay trang và Thay đổi kích thước

Bạn có thể xoay các trang bị ngược hoặc bị ngang theo góc 90, 180, 270 độ.
    
    
    from pypdf import PdfReader, PdfWriter
    
    reader = PdfReader("input.pdf")
    writer = PdfWriter()
    
    page = reader.pages[0]
    # Xoay theo chiều kim đồng hồ 90 độ
    page.rotate(90) 
    
    writer.add_page(page)
    with open("xoay_trang.pdf", "wb") as f:
        writer.write(f)
    

## 4\. Mã hóa và Đặt mật khẩu bảo mật (Password Protection)

Bạn có thể đặt mật khẩu để bảo vệ file PDF không cho người khác mở nếu không có quyền.
    
    
    from pypdf import PdfReader, PdfWriter
    
    reader = PdfReader("input.pdf")
    writer = PdfWriter()
    
    # Sao chép toàn bộ trang sang writer
    for page in reader.pages:
        writer.add_page(page)
    
    # Đặt mật khẩu cho file xuất ra
    writer.encrypt("mat_khau_cua_ban_123")
    
    with open("file_bao_mat.pdf", "wb") as f:
        writer.write(f)
    

* * *

## ⚠️ Một số hạn chế của `pypdf` bạn cần lưu ý:

  1. Không hỗ trợ OCR: Nếu PDF là ảnh quét (chụp từ điện thoại, scan giấy), `pypdf` sẽ trả về chuỗi rỗng.
  2. Bố cục bảng biểu (Table): Khi trích xuất văn bản từ bảng, `pypdf` sẽ nối các ô thành một dòng văn bản liên tục, làm mất cấu trúc cột.
  3. Không chỉnh sửa trực tiếp text: Bạn không thể dùng `pypdf` để sửa một từ ngữ bất kỳ nằm bên trong file PDF có sẵn (thư viện chỉ hỗ trợ đọc, sao chép trang, gộp trang và tạo file mới).



Bạn đang muốn áp dụng `pypdf` vào bài toán cụ thể nào (như tự động hóa gộp file báo cáo, cắt trang, hay phân tích dữ liệu)? Hãy chia sẻ để tôi viết đoạn mã tối ưu riêng cho bạn nhé!