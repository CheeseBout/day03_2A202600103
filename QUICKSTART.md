# Hướng dẫn chạy Lab 3

## 1. Cài dependencies

```bash
pip install -r requirements.txt
```

## 2. Cấu hình API key

```bash
cp .env.example .env
```

Mở file `.env` và điền API key:
```
OPENAI_API_KEY=sk-...
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
GEMINI_API_KEY=your_gemini_api_key_here
LOCAL_MODEL_PATH=./models/gemma-4-E4B-it-Q4_1.gguf
SERPAPI_API_KEY=your_serpapi_api_key_here
```

## 3. Khởi tạo database

Chỉ cần chạy 1 lần:
```bash
python src/tools/init_db.py
```

Kết quả: tạo file `src/tools/products.db` với 6 sản phẩm mẫu.

## 4. Mô tả các Tools

### `search_product(query)`
Tìm kiếm sản phẩm trong kho theo tên hoặc danh mục.

- Input: chuỗi tìm kiếm, ví dụ `"iPhone"`, `"Laptop"`, `"Điện thoại"`
- Xử lý: query SQLite `WHERE name LIKE '%query%' OR category LIKE '%query%'`
- Output: danh sách sản phẩm khớp gồm id, tên, giá, danh mục
- Lỗi: trả về thông báo nếu không tìm thấy

```
Tìm thấy 2 sản phẩm:
p001 - iPhone 15 128GB - 22,000,000đ - Điện thoại
p002 - iPhone 15 256GB - 25,000,000đ - Điện thoại
```

---

### `get_product_detail(product_id)`
Xem toàn bộ thông tin chi tiết của 1 sản phẩm.

- Input: id sản phẩm, ví dụ `"p001"`
- Xử lý: query SQLite `WHERE id = product_id`, lấy tất cả các cột
- Output: tên, danh mục, giá, thông số kỹ thuật, tồn kho
- Lỗi: trả về thông báo nếu id không tồn tại

```
Tên: iPhone 15 128GB
Danh mục: Điện thoại
Giá: 22,000,000đ
Thông số: 6.1 inch, chip A16 Bionic, camera 48MP, pin 3279mAh
Tồn kho: Còn 5 sản phẩm
```

---

### `compare_product(product_list)`
So sánh nhiều sản phẩm cùng lúc theo giá, thông số, tồn kho.

- Input: các product_id cách nhau bởi dấu phẩy, ví dụ `"p001,p003"`
- Xử lý: query SQLite `WHERE id IN (...)`, trả về bảng so sánh dạng text
- Output: bảng gồm tên, giá, tồn kho, thông số của từng sản phẩm
- Lỗi: trả về thông báo nếu không tìm thấy sản phẩm nào

```
Tên                       Giá           Tồn kho    Thông số
--------------------------------------------------------------------------------
iPhone 15 128GB     22,000,000đ  Còn 5       6.1 inch, chip A16 Bionic...
Samsung Galaxy S24  20,000,000đ  Còn 8       6.2 inch, Snapdragon 8 Gen 3...
```

---

### `check_inventory(product_id)`
Kiểm tra nhanh số lượng tồn kho của 1 sản phẩm.

- Input: id sản phẩm, ví dụ `"p002"`
- Xử lý: query SQLite `SELECT name, stock WHERE id = product_id`
- Output: tên sản phẩm + số lượng còn hoặc thông báo hết hàng
- Lỗi: trả về thông báo nếu id không tồn tại

```
iPhone 15 256GB: Hết hàng
iPhone 15 128GB: Còn 5 sản phẩm trong kho
```

---

### `web_search_product(query)`
Tìm kiếm thông tin, tính năng và giá cả của một sản phẩm trên mạng Internet nếu sản phẩm không có trong kho.

- Input: từ khóa tìm kiếm, ví dụ `"iPhone 15 Pro Max"`
- Xử lý: Gọi API SerpAPI để tìm kiếm Google
- Output: Danh sách các trang web tìm thấy gồm tiêu đề, URL, snippet
- Lỗi: trả về thông báo lỗi nếu yêu cầu bị lỗi

```
Kết quả tìm kiếm web cho 'iPhone 15 Pro Max':
1. iPhone 15 Pro Max - Apple (VN)
URL: https://www.apple.com/vn/iphone-15-pro/...
Snippet: ...
```

---

### `read_web_page(url)`
Đọc chi tiết văn bản của một bài viết hoặc trang web để lấy thông tin.

- Input: một đường link (URL) hợp lệ
- Xử lý: Lấy nội dung trang bằng BeautifulSoup, loại bỏ thẻ không cần thiết, tự động cắt bớt văn bản quá dài
- Output: Nội dung văn bản thuần túy tóm gọn của URL đó
- Lỗi: trả về thông báo nếu mất mạng hoặc quá thời gian truy cập (timeout)

```
Nội dung từ https://example.com/article:
... (văn bản của trang web)
```

---

## 5. Test từng tool riêng lẻ

```bash
python -c "from src.tools.search_product import search_product; print(search_product('iPhone'))"
python -c "from src.tools.get_product_detail import get_product_detail; print(get_product_detail('p001'))"
python -c "from src.tools.compare_product import compare_product; print(compare_product('p001,p003'))"
python -c "from src.tools.check_inventory import check_inventory; print(check_inventory('p002'))"
python -c "from src.tools.web_search_product import web_search_product; print(web_search_product('iPhone 15'))"
python -c "from src.tools.read_web_page import read_web_page; print(read_web_page('https://example.com'))"
```

## 6. Chạy demo Agent vs Chatbot

```bash
python run_demo.py
```

Log sẽ được lưu tại `logs/YYYY-MM-DD.log`.

## Cấu trúc thư mục

```
src/
├── agent/
│   ├── agent.py        # ReAct Agent (vòng lặp Thought-Action-Observation)
│   └── chatbot.py      # Chatbot baseline (gọi LLM thẳng)
├── core/
│   ├── llm_provider.py # Abstract base class
│   ├── openai_provider.py
│   └── gemini_provider.py
├── tools/
│   ├── init_db.py          # Khởi tạo SQLite database
│   ├── products.db         # File database (tự sinh sau bước 3)
│   ├── search_product.py
│   ├── get_product_detail.py
│   ├── compare_product.py
│   ├── check_inventory.py
│   ├── web_search_product.py
│   └── read_web_page.py
└── telemetry/
    ├── logger.py
    └── metrics.py
```
