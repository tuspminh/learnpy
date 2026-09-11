Thư viện `pdfminer.six` (phiên bản duy trì tích cực của `pdfminer` gốc dành cho Python 3) là công cụ trích xuất văn bản mạnh mẽ nhất khi bạn cần giữ nguyên cấu trúc bố cục (layout) hoặc phân tích sâu cấu trúc bên trong file PDF.

Khác với `pypdf` trích xuất text thô theo luồng đọc, `pdfminer.six` phân tích chính xác tọa độ XY của từng ký tự trên trang để nhóm chúng thành các từ, dòng và khối văn bản (text blocks).

* * *

## 1\. Cách đơn giản nhất để lấy Text (Giữ bố cục)

Nếu bạn chỉ muốn trích xuất văn bản một cách nhanh chóng nhưng có độ chính xác cao về ngắt dòng và khoảng cách, hãy dùng hàm `extract_text`:
    
    
    from pdfminer.high_level import extract_text
    
    # Trích xuất toàn bộ văn bản
    text = extract_text("tai_lieu.pdf")
    
    # Hoặc chỉ trích xuất một số trang cụ thể (Ví dụ: Trang 1 và Trang 3)
    text_page_1_3 = extract_text("tai_lieu.pdf", page_numbers=[0, 2])
    
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text)
    

## 2\. Phân tích cấu trúc chi tiết (Layout Analysis)

Điểm ăn tiền của `pdfminer.six` là khả năng bóc tách file PDF thành các đối tượng đồ họa:

  * `LTTextBoxHorizonal`: Khối văn bản nằm ngang.
  * `LTTextLine`: Dòng văn bản.
  * `LTFigure`: Hình ảnh hoặc sơ đồ.
  * `LTImage`: Ảnh dạng bitmap.



Dưới đây là đoạn code giúp bạn đọc văn bản theo từng khối (Paragraph/Block) kèm theo tọa độ của khối đó trên trang:
    
    
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextBoxHorizontal
    
    # Lặp qua từng trang của PDF
    for page_layout in extract_pages("tai_lieu.pdf"):
        print(f"--- Trang số {page_layout.pageid} ---")
        
        # Lặp qua từng phần tử xuất hiện trên trang
        for element in page_layout:
            # Nếu phần tử đó là một khối văn bản
            if isinstance(element, LTTextBoxHorizontal):
                # Lấy tọa độ (X_trái, Y_dưới, X_phải, Y_trên)
                x0, y0, x1, y1 = element.bbox
                text_content = element.get_text().strip()
                
                print(f"Vị trí: [{x0:.1f}, {y0:.1f}] -> Nội dung: {text_content}")
    

## 3\. Trích xuất Text sang định dạng HTML / XML

Nếu bạn muốn chuyển PDF thành một file HTML để hiển thị trên web mà vẫn giữ nguyên vị trí font chữ, cỡ chữ, `pdfminer.six` có công cụ hỗ trợ sẵn:
    
    
    import io
    from pdfminer.converter import HTMLConverter
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from pdfminer.pdfpage import PDFPage
    from pdfminer.layout import LAParams
    
    rsrcmgr = PDFResourceManager()
    retstr = io.BytesIO()
    laparams = LAParams() # Cấu hình phân tích bố cục
    
    # Thay HTMLConverter bằng XMLConverter nếu muốn xuất file XML
    device = HTMLConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open('tai_lieu.pdf', 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    
    html_text = retstr.getvalue().decode()
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_text)
    
    fp.close()
    device.close()
    retstr.close()
    

* * *

## Đang so sánh: Nên chọn `pypdf` hay `pdfminer.six`?

Tiêu chí| `pypdf`| `pdfminer.six`  
---|---|---  
Tốc độ xử lý| Rất nhanh| Chậm hơn (do tính toán tọa độ)  
Độ chính xác bố cục| Trung bình (dễ bị dính chữ, lệch dòng)| Rất cao (giữ nguyên đoạn, cột)  
Tài liệu nhiều cột (Báo bài)| Đọc lẫn lộn từ trái sang phải| Đọc chính xác theo từng cột  
Tính năng khác| Gộp, cắt, xoay, mã hóa file PDF| Chỉ tập trung trích xuất dữ liệu  
  
Bạn có muốn tôi hỗ trợ cấu hình sâu thông số `LAParams` để xử lý các tài liệu phức tạp (như căn chỉnh khoảng cách dòng, khoảng cách từ) hoặc hướng dẫn cách trích xuất hình ảnh từ file PDF bằng `pdfminer.six` không?