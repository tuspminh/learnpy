Cách đơn giản nhất để chuyển đổi PDF thành text bằng Python là sử dụng thư viện `pypdf` (thế hệ mới của PyPDF2) với vài dòng code cơ bản.

## Cài đặt thư viện

Chạy lệnh sau trong terminal để cài đặt `pypdf`:
    
    
    pip install pypdf
    

## Code mẫu chuyển PDF sang Text

Tạo file Python và chạy đoạn mã sau để đọc file PDF và ghi nội dung ra file `.txt`:
    
    
    from pypdf import PdfReader
    
    # Mở file PDF
    reader = PdfReader("ten_file.pdf")
    
    # Khởi tạo chuỗi chứa text
    text = ""
    
    # Lặp qua từng trang và lấy văn bản
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Ghi văn bản ra file txt
    with open("ket_qua.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("Đã chuyển đổi thành công!")
    

## Các thư viện thay thế phổ biến khác

  * `pdfminer.six`: Phù hợp khi bạn cần trích xuất văn bản phức tạp, giữ bố cục tốt hơn. Hướng dẫn nhanh tại [Trích xuất văn bản từ PDF - Reddit](https://www.reddit.com/r/Python/comments/16d6ond/extract_text_from_pdf_in_2_lines_of_code_python/?tl=vi).
  * `pdfplumber`: Hỗ trợ rất tốt việc trích xuất dữ liệu dạng bảng (table) từ PDF.
  * `pytesseract`: Dùng cho các file PDF dạng ảnh quét (scanned PDF) cần công nghệ nhận dạng ký tự quang học (OCR). [1] 



Bạn có muốn chia sẻ thêm về loại file PDF của bạn (PDF chữ bình thường, PDF có bảng biểu hay PDF là ảnh quét) để tôi hướng dẫn thư viện phù hợp nhất không?

  


[1] [https://www.reddit.com](https://www.reddit.com/r/Python/comments/16d6ond/extract_text_from_pdf_in_2_lines_of_code_python/?tl=vi)