# RUNTIME_EVIDENCE_01(KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_02、OPEN-458、2026-10-22)

Status: `WIRED_PENDING_FABLE`(PRODUCTION_WIREDはFable受入後)。配線commit=①`58932e328` / ②`a3bb2b50c` / 撤去`65200313d`(いずれも`git push origin HEAD:main`済み)。
実行前確認: STOPセンチネル rc=0(`runtime_01/stop_check_*.json`、run dirごと)、`TTS_EXECUTION_MODE=STANDARD`、Production .py未commit差分0(配線commit後に実行)、使用モデルは本番の既定どおり(KP選定=gpt-6-luna、TTS=gemini-3.8-flash-lite-tts[Aoede]、ASR=OpenAI/Azure/ローカルWhisper small int8。評価用モデルの新規選定なし)。
集計script=`er108_kp_quality_runtime_aggregate_01.py`(read-only)→`runtime_01/aggregate_01.json`。run出力の要点コピー=`runtime_01/<run>/`。

## 1. 判定表(X/Z別・①②別)
| # | 項目 | X | Z | 根拠 |
|---|---|---|---|---|
| ①-(a) | 保存音声(coffee `pump one's fist` 8本+KP3V保存84件=96行)を配線後の本番adapter(monkeypatchなし)で再判定 | 判定変化2件のみ(N1#1・N2#4 NG_PROTECTED_DISSENT→PASS_VOTE_2OF3 P+W、Whisper `Pump One's Fist`)。84件の偽PASS増加0。N1#4・N2#2/#3・N1#2/#3は両NGのまま(a2型は残存)。N2#1はWhisper `Pump Ones Fest`でNG_VOTE_WHISPER_NG | (同一共通judge) | `guard_lifted_reeval_01.json`、Azure実呼出0・費用0 |
| ①-(a2) | 非KP音声(Family A/B/C・本文等) | 保存4,032ペア×3=12,096行の署名が配線前(HEAD overlay)と配線後でバイト一致(sha256 `2b8235fd…037b05`) | 同 | `er104_nonkp_before_after_01.py`(`KP3V_OVERLAY`=HEAD worktree)。A/B/C同名labelの再利用guardは保護維持(test) |
| ①-(b) | 正式入口の新規生成でKP英語`pump one's fist` | **自然発火**: coffee a2 kp1 `pump one's fist`: P=`Pump one's fist.`(PASS) / S(Azure)=`Pump 1's fist.`(NG、値ガード差`observed_protected_diff.secondary=true`) / **Whisper呼出**=`Pump One's Fist`(PASS) → `PASS_VOTE_2OF3`・行P+W。旧規則では`NG_PROTECTED_DISSENT`(Whisper不呼出)で停止していたケース。kp2=P+S、kp3=Store再利用(`stored_evidence_rejudged`) | Z melos b1b kp1 `sentence him to death`: P=`Sentenced…`(NG)/S PASS/W PASS → `PASS_VOTE_2OF3`行S+W(`PASS_WITH_WARNING`、事後試聴リスト対象)。kp2・kp3=P+S。保護差を伴う票は未観測 | `runtime_01/coffee_prices__run_kpq_01/tts_generation_results.json`、`runtime_01/melos__run_kpq_01/b1b/tts_generation_results.json` |
| P-08(a) ① | 全KP vote記録の`guard_lifted` | 生成時vote記録5件(X 2+Z 3)すべて`guard_lifted:true`、`kp_vote_check`証跡も全件`guard_lifted:true`(再利用entryの証跡含む) | 同 | `aggregate_01.json` summary `all_generated_vote_guard_lifted=true`・`all_checks_guard_lifted=true`(vote記録6件) |
| ② M1 | 選定でのCMU未登録語の除外→再選定 | **自然発火2回**: small_bag a2 run1: attempt1 `minaudières`(単語1語のitem)→item_reasonsに『CMU発音辞書に登録されていない語を含む(未登録語: minaudières)』→attempt2が登録語のみで`KEY_WORDS_STRUCTURE_PASS`。run2: attempt1 `minaudière`→同様にattempt2でPASS。cmu_gate=`attempts_with_cmu_reason:[1]` | melos a2/b1b: 全KP登録語(`someone's`/`one's`等が誤除外されずにM1・M2を通過)、cmu_gate付与 | `runtime_01/small_bag__run_kpq_0{1,2}/keywords_runtime_metadata.json`・`keywords_selector_raw_attempts.json` |
| ② 最終attempt除外/shortfall | | **runtime未観測**(testのみ: `er108_kp_cmu_lexicon_gate_01_test_01`の`test_er105_gate_final_attempt_excludes_cmu_only_and_confirms_shortfall`等) | 同 | mock再生はruntime evidenceではない |
| ② M2 | canonicalization後`used_form`のCMU再確認 | 全run `cmu_post_canon.ok=true`(coffee 3件 checked)。NG発火は**runtime未観測**(testのみ: 即退避・note引継ぎ・exhausted時に本名ファイル無し) | melos a2/b1b `cmu_post_canon.ok=true`(各3件) | `outer_retry_log.json` |
| P-08(a) ② | 全選定metadataの`cmu_gate` | 全5件(coffee a2/small_bag run1・run2/melos a2・b1b)に付与、`lexicon.package_cmudict=1.1.3`・entries 135,166 | 同 | `aggregate_01.json` `all_selection_metadata_have_cmu_gate=true` |
| ② 結果の最終成果物 | | coffee a2: CANONICALIZATION_PASS(KP 3件: `pump one's fist`/`the moment the market moves`/`push prices up`)→KP音声3件OK。small_bag a2: run1・run2とも`OUTER_RETRY_EXHAUSTED`(§4、`kp_stage_failed.json`、keywords_canonicalized.jsonなし=後段は読まない・HR Lockへ送らない) | melos a2/b1b: KP PASS | `runtime_01/*/outer_retry_log.json` |

## 2. 回帰
- `run_project_regression.py`(unittest discovery `er0*_test_*.py`、最終run `reg2`): collected 6,872 / passed 6,834 / failed 14 / errors 18 / skipped 6(313 test files)。HEAD単体では収集不能(untracked資産欠落)のため直近baseline(`kpx2`: 3,344件/failed 7)とは母集団が異なり数値直接比較は不可。**自分起因の新規失敗0**: 1回目(reg1)で出た自分起因6件(`er062 KpOuterRetryTest`×3=fixtureの数字入り語がCMU未登録→CMU語へ更新[設計§6]、`er064 test_no_tracked_py_or_template_modified`=未commit差分、`er078 06c test_c_x_runner_kp_reuse_guard`=KP英語は保護再判定ではなくvote gateが決める新規則に合わせ期待値更新[explanation role+rollback時で保護維持を固定]、`er104 allowlist`)を是正し、reg2で解消。
- 残32件は(a)HEADでも失敗する既存分(`er003_test_bad`・`er008 pricing`・`er012 TtsMode`・`er020 RegressionCorpus`・`er025`・`er040/043`・`er053`・`er064 kp_int/opt`・`er066/068`・`er073`・`er015/069/070/074 import`ほか)、(b)他task起因の未commitファイル(`er109_*`が`er094 StaticChecks`・`er078 ja_wiring allowlist`に影響)、(c)並行実行による共有state競合(`er026 MockFullPipelineTest`は単独実行で42件OK)。
- pytest群(er078*/er103/er104*/er105/er106/er108*)単独run: 3 failed(`er078 ja_wiring`=er109起因/`06c`/`er104 allowlist`=er109起因)→自分起因2件是正+allowlistへ`er109_pattern_probe_01`/`er109_stored_census_01`を研究script扱いで追加→145 passed(wiring+06c)。
- 新規test: `er104_kp_vote_guard_lifted_test_01.py` 26件(真理値表・保護差全組合せ不変・数値/否定の合成誤転写[OF-KPQ-P-10]・Dangling)、`er104_kp_vote_wiring_test_01.py`+P-01(guard_entry明示引数・A/B/C/rollback保護維持・`reuse_blocked`尊重)5件+P-06(P1解除でP2除外が評価)+AMBIGUOUS/非KP保護不変、`er108_kp_cmu_lexicon_gate_01_test_01.py` 37件(M1実gate・cmu_gateメタデータ・M2即退避/次周note/exhausted・importer許可リスト=er105とscaffoldのみ・A/B/Cが通らない)。
- Dangling Grep: 撤去識別子`NG_PROTECTED_DISSENT`/`protected_dissent_blocks`/`kp3v.NG_PROTECTED`/`er108_kp_vote_noguard_01`/`.protected_diff`はProduction .pyに0件。残置=記録系`er106_joint_runtime_evidence_01.py:921`(過去runの状態集計)・`er107_fx_kp_audio_ng3_listen_page_01.py:123`(過去runの説明文、撤去注記追記済み)、およびそれらを禁止するtest自身。

## 3. 費用(出典付き)
X coffee_prices a2 KP段+KP音声: 0.79円(runnerの累計費用表示: scaffold 0.48+tts 0.31[openai_asr 0.04/azure 0.17/gemini 0.10])/ X small_bag a2 run1 KP段 1.45円・run2 1.28円(同)/ Z melos kp 1.0809円+tts_b1b(KP3clipのみ) 0.37円=1.4483円(runner出力`spent_jpy`)。**合計約4.97円**(案件上限60円内、日次上限1,500円内。API: openai/azure/geminiのみ、perplexity等の外部検索なし)。①-(a)・非KP再実行・回帰は費用0(ローカルWhisperのみ)。

## 4. 開示・未解決
1. **small_bag a2のOUTER_RETRY_EXHAUSTED**: CMU除外後の再選定で`having a big moment`が3周同一に選ばれ、canonicalizationの既存validator(有限助動詞)で毎回INVALID。CMU条件が原因ではなく、OPEN-456 F1(外側retryが同一句を繰り返し選ぶ)と同型の既存問題。fail-closed(旧KPを残さない・HR Lockへ送らない)で目的要件(不適合KPを存在させない)には適合するが、**このarticleのa2は現状KP段が通らない可能性**がある。次の一手候補=F1の対策(canonicalization INVALIDの句を次周noteで明示除外)をFable判断で実装(`判断候補`: 仕様候補、区分B=OPEN-456 F1で起票済み・実装前Fable判断)。
2. a2型(OpenAI `'s`脱落+Azure `1's`の両NG)は残存。UDR #155(C1不採用、包括対策OPEN)。
3. M1最終attempt除外/shortfall・M2 NGのruntime自然発火は未観測(testのみ)。Z側で保護差を伴う票は未観測(Z KP vote記録でguard_lifted記録のみ確認)。
4. `rebuild_state(rejudge_f1)`(narration系の明示CLI、KP英語は対象にならない)は対象外としdocstringに運用注記。bulk rejudge script(`--apply-marks`)にKP英語entryへ使わない運用注記を追加(OF-KPQ-P-09)。
5. 試聴: S+W行(Z kp1 `sentence him to death`)は事後試聴リスト対象(`pass_with_warning_listening_list.json`、行に`observed_protected_diff`)。ユーザー試聴ページは本委任では作成していない(新規記事の完成物ではないため)。

## 5. 失敗終了時の最終成果物(small_bag a2 run1/run2)
`er019_output/family_x_audio_production_wiring_01/small_bag__run_kpq_0{1,2}/a2/key_phrases/`: `kp_stage_failed.json`(KP_STAGE_FAILED(OUTER_RETRY_EXHAUSTED))、`outer_retry_log.json`、`outer_retry/attempt_{1,2,3}`、`keywords_runtime_metadata.json`(cmu_gate付き)。`keywords_canonicalized.json`は存在しない(後段TTS/assemblyは読めない)。ユーザー原文の要求(CMU未登録KPを存在させない/不要NGを増やさない)に対し、KPなしでSTOP=安全側。
