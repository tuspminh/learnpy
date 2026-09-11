Thư viện `PaddleOCR` (phát triển bởi Baidu) hiện đang là một trong những công cụ OCR mạnh mẽ và đạt độ chính xác cao nhất thế giới hiện nay cho tiếng Việt, vượt trội hơn cả Tesseract và EasyOCR trong hầu hết các bài kiểm tra thực tế.

`PaddleOCR` sử dụng các mô hình học sâu siêu nhẹ (PP-OCR), giúp nó chạy cực nhanh ngay cả trên CPU thông thường mà không bắt buộc phải có card đồ họa (GPU) như EasyOCR. Thư viện này nhận diện cực tốt chữ in, chữ viết tay, hóa đơn, bảng biểu, biển số xe hay văn bản bị mờ, cong vênh.

* * *

## 1\. Cài đặt thư viện

Bạn chỉ cần cài đặt `paddleocr`, thư viện xử lý ảnh `paddlepaddle` (hoặc `paddlepaddle-gpu` nếu máy có card NVIDIA), cùng với `pdf2image` để rã file PDF:
    
    
    pip install paddleocr paddlepaddle pdf2image pillow openpyxl
    

* * *

## 2\. Code mẫu chuyển Scanned PDF thành Text với PaddleOCR

PaddleOCR tự động tải mô hình tiếng Việt (`vi`) trong lần chạy đầu tiên. Dưới đây là đoạn code tối ưu để quét toàn bộ file PDF và trích xuất chữ:
    
    
    from pdf2image import convert_from_path
    from paddleocr import PaddleOCR
    import numpy as np
    
    pdf_path = "tai_lieu_scan.pdf"
    output_text_file = "ket_qua_paddleocr.txt"
    
    # 1. Khởi tạo PaddleOCR với ngôn ngữ Tiếng Việt ('vi')
    # Thay use_gpu=False thành True nếu máy bạn có card đồ họa NVIDIA
    ocr = PaddleOCR(use_angle_cls=True, lang='vi', use_gpu=False)
    
    # 2. Chuyển PDF thành danh sách ảnh các trang (DPI 200 là tối ưu cho OCR)
    pages = convert_from_path(pdf_path, dpi=200)
    full_text = ""
    
    # 3. Quét từng trang một
    for i, page_img in enumerate(pages):
        print(f"Đang OCR trang {i+1}...")
        
        # Chuyển ảnh PIL thành mảng Numpy để PaddleOCR xử lý
        img_np = np.array(page_img)
        
        # Chạy mô hình nhận diện
        result = ocr.ocr(img_np, cls=True)
        
        # Lưu trữ chữ của trang hiện tại
        page_lines = []
        
        # Duyệt qua các dòng chữ tìm được
        # Lưu ý: result là một danh sách, phần tử đầu tiên chứa kết quả của ảnh
        if result and result[0]:
            for line in result[0]:
                # line[1][0] là chuỗi văn bản nhận diện được
                text_line = line[1][0]
                page_lines.append(text_line)
                
        # Ghép các dòng chữ lại với nhau
        page_text = "\n".join(page_lines)
        full_text += f"--- TRANG {i+1} ---\n" + page_text + "\n\n"
    
    # 4. Lưu kết quả ra file text
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print("Đã hoàn thành OCR bằng PaddleOCR!")
    

* * *

## 3\. Trích xuất Text kèm Tọa độ (Phân tích Layout phức tạp)

Nếu bạn không truyền `line[1][0]` như ở trên, cấu trúc kết quả trả về của `ocr.ocr()` rất chi tiết, bao gồm: `[Tọa độ 4 góc hộp chữ, (Nội dung chữ, Độ chính xác)]`.
    
    
    for line in result[0]:
        bbox = line[0]  # Tọa độ 4 góc: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        text = line[1][0]  # Nội dung chữ
        confidence = line[1][1]  # Độ tin cậy từ 0.0 đến 1.0
        print(f"Chữ: {text} | Độ chính xác: {confidence:.2f} | Tọa độ góc trên trái: {bbox[0]}")
    

* * *

## Bảng tổng kết: Chọn thư viện OCR nào cho Scanned PDF?

Tiêu chí| `Tesseract`| `EasyOCR`| `PaddleOCR`  
---|---|---|---  
Độ chính xác Tiếng Việt| Khá (Dễ lỗi dấu)| Tốt| Xuất sắc nhất  
Tốc độ trên CPU| Nhanh| Rất chậm| Rất nhanh (Mô hình PP-OCR cực nhẹ)  
Cài đặt| Phức tạp (Cần cài thêm file `.exe`/`apt`)| Dễ (`pip install`)| Dễ (`pip install`)  
Xử lý ảnh mờ/nghiêng| Kém| Tốt| Rất tốt (Có module chỉnh góc nghiêng tự động)  
Tính năng mở rộng| Chỉ nhận diện chữ| Chỉ nhận diện chữ| Có sẵn module nhận diện Bảng biểu (StructureV2)  
  
## 💡 Tính năng nâng cao độc quyền của PaddleOCR:

Nếu bảng biểu nằm trong file PDF dạng ảnh quét, bạn có thể gọi module `PP-Structure` của PaddleOCR. Nó sẽ tự động dựng lại cấu trúc bảng và xuất thẳng ra file Excel (`.xlsx`) cho bạn mà không làm xáo trộn dữ liệu.

Chúng ta đã đi qua toàn bộ các giải pháp từ PDF chữ thông thường (`pypdf`, `pdfminer.six`, `pdfplumber`) đến PDF ảnh quét (`Tesseract`, `EasyOCR`, `PaddleOCR`).

Bạn đã chọn được công cụ phù hợp nhất với file PDF của mình chưa, hay bạn cần tôi hỗ trợ viết tiếp đoạn code xử lý một tính năng cụ thể nào khác?