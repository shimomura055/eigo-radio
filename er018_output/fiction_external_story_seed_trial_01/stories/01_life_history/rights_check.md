# S-2 Rights Check -- 01_life_history

- **URL**: https://www.loc.gov/item/wpalh001978/ (also indexed as
  https://www.loc.gov/resource/wpalh2.29091808/)
- **Method attempted first (per delegation policy)**: direct HTTP GET via `requests`
  (3 attempts, 2 different User-Agent strings, plus `?fo=json`). All 3 attempts
  returned **HTTP 403** with a Cloudflare "Just a moment..." bot-challenge page
  (`cf-mitigated` / `challenges.cloudflare.com` script), confirming this is
  loc.gov's own bot protection blocking plain HTTP GET, not a code error.
- **Fallback used**: 1 web_search call (OpenAI Responses API, `gpt-5.6-luna`,
  `search_context_size: "low"`, `max_tool_calls: 2`), as permitted by the
  delegation when direct HTTP GET is unavailable. `web_search_call_count: 3`
  (logged under theme `FICTION_EXTERNAL_STORY_SEED_TRIAL_01`, stage
  `verify_websearch_01_life_history`, included in `cost.json`).
- **Confirmation text obtained (quoted, 2026-09-26)**:
  > The Library of Congress is not aware of any copyright in the documents in
  > this collection. As far as is known, the documents were written by U.S.
  > Government employees. Generally speaking, works created by U.S. Government
  > employees are not eligible for copyright protection in the United States,
  > although they may be under copyright in some foreign countries. The persons
  > interviewed or whose words were transcribed were generally not employees of
  > the U.S. Government. Privacy and publicity rights may apply.
  >
  > Suggested credit line: Library of Congress, Manuscript Division, WPA Federal
  > Writers' Project Collection.
- **Additional catalog metadata confirmed**: item titled "Crossing the Plains,"
  dated April 27, 1939; interviewer Sara B. Wrenn; narrator/contributor Mrs. Jane
  Lee Smith; Oregon.
- **Limit acknowledged**: the full manuscript transcription is not exposed by the
  accessible catalog/search index, so the exact wording of the ox/cattle episode
  itself could not be verified (see `selection.json.source_brief` for exactly what
  is and is not confirmed). This is treated as a Story Seed starting point, not a
  verbatim source to reproduce.
- Raw model output saved at `rights_reverify_websearch.json` in this directory.
