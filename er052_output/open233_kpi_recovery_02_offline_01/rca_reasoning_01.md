### 全MAJOR claim(batch単位reasoning、reasoning記録あり)
- LLM非BLOCKING(降格候補): n=390 min=119 p25=486 med=1413 p75=2874 max=6432
- LLM BLOCKING: n=287 min=155 p25=776 med=1543 p75=2453 max=6432
  - reasoning[0,400): n=119 非BLOCKING=84 率=0.706
  - reasoning[400,700): n=81 非BLOCKING=53 率=0.654
  - reasoning[700,1200): n=89 非BLOCKING=41 率=0.461
  - reasoning[1200,1000000000): n=388 非BLOCKING=212 率=0.546
### batch内MAJOR=1件のみ(claimごとのreasoningに近い)
- LLM非BLOCKING(降格候補): n=61 min=119 p25=204 med=261 p75=516 max=2121
- LLM BLOCKING: n=109 min=155 p25=318 med=628 p75=972 max=2429
  - reasoning[0,400): n=74 非BLOCKING=39 率=0.527
  - reasoning[400,700): n=40 非BLOCKING=15 率=0.375
  - reasoning[700,1200): n=38 非BLOCKING=5 率=0.132
  - reasoning[1200,1000000000): n=18 非BLOCKING=2 率=0.111
### V7b・単独batch
- LLM非BLOCKING(降格候補): n=20 min=120 p25=203 med=248 p75=306 max=641
- LLM BLOCKING: n=15 min=155 p25=233 med=490 p75=611 max=963
  - reasoning[0,400): n=23 非BLOCKING=17 率=0.739
  - reasoning[400,700): n=9 非BLOCKING=3 率=0.333
  - reasoning[700,1200): n=3 非BLOCKING=0 率=0.000
  - reasoning[1200,1000000000): n=0
### Safety-critical claim
- LLM非BLOCKING(降格候補): n=6 min=259 p25=306 med=958 p75=3145 max=3145
- LLM BLOCKING: n=64 min=346 p25=1131 med=1683 p75=2357 max=4141
  - reasoning[0,400): n=3 非BLOCKING=2 率=0.667
  - reasoning[400,700): n=5 非BLOCKING=1 率=0.200
  - reasoning[700,1200): n=14 非BLOCKING=1 率=0.071
  - reasoning[1200,1000000000): n=48 非BLOCKING=2 率=0.042
### Safety-critical・単独batch
- LLM非BLOCKING(降格候補): n=4 min=259 p25=306 med=434 p75=958 max=958
- LLM BLOCKING: n=25 min=346 p25=716 med=1028 p75=1253 max=1895
  - reasoning[0,400): n=3 非BLOCKING=2 率=0.667
  - reasoning[400,700): n=5 非BLOCKING=1 率=0.200
  - reasoning[700,1200): n=13 非BLOCKING=1 率=0.077
  - reasoning[1200,1000000000): n=8 非BLOCKING=0 率=0.000
### 降格(最終非BLOCKING)のうちbasis=noneのreasoning
- basis=none: n=177 min=119 p25=334 med=870 p75=2070 max=5523
- basis!=none: n=221 min=138 p25=805 med=1759 p75=2874 max=6432
### Safety-critical誤降格各件のreasoning(batch単位)と同groupのBLOCKING回の中央値
- ner_01_iter8 B3 rub=V5 reasoning=958 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895
- ner_01_iter8 B3 rub=V5 reasoning=434 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895
- ner_01_iter8 A2A3-0 rub=V5 reasoning=3145 同sub_id・同batchサイズのBLOCKING回: n=16 min=1552 p25=1683 med=2282 p75=3046 max=4141
- ner_01_iter8 A2A3-0 rub=V5 reasoning=3145 同sub_id・同batchサイズのBLOCKING回: n=16 min=1552 p25=1683 med=2282 p75=3046 max=4141
- ner_01_rep24 B3 rub=V7b reasoning=259 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895
- ner_01_rep25 B3 rub=V7b reasoning=306 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895
- nner_01_rep7 B3 rub=R3''' reasoning=None 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895
- nner_01_rep7 B3 rub=R3''' reasoning=None 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895
- nner_01_rep7 B3 rub=R3''' reasoning=None 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895
- nner_01_rep7 B3 rub=R3''' reasoning=None 同sub_id・同batchサイズのBLOCKING回: n=21 min=628 p25=837 med=1120 p75=1325 max=1895