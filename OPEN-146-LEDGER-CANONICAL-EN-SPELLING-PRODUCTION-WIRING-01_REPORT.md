# OPEN-146-LEDGER-CANONICAL-EN-SPELLING-PRODUCTION-WIRING-01 報告書

管理ID: `OPEN-146-LEDGER-CANONICAL-EN-SPELLING-PRODUCTION-WIRING-01`
(A-Family/News Ledger公式英語表記のProduction配線、Sonnet委任初回)。
ユーザー決定2026-09-12「#12 A-Family/News Ledger公式英語表記のProduction
採用⇒採用」(`APPROVED_FOR_PRODUCTION`)に基づく配線実装。**`PRODUCTION_
WIRED`は宣言していない**(Gate 3=`PM_GOVERNANCE.md` L146-152完了まで
未完了、9節参照)。API支出(Web検索/LLM/TTS)は一切行っていない。

## 要点(5行)

1. Failure mode(日本語情報源由来のLedgerの固有名詞をWriterが実行ごとに
   推測でローマ字化する、`FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-
   TRIAL-15`でVALIDATED)への対策を、Trial-15の実証済み方式(既存
   Production関数`build_common_block()`/`COMMON_BLOCK_TEMPLATE`は無改変、
   Ledgerテキスト自体への1文追記)のまま、新規モジュール
   `er011_open146_ledger_canonical_en_spelling_production_01.py`として
   配線した。
2. 3箇所の既存Production関数(`er003_v1_n3_01_articles_generate.py::
   run_theme()`のLedger読込、同ファイル`run_one_pattern()`のFact
   Checker呼び出し、`er002_ja_web_research_r3.py::build_fact_check_
   prompt()`)へ、いずれも**後方互換オプション引数/no-op分岐**として
   配線した。`canonical_en_spelling`行が無い既存Ledger(全既存Production
   Ledgerを含む)では、`build_common_block()`出力・Fact Checkerプロンプト
   出力ともbyte単位で完全に不変であることをテストで確認した。
3. Research/Ledger作成は現状、自動Pythonパイプラインではなく手動作成
   運用(`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01`で
   確認済み)であるため、「自動フック配線」ではなく「Ledger作成時に呼ぶ
   再利用可能な関数群の提供+SOP明記」として実装した。
4. 新規回帰テスト24件(¥0、Web検索/LLMは全てモック)+既存回帰テスト
   `er012_open131_fact_attribution_production_wiring_01_test_01.py`の
   1件を本タスクの変更に合わせて更新、プロジェクト全体回帰
   (`run_project_regression.py`、2346件収集)は既知fail3件
   (`er003_test_p2j_investigate.py`のテスト件数自己集計drift、本タスクと
   無関係)以外全PASS(2343/2346)。
5. realAPI runtime evidence(実News Production run)は未取得(Gate 3
   未完了、新規記事テーマはPM_GOVERNANCE.md 13節によりユーザー選定が
   必要なため本タスクでは生成していない)。既存Production Ledgerへの
   遡及適用は行っていない(`USER_DECISION_REQUIRED`候補、8節)。

---

## 1. 配線図

| 変更対象 | 変更内容 | 既定/非該当時の挙動 |
|---|---|---|
| `er011_open146_ledger_canonical_en_spelling_production_01.py`(新規) | Ledger内`canonical_en_spelling:`行の検出/抽出、Writerへの1文追記(`append_canonical_spelling_instruction_if_present()`)、Fact Checker照合ブロック構築(`build_canonical_spelling_fact_check_block()`)、固有名詞抽出(Web検索なしLLM呼び出し、`make_proper_noun_extraction_fn()`)、公式表記confirmation(既存`r3.make_writer_research_fn()`を無改変で再利用、`run_canonical_spelling_research()`)、Ledger本文への追記(`append_canonical_spelling_section()`)を提供 | 該当行/entities無しでは全関数がno-op(空文字列/空リスト/元テキストそのまま) |
| `er003_v1_n3_01_articles_generate.py::run_theme()` | `verified_ledger_text = load_text(...)`を`canon_spelling.append_canonical_spelling_instruction_if_present(load_text(...))`でラップ | 既存Ledger(該当行無し)ではbyte不変 |
| `er003_v1_n3_01_articles_generate.py::run_one_pattern()` | Fact Checker呼び出し直前で`canon_spelling.build_canonical_spelling_fact_check_block(verified_ledger_text)`を計算し、`r3.build_fact_check_prompt(...)`へ`canonical_spelling_block=`として渡す | 該当行無しでは`""`、Fact Checkerプロンプトはbyte不変 |
| `er002_ja_web_research_r3.py::build_fact_check_prompt()` | 後方互換オプション引数`canonical_spelling_block: str = ""`を追加(OPEN-131`voice_attribution_block`と同型パターン) | 既定""でbyte単位で完全に同一。B-Family等の既存呼び出し元は本引数を渡さないため無影響 |

Gate 4(Dangling Reference Check): `verified_ledger_text`はNews生成
パイプライン内で`run_theme()`の1箇所でのみファイルから読み込まれ、
Local Rewrite・Ledger Deviation Checker・Point Overlap retry・Directional
Fact Precheckはすべて同一変数を引数として受け取るのみで再読込しない
ため、Writer指示追記後のテキストが全工程で一貫する(コード追跡で確認)。
`build_fact_check_prompt()`の全呼び出し元(grep、68ファイル)を確認し、
新規引数追加による位置引数衝突が無いことを確認した(全呼び出しが
keyword引数または3引数のみ)。

## 2. 既存Trial実証根拠との対応(実装の妥当性)

`FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15`が実際に使った
`run_one_pattern_connected()`(Trial harness、無変更のまま使用)は、
本配線が新たに触れた`run_deviation_check()`・Point Overlap
Gate・Fact Checkerの全てを同一のProduction呼び出し列で実行済みであり、
条件F(Ledgerへの追記+同一文言のWriter指示)で最終NG率0%(0/6)・
Ledger Deviation Check起因のNGも無かったことを、新規API呼び出しなしで
根拠として引用した(4-1節)。これにより、本配線が既存retry/fallback/
regeneration機構(Local Rewrite・Point Overlap retry・Ledger Deviation
Checker)を壊さないことは、Trial-15のrealAPI実測で既に裏付けられている
(本タスクで新規に実行したのはオフラインのbyte比較・mock APIテストのみ)。

## 3. テスト結果(実測、¥0)

- 新規`er011_open146_ledger_canonical_en_spelling_production_wiring_01_test_01.py`: **24/24 PASS**(受入基準6-a〜6-eに対応する各クラス、Web検索/LLMはすべて`unittest.mock.MagicMock`または依存性注入)。
  - 6-a(抽出→canonical_en_spelling行生成、モック): `ProperNounExtractionMockedTest`/`CanonicalSpellingResearchMockedTest`
  - 6-b(英語情報源テーマで非発火): `WriterInstructionAppendTest.test_no_canonical_field_returns_byte_identical_text`、`run_canonical_spelling_research([])`がAPI呼び出しをスキップすること
  - 6-c(該当行なしLedgerでbyte不変): `BuildCommonBlockByteInvarianceTest`
  - 6-d(Fact Checkerプロンプト差分pin): `FactCheckPromptBackwardCompatTest`
  - 6-e(Trial-15条件F Ledgerで本番関数が同一instruction/canonical行を再現): `Trial15ConditionFReproductionTest`(既存artifact読み取り専用、新規API呼び出しなし)
- 既存`er012_open131_fact_attribution_production_wiring_01_test_01.py`: 本タスクの変更(Fact Checker呼び出しシグネチャ変化)に合わせ`test_a_family_fact_check_call_site_still_passes_no_extra_args`を`test_a_family_fact_check_call_site_still_passes_no_voice_attribution_arg`へ更新(voice_attribution_block非混入の確認という元の目的は維持)。**18/18 PASS**。
- プロジェクト全体回帰(`run_project_regression.py`、pattern `er0*_test_*.py`): **collected=2346 passed=2343 failed=3 errors=0**。失敗3件はすべて`er003_test_p2j_investigate.py`のテスト件数自己集計(reconciliation arithmetic、例: `1037 != 1032`)で、新しいテストファイルが追加されるたびに既知の形で失敗する既存の自己参照的カウント検証であり、本タスクの機能変更とは無関係(3-1節)。

### 3-1. 既知fail3件の内容(確認、本タスク起因ではない)

```
FAIL: test_combined_equals_sum_of_er002_and_er003 (2346 != 1823)
FAIL: test_p2h_reported_count_matches_er002_plus_er003_at_that_time (1037 != 1032)
FAIL: test_p2i_reported_count_matches_er003_at_p2i_era (665 != 660)
```
いずれも「過去のある時点で報告されたテスト総数」と「現在の実測総数」を
比較するハードコード定数照合であり、本タスクで新規テストファイルを
1つ追加したことで実測値が動いた結果である(機能的な回帰ではない)。

## 4. コスト影響評価(概算、実測ではない)

- **Research confirmation(Web検索、既存`r3.make_writer_research_fn()`を再利用)**: `FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15`実測値をそのまま参照可能(10件バッチで¥49.5)。1件あたり概算¥5前後。
- **固有名詞抽出(新規、Web検索なしLLM呼び出し1回)**: 本タスクではAPI呼び出しを実行していないため未実測。`pricing_snapshot.json`(input $5/M tokens、output $30/M tokens)から概算すると、Ledger本文(数千文字)を入力し短いJSON配列を出力する程度のタスクのため、reasoning_effort="medium"で概算¥5〜15程度と見積もる(**見積もりであり実測ではない**、次回News Ledger作成時に`cost_summary`相当のログで実測すべき)。
- **合計概算**: 1本のNews Ledger作成につき追加概算¥55〜65(一過性、Ledger作成時のみ発生。A2/B1は同一Ledgerを共有するため記事本数に応じて再発生しない、Trial-15 4-3節と同じ構造)。
- **5区分コスト表への算入**: 「① 今回実測コスト」相当は本タスクでは¥0(API呼び出しなし)。将来の実News Production runでは、上記概算を「② Trial/導入時特有の追加コスト」相当(Ledger作成の一過性コスト)として計上するのが適切(Trial-15の費用区分と同型)。「④ Standard同期でのコスト」(通常の記事生成一式)への影響は無い(Writer/Fact Checkerプロンプトへの追記はいずれもLedgerに該当行がある場合のみわずかにトークン数が増える程度で、既存の同期呼び出し1回に収まる)。「⑤ Batch量産換算」はTrial-15同様、web_search toolのBatch単価が`pricing_snapshot.json`に存在しないため算出不可(該当なし)。

## 5. Gate 3/4個別判定

| Gate項目 | 判定 | 根拠 |
|---|---|---|
| Gate 4: Dangling Reference Check | **PASS** | 1節参照。`verified_ledger_text`単一読込点、全呼び出し元grep確認済み |
| Gate 3: 既存機構との整合(retry/fallback/regeneration) | **PASS(Trial実測根拠、本タスクでの新規API実行なし)** | 2節。Trial-15が同一Production呼び出し列で実測済み |
| Gate 3: A2/B1両レベルへの影響確認(Cross-Level Consistency Check) | **PASS** | `run_theme()`のLedger読込1箇所をラップしたため、A2/B1は同一の`verified_ledger_text`(指示追記後)を共有し、片側だけ修正される余地が無い |
| Gate 3: realAPI runtime evidence(実News Production run) | **未完了** | 新規記事テーマはPM_GOVERNANCE.md 13節によりユーザー選定が必要なため本タスクでは実施していない。次回News生成時に取得予定 |
| Gate 3: Production採用の正式宣言(`PRODUCTION_WIRED`) | **未宣言** | 上記runtime evidence未完了のため、本タスクでは明示的に`PRODUCTION_WIRED`と記載していない(CURRENT_SPEC.md該当行の状態欄は`APPROVED_FOR_PRODUCTION`のまま) |

## 6. 変更ファイル一覧

- `C:\Users\tensh\eigo-radio\er011_open146_ledger_canonical_en_spelling_production_01.py`(新規)
- `C:\Users\tensh\eigo-radio\er011_open146_ledger_canonical_en_spelling_production_wiring_01_test_01.py`(新規、テスト24件)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_articles_generate.py`(import追加、`run_theme()`/`run_one_pattern()`の2箇所)
- `C:\Users\tensh\eigo-radio\er002_ja_web_research_r3.py`(`build_fact_check_prompt()`へ後方互換オプション引数追加)
- `C:\Users\tensh\eigo-radio\er012_open131_fact_attribution_production_wiring_01_test_01.py`(既存assertion更新、本タスクのシグネチャ変更に追随)
- `C:\Users\tensh\eigo-radio\CURRENT_SPEC.md`(「Cross-level仕様」節へ1行追加、Ledger schema・配線内容・検証根拠・未完了事項を記載)

## 7. 禁止事項の遵守確認

- `docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`: 触れていない。
- `OPEN_ITEMS.md`/`DECISION_LOG.md`: 編集していない(`CURRENT_SPEC.md`のみ編集)。
- API支出(Web検索/LLM/TTS): 実行していない(全テストはmock/依存性注入)。
- Overlap Gate順序・verdict語彙・判定閾値: 無変更(`build_fact_check_prompt()`の`FACT_CHECK_VERDICTS`・`build_common_block()`のtemplate構造・Point Overlap Gate呼び出し順序はいずれも触れていない)。
- 既存Production Ledger: 書き換えていない(`er003_output/n3_01/*/research/verified_fact_ledger.txt`等は未変更)。
- `PRODUCTION_WIRED`宣言: していない(CURRENT_SPEC.md該当行は`APPROVED_FOR_PRODUCTION`+未完了事項の明記のみ)。
- `git stash`/`git clean`/Git操作全般: 実行していない(Commit/Pushはユーザー確認待ち、本タスクの指示範囲外)。

## 8. UDR候補(採用可否は判断していない)

1. **既存Production Ledgerへの遡及適用**: `er003_output/n3_01/hanshin/research/verified_fact_ledger.txt`等の既存Ledgerに`canonical_en_spelling`行を追記するかどうか(今回は新規Ledger作成時からの適用のみとし、遡及適用は行っていない)。
2. **固有名詞抽出コストの実測**: 4節の概算(¥5〜15)は見積もりであり、次回News Ledger作成(実API実行)時に実測してCURRENT_SPEC.mdの概算値を実測値へ更新すべきか。
3. **Ledger内instruction文言の"Trial-15"表記**: 本配線ではTrial-15で実証済みの文言(見出し内の"Trial-15"表記を含む)をbyte単位でそのまま踏襲した(再検証なしの文言変更を避けるため)。将来的にこの内部ラベルをProduction向けの汎用表記へ整理するか(機能への影響は無い、cosmetic)。

## 9. 未完了事項(Gate 3)

realAPI runtime evidence(実News Production run、固有名詞抽出→Web検索
confirmation→Ledger追記→A2/B1記事生成→Fact Checker照合の全経路を実API
で1回通す)は本タスクでは取得していない。新規記事のテーマ選定は
PM_GOVERNANCE.md 13節によりユーザーが複数候補から選ぶ必要があるため、
別タスクとして着手する。取得後、本REPORTおよびCURRENT_SPEC.md該当行の
状態欄を`PRODUCTION_WIRED`へ更新するかはユーザー判断とする。
