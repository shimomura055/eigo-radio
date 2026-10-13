# MELOS_12TAKE_RESULT_01 (ASR-PHONETIC-EQUIVALENCE-MELOS-12TAKE-RESULT-01 委任_01)

既存転写・既存wavのみ使用(新規TTS/ASR/LLM API 0、費用JPY0)。VALIDATED/REJECTED判定・Production採用判断なし。

## 1. 12件の構成と出所
- 出所: `er069_output/attribution_clip_split_trial_01/results_02.json`(FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_02)の Melos x `said` 12行。canonical=`Melos said.`、TTS Aoede、wavは`gen02/wav/`に12本全て実在。
- 構成: 4 take(t1-t4)x 3条件(Standard減速前=raw / Standard減速後=slow6 / Advanced=raw)=12観測=12本の別wav(減速後は同take減速前wavの時間伸長で別ファイル)。
- 従来方式のPASS定義: OR = OpenAI転写を`evaluate_attempt`(Production)で判定してPASS、またはAzure転写(Phrase List=[Melos]あり)を`classify_asr_match`(Production)で判定してPASS、のいずれか。
- 従来 engine別: OpenAI単独 PASS 0/12、Azure(PLあり)単独 PASS 4/12、OR PASS 4/12(results_summary_02.mdの値と一致)。
- 改訂M1(V1') = `er068_...offline.py`の`design_judge`(ASR転写に対し同音/音素正規化 `m1_try`[F1ガード・ALLOWED_VARIANT_CLASSES・所有格正規化込み]を適用し、Production判定へ流す)。各engineの転写ごとに適用し、同じOR定義で集計。判定は role gating `full_story_part1`、Tier3(Azure再確認)除外のread-only再計算。従来判定の再計算値は記録値と全12件で整合(従来PASSは同じ4件)。
- V2'(末尾暫定ゲート付き)は参考として別列(wavから`tail_integrity`を算出、12/12算出可)。

## 2. 表1

| 判定 | 従来方式 | 改訂M1(V1') | (参考)V2'末尾ゲート付き |
|---|---|---|---|
| PASS | 4/12 | 12/12 | 10/12 |
| 非PASS | 8/12 | 0/12 | 2/12 |

engine別PASS: 従来 OpenAI 0/12・Azure 4/12 / M1 OpenAI 11/12・Azure 12/12。

注意: これは『判定のPASS/非PASS』であり、音声が実際に`Melos`と正しく発音されているかの正解ではない(4節)。

## 3. 表2(12件全行)

| # | Take | レベル | OpenAI転写 | Azure転写(PLあり) | 従来(OA/Az/OR) | M1(OA/Az/OR) | V2' OR | M1変化理由 | 音声の正否 客観確認 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Melos_said_L2_std_t1 | Standard減速前 | `Mello said.` | `Mellow said.` | 非PASS/非PASS/非PASS | PASS/PASS/PASS | 非PASS(tail -25.97dB SUSPECT) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: `Mellow said.`中の`mellow`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`mellow said`) |
| 2 | Melos_said_L2_std_t2 | Standard減速前 | `Mello said.` | `Mellow said.` | 非PASS/非PASS/非PASS | PASS/PASS/PASS | PASS(tail -49.25dB OK) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: `Mellow said.`中の`mellow`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`Mellow said.`) |
| 3 | Melos_said_L2_std_t3 | Standard減速前 | `Mello said.` | `Melos said.` | 非PASS/PASS/PASS | PASS/PASS/PASS | PASS(tail -48.15dB OK) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: 従来からEXACT(変化なし) | 未確認(聴感・音響正解なし。参考: Whisper-small=`Melo said.`) |
| 4 | Melos_said_L2_std_t4 | Standard減速前 | `Mello said,` | `Melo said.` | 非PASS/PASS/PASS | PASS/PASS/PASS | PASS(tail -52.07dB OK) | OA: `Mello said,`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: 従来からPROD_PASS_UNCHANGED(変化なし) | 未確認(聴感・音響正解なし。参考: Whisper-small=`Melo said`) |
| 5 | Melos_said_L2_std_t1 | Standard減速後 | `Mellow said.` | `Mellow said. ` | 非PASS/非PASS/非PASS | PASS/PASS/PASS | 非PASS(tail -25.73dB SUSPECT) | OA: `Mellow said.`中の`mellow`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: `Mellow said.`中の`mellow`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`mellow said`) |
| 6 | Melos_said_L2_std_t2 | Standard減速後 | `Mello said.` | `Mellow said.` | 非PASS/非PASS/非PASS | PASS/PASS/PASS | PASS(tail -47.81dB OK) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: `Mellow said.`中の`mellow`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`Mellow said.`) |
| 7 | Melos_said_L2_std_t3 | Standard減速後 | `Mello said.` | `Melos said. ` | 非PASS/PASS/PASS | PASS/PASS/PASS | PASS(tail -48.45dB OK) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: 従来からEXACT(変化なし) | 未確認(聴感・音響正解なし。参考: Whisper-small=`Mellow said.`) |
| 8 | Melos_said_L2_std_t4 | Standard減速後 | `Mello said,` | `Mellow said.` | 非PASS/非PASS/非PASS | PASS/PASS/PASS | PASS(tail -51.69dB OK) | OA: `Mello said,`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: `Mellow said.`中の`mellow`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`Mello said`) |
| 9 | Melos_said_L2_adv_t1 | Advanced | `Mello said.` | `Mellow said.` | 非PASS/非PASS/非PASS | PASS/PASS/PASS | PASS(tail -46.64dB OK) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: `Mellow said.`中の`mellow`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`Mello said.`) |
| 10 | Melos_said_L2_adv_t2 | Advanced | `Mello said.` | `Mello said.` | 非PASS/非PASS/非PASS | PASS/PASS/PASS | PASS(tail -47.95dB OK) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`Mellow said.`) |
| 11 | Melos_said_L2_adv_t3 | Advanced | `Mella said.` | `Mello said.` | 非PASS/非PASS/非PASS | 非PASS/PASS/PASS | PASS(tail -60.67dB OK) | OA: `Mella said.`は音素説明不能(DEFER_NOT_EXPLAINED)で変化なし; Az: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept | 未確認(聴感・音響正解なし。参考: Whisper-small=`Melo said.`) |
| 12 | Melos_said_L2_adv_t4 | Advanced | `Mello said.` | `Melos said.` | 非PASS/PASS/PASS | PASS/PASS/PASS | PASS(tail -58.3dB OK) | OA: `Mello said.`中の`mello`を`melo`へスペル近似(oov_spelling_fallback)で正規化→Production CONNECTED_SPEECH_ACCEPTでaccept; Az: 従来からEXACT(変化なし) | 未確認(聴感・音響正解なし。参考: Whisper-small=`Mello said.`) |

Azure Phrase Listなし条件の転写(参考、従来PASSは1/12): t1/Standard=`Mellow said.`; t2/Standard=`Mellow said.`; t3/Standard=`Mellos said.`; t4/Standard=`Melo said.`; t1/Standard=`Mellow said.`; t2/Standard=`Mellow said.`; t3/Standard=`Mello said.`; t4/Standard=`Mellow said.`; t1/Advanced=`Mellow said.`; t2/Advanced=`Mello said.`; t3/Advanced=`Mello said.`; t4/Advanced=`Mellow said.`

## 4. 真値(聴感・音響正解)の有無
- `er069_output/attribution_clip_split_trial_01/`配下に聴感ラベル・人間verdictは無い(`trial_conclusion_01/02.md`に『聴感評価は未実施』と明記)。`er065_output/short_clip_asr_context_trial_01/`の音響指標も本12wavには無い。
- よって12本が実際に`Melos`(語末の/s/を含む)と発音されているかは**客観的に未確認**。**真の誤判定率は未確定**。
- 従来PASS 4/12は『転写がMelos/Meloとして通った』結果、M1 PASS 12/12(OA11+Az12のOR)は『転写の綴り揺れ`Mello/Mellow`を`Melo`に寄せ、Production既存の連結発音ルール(CONNECTED_SPEECH_ACCEPT)で受理した』結果で、どちらも音声の正解ではない。
- 観察事実(判断なし): 12件の転写はほぼ全て`Mello/Mellow/Melo`で語末`s`が転写されない(`Melos/Mellos`はAzure 2件のみ)。M1の置換は全てspelling fallback(`Melos`がCMU辞書OOVのため)で、『音素一致』ではなく綴り近似による受理であり、語末`s`欠落(発音が`Melo said`の可能性)と区別できない。Std t1のraw/slow6のみ末尾ゲートSUSPECT(-26dB)。

## 5. 比較不能件数
0件(12/12を同一条件=同一転写・同一OR定義で比較済み)。不足データは真値のみ(上記)。
## 6. 費用
JPY0(API呼出0)。
