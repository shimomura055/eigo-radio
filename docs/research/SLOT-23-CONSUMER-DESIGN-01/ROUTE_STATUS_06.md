# ROUTE_STATUS_06 6経路×受入条件14の対応表(F班evidence時点。PRODUCTION_WIRED判定はFable)
凡例: **E**=runtime EVIDENCE取得(DEV複製run)/ **E△**=EVIDENCE取得だが条件付き(注) / **未**=未取得(理由)/ **他**=他班・Fable・SSOT担当。条件定義=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md` §6。
証跡=`EVIDENCE_RESULT_06.md`・`BROWSER_CHECK_06.md`・`COST_06.md`・`evidence_runs/`。

| # | 条件 | Y Std | Y Adv | Z Std | Z Adv | X Std | X Adv |
|---|---|---|---|---|---|---|---|
| 1 | 正式初回経路に①②③表示が接続 | E(new_review→マーク→display_spec→Part 1→装飾→G3、実runner) | E | E | E | **E△**(runner `player`はE。公開page builderは不具合D-F1でSTOP) | **E△**(公開builderはStdと同一pageでSTOP) |
| 2 | ②で解説全文が生成・表示 | E(Part 1=①+②5件、`gpt-6-luna`、日本語=作業仮定A。**英語化は未実装・ユーザー確認中**) | E(同、Adv golden不変) | E | E | E△(player。公開page未) | E△ |
| 3 | 表示強度=承認仕様 | E(computed style・画素差分、PC/375/390) | E | E | E | E△(player.html。公開page未) | E△ |
| 4 | ③日本語意味表示 | E(`ul.lk-meaning`=確定gloss逐語) | E | E | E | E△(player) | E△ |
| 5 | 確定内容と記事表示一致 | E(`data-hl`件数・id集合=確定、cmp同一) | E | E | E | E△(player) | E△ |
| 6 | retry/fallback/regeneration/resume整合 | E(pages再実行sha同一・API 0、`kp_part1_a2` regenerate+確定不変。fallback/Local Rewriteは対象外=未) | E(pages再実行は同一ページ) | E(同) | E | E△(player再実行sha同一・study_text reuse。`--regenerate-stage`なし) | E△ |
| 7 | DEV/Trial専用経路でない | E△(正式runner `er121_family_y_runner_01.py`だが記事はDEV複製run=evidence。実記事の正式初回は未) | E△ | E△(`er026…runner`) | E△ | E△(`er019…runner`) | E△ |
| 8 | 正式runtimeでの発火証拠 | E(DEV run dir。**実記事の公開runではない**) | E | E | E | E△ | E△ |
| 9 | 必須Regression/Validator/Integration PASS | 他(M班`REGRESSION_M_01.md`。F班は新規実行なし) | 他 | 他 | 他 | 他 | 他 |
| 10 | actual model_id・routing・Prompt・Style | E(`gpt-6-luna`=requested、Part 1 Adv template sha不変/Std=`PROMPT_TEMPLATE_SHA256_A2`、TTS=`gemini-3.8-flash-lite-tts`) | E | E | E | E | E |
| 11 | Fable独立受入 | 他 | 他 | 他 | 他 | 他 | 他 |
| 12 | SSOT更新 | 他(文案=`RESULT_PACKET_S23F.md` §7) | 他 | 他 | 他 | 他 | 他 |
| 13 | Git反映 | E(F班evidence docs/toolsのcommit。Productionコードは変更なし) | 同 | 同 | 同 | 同 | 同 |
| 14 | 未承認仕様の参照/Dangling無し | 未(F班は追加Grepなし。M班`IMPL_M_01.md` §3のGrep総括を参照) | 未 | 未 | 未 | 未(+D-F1: 標準builderが参照する`public_study_html`のPart 1がb1b限定のまま=旧規則の残存) | 未(同) |

## AI島(X Std/Adv 実記事 `ai_island_temple__run_form_prod_01`)
F班は触っていない。**「AIF委任_06で適用中」**(AI島 run のreconsume/再ビルド/公開は別委任)。注意: 不具合D-F1(X標準公開builderのStd Part 1)がAI島のStd再ビルドにも影響する見込み(AIF委任_06が標準builder経由[`tools/build_aif3_listening_page_01.py`ラッパ]を使う場合)。修正はProductionコード変更のためFable判断(次委任案: `er120_part2_wiring_01.public_study_html`のlevel化)。

## 総括
- Y Std/Adv・Z Std/Adv: 条件1〜8・10は**EVIDENCE取得**(条件7/8は実記事ではなくDEV複製runの正式runner発火)。条件9・11〜14は他班/Fable。→ WIRED判定可能な材料は揃った(判定はFable)。
- X Std/Adv: runner `player`段まではEVIDENCE。**公開page(標準builder)は不具合D-F1により未取得**。D-F1修正後に再取得が必要(X公開pageの`check_page(public)`・mp3生成・公開ページ上のブラウザ検証)。
