# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01 CURRENT_STATE_01(調査・API 0・Production変更0)

作成: 2026-10-30。基点=origin/main `bad0bda8c`(一時worktree)。ユーザー原文=`docs/pm/delegation_log/2026-10-30_FX4-LATTER-APPROVAL-AND-FLAP-T-TRIAL_USER.md`(origin/main `43c5144f7`で反映確認。本書は原文§3-§4に基づく)。
再現: 本書の数値は `tools/` の3 scriptをrepo rootで `.venv\Scripts\python.exe` 実行して得た(出力=同dirの `voice_census_01.json` `stored_census_01.json` `rescue_surface_01.json` `case_results_01.json`)。全てAPI 0・Production file無変更(census scriptはProduction telemetry追記をno-op化済み)。

## (a) 既存のASR判定・発音同等性救済機構の全体像

### a-1 判定の流れ(EN。vocab/KP英語=3-ASR多数決モード)
| 層 | 内容 | 位置(file:line) |
|---|---|---|
| 分類本体 | `classify_asr_match`=薄いwrapper(Tier1数値早期exit→`_classify_asr_match_core`→標準contraction展開) | `er006_preprod_hardening_01_validation.py:1360`(core :1148) |
| 1:1同音(`homophone_candidate`) | 単一語置換差で**CMU音素列(いずれかのvariant)完全一致**なら同音候補。差分生成時に付与 | 同 :821-846(`homophone_en.homophone_arpabet_equivalent`) |
| 同音のratioゲート迂回(B-2) | strict条件(canonical強勢読み1つ・ASR代表読み一致=P-01〜03) | 同 :1115、`er008_asr_variant_hardening_15_homophone_en.py:197`(`strict_homophone_pair`) |
| 多語同音(PNMH-01) | 1語と連続2〜3語のCMU音素連結一致 | 同 :834、CURRENT_SPEC.md:2956-2961 |
| Tier1(数値等)/Tier3 | `_tier1_atoms`/`tier1_numeric_equivalence`(5role限定)、Tier3=`determine_sub_reason`/`corroboration_supports`(独立ASRがdiff位置でcanonicalを支持) | `er021_en_asr_semantic_equivalence_production_01.py:508/758/865/854` |
| approved_equivalence | 最終ANDゲートが再否定しない基底=`HOMOPHONE_MATCH_NUMBER_EXCEPTION`/`TIER1_DIFF_ANCHORED`/`TIER1_NUMERIC_EQUIVALENCE`のみ(er109 ORTHO_BASISは**意図的に含めない**) | `er078_asr_unified_judge_01.py:73-77`、`er109_xz_scope_01.py:30` |
| Primary P-chain | Tier1→baseline→contraction→B1 CS→CS Equivalence層→Tier3→非ラテン→CMU alternate(`HOMOPHONE_EQUIVALENT`)→M1→**er109(X/Y/Z scopeのみ)** | `er006_secondary_asr_01.py:874`(`evaluate_attempt_with_cascade_detail`)、CS層 :981、Tier3 :1025、er109 :1135/:1207、`_step_alternate_pass` :665、PrimaryResult組立 :1169 |
| 統一judge | Primary PASS→最終ANDゲート(値DIFF/否定差)、Primary NG→P1保護差/P2除外/P3 Secondary(Azure)1回。`vote_required`(KP英語・vocab_extra_english)は OpenAI/Azure/**Whisper(local small)**の2/3多数決 | `er078_asr_unified_judge_01.py:25-30`(状態機械)、:542(vote_required)、`er104_kp_three_asr_vote_01.py:160`(`tally`)、:246(`_classify`)、:263(`make_voter`) |
| ASR系統 | Primary=OpenAI `gpt-4o-mini-transcribe`、Secondary=Azure、3票目=ローカル faster-whisper small(割れた時だけ) | `er006_asr_provider_routing_01.py:31`、`er104_kp_three_asr_vote_01.py:35` |

### a-2 既存の発音同等性救済の性質(Flap-Tとの関係)
- 既存1:1同音・er109・PNMHは**全てCMU辞書の音素列が一致すること**が根拠。`latter`=`L AE1 T ER0` と `ladder`=`L AE1 D ER0` は**辞書上は別音素**(T≠D)のため、どの層でも救済されない(実測: `.venv`でCMU直接確認、`case_results_01.json` P01)。
- **ASR収束は根拠にならない**(CURRENT_SPEC.md:1864「ASR consensus ≠ pronunciation verification」、同:1866)。FX4⑨の8判定が全て『Ladder』でも、それ自体は救済根拠にしない。根拠は音韻規則(CMU音素+flap環境)に置く。
- 既存**Connected Speech Equivalence Layer**(OPEN-122)にカテゴリF `flapping_intervocalic` があるが、(1)判定対象は『語末子音の脱落/place置換が次語頭と作る環境』のみで**語中のt<->d置換は対象外**(`er011_connected_speech_equivalence_layer_production_01.py:125-131`、`phoneme_prefix_drop`/`phoneme_final_place_substitution`)、(2)**独立ASRがcanonicalを支持**(corroboration>=1)しないとACCEPTしない(同 `classify_connected_speech_equivalence`)=latterは全ASRがLadderなので原理的に不成立、(3)適用範囲はA2/B1本文segmentのみ(同 冒頭)でKP/vocab英語には非適用。→ **既存機構の単純な拡張では届かず、新規ルール(語中flap層)が必要**。
- 再利用できる土台: er109(X/Y/Zのrun scope+単一flag読取関数+UKUS第2層が親flag従属で併設された前例)=`er109_xz_scope_01.py:92/100/149`、`er109_asr_orthographic_equivalence_01.py:45/657/733`。Flap層はUKUS層と同型の『第3層』として置くのが既存機構優先の最短経路(DESIGN_01 M1)。

### a-3 後段Gate・HRとの関係
- ASR長さ上限(max_len): 転写長で判定(`er078_asr_unified_judge_01.py` A3、`ctx.max_len`)。`latter`と`ladder`は同長で影響なし(vocab: length_ok=true 6字/上限16)。
- **Repetition QA方式A**: ASR転写の3語以上の反復spanのcanonical出現数を数える(`er011_open121_repetition_qa_production_01.py:582-634`)。flap語を含む3語以上のspanが台本で2回以上繰り返される場合のみ、ASR側`ladder`のspanがcanonical `latter`のspanと一致せず`canonical_repeat_count=0`となり偽NGになりうる(Å事案と同型)。適用はA2/B1本文のみ・発生はごく稀。**Flap層Production化の際の確認項目**(DESIGN_01 8節)。
- HR Lock: `er011_human_review_lock_01.py:475`(`approve_regenerate`)。Flapで救済された場合HRに入らない。FX4⑨の採用手順(`tools/fx4h_hr_adopt_meta_vocab3.py`)は並行作業で、本委任は触れない。
- 発音台帳(`er006_output/pronunciation_ledger_01/ledger.json`、`er006_pronunciation_ledger_01.py`): 固有名詞の発音情報cache(Perplexity)。**自動PASSの根拠にしない**(CURRENT_SPEC.md:1864(B))。Flap層とは独立。
- PHONETIC_MATCH(JA側): `er007_ja_secondary_asr_01.py:83/428`(JA読み一致)。言語が別でFlap-Tとは無関係(参考のみ)。

## (b) Voice実態

### b-1 設定・経路
- TTSは全てGemini prebuilt Voice(Voice名のみ指定)。`build_speech_config` が **`language_code=common.LANGUAGE_CODE`("en-us")** を送る=`er002_gemini_client.py:62-70`、`er002_common.py:53-55`(`MODEL_NAME="gemini-2.5-pro-preview-tts"`、`LANGUAGE_CODE="en-us"`)。flash-lite経路も同じ`gclient.build_speech_config`を使う(`er003_b1_p7a_audio.py:83-106`)。vocab英語=`gemini-3.8-flash-lite-tts`(`tts_backend: speech_metadata_flash_lite`、FX4⑨ attempt JSONで確認)。
- 既定Narrator Voice=Aoede(`er002_gemini_client.py:44`)。Z登場人物Voice=男性1 Algieba/2 Schedar/3 Fenrir/4 Orus/5 Puck・女性1 Zephyr/2 Kore/3 Leda/4 Sulafat/5 Erinome(CURRENT_SPEC.md:1566-1567)、Y候補=男性Puck/Schedar/Fenrir/Orus/Iapetus・女性同上(同:3147)。告げ口心臓Narrator=Fenrir(同:1569-1571)。Std/AdvでのVoice差は設定上なし(level差はmodel/styleのみ)。
- **英国英語等の非米音Voice/locale設定はEN本番経路に存在しない**(`en-GB/British/en-AU/en-IN`のGrep=`er003_audio_tts_asr_safety.py:256`の綴り正規化ルールと`er109_ukus*`のみ。TTS設定には0件)。
- ただし『設定が`en-us`』は**実音声が米音であることの証明ではない**(Geminiの`language_code`は指示でありVoice名と独立。実音声のflap/rhoticityはVoiceごとに未検証)。→ Voice別適用は『設定』ではなく『実音声での実証』で決める(DESIGN_01 4節)。

### b-2 保存attempt記録のVoice実績(`voice_census_01.json`。5,189 attempt record/5,302 file、unreadable 0)
EN attempt数(Family列は保存path由来。`other`=A/B/C/Trial/research):
| Voice | X | Y | Z | other |
|---|---|---|---|---|
| Aoede | 885 | 148 | 715 | 950 |
| Charon | 268 | 37 | 145 | 290 |
| Algieba | 0 | 48 | 136 | 70 |
| Schedar | 0 | 17 | 44 | 16 |
| Zephyr | 0 | 22 | 73 | 26 |
| Fenrir | 0 | 0 | 39 | 2 |
| Orus | 0 | 0 | 21 | 5 |
| Puck | 0 | 5 | 13 | 0 |
| Kore | 0 | 0 | 28 | 3 |
| Erinome | 0 | 0 | 28 | 35 |
| Leda | 0 | 0 | 0 | 2 |

model/backend内訳: `gemini-3.8-flash-lite-tts`(speech_metadata_flash_lite)2,306、`gemini-2.5-pro-preview-tts`(標準)1,665、同(structured_separation)79、flash-lite(backend記録なし)21。Voice名は11種(Sulafat・Iapetusは記録0件)。**全てGemini prebuilt Voice**、locale記録はattempt JSONに無い(config側のみ)。

### b-3 実音声での米音性(flap)確認方法案
1. **既存記録の実証(完了・API 0)**: 『canonicalはt綴り語、全ASRがd綴り語』の実例を、attempt JSONの`voice`/`model`に結び付けた(`stored_census_01.json` RESCUE_examples+各`narration/attempts/*.json`)。**flap実証済みVoice=3種**: Aoede(latter→Ladder、flash-lite、FX4⑨ vocab)、Zephyr(Bertie→Birdie、2.5-pro、FZ The Open Window `full_story_part1_c14`)、Schedar(Bertie→Birdie、2.5-pro、同 `full_story_part3_c2`)。**未実証=Charon・Algieba・Fenrir・Orus・Puck・Kore・Erinome・Leda(記録なし)・Sulafat・Iapetus**。『flapの記録なし』は英国音の証拠ではなく『該当語が未出現』=未確認として扱う(未確認Voiceを米音と決めつけない)。
2. **Voice probe(DESIGN_01 6節Phase 2。有料・Cap案≤¥30)**: 各Voiceにflap対象語(latter/metal/betting/atom/Bertie/petal等)を単語発話させ、OpenAI+Azureの転写でd綴り語の出現率を測る。d綴り転写が出れば当該Voiceはflap実証、全てt綴りなら『crisp-t(非flap)または単にASRが文脈なしで正しく書いただけ』=不適用のまま。
3. rhoticity(語末R)は転写綴りに現れないため本Trialの判定対象外。目的は『このVoiceでflap同等性救済を許可するか』の根拠に限定し、Voiceを米音と断定する用途ではない。

## (c) 過去NG記録の集計(`stored_census_01.json`)
母集団: 全`*tts_generation_results*.json` 421 file(本文/KP/**vocab_extra.v3**/各fallback attempts_log・Azure転写含む再帰走査)+全`human_review_queue*.jsonl`のsteps。転写 6,951件・うち保存NG 1,516件・現行コードでも不合格 1,330件。distinct segment 4,949、うち STOPPED/HR 131(X 17・Y 7・Z 7・other(A/B/C等)100)。
Flap-T規則(`tools/flapt_equivalence_proto_01.py`)を『現行でもNGの転写』に適用:

| 判定 | 行数 | distinct(canonical,転写) | Family | 経路 | 語 |
|---|---|---|---|---|---|
| RESCUE(自動救済) | 13 | 7 | X 4・Z 9 | vocab英語 4・本文 9 | latter→ladder 4(FX4⑨ vocab_extra_english、OpenAI+Azure x 2 attempt分。**STOPPED=HR**) / bertie→birdie 9(Z The Open Window `full_story_part1_c14`・`part3_c2`、a2/b1b。いずれも**最終的にOK**=リトライで通過) |
| REQUIRES_EXTRA_EVIDENCE(AY/AW) | 1 | 1 | other | 本文 | title→tidal(AKB48 b1b。自動救済しない) |
| t/d差だが救済せず(`td_diff_declined`) | 80 | - | - | - | canonical複数読み 42(its/it等・putting型含む)・音素同一(既存homophone層担当)22・CMU未登録 10・音素長相違 4・語頭語末 1・t/d以外の子音差 1 |

(注: 同一attemptがresults側とnarration/attempts側の両経路で拾われる場合があり『行数』はattempt x 系統の概数。重複を除いた比較にはdistinct列を使う。)
見込み(根拠=上表):
- **HR削減**: 保存済みSTOPPED/HR 131 segmentのうちFlap-Tで救済可能は**1**(X FX4⑨ latter。Xに限れば17件中1件)。過去全体では小さい(0.8%)が、**⑨Advは現にこれ1件でBLOCKされている**ので当該記事の完成には直結する。今後のvocab英語(latter型の語)でも再発しうる構造的な穴。
- **再生成(リトライ)削減**: Z The Open Windowの4 segmentで『Bertie→Birdie』によりNGとなった**9 attempt**が、Flap-T救済があれば初回で通過し得た(上限見積)。attemptあたり費用の金額換算は未算出(cost telemetry突合は委任_02)。
- **量産単価**: API 0(CMU辞書のみ、追加ASR/LLM呼出なし)。救済は再生成TTS/ASRとHR工数の削減側に働き、単価増はない。
- 注意: 母集団には旧run(A/B/C等)を含む。旧コード由来の過大計上は『現行コードでも不合格』で除いた。HR queue jsonlには今回の対象(flap)が0件(古い記録中心)。
