Dưới đây là đoạn code Python hoàn chỉnh kết hợp giữa `edge-tts` và thư viện tạo giao diện `tkinter` (có sẵn trong Python). Giao diện này cho phép bạn dán văn bản truyện, chọn nhanh giọng đọc phù hợp, chỉnh tốc độ và bấm nút để xuất file MP3 trực tiếp.

## 1\. Cài đặt thư viện hỗ trợ

Để `tkinter` hoạt động mượt mà với các tác vụ bất đồng bộ (asyncio) của `edge-tts`, bạn cần cài thêm thư viện `async_tkinter_loop`. Hãy chạy lệnh sau trong Terminal / Command Prompt:
    
    
    pip install edge-tts async_tkinter_loop
    

## 2\. Đoạn code giao diện Python (GUI)

Bạn hãy tạo một file mới tên là `app_doc_truyen.py`, dán đoạn code sau vào và chạy:
    
    
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from async_tkinter_loop import async_handler, async_mainloop
    import edge_tts
    
    # Danh sách giọng đọc hay nhất cho truyện đã lọc sẵn
    VOICES = {
        "Nữ Mỹ (Aria) - Truyền cảm": "en-US-AriaNeural",
        "Nữ Mỹ (Jenny) - Cổ tích nhẹ nhàng": "en-US-JennyNeural",
        "Nam Mỹ (Guy) - Trầm ấm": "en-US-GuyNeural",
        "Nam Mỹ (Steffan) - Cuốn hút": "en-US-SteffanNeural",
        "Nữ Anh (Sonia) - Sang trọng, cổ điển": "en-GB-SoniaNeural",
        "Nam Anh (Ryan) - Tự nhiên như người thật": "en-GB-RyanNeural",
    }
    
    @async_handler
    async def handle_convert():
        text = text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung truyện!")
            return
    
        # Lấy thông tin cấu hình từ giao diện
        selected_label = voice_combo.get()
        voice_code = VOICES[selected_label]
        rate_speed = rate_scale.get()
        
        # Định dạng chuỗi rate cho edge-tts (ví dụ: -10% hoặc +5%)
        rate_str = f"{int(rate_speed):+d}%" if rate_speed != 0 else "+0%"
    
        # Chọn vị trí lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("Audio files", "*.mp3")],
            title="Chọn nơi lưu file truyện"
        )
        if not file_path:
            return
    
        # Trạng thái xử lý
        status_label.config(text="Đang xử lý tạo file MP3... Vui lòng đợi.", fg="blue")
        btn_convert.config(state=tk.DISABLED)
    
        try:
            communicate = edge_tts.Communicate(text, voice_code, rate=rate_str)
            await communicate.save(file_path)
            messagebox.showinfo("Thành công", f"Đã lưu file truyện tại:\n{file_path}")
        except Exception as e:
            messagebox.onerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
        finally:
            status_label.config(text="Sẵn sàng", fg="green")
            btn_convert.config(state=tk.NORMAL)
    
    # --- Khởi tạo Giao diện Windows ---
    root = tk.Tk()
    root.title("Edge-TTS Story Reader")
    root.geometry("600x550")
    root.resizable(False, False)
    
    # 1. Khung nhập văn bản
    lbl1 = tk.Label(root, text="Nhập hoặc dán truyện tiếng Anh vào đây:", font=("Arial", 11, "bold"))
    lbl1.pack(pady=(10, 5), anchor="w", px=15)
    
    text_area = tk.Text(root, wrap=tk.WORD, font=("Arial", 10), height=12)
    text_area.pack(fill=tk.BOTH, padx=15, pady=5)
    text_area.insert(tk.END, "Once upon a time, in a magical land far away...")
    
    # Khung chứa cấu hình dưới dạng lưới (Grid)
    config_frame = tk.Frame(root)
    config_frame.pack(fill=tk.X, padx=15, pady=10)
    
    # 2. Chọn giọng đọc
    tk.Label(config_frame, text="Chọn giọng đọc:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
    voice_combo = ttk.Combobox(config_frame, values=list(VOICES.keys()), width=40, state="readonly")
    voice_combo.grid(row=0, column=1, padx=10, pady=5)
    voice_combo.current(0)  # Mặc định chọn Aria
    
    # 3. Tùy chỉnh tốc độ
    tk.Label(config_frame, text="Tốc độ (Khuyên dùng -10%):", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
    rate_scale = tk.Scale(config_frame, from_=-50, to=50, orient=tk.HORIZONTAL, length=260)
    rate_scale.set(-10)  # Mặc định giảm 10% tốc độ để giọng thong thả
    rate_scale.grid(row=1, column=1, padx=10, pady=5)
    
    # 4. Trạng thái hoạt động
    status_label = tk.Label(root, text="Sẵn sàng", fg="green", font=("Arial", 10, "italic"))
    status_label.pack(pady=5)
    
    # 5. Nút bấm xuất file
    btn_convert = tk.Button(root, text="XUẤT FILE AUDIO (MP3)", bg="#28a745", fg="white", font=("Arial", 12, "bold"), height=2, command=handle_convert)
    btn_convert.pack(fill=tk.X, padx=15, pady=10)
    
    # Chạy giao diện hỗ trợ Asyncio mượt mà
    async_mainloop(root)
    

## Các tính năng có trong giao diện này:

  * Giao diện trực quan: Gồm ô nhập văn bản lớn, thanh kéo chỉnh tốc độ độc lập và menu thả xuống để chọn nhanh 6 giọng kể chuyện tốt nhất.
  * Không bị đơ màn hình: Sử dụng vòng lặp bất đồng bộ giúp phần mềm luôn phản hồi mượt mà, không bị hiện tượng "Not Responding" khi đang render file âm thanh dài.
  * Tự do lưu file: Chương trình sẽ hiển thị cửa sổ để bạn tự đặt tên file và chọn thư mục lưu (Desktop, Download...) theo ý muốn.



Bạn có gặp khó khăn gì trong việc chạy file Python này hoặc có cần tôi hướng dẫn cách đóng gói nó thành một file `.exe` để click đúp chạy luôn không?