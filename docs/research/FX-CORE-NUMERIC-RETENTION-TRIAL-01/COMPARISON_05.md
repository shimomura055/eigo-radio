# COMPARISON_05 (FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_05、R5 v4追加検証)

<!-- 委任_06 C-3 修正 -->
> 委任_06 C-3(Opus条件C)で表示不具合2件を修正して再生成(`er115_fx_numeric_r5_comparison_fix_01.py`、API 0): (1) 欄行の『rerun=None』はm1_result.jsonのキー名誤りによる表示不具合で、実データは`b3_rerun`(再実行あり=True、1回目の欄と違反理由を併記)。 (2) EN数値トークンの単位なし『3』は『3D』への誤一致で、先読みで除外(修正前=ig r5b1 EN_Std ['3'] → 修正後 []。判定には使っておらず表示のみ)。


評価基準は`PREREGISTERED_CRITERIA_04.md`(B3が選んだ切り口基準)。固定表(`PREREGISTERED_CRITERIA_03.md` §1)による分類は**参考情報**で合否に使わない。数値分類は決定論の機械分類、「切り口への必要性」はSonnet所見(Fable独立レビュー対象)。


## moon_shrinking

### Before(参考。切り口が異なれば機械比較しない)
- **Before 公開版W-1 run_ms_02(数値脱落版)** (`er019_output/moon_shrinking/run_ms_02`)
  - R0: 必須[なし] / 任意[なし] / 不要(表)[8,900本超] / 不要(未分類)[なし] / 文脈[なし] / 不要数=1 ユニーク数値表記数=1
  - R2: 必須[なし] / 任意[なし] / 不要(表)[8,900本超] / 不要(未分類)[なし] / 文脈[なし] / 不要数=1 ユニーク数値表記数=1
  - EN_Std: 必須の存在={'約42〜46 m': False} 数値トークン=['8,900', '8,900', '8,900', '8,900 M']
  - EN_Adv: 必須の存在={'約42〜46 m': False} 数値トークン=['8,900', '8,900', '8,900', '8,900']
- **Before 前回Trial v2s1(委任_03 Storyline方式)** (`er115_output/fx_numeric_retention_trial_01/moon_shrinking/A/v2s1`)
  - R0: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
  - R2: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
  - EN_Std: 必須の存在={'約42〜46 m': True} 数値トークン=['42', '46 meters']
  - EN_Adv: 必須の存在={'約42〜46 m': True} 数値トークン=['42', '46 meters']

### 月 r6m1 (`er115_output\fx_numeric_retention_trial_01\moon_shrinking\A\r6m1`)
- B3 Storyline: 月の「しわ」が記録する後期の半径収縮は約42〜46 mとの推定で、熱史モデルの累積予測より小さく、表層の断熱作用や断層のできにくさが関わる可能性はあるものの、理由は未解明だ。
- 欄(reader_must_hear_numbers): ['約42〜46 m'] / M1=E_OK first_pass_ok=True b3_rerun=False
- 欄とStoryline整合: {'storyline_numbers': ['約42〜46'], 'field_numbers': ['約42〜46'], 'storyline_not_in_field(record_only)': [], 'field_not_in_storyline': [], 'storyline_m1_violations_record_only': [], 'match': True}
- 費用: {"storyline_b3": 12.356, "b3_core_number_rounding": 0.125, "w1_r0": 6.9, "w1_astra_r1": 2.172, "w1_astra_r2": 2.374, "advanced": 0.319, "standard": 0.334} total=24.58
- E保持(R0/R1/R2/Std/Adv): {'R0': ['約42〜46'], 'R1': ['約42〜46'], 'R2': ['約42〜46'], 'EN_Std': ['約42〜46'], 'EN_Adv': ['約42〜46']} all={'R0': True, 'R1': True, 'R2': True, 'EN_Std': True, 'EN_Adv': True}
- O-2'付替え: ['約750'] 非E中核の混入: {'R0': [], 'R1': [], 'R2': [], 'EN_Std': [], 'EN_Adv': []} / 新規数値(M2): {'R1': [], 'R2': []} / 周辺混入: {'R0': [], 'R1': [], 'R2': []}
- 誤解表現WARN: {'R2': {'near_time_misread': [], 'origin_claims': [{'phrase': '生まれてから', 'negated': True, 'context': 'んだと推定された。\n\n「事件解決！\u3000月が生まれてから縮んだ量は、それだけ！」\n\n、と報告書を閉じるのは、早すぎる。\n\nこの数字が示す'}, {'phrase': '月が生まれて', 'negated': True, 'context': 'ル縮んだと推定された。\n\n「事件解決！\u3000月が生まれてから縮んだ量は、それだけ！」\n\n、と報告書を閉じるのは、早すぎる。\n\nこの数字が'}], 'origin_claims_unnegated': []}}
- 固定表分類 R0: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- 固定表分類 R1: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- 固定表分類 R2: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- EN_Std: 数値トークン=['42', '46 meters', '42', '46 meters']
- EN_Adv: 数値トークン=['42', '46 meters', '42', '46 meters']

日本語R2本文:
```
月の「しわ」を取り調べたら、まさかの黙秘？

夜空で涼しい顔をしている月。だが、その表面には「しわ」がある。しかもこれ、ただの模様ではない。月が縮んだ証拠らしいのだ。

「では、しわを全部調べれば、どれだけ縮んだか分かりますね？」

名探偵気分でそう迫っても、月は簡単には口を割らない。

捜査の鍵となるしわは、片側が急で、反対側がなだらかな崖のような地形。岩盤どうしが押し合い、片方がもう片方に乗り上げてできたと考えられている。月面に残された、壮大な「おしくらまんじゅう」の跡だ。

この地形から計算すると、月の半径は約42から46メートル縮んだと推定された。

「事件解決！　月が生まれてから縮んだ量は、それだけ！」

、と報告書を閉じるのは、早すぎる。

この数字が示すのは、比較的新しい断層が記録した、月の歴史の後の時期の縮み。しかも、その断層がいつでき始めたのかも、まだ確定していない。

つまり、見つかったのは月の「生涯の家計簿」ではない。途中から記録した帳簿だ。最初のページより前に何があったかは、それだけでは分からない。

一方、月の冷え方を計算するモデルの中には、積み重なった縮みが、この推定値より大きくなると予測するものもある。

「おっと、計算と証拠が食い違ったぞ！」

ここでも探偵、いったん落ち着こう。モデルが扱う期間と、しわが記録した期間は同じではない。集計期間の違う帳簿を並べても、そのまま金額の照合はできないのだ。

さらに月には、「縮んでも、すぐ顔には出さない」事情があった可能性もある。

研究チームが挙げるのは、強くて弾力のある岩盤。これが地表近くの断層をできにくくし、押す力がある程度たまるまで、断層が表れにくかったのかもしれない。

だとすれば、しわは縮みを逐一伝える実況中継ではない。条件がそろって、ようやく録画ボタンが押された映像に近い。録画前の出来事まで映っているとは限らないのだ。

ただし、これは可能性の一つ。岩盤の性質が原因だと決まったわけではなく、モデルの予測と断層からの推定に差がある理由は、まだ分かっていない。

月のしわは重要な証人。でも、すべてを語る証人ではない。

次に月を見上げたら、こう尋ねてみよう。

「どれだけ縮んだ？　、その前に、記録はいつから始めたの？」
```
EN Std 数値含有文:
  - These land shapes suggest the Moon’s radius shrank by about 42 to 46 meters.
  - So we cannot compare their amounts directly, like account books for different times.
  - Faults suggest the Moon’s radius shrank about 42 to 46 meters during a later time.
EN Adv 数値含有文:
  - Based on these landforms, the Moon’s radius is estimated to have shrunk by about 42 to 46 meters.
  - The Moon’s surface faults suggest its radius shrank about 42 to 46 meters during a later period, not across its whole history.
  - Cooling models cover a different timespan, so their larger predictions cannot be directly compared with this estimate, and the gap remains unexplained.

**判定(Sonnet所見、Fable独立レビュー対象)**
1. B3選定品質=**適切**。切り口=「しわが記録する後期の縮みは約42〜46 m(推定)、モデル予測より小さく理由は未解明」。欄=約42〜46 mのみ(切り口の答えそのもの)。約750 m・約1.1 km・約11 cm/100万年・約3〜4億年は欄に入れず、Storylineにも無い。ユーザー指定の必須数値(約42〜46 m)は期待どおり欄に入った。
2. 保持=R0〜R1〜R2〜EN Std〜EN Advの全段で保持(Gate発火0・再生成0)。範囲値は日本語『約42から46メートル』(J2)、英語『about 42 to 46 meters』で波ダッシュなし。
3. 不要数値=R2のユニーク数値1(約42〜46 m)、固定表の不要0・切り口基準の不要0。O-2'で約750を付替え済み(本文に復活なし)。M2新規0。約750 m/約1.1 km/約11 cm/100万年の復活0。
4. 文章=探偵の取り調べ比喩(「黙秘」「家計簿」「録画ボタン」)が最後まで一貫し、数字は1個で羅列感なし。軽微な欠陥: 『、と報告書を閉じるのは、早すぎる。』(行頭の孤立読点)と『「どれだけ縮んだ？　、その前に…」』(鉤括弧内の読点)。出所はR1出力(`ja_writer/revision1.md:7`、Writer既存挙動)で数値方式と無関係、全9標本中この1標本のみ。読み上げ上は短い間として許容範囲と判断(Fable判断)。
**標本判定: 合格**(軽微な文体所見あり)。

### 月 r6m2 (`er115_output\fx_numeric_retention_trial_01\moon_shrinking\A\r6m2`)
- B3 Storyline: 月面の「しわ」から推定された数億年規模の後期の半径収縮は約42〜46 mで、熱史モデルの累積予測より小さく、表層の断熱作用や断層のできにくさが差に関わる可能性はあるが、理由はまだ決着していない。
- 欄(reader_must_hear_numbers): ['約42〜46 m'] / M1=E_OK first_pass_ok=True b3_rerun=False
- 欄とStoryline整合: {'storyline_numbers': ['約42〜46'], 'field_numbers': ['約42〜46'], 'storyline_not_in_field(record_only)': [], 'field_not_in_storyline': [], 'storyline_m1_violations_record_only': [], 'match': True}
- 費用: {"storyline_b3": 11.799, "b3_core_number_rounding": 0.125, "w1_r0": 6.969, "w1_astra_r1": 2.128, "w1_astra_r2": 1.994, "advanced": 0.309, "standard": 0.335} total=23.659
- E保持(R0/R1/R2/Std/Adv): {'R0': ['約42〜46'], 'R1': ['約42〜46'], 'R2': ['約42〜46'], 'EN_Std': ['約42〜46'], 'EN_Adv': ['約42〜46']} all={'R0': True, 'R1': True, 'R2': True, 'EN_Std': True, 'EN_Adv': True}
- O-2'付替え: [] 非E中核の混入: {'R0': [], 'R1': [], 'R2': [], 'EN_Std': [], 'EN_Adv': []} / 新規数値(M2): {'R1': [], 'R2': []} / 周辺混入: {'R0': [], 'R1': [], 'R2': []}
- 誤解表現WARN: {'R2': {'near_time_misread': [], 'origin_claims': [], 'origin_claims_unnegated': []}}
- 固定表分類 R0: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- 固定表分類 R1: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- 固定表分類 R2: 必須[約42〜46] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- EN_Std: 数値トークン=['42', '46 meters', '42', '46 meters']
- EN_Adv: 数値トークン=['42', '46 meters', '42', '46 meters']

日本語R2本文:
```
月のしわに事情聴取！　縮んだ月が語らない「過去」

月にも、しわがある。ならば聞いてみよう。「月さん、ずいぶん縮みましたね？」。ところが、この証人、そう簡単には全貌を明かさない。今回の研究は、月の顔に刻まれた手がかりを追う、宇宙の捜査劇だ。

まずは現場検証。しわの正体は、片側が急で、反対側がなだらかな崖。岩盤どうしが押し合い、一方がもう一方に乗り上げた跡と考えられている。研究チームはカメラ画像からこうした崖を地図にし、月の縮み具合を逆算した。

浮かび上がった数字は、半径で約42から46メートル。月のしわ、意外と具体的にしゃべるではないか。

だが、ここで「月の縮み、完全解明！」と見出しを打つのは早い。この数字が示すのは、比較的若い断層が記録した、月の歴史の後の時期の縮み。誕生から現在までの総決算ではない。押収した日記に、創刊号から全部そろっていたわけではないのだ。

さらに捜査をややこしくするのが、計算モデルとの食い違いだ。今回の見積もりは、月が冷えて縮むモデルの予測より小さい。ただし、モデルが示すのは縮みの積み重ね。同じ期間を同じ方法で調べた数字ではない。「モデル、容疑者確定！」とはいかない。

では、差の背景には何があるのか。研究チームが挙げる一つの可能性は、月の表面を覆う、すき間のある厚い岩くずの層。これが断熱材となり、内部の熱を逃がしにくくしたのかもしれない。月、まさかの厚着説。岩くずの「上着」で、冷えて縮むペースが落ちていた可能性がある。

もう一つは、月の表面が報告をため込んだ可能性だ。強く弾力のある岩盤が、力が十分たまるまで地表近くの断層形成を抑えていたのかもしれない。つまり、縮んだから即しわ、とは限らない。「変化はありました。でも表には出していません」というわけだ。

冷え方そのものが違ったのか。それとも、縮みがしわになるまでに事情があったのか。差の理由は、まだ決着していない。

月のしわは有力な証人だが、全時代を語れるわけではない。証言は大切に、ただし沈黙にも目を配る。月の顔を読む捜査には、名探偵のひらめきだけでなく、地道な裏取りが欠かせないらしい。
```
EN Std 数値含有文:
  - The estimate was that the Moon’s radius had shrunk by about 42 to 46 meters.
  - Young faults on the Moon suggest its radius shrank about 42 to 46 meters later, not over its whole history.
EN Adv 数値含有文:
  - The figure that emerged was about 42 to 46 meters of shrinkage in the Moon’s radius.
  - Young lunar faults suggest the Moon’s radius shrank by about 42 to 46 meters during a later period, not over its entire history.

**判定**
1. B3選定品質=**適切**。切り口=「数億年規模の後期収縮は約42〜46 m、モデルより小さく理由は未決着」。欄=約42〜46 mのみ(Storylineにも同じ数値、一致)。他の周辺数値は欄にも本文にも無い。
2. 保持=全段保持、Gate発火0・再生成0。EN Std/Advとも『about 42 to 46 meters』。
3. 不要数値=ユニーク数値1、不要0、O-2'付替え0(他の核数値は欄外に出なかった)、M2新規0、復活0。
4. 文章=「事情聴取」「押収した日記」「月、まさかの厚着説」と比喩が豊富で読みやすい。数字は1個。やや不自然な表現『月の表面が報告をため込んだ可能性』(比喩のぶれ)が1か所のみ。
**標本判定: 合格**。


## coffee_prices

### Before(参考。切り口が異なれば機械比較しない)
- **Before 公開版 run_fxpw_01** (`er019_output/coffee_prices/run_fxpw_01`)
  - R0: 必須[41%] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[2月] / 不要数=0 ユニーク数値表記数=1
  - R2: 必須[41%] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[2月] / 不要数=0 ユニーク数値表記数=1
  - EN_Std: 必須の存在={'4.30米ドル': False, '41%': True} 数値トークン=['41%', '41%']
  - EN_Adv: 必須の存在={'4.30米ドル': False, '41%': True} 数値トークン=['41%', '41%']
- **Before 前回Trial p3(Storyline方式)** (`er115_output/fx_numeric_retention_trial_01/coffee_prices/A/p3`)
  - R0: 必須[4.30、41%] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[2025年2月] / 不要数=0 ユニーク数値表記数=2
  - R2: 必須[4.30、41%] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[2025年2月、1] / 不要数=0 ユニーク数値表記数=2
  - EN_Std: 必須の存在={'4.30米ドル': True, '41%': True} 数値トークン=['2025', '$4.30', '41%', '41%']
  - EN_Adv: 必須の存在={'4.30米ドル': True, '41%': True} 数値トークン=['2025', '$4.30', '41%', '41%']

### コーヒー r6c1 (`er115_output\fx_numeric_retention_trial_01\coffee_prices\A\r6c1`)
- B3 Storyline: 米国の挽いたコーヒーの平均小売価格が前年同月比+41%に上昇した主因は関税以前の供給不足と生豆高で、関税撤回後も豆価格の変化が小売に届くまでには時間差がある。
- 欄(reader_must_hear_numbers): ['前年同月比+41%', '少なくとも約9か月'] / M1=E_OK first_pass_ok=True b3_rerun=False
- 欄とStoryline整合: {'storyline_numbers': ['41%'], 'field_numbers': ['41%', '約9か月'], 'storyline_not_in_field(record_only)': [], 'field_not_in_storyline': ['約9か月'], 'storyline_m1_violations_record_only': [], 'match': False}
- 費用: {"storyline_b3": 12.916, "b3_core_number_rounding": 0.134, "w1_r0": 6.667, "w1_astra_r1": 2.771, "w1_astra_r2": 2.136, "advanced": 0.499, "standard": 0.388} total=25.511
- E保持(R0/R1/R2/Std/Adv): {'R0': ['約9か月', '41%'], 'R1': ['約9か月', '41%'], 'R2': ['約9か月', '41%'], 'EN_Std': ['約9か月', '41%'], 'EN_Adv': ['約9か月', '41%']} all={'R0': True, 'R1': True, 'R2': True, 'EN_Std': True, 'EN_Adv': True}
- O-2'付替え: ['3%'] 非E中核の混入: {'R0': [], 'R1': [], 'R2': [], 'EN_Std': [], 'EN_Adv': []} / 新規数値(M2): {'R1': [], 'R2': []} / 周辺混入: {'R0': [], 'R1': [], 'R2': []}
- 誤解表現WARN: {'R2': {'near_time_misread': [], 'origin_claims': [], 'origin_claims_unnegated': []}}
- 固定表分類 R0: 必須[41%] / 任意[約9か月] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[9月] / 不要数=0 ユニーク数値表記数=2
- 固定表分類 R1: 必須[41%] / 任意[約9か月] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[9月] / 不要数=0 ユニーク数値表記数=2
- 固定表分類 R2: 必須[41%] / 任意[約9か月] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[9月] / 不要数=0 ユニーク数値表記数=2
- EN_Std: 数値トークン=['41%', '41%']
- EN_Adv: 数値トークン=['41%', '41%']

日本語R2本文:
```
コーヒーの値札、ただいま時差ボケ中

「関税をやめました」。そのニュースを聞いて、頭の中でコーヒーの値札を下方修正。ところが売り場に着くと、現実の値札は微動だにしない。「連絡、来てません？」と棚に聞きたくなる。

でも、値札にも事情がある。どうやらこの数字、最新ニュースではなく、少し前のニュースを読んでいるらしい。

米国では、9月の挽いたコーヒーの平均小売価格が、前年の同じ月より41％上昇した。カフェで頼む特別な一杯ではない。家でいれる、あのコーヒーの話だ。眠気覚ましのはずが、値段だけで目が覚める。

ここで容疑者として浮かぶのが関税。「犯人はお前だ！」と指をさしたくなるが、早まってはいけない。この事件、登場人物の出番を間違えると話がややこしくなる。

ロイターによると、値上がりの主な理由は、関税がかかる前から続いていた豆不足と、生のコーヒー豆の値上がりだった。関税も原料の豆を高くしたが、報道時点では、その影響はまだ消費者の払う価格に十分には届いていなかったという。

つまり、いま店頭で存在感を放っているのは、以前の豆不足や原料高。その後に加わった関税の影響は、まだ到着しきっていない。ニュースは速報でも、値札への配達はのんびりなのだ。

では、関税を撤回すれば、この配達は取り消せるのか。「はい、明日からお安くします！」という展開を期待したいが、そう簡単ではない。

米国がコーヒーなどの関税を撤回した後も、原料の価格変化が、豆を焼き、袋に詰め、店で売る段階の価格に届くには時間がかかると報じられた。

専門家たちの見積もりでは、その待ち時間は少なくとも約9か月。こちらは今日の一杯を買いたいのに、値札の時計はずいぶんゆっくり進む。

ただし、ここでカレンダーを取り出すのは早い。「約9か月後には必ず値下げ」という予告ではない。これは生の豆の価格が小売価格に伝わるまでの目安で、どの会社や商品にも同じように当てはまる期間ではないのだ。

「関税がなくなった」と「コーヒーが安くなった」は、同時上映とは限らない。政策発表でパチンと切り替わるスイッチを、値札は持っていない。

次に売り場で値段を二度見したら、こんな問いも添えてみたい。「この数字、いつのニュースですか？」。値札は今日の顔をして、少し前の事情を語っているのかもしれない。
```
EN Std 数値含有文:
  - It was 41% higher than in the same month a year earlier.
  - Next time you look twice at a price in a store, you might also ask, “When is this number’s news from?” A price tag may look like it belongs to today, but tell a story about what was happening a little while ago.
  - ground coffee prices were 41% higher than in September a year earlier, mainly because of earlier bean shortages and higher raw-bean prices.
EN Adv 数値含有文:
  - In the United States, the average retail price of ground coffee in September was 41% higher than in the same month a year earlier.
  - Next time you look twice at a price in the store, you might also ask, “When is this number’s news from?” The price tag may look like it belongs to today while telling a story about what was happening a little while ago.
  - ground coffee prices rose 41% year over year, mainly because of earlier bean shortages and higher raw-bean prices.

**判定**
1. B3選定品質=**適切**。切り口=「+41%上昇の主因は関税以前の供給不足と生豆高で、関税撤回後も小売に届くまで時間差がある」。欄=前年同月比+41%(説明される現象)+少なくとも約9か月(時間差の答え)。どちらも切り口の問いと答えを直接支える。ユーザー指定の必須数値のうち41%は欄に入った。**4.30ドル/ポンドは欄に入っていない**(B3の切り口が前回Trial p3の『価格水準の比較(4.30と41%)』から『時間差』へ変わり、4.30は切り口に不要となった。切り口が変わったため参考記録のみ)。9.14ドル・前月比3%は欄にも本文にも無い(3%はO-2'で付替え)。
2. 保持=41%・約9か月とも全段保持(Gate発火0・再生成0)。英語は『41%』は数字、『約9か月』は『about nine months / at least about nine months』と語表記で保持。
3. 不要数値=R2のユニーク数値2(41%、約9か月)+文脈数値『9月』(出典の月名)。固定表の不要0、切り口基準の不要0、M2新規0。9.14・3%の増加0。
4. 文章=『値札は時差ボケ』の比喩で一貫し、41％は『9月の挽いたコーヒーの平均小売価格が…41％上昇』と自然な1文。『少なくとも約9か月』の直後に『必ず値下げという予告ではない』と誤解を防ぐ。羅列感なし。
**標本判定: 合格**。

### コーヒー r6c2 (`er115_output\fx_numeric_retention_trial_01\coffee_prices\A\r6c2`)
- B3 Storyline: 国際相場が下落する一方、米国のコーヒーCPIは前年同月比+7.1%となっており、過去の供給不足による生豆高と、小売への反映に推定で少なくとも約9か月かかる時間差を手掛かりに、値下がりしにくさを読み解く。
- 欄(reader_must_hear_numbers): ['+7.1%', '少なくとも約9か月'] / M1=E_OK first_pass_ok=False b3_rerun=True(1回目の欄=['前月比8.7%下落', '前月比+0.6%'] 違反=[('0.6%', 'peripheral_number_in_storyline')])
- 欄とStoryline整合: {'storyline_numbers': ['7.1%', '約9か月'], 'field_numbers': ['7.1%', '約9か月'], 'storyline_not_in_field(record_only)': [], 'field_not_in_storyline': [], 'storyline_m1_violations_record_only': [], 'match': True}
- 費用: {"storyline_b3": 26.957, "b3_core_number_rounding": 0.126, "w1_r0": 14.838, "w1_astra_r1": 1.907, "w1_astra_r2": 3.824, "advanced": 0.233, "standard": 0.364} total=48.248
- E保持(R0/R1/R2/Std/Adv): {'R0': ['約9か月', '7.1%'], 'R1': ['約9か月', '7.1%'], 'R2': ['約9か月', '7.1%'], 'EN_Std': ['約9か月', '7.1%'], 'EN_Adv': ['約9か月', '7.1%']} all={'R0': True, 'R1': True, 'R2': True, 'EN_Std': True, 'EN_Adv': True}
- O-2'付替え: ['8.7%'] 非E中核の混入: {'R0': [], 'R1': [], 'R2': [], 'EN_Std': [], 'EN_Adv': []} / 新規数値(M2): {'R1': [], 'R2': []} / 周辺混入: {'R0': [], 'R1': [], 'R2': []}
- 誤解表現WARN: {'R2': {'near_time_misread': [], 'origin_claims': [], 'origin_claims_unnegated': []}}
- 固定表分類 R0: 必須[なし] / 任意[約9か月] / 不要(表)[7.1%] / 不要(未分類)[なし] / 文脈[なし] / 不要数=1 ユニーク数値表記数=2
- 固定表分類 R1: 必須[なし] / 任意[約9か月] / 不要(表)[7.1%] / 不要(未分類)[なし] / 文脈[なし] / 不要数=1 ユニーク数値表記数=2
- 固定表分類 R2: 必須[なし] / 任意[約9か月] / 不要(表)[7.1%] / 不要(未分類)[なし] / 文脈[なし] / 不要数=1 ユニーク数値表記数=2
- EN_Std: 数値トークン=['7.1%']
- EN_Adv: 数値トークン=['7.1%']

日本語R2本文:
```
コーヒー相場は下がったのに、値札はなぜドヤ顔なのか

「コーヒーの相場が下がった」と聞けば、頭の中ではもう特売のファンファーレ。ところが売り場に行くと、値札は高いまま、堂々の仁王立ち。「あの、ニュースをご覧になっていない？」

実は、値札がニュースに疎いのではありません。こちらと見ているカレンダーが違うのです。

国際的なコーヒー価格の指標は、月平均で前の月より下がりました。一方、同じ月の米国では、都市部のコーヒーの消費者物価指数が前年同月比で7.1％上昇。前の月と比べても上がっていました。

相場と値札、まさかの別行動。けんかでもしたのでしょうか。

このすれ違いを解く鍵は「時間差」。今日の値札は、今日の相場を映すライブ中継ではありません。少し前の豆の値段が、遅れてやって来る場所。いわば「過去から届いた請求書」です。

ロイター通信が以前伝えた専門家らの推定では、生豆の価格変化が小売価格に届くまで、少なくとも約9か月かかるといいます。焙煎や包装を経て、値札に届くまでには待ち時間があるのです。

こちらが「豆、安くなったんだって！」とはしゃいでも、値札は「ただいま、高かったころの分をお届け中です」。そりゃ会話もかみ合いません。

しかも、同通信の当時の報道では、米国の小売コーヒー価格の上昇の大部分は、過去の供給不足と生豆の値上がりによるものとされていました。値上げの犯人を直近のニュースだけで探すと、時系列という名のアリバイを見落とします。

「なるほど。では9か月後に安売りですね？」

残念、それは早合点。「少なくとも約9か月」は専門家らの推定で、会社や商品すべてに共通する固定の期間ではありません。その時期に必ず値下がりする、という予約票でもないのです。

時間差は、相場の下落がすぐ値札に届かない理由のひとつ。コーヒーが高いままでも、今日のニュースと矛盾しているとは限りません。

次に売り場でため息が出たら、「高い！」のあとに「いつの豆の話？」を。財布には厳しいけれど、値札はまだ、過去からの荷物を受け取っている最中なのかもしれません。
```
EN Std 数値含有文:
  - At the same time, the US consumer price index for coffee in cities was 7.1% higher that month than in the same month a year earlier.
EN Adv 数値含有文:
  - At the same time, in the US that month, the consumer price index for coffee in cities was up 7.1% from the same month a year earlier.

**判定**
1. B3選定品質=**適切(境界あり)**。切り口=「国際相場が下落する一方、米国のコーヒーCPIは前年同月比+7.1%、過去の供給不足と推定で少なくとも約9か月の時間差から値下がりしにくさを読み解く」。欄=+7.1%(CPI前年同月比)+少なくとも約9か月。9か月は答えで必須級。+7.1%は『相場が下がっても小売指標は上がっている』という論旨の前提を支える唯一の小売側実数で、言葉だけでは具体性が出にくい(v4の④)ため適切と判断するが、論旨の中心は9か月であり、7.1%の必要性は相対的に弱い=境界。固定表は7.1%を『不要』としているが、本標本の切り口ではStorylineが7.1%を明示しており、固定表を機械適用せず切り口基準で評価した(ユーザー原文§5)。ユーザー指定の4.30・41%は欄に入っていない(切り口変更。参考記録)。B3の1回目の欄は[前月比8.7%下落, 前月比+0.6%]で0.6%がM1違反(周辺数値)→既存のB3再実行(1回)で2回目に上記へ(`storyline_b3_attempt1/`)。
2. 保持=7.1%・約9か月とも全段保持(Gate発火0・再生成0)。英語は7.1%は数字、9か月は語表記。
3. 不要数値=R2のユニーク数値2(7.1%、約9か月)、切り口基準の不要0、M2新規0。O-2'で8.7%を付替え(本文に無い)。9.14・3%の増加0。
4. 文章=「値札はドヤ顔」「過去から届いた請求書」の比喩で一貫。数字2個で羅列感なし。ですます調(他標本はである調。Writer既存のばらつき)。
**標本判定: 合格(7.1%は境界)**。費用が大きい(48.25円)のは、B3再実行(26.96円)に加え、per-run cap 30円で1回chainが停止し1回再実行したため(下記「実行上の事象」)。


## semiconductor_earnings

### Before(参考。切り口が異なれば機械比較しない)
- **Before 公開版相当 run_devconfirm_01** (`er019_output/semiconductor_earnings/run_devconfirm_01`)
  - R0: 必須[167億ドル、約348億ドル] / 任意[295億9,100万ドル] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=3
  - R2: 必須[167億ドル、約348億ドル] / 任意[295億9,100万ドル] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=3
  - EN_Std: 必須の存在={'167億ドル': True, '約348億ドル': True} 数値トークン=['$29.591 billion', '$16.7 billion', '$16.7 billion', '$34.8 billion', '$29.591 billion', '$34.8 billion', '$34.8 billion', '$16.7 billion', '$34.8 billion']
  - EN_Adv: 必須の存在={'167億ドル': True, '約348億ドル': True} 数値トークン=['$29.591 billion', '$16.7 billion', '$16.7 billion', '$34.8 billion', '$29.591 billion', '$34.8 billion', '$34.8 billion', '$16.7 billion', '$34.8 billion']
- **Before 前回Trial r5s2(R5 v4)** (`er115_output/fx_numeric_retention_trial_01/semiconductor_earnings/A/r5s2`)
  - R0: 必須[167億ドル] / 任意[なし] / 不要(表)[217億ドル] / 不要(未分類)[なし] / 文脈[なし] / 不要数=1 ユニーク数値表記数=2
  - R2: 必須[167億ドル] / 任意[なし] / 不要(表)[217億ドル] / 不要(未分類)[なし] / 文脈[なし] / 不要数=1 ユニーク数値表記数=2
  - EN_Std: 必須の存在={'167億ドル': True, '約348億ドル': False} 数値トークン=['$16.7 billion', '$21.7 billion', '$16.7 billion', '$21.7 billion', '$16.7 billion', '$21.7 billion']
  - EN_Adv: 必須の存在={'167億ドル': True, '約348億ドル': False} 数値トークン=['$16.7 billion', '$21.7 billion', '$16.7 billion', '$21.7 billion', '$16.7 billion', '$21.7 billion']

### 半導体 r6s1 (`er115_output\fx_numeric_retention_trial_01\semiconductor_earnings\A\r6s1`)
- B3 Storyline: Broadcomは第3四半期のAI半導体売上高167億ドル（前年同期比+221％）を報告し、CEOがカスタムAIアクセラレーターとネットワーキングの強い需要を指摘するなか、翌四半期の全社売上高も大幅増を見込んだ。
- 欄(reader_must_hear_numbers): ['167億ドル', '+221％'] / M1=E_OK first_pass_ok=False b3_rerun=True(1回目の欄=['167億ドル', '217億ドル'] 違反=[('217億ドル', 'peripheral_number_in_storyline')])
- 欄とStoryline整合: {'storyline_numbers': ['167億ドル', '221%'], 'field_numbers': ['167億ドル', '221%'], 'storyline_not_in_field(record_only)': [], 'field_not_in_storyline': [], 'storyline_m1_violations_record_only': [{'surface': '第3四半期', 'reason': 'peripheral_number_in_storyline'}], 'match': True}
- 費用: {"storyline_b3": 14.705, "b3_core_number_rounding": 0.118, "w1_r0": 5.078, "w1_astra_r1": 2.85, "w1_astra_r2": 2.228, "advanced": 0.331, "standard": 0.291} total=25.602
- E保持(R0/R1/R2/Std/Adv): {'R0': ['167億ドル', '221％'], 'R1': ['167億ドル', '221％'], 'R2': ['167億ドル', '221％'], 'EN_Std': ['167億ドル', '221％'], 'EN_Adv': ['167億ドル', '221％']} all={'R0': True, 'R1': True, 'R2': True, 'EN_Std': True, 'EN_Adv': True}
- O-2'付替え: ['54％'] 非E中核の混入: {'R0': [], 'R1': [], 'R2': [], 'EN_Std': [], 'EN_Adv': []} / 新規数値(M2): {'R1': [], 'R2': []} / 周辺混入: {'R0': [], 'R1': [], 'R2': []}
- 誤解表現WARN: {'R2': {'near_time_misread': [], 'origin_claims': [], 'origin_claims_unnegated': []}}
- 固定表分類 R0: 必須[167億ドル] / 任意[221%] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=2
- 固定表分類 R1: 必須[167億ドル] / 任意[221%] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=2
- 固定表分類 R2: 必須[167億ドル] / 任意[221%] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=2
- EN_Std: 数値トークン=['$16.7 billion', '221%', '$16.7 billion', '$16.7 billion']
- EN_Adv: 数値トークン=['$16.7 billion', '221%', '$16.7 billion', '$16.7 billion']

日本語R2本文:
```
AI劇場、主役の隣で「つなぐ係」もざわついている

「AIは、どれだけ賢くなった？」

ニュースを開くたび、私たちはスターの成長を確かめる。難問に答えた、新しい技を覚えた。よし、拍手！　でも今日は、その隣にいる地味な係にマイクを向けたい。どうやら舞台袖も、にぎやかなのである。

まず、ブロードコムが発表した数字がすごい。AI半導体売上高は167億ドル。前年同期比221％増だ。数字だけで登場曲が鳴り、背後からスモークまで出てきそうな勢いである。

ただし、紙吹雪はまだ待ってほしい。167億ドルは会社全体ではなく、AI半導体に限った売上高だ。派手な数字ほど、胸についた名札を確認しよう。ここ、早押しクイズなら引っかけ問題になりかねない。

そして今回、耳をそばだてたいのはCEOの説明だ。カスタムAIアクセラレーターとネットワーキングへの需要が、引き続き非常に強いという。

用途に合わせたAI向け半導体に、強い引き合い。それは分かる。だが、もう一人いた。

「えっ、つなぐ係さん。あなたも？」

ネットワーキングは、機器同士が情報をやり取りするための仕組み。AIを劇場に見立てるなら、私たちが見つめるのは、難しいせりふもすらすら話す主演スター。一方こちらは、舞台裏の連絡を支える係だ。

主演の囲み取材をしていたら、隣から「こちらにも注文、来てます」と声がする。振り向けば、裏方さんの予定表も気になる。今回の話には、そんな面白さがある。

とはいえ、ここで「真の主役はネットワーキングだった！」と叫ぶのは、少々せっかちだ。まだ授賞式を始めてはいけない。

この情報だけでは、カスタムAIアクセラレーターとネットワーキングが、それぞれ売上高をどれだけ押し上げたのかは分からない。需要が強いという説明と、売上増への貢献度は、別の話である。

それでも、CEOが両方を挙げた点は見逃せない。AIのニュースは「頭脳がどれほど優秀か」だけでなく、「何と何を、どうつなぐか」に目を向けても面白いのだ。

普段、私たちが見るのは画面に現れる答え。その出来栄えに感心したら、たまには舞台袖ものぞいてみよう。どんな機器があり、どうつながっているのか。スターを見るだけでは浮かばなかった疑問が、そこにはある。

主役を交代させる話ではない。拍手を送りつつ、マイクを少し横へずらすだけだ。

「ところで、つなぐ係さん。そちらも、お忙しいんですか？」
```
EN Std 数値含有文:
  - Sales of AI chips reached $16.7 billion, up 221% from the same time last year.
  - The $16.7 billion is not all of the company’s sales.
  - When we admire how good they are, let’s sometimes look backstage, too.
  - Broadcom reported $16.7 billion in AI chip sales, with strong demand for custom chips and networking.
EN Adv 数値含有文:
  - Sales of AI chips were $16.7 billion, up 221% from the same period last year.
  - The $16.7 billion is not the company’s total sales; it is sales of AI chips alone.
  - When we admire how good they are, let’s sometimes take a look backstage, too.
  - Broadcom reported $16.7 billion in AI chip sales, and its CEO said demand for custom accelerators and networking remains very strong.

**判定**
1. B3選定品質=**適切**。切り口=「Broadcomの第3四半期AI半導体売上高167億ドル(前年同期比+221%)、CEOがカスタムAIアクセラレーターとネットワーキングの強い需要を指摘、翌四半期も大幅増を見込む」。欄=167億ドル+221%でStorylineの数値と完全一致。記事の主軸は『AIの隣で需要が強いネットワーキング(つなぐ係)』だが、167億・221%は決算の見出し事実で導入に必要。前回Trialで『過剰』とした217億ドルは1回目の欄に再び入った([167億, 217億])が、**既存M1(周辺数値違反)でB3再実行となり**2回目で167億+221%に修正された(`storyline_b3_attempt1/`)。ユーザー評価(前回の167億・217億は妥当)に従い、今回の選定も切り口に対して妥当と判断。
2. 保持=167億ドル・221%とも全段保持(Gate発火0・再生成0)。英語は『$16.7 billion』『221%』。
3. 不要数値=R2のユニーク数値2。固定表: 必須167億+任意221%、不要0。348億・295億・217億は本文に無い。切り口基準の不要0、M2新規0、O-2'で54%を付替え。
4. 文章=『主役の隣の“つなぐ係”』の舞台比喩で一貫。『167億ドルは会社全体ではなくAI半導体に限った売上高』と範囲を取り違えない注意が自然に入る。実績と見通しの区別(翌四半期は数字なし)。羅列感なし。
**標本判定: 合格**。

### 半導体 r6s2 (`er115_output\fx_numeric_retention_trial_01\semiconductor_earnings\A\r6s2`)
- B3 Storyline: Broadcomは第3四半期のAI半導体売上高が167億ドルに拡大し、CEOがカスタムAIアクセラレーターとネットワーキングの強い需要を説明するなか、次四半期も連結売上高の大幅増を見込んだ。
- 欄(reader_must_hear_numbers): ['167億ドル', '+221％'] / M1=E_OK first_pass_ok=False b3_rerun=True(1回目の欄=['167億ドル', '217億ドル'] 違反=[('217億ドル', 'peripheral_number_in_storyline')])
- 欄とStoryline整合: {'storyline_numbers': ['167億ドル'], 'field_numbers': ['167億ドル', '221%'], 'storyline_not_in_field(record_only)': [], 'field_not_in_storyline': ['221%'], 'storyline_m1_violations_record_only': [{'surface': '第3四半期', 'reason': 'peripheral_number_in_storyline'}], 'match': False}
- 費用: {"storyline_b3": 14.58, "b3_core_number_rounding": 0.121, "w1_r0": 6.463, "w1_astra_r1": 2.634, "w1_astra_r2": 2.131, "advanced": 0.297, "standard": 0.381} total=26.609
- E保持(R0/R1/R2/Std/Adv): {'R0': ['167億ドル', '221％'], 'R1': ['167億ドル', '221％'], 'R2': ['167億ドル', '221％'], 'EN_Std': ['167億ドル', '221％'], 'EN_Adv': ['167億ドル', '221％']} all={'R0': True, 'R1': True, 'R2': True, 'EN_Std': True, 'EN_Adv': True}
- O-2'付替え: ['54％'] 非E中核の混入: {'R0': [], 'R1': [], 'R2': [], 'EN_Std': [], 'EN_Adv': []} / 新規数値(M2): {'R1': [], 'R2': []} / 周辺混入: {'R0': [], 'R1': [], 'R2': []}
- 誤解表現WARN: {'R2': {'near_time_misread': [], 'origin_claims': [], 'origin_claims_unnegated': []}}
- 固定表分類 R0: 必須[167億ドル] / 任意[221%] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=2
- 固定表分類 R1: 必須[167億ドル] / 任意[221%] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=2
- 固定表分類 R2: 必須[167億ドル] / 任意[221%] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=2
- EN_Std: 数値トークン=['$16.7 billion', '221%', '$16.7 billion', '$16.7 billion']
- EN_Adv: 数値トークン=['$16.7 billion', '221%', '$16.7 billion', '$16.7 billion']

日本語R2本文:
```
AIの主役は「頭脳」だけ？　舞台裏の「つなぐ係」に拍手を

AIのニュースは、今日もスターの新技発表会。「また賢くなった！」「そんなことまでできるの？」と、客席は大盛り上がりだ。でも今回は、スポットライトを少し横へ。主役の隣で名前を呼ばれた「つなぐ」という仕事に、ちょっと注目してみたい。

きっかけは、ブロードコムの決算。AI半導体売上高は167億ドル。CEOの説明によると、前年の同じ時期から221％増えたという。さらりと読み流すには、数字の存在感が強すぎる。「AI、絶好調！」と拍手したくなるが、見どころはその先にもある。

CEOが引き続き需要は非常に強いと語ったのは、「カスタムAIアクセラレーター」と「ネットワーキング」だった。専門用語が二つ並ぶと、急に客席から置いていかれた気分になる。ここではひとまず、「AI向け」と「機器をつなぐ」の二つを押さえておこう。

気になるのは、後者の「つなぐ」だ。AIがライブの主役なら、私たちが見つめがちなのは、その華麗なパフォーマンス。ところが決算をのぞくと、舞台裏からも声がする。「こちらにも強い需要があります！」。おや、そちらも盛り上がっているのか。

もちろん、「つなぐ」という言葉は地味だ。新機能のように、ひと目で「すごい！」とはなりにくい。それでも、今回のCEOの説明では、需要の強い分野として名前が挙がった。華やかな答えだけを追っていると、この見どころは通り過ぎてしまいそうだ。

ただし、ここで脳内の見出しを「売上急増の真犯人は、つなぐ技術！」にするのは早い。今回の説明だけでは、それぞれがどれだけ売れたのかは分からない。需要が非常に強いというのも、同社CEOの評価だ。勢いで主演賞を贈る前に、分かることと分からないことは分けておこう。

さらに同社は、次の四半期も会社全体の売上高が増えると見込んでいる。ただし、こちらは未来の予想。すでに出た実績とは違い、実際の結果が変わる可能性もある。「今、売れた」と「これから増えそう」は別の話だ。景気のいい数字に気分が上がるときほど、この区別は大切にしたい。

次にAIの新技に驚いたら、その答えを支える側にも目を向けてみよう。「何ができる？」に加えて、「AIに関わる商売では、何が求められている？」と聞いてみる。167億ドルを入り口に、今回は「つなぐ」を観察する。スターだけでなく舞台裏も見ると、決算という演目が、少し違って見えてくる。
```
EN Std 数値含有文:
  - Sales of AI semiconductors came to $16.7 billion.
  - The CEO said this was 221% higher than in the same period a year earlier.
  - Along with asking, “What can it do?” ask, “What is in demand in businesses related to AI?” Starting with $16.7 billion, this time we’re looking at “connecting.” When we look backstage as well as at the stars, the earnings report can look a little different, like a show.
  - Broadcom reported $16.7 billion in AI semiconductor sales, while its CEO said demand stayed very strong for custom AI accelerators and networking.
EN Adv 数値含有文:
  - Sales of AI semiconductors came to $16.7 billion.
  - According to the CEO, that was up 221% from the same period the year before.
  - Along with asking, “What can it do?” ask, “What is in demand in businesses related to AI?” Starting with $16.7 billion, this time we’re looking at “connecting.” When we look at the backstage as well as the stars, the earnings report, like a show, can look a little different.
  - Broadcom reported $16.7 billion in AI semiconductor sales, while its CEO said demand remained very strong for custom AI accelerators and networking.

**判定**
1. B3選定品質=**適切(境界あり)**。切り口=「Broadcomの第3四半期AI半導体売上高が167億ドルに拡大、CEOがカスタムAIアクセラレーターとネットワーキングの強い需要を説明、次四半期の連結売上高も大幅増を見込む」。欄=167億ドル+221%。221%はStorylineには無い(欄とStoryline不一致=記録のみ、欄優先)が、台帳の【実績】に『CEOによると前年同期比+221%』とあり、実績の成長率という『比較の結果』でありv4の②③に当たる。論旨の中心はネットワーキングの需要で、221%は導入の補強=相対的に弱い境界。1回目の欄は[167億, 217億]で217億ドルがM1違反→B3再実行→2回目で上記(s1と同じ経路)。
2. 保持=167億・221%とも全段保持(Gate発火0・再生成0)。
3. 不要数値=ユニーク数値2、固定表の不要0(221%は任意)、切り口基準の不要0、M2新規0、O-2'で54%を付替え。348億・295億・217億は本文に無い。
4. 文章=『AIの主役は頭脳だけ？舞台裏のつなぐ係に拍手を』。221%は『CEOの説明によると前年同期比221%増』と出典(台帳=CEOによる)どおり帰属。次四半期の見込みを『未来の予想で実績と違う』と区別。羅列感なし。
**標本判定: 合格(221%は境界)**。


## ig_nobel_2026(再利用: 前回r5b1。再実行なし)

- **Before 公開版 run_nws_02** (`er019_output/ig_nobel_2026/run_nws_02`)
  - R0: 必須[3倍] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
  - R2: 必須[3倍] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
  - EN_Std: 必須の存在={'3倍超': True} 数値トークン=[]
  - EN_Adv: 必須の存在={'3倍超': True} 数値トークン=[]
### イグ r5b1(R5 v4、委任_04で取得済み・再利用) (`er115_output\fx_numeric_retention_trial_01\ig_nobel_2026\A\r5b1`)
- B3 Storyline: 今年のイグ・ノーベル賞を受賞した「ゴキブリのミルク」研究は、胚の栄養結晶の構造を解き、結晶として栄養を蓄える仕組みが胚を養ううえで持つ意義を論じた。
- 欄(reader_must_hear_numbers): ['同質量の哺乳類の乳の3倍超'] / M1=E_OK first_pass_ok=True b3_rerun=False
- 欄とStoryline整合: {'storyline_numbers': [], 'field_numbers': ['3倍'], 'storyline_not_in_field(record_only)': [], 'field_not_in_storyline': ['3倍'], 'storyline_m1_violations_record_only': [], 'match': False}
- 費用: {"storyline_b3": 10.143, "b3_core_number_rounding": 0.096, "w1_r0": 5.501, "w1_astra_r1": 2.869, "w1_astra_r2": 3.711, "advanced": 0.436, "standard": 0.323} total=23.08
- E保持(R0/R1/R2/Std/Adv): {'R0': ['3倍'], 'R1': ['3倍'], 'R2': ['3倍'], 'EN_Std': ['3倍'], 'EN_Adv': ['3倍']} all={'R0': True, 'R1': True, 'R2': True, 'EN_Std': True, 'EN_Adv': True}
- O-2'付替え: [] 非E中核の混入: {'R0': [], 'R1': [], 'R2': [], 'EN_Std': [], 'EN_Adv': []} / 新規数値(M2): {'R1': [], 'R2': []} / 周辺混入: {'R0': [], 'R1': [], 'R2': []}
- 誤解表現WARN: {'R2': {'near_time_misread': [], 'origin_claims': [], 'origin_claims_unnegated': []}}
- 固定表分類 R0: 必須[3倍] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- 固定表分類 R1: 必須[3倍] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- 固定表分類 R2: 必須[3倍] / 任意[なし] / 不要(表)[なし] / 不要(未分類)[なし] / 文脈[なし] / 不要数=0 ユニーク数値表記数=1
- EN_Std: 数値トークン=[]
- EN_Adv: 数値トークン=[]

日本語R2本文:
```
ゴキブリのミルク、飲む話より「しまう話」がすごかった

「ゴキブリのミルク」と聞いた瞬間、脳内の喫茶店が閉店した方へ。ご安心ください。今日は飲みません。グラスもストローも不要です。必要なのは、ちょっとだけ強めの好奇心。

今年のイグ・ノーベル賞を受賞したこの研究。主役は、人間向けの新商品ではなく、母親の体内で育つゴキブリの子ども。その腸にある、栄養を含んだたんぱく質の結晶です。

ミルクなのに、結晶。いきなり「ドリンク売り場」から「倉庫見学」へ案内されました。しかも所在地は、子どものおなかの中。予想外にもほどがあります。

研究者たちは、母親の体内で子どもを育てる種類のゴキブリを調査。子どもの腸の一部から結晶を取り出し、エックス線で立体的な構造を解析しました。

すると、たんぱく質には脂肪の仲間の物質が結びつき、糖がつながった部分も。「たんぱく質の結晶」と名乗っていますが、それだけが入ったシンプルな箱ではありません。

さらに論文には、思わず二度見する数字が。この結晶は、いくつかの種類の哺乳類の乳と同じ重さで比べると、３倍を超えるエネルギーを含むと推定されているのです。

「では、次世代のスーパードリンクに？」

お待ちください。そのメニュー表、まだ作れません。この研究は、人間が食べたときの栄養の効果や、食品としての安全性を調べたものではありません。エネルギーの数字だけで「飲むとすごい」と考えるのは、倉庫を見学した勢いでレストランを開くようなものです。

今回の見どころは、「飲めばすごい」ではなく「こんなしまい方があるのか」。液体を想像していたところへ現れる、栄養の結晶。その意外性だけでも、好奇心には十分ごちそうです。

著者たちは、栄養を結晶として蓄える仕組みが、生まれる前の子どもへの栄養補給を支えるのではないかと論じています。ただし、その役割はまだ確定していません。倉庫の姿は見えても、働きには調べる余地があります。

食べ物を見るとき、つい気になるのは「何が入っているか」。でも、「どうしまっておくか」にも、生き物の面白さは潜んでいます。

ゴキブリのミルク。注文する予定はなくても、その収納術には、ちょっと身を乗り出したくなりませんか。
```
EN Std 数値含有文:
  - Then they used X-rays to study the crystals’ 3D shape.
  - The paper also gives a number that makes you read it twice.
  - For the same weight, these crystals are thought to contain over three times as much energy as milk from several kinds of mammals.
  - Researchers found nutrient-rich crystals in baby cockroaches’ guts, thought to hold over three times the energy of the same weight of milk from several kinds of mammals.
EN Adv 数値含有文:
  - They removed crystals from part of the young cockroaches’ intestines and used X-rays to analyze their three-dimensional structure.
  - The paper also includes a number that makes you read it twice.
  - For the same weight, these crystals are estimated to contain more than three times as much energy as milk from several kinds of mammals.
  - Researchers found nutrient-rich crystals in baby cockroaches’ guts, estimated to contain over three times the energy of the same weight of several kinds of mammal milk.

**判定(委任_04で取得済み。再実行なし)**
1. B3選定品質=適切(欄=『同質量の哺乳類の乳の3倍超』のみ。切り口『飲む話よりしまう話』の中の唯一の定量的な驚き。1.2 Å・試行数・16.5%等は欄に無い)。
2. 保持=3倍超がR0初稿〜R1〜R2〜EN Std〜EN Advで保持(Gate発火0)。
3. 不要数値=0(Before公開版も0)。新規0。
4. 文章=比喩を維持、数字1個、『人が飲めば3倍元気ではない』を明示(誤解防止)。
**標本判定: 合格(委任_04の結果を再利用)**。
