"""JIB.co.th price tracker — scrape product list, export CSV."""

import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PRODUCT_LIST = DATA_DIR / "products.txt"

BASE_URL = "https://www.jib.co.th/web/product/readproduct"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "th,en;q=0.9",
}
REQUEST_DELAY = 1.0
TIMEOUT = 15


def fetch_product(product_id: int) -> dict:
    url = f"{BASE_URL}/{product_id}"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    name_el = soup.select_one("h2.promotion_name") or soup.select_one("h1") or soup.select_one("title")
    price_el = soup.select_one(".price_block strong")

    name = name_el.get_text(strip=True) if name_el else None
    price_text = price_el.get_text(strip=True) if price_el else None
    price_value = _parse_price(price_text)

    return {
        "product_id": product_id,
        "url": url,
        "name": name,
        "price_text": price_text,
        "price": price_value,
    }


def _parse_price(text: str | None) -> float | None:
    if not text:
        return None
    cleaned = text.replace(",", "").replace("บาท", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def load_product_ids(path: Path) -> list[int]:
    ids: list[int] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            ids.append(int(line))
        except ValueError:
            print(f"warn: skip invalid id {line!r}", file=sys.stderr)
    return ids


def scrape_all(product_ids: list[int]) -> pd.DataFrame:
    rows = []
    for i, pid in enumerate(product_ids, 1):
        print(f"[{i}/{len(product_ids)}] {pid} ...", end=" ", flush=True)
        try:
            row = fetch_product(pid)
            row["scraped_at"] = datetime.now().isoformat(timespec="seconds")
            row["error"] = None
            print(f"{row['price']} | {(row['name'] or '')[:50]}")
        except Exception as exc:
            row = {
                "product_id": pid,
                "url": f"{BASE_URL}/{pid}",
                "name": None,
                "price_text": None,
                "price": None,
                "scraped_at": datetime.now().isoformat(timespec="seconds"),
                "error": str(exc),
            }
            print(f"ERROR {exc}")
        rows.append(row)
        if i < len(product_ids):
            time.sleep(REQUEST_DELAY)
    return pd.DataFrame(rows)


def export_csv(df: pd.DataFrame, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"prices_{stamp}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


def main() -> int:
    list_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PRODUCT_LIST
    if not list_path.exists():
        print(f"product list not found: {list_path}", file=sys.stderr)
        return 1

    ids = load_product_ids(list_path)
    if not ids:
        print("no product ids to scrape", file=sys.stderr)
        return 1

    print(f"scraping {len(ids)} products from JIB.co.th\n")
    df = scrape_all(ids)
    out_path = export_csv(df, DATA_DIR)

    ok = df["error"].isna().sum()
    fail = len(df) - ok
    print(f"\ndone: {ok} ok, {fail} failed")
    print(f"csv : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
