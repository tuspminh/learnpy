Để cấu hình Replication (Mô hình Master-Slave hay còn gọi là Primary-Replica) cho MariaDB chạy trên Docker, chúng ta sẽ thiết lập 2 container trên cùng một mạng Docker (`docker network`).

Mô hình này giúp Master xử lý các lệnh Ghi (Write), trong khi Slave đồng bộ dữ liệu theo thời gian thực để xử lý các lệnh Đọc (Read) hoặc làm DB dự phòng.

* * *

## Bước 1: Tạo cấu hình cho Master và Slave

Tạo một cấu trúc thư mục như sau trên máy tính của bạn:
    
    
    mariadb-replication/
    ├── docker-compose.yml
    ├── master_config/
    │   └── my.cnf
    └── slave_config/
        └── my.cnf
    

## 1\. File cấu hình cho Master (`master_config/my.cnf`)
    
    
    [mysqld]
    # Định danh duy nhất cho Master (Bắt buộc)
    server-id=1
    
    # Bật tính năng ghi Log Binary để Slave đọc dữ liệu
    log-bin=mysql-bin
    
    # Định nghĩa database muốn đồng bộ (tùy chọn)
    binlog-do-db=mydb
    

## 2\. File cấu hình cho Slave (`slave_config/my.cnf`)
    
    
    [mysqld]
    # Định danh duy nhất cho Slave (Phải khác Master)
    server-id=2
    
    # Bật tính năng ghi log cho slave để tăng tính an toàn
    relay-log=mysql-relay-bin
    log-bin=mysql-bin
    
    # Chỉ định database sẽ nhận đồng bộ
    replicate-do-db=mydb
    

* * *

## Bước 2: Tạo file `docker-compose.yml`

File này sẽ khởi tạo cả 2 DB Server cùng một lúc và kết nối chúng vào chung một mạng tên là `mariadb_net`.
    
    
    version: '3.8'
    
    services:
      mariadb_master:
        image: mariadb:11.4
        container_name: mariadb_master
        restart: always
        ports:
          - "3306:3306"
        environment:
          MARIADB_ROOT_PASSWORD: MasterRootPassword
          MARIADB_DATABASE: mydb
        volumes:
          - master_data:/var/lib/mysql
          - ./master_config:/etc/mysql/conf.d
        networks:
          - mariadb_net
    
      mariadb_slave:
        image: mariadb:11.4
        container_name: mariadb_slave
        restart: always
        ports:
          - "3307:3306" # Đổi port ngoài thành 3307 để tránh trùng với Master
        environment:
          MARIADB_ROOT_PASSWORD: SlaveRootPassword
        volumes:
          - slave_data:/var/lib/mysql
          - ./slave_config:/etc/mysql/conf.d
        networks:
          - mariadb_net
        depends_on:
          - mariadb_master
    
    volumes:
      master_data:
      slave_data:
    
    networks:
      mariadb_net:
        driver: bridge
    

Chạy lệnh sau để khởi động cả 2 container:
    
    
    docker compose up -d
    

* * *

## Bước 3: Cấu hình trên Replication Server

## 1\. Thiết lập trên Master (`mariadb_master`)

Bạn cần tạo một tài khoản đặc quyền để Slave có thể kết nối vào lấy dữ liệu.

Truy cập vào Master container:
    
    
    docker exec -it mariadb_master mariadb -u root -pMasterRootPassword
    

Chạy các lệnh SQL sau:
    
    
    -- Tạo user dành riêng cho việc replication
    CREATE USER 'repl_user'@'%' IDENTIFIED BY 'ReplicaPassword123';
    GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
    FLUSH PRIVILEGES;
    
    -- Kiểm tra trạng thái hiện tại của Master để lấy thông tin File và Position
    SHOW MASTER STATUS;
    

_Lưu ý:_ Hãy ghi lại giá trị của cột File (ví dụ: `mysql-bin.000001`) và Position (ví dụ: `342`) từ kết quả lệnh `SHOW MASTER STATUS`. Gõ `exit` để thoát Master.

## 2\. Thiết lập trên Slave (`mariadb_slave`)

Truy cập vào Slave container:
    
    
    docker exec -it mariadb_slave mariadb -u root -pSlaveRootPassword
    

Chạy các lệnh SQL sau để liên kết Slave với Master (Thay thế các giá trị `MASTER_LOG_FILE` và `MASTER_LOG_POS` bằng thông tin bạn vừa ghi lại ở bước trên):
    
    
    -- Cấu hình kết nối tới Master
    CHANGE MASTER TO
      MASTER_HOST='mariadb_master',
      MASTER_USER='repl_user',
      MASTER_PASSWORD='ReplicaPassword123',
      MASTER_LOG_FILE='mysql-bin.000001',
      MASTER_LOG_POS=342;
    
    -- Kích hoạt tính năng Replication
    START SLAVE;
    
    -- Kiểm tra trạng thái đồng bộ
    SHOW SLAVE STATUS\G
    

* * *

## Bước 4: Kiểm tra kết quả (DBA Testing)

Để đảm bảo hệ thống hoạt động chính xác, bạn hãy kiểm tra 2 thông số quan trọng trong kết quả của lệnh `SHOW SLAVE STATUS\G`:

  * `Slave_IO_Running: Yes`
  * `Slave_SQL_Running: Yes`



Thử nghiệm thực tế:

  1. Bạn kết nối vào Master và tạo một bảng mới hoặc chèn dữ liệu vào database `mydb`.
  2. Kết nối vào Slave, chạy lệnh `SELECT` kiểm tra xem dữ liệu đó đã tự động xuất hiện bên Slave hay chưa.



* * *

Nếu hệ thống gặp lỗi hoặc bạn muốn tối ưu sâu hơn, hãy cho tôi biết:

  * Bạn có gặp lỗi `Slave_IO_Running: No` khi kiểm tra trạng thái không?
  * Bạn có muốn cấu hình thêm mô hình Master-Master (Active-Active) để cả 2 bên đều ghi được dữ liệu không?
  * Bạn có cần giải pháp tự động chuyển mạch (Failover) khi Master bị sập không?