# JA-GLOSS-QUALITY-ALARM-TRIAL-01 Trial計画 v2(事前登録) (TRIAL_PLAN_02)

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / OPEN-636 / 委任_02A(2026-10-31)で作成。**TRIAL_PLAN_01.md を置換する事前登録**(Opus条件Aレビュー `OPUS_REVIEW_01.md` とFable決定を反映)。本格Trialは委任_02B。モデル=gpt-6-luna固定。Production変更0・配線なし(Trial専用経路)。
**実行前に確定し、結果を見た後で判定基準・集計方法・ラベルを緩和・変更しない**(ユーザー原文§4)。基準を変える場合は変更理由と日時を本書末尾「変更履歴」に追記し、変更前の基準での結果も併記する。v01から変更のない節は「v01 §N のとおり」と参照する。

## 0. 凍結宣言(ラベル)
- 凍結ラベル=`labels_frozen_01.json`、**sha256=`e98e830d3da315507c3fc9832cdbae4f76c3e6a9d375762612761e8180833a85`**(LF改行のバイト列。確認=`git show <commit>:docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/labels_frozen_01.json | sha256sum`)。内容=346件のブラインド裁定(T2 71・T4 14・運用プール261)+T3'16件(`t3prime`)。裁定の手順・件数・κ=`ADJUDICATION_01.md`、基準=`ADJUDICATION_RUBRIC_01.md`。
- **以後の付け替え禁止**: Trial実行後の再ラベルを含む。検査器が警告した項目の再裁定でラベルを変えることをしない(v01 §5-2の『警告が出たT2・プール項目の事後裁定』は**廃止**。M-1)。割れ・疑義があっても本ファイルは書き換えず、本書末尾に追記する。
- T1/T3(既存の `eval_set/items.json`)のラベルは委任_01のまま(T1=ユーザー指摘/HR修正、T3=合成)。T3'=`items.json` の tier `T3P`(16件)と `t3prime` セクション。

## 1. 母集団と合否指標の一本化(M-11、事前登録)
### 1-1. 母集団(凍結ラベルによる)
| 集合 | 内容 | problem | normal |
|---|---|---|---|
| **P-a'**(運用プール、devで使った評価項目を除く) | プール261のうち `in_dev_set=false` | 8 | 208 |
| P-a(運用プール全体) | 261 | 12 | 249 |
| P-c(held-out、実データのみ) | T1 held-out 4 + T2/T4 held-out | 5(T1 4+T4 insulation 1) | 39(T2 33+T4 6) |
| P-dev(dev、実データのみ) | T1 dev 4 + T2/T4 dev | 5(T1 4+T2 side by side 1) | 44(T2 37+T4 7) |
| T3'(巧妙型・合成) | dev8/held-out8 | 16 | - |
| T3(易しい型・合成) | dev12/held-out10 | 22 | - |
- exclude は0件(裁定時に使用0)。そのため『excludeをFP扱いにした下限』と『除外した値』は一致する(両方報告は維持)。
- **P-a'とP-c/P-a の重複**: P-a'のproblem 8件のうち5件(culprit、radius、equivalent width×2、insulation)はheld-outのT1/T4項目と同一内容。独立なのは3件(scrape one's chair across、hold one's son back、blame one's scream on)。したがってP-a'とP-cは独立の2検証ではない(合否の根拠をP-a'に一本化する理由の一つ)。
### 1-2. 指標の役割(一本化)
- **主合否指標=P-a'のPrecision**(凍結した主構成、`TP/(TP+FP)`、Wilson 95%区間を併記)。判定: 点推定≥80%で『目標到達』。区間下限が80%未満なら『点推定は達したが区間下限は未達』と併記し、**合格を断定しない**。ユーザー目標は80〜90%(保証でない)。
- **副指標(報告のみ。合否に使わない)**: P-a(全体)、P-c(held-out)、R-4の事前統合値、P-dev。それぞれWilson 95%区間を併記。
- **R-4の事前統合値(統合規則を固定)**: `Pooled = (TP_P-a' + TP_P-c') / (警告_P-a' + 警告_P-c')`。P-c'=P-cから、P-a'に同一内容(表現・現訳・該当英文が一致)で含まれる項目を除いたもの(二重計上を避ける)。同じ凍結構成(同一run)の結果のみを使い、**良い方を後から選ばない**(主=P-a'は不変)。
- **TP定義(M-5)**: 厳格TP=項目が凍結ラベルでproblemかつ警告の `reason_ja` が凍結ラベルの問題(凍結 `reason_ja`/`category` と同じ点)を指す。寛容TP=項目がproblem(警告の理由は問わない)。**両方を併記**。理由の一致判定は、凍結 `reason_ja` と警告理由を並べ、手順=『同じ観点(意味のずれ/比喩/定訳/不自然)を指すか』で行い、判定者は凍結ラベルを変更しない。
- **FP**: 凍結ラベルがnormalの項目への警告(境界normal19件〈`borderline_normal=true`〉への警告も数えるが、別掲する=『境界normalへの警告』)。
- Family別・level別は参考表示(区間が極めて広い。Y/Zのproblemは極少)。
### 1-3. 重大誤訳ガード(M-12、副Gate、事前登録)
- ガードA(必須の副Gate)=**T1+T3'(巧妙型)のうち severity=major の検出率≥85%**(rubric適用後のT1 severityを使う。ADJUDICATION_01 §5-3)。分母: dev = T1 dev major 4(verdict×2、charge、things left out)+ T3' dev major 6 = 10。held-out = T1 held-out major 2(radius、equivalent width〈光の線の特徴を表す幅〉)+ T3' held-out major 6 = 8(85%を満たすには7/8以上)。agent案severity(held-out T1 major 0)での値も併記する。
- ガードB(併記)= T1+T3'の**全件**(minor含む)の検出率。T3(易しい型)は**別掲**(ガードの分母に入れない)。severity=minorの見逃しはガードに入れず、一覧として報告する。
- **未達の扱い(一本化)**: ガードA未達(dev・held-outのいずれか)=その構成は **VALIDATEDにせず `USER_DECISION_REQUIRED`**(採否はユーザー。不採用の自動決定をしない)。数値と見逃し一覧(全件個別)を付けて提示する。held-outの分母が8しかないため、1件の見逃しで85%を割る(区間付きで報告し、点推定だけで断定しない)。
### 1-4. 有病率の根拠(M-4)
- 運用プール261件のブラインド裁定(`ADJUDICATION_01.md` §4): problem率 全体4.6%(Wilson 2.6〜7.9%)、dev項目を除く3.7%(1.9〜7.1%)。TRIAL_PLAN_01の仮置き3〜10%は根拠なしだったが、結果は範囲内。ただしproblem 12件中7件はユーザー既知の型。
- **Precisionの算数**(`P=πr/(πr+(1-π)f)`、π=有病率、r=Recall、f=FPR): P-a'(π=8/216=3.7%、正常208件)で r=0.8 のとき P≥80% に必要な f≤0.77%(**正常208件中の誤警告は約1.6件以下**)。π=4.6%(全体)なら f≤0.96%。Recall 0.9なら f≤0.87%。**P-a'で80%を点推定で達するには、誤警告が正常208件中ほぼ1〜2件に収まる必要がある**。この厳しさはTrial前の事実として記録する(結果を見てから基準を緩めない)。確認負担(警告件数/12候補)はPrecisionと別に必ず報告する。
- **判断候補**: 上の算数が示すとおり、P-a'に対するPrecision 80〜90%はLunaの誤警告率に非常に厳しい条件である。方式比較・規則選択はP-dev等で行うが、合否の主指標をP-a'に固定する以上、未達の場合の扱い(基準は動かさない=USER_DECISION_REQUIREDで提示)をユーザーに事前周知するかはFable判断。

## 2. 固定条件(v01 §1のとおり、以下を追加・変更)
- モデル: gpt-6-luna(応答modelも照合)。reasoning_effort=下の規則で選ぶ。他モデル不使用。
- 検査単位: 記事×level。入力は 表現/現訳/該当英文/前後2文/記事全文/level(DESIGN_OPTIONS_01 §0)。
- **R-9(類型6、記事内不整合)**: (a)を採用。同じ記事の他levelで同じ表現に付いた訳を**参考入力**に加える(委任_02Bで実装)。解説ベースの不整合は、HR段階では解説が未生成のため**対象外**と明記。類型6の検出率は、実装後に別途(Trialでの記事内不整合の実例が凍結ラベルに0件のため、合成での確認のみ)報告し、合否に使わない。
- **R-3(評価バッチの構成)**: 各バッチを、**同じ記事・levelの運用プール候補で12件まで埋める**(本番入力=12候補/level)。埋めた候補は凍結ラベルで採点する(M-4)。T3'・T3の挿入時は、その元のT2(`must_not_share_batch_with`/`synthetic_of`)を同じバッチに入れない。同じ表現を1バッチに2回入れない(v01のview A/B方針を継承)。1項目はrunごとに1回だけ出現させる(二重計上を避ける)。
- dev=Prompt調整に使ってよい。held-out=凍結後に**1回だけ**(3回再現含む)評価。dev項目=`labels_frozen_01.json` の `in_dev_set=true`+items.jsonのsplit=dev。
- **M-8(Promptへの特定語混入の機械照合)**: Prompt変更のたび、`eval_set/items.json`(131件)とプール261件の `expression`・`current_ja` がPromptに**含まれない**ことを機械照合し、PASS時のみ `frozen_config.json` に記録する。現行probe Prompt(`tools/probe_01.py:36-43`)は適合(委任_01確認)。Promptの例示語は禁止。

## 3. 規則・effort・主構成の選択規則(M-6/M-7、事前登録)
1. **警告化規則**(R_strict/R_default/R_loose、DESIGN_OPTIONS_01 §3)の選択=『**devのガードA(≥85%)を満たす規則のうち、P-devのPrecision(P-c相当のdev実データ)が最大**。同点ならRecallが高い方』。ガードAを満たす規則がなければdevで打ち切り(`USER_DECISION_REQUIRED`の材料として報告)。
2. **reasoning_effort**: 『**上位effortより全指標が5pt以上悪化しない最も低いeffort**』を選ぶ。判別できなければmedium以上(Q>C)。R-8: R1bのeffort比較(low/medium/high)は、M2に加えて**R2で残った上位2方式**でも行う。
3. **主構成は凍結時に1つ指名**(M-7)。2つ目は参考(held-outの結果で主を入れ替えない)。主指標=**1回ごとの指標の平均と最小値**(3回再現の集計。多数決は禁止)。
4. 方式の追加: M5の段2は『確信がhighでない/minor』限定案と**全警告に掛ける案**の両方を比較する(R-5、約¥0.06/level)。段2で取り消された警告のうち凍結ラベルがproblemだった件数を記録。M6(独立検査)は同系統モデルのため限定的な独立性である旨を報告に明記し、代案として『分析→判定』型(M2/M3のschemaに `context_sense_en`/`figurative(bool)`/`established_term` を先に書かせてから判定させる変種、特定語に依存しない)を比較する(R-6)。M7(生成時メタ情報の利用)はablationのみで**主構成候補にしない**(R-7。プールに生成時メタ情報があるか未確認)。
5. **severityと類型**: rubricの定義(`ADJUDICATION_RUBRIC_01.md` §4/§7)で凍結。類型別Recall(1〜6)を必ず報告(R-9。R_defaultがminor〈類型5・6〉を警告しない設計なら類型5のRecallが設計上低い点も明記)。
6. R-2: things left out(`comment_translation`)はKP/KW訳と対象が違う。集計では分けて表示。R-1: T1は6表現(すべてX)。表現単位の件数でも報告。

## 4. 実行段(v01 §4のとおり、Trial効率のため独立な実行は並列)
R1(dev方式比較)→R1b(effort。上位2方式)→R2/R3(改善、最大2周)→再現性(dev)→凍結(`frozen_config.json`: 方式・Prompt全文sha256・effort・規則・主構成・M-8照合結果)→H(held-out、凍結構成3回)→P(運用プール261件を凍結構成で検査。**警告が出た項目の事後裁定は行わない**=ラベルは凍結済み)→UI試作(API 0)。
- **R-10(検査失敗の扱い)**: API error・JSON破損・resultsに抜けたidは『警告なし』に数えない。件数を別掲で報告する。id集合照合・再試行・失敗扱いをprobeに実装(02B)。UIには level単位の既存status行(`data_warnings`)に『訳語チェック未実施(N件)』を表示(項目単位の表示は足さない。警告ゼロ記事は表示なし)。
- **R-11**: 重大度は2段に分けない(規則を通過した警告を1種類で出す)。

## 5. HR警告表示試作(DEV専用、委任_02Bで実装)
- **M-9**: DEVページ `index.html` に『DEV試作・ここから選定結果を送らない』の**常時バナー**を表示する(`form_logic.js` は変えない)。差分検証に『DEVのコピー文を restore に通したときの挙動』を追加(未検証の恐れを検証する)。
- **M-10**: 『改善候補が妥当だった率(TPのうち)』と『誤警告に有害な改善候補が付いた件数』を測定項目に追加。suggestionが現訳と同じ場合は表示しない。
- UI案はHR_UI_MOCK_DESIGN_01.mdのとおり(署名・照合コード・確定内容に影響しない表示専用)。

## 6. 費用
- **委任_02A=¥0(API 0・Luna呼出なし)**。
- **委任_02B Cap=¥60、止め線¥48(80%到達で報告)**(Fable決定R-12)。見積の根拠: v01小計¥35.6に、M-2(T3'追加)・R-3(12件埋め)・R-5(段2全警告)・R-8(上位2方式のeffort)で概算+¥8〜15、予備を含めてCap ¥60。7-7の『承認済みScope内で案件見積300円以下』=AI自律範囲。追加が必要な兆候はCapの80%到達前に事前申請する(予算切れ後の事後報告をしない)。

## 7. Production分離・到達Status(v01 §7のとおり)
Trial専用経路(`docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/tools/`)のみ。Productionの `er003_*`・`er119_*`・`er128_*`・`user_test/selection_form_v3/` は変更しない。flagは追加しない。到達可能Status=VALIDATED / REJECTED / USER_DECISION_REQUIRED。Production配線はユーザー正式承認後。

## 8. 成果物(委任_02B)
trial/ledger.json、trial/out/*.json、`frozen_config.json`、RESULTS_01.md(P-a'主指標・副指標・厳格/寛容TP・ガードA/B・T3別掲・類型別Recall・検査失敗件数・境界normalへの警告・Family/level別・誤警告/見逃し一覧)、DEV UI URL、RESULT_PACKET。

## 変更履歴
| 日付 | 変更 | 理由 |
|---|---|---|
| 2026-10-31 | v01→v02: 合否指標の一本化(主=P-a')、ガード(major・T1+T3')と未達=USER_DECISION_REQUIRED、事後裁定の廃止(ラベル凍結)、規則・effort・主構成の選択規則、TP厳格/寛容、T3'の追加、M-9/M-10/R-3/R-5〜R-11、Cap¥60 | Opus条件Aレビュー(OPUS_REVIEW_01.md)とFable決定。Trial実行前の変更であり、変更前の基準での結果はない |

## 9. 委任_02B 実行前追記(事前登録・Trial実行前に確定。2026-10-31)
### 9-1. Fable決定(02Aの判断候補への回答)
1. P-a' Precision 80〜90%目標は**ユーザー基準のまま動かさない**。未達=`USER_DECISION_REQUIRED`(§1-2のとおり)。有病率3.7%下で必要FPR≤0.77%(正常208件中の誤警告約1.6件以下)であることは RESULT_02 に明記する。
2. T1 severity は **rubric適用後**(凍結pool裁定。radius/equivalent width『光の線の特徴を表す幅』=major、culprit/equivalent width『スペクトル線の強さを示す等価幅』=minor)を主、agent案(items.json)を併記。`items.json` 本体は不変。実装: `tools/jaq02b_data.py` が mapped T1 の severity を pool 凍結値に差し替え、`severity_agent` に原値を保持。
3. ガードA=major分母(held-out 7/8以上、dev 9/10以上)、ガードB=全件検出率併記。採用。
4. Fable抜き取り20件(seed=20261101)=20/20一致(ADJUDICATION_01.md §8)。κの限界(同一裁定者)は維持。
### 9-2. データ・バッチ構成(tools/jaq02b_data.py、決定論、seed=20261101)
- 評価単位: eval項目(131)+プール261。eval項目のうち(slug・level・表現・現訳)が一致するT1/T2/T4は**pool項目に対応づけ**(`pool_uid`)、最終runでは自然batchの結果を使う(二重出現なし)。対応しないreal項目と合成T3/T3'(元項目と同一batch禁止)は評価batch(E)に入れ、**同slug・levelのpool候補で最大12件まで埋める**(R-3)。埋め草(filler)の結果は採点しない(dev段では dev・held-out対応のpool項目を優先的に避ける)。
- dev: 23 batch(うち合成専用S 11)。final: 自然batch 27(プール261全件)+E 13。item idは不透明(c01…)、batch内順序はseed固定でshuffle(repごとに別seed)。
- 母集団はTRIAL_PLAN_02 §1のとおり。P-c=held-out real(T1/T2/T4)。ガードAの分母=T1 major(rubric後)+T3' major。
- 評価対象の信頼境界: `confidence` の列挙値は `low|mid|high`(`medium` はeval表現に実在するためM-8照合のため改名。意味は同じ)。M-8照合結果=`trial/m8_check_<sha12>.json`(expression/current_ja 521種、Prompt・schema全体との照合、PASS)。
### 9-3. 方式の順位付けと選択(結果を見る前に固定)
- R1(dev、effort=medium固定): M1(基準線、評価項目のみ1項目1call)/M2/M3/R6(分析→判定型)/M6(盲検再生成。段1:現訳を見せず推奨訳、段2:同等判定。現訳と推奨訳・別訳が文字一致なら段2省略)。M5=M2の出力に段2強制比較(A/B順は項目ごとにseed固定の乱択)を掛けた**同一段2呼出から** M5all(全警告=suggestionあり)/M5lim(確信がhighでない、またはminorのみ)の2案を後処理で作る(suggestion空の警告は段2に回さず維持)。段2で取り消された警告のうち凍結ラベルがproblemだった件数を記録。M7=ablationのみ。
- 各方式の規則は§3-1(ガードA dev≥85%=9/10以上を満たす規則のうちP-devのPrecision最大、同点はRecall)。ガードAを満たす規則がない方式は順位対象外(参考表示)。
- **方式の順位**: ガードA(dev)を満たす方式のみ対象 → P-dev Precision(lenient、問題項目=凍結problem)の降順 → 同点は dev全問題(real+T3'+T3)のRecall → なお同点は費用が低い方。上位2方式をR1bへ。主構成の第1候補は順位1位。
- R1b(effort): M2と上位2方式を low/high でも実行(medium値はR1)。『上位effort(high)より全指標が5pt以上悪化しない最も低いeffort』。費用が止め線に近づく場合の縮退(事前登録): highはM2と順位1位方式のみ。縮退したら理由と金額を記録。
- R-9(a)参考入力: 凍結候補構成にref入力(同記事の他levelの同表現の訳)を足した dev 1 run を比較。**devのFP数が増えず、ガードA検出数が減らない場合のみ凍結構成に含める**。それ以外は無効化し、類型6入力は『合成確認のみ』として報告(合否に使わない)。
- 再現性(dev): 凍結候補で別shuffle(rep2)を1回。ガードA・P-devは rep1/rep2 の平均と最小を併記。
- 凍結(`frozen_config.json`): 方式・Prompt sha256・effort・規則・ref有無・主構成1つ・M-8結果。held-out + プールは凍結構成で実施。反復回数は、凍結時点の費用実績から『見込み総額≤¥52』となる最大のk∈{3,2,1}(事前登録)。主指標=repごとのP-a'の平均と最小。
### 9-4. 採点・報告の補足(事前登録)
- 未検査(API error・JSON破損・id抜け)は『警告なし』に数えず別掲(R-10)。FP/Precisionの分母にも入れない。
- 厳格TP/寛容TPは、警告されたproblem項目について凍結理由と警告理由を並べ人手(本Worker)で判定し全件を記録。凍結ラベルは変更しない。
- 費用/記事セット = 自然batch 1本あたり平均費用×2(Std・Adv)。処理時間=batch平均所要。
- 未実施・縮退した項目(M7等)は、その理由と金額を RESULT_02 に明記する(『実施した』と書かない)。
### 9-5. R1(dev, medium)結果を受けた R1b/R2 の縮退・手順(2026-10-31、R1b実行前に記録。費用起因の縮退であり、R1の数値による基準の緩和ではない)
- R1結果(dev、規則はガードA(≥9/10)を満たすもののうちP-dev Precision最大): R6=R_default P-dev 4/6(66.7%)ガードA 9/10 / M3=R_loose 5/8(62.5%)9/10 / M2=R_loose 5/10(50.0%)9/10 / M5(all・lim同一、段2で取消0/38件)=M2と同一(+費用) / M1=R_loose 5/11(45.5%)9/10 / M6=ガードA満たす規則なし(最大8/10)。順位: R6 > M3 > M2 > M1。**上位2方式=R6、M3**。累計費用¥17.53。
- 費用上の縮退(事前登録): 累計+R1b+R2+再現性+ref+finalが¥55に収まるよう、R1bは **R6の low/high、M3の low のみ**(medium値はR1)。M2のeffort比較、M3のhighは費用起因で未実施(『実施した』と書かない。RESULT_02に明記)。
- 効果が測れない場合の扱い: M5は段2が全38警告を『提案訳が優位』と判定(取消0)したため方式として機能せず、以降の最適化対象にしない(Status上は比較実測済み)。
- R2(Prompt改善、最大2周中まず1周): 対象は上位方式のみ。**変更は一般基準の追記に限り、特定語・例を入れない**(severityの定義を凍結rubric §4の一般基準[意味が変わる・辞書第一義への一般化・比喩/像の喪失で意味が変わる・定訳の不適切な言い換え=major]に合わせる等)。変更のたびM-8機械照合をPASSさせsha256を記録。R2の結果は dev のみで評価し、held-out/プールの数値は見ない。
