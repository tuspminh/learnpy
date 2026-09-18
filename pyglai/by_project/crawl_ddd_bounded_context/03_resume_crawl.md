Khi thực hiện cào dữ liệu hàng loạt (Bulk Crawl) với khối lượng hàng nghìn đến hàng chục nghìn chương truyện, việc gặp sự cố như mất mạng, lỗi server nguồn (502/504), bị khóa IP tạm thời, hoặc ứng dụng bị crash là điều chắc chắn sẽ xảy ra.

Áp dụng tư duy DDD, trạng thái cào (Crawling State) không thuộc về thực thể truyện (Novel Entity) mà thuộc về Application State của `Data Ingestion Context`. Hệ thống cần một cơ chế Checkpoint & Idempotency (Đồng nhất dữ liệu) để khi chạy lại, nó sẽ tự động bỏ qua những gì đã làm và chỉ cào tiếp phần còn thiếu.

Dưới đây là 3 phương án thiết kế từ đơn giản đến chuyên nghiệp để bạn lựa chọn.

* * *

## Phương án 1: Trạng thái dựa trên Database (State-in-DB) – Khuyên dùng cho dự án vừa và nhỏ

Vì bạn chỉ cào 2-3 nguồn và chạy bulk theo đợt, phương án tối ưu nhất là dùng chính Database làm nơi lưu trạng thái tiến độ (`Crawling Job`).

## Thiết kế cấu trúc dữ liệu Checkpoint:

Bạn tạo một bảng hoặc collection tên là `crawl_tasks` (hoặc `crawl_checkpoints`):

  * `id`: Khóa chính (thường là mã băm MD5 của URL chương để tìm kiếm nhanh).
  * `novel_id`: ID truyện đang cào.
  * `source`: Nguồn truyện (nguon1, nguon2...).
  * `url`: URL chính xác của chương đó.
  * `status`: Trạng thái (`PENDING` \- Chờ cào, `PROCESSING` \- Đang cào, `COMPLETED` \- Thành công, `FAILED` \- Thất bại).
  * `retry_count`: Số lần đã thử lại (mặc định = 0).



## Kịch bản hoạt động (Workflow):

  1. Giai đoạn Discovery (Khám phá): Trước khi cào, hệ thống quét qua mục lục của nguồn để lấy toàn bộ danh sách URL chương. Sau đó lưu tất cả vào bảng `crawl_tasks` với trạng thái `PENDING`. (Nếu danh sách chương quá lớn, bạn có thể lưu theo cơ chế Bulk Insert trước).
  2. Giai đoạn Execution (Chạy cào):

     * Khi khởi chạy, hệ thống truy vấn DB lấy ra các URL có trạng thái `PENDING` hoặc `FAILED` (với `retry_count` < 3).
     * Đẩy các URL này vào `asyncio.Queue`.

  3. Giai đoạn Checkpoint (Ghi nhận kết quả):

     * Khi Fetcher + Parser xử lý thành công và dữ liệu chương đã được lưu thành công vào DB truyện $\rightarrow$ cập nhật trạng thái tác vụ đó trong bảng `crawl_tasks` thành `COMPLETED`.
     * Nếu lỗi, cập nhật thành `FAILED` và tăng `retry_count` thêm 1.




> Ưu điểm: Nếu hệ thống bị sập giữa chừng, khi khởi động lại, lệnh `SELECT WHERE status = 'PENDING'` sẽ tự động lấy đúng điểm bị dừng để chạy tiếp mà không bị trùng lặp dữ liệu.

* * *

## Phương án 2: Sử dụng Redis làm Hàng đợi bền vững (Persistent Queue) – Tối ưu cho tốc độ

Nếu bạn muốn tốc độ đọc/ghi checkpoint cực nhanh và không muốn làm phiền đến Database chính trong lúc cào bulk, Redis là sự lựa chọn hoàn hảo nhờ cơ chế cấu trúc dữ liệu nguyên tử (Atomic).

## Thiết kế cấu trúc dữ liệu trong Redis:

Mỗi truyện hoặc mỗi chiến dịch cào bulk sẽ sở hữu 3 cấu trúc dữ liệu dạng Set hoặc List trong Redis:

  1. `crawl:{novel_id}:pending` (Redis Set): Chứa toàn bộ các URL cần cào. Do là Set nên sẽ tự động loại bỏ trùng lặp (De-duplication).
  2. `crawl:{novel_id}:processing` (Redis Set): Chứa các URL đang được Fetcher tải về.
  3. `crawl:{novel_id}:completed` (Redis Set): Chứa các URL đã bóc tách và lưu DB thành công.



## Kịch bản hoạt động:

  * Sử dụng lệnh `RPOPLPUSH` hoặc các lệnh tương đương để lấy một URL từ tập `pending` chuyển sang tập `processing` một cách an toàn (tránh trường hợp worker lấy xong rồi crash mất luôn URL).
  * Khi Worker xử lý xong xuôi $\rightarrow$ Xóa URL khỏi `processing` và thêm vào `completed`.
  * Khi bị đứt gánh: Bạn chỉ cần viết một hàm cứu hộ (Recovery Script) quét toàn bộ URL còn sót lại trong tập `processing` đẩy ngược lại về tập `pending`, sau đó tiếp tục bật hệ thống lên chạy bình thường.



* * *

## Phương án 3: Lưu log file vật lý dạng JSON Lines (Chữa cháy / Không dùng DB phụ trợ)

Nếu bạn không muốn cài đặt Redis hay tạo thêm bảng trong DB, bạn có thể áp dụng cơ chế ghi nhật ký Write-Ahead Logging (WAL) thủ công bằng file.

  * Mỗi khi hệ thống chuẩn bị cào, bạn sinh ra một file text đặt tên là `checkpoint_{novel_id}.jsonl`.
  * Khi một chương cào thành công, append (ghi nối đuôi) một dòng JSON vào file: `{"url": "...", "status": "success"}`.
  * Khi khởi động lại: Hệ thống sẽ đọc toàn bộ file `jsonl` này, nạp toàn bộ các URL có chữ `"success"` vào một biến dạng `set()` trong Python (In-memory). Sau đó khi duyệt danh sách URL cần cào, chỉ cần kiểm tra nhanh bằng câu lệnh `if url in completed_set: continue` để bỏ qua.



* * *

## 🛠 Thiết kế Code mẫu minh họa cho Phương án 1 (State-in-DB với Checkpoint)

Dưới đây là cách tích hợp tư duy Checkpoint vào mã nguồn Python Asyncio đã tối ưu ở câu trả lời trước:
    
    
    import asyncio
    from typing import List
    
    class BulkScraperWithCheckpoint:
        def __init__(self, fetcher, db_adapter):
            self.fetcher = fetcher
            self.db = db_adapter  # Interface giao tiếp với Database của bạn
    
        async def worker(self, url_queue: asyncio.Queue, source_type: str, novel_id: str):
            parser = ParserFactory.get_parser(source_type)
            
            while not url_queue.empty():
                task_item = await url_queue.get()
                url = task_item["url"]
                task_id = task_item["id"]
                
                try:
                    # 1. Chuyển trạng thái sang PROCESSING trong DB để các tiến trình khác (nếu có) không tranh giành
                    await self.db.update_task_status(task_id, "PROCESSING")
                    
                    # 2. Tiến hành tải và bóc tách
                    html = await self.fetcher.fetch(url)
                    if not html:
                        raise Exception("Không thể tải nội dung HTML")
                        
                    chapter_data = parser.parse(html, novel_id)
                    
                    # 3. Ghi dữ liệu sạch vào DB và cập nhật checkpoint đồng thời (Atomic Transaction)
                    # Đảm bảo nguyên tắc: Hoặc cả hai cùng thành công, hoặc cùng thất bại
                    await self.db.save_chapter_and_complete_task(chapter_data, task_id)
                    print(f"-> Đã cào xong & checkpoint: {chapter_data.title}")
                    
                except Exception as e:
                    print(f"❌ Lỗi xử lý URL {url}: {e}")
                    # Cập nhật trạng thái lỗi để lần sau cào lại
                    await self.db.handle_task_failure(task_id)
                    
                finally:
                    url_queue.task_done()
    
        async def run_pipeline(self, novel_id: str, source_type: str):
            # 1. Lấy danh sách task chưa hoàn thành từ Database (PENDING hoặc FAILED nhưng còn lượt retry)
            pending_tasks: List[dict] = await self.db.get_uncompleted_tasks(novel_id)
            
            if not pending_tasks:
                print("🎉 Tất cả các chương đã được cào thành công trước đó. Không có gì cần cào thêm!")
                return
    
            print(f"🔄 Tìm thấy {len(pending_tasks)} chương chưa hoàn thành. Bắt đầu cào tiếp từ điểm dừng...")
    
            # 2. Nạp các task dở dang vào hàng đợi
            queue = asyncio.Queue()
            for task in pending_tasks:
                await queue.put(task)
    
            # 3. Chạy các worker song song để xử lý tiếp
            workers = [
                asyncio.create_task(self.worker(queue, source_type, novel_id))
                for _ in range(5)
            ]
            
            await queue.join()
            print("🏁 Hoàn thành đợt cào dữ liệu!")
    

## Lời khuyên khi triển khai thực tế:

  * Luôn sử dụng cơ chế Idempotent Key (thường là URL hoặc slug của chương). Nghĩa là dù bạn có lỡ cào trùng một URL 2 lần, Database cũng sẽ tự động xử lý (ví dụ dùng câu lệnh `INSERT ... ON CONFLICT DO UPDATE` hoặc `UPSERT`) chứ không sinh ra hai chương trùng nhau, làm hỏng trải nghiệm đọc truyện.



Để hoàn thiện trọn vẹn bài toán cào bulk này, bạn có muốn chúng ta cùng thảo luận về:

  * Cách thiết kế cấu trúc Bảng dữ liệu trong Database (Schema) để vừa lưu trữ tối ưu dữ liệu bulk, vừa hỗ trợ app đọc truyện hiển thị mục lục (Phân trang chương 1, 2, 3...) mượt mà nhất?
  * Hay bạn muốn tìm hiểu kỹ thuật Xoay tua Proxy / Fake Headers để phòng trường hợp 2-3 nguồn truyện kia bất ngờ bật lá chắn chống Bot (Anti-Bot)?