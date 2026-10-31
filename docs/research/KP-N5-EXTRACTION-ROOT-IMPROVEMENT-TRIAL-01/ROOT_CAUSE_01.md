# ROOT_CAUSE_01 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_01(2026-10-31)

ユーザー原文=`docs/pm/delegation_log/2026-10-31_KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01_USER.md`(§2 原因究明5項目)。前提=`docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/AUDIT_01.md`(OPEN-631)。
Status=**原因究明完了(確度は項目ごと)・Production変更0**。probe script=`tools/probe_extract_01.py`・`tools/pool_pick_probe_01.py`・`tools/dict_seed_probe_01.py`(Trial専用、Production module/Prompt/閾値/Gate無編集、メモリ上でprompt文字列を作るのみ)。証跡=`ev01/`。費用=**¥9.45 / Cap ¥25(止め線¥20)**(`ev01/cost_summary.json`)。
使用モデル: 抽出probe・SEL=`gpt-6-luna`(Production既定=B1_SUPPORT/SEL。`probe_extract_result_*.json`の`model`)。評価目的で旧/下位モデルは使っていない(最新世代系。PM_GOVERNANCE 25節)。

## 0. 結論(先に)

1. **`put away`/`leave out`/`in the way`/`in sight`は「モデルが認識できない」のではない。** 同じモデル・同じ本文で、Promptを「難易度・学習価値で絞らず網羅列挙」に変えるだけで、4表現すべてが3/3で抽出された(L3。`put away`は`put away`/`put it away`/`put that away`の3形を返す)。分離形(`put it away`)・受動(`it put away`)も連続一致規則(条件1)の下で抽出できる=**連続一致規則との衝突仮説は棄却**。
2. **主因は、抽出Promptが「網羅(recall)」と「価値順位付け(precision)」を1つのPromptに混ぜ、かつ小さな件数枠(B1=14個、P7=7個)で出させていること。** 基本語だけの句動詞(`put away`/`leave out`)は価値順位で常に下位になり、枠が埋まって出ない。`in the way`/`in sight`は条件4・5(上級者向け優先・易しい表現の除外)で落ちる(条件除去で3/3)。`put away`は条件を除去しても枠(14)に入らない(L1 0/3)が、枠を30に広げると2/3、網羅列挙(上限40)で3/3。
3. **抽出が成功しても、pick(難易度順→上限7件)で落ちる**(別の層の取りこぼし)。網羅プールにするとkeepが17〜20件に増え、難易度順の上位7件に`put it away`/`put away`(SELが2回とも`easy`)は入らない。SELの難易度ラベルは同一表現でも実行ごとに揺れる(`turn into an interrogation` easy/upper、`in sight` upper/easy)ので、難易度順は不安定な基準で順位を決めている。
4. 繰り返し(`put away`6箇所、`leave out`6箇所、`in sight`5箇所)という**本文中心性の信号は、抽出Promptにもpickにも使われていない**(`er138_kp_n5_generalization_01.py:316-324`、`:950-961`に出現回数の条件なし)。

確度: `in the way`/`in sight`=条件4・5が主因(**高**: L1 3/3 vs 本番方式0/9以上)。`put away`/`leave out`=件数枠+価値順位付けの混在(**中〜高**: L1 0/3、L2 2/3・1/3、L3 3/3、L5 3/3の整合する4点。枠サイズだけを単独で操作した対照は無く、「枠の内側での順位」を直接観測したわけではない=中)。pick側の欠落=**高**(poolpick 2回で再現、R0規則の仕様どおりの帰結。ただしSEL標本は2)。

## 1. 「抽出されない」(i)と「抽出後に落ちる」(ii)の分離表(ユーザー原文§2)

対象: Family X untidiness Advanced(b1b)本文(sha256=937862fe…、AUDIT_01 §1と同一)。S1/S2=網羅列挙L3の標本1/2のプールをSEL(無変更)に1回ずつ通した結果(`ev01/poolpick_untidi_b1b_L3_1.json`・`…_2.json`)。

| 表現(本文箇所数) | (i)抽出段: 本番方式(P7 call1/B1/補完)の抽出率 | (i)抽出段: 変種の抽出率(本probe, N=3) | (ii)抽出後: SEL(cls/難易度/keep) | (ii)pick(上限7件、難易度順R0) |
|---|---|---|---|---|
| `put away`(6) | 0/11(P7 0/5・B1 0/4・補完0/2。AUDIT_01 §3) | L1(難易度条件なし・14個) 0/3 / L2(同・30個) 2/3 / **L3(網羅列挙) 3/3** / **L5(句動詞全箇所) 3/3** / L4(3分割) 3/3 | S1: `put it away` C easy keep、`put away`・`put that away`は重複扱いでkeep=False。S2: `put away` C easy keep | **落ちる 2/2**(easy。S1:keep17件、S2:keep20件) |
| `in the way`(1) | P7 0/5・B1 0/4・補完1/2 | **L1 3/3** / L2 3/3 / L3 3/3 / L5 0/3(句動詞でない=想定どおり) | `something in the way` C upper keep(S1・S2とも) | **採用 2/2**(upper) |
| `leave out`(6) | 単体0/11(B1は`working things left out`を3/4) | L1 0/3 / L2 1/3 / **L3 3/3** / **L5 3/3**(`leave it out`) | S1: `leave it out` **F easy**(keepでない)、`working things left out` F。S2: `left out again` C upper keep(題名句。`leave out`の用法とは別の意味単位) | S1:対象外(F)。S2:`left out again`が採用 |
| `in sight`(5) | P7 0/5・B1 1/4 | **L1 3/3** / L2 3/3 / L3 3/3 / L5 0/3 | S1:C upper keep、S2:C **easy** keep(ラベル揺れ) | S1:採用、S2:落ちる(easy)=**1/2** |
| `force away`(1) | 0/11 | L5で`force it away`を返す(想定内) | **F**(S2。AUDIT_01と同じ) | 対象外(意味判定による除外=妥当) |

読み方: **(i)の欠落は「Prompt枠・条件」の問題、(ii)の欠落は「難易度順pick+SELラベルの揺れ」の問題で、別個に起きる**。`put away`は(i)(ii)の両方で落ちる(だから条件5を外すだけでは直らなかった)。`in the way`は(i)だけが原因(抽出されれば(ii)は通る)。`in sight`は(i)が主、(ii)が揺れ要因。`leave out`は(i)に加え、SEL側で`leave it out`がF判定になる標本がある(AUDIT_01の強制投入ではC・keep 3/3だった=SEL判定がpool構成で揺れる)。

## 2. 重点調査5項目と証拠

**項目1: `put away`が9回(監査では計11回)拾われなかった原因**
- 抽出Prompt: B1=`er138_kp_n5_generalization_01.py:316-324`(最大14個・条件4,5=`:308-310`逐語・「広めに」)、P7=`er119_kp_p7w5_prompts_01.py:34-41`(最大7つ・学習価値の高い順)。いずれも「上級者が学ぶ価値のある」表現を選ぶ指示で、`put away`のような基本語句動詞は価値順位の上位に来ない。
- 決定的な対照: **同一本文・同一モデルで、条件を「難易度不問の網羅列挙(L3)」に変えると3/3**(`ev01/probe_extract_result_untidi_b1b_L1-L3-L5.json` runs.L3[].hits)。
- 追加の観測: L3の出力は`put away`だけでなく`put it away`・`put that away`の3形を同時に返す(同ファイル runs.L3[0].spans)。本文で連続一致する`put away`は受動の3箇所(s008/s019/s020)のみで、能動形は代名詞を挟む(`put it away`/`put that away`/`putting something away`)。モデルは両方を扱える=条件1(連続一致)と条件3(最短形)の衝突仮説は成り立たない。

**項目2: 条件5を外しても`put away`・`leave out`が出ない原因**
- 条件5だけを外した診断(AUDIT_01 §3: 0/6)に加え、**条件4・5を両方外し「難易度は問わない」とした変種(L1, 14個)でも`put away` 0/3・`leave out` 0/3**。一方`in the way`・`in sight`・`hear it out`・`gets heated`は3/3(`ev01/…L1-L3-L5.json` runs.L1[].hits)。
- 枠を30に広げた変種(L2)で`put away` 2/3・`leave out` 1/3(`ev01/probe_extract_result_untidi_b1b_L2-L4.json`)=出現するが不安定=順位(枠内の優先度)の問題。網羅(L3、上限40)で3/3。
- よって**「条件5以外の要因」=枠(件数)内の価値順位付け**。条件を外しても、モデルは「候補を広めに14個」の中で、慣用性の高い・語彙が難しい表現を優先して埋める。

**項目3: `in the way`が補完枠では出るが安定しない原因**
- 通常P7/B1では条件4・5で落ちる(L1で条件除去すると3/3、L2 3/3、L3 3/3)。補完P7(AUDIT_01)は、すでに選ばれた表現を除外して再選定するため、上位候補が埋まった後に下位の`in the way`が到達した=偶然の空き枠。再現性がないのは、条件4・5による抑制が確率的にしか破れないため。
- **この項目は条件4・5が原因と確定(確度高)**。

**項目4: 句動詞・固定表現・分離形・繰り返し・文脈の影響**
- 句動詞: 句動詞限定Prompt(L5)は`put away`(`put it away`)・`leave out`(`leave it out`)を3/3で返すが、`in the way`・`in sight`(前置詞句)は0/3=句動詞探索だけでは固定表現が落ちる(**句動詞探索の単独採用は不十分**)。網羅列挙(L3)は両方を拾う。
- 分離形: 抽出可能(上記)。分離形のsurface(`put it away`)は代名詞を含むので、N5のGEN5が`put something away`へ一般化する(AUDIT_01 §2でL3 SAME確認済み)。抽出は代名詞入りの形で問題ない。
- 繰り返し: 本文中の出現回数は探索的特徴(`tools/pool_pick_probe_01.py` `occ()`)で、`put it away` 5、`in sight` 4、`something in the way` 2、`turn into an interrogation` 1、`hear it out` 1。記事の中心概念(物を片づける/出しっぱなし)に関わる表現ほど繰り返されるが、現行PromptもSEL/pickもこの信号を使っていない。
- 文脈: 抽出は本文全体を渡す方式で、文脈は与えられている。文脈の与え方が原因という証拠はない(L3も同じ本文で成功)。

**項目5: 抽出段階とN5選定上限7件の取りこぼしの分離**
- 抽出段: 本番方式の抽出プールは1記事あたりP7 7+B1 14前後で、そこに4表現(`in the way`/`in sight`/`put away`/`leave out`)はほぼ入らない(本番0/11〜1/4)。
- 選定段: 網羅プール(41/40件)をSELに渡すとkeepは17/20件。`pick`(`er138:950-961`)は難易度(advanced→upper→easy)順で上位7件に切る(`PHRASE_PICK_CAP=7`、`:47`)。結果(R0): S1は`in sight`・`something in the way`が入り`put it away`が落ちる、S2は`something in the way`が入り`put away`・`in sight`が落ちる。
- 同時に観測: 網羅プールでもR0は`turn into an interrogation`(S1: easyのため落ちる)のように、HRが過去に選んだ価値の高い表現を押し出し得る。**難易度順pickは、プールを広げるほど既存の良い候補を押し出す副作用が出る**ので、抽出を広げるなら選定規則も同時に見直す必要がある(設計案はDESIGN_OPTIONS_01.md)。

## 3. 原因仮説の確認/棄却

| 仮説 | 検証(probe) | 結果 |
|---|---|---|
| H1 条件5(易しい表現の除外)が唯一の原因 | AUDIT_01 診断0/6、L1(条件4+5除去)でも`put away`0/3 | **棄却**(`in the way`/`in sight`には有効、`put away`/`leave out`には無効) |
| H2 条件4(上級者向け優先)+条件5の組合せ | L1: `in the way`3/3、`in sight`3/3(本番0/9以上) | **確認**(`in the way`/`in sight`の主因)。`put away`/`leave out`は説明できない |
| H3 件数枠内の価値順位付けで基本語句動詞が下位になる | L1(14)0/3→L2(30)2/3→L3(網羅40)3/3、L5 3/3 | **確認(中〜高)**。枠サイズだけを操作した単独対照はなく、枠と「網羅」指示は同時に変わっている |
| H4 連続一致(条件1)と最短形(条件3)が分離形で衝突 | L3が`put away`/`put it away`/`put that away`を同時に返す。L5が`put it away`/`leave it out`を返す | **棄却** |
| H5 モデルが句動詞を認識できない | L5 3/3 | **棄却** |
| H6 本文の与え方(区切り・位置)の問題 | L3も同じ区切り(`er138:BODY`)・同じ本文で成功 | **棄却** |
| H7 重複回避規則(一方が他方を含む類似語句は重ねない)が`put away`を抑制 | L3は「代表1箇所」で`put away`系3形を返した。L0/L1では規則が同文で効いている | **未分離**(PromptがL0/L1とL3で他の部分も変わるため単独効果は不明。影響があっても主因ではない) |
| H8 繰り返し(中心性)が信号になっていない | Prompt全文に出現回数条件なし(`er138:316-324`、`er119_kp_p7w5_prompts_01.py:34-41`) | **確認(構造的事実)**。ただし「入れれば直る」ことの実証は未実施(委任_02で検証) |
| H9 SELの難易度ラベル揺れがpickを不安定にする | `turn into an interrogation` easy(S1)/upper(S2)、`in sight` upper(S1)/easy(S2)、`leave it out` F(S1) vs AUDIT_01でC | **確認** |

## 4. 一般化の確認(別記事・別Family、抽出段のみ、N=2)

辞書見出し(WordNet多語見出し)に一致する本文中の連続語句(ノイズ含む上限指標。`tools/dict_seed_probe_01.py`、`ev01/dict_seed_all_cases.json`、`ev01/dict_recall_by_variant.txt`)のうち抽出spanに含まれた数(各標本。括弧=抽出件数):

| 記事 | 辞書一致 | 本番B1(L0)/L1 | 網羅列挙(L3) | 句動詞(L5) |
|---|---|---|---|---|
| ai_cha_b1b | 18 | L0: 4, 4 (13,10) | **15, 14** (40,40) | 4, 4 (9,9) |
| melos_b1b(Z) | 13 | L0: 1, 3 (8,14) | **11, 10** (40,41) | 7, 5 (13,11) |
| untidi_b1b | 21 | L1: 5, 5, 7 (14) | **15, 16, 15** (40,40,39) | 8, 8, 8 (17,16,19) |

網羅列挙は本番B1の約3〜4倍の辞書一致語句を拾う(件数枠の問題が記事共通であることを示す)。ただし辞書一致は`a little`/`kind of`等の易しい語句やノイズを多く含む=後段(SEL)で絞る必要がある。Family X/Y/Z・Standard/Advancedの共通性は構造(同一B1/P7 Prompt、同一pick)から共通と見込まれるが、確認は委任_02(held-out記事)で行う。

## 5. 副作用の予備観測(L3)

- 本文に存在しない表現: L3/L4計12呼出のうち2件で`prevent missed doses`(本文一致なし)。既存の`collect_pool`(`er138:1198-1200` `span_in_text`)と`make_b1_gate`(本文一致+1〜5語)で落ちる=既存Gateで吸収。
- 易しい表現の増加: L3出力~40件には`in the kitchen`・`sits alone`・`personal failure`等の非塊が多い。SELがF判定で落とす(poolpick: keepは41中17、40中20)。SELの判断コストは増えるが塊判定自体は既存のまま。
- 費用/時間(1呼出): 本番B1 ¥0.15〜0.22・12秒、L3 ¥0.28〜0.35・29〜38秒、L4(3分割) ¥0.48〜0.65・56〜84秒(逐次)、SEL(40件) ¥0.49〜0.50。
- 技術失敗: 実行は例外なく完了。コスト台帳に意図した呼出数より1件多い=JSON途切れ再試行の可能性(`ev01/cost_log_probe.jsonl`、未特定・影響軽微)。
- 備考: `pool_pick_probe_01.py` L3標本3の実行は自分の`timeout 100`で中断(標本3のSEL費用は台帳に最大1回分含まれ得る)。再現のための再実行はしていない。

## 6. 限界

1記事中心(+2記事の抽出段のみ)・N=2〜3。LLM揺れの統計的頻度は推定できない。SEL判定は1 pool 1回のため、SELラベル揺れ(難易度・F/C)は2標本のみ。GEN5/VER5/CHK5(意味判定)は本委任で未実行(AUDIT_01の強制投入結果を引用)。条件4・5を外した変種を採用する価値判断は本委任の範囲外(承認済みPrompt仕様の変更を伴う=委任_02以降のTrial→VALIDATED→ユーザー判断)。
