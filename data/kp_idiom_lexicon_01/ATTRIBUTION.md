# Attribution / License: kp_idiom_lexicon_01

- Content: headword titles only (one phrase per line, `idioms.txt`), taken from the English Wiktionary category **Category:English idioms**
  (https://en.wiktionary.org/wiki/Category:English_idioms), namespace 0 only. No definitions, example sentences, etymologies or page text are stored.
- Source: Wiktionary contributors, English Wiktionary, via the MediaWiki API (`action=query&list=categorymembers`).
- License of Wiktionary text: **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/) and GFDL.
- Retrieval: see `meta.json` (`fetched_at_utc`, `api_calls`, `n_titles`, `idioms_txt_sha256`). Reproduce with `fetch_wiktionary_idioms_01.py`
  (User-Agent set, sequential requests, backoff on HTTP 429). The runtime loads `idioms.txt` only; an sha256 mismatch against both the constant in
  `er125_kp_rescue_production_01.py` and `meta.json` disables the idiom exception entirely (fail-closed).
- Use in this repository: internal matching of candidate Key Phrases against headwords (a membership test). The list is not republished or shown to
  learners; learner-facing output contains only phrases taken from the article text. If a composite artifact containing this list is ever published
  externally, keep this attribution file with it (ShareAlike applies to the list itself).
- The previous Trial snapshot (2026-09-27, 10,632 titles, `er023_output/key_phrase_db_trial_01/db/wiktionary/idioms.json`, sha256
  `79956b90bf29df26710d1cbf1afcf1ddb6a871603e751b8446767a6db7793cff`) is superseded by this snapshot; update procedure: re-run the fetch script,
  review the diff of added/removed headwords, update `LEXICON_SHA256` in `er125_kp_rescue_production_01.py`, re-run `er125_kp_rescue_production_test_01.py`.
