# AUDIO_QA_01: Family Y 統合Trial Phase 3 音声Trialの実行結果と音声QA(FAMILY-Y-VOICES-DESIGN-01 委任_05)

実行: 2026-10-23 JST 12:35〜13:55(R2gとR0gを別processで並列、各1回起動、再起動0)。DEV/Trial経路のみ(`er110_family_y_audio_trial_01.py`)。TTS=`gemini-3.8-flash-lite-tts`(Flash-Lite、**Pro系TTSは不使用**: raw_usage_logの全gemini_batch呼出[R2g 38件・R0g 37件]が同モデル)。固定Voice=Algieba/Zephyr/Schedar(ユーザー決定)。出典=`er110_output/family_y_trial_01/audio/<r2|r0>/`(`raw_usage_log.jsonl`、`audio_qa_summary.json`、`{b1b,a2}/audit/`)。X/Z Production .py・Prompt・flag・閾値の変更0。

## 1. 結果の要約(事実)
| 候補 | レベル | 全segment(Preview/Comment1〜3/本文5/In One Line/KP) | 全編Assembly |
|---|---|---|---|
| R0g | Advanced | 全OK(ASR判定すべてPASS、再生成0) | **OK** 292.2秒 |
| R0g | Standard | 全OK(PASS。再生成: Comment2・人物1・人物2が各1回) | **OK** 303.2秒(人物の語りだけ減速なし版 297.1秒も作成) |
| R2g | Advanced | 本文5パート中**人物2(予算査定職員・Zephyr)だけSTOPPED**(§6)。他は全OK | **未作成**(Audio Validation Gate / Y style gateが拒否=人間確認待ち) |
| R2g | Standard | 全OK(PASS。PASS_WITH_WARNING 1件=人物3「wanna」) | **OK** 327.8秒(減速なし版 320.9秒) |

- 実費は2候補合計**29.10円**(R2g 14.70円[Gemini Batch 7.54/OpenAI ASR 4.09/Azure 3.05/LLM 0.03]、R0g 14.40円[6.72/3.53/4.11/0.04])。通算 146.28 + 29.10 = **175.38円 / 上限250円**。事前見積(20〜32円/候補、`audio/pre_run_estimate.json`)の約半分(Master Audio Storeの定型音声・KP英語の再利用、再生成が少なかったこと)。
- 使用モデル: TTS=gemini-3.8-flash-lite-tts(最新世代Flash-Lite、X/Zと同じ。Pro不使用=ユーザー指示)。ASR=X既定(gpt-4o-mini-transcribe主、Azure二次、KP英語はKP3Vで追加Whisper)。LLM呼出(Adv KP解説の文面生成等、X既定経路)=gpt-6-luna(R2g 1回・R0g 3回、合計0.07円)。25節の「最新最上位系」原則に対し、Xの音声段が使う既定モデルをそのまま継承(Trial専用に変更しない)。

## 2. 適用した検査 / 適用しなかった検査(列挙)
適用(X共有部品をそのまま呼出し、Y本文5segmentすべてに同じ経路): 3層ASR(Primary + Secondary Azure + 統一判定J7)・値ガード・否定差ガード・disfluency QA(In One Line)・**Repetition QA**(本文5segment)・Connected Speech/Local Rewrite対象(5segmentがFULL_STORYと解決される)・HR Lock(3試行上限・10分cool-down、回避なし)・Std 6%減速+減速後再ASR(本文5segment+In One Line)・Audio Validation Gate・KP source gate・Style profile M3 Gate(fx_20261017、Y版で本文5segmentに拡張)・KP3V(KP英語phrase)・Master Audio Store(Trial名前空間)・Secondary run scope(run単位cache+circuit breaker)・PASS_WITH_WARNING事後試聴リスト。
適用しなかった検査: ①er109(表記違い同音の同値判定層): scopeがX/Zのリテラルに固定(AST test)でYは非活性 ②PNAP(固有名詞アラーム方針): 同じくX/Z scope限定 ③`ensure_rf_record`(TTS直前のRF保険): Phase 2でRF実行済みのため再実行せず ④X共有のStd 6%減速未適用検知(`A2_SLOWDOWN_TARGET_SEGMENTS`=part1/2/in_one_lineのみ。OPEN-466): Yは自前で本文5segment+In One Lineの`slowdown_applied=True`を確認(全PASS) ⑤Comment 4(廃止、生成なし)。
Y側の追加確認(`y_style_gate`): X M3 Gateの結果から「Yに存在しないsegment(comment_4のNO_SEGMENT_RECORD)」だけを除外し、本文5segment(alias ID含む)に同じ判定(style_base_sha・最終style・minimal_fallback・fallback_used・Local Rewrite)を追加で掛けた。他の緩和なし。

## 3. 実装上の方式(事実)
- 本文segment ID: X共有検証部品がFULL_STORYと解決するalias(`full_story_part1`=リード、`part2`=人物1、`part3`=人物2、`part3_c2`=人物3、`part3_c3`=最終)。ZのPart内clip用の既存後方互換パターン(`full_story_part[1-3]_c[0-9]+`、er020)を利用。共有ファイル無変更。
- Voice切替: Xの本文生成関数(`generate_news_narration_wide_margin`/`generate_a2_segment_with_slowdown`)をそのまま呼び、`p9a.VOICE_NAME`をcontext managerで一時差替え(finallyで復元、test済み)。実際に使われたVoiceはraw_usage_logの`voice`欄で確認: R2g=Aoede 25/Algieba 2/Zephyr 4/Schedar 2/Charon 5、R0g=Aoede 24/Algieba 3/Zephyr 3/Schedar 2/Charon 5。Voice1〜3に誤ったVoiceが使われた呼出は0(各attempt metadataの`voice`も要求Voiceと一致、`audio_qa_summary.json` voice_evidence)。
- Voiceのstyle: PD06(Full Story style)をVoice1〜3にもそのまま適用(Std/Advともfx_20261017の既定)。
- **Master Audio Store**: Productionストア(`er006_output/master_audio_store_01`)のスナップショットをTrial dir(`audio/master_store_trial_<cand>`)へコピーし、process内で`er006_master_audio_store_01.STORE_DIR/AUDIO_DIR/MANIFEST_PATH/TELEMETRY_PATH`を差し替えた(`audio/<cand>/trial_store_info.json`)。新規生成分はTrial側にのみ保存され、Production storeへの書込み・reuse_key衝突は0。
- Voice同士・リード/最終・In One Line間の無音: Xの語り手切替pauseと同値0.8秒(`CHARON_TO_AOEDE_PAUSE_SECONDS`)。人物1→2→3の間にComment・効果音なし(testで順序固定)。

## 4. Voice別の実測(事実。F0は自己相関法の簡易推定で相対比較用)
各segmentの生成wav(Assembly前の個別音声)の実測。F0中央値=有声フレーム。F0幅=p10〜p90の半音数。重心=スペクトル重心(声の明るさの目安)。
| 候補 | レベル | パート | Voice | 長さ(秒) | 語数 | 話速(語/分) | F0中央値(Hz) | F0幅(半音) | 重心(Hz) |
|---|---|---|---|---|---|---|---|---|---|
| R2g | Advanced | リード(語り手) | Aoede | 21.73 | 68 | 187.8 | 177.8 | 9.93 | 2971 |
| R2g | Advanced | 人物1 教員(男性) | Algieba | 43.47 | 129 | 178.1 | 107.1 | 12.54 | 2774 |
| R2g | Advanced | 人物2 予算査定職員(女性) | Zephyr | 42.63 | 132 | 185.8 | 183.2 | 8.38 | 2506 |
| R2g | Advanced | 人物3 定時制の生徒(男性) | Schedar | 36.64 | 117 | 191.6 | 120.0 | 11.61 | 3489 |
| R2g | Advanced | 最終(語り手) | Aoede | 41.24 | 124 | 180.4 | 176.5 | 8.5 | 3228 |
| R2g | Advanced | In One Line | Aoede | 14.24 | 40 | 168.5 | 155.8 | 7.52 | 2721 |
| R2g | Standard | リード(語り手) | Aoede | 22.13 | 60 | 162.7 | 170.2 | 10.88 | 3002 |
| R2g | Standard | 人物1 教員(男性) | Algieba | 41.53 | 118 | 170.5 | 97.6 | 12.13 | 3099 |
| R2g | Standard | 人物2 予算査定職員(女性) | Zephyr | 42.33 | 119 | 168.7 | 171.4 | 8.77 | 2580 |
| R2g | Standard | 人物3 定時制の生徒(男性) | Schedar | 37.97 | 113 | 178.6 | 113.2 | 10.83 | 3695 |
| R2g | Standard | 最終(語り手) | Aoede | 42.94 | 126 | 176.1 | 171.4 | 8.88 | 3324 |
| R2g | Standard | In One Line | Aoede | 13.0 | 34 | 156.9 | 169.0 | 7.96 | 2692 |
| R0g | Advanced | リード(語り手) | Aoede | 19.11 | 50 | 157.0 | 177.8 | 9.33 | 3632 |
| R0g | Advanced | 人物1 教員(男性) | Algieba | 34.95 | 100 | 171.7 | 114.3 | 14.0 | 3094 |
| R0g | Advanced | 人物2 予算査定職員(女性) | Zephyr | 36.27 | 102 | 168.7 | 166.7 | 8.5 | 3013 |
| R0g | Advanced | 人物3 定時制の生徒(男性) | Schedar | 35.17 | 113 | 192.8 | 127.7 | 13.12 | 4020 |
| R0g | Advanced | 最終(語り手) | Aoede | 40.89 | 130 | 190.8 | 166.7 | 8.52 | 3442 |
| R0g | Advanced | In One Line | Aoede | 13.07 | 38 | 174.4 | 165.5 | 8.09 | 2768 |
| R0g | Standard | リード(語り手) | Aoede | 18.48 | 48 | 155.9 | 190.5 | 10.78 | 3088 |
| R0g | Standard | 人物1 教員(男性) | Algieba | 34.96 | 92 | 157.9 | 119.4 | 15.39 | 2855 |
| R0g | Standard | 人物2 予算査定職員(女性) | Zephyr | 38.18 | 104 | 163.5 | 166.7 | 9.12 | 3023 |
| R0g | Standard | 人物3 定時制の生徒(男性) | Schedar | 35.86 | 103 | 172.3 | 117.1 | 15.53 | 3662 |
| R0g | Standard | 最終(語り手) | Aoede | 36.82 | 113 | 184.1 | 160.0 | 10.23 | 3582 |
| R0g | Standard | In One Line | Aoede | 14.62 | 37 | 151.8 | 187.5 | 7.65 | 2846 |

読み取り(事実と所見を分ける):
- 事実: 男性Voice 2人(Algieba/Schedar)のF0中央値差は R2g Adv 12.9Hz(1.97半音)・R2g Std 15.6Hz(2.57半音)・R0g Adv 13.4Hz(1.92半音)・**R0g Std −2.3Hz(−0.34半音、差なし)**。スペクトル重心はSchedarが4条件すべてで高い(+596〜+926Hz)。話速もSchedarが速い(Adv 191.6〜192.8語/分 vs Algieba 171.7〜178.1、Std 172.3〜178.6 vs 157.9〜170.5)。
- 事実: 女性Voice(Zephyr)と男性Voice(Algieba)はF0中央値で5.8〜9.7半音離れる。Zephyrと語り手Aoede(F0約160〜190Hz)は同帯域でF0では近い(重心はZephyrが低め: Adv R2g 2506 vs 2971等)。
- 所見(数値上の聞き分けの材料): 男女の区別は明確。男性2人(教員/生徒)はF0だけでは近く、**重心(明るさ)と話速の差**が主な手掛かり。R0g Stdの2人はF0差が消えており、聞き分けは自己紹介文(場面)頼みになる可能性がある。実際に聞き分けられるかは**ユーザー試聴の評価項目(a)**(本資料は数値のみ、Sonnetは聴取判定をしていない)。固定割当(ユーザー決定)の変更は勝手に行っていない。

## 5. 長さ・Std「減速あり/なし」の差(事実)
| 候補 | Adv | Std(標準=全編約6%減速) | Std(人物1〜3の語りのみ減速なし) | 差 |
|---|---|---|---|---|
| R0g | 292.2秒(4分52秒) | 303.2秒 | 297.1秒 | −6.1秒(−2.0%) |
| R2g | 未作成(人間確認待ち。承認を疑似記録したscratch検証では308.4秒) | 327.8秒 | 320.9秒 | −6.9秒(−2.1%) |
- Voice part単体(Std): 減速後/減速前の長さ比は1.059〜1.060(全segment一定)。話速は例 R2g 人物1 170.5→180.7語/分(減速なし)。減速なし版は`<name>_original.wav`(減速前・生成時にASR検証済み)を人物1〜3だけに差し替えて組み立てた(TTS呼出0・追加費用0)。減速なし版の語りは減速後の再ASRを受けていない。
- X実績(直近3記事、同じAssembly規約): Std 278.8〜306.7秒、Adv 272.6〜286.0秒(`run_summary_assemble.json`)。YはR0g Std 303.2/Adv 292.2が範囲の上端〜やや超、R2g Std 327.8はX最大より+21秒(+7%)。語数(Y Std 460〜536語 vs X 385〜434語)の差と整合。
- 所見: 減速の差は全編で約2%(約6〜7秒)、Voice part単体では約6%。Zは会話の減速を撤去済み(OPEN-462)、Yは「独白」で会話ではない。**どちらが聞きやすいかはユーザー試聴で決める**(試聴ページに併置済み)。

## 6. R2g Advancedの停止(重要。原因・証跡・選択肢)
- 事実: R2g Advanced の人物2(`full_story_part3`、Zephyr、132語)が3回試行(attempt1〜3)ともASR判定はPASS(分類 NORMALIZED_MATCH → HIGH_SIMILARITY_SAFE → EXACT_MATCH、値ガード・否定差なし、長さOK)にもかかわらず、**Repetition QA(方式A: n-gram反復、OPEN-121)が3回とも`flagged`**(span「the cost of」が3.5〜3.7秒付近と11.0〜11.7秒付近の2回、`canonical_repeat_count=1`で『意図した反復』と判定されず)となり`verified=False`→STOPPED→HUMAN_REVIEW_REQUIRED(累計TTS 3回、10分cool-downを含む)。本文の他4パート・KP・Preview・Commentは全OK。
- 原因(仮説→根拠): 原稿に「the costs of managing devices」(60文字目)と「the cost of putting phones away」(191文字目)が離れて出る。Repetition QAの語レベル転写(local faster-whisper、small/int8)が前者の複数形「costs」を「cost」と書き起こし(span_textは全attemptで"the cost of")、canonical側は「costs」と「cost」で別tokenのためcount=1。→ 台本どおり読めているが、**単数/複数のASR揺れによるRepetition QAの偽陽性**(R0g Std 人物1のattempt1でもRepetition flagが出てattempt2で通過した、同系の挙動)。同じ原稿の再試行は同じ偽陽性を再現するため、再起動・再生成では解決しない(3試行は使い切り)。
- 証跡: `r2/b1b/audit/review_lock_state.json`(`full_story_part3`: HUMAN_REVIEW_REQUIRED)、`r2/b1b/narration/attempts/full_story_part3_attempt{1,2,3}_*.wav/json`(各attemptのrepetition_qa_evidence)、`r2/b1b/audit/y_style_profile_gate.json`(BLOCK: 当該segmentのみ)。
- 取り扱い(安全装置は回避していない): Gate・HR Lock・上限3回・Repetition QAの閾値に触れていない。Productionの偽陽性是正や原稿の再生成は本委任の範囲外(禁止事項)。人間承認(`record_human_approval`、聴取しPASSと判断した場合のみ)の後は**API 0で再組立できる**ことをscratch複製で確認済み(承認を疑似記録して`assemble_level`を実行→OK、308.4秒。scratchは削除済み、実際のR2g dirには承認を記録していない)。
- 選択肢(Fable判断): (A)ユーザーが試聴ページの当該take(「人間確認待ち」表示)を聴いて承認 → 再組立(API 0)してR2g Advを完成 (B)R2gはStandardのみで比較しAdvはR0gで評価 (C)R2g Adv人物2の英文を1箇所変える(例「the cost of」の言い換え)→再TTS(本文再生成禁止のため新規委任が必要、約1〜3円) (D)Production側の偽陽性是正(別案件、本Trialでは触れない)。推奨=(A)(実聴確認で承認ルールに合致し、追加費用0)。

## 7. ASR不一致・リトライ・PASS_WITH_WARNING(事実)
- R0g: Std Comment2(attempt1: 日本語の文字起こしが内容不一致[TRUE_CONTENT_MISMATCH]→attempt2 PHONETIC_MATCH合格)、Std 人物2(attempt1: 「add」→「have」・「used」→「use」の読み変え[TRUE_CONTENT_MISMATCH]→attempt2合格)、Std 人物1(attempt1: 「text」→「texts」HIGH_SIMILARITY + Repetition flag→attempt2合格)。Advは全segment attempt1で合格。
- R2g: Stdは全segment attempt1合格(PASS)。Advは人物2のみ上記STOP。
- PASS_WITH_WARNING(事後試聴リスト): R0g 0件。R2g Std 1件=人物3(Schedar)の「want to→wanna」(Secondary ASR確認、`SECONDARY_CONFIRMED`)。意味は同一でくだけた発音になった箇所(原稿は「want to」)。
- HR Lock: 本Trial全体で1件(R2g Adv 人物2)。

## 8. 一人称保持・5パート構造の音声での成立(事実の範囲)
- 事実: 5本文segmentすべてを原稿どおりのテキストで生成し、ASRが原稿と一致(上記PASS)。人物1〜3は英語原稿の一人称(I ...)、リード/最終は語り手のまま音声の台本として成立している。Assembly順序は Comment1→リード→Comment2→人物1→人物2→人物3→Comment3→最終→In One Line(`timeline.json`、testで固定)。人物間に効果音・Commentなし、境界の無音0.8秒。
- 未確認(音を聴かないと判断できない): 話者切替の明瞭さ・人物の聞き分け・PD06が人物の語りを平板化していないか(S9)は**ユーザー試聴(評価項目a〜d)**の対象。
