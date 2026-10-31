# JA-GLOSS-QUALITY-ALARM-TRIAL-01 本格Trial結果 (RESULT_02)

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / OPEN-636 / 委任_02B(2026-10-31)。モデル=**gpt-6-luna(Luna 6.0)限定**(応答modelも全399 callで一致確認)。事前登録=`TRIAL_PLAN_02.md`(§9=実行前追記)、凍結ラベル sha256 `e98e830d…`(変更なし)。Production変更0・配線なし・flagなし。
**結論(Fable判定用の事実)**: 事前登録の主合否指標 **P-a' Precision = 36.4% / 30.8%(2 rep、平均33.6%、最小30.8%)**で、ユーザー目標80〜90%に**届かない**。重大誤訳ガードA(held-out)は 7/8=87.5% で通過、運用Recall=6/12=50%。事前登録どおり **Status候補=USER_DECISION_REQUIRED**(VALIDATEDにしない)。費用合計 ¥50.76 / Cap ¥60。

## 1. 推奨方式と仕組み(Fable判定用。私の推奨は候補)
- **主構成(凍結時に1つ指名)= R6「分析→判定型」一括検査、effort=medium、警告化規則 R_default、参考入力(ref)なし**。凍結構成=`trial/frozen_config.json`(developer文+schemaのsha256、M-8照合PASS、凍結後に変更なし)。参考のみ M3/medium/R_loose(devのみ・held-out未実施)。
- 仕組み(1記事セット=2 call: Standard・Advancedのlevel単位で1 callずつ): 入力=記事全文(英語)+level+そのlevelの候補12件(表現/現訳/該当英文/前後2文)。Luna(medium)が項目ごとに先に **分析欄**(`context_sense_en`=この箇所での意味、`figurative`=比喩か、`established_term`=定訳があるか)を書き、その後に `warn/severity(none|minor|major)/confidence(low|mid|high)/category/reason_ja(≤60字)/suggestion` を返す(strict JSON schema)。**コード側の規則 R_default**: `severity=major` なら警告、または `severity=minor かつ confidence=high かつ category∈{meaning_mismatch,too_generic,lost_nuance,established_term_replaced}` なら警告(unnaturalのminorは警告しない)。警告は1種類(「訳語の確認を推奨」)、`reason_ja`と(現訳と異なる場合のみ)`suggestion`を表示。Production Promptは不変、訳の自動修正なし、承認操作を妨げない。検査失敗(API error・JSON破損・id抜け)は「警告なし」に数えず未検査として別掲。
- **方式選択の経緯(dev=69項目、effort=medium、事前登録の規則選択・順位規則どおり)**: 各方式の規則は『ガードA(devの重大誤訳10件中9件以上)を満たす規則のうち、P-dev Precision最大』。

| 方式 | 選ばれた規則 | P-dev(実データdev 49中、problem 5) | ガードA(dev) | 費用(dev 23batch) | 備考 |
|---|---|---|---|---|---|
| **R6 分析→判定** | R_default | **4/6 = 66.7%** | **9/10** | ¥4.02 | 順位1 |
| M3 意味・自然さ分離 | R_loose | 5/8 = 62.5% | 9/10 | ¥3.34 | 順位2 |
| M2 一括(基準) | R_loose | 5/10 = 50.0% | 9/10 | ¥2.68 | |
| M1 1項目1call(評価項目のみ) | R_loose | 5/11 = 45.5% | 9/10 | ¥2.55 | 基準線 |
| M5 段2強制比較(M2+) | M2と同一 | M2と同一 | 9/10 | +¥0.70 | **段2が38警告すべてを『提案訳が優位』と判定=取消0件**。方式として機能せず |
| M6 盲検再生成→比較 | **該当なし** | 最良でも 3/9 | 最大8/10(<9) | ¥4.25 | ガードA未達=順位対象外 |
| M7 生成時メタ併用 | **未実施** | - | - | - | ablation専用・主構成候補外。費用上の縮退(§9-5) |
- **effort比較(R1b)**: R6 low=ガードA最大7/10(P-dev 37.5%)・R6 high=最大9/10(R_looseのみ、P 55.6%、R_defaultは8/10・60.0%)・R6 medium=9/10・66.7%。M3 low=最大8/10。→『上位(high)より全指標が5pt以上悪化しない最も低いeffort』=**medium**。注意: dev単一run・problem 5件でありノイズが大きい(effortの確定的優劣は主張しない)。**未実施(費用起因の縮退、事前登録済み)**: M2のeffort比較、M3のhigh。
- **R2(Prompt改善1周)**: R6v2(凍結rubricの一般基準を記述、特定語なし、M-8 PASS)はガードAが最大8/10で**不採用**(事前登録: ≥9/10が条件)。**ref入力(同記事の他levelの同表現訳)**: v2上で測定=FP・ガードAとも改善せず(R_loose 3/5・8/10、`inconsistent`警告が2件出たのみ)、v1は未測定のため**無効**(事前登録の保守側既定)。→R-9(a)の類型6入力は『実装したが凍結構成では無効』。類型6の検出率は凍結ラベルに実例0件で測定不能(合成確認も費用上未実施)。
- 反復回数: 事前登録の費用規則(見込み総額≤¥52を満たす最大k)により**final=2 rep**(3 repは約¥57で超過)。dev再現性rep2も費用上省略(finalの2 repで再現性を測定)。

## 2. Precision / Recall / 誤警告 / 見逃しの実測(凍結構成、final=held-out+運用プール261、各rep独立実行)
母集団(凍結ラベル): P-a'=運用プールからdev項目を除く216(problem 8/normal 208)、P-a=プール261(problem 12/normal 249)、P-c=held-out実データ44(problem 5/normal 39)。Wilson 95%区間を併記。

| 指標 | rep1 | rep2 | 平均 / 最小 |
|---|---|---|---|
| **P-a' Precision(主合否)** | 4/11=**36.4%**(15.2〜64.6) | 4/13=**30.8%**(12.7〜57.6) | **33.6% / 30.8%** |
| P-a' 誤警告(FP)/正常208 | 7(FPR 3.4%) | 9(FPR 4.3%) | 目標80%に必要=約1.6件以下 |
| P-a Precision(副) | 6/13=46.2%(23.2〜70.9) | 6/17=35.3%(17.3〜58.7) | 40.8% / 35.3% |
| P-c Precision(副、held-out実データ) | 3/6=50.0%(18.8〜81.2) | 2/3=66.7%(20.8〜93.9) | 58.4% / 50.0% |
| R-4 事前統合値 Pooled | 4/11=36.4% | 4/13=30.8% | P-c'(9件)から追加の警告0件 |
| 運用Recall(プールのproblem 12件) | 6/12=50.0%(25.4〜74.6) | 6/12=50.0% | 50.0% / 50.0% |
| P-a' Recall(problem 8件) | 4/8=50% | 4/8=50% | |
| **ガードA(held-out major 8件)** | **7/8=87.5%**(52.9〜97.8) 通過 | 7/8=87.5% 通過 | 点推定≥85%。分母8のため1件の見逃しで85%を割る |
| ガードB(T1+T3' held-out 全件12) | 7/12=58.3% | 7/12=58.3% | 併記 |
| T3(易しい合成、別掲、10件) | 10/10 | 10/10 | ガード分母に入れない |
| 未検査(API error等) | 0 | 0 | 全399 callでretry 0・失敗0 |
| 確認負担(警告/level、候補12件あたり) | 平均0.48件(最大4) | 平均0.63件(最大3) | 約4〜5% |

- **TP厳格/寛容**: 警告されたproblemはすべて凍結理由と同じ観点(定訳/所有の読み違い/裁判の比喩)で、**厳格TP=寛容TP**(rep1: equivalent width『光の線の特徴を表す幅』・insulation・radius・hold one's son back[P-a']、verdict×2[dev、P-aのみ]。rep2: equivalent width・radius・hold one's son back・scrape one's chair across[P-a']、side by side・verdict[dev])。凍結ラベルは変更なし。excludeは0件で『excludeをFP扱いにした下限』=報告値と一致。
- **類型別Recall**(プールproblem12+T3'8): 類型2=2/2(100%)、類型3=3/6・2/6、類型4=5/6・4/6、類型5=1/6・3/6(rep1・rep2)。類型5(日本語の不自然)はR_defaultがminor unnaturalを警告しない設計のため低い(設計どおり)。類型6=測定不能(上記)。
- **見逃し一覧(P-a' problem 8件のうち未警告)**: 両rep共通=equivalent width『スペクトル線の強さを示す等価幅』(minor)、culprit『原因』(minor)、blame one's scream on(minor)。rep1のみ=scrape one's chair across、rep2のみ=insulation。プール全体の追加見逃し=charge『非難』(dev・major、minor/midで警告化されず)、verdict(rep2のP-227、minor/mid)、side by side(rep1。minor/high/unnatural_jaで規則除外)。重大(major)の見逃しは凍結ラベルのP-a'に無し、held-out T3'では `shoving match→押し合いの試合`(類型3、minor/high/unnatural_jaで規則除外)1件。
- **誤警告一覧(P-a' FP)**: rep1(7)=sponsored『スポンサーの支援を受けた』[境界normal]・shepherd『羊の世話をする人』・registration『届け出』・slip away『そっと立ち去る』・go no farther『それ以上先へ進まない』・bar『通れないようにふさぐ』・struggle『苦労する』。rep2(9)=sponsored[境界]・obstacle『障害物』・line's absence from images・compensation[境界]・exception[境界]・forced to log in[境界]・as you deserve・go no farther・struggle(うち境界normal 4件)。**2 rep共通の誤警告=sponsored・go no farther・struggle**(3件)。
- 参考(事後の探索的分析。事前登録外・合否に不使用): (a) 境界normalへの警告を除いても P-a' は rep1 4/10=40.0%、rep2 4/9=44.4%。(b) 規則別(final): R_strict P-a' 4/9・2/9(44.4%・22.2%、ガードA 7/8)、R_loose 5/18・5/21(27.8%・23.8%、ガードA 8/8)。(c) 2 repの警告の共通部分=3/6=50%。いずれも80%に届かない。
- M-10(改善候補の妥当性、人手判定・基準=現訳と置き換えて意味が保たれ訳語の形になっているか): TPの suggestion はrep1の6件・rep2の6件とも妥当(半径・等価幅・断熱材・判決・並べて 等。hold one's son backは『息子の選択を妨げる/行く手を阻む』で所有の読み違いは解消)。誤警告に付いた有害な改善候補(文脈固有の長い説明文になる等)=rep1 2件(slip away『煙出しからするりと姿を消す』、struggle『吹雪の中を苦労して進む』)、rep2 5件(forced to log in『耳まで他人のおすすめ動画に強制ログインさせられる』、struggle、as you deserve、line's absence from images、sink for ever)。suggestionが現訳と同一で非表示にした件数=0。reason_ja 60字超=0。
- 注意(ラベル不変の確認): 誤警告のうち shepherd(→羊飼い)・registration(→婚姻届)・exception(→例外)・compensation(→補償金)は『定訳がある語の説明的な訳』への指摘で内容は理解できる指摘だが、凍結ラベルでは好み水準のnormal。事前登録(ラベル付け替え禁止)どおり**ラベルは変えず、FPとして集計**した。

## 3. 成功例・失敗例
- **成功**: radius『中心から外側までの長さ』→『半径』、equivalent width『光の線の特徴を表す幅』→『等価幅』(定義文化)、hold one's son back『人の息子の足を引っ張る』(『人の息子』が他人の息子に読める)、巧妙型T3' 7/8(例: adopted『採用された』→『婿養子』、wavelength『周波数』→『波長』、bar『出入りを禁じる』→『戸にかんぬきをかける』)、易しい型T3 10/10。
- **失敗(見逃し)**: culprit『原因』・equivalent width『スペクトル線の強さを示す等価幅』は両repで無警告(ユーザー指摘型のminor)。charge『非難』は『法廷での告発の響きが薄れる』とminor・midで指摘しながら規則で除外。**モデルは比喩の喪失を major でなく minor と評価しがち**(凍結rubricは「ユーザーが修正を指示した型は problem」)。
- **失敗(誤警告)**: 文学(Family Z)の文脈依存の言い換えや、定訳らしき語への指摘が集中(§4)。誤警告の数がrepごとに変わる(rep1 7件、rep2 9件、共通3件)=**出力の再現性が低い**。

## 4. Family / Level別の適用可能性(P-a、rep1/rep2。区間が極めて広い=参考)
| Family|level | 候補n | problem | TP | FP | FN |
|---|---|---|---|---|---|
| X Advanced | 78 | 5 | 3 / 2 | 1 / 2 | 2 / 3 |
| X Standard | 66 | 4 | 2 / 2 | 0 / 3 | 2 / 2 |
| Y Advanced | 22 | 1 | 1 / 1 | 1 / 1 | 0 |
| Y Standard | 19 | 0 | 0 | 0 | 0 |
| Z Advanced | 45 | 0 | 0 | **4 / 5** | 0 |
| Z Standard | 31 | 2 | 0 / 1 | 1 / 0 | 2 / 1 |
- problemの大半は Family X(科学・社会記事、定訳・比喩)に集中し、Zは problem が少ない一方で、**Z Advanced(文学)は誤警告のみ(0 TP)**。X/Yでは有用だが、文学では誤警告が主になる。Y Standardは件数が少なく結論不可。有病率が低い(P-a' 3.7%)ため、Precisionは誤警告数に強く依存する。

## 5. DEV試作URL(HR警告表示。API 0・表示時のLLM呼出なし)
- `https://shimomura055.github.io/eigo-radio/user_test/dev_ja_alarm_mock_01/index.html?dev=all`(警告のあるセット例: `...index.html?dev=all&set=moon_shrinking__b1b`。`&qa=off` で警告なし表示に切替)。公開直後は反映に数分かかる場合がある。
- 実装: Production `selection_form_v3` の複製。**`form_logic.js` はバイト同一**(sha256 `977cb3bd…` 一致)。`index.html` の差分=(a)CSS (b)常時バナー『DEV試作・ここから選定結果を送らない』 (c)`qaHtml` 関数と描画呼出1か所 (d)localStorageキー接頭辞(Productionのdev状態と混在させない)。警告=規則通過項目のみ1種類、reason≤60字、改善候補は有用時のみ(現訳と同一なら非表示)、level単位の未検査は既存 `data_warnings` 欄に『訳語チェック未実施(N件)』(実データは未検査0件。注入テストで表示を確認)。データ=Productionの27候補ファイル(261候補)に、final rep1の保存済み出力から `quality_alarm` を決定論的に付与(警告13件=1 level平均0.48件)。
- 検証(`trial/mock_verify_result.json`): (1)form_logic.js sha256一致 (2)**全27 level**で、警告ブロック除去後の候補行DOMがProductionと同一・警告数=期待値(不一致0)・`?qa=off`でも一致 (3)同じ選択操作でstats/miniStats/選定結果も一致。コピー文は『照合コード』行(データファイルのsha6が異なる)以外すべて一致 (4)**DEVのコピー文を Production の `restore()` に通すと『選定時のデータ版(d6=…)が見つかりません』で fail-closed 拒否**、Production生成文(対照)は受理(`trial/mock_restore_check.json`)=本番取り込みされない。警告は操作を妨げない(チェック・コピー・Doneの動作は同一)。(5)スクショ=`trial/mock_shots/dev_mock_{pc,sp}_{top,alarm}.png`(PC 1280px・スマホ390px、ページエラー0)。

## 6. 量産単価・処理時間
- **記事セット当たり追加費用 ≈ ¥0.36**(自然batch平均 ¥0.18/level × 2 level。rep1 ¥0.179、rep2 ¥0.186。目標70円の約0.5%)。1 callのみ(level単位)、追加の再試行なし。モデル=gpt-6-luna(medium)。
- 処理時間: 1 level callの平均17.5秒(最大33秒)。2 levelは並列可能で約20〜35秒/セット。HR待ち前の非同期処理にできクリティカルパスに載らない。
- **Trial費用合計 ¥50.757 / Cap ¥60**(ledger=`trial/ledger_02b.json`、399 call): dev R1 ¥17.53(M1 2.55・M2 2.68・M3 3.34・R6 4.02・M6 4.25・M5段2 0.70)、R1b ¥10.18、R2 ¥8.34、final ¥14.71(7.29+7.42)。止め線¥48は final 実行中に超過(事前登録§9-6で見込み¥50と記録済み、¥55には未到達)。無断の引上げなし。

## 7. 既存仕様・Production経路の変更なしの証明
- `git diff --stat`(本委任のcommit群): 変更は `docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/`、`user_test/dev_ja_alarm_mock_01/`(新規)、`OPEN_ITEMS.md`(OPEN-636行のみ)のみ。`user_test/selection_form_v3/`・`er003_*`・`er119_*`・`er128_*`・訳生成Prompt・`CURRENT_SPEC.md`・`DECISION_LOG.md` は**無変更**(実測は RESULT_PACKET_JAQ_02B.md の(1)/(2)行)。
- flag追加なし・起動script/.env変更なし。Trial専用経路(`tools/jaq02b_*.py`)のみ。到達可能Status=VALIDATED/REJECTED/USER_DECISION_REQUIRED。Production配線はユーザー正式承認後。

## 8. Status候補とユーザー採用判断に必要な事項
- **Status候補=USER_DECISION_REQUIRED**(事前登録: P-a' Precision 80〜90%目標は基準を動かさず、未達はユーザー提示)。VALIDATEDの要件を満たさず、REJECTEDの自動決定もしない。
- ユーザー判断に必要な事実:
  1. 目標80〜90%に対し、実測 P-a' 33.6%(最小30.8%、区間下限約13〜15%)。有病率3.7%・正常208件のもとで80%に必要な誤警告は約1.6件以下だが、実測は7〜9件(2 repで再現性も低い)。ユーザー基準は変えていない。
  2. 一方、重大誤訳ガードA=7/8(87.5%、通過)、易しい合成誤訳は10/10。ただしユーザーが実際に修正を指示した型(比喩・原因)のminor評価は見逃しやすく、運用Recallは50%(12件中6件)。
  3. 確認負担は小さい(警告平均0.5〜0.6件/level、記事セット追加費用¥0.36、HR待ち前に非同期)。ただし警告の約3分の2は誤警告(好み水準の指摘を含む)で、特に文学(Z Advanced)は誤警告のみ。
  4. 方式面の見込み: 段2強制比較(M5)と盲検再生成(M6)は効果なし、Prompt改善(R2)もガードAを下げた。本モデル限定の範囲で追加Trialの改善見込みは低い(同方式の繰り返しではなく、検査単位・追加情報の見直しが必要)と評価する。
  5. 選択肢(採用判断はユーザー): (A)基準維持で不採用(REJECTED) (B)基準(Precision目標)・用途(警告ではなく『確認の目安』)を見直したうえで運用試行 (C)別仕様(方式変更)の設計を新Trialとして起案。基準の変更・採否はAIが決めない。
- 本Trialで実施しなかったこと(費用起因の事前登録済み縮退): M7、M2/M3の一部effort、dev rep2、final 3rep、類型6の合成確認。いずれも『実施した』とは書かない。

## 付録: 再現と証跡
- 台帳=`trial/ledger_02b.json`、各runの全出力=`trial/out/<run>/`、凍結=`trial/frozen_config.json`、M-8照合=`trial/m8_check_*.json`、final集計=`trial/final_result.json`、DEV検証=`trial/mock_*`。ツール=`tools/jaq02b_{data,prompts,run,score,final,mock_build,mock_verify}.py`。
