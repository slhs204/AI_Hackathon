# phishhook (copied rule engine)

`engine.py`, `directory.json` and `drill_bank.json` are copied **unchanged** from Albert's
prototype `1_pause_check_pay_v2/phishhook/` (2026-11-07). The FastAPI backend wraps
`engine.analyze_contract()`; it does not edit the engine.

To pick up Albert's changes, copy the three files again and run `pytest`.
Check that the copy is identical with `shasum phishhook/engine.py`.
