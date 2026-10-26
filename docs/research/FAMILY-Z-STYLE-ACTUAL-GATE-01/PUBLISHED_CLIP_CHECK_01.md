# PUBLISHED_CLIP_CHECK_01: 猿の手Std `full_story_part1_c10`(Style脱落fallback採用clip)は公開版に含まれるか

管理ID: FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01 / 2026-10-27。read-only(run dir・公開ページ・mp3は不変)。API 0、JPY 0。

## 結論(先頭)
**含まれる。** 公開済みの猿の手Std(a2)のmp3(`user_test/family_z_monkeys_paw_01/audio_standard/MonkeysPaw_a2_full.mp3`、git commit `8cf1f772638d3aeee08f44c113b6ed775126c9a4`、2026-10-24 18:46 JST、origin=github.com/shimomura055/eigo-radio)の **128.623〜133.361秒(2:08.6、長さ4.738秒)** に、承認Style(PD06)を落としたfallback音声が入っている。Adv(b1b)は同run内にfallback採用なし。

## 事実と根拠(照合手順)
1. **採用記録**: `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/a2/audit/tts_generation_results.json` の `full_story_part1_c10`(NARRATOR_FULL_STORY_STD): attempt `standard1`・`standard2`・`fallback1`がすべて`ASR_VALIDATION_UNCERTAIN`(verified=false)。`fallback1`の`instruction_label=FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、`style_prefix_head="natural, clear, conversational"`(承認PD06=「Speak directly to one listener with warm…」を落とす)。`z_adoption=adopted`、`status=OK`、`style.fallback_used=true`、`asr_judgement.state=PASS (primary_pass, NORMALIZED_MATCH)`、人間承認recordなし(Zに該当Gateが無かった=OPEN-551)。
2. **採用wavの特定**: entry.sha256 = `ca02fcab026bcf8d2cb4154bd271099bc4c28360470f167edb8e2e290f97f9cd` = `a2/narration/full_story_part1_c10.wav` の実sha256(一致)。
3. **組立への取込み**: `a2/assembly/timeline.json` に `{"part":"full_story_part1_c10","start_seconds":128.623,"duration_seconds":4.738}`(総尺301.848秒)。組立wav(`Family_Z_the_monkeys_paw_a2.wav`、48kHz)の同区間と`narration/full_story_part1_c10.wav`の正規化相互相関の最大値=**1.0**(同一波形)。他候補との相関(同じ区間): `_original.wav`(減速前)0.338 / standard attempt1 0.069 / attempt2 0.053 / attempt3(minimal fallback) 0.050(=別音声)。
4. **公開mp3への取込み**: 公開`MonkeysPaw_a2_full.mp3`(48kHz、301.848秒=timeline総尺と一致)の同区間(±0.3秒窓)と`full_story_part1_c10.wav`の正規化相互相関最大値=**0.9993**(mp3符号化差のみ)。attempt2との相関0.054。
5. 公開ページ(`standard.html`/`index.html`)は同run(2026-10-24 18:42生成)由来で、上記mp3を参照(`audio_standard/MonkeysPaw_a2_full.mp3`、`a2_00..` 分割mp3)。

照合スクリプト: ad hocのpython(soundfile+scipy相互相関。本ファイルの手順どおり再現可。run dir・公開物は読み取りのみ)。

## 内容(聴感影響の見積り)
- 該当clipの本文: `…His friend warned. After their guest left, Herbert joked,`(原稿)。**音声は`visitor`**(Local Rewriteで`guest→visitor`に書換え、`audio_text_deviation`に記録済み。standard attemptはASRが`guests`と聞いた)。
- 4.7秒/301.8秒(約1.6%)。fallback Styleは「自然・明瞭・会話調」で、承認PD06(「一人の聞き手に語りかけ、温かさと微笑みのある声、落ち着いて安定した安心感、朝のラジオ番組ホストのように」)の質感とは異なる(Style脱落の聴感差は小さい可能性があるが、未聴取で断定しない)。
- 同runの他Std clipはすべてPD06一致(`a2`/`b1b`両levelのresultsでfallback_used=trueはこの1clipのみ、本調査で再集計。KP/日本語roleは本調査時点で実測未記録のため別途Gateで今後担保)。

## 選択肢(いずれも本委任では実施していない)
| 案 | 内容 | 費用/工数 | 備考 |
|---|---|---|---|
| A 現状維持 | 公開版をそのまま継続。Gate導入後の新規runから防止 | 0 | 1clip(約1.6%)のStyle脱落+`visitor`語が残る。品質基準(承認Styleを送ること)からの逸脱が公開物に1箇所残る |
| B 差替え | `--only-clips full_story_part1_c10`で当該clipのみ再生成(Std、最大3 attempt、承認PD06・Gateあり)→再組立→mp3/分割mp3/ページ再生成→公開更新 | 再生成¥1〜2(TTS+ASR)、再組立・公開更新は既存手順 | **公開物の差替えはユーザー判断**(`判断候補`)。再生成が再びfallbackに落ちた場合は新Gateが人間承認を要求(それもBLOCK対象)。 |
| C Human Reviewで承認 | 当該clipを聴いて許容するなら`human_approved_segments.json`に承認を記録(新Gateでも通る) | 0 | 承認の主体は人間のみ。未聴取で承認しない |

## 判断候補(Fableがユーザー判断化するか決める)
- **分類D(新しい判断)**: 公開済み猿の手Stdの当該clipを差替えるか(案A/B/C)。公開物の差替えは重要Scope/公開物変更のため、AI単独で実施しない。推奨=案B(約¥1〜2、公開更新を含む)をユーザーに提示。Gate導入で再発は止まるが、既存公開物は自動では直らない。
