# SELECTION_02 — 追加2作品とセリフの選定(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_04、2026-10-26、API 0)

- 依頼: `docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_USER_02.md` §2(対象作品の選定はClaudeに委任・選定理由を記録)。
- **結論: 追加2作品 = 『開いた窓』(The Open Window)と『猿の手』(The Monkey's Paw)。各作品 Advanced(b1b)のセリフ8件、計16件。**
- 機械可読版: `er118_output/fz_dialogue_context_tts_trial_02/{open_window,monkeys_paw}/phase0/selection.json`(`py er118_fz_dialogue_context_tts_trial_01.py --work <key> plan` で再生成可、API 0)。
- 範囲: Round 1と同じく Advanced の dialogue clip だけ。Std(a2)は文面がAdvの言い換えでカテゴリが重複するため使わない。

## 1. ユーザー原文§2の要件と選定への反映

| 原文§2の要件 | 反映 |
|---|---|
| Family Zの既存作品から追加2作品、既存の確定本文・Voiceを利用 | Production完走・公開済みの `run_sf_prod_01`(Adv=b1b)の `segment_plan_b1b.json`・`voice_assignment.json` をそのまま使用(編集なし) |
| 感情変化・緊張・驚き・怒り・不安・喜びなど文脈が音声表現に影響しそうなセリフ優先 | 開いた窓=不安/緊張・同情・静かな語り・喜び・落ち着いた嘘・日常対照、猿の手=警告・喜び・期待と半信半疑・重い知らせ・悲嘆・恐れ・震え声・事務的対照。**怒りの明示は両作品のAdv地の文に無い**(猿の手の警告が最も近い)ため、怒りの網羅は残る限界 |
| 各作品6〜10セリフ、極端に短いセリフばかりにしない | 各8件。語数4語以上を主体(各作品6件以上)、2語以下は開いた窓1件(`part1_c10` 2語)・猿の手0件。1語セリフ(Jimmy!/Herbert!/Wait!)は不採用 |
| 感情・場面が異なる複数、特定の感情に偏らせない | 各作品に、方向あり5・過剰演技の監視2・安定監視(対照)1を置き、感情種別を分散(下表) |
| 選定理由を記録 | 本書 §2〜§4 |

追加の選定規則(Round 1の構造に合わせる。TTS観測前に固定): **各作品=方向あり5(地の文の手がかり語から主指標と期待方向を事前登録) + 過剰演技の監視2 + 安定監視1(感情・演出の明記なし)**。安定監視clipは、Round 1で2語clip(Madame `Twenty dollars.`)の±20%監視が不成立だった教訓から**6語以上**に限定(開いた窓9語・猿の手13語)。

## 2. 候補作品の比較(不選定理由を含む)

OPEN-511のセリフ比率と本委任で `segment_plan_b1b.json` / `tts_generation_results.json` を直接読んだ事実。

| 作品 | Adv dialogue clip | ①(Production既存clip)の再利用 | 地の文の演出手がかり | 判定 |
|---|---|---|---|---|
| **開いた窓** | 17件(約49%)、話者4(Vera=Zephyr/Framton=Algieba/Vera's aunt=Kore/men=Schedar) | 全clipに原音wav・attempt json・ASR判定(asr_judgement)あり。選定8件は全て state=PASS | 豊富(`murmured`/`hurried into the room`/`her face brightened`/`Vera's voice grew quieter`/`Vera said calmly`/`stared`) | **選定** |
| **猿の手** | 17件(約25%)、話者5(元軍曹=Algieba/Mr. White=Schedar/Herbert=Fenrir/男=Orus/Mrs. White=Zephyr) | 同上。選定8件は全て state=PASS(`part3_c1`のみProduction側で2 attempt、採用原音はattempt2と一致) | 中程度(`Herbert laughed`/`with a smile`/`Her face was wet with tears`/`He turned away`/`His voice shook`)。感情の幅(喜び・警告・悲嘆・恐れ・震え)が最大 | **選定** |
| 賢者の贈り物 | 8件 | — | — | Round 1で使用済みのため対象外(3作品横断の1作品目として比較) |
| After Twenty Years | 19件(約49%) | **`tts_generation_results.json` に `asr_judgement` が無く(19件全てNone)、①のASR判定を新2作品・Round 1と同一形式で照合できない** | 乏しい(`smiled`/`hurried`/`stared`程度) | 不選定。加えて最終セリフが54語(費用大)・1語/3語セリフ多数。2作品で多様性が足りるため追加調査はしない |
| Melos | 11件(約20%) | 最終runが `run_sf_prod_01` 配置でなく別run dirに分かれ、①の参照pathの確定に追加調査が要る(**本委任では未精査**) | 未確認 | 不選定(2作品で足りるため。必要なら別委任) |
| Tell-Tale Heart | 1件(2語、約0%) | — | — | 対象外(セリフがほぼ無い) |

## 3. 不採用にした個別セリフの主な理由(選定した2作品内)

- **ASR記録に難がある**: 開いた窓 `part1_c14`(27語、Productionでattempt 8まで要し最終は PASS_WITH_WARNING[SECONDARY_ASR_CORROBORATED_MATCH]、`Bertie`が`Birdie`と転写される)、`part3_c2`(`Bertie, why do you bound?`、同じ理由で PASS_WITH_WARNING)。新armで再試行が連発して費用を押し上げ、条件(a)(ASR PASS)を固有名詞の転写ゆれで失う恐れがあるため外した(`part3_c2` はもともと過剰演技の監視で、`part1_c12` に差し替え)。
- **前後の地の文が別人の動作を手がかり語として拾う(manner_words汚染)**: 開いた窓 `part2_c2`(直後地の文`her aunt hurried`が`hurried`として混入)、猿の手 `part1_c11`(直後地の文`Herbert laughed`が`laughed`として混入)。抽出規則はRound 1から無変更のため、汚染が出る対象は外した。猿の手 `part1_c15`(`smile`と直後の`cried`が混在)は**混在を承知で方向ありに採用**(DESIGN_02 §6)。
- **極短・中立**: 1語(`Jimmy!` `Herbert!` `Wait!`)、2語(`All three.` `Burn it,`)、3語(`He is dead.` `He's our son!`)は計測が不安定/感情の読み取りが文脈だけでは弱いため外した。
- **費用が大きい**: 開いた窓 `part1_c9`(41語)。

## 4. 選定結果(16件)

役割の凡例: **方向あり**=地の文の手がかり語に対応する主指標と期待方向を事前登録(`PREREGISTERED_CRITERIA_02` §5の対応則。DESIGN_02 §3)/**過剰演技の監視**=方向なし、②両takeのF0幅>1.5×max(①,base)なら過剰演技疑い/**安定監視(対照)**=②両takeが①・baseの範囲±20%内か。

### 作品: 開いた窓(The Open Window) — work key `open_window` / Adv(b1b) / 出典 `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/segment_plan_b1b.json`

| # | clip_id | 話者(Voice) | 語数 | ①原音(秒) | 役割 | 想定感情・場面 | 前後の文脈(決定論抽出) |
|---|---|---|---|---|---|---|---|
| 1 | `part1_c7` | vera (Zephyr) | 8 | 4.24 | 過剰演技の監視 | 不安・緊張・静かな告白: 客のFramtonに、Veraが叔母の『悲劇』を切り出す場面。Veraは開け放たれたフランス窓を見やってから話し始める。 | 前セリフ[Vera:part1_c4 / Framton:part1_c5] 後セリフ[Vera:part1_c9] 直前地の文「he admitted. Vera glanced towards the French window, which stood wide open to the lawn.」 直後地の文「Framton stopped turning the letter.」 manner=stopped |
| 2 | `part1_c10` | framton (Algieba) | 2 | 1.84 | 方向あり → 揃える前RMS↓ | 驚き・同情・ささやき・静かな発言: 窓の外へ出て行方不明になった叔母の家族の話を聞き、Framtonが小声で『なんと恐ろしい』とつぶやく場面(地の文に『murmured』)。 | 前セリフ[Vera:part1_c7 / Vera:part1_c9] 後セリフ[Vera:part1_c12] 直前地の文「なし」 直後地の文「Framton murmured.」 manner=なし |
| 3 | `part1_c12` | vera (Zephyr) | 17 | 6.17 | 過剰演技の監視 | 不気味さ・悲しみ・静かな語り: Framtonがつぶやいた後、Veraが『叔母は今もみんなが帰ってくると思っていて、暗くなるまで窓を開けて待っている』と静かに続ける場面(直後の地の文に『Vera's voice grew quieter』)。 | 前セリフ[Vera:part1_c9 / Framton:part1_c10] 後セリフ[Vera:part1_c14] 直前地の文「Framton murmured.」 直後地の文「Vera's voice grew quieter.」 manner=なし |
| 4 | `part2_c4` | mrs_sappleton (Kore) | 33 | 12.09 | 方向あり → 調音話速↑ | 喜び・驚き・感情が変化する場面: 叔母が急いで部屋に入ってきて、Framtonに話しかけ、開けた窓のこと、もうすぐ帰る夫と弟たちのことをにこやかに話す場面(直前の地の文に『hurried into the room』)。 | 前セリフ[Vera:part1_c14 / Vera:part2_c2] 後セリフ[なし] 直前地の文「Before Framton could reply, her aunt hurried into the room.」 直後地の文「Framton felt a chill. So she really was waiting.」 manner=hurried |
| 5 | `part2_c6` | mrs_sappleton (Kore) | 5 | 2.53 | 方向あり → F0中央値↑ | 喜び・驚き: 窓の外を気にしていた叔母の顔がぱっと明るくなり、『やっと帰ってきた』と声を上げる場面(直前の地の文に『her face brightened』)。 | 前セリフ[なし] 後セリフ[なし] 直前地の文「Again and again, she looked past him towards the lawn. Then her face brightened.」 直後地の文「Vera stared outside, her eyes wide with horror. Framton turned.」 manner=stared |
| 6 | `part3_c8` | mrs_sappleton (Kore) | 9 | 4.69 | 安定監視(対照) | 戸惑い・日常の会話(対照): 逃げるように帰った客のことを、叔母が帰宅した家族に『神経の話をしたかと思ったら急に走って行った』と何気なく話す場面。 | 前セリフ[one of the returning men:part3_c4 / Vera's aunt:part3_c6] 後セリフ[Vera:part3_c9] 直前地の文「his wife said.」 直後地の文「なし」 manner=なし |
| 7 | `part3_c9` | vera (Zephyr) | 4 | 2.17 | 方向あり → 調音話速↓ | 落ち着いた嘘・相手の発言を受けた返答: 客が逃げた理由を問われ、Veraが落ち着いて『犬のせい』と答える場面(直後の地の文に『Vera said calmly』)。 | 前セリフ[Vera's aunt:part3_c6 / Vera's aunt:part3_c8] 後セリフ[Vera:part3_c11] 直前地の文「なし」 直後地の文「Vera said calmly.」 manner=なし |
| 8 | `part3_c11` | vera (Zephyr) | 29 | 11.76 | 方向あり → 調音話速↓ | 落ち着いた嘘・作り話の語り: 逃げた客について、Veraが落ち着いたまま、インドで犬の群れに追われ墓穴で一晩過ごしたという作り話をすらすらと語る場面(直前の地の文に『Vera said calmly』、直後の地の文でそれが作り話だと明かされる)。 | 前セリフ[Vera's aunt:part3_c8 / Vera:part3_c9] 後セリフ[なし] 直前地の文「Vera said calmly.」 直後地の文「Inventing convincing stories at a moment's notice was Vera's speciality.」 manner=なし |

セリフ本文(英):
1. `part1_c7` "Her great tragedy happened three years ago today."
2. `part1_c10` "How terrible,"
3. `part1_c12` "My aunt still thinks they'll come back. She keeps the window open until dark, waiting for them."
4. `part2_c4` "I hope Vera has kept you company! You don't mind the open window? My husband and brothers will be back soon. They've been shooting. Their boots will be covered in mud, of course!"
5. `part2_c6` "Here they are at last!"
6. `part3_c8` "He talked about his nerves, then suddenly ran away."
7. `part3_c9` "It was the spaniel,"
8. `part3_c11` "He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the whole night there, with them snarling above him."

### 作品: 猿の手(The Monkey's Paw) — work key `monkeys_paw` / Adv(b1b) / 出典 `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/segment_plan_b1b.json`

| # | clip_id | 話者(Voice) | 語数 | ①原音(秒) | 役割 | 想定感情・場面 | 前後の文脈(決定論抽出) |
|---|---|---|---|---|---|---|---|
| 1 | `part1_c4` | morris (Algieba) | 9 | 4.33 | 過剰演技の監視 | 不吉な警告・静かな語り: 元軍曹が暖炉のそばで猿の手の由来を語り、『運命に手を出す者には悲しみをもたらす』と続ける場面。 | 前セリフ[the retired sergeant-major:part1_c2] 後セリフ[Mr. White:part1_c5] 直前地の文「he said,」 直後地の文「なし」 manner=なし |
| 2 | `part1_c13` | herbert (Fenrir) | 12 | 4.65 | 方向あり → F0中央値↑ | 喜び・冗談めかした提案: 訪問者が帰ったあと、Herbertが笑いながら、父に『200ポンドを願って家のローンを払おう』と促す場面(直前の地の文に『Herbert laughed』)。 | 前セリフ[the retired sergeant-major:part1_c9 / the retired sergeant-major:part1_c11] 後セリフ[Mr. White:part1_c15] 直前地の文「After their visitor left, Herbert laughed.」 直後地の文「Mr. White raised the paw with a smile.」 manner=laughed,smile |
| 3 | `part1_c15` | mr_white (Schedar) | 6 | 3.53 | 方向あり → F0中央値↑ | 期待と半信半疑・願い事: Mr. Whiteが微笑みながら猿の手を掲げ、『200ポンドが欲しい』と願う場面(直前の地の文に『with a smile』、直後に手がねじれて叫ぶ)。 | 前セリフ[the retired sergeant-major:part1_c11 / Herbert:part1_c13] 後セリフ[なし] 直前地の文「Mr. White raised the paw with a smile.」 直後地の文「It twisted in his hand. He cried out and dropped it.」 manner=cried,smile |
| 4 | `part2_c2` | visitor (Orus) | 7 | 2.41 | 過剰演技の監視 | 悲しみ・重い知らせ: 工場から来た見知らぬ男が、Whiteさん夫妻に息子の事故を切り出す場面。 | 前セリフ[なし] 後セリフ[the stranger from the firm:part2_c4] 直前地の文「White cleared the table. Later, a stranger from the firm arrived.」 直後地の文「he said.」 manner=なし |
| 5 | `part2_c6` | visitor (Orus) | 13 | 6.22 | 安定監視(対照) | 事務的な発言(対照): 息子の死を告げたあと、会社は責任を負わないが見舞金として200ポンドを出すと、男が事務的に伝える場面。 | 前セリフ[the stranger from the firm:part2_c2 / the stranger from the firm:part2_c4] 後セリフ[Mrs. White:part2_c8] 直前地の文「Mr. White reached for his wife's hand.」 直後地の文「Mr. White fell from his chair.」 manner=なし |
| 6 | `part2_c8` | mrs_white (Zephyr) | 11 | 5.32 | 方向あり → 調音話速↓ | 悲しみ・必死の頼み・感情が変化する場面: 埋葬の1週間後、涙で顔を濡らしたMrs. Whiteが夫を揺り起こし、猿の手に残った願いで息子を生き返らせてと迫る場面(直前の地の文に『Her face was wet with tears』)。 | 前セリフ[the stranger from the firm:part2_c4 / the stranger from the firm:part2_c6] 後セリフ[Mr. White:part2_c10] 直前地の文「White shook her husband awake. Her face was wet with tears.」 直後地の文「He turned away.」 manner=tears |
| 7 | `part2_c10` | mr_white (Schedar) | 11 | 3.93 | 方向あり → 揃える前RMS↓ | 恐れ・ためらい: 夫が顔をそむけ、『お前は息子の姿を見ていない。何が戻ってくるのか怖い』と答える場面(直前の地の文に『He turned away』)。 | 前セリフ[the stranger from the firm:part2_c6 / Mrs. White:part2_c8] 後セリフ[Mrs. White:part2_c11] 直前地の文「He turned away.」 直後地の文「なし」 manner=なし |
| 8 | `part3_c1` | mr_white (Schedar) | 5 | 2.89 | 方向あり → 調音話速↓ | 恐れと決意・震え声: 階下で猿の手を見つけたMr. Whiteが、震える声で『息子を生き返らせてほしい』と最後に近い願いを口にする場面(直前の地の文に『His voice shook』)。 | 前セリフ[Mr. White:part2_c10 / Mrs. White:part2_c11] 後セリフ[Mrs. White:part3_c3] 直前地の文「His wife followed. His voice shook.」 直後地の文「It fell from his hand. They waited in the dark, listening to the clock.」 manner=なし |

セリフ本文(英):
1. `part1_c4` "but brings sorrow to anyone who interferes with fate."
2. `part1_c13` "Ask for two hundred pounds, Father. Enough to pay off the house!"
3. `part1_c15` "I wish for two hundred pounds."
4. `part2_c2` "Your son was caught in the machinery,"
5. `part2_c6` "The firm accepts no responsibility, but offers you two hundred pounds in compensation."
6. `part2_c8` "The paw! We have two wishes left. Wish him alive again!"
7. `part2_c10` "You didn't see him. I'm afraid of what might come back."
8. `part3_c1` "I wish Herbert alive again."

## 5. 感情種別の分布

- 開いた窓(8): 不安・緊張(1)/同情・小声(1)/不気味・悲しみ(1)/喜び・驚き・感情変化(2)/日常・戸惑い(対照1)/落ち着いた嘘(2)。
- 猿の手(8): 不吉な警告(1)/喜び・冗談(1)/期待と半信半疑(1)/重い知らせ(1)/事務的(対照1)/悲嘆・必死の頼み(1)/恐れ・ためらい(1)/恐れと決意・震え声(1)。
- 賢者の贈り物(Round 1)と合わせた3作品=24セリフで、喜び・悲しみ・不安・ささやき・事務的対照・落ち着いた嘘・恐れを網羅する。

## 6. ①(Production既存clip)の再利用確認(API 0)

- 16件すべて: `…/b1b/narration/<clip>_original.wav`(速度加工前の原音)と `…/b1b/narration/<clip>.wav`(最終音声)が存在、`tts_generation_results.json` の `asr_judgement.state=PASS`、`tts_execution_mode=STANDARD`、`tts_model_id=gemini-2.5-pro-preview-tts`、`style_effective_sha256=add26d27…`(Production既定styleと一致)。
- 採用原音は `attempts/<clip>_attempt<N>_englishstyleprefixwidemargin.json` の sha256 と一致(15件=attempt1、猿の手`part3_c1`のみattempt2)。= 比較対象①は「Productionが実際に最終採用した音声」。これを読み取りのみで再利用し、**①側のAPI生成は0**(`existing_audio_record` の `original_attempt_index` に記録)。
- Voiceは `voice_assignment.json`(Production Z)から取得し、①の実生成Voiceとtestで一致を検証(`test_round2_existing_audio_reusable_api0`)。
