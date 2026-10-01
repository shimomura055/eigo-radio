# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_30(2026-10-01)

## 1. 委任内容(要旨)

Hook境界群の最終小修正、重大誤解原則のrunner既定化、実記事代表5ケース
でのend-to-end確認。広い29件Trialは禁止。Guardrail¥15。

## 2. 実施内容

### Part1(Hook rubric V4、¥0.7000)

`HOOK_TIEBREAK_TEXT_V4`(既存V3へ、時間経過・順序の曖昧な演出は
具体的Factの追加ではないというtie-break判定軸を明記する1段落のみ
追加)を新設。n=2再測定(boundary-1・元Hook accept-1・NG4群)の結果、
boundary-1(0 false block、解消)・元Hook(0 false block、維持)・
NG4群(0 false pass、維持)を確認した。

Trial C期待2(BLOCKING経路を強制した場合のactor_rewrite_guard_ok実
挙動、¥0.0637)を実測した結果、`classify_problem_kind`の優先順位
(term_scope>actor)により、changed_scope/changed_actorが同時に真の
claimでは主体置換ガードが一度も発火しないまま置換が通ることを発見
した(本caseは偶然ledger不一致を検出できなかっただけで、ガード自体が
機能していたら却下していたはずと確認済み)。優先順位の見直し要否は
本委任スコープ外のためFable/ユーザー判断へ送る。

### Part2(runner既定化、¥0)

重大誤解原則(Stage1 V4A・Stage2 body V4・Hook V4)を
`er052_open233_self_recovery_flow_runner_01.py`本体の既定経路へ実配線
した。`ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT`(既定True)で制御し、
Falseで既存iteration1〜7・rep7〜15と同一の挙動へ復帰できる。unittest
6件新設、既存4件はrubric既定切り替えに伴いfake/assertionを追従更新。

### Part3(rep16、実記事代表5ケースend-to-end確認)

`hormuz_run03_standard`/`neg1_meta_b3prod_a2`/
`neg3_hormuz_prodrunner_b1b`/`meta_run03_standard`/`bgroup_B3`を
Stage1 fresh・n=2で実行した。sample1(5/5完走、¥10.3338)で
`neg3_hormuz_prodrunner_b1b`がSTAGE4_ESCALATION(FAIL)。

**neg3 FAILの根本原因・小修正1回・検証**: `paired_rewrite`が片側
(EN/JAいずれか)のみ対象文を特定できた場合、ladder構築自体が一度も
実行されず0 callで⑥disabled経路へ落ちる設計上の穴を特定。是正:
`en_located != ja_located`の新設elif分岐で、特定できた側だけを既存
`single_text_rewrite`(①〜④の非⑥ローカル編集ラダー)へ委譲する。
unittest 2件で再発防止。実際に失敗していたclaimを再構成して単体検証
した結果、guard_ok=True・JA文を「貨物に」→「貨物について」(支払
義務者を特定しない表現)へ1語修正で解決した(¥0.0758)。

残り4 instanceのsample2完走(Safety関連2件を優先する順序へ変更)を
行った結果、4件ともsample1/sample2一致でRESOLVED(Stage4到達0・
false PASS 0、段落・全文Rewrite 0、Safety-critical[bgroup_B3]は
BLOCKING経由で正しく検出され続け誤降格なし)を確認した(sample2
追加¥3.3225)。neg3のsample2は予算制約により未完走のまま残った
(修正自体の有効性は単体検証で確認済み、既知の残課題)。

## 3. 確認事項(Fable/ユーザーへ)

- `classify_problem_kind`の優先順位見直し要否(actor置換ガードの
  設計上の盲点、changed_scope/changed_actor同時真の場合にガードが
  発火しない)。
- neg3のsample2完走(追加予算)の要否。
- Phase 2(10〜20実記事規模)の新規テーマ選定(PM_GOVERNANCE§13)。

## 4. 費用・Status

本委任合計¥14.496(Part1¥0.7637+Part3 rep16¥13.6565+neg3単体検証
¥0.0758、Guardrail¥15のうち残¥0.504)。Phase累計¥418.3982+¥14.496=
¥432.8942/総枠¥600、残¥167.1058。
Status=`HOOK_V4_BOUNDARY_RESOLVED_DEFAULT_WIRED_REP16_PARTIAL_N2_
ACTOR_GUARD_GAP_DISCLOSED`。詳細:
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§28、
`docs/pm/design_open233_self_recovery_flow_01.md`§4-23/§9-1⑳、
`DECISION_LOG.md`2026-10-01委任_30エントリ、
`er052_output/open233_element_trial_meta_hook_02/`、
`er052_output/open233_self_recovery_flow_runner_01_rep16/`。
