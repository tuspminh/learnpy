Dưới đây là đoạn code Python hoàn chỉnh sử dụng thư viện `edge-tts` để cấu hình giọng đọc truyện. Code này đã được tối ưu tốc độ chậm lại (`--rate=-10%`) giúp giọng đọc thong thả, truyền cảm đúng chất kể chuyện và tự động xuất ra file âm thanh.

## 1\. Cài đặt thư viện

Nếu chưa cài đặt, bạn mở Terminal/Command Prompt và chạy lệnh:
    
    
    pip install edge-tts
    

## 2\. Đoạn code Python mẫu

Bạn có thể copy đoạn code này, thay đổi nội dung truyện trong biến `TEXT` và đổi tên giọng đọc trong biến `VOICE` tùy ý:
    
    
    import asyncio
    import edge_tts
    
    # 1. Đoạn văn bản truyện tiếng Anh muốn đọc
    TEXT = """
    Once upon a time, in a deep, magical forest, there lived a little golden bird. 
    Every evening, she would sing a beautiful melody that brought sweet dreams to everyone.
    """
    
    # 2. Chọn giọng đọc (Ví dụ: en-US-AriaNeural hoặc en-GB-SoniaNeural)
    VOICE = "en-US-AriaNeural"
    
    # 3. Tên file âm thanh xuất ra
    OUTPUT_FILE = "fairy_tale.mp3"
    
    async def generate_fairytale():
        # Cấu hình giảm tốc độ xuống -10% để giọng đọc thong thả, hợp kể chuyện
        communicate = edge_tts.Communicate(TEXT, VOICE, rate="-10%")
        
        print(f"Đang tiến hành chuyển đổi truyện bằng giọng {VOICE}...")
        await communicate.save(OUTPUT_FILE)
        print(f"Thành công! File truyện đã được lưu tại: {OUTPUT_FILE}")
    
    # Chạy chương trình
    if __name__ == "__main__":
        asyncio.run(generate_fairytale())
    

## 3\. Cách nâng cao: Đổi giọng theo nhân vật (Kể chuyện chuyên nghiệp)

Nếu truyện của bạn có cả người dẫn truyện (Narrator) và lời thoại của nhân vật, bạn có thể chia nhỏ văn bản và ghép các giọng khác nhau vào cùng một file như sau:
    
    
    import asyncio
    import edge_tts
    
    # Danh sách các câu thoại phân theo vai
    STORY_PARTS = [
        {"voice": "en-US-GuyNeural", "text": "The old king looked at the boy and asked:"}, # Giọng nam kể chuyện
        {"voice": "en-US-JennyNeural", "text": "What is your name, little traveler?"},     # Giọng nhân vật nhí/nữ
        {"voice": "en-US-GuyNeural", "text": "The boy was silent for a long time."},
    ]
    
    OUTPUT_FILE = "advanced_story.mp3"
    
    async def generate_advanced_story():
        with open(OUTPUT_FILE, "wb") as fp:
            for part in STORY_PARTS:
                # Giảm tốc độ -10% cho tất cả các giọng
                communicate = edge_tts.Communicate(part["text"], part["voice"], rate="-10%")
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        fp.write(chunk["data"])
                        
        print(f"Đã tạo xong file truyện phân vai: {OUTPUT_FILE}")
    
    if __name__ == "__main__":
        asyncio.run(generate_advanced_story())
    

Bạn có muốn tôi hướng dẫn cách tích hợp đoạn code này vào một giao diện đồ họa đơn giản (GUI) để bạn chỉ cần dán truyện vào là bấm nút chạy không?