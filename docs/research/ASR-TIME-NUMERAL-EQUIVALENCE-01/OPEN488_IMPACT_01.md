# OPEN488_IMPACT_01(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、OPEN-488 24時間表記・分00〜09 の影響調査、API 0・Production変更0)

## 結論(先に)
**分類: 24時間表記=不具合ではない(現行で正しくPASS、対応不要) / 分00〜09の語形(`ten oh five`↔`10:05`)=仕様外の拡張(現行は意図的に保守的なNG側)かつ実害未観測 → 対応不要(根拠を記録)。独断で新仕様は追加しない。**

## 1. 現行仕様が想定する時刻表現の範囲(照合)
- `er021 _try_clock_pair`(OPEN-482案C): 時1〜12 + 分10〜59 の隣接2語→数字化後と同じ2atom(am/pm付きはtime atom)。00〜09分・24時間表記は意図的に対象外(Opus OPUS_REVIEW_01.md:42『24時間表記・分00〜09: 救済の追加にあたるため別件』、DESIGN_01の範囲定数`_CLOCK_MINUTE_MIN,_MAX=10,59`)。
- `er021 _try_spoken_time`(am/pm付きの語形時刻)は分`oh five`を扱う: `six oh five am`↔`6:05 am` はPASS(実測)。am/pm無しは『時刻として確定させない(安全側)』(er021:373)と明記。
- `er078 _clock_pair`: 数字2atom(時0〜24・分10〜59)↔time atom。

## 2. 実測(正式経路の純関数、Primary 1本。`p488_probe_03.txt`、`$TMP/p488.py`)
| 表現 | 結果 | 判定 |
|---|---|---|
| `nineteen thirty`↔`19:30`、`19:30`↔`nineteen thirty`、`fourteen fifteen`↔`14:15`、`nineteen hundred`↔`19:00` | PASS(分類層でtoken一致`19 30`==`19 30`。value_guard=UNKNOWN[止めない]) | **現行で正しくPASS=不具合なし**(案A/Bいずれの影響評価でも案Aでは不変、TEST_MATRIX_487_01 #23-25) |
| `At 19:30`↔`At 7:30 pm` | NG_PROTECTED(p1_value_diff) | 正しい非同値(24時間と12時間+pmの対応は別表記の意味変換=新規則になるため救済しない) |
| `ten oh five`↔`10:05`(am/pmなし) 、`ten o five`↔`10:05`、`6:05`↔`six oh five` | **NG_PROTECTED(p1_value_diff)=誤NG** | 仕様外の拡張候補(上記の意図的な保守設計) |
| `six oh five am`↔`6:05 am` | PASS | 既存仕様内(am/pm付き) |
| `ten oh five`↔`10:50`/`1005` | NG | 正しい非同値 |
| `three o'clock`↔`3:00`、`twelve o'clock`↔`12:00` | NG_SECONDARY_UNAVAILABLE | 承認済みer109(X/Z、`o'clock`を伴う読みは同値)の対象。Primary 1本の純関数では不可だがX/Zはer109が救済設計。A/B/Cは範囲外 |

## 3. 発生状況と実害(既存Production入力・ASR結果の実測)
対象: 全リポジトリ47,132 json/jsonlから抽出した(canonical, asr)対 5,330対(replay基盤)と、HR queue 21ファイル503イベントのcanonical/asr text。
| 項目 | 件数 |
|---|---|
| 24時間表記(13〜23時)の時刻が canon/asr に出現 | **0**(`17:58`等のhit多数は全て ISO timestamp/ファイル時刻でnarration本文ではない) |
| 分00〜09 の語形(`oh`/`o`/`zero`+一桁)が canon/asr に出現 | 2(同一fixture=`six oh five`、OPEN-482/488のTrial用corpus。実作品の本文・ASRではない) |
| 分00〜09 の数字表記(`11:04`等) | canon 81 / asr 73(全て**数字表記同士で一致**。ASRは時刻を数字で返す傾向: 分0X時刻のasrは全て`H:MM`数字) |
| 該当表現に起因する 誤NG・誤PASS・不要な再生成・Human Review | **0件**(HR queue 503イベントの時刻表現は`11:04`/`10:16`の数字のみで、語形・24時間表記なし) |
- 時刻表現そのものが少ない: 5,330対中、時刻らしい表現を含むのは実質3記事程度(`11:04`の記事・`10:16`の記事等、重複排除前の対数)。

## 4. 対応する場合の技術的難易度・影響・量産単価(見積)
- 24時間表記: 修正不要(現行PASS)。
- 分00〜09語形: er021 `_try_clock_pair`が『分=`oh|o|zero`+一桁語』を許す拡張(約15行)+value_guard `_clock_pair`の対応(約8行)+正規化層との整合の3点。時刻は am/pm なしだと `seven oh seven`(Boeing 707型・部屋番号等)と区別できず、**誤PASSのリスクを伴う新しい受理面**になるため、am/pm必須等の追加ルールが必要=新仕様の設計・Opusレビュー対象。API費用0、量産単価への影響0(判定は純関数、再生成が減る方向だが対象が観測0件)。
- 共通化: OPEN-489(and分割)・OPEN-487(despace境界)とは別層(Tier1 atom化の時刻形追加)。OPEN-489の`_consume_number_word_run`修正と同じ関数に触れるが、機能的な共通化はできない(条件が別)。487案Aは24時間表記・`oh`の扱いに影響しない(確認済み)。

## 5. 推奨と記録
- **対応不要(実害なし・拡張候補、新仕様は独断で追加しない)**。トリガ(再評価条件): 実作品で分00〜09語形/24時間表記が原因の誤NG・再生成・HR Lockが1件でも観測されたとき(その時点で『不具合』か『拡張』かを再分類)。OPEN_ITEMSのOPEN-488へ上記根拠を記録する。
- ユーザー判断は不要(判断候補なし。仕様拡張を採るかどうかは実害観測後の別判断)。
