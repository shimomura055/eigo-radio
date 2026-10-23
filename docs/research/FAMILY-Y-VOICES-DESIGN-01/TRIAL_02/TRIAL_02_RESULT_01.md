# TRIAL_02_RESULT_01: Family Y「Persona→Voice」Phase B 結果(Fable評価資料)

Status: `TRIAL_TEXT_DONE_AUDIO_INCOMPLETE_PENDING_FABLE`(委任_08、DEV/Trial、Production変更0)。**`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。VALIDATED自己宣言なし。**
検証の範囲: **手作業Persona Sheet(Arm H)・1テーマ(学校でスマホを預けるべきか)での検証**。Persona Generator(量産)の可能性・他テーマへの一般化は未検証(OF-Y3-17)。
最終稿=it2(テキスト2回目)。音声は**未完了**: Advancedは人物1の語りがRepetition QAでHuman Review待ち、Standardは費用上限超過のため途中で停止(§6、`判断候補`はRESULT_PACKET_FYT5.md)。

## 1. 最終報告項目の対応(10項目中 1〜7・9)
| # | 内容 | 場所 |
|---|---|---|
| 1 | 根本原因 | `REDESIGN_01/ROOT_CAUSE_01.md`(Phase A)、本Trialでの追加原因分析=`ITERATION_LOG_01.md` |
| 2 | 3人のPersona | §2、`PERSONA_SHEETS_FINAL_01.md` |
| 3 | 組合せと選定理由 | §2、`REDESIGN_01/PERSONA_CANDIDATES_01.md` |
| 4 | 構成実例(Comment 1/2・見出し・Tension+Closing) | §3 |
| 5 | R0のStd/Adv本文 | §4(音声試聴URL=§6、途中経過版) |
| 6 | 品質評価 | §5 |
| 7 | Research/Leakage整合 | §7、`B0_LEAKAGE_CONTROL_01.md` |
| 9 | 費用・推定量産単価・時間 | §8 |
(8=Opus/Fable評価はFableが実施。blind対比較の準備物=`BLIND_PAIRS_01.md`/`BLIND_KEY_01.json`)

## 2. 3人のPersona(最終Sheet、要約。全文=`PERSONA_SHEETS_FINAL_01.md`)
共通前提(3人とも同じ具体案): 学校が、登校した生徒のスマホを朝にまとめて預かり、下校のときに返す(登校している間はずっと預かる)ルールにするかどうか。

| | V1 | V2 | V3 |
|---|---|---|---|
| 人物 | 43歳、設備工事会社の現場監督(高校生の娘の父) | 54歳、高校の養護教諭 | 19歳、昼は倉庫で仕分け・夜は定時制の生徒 |
| 主張 | 学校が朝に一律で預かって下校時に返すと決めてくれれば「学校もそう言ってる」と言える。俺ひとりが悪者にならずに済む。 | 保健室まで没収の場にしたくない。禁止で「対策した」と安心されたら、夜のことを打ち明けてくれる子の行き場がなくなる、と私は思う。 | 授業中は鞄の奥に入れると約束する。でも朝から預けっぱなしは、仕事の連絡が切れるから守れない。 |
| 文のリズム(Sheet) | 短文の連続・平均約15字・長文は1つ | 短い断片と長めの文・平均約30字 | 中くらいの短文を「でも」で切返し・平均約18字 |
| 締めの型 | 自嘲的な断言 | 問い返し | 約束+要求 |
| 台帳事実 | JP-03(任意。実際は使われず0件) | 0件 | 0件 |

選定理由: 教師・親・生徒の主要当事者を含み、軸が夜の家庭/朝の保健室/昼の仕事で重ならない。V2(養護教諭)は教員のうち「取り上げられた後」を毎朝見る立場で、教科担任(Alt-A、V1と「悪者役」軸が重なる)より分離が良い。V3は前回V3・ユーザー原文の例示と同類型(開示)。男性2声(V1/V3)は音色差が小さいため、一人称・リズム・語り出し・語彙で聞き分けを補う設計。

## 3. 構成の実例(it2、全文)

### Comment 1(テーマ導入。共通前提を具体提示、背景factは台帳から手選び NL-01/FR-02/OECD-01)
**Std(日本語・Aoede)**
> 学校でスマートフォンをいつ、どのように使えるようにするかが、考えるテーマになっています。PISA 2022では、OECD平均で、生徒の30%が数学の授業中にデジタル機器の使用で気が散ると答えました。ただし、この数字はスマートフォンだけについてのものではありません。今回考えるのは、学校が登校した生徒のスマホを朝に預かり、登校中はずっと預かって、下校時に返すルールにするかどうかです。

**Adv(英語・Charon)**
> Rules about phones at school can cover different parts of the day. In the Netherlands, phones are not allowed during lessons, except when needed for learning, medical reasons, or a disability, and schools decide the details. The rule we are considering would have schools collect students’ phones in the morning and return them at dismissal, keeping them for the whole school day. The question is whether a school’s phone rule should last all day, not just during lessons.

### Comment 2(Voiceへの導入。人物紹介・取材表現なし)
**Std**
> これから、暮らしも立場も違う3人の声を続けて聞きます。それぞれが、どんな場面に目を向けているかに耳を傾けてください。

**Adv**
> Next, you’ll hear from three people with different lives and perspectives. As you listen, notice what each person focuses on.

### 見出し(Narrator Aoede。ordinal prefixは決定論付与)
- `One Voice: The bad guy at breakfast`(日本語表示: 朝食の悪者)
- `Another Voice: The sleepy faces by the bed`(日本語表示: ベッド脇の眠そうな顔)
- `A Third Voice: The work calls during class breaks`(日本語表示: 休み時間の仕事の電話)

### Tension+Closing(Gate通過後のVoice本文から生成。日本語)
> 朝の食卓でも、保健室の枕元でも、仕事の連絡でも、相手と話せるままでいたい。学校の預かりは、夜のカゴをめぐる押し問答を減らしても、枕元の話を遮るかもしれない。教室での学びを守れても、休憩中のシフトの連絡まで止まれば、職場の信用が揺らぐ。学校に助けを求める父親も、取り上げたあとの沈黙は、もう繰り返したくない。預ける時間には食い違いがあっても、話せる相手を残したいところは重なる。あなたがすぐに返したい連絡は、いつ、誰から届く？

## 4. R0本文
### 日本語(Gate通過後の最終稿)

**V1(父親・Algieba・「俺」)**
> うちの娘の高校で預かってほしい。朝にスマホをまとめて集める。下校のときに返してもらう。それまではずっと預けっぱなしだ。俺だけが悪者にならずに済む。夜は居間のカゴに入れる約束だ。うちの娘は守らなかった。俺はスマホを取り上げた。翌朝の食卓は静かだった。皿の音ばかり耳についた。決めたことは守ってほしかったのに、取り上げた俺のほうが娘の顔を見られなかった。あの朝は、もうごめんだ。学校もそうだと言えれば助かる。俺は夜の押し問答に疲れた。でも、学校に押しつけたいだけだ。現場じゃ段取りをつける側だ。家じゃ悪者役から逃げたいんだ。学校に助っ人を頼む親父だな、俺は。

**V2(養護教諭・Zephyr・「私」)**
> 眠い、って。朝いちばん、保健室へ来る子の顔を毎朝見ていると、私はその言葉の先が気になるんだ。この前、ベッドで休む子の枕元でスマホの画面が光っていた。私はその光から目を離せず、昨夜のことを聞きたくても、取り上げる先生だと思われたらどうなるんだろう？話せるのかな？朝にスマホをまとめて預かって下校まで返さない、それで済んだと思っていいのかな？預かったからもう大丈夫、となるのが私は怖い。私は、あの子が夜のことを話せるように、保健室だけは取り上げる場所にしたくないんだ。スマホを預かったあと、あの子の話は誰が聞くんだろう？

**V3(定時制の生徒・Schedar・「僕」)**
> 昼は倉庫で仕分けして、夜は定時制へ行く。でも、下校までスマホを預けるのは無理だ。授業で触らない約束なら守れる。休憩には、仕事の連絡を返したいんだ。前に、授業中に職場の着信が続いた。僕は出られず、画面の着信だけが増えた。あとで、連絡がつかないのは困ると言われた。シフトまで減らされそうになった。僕は働いたお金を家に入れている。僕は自分で、職場の信用を作りたい。でも、学校を辞めたいわけじゃない。ここで授業が分かるようになったんだ。仕事か学校かなんて、僕は選びたくない。授業中は鞄の奥にしまっておくと約束する。だから、決める前に僕の話を聞いてほしい。

### 英語 Standard(A2簡易化)
```
# Phones Handed In in the Morning: Different Voices

I want my daughter's high school to keep the phones. Collect them all in the morning. Give them back when school lets out. Until then, they stay with the school. Then I wouldn't be the only bad guy. We agreed she'd put her phone in a basket in the living room at night. My daughter didn't keep that promise. So I took her phone away. The next morning, breakfast was quiet. I could hear only dishes. I wanted her to keep our agreement. But after taking her phone, I couldn't look her in the face. I don't want another morning like that. It would help if I could say the school did it too. I'm tired of arguing every night. But really, I just want to push this onto the school. At work, I'm the one who makes the arrangements. At home, I want to get out of being the bad guy. I'm a dad asking the school to come to my rescue.

“I'm sleepy,” they say. Every morning, I see kids come to the nurse's office first thing. I wonder what else is behind that word. The other day, a child's phone screen glowed beside their pillow. The child was resting on a bed. I couldn't look away from that glow. I wanted to ask what happened last night. But what if they thought I was a teacher who takes phones away? Would they still talk to me? We could collect all the phones in the morning and keep them until school lets out. But can we say that is enough? I'm afraid that once we've collected the phones, we'll think everything is fine. I want that child to be able to talk about what happens at night. I don't want phones to be taken away in the nurse's office. After we take a phone away, who will listen to that child?

I sort packages in a warehouse during the day. At night, I go to evening high school. But I can't hand in my phone until school lets out. I can promise not to touch it during class. During breaks, I want to answer messages from work. Before, calls from work kept coming during class. I couldn't answer them. The missed calls kept piling up on my screen. Later, they told me it was a problem that they couldn't reach me. I almost had my shifts cut. I give the money I earn to my family. I want to earn trust at work myself. But I don't want to quit school. I've started to understand the lessons here. I don't want to choose between work and school. I promise I'll keep my phone at the bottom of my bag during class. So please listen to what I have to say before you decide.

At breakfast, by the pillow in the nurse's office, and when work messages come, people want to stay in touch. The school's phone collection might reduce arguments about the basket at night. But it could stop a talk by the pillow. It might protect learning in class. If it also stops work messages during breaks, trust at work could suffer. The father asks the school for help. He also doesn't want another silent morning after taking the phone away. They may disagree about how long phones should be handed in. But they all want someone they can still talk to. What message do you want to answer right away? When does it come, and who sends it?

## In one line
A father wants all-day phone collection, while a nurse and working student fear it may stop talks. They disagree about phone hand-in times, but all want someone to talk to.
```

### 英語 Advanced(忠実英訳)
```
# Phones Handed In in the Morning: Different Voices

I want my daughter's high school to hold onto the phones. Collect them all in the morning. Give them back when school lets out. Until then, they stay handed in. Then I wouldn't be the only bad guy. We agreed that at night, she'd put her phone in a basket in the living room. My daughter didn't keep that promise. I took her phone away. The next morning, breakfast was quiet. All I could hear was the sound of dishes. I wanted her to stick to what we'd agreed, but after I took her phone, I was the one who couldn't look her in the face. I don't want another morning like that. It would help if I could say the school was doing the same thing. I'm tired of arguing every night. But I just want to push this onto the school. At work, I'm the one who makes the arrangements. At home, I want to get out of being the bad guy. I'm a dad asking the school to come to my rescue.

“I'm sleepy,” they say. Every morning, I see the faces of kids who come to the nurse's office first thing, and I wonder what else is behind that word. The other day, a phone screen was glowing beside the pillow of a child resting on a bed. I couldn't look away from that glow. I wanted to ask about last night, but what would happen if they thought I was a teacher who takes phones away? Would they still talk to me? If we collect all the phones in the morning and don't give them back until school lets out, can we say that's enough? I'm afraid that once we've collected the phones, we'll think everything is fine. I want that child to be able to talk about what happens at night. I don't want the nurse's office to be a place where phones are taken away. After we take a phone in, who will listen to that child?

I sort packages in a warehouse during the day, and go to evening high school at night. But I can't hand in my phone until school lets out. I can keep my promise not to touch it during class. During breaks, I want to answer work messages. Before, calls from work kept coming during class. I couldn't answer, and the missed calls just kept piling up on my screen. Later, they told me it was a problem that they couldn't reach me. I almost had my shifts cut. I give the money I earn to my family. I want to earn my workplace's trust myself. But I don't want to quit school. I've started to understand the lessons here. I don't want to choose between work and school. I promise I'll keep my phone at the bottom of my bag during class. So please listen to what I have to say before deciding.

At the breakfast table, beside the pillow in the nurse's office, and when work messages come, people want to stay able to talk to the other person. The school's phone collection might reduce arguments over the basket at night, but it could cut off a conversation by the pillow. It might protect learning in class, but if it also stops messages about shifts during breaks, trust at work could be shaken. The father asking the school for help also doesn't want to go through the silence after taking the phone away again. They may disagree about how long phones should be handed in, but they share a wish to still have someone they can talk to. What message do you want to answer right away? When does it come, and who sends it?

## In one line
A father wants his daughter’s school to collect phones all day, while a nurse and a working student worry about what that could interrupt. They disagree about when phones should be handed in, but all want to stay able to talk to someone.
```


## 5. 品質評価(E1〜E14。Gate化しない観測。LLM判定は補助=gpt-6-luna、同系列バイアスあり)
証跡: `er110_output/family_y_persona_trial_01/school_phone_ban/it1/eval_01.json`・`it2/eval_01.json`・`it2/monitors_ja.json`。baseline=前回R0g(`REDESIGN_01/baseline_gate_r0.json`)。最終はOpus blind対比較・Fable評価・ユーザー試聴。
| ID | 項目 | it1 | **it2(最終)** | 目安 | 判定(自己評価、合否線は提案) |
|---|---|---|---|---|---|
| E1 | 主張の明確さ(blind claim extraction、英語) | Std 0/3 MATCH(PARTIAL 3)・Adv 0/3 | Std **1/3 MATCH**(PARTIAL 2)・Adv 0/3(PARTIAL 3) | 3/3 | 未達(LLM判定が厳格。抽出文は3人とも主張の前半を捉え、後半[V1の「学校ルールを後ろ盾に」、V2の「没収の場にしたくない」、V3の「預けっぱなしは無理」]を欠く場合にPARTIAL) |
| E2 | Persona差(blind speaker attribution) | 全文3/3・冒頭2文版3/3(Std/Adv) | 全文3/3・冒頭2文版3/3(Std/Adv) | 3/3 | 達成 |
| E3 | 抽象語率(/100字、日本語) | Voice最大0.0、Tension 0.48 | Voice最大0.37、Tension 0.0 | Voice≦2.0、Tension≦2.5 | 達成(語彙リスト素案による) |
| E4 | 具体場面数 | 各1以上 | 各1以上(V1=食卓の沈黙、V2=枕元の画面、V3=着信が増える画面) | 各≧1 | 達成 |
| E5 | 感情語(語彙リスト) | 2/2/1 | 2/1/1 | 各≧1 | 達成(語彙リストのみ。行為・間での表出は目視) |
| E6 | 文のリズム差(日本語、平均文長の範囲) | 2.9字(27.4/24.6/24.5) | **13.3字**(15.4/28.7/18.2) | ≧6字 | 達成 |
| E6' | 英語の文長範囲 | Std 1.4語・Adv 3.3語 | Std 1.4語・Adv 4.8語 | (参考) | Stdは未達(A2簡易化が文長を揃える)。Advは差が残る |
| E6'' | 語り出し・一人称・締めの型 | 3種/3種/3種 | 3種/3種/3種(自嘲的断言・問い・約束+要求) | 各3種 | 達成 |
| E8 | Leakage(最終稿、初回判定) | FAIL項目0 | FAIL項目0(Voice・Tension、judge=gpt-6-luna high) | 0 | 達成 |
| E9 | 芝居・誇張 | 「！」0、役割語0 | 「！」0、役割語0 | ≦1/0 | 達成 |
| E10 | Tensionに3つの具体物(Std/Adv英語) | 3/3・3/3 | 3/3・3/3(basket in the living room / pillow in the nurse's office / shift messages) | 3つ | 達成(テキスト上。ASR確認は音声未完のため未実施) |
| E11 | Tensionの文長・二重否定・抽象連鎖 | 最長39字・0・0・問い「？」なし | 最長41字・0・0・問いは「？」で終わる | ≦45字/0/抽象≦2 | 達成 |
| E12 | Comment 1/2・見出し | — | Comment 1に職業語0、取材表現0。見出し3本は5〜6語・ordinal正・数字なし・語の重複なし・ASR欠落0(両レベル6/6が初回で一致) | 同左 | 達成。英語のC1-C2 bigram重なりは文字bigramのため参考にならない(日本語: C1-C2 0.015、C1-Preview 0.085) |
| E13 | 優等生化していないか | — | 補助LLM対比較(前回R0g vs 新稿、順序ランダム・盲検)で新稿が「実在の人らしい」2/2・「丁寧に説明している感が強い」でない2/2。**主評価=Opus blind対比較(`BLIND_PAIRS_01.md`)** | Opus/Fable 4以上 | 未評価(Opus/Fable待ち) |
| E14 | 従来の安全条件 | PASS | PASS(数字0、取材表現0、一人称保持、4パート契約) | PASS | 達成 |
未達として残るもの: E1(LLM判定が厳格、主張の後半の抽出)、E6'(Std英語のリズム差)、E13のOpus/Fable判定。V1の冒頭がやや硬い(「うちの娘の高校で預かってほしい」)。これらはOpus blind対比較とユーザー試聴で優先度を決める事項。
止めどころ(OF-Y3-11)との対応: E1 3/3(英語)=未達、E8 0=達成、E14 PASS=達成、blind対比較=未実施(準備済み)、E10具体物3つ=達成。E1を目的化した3回目は行っていない(Charter 1・5、ITERATION_LOG_01.md)。

## 6. 音声(未完了。Status=AUDIO_INCOMPLETE)
- 実行: 最終稿it2のみ、Std/Adv各1回(`er110_family_y_persona_audio_trial_01.py --stage all`、Pro系TTS不使用=gemini-3.8-flash-lite-tts、固定Voice Algieba/Zephyr/Schedar、Narrator Aoede)。再起動なし。
- **Advanced**: 見出し3本(Aoede、減速なし、独立予算)は初回でOK(ASRは「One voice,」「Another voice,」「A third voice,」を含む=F11の接続句欠落なし)。V2・V3・Tension+Closing・In One Line・Key Phrase 6本・Comment 1/2・Previewは初回OK。**人物1(V1)の語りは3回の試行がRepetition QA(method D'=短ラグのスペクトル検出)で停止し、Human Review待ち(`HUMAN_REVIEW_REQUIRED`、cumulative_tts_attempts=3)**。3テイクとも約10.4秒付近で同じ検出(run長0.68秒>閾値0.6秒、lag約1.9秒)。HR Lockは迂回していない。従って全編通し音声(Adv)は未作成。
- **Standard**: 見出し3本は6%減速つきで初回OK(同じ接続句あり)、JA title・Preview・Comment 1/2もOK。人物1の語りの再試行中(Adv V1と同じ箇所で検出の兆候)に**費用が残枠を超過したため、私が自プロセスを停止**(§8)。Std人物2・人物3・Tension・In One Line・Key Phraseは未生成。通し音声なし。
- 試聴ページ(途中経過版、パート別のみ): `user_test/family_y_trial_02/index.html`(公開URLはRESULT_PACKET_FYT5.md)。Adv=人物1以外の全パート、Std=Comment/見出し/Previewのみ。Playwright実再生検証=`er110_output/family_y_persona_trial_01/audio/it2/play_verify.json`(RESULT_PACKETに結果)。
- 見出しの音声での確認(OF-Y3-05・16): 6本ともASR一致(NORMALIZED_MATCH)。A2語彙は「The bad guy at breakfast」「The sleepy faces by the bed」「The work calls during class breaks」で、旧「The basket where the phones sleep」型の比喩は避けられた。
- Comment 1/2の連続同声(Std=日本語Aoede、OF-Y3-15)は音声が揃っていないため試聴確認は未了。

## 7. Research/Leakage整合の確認(OPEN-470)
`B0_LEAKAGE_CONTROL_01.md`。現行判定(許容リストなし)は本人主語の伝聞1文をPASS 3/3、研究主語の文(報告調・伝聞形)をFAIL 3/3 → **ア'は不要、判定器・入力・定義は変更なし**(区分問題なし)。直したのはWriter Promptの伝聞形例示と書換え規則のみ。実Trialの最終稿では事実の使用は0件(V1は任意)で、「事実の自然な織込み」の実証はcontrolレベルまで(範囲の限定)。

## 8. 費用・推定量産単価・時間(出典=各`raw_usage_log*.jsonl`、`er053_cost_aggregate_01`/`xr.compute_cost_jpy_so_far`)
| 段 | 円 |
|---|---|
| B-0(Leakage control、luna) | 0.73 |
| it1: テキスト(Voice×3 12.56+Tension 4.98+Gate等) | 17.84 |
| it1: 英語+監視Leakage / 評価 | 1.27 / 0.23 |
| it2: テキスト(Voice×3 14.61+Tension 7.44+Gate等) | 22.27 |
| it2: 英語+監視Leakage / 見出し再生成 / 評価 | 1.11 / 0.08 / 0.23 |
| it2: scaffold(Comment 1/2・Preview・KP) / RF | 2.74 / 2.06 |
| 音声: Adv(Gemini batch 4.88 + OpenAI ASR 2.00 + Azure STT 7.31 + OpenAI 0.52) | 14.71 |
| 音声: Std(途中まで。**Comment 1の日本語読み方確認の1 call=gpt-5.6-sol+web検索3回で22.8**、他4.3) | 27.13 |
| **合計** | **90.37**(残枠74.62円に対し**+15.75円超過**。通算175.38+90.37=265.75円、上限250円に対し+15.75円) |
超過の主因: (1)Std `comment_1`(日本語)の読み方確認(`generate_a2_japanese_with_reading_safety`内、web検索3回+30k tokens入力)が1 callで22.8円。Comment 1に「PISA 2022」「OECD」「30%」を含めたため発火(旧Trialの日本語Commentには無かった)。事前見積に入れていなかった。(2)Adv V1のRepetition QA再試行3回(Azure STT等で約12円)。
日次(JST)開発費: 作業開始時 adopted 536.81円(`daily_dev_cost_01.py`)+本Phase 90.37円 → 約627円(1,000円未満)。
時間: 約5時間(テキスト2回約1.5時間、音声約1時間、残りは設計・実装・評価)。Gemini batchの待ち時間が最大約12分/segmentに伸びた。
推定量産単価(OF-Y3-17): テキスト段はSonnet設計Sheet(Arm H)で、Voiceごと別call(high)が各4〜5円、Tensionが5〜7円。DESIGN_PROPOSAL_03の想定95〜98円/記事は、Voice・Tensionのhigh effort callが想定より高く(+約10円/記事)、**約100円超**の可能性がある(70円目標は未達。主因はResearch/Ledger約40〜50円と、Writerのhigh effort)。Trial 1テーマの実測からの推定で、量産(Persona Generator)の費用は含まない。

## 9. 未解決・範囲外・注意
- 音声Trialの完遂にはAdv V1のHR承認(人間がテイクを聴く)と、Stdの残り生成(推定+8〜12円、V1が同じRepetition QAで止まる可能性が高い)が必要。費用は上限超過のため停止中(`判断候補`、RESULT_PACKET_FYT5.md)。
- Repetition QA(method D')が同じ箇所を3テイクで検出 → 検出対象の語句が決まっている可能性(OPEN-469と同系の過検出)。迂回していない。
- 採用時にユーザー判断事項: 5→4パート変更(リード廃止)、見出し読み上げ、Comment 3廃止、Voice長の増加(190→約270字)。いずれもTrialはDEV経路のみ。
- Std英語のリズム差は、X共有のA2簡易化関数を変更しない限り限定的(Y wrapperのmust_fix文のみ)。
