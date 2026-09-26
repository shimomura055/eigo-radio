# Rights check -- 03_japanese_lit_1 (Akutagawa, Rashomon)

- **Card URL**: https://www.aozora.gr.jp/cards/000879/card127.html
- **Full-text URL**: https://www.aozora.gr.jp/cards/000879/files/127_15260.html
- **Method**: direct HTTP GET (`requests`), no web_search. Both returned HTTP 200.
- Author Ryunosuke Akutagawa died 1927-07-24 (card metadata field 没年, confirmed
  in the raw fetched card page). Well past any Japanese copyright term (50 years
  from death under the law in force during most of this term, and even 70 years
  under the 2018 revision expired in 1997/2018 respectively).
- Aozora Bunko hosts complete downloadable files for this work (plain-text zip,
  .ebk, and XHTML), consistent with Aozora's operating policy of only hosting
  full-text downloads for works whose copyright has expired ("著作権の切れている
  作品については、了解を求めたりする必要はありません" -- Aozora's general
  policy, previously confirmed via web_search in Trial-01 and consistent with
  this Trial's direct fetch of the same card).
- Known limitation (carried over from Trial-01's note): this specific card uses
  Aozora's older page template, and this Trial's attempt to re-fetch the
  individual "copyright: none" badge text via direct HTTP GET hit encoding
  inconsistencies in the raw page (mixed Shift_JIS/UTF-8 artifacts on this
  legacy template); this does not affect the full-text file itself, which
  fetched and decoded cleanly (see primary_text_excerpt.md).
