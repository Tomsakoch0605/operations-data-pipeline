# Portfolio presentation

**GitHub description (under 160 characters):** Resilient Python pipeline with a fictional local API, seeded synthetic data, SQLite deduplication, retries, tests and CSV reporting.

**Suggested topics:** `python`, `data-engineering`, `etl`, `api-integration`, `automation`, `sqlite`, `pytest`, `github-actions`

## Resume bullets (demonstration facts only)

- Built an independent Python pipeline integrating a paginated mock REST API, schema validation, and SQLite persistence.
- Implemented repeatable synthetic test data, primary-key deduplication, bounded HTTP retries, and CSV aggregate reporting.
- Added automated unit/integration tests, Python package entry points, architecture documentation, and GitHub Actions CI.

## 60-second interview pitch

“In my professional work, I encountered engineering challenges involving automation, data integration, and reliable recurring reporting. For my public portfolio, I independently designed and built a fictional operations data pipeline to demonstrate those transferable skills without exposing an employer’s code or data. The demo generates seeded synthetic transactions, serves them via a localhost API, ingests paginated responses with bounded retries, validates records, and writes to SQLite with deduplication. It then exports an aggregated CSV summary. I deliberately avoided unnecessary cloud infrastructure, while providing integration tests and CI. The code in this repository is a separate demonstration, not the production implementation.”

## Likely technical interview questions

1. **How is the pipeline idempotent?** `transaction_id` is a SQLite primary key; duplicate inserts are ignored.
2. **What happens if the source updates an existing transaction?** The current model is append-only; an explicit update/upsert policy is a documented future enhancement.
3. **Why integer cents?** It avoids floating-point drift in stored monetary values.
4. **Which failures retry?** Transport failures and HTTP 5xx; not ordinary 4xx errors or validation failures.
5. **Why not use a cloud provider?** The demo's aim is a reproducible, independently executable integration example.
6. **How was proprietary information excluded?** All interfaces, fictional IDs, data generation, and reporting logic were independently created for a generic scenario.
