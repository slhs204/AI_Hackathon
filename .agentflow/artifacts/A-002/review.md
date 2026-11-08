# Final delta review: A-002 Cloud Run AI connector

**Verdict: PASS.** I found no material defects. N1 is fixed in the source, and L1–L3 are resolved. F1–F8 are not regressed, and INV-1 through INV-3 still hold. The remaining items are proof conditions, not source failures.

## N1 is resolved

- **Fix:** `start-demo.ps1` now sets `$env:CLOUDSDK_PYTHON = $venv` only when it is unset and bundled Python is absent.
  - `$venv` is always absolute, because it is built by `Join-Path` from `Split-Path $PSScriptRoot -Parent`.
  - On a fresh clone, the venv creation step removes the ready marker, which forces `pip install` through `$venv`. So the interpreter exists before the connector reads it.
- **Regression test:** the fresh-host test covers the exact failure path:
  - the only Python is bare `python` on PATH;
  - no venv exists, so a PowerShell function named `python` intercepts `-m venv`;
  - bundled Python is removed;
  - `CLOUDSDK_PYTHON` is unset.
  
  It asserts that the connector receives the absolute `$fakeVenv`, and that the variable is restored to empty afterwards.
- **Consistency:** the launcher and connector now choose the same interpreter in every case:

  | Case | Launcher | Connector |
  |---|---|---|
  | `CLOUDSDK_PYTHON` already set | Leaves it unchanged | Uses it |
  | Bundled Python exists | Leaves `CLOUDSDK_PYTHON` unset | Uses bundled Python |
  | Neither | Sets it to `$venv` | Uses `$venv` (also `sys.executable`) |

## Low findings are resolved

- **L1:** the connector now prefers bundled Python before `sys.executable`. `test_sdk_wrapper_requires_script_and_uses_python_fallback` asserts both branches.
- **L2:** the request body uses `ensure_ascii=False` with compact separators. The test arithmetic is sound:
  - 36,000 CJK characters escaped is more than 216 KB, which is over the limit;
  - the same text as UTF-8 is about 108 KB, which is under the 200 KB limit.
- **L3:** the duplicate README paragraph is removed, as reported.

## Residual observations (non-blocking, no change required)

1. **A user-set relative `CLOUDSDK_PYTHON` is preserved.** The connector then fails closed with the generic sign-in message, which is covered by `test_bad_sdk_interpreter_fails_without_spawn`. This comes from the user's own configuration, not from the launcher, so it is acceptable as is.
2. **The connector does not replicate `gcloud.cmd`'s `CLOUDSDK_PYTHON_ARGS`, such as a default `-S`.**
   - With bundled Python, this is irrelevant.
   - On the venv fallback, venv site-packages could in principle shadow SDK modules.
   - Live minting through both the configured SDK and the venv fallback is reported as proved on this host. Treat any recurrence as a host-specific issue, not a source defect.

## Proof conditions (not source failures)

1. **Promotion:** move production traffic from the old revision to this revision. Then run the connector with no `CLOUD_RUN_URL` against the base URL. After that, confirm:
   - IAM is unchanged;
   - the rollback revision and the `rules-only` tag are retained;
   - the legacy `rules-only` session still returns 200.
2. **Bundle:** confirm the final bundle matches this source and contains no credentials.
3. **Whole fresh machine:** an end-to-end first launch on a clean machine has not been run. The mocked PS5.1 regression covers the logic only.
4. **Accepted limits:**
   - The worst-case timing bound is 8 s for minting plus 35 s per socket read, against the 45 s client timeout.
   - A request that times out may still consume credits upstream. This is disclosed.
   - The `-Local` sampler expires 2026-11-09 05:19:36 UTC. The cloud default does not depend on it.

