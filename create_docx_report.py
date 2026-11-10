import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout_box(doc, title, text, bg_color="FFFBEB", border_color="F59E0B", icon="👉"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    r_icon = p.add_run(f"{icon} {title}: ")
    r_icon.bold = True
    r_icon.font.name = "Calibri"
    r_icon.font.size = Pt(10.5)
    r_icon.font.color.rgb = RGBColor(146, 64, 14)
    
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = RGBColor(30, 41, 59)
    
    # spacing after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_image_with_caption(doc, img_path, caption, width=Inches(6.4)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(f"Hình: {caption}")
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(100, 116, 139)

def build_document():
    doc = Document()
    
    # Set standard margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    img_dir = r"c:\Users\ASUS\Downloads\erpnet\slide_images"
    
    # ----------------------------------------------------
    # DOCUMENT HEADER / TITLE BLOCK
    # ----------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    run_pre = p_title.add_run("TÀI LIỆU KỸ THUẬT HỆ THỐNG THÔNG TIN DOANH NGHIỆP\n")
    run_pre.font.name = "Calibri"
    run_pre.font.size = Pt(10.5)
    run_pre.font.bold = True
    run_pre.font.color.rgb = RGBColor(2, 132, 199)
    
    run_title = p_title.add_run("Kiến Trúc Toàn Diện Frappe Framework, Frappe Bench & DocType")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(2)
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run("Phân tích giải phẫu 6 tầng kiến trúc: Từ lớp điều phối môi trường (Bench), nền tảng lập trình (Frappe), viên gạch siêu dữ liệu (DocType), thực thể đa người thuê (Site), hệ sinh thái gói phần mềm (App) đến giải pháp ERP nghiệp vụ (ERPNext).")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11)
    run_sub.font.color.rgb = RGBColor(71, 85, 105)
    
    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(14)
    r_div = p_div.add_run("―" * 55)
    r_div.font.color.rgb = RGBColor(226, 232, 240)
    
    # ----------------------------------------------------
    # 1. BENCH — LỚP ĐIỀU PHỐI MÔI TRƯỜNG
    # ----------------------------------------------------
    h1 = doc.add_heading("1. Bench — Lớp Điều Phối Môi Trường", level=1)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)
    for run in h1.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        
    p1 = doc.add_paragraph()
    p1.paragraph_format.line_spacing = 1.15
    p1.paragraph_format.space_after = Pt(6)
    p1.add_run("• ").bold = True
    p1.add_run("Là gì: ").bold = True
    p1.add_run("Frappe Bench vừa là một công cụ dòng lệnh (Command Line Interface - CLI), vừa là một thư mục chuẩn hóa quy chuẩn chứa toàn bộ môi trường chạy và không gian làm việc của hệ thống.\n")
    p1.add_run("• ").bold = True
    p1.add_run("Vai trò: ").bold = True
    p1.add_run("Quản lý vòng đời mọi thứ trong hệ thống — từ việc tạo site mới, cài đặt app, chạy WSGI web server, background worker, scheduler, thiết lập kết nối MariaDB/Redis, đồng bộ mã nguồn qua Git đến sao lưu và phục hồi dữ liệu.")
    
    # Slide 1 image
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_1.png"),
        "Sơ đồ 3 trụ cột của Frappe Bench (CLI Tool, Workspace Manager, Process Orchestrator)"
    )
    
    p_cols = doc.add_paragraph()
    p_cols.paragraph_format.line_spacing = 1.15
    p_cols.paragraph_format.space_after = Pt(6)
    p_cols.add_run("Bench được thiết kế vững chắc trên 3 trụ cột độc lập:\n")
    p_cols.add_run("1. CLI Tool: ").bold = True
    p_cols.add_run("Cung cấp tập lệnh điều khiển mạnh mẽ (bench migrate, bench execute, bench backup) giúp tự động hóa vận hành.\n")
    p_cols.add_run("2. Workspace Manager: ").bold = True
    p_cols.add_run("Quản lý cô lập không gian mã nguồn (apps/), các phân vùng dữ liệu site (sites/) và môi trường ảo Python cách ly (env/).\n")
    p_cols.add_run("3. Process Orchestrator: ").bold = True
    p_cols.add_run("Tự động cấu hình và giám sát máy chủ Nginx, WSGI Gunicorn, hàng đợi RQ Workers, Scheduler và 3 cụm Redis.")
    
    # Slide 2 image (Overview 5-layer diagram)
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_2.png"),
        "Kiến trúc hạ tầng tổng quan 5 tầng của Frappe Bench (Từ *nix OS Layer đến Viewing IO Interface)"
    )
    
    p_infra = doc.add_paragraph()
    p_infra.paragraph_format.line_spacing = 1.15
    p_infra.paragraph_format.space_after = Pt(6)
    p_infra.add_run("Kiến trúc hạ tầng tổng quan (như thể hiện trong sơ đồ chuẩn trên) được chia thành 5 phân tầng kỹ thuật:\n")
    p_infra.add_run("• Tầng Hệ Điều Hành (*nix OS Layer) & Dependencies: ").bold = True
    p_infra.add_run("Chạy trên Linux/macOS/Docker, tận dụng phân quyền POSIX và socket, với các nền tảng phụ thuộc là GIT, Python và PIP.\n")
    p_infra.add_run("• Tầng Công Cụ (bench) & Prerequisites: ").bold = True
    p_infra.add_run("Cài qua `pip install frappe-bench`, tự động kết nối và điều khiển 5 dịch vụ nền: MariaDB, Node.js, Nginx, Wkhtmltopdf và Fail2ban.\n")
    p_infra.add_run("• Tầng Ba Khối Trung Tâm: ").bold = True
    p_infra.add_run("Configuration Layer (sinh tệp cấu hình tự động), Multi-Tenant Layer (quản lý các bench-instance chứa sites và apps), và Scheduling Layer (ma trận jobs chạy ngầm).\n")
    p_infra.add_run("• Tầng Trên Cùng: ").bold = True
    p_infra.add_run("Viewing IO Interface (Desk UI Desktop & Mobile) kết nối với Request Queue để điều phối yêu cầu HTTP và tác vụ định kỳ.")
    
    # Slide 3 image (Runtime space)
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_3.png"),
        "Không gian làm việc và tiến trình Runtime bên trong Frappe Bench (/home/frappe/frappe-bench)"
    )
    
    p_struct = doc.add_paragraph()
    p_struct.paragraph_format.line_spacing = 1.15
    p_struct.paragraph_format.space_after = Pt(6)
    p_struct.add_run("• ").bold = True
    p_struct.add_run("Cấu trúc thư mục xương sống:\n").bold = True
    p_struct.add_run("  - apps/: ").bold = True
    p_struct.add_run("Chứa mã nguồn của toàn bộ các ứng dụng (frappe, erpnext, custom_app).\n")
    p_struct.add_run("  - sites/: ").bold = True
    p_struct.add_run("Vùng dữ liệu đa người thuê, chứa cấu hình site_config.json, file đính kèm public/private của từng tenant.\n")
    p_struct.add_run("  - env/: ").bold = True
    p_struct.add_run("Môi trường ảo Python Virtualenv cô lập hoàn toàn các thư viện phụ thuộc.\n")
    p_struct.add_run("  - config/ & logs/: ").bold = True
    p_struct.add_run("Nơi lưu các file cấu hình tự sinh (nginx.conf, supervisor.conf) và nhật ký vận hành.")
    
    # Slide 4 image (Directory breakdown)
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_4.png"),
        "Giải phẫu chi tiết cấu trúc thư mục frappe-bench"
    )
    
    p_cmds = doc.add_paragraph()
    p_cmds.paragraph_format.line_spacing = 1.15
    p_cmds.paragraph_format.space_after = Pt(6)
    p_cmds.add_run("• ").bold = True
    p_cmds.add_run("Lệnh tiêu biểu trong thực tế:\n").bold = True
    p_cmds.add_run("  - bench start: ").bold = True
    p_cmds.add_run("Khởi động đồng thời tất cả tiến trình (Web, Redis, Worker, Scheduler).\n")
    p_cmds.add_run("  - bench new-site [site]: ").bold = True
    p_cmds.add_run("Tạo một site mới, cấp phát cơ sở dữ liệu MariaDB riêng biệt.\n")
    p_cmds.add_run("  - bench get-app [repo_url]: ").bold = True
    p_cmds.add_run("Tải mã nguồn app từ Git và cài vào môi trường ảo env/.\n")
    p_cmds.add_run("  - bench --site [site] install-app [app]: ").bold = True
    p_cmds.add_run("Cài đặt và di trú bảng dữ liệu của app vào site chỉ định.\n")
    p_cmds.add_run("  - bench --site [site] migrate: ").bold = True
    p_cmds.add_run("Đồng bộ định nghĩa DocType mới nhất vào các bảng CSDL.")
    
    add_callout_box(
        doc,
        "Ý tưởng cốt lõi cho sinh viên",
        "Bench là 'người quản gia' — bản thân Bench không chứa logic nghiệp vụ bán hàng hay kế toán nào, nhiệm vụ của nó là điều phối và cung cấp môi trường sống lý tưởng cho các ứng dụng vận hành.",
        bg_color="FEF3C7",
        border_color="D97706",
        icon="👉"
    )
    
    # ----------------------------------------------------
    # 2. FRAPPE FRAMEWORK — NỀN TẢNG LẬP TRÌNH
    # ----------------------------------------------------
    h2 = doc.add_heading("2. Frappe Framework — Nền Tảng Lập Trình", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    for run in h2.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        
    p2 = doc.add_paragraph()
    p2.paragraph_format.line_spacing = 1.15
    p2.paragraph_format.space_after = Pt(6)
    p2.add_run("• ").bold = True
    p2.add_run("Là gì: ").bold = True
    p2.add_run("Frappe Framework là một web framework full-stack mã nguồn mở (Backend bằng Python, Frontend bằng JavaScript/Desk UI) phát triển theo triết lý hướng siêu dữ liệu (metadata-driven) và low-code.\n")
    p2.add_run("• ").bold = True
    p2.add_run("Vai trò: ").bold = True
    p2.add_run("Cung cấp sẵn toàn bộ các thành phần hạ tầng mà một hệ thống doanh nghiệp cần: Python ORM, tự sinh REST API, hệ thống phân quyền đa cấp theo vai trò (Role-Based Access Control) và đối tượng (User Permissions), giao diện bàn làm việc (Desk UI), quy trình duyệt (Workflow), trình tạo báo cáo (Report Builder), background scheduler và email gateway.\n")
    p2.add_run("• ").bold = True
    p2.add_run("Điểm mấu chốt: ").bold = True
    p2.add_run("ERPNext được xây dựng 100% dựa trên Frappe Framework. Frappe đóng vai trò xây dựng 'khung xương kỹ thuật', còn ERPNext chỉ đơn thuần khai báo thêm các 'DocType nghiệp vụ' (như Hóa đơn, Đơn đặt hàng, Sổ cái kế toán).")
    
    # Slide 5 image (Runtime Lifecycle)
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_5.png"),
        "Vòng đời hoạt động (Runtime Lifecycle) xử lý yêu cầu của Frappe Framework"
    )
    
    p_life = doc.add_paragraph()
    p_life.paragraph_format.line_spacing = 1.15
    p_life.paragraph_format.space_after = Pt(6)
    p_life.add_run("Mọi yêu cầu tương tác qua Frappe Framework đều trải qua chuỗi vòng đời 4 bước nghiêm ngặt:\n")
    p_life.add_run("1. Định danh Site & Khởi tạo ngữ cảnh (frappe.init): ").bold = True
    p_life.add_run("Xác định site qua HTTP Host header hoặc tham số CLI, nạp site_config.json và khởi tạo biến luồng frappe.local.\n")
    p_life.add_run("2. Mở kết nối CSDL & Nạp Cache (frappe.connect): ").bold = True
    p_life.add_run("Mở connection pool tới CSDL MariaDB riêng của site và truy xuất metadata siêu tốc từ Redis Cache.\n")
    p_life.add_run("3. Thực thi ORM & Hooks (DocType Controller): ").bold = True
    p_life.add_run("Xử lý dữ liệu qua chuỗi validate() ➔ before_save() ➔ on_submit(). Đẩy các việc nặng vào Redis Queue.\n")
    p_life.add_run("4. Cam kết giao dịch & Giải phóng tài nguyên (frappe.destroy): ").bold = True
    p_life.add_run("Gọi frappe.db.commit() ghi đĩa an toàn (hoặc rollback() nếu lỗi), bảo toàn nguyên vẹn dữ liệu chuẩn ACID.")
    
    add_callout_box(
        doc,
        "So sánh trực quan",
        "Mối quan hệ giữa Frappe và ERPNext giống hệt như Django và một Website viết bằng Django. Tuy nhiên, Frappe vượt trội hơn ở chỗ nó tích hợp sẵn giao diện quản trị Admin Desk, hệ thống phân quyền và API tự sinh mà không cần lập trình viên phải tự viết template HTML.",
        bg_color="EFF6FF",
        border_color="2563EB",
        icon="⚖️"
    )
    
    # ----------------------------------------------------
    # 3. DOCTYPE — VIÊN GẠCH CƠ BẢN CỦA HỆ THỐNG
    # ----------------------------------------------------
    h3 = doc.add_heading("3. DocType — Viên Gạch Cơ Bản Của Hệ Thống", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)
    for run in h3.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        
    p3 = doc.add_paragraph()
    p3.paragraph_format.line_spacing = 1.15
    p3.paragraph_format.space_after = Pt(6)
    p3.add_run("• ").bold = True
    p3.add_run("Là gì: ").bold = True
    p3.add_run("DocType (Document Type) là đơn vị mô hình dữ liệu căn bản nhất trong Frappe. Một DocType định nghĩa đồng thời 4 yếu tố: Bảng trong CSDL MariaDB + Màn hình Form/List nhập liệu + Bộ điều khiển logic nghiệp vụ (Python/JS) + Ma trận phân quyền RBAC.\n")
    p3.add_run("• ").bold = True
    p3.add_run("Đặc biệt: ").bold = True
    p3.add_run("Triết lý 'Everything in Frappe is a DocType' (Tất cả mọi thứ đều là DocType). Kể cả bản thân thực thể 'DocType' cũng được quản lý như một DocType (tính chất siêu hình học - metadata). Từ Customer, Supplier, Sales Invoice, User đến Role, Permission... tất cả đều là các DocType.")
    
    # Slide 6 image (DocType overview)
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_6.png"),
        "Bản chất cốt lõi, mục đích sử dụng và cơ chế kết nối CSDL của DocType"
    )
    
    p_comp = doc.add_paragraph()
    p_comp.paragraph_format.line_spacing = 1.15
    p_comp.paragraph_format.space_after = Pt(6)
    p_comp.add_run("• ").bold = True
    p_comp.add_run("Các thành phần cấu thành nên một DocType:\n").bold = True
    p_comp.add_run("  - Fields (Trường dữ liệu): ").bold = True
    p_comp.add_run("Định nghĩa các cột thông tin (Data, Int, Currency, Date, Text...).\n")
    p_comp.add_run("  - Links (Khóa ngoại logic): ").bold = True
    p_comp.add_run("Liên kết quan hệ giữa các DocType mà không phụ thuộc vào ràng buộc cứng của database engine.\n")
    p_comp.add_run("  - Child Table (Bảng con): ").bold = True
    p_comp.add_run("Chứa các dòng chi tiết danh mục hàng hóa (liên kết với cha bằng parent, parentfield, parenttype).\n")
    p_comp.add_run("  - Naming Series: ").bold = True
    p_comp.add_run("Quy tắc sinh mã tự động cho chứng từ (ví dụ: PO-.YYYY.-.#####).\n")
    p_comp.add_run("  - Permissions: ").bold = True
    p_comp.add_run("Quy định cụ thể Role nào được quyền Đọc, Viết, Tạo, Nộp duyệt, Hủy bỏ.\n")
    p_comp.add_run("  - Server Script & Client Script: ").bold = True
    p_comp.add_run("Code Python kiểm tra tính hợp lệ ở backend và code JS tăng cường trải nghiệm ở giao diện Desk.")
    
    # Slide 7 image (DocType architecture part 1)
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_7.png"),
        "Sơ đồ tổng quan kiến trúc DocType trong Frappe Framework (File định nghĩa, Metadata gốc, Phân loại, CSDL MariaDB và Redis Cache)"
    )
    
    p_arch1 = doc.add_paragraph()
    p_arch1.paragraph_format.line_spacing = 1.15
    p_arch1.paragraph_format.space_after = Pt(6)
    p_arch1.add_run("Phân tích chuyên sâu sơ đồ DocType (Hình trên):\n")
    p_arch1.add_run("1. File định nghĩa trong app: ").bold = True
    p_arch1.add_run("Mỗi DocType gồm bộ 4 tệp ([doctype].json đặc tả schema, [doctype].py xử lý server, [doctype].js xử lý form client, test_[doctype].py kiểm thử).\n")
    p_arch1.add_run("2. Ba DocType gốc (Metadata): ").bold = True
    p_arch1.add_run("Hệ thống khởi nguồn từ 3 hạt nhân: DocType (định nghĩa thực thể), DocField (định nghĩa trường), DocPerm (định nghĩa quyền).\n")
    p_arch1.add_run("3. Phân loại DocType: ").bold = True
    p_arch1.add_run("Gồm Standard (bảng riêng), Child Table (nằm trong cha), Single (bảng 1 dòng lưu cài đặt), Submittable (chứng từ có luồng duyệt), Tree (cấu trúc phân cấp cha con), và Custom (tạo nhanh trên giao diện).\n")
    p_arch1.add_run("4. Cơ sở dữ liệu MariaDB: ").bold = True
    p_arch1.add_run("Mỗi site một CSDL riêng; bảng thực thể có tiền tố `tab[DocType]`, bảng con `tab[Child DocType]`, và bảng `tabSingles`.\n")
    p_arch1.add_run("5. Redis Cache: ").bold = True
    p_arch1.add_run("Nạp siêu dữ liệu (metadata) vào RAM qua hàm frappe.get_meta() để tăng tốc xử lý và tự xóa cache khi sửa cấu trúc.")
    
    # Slide 8 image (DocType architecture part 2)
    add_image_with_caption(
        doc,
        os.path.join(img_dir, "slide_8.png"),
        "Sơ đồ vòng đời Document, trạng thái docstatus, quyền hạn, giao diện tự sinh và quan hệ giữa các DocType"
    )
    
    p_arch2 = doc.add_paragraph()
    p_arch2.paragraph_format.line_spacing = 1.15
    p_arch2.paragraph_format.space_after = Pt(6)
    p_arch2.add_run("Cơ chế vận hành và vòng đời DocType (Hình trên):\n")
    p_arch2.add_run("6. Vòng đời Document (.py): ").bold = True
    p_arch2.add_run("Chuỗi hooks tự động kích hoạt: before_insert ➔ validate ➔ before_save ➔ on_update ➔ before_submit ➔ on_submit ➔ on_cancel ➔ on_trash.\n")
    p_arch2.add_run("7. Trạng thái docstatus: ").bold = True
    p_arch2.add_run("0 = Bản nháp (Draft), 1 = Đã nộp/duyệt (Submitted - khóa sửa trực tiếp), 2 = Đã hủy (Cancelled - cho phép tạo bản sao sửa đổi Amend).\n")
    p_arch2.add_run("8. Quyền và mở rộng: ").bold = True
    p_arch2.add_run("Kết hợp Role + DocPerm, User Permission (giới hạn theo kho/công ty), Workflow nhiều cấp duyệt, và hooks.py gắn logic chéo.\n")
    p_arch2.add_run("9. Giao diện và API tự sinh: ").bold = True
    p_arch2.add_run("Tự sinh Form view nhập liệu, List view danh sách, Report view báo cáo tổng hợp, bản in Print Format và các endpoint REST API chuẩn.\n")
    p_arch2.add_run("10. Quan hệ giữa các DocType: ").bold = True
    p_arch2.add_run("Liên kết Link 1-nhiều (Quotation ➔ Customer), quan hệ bảng con 1-nhiều (Quotation ➔ Quotation Item), và Dynamic Link linh hoạt.")
    
    add_callout_box(
        doc,
        "Ý tưởng cốt lõi cho sinh viên",
        "Hiểu được DocType chính là hiểu được bí mật lớn nhất của Frappe: Cách hệ thống biến một định nghĩa dữ liệu thuần túy (file JSON) thành một ứng dụng web hoàn chỉnh, có bảng CSDL, form nhập liệu, bảo mật và API mà lập trình viên gần như không cần viết một dòng SQL hay HTML nào.",
        bg_color="FEF3C7",
        border_color="D97706",
        icon="👉"
    )
    
    # ----------------------------------------------------
    # 4. SITE — THỰC THỂ VẬN HÀNH (MULTI-TENANT)
    # ----------------------------------------------------
    h4 = doc.add_heading("4. Site — Thực Thể Vận Hành (Multi-Tenant)", level=1)
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(6)
    for run in h4.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        
    p4 = doc.add_paragraph()
    p4.paragraph_format.line_spacing = 1.15
    p4.paragraph_format.space_after = Pt(6)
    p4.add_run("• ").bold = True
    p4.add_run("Là gì: ").bold = True
    p4.add_run("Một Site là một thể hiện vận hành độc lập (isolated tenant instance). Mỗi Site tương ứng với: Một cơ sở dữ liệu MariaDB riêng biệt + Một file cấu hình site_config.json riêng + Thư mục lưu trữ tệp đính kèm (public/private files) riêng.\n")
    p4.add_run("• ").bold = True
    p4.add_run("Vai trò: ").bold = True
    p4.add_run("Hiện thực hóa kiến trúc Đa người thuê (Multi-Tenancy). Một Bench duy nhất có thể chứa và phục vụ hàng trăm Site cùng lúc. Mỗi Site là một doanh nghiệp hoàn toàn độc lập, có tên miền riêng và dữ liệu cô lập tuyệt đối.\n")
    p4.add_run("• ").bold = True
    p4.add_run("Minh họa thực tế: ").bold = True
    p4.add_run("Hai site `site_cuahang.local` và `site_truonghoc.local` cùng chạy chung trên một Bench, dùng chung bộ mã nguồn ERPNext, nhưng database của cửa hàng và trường học hoàn toàn riêng biệt, nhân viên bên này không bao giờ xem được dữ liệu bên kia.")
    
    add_callout_box(
        doc,
        "Ý tưởng cốt lõi cho sinh viên",
        "App là mã nguồn (dùng chung cho mọi người), Site là dữ liệu (cô lập riêng biệt cho từng khách hàng). Bạn chỉ cần viết một App một lần duy nhất, sau đó có thể cài App đó lên bao nhiêu Site tùy thích mà không cần nhân bản mã nguồn.",
        bg_color="FEF3C7",
        border_color="D97706",
        icon="👉"
    )
    
    # ----------------------------------------------------
    # 5. APP — GÓI PHẦN MỀM CÀI VÀO SITE
    # ----------------------------------------------------
    h5 = doc.add_heading("5. App — Gói Phần Mềm Cài Vào Site", level=1)
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(6)
    for run in h5.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        
    p5 = doc.add_paragraph()
    p5.paragraph_format.line_spacing = 1.15
    p5.paragraph_format.space_after = Pt(6)
    p5.add_run("• ").bold = True
    p5.add_run("Là gì: ").bold = True
    p5.add_run("App là một package Python chuẩn hóa chứa các DocTypes, module nghiệp vụ, logic điều khiển, giao diện và báo cáo. App được đưa vào Bench bằng lệnh `bench get-app`, sau đó được cài đặt lên từng Site cụ thể thông qua lệnh `bench --site [tên_site] install-app [tên_app]`.\n")
    p5.add_run("• ").bold = True
    p5.add_run("Phân loại cấu trúc phân tầng:\n").bold = True
    p5.add_run("  1. frappe (Lõi nền tảng): ").bold = True
    p5.add_run("Bắt buộc phải có trong mọi Bench, cung cấp các hạt nhân framework.\n")
    p5.add_run("  2. erpnext (Ứng dụng nghiệp vụ): ").bold = True
    p5.add_run("Cung cấp các phân hệ chuẩn ERP (Bán hàng, Mua hàng, Kho, Kế toán, Sản xuất).\n")
    p5.add_run("  3. custom_app (Ứng dụng mở rộng do lập trình viên/sinh viên tự viết): ").bold = True
    p5.add_run("Chứa các tính năng đặc thù (như AI Agent, tích hợp cổng thanh toán MoMo/VNPay, OMS đa kênh).")
    
    add_callout_box(
        doc,
        "Ý tưởng cốt lõi cho sinh viên",
        "Kiến trúc Plug-in (Cắm - Rút) hoàn hảo: Bạn muốn mở rộng chức năng hệ thống? Hãy tạo một App mới và cài vào Site. TUYỆT ĐỐI KHÔNG BAO GIỜ sửa trực tiếp mã nguồn trong lõi Frappe hay ERPNext, vì việc đó sẽ làm vỡ hệ thống khi cập nhật phiên bản mới.",
        bg_color="FEF3C7",
        border_color="D97706",
        icon="👉"
    )
    
    # ----------------------------------------------------
    # 6. ERPNEXT — ỨNG DỤNG NGHIỆP VỤ TRÊN CÙNG
    # ----------------------------------------------------
    h6 = doc.add_heading("6. ERPNext — Ứng Dụng Nghiệp Vụ Trên Cùng", level=1)
    h6.paragraph_format.space_before = Pt(14)
    h6.paragraph_format.space_after = Pt(6)
    for run in h6.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        
    p6 = doc.add_paragraph()
    p6.paragraph_format.line_spacing = 1.15
    p6.paragraph_format.space_after = Pt(6)
    p6.add_run("• ").bold = True
    p6.add_run("Là gì: ").bold = True
    p6.add_run("ERPNext là một ứng dụng Frappe hoàn chỉnh và toàn diện nhất thế giới, đóng gói hàng trăm DocTypes và module nghiệp vụ: Kế toán tài chính (Accounting), Bán hàng (Selling), Mua hàng (Buying), Quản lý kho vận (Stock), Quản lý sản xuất (Manufacturing), Nhân sự tiền lương (HR), Quản lý quan hệ khách hàng (CRM), và Quản lý dự án (Projects)...\n")
    p6.add_run("• ").bold = True
    p6.add_run("Vai trò: ").bold = True
    p6.add_run("Biến toàn bộ nền tảng kỹ thuật phức tạp bên dưới thành một giải pháp ERP thực tiễn, phục vụ công tác điều hành sản xuất kinh doanh cho doanh nghiệp.")
    
    # Master Connection Box
    add_callout_box(
        doc,
        "KẾT NỐI TRỌN VẸN TOÀN BỘ HỆ THỐNG",
        "ERPNext (App nghiệp vụ) được cài đặt lên một Site (Database độc lập), vận hành trơn tru nhờ nền tảng Frappe Framework, toàn bộ các quy trình nghiệp vụ được mô hình hóa nhất quán bằng DocType, và tất cả được điều phối nhịp nhàng bởi Bench trên hạ tầng công nghệ Python, MariaDB và Redis.",
        bg_color="ECFDF5",
        border_color="059669",
        icon="🎯"
    )
    
    # Save the document
    out_path = r"c:\Users\ASUS\Downloads\erpnet\Kien_Truc_Frappe_Bench_DocType_ERPNext.docx"
    doc.save(out_path)
    print(f"Document successfully created at: {out_path}")

if __name__ == "__main__":
    build_document()
