"""JIB.co.th product scraper — chunk 1: fetch single product."""

import sys

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "th,en;q=0.9",
}

DEFAULT_URL = "https://www.jib.co.th/web/product/readproduct/27414"


def fetch_product(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    name_el = soup.select_one("h2.promotion_name") or soup.select_one("h1") or soup.select_one("title")
    price_el = soup.select_one(".price_block strong")
    stock_el = soup.select_one(".product_status") or soup.select_one(".stock")

    return {
        "url": url,
        "name": name_el.get_text(strip=True) if name_el else None,
        "price": price_el.get_text(strip=True) if price_el else None,
        "stock": stock_el.get_text(strip=True) if stock_el else None,
    }


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    product = fetch_product(url)
    print(f"URL   : {product['url']}")
    print(f"Name  : {product['name']}")
    print(f"Price : {product['price']}")
    print(f"Stock : {product['stock']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
