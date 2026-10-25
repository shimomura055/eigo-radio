# COMPARISON_06(Part 2: Trial-04 / Trial-05 / Trial-06 の選定並置。無編集の事実のみ)

管理ID: 委任_11。**Step A''が事前登録基準で不合格のため、終了条件(PREREGISTERED_CRITERIA_06 §4)によりStep Bは未実行。完成形(学習者向けPart 2全文)の並置は作れていない。**学習者向けの完成形Part 2は`OUTPUT_04_<work>_r1_USER.md`(Trial-04。Part 2は事実上Trial-04の選定による)を参照。開発者向け記録は`OUTPUT_06_<work>_r<n>_STEPA_DEV.json`(`rule_selected.records`)。
Before=Trial-04 r1(Step A、相対評価)/ Trial-05(Step A'、tier/rank)。After=Trial-06(Step A''、分類のみ+決定論規則)。[core]=中核 [either]=どちらでも可 [outside]=許容集合外。

| 作品 | Trial-04 r1 | Trial-05(A') | Trial-06 r1 | r2 | r3 |
|---|---|---|---|---|---|
| 開いた窓 | P23 `The dead were coming towards the house.`(the+形容詞=基礎) | **P21** 5/6標本・r5は0件 | P21 INV[core], P12 FRONT[outside] | P12 FRONT[outside], P29 HEAVY[either](P21はresolve失敗で脱落) | P21 INV[core], P12 FRONT[outside] |
| イグ・ノーベル賞 | P3 + P11 | r1 P5,P4 / r2 P5,P4 / r3,r4 P5 / r5 P4 / r6 0件 | P4 CLEFT[core], P5 CMP[core] | P8 CLEFT[core], P5 CMP[core] | P4 CLEFT[core], P5 CMP[core] |
| 賢者の贈り物 | P30 | r1 P30,P22 / r2 P16(使役動詞=SPEC定義の欠陥),P22 / r3 P30 | P22 INV[core], P5 FRONT[outside] | P4 POSTMOD[core], P1 ELL[outside] | P22 INV[core], P2 ELL[outside] |
| 猿の手(Trial-05ホールドアウト→06開発用) | — | r1 P24 / r2 0件 / r3 P22 | P24 INV[core], P1 FRONT[outside] | P24 INV[core], P8 FRONT[outside] | P24 INV[core], P8 FRONT[outside] |
| 告げ口心臓(06新ホールドアウト) | — | — | P8 INV[core], P17 FRONT[either] | P8 INV[core], P17 FRONT[either] | P8 INV[core], P17 FRONT[either] |
| 二十年後(06平易な本文) | — | — | P8 FRONT[outside], P23 ELL[either] | P8 FRONT[outside], P15 ELL[outside] | P8 FRONT[outside], P1 POSTMOD[outside] |

観察(事実): Trial-05で問題だった「0件標本」「基礎文(使役動詞)の混入」は解消(0件標本0・基礎のみ選定0)。一方、新しく「許容集合外の2件目」が4作品で出現した(EVAL_06 §3)。

## 英文逐語(Trial-06で選ばれた文。本文側の文字列)
- 開いた窓: P21 `Across the quiet garden came a young voice:` / P12 `Before Framton could reply, her aunt hurried into the room.` / P29 `Inventing convincing stories at a moment’s notice was Vera’s speciality.`
- イグ: P4 `If you were expecting a fancy latte, what you got was a map of molecules.` / P5 `The crystals contain more than three times as much energy as the same weight of milk from several kinds of mammals.`(先頭、途中以降は`OUTPUT_06_ig_nobel_r*_STEPA_DEV.json`の`rule_selected`) / P8 `What’s more interesting is the idea of turning nutrients into crystals and storing them away.`
- 賢者: P22 `Inside were the tortoise-shell combs she had so often admired in a shop window.` / P4 `One was Jim’s gold watch, handed down from his grandfather to his father, and then to him.` / P5 `Then, before she could change her mind, she pulled on her coat.` / P1 `Still the same.` / P2 `She had saved every penny she could.`
- 猿の手: P24 `Then came a soft knock.` / P1 `Beside them, Mrs. White smiled over her knitting.` / P8 `After their visitor left, Herbert laughed.`
- 告げ口心臓: P8 `From the bed came a small groan of terror.` / P17 `Calm and confident, he sat directly above the hidden body.`
- 二十年後: P8 `Before we parted, we promised to meet here at ten tonight, whatever happened.` / P23 `Twenty years can change a man, but not the shape of his nose.` / P15 `Once, he took out his watch, then slipped it away again.` / P1 `Bob stood in the doorway of a closed hardware store, sheltered from the rain.`
