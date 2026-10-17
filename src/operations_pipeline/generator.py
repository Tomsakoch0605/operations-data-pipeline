"""Create reproducible, entirely invented transaction records."""
import csv
from datetime import date, timedelta
from pathlib import Path
from random import Random

FIELDS = ("transaction_id", "customer_id", "date", "category", "amount", "status")
CATEGORIES = ("books", "stationery", "home", "garden")
STATUSES = ("completed", "pending", "cancelled")


def generate(path: str | Path, count: int = 100, seed: int = 42) -> Path:
    if count < 0 or count > 100_000:
        raise ValueError("count must be between 0 and 100000")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rng = Random(seed)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for index in range(1, count + 1):
            writer.writerow({
                "transaction_id": f"DEMO-{index:06d}",
                "customer_id": f"SYN-{rng.randint(1, 30):04d}",
                "date": (date(2025, 1, 1) + timedelta(days=rng.randint(0, 89))).isoformat(),
                "category": rng.choice(CATEGORIES),
                "amount": f"{rng.randint(500, 25000) / 100:.2f}",
                "status": rng.choices(STATUSES, weights=[75, 15, 10])[0],
            })
    return target
