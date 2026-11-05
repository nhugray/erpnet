# ERPNext Local Project

Dự án ERPNext chạy cục bộ trên môi trường Docker (Frappe Docker) cùng mã nguồn ứng dụng ERPNext và tập lệnh khởi tạo dữ liệu mẫu.

---

## 1. Thông tin truy cập hệ thống

* **Địa chỉ:** [http://localhost:8080](http://localhost:8080)
* **Tài khoản:** `Administrator`
* **Mật khẩu:** `admin`

---

## 2. Hướng dẫn chạy & dừng hệ thống

### Cách 1: Sử dụng các tệp kịch bản (1-Click)
* **Khởi động:** Bấm đúp vào tệp `Chay_ERPNext.bat` (hoặc phím tắt *Start ERPNext* trên Desktop).
* **Dừng:** Bấm đúp vào tệp `Dung_ERPNext.bat` (hoặc phím tắt *Stop ERPNext* trên Desktop).

### Cách 2: Sử dụng dòng lệnh (Docker Compose)
* **Khởi động:**
  ```powershell
  cd frappe_docker
  docker compose -f pwd.yml up -d
  ```
* **Dừng:**
  ```powershell
  cd frappe_docker
  docker compose -f pwd.yml stop
  ```

---

## 3. Cấu trúc thư mục

* `erpnext/`: Mã nguồn ứng dụng ERPNext (DocTypes, modules, APIs).
* `frappe_docker/`: Cấu hình Docker Compose để triển khai ERPNext, MariaDB 11.8, Redis, Socket.IO.
* `create_sample_warehouses.py`: Kịch bản Python tự động khởi tạo dữ liệu 9 kho mẫu tại 3 khu vực (Hà Nội, Đà Nẵng, TP. Hồ Chí Minh).
* `Chay_ERPNext.bat` & `Dung_ERPNext.bat`: Tệp lệnh khởi động và dừng nhanh hệ thống.
