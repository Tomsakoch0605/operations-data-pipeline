# Publication checklist

- [x] Built as a new, standalone source tree (no copied repository files).
- [x] Only fictional IDs, data and localhost API appear in code.
- [x] Generated reproducible demonstration dataset.
- [x] Included unit and local integration tests.
- [x] Added `.gitignore` for secrets, environment files, caches and databases.
- [x] No actual secrets required or embedded by design.
- [ ] Re-run tests and review exact files after any later modification.
- [ ] Scan the *new Git repository history* after repository initialization using a secret scanner (e.g. Gitleaks).
- [ ] Perform final dependency vulnerability/license review for versions selected at publish time.
- [ ] Confirm the publishing account, GitHub repository visibility, and portfolio wording.
- [ ] Verify any intellectual-property/contractual permissions not established by the code scan.

**Status: REQUIRES REVIEW** until final security/history checks and rights assessment are complete. A source-tree scan cannot establish authorization or prove the absence of every risk.
