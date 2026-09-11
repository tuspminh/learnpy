Thư viện `pytesseract` là một wrapper Python dành cho Tesseract OCR Engine của Google. Đây là giải pháp bắt buộc phải dùng khi file PDF của bạn là dạng ảnh quét (scanned PDF) — tức là tài liệu được chụp lại bằng điện thoại, scan từ máy giấy, hoặc file PDF khóa không cho copy chữ.

Vì `pytesseract` chỉ đọc được hình ảnh, nên khi làm việc với PDF, chúng ta thường kết hợp nó với thư viện `pdf2image` để chuyển các trang PDF thành ảnh trước khi nhận diện chữ.

* * *

## 🛠️ Bước 1: Cài đặt công cụ bắt buộc

Khác với các thư viện thuần Python, Tesseract yêu cầu bạn phải cài đặt phần mềm core vào máy tính trước.

  1. Cài đặt Tesseract OCR Engine:

     * Windows: Tải file cài đặt `.exe` từ UB Mannheim Tesseract và cài đặt. Hãy nhớ đường dẫn (thường là `C:\Program Files\Tesseract-OCR\tesseract.exe`).
     * Ubuntu/Linux: Chạy lệnh `sudo apt install tesseract-ocr tesseract-ocr-vie` (để cài thêm ngôn ngữ tiếng Việt).
     * Mac: Chạy lệnh `brew install tesseract tesseract-lang`.

  2. Cài đặt thư viện Python:
         
         pip install pytesseract pdf2image pillow
         

_(Lưu ý:`pdf2image` yêu cầu máy tính có công cụ `poppler`. Trên Windows, bạn cần tải poppler và thêm vào biến môi trường PATH)._



## 2\. Code mẫu chuyển Scanned PDF thành Text (Hỗ trợ Tiếng Việt)

Đoạn code dưới đây sẽ chuyển từng trang PDF thành ảnh, sau đó dùng `pytesseract` để quét chữ tiếng Việt và tiếng Anh.
    
    
    from pdf2image import convert_from_path
    import pytesseract
    import os
    
    # --- CHỈ DÀNH CHO WINDOWS ---
    # Nếu dùng Windows, bạn phải chỉ định đường dẫn tới file tesseract.exe
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # poppler_path = r"C:\path\to\poppler-xx\bin" 
    # ----------------------------
    
    pdf_path = "tai_lieu_scan.pdf"
    output_text_file = "ket_qua_ocr.txt"
    
    # 1. Chuyển đổi các trang PDF thành danh sách hình ảnh (độ phân giải 200 DPI)
    # Nếu dùng Windows, thêm tham số: poppler_path=poppler_path
    pages = convert_from_path(pdf_path, dpi=200)
    
    full_text = ""
    
    # 2. Lặp qua từng trang ảnh để OCR
    for i, page_img in enumerate(pages):
        print(f"Đang xử lý trang {i+1}...")
        
        # Sử dụng cấu hình ngôn ngữ: 'vie' (Tiếng Việt) và 'eng' (Tiếng Anh)
        # Kết nối bằng dấu '+'
        text = pytesseract.image_to_string(page_img, lang="vie+eng")
        
        full_text += f"--- TRANG {i+1} ---\n" + text + "\n\n"
    
    # 3. Ghi kết quả ra file text
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print("Đã hoàn thành OCR PDF sang Text!")
    

## 3\. Các cấu hình nâng cao (Page Segmentation Modes - PSM)

Tesseract cung cấp các chế độ quét (PSM) khác nhau tùy thuộc vào định dạng trang tài liệu của bạn. Bạn có thể truyền cấu hình này vào tham số `config`.
    
    
    # Ví dụ: Cấu hình PSM 6 - Coi toàn bộ hình ảnh là một khối văn bản duy nhất
    custom_config = r'--psm 6'
    text = pytesseract.image_to_string(page_img, lang="vie", config=custom_config)
    

Một số chế độ PSM phổ biến:

  * `--psm 3`: Tự động phân tích bố cục (Mặc định).
  * `--psm 4`: Giả định văn bản có nhiều cột, kích thước chữ khác nhau (Phù hợp cho bài báo, tạp chí).
  * `--psm 6`: Coi hình ảnh là một khối văn bản duy nhất (Phù hợp cho một trang sách thông thường).
  * `--psm 11`: Tìm kiếm càng nhiều chữ càng tốt mà không cần quan tâm đến thứ tự (Tìm chữ trên nhãn mác, biển báo).



* * *

## 💡 Đánh giá ưu & nhược điểm của `pytesseract`

  * Ưu điểm: Cứu cánh duy nhất cho file PDF dạng ảnh; Hỗ trợ đa ngôn ngữ (bao gồm tiếng Việt) rất tốt nếu ảnh rõ nét; Hoàn toàn miễn phí và mã nguồn mở.
  * Nhược điểm: Tốc độ xử lý tương đối chậm; Yêu cầu cài đặt công cụ bên ngoài phức tạp; Độ chính xác phụ thuộc hoàn toàn vào chất lượng ảnh quét (ảnh mờ, nghiêng, nhiễu sẽ bị sai chữ).



Nếu bạn gặp khó khăn trong bước cài đặt Tesseract / Poppler trên hệ điều hành của bạn, hoặc muốn tìm hiểu các công cụ OCR hiện đại hơn như EasyOCR hay PaddleOCR (không cần cài phần mềm core), hãy cho tôi biết nhé!