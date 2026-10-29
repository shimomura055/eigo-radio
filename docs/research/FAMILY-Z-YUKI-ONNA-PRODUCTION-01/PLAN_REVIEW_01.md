# PLAN_REVIEW_01 (FAMILY-Z-YUKI-ONNA-PRODUCTION-01 委任_01、2026-10-30、API 0)

目的(ユーザー原文§1・§3): 「英語学習者が音声を聞きながらでもストーリーを追いやすく、作品として楽しめる」。核の因果=吹雪の夜の出会い -> 「誰にも話すな」の約束 -> 後年の再会/正体判明 -> 約束を破った結果。
範囲: 原作(Hearn英語原文)とSeed(`er026_seeds/yuki_onna/seed.json`)に基づく**設計メモ**。実際の英語本文とrunner `plan`段(clip分割・話者判定)は本文(writer/std_adjust)の出力が入力のため、本文生成後でないと実行できない(下記§6)。以下の自己点検は「Seedが指示する構成」への事前点検で、**本文確定後に同じ5項目を再点検する**(委任_02の停止点)。

## 1. 登場人物・話者・Voice(Family Z既存仕様、導出結果は`derive_voice_assignment('yuki_onna')`で確認済み)
| 役割 | 名前 | 台詞 | Voice | 備考 |
|---|---|---|---|---|
| 語り手(三人称の語り部) | - | 地の文 | Aoede(narrator既定) | 場面頭で時・場所を告げる |
| 若い木こり | Minokichi(巳之吉) | あり(最終場面) | Algieba(男性Pool1番目) | keep_name |
| 白い女 = 後年の妻 | Yuki(お雪) | あり(小屋の囁き・最終場面) | Leda(女性Pool1番目=2026-10-29新順位、pinなし) | keep_name。**白い女と妻は同一話者=同一Voice**(聞き手が「同じ声だ」と気づける) |
| 老いた木こり | (Mosaku、名は出さない) | なし | - | 役割名のみ。lintでMosakuを禁止名に |
| 巳之吉の母・子どもたち | - | なし | - | 台詞なし |
- 話者は**2名+語り手**だけ(藪の中は7名+語り手不在)。Pool消費は男1・女1。登場人物名は2つだけ(Minokichi, Yuki)。Seedの`key_roles`/ESSENTIALS上限5件ちょうど(ending 1+setup 1+causality 1+keep_name 2)。

## 2. 場面・時系列(直線。回想・並行・視点交代なし)
| 場面(=Part境界の想定) | 時 | 内容 | 想定語数/台詞 |
|---|---|---|---|
| Part 1 | 吹雪の夜 | 老いた木こりと巳之吉が小屋に避難 -> 白い女が老人に息を吹きかけ凍死 -> 巳之吉に「誰にも話すな、母にも。話せば殺す」 -> 巳之吉は誰にも話さない | 約140語、台詞=白い女の囁き(Yuki Voice) |
| Part 2 | 翌年の冬〜年月 | 帰り道でYukiと出会う -> 母が気に入り同居 -> 結婚 -> 子ども10人、Yukiは歳をとらない(事実として1文) | 約100語、地の文中心(テンポ重視) |
| Part 3 | 数年後の夜 | ランプの下で縫い物をするYuki -> 巳之吉が「あの夜」を話す -> Yuki「それは私だ。話せば殺すと言った。子どもたちのために今は殺さない。大事にしろ」-> 霧になって消え二度と現れない | 約160語、台詞=巳之吉/Yukiの掛け合い(2声) |
- 各場面の冒頭に「いつ・どこ」を告げる短い1文(Seed `conversion_plan`: "open each of the three scenes with one short, plain sentence")。時系列は"strictly chronological"と指示。約束は(a)小屋で言い渡し (b)「巳之吉は誰にも話さなかった」と1文で明示 (c)最終場面でYukiが同じ内容を繰り返す、の3回出て聞き手が因果を保持できる。
- 因果の直線: 約束(Part 1) -> 沈黙(Part 1末) -> 結婚(Part 2) -> 約束を破る(Part 3) -> 正体判明と結果(Part 3)。『藪の中』のような「複数証言を突き合わせないと理解できない構造」は**ない**。

## 3. 自己点検(ユーザー原文§5の5項目、Seed段階の事前評価。○=問題なし/△=本文確認で条件付き/×=不可)
| # | 項目 | 判定 | 理由 |
|---|---|---|---|
| 1 | 音声だけでも理解しやすいか | ○ | 出来事は一本道・因果が3回リフレイン(上記)。語り部が各場面の頭で時・場所を告げる。感覚(風・雪・白い息・氷の顔・ランプ・風のような声)中心で、理解に視覚を要しない |
| 2 | 登場人物の関係は明確か | ○ | 話者2名のみ。名前は2つ(Minokichi, Yuki)で他は役割名(old woodcutter, his mother)。「妻が白い女と同一」は同一Voiceで音声上も裏付けられる |
| 3 | 「今どの場面か」を追えるか | ○(△要確認) | 3場面+場面頭の時間・場所文を指示済み。**本文で場面頭の1文が実際に書かれたかは委任_02の本文確認で検証**。Part境界(plan段)が場面と一致するかも本文後に確認 |
| 4 | 怪談の雰囲気を保ちつつ説明不足になっていないか | ○ | 正体を説明する語り(語り手のコメント)は禁止、正体はYuki本人の台詞で明かす(原作と同じ)。必要な因果(約束・沈黙・破った・結果)は台詞と1文で明示 |
| 5 | セリフと地の文のバランス | ○(△要確認) | Seedは台詞を全体の約1/3と指示(白い女の囁き+最終場面の掛け合い)。藪の中は台詞ほぼ全体だったが、本作は地の文が主で台詞が山場に集中。**実際の比率は本文で確認** |

## 4. 懸念と対応(委任範囲内で調整した点 / 仕様上の限界)
1. 原作1,467語 -> 約400語(Adv/Std)の圧縮: 削る要素を`discarded_elements`・`free_to_cut`で明示。残す要素は`seed_elements`の14項目(出会い・約束・沈黙・結婚・変わらぬ姿・語り・正体・結末)。**調整済み(Seed記述のみ。Prompt・コード不変)**
2. 正体判明の伝わりやすさ: Yukiの台詞を「It was I - Yuki!」+約束の繰り返し+「子どもたちのため」の3点で着地させるよう指示。前もって匂わせない(`withhold_until_end`)が、原作の小さな手がかり(白い肌・年をとらない)は事実として残してよい。**調整済み**
3. 引用符・話者固定: 『藪の中』で問題になった「閉じ引用符の無い発言がnarratorで読まれる」(OPEN-596、`er062 quote_spans`)は**story非依存の関数のため雪女にも適用される**(testで確認: `test_unclosed_opening_quote_is_a_quote_span`)。話者固定(`STORY_VOICE_PINS`)は**雪女には適用外**(pinは藪の中等の制作済み作品の旧女性Voice維持用。雪女は新規作品=pinなし、女性は新順位のLeda)。narrator pin(`STORY_NARRATOR_VOICE_PINS`)も雪女は対象外(語り手=Aoede)。
4. 発話者判定: 決定論キーワードは明示名(minokichi/yuki/o-yuki/the woman in white/the white woman/the snow woman/his wife + 発話動詞)のみ。"she/he"のみの引用はLLM判定(runnerの既存突合。決定論とLLMが食い違うとSTOP)。Seedに「plain speech tag that names the speaker」を指示し決定論判定の的中率を上げる。
5. 日本語タイトルTTS「雪女」のASR(藪の中のOPEN-593=人名ASR誤認の再発性): 「雪女」は一般語であり人名よりリスクは低いと見込むが**未検証**(Std日本語clip生成時に確認)。人名Minokichi/Yukiの発音確認はledger/CMU経路(既存retry/fallback)に従う。
6. **仕様上の限界(既存入力で調整できない点)**: narrator(Aoede、女性系)と女性話者Yuki(Leda)の声の聞き分けしやすさ。Voice割当は承認済みの決定的規則(narrator固定Aoede・女性Pool Leda/Erinome/Sulafat/Kore/Zephyr)で、雪女だけ変えるには新規のstory別narrator pin(告げ口心臓のFenrir例=ユーザー決定の前例)が必要=新仕様。現時点で判断不要。**本文後の実音声(Yukiの囁きがナレーションと聞き分けられるか)で問題が出た場合に限り判断候補D**とする(Z既存のダイアログ用style/ctx指示で演じ分けが入るため、まず実測)。
7. 最大TTS6回(Dialogue)・LR1回・HR停止点は既存のまま(変更なし)。台詞clipが藪の中より少ない(2話者・約8引用の見込み)ため、費用・再生成リスクは藪の中より低い見込み。

## 5. Std / Adv の想定
- Adv: 約400語(330-470許容)。三人称・過去形の語り+台詞。語彙はHearn原文由来(snowstorm, ferry, hut, woodcutter, whisper, melt, mist 等)を平易な現代英語で。Comment/KP/Wordは英語(Adv)。
- Std: Advから難易度調整(Z既存のstd_adjust)。同一ストーリー・同一場面構成・同一話者のまま、語彙と文長のみ平易化(台詞は短文化)。日本語Comment/KP意味(Std)。
- 難度差はZ既存仕様どおり(新Validator・新Gateなし。ユーザー決定2026-10-12)。

## 6. runner `plan`段について(重要な前提)
- E2E_STAGES順=seed_check, writer, std_adjust, **plan**, support, kp, tts_b1b, tts_a2, provision_shell, gate, assemble, pages, page_verify(`er026...runner.py:1183`)。`plan`段(`stage_plan`、`er026...runner.py:1483`)は`segment_plan_{lv}.json`を**英語本文**から作る(LLM: 3分割+会話話者判定)ため、writer/std_adjustの出力が前提。したがって本文を生成せずにrunner `plan`段を正式経路で実行することはできない。
- 本委任で実行したのは seed_check の dry-run(API 0、SEED_CHECK_DRYRUN_01.txt: essentials 5件・fail-closed確認・Voice導出 narrator=Aoede/yuki=Leda/minokichi=Algieba)と、CP checklist機械生成(CP_CHECK_01.md)まで。
- 提案: 委任_02を**停止点付き**にする(下記)。writer+std_adjust+planまでを1起動で行い(`--stages seed_check,writer,std_adjust,plan`)、本文と構成(Part境界・clip数・話者判定)を§3の5項目で再点検してから、support/KP/TTS以降へ進む。これにより費用の大きいTTS(約¥20-30)の前に作品適性を本文で確認できる。
