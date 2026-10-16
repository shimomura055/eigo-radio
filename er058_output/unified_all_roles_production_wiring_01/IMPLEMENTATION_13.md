# AUW 委任_13: A3[length NG]是正の実装(2026-10-16、作業worktree `eigo-radio-a3` / branch `work/a3-01`)

ユーザー指示(`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`「# A.」A-2): 「**Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない。**」「7. 数値・否定などの明確な重大内容差、独立音声品質QAは維持する。」
性質: ユーザー承認済み仕様(A-2)への実装修正(Production判定フロー)。到達上限Status=`A3_FIXED_PENDING_FABLE`。`PRODUCTION_WIRED`でも`APPROVED_FOR_PRODUCTION`でもない。

## 1. 何が問題だったか
呼出元10箇所は `verified = verified_content and length_ok` でPrimary転写の文字数(`len(asr_text) <= max_len`)を最終ANDに使っていた。JAは統一judgeのA3(P2事前除外)でSecondary不呼出、またPrimaryが水増し転写でも(=Primary内容PASS+length NG)呼出元ANDで不合格になり、Secondaryが正しい長さで原稿を支持しても救えなかった。「Secondaryの正当なPASSを拒否」にあたる(A-2太字と不整合)。

## 2. 変更内容(設計D1 + Opus条件Aレビュー A3R-01〜09全件採用)
| Opus | 対応 | 実装箇所 |
|---|---|---|
| R1(A3R-01) 呼出元ごとのmax_lenをjudgeへ | EN6/JA4の全箇所が`attempt_ctx`経由で`max_len`を渡す。judge内で`len(text)+15`等を再計算しない | `er078_asr_unified_attempt_ctx_01.py`(`build_attempt_ctx(max_len=)`)、`er078_asr_unified_judge_01.py` `AttemptCtx.max_len`、`er006_secondary_asr_01.py`(ctx生成)、`er007_ja_secondary_asr_01.py`(ctx生成)、呼出元10箇所 |
| R2(A3R-02) Primary内容PASS+length NG→P3降格 | `primary_ng_reason="primary_length_ng"`。Secondary合意時は`PASS_WITH_WARNING`(reason=`secondary_confirmed_primary_length_ng`)。`force_secondary`でも無警告PASSにしない。Primary長さは`gate_text`(adopted_text)基準+`ctx.length_ok`のAND(fail-closed) | `er078_asr_unified_judge_01.py` unified_judge |
| R3(A3R-03) 安全ラッチ+fail-closed helper | `max_len is None`なら従来挙動(JA=A3事前除外/EN=従来)。`final_length_ok(length_ok_primary, detail)`は置換条件(`asr_judgement`存在∧state∈PASSING∧`length.adopted_from=="secondary"`∧`adopted_ok is True`)以外は常にPrimaryのlength_okを返す。静的testで10箇所を固定、legacy/Trialは明示除外list | judge `_a3_reeval_active`/`final_length_ok`、`er078_asr_unified_wiring_13_test_01.py` test_16〜18 |
| R4(A3R-04) (c)案(judgeでTrue上書き)不採用 | 採用せず。呼出元ANDは`final_length_ok`で置換 | - |
| R5(A3R-05) JA診断文・docstring・旧挙動test棚卸し | `er007_ja_secondary_asr_01.py` `length_not_ok`診断文はmax_len未指定(旧挙動)の呼出元だけに出す。docstring更新。旧挙動固定test(`er078_asr_unified_judge_01_test_01.py:112-114,138`・`er078_asr_unified_ja_wiring_test_01.py:238-240`・`er007_ja_scg_test_01.py:452-457`・`er078_asr_unified_wiring_10_test_01.py:59-62`)はmax_len未指定=安全ラッチの固定として**不変で有効**(α期待値の変更0。コメントのみ`wiring_10`で更新)。β(最終判定の安全性)の期待値は不変 | `er007_ja_secondary_asr_01.py`、`er078_asr_unified_wiring_10_test_01.py` |
| R6(A3R-06) 監査 | attempt logに`final_length_ok`追加(Primary `length_ok`は残す)。`asr_judgement.length{applied,primary_len,secondary_len,max_len,adopted_from,adopted_ok,surface_len(参考),primary_ok}` | judge audit、呼出元attempt log |
| R7(A3R-07) Primary超過の大きいSecondary救済に警告 | additive label `PRIMARY_LENGTH_EXCESS`(受理条件不変)。**閾値は置かず**Primary長さ超過でSecondary救済した全件に付与(新しい数値閾値=新gateを作らない判断)。試聴リストは`warning_labels`をそのまま導出(test_13) | judge `W_PRIMARY_LENGTH_EXCESS` |
| R8(A3R-08) OPEN-388訂正 | 「過短/過長」→「過長(上限のみ)」 | `OPEN_ITEMS.md` OPEN-388 |
| R9(A3R-09) rollback | A3ルールは表から削除せず module定数 `A3_SECONDARY_LENGTH_REEVAL = True`(env/flagではない)で無効化可能。Secondary障害露出増は記録のみ | judge |

## 3. 呼出元10箇所の`max_len`(R1)と変更行
| # | ファイル:行 | 言語 | max_len | 備考 |
|---|---|---|---|---|
| 1 | `er003_v1_crosslevel_audio_02_common.py:368-370` | EN | `_run_a2_minimal_fallback_attempt`の引数`max_len`(標準呼出=`len(text)+max_extra_chars`[既定60]、LR後v1=`retts_max_len=len(rewritten_text)+max_extra_chars`)を`dict(attempt_ctx, max_len=max_len)`で渡す | 戻り値dictに`final_length_ok`追加 |
| 2 | `er003_v1_n3_01_tts_generate.py:734-736` | JA | `len(text)+max_extra_chars`(`generate_a2_japanese_with_fallback`既定40、呼出元20/30/40) | |
| 3 | `er003_v1_repro01_main_generate.py:366-368` | EN | `len(text)+max_extra_chars`(既定15、KP minimalは10) | |
| 4 | `er003_v1_repro01_main_generate.py:389-391` | JA | 同上 | |
| 5 | `er003_v1_sing01_news_tail_fix.py:212-214` | EN | `len(text)+max_extra_chars`(既定15) | |
| 6 | `er003_v1_sing01_point_headings_aoede.py:132-134` | EN | `len(text)+15` | |
| 7 | `er003_v1_sing01_voice01_generate.py:255-257` | EN | `len(text)+15` | |
| 8 | `er003_v1_sing01_voice01_generate.py:528-530` | JA | `len(text)+15` | |
| 9 | `er003_v1_sing01_voice01_generate.py:581-583` | JA | `len(text)+15`(fallback) | |
| 10 | `er012_b_family_voices_production_01.py:557-559` | EN | `len(text)+max_extra_chars`(既定15) | |

除外list(legacy/Trial、max_len未指定=旧挙動のまま。Production正式経路ではない): `er003_v1_b1_scaffold_audio_01_generate.py`・`..._03_generate.py`・`er003_v1_iran01_b1_audio_fix.py`・`er003_v1_sing01_audio_generate.py`・`er010_no9_a2_keyphrase_article_reduction_trial_26.py`・`er010_no9_keyphrase_english_lock_fallback_trial_21.py`・`er010_no9_keyphrase_minimal_instruction_minitrial_20_r2.py`・`er012_editorial_b_voices_trial_09_audio.py`・`er038_tts_all_spoken_role_style_trial_01.py`・`er057_tone_trial_final_build_03.py`・`er058_kp_english_lock_trial_01.py`(委任_11 §3-1の一覧と一致。10箇所超過・区別不能な箇所はなくs7非該当)。

## 4. 実装時確認: `detect_duration_anomaly`(ASR前のhallucination長検出)のJA minimal fallback適用
- n3のJA minimal fallback(`_generate_a2_japanese_minimal_instruction`、`er003_v1_n3_01_tts_generate.py:631`)には**効いている**。
- voice01のJA minimal fallback(`generate_charon_japanese_minimal_instruction`、`er003_v1_sing01_voice01_generate.py:409-439`)には**効いていない**(同関数に`detect_duration_anomaly`呼出なし。標準経路の`:510`には存在)。
- 影響: Primary水増し(hallucination)だがSecondaryは正しい転写を返すケースは、voice01 JA fallbackでは音声長の事前検出がなくR7(`PRIMARY_LENGTH_EXCESS`警告)が唯一の事後検出になる。**新gateは追加していない**。重要度が上がるためOPEN候補として記録(OPEN-397)。

## 5. 実音声evidence(Azure STTのみ、TTS 0・OpenAI ASR 0=Primary転写はmock)
`er078_auw_runtime_evidence_13.py`、証跡=`evidence_13/`。詳細=`RUNTIME_EVIDENCE_06.md`§19。ENの正例/負例と、JAの正例(2回目)で期待どおり。

## 6. test
- 新規 `er078_asr_unified_wiring_13_test_01.py`: 59 passed(judge unit 12項目[#1〜#12]、試聴リスト導出、呼出元10箇所のmock leaf救済/継続NG[test_14/15=各10パラメータ]、静的test_16〜22)。`A3_SECONDARY_LENGTH_REEVAL=False`にすると救済系が落ちることも確認(非vacuous)。
- 広域(中核+呼出元に対応する既存test、`netguard`でネットワーク遮断)。baseline(origin/main)と新規失敗の差分: 新規失敗0(失敗は既存44件と同一集合。`er020_*ProductionModuleUnchanged` 2件はcommit前の差分検査でありcommit後に再実行)。
- 静的監査 `er078_asr_unified_wiring_static_audit_01.py`: script差分空(`unlisted_new_calls`/`vanished`/`count_changed`すべて空)。

## 7. リスク・注意
- A3の実績は0件(統一judge記録中のA3作用0)のため、本是正による合格率変化は小さい見込みだが、Secondary呼出が増える(max_len超過のPrimary NG/PASS)=費用微増・Secondary障害露出増(R9、記録のみ)。
- JA Secondaryは送り仮名・表記差(`お話しします`/`お話します`、`9か月`/`9カ月`)をJA許容集合外とする既存挙動(長さ無関係)。実音声JA正例はclip選定で回避(`RUNTIME_EVIDENCE_06.md`§19)。OPEN候補(OPEN-398)。
