# COMPARISON_01 (KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01、2026-10-26)

数値の出典: `trial_runs_01.json`(件数・call数・費用はusage log)、`summary_01.json`、`own_rubric_01.json`(自ルーブリックY/B/N。judge結果を見る前に確定)、`judge/judge_*.json`(gpt-6.1-sol・匿名シャッフル)、`gate_results_01.json`。候補全文と6 level×8行比較表は `RESULT_01.md`、現行方式の棚卸しは `CURRENT_BASELINE_01.md`。

## 1. 総括(6 level。Trial=各level 2回=12 run、現行=各level 1回=6 run)
| 項目 | 現行方式(6 level) | Trial方式 P7→W3(12 run) |
|---|---|---|
| 要求件数 | 最大8(3+5) | フレーズ7+単語3=10 |
| AI返答件数(平均) | 7.25(fresh 4 level)/7(AI島2 level) | P7 平均5.4(4〜7)+W3 3(12/12回とも3)=平均8.4 |
| Gate除外件数 | 計5(AI島2+fresh3)=0.83/level | 計7=0.58/run(canonicalization 6 + validate 1) |
| 最終候補件数 min/中央/max | 5 / 6.5 / 8 | 6 / 8 / 9 |
| フレーズ/単語(最終) | フレーズ33・単語5(X 4 levelは単語0。Z b1bのみ単語4) | フレーズ58・単語36(全run単語3) |
| 自ルーブリックY件数 min/中央/max | 2 / 4 / 5 | 3 / 5.5 / 7 |
| 自Y+B件数 min/中央/max | 3 / 5.5 / 6 | 6 / 7.5 / 9 |
| judge Y件数 min/中央/max | 2 / 5 / 6 | 5 / 6 / 9 |
| 自Yかつjudge Y(両者一致Y) min/中央/max | 2 / 3.5 / 5 | 2 / 5.5 / 7 |
| Y≥6のrun数 | 0/6 | 自Y 6/12、自Y+B 12/12、両者Y 6/12、judge Y 9/12 |
| 候補のN(数合わせ型)割合(自) | 8/38=21% | 4/94=4% |
| 候補のY割合(自) | 23/38=61% | 62/94=66% |
| 生成費用(平均/level) | fresh 4 level平均 ¥1.60(6.0 call) | ¥1.79(5.8 call)=+¥0.19/level |
| 所要(平均elapsed) | 144.5秒 | 169.2秒(並列起動のため参考値) |

## 2. フレーズ側の品質は下がったか(Fable設計指示・ユーザー§4-7/8)
- フレーズ候補のY率(自): 現行 20/33=61% → Trial 36/58=62%(差+1pt)。**フレーズ品質の低下は観測されず**。
- ただし**フレーズ件数そのものは増えない**: P7は「7件」を要求しても平均5.4件しか返さなかった(7件返答は2/12run、4件が2run)。最終フレーズは現行5.5/levelに対しTrial 4.8/run。モデルは『数合わせしない』を守り、増えた件数はほぼ単語3件分。
- 品質低下が出たlevel: **猿の手 Advanced**(r1/r2とも自Y=3。P7の5件中フレーズY=0〜1)。文学作品で慣用句相当が少なく、P7が記事固有の描写フレーズ(`pay off the house`・`caught in the machinery`・`shake one's husband awake` 等)でフレーズ枠を埋めた形(自判定: B/N)。現行も同levelはY=4で、Trialは単語Y=2〜3に依存。**数合わせ(filler)に近い傾向は『7件要求でフレーズ枠が満ちる文学テキスト』で再現した**(r1: N1・B4)。他5 levelでは再現せず。
- 英国電車マナー Standard はフレーズが3件(r1/r2同一)で、現行6件より少ない(現行は `point to current rail rules`・`put on an unwanted show` が自N、`written permission` がP7では `given written permission` として返りcanonicalizationで除外=§5)。

## 3. 単語候補(W3)
- 返答は12/12回とも3件。Gate(validate/CMU/canonicalization/gloss/RQA)は36/36件通過、containment(フレーズに含まれる語)による除外は0件(W3がP7句を入力されて重複を避けた)。単語候補に対してProduction Gateは「1語」でも問題なく機能(単語専用の新設Gate不要)。
- 自判定: 単語36件=Y 26(72%)/B 8(22%)/N 2(6%)。単語Yが1件以上あるlevel=6/6。Yの代表: `obstacle`・`separately`・`overlook`・`exploration`・`masterpiece`・`exception`・`uninvited`・`fate`・`scrape`・`deserted`・`compensation`・`snatch`・`burial`。
- 弱い単語(B/N): `performance`(AI Adv、N×2。judgeはY)・`discovery`/`Strategy`(AI Std、基本寄り。`Strategy`は見出し由来で大文字表記が残る)・`audience`/`carriage`(UK Std)・`automatically`(UK Adv)・`technique`・`responsibility`。W3が必ず3件返すため、**3件目が基本寄りになりやすい**(『数合わせしない』指示にもかかわらず12/12回3件=弱い数合わせ傾向。ただしN率は6%)。
- 『AIの仮想の島』のユーザー例 `cathedral`/`feature`: 本文には実在する(Std/Advとも "the Cathedral"=ゲーム内の建物名の固有名、`a feature of play`=1回)が、W3は4 run(Std/Adv×2)とも選ばなかった。自ルーブリックでは `Cathedral` は記事固有の呼称(R3不充足)、`feature` は基本寄り(R4)で、選ばれなかったことはルーブリックと整合する(必須語としては指定しない原文どおり)。Std W3: obstacle/separately/discovery(r1)・Strategy/separately/obstacle(r2)。Adv W3: performance/exploration/overlook(r1)・overlook/technique/performance(r2)。

## 4. 『AIの仮想の島』現行 Std5/Adv7 との差分
- Std 現行5(carry over / worth paying attention to / a useful card to play / take a detour / one step ahead、Gate除外2=`too soon to wave a flag`[6語]・`studied separately`[canonicalization])。Trial r1: 現行5を**全て保持** + `make a difference` + 単語 obstacle/separately/discovery=9件(自Y7)。r2: 現行5を全て保持 + Strategy/separately/obstacle=8件(自Y6)。`separately` は現行がフレーズ `studied separately` で除外された学習点を単語として救う形になった(救済フローではなく、W3が自力で選んだ結果)。
- Adv 現行7(carry over / call on / look at separately / one step ahead / card to play / take a detour / no use right now)。Trial r1: carry over / a useful card to play / call on / look at separately / take a detour + performance/exploration/overlook=8件(自Y5)、r2: 5フレーズ(exploration mode含む)+overlook/technique/performance=8件(自Y4)。**Trialは現行の `one step ahead`(Y)・`card to play`(Y。Trialは修飾付き `a useful card to play`[B])を落とし**、現行の `no use right now`(N)も落とした。単語の `exploration`/`overlook` はYだが `performance` はN(基本寄り)。Advの自Yは現行5 → Trial 5/4で**改善なし**。
- つまりAI島では、Stdは純増(Y 4→6〜7)、Advは横ばい(5→4〜5)。

## 5. Gate除外の内容(全件。`gate_results_01.json`)
Trial 12 run: 計7件。いずれも**Production既存Gateの既知挙動**で、P7/W3分離とは無関係。
| run | 句 | stage | 理由 |
|---|---|---|---|
| UK Std r1/r2 | given written permission | canonicalization | key_phrase `give written permission` が display/source_span の連続部分と不一致(Rule7。句頭の過去分詞の原形化が受理面外) |
| UK Std r2 | up to £1,000 (P7段) | validate | 数字を含む(数値placeholder型の回避) |
| 猿の手 Std r1/r2 | pulling free | canonicalization | `pull free` が連続部分と不一致(同上) |
| 猿の手 Adv r1 | accepts no responsibility / pulled free | canonicalization | 同上(動詞の三単現・過去形の原形化) |
現行側の除外: AI Std `too soon to wave a flag`(6語)・`studied separately`(canonicalization)、UK Std `up to £1,000`(validate)、猿の手 Std `pulling free`・Adv `accepts no responsibility`(canonicalization)。
単語候補へのGate適用: validate(連続一致・1語・有限助動詞・数値)=適用/CMU=適用/containment=適用(除外0)/canonicalization=適用(全通過)/gloss再整合・RQA=適用。除外の救済は適用していない(DESIGN §6)。Redundancy QA(旗)はTrial 12/12でREDUNDANCY_PASS、現行はUK Std 1件のみREDUNDANCY_NG(`put on an unwanted show`と`sound no one asked for`の意味重複)。

## 6. 再現性(r1/r2、同一Prompt・同一モデル)
最終候補集合のJaccard(r1∩r2/r1∪r2、全体): AI Std 0.70・AI Adv 0.60・UK Std 0.71・UK Adv 0.89・猿の手 Std 0.70・猿の手 Adv 0.25。単語のみ: 0.5・0.5・0.5・1.0・1.0・0.2。フレーズ: 0.83・0.67・1.0・0.83・0.57・0.29。**猿の手 Advanced は2回で候補がほぼ入れ替わる**(安定性が低い)。件数自体は6〜9で安定(最大差=猿の手 Adv 8→7、AI Std 9→8)。

## 7. judge(gpt-6.1-sol)と自ルーブリックの食い違い
- 全69候補(全level、現行+Trialの和集合)で一致46(67%)。内訳: (自,judge)=(Y,Y)38・(N,N)8・(B,Y)12・(B,N)8・(N,Y)1・(Y,N)1・(N,B)1。judgeは**自より甘い**(B→Yが12)。
- 主な食い違い: judgeがYとし自がB/Nとしたもの=`a useful card to play`・`discovery`・`Strategy`・`performance`(自N)・`technique`・`audience`・`carriage`・`due to be shared`・`automatically`・`interfere with fate`・`wail of loss`・`caught in the machinery`・`in compensation`。judgeがN/Bとし自がYとしたもの=`compensation`(Z Adv。judgeは`in compensation`との重複を指摘[R5。同一run内の重複ではなく別runの候補同士を同一プールで比較した影響])。judgeが自Bを`too_easy`/重複でNとしたもの=`look at separately`・`a useful card to play`(Adv)・`exploration mode`・`sound no one asked for`・`responsibility`。
- どちらを採用してもTrialが現行を上回る方向は同じ(judge Y中央値 6 vs 5、自Y 5.5 vs 4)。**判定基準による差は『Y≥6を満たすか』で現れる**: judge基準=満たす(中央値6・min5)、自ルーブリック基準=満たさない(中央値5.5・min3)。judgeは単独の合否根拠にしない(Fable設計指示)ため、本Trialの判定は自ルーブリックを主、judgeを副とする。

## 8. 費用・時間・単価
- 本Trial実費: 16 run(Trial 12=¥21.43・現行fresh 4=¥6.39)=¥27.82、judge 6 call=¥10.82、**合計¥38.64**(Guardrail ¥80内。見積20〜55円内)。usage log出典: `runs/*/usage_log.jsonl`・`judge/usage_log.jsonl`。モデル: 候補生成・canonicalization・gloss・RQA=gpt-6-luna(Production SUPPORT_MODEL。最新世代最上位ではないが『現行方式との比較条件統一』が例外理由)、judge=gpt-6.1-sol(リポ内最新最上位系)。
- Production採用時の単価影響: KP候補生成1 levelあたり +¥0.19(¥1.60→¥1.79。+12%)、1記事セット(Std+Adv)で約+¥0.4(量産単価目標¥70の約0.5%)。call数は同等(6.0→5.8)。Trial run 12本でProduction既定の外側retryが発火する条件(AUTO<3かつGate除外あり)に該当したrunは0。
