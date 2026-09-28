## 管理ID

EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(Fableからの修正1回目=Opus L3所見反映、ユーザー承認済み。承認済みstrict Tier 1仕様への**適合修正**であり新仕様追加ではない)。一時ファイル `docs/pm/ACTIVE_TASK_ASR4.md` / `docs/pm/RESULT_PACKET_ASR4.md`(commitしない)。並行衝突: 別SonnetがFlash-Lite(`er003_v1_*`、`er006_audio_cost_pilot_02_*`、`er019_*`、`er033_*`、`er003_test_v1_n3_01_tts_generate.py`)、KP 4+1(`er003_key_words_*`、`er030_*`、`er035_*`)、SSOT/PM_GOVERNANCE(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`)を編集中 → **これらは一切編集しない**。本タスクの所有ファイル: `er021_en_asr_semantic_equivalence_production_01.py`、`er006_preprod_hardening_01_validation.py`(:1205-1275の早期exit周辺のみ)、`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`、`er021_output/coverage_review_02/`、`docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`、`EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md`。開始時 `git status --porcelain` で所有ファイルに他Agent差分が無いことを確認、あれば触らず報告してSTOP。SSOT 4点への追記は**文案をRESULT_PACKETへ書くのみ**。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様への適合修正(決定論のみ)。到達上限Status: Sonnetは `PRODUCTION_WIRED` を宣言しない(Gate 3再確認表を報告、判定はFable)。
- 費用: 上限¥0(Guardrail)。追加ASR/LLM/TTS/外部API呼び出しは行わない。必要と判明したら実行せずSTOPして報告。
- 禁止: 受理範囲を広げる追加仕様(拡張が必要になったらSTOP)、`'s` の吸収実装(DEFERRED維持)、Hormuz記事の再生成、`git add -A`、履歴書き換え、APIキー本文の表示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_04.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_04.md --json-out docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_04.md_check.json` を実行、結果1行記録。
T-2: TTS実行なし。
T-3: 費用上限¥0、上記「性質」欄のとおり。

## ユーザー指示(原文)

「2. ASR strict Tier 1実装漏れ修正 承認。進めてください。今回は新仕様追加ではなく、承認済みstrict Tier 1仕様への適合修正として扱ってください。必須: 「差分に句読点atomを含む」条件を正しく実装/not able ↔ notable のようなfalse acceptを防止/DEFERRED扱いの 's が事実上吸収されないこと/否定語保護の二重防御/分かち書き / apostrophe negative test追加/telemetry汚染の隔離/REPORT / SSOT記載是正/既存NEGATIVE fixture全再実行/false accept 0確認。受理範囲を広げる追加仕様は不要です。もし新たに拡張が必要になった場合は勝手に進めずSTOPしてください。」「Flash-Lite / ASRともGate 3完了まではPRODUCTION_WIREDとしないこと。」

## 事前指定Read一覧

- `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md` 末尾「## Opus L3診断所見(逐語、2026-09-28)」(Grep → 末尾まで)。**行番号参照が正**。
- `er021_en_asr_semantic_equivalence_production_01.py`:440-465(literal/roman)、:510-530(`_atom_key`)、:535-580(`_closed_punctuation_diff_ok`、SF-2の恒真assert含む)、:40-60(`TELEMETRY_LOG_PATH`)
- `er006_preprod_hardening_01_validation.py`:670-680(`protected_check` 否定語)、:980-995(`despaced`)、:1205-1275(早期exit・telemetry書込)
- `er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`:534-774(`StrictTier1SynthesisRuleTest`)
- `er021_output/coverage_review_02/` のオフライン再判定script(Glob `*reclassify*.py`)

## 事前指定Grep一覧+追記位置・更新位置の手順

- BLOCKER-1: `_closed_punctuation_diff_ok()` へ「差分op両側のatomのうち、alnum除去後が空のatom(句読点atom)が少なくとも1つ存在する」条件を追加(Opus最小修正案の2行)。あわせてOpus「残存リスク」の追加条件「句読点atomを除いた側のatom数の min が 1」も実装する(承認仕様「句読点のみのlocal差」を閉じる方向の締め=受理範囲を広げない。Hormuz型 `["us"]` vs `["u",".","s","."]` は min(1,2)=1 で通ることをtestで固定)。SF-2: 恒真assertを削除し、実効のある不変条件(非literal atom不在/句読点atom存在)のassertまたは通常の条件式へ置換。
- 否定語二重防御: `er006_preprod_hardening_01_validation.py:1211` 付近で `tier1.get("diff_anchored")` がTrueのときのみ `protected_check(tokenize(canonical_text), tokenize(asr_text)).negation_mismatches` が空であることを追加条件にする(空でなければ早期PASSしない=従来経路へ)。
- SF-4 negative test(Tier1直呼び+`classify_asr_match(..., segment_id="full_story_part1")` 経路の両方): `not able`/`notable`、`a part`/`apart`、`Ottawa's`/`Ottawa s`、`were`/`we're`、`may be`/`maybe`、混在型 `U.S. not able`/`US notable`(いずれもOpus反例の文をそのまま使用)。positive維持test: Hormuz型、`safe. But`/`safe, but`。
- SF-1 telemetry隔離: testで `TELEMETRY_LOG_PATH` を一時ディレクトリへmonkeypatch(全test class共通fixture)。既存の混入分は削除せず、`er021_output/coverage_review_02/telemetry_contamination_note.json` に「test由来混入期間・件数(母数4,187→4,536、protected_number 1,672→1,813)」を記録し、OPEN_ITEMS文案へ「test由来期間」として明記。
- 既存NEGATIVE fixture全再実行: Trial-01 68件+OPEN-123 Regression 57件+新規25件+今回追加分。false accept 0を集計表で報告。
- オフライン再判定の再実行(¥0、決定論): 修正後コードで `er021_output/coverage_review_02/` の再判定scriptを再実行し、reversal 7件が維持されるか(Opus予測: 不変)を確認、結果を `_02_result.json` として保存。
- N-9: `git show 3d9a28be -- er006_preprod_hardening_01_validation.py er021_en_asr_semantic_equivalence_production_01.py` で `_MONTHS`/`_DATE_ORDINAL_RE`/`_ORDINAL_WORDS` の移設前後の集合同一性を確認し1行記録。
- REPORT記載是正: SF-3(「既存合格経路の挙動は完全に同一」→「比較方式は不変、atom化は分類A修正の範囲で変更[ローマ数字安全化は従来PASSの一部を落とす安全方向の変更]」)、SF-5(Gate 3表のruntime evidence行に「新規則の実経路発火は(b)実Production artifact再判定で確認、(c)実TTS+ASR 2 segmentは発火せず」)、`'s` DEFERRED記述の是正(修正後は事実としてDEFERRED)、N-7(offline再判定はfalse reject減少のみ測定可、false accept増加は検出不能)、N-8(insert/delete不吸収・op上限3の実務上の狭さ、「構造的耐性」の過大表現を避ける)。設計書§5(B)-2/§7-5との対応表を追記(N-6)。
- Dangling Reference Check: Grep `_closed_punctuation_diff_ok|diff_anchored|negation_mismatches|TELEMETRY_LOG_PATH` 全体。

## 実行コマンド全文

- `.venv\Scripts\python.exe -m pytest er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py -q`(pytest未導入なら `.venv\Scripts\python.exe -m unittest er021_en_asr_semantic_equivalence_production_wiring_01_test_01 -v`、実行コマンドを逐語記録)
- 既存corpus再実行: Trial-01/OPEN-123 corpusを実行する既存test/scriptを Grep `OPEN-123|trial_01` in `er021_*test*.py` `er021_*.py` で特定し実行(逐語記録)。
- `.venv\Scripts\python.exe run_project_regression.py`(全件1回、既知baseline failed=7/errors=2 と照合)
- オフライン再判定: `er021_output/coverage_review_02/` 内scriptを `.venv\Scripts\python.exe <script> --out er021_output/coverage_review_02/offline_telemetry_reclassify_02_result.json` 相当で再実行(引数は実装に合わせ逐語記録)。

## SSOT追記文

RESULT_PACKETへ文案: CURRENT_SPEC「English ASR Semantic Equivalence Layer」節(修正1回目: 句読点atom必須+min1条件+否定二重防御、`'s` DEFERRED維持、SF-3の書き分け、N-8の実務上の範囲)、DECISION_LOG新規エントリ(ユーザー承認原文要旨、Opus L3 BLOCKER-1と反映、検証結果)、OPEN_ITEMS(OPEN-186追記: 修正1回目; 新規: telemetry test由来混入期間の記録; 新規[任意]: N-10層間不整合 `July thirteenth`↔`July 13` はfalse rejectのみ)、REPORT_LEDGER行更新。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: 所有ファイル+`er021_output/coverage_review_02/` の新規結果+delegation_log+`_check.json`。他Agent差分は一切addしない。
- メッセージ: `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02 修正1回目: Opus L3 BLOCKER-1反映(句読点atom必須+否定二重防御+分かち書き/apostrophe negative+telemetry隔離+記載是正)`、trailer `Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`。`git push origin main`。

## 報告(RESULT_PACKET項目)

T-0結果/所見→対応の照合表(BLOCKER-1、SF-1〜5、N-6/N-7/N-8/N-9)/変更差分要約/negative test結果(各反例ペアの判定)/既存corpus再実行集計(false accept 0)/オフライン再判定 reversal 件数(前後比較)/regression結果/telemetry隔離の確認/Dangling Reference Check/Gate 3再確認表(ユーザー指定9項目)/SSOT文案/STOP・新規USER_DECISION候補(受理範囲拡張が必要になった場合はここでSTOP)/commit hash/raw URL。
