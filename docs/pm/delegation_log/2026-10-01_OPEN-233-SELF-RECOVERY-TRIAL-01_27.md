# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_27(2026-10-01)

## 1. 委任内容(要旨)

ユーザー上位原則「重大誤解原則」の明文化、¥0是正4点、Hormuz要素Trial A。
Meta要素Trialは次委任_28。広い29件Trialは禁止。Guardrail¥25(Part2)。

## 2. 背景

ユーザー指示(2026-10-01): OPEN-233は「Ledgerとの差異を全部直す」
プロジェクトではなく、「英語学習者に記事の本質について重大な誤解を
与えるものだけを止め、それ以外はできるだけ元記事を守ること」が目的。
既存ユーザー意図の明文化(新規Product原則ではない)。

## 3. 実施内容

### Part 0(¥0、明文化)
`docs/pm/design_open233_self_recovery_flow_01.md`§0(上位原則)を
新設。許容/BLOCK候補表・問題種類→初期単位表・主体置換ガード方針・
Fable PMレビュー7観点を記載。`PM_GOVERNANCE.md`23節(要約+参照)・
`PM_BRIEF.md`参照1行を追加。§7-0-iter27でhormuz-HF009の「Oil prices」
型scope一般化claimをBLOCKING→ACCEPTABLE/QUALITYへ再ラベル。

### Part 1(¥0是正4点、`er052_open233_self_recovery_flow_runner_01.py`)
1. `escalate_to_paragraph`ladder skipを新設フラグ
   `ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP`(既定False)でガード廃止。
2. `classify_problem_kind`+`filter_levels_by_problem_kind`で問題種類→
   初期Rewrite単位の写像を実装。
3. `actor_rewrite_guard_ok`で主体置換ガードを実装(neg1 cycle2実データ
   でusers→employees却下を確認)。
4. `ja_en_equivalence_reason`をcycle_record/call_logへ保存。
5. Stage2 body/Hook/Stage1(V4A)へ重大誤解原則rubricを新定数として追加
   (Stage2 bodyのみ実配線・実測、Stage1/Hookは未配線)。
unittest新規19件+既存222件=**計241件全PASS**。

### Part 2(Hormuz要素Trial A、¥2.2597)
`er052_open233_element_trial_hormuz_terms_01.py`(新規)で許容5/NG5/
Safety2(hormuz-HF009自身は再ラベル対象のため対照から除外、代わりに
B3因果+er009 changed_scope使用)をn=2実測。初回rubricでaccept-1
("Oil prices did not fall across the whole market...")が2/2 false
BLOCK。最小修正1回(`..._V2`、market全体表現の許容明確化)で再実測
n=2は全群false PASS/false BLOCK 0件。Trial A-2(`er052_open233_
element_trial_a2_deterministic_rewrite_01.py`、¥0.1261)でNG2件+原文2
を決定論名詞句置換、diff+局所QA1call(verdict REVIEW_REQUIRED、唯一の
指摘は置換と無関係な既存箇所)で周辺影響なしを確認。

## 4. 確認事項(Fable/ユーザーへ)

- hormuz-HF009を`SAFETY_CRITICAL_SUB_IDS`(既存10件)から除外する編集
  要否(本委任では定数自体は未変更)。
- Stage1(V4A)・Hook専用rubricへの重大誤解原則の実配線・実測は次回以降。
- Meta要素Trial(委任_28)完了後、両要素の結果を踏まえた配線可否判断。

## 5. 費用・Status

本委任合計¥2.2597(Guardrail¥25のうち)。Phase累計¥393.2155+¥2.2597=
¥395.4752/総枠¥600、残¥204.5248。
Status=`ELEMENT_TRIAL_MISCONCEPTION_PRINCIPLE_CODIFIED_HORMUZ_TRIAL_A_
PASSED_AFTER_ONE_MINOR_FIX`。詳細:
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§25、`DECISION_LOG.md`
2026-10-01委任_27エントリ、`docs/pm/design_open233_self_recovery_
flow_01.md`§0/§4-18/§5-11/§7-0-iter27/§9-1⑰。
