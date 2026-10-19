# ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02、2026-10-19、Status=`ITEMS23_OPUS_H_CONDITIONS_MET_PENDING_FABLE_WIRED_JUDGMENT`[委任_03、2026-10-19]。旧Status=`ITEMS23_FIXED_TESTED_PENDING_OPUS_AND_FABLE`[委任_02])

対象: 不具合②(Rewrite発動条件「両ASR合意」の削除=ユーザー決定`APPROVED_FOR_PRODUCTION`の原因調査+Production反映)と不具合③(Rewrite後の音声検査が書換え前の原稿と照合される不整合=OPEN-283)。
原文: `docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md`§3・§4。新規TTS 0・Azure 0・LLM 0・OpenAI ASR 0(既存転写再利用、実費JPY0)。HR Lock(`review_lock_state.json` sha256 `6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19`)前後一致。`run_e2e_04`配下は読取のみ。
結論の先出し: **②=「両ASR合意」ガードは一度も実装されていなかった**(コードは元からユーザー決定後の基本フローと同じ。条件削除に伴うコード側の削除対象は無く、docstring/仕様文の整理とRegression固定のみ)。**③=修正済み**(正解原稿の単一参照点`er020.resolve_expected_text_after_local_rewrite`を新設し、減速後再検証・再利用/継承の再判定がそれを読む)。run_e2e_04 Std part3_c1のLR版を修正後の正式関数で再検証すると書換え後文に対し`NORMALIZED_MATCH`(PASS相当)。

## §1 ②導入経緯と不一致原因(証拠付き)
| 日付 | 文書(行) | 内容 | 状態 |
|---|---|---|---|
| 2026-10-12 | `er058_output/RECONCILIATION_FINAL_REPORT_01.md` §6-2(L121-122)・D-9(L159)・L194 | Trial C/Aで「v0 3回全NGでも正しい音声のASR誤認が多い。LRが発火すると正しい原稿を書換える」。案R3=「LRは独立3系統のうち2系統以上が同じ差分でNG=合意誤読の場合のみ」。**新規仕様候補(未承認・未実装、USER_DECISION_REQUIRED)** | 候補 |
| 2026-10-12 | `OPEN_ITEMS.md` OPEN-290(L793) | 同案をOPEN候補化。「ユーザー判断待ち・未実装・未承認」 | 候補 |
| 2026-10-15 | `unified_all_roles_production_wiring_01/DESIGN_01.md` L87(§6-4)・L299・**L324(§4-7⑤)**・**変更表#17(L474)** | ユーザー原文§6「原稿の問題ではなくASR誤認と推定される場合は、安易に原稿を書き換えない」(L87に原文引用)を受け、発火条件⑤「両エンジン合意誤読=PrimaryとSecondaryの`identify_ng_span`差分spanが同一」を設計。変更表#17=`er020 run_local_rewrite_recovery`入口へ「合意誤読ガード」を追加(担当=委任_03) | 設計 |
| 2026-10-15 | `OPUS_REVIEW_A_01_VERBATIM.md` L81-83(OF-AUW-07) | 「判定に差分spanの一致を使うとMello/Mallowも同じspan(Melos)で『合意』になり、同じ段落の『LRしない』例示と矛盾する」。修正案=「両エンジンのASR側の語が一致、またはARPAbet距離が閾値以下」+Melos転写の単体test | 指摘 |
| 2026-10-15 | `DESIGN_02_ADDENDUM_01.md` L17・**§5(L113-114)** | OF-AUW-07を「採用」し定義を文章化(語一致 or **ARPAbet距離が閾値以下**)。**閾値の数値は未定義**。`docs/pm/OPUS_FINDINGS_LEDGER.md` L337: 反映状況=`未`、Status=`FABLE_ADOPTED` | 設計(閾値空白) |
| 2026-10-15〜16 | `IMPLEMENTATION_02b/03/04/05/06c/10/11/13.md`・`CLOSEOUT_PLAN_07.md` | **「合意誤読」「#17」「ガード」の実装記録は0件**(Grep全文)。委任_03の「未実装」欄(IMPLEMENTATION_03 L53)はLR script_version配線のみ言及。CLOSEOUT_PLAN_07 L76「retry・fallback・regenerationとの整合: 充足」、L136「LR後の整合: 充足」は**LR後v1/再TTS計数/Lock不変のみを検証**し、発火条件⑤の有無は項目に無い | 実装なし |
| 2026-10-16 | `CURRENT_SPEC.md` L2808・L2818(commit `2316deceb` 委任_07 SSOT草案) | DESIGN_01の発火条件(⑤含む)を**そのまま「仕様」として転記**。Status「`PRODUCTION_WIRED`(Fable独立照合=条件15、委任_14)」 | 仕様のみ |
| 2026-10-19 | `HR_LOCK_PART3C1_ROOT_CAUSE_01.md` §0-2・§4 | run_e2e_04 part3_c1でLR(Melos→He)が発火。コード(`er020:708-775`、`crosslevel:386-440`)に⑤が不在と発見。閾値未定義のため独断実装せずFableへ報告(R-B) | 乖離検出 |
| 2026-10-19 | ユーザー指示§3 | 「両ASR合意」条件の**削除**を正式決定(`APPROVED_FOR_PRODUCTION`) | 解決 |

**不一致の原因(推定ではなく証拠で確認できる範囲)**: (1) DESIGN_01の変更表#17(er020入口ガード)は委任_03に割当だったが、委任_03〜13の実装記録・test・commit(`git log -- er020_tts_retry_local_rewrite_01.py`: AUW期間の変更は10-16 `4a7ee50d7`[Family X配線]のみで`run_local_rewrite_recovery`のガードは無い)にガード実装が存在しない。(2) Opus指摘OF-AUW-07で**判定式が内部矛盾**とされ、ADDENDUMで「ARPAbet距離が閾値以下」へ改めたが**閾値が未確定**のまま、台帳の反映状況が`未`のまま閉じた(OPEN_ITEMSへの登録も無し。OPEN-290は10-12時点のR3候補でOF-AUW-07の後続ではない)。(3) 実装文書は「LR後v1/再TTS計数/HR Lock不変/JA・KP非LR」を検証対象とし、**設計書の発火条件⑤が実装されたかを突合する項目が完了条件15項目(CLOSEOUT_PLAN_07 §4)に無かった**。(4) CURRENT_SPECは設計書の転記であり、実コードとの行単位照合(E-1)を経ずに`PRODUCTION_WIRED`が付いた。分類=「未実装のまま配線完了と扱われた」+「閾値未定義で実装が保留され、保留がどこにも記録されなかった」の複合。別条件で代替した事実は確認できない(Grep: `agreed|合意|consensus`を含むLR関連コード0件)。
**OF-AUW-07の処理**: ADDENDUMで採用→OPUS_FINDINGS_LEDGER L337 `FABLE_ADOPTED`・反映`未`のまま。OPEN_ITEMS登録なし。→ 本委任でユーザー決定(条件削除)により**解消**(§2、台帳へ追記)。

### §1-b CURRENT_SPEC L2818「発火条件」の各項と実装の差(E-1)
| 条件(CURRENT_SPEC旧文) | 実装(関数:行) | 差 |
|---|---|---|
| slot3 NG | `crosslevel.generate_english_segment_with_fallback`(L81)の標準2回+fallback1回尽き後に`_local_rewrite_recovery_for_english_segment_with_fallback`(L302)。voice01/news_tail_fixも同型 | 実装あり(=ユーザー決定の基本フロー「最大2回再生成後にRewrite」) |
| role∈5 role | `enable_connected_speech_equivalence_layer`=`er020.connected_speech_enabled_for`(L163) | 実装あり |
| `lr_used==0` | 明示カウンタ無し。呼出が1生成につき1回で、LR再TTSがNGなら`None`→HR(2回目LRなし) | 構造的に満たす(明示判定は無い) |
| 3NGにSecondary障害を含まない | 無し(U4=OPEN-371、IMPLEMENTATION_06c L78「Secondary障害のみの最終STOPPEDをLock/LRより前に止めるか」はユーザー判断待ち) | **未実装(今回の削除対象外。判断候補)** |
| 両エンジン合意誤読 | **無し(一度も実装されていない)** | **ユーザー決定で削除(本委任)** |
| 既存7 Gate | `er020.select_final_candidate`/`build_full_candidate_records`(L655-678) | 実装あり |
| LR後v1=標準Prompt・1 attempt・force_secondary・`LR_REWRITTEN` | `crosslevel._local_rewrite_recovery..._retts_fn`(L409-423)、`attempt_ctx={"script_version":"v1"}` | 実装あり |

## §2 ②Production反映
- `CURRENT_SPEC.md` L2808(基本フロー)・L2818(LR節)を最小修正: 「合意誤読のみ」「両エンジン合意誤読…・ASR誤認と推定される場合は書き換えずHR」を削除し、基本フロー「TTS初回→Primary/Secondaryの承認済み検証→NGなら最大2回のTTS再生成→なおNGならRewrite」を明記。他の条件(slot3 NG/5 role/lr_used/Secondary障害/7 Gate)・LR後v1・HR Lockは不変。新旧はRESULT_PACKET_FZAQ2.md参照。
- コード: **「合意」条件の名残は0**(Grep: `er020`/`crosslevel`/`er003_v1_n3`/`voice01`/`news_tail_fix` に`合意誤読|agreed_misread|consensus`の実装・未使用引数・flag・test期待なし。`news_tail_fix.py:55`の`ASR consensus ≠ 発音の証明`は別趣旨の既存コメント)。したがって**条件削除に伴うコード削除は無し**。`er020.run_local_rewrite_recovery`のdocstringに「発動条件=基本フロー・旧⑤はユーザー決定で削除/実装されたことはない」を追記(挙動不変)。
- 未承認条件の追加なし。他の発動条件を緩めていない(`stop_retrying`経由の早期LRはcascade有効=Production既定では常にFalse[`er006_secondary_asr_01.py:236,973`]で、Regression(e)で固定。`FEATURE_FLAG_SECONDARY_ASR_ENABLED=False`のロールバック経路[`:717`]でのみ`val.evaluate_attempt`由来のTrueが残り得る=既存のrollback設計、本件で変更せず)。
- Regression(e)(`er020_lr_post_rewrite_expected_text_fzaq2_test_01.py`): 標準2+fallback1の通算3回を使い切った後でのみLRへ進む/fallbackが承認済み検証(統一judge)に合格すればLR不到達/fallback本体が`secondary_asr.evaluate_attempt_with_cascade`+`force_secondary=True`(M1・Tier3・音韻同等性を含む既存層)を必ず通る/cascade有効では同一signature連続でも`stop_retrying=False`。
- **①との整合(Fableが委任_03で統合)**: 「Rewrite前のNG判定が①の修正で変わり得る箇所」=(i)`_run_a2_minimal_fallback_attempt`(crosslevel L311)内の`secondary_asr.evaluate_attempt_with_cascade`(Primary: Tier1/CMU Case A・homophone/**M1**=`er006_m1_multi_candidate_01.py:407 _post_check`・`:425 _entry_gate`/**F1 Pattern A**=`er011_b1_connected_speech_validator_01.py:153-168`/**Tier3**=`er021_...py:731 corroboration_supports`/統一judge`er078_asr_unified_judge_01.py:352`)。①が音韻同等性判定の棄却条件(M1/F1/Tier3のいずれか)を修正すると、これらの判定がNG→PASS(_WITH_WARNING)になり、**標準attempt1/2やfallbackの段階でPASSして通算3回に達する前に終了**し、LRに到達する件数が減る(part3_c1型=Melos+非歯擦音後続は①次第でLR自体が起きない)。(ii)`generate_english_segment_with_fallback`の標準attempt(`generate_narration_snippet_verified_strict`)内の同じ判定。(iii)LR後v1の再TTSの判定(同関数、`script_version="v1"`、LR_REWRITTEN警告)。②③の修正は判定ロジックに触れていないので、①の変更とは独立に統合できる(③の正解原稿の参照点は判定関数の外側)。

## §3 Rewrite採用〜HR移行の実フロー(関数:行、③修正後)
1. `n3_tts.generate_a2_segment_with_slowdown`(L310)の外側ループ(最大`max_slowdown_attempts`回、通算TTS`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS=3`[er011:80]を共有)。
2. `crosslevel.generate_english_segment_with_fallback`(L81、`@guarded_generate`=HR Lockのガード): 標準2回(`generate_narration_snippet_verified_strict`)→NGならfallback(`_run_a2_minimal_fallback_attempt` L311、最大`3−標準消費`回、3回目直前に600秒cool-down)。各attemptの判定は統一judge(Primary/Secondary/M1/Tier3/音韻同等性)。
3. 通算3回なおNG(status=STOPPED)→`_local_rewrite_recovery_for_english_segment_with_fallback`(L302/L386)→`er020.run_local_rewrite_recovery`(L708): NG span特定→Luna候補→7 Gate→採用→再TTS(`_retts_fn` L409、標準Prompt・1 attempt・`force_secondary=True`・`script_version="v1"`)。再TTSがPASS系ならstatus=OK・`local_rewrite_recovery`・`canonical_text_before_local_rewrite`付きで返る(L437)。再TTSがNGなら`None`→元のSTOPPEDのまま(HR Lock経路)。
4. 呼出元へ戻り、`n3_tts.apply_a2_slowdown_postprocess`(L182): wav→`_original.wav`にcopy→ffmpeg 6%→`routing.transcribe`→**正解原稿=`retry_primitive.resolve_expected_text_after_local_rewrite(result, tts_input_text)`(L206)**→`_post_slowdown_unified_judge`(L121)。PASS/PASS_WITH_WARNING→status OK(`asr_judgement`は減速後recordに更新、減速前は`asr_judgement_pre_slowdown`へ退避)。NG→STOPPED。
5. 減速後NGで通算TTS予算が残る場合は外側ループが次周を**元の原稿から**取り直す(retry: 新しい生成の正解原稿はその生成結果が決める。LRが再採用されればその周は書換え後文)。予算尽きなら`is_last_slot=True`でHR queueへ1行→`finalize_a2_slowdown_final_ng`(L288)→`review_lock.record_outcome(out_path, tts_input[=元の原稿], "en", STOPPED)`(er011:357)→Lock=`HUMAN_REVIEW_REQUIRED`→Z側`FamilyZTtsClipFailedStop`。**Lockのkey(canonical sha)・承認記録(`record_human_approval`のcanonical_text_sha256)は元の原稿のまま**(③の修正で変更しない。HR承認の同一性とLock状態を維持するため)。
6. 整合確認: ③の修正前は手順4が元の原稿で判定→LR採用の正しい音声がSTOPPED→HR Lockへ行っていた(run_e2e_04 part3_c1)。修正後は手順4が書換え後文で判定し、Primary PASSならそのまま採用(PASS_WITH_WARNING警告は再TTS段階の`LR_REWRITTEN`で付与済み、試聴リストに載る)。最終NG(書換え後文とも一致しない)ならHR Lockへ遷移する(Regression(d))。

## §4 ③原因(原稿の保持と更新)
| 保持先 | LR採用時 | 実体 |
|---|---|---|
| `tts_input`(呼出元の引数) | **更新されない** | `generate_a2_segment_with_slowdown(tts_input,…)`/`generate_with_a2_slowdown_outer_loop(name, tts_input,…)`の関数引数。LRはその内側(`generate_english_segment_with_fallback`)で完結し、戻り値dictにしか書換え後の文が現れない |
| `result["text"]` | 書換え後に更新(再TTSが送った文) | `retts_fn`の戻り値(`generate_english_component_minimal_instruction`)の`text` |
| `result["local_rewrite_recovery"]` | 追加(`selection.selected.rewritten_segment`、`retts_result.text`) | `resolved`(crosslevel L433-438) |
| `result["canonical_text_before_local_rewrite"]` | 追加(書換え**前**) | 同 |
| `last_asr_text` | LR入力(Primary転写)のみ。検査の正解原稿ではない | crosslevel L257-272/L302 |
| manifest/`*_original.wav`付随json | 原稿の保持なし(`attempts/..._attemptN.json`は各attemptの転写) | — |
| Lock key/承認記録 | 元の原稿のsha | `record_outcome`/`record_human_approval` |
→ 原因: `apply_a2_slowdown_postprocess(name, narration_dir, tts_input_text, result,…)`が**呼出元から渡された`tts_input_text`(LR前の原稿)をそのまま**統一judgeの`canonical_text`(期待テキスト)にしていた(`n3_tts`旧L214付近)。LR採用情報は`result`に既にあったが減速後再検証は参照していなかった。LR設計(DESIGN_01 §4-7「LR後v1の判定は統一judge」)は再TTS直後の判定のみ記述し、**後続のA2 6%減速後再検証の正解原稿**を規定していなかった(OPEN-283、2026-10-12起票)。
実ログ裏付け(run_e2e_04 Std part3_c1): `er011_output/attempt_history.jsonl` 行15172(LR final_status=RESOLVED_BY_LOCAL_REWRITE、changed_span Melos→He)、行15173(内側生成 result_status=OK・final_lock_state=RESOLVED)、行15174-15175(`A2_SLOWDOWN_REVERIFY` status=STOPPED・減速後転写`…He drank, got onto…`・canonicalは`…Melos drank…`)、行15176(Lock=HUMAN_REVIEW_REQUIRED)。`er021_output/.../telemetry.jsonl`行9619-9621: `canonical`=Melos入り vs `asr`=`He drank`。`lr_slowdown_whatif_part3c1_10_result.json`: 旧原稿=ASR_VALIDATION_UNCERTAIN/書換え後文=NORMALIZED_MATCH。

## §5 ③修正と横展開
- 修正(Productionコード3箇所、新Gate/閾値なし): (1)`er020_tts_retry_local_rewrite_01.py:784 resolve_expected_text_after_local_rewrite(result, canonical_text)->(text, source)`=**正解原稿の単一参照点**(純関数・API 0。LRが`RESOLVED_BY_LOCAL_REWRITE`で採用済みなら`selection.selected.rewritten_segment`→`retts_result.text`→`result["text"]`の順で実送信文、それ以外は元の原稿)。(2)`n3_tts.apply_a2_slowdown_postprocess`(L206): 判定前に(1)で期待テキストを置換(Ledger PhraseList導出も同じ値)、`result["post_slowdown_expected_text_source"]`(`local_rewrite_text`/`canonical_text`)をadditiveに記録。(3)`er019_family_x_validation_inheritance_01.rejudge_with_current_judge`(L248-254): 再利用/継承/reuse-guard(`er078_reuse_value_guard_01.guard_entry`経由)の保存転写再判定も(1)を読む(LR記録のあるentryのみ。`probe`/Master Store/bulk再判定はLR記録が無く従来どおり)。
- 経路別の参照(全て上記の同一ソース): 減速後再検証=`apply_a2_slowdown_postprocess`(Z narrator `er063:781`、Z Dialogue `er063:791`の`generate_with_a2_slowdown_outer_loop`、X A2 `er019`、Voices `er012_b_family_voices_a2_production_01:699,751`、全て同関数) / retry(外側ループ)=各周の`result`から再導出 / fallback=`fallback_used`付きLR結果も同じキーを持つ / resume・再利用・継承=`rejudge_with_current_judge`(上記(3)) / 最終検証・HR遷移=`finalize_a2_slowdown_final_ng`は意図的に元の原稿(Lock key)。
- 横展開確認(Grep `tts_input|expected_text|script_text|original_text|rewritten`): Family X B1(`voice01.generate_charon_english`/`news_tail_fix.generate_news_narration_wide_margin`)はLR採用結果をそのまま返し、後段に原稿照合する検査なし(再TTS時点で書換え文を検査済み、A2 6%減速なし)→変更不要。Family X A2/Z(narrator・Dialogue・Voices A2)=A2 6%減速経路で`apply_a2_slowdown_postprocess`を共有→(2)で一括修正。Family Z b1b・topic_intro・charon_en=減速なし→変更不要。Family Y(`er036_family_y_voice_structure_trial_01.py`)=Trial、Production関数を呼ばずLR/減速なし→変更不要(記録のみ)。Legacy A/B/C: 共有`n3_tts`関数を使うLegacy A/Bの呼出(`er008_*`/`er009_*`/`er011_*`の各単発script)は同関数を通るため**共有コードの挙動としては修正が及ぶ**(LR記録のないresultは従来どおりなので既存の挙動は不変)。Legacy専用のコード複製・個別変更はしていない(記録のみ)。
- 検出した同種の不整合で今回は変えなかったもの: `er063.build_entry`の`entry["text"]`/`canonical_text`は元の原稿(監査・Lock・HR承認の同一性のため意図的。書換え後文は`audio_text_deviation`に記録済み)。`er019_family_x_validation_inheritance_01._text_matches`(entryの出自照合)は元の原稿で照合(識別子としての役割、LR後文で照合すると別segmentと誤認するため変更しない)。

## §6 Regression
新規`er020_lr_post_rewrite_expected_text_fzaq2_test_01.py` 18 passed(mock ASR/Azure、API 0): helper単体3(LRなし/LR採用[selection・retts text]/未採用LR記録)、(a)2(LR採用後の減速後再検証が書換え後文で照合・Azure 0 / 旧参照相当は同じ転写がSTOPPED=検出力)、(b)3(LR非採用は従来どおりcanonical/不一致は従来どおりSTOPPED/未採用LR記録は原稿不変)、(c)4(外側ループ周ごとに正解原稿が結果に従う[1周目LR→NG、2周目通常→OK]/Dialogue outer loop/Ledger PhraseList導出も書換え後文/再利用・継承の保存転写再判定・value guard)、(d)1(最終NG→`finalize_a2_slowdown_final_ng`→`record_outcome(text=元の原稿)`・Lock=HUMAN_REVIEW_REQUIRED・`human_review_required=True`)、(e)4(通算3回使い切り後にのみLR/fallback PASSならLR不到達/fallbackが統一judge[force_secondary]を通る/cascade有効で`stop_retrying`常にFalse)。ミューテーション確認: `apply_a2_slowdown_postprocess`の置換行を無効化するとtest 4件(a・c×3)が失敗(検出力あり)、復元済み。
関連suite+全体suite(per-fileランナー`er058_output/unified_all_roles_production_wiring_01/patch_03b/run_tests_per_file.py` W=4、`*test*.py` 347+1ファイル): 修正前baseline files=347 passed=8539 failed+error=153 → 修正後 files=348 passed=8555 failed+error=155。新規failは2件のみ(`er019_family_x_pointless_01_test_01.py::FamilyAUnchangedTest::test_family_a_files_have_no_working_tree_diff`、`er064_kp_int_01_test_01.py::ProductionUnchanged::test_no_tracked_py_or_template_modified`)=**未commit差分検出guard**(IMPLEMENTATION_03/04のgamma 4 idと同種、commit後に解消する既知の型)。commit後に再実行して差分0を確認(§7末尾に追記)。

## §7 正式経路検証(offline、新規TTS 0)
`item3_formal_path_verify_01.py`(`ITEM3_FORMAL_PATH_VERIFY_01.json`)。run_e2e_04の`narration/full_story_part3_c1_original.wav`(sha `40c6907e…`、LR版・減速前)を一時dir`run_e2e_04_verify_fzaq2/`へcopyし、修正後の`apply_a2_slowdown_postprocess`(ffmpeg 6%減速→Primary→統一judge)を実行。ASRは、再現した減速後wavのsha256が実run(`713252709b97…`)と**一致**したため実runの保存転写(AH行15175)を再利用(OpenAI ASR 0呼出・Azure 0・LLM 0・TTS 0。実費JPY0)。
| ケース | 期待テキスト | status | 分類 |
|---|---|---|---|
| 修正後(正式経路) | 書換え後文(`…He drank, got onto his knees…`) | **OK** | **NORMALIZED_MATCH**(`asr_judgement.state`=PASS) |
| 旧参照相当(LR記録なし) | 元の原稿(`…Melos drank…`) | STOPPED | ASR_VALIDATION_UNCERTAIN(Azure呼出は遮断、本番と同じNG) |
本体run dir・`review_lock_state.json`(sha一致)は不変、HR Lockは解除していない(Lockの扱いはFable/ユーザー)。

## §8 E-1 Family別配線状況表
| Family | 経路 | LR | 後続の原稿照合 | ③の状態 |
|---|---|---|---|---|
| X B1 | voice01.generate_charon_english / news_tail_fix | あり(5 role) | 再TTS時に書換え文で検査。後段照合なし | 変更不要 |
| X A2 | crosslevel+n3.generate_a2_segment_with_slowdown | あり | 6%減速後再検証 | **修正済み** |
| Z narrator A2 / Dialogue A2 | n3.generate_a2_segment_with_slowdown / generate_with_a2_slowdown_outer_loop(er063:781,791) | narratorあり・Dialogue内側はLRなし(voice body) | 6%減速後再検証 | **修正済み**(同一関数) |
| Z b1b・topic_intro・charon_en | news_tail_fix / crosslevel / voice01 | あり | 減速なし | 変更不要 |
| Y | `er036_family_y_voice_structure_trial_01.py`(Trial) | 呼ばない | — | 記録のみ |
| Legacy A/B/C | `er008_*`等の単発script・Family A/B/C runner | 共有関数経由 | 共有`n3_tts`を通る | 共有コードの挙動として修正が及ぶ。専用の変更なし |
| 再利用/継承(X/Z/C共通) | `rejudge_with_current_judge`・`guard_entry` | — | 保存転写の再判定 | **修正済み**(LR記録entryのみ書換え後文) |

## §9 Opus観点案(条件C: ③はCross-Family共通経路の変更。Fableが依頼)
(1)単一参照点の妥当性: `selection.selected.rewritten_segment`→`retts_result.text`→`result["text"]`の優先順は、LR採用結果の実形(voice01/news_tail_fix/crosslevelの3実装)すべてで再TTSに実際に渡した文と一致するか。`result["text"]`が正規化後(`tts_safe_*`)の文を持つ経路は無いか。(2)Lock key/HR承認(`record_outcome`/`record_human_approval`のcanonical sha)を元の原稿のまま維持する判断が、承認済みHR Lock仕様(「同一segment・同一文面の再runは`approve_regenerate`まで0 API」)と整合するか。(3)品質面: 修正で「名前が消える書換え文(Melos→He)」の自動採用が増える(これまではHR Lockで止まっていた)。LR自体は承認済みでLR_REWRITTEN警告+試聴リスト(事後確認)が付くが、このQ影響をユーザー判断に上げる必要があるか(§3の手順6)。(4)`rejudge_with_current_judge`への波及(再利用ガード・継承・clobber restore)が過剰ブロック/過剰許容を生まないか。(5)`stop_retrying`のrollback経路(`FEATURE_FLAG_SECONDARY_ASR_ENABLED=False`)が「最大2回再生成後のみRewrite」を破り得る点を放置してよいか。(6)CURRENT_SPECが記す条件のうち「3NGにSecondary障害を含まない」「`lr_used==0`の明示判定」が未実装/暗黙のままである点(今回の削除対象外)の扱い。

## §10 委任_03: Opus_H(GO_WITH_CHANGES)必須修正6条件の充足(2026-10-19)
Opus_H逐語=`OPUS_REVIEW_H_01_VERBATIM.md`(16,696文字、sha256 `2e06aeea2dac61e619eae7a29e08e75b1a8b2298edd5810a7224c0275d2f05a8`)。Opus_G逐語=`OPUS_REVIEW_G_01_VERBATIM.md`(15,845文字、sha256 `cfd567b2a04fde06191b518d6a98c33a0684a93a134f6d94dc81b7ad90ed8774`)。PRODUCTION_WIRED判定はFable(本書では判定しない)。
**Status注記(条件6)**: runtime evidence=offline正式経路(実wav・実ffmpeg・保存転写、§7)。**LRのlive発火は未観測**。`post_slowdown_expected_text_source=local_rewrite_text`のlive観測は次回LR発火時に確認する。条件1〜3の新規testもmock(ASR/Secondary/TTS/ffmpeg)で、API 0・新規TTS 0。
| 条件 | 実装箇所 | test(`er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py`) | 結果 |
|---|---|---|---|
| 1 論点2 M5(LR後M1凍結のanchor引継ぎ、OF-179) | `er006_secondary_asr_01.py` `_m1_frozen_for(canonical_text, *, anchor_text=None)`(anchor凍結済み→その`segment_started_at`と保存snapshotで書換え後文を凍結[キー`("anchor",anchor,canonical)`]。anchor未凍結/凍結失敗→**None=M1不発**、現在時刻・Noneでは凍結しない)。受け渡し=`attempt_ctx["m1_anchor_text"]`(`er078_asr_unified_attempt_ctx_01.build_attempt_ctx(m1_anchor_text=)`、未指定ならキー無し=従来dictと同一)。読取=`evaluate_attempt_with_cascade_detail`(`actx.get("m1_anchor_text")`)。配線4箇所: crosslevel `_retts_fn`(`er003_v1_crosslevel_audio_02_common.py:415-417`)、voice01 LR再TTS(`generate_charon_english(m1_anchor_text=)`)、news_tail_fix LR再TTS(`generate_news_narration_wide_margin(m1_anchor_text=)`)、`apply_a2_slowdown_postprocess`→`_post_slowdown_unified_judge`(出典が`local_rewrite_text`のときのみ元原稿を渡す) | (i)`test_i_entry_upserted_after_original_segment_start_is_excluded_after_lr`・`test_i_end_to_end_lr_retts_judge_does_not_accept_late_candidate`(旧経路=anchorなしは後続upsertを候補に入れて受理する再現を含む) (ii)`test_ii_entry_before_original_segment_start_stays_candidate` (iii)`test_iii_unfrozen_anchor_disables_m1_and_never_freezes_with_now` (iv)`test_iv_no_lr_path_is_unchanged`(ctx dict・`_m1_frozen_for`呼出形・出力dictが従来と一致) 配線: `test_wiring_slowdown_passes_anchor_only_when_lr_adopted`・`test_wiring_crosslevel_and_leaf_signatures_carry_anchor` | 11 passed(本ファイル全体) |
| 2 論点1 1-a(Z形entry) | `er020_tts_retry_local_rewrite_01.py` `resolve_expected_text_after_local_rewrite`: `local_rewrite_recovery`が無いentryは2次出典`audio_text_deviation.audio_text_after`(非空・元原稿と異なる場合のみ)を読む(X形の挙動は不変)。`er063.build_entry`は変更なし | `test_condition2_z_entry_resolves_to_rewritten_text`・`test_condition2_z_entry_guard_and_rejudge_use_rewritten_text`(実`build_entry`で作ったZ形entryに対し`rejudge_with_current_judge` ok・`guard_entry` blocked=False、LR記録なしZ entryは従来どおりNG) | passed |
| 3 論点3(HR queue行の元原稿記録) | `er003_v1_n3_01_tts_generate.py` `_post_slowdown_unified_judge(lock_canonical_text, expected_text_source, m1_anchor_text)`→`er006_secondary_asr_01._log_human_review`が`lock_canonical_text`/`expected_text_source`を追加の形で記録(未指定の経路は従来行と同一)。HR承認手順の明記=`er003_v1_n3_01_assemble.py` `record_human_approval` docstring(HR手順書は独立文書が存在せずこのdocstringとCURRENT_SPEC LR節が唯一の手順記述)+CURRENT_SPEC LR節 | `test_condition3_hr_queue_row_records_lock_canonical_text_and_source`・`test_condition3_hr_queue_row_unchanged_without_lr` | passed |
| 4 論点4・1-b(CURRENT_SPEC注記) | `CURRENT_SPEC.md` LR節: 「3NGにSecondary障害を含まない」=未実装・OPEN-371(U4)ユーザー判断待ち/`lr_used==0`=構造的に満たす(明示判定なし)/『減速後再検証・retry・fallback・resume・最終検証』を実態(最終HR遷移・Lock keyは元の原稿、resumeはLR記録のあるentryのみ[Z形は`audio_text_deviation`]、M1凍結のanchor)へ訂正。rollback(`FEATURE_FLAG_SECONDARY_ASR_ENABLED=False`)時の早期LR=既知の逸脱(rollback時のみ、既定True)をOPEN-422内へ1行記録(挙動変更なし) | (文書) | 反映 |
| 5 全体suite再実行 | 下記§10-1 | | 下記 |
| 6 Status注記 | 本節冒頭 | | 反映 |
**`_M1_FROZEN_CACHE`はプロセス内で保持され(`_reset_m1_freeze_cache()`でのみ消去)、別segment・別runでも同一文なら古い凍結を使い回す(結果はより厳しい側に倒れるだけで無害、Opus_H論点2 任意改善)**。
**未実装のまま残す事実(新仕様なので実装しない)**: entity保全Gate(固有名詞→代名詞の書換えはLLM Gate[文脈なし]のみで採用、事後試聴で確認=Opus_H論点5)。rollback時の早期LR(上記)。①(P1)はユーザー判断待ちのため未実装。

### §10-1 条件5: commit後の全体suite再実行(委任_03、`834b93a6d`+`75bb156c6`後)
同じper-fileランナー(`er058_output/unified_all_roles_production_wiring_01/patch_03b/run_tests_per_file.py`、`W=4 .venv/Scripts/python.exe <runner> <out.json> ""`、`*test*.py` 全件)。結果: files=351 passed=8595 failed+error=153。
- **fail集合(テストID単位)はbaseline(委任_02前、files=347 passed=8539、148 id)と完全一致(新規fail 0・消滅は下記2件のみ)**。委任_02後(150 id)との差=未commit差分検出guard2件(`er019_family_x_pointless_01_test_01.py::FamilyAUnchangedTest::test_family_a_files_have_no_working_tree_diff`・`er064_kp_int_01_test_01.py::ProductionUnchanged::test_no_tracked_py_or_template_modified`)がcommit後に解消(予告どおり)。差0を確認。
- passed増分の内訳: 本修正の新規test 11(`er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py`)+並行agent(B3 Trial、`er083_*`)の新規27 (18+9)+guard解消2 = 8555→8595。
- 関連suite(ファイル名が`er020|local_rewrite|er003_v1_n3|crosslevel|er063|slowdown|secondary_asr|m1_multi|human_review`に一致するファイル、per-file): 438 passed / 3 failed。3件(`er007_ja_secondary_asr_01_test.py::test_koro_kanji_variant_confirmed_by_reading_candidates`・`::test_single_engine_repetition_does_not_confirm_orthographic_variant`、`er020_tts_retry_local_rewrite_fullseg_test_01.py::RegressionCorpusTest::test_recorded_candidates`)はbaseline(委任_02前)から存在する既知failで本修正と無関係(fail集合の一致で確認)。委任文のルート全体`pytest -k`はルート配下の`*_output`内スクリプト(`sys.exit`をモジュール直下で呼ぶもの、`er052_output/...`・`er064_kp_opt_01_fix_test_02.py`)でcollectionがINTERNALERRORになるため、実測にはper-fileランナーを使った。
- 注: 自分のcommitは並行agentのcommit(`834b93a6d`、B3 Trial SSOT)の実行と同時刻に重なり、私がstage済みだった16ファイルがその1commitに収録された(commit messageは並行agent側の文面)。内容は欠落なく履歴に入っている。

