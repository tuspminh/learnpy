Được, bạn hoàn toàn có thể dùng một mình thư viện MediaPipe để xóa nền mà không cần kết hợp với bất kỳ thuật toán cắt lề nào của OpenCV.

Bản thân MediaPipe sẽ tự động quét toàn bộ bức ảnh, phát hiện vị trí vật thể/người, tách nền và trả về cho bạn một bức ảnh mới đã được xóa nền sạch sẽ.

## Cách thực hiện (Dùng một mình MediaPipe)

Để giữ code chạy độc lập và không phụ thuộc vào thư viện bên ngoài, chúng ta sẽ dùng thư viện chuẩn `Pillow` (thư viện xử lý ảnh mặc định đi kèm trong hầu hết môi trường Python) kết hợp với MediaPipe.

## 1\. Cài đặt thư viện
    
    
    pip install mediapipe pillow
    

## 2\. Chuẩn bị File Model AI

MediaPipe yêu cầu một file model siêu nhẹ để chạy offline. Bạn hãy tải file `selfie_segmenter.tflite` (chuyên tách người, chỉ khoảng 5MB) từ Google bằng cách bấm vào link này:  
👉 Tải file selfie_segmenter.tflite

 _(Sau khi tải về, hãy để file này cùng thư mục với file code Python của bạn)._

## 3\. Mã nguồn Python
    
    
    import os
    import numpy as np
    from PIL import Image
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    
    def remove_background_mediapipe(image_path, output_path, segmenter):
        # 1. Mở ảnh bằng Pillow và chuyển sang định dạng RGB
        pil_img = Image.open(image_path).convert("RGB")
        w, h = pil_img.size
        
        # 2. Chuyển ảnh Pillow thành đối tượng MediaPipe Image
        numpy_image = np.array(pil_img)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
    
        # 3. Chạy AI để phân tách nền
        segmentation_result = segmenter.segment(mp_image)
        
        # Lấy mặt nạ (mask) từ kết quả AI trả về
        category_mask = segmentation_result.category_mask.numpy_view()
        
        # Tạo mặt nạ nhị phân: vùng đối tượng = 255 (trắng), vùng nền = 0 (đen)
        # Ngưỡng 0.5 giúp đường biên cắt sắc nét hơn
        mask_data = (category_mask > 0.5).astype(np.uint8) * 255
        
        # Chuyển mặt nạ thành ảnh Pillow (hệ màu L - Grayscale)
        mask_image = Image.fromarray(mask_data, mode="L")
    
        # 4. Tạo ảnh trong suốt (Nền suốt PNG)
        # Gắn mặt nạ vừa tạo làm kênh Alpha (độ trong suốt) cho ảnh gốc
        output_image = pil_img.copy()
        output_image.putalpha(mask_image)
    
        # Nếu bạn muốn đổi thành NỀN TRẮNG (thay vì suốt), hãy dùng 3 dòng dưới này:
        # white_bg = Image.new("RGB", pil_img.size, (255, 255, 255))
        # output_image = Image.composite(pil_img, white_bg, mask_image)
    
        # 5. Lưu kết quả
        output_image.save(output_path, "PNG")
        print(f"Đã xóa nền xong: {output_path}")
    
    
    if __name__ == "__main__":
        # Cấu hình mô hình AI chạy offline
        model_path = "selfie_segmenter.tflite"
        
        if not os.path.exists(model_path):
            print(f"Lỗi: Thiếu file '{model_path}'. Hãy tải về và đặt cạnh file code.")
            exit()
    
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.ImageSegmenterOptions(
            base_options=base_options,
            output_category_mask=True
        )
        
        # Khởi tạo AI Engine 1 lần duy nhất để dùng chung cho các ảnh
        print("Đang khởi động MediaPipe...")
        with vision.ImageSegmenter.create_from_options(options) as segmenter:
            # Đường dẫn ảnh đầu vào và đầu ra của bạn
            remove_background_mediapipe("cua_hang/anh_goc.jpg", "ket_qua_xoa_nen.png", segmenter)
    

## Đánh giá khi dùng một mình MediaPipe

  * Ưu điểm: Code rất sạch, gọn gàng, không cần cài đặt thư viện OpenCV nặng nề. Tốc độ xử lý cực kỳ nhanh (mất chưa tới 0.05 giây/ảnh).
  * Nhược điểm: Ảnh kết quả sẽ giữ nguyên kích thước gốc của bức ảnh ban đầu, không tự động thu nhỏ (crop) sát vào viền của vật thể như khi kết hợp với thuật toán OpenCV.



Nếu bạn muốn nâng cấp đoạn code này, bạn có muốn tôi hướng dẫn:

  * Cách cấu hình để chạy trực tiếp trên Video (hoặc WebCam thời gian thực) không?
  * Cách chuyển sang mô hình `deeplab_v3.tflite` nếu ảnh của bạn là đồ vật/sản phẩm chứ không phải là người?