# 委任文 保存: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_01 (2026-10-13)

(T-0保存。「ユーザー指示(原文)」節は逐語、他節は見出し保持の要点保存。)

## 管理ID

FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_01(初回。是正①Std KP Rule7の根本原因・修正、是正②Adv assemble Gateの検証状態引継ぎ不備の根本原因・修正、Regression追加まで。有料run・再生成は本委任では行わない=JPY0。是正③Part 2 N01再生成・完成版・試聴ページは、Fableが①②の修正をOpusレビューした後の委任_02で実施)。前身: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01(委任_01〜03、Sonnet上限到達のため新ID)。

並行タスク(領域分離): (a) ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_03 が `er011_b1_connected_speech_validator_01.py`/`er006_preprod_hardening_01_validation.py`/`er011_connected_speech_equivalence_layer_production_01.py`/`er006_secondary_asr_01.py` を編集中(本委任は読取のみ・編集禁止)。(b) FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01(`er076_*`)。一時ファイル: `docs/pm/ACTIVE_TASK_XZC.md`/`docs/pm/RESULT_PACKET_XZC.md`(commitしない)。出力: `er071_output/m2p0_n01_production_wiring_01/completion_01/`。SSOT編集権: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS[OPEN-310/343/346+新規]/UDR/REPORT_LEDGER。SSOT編集は最後にまとめ、直前 `git status --porcelain` で他agent未commit変更確認(あれば60秒x5回待ち、残れば自分の行のみ)。`.git/index.lock`待ち30秒x3、fetch->ff-only(不可なら`git pull --no-rebase`、conflict時は両追記保持)。全commitに `Managed-ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01` trailer。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様(M2P0・N01=APPROVED_FOR_PRODUCTION)を正常にProductionで動かすための既存不具合の是正(①②)。新Trial・仕様変更ではない。
- 到達上限Status: ①②=`FIXED_PENDING_PRODUCTION_RUN`(unit/regressionで修正確認、正式経路での完走は委任_02)。`PRODUCTION_WIRED`は付与しない。
- 費用: JPY0(LLM/TTS/ASR有料呼出禁止。既存artifact・mock・既存転写のみ)。
- 禁止: Rule7/Audio Validation Gate/M3 Gate/ASR Gateの緩和・迂回、未検証segmentの機械的PASS扱い、承認済みPrompt(N01/M2P0 P0 template sha 69d0e6ff.../static b8af4d50.../guidance 026aa730...)の実質変更、KP canonicalization promptの意味的変更(仕様上の新しい許容ルールが必要ならSTOP)、Family Z音声生成・記事再生成、Family Z KP経路変更(Strategy L維持)、並行agent編集中ファイルの編集、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`、秘密値出力、wav/telemetry/log add、ACTIVE_TASK/RESULT_PACKET commit、共有ファイル追記test(`er026_post_slowdown...test`、`er011*`一括、`er026_family_z_stop_sentinel_test_01.py`)実行、外部プロセス再起動、監督ループ/timeoutラッパ、Coffee run dir内の既存成果物の削除・上書き(新規ファイル追加・summary追記は可)。
- STOP条件: 仕様上の新しい許容ルール(Rule7の例外、canonicalizationの新規則)が必要 / Gate安全性を維持したまま引継ぎを実現できない(=正式Validation再実行が必要でそれが有料) -> 具体的判断事項と選択肢を明示して報告。「エラーが再発した」だけでは戻さない。
- STOP確認義務: `er026_output/family_z_production_e2e_01/`配下と `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/`配下の STOP/STOP_ALL/STOP_NOTICE 確認・記録(2026-10-12 Melos旧STOP_NOTICE=非適用)。
- Opus Gate: ②はGate入力の処理フロー変更に当たるため、実装後にFableがOpus条件Aレビューを行う(本委任は実装+testまで。`FIX2_DESIGN_01.md`を必ず書く)。①も同様に `FIX1_ROOT_CAUSE_01.md`。
- 時間見込み: 90〜120分。①②は独立(並列調査可)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep->該当行範囲Read基本。G-1: git出力は --porcelain/--stat/--short。F-1: transcript退避不要。T-0: 委任文を本ファイルへ保存し `check_delegation_prompt.py --file <path> --json-out <path>_check.json` 実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2: TTSなし。T-3: JPY0。

## ユーザー指示(原文)

(2026-10-13、管理ID FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01、全文)

# Claude Codeへの回答・是正指示

**管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01**

## 1. 今回の報告に対するユーザー・PM評価

`FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01` 委任_03の報告を確認した。

M2P0・N01のProduction配線が進んだこと、品質Gateを迂回せずSTOPしたことは適切。

しかし、次の3点について、原因調査・是正・検証を完了せず、ユーザーへ対応方針の判断を求めたことは不適切。

1. Standard KPのRule7エラー
2. AdvancedのAudio Validation Gateにおける検証状態引継ぎ不備
3. Standard Part 2の旧Fallback音声残存

**いずれも、原則として開発側が自律的に解決すべき既存不具合・未完了作業であり、ユーザーの仕様判断事項ではない。**

ユーザーはM2P0・N01の正式Production採用を既に承認している。

したがって、今回の作業は追加Trialではなく、承認済み仕様を正常にProductionで動かすための是正・完成作業とする。

現在Status: `APPROVED_FOR_PRODUCTION`(配線済みだが未完了)

今回の到達目標: `PRODUCTION_WIRED`

ただし、PM強制Gate未充足の場合は完了扱いとしない。

---

## 2. 是正①: Coffee Standard KP Rule7エラー

### 現象

`based on` -> `based on interviews` の不整合により、2 job・内部retry計4回で `CANONICALIZATION_INVALID`。

同じ失敗が再現している。

### 指示

**再生成を繰り返すのではなく、原因を特定して根本是正すること。**

以下を確認する。

- 元のKP選定結果とcanonicalizationへの入力
- `based on interviews` へ変化する工程
- Prompt、正規化ロジック、Rule7 Validatorの責任範囲
- 既存の同種不具合、特にOPEN-310との関連
- retryしても同じ不整合が繰り返される理由
- Family X・Z等の共通経路への影響

### 期待結果

- 原文とKPの整合性を維持する。
- Rule7を緩和して通すのではなく、正しいcanonicalization結果を生成する。
- 再発しうる同種の表現にも対応する。
- 原因のある工程で是正する。
- 必要なRegressionを追加する。
- 修正後にStandard KPを正式Production経路で完走させる。

仕様上の新しい許容ルールが必要な場合のみ、具体的な判断事項を明示してSTOPする。

**単にエラーが再発したという理由でユーザーへ戻さないこと。**

---

## 3. 是正②: Advancedの正式assemble Gate BLOCK

### 現象

音声自体は生成済みだが、再利用segmentが `SKIPPED_NOT_SELECTED=UNVALIDATED` と扱われ、正式assembleがBLOCK。

OPEN-346②と関連。

### 指示

**検証済み状態の正しい引継ぎを実現すること。**

以下を確認する。

- 元segmentの実際の検証結果
- 検証結果の保存・参照・継承経路
- 再利用時にUNVALIDATEDとなる原因
- retry・fallback・再assemble時の扱い
- 未検証segmentと検証済みsegmentを正しく区別できるか

### 期待結果

- 検証済みであることが証拠で確認できるsegmentのみ、正しい検証状態を引き継ぐ。
- 未検証segmentを機械的にPASS扱いしない。
- Gate自体は緩和しない。
- 必要なら元の正式Validationを再実行する。
- Regressionを追加する。
- Advancedの正式assembleをGate通過まで実行・確認する。

これは既存Gateの正常動作を回復する修正である。

**Gateの安全性を維持できる範囲の不具合是正について、ユーザーに「修正してよいか」と聞く必要はない。**

---

## 4. 是正③: Coffee Standard Part 2のN01適用

### 現象

Standard Part 2が、正式採用済みN01ではない旧Fallback音声のまま残っている。

M3 GateでBLOCK。

### 指示

**Standard Part 2を承認済みN01で再生成し、正式Validationを実施すること。**

- 既存N01 Promptをそのまま使用する。
- Standardの6%減速後検証を含める。
- ASR・音声品質Gateを通す。
- retry・fallbackを含め、正式採用仕様との整合を確認する。
- 不要な他segmentを再生成しない。
- 正式assembleに反映する。

既存の承認済み仕様・予算の範囲内で進めること。

**通常の再生成費用について逐一ユーザー判断を求めない。**

ただし、承認済み予算・retry上限を超える場合はSTOPする。

---

## 5. Production完成・試聴ページ

①〜③の是正後、Coffee Standard・Advancedについて、正式Production経路を使用して完成版を作成すること。

### Standard

- M2P0 Key Phrase生成・検証PASS
- N01 Full Story全対象part生成
- Standard 6%減速およびASR再検証PASS
- Audio Validation / M3等の必要Gate PASS
- 正式assemble完了

### Advanced

- M2P0 KPの正式反映
- N01 Full Story各partの正式反映
- 再利用segmentのValidation状態を正しく検証・引継ぎ
- 正式assemble完了

### 試聴ページ

現在のCoffee試聴ページは途中段階の品質確認用であり、Production完成版の証拠ではない。

是正後は、**正式完成版の音声を用いた試聴ページを改めて提示すること。**

ユーザーが旧版と新版を混同しないよう、対象音声・生成日時・適用仕様を識別可能にする。

速度・ポーズの最終聴感判断は、完成版を提示した段階で依頼する。

---

## 6. ユーザー判断と開発側責任の区分【再発防止】

今後、以下を厳格に区別すること。

### 開発側が自律的に実施する事項

- 原因調査
- 既存仕様に沿ったバグ修正
- Validator不整合の原因是正
- Regression追加・実行
- 正当な検証記録の引継ぎ
- 承認済みPromptによる再生成
- 承認済みProduction経路への配線
- runtime evidence取得
- SSOT・Git反映
- 承認済み仕様への適合確認

これらについて、単に作業が必要だからという理由でUSER_DECISION_REQUIREDとしない。

### ユーザー判断が必要な事項

- 新しい仕様・品質基準の採用
- Validator / Gateの安全基準変更・緩和
- 承認済みPromptの実質的変更
- 承認済み仕様の撤回・対象範囲変更
- 予算・実行上限を超える作業
- 品質と機能のトレードオフを伴う方針変更

**重要: 技術的に難しい問題であっても、それだけではUSER_DECISION_REQUIREDではない。**

まず原因・既存仕様・安全な修正方法を調査すること。

それでもユーザーにしか決められない仕様上の選択肢が残る場合に限り、具体的な判断事項を提示する。

一方、必要な安全Gateに不合格となった場合は、Gateを迂回せずSTOPする。

STOPすべき場合と、自律的に原因調査・是正を続けるべき場合を混同しないこと。

---

## 7. 既存決定との整合

以下の既存承認事項を維持する。

- Family X: M2P0正式採用
- Family Z: KPはStrategy L維持、DB Hybrid+M2P0不採用
- Family X・Z: N01正式採用
- N01 Prompt文言は変更しない
- Family Zの記事再生成・音声化STOP維持

今回の作業でFamily Zの音声生成を開始しない。

N01の適用範囲・Coffee原稿v5・既存再生成範囲等については、CURRENT_SPECと過去のユーザー決定を照合し、承認済み範囲で進めること。

真に未決の仕様があり、完成作業に影響する場合だけ、具体的な選択肢と影響を示して報告する。

---

## 8. QCD・作業効率

- 原因調査を先行し、失敗が確実な再生成を繰り返さない。
- 共通原因があれば個別patchではなく共通機構を修正する。
- 既存の実装・テスト・成果物を最大限再利用する。
- API費用・時間・品質への影響を記録する。
- 独立作業は可能な範囲で並列化する。
- ただし共有state・STOP_ALL等の競合がある作業は同時実行しない。
- 承認済み予算・安全Gate・retry上限を厳守する。
- 新しい改善Trialを独自に開始しない。

承認済み作業の範囲で合理的に解決できる不具合は、調査・修正・検証まで進めること。

---

## 9. Production Wiring Checklist

以下をすべて確認すること。

1. 正式Production初回経路に実装済み
2. retry / fallback / regenerationで仕様整合
3. DEV / Trial専用経路への依存なし
4. 正式Production runtimeで発火確認
5. 必要なRegression / Validator / integration test PASS
6. actual model_id / routing等のruntime evidence
7. CURRENT_SPEC更新
8. DECISION_LOG更新
9. OPEN_ITEMS更新・close
10. 必要なGit commit / push / merge確認
11. ユーザー承認内容とProduction挙動の一致
12. 関連する未解決事項の報告・管理

1項目でも未確認なら`PRODUCTION_WIRED`にしない。

Dangling Reference Checkも実施すること。

---

## 10. 最終報告

以下を簡潔に報告すること。

1. Standard KPの根本原因・修正内容・再発防止策
2. Advanced Validation引継ぎ不備の原因・修正内容
3. Standard Part 2のN01再生成結果
4. Standard / Advanced正式assemble・Gate結果
5. Production runtime evidence
6. Regression結果
7. 最終完成版の試聴URL
8. 使用費用・所要時間・QCD
9. CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS・Git反映
10. 未完了事項および真に必要なユーザー判断事項

**今回の目的は、技術的な問題をユーザーへ差し戻すことではなく、承認済みのM2P0・N01を正式Production経路で完成させることである。**

未承認の仕様変更が本当に必要な場合だけSTOPする。それ以外は原因調査・是正・再検証まで責任を持って実施すること。

(ユーザー指示 原文ここまで)

## Fable補足(要点)

- 事前指定Read: 前回成果 `er071_output/m2p0_n01_production_wiring_01/{FINAL_REPORT_02,EVIDENCE_02,CHECKLIST_02}.md`、`docs/pm/RESULT_PACKET_XZW.md`、Coffee run dir `a2/key_phrases/`・`a2/key_phrases_d02_attempt_invalid/`・`b1b/`、関係コード(er030 selector/core/m2_supply、er003_v1_n3_01_scaffold_generate.py、Rule7実装、er019 runner、Audio Validation Gate実装)、OPEN-310/343/346。禁止ファイル(読取のみ): er011_*、er006_preprod_hardening_01_validation.py、er006_secondary_asr_01.py。
- 是正①: 根本原因特定(`FIX1_ROOT_CAUSE_01.md`)/原因工程での修正(Rule7を緩めず、P0 template/static/guidance shaを変えない)/Regression(『based on』型+同種表現、既存er030/er003 PASS、Parity Gate維持確認)/dry-run(API 0)。
- 是正②: 根本原因(`FIX2_DESIGN_01.md`)/修正設計(証拠で確認できるsegmentのみ`REUSED_VALIDATED`で引継ぎ、記録なし・sha不一致はUNVALIDATEDのままGate BLOCK維持、Gate判定自体は変更しない)/実装+Regression/dry-run(新規ファイル`b1b/validation_state_rebuilt_01.json`)。
- SSOT(最後): OPEN-343/346/310追記、DECISION_LOG本IDエントリ、CURRENT_SPECは変更しない(矛盾があれば報告)、UDR #47/#50を「開発側責任として是正中」へ、REPORT_LEDGER行。
- Git: 明示addのみ。commit 2回(実装+test / SSOT)、メッセージ例「FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_01: 是正①Std KP Rule7根本原因+修正、是正②再利用segment検証状態引継ぎ(REUSED_VALIDATED)+Regression、JPY0、有料runなし」。secret_scan hits=0。push。
- 報告(RESULT_PACKET_XZC.md): (0)check結果・STOP確認 (1)①根本原因・修正・再発防止・Parity・dry-run (2)②原因・設計・実装・dry-run (3)Regression前後件数 (4)Family Z/共通経路影響 (5)SSOT更新 (6)commit hash+raw URL (7)Status(①②=FIXED_PENDING_PRODUCTION_RUN)、委任_02で必要な有料run一覧と見積、STOP該当の判断事項。

## 事前指定Grep一覧+追記位置・更新位置の手順

Grep: `Grep -n "Rule7|RULE_7|CANONICALIZATION_INVALID"`、`Grep -rn "SKIPPED_NOT_SELECTED|UNVALIDATED|audio_validation_gate"`、`Grep -n "**OPEN-310"`。追記位置: OPEN_ITEMS該当行末尾、DECISION_LOG末尾、UDR #47/#50、REPORT_LEDGER末尾。

## 実行コマンド全文

```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_01.md --json-out docs\pm\delegation_log\2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_01_check.json
.venv\Scripts\python.exe -m pytest <新規test> -q
.venv\Scripts\python.exe run_project_regression.py --pattern "er030*_test*.py" / "er003_v1_n3_01*_test*.py" / "er019*_test*.py"
.venv\Scripts\python.exe tools\secret_scan_01.py --staged
```
