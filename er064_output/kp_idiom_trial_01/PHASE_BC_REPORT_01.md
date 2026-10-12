# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase B+C 報告(委任_02、2026-10-12)

範囲: Phase B(Trial実装、JPY0)+Phase C(Coffee v4 Std/Adv初回Trial、有料)。Phase Dは実行せず準備のみ(`phase_d/GOLD_TABLE_DRAFT_01.md`)。
Production code/Prompt/DB/共有Template/共有canonicalizationは無変更(`git diff`で確認、空)。SSOT未編集。
使用モデル: **gpt-6-luna**(選定・抽出・正規化・重複QAすべて)。最新世代か: Productionの Family X KP選定が使うSUPPORT_MODEL(`er006` `SUPPORT_MODEL`)と同一。PM_GOVERNANCE 25節の例外「Productionとの比較可能性」として事前に採用(委任B8)。最新世代の最上位モデルかどうかはこのTrialでは評価していない(要Fable確認)。

## 1. B1 正規化(Rule7)先行確定test(`er064_kp_idiom_trial_01_test_01.py::B1CanonicalizationRule7`、10件PASS)

| 入力(key_phrase / display_phrase / source_span, reason) | 結果 | 意味 |
|---|---|---|
| `pump one's fist` / `pumps its fist` / `pumps its fist`, generalize | **INVALID** | pumps->pump(活用の基本形化)は`_PERSON_DEPENDENT_TO_GENERIC`表に無い |
| `pump one's fist` / `pump its fist` / `pumps its fist`, generalize | **PASS** | its->one'sの1対1置換のみ(語数同一) |
| 同上だが reason=other | INVALID | reasonが`generalize_person_dependent_reference`でないと通らない |
| `pumps one's fist` / `pumps its fist` | PASS | 活用形のまま所有格だけ一般化 |
| `pull someone's leg` / `pull my leg` / `pulling my leg` | **INVALID** | 表は my -> {one's} のみ。someone'sは許可されない |
| `pull one's leg` / `pull my leg` | PASS | |
| `pull someone's leg` / `pull your leg` | PASS | your -> {one's, someone's, somebody's} |
| `mark the date on your calendar`(6語、無変更) | **INVALID** | KEY_PHRASE_MAX_WORDS=5 |
| `mark the date`(3語) | PASS | |

**MUST達成の前提条件(設計書へ明記)**: 選定LLMのdisplay_phraseが「動詞だけ基本形、代名詞は本文のまま」(`pump its fist`)または「`pump one's fist`」の形で出る必要がある(Template L7の動詞基本形化指示が前提)。`pumps its fist`のまま出ると正規化でINVALIDになる(活用変化は表にない)。`my`->`someone's`もINVALID。Rule7の表は変更していない(OPEN-310、別管理ID・ユーザー判断)。Phase C実測では、display_phraseは 6回中5回が`pump its fist`/`pump one's fist`形(1回は`wallet pumps its fist`と主語込みで出て無変更採用)。正規化中にLLMが`pump someone's fist`を出して1回INVALIDになった(後述)。

## 2. B2 (a) placeholder/lemma照合 と 25件ラベル

実装: `er064_kp_idiom_trial_01_matcher.py`。strict版の硬化: OBJ slotが見出し末尾なら除外、placeholder以外の内容語2語以上必須、`something`/`'s`/bare `one`除外、既存の文脈不一致検出(detect_context_mismatch_v3)と除外Gateを適用、候補は`evidence=placeholder_title`+`matched_title`付きで追加のみ。パターン数 1336(Phase A strict)->1154(硬化版)。
手作業ラベル(`phase_b/placeholder_hits_labeled_01.json`、全文脈つき):

| 集合 | 件数 | IDIOM_USE | AMBIGUOUS | LITERAL_USE(字義) | WRONG_HEADWORD_SENSE(見出し義と別) | 精度(IDIOM_USE/全体) |
|---|---|---|---|---|---|---|
| Phase A strict版(400本走査の新規ヒット) | 25 | 4 | 1 | 5 | 15 | **16%**(曖昧込み20%) |
| 硬化版(Phase B) | 9(5 unique表層) | 4 | 1 | 4 | 0 | **44%**(曖昧込み56%) |
| 硬化で除外された分 | 16 | 0 | 0 | 1 | 15 | - |

結論: 硬化により「慣用義でない通常用法の誤ヒット15件」は全て除去、正しい慣用用法(`made its/his mark`、`changes my mind`)は4/4維持。残る誤りは`open your eyes`の字義用法(4件、同一表層)。Coffee v4への新規ヒットは0件(想定どおり。DB未収録)。400本あたり新規0.02件(9/400)。

## 3. B3/B6 ablation shortlist(`phase_b/ablation_shortlist_01.json`、決定論¥0)

実装: `er064_kp_idiom_trial_01_pipeline.py`。V0=Production現行の`run_stage1_and_shortlist`出力そのもの(Wiktionary公開APIを含むためstage1結果をpickleキャッシュ。V0はPhase AのINV-01記録件数と一致: Std 439/439/204/156/155、Adv 489/499/226/181/180)。予約枠: llm/placeholder由来のみ(任意flagでcap15で切られたonline hit)、上限5、cap15の外側、並び=(由来優先, 内容語の最小Zipf[希少度昇順], alphabet)。

| Level | V0 shortlist | V1(a+c) | V2(a、b1抜き) | V3(b2ルール+c) |
|---|---|---|---|---|
| Std | 26件、pumps its fist=× | 26(新規0) | 26(新規0) | 28(`pumps its fist`/`imagine your usual`追加。`pumps its fist`=○) |
| Adv | 32件(phrase 16件中 `waiting for` が cap15 で脱落)、×  | 32 | 32 | 34(`pumps its fist`/`news your wallet`追加。○) |

- `mark the date`: 全variantでshortlistに入らない(DB未収録、ルールでも取れない。b1のみが可能性)。
- online lookup hit が cap15 で切られる問題(core:385/455): Coffee両Levelでは cut online hits=0(demoted_to_phraseが0件)。`include_cut_online_hits` flag(既定OFF)を実装、診断用にcut件数を記録するのみ。実運用の扱いは未決(論点)。
- **不変条件「V0 shortlist ⊆ V1/V2/V3 shortlist」(かつ先頭順序もV0と完全一致、追加は末尾の予約枠のみ・最大5)を単体testで固定**(`B3ShortlistInvariants`)。test総数36件PASS(`phase_b/test_results_01.txt`)。

## 4. B4 (b1) LLM補助抽出 と B5 (d) 選定ガイダンス

- 抽出Prompt(`prompts/extractor_prompt_v1.txt`、sha凍結 `FROZEN_SHA_01.json`): 非透明複数語、最大5件、0件許可を明記、本文のまま2-5語、Levelを渡す。例示は`out of the blue`/`a blessing in disguise`(一般例。「本文にあるかとは無関係」と明記)と否定例`a cup of tea`/`go to school`のみ。**Coffee語句(pump/fist/calendar/wallet/coffee等)ゼロ**をtestで固定(`D5GuidanceAndNoHardcode`、Prompt全文+Trialコード4ファイルを走査)。
- 決定論検証: `build_sentence_units`のtoken列と照合、`\b`境界でraw文にも実在すること(句読点をまたぐ・書式差は拒否)、閉クラスのみ拒否、既存除外Gate適用、既存DB候補とcanonical重複は除外(追加のみ)、検証後件数上限5。shortlist候補IDへの復元(`context_sentence_id`/`surface_form`)は既存`attach_compact_context`と`correct_shortlist_source_span_consistency`をそのまま通る(testで確認)。
- 選定ガイダンス(`prompts/trial_guidance_{std,adv}.txt`、diff=`guidance_diff_{std,adv}.diff`): Production guidanceの「残りは[phrase/idiom/phrasal verb候補]区分を優先」2行を、条件付き基準へ**置換**(追記ではない)。非字義的+初回リスニングで難しいものを最優先、区分名だけでは選ばない、透明/高頻度は下げる、Std/Advで既知範囲を分ける、`llm_noncompositional`/`placeholder_title`は同じ基準で評価。重要語4+Topic1・本文出現・candidate ID契約・backup_item・CEFR非軸は維持(testで固定)。共有Template無変更(sha一致)。Productionと同じguidanceを渡した場合にTrial版のmessageがProduction関数の出力と完全一致することをtestで固定。

## 5. B7 受入基準(事前確定)と判定

| 基準 | 内容 | 結果 |
|---|---|---|
| MUST-1 | `pumps its fist`相当が両Levelで(b1)抽出3/3かつV2 shortlist 3/3 | **達成 6/6**(Std 3/3、Adv 3/3。表層が完全一致`pumps its fist`は4/6、2回は主語込み`your wallet pumps its fist`/`wallet pumps its fist`) |
| MUST-2 | 最終選定で各Level 2/3以上 | **達成 Std 3/3、Adv 3/3** |
| MUST-3 | 正規化PASS・重複QA PASS・source_span整合 | **item単位は達成、run単位は条件付き**(下記) |
| WANT | `mark the date`(3語+文脈)がshortlist/選定に残る | **未達 0/6**(抽出0/6、VL 0/6。LLMが非透明と判断しない) |
| 陰性対照で悪化0 | Phase D(本委任に含まず) | 未検証 |

## 6. Phase C 各段結果

### C1: (b1)抽出のみ x3 x 2 Level(JPY0.9286、停止条件に非該当のため続行)
| Level | run | 抽出raw件数 | 抽出された表現 | `pumps its fist`相当 | V2 shortlist |
|---|---|---|---|---|---|
| Std | 1 | 5 | your wallet pumps its fist / numbers in the ring / in stock / pushed prices up / hidden clock | ○(主語込み) | ○ |
| Std | 2 | 5 | pumps its fist / in the ring / pushed prices up / in stock / own hidden clock | ○ | ○ |
| Std | 3 | 5 | pumps its fist / in the ring / in stock / pushed prices up / its own hidden clock | ○ | ○ |
| Adv | 1 | 5 | wallet pumps its fist / in the ring / show up in / flash to a new price / clock of its own | ○(主語込み) | ○ |
| Adv | 2 | 5 | pumps its fist / in the ring / entered the market / road to a price tag / unseen clock of its own | ○ | ○ |
| Adv | 3 | 5 | pumps its fist / figures in the ring / show up in / flash to a new price / behind price increases | ○ | ○ |
- 抽出件数分布: **6回すべてちょうど5件(上限)**。0件許可でも枠埋め偏りが出た(Coffeeは比喩が実在するが、`in stock`/`pushed prices up`等の透明に近い句も5件目まで含まれる)。検証rejectは0件、既存DB候補との重複除外も0件。`mark the date`は抽出0/6。
- V2 shortlist: Std 26->31件、Adv 32->37件(予約枠5件。placeholder追加0)。
- 費用実測: 1回平均 JPY0.1548(抽出)。

### C2: VL(既存Strategy L全文方式) x3 x 2 Level(JPY2.9811)
| Level | 結果(display_phrase) | `pump(s) its/one's fist`選定 |
|---|---|---|
| Std 1 | keep raw beans in stock / pump one's fist / in the ring / reach a price tag / push prices up | ○ |
| Std 2 | pump one's fist / appear in US shop prices / in stock / raw-bean prices / push prices up | ○ |
| Std 3 | pump one's fist / hidden clock / appear in US shop prices / keep raw beans in stock / raw-bean prices | ○ |
| Adv 1 | pump one's fist / time lag / show up in / negotiate prices / raw beans | ○ |
| Adv 2 | time lag / show up in / be behind price increases / keep in stock / fall along with | × |
| Adv 3 | time lag / show up in / be behind / price measure / keep in stock | × |
- VLは Std 3/3、Adv 1/3 で`pump one's fist`を選ぶ(安定せず)。V0(DB Hybrid現行、INV-01の1回分)は両Levelとも 0。VL費用 1回 JPY0.37-0.71(平均0.50)。

### C3: V2(a+b1+c+d)選定 x3 x 2 Level -> canonicalization -> 重複QA -> source_span整合(JPY6.7458)
(V0 BeforeはINV-01記録を再利用、再実行なし。Std V0最終5=raw bean(topic)/push prices up/take time/right away/on a regular basis。Adv V0最終5=lag(topic)/price tag/show up/come down/come with。)

| run | 最終5件(display_phrase、候補由来) | pump-fist | 選定 | 正規化(初回->最終) | 重複QA | source_span整合 |
|---|---|---|---|---|---|---|
| Std1 | pump its fist[LLM] / hidden clock[LLM] / numbers in the ring[LLM] / push prices up[LLM `pushed prices up`] / raw-bean(topic) | ○ | PASS | REVIEW_REQUIRED(numbers in the ring, raw-bean) | PASS | 不一致0 |
| Std2 | raw bean(topic) / pump one's fist / in stock / in the ring / own hidden clock | ○ | PASS | **INVALID x2**(`one's own hidden clock`が原因、pump項目ではない) | 未実行 | 0 |
| Std3 | pump its fist / raw bean(topic) / hidden clock / in the ring / in stock | ○ | PASS | INVALID(`pump someone's fist`: its->someone'sは表に無い)->再試行PASS | PASS | 0 |
| Adv1 | wallet pumps its fist / lag / in the ring / clock of its own / price tag(topic) | ○(主語込みのまま採用、key_phrase=`wallet pumps its fist`) | PASS | PASS | **NG**(lag vs clock of its own) | 0 |
| Adv2 | in the ring / lag / price tag(topic) / unseen clock of its own / pump its fist | ○ | PASS | PASS(`pump one's fist`) | **NG**(lag vs unseen clock) | 0 |
| Adv3 | put figures in the ring / flash to a new price / lag / pump its fist / price tag(topic) | ○ | PASS | PASS(`pump one's fist`) | **NG**(flash to a new price vs lag) | 0 |

- 最終選定で`pump-fist`選定: **6/6**(Std 3/3、Adv 3/3)。`mark the date`: 0/6。
- **正規化INVALID率**: 試行単位 3/8(37.5%、うち2回はpump項目以外の`one's own hidden clock`が原因、1回が`pump someone's fist`)。run最終単位 1/6(Std2)。
- **重複QA**: 初回 NG 3/3(Adv全件)、Std PASS 2/2評価(Std2は正規化INVALIDで未評価)。V2は比喩候補(`clock of its own`等)が単語候補(Topic/重要語の`lag`)と意味重複しやすい。

### C3R: Production方式のredundancy retry整合確認(追加: Adv NG 3件に対し診断メモ付き再選定を各1回、JPY3.7856)
Productionの`run_key_phrases`は重複QA NGで診断メモ付きに選定からやり直す(上限POINT_OVERLAP_ARTICLE_RETRY_MAX=2)。その1回目だけを再現(`build_redundancy_diagnostic_note`をそのまま使用)。

| run | retry 1 後の最終5件 | pump-fist | 正規化 | 重複QA |
|---|---|---|---|---|
| Adv1 | pump one's fist / in the ring / show up in / lag / price tag | ○ | PASS | **PASS** |
| Adv2 | pump its fist / lag / raw beans / price measure / in the ring | ○ | PASS | **PASS** |
| Adv3 | lag / figures in the ring / behind price increases / price tag / pumps its fist | ○ | REVIEW_REQUIRED | **PASS** |
- 既存retry機構と整合: 1回のretryで重複NGは3/3解消し、pump-fistは3/3維持。上限(2回)は超過せず、独自の安全装置回避なし。
- 判定(MUST-3): item単位(pump項目が正規化PASS・source_span整合)は 6/6 初回選定で達成。run単位でgateを全PASS(正規化PASS+重複PASS)した割合は、Std 1/3(Std3のみ、Std1はREVIEW_REQUIRED、Std2はINVALID)、Adv 初回0/3 -> Production方式retry後 2/3(+1/3はREVIEW_REQUIRED=人間確認)。

### Before/After と押し出された候補の妥当性(判断材料。妥当性の最終判定はFable/ユーザー)
- Std: V0の`take time`/`right away`/`on a regular basis`(高頻度で透明に近い、INV-01で指摘済み)は V2 3/3 でそろって最終5件から押し出された。A2学習者が既知とみなせる句なので、意図どおり(ガイダンスの狙い)。`push prices up`は1/3のみ維持(2/3は`in stock`等に置換)。`raw bean`/`raw-bean`(Topic)は 3/3維持。
- Adv: V0の`show up`/`come down`/`come with`(phrasal verb。B1にはコロケーション/phrasal verbも評価する旨をAdvガイダンスに書いた)は 初回で 3/3 押し出された(retry後は`show up in`が1/3で復活)。`lag`と`price tag`は維持。**押し出しが学習価値のある表現を落としている可能性**(特に`come with`は意味が文脈依存で非字義的)。要判断。
- 新規採用された表現: `hidden clock`/`clock of its own`(比喩)、`in the ring`/`numbers in the ring`(比喩、記事内の拳闘比喩)、`in stock`(定型・透明寄り)。比喩は非透明性が高いが、`in stock`は透明に近く、抽出枠埋め偏りの影響の可能性。
- 最終5件に占めるLLM抽出由来: Std 4/5(run1)・4/5(run2)・4/5(run3)、Adv 3/5 x3。抽出5件のうち3-4件が最終選定に残る=**選定側が`llm_noncompositional`ラベル/ガイダンスに引き寄せられている可能性がある**(ラベルの効果と純粋な価値判断を分離していない。要検討)。

### C4: Prompt凍結
`prompts/FROZEN_SHA_01.json`: extractor_prompt_v1、trial_guidance_std/adv、production_guidance_before、共有Template(無変更)。Phase C途中でPrompt変更なし。

## 7. hardcode不在の確認
- Prompt(抽出・guidance)とTrialコード4ファイルにCoffee語句(pump/fist/calendar/wallet/mark the date/coffee/barista/latte)が無いことをtestで固定(36件中)。
- 評価fixture(`TARGETS`)は`er064_kp_idiom_trial_01_phase_c_run.py`(評価用runner)内のラベル判定にのみ使用、実装関数へは渡さない。ablation scriptの`TARGETS`も同様。
- guidance diff: `prompts/guidance_diff_{std,adv}.diff`。差分は「残りは区分を優先」2行の置換のみ。

## 8. 費用実績(JPY、上限20、実際に使用した累計14.44)
| 段 | 内容 | 費用 |
|---|---|---|
| C1 | 抽出 x6 | 0.9286 |
| C2 | VL x6 | 2.9811 |
| C3 | V2選定+正規化+重複QA x6 | 6.7458 |
| C3R | 重複NGのretry確認 x3(追加) | 3.7856 |
| **累計** | | **14.4411**(本件専用上限JPY50のうち残 35.56、Phase C上限JPY20のうち残 5.56) |
単価: 抽出 約0.15/回、V2(選定0.43-0.59 + 正規化0.28-0.60 + 重複QA 0.14-0.41)=1.0-1.5/run、VL 0.37-0.71。C3Rは「委任のC1-C4」外の追加確認(既存retry機構との整合確認の目的)。

## 9. Phase D 準備
`phase_d/GOLD_TABLE_DRAFT_01.md`(案、凍結前にFable確認要)。費用見積: 約JPY31.5-33.5(残JPY35.56内、余裕小)。

## 10. 未解決論点・リスク
1. **枠埋め偏り**: 抽出は6/6で上限5件。陰性対照(Idiomなし記事)で偽陽性が最終5件を押し出すリスクが最大の懸念。Phase D陰性対照が必須。上限を3に下げる/Level別基準/件数に『以下』制約の導入は設計見直し候補(今回は実施せず)。
2. **ラベル誘導の分離**: 最終5件のLLM由来比率が高い。ガイダンス(d)の効果と`llm_noncompositional`ラベルの効果を分離する追加Trial(ラベルなし/ガイダンスのみ等)が必要か要判断。
3. **主語込み抽出**: `your wallet pumps its fist`(5語)/`wallet pumps its fist`(4語)の主語込みが2/6。key_phraseとして主語込みが採用される(Adv1)と学習単位として不適切。抽出Promptへ「主語を含めない」指示を足すか、検証関数で述語中心へ縮める(LLMが出した語の範囲内でのみ)か要判断。
4. **Std正規化INVALID**: `pump someone's fist`(its->someone'sは表に無い)と`one's own hidden clock`(語追加)が原因。Rule7の表拡張はOPEN-310(別管理ID・ユーザー判断)。Trialでは変更していない。
5. **重複QA NG**: 比喩候補と単語/Topic候補の意味重複(`lag`)。Production retry 1回で3/3解消したが、retryは費用増(約+JPY1.0-1.5)と所要時間増。
6. **押し出しの妥当性**: Advで`show up`/`come down`/`come with`が押し出される。B1学習者に価値のあるphrasal verbを落とす可能性。ガイダンス文言の調整要否。
7. `mark the date`(WANT)は抽出も選定も0/6。LLM判断で透明と見なされる。DB拡充(Wiktionary追加)か、WANTを外すかの判断。
8. (b1)は「本文全文をLLMへ送らない」原則(`CURRENT_SPEC.md:1847`)と衝突(Trial限定)。Production採用には別途ユーザー判断が必要。
9. 使用モデルはgpt-6-luna(Production同一)。最新世代最上位かの確認はFable/ユーザー。
10. Opusレビュー②(条件B: 同一問題への2回修正後の再発は無し、条件C: 重要変更のProduction採用提案前)の要否はFable判断。

## 11. 成果物
- 実装: `er064_kp_idiom_trial_01_{matcher,pipeline,extractor,select,phase_c_run}.py`、test `er064_kp_idiom_trial_01_test_01.py`(36件PASS)
- `phase_b/`: scan/ラベル/ablation/test結果/stage1キャッシュ。`phase_c/`: c1_extraction/c2_vl/c3_v2(retry含む)・各summary・`cost.json`。`prompts/`: 抽出Prompt、guidance(Before/After/diff)、`FROZEN_SHA_01.json`。`phase_d/GOLD_TABLE_DRAFT_01.md`
