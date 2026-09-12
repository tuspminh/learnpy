Có thể xử lý được. Để gom các dòng sát nhau thành một đoạn (paragraph) và tách thành đoạn mới khi khoảng cách giữa chúng quá xa, bạn không nên dùng hàm get_text_bounded() mặc định vì hàm này nối tất cả chữ lại theo một luồng thô và dùng dấu ngắt dòng \n cho mọi dòng.
Thay vào đó, bạn cần sử dụng tính năng Phân tích tọa độ dòng văn bản (Text Blocks / Text Lines) của pypdfium2. Thư viện này cho phép lấy ra tọa độ (Bounding Box) của từng dòng chữ trên trang. Dựa vào khoảng cách dọc (y-distance) giữa dòng hiện tại và dòng trước đó, ta sẽ quyết định xem chúng thuộc cùng một đoạn văn hay tách sang đoạn mới.
Dưới đây là hàm extract_text_from_pdf đã được nâng cấp thuật toán gom cụm thông minh:
## Cập nhật mã nguồn Python

import pypdfium2 as pdfium
def extract_text_from_pdf(pdf_path, output_txt_path, spacing_threshold=8):
    """
    Trích xuất văn bản thông minh từ PDF:
    - Gom các dòng sát nhau (khoảng cách dọc <= spacing_threshold) thành 1 paragraph.
    - Tạo đoạn mới (thêm \n\n) khi khoảng cách giữa 2 dòng cách xa nhau.
    
    :param spacing_threshold: Ngưỡng khoảng cách dọc (pixel). 
                              Nếu khoảng cách giữa 2 dòng lớn hơn số này, sẽ tách đoạn.
                              Mặc định là 8 (bạn có thể tăng lên 10-12 nếu phông chữ quá lớn).
    """
    print("▶️ Đang bóc tách văn bản và gom đoạn thông minh từ PDF...")
    doc = pdfium.PdfDocument(pdf_path)
    full_text = ""
    
    try:
        for i, page in enumerate(doc):
            text_page = page.get_textpage()
            page_paragraphs = []
            current_paragraph = []
            last_bottom = None  # Toạ độ đáy của dòng trước đó
            
            try:
                # 1. Lấy tất cả các khối hộp chứa chữ (rectangles) trên trang
                rects = text_page.get_rects()
                
                for rect_idx, rect in enumerate(rects):
                    # Lấy toạ độ hộp: (trái, dưới, phải, trên)
                    left, bottom, right, top = rect
                    
                    # Lấy nội dung chữ nằm trong phạm vi hộp tọa độ này
                    line_text = text_page.get_text_bounded(left, bottom, right, top).strip()
                    
                    # Bỏ qua dòng trống rác nếu có
                    if not line_text:
                        continue
                        
                    # 2. Thuật toán kiểm tra khoảng cách để gom đoạn
                    if last_bottom is not None:
                        # Trong PDF, hệ toạ độ Y có thể tính từ dưới lên.
                        # Khoảng cách dọc giữa dòng hiện tại (top) và dòng trước (last_bottom)
                        distance = abs(last_bottom - top)
                        
                        # Nếu khoảng cách vượt ngưỡng -> Lưu đoạn cũ, khởi tạo đoạn mới
                        if distance > spacing_threshold:
                            if current_paragraph:
                                page_paragraphs.append(" ".join(current_paragraph))
                                current_paragraph = []
                    
                    # Thêm dòng hiện tại vào đoạn đang xây dựng
                    current_paragraph.append(line_text)
                    last_bottom = bottom  # Cập nhật lại đáy cho dòng tiếp theo
                
                # Gom nốt đoạn cuối cùng của trang nếu còn dư
                if current_paragraph:
                    page_paragraphs.append(" ".join(current_paragraph))
                
                # 3. Kết hợp các đoạn của trang bằng 2 dấu xuống dòng (\n\n)
                page_content = "\n\n".join(page_paragraphs)
                full_text += f"--- TRANG {i+1} ---\n{page_content}\n\n"
                
            finally:
                text_page.close()
                page.close()
                
        # Ghi nội dung ra file
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"✅ Đã trích xuất và gom đoạn thành công vào file: {output_txt_path}\n")
        
    finally:
        doc.close()

## 💡 Giải thích nguyên lý hoạt động của thuật toán:

   1. text_page.get_rects(): Thay vì lấy cả mớ chữ, hàm này bóc tách trang PDF thành từng dòng văn bản nhỏ riêng biệt.
   2. abs(last_bottom - top): Nó tính toán khoảng cách khoảng trống (khoảng trắng dọc) giữa chân của dòng phía trên (last_bottom) và đỉnh đầu của dòng phía dưới (top).
   3. " ".join(current_paragraph): Nếu các dòng có khoảng cách khít nhau (nhỏ hơn spacing_threshold), hệ thống hiểu chúng là một câu dài bị ngắt dòng do hết lề trang, nó sẽ gộp lại và ngăn cách bằng dấu cách " ". Nếu khoảng cách xa nhau, nó ngắt đoạn bằng dấu \n\n.

## ⚙️ Cách tinh chỉnh tham số spacing_threshold:

* Nếu bạn thấy chữ vẫn bị xuống dòng quá nhiều (chưa gộp hết đoạn): Hãy tăng spacing_threshold lên 10 hoặc 12.
* Nếu bạn thấy các đoạn văn cách xa nhau vẫn bị gộp dính vào nhau: Hãy giảm spacing_threshold xuống 5 hoặc 6.

Nếu bạn chạy thử và thấy cấu trúc văn bản ổn định, bạn có muốn:

* Tích hợp thuật toán gom đoạn này vào thư viện pdf_processor trong cấu trúc src/ layout đã làm ở bước trước không?
* Hỗ trợ tự động loại bỏ các số trang (Page Numbers) hoặc tiêu đề đầu trang (Headers/Footers) dựa trên tọa độ biên của trang luôn không?


