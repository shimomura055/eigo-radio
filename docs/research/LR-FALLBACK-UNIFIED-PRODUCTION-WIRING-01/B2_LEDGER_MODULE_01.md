# B2_LEDGER_MODULE_01: er129 LR/Fallback台帳導出module(未配線の純module)+保存LR entry適用結果(委任_07 / Phase B B0+B2、API 0)

管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01。委任文=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_委任_07.md`。ユーザー原文=`…_USER.md`(UD-1/UD-3、最終Human報告の表示仕様)。設計=`INTEGRATION_01.md`(F-1/F-3/F-6/F-11)・`OPUS_REVIEW_01.md`(M-1〜M-6)・`W2_UD1_BODY_REFLECTION_DESIGN_01.md` §4-§6・`W4_FINAL_HUMAN_REPORT_DESIGN_01.md` §3・`W1_ROUTE_WIRING_AND_RECORDS_01.md` §2。

## 0. 結論(先に)
1. `er129_lr_display_reflection_01.py`を新設(**未配線**=どのProductionコードからもimportされない。test `test_u8_no_production_module_imports_er129`で固定)。既存Productionコード・run dir・SSOTは無編集(run dirの前後sha一致=`test_u7_run_dir_is_not_modified_by_ledger_derivation`)。API 0・LLMなし。
2. test 39件PASS(`er129_lr_display_reflection_01_test_01.py`、実測約5秒)。W2 U1-U8+Opus M-1〜M-6再現ケース(正規化差・insert/delete・句読点・resume形・HR原文復帰・Store再利用・旧記録・UNKNOWN・RECORD_MISMATCH・T2 1文・T3表示側)を含む。
3. **保存LR entry 43件の適用**: tts_generation_results.json上で処理可能な**35 entry全件が偽STOP 0**(PASS 31+PASS_SUPERSEDED_BY_HUMAN 4)。残り8件はentry内にLR採用記録の無い複写/単体ファイルで台帳導出の対象外(§3)。
4. **AI島**: LR記録から`AI agents`(Std)/`AI systems`(Adv)を特別扱いコードなしで自動導出し、表示overlayに反映できることを確認(R-7、§4)。
5. 想定外の発見2件(§5): (a)Y E-1 a2の人間承認takeはattempt直接記録上「role Style」(W4 §3-3の「Fallback」と食い違い、entry直下の旧値が陳腐化)。(b)Z猿の手Std `full_story_part1_c10`はLRブロックattemptが未記録で採用takeがUNKNOWN(記録欠落。委任_06のfinal_adoptionで将来のrunは解消)。
6. `classify`は作っていない(B4)。ledgerのキー(`verdict`/`fallback.state`/`warnings`/`adopted_take.status`)をB4が受け取る。

## 1. module API(契約B0に対応)
| 契約 | 関数 | 要点 |
|---|---|---|
| 1 | `resolve_adopted_take(entry, block_progress, hr_records, store_info)` → `AdoptedTake` / `UNKNOWN` | 優先順位=①人間承認(`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`・`adopted_attempt_audio_path`・`ypl7_user_approval_record_*`) ②再利用(`reused`/`final_adoption.source=store_reuse`、固定殻=`existing_master`) ③`final_adoption`とBlockProgress `verified`(depth,ordinal)の突合(食い違い=`RECORD_MISMATCH`、BlockProgress無し/block欠落=突合不能としてnote) ④旧記録導出(attempt wavのsha一致→`dialogue_tts.final_mode`→`english_lock_attempts_log`→attempts_log→`fallback_used`(LR採用なしのみ)) ⑤UNKNOWN。status≠OKの終端NG(STOPPED等)は`status=NOT_ADOPTED`(記録欠落ではない)。**「記録完全」=`status==OK`のAdoptedTakeが返ること**に一本化 |
| 2 | `build_lr_ledger(run_dir, level, results_path=, level_dir=)` / `write_ledger_audit(ledger, path)` | メモリ導出(clip毎: role/segment・chunk/adopted take/lr{before,after,ops,changed_spans,reason,source}/fallback{state,used,adopted_style,from_style,slot}/text_parity/overlap{T1,T2,T3}/warnings/verdict)。ASR正解は`er020.resolve_expected_text_after_local_rewrite`を唯一の参照点(HR原文復帰も反映)。監査出力は内部キーを落として全置換、Gate/表示入力にしない |
| 3 | `compute_ops` / `locate_op` / `apply_overlay` | 変更opをreplaceへ正規化(insert/deleteは隣接一致語を取り込む、隣接opは併合)。表示文(正規化前)中の一意位置を前後k語(k=2→4)のanchorで特定(両側→片側へ縮退、反映済み=AFTER状態も検出)。数詞(one〜twenty・tens)は数字へ寄せて比較。句読点は語単位一致で無視。表示側の綴り・曲引用符は取り込み語について保持 |
| 4 | `check_text_parity(display_after, tts_input, asr_expected, strict_phrases)` | 文単位。V3(TTS入力≈ASR正解)・V2/V1(表示⊇各)。LR変更文以外の正規化差はPASS_NORMALIZED、LR変更文は変更語句を含み類似度>=0.8を要求(偽STOPと見逃しの両方を避ける)。ZのTTS入力=`audio_text_after`(entry["text"]は表示形) |
| 5 | `check_confirmed_overlap(ledger_clip, confirmed_selection, grammar, facts)` | T1=`er128.lr_overlap`の純関数再計算(`confirmed_kp_lr_overlap.json`は読まない) / T2=変更箇所を含む**1文**と確定項目・文法の出典文 / T3=表示側実文字の数字と固有名詞(人名は全文に残ればPASS+`entity_pronoun_substitution`、消えればSTOP、fact表が無ければSKIPPED=偽STOPにしない) |
| 6 | (分類核は未作成) | B4が受領 |

clip verdict: `NO_LR`/`PASS`/`PASS_SUPERSEDED_BY_HUMAN`/`STOP_UNLOCATABLE`/`STOP_AMBIGUOUS`/`STOP_PARITY`/`STOP_T1|T2|T3`/`RECORD_MISMATCH`。採用take不明は`warnings=RECORD_INCOMPLETE:adopted_take`・`fallback.state=UNKNOWN`として**LR位置特定・三者一致の結果とは別に**出す(Fallback表示・B4のfail-closed判断はこの項目を見る)。

## 2. 手順と規則修正の記録(偽STOPの原因と修正)
初回実行(規則初版)では35件中20件が`STOP_PARITY`になった。原因を特定し規則を修正して0件にした(Opus (b)-6の範囲内の規則修正。TTSのStyle・Gate・閾値・ASR判定は無変更):
| # | 初回の偽STOP | 原因(観測) | 修正 |
|---|---|---|---|
| a | Z 16件(Melos→He・guest→visitor・topic→subject等) | ZのTTS入力に`entry["text"]`(表示形canonical)を使っていた。Zの実TTS入力は`audio_text_deviation.audio_text_after`(OPUS M-1 ZのV2照合元) | Z形はTTS入力=`audio_text_after` |
| b | X 3件(hormuz comment_4・meta in_one_line・er056/057 comment_2) | `entry.text`(`retts_result.text`=送信前正規化後)と選定文(`selection.selected.rewritten_segment`)の語列が一致しない(例: `some Muse calls`→`some calls for Muse`、`then changed`→`and changed`。TTS側の語順/接続語正規化) | V3を語列完全一致から「LR変更文以外の正規化差は許容」へ(LR変更文は変更語句を含み類似度>=0.8) |
| c | X 1件(hormuz run_04 `Act One`→`The first act`) | 表示は`Act Two`/`three`、TTS入力は`Act 2`/`3`(数詞の語化と数字化が逆向き)で短文の類似度<0.6 | 数詞(one〜twenty・tens)を数字へ寄せて比較+文列の位置対応を追加 |
| d | (副次)上記cの直後に`Act One`がT3数字STOP | 数詞語をtokensで数字化したため、語のままの変更がT3の「数字」に当たった | T3の数字判定は表示側の実文字0-9に限定。数詞語の変更は`number_word_in_change`警告に留める |
| e | Y E-1のHR採用take | attempt json参照のパス比較不一致(`\`と`/`) | `normpath`比較へ。HR採用takeはadopted wavの隣のjsonを直接読む(stdchunkコピーは別run dirのattemptを指すため) |

規則修正後の最終: **偽STOP 0**(`STOP_UNLOCATABLE`/`STOP_AMBIGUOUS`/`STOP_PARITY`=0、`RECORD_INCOMPLETE`はZ猿の手Std 3 entryのみで、いずれもLR位置特定・三者一致はPASS。§5(b)の記録欠落そのもの)。

## 3. 保存LR entry適用結果(35 entry)
凡例: 位置=`変更前→変更後[r=replace/i=insert、k=anchor語数] (表示unit出典)`。parity=三者一致。T1/T2/T3=確定内容重なり(SKIP=確定項目なし・fact表なしで判定対象外)。fb=最終採用takeのFallback(NOT_USED/USED:種別/UNKNOWN)。

| # | run/level | clip | 判定 | 位置 | parity | T1/T2/T3 | fb | 警告 |
|---|---|---|---|---|---|---|---|---|
| 1 | X:ai_island_temple__run_form_prod_01/a2 | full_story_part1_k2 | PASS | AIs→AI agents[r,k2] (parts.json:part1) | PASS | PASS/PASS/PASS | NOT_USED | - |
| 2 | X:ai_island_temple__run_form_prod_01/b1b | full_story_part1_k2 | PASS | AIs→AI systems[r,k2] (parts.json:part1) | PASS | PASS/PASS/PASS | NOT_USED | - |
| 3 | X:coffee_prices__run_tru_ev_x_adv_16/b1b | in_one_line | PASS | affect→influence[r,k2] (parts.json:in_one_line) | PASS | SKIP/SKIP/PASS | USED:FALLBACK_MINIMAL_EN | LR_REASON_UNAVAILABLE |
| 4 | X:coffee_prices__run_tru_ev_x_adv_2/b1b | comment_1 | PASS | compares with→stacks up against[r,k2] (b1_support_texts.json:comment_1) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 5 | X:coffee_prices__run_tru_ev_x_std_2/a2 | topic_intro | PASS | topic→subject[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 6 | X:b3/hormuz__run_02/b1b | comment_4 | PASS | then→and[r,k2] (b1_support_texts.json:comment_4) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 7 | X:b3/hormuz__run_03_baseline/b1b | comment_4 | PASS | a proposed→an initial proposal for a[r,k2] (b1_support_texts.json:comment_4) | PASS_NORMALIZED | SKIP/SKIP/PASS | NOT_USED | - |
| 8 | X:b3/hormuz__run_03_baseline/b1b | full_story_part2 | PASS | US→United States[r,k2] (parts.json:part2) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 9 | X:b3/hormuz__run_04_parallel_a/b1b | full_story_part1 | PASS | Act One→The first act[r,k2] (parts.json:part1) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 10 | X:b3/small_bag__run_02/b1b | preview | PASS | Mini→Small[r,k2] (b1_support_texts.json:preview) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 11 | X:meta__run_regen_01/b1b | in_one_line | PASS | handle→manage[r,k2] (parts.json:in_one_line) | PASS_NORMALIZED | SKIP/SKIP/PASS | NOT_USED | - |
| 12 | X:word_gacha__run_wg_01/b1b | full_story_part3 | PASS | you've→you have[r,k2] (parts.json:part3) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 13 | Z:melos/run_e2e_01/b1b | full_story_part2_c1 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 14 | Z:melos/run_e2e_01/b1b | full_story_part2_c2 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 15 | Z:melos/run_e2e_02/b1b | full_story_part3_c1 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 16 | Z:melos/run_e2e_04/b1b | full_story_part3_c1 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 17 | Z:melos/run_kga3_off_z_01/b1b | full_story_part3_c1 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 18 | Z:melos/run_kgcpw_z_01/b1b | full_story_part3_c1 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 19 | Z:melos/run_kgcpw_z_e5_a2_01/b1b | full_story_part3_c1 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 20 | Z:melos/run_kgcpw_z_e5_b1b_01/b1b | full_story_part3_c1 | PASS | Melos→He[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 21 | Z:the_monkeys_paw/run_sf_prod_01/a2 | full_story_part1_c10 | PASS | guest→visitor[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | UNKNOWN | RECORD_INCOMPLETE,LR_REASON_UNAVAILABLE |
| 22 | Z:the_monkeys_paw/run_tru_ev_z_adv_4/b1b | topic_intro_en | PASS | topic→subject[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 23 | Z:the_monkeys_paw/run_tru_ev_z_std_6/a2 | topic_intro_en | PASS | topic→subject[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 24 | Z:the_open_window/run_sf_prod_01_preserve_20261023/b1b | full_story_part3_c12 | PASS | speciality→forte[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 25 | er056_output/en_asr_confirm_retry_redesign_01/evidence_snapshot/b1b_audit/tts_generation_results.json | comment_2 | PASS | entered→reached[r,k2] (entry.canonical_text) | PASS_NORMALIZED | SKIP/SKIP/PASS | NOT_USED | - |
| 26 | er057_output/coffee_final_listening_tone_trial_01/part_45/evidence_snapshot/b1b | comment_2 | PASS | entered→reached[r,k2] (entry.canonical_text) | PASS_NORMALIZED | SKIP/SKIP/PASS | NOT_USED | - |
| 27 | er058_output/unified_all_roles_production_wiring_01/evidence_06b/lr_en/run/b1b | full_story_part1_c1 | PASS | ∅→The[i,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | NOT_USED | LR_REASON_UNAVAILABLE |
| 28 | er118_output/fz_full_episode_trial_01/monkeys_paw/a2/run/a2 | full_story_part1_c10 | PASS | guest→visitor[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | UNKNOWN | RECORD_INCOMPLETE,LR_REASON_UNAVAILABLE |
| 29 | er118_output/fz_full_episode_trial_01/monkeys_paw/a2/run_selfcheck/a2 | full_story_part1_c10 | PASS | guest→visitor[r,k2] (entry.canonical_text) | PASS | SKIP/SKIP/PASS | UNKNOWN | RECORD_INCOMPLETE,LR_REASON_UNAVAILABLE |
| 30 | Y:redelivery_fee/run_01/a2 | y_voice_1 | PASS_SUPERSEDED_BY_HUMAN | - (-) | PASS | SKIP/SKIP/SKIP | NOT_USED | STYLE_RECORD_CONFLICT |
| 31 | Y:redelivery_fee/run_01/b1b | y_voice_1 | PASS_SUPERSEDED_BY_HUMAN | - (-) | PASS | SKIP/SKIP/SKIP | NOT_USED | - |
| 32 | Y:redelivery_fee/run_tru_ev_y_adv_1/b1b | comment_1 | PASS | about→of[r,k2] (support_texts.json:comment_1) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 33 | Y:redelivery_fee/run_tru_ev_y_adv_4b/b1b | y_voice_1 | PASS | notice→note[r,k2] (parts.json:segments.y_voice_1) | PASS | SKIP/SKIP/PASS | NOT_USED | - |
| 34 | Y:redelivery_fee_stdchunk_ev/run_ev_01/a2 | y_voice_1 | PASS_SUPERSEDED_BY_HUMAN | - (-) | PASS | SKIP/SKIP/SKIP | NOT_USED | STYLE_RECORD_CONFLICT |
| 35 | Y:redelivery_fee_stdchunk_ev/run_ev_01/b1b | y_voice_1 | PASS_SUPERSEDED_BY_HUMAN | - (-) | PASS | SKIP/SKIP/SKIP | NOT_USED | - |

読み方: `LR_REASON_UNAVAILABLE`=LR理由が記録に無い(Z形は`diff_summary`のみ、resume形等)。表示用の語句差分はbefore/afterから導出済みなので位置特定・overlayには影響しない。#21/#28/#29=Z猿の手Std(§5(b))。#30/#34=Y E-1 a2の`STYLE_RECORD_CONFLICT`(§5(a))。Melos→Heは`T3`でPASS+`entity_pronoun_substitution`フラグ(`speaker_table.md`の話者名を人物台帳に使用、全文にMelosが残るため。INTEGRATION F-12どおり、名前が全文から消える将来のケースはT3でSTOP→ユーザー判断)。

**台帳導出の対象外(8件、43-35)**: W4 §3一覧の#1-3(`er011_output/local_rewrite_recovery/*`のartifact複写=LR監査コピーのみでentryなし)、#6(coffee m2p0 comment_2: 最終音声は原文でentryにLR記録なし=派生run)、#15・#16(kgcpw E7: 同形の派生)、#19(`er020`のevidence json単体)、#34(`ence_06b/lr_en/local_rewrite_recovery_*.json`単体。同一事象の`er058 run`=本表#27は処理済み)。いずれもtts_generation_results.json上にLR採用entryが無く、`build_lr_ledger`の入力にならない(複写/派生)。

## 4. AI島(R-7)と代表Fallback採用entry
AI島 `ai_island_temple__run_form_prod_01`(a2/b1b、保存済みLR後音声のまま・再TTSなし):

| level | 導出されたLR | 表示overlay | 採用take | Fallback | T1/T2/T3 |
|---|---|---|---|---|---|
| a2(Std) | `AIs`→`AI agents`(replace、anchor `the`+`sent to the`) | parts.json part1の該当1語のみ`AI agents`へ(`unit_sha_before/after`を記録) | attempt wavのsha一致(attempt7=LRブロック第1回、role Style sha=`3a680861…`=`expected_base_sha256`) | NOT_USED(元の未採用③をFallbackと誤表示しない=W4落とし穴1) | PASS/PASS/PASS(確定5項目、T2の出典文18) |
| b1b(Adv) | `AIs`→`AI systems`(記録changed_spanは`The AIs sent to the`だがトークン差分は`AIs`1語) | part1の該当1語のみ`AI systems`へ | 同(attempt4、route=`english_style_prefix_wide_margin`=role Style) | NOT_USED | PASS/PASS/PASS(出典文19) |

parity=PASS(表示overlay後=TTS入力=ASR正解)。

Fallback採用entry(`er019`/`er121`/`er026`配下の保存済みtts_generation_results.json 276件を走査、API 0): Fallback採用と導出された**32 clip**=EN短文12・JA短文7・ENGLISH_LOCK 8・Z会話LEGACY_DIALOGUE 5(いずれもtru_ev/evidence/trial系+告げ口心臓の2件)。主要例:
- **告げ口心臓Adv `kp2_en`(`run_reselect_01`)=ENGLISH_LOCK**(attempt wavのsha一致、instruction sha=`dcd08dca…`)。Zの既存`style_actual`がK2と誤同定していた件(W4 A-1/INTEGRATION F-7)を、er129は正しく導出(`test_real_tell_tale_heart_adv_kp2_en_is_english_lock`)。告げ口心臓の他のFallback: `comment_2`(a2、`run_chunk_01`)=JA短文。
- tru_ev系: X(EN短文: x_adv_1/12/14b/16・x_std_1b/4、ENGLISH_LOCK: x_adv_10・x_std_8、JA短文: x_std_6)、Y(EN短文: y_std_4b、JA短文: y_std_2b)、Z(ENGLISH_LOCK: z_adv_6・z_std_5、JA短文: z_std_4、LEGACY_DIALOGUE: z_adv_2・z_std_2・fzcw e2/e3)。うち3 entry(smoke1 x_std_1 topic_intro、small_bag kp5_japanese_meaning ほか)はstyle shaを持たない旧記録で`fallback_used`フラグ+verified行から導出(`how=fallback_used_flag(no LR)+verified row`、LR採用なしのときだけ使用)。
- 終端NG(STOPPED等)39件は`NOT_ADOPTED`(採用take自体が無い。Fallback/LR表示対象外)。

## 5. 想定外の発見(判断候補、区分付き。`USER_DECISION_REQUIRED`の付与はFable)
(a) **Y E-1 a2 `y_voice_1`**: ユーザーがHR承認した`attempt5`のattempt json(`y_voice_1_attempt5_custom53fd514d.json`)は`route=custom_53fd514d`、`instruction_text`のsha=`9293e0c3…`(`calm, steady news narration`=役割Style)で、**Fallback Styleではない**。一方entry直下の`instruction`/`style_prefix`は`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`(dba23e66…)で、これはHR採用前の最終試行の値(陳腐化)。W4 §3-3の「Y E-1 a2=attempt5(EN短文Fallback)」はentry直下値に依拠していた可能性。er129は**送信時の直接記録(attempt json)を正**とし、`STYLE_RECORD_CONFLICT`警告を付けた。最終Human報告でY E-1 a2を濃青(Fallback)にするかの根拠が変わる→**区分B(Fable判断)**。ユーザー承認記録(`ypl7_user_approval_record_y_voice_1.json`: adopted_attempt=5、wav=`attempt5_custom53fd514d.wav`)とは整合。b1b(attempt6、`english_style_prefix_wide_margin`=role Style)は両記録が一致しNOT_USED。
(b) **Z猿の手Std `full_story_part1_c10`(公開物、#21/#28/#29)**: LRブロックのattemptがattempts[]にもattempt jsonにも残っておらず(jsonは元ブロック①②③のみ。最終wav `ca02fcab…`と`_original.wav` `2907822b…`はどのattemptのshaとも不一致)、採用takeを導出できない(`UNKNOWN`)。LR自体(`guest`→`visitor`の位置特定・三者一致)はPASS。これは**記録欠落そのもの**で規則では救えない(推測しない)。委任_06のfinal_adoptionにより今後のrunでは記録される。既存公開物は最終Human報告で「LR=赤(あり)/Fallback=記録なし」と表示される。B4のfail-closedでは旧記録UNKNOWNはBLOCK(F-6)だが、既公開記事の再組立は発生しないので実害なし。**区分C(軽微・実害なし)**。
(c) **entry.textとselection.rewritten_segmentが語順/接続語で異なる事例**(#7 hormuz comment_4、#11 meta in_one_line、#25/#26 comment_2)は送信前正規化(TTS側)による差。M-1どおり表示=選定文(`rewritten_segment`)を基準とし、TTS入力との差は`PASS_NORMALIZED`。**区分A(既存仕様内で自己解決済み)**。

## 6. 検証(runtime evidence)
- `.venv\Scripts\python.exe -m pytest er129_lr_display_reflection_01_test_01.py -q` → 39 passed(約5秒)。内訳: 合成ケース(U1位置特定8・U2 overlay2・U3経路6・U4三者一致2・U5重なり3・U6採用take6・U7/U8純module/監査出力3)+実データ(AI島・告げ口心臓・Y E-1・保存LR 7 level parametrizeで偽STOP 0確認)。
- 実データ全件の再現=`build_lr_ledger('', '', results_path=<各tts_generation_results.json>)`(読取のみ)。本書§3の値はこの実行結果。
- 既存test(er020/er127/er128等)は未実行・未変更(既存Productionコードに触れていないため。本委任の変更は新規2ファイル+OPUS台帳+本成果物のみ)。

## 7. 未観測・限界
- `final_adoption`(委任_06が追加中)を持つ実entryは本調査時点で保存データに存在しない。③の経路は合成entryで検証(実runでの記録は次回run)。
- Z会話ctx・KP_EN Store key B hitの実データでの`final_adoption`経路は未観測(合成のみ)。KP_EN Store再利用の旧entryで`reused`印のみの実例は固定殻(`existing_master`=NORMAL扱い)に限られる。
- 確定内容重なり(T1/T2)は`confirmed_selection.json`のある保存runがAI島のみのため、実データのT1/T2検証はAI島(確定5項目、全非該当)のみ。他は合成ケース。
- HR採用でadopted attemptのjsonが無い場合は`kind=None`(`RECORD_INCOMPLETE:adopted_style`)を返す設計(実例0)。
- 数詞比較は`one`〜`twenty`・tensのみ。`hundred`以上・序数(first/second)は語のまま。
- 表示unit候補の優先順(parts.json part*/segments → support texts → entry.canonical_text)は実データ7構造(X part/support、Y segments/support、Z clip)で確認。X chunkの親part写像検証(W2 §4-2-3)は`chunk_tts.parent_id`による親part特定まで(chunk plan再分割一致の検証は未実装=B3/統合時)。

## 8. RESULT_PACKET用4行
1. 既存仕様整合: `er020_tts_retry_local_rewrite_01.py:852-891`(ASR正解の唯一の参照点)、`er128_kp_confirmed_content_01.py:1236-1259`(`lr_overlap`再利用)、`er127_tts_block_policy_01.py:582-612`・`er122_fz_ctx_policy_01.py:390-405`・`er019_family_x_kp_en_k2_store_01.py:55-70`(`final_adoption` schema=委任_06)、`er121_e1_hr_adopt_r0_01.py:132-147`(HR採用記録)、OPUS_REVIEW_01 (b)1-6/M-1〜M-6、W2 §4-§6。
2. Production到達経路の未承認機能既定値: 本moduleは未配線(importゼロ、`test_u8_no_production_module_imports_er129`)。flag・起動script・.envへの接続なし。API呼出0。
3. 失敗終了時の最終成果物: 該当なし(正常終了)。成果物=`er129_lr_display_reflection_01.py`+`er129_lr_display_reflection_01_test_01.py`+本書+OPUS台帳OF-LRW-M01〜M10。目的要件(LR後の英文を表示本文へ反映するための台帳導出・採用take解決・偽STOP 0)に対し、保存35 entryで偽STOP 0・AI島のAI agents/AI systems導出を実測確認。ただしProduction未配線のため最終表示本文への反映はまだ(B3・統合commit後)。
4. 撤去・残置: 撤去した規則/検査なし(新規module)。`confirmed_kp_lr_overlap.json`はGate入力にしない(er129内に読込0)、entry直下`fallback_used`はLR採用なしの最終手段のみ(LR採用時は使わない)。

判定整合: 重大NG=なし
