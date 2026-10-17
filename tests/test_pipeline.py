import csv
import threading
from urllib.error import HTTPError
import pytest
from operations_pipeline.client import fetch_all
from operations_pipeline.generator import generate
from operations_pipeline.mock_api import create_server
from operations_pipeline.storage import connect, save, export_summary
from operations_pipeline.validation import parse_transaction


def test_generator_is_deterministic(tmp_path):
    first = generate(tmp_path / "first.csv", count=12, seed=8)
    second = generate(tmp_path / "second.csv", count=12, seed=8)
    assert first.read_bytes() == second.read_bytes()
    assert len(list(csv.DictReader(first.open()))) == 12


def test_validation_rejects_non_demo_identifiers():
    with pytest.raises(ValueError):
        parse_transaction({"transaction_id": "REAL-1", "customer_id": "SYN-01", "date": "2025-01-01", "category": "books", "amount": "2.00", "status": "completed"})


def test_validation_rejects_excess_precision():
    with pytest.raises(ValueError):
        parse_transaction({"transaction_id": "DEMO-1", "customer_id": "SYN-01", "date": "2025-01-01", "category": "books", "amount": "2.001", "status": "completed"})


def test_full_pipeline_and_idempotency(tmp_path):
    data = generate(tmp_path / "data.csv", count=53, seed=12)
    server = create_server(data, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        records = list(fetch_all(base, limit=17))
        assert len(records) == 53
        db = connect(tmp_path / "data.db")
        assert save(db, records) == 53
        assert save(db, records) == 0
        output = export_summary(db, tmp_path / "report.csv")
        rows = list(csv.DictReader(output.open()))
        assert sum(int(row["transaction_count"]) for row in rows) == 53
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 53
        db.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_client_rejects_non_local_api():
    with pytest.raises(ValueError):
        list(fetch_all("https://somewhere.example"))


def test_invalid_pagination_returns_400(tmp_path):
    data = generate(tmp_path / "data.csv", count=2)
    server = create_server(data, port=0)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        from urllib.request import urlopen
        with pytest.raises(HTTPError) as exc:
            urlopen(f"http://127.0.0.1:{server.server_port}/transactions?page=-1")
        assert exc.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=2)
