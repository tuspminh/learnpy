Các thư viện phổ biến và tốt nhất để chuyển đổi file PDF thành JPG trong Python gồm pdf2image, PyMuPDF (fitz), và pypdfium2. Trong đó, `pdf2image` rất phổ biến nhưng cần cài thêm Poppler, còn `PyMuPDF` hoạt động cực kỳ nhanh và không cần cài phần mềm ngoài. [1] 

## Các thư viện tốt nhất

  * pdf2image: Biến trang PDF thành ảnh thông qua Poppler, dễ dùng, chất lượng cao.
  * PyMuPDF (fitz): Siêu nhanh, gọn nhẹ, không cần cài đặt gì ngoài gói pip.
  * pypdfium2: Thư viện hiện đại, hiệu suất cao, thay thế tốt cho các bản cũ. [1, 2, 3, 4] 



## Ví dụ mã nguồn nhanh

## Sử dụng PyMuPDF
    
    
    import fitz  # PyMuPDF
    
    doc = fitz.open("file.pdf")
    for i, page in enumerate(doc):
      pix = page.get_pixmap()
      pix.save(f"trang_{i + 1}.jpg")
    

## Sử dụng pdf2image
    
    
    from pdf2image import convert_from_path
    
    images = convert_from_path("file.pdf")
    for i, image in enumerate(images):
      image.save(f"trang_{i + 1}.jpg", "JPEG")
    

Nếu bạn muốn, tôi có thể hướng dẫn cách:

  * Cài đặt phần mềm phụ trợ Poppler cho `pdf2image` trên máy của bạn
  * Chỉnh độ phân giải (DPI) ảnh cho sắc nét hơn
  * Chỉ định chuyển đổi một vài trang cụ thể thay vì cả file



  


[1] [https://levelup.gitconnected.com](https://translate.google.com/translate?u=https://levelup.gitconnected.com/4-python-libraries-to-convert-pdf-to-images-7a09eba83a09&hl=vi&sl=en&tl=vi&client=sge)

[2] [https://stackoverflow.com](https://translate.google.com/translate?u=https://stackoverflow.com/questions/6605006/convert-pdf-to-image-with-high-resolution&hl=vi&sl=en&tl=vi&client=sge)

[3] [https://blog.fileformat.com](https://blog.fileformat.com/vi/programming/convert-pdf-to-image-in-python/)

[4] [https://ocrmypdf.readthedocs.io](https://translate.google.com/translate?u=https://ocrmypdf.readthedocs.io/en/latest/introduction.html&hl=vi&sl=en&tl=vi&client=sge)