# EVAL_06(Trial-06 Step A'' 結果と事前登録基準の機械的当てはめ。Fable評価待ち)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_11 / 日付: 2026-10-25 / 基準: `PREREGISTERED_CRITERIA_06.md`(生成前commit 81fd0ce86) / 集計: `analysis_06.json`(`analyze_06.py`)/ 生データ: `OUTPUT_06_<work>_r<n>_STEPA_DEV.json`・`usage_06_*.json`・`_raw_06_*.txt`
モデル: gpt-6-luna(全18 callでresponse.model一致。最新世代の推奨系。Trial-01〜05と同一。temperature/seed/reasoning未指定)。
Status: DEV/Trial専用。判定はSonnetが事前登録基準を機械的に当てはめた所見(最終判定はFable)。

## 1. 結論(事前登録基準)
**Step A'' = 不合格(6作品中2作品のみ合格: イグ・ノーベル賞2026、告げ口心臓[新ホールドアウト])**。不合格4作品=開いた窓・賢者の贈り物・猿の手・二十年後(平易)。
`PREREGISTERED_CRITERIA_06.md` §4の終了条件に従い、**Step Bは実行せず、4回目は設計しない**。撤退案をQCD付きで整理してFableへ報告する(`ADOPTION_NOTE_06.md`)。
- 18標本すべて取得(parse失敗0・call失敗0・incomplete 0・再起動0)。0件標本は難所のある5作品で0(「0件標本なし」は全作品で達成)。基礎のみ(basic_only=true)の選定は主規則上0(適格条件で除外。18標本でbasic_only=trueは1件も付かず=Trial-05と同じ。Opus所見どおりこの欄は機能していない)。
- 不合格の原因はすべて「許容集合外の選定」(12標本・14件)。拾い漏れ(中核が選ばれない)ではなく、**2件目に選ばれる中クラスの文が許容集合外**になった。

## 2. 作品別の選定(英文は本文側の逐語。[core]=中核/[either]=どちらでも可/[outside]=許容集合外)
### 開いた窓(open_window) 判定=**不合格**

| 標本 | 主規則の選定(段落・分類・許容集合との関係・英文逐語) | 元what-if規則(O)の選定 | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P21 INV [core] `Across the quiet garden came a young voice:`<br>P12 FRONT [outside] `Before Framton could reply, her aunt hurried into the room.` | P21 INV [core], P12 FRONT [outside] | 3/4 | 0.2977 |
| r2 | P12 FRONT [outside] `Before Framton could reply, her aunt hurried into the room.`<br>P29 HEAVY [either] `Inventing convincing stories at a moment’s notice was Vera’s speciality.` | P12 FRONT [outside], P29 HEAVY [either] | 2/4 | 0.3514 |
| r3 | P21 INV [core] `Across the quiet garden came a young voice:`<br>P12 FRONT [outside] `Before Framton could reply, her aunt hurried into the room.` | P21 INV [core], P12 FRONT [outside] | 2/3 | 0.3043 |

### イグ・ノーベル賞2026(ig_nobel) 判定=合格

| 標本 | 主規則の選定(段落・分類・許容集合との関係・英文逐語) | 元what-if規則(O)の選定 | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P4 CLEFT [core] `If you were expecting a fancy latte, what you got was a map of molecules.`<br>P5 CMP [core] `The crystals contain more than three times as much energy as the same weight of milk fr…` | P4 CLEFT [core], P8 CLEFT [core] | 11/11 | 0.5753 |
| r2 | P8 CLEFT [core] `What’s more interesting is the idea of turning nutrients into crystals and storing them…`<br>P5 CMP [core] `The crystals contain more than three times as much energy as the same weight of milk fr…` | P8 CLEFT [core], P5 CMP [core] | 11/15 | 0.762 |
| r3 | P4 CLEFT [core] `If you were expecting a fancy latte, what you got was a map of molecules.`<br>P5 CMP [core] `The crystals contain more than three times as much energy as the same weight of milk fr…` | P4 CLEFT [core], P8 CLEFT [core] | 8/8 | 0.4498 |

### 賢者の贈り物(gift) 判定=**不合格**

| 標本 | 主規則の選定(段落・分類・許容集合との関係・英文逐語) | 元what-if規則(O)の選定 | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P22 INV [core] `Inside were the tortoise-shell combs she had so often admired in a shop window.`<br>P5 FRONT [outside] `Then, before she could change her mind, she pulled on her coat.` | P22 INV [core], P30 INV [core] | 11/11 | 0.4729 |
| r2 | P4 POSTMOD [core] `One was Jim’s gold watch, handed down from his grandfather to his father, and then to him.`<br>P1 ELL [outside] `Still the same.` | P4 POSTMOD [core], P1 ELL [outside] | 2/2 | 0.467 |
| r3 | P22 INV [core] `Inside were the tortoise-shell combs she had so often admired in a shop window.`<br>P2 ELL [outside] `She had saved every penny she could.` | P22 INV [core], P30 INV [core] | 3/3 | 0.3633 |

### 猿の手(開発用)(paw) 判定=**不合格**

| 標本 | 主規則の選定(段落・分類・許容集合との関係・英文逐語) | 元what-if規則(O)の選定 | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P24 INV [core] `Then came a soft knock.`<br>P1 FRONT [outside] `Beside them, Mrs. White smiled over her knitting.` | P24 INV [core], P1 FRONT [outside] | 15/15 | 0.6162 |
| r2 | P24 INV [core] `Then came a soft knock.`<br>P8 FRONT [outside] `After their visitor left, Herbert laughed.` | P24 INV [core], P8 FRONT [outside] | 8/9 | 0.6117 |
| r3 | P24 INV [core] `Then came a soft knock.`<br>P8 FRONT [outside] `After their visitor left, Herbert laughed.` | P24 INV [core], P8 FRONT [outside] | 7/7 | 0.554 |

### 告げ口心臓(新ホールドアウト)(tth) 判定=合格

| 標本 | 主規則の選定(段落・分類・許容集合との関係・英文逐語) | 元what-if規則(O)の選定 | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P8 INV [core] `From the bed came a small groan of terror.`<br>P17 FRONT [either] `Calm and confident, he sat directly above the hidden body.` | P8 INV [core], P15 INV [core] | 6/6 | 0.5365 |
| r2 | P8 INV [core] `From the bed came a small groan of terror.`<br>P17 FRONT [either] `Calm and confident, he sat directly above the hidden body.` | P8 INV [core], P15 INV [core] | 4/4 | 0.4339 |
| r3 | P8 INV [core] `From the bed came a small groan of terror.`<br>P17 FRONT [either] `Calm and confident, he sat directly above the hidden body.` | P8 INV [core], P15 INV [core] | 5/5 | 0.4791 |

### 二十年後(平易な本文)(promise) 判定=**不合格**

| 標本 | 主規則の選定(段落・分類・許容集合との関係・英文逐語) | 元what-if規則(O)の選定 | 適格数/features | 費用(円) |
|---|---|---|---|---|
| r1 | P8 FRONT [outside] `Before we parted, we promised to meet here at ten tonight, whatever happened.`<br>P23 ELL [either] `Twenty years can change a man, but not the shape of his nose.` | P8 FRONT [outside], P16 FRONT [outside] | 7/7 | 0.4659 |
| r2 | P8 FRONT [outside] `Before we parted, we promised to meet here at ten tonight, whatever happened.`<br>P15 ELL [outside] `Once, he took out his watch, then slipped it away again.` | P8 FRONT [outside], P26 FRONT [outside] | 5/5 | 0.402 |
| r3 | P8 FRONT [outside] `Before we parted, we promised to meet here at ten tonight, whatever happened.`<br>P1 POSTMOD [outside] `Bob stood in the doorway of a closed hardware store, sheltered from the rain.` | P8 FRONT [outside], P26 FRONT [outside] | 5/5 | 0.712 |

## 3. 原因分析(根拠の観測値)
1. **許容集合外14件の内訳**(`posthoc`含む集計。`analysis_06.json`の`outside`): 中クラスFRONT 10件[`Before Framton could reply, her aunt hurried into the room.`×3(開いた窓r1〜r3)/ `Then, before she could change her mind, she pulled on her coat.`(賢者r1)/ `Beside them, Mrs. White smiled over her knitting.`(猿の手r1)/ `After their visitor left, Herbert laughed.`×2(猿の手r2,r3)/ `Before we parted, we promised to meet here at ten tonight, whatever happened.`×3(二十年後r1〜r3)]、ELL 3件[`Still the same.`(賢者r2)/ `She had saved every penny she could.`(賢者r3)/ `Once, he took out his watch, then slipped it away again.`(二十年後r2)]、POSTMOD 1件[`Bob stood in the doorway of a closed hardware store, sheltered from the rain.`(二十年後r3)]。
2. **最大の原因はFRONT(10/14件)**: 文頭の時の副詞節(before/after+節)を「主節の主語・動詞を取り違えやすい」としてFRONT・basic_only=falseにした。**これはPrompt(私の設計)の内部矛盾**: FRONTの定義に「副詞節」を例示した一方、基礎項目に「基本的な接続(when・if・while…)」を置いたため、モデルはFRONTの定義を優先した。`misread_target=SUBJECT`・`misread_quote`逐語の追加条件は全件成立し、**中クラス追加条件(Opus(b)2)では埋め草を防げなかった**(`mid_cond_rejected`は全18標本で0件=この条件で落ちた候補がなかった)。
3. **揺れの所在が移った**: 2件目(中クラス)の選定が標本ごとに変わる。1件目の強クラス(INV/CLEFT/CMP)はほぼ安定: 強クラスが選ばれた標本=開いた窓2/3(r2は`Across the quiet garden came a young voice: “Bertie, why do you bound?”`と次段落を連結して返し**resolve失敗でP21が脱落**=`sentence not found in para`、`resolve6`の対象外)、イグ3/3、賢者2/3(r2はfeaturesが2件のみで網羅性が低い)、猿の手3/3、告げ口心臓3/3。
4. **分類コードの安定**: 登録済み文の分類コードは中核INV/CLEFT/CMP(P24, P8, P15, P21, P22, P30, イグP4/P5/P8)ではほぼ一致。ただしイグP4は`FRONT/CLEFT/HEAVY`に分かれた標本あり、賢者P22/P30はr2で未収載(featuresが2件のみ)、猿の手P18/P22はSPEC(r1,r2)・未収載(r3)。分類コード自体の揺れ(OPUSのリスク記載どおり)は残る。
5. **同一クラス制約・優先順位は設計どおり機能**: 元what-if規則(O)との差は主にイグ(O: `{P4,P8}` CLEFT2件 → 主規則: `{P4/P8, P5}`)と告げ口心臓(O: `{P8,P15}` INV2件 → 主規則: `{P8, P17}`)。いずれも許容集合内。選定が強クラス1件+中クラス1件になる構造は意図どおり。
6. **平易な作品(二十年後)で埋め草化を防げなかった**: 適格が各標本5〜7件あり、3標本すべてで許容集合外(FRONT[Before…]・ELL・POSTMOD)を選定。0件にならなかった。Opusが懸念した「平易な本文でも常に2件選ぶ」が再現した。
7. 比較用(N)(同一クラス・同一段落制約を外した版)と(O)は許容集合外の選定件数が同じ(開いた窓3/賢者1/猿の手3/二十年後6件)。主規則は賢者で3件(O/Nは1件: 強クラスINVの2件目P30[中核]が選ばれる代わりに、同一クラス制約で別クラスのFRONT/ELLに移った)、二十年後で5件(O/Nは6件)。すなわち**同一クラス制約(Opus(b)3)は、強クラスが2件とも中核であれば逆効果(賢者)になり、平易作品では2件目が別クラスの低価値文へ移る**ことが観測された。

## 4. 事後分析(API 0。合否に使わない・事前登録外・4回目の設計ではない。`posthoc_06.py`/`posthoc_06.json`)
同じ18標本に規則を事後に変えて当てた反事実。**同じデータを見てから作る事後規則であり、新標本での確認なしに採否判断の根拠にしてはならない**(Opusリスク記載と同じ)。
| 規則 | 開いた窓 | イグ | 賢者 | 猿の手 | 告げ口心臓 | 二十年後 |
|---|---|---|---|---|---|---|
| 主規則(事前登録) | 不合格 | 合格 | 不合格 | 不合格 | 合格 | 不合格 |
| FRONT除外 | 合格 | 合格 | 不合格(2標本外) | 不合格(1標本外) | 合格 | 不合格(2標本外) |
| FRONT+ELL除外 | 合格 | 合格 | 合格 | 合格 | 合格 | 不合格(1標本外=POSTMOD) |
| 強クラスのみ | 不合格(0件1標本=P21脱落) | 合格 | 不合格(0件1標本) | 合格 | 合格 | 合格 |
読み取り: 外れ値の大半はFRONT・ELLに集中しており、強クラスのみにすると平易作品は0件で正しく処理できる(二十年後は3/3が0件、許容集合外0)が、強クラスの拾い漏れ(開いた窓r2のresolve失敗、賢者r2のfeatures過少)が0件標本を作る。いずれの変更も新規Trial(4回目)であり、終了条件によりユーザー判断なしには実施しない。

## 5. 追加の測定(合否外)
- 費用: 18 call合計 **8.855円**(平均0.492円/call、0.298〜0.762円)。入力平均2,736 token・出力平均5,930 token(最大8,983、`max_output_tokens=13000`に未到達、全call status=completed)。予約方式ガード: 開始時の最大予約合計は12.53円(上限12.6円内)で、実費は上限12.6円・委任上限14円に対しそれぞれ70%・63%。所要: 全体149.0秒、1 call平均52.3秒(最大76.8秒)。
- 全文カバレッジ: `uncovered_paras`は全18標本で空(網羅OK)。`sentence_replaced_by_body`=0(引用符起因の置換なし。`resolve6`の引用符除去が本番で発動した例は無し)。resolve失敗は開いた窓r2の1件のみ(上記3)。材料欄欠落で除外された適格候補=0。
- 比較用規則: (O)・(N)の許容集合外選定=開いた窓3/賢者1/猿の手3/二十年後6件(主規則は3/3/3/5件。上記3-7)。
