Dưới đây là đoạn code mẫu sử dụng thư viện `pypdf` để trích xuất các trang cụ thể từ một file PDF có sẵn và lưu thành một file PDF mới.
    
    
    from pypdf import PdfReader, PdfWriter
    
    def extract_pages(input_pdf, output_pdf, pages_to_extract):
        """
        Trích xuất các trang cụ thể từ file PDF.
        
        :param input_pdf: Đường dẫn file PDF gốc
        :param output_pdf: Đường dẫn file PDF kết quả sau khi trích xuất
        :param pages_to_extract: Danh sách các số trang cần lấy (bắt đầu từ trang 1)
        """
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        # Duyệt qua các số trang được yêu cầu
        for page_num in pages_to_extract:
            # pypdf đếm số trang từ 0, nên cần trừ đi 1
            zero_indexed_page = page_num - 1 
            
            # Kiểm tra xem số trang có hợp lệ không
            if 0 <= zero_indexed_page < len(reader.pages):
                page = reader.pages[zero_indexed_page]
                writer.add_page(page)
            else:
                print(f"Cảnh báo: Trang {page_num} không tồn tại trong file gốc.")
    
        # Lưu lại thành file PDF mới
        with open(output_pdf, "wb") as f:
            writer.write(f)
        print(f" Đã trích xuất thành công vào file: {output_pdf}")
    
    # --- CÁCH SỬ DỤNG ---
    # Ví dụ: Trích xuất trang 1, trang 3 và trang 5 từ file 'tailieu.pdf'
    pages_list = [1, 3, 5] 
    extract_pages("tailieu.pdf", "trang_da_trich_xuat.pdf", pages_list)
    

## Các tùy chọn trích xuất phổ biến khác bằng pypdf:

  * Trích xuất một khoảng trang liên tục (Ví dụ: Từ trang 5 đến trang 10):
        
        # Thay thế vòng lặp ở đoạn code trên bằng cách dùng range()
        for page_num in range(5, 11): # Lấy từ trang 5 đến hết trang 10
            writer.add_page(reader.pages[page_num - 1])
        

  * Trích xuất tất cả các trang chẵn hoặc lẻ:
        
        # Lấy tất cả trang lẻ (trang 1, 3, 5...)
        for i in range(0, len(reader.pages), 2):
            writer.add_page(reader.pages[i])
        




Nếu bạn muốn nâng cao hơn, tôi có thể hướng dẫn bạn cách:

  * Đặt mật khẩu bảo mật cho file PDF mới tạo ra.
  * Xoay dọc/ngang (rotate) các trang được trích xuất trước khi lưu.
  * Xử lý trích xuất hàng loạt file PDF cùng lúc từ một thư mục.



Bạn có muốn bổ sung tính năng nào ở trên vào code không?