## 管理ID

FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01(Phase A=Existing Spec/Repo 確認・設計・費用概算のみ、委任 _01)。一時ファイル `docs/pm/ACTIVE_TASK_FZ1.md` / `docs/pm/RESULT_PACKET_FZ1.md`(commitしない)。並行: 別Sonnet 1件(`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01` Phase A、設計書 `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md` を作成中、読み取り可・編集不可)→ 触れない。本タスクの所有: 新規 `docs/pm/design_family_z_melos_production_e2e_and_latest_spec_wiring_01.md`、delegation_log。**Phase A ではコード・Prompt・SSOT・Master Store・出力ディレクトリを一切変更しない(設計書のみ)。API 支出 上限¥0。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。**

## 性質/到達上限Status

- 性質: Family Z Production Wiring の Phase A(設計)。ユーザー判断: Family Z へ今回の共通仕様を正式反映/Family Z の Production 配線も今回完成/3 分割構造も Production へ/3 分割の出来は完成版 Melos をユーザーが試聴して確認/追加の構造 Trial は挟まない。対象仕様は `APPROVED_FOR_PRODUCTION` として扱う。Phase A 完了時点では Status 変更なし。
- 依存関係: 共通層(固定 Master Champion の Production Master Store 登録、J3/E2 定数、3 分割 Contract の Production 実装、Japanese Title J3、cache version、runtime evidence)は `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01` で先に配線される予定。本設計書では「REFRESH-01 の成果を reuse する箇所」と「Family Z 固有に実装する箇所」を明確に分ける(共通層を二重実装しない)。
- STOP 条件(該当したら設計書に明記して報告、代替案は列挙のみ): Melos 既存 article を正式 artifact として再利用できない/3 分割で Story の意味・Dialogue 構造を安全に維持できない/Family X 仕様を Family Z へ適用すると既存 Family Z 正式仕様と矛盾/新しい Voice・Style・Product 仕様の採用判断が必要/未承認 Prompt 変更が必要/Production 共通層へ重大な意味変更が必要/予算 Guardrail 超過見込み。既存承認仕様から一意に決まる実装上の是正は進めてよい。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(SSOT 全文 Read 禁止、Grep→該当範囲)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01_01.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## ユーザー指示(原文要旨、設計書 §0 に逐語転記)

目的: Family Z の既存「走れメロス」記事を再利用し、Family X で正式採用した記事構造・音声仕様のうち Family 共通として使えるものを Family Z にも正式採用・Production 配線し、Melos を Family Z 最初の正式な完成 E2E として Production 正式経路だけで完成音声・試聴まで通す。
1. Existing Spec/Repo 確認: Family Z 専用 runner/既存 Melos Production artifact(`er026_output/family_z_production_e2e_01/melos/run_01/`)/article.md/story_type・rights block/Preview/Comment/In One Line/Key Phrase/segment plan/Family C 由来 Dialogue Voice 機構/pronunciation resolver/TTS symbol normalization/retry・fallback・Local Rewrite/Connected Speech。実装済みは作り直さない。canonical article は再利用。
2. Melos 本文: 既存 article.md を再利用(再生成禁止)。再利用前に「正式 Family Z 生成物か/story_type=literature と整合/rights 記録の存在/承認済み Family Z Story 仕様に反していないか/artifact hash・由来」を確認。Story 本文に新たな Product 判断が必要な問題のみ STOP。
3. 正式記事構造: Comment1→body1→Comment2→body2→Comment3→body3→Comment4→In One Line。分割ルール: canonical text を書き換えない/自然な段落・場面・意味の切れ目/可能な範囲で均す/会話・Dialogue の途中を切らない/因果・緊張感・progression を壊さない/Heading 新設で 3 分割を表現しない。News 用ロジックのコピーではなく同じ 3 分割 Contract を Story に適用。
4. Comment 1〜4: 役割共通化(1=入口、2=body1→2 Bridge、3=body2→3 Bridge、4=全体を軽く回収し In One Line へ)。Story 先取り禁止/再説明しすぎない/ネタバレ禁止/没入感を壊さない/内部用語(body1 等)を口にしない。既存 Family Z/Family C Prompt を最大限 reuse、最小限の Family Z 適応のみ。
5. In One Line: 既存 Family Z 承認どおり既存機構を Fiction 向けに最小変更で reuse。短い・自然な一文・詰め込みすぎない。Story の核心を短く回収。
6. Dialogue Voice: 既承認仕様維持(単一 canonical text、Voice ごとに複製しない、Dialogue のみ Family C 由来 speaker/voice assignment、narrator/dialogue 切替)。3 分割後も Quote 境界・speaker 判定・Voice assignment・body 境界をまたぐ Dialogue が壊れないことをテスト。分割位置が Dialogue 途中に入らないこと。
7. 音声仕様の展開: 固定 Master=最新 Champion(welcome=A/preview_intro=C/key_phrases_intro=C/full_story_intro=C/num_one=C/num_two=B/num_three=B take1/num_four=C/num_five=B take1/point_explanation=B)を共通 Master から必要なものだけ reuse(使わない phrase を無理に追加しない)。Variable Role Style: 同じ Role・同じ言語には正式採用品を reuse(JA=J3、EN TOPIC_INTRO/FULL_STORY/IN_ONE_LINE=E2)。Preview/Comment 等は既存 Family Z の言語・Voice・Role 構造を確認し News 固有 style を機械的にコピーしない(意味が同じなら reuse、Story 固有演出が必要なら新 style を作らず STOP 報告)。Title: 「Title だけ旧 Style」の再発禁止、周辺 segment との Style 整合を確認。
8. Key Phrase: 既存 Family Z 実装を reuse。既存 Melos KP artifact と最新正式仕様の互換性確認。共通採用済み仕様は適用。再選定不要なら reuse。新候補 Trial を始めない。
9. TTS Production 仕様維持: attempt1→即時 attempt2→10 分 cool-down→attempt3→NG なら Local Rewrite、Natural English QA、pronunciation resolver、symbol normalization、ASR validation、Connected Speech(Full Story/Comment/Preview/Topic intro/In One Line)。Dialogue Voice との整合、retry/fallback で Voice assignment・Role Style が消えないこと。
10. story_type=literature: REAL STORY/TRUE CRIME 表示なし、"This is a true story." 等なし。分岐を壊さない。
11. 正式 runner へ統合(3 分割/Comment/In One Line/KP/Dialogue Voice/共通 Master/共通 Role Style/pronunciation resolver/retry・fallback/Local Rewrite/Assembly/Audio Validation/player)。DEV/Trial script のみに存在する状態は禁止。
12. Melos E2E: 既存 article 入力で正式 path 完走(Story/3 分割/Preview/Comment/In One Line/KP/Dialogue Voice/TTS/retry・fallback evidence/Assembly/Audio Validation/完成音声/試聴ページ)。完成 Podcast として、寸断感・Comment の没入感・Dialogue Voice の自然さ・Style 統一・In One Line への接続を確認できるように。
13. Gate: initial path/retry/fallback/regeneration/Local Rewrite/cache reuse 整合/Dialogue Voice/story_type 分岐/pronunciation resolver/symbol normalization/Connected Speech/Master Store/runtime evidence/actual model・voice・style/integration・regression/Melos E2E 完走/Audio Validation PASS/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/commit・push/Dangling Reference Check。
14. Opus L2: Mandatory(実装後、PRODUCTION_WIRED 判定前に 1 回)。Opus の新 Product 仕様提案は採用しない。
15. Cost: A(一回限り: wiring/runtime evidence/E2E 確認 TTS/regression 用生成)と B(量産継続: 1 記事あたり追加 call、3 分割化による TTS call 差、Comment 増減、Validator/retry の恒常差)を分離。
Closeout 13 項目(設計書 §末尾に証拠計画として列挙)。

## Phase A の成果物(設計書、根拠ファイル・行付き)

§1 **Existing Spec/Repo 対応表**: 上記 1 の各項目について「所在(Production file:関数)/現行仕様(CURRENT_SPEC 該当行)/Melos run_01 の artifact(パス・sha256・生成 commit)/今回の扱い(reuse/変更/新規)」。Grep 先: `CURRENT_SPEC.md`(`Family Z|Melos|メロス|story_type|literature|rights|Dialogue|Family C|Connected Speech|Local Rewrite|cool-down|Natural English QA`)、`OPEN_ITEMS.md`(`Family Z|Melos|Dialogue|OPEN-2[0-3][0-9]`)、`DECISION_LOG.md`(`FAMILY-Z|Melos`)、`docs/pm/REPORT_LEDGER.md`(`FAMILY-Z`)、Production: `er026_*`(Family Z runner、Grep `def |story_type|rights|segment_plan|comment|in_one_line|key_phrase|dialogue|speaker|voice`)、Family C の Dialogue Voice(`er0*` Grep `speaker_assignment|dialogue_voice|quote_boundary`)、`er026_output/family_z_production_e2e_01/melos/run_01/`(Glob、article.md・audit・segment plan・KP・rights)。
§2 **Melos 本文の再利用判定**: 正式生成物か・story_type=literature・rights 記録・承認済み Story 仕様との整合・sha256/由来 commit。問題なければ「再生成禁止・reuse」と結論。STOP 該当なら明記。
§3 **Family Z 構造設計**: (a) 3 分割: REFRESH-01 で Production 化予定の決定論分割(段落境界・長さ均等)を **Story 用 Contract**として適用する設計(Dialogue 途中禁止=Quote 境界/speaker span を分割候補から除外する制約を追加、場面の切れ目を優先する規則を段落メタデータで表現できるか)。Melos の canonical text に対する候補分割点と 3 部の長さ(文字数)を **機械的に試算**(API なし)し、Dialogue を跨がない分割が存在するかを確認(存在しなければ STOP 候補)。(b) Comment 1〜4: 既存 Family Z/Family C の Comment Prompt を Grep し、役割 4 種への最小適応案(逐語 diff、News 固有語の除去、ネタバレ禁止・内部用語禁止の既存有無)。既存 Melos run_01 の Comment artifact が「4 Comment 構造」で使えるか(数・位置・内容)、reuse か再生成かの判定。(c) In One Line: 既存 Family Z 機構の Fiction 向け最小変更案(逐語)。(d) Preview/Title/Topic intro 等の Family Z segment 一覧(言語・Voice・Role)と、J3/E2 の適用可否判定表(同 Role・同言語=reuse、Story 固有演出が必要=STOP 候補として列挙)。(e) 固定 Master: Family Z が使う phrase の一覧(使わない phrase は追加しない)と共通 Master からの reuse 経路。(f) Dialogue Voice: 3 分割後の Quote 境界・speaker 判定・Voice assignment・body 境界跨ぎのテスト設計、retry/fallback/Local Rewrite で Voice assignment・Role Style が保持される経路の確認。(g) Key Phrase: 既存 Melos KP artifact の schema(4+1/`key_phrase_role`/canonicalization/Pronunciation Phase 4)互換性と、Advanced 英語解説(Family X で採用)が Family Z の対象か=CURRENT_SPEC の Family Z KP 仕様を確認(対象外なら適用しない理由を記録、判断が必要なら STOP 候補)。(h) story_type 分岐の維持箇所。(i) Assembly/Audio Validation/player の Family Z 構造対応(Heading なし、Comment 配置)。
§4 **Regression/integration 計画**(Dialogue 境界テスト、story_type 分岐テスト、Dangling Reference Check の対象)。
§5 **E2E 計画と費用概算(A/B 分離)**: reuse artifact(article/KP/既存音声の条件確認方法)、新規生成(Comment 4、In One Line、TTS segment 数[Dialogue Voice 切替を含む]、ASR)、概算費用(直近実測を根拠)と Guardrail 案。B は Family Z 1 記事あたりの増減(3 分割による call 差、Comment 数差、Validator/retry 恒常差)。
§6 **Gate 22 項目の証拠計画**、**Opus L2 論点候補**、**STOP 該当有無**。
§7 SSOT 文案骨子(CURRENT_SPEC Family Z 節更新箇所、DECISION_LOG、OPEN 更新/CLOSE 候補、REPORT_LEDGER)。
§8 REFRESH-01 との依存関係と実装順序(共通層は REFRESH-01 の完了後に Family Z 側で reuse。並列可能な Family Z 固有実装の分割案)。

## 事前指定Read一覧

- `CURRENT_SPEC.md`: 上記 Grep → 該当行範囲のみ
- `er026_*` runner(Grep 上記)、`er026_output/family_z_production_e2e_01/melos/run_01/` 配下(Glob、article.md 全文可)
- Family C Dialogue Voice 実装(Grep で特定)
- `docs/pm/design_family_x_no_heading_segmentation_trial_01.md`(3 分割アルゴリズム)、`docs/pm/design_family_x_refresh_e2e_production_wiring_01.md`(存在すれば、読み取りのみ)
- 直近の Family Z REPORT(`FAMILY-Z-*_REPORT.md` Glob → 最新のものの §構造・Status)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。追記位置: 設計書(新規)。更新位置: なし。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01_01.md_check.json`
- Melos article の sha256(`certutil -hashfile` または Python)
- 3 分割試算: scratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\f1538907-8efe-486d-9790-ef5c6cd789fa\scratchpad\`)の一時スクリプトで段落境界・Quote 境界を機械集計(API なし、リポジトリへ置かない)
- `git status --porcelain -- "er0*.py" CURRENT_SPEC.md`(本タスク由来の差分なし)

## SSOT追記文

設計書 §7 に骨子のみ。

## Git

- add対象(path指定のみ): 設計書、delegation_log+`_check.json`。SSOT編集権なし。
- メッセージ: `FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01: Phase A(Family Z既存仕様対応表・Melos再利用判定・3分割Story Contract設計・Comment/In One Line/Dialogue Voice整合・費用概算A/B)`、trailer `Management-ID: FAMILY-Z-MELOS-PRODUCTION-E2E-AND-LATEST-SPEC-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_FZ1 + handback、目安40行)

対応表の要約/Melos 本文の再利用判定(hash・由来)/3 分割試算結果(Dialogue を跨がない分割の有無、3 部の長さ)/Comment・In One Line・Role Style・Master・KP の設計要点と STOP 候補/Regression 計画/E2E 費用概算(A/B、Guardrail 案)/REFRESH-01 との依存・実装順序/Opus L2 論点/commit hash・raw URL。
