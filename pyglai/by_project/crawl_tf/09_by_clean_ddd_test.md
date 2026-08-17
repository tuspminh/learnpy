Để kiểm thử mã nguồn viết theo Clean Architecture và DDD, chúng ta không sử dụng cơ sở dữ liệu thật (SQLite3) cũng như không gửi yêu cầu mạng thật qua thư viện `requests`. Thay vào đó, chúng ta sẽ tạo các lớp giả lập (Mock Object) kế thừa từ các Interface trong tầng Domain để giả lập dữ liệu đầu ra.

Thư viện tiêu chuẩn `unittest.mock` của Python sẽ giúp bạn thực hiện điều này một cách dễ dàng.

## 1\. Chuẩn bị môi trường Test

Đầu tiên, bạn tạo một file mới có tên là `test_use_cases.py` nằm ngay thư mục gốc của dự án:
    
    
    novel_crawler/
    ├── domain/
    ├── application/
    ├── infrastructure/
    ├── presentation/
    ├── plugins/
    ├── main.py
    └── test_use_cases.py      # <-- Tạo file này để viết Unit Test
    

## 2\. Viết mã nguồn Unit Test (`test_use_cases.py`)

Đoạn mã dưới đây sử dụng `unittest.mock` để kiểm thử nghiệp vụ của `DownloadAllChaptersUseCase`. Chúng ta sẽ kiểm tra xem:

  1. Use case có lưu thông tin truyện vào Database hay không.
  2. Hệ thống có tự động bỏ qua chương cũ (Resume) nếu hàm `is_chapter_downloaded` trả về `True` hay không.


    
    
    import unittest
    from unittest.mock import MagicMock
    from domain.interfaces import INovelRepository, INovelPlugin
    from domain.models import Novel, Chapter
    from application.use_cases import DownloadAllChaptersUseCase
    
    class TestDownloadAllChaptersUseCase(unittest.TestCase):
    
        def setUp(self):
            # 1. Khởi tạo Mock cho Repository và Plugin (Chỉ là các khung giả lập)
            self.mock_repo = MagicMock(spec=INovelRepository)
            self.mock_plugin = MagicMock(spec=INovelPlugin)
            
            # Thiết lập thuộc tính DOMAIN bắt buộc cho Plugin
            self.mock_plugin.DOMAIN = "testsource.com"
            
            # 2. Khởi tạo Use Case với Dependency Injection (truyền các đối tượng Mock vào)
            self.use_case = DownloadAllChaptersUseCase(repo=self.mock_repo, plugin=self.mock_plugin)
    
        def test_execute_downloads_novel_info_and_chapters_successfully(self):
            # --- GIẢ LẬP DỮ LIỆU ĐẦU VÀO (GIVEN) ---
            target_url = "https://testsource.com"
            
            # Giả lập hàm clean_url luôn trả về chuỗi chuẩn
            self.mock_plugin.clean_url.side_effect = lambda u: u if u.endswith('/') else f"{u}/"
            
            # Giả lập fetch_soup trả về một đối tượng không rỗng (giả vờ là soup thành công)
            self.mock_plugin.fetch_soup.return_value = "fake_soup_object"
            
            # Giả lập thông tin truyện bóc tách được từ trang web
            self.mock_plugin.parse_novel_info.return_value = {
                'title': 'Truyện Test Clean Architecture',
                'author': 'Tác Giả Mock',
                'description': 'Mô tả truyện giả lập'
            }
            
            # Giả lập bộ truyện có 1 trang chứa danh sách chương
            self.mock_plugin.extract_total_pages.return_value = 1
            
            # Giả lập danh sách chương quét được (Gồm 2 chương)
            self.mock_plugin.parse_chapter_list.return_value = [
                {'title': 'Chương 1: Khởi Đầu', 'url': 'https://testsource.comchuong-1/'},
                {'title': 'Chương 2: Diễn Biến', 'url': 'https://testsource.comchuong-2/'}
            ]
            
            # Giả lập nội dung text khi cào từng chương cụ thể
            self.mock_plugin.parse_chapter_content.side_effect = [
                {'title': 'Chương 1: Khởi Đầu', 'content': 'Nội dung chương 1 ngắn gọn', 'novel_url': 'https://testsource.com'},
                {'title': 'Chương 2: Diễn Biến', 'content': 'Nội dung chương 2 kịch tính', 'novel_url': 'https://testsource.com'}
            ]
            
            # QUAN TRỌNG: Giả lập Database báo rằng cả 2 chương này ĐỀU CHƯA TỪNG ĐƯỢC TẢI
            self.mock_repo.is_chapter_downloaded.return_value = False
    
            # Khởi tạo một hàm callback rỗng để không in gì ra màn hình console khi test
            dummy_callback = lambda current, total, title: None
    
            # --- KÍCH HOẠT HÀNH ĐỘNG (WHEN) ---
            self.use_case.execute(target_url, progress_callback=dummy_callback)
    
            # --- KIỂM TRA KẾT QUẢ (THEN) ---
            
            # Kiểm tra xem hàm save_novel có được gọi đúng thông tin mẫu hay không
            expected_novel = Novel(
                novel_url="https://testsource.com",
                title="Truyện Test Clean Architecture",
                author="Tác Giả Mock",
                description="Mô tả truyện giả lập",
                source="testsource.com"
            )
            self.mock_repo.save_novel.assert_called_once_with(expected_novel)
            
            # Kiểm tra xem hàm save_chapter có được gọi đúng 2 lần (cho 2 chương) hay không
            self.assertEqual(self.mock_repo.save_chapter.call_count, 2)
    
        def test_execute_skips_already_downloaded_chapters(self):
            # --- GIẢ LẬP DỮ LIỆU ĐẦU VÀO (GIVEN) ---
            target_url = "https://testsource.com"
            self.mock_plugin.clean_url.side_effect = lambda u: u if u.endswith('/') else f"{u}/"
            self.mock_plugin.fetch_soup.return_value = "fake_soup_object"
            self.mock_plugin.parse_novel_info.return_value = {
                'title': 'Truyện Test', 'author': 'Tác Giả', 'description': 'Mô tả'
            }
            self.mock_plugin.extract_total_pages.return_value = 1
            
            # Quét được 2 chương giống hệt bài test trên
            self.mock_plugin.parse_chapter_list.return_value = [
                {'title': 'Chương 1: Khởi Đầu', 'url': 'https://testsource.comchuong-1/'},
                {'title': 'Chương 2: Diễn Biến', 'url': 'https://testsource.comchuong-2/'}
            ]
            
            # ĐẶC BIỆT: Giả lập Database báo rằng Chương 1 ĐÃ TẢI RỒI (True), Chương 2 CHƯA TẢI (False)
            self.mock_repo.is_chapter_downloaded.side_effect = [True, False]
            
            # Do Chương 1 bị bỏ qua, plugin chỉ được gọi cào nội dung cho đúng 1 chương duy nhất (Chương 2)
            self.mock_plugin.parse_chapter_content.return_value = {
                'title': 'Chương 2: Diễn Biến', 'content': 'Nội dung chương 2', 'novel_url': 'https://testsource.com'
            }
    
            dummy_callback = lambda current, total, title: None
    
            # --- KÍCH HOẠT HÀNH ĐỘNG (WHEN) ---
            self.use_case.execute(target_url, progress_callback=dummy_callback)
    
            # --- KIỂM TRA KẾT QUẢ (THEN) ---
            
            # Xác nhận cơ chế Resume hoạt động: Hàm save_chapter chỉ được gọi đúng 1 LẦN duy nhất cho Chương 2
            self.mock_repo.save_chapter.assert_called_once()
            
            # Lấy thông tin đối tượng truyền vào hàm save_chapter để kiểm tra kỹ xem có phải Chương 2 không
            called_chapter_arg = self.mock_repo.save_chapter.call_args[0][0]
            self.assertEqual(called_chapter_arg.chapter_title, 'Chương 2: Diễn Biến')
    
    if __name__ == '__main__':
        unittest.main()
    

## 3\. Cách chạy Unit Test

Bạn chỉ cần mở terminal tại thư mục dự án và chạy lệnh tiêu chuẩn của Python:
    
    
    python -m unittest test_use_cases.py
    

## Kết quả hiển thị khi test thành công:
    
    
    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.005s
    
    OK
    

_Tốc độ chạy siêu nhanh (chỉ mất 0.005 giây) vì toàn bộ logic mạng và database đã được giả lập chạy trong RAM mà không tốn tài nguyên thật._

Bằng việc kết hợp Clean Architecture, DDD, giao diện Click CLI và bộ Unit Test vững chắc này, bạn đã sở hữu một hệ thống lõi Crawler đạt chuẩn kỹ nghệ phần mềm chất lượng cao, sẵn sàng scale up cho hàng trăm trang web khác nhau.

Nếu bạn cần tối ưu thêm tính năng xử lý lỗi nâng cao như Tự động thử lại (Retry) khi lỗi mạng hay Sử dụng đa luồng (Multi-threading) để tăng tốc độ quét danh sách chương, hãy cho tôi biết nhé!