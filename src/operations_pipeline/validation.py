"""Contract validation at the external-data boundary."""
from datetime import date
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass

@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    customer_id: str
    date: str
    category: str
    amount_cents: int
    status: str


def parse_transaction(record: dict) -> Transaction:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    required = ("transaction_id", "customer_id", "date", "category", "amount", "status")
    if any(key not in record for key in required):
        raise ValueError("missing required transaction field")
    tid, customer = str(record["transaction_id"]), str(record["customer_id"])
    category, status = str(record["category"]), str(record["status"])
    if not tid.startswith("DEMO-") or not customer.startswith("SYN-"):
        raise ValueError("invalid synthetic identifier")
    if len(tid) > 30 or len(customer) > 30:
        raise ValueError("identifier too long")
    if category not in {"books", "stationery", "home", "garden"}:
        raise ValueError("unknown category")
    if status not in {"completed", "pending", "cancelled"}:
        raise ValueError("unknown status")
    try:
        parsed_date = date.fromisoformat(str(record["date"]))
        amount = Decimal(str(record["amount"]))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError("invalid date or amount") from exc
    if not amount.is_finite() or amount < 0 or amount > 1_000_000 or amount.as_tuple().exponent < -2:
        raise ValueError("amount out of range or precision")
    cents = int(amount * 100)
    return Transaction(tid, customer, parsed_date.isoformat(), category, cents, status)
