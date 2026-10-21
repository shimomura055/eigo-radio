# 委任文(Fable→sonnet-worker)

## 管理ID
PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01 委任_01(Pronunciation Ledgerの不正データ[`us`→canonical "unknown"等]の是正、`melos` hint混入の是正、同種登録の点検、再発防止の最小改善、Family X/ZのPhrase List供給検証、golden再判定。到達目標=`PRODUCTION_WIRED`[全証拠確認時のみ、判定はFable])。並行agentなし。

## 性質/到達上限Status/禁止事項
- 性質: 承認済み仕様内のデータ是正+原因究明+最小の再発防止(Charter 4)。到達上限=PRODUCTION_WIRED判定材料。
- 費用: 原則API 0。golden再判定は保存済み転写のoffline再判定(API 0)。Phrase List供給検証はoffline(`get_hint_for_text`再計算)+必要なら**既存wavへのAzure再実行1〜2本のみ**(JPY数円)。T-3 Guardrail=JPY20。TTS生成禁止。
- 禁止: `AZURE_PHRASE_LIST_WEIGHT=2.0`の変更、ASR判定ロジック・同音等価・閾値・品質基準の変更、新Trial・大規模機構追加、正当な既存entryの削除、`git add -A`等。Ledgerの変更は**無効化(disable/退避)を優先**し物理削除は避ける(履歴保持)。変更前のledger.jsonをsha付きでバックアップ。
- STOP: 新品質基準・仕様変更が必要/品質への重大影響(golden再判定でPASS→NGが出て原因が是正に起因し品質低下となる場合等)→`USER_DECISION_REQUIRED`で報告。
- 11-3 Opus: 非該当(構造変更なし。再発防止がLedger書込validatorの新設に及ぶ場合は「既存の登録検証機構の最小改善」の範囲か自己判定し、超えるならFableへ報告)。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「LEDGER-INVALID-ENTRY-REMEDIATION-01 委任_01」を含む最新index)。check結果1行。T-2: TTSなし。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
## Claude Code指示：Pronunciation Ledger不正データ是正

**目的：** Pronunciation Ledgerの不正データを是正し、Azure Phrase Listへの誤った語句供給を防止する。

### 1. 対象

- `us → unknown`：不正なLedger登録を無効化する。
- `melos`：hint混入の内容・原因・正しい登録状態を確認し、必要な是正を行う。
- 同種の不正登録がないか、既存Ledgerを点検する。

### 2. 実施方針

1. CURRENT_SPEC・過去のTrial・承認済み仕様を確認する。
2. 不正登録の発生原因を特定する。
3. 不正データを是正し、既存の正しい登録は維持する。
4. 同じ問題が再発しないよう、既存の登録・検証機構を必要最小限で改善する。
5. Family X／Zの双方で、Azure Phrase Listへの供給が正しくなることを検証する。

**重要：**
- Azure Phrase Listの重み2.0は正式採用済み。変更禁止。
- 既存の品質基準・ASR判定ロジック・承認済み仕様を無断変更しない。
- 新しいTrialや大規模な仕組みの追加は不要。
- 不正なhintの除去によって認識結果が変わる可能性はあるため、PASS/NGの不変を前提とせず、golden再判定で影響を確認する。

### 3. 受入条件

- `unknown`など不正な語句がPhrase Listへ供給されない。
- `Melos`など正当な固有名詞の検出・供給が維持される。
- Family X／ZのRegression・ValidatorがPASS。
- 既存のPASS/NG判定に変化があれば、原因と品質影響を報告する。
- Production初回経路およびretry／fallback／resumeとの整合を確認する。
- CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSを必要に応じて更新し、Git反映する。

### 4. 自律解決・STOP条件

既存仕様の範囲内のデータ修正・原因究明・再発防止・検証は自律的に完了させる。

新しい品質基準・仕様変更が必要な場合、または品質への重大な影響が判明した場合はSTOPし、USER_DECISION_REQUIREDとして報告する。

品質を守りながら最短で完了させ、不要な追加Trial・逐次作業を避ける。

### 5. 完了報告

以下を簡潔に報告する。

- 修正した不正データと原因
- 同種問題の点検結果
- 再発防止策
- Family X／ZのProduction動作とRegression結果
- PASS/NGへの影響
- Git commit・SSOT反映状況
- 残存Open Itemと最終Status

**到達目標：PRODUCTION_WIRED（必要な証拠がすべて確認できた場合のみ）。**
--- 原文ここまで ---

## 手がかり(前調査、鵜呑みにせず再確認)
- `er006_output/pronunciation_ledger_01/ledger.json:1098`付近 `us` entry(canonical="unknown"、resolution_method=cascade_unresolved_entity、confidence low、hint=`uhn-NOHN`)。76本文で発火し得る(`PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md`、er089漏れ測定)。記事A run_pp_01 Std in_one_lineで実際に`["unknown"]`が重み2.0で供給(`er011_output/attempt_history.jsonl:16198-16199`)。
- `melos` cascade entryのhintに括弧付き別案が混入(`TRIAL_DESIGN_01.md`[PNEP] §2-2、Opus OF-PNEP-R-06)。一方、Family Zの正当な"Melos"供給はrun_e2e_06で機能(phrases=["Melos"])。是正後も"Melos"供給が維持されること。
- 登録経路: `er006_secondary_asr_01.py:341-379` `_resolve_unresolved_entity_for_review`→`research_pronunciations`(Perplexity、現在401 insufficient_quota)→`upsert`。cascadeが「unresolved entity」として一般語"us"を拾い、研究結果が"unknown"のまま登録された可能性。原因切り分け: (a)entity抽出が一般語を拾った(entity_like判定、先頭大文字"Us"?) (b)研究失敗時の戻り値をそのまま登録した(canonical="unknown"を弾くvalidatorが無い) (c)Perplexity応答の品質。該当時刻のtelemetry/attempt_historyで発生runを特定。
- Ledger API: `er006_pronunciation_ledger_01.py`(entry構造、`get_hint_for_text:164-206`、disable手段=`tts_injection_disabled`はTTS用のみ、Phrase List/M1用の無効化手段は無い[Opus J6]。**本委任では「entryを無効化してPhrase List/M1/TTSのいずれにも供給されない」最小の手段**が必要: 既存fieldで実現できるか[例: hintを空にする=`get_hint_for_text`が除外、sources空、confidence]、無ければ最小のfield追加[`disabled: true`+`get_hint_for_text`/M1 snapshotでの除外]。field追加はProduction code変更になるので、Fable判断材料として「既存fieldで可能か」を先に示し、不可なら最小変更案+testで実装してよい[11-8範囲=不正データ供給防止は承認済み仕様の遵守是正])。
- 点検基準(同種不正): canonical/hintが"unknown"/空/プレースホルダ、canonicalが一般語(CMU収録かつ固有名詞でない)でcascade自動登録、hintに括弧・複数案・日本語混入、sources空でconfidence low、ja_reading_katakanaのみでEN hintにカタカナ由来推定が入っているもの(J7未承認)。各候補を「不正(是正)/疑義(報告のみ)/正当(維持)」に分類し、是正は不正のみ。
- golden再判定: 既存run(run_mey_02、coffee run_fxpw_01、run_pp_01、run_byus_01、Family Z run_e2e_06)の保存済み転写をLedger是正前/後で`evaluate_attempt_with_cascade`(M1有効、既存転写注入、`_reset_m1_freeze_cache()`で条件切替)により再判定し、PASS/NG変化を全列挙。Phrase List供給の変化は`get_hint_for_text`再計算で全EN segment本文について前後比較(unknownが0件になること、Melos等が維持されること)。
- 再発防止の最小改善候補(既存機構の範囲): 登録時validator(canonical/hintが"unknown"・空・一般語[CMU収録かつentity_likeでない]なら登録しない、研究失敗時は`confidence="unconfirmed"`のentryをPhrase List供給対象外にする等)。既存の「研究失敗時もunconfirmed entryを残す」仕様(CURRENT_SPEC.md:1829 ER-23)と矛盾しないこと(HRパッケージ用の記録は残しつつ、Phrase List/M1/TTSへは供給しない)。
- Family X/Z経路: 両方が`get_hint_for_text`→同じAzure関数(MDJF1で証明済み)。是正後の供給をX(記事A in_one_line本文、記事B本文)/Z(メロス本文)で再計算して示す。

## 手順
S0. daily cost、`git status`件数、T-0・原文保存、ledger.jsonバックアップ(sha)。S1. 原因特定(発生run・時刻・経路)。S2. 点検(全entry分類表)。S3. 是正(無効化手段の決定→実施。不正entryの一覧と理由)。S4. 再発防止(最小改善+test、既存test全件PASS)。S5. 検証: 供給前後比較(X/Z)、golden再判定(PASS/NG変化一覧、変化があれば原因と品質影響)、必要なら既存wav 1〜2本でAzure実呼出(是正後Phrase Listでの転写)。S6. retry/fallback/resume整合(Ledger読込タイミング[OF-179時刻条件]、M1 snapshot、cascade研究経路が今後401で失敗したときの挙動=unconfirmed entryが供給対象外になること)。S7. SSOT: CURRENT_SPEC Pronunciation Ledger節へ是正注記、DECISION_LOG 1件、OPEN_ITEMS新規行(Status `LEDGER_REMEDIATION_DONE_PENDING_FABLE`)、OPEN-339(自動/人手区別)への関連注記、REPORT_LEDGER、ACTIVE_TASK。S8. secret scan→明示add(ledger.json、バックアップ、code+test、docs/research/PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01/*、delegation_log、SSOT)→commit→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_PLIR1.md 上書き。ユーザー§5の順)
修正した不正データと原因/同種点検結果(表)/再発防止策(file:行、test)/X・ZのProduction動作(供給前後)とRegression/PASS/NG影響(golden)/commit・SSOT/残存Open ItemとStatus材料(PRODUCTION_WIRED判定のチェック表、未確認項目)+4行判定。STOP時はUSER_DECISION_REQUIRED材料。