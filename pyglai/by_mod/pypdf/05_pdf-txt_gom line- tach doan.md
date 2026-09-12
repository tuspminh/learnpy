Để giải quyết bài toán gom các dòng (lines) dựa trên khoảng cách dọc, chúng ta không thể dùng hàm `extract_text()` mặc định vì nó chỉ trả về chuỗi text thô đã được nối sẵn.

Thay vào đó, ta cần sử dụng hàm ẩn `page._extract_text_objects()` của `pypdf`. Hàm này trả về chi tiết tọa độ `(x, y)` của từng từ/cụm từ, giúp ta tính toán chính xác khoảng cách dòng để gom đoạn (paragraph).

Dưới đây là hàm `extract_text_pdf` đã được nâng cấp. Thuật toán sẽ tính khoảng cách `y` giữa dòng dưới và dòng trên. Nếu khoảng cách này vượt quá một ngưỡng (threshold) chỉ định, nó sẽ tự động ngắt đoạn (`\n\n`).

## Code nâng cấp xử lý gom đoạn theo khoảng cách:
    
    
    from pypdf import PdfReader
    
    def extract_text_with_smart_paragraphs(page, threshold=5.0):
        """
        Trích xuất text của 1 trang và tự động gom nhóm các dòng gần nhau thành đoạn.
        :param page: Đối tượng page của pypdf
        :param threshold: Ngưỡng khoảng cách dọc tối đa để coi là cùng 1 đoạn (đơn vị: points)
        """
        # Lấy danh sách các đối tượng văn bản có kèm tọa độ từ pypdf
        # Mỗi đối tượng có cấu trúc dạng text, hoặc chứa thông tin vị trí (y, x...) tùy phiên bản
        # Để an toàn và chính xác, pypdf cung cấp visitor_text để can thiệp vào quá trình trích xuất
        
        lines_with_y = []
        
        # Định nghĩa hàm visitor để lấy text và tọa độ Y của từng khối text nhỏ
        def visitor_body(text, cm, tm, font_dict, font_size):
            # tm[5] chính là tọa độ Y (vị trí thẳng đứng) của đoạn văn bản trên trang
            text_stripped = text.strip()
            if text_stripped:
                y_coord = tm[5]
                lines_with_y.append((y_coord, text))
    
        # Chạy trích xuất với visitor
        page.extract_text(visitor_text=visitor_body)
        
        if not lines_with_y:
            return ""
        
        # PDF thường sắp xếp tọa độ Y từ dưới lên trên, hoặc có thứ tự xáo trộn.
        # Gom các cụm text có cùng tọa độ Y trước (cùng một dòng)
        unique_lines = {}
        for y, text in lines_with_y:
            # Làm tròn Y một chút để tránh lệch vài pixel do định dạng
            y_round = round(y, 1) 
            if y_round not in unique_lines:
                unique_lines[y_round] = []
            unique_lines[y_round].append(text)
        
        # Sắp xếp các dòng từ TRÊN xuống DƯỚI (Y giảm dần)
        sorted_y = sorted(unique_lines.keys(), reverse=True)
        
        paragraphs = []
        current_paragraph = []
        prev_y = None
        
        for y in sorted_y:
            # Gộp các text trên cùng một dòng thành chuỗi hoàn chỉnh
            line_text = "".join(unique_lines[y]).strip()
            if not line_text:
                continue
                
            if prev_y is not None:
                # Tính khoảng cách dọc giữa dòng trước và dòng hiện tại
                # Vì Y giảm dần từ trên xuống, nên khoảng cách = prev_y - y
                distance = prev_y - y
                
                # Nếu khoảng cách vượt ngưỡng threshold, coi như sang đoạn mới
                if distance > threshold:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = [line_text]
                else:
                    # Nếu gần nhau, gộp vào đoạn hiện tại bằng dấu cách
                    current_paragraph.append(line_text)
            else:
                current_paragraph.append(line_text)
                
            prev_y = y
            
        # Thêm đoạn cuối cùng vào danh sách
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
            
        # Nối các đoạn với nhau bằng 2 dấu xuống dòng (\n\n) để phân tách rõ ràng
        return "\n\n".join(paragraphs)
    
    
    # --- 3. EXTRACT TEXT: Hàm chính tích hợp vào mã nguồn của bạn ---
    def extract_text_pdf(input_pdf, page_num=None, paragraph_threshold=14.0):
        """
        page_num: Nếu là số (1, 2...), chỉ lấy text trang đó. Nếu là None, lấy toàn bộ PDF.
        paragraph_threshold: Khoảng cách dòng lớn hơn số này sẽ bị tách thành đoạn mới (\n\n).
                             Thông thường từ 12.0 đến 18.0 là hợp lý cho tài liệu tiêu chuẩn.
        """
        reader = PdfReader(input_pdf)
        
        if page_num is not None:
            idx = page_num - 1
            if 0 <= idx < len(reader.pages):
                page_text = extract_with_smart_paragraphs(reader.pages[idx], paragraph_threshold)
                return f"--- Trang {page_num} ---\n{page_text}"
            return "Trang không tồn tại."
        
        full_text = []
        for i, page in enumerate(reader.pages):
            page_text = extract_text_with_smart_paragraphs(page, paragraph_threshold)
            full_text.append(f"--- Trang {i+1} ---\n{page_text}")
        return "\n\n".join(full_text)
    

## Cơ chế hoạt động của Code:

  1. `visitor_text`: Hàm này chặn đầu vào dòng dữ liệu của `pypdf`, lấy ra tọa độ `Y` (vị trí chiều dọc) chính xác của từng dòng chữ khi nó được vẽ lên màn hình.
  2. Sắp xếp theo trục Y: Sắp xếp các dòng văn bản theo thứ tự từ đỉnh trang xuống đáy trang.
  3. So sánh khoảng cách: Biến `distance = prev_y - y` đo lường khoảng trống giữa 2 dòng liên tiếp.

     * Nếu các dòng là văn bản liên tục trong một đoạn (Paragraph), khoảng cách này rất nhỏ (thường chỉ khoảng `10` \- `12` points).
     * Nếu sang tiêu đề mới hoặc đoạn văn mới, khoảng cách này sẽ nhảy lên cao (thường từ `16` \- `24` points trở lên).




Để tối ưu độ chính xác cho riêng file của bạn, bạn có thể cho tôi biết:

  * File PDF của bạn thuộc loại nào? (Ví dụ: văn bản luật truyện chữ, hóa đơn/báo cáo có bảng biểu, hay sách giáo khoa nhiều cột?)
  * Nếu kết quả chạy thử bị rời rạc quá hoặc dính nhau quá, hãy báo lại để tôi hướng dẫn bạn cách dò tìm chỉ số `paragraph_threshold` hoàn hảo cho tài liệu đó.