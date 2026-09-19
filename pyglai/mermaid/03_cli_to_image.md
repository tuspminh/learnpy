Để xuất sơ đồ Mermaid ra ảnh bằng dòng lệnh (CLI) trong Python, cách ổn định và chuyên nghiệp nhất là sử dụng thư viện `playwright` để giả lập một trình duyệt ngầm (headless browser), nạp thư viện Mermaid và chụp ảnh màn hình sơ đồ đó.

Cách này không phụ thuộc vào các công cụ cài đặt phức tạp của hệ thống như Node.js hay Graphviz. Dưới đây là hướng dẫn chi tiết từng bước.

* * *

## Bước 1: Cài đặt các thư viện cần thiết

Bạn mở Terminal / Command Prompt lên và chạy lệnh sau để cài đặt `playwright` và cài đặt trình duyệt ngầm cho nó:
    
    
    pip install playwright
    playwright install chromium
    

* * *

## Bước 2: Viết mã Python để chuyển code Mermaid thành ảnh

Bạn tạo một file Python (ví dụ: `mermaid_to_image.py`) và dán đoạn mã bên dưới vào. Đoạn mã này sẽ tạo ra một trang HTML tạm thời, render mã Mermaid của bạn và chụp lại ảnh ở định dạng PNG (hoặc JPEG).
    
    
    import asyncio
    from playwright.async_api import async_playwright
    
    # 1. Định nghĩa đoạn mã Mermaid của bạn
    mermaid_code = """
    flowchart TD
        A[Start Context] -->|Request| B(Processing)
        B --> C{Success?}
        C -->|Yes| D[(Database)]
        C -->|No| E[Error Log]
    """
    
    # HTML template chứa thư viện Mermaid.js từ CDN
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module">
            import mermaid from 'https://jsdelivr.net';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        <style>
            body {{
                margin: 0;
                background-color: white;
                display: inline-block; /* Giúp kích thước body vừa khít với sơ đồ */
            }}
            .mermaid {{
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid">
            {mermaid_code}
        </div>
    </body>
    </html>
    """
    
    async def generate_mermaid_image(output_path="diagram.png"):
        async with async_playwright() as p:
            # Khởi chạy trình duyệt ngầm
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Nạp nội dung HTML vào trang
            await page.set_content(html_template)
            
            # Chờ thư viện Mermaid render xong sơ đồ (chờ selector svg xuất hiện)
            await page.wait_for_selector(".mermaid svg")
            
            # Lấy phần tử chứa sơ đồ để chụp ảnh chuẩn kích thước, không thừa khoảng trắng
            element = await page.query_selector(".mermaid")
            
            # Chụp ảnh và lưu lại
            await element.screenshot(path=output_path, omissions_background=True)
            print(f" Xuất ảnh thành công: {output_path}")
            
            await browser.close()
    
    # Chạy chương trình
    asyncio.run(generate_mermaid_image("my_diagram.png"))
    

* * *

## Bước 3: Chạy CLI và kiểm tra kết quả

Bạn chạy file Python vừa tạo bằng lệnh:
    
    
    python mermaid_to_image.py
    

Sau khi chạy xong, một file ảnh `my_diagram.png` sẽ xuất hiện ở ngay thư mục chứa file code của bạn với chất lượng hiển thị sắc nét.

## Mẹo nâng cao:

  * Muốn đổi sang ảnh nền tối (Dark mode): Bạn chỉ cần sửa cấu hình ở phần đầu đoạn mã HTML thành: `mermaid.initialize({ startOnLoad: true, theme: 'dark' });` và đổi css `background-color: #1e1e1e;`.
  * Đọc code từ file `.md`: Bạn có thể viết thêm vài dòng lệnh Python để tự động mở một file Markdown sẵn có, trích xuất đoạn code nằm giữa cặp thẻ ````mermaid` rồi truyền vào biến `mermaid_code`.



Bạn có muốn tôi viết nâng cao thêm đoạn code trên để nó tự động đọc trực tiếp một file `.md` có sẵn rồi tự động quét và xuất toàn bộ sơ đồ trong đó ra file ảnh không?