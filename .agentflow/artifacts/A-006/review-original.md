# Review: A-006 captured-email spot check

**Bottom line:** I recomputed all of the report's counts from `metrics.json` and they match. The most urgent issue is pre-commit hygiene: an audit file the report calls private appears to sit in the public artifacts folder, and the run scripts contain machine paths and a GCP project ID. There are also two input and evidence-quality gaps the report doesn't disclose.

I only read the pasted sources. Anything that depends on private files is listed as a host check.

## Counts (verified)

| | Rules | Rules+Qwen |
|---|---|---|
| Phishing warned | 2 (`35c3`, `3622`) | 8 |
| Phishing no warning | 7 | 1 (`d4e5`) |
| Phishing failed | 0 | 1 (`58b6`) |
| Ham warned | 1 (`1831`) | 1 (`1831`) |
| Ham no warning | 9 | 9 |

- The six new warnings are `63a1`, `8b2e`, `a958`, `df4a`, `2373` and `2aea`.
- 17/19 completed results agree with the labels. The report correctly refuses to present that as overall accuracy.
- `analysis_complete` is 0 for every case, which fits `extraction_complete=False`.
- The time conversion is right: EST is UTC−5 on 2026-11-08.

## Fix before the local commit (INV1)

1. **`manifest-initial-unrun.json` is probably in the public folder.**
   - `finalize-a006.py` renames the draft to `.agentflow/artifacts/A-006/manifest-initial-unrun.json`, not into `private/`.
   - That folder shows as untracked (`?? .agentflow/artifacts/A-006/`).
   - Both the report ("private audit copy") and the manifest note ("draft private") say it is private.
   - The draft likely contains subjects and the invalidated labels.
   - **Check:** list A-006 and either move the file or correct the report before `git add`.
2. **The full manifest with subjects was written to the public path.**
   - Both scripts write a manifest that includes `subject` to `.agentflow/artifacts/A-006/manifest.json`. The committed file is a later projection without subjects.
   - **Check:** confirm only the projection gets staged.
   - **Check:** confirm `frozen_manifest_sha256` (`f58c…`) equals `freeze.json.selection_manifest_sha256`. The projection's own hash cannot match, so the report's "manifests bind" claim only holds for the private copy. Say that.
3. **The `work/` scripts expose local details.**
   - `run-a006.py` contains `C:\Users\pc297\…`, the GCP project `lateral-nomad-514001-c7` and the secret name `phish-tinker-key`. No key value is present.
   - Either leave `work/` uncommitted or redact these. That is your call, but "no app/provider key values" is only true in the narrow sense.

## Input quality (INV2/INV4): not disclosed in the report

4. **The subject redaction in `run-a006.py` can corrupt subjects.**
   - It collects every local part of 5+ characters from anywhere in the raw email, including sender, list and support addresses. It then replaces them in the subject case-insensitively, with no word boundaries.
   - Example: a local part like `security`, `support`, `service`, `account` or `admin` would turn "Security alert" into "[RECIPIENT] alert", or mangle "administrator". That can remove lure cues from phishing subjects or alter ham subjects.
   - The body pass in `finalize` has the same substring problem, but limited to `To:` local parts.
   - **Check (private):** count `[RECIPIENT]` in all 20 frozen subjects and bodies, and look at each hit. If any phishing lure word was replaced, disclose it per ID. If there are none, add "0 substitution artifacts".
5. **The report omits this pass from its chronology.**
   - The run script modified all 20 fixtures and re-stamped `frozen_at` 1.5 seconds before the first call (12:48:31.8 → 12:48:33.4).
   - This is still pre-inference, so INV2 holds. Add one line saying the final subject redaction ran inside the run script, right before inference.
6. **The overlap claim isn't checked by the script.**
   - `finalize` never asserts or prints `len(existing)`, so the figure of 223 prior fixtures isn't evidenced there. It also reimplements `clean()` while commenting "exact existing sanitizer".
   - **Check:** print the count and confirm it is 223.

## Evidence and benefit claims (AC3)

7. **Five of the six gains rest on weakly checked link findings.**
   - Five of the six new warnings include `deceptive_link`. `pot-237385b1ba7c` is `sender_impersonation` only.
   - In `evidence.py`, `verify()` accepts link evidence if `link_id` exists. It does not check a quote or the domain.
   - So the "evidence check rejected unsupported quotations" framing doesn't apply to most of the gains.
   - **Fix:** add a sentence saying link findings are checked only for the link's existence. The model's reasoning about domains is unverified explanation, not checked evidence.
   - For `pot-2aea4270287d`, confirm in the private row that the explanation actually mentions the sender/link domain mismatch.
8. **The Unicode bug can also misplace highlights silently.**
   - In `_normalize_with_map`, `out.append(c.casefold())` adds a multi-character string (`ß` → `ss`, `İ` → `i̇`) but only one `index_map` entry.
   - At the end of a string this causes `IndexError`, which matches the reproduction.
   - When an expanding character comes *before* a matched quote, the returned substring is shifted with no error. That would highlight the wrong text, breaking the module's own guarantee.
   - **Check (private):** for the 19 completed rows, confirm each kept text quote is a real substring that normalizes back to itself, and scan the bodies for `ß`, `İ` or `ŉ`. Disclose this second failure mode in "Next validation".
9. **The selection confound is understated where the headline is used.**
   - The people who wrote the rules hand-picked the phishing cases for "clear lures". That could favour lures the rules miss, which inflates the 2 → 8 contrast.
   - The judge line says "selected suspected-phishing cases". Change it to "hand-picked" and add that n=10 per class. The Wilson 95% interval for 8/10 is about 0.49–0.94.
10. **The short judge line may misdescribe the earlier test.**
    - The script docstrings describe `core` as Albert's samples plus handwritten cases, and `blind` as the Teddyha dataset. Neither is described as synthetic.
    - The line "captured public emails as well as synthetic examples" may be wrong. Check, or say "our earlier test sets".

## Minor

- `metrics.json` field `model_categories` appears to hold all categories, including rules findings (for example `ham-1831` urgency). Rename it or note this.
- `model_discarded` is parsed with `x.split()[4]` on a limitation string, which is fragile. Spot-check `d4e5`=2, `2373`=1 and `35c3`=1 against the private rows.
- `finalize` contains dead code: the `ast`/`ns`/`keep` setup and `assert80 if False else True`, which is a no-op. It's harmless but looks bad if published.
- For CC BY-NC 4.0 attribution, add the license link and "modified (redacted/transformed)".

## Proof limits

- I could not verify anything from private files: raw emails, model text, the journal, the `[RECIPIENT]` hits, or quote alignment.
- The failure attribution for `pot-58b65de0ae7b` stays "plausible". No model response was saved, and the report's wording is already appropriately hedged.
- The design and scripts support no early replay, no replacement and no retuning. That rests on `assert not private/a006-model.jsonl exists` and the single-pass structure, not on an independent log audit.

**If you only have time for two things before 08:00:** do item 1, then add the one-sentence disclosures for items 4/5 and 7.

