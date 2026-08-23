Để cào (crawl) truyện từ trang [truyenfull.live](https://truyenfull.live/) hiệu quả bằng Python, phương pháp tối ưu nhất là sử dụng thư viện `requests` kết hợp với `BeautifulSoup`. [1] 

Cấu trúc HTML của hệ thống TruyenFull thường render sẵn nội dung chữ (Static HTML), do đó bạn không cần dùng đến các công cụ nặng nề như Selenium hay Playwright, giúp tốc độ cào rất nhanh và tiết kiệm tài nguyên. [2, 3] 

Dưới đây là hướng dẫn phân tích "hiện trường" và mã nguồn mẫu chi tiết. [4] 

* * *

## 1\. Phân tích cấu trúc HTML của TruyenFull

Khi F12 (Inspect) một chương truyện bất kỳ trên TruyenFull: [5] 

  *   * Tiêu đề chương: Thường nằm trong thẻ `<a>` có class `.chapter-title` hoặc tiêu đề của trang.
  * Nội dung truyện: Toàn bộ chữ nằm trong một thẻ `<div>` có class là `.chapter-c`.
  * Nút Chương tiếp theo: Thường là thẻ `<a>` có id `#next_chap` hoặc class chứa thuộc tính `href` dẫn thẳng tới chương kế tiếp. [4] 
  * 


* * *

## 2\. Mã nguồn Python mẫu (Cào toàn bộ 1 bộ truyện)

Đoạn code dưới đây sẽ tự động cào chương 1, lấy nội dung, sau đó tìm link của chương 2 để tự động nhảy tiếp (Pagination Loop), lặp lại cho đến khi hết truyện và lưu thành một file `.txt`. [5] 
    
    
    import time
    import re
    import requests
    from bs4 import BeautifulSoup
    
    def crawl_truyenfull(start_url, output_file="truyen_output.txt"):
        # Cấu hình Header giả lập trình duyệt để tránh bị chặn (HTTP 403)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        current_url = start_url
        
        with open(output_file, "w", encoding="utf-8") as f:
            while current_url:
                print(f"Đang cào: {current_url}")
                
                try:
                    response = requests.get(current_url, headers=headers, timeout=10)
                    if response.status_code != 200:
                        print(f"Lỗi truy cập trang: {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 1. Lấy tiêu đề chương
                    title_element = soup.find('a', class_='chapter-title')
                    chapter_title = title_element.get_text(strip=True) if title_element else "Chương không rõ tên"
                    
                    # 2. Lấy nội dung chương
                    content_div = soup.find('div', class_='chapter-c')
                    if not content_div:
                        print("Không tìm thấy nội dung truyện (Thẻ .chapter-c thay đổi?)")
                        break
                    
                    # Xử lý xuống dòng cho đẹp (thay thế thẻ <br> thành dấu xuống dòng \n)
                    for br in content_div.find_all("br"):
                        br.replace_with("\n")
                    
                    chapter_content = content_div.get_text()
                    
                    # 3. Ghi vào file text
                    f.write(f"\n\n=== {chapter_title} ===\n\n")
                    f.write(chapter_content.strip())
                    
                    # 4. Tìm link của chương tiếp theo (Next Chapter)
                    # TruyenFull thường đặt id="next_chap" cho nút Tiếp Theo
                    next_button = soup.find('a', id='next_chap')
                    
                    # Kiểm tra xem nút Next có bị disable hoặc không có link không
                    if next_button and 'href' in next_button.attrs and 'javascript:void' not in next_button['href']:
                        current_url = next_button['href']
                        # Giãn cách thời gian cào để tránh làm sập server người khác (Crawl Delay)
                        time.sleep(1.5) 
                    else:
                        print("Đã cào đến chương cuối cùng!")
                        current_url = None # Thoát vòng lặp
                        
                except Exception as e:
                    print(f"Đã xảy ra lỗi hệ thống: {e}")
                    break
    
    if __name__ == "__main__":
        # Thay đường dẫn Chương 1 của bộ truyện bạn muốn cào vào đây
        url_chuong_1 = "https://truyenfull.live"
        
        crawl_truyenfull(url_chuong_1, output_file="truyen_cua_toi.txt")
    

* * *

## 3\. Các lưu ý quan trọng khi cào TruyenFull

  *   * Tần suất cào (Rate Limit): Đừng bỏ đoạn `time.sleep(1.5)` đi. Nếu bạn gửi yêu cầu liên tục quá nhanh (vòng lặp không nghỉ), hệ thống bảo mật Cloudflare hoặc Firewall của website sẽ quét và khóa IP (Ban IP) của bạn ngay lập tức. [6, 7] 
  * Bảo mật Cloudflare: Đôi khi tên miền `.live` hoặc các tên miền mới của hệ thống này bật tường lửa "Cloudflare Waiting Room" để chống ddos/bot. Nếu chạy code trên bị lỗi chặn (HTML trả về yêu cầu xác minh "Verify you are human"), bạn buộc phải chuyển sang dùng thư viện `cloudscraper` để vượt qua:
        
        pip install cloudscraper
        

Sau đó thay `requests.get(...)` trong mã nguồn thành `cloudscraper.create_scraper().get(...)`.
  * Dữ liệu rác: Đôi khi trong nội dung truyện ẩn chứa các câu text rác quảng cáo (ví dụ: _"Truy cập truyenfull.live để đọc chương mới nhất"_). Bạn có thể dùng hàm `re.sub()` của thư viện `re` trong Python để lọc bỏ những cụm từ trùng lặp này trước khi ghi file.
  * 


Bạn muốn tích hợp mã nguồn cào truyện này vào giao diện PySide6 theo mô hình hướng sự kiện (EDA) đã thảo luận phía trên (để có thanh tiến trình Progress Bar, nút Bắt đầu/Tạm dừng không lo treo UI) không? Tôi có thể viết mẫu cấu trúc đó cho bạn!

  


[1] [https://www.firecrawl.dev](https://www.firecrawl.dev/blog/web-scraping-intro-for-beginners)

[2] [https://truyenfull.live](https://truyenfull.live/)

[3] [https://www.firecrawl.dev](https://www.firecrawl.dev/blog/best-web-scraping-tools)

[4] [https://digotech.vn](https://digotech.vn/huong-dan-cao-du-lieu-web-scraping-bat-ky-website-nao-chi-bang-trinh-duyet/)

[5] [https://magicalapi.com](https://magicalapi.com/blog/recruiting-best-practices/how-to-build-a-web-scraper/)

[6] [https://iproyal.com](https://iproyal.com/blog/how-to-build-a-web-crawler/)

[7] [https://realpython.com](https://realpython.com/tutorials/web-scraping/)