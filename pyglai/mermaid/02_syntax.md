Để viết sơ đồ trong Markdown, bạn cần sử dụng khối mã (code block) có nhãn là `mermaid`. Cấu trúc cốt lõi của một sơ đồ luôn gồm 2 phần: Khai báo loại & hướng sơ đồ và Định nghĩa các mối quan hệ.

Dưới đây là hướng dẫn cú pháp từ cơ bản đến nâng cao để bạn dễ dàng làm chủ:

## 1\. Cú pháp cơ bản & Các loại hình khối (Node)

Mặc định, nếu bạn chỉ ghi chữ, node sẽ có hình chữ nhật. Để đổi hình dạng, bạn bao bọc văn bản bằng các ký tự đặc biệt:
    
    
    ```mermaid
    graph TD
        NodeA[Hình chữ nhật]
        NodeB(Hình chữ nhật bo góc)
        NodeC([Hình viên thuốc])
        NodeD[[Hình quy trình con]]
        NodeE[(Hình trụ - Cơ sở dữ liệu)]
        NodeF((Hình tròn))
        NodeG{Hình thoi - Nhánh điều kiện}
        NodeH{{Hình lục giác}}
        NodeI[\Hình bình hành dòng chảy\]
    ```
    

## 2\. Cú pháp các loại mũi tên (Cạnh nối)

Bạn có thể tùy biến đường nối giữa các node để thể hiện các loại liên kết khác nhau:

  * Mũi tên cơ bản: `A --> B`
  * Mũi tên không có đầu nhọn: `A --- B`
  * Mũi tên có chữ ở giữa: `A -->|Nội dung chữ| B` hoặc `A -- Chữ --> B`
  * Đường nét đứt (Dotted): `A -.-> B` hoặc có chữ: `A -. Chữ .-> B`
  * Đường nét đậm (Thick): `A ==> B` hoặc có chữ: `A == Chữ ==> B`



* * *

## 3\. Cú pháp nhóm các Node (Subgraph)

Để gom các thành phần liên quan vào một vùng (như cách bạn làm với Core/Supporting Domain), hãy dùng từ khóa `subgraph`:
    
    
    subgraph "Tên Nhóm Hiển Thị"
        Node1[Nội dung 1]
        Node2[Nội dung 2]
        Node1 --> Node2
    end
    

* * *

## 4\. Cách thêm màu sắc và kiểu dáng (Styling)

Bạn có thể tự định nghĩa màu sắc, viền, chữ cho từng node thông qua từ khóa `style`:
    
    
    ```mermaid
    graph LR
        A[Node Khách Hàng] --> B[Node Hệ Thống]
        
        %% Cú pháp: style [TênNode] fill:[MãMàu],stroke:[MãMàuViền],stroke-width:[ĐộDàyViền]
        style A fill:#f9f,stroke:#333,stroke-width:4px
        style B fill:#bbf,stroke:#f66,stroke-width:2px,stroke-dasharray: 5 5
    ```
    

_(Mẹo: Dấu`%%` dùng để viết ghi chú/comment trong Mermaid, hệ thống sẽ không hiển thị đoạn này)._

* * *

## 5\. Một số loại sơ đồ phổ biến khác ngoài `graph`

Mermaid không chỉ vẽ lưu đồ (`graph`/`flowchart`), nó còn hỗ trợ rất nhiều loại sơ đồ chuyên dụng khác bằng cách thay đổi từ khóa khai báo ở dòng đầu tiên:

  * Sơ đồ tuần tự (Sequence Diagram): Dùng cho luồng API hoặc giao tiếp qua lại.
        
        sequenceDiagram
            Alice->>Bob: Hello Bob, how are you?
            Bob-->>Alice: Great!
        

  * Sơ đồ trạng thái (State Diagram):
        
        stateDiagram-v2
            [*] --> Still
            Still --> [*]
        

  * Sơ đồ thực thể mối quan hệ (ER Diagram): Dùng để thiết kế database.
        
        erDiagram
            CUSTOMER ||--o{ ORDER : places
        




Bạn đang muốn tập trung viết loại sơ đồ nào tiếp theo? Mình có thể hỗ trợ cung cấp mẫu chuẩn (template) của loại sơ đồ đó (ví dụ: sơ đồ tuần tự API, sơ đồ thực thể Database...) để bạn chỉnh sửa cho nhanh.