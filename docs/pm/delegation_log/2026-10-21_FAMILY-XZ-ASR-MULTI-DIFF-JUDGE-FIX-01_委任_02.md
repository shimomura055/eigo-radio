# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_02(Fable判定=**PRODUCTION_WIRED**の記録のみ。API 0・費用JPY0・コード変更なし)。並行agent: `FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_02`(er089、OPEN-434、Opus台帳、REPORT_LEDGER、ACTIVE_TASKを編集中)。共有プロトコル厳守(編集直前`git status --porcelain`+再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち、他agent分は`git restore --staged`)。

## Fable判定(記録用、変更しない)
- Status: **PRODUCTION_WIRED**(2026-10-21、Fable判定)。根拠: (1)実ログ(記事B Adv第1部attempt1)で旧コード再現→新コードPASS(HOMOPHONE_EQUIVALENT) (2)最小修正+27行、新ルール/閾値/辞書/flagなし、既存全文規則と同基準の個別span適用 (3)必須ケース(a)〜(g)18件PASS、旧コードで4件FAIL確認 (4)golden再判定193件: PASS→NG 0件、NG→PASS 1件(根拠明記)、中東/コーヒー/メロスは変化0 (5)X(er003 repro01:356)/Z(er012:553)が同一関数`evaluate_attempt_with_cascade`→同一valを通ることをtest固定 (6)契約不変test(ラベル集合・retry契約) (7)runtime evidence: Z=メロス既存clipで既存記録と整合、X=既存wav実ASRで対象span(storymaking)が吸収されたことを確認(別差分byus→BAUSでNGは判定基準どおり、是正対象外) (8)既存test非回帰(失敗6件は是正前から同一・無関係)。
- 付帯(未達ではない、監視項目): 新規音声のProduction E2Eでの再発防止は、次回以降のProduction run(記事A/B後続、開いた窓等)で自然発火を監視する(OPEN-283と同型の「monitor継続」)。専用の有料E2Eは起こさない。
- 既存test失敗6件(是正前から: er020 fullseg/er025 phase3/er006 routing/er006 kp5/er006 pool benches/er012 3v)は本件と無関係。後日の整備候補として記録のみ。

## 作業
S0. T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01_委任_02.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「MULTI-DIFF-JUDGE-FIX-01 委任_02」を含む最新index)。check結果1行。
S1. `OPEN_ITEMS.md` OPEN-435行頭Statusを`PRODUCTION_WIRED(Fable判定2026-10-21、監視: 新規Production runでの自然発火)`へ(旧Status保持)、行末にFable根拠(1)〜(8)を1文ずつ+付帯。
S2. `CURRENT_SPEC.md` OPEN-121節末の是正注記(委任_01追記)の直後に「【Fable判定 2026-10-21】`PRODUCTION_WIRED`(根拠=OPEN-435、証跡=docs/research/FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/)。既存6test失敗は是正前から同一で無関係」を1文追記。
S3. `DECISION_LOG.md`末尾の委任_01エントリの直後に「Fable判定: PRODUCTION_WIRED(根拠(1)〜(8)、付帯=monitor)」の短い追記エントリ1件。
S4. `docs/pm/REPORT_LEDGER.md` 1行、`docs/pm/ACTIVE_TASK.md`先頭追記。`docs/pm/USER_DECISION_REGISTER_01.md`は変更不要(ユーザー判断事項なし)。
S5. secret scan→明示add(delegation_log 2件、OPEN_ITEMS.md、CURRENT_SPEC.md、DECISION_LOG.md、REPORT_LEDGER.md)→commit(`FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_02: Fable判定PRODUCTION_WIRED記録(OPEN-435/CURRENT_SPEC/DECISION_LOG)`)→`git push origin HEAD:main`→到達確認。

## 報告(docs/pm/RESULT_PACKET_MDJF2.md 上書き)
各反映行番号、commit hash、raw URL、4行判定。