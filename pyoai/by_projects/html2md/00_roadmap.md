
# 14. Roadmap chúng ta sẽ học và xây

Mình đề xuất làm thành **khóa học + project thực tế**, từng buổi hoàn thiện một phần.

### Phase I — Windows Clipboard

**Buổi 1**

* Kiến trúc project
* Flet desktop
* Windows Clipboard
* CF_UNICODETEXT
* CF_HTML
* đọc HTML từ clipboard

**Buổi 2**

* CF_HTML format
* `StartHTML`
* `EndHTML`
* `StartFragment`
* `EndFragment`
* parser metadata Windows
* lấy HTML fragment chính xác

**Buổi 3**

* Clipboard monitor
* phát hiện clipboard thay đổi
* sequence number
* tránh infinite loop

### Phase II — HTML Cleaner

**Buổi 4**

* BeautifulSoup
* parse tree
* remove tag

**Buổi 5**

* loại quảng cáo
* tracking
* navigation
* social
* cookie
* popup

**Buổi 6**

* cleaning rule system
* `CleaningPolicy`
* configurable rules

### Phase III — Markdown

**Buổi 7**

* html2text
* configuration
* heading
* paragraph
* link
* image

**Buổi 8**

* `<pre>`
* `<code>`
* inline code
* fenced code block
* language detection

**Buổi 9**

* bảo vệ code trước khi convert
* restore code sau khi convert
* xử lý indentation

### Phase IV — Pipeline

**Buổi 10**

* Processor
* pipeline architecture
* error handling

**Buổi 11**

* logging
* statistics
* retry
* performance

### Phase V — Flet UI

**Buổi 12**

* Flet window
* always-on-top
* ON/OFF
* status

**Buổi 13**

* UI state
* processing indicator
* error indicator
* history

### Phase VI — Production

**Buổi 14**

* settings
* cấu hình cleaning rules

**Buổi 15**

* system tray
* start with Windows
* minimize to tray

**Buổi 16**

* test

**Buổi 17**

* đóng gói `.exe`

**Buổi 18**

* hoàn thiện `Clip2MD`

---