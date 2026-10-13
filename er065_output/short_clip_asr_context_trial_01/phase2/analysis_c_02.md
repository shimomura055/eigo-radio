## C-1. Melos 7 take別: Fallback方式ごとの『救済(exact一致 or 現行PASS)』と『音韻説明可(Trial)』

F0=単独1回(OpenAI rep1) / F1=同条件繰返し(単独OpenAI rep1-2のどちらかexact) / F2=前後音声付き(OpenAI 全文脈recipeのいずれかでexact) / F3=別engine単独(Azure or whisper exactが1回以上) / F4=単独転写のうち音韻説明可(FUSION)の割合(OpenAI+Azure+whisper単独) 

| take | prod判定ラベル(委任_01) | F0 exact | F1 繰返し exact | F2 文脈付き exact(回数/観測) | F3 別engine exact | F4 単独転写が連結発音で説明可 | F4で説明不能の転写例 | 単独転写の内訳(engine:出力) |
|---|---|---|---|---|---|---|---|---|
| a2_att1 | prod_ok | N | N | 4/46 | Y | 6/6 (100%) | [] | azu:melos said; ope:mello said; whi:mello said; whi:mellow said |
| a2_att2 | prod_ng | N | N | 1/46 | N | 6/6 (100%) | [] | azu:mellow said; ope:mello said; whi:mello said; whi:mellow said |
| a2_att3 | prod_ok | N | N | 3/46 | N | 6/6 (100%) | [] | azu:melo said; ope:mello said; whi:mellow said; whi:melo said |
| a2_att4 | prod_ng | N | N | 5/46 | N | 2/6 (33%) | ['mallow said', 'mellis said'] | azu:mallow said; ope:mellis said; whi:mellow said; whi:melo said |
| a2_att5 | prod_ng | N | N | 3/46 | N | 4/6 (67%) | ['melloset', 'mellowset'] | azu:melo said; ope:melloset; ope:mellowset; whi:mellow said; whi:melo said |
| a2_att6 | prod_ng | N | N | 17/45 | N | 3/6 (50%) | ['mellow set', 'meloset'] | azu:mellow said; ope:meloset; whi:mellow set; whi:melo said |
| b1b_att1 | prod_ng | N | N | 0/23 | N | 5/5 (100%) | [] | azu:mellow said; ope:mello said; whi:mello said; whi:mellow said |

## C-2. NG take(att2,4,5,6, b1b_att1の5本; Production判定でNGだったtake)全体の救済率

観測単位=(take, engine, rep, recipe)。F4は音韻説明可(PHON_EXPLAINED_FUSION)、F4'はVOICING弱説明、NOTは不能。

| 方式 | 対象観測 | 救済(exactまたは現行PASS) | 音韻説明可(FUSION) | 音韻弱説明(VOICING) | 説明不能(NOT_EXPLAINED) | 音韻証拠なし(OOV等) | 同音綴り違い(HOMOPHONE) |
|---|---|---|---|---|---|---|---|
| F0/F1 単独OpenAI(全rep) | 9 | 0/9 (0%) | 3/9 (33%) | 4/9 (44%) | 2/9 (22%) | 0/9 (0%) | 0/9 (0%) |
| F3 単独Azure+Phrase List | 10 | 2/10 (20%) | 8/10 (80%) | 0/10 (0%) | 2/10 (20%) | 0/10 (0%) | 0/10 (0%) |
| F3 単独whisper-small | 5 | 3/5 (60%) | 5/5 (100%) | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| F3 単独whisper-medium | 5 | 0/5 (0%) | 4/5 (80%) | 1/5 (20%) | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| F2 文脈付きOpenAI(全recipe) | 206 | 60/206 (29%) | 118/206 (57%) | 10/206 (5%) | 33/206 (16%) | 0/206 (0%) | 6/206 (3%) |
| F2 文脈付きAzure | 29 | 9/29 (31%) | 25/29 (86%) | 1/29 (3%) | 3/29 (10%) | 0/29 (0%) | 0/29 (0%) |

## C-3. 既知欠陥・NG proxy反例に対する音韻判定の誤説明(= 欠陥を『連結発音で説明可』と誤る件数。独立証拠なしでも『許容』にはならないが、HR候補に載る件数)

| 群 | engine | 観測 | 現行PASS | FUSION(誤説明候補) | VOICING | HOMOPHONE | NOT_EXPLAINED | 備考 |
|---|---|---|---|---|---|---|---|---|
| synthetic | openai | 125 | 73 | 20 | 0 | 6 | 27 | |
| synthetic | azure | 5 | 0 | 3 | 0 | 0 | 2 | |
| synthetic | whisper-small | 98 | 74 | 12 | 0 | 5 | 24 | |
| natural_ng | openai | 68 | 22 | 0 | 0 | 0 | 37 | |
| natural_ng | azure | 11 | 7 | 0 | 0 | 0 | 3 | |
| natural_ng | whisper-small | 47 | 23 | 0 | 0 | 0 | 14 | |

FUSION/VOICINGと判定された反例観測の全列挙(canonical → region):

- synthetic/syn_B1_trunc140 [azure] `Melos said.` → `mellow said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc220 [azure] `Melos said.` → `mellow said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc70 [azure] `Melos said.` → `mellow said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc70 [openai] `Melos said.` → `mello said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc140 [openai] `Melos said.` → `mello said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc220 [openai] `Melos said.` → `mello said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc140 [openai] `Melos said.` → `melo said` : PHON_EXPLAINED_FUSION
- synthetic/ctl_B1_intact [openai] `Melos said.` → `mello said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc70 [whisper-small] `Melos said.` → `melo said` : PHON_EXPLAINED_FUSION
- synthetic/syn_B1_trunc220 [whisper-small] `Melos said.` → `melo said` : PHON_EXPLAINED_FUSION
- synthetic/ctl_B1_intact [whisper-small] `Melos said.` → `melo said` : PHON_EXPLAINED_FUSION
- synthetic/ctl_B1_intact [whisper-small] `Melos said.` → `mellow said` : PHON_EXPLAINED_FUSION