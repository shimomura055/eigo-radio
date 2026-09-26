# NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-02_REPORT.md

管理ID: NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-02(Sonnet実行、2026-09-26)

Production実装ではない。Trialのみ、最大分類VALIDATED、文章生成まで
(3分割・Comment・scaffold・TTS・assemble・E2E・Production wiring禁止)。
Production Prompt/moduleは一切変更していない(既存定数・関数のimport・
流用のみ)。Control/B1の再生成はしていない(Trial-01出力のコピー再掲)。

## §1 目的

Trial-01のB(Selected Fact Brief、7 Fact)でも、「Factとして正しいが
中心Storylineと直接つながらない情報」(従業員約半数・opt-out、確認範囲の
注意書き等)が残り、Writerが渡されたFactを全部使う傾向が確認された。
本Trialでは、より厳格な2つのFact選定基準——**B2(因果必須基準、目安
4-6件)**/**B3(最小核基準、目安3-5件)**——でBriefを作り直し、
Control(現状相当)・B1(Trial-01のB)と4条件で比較する。

## §2 条件と入力差(Fact件数、Brief全文)

Writer Prompt本体(P7)・model/effort・Original→R1→R2のRevision指示・
English Adaptation prompt本体は4条件で完全同一(Trial-01と逐語同一)。
差は[ニュース]欄へ挿入する素材のみ。

| 条件 | 由来 | Fact件数 | 素材文字数 |
|---|---|---|---|
| control | Trial-01出力の再掲(新規生成なし) | 実質3件相当 | 209字 |
| b1 | Trial-01出力(b_selected_brief)の再掲(新規生成なし) | 7件(003/006/007/008/009/010/018) | 3,216字 |
| b2_causal | 本Trial新規(因果必須基準) | 5件(003/006/008/009/010) | 2,213字 |
| b3_minimal | 本Trial新規(最小核基準) | 4件(006/008/009/010) | 1,816字 |

Core Storyline(参照、固定文として押し付けない): 「Museが電話代行する→
AIだと気付かれると切られることがある→人間スタッフへ引き渡す→人間介在
によるprivacy/disclosure問題→Metaが機能を一旦戻す」。

Brief全文: `er015_output/family_x_writer_fact_selection_trial_02/
{b2_causal,b3_minimal}/writer_input.md`。

## §3 Fact選定テスト表(全18 Fact、Test1-4 + B2/B3採否)

全文は `er015_output/family_x_writer_fact_selection_trial_02/
fact_selection_{b2,b3}.md` に保存(各ファイルに同一の18 Fact全件表+
条件別の採否理由を記録)。要旨:

- 因果チェーンの核4 Fact(MUSE-006[人間への引渡]・008[なぜ切られたか]・
  009[プライバシー懸念]・010[ロールバック])はB2・B3とも採用(Test1で
  「消すと理解できない」に該当する唯一のFact群)。
- MUSE-003(電話機能の具体例)は境界的Factと明記した上で、B2は「何が
  起きたか」の具体性を担保する目的で採用、B3(最も厳しい最小核基準)は
  MUSE-006自身の文言で核が壊れないため除外。
- MUSE-007(規模・約半数・opt-out)は、ユーザー指示で明示された再評価対象。
  4テストを厳格に適用した結果、B2・B3とも除外(Trial-01のB1では採用して
  いたが、本Trialでは方針を変更)。
- MUSE-018(スコープ注意書き)も同様に、核の因果チェーンには使われない
  ため厳格には除外対象。ただし「削ると過度な一般化のリスクがある」という
  既知のトレードオフをfact_selection_b2/b3.mdに明記した上で、実際に
  生成結果で過度な一般化(drift)が起きるかを§8で客観的に確認した
  (結果: 起きなかった、§8参照)。

## §4 Control全文(再掲)

`er015_output/family_x_writer_fact_selection_trial_02/control/{r2.md,
english.md}`(Trial-01出力のコピー、無変更)。

日本語R2(841字)要旨: 「AIに電話を任せたら舞台袖から人間が出てきた」
という舞台メタファー。English(404語)も同旨。**「なぜ人間が必要だったか」
(AIだと分かると切られる問題)を説明するFactが素材に含まれておらず、本文
でも「状況が難しくなると」としか書かれていない**(§7-2の因果表参照)。

## §5 B1全文(再掲)

`er015_output/family_x_writer_fact_selection_trial_02/b1/{r2.md,
english.md}`(Trial-01出力のコピー、無変更)。

日本語R2(910字)要旨: 「AI電話の"ラスボス"は、AIだと気づく人間だった」
というゲーム的メタファー。English(414語)。7 Fact全て使用、因果4段は
全て揃っている。

## §6 B2(因果必須基準)全文

日本語Original/R1/R2、English全文は
`er015_output/family_x_writer_fact_selection_trial_02/b2_causal/
{original.md, r1.md, r2.md, english.md}` に保存。

日本語R2(1,050字)要旨: 「AIに電話を任せたら、舞台袖から人間が出てきた」
という舞台メタファー(Controlと類似の比喩系統だが、因果4段が全て揃って
いる点が異なる)。English(**503語、目標280-420を約20%超過**)要旨:
Museの電話機能の具体例(ヘアカット予約・在庫確認・見積り)→AIだとバレて
切られる問題→人間コンシェルジュへの引継ぎ→プライバシー懸念→
副社長によるロールバック、の順で因果チェーンが明示的に閉じている。

## §7 B3(最小核基準)全文

日本語Original/R1/R2、English全文は
`er015_output/family_x_writer_fact_selection_trial_02/b3_minimal/
{original.md, r1.md, r2.md, english.md}` に保存。

日本語R2(871字)要旨: 「AIが電話すると切られる。そこでMetaが呼んだ
"本物の人間"」。English(**390語、目標280-420内**)要旨: 電話機能の
具体例は含まれず(MUSE-003を除外したため一般論のみ)、AIだとバレて
切られる問題→人間コンシェルジュへの引継ぎ→「常に人間だったわけでは
ない」という自発的な注記(MUSE-018を与えていないが同趣旨の文をWriterが
自ら生成)→プライバシー懸念→ロールバック、の順。

## §8 客観比較表

全文は `er015_output/family_x_writer_fact_selection_trial_02/
comparison.md` に保存(9節構成: Fact件数/必須Fact欠落/Storyline外混入・
drift/語数・読みやすさ/水増し・比喩/因果・説明記事化/Storytelling所見/
QCD/総括)。主要な客観差分:

| 指標 | control | b1 | b2_causal | b3_minimal |
|---|---|---|---|---|
| Brief Fact数 | 3相当 | 7 | 5 | 4 |
| 実使用Fact数 | 3相当 | 7/7 | 5/5 | 4/4 |
| 必須4段欠落 | **1件(なぜ[N1])** | 0件 | 0件 | 0件 |
| Storyline外Fact混入 | 0 | 0 | 0 | 0 |
| Fact drift | なし | なし | なし | なし |
| English語数 | 404(○) | 414(○) | **503(×、+83語)** | 390(○) |
| FK概算(簡易計算) | 8.4 | 7.1 | 7.4 | 6.9 |

**採否判断は書かない(ユーザー試読前提)。**

## §9 参考所見(Storytelling等、断定なし)

- Controlは比喩(舞台/役者)が一貫しているが、「なぜ人間が必要だったか」
  という理由が欠けており、比喩が理由説明の代わりになってしまっている
  (Trial-01でも同様の所見)。
- B1はタイトルの比喩(「Final Boss」)が本文で展開されず、題名と本文の
  トーンがやや乖離(Trial-01 REPORT §10と同様)。
- B2はB1より少ないFact数(5件)にもかかわらず語数が最多(503語)となった。
  本文を読むと、「なぜ切られたか」という因果点を段落5・6で異なる言い回し
  により2回説明している箇所があり、これが語数超過の一因である可能性が
  ある(参考所見、断定なし)。Fact数の多寡と語数超過が単純比例しないことを
  示す一データ点。
- B3は最少Fact数(4件)だが、MUSE-018(スコープ注意)を明示的に与えなくても、
  MUSE-006自身の「一部の電話依頼」という文言から、Writerが「常に人間
  だったわけではない」という同趣旨の注記を自発的に生成した。これは
  「018を削ると過度な一般化のリスクがある」という懸念(§3参照)が、
  少なくとも今回の1回の生成では顕在化しなかったことを示す一データ点
  (1回のみの観測であり、再現性は未検証)。

## §10 QCD

- Quality: b2_causal/b3_minimalの新規8 call(Original→R1→R2→Adaptation
  ×2条件)全て成功。STRUCTURE_INVALID・空応答等の異常なし。Control/B1は
  0 call(コピー再掲のみ、`SOURCE_NOTE.md`参照)。
- Cost: 実測 **¥2.28**(上限¥20の約11.4%)。
  `er015_output/family_x_writer_fact_selection_trial_02/cost.json`保存。
- Delivery: 単一セッションで完結(1管理ID・初回のみ、Fableへの差し戻し
  なし)。

## §11 Sonnet仮分類(最大VALIDATED)

4条件とも Runtime evidence 取得済み。B2・B3はいずれもControlの弱点
(因果の「なぜ」段の欠落)を解消し、B1と同じく因果4段(なぜ→何が起きた→
結果→結論)を全て満たした。B2はFact数を7→5へ絞ってもStoryline外混入
0件・drift無しを維持したが、English語数目標(280-420)を503語で超過した
(B1[414語]・B3[390語]は目標内)。B3はFact数を4件まで絞っても因果4段の
欠落は生じず、MUSE-018を与えずとも同趣旨の注記をWriterが自発的に生成した
(1回の観測)。

「B ≥ Control」的な採用最低条件の考え方をB2/B3双方に当てはめると、
Fact completeness(必須4段の欠落数)ではB2・B3ともControlを上回る
(0件 vs 1件)。詰め込みの少なさでは、B3(4 Fact、語数390で目標内)が
B1(7 Fact、414語)・B2(5 Fact、503語で目標超過)より優位。B2は
Fact数を絞ったにもかかわらず語数超過という新たな客観的弱点が今回
確認された。

Sonnet暫定分類: **VALIDATED**(Trial範囲内。1テーマ1回のみの実行であり、
他テーマでの再現性・複数記事での安定性は未検証。B2の語数超過が本条件
固有の傾向か偶発的かも未検証。Production採用はユーザーの正式承認
[APPROVED_FOR_PRODUCTION]が必要)。

## §12 Fable評価

[Fable記入]

## §13 分類(Fable最終判断)

[Fable記入]
