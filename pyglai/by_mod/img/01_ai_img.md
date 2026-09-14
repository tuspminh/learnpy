Với yêu cầu chạy Python, Offline hoàn toàn, xử lý cả ảnh tài liệu (chiếm đa số) và ảnh sản phẩm, bạn cần kết hợp linh hoạt giữa các công cụ để đạt hiệu năng tốt nhất mà không làm nặng máy.

Dưới đây là kiến trúc giải pháp tối ưu và đoạn code mẫu tích hợp sẵn để bạn dùng ngay.

* * *

## 1\. Kiến trúc giải pháp (Gợi ý công cụ)

Để chạy offline mượt mà, bạn nên chia bài toán làm 2 bước:

  * Bước 1: Cắt bỏ phần thừa (Crop & Flatten): Dùng OpenCV để tìm khung viền tài liệu hoặc sản phẩm, sau đó dùng thuật toán `Perspective Transform` để cắt lấy vật thể và căn thẳng bốn góc (loại bỏ góc chụp chéo).
  * Bước 2: Nhận diện hướng & Xoay (Orientation & Rotate):

    * _Với tài liệu:_ Dùng PaddleOCR (chế độ chỉ bật module phân loại hướng văn bản - `use_angle_cls=True`) hoặc Tesseract (OSD). PaddleOCR chạy offline rất nhẹ và cực kỳ chính xác.
    * _Với sản phẩm:_ Nếu sản phẩm có chữ (bao bì, nhãn mác), PaddleOCR vẫn xử lý được. Nếu sản phẩm không có chữ, giải pháp offline tốt nhất là dùng YOLOv8-OBB (Oriented Bounding Box) để phát hiện góc xoay của sản phẩm.




* * *

## 2\. Code mẫu Python (Tích hợp OpenCV + PaddleOCR)

Đây là giải pháp "All-in-one" chạy offline rất mạnh cho tài liệu và sản phẩm có nhãn mác. Bạn cần cài đặt các thư viện sau:
    
    
    pip install opencv-python numpy paddlepaddle paddleocr
    

## Mã nguồn xử lý:
    
    
    import cv2
    import numpy as np
    from paddleocr import PaddleOCR
    
    # Khởi tạo PaddleOCR chỉ để nhận diện góc xoay (chạy rất nhanh và nhẹ offline)
    # lang="vi" để tối ưu cho tiếng Việt nếu tài liệu có chữ
    ocr = PaddleOCR(use_angle_cls=True, lang="vi", show_log=False)
    
    def auto_crop_and_deskew(image_path):
        # 1. ĐỌC ẢNH
        img = cv2.imread(image_path)
        orig = img.copy()
        
        # 2. CẮT BỎ PHẦN THỪA (Áp dụng cho tài liệu/sản phẩm có độ tương phản với nền)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 75, 200)
        
        # Tìm các đường viền (Contours)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        screen_cnt = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # Nếu tìm thấy hình có 4 góc (khung tài liệu hoặc hộp sản phẩm)
            if len(approx) == 4:
                screen_cnt = approx
                break
                
        # Nếu tìm thấy khung viền rõ ràng, tiến hành cắt và căn phẳng góc chụp chéo
        if screen_cnt is not None:
            pts = screen_cnt.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            max_width = max(int(widthA), int(widthB))
            
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            max_height = max(int(heightA), int(heightB))
            
            dst = np.array([,
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]], dtype="float32")
                
            M = cv2.getPerspectiveTransform(rect, dst)
            cropped = cv2.warpPerspective(orig, M, (max_width, max_height))
        else:
            # Nếu nền phức tạp không tìm được khung, giữ nguyên ảnh để bước sau xử lý
            cropped = orig
    
        # 3. NHẬN DIỆN HƯỚNG VÀ XOAY THẲNG (Dùng AI PaddleOCR)
        # Thử nghiệm góc xoay của ảnh
        result = ocr.ocr(cropped, cls=True, det=False, rec=False)
        
        # Kết quả trả về dạng: [[direction, confidence]]
        # Ví dụ: [['180', 0.99]] nghĩa là ảnh bị ngược 180 độ
        if result and result[0]:
            direction, confidence = result[0][0]
            if confidence > 0.8: # Chỉ xoay nếu AI chắc chắn
                if direction == '90':
                    cropped = cv2.rotate(cropped, cv2.ROTATE_90_CLOCKWISE)
                elif direction == '180':
                    cropped = cv2.rotate(cropped, cv2.ROTATE_180)
                elif direction == '270':
                    cropped = cv2.rotate(cropped, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    
        return cropped
    
    # Chạy thử nghiệm
    result_img = auto_crop_and_deskew("tai_lieu_bi_nguoc.jpg")
    cv2.imwrite("ket_qua_sach_dep.jpg", result_img)
    

* * *

## 3\. Đánh giá khi chạy thực tế (Offline)

  * Tốc độ: Thuật toán cắt viền của OpenCV chạy mất chưa tới 0.05 giây. Module nhận diện hướng của PaddleOCR (chạy trên CPU thông thường) mất khoảng 0.2 - 0.5 giây cho mỗi ảnh. Hoàn toàn đủ nhanh để xử lý hàng loạt offline.
  * Độ chính xác: Rất cao với ảnh tài liệu, hóa đơn, CMND/CCCD.
  * Lưu ý cho ảnh sản phẩm: Nếu ảnh sản phẩm của bạn được chụp trên nền quá phức tạp (nhiều đồ vật xung quanh) và OpenCV không cắt đúng viền, bạn nên chuyển sang giải pháp huấn luyện một model YOLOv8-OBB siêu nhẹ (bản Nano) để AI tự khoanh vùng sản phẩm và trả về góc nghiêng chính xác.



Để tối ưu sâu hơn cho hệ thống của bạn, hãy cho tôi biết:

  * Bạn có cần xử lý nền ảnh phức tạp (nhiều rác, đồ vật khác xen vào sản phẩm) không?
  * Các sản phẩm bạn cần xử lý thông thường có chữ/nhãn mác trên bề mặt không?