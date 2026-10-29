# WIRING_DESIGN_01 配線設計(仕様①候補提示前QA / 仕様②重複アラーム非ブロッキング)

前提: CURRENT_STATE_01.md。全Family(X/Y/Z)・全レベル(Std/Adv)は共通module(er119_kp_candidates_01 / er119_kp_human_review_01 / er128 / export_form_data_01)の修正で一括対応。Productionへの実装は**本設計のOpus条件Aレビュー後**(本委任はAPI 0・コード変更0)。両仕様はユーザー`APPROVED_FOR_PRODUCTION`(原文§1)のため11-7の限定例外(flag隔離)は不要で、通常のProduction変更(既存flag/Prompt/閾値は不変)。

## A. 仕様①: 候補は提示前に品質検査(QA FAILは選択可能候補として提示しない)

### A-1 基本方針と変更点(qa_failを旗でなく**除外(drop)**に格上げ)
既存の品質基準(11 QAフィールド、qa_overall_status判定、閾値)は**一切変えない**。変えるのは「QA判定の結果の扱い」だけ。
1. er119_kp_candidates_01.py:277-285(`_gate_chain`の候補組立): `qa_overall_status != "PASS"`(REVIEW_REQUIRED**および欠落・未知値=fail-closed**)の候補は、`dropped`へ`stage="canonicalization_qa"`(reasons=失敗したQAフィールド名+日本語要約、`item.qa`から決定論で作る)として追加し`cands`へ入れない(Human NG除外 :270-274 と同型)。`flags.qa_fail`は新規docでは常にFalse(スキーマ互換のため残す)。
   - 効果: 除外件数は既存の`gate_dropped`に数えられる(`GATE_DROP_EXEMPT_STAGES` er119_kp_backfill_01.py:25に入れない) -> **既存の補完(backfill、Gate除外の代替候補を1回補う)で候補数が補われる**(E計算 :115,:181は NOT_COUNTED_STAGES以外を数える=追加配線不要)。backfill OFF(EIGO_KP_BACKFILL=0)では既存の外側retry条件(:466-476)がn_auto/gate_droppedで働く。**新しいretry/上限は作らない**。
   - 補完候補自身(_run_backfillが同じ`_gate_chain`を通る)も同一規則で除外される(再帰補完しない=既存「1周1回」)。
   - rescue(救済、er125)のQA再判定FAIL候補(`RESCUED_QA_REJUDGED_FAIL`)も`qa_overall_status`がFAILのため同規則で除外。救済PASS/再判定PASSは従来通り提示。
2. 自動canonical化(例: `old-fashioned about it`->`old-fashioned`)の可否: 正規形は**候補データに存在しない**(CURRENT_STATE 0)。解決策の選択肢:
   - **案α(推奨・本実装)**: 除外+補完のみ。API増0(補完は既存機構)。判断根拠: 追加のLLM/決定論rule(例:「残余文脈語を機械的に削る」)は新しい正規化規則=新仕様の追加(承認済み基準の変更に当たる恐れ)であり、仕様①は「問題候補は原則提示しない」を許容している。
   - 案β(次段階の改善候補・今回は実装しない): QA FAIL itemのFAILフィールド名(例: qa_no_residual_context_word)を渡して**同一canon_fn・同一QAで1回だけ再canonicalization**し、PASSなら正規形で提示。追加費用は1 item x 1 call(約¥0.5-1/記事レベル)。新Prompt変更を伴うため別承認(判断候補D)。
3. 提示セットの単一関数: `er119_kp_human_review_01.presentable_candidates(cands)`を新設(`human_selectable`かつ`not flags.qa_fail`)。以下がこれ**だけ**を使う(重複定義しない): (a)`render_request_md`(er119_kp_human_review_01.py:1296-1327。除外分は「提示から除外した候補」節に理由付きで表示=人間が事実を確認可能)、(b)フォームdata exporter(export_form_data_01.py:62-86,155,`entry()`の呼出側)、(c)`auto_select`(:577-)。
   - これは**旧doc(既に旗qa_fail=Trueを持つ既存run)の防御**: 新docではqa_fail候補が存在しないが、resume(候補sha一致=再生成しない、er119_kp_human_review_01.py:1396-)で旧docを読むため、提示時点で同じ規則を再適用する(遡及で旧runの提示を変える点は下記A-4)。
4. `exporter`のfail-closed: 提示セット外のqa_fail候補をdataへ出さない。出力に`data_warnings`(既存の仕組み export_form_data_01.py: reason_missing_warning と同型)で `qa_fail_excluded: [candidate_id...]`を記録(隠さない)。

### A-2 確定時検査との役割分担(明文化)
| 検査 | 提示前(候補生成・presentable_candidates) | 確定時(validate_selection/op_select/finalize) |
|---|---|---|
| canonicalization QA FAIL | **ここで解決(除外)**。人間には出さない | 「提示セット外の選択」を拒否する安全網として**維持**(er119_kp_human_review_01.py:555-556。新docでは到達不能。手編集・旧doc・API直叩き対策) |
| NG/類似NG | 提示前に除外(Human NG、:270-274) | 維持(:559-564、後からNG追加された場合=提示後に変わり得る条件) |
| gloss HR待ち(gloss_hr_pending) | 旗付き提示(意味確認はresolve-glossという人手工程) | 維持(:557-558) |
| 件数/KP⊂vocab/重複選択 | - | 維持(提示後にしか決まらない条件) |
| Redundancy(候補全体/確定集合) | 旗(提示用)のみ | **アラームのみ**(B) |
=> 「提示後に変わり得ない条件(候補固有のQA)」は提示前に完結、「提示後に決まる条件(選択の組合せ・NG追加・件数)」のみ確定時検査に残る。

### A-3 `--accept-qa-fail`の扱い
- 新docではqa_fail候補が存在しないため不要化する。**今回は削除せず残置**(旧doc救済・明示override。`select`経路のみ、er119_kp_human_review_cli_01.py:272-285。op_select :648-)。残す根拠: 旧runのresume時に例外経路が必要・削除は別承認の仕様変更(承認済み運用の撤去)・Danglingは下記で確認。
- 残置に伴う整理: `human_accepted_qa_fail`/`REVIEW_REQUIRED_HUMAN_ACCEPTED`(er119_kp_human_review_01.py:1051-1065)は消費側が無い=無害な記録のため残置。新doc由来では書かれない。`--accept-qa-fail`は「旧doc専用」と`--help`/request.mdの文言で明示(文言は新docでは出さない)。撤去は新docが全稼働後の別委任(判断材料: 旧doc run数0になった時点)。

### A-4 旧run・Y記事への影響(遡及)
- 旧docが残るrun(Y姓テーマ run_02 a2、他の未確定run)は、presentable_candidatesにより**提示から外れる**。確定済みrun(確定レコード保有)は影響を受けない(G0保護、validate_selectionは確定時のみ)。ユーザー再選定は求めない。Y姓テーマStdは下記Eで専用手順。

## B. 仕様②: 重複(意味・用法)は**アラームのみ**(確定・音声・組立・Productionを停止しない)

### B-1 方針
判定(4観点x10ペア LLM、`REDUNDANCY_NG`)と`flags.redundant_with`は**維持**。変えるのは「NGが出たときの動作」を停止から**記録+表示**へ。判定不能(INVALID等)は重複ではないため**従来どおりfail-closed**(B-4)。

### B-2 変更箇所(停止条件の変更一覧、file:line)
| # | 場所 | 現状 | 変更 |
|---|---|---|---|
| 1 | er119_kp_human_review_01.py:566-570(validate_selection pair検査) | `errs.append("...重複...どちらか一方にしてください")` | 削除。`_pairs`(:493-)は`auto_select`(:577-)が使うので残す。代わりに新関数`redundancy_alarms(cands, selection, level)`(純関数、API 0)が選択内のpair(候補doc `redundancy_qa.duplicate_pairs`のreasoning・4観点を紐付け)を返す |
| 2 | er119_kp_human_review_01.py:694-722(op_select) | 検証エラーで拒否 | 検証通過後に`redundancy_alarms`を計算し`review["redundancy_alarms"]`(source=candidate_qa)と`history`イベント`redundancy_alarm`を保存。拒否しない |
| 3 | er119_kp_human_review_01.py:1007(finalize内validate_selection)、er128 :2095(cmd_reconsume) | pair検査で拒否 | #1の削除により自動的に非ブロッキング(コード変更不要。reconsume時はアラーム再計算) |
| 4 | er119_kp_human_review_01.py:1015-1016(M-8キャッシュ条件) | `fq.status != "REDUNDANCY_PASS"`ならdirty=再実行 | `status in ("REDUNDANCY_PASS","REDUNDANCY_ALARM")`かつ`key==_qa_key(sel)`ならキャッシュ有効(NGでも毎回有料再実行しない) |
| 5 | er119_kp_human_review_01.py:961-987(`_run_final_qa`) | NG時 status=REDUNDANCY_NG, ng_pairs | NG時 status=`REDUNDANCY_ALARM`、`alarm_pairs`(rank/candidate_id/used_form/観点/reasoning)を結果に持つ。INVALID等(:983-984)は従来のKpReviewError(fail-closed)維持 |
| 6 | er119_kp_human_review_01.py:1033-1043(finalize 人間選定のNG分岐) | PENDINGへ巻戻し・selection消去・`on_final_redundancy_ng`・`KpReviewPending` | 削除。`review.final_qa=fq`(ALARM)として保存し`history`に`final_redundancy_alarm`、確定処理を**続行**。AUTO分岐(:1017-1030)は不変(AIの自動選定=人間選定ではないため。尽きた場合のSTOPも維持) |
| 7 | er128_kp_confirmed_content_01.py:701-719(`on_final_redundancy_ng`/`raise_issue_nowait`) | 確定レコードをRECONFIRM化+CONFIRMED_CONTENT_ISSUE | 呼出元(#6)が無くなる。`on_final_redundancy_alarm(kp_dir, pairs)`へ置換: **レコード状態は変えず**historyへ非ブロッキング注記のみ。旧関数は撤去 |
| 8 | er119_kp_human_review_01.py:1075-1078(kp_selection_final.json) | `final_redundancy_qa: review.final_qa` | 既存フィールドがALARM+pairsを含む(run auditとして永続) |
| 9 | er119_kp_wiring_01.py:47(`_shape_final`の`redundancy_qa`) | review.final_qa を返す | 変更なし(statusはREDUNDANCY_ALARMになる。Grep: runner側でstatusを条件分岐する箇所は無い=CURRENT_STATE 3-5) |
| 10 | er119_kp_human_review_01.py:1296-1327(render_request_md)・export_form_data_01.py:84-85(flag_notes) | 「重複」旗のみ | 旗はそのまま(提示用)。アラーム詳細(対象・観点・理由)は#11の記録を参照 |

### B-3 アラームの記録と表示(既存の非ブロッキング掲載方式に合わせる)
- 記録: (i)正本=`kp_selection_final.json.final_redundancy_qa`(ALARM+pairs。finalizeと同時にatomic書込、:1075-1090) (ii)`kp_human_review.json.history`の`final_redundancy_alarm`/`redundancy_alarm` (iii)派生ファイル`<kp_dir>/redundancy_alarm.json`(再導出可能・`write_*_safe`型=書込失敗はwarningログのみで確定・制作を失敗させない。er078_pass_with_warning_registry_01.write_listening_list_safe:187と同じ思想)。内容=schema/level/selection_signature/sets(kp|vocab)/pairs[{candidate_id_a,b, ai_rank, used_form, slot(KP|追加解説|本文意味), 観点別PASS/FAIL, reasoning(日本語), source(candidate_qa|final_set_qa)}]/checked_at。
- 表示: (a)`kp_human_review_request.md`/readable内の旗の隣にreasoningの要約、(b)CLI `select`/`status`/`confirm`の出力に`redundancy_alarms`、(c)各runnerの完了報告ブロック(X=er019:3465付近の事後試聴リスト節の隣、Y=er121_family_y_runner_01.py:1295付近、Z=該当節。er078 `emit_completion_block`:385と同方式の「選定表現の重複アラーム(確認用・非停止)」節。0件でも「0件」と明記)、(d)ユーザー試聴ページ(user_test)の事後確認節: PASS_WITH_WARNING節と同方式で追加するか否かは**判断材料B**(一般向け公開ページには出さない。user_testの事後試聴リスト掲載が既に存在するpageのみ、export時に節を追加=推奨。範囲外ならrunner報告+run auditのみで仕様②の「確認可能・記録」は満たす)。

### B-4 失敗経路(fail方針)
| 事象 | 方針 | 根拠 |
|---|---|---|
| 仕様①: QA判定欠落/未知値/例外 | **fail-closed**(候補として提示しない=dropped。例外は`generate_candidates`を失敗させ既存のOUTER_RETRY_EXHAUSTED/FAILED経路へ。未検査候補を提示しない) | Q>D。誤提示の害>候補減の害(補完機構あり) |
| 仕様②: Redundancy QA判定不能(INVALID、技術失敗後) | **従来のfail-closed維持**(KpReviewError、:983-984)。ただし`make_redundancy_fn`の既存技術retry(最大2回、er011_key_phrase_set_redundancy_qa_01.py:225)は維持 | 重複**アラーム**ではなく検査器自体の故障。ユーザー承認は「重複アラームだけを理由に止めない」=判定器故障は含まない(Opus論点1) |
| アラーム派生ファイル書込失敗 | warningログのみ・確定続行(正本はfinal.json/history=確定と同時atomic) | 非ブロッキング |
| 正本(final.json)書込失敗 | 従来どおり確定失敗(既存の安全装置) | 重複と無関係の既存fail |
| resume(確定済み、署名一致) | idempotent: 署名同一ならファイル書き直さず、`final_qa.key`一致でRedundancy QAを再実行しない(#4)。派生`redundancy_alarm.json`が無ければ決定論で再生成(API 0) | 有料二重呼出防止 |
| 再選定(op_reselect)/本文変更 | 新roundの`review`は`redundancy_alarms`を引き継がない(選定データごと失効)。確定レコードのREBOUND時は選定同一ならアラーム再利用 | 選定が変わればアラームも変わる |

### B-5 維持するもの(他Gate不変)
canonicalization QA基準、CMU、記号、人称整合、SRC D1、NG、gloss HR、件数/KP⊂vocab、G0確定内容保護、AUTOの重複回避、判定不能fail-closed、Master Store/ASR等の後続Gate。

## C. 撤去・残置
| 識別子 | 判断 |
|---|---|
| `validate_selection`のRedundancy pair検査(er119_kp_human_review_01.py:566-570) | **撤去** |
| `finalize_kp`人間選定NG->PENDING巻戻し(:1033-1043)・`event: final_redundancy_ng` | **撤去** |
| er128 `on_final_redundancy_ng` / `raise_issue_nowait`(:701-719)・RECONFIRM(redundancy起因) | **撤去**(`on_final_redundancy_alarm`へ置換) |
| 旧test: er119_kp_human_review_01_test_01.py:236(重複選択が拒否される)、:293-302(`test_final_redundancy_ng_on_human_selection_returns_to_pending_M8`)、er128_kp_confirmed_content_test_01.py:582-593(`test_redundancy_ng_marks_reconfirm_required_and_allows_user_reselect`)、er128_kp_confirmed_content_slot23_test_01.py:329(validate_selectionモックの重複メッセージ文言) | **反転して書き換え**(非ブロッキング期待値へ)。不整合な出力を期待値にするtestは残さない |
| `_pairs`/`auto_select`の重複回避、AUTO final QA繰上げ(:1017-1030)・test(:322-351) | **残置**(AI選定の品質、人間選定ではない) |
| `--accept-qa-fail`・`accepted_qa_fail`・`human_accepted_qa_fail` | **残置**(旧doc/明示override、A-3) |
| `flags.qa_fail`・`flags.redundant_with`・`REDUNDANCY_NG`判定 | **残置**(提示用の旗・判定そのもの) |
| 旧経路(er003_v1_n3_01_scaffold_generate.py:877-897、A/B/C) | **無変更**(27-7、X/Y/Z正式経路ではない) |
| ニュアンスの提示前重複判定(er134、er120_part2_wiring_01.py:589) | **無変更**(別目的・提示前) |
Dangling Reference確認(実装時に再Grep): `final_redundancy_ng`/`on_final_redundancy_ng`/`redundancy_ng_reconfirm_required`/`意味・用法が重複しています`/`--accept-qa-fail`の参照を、コード・test・docs(ユーザー向けrequest文言、`docs/pm`運用手順)で0件または意図的残置のみにする。

## D. Family間差異と論点
- Family差: 無し(CURRENT_STATE 5)。X/Y/Zのrunner側の変更は**完了報告ブロックの節追加のみ**(B-3 c)。Z固有のSRC D1/人称整合は`_gate_chain`内で①の前に効く(順序: 既存dropが先、QA除外は最後=:277)。
- Opus条件A論点(Fableが設計レビュー依頼): (1)判定不能(INVALID)をfail-closedに残すことが「重複でProductionを止めない」に反しないか (2)qa_failを旗->除外にする際の補完(backfill)連携と候補数不足(shortfall)時の扱い(E<N、補完1回で埋まらない場合は現行shortfallの`shortfall_detail`のまま=人間は少ない候補から選ぶ。0件はOUTER_RETRY_EXHAUSTED) (3)旧doc/旧runへの遡及(presentable_candidates)の是非 (4)`--accept-qa-fail`の残置/撤去時期 (5)gloss_hr_pending(意味確認待ち)を「提示前に解決」の対象に含めるか(現状は提示後に`resolve-gloss`で人手解消=人手確認とフォーム扱いが別。**推奨=今回は含めない**。理由: ユーザー原文§2-3「必要な人手確認と選定フォームでの扱いを整合」の範囲だが、承認済みの意味確認(gloss整合)は人間が訳を決める工程でありQA FAILの除外とは別。含める場合は提示前にresolve-gloss相当を要求=フォーム提示がHR待ちになる運用変更でQCD影響大) (6)AUTOの重複回避を維持する妥当性 (7)案β(再canonical化)の別承認要否 (8)アラームの試聴ページ掲載範囲。
- 原文§2-3「REVIEW_REQUIRED等」の「等」: 本設計はqa_fail(REVIEW_REQUIRED)のみ除外対象とし、gloss_hr_pending・similar_to_ngは論点(5)として据置。

## E. Family Y「夫が妻の姓を選ぶとき」run_02への適用手順(ユーザー再送信なし)
出所(記録): ユーザー原文§2(Std: `old-fashioned about it`->`old-fashioned`、他維持)/§3(Adv: let go of / hold one's son back / give something up を維持し重複アラームを記録して確定)/§6(再開)。user_ref=docs/pm/delegation_log/2026-10-29_HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01_USER.md §2/§3/§6、元のHR選定=docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER_HR_01.md と run_02/hr/readable_{a2,b1b}.txt。

**Adv(b1b)**: 候補docにqa_fail=0件・データ変更なし(d6不変)->ユーザー送信済みreadable_b1b.txt(AIF1コード有効)をそのまま`confirm --from-readable`へ。仕様②実装後、validate_selectionのpair検査が消えるため通る。finalizeでRedundancy QA(約¥1-2、1 call/集合)が走り`REDUNDANCY_ALARM`を記録して続行(原文§3-4)。**可。実装①②の完了が前提**。

**Std(a2)**: `old-fashioned`は候補docに無い(上記A-1 2)。手順案:
- 方式P(推奨): 新op `op_requalify_candidate`(PENDING_REVIEW中のみ、`op_resolve_gloss` er119_kp_human_review_01.py:860-の同型。review_lock・candidates_sha再計算・review.candidates_sha256更新・historyに出所user_ref記録)で、rank5の`used_form/key_phrase`を `old-fashioned` に差し替え、**同じcanon QA(qa再判定、er125 qa_rejudge:503の既存関数)とgloss再整合(ga)**を通す。PASSなら候補として提示、FAILなら本手順は不成立(ユーザー意図との不一致=Fable/ユーザー報告)。費用: qa再判定1 call + gloss整合1 call = 約¥1-3。ただし「Production候補のin-place編集」は新opであり、操作範囲を`ユーザーが明示した正規形への差替え`に限定する(任意文字列不可、`old-fashioned`が本文に連続一致するspanであることを`source_sentence`で決定論検証=`qa_traceable_contiguous_span`)。
- 方式Q(代替): Std a2のKP候補生成を再実行(新規候補生成: 約¥?+、本文固定)。結果に`old-fashioned`が出る保証なし->ユーザー決定(`old-fashioned`)を満たせないリスクがあり非推奨。
- 方式R(代替): 候補rank5のまま`select --accept-qa-fail 5`でused_form `old-fashioned about it`を確定し、確定後に`confirm-revise`で表示文言を`old-fashioned`へ。ユーザー指示(正規形`old-fashioned`でQA PASS)と、確定後の差替えを許さない原則の双方に反し非推奨。
- 方式Pの後: exporter(新)で`surname_choice__a2__prod.json`を再生成(rank5が`old-fashioned`、QA FAILなし)。**d6が変わる**ため、旧readable_a2.txtのコードは新dataには無効。選定は「その他維持」なので、**readableの再構成**:
  1. 旧readable_a2.txtを旧data(git履歴d6、`git_history_lookup`)で`restore`し選択(candidate_id列・文法・コメント)を取得(既存機能、er128_form_readable_restore_01.restore:358)。
  2. rank5(candidate_id不変: id=`candidate_id_for(selection_phrase)`のため差替え前後で同一にするには`selection_phrase`を保持=方式Pでは`selection_phrase`は不変・`used_form`のみ差替え)なので選択のcandidate_idは**そのまま**、termだけ`old-fashioned`に更新。
  3. 新dataに対し、フォームと同一ロジックでreadable+照合コードを生成: **推奨=form_logic.js(user_test/selection_form_v3/form_logic.js)をnode(v24.18.0、確認済み)で実行**(`buildText`/`buildStructured`/照合コード関数、:147-,:293-)。state(choices: term->category、grammar id、comment)を注入しreadable文字列を得る。Python側`er128_form_readable_restore_01.build_readable:187`/`make_code:168`との**バイト一致を両者で照合**(既存testの同一性検査 er128_form_readable_restore_test_01.py を流用)。一致した出力を`restore`で読み戻し、`confirm --from-readable`(by=ユーザー決定の実行代行ではなくuser_ref付き)で確定。
  4. 確定レコードの`attestation`/`user_ref`: 「フォーム送信の再現」ではなくユーザー原文§2/§6の明示決定である旨を記録(`ACTOR_USER`か`EVIDENCE_RUN`かの区分はFable判断=判断候補B)。ユーザーの再送信は求めない(要件)。
- 可否: **Adv=可、Std=方式Pで可(新opの実装・Opus条件Aレビューが前提)**。代替(PがQA再判定FAILで不成立の場合): Std/Advの再選定ではなく、`old-fashioned`のQA状態の事実を報告してユーザー判断(D)。
- 費用見込み(Y記事のみ): Std op=qa再判定+gloss整合 約¥1-3、Std/Adv最終Redundancy QA 約¥2-4 -> **合計約¥3-7(目安・上限¥10)**。実測前の見積で案件300円以下(7-7)。以降の音声生成以降は既存手順・予算(別見積、本委任範囲外)。

## F. 実装順序(Production実装委任時の分解案、依存・並列)
1. [先行・並列] presentable_candidates + _gate_chain除外 + exporter filter(①) / validate_selection・finalize・on_final_redundancy_alarm(②)(別ファイル=er119_kp_candidates_01 / er119_kp_human_review_01 / er128でファイル競合なし。ただしer119_kp_human_review_01.pyは①②両方が触る=①request.md部と②validate/finalize部は別関数だが同一ファイルのため直列(同一ファイル競合))。
2. test反転・新test(TEST_PLAN_01)。3. 完了報告ブロック節。4. Y適用(op新設後)。5. copy-run runtime evidence(X/Y/Z x Std/Adv)。6. SSOT(CURRENT_SPEC:1987,1995置換追記、DECISION_LOG、OPEN_ITEMS)。
