# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_17(2026-09-30)

## 1. 委任内容(要旨)

Hook演出許容を共通rubricから分離した「Hook専用Stage2」の実装(委任_16
B-2のprompt priming regressionの是正)+代表5ケース×n=2再試行。広い
Trial(29 instance全量)は本委任に含めない。

## 2. 実施内容

- 作業A(¥0): セクション判定(既存`detect_claim_section_type`、変更
  なし。判定基準・境界例を設計書§4-14へ明記)+Hook専用Stage2(新規
  `er052_open233_self_recovery_stage2_hook_01.py`=s2h、title/hookの
  claimのみ別Prompt・別call。入力=Ledger全文+source context+タイトル・
  hook段落のみ、schema=materiality/basis/rewrite_kind/rewrite_hint)+
  runner分岐実装(`run_stage2`をhook群/body群へ分割、`HOOK_ONLY_
  STAGE2_SECTION_TYPES`)+unittest新規4件(`TestHookOnlyStage2
  Separation`、mockベース・¥0)。`docs/pm/ACTIVE_TASK_C233T.md`で
  Trial開始前チェック表(A〜F+関連項目、未反映0件)を作成。
- 作業B(¥5.2181): 代表5 instance(neg1_meta_b3prod_a2/bgroup_B3/
  hormuz_run03_standard/safety_er009_changed_actor/_number、委任_16
  rep7と同一集合)をn=2実行(新規`er052_open233_self_recovery_flow_
  runner_01_rep8_representative_01.py`、OUT_DIR=`er052_output/
  open233_self_recovery_flow_runner_01_rep8`、Guardrail¥14)。
- 作業C(報告): REPORT§17、DECISION_LOG新規エントリ、design書§4-14/
  §9-1⑬/冒頭Status更新、OPEN_ITEMS.md OPEN-233行更新。

## 3. 得られた結論(要約)

Hook専用Stage2(API call分離)により、委任_16 B-2で観測されたprompt
priming(Hook-aware原則文が共通rubricに存在するだけで無関係なclaimの
判定にも寛容化バイアスが波及する現象)は再現しなかった。**代表5ケース
全て(5/5)がn=2両方でPASS**: neg1(Meta hook)はHook専用StageがQUALITY/
ACCEPTABLEと判定しRewriteなしで通過(委任_16でFAILしていたケースが
解消)、bgroup_B3はsection_type="in_one_line"としてbody経路(Hook専用
Stage2は一切呼ばれず、`stage2_route="body"`をinstance jsonで確認)を
通り、BLOCKING維持のまま`ladder_level_used=1_word_connective`(so→
while相当)で解消(誤降格regressionは再現せず)、hormuz_run03_standard/
safety_er009系2件も従来どおりfloor維持+minimal resolutionで解消。
STAGE4到達0件・API error 0件・section_role_violation 0件。**最小修正
フェイズは不要だった**(1回目実行で全PASS)。**広いiteration7 Trial
へは進んでいない**(本委任のスコープ外、次回委任でユーザー判断)。
iteration6のGate=REJECTED判定自体は変更なし。

## 4. USER_DECISION_REQUIRED該当有無

該当なし(6条件いずれも非該当)。既存の安全装置(deterministic floor・
pre-check floor・既存post-hoc downgrade)はいずれも変更・回避して
いない。予算は¥5.2181/Guardrail¥14内、Phase累計¥297.8057/総枠¥500内。

## 5. Git

commit予定(本ファイル含む)。パス指定`git add`(`-A`不使用)。

## 6. 報告(handback)

SubagentHandbackで報告(REPORT§17と同内容の要約)。
