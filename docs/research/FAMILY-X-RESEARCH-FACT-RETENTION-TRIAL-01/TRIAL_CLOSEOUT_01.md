# TRIAL_CLOSEOUT_01: Family X Researcher Fact保持 比較Trial Closeout(委任_02)

- 管理ID: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_02(2026-10-20)。到達Status: `XRFR_TRIAL_CLOSEOUT_PENDING_FABLE`。方式別ラベルはeval機械判定(設計v02 §9-1、`classify_variant`)で、**最終ラベルはFable**。Production採用は人間ユーザーのみ。**Production変更0**(Prompt/schema/Researcher/検証/B3/Writer/Ledger・Production run dirへの書込みなし)。
- 事前登録: 設計v02(基準(a')・検索込み腕・S-check廃止)は実走前にcommit済み(`eff1fe65c`)。結果を見ての基準変更なし。ただし**1点、実走後に採点器の出典取得規則を拡張**(下記7-5に開示。全方式に同一適用、基準・閾値は不変)。
- 証跡: 検索なし=`er085_output/research_fact_retention_trial_01/{mey,muse,coffee}/s{1,2}/<方式>/`、`eval_summary.json`、`docs/research/.../COMPARISON_RESULT_01.md`。検索込み=`.../search_arm/`、`SEARCH_ARM_RESULT_01.md`。B3=`.../b3_link/`。創作照合=`adjudication_01.json`(検索なし)・`adjudication_02.json`(検索込み)。出典全文はcommitしない。
- 使用モデル: `gpt-6-luna`(effort high)=Production Researcher/検証と同一(最新上位系原則25節の例外=「Production Researcherで効くか」の比較のため。本番ラインのモデル選定は別判断)。B3確認は現行Production B3(`gpt-6.1-sol`)。

## 1. 最も推奨する改善方式と、その理由

**現時点でProduction採用候補として推奨できる方式はない(VALIDATED候補 0/5)。Production Promptは現行維持が妥当。** 判断のため、最も有望なB(構造欄)の検索込み検証を追加で行うかの判断が要る(8章)。

| 方式 | eval機械判定 | 主な根拠(事前登録基準) |
|---|---|---|
| A(Prompt第5・6観点) | **REJECTED** | 検索なし: mey KEY 0.667(E0 0.75)=改善なし、かつ創作UNSUPPORTED 1件(下記)。検索込み: 保持 0.467 vs E0 0.375=+0.09(<+0.10) |
| B(Trial専用schema actor/context→既存欄へ畳込み) | **NOT_VALIDATED_CRITERIA_UNMET**(判断候補) | mey KEY **1.0(12/12)**で(a')達成。ただし(b)一般化 muse 0.75=E0同値・coffee +0.083(要+0.15)、(c)mey CTRL 0.5(E0 1.0)の回帰、(e)muse Δfacts +2.5(>+2)。**検索込みでは未測定** |
| C(検証に省略検知1行) | **REJECTED** | mey KEY 0.75=E0同値(改善0)。VERIFIED→AMBIGUOUS化が増えB3下限2件に影響する副作用(5.参照) |
| D(A+C) | **REJECTED** | 検索なし: mey KEY 0.667(改善なし)+創作UNSUPPORTED 1件。muse VERIFIED 6/20(AMBIGUOUS 14)=B3下限2件が崩れる。検索込み: +0.125(<(a')+0.17) |
| E(保持監査LLM+1回) | **REJECTED** | mey KEY 0.75=E0同値、Fact数+15.5/呼出+1/時間 431s(E0 114s)。muse 0.938(+0.19)は改善だが費用対効果例外(f)も満たさない |

理由: ユーザー原文§2「品質が同等なら追加検索・追加LLM呼出が少なく安価な方式を優先」に従い比較した結果、**追加検索0・追加LLM0で品質を明確に上げた方式は、題材をまたいで再現しなかった**。B(追加検索0・追加LLM0)だけがmeyで12/12に到達し、特に背景項目(M-B1〜B4)をすべて保持したが、(i)別題材(muse/coffee)で改善せず、(ii)mey自体で一部CTRL(GACA 12人/309人、アデン)を落とし、(iii)Production相当の検索込みでは未検証。**「不確かなまま配線しない」**が事前登録基準どおりの結論。

## 2. 現行方式と改善候補の品質比較

### 2-1 検索なし(同一出典packet、E0/A/B/C/D/E x 3題材 x 2 sample = 36 cell。gold=gold_02、rendered Ledgerの単一Factブロックで採点)
KEY保持率(CTRL回帰、Fact数Δ対E0):

| 方式 | mey KEY | mey CTRL | mey Δfacts | muse KEY | muse CTRL | muse Δfacts | coffee KEY | coffee CTRL | coffee Δfacts | 創作UNSUPPORTED |
|---|---|---|---|---|---|---|---|---|---|---|
| E0(現行) | 0.75 | 1.0 | 0 | 0.75 | 0.0* | 0 | 0.667 | 1.0 | 0 | 0 |
| A | 0.667 | 1.0 | -1.5 | 0.75 | 0.0* | 0 | 0.583 | 1.0 | -0.5 | **1**(mey s2 F12) |
| B | **1.0** | **0.5** | 0 | 0.75 | 0.0* | **+2.5** | 0.75 | 1.0 | -3.5 | 0 |
| C | 0.75 | 1.0 | 0 | 0.75 | 0.0* | 0 | 0.667 | 1.0 | 0 | 0 |
| D | 0.667 | 1.0 | -1.5 | 0.75 | 0.0* | 0 | 0.583 | 1.0 | -0.5 | **1**(mey s2 F12) |
| E | 0.75 | 1.0 | +15.5 | **0.938** | 0.0* | +10 | 0.75 | 1.0 | +8.5 | 0 |
(*muse CTRL=U-C1「DL250万」はE0を含む全方式が未保持=差なし・回帰なし。)

- n=2 sample/cell(KEY 6観測×2=12観測/題材)のため**±0.083は1観測の差**。A・Dのmey 0.667とE0 0.75の差(1観測)はノイズ範囲で、「悪化した」とも言えない(ただし改善の証拠もない)。
- 脱落の診断(draft段階で既に無い=抽出での脱落): E0のmey脱落はM-B3(海上交易路・エネルギー市場)4/4、M-A1 2/4で、いずれも`absent_in_draft`。この脱落を回復したのはBのみ(12/12)。Eは保持監査の追加でFactが+15.5増えてもM-A1・M-B3の脱落は回復せず(KEY 0.75=E0同値)。

### 2-2 検索込み(Production経路と同一`run_researcher_for_topic`、web_search tool固定、mey、E0/A/D x 2 sample = 6 run)
出典を無料HTTPで取得し、各runが**実際に引用した出典が明示している項目のみ**を採点対象(expected)とし、Ledger(Dは検証後/E0・Aはdraft view)の単一Factブロックへの保持を判定:

| 方式 | expected観測 | 保持 | retention | 対E0 | SA(攻撃主体) | SC(紅海・海上交易路の文脈) | gold M-B1〜B4(背景) | 創作UNSUPPORTED |
|---|---|---|---|---|---|---|---|---|
| E0 | 16 | 6 | 0.375 | – | 2/2 | 0/2 | 0/8 | 0 |
| A | 15 | 7 | 0.467 | +0.092 | 2/2 | 1/2 | 1/8 | 0 |
| D | 12 | 6 | 0.500 | +0.125 | 2/2 | 1/2 | 1/5 | 0 |

- **重要な所見**: 今回の検索込み6 runでは**攻撃主体(SA)は6/6、gold M-A1は5/5保持**(E0単独でもSA 2/2・M-A1 2/2)で、Production run_mey_01の0/6(委任_01採点)は再現しなかった。一方**背景(SC+M-B1〜B4)はE0で0/10、A 2/10、D 2/7と大半が脱落**し、Productionの「背景の欠落」は再現した。→ Productionの観測された欠落は「主体」より「背景(直接の文脈)」で安定して再現する。run間でも出典(検索結果)が揺れる(同題材でもE0 s1 15回・s2 4回検索)ため、主体の脱落は確率的な可能性がある。
- A・Dの背景保持は+1観測程度で、n=2では改善とは言えない(A:+0.092は事前登録のREJECTED閾値+0.10未満、D:+0.125は(a')+0.17未満)。
- 注意: expected観測数は方式で異なる(引用出典が異なるため。E0 16/A 15/D 12)=**非対称な比較**。同一出典での比較は2-1(検索なし)、Production忠実性は2-2という分担。

## 3. Web検索回数・LLM呼出・量産単価・処理時間の比較

### 3-1 検索込み腕の実測(Production忠実、mey、2 sample)
| 方式 | Researcher検索回数(s1,s2) | 平均 | 検証検索 | Researcher費用JPY(平均) | 総費用JPY(平均) | 入力tok(平均) | 出力tok | 時間s(Researcher平均) | 追加LLM呼出 |
|---|---|---|---|---|---|---|---|---|---|
| E0 | 15, 4 | 9.5 | – | 16.99 | 16.99 | 71,827 | 7,992 | 126.5 | 0 |
| A | 14, 7 | 10.5(+1.0) | – | 18.77(+1.78) | 18.77 | 80,132 | 8,580 | 117.8 | 0 |
| D | 9, 10 | 9.5(±0) | 5, 5(Production実績5) | 17.07(+0.08) | 26.34(検証込み) | 72,528 | 8,864 | 116.4(検証込み185.2) | 0(検証はProductionに既存) |
- **Prompt変更で検索回数が増える証拠は得られなかった**: A +1.0回(許容+2回内)、D ±0。1 runの最大15回(異常STOP閾値40の下、Production実績20の下)。検索1回=JPY1.6。事前登録の検索回数判定((h)具体化: 平均+2回以内・費用+JPY3以内・検証検索10回以内)は**A・Dとも満たす**。ただしn=2の検出力は低い(同題材でE0が15回と4回)。
- 実測の検索回数: 総検索69回(Researcher 59回+Dの検証10回)。検索由来が費用の大半(Productionと同じ構造。Researcher 1runの費用7.5〜26.5円は検索回数にほぼ比例)。

### 3-2 検索なしharness(同一packet、Productionの代替ではない)
| 方式 | 追加LLM呼出 | 費用JPY/cell(mey平均) | 時間s(mey平均) | 備考 |
|---|---|---|---|---|
| E0 | 0 | 0.98 | 114 | 基準 |
| A | 0 | 0.96 | 89 | 追加token +250相当 |
| B | 0 | 0.89 | 94 | 出力 +actor/context欄 |
| C | 0 | 1.08 | 121 | |
| D | 0 | 1.00 | 94 | |
| E | **+1** | 1.87 | **431** | 費用 約1.9倍、時間 約3.8倍、Fact +15.5 |

### 3-3 量産単価(70円/記事セット)への影響(Trial費用と恒常費用を区別)
- 現行Production Research+Ledger検証 = **JPY36.1/記事(run_mey_01実測)=70円目標の約52%**。うち検索20回分JPY32.0(89%)。
- A/B/C/D(追加検索0・追加LLM0): 追加は入力約+200〜330 tok・出力約+5〜10%のみ=**約+JPY0.1以下/記事(70円の約0.15%以下)**、**Prompt変更による検索回数増が確認されない限り**恒常費用は実質不変。ただし**検索回数が変動すれば1回=JPY1.6が支配的**で、本Trialではその差を検出できる標本数がない。
- E: 追加LLM呼出+1(約JPY0.9〜1.9、約+1〜3%)+時間3.8倍=費用対効果の対照としても不採用。
- D/Cの副作用: AMBIGUOUS増(下5-3)により、AMBIGUOUS化されたFactはB3の「VERIFIED下限2件」に算入されず、再評価・再生成の追加LLM呼出(約JPY7〜9/回)を誘発し得る=**間接的な恒常費用リスク**。
- Trial費用(開発費、恒常費用ではない): 本委任の実費は「9. 費用」参照。

## 4. 中東記事の欠落改善結果(Before/After、具体Fact、出典逐語照合済み)

**Before(Production run_mey_01、検索込み、11 Fact、gold_02でKEY 0/6)**
- F04: 「GACAは、10月10日のキング・ハーリド国際空港への攻撃について、12人が死亡し309人が負傷したと、10月11日の続報で発表した。」→ **誰の攻撃か(主体)なし**(出典=国連特使声明10/11は「continuing attacks ... by Ansar Allah, including the latest attack on 10 October against King Khalid International Airport」)。
- F11: 「国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し、10月10日のリヤド空港攻撃について…」→ **「Ansar Allah」が受動形で消えている**。
- 背景(Ansar Allahのモカ・バブ・アル・マンデブ進攻、紅海の商船への脅迫、海上交易路・エネルギー市場との絡み)に相当するFactは**無い**。

**After例1: 方式B(検索なし、mey s1、Trial、actor欄が既存`conditions`へ畳込み)**
- F7: 「Hans Grundberg said an attack on King Khalid International Airport in Riyadh on 10 October killed 12 people and injured more than 300, according to Saudi authorities.」 / conditions: 「【主体】Ansar Allah, identified by the Special Envoy as responsible for the attack」(出典逐語: 「the continuing attacks against civilian infrastructure ... by Ansar Allah, including the latest attack on 10 October against King Khalid International Airport」)
- F6: 「The Special Envoy said Ansar Allah’s threats against Saudi-linked commercial ships in the Red Sea undermined freedom of navigation.」 / notes: 「【背景】The Special Envoy said the threats were becoming enmeshed with a broader confrontation over maritime trade routes and stresses on the international energy market.」(出典逐語: 「These threats are becoming enmeshed with the broader confrontation over control of maritime trade routes and the stresses on the international energy market」)
- F2 notes: 「【背景】The report says the fighting followed Ansar Allah advances on Mokha and the coast along the Bab al-Mandab.」→ **背景項目M-B1〜B4が全て保持**(mey 12/12)。

**After例2: 方式D(検索込み、mey s1、Productionと同一経路+Prompt差分)**
- 「国連イエメン担当特使は、2026年10月10日のリヤド・キング・ハーリド国際空港への攻撃をアンサール・アッラー（フーシ派）によるものと述べ、サウジ当局の発表として12人死亡、300人超負傷を伝えた。」(主体保持。ただし**検索込みE0でも同様に主体は保持**されており、Dの寄与ではない)
- 背景は1/4項目(M-B1のみ)。

**まとめ**: 主体は検索込みE0でも保持された(Production 0/6は今回再現せず)。背景はE0・A・Dとも大半が欠落(Productionと整合)。**背景欠落を安定して解消したのは、検索なしのB(actor/context専用欄)のみ**。創作は出典外の主体・動機・因果を作った例なし(下5-3)。

## 5. 別記事での一般化結果(muse=正例、coffee=陰性寄り対照)

- **muse**(Reuters via CNA、Meta「Muse」ヒューマン・コンシェルジュ): E0 KEY 0.75。B/A/C/D=0.75(**改善なし**)、E=0.938(+0.19、ただしFact+10・呼出+1・時間400s)。Bは`Δfacts`+2.5(基準+2超)。Dは14/20がAMBIGUOUS化(VERIFIED 6)=B3下限に影響。
- **coffee**(ICO報告、機関報告・創作誘発対照): E0 0.667。B=0.75(+0.083、要+0.15)、A/D=0.583(悪化1観測)、C=同値、E=0.75。**創作UNSUPPORTED 0**(関税・為替・投機筋など出典にない要因を足した例なし。全65ユニークFactを出典の要因表と照合)。
- **一般化の結論**: meyのB 12/12は、別題材で再現しなかった。mey固有(出典に主体・背景が明示される報道の構造)の効果の可能性があり、n=2では判別不能。
- 5-3 創作照合(要件③): 全方式でUNSUPPORTEDは**検索なし 1ユニークFact(A/D mey s2 F12の「ダンマーム近郊のダハラン」、出典はDhahranと東部州のみ=地理付加。主体・動機・因果の創作ではない軽微)**と検索込み 0。**同種の付加は委任_01のX1(E0 Prompt・生ページ)にも出ており、A/D固有の失敗ではない**。事前登録ルール(UNSUPPORTED≥1→REJECTED)を機械適用すれば A・Dが理由としてREJECTEDだが、**この1件は軽微な地理付加であり、Fableが最終ラベルで扱いを判断**(なお、A・Dはいずれも改善基準でも未達)。数値は全Fact機械チェックで出典外数値0(単位換算を除く)。未判定0。

## 6. Ledger→B3接続確認(現行Production B3を2 call、`gpt-6.1-sol`、実費JPY15.90)
- 対象: E0 mey s1 Ledger(主体M-A1がdraft段階で脱落)とB mey s1 Ledger(M-A1=F7・M-A2=F4が`conditions`に【主体】を保持、Production schema検証PASS、`build_verified_ledger_text`で描画)。
- 結果: **B3はLedgerを解釈できた**(fact_id抽出・VERIFIED下限2件成立、min2再評価なし。ID形式、【主体】/【背景】付き`conditions`/`notes_for_writer`は破綻なし)。**ただし主体Factは採用されなかった**: E0 Ledgerは空港攻撃の被害(F8、F9)を軸に採用。B LedgerはStorylineが「国連特使のイエメン全面戦争・地域相互影響」に変わりF1・F5を採用し、F7(主体保持の空港攻撃Fact)はF8と重複として除外、F4は「別地域…」として除外。
- 含意: Ledger段で主体・背景が保持されても、**B3のStoryline選択次第で記事に入る保証はない**(n=1+1)。Ledger保持改善は記事の欠落是正の必要条件であり十分条件ではない。C1陽性対照(PC2 baseline 2/2採用)と整合するのは「Ledgerに主体Factがあり、Storylineが空港攻撃中心の場合」。B3側の選好(Storyline選択)は本Trialの対象外。
- 出力: `er085_output/research_fact_retention_trial_01/b3_link/`(Production run dir・Ledgerへ書込みなし)。

## 7. 未解決問題・リスク
1. **検索なし/検索込みの乖離**: 検索なしE0 mey KEY 0.75、検索込みE0の主体保持6/6・背景0/10、Production実績0/6。検索あり条件の出典・粒度で結果が変わる。検索なしの結果は検索込みの代理指標としては不完全(設計書§1-4の限界が現実化)。
2. **検索出典の揺れ**: 同題材でも検索回数4〜15、引用出典セットが異なる。expected項目数が方式間で非対称(16/15/12)。n=2では背景保持の差(+0.09〜+0.125)を識別できない。
3. **goldの限界**: gold_02はmey 6 KEY・muse 8・coffee 6で、単一Factブロックのregex一致。同義の別表現は不一致になる(偽陰性)。検索込み採点の出典窓判定(700字窓)は、AP等のページ内関連記事を含み得る(`RichTextStoryBody`以降のみに限定したが完全ではない)。
4. **Production同等性**: Bの検索込み経路は未実装・未測定。検索込みE0/A/Dは検証を走らせていない(E0・Aは「draft view」)ため、Productionで検証が追加で脱落/AMBIGUOUS化させる効果は含まれない(Dのみ検証込み)。
5. **採点器の出典取得規則を実走後に拡張(開示)**: 検索込み腕の初回取得で、AP(403)・SPA(JS描画)・UN Press等の本文が取れずexpectedが過少になった。基準・閾値は不変のまま、取得規則を拡張(ブラウザUA、AP本文`RichTextStoryBody`抽出、SPA`__NEXT_DATA__`のnewsDetailsのみ)して再取得・再採点した(全方式同一適用)。拡張前の暫定値はE0 0.375/A 0.429/D 0.545(取得可出典2〜4件)で、拡張後と大差ない結論(A・Dは(a')未達)。`press.un.org`の1ページ(209字)は取得不能のため、それを根拠とする1 Factは出典照合できていない(検索込みE0 s1)。
6. **C/DのAMBIGUOUS増**: C・Dは検証が「省略あり」をAMBIGUOUSとするため、muse Dで20 Factのうち14がAMBIGUOUS(VERIFIED 6)。AMBIGUOUSは`[AMBIGUOUS]`タグでB3下限2件に算入されない=B3再評価・再生成の追加費用リスク。
7. **gold外Factの未検出創作リスク**: 機械フラグ200件(123ユニーク文)+検索込み13件を出典逐語で全件照合、数値は全Factを機械チェックした。しかし機械フラグに引っかからない、数値でも固有名詞でもない種類の付加(地理付加のようなもの)は、フラグ外の目視に依存する(全Factを読んだが、見落としゼロは保証できない)。Fableの独立評価を推奨。
8. 記事保持と使用の乖離(6章): B3が主体Factを選ぶ保証はない。

## 8. Production採用に必要なユーザー判断(判断候補。ラベルはFableが付与)
1. **Bの検索込み検証を追加で行うか**(分類D、Scope追加): 現状でProduction採用候補にできる方式はない。最も有望なB(meyで12/12・背景全保持、追加検索0・追加LLM0)は検索込み未測定。検索込みB 2 sample(Researcher段のみ、約JPY35〜55、案件合算は約JPY205〜225で300円以内=承認区分C)を追加する案、あるいはBのsample増(n=4程度、検索なし約JPY6)で一般化を再確認する案。**推奨**: 検索込みB 2 run(Production忠実性が採否の分かれ目のため)。
2. **採用する場合の配線方式**(Bまたは他方式がVALIDATED後): (i)`vfl01`は15本超がimportする共用moduleのため、Family X専用の新テンプレート+単一flag(既定OFF、11-7限定例外)で隔離する/(ii)全Family共通のPrompt変更(広範な回帰確認が要る)。**推奨**: (i)。
3. **条件Cレビュー**: Production採用提案前にOpus独立レビュー(条件C)が必須(別委任)。
4. **事前登録ルールの扱い**: 創作UNSUPPORTEDの機械適用でA・Dが形式上REJECTEDになる1件の地理付加(軽微)を、最終ラベルでどう扱うか(Fable判断。A・Dは改善基準でも未達のため結論は変わらない)。
5. **現行維持とする場合**: 背景欠落(M-B1〜B4)の別の是正策(B3側のStoryline選択、Writer側)は本Trialの対象外。

## 9. 費用・実績(JPY)
| 項目 | 実費 |
|---|---|
| 検索なし本走(委任_02新規、E0 muse/coffee含む35 cell相当) | 25.83 |
| 検索込み腕 6 run(うちD検証2 run) | 124.18(検索回数 Researcher 59回+検証10回=計69回) |
| Ledger→B3接続 2 call | 15.90 |
| **委任_02実費** | **165.92**(Cap 230内、見積216〜234を下回る) |
| 委任_01実費 | 4.245 |
| 案件合算 | **170.17**(<300、承認区分C) |
| 当日累計(修正後`daily_dev_cost_01.py`) | **480.41**(<1,000。dry-run stubのJPY107.59は別枠で除外表示) |
- 異常STOPなし(最大1 run 15検索)。再起動なし。有料runの失敗・重複なし。

## 10. 方式別Status候補(eval機械判定。最終ラベルはFable。VALIDATEDでも自動配線しない)
- A: REJECTED / B: NOT_VALIDATED_CRITERIA_UNMET(判断候補・追加検証候補) / C: REJECTED / D: REJECTED / E: REJECTED
- 現行E0(Production): 無変更。

---

## §v02追記(委任_03、2026-10-20): 方式Bの検索込み追加検証+CTRL低下/Fact増の原因分析(判定基準v02は不変。結果を見て変更していない)

### v02-1 方式B 検索込み結果(Production同一`run_researcher_for_topic`、mey、2 sample、model=gpt-6.1-sol 最新世代)
実装: `er085_research_fact_retention_trial_01_search_arm.py`に`B`を追加(`patched_prompts("B")`: Researcher Promptへ`lib.B_PROMPT_ADD`挿入+`FACT_LEDGER_JSON_SCHEMA`をTrial schema[actor/context追加]へprocess内のみ差替、終了時復元。出力後にactor/contextを`fold_b_to_ledger`で既存欄へ決定論畳込み=LLM 0。`SEARCH_ARM_DEFAULT`には含めず、明示`--variants B`時のみ。test: `test_02.py::test_patched_prompts_B_diff_schema_and_restore` PASS、9 passed)。採点・出典取得規則は委任_02[拡張後]と同一。E0/A/Dの再集計値は委任_02から不変(E0 0.375 / A 0.467 / D 0.500)。

| run | 検索回数 | Fact数 | 費用JPY | 時間s | in/out tok | 引用 | 主体SA | 背景SC・M-B | CTRL | UNSUPPORTED |
|---|---|---|---|---|---|---|---|---|---|---|
| B s1 | 8 | 9 | 14.81 | 176.7 | 73,607 / 10,356 | 7/7取得可 | OK | SC MISS・M-B1〜B4 全MISS | (検索込み腕はCTRL項目なし) | 0 |
| B s2 | 10 | 6 | 18.02 | 127.4 | 79,748 / 9,320 | 6/6 | OK・M-A1 OK | M-B1 MISS | 同上 | 1(軽微な地理誤り) |
| B 平均/計 | 9.0 | 7.5 | 計32.83 | 152.0 | - | - | 2/2 | 0/2(SC期待1、M-B全期待5中0) | - | 1 |
| (参考)E0 平均 | 9.5 | 8.0 | 16.99 | 126.5 | - | - | 2/2 | 0 | - | 0 |

- retention(expected項目のうちLedgerに保持): **B 4/10=0.40 vs E0 6/16=0.375(+0.025)**。A +0.092(REJECTED閾値+0.10未満)、D +0.125(基準(a')+0.17未満)に対し、Bは最も小さい改善。検索回数はE0+2回以内(平均-0.5)・費用はE0比-0.57円で追加検索・費用増は無し(安全装置STOP40回に対し最大10回)。
- **actor/contextの充填(Productionプロンプトへ挿入しても『背景』は戻らない)**: actor 11/15 Fact(73%)、context 7/15(47%)。filled contextは『GACAは損害評価継続中』『AP報道は前日攻撃の翌日の攻撃』等、直近の個別事実の補足で、goldの『Mokha/Bab al-Mandab進出』『紅海航行・海上交易路』は出ない。背景段落を含む出典(dppa/osesgy)はs1/s2ともB runの引用に入っているが、Fact選定の段階で背景を含むFact自体が作られていない(Fact数6〜9件、検索なしBのような14件に至らない)。つまり検索込みでは欠落の本質は『欄が無いこと』ではなく『Researcherが背景を含む素材を選ぶか』。
- 創作照合(出典逐語、`adjudication_02.json`にB 8件追記): 機械フラグ7件=SUPPORTED(F03は死者13/負傷300超が別AP記事に実在=引用URL不一致[出典実在]、F06は『Al Masirah・住民』『目撃者の爆発音』が同期間AP、他は逐語一致)。機械フラグ外で手動に見つけた1件=**s2『東部州ダンマームのアラムコ行政棟』=出典(SPA N2700899アラビア語)は『الظهران(ダーラン)・東部州』=都市名の誤り(地理付加、主体・動機・因果の創作ではない軽微)**。
- **地理付加の再発計数(検索込み、mey 8 run)**: UNSUPPORTED地理付加はE0 0/2、A 1/2(s2)、D 1/2(s2)、B 1/2(s2)=**計3/8 run。全て同一出典(SPA N2700899、ダーラン)に対して、Researcherが『ダンマーム』を付加**(A/Dは『ダンマーム近郊のダーラン』、Bは『ダンマーム』)。E0は同出典を引用せず発生しない。方式固有ではなく、『都市名が短いアラビア語/SPA本文のみで確認されるとき、地名の取り違え・付加が起きる』検索込み共通の観点=採用時の検証観点(出典の地名のcharacter-level一致)として記録。主体・動機・因果の創作は全方式0。
- 機械判定(検索込み腕、v02 §9-2): 保持改善+0.025<+0.10・UNSUPPORTED=1 → **REJECTED(機械)**。Fable決定(3)により地理誤り1件はREJECTED根拠とせず、保持改善+0.025だけでも基準(a')+0.17・REJECTED閾値+0.10の両方に届かない。

### v02-2 CTRL低下(mey 0.5)とFact増(muse +2.5)の原因分析(検索なしB出力、API 0、採点規則は不変)

**(a) mey CTRL 0.5 の原因 = 『Bの出力が英語になり、日本語前提のgold正規表現に一致しなかった』採点規則の限界+1件の分割。内容としてはCTRL 4項目×2 sample全て保持されている。**
- 観測: B(検索なし)のclaimは **mey 14/14+14/14 Fact、muse 14/14+11/11 Factが英語**(E0は全て日本語、coffeeのBは日本語17/17・11/11)。B_PROMPT_ADDの『出典の表現どおりに記す』が引き金となり、英語出典を持つ2題材で出力言語が英語化した(仮説。coffeeでは起きない理由は未確認)。
- 消えたCTRL: M-C1(GACA『12人・309』)とM-C2(アデン空港『ミサイル2発・フーシ派』)が両sampleで不一致。goldのgroupsは日本語のみ((12人|12名)・(アデン)・(2発|ミサイル2))。実Fact: s1 F8『GACA stated... 12 fatalities and... 309 people injured』、s1 F11/s2 F11『two missiles/rockets launched by the Houthi group fell within... Aden International Airport』=**4/4保持**(内容)。
- ただしs2のM-C1は別理由の限界も併存: 『12 fatalities』がF7、『309 injured』がF8に**分割**され、単一Factブロック採点では(英語tolerantにしても)不一致。
- 反面、同じ英語化は他項目に有利にも不利にも働く: 例 M-B3(maritime trade routes)はgroupsに英語併記があり一致、muse U-B1は日本語のみ(電話|通話)で英語claimが不一致。よってBのKEY値にも言語起因の偏りが両方向にある。mey KEY 1.0の中身はM-B3のみ真の増(E0は『広い対立/海上交易路』を落とす。Bはcontext欄で保持=genuine)、M-A1 s1も真の増。
- 分類: CTRL 8セル項目中、消失(採点漏れ)=言語4/分割併発1(=C1 s2)。**内容の真の脱落=0**。構造化欄がCTRLを押し出した事実は無い(CTRL 4項目は各Factにそのまま残る)。

**(b) muse Δfacts +2.5(E0 10.0→B 12.5、net +5/2 sample)の内訳**
- s1(E0 12→B 14、+2): 同一事実の分割1(E0 F9『人種差別発言+副社長の謝罪』→B F11・F12)、新規だが周辺1(B F5『社内投稿: 訓練を受けたエージェントが通話を代行』=仕組み説明)。
- s2(E0 8→B 11、+3): 同一事実の分割1(E0 F4『従業員の半数+オプトアウト』→B F2・F3)、新規だが周辺1(B F4『同上、仕組み説明』)、**新規かつ必要寄り1**(B F10『人種差別発言+謝罪』=gold SEC U-B7、E0 s2は欠落)。逆にBは目的説明(E0 F7の前半)を落とした(U-R1の一部)。
- 合計: 同一事実の分割2、新規だが周辺2、新規で必要寄り1。『不要なFactを大量生成』ではなくFact数増は5件=2.5件/sample。ただし、(i)actor欄が**81%(66/81 Fact)**、context欄が77%(62/81)で充填され、nullableなのにほぼ全Factで埋まる=ユーザー要件『全Factに一律の項目を強制しない』に抵触する挙動(検索込みでは73%/47%に低下)、(ii)分割はWriter/B3の選定対象を増やす。v02基準(e)『Δfacts>+2』は+2.5で未達のまま(基準は変えない)。

**(c) 小結**: 『CTRL低下』は内容の脱落ではなく英語化(B_PROMPT_ADD起因と推定)+gold言語依存+分割による採点漏れで、Bのidea自体の欠陥ではない。ただし(1)英語出力はProductionのJapanese Ledger(B3/Writer)との整合に影響する未検証の副作用、(2)全Factへの欄充填、(3)Fact増+2.5は、検索込みでの改善が無い(v02-1)ため採用判断を覆す材料にはならない。

### v02-3 方式Bの候補Status再評価(基準v02に対して。最終ラベルはFable)
| 基準 | 検索なし | 検索込み |
|---|---|---|
| (a') mey KEY改善 | 1.0(+0.25)=充足 | 保持 +0.025 → 未達(REJECTED閾値+0.10未満) |
| (b) muse/coffee改善 | 両方未達(E0 0.75/0.667, 改善不足) | 未検証 |
| (c) CTRL退行 | 機械は退行(0.5)だが原因=採点規則の言語限界(内容は保持) | - |
| (e) Δfacts | muse +2.5(基準+2超) | Fact数 7.5(E0 8.0)=増なし |
| (d) 創作 | 0 | 地理誤り1(軽微) |
| (h) 検索回数・費用 | - | 平均-0.5回・-0.57円=充足 |
- 候補Status: **REJECTED(検索込み腕で保持改善+0.025、基準(a')およびREJECTED閾値に不達)**。検索なしでの優位(mey 1.0)は、検索込み(Production忠実)で再現しない=『出典が全文揃っているとき欄が背景を拾う』現象であって、Productionの欠落(Fact選定段階の脱落)を直さない。

### v02-4 推奨の更新
- **推奨方式なし(VALIDATED候補0)。Production現行維持。Bを含む全5方式を『検索込み保持の向上』で比較した結果、A +0.092 / D +0.125 / B +0.025 / (C・Eは検索なしでREJECTED)で基準+0.17に届く方式が無かった。** 追加検索・追加LLM呼出が少なく安価な方式(A/B/C/D)は品質で、品質が上がる方式(E)はコスト(+1 LLM・3.8倍時間)で不採用。
- 根拠: 同一方向(Researcher側で背景を拾う指示・欄の追加)の4候補が検索込みで+0.025〜+0.125にとどまる。8原則5の観点から、同種の再Trial(Bのsample増など)は見込みが乏しい。見込みの違う切り口(進言、未実施): 欠落の本質が『Researcherが背景を含むFactを作らない』ことなら、(i)背景専用の独立した短い追加call(Eの縮小版、Fact選定後に背景のみ補完)、(ii)背景はWriter/B3側で既存素材から補う、(iii)許容する(Production run_mey_01の主体0/6は再現せず、背景のみ安定欠落)。いずれもQCD影響の見積と新Trialが要る=判断候補。
- B固有の採用時懸念(参考): 英語化、全Fact欄充填、地理誤り検証観点。

### v02-5 Production採用に必要なユーザー判断(更新、判断候補。ラベルはFableが付与)
1. 本Trialの結論(推奨方式なし/現行維持)を受け入れるか、(2)の別手段Trialを承認するか(新仕様・Scope追加、見積は設計後)。
2. 背景欠落(主体は再現せず)を許容水準とするか(品質ライン判断)。
3. 地理誤り等の検索込み共通の検証観点を既存Gate(fact_check等)で扱うか(新規Gate追加なら承認要)。

## 最終ラベル(ユーザー正式決定 2026-10-20)
- A〜E全5方式=`REJECTED`(ユーザー決定①)。原文=docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_USER.md §1①(sha256=76b6552882e2a9bf2d8219cf11f188a693601d190cda1962306925d92d8dad1f)。
- 現行Researcher／検証仕様を維持。追加Trialは実施しない。Production変更0。
- Trial実費合計: JPY203.00(委任_01 4.245 + 委任_02 165.92 = 170.17 + 委任_03 32.83)。出典=本書「9. 費用・実績」(委任_01/委任_02実費行)・OPEN_ITEMS.md OPEN-427行(案件合算203.00)・docs/pm/RESULT_PACKET_XRFR3.md。
- 本Closeoutにより、§v02-5の判断候補(別手段Trial承認・許容水準・検証観点追加)は、ユーザー決定①②(背景Fact欠落=現行維持、改善Trial再開はユーザー判断のみ)で解消済み。
