# TEST_PLAN_01(Part 2 Production化 受入条件10項目 × test / evidence 対応)

管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01 / 日付: 2026-10-25。実施済み=委任_01(module、API 0)。未実施=次委任(runner hook+文法HR+evidence)。

## 1. 受入条件10項目の対応
| # | 受入条件 | 委任_01で実施済み(module単位) | 次委任で実施(配線・runtime) |
|---|---|---|---|
| 1 | 正式初回経路に存在 | `EXISTING_SPEC_CHECK_01.md` §3(X/Z/Yの経路・配置位置を特定)。moduleはFamily非依存(`test_P2`)。`test_P3`=現時点で未配線を固定 | Z: 新stage`part2_b1b`(`ensure_stage`)+`stage_pages`描画。X: scaffold b1b内+再実行stage+`tts/assemble/player`入口。静的test: 両runnerが`er120`を呼ぶ・A/B/C/Yは呼ばない(`test_P3`を「配線済み」assertに置換) |
| 2 | retry/fallback/regeneration/resume整合 | `test_D2`(resume API 0)・`D3`(本文変更で再抽出)・`D4`(Human選択変更で解説のみ再生成)・`D8`(retry上限=初回+1、なお不正でSTOP)・`D9`(parse不能を0件にしない)・`D10`(Step B構造不正STOP)・`D11`(model不一致はretryなしSTOP)・`D13`(予算guardでAPI前停止)・`D14`(T1失敗はfail-closed) | Z: `--regenerate-stage part2_b1b`・`DEPENDENTS` `r2`従属・ProvenanceMismatch STOPの次コマンド表示。X: 署名不一致の自動再生成・専用marker・`rc`。外側retry(KP)から独立していることの統合test。copy-run(複製run)でreuse |
| 3 | HR候補提示→操作→反映 | `test_C1〜C10`(順位・TOP1/TOP2・auto/wait・top1/top2/reselect/omit・stale review拒否・0件・再選定API 0・ID安定)・`D5`(PENDING_REVIEWで有料downstream 0)・`D4` | er119 `kind="grammar"`に`review_request`を渡す→CLI操作(`top1/top2/reselect/omit`・`--accept-ai`)→`grammar_human_review.json`→再実行で選定反映。未レビュー=UNREVIEWED_AUTO_ADOPTED。Human修正内容・理由の`history`記録(KP HR evidence R1〜R4と同一runで取得) |
| 4 | 後続の解説/音声/組立への反映 | `test_E3`(`require_fresh_part2`が欠落・改変・古いを拒否)・`E4`(markdown/HTML規約)・`E5`(保存・再読込でAPI 0) | 選定→解説→訳→`part2_result.json`→`study_text/`→Z`index.html`/X`player.html`・公開ページ共通builder(Part 1ブロック直後)。Part 2は音声に影響しない(TTS入力に含めない)ことの確認。`check_page`・`_INTERNAL_RE`非該当・`study_html`未指定時のバイト同一(従来ページ) |
| 5 | Regression/Validator/Integration PASS | module test 77 PASS(A=Trial同一性7、B=29標本回帰、C=選定/HR 10、D=LLM mock 14、E=検証/描画8、P=境界5)。**変異検査**: `select_tiered`の順位反転で`test_B2`がFAILすることを確認 | `run_project_regression.py`全体(自分起因failed=0)、`er006`/`er054`(`LATER_APPROVED_PRODUCTION_KEYS`)/`er009…open251`/`er053`の列挙testへの影響、Z/X統合test(mock mode)、A/B/C非適用test |
| 6 | 正式runtime発火証拠 | (なし。委任_01はAPI 0・runner起動0) | X/Z各1 run以上、正式CLI(Z `--stage`、X `--stage study_text`/scaffold)。HRなし(auto宣言)/あり(top2選択)の両方。実response_id・usage・cost。`EVIDENCE_01.md`へ |
| 7 | actual model_id/routing/Prompt確認 | `test_A1〜A3`(Prompt shaをTrial有料呼出と一致)・`D1`(auditにmodel・process・template sha)・`P1`(routing未登録はfail-closed)・`P5`(MODEL=gpt-6-luna) | `er006`へ2 process登録後、実runの`audit.extract.model`/`explain.model`==`gpt-6-luna`(応答のmodel_id)、`prompt_sha256`==固定値(`51912fe1…`/`59588b59…`)、`cost_log`のstageタグ(`part2_*`) |
| 8 | SSOT更新 | OPEN新規登録(Status=APPROVED_FOR_PRODUCTION・IMPLEMENTING、X/Y/Z別到達状況)・OPEN-497/484追記・DECISION_LOG正式採用1件 | 配線完了時: OPEN更新(PRODUCTION_WIRED化、runtime evidence後のみ)・`CURRENT_SPEC.md`にPart 2節・`DESIGN_04.md §1`/`ADOPTION_NOTE_08.md §3`へ配線済み追記 |
| 9 | Git | 対象pathのみcommit→push | 同様 |
| 10 | Fable独立照合 | `OPUS_REVIEW_REQUEST_01.md`(O-1〜O-6)を提出。Fableが照合 | 配線後のFable受入(DQI) |

## 2. 委任_01で追加した回帰fixtureの要点
- 29標本(Trial-07の18+Trial-08の11)のLLM raw応答(`_raw_07_*`/`_raw_08_*`)を固定入力とし、本moduleの`parse_candidates`→`select_tiered`が、Trial-08の保存結果(`reselect_08.json`/`OUTPUT_08_*`)と**選定・tier・Tier表・features**で一致することを確認(`test_B2`)。代表8作品の結果表(倒置選定=8作品中1: 賢者のみ)も固定(`test_B3`)。
- API 0の証明: 全testで実client生成(`b1s.get_client`)をblockするautouse fixture(呼ばれたら失敗)。LLMは全て`call_fn` mock(呼出回数をカウント: 初回3、resume 0、PENDING 1、ZERO 1等をassert)。有料呼出0。
- 次委任で追加する予定のtest: Z/X統合(mock mode)、HR CLI往復、`require_fresh_part2`の使う側確認(TTS/Gate/Assembly/pages/player各入口)、実run artifactの再parse(evidence run出力をfixture化)。

## 3. evidence計画(次委任)
| 項目 | 内容 |
|---|---|
| 対象 | X 1 run以上 + Z 1 run以上(完成済みrun artifactの複製を正式CLIで実行。新規記事生成・TTSなし) |
| 条件 | (a)HRなし=auto宣言でTOP1自動採用 (b)HRあり=TOP2選択(または再選定) |
| 費用節約 | KP HR evidence R1〜R4と**同一run**で取得(同じ複製runでKP HR操作+文法HR操作)。Part 2の追加は1 runあたり0.43〜0.54円 |
| 取得物 | `grammar_candidates.json`(TOP1/TOP2・tier表)、`part2_result.json`(audit: model・prompt sha・response_id・usage・cost)、`grammar_human_review.json`、描画後ページ(Part 1直後)、resume再実行のAPI 0確認、本文変更→再抽出の確認 |
