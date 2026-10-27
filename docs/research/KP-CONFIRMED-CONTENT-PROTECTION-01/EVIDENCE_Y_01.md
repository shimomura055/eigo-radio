# EVIDENCE_Y_01(Family Y。コピーdir実測)

コピー元: `er121_output/family_y_production_01/sns_age_limit/run_01`(a2・b1bともREVIEWED)→ `er128_output/evidence_01/y/run_kcp2b_ev_y_01`(runnerへはNTFS junction `er121_output/family_y_production_01/sns_age_limit/run_kcp2b_ev_y_01`で接続。終了時にjunctionのみ撤去)。

| # | 手順 | 結果 | 証跡 |
|---|---|---|---|
| 0 | 旧run G1 | PASS(レコード無し) | y/00_legacy_g1_*.txt |
| a | payload→`confirm --from-form --actor evidence`(a2 KP3 / b1b KP3+vocab2、文法なし) | rc=0。revision 1。確定後G1 PASS | y/01_confirm_form_*.txt, 02_g1_after_confirm_*.txt |
| b | 改変マトリクス(実artifact) | G1 英語/日本語訳/vocab訳/category/assets copy訳、G2 TTS英語/日本語、G3 a2ページ(`pages/index.html`)訳 → すべてBLOCK。復元後 PASS | y/10_tamper_matrix.{txt,json} |
| b' | 実runner `--stage tts_a2 --mode real --approved-budget-jpy 1` に改変を載せて起動 | rc=2。ただし停止理由は runner の旧run前提(`style_profile.json`未作成: 既存run記録の混在防止)で、確定内容保護より前。cost_log.jsonl は 146行のまま(API 0) | y/11_realrunner_tamper_tts_a2.txt |
| c | resume / STALE再バインド / STALE ISSUE(実`ensure_kp_review`。本文は`ys.canonical_body(translate/<lv>.md)`) | a2・b1bとも resume=FINALIZED(Redundancy QA stub 1〜2回=既存仕様M-8)、再バインド=revision 1→2・G1 PASS、ISSUE=PENDING・レコード不変 | y/20_ops.{txt,json} |
| d | 操作ガード | すべて LOCKED | y/20_ops.txt |
| g | 公開URL G3(read-only): `https://shimomura055.github.io/eigo-radio/user_test/family_y_production_sns_age_limit_01/index.html`(HTTP 200)に対し、コピー確定レコードの訳(線を引く/別の疑問を持ち出す/大人に頼る)を `verify_outputs` で検査 | PASS | y/50_public_g3.txt |
| h | Std「～」表示 | Yの既存a2に「～」gloss無し→単体test(`test_y_std_user_page_shows_display_gloss`)で表示=確定gloss・TTS入力不変 | `er128_kp_confirmed_content_02b_test_01.py` |
| runtime mock | stage_kp G1 が実行時に発火 | PASS(単体test `TestYStageKpG1Runtime`) | 同上 |

**限界(判断候補)**: このコピー元runには `study_text`(Part 1/Part 2)が無く、現行Y runnerの `tts_b1b`/`gate`/`pages` は `_assert_study_ready` で Part 1/2 を要求し、`tts_a2` は旧run記録(style_profile無し)でSTOPする。runner段階の成功(a)(c)(e)をYの実runで取るには新規の有料生成(本文〜Part 1/2)が必要で、¥30枠・コピーdir方針を超えるため行わず、関数レベル(実artifact)+mock runtime testで代替した。
モデル/routing: 本Family分の新規API 0(¥0)。
