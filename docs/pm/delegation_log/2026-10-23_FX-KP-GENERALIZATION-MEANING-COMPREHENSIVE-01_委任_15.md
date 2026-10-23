FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_15-FABLE-BLIND-RESULT-04-RECORD-AND-REAGGREGATE-20261023

# 記録・再集計のみ(API 0・Production変更0)。Trial_04(委任_14)のFable盲検判定を保存し、`py er112_kp_gm_trial_04_report.py report --labels <json>` で再集計、TRIAL_RESULT_04へ「Fable確定」節を追加、OPEN-474更新、Git。

## 0. 読むもの
`docs/pm/ACTIVE_TASK.md`(line 2、KP行)、`docs/pm/RESULT_PACKET_KPGM14.md`、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{TRIAL_RESULT_04,DESIGN_06,WIRING_DESIGN_04}.md`、`TRIAL_04/{fable_blind_04.md,fable_blind_04_key.json,PHASE0_CALIBRATION_01.md,BUDGET_LOG_01.md}`、`er112_kp_gm_trial_04_report.py`(labels形式: `"行番号:列": "PASS|THIN|FAIL|FAIL_LIT"`)。

## 1. Fable盲検判定(key開封前に判定、開封後に帰属。逐語で `TRIAL_04/FABLE_BLIND_RESULT_04.md` に保存)
PASS以外のセルのみ(他は全てPASS):
- FAIL_LIT: 2:A「見えない時計」(M/rep1) / 13:E「より青々とした芝生」(B0/rep1, B0/rep2) / 27:D「トロフィーの形をした質問」(B0/rep1, C/rep1) / 27:E「トロフィーの形をした問いかけ」(M/rep2) / 27:F「トロフィーの形をした問い」(B0/rep2)
- FAIL(語義誤認): 27:B「成果や地位を誇示するような問い」(C/rep2。本文=賞そのものが「選ぶ側の価値観を問う問い」の比喩。誇示の意味はない)
- THIN(△): 8:B「区別する」(Cp) / 24:B「影響する」(M/rep2) / 25:D「自分の拳を突き上げる」(B0/rep2、喜びの含意欠落) / 46:C「商品が作られて店に届くまでの流れ」(Cp、範囲が狭い)
- 判定メモ: 17 keep someone company の「話し相手」系・「人の相手をする」はTrial_03のFable判定と整合させPASS。35 take the wheel「車を運転する」はgold許容でPASS。2:B/C/D(時間の流れ/タイミングの仕組み)はPASS(比喩を捉えている)。3 behind the curtain「陰で動いている/関わっている」はPASS(Sonnet参考のTHINと不一致)。
- Trial_03で確定済みのB0文字列(an unseen clock「目に見えない時計」FAIL_LIT×2 等)はラベル継承。
Fable所見(そのまま記載): (1)課題①: B0のF層字義NGは本表+継承で6出力(unseen clock×2、greener grass×2、trophy×2)。C(独立検査+flag項目のみ再生成)は unseen clock 2/2・greener grass 2/2 を修復、trophy は rep1未修復(FAIL_LIT残)・rep2は誤った再生成(語義誤認)。C後のF層NG=2出力(字義1+語義誤認1)。flag項目内の悪化は1件(27:B)。Cp(同一call自己監査、1 repのみ)は検出器としてはrecall 0だが、出力自体は本表でFAIL 0(unseen clock/greener grass/trophyいずれもPASS)。ただしB0と文字列が変わっており(事実上の生成Prompt変更)、未flag項目バイト同一の保証はない。M(再整合指示を除いたmessage)はFAIL_LIT 2(unseen clock rep1、trophy rep2)で改善なし。(2)「解消」とは書けない(F層残存NG 2/122、既知事例3種のうち2種は解消、1種[trophy]は未解消)。(3)課題②は決定論スコアで誤り9→0(1 rep)。

## 2. 作業
- 上記をlabels JSON(`TRIAL_04/fable_labels_04.json`、PASSセルも含め全232セル分を明示)にし、`py er112_kp_gm_trial_04_report.py report --labels TRIAL_04/fable_labels_04.json` で再集計→出力を `TRIAL_04/REPORT_FABLE_04.md` に保存(arm別 PASS/THIN/FAIL/FAIL_LIT、flag項目内の改善/不変/悪化、F層/N層別、継承ラベル込みの全体)。
- `TRIAL_RESULT_04.md` 末尾に「Fable確定(2026-10-23)」節: 上記数値と所見、Sonnet参考との差分(THIN/FAILの不一致セル一覧)。手段/目的の区別を明記(②=目的達成の見込み[採用判断待ち]、①=部分改善・未解消)。
- OPEN-474: 「Trial_04 Fable確定: ②誤り9→0(VALIDATED候補、Opus条件C→ユーザー採否へ)、①部分改善(F層NG 6→2/122、trophy型未解消)、次の方針はユーザー判断」。ACTIVE_TASK KP行更新。
- 委任文逐語保存 `..._委任_15.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致)。
- secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。
## 3. 禁止
コード変更0(report scriptの実行のみ)。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行を編集しない。完了したら再集計の主要数値(arm別FAIL/FAIL_LIT/THIN、flag項目内の改善/悪化)とcommit hashのみ報告。