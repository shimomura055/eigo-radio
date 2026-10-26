# EVIDENCE_01: Gate除外候補の補完(Production配線)の正式経路runtime evidence(委任_03、2026-10-26)

到達上限Status=**EVIDENCE_COLLECTED**(PRODUCTION_WIRED判定はFable)。機械可読版=`evidence_01.json`(`tools/collect_evidence_02.py`が生成、API 0)。fresh候補ファイル=`evidence_runs/fresh_candidates/`、replay=`replay_results/<case>/{replay_result.json,kp_candidates_doc.json}`、起動ログ=`evidence_runs/*.log`、stop確認=`stop_check_*.json`、費用=`COST_01.md`、フォーム用データ=`FORM_DATA_01.md`。
Production経路は無変更(コード編集0。`git diff`対象はtool/データ/文書のみ)。補完の既定=ON(`er119_kp_backfill_01.py:25-27` `backfill_enabled()`、環境変数`EIGO_KP_BACKFILL`が`"0"`のときだけOFF。委任文が承認済み仕様としたため)。

KPI provenance(混ぜない): **fresh**=production_formal_path(各Family正式runnerのKP stage、新規run dir、TTS/本文生成なし、補完ON既定) / **replay**=凍結した初回出力(call1・call2・canonicalization初回)+実LLM(補完call・補完分canonicalization・gloss整合・救済後QA再判定・Redundancy QA)を正式`er119_kp_candidates_01.generate_candidates`経由で実行(補助証拠。`tools/replay_backfill_01.py`)。**synthetic**=R2(数字句の注入)・R5b(`interferes`の注入)は凍結call2へ句を足した/置換した合成入力(§3注記)。

## 1. 起動コマンド全文(`--help`で引数確認。いずれもKP stageのみ・TTS/本文生成なし。`TTS_EXECUTION_MODE=STANDARD`明示)
| Family | run dir(入力は既存runの複製) | コマンド |
|---|---|---|
| X(AI島) | `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01`(source `er019_output/ai_island_temple/run_kpbf_ev_01`=run_ai_01のarticle.md複製、support texts複製) | `.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug ai_island_temple --run run_kpbf_ev_01 --level both --stage scaffold --scaffold-only kp --budget-jpy 20` |
| Y(再配達) | `er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01`(translate/・text/複製) | `.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_kpbf_ev_01 --stages kp --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 20 --tts-execution-mode STANDARD` |
| Z(メロス。猿の手は§6の理由で代替) | `er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01`(writer/r2.md・std.md・provenance.json複製) | `.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_kpbf_ev_01 --stage kp --mode real --approved-budget-jpy 20 --tts-execution-mode STANDARD` |
| X R-9 #1(コーヒー価格) | `.../coffee_prices__run_kpbf_ev_02`(run_fxpw_01の複製) | X同型(`--slug coffee_prices --run run_kpbf_ev_02`) |
| X R-9 #2(中東情勢) | `.../middle_east_yemen_saudi__run_kpbf_ev_03`(run_mey_02の複製) | X同型(`--slug middle_east_yemen_saudi --run run_kpbf_ev_03`) |

起動時刻(UTC、`evidence_runs/*_start.txt`): X(AI島) 14:02:16 → Y 14:05:02 → Z(猿の手、STOP) 14:07:36 → Z(メロス) 14:11:49。再起動確認: Y 14:11:04 / Z(メロス) 14:17:42 / X(中東) 14:27:04(初回14:21:08)。X R-9 #1(コーヒー)は14:16:18→14:16:33。各run dirは5分内3回なし(最大2回)。起動前に`tools/stop_scope_check_01.py`(全rc=0、`stop_check_*.json`)。
**規律からの逸脱(自己申告)**: X R-9 #1(コーヒー)の初回起動は入力article.mdの複製漏れでAPI前に`FileNotFoundError`(原因判明・費用0・`x_r9_launch1.log`)、複製後の再起動は**15秒後**(委任文の起動間隔150秒以上を下回った。同一run dirで5分内2回=RESTART_STORM閾値の3回未満、API前失敗のため実害なし)。他の起動間隔は150秒以上。
rc=4はKP Human Review待機(設計どおり、失敗ではない)。

## 2. fresh 10 level-run(KP stage限定、補完ON既定)の観測表
Std=A2(a2)/Adv=B1(b1b)。E=Gate除外件数(救済成立・HR限定・overflowは数えない)、N=補完上限=min(E,8-現存,5)。

| Family | 記事 | Lv | 候補(call1/call2/補完) | auto可 | E(段) | 補完 | 追加(ai_rank) | 補完callの返答→Gate通過 | 救済(auto可否) | outer retry | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X | AI島 | a2 | 7(3/4/0) | 7 | 0 | **不発動(E=0)** | - | - | 0 | 1周 | 上限未満(7<8)でも不発動=受入4 |
| X | AI島 | b1b | 7(3/4/0) | 7 | 0 | **不発動(E=0)** | - | - | 0 | 1周 | 同上 |
| Y | 再配達 | a2 | 7(3/3/1) | 7 | **1**(validate: `as it is`) | **発動 OK** | `have a hard time`(7) | 4返答→2通過(CMU: `redelivery fee`、本文不一致: `make more sense than`を除外) | 0 | 1周 | surplus 1件(`doesn't feel right`) |
| Y | 再配達 | b1b | 7(3/4/0) | 7 | 0 | **不発動(E=0)** | - | - | 1(`doesn't sit right with someone`、auto可) | 1周 | 救済成立は数えない=受入6 |
| Z | メロス | a2 | 7(3/3/1) | 7 | **1**(validate: `in his place`) | **発動 OK** | `a knife flashed`(7) | 3返答→3通過 | 0 | 1周 | 補完候補もSRC D1=PASS |
| Z | メロス | b1b | 8(3/5/0) | 8 | 0 | **不発動(E=0)** | - | - | 0 | 1周 | 上限8到達 |
| X(R-9) | コーヒー価格 | a2 | 7(3/4/0) | 7 | 0 | 不発動 | - | - | 0 | 1周 | |
| X(R-9) | コーヒー価格 | b1b | 8(3/5/0) | 8 | 0 | 不発動 | - | - | 0 | 1周 | |
| X(R-9) | 中東情勢 | a2 | 6(3/2/1) | 6 | **1**(cmu: `to weaken Houthi military targets`、`Houthi`未登録) | **発動 OK** | `more than the facts show`(6) | 2返答→2通過 | 0 | 1周 | call2が3件返答→CMU除外で2件に |
| X(R-9) | 中東情勢 | b1b | 8(3/3/2) | **5** | **2**(validate×2: `stretch what was said`・`settle who is responsible`、有限助動詞) | **発動 OK** | `Saudi-led coalition forces`(7)・`track down the subject`(8) | 5返答→5通過、先頭2件採用・surplus 3 | **3**(`intercepted and destroy`[M1]・`goes beyond the evidence`・`backs operations`[REVERT]、いずれauto不可=`rescued_not_auto`3) | 1周 | n_auto=5≥3 |

要点: 発動4/10(E>0のとき必ず発動、追加件数=E以下[1,1,1,2]。受入2)、不発動6/10(全てE=0。受入3)。候補0件・技術失敗の外側retryは0回(全て1周)。補完の追加は全て末尾(ai_rank 6-8)で、初回候補の入れ替えは無い(`kp_candidates.json`のcall1/call2のcandidate_id・ai_rankは補完前後で連続)。

## 3. replay 7件(凍結初回出力+実LLM補完。「正式関数の動作証拠(補助)」)
| case | 凍結入力 | E(段) | 補完 | 追加 | 結果の要点 |
|---|---|---|---|---|---|
| R1 X AI島Std | HR候補doc(run_ai_01 a2)のcall1/call2。call2=`taken a detour`/`one step ahead`/`studied separately`/`too soon to wave a flag` | 1(validate: 6語`too soon to wave a flag`) | OK | `way around this` | `studied separately`はcanonicalization初回凍結でINVALID→再試行(実LLM)でPASS(区分1是正後の現行Gate)。surplus 2。E=1のため追加1件(N=1)。Gateは6語を緩めていない |
| R2 X UK Std | `uk_train_speaker_playback` run_kprescue_ev_01 a2のcall1/call2+**synthetic**`a fine of up to £1,000`(数字句)をcall2末尾へ注入 | 1(validate: 数字) | OK | `take away`(phrase) | E=phrase 1のため単語`masterpiece`は**surplusで不採用**(種類別quota=R-1。単語で埋めない) |
| R3 Y 再配達Std | fixture 9(run_01 a2のdoc) | 1(cmu: `redelivery fee`) | OK | `go to delivery workers` | 選定段救済`it can’t be helped`→`can’t be helped`(IDIOM_CORE_WITHOUT_IT、auto可)は**E外**(受入6)。補完側でも`as it is`を本文不一致/finite auxで除外(`dropped` origin=backfill) |
| R4 Y SNS Adv | fixture 13 | 0 | **不発動** | - | `catch their interest`→`catches their interest`(REANCHOR_D1)・`takes our use into account`(M1、auto不可=`rescued_not_auto`)の**救済2件は除外に数えられずE=0**(受入6)。`have a say`は現行Gateで通過 |
| R5a Z 猿の手Adv | Trial現行方式docのcall1/call2(本文sha=run_sf_prod_01 r2.mdのcanonical化と一致 8388280a…) | 0 | 不発動 | - | 候補8(上限)。`accepts no responsibility`は現行Gateでcanonicalization PASS(区分1是正後) |
| R5b Z 猿の手Adv | R5aのcall2のうち`sergeant-major`を**synthetic**`interferes`へ置換(Trial-02 COMPARISON_02:111の`duplicate_of_top3`事例) | 1(`duplicate_of_top3`、単語) | OK | `sergeant-major`(単語) | **Gate維持**: `interferes`は`interferes with fate`との包含で再び除外される。補完は単語を要求(種類別)、フレーズ2件はsurplus |
| R6 Z メロスAdv | melos run_p2_evidence_r3 b1bのcall1/call2 | 0 | 不発動 | - | `held out`(REDERIVE_M1_WINDOW、auto不可)の救済は数えずE=0=受入6。SRC D1 PASS |

replay費用等は`COST_01.md`。replay内の初回call1/call2/canonicalization返答のmodel_idは`REPLAY_FIXTURE`(凍結)で、実LLM部分(補完call他)は`gpt-6-luna`。

## 4. 不発動の証拠(受入3・4)
- (a) **E=0**: §2のfresh 6件(X AI島a2/b1b・Y b1b・Z b1b・コーヒーa2/b1b)・replay R4/R5a/R6。`backfill.triggered=false, status=NOT_TRIGGERED, reason="E=0"`、補完callは**usage logに0行**(`backfill.response_id`が無く、`backfill_1/`ディレクトリが生成されない)。
- (b) **初回が上限未満でE=0**(runtime観測あり): X AI島a2/b1b(7件=3+4、call2が4件返答)・Y b1b(7)・コーヒーa2(7) = 上限8に満たないが`triggered=false`(数合わせしない)。`shortfall_detail`=`{n_candidates:7, cap:8, missing:1, E_total:0, backfilled:0}`(`kp_candidates.json`)。mock testも`er119_kp_backfill_test_01.py:216 test_below_cap_without_exclusion_does_not_trigger_TBF02`でPASS(55件PASS)。

## 5. 救済非計上・外側retry・M-1・resume・HR依頼書・Z整合(受入5・6)
| 項目 | 結果 | 証拠 |
|---|---|---|
| 救済済みは除外に数えない | **runtime観測あり**: Y b1b(救済1)・X中東b1b(救済3[auto不可]、E=2は救済と無関係の別句)・R3/R4/R6 | `evidence_01.json`の`rescued`と`E`、R4: 救済2件でE=0 |
| 補完が外側retryを置換(`rescued_not_auto`があっても再生成されない) | **runtime観測あり**: X中東b1bは`rescued_not_auto`=3件・Gate除外2・n_auto=5だが`outer_attempts=1`(全10 level-runが1周)。旧条件(Gate除外+n_auto<3の全件再生成)は**n_auto<3のrun自体が観測できず**未観測 | `outer_retry_log`(`kp_candidates.json`)、mock: `test_gate_drop_with_auto_lt3_no_longer_retries_on_TBF18a`(test:380)・`test_rescued_not_auto_leg_removed_on_TBF18c`(:397) |
| M-1(call1最終attemptの除外を計数) | **runtime未観測**(fresh/replayでorigin=call1の除外は出なかった) | mock: `test_call1_final_attempt_drops_are_counted_and_backfilled`(`er119_kp_backfill_test_01.py:345`) |
| 重複混入(補完が既存/除外句を返す)の捨て | **runtime未観測**(補完返答の重複率0。`backfill_duplicate`の発生0)。O8: 補完call 8回(fresh4+replay4)で返答計26件中、現存候補との重複0(`backfill_duplicate`0)、Gate不通過は3件(Y a2: CMU1・本文不一致1、R3: 本文不一致1)・通過23件 | mock: TBF12(`:286`)。`evidence_01.json`の`backfill_call` |
| resume再課金0・sha不変 | Y: `kp_candidates.json` a2/b1b sha不変・usage行数16→16(`evidence_runs/y_*`)、Z(メロス): sha不変・14→14(`z_*`)、X(中東): sha不変・19→19(`xmey_*`)。各rc=4(Human Review待機) | `evidence_runs/{y,z,xmey}_{sha,usage}_*.txt` |
| HR依頼書の補完要約行・旗 | Y a2・Z a2・X中東a2/b1b: `- Gate除外 N件(フレーズ…)に対し、補完候補 M件を末尾に追加しました(補完status: OK)`+表の旗列に`補完候補(Gate除外の代替)`。不発動のrunには出ない(Y b1bで`補完`0件) | `evidence_runs/fresh_candidates/*_kp_human_review_request.md` |
| Z SRC D1・人称整合 | メロスa2(補完あり)/b1b: 全候補の`gates.src_d1=PASS`(補完候補`a knife flashed`含む)。補完分のgloss整合は`work/backfill_1/gloss_alignment_*`で実行。人称整合のrepairは未発火のため`gloss_person_repair_backfill`ディレクトリ未生成(出力先分離の挙動自体はmock `:507,:525,:543`) | `kp_candidates.json`、`backfill_1/` |
| AUTO挙動(n_auto<3、HRなし宣言) | **runtime未観測**(HRなし宣言はユーザー宣言なしでは使えないため宣言付きrunは実行していない)。mock引用のみ | `test_auto_select_works_with_backfilled_candidates_tail`(`:614`) |

## 6. 規律・逸脱の自己申告と発見事項
- **猿の手(Z)のfresh runは不可**: `the_monkeys_paw`のseed.json(2026-10-25更新、sha`8f763160…`)が既存writer provenance(`8f1128b9…`、run_sf_prod_01/run_fzcw_e1_02等すべて)と不一致となり、`FamilyZProvenanceMismatchStop`で**API前に停止**(`evidence_runs/z_launch1.log`、費用0、1回のみ・原因判明)。provenanceの手書き換え(Gate回避)はせず、Zは`melos`(同じ共通KP経路・provenance一致)へ代替し、猿の手はTrial現行方式docの凍結+実LLM補完のreplay(R5a/R5b)で関数の動作証拠を取った。**発見事項(Fableへ)**: 猿の手は公開済みtext(run_sf_prod_01)がseed更新前のもので、seedを再確定/本文再生成するまでZ runner経由のKP stageは起動できない(新規OPEN候補。分類は`RESULT_PACKET_KBF3.md`(9)参照)。
- 委任文の「Y=SNS・猿の手AdvをfreshでなくreplayR4/R5で」は計画どおり。fresh対象はX=AI島(+R-9の2記事)・Y=再配達・Z=メロス。
- 並列起動した初回3 run(X/Y/Z)は別run dir・別Family。RESTART_STORM/STOP/rate limit等の実害なし。replayはfreshと並行実行(別process・別out dir)。
- フォーム: 既存JS単体test(`selection_form_logic_test_01.js` 1行)を、index枠数の判定から`_prod`slugを除く最小修正(6件追加で『9記事枠』の数え方が変わるため。UI・form_logic.js・既存データは不変)。

## 7. 受入条件(委任文§6)との対応
| 条件 | 内容 | 結果 | 主な証拠 |
|---|---|---|---|
| 2 | 正式経路でのGate除外→補完の動作 | **観測(runtime)**: fresh 4件でX/Y/Z全Familyに自然発動(X中東a2/b1b、Y再配達a2、Z メロスa2)。追加件数=E以下。補完もGate再検査(validate/CMU)を受ける | §2、`evidence_01.json` |
| 3 | E=0で補完不発動(補完API 0) | **観測**: 6件+replay 3件。`triggered=false`・補完call 0行 | §4 |
| 4 | 初回が上限未満でも不発動 | **観測**: 7件(X AI島×2・Y b1b・コーヒーa2) | §4(b) |
| 5 | 補完後のGate再検査と重複防止 | Gate再検査は観測(補完側でcmu/validate除外、R5bで`duplicate_of_top3`再除外)。重複の捨て(`backfill_duplicate`)はruntime未観測(mock TBF12) | §3、§5 |
| 6 | retry/fallback/resume/HR/救済との整合 | 救済非計上・外側retry不発火・resume・HR依頼書・Z整合は観測。M-1・AUTO n_auto<3・旧retry条件は未観測(mock) | §5 |
| 7 | 必須Regression | 本委任は実装変更なし。補完test 55件PASS・フォームtest 6件PASS(Production code無変更)。全回帰は委任_02のRESULT_PACKET_KBF2 | `run_project_regression.py` |
| 8 | actual model_id/Prompt/routing | 補完call・全生成callのmodel_id=`gpt-6-luna`(現行routing契約`SUPPORT_MODEL`、本番ライン無変更。開発・評価の最新モデル原則[25節]: 本番routing契約のモデルを使用、最新性は本番ライン判断=別。例外理由=現行本番の補完動作を検証する目的)。Prompt 2-V sha=`e1d5349c…`(固定値と全補完callで一致、`backfill_prompt_sha_pinned_match=true`)。Prompt 2 sha=`a12896f4…`。補完Promptは2-V本文無変更+`already`+既存exclusion note(件数文言なし) | `evidence_01.json`の`backfill_prompt_sha_pinned_match`、`kp_candidates.json`の`prompt_sha256` |
| 11 | フォーム用データ契約JSONを正式経路から生成(委任文§6の11。本文未取得のため委任_03の実施事項6に基づく) | 6件を`user_test/selection_form_v3/data/`へ追加・index登録、フォームtest PASS | `FORM_DATA_01.md` |

2-Vが指示を守るか(O8、件数文言なしで足りるか): 補完call 8回(fresh4・replay4)で、返答は『すでに選ばれた表現』と重複せず(0/26)、要求した種類(フレーズ/単語)で返答し(R2/R5bの単語・フレーズ別quotaで採用判定)、Gate通過率は23/26(88%)。**件数文言を足す新Promptは現時点で不要**(判断候補なし)。ただし標本は小さい。

## 8. 補完品質に関する所見(事実のみ。判定はFable/ユーザー)
- 補完で追加された句の例: `have a hard time`・`a knife flashed`・`more than the facts show`・`Saudi-led coalition forces`・`track down the subject`・`way around this`・`take away`・`go to delivery workers`・`sergeant-major`。`a knife flashed`(文に近い形)・`more than the facts show`は学習項目としての質に個人差がある可能性があるが、Gate(承認済み基準)は通過している。AI島/UKなど既存の評価基準は変更していない(品質基準の引上げ/引下げはしない)。
