# BASELINE_REPRO_01: ①現行再現 E0 x mey x 2 sample(+探索腕X1 x 2)

(機械採点。gold=gold_02: 2026-10-20 ①E0実走後・候補方式(A〜E)の実走前に作成。gold_01(commit 383beeb22)からの変更はM-A1の1項目のみ)

## 方式×題材 集計

| 方式|題材 | n | KEY保持(Ledger) | KEY保持(下書き) | SEC | CTRL | Fact数平均 | Δ対E0 | フラグ(未判定/創作) | LLM呼出 | 費用JPY | 時間s | 検索 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E0|mey | 2 | 0.75 | 0.75 | 0.5 | 1.0 | 14 | 0 | 9(0/0) | 2 | 0.983 | 114.1 | 0 |
| X1|mey | 2 | 0.75 | 0.75 | 0.5 | 1.0 | 13 | -1 | 5(0/1) | 2 | 1.14 | 78.0 | 0 |

## gold項目別(各セル)

- E0/mey/s1 (facts=12, {'VERIFIED': 12, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:MISS[absent_in_draft] M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:MISS[absent_in_draft] M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- E0/mey/s2 (facts=16, {'VERIFIED': 16, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- X1/mey/s1 (facts=14, {'VERIFIED': 13, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:MISS[absent_in_draft] M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- X1/mey/s2 (facts=12, {'VERIFIED': 11, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:MISS[absent_in_draft] M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK

## 創作候補フラグ(出典逐語照合が必要)

- E0|mey|s1|F2: motive_causal_marker -> SUPPORTED
- E0|mey|s1|F7: causal_stated_by_source -> SUPPORTED
- E0|mey|s1|F8: causal_stated_by_source,watch:us_israel_others -> SUPPORTED
- E0|mey|s1|F9: causal_stated_by_source -> SUPPORTED
- E0|mey|s1|F12: causal_stated_by_source -> SUPPORTED
- X1|mey|s1|F05: causal_stated_by_source -> SUPPORTED
- X1|mey|s1|F14: causal_stated_by_source -> SUPPORTED
- E0|mey|s2|F02: motive_causal_marker -> SUPPORTED
- E0|mey|s2|F06: causal_stated_by_source -> SUPPORTED
- E0|mey|s2|F07: causal_stated_by_source -> SUPPORTED
- E0|mey|s2|F10: causal_stated_by_source -> SUPPORTED
- X1|mey|s2|F1: motive_causal_marker -> SUPPORTED
- X1|mey|s2|F7: watch:us_israel_others -> SUPPORTED
- X1|mey|s2|F8: causal_stated_by_source -> SUPPORTED

---

## 所見(worker記述。数値は上表/`eval_summary.json`/`calls_real.jsonl`による)

### 1. 結論: Production(検索込み)の脱落は、検索なし・出典全文同梱では**部分再現**にとどまる
| 条件 | KEY保持(Ledger、gold_02、6項目) | 備考 |
|---|---|---|
| Production run_mey_01(検索込み、既存`verified_fact_ledger.txt`11 Fact) | **0/6**(M-A1,A2,B1〜B4すべて脱落。CTRL 4/4は保持) | `lib.match_gold`で再採点(同gold_02) |
| E0 searchless s1(12 Fact) | 4/6(A1・B3脱落+副指標B5脱落) | A1: F7は10/10空港攻撃を述べるが主体Ansar Allahなし(別出典由来のF5に主体はある) |
| E0 searchless s2(16 Fact) | 5/6(B3のみ脱落) | F08がAnsar Allah+リヤド空港攻撃を保持 |
| E0 計(n=2) | **9/12=0.75**(gold_01では10/12=0.833) | 費用JPY1.965(R 0.53/0.84、V 0.27/0.32)、時間98.5s/129.6s |
| 探索腕X1(同Prompt、出典=生ページ全文・ノイズ込み約41K文字、n=2) | 9/12=0.75(A1: s2脱落、B3: 両方脱落) | 入力量約3倍・ノイズ増では保持は変わらない |

### 2. 脱落の再現状況(項目別)
- **再現した脱落**: M-B3(海上交易路・エネルギー市場との絡み、特使の状況認識)= E0・X1とも**4/4 sampleで下書き段階から脱落**(`absent_in_draft`)。M-A1(10/11声明の空港攻撃の主体Ansar Allah)= E0 s1とX1 s2で脱落(2/4)。副指標M-B5も2/4で脱落。いずれも**抽出・構造化段階の脱落**(draft段階で既に無い。検証での脱落ではない)。XRG 委任_01の『構造化(claim化)で脱落、検証は検知せず』と同型。
- **再現しなかった脱落**: M-A2・M-B1・M-B2・M-B4(Production 0/6)は検索なしE0で4/4 sample保持。Productionでは**11 Fact全部が『1出典=1 Fact』の粗い粒度**だったのに対し、検索なし条件ではS1(国連DPPA)から4〜6 Factに分割して抽出された(E0 12〜16 Fact、X1 12〜14 Fact)。
- 検証(V0)は、E0両sampleで脱落を検知せず(AMBIGUOUS 0、REJECTED 0。XRG 委任_01の『検証は正しさのみ』と整合)。X1ではAMBIGUOUS 1件ずつ出たが、いずれも脱落検知ではなく『攻撃主体不記載/脅迫の実態不明』の曖昧さ注記。

### 3. 条件差の分析(再現が弱い理由の仮説、反証付き)
1. **粒度仮説(最有力)**: Productionは15回の検索で大量の素材(入力119,459 tok)を受け取り、出力13,549 tok(推論8,685)の中で11 Factに圧縮した。検索なし条件は素材が3,027 tok(本文切出し)で、出力は6,017〜9,946 tok→12〜16 Fact。→ 素材量/検索負荷が大きいほど1出典あたりのFactが粗くなり、主体・文脈が落ちやすい可能性。**反証の試み**: 入力量・ノイズを約3倍(Researcher入力3,027 tok→9,487 tok、約41K文字)にした探索腕X1でもKEY保持は0.75で変化なし→『ページ全文の量・ノイズ』は主因ではない。残る差は『検索toolの存在そのもの(推論予算の配分・検索結果の断片化・複数ターン)』と考えられるが、**検索なしharnessでは検証不能**。
2. **出典セット差**: Productionは11出典(SPA・AP・UN News等を含む)から、本packetは本文取得できた6出典。F01/F11の出典は含まれており、M-A1/M-A2の原文は両方ともpacketに存在する(gold引用はtestで逐語確認)。
3. **sample数**: 検索なしn=2、Productionはn=1。run間変動(A1: s1脱落/s2保持)があり、Productionの0/6が確率的に起きた脱落である可能性は除外できない。
4. **結論としての含意**: 本harnessで測れるのは『同一の十分な素材を与えたときに主体・背景が抽出されるか(E0=0.75、脱落はB3・A1・B5に集中)』であり、Productionの0/6を直接再現していない。設計書§1-4(同等性の限界)の(1)(3)が現実になった。**A〜Eの比較は『E0=0.75』を基準にしたceiling近傍での比較になる**。

### 4. 事前登録基準への影響(**設計書の判定基準(a)が数学的に厳しすぎる: Fable判断を要する**)
- 設計書§4 (a)『mey KEY保持率がE0より+0.25以上かつ0.667以上』は、E0=0.75では**1.0(12/12)**でなければ満たせない。これは事前登録時の暗黙の前提(E0が低い)が①で崩れたことによる。基準は本委任では変更していない。
- 提案(Fable判断・候補方式未実走の今なら偏りなく変更可能): (a')『E0が0.75以上の場合は、KEY保持率 ≥ 0.917(11/12観測)または E0+0.17(2観測以上の増)』、(a'')脱落が集中する項目(M-B3、M-A1、M-B5)に絞った『脱落項目回復率』を併記。
- 追加の選択肢: Productionに近い条件を作る **with-searchの比較**(Researcher段のみ、方式E0/A/B×2 sample×約JPY27=約JPY162)は、費用が大きく(案件合算で約JPY200超)、検索由来の出典揺れで固定goldとの対応が崩れるため、まず検索なしでの差(特にB3回復)を見て、候補1方式のみS-checkで確認する現行設計(§7)を推奨。

### 5. 創作(要件③)の確認(E0)
- 機械フラグ9件(s1:5、s2:4)をすべて出典逐語と照合(`adjudication_01.json`)し**全件SUPPORTED(UNSUPPORTED 0)**。内訳: 否定免責文への誤検出2(『引き起こしたと断定しない』)、CAUSAL_STATED_BY_SOURCEの付与が死傷数・特使評価の記述に対する妥当/軽微な不適切(F7等)、watch語『米国人』は死亡者国籍。全Factを目視し、主体・動機・因果の創作は見つからなかった。
- 探索腕X1: 1件の軽微な付加(X1 s1 F12『ダンマーム近郊』、地理的付加、主体・動機・因果ではない)を目視で検出(機械フラグ外)。判定には使わないが、**gold外目視が必要な理由**として記録。
- 品質所見: E0 s1 F7等、`causal_strength=CAUSAL_STATED_BY_SOURCE`が因果ではない記述に付く(enum選択の不適切)。Ledger仕様違反ではないが、B3/Writerが『出典が因果を主張した』と誤認するリスク(別論点、本Trialの対象外)。

### 6. 費用・時間(実測)
- ①E0×2(R0+V0): JPY1.965(0.797+1.168)。X1×2: JPY2.28(1.161+1.119)。**本委任の有料実費 合計JPY4.245**(上限30内)。`raw_usage_log.jsonl`(`cl.logging_context(XRFR_TRIAL_01)`)と`calls_real.jsonl`の合算で一致。web_search_call_count=0(tool未使用を確認)。
- 時間: E0 98.5s/129.6s(R 77.1/100.3s、V 21.4/29.3s)。Production run_mey_01は196.8s(R 158.9+V 37.9)→検索なしは約33〜50%短いが、Productionの検索を代替できないため直接比較は不可。
- 見積(設計書 `cost_estimate_jpy`)との差: R(mey)見積JPY1.07に対し実測0.53〜0.84、V見積0.69に対し0.27〜0.32。入力tokenは見積7K/13Kに対し実測3.0K/7.0〜8.0K(日本語・アラビア語のtoken効率)。→ 設計書の見積は約1.5〜2倍の保守側。
