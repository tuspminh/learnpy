Được. Vì chúng ta đã hoàn thành **Giai đoạn III — OOP Master**, mình đề xuất Giai đoạn IV không chỉ là học thêm syntax nâng cao, mà chuyển sang mục tiêu:

> **Hiểu Python ở mức runtime + concurrency + metaprogramming + production engineering.**

Đặc biệt mình sẽ sắp xếp lại thứ tự một chút để kiến thức đi từ **Python internals → typing/metaprogramming → concurrency → performance → packaging/testing → design → architecture → production project**.

# 🐍 GIAI ĐOẠN IV — PYTHON ADVANCED

**Mục tiêu cuối giai đoạn**

Sau giai đoạn này, bạn có thể:

* Hiểu Python quản lý object và memory như thế nào.
* Hiểu Reference Counting và Garbage Collector.
* Hiểu Descriptor, `__getattribute__`, `__getattr__`, `property`.
* Hiểu Metaclass và class creation.
* Làm việc với Reflection / Introspection / Dynamic Import.
* Đọc và hiểu Python Bytecode cơ bản.
* Hiểu GIL và mô hình Thread / Process / AsyncIO.
* Xây dựng crawler concurrent.
* Profiling và tối ưu Python.
* Viết package/library production.
* Testing ở mức architecture.
* Áp dụng Design Pattern đúng lúc.
* Thiết kế framework có plugin architecture.
* Xây dựng một **production-style crawler framework**.

---

# PHẦN I — Python Runtime & Memory

### Buổi 1 — Python Object Model

```text
object
  ↓
type
  ↓
instance
```

Học:

* Object là gì?
* Identity
* Type
* Value
* `id()`
* `type()`
* `isinstance()`
* `__class__`
* `__dict__`

---

### Buổi 2 — Memory Management

* Python memory model
* Stack vs Heap
* Object allocation
* Python Memory Manager
* `pymalloc`
* Arena
* Pool
* Block

---

### Buổi 3 — Reference Counting

```python
sys.getrefcount()
```

Học:

* Reference
* Reference count
* `INCREF`
* `DECREF`
* Khi nào object được giải phóng?
* Circular reference

---

### Buổi 4 — Garbage Collector

* CPython GC
* Generational GC
* Generation
* `gc` module
* Detect cyclic references
* `gc.collect()`
* `gc.get_objects()`
* Debug GC

---

### Buổi 5 — Shallow Copy

```python
copy.copy()
```

* Assignment vs Copy
* Shallow copy
* Nested object
* Mutable object
* `__copy__`

---

### Buổi 6 — Deep Copy

```python
copy.deepcopy()
```

* Deep copy algorithm
* Memo dictionary
* Circular reference
* `__deepcopy__`
* Khi nào không nên deepcopy?

---

### Buổi 7 — Memory Debugging

* `sys.getsizeof`
* `gc`
* `tracemalloc`
* Memory leak
* Object retention
* Snapshot
* Memory profiling

### Mini Project

**Memory Leak Lab**

Tạo các chương trình cố tình gây:

```text
Reference Leak
Circular Reference
Cache Leak
Global Object Retention
```

---

# PHẦN II — Descriptor & Attribute System

### Buổi 8 — Attribute Lookup

Đây là buổi cực kỳ quan trọng.

Tìm hiểu:

```python
obj.x
```

Python thực sự làm gì?

```text
object
 ↓
__getattribute__
 ↓
descriptor
 ↓
instance __dict__
 ↓
class
```

---

### Buổi 9 — `__getattribute__`

* Attribute interception
* Override lookup
* Infinite recursion
* `object.__getattribute__`

---

### Buổi 10 — `__getattr__`

```python
def __getattr__(self, name):
    ...
```

Phân biệt:

```text
__getattribute__
        vs
__getattr__
```

---

### Buổi 11 — Descriptor Foundation

```python
class Descriptor:
    def __get__(...)
    def __set__(...)
    def __delete__(...)
```

---

### Buổi 12 — Data Descriptor

* `__get__`
* `__set__`
* `__delete__`
* Precedence rules

---

### Buổi 13 — Non-data Descriptor

```python
__get__
```

Hiểu tại sao:

```python
obj.method
```

hoạt động.

---

### Buổi 14 — `property`

Hiểu `property` thực chất là Descriptor.

```python
@property
def name(self):
    ...
```

---

### Buổi 15 — Descriptor thực chiến

Xây:

```text
ValidatedField
TypedField
RangeField
RequiredField
```

---

### Buổi 16 — Descriptor Framework

Mini framework:

```python
class User:
    name = StringField()
    age = IntegerField()
    email = EmailField()
```

---

# PHẦN III — Reflection & Introspection

### Buổi 17 — Introspection

```python
dir()
type()
id()
vars()
```

---

### Buổi 18 — `inspect`

```python
inspect.signature()
inspect.getmembers()
inspect.getsource()
inspect.isfunction()
inspect.ismethod()
```

---

### Buổi 19 — Reflection

* Runtime inspection
* Dynamic attribute access
* Dynamic method invocation

```python
getattr()
setattr()
hasattr()
delattr()
```

---

### Buổi 20 — Dynamic Import

```python
importlib.import_module()
```

Xây:

```text
Plugin Loader
```

---

### Buổi 21 — Dynamic Class Discovery

Tìm tất cả subclass:

```python
BasePlugin.__subclasses__()
```

---

### Buổi 22 — Plugin System

```text
Application
    ↓
Plugin Loader
    ↓
Plugin A
Plugin B
Plugin C
```

---

# PHẦN IV — Metaclass

### Buổi 23 — Class là Object

```python
class User:
    pass
```

Thực chất:

```text
User
 ↓
instance of type
```

---

### Buổi 24 — `type`

```python
type("User", (), {})
```

Dynamic class creation.

---

### Buổi 25 — Metaclass Foundation

```python
class Meta(type):
    ...
```

---

### Buổi 26 — `__new__` của Metaclass

Hiểu quá trình:

```text
class statement
       ↓
metaclass
       ↓
__new__
       ↓
__init__
       ↓
class object
```

---

### Buổi 27 — `__prepare__`

```python
class Meta(type):
    @classmethod
    def __prepare__(...)
```

---

### Buổi 28 — Metaclass Validation

Xây:

```python
class Model:
    ...
```

Metaclass tự động kiểm tra field.

---

### Buổi 29 — Metaclass Registry

```text
BaseModel
   ↓
User
Product
Order
```

Tự động register class.

---

### Buổi 30 — Metaclass vs Decorator vs Descriptor

So sánh:

```text
Decorator
Descriptor
Metaclass
```

Khi nào dùng cái nào?

---

# PHẦN V — Advanced Typing

### Buổi 31 — Abstract Base Class nâng cao

```python
ABC
abstractmethod
```

* ABC internals
* Virtual subclass
* `register()`

---

### Buổi 32 — Protocol

```python
class Repository(Protocol):
    ...
```

Structural typing.

---

### Buổi 33 — ABC vs Protocol

```text
ABC
↓
Nominal typing

Protocol
↓
Structural typing
```

---

### Buổi 34 — Generic cơ bản nâng cao

```python
TypeVar
Generic
```

---

### Buổi 35 — Generic Class

```python
Repository[T]
```

---

### Buổi 36 — Generic Function

```python
def first(items: Sequence[T]) -> T:
    ...
```

---

### Buổi 37 — Generic nâng cao

* `TypeVar`
* Bound
* Constraint
* Variance
* Covariance
* Contravariance
* Invariance

---

### Buổi 38 — `ParamSpec`

Typing decorator.

---

### Buổi 39 — `TypeVarTuple`

Variadic generics.

---

### Buổi 40 — Advanced Type Design

Kết hợp:

```text
Protocol
+
Generic
+
ABC
+
TypeVar
```

Thiết kế:

```python
Repository[T]
Service[T]
Cache[T]
```

---

# PHẦN VI — Python Bytecode & CPython

### Buổi 41 — Python Compilation Pipeline

```text
.py
 ↓
Tokenizer
 ↓
Parser
 ↓
AST
 ↓
Bytecode
 ↓
Python VM
```

---

### Buổi 42 — `dis`

```python
import dis
```

Đọc bytecode.

---

### Buổi 43 — Code Object

```python
function.__code__
```

Tìm hiểu:

```text
co_code
co_consts
co_names
co_varnames
```

---

### Buổi 44 — Bytecode Deep Dive

* LOAD
* STORE
* CALL
* RETURN
* JUMP
* BUILD

---

### Buổi 45 — Python Execution Model

```text
Source
 ↓
AST
 ↓
Bytecode
 ↓
Frame
 ↓
Evaluation Loop
```

---

# PHẦN VII — GIL & Threading

### Buổi 46 — GIL

* GIL là gì?
* Vì sao CPython có GIL?
* GIL ảnh hưởng CPU-bound?
* GIL ảnh hưởng I/O-bound?

---

### Buổi 47 — Thread Foundation

```python
threading.Thread
```

---

### Buổi 48 — Thread Synchronization

* Lock
* RLock
* Semaphore
* Event
* Condition

---

### Buổi 49 — Race Condition

Ví dụ:

```text
Thread A
Thread B
   ↓
shared state
```

---

### Buổi 50 — ThreadPoolExecutor

```python
concurrent.futures
```

---

### Buổi 51 — Producer / Consumer

```text
Producer
   ↓
Queue
   ↓
Workers
```

---

### Buổi 52 — Thread Architecture

Thiết kế:

```text
Crawler
   ↓
Queue
   ↓
Worker Threads
   ↓
Downloader
   ↓
Parser
```

---

# PHẦN VIII — Multiprocessing

### Buổi 53 — Process

```python
multiprocessing.Process
```

Thread vs Process.

---

### Buổi 54 — ProcessPoolExecutor

```python
ProcessPoolExecutor
```

---

### Buổi 55 — IPC

* Queue
* Pipe
* Shared Memory

---

### Buổi 56 — Serialization

```text
Process
 ↓
pickle
 ↓
IPC
```

---

### Buổi 57 — CPU-bound Architecture

```text
Main
 ↓
Process Pool
 ↓
CPU Workers
```

---

### Buổi 58 — Thread vs Process

So sánh toàn diện:

|               | Thread  | Process     |
| ------------- | ------- | ----------- |
| Memory        | Shared  | Separate    |
| GIL           | Có      | Mỗi process |
| I/O           | Tốt     | Tốt         |
| CPU           | Hạn chế | Tốt         |
| Communication | Dễ      | Khó hơn     |

---

# PHẦN IX — Async Programming

### Buổi 59 — Coroutine

```python
async def
await
```

---

### Buổi 60 — Event Loop

```text
Event Loop
   ↓
Task
   ↓
Coroutine
```

---

### Buổi 61 — `await` Deep Dive

* Awaitable
* Coroutine
* Future
* Task

---

### Buổi 62 — Task

```python
asyncio.create_task()
```

---

### Buổi 63 — Cancellation

```python
task.cancel()
CancelledError
```

---

### Buổi 64 — Async Exception

```python
asyncio.gather()
```

---

### Buổi 65 — Timeout

```python
asyncio.timeout()
asyncio.wait_for()
```

---

### Buổi 66 — Async Context Manager

```python
async with
```

---

### Buổi 67 — Async Generator

```python
async def generator():
    yield
```

---

### Buổi 68 — Async Iterator

```python
__aiter__
__anext__
```

---

### Buổi 69 — Async Queue

```python
asyncio.Queue
```

---

### Buổi 70 — Async Semaphore

```python
asyncio.Semaphore
```

---

### Buổi 71 — Async Architecture

```text
Event Loop
    ↓
Task
    ↓
Queue
    ↓
Workers
```

---

# PHẦN X — Concurrency Architecture

### Buổi 72 — I/O-bound vs CPU-bound

---

### Buổi 73 — Thread vs AsyncIO

---

### Buổi 74 — AsyncIO vs Multiprocessing

---

### Buổi 75 — Hybrid Concurrency

Thiết kế:

```text
AsyncIO
   ↓
I/O
   ↓
ProcessPool
   ↓
CPU
```

---

### Buổi 76 — Backpressure

```text
Producer
    ↓
Queue
    ↓
Workers
```

Nếu Producer nhanh hơn Worker thì sao?

---

### Buổi 77 — Rate Limiting

---

### Buổi 78 — Retry / Timeout / Cancellation

---

### Buổi 79 — Graceful Shutdown

---

# PHẦN XI — Profiling & Performance

### Buổi 80 — Performance Measurement

```python
timeit
perf_counter
```

---

### Buổi 81 — `cProfile`

---

### Buổi 82 — `pstats`

---

### Buổi 83 — Line Profiler Concept

---

### Buổi 84 — Memory Profiling

```python
tracemalloc
```

---

### Buổi 85 — Benchmarking

* Benchmark function
* Benchmark algorithm
* Benchmark I/O
* Benchmark concurrency

---

### Buổi 86 — Python Optimization

* Algorithm
* Data structure
* Caching
* Lazy evaluation
* Generator
* Batch processing

---

# PHẦN XII — Packaging nâng cao

### Buổi 87 — Python Package Architecture

```text
src/
    package/
        __init__.py
```

---

### Buổi 88 — `pyproject.toml`

---

### Buổi 89 — Build System

```text
Source
 ↓
Build
 ↓
Wheel
 ↓
Install
```

---

### Buổi 90 — Dependencies

* Runtime dependencies
* Development dependencies
* Optional dependencies

---

### Buổi 91 — Versioning

```text
Semantic Versioning
```

---

### Buổi 92 — CLI Package

---

### Buổi 93 — Plugin Package

---

### Buổi 94 — Production Library

Thiết kế một library có:

```text
API
Documentation
Typing
Testing
Logging
Error handling
Packaging
```

---

# PHẦN XIII — Testing chuyên sâu

### Buổi 95 — Testing Architecture

```text
Unit
Integration
System
```

---

### Buổi 96 — pytest nâng cao

* Fixture
* Parametrize
* Marker
* Scope

---

### Buổi 97 — Mock

```python
Mock
MagicMock
patch
```

---

### Buổi 98 — Dependency Injection + Testing

---

### Buổi 99 — Async Testing

---

### Buổi 100 — Concurrency Testing

---

### Buổi 101 — Property-based Testing

---

### Buổi 102 — Test Architecture

```text
Domain
Application
Infrastructure
        ↓
Testing Strategy
```

---

# PHẦN XIV — Design Pattern

Ở đây chúng ta **không học pattern như danh sách thuộc lòng**.

Ta học:

> Problem → Forces → Design → Trade-off → Implementation.

### Buổi 103 — Pattern Foundation

* Creational
* Structural
* Behavioral

---

### Buổi 104 — Singleton

---

### Buổi 105 — Factory

---

### Buổi 106 — Builder

---

### Buổi 107 — Strategy

---

### Buổi 108 — Observer

---

### Buổi 109 — Adapter

---

### Buổi 110 — Decorator

---

### Buổi 111 — Command

---

### Buổi 112 — State

---

### Buổi 113 — Template Method

---

### Buổi 114 — Repository

---

### Buổi 115 — Unit of Work

---

### Buổi 116 — Dependency Injection

---

### Buổi 117 — Pattern Combination

Ví dụ:

```text
Factory
 +
Strategy
 +
Repository
 +
Dependency Injection
```

---

# PHẦN XV — Architecture

### Buổi 118 — Layered Architecture

```text
Presentation
Application
Domain
Infrastructure
```

---

### Buổi 119 — Clean Architecture

---

### Buổi 120 — Hexagonal Architecture

```text
Domain
   ↑
Ports
   ↑
Adapters
```

---

### Buổi 121 — Dependency Rule

---

### Buổi 122 — Dependency Injection

---

### Buổi 123 — Application Service

---

### Buổi 124 — Domain Service

---

### Buổi 125 — Repository Architecture

---

### Buổi 126 — Event-driven Architecture

---

# PHẦN XVI — Framework Design

Đây là phần rất quan trọng nếu mục tiêu của bạn là **tự xây framework Python**.

### Buổi 127 — Framework vs Library

---

### Buổi 128 — Extension Point

---

### Buổi 129 — Hook System

---

### Buổi 130 — Plugin Architecture

---

### Buổi 131 — Registry Pattern

---

### Buổi 132 — Dependency Injection Container

---

### Buổi 133 — Middleware

```text
Request
 ↓
Middleware
 ↓
Middleware
 ↓
Handler
```

---

### Buổi 134 — Event System

---

### Buổi 135 — Command System

---

### Buổi 136 — Configuration System

---

### Buổi 137 — Lifecycle Management

```text
startup
   ↓
running
   ↓
shutdown
```

---

### Buổi 138 — Framework Error Handling

---

### Buổi 139 — Framework Logging

---

### Buổi 140 — Framework Testing

---

# PHẦN XVII — Production Library Engineering

### Buổi 141 — Public API Design

---

### Buổi 142 — Backward Compatibility

---

### Buổi 143 — Error Design

```text
Exception hierarchy
```

---

### Buổi 144 — Logging Architecture

---

### Buổi 145 — Configuration

---

### Buổi 146 — Observability

```text
Logs
Metrics
Tracing
```

---

### Buổi 147 — Documentation

---

### Buổi 148 — API Stability

---

### Buổi 149 — Production Checklist

---

# PHẦN XVIII — FINAL PROJECT

## 🚀 Buổi 150–160 — Production Crawler Framework

Đây sẽ là project tổng hợp toàn bộ Giai đoạn IV.

Kiến trúc dự kiến:

```text
                    CRAWLER FRAMEWORK
                           │
                           ▼
                     Application
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
        Crawler Engine              Scheduler
             │                           │
             ▼                           ▼
          Queue                     Task Manager
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
   Worker Worker Worker
       │     │     │
       └─────┼─────┘
             ▼
         Downloader
             │
             ▼
          Parser
             │
             ▼
        Data Pipeline
             │
       ┌─────┴─────┐
       ▼           ▼
    Storage      Export
```

### Buổi 150 — Project Architecture

### Buổi 151 — Crawler Domain

### Buổi 152 — Request / Response Model

### Buổi 153 — Downloader

### Buổi 154 — ThreadPool Worker

### Buổi 155 — Queue + Producer/Consumer

### Buổi 156 — Retry / Timeout / Rate Limit

### Buổi 157 — Parser Plugin

```text
Parser
 ├── SiteAParser
 ├── SiteBParser
 └── SiteCParser
```

### Buổi 158 — Async Downloader

So sánh:

```text
Thread Downloader
        vs
Async Downloader
```

### Buổi 159 — Monitoring / Metrics

### Buổi 160 — Production Refactoring

Hoàn thiện:

```text
Typing
Testing
Logging
Packaging
Documentation
Architecture
Performance
```

---

# 🧭 Tổng quan toàn bộ Giai đoạn IV

```text
GIAI ĐOẠN IV — PYTHON ADVANCED
│
├── I. Python Runtime
│   ├── Object Model
│   ├── Memory
│   ├── Reference Counting
│   ├── GC
│   └── Copy
│
├── II. Descriptor
│   ├── Attribute Lookup
│   ├── Descriptor
│   ├── property
│   └── Validation
│
├── III. Reflection
│   ├── Introspection
│   ├── inspect
│   ├── Reflection
│   └── Dynamic Import
│
├── IV. Metaclass
│   ├── type
│   ├── Metaclass
│   ├── __new__
│   ├── __prepare__
│   └── Registry
│
├── V. Advanced Typing
│   ├── ABC
│   ├── Protocol
│   ├── Generic
│   ├── ParamSpec
│   └── TypeVarTuple
│
├── VI. Bytecode
│   ├── AST
│   ├── Bytecode
│   ├── dis
│   └── Code Object
│
├── VII. Threading
│   ├── Thread
│   ├── Lock
│   ├── Queue
│   └── ThreadPool
│
├── VIII. Multiprocessing
│   ├── Process
│   ├── ProcessPool
│   └── IPC
│
├── IX. AsyncIO
│   ├── Coroutine
│   ├── Event Loop
│   ├── Task
│   ├── Async Generator
│   └── Async Context Manager
│
├── X. Concurrency Architecture
│   ├── Thread vs Async
│   ├── Process
│   ├── Backpressure
│   ├── Rate Limit
│   └── Graceful Shutdown
│
├── XI. Performance
│   ├── Profiling
│   ├── cProfile
│   ├── tracemalloc
│   └── Benchmark
│
├── XII. Packaging
│   ├── pyproject.toml
│   ├── Wheel
│   ├── Dependencies
│   └── Production Library
│
├── XIII. Testing
│   ├── pytest
│   ├── Mock
│   ├── Async Testing
│   └── Property Testing
│
├── XIV. Design Pattern
│
├── XV. Architecture
│
├── XVI. Framework Design
│
├── XVII. Production Library
│
└── XVIII. FINAL PROJECT
        │
        └── Production Crawler Framework
```

## Một thay đổi quan trọng trong cách học

Ở **Giai đoạn III — OOP Master**, trọng tâm là:

```text
Class
Object
Inheritance
Composition
Polymorphism
Encapsulation
```

Sang **Giai đoạn IV**, chúng ta chuyển sang:

```text
Python Runtime
      ↓
Object Model
      ↓
Memory
      ↓
Descriptor
      ↓
Metaclass
      ↓
Typing
      ↓
Concurrency
      ↓
Performance
      ↓
Packaging
      ↓
Testing
      ↓
Design Pattern
      ↓
Architecture
      ↓
Framework
      ↓
Production
```

Vì vậy mình đề xuất **không nhảy ngay vào AsyncIO**. Phần Memory → Descriptor → Metaclass sẽ giúp bạn hiểu sâu Python trước; sau đó Thread/Process/AsyncIO sẽ dễ hơn rất nhiều.

**Tổng cộng: 160 buổi**, và cuối cùng chúng ta sẽ có một project đủ lớn để liên kết gần như toàn bộ kiến thức Advanced Python thành một hệ thống thực tế.

Nếu tiếp tục theo roadmap này, **Buổi 1 của Giai đoạn IV sẽ là: *Python Object Model — Python thực sự quản lý Object như thế nào?***
