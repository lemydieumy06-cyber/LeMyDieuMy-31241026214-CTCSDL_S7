# Python cho Phân tích Dữ liệu Kinh doanh – Bộ bài tập thực hành

## Cấu trúc thư mục

```
python_kinh_doanh/
├── data/        Dữ liệu kinh doanh giả lập dùng cho 9 buổi (+ make_data.py để tạo lại)
├── bai_tap/     Buoi_01_BaiTap.ipynb … Buoi_09_BaiTap.ipynb  – phát cho sinh viên
└── loi_giai/    Buoi_01_LoiGiai.ipynb … Buoi_09_LoiGiai.ipynb – chỉ dành cho giảng viên
```

Mỗi notebook gồm 3 phần:

- **Phần A – Bài tập có hướng dẫn:** code mẫu và giải thích từng bước, sinh viên chạy và quan sát.
- **Phần B – Bài tập tự làm (bắt buộc):** 5 bài, ô code để trống, nộp cuối buổi.
- **Phần C – Bài tập làm thêm:** 3 bài nâng cao cho sinh viên siêng năng.

Bản lời giải có đủ code cho Phần B và C, đã chạy sẵn kết quả để giảng viên đối chiếu.

## Cài đặt

Khuyến nghị Anaconda (Python 3.10 trở lên). Thư viện cần thêm:

```
pip install plotly openpyxl beautifulsoup4 lxml requests scikit-learn seaborn
```

Mở notebook từ thư mục `bai_tap/` (hoặc `loi_giai/`) để đường dẫn `../data/` hoạt động.
Dùng Google Colab: tải thư mục `data/` lên và sửa biến `DATA = "/content/data/"` ở ô đầu notebook.

## Dữ liệu

| Tệp | Mô tả | Buổi |
|---|---|---|
| supermarket_sales.csv | 1.000 hóa đơn siêu thị 2025, 3 thành phố, 6 nhóm hàng (tiền: nghìn đồng) | 3, 6, 9 |
| san_pham.xlsx | Danh mục sản phẩm và nhà cung cấp (2 sheet) | 4 |
| cua_hang.db | CSDL SQLite: bảng khach_hang, don_hang (6 tháng cuối 2025) | 4 |
| ty_gia_api.json | Dữ liệu mẫu dạng phản hồi API tỷ giá tháng 10/2025 | 4 |
| cua_hang_mau.html | Trang web mẫu để thực hành web scraping | 4 |
| ecommerce_orders_raw.csv | 3.816 đơn hàng TMĐT có lỗi cài sẵn (trùng, thiếu, sai định dạng, ngoại lai) | 5 |
| ecommerce_orders_clean.csv | Bản sạch của dữ liệu đơn hàng | 6, 8, 9 |
| customers.csv | 600 khách hàng: vùng, tuổi, giới tính, ngày đăng ký | 5, 6, 9 |
| advertising.csv | 200 thị trường: chi phí quảng cáo TV, radio, mạng xã hội và doanh số | 7 |
| house_prices.csv | 500 căn hộ TP.HCM: quận, diện tích, số phòng, tuổi nhà, giá (tỷ đồng) | 7 |
| telco_churn.csv | 2.000 thuê bao nhà mạng, nhãn rời bỏ (29%) | 8 |

Toàn bộ dữ liệu là **giả lập** (seed cố định 2026), chỉ dùng cho mục đích giảng dạy.
