Dưới đây là toàn bộ mã nguồn được chuyển đổi thành ứng dụng giao diện dòng lệnh (CLI) chuyên nghiệp bằng thư viện `click`.

Mã nguồn vẫn được giữ cấu trúc DDD/SOLID, tách biệt logic dọn dẹp văn bản (`TextNormalizer`), chia nhỏ chuỗi (`StoryDocument`), chuyển đổi AI (`EdgeTTSService`) và gộp âm thanh (`PydubAudioMerger`).

## 1\. File mã nguồn hoàn chỉnh: `cli_app.py`
    
    
    import sys
    import os
    import re
    import glob
    import asyncio
    from typing import List, Optional
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    import click
    import edge_tts
    from pydub import AudioSegment
    
    # =====================================================================
    # 1. LỚP DOMAIN (Models, Rules & Interfaces)
    # =====================================================================
    
    @dataclass(frozen=True)
    class Voice:
        id: str
    
    @dataclass(frozen=True)
    class AudioPreset:
        name: str
        rate: str
        pitch: str
    
    @dataclass
    class StoryDocument:
        name: str
        text: str
    
        def is_empty(self) -> bool:
            return not self.text.strip()
    
        def get_chunks(self, max_chars: int = 2500) -> List[str]:
            """Chia văn bản thành các đoạn nhỏ dưới max_chars, không làm cắt đôi từ"""
            if self.is_empty():
                return []
                
            sentences = re.split(r'(?<=[.!?])\s+', self.text.strip())
            chunks = []
            current_chunk = []
            current_length = 0
    
            for sentence in sentences:
                if len(sentence) > max_chars:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    for i in range(0, len(sentence), max_chars):
                        chunks.append(sentence[i:i+max_chars])
                    continue
    
                if current_length + len(sentence) + 1 > max_chars:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_length += len(sentence) + 1
    
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            return chunks
    
    class TextNormalizer:
        """Quy tắc lõi chuẩn hóa văn bản truyện giúp AI đọc chuẩn ngữ điệu"""
        @staticmethod
        def normalize(text: str) -> str:
            if not text: return ""
            text = re.sub(r'[“”„‟″‴]', '"', text)
            text = re.sub(r'[‘’‚‛′]', "'", text)
            text = re.sub(r'–', '-', text)
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            text = re.sub(r'\.{4,}', '...', text)
            text = re.sub(r',+', ',', text)
            text = re.sub(r'!+', '!', text)
            text = re.sub(r'\?+', '?', text)
            text = re.sub(r'[^\w\s.,!?;:"\'\-\(\)\[\]\n]', '', text)
            def capitalize_match(match):
                return match.group(1) + match.group(2).upper()
            text = re.sub(r'([.!?]\s+)([a-zỳỹỷỹỵựửữựửứừứợởỡờớảãạảáàạậẩẫậấpấầẩẫậpếềểễệpíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ])', capitalize_match, text)
            lines = text.split('\n')
            cleaned_lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in lines if re.sub(r'[ \t]+', ' ', line).strip()]
            return '\n'.join(cleaned_lines)
    
    class ITTSService(ABC):
        @abstractmethod
        async def convert_chunk_to_mp3(self, text: str, voice: Voice, rate: str, pitch: str, output_path: str) -> None: pass
    
    class IAudioMerger(ABC):
        @abstractmethod
        def merge_mp3_files(self, src_paths: List[str], dest_path: str) -> None: pass
    
    class IFileRepository(ABC):
        @abstractmethod
        def read_text(self, path: str) -> str: pass
        @abstractmethod
        def write_text(self, path: str, content: str) -> None: pass
    
    # =====================================================================
    # 2. LỚP INFRASTRUCTURE (Cài đặt hạ tầng công nghệ)
    # =====================================================================
    
    class EdgeTTSService(ITTSService):
        async def convert_chunk_to_mp3(self, text: str, voice: Voice, rate: str, pitch: str, output_path: str) -> None:
            communicate = edge_tts.Communicate(text=text, voice=voice.id, rate=rate, pitch=pitch)
            await communicate.save(output_path)
    
    class PydubAudioMerger(IAudioMerger):
        def merge_mp3_files(self, src_paths: List[str], dest_path: str) -> None:
            if not src_paths: return
            combined = AudioSegment.empty()
            for path in src_paths:
                if os.path.exists(path):
                    combined += AudioSegment.from_mp3(path)
            combined.export(dest_path, format="mp3")
    
    class LocalFileRepository(IFileRepository):
        def read_text(self, path: str) -> str:
            with open(path, "r", encoding="utf-8") as f: return f.read()
        def write_text(self, path: str, content: str) -> None:
            with open(path, "w", encoding="utf-8") as f: f.write(content)
    
    # =====================================================================
    # 3. LỚP APPLICATION (Điều phối kịch bản Usecases)
    # =====================================================================
    
    class TTSOrchestrator:
        def __init__(self, tts_service: ITTSService, audio_merger: IAudioMerger, file_repo: IFileRepository):
            self._tts_service = tts_service
            self._audio_merger = audio_merger
            self._file_repo = file_repo
    
        async def process_document(self, doc: StoryDocument, voice: Voice, rate: str, pitch: str, output_path: str) -> None:
            chunks = doc.get_chunks(max_chars=2500)
            if not chunks: return
            
            temp_files: List[str] = []
            output_dir = os.path.dirname(output_path) or "."
            
            try:
                for idx, chunk in enumerate(chunks):
                    click.echo(f"  -> Đang xử lý khối {idx + 1}/{len(chunks)}...")
                    temp_path = os.path.join(output_dir, f"temp_{doc.name}_{idx}.mp3")
                    await self._tts_service.convert_chunk_to_mp3(chunk, voice, rate, pitch, temp_path)
                    temp_files.append(temp_path)
                    
                click.echo(f"  -> Đang gộp âm thanh vào: {output_path}")
                self._audio_merger.merge_mp3_files(temp_files, output_path)
            finally:
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        try: os.remove(temp_file)
                        except Exception: pass
    
    # =====================================================================
    # 4. LỚP PRESENTATION (Giao diện CLI dùng Click)
    # =====================================================================
    
    PRESETS = {
        "co-tich": AudioPreset("co-tich", "-12%", "+3Hz"),
        "kinh-di": AudioPreset("kinh-di", "-16%", "-4Hz"),
        "ngon-tinh": AudioPreset("ngon-tinh", "-15%", "-1Hz"),
        "kiem-hiep": AudioPreset("kiem-hiep", "-13%", "-3Hz"),
        "mac-dinh": AudioPreset("mac-dinh", "+0%", "+0Hz")
    }
    
    @click.command()
    @click.argument('path', type=click.Path(exists=True))
    @click.option('--output', '-o', type=click.Path(), help='Đường dẫn file MP3 đầu ra (nếu là input file) hoặc thư mục lưu MP3 (nếu là input folder).')
    @click.option('--preset', '-p', type=click.Choice(list(PRESETS.keys())), help='Sử dụng cấu hình dựng sẵn (co-tich, kinh-di, ngon-tinh, kiem-hiep, mac-dinh).')
    @click.option('--rate', '-r', default='+0%', help='Tốc độ đọc, ví dụ: -10% hoặc +5% (Bị bỏ qua nếu dùng --preset).', show_default=True)
    @click.option('--pitch', '-pi', default='+0Hz', help='Cao độ giọng, ví dụ: -2Hz hoặc +3Hz (Bị bỏ qua nếu dùng --preset).', show_default=True)
    @click.option('--voice', '-v', default='en-US-AriaNeural', help='Mã giọng đọc Edge-TTS (Ví dụ: en-US-AriaNeural, vi-VN-HoaiAnNeural).', show_default=True)
    @click.option('--normalize', is_flag=True, help='Tự động chạy bộ dọn dẹp, sửa lỗi dấu câu và viết hoa file text gốc trước khi chuyển audio.')
    def run_cli(path: str, output: Optional[str], preset: Optional[str], rate: str, pitch: str, voice: str, normalize: bool):
        """
        Ứng dụng CLI chuyển đổi văn bản sang audiobook sử dụng Edge-TTS.
        PATH: Đường dẫn tới file .txt đơn lẻ HOẶC một Thư mục chứa các file .txt.
        """
        # 1. Khởi tạo cấu trúc dependencies
        file_repo = LocalFileRepository()
        tts_service = EdgeTTSService()
        audio_merger = PydubAudioMerger()
        orchestrator = TTSOrchestrator(tts_service, audio_merger, file_repo)
    
        # 2. Xác định thông số âm thanh (Ưu tiên preset)
        final_rate = rate
        final_pitch = pitch
        if preset:
            final_rate = PRESETS[preset].rate
            final_pitch = PRESETS[preset].pitch
            click.echo(click.style(f"[*] Áp dụng preset '{preset}': Rate={final_rate}, Pitch={final_pitch}", fg="cyan"))
    
        voice_obj = Voice(voice)
    
        # 3. Phân tách logic xử lý File đơn lẻ hoặc Thư mục
        is_dir = os.path.isdir(path)
        txt_files = glob.glob(os.path.join(path, "*.txt")) if is_dir else [path]
    
        if is_dir and not txt_files:
            raise click.ClickException("Không tìm thấy file .txt nào trong thư mục đã chỉ định!")
    
        # Xác định thư mục đầu ra
        if is_dir:
            out_dir = output if output else path
            os.makedirs(out_dir, exist_ok=True)
        else:
            out_dir = os.path.dirname(output) if output else os.path.dirname(path) or "."
    
        click.echo(click.style(f"[+] Bắt đầu quét và xử lý {len(txt_files)} file văn bản...", fg="green", bold=True))
    
        for file_p in txt_files:
            base_name = os.path.splitext(os.path.basename(file_p))[0]
            click.echo(click.style(f"\n[➔] File đang xử lý: {file_p}", fg="yellow"))
    
            # Tiến hành chuẩn hóa nếu có flag --normalize
            if normalize:
                click.echo("  -> Đang tự động chuẩn hóa dấu câu và viết hoa văn bản...")
                raw_content = file_repo.read_text(file_p)
                cleaned_content = TextNormalizer.normalize(raw_content)
                file_repo.write_text(file_p, cleaned_content)
    
            # Đọc dữ liệu đã xử lý để chuyển đổi tts
            final_content = file_repo.read_text(file_p)
            doc = StoryDocument(name=base_name, text=final_content)
    
            if doc.is_empty():
                click.echo(click.style("  -> Bỏ qua vì file trống.", fg="red"))
                continue
    
            # Xác định file mp3 đích cuối cùng
            if is_dir:
                final_mp3_path = os.path.join(out_dir, f"{base_name}.mp3")
            else:
                final_mp3_path = output if output else os.path.join(out_dir, f"{base_name}.mp3")

            # Chạy tác vụ bất đồng bộ thông qua asyncio loop  
            asyncio.run(orchestrator.process_document(doc, voice_obj, final_rate, final_pitch, final_mp3_path))  
            click.echo(click.style(f" ✓ Đã hoàn thành audiobook tại: {final_mp3_path}", fg="green"))

            click.echo(click.style("\n[===] HOÀN THÀNH TẤT CẢ CÁC TÁC VỤ! [===]", fg="green", bold=True))

    if name == 'main':  
    run_cli()
        
 
---
    
### 2. Cách cài đặt & Chạy ứng dụng bằng `uv`

Vì ứng dụng chạy trên môi trường CLI, bạn cần cài đặt thư viện `click`:
```bash
uv pip install click edge-tts pydub
    

## Hướng dẫn các câu lệnh chạy thực tế:

  * Chuyển đổi 1 file, dùng Preset có sẵn (ví dụ: `co-tich`), tự động dọn lỗi chữ hoa dấu câu (`--normalize`):
        
        uv run cli_app.py story.txt --preset co-tich --voice en-US-JennyNeural --normalize
        

  * Chuyển đổi 1 file, tự định nghĩa cụ thể `--rate` và `--pitch` nâng cao:
        
        uv run cli_app.py story.txt -r "-15%" -pi "+2Hz" -v en-US-GuyNeural -o outputs/fairy_tale.mp3
        

  * Quét hàng loạt cả Thư mục chứa nhiều file text, tự gộp theo mỗi file riêng biệt:
        
        uv run cli_app.py ./my_stories_folder/ --preset kinh-di -v vi-VN-NamMinhNeural -o ./audio_outputs/
        




* * *

## 3\. Đóng gói ứng dụng thành file CLI `.exe` độc lập

Bạn có thể đóng gói kịch bản CLI này bằng PyInstaller để người khác có thể sử dụng ngay trong Terminal/CMD mà không cần máy phải cài môi trường Python:
    
    
    uv run --with click --with edge-tts --with pydub --with pyinstaller pyinstaller --onefile --name="story-tts" cli_app.py
    

_(Lưu ý: Không dùng tham số`--noconsole` khi đóng gói ứng dụng CLI, để hệ thống hiển thị văn bản hướng dẫn `click.echo` trực tiếp ra màn hình terminal)._

Sau khi chạy xong, file `story-tts.exe` trong thư mục `dist` có thể gõ lệnh trực tiếp dạng: `story-tts.exe my_story.txt -p co-tich`. Bạn có cần hỗ trợ thêm về cách viết tài liệu hướng dẫn nhanh (README) cho file CLI này không?