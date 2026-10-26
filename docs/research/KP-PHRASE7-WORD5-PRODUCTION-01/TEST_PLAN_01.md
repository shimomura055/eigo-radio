# TEST_PLAN_01: 受入条件1〜9 x test設計
KP-PHRASE7-WORD5-PRODUCTION-01 委任_01 / 2026-10-27 / 計画のみ(test未作成・API 0)。原文§6の番号に対応。mock/golden/DefaultOnはAPI 0、実LLMは`EVIDENCE_PLAN_01.md`。
禁止: 不整合な出力を期待値としてassertするtestは書かない。**易語の混入をassert失敗にしない**(原文§2)。

## 0. 追加するtestの置き場(既存ファイルを優先、新規は最小)
- 新規 `er119_kp_p7w5_test_01.py`(Prompt pin・message・parse・run_selection_gate(P7)・run_vocab_selection(W5')・cap・補完の種類別)。
- 既存改訂: `er119_kp_backfill_test_01.py`(plan_quota/pick_backfill/定数、22参照)、`er119_kp_human_review_01_test_01.py:79`(12)、`er105_kp_fulltext_selector_01_test_01.py`(keyword-only引数の既定=従来動作を明示test)、`er119_isolation_test_01.py:71`(新moduleをA/B/C非importの対象へ)、`er106_joint_runtime_evidence_01_test_01.py`(旧run専用化)、`er119_kp_rescue_wiring_test_01.py`/`er125_*test*`(注入経路の回帰)。
- 据置(変更しない): Prompt 2 sha(`a12896f4…`)・2-V sha(`e1d5349c…`)のpin test(`er105_*test*`, `er003_test_kp_fulltext_wiring_01.py`, `er003_test_kp_outer_retry_exclusion_01.py`, `er119_kp_backfill_test_01.py`, `er119_kp_human_review_01_test_01.py`)。Trial module `er124_*test*`は無変更で回帰PASSを維持。

## 1. 条件別test
| 受入 | 検証内容 | 種別 | 新規/改訂 |
|---|---|---|---|
| 1 正式初回経路で7+5が適用 | (a)`generate_candidates`を`select_fn/vocab_call_fn`**未注入**(=DefaultOn)でLLM呼出関数だけmockし、call1のmessageが`P7_TEXT+BODY_DELIMITER+本文`(先頭がP7 sha)、call2が`W5'`(先頭W5' sha+ALREADY節)であることをassert。(b)`.env`/環境変数/引数でP7/W5'をOFFにできない(DefaultOnIsolation相当: 環境変数全消し+全クリアで同一) (c)X/Y/Z runner(`kw.run_kp_with_review`)の`kp_generate_fn`未注入real経路がP7/W5'を選ぶ(runnerのreal分岐をmock clientで) (d)doc`prompt_ids/prompt_sha256`がP7/W5'、`model_id`=gpt-6-luna | DefaultOn | 新規 |
| 2 5条件・補足・出力規則が承認どおり | W5'本文を原文§3と**条件文字列単位**で照合(5条件の順序・「絶対条件」ラベル・条件5「必須条件にはしない」・補足3行・出力規則[最大5・順位付け・理由1文40字以内・数合わせ禁止・出力直前再確認・語数併記])。順序入替・条件追加がsha変化で検出されること。KP含有語除外の補足が**除外**文言であること(Trial W5の「一律除外しない」が残っていないGrep) | pin/文字列 | 新規 |
| 3 本文一致・1語・包含重複除外 | (a)本文に無い語→validate drop (b)`count_words!=1`→`not_single_word`(D3) (c)語がcall1フレーズに含まれる→`duplicate_of_top3` (d)含まれない語は通過 (e)基本形化後の重複(R-3)。実Gate関数(validate/CMU/containment)を使い、LLMだけ固定返答 | unit/golden | 新規 |
| 4 上限未満でも不必要な補完をしない | P7が4件・W5'が3件返答でGate除外0 → `backfill.triggered=False`・補完call数0(`vocab_call_fn`呼出カウント)。**E=0かつ初回が7/5未満**と**E=0かつ7/5到達**の両方 | unit | 新規 |
| 5 Gate除外時のみ適切件数を補完・既存保持 | E_phrase=2/E_word=1 → フレーズ補完call(P7)とWord補完call(W5')が各1回、採用は種類別quota以内、初回候補のai_rank/内容がsha一致(保持)、末尾追加。フレーズ空き<E_phrase(例: 現存6フレーズ・E_phrase=3)→quota=1。単語空き0→単語call 0。`overflow`/`overflow_kind`はEに数えない。救済成立はEに数えない(現行回帰) | unit/golden | 改訂(`er119_kp_backfill_test_01.py`) |
| 6 KP救済・QA・HR・フォーム | 救済候補(`rescue`)がフレーズ/単語とも現行どおりannotate・NG照合(`er119_kp_rescue_wiring_test_01.py`回帰)。HR依頼書12行の描画(`render_request_md`)、`auto_select`(kp=先頭3、Adv vocab=先頭5)の結果がP7上位=現行コード挙動のまま(D2)。`candidates_sha256`・review整合・`finalize_kp`が12件docで通る。フォームexport(`export_form_data_01.py`は**読み取りのみ**)に12件docを通し`phrases<=7/words<=5/overflow空`をassert(read-only import、コード無編集) | 結合 | 新規 |
| 7 retry/fallback/regen/resume | (a)resume: 保存済み7+5 docがある状態で`ensure_kp_review`再実行→generate_fn呼出0・doc sha不変(API 0) (b)旧3+5 docをresumeしても再生成されない (c)reselect round2でHuman NGがP7/W5'のnote/機械除外に入り、旧NG句が復活しない (d)外側retry(call2失敗)でも既存候補は保持されず全体再生成される従来仕様の回帰(`outer_attempts`) (e)補完は1周1回・補完call失敗でも初回候補で続行(FAILED記録) (f)STOP sentinel/routing違反は伝播 (g)確定済みreview(REVIEWED)は`generate_fn`を呼ばない | unit | 新規+回帰 |
| 8 Validator/回帰/統合 | `run_project_regression.py`全体(collected/failedを実行ログで記録、HEAD既存失敗[OPEN-543の4件等]は区別)。mock E2E: X/Y/Z x Std/Adv の`kp_generate_fn`注入runner経路で候補生成→HR依頼書→AUTO宣言→finalize→下流整合(`require_final_consistent`) | 回帰/E2E(mock) | 実行 |
| 9 formal runtime evidence | `EVIDENCE_PLAN_01.md` | 実API | 委任_03 |

## 2. golden(Prompt差替以外の副作用検出、R-6の教訓)
- 実装前のHEADで、`generate_candidates`へ**固定LLM返答**(select_fn/vocab_call_fn/canon_fn注入、Gate連鎖は実関数)を与えた13 scenario(AI島/猿の手/メロス/再配達等の凍結入力、E=0/E>0/救済/CMU除外/Z人称・SRC D1)の候補docを保存し、実装後に**同一注入・Prompt差替以外のパラメータ同一**で実行して、`candidates[].{used_form,japanese_gloss,flags,gates,kind,ai_rank}`が(7+5の件数差を除き)同一であることを確認。Gate連鎖(`_gate_chain`)を触らない前提の裏取り。
- 既存golden: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/golden_02a`(読取のみ)を再利用可能な範囲で流用。

## 3. 静的test(隔離・旧ルール)
- A/B/C(`strategy_l`経路)が新module・`er119_kp_candidates_01`を**import しない**(`er119_isolation_test_01.py`拡張)。
- Prompt 2 / 2-V のsha/本文が**不変**(据置pin)。
- `Grep "一律除外しない"`: W5'本文・新module・docstringに残っていないこと。Trial module `er124`は履歴として残置(Trial、Production非import)。
- `Grep "KP_CANDIDATE_MAX\s*=\s*8"`: 残存0。

## 4. 実行
unit/golden/DefaultOn/isolation: 数十秒(API 0)。回帰全体: 既存どおり(7000+件)。結果はIMPLEMENTATION_01.mdに実行ログ(コマンド・件数・失敗内訳)で記録し、**PASS宣言は実行後のみ**。
