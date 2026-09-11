Thư viện `EasyOCR` là một công cụ nhận dạng ký tự quang học (OCR) hiện đại, được xây dựng trên nền tảng Học sâu (Deep Learning) với PyTorch.

So với `pytesseract`, `EasyOCR` có một ưu điểm cực kỳ lớn: Nó là một thư viện thuần Python (Pure Python package) cài qua `pip`. Bạn không cần phải cài đặt thêm phần mềm bên ngoài hệ điều hành (như Tesseract OCR core) hay cấu hình biến môi trường phức tạp. Ngoài ra, nó nhận diện chữ viết tay, chữ bị nghiêng, và chữ Tiếng Việt có dấu tốt hơn Tesseract nhờ mô hình AI.

* * *

## 1\. Cài đặt thư viện

Bạn chỉ cần chạy lệnh sau trong terminal:
    
    
    pip install easyocr pdf2image pillow
    

_Lưu ý: Giống như Tesseract, vì EasyOCR chỉ nhận diện hình ảnh nên chúng ta vẫn cần`pdf2image` để rã các trang PDF thành ảnh trước khi quét._

## 2\. Code mẫu chuyển Scanned PDF thành Text với EasyOCR (Hỗ trợ Tiếng Việt)

Trong lần đầu tiên chạy code, EasyOCR sẽ tự động tải các mô hình AI (model weights) của ngôn ngữ Tiếng Việt (`vi`) và Tiếng Anh (`ch_sim` hoặc `en`) về máy tính, các lần sau sẽ chạy trực tiếp.
    
    
    from pdf2image import convert_from_path
    import easyocr
    import numpy as np
    
    pdf_path = "tai_lieu_scan.pdf"
    output_text_file = "ket_qua_easyocr.txt"
    
    # 1. Khởi tạo Reader với ngôn ngữ Tiếng Việt ('vi') và Tiếng Anh ('en')
    # Nếu máy bạn có card đồ họa NVIDIA, EasyOCR sẽ tự động dùng GPU để chạy cực nhanh
    reader = easyocr.Reader(['vi', 'en'], gpu=True)
    
    # 2. Chuyển PDF thành danh sách các trang ảnh
    pages = convert_from_path(pdf_path, dpi=200)
    full_text = ""
    
    # 3. Lặp qua từng trang để nhận diện chữ
    for i, page_img in enumerate(pages):
        print(f"Đang OCR trang {i+1}...")
        
        # EasyOCR làm việc tốt nhất với định dạng mảng Numpy (Numpy array)
        img_np = np.array(page_img)
        
        # Đọc chữ từ ảnh (Hàm readtext trả về text kèm tọa độ và độ tự tin)
        # detail=0 nghĩa là chỉ lấy chuỗi text thô, bỏ qua tọa độ
        results = reader.readtext(img_np, detail=0)
        
        # Ghép các đoạn chữ tìm được thành một văn bản hoàn chỉnh của trang
        page_text = "\n".join(results)
        
        full_text += f"--- TRANG {i+1} ---\n" + page_text + "\n\n"
    
    # 4. Lưu kết quả
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print("Đã hoàn thành OCR bằng EasyOCR!")
    

## 3\. Trích xuất Text nâng cao kèm Tọa độ (Bounding Box)

Nếu bạn đặt `detail=1` (hoặc mặc định không truyền `detail`), EasyOCR sẽ trả về một danh sách các Tuple chứa: [Tọa độ 4 góc của hộp chữ, Nội dung chữ, Độ chính xác (0.0 -> 1.0)].

Tính năng này rất hữu ích khi bạn muốn phân tích xem chữ đó nằm ở khu vực nào trên trang PDF.
    
    
    # Lấy chi tiết tọa độ
    results = reader.readtext(img_np, detail=1)
    
    for bbox, text, confidence in results:
        # bbox = [[x_top_left, y_top_left], [x_top_right, y_top_right], ...]
        top_left = bbox[0]
        print(f"Vị trí: {top_left} | Chữ: {text} | Độ tự tin: {confidence:.2f}")
    

* * *

## So sánh: `EasyOCR` vs `Tesseract (pytesseract)`

Tiêu chí| `Tesseract`| `EasyOCR`  
---|---|---  
Cài đặt ban đầu| Phức tạp (Cần cài phần mềm `.exe` / `apt` ngoài Python)| Rất dễ (Chỉ cần `pip install`)  
Tốc độ trên CPU| Nhanh hơn| Chậm hơn (Mô hình Deep Learning nặng hơn)  
Hỗ trợ phần cứng| Chủ yếu chạy CPU| Hỗ trợ GPU (CUDA) chạy siêu nhanh  
Chữ viết tay / Chữ nghiêng| Kém, dễ bị nhận diện sai ký tự| Khá tốt nhờ mạng Neural mạng mẽ  
Độ chính xác Tiếng Việt| Khá (Nếu ảnh nét và chuẩn phông chữ)| Rất tốt (Nhận diện dấu và từ ngữ tự nhiên hơn)  
  
## 💡 Lời khuyên lựa chọn:

  * Dùng EasyOCR nếu bạn lười cài đặt các phần mềm phụ thuộc vào hệ thống, hoặc tài liệu có nhiều chữ bị lệch, nghiêng, chữ viết tay, và bạn có sẵn card đồ họa (GPU).
  * Dùng Tesseract nếu bạn cần chạy trên các máy tính cấu hình yếu, không có GPU và tài liệu scan của bạn ở dạng văn bản in đóng tập rất ngay ngắn.



Bạn đã lựa chọn được thư viện nào phù hợp cho dự án của mình chưa? Nếu bạn cần, tôi có thể hướng dẫn cách tối ưu hóa tốc độ quét nhiều trang cùng lúc (multiprocessing) hoặc chuyển sang PaddleOCR — một bộ công cụ OCR của Baidu đang giữ kỷ lục về độ chính xác tiếng Việt hiện nay.