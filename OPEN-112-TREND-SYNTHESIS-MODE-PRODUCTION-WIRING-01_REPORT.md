# OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01 — Trend Synthesis mode Gate 3配線

**管理ID**: OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01(Lane A-1)
**性質**: ユーザー承認(2026-09-08、`APPROVED_FOR_PRODUCTION`)に基づくGate 3配線実装。
Discovery側・4件の追加Trial候補(Mode判定自動化/News Ledger自動供給/Reference
Digest/Retry語彙拡張)は仕様化していない(Open Item継続)。

---

## 0. 訂正記録(作業ミスの開示)

Runtime evidence取得の最初の試行で、「Theme 2 Ledger(承認済み)」を誤って
米国・イラン/ホルムズ海峡テーマ(`OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-
TRIAL-09`/`OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10`がFocus Module
検証用に使った、Production採用に至っていない一回限りのTrialテーマ)から使用
してしまった。実際の`APPROVED_FOR_PRODUCTION`「Theme 2」は日本の若者のスロー
旅行志向を扱う別テーマ(`FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01_
REPORT.md`§0が指す「若者の旅」、Ledgerは`er011_output/open112_trend_theme2_
b_a2_b1_text_trial_12/research/theme2_verified_fact_ledger_CORRECTED_
trial12.txt`)である。誤りに気づいた時点で、誤ったrunの成果物を
`er011_output/open112_trend_synthesis_production_wiring_01/
_superseded_wrong_theme_iran_hormuz/`へ退避(削除はしていない、README_
MISTAKE.md参照)し、正しいTheme 2 Ledger/topicで再実行した。結果として
LLM費用が当初上限¥100を超過した(§6参照)。この経緯を隠さずそのまま報告する。

---

## 1. 配線実装

### 1.1 `er003_v1_n3_01_articles_generate.py`

- `build_common_block()`(348行付近)へ新規オプション引数
  `editorial_type_module_block: str = ""`を追加(既存`shared_point_
  blueprint_block`/`evidence_compression`と同型の後方互換パターン)。
- `COMMON_BLOCK_TEMPLATE`内、「【Spoken-first原則(数字の扱い)】」直前に
  `{editorial_type_module_block}`placeholderを追加。既定値`""`の場合は
  この位置に何も挿入されず、既存出力と完全に同一(§2で単体テスト固定)。
- Trend Synthesis用の新規定数`TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`
  (Trial-09でVALIDATED済みの内容を無変更で採用)・
  `TREND_SYNTHESIS_ENGAGEMENT_BLOCK`(Trial-10施策1でVALIDATED済みの
  内容を無変更で採用。施策2[Reference Digest]は含めない)を追加し、
  `EDITORIAL_TYPE_MODULE_BLOCKS = {"trend_synthesis": FOCUS + "\n\n" +
  ENGAGEMENT}`として登録。
- `resolve_editorial_type_module_block(editorial_mode: str | None) ->
  str`を新設。`None`/`""`は`""`を返し(既定挙動不変)、未知のmode文字列は
  `ValueError`(fail-closed、無音No-op化しない)。Mode自動判定ロジックは
  実装していない。
- Trial専用の`COMMON_BLOCK_TEMPLATE.replace()`アンカー置換方式には一切
  依存しない(明示的parameter化のみ)。

### 1.2 `er006_pool_pilot_01_writer.py`

- `run_writer_for_theme()`(Production Writer正式初回経路、`er010_no9_*`
  等多数の既存Production run記録で「Production正式初回経路」と明記されて
  いる関数)へ`editorial_mode: str | None = None`・`trend_gate_
  checklist: dict | None = None`引数を追加。
- `editorial_type_module_block = gen.resolve_editorial_type_module_
  block(editorial_mode)`を計算し、B1B/A2両方の`gen.build_common_
  block()`呼び出しへスレッド。
- `trend_gate_checklist`(手動判定結果)は、新規ファイル`run_metadata.
  json`へ`{"editorial_mode":..., "trend_gate_checklist":...}`として
  記録する。**既存`articles_run_summary.json`のschemaは変更していない**
  (下流でこのファイルをparseする既存コードは確認されなかったが、既定
  挙動不変の原則を優先し、mode metadataは別ファイルへ分離した)。

---

## 2. 既定値不変テスト(新規単体テスト)

`er011_open112_trend_synthesis_mode_production_wiring_01_test_01.py`
(11 tests、無料・API呼び出し無し、`unittest`)。

- **golden-master byte parity**: git HEAD(本タスク着手前・配線前)の
  `build_common_block()`を`git show`で取得し、同一入力で生成した出力を
  `er011_output/open112_trend_synthesis_mode_production_wiring_01/
  fixtures/`(3ファイル: 既定/shared_point_blueprint_block指定/
  evidence_compression指定)へ固定保存。現行コードの既定引数呼び出しが
  これらとバイト単位で完全一致することを確認(3 tests、いずれもPASS)。
- `{editorial_type_module_block}`placeholder文字列が既定出力へ一切
  漏れないことを確認。
- `editorial_mode="trend_synthesis"`指定時にFocus Module・Engagement
  Blockが実際に注入され、Anchor直前へ挿入順序どおり配置されることを確認。
- `resolve_editorial_type_module_block(None)`→`""`、未知mode→
  `ValueError`。
- Diagnostic Full Retry経路(`build_diagnostic_retry_prompt()`)が
  `original_prompt`(Focus Module込み)をそのまま部分文字列として保持する
  ことを確認(§3参照)。
- `run_writer_for_theme()`のソースを`inspect.getsource()`で静的検査し、
  `editorial_mode`/`resolve_editorial_type_module_block`/`editorial_
  type_module_block=editorial_type_module_block`/`trend_gate_
  checklist`が実際にコード中に存在することを確認。

**既存回帰テストの修正(付随)**: `er010_n9_production_integration_09_
test_01.py::test_template_still_formats_without_error`が、
`COMMON_BLOCK_TEMPLATE.format()`を直接、旧5-key(`editorial_type_
module_block`無し)で呼んでいたため、新placeholder追加により
`KeyError`で落ちた(regression実行で発見)。`editorial_type_module_
block=""`を追加して修正(1箇所、既存の`evidence_compression_block`
追加時にも同様の追随修正が必要だった前例と同型)。

全11 tests PASS(実行結果: `unittest`, `Ran 11 tests ... OK`)。

---

## 3. retry・fallback・regeneration整合(コード追跡+実runtime evidence)

| 経路 | 実装 | mode保持の根拠 |
|---|---|---|
| Diagnostic Full Retry(Point Overlap/Value QA NG時の記事全体再生成、`run_one_pattern()`内`while`ループ、最大`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`回) | `build_diagnostic_retry_prompt(original_prompt, article_text, point_overlap)`が`return original_prompt + "\n\n" + diagnostic_section`のみ。`COMMON_BLOCK_TEMPLATE`/`build_common_block()`を一切再呼び出ししない | `original_prompt`自体がeditorial_type_module_block込みで構築済みのため、機械的に保持される。単体テスト`test_diagnostic_retry_prompt_preserves_editorial_module_text`で確認。**実runでも確認**: 訂正後Theme 2 B1Bで実際に2回のDiagnostic Full Retryが発火し(§5)、最終的にOK到達 |
| Evidence Compression Editor(`ec_editor.run_lossless_editor(client, article_text, model)`) | `article_text`のみを受け取り、prompt再構築なし | mode非依存(既生成テキストの軽量化のみ) |
| Point Overlap QA(`run_point_overlap_qa_and_regenerate()`) | `article_text`のsection分割のみで動作、prompt再構築なし。Point-only regenerationは既に無効化済み(常にDiagnostic Full Retryへ委譲) | mode非依存 |
| Fact Checker(`r3.build_fact_check_prompt(topic, article_text, [])`) | 記事全文+topicのみ、Writer promptは無関係 | mode非依存 |
| Ledger Deviation Checker / Local Rewrite(Hook-aware) | 記事全文+Ledgerのみで動作 | mode非依存 |
| Directional Fact Precheck | 記事全文+Ledgerのみで動作 | mode非依存 |
| Human Review再生成 | 既存の「一回限りのrerun scriptを都度書いて`run_writer_for_theme()`を再度明示的に呼ぶ」運用パターン(`er010_no9_*`/`er011_open113_*`等の前例)を維持。再度呼ぶ際は`editorial_mode`を明示的に指定する必要がある(自動継承の仕組みは無い。既存の`blueprint`/`evidence_compression`等の他オプション引数も同様に呼び出し側の明示指定が必要という既存設計と一貫) | 設計変更なし(既存パターンを踏襲) |

Diagnostic診断語彙自体(evidence listing/trend overclaim等)の拡張は
行っていない(Gapとして`OPEN_ITEMS.md`に残す、変更禁止事項どおり)。

---

## 4. Research/Ledger供給経路の現状

Production Writerへの入力Ledgerは、**既存の承認済みTheme 2 Ledger
(手動作成・Trial-12で精度修正済み)をファイルとしてそのまま使う**手順が
正式initial path。今回のrunnerスクリプトはこのLedgerファイルをパス経由で
直接読み込むだけで、Trial Pythonモジュールはimportしない(Gate 4参照)。

既存自動Research pipeline(`er002_ja_web_research_r3.py`等)の出力形式との
互換性は**未検証・不明**。Ledgerを自動Research経路から供給する統合は今回
配線していない(`USER_DECISION_REQUIRED`のまま、`OPEN_ITEMS.md`残件)。

Trend Gate 6条件チェックリストも、Theme 2については記事生成前の正式な
事前記録(Iran/HormuzテーマのTrial-09にあった`trend_gate_result.json`
相当)が存在しなかったため、本タスク実施者が既存Ledger内容を読んで
事後的に手動判定した(`er011_open112_trend_synthesis_production_
wiring_01_run.py::THEME2_TREND_GATE_CHECKLIST`、6条件+Mode判定2問とも
`PASS`/`TREND_SYNTHESIS`)。自動判定ロジックは実装していない。

---

## 5. Runtime evidence

配線後のProduction Writer正式初回経路(`er006_pool_pilot_01_writer.
run_writer_for_theme` → `er003_v1_n3_01_articles_generate.run_one_
pattern`、Trialスクリプト非経由)で、正しいTheme 2 Ledger/topicから
`editorial_mode="trend_synthesis"`を指定してA2・B1Bを実際に1本ずつ生成。
保存先: `er011_output/open112_trend_synthesis_production_wiring_01/`。

| Level | 結果 | Fact QA | Ledger Deviation | Directional Precheck | Point Overlap | 備考 |
|---|---|---|---|---|---|---|
| B1B | `status=OK` | `REVIEW_REQUIRED`(non-blocking advisory) | `LEDGER_COMPLIANT`(Local Rewrite cycle 1回でMAJOR 1件を解消後) | `DIRECTION_REVIEW_REQUIRED`(non-blocking advisory) | Diagnostic Full Retry 2回発火、2回目でPASS(`point_overlap_article_retry_log.json`: attempt0/1 flagged=True、attempt2 flagged=False) | Key Phrase選定まで到達せず(§6の費用制約で今回はskip。ただし後述の訂正前runで同一Focus Module注入済みprompt上でKey Phrase選定[`REDUNDANCY_PASS`]が機能することは別テーマで実証済み) |
| A2 | `status=NG_REVIEW_REQUIRED` | 未実行(Point Overlap QAで先にblock) | 未実行 | 未実行 | Diagnostic Full Retry 2回発火するも、2回目終了時点でもPoint One/Two対Full Storyのlexical overlapが閾値超過(`point_one: ratio=0.414`, `point_two: ratio=0.455`, 閾値0.40)で解消せず、既存Loop Budget上限(`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`)に到達し`NG_REVIEW_REQUIRED`で終了 | 既存安全装置(Loop Budget)を独自判断で回避・追加retryせず、そのまま報告する(禁止事項どおり) |

Focus Module実発火ログ: 両Levelの`audit/prompt.txt`に`Trend Synthesis
Focus`・`Interesting/Engaging/Entertaining原則`の文字列が実際に含まれる
ことを確認済み(`grep -c`で各2件)。生成されたB1B記事(`b1b/article.md`)は、
時系列列挙ではなく「意識と実際の行動のギャップ」という対比構造で書かれ、
Point One(“Slow can mean control”)・Point Two(性別による違い)が
それぞれ異なる意味づけを持ち、In One Lineが方向感+留保("a direction
taking shape, not a completed shift")で結ばれており、既存rerun_04
完成テキスト(同一Theme 2、施策2[Reference Digest]込みで生成された
過去バージョン)と構造的に類似する結果になった(同一である必要はない、
と指示どおり比較のみ)。退行は確認されなかった。

---

## 6. 費用(§0の訂正を含む実費、透明開示)

- 誤ったIran/Hormuzテーマでのrun(B1B+A2+A2追加retry1回+B1B Key Phrase
  選定1回): 約¥83.01(内訳: token代¥13.69相当+web_search_call課金
  37回分¥0.37相当[USD]。pricing snapshotは`er005_output/cost_
  baseline_01/pricing_snapshot.json`)。
- 訂正後の正しいTheme 2 run(B1B 2 Diagnostic Full Retry込み+A2 2
  Diagnostic Full Retry込み): 約¥37.11。
- **合計 約¥120.12**。当初上限¥100を、§0の作業ミスとその是正のため
  超過した。追加のA2再実行(3回目)・Key Phrase選定(Theme 2側)・TTS等、
  これ以上の追加課金は行っていない(ここでSTOP)。

---

## 7. Regression

`run_project_regression.py`(唯一の実行手段)。

- 配線直後(修正前): `collected=2195 passed=2192 failed=3 errors=1`
  (新規error 1件、§2の`er010_n9_production_integration_09_test_01.py`
  KeyError、既存テストの追随修正で解消)。
- 修正後・最終確認: `collected=2195 passed=2192 failed=3 errors=0`。
  failed 3件は既知の無関係failure(`er003_test_bad.FixtureTests.
  test_case_0`、`er003_test_p2j_investigate`の集計系2件)のみで、
  本タスクによる新規failureは0件。

---

## 8. Gate 3チェックリスト(13項目、ユーザー指定)

| # | 項目 | 充足状況 |
|---|---|---|
| 1 | Production Writer正式初回path | 充足。`run_writer_for_theme()`→`run_one_pattern()`。§1 |
| 2 | retry・fallback・regeneration整合 | 充足。§3(コード追跡+実run2回のDiagnostic Full Retry発火で実証) |
| 3 | Trial専用Replace依存なし | 充足。明示的`{editorial_type_module_block}`parameter化のみ。§1.1 |
| 4 | runtime evidence | 充足(A2は既存Loop Budget上限内でNG_REVIEW_REQUIRED、B1Bは`OK`到達)。§5 |
| 5 | regression・validator・integration | 充足。§7(collected=2195、既知3件除き全PASS) |
| 6 | Research・Ledger供給経路の現状 | 記録として充足(自動化はスコープ外、現状=手動供給を明記)。§4 |
| 7 | Focus Module | 充足。VALIDATED内容を無変更で正式採用。§1.1 |
| 8 | Engagement・Storytelling原則 | 充足。Trend Synthesis限定採用、施策2[Reference Digest]は含めない。§1.1 |
| 9 | Trend Gate・Mode判定 | 充足(手動判定結果の記録機構のみ、自動判定なし)。§4 |
| 10 | Point Overlap・Ledger Deviation | 充足。既存機構無変更、mode非依存で実際に機能(A2をblock、B1BはLocal Rewriteで解消)。§3・§5 |
| 11 | CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS | 充足(本コミットで反映)。§9 |
| 12 | Git | 充足(本コミットで実施)。§10 |
| 13 | Dangling Reference | 充足(Trialスクリプトへのimport無し)。§9(Gate 4表) |

**未充足項目: なし**。ただし§0の作業ミス(誤テーマでのrun、費用超過)は
瑕疵として明記する。B1BはKey Phrase選定まで到達していない(費用制約による
今回のskip、既存run(誤テーマ)で技術的には動作確認済み)。

---

## 9. Gate 4 Dangling Reference Check

Production初回path・retry・fallback・regeneration・validator・Human
Reviewのいずれの経路にも、Trialスクリプト(`er011_*trend*trial*`等)への
importは存在しない。

| 確認対象 | Trial import | monkeypatch/setattr | 結果 |
|---|---|---|---|
| `er003_v1_n3_01_articles_generate.py`(build_common_block/resolve_editorial_type_module_block/run_one_pattern) | 無し(grep確認) | 無し | Dangling Referenceなし |
| `er006_pool_pilot_01_writer.py`(run_writer_for_theme) | 無し(grep確認) | 無し | Dangling Referenceなし |
| Mode自動判定・Ledger自動供給・Reference Digest・Retry語彙拡張への参照 | 無し(いずれも未実装) | — | 該当なし |

**残存する既知の相互依存の注記**(Dangling Referenceではないが、将来の
参考情報として記録): `COMMON_BLOCK_TEMPLATE`へ新規`{editorial_type_
module_block}`placeholderを追加したため、過去のTrialスクリプト
(`er011_open112_trend_*trial*`・`er012_editorial_b_voices_trial_03〜
07`等)が採用している`gen.COMMON_BLOCK_TEMPLATE.replace(ANCHOR,...)
.format(hanshin_master_full_text=..., ..., evidence_compression_
block="")`という直接`.format()`呼び出しパターンは、`editorial_type_
module_block`キーを渡さない場合`KeyError`になる。これは`shared_point_
blueprint_block`/`evidence_compression_block`追加時と同型の既知の
拡張パターンであり、これらのTrialスクリプト自体も`assert ANCHOR in
gen.COMMON_BLOCK_TEMPLATE`という「Production側テンプレート変更時は
fail-closedで停止する」設計を既に内包している。現在のLane B active
runner(`er012_b_family_production_runner_01.py`等)はこれら旧Trial
スクリプトを経由せず、`gen.COMMON_BLOCK_TEMPLATE`を一切参照しない独自
経路(Phase 1 runner)であることをgrepで確認済みのため、現時点で実行中の
他タスクとの衝突リスクは無い。

---

## 10. SSOT・Git

- `CURRENT_SPEC.md`: 新規節「## News Editorial Mode(Trend Synthesis)」
  追加(`## Cross-level仕様`直前)。各項目`PRODUCTION_WIRED候補(Fable
  受入待ち)`(Sonnetは`PRODUCTION_WIRED`を自称しない)。
- `DECISION_LOG.md`: 新規`## OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-
  WIRING-01`セクション追加。
- `OPEN_ITEMS.md`: OPEN-112行へ追記(mode配線完了、`PRODUCTION_WIRED
  候補[Fable受入待ち]`+commit hash、残件4件明記)。
- Git: G1(配線コード・テスト・Report・evidence)→G2(SSOT 3ファイル)の
  2段階commit、`git add`はファイル名指定のみ(`-A`/`.`不使用)、wav除外
  (本タスクはテキストのみで生成しておらず該当ファイルなし)。

---

## 11. 修正指示1回目への対応(Fable Gate 7差し戻し)

Fableの受入判定(Gate 7)により、(1) A2のruntime evidenceが
`NG_REVIEW_REQUIRED`止まり、(2) B1BのKey Phrase選定skip、(3) 費用上限
超過、の3点が差し戻された。既存Loop Budget(`POINT_OVERLAP_ARTICLE_
RETRY_MAX=2`)・Point Overlap閾値(0.40)は無変更のまま、以下を実施した。
本節の実装コード: `er011_open112_trend_synthesis_production_wiring_01_
a2_rerun_02.py`(新規、A2再実行)。既存
`er011_open112_trend_synthesis_production_wiring_01_run.py`・
`er003_v1_n3_01_articles_generate.py`・`er006_pool_pilot_01_writer.py`は
一切変更していない。

### 11.1 A2再実行(新規runとして最大2回まで)

「同じProduction正式path」の解釈: `run_writer_for_theme()`はB1B・A2の
両方を毎回生成する設計(既にOK到達済みのB1Bを再生成すると無駄な追加費用
になる)ため、`run_writer_for_theme()`がA2 labelに対して実際に呼ぶのと
**全く同一の関数列**(`gen.resolve_editorial_type_module_block` →
`gen.build_common_block` → `gen.build_prompt` → `gen.run_one_pattern`、
`apply_evidence_compression=True`既定)を、A2単体に絞って直接呼び出した
(`er006_pool_pilot_01_writer.py` 66-87行と同一ロジック、B1Bループを
省いただけ)。`gen.run_one_pattern()`内部のLoop Budget・Point Overlap
閾値・Diagnostic Full Retry・Point Value QAは無変更のまま使用。

保存先: `er011_output/open112_trend_synthesis_production_wiring_01/
a2_rerun_02/attempt{1,2}/`(既存`a2/`evidenceは上書きしていない)。

| 新規run | 内部Diagnostic Full Retry(記事全体再生成) | 最終Point Overlap ratio | 最終status |
|---|---|---|---|
| 元run(参考、既報告済み) | attempt0→2まで3回生成、全て`point_one`or`point_two`いずれかflagged継続 | point_one=0.414, point_two=0.455(共にflagged) | `NG_REVIEW_REQUIRED`(Loop Budget上限到達) |
| 新規run 1回目(`a2_rerun_02/attempt1`) | 同様に3回生成、attempt0(p1=0.406flagged/p2=0.364)→attempt1(p1=0.342/p2=0.406flagged)→attempt2(p1=0.48flagged/p2=0.655flagged) | point_one=0.48, point_two=0.655(共にflagged、悪化) | `NG_REVIEW_REQUIRED`(Loop Budget上限到達) |
| 新規run 2回目(`a2_rerun_02/attempt2`) | attempt0(p1=0.483flagged/p2=0.343)→attempt1(p1=0.361/p2=0.308、いずれもflagなし)で解消(記事全体retry 1回で解消) | point_one=0.361, point_two=0.308(共にflagなし) | `status=OK` |

新規run 2回目でProduction正式path上`status=OK`に到達したため、3回目
(許可された最大2回を超える追加run)は実行していない。`status=OK`到達後の
下流QAは以下のとおり(いずれもnon-blocking advisory、既存運用どおり
`status=OK`の判定材料にしていない):

- Fact Checker: `verdict=REVIEW_REQUIRED`(「ますます」等の経年変化表現・
  意向データを実績のように読む表現・観光白書の政策記述の解釈、の3点を
  参考指摘として記録。矛盾[FAIL]ではない)。
- Ledger Deviation Checker(Hook-aware): `LEDGER_COMPLIANT`(deviation
  0件、局所Rewriteサイクル不要)。
- Directional Fact Precheck: `DIRECTION_REVIEW_REQUIRED`(advisory)。

**参考所見(対策は実装せず、論点として提示のみ)**: 3回の独立した生成
(元run・新規1回目・新規2回目)を比較すると、内部Diagnostic Full Retryの
1回目・2回目で必ずratioが単調に改善するわけではない(新規1回目は
attempt0→2で悪化: 0.406→0.48)。一方、新規2回目はattempt0→1で明確に
改善して解消した(0.483→0.361)。Trend Synthesis Focus Module
(「意識と実際の行動のギャップ」という対比構造を書かせる指示)が、
Point One/TwoでLedgerの同じ数値的Evidence(宿泊日数・アンケート回答率
等)へ言及させやすく、Full Story側とのlexical overlapを高める傾向が
ある可能性はある一方、既存Theme 2 Trial(`OPEN-112-TREND-THEME2-B-
LEDGER-FIX-AND-A2-B1-TEXT-TRIAL-12`、editorial_mode配線前・Focus
Module無し)のA2でも、§16の記録によればPoint Overlap Article Retryが
1回発火している(1回目で解消、`NG_REVIEW_REQUIRED`までは至らなかった)。
つまりFocus Module無しでもTheme 2 A2はPoint Overlapがflagされる余地が
元々あり、Focus Moduleが唯一の原因と断定できる材料は今回の3 runsだけでは
不十分。run-to-run varianceが大きく(同一prompt構造でも生成ごとに
ratioが0.31〜0.66まで振れ、内部retryを重ねても単調に改善しない)、
「Focus Module起因で悪化幅が増えている」可能性と「単純なsampling
variance」を切り分けるには追加run(未実施、費用がかかる)が必要。この
切り分け自体はFable/ユーザー判断事項として提示するのみで、本タスクでは
対策(Focus Module修正・閾値変更等)を実装していない。

### 11.2 B1B Key Phrase選定

対象: 既存OK到達済みのB1B本文(`er011_output/open112_trend_synthesis_
production_wiring_01/b1b/article.md`、無変更)。実行コード:
`er011_open112_trend_synthesis_production_wiring_01_keyphrase_run.py`
(既存、`er003_v1_n3_01_scaffold_generate.run_key_phrases()`をB1B用
`process="B1_SUPPORT"`で呼ぶだけ、Production Key Phrase経路そのもの)。
保存先: `er011_output/open112_trend_synthesis_production_wiring_01/
b1b/key_phrases/`(新規、既存B1B evidenceの上書きなし)。

- Selection: `KEY_WORDS_STRUCTURE_PASS`。
- Canonicalization: `CANONICALIZATION_PASS`(5件、QA全項目PASS)。
- Redundancy QA(5件相互の意味重複QA): 1回目`REDUNDANCY_NG`(rank2
  "quiet contradiction" とrank3 "unresolved tension" が意味・使用場面・
  概念的役割で重複と判定)→ 既存の選定やり直し機構(`KEY_PHRASE_
  REDUNDANCY_RETRY_MAX`以内)で2回目`REDUNDANCY_PASS`。
- 最終5件(rank・key_phrase・japanese_gloss): 1 "quiet contradiction"/
  目立たない矛盾、2 "be read as proof"/証拠と受け取ってはいけない、
  3 "median"/真ん中の値、4 "landmark-based itineraries"/名所を中心に
  組んだ旅程、5 "take shape"/形になり始める。

### 11.3 費用実績

| 項目 | USD | 円(1USD=160円固定、`er005_stage7_cost_compute.py`と同一換算SSOT) |
|---|---|---|
| A2再実行 新規run 1回目(`a2_rerun_02/attempt1`、NG) | $0.0375 | ¥6.00 |
| A2再実行 新規run 2回目(`a2_rerun_02/attempt2`、OK。Fact Checker/Directional Precheckのweb_search 15回分を含む) | $0.2111 | ¥33.78 |
| B1B Key Phrase選定(selection×2+canonicalization+redundancy QA×2) | $0.0281 | ¥4.50 |
| **合計** | **$0.2768** | **¥44.28** |

上限¥50以内(超過なし)。raw usage log: `er011_output/
open112_trend_synthesis_production_wiring_01/a2_rerun_02/raw_usage_
log.jsonl`・`er011_output/open112_trend_synthesis_production_wiring_01/
b1b/key_phrases/raw_usage_log.jsonl`。

### 11.4 Gate 3チェックリスト項目4(runtime evidence)の更新

§8表の項目4「runtime evidence」を以下のとおり更新する(他の項目・
既存章は書き換えない)。

**旧記載**: 「充足(A2は既存Loop Budget上限内でNG_REVIEW_REQUIRED、
B1Bは`OK`到達)。§5」

**新記載**: 充足。A2は新規run 2回目(`a2_rerun_02/attempt2`)で
Production正式path上`status=OK`に到達(§11.1)。B1BはKey Phrase選定
まで完了(`REDUNDANCY_PASS`、§11.2)。A2・B1Bとも`status=OK`+Key
Phrase到達という、修正指示前より高い充足水準に更新。ただし新規run
1回目は依然`NG_REVIEW_REQUIRED`であり(§11.1表)、run-to-run varianceが
大きいことは§11.1の参考所見のとおり未解決の論点として残る。

### 11.5 本節のSSOT・Git

本タスクの指示によりSSOT編集・Git操作は行っていない(Lane B並行タスクとの
衝突回避のため)。CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.mdへの
反映・commitは、Fable側で別途一括して行う前提。
