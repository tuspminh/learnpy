# Buổi 3 — Xây Queue Server qua TCP

Hôm nay chúng ta sẽ biến `InMemoryQueue` của Buổi 2 thành **một Queue Server độc lập**.

Mục tiêu:

```text
                    TCP
Producer ───────────────────┐
                            ▼
                     ┌──────────────┐
                     │ Queue Server │
                     │              │
                     │ InMemoryQueue│
                     └──────┬───────┘
                            ▲
                            │ TCP
                       ┌────┴────┐
                       │         │
                    Worker 1  Worker 2
```

Sau buổi này, `crawl-worker` sẽ **không cần import `InMemoryQueue` nữa**.

Nó giao tiếp với queue server qua TCP.

---

# 1. Vì sao phải dùng TCP?

Buổi 2:

```python
queue = InMemoryQueue()

worker = CrawlWorker(queue)
```

Queue nằm cùng process:

```text
┌──────────────────────────┐
│ Python Process            │
│                          │
│ Queue                    │
│   ▲                      │
│   │                      │
│ Worker                   │
└──────────────────────────┘
```

Điều này không phù hợp với crawler thực tế.

Ta muốn:

```text
┌──────────────────┐
│ Queue Server     │
│ :9000            │
└────────┬─────────┘
         │
    TCP network
         │
    ┌────┼────┐
    ▼    ▼    ▼
   W1    W2   W3
```

Worker có thể chạy:

```text
process 1
process 2
process 3
máy A
máy B
máy C
```

miễn là truy cập được Queue Server.

---

# 2. Kiến trúc Buổi 3

Ta tách thành 4 tầng:

```text
┌──────────────────────────────┐
│          Client              │
│                              │
│ enqueue()                    │
│ reserve()                    │
│ ack()                        │
│ fail()                       │
└──────────────┬───────────────┘
               │
               │ TCP
               ▼
┌──────────────────────────────┐
│        TCP Server            │
│                              │
│ accept connection             │
│ read request                  │
│ parse protocol                │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│        Dispatcher            │
│                              │
│ ENQUEUE → queue.enqueue()    │
│ RESERVE → queue.reserve()    │
│ ACK     → queue.ack()        │
│ FAIL    → queue.fail()       │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│       InMemoryQueue          │
└──────────────────────────────┘
```

Đây là architecture quan trọng.

**TCP Server không được chứa logic queue.**

---

# 3. Protocol là gì?

Client và server cần thống nhất cách nói chuyện.

Ví dụ client gửi:

```text
ENQUEUE
```

server không biết payload là gì.

Ta cần protocol.

Phiên bản đầu tiên dùng JSON.

Request:

```json
{
    "command": "ENQUEUE",
    "queue": "chapter",
    "payload": {
        "url": "https://example.com/chapter/1"
    }
}
```

Server trả:

```json
{
    "ok": true,
    "job_id": "abc123"
}
```

Đây là một protocol application-level.

---

# 4. Tại sao không gửi Python object?

Không làm:

```python
pickle.dumps(job)
```

cho protocol public.

Vì:

* coupling mạnh
* khó debug
* khó tương thích
* security risk với dữ liệu không tin cậy

Ta muốn:

```text
JSON
 ↓
bytes
 ↓
TCP
```

và ngược lại:

```text
TCP
 ↓
bytes
 ↓
JSON
```

---

# 5. TCP là stream, không phải message

Đây là kiến thức **cực kỳ quan trọng**.

Bạn không thể giả định:

```python
data = conn.recv(4096)
```

sẽ nhận đúng một request.

Ví dụ client gửi:

```text
REQUEST A
REQUEST B
```

TCP có thể trả:

```text
REQUEST A + REQUEST B
```

hoặc:

```text
REQUEST
A
```

hoặc:

```text
REQ
UEST A
```

Do đó chúng ta cần **framing protocol**.

---

# 6. Framing bằng newline

Phiên bản đầu tiên:

```text
JSON_REQUEST\n
```

Ví dụ:

```json
{"command":"STATS"}\n
```

Mỗi request kết thúc bằng:

```text
\n
```

Server đọc:

```python
reader.readline()
```

Như vậy:

```text
TCP Stream

{"command":"STATS"}\n
{"command":"RESERVE"}\n
{"command":"ACK"}\n
```

được tách thành:

```text
Request 1
Request 2
Request 3
```

Đây là protocol rất đơn giản nhưng cực kỳ phù hợp để học.

---

# 7. Tạo project

Tạm thời:

```text
queue_server/
│
├── job.py
├── queue.py
├── protocol.py
├── server.py
└── client.py
```

---

# 8. `job.py`

Dùng model của Buổi 2:

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class Job:
    queue: str
    payload: Any

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: str = "pending"

    attempts: int = 0

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

---

# 9. `queue.py`

Ta cải tiến queue.

```python
from collections import deque
from threading import Lock

from job import Job


class InMemoryQueue:

    def __init__(self):
        self._pending = deque()
        self._running = {}
        self._completed = {}

        self._lock = Lock()

    def enqueue(self, job: Job) -> str:
        with self._lock:
            job.status = "pending"
            self._pending.append(job)

            return job.id

    def reserve(self) -> Job | None:
        with self._lock:

            if not self._pending:
                return None

            job = self._pending.popleft()

            job.status = "running"
            job.attempts += 1

            self._running[job.id] = job

            return job

    def ack(self, job_id: str) -> bool:
        with self._lock:

            job = self._running.pop(
                job_id,
                None,
            )

            if job is None:
                return False

            job.status = "completed"

            self._completed[job.id] = job

            return True

    def fail(self, job_id: str) -> bool:
        with self._lock:

            job = self._running.pop(
                job_id,
                None,
            )

            if job is None:
                return False

            job.status = "pending"

            self._pending.append(job)

            return True

    def stats(self) -> dict:
        with self._lock:
            return {
                "pending": len(self._pending),
                "running": len(self._running),
                "completed": len(self._completed),
            }
```

---

# 10. Protocol

Tạo `protocol.py`.

```python
import json


def encode_message(message: dict) -> bytes:
    data = json.dumps(
        message,
        ensure_ascii=False,
    )

    return (data + "\n").encode("utf-8")


def decode_message(data: bytes) -> dict:
    return json.loads(
        data.decode("utf-8")
    )
```

Ví dụ:

```python
message = {
    "command": "STATS",
}

data = encode_message(message)

print(data)
```

Ta nhận:

```text
b'{"command": "STATS"}\n'
```

---

# 11. Server TCP cơ bản

Python có:

```python
import socket
```

Server:

```python
import socket


HOST = "127.0.0.1"
PORT = 9000


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)

server.bind((HOST, PORT))
server.listen()

print(
    f"Queue Server listening "
    f"on {HOST}:{PORT}"
)
```

Sau đó:

```python
while True:
    conn, addr = server.accept()

    print(
        f"Client connected: {addr}"
    )

    conn.close()
```

Chạy:

```text
Queue Server listening on 127.0.0.1:9000
```

Server đang lắng nghe TCP.

---

# 12. Nhận request

Ta thử:

```python
while True:
    conn, addr = server.accept()

    data = conn.recv(4096)

    print(data)

    conn.close()
```

Nếu client gửi:

```json
{"command":"STATS"}\n
```

server nhận bytes.

Nhưng chúng ta cần:

```text
bytes
 ↓
decode
 ↓
JSON
 ↓
dict
```

---

# 13. Server handler

Tạo:

```python
def handle_client(conn):
    data = conn.recv(4096)

    message = decode_message(data)

    print(message)

    response = {
        "ok": True,
    }

    conn.sendall(
        encode_message(response)
    )

    conn.close()
```

Server:

```python
while True:
    conn, addr = server.accept()

    handle_client(conn)
```

---

# 14. Dispatcher

Đây mới là phần quan trọng.

Không nên:

```python
if command == "ENQUEUE":
    ...
elif command == "RESERVE":
    ...
```

trộn lẫn vào TCP code.

Tạo:

```python
class Dispatcher:

    def __init__(self, queue):
        self.queue = queue

    def dispatch(self, request: dict) -> dict:

        command = request.get("command")

        if command == "STATS":
            return self.handle_stats()

        return {
            "ok": False,
            "error": "unknown_command",
        }

    def handle_stats(self):
        return {
            "ok": True,
            "stats": self.queue.stats(),
        }
```

---

# 15. Thêm `ENQUEUE`

```python
def handle_enqueue(self, request):
    queue_name = request["queue"]
    payload = request["payload"]

    job = Job(
        queue=queue_name,
        payload=payload,
    )

    job_id = self.queue.enqueue(job)

    return {
        "ok": True,
        "job_id": job_id,
    }
```

Dispatcher:

```python
def dispatch(self, request):

    command = request.get("command")

    if command == "ENQUEUE":
        return self.handle_enqueue(request)

    if command == "STATS":
        return self.handle_stats()

    return {
        "ok": False,
        "error": "unknown_command",
    }
```

---

# 16. Thêm `RESERVE`

```python
def handle_reserve(self, request):
    job = self.queue.reserve()

    if job is None:
        return {
            "ok": True,
            "job": None,
        }

    return {
        "ok": True,
        "job": {
            "id": job.id,
            "queue": job.queue,
            "payload": job.payload,
            "status": job.status,
            "attempts": job.attempts,
        },
    }
```

Request:

```json
{
    "command": "RESERVE",
    "queue": "chapter"
}
```

Response:

```json
{
    "ok": true,
    "job": {
        "id": "...",
        "queue": "chapter",
        "payload": {
            "url": "..."
        },
        "status": "running",
        "attempts": 1
    }
}
```

---

# 17. Thêm `ACK`

```python
def handle_ack(self, request):
    job_id = request["job_id"]

    success = self.queue.ack(job_id)

    return {
        "ok": success,
    }
```

Request:

```json
{
    "command": "ACK",
    "job_id": "abc"
}
```

---

# 18. Thêm `FAIL`

```python
def handle_fail(self, request):
    job_id = request["job_id"]

    success = self.queue.fail(job_id)

    return {
        "ok": success,
    }
```

---

# 19. Dispatcher hoàn chỉnh

```python
from job import Job


class Dispatcher:

    def __init__(self, queue):
        self.queue = queue

    def dispatch(self, request: dict) -> dict:

        command = request.get("command")

        if command == "ENQUEUE":
            return self.handle_enqueue(request)

        if command == "RESERVE":
            return self.handle_reserve(request)

        if command == "ACK":
            return self.handle_ack(request)

        if command == "FAIL":
            return self.handle_fail(request)

        if command == "STATS":
            return self.handle_stats()

        return {
            "ok": False,
            "error": "unknown_command",
        }

    def handle_enqueue(self, request):

        job = Job(
            queue=request["queue"],
            payload=request["payload"],
        )

        job_id = self.queue.enqueue(job)

        return {
            "ok": True,
            "job_id": job_id,
        }

    def handle_reserve(self, request):

        job = self.queue.reserve()

        if job is None:
            return {
                "ok": True,
                "job": None,
            }

        return {
            "ok": True,
            "job": {
                "id": job.id,
                "queue": job.queue,
                "payload": job.payload,
                "status": job.status,
                "attempts": job.attempts,
            },
        }

    def handle_ack(self, request):

        success = self.queue.ack(
            request["job_id"]
        )

        return {
            "ok": success,
        }

    def handle_fail(self, request):

        success = self.queue.fail(
            request["job_id"]
        )

        return {
            "ok": success,
        }

    def handle_stats(self):

        return {
            "ok": True,
            "stats": self.queue.stats(),
        }
```

---

# 20. Server hoàn chỉnh

```python
import socket

from queue import InMemoryQueue
from protocol import (
    decode_message,
    encode_message,
)
from dispatcher import Dispatcher


HOST = "127.0.0.1"
PORT = 9000


queue = InMemoryQueue()
dispatcher = Dispatcher(queue)


def handle_client(conn):

    try:
        data = conn.recv(4096)

        request = decode_message(data)

        response = dispatcher.dispatch(
            request
        )

        conn.sendall(
            encode_message(response)
        )

    except Exception as exc:

        response = {
            "ok": False,
            "error": str(exc),
        }

        conn.sendall(
            encode_message(response)
        )

    finally:
        conn.close()


def main():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1,
    )

    server.bind(
        (HOST, PORT)
    )

    server.listen()

    print(
        f"Queue Server listening "
        f"on {HOST}:{PORT}"
    )

    while True:

        conn, addr = server.accept()

        print(
            f"Client connected: {addr}"
        )

        handle_client(conn)


if __name__ == "__main__":
    main()
```

---

# 21. Client

Bây giờ tạo `client.py`.

```python
import socket

from protocol import (
    encode_message,
    decode_message,
)


class QueueClient:

    def __init__(
        self,
        host="127.0.0.1",
        port=9000,
    ):
        self.host = host
        self.port = port

    def execute(
        self,
        request: dict,
    ) -> dict:

        with socket.create_connection(
            (self.host, self.port)
        ) as conn:

            conn.sendall(
                encode_message(request)
            )

            data = conn.recv(4096)

            return decode_message(data)
```

---

# 22. `enqueue()`

Thêm:

```python
def enqueue(
    self,
    queue: str,
    payload: dict,
):

    return self.execute({
        "command": "ENQUEUE",
        "queue": queue,
        "payload": payload,
    })
```

Client hoàn chỉnh:

```python
class QueueClient:

    def __init__(
        self,
        host="127.0.0.1",
        port=9000,
    ):
        self.host = host
        self.port = port

    def execute(self, request):

        with socket.create_connection(
            (self.host, self.port)
        ) as conn:

            conn.sendall(
                encode_message(request)
            )

            data = conn.recv(4096)

            return decode_message(data)

    def enqueue(
        self,
        queue,
        payload,
    ):
        return self.execute({
            "command": "ENQUEUE",
            "queue": queue,
            "payload": payload,
        })

    def reserve(self, queue):

        return self.execute({
            "command": "RESERVE",
            "queue": queue,
        })

    def ack(self, job_id):

        return self.execute({
            "command": "ACK",
            "job_id": job_id,
        })

    def fail(self, job_id):

        return self.execute({
            "command": "FAIL",
            "job_id": job_id,
        })

    def stats(self):

        return self.execute({
            "command": "STATS",
        })
```

---

# 23. Test Queue Server

Terminal 1:

```text
python server.py
```

Ta có:

```text
Queue Server listening on 127.0.0.1:9000
```

Terminal 2:

```python
from client import QueueClient


client = QueueClient()

result = client.enqueue(
    queue="chapter",
    payload={
        "url": "https://example.com/chapter/1",
        "book_id": 100,
    },
)

print(result)
```

Ví dụ:

```text
{
    'ok': True,
    'job_id': '...'
}
```

---

# 24. Reserve Job

```python
result = client.reserve("chapter")

print(result)
```

Ví dụ:

```text
{
    "ok": True,
    "job": {
        "id": "...",
        "queue": "chapter",
        "payload": {
            "url": "https://example.com/chapter/1",
            "book_id": 100
        },
        "status": "running",
        "attempts": 1
    }
}
```

---

# 25. ACK

```python
job_id = result["job"]["id"]

print(
    client.ack(job_id)
)
```

Server:

```text
running
   │
   │ ACK
   ▼
completed
```

---

# 26. STATS

```python
print(
    client.stats()
)
```

Ví dụ:

```text
{
    "ok": True,
    "stats": {
        "pending": 0,
        "running": 0,
        "completed": 1
    }
}
```

---

# 27. Bây giờ Crawl Worker không biết Queue implementation

Đây là thành quả quan trọng nhất của Buổi 3.

Worker:

```python
from client import QueueClient


class CrawlWorker:

    def __init__(self):
        self.queue = QueueClient()

    def run_once(self):

        response = self.queue.reserve(
            "chapter"
        )

        job = response["job"]

        if job is None:
            return

        try:
            self.process(job)

        except Exception:
            self.queue.fail(job["id"])

        else:
            self.queue.ack(job["id"])

    def process(self, job):

        url = job["payload"]["url"]

        print(
            f"Crawling {url}"
        )
```

Worker:

```text
CrawlWorker
     │
     │ TCP
     ▼
Queue Server
     │
     ▼
InMemoryQueue
```

Worker **không biết**:

```text
deque
dict
Lock
```

nó cũng không biết queue đang dùng:

```text
memory
SQLite
Redis
PostgreSQL
```

Đây chính là abstraction mà ta cần.

---

# 28. Một vấn đề rất lớn trong server hiện tại

Server của chúng ta đang:

```python
conn, addr = server.accept()

handle_client(conn)
```

Điều này nghĩa là:

```text
Client A
   │
   │ request
   ▼
server
   │
   │ xử lý
   │
   │ xong
   ▼
Client B
```

Nếu Client A mất 10 giây:

```text
Client A ────────────── 10s ──────────────►
                                             
Client B
   │
   │ bị chờ
   X
```

Đây là **single-threaded server**.

Không phù hợp với nhiều crawl worker.

---

# 29. Phiên bản tiếp theo

Ta sẽ chuyển:

```text
                 Server
                   │
                   ▼
              accept()
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
        Thread   Thread   Thread
          │        │        │
          W1       W2       W3
```

hoặc sau này:

```text
asyncio
   │
   ├── client 1
   ├── client 2
   ├── client 3
   └── client 4
```

Nhưng **chưa làm ngay**.

Trước tiên phải giải quyết một vấn đề còn quan trọng hơn.

---

# 30. Protocol hiện tại còn lỗi

Client đang:

```python
conn.sendall(request)
data = conn.recv(4096)
```

Giả định response nhỏ hơn 4096 bytes.

Điều này không an toàn.

Đặc biệt payload crawler có thể lớn:

```json
{
    "url": "...",
    "headers": {},
    "metadata": {},
    "options": {}
}
```

TCP không đảm bảo:

```python
recv(4096)
```

nhận đủ response.

Ở phiên bản tiếp theo ta sẽ xây **proper framing**:

```text
┌────────────┬─────────────────────────┐
│ length     │ JSON payload            │
│ 4 bytes    │ N bytes                 │
└────────────┴─────────────────────────┘
```

Ví dụ:

```text
00000087{"command":"RESERVE", ...}
```

hoặc sử dụng newline framing nhưng phải xử lý nhiều message trên cùng connection đúng cách.

---

# 31. Trạng thái hệ thống hiện tại

Sau Buổi 3:

```text
                 ┌─────────────────────┐
                 │    Queue Server     │
                 │                     │
                 │ TCP :9000           │
                 │                     │
                 │ Dispatcher          │
                 │        │            │
                 │        ▼            │
                 │ InMemoryQueue       │
                 └─────────┬───────────┘
                           │
                    ┌──────┼──────┐
                    │      │      │
                    ▼      ▼      ▼
                   W1     W2     W3
```

Protocol:

```text
ENQUEUE
RESERVE
ACK
FAIL
STATS
```

Job lifecycle:

```text
PENDING
   │
   │ RESERVE
   ▼
RUNNING
   │
   ├──── ACK ────► COMPLETED
   │
   └──── FAIL ───► PENDING
```

---

# Bài tập Buổi 3

Bạn nên tự code lại từ đầu, **không copy nguyên project**.

### Bài 1

Thêm command:

```text
PING
```

Request:

```json
{
    "command": "PING"
}
```

Response:

```json
{
    "ok": true,
    "message": "PONG"
}
```

### Bài 2

Thêm:

```text
QUEUE_SIZE
```

Ví dụ:

```json
{
    "command": "QUEUE_SIZE",
    "queue": "chapter"
}
```

Response:

```json
{
    "ok": true,
    "queue": "chapter",
    "size": 10
}
```

### Bài 3

Test scenario:

```text
Producer
   │
   ├── Job 1
   ├── Job 2
   ├── Job 3
   ├── Job 4
   └── Job 5
```

Sau đó:

```text
Worker
   │
   ├── reserve Job 1
   ├── ACK
   ├── reserve Job 2
   ├── FAIL
   └── reserve Job 3
```

Kiểm tra `STATS`.

### Bài 4 — quan trọng

Viết một script:

```text
producer.py
```

tạo **100 chapter jobs**:

```text
chapter/1
chapter/2
...
chapter/100
```

Sau đó dùng một client khác reserve từng job.

Mục tiêu là bạn phải nhìn thấy rõ:

```text
Producer
    │
    │ 100 jobs
    ▼
Queue Server
    │
    │ reserve
    ▼
Worker
```

---

## Buổi 4 sẽ làm gì?

Buổi 4 chúng ta sẽ **thiết kế Job Model chuyên nghiệp hơn**, không còn chỉ là `dataclass` đơn giản:

```text
Job
├── job_id
├── queue_name
├── job_type
├── payload
├── priority
├── status
├── attempts
├── max_attempts
├── created_at
├── reserved_at
├── completed_at
├── failed_at
├── error
└── metadata
```

Sau đó xây **Job State Machine**:

```text
                 ┌──────────────┐
                 │   PENDING    │
                 └──────┬───────┘
                        │
                     RESERVE
                        │
                        ▼
                 ┌──────────────┐
                 │   RUNNING    │
                 └──────┬───────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
           SUCCESS              ERROR
              │                   │
              ▼                   ▼
         COMPLETED             RETRY
                                  │
                                  ▼
                              PENDING
                                  │
                           max_attempts
                                  │
                                  ▼
                                DEAD
```

Đây là bước bắt đầu đưa Queue Server của chúng ta từ một **TCP demo** thành một **job queue thực sự có semantics rõ ràng**, phù hợp để gắn vào crawler framework của bạn.
