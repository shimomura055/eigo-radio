FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_04-A3-ADDITIONAL-VERIFICATION-20261023

# 委任_04: A-3 v3(Adv英語説明Prompt補正)の追加検証。既存Trialデータ最大再利用、**追加費用目標10円・上限20円**。Production/Prompt変更0。Closeoutは VALIDATED/REJECTED/USER_DECISION_REQUIRED のいずれか(採用はユーザー判断)。

## 背景(ユーザー決定 2026-10-23)
A-1=APPROVED_FOR_PRODUCTION(X/Z、配線はA-3判断後にまとめて。準備は先行)。A-3 v3=追加検証後に採用判断。OPEN-476=DEFERRED。OPEN-477=再発防止承認。**原文を保存して読むこと**(§3検証方針・§7報告)。別agent(委任_05)がA-1配線設計・SSOT決定記録・OPEN-477を担当。

## T-0
1. **ユーザー原文を逐語保存**: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の最新userメッセージ(「# 指示｜Family X/Z Key Phrase品質改善・追加Trial・Open Items整理」)を `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_02.md` へ無改変保存(最初にcommit/push。委任_05 agentも参照)。
2. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_04.md`(index 364以降、先頭MARKER一致)。
3. ACTIVE_TASK自分の行のみ(並行: 委任_05、ASR PN/UKUS配線設計、FAMILY-Y 委任_08[有料run中の可能性]。**pythonプロセスは自分が起動したPIDのみ終了可、イメージ名一括kill禁止**)。SSOT行は委任_05が担当(本委任はOPEN-474へA-3検証結果の1行追記のみ)。

## 検証設計(Fable指定、必要十分)
- **再利用**: `er112_output/kp_gm_trial_01/` の既存出力(a1gE0=現行Prompt、a1gE3=A-3 v3、各3回、難例20件のAdv分)とJudge結果をまず集計し直す(API 0): KPごとに「改善/悪化/維持/判断分かれ」を、観点=(i)本文中の意味との一致 (ii)記事固有条件の混入 (iii)過度な語義限定 (iv)説明の自然さ、で2系統Judgeの既存結果+Sonnet目視で分類。
- **追加生成(≤20円)**: 意味・用途の異なるKP種別を広げる。既存Trialで未カバーの種別(句動詞/慣用句/名詞句/数量表現/コロケーション/比喩、X news・Z fiction)から**正常KP 20〜25件(Adv、既存run由来、replay入力あり)**を選び、現行Prompt vs A-3 v3を同条件で各2回生成(gpt-6-luna、本番と同一。見積: 説明call約0.1円×2arm×2回×25=約10円)。Judgeは費用節約のため1系統(gpt-6.1-sol or sonnet5.5の安い側)+Sonnet目視、判断が分かれた例のみ2系統目。
- **判定基準**: 改善率・悪化率(悪化=本文中の意味から外れる/不自然/曖昧化)、記事固有混入率、過度限定率を arm別に。VALIDATEDの目安=悪化率がbaseline以下かつ改善が有意に観察(数値はDESIGN_02 §5の基準を流用、±1件は方向判断)、REJECTED=悪化が上回る、USER_DECISION_REQUIRED=拮抗。
- 代表例(改善・悪化・判断分かれ 各≥3)を原文付きで並記。
- 新たな対策案の探索・Prompt再調整は行わない(v3固定)。

## 成果物
`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/A3_VERIFICATION_01.md`(設計・集計表・代表例・Closeout案・残存リスク・費用出典)。生成物は `er112_output/kp_gm_trial_01/a3_verify/`。OPEN-474へ1行追記、REPORT_LEDGER 1行。commit(明示add)、secret_scan hits=0、`git push origin HEAD:main`。

## 禁止
Production/Prompt変更、A-1配線作業(委任_05担当)、20円超過、v3以外のPrompt案、記事B成果物変更。

## 報告(docs/pm/RESULT_PACKET_KPGM4.md)
(1)改善・悪化・維持・判断分かれの実績(件数/率、arm別)と代表例 (2)既存Productionとの品質比較 (3)Closeout案とFable向け推奨材料・残存リスク (4)費用(出典) (5)commit・raw URL + RESULT_PACKET 4行 + 「判定整合: 重大NG=なし」。