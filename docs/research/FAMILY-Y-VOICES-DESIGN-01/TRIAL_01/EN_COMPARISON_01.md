# EN_COMPARISON_01: Standard / Advanced 英語本文と評価(FAMILY-Y-VOICES-DESIGN-01 委任_04 Phase 2)

入力: Gate通過後の日本語原稿(`y_writer/gate_{r0,r1,r2}/article_final.md`)の3本。処理: Advanced=既存の忠実英訳(`generate_family_x_faithful_translation`)+In One Line(`_advanced_in_one_line`、M1(a)入り=日本語原稿とLedgerを入力に含む)、Standard=既存のA2簡易化(`generate_family_x_standard_a2_no_heading`、Advanced英文から)。**X関数は無変更で呼出のみ**。段落数ちょうど5・話者(Voice段落に一人称あり/リード・最終パートが一人称で始まらない)・Title+In One Lineの確認(M2)はY側の決定論確認(`check_en_contract`)。モデル: 英訳・簡易化・In One Line=X既定(gpt-6.1-sol)。監視Leakage(S3)=gpt-6-luna high(Gateにしない)。Risk Flagger=X既定(非停止、Review QueueはTrialのdir内に保存し、X/Zの正式Queueには書いていない)。

## 1. 事実(機械結果)
| 項目 | R0g | R1g | R2g |
|---|---|---|---|
| Advanced 5段落契約(再生成0) | PASS | PASS | PASS |
| Standard 5段落契約(再生成0) | PASS | PASS | PASS(X既定/S2とも) |
| 本文語数 Adv / Std | 495 / 460 | 529 / 503 | 570 / 536(S2版 542) |
| In One Line語数 Adv / Std | 38 / 37 | 37 / 33 | 40 / 34 |
| Voice段落の一人称語数(Std、V1/V2/V3) | 8/12/17 | 10/10/20 | 11/10/20 |
| リード/最終パートの一人称語数(Std) | 0 / 1 | 0 / 0 | 0 / 0 |
| Voice段落の数値表現(Std) | 0 | 0 | 0 |
| **S3 監視Leakage(Std英語、Gateにしない)** | 0件 | 0件 | 0件 |
| RF(Risk Flagger)flag件数 Adv / Std | 2 / 0 | 3 / 4 | 7 / 7 |
| 　うちVoice段落(2〜4段落目)のflag | Adv 0 / Std 0 | Adv 3 / Std 4 | Adv 4 / Std 6 |
| 　台帳外の事実断定とみなせるflag | 0 | 0 | 0 |
| 英語化の費用(忠実英訳+In One Line+A2簡易化[+S2]、実測円) | 約0.84 | 約1.01 | 約1.85(S2含む) |
| RF費用(Adv+Std、円) | 1.68 | 1.77 | 1.80 |
| 監視Leakage S3費用(円) | 0.15 | 0.22 | 0.16 |

注: 本文語数はXの実測(Std 385〜434、Adv 416〜446語、設計書01A §2)より多い(Y Std 460〜536語=+6〜+24%)。音声の尺・TTS/ASR費用に効くためPhase 3費用に反映する。語数・尺はGateにしない(Xと同じ)。

## 2. S2 (A2簡易化に話者・一人称・迷い保持の1文を足した版)の比較(R2gのみ)
実装: A2 Prompt本体は無変更で、既存の`must_fix`欄に「Paragraphs 2〜4は3人が一人称で語る。簡易化しても話者・一人称・迷い・混ざった気持ちを保ち、中立な説明にしない」を追加。事実: 契約PASS、一人称語数 X版 11/10/20 vs S2版 12/10/21、語数 536 vs 542。所見: 差は微小(n=1)。S2版は「I also don't want to give up my responsibility...」など一人称の語の保持がやや多いが、X版も3人の一人称・ためらい(「Still, I can't say...」「can I really say with confidence」)は保持されており、**S2の追加効果は本Trialでは確認できない**(約+0.5円で追加する価値は不明。判断はせず記録のみ)。

## 3. 評価(所見。Sonnetの読み)
1. **人物の個性・立場・主観性は英語でも維持された**: 3人とも一人称、具体的な場面始まり(教卓/資料と付箋/ノートの余白)、迷い(「I can't say...」「Can I really explain...」)が残った。S3監視Leakage 0件・一人称保持率が高く、英語化による解説者化の兆候は機械的には出ていない。
2. **ただし平板化の傾向は残る**: Std英語は文が短くなり、3人の文のリズムがさらに近づく(「I check... I lay out... I mark...」の並び)。日本語で人物間の質感の同質性があった点が、Stdでは強まって見える(所見)。聞き分けは声(Algieba/Zephyr/Schedar)の差に依存する度合いが高まる。
3. **最終パート**は抽象度が高く(「The power to decide where money goes, the power to run a classroom, and the responsibility to manage your own life are not the same.」)、A2学習者には負荷が高い(所見)。Std版も内容は簡略化されきっておらず、Y全体の「聞きやすさ」は最終パートが律速になる可能性がある。
4. R1g/R2gの修辞(「alarms ring in their minds」「One bag cannot hold everyone's idea of what is 'good'」)は英語でも意味が通る。「打ち出の小づち」は「The budget cannot make money appear from nowhere」と自然に言い換えられ、問題なし。
5. RFのflagの大半は人物の自己紹介文(「I teach Japanese at a junior high school」「I review school budgets for the local government」等=Cardの人物設定)で、台帳に無いため機械的にflagされたもの(設計書が予告した「Voice個人内容は台帳に無くflagが量産される」の実測)。R2は7件(R0は0〜2件)と多いが、R2の方が人物の場面描写が長い(自己紹介的な文が増える)ことに対応する。flagは人の確認待ちリストに入るだけで停止しない(X仕様)。**事実創作とみなせるflagは0件**(全件確認)。
6. 英語本文の語数がXより多い。Stdで約+25%は、TTS/ASR費用とStd尺(6%減速の適用後)に効く。最終パート(約110語)とVoice(約100〜125語×3)が主因。短縮は日本語段階のプロンプト長指定(段落字数の目安)で調整可能だが、新基準は作らない(記録のみ)。

## 4. 英語全文


### R0g Advanced
```
# What Comes After Putting Away Our Smartphones

If we put our smartphones away, what changes in the classroom? Where do looking away from the screen and learning meet? There are teachers, people who review school budgets, and people who study while working. Even when they face the same smartphone, they do not necessarily have the same concerns.

In a classroom before class, I teach Japanese at a middle school and mark a text we want to discuss. If smartphones no longer distract us, could we focus more on the text? I do hope so. But what I want to protect, apart from test scores, is not just a quiet classroom. It is time to encounter, through words, a point of view different from my own. I look over the lesson plan on the teacher’s desk. I don’t want to cut the time we spend with the text by focusing only on checking whether phones are put away.

As someone who reviews school budgets for a local government, I spread documents about device management and learning support across my desk and add sticky notes. Do I see this as money spent to reduce device use, or money spent to help students learn more? My hand stops as I write the review notes. I can’t say one should take priority while that difference remains unclear. I’m afraid of cutting necessary support from a limited budget. I can’t simply use findings from overseas as the answer for my own area. I have to explain what evidence I used to choose this allocation.

In an evening high school classroom after work, I take out my notebook and check whether there are any work messages on my phone. I want to avoid using it during class. Still, I can’t say that I will stay away from messages no matter what happens. As an adult, I want to take responsibility for both my work and my studies. In the margin of my notebook, I write what I want to tell the school. Before it is decided that devices will be locked away, I want room to think about it too. I don’t want to put in the bag my responsibility to manage how I use the device myself.

Everyone wants to value the time they spend learning. I think we agree on that. But when a decision is wrong, what people lose and how much they have to take on themselves are different. So we do not all have the same standard for saying it was a good choice. The power to decide where the money goes, the power to run a classroom, and the responsibility to manage one’s own life are not the same thing. And even if you have little say in what is decided, the weight of the decision is not necessarily any lighter. Even if you have something deeply important to protect, that does not mean you will have a say in the decision. Whose understanding is still waiting to be put into words?

## In one line
Teachers, budget reviewers, and working students all value learning time, but they have different concerns about smartphone rules. People who bear a decision’s weight may have little say in it, so their concerns still need to be heard.
```

### R0g Standard(X既定)
```
# What Comes After Putting Away Our Smartphones

If we put away our smartphones, what changes in class? How do looking away from screens and learning come together? Teachers, people who check school budgets, and people who study while working are all here. Even when they face the same smartphone, they may worry about different things.

Before class, I am in a middle school classroom. I teach Japanese and mark a text we want to discuss. If phones no longer distract us, could we focus more on the text? I hope so. But beyond test scores, I want to protect more than a quiet classroom. I want time to meet a point of view different from mine through words. I look over the lesson plan on the teacher’s desk. I don’t want us to spend less time with the text just to check if phones are put away.

As someone who checks school budgets for the local government, I spread papers about managing devices and helping students learn across my desk. I add sticky notes. Do I see this as money spent to reduce device use, or to help students learn more? My hand stops as I write my review notes. While this difference is unclear, I can’t say which should come first. I’m afraid of cutting needed support from a small budget. I can’t simply use findings from other countries as the answer for my area. I have to explain what information I used to choose how to spend this money.

In an evening high school classroom, after work, I take out my notebook. I check if I have any work messages on my phone. I want to avoid using it in class. Still, I can’t say I will stay away from messages, whatever happens. As an adult, I want to take responsibility for both my work and studies. In my notebook’s margin, I write what I want to tell the school. Before it is decided to lock devices away, I want room to think about it too. I don’t want to put my responsibility for managing my own device use into the bag.

Everyone wants to value the time they spend learning. I think we agree on that. But when a decision is wrong, people lose different things. They also have to carry different amounts themselves. So we do not all use the same standard to decide if it was a good choice. The power to decide where money goes, run a classroom, and manage your own life are not the same. Even if you have little say in a decision, its weight may not be any lighter. Even if you have something very important to protect, you may not get a say in the decision. Whose understanding is still waiting to be put into words?

## In one line
Teachers, people who check budgets, and working students all value learning time. But they have different worries about phone rules. People who carry a decision’s weight may have little say. Their worries still need to be heard.
```

### R1g Advanced
```
# Putting Away Our Phones, and What Comes Next

Put phones away and lock them up. Apparently, that does not solve everything in the classroom. If students look away from their screens, will learning switch on too? A teacher, someone who manages a school budget, and someone who studies while working may all look at the same phone, but different alarms are ringing in their minds.

Before class, I mark the parts of a text I want to discuss with my students. I teach Japanese at a junior high school. If the phones are in bags, will students be able to give their attention to the text in front of them? That makes me hopeful. But what I want to protect, apart from test scores, is not just “a completely quiet classroom.” It is a chance to meet views different from our own through words. I look back at my lesson plan. What if checking that the phones are away cuts into the time for working with the text? That would be a problem.

I review school budgets for the local government. I spread papers on device management and learning support across my desk and add sticky notes. Should spending to reduce phone use also be a priority as a way to help students do better in school? My hand stops as I write notes on the budget. Can I really explain the link: put phones away, and grades go up? Budgets are limited. I am afraid that spending money on bags could mean cutting support that students need. I cannot treat schools overseas and schools in this area as if they were the same. Even so, I have to show why I think the money should go where it does.

At the evening high school I go to after work, I take out my notebook and check whether I still have work messages on my phone. I want to avoid using it in class. But I cannot promise, “No matter what happens, I will stay away from work messages.” I want to take responsibility, as an adult, both for my job and for my studies. In the margin of my notebook, I write what I want to tell the school. Before the bag is closed, I want the door to a discussion to stay open. I do not want to put away my responsibility to control my own phone use along with my phone.

We all want to value the time we spend learning. That is what we share. But what we lose if a decision is wrong, and how much responsibility we must take on, are different. That is probably why we do not all use the same measure for what counts as “good.” The power to decide where money goes, the power to run a classroom, and the responsibility to keep life going are separate things. Even if you have little power to make decisions, the burden you carry is not any lighter. Even if what you want to protect matters deeply, you may not be able to take part in the decision. Before we close the bag, are we leaving behind someone who has not yet put into words that they can accept it?

## In one line
Putting phones away does not settle everything; teachers, budget officials, and working students face different concerns. They all value learning, but have different responsibilities and decision-making power, so discussion should stay open to concerns not yet voiced.
```

### R1g Standard(X既定)
```
# Putting Away Our Phones, and What Comes Next

Put phones away and lock them up. Still, this does not fix everything in class. If students stop looking at screens, will learning begin too? A teacher, someone who checks school budgets, and someone who studies while working may all see the same phone. But different alarms ring in their minds.

Before class, I mark the parts of a text that I want to discuss with my students. I teach Japanese at a junior high school. If phones are in bags, can students focus on the text in front of them? That makes me hopeful. But I want to protect more than test scores. I do not just want “a completely quiet classroom.” I want students to meet different views through words. I look back at my lesson plan. What if checking that phones are away takes time from working with the text? That would be a problem.

I review school budgets for the local government. I spread papers about managing devices and supporting learning across my desk. Then I add sticky notes. Should spending money to reduce phone use also be a priority, to help students do better at school? My hand stops as I write notes about the budget. Can I really explain the link: put phones away, and grades go up? Budgets are limited. I worry that spending money on bags could mean cutting support students need. I cannot treat schools overseas and schools in this area as the same. Even so, I have to show why I think the money should be spent that way.

At the evening high school I go to after work, I take out my notebook. I check whether I still have work messages on my phone. I want to avoid using it in class. But I cannot promise, “No matter what happens, I will stay away from work messages.” As an adult, I want to take responsibility for my job and my studies. In the margin of my notebook, I write what I want to tell the school. Before the bag is closed, I want the door to a discussion to stay open. I do not want to put my duty to control my own phone use away with my phone.

We all want to value the time we spend learning. That is what we share. But if a decision is wrong, what each of us loses is different. We also have different amounts of responsibility to take on. That is probably why we do not all use the same measure for what counts as “good.” The power to decide where money goes, the power to run a classroom, and the duty to keep life going are separate things. Even if you have little power to decide, your load is no lighter. Even if something you want to protect matters deeply, you may not be able to take part in the decision. Before we close the bag, are we leaving out someone who has not yet found words to say they can accept it?

## In one line
Putting phones away does not solve everything; teachers, budget workers, and working students face different worries. They value learning, but their duties and power differ, so we should hear worries not yet shared.
```

### R2g Advanced
```
# Putting Away Our Phones—and What Comes Next

Put a phone in a bag and click the lock shut. If only we could lock away the problems in the classroom, too. When the screen goes dark, does the learning switch turn on by itself? A Japanese teacher, someone who reviews school budgets, and a student who goes to school while working: even when they face the same bag, different alarms go off in each person’s mind.

Before class, I mark the passages I want to discuss with my middle school Japanese class. Looking at the lesson plan spread across the teacher’s desk, I think about where to add a check that everyone has put their phone away. I want them to focus on the text without worrying about their screens. But what I want to protect, beyond test scores, is not just a quiet classroom. It’s time to hear, through words, how other people see things differently. I read over the parts I’ve marked, then suddenly stop. What if all the checks to see whether phones are put away leave less time to read the text that matters? It’s my responsibility to keep the lesson moving. I can’t think that a quiet classroom is enough.

I review school budgets for the local government. I lay out the costs of managing devices and the papers on learning support on my desk, and mark them with sticky notes. Is it right to count the cost of putting phones away as spending to help students do better in school? I start to write a note about the budget review, then stop. How can I explain the link between not using phones and being able to learn? The budget can’t make money appear out of nowhere. I worry that spending money on the bags could mean cutting support for students who need help with learning. At the same time, I still can’t tell whether this cost is necessary. Since I decide how the money is divided, I can’t avoid explaining why.

After work, at the evening high school I attend, I take out my notebook and check whether I still have any work messages on my phone. I want to avoid using it during class. But can I really say with confidence, “No matter what happens, I can stay away from work messages”? I take both my work and my studies seriously. As an adult, I want to be responsible for both. In the margin of my notebook, I write what I want to tell the school. Before the bag is closed, I want the door to a conversation to stay open. I don’t want to give away my responsibility for managing how I use my phone, too.

We all want to value the time we spend learning. But even when we want the same thing, what we stand to lose if a decision is wrong—and how much responsibility we must take on—are different. One bag can’t hold everyone’s idea of what counts as “good.” The power to decide how money is spent, the power to shape the classroom, and the responsibility to keep daily life going. Even when people have little say in decisions, the burdens they carry are no lighter. Even if what they need to protect matters deeply, they may not get to take part in the decision. Before we close the bag, are we shutting out even the acceptance someone has not yet found the words to express?

## In one line
A teacher, a school budget reviewer, and a working student each see different risks in locking phones away at school. They all value learning, but their stakes and responsibilities differ, and those with much to protect may have little say.
```

### R2g Standard(X既定)
```
# Putting Away Our Phones—and What Comes Next

Put a phone in a bag and click the lock shut. If only we could lock away classroom problems, too. When the screen goes dark, does learning start by itself? A Japanese teacher, a school budget worker, and a student who works and goes to school all face the same bag. But different alarms go off in each person’s mind.

Before class, I mark parts to discuss with my middle school Japanese class. I look at the lesson plan spread across the teacher’s desk. I think about where to add a check. It would make sure everyone has put their phone away. I want them to focus on the text, not their screens. But I want to protect more than test scores or a quiet classroom. I want time to hear how other people see things differently. I read the parts I marked again, then suddenly stop. What if all these checks leave less time to read the text that matters? It is my job to keep the lesson moving. I cannot think a quiet classroom is enough.

I check school budgets for the local government. I lay out device costs and papers about learning help on my desk. I mark them with sticky notes. Should money for putting phones away count as spending to help students do better at school? I start writing a note about the budget review, then stop. How can I explain the link between not using phones and learning? The budget cannot make money appear from nowhere. I worry that money for the bags could mean less help for students who need help with learning. At the same time, I still do not know if this cost is needed. I decide how the money is shared. So I cannot avoid explaining why.

After work, I take out my notebook at the evening high school I attend. I check if my phone still has any work messages. I want to avoid using it during class. But can I say with confidence, “No matter what happens, I can stay away from work messages”? I take both my work and my studies seriously. As an adult, I want to be responsible for both. I write what I want to tell the school in my notebook’s margin. Before the bag is shut, I want the door to a talk to stay open. I do not want to give up my responsibility to manage how I use my phone, either.

We all want to value the time we spend learning. But even when we want the same thing, a wrong choice can cost each of us different things. We also have different amounts of responsibility to take on. One bag cannot hold everyone’s idea of what is “good.” There is power to decide how money is spent. There is power to shape the classroom. And there is the duty to keep daily life going. Even people with little say in decisions have burdens just as heavy. What they need to protect may matter deeply. Still, they may not get to take part in the decision. Before we close the bag, are we shutting out even the acceptance someone has not yet found the words to express?

## In one line
A teacher, a budget worker, and a working student see different risks in phone bags at school. They value learning, but their duties differ, and those with much to protect may have little say.
```

### R2g Standard(S2版)
```
# Putting Away Our Phones—and What Comes Next

Put a phone in a bag and click the lock shut. If only we could lock away classroom problems, too. When the screen goes dark, does the learning switch turn on by itself? A Japanese teacher, a school budget reviewer, and a working student face the same bag. But different alarms go off in each person’s mind.

Before class, I mark parts to discuss with my middle school Japanese class. I look at the lesson plan spread across my desk. I think about where to add a check that everyone has put their phone away. I want them to focus on the text without worrying about their screens. Beyond test scores, I want more than a quiet classroom. I want time to hear, through words, how other people see things differently. I read the parts I marked, then suddenly stop. What if all the checks to see whether phones are put away leave less time to read the text that matters? It is my job to keep the lesson moving. I can’t think that a quiet classroom is enough.

I review school budgets for the local government. I lay out the costs of managing devices and papers about learning support on my desk. I mark them with sticky notes. Is it right to count the cost of putting phones away as money spent to help students do better at school? I start a note about the budget review, then stop. How can I explain the link between not using phones and learning? The budget can’t make money appear from nowhere. I worry money for the bags could mean less support for students who need help with learning. At the same time, I still don’t know if this cost is needed. Since I decide how the money is divided, I can’t avoid explaining why.

After work, I go to the evening high school I attend. I take out my notebook and check whether I still have any work messages on my phone. I want to avoid using it during class. But can I really say with confidence, “No matter what happens, I can stay away from work messages”? I take both my work and my studies seriously. As an adult, I want to be responsible for both. In the margin of my notebook, I write what I want to tell the school. Before the bag is closed, I want the door to a conversation to stay open. I also don’t want to give up my responsibility for how I use my phone.

We all want to value the time we spend learning. But if a choice is wrong, we each have different things to lose. We also have different amounts of responsibility to take on. One bag can’t hold everyone’s idea of what counts as “good.” There is power to decide how money is spent. There is power to shape the classroom. There is also a duty to keep daily life going. Even when people have little say in decisions, their burdens are no lighter. What they need to protect may matter deeply. Still, they may not get to take part in the decision. Before we close the bag, are we shutting out even the acceptance someone has not yet put into words?

## In one line
A teacher, a budget reviewer, and a working student see different risks in locking phones away. They value learning, but their duties differ; those with much to protect may have little say.
```
