# 事例別 Before/After 詳細(自動生成、er066_..._eval_01.py の出力 before_after_01.json から)

## A. 過去実転写コーパス(分類別、is_real=実run由来のみ)

| 分類 | 件数 | Before通過 | After通過 | 新規救済 | 取消(PASS→UNCERTAIN) |
|---|---|---|---|---|---|
| 真の誤読(別語・脱落・挿入) | 138 | 0 | 0 | 0 | 0 |
| (既存PASS: 現行Productionで通過) | 690 | 690 | 690 | 0 | 0 |
| その他(ASR断片・脱落) | 5 | 0 | 0 | 0 | 0 |
| 外来語・固有名詞(カタカナ長音・促音等) | 5 | 0 | 0 | 0 | 0 |
| 数値を含む差(他の誤読を併発または対象外) | 19 | 0 | 0 | 0 | 0 |
| 数値表記差(漢数字/算用数字・助数詞・単位) | 6 | 0 | 6 | 6 | 0 |
| 同音異表記・漢字/かな(Cascade域) | 6 | 0 | 0 | 0 | 0 |
| その他(ASR幻覚・プロンプト漏洩・混入) | 18 | 0 | 0 | 0 | 0 |
| 真の誤読(値/助数詞の違い) | 8 | 0 | 0 | 0 | 0 |
| 外来語・固有名詞(ラテン⇔カタカナ) | 8 | 0 | 0 | 0 | 0 |

## B. 新規救済された過去事例(全件)

| 由来 | 原稿(先頭) | ASR(先頭) | Trial判定 |
|---|---|---|---|
| 実run | まず、20％という計画が発表されたあと、支払い方法など何がまだ決まっていなかったのかに注目 | まず、20パーセントという計画が発表された後、支払い方法など何がまだ決まっていなかったのか | TRIAL_READING_MATCH |
| 実run | 英国政府が、10代の若者とSNSの使い方をめぐる新しい計画を発表しました。夜のSNS利用を | 英国政府が、十代の若者とSNSの使い方をめぐる新しい計画を発表しました。夜のSNS利用を見 | TRIAL_NOTATION_MATCH |
| 実run | 料金の話は、わずか1日で投資の話へと変わりました。では、原油市場はこれで落ち着いたのでしょ | 料金の話は、わずか一日で投資の話へと変わりました。では、原油市場はこれで落ち着いたのでしょ | TRIAL_NOTATION_MATCH |
| 実run | メロスは、恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式 | メロスは恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式に | TRIAL_NOTATION_MATCH |
| 実run | メロスは王に、公平な裁判もせず人を殺すのは不公平だと訴えます。妹の結婚式に出るため三日間の | メロスは王に、公平な裁判もせず人を殺すのは不公平だと訴えます。妹の結婚式に出るため3日間の | TRIAL_READING_MATCH |
| 実run | メロスは王に、公平な裁判もせず人を殺すのは不公平だと訴えます。妹の結婚式に出るため三日間の | メロスは王に、公平な裁判もせず人を殺すのは不公平だと訴えます。妹の結婚式に出るため3日間の | TRIAL_READING_MATCH |
| 合成fixture(er058) | 二人で行きました。 | 2人で行きました。 | TRIAL_NOTATION_MATCH |
| 合成fixture(er058) | 20％の人が来ました。 | 20パーセントの人が来ました。 | TRIAL_NOTATION_MATCH |
| 合成fixture(er058) | 三十人が来ました。 | 30人が来ました。 | TRIAL_NOTATION_MATCH |
| 合成fixture(er058) | 100円でした。 | 百円でした。 | TRIAL_NOTATION_MATCH |

## C. 正常例(合成37件): Before=現行Production / After=Trial

| 原稿 | ASR | 種別 | Before | After |
|---|---|---|---|---|
| 三日間 | 3日間 | 漢数字/算用数字+助数詞(日) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 三日間の猶予を求め | 3日間の猶予を求め | 漢数字/算用数字+助数詞(日) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 二人で行きました。 | 2人で行きました。 | 漢数字/算用数字+助数詞(人) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 三十人が来ました。 | 30人が来ました。 | 漢数字/算用数字(位取り) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 100円でした。 | 百円でした。 | 漢数字/算用数字+単位(円) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 一万円です | 1万円です | 漢数字/算用数字(万) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 一万円です | 10000円です | 漢数字/算用数字(万) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 千円です | 1,000円です | 漢数字/算用数字(桁区切り) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 20％の人が来ました。 | 20パーセントの人が来ました。 | 略記・単位(%) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 20％の人 | 二十パーセントの人 | 略記・単位(%) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 二泊三日の旅 | 2泊3日の旅 | 日付・期間 | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 三日坊主で終わった | 3日坊主で終わった | 助数詞(日)+慣用句 | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 三時十五分に着く | 3時15分に着く | 日付・時刻 | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 四月二日に会う | 4月2日に会う | 日付・時刻 | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 十月に始まる | 10月に始まる | 日付・時刻 | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 二十歳になった | 20歳になった | 助数詞(歳) | PASS | PRODUCTION_PASS |
| 三百人が集まった | 300人が集まった | 漢数字/算用数字+助数詞(人) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 五十回試した | 50回試した | 助数詞(回) | PASS | PRODUCTION_PASS |
| 三キロ歩く | 3キロ歩く | 略記・単位(キロ) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 二倍になる | 2倍になる | 助数詞(倍) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 一週間待つ | 1週間待つ | 助数詞(週) | PASS | PRODUCTION_PASS |
| 三階に行く | 3階に行く | 助数詞(階) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 三日間の旅 | みっかかんの旅 | 読み(日+間) | PASS | PRODUCTION_PASS |
| 二人で行く | ふたりで行く | 読み(人) | PASS | PRODUCTION_PASS |
| 四月に会う | しがつに会う | 読み(月) | PASS | PRODUCTION_PASS |
| 10分待つ | じゅっぷん待つ | 読み(分) | NG(TRUE_C) | TRIAL_READING_MATCH |
| 三人で行く | さんにんで行く | 読み(人) | PASS | PRODUCTION_PASS |
| 三時間かかる | さんじかんかかる | 読み(時間) | NG(TRUE_C) | TRIAL_READING_MATCH |
| 百円です | ひゃくえんです | 読み(円) | PASS | PRODUCTION_PASS |
| 3本ください | さんぼんください | 読み(本) | NG(TRUE_C) | TRIAL_READING_MATCH |
| 六日に着く | むいかに着く | 読み(日) | PASS | PRODUCTION_PASS |
| 20歳になった | はたちになった | 読み(歳) | NG(TRUE_C) | TRIAL_READING_MATCH |
| 七月に行く | しちがつに行く | 読み(月) | PASS | PRODUCTION_PASS |
| 1日で終わった | 一日で終わった | 漢数字/算用数字+助数詞(日) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 10代の若者 | 十代の若者 | 漢数字/算用数字+助数詞(代) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 20代の人 | 二十代の人 | 漢数字/算用数字+助数詞(代) | NG(TRUE_C) | TRIAL_NOTATION_MATCH |
| 十代の若者 | じゅうだいの若者 | 読み(代) | PASS | PRODUCTION_PASS |

## D. 敵対的反例(合成35件): 誤PASSしてはならない

| 原稿 | ASR | 種別 | Before | After |
|---|---|---|---|---|
| 三日間 | 二日間 | 値違い | NG | NO_RESCUE |
| 三日間 | 4日間 | 値違い | NG | NO_RESCUE |
| 3日間 | 四日間 | 値違い | NG | NO_RESCUE |
| 三人で行きました。 | 四人で行きました。 | 値違い | NG | NO_RESCUE |
| 30人が来ました。 | 40人が来ました。 | 値違い | NG | NO_RESCUE |
| 三十人が来ました。 | 四十人が来ました。 | 値違い | NG | NO_RESCUE |
| 十五件ありました | 50件ありました | 値違い(位取り) | NG | NO_RESCUE |
| 一万円です | 千円です | 桁違い | NG | NO_RESCUE |
| 百円です | 10円です | 桁違い | NG | NO_RESCUE |
| 二十人が来た | 2人が来た | 桁違い | NG | NO_RESCUE |
| 千円です | 1円です | 桁違い | NG | NO_RESCUE |
| 百万円です | 100円です | 桁違い | NG | NO_RESCUE |
| 1,000円です | 100円です | 桁違い | NG | NO_RESCUE |
| 0.5倍になる | 5倍になる | 小数点 | NG | NO_RESCUE |
| 三時に着く | 3時間で着く | 助数詞違い | NG | NO_RESCUE |
| 三日待った | 三回待った | 助数詞違い | NG | NO_RESCUE |
| 三日間 | 3日 | 助数詞違い(間の脱落) | NG | NO_RESCUE |
| 四月に会う | 4日に会う | 助数詞違い | NG | NO_RESCUE |
| 20％の人 | 30％の人 | 値違い(%) | NG | NO_RESCUE |
| 二泊三日の旅 | 三泊二日の旅 | 順序入替 | NG | NO_RESCUE |
| 三日坊主で終わった | 四日坊主で終わった | 値違い(慣用句) | NG | NO_RESCUE |
| 十分待った | 10分待った | 曖昧語(十分=sufficient/10分) | NG | AMBIGUOUS_NO_RESCUE |
| 10分待った | 十分待った | 曖昧語(十分=sufficient/10分) | NG | AMBIGUOUS_NO_RESCUE |
| 十分に理解した | 10分に理解した | 曖昧語(十分=sufficient/10分) | NG | AMBIGUOUS_NO_RESCUE |
| 三日間行かない | 3日間行く | 否定の欠落 | NG | NO_RESCUE |
| 3日間ない | 三日間ある | 否定の反転 | NG | NO_RESCUE |
| 三人で来た | 3人で来なかった | 否定の追加 | NG | NO_RESCUE |
| 三日間は休む | 3日間は働く | 別語 | NG | NO_RESCUE |
| 三日間 | 三日目 | 別語 | **誤PASS** | VETO_PROD_PASS |
| 三日間 | ふつかかん | 読み違い(値違い) | NG | NO_RESCUE |
| 二人で行く | さんにんで行く | 読み違い(値違い) | NG | NO_RESCUE |
| 三人で行く | よにんで行く | 読み違い(値違い) | NG | NO_RESCUE |
| 三日間の旅 | さんにちかんの旅 | 真の誤読(みっか→さんにち) | NG | NO_RESCUE |
| 10代の若者 | 20代の若者 | 値違い(代) | NG | NO_RESCUE |
| 三階に行く | 四階に行く | 値違い(階) | NG | NO_RESCUE |
