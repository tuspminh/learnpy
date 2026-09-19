Để hiểu sâu và làm chủ hoàn toàn Mermaid, dưới đây là cẩm nang chi tiết toàn bộ các tính năng từ cơ bản đến nâng cao của loại sơ đồ phổ biến nhất: Flowchart (Sơ đồ lưu đồ).

* * *

## 1\. Phân biệt `graph` và `flowchart`

Ở các phiên bản Mermaid mới, bạn nên dùng từ khóa `flowchart` thay cho `graph`.

  * `flowchart` hỗ trợ vẽ đường nối đẹp hơn, không bị đè lên chữ và hỗ trợ nhiều hình khối nâng cao hơn.
  * Cú pháp chung: `flowchart [HƯỚNG]` (Ví dụ: `flowchart TD`, `flowchart LR`).



* * *

## 2\. Chi tiết cấu trúc ID và Nhãn (Text)

Một Node (nút) luôn gồm 2 phần: ID (dùng để viết code nối mạch) và Nhãn (chữ hiển thị trên màn hình).

  * Cú pháp: `ID[Chữ hiển thị]`
  * Quy tắc: ID không được chứa dấu cách hoặc ký tự đặc biệt. Chữ hiển thị thì thoải mái.
  * Mẹo xuống dòng: Sử dụng thẻ `<br>` nếu muốn chữ trong nút xuống hàng.


    
    
    flowchart LR
        id1[Dòng thứ nhất <br> Dòng thứ hai]
    

* * *

## 3\. Toàn bộ các hình khối Node hỗ trợ trong Mermaid

Bạn có thể copy đoạn mã này vào [Mermaid Live Editor](https://mermaid.live/) để xem hình dáng trực quan:
    
    
    flowchart TD
        A[Chữ nhật mặc định]
        B(Chữ nhật bo góc)
        C([Hình viên thuốc / Start-End])
        D[[Quy trình con / Subroutine]]
        E[(Cơ sở dữ liệu / Database)]
        F((Hình tròn / Circle))
        G>Cờ đuôi nheo / Asymmetric]
        H{Hình thoi / Điều kiện}
        I{{Hình lục giác / Hexagon}}
        J[\Hình bình hành / Input-Output\]
        K[/Hình bình hành ngược/]
        L[\Hình thang/]
        M[/Hình thang ngược/]
    

* * *

## 4\. Chi tiết các loại đường nối (Edgelink) nâng cao

Ngoài các mũi tên cơ bản, bạn có thể kiểm soát độ dài và kiểu dáng của đường nối bằng cách thêm các ký tự `-` hoặc `=`.

  * Độ dài mũi tên: Thêm dấu `-` để kéo dài đường nối giúp sơ đồ thoáng hơn.

    * Ngắn: `A --> B`
    * Dài vừa: `A ---> B`
    * Rất dài: `A ----> B`

  * Mũi tên 2 đầu: `A <--> B`
  * Mũi tên dạng liên kết ẩn (Không có đầu nhọn): `A --- B`
  * Đường nối có mũi tên tròn hoặc chéo (Chỉ có ở `flowchart`):

    * Đầu tròn: `A --o B`
    * Đầu chéo chữ X: `A --x B`




* * *

## 5\. Tương tác và Liên kết (Click Events & Siêu liên kết)

Mermaid cho hiện thực hóa sơ đồ tĩnh thành sơ đồ động bằng cách chèn liên kết web (Hyperlink) vào các Node:
    
    
    flowchart LR
        A[Google] --> B[GitHub]
        
        %% Cú pháp click: click [ID_Node] "[Đường_Dẫn_Web]" "Tiêu đề khi di chuột vào"
        click A "https://google.com" "Mở Google"
        click B "https://github.com" "Mở GitHub"
    

_Lưu ý: Tính năng click này hoạt động tốt trên Mermaid Live Editor và các trang web hỗ trợ HTML, nhưng có thể bị chặn trên một số trình xem Markdown tĩnh vì lý do bảo mật._

* * *

## 6\. Quản lý Font chữ và Định dạng Text nâng cao (Markdown in Nodes)

Nếu bạn muốn chữ bên trong Node được in đậm, _in nghiêng_ hoặc có icon, hãy kích hoạt tính năng Markdown bằng cách thêm dấu `"` ở hai đầu nhãn:
    
    
    flowchart LR
        A["Cần **in đậm** ở đây"] --> B["Hoặc *in nghiêng* chỗ này"]
    

* * *

## 7\. Thiết lập Themes (Giao diện hiển thị)

Bạn có thể đổi toàn bộ màu sắc của sơ đồ sang các bộ màu có sẵn bằng cách khai báo chỉ thị `%%{init: {...}}%%` ở ngay dòng đầu tiên của khối mã:

  * Màu tối (Dark Mode):
        
        %%{init: {'theme': 'dark'}}%%
        flowchart TD
            A --> B
        

  * Các theme khác: Thay thế `'dark'` bằng `'neutral'` (trung tính), `'forest'` (xanh lá cây), hoặc `'base'` (để tự custom hoàn toàn).



Bạn có muốn tôi cung cấp cấu trúc chi tiết của một loại sơ đồ phức tạp hơn như Sequence Diagram (Sơ đồ tuần tự tương tác API) hay Gantt Chart (Sơ đồ tiến độ dự án) không?