Cách nhanh nhất để chuyển file PDF thành text bằng Python là sử dụng thư viện `pypdf`. [1] 

## Các bước thực hiện

  1. Cài đặt thư viện:  
Mở terminal hoặc cmd và chạy lệnh:
         
         pip install pypdf
         

  2. Mã nguồn Python:  
Dùng đoạn code sau để đọc file PDF và lưu nội dung thành file `.txt`:
         
         from pypdf import PdfReader
         
         # Mở file PDF
         reader = PdfReader("example.pdf")
         
         # Khởi tạo chuỗi chứa text
         text = ""
         
         # Duyệt qua từng trang và lấy text
         for page in reader.pages:
           text += page.extract_text() + "\n"
         
         # Lưu ra file text mới
         with open("output.txt", "w", encoding="utf-8") as f:
           f.write(text)
         
         print("Đã chuyển đổi xong!")
         



    
    
    <FollowUp>
    Nếu file PDF của bạn là **ảnh quét (scanned PDF)**, đoạn code trên sẽ không đọc được chữ. Bạn có muốn tôi hướng dẫn dùng thêm thư viện nhận diện ký tự quang học (**OCR** như `pytesseract`) không?
    </FollowUp>
    

  


[1] [https://www.reddit.com](https://www.reddit.com/r/Python/comments/16d6ond/extract_text_from_pdf_in_2_lines_of_code_python/?tl=vi)