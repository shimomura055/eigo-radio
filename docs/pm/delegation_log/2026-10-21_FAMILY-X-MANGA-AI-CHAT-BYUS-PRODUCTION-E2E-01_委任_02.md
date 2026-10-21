# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_02(決定論annotation producerの「ドット区切りバージョン表記」抽出/注記不整合の是正[11-8範囲内の不具合是正、Fable判定済み]→回帰確認→`run_byus_01`を既存Research/Ledger/B3成果から再開→Writer/Std/Adv→音声→試聴ページ公開→SSOT。委任_01の手順・CP・禁止事項・Git・報告形式を全て継承する: `docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_01.md`を最初に読むこと)。
**並行agent**: 記事A `FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_01`が同じrunner・共有ログを使用中(text工程またはaudio工程)。共有プロトコル(委任_01冒頭)を適用。記事Aのrun dir・page・script・SSOT行は触らない。

## 性質/到達上限Status/禁止事項
- 性質: Production不具合是正(11-8範囲内)+Production E2E継続。到達上限=技術完成→`USER_LISTENING_PENDING`。
- Fable判定(記録用): `er053_b3_deterministic_producer_01.py`のSURF_RE(抽出器)が「26.10.10以上」を「26.10」「10以上」に分割し、`find_all`(注記器)が同じ表記の出現を認めない=抽出器と注記器の自己矛盾。承認済み設計(producer失敗=課金前STOP、注記なしfallbackなし)は維持したまま、**両者が同じ表記単位(ドット区切りの数値列=バージョン番号・小数等)を一貫して扱う**よう是正する。受理面・閾値・方式の新設/拡大ではなく、既存規則の整合是正。Opus独立レビュー(11-3)は非該当(構造変更なし・初回修正)。
- 費用: 本記事既使用JPY26.05(text: Research+Ledger 16.66、B3 9.39)。Guardrail JPY150(委任_01と同じ、合算)。残工程見積: Writer R0-R2約12.7+Adv/Std/RF約1.8+audio約23〜30=約JPY38〜45。当日累計(直近実測158.87、並行分含む)。是正・回帰テストは**API 0**で行う。
- 禁止(委任_01継承に加え): Fact/Ledger/B3の手編集、`--regenerate-stage storyline_b3`、研究・Research再試行(基本Factは揃っているため不要)、注記失敗時にfallbackで注記なしB3へ進む経路の新設、`rules_sha256`固定テストを「値の差し替え」だけで通すこと(差し替える場合は理由と新旧値を記録)、記事Aの出力への介入。

## 固定ブロック
E-1/D-1/G-1/F-1: 委任_01と同じ。
T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_02.md`へ逐語保存(extract tool、N=「BYUS-PRODUCTION-E2E-01 委任_02」を含む最新index)、`check_delegation_prompt.py`結果1行。
T-1: `TTS_EXECUTION_MODE=STANDARD`。T-2: TTSあり。

## 作業手順
S0. `git status --porcelain`(件数)、`daily_dev_cost_01.py --date 2026-10-21`、記事Aの進行状況は`er019_output/paycheck_personality/`の有無と`ps`で**観測のみ**(記事Aのprocessが実行中でも本修正はfile差し替えなので影響しない: 既にimport済みのmoduleは変わらない。ただし記事AがまだPythonを起動していない段階なら新規則で走る。どちらかを記録)。
S1. 原因の最小再現test(API 0): `er053_b3_deterministic_producer_01.py`の抽出器/注記器を直接呼び、`run_byus_01/research_ledger/verified_fact_ledger.txt` L90相当の文「アプリバージョン26.10.10以上」で `b_numbers`/`e_sidecar` が失敗することを再現し、test fileへ固定(`er053_b3_deterministic_producer_01_test_NN.py`の既存testに追加、または新規`..._dotted_version_test_01.py`)。
S2. 是正(最小差分): SURF_REにドット区切り数値列(`\d+(?:\.\d+)+`、例 26.10.10 / 5.5 / 1.2.3)を**1トークンとして最長一致**で扱う規則を追加し、`find_all`側も同じ表記単位で出現判定するように整合させる(既存「5.5の中の5を除く」規則は維持し、その意図=部分一致禁止を壊さない)。「26.10.10以上」のように数値列+助数/範囲語が連結する場合は、既存の数値+接尾語の扱いに合わせる(既存規則の読み取り結果を報告に記載)。コメントに管理IDと理由を1行。
S3. 回帰(API 0): (a)既存er053 producer関連test全件PASS。(b)`rules_sha256`が変わることを確認し、固定している箇所(test/golden)を特定して新値へ更新(新旧値を報告)。(c)**出力不変の証明**: 既存run(`er019_output/middle_east_yemen_saudi/run_mey_02`、および`er019_output/coffee_prices/`配下の最新run 1件)のLedger+selected_briefに対しproducerをoffline実行し、`rules_sha256`以外の出力(annotated md・sidecar・checks)が旧版とバイト同一であることを示す(旧版出力は既存run dirの成果物をそのまま比較対象にする)。差があれば是正を見直す(差分を広げない)。(d)run_byus_01のLedger+briefで全checks PASSになることをoffline確認。
S4. commit/push(是正+test+回帰evidence `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/ANNOTATION_FIX_01.md`: 問題/変更/改善/リスク、変更行、新旧rules_sha256、回帰結果)。
S5. 再開: runnerが既存Research/Ledger/B3を再利用して`writer`から継続できるか`--stage writer`の挙動をコードreadで確認(`er019_family_x_entertainment_production_runner_01.py`のstage分岐・既存artifact再利用条件)。再利用できるなら`--stage writer`→`--stage advanced`→`--stage standard`(または`--stage all`で既存stageがskipされる場合はそれ)で継続。再利用されず課金stageが再実行される設計なら、**開始前にSTOPして報告**(Research/B3の再課金はFable判断)。console→`console_text_02.txt`。
S6. 以降は委任_01 S2(text CP: CP-B1〜B7)→S3(audio)→S4→S5(ページ `user_test/manga_ai_chat_byus_e2e_01`)→S6(費用: 是正前26.05を含む合算)→S7(SSOT: OPEN-431行頭Status更新[新規行は作らない]、REPORT_LEDGER 1行、ACTIVE_TASK)→S8(secret scan→commit→push `HEAD:main`)。
S7. E2E_PLAN_01.md §2に「是正後再開」行、§Xに是正の記録(ANNOTATION_FIX_01.mdへの参照、記事Aとのrules_sha256の差[旧値で走った場合])を追記。

## 報告(docs/pm/RESULT_PACKET_FXBY2.md 上書き。委任_01の報告形式1〜8に加え、先頭に「是正」節: 1.何が問題だったか 2.何を変更したか(file:行) 3.何が改善されるか 4.リスク・注意点(rules_sha256変更、記事Aとの版差、既存出力不変の証明結果))。STOP時は到達stage・原因観測・既使用額・残作業・差分resume手順。末尾に4行判定。