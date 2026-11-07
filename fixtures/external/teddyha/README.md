# Teddyha/phishing_benign_email_dataset (blind test set)

- Source: https://huggingface.co/datasets/Teddyha/phishing_benign_email_dataset
- License: MIT (per the dataset card). Copied here unchanged for evaluation.
- 200 rows: 100 phishing, 100 benign. Fields: id, subject, body, intent, technique, target,
  spoofed_sender, label. Mostly credential harvesting and malware; 1 BEC (wire) row; no payroll rows.
- Downloaded 2026-11-07 with the Hugging Face datasets-server `rows` API (`rows_0.json`, `rows_100.json`).

Nobody on the team wrote these emails or tuned the rules to them, so they are the closest thing we have
to a held-out test. URLs inside may be real malicious links: never open them. The backend never fetches URLs.

Convert with `backend/.venv/bin/python fixtures/convert_teddyha.py`, then run
`cd backend && .venv/bin/python -m eval.run_eval --set blind`.
