# match_results.md — 機械一致判定(仮)+ Advanced解説チェック

機械判定はexact/substringのみ。同義・学習単位の近さを含む最終PASS/STRONG PASS/FAILはREPORTでSonnetが目視判定する。


## sewer_standard (machine_match=2/5)

| phrase | is_topic_word | machine_match_label | matched_expected |
|---|---|---|---|
| joining together | False | NO_MACHINE_MATCH | None |
| instead of ... | False | MACHINE_PARTIAL | instead of |
| take care of the rest | False | MACHINE_PARTIAL | take care of |
| hard to find | False | NO_MACHINE_MATCH | None |
| grow old | False | NO_MACHINE_MATCH | None |

## sewer_advanced (machine_match=1/5)

| phrase | is_topic_word | machine_match_label | matched_expected |
|---|---|---|---|
| replace A with B | False | EXACT | replace A with B |
| take care of the rest | False | NO_MACHINE_MATCH | None |
| hard to find where A is damaged | False | NO_MACHINE_MATCH | None |
| come in | False | NO_MACHINE_MATCH | None |
| move A closer to B | False | NO_MACHINE_MATCH | None |

## meta_standard (machine_match=0/5)

| phrase | is_topic_word | machine_match_label | matched_expected |
|---|---|---|---|
| tell ... what you need | False | NO_MACHINE_MATCH | None |
| not always a bad thing | False | NO_MACHINE_MATCH | None |
| contain personal information | False | NO_MACHINE_MATCH | None |
| hand ... to ... | False | NO_MACHINE_MATCH | None |
| feel safe | False | NO_MACHINE_MATCH | None |

## meta_advanced (machine_match=0/5)

| phrase | is_topic_word | machine_match_label | matched_expected |
|---|---|---|---|
| on A's behalf | False | NO_MACHINE_MATCH | None |
| raise concerns | False | NO_MACHINE_MATCH | None |
| put A on hold | False | NO_MACHINE_MATCH | None |
| fill in | False | NO_MACHINE_MATCH | None |
| appear to be | False | NO_MACHINE_MATCH | None |

## 全体機械一致率(仮) 3/20
