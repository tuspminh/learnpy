Để xử lý bằng MediaPipe Self-Segmentation (hoặc Object Segmentation), ưu điểm lớn nhất là tốc độ cực kỳ nhanh và tiêu tốn rất ít tài nguyên phần cứng.

Dưới đây là kiến trúc và mã nguồn Python giúp bạn chạy offline quy trình: Đọc ảnh -> Cắt viền vật thể -> Xóa nền bằng MediaPipe -> Thay nền trắng/hoặc giữ suốt theo cơ chế tối ưu hóa xử lý hàng loạt.

## 1\. Cài đặt thư viện cần thiết
    
    
    pip install opencv-python numpy mediapipe pillow
    

* * *

## 2\. Code mẫu: Tách nền bằng MediaPipe (Tối ưu hóa chạy hàng loạt)

Khác với `rembg`, MediaPipe sử dụng một kiến trúc dựa trên `SelfieSegmentation` (chuyên cho người) hoặc mô hình `ImageSegmenter` đa năng hơn. Dưới đây là cách sử dụng `ImageSegmenter` từ bộ công cụ MediaPipe Tasks mới nhất để xử lý được cả người và các đồ vật phổ biến.
    
    
    import os
    import cv2
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    
    def process_mediapipe_pipeline(image_path, output_path, segmenter):
        # 1. ĐỌC ẢNH VÀ CHUYỂN ĐỔI ĐỊNH DẠNG CHO MEDIAPIPE
        cv_img = cv2.imread(image_path)
        if cv_img is None:
            print(f"Không thể đọc ảnh: {image_path}")
            return
            
        h_orig, w_orig, _ = cv_img.shape
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Tạo đối tượng MP Image từ ma trận numpy
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
    
        # 2. CHẠY AI PHÂN ĐOẠN (SEGMENTATION)
        segmentation_result = segmenter.segment(mp_image)
        category_mask = segmentation_result.category_mask.numpy_view()
    
        # 3. TẠO MẶT NẠ NHỊ PHÂN (BINARY MASK)
        # MediaPipe trả về mask: Vùng đối tượng chính có giá trị gần 1, nền có giá trị gần 0
        # Thiết lập ngưỡng (threshold) 0.5 để phân tách rõ ràng
        mask = (category_mask > 0.5).astype(np.uint8) * 255
    
        # 4. CẮT BỎ PHẦN RÌA THỪA DỰA TRÊN MẶT NẠ (OPENCV CORPPING)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Thêm padding 10px để tránh mất chi tiết sát viền
            padding = 10
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(w_orig, x + w + padding)
            y_end = min(h_orig, y + h + padding)
            
            # Cắt cả ảnh và mặt nạ theo vùng vật thể chính
            cv_img = cv_img[y_start:y_end, x_start:x_end]
            mask = mask[y_start:y_end, x_start:x_end]
    
        # 5. XÓA NỀN (TẠO ẢNH TRONG SUỐT PNG HOẶC NỀN TRẮNG)
        # Tách các kênh màu B, G, R
        b, g, r = cv2.split(cv_img)
        # Đưa mặt nạ mask vào làm kênh Alpha (độ trong suốt)
        rgba = [b, g, r, mask]
        final_rgba = cv2.merge(rgba, 4)
    
        # Nếu muốn đổi sang NỀN TRẮNG thay vì trong suốt, bỏ comment 3 dòng dưới:
        # background = np.ones_like(cv_img, dtype=np.uint8) * 255
        # mask_3ch = cv2.merge([mask, mask, mask])
        # final_rgba = np.where(mask_3ch == 255, cv_img, background)
    
        # 6. LƯU KẾT QUẢ
        cv2.imwrite(output_path, final_rgba)
        print(f"Đã xử lý xong: {output_path}")
    
    
    if __name__ == "__main__":
        # ==========================================================
        # CẤU HÌNH VÀ TẢI MÔ HÌNH (Khởi tạo 1 lần duy nhất cho cả Batch)
        # ==========================================================
        # Tải file model chính thức từ Google (Dung lượng siêu nhẹ ~ 3MB đến 5MB)
        # Link tải model nếu chưa có: https://googleapis.com
        model_path = "deeplab_v3.tflite" 
        
        if not os.path.exists(model_path):
            print(f"Lỗi: Hãy tải file '{model_path}' từ Google MediaPipe Models và để cùng thư mục code.")
            exit()
    
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.ImageSegmenterOptions(
            base_options=base_options,
            output_category_mask=True
        )
        
        print("Đang khởi động MediaPipe Engine...")
        with vision.ImageSegmenter.create_from_options(options) as segmenter:
            input_folder = "anh_dau_vao"
            output_folder = "anh_xoa_nen_mediapipe"
            os.makedirs(output_folder, exist_ok=True)
            
            if os.path.exists(input_folder):
                for filename in os.listdir(input_folder):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        in_path = os.path.join(input_folder, filename)
                        out_path = os.path.join(output_folder, f"mp_{os.path.splitext(filename)[0]}.png")
                        
                        process_mediapipe_pipeline(in_path, out_path, segmenter)
            else:
                print(f"Vui lòng tạo thư mục '{input_folder}' và bỏ ảnh vào.")
    

* * *

## 3\. So sánh thực tế hiệu năng khi đổi sang MediaPipe

  * Tốc độ: MediaPipe xử lý mỗi bức ảnh chỉ mất từ 0.02 đến 0.08 giây trên CPU (nhanh gấp 10 - 20 lần so với `rembg`). Cực kỳ lý tưởng nếu hệ thống của bạn cần xử lý hàng ngàn ảnh trong thời gian ngắn hoặc chạy trên các máy tính mini/nhúng (như Raspberry Pi).
  * Độ mịn của viền: Vì model MediaPipe rất nhẹ nên độ chi tiết ở phần biên (như các sợi tóc nhỏ, các góc răng cưa của sản phẩm phức tạp) sẽ không bằng `rembg` (`u2net`). Nó sẽ cho ra một đường cắt dạng phẳng (smooth mask).



Để hoàn thiện ứng dụng, bạn có cần tôi hỗ trợ:

  * Cách viết một hàm tự động tải file `deeplab_v3.tflite` bằng code nếu file đó chưa tồn tại trong máy?
  * Cách tối ưu đa luồng (Multithreading) để MediaPipe xử lý đồng thời nhiều ảnh cùng lúc?