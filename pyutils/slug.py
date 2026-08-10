import re
import unicodedata


def create_slug(text):
    # 1. Chuyển sang chữ thường
    text = text.lower()
    # 2. Xử lý riêng chữ đ
    text = text.replace("đ", "d")
    # 3. Tách các dấu tiếng Việt ra khỏi chữ cái gốc
    text = unicodedata.normalize("NFKD", text)
    # 4. Chỉ giữ lại chữ cái latin gốc, xóa các dấu đi kèm
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # 5. Xóa ký tự đặc biệt (chỉ giữ chữ, số, khoảng trắng, gạch ngang)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    # 6. Thay thế khoảng trắng thành dấu gạch ngang và loại bỏ gạch ngang thừa ở đầu/cuối
    text = re.sub(r"[\s-]+", "-", text).strip("-")

    return text


# Chạy thử nghiệm
# title = " Phúc Tinh Nhà Nông: Ba Vị Ca Ca Cưng Chiều Không Ngớt"
# slug = create_slug(title)
# print(slug)
# Kết quả: phuc-tinh-nha-nong-ba-vi-ca-ca-cung-chieu-khong-ngot
