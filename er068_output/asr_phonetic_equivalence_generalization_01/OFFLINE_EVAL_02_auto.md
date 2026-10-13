# OFFLINE_EVAL_01: 発音同等性に基づく一般化ASR判定(Trial隔離プロトタイプ)の既存データ read-only 評価

管理ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01 / 費用 JPY0 / 新規API呼出 0 / 使用モデル: なし(CMU辞書・ローカルDSPのみ) / Production無変更

KPI provenance: 本表の数値はすべて `reuse`(既存転写・既存wavの再評価)+`synthetic`(er065合成反例・CS監査合成sweep・本script内の構成テキスト反例)。fresh Production初回path E2E値: No。

## 0. 比較する判定(定義)

- **V0** Production現行: `val.classify_asr_match`(segment_id=FULL_STORY)+ `_step_alternate_pass`(CMU同音Case A)。Tier3(Azure)等ASR呼出を要する救済は含まない(read-only)。
- **VA** 既存Pattern A/B/C単独(`csv3.classify_connected_speech`)。
- **V1** 設計判定(ASR転写テキストのみ): V0がPASSならそのまま(判定を変えない)/ V0 UNCERTAIN(固有名詞・同音語のみの差)でM1(CMU確認済み同音綴り正規化→既存判定)が通れば ACCEPT_M1 / 音素水準で連結発音と説明できれば説明付きHR候補(M2)/ 説明不能は既存判定へ委譲。
- **V2** V1のACCEPT_M1に『clip末尾完全性の独立確認(ローカルDSP)』をAND。確認不能(wavなし)・NGはHR候補へ降格。
  末尾確認: 末尾50msの最大フレームRMSが、clipのp95フレームRMS比-30dB以下。閾値はProduction健全wavのみから決定(切詰wavでは調整していない)。

## 1. 評価A: 正常音声の誤NG削減(V0が通さないもののうち、V1/V2が救済する件数)

真値列: normal=Production採用済み正常音声由来/unknown=真値未確定(HR待ちを含む)/normal_by_construction=構成上正常想定(循環の恐れあり、参考値)。

| データセット | 真値 | n | V0 PASS | V0非PASS | V1 新規ACCEPT | V1 HR候補 | V2 新規ACCEPT | V2 HR候補 | wav有 |
|---|---|---|---|---|---|---|---|---|---|
| control_synth_intact | normal | 33 | 25 | 8 | 7 | 0 | 7 | 0 | 33 |
| cs_sweep_exact_stem_drop | normal_by_construction | 108 | 108 | 0 | 0 | 0 | 0 | 0 | 0 |
| cs_sweep_stem_variant_spelling | normal_by_construction | 114 | 12 | 102 | 12 | 12 | 0 | 24 | 0 |
| cs_synthetic_normal | normal_by_construction | 19 | 12 | 7 | 2 | 1 | 0 | 3 | 0 |
| general_2word_control | normal | 46 | 33 | 13 | 0 | 0 | 0 | 0 | 0 |
| general_2word_fusion | normal | 278 | 129 | 149 | 0 | 0 | 0 | 0 | 0 |
| melos_takes_alone | unknown | 41 | 10 | 31 | 22 | 5 | 22 | 5 | 41 |
| normal_text_general_homophone_spelling | normal | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| normal_text_general_nonword_spelling | normal | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| normal_text_general_pattern_a_native | normal | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| normal_text_pattern_b_native | normal | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| normal_text_proper_noun_homophone_spelling | normal | 4 | 0 | 4 | 3 | 0 | 0 | 3 | 0 |
| normal_text_proper_noun_homophone_spelling_s_present | normal | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 0 |
| normal_text_proper_noun_other_spelling | normal | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| normal_text_proper_noun_pattern_a_native | normal | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| real_diff_instances | normal | 124 | 42 | 82 | 10 | 5 | 0 | 15 | 0 |
| real_pairs_612 | unknown | 612 | 16 | 596 | 23 | 20 | 0 | 43 | 0 |
| reeval_post_slowdown_primary | normal,unknown | 20 | 0 | 20 | 12 | 0 | 12 | 0 | 20 |
| slowdown_pair | unknown | 68 | 37 | 31 | 22 | 2 | 0 | 24 | 0 |

実データ系の合計(real_pairs_612 / general_2word_fusion / general_2word_control / melos_takes_alone / control_synth_intact / reeval_post_slowdown_primary。real_diff_instances は real_pairs_612 と同一ログ由来のため重複除外): V0非PASS 817件中、V1新規ACCEPT 64件、V1説明付きHR候補 25件。
(slowdown_pair・cs_sweep・normal_text・cs_synthetic は構成/重複のため別掲の参考値で合計に含めない。)

### 1-1. V1新規ACCEPTの内訳(真値normal/unknown/構成想定の全データセット、重複を含む)

| 種別 | 受理に使われた既存規則 | 件数 |
|---|---|---|
| proper_noun | Pattern_A_sibilant_sequence | 66 |
| proper_noun | NORMALIZED_MATCH | 28 |
| proper_noun | EXACT_MATCH | 20 |

新規ACCEPTの正規化(元綴り→置換綴り→対応canonical語):

| ASR綴り | 置換(同音綴り) | canonical語 | 根拠 | 固有名詞扱い | 件数 |
|---|---|---|---|---|---|
| mello | melo | melos | cmu | True | 39 |
| mellos | melos | melos | cmu_stem+regular_s | True | 31 |
| mellow | melo | melos | cmu | True | 27 |
| mellows | melos | melos | cmu_stem+regular_s | True | 17 |

**Melos以外の新規ACCEPT件数: 0件**(実データ・sweepとも、新規救済はMelosの `Mello/Mellow/Mellos/Mellows` に限られた。一般化の実効は『ASR綴りがCMU収録語の同音綴りで、かつ承認済みPattern/厳密一致が期待する綴りと同音』の場合に限られ、実データではMelosのみ。)

### 1-2. V1 説明付きHR候補の内訳(自動受理ではない。HR件数は減らさず確認時間の短縮のみ)

| 区分 | 音韻診断(境界型等) | 件数 |
|---|---|---|
| HR_CANDIDATE_RISK_FLAGGED | voicing_weak:GEMINATE_SAME | 9 |
| HR_CANDIDATE_RISK_FLAGGED | fusion:GEMINATE_SAME | 7 |
| HR_CANDIDATE_RISK_FLAGGED | homophone_spelling_only | 6 |
| HR_CANDIDATE_EXPLAINED | fusion:SIBILANT_SEQ+resegmentation | 6 |
| HR_CANDIDATE_EXPLAINED | fusion:SIBILANT_SEQ | 5 |
| HR_CANDIDATE_EXPLAINED | resegmentation+voicing_weak:SIBILANT_SEQ | 5 |
| HR_CANDIDATE_RISK_FLAGGED | fusion:STOP_STOP_UNRELEASED | 2 |
| HR_CANDIDATE_EXPLAINED | homophone_spelling_only | 2 |
| HR_CANDIDATE_RISK_FLAGGED | fusion:SIBILANT_SEQ | 1 |
| HR_CANDIDATE_EXPLAINED | homophone_spelling_only+resegmentation | 1 |
| HR_CANDIDATE_EXPLAINED | voicing_weak:SIBILANT_SEQ | 1 |

## 2. 評価B: 異常音声の誤PASS防止(真値=欠陥のデータセット)

既存誤PASS(V0 PASS)は『テキストだけでは検出できない既存の限界』(例: 末尾切詰でASRが全文を正しく書いた、Pattern Aの first-diff-only 受理)を含む。本設計の評価指標は **増分** = V0がPASSにしないのにV1/V2がACCEPTにした件数(目標0)。

| データセット(欠陥の種類) | n | V0 PASS(既存誤PASS) | VA PASS | V1 新規ACCEPT=増分 | V2 新規ACCEPT=増分 | V1→V2でHRへ降格 |
|---|---|---|---|---|---|---|
| cs_synthetic_counter | 6 | 0 | 0 | 0 | 0 | 0 |
| defect_natural_ng_proxy_content_mispronounced | 8 | 0 | 0 | 0 | 0 | 0 |
| defect_natural_ng_proxy_context_guessable_homophone | 31 | 28 | 28 | 0 | 0 | 0 |
| defect_natural_ng_proxy_final_consonant_added | 34 | 23 | 22 | 0 | 0 | 0 |
| defect_natural_ng_proxy_final_consonant_drop | 13 | 1 | 1 | 0 | 0 | 0 |
| defect_natural_ng_proxy_proper_noun_mispronounced | 39 | 0 | 0 | 0 | 0 | 0 |
| defect_synth_missing_word | 26 | 0 | 0 | 0 | 0 | 0 |
| defect_synth_tail_trunc | 150 | 122 | 116 | 28 | 0 | 28 |
| defect_synth_wrong_name | 15 | 0 | 0 | 0 | 0 | 0 |
| defect_text_context_extra_word | 2 | 0 | 0 | 0 | 0 | 0 |
| defect_text_meaning_flip | 2 | 0 | 0 | 0 | 0 | 0 |
| defect_text_multi_diff_masking_existing_hole | 1 | 1 | 1 | 0 | 0 | 0 |
| defect_text_multi_name_one_homophone | 2 | 0 | 0 | 0 | 0 | 0 |
| defect_text_negation | 5 | 0 | 0 | 0 | 0 | 0 |
| defect_text_number | 4 | 0 | 0 | 0 | 0 | 0 |
| defect_text_tense | 4 | 2 | 2 | 0 | 0 | 0 |
| defect_text_word_dropped | 4 | 0 | 0 | 0 | 0 | 0 |
| defect_text_wrong_name | 9 | 0 | 0 | 0 | 0 | 0 |
| defect_text_wrong_name_or_spelling | 1 | 1 | 0 | 0 | 0 | 0 |
| defect_text_wrong_word | 7 | 1 | 1 | 0 | 0 | 0 |

**合計: 欠陥観測 363件、既存誤PASS(V0) 179件、V1増分 28件、V2増分 0件。**

V1増分の全内訳(ds / target / ASR転写 / 末尾チェック):
  - defect_synth_tail_trunc / syn_B1_trunc140 / `mello said` / tail_ok=False : 5件
  - defect_synth_tail_trunc / syn_B1_trunc140 / `mellos said` / tail_ok=False : 3件
  - defect_synth_tail_trunc / syn_B1_trunc140 / `mellow said` / tail_ok=False : 1件
  - defect_synth_tail_trunc / syn_B1_trunc220 / `mello said` / tail_ok=False : 6件
  - defect_synth_tail_trunc / syn_B1_trunc220 / `mellos said` / tail_ok=False : 2件
  - defect_synth_tail_trunc / syn_B1_trunc220 / `mellow said` / tail_ok=False : 1件
  - defect_synth_tail_trunc / syn_B1_trunc70 / `mello said` / tail_ok=False : 5件
  - defect_synth_tail_trunc / syn_B1_trunc70 / `mellos said` / tail_ok=False : 4件
  - defect_synth_tail_trunc / syn_B1_trunc70 / `mellow said` / tail_ok=False : 1件

**判定規則(委任文)**: Pattern A比の誤PASS増分>0の方式は採用候補から外す(REJECTED候補)。V1(テキストのみ)の増分は 28件 → **REJECTED候補**。V2(+末尾確認)の増分は 0件(ただし下記のとおり検出網羅性は未検証)。

## 3. 末尾完全性チェックの較正と検出率

| 健全wav群(Production run_e2e_02、_original除く) | n | tail_ok | 最大rel_tail_db |
|---|---|---|---|
| production_a2_narration | 48 | 48 | -38.23 |
| production_b1b_narration | 49 | 49 | -30.44 |

切詰・欠陥wav側(target単位、wav数/末尾チェックで検出された数):

| ds target | wav数 | tail_flagged |
|---|---|---|
| control_synth_intact|ctl_B1_intact | 1 | 0 |
| control_synth_intact|ctl_B2_intact | 1 | 0 |
| control_synth_intact|ctl_B4_intact | 1 | 0 |
| defect_natural_ng_proxy_content_mispronounced|nat_turnout | 1 | 0 |
| defect_natural_ng_proxy_context_guessable_homophone|nat_bements | 1 | 0 |
| defect_natural_ng_proxy_context_guessable_homophone|nat_design | 1 | 0 |
| defect_natural_ng_proxy_context_guessable_homophone|nat_feet | 1 | 0 |
| defect_natural_ng_proxy_final_consonant_added|nat_counts | 1 | 0 |
| defect_natural_ng_proxy_final_consonant_added|nat_forced | 1 | 0 |
| defect_natural_ng_proxy_final_consonant_added|nat_paused | 1 | 0 |
| defect_natural_ng_proxy_final_consonant_drop|nat_reduce | 1 | 0 |
| defect_natural_ng_proxy_proper_noun_mispronounced|nat_melus_hand | 1 | 0 |
| defect_natural_ng_proxy_proper_noun_mispronounced|nat_milo | 1 | 0 |
| defect_natural_ng_proxy_proper_noun_mispronounced|nat_milos_hand | 1 | 0 |
| defect_synth_tail_trunc|sweep_B2_trunc300 | 1 | 1 |
| defect_synth_tail_trunc|sweep_B2_trunc380 | 1 | 1 |
| defect_synth_tail_trunc|sweep_B2_trunc460 | 1 | 1 |
| defect_synth_tail_trunc|syn_B1_trunc140 | 1 | 1 |
| defect_synth_tail_trunc|syn_B1_trunc220 | 1 | 1 |
| defect_synth_tail_trunc|syn_B1_trunc70 | 1 | 1 |
| defect_synth_tail_trunc|syn_B2_trunc140 | 1 | 0 |
| defect_synth_tail_trunc|syn_B2_trunc220 | 1 | 1 |
| defect_synth_tail_trunc|syn_B2_trunc70 | 1 | 1 |
| defect_synth_tail_trunc|syn_B4_trunc140 | 1 | 0 |
| defect_synth_tail_trunc|syn_B4_trunc220 | 1 | 1 |
| defect_synth_tail_trunc|syn_B4_trunc70 | 1 | 0 |

注意(未検証/限界): (1) 合成切詰wav(syn_B*_trunc)は『発話末をN ms削除+8ms fade』で作られ、**元wavの末尾無音も同時に失われる**ため、末尾エネルギー検出が実際のTTS切詰より容易な可能性がある。(2) B2/B4の70-220ms切詰の一部は末尾チェックを通過する(検出されない)。(3) 自然に発生したTTS末尾欠損の真値付きwavは本データに無い(natural_ng は proxy)。→ V2の増分0は『この小さな合成セットで』であり一般的な保証ではない。

## 4. 減速前後(Std 6%減速)の判定一致

attempt_history の A2_SLOWDOWN_REVERIFY 由来の(減速前Primary転写, 減速後Primary転写)対: 34対(canonicalはtts_generation_resultsから復元、sha256一致のみ採用)。
- 同一転写文字列の対 15対で、V1の判定が同一: **15/15**(判定はcanonicalと転写テキストの純関数であり、減速の有無を入力に持たない=判定思想は減速前後で同一)。
- 転写が異なる対を含む全34対での PASS/HR/DEFER 群の一致: V0=29/34、V1=26/34。不一致はASR転写自体が減速で変わったこと(例 Mellows→mellowes)による。
- 注意: 減速前後は別音声(6%伸長)のため『同一wav対』ではなく『同一take対』。ASR転写が揺れる限り判定も揺れる(判定器でなくASR揺れの問題)。

| pair | canonical | 減速前ASR | 減速後ASR | 前V1 | 後V1 |
|---|---|---|---|---|---|
| run_e2e_01:full_story_part1_c18:1:12427 | His friend's warm, steady fingers closed | His friend's warm, steady fingers closed | His friend's warm, steady fingers closed | EXACT | DEFER_NOT_EXPLAINED |
| run_e2e_02:full_story_part3_c1:1:12687 | He remembered the hands held out for the | He remembered the hands held out for the | He remembered the hands held out for the | ACCEPT_M1 | DEFER_NOT_EXPLAINED |
| run_e2e_02:full_story_part3_c1:2:12689 | He remembered the hands held out for the | He remembered the hands held out for the | He remembered the hands held out for the | EXACT | DEFER_NOT_EXPLAINED |
| run_e2e_02:full_story_part3_c1:3:12692 | He remembered the hands held out for the | He remembered the hands held out for the | He remembered the hands held out for the | HR_CANDIDATE_EXPLAINED | EXACT |
| run_e2e_02:full_story_part3_c3:1:12695 | His friend turned around, and Melos fell | His friend turned around and Mellows fel | His friend turned around and mellowes fe | ACCEPT_M1 | DEFER_NOT_EXPLAINED |
| run_e2e_02:full_story_part1_c1:1:12738 | Melos called across the hall, | Mellus called across the hall. | Mellos called across the hall. | DEFER_NOT_EXPLAINED | ACCEPT_M1 |
| run_e2e_02:full_story_part3_c3:1:12740 | His friend turned around, and Melos fell | His friend turned around, and Mellis fel | His friend turned around, and Mellos fel | DEFER_NOT_EXPLAINED | ACCEPT_M1 |
| run_e2e_02:full_story_part1_c5:1:12766 | Melos said. | Mellowset | Mella said. | HR_CANDIDATE_EXPLAINED | DEFER_NOT_EXPLAINED |

## 5. 受理面の拡張プローブ(構成のみ・真値なし): 同音綴り正規化で『Pattern Aが受理する綴り』に何が加わるか

s終わり固有名詞 54語 x 歯擦音始まり動詞6語。Pattern A が受理する ASR 形(stem 綴り)の CMU 代表発音同音綴りのうち、M1 が新たに ACCEPT にした綴りの数: **10語で追加あり、追加綴り延べ 21個**。
これは『ASRが語末sを落とした音声の別綴り』だけでなく、**語末sが元から無い別の実在語・別の名前**(例 Jones→Joan、Hayes→Hey、Torres→Tore)も、s脱落の仮定の下で同じ基準で受理されることを意味する。Pattern A 自体が `Hayes said ← Hay said` を綴りで受理する既存の性質(OPEN-330)の自然な延長だが、**受理面が広がる**事実は誤PASS露出の増分として Opus/ユーザーの判断対象(音響の独立証拠なしには区別不能)。

| 名前 | Pattern A が受理する stem 綴り | M1 が追加で受理する同音綴り |
|---|---|---|
| Carlos | carlo | carlough, carlow, karlow |
| Lucas | luca | lucca, luka |
| Jones | jon, jone | joan |
| Wells | well | welle |
| Mills | mill | mil, mille |
| Hayes | hay, haye | haigh, hey |
| Santos | santo | santow |
| Silvas | silva | cilva, sylva |
| Haynes | hayn, hayne | hahne, hain, hane, heyn, heyne |
| Melos | melo | mello, mellow |

## 6. State guard

`state_guard_01.json` 参照: 実行前後で Production state 9ファイル(Melos run_e2e_02 a2/b1b の review_lock_state・tts_generation_results、Master Store manifest、er021 telemetry、HR queue、attempt_history、Pronunciation ledger)の sha256/行数が不変: True
