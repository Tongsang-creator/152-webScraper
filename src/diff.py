"""Compare two latest price CSVs, report changes."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def latest_csvs(data_dir: Path, n: int = 2) -> list[Path]:
    files = sorted(data_dir.glob("prices_*.csv"), reverse=True)
    return files[:n]


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def diff(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    merged = new.merge(
        old[["product_id", "price"]].rename(columns={"price": "price_old"}),
        on="product_id",
        how="left",
    )
    merged = merged.rename(columns={"price": "price_new"})
    merged["delta"] = merged["price_new"] - merged["price_old"]
    merged["pct"] = (merged["delta"] / merged["price_old"]) * 100
    return merged


def classify(row: pd.Series) -> str:
    if pd.isna(row["price_old"]):
        return "NEW"
    if pd.isna(row["price_new"]):
        return "MISSING"
    if row["delta"] == 0:
        return "SAME"
    return "DOWN" if row["delta"] < 0 else "UP"


def main() -> int:
    files = latest_csvs(DATA_DIR)
    if len(files) < 2:
        print(f"need >=2 csv files in {DATA_DIR}, got {len(files)}", file=sys.stderr)
        return 1

    new_path, old_path = files[0], files[1]
    print(f"new: {new_path.name}")
    print(f"old: {old_path.name}\n")

    new_df = load(new_path)
    old_df = load(old_path)
    report = diff(old_df, new_df)
    report["status"] = report.apply(classify, axis=1)

    changed = report[report["status"].isin(["UP", "DOWN", "NEW", "MISSING"])]

    if changed.empty:
        print("no price changes")
        return 0

    cols = ["product_id", "name", "price_old", "price_new", "delta", "pct", "status"]
    print(changed[cols].to_string(index=False))

    out_path = DATA_DIR / f"diff_{new_path.stem.replace('prices_','')}.csv"
    report.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nfull report: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
