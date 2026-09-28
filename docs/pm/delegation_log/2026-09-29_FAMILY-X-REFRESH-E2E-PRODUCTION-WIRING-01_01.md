## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase A=Existing Spec/Repo 確認・対応表・実装設計・費用概算のみ、委任 _01)。一時ファイル `docs/pm/ACTIVE_TASK_RF1.md` / `docs/pm/RESULT_PACKET_RF1.md`(commitしない)。並行Agentなし。本タスクの所有: 新規 `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md`、delegation_log。**Phase A ではコード・Prompt・SSOT・Master Store・出力ディレクトリを一切変更しない(設計書のみ)。API 支出 上限¥0(LLM/TTS/ASR 禁止)。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。**

## 性質/到達上限Status

- 性質: Production Wiring の Phase A(設計)。新しい Trial・新しい仕様は作らない(ユーザー承認済み仕様の配線計画のみ)。到達上限 Status: 変更なし。
- STOP 条件(該当したら設計書に明記して報告、実装案を勝手に作らない): 承認済み仕様同士の矛盾/新しい Product 判断が必要/未承認 Prompt 変更が必要/既存 Production 機構では新構造を安全に実現できない/Hormuz・Meta の再利用すべき日本語 R2 が一意に特定できない/Standard・Advanced に意図しない非対称/共有 TTS 層への新しい意味変更が必要/予算 Guardrail 超過見込み。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(Grep→該当範囲 Read。SSOT 全文 Read 禁止。全文 Read は設計書類のみ可)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_01.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## ユーザー指示(原文要旨、設計書 §0 に逐語転記すること)

目的: 直近で正式採用した Family X の記事構造・Key Phrase・音声仕様を、Trial 用 script の寄せ集めではなく Production 正式経路へすべて配線し、その正式経路だけで Hormuz/Meta の 2 記事を完成音声まで E2E 再構築する。新しい改善 Trial ではない。
最初に: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT/Production code を確認し、各仕様について「既に PRODUCTION_WIRED/APPROVED_FOR_PRODUCTION だが未配線/旧仕様が残存/Trial 専用 script にしか存在しない」の対応表を作る。Standard/Advanced 共通仕様なのに片方だけに反映されている非対称を確認。
1. 記事入力: Hormuz/Meta の既存 AN3-T0 最終 R2 を再利用(再生成しない)。使用前に「正しい AN3-T0 成果物か/R1/R2 reminder なしで生成された Trial-02 条件と整合するか/Fact Check 済みの最終 R2 か/artifact・hash・由来が特定できるか」を確認。特定不能なら代替生成せず STOP 報告。
2. 新記事構造(APPROVED_FOR_PRODUCTION): 途中 Heading 廃止/完成 JA R2 を忠実英訳(再構成・脚色なし、段落構造維持)/英訳後に本文を書き換えず自然な段落境界で body1/2/3 へ 3 分割(均等化のための書き換え禁止)/完成音声構造 Comment1→body1→Comment2→body2→Comment3→body3→Comment4→In One Line/既存 Heading Readout を撤去/In One Line は短い自然な一文(Trial の語数目標をそのまま絶対上限にしない)/既存の Deviation Check→MAJOR 時 must-fix retry 1 回を維持(新設ではない)。
3. OPEN-228: 新構造配線完了時点で旧 Heading 依存 split・intro 2 paragraph 前提・旧 structure gate/retry を確認し、不要になったものを撤去・置換 → OPEN-228=CLOSED/SUPERSEDED(履歴は残す)。OPEN-230 の must-fix retry 論点も整合。
4. AN3-T0: AN3 は Original 側のみ、reminder は削除済み。normal R1/R2・Fact Check must-fix・symbol must-fix・fallback のどこにも復活していないことを再確認。E2E 完走後に Gate 3 を満たせば PRODUCTION_WIRED 判定対象。
5. Advanced Key Phrase 英語解説: text 仕様=既承認、Audio Style=**Trial-04 Variant B**(`clear, precise, at a measured pace, without dragging`)、APPROVED_FOR_PRODUCTION。Trial script に依存せず Production 正式 Key Phrase 経路へ配線。Standard/Advanced の対象範囲を確認し、レベル固有でない部分に非対称を作らない。
6. 固定フレーズ Master Champion(10 phrase 決定済み): welcome=A、preview_intro=C、key_phrases_intro=C、full_story_intro=C、num_one=C、num_two=B、num_three=B/take1、num_four=C、num_five=B/take1、point_explanation=B。Three/Five の take1 は ASR 合格素材。再 Trial しない。Production Master Store へ正式登録し Standard/Advanced 双方の正式経路で使用。model/voice 不変(Flash-Lite/Charon 系統)。
7. Variable Role Style: JA=J3(逐語「落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてください。」)、EN=E2(Trial の Role 別 E2 逐語)。APPROVED_FOR_PRODUCTION。**Japanese Title も J3 系統へ統一**(Trial 設計漏れ、追加 Trial 不要。Japanese Title だけ旧長文 JAPANESE_STYLE_PREFIX を残さない)。
8. Standard/Advanced 整合: 6-role 英語 Style は共通/Standard 固有の slower instruction・6% slowdown は維持/固定 Master は両レベル共通/新記事構造・Heading 廃止も両レベル共通/Full Story E2 は part1/2/3 すべて同じ Role 解決/retry・fallback・Local Rewrite でも Role Style が矛盾しない。J3 は日本語 segment の仕様であり、Advanced に同じ日本語 segment が無ければ無理に適用しない。
9. Opus L2 指摘の是正(既報 MAJOR): runtime evidence(TOPIC_INTRO/FULL_STORY/IN_ONE_LINE 等の実 style 文字列・model_id・voice を Production 経路で記録、Advanced 英語経路含む)/cache(可変 Role Style の version を使い、現行正式 Style と cache 生成時 Style が不一致なら reuse しない。共有層を不必要に変更しない)/Japanese Title の J3 統一。
10. E2E: すべて配線後、Hormuz/Meta を Production 正式 path だけで完成音声まで生成。Trial output を完成品としてコピーしない。正式に再利用可能なものは reuse 可(source hash/model/voice/Style version/Master version/canonical text が現行正式仕様と一致することを確認)。
11. 完成確認: 両記事・両レベルで 記事/Preview/Comment1〜4/body1/2/3/In One Line/Key Phrase/Advanced 英語解説/固定 Master phrase/Japanese Title/TTS/retry・fallback/Assembly/Audio Validation/player・試聴ページ。完成 Podcast として Standard/Advanced の完成版を試聴可能にする。
12. Cost 管理: A. 開発・検証の一回限り費用(Wiring 確認 TTS、runtime evidence、regression、E2E 検証再生成)と B. Production 量産時の継続コスト(1 記事あたり追加 API call、retry 増、Validator 追加 call、TTS call 増減)を分離して報告。E2E 前に概算、完了後に実測。
13. Production Wiring Gate(すべて満たすまで PRODUCTION_WIRED としない): 初回 path/retry/fallback/regeneration/Local Rewrite/cache/Master Store/Standard・Advanced 整合/runtime evidence/actual model・voice・Style/Regression・integration test/Hormuz・Meta の E2E 実発火/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/commit・push/OPEN-228 close/approved 仕様と実挙動の一致。
14. STOP 条件: 上記「性質」欄。技術的に一意に直せる実装不備は既存承認仕様に沿って是正してよい。
Closeout: 1 各採用仕様の APPROVED→WIRED 状況 2 Hormuz/Meta×Standard/Advanced 完成状況 3 再利用/新規 artifact 4 runtime evidence 5 regression/integration 6 一回限り費用 7 量産コスト増減 8 CLOSED した Open Item 9 残存 USER_DECISION_REQUIRED 10 残存 APPROVED but not WIRED。新たな USER_DECISION_REQUIRED が生じたら次へ進まず STOP。

## Phase A の成果物(設計書、全て根拠ファイル・行付き)

§1 **対応表**: 上記 2〜9 の各仕様(+AN3-T0、KP 4+1、Flash-Lite backend の既定/明示条件、Pronunciation 等の関連既配線)について「Status(PRODUCTION_WIRED/APPROVED 未配線/旧仕様残存/Trial script のみ)」「現在の所在(Production file:行 or Trial script)」「配線先(Production file/関数)」「Standard/Advanced の対称性」「Opus L2 必要性(共有層か)」を表にする。Grep 先: `CURRENT_SPEC.md`(`Family X|Heading|Section Segmentation|In One Line|Key Phrase|Role Style|固定|shared narration|Master|AN3|Flash-Lite|backend`)、`OPEN_ITEMS.md`(`OPEN-201|OPEN-221|OPEN-222|OPEN-223|OPEN-226|OPEN-228|OPEN-229|OPEN-230`)、`docs/pm/REPORT_LEDGER.md`(直近 15 行)、Production: `er019_family_x_entertainment_production_runner_01.py`、`er019_family_x_audio_production_runner_01.py`、`er012_e_family_entertainment_two_level_runner_01.py`、`er003_v1_n3_01_advanced_adaptation_generate.py`、`er003_v1_n3_01_scaffold_generate.py`(`split_article_text`)、`er003_v1_n3_01_assemble.py`、`er006_audio_cost_pilot_02_shared_narration.py`、`er006_master_audio_store_01.py`、`er033_tts_flash_lite_family_x_styles_01.py`、`er003_b1_p9a_audio.py`、KP 経路(`er003_key_words_min_unit*`、`er030_*` KP backend、Advanced KP 音声生成箇所 Grep `kp_english|kp_japanese|japanese_gloss|KEY_PHRASE`)、Trial: `er045_*`(忠実英訳 Prompt/決定論 3 分割/In One Line v2 Prompt)、`er046_*`(Variant B style)、`er043_*`/`er047_*`(Champion 音声・metadata)、`er044_*`(J3/E2)、`er041_*`(KP 解説 text 生成)。
§2 **記事入力の特定**: Hormuz/Meta の「AN3-T0 最終 R2」候補を列挙(`er039_output/.../cells/AN3-T0_ja*`、`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/`、その他)。各候補について: 生成時の R1/R2 指示に reminder が含まれていたか(生成時 commit・runtime_evidence の sha キー有無・`REVISION_INSTRUCTIONS` 逐語で判定。**注意**: `an3_t0_wiring_regression_01` は Phase B 時点=reminder あり構成で生成されている可能性が高い)、Fact Check(must-fix)を通過した最終 R2 か、sha256、由来 commit。**「Trial-02 条件(AN3 は Original のみ、R1/R2 は既存指示のみ)かつ Fact Check 済み最終 R2」を満たす候補が一意に存在するか**を判定。存在しなければ STOP 候補として明記(代替案は列挙のみ、実施しない)。
§3 **実装設計(最小 diff、逐語)**: (a) 新記事構造: Advanced 化 Prompt の「見出し生成・再構成・In One Line」指示の扱い(既存 Prompt 定数をどう置き換えるか。er045 の Trial Prompt を Production 定数へ移設する案、`ADVANCED_VOCAB_RULE_V2_BLOCK` 等の既存ブロック維持)、決定論 3 分割関数の Production 化(`split_article_text` の置換/新関数)、In One Line の Production Prompt(語数の絶対上限は設けない、簡潔化方針を文言化)、Assembly の構造変更(Heading Readout 撤去、Comment 配置)、Audio Validation Gate の parts 定義変更、OPEN-228 の旧 gate 撤去箇所。Standard(A2)側の構造(A2 は英語本文をどう生成しているか=crosslevel/repro01 経路)も同様に変更が必要かを確認(両レベル共通)。 (b) KP 英語解説: text 生成(er041 の Prompt)を Production KP 経路(canonicalization/4+1 schema 後、Advanced のみ?)へ組み込む位置、音声(Variant B style、Role `KEY_PHRASE_EXPLANATION_EN`)、Assembly での配置(Phrase EN → 解説 EN → JA 意味? の順序は既存 CURRENT_SPEC の Advanced KP 構造を確認し、無ければ STOP 候補=Product 判断)。 (c) 固定 Master 登録: Champion 音声(er043/er047 出力 wav、sha256)を Production Master Store へ登録する手順(`register`/`EQUALITY_FIELDS`、`style_instruction_id/version` を Champion 用に bump、旧 Master の扱い=残置で reuse されない key)、両レベルの shell 解決関数が新 Master を選ぶこと。 (d) Role Style: japanese_title へ J3、cache version guard(`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`)、runtime evidence(Advanced 英語経路 3 ファイルへの `style_prefix` 追加、既定時ラベル化)。 (e) AN3 reminder 不在の再確認手順(Grep+テスト)。 (f) 各変更の影響ファイル一覧と、並列実装のためのファイル所有分割案(衝突しない単位、依存順序)。
§4 **Regression/integration 計画**: 既存テストへの影響(er003 系 assemble/scaffold テスト、er019/er033/er038/er044、Section Segmentation 関連)、新規 integration test(新構造 assembly、Master 選択、Style version guard)。
§5 **E2E 計画と費用概算(A/B 分離)**: Hormuz/Meta × Standard/Advanced の生成段階(JA 再利用、英訳、Comment=既存 reuse か再生成か、KP、TTS segment 数、ASR、Assembly)、reuse 可能 artifact の条件確認方法、TTS call 数と概算費用(直近実測: Task B Advanced 19 segment ≈¥30、Task 3 24 segment ¥20.7、Trial-02 text ¥16.9/8 セル を根拠に)。**A. 一回限り費用**(Wiring 確認・runtime evidence・regression・E2E 再生成)と **B. 量産時の 1 記事あたり増減**(KP 解説 text 1 call+音声 5 segment 増、Heading Readout 撤去による TTS 減、Master reuse による固定 phrase 0 call、must-fix retry は既存)を表で概算。Guardrail 案(段階別)。
§6 **Gate 13 項目の証拠計画**と **STOP 該当有無**(§2 の R2 特定を含む)。
§7 SSOT 文案の骨子(CURRENT_SPEC 更新箇所一覧、OPEN-228 CLOSED/SUPERSEDED 文案、OPEN-230 整合、REPORT_LEDGER)。

## 事前指定Read一覧

- `CURRENT_SPEC.md`: 上記 Grep → 該当行範囲のみ
- `docs/pm/design_family_x_no_heading_segmentation_trial_01.md`、`docs/pm/design_tts_variable_role_style_production_wiring_01.md`(§7-9)、`docs/pm/design_tts_fixed_shell_master_champion_trial_02.md`、`docs/pm/design_key_phrase_advanced_english_explanation_audio_style_trial_04.md`(全文可)
- `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md` §Opus L2 所見(MAJOR-1/2/3、MINOR-A/C)
- `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md` §16(reminder 削除)
- Production/Trial script: 上記 §1 の Grep

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。追記位置: 設計書(新規)。更新位置: なし。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_01.md_check.json`
- 候補 R2 の sha256: `certutil -hashfile <path> SHA256`(または Python)
- `git status --porcelain -- "er0*.py" CURRENT_SPEC.md`(本タスク由来の差分なし)

## SSOT追記文

設計書 §7 に骨子のみ。

## Git

- add対象(path指定のみ): 設計書、delegation_log+`_check.json`。SSOT編集権なし。
- メッセージ: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01: Phase A(既存仕様対応表・記事入力特定・実装設計・E2E費用概算A/B)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_RF1 + handback、目安40行)

対応表の要約(仕様ごとの Status と非対称の有無)/記事入力の特定結果(一意に特定できたか、STOP 該当か)/実装設計の要点と並列分割案/Regression 計画/E2E 費用概算(A/B 分離、Guardrail 案)/STOP 該当有無と Fable・ユーザー確認事項/commit hash・raw URL。
