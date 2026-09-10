# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-02-BUDGET-GUARD-AND-COMMENT3-01

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-02-BUDGET-
GUARD-AND-COMMENT3-01`。委任範囲は「Opus L2レビュー
(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-01-OPUS-L2-
REVIEW-01_REPORT.md`)指摘1-b(予算ガード)と論点2(Comment 3文言混在)への
対応」。書き込みは対象4ファイル(registry・production_01・
production_runner_01・新規テストファイル1本)・本REPORTのみ。SSOT
(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・`docs/pm/
ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は未編集。Git操作
(add/commit/push)は未実施。API呼び出し0回(費用¥0)。

## 0. Reconciliation Check(着手前の重要な発見)

着手前に対象4ファイルの現物とGit履歴を確認したところ、**指摘1-b(予算
ガード)は本タスク着手前に既に実装・commit済み**であることが判明した。

- `er012_b_family_voices_production_01.py::run_tts_3v()`は既に
  `budget_check_fn=None`(既定None)引数を持ち、2V `run_tts()`の
  `assert_budget_ok`と対称な5箇所(topic_intro後/preview・comment後/
  Narrator heading後/Voice A・B・C後/Hook・Tension・Closing後)で
  `budget_check_fn(note)`を呼ぶ実装が既に存在する(該当コードのdocstringに
  「Fable修正指示3回目(Opus L2レビュー指摘E)」と明記)。
- `er012_b_family_production_runner_01.py::main_b1_3v()`のttsステージも
  既に`run_tts_3v(..., budget_check_fn=assert_budget_ok_3v)`で呼んでいる。
- 対応する契約テスト(`RunTts3vBudgetCheckFnContractTests`、既定None時の
  後方互換・5回呼び出しの順序とnote文言・例外伝播で以降のTTSが発火
  しないことの3件)も既に存在し、`git log`確認では`git show
  HEAD:er012_b_family_voices_production_01.py`に該当コードが含まれる
  (コミット`b358b85 PM-CLOSEOUT-CONSOLIDATION-72`で本タスク開始前に
  Git統合済み)。
- したがって**指摘1-bに対する新規コード変更は不要**と判断し、対称性・
  テスト内容の検証のみ行った(1節参照、変更なし)。
- 一方、**論点2(Comment 3タイトル行/役割行の表現混在)は未解決のまま**
  だった(タイトル行L144は「どちらが正しいか」、役割行L147は「どの声が
  正しいか」のまま残存)。ユーザー決定に基づき、本タスクではこの点のみ
  実装した(2節)。

## 1. 指摘1-b(予算ガード): 検証のみ、変更なし

対称性を実コードで再確認した。

| 2V `run_tts()`(既存、無変更) | 3V `run_tts_3v()`(既存実装、無変更) |
|---|---|
| topic_intro後 `assert_budget_ok("after topic_intro TTS")` | topic_intro後 `budget_check_fn("after topic_intro TTS")` |
| preview・comment後 `"after preview/comment TTS"` | 同左 |
| Narrator heading後 `"after Narrator heading TTS"` | 同左 |
| Voice A/B後 `"after Voice A/B TTS"` | Voice A/B/C後 `"after Voice A/B/C TTS"` |
| Hook/Tension/Closing後 `"after Hook/Tension/Closing TTS"` | 同左 |

note文言・呼び出し順序とも既存テスト
(`RunTts3vBudgetCheckFnContractTests::
test_budget_check_fn_called_once_per_segment_group`)でpinされていることを
確認した。2Vコード(`run_scaffold`/`run_tts`/`main()`の2V分岐)は本タスクで
一切触れていない。

## 2. 論点2(Comment 3表現混在): 実装

`er012_b_family_editorial_type_registry_01.py::VOICES_COMMENT_3_ROLE`の
タイトル行(「その間に流す、Comment 3(役割: 「どちらが正しいか」ではなく
...」)を、既存の役割行(L147、修正指示2回目で既に変更済み)と同じ
「どの声が正しいか」側へ統一した。Comment 4(`VOICES_COMMENT_4_ROLE`)は
本タスクのユーザー決定の対象外のため「どちらが正しいか」のまま無変更。

- `VOICES_COMMENT_3_ROLE`は`COMMENT_ROLES`辞書経由でB1(2V/3V)・A2から
  共有される**単一定数**であることを確認した。3V専用の分岐は作っていない
  (3V専用キー化はしなかった)。理由: 役割行の同種の変更(修正指示2回目、
  「どちらが正しいか」→「どの声が正しいか」)が既に同じ共有定数へ適用
  済みで、その際「2V/A2のComment 3再生成にも同様に波及するが意図した
  変更」と明記されている(前回REPORT 13-5節)。タイトル行だけを3V専用に
  分岐させると、同一プロンプト内でタイトル行(3V専用)と役割行(共有)が
  異なる管理ドメインになり、かえって整合性が崩れる。今回のユーザー決定
  文言(「タイトル行を役割行と揃える」)とも整合するため、既存の共有定数を
  そのまま編集する方針を踏襲した。
- 2V出力(オフライン構造レベル)への影響: `test_voice_c_omitted_matches_
  pre_existing_2v_b1_output`等の既存pinテストはsegment構造(名称・個数)の
  比較のみで、プロンプト文字列自体を比較しないため**無影響で継続PASS**
  (3節で実測確認)。ただし2V/A2の**実際のLLM生成プロンプト文言**は変わる
  (修正指示2回目と同じ性質の波及、新規ではない)。

## 3. 追加テスト

`er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`へ
新規クラス`Comment3TitleRoleWordingUnifiedTests`(2件)を追加した。

- `test_comment_3_title_and_role_lines_both_use_which_voice_phrasing`:
  Comment 3本文中に「どの声が正しいか」が2箇所(タイトル行+役割行)
  含まれ、「どちらが正しいか」が1つも残っていないことを固定。
- `test_comment_4_wording_untouched_by_this_task`: Comment 4は
  「どちらが正しいか」のまま・「どの声が正しいか」を含まないことを固定
  (意図せぬ波及がないことの確認)。

指摘1-b(予算ガード)側は既存テスト3件(1節参照)がそのまま該当するため、
新規テストは追加していない(重複pinを避けた)。

## 4. Offline regression結果(API呼び出し0回、費用¥0)

- `.venv/Scripts/python.exe -m unittest
  er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01 -v`:
  **56テスト全PASS**(`Ran 56 tests in 0.109s / OK`、新規2件含む、旧54件
  +2件)。証跡:
  `er012_output/editorial_b_family_voices_3v_production_wiring_phase1_01/
  regression_evidence/phase1b_02_offline_test_run_log.txt`。
- `.venv/Scripts/python.exe run_project_regression.py --pattern
  "er012_*b_family*test*.py"`: **89テスト全PASS**
  (`collected=89 passed=89 failed=0 errors=0 skipped=0`、旧87件+2件)。
  証跡: 同ディレクトリ`phase1b_02_b_family_pattern_log.txt`。
- `.venv/Scripts/python.exe run_project_regression.py`(全体):
  `collected=2309 passed=2306 failed=3 errors=0 skipped=0`。**failed=3件は
  いずれも`er003_test_p2j_investigate.py`の既知failure**
  (`test_combined_equals_sum_of_er002_and_er003`・
  `test_p2h_reported_count_matches_er002_plus_er003_at_that_time`・
  `test_p2i_reported_count_matches_er003_at_p2i_era`、テスト名を`FAIL:`行の
  grepで前回REPORT記載と完全一致することを確認、本タスク前から存在する
  テスト総数カウント照合の既知事象で本タスクと無関係)。**新規failureは
  ゼロ**(前回2307→今回2309[+2、本タスクの新規テスト2件分]で件数増加は
  説明がつく)。証跡: 同ディレクトリ`phase1b_02_full_regression_log.txt`・
  `phase1b_02_summary.json`。
- API呼び出しは0回(TTS/LLM/ASR未使用)。regression中に表示される
  `[B-FAMILY-VOICES-3V-PROD]`等のログは既存test群がmockで`main()`系関数を
  呼ぶ際の印字であり、実API呼び出しではない(前回REPORTと同じ確認方法、
  cost固定値0.00 JPY表示で確認)。費用¥0。

## 5. Opus指摘対応表(`PHASE1B-01-OPUS-L2-REVIEW-01`全項目)

| # | 内容 | 状態 | 備考 |
|---|---|---|---|
| 1-a | content integrity checkが Trial=record-only→Production=fail-closed STOP(挙動追加、2V非対称は意図的) | **注記のみ(既存)** | 本タスク以前の`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01_REPORT.md`15-1節で既に明記・commit済み。本タスクでの変更なし。 |
| 1-b | `run_tts_3v()`に予算ガードが無い | **対応済み(既存実装を検証)** | 0節・1節参照。本タスク着手前に既に実装・テスト・commit済みであることを確認。新規コード変更なし。 |
| 1-c | integrity checkの実行位置がLLM 5回生成の後 | **未対応(理由: 任意改善、安全上必須ではない)** | Opus自身が「任意(safety上の必須ではない)」と明記。承認済み3V仕様の不足配線の範囲を超える最適化のため、本タスクでは対応しない。 |
| 1-d | STOP判定に含まれない項目(Hook分割・Key Phrase不在)がある | **注記のみ(既存)** | 前回REPORT 15-1節で既に明記・commit済み。 |
| 1-e | Tension語数観測ログに新QA基準混入なし | OK(対応不要) | 既存テストでpin済み、変更なし。 |
| 1-f | Ledger Deviation接続は2Vと同一 | OK(対応不要) | 既存実装のまま、変更なし。 |
| 1-g | Voice衝突ガードは2Vで誤発火しない | OK(対応不要) | 既存実装のまま、変更なし。 |
| 1-h | Voice A一過性失敗が3V全体STOPになる(運用注意) | **注記のみ(既存)** | 前回REPORT 15-7節で既に運用注記を追加・commit済み(まず`voice_check`単独再実行を推奨する旨)。 |
| 論点2 | Comment 3役割行変更の2V regression影響なし、ただしタイトル行/役割行の表現混在が残存 | **対応済み(本タスクで実装)** | 2節・3節参照。タイトル行を役割行と同じ「どの声が正しいか」へ統一、pinテスト2件追加。 |
| 論点3 | registry「2重定義解消」表現がTrial側残存の実態とズレる | **注記のみ(既存)** | 前回REPORT 15-4節で「正本宣言(Trial側は据え置き、テストで同値pin)」表現へ既に修正・commit済み。 |

## 6. Production全経路のうち残る未配線項目・runtime evidence未取得項目

いずれも本タスクの範囲外(承認済み3V仕様の不足配線のみという委任範囲を
超えるため、STOPとして現状維持、実装していない)。

- **Writerステージ(新テーマからの記事生成)は依然未配線**
  (`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01_REPORT.md`
  14-2節のSTOP事項: Ledger作成のProduction化・Writer retry上限の決定・
  OPEN-132構造ゲート非互換、いずれも未解決のまま)。
- **runtime evidence 13項目(同REPORT 14-8節)は未取得のまま**
  (実行同一性・model_id実測・Voice 3値相互相違の実測・16 segment実測・
  mandatory disfluency 9件実測・OPEN-121/122有効化記録・Human Review Lock
  非発火確認・OPEN-129 opt-in構造Gate実測・音声実測・Key Phrase記録・
  費用実測・Comment 1-4実出力記録・SSOT整合確認)。本タスクはオフライン
  実装+testのみのためAPI呼び出しを伴うこれらは取得していない。
- `B_FAMILY_B1_3V_REQUIRED_SEGMENTS`(opt-in構造Gate)は現在も
  `main_b1_3v()`の実走経路から呼ばれておらず(2Vと同じ非mandatory運用、
  意図的)、OPEN-129系の別evidence取得スクリプト専用のまま(変更なし)。
- `PRODUCTION_WIRED`は本タスクでも宣言していない(Writerステージ未配線の
  ため、実質的な新テーマ記事の完走経路はまだ存在しない)。

## 7. 費用・変更範囲まとめ

- 費用: ¥0(API呼び出し0回)。
- 変更ファイル: `er012_b_family_editorial_type_registry_01.py`
  (Comment 3タイトル行1行+コメント、計18行変更)・
  `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`
  (新規テストクラス1件・2メソッド、25行追加)の2ファイルのみ。
  `er012_b_family_voices_production_01.py`・
  `er012_b_family_production_runner_01.py`は本タスクでは無変更(0節、
  既に別コミットで統合済みのため)。
- Git操作: 未実施(commit/pushはFableが別途統合)。

---
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
