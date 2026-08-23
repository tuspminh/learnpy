# Buổi 17 — Thiết kế CLI theo SOLID + Clean Architecture

Hôm nay chúng ta bắt đầu **xây một project thật**, không còn chỉ nói lý thuyết.

Mục tiêu:

```text
CLI
 ↓
Application / Use Case
 ↓
Domain
 ↓
Repository Interface
 ↓
SQLite Repository
```

Điểm quan trọng nhất:

> **CLI chỉ là nơi nhận input/output. Business logic không được nằm trong CLI.**

---

# 1. Bài toán

Chúng ta xây một CLI quản lý `Story`.

CLI cần hỗ trợ:

```bash
novel story create "Harry Potter"
novel story get 1
novel story rename 1 "Harry Potter - Updated"
novel story publish 1
novel story delete 1
```

Architecture:

```text
                    CLI
                     │
                     ↓
              Application
                     │
                     ↓
                  Domain
                     │
                     ↓
             Repository Protocol
                     ↑
                     │
             SQLite Repository
```

---

# 2. Tại sao không viết CLI kiểu này?

Ví dụ rất dễ viết:

```python
@app.command()
def create(title: str):

    connection = sqlite3.connect("stories.db")

    cursor = connection.execute(
        "INSERT INTO stories(title) VALUES (?)",
        (title,),
    )

    connection.commit()

    print("Created")
```

Code chạy.

Nhưng architecture rất tệ.

CLI đang biết:

```text
SQLite
SQL
Database connection
Persistence
Business behavior
Presentation
```

---

# 3. Phân tích SOLID

Đoạn trên vi phạm:

### SRP

CLI command làm quá nhiều việc.

### DIP

CLI phụ thuộc trực tiếp SQLite.

### OCP

Đổi database phải sửa CLI.

### Testing

Muốn test command phải dựng database.

---

# 4. Architecture mục tiêu

Ta muốn:

```text
src/
└── novel/
    │
    ├── domain/
    │
    ├── application/
    │
    ├── infrastructure/
    │
    ├── presentation/
    │
    └── composition.py
```

Chi tiết:

```text
src/novel/
│
├── domain/
│   └── story.py
│
├── application/
│   └── story_service.py
│
├── infrastructure/
│   └── sqlite_story_repository.py
│
├── presentation/
│   └── cli.py
│
└── composition.py
```

Đây là version đơn giản trước.

Sau đó chúng ta có thể mở rộng thành package lớn hơn.

---

# 5. Domain trước

Đừng bắt đầu bằng CLI.

Hãy bắt đầu bằng business.

```python
# domain/story.py

from dataclasses import dataclass


@dataclass
class Story:

    id: int | None
    title: str
    published: bool = False

    def rename(self, title: str) -> None:

        title = title.strip()

        if not title:
            raise ValueError(
                "Story title cannot be empty"
            )

        self.title = title

    def publish(self) -> None:

        if not self.title.strip():
            raise ValueError(
                "Cannot publish story without title"
            )

        if self.published:
            raise ValueError(
                "Story is already published"
            )

        self.published = True
```

---

# 6. Tại sao `Story` không có SQLite?

Không viết:

```python
class Story:

    def save(self):
        sqlite3.connect(...)
```

Vì `Story` không phải database object.

`Story` đại diện cho:

```text
Business Concept
```

SQLite là:

```text
Infrastructure Detail
```

---

# 7. Business behavior nằm trong Entity

Ta có:

```python
story.rename("New title")
```

và:

```python
story.publish()
```

Thay vì:

```python
if not title:
    ...
```

rải rác khắp application.

Domain tự bảo vệ invariant.

---

# 8. Repository Interface

Bây giờ cần persistence abstraction.

```python
# domain/story_repository.py

from typing import Protocol

from .story import Story


class StoryRepository(Protocol):

    def create(self, story: Story) -> Story:
        ...

    def get_by_id(
        self,
        story_id: int,
    ) -> Story | None:
        ...

    def save(self, story: Story) -> None:
        ...

    def delete(self, story_id: int) -> None:
        ...
```

Đây là **Port**.

---

# 9. Vì sao dùng `Protocol`?

Python có duck typing.

Ta chỉ cần:

```python
class SQLiteStoryRepository:

    def get_by_id(...):
        ...

    def save(...):
        ...
```

Nếu phù hợp contract:

```text
SQLiteStoryRepository
        ↓
satisfies
        ↓
StoryRepository
```

Không cần:

```python
class SQLiteStoryRepository(StoryRepository):
```

---

# 10. Đây là ISP

Repository interface nhỏ:

```text
create
get_by_id
save
delete
```

Không nhét:

```text
crawl
parse
download
notify
login
export
```

vào cùng một interface.

Nếu application chỉ cần đọc:

```python
class StoryReader(Protocol):

    def get_by_id(
        self,
        story_id: int,
    ) -> Story | None:
        ...
```

thì càng tốt.

---

# 11. Application Layer

Bây giờ tạo Use Case.

Thay vì một class khổng lồ:

```text
StoryManager
```

ta có từng use case.

Ví dụ:

```text
CreateStory
GetStory
RenameStory
PublishStory
DeleteStory
```

---

# 12. CreateStory

```python
# application/create_story.py

from domain.story import Story
from domain.story_repository import StoryRepository


class CreateStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def execute(
        self,
        title: str,
    ) -> Story:

        story = Story(
            id=None,
            title=title,
        )

        return self.repository.create(story)
```

---

# 13. GetStory

```python
# application/get_story.py

from domain.story_repository import StoryRepository


class GetStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def execute(
        self,
        story_id: int,
    ):
        return self.repository.get_by_id(
            story_id
        )
```

---

# 14. RenameStory

```python
# application/rename_story.py

from domain.story_repository import StoryRepository


class RenameStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def execute(
        self,
        story_id: int,
        title: str,
    ):

        story = self.repository.get_by_id(
            story_id
        )

        if story is None:
            raise ValueError(
                "Story not found"
            )

        story.rename(title)

        self.repository.save(story)

        return story
```

---

# 15. PublishStory

```python
# application/publish_story.py

from domain.story_repository import StoryRepository


class PublishStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def execute(
        self,
        story_id: int,
    ):

        story = self.repository.get_by_id(
            story_id
        )

        if story is None:
            raise ValueError(
                "Story not found"
            )

        story.publish()

        self.repository.save(story)

        return story
```

---

# 16. Một điểm rất quan trọng

Application không làm:

```python
if story.published:
    ...
```

Business rule:

```text
Story không publish 2 lần
```

thuộc Entity.

Do đó:

```python
story.publish()
```

là đúng.

Application chỉ orchestration:

```text
load
 ↓
call domain behavior
 ↓
save
```

---

# 17. DeleteStory

```python
# application/delete_story.py

from domain.story_repository import StoryRepository


class DeleteStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def execute(
        self,
        story_id: int,
    ) -> None:

        story = self.repository.get_by_id(
            story_id
        )

        if story is None:
            raise ValueError(
                "Story not found"
            )

        self.repository.delete(
            story_id
        )
```

---

# 18. Infrastructure — SQLite

Bây giờ mới đến SQLite.

```python
# infrastructure/sqlite_story_repository.py

import sqlite3

from domain.story import Story


class SQLiteStoryRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection
```

Nó biết SQLite.

Đây là điều bình thường.

---

# 19. Initialize database

```python
class SQLiteStoryRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection

    def initialize(self):

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                published INTEGER NOT NULL
            )
            """
        )

        self.connection.commit()
```

Đây là Infrastructure.

---

# 20. Create

```python
def create(self, story: Story) -> Story:

    cursor = self.connection.execute(
        """
        INSERT INTO stories (
            title,
            published
        )
        VALUES (?, ?)
        """,
        (
            story.title,
            int(story.published),
        ),
    )

    self.connection.commit()

    return Story(
        id=cursor.lastrowid,
        title=story.title,
        published=story.published,
    )
```

---

# 21. Get

```python
def get_by_id(
    self,
    story_id: int,
) -> Story | None:

    cursor = self.connection.execute(
        """
        SELECT
            id,
            title,
            published
        FROM stories
        WHERE id = ?
        """,
        (story_id,),
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return Story(
        id=row[0],
        title=row[1],
        published=bool(row[2]),
    )
```

---

# 22. Save

```python
def save(self, story: Story) -> None:

    self.connection.execute(
        """
        UPDATE stories
        SET
            title = ?,
            published = ?
        WHERE id = ?
        """,
        (
            story.title,
            int(story.published),
            story.id,
        ),
    )

    self.connection.commit()
```

---

# 23. Delete

```python
def delete(
    self,
    story_id: int,
) -> None:

    self.connection.execute(
        """
        DELETE FROM stories
        WHERE id = ?
        """,
        (story_id,),
    )

    self.connection.commit()
```

---

# 24. Đến đây architecture đã tách

```text
Domain
  │
  │ Story
  │ StoryRepository
  │
  ↓
Application
  │
  │ CreateStory
  │ RenameStory
  │ PublishStory
  │ DeleteStory
  │
  ↓
Infrastructure
  │
  └── SQLiteStoryRepository
```

Nhưng còn một vấn đề:

> Ai tạo `SQLiteStoryRepository`?

---

# 25. Composition Root

Đây là nhiệm vụ của:

```text
composition.py
```

```python
# composition.py

import sqlite3

from application.create_story import CreateStory
from application.get_story import GetStory
from application.rename_story import RenameStory
from application.publish_story import PublishStory
from application.delete_story import DeleteStory

from infrastructure.sqlite_story_repository import (
    SQLiteStoryRepository,
)
```

---

# 26. Build Application

```python
def build_application():

    connection = sqlite3.connect(
        "stories.db"
    )

    repository = SQLiteStoryRepository(
        connection
    )

    repository.initialize()

    return {
        "create_story": CreateStory(repository),
        "get_story": GetStory(repository),
        "rename_story": RenameStory(repository),
        "publish_story": PublishStory(repository),
        "delete_story": DeleteStory(repository),
    }
```

Đây chính là **Composition Root**.

---

# 27. CLI

Bây giờ CLI cực kỳ mỏng.

Ta dùng Typer.

```python
# presentation/cli.py

import typer

from composition import build_application


app = typer.Typer()

story_app = typer.Typer()

app.add_typer(
    story_app,
    name="story",
)
```

---

# 28. Create command

```python
@story_app.command()
def create(title: str):

    services = build_application()

    story = services[
        "create_story"
    ].execute(title)

    typer.echo(
        f"Created story #{story.id}"
    )
```

CLI chỉ:

```text
input
 ↓
use case
 ↓
output
```

---

# 29. Get command

```python
@story_app.command()
def get(story_id: int):

    services = build_application()

    story = services[
        "get_story"
    ].execute(story_id)

    if story is None:
        typer.echo(
            "Story not found"
        )
        raise typer.Exit(1)

    typer.echo(
        f"#{story.id} "
        f"{story.title} "
        f"published={story.published}"
    )
```

---

# 30. Rename command

```python
@story_app.command()
def rename(
    story_id: int,
    title: str,
):

    services = build_application()

    story = services[
        "rename_story"
    ].execute(
        story_id,
        title,
    )

    typer.echo(
        f"Renamed story #{story.id}"
    )
```

---

# 31. Publish command

```python
@story_app.command()
def publish(story_id: int):

    services = build_application()

    story = services[
        "publish_story"
    ].execute(story_id)

    typer.echo(
        f"Published story #{story.id}"
    )
```

---

# 32. Delete command

```python
@story_app.command()
def delete(story_id: int):

    services = build_application()

    services[
        "delete_story"
    ].execute(story_id)

    typer.echo(
        f"Deleted story #{story_id}"
    )
```

Cuối file:

```python
if __name__ == "__main__":
    app()
```

---

# 33. CLI bây giờ làm rất ít

Ví dụ:

```bash
novel story publish 1
```

Luồng:

```text
Typer
  ↓
publish()
  ↓
PublishStory.execute()
  ↓
StoryRepository.get_by_id()
  ↓
Story.publish()
  ↓
StoryRepository.save()
  ↓
SQLite
```

Đây chính là Clean Architecture.

---

# 34. Dependency Graph

Nhìn source-code dependency:

```text
presentation
      ↓
application
      ↓
domain
```

và:

```text
infrastructure
      ↓
domain
```

Composition Root:

```text
composition
 ├── presentation
 ├── application
 ├── infrastructure
 └── domain
```

---

# 35. Infrastructure không được "kéo" Application vào

Ví dụ không nên:

```python
# infrastructure/sqlite.py

from application.publish_story import PublishStory
```

SQLite không cần biết Use Case.

Nó chỉ implement port.

```text
SQLiteRepository
       ↓
StoryRepository
```

---

# 36. Application không được tạo Infrastructure

Sai:

```python
class PublishStory:

    def __init__(self):

        self.repository = (
            SQLiteStoryRepository(...)
        )
```

Đây là violation DIP.

Đúng:

```python
class PublishStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository
```

---

# 37. CLI cũng không nên tạo SQLite

Sai:

```python
def publish(story_id):

    connection = sqlite3.connect(...)

    repo = SQLiteStoryRepository(connection)

    ...
```

Nếu làm vậy:

```text
CLI
 ↓
SQLite
```

CLI đã biết infrastructure.

Tốt hơn:

```text
CLI
 ↓
Composition Root
 ↓
Use Case
```

---

# 38. Nhưng `build_application()` đang được gọi trong mỗi command?

Đúng.

Với project nhỏ, có thể chấp nhận.

Nhưng khi project lớn hơn, ta có thể tạo Application object một lần.

Ví dụ:

```python
services = build_application()
```

rồi dùng lại.

Tuy nhiên đừng vội tối ưu architecture trước khi có nhu cầu.

---

# 39. Một cải tiến: Application Container

Thay dictionary:

```python
{
    "create_story": ...,
    "get_story": ...,
}
```

ta có:

```python
from dataclasses import dataclass


@dataclass
class Application:

    create_story: CreateStory
    get_story: GetStory
    rename_story: RenameStory
    publish_story: PublishStory
    delete_story: DeleteStory
```

Composition:

```python
def build_application():

    connection = sqlite3.connect(
        "stories.db"
    )

    repository = SQLiteStoryRepository(
        connection
    )

    repository.initialize()

    return Application(
        create_story=CreateStory(repository),
        get_story=GetStory(repository),
        rename_story=RenameStory(repository),
        publish_story=PublishStory(repository),
        delete_story=DeleteStory(repository),
    )
```

Đây thường dễ dùng hơn.

---

# 40. CLI với Application

```python
application = build_application()
```

Command:

```python
@story_app.command()
def create(title: str):

    story = application.create_story.execute(
        title
    )

    typer.echo(
        f"Created #{story.id}"
    )
```

Rất sạch.

---

# 41. Nhưng test CLI thế nào?

Đây là điểm tuyệt vời.

CLI không cần SQLite nếu ta inject application.

Ví dụ:

```python
class FakeCreateStory:

    def execute(self, title):
        return Story(
            id=1,
            title=title,
        )
```

Ta có thể test presentation riêng.

---

# 42. Test Application bằng Fake Repository

Đây mới là unit test quan trọng.

```python
class FakeStoryRepository:

    def __init__(self):
        self.stories = {}
        self.next_id = 1

    def create(self, story):

        story.id = self.next_id

        self.stories[
            self.next_id
        ] = story

        self.next_id += 1

        return story

    def get_by_id(self, story_id):

        return self.stories.get(story_id)

    def save(self, story):

        self.stories[story.id] = story

    def delete(self, story_id):

        del self.stories[story_id]
```

---

# 43. Test CreateStory

```python
def test_create_story():

    repo = FakeStoryRepository()

    use_case = CreateStory(repo)

    story = use_case.execute(
        "Harry Potter"
    )

    assert story.id == 1
    assert story.title == "Harry Potter"
```

Không cần:

```text
SQLite
filesystem
CLI
```

---

# 44. Test PublishStory

```python
def test_publish_story():

    repo = FakeStoryRepository()

    story = Story(
        id=None,
        title="Harry Potter",
    )

    story = repo.create(story)

    use_case = PublishStory(repo)

    result = use_case.execute(
        story.id
    )

    assert result.published is True
```

---

# 45. Test business invariant

```python
def test_cannot_publish_twice():

    repo = FakeStoryRepository()

    story = repo.create(
        Story(
            id=None,
            title="Harry Potter",
        )
    )

    use_case = PublishStory(repo)

    use_case.execute(story.id)

    try:
        use_case.execute(story.id)
    except ValueError as exc:
        assert "already published" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )
```

Nếu dùng pytest:

```python
import pytest


def test_cannot_publish_twice():

    repo = FakeStoryRepository()

    story = repo.create(
        Story(
            id=None,
            title="Harry Potter",
        )
    )

    use_case = PublishStory(repo)

    use_case.execute(story.id)

    with pytest.raises(ValueError):
        use_case.execute(story.id)
```

---

# 46. Lưu ý về Domain Model

Ở ví dụ trên:

```python
Story(
    id=None,
    title="Harry Potter",
)
```

cho phép title invalid nếu title là `""`.

Ta nên cải thiện:

```python
@dataclass
class Story:

    id: int | None
    title: str
    published: bool = False

    def __post_init__(self):

        if not self.title.strip():
            raise ValueError(
                "Story title cannot be empty"
            )
```

Như vậy invariant được bảo vệ ngay khi tạo Entity.

---

# 47. Tốt hơn nữa: Value Object

Sau này:

```python
@dataclass(frozen=True)
class StoryTitle:

    value: str

    def __post_init__(self):

        value = self.value.strip()

        if not value:
            raise ValueError(
                "Title cannot be empty"
            )
```

Entity:

```python
@dataclass
class Story:

    id: int | None
    title: StoryTitle
```

Khi đó:

```python
Story(
    id=None,
    title=StoryTitle("Harry Potter"),
)
```

Đây là hướng DDD mà chúng ta đã học ở Buổi 15.

---

# 48. CLI không cần biết Value Object

CLI:

```python
title = StoryTitle(value)
```

hoặc Use Case làm conversion.

Một thiết kế tốt hơn về sau là:

```text
CLI input
 ↓
DTO / Command
 ↓
Use Case
 ↓
Value Object
```

CLI không nên chứa business validation.

---

# 49. Error Handling

Application có thể raise:

```python
ValueError("Story not found")
```

CLI chuyển thành:

```python
try:
    ...
except ValueError as exc:
    typer.echo(
        str(exc),
        err=True,
    )
    raise typer.Exit(1)
```

Không nên để Domain biết:

```python
typer.echo(...)
```

Domain chỉ raise domain-level error.

---

# 50. Custom Exception

Khi project lớn hơn:

```python
class StoryNotFoundError(
    Exception
):
    pass
```

và:

```python
class StoryAlreadyPublishedError(
    Exception
):
    pass
```

Use Case:

```python
if story is None:
    raise StoryNotFoundError(story_id)
```

CLI:

```python
except StoryNotFoundError:
    typer.echo(
        "Story not found",
        err=True,
    )
```

Boundary chuyển domain/application error thành presentation error.

---

# 51. Đây chính là Adapter

```text
Domain/Application Exception
            ↓
        CLI Adapter
            ↓
       User message
```

Ví dụ:

```text
StoryNotFoundError
        ↓
"Story #10 not found"
```

API adapter có thể chuyển thành:

```json
{
    "error": "story_not_found"
}
```

Flet adapter:

```text
QMessageBox / Dialog
```

Business logic không đổi.

---

# 52. Một điểm rất quan trọng: DTO

Khi hệ thống lớn, không nên để CLI/API làm việc trực tiếp với Entity ở mọi nơi.

Có thể tạo:

```python
@dataclass
class StoryOutput:

    id: int
    title: str
    published: bool
```

Use Case:

```python
return StoryOutput(
    id=story.id,
    title=story.title,
    published=story.published,
)
```

CLI:

```python
result = use_case.execute(...)

print(result.title)
```

Điều này giúp presentation không phụ thuộc quá sâu vào domain object.

---

# 53. Kiến trúc hoàn chỉnh hơn

```text
src/novel/
│
├── domain/
│   ├── story.py
│   └── story_repository.py
│
├── application/
│   ├── create_story.py
│   ├── get_story.py
│   ├── rename_story.py
│   ├── publish_story.py
│   └── delete_story.py
│
├── infrastructure/
│   └── sqlite_story_repository.py
│
├── presentation/
│   └── cli.py
│
└── composition.py
```

Dependency:

```text
presentation ──────┐
                   ↓
application ───────→ domain
                   ↑
infrastructure ────┘
```

---

# 54. Nhưng còn một vấn đề

Hiện tại:

```python
from domain.story import Story
```

Infrastructure import Domain.

Tốt.

Nhưng:

```python
application
    ↓
domain
```

Tốt.

Và:

```python
presentation
    ↓
application
```

Tốt.

Điều quan trọng:

```text
domain
  ✗ → application
  ✗ → infrastructure
  ✗ → presentation
```

---

# 55. Dependency Rule kiểm tra bằng tư duy

Hãy hỏi từng package:

### Domain

> Có chạy được mà không có SQLite không?

**Phải có.**

### Application

> Có chạy được mà không có Typer không?

**Phải có.**

### Infrastructure

> Có thể thay SQLite bằng memory implementation không?

**Phải có.**

### Presentation

> Có thể thay CLI bằng Flet không?

**Phải có.**

Đây là cách kiểm tra architecture rất thực tế.

---

# 56. SOLID trong project này

### SRP

```text
Story
→ domain behavior

CreateStory
→ create use case

SQLiteRepository
→ persistence

CLI
→ presentation
```

### OCP

```text
SQLiteRepository
MemoryRepository
PostgresRepository
```

### LSP

Các repository phải cùng contract.

### ISP

Repository interface nhỏ.

### DIP

Use Case không tạo SQLite.

---

# 57. Composition Root là nơi "vi phạm" DIP một cách có chủ đích

Điều này rất thú vị.

Ở đây:

```python
repository = SQLiteStoryRepository(...)
```

được phép.

Nhưng **chỉ ở Composition Root**.

Vì Composition Root là nơi chịu trách nhiệm:

> Chọn implementation nào được sử dụng.

Ví dụ production:

```text
SQLite
```

Test:

```text
Fake
```

Production server:

```text
PostgreSQL
```

---

# 58. Production vs Test

Production:

```python
repository = SQLiteStoryRepository(
    connection
)

use_case = PublishStory(
    repository
)
```

Test:

```python
repository = FakeStoryRepository()

use_case = PublishStory(
    repository
)
```

Use Case giống hệt.

Đây là **Dependency Injection**.

---

# 59. Một mental model cực mạnh

Đừng nghĩ:

```text
"Use Case gọi SQLite"
```

Hãy nghĩ:

```text
"Use Case gọi Repository"
```

và:

```text
"SQLite là một implementation của Repository"
```

Tương tự:

Đừng nghĩ:

```text
"Use Case gọi requests"
```

Hãy nghĩ:

```text
"Use Case gọi HttpClient"
```

và:

```text
"requests là implementation của HttpClient"
```

---

# 60. Đây là Ports & Adapters

Clean Architecture có quan hệ rất gần với Hexagonal Architecture.

Ta có:

```text
              Application
                   │
          ┌────────┴────────┐
          ↓                 ↓
       Port              Port
          ↑                 ↑
          │                 │
     SQLite Adapter     HTTP Adapter
```

Trong Python:

```python
class StoryRepository(Protocol):
    ...
```

là một **port**.

```python
class SQLiteStoryRepository:
    ...
```

là **adapter**.

---

# 61. Crawler sau này sẽ dùng chính mô hình này

Ví dụ:

```python
class Crawler(Protocol):

    def crawl(
        self,
        url: str,
    ) -> Story:
        ...
```

Use Case:

```python
class CrawlStory:

    def __init__(
        self,
        crawler: Crawler,
        repository: StoryRepository,
    ):
        ...
```

Plugin:

```text
SiteA Crawler
SiteB Crawler
SiteC Crawler
```

Đây chính là nội dung Buổi 18.

---

# 62. Bài tập thực hành

## Bài 1

Tạo project:

```text
novel/
```

với:

```text
domain/
application/
infrastructure/
presentation/
composition.py
```

---

## Bài 2

Implement:

```text
Story
StoryRepository
CreateStory
GetStory
RenameStory
PublishStory
DeleteStory
SQLiteStoryRepository
```

---

## Bài 3

CLI:

```bash
novel story create "Python"
novel story get 1
novel story rename 1 "Python Advanced"
novel story publish 1
novel story delete 1
```

---

## Bài 4

Viết:

```text
FakeStoryRepository
```

và test:

```text
create
rename
publish
delete
```

Không dùng SQLite.

---

# 63. Bài tập nâng cao

Thêm:

```bash
novel story create "Python"
```

nhưng không cho:

```bash
novel story create ""
```

Rule phải nằm ở:

```text
Domain
```

không phải:

```text
CLI
```

Sau đó thử tạo Story bằng test trực tiếp:

```python
Story(
    id=None,
    title="",
)
```

Nó cũng phải fail.

Đây là cách kiểm tra xem business rule có thực sự nằm đúng layer hay chưa.

---

# 64. Bài tập kiến trúc

Thử thay:

```text
SQLiteStoryRepository
```

bằng:

```python
class InMemoryStoryRepository:
    ...
```

**Không được sửa:**

```text
Story
CreateStory
GetStory
RenameStory
PublishStory
DeleteStory
```

Nếu làm được:

> Architecture đang đi đúng hướng.

---

# 65. Tổng kết Buổi 17

Chúng ta vừa xây pipeline:

```text
                    User
                     │
                     ↓
                  Typer CLI
                     │
                     ↓
                 Use Case
                     │
                     ↓
                  Domain
                     │
                     ↓
            StoryRepository
               (Protocol)
                     ↑
                     │
          SQLiteRepository
                     │
                     ↓
                  SQLite
```

Điều quan trọng nhất:

```text
CLI
  ✗ không biết SQL

Use Case
  ✗ không biết SQLite

Domain
  ✗ không biết database
  ✗ không biết CLI
  ✗ không biết Typer

SQLite
  ✓ biết Domain
  ✓ implement Repository
```

Và toàn bộ dependency được lắp tại:

```text
Composition Root
```

---

# Roadmap

```text
Phần VI — SOLID trong Clean Architecture

✅ Buổi 16 — SOLID + Clean Architecture

✅ Buổi 17 — CLI
   CLI
    ↓
   Application
    ↓
   Domain
    ↓
   Repository Interface
    ↓
   SQLite Repository

⬜ Buổi 18 — Crawler
   Crawler
    ↓
   Use Case
    ↓
   Crawler Interface
    ↓
   Crawler Plugin

⬜ Buổi 19 — Refactoring
   CrawlerManager
        ↓
   God Object
        ↓
   SRP
        ↓
   OCP
        ↓
   DIP
        ↓
   DDD
        ↓
   Clean Architecture
```

**Điểm mấu chốt cần nắm sau Buổi 17:** `CLI → Use Case → Domain` là luồng nghiệp vụ; `Repository Protocol → SQLite Repository` là boundary persistence; và **Composition Root là nơi duy nhất nên quyết định implementation cụ thể**. Đây chính là nền móng để Buổi 18 xây hệ thống `Crawler → Use Case → Crawler Protocol → Crawler Plugin`.
