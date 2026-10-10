# INVENTORY_01: A4 DualModel OR Trial Phase 1 棚卸(課金API 0件、2026-10-10)

結論: **Human判定(A/B/C/D、境界ラベルC-B/B-C/C-D)の所在がリポジトリ内で確認できない => STOP条件に該当。Phase 1の残り(dm_driver.py / PREREGISTRATION_01.md)は作成していない。**

## 1. 評価セット候補の事実表
| 項目 | (a) POST-EN-TRIAL-01 英語稿 | (b) ANTENNA-TRIAL-01 日本語R0 |
|---|---|---|
| 記事数 | 11(U01-U08, X09-X11。うちSTOP稿U07/U08/X11、旧稿X09/X10) | 9(3テーマ byd_recall/space_weapons/streaming_price x R0モデル luna/sol/astra) |
| 完全台帳 | あり(11本ともEmbedded=research_ledger一致、LEDGER_COMPLETENESS_01.md) | あり(FIX02で9記事同一sha・同一文分割) |
| splitter | post_en_common(EN)。X09/X10/U08等の文ID安定、ただしU08 s25は`.”`で結合 | R._split_sentences(JA) |
| 既存A3/A4の実行モデル(実測) | gpt-6.1-sol のみ(22 call、cost_ledgerのmodel列) | gpt-6.1-sol のみ(54 call = 9x6レベル、flagger_model=gpt-6.1-sol) |
| Prompt sha | A3=9d995042...(9d9950428419c3af...3538e9) / A4=c87b95e5...(c87b95e5bcf1b5c2...ef01) | 同一 |
| Union Flag | 29件(問題単位23) | A3/A4のFlag(HUMAN_CHECK_ANTENNA_01.md、レベル別一覧) |
| Human A/B/C/D判定 | **リポジトリ内に無し**(下記2) | **無し**(HUMAN_CHECK_ANTENNA_01.mdは「有用/ノイズの最終判定はユーザー」と明記、ラベル欄なし) |

## 2. Human判定の所在(事実)
- `post_en_trial_01/HUMAN_REVIEW_POST_EN_01.md` はユーザー確認用一覧(Union 29件、理由、Known/New)であり、A/B/C/D欄・判定は無い。「有用/不要の判断は未確定(ユーザー確認用)」と本文に明記。
- `pre_sorter_blind_trial_01/PREREGISTRATION_01.md` L23/L46・`RESULT_01.md` L3/L184: 「User/ChatGPTのA/B/C/D判定はリポジトリ参照せず、Claude(Sonnet/Fable)とも未見。照合はChatGPT側」と明記。
- grep(docs/pm, ER-*_REPORT.md, er052_output/writer_dev_risk_flagger_01)で Union29に対するA/B/C-B/B-C/C-D/D判定を記録したファイルは **0件**(C-B等のヒットは無関係の旧タスク)。
- 結論: ユーザー/ChatGPT判定は **所在未確認**(ChatGPT側会話にある可能性。リポジトリには無い)。件数・ラベル分布・誰の判定かは推測しない。
- Antenna(b)にもHuman判定なし。

## 3. Luna既存結果の再利用可否
- Luna(gpt-6-luna)がRisk Flagger(A3/A4 Prompt)として走った保存artifact = `meta_rollback_crossmodel_01/runs/luna/`(META 1記事 er019 run_03、A3/A4各1call)のみ。POST-EN/Antenna評価セットの記事ではない。
- `antenna_trial_01/flags/*/gpt-6-luna.json` の gpt-6-luna は R0 **Writer**(model_r0)で、Flaggerは flagger_model=gpt-6.1-sol(実測確認)。`pre_sorter_blind_trial_01` のLunaはPre-sorter(別Prompt、Flaggerではない)。
- 結論: **Luna A3/A4・Gemini A3/A4は全件新規実行が必要(再利用0 call)**。

## 4. Gemini確認(2026-10-10実測、課金なし)
- GEMINI_API_KEY読込=True(bool)。models list(HTTP 200、62件)に `models/gemini-3.5-flash-lite` 実在(generateContent対応)。
- 価格(ai.google.dev/gemini-api/docs/pricing、本日再取得): gemini-3.5-flash-lite $0.30 in / $2.50 out(thinking込み)。xm_prices_01.json(2026-10-10T04:50Z)と一致。
- **注意: 「これより安価なFlash-Lite系が無い」は成立しない**。旧世代 gemini-3.1-flash-lite($0.25/$1.50)、gemini-2.5-flash-lite($0.10/$0.40)が同listに実在し、より安価。3.5-flash-liteは最新世代のFlash-Lite(PM_GOVERNANCE 25節の最新原則に整合)。「最廉価」の定義(最新世代内か全世代か)はFable/ユーザー判断が必要。

## 5. 費用見積
estimate_01.json 参照。必要call: POST-EN 11記事 x 4条件 = 44 call(全て新規)。中央JPY10.3 / 高位JPY33.6(再試行各1回を含む最悪約JPY67)。Antenna 9記事なら36 call、約JPY9-10(概算)。JPY100目安内。

## 6. 未実施(STOPのため)
dm_driver.py / `--dry-run` / aggregate_dm_01.py設計 / PREREGISTRATION_01.md は未作成。再開にはHuman判定の所在確認(ユーザーがChatGPT側判定をリポジトリへ持ち込むか)が必要。
