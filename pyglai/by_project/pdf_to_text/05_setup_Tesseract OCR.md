Để chạy được đoạn code OCR phía trên cho Windows, bạn cần cài đặt phần mềm Tesseract OCR lên máy tính theo 3 bước cực kỳ đơn giản sau đây:

## Bước 1: Tải bộ cài đặt Tesseract cho Windows

  1. Truy cập vào trang tải file cài đặt chính thức: Tesseract OCR W64.
  2. Tìm và click vào dòng đầu tiên (bản mới nhất) có dạng: `tesseract-ocr-w64-setup-vX.X.X.XXXXXXXX.exe` để tải về máy.



## Bước 2: Cài đặt phần mềm

  1. Mở file `.exe` vừa tải về → Chọn ngôn ngữ cài đặt là English.
  2. Nhấn Next và chọn I accept the agreement.
  3. Nhấn Next liên tiếp cho đến phần Choose Components (Chọn thành phần):

     * Vì bạn chỉ dùng tiếng Anh, bạn có thể bấm Next luôn để bỏ qua bước tải gói ngôn ngữ bổ sung.

  4. Lưu ý quan trọng: Ở các bước tiếp theo, màn hình sẽ hiển thị đường dẫn cài đặt, mặc định là:  
`C:\Program Files\Tesseract-OCR`  
 _(Hãy giữ nguyên đường dẫn mặc định này để khớp với đoạn code Python)._
  5. Nhấn Install và đợi vài giây → Nhấn Finish để hoàn tất.



## Bước 3: Chạy Code Python

Sau khi cài đặt xong phần mềm, bạn chỉ cần mở trình soạn thảo code (VS Code, PyCharm, IDLE...) và chạy đoạn code Python sau để chuyển PDF ảnh quét tiếng Anh thành văn bản:
    
    
    import io
    from PIL import Image
    import pymupdf
    import pytesseract
    
    # Đường dẫn này khớp hoàn toàn với vị trí cài đặt mặc định ở Bước 2
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    
    # Nhập tên file PDF tiếng Anh dạng ảnh quét của bạn ở đây
    input_pdf = "scanned_eng.pdf"
    output_txt = "ocr_eng_output.txt"
    
    try:
      doc = pymupdf.open(input_pdf)
      full_text = []
    
      print("Bắt đầu quá trình OCR...")
      for i, page in enumerate(doc):
        # Tăng độ nét ảnh để OCR chính xác hơn
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
    
        # Tiến hành nhận diện tiếng Anh
        text = pytesseract.image_to_string(img, lang="eng")
        full_text.append(f"--- PAGE {i+1} ---\n{text}")
        print(f" Đã xử lý xong trang {i+1}/{len(doc)}")
    
      # Ghi nội dung ra file txt
      with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
      print(f"\n Xuất file thành công! Kết quả lưu tại: {output_txt}")
    
    except FileNotFoundError:
      print(
          f"Lỗi: Không tìm thấy file '{input_pdf}'. Bạn hãy kiểm tra lại đường"
          " dẫn file nhé."
      )
    except Exception as e:
      print(f"Có lỗi xảy ra: {e}")
    

Nếu trong lúc cài đặt phần mềm hoặc chạy code gặp bất kỳ thông báo lỗi nào, bạn hãy chụp màn hình hoặc gửi dòng lỗi đó lên đây để tôi hỗ trợ bạn xử lý ngay nhé!