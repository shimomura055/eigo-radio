# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_03(是正[er053 deterministic producer NUM量化子、commit 35c3c450f]のSSOT整合: CURRENT_SPEC/DECISION_LOGの旧`rules_sha256`記述へ新値注記、DECISION_LOG是正エントリ、commit後のer083 test再確認)+小整備(er053静的参照testの許可リストにTrial harness群を追加)。API 0・費用JPY0。並行agentなし(記事A/Bの本体runは終了済み)。

## 性質/到達上限Status/禁止事項
- 性質: 記録整合+test整備のみ。Production .py(`er053_b3_deterministic_producer_01.py`等)は変更しない。到達上限=`DONE`。
- 禁止: Production code/Prompt変更、閾値変更、`git add -A`等、CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSの全文読込(Grep→該当行のみ)。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_03.md`へ逐語保存(extract tool、N=「BYUS-PRODUCTION-E2E-01 委任_03」を含む最新index)、check結果1行。T-2: TTSなし。

## 作業手順
S1. `CURRENT_SPEC.md`で`525f2309`をGrep(2箇所)。各箇所の文脈を読み、旧値は消さずに「(2026-10-21 FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_02でNUM量化子`(?:\.\d+)?`→`(?:\.\d+)*`に是正[ドット区切り数値列を1表面として抽出器/注記器を整合、11-8範囲内]、現行rules_sha256=3b4b7fdf8dc6816cf8368b538c4b85485dba33ed2a114a8319b13a060050f723。是正記録=docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/ANNOTATION_FIX_01.md)」の注記を追記。仕様文の意味は変えない。
S2. `DECISION_LOG.md`末尾(直近エントリ書式=L21866付近をGrep)に是正エントリ1件: 問題/変更(file:行、新旧sha)/改善/リスク(既存3 runでrules_sha256以外バイト同一、test固定の更新)/判定根拠(11-8: 抽出器と注記器の自己矛盾の是正、受理面・閾値・方式の新設なし、producer失敗=課金前STOPの設計維持、Opus非該当)/ユーザー指示原文path(`docs/pm/delegation_log/2026-10-21_FAMILY-X-TWO-ARTICLES-PARALLEL-PRODUCTION-E2E_USER.md` §5「既存の承認済み仕様内で解決できる不具合は、自律的に原因究明・修正・検証する」)。`DECISION_LOG.md`内の`525f2309` 2箇所は書き換えず(履歴)。
S3. commit後の状態で`er083_b3_background_fact_trial_01_test_01.py`全件と`er053_b3_deterministic_producer_dotted_version_test_01.py`、`er019_family_x_b3_min2_test_01.py`を実行し結果を記録(未commit差分検出型のFAILが残るなら、その差分file名と理由)。
S4. 小整備: `er053_family_x_factlock_ja_writer_01_test_01.py::StaticTests::test_w1_rf_queue_contract_referenced_only_by_entertainment_runner_after_c2`(委任DWA 委任_02で既存FAIL。Trial harness er082/er083/er086がProduction module名を参照)について、testの許可リストに**Trial harness群(`er082_*`, `er083_*`, `er086_*`、必要なら`er087_*`)を読み取り専用importとして許可**する最小変更。testの意図(Production経路以外からの書込/配線を防ぐ)を壊さないこと: 許可はimport参照のみで、Production module内の書込経路の新設を許すものではない旨をコメントに。変更後、同test file全件PASSを確認。Production .pyは触らない。
S5. OPEN-431行末に「委任_03: SSOT整合済み」1文、REPORT_LEDGER 1行、ACTIVE_TASK先頭追記。secret scan→明示add(CURRENT_SPEC.md、DECISION_LOG.md、OPEN_ITEMS.md、REPORT_LEDGER.md、test file、delegation_log)→commit(`FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_03: er053是正のSSOT整合(CURRENT_SPEC注記+DECISION_LOG)+静的参照test許可リスト整備`)→`git push origin HEAD:main`→到達確認。

## 報告(docs/pm/RESULT_PACKET_FXBY3.md 上書き)
1. CURRENT_SPEC注記箇所(行番号・注記文) 2. DECISION_LOGエントリ(行番号) 3. S3 test結果 4. S4変更内容(file:行、PASS件数) 5. commit hash・raw URL 6. 4行判定。