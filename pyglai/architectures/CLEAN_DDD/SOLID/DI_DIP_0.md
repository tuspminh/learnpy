Để kết hợp Dependency Inversion Principle (DIP) và Dependency Injection (DI), bạn cần dùng DIP làm định hướng thiết kế (tạo ra các Interface) và dùng DI làm kỹ thuật để hiện thực hóa thiết kế đó (bơm đối tượng vào lớp sử dụng).

Dưới đây là hướng dẫn từng bước theo mô hình Trước và Sau khi áp dụng, minh họa bằng ngôn ngữ TypeScript/JavaScript.

* * *

## ❌ Khi chưa áp dụng DIP và DI (Thiết kế tồi)

Trong ví dụ này, lớp cấp cao `OrderManager` tự khởi tạo trực tiếp lớp cấp thấp `MySQLDatabase`. Điều này vi phạm DIP (phụ thuộc chặt chẽ) và không thể áp dụng DI.
    
    
    // Module cấp thấp (Chi tiết triển khai)
    class MySQLDatabase {
        saveOrder(orderId: string) {
            console.log(`Đang lưu đơn hàng ${orderId} vào MySQL...`);
        }
    }
    
    // Module cấp cao (Logic nghiệp vụ)
    class OrderManager {
        private database: MySQLDatabase;
    
        constructor() {
            // Tự khởi tạo đối tượng cụ thể -> Dính chặt (Tightly Coupled)
            this.database = new MySQLDatabase(); 
        }
    
        createOrder(orderId: string) {
            // Xử lý logic...
            this.database.saveOrder(orderId);
        }
    }
    

  * Hệ quả: Nếu sau này bạn muốn đổi sang MongoDB, bạn buộc phải sửa lại code bên trong lớp `OrderManager`. Việc viết Unit Test cũng cực kỳ khó khăn vì không thể thay thế `MySQLDatabase` bằng dữ liệu giả (Mock).



* * *

## Cách kết hợp DIP và DI (Thiết kế chuẩn)

Để giải quyết vấn đề, chúng ta thực hiện 3 bước:

  1. DIP - Tạo tính trừu tượng: Tạo ra một `Interface` chung làm cầu nối.
  2. DIP - Đảo ngược phụ thuộc: Cả lớp cấp cao và cấp thấp đều hướng về `Interface` này.
  3. DI - Tiêm phụ thuộc (Injection): Không tự `new` đối tượng bên trong lớp nữa, mà truyền nó vào thông qua `constructor`.


    
    
    // ==========================================
    // BƯỚC 1: Tạo Abstraction (Interface) theo DIP
    // ==========================================
    interface Database {
        saveOrder(orderId: string): void;
    }
    
    // ==========================================
    // BƯỚC 2: Các module cấp thấp triển khai Interface
    // ==========================================
    class MySQLDatabase implements Database {
        saveOrder(orderId: string) {
            console.log(`Lưu đơn hàng ${orderId} vào MySQL.`);
        }
    }
    
    class MongoDatabase implements Database {
        saveOrder(orderId: string) {
            console.log(`Lưu đơn hàng ${orderId} vào MongoDB.`);
        }
    }
    
    // ==========================================
    // BƯỚC 3: Module cấp cao nhận Interface qua DI (Constructor Injection)
    // ==========================================
    class OrderManager {
        private database: Database; // Phụ thuộc vào Interface, không phụ thuộc Class cụ thể
    
        // KỸ THUẬT DI: Bơm đối tượng từ ngoài vào thông qua constructor
        constructor(database: Database) {
            this.database = database;
        }
    
        createOrder(orderId: string) {
            this.database.saveOrder(orderId);
        }
    }
    
    // ==========================================
    // CÁCH VẬN HÀNH TRONG THỰC TẾ
    // ==========================================
    // Nếu muốn dùng MySQL:
    const mySQLDb = new MySQLDatabase();
    const orderManagerWithMySQL = new OrderManager(mySQLDb); // Tiêm MySQL vào
    orderManagerWithMySQL.createOrder("HD001");
    
    // Nếu muốn đổi sang MongoDB, lớp OrderManager hoàn toàn KHÔNG CẦN THAY ĐỔI CODE:
    const mongoDb = new MongoDatabase();
    const orderManagerWithMongo = new OrderManager(mongoDb); // Tiêm MongoDB vào
    orderManagerWithMongo.createOrder("HD002");
    

* * *

## 3 Phương pháp "Tiêm" phụ thuộc (DI Types) phổ biến

Trong thực tế, bạn có thể truyền đối tượng phụ thuộc vào lớp cấp cao qua 3 con đường chính:

  * Constructor Injection (Khuyên dùng): Truyền phụ thuộc trực tiếp qua hàm khởi tạo `constructor()` như ví dụ phía trên. Đảm bảo đối tượng luôn đủ dữ liệu ngay khi vừa tạo ra.
  * Setter Injection: Truyền phụ thuộc qua một hàm gán (Setter method). Thích hợp khi phụ thuộc có thể thay đổi linh hoạt trong quá trình chạy (Runtime).
        
        class OrderManager {
            private database!: Database;
            setDatabase(database: Database) { this.database = database; } // Setter
        }
        

  * Interface Injection: Định nghĩa một Interface có sẵn hàm để nhận phụ thuộc. Phương pháp này ít được sử dụng nhất trong các dự án hiện đại vì rườm rà.



* * *

## Sử dụng IoC Container (Tự động hóa DI)

Khi dự án lớn lên, việc tự tay `new` từng đối tượng rồi truyền vào nhau (Manual DI) sẽ rất mệt mỏi. Các lập trình viên thường dùng các thư viện/framework gọi là IoC Container để tự động làm việc này (ví dụ: NestJS/InversifyJS trong Node.js, Spring Boot trong Java, hay .NET Core ServiceCollection).

Bạn chỉ cần khai báo: _"Tôi muốn lớp`OrderManager` cần một `Database`"_, Container sẽ tự tìm xem `Database` đang được cấu hình là loại nào (MySQL hay Mongo) để tự khởi tạo và gom chúng lại với nhau.

* * *

Nếu bạn muốn tiếp tục đào sâu, hãy cho tôi biết:

  * Bạn muốn xem cách cấu hình IoC Container tự động trên một framework cụ thể nào không (ví dụ: NestJS, Spring Boot, .NET Core)?
  * Bạn muốn tìm hiểu cách viết Unit Test (Mocking) cho lớp `OrderManager` sau khi đã áp dụng DI/DIP?