Để hiển thị thanh tiến trình (Progress Bar) trực quan cho người dùng khi ứng dụng đang xử lý từng chunk văn bản, chúng ta sẽ tích hợp thư viện `tqdm`.

Để tuân thủ nghiêm ngặt nguyên lý Clean Architecture, lớp logic nghiệp vụ (`Use Case`) sẽ không import trực tiếp `tqdm` vì đây là một thư viện giao diện (UI) thuộc lớp ngoài cùng (`Infrastructure`). Thay vào đó, chúng ta sẽ định nghĩa một cơ chế Callback hoặc Observer trừu tượng để Use Case thông báo tiến độ, và CLI phía ngoài sẽ hiện thực hóa bằng `tqdm`.

* * *

## 📦 Bước 1: Cài đặt thư viện tqdm bằng uv

Thêm gói `tqdm` vào các dependency chính của dự án:
    
    
    uv add tqdm
    

* * *

## 🎛️ Bước 2: Định nghĩa Cổng giao tiếp Tiến độ (Interface)

Tạo một interface đơn giản trong lớp Domain hoặc Interfaces để định nghĩa cách Use Case gửi tín hiệu tiến độ ra ngoài.
    
    
    # src/tts_app/interfaces/progress_reporter.py
    from abc import ABC, abstractmethod
    
    class IProgressReporter(ABC):
        @abstractmethod
        def initialize(self, total_steps: int, desc: str) -> None:
            """Khởi tạo thanh tiến trình với tổng số bước."""
            pass
    
        @abstractmethod
        def update(self, steps: int = 1) -> None:
            """Cập nhật tiến độ thêm n bước."""
            pass
    
        @abstractmethod
        def close(self) -> None:
            """Đóng thanh tiến trình khi hoàn thành."""
            pass
    

* * *

## 🧠 Bước 3: Cập nhật Lớp Use Case để truyền dữ liệu tiến độ

Sửa đổi `ProcessTTSUseCase` để nhận vào một `IProgressReporter`. Use Case sẽ tính toán số lượng chunk trước, sau đó kích hoạt thanh tiến trình và cập nhật sau mỗi lần một file chunk được engine tổng hợp xong.
    
    
    # src/tts_app/use_cases/process_tts.py
    from pathlib import Path
    from typing import Optional
    from tts_app.domain.models import TTSConfig
    from tts_app.interfaces.tts_engine import ITTSEngine
    from tts_app.interfaces.text_splitter import ITextSplitter
    from tts_app.interfaces.progress_reporter import IProgressReporter
    
    class ProcessTTSUseCase:
        def __init__(self, engine: ITTSEngine, vi_splitter: ITextSplitter, en_splitter: ITextSplitter):
            self.engine = engine
            self.vi_splitter = vi_splitter
            self.en_splitter = en_splitter
    
        def execute(
            self, 
            input_path: Path, 
            config: TTSConfig, 
            language: str = "vi", 
            progress_reporter: Optional[IProgressReporter] = None
        ) -> None:
            # 1. Đọc văn bản đầu vào
            text = input_path.read_text(encoding="utf-8")
            
            # 2. Phân tách văn bản thành các chunk tối ưu ngữ cảnh
            splitter = self.vi_splitter if language == "vi" else self.en_splitter
            chunks_text = splitter.split(text, default_size=config.chunk_size)
            total_chunks = len(chunks_text)
            
            if total_chunks == 0:
                return
    
            # 3. Khởi tạo cấu trúc thư mục chứa output chunk
            chunk_dir = input_path.parent / input_path.stem
            chunk_dir.mkdir(parents=True, exist_ok=True)
            
            # 4. Kích hoạt thông báo tiến độ (nếu có)
            if progress_reporter:
                progress_reporter.initialize(total_steps=total_chunks, desc=f"Converting {input_path.name}")
            
            generated_files = []
            
            # 5. Lặp và xử lý từng chunk văn bản
            for idx, chunk_txt in enumerate(chunks_text):
                chunk_file = chunk_dir / f"chunk_{idx+1}.mp3"
                
                # Gọi Engine xử lý tín hiệu âm thanh
                self.engine.synthesize(chunk_txt, chunk_file, config)
                generated_files.append(chunk_file)
                
                # Cập nhật thanh tiến trình sau khi hoàn thành xong 1 chunk
                if progress_reporter:
                    progress_reporter.update(1)
                    
            if progress_reporter:
                progress_reporter.close()
    
            # 6. Tiến hành gộp file âm thanh
            if config.merge_audio and total_chunks > 1:
                merged_file = input_path.parent / f"{input_path.stem}_merged.mp3"
                self._merge_files(generated_files, merged_file)
    

* * *

## 🖥️ Bước 4: Hiện thực hóa Bộ hiển thị bằng tqdm ở lớp CLI (Infrastructure)

Bây giờ tại lớp giao diện dòng lệnh, chúng ta sẽ tạo lớp `TqdmProgressReporter` kế thừa từ Interface phía trên và bọc thư viện `tqdm` lại.
    
    
    # src/tts_app/infrastructure/cli/progress.py
    from tqdm import tqdm
    from tts_app.interfaces.progress_reporter import IProgressReporter
    
    class TqdmProgressReporter(IProgressReporter):
        def __init__(self):
            self._pbar = None
    
        def initialize(self, total_steps: int, desc: str) -> None:
            # Cấu hình giao diện thanh tiến trình trực quan
            self._pbar = tqdm(
                total=total_steps,
                desc=desc,
                unit="chunk",
                leave=True,
                bar_format="{l_bar}{bar:30}{r_bar}{bar:-10b}"
            )
    
        def update(self, steps: int = 1) -> None:
            if self._pbar:
                self._pbar.update(steps)
    
        def close(self) -> None:
            if self._pbar:
                self._pbar.close()
    

* * *

## 🔌 Bước 5: Cập nhật hàm điều phối CLI và lệnh đóng gói

Cập nhật lại lệnh `convert` trong file `src/tts_app/infrastructure/cli/commands.py` để nhét `TqdmProgressReporter` vào Use Case:
    
    
    # Thêm import ở đầu file commands.py
    from tts_app.infrastructure.cli.progress import TqdmProgressReporter
    
    # Trong hàm convert_text sau khi khởi tạo use_case:
    for target in targets:
        # Khởi tạo một reporter mới cho mỗi file văn bản
        reporter = TqdmProgressReporter()
        use_case.execute(target, config, language=lang, progress_reporter=reporter)
    

Khi đóng gói lại ứng dụng bằng PyInstaller, bạn nhớ thêm flag `--hidden-import="tqdm"` để đảm bảo thư viện tiến trình được nhét trọn vẹn vào file thực thi:
    
    
    uv run pyinstaller --onefile \
        --name="tts" \
        --additional-hooks-dir=hooks \
        --add-data "bin:bin" \
        --hidden-import="click" \
        --hidden-import="edge_tts" \
        --hidden-import="google.cloud.texttospeech" \
        --hidden-import="pydub" \
        --hidden-import="tqdm" \
        src/tts_app/main.py
    

## 🎯 Giao diện Terminal thực tế khi chạy

Khi người dùng chạy file thực thi hoặc qua lệnh gõ dòng lệnh, họ sẽ nhìn thấy một thanh tiến trình chạy mượt mà ngay trên Terminal:
    
    
    Converting tailieu.txt:  40%|████████████            | 2/5 [00:04<00:06, 2.1s/chunk]
    

Cấu trúc ứng dụng của bạn hiện tại đã cực kỳ hoàn chỉnh và đạt chuẩn doanh nghiệp (Production-ready). Bạn có muốn mở rộng thêm tính năng Xử lý đa luồng (Multi-threading / Async) để chuyển đổi song song nhiều file văn bản cùng lúc nhằm tối ưu hóa thời gian chờ không?