# Fresh captured-email spot check

Dobby's Catch uses rules and Qwen to identify warning clues in visible email text. This small check tests whether it can handle captured public email rather than only our handwritten demo messages. It compares the same frozen inputs with and without Qwen.

**Result:20 planned,19 analysis results,1 processing failure.** Of 10 provisionally phishing-labelled messages, rules+Qwen warned on 8, returned no findings on 1, and failed processing 1. Of 10 source-ham messages,1 was warned and 9 were not. Rules alone warned on 2 of 10 phishing and 1 of 10 ham. Six additional phishing cases gained warnings with Qwen. All returned analyses stayed incomplete; no result establishes safety or payment approval.

The run finished at **2026-11-08 07:48:49 EST**, before the 08:00 deadline. There were 20 underlying Tinker calls, no correction retry, no post-result sample replacement or prompt/runtime change. The product authors hand-picked the 10 suspected-phishing cases before seeing outputs, which can favour the observed contrast. This is a **purposive spot check with provisional labels**, not a real-world accuracy benchmark or payroll validation. Full planned denominator 20 and the failure are retained; do not present 17/19 successful-result agreement as overall accuracy.

## Sources and selection

- [Phishing Pot](https://github.com/rf-peixoto/phishing_pot), by [rf-peixoto](https://www.linkedin.com/in/rf-peixoto), pinned commit `78be141545ed9e56eefb857808ac78e83eb81b81`. The dataset card describes messages actually received by controlled/long-observed addresses. [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/); inputs modified by redaction/transformation. This is noncommercial educational evaluation; no raw corpus redistribution or commercial-use permission claimed.
- [Apache SpamAssassin public corpus](https://spamassassin.apache.org/old/publiccorpus/readme.html), archive `20030228_easy_ham.tar.bz2`. The source identifies non-spam messages posted publicly or supplied with awareness of publication; message copyrights remain their original senders. No messages were injected into any live mail system.

The 20 actual inputs were frozen before paid calls. Ham:10 messages selected by seeded SHA 256 ranking. Phishing:10 messages purposively selected from the first 60 seed-ranked PhishingPot candidates for visible account/payment/security lures and category variety. Generic marketing, unreadable/oversized content and ambiguous material were not automatically called phishing. This selection was made before model output and is **not random**. Phishing labels are the host's provisional content assessment supported by corpus provenance, not independent expert-adjudicated gold. Source-ham means non-spam, not proven harmless.

There was no exact normalized-body match to prior core/blind fixtures. This does not establish no campaign/fuzzy overlap or absence from model pretraining. The ham set is from 2002; the phishing collection includes multilingual/newer mail, creating strong source/time/language confounds. These are not representative modern payroll emails.

## What was tested

Runtime commit `e120308`, unchanged Qwen3-8B/v3, temperature 0.2, max 4000 tokens, 30 s timeout, max 3 workers. Same production analysis code and Tinker API were used locally. This run **did not traverse Cloud Run or the Gmail extension**. Inputs approximate Gmail-visible content from MIME: raw authentication headers, Reply-To and attachment contents excluded; sender display names suppressed, email localparts/IPs/long numeric identifiers and URL query/fragments minimized. This is not certified anonymization; transformations can change identity/link cues. Raw emails and full model text remain in ignored private files. The exact frozen private manifest matches the recorded digest; the public manifest is a projection with subjects removed, not a byte-identical copy.

Before inference, validation caught a draft mbox-envelope parsing mistake and mixed marketing/phishing source labels. Both were corrected and the selection refrozen before any paid output. A final subject-redaction pass ran inside the runner immediately before inference and the final freeze. Host inspection found 8 [RECIPIENT] substitutions across 4 messages: 3 ham mailing-list identifiers and 1 phishing user ID. No removal of a security/account/payment lure word was observed; these context changes remain a limitation. The initial draft was never run; its private audit copy remains. Manifests bind original-source and transformed-input hashes, runtime, prompts and generation settings. Rules used the same frozen transformed inputs.

## Inspectable examples and failures

- **Additional warning:**`pot-2aea4270287d`, a captured hardware-wallet 2FA activation/suspension lure. Rules had no warning; Qwen added a deceptive-link finding anchored to **Activate 2FA**. It noted the mismatch between the claimed sender and link domains. This is an inspectable clue, not independent proof that a domain is malicious. Live targets were not opened.
- **Normal message without warning:**`ham-b0f5f3a12357`, an archived technical discussion. Neither path warned; no safety conclusion follows.
- **False alarm retained:**`ham-1831c0e59b13`, an archived software traceback discussion, received a rules-based urgency warning anchored to **today** in both paths. Adding Qwen did not fix it; no retuning was performed.
- **Miss retained:**`pot-d4e53126383c`, an exchange-account identity-confirmation lure, had no retained warning. The evidence check rejected 2 unsupported model quotations. Rejecting unsupported text is useful, but **the case still counts as a missed warning**, not a success.
- **Processing failure retained:**`pot-58b65de0ae7b`, German bank 2FA text, produced an `IndexError` before a completed analysis row was saved. Its provider call was attempted; it was not replayed or replaced. Separately, local tests reproduce an index-map failure for German sharp-s casefold expansion in evidence matching; this is a plausible related defect, not an exact captured per-request stack trace. Source was left frozen.

All 14 retained finding snippets were checked by the host and occur verbatim in the submitted fields. All retained model findings use text-evidence matching; a deceptive_link category does not itself mean domain reputation was verified. Five of the six additional-warning cases include model link explanations. Claims about domain legitimacy or maliciousness remain unverified explanations, not independent URL/reputation checks. No completed-row input had a casefold-expanding character; the failed German input did.

## All 20 cases

| Case | Label | Rules warning | Rules+Qwen warning | Status |
|---|---|---|---|---|
| ham-8fbea4b8839d | legit | no | no | completed_partial |
| ham-138b12553770 | legit | no | no | completed_partial |
| ham-1831c0e59b13 | legit | yes | yes | completed_partial |
| ham-b0f5f3a12357 | legit | no | no | completed_partial |
| ham-1aefed29d3ad | legit | no | no | completed_partial |
| ham-2bc77a45c897 | legit | no | no | completed_partial |
| ham-7933961b53fa | legit | no | no | completed_partial |
| ham-52e86e8bd492 | legit | no | no | completed_partial |
| ham-9a06cd7bb4ee | legit | no | no | completed_partial |
| ham-1c17f3f04aaf | legit | no | no | completed_partial |
| pot-58b65de0ae7b | phishing | no | failed | processing_failed_IndexError |
| pot-63a1c05e2a47 | phishing | no | yes | completed_partial |
| pot-8b2ed31f6061 | phishing | no | yes | completed_partial |
| pot-a958a0028317 | phishing | no | yes | completed_partial |
| pot-df4ae155db88 | phishing | no | yes | completed_partial |
| pot-237385b1ba7c | phishing | no | yes | completed_partial |
| pot-35c325c80421 | phishing | yes | yes | completed_partial |
| pot-36229780890c | phishing | yes | yes | completed_partial |
| pot-2aea4270287d | phishing | no | yes | completed_partial |
| pot-d4e53126383c | phishing | no | no | completed_partial |

## What to tell judges

“We tested a hand-picked set of 10 suspected-phishing emails and 10 archived non-spam emails from public collections. Rules plus Qwen flagged 8 of the suspected-phishing messages, compared with 2 using rules alone. We also saw one false alarm, one missed warning and one processing failure. This is an initial spot check, and we kept every outcome.”

For a shorter live-demo line: **“We added captured public emails to our earlier test sets, and kept the errors visible.”** Keep the detailed counts ready for questions; the earlier 97/100 test is a different dataset and must not be merged with this one.

## Next validation

Obtain independently reviewed labels, contemporaneous ham and genuine payroll/BEC cases; test unredacted-domain/identity effects under authorized privacy controls; repair/retest Unicode evidence mapping separately, including silent misaligned highlights when expanding characters occur before a quote. No learning-outcome or payment-safety claim follows from this run.

Follow-up **B-001 (proposed): Unicode evidence matching** is recorded for a separate repair and regression; this evaluation did not modify or redeploy the product.

Machine-readable [all-case metrics](REAL_EMAIL_SPOTCHECK.metrics.json) and [source/input hash manifest](REAL_EMAIL_SPOTCHECK.sources.json) support this report. Exact frozen inputs and journal are retained privately; no original message bodies are republished.
