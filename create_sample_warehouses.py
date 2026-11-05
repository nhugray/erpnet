import frappe

def main():
    frappe.init('frontend')
    frappe.connect()

    company = frappe.defaults.get_global_default('company') or 'nhom4-httt'
    abbr = frappe.db.get_value('Company', company, 'abbr')
    root = frappe.db.get_value('Warehouse', {'is_group': 1, 'company': company, 'parent_warehouse': ('is', 'not set')}, 'name') or f'All Warehouses - {abbr}'

    regions = {
        'Hà Nội': {
            'group_name': 'Khu vực Hà Nội',
            'city': 'Hà Nội',
            'warehouses': [
                {
                    'name': 'Kho Hà Nội - Cầu Giấy',
                    'address': 'Số 18 Phố Duy Tân, Phường Dịch Vọng Hậu, Quận Cầu Giấy',
                    'phone': '024 3795 8888',
                    'city': 'Hà Nội'
                },
                {
                    'name': 'Kho Hà Nội - Long Biên',
                    'address': 'KCN Đài Tư, 386 Nguyễn Văn Linh, Phường Sài Đồng, Quận Long Biên',
                    'phone': '024 3875 6666',
                    'city': 'Hà Nội'
                },
                {
                    'name': 'Kho Hà Nội - Thanh Trì',
                    'address': 'Cụm Công nghiệp Ngọc Hồi, Xã Ngọc Hồi, Huyện Thanh Trì',
                    'phone': '024 3681 5555',
                    'city': 'Hà Nội'
                }
            ]
        },
        'Đà Nẵng': {
            'group_name': 'Khu vực Đà Nẵng',
            'city': 'Đà Nẵng',
            'warehouses': [
                {
                    'name': 'Kho Đà Nẵng - Hải Châu',
                    'address': 'Số 120 Bạch Đằng, Phường Hải Châu 1, Quận Hải Châu',
                    'phone': '0236 3822 111',
                    'city': 'Đà Nẵng'
                },
                {
                    'name': 'Kho Đà Nẵng - Liên Chiểu',
                    'address': 'Đường số 3, KCN Hòa Khánh, Phường Hòa Khánh Bắc, Quận Liên Chiểu',
                    'phone': '0236 3733 222',
                    'city': 'Đà Nẵng'
                },
                {
                    'name': 'Kho Đà Nẵng - Cẩm Lệ',
                    'address': 'KCN Hòa Cầm, Phường Hòa Thọ Tây, Quận Cẩm Lệ',
                    'phone': '0236 3677 333',
                    'city': 'Đà Nẵng'
                }
            ]
        },
        'Hồ Chí Minh': {
            'group_name': 'Khu vực Hồ Chí Minh',
            'city': 'Hồ Chí Minh',
            'warehouses': [
                {
                    'name': 'Kho TP.HCM - Tân Bình',
                    'address': 'Đường CN13, KCN Tân Bình, Phường Tây Thạnh, Quận Tân Bình',
                    'phone': '028 3816 8888',
                    'city': 'Hồ Chí Minh'
                },
                {
                    'name': 'Kho TP.HCM - Thủ Đức',
                    'address': 'Đường D1, Khu Công nghệ cao, Phường Tăng Nhơn Phú B, TP. Thủ Đức',
                    'phone': '028 3730 7777',
                    'city': 'Hồ Chí Minh'
                },
                {
                    'name': 'Kho TP.HCM - Quận 7',
                    'address': 'Đường Tân Thuận, KCX Tân Thuận, Phường Tân Thuận Đông, Quận 7',
                    'phone': '028 3770 6666',
                    'city': 'Hồ Chí Minh'
                }
            ]
        }
    }

    results = []

    for region_name, rdata in regions.items():
        group_wh_name = f"{rdata['group_name']} - {abbr}"
        if not frappe.db.exists('Warehouse', group_wh_name):
            gw = frappe.new_doc('Warehouse')
            gw.warehouse_name = rdata['group_name']
            gw.company = company
            gw.is_group = 1
            gw.parent_warehouse = root
            gw.city = rdata['city']
            gw.state = rdata['city']
            gw.insert(ignore_permissions=True)
            results.append(f"[+ Group] {gw.name}")
        else:
            results.append(f"[= Group exists] {group_wh_name}")

        for wh in rdata['warehouses']:
            wh_full_name = f"{wh['name']} - {abbr}"
            if not frappe.db.exists('Warehouse', wh_full_name):
                w = frappe.new_doc('Warehouse')
                w.warehouse_name = wh['name']
                w.company = company
                w.is_group = 0
                w.parent_warehouse = group_wh_name
                w.address_line_1 = wh['address']
                w.city = wh['city']
                w.state = wh['city']
                w.phone_no = wh['phone']
                w.insert(ignore_permissions=True)
                results.append(f"  [+ Kho] {w.name} | ĐC: {w.address_line_1} | SĐT: {w.phone_no}")
            else:
                results.append(f"  [= Kho exists] {wh_full_name}")

    frappe.db.commit()
    print("\n".join(results))

if __name__ == '__main__':
    main()

