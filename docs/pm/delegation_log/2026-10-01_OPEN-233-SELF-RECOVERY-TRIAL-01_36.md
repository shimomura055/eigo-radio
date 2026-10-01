# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_36(2026-10-01)

## 1. 委任内容(要旨)

rep20 sample2で発生した`ladder_exhausted_without_full_rewrite`の原因を
特定し、小修正1回を実装・再検証する。広いTrialは含めない。Guardrail¥7。

## 2. 実施内容

### A. 原因特定(¥0、API呼び出しなし)

rep20 sample2 cycle2のinstance jsonを逐語確認した。cycle1は
MUSE-HC-011(`changed_number`)が`deterministic_floor:changed_number`で
BLOCKING、`e1_minimal_word_edit`で解消。cycle2のRecheckが新規claim
(MUSE-HC-012、claim_text=`“They could not tell if it was AI or a
person” and “They did not realize it.”`、`llm_materiality=BLOCKING`、
floor非適用[LLM独立判定]、`changed_scope=True`)を検出した。sample1の
同種claimは`disclosure_gap_negative_inference_downgrade`floorで
QUALITYへ降格されるが、sample2 cycle2のこのclaimは`changed_scope=True`
が立っており降格対象外(floor適用条件3)のままBLOCKINGに残った
(Stage2 LLMの非決定性)。

このclaim_textを決定論的な再現スクリプトで解析したところ、記事中の
非隣接2文(「They could not tell if it was AI or a person.」と「They
did not realize it.」)を“…” and “…”で結合した合成claimであり、両断片
とも`en_full`に逐語で実在することを確認した。既存`locate_target()`は
rewrite_hintの引用断片(本caseはJA文のためen_targetには不一致)に失敗
すると、claim_text全体への1文fuzzy match(`locate_best_sentence`、
SequenceMatcher)のみを試みるため、2断片のうち一方(「They could not
tell if it was AI or a person.」、ratio=0.74)しか`en_target`に入らず、
もう一方の「They did not realize it.」がladder①(単語・接続詞)→③
(1文)→④(段落)のいずれの編集対象にも一度も入らないまま残っていた。
JA側も、rewrite_hintの引用断片がEN側の(修正前の)1文targetとは対応しない
広い範囲を拾っており、EN/JA双方で対象範囲が食い違っていた。

### B. 修正(1回、fail-closed新規追加のみ)

`er052_open233_self_recovery_flow_runner_01.py`へ以下を実装した
(design書§6-17参照)。

1. `extract_all_quoted_fragments(text)`: 既存`extract_quoted_fragment`
   (最長1件のみ返す)の複数版。text中の全bracket-quote断片
   (“”/「」/『』)を出現順に返す。
2. `locate_multi_quote_span(claim_text, full_text, max_span_chars=600)`:
   claim_textが2つ以上の断片を含み、かつ全断片がfull_text中に逐語で
   実在する場合のみ、それらを包含する最小スパンを返す。断片が1つ以下・
   いずれかが不在・空行を跨ぐ・600文字超の場合はNoneを返し(fail-closed)、
   既存の`locate_best_sentence`経路へそのまま委ねる。
3. `locate_target()`: 第一キー(rewrite_hintのexact substring)の次、
   第二キーとして`locate_multi_quote_span`を追加。
4. `run_paired_local_rewrite()`のJA側target決定: `en_target`が
   `multi_quote_span`で特定された場合に限り、rewrite_hintのJA引用断片
   より位置写像(`locate_ja_counterpart_by_position`)を優先する。

unittest: 開始前チェック(既存304件、API呼び出し前に再確認、全PASS)→
新規13件(`TestExtractAllQuotedFragments`5件・`TestLocateMultiQuoteSpan`
5件・`TestLocateTargetMultiQuoteIntegration`3件、うち1件はrep20
sample2 cycle2の実データをそのまま使った回帰ロックテスト)→計317件、
全PASS(¥0、API呼び出し前)。

### C. rep21(¥3.561、Guardrail¥6.5のうちのsub-budget)

rep19/rep20と同一のfrozen fixtureを、修正後のコードでn=2+Safety対照
(changed_number fixture、full flow n=1)で再実行した
(`er052_open233_self_recovery_flow_runner_01_rep21_representative_
01.py`新規、`OUT_DIR_REP21`新設)。

結果:
1. sample2(本委任の修正対象): `RESOLVED_REWRITE_THEN_DOWNGRADE`
   (2cycle、¥1.2052)。STAGE4へ至らず解消。ただし本run自体では
   Stage2 LLMの非決定性により2断片合成claimの形自体は再現しなかった。
   修正の有効性は決定論的unittest(API非依存)で確認済み。
2. sample1: `STAGE4_ESCALATION`(`cycle_limit_exhausted`、3cycle、
   ¥2.1567)。rep20では3cycleで`RESOLVED_REWRITE_THEN_DOWNGRADE`
   だったが、本runでは逆転した。原因を追跡し、本委任の修正とは
   **無関係**であることを決定論的に確認した: 該当claim_textの断片は
   1つのみ(2文が1つの“…”で囲まれている)であり、`locate_multi_quote_
   span`は`not_multi_quote`を返して即座に既存経路へ委ねる(新規コード
   パス不発火、修正前後でコード経路が完全同一)。実際の原因は、cycle1
   でStage2 LLMが`rewrite_hint`を空文字列で返したこと(rep20では
   引用断片入りのrewrite_hintを返していた、run間非決定性)により、
   `locate_target`の第一キーが不発火となり、1文SequenceMatcher
   fallbackが2文結合quoteのうち1文しか捕捉できず、未捕捉側が
   cycle2以降も再検出され続け、cycle上限(3)に達したことによる。本委任
   が修正した「2つの独立した引用断片」パターンとは別の、「1つの引用が
   複数文へまたがる」という近縁だが別個の既知の限界であり、変種(e)と
   して記録する。false PASSではない(STAGE4_ESCALATIONは安全側の
   fail-closed)。
3. Safety対照(changed_number、full flow n=1、¥0.1991): 引き続き
   `deterministic_floor:changed_number`でBLOCKING→Rewrite→`RESOLVED_
   REWRITE`(floorが弱まっていないことを確認)。

false PASS: 0件。`detect_safety_critical_misdowngrades`: 該当行なし
(0件)。

## 3. 結果・Status

`MULTI_QUOTE_LOCATE_FIX_IMPLEMENTED_REP21_SAMPLE2_RESOLVED_SAMPLE1_
SEPARATE_PREEXISTING_VARIANT_E_FOUND_NO_SAFETY_DOWNGRADE`。

design書§6-17(原因特定・修正内容・rep21実測・変種(e))を新設。本委任の
修正対象(rep20 sample2 cycle2のladder枯渇)は実装・検証とも完了し、
決定論的unittestで有効性を確認した。sample1で新規に観測された
STAGE4は、本委任の修正と無関係な別の既知の限界(変種(e))であることを
決定論的に確認し、修正せず報告のみに留めた(範囲拡大の勝手な判断は
行わない)。

## 4. 費用

分析・原因特定(Part A)¥0+修正実装(Part B)¥0+rep21(Part C本体
¥3.3619[sample1¥2.1567+sample2¥1.2052]+Safety対照¥0.1991)=
**¥3.561**(Guardrail¥7のうち約51%)。Phase累計¥482.3665+¥3.561=
**¥485.9275**/総枠¥600、残**¥114.0725**。

## 5. unittest・Git

unittest317件(既存304+新規13)を実行前に再確認し全PASS
(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_
flow_runner_01_test_01`、¥0)。project-wide regression
(`run_project_regression.py`)も実行し、collected=4284(既存4271+
新規13)・failed=6・errors=5。失敗/エラー計11件は`er003_test_bad`
(`test_case_0`)、`er003_test_p2j_investigate`(4件)、`er015_standard_
a2_6000_generation_first_trial_01_test_01`(loaderエラー)、`er025_
pronunciation_resolution_phase3_b1b_en_wiring_01_test_01`、`er040_
tts_fixed_shell_master_champion_trial_01_test_01`、`er043_tts_fixed_
shell_master_champion_trial_02_test_01`、`er011_open112_trend_
synthesis_mode_production_wiring_01_test_01`(3件)のみで、いずれも
本委任が変更した`er052_open233_self_recovery_flow_runner_01.py`/
`er052_open233_self_recovery_flow_runner_01_test_01.py`を経由しない
(既存の無関係failure、`er052_open233_self_recovery_flow_runner_01_
test_01`単独実行317件全PASSで別途確認済み)。本委任由来の新規failure
なし。

**変更ファイル**: `er052_open233_self_recovery_flow_runner_01.py`
(`extract_all_quoted_fragments`/`locate_multi_quote_span`新設、
`locate_target`/`run_paired_local_rewrite`のja_target決定への組み込み、
`OUT_DIR_REP21`/`BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`新設、既存
`OUT_DIR_REP7`〜`REP20`等は無変更)。`er052_open233_self_recovery_
flow_runner_01_test_01.py`(新規unittest13件)。新規
`er052_open233_self_recovery_flow_runner_01_rep21_representative_
01.py`、`er052_output/open233_self_recovery_flow_runner_01_rep21/`
(新規)、`docs/pm/design_open233_self_recovery_flow_01.md`
(§6-17/§9-1㉖追記)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`
(§34追記)、`DECISION_LOG.md`(新規エントリ)、`OPEN_ITEMS.md`
(OPEN-233行追記)、`docs/pm/delegation_log/2026-10-01_OPEN-233-SELF-
RECOVERY-TRIAL-01_36.md`(本ファイル)。**Production code(er003/
er006/er009/er010/er012/er019)・既存iteration1〜8・rep7〜20・rep19
frozen fixtureは無変更。**

## 6. STOP条件該当確認

¥7超え見込み(該当せず、累計¥3.561/¥7)/API error 3連続(該当せず、
0 error)/Production・既存証跡変更(該当せず)/USER_DECISION_REQUIRED
5条件(該当せず)/開始前チェック未反映(0件)/Safety12の違反文または
Safety-critical 8がBLOCKINGでなくなる(該当せず、2-C参照、downgrade
0件)/false PASS 1件以上(該当せず、0件)/小修正1回後もFAIL(該当せず、
本委任の修正対象[sample2 cycle2のladder枯渇]は決定論的unittestで解消を
確認)。STOP条件はいずれも非該当。

次アクション: 変種(e)(1つの引用が複数文にまたがり、かつrewrite_hintが
空の場合の既知の限界)の修正要否、meta_run03_standardの(b)Stage1 fresh
enumeration非決定性そのものの改善要否(委任_33から継続する未決事項)、
Phase 2新規テーマ選定(PM_GOVERNANCE§13、ユーザー判断)はいずれも
Fable/ユーザー判断事項として継続。
