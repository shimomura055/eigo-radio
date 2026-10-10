# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_16 (CURRENT_SPEC更新 + 完了条件照合表)

実行日: 2026-10-11 / 実行層: Sonnet 5.5 / ドキュメント作業のみ(API 0件、コード変更なし、run実行なし)。
並行: 委任_15(META再生成)が DECISION_LOG.md / er019_output/meta / review_queue / 委任ログ_15 を担当。本委任はそれらを編集せず、METAのrun dirも読んでいない。

## 実施
- CURRENT_SPEC.md: 新節「Family X Production経路 — W-1 Fact Lock Writer + Risk Flagger + Review Queue」追加(経路全体図、RF 4条件・Prompt sha・非Blocking・Queue構造、旧Fact Checker撤去、U-1/U-2、単価登録[gemini-3.5-flash-lite / gpt-6-luna OPEN-251]、L3 runtime evidence)。旧記述4か所(AN3節の適用path、Family X音声構造節の項4/項5、OPEN-233 Production Flow仕様見出し)へ「撤去済み(2026-10-10)」注記、冒頭に更新行。既存文言は削除・改変していない。Status=配線済み(最終Gate判定待ち)、PRODUCTION_WIREDとは記載せず。
- 照合表: er053_output/risk_flagger_production_wiring_01/completion_matrix_01.md(完了条件は逐語19項目[委任文は18点]、STOP条件7点、承認内容 vs 実挙動対応表)。
- OPEN_ITEMS.md: OPEN-244行に委任_16進捗を追記(closeせず)。

## 未確認(別途確認要)
- Luna RF effort=medium / W-1 R0 effort=high は承認文に明示値がなくコードのTrial移植値(一致と推定)。
- L3のadvanced stage 2 callのうちどちらがM1(a)のIn one lineかは未識別。
- audio側KP選定・TTS・ASRのmodel_id逐一照合は未実施。
- a2 derived sha警告、retry_count=0、META結果は委任_15で確認中。
