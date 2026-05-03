# JIB Price Tracker

ระบบติดตามราคาสินค้าจาก [JIB.co.th](https://www.jib.co.th) อัตโนมัติ ส่งออก CSV และตรวจจับการเปลี่ยนแปลงราคาเทียบกับรอบก่อนหน้า

> Automated price tracker for JIB.co.th — scrape product list, export to CSV, detect price changes between runs.

---

## ใช้ทำอะไรได้ (Use cases)

- ติดตามราคาคู่แข่ง (competitor monitoring) สำหรับร้านค้าออนไลน์
- แจ้งเตือนเมื่อสินค้าที่จับตาลดราคา / ขึ้นราคา
- เก็บข้อมูลราคาย้อนหลังเพื่อวิเคราะห์เทรนด์
- พื้นฐานสำหรับ price comparison engine

---

## Demo

Scrape 9 products and export CSV:

```text
$ python src/scraper.py
scraping 9 products from JIB.co.th

[1/9] 27414 ... 48900.0 | NOTEBOOK DELL INSPIRON 7370-W5675003CTHW10
[2/9] 30000 ... 14990.0 | DESKTOP PC HP PAVILION 590-P
[3/9] 35000 ... 2990.0  | DVR DAHUA DH-XVR4108HS-X 8 CHANNEL
[4/9] 40000 ... 4490.0  | MAINBOARD ASUS ROG STRIX B460-H GAMING
[5/9] 45000 ... 450.0   | KEYBOARD & MOUSE GENIUS COMBO
[6/9] 55000 ... 690.0   | CPU AIR COOLER GAMDIAS BOREAS E1-410
[7/9] 60000 ... 42690.0 | COMPUTER SET JIB MARU-2306091
[8/9] 28500 ... 590.0   | CHARGER UGREEN QUICK CHARGE 3.0
[9/9] 32000 ... 9900.0  | NOTEBOOK ASUS X407UF-BV054T

done: 9 ok, 0 failed
csv : data/prices_20260503_121629.csv
```

Detect price changes between runs:

```text
$ python src/diff.py
new: prices_20260503_121629.csv
old: prices_20260502_090000.csv

 product_id  name                     price_old  price_new  delta     pct  status
      27414  NOTEBOOK DELL INSPIRON     46900.0    48900.0  2000.0   4.26  UP
      35000  DVR DAHUA DH-XVR4108HS-X    3490.0     2990.0  -500.0 -14.33  DOWN
      32000  NOTEBOOK ASUS X407UF         NaN      9900.0    NaN     NaN   NEW
```

---

## Features

- Scrape สินค้าหลายรายการพร้อมกัน (multi-product batch)
- Export CSV พร้อม timestamp ในชื่อไฟล์
- ตรวจจับการเปลี่ยนแปลง: `UP` / `DOWN` / `NEW` / `MISSING` / `SAME`
- คำนวณ delta + percentage change
- จัดการ error รายตัว (1 product fail ไม่ทำให้ batch ล้ม)
- Rate limiting (1 sec / request) ลด server load
- UTF-8 BOM CSV เปิดใน Excel ได้ทันที

---

## Tech Stack

- **Python 3.10+**
- `requests` — HTTP client
- `beautifulsoup4` + `lxml` — HTML parsing
- `pandas` — data manipulation + CSV export

---

## Quick Start

```bash
# clone
git clone https://github.com/Tongsang-creator/152-webScraper.git
cd 152-webScraper

# venv
python -m venv venv
source venv/Scripts/activate   # Windows: venv\Scripts\activate

# install
pip install -r requirements.txt

# scrape
python src/scraper.py

# detect changes (need >= 2 CSV files in data/)
python src/diff.py
```

---

## Customize Product List

แก้ไข `data/products.txt` — 1 product ID ต่อบรรทัด:

```
27414
30000
35000
```

หา product ID จาก URL JIB:
`https://www.jib.co.th/web/product/readproduct/<ID>`

---

## Sample CSV Output

```csv
product_id,url,name,price_text,price,scraped_at,error
27414,https://www.jib.co.th/web/product/readproduct/27414,NOTEBOOK DELL INSPIRON 7370,"48,900",48900.0,2026-05-03T12:16:29,
30000,https://www.jib.co.th/web/product/readproduct/30000,DESKTOP PC HP PAVILION,"14,990",14990.0,2026-05-03T12:16:30,
```

---

## Project Structure

```
152-webScraper/
├── src/
│   ├── scraper.py     # multi-product scrape + CSV export
│   └── diff.py        # compare 2 latest CSVs, report changes
├── data/
│   ├── products.txt   # product IDs to track
│   └── prices_*.csv   # scrape outputs (timestamped)
├── requirements.txt
└── Readme.md
```

---

## Roadmap (next iterations)

- [ ] Schedule (cron / Task Scheduler) — รัน scrape วันละครั้ง
- [ ] Notification: LINE Notify / Discord webhook เมื่อราคาเปลี่ยน
- [ ] Multi-site support: Lazada, Shopee, Advice
- [ ] Web dashboard — chart ราคาย้อนหลัง
- [ ] Database storage แทน CSV (SQLite / Postgres)

---

## Note

Project นี้สร้างเพื่อเป็น portfolio demo ของ web scraping + data pipeline skill. ใช้งานจริงควรเคารพ `robots.txt` ของเว็บไซต์เป้าหมาย และตั้ง rate limit ที่เหมาะสม

Built as a portfolio demo. For production use, respect target site's `robots.txt` and use appropriate rate limits.
