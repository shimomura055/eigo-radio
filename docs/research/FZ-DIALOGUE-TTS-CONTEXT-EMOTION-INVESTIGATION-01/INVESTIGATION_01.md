# INVESTIGATION_01 — Family Z セリフTTSの文脈・感情表現 read-only調査(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01 委任_01)

- 原文: `docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01_USER.md`。委任文: 同 `_DELEGATION_01.md`。逐語証跡: `EVIDENCE_01.md`(同ディレクトリ)。
- 範囲: read-only。API 0円、Production/Prompt/flag/Seed変更0、新規TTS 0、Trial 0。新仕様の採用提案は含まない(選択肢の比較のみ。採用はユーザー判断)。
- 記述ごとのタグ: [確認済み: path] = 実ファイル/コード/実行記録で確認。[推測] = 推論(未確認)。
- 注記(重要): 実際にTTSへ送ったprompt全文は**どこにも保存されていない**(EVIDENCE_01 §0)。style部のsha256が実行時記録と一致することを確認した上でProduction関数から再構成した。聴感は未評価(AI側に聴取手段なし)=**人手試聴必要**。

## 1. 結論(PM向け)

**現行ProductionのセリフTTSは、前後の会話・場面・登場人物の感情を把握していない。** TTSモデルに渡るのは「そのセリフ1件の英文(引用符つき)」と「全セリフ共通の汎用スタイル文」だけで、直前直後のセリフ・地の文・話者の感情・場面の情報は**一切入力されない**(渡していない)。感情の制御機構も存在せず、Voiceの割当(性別・年齢イメージ)は感情制御ではない。感情らしい抑揚は、セリフ本文の語彙と句読点(`!`・`?`)からTTSモデルが局所的に推測した結果に依存する。[確認済み: EVIDENCE_01 §0-§4]

影響度(会話の自然さ): 設計上の限界は確実にある(A=いいえ)。ただし**実害の大きさは作品と場面による**。
- セリフが本文に占める語数の割合: Open Window 約49%、After Twenty Years 約49%、Monkey's Paw 約24-27%、Melos 約19-20%、Gift of the Magi 約13-16%、Tell-Tale Heart ほぼ0%。[確認済み: 各作品の`segment_plan_{b1b,a2}.json`語数集計]
- 現行成果物は、少なくとも『開いた窓』はユーザー最終試聴PASS(REGISTER #157、2026-10-23)、Monkey's PawもCLOSED_USER_PASS([確認済み: `docs/pm/ACTIVE_TASK.md`])。つまり「必要十分な品質」の判定は現行方式のままでPASSの実績がある。これは本調査が現行品質を不合格とする根拠が無いことも意味する。
- 一方、Gift of the Magiは原文要件が「DellaとJimの会話で感情が伝わることを重視」(`docs/pm/delegation_log/2026-10-24_FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01_USER.md:41`)だが、その達成手段は**Voice選定のみ**で、生成時の感情伝達は検証されていない[確認済み: 上記+本調査]。「ささやき」「涙ながらの笑顔」のような演出が、演出情報を持つ地の文(別clip・別Voice)とは分離されたセリフclipに反映される根拠は無い。機械指標(EVIDENCE_01 §2)では例1の「ささやき」は反映されていない可能性が高いが、**確証はユーザー試聴待ち**。
- 英語学習ラジオとしての評価軸(語の聞き取りやすさ・意味の理解)に対しては、ASR Gateが「正しい語が読まれたか」を担保しており重大な欠陥は確認されていない(例1-3すべてPASS)。影響するのは主に**物語としての臨場感・会話の自然さ**(学習効果より、聴き味の品質)。

## 2. TTSへ渡す情報の一覧(ユーザー原文 §2①)

Z正式経路のdialogue clip 1件=Gemini TTS 1 call(model `gemini-2.5-pro-preview-tts`、Voice=話者別固定)。

| 項目 | 渡している? | 根拠 |
|---|---|---|
| 当該セリフの英文 | **渡している**(引用符`"…"`つき。`tts_safe_news_en`整形後) | [確認済み: `er063_family_z_audio_01.py:815-818, 853-865`, `er012_b_family_voices_production_01.py:519-520`] |
| 話者・Voice ID | **渡している**(speech configのvoice名のみ。話者名「Della」等のテキストはpromptに入らない) | [確認済み: `er012_b…:519 make_batch_tts_call_fn(model, voice_name)`; `…/the_gift_of_the_magi/run_sf_prod_01/voice_assignment.json`; prompt再構成=EVIDENCE_01 §1にDellaの名前は無い] |
| Dialogue Style / TTS Prompt | **渡している**(ただし**全dialogue clip共通の汎用文**。物語ナレーション用の文で、セリフ専用ではない) | [確認済み: `style.effective_style_prefix_sha256=add26d27…`が`er002_common.build_style_prefix()`と一致、EVIDENCE_01 §0-§1; 方針根拠 `CURRENT_SPEC.md:1612`「従来Dialogue Style」] |
| 直前・直後のセリフ | **渡していない** | [確認済み: EVIDENCE_01 §1(TEXT TO SPEAK=1セリフのみ)、`er063:1743-1760`は音声ファイル連結のみでTTS入力に使わない] |
| 地の文・場面の状況 | **渡していない**(地の文は別clip・別Voice[Aoede]で別API呼出) | [確認済み: `segment_plan_b1b.json`のclip分割、`er062_family_z_structure_01.py:851-866 build_flat_chunks`/`er013_family_c_production_01.py:_build_base_segments`(voice境界で必ず分割)] |
| 登場人物の感情・心理状態 | **渡していない**(どの段階にも感情フィールドが無い) | [確認済み: `segment_plan_*.json`のclipキー=id/part/voice/speaker/voice_role/text/…にemotion系キー無し] |
| 会話全体の流れ | **渡していない** | 同上。styleに「story arc」の文言はあるが物語内容は渡らない |
| 当該セリフ以外の文章 | **渡していない**(style文の説明テキスト以外、他のセリフ・地の文は0) | [確認済み: EVIDENCE_01 §1] |

補足: 話者の決定は別段(LLM `FAMILY_Z_DIALOGUE_ATTRIBUTION`+決定論照合、`er063:467-484`)で、結果はVoice割当にのみ使われ、感情には使われない。

## 3. 感情表現の仕組み(ユーザー原文 §2②)

**結論: 感情・語調の個別制御は存在しない。** 以下すべて「制御なし」。唯一の間接要素は、セリフ本文の語彙・句読点とstyle文の汎用指示。

| 表現 | 制御 | 内容 |
|---|---|---|
| 怒り/恐怖/喜び/悲しみ | **制御なし** | emotion値・演出タグ・話者の心理フィールドは仕様に無い。モデルがセリフ本文の語・`!`から推測するのみ[確認済み: コードにemotion系入力なし(Grep: `er063`/`er012_b`/`er062`で`emotion|感情|tone`のproduction入力経路0)、style文に感情語指定なし] |
| 驚き/ためらい/皮肉 | **制御なし** | 「ためらい」は台本のダッシュ(`really will—`)や`,`の有無が唯一の手掛かり。皮肉は本文の語義のみ |
| 問いかけ・返答 | **制御なし** | 直前発話を渡さないため、返答の間・食い気味・声の調子は決まらない。clip間の無音は組立で固定(dialogue後0.2秒、narrator後0.5秒)[確認済み: `er013_family_c_production_runner_01.py:665-670`] |
| 同一人物の場面による感情変化 | **制御なし** | 各clipが独立API呼出で同一style。連続性は保証されない(EVIDENCE_01 §4) |
| Voice割当 | 感情制御ではない | `voice_assignment.json`の性別プール(male/female)からの決定論的割当・固定Voice。Voice選定時に感情を考慮するのはVoice**選択段**(ユーザー意図)であって、生成時の制御ではない[確認済み: `docs/pm/delegation_log/…GIFT-OF-THE-MAGI…_USER.md:41`、`er062_family_z_structure_01.py:105-144 assign_dialogue_voices`] |

付随の事実([確認済み]):
- style文は「complete storyをTTSせよ」「Treat the narration as one continuous program」等、**ナレーション用の長文**をそのまま1セリフに適用している(由来=Family B Voices本文用の`ENGLISH_STYLE_PREFIX`。`er012_b_family_voices_production_01.py:520`の既定)。「Do not … exaggerate feelings that are not present in the script」により、台本(=1セリフ)に表れない感情は**抑制方向**の指示になっている。
- Gate(ASR一致・値/否定ガード・Repetition QA)は語の一致を見るもので、**感情・抑揚は検査対象外**。ASRテキストの句読点(例: `How terrible,`→ASR`How terrible!`)から読み取れる程度。
- 最終組立は各clipを個別にtarget RMSへgainする(`er063:1764-1770 gs`、`er013_…runner_01.py:663-664`)ため、「小声=低音量」等の音量差による表現は最終音声でほぼ平準化される[確認済みコード]。
- 監査ラベルの軽微な不整合: `FAMILY_Z_ROLE_STYLE["DIALOGUE_STD"].style_label`が`…+post6%`のままだが、速度仕様v2(2026-10-23)でStd会話の後処理6%減速は撤去済み(実際は`speed_profile=std_dialogue_none`)。表示ラベルのみで挙動への影響なし[確認済み: `er063:211-214` vs `tts_generation_results.json`]。分類=実害なし。

## 4. セリフの分割・生成・組立(ユーザー原文 §2③)

| 項目 | 現行 | 根拠 |
|---|---|---|
| 分割単位 | 引用符区間(`QUOTE_RE`)と地の文で分割、voiceが変わる箇所で必ずclip境界。同一voiceの連続はclip結合、語数目安超過時のみ段落境界で分割 | [確認済み: `er062_family_z_structure_01.py:851-866`, `er013_family_c_production_01.py:_build_base_segments/_apply_word_guideline_splits`] |
| 同じ話者の連続セリフ | **仕様上は隣接していれば結合される**が、実作品では**結合されたclipは0件**(話者タグ「said Vera」等の地の文が必ず間に入るため)。複数引用/複数段落にまたがるdialogue clip=0 | [確認済み: 全作品のsegment_planの統計、EVIDENCE_01 §5] |
| 別場面の同一Voiceセリフ | **個別生成**(clipごとに独立API呼出。場面・part・同一話者を問わず) | [確認済み: `er063:1303 run_tts_stage`がclip単位、`tts_generation_results.json`のclip別attempts] |
| TTS生成時の文脈 vs 組立時の前後関係 | 生成時: 文脈なし。組立時: `build_family_c_episode_sequence`が`clip順`にwavを連結し、dialogue後0.2秒/narrator後0.5秒の無音を挿入、各clipを個別gain。前後関係は**ここで初めて作られる**が、それは「並べる」だけで感情の調整ではない | [確認済み: `er063:1722-1742`, `er013_family_c_production_runner_01.py:616-678`] |
| retry/再生成時の入力 | **同一**(retry時も同じstyle+同じ1セリフ。minimal_fallbackは感情指示がさらに減る方向だが、全415 dialogue記録で使用0件)。文脈や感情は増えない | [確認済み: `er012_b…:518-541`、EVIDENCE_01 §5] |
| 最大試行 | 通算3回(`PRODUCTION_MAX_TTS_ATTEMPTS=3`)+高速化後ASR再検証のouter loop(Adv) | [確認済み: `er011_human_review_lock_01.py:80`, `er063:853-865`] |

## 5. 現行方式の問題と影響範囲

問題([確認済み]の事実から導く設計上の限界。実際の聴感影響の大小は**人手試聴必要**):
1. 返答・掛け合いの調子(質問と返答の間、驚き、被せ)がTTS側で作れない。テンポは組立で固定0.2秒。
2. 演出情報(「she whispered」「voice grew quieter」)は別clip・別Voiceにあるため、セリフ本体の声色・音量に反映されない。音量差はさらに組立のgainで平準化。
3. 同一人物の感情の連続性・変化が担保されない(独立生成)。短いセリフ(≤3語: Adv 16件/Std 5件)ほど文脈なしの影響が大きいと推測[推測]。
4. styleがナレーション向けの汎用文で、セリフらしい口語・演技の指示ではない。かつ「台本に表れない感情を足すな」と抑制。
5. 品質Gateに感情・抑揚の検査が無い。劣化があってもASR PASSで素通りし、人手試聴でしか気づけない。

影響範囲:
- 対象=Family Zのdialogue clip(Adv 73/Std 69件、6作品)。Family B Voices本文(`generate_voice_body_wide_margin`の共用)も同一styleだが、本調査の範囲外(Z開発のみ=27-7)。
- 影響が大きいのはセリフ比率の高い作品(Open Window/After Twenty Years約49%、Monkey's Paw約25%)。ただし現時点で重大NG・ユーザー不合格の記録は確認していない[確認済み: ACTIVE_TASK等]。

## 6. 評価(ユーザー原文 §3 A〜D)

**A. 現行方式のままで前後の会話・感情を反映できる設計か → できない(設計上)。** 入力に前後文脈も感情情報も無く、反映の経路が存在しない。例外は、セリフ本文そのものに含まれる語・句読点を手掛かりにしたモデルの局所推測のみ(F0が190→304Hz等で変動した実測[確認済み: EVIDENCE_01 §4]はこの範囲の現れ。ただし場面の感情と対応する保証は無い)。

**B. 反映できている場合、どの情報によるか →** 反映と呼べるのは「セリフ本文の語彙・`!`/`?`/ダッシュ」と、汎用styleの『台本の意味に従った感情の弧』『表情豊かに』という包括指示のみ。場面・相手・直前直後・感情情報によるものは**無い**。

**C. 反映できていない理由 →** (1)1 clip=1 API call、他の文章を入力しない設計(clip分割がvoice境界必須)。(2)styleがdialogue専用でなく、感情・文脈の欄が無い。(3)演出情報がnarrator clipにあり別Voice・別callに隔離。(4)retryも同一入力。(5)組立で一律の無音・個別gain。(6)Gateは語一致のみ。いずれも設計上の帰結で、不具合ではない(Z Voice正式表・Dialogue Style・速度仕様v2と矛盾しない。`CURRENT_SPEC.md:1612`が「従来Dialogue Style」を明記)。

**D. 同一Voiceのセリフを一括生成して後から分割する方式は有効か →** 部分的に有効だが、これだけでは文脈・感情の問題は解決しない。

| | 内容 |
|---|---|
| 効果(見込み)[推測] | 同一Voiceの声質・テンション・息づかいの連続性(例: Della全6セリフの音色の一貫)。極短文(≤3語)が単独callで不安定になる現象の緩和(同種の短clip問題は既知[確認済み: OPEN-222(narrator flash-lite)、SHORT-CLIP-SPEED-GATE-01])。呼出回数・styleトークンの削減(1作品の入力は元々約0.45k token/call×約9-17callで微小)。 |
| 限界 | (1)渡る文脈は「同じVoiceの他のセリフ」だけで、**相手の発言・地の文(演出)は入らない**。掛け合い・返答の問題は未解決。(2)別場面(別part)のセリフを一括すると、場面の感情差を無視して一続きに読む恐れ。(3)境界の復元(分割)が必要。(4)再生成の単位が一括全体に拡大(1セリフのASR NGで全体を撮り直し=費用・時間増、HR Lockの単位も変わる)。(5)Gate(ASR一致)は分割後の各clipに掛け直す必要。 |
| 既存機構の再利用 | ①`er113_fx_paragraph_chunk_trial_01.py:472 measure_alignment`(faster-whisper word timestamps+difflib整列で台本単位の発話区間・境界gapを実音声から計測。DEV/Trial専用の計測実装[確認済み])=分割位置の推定に流用できる可能性。ただしローカルWhisperのProduction導入は不採用の既存決定がある(`CURRENT_SPEC.md:2836`、ASR3W UDR #136。ASR判定器としての不採用であり分割用途の扱いは**未決**)。②`build_tts_prompt`のStructured Separation(`er003_b1_p4c_audio.py:78-100`)=STYLE区画に文脈を置き、TEXT区画だけ読ませる既存機構で、文脈注入先として使える。③Gemini TTS `multi_speaker_voice_config`はSDKに存在するが([確認済み: `er003_output/b1_p3v/A01/capability/tts_capability_report.md:17`])Productionでは未使用・Trial実績なし。④組立(`build_family_c_episode_sequence`)・gain・ASR Gate・Review Lock keyはclip単位のwavを前提としており、分割後wavなら再利用可。⑤FZ-NARRATION-CHUNK-TTS-TRIAL-01(OPEN-510、並行)は**地の文の分割**でdialogue境界は維持する方針[確認済み: `docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_USER.md:15,55`]=本件と独立(同時に実装・Trialを進めるなら衝突に注意)。 |
| 実装上の落とし穴[確認済み] | `build_reuse_key`の`style_prefix_sha256`はdialogueでNone(`er063:738-750`)。dialogueのstyle/入力文脈を変えてもreuse_keyが変わらず、**保存済み旧音声が再利用される**(`reused_from_previous_run`、EVIDENCE_01 §2/§3の実例)。文脈注入を行うならreuse_keyへ文脈/styleのhashを含める変更が必須。 |

## 7. 改善が必要な場合の選択肢とQCD比較(採用判断はユーザー。以下は比較のみ)

見積の前提: 1 dialogue callの実トークン(Magi Adv b1b): 入力約450 token・出力約71 token(音声)。`gemini-2.5-pro-preview-tts` Standard=入力$1/M・出力$20/M(`er005_output/cost_baseline_01/pricing_snapshot.json`)→1 call約$0.0019≈0.28円(為替150円/$は[推測])。Magi Adv 8 clip≒約2.5円。作品あたりdialogue費用は数円規模で、**Cはほぼ影響しない**(Q中心の判断)。

| 案 | 内容 | 品質見込み(Q)[推測] | 量産単価増分(C)[推測] | 処理時間(D) | 実装規模 | リスク |
|---|---|---|---|---|---|---|
| (1) 現状維持 | 変更なし | 現行どおり(ユーザーPASS実績あり)。会話の臨場感の上限は低いまま | 0 | 0 | 0 | Magiのように感情が主題の作品で聴き味が弱い可能性(試聴で確認) |
| (2) clip単位のまま、style(STYLE区画)に「話者の感情/場面ヒント+直前直後1〜2セリフ+地の文の演出語(whispered等)」を注入 | 1セリフ=1 callは不変。文脈は`TEXT TO SPEAK`の外(Structured Separation)に置く | 中〜高(返答・演出語が入る。抑揚の向上が期待できるが、モデルがどこまで従うかはTrial未実施=不明) | 入力+約100〜300 token/call≒+0.05円/call未満。感情ヒントをLLMで作るなら+数円/作品(gpt-6.x 1 call、推定) | 変化小(LLM 1 call+生成は同数) | 中(新しいdialogue用style関数+文脈組立+reuse_key拡張+DefaultOffIsolation。Z専用新関数経由で既存Prompt直接編集なし) | 文脈語の読み上げ漏れ(leakage)=ASR Gateで捕捉可だがretry増。音量はgainで平準化されるため効果が限定的。Production Prompt/仕様の意味変更=ユーザー承認+Opus条件A要 |
| (3) 同一話者の連続セリフを1 clipにまとめる | 現行も隣接時は結合。実作品で結合対象0件 | ほぼ変化なし | 0 | 0 | 小 | 効果が出る箇所が無い(地の文が間に入るため)。単独では無意味 |
| (4a) 同一Voiceの全セリフ(場面/part単位)を1 callで一括生成→ASR整列で分割 | 声質・感情の弧の連続性を得る | 中(文脈は同一話者のセリフのみ。返答・演出は不足) | callと入力は減る。再生成単位拡大で最悪ケース費用↑ | 分割処理(ASR整列)+ASR Gate再実行で時間↑ | 大(分割位置推定・境界trim・wav再構成・HR Lock/ASR判定単位の再設計) | 分割誤り、再生成単位の増大、HR Lock単位変更、別場面の感情混濁。ASR3W不採用との整合要確認 |
| (4b) 場面(質問↔返答)をmulti-speaker 1 callで一括生成→分割 | 掛け合いの自然さが最も高い可能性 | 高い可能性(ただし未検証) | 出力トークンは同等で入力は減。再生成単位拡大 | 分割+Gate | 大(multi-speaker API未使用、話者数上限・Voice割当との整合、narrator[Aoede]との接続) | **未使用API**。Voice割当仕様(話者別固定Voice)・3人以上の場面・地の文との接続が未検証。新仕様=ユーザー承認+Trial要 |
| (5) narrator+dialogue全体を1 callで一括生成 | 最も自然 | Voice別割当仕様と矛盾(ユーザー承認済みDialogue別Voice)=仕様変更が前提 | — | — | 大 | 承認済み仕様の変更になるため本調査の対象外。候補としてのみ記載 |

推奨(採用はユーザー判断): **(1)のまま、まず人手試聴で現行の聴き味を確認**(0円。Magi Adv `part2_c7`/`part3_c4`/`part3_c6`と『開いた窓』`part1_c4→c5`の4-5本、EVIDENCE_01末尾のwav)。聴いて「問題あり」と判断された場合のみ、**(2)を第1候補の小規模Trial**(Magi+Open Windowの代表clip、現行vs注入の各2 take、概算64 call≒約18円・上限30円目安[推測])から開始し、効果が不足する場合のみ(4b)をTrial候補とする。(3)は効果が出る箇所が無いため非推奨。(4a)は(2)と(4b)の中間だが実装規模が大きい割に文脈が弱く、優先度は低い。改善Trial・Production変更は本調査の範囲外=別途ユーザー判断(委任文の指示どおり)。

## 8. 過去Trial・仕様との照合(21節)

- 「セリフ前後文脈をTTSへ渡す」「感情タグ」「一括生成→分割」が**過去に検討・不採用になった記録は確認できなかった**。`DECISION_LOG.md`/`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`docs/research/FAMILY-Z-*`/`FAMILY-Y-*`のGrep(感情タグ/emotion tag/前後文脈/前後のセリフ/文脈をTTS/一括生成.*分割)で該当なし。近縁: (a)ER-003-B1-P3V(2026-08、`er003_output/b1_p3v/A01/ER-003-B1-P3V_stop_report.md`)=TTS APIにbreak/SSML/mark/timestampが無いと判定し、無音挿入制御の方式(句読点・ASR・最長無音)へは戻らず停止した[確認済み]。「一括生成→分割」を無音/ASRで行う道は、その時点で別目的(pause制御)として検討・停止しており、**本件の目的での再検討は未実施**。(b)FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01=感情文を含む短文でVoice**選定**をしたのみ(`TRIAL_DESIGN_01.md:19`)で、生成時の文脈注入ではない。(c)`CURRENT_SPEC.md:2076`「前後文脈のない短いフレーズは専用の最小限instructionで生成」(短文narration用)=文脈なし生成が既知の限界として扱われてきた記録。(d)FX-PARAGRAPH-CHUNK(OPEN-506)=逆方向(長いpartを段落chunkへ)。
- 承認済み仕様との矛盾: 無し。現行のdialogue挙動はCURRENT_SPEC.md:1612・1629-1630・1699と整合(「従来Dialogue Style」「Voice別」)。本調査で見つけた不整合は上記の監査ラベル1件(実害なし)のみ。
- 既存のretry/Gate/HR Lock/Master Audio Storeはいずれも変更していない。
