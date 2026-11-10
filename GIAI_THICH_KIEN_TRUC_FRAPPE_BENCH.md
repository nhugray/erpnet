# Tài Liệu Giải Thích Chi Tiết Kiến Trúc Frappe Bench
*(Dành cho Frappe Framework & ERPNext)*

---

## 1. Frappe Bench Là Gì?

**Frappe Bench** là một hệ sinh thái quản lý toàn diện dành cho Frappe Framework và ERPNext. Khác với các framework thông thường (như Django, Laravel, Rails - vốn chỉ cung cấp một thư viện mã nguồn và một công cụ dòng lệnh cơ bản), Frappe Bench đóng 3 vai trò cùng lúc:

1. **Bộ công cụ dòng lệnh (CLI Tool - `bench`):** Hỗ trợ tạo site mới, cài đặt ứng dụng, cập nhật cơ sở dữ liệu (`migrate`), sao lưu (`backup`), quản lý tiến trình và chạy script tự động.
2. **Không gian làm việc cô lập (Workspace / Directory Manager):** Tổ chức mã nguồn đa ứng dụng (**Multi-App**), cấu hình đa người thuê (**Multi-Tenant Sites**), và môi trường ảo Python (**Python Virtualenv**) trong cùng một cấu trúc thư mục tiêu chuẩn.
3. **Bộ điều phối dịch vụ phụ trợ (Process Orchestrator):** Tự động sinh cấu hình và giám sát các dịch vụ nền tảng: máy chủ web WSGI (Gunicorn), cổng chuyển tiếp (Nginx), bộ nhớ đệm (Redis), hàng đợi công việc nền (RQ Workers), trình lập lịch tác vụ định kỳ (Scheduler) và truyền thông thời gian thực (Node.js Socket.IO).

---

## 2. Giải Phẫu Cấu Trúc Thư Mục `frappe-bench`

Khi một Bench được khởi tạo, toàn bộ hệ thống nằm gọn trong thư mục gốc (thường là `/home/frappe/frappe-bench/` hoặc đường dẫn do người quản trị chỉ định). Cấu trúc gồm 5 thành phần xương sống:

```text
frappe-bench/
├── apps/                         # Nơi chứa mã nguồn các ứng dụng Python / JS
│   ├── frappe/                  # Framework cốt lõi (Core Engine)
│   ├── erpnext/                 # Ứng dụng quản trị doanh nghiệp chuẩn
│   └── custom_app/              # Ứng dụng tự phát triển độc lập
│
├── sites/                        # Vùng dữ liệu đa người thuê (Multi-Tenancy)
│   ├── common_site_config.json  # Cấu hình dùng chung của toàn bộ Bench
│   ├── apps.txt                 # Danh sách các app được nạp vào Bench
│   ├── assets/                  # Symlinks trỏ tới file tĩnh (CSS/JS) của các app
│   └── [site_name]/             # Thư mục riêng của từng Site (Tenant)
│       ├── site_config.json     # Cấu hình CSDL, mật khẩu DB, mã hóa của Site
│       ├── public/files/        # Tệp đính kèm công khai (không cần đăng nhập)
│       ├── private/files/       # Tệp chứng từ nhạy cảm (bắt buộc xác thực)
│       └── locks/               # Khóa trạng thái scheduler / migration
│
├── env/                          # Môi trường ảo Python (Virtual Environment)
│   ├── bin/python               # Trình thông dịch Python chuẩn của Bench
│   ├── bin/gunicorn             # Web Server WSGI
│   └── lib/python3.x/           # Thư viện phụ thuộc (pip packages)
│
├── config/                       # Tệp cấu hình dịch vụ do Bench tự sinh
│   ├── nginx.conf               # Cấu hình Web Server Nginx
│   ├── supervisor.conf          # Cấu hình giám sát tiến trình hệ thống
│   ├── redis_cache.conf         # Cấu hình Redis Cache
│   ├── redis_queue.conf         # Cấu hình Redis Queue
│   └── redis_socketio.conf      # Cấu hình Redis Socket.IO
│
└── logs/                         # Nhật ký ghi nhận hoạt động và lỗi
    ├── frappe.log               # Nhật ký xử lý ngoại lệ và ứng dụng
    ├── web.log / web.error.log  # Nhật ký truy cập HTTP qua Gunicorn
    ├── worker.log               # Nhật ký tiến trình nền RQ Worker
    └── schedule.log             # Nhật ký kích hoạt tác vụ định kỳ
```

---

## 3. Cơ Chế Đa Người Thuê (Multi-Tenancy) Của Frappe Bench

Một ưu điểm kiến trúc vượt trội của Frappe Bench là khả năng phục vụ **nhiều Site (nhiều khách hàng/doanh nghiệp)** trên **cùng một nền tảng mã nguồn duy nhất**:

```
                       ┌─── Domain: congty-a.vn ───► Database: _db_congty_a
                       │
Mã Nguồn (apps/) ──────┼─── Domain: congty-b.com ──► Database: _db_congty_b
                       │
                       └─── Domain: test.local ────► Database: _db_test
```

### Cơ chế hoạt động:
* **Nhận diện Site (Site Resolution):**
  * Khi người dùng truy cập qua trình duyệt, Nginx chuyển tiếp header `Host: congty-a.vn` vào Gunicorn.
  * Frappe đọc header này, đối chiếu tên miền với danh mục thư mục trong `sites/` để nạp đúng cấu hình `sites/congty-a.vn/site_config.json`.
  * Khi gọi qua lệnh CLI, cờ `--site <tên_site>` đóng vai trò chỉ định Site đích.
* **Cách ly dữ liệu hoàn toàn:**
  * Mỗi Site sở hữu một CSDL MariaDB/PostgreSQL riêng biệt với thông tin tài khoản truy cập khác nhau.
  * Tệp tải lên (ảnh, PDF, hợp đồng) được lưu tại thư mục `sites/<site>/public/` và `sites/<site>/private/`, không thể bị truy cập chéo giữa các Site.

---

## 4. Kiến Trúc Tiến Trình Runtime (Runtime Process Architecture)

Hệ thống vận hành của Frappe Bench là sự kết hợp nhịp nhàng giữa 6 phân lớp dịch vụ:

### 4.1. Cổng Đón Nhận (Reverse Proxy - Nginx)
* Lắng nghe tại cổng tiêu chuẩn (80 / 443 hoặc cổng tùy biến như 8080).
* Phục vụ trực tiếp tài nguyên tĩnh (`/assets/*`, `/files/*`) mà không cần chuyển tiếp vào Python, giúp giải phóng tải CPU.
* Định tuyến lưu lượng động: Các yêu cầu API và giao diện Desk (`/app/*`, `/api/*`) được chuyển qua Gunicorn; các kết nối WebSocket thời gian thực được đẩy qua Node.js Socket.IO.

### 4.2. Máy Chủ Ứng Dụng WSGI (Gunicorn Web Server)
* Chạy bằng trình thông dịch bên trong `env/bin/gunicorn`, lắng nghe tại cổng nội bộ 8000.
* Nạp hàm ứng dụng Python `frappe.app.application`.
* Điều phối nhiều luồng xử lý (Workers) chạy song song để giải quyết các yêu cầu HTTP đồng thời.

### 4.3. Máy Chủ Sự Kiện Thời Gian Thực (Node.js Socket.IO Server)
* Lắng nghe tại cổng nội bộ 9000 (`socketio.js`).
* Đảm nhận kết nối 2 chiều liên tục (Full-duplex WebSocket) với trình duyệt người dùng.
* Ứng dụng: Đẩy thông báo tức thời (Realtime Notifications), hiển thị người dùng đang cùng mở xem một chứng từ (Document Viewers), và khóa chỉnh sửa tránh xung đột dữ liệu.

### 4.4. Bộ Ba Cụm Redis (Redis Triad)
Frappe không dùng chung một cổng Redis cho tất cả tác vụ, mà tách thành 3 cụm riêng biệt để tối ưu hiệu năng và tránh tắc nghẽn bộ nhớ:
1. **Redis Cache:** Lưu trữ trạng thái phiên làm việc (Session), cấu hình DocType, và quyền hạn người dùng (Permissions). Khi DocType được cập nhật, Bench xóa cache này để áp dụng ngay.
2. **Redis Queue:** Đóng vai trò là Message Broker (kênh trung chuyển) quản lý hàng đợi cho các tiến trình xử lý ngầm (RQ).
3. **Redis SocketIO:** Kênh Pub/Sub kết nối giữa Python Backend và Node.js Socket.IO Server để truyền phát sự kiện ra trình duyệt.

### 4.5. Hàng Đợi Công Việc Nền (RQ Background Workers)
* Xử lý các tác vụ tốn thời gian mà người dùng không thể đợi đồng bộ (như gửi email hàng loạt, xử lý báo cáo kế toán nặng, đồng bộ dữ liệu lớn).
* Phân thành 3 mức hàng đợi ưu tiên:
  * `short`: Tác vụ nhanh, hoàn tất dưới 5 phút.
  * `default`: Tác vụ tiêu chuẩn.
  * `long`: Tác vụ tính toán kéo dài (tối đa nhiều giờ).

### 4.6. Trình Lập Lịch Định Kỳ (Frappe Scheduler)
* Chạy dưới dạng tiến trình nền liên tục (`bench schedule`).
* Cứ mỗi phút, Scheduler quét bảng tác vụ và kiểm tra các hàm được khai báo trong `hooks.py` theo các tần suất: `all`, `hourly`, `daily`, `weekly`, `monthly` hoặc biểu thức `cron(...)`.
* Khi đến hạn, Scheduler tự động đẩy tác vụ đó vào Redis Queue để Background Worker xử lý.

### 4.7. Tầng Lưu Trữ Quan Hệ (MariaDB / PostgreSQL)
* Toàn bộ mô hình dữ liệu (DocType) trong Frappe được ánh xạ tự động thành bảng CSDL vật lý có tiền tố `tab` (Ví dụ: `tabUser`, `tabItem`, `tabCustomer`).
* Đảm bảo tính toán vẹn dữ liệu qua cơ chế giao dịch ACID và khóa dòng (Row-level Locking).

---

## 5. Vòng Đời Hoạt Động (Lifecycle) Của Một Tác Vụ Trong Bench

Khi một lệnh CLI được gõ (ví dụ `bench --site site1.local execute my_module.run`) hoặc một yêu cầu HTTP gửi đến API, chuỗi xử lý diễn ra qua 4 bước:

```
[1. Khởi tạo]            [2. Kết nối CSDL]        [3. Thực thi Logic]       [4. Giải phóng]
frappe.init(site)   ──►  frappe.connect()   ──►  Controller / Hooks   ──►  frappe.destroy()
Nạp site_config          Nạp DB Connection        validate() ➔ on_save     commit() / rollback()
& ngữ cảnh luồng         & Redis Cache            Enqueue background job   Đóng kết nối DB
```

1. **Khởi tạo ngữ cảnh (`frappe.init(site)`):** Frappe nạp cấu hình của Site được chỉ định, gán biến `frappe.local` chứa thông tin phiên, ngôn ngữ và múi giờ.
2. **Mở kết nối (`frappe.connect()`):** Mở kết nối chuyên dụng tới CSDL của Site đó và nạp cache từ Redis.
3. **Thực thi logic nghiệp vụ:** Chạy hàm xử lý, kích hoạt chuỗi sự kiện vòng đời (`validate()`, `before_save()`, `on_submit()`). Nếu có tác vụ ngầm, đẩy vào Redis Queue.
4. **Cam kết và dọn dẹp (`frappe.destroy()`):** 
   * Nếu thành công: Gọi `frappe.db.commit()` để lưu dữ liệu vĩnh viễn vào đĩa.
   * Nếu xảy ra lỗi: Gọi `frappe.db.rollback()` hoàn tác trạng thái ban đầu, ghi log lỗi vào `logs/frappe.log`, sau đó giải phóng kết nối CSDL.

---

## 6. Tổng Hợp Các Lệnh Bench Cốt Lõi Trong Thực Tế

| Nhóm Lệnh | Cú Pháp Lệnh | Mục Đích Sử Dụng |
| :--- | :--- | :--- |
| **Quản lý Site** | `bench new-site <site>` | Tạo một Site mới và khởi tạo CSDL MariaDB riêng. |
| | `bench drop-site <site>` | Xóa hoàn toàn Site và CSDL tương ứng. |
| **Cài đặt App** | `bench get-app <git-url>` | Clone mã nguồn ứng dụng mới vào thư mục `apps/` và cài vào môi trường `env/`. |
| | `bench --site <site> install-app <app>` | Cài đặt và di trú bảng của ứng dụng vào Site cụ thể. |
| **Di trú CSDL** | `bench --site <site> migrate` | So sánh cấu trúc DocType mã nguồn và tự động `ALTER TABLE` cập nhật CSDL. |
| **Lập trình & Script** | `bench --site <site> execute <path.func>` | Chạy một hàm Python có nạp sẵn toàn bộ ngữ cảnh và kết nối CSDL. |
| | `bench --site <site> console` | Mở cửa sổ tương tác IPython trực tiếp với CSDL và ORM của Frappe. |
| **Sao lưu & Phục hồi**| `bench --site <site> backup --with-files` | Xuất file dump CSDL (`.sql.gz`) và toàn bộ file đính kèm. |
| | `bench --site <site> restore <path.sql.gz>` | Phục hồi lại dữ liệu CSDL từ bản sao lưu. |
| **Vận hành hệ thống** | `bench start` | Khởi động đồng thời tất cả các tiến trình (trong môi trường phát triển local). |
| | `bench restart` | Khởi động lại các tiến trình Gunicorn và Worker khi có cập nhật mã nguồn. |

---

*Tài liệu này được tạo để chuẩn hóa kiến thức kiến trúc hệ thống Frappe Framework & ERPNext.*
