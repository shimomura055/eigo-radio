# RLCT Stage 1a 人手評価(STAGE_1A_EVAL_01)

- 管理ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_06 / 評価日: 2026-10-17(JST) / 費用: JPY0(有料API・Trial再実行なし、保存済み出力のread-only評価)
- 性質: Trial評価(Production不変、未承認、採否判断なし)。到達上限Status: `STAGE_1A_EVALUATED_PENDING_FABLE`。
- 評価者: Sonnet(机上、1名)。Fable独立判定・Opusは未実施(重大判定/不一致時のみ、Fable判断)。
- 入力: `STAGE_1A_RESULTS_01.md`、`er082_output/rlct_trial_01/<article>/<method>/`(storyline_b3/selected_brief.md、result.json、_work/verify_*.json、research_ledger/)。M0のverdict/notesは`<article>/_inputs/research_ledger/fact_ledger_verification.json`。

## 1. 判定手順と限界

手順(事前登録ルールどおり、TRIAL_DESIGN_02 4-4):
1. 各記事で M0b/M1/M2/M3 の `selected_brief.md`+選定Fact ID+最終verdictを、方式名を伏せたラベル(α〜δ、順序は乱数seedでシャッフル)で並べ、対応表(blind_key)は判定が終わるまで開かなかった。M0はベースライン(REF)として明示。
2. 構成差3段階(軽微=骨格同じ / 中程度=骨格維持・焦点や展開が変化 / 重大=主題・結論・骨格が大きく変化)をM0基準で判定。品質は M0 vs 各ラベルの一対比較(面白さ/一貫性/事実整合、良い/同等/悪い)。構成差の大きさと品質の良し悪しは別列。
3. 判定を記録(scratchpad)した後でblind_keyを開き、方式名を復元。§4(中心Fact断定)と§5(Verifier再現性)は方式名を開いた後の整理。
4. 事前登録ルール: 「M0とM0bの差が中程度以上の記事では、方式差が中程度以下なら方式効果と認めない」。結果として両記事ともM0-M0b差は軽微のため、**ルールは発動せず**、方式差(中程度以上)は方式効果として扱える(ただしn=1)。

限界(ブラインドの不完全性):
- M0は基準として開示。ブラインドはM0b/M1/M2/M3の4ラベル(M0を5番目の伏せラベルにすると「M0基準の比較」が成立しないため採らなかった)。
- 推測可能な点: (1)M2/M3のBriefは `[UNVERIFIED]`/「検証済み」/「独立検証後に使用」等の注記を含み、方式群(M2/M3)が内容から識別できた(Inbound α/βは全文同一で区別不能=共有初回B3)。(2)Fact集合がM0と完全一致するもの(Coffee α)はM0bと推測できた。(3)判定前の推測は Coffee α=M0b / δ=M1 / γ=M2相当 / β=M3相当(F10の「未検証・独立検証後に使用」)、Inbound γ=M0b / δ=M1(F05の推計/確定差の注記)で、復元後の対応表と一致した。完全ブラインドではない。
- 単一評価者(Sonnet)、各セルn=1回の生成。生成のばらつきはM0bのみで推定(1記事1サンプル)。
- 事実整合は選定Factの最終verdictとStoryline/Brief断定の有無を主根拠にした。AMBIGUOUS/REJECTEDの正否そのもの(Verifierの判定が真実か)は判定対象外(§5で事実のみ整理)。

blind_key(復元後): Coffee α=M0b, β=M3, γ=M2, δ=M1 / Inbound α=M3, β=M2, γ=M0b, δ=M1。

## 2. B3構成差(M0基準、3段階)

| 記事 | 方式(判定時ラベル) | 選定Fact | 構成差 | 根拠(Storyline/選定Factの差) |
|---|---|---|---|---|
| Coffee | M0 | F02,F07,F09,F11 | 基準 | 「天候による供給懸念とアラビカ相場の記録的高騰を背景に、2025年の米国では挽いたコーヒーが値上がり…大部分は夏の関税以前からの供給不足と生豆高」 |
| Coffee | M0b(α) | 同一 | **軽微** | Fact集合・骨格が同一。Storylineは「ブラジルの干ばつなどによる供給懸念のなか、2025年2月のアラビカ先物は最高値…」と言い換えのみ。**自然ばらつきの基準=軽微** |
| Coffee | M1(δ) | F02,F07,F09,F15 | **中程度** | 供給懸念→先物最高値→関税位置の骨格は維持。F11(米小売平均+41%)がF15(シカゴ1事業者の約15%値上げ)に替わり、末尾が「カフェでも仕入れ費と飲料価格の上昇」へ焦点移動(軽微との境界、骨格維持なので中程度側と判定) |
| Coffee | M2(γ) | F01,F09,F15 | **中程度** | 「2024年のアラビカ先物急騰から米国の一杯の値上げへ」。供給不足→生豆高→関税未転嫁の因果骨格は維持するが、天候(F07)・2025年2月最高値(F02)・米小売統計(F11)が落ち、起点がF01(2024年11月)、終点が1事業者の値上げ(F15)に変化 |
| Coffee | M3(β) | F01,F09,F10,F15 | **重大** | Storylineの結論が「関税撤回が消費者価格の即時の値下がりにつながるとは限らない」(F10: 専門家の約9か月推定)へ変化。主題が「なぜ上がったか」から「すぐ下がるか」へ移り、F07/F02/F11が落ちる |
| Inbound | M0 | F01,F02,F09 | 基準 | 「8月として最多」14市場(市場別記録)は全国総数の過去最高を意味しない、が主題 |
| Inbound | M0b(γ) | F01,F02,F03,F09 | **軽微** | 14市場vs全国の骨格が同じ。F03(2019年8月比約23%増)の1要素追加。**自然ばらつきの基準=軽微** |
| Inbound | M1(δ) | F01,F02,F04,F05 | **中程度** | 主題が「市場別記録≠全国記録」から「2025年の年間記録/2026年の前年割れ/コロナ禍前比」へ移動。全国前年割れの骨格は共通、F09(14市場)が落ちF05/F04が入る |
| Inbound | M2(β) | F01,F02,F04,F05 | **中程度** | M1と同主題。Storylineに「【独立検証前の編集仮説】」、Briefに「検証状態：すべて[UNVERIFIED]」等の内部注記が残る(M2/M3のBriefは全文同一) |
| Inbound | M3(α) | F01,F02,F04,F05 | **中程度** | M2とBrief全文同一(共有初回B3、再選定0回) |

- 事前登録ルール適用: Coffee・Inbound ともM0-M0b差=軽微。方式差はCoffee M1/M2=中程度、M3=重大、Inbound M1/M2/M3=中程度で、いずれも自然ばらつき基準(軽微)を上回る。→ 方式効果として扱える(n=1)。
- 構成差の主因(事実): M2/M3のBriefが変わる経路は、Verifier verdictをB3入力に含めない/含める(UNVERIFIED表記・再選定)というPrompt差(RESULTS §4注記)。Inbound M2/M3は再選定0回で、初回B3(検証前)のBriefがそのまま最終Briefになっている。

## 3. 品質一対比較(M0 vs 各方式、構成差とは別列)

| 記事 | 方式 | 面白さ | 一貫性 | 事実との整合 | 理由(1行) |
|---|---|---|---|---|---|
| Coffee | M0b | 同等 | 同等 | 同等 | 同一Fact集合、言い換えのみ。F07(AMBIGUOUS)を同様に採用 |
| Coffee | M1 | **良い** | 同等 | 同等 | 末尾が個別カフェの値上げ事例で身近。F07(AMBIGUOUS)を同様に採用し事実整合はM0と同じ |
| Coffee | M2 | 同等 | 同等 | **良い** | AMBIGUOUSのF07(REJECTEDに降格)を外し、全選定FactがVERIFIED。起点→終点の鎖は明快だが天候・最高値の見せ場を失う |
| Coffee | M3 | 同等 | 同等 | **良い** | 全選定FactがVERIFIED。「すぐ安くなるとは限らない」は実用的で面白いが、F10は専門家の推定(Briefは推定と明示)で主題がM0から離れる |
| Inbound | M0b | 同等 | 同等 | 同等 | 全選定FactがVERIFIED、骨格同一 |
| Inbound | M1 | 同等 | 同等 | **悪い(軽度)** | F05(非VERIFIED、AMBIGUOUS)を中心に採用。Briefは「初回発表値は推計、確定値42,683,301、確定値として扱わない」と留保しStorylineの結論(年間過去最多)は両値で不変 |
| Inbound | M2 | 同等 | **悪い** | **悪い** | Brief/Storylineに「独立検証前」「[UNVERIFIED]」が残り、最終verdictと不整合。F05(AMBIGUOUS)を推計/確定差の留保なしで採用 |
| Inbound | M3 | 同等 | **悪い** | **悪い** | M2とBrief全文同一のため同判定 |

- 注: M0自身のCoffee BriefはF07(AMBIGUOUS: ベトナム部分が出典に無い)の「ベトナムの生産・輸出見通しへの懸念も伝えた」を無留保で含む。Coffeeの「良い(事実整合)」はこのM0の状態に対する相対評価。
- 注: Inbound M2/M3の最終Ledger(`research_ledger/verified_fact_ledger.txt`)ではF05が`[AMBIGUOUS - 断定禁止、曖昧さを保持すること]`とタグ付けされている(下書き文の「確定発表」をそのまま保持)一方、Briefは初回B3のまま。Writer側がLedgerのタグを優先するかは本評価の範囲外(未確認)。

## 4. 中心FactのAMBIGUOUS断定(R-07、測定のみ)

機械抽出(RESULTS §5)の「中心AMBIGUOUS」は、数値/8文字一致の緩いヒューリスティック(`er082_rlct_trial_01_lib.py` central_facts)で、Storyline/Briefに言及のないFactも数えている(例: Inbound F06・Coffee F12は全方式のBrief/Storylineに登場しない)。以下は原文での人手判定。

| 記事 | 方式 | 対象Fact(verdict) | 判定 | 原文引用 |
|---|---|---|---|---|
| Coffee | M0 | F07(AMBIGUOUS) | **断定** | Brief「ベトナムの生産・輸出見通しへの懸念も伝えた」(出典に記載なしとVerifierが指摘した部分を無留保。留保は寄与率のみ)。Storyline「天候による供給懸念」(検証済み部分のみ) |
| Coffee | M0b | F07 | **断定** | 同上「ベトナムの生産・輸出見通しへの懸念も伝えた」。Storyline「ブラジルの干ばつなどによる供給懸念」 |
| Coffee | M1 | F07 | **断定** | 「ベトナムの生産・輸出見通しへの懸念も伝えた。市場参加者の見通しを含むため、実際の減産や価格への寄与率が確定したとは書かない」。Storyline「ブラジルの干ばつなどを受けた供給懸念」 |
| Coffee | M2 | (F07はREJECTEDとなり選定から除外) | 該当なし(0) | Brief/StorylineにF07・ベトナム言及なし |
| Coffee | M3 | 同上 | 該当なし(0) | 同上 |
| Inbound | M0 | (機械抽出F04は選定外) | 言及なし(0) | 選定F01,F02,F09は全てVERIFIED |
| Inbound | M0b | (機械抽出F04,F06は選定外) | 言及なし(0) | 選定F01,F02,F03,F09は全てVERIFIED |
| Inbound | M1 | F05(AMBIGUOUS) | **留保あり**(Storylineの結論部分は断定) | Brief「2026年1月21日の初回発表値42,683,600人は推計値であり、後続資料の確定値は42,683,301人…初回発表値を確定値として扱わない」。Storyline「2025年に年間過去最多を記録した」(Verifierは「記録更新自体は後続値でも維持」と記載)。F06は言及なし |
| Inbound | M2 | F05 | **断定**(AMBIGUOUS理由の推計/確定差は未反映) | Brief「JNTOは2025年の訪日外客数を42,683,600人とし…年間過去最多と発表した」。留保は冒頭の包括注記「以下はすべて[UNVERIFIED]の選定候補」のみ。Storyline「【独立検証前の編集仮説】訪日外客数は2025年に年間過去最多となった一方…」。F06は言及なし |
| Inbound | M3 | F05 | **断定**(同上) | M2とBrief全文同一 |

- 件数(断定): Coffee M0=1 / M0b=1 / M1=1 / M2=0 / M3=0。Inbound M0=0 / M0b=0 / M1=0(留保あり1) / M2=1 / M3=1。
- M0/M0b比: CoffeeはM1がM0/M0bと同じ1件、M2/M3が0件(Verifierで除外)。InboundはM0/M0bの0件に対しM2/M3が各1件(M1は留保付き1件)。
- 0でない方式がある(M0/M0b含む)ため、設計(TRIAL_DESIGN_02 4-3)どおり**Trial後のユーザー判断事項**となる可能性(Fable判断)。

## 5. Verifier再現性の整理(判定ではなく事実整理)

条件: M0=既存run(2026-10-08〜10-16、上限なし、各記事1回)、M0p=本Trial同日(2026-10-17)の上限なし再検証、M1=同日の上限付き(Prompt内ソフト上限)再検証。Verifier model は全run gpt-6-luna(RESULTS 冒頭、`verifier_model_matches_m0=true`)。各セルn=1。M2/M3は選定Factのみ検証(「-」は未検証)。

| 記事 | Fact | M0 | M0p(上限なし) | M1(上限付き) | M2 | M3 | 既知欠陥 |
|---|---|---|---|---|---|---|---|
| Coffee | F02 | VERIFIED | **AMBIGUOUS** | VERIFIED | - | - | - |
| Coffee | F07 | AMBIGUOUS | AMBIGUOUS | AMBIGUOUS | REJECTED | REJECTED | 部分欠落(ベトナム) |
| Coffee | F12 | AMBIGUOUS | **VERIFIED** | **VERIFIED** | - | - | BLS前月比-0.3%は季節調整済みなのに下書きは未調整と誤記 |
| Coffee | F16 | AMBIGUOUS | AMBIGUOUS | **VERIFIED** | - | - | 輸出量は生豆のみ/USDA URLが版を固定しない |
| Coffee | F17 | AMBIGUOUS | **VERIFIED** | **VERIFIED** | - | - | USDA URLが版を固定しない |
| Inbound | F04 | AMBIGUOUS | **VERIFIED** | **VERIFIED** | **VERIFIED** | **VERIFIED** | - |
| Inbound | F05 | REJECTED | REJECTED | **AMBIGUOUS** | **AMBIGUOUS** | **AMBIGUOUS** | 推計値を「確定発表」とラベル誤り |
| Inbound | F06 | AMBIGUOUS | AMBIGUOUS | AMBIGUOUS | - | - | - |
| Inbound | F12 | REJECTED | REJECTED | **VERIFIED** | - | - | 資料の時期誤り(2025年6月20日資料を2026年の政策資料としている) |

verification_notes根拠(抜粋、原文は`<article>/<method>/_work/verify_*.json`):
- **Inbound F12(既知欠陥: 時期誤り)**: M0=REJECTED「引用資料は2026年の政策資料ではなく、第50回観光分科会の2025年6月20日資料であるため、記載された時期が誤っている」。M0p=REJECTED「提示された資料は第50回観光分科会（2025年6月20日）の資料であり、『2026年の観光政策資料』とする日付は誤りです」。M1=VERIFIED「引用された観光政策資料には、主要観光地へ向かう路線の混雑と、大型手荷物の持ち込みによる円滑な運行への支障が課題として記載されています。…」(日付への言及なし)。→ **REJECTED→VERIFIEDの昇格はM1(上限付き)のみで、同日・上限なしのM0pは昇格しなかった**(M0・M0pの2回は同じREJECTED)。M1の1回の結果であり、上限の効果かサンプリングのばらつきかを本データだけでは切り分けられない(原因は断定しない)。
- **Coffee F12**: M0=AMBIGUOUS「LedgerがBLSの前月比-0.3%を『季節調整前』としている点は不正確で、BLSの表では-0.3%は季節調整済み」。M0p=VERIFIED「前月比（季節調整前）を−0.3%としています」、M1=VERIFIED「季節調整前の前月比0.3%下落です」。→ **上限なし(M0p)でも昇格**。両runとも既知欠陥の指摘(季節調整済み)が消え、下書きの「季節調整前」を追認。F12は全方式で非選定のため実害はない。
- Coffee F02: M0=VERIFIED、M0p=AMBIGUOUS「4.3195ドルは3月限のスポット契約の高値で…契約を区別しない『アラビカ先物が4.30ドル超』は範囲が曖昧」、M1=VERIFIED「…6%超上昇し、1ポンド4.30ドルを超える過去最高値」。M0の同じ指摘は「事実の要点は正しい」でVERIFIED。→ 同一事実で上限なしでも揺れる(M0pのみ降格)。
- Coffee F16/F17: F16はM0pでもAMBIGUOUS(「131.4は『豆の輸出』の予測値で…範囲を明記していない」)、M1のみVERIFIED。F17はM0pでもM1でもVERIFIED(M0は「提示URLが7月版ではなく2025年12月版を返した」を理由にAMBIGUOUS、M0p/M1は`circulars/2026/07/coffee.pdf`で確認)。URL版問題はM0pでも解消(同日のWebに依存)。
- Inbound F05: M0/M0p=REJECTED(「確定値として扱うのは誤り」)。M1/M2/M3=AMBIGUOUS。M3の判定文は「『確定発表』とするのは不正確」と述べつつAMBIGUOUS。上限付きの3回(M1/M2/M3)が同方向、上限なしの2回(M0/M0p)が同方向。
- Inbound F04: M0=AMBIGUOUS(37人差の基準問題)、M0p/M1/M2/M3=VERIFIED(別資料で確認)。上限なしM0pでも昇格。

整理(事実のみ):
- AMBIGUOUS/REJECTED→VERIFIED昇格は、上限なしのM0pでも発生: Coffee F12・F17、Inbound F04(計3件)。M0pの降格はCoffee F02の1件。
- M1のみで起きた昇格(M0pでは起きていない): Coffee F16、Inbound F12(Inbound F05のREJECTED→AMBIGUOUS緩和はM1/M2/M3共通)。各1回のためばらつきとの切り分け不能。M0pのみ厳しい判定はCoffee F02(降格)の1件。
- 件数が少なく各セルn=1のため、上限付きが緩い方向に偏るかは統計的に主張できない。

## 6. 受入条件(原指示§7)の記事別暫定判定(**暫定**: 1a 2記事分・n=1・単一評価者)

凡例: 充足 / 条件付 / 不充足。方式は M1/M2/M3(M0p・M0bは基準)。

| 受入条件 | Coffee | Inbound | 根拠 |
|---|---|---|---|
| 採用Factに重大誤りが残らない(R-08) | 充足(M1はF07=AMBIGUOUSを検出したまま採用[a]、M2/M3は除外) | 条件付(F05=AMBIGUOUSを採用[a]、b_selected_missed=0) | RESULTS §7: 見逃し(b)0件。任意A故障注入3件×2は全てREJECTED(重大NG 0、RESULTS §8)。ただしInbound F12(既知欠陥)がM1でVERIFIEDに昇格しており、選ばれていれば(b)になる潜在リスク |
| VERIFIED降格は根拠付き | 充足 | 充足 | 降格はM0pのCoffee F02の1件のみ(根拠notesあり、M0の同指摘は『要点は正しい』でVERIFIEDだった)。M1/M2/M3の降格0 |
| 不確実FactをVERIFIEDに昇格させない(遷移0) | **不充足**(M1: F12,F16,F17。M0pもF12,F17) | **不充足**(M1: F04,F12。M2/M3: F04。M0pもF04) | 厳密基準(遷移0)は上限なしのM0pでも満たされない=基準自体のばらつき込み。誤りに見える昇格は Coffee F12(季節調整)・Inbound F12(時期)の既知欠陥2件、他(F16/F17/F04)は別資料での確認と読め、適否は別途Fable判定が必要 |
| B3ストーリー品質維持 | 条件付(構成差M1/M2中程度・M3重大、品質は面白さ/事実整合で同等〜良い、悪化なし) | **不充足**(M2/M3: 一貫性・事実整合が悪い。M1は事実整合が軽度悪い) | §2,§3。Inbound M2/M3は再選定0回でBriefが検証前のまま |
| AMBIGUOUS断定の非流入(R-07、測定) | 断定: M0=1,M0b=1,M1=1,M2=0,M3=0 | 断定: M0=0,M0b=0,M1=0(留保付き1),M2=1,M3=1 | §4。0でない→Trial後ユーザー判断事項(Fable判断) |
| 実測総費用で削減 | 充足: M1 4.1%・M2 7.7%・M3 11.2%(M0bは-3.1%=ノイズ幅) | 充足: M1 10.5%・M2 29.0%・M3 26.4%(M0b 0.2%) | RESULTS §1(本番換算)。CoffeeのM1削減(4.1%)はM0b差(-3.1%)と近くノイズ域 |
| Fact Lock・RF整合(契約検証) | 充足(全6方式PASS) | **不充足**(M0b/M1/M2/M3 FAIL、M0のみPASS) | RESULTS §6。FAILはOPEN-407(d_tags `【2019年…】`)。ラベル付きclaim(F03/F04)を選んだ方式で発生し、M0b(自然ばらつき)でも発生=方式固有ではない |
| 傾向と例外 | M2/M3のF07除外が最大の品質利点。M3は主題が重大変化 | M2/M3は最大の削減(26〜29%)だが検証前Briefが残る。F12昇格はM1のみ | §2〜§5 |

## 7. 1b進行に関する所見(判断はFable)

事実として:
1. RESULTS §10の機械判定(上限遵守率の記録・再選定loop動作・費用÷見積≦1.3・sha不変)は全て充足。評価面で新たに分かった点は下記。
2. 方式差の大きさは自然ばらつき(M0b=軽微)を超える(Coffee M3=重大)。1bでも同じM0b比較が必要(n=1のため方式効果の確度が低い)。
3. Inbound M2/M3は、再選定が発生しない場合、検証前のBrief(「独立検証前の編集仮説」「[UNVERIFIED]」)が最終Briefとして残り、LedgerとBriefでF05のAMBIGUOUS情報が揃わない構造が観測された(Coffeeは再選定1回でBriefが更新された)。1bの他記事でも再選定が0回の場合は同様になり得る(仕様変更の要否は新仕様のためFable/ユーザー判断)。
4. 機械抽出の「中心AMBIGUOUS件数」は原文判定と一致しない(過大計上)。1bでは原文判定が引き続き必要。
5. 判断候補(提案のみ、実施せず): (a)Verifier再現性(Inbound F12等)を切り分けるには同条件の反復が要るが有料。(b)OPEN-407(d_tags `【2019年…】`)がInboundの契約検証FAIL原因で、Production化時のSTOP要因になり得る(RESULTS §6)。

## 追補(委任_08): 評価手順の是正
> 根拠: Opus独立レビュー_B(`OPUS_REVIEW_B_01_VERBATIM.md`、総合判定GO)R-B9-1/R-B1/R-B5/R-B2/R-B7。Fable採択。上記§1〜§7の既存判定は変更しない(1a初回実行の評価として残置)。本追補は**補正結果(M2c/M3c)の評価と1b評価に適用**する。

1. **ラベルのマスク(R-B9-1)**: inbound M2/M3のStorylineは「【独立検証前の編集仮説】」で始まり(`inbound_tourism/M2/result.json`:62、M3:61)、selected_brief.mdにも1件ある(機械集計: 1a全12 methodのうちinbound M2/M3のみ各1件、Coffee M2/M3は0件)。上記§2のブラインド評価ではこのラベルが方式を識別させる手掛かりの一つだった(§1の「ブラインドの不完全性」(1)と同根)。今後は(a)ブラインド評価時にこのラベルを隠す(マスク)、(b)§4のR-07人手判定ではこのラベルを「Fact固有の留保」として数えない(上記§4のInbound M2/M3「留保は冒頭の包括注記のみ」判定と整合)、(c)ラベル出現件数を方式別に「方式固有の欠陥候補」として記録する。B3 Prompt文言は変更しない。
2. **R-07の基準(R-B1)**: 全方式同一基準。文字列検査によるGateは追加しない。判定NG(確定条件は満たしたが断定が残った)は別集計とし、Trial後のユーザー判断事項(新仕様は入れない)。
3. **M2c↔M3cの差(R-B5)**: 同じ選定・ほぼ同じ判定を入力にした独立2回のB3呼出であり、Brief差は「B3出力の揺らぎの標本」。案1上限の効果ではない。
4. **未成立の内訳(R-B2)**: `unmet`(REJECTED_SELECTED / AMBIGUOUS_NOT_CONFIRMED)で分けて示す。「確定条件のもとでの成立率」は案2系のみの指標。上限到達Briefは成立扱いに戻さない。
5. **集計列(R-B7)**: Coffee M2/M3+inbound M2c/M3c+1b新設計が新設計列。inbound旧M2/M3は「旧設計・参考」行のみ。
