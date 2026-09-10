# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01`(Phase 1=
実装+オフラインtest、API呼び出しなし、費用¥0)。委任範囲の正本は
`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PLAN-01_REPORT.md`。書き込みは
実装範囲1〜4のコード・新規テストファイル1本・regressionログ(scratch)・本
REPORTのみ。SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/
`ARTIFACT_REGISTRY.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は
未編集。Git操作(add/commit/push)は未実施。API呼び出し(LLM/TTS/ASR)は0回
(費用¥0、regression実行でもAPIは呼ばれない)。

## エグゼクティブサマリー

1. 3V(3声Voice構成)のProduction正式経路(registry・B-Family集約module・
   runner)への配線コードを実装した。2V(2声)経路の既存関数は**1つも変更
   せず**、全て新規関数・新規オプション引数(既定値でOFF)として追加した。
2. `registry.build_required_structure()`へ`voice_c: str | None = None`
   (既定None)を追加し、`voice_c`省略時は修正前と**byte単位で同一**の出力
   になることを単体テストで固定した。`voice_c`指定時のみ3V用16 segment
   (`point_one/two/three`命名、Trial実測構造と一致)を返す。
3. Comment 2・3の登録テキスト(`VOICES_COMMENT_2_ROLE`/`VOICES_COMMENT_3_
   ROLE`)を、2026-09-10ユーザー決定に基づきVoice数非依存の汎用表現へ
   最小限だけ書き換えた(3V専用の別Contractは新設していない)。役割
   マーカー(意味)は維持し、count固有の言い回し(「One Voice/Another
   Voice」「2つの声」「どちらか一方」等)のみ除去した。**この変更点は
   人間レビューを推奨する**(4節)。
4. 共有ファイル`er003_v1_n3_01_assemble.py`は、`DISFLUENCY_QA_MANDATORY_
   SEGMENTS_BY_LEVEL["B1"]`へ`point_three_heading`を1エントリ追加しただけ
   (STOP条件(b)の上限内)。
5. Trial専用実装(`er012_editorial_b_voices_3v_audio_trial_01.py`)への
   依存はゼロ(モジュールレベルimportなしをASTで機械確認、単体テスト
   3件)。STOP条件(d)は該当しない。
6. **STOP条件(a)に該当する新規regression failureが1件発生した**
   (`er012_editorial_b_family_production_phase1_test_01.py::
   DisfluencyQaMandatoryDictB_FamilyA2Tests::
   test_existing_b1_and_standard_a2_entries_unchanged`)。原因は明確
   (4節で説明する、既存の"B1"タプルへ`point_three_heading`を1件追加した
   結果、その既存テストがpinしていた旧タプル値と不一致になった)。この
   既存テストファイルは本タスクの書き込み許可対象外のため、**自分では
   修正していない**。変更は巻き戻していない。詳細と選択肢は5節。
7. 新規オフラインtest 36件全PASS。`run_project_regression.py`
   (collected=2289 passed=2285 failed=4)。failed 4件中3件は本タスクと
   無関係の既知failure(`er003_test_p2j_investigate.py`の帳簿的カウント
   照合テスト、テスト総数が増えるたびに失敗する設計上の既知事象)、
   残り1件が上記6の新規failure。
8. Phase 1では`APPROVED_FOR_PRODUCTION`(2026-09-10確定)からの配線コード
   実装・オフラインtestまでを完了した。`PRODUCTION_WIRED`は宣言していない
   (Phase 2 runtime evidence・Phase 3 SSOT更新が必要、8節)。
9. 残存課題6点(3V長文化/Tension再膨張/Local RewriteのVoice抽象化/Fact
   Checker A'負荷/Distinctness維持/Audio structural gate mandatory化
   deferred)はいずれも本Phaseで解決していない(9節)。

---

## 1. Reconciliation Check(PM_GOVERNANCE 2-1節)

着手前に計画正本(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-
PLAN-01_REPORT.md`)全文・対象4ファイルの現行実装・Trial実装
(`er012_editorial_b_voices_3v_audio_trial_01.py`)を確認した。

- 計画時点との差分: 計画作成後に他の並列タスクが同一ファイル群を変更した
  形跡はなし(実ファイルの行番号・関数シグネチャは計画Report記載どおり)。
- 既存retry/fallback/regeneration機構(TTS retry cascade・Human Review
  Lock・disfluency gate・OPEN-121/122)はvoice_nameを引数で受け取る汎用
  primitiveのままで、今回のVoice 3(Schedar)追加でも無改造で組み込める
  ことを実装前に確認済み(計画4節の分析どおり)。
- OPEN-129(Audio structural gate)はopt-in・mandatory化deferredのまま
  変更していない(9節)。

## 2. 変更ファイル一覧と差分要旨

`git diff --stat`実測値(見出しのみ抜粋、詳細は各ファイルのコード
コメント参照):

| ファイル | 行数変化 | 内容要旨 |
|---|---|---|
| `er012_b_family_editorial_type_registry_01.py` | +102/-8 | `VOICE_ASSIGNMENT["voice_c"]="Schedar"`追加(fallbackキーなし)、`VOICES_COMMENT_2_ROLE`/`_3_ROLE`のVoice数非依存汎用化、`B_FAMILY_B1_3V_REQUIRED_SEGMENTS`(16 segment)・`B_FAMILY_B1_3V_CONFIG`新規、`EDITORIAL_TYPES["b_family_voices"]["b1_3v"]`登録、`get_editorial_type_b1_3v()`新規、`_ROLE_TO_VOICE_RESOLVERS_3V`新規、`build_required_structure()`へ`voice_c=None`引数追加(2V経路は無変更のまま分岐) |
| `er012_b_family_voices_production_01.py` | +307 | import追加(`tts_gen`/`point_headings`/`voice01`/`cl`/`shared_narration`)、`split_six_voice_sections()`/`build_parts_3v()`新規(6区切りparser)、`resolve_voice_names_3v()`新規、`load_b1_sources_3v()`新規、`build_b1_voices_timeline_3v()`新規、`run_tts_3v()`新規(Trial側`run_tts_3v()`を正式移設、narration_dir引数化) |
| `er012_b_family_production_runner_01.py` | +434 | `level="b1_3v"`分岐追加(`main()`)、`prepare_3v`/`voice_check_3v`/`reuse_key_phrases_3v`/`run_scaffold_3v`/`finalize_tts_results_3v`/`run_assembly_3v`/`_row_info_3v`/`build_player_html_3v`/`main_b1_3v`/`assert_budget_ok_3v`新規、3V用定数(`ARTICLE_PATH_3V`等)新規 |
| `er003_v1_n3_01_assemble.py`(共有) | +11/-1 | `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]`へ`point_three_heading`を1エントリ追加(コメント含む、データ変更は1エントリのみ) |
| `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`(新規) | +約440行 | 11クラス・36テスト(3節参照) |

いずれも2V/A-Family既存関数は1つも書き換えておらず、新規関数・新規
オプション引数(既定値で無効)としてのみ追加した。

## 3. 2V互換性の確認方法と結果

- `registry.build_required_structure("b1", voice_a, voice_b)`(`voice_c`
  省略)が、修正前の2V出力とbyte単位で一致することを
  `RegistryVoiceCArgumentBackwardCompatibilityTests`で固定(3テスト、
  期待値を修正前のハードコード14 segmentタプルとして直接比較)。
- `voice_c=None`明示指定と省略時が完全同一であることも確認。
- `"a2"`level側は`voice_c`拡張の影響を受けないことを確認
  (`test_a2_level_unaffected_by_voice_c_extension`)。
- `split_six_voice_sections()`(3V専用)は既存`split_five_voice_
  sections()`(2V、無変更)と独立して動作し、互いに相手の構造を誤検出
  しないことを確認(`test_existing_five_section_parser_unaffected`)。
- `build_b1_voices_timeline_3v()`が既存`build_b1_voices_timeline()`
  (2V)・`asm.build_b1_timeline()`(A-Family)のいずれも呼ばないことを
  mockで確認。
- `run_project_regression.py`実測: `collected=2289 passed=2285 failed=4`。

## 4. Comment 2/3のVoice数非依存汎用化(人間レビュー推奨)

`VOICES_COMMENT_2_ROLE`/`VOICES_COMMENT_3_ROLE`(LLMへ渡すRole
instruction文字列本体)を、下記のとおり最小限だけ書き換えた。役割
(Comment 2=Hookの問いから複数Voiceへの橋渡し、Comment 3=「正しさの
判定」ではなく「なぜ違って感じるか」への視点移動)自体は変更していない。

- Comment 2: 「(One Voiceの後、続けてAnother Voice)を聞きます」→
  「を、声を変えながら順番に聞きます」。avoidリストの「One Voice・
  Another Voiceの具体的な内容の先取り」→「これから聞く各Voiceの具体的な
  内容の先取り」。
- Comment 3: 「(One Voice・Another Voice)を両方すでに聞き終わり」→
  「をすべて聞き終わり」。「2つの声を聞き終えたリスナー」→「複数の声を
  聞き終えたリスナー」。「どちらか一方の声を」→「いずれかの声を」。
  タイトル行の「どちらが正しいか」自体は変更していない(2V向けの
  変更として不要と判断し、変更範囲を最小化した)。

Comment 1・4は本タスクで一切変更していない(登録文字列のマーカー検査で
確認)。2Vの実際のLLM生成結果(Comment 2/3の実出力テキスト)を固定した
既存test fixtureは見つからなかった(コードベース内grep確認、コメント
Contractの生成出力自体は毎回LLMが生成するため決定的な期待値を持つ
test/fixtureは存在しない)ため、既存test資産への影響はゼロだったが、
**この文言変更自体がPromptの実質的な書き換えである**ため、Fable/
ユーザーによる内容レビューを推奨する。意味変更が避けられないと判断した
箇所(タイトル行の「どちらが正しいか」)はあえて変更していない。

## 5. STOP条件(a)該当: 新規regression failure 1件(未対応)

`er003_v1_n3_01_assemble.py`の`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_
LEVEL["B1"]`へ`point_three_heading`を追加した結果(2節、計画4/9節で
明示的に承認された変更)、既存テスト
`er012_editorial_b_family_production_phase1_test_01.py::
DisfluencyQaMandatoryDictB_FamilyA2Tests::
test_existing_b1_and_standard_a2_entries_unchanged`が失敗する
(`AssertionError: Tuples differ`、旧8要素タプルを直接pinしていたため)。

- **本タスクの書き込み許可範囲は実装範囲1〜4・新規テストファイル・本
  REPORTのみであり、この既存テストファイルは対象外**のため、自分では
  修正していない。
- 変更(`point_three_heading`追加)自体は巻き戻していない(計画・委任文で
  明示的に承認された、共有ファイルへの唯一許容される変更のため)。
- これは2V/A-Family Production挙動そのものの機能劣化ではなく、既存
  テストが「B1」タプルの正確な要素数・順序をハードコードしていたために
  発生した、想定内の副作用と判断する(`point_headings.generate()`は
  `point_one_heading`/`point_two_heading`と同じ関数のため、
  `point_three_heading`も同じ規約でdisfluency_checkedを記録することを
  コード上確認済み。3節の新規テストで非影響を機械確認済み)。
- **選択肢**(ユーザー/Fable判断待ち):
  (a) 該当1行(期待タプル)を`point_three_heading`込みへ更新する1行修正を
      Fable側またはユーザー承認のうえ実施する(最小・低リスク)。
  (b) 既知failureとして4件目を受け入れ、Phase 3のSSOT更新まで保留する。
  (c) その他の指示。

## 6. テスト結果

- 新規オフラインtest: `er012_editorial_b_family_voices_3v_production_
  wiring_phase1_test_01.py`、11クラス・36テスト、**全PASS**(実行ログ:
  `Ran 36 tests in 0.078s / OK`)。
- `run_project_regression.py`実測: `collected=2289 passed=2285 failed=4
  errors=0 skipped=0`。failed内訳:
  - `er003_test_p2j_investigate.py`の3件(`test_combined_equals_sum_of_
    er002_and_er003`/`test_p2h_reported_count_matches_er002_plus_
    er003_at_that_time`/`test_p2i_reported_count_matches_er003_at_
    p2i_era`) — 本タスク前から存在する既知failure(帳簿的カウント照合、
    テスト総数増加のたびに失敗する設計、本タスクと無関係)。
  - `test_existing_b1_and_standard_a2_entries_unchanged` — 5節の新規
    failure。
- API呼び出しは0回(TTS/LLM/ASR未使用、費用¥0)。
- 証跡保存先: `er012_output/editorial_b_family_voices_3v_production_wiring_
  phase1_01/regression_evidence/`(`run_project_regression_full_log.txt`・
  `run_project_regression_summary.json`・`new_offline_test_run_log.txt`)。

## 7. Trial専用実装への依存確認

`NoTrialScriptModuleLevelImportTests`(3テスト)で、registry・
`voices_production_01`・`production_runner_01`のいずれも、モジュール名に
"trial"を含むモジュールをモジュールレベルでimportしていないことをAST
解析で機械確認した(全PASS)。3V用の6区切りparser・required_structure・
timeline builder・`run_tts_3v()`はいずれもTrialスクリプトから**正式移設**
した実体であり、Production経路がTrialスクリプトを参照する箇所はゼロ。
STOP条件(d)は非該当。

## 8. PRODUCTION_WIRED完了条件(Gate 3)の充足状況(Phase 1時点)

計画Report10節どおり、`PRODUCTION_WIRED`はPhase 3まで宣言しない。
Gate 3の各項目(PM_GOVERNANCE.md 2節)の現時点ステータス:

| 項目 | 状態 | 備考 |
|---|---|---|
| (a) Production正式初回経路 | 一部達成 | コード上の経路は実装済み(`level="b1_3v"`)、実運用未実施 |
| (b) retry/fallback/regenerationとの整合 | コードレベルで達成 | 既存primitiveを無改造で利用、Voice 3は専用fallbackなし・既存Human Review Lockへ委ねる設計を実装・テスト済み |
| (c) DEV/Trial-onlyではないこと | 達成 | 7節参照(Trial import 0件を機械確認) |
| (d) Production runtimeでの実発火 | **未達** | Phase 2待ち |
| (e) 必要testのPASS | 新規test達成、既存regressionは5節のSTOP事項あり | 新規36件PASS、regression4件failed中1件が新規(5節) |
| (f) runtime evidence | **未達** | Phase 2待ち |
| (g) 実際のmodel_id・routing確認 | **未達** | Phase 2待ち(runtime実行が前提) |
| (h) コスト影響評価 | Phase 1分は達成(¥0実測) | Phase 2見込み¥90〜150(計画Report5節基準) |
| (i)(j)(k) SSOT反映(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`) | **未達(意図的)** | 本タスクの書き込み範囲外、Phase 3でFable/ユーザーが実施 |
| (l) 必要なGit反映 | **未達(意図的)** | 本タスクではGit操作をしない(委任条件どおり)。Fableが後続タスクでcommit |
| (m) approved specとProduction挙動の一致 | 部分達成(構造レベル) | segment構造・Voice割当はTrial承認内容と一致を単体テストで確認済み。挙動一致の最終確認はPhase 2 runtime実行後 |

## 9. 残存課題6点(未解決、本Phaseでは対応していない)

計画Report7節の6項目(3V長文化/Tension再膨張/Local RewriteによるVoice
抽象化/Fact Checker A'負荷/Voice Distinctness維持/Audio structural gate
mandatory化)は、いずれも本Phase 1で**変更・解決していない**(deferred
維持または観測継続のまま)。特にLocal Rewriteの失敗モード(Trial-01/03で
計2回観測)は再発リスクが構造的に残ったままである。

またPhase 1固有の設計判断として、`run_scaffold_3v()`ではLedger
Deviation Check(`vfl01.run_deviation_check`、2V B1 Production runnerが
実施しているmonitoring専用の既存機構)を**実装していない**(3V Audio
Trial-01自体もこのチェックを実施していなかったため、Trial実績に忠実な
「正式移設」の範囲にとどめた判断)。これはTension再膨張の観測強化に
つながる項目であり、Phase 2以降で追加要否をユーザー判断へ委ねる。

## 10. Phase 2への前提・見込み費用

- 前提: (1) 5節のSTOP事項(新規regression failure)についてFable/
  ユーザー判断を得ること、(2) 4節のComment 2/3文言変更を人間レビューで
  承認すること、(3) Voice 3(Schedar)の技術的availabilityが実際に確認
  できること(不可の場合は計画Report10節Phase 2 STOP条件(b)により即
  STOP)。
- 記事: 3V Audio Trial-01/02基準記事(`er012_output/editorial_b_voices_
  3v_person_voice_trial_02/b1b_run01_attempt2/article.md`)を再利用する
  設計(Writer費用¥0)。同記事のKey Phrase選定済み出力
  (`er012_output/editorial_b_voices_3v_audio_trial_01/b1b/`)を`reuse_
  key_phrases_3v()`でhash照合のうえ再利用する設計を実装済み(記事
  hash一致を実測確認済み、2節)。
- 見込み費用: 計画Report5節・10節の基準どおり¥90〜150(3V Audio Trial
  実測¥93.82を上限目安)。Phase 1自体は¥0(実測)。
- 実行コマンド(Phase 2実施時の想定、本タスクでは未実行):
  `python er012_b_family_production_runner_01.py all b1_3v`。

## 11. Dangling Reference Check

- 新規名称(`voice_c`引数、`B_FAMILY_B1_3V_REQUIRED_SEGMENTS`、`run_tts_
  3v()`、`level="b1_3v"`等)はいずれも既存命名規約(`voice_a`/`voice_b`、
  `B_FAMILY_B1_REQUIRED_SEGMENTS`、`run_tts()`、`level="a2"`)の延長で
  あり、対の概念(2V版)が既に存在する。
  (`B_FAMILY_B1_3V_REQUIRED_SEGMENTS`のみ、命名規約はTrial側`build_
  required_structure_3v()`ではなく既存2V registry規約[`voice_a`/
  `voice_b`役割文字列]を優先し、3V専用の`voice_c`役割を追加する形へ
  統一した。Trial側の`voice_1/2/3`という別命名とは字面が異なるが、
  segment名自体[`point_one/two/three`]はTrial実績と完全一致させた。)
- 未承認・未実装のTrial-only仕様(Comment 2/3のTrial手動ドラフト文言、
  `TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED`)への参照はゼロ
  (`run_scaffold_3v()`は登録済みregistry Comment Contractのみを使用)。
- OPEN-129 opt-in構造Gateへの参照(`registry.build_required_structure`
  の`voice_c`経由呼び出し)は、`run_assembly_3v()`では**呼んでいない**
  (2V`run_assembly()`との対称性を保つ設計、mandatory化はdeferredの
  ままのため)。将来のevidence取得スクリプトからのみ利用可能。

## QCD(品質・費用・納期)

- **品質**: 新規機能はいずれも既存関数のコピー+最小拡張(既存primitiveの
  再利用)であり、2V/A-Family既存挙動への意図しない影響は新規offline
  test 36件+regressionで確認した。ただし5節のSTOP事項1件が未解決の
  ままである。
- **費用**: Phase 1実測¥0(API呼び出しなし)。Phase 2見込み¥90〜150
  (10節)。
- **納期**: 本セッション1回でPhase 1実装+テスト+regression確認まで
  完了(委任文のループ上限[初回+修正最大3回]の範囲内)。

## 12. Fable修正指示1回目(2026-09-10)

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01`(Fableから
の修正指示1回目)。並列稼働中の`PM-CLOSEOUT-CONSOLIDATION-68`(SSOT編集+
Git操作)・`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12`
(`er011_output/news_ledger_enrichment_ab_trial_12/`)と衝突する編集は行って
いない。本節はGit操作(add/commit/push)・SSOT(`OPEN_ITEMS.md`/
`DECISION_LOG.md`/`CURRENT_SPEC.md`)編集・`docs/pm/`編集をせず、API呼び出し
0回(費用¥0)で完了した。

### 12-1. 作業1: pinテストの1行修正(選択肢(a)採用、Fable承認済み)

ユーザー正式決定(2026-09-10)「共有Audio Gate=3Vに必要な`point_three`系
entryを最小追加」に基づき、`er012_editorial_b_family_production_phase1_
test_01.py::DisfluencyQaMandatoryDictB_FamilyA2Tests::test_existing_b1_
and_standard_a2_entries_unchanged`(旧8要素タプルをpinしていた既存テスト)
を、下記のとおり書き直した(該当テスト1メソッド内のみ、他ファイル・他
テストは無変更)。

```python
def test_existing_b1_and_standard_a2_entries_unchanged(self):
    # EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01(Fable修正指示1回目、
    # 2026-09-10): ユーザー正式決定により"B1"へ`point_three_heading`が追加された
    # (3Vに必要な最小追加、er003_v1_n3_01_assemble.py参照)。旧8要素タプルはその
    # まま部分集合として保持し、追加は`point_three_heading`1件のみであることを固定する。
    old_b1_entries = ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
                       "in_one_line", "point_one_heading", "point_two_heading")
    current_b1 = asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]
    self.assertEqual(current_b1[:len(old_b1_entries)], old_b1_entries)
    self.assertEqual(current_b1[len(old_b1_entries):], ("point_three_heading",))
```

「旧8要素が順序どおり含まれること」+「追加は`point_three_heading`のみ」の
2アサーションへ分割することで、テストの元々の意図(既存B1/A2 entryが不変で
あること)を保ったまま、3V配線による1件追加を許容する形にした。

**regression再実行結果**(実行環境: `.venv/Scripts/python.exe`、リポジトリ
直下venvにnumpy等の依存関係が揃っている。素の`python`コマンドは`numpy`
未導入のため別途venvを特定して使用した):

- 該当テストファイル単独実行: `er012_editorial_b_family_production_phase1_
  test_01.py`、33テスト全PASS(`Ran 33 tests in 0.033s / OK`、
  修正した`test_existing_b1_and_standard_a2_entries_unchanged`含む)。
- 新規オフラインtest 36件(`er012_editorial_b_family_voices_3v_production_
  wiring_phase1_test_01.py`)再実行: 全PASS(`Ran 36 tests in 0.096s / OK`)。
- 両ファイル合計69件も再実行: 全PASS(`Ran 69 tests in 0.109s / OK`)。
- `run_project_regression.py`(全体、対象102ファイル・2289件)再実行:
  `collected=2289 passed=2286 failed=3 errors=0 skipped=0`。**failed=3件は
  いずれも`er003_test_p2j_investigate.py`の既知failure**
  (`test_combined_equals_sum_of_er002_and_er003`/`test_p2h_reported_count_
  matches_er002_plus_er003_at_that_time`/`test_p2i_reported_count_matches_
  er003_at_p2i_era`、本タスク前から存在するテスト総数カウント照合の既知事象、
  本タスクと無関係)のみで、**新規failureはゼロ**(前回セッションの5節の
  STOP事項は本修正で解消)。
- 実行中の出力に`[B-FAMILY-PROD-RUNNER]`/`[B-FAMILY-VOICES-3V-PROD]`の
  cost計算ログが表示されるが、これは既存test群がmockで`main()`系関数を
  呼ぶ際の印字であり、前回保存済みの`run_project_regression_full_log.txt`
  と同一パターン(cost固定値28.64円、実際のAPI呼び出しではない)であることを
  比較確認した。API呼び出しは0回(費用¥0)。
- 証跡保存先(全て`er012_output/editorial_b_family_voices_3v_production_
  wiring_phase1_01/regression_evidence/`、既存の`run_project_regression_
  full_log.txt`/`run_project_regression_summary.json`/`new_offline_test_
  run_log.txt`はPhase 1時点のまま保持し、本修正の再実行分を`rerun_*`
  として追加保存): `rerun_full_log.txt`(全体regression実行ログ)・
  `rerun_summary.json`(`{"collected": 2289, "passed": 2286, "failed": 3,
  "errors": 0, "skipped": 0}`)・`rerun_new_offline_test_run_log.txt`
  (新規36件+修正済み33件、計69件のverbose実行ログ)。

### 12-2. 作業2: Phase 2「新テーマをProduction正式経路で記事→Support→
Audioまで」に不足している配線の調査(読み取り専用、実装なし)

**調査方法**: `er012_b_family_production_runner_01.py`
(管理ID`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`)・
`er012_b_family_voices_production_01.py`・`er012_b_family_editorial_type_
registry_01.py`のコード現物を読み、`DECISION_LOG.md`該当箇所
(`PM-CLOSEOUT-CONSOLIDATION-14`、2026-09-08「B-Family Phase 1の
`PRODUCTION_WIRED`確定」)と照合した。API呼び出し・runtime実行はしていない
(コード読解のみ)。

**1. 現行Production runner(2V経路)がどこまでProduction正式関数で通るか**

- **最重要の発見**: 現行`er012_b_family_production_runner_01.py`の2V
  B1/A2経路は、`ARTICLE_PATH`(B1)/`A2_SOURCE_DIR`(A2)という**既存の
  ハードコードされたファイルパス**(Trial-07で生成・ユーザーが試聴承認済みの
  既存記事、A2は2026-09-09承認済みsegment)から記事本文・Ledger・Key
  Phrase選定結果を**読み取るだけ**であり、**Research(Web検索)・Ledger
  作成・Writer(記事生成)・Key Phrase選定のいずれもこの経路のコード内には
  存在しない**。`prepare()`関数のdocstring自体に「記事生成[Writer]自体は
  Phase 2待ちのためこのrunnerの範囲外」と明記されている(コード冒頭コメント
  3〜27行、`prepare()`159〜167行、`prepare_a2()`1085〜1093行で直接確認)。
  `DECISION_LOG.md`の「B-Family Phase 1の`PRODUCTION_WIRED`確定」
  (2026-09-08)は、この「既存承認済み記事の音声化のみ」の範囲を指しており、
  「新テーマからの記事生成」を含むPRODUCTION_WIRED宣言ではないことを
  コード・SSOT両面で確認した。
- `run_fact_check_b1()`/`run_fact_check_a2()`(Fact Checker A'呼び出し
  関数)自体はコード上存在するが、`main()`の実行stage一覧(prepare/
  voice_check/kp_reuse/scaffold/tts/assemble/player/all)には**含まれて
  いない**(226行のコメントで意図的除外と明記、OPEN-131 runtime evidence
  取得専用の別スクリプトからのみ呼ばれる設計)。
- Key Phrase選定は2V B1/A2いずれも`reuse_key_phrases()`/`reuse_approved_
  a2_assets()`という**既存Trial/承認済み出力からのbyte/hash再利用関数**
  のみで、新規記事に対する選定ロジック自体はB-Family runner内に存在しない。
  ただし、共有Production関数`er003_v1_n3_01_scaffold_generate.py`
  (`sc`としてrunner内に既にimport済み)に`run_key_phrase_selection()`/
  `run_key_phrase_canonicalization()`/`run_key_phrase_redundancy_qa()`/
  `run_key_phrases()`という**A-Family(News/Discovery)向けの正式Production
  Key Phrase選定関数群が既に存在**しており、これをB-Family記事へ適用する
  経路は(今回確認した範囲では)未配線だが、関数自体は既存Production資産
  として再利用できる可能性が高い(詳細検証はPhase 1bで必要)。
- 結論: 2V B1は「Audio Gate通過」の意味では`PRODUCTION_WIRED`だが、
  「新テーマからの記事生成」の意味では**Research/Ledger/Writer/Key
  Phrase選定のいずれも未配線**であり、A2側も同様(`reuse_approved_a2_
  assets()`は承認済み記事の完全な音声・Key Phrase再利用が前提)。

**2. 3Vで不足しているもの**

- **3V Writer(3人物Voice本文生成)のProduction経路**: 存在しない。現状は
  Trialスクリプト`er012_editorial_b_voices_3v_person_voice_trial_02.py`
  (121KB、関数30個、`run_writer_stage()`・`build_candidate_prompt()`等)
  にのみ存在する。B-Family Production module(`er012_b_family_voices_
  production_01.py`)には`run_fact_checker`・parser・TTS body生成関数
  はあるが、Writer関数(記事本文生成)は2V/3Vいずれも**皆無**
  (関数一覧を機械確認、コード30行、`^def `検索で該当なし)。
- **3V用Ledger作成経路**: 存在しない。B-Family runnerが読むLedgerは
  いずれも既存ファイル(`LEDGER_PATH`固定パス)の読み取りのみ。Ledger新規
  作成関数(Researcher/Verification)は`er003_v1_en_direct_vfl_01_
  generate.py`(`run_researcher`/`run_verification`/`build_verified_
  ledger_text`)に存在するが、これは単一Narrator様式("master_full_text"
  模倣)向けのWriterプロンプト設計であり、B-Family Voices(複数人物視点)
  様式への転用可否は未検証。
- **Support(Comment 2/3の3V対応は済み、Preview/Key Phraseは?)**: 調査
  結果、`run_scaffold_3v()`(production_runner_01.py 702〜752行)は
  Comment 1-4に加え**Preview生成も含まれている**(`b1s.PREVIEW_ROLE`
  経由、既存Production Prompt無変更で呼び出し済み)ため、Previewは既に
  3V対応済みと確認した。Key Phraseは`reuse_key_phrases_3v()`(676〜699行)
  で、2V同様「既存Trial出力(3V Audio Trial-01)からのhash照合済み再利用」
  のみであり、**新規記事に対するKey Phrase選定ロジックは3Vにも存在しない**
  (2Vと同一の制約)。
- **Ledger Deviation Check(`run_scaffold_3v()`未実装)**: 前回報告
  (9節)のとおり、`run_scaffold_3v()`は`vfl01.run_deviation_check`を
  呼んでいない。今回の再確認でも同様(702〜710行のdocstringに明記)。
- **Fact Checker A'のVoice別事実帰属opt-in(`FACT_ATTRIBUTION_MODE_
  DEFAULT`)の3V扱い**: `FACT_ATTRIBUTION_MODE_DEFAULT = False`
  (registry 343行)は`EDITORIAL_TYPES["b_family_voices"]`単一の
  `fact_attribution_mode`フラグであり、`b1`(2V)・`b1_3v`(3V)の両
  sub-config(`config["levels"]["b1"]`/`config["levels"]["b1_3v"]`)に
  対して**共通の1つのフラグ**が適用される設計(`is_fact_attribution_
  mode_enabled()`はeditorial_type単位で判定、level単位の分岐なし、
  425〜458行で確認)。3V専用の別扱いは存在しない(既定OFF、Voice数に
  かかわらず同一挙動)。
- **Tension尺・Analytical Leakage・Voice distinctnessの観測ログ出力**:
  `er012_b_family_production_runner_01.py`・`er012_b_family_voices_
  production_01.py`のいずれにも該当する観測ログ出力コードは**存在しない**
  (`leakage`/`tension_length`/`distinctness`等のキーワードで機械grep、
  0件)。これらはいずれもTrial側の評価専用スクリプトでのみ観測されており、
  Production経路には一切配線されていない。OPEN-131 Fact Attributionの
  前例(`er012_open131_fact_attribution_production_wiring_evidence_01.py`
  という専用evidence取得スクリプトをmain()経路とは別に用意する設計)を
  踏襲すれば、Production main()自体を変更せずに観測データだけ追加取得する
  設計は技術的に可能と見込む。

**3. 「Phase 1b: 3V Writer/Ledger/Support経路のProduction配線+offline
test(¥0)」として追加実装する場合の見込み**

- **変更ファイル(見込み)**: (a)Ledger作成: 新規または`er003_v1_en_
  direct_vfl_01_generate.py`ベースの3V対応版(Researcher/Verification
  自体はNarrator数に非依存の可能性が高く流用余地あり、Writerプロンプト
  部分のみ3V専用書き換えが必要)、(b)3V Writer: `er012_editorial_b_
  voices_3v_person_voice_trial_02.py`から`run_writer_stage()`相当の
  正式移設(前回Phase 1で`run_tts_3v()`を移設した際と同様の手法、
  ただし対象コードが121KB・関数30個とTTS移設[単一関数]より大幅に大きい)、
  (c)Key Phrase選定: `er003_v1_n3_01_scaffold_generate.py`の既存
  `run_key_phrases()`をB-Family記事向けに呼び出す新規glue関数、
  (d)`er012_b_family_production_runner_01.py`: `main_b1_3v()`の前段に
  Research/Ledger/Writer/Key Phrase選定stageを追加する新規分岐、
  (e)新規offline testファイル1本(前回同様Trial-onlyへの依存ゼロを機械
  確認するAST test含む)。
- **規模(見込み)**: 前回Phase 1(registry+305〜440行×3ファイル)より
  大きい。特に3V Writerプロンプト自体の移設・検証(Voice distinctness
  維持・Analytical Leakage再発防止の作り込みがTrial-05/06で反復修正
  されていた経緯)が最大のリスク要因であり、単純なコード移設では済まない
  可能性が高い(前回9節で述べた残存課題1・3・5がそのままPhase 1bの
  技術的難所になる)。
- **リスク(見込み)**: (i)3V Writerプロンプトを移設する過程で、Trial側で
  何度も反復修正された「調査結果整理としてWriterが動いてしまう」失敗
  モード(Trial-04/05等で複数回観測)が、Production配線後の新テーマ
  (宿題/自由時間)で再発する可能性、(ii)Ledger作成をB-Family Voices
  様式向けに転用する際、既存Direct VFL Writerプロンプトとの様式差異
  (単一Narrator前提 vs 複数人物視点)を吸収する設計が必要になる可能性、
  (iii)Key Phrase選定glue関数の新規動作確認(A-Family向け関数をB-Family
  記事へ初めて適用するため、既存A-Family regressionへの影響有無の確認が
  追加で必要)。
- **STOP条件(見込み)**: 既存STOP条件(a)〜(d)(regression新規failure・
  共有ファイル変更量超過・cost超過・Trial専用実装への依存残存)に加え、
  (e)3V Writerプロンプト移設後、新テーマでAnalytical Leakage Check相当の
  品質劣化が観測された場合、(f)Ledger作成の3V転用がFact Safety機構
  (既存Ledger逸脱検出)と整合しない挙動を示した場合、は追加STOP条件と
  見込む(いずれもFable/ユーザー判断が必要な性質の問題であり実装側の
  独自判断では回避しない)。
- **見込みセッション数**: Phase 1(本タスク)が委任1回(修正込み)で完了
  した規模感より明確に大きく、Ledger/Writer移設・Key Phrase glue・
  offline test作成・regression確認を1セッションに収めるのは困難と見込む。
  **2〜3セッション程度(見込み、実装内容の複雑度次第で変動)**が妥当な
  見積もりと考える。
- **Phase 2(新テーマ3V記事1本)・2V比較記事1本の見込み費用**: ユーザー
  提示の参考値(Discovery Trial-11: Ledger¥55+記事¥62、3V Audio Trial
  実測¥93.82)を踏まえると、新テーマ3V記事1本は「Ledger作成(Web検索
  含む)+Writer記事生成+Fact Checker A'+Local Rewrite(発生した場合)+
  Support(Comment/Preview)+TTS+ASR」を合算する必要があり、**見込み
  ¥150〜250程度**(Ledger¥55+記事¥62程度の合計¥117に、3V Audio生成
  ¥93.82を加えた単純合算で¥211、Fact Checker A'・Local Rewrite再発生分の
  上振れを見込んだ幅、確定額ではない)。2V比較記事1本は3V相当より本文
  生成量が少ない分やや低く、**見込み¥100〜180程度**(同様に単純合算
  ベースの見込み、確定額ではない)。

**4. 2V比較記事(新テーマ)が現行2V Production経路で完走できるか**

**できない**。1節の調査結果のとおり、現行2V B1/A2 Production runnerは
Research/Ledger作成・Writer(記事生成)・Key Phrase選定のいずれも経路
内に存在せず、既存の承認済み記事を読み取ることを前提とした設計
(`ARTICLE_PATH`/`A2_SOURCE_DIR`のハードコード)である。不足配線を列挙
すると: (a)Research/Ledger作成(2V用Writerプロンプトは`er012_editorial_
b_voices_trial_*.py`にのみ存在し、Production module未移設)、(b)Writer
本体(2V記事生成関数がB-Family Production moduleに存在しない、3Vと
同じ制約)、(c)Key Phrase選定glue(A-Family既存関数の適用未検証)。
つまり2V比較記事についても、Phase 1bに準ずる配線作業(2V Writer移設)が
別途必要であり、「2Vは既にPRODUCTION_WIREDだから新テーマでもすぐ通る」
という前提は**誤り**であることが今回の調査で判明した。

**5. 選択肢整理**

- **(A) Phase 1b実装(3V+2V Writer/Ledger/Support配線)→Phase 2新テーマ
  3V記事1本→2V比較記事1本**(ユーザー決定に最も忠実): 費用はPhase 1b
  自体は¥0(オフライン実装+test)、Phase 2実行時に3V記事¥150〜250見込み+
  2V比較記事¥100〜180見込み(3節)。期間はPhase 1bだけで2〜3セッション
  見込み、Phase 2実行(記事生成→Audio Gate)も別途1セッション以上必要。
  リスクは3節のとおり(3V Writerプロンプト移設時の失敗モード再発、Ledger
  転用整合性)が最大。**メリット**: ユーザー決定(新テーマ・Production
  正式経路)へ完全準拠し、実際のProduction配線状態でのruntime evidence
  (3V追加観測含む)が得られる。
- **(B) Phase 2は既存Trial記事再利用でruntime evidenceのみ先に取得し、
  新テーマは別途**(前回Phase 1報告10節の前提、今回ユーザー決定とは
  不一致と判明済み): 費用は3V Audio Trial実測¥93.82を上限目安とする
  低コスト(¥90〜150見込み)、期間は1セッション程度で完了見込み。
  リスクは低い(既存承認済み記事の再音声化のみ)が、**ユーザー正式決定
  (新テーマ・Production正式経路までの完走)に反する**ため、そのまま
  採用すると手戻りになる可能性が高い。
- **(C) その他**: 例えば「Phase 1bをWriter/Ledgerのみ先行実装し、Key
  Phrase選定glueは既存Trial出力のhash再利用のまま新テーマ記事に暫定
  適用する(Key Phrase選定ロジック自体の正式配線は別タスクへ分離)」
  というスコープ縮小案も考えられるが、新テーマ記事はTrial-07/3V Audio
  Trial-01の記事とは別内容のためhash不一致となり、この暫定適用は技術的に
  成立しない(reuse関数はfail-closedでhash不一致時にRuntimeErrorを送出
  する設計、`reuse_key_phrases()`/`reuse_key_phrases_3v()`192〜196行・
  680〜684行で確認)。したがって(C)は「Key Phrase選定glueも含めて
  Phase 1bに含める」以外の現実的な縮小余地は乏しいと判断する。

**推奨**: (A)を推奨する。理由: (i)ユーザーが2026-09-10に明示的に
「既存Trial記事の再利用ではなく新テーマで」と決定しており、(B)はこの
決定と正面から矛盾する、(ii)Key Phrase選定reuse関数がfail-closed設計の
ため(C)のような部分的回避も技術的に困難、(iii)Phase 1bのコスト自体は
¥0(オフライン実装)であり、費用リスクはPhase 2実行段階(記事生成〜
Audio Gate完走)に限定される。ただし規模・リスクが前回Phase 1より
明確に大きいため、**Phase 1b着手の可否・スコープ(Ledger/Writer移設の
詳細設計)は実装開始前にFable/ユーザーの承認を得ることを推奨する**
(本タスクでは調査のみに留め、実装はしていない)。

---
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EqG9xnr2dZhshz85bFW4Kt
