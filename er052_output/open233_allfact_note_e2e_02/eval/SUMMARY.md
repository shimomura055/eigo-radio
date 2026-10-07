# SUMMARY OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02(2026-10-07、Trial限定・Production無関係)

Status = **USER_DECISION_REQUIRED**(Fable判定。VALIDATED不可: P2版Fact誤り件数が従来版を下回らず、hormuzでは上回る(P2 8/10件 vs 従来2件)。REJECTED不可: n=2/テーマ・brief採用factが版ごとに異なりNote由来かrun揺れか切り分け不能、meta HC-012のrollback表現はP2 2/2で「正しい」)。Production採用判断なし。Checker構成はAPPROVED_FOR_PRODUCTION(OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01)・PRODUCTION_WIRED未のまま不変。残11 run待機。

## 1. 評価表(15 run: P2 10本 + 従来版(TRIAL-04 Control rep1)5本)
summary_*.json 3ファイルで検算済み: 全15 runのFact誤り合計(space_weapons・従来版のEN/JA併記を含む)・★分類・退行・Checker項目は下表と齟齬なし。

| run | Fact誤り合計(JA R2/EN最終) | ★分類 | 退行 | Checker誤許容 | Checker final/cycle/Rewrite |
|---|---|---|---|---|---|
| meta P2 r1 | 5 | HC-012 正しい | 3 | 2 | REWRITE_THEN_DOWNGRADE/2/有 |
| meta P2 r2 | 7 | HC-012 正しい, HC-014 曖昧 | 3 | 6 | REWRITE_THEN_DOWNGRADE/3/有 |
| meta 従来 | 4 | HC-012 正しい | 1 | 2 | REWRITE_THEN_DOWNGRADE/2/有 |
| hormuz P2 r1 | 8 | HF-007 曖昧 | 4 | 6 | REWRITE_THEN_DOWNGRADE/3/有 |
| hormuz P2 r2 | 10 | HF-007 正, HF-009 正 | 4 | 5 | REWRITE_THEN_DOWNGRADE/2/有 |
| hormuz 従来 | 2 | HF-007/008/009 正 | 0 | 0 | STAGE2_DOWNGRADE/1/無 |
| space_weapons P2 r1 | 1 | ★なし(参考 全て正) | 0 | 0 | STAGE2_DOWNGRADE/1/無 |
| space_weapons P2 r2 | EN5/JA7 | ★なし(参考F-001 JA重大誤読・EN曖昧) | 2 | 2 | REWRITE_THEN_DOWNGRADE/5/有(EN側) |
| space_weapons 従来 | EN2/JA3 | — | 0 | 0(json) | REWRITE_THEN_DOWNGRADE/3/有 |
| sewer P2 r1 | 4 | F-012 曖昧 | 2 | 4 | STAGE2_DOWNGRADE/1/無 |
| sewer P2 r2(再実行版) | 5 | F-010 正 | 3 | 3 | STAGE2_DOWNGRADE/1/無 |
| sewer 従来 | 6 | F-012 正 | 1 | 3 | STAGE2_DOWNGRADE/1/無 |
| ai_control P2 r1 | 6 | ★なし | 3 | 1 | REWRITE_THEN_DOWNGRADE/3/有 |
| ai_control P2 r2 | 4 | CONTROL-003 正 | 1 | 3 | REWRITE_THEN_DOWNGRADE/4/有 |
| ai_control 従来 | 5 | ★なし | 1 | 3 | STAGE2_DOWNGRADE/1/無 |

注: space_weapons 従来のChecker誤許容は指示表で「—」、summary_space_weapons.jsonでは0。

## 2. 重大3件(読者を誤らせる水準、全文)
1. meta P2 r2 JA「ただし、主役になった人間が知らされていなかった。」(開示対象を契約スタッフ本人に取り違え。ENはCheckerが別の根拠なし表現へ書換)
2. space_weapons P2 r2 JA「つまり今回の発表は、「衛星を狙う兵器を配備した」と単純に読む話ではありません。宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」ほか1文(台帳F-001の配備承認を超える。ENはCheckerがRewriteで修正、JA未修正)
3. ai_control P2 r2 CheckerのRewrite誤動作: 「The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.」→無関係な「In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.」に置換(cycle2で削除、元の内容は最終ENから欠落)。→ OPEN-238

## 3. 横断所見
- 全10 runで両Note(多義+従来notes)がbriefに逐語到達(10/10 ALL_PASS)。brief長は従来の約2倍。
- Checker最終重大は10本とも0だが、独立評価では誤り残存(Checker通過≠品質保証)。
- JA R2はChecker対象外のため、ENで修正・削除された問題文がJAに残りJA/EN不一致(ai_control r1, space_weapons r2, meta r2)。→ OPEN-239
- Checker判定ぶれ(同種の支払義務者問題をr1 ACCEPTABLE/r2 BLOCKING)。

## 4. 費用・時間
実費≈¥110.4(phase1 ¥43.4 / EN ¥14.2 / Checker ¥52.7。sewer rep2停止1回分は未記録・数円推定)/上限¥300。時間: Phase A 16分、Phase B 15分、評価(3並列)約7分、準備(並列)約3分。

## 5. 参照
- 評価: `eval/E_{meta,hormuz,sewer,ai_control,space_weapons}.md`、`eval/summary_*.json`(3)
- 実行: `runs/manifest.json`、`cost.json`、`ledger/FREEZE.json`、`checker_switch_check.json`
- 比較資料: `docs/pm/allfact_e2e_02/comparison_articles.md`、`eval_template.md`、`theme_fact_watchlist.md`
- REPORT §94(`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`)、委任ログ `docs/pm/delegation_log/2026-10-07_OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02_{A1,D1}.md`

## 6. 人間比較8点のraw URL(comparison_articles.md 第4節。commit/push後に有効)
従来版(Noteなし):
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/hormuz/control/rep1/ja_writer/revision2.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/hormuz/control/rep1/b1b/article.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/sewer/control/rep1/ja_writer/revision2.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/sewer/control/rep1/b1b/article.md
P2版 rep1:
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1/ja_writer/revision2.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1/b1b/article.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep1/ja_writer/revision2.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep1/b1b/article.md
