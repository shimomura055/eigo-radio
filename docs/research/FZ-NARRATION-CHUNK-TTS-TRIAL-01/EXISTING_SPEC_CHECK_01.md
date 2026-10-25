# EXISTING_SPEC_CHECK_01 (FZ-NARRATION-CHUNK-TTS-TRIAL-01 委任_01 Phase 0、API 0・Production変更0)

原文: `docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_USER.md` §3〜§5。21節(PM_GOVERNANCE.md:3279)の照合結果を先頭に置く。

## 0. 分類(21節)
- **B(過去Trialあり・未採用/未確定)**: 段落単位TTS chunk(X: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01)は直前Trial済み(OPEN-506)、Zの『長い地の文のみ追加分割』は未Trial。P6B(2-Macrochunk、ユーザー試聴不合格)とは条件が異なる(下記§5)。再検証が必要な理由=Zのnarrator story clipは1 clip 90〜150語(35〜48秒)で、Xのpart全体(約143語)と同規模の1 call読みであり、Xで確認した『chunk化で実発話が約5〜7%遅くなる』効果がZの一人称独白でも得られるか、かつ文学的緊張を損なわないか、が未検証のため。
- **A(既存仕様あり、流用)**: Dialogue/話者切替clip分割、Voice割当、clip間gap、音量正規化、速度仕様v2、trim、結合関数(§1〜§4)。新規仕様にしない。
- **C(新規)**: 『narrator clipが閾値超のとき追加分割し、chunk間を0.2秒でつなぐ』の規則そのもの(ユーザー指示2026-10-25で方向は承認済み、閾値と優先順は本Trialで設計→試聴で採否)。

## 1. Family Z正式経路のsegment分割構造(照合済み)
| 項目 | 内容 | 出典(file:line) |
|---|---|---|
| story段 | `plan`(段落分割・話者帰属・clip化)→`support`→`kp`→`tts_b1b`/`tts_a2`→`provision_shell,gate,assemble,pages,page_verify` | `er026_family_z_fiction_production_runner_01.py:1416(stage_plan),1437(stage_support),1843(stage_tts),1866,1875,1885,1897,1930` |
| 平坦化 | 段落→(段落index, voice, 生テキスト)列。引用(`QUOTE_RE`)は話者のvoice、地の文はnarrator。引用間の空白chunkは捨てる | `er062_family_z_structure_01.py:851-865(build_flat_chunks)` |
| clip化 | `plan_story_segments(flat, force_split_before_paragraphs={b1,b2})`を全文1回で呼び、`full_story_part{n}_c{k}`へ改名。Part境界を跨ぐclipはSTOP | `er062…:868-893(plan_clips)`、`er013_family_c_production_01.py:202-248(_build_base_segments)` |
| 同一Voice連続の結合 | 同一Voiceが続く限り(段落をまたいでも)1 clipに結合。voiceが変わる/force_splitでのみ分割。**このため『セリフが少ない作品』では地の文が段落を越えて1 clipに連結される** | `er013_family_c_production_01.py:202-248` |
| 語数目安 | target 100 / soft_max 120 / hard_avoid 150語。**hard_avoid超過時のみ**、複数段落なら語数中点に最も近い段落境界で2分割(Voice/scene境界は上書きしない)。それ以外は警告のみ(ブロックしない) | `er013_family_c_production_01.py:251-303(_apply_word_guideline_splits),306-326(plan_story_segments)` |
| TTS生成 | narrator: Advは`news_tail_fix.generate_news_narration_wide_margin(…style_prefix_override, enable_repetition_qa=True, enable_pronunciation_resolver=True, enable_connected_speech_equivalence_layer=cs(spec), tts_backend=speech_metadata_flash_lite)`、Stdは`generate_a2_segment_with_slowdown`(6%減速)。dialogue: Advは`generate_with_a2_slowdown_outer_loop(slowdown_pct=-5.66)`(atempo 1.06高速化)、Stdは後処理なし | `er063_family_z_audio_01.py:835-860,863-873` |
| 速度仕様v2 | (Std,Narrator)=6%減速 / (Std,Dialogue)=後処理なし / **(Adv,Narrator)=後処理なし** / (Adv,Dialogue)=約6%高速化。`Z_SPEED_PROFILE_VERSION=z_speed_v2` | `er063…:49-64`、`CURRENT_SPEC.md:1630,1692` |
| Voice割当 | narrator=Aoede、会話=決定的割当(男5/女5 pool、初出順、`derive_voice_assignment`)。『告げ口心臓』は`old_man`=Algieba、`officer`=Schedar | `er062…:47-53,105-145`、`run_sf_prod_01/voice_assignment.json` |
| 音量 | `target_rms=(preview RMS + 最初のstory clip RMS)/2`、各clipを`compute_gain_for_target_rms`で個別にscalar gain(独立TTS出力ごと)→`mono_24k_to_stereo_target`→`assemble_with_timeline`→`apply_headroom_safety_valve` | `er063…:1761-1765,1771-1776,1793-1795` |
| trim | TTS生成関数内部の`trim_english_keyword_silence`(前後~0.24〜0.35s残置)。Z固有の追加trimは未確認(生成関数内trimのみ使用) | `er003_b1_p3u_audio`(X Trial EXISTING_SPEC_CHECK_01 §と同一) |
| clip間gap | story clip間: narratorの後=**0.5秒**、voice≠narratorの後=**0.2秒**。Comment挿入時は前後に1.0/0.8秒 | `er013_family_c_production_runner_01.py:670` |
| 結合 | `np.concatenate`のみ(crossfade・重ね合わせなし) | `er003_v1_n3_01_assemble.assemble_with_timeline`(X Trialと同一) |
| 再利用/記録 | clipごとのreuse_key(text_sha・style・speed_profile等)、`tts_generation_results.json`、人手承認/HR Lock | `er063…:738-806` |

**重要な帰結**: 追加chunk間のポーズ0.2秒は、既存のZ story clip gapのうち『voice≠narratorの後=0.2秒』と同じ秒数で、新規の独自秒数ではない(ユーザー指定)。一方、narrator→narratorの既存gapは0.5秒(旧Xの旧B)で、今回の追加分割ではそれより短い0.2秒を使うため、聴感上『同一場面内の連続』として扱う設計になる。

## 2. 『告げ口心臓』現行run(`run_sf_prod_01`)のclip構成(定量)
出典: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/segment_plan_b1b.json`+`b1b/assembly/timeline.json`、集計=`er026_output/family_z_dev_trials/fz_narration_chunk_01/clip_distribution_01.json`。

Advanced(b1b)全6 clip:
| clip | voice | 語数 | 段落数 | 秒 | WPM(clip全長/秒) |
|---|---|---|---|---|---|
| part1_c1 | narrator | **135** | 5 | 47.15 | 172 |
| part2_c1 | narrator | 12 | 1 | 4.48 | 161 |
| part2_c2 | old_man | 2 | 1 | 1.16 | — |
| part2_c3 | narrator | **118** | 8 | 48.20 | 147 |
| part3_c1 | narrator | 91 | 4 | 35.40 | 154 |
| part3_c2 | narrator | 73 | 4 | 27.86 | 157 |
(part3_c1/c2は元164語が`hard_avoid_words=150`超過で既存の自動分割が発火したもの=既存の分割仕様の実例)。Std(a2)も同構造(135/122/93/72語)。

**この作品の地の文は、全語数約431語のうち429語(約99%)がnarrator、最長clipは135語/47秒。** 

全作品(Advanced・narrator clip)の語数別WPM(clip全長ベース、端のtrim残置を含む。**短いclipほど端の無音比率が大きいため低く出る交絡あり**):
| 語数 | clip数 | 平均WPM |
|---|---|---|
| <30 | 41 | 127.1 |
| 30〜59 | 9 | 156.0 |
| 60〜99 | 6 | 159.9 |
| >=100 | 3 | 163.3 |
(Std narrator>=100語: 157.6 WPM、6%減速後)。長いclipほどWPMが高い傾向はあるが、30語以上では差は小さい(30〜59→>=100で+7 WPM、約4%)。**ユーザー指摘『地の文が長く続くと速くなりやすい』は、この集計でも方向は裏付けられるが、効果量は約4%程度で、閾値決定の根拠にはなるが、体感を機械指標だけで断定できない。**

他候補作品(Adv・narrator clipの最大語数): 『賢者の贈り物』123(part1_c1、43.1秒、171 WPM)/87/78、『猿の手』71/68/58/51、『二十年後』74、『開いた窓』45。**閾値100語を超えるのは『告げ口心臓』(135/118)と『賢者の贈り物』(123)のみ。** 『猿の手』『二十年後』『開いた窓』は閾値100語では分割対象なし(=Trial比較対象には不適。セリフが多く既存分割が十分に細かい作品に不要な分割を足さないという規則の性質を示す)。

## 3. 現在の一人称化(案A)との関係
- 案A(FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01、UDR #192)は一人称独白のAdvを生成する。Trial 1b_s1(`er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1b_s1`)のAdvは3つの長いnarrator clip(141/118/148語、段落数4/6/6)と短いclip(5語+セリフ2語)で構成。現行`run_sf_prod_01`のAdv(三人称、USER_NG)とは本文が異なる。
- 案Aの正式再生成(`run_sf_prod_02`)は委任_04(Opus条件Aレビュー後のFable Go)で実施予定=本Phase 0時点で未生成(`er026_output/family_z_production_e2e_01/the_tell_tale_heart/`に`run_sf_prod_02`なし、Grep確認)。本Trialは**読取専用**でのみ再利用し、Production run dir・store・公開ページへ書込まない。

## 4. 速度仕様v2・Std
- Adv narratorは速度後処理なし。**Trial対象はAdvのnarratorに限定**する(Std narratorは生成後6%減速が全clip単位で掛かる[`generate_a2_segment_with_slowdown`]ため、chunk化すると『chunkごとの6%減速』と『Z先例の減速検証[`verify_std_english_slowdown`]』の再設計が絡み、A/B条件の分離が崩れる)。Stdは本Trialの対象外とし、Advでの試聴結果が良好な場合に別途判断(判断候補)。
- 会話速度仕様v2(Adv会話atempo 1.06)・極短clip速度Gate(`adv_dialogue_ratio_range`)は会話clip対象でありnarrator chunkには掛からない。本Trialは会話clipを一切変更しないため非干渉。

## 5. 過去Trial・不採用との関係(21節B)
| 先例 | 内容 | 本Trialとの関係 |
|---|---|---|
| ER-003-B1-P4D〜P6B(`CURRENT_SPEC.md:2052,2065,2074`) | 日本語Full Storyを3chunk/2-Macrochunk(別TTS call)で結合→ユーザー試聴で**P6B不合格**(『Macrochunk AとBで声質差があり接続が不自然』)。以降単一TTS call凍結 | 条件差: 本Trialは英語・`gemini-3.8-flash-lite-tts`・段落/文(意味の切れ目)単位・既存RMS正規化+0.2秒の接続・Voice固定(Aoede)・Style同一。P6Bの不合格理由『声質の一貫性』を最重点の試聴項目にする。**無断再導入ではない(ユーザーが2026-10-25に承認したTrial)**。 |
| FX-PARAGRAPH-CHUNK-TTS-TRIAL-01(OPEN-506、UDR #191) | X: 段落Chunk、実発話-約7%、境界音量差<=5.8dB、語欠け/二重なし。0.5秒は長いとの指摘→0.2秒版(本委任Part A)へ | Zの規則はXの結果(段落境界優先・chunk語数・音量差の許容感)を参考にする。 |
| `FAMILY-Z-DIALOGUE-SPEED` v2 | 会話のみの速度調整(Adv会話高速化)。地の文の速度は未対応 | 補完関係(地の文の速度は本Trialが初)。 |
| Family Cの語数目安(`hard_avoid_words=150`の自動分割) | 150語超のみ段落境界で2分割(品質ではなく『長すぎる1 call』回避) | 同系統の既存仕様。本Trialは閾値を100語(同じ`target_words`)に下げた場合の効果検証。Production側の`hard_avoid_words`/`target_words`は**直接編集しない**(承認前仕様のため)。 |

## 6. 結論(Phase 0)
- 既存仕様の再利用で足りる範囲: Dialogue分割・Voice・Style・速度仕様v2・音量・trim・結合・ヘッドルーム弁(全てA)。
- 新規部分(C): 閾値超narrator clipの内部分割規則(DEV専用planner `er114_fz_narration_chunk_trial_01.py`)と、その音声をZ sequenceに差し込むDEV assemblerのみ。
- 本調査でProduction fileの編集は0。
