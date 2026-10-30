# KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 委任_02 EVIDENCE(2026-10-30)

状態: N5を正式Production経路へ配線し、全6経路でruntime evidenceを取得した。**PRODUCTION_WIREDとは呼ばない**(Fable独立受入待ち、判断候補J2・未観測項目あり。§8)。
証跡の置き場: 本ファイルと `ev02/`(M10=`ev02/m10/`、X=`ev02/x/`、Y=`ev02/y/`、Z=`ev02/z/`、QA12=`ev02/qa12/`、テスト=`ev02/tests/`、起動記録=`ev02/launches.txt`)。複製run dir本体(音声なし)は一時領域のため未commit。判断に要る成果物(kp_candidates.json・費用log・console log)は`ev02/`へ複製済み。

## 1. 実装(単一統合点)
- 新module `er138_kp_n5_generalization_01.py`(Trial 03 `kpg04_methods.py ARMS['N5']` のPrompt/schema/規則定数・検証関数をAST抽出で逐語移植。Trial codeはimportしない)。方式id `N5@T3-2026-10-30`。
- 配線: `er119_kp_candidates_01.py`の `_generate_candidates_impl`/`_gate_chain`/`_run_backfill` 1箇所(X=er019:997・Y=er121:583・Z=er026:2218は全て`run_kp_with_review`→`make_generate_fn`→`generate_candidates`経由。静的test `TestStaticReachability`で固定)。flag/kill switch無し(既定ON)。N5失敗=外側retry/STOP、旧方式へは戻らない。
- Opus条件M1〜M13: M1=`_gate_chain`でmerged直後・CMU post-canon前にL3、dropは`drop_rank(stage=n5_*)`。M2=L1(B1+P7→Gate→SEL→pick)をcall1とcall2の間、B1も`_screen_human_ng`。M3=`NOT_COUNTED_STAGES`に`n5_pool/n5_select/n5_pick`、`n5_generalize/verify/check`は計数。M4=P7由来canon/ga glossのみPROD_GLOSS、LLM段へ渡すspanはselection_phrase。M5=canon系fieldは`n5.canon_pre`へ退避しN5対でALIGNEDを再決定(`gloss_alignment.status=N5_CONFIRMED`)、人称整合はX/Y/Z。M6=5語上限はN5形。M7=送信形の同一性test。M8=CHK5は全非revert。M9=CHK5欠落verdictは欠落分のみ1回再要求→`n5_check`でdrop。M10=§3。M11=§7。M12=`generate_candidates`内threadなし。M13=Geminiの`model_version`を正規化比較、不一致=`N5ContractError`(STOP)。
- 付随: routing `KP_N5_VERIFY`(gemini-3.8-flash)/`KP_N5_CHECK`(gpt-6.1-sol)、`pricing_snapshot.json`にgemini-3.8-flash単価、WordNet 3.0を`data/nltk_data/corpora/wordnet.zip`(sha256 cbda5ea6…、fail-closed)に同梱、`requirements-ci.txt`にnltk系固定、Y/Zの`STAGE_EST_JPY["kp"]` 10→20(budget guardの見積り)。

## 2. Trial 03との一致(API 0)
- Trial cache keyを再計算して一致(model・user・schema・effort・think_budget=Prompt/設定同一性の証明)。記録応答replayで19ケース(ALL14+HELDOUTのうちcache完全なもの)の最終itemがTrial記録と**完全一致**。moon_a2のみTrial cacheにB1下流の応答が無く再現不能(除外、記録)。
- Prompt sha16: B1 97dd3c28…/GEN5_EXTRA a4252120…/GEN2_RULES 32f51f35…/VER5 1483f97b…/CHK5 b10a6edc…、FLAGS_V1 hash 3bba7ad2cc6a(CURRENT_STATE_01 §4の値と一致)。
- 必須回帰(原文§4A①〜⑦)は`er138_kp_n5_generalization_01_test_01.py`(51)で固定: hear it out→hear someone out、take points away from→take something away from+訳修正、keep one's eye on境界、set a lower limit→set a limit、took an unexpected turn→take a turn、旧語義のgloss残存防止、良質候補保持(19ケースexact)。

## 3. M10 統合replay(実API、Production `generate_candidates`公式経路、判定基準は実行前固定=`ev02/m10_thresholds_fixed.md`)
対象4level(untidi_a2/untidi_b1b/melos_a2/jwst_m_b1b)。費用 **¥21.80(M10上限¥20を¥1.80超過)**: 並列2本ずつ起動したため事前合算guardが効かなかった(運用ミス、§9)。jwst_m_a2は費用上限のため未実施。

| 集計 | 値 |
|---|---|
| Trial生存候補(分母) | 28 |
| Productionで同span保持 | 17 |
| 既存Gateで失われた | 1(3.6%、基準15%以下)。untidi_b1b `gets heated`: 既存救済`er125.qa_rejudge`の応答keyが不一致でNOT_REJUDGED→`rescue_unverified`でfail-closed drop(N5前段、既存Gate) |
| N5が落とした(n5_*) | 1(untidi_a2 `make life work`: SELがcls=Fと判定) |
| 未再現(LLM非決定性、Production側にspanが現れない/重複扱い) | 9 |

§4A: ①hear it out→hear someone out(untidi_a2/b1b)=保持 ②take points away from→take something away from(untidi_a2)、taking points away→take points away(untidi_b1b、GEN5が直接SAME)=保持 ⑤took an unexpected turn→take a turn(jwst_m_b1b)=保持(CHK5=MODIFIER_DROPPED_OK)。**③keep one's eye on(melos_a2)=未再現**(Production側P7/B1が`kept his eyes on them`を出さなかった)。**④set a lower limit=失われた**(jwst_m_b1b: B1は`set a lower limit`を返したが、P7候補`a lower limit`との包含dedupe(`n5_pool`)で除外され、そのP7候補はSELがF判定→superset側も残らない。Trial逐語の`collect_pool`と同一ロジック)。

**判定: J2発動**(基準(a)「§4A①〜⑤のいずれかが失われた」に③④が該当。ただし原因は既存Gateではない[③=LLM非決定性による未生成、④=N5のpool包含dedupeとP7候補の相互作用]。基準(b)は3.6%で非該当)。是正せず判断候補として報告(§8 J2)。詳細=`ev02/m10/analysis.txt`、各level結果=`ev02/m10/<case>/result.json`。

## 4. 6経路 runtime evidence(正式runner CLI、複製run上のKP段のみ。本文・TTS再生成0)
実行コマンド(いずれも`stop_scope_check_01.py`rc=0確認後): X=`er019_family_x_audio_production_runner_01.py --slug untidiness_family_resource --run run_n5ev --level both --stage scaffold --scaffold-only kp`、Y=`er121_family_y_runner_01.py --slug redelivery_fee --run run_n5ev2 --stage kp --mode real`(+theme-package/reuse-manifest)、Z=`er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --slug the_tell_tale_heart --run run_n5ev --stages kp --mode real`。複製元=X untidiness_family_resource__run_fx4_01、Y redelivery_fee/run_01、Z the_tell_tale_heart/run_sf_prod_02(音声・key_phrases・KP/TTS provenance entryを除いた複製)。全runはKP Human Review PENDING(rc=4、想定どおり)で停止し、候補doc(`kp_candidates.json`)にN5記録が残る。

| 項目 | X a2 / b1b | Y a2 / b1b | Z a2 / b1b |
|---|---|---|---|
| actual model_id(応答値) | B1/SEL/GEN5=gpt-6-luna、VER5=gemini-3.8-flash、CHK5=gpt-6.1-sol(全6level共通) | 同左 | 同左 |
| Gemini model_version | gemini-3.8-flash(正規化一致、全level) | 同左 | 同左 |
| 候補数 / うちN5対象(phrase) | 10/6、10/5 | 11/6、11/7 | 7/4、10/5 |
| used_form語数分布(N5対象) | 2語1・3語3・4語2 / 2語2・3語3 | 2語3・3語1・4語1・5語1 / 2語3・3語2・4語2 | 3語3・5語1 / 2語2・3語3 |
| 英日本文の一致(used_form==key_phrase==n5.display_form、japanese_gloss==n5.gloss_ja、source_spanが本文に実在) | 全件一致 | 全件一致 | 全件一致 |
| gloss_alignment_status(再決定後) | 全ALIGNED(`gloss_alignment.status=N5_CONFIRMED`) | 全ALIGNED | 全ALIGNED |
| B1 poolのGate/dedupe drop(n5_pool) | 4 / 5(包含重複4+節断片1) | 7 / 9(CMU未登録1、validate有限助動詞1、節断片1+2、包含重複5+6) | 4 / 5(語数7語1、有限助動詞1+1、包含重複2+4) |
| n5_* drop(最終) | n5_pick1・n5_select1 / n5_select4 | n5_select1・n5_generalize2 / n5_pick1・n5_generalize1 | n5_select1 / n5_select2 |
| 既存Gate drop(参考) | canonicalization_qa2 / 1 | cmu1・validate1・canonicalization_qa2 / validate1 | なし / canonicalization_qa2 |
| 補完(backfill) | 発火(OK) / 発火(OK) | 発火(OK) / 発火(OK) | 不発動 / 発火(OK) |
| N5 L3のCHK5 relation | a2: SAME6+MODIFIER_DROPPED_OK1(+補完SAME1) / b1b: SAME4+MODIFIER_DROPPED_OK1+revert1(relation=NONE) | a2: SAME・MODIFIER_DROPPED_OK混在 / b1b: SAME6(+補完SAME1) | a2: SAME3+FRAME_SHIFT1 / b1b: SAME4+MODIFIER_DROPPED_OK1 |
| 人称整合でN5 glossを書換えた件数 | 0 | 0 | 0 |
| N5のLLM call数(level) | 9(補完込み) / 5 | 9 / 9 | 5 / 5 |
| 費用(各runの実測) | ¥24.48(a2は再選定で2 round、b1b初回は不具合再実行分を含む。§9) | ¥15.65 | ¥10.76 |

※ revert1件(X b1b)は`reverted=True`でform・glossが本文語義に対で戻ることを`ev_collect`で確認(`used_eq_key_eq_n5`/`gloss_eq_n5`とも真)。N5各段の判定記録(`n5.verify/check/reverted/flags/reconcile`)・L1記録(`n_p7_in/n_b1_returned/pool_size/n_judged/n_keep/n_picked/picked_origin`)は各`kp_candidates.json`の`candidates[].item.n5`と`generalization.attempts[]`。路別の集計JSON=`ev02/{x,y,z}/evidence_{a2,b1b}.json`、stage別費用=`ev02/n5_cost_by_level.json`。

Prompt/設定: 全6levelの`generalization.prompt_sha16`・`FLAGS_V1_HASH 3bba7ad2cc6a`・method `N5@T3-2026-10-30`・`params`(max_out/think_budget/effort)がCURRENT_STATE_01 §4の値と一致(各`evidence_*.json`の`prompt_sha16`/`models_requested`)。routing(`KP_N5_VERIFY`/`KP_N5_CHECK`/A2_SUPPORT/B1_SUPPORT)の解決結果は応答model_idで確認。

## 5. retry / fallback / regeneration / resume
- 再選定round(実run): X a2で`reselect --ng 4:…`(NG1件)→同コマンド再実行でround 2を再生成(L1はSEL+pickのみ・`seen_keys`・補完もn5経由)。NG句は復活せず(`take something seriously`不在)、round1文書は`kp_candidates.SUPERSEDED_1.json`へ退避、費用約¥6.0。
- resume API 0(実run): X同コマンド再実行(PENDING再表示)で`raw_usage_log.jsonl`が49→49行(新規API 0)。
- 外側retry/技術失敗/ModelContract/STOP(mock注入test、実APIは故意に失敗させない): `er138_wiring_test_01.py` TestRetryAndFailure(N5 L1失敗=外側retry、技術失敗の上限到達=候補0・N5無し継続なし、routing違反の伝播、stop_checkのN5各段呼出)、`er138_kp_n5_generalization_01_test_01.py`(JSON途切れ1.6倍再試行・技術retry2回・STOP伝播・ModelContractViolation非握り)。
- 補完内のN5: 実runでX a2・Y両level・X/Z b1bに自然発火(§4)。N5 L1(SEL+pick)→`_gate_chain`の順。Gate除外のE計数はn5_pool/select/pickを非計数。
- 任意: `er125.qa_rejudge`をN5形にrecord-onlyで適用(Y b1b・Z a2の8件、¥0.69): 6件PASS、2件(`end up receiving→end up`、`hard on us→hard on`)はrejudge応答のkeyが入力と不一致でNOT_REJUDGED(rejudgeの入力契約は救済後canon形であり、修飾語を落としたN5形は対象外)。β′解釈(QA12は選定単位canon形の品質、提示形の意味はVER5/CHK5で保証)と整合。`ev02/qa12/`。

## 6. 後続工程(API 0)
exporter(`export_form_data_01.py`)がused_form・selection_phrase・難易度を読めることをtest(TestDownstream)で確認(read-only、form本体は変更なし)。`finalize_kp`出力のfield一致、`person_reference_mismatch`のN5形検査、多語N5形でも`kind_of_phrase`=phrase。TTS実音声の再生成は行っていない(語形はone's/someoneの既存実績の範囲。実音声が必要なら別Cap)。

## 7. M11(進行中のrun、報告のみ)
`kp_human_review.json`を持つ全144 run level中、`generalization.method=N5@…`が無いものは144件(REVIEWED 81・PENDING_REVIEW 42・UNREVIEWED_AUTO_ADOPTED 21)。PENDING_REVIEW 42件の一覧=`ev02/m11_inflight_runs_without_n5_marker.txt`(多くは`*_ev_*`証跡run・backup)。再開時の挙動=`ensure_kp_review`が警告ログのみで再生成しない。実運用で待機中の記事があるかはFable確認。

## 8. 残課題・判断候補
- **J2(M10)**: §3。③は未再現(LLM非決定性)、④はN5のpool包含dedupe×P7候補の相互作用。是正案(未実装・仕様候補): 包含dedupeをSEL判定後に行い、F判定のP7 sub-spanが残らないときはB1のsupersetを再投入する。Trialの確定挙動を変えるため実装せず判断を仰ぐ。
- 未観測(実run): 実run上の技術失敗injection(mock testのみ)、人称整合でN5 glossを書換える実例(0件、mock testで確認)、Y/Zでの再選定round実run(Xのみ実run、Y/Zは共通コードでmock test)、retry/fallbackの自然発火。
- 副次所見: 補完でN5が再実行されるため、補完発火時は1levelあたりN5費用がほぼ倍(Y両level=補完込み9 call)。

## 9. 費用・運用上の事実(隠さず記録)
- 合計 ¥73.38/Cap¥80: M10 ¥21.80(**M10枠¥20を¥1.80超過**、並列起動で事前合算guard未適用)、runtime evidence ¥51.58(上限¥60内)=X ¥24.48(初回b1bはjson key=None不具合で保存直前に失敗し再生成した分約¥5.3を含む)・Y ¥15.65・Z ¥10.76・QA12 ¥0.69。
- 不具合(実runで発見・修正): `_n5_l3_summary`のdict keyにNone(CHK5対象外の`relation=None`)が入り、本番のsort_keys署名(`candidates_sha256`)で`TypeError`。mock/M10は署名を通さず未検出。是正=keyを「NONE」へ統一+全wiring testに`json.dumps(sort_keys=True)`検査+単体test追加。以後の全runは修正後。
- 起動規則違反: Y runを課金前STOP(style profile・provenance seed sha)で3回起動し、2回目と3回目の間隔66秒(規則>=150秒に違反)、300秒窓3回でRESTART_STORM保護が`run_n5ev/STOP`を自動作成。いずれも課金前のSTOP(API 0)。このSTOPは解除せず、新規複製dir`run_n5ev2`で実施(起動記録=`ev02/launches.txt`)。以後は記録表で間隔150秒以上を守った。
- 有料runの再起動: X run1が自コード不具合でrc!=0→修正・unit test後に再実行1回。外部停止・監督ループ・自動再試行ラッパなし。
- 測定した量産単価(N5段のみ、1記事セット=Std+Adv): X ¥6.92(a2はround2のみ)・Y ¥8.90(補完込み)・Z ¥5.58。M10 4levelの1level平均は¥3.8〜4.6相当。Trial見積¥6.28/setに対し補完なし経路は同程度、補完発火経路は+約¥2〜3。未承認の節約策は採用していない。stage内訳=`ev02/n5_cost_by_level.json`、chk5(gpt-6.1-sol)が全体の約半分。
