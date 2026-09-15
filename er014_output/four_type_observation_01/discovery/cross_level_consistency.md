# Cross-Level Consistency: A2 vs B1B (Discovery, post fact-fix, CONT2 final)

| Marker | A2 | B1B | Consistent? |
|---|---|---|---|
| F002 total sample | no | no | absent in both |
| F002 video watchers | no | no | absent in both |
| F002 fluent group | no | no | absent in both |
| F002 disrupted group | no | no | absent in both |
| F002 base-rate group | no | yes | present in B1B only |
| F001 sample | yes | yes | present in both |
| F005 duration range | yes | yes | present in both |
| F006 sample | yes | yes | present in both |
| F007 sample | yes | yes | present in both |
| F011/F010 duration | yes | yes | present in both |
| F011 sample (hedged) | yes | yes | present in both |
| F012 review count | yes | yes | present in both |

Overall consistent (no direct numeric contradiction detected): True

Notes:
- F002 video watchers: 単純な部分一致'37'はF012('review of 37 studies')へ誤ヒットする(CONT1のoperator修正でF002の視聴者数は本文から削除済みのため)。このため'37'の直近20文字に'stud'(study/studies)を含む場合は除外し、それ以外の独立した'37'のみをhitとする。A2/B1Bとも現在は視聴者の具体的人数を明記していないため、この行は'no/no'になる想定。

All quotations/markers in this table are derived directly from the final canonical files `a2/article.md` and `b1b/article.md` as of this task (EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE, CONT2).

## USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY B1B短文化とA2のCross-Level Consistency(STOP時点)

B1Bのfull_story_part2該当文は、Attempt1(1文短文化)・Attempt2(2文分割、意味不変)とも
Fact Checker A'/Ledger Deviation Checker(diff QA)・Directional Fact Precheckは通過したが、
既存TTS/ASR検証(既存上限3回)はいずれも通らず(TRUE_CONTENT_MISMATCH x3+x3)、B1B音声は
未完成のままSTOPした(USER_DECISION_REQUIRED)。現在のcanonical b1b/article.md本文は
Attempt2(2文分割)の状態「In a study of about 2,500 college students in 11 countries, an
everyday activity was enjoyed more than thinking for pleasure. This was true in every country
tested.」で確定している(QAはPASS、音声のみ未完成)。

A2側は「In a study of 2,557 college students at 12 sites in 11 countries, an everyday activity
was more enjoyable than thinking for pleasure in every country tested.」のままで本タスクでは
変更していない。両者の差(2,557 vs about 2,500、12 sitesの有無、1文 vs 2文)はLevel間の解像度差
(A2はより正確な数値+siteを保持、B1BはTTS安定性のため丸め+分割を試行)であり、Ledger F007との
矛盾ではない(Spoken-first Number Treatment原則の範囲内)。

## USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY A2再生成後のCross-Level Consistency

A2はDiscovery S2正式Production path(同一Verified Fact Ledger、Research再実行なし)で再生成した
(新word_count=530語、公式ロジック[見出し除外・本文のみ])。B1B(内部ID b1b)側は本タスクでは
本文・音声とも変更していない(Part Aは既存attempt音声のHuman Review player作成のみ)。

F007(college students study)該当文の引用:
- A2(新版): college students at 12 sites in 11 countries, everyday activities were more enjoyable than thinking for pleasure in every country.
- B1B(現行): college students in 11 countries, an everyday activity was enjoyed more than thinking for pleasure.

両者の差(数値の丸め方・site数の有無・文分割)はLevel間の解像度差であり、Ledger F007との直接矛盾は
本チェックの範囲では検出されなかった(簡易grepによる軽量再突合、旧cross_level_consistency.mdの
詳細marker表[F001-F012]は本タスクでは再生成していない。フルの再生成が必要な場合はユーザー判断)。
