Để chuyển đổi file PDF dạng ảnh quét (Scanned PDF) thành văn bản, bạn cần sử dụng kỹ thuật OCR (Nhận diện ký tự quang học). Kết hợp `pdf2image` (chuyển PDF thành ảnh) và `pytesseract` (nhận diện chữ) là giải pháp phổ biến nhất.

## Các bước chuẩn bị hệ thống

Vì OCR cần công cụ bên ngoài, bạn không thể chỉ cài qua `pip` mà cần cài đặt phần mềm lên máy tính:

  1. Cài đặt Tesseract OCR:

     * Windows: Tải bản cài đặt `.exe` từ GitHub (tìm bản của UB Mannheim). Sau khi cài, ghi lại đường dẫn (thường là `C:\Program Files\Tesseract-OCR\tesseract.exe`).
     * Mac: Chạy lệnh `brew install tesseract`.
     * Linux: Chạy lệnh `sudo apt install tesseract-ocr`.

  2. Cài đặt gói ngôn ngữ tiếng Việt:

     * Khi cài đặt trên Windows, tích chọn phần Additional script data và Additional language data -> chọn Vietnamese.

  3. Cài đặt Poppler (bắt buộc cho pdf2image):

     * Windows: Tải file zip poppler, giải nén và copy đường dẫn đến thư mục `bin`.
     * Mac: Chạy lệnh `brew install poppler`.




## Cài đặt thư viện Python

Chạy lệnh sau trong terminal hoặc cmd:
    
    
    pip install pytesseract pdf2image pillow
    

## Mã nguồn Python

Đoạn code dưới đây sẽ chuyển từng trang PDF thành hình ảnh, sau đó dùng Tesseract để đọc chữ tiếng Việt (`vie`) và lưu lại:
    
    
    from pathlib import Path
    from pdf2image import convert_from_path
    import pytesseract
    
    # --- CẤU HÌNH ĐƯỜNG DẪN (CHỈ DÀNH CHO WINDOWS) ---
    # Nếu dùng Mac/Linux, bạn có thể xóa hoặc comment 2 dòng cấu hình này.
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    PATH_POPPLER = r"C:\path\to\poppler\bin"  # Thay bằng đường dẫn poppler của bạn
    
    
    def scanned_pdf_to_text(pdf_path, output_txt_path):
      # 1. Chuyển đổi các trang PDF thành danh sách ảnh
      # Nếu dùng Mac/Linux: bỏ tham số poppler_path
      pages = convert_from_path(pdf_path, dpi=300, poppler_path=PATH_POPPLER)
    
      full_text = []
    
      # 2. Duyệt qua từng ảnh để nhận diện chữ
      for i, page_img in enumerate(pages):
        print(f"Đang xử lý trang {i+1}/{len(pages)}...")
    
        # Nhận diện tiếng Việt ('vie'). Nếu tài liệu tiếng Anh, đổi thành 'eng'
        text = pytesseract.image_to_string(page_img, lang="vie")
    
        full_text.append(f"--- TRANG {i+1} ---\n{text}\n")
    
      # 3. Lưu toàn bộ nội dung ra file txt
      with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
      print(f"Xử lý thành công! File kết quả: {output_txt_path}")
    
    
    # Chạy thử nghiệm
    if __name__ == "__main__":
      file_pdf = "tai_lieu_quet.pdf"
      file_txt = "ket_qua_ocr.txt"
      scanned_pdf_to_text(file_pdf, file_txt)
    

Nếu bạn gặp khó khăn trong bước cài đặt Tesseract/Poppler trên hệ điều hành của mình, hãy cho tôi biết bạn đang dùng Windows, Mac hay Linux để tôi hướng dẫn từng bước cấu hình chi tiết nhé!