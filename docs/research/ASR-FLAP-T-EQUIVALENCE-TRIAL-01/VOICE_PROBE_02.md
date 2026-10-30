# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_02 Phase 2: Voice probe(実音声。Trial専用・Production変更0)

実施: 2026-10-30。ユーザー原文§3.3(Voice確認)の実測。生データ=`voice_probe_02.json`(clip sha・model・voice・設定・3系統転写・分類)、`probe_02/results.jsonl`+`probe_02b/results.jsonl`(clip単位の原記録、2 shard)、`probe_02*/cost_log.jsonl`(Gemini token実測)。実装=`tools/flapt_voice_probe_02.py`(Production leaf `er003_b1_p9a_audio.generate_narration_snippet` + `gclient.voice_override` を呼ぶだけ。Production file無変更)、集計=`tools/flapt_probe_analyze_02.py`(API 0)。clip wavはcommitしない(shaで同定、`probe_02*/wav/`はローカルのみ)。

## 1. 条件(Production経路との同一性)
- TTS設定: `language_code="en-us"`(`er002_gemini_client.py:62-70`)、Voiceは `voice_override` で送信値を置換(`er002_gemini_client.py:54`の`effective_voice`、attempt記録`voice_sent`で確認)。出力はProductionの `trim_english_keyword_silence` 済み。
- model経路は実使用の組合せ(`voice_census_01.json`): `fl`=`gemini-3.8-flash-lite-tts`+`speech_metadata_flash_lite`(style=`FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"]`="brief and clear"。X/Y/Zのflash-lite使用Voice: Aoede/Charon/Algieba/Puck/Schedar/Zephyr/Fenrir)、`pro`=`gemini-2.5-pro-preview-tts`+`ENGLISH_STYLE_PREFIX`(Z等の2.5-pro使用Voice: Orus/Kore/Erinome/Sulafat/Leda/Iapetus)。実行はStandard同期(`TTS_EXECUTION_MODE=STANDARD`。Production既定のBatchと同一model・同一speech_config)。
- ASR 3系統=Production同一関数: OpenAI `gpt-4o-mini-transcribe`(`er006_asr_provider_routing_01.transcribe`)/Azure(`er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list`、phrase list無)/ローカルWhisper small(`er104_kp_three_asr_vote_01.whisper_transcribe`)。
- 項目12語: latter, metal, betting, atom, waiting, coating, water, writer, little, better, city, "the latter one"(語単体11+短文脈1)。d綴り対応語があり「d綴り転写=flap実証」が可視化できる**観測項目は7**(latter, metal, betting, atom, waiting, coating, the latter one)。残り5語は対照(water/little/better/city はd綴り対応語なし、writer=AY核)。
- 判定(`flapt_equivalence_proto_01.evaluate`でAPI 0分類): `FLAP_D`=d綴り語へ転写(例 latter→Ladder)/`EXACT`=t綴り一致/`OTHER`/`EMPTY`。Voice判定: ≥2観測項目で**≥2系統**がFLAP_D=`FLAP_DEMONSTRATED`、d綴りが全く無くt綴り完全一致が≥5/7=`T_SPELLED`、他=`INDETERMINATE`。
- 較正: Aoede(flash-lite)の `latter`→OpenAI/Azure/Whisperすべて「Ladder」で、FX4⑨本番失敗(attempt 4件x 2系統すべてLadder)と**同じ現象を再現**した(`probe_02/results.jsonl`の`Aoede|fl|latter|normal`)。

## 2. 結果(clip数 通常155+減速版36。TTS失敗0)
Voice|path別(`voice_probe_02.json`の`voices`)。flap観測語=≥2系統がd綴り、d綴り出現語=≥1系統がd綴り。

| Voice\|path | clips | flap観測語(>=2系統) | d綴り出現語(>=1系統) | t綴り一致語 | 判定 | 保存記録の実証 |
|---|---|---|---|---|---|---|
| Aoede\|fl | 12 | latter, betting, atom, coating | 同左 | 3/7 | FLAP_DEMONSTRATED | FX4 latter(flash-lite) |
| Charon\|fl | 12 | betting, atom, coating | latter, betting, atom, coating | 4/7 | FLAP_DEMONSTRATED | - |
| Algieba\|fl | 12 | latter, atom | latter, atom, coating | 5/7 | FLAP_DEMONSTRATED | - |
| Puck\|fl | 12 | latter, atom, coating | 同左 | 4/7 | FLAP_DEMONSTRATED | - |
| Schedar\|fl | 12 | latter, atom, coating | latter, betting, atom, coating | 4/7 | FLAP_DEMONSTRATED | (Schedar\|pro: FZ Bertie) |
| Zephyr\|fl | 12 | latter, atom, coating | latter, betting, atom, coating | 4/7 | FLAP_DEMONSTRATED | (Zephyr\|pro: FZ Bertie) |
| Fenrir\|fl | 12 | atom, coating | latter, metal, betting, atom, coating | 4/7 | FLAP_DEMONSTRATED | - |
| Orus\|pro | 12 | atom, coating | latter, atom, coating | 2/7 | FLAP_DEMONSTRATED | - |
| Kore\|pro | 12 | latter, atom, coating | 同左 | 2/7 | FLAP_DEMONSTRATED | - |
| Erinome\|pro | 12 | latter, betting, atom, coating | 同左 | 3/7 | FLAP_DEMONSTRATED | - |
| Sulafat\|pro | 12 | latter, atom, coating | 同左 | 3/7 | FLAP_DEMONSTRATED | - |
| Leda\|pro | 12 | latter, betting, atom, coating | 同左 | 1/7 | FLAP_DEMONSTRATED | - |
| Iapetus\|pro | **9**(Cap停止) | latter, betting, atom | 同左 | 2/7 | FLAP_DEMONSTRATED | - |
| Zephyr\|pro | 2(較正のみ) | latter | latter | 1/7 | INDETERMINATE(clip不足) | FZ Bertie→Birdie |

- **T_SPELLED(t綴りのみ=flapが弱い/米音でない可能性)と判定されたVoice x path: 0件。** 試験した13組合せはいずれも複数語・複数系統でd綴り転写が出た。非rhoticの兆候(語末-erが母音終わりで転写される)も全clipで0(`nonrhotic_hint_count`=0。ただし綴りは語末Rの実音を反映しにくいので**補助観察のみ**で米音/英音の断定には使わない)。
- 減速版(Std 6%=`er008_a2_postprocess_slowdown_01.apply_a2_slowdown(6.0)`。既存wavにatempo後ASRのみ、TTS再生成なし): Aoede/Schedar/Zephyr(fl)すべてflap維持(d綴り出現語集合が通常と同一[latter, betting, atom, coating]、≥2系統の観測語数はAoede 4→2、Schedar 3→3、Zephyr 3→3。Aoedeは1系統が無音/空転写[`azure=EMPTY`]の揺らぎによる)。減速によるflap消失は観測されなかった。生成時の「slightly slower」指示文の効果は未測定(post-processのみ検証)。
- AY核 `writer`: 13組合せ 39転写のうち「Rider」は**1件**(Algieba|fl OpenAI。同clipのAzure/WhisperはWriter)、33件が Writer、残り5件はTTS側の崩れ・空転写(Kore「rayer/rarer」3、Orus OpenAI「ライター」、Leda Azure空)。ASRは writer/rider を**通常は区別している**=『ASRが常に同じ語に倒れて区別不能』は実証されず→AY/AW核を自動救済しない方針(DESIGN_01 I-5)を維持(M2'の結論=非救済)。
- 副次観察: 単語単体clipのTTSは時々語自体を崩す(例 Orus|pro metal→「Ne/No.」、Kore|pro betting→「Telling」、Leda|pro metal→「Nettle」)。flapとは別事象で`OTHER`に分類され、Voice判定は他の観測語で行った。

## 3. Voice許可リスト案(実証ベース。単位=(Voice, TTS path)。`voice_probe_02.json`の`allowlist_proposal`)
許可(probeでFLAP_DEMONSTRATED、または保存記録で実証): `Aoede|fl, Charon|fl, Algieba|fl, Puck|fl, Schedar|fl, Zephyr|fl, Fenrir|fl, Orus|pro, Kore|pro, Erinome|pro, Sulafat|pro, Leda|pro, Iapetus|pro, Schedar|pro, Zephyr|pro`(後2者は保存記録[FZ Bertie→Birdie]由来)。
**不適用(未確認=fail-closed)**: 上記に無い組合せ全て。Z本番で実使用される `Algieba|pro, Charon|pro, Puck|pro, Fenrir|pro, Aoede|pro, Kore|flash-lite` 等は**未probe**のため現時点では不適用(追加probeで拡張可。1組合せ約¥0.1〜0.26/12 clip)。Voice不明(attempt_ctxに`voice`/modelが無い)も不適用(`flapt_equivalence_proto_01.voice_applicable`、test済)。

## 4. 限界・注意(断定しないこと)
1. 「d綴りで転写された」はflap音の存在を強く示すが、**米国英語の証明ではない**(ASRの語彙prior・文脈無し条件の影響を排除できない)。したがって許可リストは『Flap層を適用してよいVoice』の根拠(=このVoiceでASRがd綴りに倒れる実害が実在する)であり、Voiceのアクセントを断定する用途ではない。本probeの結果は、全13組合せで『d綴り転写が実際に起こり得る』=Flap層が必要な場面が全Voiceで再現しうる、と読む。
2. 判定は1 clip/項目(各Voiceで12 clip)。揺らぎ(同一Voiceでも項目により t/d 綴りが割れる)があるため『Voice単位の確率』は出していない。
3. Iapetus|proは `better, city, "the latter one"` の3 clip(想定 約¥0.8)がCapにより未実行(件数を減らして継続せずCapで停止した)。観測項目では「the latter one」のみ未取得で、判定には影響しない(観測6項目中3項目でflap観測)。
4. Whisperは3票目(割れた時だけ使われる)。probeでは全clipで取得したため系統別の出現を比較できる。

## 5. 費用(実測)
Gemini TTS: Production cost logger(`er005_cost_logger`)のtoken実測x公式単価(`er005_output/cost_baseline_01/pricing_snapshot.json`)。ASR: Azure=ceil(秒)x$1/h x160円、OpenAI=秒x$0.003/min x160円(概算。Whisperはローカル¥0)。
| shard | TTS | ASR | 計 | 内訳 |
|---|---|---|---|---|
| probe_02(fl 7 Voice 84 clip+減速版36[ASRのみ]+較正4) | ¥6.139 | ¥6.049 | **¥12.188** | |
| probe_02b(pro 6 Voice 69 clip) | ¥13.788 | ¥3.665 | **¥17.453** | 約¥0.25/clip |
| **合計** | ¥19.927 | ¥9.714 | **約¥29.64**(Cap ¥30固定の範囲内。Cap引上げなし) | |
単価確定(実行前): flash-lite 約¥0.10/clip(TTS 0.05+ASR 0.05)、2.5-pro 約¥0.26/clip(TTS 0.21+ASR 0.05)、減速版ASRのみ 約¥0.05/clip。13組合せx12 clip+減速36+較正の見積≒¥30.3は上限超過見込みのため、Iapetusの末尾3 clip(約¥0.8)を**実行しない**判断をした(件数削減ではなくCap厳守の停止。実行前に確認した単価=較正4 clipの実測)。
運用: 2 shard並列(別out-dir)。proc1(fl)は計画どおりFenrir完了後に自PIDで終了、proc2(pro)はIapetus 9 clip目でCap監視(自PIDのkill)により終了。launchは4回(21:00:46較正、21:02:35本番fl、21:06:55本番pro[別shard]、21:19:03 Aoede減速版補完[既存wavのASRのみ・約¥0.1])。300秒窓内の最大は2回で、storm guardの発動なし・再起動なし。ただし**較正と本番flの起動間隔は109秒で、指示の『≥150秒間隔』を41秒下回った**(自己申告。いずれも別目的の新規launchで、同一runの再起動ではない)。
