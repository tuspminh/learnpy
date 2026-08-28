Nếu file PDF của bạn thuần tiếng Anh, mọi việc sẽ trở nên đơn giản hơn rất nhiều. Bạn không cần phải cài thêm gói ngôn ngữ phụ nào cả, vì tiếng Anh (`eng`) luôn là ngôn ngữ mặc định của các công cụ OCR.

Dưới đây là mã nguồn tối ưu bằng `fitz` (PyMuPDF) dành riêng cho file PDF tiếng Anh:

## 1\. Nếu là PDF chữ thông thường (Đọc siêu tốc)

Không cần cài Tesseract, chạy trực tiếp để trích xuất chữ:
    
    
    import pymupdf
    
    doc = pymupdf.open("tailieu_tienganh.pdf")
    text = "".join([page.get_text() for page in doc])
    
    with open("output_eng.txt", "w", encoding="utf-8") as f:
      f.write(text)
    
    print("Hoàn thành trích xuất tiếng Anh!")
    

## 2\. Nếu là PDF ảnh quét (Scanned PDF)

Bạn vẫn cần cài Tesseract OCR phần mềm gốc trên máy (Windows/Mac/Linux), nhưng không cần tích chọn tải thêm gói ngôn ngữ tiếng Việt lúc cài đặt nữa.

Trong code, bạn chỉ cần đổi tham số nhận diện thành `lang='eng'`:
    
    
    import io
    import pymupdf
    from PIL import Image
    import pytesseract
    
    # Cấu hình Tesseract (Chỉ dành cho Windows, Mac/Linux hãy xóa/comment dòng này)
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    
    doc = pymupdf.open("scanned_eng.pdf")
    full_text = []
    
    for i, page in enumerate(doc):
      print(f"Đang OCR trang {i+1}/{len(doc)}...")
    
      # Tăng nét ảnh lên 2 lần để nhận diện tiếng Anh chính xác nhất
      pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
      img_data = pix.tobytes("png")
      img = Image.open(io.BytesIO(img_data))
    
      # Nhận diện tiếng Anh (Mặc định 'eng')
      text = pytesseract.image_to_string(img, lang="eng")
      full_text.append(f"--- PAGE {i+1} ---\n{text}")
    
    with open("ocr_eng_output.txt", "w", encoding="utf-8") as f:
      f.write("\n".join(full_text))
    
    print("Đã OCR xong toàn bộ file tiếng Anh!")
    

Bạn có cần hỗ trợ cài đặt Tesseract OCR trên hệ điều hành đang dùng để chạy đoạn code quét ảnh này không?