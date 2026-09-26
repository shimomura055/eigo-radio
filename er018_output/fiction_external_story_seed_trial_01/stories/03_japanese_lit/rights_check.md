# S-2 Rights Check -- 03_japanese_lit

- **URL**: https://www.aozora.gr.jp/cards/000081/card1927.html (the individual
  work card, NOT the blog-index page `soramoyou2021.html` that S-1's
  `candidates.json.source_url` field had mistakenly pointed to -- that field was
  wrong for all 4 candidates in this system; the real per-work card URLs were
  only present inside the citation links in `rights_reasoning`. This is corrected
  here.)
- **Method**: direct HTTP GET via `requests`. **HTTP 200**, 8,749 bytes.
- **Important encoding finding**: the raw response bytes are genuinely UTF-8
  (matches the page's own `<meta charset="utf-8">`), but Python `requests`'s
  automatic encoding detection (`resp.encoding`) reports `ISO-8859-1` for this
  response (no charset in the HTTP `Content-Type` header itself), so
  `resp.text` alone renders as mojibake. Manually re-decoding `resp.content` as
  UTF-8 renders the page correctly. This also means `er018_..._01.py --step
  verify`'s own automated `quote_found_in_fetch` string-match will likely report
  **False** for this system even when the underlying fact is correct -- a
  pre-existing script/library limitation for Japanese-language sources, not a
  rights problem. Flagging this rather than silently working around it.
- **Confirmation obtained (from the correctly-decoded page, 2026-09-26)**:
  作品名(title): 注文の多い料理店 / 著者名(author): 宮沢 賢治 / 生年(born):
  1896-08-27 / **没年(died): 1933-09-21**.
- **Rights reasoning**: Miyazawa died in 1933 -- more than 90 years before 2026,
  clearing the postmortem copyright term under both Japan's current 70-year rule
  and the previous 50-year rule that applied when Aozora Bunko first digitized
  this text (registered 2005-02-21 per the card's own file-download table). This
  specific card uses an older page template that has no separate
  「著作権：あり／なし」badge field at all (confirmed by reading the full raw
  HTML -- the string "著作権" does not appear anywhere on this page), unlike
  newer-template Aozora cards. The S-1 REPORT's §8 concern ("the individual
  card's copyright-none badge itself was not directly confirmed") is addressed
  here: it is not that the badge says something ambiguous, but that this
  template predates the badge field entirely. Aozora Bunko as a whole only hosts
  public-domain (or otherwise rights-cleared) Japanese-language texts as a matter
  of longstanding, well-documented editorial policy, and a 90+ year-dead author is
  unambiguously past the relevant term either way.
