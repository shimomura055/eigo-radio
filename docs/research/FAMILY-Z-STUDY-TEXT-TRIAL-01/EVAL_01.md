# EVAL_01(agent機械・目視評価。Fable独立評価は別途。初回出力=`OUTPUT_01_RAW.md`を無編集のまま評価)

## A. 本文との整合性

### A-1 英文引用の逐語照合(機械、`r2.md`との部分文字列一致、curly apostrophe込み)
| # | 位置 | 引用 | 結果 |
|---|---|---|---|
| 1 | P1-1 | One was Jim’s gold watch, handed down from his grandfather to his father, and then to him. | 存在(逐語一致) |
| 2 | P1-2 | Then she caught sight of herself in the mirror. | 存在(逐語一致) |
| 3 | P1-3 | Outside a hair-goods shop, she paused just long enough to catch her breath. | 存在(逐語一致) |
| 4 | P2 | Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers. | 存在(逐語一致) |
| 5 | P3 | How could she buy Jim something worthy of him? | 存在(逐語一致) |
| 6 | P3 | Like Jim, it needed no decoration to prove its worth. | 存在(逐語一致) |

不一致0・部分一致0・欠落0(6/6)。太字内の英語断片のうち本文に無いもの(hand down / catch sight of / catch one’s breath / just long enough to do / worthy of + 人・物 / two foolish young people sat here / which had been handed down)は、見出し語化したKP・型の提示・説明用の再構成であり、「本文の引用」として提示されていない(`which had been handed down`と`two foolish young people sat here`は説明用の言い換えとして明示)。本文の引用と誤認させる箇所なし。

### A-2 日本語訳・文法説明(agent目視)
- 日本語訳(P1×3・P2・P3×2・P4×2): 意味の誤りなし。「必要なだけ立ち止まった」(just long enough)・「手にした」(with gifts…)はやや意訳だが許容。
- 文法説明: 誤りは検出せず。P1-1の「過去分詞が名詞を後ろから修飾=関係節`which had been handed down`の短縮形」、P2の「here先置き+主語後置(場所の倒置)」「with gifts…=状況の付帯句」「they could not use=giftsを修飾する節」、P1-3の「just long enough to do」はいずれも妥当。
- **要Fable確認(断定不可)**: (a) P1-2「視界に入った自分の姿が、次の行動を思いつくきっかけになったことが伝わります」は、本文は`Then she caught sight of herself`の直後に髪の描写が続くのみで、「きっかけ」は本文の字面にない推論(語法説明ではなく物語解釈寄り)。(b) P3「worthyは何かに見合うかどうか、worthは価値そのものに焦点」は一般的語義としては妥当だが、品詞の違い(形容詞/名詞)の説明が中心で「ニュアンス差」と言えるかは評価が分かれる。
- 本文にない事実・出来事の創作: なし(Part 4の回答例は学習者向け意見で、物語事実の主張ではない)。

## B. 学習価値
- **Advanced適性**: 日本語説明は読みやすく平易。Part 2(場所の倒置)はB1〜B2で価値が高い選定。Part 1は3件とも平易で、語法・構造への言及が1〜2点にとどまり深さは浅め。
- **Part 1の深さ/重複**: 下表のとおり音声解説の単純繰り返しではない(いずれも文法・構造の観点を追加)。ただし(1)handの語法(`hand X down to Y`、受動、`pass down`との関係)、(2)sightの名詞用法・`catch a glimpse of`等との差、(3)`catch one's breath`の「息が上がった後」という含意は触れず、「学習上の重要性」(なぜ覚えるべきか)の記述は実質ほぼ無い。

| KP | 既存音声解説(英語) | Part 1の説明(要旨) | 重複判定 |
|---|---|---|---|
| hand down | to pass something to a younger person or a later generation | 過去分詞の後置修飾(=which had been handed down)。家族の中で代々伝わった品 | 意味部分は部分重複、構造観点は新規。単純繰り返しではない |
| catch sight of | to see something suddenly or by chance | `catch sight of+名詞`の形。herselfがofの後。視界に入った自分が行動のきっかけ | 意味は同趣旨(「鏡を意識してじっと見たというより」)、形の説明は自明に近く薄い。やや重複、かつ「きっかけ」は推論 |
| catch one's breath | to pause and breathe normally again after effort | `just long enough to do`の構造、所有格が主語に合わせて変わる | 意味の再説明なし、構造観点のみ。重複なし(ただし表現自体の説明が薄い) |

- **Part 2選定の妥当性**: 本文に`whose love made them the wisest`(関係詞+make O C)、`Each had sold their greatest treasure to buy the other a gift`(each+their、目的のto不定詞、授与動詞の二重目的語)、`Her hair was gone; the combs could not hold it.`(セミコロンによる対句)、`I couldn't let Christmas come without giving you something`(let O V、without -ing)等の候補がある。選定された場所の倒置は妥当かつ学習価値あり。ただし同じ文中の`whose love made them…`(関係詞+使役make)を説明していないのが惜しい。1個のみ選定(上限2)は「無理に2個選ばない」に合致。
- **Part 3選定の妥当性**: worthy of / worth は本文根拠あり・Part 1/2と重複なし。ただし(i)語義が基礎的でAdvanced学習者には既知に近い、(ii)比較対象が「別品詞の別語形」で「似た表現との違い」としては対比が弱い、(iii)本文中のより「ニュアンス差」が活きる候補(`shabby`、`Nothing showy, nothing unnecessary`の省略構文、`foolish`と`wisest`の皮肉、`pressed`/`held`、`treasure`)に比べ選定の優先度は低い。0個にせず選んだ判断自体は不当ではないが、深掘りというより辞書的比較に留まる。
- **無理な解説の有無**: 無理な創作は見当たらない。Part 3がやや「無理にひねり出した」印象(要Fable確認)。Part 2/3が0個のケースは今回発生せず、0個判断の妥当性は検証できていない(1回のみ)。
- **Part 4**: 英語質問・訳・回答例・訳の4点が揃い自然。作品への関連は`gift`の一般論でやや弱い(物語固有の要素の参照なし)。

## C. Production適性
- **1回で実用品質か**: 構造・形式要件(4Part、逐語引用、日本語)は1回で満たした。内容面は「使えるが深さは浅め」。校正・確認を前提にすれば出荷可能な水準に近く、そのままの自動公開は確信が持てない(Fable/ユーザー評価待ち)。
- **確認・修正の手間見積(1記事・1レベル)**: 機械照合(逐語引用)0分(script化可)、日本語訳・文法・ニュアンス妥当性の人手確認 約8〜12分。Std+Advで16〜24分/記事。
- **量産時の再現性の懸念**: (1)Part 2/3の選定が毎回ぶれる可能性(1サンプルのみ、再現性は未検証)。(2)Part 1の深さがKPの種類(慣用句かどうか)に依存。(3)Part 3が「無理に作る」方向に寄る可能性。(4)Prompt非依存の一般的な傾向は本Trialでは判定不能(N=1)。
- **追加費用**: 実測0.230円/Adv 1本(input 1,751/output 2,529[reasoning 1,255]、gpt-6-luna、reasoning未指定)。Std(KP3件、本文がやや短い想定)も同程度とすると約0.45〜0.5円/記事セット=70円の約0.7%。KP5件の記事でも1円未満の見込み。固定審査(引用の機械照合)は追加費用0円。

## Fable判定(委任_02、2026-10-24、詳細=FABLE_EVAL_01.md)
- 要Fable確認1(catch sight ofの解釈): 許容。原作・本文の流れに沿った軽い解釈で、創作ではない。
- 要Fable確認2(worthy of/worth): ニュアンス解説としては弱い(品詞差の説明で、Advanced学習者への価値が低い)。
- Status(Fable): USER_DECISION_REQUIRED(UDR #182)。
