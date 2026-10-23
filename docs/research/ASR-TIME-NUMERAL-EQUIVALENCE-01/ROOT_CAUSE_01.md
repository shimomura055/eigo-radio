# ROOT_CAUSE_01 根本原因(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01、API 0、Production変更0)

再現スクリプト `root_cause_repro_01.py`(出力: `root_cause_repro_baseline_01.txt`=HEAD、`root_cause_repro_protoC_01.txt`=推奨案C)。正式経路の関数(`_tier1_atoms`・`normalize_numeric`・`value_guard`・`unified_judge`)を実入力で呼んだ実測。

## 結論(先に)
**構造問題と判定する**: 『隣接する数詞語2語』の読みを、文脈なしに、**層ごとに別の1通りで固定**している。
- er006 `_convert_cardinal_words`(:296): 分割して2数字(`ten thirty`→`10 30`)
- er021 `_parse_bare_number_run`(:249): 2つの2桁グループ=**年ペア読み・桁連結の1数**(`ten thirty`→number 1030)。一の位の語+十の位の語(`two thirty`)は単独一桁語規則でliteral+30
- er021 `_try_spoken_time`(:340) + er078 `_clock_pair`(:531): am/pm付き or 『数値2atom vs time1atom』のみ時刻
→ 同じ発音『ten thirty』が number 1030 / time 1030 / num10+num30 / literal+num30 の4通りに変換され、**どの組合せが一致するかは偶然**(下表)。OPEN-482の2件は同じ原因の2つの現れ。個別救済(例外登録)では次の組合せ(`one thirty`・`two fifteen`・`ten thirty five`・`10 thirty pm`等)で再発するため、atom化の1点で揃える(DESIGN_01)。

## (1) 発生機序: 純語形`ten thirty` vs `10:30`
実測(root_cause_repro_baseline_01.txt):
```
'At ten thirty'  atoms=[literal at, number 1030]        <- _parse_bare_number_run が 10*100+30 の桁連結に
'At 10:30'       atoms=[literal at, time 1030]          <- _TIME_RE(:405)
value_guard('At ten thirty','At 10:30') = UNKNOWN  "kind_mismatch:num/time:'1030'->'1030'"   (値は同じ1030だが kind が number≠time)
```
- 機序: 語形側が number(年/桁連結)、記号側が time → `_compare_pair`(er078:376)が kind不一致=UNKNOWN。
- **現実の影響(重要な訂正)**: 統一Judgeの最終Gateが止めるのは DIFF のみ(`er078_asr_unified_judge_01.py:541,688`)。UNKNOWN は止めないので、この純語形の組は**現行でもPASS**(正式経路再現: `judge=PASS/primary_pass`)。OPEN-482(1)の『NG』は value_guard 単体の戻り値(UNKNOWN=PASS不可の安全側表現)であって、Primary 1本の正式判定では偶然PASSしている。
- **現実にNG(誤NG)を起こす経路**(同根の別の現れ。実測 `root_cause_repro_baseline_01.txt` C節 / `baseline_matrix_01.txt`):
  1. canon=TTS数字化後(`At 10 thirty`: `tts_safe_number_words_en`は two..twelve のみ数字化=er003_v1_n3_01_tts_generate.py:973) × ASR=語形(`ten thirty`/`ten-thirty`): canon=[num10,num30]、ASR=[number 1030] → **DIFF → NG_PROTECTED(final_gate_value_diff)**。**c8実run(`run_sf_prod_01`)の実ASR対で再現済み**: canon『At 10 thirty』×ASR『At ten-thirty』(replay基盤が抽出した実対、案Cで NG→PASS)。
  2. canon=数字化後 × ASR=`10 30`/am・pm付き(`10 thirty pm` vs `10:30 pm`、`1 30`等)→ DIFF → NG。
  3. canon=語形のまま(`one thirty`はoneが数字化されない / KP英語は`tts_safe_kp_en`で数字化されない)× ASR=`1:30`: UNKNOWN(PASSだが、`1 30`なら DIFF)。
- 発生し得る経路まとめ: 原稿が数字化されてTTSに渡る経路(本文・Preview・Comment等)と純語形のまま判定に届く経路(KP英語・`one thirty`・Secondary/Whisper転写がword形のとき)の**両方**が実在し、ASR側表記が不定のため全組合せが起こり得る。

## (2) 発生機序: 純語形`ten thirty` vs `1030`(桁連結が一致)
```
'At ten thirty'  atoms=[at, number 1030]     'At 1030' atoms=[at, number 1030]    -> 同一atom
classify_asr_match(...,role=FULL_STORY) -> NUMERIC_EQUIVALENCE_MATCH (Tier1 early-exit)
unified_judge -> PASS / primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE   (最終Gate自体がskipされる)
```
- 機序: (1)と同じ年ペア読みが、**相手が桁連結の数 1030 のときだけ**同kind・同値になり Tier1 が等価と断定する。Tier1由来のPASSは `APPROVED_EQUIVALENCE_BASES`(er078_asr_unified_judge_01.py:68)に入っており**最終Gateを通らない**ため、value_guardの値判定すら受けない(`ten thirty five`↔`1035` も同様にPASS)。
- 同型の取り違え: `eleven fifty`↔`1150`、`twelve fifteen`↔`1215`、`ten thirty five`↔`1035`(実測 baseline_matrix_01.txt)。逆に canon が数字化済みの `10 thirty`↔`1030` は value_guard が DIFF で正しくNG(経路差による非対称)。
- 年号は別: `nineteen ninety`↔`1990`・`twenty twenty six`↔`2026` は『分が60以上または時が13以上』で時刻として成立せず、年ペア読みの本来の用途。これを壊さないことが制約。

## (3) 構造問題かの判定
Yes。根拠: (a) 3つの層が同じ語列に別の読みを与える(上記)、(b) 修正済みの第1層(er006 b5138e452)・第2層(er078 e0eb13ab4)は各層内で閉じており、第3の層(er021 atom化)が未整合のまま残った、(c) 最終Gateの作用が非対称(DIFFのみ・Tier1はskip)で層間の食い違いが『誤NG』と『誤PASS』に分かれて現れる。3回目の局所パッチ(`_guard_en`にさらに分岐を足す等)は不採用とし、**atom化の1点(er021 `_tier1_atoms`)で隣接数詞語の読みを時刻形に統一**する(DESIGN_01案C)。

## 付: 新所見(範囲外、Fableへ報告)
- F-1: `tts_safe_number_words_en` は space区切りの複合数(`thirty five`)の `five` だけを `5` にする(ハイフン複合は保護)。canon が `thirty 5` になり、分類層(normalize_numeric)が `30 5` と読むため `35`/`thirty five` とNG(`thirty 5 people`↔`35 people` TRUE_CONTENT_MISMATCH、実測)。時刻に限らない既存不具合の候補(原稿が『thirty five』とスペースで書かれた場合のみ)。
- X-2: `one hundred thirty people`↔`1:30 people` は分類のdespace一致+value_guard UNKNOWN(止めない)でPASS(現行も案C後も同じ)。`At 1030`↔`At 10:30` は er109 が承認済み同音規則で同値(`er109_probe_baseline_01.txt`: RESCUE)。いずれも本件(OPEN-482)の2件の外。
