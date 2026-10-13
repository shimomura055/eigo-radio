# COMPARE_REPORT_01: Melos Preview Std統一Prompt x3 / Adv現行Prompt x3 (FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01, Trial)

Status: **USER_DECISION_REQUIRED**(Trial。Production採用・Prompt変更の判断なし。`APPROVED_FOR_PRODUCTION`ではない)

## 0. 条件
- 使用モデル: `gpt-6-luna`(応答model_id実測=全6 call `gpt-6-luna`)、reasoning effort `high`(Production同一。最新原則の例外理由=Production Preview生成との比較可能性)。
- Std Prompt: er070統一Prompt(Family X準拠)。送信prompt全文sha256 = er070と一致(`2b3691e9...6a0831`)。入力=Std Comment 1・2(`a2_support.json`既存)+`std.md`全文。
- Adv Prompt: 現行`b1s.PREVIEW_ROLE`。送信prompt sha256 `e0912dac...6c3a`。`run_support_adv`にmock fnを渡して捕捉したPreview送信promptと一致を検証済み。入力=Adv Comment 1・2(`b1b_support.json`既存)+`r2.md`全文+NOT_NEWS_NOTE。
- 6 takeは全て新規生成(1 take=1 call、max_attempts=1、lint NGでも再生成しない)。lintは全6件OK(違反なし)のため再生成なし。
- Prompt・Comment・原稿・KPは一切変更・再生成なし。TTSなし。

## 1. 入力Comment(両levelで既存のものをそのまま使用)
- Std Comment 1: メロスは、恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式に出るため三日間の猶予を求め、友人を残して出発しますが、遅れて戻れば友人が代わりに死ぬことになっています。
- Std Comment 2: 橋のない川を渡り、道をふさいだ三人から逃げた彼は、午後には足が血だらけになり、岩のそばで立てなくなります。彼には、ここで待つか家へ戻るかの選択が残っています。戻らなければ、友人が代わりに命を失います。
- Adv Comment 1: Listen for what Melos promises before he leaves.
- Adv Comment 2: Melos promised to return, and his friend chose to trust him. What will happen as Melos makes his way back to the city?

(観察: Std Commentは各3文で物語の導入〜中盤の事実をほぼ網羅する。Adv Commentは各1〜2文でPart内容を示唆するのみ。この分量差はPreview側の「重複回避」の余地に影響しうる。後述の安定性結論を参照。)

## 2. Preview全文(省略なし)

### Standard(日本語)
| Take | 全文 | 字数 | 文数 | lint(ja) |
|---|---|---|---|---|
| Take1 | 友人との約束を守ろうとする男の物語です。彼が苦しい状況に向き合う姿を通して、信頼がどのように試されるのか、そして人を信じることにどんな意味があるのかを考えます。 | 80 | 2 | OK |
| Take2 | ある青年と友人は、ある約束をきっかけに、命に関わる厳しい状況に置かれます。二人の間で信頼がどのように試されるのかを通して、約束を守ることの重さを描く物語です。 | 79 | 2 | OK |
| Take3 | 命がかかった状況で、友人を信じる気持ちは、ほかの人の考えにも影響するのでしょうか。メロスと友人、そして支配者が向き合う物語から、信頼について考えます。 | 75 | 2 | OK |

### Advanced(英語)
| Take | 全文 | 語数 | 文数 | lint(en) |
|---|---|---|---|---|
| Take1 | A young shepherd speaks out against a ruler who will not let people speak. This story asks what can happen when someone stands up to power, and whether a ruler can learn to listen. | 34 | 2 | OK |
| Take2 | A young shepherd speaks up to a ruler who will not listen, and the ruler sentences him to death. Listen for what this story shows about speaking up when one person holds all the power. | 35 | 2 | OK |
| Take3 | This story begins when Melos, a young shepherd, speaks against a ruler and is sentenced to die. As you listen, consider what can happen when someone speaks up to a person in power. | 33 | 2 | OK |

### 比較参照(既存、reuse)
| 参照 | 全文 | 規模 |
|---|---|---|
| Std 現行Production(`a2_support.json`) | 結婚式を終えたメロスは、三日目の夜明け前に町へ戻り始めます。帰り道には、橋のない川と、道をふさぐ男たちがいます。川は雨で茶色くなり、流れもとても速くなっています。 | 81字・3文 |
| Std er070 AFTER(単発) | この物語では、友への信頼をめぐって、羊飼いメロスと王が向き合います。メロスの行動を前に王は何を考えるのか、人の心が動くきっかけを追っていきます。 | 72字・2文 |
| Std er067(単発) | 友人の信頼に応えたい思いと、苦しさから逃れたい気持ちの間で揺れるメロスを描いた物語です。人を信じることの重さや、信頼に応える難しさも感じられます。 | - |
| Adv 現行Production(`b1b_support.json`) | This story follows a young shepherd who speaks out against a ruler and is sentenced to die. As he faces a choice that affects someone close to him, what will guide him through this moment of great pressure? | 38語・2文 |

(Std現行Previewは物語の後半(帰路)の場面を描写しており、Std Comment 2と場面が重なる。本タスクの比較対象は新規6 takeであり、現行の評価は行わない。事実の並記のみ。)

## 3. 評価表(8観点。事実ベース、採用判断なし)

### 観点1 興味を引く導入か
- Std: Take1は「約束を守ろうとする男の物語」と一般化した導入で、固有の引きは弱い。Take2は「ある青年」「ある約束」と指示語・不定表現が続き、何の話か具体性に欠ける。Take3は問い(「友人を信じる気持ちは、ほかの人の考えにも影響するのでしょうか」)で始まり、疑問形の引きはあるが、「ほかの人の考え」が誰を指すか文脈なしには不明瞭。
- Adv: 3 takeとも「若い羊飼いが支配者に物申す」という具体的な事象から入り、続けてテーマを問う2文構成。Take3は主人公名(Melos)と死刑宣告を含む。導入の引きは3 takeで同程度。

### 観点2 具体的な状況・問題の提示
- Std: Take1「苦しい状況」(内容なし)、Take2「命に関わる厳しい状況」(内容なし)、Take3「命がかかった状況」+登場人物名(メロス・友人・支配者)。3 takeとも、何が起きているか(誰が何をしたか・何を約束したか)の具体的な出来事の提示はない。具体性はTake3が相対的に高いが、状況は「命がかかった」止まり。
- Adv: 3 takeとも「羊飼い/支配者に声を上げる(speak out/up)」という出来事を提示。Take2・Take3は「死刑(sentences him to death / sentenced to die)」まで提示。ただし友人・約束・期限など物語の中心要素は3 takeとも含まない。

### 観点3 あらすじ化していないか
- Std/Adv: 3+3 takeとも、出来事を時系列で並べるあらすじ形式にはなっていない(2文構成、テーマ提示+問い/考察への誘い)。Std 3 takeはほぼテーマ提示(「信頼」)で、出来事の要約部分自体が乏しい。Adv 3 takeは冒頭の発端(声を上げる→死刑)に限った提示。

### 観点4 ネタバレ
- Std: 結末・転換点・後半展開の先出しなし(3 take)。
- Adv: Take2「sentences him to death」、Take3「sentenced to die」は冒頭の事実(Adv本文Part 1の出来事、Adv現行Previewも同じ事実を含む)。結末の先出しなし。Take1「whether a ruler can learn to listen」は、支配者が変わるかを示唆する表現であり、物語の終盤の展開(支配者の変化)に触れる可能性がある表現(断定はしない。どこまでを「転換点」とみなすかの判断はユーザーに委ねる)。lintのSPOILER語検査は3 takeとも該当なし。

### 観点5 Comment 1・2との重複
- 文単位: 両level・6 takeとも、Comment 1・2と同一/ほぼ同一の文はない。
- 語彙/事実単位: Std 3 takeは「約束」「友人」「命」といったStd Comment 1・2で既出の語・事実を再掲する(Take1: 約束・友人、Take2: 約束・友人・命、Take3: 命・友人)。ただし出来事の再説明ではなく抽象化した言及。Adv 3 takeはComment 1・2で言及される「約束(promise)」「友人(friend)」「帰還(return)」を含まず、語彙重複なし。

### 観点6 自然で聞きやすい文章か
- Std(日本語として): 文法上の誤りなし。Take2は「ある青年と友人は、ある約束をきっかけに」と「ある」が2回続き、指示が曖昧で耳で聞くと印象に残りにくい。Take1・Take2は「〜を通して〜を考えます/描く物語です」の評論的な結び。Take3の「友人を信じる気持ちは、ほかの人の考えにも影響するのでしょうか」は意味がやや取りにくい。
- Adv(英語として): 3 takeとも平易で短く、文法的に自然。Take2の「Listen for what this story shows」、Take3の「As you listen, consider」は聴取指示を含むが、enのlint(聴取指示は検査対象外の設計)はOK。

### 観点7 Take間のばらつき
- Std: 長さは75〜80字(目安80〜110字のうち下限を割るものが2/3)、構成は3 takeとも「前文=状況/問い、後文=信頼についての考察」で一定。焦点は3 takeとも「信頼」。ばらつきは主に具体性(Take3のみ名前・複数人物を出す)と書き出し(平叙/不定表現/疑問)の違い。
- Adv: 33〜35語、構成は「羊飼いが支配者に声を上げる(発端)+テーマを問う」で一定。焦点は3 takeとも「権力への発言(speaking up to power)」。ばらつきは主人公名の有無、死刑の言及有無、聴取指示表現の差のみ。Std以上に3 takeが近い。

### 観点8 Std vs Advの構成・センス
- 構成: Advは「発端の具体事実+問い」、Stdは「テーマ(信頼)+考察への誘い」。Advは出来事から入るのに対し、Stdは3 takeとも出来事の具体性が乏しい。
- 焦点: Advは「権力への発言」(物語の発端)に焦点を当て、Stdは「友人との約束・信頼」(物語の中心)に焦点を当てる。どちらも物語の一側面であり、焦点が揃っていない(両levelで同じ物語の同じ側面を指していない)。
- 長さ・形式: 2文、Std75〜80字/Adv33〜35語でともに「短い導入」の形式要件は満たす。
- Previewとしての役割の揃い: Advは具体的な状況提示を果たしているが、Stdは具体的な状況提示が3 takeとも弱く、役割の達成度が揃っていない(事実としての記述。どちらが良いかの採用判断は行わない)。

## 4. 出力の安定性の結論(断定せず、証拠付き)
- 同一Prompt内の一貫性: Std 3 take、Adv 3 takeとも構成(2文)・焦点・ネタバレ傾向は一貫。Stdは3/3が「信頼」テーマで出来事の具体性が低い、Advは3/3が「声を上げる→死刑(2/3)」で具体事象を含む。Take間の差は小さく、レベル間(Std vs Adv)の差の方が大きい。
- 前回との整合: er067(単発)・er070 AFTER(単発)も抽象的な「信頼」論調であり、今回のStd 3 takeと同傾向。Std統一Promptの出力は、既出2件+今回3件の計5件すべて抽象・評論調(出来事の具体的提示が弱い)。
- 「抽象・評論調はPrompt構造由来か出力の揺れか」: 5/5件で同傾向であり、単なる確率的な揺れとは考えにくい(揺れの場合は具体的出力が混ざることが期待されるが、観察されなかった)。ただし原因をPrompt構造に特定することはできない。交絡要因として、(a)Std Commentが3文×2で物語の発端〜中盤の事実をほぼ網羅しており「Commentと重複しない」制約下で出来事を書く余地が小さいこと、(b)Advと異なる入力量・Prompt文言(Std統一PromptはX由来、theme/problem/valueを短く、question省略可)があること、がある。Comment量とPrompt構造の切り分けには、片方だけを変える追加Trial(今回の禁止範囲外)が必要。今回はその追加Trialは実施していない。
- 今回のサンプルはStd 3件・Adv 3件・メロス1作品のみ。一般化はできない。

## 5. 費用・テスト
`cost_01.json`参照。6 call合計 JPY 0.5652(Guardrail JPY5以内、事前見積JPY約0.9以内)。call別: Std 0.1125/0.1145/0.1029、Adv 0.0788/0.0850/0.0714。単価=gpt-6-luna input $0.10/output $0.50 per 1M(`er006_model_routing_pricing_coverage_test_01.py` L50-52)、USD/JPY=160。
- 検証: `er072_..._test_01.py` 7 PASS / `er062_family_z_writer_01_test_01.py` 64 OK / `er070_..._test_01.py` 23 PASS。
- state_guard(`state_guard_01.json`): run_e2e_02配下+Production py 5本のsha256前後不変(changed=[])。
