# Opus Context Packet: OPEN-233 Stage 2降格の確認構造(案S1、降格の2-of-2)、Opus独立技術レビュー#10(条件A)

作成: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_67)、2026-10-04。雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。読み取り専用レビュー。Production採用可否は判断しない(人間ユーザーのみ)。

---

## (a) 論点(限定)

管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_67)。読み取り専用レビュー(ファイル作成・編集なし)。対象は設計案S1(降格の2-of-2)であり、Production採用可否は判断しない。

背景(2行): rep25(委任_66)で、Checker(Stage 1)がMAJORで検出したSafety-critical B3(因果`so`のclaim)を、Stage 2(body rubric V7b、1 call)がACCEPTABLEへ降格し、Rewriteされず合格した(Safety KPI=重大Fact見逃し0件に反する事象)。同一入力の再実行(V7b n=10)は10/10 BLOCKINGで、原因は1回判定の非決定性と判断している。

1. **単独LLM判定による降格は、重大見逃し0と両立するか。** 「Checker MAJOR→Stage 2が非BLOCKING」(rep24: MAJOR 102件中68件)は通常の経路であり、この降格が確率的な単独判定であることを、Safety KPIに対してどう評価するか。
2. **案S1の2-of-2は十分か。** 見逃し率p→p²の仮定は妥当か。同一prompt・同一入力・既定temperatureの再呼び出しの独立性(claim難易度による相関、B3はR3'''で4/26・V5で2/2が非BLOCKING)をどう見るか。S1後も残る見逃し率は許容してよいか、より強い構造(3回、別prompt)が要るか。
3. **より単純な構造はないか。** 例: MAJORは降格不可(QUALITY/MINORのみStage 2対象、ただしrep24では68/102 MAJORがRewriteへ回る)、降格はQUALITYまで(ACCEPTABLE禁止)、Stage 2の1回目がreasoning少の場合のみ再判定、等。
4. **過剰Major・不要Rewrite・Human Reviewを増やさないか。** 2回目だけBLOCKINGのclaim(率q、未測定)がRewriteへ回る。qの限定測定(rep24の68件、約30 call=約¥4)を実装前に行うべきか、実装後のrep25再開で測れば足りるか。
5. **費用。** 追加30 call/38 instance-run(約¥0.11/instance-run、推定でq次第で最大+¥0.45/記事)は妥当か。+¥2/記事以内か。2回目のprompt cacheによる低減の見込み。
6. **cycle/Recheck/floor_verify/既存2-of-2との整合。** 対象集合の排他性(S1=1回目LLM非BLOCKING、既存2-of-2=1回目BLOCKING+NORMAL群、floor_verify=floorだけBLOCKING)の整理は正しいか。Opus#8指摘(2回目は`llm_materiality`で比較、`apply_floor`再適用の落とし穴)への対応は十分か。floor_verify解放済みclaimはS1の対象外としたが妥当か。
7. **Production配線時の矛盾。** `NORMAL_GROUP_INSTANCE_IDS`(評価用の正解ラベル付きinstance集合)に依存する既存2-of-2(「1回でも非BLOCKINGなら降格」)と、S1(「2回とも非BLOCKINGでなければ降格しない」)は向きが逆で、Production側にNORMAL群の概念が無い。どう整理するか。ACCEPTABLE_STAGE1経路(runner 6732行付近)へもS1が必要か。
8. (補足、判断を求める) Stage 1が代替投入(`substitute_baseline_on_stage1_miss`)であるB3は、実Productionでは「Stage 1 recall欠落」が先行リスクとして残る(既知、§10/§14)。S1はStage 1の取りこぼしには効かない。この責任分界の整理は本レビューの範囲外としてよいか。

### 論点と材料の対応チェック

| 論点番号 | 必要な材料 | (b)/(c)のどこにあるか | 不足時の扱い |
|---|---|---|---|
| 1 | 既存ログ集計、B3 claim・本文、rep24のMAJOR→非BLOCKING件数 | (b)「既存ログ集計」「B3の事実」「費用試算」 | 不足なし |
| 2 | 診断(a)(c)の実測、p推定とCI、B3の版別非BLOCKING率 | (b)「診断結果表」「p推定」 | 不足なし |
| 3 | rep24の件数(ACCEPTABLE 45/QUALITY 23、body50/hook18) | (b)「費用試算」 | 不足なし |
| 4 | qは未測定 | (b)「未測定・推測の区別」 | 未測定と明記 |
| 5 | 費用試算の式と実測単価 | (b)「費用試算」 | 不足なし |
| 6 | runner行範囲、`apply_stage2_two_of_two`適用条件、Opus#8要旨 | (c)、(b)「Opus#8との関係」 | 不足なし |
| 7 | `NORMAL_GROUP_INSTANCE_IDS`の定義、Production側概念の有無 | (c)、(d) | Productionコードは未確認(runnerのみ確認)と明記 |
| 8 | B3のStage 1由来(substitute_baseline) | (b)「B3の事実」 | 不足なし |

条件・発火: 条件A(新しい構造・処理フローの設計。Stage 2の判定構造=Safety処理の変更に当たる)。必須レビュー(回数上限の対象外)。既存Opus#8(`docs/pm/opus_l2_review_open233_self_recovery_08.md`)は機械floor(決定論)の整合設計とF5(floor_verify、比較・時期の2回確認)であり、本件の「LLMが降格した後に確認が無い」構造は未レビュー。Opus#8の論点2(F4の独立再判定)の「同じpromptの引き直しは新しい独立性を得ない」「`run_stage2`を呼び直すと`apply_floor`が再適用される」という指摘は、本案S1の独立性評価と実装注意点へ直接関係するため、(b)に要旨を載せる。

---
## (b) 主要数値表・要点

### 要点(5行以内)

1. 原因: rep25 B3 s1のStage 2(V7b、1 call)がACCEPTABLEを返した1回の判定のブレ。入力はrep24 cycle 1と同一(prompt sha256一致、同じbatch=1 claim、同じrubric V7b)。
2. 診断: 同一入力でV7b 10/10 BLOCKING、V7 9/10 BLOCKING+1/10 ACCEPTABLE。V7b文言起因は確認できず。ACCEPTABLEの2回(rep25、V7 run7)はreasoning tokensが少ない(306、262 vs BLOCKING回418〜893)が、n=2の相関のみ。
3. 構造: floor(5フラグ)は`changed_causality`を含まず対象外。既存2-of-2は「BLOCKING→降格」方向のみ・NORMAL群限定で、**MAJOR→非BLOCKINGの降格には確認が無い**。
4. 提案S1: Checker MAJOR+1回目LLM非BLOCKINGのときだけ2回目を呼び、2回とも非BLOCKINGのときだけ降格。追加は約30 call/38 instance-run(rep24実測、約¥0.11/instance-run)。
5. 残る不確実性: 2回目のBLOCKING率q(不要Rewrite/Human Reviewの増加)は未測定。p²は独立性の仮定に依存。

### B3の事実

- Stage 1の由来: `substitute_baseline_on_stage1_miss`(runner 6321行)。V4A再利用はB3を検出せず(既知recall欠落)、fixtureの`baseline_parsed`(V0、MAJOR)を代替投入。rep24/rep25とも同じ。
- claim(逐語): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.`
- Stage 1: severity=MAJOR、related_fact_id=HF-007、`changed_causality=true`のみtrue(他flagすべてfalse)、issue「継続していた攻撃・封鎖・タンカー安全への懸念が、20％案の撤回・置換や価格回復の原因だったかのように読める。Ledgerは、撤回・置換の理由としてトランプ氏が「非常に生産的な協議」を挙げたことと、供給懸念が継続していたことを確認しているが、両者の因果関係は確認していない。」explanation「同日に生じた政策転換と市場の値動き、および継続する懸念を、接続語「so」により因果関係として結び付けている。」
- Ledger HF-007(逐語): トランプ大統領は7月14日午前11時4分(米東部夏時間)、20％の米国償還料を、湾岸諸国による対米貿易・投資案件に置き換えると投稿した。 conditions: トランプ氏は、中東指導者との「非常に生産的な協議」に基づく決定だと説明した。causal_strength: CAUSAL_STATED_BY_SOURCE(置換の理由を述べたもの。懸念の継続が理由とは書かれていない)。HF-009 conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。
- Stage 2 rep25: ACCEPTABLE、basis=none、rewrite_hint=""(schemaに理由欄なし)、reasoning 306 tokens、¥0.1582、`floor_reason=null`、route=body、section_type=in_one_line。rep24 cycle 1: BLOCKING(`unsupported_relationship`、`narrow_scope`)。

### 診断結果表(`er052_output/open233_stage2_b3_misdowngrade_diag_01/results_01.json`、50 call、¥5.7761)

| 測定 | 入力 | n | BLOCKING | 非BLOCKING |
|---|---|---|---|---|
| (a) V7b | rep25 B3 s1と同一(sha一致) | 10 | 10 | 0 |
| (a) V7 | 同上(rubricのみV7) | 10 | 9 | 1(ACCEPTABLE、run7、reasoning 262) |
| (b) 単独 | rep25自体が1 claim batchのため(a)と同一→省略 | - | - | - |
| (c) B4-a | 委任_61 Part Aと同じgroup batch、V7b | 5 | 5 | 0 |
| (c) A2A3-0 | 同上 | 5 | 5 | 0 |
| (c) A4-0 | 同上 | 5 | 5 | 0 |
| (c) A5-0 | 同上 | 5 | 5 | 0 |
| (c) K16 | 委任_61 Part E | 5 | 5 | 0 |
| (c) K20 | 同上 | 5 | 5 | 0 |

### 既存ログ集計(Rewrite前=cycle 1のStage 2判定、27ディレクトリ・475 instance JSON、rubric版はdir名から推定)

| claim | 観測 | BLOCKING | QUALITY | ACCEPTABLE |
|---|---|---|---|---|
| B3 | 35 | 28 | 6 | 1 |
| A2A3-0 | 31 | 29 | 2 | 0 |
| A4-0 | 19 | 18 | 0 | 1(floor `changed_actor`でBLOCKING維持) |
| A5-0 | 16 | 16 | 0 | 0 |
| B4-a | 11 | 11 | 0 | 0 |

版別の非BLOCKING/観測: B3: R3''' 4/26、V4 0/2、V5 2/2、V6 0/2、V7b 1/3。A2A3-0: R3''' 0/13、V5 2/4、V6 0/4、V7b 0/10。A4-0: V7b 0/6。A5-0: V7b 0/2。B4-a: V7b 0/2。最終的に非BLOCKINGで合格した見逃しは9件(B3 7[R3''' 4、V5 2、V7b 1]、A2A3-0 2[V5])。現行rubric(V7b)の実flowは23観測中1件。

p推定(推測、CI広い): V7bのB3 実flow1/3+診断0/10=1/13(約8%、95%上側限界約36%)。Safety-critical全体 実flow1/23+診断0/30+(a)0/10=1/63(約1.6%、95%上側限界約8%)。S1のp²: B3約0.6%、全体約0.03%、B3上限で約13%(独立の仮定)。

### 費用試算(rep24ログ、確認できた数値)

- rep24: 38 instance-run、29記事、総額¥16.7238、Stage 2 call 45件(平均¥0.1402)。
- Checker MAJOR 102件のうちStage 2最終が非BLOCKING 68件(ACCEPTABLE 45、QUALITY 23)。route: body 50/hook 18。cycle別: c1 62、c2 6。(instance,cycle,route)単位のS1追加call: 30(body 20、hook 10)。
- 追加費用: 30×¥0.1402≈¥4.2/38 instance-run=約¥0.11/instance-run(29記事分母で約¥0.145/記事)。diag実測の単価は約¥0.075(cache有、2回目は同入力でcacheが効く見込み、推測)。
- Rewrite追加(推定、q未測定): q=10〜30%で約+¥0.1〜0.3/記事(1 Rewrite≈¥0.5〜0.8の推定)。**合計は+¥2/記事以内(推定)**。

### Opus#8との関係(要旨、`docs/pm/opus_l2_review_open233_self_recovery_08.md`)

- F4(floor UNDETERMINED時にStage 2をもう1回独立に呼びORで維持)は、Opus#8が「Stage 2は現行でもフラグを見ておらず、同じpromptで引き直すだけ、新しい独立性は得られない」と指摘(calibration_01.py 627〜638行にdevが入らない)。S1の2回目も同一prompt・同一入力の引き直しで、独立性はLLMの非決定性だけに依る。
- 実装の落とし穴: `apply_stage2_two_of_two`は`run_stage2`を呼び直し、その中で`apply_floor`が再適用されるため、2回目の`materiality`は常にBLOCKINGになる。`llm_materiality`で比較する必要がある。
- 結論: Fable推奨はF5(比較・時期に限る2回確認、2回とも非BLOCKINGのときだけ解放、失敗はBLOCKING固定)で、`FLOOR_VERIFY_MODE=time_only`として実装済み(既定off、rep24/25ではtime_only)。**S1は同じ「2回とも非BLOCKINGのときだけ」という原則(ユーザー判断D/選択肢3)を、floorのBLOCKINGではなく、MAJORの降格へ拡張する案**。
- 既存2-of-2(`apply_stage2_two_of_two`、委任_13): NORMAL群(評価用の正解ラベル付きinstance)でStage 2がBLOCKINGの場合のみ2回目を呼び、1回でも非BLOCKINGなら降格する(S1と向きが逆)。`bgroup_B3`はNORMAL群外のため適用外。

### 未測定・推測の区別

- 確認できたこと: rep25/rep24のJSON(Stage 1/2の入出力、flag、call_log)、runnerのコード、診断50 call、ログ475件の集計。
- 推測: p(CI広い)、reasoning tokensと降格の関係(n=2)、q、Rewrite追加費用、2回目のcache効果、S1の費用。
- 未測定: 2回目だけBLOCKINGになる率q(実装前に限定測定するか判断を仰ぐ)。

### B3記事本文(`fixture["article_text"]`、runner `build_target_instances()`のbgroup_B3)

```
# 20% Withdrawn—but the Oil Chart Was Not Finished Yet

This news feels like a short play in three acts. Act One was “20%.” Act Two brought an unexpected turn. Act Three was an unexpected move in oil prices.

The curtain rose on July 13. Trump posted that the United States would seek a 20% charge on all cargo passing through the Strait of Hormuz. The aim was to recover the cost of US efforts to keep the strait safe.

But “20%” was not a finished system. The post did not say who would pay, how the money would be collected, or what legal basis would support it. For the moment, only a large number stood at center stage.

The number stayed at center stage for about a day. Then the story took a sharp turn.

### The 20% plan changes overnight

The next day, Trump said the 20% plan would be replaced by trade and investment projects between Gulf states and the US. He cited “very productive discussions” with Middle Eastern leaders. He also said no one should charge ships in the strait, and that he disliked fees.

The change was sudden. But to read the oil move, the dates must be kept separate. On July 13, Brent rose about 10% and settled at about $83 a barrel. The rise was linked to concern about a US sea blockade of Iran, planned for the next day, and energy shipments through the Strait of Hormuz.

### The chart refuses to stay down

On July 14, after the withdrawal and replacement announcement, Brent crude futures briefly gave back some of their gains. Soon, they returned close to the high level before the announcement. At the time of reporting, Brent was up about 3%, above $85 a barrel. Its final settlement price was about $85, up about 2% from the day before.

## In one line

Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.
```

### 費用按分単位

- 按分単位: instance-run(38)、記事(29)。単価(Stage 2 call): rep24実測¥0.1402、diag cache有で約¥0.075。

### failure modeの条件差

- 条件差: B3は旧rubric(R3''')でも4/26=15%、V5で2/2が非BLOCKING(QUALITY)になり、他のSafety-critical claimより境界例。V7bの実flowは1/3、診断(a)は0/10。他のSafety-critical(A2A3-0等)はV7bで0/(23+30)。claim難易度による相関があり、pが全claim共通ではない。
- 発生条件: reasoning tokensが少ない回(306/262)にACCEPTABLE(n=2、因果は推測)。

---
## (c) 必要なProduction code/spec sectionの該当行範囲のみ

全てrunner(`er052_open233_self_recovery_flow_runner_01.py`)、Trial/検証用(Production正式pathではない)。行番号は2026-10-04時点、Grepで実在確認済み。

| ファイル | 行範囲 | この範囲が必要な理由 | Grep確認 |
|---|---|---|---|
| `er052_open233_self_recovery_flow_runner_01.py` | 2689-2905(`run_stage2`) | Stage 2のbody/hook分離call、floor/hook-aware/disclosure-gap/floor_verifyの適用順、`llm_materiality`と最終`materiality`の別 | 済(`Grep def run_stage2`) |
| 同上 | 2784-2790 | body groupで`BODY_RUBRIC_DEFAULT`を使う1 call | 済 |
| 同上 | 447-450 | `BODY_RUBRIC_DEFAULT`=V7b | 済(`Grep BODY_RUBRIC_DEFAULT`) |
| 同上 | 552-555(`FLOOR_FLAGS`) | `changed_causality`が含まれない=floor対象外の根拠 | 済 |
| 同上 | 2918-2956(`stage2_two_of_two_eligible`/`apply_stage2_two_of_two`) | 既存2-of-2の適用条件(BLOCKING→降格方向のみ、NORMAL群限定、floor不発) | 済 |
| 同上 | 6782-6827 | cycleごとのStage 2呼び出し→既存2-of-2→blocking/non_blocking分類。S1の挿入候補位置(6812行直後) | 済(`Grep apply_stage2_two_of_two`) |
| 同上 | 7438-7441(B3定義)、7478-7482、7510-7534(`detect_safety_critical_misdowngrades`) | Safety-critical判定の正本定義・検出 | 済 |
| 同上 | 6517(`compute_residual_at_pass`) | `residual_at_pass`の算出 | 済 |
| 同上 | 6307-6326(`build_target_instances`) | `substitute_baseline_on_stage1_miss`(B3のStage 1由来) | 済 |
| 同上 | 588-589(`NORMAL_GROUP_INSTANCE_IDS`) | 既存2-of-2の対象集合の定義 | 済 |
| `er052_open233_self_recovery_stage2_calibration_01.py` | 604-614(V7b)、649-689(`run_stage2_batch_variant`) | V7b文言と、Stage 2の入力構成(dev非入力) | 済(`Grep V7B`) |
| `er052_open233_stage2_b3_misdowngrade_diag_01.py` | 全体 | 診断の実行内容(runner未変更、既存Stage 2呼び出しの再利用) | 作成者として確認 |

関連ファイル(読む必要があれば): `docs/pm/design_open233_stage2_safety_downgrade_01.md`(本件の設計§1〜§6、逐語・集計の詳細)、`docs/pm/design_open233_floor_alignment_01.md` §2-4、`docs/pm/opus_l2_review_open233_self_recovery_08.md`。

---
## (d) Sonnet要約

rep25のB3見逃しは、同一入力(sha一致)に対するStage 2の1回判定のブレで、入力差・batch構成・V7b文言・floor・Stage 1差のいずれでもない(V7b 10/10 BLOCKING、V7 9/10、実flow V7bのB3 1/13、Safety-critical全体1/63)。Stage 2の降格(MAJOR→非BLOCKING)は通常経路(rep24で68/102)だが、確認が無い。案S1(1回目非BLOCKINGのときだけ2回目、2回とも非BLOCKINGでのみ降格)を推奨するが、(i)p²は独立の仮定でB3のようにclaim難易度の相関が強い場合は楽観的、(ii)2回目だけBLOCKINGの率qが未測定で不要Rewrite/Human Reviewの増加が読めない、(iii)NORMAL群の既存2-of-2は向きが逆でProduction側に概念が無い、(iv)Stage 1 recall欠落(B3は代替投入)には効かない、が残る。「MAJORは降格不可」はrep24で68件がRewriteへ回るため現実的でない。案S2(決定論ガード)は過剰Majorを増やすため推奨しない。

---

## (e) Progressive Disclosure手順(Opus向け指示文)

> 上記(a)〜(d)で診断できない場合のみ、追加でファイルを読んでよい。
> ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、
> 診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告する
> こと。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、
> 必要な事実を省いてまで読込量を減らしてはならない。

---
## (f) 入力文字数の自己計測欄

- (a)論点セクション(論点と材料の対応チェック含む): 2737字
- (b)主要数値表・要点セクション: 7046字
  - うち記事本文小節のみ: 1972字(B3本文)
- (c)Production code/spec抜粋セクション(Grep確認欄含む): 1748字
- (d)Sonnet要約セクション+(e)Progressive Disclosure指示文: 763字
- (g)発火条件+独立レビューブロック: 1460字
- packet合計文字数: 14362字(目安2〜3万字以内。範囲内)
- 前回packet(Opus#9用)との差分: 本件はB3の記事本文と診断表を転記した。Opusが元JSONやREPORTを追加で読む必要を減らす目的。

---
## (g) 発火条件の記入欄と独立レビューブロック

管理ID: PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02(`docs/pm/PM_GOVERNANCE.md` 11-3節)。

- 発火条件: **条件A**(新しい構造・処理フロー設計)。根拠: Stage 2の判定構造(MAJORの降格をLLM単独判定から2回確認へ変更する、Safety処理の変更)を新設する設計であり、既存より厳しくなる変更(降格が減る)でユーザー承認事項。
- 重複レビューの確認: 同じ内容の既存Opusレビュー: なし。関連する既存レビューは`docs/pm/opus_l2_review_open233_self_recovery_08.md`(#8、floorの整合とF5、2回確認)。本件は「LLMが降格する判定」への確認構造であり#8の対象外のため、再利用せず新規レビュー(Opus#10)とする。

【以下、`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`の貼付ブロック(逐語、改変なし。条件Aは追加観点なし)】

---
【Opus独立技術レビューの目的】
あなたの役割は「重要な技術設計に対する独立レビュー」である。Claude/Fableの案を
追認することが目的ではない。必ず次を独立に評価すること。
- そもそもその設計が必要か
- より単純な方法がないか
- 既存処理をそのまま利用できないか
- 不要な複雑化をしていないか
- 根本原因に対する対策になっているか
- 別のFailureを生まないか

【最低限、独立してレビューする12観点】
1. そもそもこの変更・設計は必要か
2. より単純な構造にできないか
3. 既存処理・既存データを利用できないか
4. 前段で取得済みの情報を後段で失ったり再探索したりしていないか
5. 不要なLLM処理を追加していないか
6. 非決定性を増やさないか
7. Human Reviewを増やさないか
8. 不要Rewriteを増やさないか
9. コストを不必要に増やさないか
10. retry / fallback / regenerationと矛盾しないか
11. Failure時に安全側へ倒れるか
12. 個別パッチではなく再発防止になっているか

【追加観点(発火条件別)】
- 条件B(同じ問題へ2回修正しても再発): 「個別バグの連続なのか、根本設計に問題があるのか」を
  必ず明示的に判定すること。
- 条件C(Production採用候補の最終レビュー): 次の6点も必ず確認すること。
  Trial専用実装になっていないか / Production全体で矛盾しないか /
  初回・retry・fallback間で仕様が一致しているか / Dangling Referenceがないか /
  Failure時に安全側へ倒れるか / QCD上の新しい問題を生まないか。
  これはユーザーのProduction採用判断を代替するものではない(採用可否は
  人間ユーザーのみが決める。あなたは採用可否を宣言しない)。

【レビューの姿勢】
Claude/Fableの案を前提として追認しない。代替案の方が良い場合は、その代替案を
明確に提案すること。結論は「必要/不要」「推奨構造」「リスク」「代替案」の順で
簡潔に返す。
---
