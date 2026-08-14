# Dataclass Deep Dive — Buổi 23

# Serialization với YAML, TOML và XML

Hôm nay chúng ta tiếp tục **Phần III — Serialization**.

Sau Buổi 21–22:

```text
Dataclass
   ↓
asdict()
   ↓
dict
   ↓
JSON
```

Hôm nay mở rộng:

```text
                    Dataclass
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
         JSON          YAML          TOML
                                      │
                                      ▼
                                     XML
```

Mục tiêu không phải học cú pháp YAML/TOML/XML đơn thuần, mà phải hiểu:

> **Dataclass nên được serialize sang format nào, trong trường hợp nào, và kiến trúc serializer nên thiết kế ra sao.**

---

# 1. Serialization không chỉ có JSON

Trong project thực tế, bạn sẽ gặp:

| Format      | Thường dùng cho                   |
| ----------- | --------------------------------- |
| JSON        | API, queue, web                   |
| YAML        | config, human-readable document   |
| TOML        | configuration                     |
| XML         | legacy API, document, integration |
| Pickle      | Python object persistence         |
| MessagePack | binary protocol                   |
| Protobuf    | distributed systems               |

Dataclass có thể đóng vai trò:

```text
Domain object
      ↓
DTO
      ↓
Serialization boundary
      ↓
Format
```

---

# 2. Dataclass → YAML

Python không có YAML trong standard library.

Một thư viện phổ biến:

```python
import yaml
```

thường đến từ:

```text
PyYAML
```

Cài:

```bash
pip install pyyaml
```

---

# 3. YAML cơ bản

Ví dụ:

```python
data = {
    "id": 1,
    "name": "Alice",
    "age": 20,
}
```

Serialize:

```python
import yaml

text = yaml.safe_dump(
    data,
    allow_unicode=True,
)
```

Kết quả:

```yaml
age: 20
id: 1
name: Alice
```

---

# 4. Dataclass không nên đưa thẳng vào YAML

Ví dụ:

```python
@dataclass
class User:
    id: int
    name: str
```

Không nên mặc định:

```python
yaml.safe_dump(user)
```

Thay vào đó:

```python
yaml.safe_dump(
    asdict(user),
    allow_unicode=True,
)
```

Pipeline:

```text
Dataclass
   ↓
asdict()
   ↓
dict
   ↓
YAML
```

---

# 5. YAML rất phù hợp với Configuration

Ví dụ project crawler:

```yaml
crawler:
  workers: 10
  timeout: 30
  retry: 3

database:
  path: data.db

logging:
  level: INFO
```

Ta có Dataclass:

```python
@dataclass
class CrawlerConfig:
    workers: int
    timeout: int
    retry: int


@dataclass
class DatabaseConfig:
    path: str


@dataclass
class AppConfig:
    crawler: CrawlerConfig
    database: DatabaseConfig
```

Đây là một use case rất tự nhiên.

---

# 6. YAML → Dataclass

Chiều ngược lại:

```python
data = yaml.safe_load(text)
```

Ta nhận:

```python
{
    "crawler": {
        "workers": 10,
        "timeout": 30,
        "retry": 3,
    },
    "database": {
        "path": "data.db",
    },
}
```

Sau đó:

```python
config = AppConfig(
    crawler=CrawlerConfig(
        **data["crawler"]
    ),
    database=DatabaseConfig(
        **data["database"]
    ),
)
```

Pipeline:

```text
YAML
 ↓
dict
 ↓
Dataclass
```

---

# 7. YAML không tự động tạo Dataclass

Đây là misconception quan trọng.

```python
yaml.safe_load(...)
```

thường cho:

```text
dict
list
str
int
float
bool
None
```

Nó không biết:

```text
dict
 ↓
AppConfig
```

trừ khi bạn xây thêm mapping layer.

---

# 8. Configuration Loader

Ta có thể tạo:

```python
def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return AppConfig(
        crawler=CrawlerConfig(
            **data["crawler"]
        ),
        database=DatabaseConfig(
            **data["database"]
        ),
    )
```

Sau đó:

```python
config = load_config(
    "config.yaml"
)
```

Kết quả:

```text
config
   ↓
AppConfig
```

Đây chính là pattern **Configuration Object** mà chúng ta sẽ gặp lại ở Buổi 29.

---

# 9. YAML và Security

Một điểm cực kỳ quan trọng:

> Không nên sử dụng `yaml.load()` một cách tùy tiện với dữ liệu không tin cậy.

Ưu tiên:

```python
yaml.safe_load(...)
```

và:

```python
yaml.safe_dump(...)
```

Đặc biệt với:

```text
Internet
crawler
uploaded file
user input
plugin
```

hãy coi YAML là **untrusted input** nếu nguồn không đáng tin.

---

# 10. YAML có ưu điểm gì?

YAML:

```text
+ human readable
+ nested structure
+ configuration friendly
+ comments
+ Unicode tốt
```

Ví dụ:

```yaml
crawler:
  workers: 10  # số worker

  timeout: 30
```

JSON cũng biểu diễn được cấu trúc này, nhưng YAML thường dễ đọc hơn cho config.

---

# 11. YAML có nhược điểm gì?

YAML có:

```text
- nhiều syntax
- implicit typing
- parser phức tạp hơn JSON
- dễ gây nhầm indentation
```

Ví dụ:

```yaml
enabled: yes
```

có thể có semantics khác nhau tùy YAML implementation/version/schema.

Do đó với config quan trọng:

> Đừng nghĩ YAML luôn "đơn giản hơn JSON".

---

# 12. TOML

TOML đặc biệt phù hợp với:

```text
Configuration
```

Python hiện đại đã có parser TOML trong standard library:

```python
import tomllib
```

cho đọc TOML.

Ví dụ:

```toml
[crawler]
workers = 10
timeout = 30
retry = 3

[database]
path = "data.db"
```

---

# 13. TOML → Dict

```python
import tomllib

with open(
    "config.toml",
    "rb",
) as f:
    data = tomllib.load(f)
```

Kết quả:

```python
{
    "crawler": {
        "workers": 10,
        "timeout": 30,
        "retry": 3,
    },
    "database": {
        "path": "data.db",
    },
}
```

Sau đó:

```python
config = AppConfig(
    crawler=CrawlerConfig(
        **data["crawler"]
    ),
    database=DatabaseConfig(
        **data["database"]
    ),
)
```

---

# 14. TOML và Dataclass

Pipeline:

```text
TOML
 ↓
tomllib
 ↓
dict
 ↓
Dataclass
```

Ngược lại:

```text
Dataclass
 ↓
asdict()
 ↓
TOML serializer
 ↓
TOML
```

Điểm quan trọng:

> Python standard library có `tomllib` để đọc TOML, nhưng không cung cấp writer tương ứng trong `tomllib`.

Nếu cần ghi TOML, bạn thường dùng thư viện bên ngoài như `tomli-w`.

---

# 15. TOML vs YAML

Ví dụ cùng một config.

### YAML

```yaml
crawler:
  workers: 10
  timeout: 30

database:
  path: data.db
```

### TOML

```toml
[crawler]
workers = 10
timeout = 30

[database]
path = "data.db"
```

Cả hai đều dễ đọc.

Nhưng TOML có mục tiêu rất rõ:

> Configuration file.

---

# 16. TOML rất hợp với Python project

Ví dụ:

```text
pyproject.toml
```

Bạn đã gặp:

```toml
[project]
name = "my-app"
version = "1.0.0"
```

TOML đặc biệt phổ biến trong Python packaging hiện đại.

---

# 17. Khi nào dùng YAML?

Ví dụ:

```text
config.yaml
```

phù hợp với:

```text
complex configuration
deployment
CI/CD
Docker-related configuration
human-authored documents
```

---

# 18. Khi nào dùng TOML?

Phù hợp với:

```text
application configuration
Python package metadata
simple structured configuration
```

Ví dụ:

```text
pyproject.toml
app.toml
crawler.toml
```

---

# 19. XML

Bây giờ tới XML.

XML có cấu trúc:

```xml
<user>
    <id>1</id>
    <name>Alice</name>
</user>
```

Python có standard library:

```python
import xml.etree.ElementTree as ET
```

---

# 20. Dataclass → XML

Không có:

```python
xml.dumps(user)
```

built-in.

Ta phải thiết kế mapping:

```text
Dataclass
   ↓
ElementTree
   ↓
XML
```

Ví dụ:

```python
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class User:
    id: int
    name: str
```

Tạo:

```python
user = User(
    1,
    "Alice",
)
```

XML:

```python
root = ET.Element("user")

id_element = ET.SubElement(
    root,
    "id",
)

id_element.text = str(user.id)

name_element = ET.SubElement(
    root,
    "name",
)

name_element.text = user.name
```

Sau đó:

```python
xml_bytes = ET.tostring(
    root,
    encoding="utf-8",
)
```

---

# 21. Kết quả

```xml
<user>
    <id>1</id>
    <name>Alice</name>
</user>
```

Bạn có thể thấy XML cần mapping rõ ràng hơn JSON/YAML.

---

# 22. Tại sao XML khó hơn?

JSON:

```json
{
  "id": 1,
  "name": "Alice"
}
```

XML:

```xml
<user>
    <id>1</id>
    <name>Alice</name>
</user>
```

Nhưng XML còn có:

```xml
<user id="1">
    <name>Alice</name>
</user>
```

Hai biểu diễn này đều hợp lý.

Do đó phải quyết định:

```text
field
 ↓
element?
attribute?
text?
CDATA?
```

Đây là **serialization policy**.

---

# 23. XML có Attribute

Ví dụ:

```xml
<user id="1">
    <name>Alice</name>
</user>
```

Mapping:

```text
User.id
    ↓
XML attribute

User.name
    ↓
XML element
```

Dataclass không tự biết policy này.

Ta có thể dùng metadata:

```python
@dataclass
class User:
    id: int = field(
        metadata={
            "xml_attribute": True
        }
    )

    name: str
```

Đây là một ví dụ rất hay về việc sử dụng `field(metadata=...)`.

---

# 24. Metadata trở thành Serialization Schema

Ta đã học:

```python
field(
    metadata={
        ...
    }
)
```

Có thể dùng:

```python
@dataclass
class User:

    id: int = field(
        metadata={
            "json_name": "userId",
            "xml_attribute": True,
        }
    )

    name: str = field(
        metadata={
            "json_name": "userName",
        }
    )
```

Bây giờ metadata chứa:

```text
Serialization policy
```

Đây chính là nền tảng của một serialization framework.

---

# 25. Một Universal Serializer

Ta có thể hình dung:

```text
                    Dataclass
                        │
                        ▼
                      Field
                        │
                     metadata
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
         JSON          YAML          XML
          │             │             │
     json_name      yaml_name     xml_attribute
```

Một model có thể phục vụ nhiều boundary.

---

# 26. Nhưng có nên làm vậy?

Không phải lúc nào.

Nếu metadata bắt đầu:

```python
metadata={
    "json_name": ...,
    "yaml_name": ...,
    "xml_name": ...,
    "xml_attribute": ...,
    "db_column": ...,
    "graphql_name": ...,
}
```

thì class bắt đầu chứa quá nhiều infrastructure concern.

Đây là:

> **Metadata coupling.**

Có thể tốt trong framework nhỏ, nhưng trong hệ thống lớn cần cân nhắc.

---

# 27. Một kiến trúc khác

Thay vì:

```text
Dataclass
 ↓
metadata
 ↓
JSON
```

có thể:

```text
Domain Dataclass
      ↓
Serializer Schema
      ↓
JSON
```

Ví dụ:

```text
User
 ↓
UserJsonSchema
 ↓
JSON
```

Điều này tách domain khỏi infrastructure.

---

# 28. Đây chính là Clean Architecture

Ví dụ:

```text
Domain
└── User

Infrastructure
├── JsonSerializer
├── YamlSerializer
├── XmlSerializer
└── TomlSerializer
```

Domain không cần biết:

```text
JSON
YAML
XML
```

Đây là thiết kế tốt nếu model là domain entity.

---

# 29. DTO thì khác

Nếu là DTO:

```python
@dataclass
class UserResponse:
    id: int
    name: str
```

thì việc DTO gắn với serialization format có thể chấp nhận được hơn.

Vì:

```text
DTO
 ↓
Boundary
```

Trong khi:

```text
Entity
 ↓
Domain
```

nên độc lập hơn.

---

# 30. Dataclass → YAML

Một helper:

```python
from dataclasses import asdict
import yaml


def to_yaml(obj) -> str:
    return yaml.safe_dump(
        asdict(obj),
        allow_unicode=True,
        sort_keys=False,
    )
```

Sử dụng:

```python
text = to_yaml(user)
```

---

# 31. Dataclass → TOML

Không có built-in writer trong `tomllib`.

Một thư viện writer có thể nhận:

```python
data = asdict(user)
```

sau đó:

```text
dict
 ↓
TOML writer
 ↓
TOML
```

Điểm quan trọng:

> `tomllib` là parser, không phải full read/write TOML package.

---

# 32. Dataclass → XML

Có thể xây generic function:

```python
from dataclasses import fields
import xml.etree.ElementTree as ET


def dataclass_to_xml(obj, root_name=None):
    root_name = (
        root_name
        or obj.__class__.__name__.lower()
    )

    root = ET.Element(root_name)

    for f in fields(obj):
        value = getattr(obj, f.name)

        child = ET.SubElement(
            root,
            f.name,
        )

        child.text = str(value)

    return root
```

Sau đó:

```python
root = dataclass_to_xml(user)

xml = ET.tostring(
    root,
    encoding="unicode",
)
```

---

# 33. Nhưng generic XML serializer này chưa đủ

Nếu:

```python
@dataclass
class User:
    address: Address
```

thì:

```python
child.text = str(value)
```

sẽ cho representation không mong muốn.

Ta cần recursive:

```text
dataclass
   ↓
field
   ├── primitive → text
   ├── dataclass → element
   ├── list → repeated elements
   └── None → policy
```

---

# 34. XML List

Ví dụ:

```python
@dataclass
class User:
    name: str
    tags: list[str]
```

Bạn có thể muốn:

```xml
<user>
    <name>Alice</name>

    <tags>
        <tag>python</tag>
        <tag>dataclass</tag>
    </tags>
</user>
```

hoặc:

```xml
<user>
    <name>Alice</name>
    <tag>python</tag>
    <tag>dataclass</tag>
</user>
```

Cả hai đều hợp lý.

Serializer phải có policy.

---

# 35. Đây là vấn đề chung của Serialization

Không chỉ XML.

Ngay cả JSON cũng có:

```python
@dataclass
class User:
    first_name: str
```

API muốn:

```json
{
    "firstName": "Alice"
}
```

Trong Python:

```python
first_name
```

Do đó:

```text
Python naming
      ↓
Serialization naming
```

cần một policy.

---

# 36. Naming Strategy

Một serializer có thể có:

```python
def snake_to_camel(name):
    ...
```

Ví dụ:

```text
first_name
     ↓
firstName
```

Sau đó:

```python
serialize(
    user,
    naming=snake_to_camel,
)
```

Đây là design rất hữu ích cho REST API.

---

# 37. YAML/TOML thường giữ tên field

Đối với config:

```python
@dataclass
class DatabaseConfig:
    connection_timeout: int
```

thường muốn:

```yaml
connection_timeout: 30
```

chứ không nhất thiết:

```yaml
connectionTimeout: 30
```

Do đó naming policy có thể phụ thuộc boundary.

---

# 38. Serialization Strategy Pattern

Ta có thể thiết kế:

```python
class Serializer:
    def serialize(self, obj):
        raise NotImplementedError
```

Các implementation:

```text
JsonSerializer
YamlSerializer
TomlSerializer
XmlSerializer
```

Sau đó:

```python
serializer = JsonSerializer()

serializer.serialize(user)
```

hoặc:

```python
serializer = YamlSerializer()

serializer.serialize(config)
```

---

# 39. Interface

Ví dụ:

```python
from abc import ABC, abstractmethod


class Serializer(ABC):

    @abstractmethod
    def serialize(self, obj):
        ...
```

JSON:

```python
class JsonSerializer(Serializer):

    def serialize(self, obj):
        ...
```

YAML:

```python
class YamlSerializer(Serializer):

    def serialize(self, obj):
        ...
```

Đây là một ứng dụng trực tiếp của:

```text
Strategy Pattern
```

---

# 40. Serialization Registry

Có thể có:

```python
SERIALIZERS = {
    "json": JsonSerializer,
    "yaml": YamlSerializer,
    "toml": TomlSerializer,
    "xml": XmlSerializer,
}
```

Sau đó:

```python
serializer = SERIALIZERS[
    "json"
]()
```

Đây cũng chính là tư duy **Plugin Architecture**.

---

# 41. Crawler Framework

Trong crawler của bạn:

```text
CrawlerTask
     ↓
Serializer
     │
     ├── JSON → Queue
     ├── YAML → Debug/config
     ├── SQLite → Repository
     └── XML → External source
```

Không nên để crawler code biết chi tiết:

```python
json.dumps(...)
yaml.safe_dump(...)
ET.tostring(...)
```

ở mọi nơi.

Nên có boundary rõ:

```text
Crawler
  ↓
DTO
  ↓
Serializer
```

---

# 42. JSON vs YAML vs TOML vs XML

| Đặc điểm           |  JSON |  YAML | TOML | XML |
| ------------------ | ----: | ----: | ---: | --: |
| API                |   ⭐⭐⭐ |     ⭐ |    ⭐ | ⭐⭐⭐ |
| Config             |    ⭐⭐ |   ⭐⭐⭐ |  ⭐⭐⭐ |   ⭐ |
| Human-readable     |    ⭐⭐ |   ⭐⭐⭐ |  ⭐⭐⭐ |  ⭐⭐ |
| Comments           | Không |    Có |   Có |  Có |
| Schema flexibility |   Cao |   Cao |  Vừa | Cao |
| Verbose            |  Thấp |  Thấp | Thấp | Cao |
| Python stdlib read |    Có | Không |   Có |  Có |
| Nested data        |   Tốt |   Tốt |  Tốt | Tốt |
| Legacy integration |     ⭐ |     ⭐ |    ⭐ | ⭐⭐⭐ |

---

# 43. Chọn format thế nào?

### REST API

```text
JSON
```

### Queue

```text
JSON
hoặc binary protocol
```

### Application config

```text
TOML / YAML
```

### Python package metadata

```text
TOML
```

### Legacy enterprise API

```text
XML
```

### Human-authored complex configuration

```text
YAML
```

---

# 44. Không nên dùng XML chỉ vì "nó serialize được"

XML có overhead lớn hơn:

```text
verbose
parsing
schema complexity
namespaces
attributes
```

Nếu API của bạn kiểm soát cả hai đầu và không có requirement XML:

```text
JSON
```

thường đơn giản hơn.

---

# 45. Dataclass Serialization Layer

Một architecture sạch:

```text
                   Domain
                     │
                     ▼
                Dataclass
                     │
                     ▼
                    DTO
                     │
                     ▼
              Serialization
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
     JSON           YAML          XML
       │             │             │
       ▼             ▼             ▼
     REST          Config       External
```

Đây là mental model nên giữ.

---

# 46. Bài tập 1 — YAML Config

Tạo:

```python
@dataclass
class CrawlerConfig:
    workers: int
    timeout: int
    retry: int


@dataclass
class DatabaseConfig:
    path: str


@dataclass
class AppConfig:
    crawler: CrawlerConfig
    database: DatabaseConfig
```

Serialize thành:

```yaml
crawler:
  workers: 10
  timeout: 30
  retry: 3

database:
  path: "crawler.db"
```

Sau đó deserialize trở lại `AppConfig`.

---

# 47. Bài tập 2 — TOML

Tạo:

```python
@dataclass
class AppConfig:
    name: str
    version: str
    workers: int
```

Tạo TOML:

```toml
name = "crawler"
version = "1.0.0"
workers = 10
```

Đọc bằng:

```python
tomllib.load(...)
```

và tạo:

```python
AppConfig(**data)
```

---

# 48. Bài tập 3 — XML

Tạo:

```python
@dataclass
class User:
    id: int
    name: str
```

Sinh:

```xml
<user>
    <id>1</id>
    <name>Alice</name>
</user>
```

Sau đó viết chiều ngược:

```text
XML
 ↓
ElementTree
 ↓
dict
 ↓
User
```

---

# 49. Bài tập 4 — Nested XML

Tạo:

```python
@dataclass
class Address:
    city: str
    country: str


@dataclass
class User:
    id: int
    name: str
    address: Address
```

Sinh:

```xml
<user>
    <id>1</id>
    <name>Alice</name>
    <address>
        <city>Ho Chi Minh</city>
        <country>Vietnam</country>
    </address>
</user>
```

---

# 50. Bài tập 5 — Serializer Interface

Thiết kế:

```python
class Serializer(ABC):

    @abstractmethod
    def serialize(self, obj):
        ...


    @abstractmethod
    def deserialize(self, data, cls):
        ...
```

Implement:

```text
JsonSerializer
YamlSerializer
TomlSerializer
XmlSerializer
```

Mục tiêu:

```python
serializer = JsonSerializer()

data = serializer.serialize(user)

user2 = serializer.deserialize(
    data,
    User,
)
```

---

# 51. Bài tập 6 — Crawler

Thiết kế:

```python
@dataclass
class DownloadTask:
    id: int
    url: str
    chapter_id: int
```

Viết:

```text
JsonTaskSerializer
```

và tạo:

```text
DownloadTask
      ↓
JSON
      ↓
Queue
      ↓
JSON
      ↓
DownloadTask
```

Đây là bài tập cực kỳ gần với queue/crawler framework bạn đang xây dựng.

---

# 52. Tổng kết Buổi 23

Hôm nay bạn cần hiểu rằng:

```text
Serialization
≠
asdict()
```

`asdict()` chỉ là:

```text
Dataclass
 ↓
Python data structure
```

Sau đó mới:

```text
Python structure
 ↓
JSON/YAML/TOML/XML
```

---

## Mental Model cuối buổi

```text
                     Dataclass
                         │
                         ▼
                     DTO / Model
                         │
                         ▼
                  Serialization Layer
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
       JSON             YAML             TOML
        │                │                │
        ▼                ▼                ▼
      REST            Config           Config


                     Dataclass
                         │
                         ▼
                        XML
                         │
                         ▼
                Legacy / External API
```

Và kiến thức quan trọng nhất:

> **Format chỉ là phần cuối của serialization pipeline.**

Phần khó thực sự là thiết kế:

```text
Object
 ↓
Field discovery
 ↓
Naming
 ↓
Nested object
 ↓
Optional
 ↓
Collection
 ↓
Special types
 ↓
Metadata
 ↓
Format
```

Đó chính là nền tảng để chúng ta xây **serializer framework mini** ở các buổi sau.

---

# Tiếp theo — Buổi 24

**Pickle + `copy` + `deepcopy` với Dataclass**

Chúng ta sẽ phân biệt rất sâu:

```text
asdict()
copy.copy()
copy.deepcopy()
pickle.dumps()
```

đặc biệt:

```text
Dataclass
   ↓
copy
   ↓
identity
   ↓
shallow copy
   ↓
deep copy
   ↓
pickle
   ↓
restore object graph
```

và một vấn đề cực kỳ quan trọng:

> **Tại sao `pickle` không nên được dùng như một format trao đổi dữ liệu giữa các hệ thống không tin cậy.**
    