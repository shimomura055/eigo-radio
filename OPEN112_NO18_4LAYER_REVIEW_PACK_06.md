# No.18 4-Layer Discovery Trial Review Pack

管理ID: OPEN-112-NO18-4LAYER-REVIEW-PACK-AND-LOCAL-REWRITE-OPENITEM-06
作成日: 2026-09-04
現在Status: `USER_REVIEW_READY`(このタスクで到達してよい最大Status。`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`ではない)

---

## 1. この資料の目的

[OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05](DECISION_LOG.md)で、A Family 4層Prompt(Layer1 Common Writing Contract / Layer2 A Family Common Skeleton / Layer3 Discovery/Why Focus Module / Layer4 Article-specific Inputs)+ 新規Discovery/Why Focus Moduleを使い、No.18のA2/B1をArticle-onlyでTrial生成した。最終Statusは`VALIDATED`(Trial手続きとして問題なし、という判定であり、記事内容そのものの採否はユーザー判断)。

この資料は、ユーザーがまだ行っていない「Trial記事の内容そのものを、現行承認済みNo.18と読み比べて判断する」ための材料です。以下を1つのMarkdownにまとめました。

- 現行承認済みNo.18(A2/B1)とTrial版No.18(A2/B1)の**全文**
- Main Story/Point One/Point Two/In One Lineごとの対比とClaudeによる差分説明(良い/悪いの断定はしません)
- 4層構造導入による記事上の変化の整理
- Fact Checker/Ledger Deviation/Point Overlap・Value QA等のQA比較
- B1で発生したLocal Rewrite後の意味重複の実例(今回新規Open Item化: **OPEN-113**)

ユーザーはこれを読んで、(a) 4層構造+Discovery/Why Focus Moduleを正式採用するか、(b) B1のLocal Rewrite後重複をどう扱うか、を判断してください。

---

## 2. 比較条件

| 項目 | 内容 |
|---|---|
| Baseline | ユーザー承認済みの現行No.18(`ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R`で生成・採用された記事本文) |
| Baseline格納先(A2) | `er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r/a2/article.md` |
| Baseline格納先(B1) | `er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r/b1b/article.md` |
| Baseline sha256(A2) | `ee2c1ad59dca0d4c38bc5df43f42372ce2c710223916e5222305851d8dbfc104` |
| Baseline sha256(B1) | `cd81f954342063866f50ee8188ff3938a7a84d8afb070b06d9687a60af8bf3dc` |
| Trial | `OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05`で生成した4層Prompt版No.18(A2 run1・B1 run1、各1回のみ) |
| Trial格納先(A2) | `er011_output/open112_a_family_4layer_prompt_trial_05/a2_run01/article.md` |
| Trial格納先(B1) | `er011_output/open112_a_family_4layer_prompt_trial_05/b1b_run01/article.md` |
| Trial sha256(A2) | `5a18d5a6e067d132e8ce623fa2ce22b56dc26d5d3bc54e7d14f28adf5b23279a` |
| Trial sha256(B1) | `49ebae3f7c62e1045434a8df82073f760aebade6e76a81011791a8b29593f640` |
| 変更した変数 | PromptへのDiscovery/Why Focus Moduleブロック追加(1箇所のみの機械的insert、削除0・置換0) |
| 変更していない条件 | Topic/Title/Verified Fact Ledger(同一Ledger)、CEFR難易度指示、Point Role Planning・Point Value QA・Evidence Compression・Fact Checker・Ledger Deviation Checker・Local Rewrite・Directional Fact Precheckのコード・ロジック、使用モデル(`gpt-5.6-luna`)、Production Writer関数(`gen.run_one_pattern()`、無変更のまま呼び出し) |

過去の途中版・未承認版は使用していません。Baseline/Trialとも上記の一意なファイル・sha256で特定しています。

---

## 3. A2 比較

### 3-1. Baseline全文(現行承認版)

# The Notification You Hear Without Looking

A phone does not need to light up in your hand to change a task. A sound may be enough. And in another study, even a silent phone on a desk was linked to lower attention.

A study published in 2022 tested 73 college students. They worked through a letter task. In some trials, they heard a notification sound. In others, they heard a neutral sound. They did not look at or touch a phone.

The result was clear: responses were slower during trials with notification sounds. Brain recordings also showed a larger signal after those sounds. This happened even though the students kept working and did not check a screen.

A second study, published in 2023, tested 42 university students. Their phones were powered off, and no notifications arrived. The researchers compared a phone on the desk with a phone in another room.

Performance was lower when the phone stayed on the desk. The attention score averaged about 100 on the desk, compared with about 109 when the phone was away. Processing speed was also lower on the desk.

Together, these studies show two different moments. A notification can affect a person during a task. A phone can also be linked to lower performance without making a sound.

### The cost you cannot see

Distraction is not always a visible choice. Someone can keep working and still spend more effort to stay with the task. The researchers read the slower responses and larger brain signal as a sign of that extra control. So a person who never checks the screen may still pay an attention cost.

### Muting is not the same as absence

A silent phone is not the same as no phone. The second study suggests that silencing alerts and moving the device may address different problems, although it did not test either action as a solution. The social side matters too: 72% of U.S. teens often or sometimes checked messages or notifications soon after waking. And 56% reported at least one of anxiety, loneliness, or upset when their phone was not nearby.

## In one line…

These studies suggest a quiet lesson: attention can be pulled by a sound, or shared with a phone that never rings.

---

### 3-2. Trial全文(4層Prompt+Discovery/Why Focus Module版)

# The Notification You Never Check Can Still Change Your Focus

A phone can take part of your attention even when you never look at it.

Imagine you are reading or writing. A familiar alert sounds. You do not touch your phone. You keep working. Still, your work may slow down. Two studies examined this hidden change in focus.

A 2022 study tested 73 university students on a visual letter task. Some rounds had a notification sound. Others had a neutral sound. The students did not look at or touch a phone. Their responses were slower when the notification sound played.

The team also measured brain signals. The notification sound produced a larger signal. The researchers interpreted this as extra mental control being used to continue the task.

A 2023 study tested 42 university students with a concentration test. The phone was powered off. It stayed on the desk in one condition and was moved to another room in the other. No notifications arrived.

With the phone on the desk, the average attention score was about 100. In the other room, it was about 109. Processing speed showed the same pattern, with a higher score when the phone was in the other room.

Neither experiment required people to reach for their phones. That is what makes the result surprising.

### Two layers of distraction

The two experiments suggest two layers of distraction. An alert can be an acute interruption. A phone nearby can be a quieter background cost. So "ignore it" is not one single task. Reducing or changing alert sounds may address the first layer, while creating physical distance may address the second.

### The pressure to answer

Checking may involve social pressure, not curiosity alone. A survey found that 72% of U.S. teens often or sometimes checked messages or notifications soon after waking. When they did not have the phone, 56% reported at least one of three feelings: anxiety, loneliness, or upset. A majority felt they should answer quickly. This does not prove a cause. Focus may require clear reply expectations, not only willpower.

## In one line…

Sometimes the hard part is not choosing to check. The alert, the nearby phone, and the pressure to reply may already be shaping the moment.

---

### 3-3. セクション別対比(A2)

**Main Story**

- Baseline: 「音だけで十分」というHook文から始まり、2研究の手続き・結果を淡々と提示。最後に「2つの異なる瞬間」とまとめる。
- Trial: 「見なくても注意の一部を奪われる」というHook文から始まり、同じ2研究を提示した上で、最後に「どちらの実験も、手を伸ばすことを要求しなかった。それが結果を意外にしている」という一文を追加している。

Claudeによる差分説明: 使用しているFact(73名/42名/about 100 vs 109等)はBaseline・Trialで同一。Trialは末尾に、2研究の共通点(「手に取らなくても影響が出た」)を明示的に言語化する一文を追加しており、これは「なぜ意外なのか」を読者に一段階言い換える、Discovery/Whyらしい効果と見える。一方で、この一文はLedger上の個別Factではなく2研究をまたぐ統合的な観察であり、新しい解釈层が加わっている。Fact自体の逸脱はLedger Deviation Checkerで確認されていない(後述QA比較参照)。冗長化は生じていない(Main Story語数はBaseline 203語→Trial 202語でほぼ同じ)。

**Point One**

- Baseline見出し: "The cost you cannot see"(見えないコスト)。「画面を見ない人でも注意コストを払っている」という心理的角度。
- Trial見出し: "Two layers of distraction"(2層の注意散漫)。「音による急性の割り込み」と「そばにあることによる背景的コスト」という2層構造として整理し、「ミュートは第1層、物理的距離は第2層に効くかもしれない」という対策の使い分けを示唆。

Claudeによる差分説明: BaselineのPoint Oneは「見えないコスト」という現象の指摘にとどまるのに対し、Trialは同じ2研究から「2層構造」という一段階抽象化した解釈を導き、対策(ミュート/物理的距離)を層ごとに紐づけている点が明確な違い。これはDiscovery/Why Focus Moduleが指示する「Point One/Twoに別々の"why"角度を持たせる」ことの効果と考えられる(Fact Checkerもこの点を「研究者側の理論的説明であり、記事中ではやや事実のように読める」とREVIEW_REQUIREDで指摘。ただし出典・数値の矛盾ではない)。語数はBaseline 52語→Trial 50語で同程度。

**Point Two**

- Baseline見出し: "Muting is not the same as absence"(消音は不在と同じではない)。ミュートと移動の違いに触れつつ、10代のSNS利用の社会的側面(72%/56%)を提示。
- Trial見出し: "The pressure to answer"(返信への圧力)。同じPew調査の数値(72%/56%)を使いながら、「チェックは好奇心だけでなく社会的圧力かもしれない」という心理的角度に絞り、「これは因果を証明しない」という断り書きと「明確な返信期待が必要かもしれない」という示唆で締める。

Claudeによる差分説明: Baselineは「ミュートと不在の違い」+「社会的側面」の2つの話題を1つのPointに詰め込んでいるのに対し、Trialは「社会的圧力」という1つの角度に絞り、Point Oneの「音・物理的距離」という角度と重複しない設計になっている。TrialのPoint Twoの方が、Point Oneとの役割分離(音/存在 vs 社会的圧力)が明確。ただしTrialは「Focus may require clear reply expectations」という実践的提案を追加しており、これはFact Checkerが「Pew調査は返信期待の明確化が集中力を改善することまでは検証していない」とREVIEW_REQUIREDで指摘した箇所(non-blocking)。語数はBaseline 70語→Trial 66語。

**In One Line**

- Baseline: 「注意は音に引かれる、あるいは鳴らない電話とも共有される」という静かな教訓としてまとめる。
- Trial: 「難しいのはチェックを選ぶことではない。アラート・そばにある電話・返信への圧力が、すでにその瞬間を形作っているかもしれない」と、Point One(音・存在)とPoint Two(社会的圧力)の両方を回収してまとめる。

Claudeによる差分説明: TrialのIn One Lineは、Point One/Twoで提示した2つの角度(物理的/社会的)を明示的に両方回収しており、記事全体の一貫性(Discovery/Whyとしての「なぜ」への収束)がBaselineよりやや強い。語数はBaseline 21語→Trial 25語で目立った冗長化はなし。

---

## 4. B1 比較

### 4-1. Baseline全文(現行承認版)

# Why a Notification Can Steal Focus Before You Check Your Phone

Imagine you are working. Your phone makes a sound. You do not pick it up or even look at the screen. Still, the moment feels different. Research suggests that distraction may begin before checking starts.

Two peer-reviewed studies help explain why. In a 2022 study, 73 university students completed a visual task while either a notification sound or an unrelated comparison sound played. They did not look at or touch a phone. Even so, the sound affected how they handled the task.

A 2023 study examined a quieter situation. Forty-two university students took a concentration test with a powered-off smartphone on the desk or in another room. No notifications were received. This study also found a difference between the two settings.

At first, this seems like a story about willpower. But the studies point to two separate pressures. One comes from the sound. The other comes from the device being part of the workspace. Together, they suggest that "not checking" is not the same as "not being affected." The studies used specific tasks and university students, so they do not show that every phone affects every person in every situation.

Outside the lab, this pull is also part of daily life for many US teens. In a 2018 survey of 743 teens aged 13 to 17, 72% said they often or sometimes checked messages or notifications soon after waking. When their phone was not with them, some reported feeling anxious, lonely, or upset; overall, 56% reported at least one of those feelings. A majority also said they felt a need to reply quickly to texts, social-media messages, or other notifications.

### The hidden cost comes before the check

The key shift is from behavior to effort. A person can keep their hands off the phone and still pay a price on the trial when the sound appears. Responses were slower, and a brain-wave signal linked by the researchers to staying on task became larger. They interpret this pattern as automatic attention capture, not necessarily a deliberate choice to check.

### A quiet phone can still take up space

The second experiment did not compare a ringing phone with a silent phone. It compared a powered-off phone on the desk with that phone in another room. Attention scores were about 100 versus 109, and processing-speed scores showed the same pattern, with lower scores when the phone was on the desk. For work or study, moving the device may address something that muting does not.

## In one line...

A notification may interrupt focus through its sound, while a silent phone may still compete through its presence. Protecting attention may involve not only resisting the urge to check, but also reducing the phone's chance to enter the task.

---

### 4-2. Trial全文(4層Prompt+Discovery/Why Focus Module版)

# Why a Notification Can Break Your Focus Without You Looking

We usually picture distraction as a simple scene: a phone rings, our eyes turn, and a hand reaches for it. But there is a quieter version. Your eyes stay on the work in front of you. Your hand stays away from the phone. Even then, your performance may change.

In a 2022 study, 73 university students completed a visual letter task over many trials. Some trials included a notification sound. Others included a neutral sound. The students did not look at or touch a smartphone. Yet they responded more slowly when the notification sound played.

The researchers also measured brain activity. A brain-wave signal they link to extra effort in controlling attention was larger during notification sounds. They interpret these behavior and brain results as evidence that a notification sound can capture attention without a person's deliberate choice. In their reading, the participant then needs extra effort to stay with the task. That interpretation applies to this experiment and task; it does not describe every phone moment in daily life.

A second study, published in 2023, tested 42 university students. A powered-off smartphone was either on the desk or in another room. No notification arrived in either condition.

Still, the scores were lower when the phone was on the desk. Attention averaged about 100 on the desk and 109 when the phone was elsewhere. Processing speed showed the same pattern: it was also lower when the phone was on the desk.

That leaves us with two quiet forms of disruption: one begins with an alert sound, and the other appears when the phone is simply present. A person may be trying to stay focused, but the task can still be affected under these test conditions.

### Two different targets for a quieter workspace

The two findings point to two different targets. Muting alerts addresses the sound pathway tested in the first experiment. Moving the phone to another room targets the separate effect of the phone being present, as tested in the second. These are not interchangeable fixes: one changes the sound environment, while the other removes the device from the workspace.

### When attention becomes a social signal

Beyond attention, a phone can carry expectations. In a 2018 survey of U.S. teens aged 13 to 17, 72% often or sometimes checked messages or notifications soon after waking. When the phone was unavailable, 56% reported at least one feeling: anxiety, loneliness, or being upset. A majority felt a need to reply quickly. Ignoring an alert may involve pressure, not just attention. **The survey found that a majority of teens reported feeling a need to respond immediately to texts, social media messages, and other notifications.**

## In one line…

A notification is not only something you hear. Focus can also be affected by the phone nearby, while everyday expectations can make ignoring it feel difficult. Protecting attention may mean changing both the workspace and the rules around replies.

(太字は本資料が追加した強調。Local Rewriteによる重複箇所です。詳細は7節)

---

### 4-3. セクション別対比(B1)

**Main Story**

- Baseline: 「Two peer-reviewed studies help explain why」から始まり、2研究の要約後、「'not checking' is not the same as 'not being affected'」という中心的主張、そして一般化への注意書き(「特定の課題・大学生対象なので、あらゆる人・状況に当てはまるとは限らない」)を含む。Pew調査もMain Story内に含めている。
- Trial: 「distractionの典型的シーン」対比から始まり、2研究の要約(研究解釈への注意書きを含む: 「その解釈はこの実験・課題に当てはまるものであり、日常のすべての電話の瞬間を説明するものではない」)で終わる。Pew調査はMain Storyに含めず、Point Twoへ移動。

Claudeによる差分説明: Trialは研究解釈の限界について、Baselineより踏み込んだ断り書き(「この実験・課題に当てはまる」)を明示的に加えており、causal overclaim防止の観点ではやや慎重な書き方になっている。一方、TrialはPew調査をMain Storyから外しPoint Twoへ集約しており、Main Story自体はA2同様「2つの研究」に集中している。語数はBaseline 261語→Trial 279語で微増。

**Point One**

- Baseline見出し: "The hidden cost comes before the check"。「行動から努力への転換」という心理的解釈。
- Trial見出し: "Two different targets for a quieter workspace"。「ミュートは音経路、移動は存在経路」という対策の使い分けに焦点。

Claudeによる差分説明: BaselineのPoint Oneは「気づかぬうちに払っているコスト」という心理側の説明に対し、TrialのPoint Oneは「対策の使い分け」という実務的示唆に寄っている。両者とも同じ2研究のFactを使っており、Ledger逸脱は確認されていない。TrialはBaselineの「A quiet phone can still take up space」(Baseline Point Two相当)の内容を先取りする形でPoint Oneに統合しており、Point Oneの役割がBaselineとTrialでやや入れ替わっている点は留意が必要。語数はBaseline 61語→Trial 58語。

**Point Two**

- Baseline見出し: "A quiet phone can still take up space"。実験の比較設計の説明+「移動はミュートでは対処できない何かに対応するかもしれない」という示唆(Fact Checkerが「消音との比較は直接検証されていない」とREVIEW_REQUIREDで指摘)。
- Trial見出し: "When attention becomes a social signal"。Pew調査(72%/56%)+「返信への圧力」という社会的角度に完全に切り替えている。ただし7節で詳述する意味重複が発生。

Claudeによる差分説明: 最も構成が変わったのはPoint Twoで、Baselineが「実験の比較設計の掘り下げ」であるのに対し、TrialはPew調査を用いた「社会的圧力」という、Main Story・Point Oneとは異なる新しい角度を導入している。これはA2同様、Discovery/Why Focus Moduleが意図した「Point Twoに別角度を持たせる」設計と整合する。しかし、Local Rewriteの副作用により、Point Two内で「即時返信の必要性」への言及が実質2回現れ、語数もBaseline 63語→Trial 81語と目立って増加している(7節参照)。

**In One Line**

- Baseline: 音による割り込みと、存在による競合の両方に触れ、「チェックを我慢するだけでなく、電話が入り込む機会を減らすことも関わる」とまとめる。
- Trial: 「通知は聞こえるものだけではない」とし、そばにある電話(Point One)と日常の期待(Point Two)の両方を回収し、「ワークスペースと返信ルールの両方を変えることかもしれない」とまとめる。

Claudeによる差分説明: 両者ともPoint One/Twoの内容を回収する構成だが、TrialはPoint Twoの「返信ルール」という表現を明示的にIn One Lineへ反映しており、社会的圧力という新しい角度がタイトルから結論まで一貫している。語数はBaseline 39語→Trial 39語で同じ。

---

## 5. 4層構造による主な変化

前提の再掲: Trial Promptで既存Prompt(`COMMON_BLOCK_TEMPLATE`)への変更は**削除0・置換0・順序変更なし**であり、追加されたのは新規Discovery/Why Focus Moduleブロック1箇所のみです(機械的な文字列再構成テストで確認済み、[phase_a_result.json](er011_output/open112_a_family_4layer_prompt_trial_05/audit/phase_a_result.json))。

その上で、出力記事上に観測された変化を整理します(A2/B1共通の傾向)。

| 観点 | 傾向 |
|---|---|
| 「なぜ？」への焦点 | Baselineも「なぜ」の要素はあったが、Trialは2つの独立した実験結果から「2層(acute/background)」「2つの標的(sound pathway/presence)」のような、より明示的な因果構造の言語化が見られた |
| Main StoryとPointsの役割分離 | Trialは概ねPoint One=物理的/心理的メカニズム、Point Two=社会的文脈、という役割分離がBaselineよりやや明確(特にA2) |
| psychological/social/practical angleの出方 | Point Oneが心理・メカニズム寄り、Point Twoが社会的圧力寄りという分担が両レベルで一貫して出現 |
| Evidenceの統合解釈傾向 | 2研究をまたいだ「2層」「2つの標的」という統合的フレーミングがA2・B1双方の共通パターンとして出現。Fact CheckerはA2でこれを名指しでREVIEW_REQUIRED扱い(6節参照) |
| causal overcloim傾向 | 明確な因果の言い過ぎ(例: 「XがYを引き起こす」と断定)は生成物には見られない。ただし「対策の効果」を示唆する一文(Trial B1「moving may address something muting does not」相当の表現、A2「Focus may require clear reply expectations」)がBaseline・Trial双方に見られ、Trial側でもFact CheckerがREVIEW_REQUIRED(non-blocking)として指摘している |

---

## 6. QA比較

Baseline側は当時のQA結果ファイル(21R生成時点)、Trial側は今回のTrial実行結果を使用しています。いずれも同一の既存QA/Validatorコードを経由しています(Trialでコード変更なし)。

| QA項目 | Baseline A2 | Trial A2 | Baseline B1 | Trial B1 |
|---|---|---|---|---|
| Fact Checker verdict | `PASS` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` |
| Fact Checker指摘件数(unsupported_specific_claims) | 0件 | 3件 | 3件 | 5件 |
| Fact Checker: 事実矛盾(contradictions) | 0件 | 0件 | 0件 | 0件 |
| Ledger Deviation overall_status | `LEDGER_COMPLIANT`(逸脱0) | `LEDGER_COMPLIANT`(MINOR 1件: "peer-reviewed"という属性追加) | `LEDGER_COMPLIANT`(MINOR 1件: Hook扱い) | `LEDGER_COMPLIANT`(MAJOR 1件→Local Rewriteで解消、最終0件) |
| Directional Fact Precheck | 記録なし(21R実行時は本チェック未導入または未記録) | `PASS` | 記録なし(同上) | `DIRECTION_REVIEW_REQUIRED`(2件、既知の非決定的パターン、`conflicts`空) |
| Point Overlap QA(lexical) | 比較不可(Baseline側の同一形式retry logは存在するが、初回で`flagged=false`) | 初回`value_qa_flagged=true`→Diagnostic Full Retry 1回で解消 | 初回`flagged=false` | 初回`lexical_flagged=true`→Diagnostic Full Retry 1回で解消 |
| Point Value QA | `PASS`(初回) | 1回NG→Retry後`PASS` | `PASS`(初回) | `PASS`(Retry後) |
| Evidence Compression(Lossless Editor) | 適用済み(Pattern A+Precision、21R時点でPRODUCTION_WIRED) | 適用済み(同一ロジック) | 適用済み | 適用済み |
| CEFR(A2/B1)難易度指示 | 同一の`A2_KAI1_INSTRUCTION`/`B1_B_DIRECT_INSTRUCTION` | 同一(Prompt無変更) | 同一 | 同一 |
| word_count | 346語 | 343語 | 424語 | 457語 |
| Point Two語数(目標25-70語) | 70語(tolerance内) | 66語(tolerance内) | 63語(tolerance内) | **81語(tolerance超過)** |
| total_within_soft_range | true | true | **false**(Baselineも実は超過) | false |
| 記事全体retry回数 | 記録なし(比較不可) | 1回 | 記録なし(比較不可) | 1回 |
| Local Rewrite回数 | 0回 | 0回 | 記録なし(比較不可、当時のMAJOR有無は不明) | 1回(1件のMAJOR、2 attempt) |

比較不可としたセルは、Baseline生成時点(21R)のログに同一形式の記録が存在しないか、当時本チェック自体が未導入だったための「比較不可」であり、推測では埋めていません。

---

## 7. B1 Local Rewrite重複実例

**今回最重要の確認事項です。**

Trial B1のLedger Deviation Checkerが、以下の文をMAJOR逸脱として検出しました。

- **Local Rewrite対象文(逸脱と判定された元の文)**: `"Clear response windows could ease it."`
- **判定理由**: 調査は10代の多数派が即時返信の必要を感じると報告しただけで、明確な返信時間帯を設けることでその圧力が軽減されることは検証していない(Ledgerにない因果的含意の追加)。

Local Rewriteは2回書き換えを試みました。

| 試行 | 書き換え文 | Ledger再判定 |
|---|---|---|
| 1回目 | "Clear response windows might help ease that pressure, although this survey did not test that possibility." | `LEDGER_DEVIATION`(まだ不十分) |
| 2回目(採用) | **"The survey found that a majority of teens reported feeling a need to respond immediately to texts, social media messages, and other notifications."** | `LEDGER_COMPLIANT` |

この2回目の書き換え文が、**Point Two内に既にあった以下の文とほぼ同じ意味内容**になっています。

> 既存文(Point Two冒頭付近): "A majority felt a need to reply quickly."

両文とも「10代の多数派が即時返信の必要を感じている」という同一の趣旨を述べており、Point Two 1つの中でほぼ同じ内容が2回現れる結果になりました。

- Point Two語数: **81語**(推奨25〜70語のtolerance込み範囲を超過)
- なぜ重複と見えるか: Local Rewriteは書き換え文がLedgerに準拠するかは検査しますが、**同じPoint内の他の文と意味が重ならないか(非冗長性)は検査しません**。今回はLedger準拠を優先した結果、既存文と内容が重なる代替文が選ばれました。
- Fact Safety面: 逸脱ではない(`LEDGER_COMPLIANT`)、事実誤りでもない。あくまで冗長性・聞きやすさの問題です。

詳細ログ:
- [`b1b_run01/audit/local_rewrite_results.json`](er011_output/open112_a_family_4layer_prompt_trial_05/b1b_run01/audit/local_rewrite_results.json)
- [`b1b_run01/audit/local_rewrite_cycles.json`](er011_output/open112_a_family_4layer_prompt_trial_05/b1b_run01/audit/local_rewrite_cycles.json)
- [`b1b_run01/ledger_deviation.json`](er011_output/open112_a_family_4layer_prompt_trial_05/b1b_run01/ledger_deviation.json)
- [`b1b_run01/length_report.json`](er011_output/open112_a_family_4layer_prompt_trial_05/b1b_run01/length_report.json)

---

## 8. Local Rewrite問題と4層設計を分離して説明

この重複は、**4層Prompt導入そのものの直接原因とは確認されていません。**

実際の因果関係:

```
Ledger Deviation(MAJOR: "Clear response windows could ease it.")
  → Local Rewrite発火(既存の全Editorial Type共通の仕組み、Trial固有ではない)
  → 書き換え後、同じPoint内の他文との意味重複を再検査するステップが既存Local Rewriteに存在しない
  → 冗長化(Point Two 81語、tolerance超過)
```

このMAJOR逸脱自体は、Trialが新たに導入したDiscovery/Why Focus Moduleの文言とは無関係に、Writerが「Clear response windows could ease it.」という、Ledgerで検証されていない対策効果を書いたために発生しました。このパターンはBaseline(現行Production)でも同じ種類のMAJOR逸脱が起きれば再現しうる、既存Local Rewrite機構自体の限界です(新規Open Item **OPEN-113**として登録済み、[OPEN_ITEMS.md](OPEN_ITEMS.md)参照)。

したがって、

- **A Family 4層設計(Discovery/Why Focus Module)の採否**
- **Local Rewrite後の重複対策の採否**

は、分けて判断できます。前者を採用しても、後者の対策は別タイミングで検討可能です。

---

## 9. ユーザー判断ポイント

### A Family 4層構造について

- Baselineより読み物として良い/同等/悪いか(3節・4節の全文・セクション別対比を参照)
- Discovery/Whyとして自然か(「なぜ意外なのか」「2層/2つの標的」という整理は自然に感じるか)
- 「なぜ？」への理解が深まるか
- Point One/Twoの役割が明確か(心理・メカニズム側 vs 社会的側、という分担は妥当か)
- 解釈が強すぎないか(Fact Checkerの`REVIEW_REQUIRED`指摘、5節・6節を参照)
- A2/B1両方で採用したいか、どちらか一方のみか

### Local Rewrite重複について

- 今回のB1 Point Two重複(7節)が実際に気になるか
- 音声化した場合に許容できるか
- 今後量産前に修正必須(OPEN-113をBlocking扱いに格上げ)とするか
- 今のままOpen Itemとしてdeferしてよいか

---

## 参照元

- [DECISION_LOG.md](DECISION_LOG.md) — `OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05`エントリ(VALIDATED判定の詳細)
- [OPEN_ITEMS.md](OPEN_ITEMS.md) — `OPEN-113`(Local Rewrite Post-Rewrite Intra-Point Redundancy Check、新規登録)
- [er011_output/open112_a_family_4layer_prompt_trial_05/](er011_output/open112_a_family_4layer_prompt_trial_05/) — Trial全ログ・runtime evidence
- [er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r/](er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r/) — Baseline(現行承認済みNo.18)一式
