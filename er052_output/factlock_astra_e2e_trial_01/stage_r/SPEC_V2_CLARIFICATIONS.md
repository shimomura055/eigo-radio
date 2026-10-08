# 仕様v2 運用明確化(委任_07、Fable決定、2026-10-09)
規則変更ではなく、未定義事例への適用判断。
(a) 台帳の個別記録に `date_or_period` / `numeric_value` 欄が無い場合は、その記録に限り代替規則(statement内の主数字・日付)を適用する(台帳単位の代替規則を記録単位に適用)。該当: byd_recall(date欄なし4記録)、central_bank_mortgage(date欄なし1記録)、各台帳のnumeric_value欄なし記録(数値を持たない記録は対象外)、small_bag(台帳単位でnumeric欄なし)。
(b) B3 brief内の丸め表現(例: hormuz新B3「約25時間後」、台帳HF-007は「約24時間48分後」)は `unmapped_claims` に「新数値(丸め)」として記録する。記事の中心数字が台帳外としてSTOP条件に該当するかは注記統合時に機械判定する。
実測(委任_07): 10テーマ中、B3 brief内の台帳外数字はhormuzの「25」のみ(他9テーマは0)。
