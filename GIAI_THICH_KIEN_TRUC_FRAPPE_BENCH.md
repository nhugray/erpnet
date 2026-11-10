# Hướng Dẫn Kỹ Thuật Toàn Diện: Kiến Trúc Frappe Framework, Frappe Bench & Bản Chất DocType

---

## MỤC LỤC
1. [Phần 1: Kiến Trúc Hạ Tầng Tổng Quan (Theo Sơ Đồ Tiêu Chuẩn Frappe)](#phần-1-kiến-trúc-hạ-tầng-tổng-quan-theo-sơ-đồ-tiêu-chuẩn-frappe)
2. [Phần 2: Kiến Trúc Chi Tiết & Cơ Chế Vận Hành Runtime Của Frappe Bench](#phần-2-kiến-trúc-chi-tiết--cơ-chế-vận-hành-runtime-của-frappe-bench)
3. [Phần 3: DocType Là Gì? Dùng Để Làm Gì? Kết Nối Với Cơ Sở Dữ Liệu Như Thế Nào?](#phần-3-doctype-là-gì-dùng-để-làm-gì-kết-nối-với-cơ-sở-dữ-liệu-như-thế-nào)
4. [Phần 4: Sơ Đồ Toàn Diện Về Vòng Đời & Cách Hoạt Động Của DocType](#phần-4-sơ-đồ-toàn-diện-về-vòng-đời--cách-hoạt-động-của-doctype)

---

## PHẦN 1: KIẾN TRÚC HẠ TẦNG TỔNG QUAN (THEO SƠ ĐỒ TIÊU CHUẨN FRAPPE)

Kiến trúc chuẩn của hệ sinh thái Frappe được xây dựng theo mô hình kim tự tháp 5 tầng từ phần cứng, hệ điều hành lên tới giao diện người dùng:

```text
 ┌────────────────────────────────────────────────────────┐   ┌─────────────────┐
 │               Viewing IO Interface                     │◄──┤  Request Queue  │
 │  ┌────────────────────────┐  ┌──────────────────────┐  │   │     (Clock)     │
 │  │      Desktop UI        │  │      Mobile UI       │  │   └────────┬────────┘
 │  └────────────────────────┘  └──────────────────────┘  │            │
 └───────────────────────────▲────────────────────────────┘            │
                             │ start (bench start)                     │
 ┌───────────────────────────┴─────────────────────────────────────────┴────────┐
 │                                                                              │
 │  ┌──────────────────────┐  ┌────────────────────────┐  ┌──────────────────┐  │
 │  │ Configuration Layer  │  │   Multi-Tenant Layer   │  │ Scheduling Layer │  │
 │  │                      │  │                        │  │                  │  │
 │  │  [nginx.conf]        │  │  ┌──────────────────┐  │  │  [jobs queue]    │  │
 │  │  [supervisor.conf]   │  │  │ bench-instance-1 │  │  │  ■ ■ ■ ■ ■ ■ ■   │  │
 │  │  [redis.conf]        │  │  │ sites (yellow)   │  │  │  ■ ■ ■ ■ ■ ■ ■   │  │
 │  │  [site_config.json]  │  │  │ apps: frappe/erp │  │  │  ■ ■ ■ ■ ■ ■ ■   │  │
 │  │                      │  │  └──────────────────┘  │  │                  │  │
 │  └──────────┬───────────┘  └───────────▲────────────┘  └────────▲─────────┘  │
 │             │ setup, config            │                        │            │
 └─────────────┼──────────────────────────┼────────────────────────┼────────────┘
               │                          │ new-site, install-app  │ enable-sched
 ┌─────────────┴──────────────────────────┴────────────────────────┴────────────┐
 │  Prerequisites:  [mariadb]   [nodejs]   [nginx]   [wkhtmltopdf]  [fail2ban]  │
 └────────────────────────────────────────▲─────────────────────────────────────┘
                                          │ install
 ┌────────────────────────────────────────┴─────────────────────────────────────┐
 │  bench CLI                             (pip install frappe-bench)            │
 └────────────────────────────────────────▲─────────────────────────────────────┘
                                          │
 ┌────────────────────────────────────────┴─────────────────────────────────────┐
 │  Dependencies:                         GIT, Python, PIP                      │
 └────────────────────────────────────────▲─────────────────────────────────────┘
                                          │
 ┌────────────────────────────────────────┴─────────────────────────────────────┐
 │  *nix OS Layer:                        Linux, Mac OS X, FreeBSD, Docker      │
 └──────────────────────────────────────────────────────────────────────────────┘
```

### 1.1. Tầng Hệ Điều Hành (*nix OS Layer) & Dependencies
* **Hệ điều hành cơ sở:** Hoạt động tối ưu trên các nền tảng nhân Unix (Ubuntu, Debian, CentOS, macOS) hoặc được đóng gói trong các Container Linux qua Docker.
* **Các gói phụ thuộc cốt lõi:**
  * `Git`: Quản lý phiên bản mã nguồn của từng ứng dụng (`apps/frappe`, `apps/erpnext`).
  * `Python (>= 3.10)`: Ngôn ngữ nền tảng xử lý toàn bộ logic máy chủ, ORM, bảo mật.
  * `PIP`: Trình quản lý thư viện Python để cài đặt Bench và các package cần thiết.

### 1.2. Tầng Công Cụ Bench CLI (`bench`)
* Được cài đặt thông qua lệnh: `pip install frappe-bench`.
* Đóng vai trò là "Tổng tư lệnh" điều khiển: bench tải ứng dụng, cài đặt CSDL, kích hoạt cron, cấu hình reverse proxy và giám sát tiến trình.

### 1.3. Tầng Dịch Vụ Nền Tảng (Prerequisites)
Được Bench tự động tương tác và thiết lập thông qua lệnh `bench setup prerequisites`:
1. **MariaDB:** Cơ sở dữ liệu quan hệ lưu trữ thực thể (InnoDB, utf8mb4, dynamic row format).
2. **Node.js (kèm npm/yarn):** Biên dịch tài nguyên giao diện Desk (Javascript, CSS bundling qua Vite/Rollup) và chạy Socket.IO server.
3. **Nginx:** Cổng đón nhận (Web Server & Reverse Proxy) điều phối tên miền đa site và phục vụ file tĩnh.
4. **Wkhtmltopdf:** Thư viện chuyển đổi giao diện HTML/CSS thành bản in PDF chuẩn (hóa đơn, phiếu kho, đơn hàng).
5. **Fail2ban:** Tự động chặn các IP dò quét mật khẩu đăng nhập bất thường.

### 1.4. Tầng Cấu Hình (Configuration Layer)
* Bench tự động sinh ra các file cấu hình tương thích từ cấu trúc thư mục mà không cần quản trị viên chỉnh sửa thủ công:
  * `config/nginx.conf`: Tự động nhận diện danh sách domain của các site để mở Virtual Host.
  * `config/supervisor.conf`: Cấu hình danh sách tiến trình nền cần chạy liên tục.
  * `sites/[site]/site_config.json`: Thông số kết nối DB và khóa bảo mật riêng của từng tenant.

### 1.5. Tầng Đa Người Thuê (Multi-Tenant Layer)
* Cho phép một máy chủ chạy cùng lúc nhiều **Bench Instance**.
* Mỗi Bench Instance lại phục vụ nhiều **Sites** độc lập (mỗi ô vuông màu vàng là một site/CSDL riêng).
* Các site chia sẻ chung các ứng dụng mã nguồn:
  * **Frappe (Đỏ):** Lõi framework.
  * **ERPNext (Xanh dương):** Ứng dụng nghiệp vụ chuẩn.
  * **Frappe App (Xanh ngọc):** Các module hoặc ứng dụng tùy biến độc lập.

### 1.6. Tầng Lập Lịch & Hàng Đợi (Scheduling Layer & Request Queue)
* Quản lý các công việc (Jobs) chạy định kỳ hoặc ngầm.
* Lệnh điều phối: `bench enable-scheduler`, `bench doctor`, `bench purge-jobs`.
* Đồng bộ trực tiếp với **Request Queue** và **Viewing IO Interface** để đảm bảo người dùng giao diện Desk luôn nhận được phản hồi mượt mà trong khi các việc nặng vẫn chạy ngầm.

---

## PHẦN 2: KIẾN TRÚC CHI TIẾT & CƠ CHẾ VẬN HÀNH RUNTIME CỦA FRAPPE BENCH

Khi hệ thống vận hành thực tế (chạy qua `bench start` hoặc trong Docker/Production), các tiến trình phối hợp theo luồng nghiệp vụ sau:

```
[Người dùng / Web Browser / REST Client]
                  │
                  ▼ (Port 80/443/8080)
           ┌──────────────┐
           │ Nginx Proxy  │
           └──────┬───────┘
                  │
        ┌─────────┴───────────────────────┐
        │                                 │
   (File tĩnh)                       (Request động)
        ▼                                 ▼
[/assets/, /files/]             ┌───────────────────┐
Trả thẳng từ đĩa                │ Gunicorn (Port 8000)│
                                └─────────┬─────────┘
                                          │ frappe.init(site)
                                          ▼
                                ┌───────────────────┐
                                │   Frappe ORM      │
                                └────┬────┬────┬────┘
                                     │    │    │
            ┌────────────────────────┘    │    └───────────────────────┐
            ▼                             ▼                            ▼
   ┌─────────────────┐           ┌─────────────────┐          ┌─────────────────┐
   │   Redis Cache   │           │   Redis Queue   │          │ MariaDB Schema  │
   │ DocType & Perms │           │  (RQ Job Push)  │          │  tab[DocType]   │
   └─────────────────┘           └────────┬────────┘          └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │   RQ Workers    │
                                 │ (short/def/long)│
                                 └─────────────────┘
```

1. **Phân tách tĩnh - động tại Nginx:** Nginx kiểm tra URI. Nếu là ảnh, CSS, JS (`/assets/*`, `/files/*`), Nginx trả về ngay lập tức với tốc độ mili-giây mà không đánh thức tiến trình Python.
2. **Giao tiếp WSGI Gunicorn:** Các yêu cầu dữ liệu hoặc giao diện Desk được chuyển tới Gunicorn. Gunicorn gọi `frappe.app.application`, nạp đúng database của Site tương ứng qua HTTP Host Header.
3. **Bộ 3 Cụm Redis (Redis Triad):**
   * **Redis Cache:** Nạp toàn bộ metadata của DocType và phân quyền người dùng vào RAM. Nhờ đó, việc kiểm tra quyền truy cập không phải thực hiện các câu lệnh `SELECT` xuống ổ cứng.
   * **Redis Queue:** Nhận các tác vụ tính toán lớn, gửi email hoặc đồng bộ CSDL từ web worker để chuyển tiếp cho Background Workers.
   * **Redis SocketIO:** Kênh Pub/Sub kết nối với Node.js để bắn thông báo chuông (Bell Notification) hoặc khóa tài liệu khi có 2 người cùng mở 1 form.
4. **Hàng đợi RQ Workers:** Chạy thường trực dưới nền theo 3 luồng: `short` (dưới 5 phút), `default` và `long` (các tác vụ nặng hàng giờ).

---

## PHẦN 3: DOCTYPE LÀ GÌ? DÙNG ĐỂ LÀM GÌ? KẾT NỐI VỚI CƠ SỞ DỮ LIỆU NHƯ THẾ NÀO?

### 3.1. DocType Là Gì?
Trong Frappe Framework, **DocType (Document Type)** là khái niệm trung tâm quan trọng nhất. 
> **"DocType is the Single Source of Truth"** (DocType là nguồn chân lý duy nhất).

DocType là một khối **Siêu dữ liệu (Metadata)** đặc tả toàn bộ vòng đời của một thực thể nghiệp vụ:
* Nó vừa là **Schema CSDL** (mô tả bảng và các cột).
* Nó vừa là **Giao diện nhập liệu (UI Form & List View)**.
* Nó vừa là **Quy tắc bảo mật & phân quyền (Role-Based Access Control)**.
* Nó vừa là **Đặc tả REST API**.

### 3.2. DocType Dùng Để Làm Gì?
Thay vì kiến trúc truyền thống nơi lập trình viên phải:
1. Viết mã tạo bảng SQL (`CREATE TABLE`).
2. Viết class Model ORM.
3. Viết Form nhập liệu HTML/JS.
4. Viết các hàm Controller CRUD.
5. Viết Endpoint REST API và code phân quyền.

👉 **Với Frappe DocType:** Bạn chỉ cần định nghĩa các trường dữ liệu một lần duy nhất trong giao diện Desk (hoặc file JSON). Frappe Framework sẽ tự động sinh ra toàn bộ 5 thành phần trên!

### 3.3. DocType Kết Nối Với Cơ Sở Dữ Liệu MariaDB Như Thế Nào?

#### A. Quy Tắc Ánh Xạ Bảng (Table Mapping)
Mỗi DocType được lưu thành một bảng vật lý trong MariaDB theo cú pháp:
$$\text{Tên Bảng} = \mathbf{tab} + \text{Tên DocType}$$

* *Ví dụ:*
  * DocType `User` ➔ Bảng `tabUser`
  * DocType `Purchase Order` ➔ Bảng `tabPurchase Order`
  * DocType `Item` ➔ Bảng `tabItem`

#### B. Ánh Xạ Kiểu Dữ Liệu (Fieldtype Mapping)

| Kiểu Trường Trong DocType | Kiểu Cột Vật Lý Trong MariaDB | Ghi Chú Kỹ Thuật |
| :--- | :--- | :--- |
| **Data, Select, Dynamic Link** | `VARCHAR(140)` hoặc `VARCHAR(255)` | Chuỗi văn bản một dòng, lựa chọn danh sách cố định |
| **Link** | `VARCHAR(140)` | **Khóa ngoại logic**. Lưu trường `name` của DocType được trỏ tới. Frappe kiểm tra tính toàn vẹn ở tầng ứng dụng. |
| **Int, Check** | `INT(11)` | Số nguyên, ô chọn boolean (0 hoặc 1). |
| **Currency, Float, Percent** | `DECIMAL(21, 9)` | Độ chính xác dấu phẩy động tài chính, chống sai số làm tròn tiền tệ. |
| **Date / Datetime / Time** | `DATE` / `DATETIME(6)` / `TIME(6)` | Thời gian có độ chính xác đến micro-giây. |
| **Text, Small Text, Code** | `TEXT` / `LONGTEXT` | Khối văn bản dài, ghi chú, mã JSON, mã script. |
| **Table (Bảng con - Child Table)** | Tạo bảng riêng: `tab[Child DocType]` | Bảng chi tiết liên kết với cha bằng 3 cột: `parent`, `parentfield`, `parenttype`. |

#### C. 7 Cột Hệ Thống Luôn Được Tự Động Tạo
Trong bất kỳ bảng `tab[DocType]` nào, Frappe luôn tạo sẵn 7 cột quản trị hệ thống:
1. `name` (`VARCHAR(140)`): Khóa chính (**PRIMARY KEY**), định danh duy nhất của bản ghi (vd: `PO-2026-0001`).
2. `creation` (`DATETIME(6)`): Thời điểm bản ghi được tạo lần đầu.
3. `modified` (`DATETIME(6)`): Thời điểm cập nhật bản ghi gần nhất.
4. `modified_by` (`VARCHAR(140)`): Email người sửa đổi gần nhất.
5. `owner` (`VARCHAR(140)`): Email người khởi tạo bản ghi.
6. `docstatus` (`INT(1)`): Trạng thái chứng từ:
   * **0 (Draft):** Bản nháp, có thể sửa hoặc xóa tự do.
   * **1 (Submitted):** Đã duyệt, khóa dữ liệu, ghi sổ cái kế toán/kho, không được sửa trực tiếp.
   * **2 (Cancelled):** Đã hủy bỏ, chứng từ bị vô hiệu hóa nhưng vẫn giữ vết kiểm toán (Audit Trail).
7. `idx` (`INT(8)`): Thứ tự sắp xếp hiển thị của dòng trong danh sách hoặc bảng con.

---

## PHẦN 4: SƠ ĐỒ TOÀN DIỆN VỀ VÒNG ĐỜI & CÁCH HOẠT ĐỘNG CỦA DOCTYPE

Một DocType được vận hành bởi sự kết hợp của 4 tệp tin trong cấu trúc thư mục ứng dụng:

```text
apps/[app_name]/[app_name]/[module]/doctype/[doctype_name]/
├── [doctype_name].json       # 1. Định nghĩa Metadata (Schema, UI layout, Perms)
├── [doctype_name].py         # 2. Server Controller (Xử lý logic nghiệp vụ Python)
├── [doctype_name].js         # 3. Client Controller (Giao diện Desk UI, tương tác JS)
└── test_[doctype_name].py    # 4. Kiểm thử tự động (Unit Tests)
```

### Vòng Đời Sự Kiện (Document Lifecycle Event Hooks)

Khi một bản ghi được thao tác từ giao diện Web, REST API hoặc mã Python (`doc.insert()`, `doc.save()`, `doc.submit()`), Frappe kích hoạt chuỗi sự kiện theo đúng thứ tự sau:

```
[Khởi Tạo] ──────► [Kiểm Tra Hợp Lệ] ──────► [Ghi Vào CSDL] ──────► [Phê Duyệt] ──────► [Lưu Đĩa]
__init__()          validate()                before_insert()        before_submit()     frappe.db.commit()
onload()            before_save()             on_update()            on_submit()
(Nạp RAM)          (Chặn dữ liệu sai)        (Chạy SQL INSERT)      (Ghi sổ cái)        (Ghi vĩnh viễn)
```

1. **Giai đoạn Kiểm Tra (`validate` & `before_save`):**
   * Được lập trình viên sử dụng nhiều nhất trong file `.py`.
   * Kiểm tra điều kiện nghiệp vụ (ví dụ: Số lượng đặt hàng có vượt tồn kho không? Ngày kết thúc có trước ngày bắt đầu không?).
   * Tự động tính toán các trường công thức (ví dụ: `grand_total = subtotal + tax`).
2. **Giai đoạn Ghi CSDL (`before_insert` & `on_update`):**
   * Frappe dịch cấu trúc Object thành câu lệnh `INSERT INTO tab...` hoặc `UPDATE tab...` và gửi xuống MariaDB thông qua C-Extension `mysqlclient`.
3. **Giai đoạn Phê Duyệt (`on_submit`):**
   * Chỉ áp dụng cho các DocType có bật tính năng `is_submittable = 1` (như Hóa đơn, Đơn đặt hàng, Phiếu xuất kho).
   * Chuyển trạng thái `docstatus` từ `0` lên `1`.
   * Kích hoạt ghi sổ kế toán (General Ledger) và sổ kho (Stock Ledger).
4. **Cam kết giao dịch (`frappe.db.commit`):**
   * Hoàn tất giao dịch ACID. Dữ liệu ghi an toàn xuống ổ đĩa.
   * Nếu có bất kỳ lỗi Python nào xảy ra trong chuỗi trên, Frappe tự động gọi `frappe.db.rollback()` để hủy toàn bộ thay đổi, giữ cho hệ thống không bao giờ bị rác hoặc mất đồng bộ.

---

*Tài liệu kỹ thuật được chuẩn hóa cho hệ sinh thái Frappe Framework & ERPNext.*
