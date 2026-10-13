# analysis_r1 (自動生成。層1=gate前の選定生出力、層2=gate。Coffeeのみアンカー採点)

## 比較表(Coffee)
| combo | Lv | valid/n | score平均/上限 | アンカー採用(full rank:回数) | fragment | 低優先枠/run | 創作比喩Imp/run | Jaccard | sel PASS | canon | redundancy | 費用/job | reasoning tok(sel) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M0P0 | adv | 3/3 | 20.0/47 | {'5': 3, '6': 3, '8': 2, '10': 1, '11': 1} | {'4': 3} | 0.67 | 0.0 | 0.508 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.853 | 2647 |
| M0P1 | adv | 1/3 | 18.0/47 | {'5': 1, '6': 1, '10': 1} | {'4': 1} | 1.0 | 0.0 | None | 1/3 | {'None': 2, 'CANONICALIZATION_PASS': 1} | {'REDUNDANCY_PASS': 1} | 0.6 | 3283 |
| M0P2 | adv | 3/3 | 17.67/47 | {'5': 3, '6': 3, '10': 2, '11': 1} | {'4': 1} | 1.0 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_NG': 2, 'REDUNDANCY_PASS': 1} | 0.951 | 3116 |
| M0P3 | adv | 3/3 | 18.0/47 | {'5': 3, '6': 3, '10': 3} | {'4': 3} | 1.0 | 0.0 | 0.778 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 1, 'REDUNDANCY_NG': 2} | 1.019 | 3659 |
| M0P4 | adv | 3/3 | 17.0/47 | {'5': 3, '6': 3, '10': 2} | {'4': 3} | 0.67 | 0.0 | 0.778 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_NG': 3} | 1.049 | 4057 |
| M1P0 | adv | 3/3 | 31.0/47 | {'1': 1, '4': 3, '5': 3, '6': 3, '10': 3} | {} | 1.0 | 0.0 | 0.667 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.819 | 2389 |
| M2P0 | adv | 3/3 | 38.0/47 | {'1': 3, '4': 3, '5': 3, '6': 3, '10': 2} | {} | 0.67 | 0.0 | 0.778 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.897 | 2842 |
| M2P1 | adv | 3/3 | 27.0/47 | {'4': 3, '5': 3, '6': 3, '10': 3} | {} | 1.0 | 0.0 | 1.0 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.86 | 2702 |
| M2P2 | adv | 3/3 | 27.0/47 | {'4': 3, '5': 3, '6': 3, '10': 3} | {} | 1.0 | 0.0 | 1.0 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_NG': 1, 'REDUNDANCY_PASS': 2} | 1.016 | 2039 |
| M2P3 | adv | 3/3 | 33.0/47 | {'1': 2, '4': 3, '5': 3, '6': 3, '10': 1} | {} | 0.33 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.962 | 3957 |
| M2P4 | adv | 3/3 | 26.0/47 | {'4': 3, '5': 3, '6': 3, '10': 2} | {} | 0.67 | 0.0 | 0.778 | 3/3 | {'CANONICALIZATION_PASS': 2, 'CANONICALIZATION_INVALID': 1} | {'REDUNDANCY_PASS': 2, 'None': 1} | 0.863 | 2833 |
| M3P4 | adv | 3/3 | 27.0/47 | {'4': 3, '5': 3, '6': 3, '10': 3} | {} | 1.0 | 0.0 | 1.0 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_NG': 2, 'REDUNDANCY_PASS': 1} | 0.978 | 2538 |
| M0P0 | std | 3/3 | 27.0/37 | {'1': 2, '3': 3, '8': 3, '9': 1, '11': 3, '12': 2} | {} | 2.0 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 2, 'CANONICALIZATION_INVALID': 1} | {'REDUNDANCY_PASS': 2, 'None': 1} | 0.888 | 3062 |
| M0P1 | std | 3/3 | 19.0/37 | {'3': 1, '7': 3, '8': 3, '9': 3, '11': 1} | {} | 1.33 | 0.0 | 0.667 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.967 | 4262 |
| M0P2 | std | 3/3 | 20.0/37 | {'3': 3, '8': 3, '9': 3, '11': 1, '12': 1} | {} | 1.67 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.902 | 4100 |
| M0P3 | std | 3/3 | 20.33/37 | {'3': 2, '7': 2, '8': 3, '9': 3, '11': 1} | {} | 1.33 | 0.0 | 0.619 | 3/3 | {'CANONICALIZATION_INVALID': 1, 'CANONICALIZATION_PASS': 2} | {'None': 1, 'REDUNDANCY_PASS': 2} | 1.054 | 4711 |
| M0P4 | std | 1/3 | 19.0/37 | {'3': 1, '8': 1, '9': 1} | {} | 1.0 | 0.0 | None | 1/3 | {'None': 2, 'CANONICALIZATION_PASS': 1} | {'REDUNDANCY_PASS': 1} | 0.673 | 3703 |
| M1P0 | std | 3/3 | 20.33/37 | {'3': 2, '7': 1, '8': 3, '9': 3, '11': 3, '12': 2} | {} | 2.67 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.919 | 3455 |
| M2P0 | std | 3/3 | 33.33/37 | {'1': 3, '3': 3, '7': 1, '8': 3, '9': 2, '11': 2, '12': 1} | {} | 1.67 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 2, 'CANONICALIZATION_INVALID': 1} | {'REDUNDANCY_PASS': 2, 'None': 1} | 0.879 | 3141 |
| M2P1 | std | 3/3 | 18.33/37 | {'3': 1, '7': 3, '8': 3, '9': 3} | {} | 1.0 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 2, 'CANONICALIZATION_INVALID': 1} | {'REDUNDANCY_PASS': 2, 'None': 1} | 0.987 | 5100 |
| M2P2 | std | 3/3 | 29.67/37 | {'1': 2, '3': 3, '7': 1, '8': 3, '9': 3, '12': 2} | {} | 1.67 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.871 | 3993 |
| M2P3 | std | 3/3 | 29.0/37 | {'1': 2, '3': 3, '7': 1, '8': 3, '9': 3} | {} | 1.0 | 0.0 | 0.587 | 3/3 | {'CANONICALIZATION_PASS': 3} | {'REDUNDANCY_PASS': 3} | 0.889 | 3607 |
| M2P4 | std | 3/3 | 21.33/37 | {'3': 3, '7': 1, '8': 3, '9': 3, '12': 1} | {} | 1.33 | 0.0 | 0.429 | 3/3 | {'CANONICALIZATION_PASS': 2, 'CANONICALIZATION_REVIEW_REQUIRED': 1} | {'REDUNDANCY_PASS': 3} | 1.014 | 4987 |
| M3P4 | std | 2/3 | 22.5/37 | {'3': 2, '7': 1, '8': 2, '9': 2, '12': 1} | {} | 1.5 | 0.0 | 0.667 | 2/3 | {'CANONICALIZATION_PASS': 2, 'None': 1} | {'REDUNDANCY_PASS': 2} | 0.952 | 4470 |

## 最終5件(層1: gate前の選定生出力のdisplay_phrase。role:display(候補)。全run)
### coffee_adv_M0P0 (round1)
- run1: T:lag / I:show up / I:come down / I:raw beans / I:hold on | backup=None score=23 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:lag / I:show up / I:come down / I:raw beans / I:right away | backup=None score=22 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:lag / I:show up / I:come down / I:price tag / I:come with<comes with> | backup=None score=15 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M0P1 (round1)
- run1: **KEY_WORDS_STRUCTURE_INVALID** [] [{'index': 0, 'reasons': ['日本語グロスに括弧書きの補足が含まれている(音声だけで意味が成立する自然な表現にすること)'], 'warnings': []}, {'index': 1, 'reasons': ['日本語グロスに括弧書きの補足が含まれている(音声だけで意味が成立する自然な表現にすること)'], 'warnings': []}]
- run2: **KEY_WORDS_STRUCTURE_INVALID** [] [{'index': 1, 'reasons': ['日本語グロスに括弧書きの補足が含まれている(音声だけで意味が成立する自然な表現にすること)'], 'warnings': []}, {'index': 2, 'reasons': ['日本語グロスに括弧書きの補足が含まれている(音声だけで意味が成立する自然な表現にすること)'], 'warnings': []}]
- run3: I:come down / I:show up / T:lag / I:come with<comes with> / I:hold on | backup=on a regular basis<on a regular basis> score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M0P2 (round1)
- run1: I:show up / I:come with<comes with> / I:come down / I:right away / T:price tag | backup=None score=17 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run2: I:show up / I:come with<comes with> / I:come down / I:hold on / T:lag | backup=None score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run3: I:come down / I:show up / I:come with<comes with> / I:hold on / T:price tag | backup=None score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M0P3 (round1)
- run1: I:lag / I:show up / I:come down / I:hold on / T:retail prices | backup=based on<an estimate based on interviews> score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:lag / I:come down / I:show up / I:hold on / T:price measure | backup=right away<right away> score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run3: I:lag / I:show up / I:come down / T:retail prices / I:hold on | backup=on a regular basis<on a regular basis> score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
### coffee_adv_M0P4 (round1)
- run1: I:show up / I:come with<comes with> / I:come down / T:lag / I:hold on | backup=take time<take time> score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run2: I:come down / I:show up / T:lag / I:price measure / I:come with<comes with> | backup=hold on<Hold on before> score=15 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run3: T:lag / I:come down / I:show up / I:come with<comes with> / I:hold on | backup=insider<market insiders> score=18 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
### coffee_adv_M1P0 (round1)
- run1: I:show up / I:come down / T:time lag / I:Hold on / I:retail prices | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:time lag / I:come down / I:show up / I:pump its fist<pumps> / I:hold on | backup=None score=39 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:time lag / I:come down / I:show up / I:hold on / I:come with<comes with> | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M2P0 (round1)
- run1: T:time lag / I:show up / I:come down / I:price tag / I:pump one's fist<pumps its fist> | backup=None score=36 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:time lag / I:show up / I:come down / I:pump one's fist<pumps its fist> / I:hold on | backup=None score=39 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:time lag / I:come down / I:show up / I:pump one's fist<pumps its fist> / I:hold on | backup=None score=39 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M2P1 (round1)
- run1: T:time lag / I:show up / I:come down / I:come with<comes with> / I:hold on | backup=take time<take time> score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:come down / I:show up / T:time lag / I:come with<comes with> / I:hold on | backup=take time<take time> score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:time lag / I:come down / I:show up in prices<show up> / I:come with costs<comes with> / I:Hold on | backup=retail prices<retail prices> score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M2P2 (round1)
- run1: T:time lag / I:show up / I:come down / I:come with<comes with> / I:hold on | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run2: I:show up / I:come down / I:hold on / T:time lag / I:come with<comes with> | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:show up / I:come down / T:time lag / I:come with<comes with> / I:hold on | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M2P3 (round1)
- run1: T:time lag / I:show up in<show up> / I:come down / I:hold on / I:come with<comes with> | backup=right away<right away> score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:time lag / I:show up / I:come down / I:come with costs<comes with> / I:pump one's fist<pumps its fist> | backup=roasting<Roasting> score=36 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:time lag / I:show up in<show up> / I:pump one's fist<pumps its fist> / I:come down / I:retail prices | backup=insiders<insiders> score=36 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M2P4 (round1)
- run1: T:time lag / I:come down / I:show up / I:hold on / I:come with<comes with> | backup=on a regular basis<on a regular basis> score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:show up / T:time lag / I:hold on / I:come down / I:come with<comes with> | backup=take time<take time> score=27 | canon=CANONICALIZATION_INVALID red=None
- run3: I:show up / I:come down / T:time lag / I:insider<insiders> / I:come with<comes with> | backup=hold on<Hold on> score=24 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_adv_M3P4 (round1)
- run1: I:come down / I:show up / T:time lag / I:hold on / I:come with<comes with> | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run2: I:show up / I:come down / I:hold on / I:come with<comes with> / T:time lag | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run3: I:come down / I:show up / T:time lag / I:come with<comes with> / I:hold on | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M0P0 (round1)
- run1: I:pump one's fist<pumps> / T:raw-bean / I:push prices up<prices up> / I:right away / I:on a regular basis | backup=None score=33 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:raw-bean / I:right away / I:take time / I:push prices up<prices up> / I:based on | backup=None score=18 | canon=CANONICALIZATION_INVALID red=None
- run3: T:raw bean<raw-bean> / I:pump one's fist<pumps> / I:right away / I:push prices up<prices up> / I:take time | backup=None score=30 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M0P1 (round1)
- run1: T:raw beans<raw-bean> / I:roasting / I:push prices up<prices up> / I:on a regular basis / I:based on | backup=take time<take time> score=25 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:raw beans<raw-bean> / I:roasting / I:on a regular basis / I:right away / I:based on | backup=take time<take time> score=17 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:on a regular basis / T:raw bean<raw-bean> / I:be based on<based on> / I:roasting / I:price tag | backup=take time<take time> score=15 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M0P2 (round1)
- run1: I:push prices up<prices up> / T:raw bean<raw-bean> / I:on a regular basis / I:take time / I:be based on<based on> | backup=None score=20 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:push prices up<prices up> / T:raw bean<raw-bean> / I:be based on<based on> / I:on a regular basis / I:feel like<feels like> | backup=None score=19 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:push prices up<prices up> / I:on a regular basis / I:right away / I:feel like<feels like> / T:raw bean<raw-bean> | backup=None score=21 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M0P3 (round1)
- run1: I:push prices up<prices up> / I:roasting / T:raw bean<raw-bean> / I:on a regular basis / I:based on | backup=right away<right away> score=25 | canon=CANONICALIZATION_INVALID red=None
- run2: I:push prices up<prices up> / T:raw-bean / I:roasting / I:on a regular basis / I:be based on<based on> | backup=take time<take time> score=25 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:on a regular basis / I:be based on<based on> / T:raw bean<raw-bean> / I:price tag / I:right away | backup=take time<take time> score=11 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M0P4 (round1)
- run1: **KEY_WORDS_STRUCTURE_INVALID** [] [{'index': 1, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}, {'index': 4, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}]
- run2: **KEY_WORDS_STRUCTURE_INVALID** [] [{'index': 1, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}, {'index': 2, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}, {'index': 3, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}]
- run3: I:push prices up<prices up> / T:raw beans<raw-bean> / I:on a regular basis / I:price tag / I:based on | backup=take time<take time> score=19 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M1P0 (round1)
- run1: T:raw bean<raw-bean> / I:push prices up<prices up> / I:roasting / I:right away / I:on a regular basis | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:raw-bean / I:push prices up<prices up> / I:take time / I:right away / I:on a regular basis | backup=None score=22 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:raw bean<raw-bean> / I:right away / I:feel like<feels like> / I:take time / I:on a regular basis | backup=None score=12 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M2P0 (round1)
- run1: T:raw bean<raw-bean> / I:pump one's fist<pumps its fist> / I:push prices up<prices up> / I:right away / I:on a regular basis | backup=None score=33 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:pump its fist<pumps its fist> / T:raw-bean / I:push prices up<prices up> / I:on a regular basis / I:take time | backup=None score=32 | canon=CANONICALIZATION_INVALID red=None
- run3: I:pump one's fist<pumps its fist> / T:raw bean<raw-bean> / I:roasting / I:right away / I:push prices up<prices up> | backup=None score=35 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M2P1 (round1)
- run1: T:raw beans<raw-bean> / I:roasting / I:on a regular basis / I:price tag / I:be based on<based on> | backup=take time<take time> score=15 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:raw beans<raw-bean> / I:roast beans<Roasting> / I:on a regular basis / I:push prices up<prices up> / I:based on | backup=take time<take time> score=25 | canon=CANONICALIZATION_INVALID red=None
- run3: T:raw-bean prices<raw-bean> / I:roast coffee<roast> / I:on a regular basis / I:price tag / I:based on interviews<based on> | backup=take time<take time> score=15 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M2P2 (round1)
- run1: I:push prices up<prices up> / I:on a regular basis / I:feel like<feels like> / I:take time / T:raw bean<raw-bean> | backup=None score=20 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:push prices up<prices up> / I:pump one's fist<pumps its fist> / I:on a regular basis / I:take time / T:raw bean<raw-bean> | backup=None score=32 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:pump one's fist<pumps its fist> / I:push prices up<prices up> / T:raw bean<raw-bean> / I:roast<Roasting> / I:on a regular basis | backup=None score=37 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M2P3 (round1)
- run1: T:raw bean<raw-bean> / I:push prices up<prices up> / I:pump one's fist<pumps its fist> / I:be based on<based on> / I:on a regular basis | backup=take time<take time> score=31 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:raw bean<raw-bean> / I:pump one's fist<pumps its fist> / I:push prices up<prices up> / I:on a regular basis / I:price tag | backup=based on<based on> score=31 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:raw bean<raw-bean> / I:push prices up<prices up> / I:roast / I:based on / I:on a regular basis | backup=price tag<price tag> score=25 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M2P4 (round1)
- run1: I:push prices up<prices up> / T:raw bean<raw-bean> / I:feel like<feels like> / I:on a regular basis / I:based on | backup=take time<take time> score=19 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:push prices up<prices up> / I:take for / I:on a regular basis / I:roast<Roasting> / T:raw bean<raw-bean> | backup=feel like<feels like a delay> score=25 | canon=CANONICALIZATION_REVIEW_REQUIRED red=REDUNDANCY_PASS
- run3: T:raw bean<raw-bean> / I:push prices up<prices up> / I:price tag / I:on a regular basis / I:take time | backup=based on<based on interviews> score=20 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### coffee_std_M3P4 (round1)
- run1: I:push prices up<prices up> / I:on a regular basis / I:based on / I:take time / T:raw bean<raw-bean> | backup=None score=20 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: **KEY_WORDS_STRUCTURE_INVALID** [] [{'index': 2, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}, {'index': 3, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}]
- run3: I:push prices up<prices up> / T:raw bean<raw-bean> / I:on a regular basis / I:based on / I:roast | backup=None score=25 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### hormuz_adv_M0P0 (phase2_C0_reuse)
- run1: I:give back<gave back> / I:futures / T:sea blockade / I:pull back<pulled back> / I:center stage | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run2: I:give back<gave back> / I:futures / T:sea blockade / I:pull back<pulled back> / I:center stage | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run3: T:sea blockade / I:Brent crude / I:give back<gave back> / I:futures / I:pull back<pulled back> | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
### hormuz_adv_M2P0 (round1)
- run1: I:give back<gave back> / I:Brent crude / T:sea blockade / I:futures / I:pull back<pulled back> | backup=center stage<stood at center stage> | canon=CANONICALIZATION_INVALID red=None
- run2: I:give back<gave back> / I:Brent crude / T:sea blockade / I:pull back<pulled back> / I:center stage | backup=futures<futures> | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
### hormuz_adv_M2P3 (round1)
- run1: I:give back gains<gave back> / I:pull back<pulled back> / T:sea blockade / I:Brent crude / I:center stage | backup=flashy<flashy> | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run2: I:give back<gave back> / I:futures / I:Brent crude / T:sea blockade / I:center stage | backup=pull back<pulled back> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### hormuz_std_M0P0 (phase2_C0_reuse)
- run1: **KEY_WORDS_STRUCTURE_INVALID** [] [{'index': 1, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}, {'index': 3, 'reasons': ["'normalization_note'が空、または文字列でない"], 'warnings': []}]
- run2: I:take back<Taken Back> / I:give back<gave back> / I:pull back<pulled back> / T:sea blockade / I:Brent crude | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run3: I:take back<Taken Back> / I:give back<gave back> / T:Strait / I:sea blockade / I:pull back<pulled back> | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
### hormuz_std_M2P0 (round1)
- run1: I:be taken back<Taken Back> / I:give back<gave back> / T:sea blockade / I:futures / I:strait | backup=pull back<pulled back> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:give back<gave back> / I:take back<Taken Back> / T:Strait / I:Brent crude / I:sea blockade | backup=center stage<center stage> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### hormuz_std_M2P3 (round1)
- run1: I:give back gains<gave back> / I:futures / I:take back a plan<Taken Back> / T:Brent crude / I:center stage | backup=pull back<pulled back> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:take back a plan<Taken Back> / T:sea blockade / I:by trade / I:pull back<pulled back> / I:center stage | backup=give back gains<gave back some gains> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### meta_adv_M0P0 (phase2_C0_reuse)
- run1: I:contract workers / I:unintentionally / T:behind the scenes / I:concierge / I:no way | backup=None | canon=CANONICALIZATION_INVALID red=None
- run2: I:behind the scenes / T:contract workers / I:unintentionally / I:no way / I:inappropriate | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:contract workers / I:behind the scenes / I:unintentionally / I:no way / I:inappropriate | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### meta_adv_M2P0 (round1)
- run1: T:behind the scenes / I:contract workers / I:no way / I:unintentionally / I:concierge | backup=call center<at a call center> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:contract worker<contract workers> / I:unintentionally / I:concierge / I:behind the scenes / I:no way | backup=troublesome<troublesome> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### meta_adv_M2P3 (round1)
- run1: T:behind the scenes / I:unintentionally / I:take care of<take care> / I:contract workers / I:no way | backup=troublesome<troublesome> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:behind the scenes / I:take care of<take care> / I:unintentionally / I:no way / T:contract workers | backup=concierge<concierge> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### meta_std_M0P0 (phase2_C0_reuse)
- run1: I:behind the scenes / I:the other end<other end> / T:contract workers / I:concierge / I:by mistake | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:behind the scenes / T:contract workers / I:on the other end<other end> / I:concierge / I:bargain | backup=None | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:behind the scenes / T:contract workers / I:other end / I:bargain / I:concierge | backup=None | canon=CANONICALIZATION_INVALID red=None
### meta_std_M2P0 (round1)
- run1: T:behind the scenes / I:contract worker<contract workers> / I:the other end<other end> / I:instead of / I:by mistake | backup=bargain<bargain over fees> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:behind the scenes / T:contract workers / I:the other end<other end> / I:bargain / I:concierge | backup=call center<call center> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
### meta_std_M2P3 (round1)
- run1: I:behind the scenes / T:contract worker<contract workers> / I:on the other end<other end> / I:bargain / I:inappropriate | backup=by mistake<by mistake> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:behind the scenes / I:inappropriate / I:on the other end<other end> / I:bargain / T:contract workers | backup=by mistake<by mistake> | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS

## 層2 gate詳細(canonicalization/Redundancyの非PASS)
- coffee_adv_M0P2 run1: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 4, 'meaning_overlap': 'PASS', 'usage_context_overlap': 'PASS', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': '語句自体は「現れる・反映される」と「すぐに」で意味や文法上の価値が異なります。ただし記事内では、どちらも市場の変化が小売価格にすぐ反映されないという遅れを示しています。'}] person_items=[]
- coffee_adv_M0P2 run2: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 5, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'この文脈のshow upは、豆の価格変化が小売価格にあとから表れることを指し、lagもその変化が表れるまでの遅れを指しています。文法的な学習価値は異なりますが、記事内では価格への遅れた反映というほぼ同じ概念を担っています。'}] person_items=[]
- coffee_adv_M0P3 run2: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 3, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'どちらも、原料価格の変化が小売価格に遅れて反映されるという内容を担っています。lagは遅れそのもの、show upはその変化が後になって価格に表れることを表しますが、この記事では実質的に同じ価格転嫁の遅れを別の形で示しています。'}] person_items=[]
- coffee_adv_M0P3 run3: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 2, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': '記事ではどちらも、原料豆の価格変化が小売価格に遅れて反映されることを表しています。文法上は名詞と句動詞で異なりますが、意味・文脈・記事内の役割は実質的に重なります。'}] person_items=[]
- coffee_adv_M0P4 run1: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 4, 'meaning_overlap': 'PASS', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': '語義は「表れる」と「時間差がある」で異なりますが、どちらも豆価格の変化が小売価格に反映されるまでの遅れを説明する文脈・役割を担っています。記事内の内容としては近いものの、show upは出現、lagは遅延そのものを表す点で文法・語彙の学習価値は異なります。'}] person_items=[]
- coffee_adv_M0P4 run2: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 2, 'rank_b': 3, 'meaning_overlap': 'PASS', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'show up自体は「表れる」、lagは「遅れ」で意味は同じではありません。ただし、この記事ではどちらも原料価格の変化が小売価格に反映されるまでの遅れを説明し、使用文脈と概念上の役割が重なります。'}] person_items=[]
- coffee_adv_M0P4 run3: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 3, 'meaning_overlap': 'PASS', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'lagは反映までの遅れ、show upは結果として価格に現れることを表し、語義自体は異なります。ただし記事ではどちらも豆価格の変化が小売価格に反映される過程を扱っています。'}] person_items=[]
- coffee_adv_M2P2 run1: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 2, 'meaning_overlap': 'PASS', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'time lagは遅れそのもの、show upは影響が表面化することを表すため、語義や文法上の学習価値は異なります。ただし記事ではどちらも、豆の価格変化が小売価格にすぐ反映されないという中心概念を担っています。'}] person_items=[]
- coffee_adv_M2P4 run2: canon=CANONICALIZATION_INVALID reasons=[[{'index': 4, 'rank': 5, 'reasons': ["key_phrase('come with costs')がdisplay_phraseと一致せず、source_span('comes with')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 4, 'rank': 5, 'reasons': ["key_phrase('comes with costs')がdisplay_phraseと一致せず、source_span('comes with')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=[]
- coffee_adv_M3P4 run1: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 2, 'rank_b': 3, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'どちらも、豆の価格変化が小売価格に遅れて反映されるという内容を扱っています。show upは結果が後から表れること、time lagはその反映までの時間差を表し、記事内での概念上の役割も実質的に重なります。'}] person_items=[]
- coffee_adv_M3P4 run2: canon=CANONICALIZATION_PASS reasons=[[{'index': 3, 'rank': 4, 'reasons': ["key_phrase('come with costs')がdisplay_phraseと一致せず、source_span('comes with')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], []] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 5, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'この記事では、どちらもコーヒー豆の価格変化が小売価格に反映されるまでの遅れを表しています。show upは結果が表れること、time lagはその反映までの時間差を表しますが、記事内では実質的に同じ内容を担っています。'}] person_items=[]
- coffee_std_M0P0 run2: canon=CANONICALIZATION_INVALID reasons=[[{'index': 0, 'rank': 1, 'reasons': ["key_phrase('raw-bean prices')がdisplay_phraseと一致せず、source_span('raw-bean')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}, {'index': 4, 'rank': 5, 'reasons': ["key_phrase('based on interviews')がdisplay_phraseと一致せず、source_span('based on')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 0, 'rank': 1, 'reasons': ["key_phrase('raw-bean prices')がdisplay_phraseと一致せず、source_span('raw-bean')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}, {'index': 4, 'rank': 5, 'reasons': ["key_phrase('based on interviews')がdisplay_phraseと一致せず、source_span('based on')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=[]
- coffee_std_M0P3 run1: canon=CANONICALIZATION_INVALID reasons=[[{'index': 4, 'rank': 5, 'reasons': ["key_phrase('based on interviews')がdisplay_phraseと一致せず、source_span('based on')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 4, 'rank': 5, 'reasons': ["key_phrase('based on interviews')がdisplay_phraseと一致せず、source_span('based on')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=[]
- coffee_std_M2P0 run2: canon=CANONICALIZATION_INVALID reasons=[[{'index': 1, 'rank': 2, 'reasons': ["key_phrase('raw-bean prices')がdisplay_phraseと一致せず、source_span('raw-bean')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 1, 'rank': 2, 'reasons': ["key_phrase('raw-bean prices')がdisplay_phraseと一致せず、source_span('raw-bean')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=['pump its fist']
- coffee_std_M2P1 run2: canon=CANONICALIZATION_INVALID reasons=[[{'index': 4, 'rank': 5, 'reasons': ["key_phrase('based on interviews')がdisplay_phraseと一致せず、source_span('based on')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 4, 'rank': 5, 'reasons': ["key_phrase('based on interviews')がdisplay_phraseと一致せず、source_span('based on')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=[]
- coffee_std_M2P4 run2: canon=CANONICALIZATION_REVIEW_REQUIRED reasons=[[]] red=REDUNDANCY_PASS dup=[] person_items=[]
- hormuz_adv_M0P0 run1: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 4, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'この文脈では、どちらも上昇していた原油価格が一時的に下がる動きを表し、典型的な使用場面と記事内の役割もほぼ同じです。ただし、give backは目的語を取って上昇分を失う表現、pull backは自動詞的に後退・下落する表現で、構文上の学習価値は異なります。'}] person_items=[]
- hormuz_adv_M0P0 run2: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 4, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'この記事では、どちらも原油価格が一時的に下がる動きを表し、同じ価格変動を別の表現で説明しています。一方、give backは上昇分を失う他動詞的な句動詞、pull backは後退・下落を表す句動詞で、構文上の学習価値には違いがあります。'}] person_items=[]
- hormuz_adv_M0P0 run3: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 3, 'rank_b': 5, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'どちらも記事では、上昇した原油価格が一時的に下がる動きを表しています。ただしgive backは上昇分を失う他動詞的な表現、pull backは価格が後退する自動詞的な表現で、構文上の学習価値は異なります。'}] person_items=[]
- hormuz_adv_M2P0 run1: canon=CANONICALIZATION_INVALID reasons=[[{'index': 0, 'rank': 1, 'reasons': ["key_phrase('give back gains')がdisplay_phraseと一致せず、source_span('gave back')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}, {'index': 3, 'rank': 4, 'reasons': ["key_phrase('crude futures')がdisplay_phraseと一致せず、source_span('futures')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 3, 'rank': 4, 'reasons': ["key_phrase('crude futures')がdisplay_phraseと一致せず、source_span('futures')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=[]
- hormuz_adv_M2P0 run2: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 4, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'どちらもこの記事では、上昇した原油価格が一時的に下がる動きを表しています。構文は「give back + 目的語」と自動詞的な「pull back」で異なりますが、意味と記事内の役割は実質的に重なります。'}] person_items=[]
- hormuz_adv_M2P3 run1: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 1, 'rank_b': 2, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'どちらもこの文脈では、いったん上がった原油価格が一時的に下がることを表しています。前者は上昇分を返す表現、後者は値が引き下がる表現で構文上の学習価値は異なりますが、記事内での役割はほぼ同じです。'}] person_items=[]
- hormuz_std_M0P0 run2: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 2, 'rank_b': 3, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'give back some gainsもpull backも、ここでは原油価格が上昇分を一時的に失う動きを表し、使用場面と記事内の役割が重なります。一方、前者は「値上がり分を返す」という他動詞的な型、後者は「価格が後退する」という自動詞的な型で、構文上の学習価値は異なります。'}] person_items=[]
- hormuz_std_M0P0 run3: canon=CANONICALIZATION_PASS reasons=[[]] red=REDUNDANCY_NG dup=[{'rank_a': 2, 'rank_b': 5, 'meaning_overlap': 'FAIL', 'usage_context_overlap': 'FAIL', 'grammatical_teaching_value_overlap': 'PASS', 'conceptual_role_overlap': 'FAIL', 'reasoning': 'どちらも発表後に原油価格がいったん下がり、上昇分の一部を失った同じ動きを述べています。一方、give back some gainsは目的語を取る表現、pull backはこの文では自動詞的な表現で、構文上の学習価値は異なります。'}] person_items=[]
- meta_adv_M0P0 run1: canon=CANONICALIZATION_INVALID reasons=[[{'index': 4, 'rank': 5, 'reasons': ["key_phrase('no way to know')がdisplay_phraseと一致せず、source_span('no way')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 4, 'rank': 5, 'reasons': ["key_phrase('no way to know')がdisplay_phraseと一致せず、source_span('no way')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=[]
- meta_std_M0P0 run3: canon=CANONICALIZATION_INVALID reasons=[[{'index': 2, 'rank': 3, 'reasons': ["key_phrase('on the other end')がdisplay_phraseと一致せず、source_span('other end')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}], [{'index': 2, 'rank': 3, 'reasons': ["key_phrase('the other end')がdisplay_phraseと一致せず、source_span('other end')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)"]}]] red=None dup=None person_items=[]
