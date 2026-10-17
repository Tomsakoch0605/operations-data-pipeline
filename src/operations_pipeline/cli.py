"""Command line interface for the self-contained demo."""
import argparse
import logging
import os
from .client import fetch_all
from .generator import generate
from .mock_api import create_server
from .storage import connect, export_summary, save

logger = logging.getLogger(__name__)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ops-pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("generate", help="Create deterministic synthetic CSV")
    g.add_argument("--output", default="data/synthetic_transactions.csv")
    g.add_argument("--count", type=int, default=100)
    g.add_argument("--seed", type=int, default=42)
    s = sub.add_parser("serve", help="Serve synthetic CSV on localhost")
    s.add_argument("--input", default="data/synthetic_transactions.csv")
    s.add_argument("--port", type=int, default=8765)
    r = sub.add_parser("run", help="Ingest from local API and export aggregate CSV")
    r.add_argument("--api", default=os.getenv("OPS_API_URL", "http://127.0.0.1:8765"))
    r.add_argument("--db", default=os.getenv("OPS_DATABASE", "output/operations.db"))
    r.add_argument("--report", default=os.getenv("OPS_REPORT", "output/summary.csv"))
    r.add_argument("--timeout", type=float, default=float(os.getenv("OPS_TIMEOUT", "3")))
    r.add_argument("--retries", type=int, default=int(os.getenv("OPS_RETRIES", "3")))
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.command == "generate":
        path = generate(args.output, args.count, args.seed)
        print(f"Synthetic dataset created: {path}")
    elif args.command == "serve":
        server = create_server(args.input, port=args.port)
        print(f"Mock API running at http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    elif args.command == "run":
        connection = connect(args.db)
        try:
            total = added = 0
            batch = []
            for record in fetch_all(args.api, args.timeout, args.retries):
                batch.append(record)
                total += 1
                if len(batch) == 100:
                    added += save(connection, batch)
                    batch.clear()
            added += save(connection, batch)
            export_summary(connection, args.report)
        finally:
            connection.close()
        print(f"Fetched: {total}; newly inserted: {added}; report: {args.report}")

if __name__ == "__main__":
    main()
