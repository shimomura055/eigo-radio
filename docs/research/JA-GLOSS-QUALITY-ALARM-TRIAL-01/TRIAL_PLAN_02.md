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
