# 委任_01: 『告げ口心臓』既存成果の固定+V3学習項目候補生成+フォーム提示+本文音声の再制作(Phase 1=第1報まで)

管理ID: FZ-TELL-TALE-HEART-RESELECT-REMAKE-01(Fable→sonnet-worker、2026-10-27)
ユーザー原文: `docs/pm/delegation_log/2026-10-27_FZ-TELL-TALE-HEART-RESELECT-REMAKE-01_USER.md`(必読・全文)。共通Charter=`CLAUDE.md`冒頭、実行層規則=`.claude/agents/sonnet-worker.md`。
成果物dir: `docs/research/FZ-TELL-TALE-HEART-RESELECT-REMAKE-01/`(新規)。報告=`docs/pm/RESULT_PACKET_FZTTR1.md`。

## 承認範囲と予算(Fable設定)
- ユーザー承認済み作業=既存Std/Advスクリプトを固定し、V3方式でKP/KW/文法候補を生成→V3フォームでユーザー選定を依頼。**本文音声(Narrator/Dialogue、Chunk分割、現行Z Production仕様)の再制作は承認済み**で、選定確定に依存しないので並列実行してよい(旧音声を完成版に流用しない。Voice/Style定義・固定Master等の共通資産は再利用)。
- **禁止**: 本文(R0/R1/R2/英訳/Std調整)の再生成・変更。学習項目のAI独断確定(`--kp-review auto`等の自動受理は使わない。`wait`でrc=4停止が正)。既存run/公開ページ(`user_test/family_z_tell_tale_heart_01`・`_chunk_01`、`run_chunk_01`/`run_sf_prod_02`)の上書き・削除。Gate緩和。未承認仕様の実装。
- **予算**: 本案件Cap=¥150(新規run全体)。Phase 1の見積(候補生成LLM+文法解説Top1/Top2 Std/Adv+本文TTS Std/Adv+ASR)を着手前に`BUDGET_PLAN_01.md`へ書き、¥150超の見込みなら実行せずFableへ報告。日次1,000円(JST)。各有料実行の前後に`stop_check`と実費を記録。
- **STOP/LR注意**: 本文TTSでLocal Rewriteが採用された(=音声用原稿が本文と食い違った)segmentがあれば、その音声を完成版・公開へ進めず、該当segmentのみSTOP扱いで事実(segment/Before→After/Gate結果)を報告する(別案件LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01で整合調査中)。他のsegment・工程は継続。Gate/HR Lockの緩和・迂回禁止。STOPセンチネル(`er026_output/family_z_production_e2e_01/STOP_ALL`等)・既存runnerのSTOP規則(PM_GOVERNANCE 26節)を遵守。

## 手順
### 1. 既存成果の確認と固定(API 0)
- OPEN-503(`OPEN_ITEMS.md` Grep)・DECISION_LOG(`告げ口心臓`/`TELL-TALE` Grep)・`docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/`・`FAMILY-Z-TELL-TALE-HEART-KP-FIX-01/`・`FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/PUBLIC_REPLACEMENT_01.md`から、Std/Advの**正式スクリプト正本**(run_sf_prod_02=案A配線後の正式再生成、run_chunk_01=その本文でのChunk分割版、公開差替え済み、ユーザー最終試聴PASS未取得)を特定し、所在・版・sha256(LF正規化と生バイト)を`FIXATION_01.md`に記録。複数候補の本文が同一か差分があるかを示す。差分があり正本を一意に決められない場合は候補版と差分を提示して本文に関わる工程をSTOP(他は継続)。
- 過去のKP選定結果・到達工程・音声・Chunk版・公開ページ・ユーザー承認状態(試聴PASS未取得、Adv三人称NG→案A再生成済み等)・現行仕様との差(V3フォーム/KP確定内容保護/文法pregen Top1-2/①②③表示仕様/Study Text Part 1/Chunk/セリフ文脈感情TTS/統一TTS retry/速度仕様/Style actual gate等。各`CURRENT_SPEC.md` Grepで`file:line`)・再利用可能資産を同ファイルに表で記録。
### 2. 新run作成+V3候補生成+フォーム提示
- 直近のZ正式記事(猿の手 `the_monkeys_paw` run_fzcw_e1_01等、`docs/research/FAMILY-Z-MONKEYS-PAW-PRODUCTION-01/`、KP-CONFIRMED-CONTENT-PROTECTION-01の`EVIDENCE_RESULT_04.md`、LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01、GRAMMAR-PREGEN-ALL-LEVELS-01、SLOT-23 `IMPL_E_01.md`/`ROUTE_STATUS_06.md`)で確立された**現行Z正式手順**を踏襲し、新run(例 `run_reselect_01`)を作る。既存本文を新runへ**そのまま**入力する方法(runnerの既存run本文再利用/`--stages`指定)はrunner(`er026_family_z_fiction_production_runner_01.py`)の承認済み機能だけを使い、本文生成stageを走らせない。本文のshaが手順1の正本と一致することを着手直後に検証して記録。
- V3方式でKP候補最大7/KW候補最大5(無理に埋めない、日本語訳+AI選定理由付き、承認済み選定仕様準拠)、文法Top1/Top2(解説全文を事前生成)をStd/Advで生成し、公開済みV3フォーム(`user_test/selection_form_v3/`)にデータを接続・公開(GitHub Pages)。候補ID・候補集合sha・本文sha(照合コード)を保持。Std/Advの選定URLを記録。runnerはHR待ちでrc=4停止(失敗ではない)。
### 3. 本文音声の再制作(選定非依存、並列)
- 現行Z Production仕様(承認済みVoice/Narrator・Dialogue Style/速度/Chunk/統一TTS retry・Fallback・LR/Primary・Secondary ASR/HR Lock/Gate)で、新runのStd/Adv本文音声を生成。runnerのstage分割で本文音声を先行できる場合のみ実施(KP/解説音声は選定確定後)。できない(本文音声がKP確定後の一括stage)場合は無理に分割せず、準備(stop_check・予算・Voice/Style解決確認・dry-run相当の検証)まで行い理由を報告。
- 生成後: ASR/Style/速度/Chunk/Gate結果、retry/fallback/LR発火の有無(発火segmentはBefore→Afterと最終採用attempt)、実費を`AUDIO_PHASE1_01.md`に記録。LR採用segmentは上記STOP規則。
### 4. 報告(第1報、`docs/pm/RESULT_PACKET_FZTTR1.md`)
ユーザー原文§8第1報の6項目: (1)固定スクリプトの版・sha (2)過去の制作状況と停止箇所 (3)V3フォームStd/Adv選定URL (4)KP/KW/文法候補の生成結果(件数・内容要約) (5)音声制作の準備/生成状況(Gate結果・LR有無) (6)未解決の品質問題・判断候補(A既判断/B自己解決/C独立/D新規の区分付き)。実費・残Cap・日次合計も記載。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)の編集はしない(Fableが同期)。ACTIVE_TASKは本案件行のみ更新可。Gitは**本案件で作成・変更したファイルのみ**`git add`してcommit/push可(`git add -A`禁止。公開ページ更新を含む)。commit messageに管理IDと実費を含める。
