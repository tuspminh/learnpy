Để phân biệt một file PDF là PDF văn bản (Digital/Searchable PDF) hay PDF ảnh quét (Scanned PDF) bằng Python, chúng ta dựa trên một nguyên lý đơn giản:

> PDF văn bản sẽ chứa dữ liệu text nguyên bản nằm trên các trang, trong khi PDF ảnh quét chỉ chứa các đối tượng hình ảnh (hoặc text rỗng) và không thể copy chữ trực tiếp bằng chuột.

Cách tối ưu nhất là sử dụng thư viện `pypdf` vì nó nhẹ, nhanh và không cần cài đặt thêm công cụ phụ thuộc.

* * *

## Cách 1: Kiểm tra dung lượng Text trích xuất được (Khuyên dùng)

Chúng ta sẽ lặp qua vài trang đầu tiên của file PDF và thử trích xuất văn bản. Nếu tổng số ký tự lấy ra gần như bằng 0 (hoặc cực kỳ ít), chứng tỏ file đó là ảnh quét.
    
    
    from pypdf import PdfReader
    
    def phan_biet_pdf(file_path, threshold=20):
        try:
            reader = PdfReader(file_path)
            total_chars = 0
            
            # Chỉ cần kiểm tra tối đa 3 trang đầu để tiết kiệm thời gian
            pages_to_check = min(3, len(reader.pages))
            
            for i in range(pages_to_check):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    # Loại bỏ khoảng trắng và xuống dòng để đếm chính xác ký tự chữ
                    total_chars += len(page_text.strip())
            
            # Tính trung bình số ký tự trên mỗi trang đã kiểm tra
            avg_chars = total_chars / pages_to_check
            
            print(f"Số ký tự trung bình mỗi trang: {avg_chars:.1f}")
            
            # Nếu trung bình mỗi trang có ít hơn `threshold` ký tự -> PDF Scan
            if avg_chars < threshold:
                return "Scanned PDF (File ảnh quét - Cần dùng OCR)"
            else:
                return "Digital PDF (File chữ - Có thể copy/trích xuất trực tiếp)"
                
        except Exception as e:
            return f"Lỗi khi đọc file: {str(e)}"
    
    # Sử dụng thử
    file_cua_ban = "tai_lieu_can_kiem_tra.pdf"
    ket_qua = phan_biet_pdf(file_cua_ban)
    print(f"Kết luận: {ket_qua}")
    

* * *

## Cách 2: Kiểm tra cấu trúc phần tử (Kiểm tra xem có chứa ảnh không)

Cách này nâng cao hơn, dùng để kiểm tra xem trên trang PDF có chứa đối tượng hình ảnh (`/XObject` dạng `/Image`) chiếm toàn bộ không gian trang hay không. Tuy nhiên, một số file PDF văn bản vẫn có thể chèn ảnh đi kèm, nên cách này thường bổ trợ cho cách 1.
    
    
    from pypdf import PdfReader
    
    def kiem_tra_doi_tuong_anh(file_path):
        reader = PdfReader(file_path)
        page = reader.pages[0] # Kiểm tra trang đầu tiên
        
        # Kiểm tra xem trang có chứa tài nguyên đồ họa/hình ảnh không
        if "/Resources" in page and "/XObject" in page["/Resources"]:
            xobject = page["/Resources"]["/XObject"].get_object()
            for obj in xobject:
                if xobject[obj]["/Subtype"] == "/Image":
                    return "Trang này có chứa hình ảnh!"
                    
        return "Không phát hiện hình ảnh lớn!"
    

* * *

## Tổng kết quy trình xử lý tự động trong dự án (Workflow)

Khi làm hệ thống tự động hóa (RPA hoặc xử lý dữ liệu lớn), bạn nên kết hợp các thư viện lại theo kiến trúc sau để tối ưu hóa hiệu năng và độ chính xác:
    
    
    [ File PDF Đầu Vào ]
             │
             ▼
    [ Chạy hàm kiểm tra (Cách 1) ]
             │
             ├──► Nếu là Digital PDF ──► Dùng `pdfplumber` hoặc `pypdf` để lấy text (Rất nhanh)
             │
             └──► Nếu là Scanned PDF ──► Chuyển hướng sang dùng `PaddleOCR` (Chậm hơn nhưng chính xác)
    

Bạn có muốn tôi tích hợp hàm phân biệt này vào một đoạn code hoàn chỉnh, tự động nhận diện loại file rồi tự quyết định dùng `pypdf` hay `PaddleOCR` để cào dữ liệu luôn không?