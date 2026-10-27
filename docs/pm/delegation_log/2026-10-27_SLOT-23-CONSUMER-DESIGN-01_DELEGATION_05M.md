## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_05M(M班: A〜E班完了(A 22f3a09ef / B 374cfc941 / C e2feca7ab / D 331474a9f / E f03f12c2e)を受けた「最後の1commit」(M14)=マーク発行の接続+残整合。API 0)。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`。並行Agent: なし(本委任は単独。SSOT編集権なし)。あなたの所有=`er119_kp_human_review_01.py`(`new_review`末尾`NOTE(M14)`への`issue_std_part1_mark(r)`接続1行)、`er128_kp_confirmed_content_01.py`(G3 `verify_outputs`の`level=="b1b"`ガード(:891付近)をlevel化=display_spec付きa2でもPart 1行と確定gloss照合)、`er128_kp_confirmed_content_slot23_test_01.py`(`test_M14_new_review_does_not_issue_mark_yet`→接続後期待値へ置換)、`er128_kp_confirmed_content_test_01.py`(`TestIsolation`は**許可リストを広げない**)、`er121_family_y_runner_01.py`・`er026_family_z_fiction_production_runner_01.py`(`import er128_*`直書きを、C班と同じ`_khr()._cc()`/遅延accessor方式へ=`er019_family_x_audio_production_runner_01.py`の方式に揃える。挙動不変)、`docs/research/SLOT-23-CONSUMER-DESIGN-01/{IMPL_M_01,REGRESSION_M_01}.md`、`..._DELEGATION_05M.md`(+check.json)、`docs/pm/RESULT_PACKET_S23M.md`(gitignore)。実run・公開・AI島再ビルドはしない。pathspec付きcommit(1 commit)、`git push origin HEAD:main`。時間見込み約1.5h。

## 実施事項

1. 接続前チェック: C/D/E班の配線が全Familyで揃っていること(`display_spec_of`参照点、Std Part 1 level化、Validator「Part 1ちょうど1個」、page_verify G3)をGrepで一覧化(`IMPL_M_01.md`)。欠けがあれば接続せず報告。
2. マーク発行接続: `new_review`→`issue_std_part1_mark(r)`(新規reviewのみ。既存記事は`reconsume`明示実行まで不変=遡及なし)。test期待値更新。`display_spec`導出がa2/b1b両方で働くこと(B班判断(a))をtestで固定。
3. G3 Std Part 1照合のlevel化(`verify_outputs`)。display_spec無しa2は従来どおり。
4. isolation整合: Y/Zの`import er128_kp_highlight_01`直書き→X方式(遅延accessor)へ。`TestIsolation`PASS、`test_default_is_on_and_single_reader`PASS。
5. 全体回帰: `.venv\Scripts\python.exe run_project_regression.py`で主要群(`er003_*`/`er019_*`/`er026_*`/`er062_*`/`er063_*`/`er119_*`/`er120_*`/`er121_*`/`er128_*`/`er_learning_highlight*`/`er_page_audience*`/`er053*`/`er030*`)を実行し、失敗を「本変更起因/既知OPEN-543/環境(genai・faster_whisper等未導入)」に分類(`REGRESSION_M_01.md`)。本変更起因は0にする。
6. 旧経路残存Grep総括(S1〜S27/T1〜T5の最終状態、`"b1b"`リテラル、`Advancedのみ`文言、`.removed`、`_part1_items_b1b`等)を`IMPL_M_01.md`に。CURRENT_SPEC更新要点(S29/S30、:2095正式入口)をSSOT文案として列挙。
7. commit: `SLOT-23-CONSUMER-DESIGN-01 委任_05M: マーク発行(std_part1/display_spec)をnew_reviewへ接続(新規reviewのみ・遡及なし)+G3 Std Part 1照合level化+Y/Z isolation整合+全体回帰(API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Read一覧

`IMPL_PLAN_03.md`(M)、`IMPL_B_01.md` §3(接続手順)、`docs/pm/RESULT_PACKET_S23{B,C,D,E}.md`(要対応・判断候補)、`er119_kp_human_review_01.py`(Grep `NOTE\(M14\)|issue_std_part1_mark|def new_review` ±10)、`er128_kp_confirmed_content_01.py`(Grep `def verify_outputs|level == "b1b"|display_spec` ±10)、`er019_family_x_audio_production_runner_01.py`(Grep `_khr|_cc\(|er128_kp_highlight` ±5)。

## 報告

`RESULT_PACKET_S23M.md`: (0)T-0、(1)接続前チェック、(2)差分、(3)回帰分類表、(4)残存Grep、(5)判断候補、(6)必須4行+「判定整合」、(7)SSOT文案、commit hash・raw URL。末尾5行要約。