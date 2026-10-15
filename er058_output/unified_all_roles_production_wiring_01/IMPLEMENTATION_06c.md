# AUW 委任_06c IMPLEMENTATION (Opus条件C所見 OF-AUW-C-01〜C-14 のFable採用分の実装) -- branch feat/auw-unified-asr-01
JPY 0(有料API 0。test実行は通信遮断plugin `netguard` 付き `.venv`、一括再判定・費用試算は保存データのみ)。main無変更。既存Prompt/モデル/Voice/速度(A2 6%減速)/閾値/HR Lock(`er011_human_review_lock_01.py`)ロジック 無変更。U1=True・U2=A2_ONLY 定数 無変更(`er078_asr_unified_judge_01.py:65-66`、`git diff`に当該行なし)。
T-0: 委任文保存 `docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_06c.md`、checker=`_check.json`(FAIL、非ブロッキング)。stop_scope_check rc=0(開始 `stop_check_06c.json`・終了 `stop_check_06c_end.json`)。
証跡: `evidence_06c/`(`reuse_bulk_rejudge.json`・`reuse_blocklist.json`・`hr_queue_cleanup_06c.json`・`cost_increment_06c.json`・`static_audit_diff_06c.json`)、`patch_06c/`(test per-file JSON)。

## 0. 当初目的(ユーザー原文。`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`)
- L54「Primary NGなら、不一致の種類によらず原則Secondaryを実行する。」 L55「Primary NG・Secondary PASSなら、PASS_WITH_WARNINGとして採用する。」 L56「PASS_WITH_WARNINGはユーザーの事前承認を求めず、自動採用する。」 L57「WARNING音声はユーザーが事後試聴できるリストへ自動登録する。」 L58「Primary・Secondary両方NGなら次のTTS再生成へ進む。」 L59「Secondaryが障害・利用不能の場合、PASS扱いせず、既存の安全な障害処理へ進む。」 L60「同じ音声に対するSecondaryの重複API呼び出しを防ぐ。」
- L97「この安全条件と「Secondary PASSなら採用」の原則が競合する場合は、数値・否定などの明確な重大内容差を誤採用しないことを優先する。保護すべき差異を警告だけで無条件に解放する仕様にはしない。」
- L204「4. Primary／Secondary両NGなら最大3回のTTS生成フローが成立。」

## 1. (a)〜(k) 対応表
| 項目 | 変更ファイル:行 | test | 根拠・結果 |
|---|---|---|---|
| (a) BLOCKER 非ラテン救済の退行(OF-AUW-C-01) | `er078_asr_unified_judge_01.py` `PrimaryResult.adopted_text`(新field)、`unified_judge`の`gate_text`(Primary PASS時は採用転写で最終ANDゲート)、audit `primary.adopted_text`/`value_guard.gate_target`。`er006_secondary_asr_01.py` 非ラテン層で`adopted_text=text_nl`を採用時のみ設定し`PrimaryResult(adopted_text=…)`へ。`er019_family_x_validation_inheritance_01.py` `rejudge_with_current_judge`(元が`adapter.layers=non_latin`なら保存Azure転写を採用根拠に)。 | `er078_asr_unified_wiring_06c_test_01.py::test_a_*`(6本、parametrize含む8) | 否定("can't wait"/"not at all"/"cannot")・数値("3 days")を含むKPの非ラテン救済→PASS_WITH_WARNING(Azure1回)。`adopted_text`なしだとNG_PROTECTED(旧挙動=退行の直接再現)。採用転写の否定差・値DIFFは引き続きNG_PROTECTED(`final_gate_negation_diff`/`final_gate_value_diff`)。**一致**。 |
| (b) Secondary障害の網羅(OF-AUW-C-02) | `er006_secondary_asr_01.py` `_AzureShared._call`を try/except(→`SecondaryOutcome(None, error)`)=CS/Tier3/非ラテンの3層+監査recordを一括。`get_full_text_via_azure_stt_with_phrase_list`のcanceledを`on_canceled`化(CancellationReason.Error=text None+err、EndOfStreamは正常、JA `_azure_stt_strict`と同形)。`er078_asr_unified_judge_01.py` `is_config_stop_error`(新)+`unified_judge`のexceptで再送出。`er007_ja_secondary_asr_01.py` 旧SCG経路の`except Exception`も再送出。 | `test_b_*`(14ケース: err/例外/timeout/空転写/canceled部分転写/費用設定不備2種 ×層) | `init_logger`未呼出・`[STOP]`単価未登録のRuntimeErrorは再送出(`er003_v1_n3_01_tts_generate.py:152-154`相当の既存方針と整合)。通常のRuntimeErrorは障害扱い。部分転写はPASS根拠にしない。**一致** |
| (c) 再利用経路の値ガード(OF-AUW-C-03) | 新 `er078_reuse_value_guard_01.py`(`guard_entry`: 保存転写のみ・API 0・Secondary新規0、DIFF/否定差=blocked、転写なし=従来どおり再利用、`reuse_blocked` markは常にblocked)。配線: `er019…_runner_01.py` `_generate_or_reuse`/`_generate_or_reuse_kp`、`er019…validation_inheritance_01.py` `try_inherit_from_cached`、`er006_master_audio_store_01.py` `get_or_generate`(blocked時は旧音声を`audio/_reuse_blocked/`へ退避して再生成)、`er063_family_z_audio_01.py` `generate_or_reuse_z`、`er013_family_c_production_runner_01.py` `resumable_reuse(…, canonical_text)`+3呼出点。`rejudge_with_current_judge(force_lang=)`をadditive。 | `test_c_*`(9ケース) | 再利用点5系統すべてでDIFF→再生成、OK→再利用。一括再判定(`er078_auw_reuse_bulk_rejudge_06c.py`、`evidence_06c/reuse_bulk_rejudge.json`): **entries 2,775(results cache)中 DIFF 16件、Master Store 225件(復元可能分)中 DIFF 0件**。→ §3。**一致(DIFF一覧はFable判断待ち)** |
| (d) Secondary障害は技術STOP、HR Lockにしない(OF-AUW-C-06) | `er006_secondary_asr_01.py`/`er007_ja_secondary_asr_01.py`: NG_SECONDARY_UNAVAILABLEのみのとき`human_review_required=False`+`technical_stop`(truthy dict、既存互換)+`technical_stop_status="TECHNICAL_STOP_SECONDARY_UNAVAILABLE"`(既存規約なし→新設)。`er078_secondary_run_scope_01.py` `circuit_open`/`technical_stop_entry`/`guard_generate`/stage終了時`[TECHNICAL_STOP]`報告。runner choke: X `_generate_or_reuse(_kp)`、Z `generate_or_reuse_z`、C `tts_call_for_voice`。`_OVERWRITABLE_STATUSES`に追加(再実行で再生成)。 | `test_d_*`(5ケース) | 承認不要・再実行で再開可・HR queue/Lock非投入(adapter/wrapper/runner層)。**一部不一致=§4-1(leaf内のHR Lock record_outcomeは未変更。Lockロジック変更が必要なためSTOP級として報告)** |
| (e) 試聴リスト導出失敗の表示(OF-AUW-C-12) | `er078_pass_with_warning_registry_01.py` `ListeningListDerivationFailed`(新)、`load_listening_list`(失敗時は`[]`でなくそれを返す)、`render_html_section`(「導出失敗(要確認)」)、`write_listening_list_safe`(単独HTMLにも表示) | `test_e_*` | 失敗は「0件」と表示されない。結果ファイル無しは従来どおり0件。**一致** |
| (f) test決定化(OF-AUW-C-14) | `er011_b1_connected_speech_validator_01_f1_test_01.py` 212・231行 `if r["verified"]:`→`assert r["verified"] is True`+`state==PASS_WITH_WARNING` | 同file 39 passed | CS/er021側に同形の条件付きassertは無し(`grep 'if .*verified'`で当該2箇所のみ)。**一致** |
| (g) 残置物(OF-AUW-C-13) | `er003_v1_n3_01_tts_generate.py` `_post_slowdown_cascade_rescue`(約59行)撤去。test付替え: `er006_secondary_asr_01_m1_wiring_test_01.py`・`er065_…regression_test_01.py`・`er078_asr_unified_en_wiring_test_01.py`→`_post_slowdown_unified_judge`(J7)。静的監査 `er078_asr_unified_wiring_static_audit_01.py`のJ7とallowlist(-1 entry, rejudgeのclassify_asr_match 1→2)。 | `test_g_*`(3ケース。flag OFF経路: `cascade_enabled=False`で旧挙動[統一judge/Secondary不通過・同一signatureでstop_retrying=True到達可能]、`if stop_retrying:`8箇所残置assert) | 付替え不能なtestなし。`er065`は旧「TCMはcascade対象外=0回」→統一仕様「1回」へ期待が変わる(§4-3)。**一致(1件β類似あり)** |
| (h) Dialogue(Std)/Voices A2 外側ループ(OF-AUW-C-08) | `er003_v1_n3_01_tts_generate.py` `generate_with_a2_slowdown_outer_loop`(新、通算TTS3回・`is_last_slot`=通算3回目のみ・`append_attempt_history_event`)。適用: `er063_family_z_audio_01.py` dialogue a2、`er012_b_family_voices_a2_production_01.py` `generate_voice_body_wide_margin_with_a2_slowdown`・`generate_narration_wide_margin_with_a2_slowdown`。 | `test_h_*`(4ケース) | Prompt(`A2_ENGLISH_STYLE_PREFIX_SLOWER`)・Voice・6%減速・Dialogue固有例外は不変、KP英語phrase 4回構成は不変(対象外)。L204「最大3回」。**一致** |
| (i) 費用試算(OF-AUW-C-10) | `er078_auw_cost_increment_06c.py`(新)→`evidence_06c/cost_increment_06c.json`、`RUNTIME_EVIDENCE_06.md` §12-9(追補)。 | — | 中央値 0.55〜0.82円/セット、95%上限 1.17〜1.74、悲観 1.82〜2.72(目標70円の約1〜4%)。**一致** |
| (j) D-B1/D-B2後始末 | `er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`(344→343行、HEADと完全一致に復帰)、`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`(12→11行)。`evidence_06b`識別子を含む行**のみ**(各1行)除去、他行・Lockのstate/sentinel 無接触。sha256前後は`evidence_06c/hr_queue_cleanup_06c.json`。 | — | er007に残る未commit差分3行は`dummy.wav`等の既存test由来(06b以前の既存test汚染。本委任の対象外、触っていない)。**一致** |
| (k) 本書+commit/push | — | — | §5。 |

## 2. test数値(通信遮断plugin付き、per-file)
- 新規 `er078_asr_unified_wiring_06c_test_01.py`: **44 passed**。
- 既存影響(per-file、baseline=05時点`patch_05/*`のfail id集合。06/06bは本番コード無変更のため同一):
  | 系統 | files | passed | failed | 新規失敗 |
  |---|---|---|---|---|
  | main(er006/007/011/019/020/021/026/064/078 + 新規) | 100 | 1,840 | 29(baseline既存29 id) | **0** |
  | extra(er003/008/009/012/013/058/063/065/068) | 113 | 2,578 | 9(baseline既存9 id) | **0** |
  | rest(er002/005/010/015…/077) | 102 | 2,868 | 29(失敗id 23=baseline同一、import error 3 file含む) | **0** |
  `patch_06c/test_post_06c_{main,extra,rest}_final.json`。初回実行で新規失敗5件が出たが原因は下記§4-2(設定不備の再送出に伴うtest側mock不足)で、4 fileを是正後に再実行し0件。
- AUW中核(per-file): er078_asr_unified_en_wiring 53・ja_wiring 51・judge 45・wiring_05 50・wiring_06c 44・static_audit 15・value_guard 58・registry 9、er006_secondary 29+m1_wiring 22、er019 inheritance 34、er063 47+12、er013 production 39 等。中核30 file合計 801 passed / 2 failed(`er007_ja_secondary_asr_01_test` の `api.openai.com` 遮断、baseline既存)。
- 静的監査: `er078_asr_unified_wiring_static_audit_01.py` 15 passed。CLI差分(`evidence_06c/static_audit_diff_06c.json`)= `unlisted_new_calls:[] / vanished:[] / count_changed:[]`(allowlist一致)。allowlistは手編集(34 entry、rescue entry削除・rejudgeのclassify_asr_match count 2)。
- 通信遮断: 本委任で触ったtest・新規testからの外部通信 0(新規file・bulk script・費用script全て遮断下、`netguard_attempts.log`に新規試行なし)。

## 3. 再利用一括再判定の結果(DIFF 16件、採用判断=Fable)
`evidence_06c/reuse_bulk_rejudge.json`(2,775 entry、判定可能2,775、REJUDGE_OK 2,669、保護差以外のNG 90、DIFF 16、Master 392中転写あり320・文面復元225・DIFF 0)。一覧は`evidence_06c/reuse_blocklist.json`。いずれも2026-08〜09の過去pilot/trial出力(`er003_output/n3_01/hanshin`・`er005_output/cost_baseline_01`・`er006_output/pool_pilot_01`・`er026`以外)で、現行runnerが再利用対象にするのは同一out_dirの前回resultsのみ。
- 実質的な誤認と見える例: hanshin topic_intro「8–1」→ASR「81」、parenting point_one「3 10-minute」→「310 minute」、pool_benches「2020」→「2021」、pool_n5_cafes「April twenty eighth」→「April 28th」(canonical側の表記ゆれ由来の可能性あり)。
- 判定器の偽陽性の可能性: JAコメント「いちばん」→「一番」(`hyp_drop(b)`)、`*Frontiers in Psychology*`のmarkdown記号を含む原稿(canonicalに装飾あり)等。
- **マーク**: Master Store manifestのDIFFは0件のため`reuse_blocked` mark付与なし。results cache側16件は履歴出力のため編集せず(provenance保持)、再利用時に`guard_entry`が同一判定を動的に適用して再生成へ回す(=実質的な再利用禁止)。削除なし。

## 4. 逸脱・要判断
1. **(d) leaf内HR Lockの残存(STOP級)**: adapter/wrapper/runner層はLock非投入だが、leaf(`generate_charon_english`等)は`@review_lock.guarded_generate`で包まれ、`record_outcome`(`er011_human_review_lock_01.py:357-410`)は「最終status!=OK」なら理由を問わず`HUMAN_REVIEW_REQUIRED`にする。Secondary障害のみで最終STOPPEDになったclipが、Lockに入ることは**本委任の範囲では防げない**(防ぐにはLockロジックへの追加=`record_outcome`冒頭でtechnical-stopのみの結果をskipする早期return、約3行が必要。委任文「HR Lockロジック変更が避けられない場合はSTOP報告」に該当)。影響の見積り: circuit breaker(連続3障害)が開くまでの最大1〜2 clipが対象で、以降のclipは`guard_generate`で停止するためLockに入らない。推奨: 追加を承認する(技術STOPの結果にだけ作用する非破壊のskip)。未実施。
2. **設定不備の再送出に伴う既存testのmock不足**: `er021…production_wiring_01_test_01`(2)・`er003_news_tail_fix_semantic_equivalence_surfacing_02_test_01`(1)は、Primary NGでSecondaryへ到達するが**Azure SDKを実際に呼んでいた**(netguardなしなら実通信)。旧は`cl.record`のinit_logger RuntimeErrorが「障害」として握りつぶされて通っていた。委任(b)のとおり再送出に変えたためfail→当該testに`get_full_text_via_azure_stt_with_phrase_list`のmockを追加(α類。API 0を担保。主題のPrimary判定は不変)。**波及リスク**: 本番でcost loggerを`install`しないrunner(06 D1が指摘したlegacy A `er003_v1_n3_01_tts_generate.py main()`)では、旧=毎回Azureを呼んで課金されつつ結果が黙って「障害」扱い→新=最初のSecondaryで`RuntimeError`により停止。OPEN化を推奨(Legacy Aの`cl.install`追加は別判断)。
3. **β類似1件**: `er065_…regression_test_01::test_post_slowdown_wiring`(死コードtestの付替え)。旧は「TRUE_CONTENT_MISMATCHなら減速後cascadeは0回」を固定していたが、05で承認済みの統一仕様(原文L54)では1回。付替えに合わせて期待を「adapterへ1回」へ更新した。`er078_asr_unified_wiring_05_test_01`の2件(Dialogue)も(h)の外側ループ化に追随(kwに`max_attempts:3`、減速後判定は`generate_with_a2_slowdown_outer_loop`経由)。
4. **`technical_stop`の型**: 委任文は`technical_stop=True`。既存互換(`result["technical_stop"]`はtruthyなdict、既存test 3箇所が`d.get("technical_stop")`)を保つため値はdictのまま、別途`technical_stop_status`(文字列)を追加した。
5. **Legacy B/A runnerのcircuit-open停止は未配線**: `cl.segment_context`に統一的なclip境界はあるが、停止用の例外/entry返却をそこへ入れるとB/Aの結果JSON未書込の恐れがあり、Active(X/Z)とC(`.ok`再開可能)だけに配線した。B/Aは従来どおり(circuitはSecondary呼出を止めるのみ)。
6. **bulk再判定の限界**: Master Store manifestはcanonical textをhashでしか持たず、225/320件はresults側のtext→hash突合で復元(95件は文面を復元できず未判定)。`get_or_generate`の実行時は`key.canonical_text`が使えるため全件対象。`.ok.meta.json`(32件)はcanonicalを持たず単独では判定不能(resumable_reuse実行時のみ判定)。
7. **新仕様候補**: なし(承認済み設計の範囲)。ただし§4-1(Lockへの技術STOP skip)は仕様判断を伴う。

## 5. 委任_06d(残Section実音声①〜④+C-11 runtime)・07への申し送り
- 06d: ①X a2 KP ②Family B B1全体・Hook/Tension/Closing・見出し ③C Comment(JA)・JA title ④Dialogue(Std)・KP phrase 4回構成の通算上限(06b §12-11-3)。**Dialogue(Std)④は外側ループ化(h)により、減速後NG→取り直し→通算3回のruntime evidenceが取れるようになった**。C-11 runtimeでは非ラテンKP救済(a)の実音声(否定・数値入り英語phrase)も確認推奨。
- 07: 旧`_post_slowdown_cascade_rescue`の記述更新(`CURRENT_SPEC.md`2・`DECISION_LOG.md`2・`OPEN_ITEMS.md`3箇所に参照が残る。SSOT編集は本委任の範囲外)、`er026_output/.../asr_root_cause_01/reeval_*.py`2本(証跡script)は撤去済み関数を参照したまま、§4-1/4-2のOPEN化。
- 費用: JPY 0。

## 6. 受入記録
(1) 当初目的=§0 (2) 成果物=本書・新規`er078_reuse_value_guard_01.py`/`er078_auw_reuse_bulk_rejudge_06c.py`/`er078_auw_cost_increment_06c.py`/`er078_asr_unified_wiring_06c_test_01.py`・変更ファイル(commit) (3) 証拠=`evidence_06c/`・`patch_06c/` (4) (a)(b)(c)(e)(f)(g)(h)(i)(j)=一致、(d)=adapter/wrapper/runner層は一致・leaf内Lockは不一致(§4-1)、(k)=commit後に§7へ追記 (5) 判定=条件付きPASS(§4-1のLock追加がFable承認待ち)。
