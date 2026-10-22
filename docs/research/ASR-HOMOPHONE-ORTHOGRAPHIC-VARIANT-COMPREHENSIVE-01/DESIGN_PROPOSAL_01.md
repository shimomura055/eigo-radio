# DESIGN_PROPOSAL_01(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01、2026-10-22。設計・未配線プロトタイプ・オフライン検証。API 0・費用0・Production既存ファイル編集0)

Status=`INVESTIGATION_DESIGN_PENDING_OPUS`(未承認・未配線)。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDのいずれでもない。品質原則『発音が同一なら同等、異なるものは同等にしない』はユーザー承認済み。具体方式はOpusレビュー+検証後にVALIDATED->ユーザー採用判断。

## 1. 設計の要点(1ページ版)

- **何を**: 期待文(canonical)と転写(ASR)を『発音(CMU音素列)として同値か』で判定する**共通層**を1つ作る(`er109_asr_orthographic_equivalence_01.py`、純関数 `evaluate(canonical, asr) -> EquivalenceResult`)。
- **どこに**: `val.classify_asr_match()`ラッパー(`er006_preprod_hardening_01_validation.py:1251`)の**末尾**。既存の baseline -> 標準contraction展開が**どちらも不合格だったときだけ**1回呼ぶ。合格へ変える方向にしか作用しない(既存の合格を変えない=構造的に回帰0)。OpenAI/Azure/Whisperの3票・KP票・Store再利用・X引継ぎは全て`classify_asr_match`経由(INVESTIGATION §3)なので、**1点で全経路に同一原則が掛かる**(Family別パッチ不要)。
- **どう判定**: ①文をunit列(語・数・記号・略語・頭字語)に分割し、unitごとに『読みの候補=CMU音素列の集合』を作る(数は基数/序数/年/小数/%/通貨/時刻/分数/'sの読み、記号・略語は閉じた表)。②canonical/ASRのunit列を`difflib`で整列し、表層が同じunitは同値。③差のあるspanごとに、語だけのspanは**承認済みの既存条件を超えない**(同数は位置ごとのCMU同音=既存1:1同音救済と同じ単位、個数が違う1:nは『綴り連結一致』[承認済みdespaced規則]または『er094の承認済み多語同音条件』を純関数のまま再利用)、数/記号/略語/頭字語/contraction展開を含むspanは音素列集合の交差で判定。④どれか1つのspanでも交わらない/CMU未登録/解析不能/長すぎる(>6 unit)/片側が空(欠落・付加)なら**全体を非同値(fail-closed)**。
- **効果(オフライン実測)**: 機械生成の正例で同値率 **KP 100%(既存90.7%)・本文99.2%(既存85.4%)**、負例(KP 3,049・本文3,749)で**新規誤同値0**、既知の問題音声21件由来の転写45件で**新規PASS 0**、`one`<->`1`・`one's`<->`1's`は同値(KP/Whisperを含む全経路)。
- **コスト**: 追加API 0、1.2 ms/判定(ローカルCPU)。偽NG由来のregenerate/Secondary(Azure)呼出が減る側のみ(増える経路なし)。

## 2. 位置・接続・重複回避

### 2-1 位置(配線案。**未実施**。次委任以降)
```
classify_asr_match(canonical, asr, ..., segment_id, role)
  1. [既存] Tier1(5 role限定のearly-exit)
  2. [既存] _classify_asr_match_core (EXACT/NORMALIZED/despaced/protected/同音候補/ratio...)
  3. [既存] baseline不合格 -> 標準contraction展開で再判定 (TRANSCRIPT_STYLE_NORMALIZED_MATCH)
  4. [新規・既定OFF] er109.is_enabled() かつ er109.evaluate(canonical, asr).equivalent
        -> ClassificationResult("ORTHOGRAPHIC_EQUIVALENT_MATCH", should_pass=True, should_retry=False,
                                 orthographic_equivalence_info=EquivalenceResult.audit())
  5. [既存] telemetry追記(不合格時のみ)
```
- 新しい返り値ラベルは`VALID_CLASSIFICATIONS`(val:956)へ追加、`ClassificationResult`にoptional field(`orthographic_equivalence_info=None`、既存dataclassと加算互換)。
- 非KPの最終ANDゲートの再否定を避けるため、`APPROVED_EQUIVALENCE_BASES`(`er078_asr_unified_judge_01.py`:68)と`_equivalence_basis_of`(`er006_secondary_asr_01.py`:772)に基底名を1つ追加(**既存の拡張点そのもの**。Tier1/数字ゲート例外と同じ扱い)。Secondary側ゲート(`er078_asr_unified_judge_01.py`:555 `svg`算出・:599 `vote is None and (svg.kind==DIFF or sneg)`)も、Secondaryの合格ラベルが本層のものなら同じ基準で除外する。
- Production変更ファイルは配線時に3つ(val・`er006_secondary_asr_01.py`・`er078_asr_unified_judge_01.py`)+フラグ読取。Whisper票(`er104._classify`)・Store再利用・X引継ぎ・retry/fallback/resumeは`classify_asr_match`経由のため**追加変更不要**(INVESTIGATION §2最下段)。

### 2-2 既存機構との関係(再利用/統合/置換しない)
| 既存 | 扱い |
|---|---|
| CMU取得`homophone_en._phone_variants` | **再利用**(新規辞書なし) |
| 標準contraction表`val._ALL_STANDARD_CONTRACTIONS` | **再利用**(contraction unitの読み候補に展開形を加える。独自表なし) |
| 多語同音`er094.multiword_span_equivalent_v3` | **再利用**(1:n語spanの承認済み安全条件=単一文字token禁止/canonical3字未満禁止/V8 FW2/entity代表発音を**そのまま継承**。広げない) |
| 複合語分かち書き(despaced) | **同基準を継承**(綴り連結一致のspanは承認済み規則と同じ扱い) |
| 固有名詞G9(代表発音のみ・entity_like) | **尊重**(canonical側の大文字始まり/外来語は代表発音のみ) |
| Tier1(5 role)・数字ゲート例外・NUMERIC_EQUIVALENCE_MATCH | **置換しない**(先に走り、不合格時のみ本層)。Tier1非適用のKPは本層が数の表記差を受ける(KPへのTier1拡張を別に行う必要がない) |
| CS Equivalence/M1/Tier3/Secondary corroboration | **置換しない**(近似/corroboration層。発音一致の層より後段) |
| 値ガード+否定差(最終ANDゲート) | 本層の同値は『値・否定の読みが同一』を意味するため、承認済みbasisとしてゲートを再否定しない設計。**発音が異なる数・否定の差は本層が非同値のため従来どおり保護**。KPは2026-10-22の保護解除どおり(監査のみ) |
| `want to`<->`wanna`等の口語縮約(2026-09-07ユーザー不採用) | 発音が異なる(CMU)ため非同値のまま(testで固定) |

### 2-3 ①②(OPEN-458)との整合・C1
- ①(KPの数値・否定保護解除)とは**独立**: 本層は`classify_asr_match`の合格範囲を表記差について広げるだけで、票の集計規則・保護解除の実装(`er104`/`er078`のvote分岐)に触れない。flagも別(`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`)。配線順は(a)①②をOPEN-458委任_02で配線 -> (b)本層。①が先に入ってもNG3 coffeeは**Primaryが`'s`を落とす最終wav(a2)**は両票NGのまま(別原因)。本層を足すと`Pump 1's fist.`のS票が`classify`で合格し、KPQの真理値表上で救済される(`kp_corpus_eval_01.json`で7件)。
- ②(CMU未登録語をKPに選ばない)とは**補完関係**: 本層はCMU未登録語を『判定不能=非同値』にするfail-closed。②でKPがCMU登録語に限られる分、本層の判定可能域が広がる(本文はOOVが残るため、OOV語を含むspanは従来どおり不合格のまま)。
- **C1(Azure lexical形の取得)は本方式に包含されない**: C1は入力側(Azureが出す形)を変える案、本層は出力表記を発音で吸収する案。ユーザー決定③『Azure整形前テキスト併用』はREJECTED(UDR #155)のため、C1は採らない前提で、本層が`1's`型を吸収する。

## 3. 判定アルゴリズム(`er109_asr_orthographic_equivalence_01.py`)

1. **unit分割**: 通貨`$5.50`・時刻`5:30 pm`・序数`3rd`・分数`1/2`・数(桁区切り`1,200`/小数/%/'s/負数)・ドット付き頭字語`U.S.`・語(ハイフン/アポストロフィ含む)・記号(`& + = @ # ° %`)。
2. **読みの候補**: 数=基数(米式/英式and有無)・年(4桁1100-2099は`twenty twenty four`も)・序数・小数(`point`)・%(`percent`)・通貨(単数/複数、セント)・時刻(`o'clock`/`oh`)・分数(`one half`/`three quarters`)・年代(`nineties`)・'s(規則的な直前音素による-s/-z/-iz)。記号・略語(`Mr. Dr. St. vs. OK etc.`ほか)は閉じた表。語=CMU全variant(ハイフン語は全体と分割の和集合)、未登録語は`'s`のみ規則補完で他は判定不能。**全てCMU音素列(ストレス無視)に落として比較**。
3. **整列と判定**: unit key(数は値、%/通貨は印付き、語は英数小文字)で`difflib`整列。差span:
   - 語のみ・同数 -> 位置ごとのCMU同音(variant交差)。
   - 語のみ・個数差 -> 綴り連結一致(承認済みdespaced)または`er094`承認条件。**oronym(`ice cream`/`I scream`)は承認条件の外=非同値**。
   - 数・記号・略語・頭字語・contraction展開を含む -> 音素列集合の交差(variant直積<=64、超過は代表発音に縮退、それでも超過は判定不能)。
4. **fail-closed**: 片側が空のspan(欠落・付加。否定語脱落もここ)、span >6 unit、CMU未登録/解析不能(長い数字列、`1.000`型の桁区切り曖昧、範囲`10-20`、未対応記号)、音素が1つでも違う場合は非同値。
5. **出力**: `EquivalenceResult(equivalent, reason, spans[各spanのcanon/asr/rule/why], rules, canon_units/asr_units)`と`audit()`(§5)。
- 変種ポリシー(Opus Q1): 既定=**any-variant**(既存`homophone_arpabet_equivalent`/`er094`の非entity語と同じ。弱形`to`/`tew`・`are`/`our`・`so`/`sow`を受ける)。`representative_only=True`(代表発音のみ)は比較用: KP正例同値率98.1%・本文90.2%に低下、負例の誤同値は両方式とも0=**any-variantの方が正例を失わず、観測した負例では安全性差が出なかった**。ただしCMU辞書の変種quirk(`tv`->television、`us`->`Y UW EH S`、`dr`->doctor/drive、`st`->saint/street)を受け入れる側に倒れるため、Opusに確認する。

## 4. 検証結果(オフライン、API 0。再現コマンドはINVESTIGATION冒頭)

### 4-1 パターンカタログ(`pattern_probe_01.json`、149件)
正例114: 本文P(最終ゲート後) 82、KP-P 68、Whisper票 68、**提案層 107**(非同値7=`analyse`[CMU未登録]・`tyre`/`tire`[CMU音素表記差]・`ice cream`/`I scream`[承認条件の外]・`cannot`/`can not`[既存で対応済み]・`°C`・`Jan.`・`No. 1`)。負例35: 既存の誤PASS 1(N30=値同じ・読み違い、承認済み値等価)、**提案層の誤同値0**。分類: A=67・B=5・B/C境界=3・C=20・C-KP=14・D=35・E=5(`PATTERN_CATALOG_01.md`)。

### 4-2 機械生成ペア(`machine_pairs_eval_01.json`、seed固定)
母集団: KP distinct used_form 663句、保存本文segmentから抽出した文700。
| 母集団 | 正例n | 既存PASS | 提案層 | 合算 | 負例n | 既存の誤PASS | 提案層の誤同値 | **新規誤PASS** |
|---|---|---|---|---|---|---|---|---|
| KP | 1,128 | 1,023(90.7%) | **1,128(100%)** | 1,128 | 3,049 | 0 | 0 | **0** |
| 本文 | 2,099 | 1,793(85.4%) | **2,083(99.2%)** | 2,091(99.6%) | 3,749 | 2(規則的な単複`product`->`products`。承認済みbenign plural) | 0 | **0** |
正例の内訳(KP/本文): `one`->`1` 既存0/24・51/53 -> 提案24/24・53/53、CMU同音語置換 326/402・504/662 -> 402/402・662/662、記号(`&`/`vs.`/`Mr.`/`Dr.`/`OK`/`+`/`percent`) 本文41/165 -> 165/165、語->数字 KP 4/9 -> 9/9。提案層の取り零し(本文16件)は生成器由来(`$eighty five`、`2.6%`->`26%`の句読点除去で数が別物になる等)と、CMU未登録語を含むハイフン語(`hot-desking`、`Wi-Fi`。既存の綴り連結規則で合格)。負例種別: 数の変更(数字/数詞)・否定語の脱落/付加・内容語の脱落・語の挿入・語のランダム置換・音素1つ違い(各語の全variantと不一致を確認済みの最小対)。代表発音版(`machine_pairs_eval_representative_01.json`)は負例誤同値0・正例KP 98.1%/本文90.2%。

### 4-3 保存KPコーパス(`kp_corpus_eval_01.json`、P/S/Whisper転写203件)
新規PASS 7件=すべて`ng3_case`(`Pump 1's fist.`)。**問題音声21件由来(`take_part_problem_13`+`er091 problem 8`)の転写45件で新規PASS 0**(同値と判定された3件は既存でも合格しているASR非検出例)。

### 4-4 保存ASR記録(`stored_census_01.json`、4,877 attempt行)
不合格914のうち提案層が同値90(現行でも不合格=偽NG候補24、distinct pair 13・21 segment、STOPPED/HR 3)。Azure転写の表記差のみ不合格6。救済行167で提案層の追加余地0(INVESTIGATION §5)。

### 4-5 層間不整合(B)の露出(`gate_exposure_01.json`)
本文の機械生成正例のうち分類が合格した1,780件に対し、非KPの最終ゲートが保護差として再否定した件数 **5件**(複合序数`sixty eighth`/`68th`、`60 percent`/`60 %`、生成器由来の`13 1000000`)=約0.3%。

## 5. 監査設計(判定結果・適用ルール・原転写の記録)

加算的記録(既存キーは不変): attempt json / `cascade_steps[*]` / unified judge `audit_record` に `orthographic_equivalence_info` = `EquivalenceResult.audit()` = `{version, equivalent, reason, rules[], contraction_expanded, spans[{canon, asr, equivalent, rule, why}]}`。原転写(`asr_text`/Azure `text`/Whisper `text`)は従来どおり各stepが保持(本層は転写を上書きしない)。classification=`ORTHOGRAPHIC_EQUIVALENT_MATCH`、should_pass=True、**警告(PASS_WITH_WARNING)の要否**はOpus Q6。現行`HOMOPHONE_EQUIVALENT`/`NUMERIC_EQUIVALENCE_MATCH`は警告なし。事後試聴リストへ入れる対象は、CMU変種に依存するrule(`cmu_homophone`/`multiword_homophone_er094`)に限る案を推奨(数・記号・略語・綴り連結は決定的な規則)。

## 6. 適用範囲(案。Family別/経路別)
| 範囲 | 扱い |
|---|---|
| X/Z 本文・KP・解説の英語ASR(OpenAI/Azure/Whisper) | `classify_asr_match`経由のため自動で同一原則。KPのWhisper票も同じ |
| retry/fallback/regeneration/resume | 各attemptの判定が`classify_asr_match`経由。本層は判定の合格範囲を広げるのみで、上限回数・Gate・HR Lockの機構は不変 |
| Store再利用・X引継ぎ(`rejudge_with_current_judge`/`kp_vote_reuse_ok`) | 保存転写を現行judgeで再判定するため、本層をONにすると過去に偽NGで止まった資産も再判定で救済される(API 0)。ただし再利用ガード(`er078_reuse_value_guard_01`)の値ガード分岐はbasis除外が必要 |
| A/B/C共有部 | 互換性のみ確認。『不合格->合格』方向のみ変わり『合格->不合格』は無い。A/B/Cに適用するか(同じ改善を受けるか)/挙動差分0を維持するか(呼出点opt-inが必要)は**Fable/ユーザー判断事項** |
| 日本語ASR | 対象外(`lang="en"`のみ) |

## 7. リスクと未解決
- **CMU辞書の変種quirk**: `tv`->television、`us`->`Y UW EH S`(国名US/代名詞usの大小無視)、`dr`/`st`。any-variantは受ける。代表発音限定は正例を失う。-> Opus Q1。
- **CMUの限界(残存偽NG)**: 未登録語(`analyse`、`covid`)・音素表記差(`tyre`/`tire`)は同値化しない=偽NGが残る。補完辞書は新規救済範囲(別判断)。
- **数詞と同音語**: `to`<->`2`、`for`<->`4`、`won`<->`1`、`know`<->`no`は発音同一のため同値(Track B[承認済み]と同方向)。`no`<->`know`は否定語の同音異表記で、非KPの否定保護との関係が品質判断(Opus Q2/ユーザー判断候補)。
- **閉じた略語表の曖昧語**: `Dr.`(doctor/drive)、`St.`(Saint/Street)。どれか1候補が相手と一致すれば同値。誤同値は『drive Lee』型の転写が必要で低リスクだが、Opus Q5。
- Whisper票の標本が小さい(保存11件)。次委任で保存wavへローカルwhisper(API 0)を回せる。
- 保存分類は旧コード由来を含む。偽NG候補は現行コードで不合格のものに限定した。
- **A/B/C共有Validator**の挙動差分(NG->PASSのみ)を許容するかは判断事項。

## 8. Opus確認事項(Q形式。ユーザー原文§4の7観点に対応)
- **Q1(観点5:誤PASS)** any-variant(既定)とrepresentative-only(厳格)のどちらを標準にするか。観測: 負例の誤同値は両方0、正例は代表発音で本文9.0pt・KP1.9pt低下(弱形to/tew等)。CMU quirk(`tv`/`us`/`dr`/`st`)の扱い(受け入れる/stoplist/代表発音限定の語リスト)。
- **Q2(観点5)** 数詞<->同音語(`to`/`2`、`for`/`4`、`won`/`1`)および否定語の同音異表記(`no`/`know`)を同値にしてよいか。同値にする場合、非KPの最終ANDゲートで『本層同値=値・否定の読みが同一』としてbasis除外してよいか、それとも否定語を含む同音は除外(NG維持)とするか。
- **Q3(観点3:既存機構との整合)** 配線位置`classify_asr_match`末尾+`APPROVED_EQUIVALENCE_BASES`追加で、Tier1(5 role)・数字ゲート例外・contraction wrapper・CS Equivalence/M1/Tier3の順序・責務が壊れないか。本層をTier1の前(早期)に置くべき場合があるか。
- **Q4(観点3)** 語境界の救済を承認済みの条件(同数=位置ごとのCMU同音、個数差=綴り連結一致orer094)に限り、oronym(`ice cream`/`I scream`)や単一文字tokenを含むspanを除外したのは適切か。数・記号・略語spanで読み候補の直積が語境界をまたぐ副作用は無いか。
- **Q5(観点1:漏れ)** 閉じた略語・記号表(`Mr Mrs Ms Dr St Jr Sr vs OK etc Inc Co Ltd`ほか)の曖昧語と、年代`90s`、時刻、通貨セント、年読み、`'s`付き数の読み候補に重大な漏れ/過剰がないか。カタログ外の重要パターン(範囲、日付、単位記号、`No. 1`、月名略語)の扱い方針。
- **Q6(観点4:偽NG削減/監査)** 合格ラベル`ORTHOGRAPHIC_EQUIVALENT_MATCH`の警告要否(rule別: 決定的規則=警告なし/CMU変種依存=PASS_WITH_WARNING+事後試聴リスト)。監査フィールド(§5)の過不足。
- **Q7(観点6:経路網羅)** retry/fallback/regeneration/resume/Store再利用/X引継ぎ/Z(`er063`)/Whisper票で`classify_asr_match`を迂回する分岐が他にないか(Grep結果: 呼出81ファイル中、再利用系は`rejudge_with_current_judge`経由)。A/B/C共有部への波及を『適用する/挙動差分0を維持する』のどちらで推奨するか。
- **Q8(観点7:費用)** 追加API 0/1.2ms/判定の前提で、量産単価・Secondary(Azure)呼出・regenerateが増える経路が無いことの確認。Azure Secondary呼出が減る方向の効果見積(保存でAzure転写の表記差のみ不合格は6/225=2.7%)。

## 9. ユーザー判断候補(現時点では判断を求めない。VALIDATED後の採用判断の材料)
(27-3分類: 原則『同一発音=同等』=A既判断[原文§2・§6]。具体方式の採用=D新規、Trial/Opus/VALIDATED後)
1. 新規救済範囲(分類C/C-KP)の採用: (a)KP・Whisper票への数の表記差の適用(Tier1はKey Phrase非適用が承認済み仕様=適用範囲の拡大)、(b)`one's`<->`1's`型(数+'s)、(c)記号・略語(`& + ° vs. Mr. Dr. St. OK etc.`)、(d)stopword同音(`they're`/`their`、`by`/`buy`)、(e)年代・時刻・セント・年読み、(f)数詞<->同音語・否定語同音(`no`/`know`)。
2. 既存安全Gate(非KPの最終ANDゲート)への影響: 本層同値をbasis除外にする設計(Q2)。
3. A/B/C共有ValidatorへのNG->PASS方向の波及を許容するか、挙動差分0(opt-in)にするか。
4. KP英語の警告/事後試聴リストの方針(Q6)。
- 既存承認仕様の不具合(B: N11複合序数ゲート、B-2到達不能[1語/短文のratioゲート]、B-3 `60 %`)は判断事項ではなく自律修正対象(次委任)。ただし修正方法として提案層の配線(ratio前に置く)を使う場合は新規救済範囲(C)を伴うため、B単独の最小修正(値ガードatomの複合序数対応、ratioゲートの1語特例)とどちらにするかをFableが決める。

## 10. 次委任の所要見込み(依存関係・クリティカルパス・並列)
1. **Opusレビュー**(Q1-Q8、本DESIGN+prototype+検証json): 約0.5日(Fable)。レビュー後に設計修正(Sonnet 1-2h)。
2. **Bの最小修正**(並列可、Production編集): 値ガードatomの複合序数、ratioゲートの1語特例、`60 %` -- 各層テスト+Regression。ただし`er078`/`er104`/`er006`はOPEN-458委任_02が編集中のため**ファイル競合あり=委任_02完了後**。所要Sonnet約半日。
3. **配線(`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`既定OFF、11-7限定例外の5条件を満たす場合のみ)+DefaultOffIsolation test+全Regression**: Sonnet約半日。11-7例外を使わない場合(Offline Trial -> VALIDATED -> ユーザー採用 -> 実装)は採用判断待ち。
4. **VALIDATED用の追加検証**: 保存wavへのローカルwhisper(API 0)、Z/Xの新規2記事の再判定(API 0)、A/B/C保存データでのNG->PASS件数。並列可。約0.5日。
- クリティカルパス: Opus -> (OPEN-458委任_02完了) -> B修正+配線 -> VALIDATED報告 -> ユーザー採用判断。並列: カタログ拡充・Whisper保存wav検証・A/B/C影響集計。
