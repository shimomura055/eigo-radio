管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01(Part 2「Grammar & Sentence Structure」+Trial-08選定方式のProduction module化。**API 0・Production run実行0・runner無改変**)。親案件: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01(別agentが同時進行中、§4参照)。

## 0. ユーザー正式決定(2026-10-25、本委任の根拠)
ユーザーは次の4項目を**Family X/Y/Z共通仕様として正式採用(APPROVED_FOR_PRODUCTION)**した: ①Part 2文法・構文解説(Trial-07で検証した機能: 本文から学習価値のある構文を選定、逐語一致英文を引用、仕組み/通常語順との比較/意味・ニュアンスを解説、適格0件は0件許容、既存承認済み品質条件維持)、②Trial-08構文選定方式(Tier1=倒置以外の適格、Tier2=倒置、Tier3=なし。Tier内順位の追加改善・HIGH判定安定化・OTHER分類拡張は**承認対象外**)、③KP Human Review、④文法Human Review(AIがTOP1/TOP2を順位付き提示、HumanはTOP1/TOP2/再選定/省略、Human不介入時はTOP1自動採用の既存承認条件維持、未レビューを勝手に最終承認扱いしない)。方針: 既知の品質課題(走れメロス等)を理由にWiringを延期しない/追加Trial・未承認基準変更を前提にしない/既存仕様から逸脱する明確な不具合は委任範囲内で修正/Human Reviewの修正内容・理由を改善に使える形で記録/X・Zは全機能PRODUCTION_WIRED目標、Yは正式経路の有無を確認し安全に配線できる部分は並行、未配線はOPEN_ITEMSへ理由・依存・解消条件を登録(runtime evidenceなしにPRODUCTION_WIREDと言わない)/並列化最大化・不要な待機・日付分割禁止/量産単価70円目標・Part 2増分推定0.41円/セット・HR込み量産費用は実測報告/受入条件10項目(正式初回経路に存在・retry/fallback/regeneration/resume整合・HR候補提示→操作→反映・後続の解説/音声/組立への反映・Regression/Validator/Integration PASS・正式runtime発火証拠・actual model_id/routing/Prompt確認・SSOT更新・Git・Fable独立照合)。

**最初に**ユーザー指示原文を逐語保存: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` のuser行(末尾付近、`queue-operation`内の場合あり)で「Family XYZ共通：Part 2文法解説・Key Phrase／文法Human Review 正式Production Wiring」を含む行を特定し、`<pasted_content>`ラッパーごと無改変で `docs/pm/delegation_log/2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md` へ保存(既存ツール `docs/pm/tools/extract_delegation_from_jsonl_01.py` が使えなければ短い読出scriptをscratchpadに書く)。

## 1. 読むもの
- `docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(新節を追記、他節を消さない)
- Trial正本: `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{DESIGN_07*,PREREGISTERED_CRITERIA_07*,EVAL_07B,PART2_TRIAL07_RESULTS_01,DESIGN_08,PREREGISTERED_CRITERIA_08,EVAL_08,ADOPTION_NOTE_08,PART2_TRIAL08_RESULTS_01}.md`、`run_trial_08.py`、`analyze_08.py`、`test_trial_08.py`、Trial-07のStep A''/Step B runner・Prompt(同dir内をGlobで特定)、翻訳T1 module `er003_kp_source_sentence_ja_01.py`
- Part 1のProduction配線を**参照パターン**として: `er003_kp_general_explanation_01.py`、`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/PART1_WIRING_EVIDENCE_02.md`、X `--stage study_text`(er019 runner)、Z `kp_part1_ja_b1b` stage(er026 runner/er062)、`docs/pm/decisions/part1_translation_decision.json`、study_text/公開ページ描画(5項描画箇所)
- KP HR Phase 0設計(文法層の接続面): `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{DESIGN_01,OPUS_REVIEW_01,DESIGN_02(存在すれば)}.md`(共通核をkind非依存、grammar kind=候補list先頭2件がTOP1/TOP2、Humanなし=TOP1自動採用、0件=省略)
- routing契約(SUPPORT_MODEL等)、`CURRENT_SPEC.md`はGrepのみ(Part 1/Part 2/study_text/Key Phrase周辺)、OPEN-497/484/512/518

## 2. Scope(本委任)
A. **既存仕様確認 `EXISTING_SPEC_CHECK_01.md`**: Trial-07/08の正式規則(Step A''抽出Prompt(1文差替え版)・eligible7・select_tiered・Step B解説Prompt・T1訳・最大1件/0件許容・逐語一致検査・基礎構文除外)を「承認済み仕様」として逐語で固定(Prompt sha記録)。**対象レベルの確定**: Trial-07/08がどのレベル本文(Advanced/Standard)を使ったかを事実で確認し、Production適用レベルはTrial条件と同一とする(Part 1はAdvのみ承認。Trialと異なるレベルへ広げるのは新仕様=行わない、報告に明記)。X/Z/Yの正式初回経路・後続経路(retry/regenerate/resume/copy-run)と、Part 2を置くべき位置(本文確定後・KP非依存か)を特定。Yは正式Production入口の有無(OPEN-484)を確認し「安全に配線できる部分」を列挙。
B. **設計 `DESIGN_01.md`+`OPUS_REVIEW_REQUEST_01.md`**(条件A: 新しい処理フローのProduction導入): Production module(新規、予定名 `er120_part2_grammar_production_01.py`、衝突確認)のI/F=入力(レベル本文・段落列・作品メタ)→候補抽出(Step A''、既存外側retry/stop_check/予算guard整合)→適格判定・Tier順位付け(select_tiered移植、決定論)→`grammar_candidates.json`(順位付きlist、TOP1/TOP2+残り、各候補に段落番号・逐語span・分類・teaching_value・理由)→**文法HR接続点**(er119共通核のkind="grammar"へ渡すI/F。本委任ではHR側を実装しない。Humanなし時はTOP1自動採用、0件=省略文面)→確定後Step B解説生成+T1訳→`part2_result.json`→study_text/公開ページ描画(Part 1ブロックの直後、既存描画規約に合わせる)。retry/regeneration/resumeとの整合、再利用キー、失敗時のfail-closed(解説欠落のまま公開しない)、Dangling Reference禁止(Trial専用pathをProductionから参照しない)、費用見積(0.41円/セット+HR確定後の再生成分)、actual model_id/routing記録。Opus論点を列挙(O-1 Trial規則の移植忠実性 O-2 HR接続面 O-3 retry/resume/regenerate O-4 描画・組立・一致検証 O-5 レベル・Family適用範囲 O-6 Yの到達性)。
C. **実装(新規ファイルのみ)**: module本体+Prompt(sha固定)+単体test(fixture。Trial-07/08の8作品既存出力を回帰fixtureに使い、select_tieredの選定がTrial-08結果と一致することを固定。LLM mockでAPI 0をカウンタ証明)。**runner(er019/er026/er062)・er119・公開ページは本委任で変更しない**(§4)。
D. **TEST_PLAN_01.md / BUDGET_PLAN_01.md**: 受入条件10項目×test/evidence対応、evidence計画(X/Z各1 run以上、正式経路、HRあり/なし。KP HR evidence R1〜R4と同一runで取る案を優先=費用節約)、見積。
E. SSOT: OPEN新規登録(11-8分類必須。Status=APPROVED_FOR_PRODUCTION・IMPLEMENTING、X/Y/Z別の到達状況欄)、OPEN-497へ「①②正式採用 2026-10-25」追記、OPEN-484へ文法/Part 2のY要件追記。**OPEN_ITEMS.md編集は直前に再Read・最小Edit・バックアップ**(別agentも編集中)。DECISION_LOGに正式採用エントリ1件(ユーザー決定の逐語要点)。CURRENT_SPECは変更しない(PRODUCTION_WIRED時)。
F. Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push。競合は両方残しSTOP報告)。`git add -A/-u`・amend・rebase・force・stash・reset --hard禁止。commit前に`git status --porcelain`で意図外混入なし確認、secret grep 0件。
G. 委任文逐語保存: 上記ツールで `--role assistant --tool-use-name Agent --tool-input-field prompt --index N`(Nは573前後、先頭「管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01」を570〜585で走査)→ `docs/pm/delegation_log/2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_DELEGATION_01.md`。

## 3. 禁止
- 有料API呼出0(LLM/TTS/ASR/Azure)。`.venv`不使用、`py`のみ。Production runner起動0。
- Tier内順位改善・HIGH判定安定化・OTHER分類拡張・Prompt改良(承認対象外)。Trial-07/08の規則を変えない(明確な不具合=仕様逸脱のみ修正し、理由を記録)。
- 新しい運用仕様の独断追加。Family Yの正式Production入口の新設。
- `er0XX_output/`既存成果物・`user_test/`の変更。

## 4. 並行agentとの競合回避(重要)
別agent(KP HR 委任_02)が `er119_kp_human_review_01.py`(新規)、`er019_family_x_audio_production_runner_01.py`、`er026_family_z_fiction_production_runner_01.py`、`er062_family_z_writer_01.py`、`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/*`、OPEN-518/484を編集中。これらは**読むだけ**。runnerへのPart 2 hook・文法HR接続は次委任(両者完了後)で行う。ACTIVE_TASK/OPEN_ITEMS/DECISION_LOGは直前再Read・最小Edit。

## 5. 報告(RESULT_PACKET_P2W1.md+口頭要約)
- 対象レベル・Family別の正式経路と配線位置(表)、Trial規則の移植忠実性(Prompt sha一致・select_tiered回帰fixture結果)、実装ファイル/関数、test件数・PASS・API 0証明、Opusレビュー依頼文の所在、次委任(runner hook+文法HR+evidence)の作業分解・見積・並列案、Yの到達性と未配線理由、費用0円、commit hash・raw URL。
- RESULT_PACKET 4行((1)既存仕様整合 (2)未承認機能の既定値 (3)失敗終了時の最終成果物 (4)撤去・残置)+判定整合。判断候補はFable/ユーザーを27-3で仕分け(推測で進めない)。