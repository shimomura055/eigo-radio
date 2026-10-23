# OPUS_REVIEW_REQUEST_01(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01 → Fableが起動するOpus独立技術レビュー、条件A=新しい処理設計/条件B=同じ問題への3回目修正)

## レビュー対象(読む順)
1. `docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/ROOT_CAUSE_01.md`(原因と実測)
2. `DESIGN_01.md`(案A/B/C/D比較と推奨案C)、`CANDIDATE_C_01.diff`(案Cのscratch差分、HEAD比 +45行/-0、`proto_C/`は実Productionに未反映)
3. `TEST_MATRIX_01.md`(84件、修正前と案Cの正式経路判定)、`STRUCTURE_01.md`(判定構造)
4. replay: `protoC_vs_baseline_01.txt`(5,330対、PASS→NG 0)、`er109_probe_*_01.txt`、`unit_tests_01.txt`
前提(ユーザー原文): OPEN-482の2件を例外登録でなく既存判定構造の根本原因解消で解決し、正常を誤NGにせず異常を誤PASSにしない。品質基準は独断変更しない。`docs/pm/delegation_log/2026-10-24_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_USER_02.md` §1-②〜§5。

## 論点(判定を求める。各に 採否/修正案 を)
1. **誤PASSリスク**: 案Cは『時1〜12+分10〜59』の隣接2語を [num時,num分] に畳む(am/pm直後はtime atom)。時刻形に見える別の読み(例: 数量2つ、金額 `one fifty`=$1.50、番号 `chapter eleven fifty`)が、相手側の `10 30`/`1:30`/`10:30` と偶然一致して通る経路はないか。特に canon が数字化後(`10 thirty`)でASRが `10:30` のとき既存`_clock_pair`が EQUAL にする条件(分10-59・単位なし)との重なり。
2. **年号との衝突と品質基準**: `nineteen ninety`/`twenty twenty`/`twenty twenty six`/`ten sixty six` は不変だが、`twelve fifteen`(1215)/`eleven fifty`(1150)型(時10〜12+分10〜59)の語形↔桁連結は PASS→NG になる(ユーザー指示②-2『ten thirty↔1030を一致扱いしない』と同型の帰結)。これを『承認済み品質基準の変更』と見るか『同一仕様の整合』と見るか。見るなら範囲を狭める案(例: 時10〜12のみ除外など)の是非。
3. **桁連結の扱い**: (2)の解消は案Cで Tier1 が不一致になり value_guard の DIFF に回ることで達成される。一方 `At 1030`↔`At 10:30` は er109 承認規則で同値(RESCUE)、`one hundred thirty people`↔`1:30 people` は despace一致+UNKNOWN非阻止でPASS(X-2、現行も同じ)。これらを本件の範囲外とした判断は妥当か。value_guardの `kind_mismatch:num/time`(UNKNOWN)をDIFFに引き上げる案(最終Gateの作用変更)を併せて検討すべきか。
4. **Secondary ASR・同音救済との整合**: 案Cでは `ten thirty`↔`10:13` が UNKNOWN→DIFF になり、Primary NG時にP1(NG_PROTECTED、Secondary不呼出)へ変わる(数字化canonでは従来からこの扱い)。Primaryが `10:13` と誤聴しSecondaryが `10:30` と正聴するケースの救済機会を失う副作用の許容可否。KP vote(guard_lifted)・Tier1 approved basis skip・er109 span解除との相互作用に見落としはないか。
5. **3層の定数不整合**: er006(ones→tens/teens境界で分割)・er078 `_clock_pair`(時0-24・分10-59)・案C(時1-12・分10-59)の定数が3つ。共通化(例: 定数/関数を er021 に1つ置き他層が参照)すべきか、案Cの範囲に留めるか。
6. **replay基準の十分性**: 5,330対中、時刻パターンを含む実対は4件(c8のみ)。基準『judge PASS→NG 0』は妥当か。補う合成セット(TEST_MATRIX 84件)の網羅は十分か(追加すべき反例)。
7. **X/Z適用**: er021/er078は共有module(X/Z/A/B/C共通)。flagなし既定ONの不具合修正として、A/B/Cへの波及(時刻形語列を含む文のみ・方向は誤NG/誤PASS解消のみ)を27-7に照らし許容してよいか。`er109_xz_scope_01` は同音救済のscopeでありこの修正の適用範囲を制限しない理解でよいか。
8. 見落とし: 案Cが破る既存test/仕様(`er006_time_numeral_test_01`・`er078_time_atom_test_01` は案CでPASS確認済み)、日本語側(`_guard_ja`)への影響なし(英語のみ)の確認。

## 既知の限界(隠さず提示)
- 本環境は google.genai/pykakasi/cmudict系依存が無く、既存test 91件は修正前から失敗(失敗集合は案C前後で同一)。`er021_..._production_wiring_01_test_01` は collection不能。委任_02で依存のある環境の回帰(`run_project_regression.py`)が必要。
- F-1(`thirty 5`型の分類層不具合)・X-2は範囲外所見(ROOT_CAUSE_01.md付)。
- 24時間表記(`thirteen thirty`)・分00-09(`ten oh five`)は案Cでも未対応(従来どおり)。

## 返してほしい形式
各論点 `承認 / 条件付き承認(条件) / 却下(代替)` + 実装前に必須の修正点 + 委任_02で追加すべきtest/replay。
