Tuyệt vời! Bạn muốn kết hợp **Crawl (Web Scraping)** với **MongoDB** - đó là một combo cực kỳ mạnh mẽ mà các công ty công nghệ lớn hay dùng. 

MongoDB rất phù hợp cho việc lưu trữ dữ liệu crawl vì:
1. **Không cần schema cố định**: Mỗi trang web có cấu trúc khác nhau, bạn có thể lưu linh hoạt.
2. **Lưu trữ dữ liệu lồng nhau**: JSON của API hay HTML được parse ra nested object lưu rất tự nhiên.

Hôm nay chúng ta sẽ xây dựng một **"Crawler thông minh"** lấy dữ liệu sách từ trang [Books to Scrape](http://books.toscrape.com/) - đây là trang web "hợp pháp" chuyên dùng để học crawl, không sợ bị kiện hay block IP nhé!

---

### Phần 1: Cài đặt "Bộ công cụ" cho Crawler

```bash
pip install pymongo requests beautifulsoup4
```
- **requests**: Lấy HTML từ web.
- **beautifulsoup4**: Phân tích cú pháp HTML, giúp trích xuất dữ liệu dễ dàng.

---

### Phần 2: Code Crawler hoàn chỉnh (Từ A đến Z)

Tôi sẽ viết thành 2 hàm rõ ràng: 1 hàm **crawl dữ liệu**, 1 hàm **lưu vào MongoDB**.

```python
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time  # Dùng để tạm dừng, tránh bị block IP

# ------------------- 1. KẾT NỐI MONGODB -------------------
client = MongoClient('mongodb://localhost:27017/')
db = client['crawl_data']
collection_sach = db['books']

# Xóa hết dữ liệu cũ để chạy thử cho sạch (comment dòng này nếu không muốn xóa)
collection_sach.delete_many({})
print("✅ Đã xóa dữ liệu cũ trong MongoDB!")

# ------------------- 2. HÀM CRAWL 1 TRANG -------------------
def crawl_mot_trang(url):
    """
    Đầu vào: URL của 1 trang danh sách sách
    Đầu ra: List các dictionary chứa thông tin sách
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Gửi request tải HTML
    response = requests.get(url, headers=headers, timeout=10)
    
    # Kiểm tra xem tải thành công chưa
    if response.status_code != 200:
        print(f"❌ Lỗi tải trang: {url}")
        return []
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tìm tất cả cuốn sách (mỗi cuốn nằm trong thẻ <article class="product_pod">)
    danh_sach_sach = []
    cac_san_pham = soup.find_all('article', class_='product_pod')
    
    for san_pham in cac_san_pham:
        # Lấy tên sách (nằm trong thẻ h3 -> a)
        ten = san_pham.find('h3').find('a')['title']
        
        # Lấy giá (nằm trong thẻ p class="price_color")
        gia = san_pham.find('p', class_='price_color').text
        # Làm sạch giá: loại bỏ ký tự £ và chuyển thành số float
        gia_float = float(gia.replace('£', '').replace('Â', ''))
        
        # Lấy đánh giá (sao) - ví dụ: class="star-rating Three" -> 3 sao
        rating_tag = san_pham.find('p', class_='star-rating')
        # Map chữ sang số
        map_rating = {
            'One': 1, 'Two': 2, 'Three': 3, 
            'Four': 4, 'Five': 5
        }
        rating = map_rating.get(rating_tag['class'][1], 0)
        
        # Lấy link chi tiết của sách
        link_detail = san_pham.find('h3').find('a')['href']
        # Tạo URL đầy đủ
        if not link_detail.startswith('http'):
            base_url = '/'.join(url.split('/')[:-1]) + '/'
            link_detail = base_url + link_detail.replace('catalogue/', '')
        
        # Gom thành 1 dict
        thong_tin_sach = {
            'ten_sach': ten,
            'gia': gia_float,
            'danh_gia': rating,
            'link_chi_tiet': link_detail,
            'trang_web': url,  # Lưu lại nguồn crawl để sau này dễ truy vết
            'da_xem_chi_tiet': False  # Cờ đánh dấu chưa crawl chi tiết
        }
        danh_sach_sach.append(thong_tin_sach)
    
    return danh_sach_sach

# ------------------- 3. HÀM LƯU VÀO MONGODB -------------------
def luu_sach_vao_mongodb(danh_sach_sach):
    if not danh_sach_sach:
        return 0
    
    # Dùng insert_many để lưu 1 lúc nhiều sách, bỏ qua lỗi trùng lặp
    ket_qua = collection_sach.insert_many(danh_sach_sach, ordered=False)
    return len(ket_qua.inserted_ids)

# ------------------- 4. CHẠY CRAWL NHIỀU TRANG -------------------
def crawl_nhieu_trang(so_trang=3):
    """
    Crawl nhiều trang, mỗi trang có 20 cuốn sách
    """
    tong_so_luong = 0
    
    for trang in range(1, so_trang + 1):
        print(f"🔄 Đang crawl trang {trang}...")
        
        # Tạo URL theo cấu trúc của Books to Scrape
        # Trang 1: http://books.toscrape.com/catalogue/page-1.html
        if trang == 1:
            url = "http://books.toscrape.com/catalogue/page-1.html"
        else:
            url = f"http://books.toscrape.com/catalogue/page-{trang}.html"
        
        # Crawl dữ liệu từ trang này
        danh_sach = crawl_mot_trang(url)
        
        # Lưu vào MongoDB
        so_luong = luu_sach_vao_mongodb(danh_sach)
        tong_so_luong += so_luong
        
        print(f"✅ Đã lưu {so_luong} cuốn sách từ trang {trang}")
        
        # Ngủ 1 giây trước khi qua trang kế (lịch sự với server)
        time.sleep(1)
    
    return tong_so_luong

# ------------------- 5. CHẠY CHƯƠNG TRÌNH -------------------
if __name__ == "__main__":
    print("🚀 Bắt đầu crawl dữ liệu sách...")
    tong = crawl_nhieu_trang(so_trang=3)  # Crawl 3 trang đầu (tầm 60 cuốn)
    print(f"🎉 Crawl hoàn tất! Tổng cộng đã lưu {tong} cuốn sách vào MongoDB.")
```

---

### Phần 3: Phân tích dữ liệu vừa crawl (Ứng dụng ngay)

Sau khi crawl xong, bạn mở Python lên và query thử nào:

```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['crawl_data']
books = db['books']

# 1. Xem thử 1 cuốn sách bất kỳ đã được lưu như thế nào
print("📖 Mẫu dữ liệu sách:")
print(books.find_one())

# 2. Sách nào rẻ nhất? (sắp xếp tăng dần theo giá)
sach_re_nhat = books.find_one(sort=[("gia", 1)])
print(f"\n💰 Sách rẻ nhất: {sach_re_nhat['ten_sach']} - Giá: {sach_re_nhat['gia']} £")

# 3. Sách nào đắt nhất? (sắp xếp giảm dần)
sach_dat_nhat = books.find_one(sort=[("gia", -1)])
print(f"💎 Sách đắt nhất: {sach_dat_nhat['ten_sach']} - Giá: {sach_dat_nhat['gia']} £")

# 4. Đếm số lượng sách theo từng mức đánh giá
print("\n⭐ Thống kê theo đánh giá:")
pipeline = [
    {"$group": {"_id": "$danh_gia", "so_luong": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]
for result in books.aggregate(pipeline):
    print(f"  {result['_id']} sao: {result['so_luong']} cuốn")

# 5. Tìm sách có giá dưới 20£ và đánh giá 5 sao (hàng "ngon bổ rẻ")
print("\n🌟 Sách dưới 20£ và đánh giá 5 sao:")
for sach in books.find({"gia": {"$lt": 20}, "danh_gia": 5}):
    print(f"  - {sach['ten_sach']} | £{sach['gia']}")
```

---

### Phần 4: Nâng cấp - Crawl chi tiết từng sách (Bonus)

Nếu bạn muốn lấy thêm mô tả, số trang,... thì hãy crawl thêm từ `link_chi_tiet` mà chúng ta đã lưu:

```python
def crawl_chi_tiet_sach(link):
    """Hàm lấy thêm thông tin từ trang chi tiết của sách"""
    response = requests.get(link)
    if response.status_code != 200:
        return {}
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Lấy mô tả (nằm trong thẻ div id="product_description" kế đến p)
    mo_ta_tag = soup.find('div', id='product_description')
    mo_ta = mo_ta_tag.find_next('p').text if mo_ta_tag else "Không có mô tả"
    
    # Lấy số trang (nằm trong thẻ table)
    so_trang = "Không có"
    table = soup.find('table', class_='table-striped')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            if 'Number of pages' in row.text:
                so_trang = row.find('td').text
                break
    
    return {
        'mo_ta': mo_ta,
        'so_trang': so_trang
    }

# Lấy 1 sách bất kỳ chưa crawl chi tiết
sach_can_crawl = books.find_one({"da_xem_chi_tiet": False})
if sach_can_crawl:
    chi_tiet = crawl_chi_tiet_sach(sach_can_crawl['link_chi_tiet'])
    # Cập nhật thêm thông tin vào MongoDB
    books.update_one(
        {"_id": sach_can_crawl['_id']},
        {"$set": {"mo_ta": chi_tiet.get('mo_ta'), "so_trang": chi_tiet.get('so_trang'), "da_xem_chi_tiet": True}}
    )
    print("✅ Đã crawl chi tiết cho 1 cuốn sách!")
```

---

### Phần 5: Bài tập thực hành cho bạn

1. **Thay đổi địa chỉ crawl**: Hãy thử crawl trang báo điện tử (VnExpress, BBC,...) lấy tiêu đề bài báo.
2. **Thêm trường `thoi_gian_crawl`**: Khi lưu vào MongoDB, hãy thêm timestamp hiện tại (dùng `datetime.now()`).
3. **Lưu lịch sử**: Thiết kế để khi crawl lại lần sau, nếu sách đã có trong DB thì update giá mới, chứ không insert trùng (gợi ý: dùng `update_one` với `upsert=True`).

---

### Lời khuyên xương máu khi crawl dữ liệu thật

1. **Luôn kiểm tra `robots.txt`**: Ví dụ: `https://facebook.com/robots.txt` để xem họ có cho phép crawl không. Nếu cấm là vi phạm pháp luật!
2. **Set User-Agent như tôi đã làm**: Nhiều trang chặn các trình duyệt không có danh tính.
3. **Dùng Proxy và xoay IP** khi crawl số lượng lớn (sau này tôi sẽ dạy bạn).
4. **Luôn dùng `time.sleep()`**: Crawl quá nhanh sẽ bị chặn IP ngay lập tức.

---

**Câu hỏi dành cho bạn**: Bạn muốn crawl trang web nào nhất? (Ví dụ: Giá điện thoại trên Tiki, tin tức, hay dữ liệu chứng khoán?). Nói cho tôi biết, tôi sẽ hướng dẫn bạn xử lý các tình huống "khó nhằn" đặc thù của trang đó! 😎