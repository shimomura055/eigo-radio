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

## 13. Fable修正指示2回目(2026-09-10、Opus L2レビュー指摘への対応)

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01`(修正指示
2回目)。出典: Opus L2レビュー(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-
WIRING-PHASE1-01-OPUS-L2-REVIEW-01`)。いずれも承認済み設計の範囲内での
是正であり、新原則の追加ではない。API呼び出し0回(費用¥0)。

### 13-1. Voice衝突ガード(HIGH、指摘#1)

`registry.VOICE_FALLBACK["voice_a"]`と`registry.VOICE_ASSIGNMENT["voice_c"]`
が同一("Schedar")のため、Voice A(Algieba)が技術的に利用不可でfallback
した場合、解決後のVoice AとVoice Cが同じ声(Schedar)になっていた
(Voice 1とVoice 3が同一の声で発話される、旧仕様では黙認)。

`er012_b_family_voices_production_01.py::resolve_voice_names_3v()`を修正:
Voice A/B/C解決後、3声がpairwiseに異なるかを検証し、衝突があれば独自の
代替声を発明せず`RuntimeError`(prefix `[VOICE_COLLISION_STOP]`、衝突ペア・
解決済み3声・reasonsを含む)で明示停止する。呼び出し側
`er012_b_family_production_runner_01.py::voice_check_3v()`はこの例外を
`audit/voice_resolution.json`へ`status="VOICE_COLLISION_STOP"`として記録
した上で再送出し、パイプライン全体を停止する(overrideしない)。

既存テスト`test_voice_a_unavailable_still_uses_existing_fallback_logic`を
`test_voice_a_unavailable_causes_collision_with_voice_c_and_stops`へ改名・
書き換え、衝突時はSTOPすることを期待値とした(ユーザー決定「Voice 3に
専用fallbackなし、使用不可時は止める」と整合)。

### 13-2. content integrity checkのProduction module正式移設(HIGH、指摘#2)

Trial `er012_editorial_b_voices_3v_audio_trial_01.py`の`run_content_
integrity_check()`(L879-903付近、6区切りparserが本文を正しく割り当てた
証跡)を、`er012_b_family_voices_production_01.py::run_content_integrity_
check_3v()`へロジックそのまま正式移設した(pure関数化、ファイルI/Oは
呼び出し側の責務に分離)。Trial側は無変更のまま(参照のみ)。

`build_parts_3v()`の消費側`er012_b_family_production_runner_01.py::
run_scaffold_3v()`で必ず実行し、結果を`audit/content_integrity_3v.json`
へ記録する。`all_section_bodies_verbatim_from_article`がFalse(NG)の場合は
`RuntimeError`(prefix `[CONTENT_INTEGRITY_STOP]`)で明示停止する。

新規テストで、移設後の関数がTrial側の同名関数と同一入力で同一出力になる
ことを固定した(`RunContentIntegrityCheck3vTests::test_matches_trial_
function_output_for_same_input`、Trialをimportするのはテストのみ、
Production module自体はimportしない)。

### 13-3. `build_required_structure()`踏み台の除去(指摘#3)

2点を修正した(`er012_b_family_editorial_type_registry_01.py::build_
required_structure()`):

1. `level="a2"`へ`voice_c`を指定すると、従来は黙って無視されていた
   (A2は3V未対応のため気づかずに2V扱いされる踏み台)。`voice_c is not
   None`の場合に`ValueError`を送出するよう変更。
2. runner CLIの`level="b1_3v"`文字列と、本関数の従来呼び出し規約
   (`level="b1"`+`voice_c=<str>`)が非対称で、`level="b1_3v"`をそのまま
   渡すと`voice_c`の有無に関わらず`ValueError("unknown level")`になる
   踏み台だった。`level="b1_3v"`を薄いaliasとして正式に受理し(`voice_c`
   必須を強制した上で`level="b1"`へ正規化)、`voice_c`省略時は明示的に
   `ValueError`で止めるようにした(黙って2V相当へfallbackしない)。

新規テストクラス`BuildRequiredStructureB13vAliasAndA2VoiceCGuardTests`
(4件)で固定した。

### 13-4. Comment 3役割行の言い換え(指摘#4、ユーザー承認済み汎用化の範囲内)

`VOICES_COMMENT_3_ROLE`内の「役割:」行(タイトル行ではない、実際にLLMへ
渡る役割説明文の1文)のみ、「どちらが正しいか」→「どの声が正しいか」へ
言い換えた。タイトル行(「その間に流す、Comment 3(役割: ...」)と
Comment 4本文はユーザー判断待ちのため本修正では変更していない。既存
テスト(`test_comment_3_role_markers_preserved`等)は継続PASS。

### 13-5. Comment 2/3汎用文言のA2 Production波及(指摘#5、人間レビュー推奨)

`VOICES_COMMENT_2_ROLE`/`VOICES_COMMENT_3_ROLE`は`registry.COMMENT_ROLES`
経由でB1(2V/3V)・A2いずれの経路からも共有される単一の定数であるため、
Phase 1(修正指示1回目)でのVoice数非依存汎用化、および本修正指示2回目の
13-4の言い換えは、いずれも`er012_b_family_voices_a2_production_01.py`
(485〜499行、`run_scaffold_a2()`)の出力(日本語Comment 2/3生成)へも
同様に波及する。A2側は個別のComment定数を持たず、B1と全く同じ
`registry.COMMENT_ROLES`辞書を参照するため、意図した変更でありB1/A2間の
不整合ではない。

### 13-6. regression結果

- `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`
  単独: 46テスト全PASS(`Ran 46 tests in 0.094s / OK`、新規12件+改修1件を
  含む)。
- `--pattern "er012_*b_family*test*.py"`(B-Family関連全体): 79テスト全
  PASS(`collected=79 passed=79 failed=0 errors=0 skipped=0`)。
- 証跡: `er012_output/editorial_b_family_voices_3v_production_wiring_
  phase1_01/regression_evidence/phase1b_offline_test_run_log.txt`
  (Part 2実装後の最終48テストログと共通、Part 1修正分もここに含まれる)。

## 14. Phase 1b(EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-01、
不足配線のみ)

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-01`。定義
(ユーザー確定2026-09-10、Fable経由): 「既にユーザー承認済みの3V仕様を、
Production正式初回経路で実際に記事生成できるようにするための不足配線
のみ」。新しい3V仕様を作る工程にはしない。API呼び出し0回(費用¥0)。

### 14-1. 設計分類(移設可 / STOP)

12-2節(修正指示1回目の事前調査)の続きとして、Trial-02(3V Writer経路:
Research→Ledger作成→Writer→Fact Checker A'→Local Rewrite→Key Phrase
選定)・2V相当Trial・関連の既存Production共有module(er008/er010系)の
コード現物を読み、各項目を「既存承認仕様の正式移設(可)」「STOP(新仕様が
必要)」に分類した。

| # | 項目 | 分類 | 根拠 |
|---|------|------|------|
| 1 | Ledger作成(Research、Perplexity sonar-pro Stage1B/2B) | **STOP** | `er012_ai_screening_ledger_trial_01.py`自身のコメントが明記するとおり、B-Family Voice Ledgerの実際の先例(Trial-04〜07)はいずれも`_perplexity_call()`パターンを**各Trialファイル内へ毎回再実装**したものであり、共有Production primitiveとして一度もGate通過・formalize(共通moduleへの集約)されたことがない。「到達してよいStatusはVALIDATED/REJECTED/USER_DECISION_REQUIREDのみ、Production採用判断はしない」と明記されている。これを今回Production化することは、ad-hocなTrial-copy-pasteパターンを初めてProduction primitiveとして新設する判断になり、「不足配線」の範囲を超える。 |
| 2 | Writer本体呼び出し(Lane A共有`gen`/`vfl01.run_writer_no_search`) | 部分的に**移設可**、ただし単独では機能しない | Trial-02は`import er003_v1_n3_01_articles_generate as gen`でLane A共有Writer(既存Production、A-Family全記事で使用中)を使うが、その内部の汎用構造ゲート(`validate_point_structure()`、H3見出し数=2を無条件要求)が3V(H3=3)と非互換なため、Trial-02はLane A Writerのラッパー関数(`gen._generate_and_compress_article()`)を経由せず、より低レベルの`vfl01.run_writer_no_search()`を直接呼ぶ回避策を取っている。この非互換はSSOT `OPEN-132`として追跡中・**未解決**とTrial自身のコメントに明記されている(「変更にはProduction側の承認が必要」)。 |
| 3 | Writer retry上限(`MAX_WRITER_ATTEMPTS=3`、是正再実行ループ) | **STOP** | Phase 1 registry(`er012_b_family_editorial_type_registry_01.py::PHASE2_PENDING_NOTES`)が「B-Family専用Writer retry上限(3回)は...USER_DECISION_REQUIREDのまま未確定」と明記(既にProduction code内のコメントとして存在、今回新たに発見したものではない)。Trial側コメントが「既存上限」と称していても、これはTrial-01からTrial-02への内部一貫性であり、Production採用の正式決定ではない。 |
| 4 | Analytical Leakage Check / Point Overlap QAの**gate化**(pass/failでWriter出力をブロックするか) | **STOP**(gate化のみ)。**record-onlyは可** | 同じくregistry `PHASE2_PENDING_NOTES`が両者とも「B-Family専用扱い...USER_DECISION_REQUIREDのまま未確定」と明記。Fable指示のとおり、既存算出関数を**記録専用**(pass/fail判定なし)として`audit/`へ書き出すことは新QA基準の追加ではないため許容し、pipelineをブロックする「gate」としての採用のみSTOPする。 |
| 5 | Ledger Deviation Check(`vfl01.run_deviation_check`、Support文への適用) | **移設可** | 2V `run_scaffold()`が既に同一関数を同一の使い方(monitoring専用、非gate)で実行済み(Phase 1から存在)。3Vへ同一パターンをそのまま適用するのみで、新しい判定ロジック・新しい閾値は一切追加しない。「既存監視機構の接続」。 |
| 6 | OPEN-131 Fact Attribution(`registry.build_voice_attribution_block`+`run_fact_checker`) | **移設可**(ただし2V精度に合わせ`main()`のstage一覧へは含めない) | 既存関数はvoice数非依存(article_text単位で動作)。2V側も`run_fact_check_b1`/`run_fact_check_a2`は`main()`のstage一覧に含まれておらず(意図的除外、Phase 2待ちと既存コメントに明記)、3V側もこの既存precedentに合わせ、今回はstage一覧へ追加しない(2Vとの対称性維持、新しい包含判断をしない)。 |
| 7 | Key Phrase選定(`er003_v1_n3_01_scaffold_generate.run_key_phrases`等) | **移設可**(関数自体は既存、ただし呼び出す新規記事が無いため今回は未使用) | A-Family(News/Discovery)が既に使っている既存Production関数であり、article_text単位で動作するためB-Family固有の新設は不要。ただし本Phase 1bでは新規記事生成(項目1・2・3のSTOP)が無いため、既存の承認済み3V記事に対して今これを実行しても得られる情報がない(hash再利用[`reuse_key_phrases_3v`]で既に確定済みの結果と同じになるだけ)。Phase 2でWriter STOPが解消され新規記事が生成された時点で接続する。 |
| 8 | Tension segment語数(record-only観測ログ) | **移設可**(実装済み) | `ab01.compute_word_count`(既存Production、A-Family Lane Aでも使用中)を再利用するのみ。pass/fail判定を持たない純粋なテキスト計算(¥0)。 |
| 9 | Voice distinctness(pairwise、`direction_agreement_rate`等) | 関数設計は**移設可**、実行は**今回未実施** | LLM呼び出しを伴う(¥0制約下の本セッションでは実行不可)。かつ既存の承認済み3V記事(Trial側で既にPASS済み)に対して再実行しても新しい情報が得られない。Phase 2で新規記事が生成された時点で、Trial側の算出関数(`run_pairwise_distinctness_check_single`等)をrecord-onlyとして移設・実行する設計。 |
| 10 | Local Rewrite回数・語数増分(record-only観測ログ) | **今回対象外**(自動Local Rewrite実行が項目3のSTOPに従属) | Local Rewrite自体はLane A Writer内部で既に使用されている既存Production機構(`er010_ledger_local_rewrite_09`、無変更)だが、Writer retry/QAループ(項目3)がSTOPのため、本Phase 1bでは新規にLocal Rewriteを発火させる経路がない。 |

### 14-2. 結論: `writer`ステージの新規実装はSTOP

項目1(Ledger作成)・項目3(Writer retry上限)は、いずれかを除いても
「新テーマから記事を生成する」という`writer`ステージの中核目的を達成
できない(Ledgerなしでは事実根拠がなく、retryなしでは技術失敗時に停止
するのみで実用に耐えない)。加えて項目2はLane A共有Writerの汎用構造
ゲートとの非互換(OPEN-132、未解決)を含む。この3点はいずれも「除いて
進める」ことができない(Fable指示2節「除けない場合は実装せずSTOP報告」に
該当)。

したがって、**runnerへの新規`writer`ステージ追加、および`all`ステージへの
「writer→support→tts→assemble」の組み込みは実装していない**。これらは
STOPとして報告し、実装しない。

### 14-3. 実装した範囲(STOPを除く、安全に独立して進められる不足配線)

STOPと無関係に独立して実施でき、Fableが明示的に許可した範囲(「既存監視
機構の接続」「record-only観測ログ、新QA基準は作らない」)のみ、既存の
承認済み3V記事(`ARTICLE_PATH_3V`)に対して実装した:

1. **Ledger Deviation Check接続**(表14-1項目5): `er012_b_family_
   production_runner_01.py::run_scaffold_3v()`のsignatureへ`ledger_text`
   引数を追加し、2V `run_scaffold()`と同一の`vfl01.run_deviation_check`
   呼び出しを追加した(monitoring専用、非gate)。Ledger入力元は新規定数
   `LEDGER_PATH_3V`(2V `LEDGER_PATH`と同じ設計、既存Trial成果物
   `er012_output/ai_screening_ledger_trial_01/research/verified_fact_
   ledger.txt`を読み取り専用のまま参照、ハッシュ照合なし=2V precedentと
   同一)。結果は`audit/support_ledger_deviation_3v.json`へ保存。
   `main_b1_3v()`の`scaffold`/`all`stageから自動実行される。
2. **Tension segment語数のrecord-only観測ログ**(表14-1項目8):
   `er012_b_family_voices_production_01.py::compute_tension_segment_
   word_count_3v()`を新設(既存`ab01.compute_word_count`を再利用する
   pure関数)。`run_scaffold_3v()`から呼び出し、`audit/tension_scale_3v.
   json`へ保存。

いずれも既存2V経路の関数・挙動は無変更。`run_scaffold_3v()`のsignature
変更(`ledger_text`引数追加)に伴い、呼び出し元`main_b1_3v()`と既存
テスト2件を追随修正した。

### 14-4. 変更ファイルと差分規模

- `er012_b_family_voices_production_01.py`: 関数2件追加(`resolve_voice_
  names_3v`衝突ガード追加・`run_content_integrity_check_3v`新設・
  `compute_tension_segment_word_count_3v`新設)、import 1件追加(`ab01`)。
- `er012_b_family_production_runner_01.py`: `voice_check_3v()`に
  try/except追加、`run_scaffold_3v()`signature変更+本文追加(content
  integrity check呼び出し+Ledger Deviation Check+Tension観測ログ)、
  `LEDGER_PATH_3V`定数追加、`main_b1_3v()`のscaffold呼び出し1箇所修正。
- `er012_b_family_editorial_type_registry_01.py`: `build_required_
  structure()`にvalidation 2件追加、`VOICES_COMMENT_3_ROLE`内1行の
  言い換え。
- `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`:
  新規テストクラス5件・既存テスト2件改修(合計48テスト)。
- 新規ファイル・新規ステージ追加は**していない**(`writer`ステージは
  STOPのため未実装)。

### 14-5. Trial import 0件の確認

`NoTrialScriptModuleLevelImportTests`(既存3テスト、AST解析でtrial文字列を
含むモジュールレベルimportが無いことを機械確認)は今回も無変更のまま
PASS。`RunContentIntegrityCheck3vTests::test_matches_trial_function_
output_for_same_input`のみテストコード内でTrialをimportするが(Production
moduleではなくテストファイル、既存precedentと同じ扱い)、Production 3
module(registry/production_01/production_runner_01)はいずれもTrialを
一切importしていない。

### 14-6. regression結果

- `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`
  単独: **48テスト全PASS**(`Ran 48 tests in 0.101s / OK`)。
- `--pattern "er012_*b_family*test*.py"`: **81テスト全PASS**
  (`collected=81 passed=81 failed=0 errors=0 skipped=0`)。
- `run_project_regression.py`(全体、対象106ファイル・2301件、Part 1
  修正+Phase 1b実装後の最終1回のみ実行): `collected=2301 passed=2298
  failed=3 errors=0 skipped=0`。**failed=3件はいずれも`er003_test_p2j_
  investigate.py`の既知failure**(本タスク前から存在するテスト総数カウント
  照合の既知事象、本タスクと無関係)のみで、**新規failureはゼロ**。
- API呼び出しは0回(費用¥0、regression実行時のcostログ表示は既存test群が
  mockで`main()`系関数を呼ぶ際の印字であり実際のAPI呼び出しではない、
  12-1節と同じ確認方法)。
- 証跡保存先(いずれも`er012_output/editorial_b_family_voices_3v_
  production_wiring_phase1_01/regression_evidence/`):
  `phase1b_offline_test_run_log.txt`(48テストverboseログ、Part 1修正+
  Phase 1b実装後の最終状態)・`phase1b_fix2_full_regression_log.txt`
  (全体regression実行ログ)・`phase1b_fix2_summary.json`
  (`{"collected": 2301, "passed": 2298, "failed": 3, "errors": 0,
  "skipped": 0}`)。

### 14-7. Dangling Reference Check

- `run_scaffold_3v(`の全呼び出し元を機械確認(3箇所: 定義・`main_b1_3v()`
  呼び出し・Trial側の同名別関数[別モジュール、無関係]): 全て新signature
  (`ledger_text`引数追加)に追随済み。
- `resolve_voice_names_3v(`の全呼び出し元(定義・`voice_check_3v()`)を
  確認: 例外ハンドリング追加済み。
- `build_required_structure(`の全呼び出し元(定義・`er011_open129_
  structural_completeness_production_wiring_evidence_01.py`2箇所)を
  確認: いずれも`voice_c`未指定のためValueError追加の影響を受けない。
- `LEDGER_PATH_3V`が指す既存ファイル(`er012_output/ai_screening_ledger_
  trial_01/research/verified_fact_ledger.txt`)の実在をファイルシステムで
  確認済み(368行、25546バイト)。

### 14-8. Phase 2で記録するruntime evidence項目(Opus論点5、13項目)

Phase 1bはWriterステージ自体がSTOPのため、以下はいずれも**Phase 1bでは
未取得**(¥0制約下・新規記事が存在しないため取得不能)であり、Phase 2
(Writer STOP解消後、新規記事生成時)で取得する対象として整理した:

1. 実行同一性(同一入力での再現性)
2. model_id・routing実測(実際に使用されたモデルIDの記録)
3. Voice 3値(Voice A/B/C)が相互に異なることの実測確認(本修正指示2回目で
   衝突ガードは実装済み、実際の衝突検知イベントの有無はPhase 2実行時に
   観測)
4. 16 segment構造の実測確認
5. mandatory disfluency 9件の実測確認
6. OPEN-121・OPEN-122(repetition QA・connected speech equivalence
   layer)有効化の実行時記録
7. Human Review Lock非発火の確認(発火した場合はoverrideせずSTOP)
8. OPEN-129 opt-in構造Gate(`build_required_structure`)発火+1回PASSの
   実測(現状3V経路からは未呼出のまま、Phase 2で呼び出すかはFable/ユーザー
   判断が必要)
9. 音声実測(実際に生成された音声の尺・品質)
10. Key Phrase再利用/選定の明示記録
11. 費用実測
12. Comment 1-4実出力全文の記録
13. SSOT前提(OPEN-131/OPEN-129/OPEN-132等)との整合確認

### 14-9. Phase 2手順(Writer STOPの解消を前提)

Phase 2(新テーマ「Should schools replace some homework with more free
time?」Voice=Student/Parent/Teacher、3V記事1本+2V比較記事1本)は、本
Phase 1bのSTOP事項(Ledger作成のProduction化・Writer retry上限の決定・
OPEN-132構造ゲート非互換の解消)がユーザー/Fableにより解決されない限り
着手できない。解決後の想定手順:

1. STOP事項(表14-1項目1・2・3)それぞれについて、Fable/ユーザーの決定を
   得る(Ledger作成primitiveの正式化可否・Writer retry上限の数値・
   OPEN-132構造ゲートの扱い)。
2. 決定に基づき`writer`ステージを実装(本Phase 1bと同じくSonnet委任、
   ループ上限に従う)。
3. `all`ステージで完走させる。`GATE_BLOCKED`等のSTATUS発生時はoverride
   せずSTOPし、Fable/ユーザーへ報告する(既存安全装置を独自判断で回避
   しない)。
4. 14-8節の13項目のruntime evidenceを取得し、REPORTへ記録する。
5. Human Review Lockが必要な場合は`record_human_approval()`等による
   再承認をユーザーへ依頼する(代行しない)。

### 14-10. 見込み費用

Phase 1b自体(本節の範囲)は¥0(オフライン実装のみ、API呼び出しなし)。
Phase 2実行時の見込み費用は12-2節3項の既存見積り(新テーマ3V記事1本
¥150〜250程度、2V比較記事1本¥100〜180程度、いずれも確定額ではない)を
維持する(本Phase 1bでは新たな見積り材料は得られていない)。

## 15. Fable修正指示3回目(Opus commit前レビュー対応)

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01`(Fableから
の修正指示3回目=最終)。出典: Opus L2レビュー(commit前、Production core
差分・2V regression・Dangling Reference限定、Blocking=なし)。いずれも
承認済み設計の範囲内での是正であり、新原則の追加ではない。SSOT
(`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`含む)は未編集(並列T-1タスク
使用中のため)、Git操作(add/commit/push)は未実施、API呼び出し0回
(費用¥0)。

### 15-1. content integrity checkの挙動追加の明記(指摘A)

Trial `run_content_integrity_check()`はTTS後にrecord-onlyで結果を保存
するのみ(pass/fail判定でパイプラインを止めない)だったのに対し、
Production移設版`run_content_integrity_check_3v()`の消費側
`run_scaffold_3v()`(13-2節)は、scaffold内で`all_section_bodies_
verbatim_from_article`がFalseの場合に`RuntimeError([CONTENT_INTEGRITY_
STOP])`でfail-closed停止する。これはTrialには無かった挙動追加であり、
2V経路には同等のgateが存在しない(3Vのみfail-closed、3Vが3声pairwise
distinctness等より複雑な構造のため安全側に倒した意図的な非対称、既存
安全装置の追加除去ではない)。

あわせて、`run_content_integrity_check_3v()`内の`all_ok`判定は、Trial版
(`er012_editorial_b_voices_3v_audio_trial_01.py::run_content_integrity_
check()`)と同一ロジックのまま移設しており、`hook_part1_and_part2_
reconstruct_hook_body`(Hook分割チェック)と`key_phrase_used_form_
appears_in_article`(Key Phrase不在チェック)の2項目は`all_ok`から明示的に
除外されている(`checks`辞書・`kp_used_forms_in_article`辞書へは記録する
が、STOP判定には含めない)。したがってHook分割ミス・Key Phrase不在は
Production版でも記録のみでSTOPしない(Trialと同一の粒度、実装コード
無変更で移設済み、本節で挙動を新たに追加したものではない)。

### 15-2. scaffold_summary.json(3V)へdeviation_overall_status追加(指摘B)

2V `run_scaffold()`消費側(`main()`のscaffold stage、L1511-1513)が
`audit/scaffold_summary.json`へ`deviation_overall_status`
(`scaffold_result["deviation"].get("overall_status")`)を含めているのに
対し、3V側`main_b1_3v()`のscaffold stageは`support_status`のみで
`deviation_overall_status`を含んでいなかった(Phase 1bでLedger Deviation
Checkを接続した際の対称化漏れ)。2Vと同一形で`deviation_overall_status`を
追加した(`er012_b_family_production_runner_01.py::main_b1_3v()`)。

### 15-3. `LEDGER_PATH_3V`と記事側Trial-02のLedger同一性の明記(指摘C)

`LEDGER_PATH_3V`(`er012_output/ai_screening_ledger_trial_01/research/
verified_fact_ledger.txt`)は、`ARTICLE_PATH_3V`が指す記事
(`er012_editorial_b_voices_3v_person_voice_trial_02.py`の出力、L132-133
付近で同一Ledgerパスを参照)と同一のLedgerである(記事本文の事実的根拠と
Deviation Check対象Ledgerが一致していることの確認、Phase 1bで既に接続
済みの実装内容自体は無変更)。

### 15-4. registryコメントの正本宣言表現への修正(指摘D)

`er012_b_family_editorial_type_registry_01.py`の`B_FAMILY_B1_3V_
REQUIRED_SEGMENTS`直前コメント(旧: 「Trial側の暫定正本はregistry側へ
統合され(2重定義解消)」)を、「Trial側`build_required_structure_3v()`/
`run_content_integrity_check()`はいずれも据え置き(削除・書き換えなし、
Trial-onlyのまま)であり、registry側(本定数・`run_content_integrity_
check_3v()`)を正本と宣言する。両者の同値は単体テストでpinする」という
表現へ修正した(実体のコード・テストは修正指示2回目時点から変更なし、
コメントの表現のみ是正)。

### 15-5. run_tts_3v()へbudget_check_fn引数追加(指摘E、3V実発火前に必須)

`er012_b_family_voices_production_01.py::run_tts_3v()`へ`budget_check_
fn=None`引数を追加した(既定None=修正前と同一挙動)。渡された場合、2V
`run_tts()`(`er012_b_family_production_runner_01.py`)と同一の粒度で、
各segment群(topic_intro/preview・comment/Narrator heading/Voice A・B・C
本文/Hook・Tension・Closing、計5群)の生成後に`budget_check_fn(note)`を
呼ぶ。`main_b1_3v()`のtts stageから`assert_budget_ok_3v`を渡すよう修正
(従前は`run_tts_3v()`の呼び出し中は予算チェックが一切走らず、tts stage
完了後の1回のみだった)。`budget_check_fn`が例外(`[BUDGET_GUARD]`等)を
送出した場合はここで揉み消さずそのまま伝播し、以降のsegment群を生成
しない(既存安全装置を独自判断で回避しない)。

新規テストクラス`RunTts3vBudgetCheckFnContractTests`(3件)で、(1)既定
None時は何も呼ばれず既存呼び出し元との後方互換が保たれること、(2)5群
それぞれの生成後に1回ずつ計5回呼ばれること(呼び出し順・note文言も固定)、
(3)budget_check_fnが例外を送出した場合はそこで即座に伝播し、以降の
TTS呼び出し(heading/Voice A・B・C/Hook等)が一切発生しないこと、を固定
した。

### 15-6. 見落とし2: Voice衝突STOP時のaudit/voice_resolution.json

`resolve_voice_names_3v()`が`[VOICE_COLLISION_STOP]`のRuntimeErrorを
送出する際、解決済み値(`resolved`辞書)とreasonsを例外オブジェクトへ
属性(`.resolved`/`.voice_reasons`)として添付するよう修正した(文字列
parseに依存させない)。呼び出し側`voice_check_3v()`はこれを使い、
衝突STOP時の`audit/voice_resolution.json`へも`voice_a`/`voice_b`/
`voice_c`(解決済み値、未解決分はnull)・`reasons`キーを含めるよう修正
した(従前はstatus/error/sample_resultsのみで、これらのキーが欠落して
いた)。

あわせて`main_b1_3v()`側で、`stage="tts"`等の単独実行時に読み込んだ
`voice_resolution.json`の`status`が`"VOICE_COLLISION_STOP"`だった場合、
従前は`resolution["voice_a"]`アクセス時に不可解な`KeyError`で落ちて
いたのを、明示メッセージの`RuntimeError`(まず`stage="voice_check"`のみ
再実行して一過性か切り分けることを促す文言含む)でSTOPするよう修正した。

新規テストクラス`VoiceCheck3vCollisionAuditTests`(2件、resolved属性あり/
なし双方)・`MainB13vCollisionStopExplicitMessageTests`(1件)で固定した。
既存`ResolveVoiceNames3vTests::test_voice_a_unavailable_causes_
collision_with_voice_c_and_stops`にも、`.resolved`/`.voice_reasons`
属性の存在確認を追加した。

### 15-7. 見落とし1/3: 運用注記の追記(REPORT文書のみ)

- `scaffold`単独実行は`kp_reuse`済み(`key_phrases/keywords_canonicalized.
  json`が存在する状態)が前提である(`run_scaffold_3v()`が`kp_merged`を
  そのファイルから読むため、未実行のまま`scaffold`単独を呼ぶと
  `FileNotFoundError`になる)。
- Voice衝突STOP発生時は、まず`stage="voice_check"`のみを再実行し、
  一過性の技術失敗(Voice A等が一時的にTTS技術失敗しただけ)か、
  構造的な衝突(`VOICE_FALLBACK`と`VOICE_ASSIGNMENT`の設計上の重複)かを
  切り分けることを推奨する(15-6節で追加した明示メッセージにも同旨を
  含めた)。
- 3V `B_FAMILY_B1_3V_REQUIRED_SEGMENTS`(opt-in構造Gate、
  `registry.build_required_structure(voice_c=...)`経由)は、現状の
  Production実走経路(`main_b1_3v()`)からは呼び出されておらず、2Vの
  `build_required_structure()`(mandatory化deferred、OPEN-129)と同じ
  非mandatory運用のままである。実際に呼ばれるのは、本Phaseの対象外の
  別evidence取得スクリプト(OPEN-129系の前例、14-1節項目9参照)からのみ。

### 15-8. 未使用定数`THEME_3V`の削除

`er012_b_family_production_runner_01.py`の`THEME_3V`
(`{"theme_id": ..., "out_dir": OUT_DIR_3V}`)は、参照ゼロ(定義箇所以外
grep該当なし)を確認した。3V Assembly(`run_assembly_3v()`)は2V
`run_assembly()`と異なり`asm.load_b1_sources(THEME)`ではなく専用の
`b1prod.load_b1_sources_3v(OUT_B1_DIR_3V)`を呼ぶ設計のため、この定数は
2V実装のコピー時に残った死コードだったと判断し、削除した(用途コメントを
付す選択肢もあったが、参照ゼロかつ将来使う予定のある設計要素ではない
ため削除を選択)。

### 15-9. 変更ファイル一覧(修正指示3回目)

- `er012_b_family_editorial_type_registry_01.py`: コメント修正のみ(D)、
  コード実体は無変更。
- `er012_b_family_voices_production_01.py`: `resolve_voice_names_3v()`の
  RuntimeErrorへ`.resolved`/`.voice_reasons`属性追加(見落とし2)、
  `run_tts_3v()`へ`budget_check_fn=None`引数+5箇所の呼び出し追加(E)。
- `er012_b_family_production_runner_01.py`: `voice_check_3v()`の
  except節でvoice_a/b/c+reasonsを保存(見落とし2)、`main_b1_3v()`で
  (i)collision-stop resolutionロード時の明示STOP追加(見落とし2)、
  (ii)scaffold_summary.jsonへdeviation_overall_status追加(B)、
  (iii)`run_tts_3v()`呼び出しへ`budget_check_fn=assert_budget_ok_3v`追加
  (E)、`THEME_3V`定数削除(15-8節)。
- `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`:
  新規テストクラス4件(`RunTts3vBudgetCheckFnContractTests`3件・
  `VoiceCheck3vCollisionAuditTests`2件・`MainB13vCollisionStopExplicit
  MessageTests`1件)・既存テスト1件へアサーション追加(合計54テスト、
  修正指示2回目時点の48テストから+6)。
- 本REPORT: 13-2節・14-7節への追記(A・C)、本15節の新設。
- いずれも2V/A-Family既存関数のロジック自体は1つも書き換えていない
  (新規オプション引数[既定値で無効]・except節の保存内容拡張・コメント
  修正・死コード削除のみ)。

### 15-10. regression結果

- `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`
  単独: **54テスト全PASS**(`Ran 54 tests in 0.101s / OK`、新規6件含む)。
  証跡: `er012_output/editorial_b_family_voices_3v_production_wiring_
  phase1_01/regression_evidence/phase1_fix3_offline_test_run_log.txt`。
- `--pattern "er012_*b_family*test*.py"`: **87テスト全PASS**
  (`collected=87 passed=87 failed=0 errors=0 skipped=0`、Phase 1bの81件
  +本修正の6件)。
- `run_project_regression.py`(全体、対象106ファイル・2307件、Part 1〜3
  修正+Phase 1b+本修正指示3回目実装後の最終1回のみ実行):
  `collected=2307 passed=2304 failed=3 errors=0 skipped=0`。証跡:
  `er012_output/editorial_b_family_voices_3v_production_wiring_phase1_01/
  regression_evidence/phase1_fix3_full_regression_log.txt`・
  `phase1_fix3_summary.json`。
- **既知failure 3件の同一性確認**: failed=3件の内訳は`er003_test_p2j_
  investigate.py`の`test_combined_equals_sum_of_er002_and_er003`・
  `test_p2h_reported_count_matches_er002_plus_er003_at_that_time`・
  `test_p2i_reported_count_matches_er003_at_p2i_era`の3件で、いずれも
  14-6節で記録した既知failure(テスト総数カウント照合、本タスクと無関係)と
  **テスト名が完全一致**する(本修正でテスト総数が2301→2307
  [+6]に増えたのに伴いこの3件のfailureメッセージ内のカウント期待値も
  ズレているだけで、fail自体の原因・対象テストは従前から変わっていない
  ことを`FAIL:`行のテスト名grep照合で確認した)。新規failureはゼロ。
- API呼び出しは0回(費用¥0、regression実行時のcostログ表示は既存test群が
  mockで`main()`系関数を呼ぶ際の印字であり実際のAPI呼び出しではない、
  12-1節と同じ確認方法)。

---
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EqG9xnr2dZhshz85bFW4Kt
