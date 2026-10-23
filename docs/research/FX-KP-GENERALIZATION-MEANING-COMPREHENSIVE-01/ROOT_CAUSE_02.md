# ROOT_CAUSE_02: Key Phrase 日本語意味(Std)・英語説明(Adv)の品質問題 — 工程・入出力・検査の構造からの根本原因再調査

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 委任_06(2026-10-23) / 前版=`ROOT_CAUSE_01.md`(委任_01)・`TRIAL_RESULT_01.md`・`A3_VERIFICATION_01.md`
範囲: read-only調査+原因切り分けprobe(DEV専用、API実費 **13.43円**、gpt-6-luna生成+claude-sonnet-5-5 Judge 1系統、上限15円内)。Production/Prompt/template/flag変更0、記事B成果物変更0、`er111_*`/`er109_*`/`er103_*`無編集。
ユーザー指示原文=`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_03.md`(これが最新、§1 A-3の不採用は目的達成ではない/§3 Promptの再調整でなく本質から再設計/§4 検証1〜6)。
目標(ユーザー例): Std `draw a line`=慣用義を捉えた日本語(「一線を引く」の成功例あり)/Adv=本文の意味を踏まえ記事固有条件に限定されない中心義(例 `to establish a clear boundary or limit`、文字列固定ではない)。

## 0. 結論(先頭)

| # | 問い | 結論 | 確度 | 主な証拠 |
|---|---|---|---|---|
| (a) | 意味の正本がどこにも無い仮説 | **部分的に正しいが、「正本を1つ作れば直る」は誤り**。下流の意味(Adv説明)は「記事全文でなく、**1文+Std向け日本語意味(gloss)**」から作られ、glossの**含意・字義寄り・記事固有条件がそのままAdvへ輸入される**(因果確認済み)。一方、同じ段で決めた「中心義」を下流へ固定すると(E3)、判断が外れた1回の誤りが全工程に固定され、**独立した第2の目が失われて悪化**した | 高(因果probe) | §3-1 probe-03b、§3-2 E3 |
| (b) | Stdが逐語/字義に戻る原因 | **検査・retryは原因ではない**(現行path 16 unit/48 itemのgloss: 初回合格16/16、qa自己申告は全PASS、mapping機械検査はrecord-onlyで不合格0)。**「全語反映」句の除去でも直らない**(G1)。原因は **モデルの語彙既定(`draw a line`→「線を引く」2/2)＋「字義か慣用かを先に決める」手順がPromptに無いこと**。ただし用法先決め(G2)は `draw a line`・`shine a light on`を直す一方 `take the wheel`・`refueling support`を壊し、**差し引き0(NG 6/28→7/28)** | 中〜高 | §3-3 |
| (c) | Advが狭い/広い原因 | **主因は入力のgloss**: glossが「一線を引く」だと説明に`acceptable`が **3/4**、「線を引く」「境界線を引く」「区別をはっきりさせる」「glossなし」では **0/4**。つまり **ユーザーが望むStd「一線を引く」が、Advを「許容できることの限界」へ狭めている**(Std成功がAdv失敗を生む構造)。`Carry the Load`は「荷物を運ぶ」で字義寄り 2/4、glossなし/「重い負担を引き受ける」で 0/4。全文を渡しても改善せず(E2: 61%<79%)、1文でも文脈名詞は入る | 高(因果probe) | §3-1 |
| (d) | Validator/retry/fallback | **意味品質の方向には何も働いていない**。gloss再整合の合否は `qa=PASS`自己申告・括弧禁止・人称不整合・数字だけ(mappingはrecord-only)、説明の合否は語数≤15・新規Fact(大文字語/数字)だけ。**意味の正否・字義/慣用・Std/Adv整合を見る検査はどの段にも無い**。fallback(gloss失敗→HR)は実績0件 | 高 | §2 |
| (e) | 既存仕様・過去Trial | Adv説明は承認済みB仕様(`CURRENT_SPEC.md:2032`: Trial-02のB候補、15語、新規Fact不可、`explanation_en`仕様文は逐語、PROMPT_SHA256)で**日本語参考意味を入力にする設計は承認済み**。変更は仕様変更(ユーザー判断)。Std glossの承認規則は文体(平易・直訳調回避)のみで**慣用句の語義選択規則は無い**。Trial-02(別工程の一般化LLM=REJECTED)の結論は「既存callの拡張で担う」。A-3 v3(Prompt追記)・A-2(gloss語義方針)・共有anchorはいずれも**手段として不採用/不要**(目的は未達のまま) | 高 | §4 |

**一言で言うと**: 現行の構造は「Std向け日本語glossを作り、それをAdv説明の入力に流す」一方向の連鎖で、glossの**言葉の癖(一線=道徳的な線、荷物=字義)がAdvに伝染**する。独立に判断し合う2つの目(Std gloss/Adv説明)は互いの誤りを訂正できる強みがあるのに、現行は片方の目をもう片方の「訳語」で曇らせている。さらに、字義か慣用かの判断(最難関)は**検査も手順も無く、モデルの既定に任されている**。「意味の正本を共有する」案(E3)は、この判断が外れたとき誤りを固定するため、現状のモデルでは逆効果だった。

## 1. 工程ごとの「意味」の扱いと受け渡し情報(file:line)

| 段 | 入力 | 出力に意味情報はあるか | 本文での意味の把握 |
|---|---|---|---|
| 選定 `er105_kp_fulltext_selector_01.py:48-67`(Prompt 2逐語固定、`SELECTOR_JSON_SCHEMA`=`phrase`,`word_count`のみ) | 記事全文 | **無い**(phraseと語数だけ) | 全文を見て選ぶが、意味は出力しない。Prompt 2はユーザー逐語固定で、ここへ意味出力を足すのは不可(OPEN-454) |
| canonicalization `b1_p2_keywords_canonicalization_fulltext_prompt_template.txt`(判定項目は形のQA11本、`reasoning`は「形を変えた理由」の日本語1〜2文) | 記事全文+候補 | **無い**(意味情報なし。reasoningは形の理由) | 全文を見ているが、意味は問われない |
| Std gloss `er003_key_words_gloss_alignment.py:575-612`(`build_user_message_corrected`)、effort high、1 callで最大3 KP | 最終key_phrase+display_phrase+source_sentence+**記事全文(参考)**。fulltext itemはcurrent gloss=null(新規生成 `:315-321`) | 日本語gloss1本+`reasoning`(自由記述)+`qa_reflects_all_key_phrase_words`(自己申告) | 全文を見られるが、**「本文の該当文での用法(字義/慣用/句動詞)を判定する手順は無い**。`source_sentence`は『辞書の複数語義から選ぶためだけ』(`:315-321`)。逆に冒頭は『key_phrase全体(…すべての語)の意味と過不足なく一致』(`:585-586`) |
| Adv説明 `er019_family_x_kp_explanation_01.py:54-85,164-178`、effort medium、1 callで全KP | **used_form+source_sentence(1文)+japanese_gloss(『accuracy check only, do not translate literally』`:174`)** | `english_explanation`のみ | **記事全文は渡らない**。意味の手がかりは1文とStd向けgloss。Promptは同時に『日本語参考意味を逐語訳するな』(`:79`)と『別の文脈でも通じる』(`:82`)を要求 |
| 検査 | gloss: 括弧/数字/人称不整合/`qa`自己申告 `:612-665`、mappingはrecord-only `:665`。説明: 語数・新規Fact `er019...:199-213` | — | 意味の正否・字義/慣用・Std/Adv整合の検査は**無い** |
| 再生成条件 | 説明の再生成signatureに**gloss文字列が含まれる** `er019_family_x_audio_production_runner_01.py:1081`(glossが変わるとAdvも再生成) | — | gloss→Advの依存が仕様として組込み済み |

受け渡し情報の差の結論: **全文を見て意味を判断できる段(選定・canon・gloss)は意味を持ち出さず、意味を最後に書く段(Adv説明)は全文を見ていない**。Std/Advは同じ記事を別callで独立に見て別の訳語に着地する(同一run同一KP 7件中2件不整合、ROOT_CAUSE_01 §3(d))。

## 2. (d) Validator・retry・fallbackの寄与(実データ、API 0)

`rc02_pipeline_stats_01.py`で現行path 26 unit(15 run)のartifactを集計:
- gloss alignment: gloss artifactのある16 unit(X)・48 itemすべて**初回ALIGN_PASS**(retry unit 0、`VALID`以外0、`qa!=PASS` 0、mapping機械検査の不合格0[record-only])。→ **gloss検査は意味品質に対し実質的に何も棄却しておらず、「全語反映」の自己申告QAが品質を押し下げる圧力にもなっていない**(仮説(b)の「mapping検査/QAがretryさせる」は否定)。
- canonicalization INVALID(23 attempt中6)は全て『有限助動詞が含まれている』(small_bag、選定側の既存defect)で意味品質と無関係。外側retry 20 attempt中3 unitのみ。
- Z(10 unit)はgloss artifactが別形式で本集計の対象外。本probeはXZ共通moduleで同一Promptのため、傾向は共通(Z固有の差は入力本文のみ、ROOT_CAUSE_01 §1)。
- 結論: **現行のValidator/retry/fallbackは意味品質に作用しない(作用してほしい方向にも、悪い方向にも)**。品質は「1回目の生成の出来」だけで決まる。

## 3. 実測(原因切り分け)

### 3-1 説明側: JA参考意味(gloss)の因果効果(probe-03b、`kp_probe_03b_gloss_variant.py`・`kp_probe_03b_result.json`)
同一KP・同一1文・同一Prompt・同一model、**日本語参考意味だけを変えて4回ずつ**生成:

| KP(文) | gloss入力 | 説明に`acceptable/allowed`が入る | 例 |
|---|---|---|---|
| `draw a line`(The words draw that line simply) | なし | 0/4 | to set a limit or show where one thing ends and another begins |
| | 線を引く | 0/4 | to set a limit or boundary between things |
| | **一線を引く** | **3/4** | to set a clear limit on what is acceptable or allowed |
| | 境界線を引く | 0/4 | to decide where one thing ends and another begins |
| | 区別をはっきりさせる | 0/4 | to make a clear distinction between things |
| `Carry the Load`(…Large Bags Carry the Load) | なし | 字義寄り 0/4 | to handle most of the weight, work, or responsibility |
| | 荷物を運ぶ | 字義寄り 2/4 | to hold and transport the things that need to be moved |
| | 重い負担を引き受ける | 字義寄り 0/4 | to take on most of the work or responsibility |

→ **Adv説明の「acceptable」型の狭さは、記事の話題ではなくStd glossの訳語(一線)が原因**。ユーザー例の「Std=一線を引く(成功)」と「Adv=狭い」は同じ原因の表裏で、Stdを良くするとAdvが悪化する関係が現行構造に埋め込まれている。A-3 v3はこの入力経路を直さず、Promptで症状だけ抑えたため『一般義への逃げ』の副作用が出た(§4)。

### 3-2 構造アーム比較(probe-03、14 KP×各2回=28行、Judge=claude-sonnet-5-5 1系統E2。`kp_probe_03.py`・`kp_probe_03_results.jsonl`・`kp_probe_03_report_out.txt`)
難例中心14KP(`draw a line, pull someone under, shine a light on, reach for someone's wallet, Carry the Load, brace yourself for, apply one's findings, refueling support, execution bell, leap into action, take the wheel, bring in, hold on, letter of introduction`、X11/Z3)。説明の入力条件だけを変えた:

| arm | 入力/構造 | PASS(sense∧core∧single) | sense_ok | core | single | 所見 |
|---|---|---|---|---|---|---|
| E0 | 現行(1文+JA gloss) | 22/28 (79%) | 28/28 | 26/28 | 23/28 | 基準。glossの質に依存(§3-1) |
| E1 | 1文のみ(glossなし) | 19/28 (68%) | 28/28 | 26/28 | 21/28 | 連想の伝染は消える。**`A or B`併記が増える**(single低下) |
| E2 | 1文+gloss+**記事全文** | 17/28 (61%) | 26/28 | 24/28 | 19/28 | 文脈量を増やしても改善せず悪化(`reach for someone's wallet`が逸脱) |
| E3 | 1文+gloss+**同じgloss callが決めたcore_sense(中心義の正本)** | **13/28 (46%)** | 22/28 | 20/28 | 17/28 | **最悪**。`take the wheel`・`Carry the Load`・`reach for someone's wallet`で用法判定(字義/比喩)が外れ、説明が固定される |
| E4 | 1文のみ(glossなし)+**説明call内で用法→中心義→説明の順に決める** | 19/28 (68%) | 25/28 | 22/28 | **28/28** | 併記は消える(single 100%)。`take the wheel`・`bring in`は独立判断で正しい側に、`draw a line`は「決める…どこで終わりどこから始まるか」(目標に近い)。ただしJudgeが「…に限定」と指摘する行が`pull someone under`等 |

注意(信頼度): n=28/arm、Judge1系統、差は±数行。**E2・E3の悪化は系統的(複数KPで同方向)で有意と見る。E0/E1/E4の間(22/19/19)はJudge strictness(下記)の影響が大きく、優劣を決められない**。Judge(`core`)は「燃料を入れる支援」を『燃料補給に限定』と誤判定するなど、**表現自体の意味(定義)と記事固有条件を区別できない偽陽性**が多い(E0/E4の不合格ノートの約半数)。→ 検証ではJudge基準(core)の修正が先に必要(DESIGN_03 §6)。
(`E3`の悪化は「sense decisionをluna 1 callで固定」した場合の結果。より高精度のmodelで決めれば別になる可能性は未検証=DESIGN_03のTrial arm。)

### 3-3 Std側: gloss Promptの「全語反映」句・用法先決めの効果(probe-03、同14KP、G0/G2=各2回、G1=1回。生成のみ・目視1名[Sonnet]判定、API Judgeなし)
| arm | 変更 | `draw a line`の日本語 | NG(字義・逐語・狭すぎ)の目視 |
|---|---|---|---|
| G0 | 現行Prompt | 線を引く / 線を引く | 6/28 (`draw a line`×2, `Carry the Load`×2[荷物を運ぶ], `reach for someone's wallet`×2[誰かの財布に手を伸ばす]) |
| G1 | 『(目的語・補語・修飾語を含む**すべての語**)』句を除去 | 境界線を引く | 3/14 (21%)(G0と同率。`draw a line`・`Carry the Load`・wallet) |
| G2 | **用法先決め**: 本文の該当文を引用→usage_type(字義/比喩/句動詞/用語)→core_sense_en(英語1文)→日本語gloss | 区別をはっきりさせる / 区別する | 7/28 (`Carry the Load`×2, wallet×2, `take the wheel`×2[車を運転する]、`refueling support`×1[空中給油=記事固有の追加]) |

- G1: **「全語反映」句は原因ではない**(NG率不変、`draw a line`は「境界線を引く」のまま)。
- G2: `draw a line`(線を引く→区別)・`shine a light on`(光を当てる→明らかにする)・`bring in`(持ち込む→取り入れる)は慣用義側に動くが、`take the wheel`(ハンドルを握る→車を運転する)・`refueling support`は悪化。**差し引きはほぼ0**。`Carry the Load`・`reach for someone's wallet`は両armとも字義のまま。
- 共通: 用法判定(字義か比喩か)が外れるKPは、Prompt/構造を変えても**同じKPで外れ続ける**(`Carry the Load`・wallet)=**モデルの判断力が律速**している可能性。これは現在のmodel(gpt-6-luna)・effort high(Production同一)での結論で、**上位modelでの再現はこのprobeでは未検証**(費用上、Sol 1 callが約2円のため)。
- 参考(Std候補の評価): ユーザー目標の「一線を引く」は`G0/G1/G2`の今回の6生成では出なかった(A-1 Trialのa1gでは1/6のみ)。`区別をはっきりさせる`は中心義としては適切だが、ユーザーが望む「慣用的な日本語」かは**ユーザー判断事項の可能性**(DESIGN_03 §6)。

## 4. (e) 既存承認仕様・過去Trialとの関係

- Adv説明: `CURRENT_SPEC.md:2032`(2026-09-28ユーザー正式採用)=Trial-02 B候補。`explanation_en`仕様文を逐語再利用、語数目安15、新規Fact不可。`PROMPT_SHA256`が逐語性の機械証拠(`er019_family_x_kp_explanation_01.py:54-85`)。**Prompt文(`japanese_reference_meaning…`行)を変えるのは承認済みB仕様の変更=ユーザー判断**。A-3 v3(Prompt追記)も同じ理由で採用不可(PROMPT_SHA256変更)。
- Std gloss: 承認規則=『短く自然な日本語グロス』『辞書的に正しいだけでなく平易な現代日本語』『直訳調を避ける』『括弧禁止』(`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`をそのまま抽出、`er003_key_words_gloss_alignment.py:40,359-374`)。**慣用句の語義選択規則は承認されていない**(新規の品質規則は承認事項)。
- Trial-02(`docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/TRIAL_RESULT_02.md:72`): 独立した一般化LLM工程=REJECTED。→ **本件の再設計も新規LLM call 0を維持**。
- 旧db_hybrid(辞書見出し形+辞書側の義): 辞書義を渡していた旧経路は`pull someone under`等の一般形を作れた(ROOT_CAUSE_01 §4)が、fulltext_p2移行(OPEN-454)で入力が本文surface起点になり、意味供給元が無くなった。**辞書資産(定義・慣用義のDB)は現リポジトリに無い**(Grep: key phrase DB関連はdb_hybrid時代の選定結果のみ。`hint`として使える慣用句辞書は未整備)。
- KPQ①②(OPEN-458)・JRE・OPEN-454: 一般化/選定/音声側で、意味生成とは無関係(ROOT_CAUSE_01 §4)。
- A-1(canonicalization規則5・参照語の不定化)は維持。A-1で『その』混入(Std)と`draw that line`の指示語は解消済み。**未解決は上記(b)(c)の二点**。

## 5. 層別分析(A3_verify 92行、`rc02_stratify_01.py`、API 0)

説明call入力のJA参考意味を目視1名(Sonnet)で3区分し、現行(E0)/A-3 v3(E3)の不合格率を層別:

| 層(JA参考意味の性質) | KP例 | n行(E0) | **core不合格**(記事固有条件混入) E0→v3 | **sense不合格**(本文意味ずれ) E0→v3 |
|---|---|---|---|---|
| N: glossに記事固有の条件を含む | apply one's findings(研究結果)・execution bell(処刑の時)・refueling support(飛行中の航空機) | 6 | **5/6 (83%)** → 2/6 (33%) | 0/6 → 0/6 |
| L: gloss自体が字義・逐語寄り | Carry the Load・pull someone under・reach for someone's wallet・take the wheel・earn such trust | 14 | 4/14 (29%) → 4/14 | **3/14 (21%)** → 4/14 (29%) |
| O: その他 | (上記以外33KP) | 72 | 8/72 (11%) → 4/72 (6%) | **1/72 (1%)** → 3/72 (4%) |
| 全体 | | 92 | 17/92 (18%) → 10/92 (11%) | 4/92 (4%) → 7/92 (8%) |

- **gloss N区分(92行中6行=7%)だけでcore不合格17件の29%(5件)**、gloss L区分(14行=15%)がsense不合格4件の75%(3件)を占める。glossが健全(O)の場合はcore 11%/sense 1%。→ **Adv説明の失敗の大半はglossの質に従属している**(因果は§3-1で別途確認。ラベルは目視1名で境界判断を含み、selection biasあり[N/Lに難例が偏る])。
- 文の長さ(短10語以下/中/長17語以上): core不合格 17%/24%/14%、sense不合格 3%/9%/0% → **1文の長さとは相関が弱い**(「1文だけ渡すから狭くなる」は主因でない。E2=全文投入も改善なしと整合)。
- KP単位のトレードオフ(E0→v3): core不合格が減ったKP 8、増えたKP 3、同じ27。sense不合格が増えたKP 4、減ったKP 2。**「記事固有条件を減らす」と「本文の意味を保つ」が同じ軸のトレードオフ**で、A-3 v3(Prompt指示)は軸上を動かしただけ(総合PASS 72%→73%)。入力の質(gloss)を変える方が軸の外から効く(§3-1)。
- 「日本語参考意味が逐語のとき説明も逐語化する率」: 層Lで説明のsense不合格 21%(層Oの1%の約21倍)。

## 6. 仮説(a)の最終整理

「各工程が独立にLLMに意味を推定させ、中心義を1回決めて共有する構造が無い」→
- 事実: 意味を明示的に決める箇所は無い(選定・canon=意味出力なし、gloss=日本語1本、Adv=英語1文)。揺れ・不整合の一因。
- ただし**共有そのものは解にならない**(E3: 悪化)。理由は、意味決定が1回の判断で、その判断が外れる(字義/慣用の誤り)KPが固定的に存在し、独立した第2の判断(Adv説明が1文から自力で読む)が誤りを訂正していたから(`take the wheel`のsense_ok: E0 2/2、E3 1/2[rep1は3項目とも不合格])。
- 実際に効いていた構造欠陥は「**共有でなく一方向の伝染**」: glossの訳語がAdvの意味を決めてしまう(§3-1)。

## 7. 限界・未検証

- Judge1系統(Sonnet)+目視1名(Sonnet)。表現自体の意味と記事固有条件を区別するJudge基準(core)に偽陽性があり、E0/E1/E4の優劣は未確定。本検証前にJudge基準の修正が必要。
- n=14 KP×2回(難例偏り)、model=gpt-6-luna(Production同一)のみ。上位model(gpt-6.1-sol)の字義/慣用判定精度は未測定(費用上)。
- probe-03のG arm・E arm は**Prompt案の最終化ではなく原因切り分け**。G2のPrompt文・E4のschemaは採用案ではない。
- Z(物語)はKP 3件(`pull someone under`・`letter of introduction`・`execution bell`)のみ。X/Z差の検証は本検証計画に含める。
- `take the wheel`等の本文意味の「正解」は目視判断(Fable再確認対象)。

## 8. 費用・証跡

- 費用: probe-03 gloss 70 call + 説明 140 call + Judge 4バッチ+1バッチ=**13.427円**(`kp_probe_03_paid_calls.jsonl`)。上限15円内。委任_02の追加費用には算入しない新規計上。
- 証跡: `kp_probe_03.py`(本体)、`kp_probe_03b_gloss_variant.py`/`kp_probe_03b_result.json`、`kp_probe_03c_e4.py`、`kp_probe_03_judge.py`/`kp_probe_03_report.py`/`kp_probe_03_report_out.txt`、`kp_probe_03_results.jsonl`(全生成物)、`kp_probe_03_summary.json`、`kp_probe_03_paid_calls.jsonl`、`rc02_pipeline_stats_01.py`、`rc02_stratify_01.py`。再現は各scriptの再実行(Judge cacheは`er112_output/kp_gm_trial_01/judge/sonnet/cache.jsonl`に追記)。
- Production・Prompt・template・flag・記事B成果物の変更0(`git diff`で`er003_*`/`er019_*`/`er105_*`/テンプレート無変更、本委任で追加したのは`docs/research/…/`配下のDEV script・結果のみ)。
