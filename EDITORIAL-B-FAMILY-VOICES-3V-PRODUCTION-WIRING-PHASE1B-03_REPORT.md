# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-03-WRITER-LEDGER-KP-GLUE

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-03-WRITER-
LEDGER-KP-GLUE`。委任範囲は「Writer/Ledger/Key Phrase Production glueの
配線(承認済み3V仕様の不足配線のみ)」。**結論: STOP(未実装)**。書き込みは
本REPORTのみ。SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は
未編集。Git操作(add/commit/push)は未実施。API呼び出し0回(費用¥0、コード
変更0件のためregression再実行は既存3Vスイート56件のみ実施)。

## 要点(5行)

1. Key Phrase選定(`er003_v1_n3_01_scaffold_generate.py::run_key_phrases`)
   は既に family/voice数非依存の汎用Production関数であり、そのまま3Vへ
   再利用可能(新Key Phrase仕様は不要)。
2. しかし「Ledger作成」の実体(`er003_v1_en_direct_vfl_01_generate.py`
   =vfl01)は自らを「実験パイプライン」と明記し、`run_researcher()`/
   `run_verification()`が単一トピックのグローバル定数`TOPIC`を無条件で
   使う設計であり、任意の新テーマへ汎用配線するには関数改修が要る。
3. 「Writer」の実体(Trial-02の`B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK`)は
   構造原則とAI審査テーマ固有内容(Voice Card・Ledger evidence tag
   [VOICE_4_EVIDENCE 4-01]等)が不可分に混在しており、汎用テンプレート化
   には「どの文が構造原則でどの文がテーマ固有か」を新たに決める必要が
   あり、これは値の異なる**新しいWriter原則の考案**に該当しうる。
4. 上記2点はいずれもユーザー指定STOP条件(6項目)のうち「3V専用の新
   Writer原則」に該当する可能性が高いと判断し、Writer/Ledger配線コードは
   **実装しなかった**(Key Phrase配線のみでは記事本文が無いため単独では
   意味を持たず、これも保留)。
5. 既存3Voffline regressionスイート56件は本タスク開始時点のままPASSを
   再確認(コード変更なし、影響ゼロ)。Phase 2の実行手順・費用見積は
   「Writer/Ledgerが配線されている前提」のためSTOPと同時に提示不可
   (7節に代替案)。

## 1. Reconciliation(2V `main()` と 3V `main_b1_3v()` の差分の機械的列挙)

`er012_b_family_production_runner_01.py`を確認した結果、**2V `main()`
自体にもWriter/Ledger作成ステージは存在しない**(OPEN-132既存記載どおり)。
`main()`は`ARTICLE_PATH`(L63、既存承認済み記事の固定パス)を読み取り専用で
読むのみで、`prepare()`(L159)はこの固定パスを開くだけの関数である。同様に
`main_b1_3v()`も同一パターン(`prepare_3v()`、固定`ARTICLE_PATH`)。つまり
2V/3Vとも「新規テーマから記事を書く」経路はこのrunner内に一切存在しない。

過去に実在の2V記事(`ARTICLE_PATH`)・3V記事(3V Audio Trial出典)を生成した
経路は、いずれも本runnerとは別の**Trialスクリプト**だった:
- 2V: `er012_editorial_b_voices_trial_07.py`(Trial-07)
- 3V: `er012_editorial_b_voices_3v_person_voice_trial_02.py`(Trial-02、
  本タスクの参照元として指定されたファイル)

両者を比較すると、Writer呼び出しパターン(Researcher→Verified Fact
Ledger→`gen._generate_and_compress_article*`によるWriter→Analytical
Leakage Check retry[MAX_WRITER_ATTEMPTS=3、初回+是正2回]→Fact Checker
A'→Ledger Deviation+Local Rewrite→Directional Fact Precheck→[Point
Overlap monitoring]→Key Phrase→Support)は**ほぼ同一の呼び出しチェーン・
同一のProduction共有primitive**(`er002_ja_web_research_r3`/
`er003_v1_n3_01_articles_generate`/`er003_v1_en_direct_vfl_01_generate`/
`er008_directional_fact_precheck_08`/`er008_point_overlap_qa_18`/
`er010_ledger_local_rewrite_09`/`er003_v1_n3_01_evidence_compression_
editor`/`er006_model_routing_contract_01`)を使っている。差はsection数
(5→6)とAnalytical Leakage Checkの3V追加項目
(`leak_tension_constraint_integration`ほか)のみで、これはPhase 1
REPORT・OPEN-120で言及済みの承認範囲内。

## 2. 個別項目の判定

### (a) Key Phrase選定 — 配線可(新仕様不要)

`er003_v1_n3_01_scaffold_generate.py::run_key_phrases(article_text,
out_dir, article_id, source_level, process=None)`は記事テキストのみを
入力とし、family/voice数に依存しない。既に`er011_family_a_completion_
a2_trend_end_to_end_01_run.py::prepare_key_phrases()`がA2(Family A)の
**新規テーマ記事**に対して`process="A2_SUPPORT"`でこの関数を直接呼んで
実運用しており、B-Family用`process="B1_SUPPORT"`も同ファイルのb1b経路で
実運用実績がある(L493-494)。3Vへそのまま`process="B1_SUPPORT"`で
呼び出せば良く、**新Key Phrase仕様は不要**と判断した。現状の3V production
runner内`reuse_key_phrases`相当の関数は存在せず(2V側`reuse_key_phrases`
L188も「Trial-08の既存選定結果をhash一致確認のうえコピーするだけ」の
関数であり新規選定ではない)、新規選定用の薄いwrapperを書くだけで済む。

### (b) Ledger作成(Research→Verified Fact Ledger) — 要改修、STOP判断

`er003_v1_en_direct_vfl_01_generate.py`(vfl01、production runnerが
`run_deviation_check`/`get_client`目的で既にimport済み)は、ファイル冒頭
コメントで自らを「実験パイプライン」と明記し(L1-24)、`TOPIC_ID = "A02"`
`TOPIC = "英国の未成年向け夜間SNS設定"`という単一テーマのグローバル定数を
持つ。実際に:
- `run_researcher(client)`(L170)は引数に`topic`を取らず、内部で
  `build_researcher_prompt()`(引数省略、既定値`TOPIC`)を呼ぶ。
- `run_verification(client, ledger_parsed)`(L253)も`build_verification_
  prompt(TOPIC, ledger_parsed)`とグローバル`TOPIC`を無条件使用する
  (`build_verification_prompt`自体は`topic`引数を取るが、呼び出し元が
  渡していない)。

したがって、任意の新テーマ用Ledgerを作るには、この2関数を無変更のまま
"glue"として呼ぶことはできず、`topic`を明示的に渡す修正版呼び出し(または
低レベルprompt builder+schema定数を再利用した薄いwrapper)が必要になる。
これは機能追加であり、"Ledger作成のProduction化"という表現の実体は
「既存関数の単純な呼び出し」ではなく「単一テーマ実験スクリプトの部分的な
汎用化」である。Ledgerの**意味**(Researcher→独立Verification→確定という
2段構成)自体は変更しないため「Ledger意味変更」そのものには該当しないが、
次項(c)と合わせて実施の是非をユーザー判断待ちとした(7節代替案)。

### (c) Writer(Focus Module/Voice Card) — STOP(新Writer原則に該当する可能性)

Trial-02の`B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK`(該当ファイルL266-598、
約330行)を全文確認した。この文字列定数には次の両方が**不可分に**含まれる:

- 構造原則(3V承認済み、既に他箇所[registry `B_FAMILY_B1_3V_REQUIRED_
  SEGMENTS`等]で確認済み): 6見出し構造、一人称ルール、Evidence脇役原則、
  Tension 4要素構造、語数目安(design.md B-6由来、約410〜450語)、禁止
  事項一覧。
- AI審査(job screening)テーマ固有の内容: Voice Card 1〜3の具体的人物像・
  具体的な出典証言(BBC Worklife記事、CVS Health訴訟、NBCUniversal
  監査等)、Tensionの外部制約統合指示が**特定のLedger evidence tag ID**
  (`[VOICE_4_EVIDENCE 4-01]`=NYC Local Law 144、`4-02`=EU AI Act、
  `4-03`=Amazon中止事例)を名指しで参照している(L530-539)。

さらに、Writer retry時の是正メモ生成関数`build_leakage_corrective_
note_3v()`(同ファイルL892-922)も、persona名("Applicant"/"Recruiter/
Hiring Manager"/"Business Owner")や「経営者の役割」といったテーマ固有
表現をハードコードしている。

この330行のうち「どの文が3V共通の構造原則で、どの文がテーマ固有内容か」
を切り分けて汎用テンプレート化する作業は、既存SSOTのどこにも定義・承認
された切り分け基準が無い(registry側にはFocus Module定義そのものが
存在しない、`er012_b_family_editorial_type_registry_01.py` L200
「未確定(Phase 1は記事生成[Writer]自体を範囲外とするため...)」参照)。
この切り分け自体を今回新たに決めることは、Fableから明示された
STOP条件「3V専用の新Writer原則」に該当しうると判断した。

## 3. STOP判定

ユーザー決定に明記されたSTOP条件6項目のうち、**「3V専用の新Writer原則」
が必要になる可能性が高い**(2節(c))と判断し、Writer/Ledger配線コードの
実装を行わなかった。Key Phrase単体(2節(a))は新仕様なしで配線可能だが、
Writerが記事本文を生成しない限りKey Phrase配線は入力(記事テキスト)が
無く単独では意味を持たないため、これも実装を見送った。

Fable指示の原文「上記6項目のいずれかが必要になったらSTOP」に従い、
Production runner・registry・Trial-02いずれのファイルも**一切編集して
いない**(git status確認、本タスクによる差分ゼロ)。

## 4. 代替案(2つ)

- **代替案A(範囲限定でSonnetへ再委任)**: 「Ledger作成」「Writer」を
  今回のスコープから外し、代わりに次の限定タスクとして再委任する:
  (i) Key Phrase glue単体の配線(新規テーマの記事テキストを外部から
  受け取り`sc.run_key_phrases(..., process="B1_SUPPORT")`を呼ぶ薄い
  wrapper、新仕様なし)。(ii) vfl01の`run_researcher`/`run_verification`
  を`topic`引数を渡せる形へ改修する提案(Ledgerの意味・スキーマは無変更、
  グローバル定数依存を除去するだけ)を差分案として提示しユーザー承認後に
  実装。(iii) Writer(Focus Module)は、Fable/ユーザーが「どの部分が3V
  共通原則でどの部分がテーマ固有か」を明示的に切り分けた設計文書
  (design.md相当)を承認したうえで、Sonnetがその承認済み切り分けに従い
  機械的にテンプレート化する(Sonnetが切り分け基準を発案しない)。
- **代替案B(Phase 2を前工程を含めて再定義)**: OPEN-132の見積り
  (「Phase 1bとしてWriter/Ledger/Key Phrase glueの追加配線、2〜3
  セッション」)を修正し、新テーマでの3V記事生成は「(1)テーマ固有の
  Voice Card/Ledger/Focus Module content作成(Trial-01/02と同種の、
  人手/Fable主導の設計セッション、ソフトウェアのglueでは代替できない)
  →(2)承認済みcontentを入力として受け取るParameterized Production
  glue(代替案Aで実装)→(3)Assembly/TTS(Phase 1で配線済み)」の3段階に
  再定義し、(1)を明示的に別セッションのスコープとして扱う。

いずれもユーザー判断が必要なため、本タスクでは選択せず提示のみとする。

## 5. OPEN-132との整合

OPEN-132の4チェックリスト項目(Fact Checker A'既定接続/一人称機械保証/
Point Role hint接続/OPEN-129 required_structure整合)はPhase 2着手前
チェックリストであり、いずれも「Writerが実際に新規記事を生成できる
状態になった後」に意味を持つ項目のため、本タスクのSTOP判定によりまだ
評価対象にならない(現状維持、DEFERREDのまま)。

## 6. テスト結果(実施した範囲のみ)

- 既存3V offline regressionスイート(`er012_editorial_b_family_voices_
  3v_production_wiring_phase1_test_01.py`)を独立再実行:
  `Ran 56 tests in 0.100s / OK`(全PASS、コード変更ゼロのため影響なし
  の確認のみ)。
- プロジェクト全体回帰: 本タスクはコード変更ゼロのため未実施(直近の
  確認済みbaseline `collected=2309 passed=2306 failed=3[既知fail]`
  [OPEN-120行 PM-CLOSEOUT-CONSOLIDATION-74記載]がそのまま有効と判断)。
- Dangling Reference Check: 新規コード追加ゼロのため対象なし
  (Trial-onlyファイルへの新規importは0件)。
- Gate 3チェックリスト14項目・Gate 4: 新規Production変更が無いため
  評価対象外(前回Phase 1b-02時点の状態から不変)。

## 7. Phase 2エントリポイント・費用見積

Writer/Ledgerが未配線のため、「新テーマ指定で3V記事を生成するコマンド」
は現時点で提示できない(そのようなコマンドは存在せず、6節(c)の代替案A/B
いずれかの実施後に初めて提示可能になる)。2V比較記事についても同様
(2V側にもWriter経路は無い、1節参照)。費用見積は、Writer/Ledger配線の
実装方針(代替案A/Bのどちらか、または全く別の方針)が確定してから行う。

## 8. 禁止事項の遵守確認

`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は未編集。SSOT
(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)は未編集。Git操作
(add/commit/push)は未実施。API支出は0件(¥0)。Trial-onlyファイル
(`er012_editorial_b_voices_3v_person_voice_trial_02.py`ほか)への新規
importは追加していない(読み取り専用で内容確認のみ)。2V経路
(`main()`/`prepare()`等)は無変更。`git stash`/`git clean`は使用していない。
