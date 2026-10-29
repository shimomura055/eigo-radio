# FABLE_ACCEPTANCE_01(HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01 委任_04、2026-10-29。受入評価対象=仕様①②・ニュアンス整合・D8掲載・Y surname記事再開)

受入記録:

## (1) 当初目的・要求された最終状態(ユーザー原文の逐語引用)
- 仕様①(`2026-10-29_HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01_USER.md:30-34`): 「Key Phrase／Word、追加解説、本文意味等の候補を、人間に提示する前に品質検査する。」/「品質上の問題がある候補は、原則として選択可能な候補として提示しない。」/「人間が選定した後になって、提示前に検出できた品質問題を理由に再選定を求める運用を解消する。」/「既存の承認済み品質基準・検査条件は変更しない。」
- 仕様②(同:42-48): 「人間が選定した表現同士に意味・用法の重複がある場合、従来どおりアラームを出す。」/「アラームの内容・対象表現・判定理由を人間が確認できるようにする。」/「**重複アラームだけを理由として、選定確定、音声生成、組立、正式Productionを停止しない。**」/「重複以外の品質Gate・安全条件は従来どおり維持する。」
- Family Y指示(同:91-98): 「Standard：`old-fashioned`へ変更し、その他の選定は維持。」/「Advanced：元の選定内容を維持し、重複アラームを記録したうえで確定。」/「音声生成以降は既存の承認済み制作手順・Gateに従う。」
- 完了条件(同:104-113): 「Family X／Y／ZのStandard／Advancedすべてに正式配線済み。」「正式runtimeでの発火証拠を取得。」「必須テストPASS。」「retry／fallback／resume等との整合確認済み。」「CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新済み。」「Git反映済み。」「未解決Open Item、未処理判断、Dangling Referenceがないことを確認。」/§5(同:85,89): 「不要となった旧ブロック処理・旧検査の撤去要否」「旧検査を無条件に削除するのではなく、必要な検査は維持し、重複アラームの停止機能のみを変更してください。」
- ニュアンス(`docs/pm/delegation_log/2026-10-29_HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01_USER_02.md:18,21-25`): 「人間の選定後は、重複アラームだけを理由に選定確定やProductionを停止しない。」/「これが候補生成段階での重複除外を意味するのであれば問題ありません。しかし、人間が選定した後にも重複NGで停止する仕組みが残っている場合は、承認済み共通仕様に反します。」(提示前除外は可、選定後の重複NG停止は共通仕様違反)

## (2) 実際の最終成果物
- commit: a6ecbbb3e(委任_02r: 仕様①②実装、24 file。`er119_kp_human_review_01.py`/`er119_kp_candidates_01.py`/`er128_kp_confirmed_content_01.py`/exporter等)、fada4be0e(委任_03A: ニュアンス3経路撤去・X/Y/Z実LLM evidence・OPEN-600/601)、本委任(委任_04: D8掲載+受入記録+isolation test整理。hashは RESULT_PACKET_HRQ4.md)。
- 本委任の変更file: `er119_kp_human_review_01.py`(共通レンダ関数 :1213 `render_redundancy_alarms`/:1241 `render_redundancy_alarms_all`)、`er019_family_x_listening_page_01.py:197`、`er121_family_y_runner_01.py:1348`、`er026_family_z_fiction_production_runner_01.py:2682`、`er063_family_z_audio_01.py:2697,2738,2768,2784`(`post_check_html`引数、既定空=従来とバイト同一)、`er119_redundancy_alarm_display_test_01.py`(新規7 test)、`er119_isolation_test_01.py`/`er128_kp_confirmed_content_test_01.py`(許可集合更新)、`user_test/family_y_production_surname_choice_01/index.html`(手動掲載→自動掲載節へ置換)、SSOT。
- 撤去(ニュアンス3件、NUANCE_REDUNDANCY_CONSISTENCY_01.md): 確定時pool_conflicts交差ISSUE(er128:1785)、V3フォーム送信/コピー拒否(form_logic.js:73、index.html:96,135)、ページ入口のKP集合変化NuanceStale(er134:1149)。撤去(KP: IMPLEMENTATION_01.md 5節): validate_selectionのpair検査、finalize人間選定NG→PENDING差戻し(final_redundancy_ng)、on_final_redundancy_ng/raise_issue_nowait/STATE_RECONFIRM/G1 RECONFIRM ISSUE/auto_adopted_after_reconfirm_required、ensure_kp_reviewの死にコードexcept、依頼書/exporterの旧QA FAIL・gloss HR待ち旗文言。
- 残置と理由: 候補段階のKP/Word重複NG・文法警告・M-4被覆ISSUE・pool鮮度ISSUE・引用改ざんNuanceStale(重複以外のGate=原文§3-5/§5)、`--accept-qa-fail`(旧doc未確定2runの救済専用、OPEN-600に撤去条件)、AUTO(不在宣言)選定の重複回避・繰上げ・枯渇STOP(人間選定ではない=範囲外)、旧経路A/B/C(27-7)。
- 失敗経路の最終成果物: 全候補がQA不合格=候補0でFAILED(OUTER_RETRY_EXHAUSTED、KP stage失敗。成果物なし)/最終Redundancy QAが判定不能(INVALID等)=fail-closed(KpReviewError。選定は保持、同じコマンド再実行で判定だけ再試行。`test_u12`)/Y surname差替えtool不合格=無変更(ToolRefused、何も書かない)。いずれも「重複を理由に止める」経路ではなく、重複以外のGate/故障のfail-closed。

## (3) 証拠
- 6組合せ(X/Y/Z×Std/Adv)の実LLM runtime evidence: EVIDENCE_01.md「6組合せ」表(X Std kp_candidates.json:998・redundancy_alarm.json:46/final.json:92、X Adv :1213、Y Std :888、Y Adv :1199+実記事redundancy_alarm.json:53、Z Std :1035、Z Adv(z_tth2) :1165・rescue_unverified提示前除外)。全6組合せ blocking=false・state=FINALIZED(`reached_next_stage=runner_kp_stage_passed`)。resume: Z Advのfinalize同一引数再実行でAPI 0(raw_usage_log 12行→12行、wrote=[])。
- Y surname実記事のalarm: `er121_output/family_y_production_01/surname_choice/run_02/key_phrases/a2/redundancy_alarm.json:33`(alarm_count 1: let one's son go×give something up)、`.../b1b/redundancy_alarm.json:53`(alarm_count 2: let go of×hold one's son back/give something up、③本文意味を含む)。選定は差し戻されずgate→assemble→pages→page_verify完走(e2e_stage_log.jsonl)。
- ニュアンス修正のtest: `er128_nuance_hr_test_01.T2...test_pool_conflict_is_alarm_only_when_that_item_is_chosen_spec2`・`T7...test_pool_conflict_never_blocks_in_form_logic_spec2`、`er134_nuance_runner_wiring_test_01.T3_Overlap.test_pool_conflict_chosen_at_hr_is_alarm_only_adoption_proceeds_spec2`、`test_redundancy_alarm_helper_is_deterministic_and_nonblocking_spec2`、`test_no_pool_conflict_records_empty_alarm_file_and_pass_spec2`、`test_kp_set_changed_after_nuance_confirm_is_alarm_not_stale_stop_spec2`。候補段階除外の不変=`test_kp_word_overlap_is_discarded_before_hr_and_not_replaced`。
- D8掲載: 共通レンダ er119_kp_human_review_01.py:1213/1241、呼出し X er019_family_x_listening_page_01.py:197・Y er121_family_y_runner_01.py:1348・Z er026_family_z_fiction_production_runner_01.py:2682(→er063:2784)。test=er119_redundancy_alarm_display_test_01(0件/複数件+重複排除+HTMLエスケープ/ファイル欠落・壊れJSON=空表示・非停止/Z index既定バイト同一/runner呼出し存在)7 OK。Y surname候補ページを`--stages pages,page_verify`(API 0、spent_jpy 48.7534不変)で再生成: pages配下53ファイル中index.htmlのみ変化、音声52ファイルsha256同一、`#post-check`節を除くとindex.htmlが再生成前とバイト同一(本文不変)、page_verify rc=0。user_test候補ページは手動節→自動節へ置換(check_page PASS、節は1つのみ=二重なし)。
- resume API 0の証拠: 上記Z Advのfinalize再実行、Y pages,page_verify再実行(費用不変)。

## (4) 目的要件との一致(項目別)
| 項目 | 判定 | 根拠 |
|---|---|---|
| 仕様①(提示前QA・不合格候補を提示しない) | 一致 | presentable_filter(IMPLEMENTATION_01.md 1節、実LLM: Z Adv rescue_unverified除外 EVIDENCE_01)、既存品質基準は不変 |
| 仕様②(アラーム表示・記録のみ、非停止) | 一致 | 全6組合せ blocking=false・FINALIZED、Y surname実記事が完走、D8で表示も実装 |
| ニュアンス整合 | 一致 | 選定後停止3経路撤去、候補段階NG/引用改ざん等は維持(mock 4 caseの発火証拠) |
| X/Y/Z × Std/Adv evidence | 一致 | EVIDENCE_01 6組合せ(PASS分岐は実記事/複製run testで補完を明記) |
| retry・resume | 一致 | resume API 0、fail-closed再試行、AUTO分岐不変 |
| 撤去 | 一致 | 上記(2)。照合Grep: `d("pool_conflicts"`・`FL.nuanceConflicts(D,get())`=0件、STATE_RECONFIRM等は撤去説明コメントのみ(er128:695-697) |
| dangling | 一致 | `TestNoDanglingAndCommonPath`で固定 |
| Y記事再開 | 一致 | Std old-fashioned・Adv元選定維持で確定、音声以降完走、候補ページ提出済み(OPEN-598、ユーザー試聴待ち) |
| D8掲載(§3「アラームを表示・記録」) | 一致 | 本委任。事後確認節+stdout |
| isolation test 2件 | 一致 | 承認済み配線のimportとして許可集合更新(OPEN-588) |
- 未確認: (a)後続stage(gate〜page)到達はX/Zの複製runでは未実行(KP stage通過まで。実記事Y surnameでは完走済み)。(b)ニュアンス解説の実LLM evidenceはmock(X/Y/Zの正式outputは全てLEGACY=ニュアンス仕様マーク無し)。(c)M8(救済QA再判定key不一致)=OPEN-601は現状維持(案A)、仕様②の達成とは独立。(d)D8の#post-check節は公開(public)ページにも入る設計(`pww`節は公開から除外される一方、候補ページへの掲載要求を優先)。正式公開時に節を残すか除くかは公開手順側の判断(Fable管理)。

## (5) 最終受入判定
**ACCEPTED: PRODUCTION_WIRED(X/Y/Z・Std/Adv)**。理由: ユーザー原文の仕様①②・ニュアンス整合・Y記事再開・完了条件8項目を、実LLM runtime evidence(6組合せ)・test・Y実記事の完走で確認し、未確認(a)(b)は上記のとおり範囲と理由を明示した(いずれも承認仕様と実動作の不一致ではない)。新flag・新品質基準・Production挙動の意味的変更なし。
判定整合: 重大NG=なし / 主因=なし / 是正対象=なし / STOP理由=なし / 提示=可
