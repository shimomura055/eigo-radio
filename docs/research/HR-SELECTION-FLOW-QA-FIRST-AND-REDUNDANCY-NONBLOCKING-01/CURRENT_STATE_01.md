# CURRENT_STATE_01 現状調査(HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01 委任_01、API 0・コード変更0)

調査日2026-10-29。ユーザー原文=docs/pm/delegation_log/2026-10-29_HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01_USER.md。

## 0. 結論(要点)
- X/Y/Z・Std/Advは**同一の共通経路**(er119_kp_wiring_01.run_kp_with_review -> er119_kp_human_review_01.ensure_kp_review -> er119_kp_candidates_01.generate_candidates)を通る。呼出元: X=er019_family_x_audio_production_runner_01.py:1022、Y=er121_family_y_runner_01.py:583、Z=er026_family_z_fiction_production_runner_01.py:2171。Family間の実装差は候補生成後の配線に無い。Std/Advの差はvocab有効性(`vocab_enabled`、er119_kp_human_review_01.py:491-)とStd Part1マーク(`std_part1`)のみ。
- 原因(Y Std): **QA FAILは「除外」でなく「旗」として候補に残り提示されている**。canonicalization LLMが`old-fashioned about it`を一般化し切れず、itemのqa(qa_no_residual_context_word / qa_standalone_comprehensibility=FAIL)->`qa_overall_status=REVIEW_REQUIRED`(er003_key_words_canonicalization.py:864-875)->`flags.qa_fail=True`/`auto_eligible=False`(er119_kp_candidates_01.py:277-284)。正規形`old-fashioned`は**候補データのどこにも存在しない**(used_form=selection_phrase=`old-fashioned about it`。run_02 a2 kp_candidates.json rank5で確認)。
- 原因(Y Adv): Redundancy QAが複数箇所でブロッキング(下記3)。Adv候補にqa_failは0件、重複旗は rank2/3/6 に付与。Stdにも重複旗あり(rank1「let one's son go」とrank4「give something up」)。

## 1. 候補生成の品質検査とフォーム提示
| 段 | 場所 | 内容 |
|---|---|---|
| canonicalization(+gloss再整合) | er119_kp_candidates_01.py:204-216 `_gate_chain`、er003_key_words_canonicalization.py:836-875 | INVALIDはitem除外後に再実行(MAX_CANON_RERUN=2、:41)。**REVIEW_REQUIREDは受理して候補に残す**(:210-212) |
| 旗付与 | er119_kp_candidates_01.py:277-285 | `flags.qa_fail`=qa_overall_status==REVIEW_REQUIRED、`auto_eligible`=not(qa_fail or hr or sim)、`human_selectable=True`固定 |
| 他Gate(除外=dropped) | :239-263 | CMU post-canon/記号/人称整合(Z)/SRC D1(Z)/Human NGは**除外**(dropped。補完backfillの対象) |
| 救済(rescue) | er125_kp_rescue_production_01.py(annotate_candidate:593) | Gate除外句の救済+QA再判定。再判定FAILはauto不可のまま(rescue_auto_ok:582) |
| Redundancy QA(候補全体1回) | er119_kp_candidates_01.py:445-459 | duplicate_pairsを`flags.redundant_with`へ(提示用の旗) |
| フォームdata exporter | docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py:62-86,155 | QA FAIL候補も**提示している**(flags.qa_fail同梱+注記「QA不合格(人間のみ採用可)」`flag_notes`:78-79、重複旗:84-85)。除外・警告ブロックはしない |
| フォーム(JS) | user_test/selection_form_v3/form_logic.js | qa_fail/redundantを一切参照しない(Grep 0件)。選択を制限しない |
| readable/request.md | er119_kp_human_review_01.py:1302-1307 | 「QA FAIL(採用には --accept-qa-fail)」「重複: n」を旗表示 |
=> 現状は**提示後(確定時)に初めてqa_failを拒否**する設計。仕様①(提示前に解決)と不一致。

## 2. 確定経路
- `confirm --from-readable`(er128_form_readable_restore_01.cmd_from_readable:618 -> er128_kp_confirmed_content_01.cmd_from_form)は :1505 の`rv.op_select(kp_dir, kp_ranks, vocab_ranks, by=by)`を呼ぶ。**accept_qa_fail引数なし**。op_select(er119_kp_human_review_01.py:648)は`validate_selection`(:516-)を呼び、qa_fail候補は`accepted_qa_fail`に無ければ拒否(:555-556)。
- `select --accept-qa-fail N`(er119_kp_human_review_cli_01.py:272-285)はaccepted_qa_failを渡す唯一の経路。finalize時にitemへ`human_accepted_qa_fail=True`、overall_status=`REVIEW_REQUIRED_HUMAN_ACCEPTED`(er119_kp_human_review_01.py:1051-1065)。この値の**消費側はproduction code内に無い**(Grep: 書込みのみ)。
- 役割分担(現状): select経路=override可、confirm(フォーム)経路=override無し=二重基準。`select`経路は**文法確定(`_apply_form_grammar_review`/`_write_grammar_sidecar` er128:1514-1534)・確定レコード(`_new_record`/`save_record` :1527-1531)・照合コードを作らない**。
- 照合コードAIF1/AIF2: er128_form_readable_restore_01.make_code:168-181。stem+d6(データJSONバイトsha256先頭6)+cand集合(c8)+term集合(t8)+**選択(s10)**+文法(g10)+コメント(m8)(+AIF2はn8=ニュアンス)。d6がデータJSON全体のhashなので、**フォームdataを再生成すると旧readableの照合コードは通らない**(git_history_lookup:231で旧版復元は可)。

## 3. Redundancy QAの判定箇所と停止箇所(全洗い出し)
判定: (a)候補全体1回(er119_kp_candidates_01.py:445-459、`redundancy_qa`doc+`flags.redundant_with`)、(b)確定集合(er119_kp_human_review_01.py:961-987 `_run_final_qa`、関数=er119_kp_candidates_01.make_redundancy_fn:656)。
**停止条件になっている箇所**
1. `validate_selection`のpair検査: er119_kp_human_review_01.py:566-570。呼出=op_select:694(select/confirm)、finalize_kp:1007、cmd_reconsume(er128:2095)。**Y Advがconfirmで拒否された主因**。
2. `finalize_kp`確定集合QA NG: er119_kp_human_review_01.py:1033-1043 -> reviewをPENDINGへ巻戻し・selection消去・`on_final_redundancy_ng`(er128_kp_confirmed_content_01.py:701-719: 確定レコードをRECONFIRMへ=確定喪失+CONFIRMED_CONTENT_ISSUE)・`KpReviewPending`で停止。ensure_kp_review:1458-1463でPENDING返却。
3. 判定不能: :983-984 (statusがPASS/NG以外=KpReviewError fail-closed)。重複とは別の**判定失敗**。維持対象。
4. AUTO(明示宣言のAI選定): auto_select(:577-591)が重複pair持ちを走査で除外、finalize AUTOは重複下位を除外して繰上げ(:1017-1030)、尽きるとSTOP。**人間選定ではない=仕様②の対象外(AI選定の最適化)**。維持。
5. 後続: runnerは`redundancy_qa`(=review.final_qa)によるSTOP分岐を持たない(Grep: er019/er026/er121/er119_kp_wiring_01に分岐無し)。assemble/gate/pagesにも無し。G0(確定内容保護、er128 on_finalize_post_write:683-)は成果物-レコード一致のみで重複は見ない。**停止は1,2に集約**。
6. 旧経路(Family A/B/C凍結ライン): er003_v1_n3_01_scaffold_generate.py:877-897(REDUNDANCY_NG -> retry -> NG_REVIEW_REQUIRED)等。27-7によりA/B/Cは開発対象外・X/Y/Z正式経路ではない -> **無変更**。Z mockの`REDUNDANCY_OK` stub(er026:2961)はtest用。
7. 別物(混同禁止): ニュアンス解説の重複判定(er134_nuance_explanation_01.py PROCESS_JUDGE、exporter rc=4 / er120_part2_wiring_01.py:589-591)は「ニュアンス候補とKP/文法の重複」を提示前に除く**提示前検査**(仕様①と整合する既存機構)。仕様②の対象(人間が選んだ表現同士)ではない -> 無変更。
Family差: 1,2はX/Y/Z・Std/Adv共通コード。Stdはvocab無効(Std Part1マーク無し)の場合のみvocab集合のQAが走らない。

## 4. retry/fallback/regeneration/resume/再選定
- ensure_kp_review(er119_kp_human_review_01.py:1370-): 候補sha一致のresumeは**再選定せずAPI 0**。本文変更(text_sha)でREBOUND(確定itemの出典文が残る)またはSUPERSEDED退避+再生成(:1396-1420、NG保持)。`op_reselect`は候補を再生成(SUPERSEDED退避)。
- 候補生成の外側retry: er119_kp_candidates_01.py:466-476。**backfill ON(既定)では撤去済み**(M-2/M-3、補完1回)。OFF(EIGO_KP_BACKFILL=0)ではn_auto<3かつgate_dropped/rescued_not_autoで再選定。`GATE_DROP_EXEMPT_STAGES`(er119_kp_backfill_01.py:25)は除外段のみ。**qa_failはdroppedでなくbackfill/retryを誘発しない**(現状は旗のみ=今回の隙間)。
- 確定済み選定: 確定レコード(er128 save_record)が保持。DEPENDENTSはstage依存(Y=er121_family_y_runner_01.py:46、Z=er062_family_z_writer_01.py:66)で、KP選定/Part1は`--regenerate-stage`の別系統(er026:1191「DEPENDENTSへは追加しない」)。選定データはkp_dir内(kp_candidates.json/kp_human_review.json/confirmed_selection.json)にありresumeで再提示されない。
- **確定集合QAのキャッシュ**: review.final_qa.key==_qa_key(selection)かつstatus==REDUNDANCY_PASSの時のみ再実行しない(er119_kp_human_review_01.py:1015-1016)。**NGを許容に変えるとstatus!=PASSで毎回有料API再呼出になる**(設計で要修正、WIRING_DESIGN B-2)。
- `finalize_kp(redundancy_fn=None)`(er128:2157,2254 `_try_refinalize`): 関数なしで確定集合QA未実施だとKpReviewErrorで諦め次回runner起動に委ねる。非ブロッキング化後もこの挙動(QA結果が未取得ならfinalizeしない)は維持が必要。

## 5. Family間差異表(X/Y/Z x Std/Adv)
| 項目 | X | Y | Z |
|---|---|---|---|
| KP Human Review共通経路 | er019:1022 `_kpw().run_kp_with_review` | er121_family_y_runner_01.py:583 | er026:2171(+`kp_redundancy_fn` hook :2159) |
| qa_fail旗・提示 | 共通generate_candidates | 同 | 同(+SRC D1/人称整合のdropが先に効く) |
| フォームdata | 共通exporter(--family X) | 同 | 同 |
| confirm(--from-readable) | 共通er128 | 同 | 同 |
| validate_selection redundancy拒否 | 共通 | 共通 | 共通 |
| finalize確定集合QA NG | 共通 | 共通 | 共通 |
| Std(a2)/Adv(b1b) | Stdはstd_part1マーク有でvocab有効、無で無効。Advは常時有効(全Family共通) | 同 | 同 |
=> 全Family同一実装。**個別Family修正箇所は無い**(共通module修正が全6組合せへ効く)。hook(`kp_redundancy_fn`)はtest注入用。

## 6. 承認済み規則との矛盾・整合(変更はしていない)
| 規則 | 場所 | 今回仕様との関係 |
|---|---|---|
| 「human review条件: いずれかのQAフィールドFAILならREVIEW_REQUIRED、自動retryなし、**人間承認で採用可**」`DECIDED`(ER-003-KP-01->02、2026-08-08) | CURRENT_SPEC.md:1987 | 仕様①は「REVIEW_REQUIRED候補を提示前に解決・原則提示しない」で、この「人間承認で採用可」運用を**置換**する。ただしQA基準(11 QAフィールド)自体は不変。2026-10-29ユーザー決定が上位。SSOT更新時に旧行へ『置換』を追記 |
| X/Z外側retry(REVIEW_REQUIREDは除外語付き再選定、`KP_OUTER_RETRY_MAX`=3、PASSのみ採用)DECIDED 2026-10-25 OPEN-504 | CURRENT_SPEC.md:1988 | **同方向・整合**。ただしPhrase7/Word5+backfill(ON既定)経路ではこのretryが撤去され(M-2/M-3)qa_failが旗として残っていた |
| Key Phrase Set Redundancy QA: REDUNDANCY_NG->選定やり直し(最大2回)、上限後`NG_REVIEW_REQUIRED` DECIDED | CURRENT_SPEC.md:1995 | 旧経路(run_key_phrases)の記述。X/Y/Z KP Human Review経路の確定集合QAは「NG->PENDINGへ戻し選び直し」。仕様②が置換(判定=4観点・10ペアは維持、停止機能のみ変更) |
| `accept-qa-fail` | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに記載0件(Grep) | 承認済み規則なし(実装上のoverrideのみ) |
=> **仕様①②と矛盾して変更不可の承認済み規則は無い**。旧行(CURRENT_SPEC:1987,1995)は新ユーザー決定でSSOT更新(置換追記)の対象。
