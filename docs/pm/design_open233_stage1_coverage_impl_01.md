# OPEN-233 Stage 1 coverage_union 実装仕様メモ(委任_06、Trial専用・¥0)

Opus#16を受けたFable確定構成のTrial実装。Production未配線・`APPROVED_FOR_PRODUCTION`ではない。実装: `er052_open233_stage1_coverage_checker_01.py`(新module、LLMは`call_fn`注入)、runnerは分岐・F3・H1のみ。

## 1. 単位ID付与規則(決定論、`split_units`)

- `T`=タイトル(`# `行)、`H{n}`=見出し(`## In one line`以外の`#`行)、`S{p}.{s}`=本文p段落のs文(p=1はhook段落、role=hook)、`L{s}`=`## In one line`以降の文(role=oneline)、`P{p}`=段落(構造のみ、judged=False)。
- 文分割はrunnerの`vs_sentence_segments_l6`(略語直後のピリオドで切らない)を`segment_fn`で再利用。英数字・かな漢字を含まない断片は単位にしない。全単位に本文offsetを持ち、`article[start:end]==text`(逐語)。
- 判定対象(judged)=T/H/S/L/R。段落(P)は判定しない(含む文が全て個別判定されるため重複判定を避ける)。
- **関係単位** `R:{直前文ID}+{当該文ID}`: 当該文の文頭(引用符・ダッシュ除く)が因果・照応語(So/This is why/That is why/That's why/As a result/As a consequence/Therefore/Thus/Hence/Consequently/Accordingly/For this reason/Because of this/This means/This led to等+runnerの`CAUSAL_SENTENCE_INITIAL_EN`=Following)の文と、同じ節(body/oneline)内の直前文の組。段落をまたぐ組も作る。Stage 2へ渡す箇所(`claim_text`)は**当該(後ろの)文のみ**(前文は文脈)。
- **同文グループ**: 文・タイトル・見出しを`norm_sentence`(NFKC・引用符統一・空白・大小・前後句読点除去)で比較し、同一が複数IDにあれば記録。

## 2. schema・prompt方針

- 3'-R(`R3_JSON_SCHEMA`): `unit_verdicts[]={unit_id, verdict∈{CANDIDATE,SUPPORTED}, support_fact_ids[], ledger_quotes[], issue, claim_in_article, related_fact_id, flags{既存10}}`。strict。**severityフィールド無し**(重大度はStage 2)。
- 5-lite(`R5_JSON_SCHEMA`): `facts[]={fact_id, matches[]={unit_id, verdict∈{MATCH,DEVIATION}, issue, claim_in_article, flags}}`。fact未対応(matches空)は許容。
- prompt方針: 判定必須IDの一覧を明示し「1件も省略しない」、SUPPORTEDは確信時のみ+逐語引用必須(一字一句・翻訳要約禁止)、「迷えば候補」、重大度は判定しない、関係単位は結び付け自体を判定、文体・言い換えは問題にしない。本文は新module内の定数。V0/V4A既存定数は無変更(テストで確認)。
- sha256(`PROMPT_SHA256`、監査ログ`audit.prompt_sha256`にも記録、全64桁):
  - R3_PROMPT_TEMPLATE `ad561d813ee0adea31d577896eab85db395c442239e037d92e43b5d29e86eff7`
  - R5_PROMPT_TEMPLATE `20624a72f2d464ce3f971f2ba6ce1e68fcb978cf6b9d3664abf64992fb65c900`
  - R3_DEVELOPER_MESSAGE `5b737601622c9cef9bcc72952c4fc5eff3cb9d08473efbf0557b7d5a7808f537` / R5_DEVELOPER_MESSAGE `e33843d9b27d7483e8c7621b4d18f9e6cadc9bf8ecaeccd2a7e6cabea0c52f7b`
  - R3_RERUN_NOTE `787bc940dd4cb4cbab5da9bbd5f763dda1a248b75becc240e1b8d4c68242e554` / FLAG_DESCRIPTIONS `5a1251cea4c677872e099c2003a1eb09aac24072d552794db541a86bcc30263b`
  - R3_JSON_SCHEMA `0343ad918cf085bbdfc8ad53c16671bd74e0dffeeda8240633409b4c089da3da` / R5_JSON_SCHEMA `d2d5dfb47caee8f68d9675b23f3052c27decd2d725c8c348a237b8b4c1750f05`

## 3. 決定論検査(SUPPORTEDを覆す検査。候補生成ではない)

SUPPORTED単位ごとに`verify_supported`。戻す理由(sub_reason): `unknown_fact_id`(引用fact_idがLedgerに無い/空)、`quote_missing`、`quote_not_in_ledger`(引用が引用factブロックに逐語[NFKC・空白除去後]で無い、または4字未満)、`number_not_in_fact`(単位内の数値言及が引用factに一致も自然な四捨五入[precheckの`is_natural_rounding`]も無い。scale語million等は換算)、`causal_not_in_fact`(単位に因果語/関係単位なのに、引用factに因果記述[日本語因果語]が無い、または因果を否定・相関とする記述がある)、`negation_polarity_mismatch`(単位の英語否定語 vs 引用factのclaim行の日本語否定語、片方だけ否定)、`group_inconsistent`((iv)同文グループ内でCANDIDATE系とSUPPORTEDが混在)。主体名照合は対象外。

## 4. 経路処理・欠落ID・∪規則

- **3'-R**: 1 call(全judged ID)。API失敗は同callを1回だけ再実行(`_call_with_one_retry`)、なお失敗なら経路失敗(`api_failure`)。応答の欠落IDは機械検査→**欠落分のみ**でprompt再実行1回(`r3_rerun`)→なお欠落なら当該単位をCANDIDATE(sub_reason=`coverage_gap`)としてStage 2へ。未知ID・重複(判定矛盾=`duplicate_conflict`)も処理。
- **5-lite**: 1 call。DEVIATIONのみ候補。fact未返却・未対応は許容(記録のみ)。
- **∪(`union_candidates`)**: 両経路の候補(決定論検査で戻した分・coverage_gap含む)を、`claim_text`の正規化(`norm_sentence`)をキーに重複排除=同文グループ・「関係単位とその当該文」の重複も1件に合流。合流時にflagsはOR、issue/related_fact_idは全て保持、`unit_ids`/`routes`/`sub_reasons`を記録。経路別の生の候補は`audit.per_route.{r3,r5}.candidates`・`unit_status`(単位ごとのSUPPORTED/CANDIDATE/MISSING/MATCH/DEVIATION/UNMENTIONED)に残す(経路別検出率・相関を後から集計可能)。
- Stage 2への変換(`candidates_to_deviations`): `claim_in_article`=単位本文(逐語、モデルの引用ではない)、`severity`=Stage 2の入口を通す印として`MAJOR`(Stage 1は重大度を決めない。`explanation`に明記)、origin=None、`er051.classify_deviation_trial`を通す。

## 5. runnerフロー変更箇所(`er052_open233_self_recovery_flow_runner_01.py`、行番号は本commit時点)

- L76 import / L458〜463 スイッチ定義 / L1752 `stage1_coverage_fresh`(retry・cost計上は`stage1_fresh_with_enumeration`と同パターン) / L1791 `stage1_fresh_dispatch`(legacyは従来関数を呼ぶだけ)
- L8060 `h1_rerun_stage1`、L8068 `stage1_api_failure_stop_result`(STOP結果、`stage4_allowlist_decision("api_failure")`を使用)
- `run_instance`: L8201 reuse分岐(coverage_unionでは保存済みV4A出力を使わずfresh)、L8229 cache key(modeを含める)、L8251〜8257 H1再実行とcache除外、L8268〜8274 **H1 STOP**(`_stage1_api_failure`はPASSへ抜けない)、L8317〜8322 **F3**(早期PASS returnの条件に`not f3_precheck_hits`を追加。該当ありなら通常ループ=precheck floor→BLOCKING→Rewriteへ)、L8353〜8356/L9402〜9408 監査記録のみ。
- 既定(`legacy_v4a`/F3 OFF/H1 OFF)は従来の2経路を同じ引数で呼ぶだけで、result dictに新キーを足さない(テスト`test_legacy_result_has_no_new_keys`)。Stage 2・S1・floor・Rewrite・Recheckは無変更。

## 6. スイッチ(Trial計測用、`KPI_TRIAL_SWITCHES`へは含めない=段階Aスクリプトが明示設定)

`STAGE1_MODE`∈{legacy_v4a(既定), coverage_union} / `STAGE1_ROUTES`∈{both(既定), r3_only, r5_only} / `F3_PRECHECK_ALWAYS`(既定False) / `STAGE1_FAIL_CLOSED`(既定False)。モデルは`MODEL`=gpt-6-luna。

## 7. 監査ログ項目(`result["stage1_coverage"]`=`audit`、記録専用)

経路別候補(`per_route.*.candidates`/`candidate_unit_ids`/`unit_status`)、欠落ID(`missing_first`/`missing_after_rerun`)、再実行(`rerun_used`)、決定論検査で戻した件数(`returned_by_check`、理由別は`unit_status`から)、同文グループで戻した件数(`group_returned`)、未知ID、`overlap`(both/r3_only/r5_only)、`union_candidates`、各callのcost/usage(`calls`)、`total_cost_jpy`、`n_calls`、prompt sha256、単位数・関係単位・同文グループ。

## 8. H1とcircuit breakerの整合(コード読解で確認)

`record_call`は`MAX_CONSECUTIVE_ERRORS`(3)連続失敗で`TrialAbort`(run全体停止)。H1の再実行(legacy: runner側1回、coverage_union: 経路ごとmodule内1回)の失敗callも同じ連続失敗数に加算される。連続3回目は`TrialAbort`が先に発火する(H1のinstance単位STOPより厳しい側=fail-closed方向。PASSには決して抜けない)。

## 9. Fableへの設計判断メモ(実装中に判断した点)

(a)段落(P)は判定対象外(含む文を個別判定)。(b)coverageプロンプトにJA原文・`origin`は含めない(origin=None。KPI構成はJA_MODE=english_only)。(c)Stage 2入口のseverityは`MAJOR`印で固定。(d)関係単位の箇所=後ろの文のみ。(e)coverage_unionではreuse fixtureもfresh実行。(f)fact因果記述の判定は日本語語彙(`CAUSAL_JA_RE`/`CAUSAL_DENIAL_JA_RE`)のヒューリスティック(誤判定は候補側=Stage 2負荷増に倒れる)。(g)段階AはStage 1のみ(Stage 2以降は走らせない)。

## 10. ¥0検証結果の要約(詳細は`er052_output/open233_stage1_coverage_dryrun_01/dryrun_report.md`・単体テスト)

- fixture dry-run(29 instance): 正式gold 6 claim -> 単位ID対応 **6/6**、neg5関係単位`R:L1+L2` **有**、判定単位/記事 平均20.4(1〜38)、関係単位計6件(6記事)、同文グループ0件(全fixture)。
- 単体テスト: `er052_open233_stage1_coverage_checker_01_test_01` 42件OK、runner単体701件OK(既定legacy不変)。
- 段階A費用概算(`er052_open233_stage1_stageA_01.py --stage estimate`、48 run): 低¥53.4/中¥72.3/高¥98.6(既定予算¥65を中位推定が上回る。推論token仮定が支配的で、実測前の推定にすぎない)。
