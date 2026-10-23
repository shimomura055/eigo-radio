# TEXT_DIFF_01: 初回稿(it1)→修正稿(it3)の差分(日本語/Standard/Advanced)

Status: DEV/Trial。LLM Writerを呼ばず手修正(初回稿を基準、世界設定整合・ねじれた文の是正)。Tension+Closingのみ、it2の具体的な構成を新設定へ合わせて作成。
凡例: `-`=初回稿のみ、`+`=修正稿のみ(文単位。同一文は省略)。「維持文数」=同一のまま残った文の数。

## 0. 保持する長所と修正の方針
### 保持する長所(根拠: TRIAL_02_RESULT_01 §5 E2/E4/E5、Fable評価[DECISION_LOG 2026-10-23 委任_09「具体的出来事・感情・明確な主張が立ち3人の語り口差が明確」]、ユーザーのV1高評価)
※Opus blind対比較の結果ファイルは本リポジトリ内に見当たらず未入手(BLIND_PAIRS_01に回答が残っていない)。長所リストは上記の記録から導出。
1. V1: 「俺だけが悪者にならずに済む」の主張 → 居間の充電カゴ・取り上げた翌朝の食卓の沈黙 → 「私だけ返事が遅れると外される」に言い返せなかった → 「楽になりたいだけな気もする」の自己矛盾 → 「家じゃ段取りも組めない現場監督だ、俺は。」の自嘲の締め。短い断言の連続。
2. V2: 「眠い、って。頭が痛い、って。」の断片、枕元で光る画面、昼間に取り上げられて来なくなった子、「来ないのと、つらくないのは同じなんだろうか」、最後の問いかけ。
3. V3: 休み時間に来るシフト連絡 → 返事が遅いと仕事が回される → 授業中の着信が続いて減らされかけた → 「仕事か学校かなんて、選びたくない」 → 約束(授業中は鞄の奥)+要求(決める前に聞いてほしい)の締め。
4. 3人の聞き分け: 一人称(俺/私/僕)・語り出し(主張/場面/主張)・締めの型(自嘲的断言/問い/約束+要求)。
5. 数字・調査説明・「！」・役割語を持ち込まない(Researchは裏方)。
### 修正対象と理由
| # | 修正 | 理由 |
|---|---|---|
| 1 | 規則の文言(V1冒頭、V2の「学校が…預かって」、V3冒頭・末尾、Tension、タイトル) | 世界設定の再設計(WORLD_SETTING_01.md: 朝回収・下校返却→休み時間・昼休みも含む校内使用の範囲) |
| 2 | V1「居間の充電カゴに入れると決めたのに守られず、…取り上げた翌朝の食卓では、娘と口をききづらかった」を2文に分けて主語を明確化。「取り上げた翌朝の食卓で、娘と口をききづらかった」 | ねじれた文(主語の切り替わり)。内容は不変 |
| 3 | V1「親父みたいに」→「うちの親父みたいに」 | 誰の親か不明確 |
| 4 | V1「ただ、昼間預けさせても夜の家は変わらないのに、学校に頼んで…」→2文に分割 | 逆接「のに」の長いねじれ。「それでも楽になりたいだけ」という自己矛盾はそのまま |
| 5 | V3「休憩中に」→「授業の合間の休み時間に」、長い1文(約45字)を2文に分割(「だから、」で受ける) | 仕事の休憩と学校の休み時間の曖昧さ除去、V3の中程度の短文リズムの回復 |
| 6 | V2に「先生に『スマホを禁止にしたら、保健室に来る子は減る？』と聞かれて、私は答えに詰まった」を1文追加 | なぜ養護教諭がこの件で発言するのか(職務・先生との関係)を自然に示す。回収の担当ではない |
| 7 | Tension+Closing全面差替(it2の具体的な構成[3つの具体物・「？」で終わる具体的な問い]を新設定に合わせて作成) | 初回稿のTensionは「暮らしや通学が苦しくなる」など抽象語が先行(ITERATION_LOG_01 it1原因分析3) |
| 8 | 英語: LLM訳の意味ずれ・誤用を手修正(「規則が既にある」と読める誤訳、「each other」「stop talking to us」等) | llm_original/との差分。Std/Advの文長・語彙差は維持 |

## 1. 日本語

### V1(父・Algieba): 初回稿10文 → 修正稿13文、維持文数 5

```
- (初回稿) 俺は、学校が朝にスマホを預かって、下校の時に返すルールに賛成だ。
- (初回稿) 現場から遅く帰って、高校に通ううちの娘と毎晩スマホで揉めるのはしんどい。
+ (修正稿) 俺は、娘の高校で、休み時間や昼休みもスマホを使わせない決まりに賛成だ。
+ (修正稿) 授業中だけじゃ足りない。
+ (修正稿) 現場から遅く帰って、毎晩スマホで揉めるのはしんどい。
- (初回稿) 居間の充電カゴに入れると決めたのに守られず、取り上げた翌朝の食卓では、娘と口をききづらかった。
+ (修正稿) 居間の充電カゴに入れる約束を、娘は守らなかった。
+ (修正稿) 取り上げた翌朝の食卓で、娘と口をききづらかった。
- (初回稿) 親父みたいに怒鳴るのも嫌だ。
- (初回稿) ただ、昼間預けさせても夜の家は変わらないのに、学校に頼んで俺が楽になりたいだけな気もする。
+ (修正稿) うちの親父みたいに怒鳴るのも嫌だ。
+ (修正稿) ただ、昼間の学校で使えなくしても、夜の家は変わらない。
+ (修正稿) 学校に頼んで俺が楽になりたいだけな気もする。
```

### V2(養護教諭・Zephyr): 初回稿11文 → 修正稿12文、維持文数 9

```
- (初回稿) 学校が朝にスマホをまとめて預かって下校まで返さないと決めたら、それで済んだと思ってしまわないかな。
+ (修正稿) 先生に「スマホを禁止にしたら、保健室に来る子は減る？」と聞かれて、私は答えに詰まった。
+ (修正稿) 学校が休み時間まで使えなくして、それで対策した気になってしまわないかな。
- (初回稿) 預かったあと、あの子の話は誰が聞くんだろう。
+ (修正稿) 使えなくしたあと、あの子の話は誰が聞くんだろう。
```

### V3(定時制の生徒・Schedar): 初回稿11文 → 修正稿12文、維持文数 7

```
- (初回稿) 僕は、朝にスマホを集めて下校まで預かるのには反対だ。
- (初回稿) 昼は倉庫で働いて、夜は定時制に通っているから、学校にいる間ずっと連絡を切る約束はできない。
- (初回稿) 休憩中にシフト変更の連絡が来る。
+ (修正稿) 僕は、休み時間までスマホを使えなくする決まりには反対だ。
+ (修正稿) 昼は倉庫で働いて、夜は定時制に通っている。
+ (修正稿) だから、学校にいる間ずっと連絡を切る約束はできない。
+ (修正稿) 授業の合間の休み時間に、シフト変更の連絡が来る。
- (初回稿) でも、まとめて預かると決める前に、僕の働き方も聞いてほしい。
+ (修正稿) でも、休み時間まで使えなくすると決める前に、僕の働き方も聞いてほしい。
```

### Tension+Closing(Narrator): 初回稿6文 → 修正稿7文、維持文数 0

```
- (初回稿) 三人とも、スマホのことで暮らしや通学が苦しくなるのを避けたい。
- (初回稿) 夜の居間のカゴ、朝の保健室の枕元、休憩中のシフト連絡では、困る時も場所も違う。
- (初回稿) 守りたいのは、親子の会話、つらさを話せる場所、働きながら通う日々だ。
- (初回稿) 預ける決まりは、親子の助けになっても、話や連絡を途切れさせるかもしれない。
- (初回稿) 父親も先生も、昼に預かるだけで夜の困りごとが消えるとは思っていない。
- (初回稿) あなたが今日、スマホを手放すと困るのは、いつ、どこにいるときだろう。
+ (修正稿) 朝の食卓でも、保健室の枕元でも、休み時間の仕事の連絡でも、相手と話せるままでいたい。
+ (修正稿) 使えない時間を広げれば、夜のカゴをめぐる押し問答は減るかもしれない。
+ (修正稿) けれど、取り上げられた子は、枕元で話してくれなくなるかもしれない。
+ (修正稿) 授業中は守れても、休み時間のシフトの連絡まで止まれば、職場の信用が揺らぐ。
+ (修正稿) 学校に助けを求める父親も、取り上げたあとの沈黙は、もう繰り返したくない。
+ (修正稿) 使える時間の長さは食い違っても、話せる相手を残したいところは重なる。
+ (修正稿) あなたがすぐに返したい連絡は、いつ、誰から届く？
```

## 2. Standard(英語)

- タイトル: 初回稿 `Phones Handed In in the Morning: Different Voices` → 修正稿 `No Phones Even at Break Time: Different Voices`

### V1(父・Algieba): 初回稿14文 → 修正稿16文、維持文数 0

```
- (初回稿) I support the rule that the school takes students’ phones each morning.
- (初回稿) It gives them back when school ends.
- (初回稿) I get home late from the worksite.
- (初回稿) It’s tiring to argue with my high school daughter about her phone every night.
- (初回稿) If I could say, “The school has the same rule,” I would not be the only bad guy.
- (初回稿) We agreed she would put her phone in the charging basket in the living room.
- (初回稿) But she did not stick to it.
- (初回稿) The morning after I took it away, it was hard to talk to her over breakfast.
- (初回稿) She also said, “If I’m the only one who replies late, I’ll be left out.” I couldn’t argue back.
- (初回稿) I want her to stick to what we decide.
- (初回稿) I don’t want to yell like my dad did.
- (初回稿) Still, even if the school keeps her phone during the day, things at home won’t change at night.
- (初回稿) Maybe I just want to ask the school to make things easier for me.
- (初回稿) I’m a site supervisor who can’t even make a plan at home.
+ (修正稿) I am for a rule at my daughter's high school.
+ (修正稿) It would keep phones off during breaks and lunch, too.
+ (修正稿) Only banning them in class is not enough.
+ (修正稿) I get home late from the job site.
+ (修正稿) Fighting about phones every night makes me tired.
+ (修正稿) If the school has the same rule, I won't be the only bad guy.
+ (修正稿) My daughter did not keep our agreement.
+ (修正稿) She was supposed to put her phone in the living-room charging basket.
+ (修正稿) I took her phone away.
+ (修正稿) The next morning, it was hard to talk to her at breakfast.
+ (修正稿) She also said, “If I am the only one who replies late, I will be left out.” Her words left me speechless.
+ (修正稿) A promise is a promise, and I want it kept.
+ (修正稿) Shouting like my father is not what I want, either.
+ (修正稿) But if she can't use her phone at school, nothing changes at home at night.
+ (修正稿) Maybe I just want the school to help so my life is easier.
+ (修正稿) I am a site supervisor who can't even manage things at home.
```

### V2(養護教諭・Zephyr): 初回稿13文 → 修正稿15文、維持文数 1

```
- (初回稿) I see the faces of children who come to the nurse’s office first thing every morning.
- (初回稿) “I’m sleepy,” they say.
+ (修正稿) First thing every morning, I see the kids who come to the nurse's office.
+ (修正稿) “I'm sleepy,” they say.
- (初回稿) The other day, I saw a bright phone screen beside the pillow of a child resting on a bed.
- (初回稿) When I hear they were awake until dawn, I wonder what I should say.
- (初回稿) I also worry about a child who stopped coming to the nurse’s office.
- (初回稿) This happened the day after the school took their phone away.
- (初回稿) Does not seeing them mean they are not having a hard time?
- (初回稿) If the school decides to collect all the phones in the morning and keep them until the end of the day, will we think that takes care of it?
- (初回稿) That is what scares me.
- (初回稿) I don’t take phones away in the nurse’s office.
- (初回稿) I want to keep a place where students can talk about what happened at night.
- (初回稿) After we take their phones, who will listen to that child?
+ (修正稿) The other day, a student was resting on the bed.
+ (修正稿) Their phone screen glowed beside the pillow.
+ (修正稿) When I hear they stayed up until morning, I don't know what to say.
+ (修正稿) I also think about one student.
+ (修正稿) After their phone was taken away at school, they stopped coming to see me.
+ (修正稿) If they don't come, does that mean they are okay?
+ (修正稿) A teacher asked me, “If we ban phones, will fewer kids come to the nurse's office?” I could not answer.
+ (修正稿) If the school bans phones during breaks too, will it think the problem is solved?
+ (修正稿) That scares me.
+ (修正稿) I don't take phones away in the nurse's office.
+ (修正稿) I want to keep a place where kids can talk about what happened at night.
+ (修正稿) After the phones are off-limits, who will listen to that child?
```

### V3(定時制の生徒・Schedar): 初回稿14文 → 修正稿17文、維持文数 2

```
- (初回稿) I’m against collecting phones in the morning and keeping them until school ends.
- (初回稿) I work in a warehouse during the day.
+ (修正稿) I'm against a rule that bans phones during breaks, too.
+ (修正稿) I work at a warehouse during the day.
- (初回稿) So I can’t promise to be out of touch the whole time I’m at school.
- (初回稿) During breaks, I get messages about changes to my shift.
+ (修正稿) So I can't promise to stop all contact while I'm at school.
+ (修正稿) Between classes, I get messages about my shifts.
- (初回稿) Once, calls kept coming from work during class, but I couldn’t answer.
- (初回稿) Later, they told me it was a problem that they couldn’t reach me.
- (初回稿) My shifts almost got cut, too.
- (初回稿) I want to graduate from here.
- (初回稿) I need to give money to my family, too.
- (初回稿) Now that I’ve started to understand my classes, I don’t want to choose between work and school.
- (初回稿) I promise to keep my phone deep in my bag and not touch it during class.
- (初回稿) But before deciding to collect everyone’s phones, please hear about how I work, too.
+ (修正稿) Once, my workplace kept calling during class.
+ (修正稿) I couldn't answer.
+ (修正稿) Later, they told me it was a problem that they could not reach me.
+ (修正稿) They almost cut my shifts, too.
+ (修正稿) I want to graduate from this school.
+ (修正稿) I also need money to give to my family.
+ (修正稿) Now I can understand my classes.
+ (修正稿) I don't want to choose between work and school.
+ (修正稿) I promise to keep my phone at the bottom of my bag.
+ (修正稿) I won't touch it during class.
+ (修正稿) But before you decide, please hear how I work, too.
```

### Tension+Closing(Narrator): 初回稿8文 → 修正稿10文、維持文数 0

```
- (初回稿) All three want to stop phone problems from making life or school harder.
- (初回稿) The trouble comes at different times and places: the basket in the living room at night, the pillow by the bed in the nurse’s office in the morning, and shift messages during breaks.
- (初回稿) What they want to protect is talk between parent and child.
- (初回稿) They want a place to talk about what is hard.
- (初回稿) They also want to keep daily life going while they go to school and work.
- (初回稿) A rule about handing in phones may help parents and children, but it might also cut off talks and contact.
- (初回稿) Neither the father nor the teacher thinks taking phones during the day alone will make problems at night go away.
- (初回稿) When and where today would it be hard for you to give up your phone?
+ (修正稿) At breakfast, beside the pillow in the nurse's office, and through work messages during breaks, people want to keep talking with someone.
+ (修正稿) Longer phone-free time may mean fewer fights about the basket at night.
+ (修正稿) But a student whose phone is taken away may stop talking at the bedside.
+ (修正稿) He may follow the rule in class.
+ (修正稿) But if his shift messages stop during breaks, his workplace may lose trust in him.
+ (修正稿) The father who asks the school for help also does not want another silent morning after taking the phone away.
+ (修正稿) They may disagree about how long phones can be used.
+ (修正稿) But they all want someone they can still talk to.
+ (修正稿) What message do you want to answer right away?
+ (修正稿) When does it come, and who sends it?
```

### In one line
```
- (初回稿) Three people say a school phone rule may help some, but make life harder for others. The rule may help families argue less, but cut off talks and contact without fixing home problems.
+ (修正稿) A father wants phones off at school even during breaks, but a nurse and a working student worry that it may stop talks. They disagree about when phones can be used, but all want someone to talk to.
```

## 3. Advanced(英語)

- タイトル: 初回稿 `Smartphones Handed In in the Morning: Different Voices` → 修正稿 `No Phones Even at Break Time: Different Voices`

### V1(父・Algieba): 初回稿11文 → 修正稿12文、維持文数 0

```
- (初回稿) I support the rule that the school takes students’ phones in the morning and gives them back when school lets out.
- (初回稿) I get home late from the worksite, and it’s exhausting to argue with my daughter, who’s in high school, about her phone every night.
- (初回稿) If I could say, “The school has the same rule,” I wouldn’t have to be the only bad guy.
- (初回稿) We agreed she would put it in the charging basket in the living room, but she didn’t stick to it.
- (初回稿) The morning after I took it away, it was hard to talk to her over breakfast.
- (初回稿) She also said, “If I’m the only one who replies late, I’ll be left out.” I couldn’t argue back.
- (初回稿) I want her to stick to what we decide.
- (初回稿) I don’t want to yell like my dad did.
- (初回稿) Still, even if the school keeps her phone during the day, things at home won’t change at night.
- (初回稿) Maybe I just want to ask the school to make things easier for me.
- (初回稿) I’m a site supervisor who can’t even make a plan at home.
+ (修正稿) I'm for a rule at my daughter's high school that keeps phones off during breaks and lunch, too.
+ (修正稿) Banning them only during class isn't enough.
+ (修正稿) I get home late from the job site, and fighting about phones every night is exhausting.
+ (修正稿) If the school has the same rule, then I'm not the only bad guy.
+ (修正稿) My daughter didn't keep our agreement to put her phone in the living-room charging basket.
+ (修正稿) The morning after I took it away, it was hard to talk to her at breakfast.
+ (修正稿) She also said, “If I'm the only one who replies late, I'll be left out.” Her words left me speechless.
+ (修正稿) Still, a promise is a promise, and I want it kept.
+ (修正稿) Yelling like my father is out of the question, too.
+ (修正稿) But even if she can't use her phone at school during the day, nothing changes at home at night.
+ (修正稿) Maybe I just want to ask the school for help so things are easier for me.
+ (修正稿) I'm a site supervisor who can't even get things organized at home.
```

### V2(養護教諭・Zephyr): 初回稿12文 → 修正稿13文、維持文数 1

```
- (初回稿) I see the faces of the children who come to the nurse’s office first thing every morning.
- (初回稿) “I’m sleepy,” they say.
+ (修正稿) First thing every morning, I see the faces of the kids who come to the nurse's office.
+ (修正稿) “I'm sleepy,” they say.
- (初回稿) The other day, a phone screen was glowing beside the pillow of a child resting on a bed.
- (初回稿) When I hear they were awake until dawn, I wonder what I should say.
- (初回稿) I also worry about the child who stopped coming to the nurse’s office the day after their phone was taken away at school.
- (初回稿) Does not seeing them mean they aren’t having a hard time?
- (初回稿) If the school decides to collect all the phones in the morning and keep them until the end of the day, will we end up thinking that takes care of it?
- (初回稿) That is what scares me.
- (初回稿) I don’t take phones away in the nurse’s office.
- (初回稿) I want to leave a place where students can talk about what happened at night.
- (初回稿) After we take their phones, who will listen to that child?
+ (修正稿) The other day, a phone screen was glowing beside the pillow of a student resting on the bed.
+ (修正稿) When I hear they were up until dawn, I wonder what I should say.
+ (修正稿) I also keep thinking about a student who stopped coming the day after their phone was taken away at school.
+ (修正稿) If they don't come, does that mean they aren't struggling?
+ (修正稿) A teacher asked me, “If we ban phones, will fewer kids come to the nurse's office?” I couldn't answer.
+ (修正稿) If the school makes phones off-limits even during breaks, won't it feel it has dealt with the problem?
+ (修正稿) That really scares me.
+ (修正稿) I don't take phones away in the nurse's office.
+ (修正稿) I want to keep a place where students can talk about what happened at night.
+ (修正稿) After phones are off-limits, who will listen to that child?
```

### V3(定時制の生徒・Schedar): 初回稿12文 → 修正稿13文、維持文数 2

```
- (初回稿) I’m against collecting phones in the morning and keeping them until school is over.
- (初回稿) I work at a warehouse during the day and go to evening high school at night, so I can’t promise to be out of touch the whole time I’m at school.
- (初回稿) During breaks, I get messages about changes to my shift.
+ (修正稿) I'm against a rule that makes phones off-limits even during breaks.
+ (修正稿) I work at a warehouse during the day and go to evening high school at night.
+ (修正稿) So I can't promise to cut off contact the whole time I'm at school.
+ (修正稿) During breaks between classes, I get messages about changes to my shifts.
- (初回稿) Once, calls kept coming from work during class, but I couldn’t answer.
- (初回稿) Later, they told me it was a problem that they couldn’t reach me.
- (初回稿) My shifts almost got cut, too.
+ (修正稿) Once, my workplace kept calling during class.
+ (修正稿) I couldn't answer, and later they told me it was a problem that they couldn't reach me.
+ (修正稿) I almost had my shifts cut, too.
- (初回稿) I need to give money to my family, too.
- (初回稿) Now that I’ve started to understand my classes, I don’t want to choose between work and school.
- (初回稿) I promise to keep my phone deep in my bag and not touch it during class.
- (初回稿) But before deciding to collect everyone’s phones, please hear about how I work, too.
+ (修正稿) I also need money to give to my family.
+ (修正稿) Now that I can follow my classes, I don't want to choose between work and school.
+ (修正稿) I promise to keep my phone at the bottom of my bag and not touch it during class.
+ (修正稿) But before you decide that phones are off-limits even during breaks, I want you to hear how I work, too.
```

### Tension+Closing(Narrator): 初回稿6文 → 修正稿8文、維持文数 0

```
- (初回稿) All three want to avoid having their lives or going to school become harder because of their phones.
- (初回稿) The times and places of trouble are different: the basket in the living room at night, the pillow by the bed in the nurse’s office in the morning, and shift messages during breaks.
- (初回稿) What they want to protect is conversation between parent and child, a place to talk about what’s hard, and daily life while going to school and working.
- (初回稿) A rule about handing in phones may help parents and children, but it might also cut off conversations and contact.
- (初回稿) Neither the father nor the teacher thinks that taking phones during the day alone will make problems at night go away.
- (初回稿) When and where today would it be hard for you to give up your phone?
+ (修正稿) At the breakfast table, beside the pillow in the nurse's office, and in work messages during breaks, people want to stay able to talk to someone.
+ (修正稿) Making phone-free time longer may mean fewer arguments over the basket at night.
+ (修正稿) But a student whose phone is taken away may stop opening up beside that pillow.
+ (修正稿) He can follow the rule during class, but if the shift messages he gets during breaks stop, his workplace may lose trust in him.
+ (修正稿) The father asking the school for help also doesn't want to go through the silence after taking the phone away again.
+ (修正稿) They may disagree about how long phones can be used, but they share a wish to keep someone to talk to.
+ (修正稿) What message do you want to answer right away?
+ (修正稿) When does it arrive, and who is it from?
```

### In one line
```
- (初回稿) Three people explain how collecting students’ phones at school could help some, but make life harder for others. The rule may ease family conflict, yet it could also cut off conversations and contact without solving problems at home.
+ (修正稿) A break-time phone ban may ease fights at home, but it could also stop students from opening up or answering work messages. The parent, nurse, and student disagree about when phones should be allowed, but all want someone they can still talk to.
```
