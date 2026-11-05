import frappe
from frappe.utils.password import update_password
from frappe.core.doctype.user.user import generate_keys

def main():
    frappe.init('frontend')
    frappe.connect()
    
    frappe.set_user('Administrator')

    company = frappe.defaults.get_global_default('company') or 'nhom4-httt'

    print("==========================================================")
    print(" BẮT ĐẦU CẤU HÌNH VAI TRÒ VÀ NGƯỜI DÙNG CHO ERPNEXT")
    print("==========================================================")

    # 1. DANH SÁCH VAI TRÒ CẦN TẠO
    custom_roles = [
        {"role_name": "Thu ngân", "desk_access": 1},
        {"role_name": "Thủ kho", "desk_access": 1},
        {"role_name": "Nhân viên mua hàng", "desk_access": 1},
        {"role_name": "Quản lý bếp", "desk_access": 1},
        {"role_name": "Quản lý chuỗi", "desk_access": 1},
        {"role_name": "Tài khoản dịch vụ AI", "desk_access": 1},
    ]

    for r in custom_roles:
        if not frappe.db.exists("Role", r["role_name"]):
            role_doc = frappe.new_doc("Role")
            role_doc.role_name = r["role_name"]
            role_doc.desk_access = r["desk_access"]
            role_doc.insert(ignore_permissions=True)
            print(f"[+] Đã tạo Role: {r['role_name']}")
        else:
            print(f"[=] Role đã tồn tại: {r['role_name']}")

    # 2. PHÂN QUYỀN VAI TRÒ (Gán Standard Roles kết hợp Custom Role)
    # 3. DANH SÁCH NGƯỜI DÙNG THEO TỪNG VAI TRÒ
    users_data = [
        {
            "email": "thungan.hanoi@erpnet.vn",
            "first_name": "Nguyễn Thị",
            "last_name": "Thu Ngân",
            "roles": ["Thu ngân", "Sales User", "Accounts User"],
            "user_permission": {
                "allow": "Warehouse",
                "for_value": "Kho Hà Nội - Cầu Giấy - N4"
            },
            "desc": "Thu ngân tại quầy (Giới hạn bán tại Kho Cầu Giấy)"
        },
        {
            "email": "thukho.hanoi@erpnet.vn",
            "first_name": "Trần Văn",
            "last_name": "Thủ Kho",
            "roles": ["Thủ kho", "Stock User"],
            "user_permission": {
                "allow": "Warehouse",
                "for_value": "Khu vực Hà Nội - N4"
            },
            "desc": "Thủ kho quản lý xuất nhập tồn khu vực Hà Nội"
        },
        {
            "email": "muahang@erpnet.vn",
            "first_name": "Lê Thị",
            "last_name": "Mua Hàng",
            "roles": ["Nhân viên mua hàng", "Purchase User", "Stock User"],
            "desc": "Nhân viên lập kế hoạch & gửi đơn mua hàng tới nhà cung cấp"
        },
        {
            "email": "quanlybep@erpnet.vn",
            "first_name": "Phạm Văn",
            "last_name": "Quản Lý Bếp",
            "roles": ["Quản lý bếp", "Manufacturing User", "Stock User"],
            "desc": "Bếp trưởng / Quản lý chế biến & định mức nguyên vật liệu (BOM)"
        },
        {
            "email": "quanlychuoi@erpnet.vn",
            "first_name": "Hoàng Văn",
            "last_name": "Quản Lý Chuỗi",
            "roles": ["Quản lý chuỗi", "Stock Manager", "Purchase Manager", "Sales Manager", "Accounts Manager", "Report Manager"],
            "desc": "Giám đốc vận hành chuỗi bán lẻ toàn quốc (3 miền)"
        },
        {
            "email": "ai_service@erpnet.vn",
            "first_name": "AI Service",
            "last_name": "Account",
            "roles": ["Tài khoản dịch vụ AI", "System Manager"],
            "is_service_account": True,
            "desc": "Tài khoản dịch vụ cho AI Agent kết nối qua REST API"
        }
    ]

    default_password = "User@12345"
    ai_keys = {}

    for u in users_data:
        email = u["email"]
        if not frappe.db.exists("User", email):
            user_doc = frappe.new_doc("User")
            user_doc.email = email
            user_doc.first_name = u["first_name"]
            user_doc.last_name = u.get("last_name", "")
            user_doc.send_welcome_email = 0
            user_doc.user_type = "System User"
            
            for r in u["roles"]:
                user_doc.append("roles", {"role": r})
            
            user_doc.insert(ignore_permissions=True)
            update_password(email, default_password)
            print(f"[+] Đã tạo User: {email} | Vai trò: {', '.join(u['roles'])}")
        else:
            user_doc = frappe.get_doc("User", email)
            existing_roles = [r.role for r in user_doc.roles]
            for r in u["roles"]:
                if r not in existing_roles:
                    user_doc.append("roles", {"role": r})
            user_doc.save(ignore_permissions=True)
            update_password(email, default_password)
            print(f"[=] User đã tồn tại (đã cập nhật vai trò): {email}")

        # 4. CẤU HÌNH USER PERMISSION (Phân quyền theo đối tượng)
        if "user_permission" in u:
            perm = u["user_permission"]
            allow_doctype = perm["allow"]
            for_value = perm["for_value"]
            
            # Kiểm tra xem đối tượng có tồn tại không
            if frappe.db.exists(allow_doctype, for_value):
                if not frappe.db.exists("User Permission", {"user": email, "allow": allow_doctype, "for_value": for_value}):
                    up = frappe.new_doc("User Permission")
                    up.user = email
                    up.allow = allow_doctype
                    up.for_value = for_value
                    up.is_default = 1
                    up.apply_to_all_doctypes = 1
                    up.insert(ignore_permissions=True)
                    print(f"    [->] Gán User Permission: {email} chỉ được xem {allow_doctype} = '{for_value}'")
                else:
                    print(f"    [=] User Permission đã có sẵn: {allow_doctype} = '{for_value}'")

        # 5. KHỞI TẠO KHÓA API CHO TÀI KHOẢN DỊCH VỤ AI
        if u.get("is_service_account"):
            keys = generate_keys(email)
            ai_keys = {
                "server_url": "http://localhost:8080",
                "user": email,
                "api_key": keys["api_key"],
                "api_secret": keys["api_secret"]
            }
            print(f"    [KEY] Tạo khóa API cho AI Service Account:")
            print(f"          API Key:    {keys['api_key']}")
            print(f"          API Secret: {keys['api_secret']}")

    frappe.db.commit()

    # Ghi khóa API ra file json ngoài thư mục làm việc để sau này AI Agent dùng
    import json
    with open("/home/frappe/frappe-bench/sites/ai_agent_credentials.json", "w") as f:
        json.dump(ai_keys, f, indent=4)

    print("\n==========================================================")
    print(" HOÀN TẤT THIẾT LẬP VAI TRÒ VÀ NGƯỜI DÙNG!")
    print(f" Mật khẩu chung cho tất cả các tài khoản mẫu: {default_password}")
    print("==========================================================")

if __name__ == '__main__':
    main()
