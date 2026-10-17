"""Sinh bộ dữ liệu giả lập cho môn Python cho Phân tích Dữ liệu Kinh doanh.
Chạy: python make_data.py  -> tạo thư mục ../course/data
"""
import json, sqlite3, os
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2026)

# ---------------------------------------------------------------- 1. Supermarket sales
branches = {"A": "TP.HCM", "B": "Hà Nội", "C": "Đà Nẵng"}
lines = {
    "Điện tử": (120, 950), "Thời trang": (60, 600), "Thực phẩm": (15, 180),
    "Sức khỏe & Làm đẹp": (40, 450), "Gia dụng": (50, 700), "Thể thao & Du lịch": (70, 800),
}
n = 1000
dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
branch = rng.choice(list(branches), n, p=[0.42, 0.35, 0.23])
pl = rng.choice(list(lines), n)
unit_price = np.array([rng.uniform(*lines[p]) for p in pl]).round().astype(int)  # nghìn đồng
qty = rng.integers(1, 11, n)
cust_type = rng.choice(["Thành viên", "Khách thường"], n, p=[0.5, 0.5])
discount = np.where(cust_type == "Thành viên", 0.05, 0.0)
subtotal = unit_price * qty
total = (subtotal * (1 - discount) * 1.08).round(1)  # VAT 8%
cogs = (subtotal * rng.uniform(0.70, 0.85, n)).round(1)
df_sm = pd.DataFrame({
    "ma_hoa_don": [f"HD{100000+i}" for i in range(n)],
    "ngay": dates.strftime("%Y-%m-%d"),
    "gio": [f"{h:02d}:{m:02d}" for h, m in zip(rng.integers(8, 22, n), rng.integers(0, 60, n))],
    "chi_nhanh": branch,
    "thanh_pho": [branches[b] for b in branch],
    "loai_khach": cust_type,
    "gioi_tinh": rng.choice(["Nam", "Nữ"], n),
    "nhom_hang": pl,
    "don_gia": unit_price,          # nghìn đồng
    "so_luong": qty,
    "chiet_khau": discount,
    "tong_tien": total,             # nghìn đồng, gồm VAT 8%
    "gia_von": cogs,
    "thanh_toan": rng.choice(["Tiền mặt", "Thẻ", "Ví điện tử"], n, p=[0.3, 0.3, 0.4]),
    "danh_gia": rng.uniform(4, 10, n).round(1),
}).sort_values("ngay").reset_index(drop=True)
df_sm["loi_nhuan_gop"] = (df_sm["tong_tien"] / 1.08 - df_sm["gia_von"]).round(1)
df_sm.to_csv(OUT / "supermarket_sales.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- 2. Products Excel (2 sheets)
sp = pd.DataFrame({
    "ma_sp": [f"SP{i:03d}" for i in range(1, 41)],
    "ten_sp": [f"Sản phẩm {i}" for i in range(1, 41)],
    "nhom_hang": rng.choice(list(lines), 40),
    "gia_ban": rng.integers(20, 900, 40) * 1000,
    "ton_kho": rng.integers(0, 300, 40),
    "ma_ncc": rng.choice([f"NCC{i}" for i in range(1, 7)], 40),
})
ncc = pd.DataFrame({
    "ma_ncc": [f"NCC{i}" for i in range(1, 7)],
    "ten_ncc": ["Công ty Minh Phát", "Công ty An Khang", "Công ty Đại Việt",
                "Công ty Sao Mai", "Công ty Hòa Bình", "Công ty Phú Quý"],
    "tinh_thanh": ["TP.HCM", "Bình Dương", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Hải Phòng"],
    "thoi_gian_giao_ngay": [2, 3, 5, 4, 3, 6],
})
with pd.ExcelWriter(OUT / "san_pham.xlsx") as w:
    sp.to_excel(w, sheet_name="SanPham", index=False)
    ncc.to_excel(w, sheet_name="NhaCungCap", index=False)

# ---------------------------------------------------------------- 3. E-commerce: customers + orders (clean core)
n_cust = 600
regions = ["Miền Bắc", "Miền Trung", "Miền Nam"]
# 4 nhóm hành vi ẩn để phân cụm có cấu trúc
seg = rng.choice(4, n_cust, p=[0.2, 0.3, 0.3, 0.2])
customers = pd.DataFrame({
    "ma_kh": [f"KH{i:04d}" for i in range(1, n_cust + 1)],
    "ho_ten": [f"Khách hàng {i}" for i in range(1, n_cust + 1)],
    "vung": rng.choice(regions, n_cust, p=[0.35, 0.2, 0.45]),
    "tuoi": rng.integers(18, 65, n_cust),
    "gioi_tinh": rng.choice(["Nam", "Nữ"], n_cust),
    "ngay_dang_ky": (pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 700, n_cust), unit="D")).strftime("%Y-%m-%d"),
})
cats = {"Điện thoại": 6500, "Laptop": 15000, "Phụ kiện": 350, "Thời trang": 450, "Mỹ phẩm": 400, "Gia dụng": 900}
products = {c: [f"{c} {k}" for k in "ABCDE"] for c in cats}
# freq/order value/recency by segment: 0 VIP, 1 trung thành, 2 mới/thỉnh thoảng, 3 ngủ đông
seg_freq = {0: (12, 20), 1: (6, 11), 2: (1, 4), 3: (1, 5)}
seg_last = {0: (0, 30), 1: (0, 60), 2: (0, 90), 3: (180, 360)}
seg_cat_p = {0: [0.25, 0.25, 0.15, 0.1, 0.1, 0.15], 1: [0.1, 0.05, 0.3, 0.25, 0.2, 0.1],
             2: [0.1, 0.05, 0.3, 0.25, 0.2, 0.1], 3: [0.1, 0.05, 0.3, 0.25, 0.2, 0.1]}
end = pd.Timestamp("2025-12-31")
rows = []
oid = 1
for i, c in customers.iterrows():
    s = seg[i]
    k = rng.integers(*seg_freq[s])
    last = end - pd.Timedelta(days=int(rng.integers(*seg_last[s])))
    span = 360 if s != 3 else 200
    for j in range(k):
        d = last - pd.Timedelta(days=int(rng.integers(0, span))) if j else last
        if d < pd.Timestamp("2025-01-01"):
            d = pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 30)))
        cat = rng.choice(list(cats), p=seg_cat_p[s])
        price = int(cats[cat] * rng.uniform(0.6, 1.5)) * 1000
        rows.append({
            "ma_don": f"DH{oid:06d}", "ngay_dat": d.strftime("%Y-%m-%d"), "ma_kh": c.ma_kh,
            "kenh": rng.choice(["Website", "App", "Sàn TMĐT", "Cửa hàng"], p=[0.25, 0.3, 0.3, 0.15]),
            "nhom_hang": cat, "san_pham": rng.choice(products[cat]),
            "so_luong": int(rng.choice([1, 1, 1, 2, 2, 3])), "don_gia": price,
            "trang_thai": rng.choice(["Hoàn thành", "Hoàn thành", "Hoàn thành", "Hoàn thành", "Đã hủy"]),
        })
        oid += 1
orders = pd.DataFrame(rows).sort_values("ngay_dat").reset_index(drop=True)
customers.to_csv(OUT / "customers.csv", index=False, encoding="utf-8-sig")

# Dirty version for Session 5
dirty = orders.copy()
dirty["vung"] = dirty["ma_kh"].map(customers.set_index("ma_kh")["vung"])
idx = rng.choice(len(dirty), 120, replace=False)
dirty.loc[idx[:40], "vung"] = dirty.loc[idx[:40], "vung"].str.upper()
dirty.loc[idx[40:70], "vung"] = " " + dirty.loc[idx[40:70], "vung"] + " "
dirty.loc[idx[70:90], "vung"] = np.nan
dirty["so_luong"] = dirty["so_luong"].astype("object")
dirty.loc[rng.choice(len(dirty), 60, replace=False), "so_luong"] = np.nan
dirty["don_gia"] = dirty["don_gia"].astype("object")
j = rng.choice(len(dirty), 150, replace=False)
dirty.loc[j[:100], "don_gia"] = dirty.loc[j[:100], "don_gia"].map(lambda v: f"{int(v):,}".replace(",", ".") + " đ")
dirty.loc[j[100:105], "don_gia"] = -1  # lỗi nhập liệu
dirty.loc[j[105:110], "don_gia"] = 999_999_000  # ngoại lai
k = rng.choice(len(dirty), 200, replace=False)
dirty.loc[k, "ngay_dat"] = pd.to_datetime(dirty.loc[k, "ngay_dat"]).dt.strftime("%d/%m/%Y")
dups = dirty.sample(45, random_state=1)
dirty = pd.concat([dirty, dups]).sample(frac=1, random_state=2).reset_index(drop=True)
dirty = dirty[["ma_don", "ngay_dat", "ma_kh", "vung", "kenh", "nhom_hang", "san_pham", "so_luong", "don_gia", "trang_thai"]]
dirty.to_csv(OUT / "ecommerce_orders_raw.csv", index=False, encoding="utf-8-sig")
orders.to_csv(OUT / "ecommerce_orders_clean.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- 4. SQLite DB (Session 4)
con = sqlite3.connect(OUT / "cua_hang.db")
customers.to_sql("khach_hang", con, if_exists="replace", index=False)
orders[orders["ngay_dat"] >= "2025-07-01"].to_sql("don_hang", con, if_exists="replace", index=False)
con.close()

# ---------------------------------------------------------------- 5. JSON "API" offline (Session 4)
base = {"USD": 25350, "EUR": 27480, "JPY": 168.2, "CNY": 3510, "KRW": 18.4, "SGD": 19620}
days = pd.date_range("2025-10-01", "2025-10-31")
api = {"source": "Dữ liệu mẫu tỷ giá (VND)", "base": "VND", "rates": []}
for d in days:
    api["rates"].append({"date": d.strftime("%Y-%m-%d"),
                         "rates": {c: round(v * (1 + rng.normal(0, 0.004)), 2) for c, v in base.items()}})
(OUT / "ty_gia_api.json").write_text(json.dumps(api, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------- 6. HTML page for scraping (Session 4)
cards = []
names = ["Tai nghe Bluetooth", "Sạc dự phòng 10000mAh", "Chuột không dây", "Bàn phím cơ", "Loa mini",
         "Đồng hồ thông minh", "Cáp sạc nhanh", "Ốp lưng điện thoại", "Giá đỡ laptop", "Webcam HD",
         "Thẻ nhớ 64GB", "USB 128GB", "Ổ cứng di động 1TB", "Bút cảm ứng", "Đèn bàn LED",
         "Quạt mini USB", "Hub USB-C", "Micro thu âm", "Kính thực tế ảo", "Máy đọc sách"]
for i, nm in enumerate(names):
    price = int(rng.integers(80, 3500)) * 1000
    old = int(price * rng.uniform(1.05, 1.5) / 1000) * 1000
    rating = round(float(rng.uniform(3.2, 5.0)), 1)
    sold = int(rng.integers(5, 5000))
    stock = "Còn hàng" if rng.random() > 0.15 else "Hết hàng"
    cards.append(f'''    <div class="product" data-id="P{i+1:03d}">
      <h3 class="name">{nm}</h3>
      <span class="price">{price:,}₫</span> <span class="old-price">{old:,}₫</span>
      <div class="rating">{rating}</div>
      <div class="sold">Đã bán {sold}</div>
      <div class="stock">{stock}</div>
    </div>'''.replace(",", "."))
html = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Cửa hàng Phụ kiện Mẫu</title></head>
<body>
  <h1>Cửa hàng Phụ kiện Mẫu – Danh mục sản phẩm</h1>
  <div id="products">
{chr(10).join(cards)}
  </div>
  <h2>Bảng giá phí vận chuyển</h2>
  <table id="shipping">
    <tr><th>Khu vực</th><th>Phí (nghìn đồng)</th><th>Thời gian (ngày)</th></tr>
    <tr><td>Nội thành TP.HCM</td><td>15</td><td>1</td></tr>
    <tr><td>Ngoại thành TP.HCM</td><td>25</td><td>2</td></tr>
    <tr><td>Miền Nam</td><td>30</td><td>2</td></tr>
    <tr><td>Miền Trung</td><td>35</td><td>3</td></tr>
    <tr><td>Miền Bắc</td><td>40</td><td>4</td></tr>
  </table>
</body></html>"""
(OUT / "cua_hang_mau.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------------------- 7. Advertising (Session 7)
m = 200
tv = rng.uniform(0, 300, m).round(1)
radio = rng.uniform(0, 50, m).round(1)
social = rng.uniform(0, 100, m).round(1)
sales = (3 + 0.045 * tv + 0.18 * radio + 0.02 * social + rng.normal(0, 1.4, m)).round(1)
pd.DataFrame({"tv": tv, "radio": radio, "mang_xa_hoi": social, "doanh_so": sales}).to_csv(
    OUT / "advertising.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- 8. House prices (Session 7)
h = 500
quan = rng.choice(["Quận 1", "Quận 3", "Quận 7", "Bình Thạnh", "Thủ Đức", "Gò Vấp"], h)
qbase = {"Quận 1": 250, "Quận 3": 200, "Quận 7": 120, "Bình Thạnh": 110, "Thủ Đức": 80, "Gò Vấp": 85}
area = rng.uniform(30, 150, h).round(1)
bed = np.clip((area / 30).round().astype(int) + rng.integers(-1, 2, h), 1, 5)
age = rng.integers(0, 30, h)
dist = np.array([{"Quận 1": 1, "Quận 3": 3, "Quận 7": 8, "Bình Thạnh": 5, "Thủ Đức": 12, "Gò Vấp": 7}[q] for q in quan]) + rng.uniform(-1, 2, h)
price = (np.array([qbase[q] for q in quan]) * area * (1 - age * 0.008) / 100 + rng.normal(0, 8, h)).round(2)
pd.DataFrame({"quan": quan, "dien_tich_m2": area, "so_phong_ngu": bed, "tuoi_nha": age,
              "khoang_cach_tt_km": dist.round(1), "gia_ty_dong": np.maximum(price, 0.8)}).to_csv(
    OUT / "house_prices.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- 9. Telco churn (Session 8)
t = 2000
tenure = rng.integers(1, 72, t)
contract = rng.choice(["Theo tháng", "1 năm", "2 năm"], t, p=[0.55, 0.25, 0.2])
internet = rng.choice(["Cáp quang", "DSL", "Không"], t, p=[0.45, 0.35, 0.2])
monthly = (rng.uniform(100, 250, t) + np.where(internet == "Cáp quang", 120, np.where(internet == "DSL", 50, 0))).round(0)
calls = rng.poisson(1.5, t)
pay = rng.choice(["Chuyển khoản", "Thẻ tín dụng", "Ví điện tử", "Tiền mặt"], t)
logit = (-1.2 - 0.04 * tenure + 1.4 * (contract == "Theo tháng") - 0.8 * (contract == "2 năm")
         + 0.6 * (internet == "Cáp quang") + 0.006 * (monthly - 250) + 0.35 * calls + 0.4 * (pay == "Tiền mặt"))
churn = (rng.random(t) < 1 / (1 + np.exp(-logit))).astype(int)
pd.DataFrame({"ma_kh": [f"TB{i:05d}" for i in range(t)], "thoi_gian_su_dung_thang": tenure,
              "loai_hop_dong": contract, "dich_vu_internet": internet, "cuoc_thang_nghin": monthly,
              "so_lan_goi_ho_tro": calls, "phuong_thuc_tt": pay, "roi_bo": churn}).to_csv(
    OUT / "telco_churn.csv", index=False, encoding="utf-8-sig")

print("Đã tạo:", sorted(p.name for p in OUT.iterdir()))
print("supermarket", df_sm.shape, "orders", orders.shape, "dirty", dirty.shape, "churn rate", churn.mean().round(3))
