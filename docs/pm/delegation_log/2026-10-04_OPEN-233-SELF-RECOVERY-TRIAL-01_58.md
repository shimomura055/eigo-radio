## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_58)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: (1)ユーザー決定(2026-10-04)の逐語記録とStatus更新、(2)機械判定(決定論的floor等)を正式採用の「重大/軽微/問題なし」基準へ整合させる**設計**(実装はしない。Opus独立レビューに出す)、(3)「動機の帰属=軽微」と「根拠のない動機の創作=重大」の仕様不一致の整理、(4)限定flow確認の計画案。
- 到達上限Status: 説明文混入対策(P-strict-closed)=`APPROVED_FOR_PRODUCTION`(未配線)。機械判定の整合=設計のみ(実装はOpusレビュー後)。次Trial(5記事×2レベル)は開始しない。
- 禁止事項: コード・Prompt・テストの編集禁止(設計のみ)。LLM/API呼び出し禁止(¥0)。Production正式pathの変更禁止。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`の編集禁止(案文はdocに)。既存より厳しくする変更を線引き採用に便乗して提案しない。主体取り違え・数値改変・否定反転など本当に重大なケースを一括して緩める案を推奨しない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分に触れない。
- 費用上限: ¥0(T-3対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 機械判定(Safety系の決定論的判定処理)の変更は条件A(deterministic処理とLLM処理の役割分担の変更、Safety判定)に該当。ユーザーも「該当する場合は必ずレビュー」と指示。本委任は設計までで、レビューはFableが依頼する。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58.md`。**委任文は全文そのまま保存(要旨化・参照形式は不可。直近2件がFAILになっている)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文)

次の全文を`DECISION_LOG.md`末尾へ一字一句そのまま引用する(作業1)。

````
OPEN-233について、以下のユーザー判断を反映して進めてください。

## 1. 今回確定したユーザー判断

### A. 説明文混入対策
今回のガード付き後段分離方式は、

- 次の確認で有効化する
- 将来Productionへ接続する自己修復機構の正式な構成要素に含める

で正式採用します。

Statusは **APPROVED_FOR_PRODUCTION** として追跡してください。

ただし、Production正式経路への接続・必要テスト・runtime evidence・SSOT/Git反映まで完了するまでは `PRODUCTION_WIRED` ではありません。

### B. `prices began to fall` と機械判定
ユーザー判断では、この表現は **軽微** です。

一部の機械判定によってMajorへ強制昇格する状態は受け入れません。

**機械判定も、今回正式採用した「重大 / 軽微 / 問題なし」の基準に合わせて見直してください。**

単にこの1文だけを例外登録するのではなく、過去再分類で

- LLM判定では軽微以下
- 機械判定だけでMajor

となっていた8種類を確認し、現在の正式基準との不整合を修正してください。

ただし、主体取り違え・数値改変・否定反転等、本当に重大なケースまで一括して緩めないこと。

### C. 次Trial前の確認
以下は実施してよいです。

- 少数の実際のflowでの確認
- 29件横断確認を1回

ただし、**5記事 × Standard / Advanced = 計10本の次Trialはまだ開始しないでください。**

今回の残課題を解消し、上記確認結果をユーザーへ報告した後にGO判断を取ります。

---

## 2. 機械判定を新しい正式基準へ整合させる

今回正式採用した基準と、現在の決定論的な機械判定を突き合わせてください。

特に、過去に確認された

**LLMでは軽微以下なのに機械判定だけでMajorになった8種類**

を1件ずつ確認してください。

各ケースについて、

- 何の機械判定が発火したか
- なぜMajorへ上がったか
- 新しい正式基準ではどう判定すべきか
- 本当に安全上残すべき検出か
- 過剰判定ならどう修正するか

を整理してください。

目的は「機械判定を弱くすること」ではなく、

**正式基準と機械判定を一致させること**

です。

個別例外の追加ではなく、同種ケースに再発しない形で修正してください。

必要な回帰テスト・安全対照を実施してください。

この変更はSafety系の判定処理に触れるため、既存のOpusレビュー条件に該当するか判定し、該当する場合は必ずレビューを入れてください。

---

## 3. 「動機」の仕様不一致を整理する

現在、

- 「動機の帰属は軽微」
- 「根拠のない動機の創作は重大」

という記述が混在しています。

これは現時点ではユーザー判断事項にしません。

まず既存仕様・過去の承認内容・実装を確認して、

- 両者が同じ事象を指しているのか
- 「動機の帰属」と「動機の創作」に実質的な違いがあるのか
- 既存仕様では何を軽微と想定していたのか
- 今回正式採用した「重大な誤解だけ止める」基準ではどう整理すべきか
- 今回の一般化によって既存より不用意に厳しくなっていないか

を整理してください。

**既存より厳しくする変更を、今回の線引き採用に便乗して追加しないでください。**

整理だけで解消できるなら仕様・実装を整合させてください。

本当に新しい価値判断が残る場合のみ `USER_DECISION_REQUIRED` としてユーザーへ戻してください。

---

## 4. 説明文混入対策を有効化

採用済みのガード付き後段分離方式を、今回の限定確認では有効にしてください。

前提：

- CheckerのPrompt・Schema・判定方法は変更しない
- 引用部分を後段で安全に分離
- 一意に確定できる場合のみ採用
- 句読点差だけなら承認済みの句読点吸収を使う
- 再推測で似た文を選ばない
- 確定不能ならfail-safe

です。

既存346件で悪化0を確認済みですが、実flowでも、

- 誤った範囲をRewriteしない
- Human Reviewが不必要に増えない
- false PASSが増えない
- Checker検出性能を変えない

ことを確認してください。

---

## 5. 句読点差対策

句読点差対策は、

**自己修復機構そのものをProductionへ接続するとき、その照合処理の一部として必ず入れる正式構成要素**

です。

今の既存Productionへ単独で差し込む話ではありません。

Production wiring時には、

- 自己修復機構
- 句読点差吸収
- 説明文混入の後段分離
- 最小Rewrite
- retry / fallback / regenerationとの整合

を一体として確認してください。

句読点差対策が抜けていた場合は `PRODUCTION_WIRED` としないこと。

---

## 6. 英語だけ修正する方針

既存方針を維持してください。

LedgerとのDeviationが英語側にある場合、原則として英語だけ修正します。

- 日本語本文へ遡って同期修正しない
- 日本語タイトルは変更なし前提
- 古い日本語から英語を再生成する場合は、再生成後に必ずCheckerを通す

この経路が実際に守られていることを限定flow確認で確認してください。

---

## 7. 今回実施してよい確認

上記の是正後、

### ① 少数の実flow確認
新しい正式基準、機械判定修正、英語だけ修正、句読点差対策、説明文混入対策を有効にした状態で確認してください。

確認項目：

- false PASSがない
- 過剰Majorが減っている
- 不要Rewriteが減っている
- Human Reviewが増えていない
- 最小Rewriteが守られている
- retry / recheckで仕様が崩れない

### ② 29件横断確認
少数flow確認で問題がなければ、29件横断を1回実施してください。

問題が出た場合は、無駄に29件へ進まずSTOPして原因を報告してください。

### 禁止
**5記事 × Standard / Advanced = 10本の次Trialは開始しないこと。**

29件まで終わったところで必ずSTOPし、ユーザーへ報告してください。

---

## 8. Closeout時の必須確認

今回の作業終了時に、

- USER_DECISION_REQUIREDが残っていないか
- APPROVED_FOR_PRODUCTIONだが未配線の項目
- Production wiring漏れ
- Trialだけに存在する対策
- CURRENT_SPEC / DECISION_LOG / OPEN_ITEMSとの不一致
- Dangling Reference
- 未報告Trial
- ユーザー承認なしの仕様追加

を確認してください。

今回のSTOP地点は、

**少数flow確認＋必要なら29件横断まで**

です。

5記事×2レベルTrialには進まないでください。
````

## 作業1: ユーザー決定の記録とStatus更新(SSOT)

1-1. `DECISION_LOG.md`末尾に「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-04、ユーザー決定[3回目]: 説明文混入対策P-strict-closedを`APPROVED_FOR_PRODUCTION`[未配線]/機械判定を正式基準へ整合[8種類の確認、本当に重大なケースは緩めない、Opusレビュー]/動機の仕様不一致は整理[便乗して厳しくしない]/限定flow確認+29件横断1回は可、次Trialは禁止/Closeout必須確認)」を追記し、上の原文を全文逐語で引用。続けて「Fableの受け止めと分担」: 委任_58=記録・機械判定整合の設計・動機の整理・限定flow計画、→Opus独立レビュー(条件A)→Fable再評価→委任_59(実装・安全対照・回帰)→委任_60(限定flow→29件横断)→委任_61(Closeout確認・報告)。
1-2. `OPEN_ITEMS.md` OPEN-233行Status: 「ユーザー決定反映中(2026-10-04、委任_58): P-strict-closed=`APPROVED_FOR_PRODUCTION`(未配線)。機械判定の正式基準への整合を設計中(Opusレビュー予定)。限定flow確認・29件横断1回は承認済み(未実施)。次Trial(5記事×2レベル)は開始禁止。`PRODUCTION_WIRED`ではない。」(旧Statusは「旧Status参考(委任_57)」として残す)。`OPEN-233-A1-PROD`行: 本文を「Production配線時に一体で確認する構成要素: 自己修復機構・句読点差吸収・説明文混入の後段分離(P-strict-closed、`APPROVED_FOR_PRODUCTION` 2026-10-04)・最小Rewrite・retry/fallback/regenerationとの整合。句読点差対策が抜けていた場合は`PRODUCTION_WIRED`としない」に更新。
1-3. `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考に1文追記。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(ユーザー決定[3回目]反映中、次Trial開始禁止)」(addしない)。

## 作業2: 機械判定を正式基準へ整合させる設計(実装しない)

対象の「8種類」: 委任_51の再分類(`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`)で「LLM判定がACCEPTABLE/QUALITYなのに決定論floorだけでBLOCKINGになった」K08・K09・K11・K12・K13・K14・K15・K17。加えて、K19(`prices began to fall`、`changed_comparison`のfloor)とK04(例1、floor発火の有無を確認)も同じ表に入れる。

2-1. **1件ずつの確認表**(記録から。`er052_output/open233_cycle_new_issue_analysis_01/cases_detail_01.csv`、`er052_output/open233_missed_detection_truth_check_01/`、各instance JSONの`stage2_results`): 原文(逐語)、Ledger事実(逐語)、Checkerのtrueフラグ、発火した機械判定の名前と条件(runnerの`FLOOR_FLAGS`によるfloor/`precheck_floor`/列挙の波及[委任_35で是正済み]/その他。関数名・行)、LLM判定、最終判定、なぜMajorへ上がったか(どのフラグがどの差を根拠に立ったか。例: `changed_actor`が「副社長→executive」の一般化で立った、`changed_comparison`が「上げ幅縮小→下落」で立った)、正式基準での判定(重大/軽微/問題なし、基準のどの項目か)、本当に安全上残すべき検出か(主体取り違え・数値改変・否定反転・因果創作・時期創作のどれかに実質的に当たるか)、過剰判定ならどう直すか(同種ケースに再発しない形)。
2-2. **機械判定の全体像**: runnerの決定論的な判定を全部列挙する(Grep `FLOOR_FLAGS`、`floor`、`precheck`、`apply_disclosure_gap_downgrade`、`hook`、`escalate`、`actor_rewrite_guard_ok`、`SAFETY_CRITICAL`、`deterministic`): 名前、発火条件、効果(BLOCKINGへ昇格/降格/ガード)、根拠にする情報(Checkerのフラグだけか、記事・Ledgerのテキスト比較か)、導入時の目的(設計書・DECISION_LOGをGrepで確認し出典を示す)。
2-3. **不整合の原因の切り分け**: 8種類の過剰判定が、(a)Checkerのフラグ自体が過剰(一般化・方向のニュアンスで`changed_actor`/`changed_comparison`を立てる)なのか、(b)floorがフラグだけを根拠にして記事・Ledgerのテキストで裏取りしていないからか、(c)列挙の波及(是正済み)の残骸か、を件数で示す。
2-4. **設計案(2案以上、個別例外は不可)**。例:
   - 案F1「フラグ+裏取り」: floorは、Checkerのフラグに加えて決定論的な裏取りがあるときだけBLOCKINGへ昇格する。裏取りの例: `changed_number`=claimとLedger値の数値トークンが実際に異なる(既存precheckの`number_mismatch`を再利用)、`changed_negation`=claimとLedger事実文の否定語の有無が異なる、`changed_actor`=claimの主体名詞がLedgerの主体と異なり、かつ一般化(上位語・役職の抽象化)ではない、`changed_comparison`/`changed_time`=数値・日付・方向語のトークンが実際に異なる。裏取りが取れないフラグは「QUALITY以上」の下限にとどめ、BLOCKINGにするかはLLM判定に委ねる。Ledgerが日本語でclaimが英語である点(言語をまたぐ裏取りの難しさ)をどう扱うかを明記する。
   - 案F2「フラグの階層化」: 数値・否定・主体の取り違え(入れ替え)は従来どおりフラグだけで昇格、比較・時期・主体の一般化はLLM判定に委ねる(フラグはQUALITY下限のみ)。「主体の取り違え」と「主体の一般化」をフラグだけで区別できるか(できないなら案F1の裏取りが要る)。
   - 案F3「Stage 2への再提示」: floorはBLOCKINGに確定させず、「フラグが立っている」事実をStage 2のPromptに明示して再判定させる(LLM呼び出しは増やさない形で、既存のStage 2呼び出しの入力に含める)。非決定性が増える。
   - 各案について: 8種類+K19+K04がどうなるか、**Safety対照(Safety12のer009 9フラグ、Safety-critical 5件、Hormuz NG5)が1件も落ちないか**を既存記録でオフライン再生(フラグと記録済みテキストから決定論部分を計算。計算できない部分は「要実測」と書く)、実装規模、retry/fallback/regenerationとの整合、非決定性、Production配線時のリスク。
   - 推奨案と理由。既存より厳しくなる箇所が無いことの確認。
2-5. **再較正の計画**: 実装後に回す安全対照の構成(委任_55の`er052_open233_element_trial_safety_control_05.py`の較正セット(a)〜(f)+8種類+K19)と費用見積もり(Stage 2単価は委任_55実測から)。

## 作業3: 「動機」の仕様不一致の整理

3-1. 出典を全部Grepで集める: Stage 2 production rubricの「動機の帰属」(`er052_open233_self_recovery_stage2_production_01.py`)、設計書§0-2「未確認の人物・行動・動機・数字の追加」(BLOCK候補)、B4-a(「when AI struggled, a person could help」=設計意図・動機の創作、BLOCKING)、K20〜K22、V4〜V7の原則文、DECISION_LOGで「動機」を含む承認エントリ(Grep `動機`)。各出典の逐語と、いつ・どの委任で・ユーザー承認の有無。
3-2. 整理: (a)「動機の帰属」(Ledgerにある行為に、Ledgerに無い理由・意図を添える)と「動機の創作」(Ledgerに無い行為・仕組み・意図そのものを新事実として書く)は同じ事象か、実質的な違いは何か、具体例で示す(B4-aは、Ledgerに無い「AIが困ったら人が助ける」という仕組みの説明=新しい具体的事実)。(b)既存仕様(rubric導入時)が軽微と想定していた事象は何か(導入時の較正例を示す)。(c)正式基準では、「新しい具体的事実の追加」に当たる動機の創作は重大、Ledgerの行為に自然に付随する理由づけで新しい具体的事実を加えないものは軽微または問題なし、と整理できるか。(d)V7の文言(委任_55)が既存より厳しくなっていないか(V6との差分`er052_output/open233_safety_control_03/rubric_diff.md`で確認。厳しくなった箇所があれば逐語で示す)。
3-3. 結論: 整理だけで解消できるなら、rubricの「動機の帰属」文と設計書§0-2の記述をどう整合させるか(案文。実装はしない)。新しい価値判断が残るなら、その論点だけを`USER_DECISION_REQUIRED`候補として明示(安易に戻さない)。

## 作業4: 限定flow確認の計画案(実行しない)

ユーザー指示§7①の確認項目(false PASSなし/過剰Majorの減少/不要Rewriteの減少/Human Review増なし/最小Rewrite/retry・recheckで仕様が崩れない)と§6(再生成後のChecker再検査の経路)を測るための構成案: 対象instance(固定Stage 1の`meta_run03_standard`、`hormuz_run03_standard`、`safety_A4`、Safety対照`safety_er009_changed_number`、`safety_A2A3`等)、有効にするスイッチ(`HANDOFF_MODE=violation_span`、`VS_MATCH_EXT`、`VS_EXPLAIN_SPLIT`、`JA_MODE=english_only`、rubric V7、機械判定修正版)、n、比較対象(rep22・rep21の同入力の記録)、測る値(`residual_at_pass`、既知問題集合の見逃し疑い、Stage 4理由分布、成立水準、P確定の件数と`dropped_remainders`、JA処理が呼ばれていないことの証跡、費用)、合否基準案、費用見積もり(rep22実測 1 runあたり¥1.0〜2.2)。29件横断の構成(iter8と同じ38 instance-run、スイッチ、見積もり¥35〜60)と「少数flowで問題が出たら29件へ進まない」判定基準案。

## 事前指定Read一覧

- `docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`: 8種類・K19・K04の節(Grep `K08`等)。
- `er052_output/open233_cycle_new_issue_analysis_01/cases_detail_01.csv`、`er052_output/open233_missed_detection_truth_check_01/cases_01.csv`・`results_01.json`: Pythonで該当行だけ。
- 各instance JSON(該当種類の`stage2_results`): スクリプトで該当フィールドだけ。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `FLOOR_FLAGS`、`floor`、`precheck_floor`、`build_precheck_floor_claims`、`apply_disclosure_gap_downgrade`、`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`、`actor_rewrite_guard_ok`、`_ACTOR_NOUN_PATTERN`、`SAFETY_CRITICAL_CLAIM_DEFS`、`escalate` → 該当範囲だけ。
- `er052_open233_self_recovery_stage2_production_01.py`: 28〜120行(rubric V7含む)、Grep `動機`。
- `er052_open233_self_recovery_stage2_calibration_01.py`: Grep `V7`、`動機`。
- `er052_output/open233_safety_control_03/rubric_diff.md`: 全文。
- `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `0-2`、`B4-a`、`動機`、`floor`、`FLOOR_FLAGS`、`precheck` → 該当範囲(全文Read禁止)。
- `DECISION_LOG.md`: Grep `動機`、`floor`(OPEN-233関連の承認エントリの確認。全文Read禁止)。
- `docs/pm/open233_materiality_criteria_2026-10-03.md`: 正式採用節。
- `er052_open233_element_trial_safety_control_05.py`: 較正セットの構成(Grep `def `と`SET`)。
- `OPEN_ITEMS.md`: Grep `OPEN-233` → 該当行。`REPORT_LEDGER.md`: 該当行。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のGrepパターン。
- `DECISION_LOG.md`末尾追記、`OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行、`ACTIVE_TASK.md`。
- 新規doc: `docs/pm/design_open233_floor_alignment_01.md`(作業2・3・4の全内容。ユーザーが読める日本語、各節冒頭に結論、数値に出所)。

## 実行コマンド全文

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58.md_check.json

オフライン再生(作業2-4。標準ライブラリのみ、runnerをimportしない):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_floor_alignment_offline_01\replay_01.py

テスト・回帰は不要(コード変更なし)。

## SSOT追記文

作業1のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾、`OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行)。
- 明示add対象: `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/design_open233_floor_alignment_01.md`、`er052_output/open233_floor_alignment_offline_01/`配下、`docs/pm/delegation_log/2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58.md`、同`_check.json`。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 2026-10-04ユーザー決定(P-strict-closed正式採用・機械判定の正式基準整合・動機仕様の整理・限定確認の承認・次Trial禁止)を逐語記録、機械判定整合の設計案と動機仕様の整理を作成(未実装、Opusレビュー前)(委任_58)`。`git push origin main`まで。競合は自動解決せず報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内(不整合の原因の内訳、推奨案、Safety対照のオフライン再生結果、動機の整理結論[解消可/USER_DECISION_REQUIRED候補]、限定flowの費用見積もり)、(2)作業2-1の表の要約、(3)設計案の比較表、(4)作業3の結論と案文、(5)作業4の計画、(6)Opusに見てほしい論点(10項目以内)、(7)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。
