## S. shortlist再現率(決定論、JPY0)  ex=exact件数/targets総数, ex|partial=exactまたはpartial件数
- N1 (std, negative_control): V0: ex 1/5 (ex|part 1), n=21, resv=[], ovf=[] / V1+d: ex 3/5 (ex|part 3), n=23, resv=['bit her tongue', 'opened his eyes'], ovf=[] / V3: ex 4/5 (ex|part 4), n=24, resv=['bit her tongue', 'lost her keys', 'opened his eyes'], ovf=['led his class', 'gave her some'] / V2_run1: ex 3/5 (ex|part 3), n=23, resv=['bit her tongue', 'opened his eyes'], ovf=[] / V2_run2: ex 3/5 (ex|part 3), n=23, resv=['bit her tongue', 'opened his eyes'], ovf=[] / V2_run3: ex 3/5 (ex|part 3), n=23, resv=['bit her tongue', 'opened his eyes'], ovf=[]
- D6 (adv, negative_control): V0: ex 0/0 (ex|part 0), n=20, resv=[], ovf=[] / V1+d: ex 0/0 (ex|part 0), n=20, resv=[], ovf=[] / V3: ex 0/0 (ex|part 0), n=20, resv=[], ovf=[] / V2_run1: ex 0/0 (ex|part 0), n=20, resv=[], ovf=[] / V2_run2: ex 0/0 (ex|part 0), n=20, resv=[], ovf=[] / V2_run3: ex 0/0 (ex|part 0), n=20, resv=[], ovf=[]
- D2 (std, positive): V0: ex 2/6 (ex|part 3), n=20, resv=[], ovf=[] / V1+d: ex 5/6 (ex|part 5), n=23, resv=['lost his temper', 'pulling my leg', 'bit her tongue'], ovf=['change her mind'] / V3: ex 5/6 (ex|part 5), n=23, resv=['lost his temper', 'pulling my leg', 'bit her tongue'], ovf=['change her mind'] / V2_run1: ex 5/6 (ex|part 5), n=23, resv=['lost his temper', 'pulling my leg', 'bit her tongue'], ovf=['change her mind'] / V2_run2: ex 5/6 (ex|part 5), n=23, resv=['lost his temper', 'pulling my leg', 'bit her tongue'], ovf=['change her mind']
- D5 (std, negative_control): V0: ex 0/0 (ex|part 0), n=21, resv=[], ovf=[] / V1+d: ex 0/0 (ex|part 0), n=21, resv=[], ovf=[] / V3: ex 0/0 (ex|part 0), n=21, resv=[], ovf=[] / V2_run1: ex 0/0 (ex|part 0), n=21, resv=[], ovf=[] / V2_run2: ex 0/0 (ex|part 0), n=21, resv=[], ovf=[] / V2_run3: ex 0/0 (ex|part 0), n=21, resv=[], ovf=[]
- D3 (adv, positive): V0: ex 2/6 (ex|part 2), n=20, resv=[], ovf=[] / V1+d: ex 3/6 (ex|part 3), n=21, resv=['holding its breath'], ovf=[] / V3: ex 3/6 (ex|part 3), n=21, resv=['holding its breath'], ovf=[] / V2_run1: ex 4/6 (ex|part 5), n=23, resv=['began to whisper', 'taken out against the future', 'holding its breath'], ovf=[] / V2_run2: ex 3/6 (ex|part 3), n=21, resv=['holding its breath'], ovf=[]
- R3 (adv, negative_control): V0: ex 0/1 (ex|part 0), n=20, resv=[], ovf=[] / V1+d: ex 1/1 (ex|part 1), n=21, resv=['open your eyes'], ovf=[] / V3: ex 1/1 (ex|part 1), n=22, resv=['Before Your Alarm', 'open your eyes'], ovf=[] / V2_run1: ex 1/1 (ex|part 1), n=22, resv=['gets the first word', 'open your eyes'], ovf=[] / V2_run2: ex 1/1 (ex|part 1), n=23, resv=['lie less in', 'gets the first word', 'open your eyes'], ovf=[] / V2_run3: ex 1/1 (ex|part 1), n=23, resv=['sleep inertia', 'gets the first word', 'open your eyes'], ovf=[]
- D4 (adv, regression_watch): V0: ex 4/8 (ex|part 4), n=27, resv=[], ovf=[] / V1+d: ex 4/8 (ex|part 4), n=27, resv=[], ovf=[] / V3: ex 4/8 (ex|part 4), n=28, resv=['rated their own'], ovf=[] / V2_run1: ex 4/8 (ex|part 4), n=27, resv=[], ovf=[] / V2_run2: ex 4/8 (ex|part 4), n=27, resv=[], ovf=[]
- R1 (adv, shortlist_only): V0: ex 0/1 (ex|part 0), n=20, resv=[], ovf=[] / V1+d: ex 1/1 (ex|part 1), n=21, resv=['changes my mind'], ovf=[] / V3: ex 0/1 (ex|part 0), n=23, resv=['change their deeper', 'outside my usual', 'through my feed'], ovf=['changes my mind', 'understand their lives'] / V2_noLLM: ex 1/1 (ex|part 1), n=21, resv=['changes my mind'], ovf=[]
- R2 (std, shortlist_only): V0: ex 0/1 (ex|part 0), n=23, resv=[], ovf=[] / V1+d: ex 1/1 (ex|part 1), n=24, resv=['made his mark'], ovf=[] / V3: ex 1/1 (ex|part 1), n=25, resv=['made his mark', 'season his first'], ovf=[] / V2_noLLM: ex 1/1 (ex|part 1), n=24, resv=['made his mark'], ovf=[]

## E. 抽出(extractor v3)
- N1: raw=[0, 0, 0] accepted=[0, 0, 0] (mean 0.00) subj=[0, 0, 0]
    run1: raw=[] -> acc=[] rej=[] dup=[] cont=[] reserved=['bit her tongue', 'opened his eyes'] ovf=[]
    run2: raw=[] -> acc=[] rej=[] dup=[] cont=[] reserved=['bit her tongue', 'opened his eyes'] ovf=[]
    run3: raw=[] -> acc=[] rej=[] dup=[] cont=[] reserved=['bit her tongue', 'opened his eyes'] ovf=[]
- D6: raw=[1, 1, 1] accepted=[0, 0, 0] (mean 0.00) subj=[0, 0, 0]
    run1: raw=[(1, 'make up', 'semi')] -> acc=[] rej=[] dup=['make up'] cont=[] reserved=[] ovf=[]
    run2: raw=[(1, 'make up', 'opaque')] -> acc=[] rej=[] dup=['make up'] cont=[] reserved=[] ovf=[]
    run3: raw=[(1, 'make up 41%', 'semi')] -> acc=[] rej=[] dup=['make up'] cont=[] reserved=[] ovf=[]
- D2: raw=[3, 3] accepted=[2, 2] (mean 2.00) subj=[0, 0]
    run1: raw=[(1, 'spill the beans', 'opaque'), (2, 'pulling my leg', 'opaque'), (3, 'bit her tongue', 'semi')] -> acc=['pulling my leg', 'bit her tongue'] rej=[] dup=['spill the beans'] cont=[] reserved=['lost his temper', 'pulling my leg', 'bit her tongue'] ovf=['change her mind']
    run2: raw=[(1, 'spill the beans', 'opaque'), (2, 'pulling my leg', 'opaque'), (3, 'bit her tongue', 'semi')] -> acc=['pulling my leg', 'bit her tongue'] rej=[] dup=['spill the beans'] cont=[] reserved=['lost his temper', 'pulling my leg', 'bit her tongue'] ovf=['change her mind']
- D5: raw=[0, 0, 0] accepted=[0, 0, 0] (mean 0.00) subj=[0, 0, 0]
    run1: raw=[] -> acc=[] rej=[] dup=[] cont=[] reserved=[] ovf=[]
    run2: raw=[] -> acc=[] rej=[] dup=[] cont=[] reserved=[] ovf=[]
    run3: raw=[] -> acc=[] rej=[] dup=[] cont=[] reserved=[] ovf=[]
- D3: raw=[3, 3] accepted=[2, 1] (mean 1.50) subj=[0, 0]
    run1: raw=[(1, 'shrugged off', 'opaque'), (2, 'taken out against the future', 'semi'), (3, 'began to whisper', 'semi')] -> acc=['taken out against the future', 'began to whisper'] rej=[] dup=['shrugged off'] cont=[] reserved=['began to whisper', 'taken out against the future', 'holding its breath'] ovf=[]
    run2: raw=[(1, 'holding its breath', 'opaque'), (2, 'shrugged off', 'semi'), (3, 'market is resting, not retreating', 'semi')] -> acc=['holding its breath'] rej=[('crosses_punctuation_or_format', 'is resting not retreating')] dup=['shrugged off'] cont=[] reserved=['holding its breath'] ovf=[]
- R3: raw=[3, 3, 3] accepted=[1, 2, 2] (mean 1.67) subj=[0, 0, 0]
    run1: raw=[(1, 'gets the first word', 'semi'), (2, 'under way', 'opaque'), (3, 'has read the clock', 'semi')] -> acc=['gets the first word'] rej=[('excluded_by_existing_gate', 'has read the clock')] dup=['under way'] cont=[] reserved=['gets the first word', 'open your eyes'] ovf=[]
    run2: raw=[(1, 'under way', 'opaque'), (2, 'lie less in', 'semi'), (3, 'gets the first word', 'semi')] -> acc=['lie less in', 'gets the first word'] rej=[] dup=['under way'] cont=[] reserved=['lie less in', 'gets the first word', 'open your eyes'] ovf=[]
    run3: raw=[(1, 'sleep inertia', 'opaque'), (2, 'under way', 'opaque'), (3, 'gets the first word', 'semi')] -> acc=['sleep inertia', 'gets the first word'] rej=[] dup=['under way'] cont=[] reserved=['sleep inertia', 'gets the first word', 'open your eyes'] ovf=[]
- D4: raw=[3, 3] accepted=[0, 0] (mean 0.00) subj=[0, 0]
    run1: raw=[(1, 'turned down the request', 'opaque'), (2, 'add up to', 'semi'), (3, 'sales picked up', 'semi')] -> acc=[] rej=[] dup=['turned down', 'add up to', 'picked up'] cont=[] reserved=[] ovf=[]
    run2: raw=[(1, 'turned down the request', 'opaque'), (2, 'add up to a clear winner', 'semi'), (3, 'sales picked up', 'semi')] -> acc=[] rej=[] dup=['turned down', 'add up to', 'picked up'] cont=[] reserved=[] ovf=[]
- 陰性対照(N1/D6/D5/R3) accepted平均/回 = 0.42 (runs 12, 基準<=1) / 記事別: N1 0.00, D6 0.00, D5 0.00, R3 1.67

## F. 最終選定(job単位)
- D2 V0 run1: ['keep an eye on', 'divide', 'take away', 'spill the beans', 'bike lane'] ev=[None, None, None, None, None] tgt ex 2/6 (ex|part 2) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.7988 t=89.45s
- D2 V2 run1: ["bite one's tongue", "pull someone's leg", "lose one's temper", 'spill the beans', 'bike lane'] ev=['placeholder_title', 'placeholder_title', 'placeholder_title', None, None] tgt ex 4/6 (ex|part 4) llm/ph=3 reserved=['lost his temper', 'pulling my leg', 'bit her tongue'] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.6485 t=76.52s
- D2 V2 run2: ["pull someone's leg", "bite one's tongue", "lose one's temper", 'spill the beans', 'bike lane'] ev=['placeholder_title', 'placeholder_title', 'placeholder_title', None, None] tgt ex 4/6 (ex|part 4) llm/ph=3 reserved=['lost his temper', 'pulling my leg', 'bit her tongue'] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.8184 t=89.36s
- D3 V0 run1: ['shrug off', 'under the surface', 'take out', 'different story', 'renter'] ev=[None, None, None, None, None] tgt ex 2/6 (ex|part 2) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=1.1187 t=135.14s
- D3 V2 run1: ['take out against the future', 'under the surface', "hold one's breath", 'shrug off', 'interest rate'] ev=['llm_noncompositional', None, 'placeholder_title', None, None] tgt ex 3/6 (ex|part 3) llm/ph=2 reserved=['began to whisper', 'taken out against the future', 'holding its breath'] red=None->None canon=['CANONICALIZATION_INVALID', 'CANONICALIZATION_INVALID'] srcmiss=[[]] cost=1.1911 t=128.13s
- D3 V2 run2: ["hold one's breath", 'shrug off', 'under the surface', 'interest rate', 'retreat'] ev=['placeholder_title', None, None, None, None] tgt ex 3/6 (ex|part 3) llm/ph=1 reserved=['holding its breath'] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.8334 t=102.82s
- D4 V0 run1: ['new schedule', 'add up to', 'figure out', 'pick up', 'teamwork'] ev=[None, None, None, None, None] tgt ex 3/8 (ex|part 3) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.7402 t=75.51s
- D4 V2 run1: ['add up to', 'pick up', 'fade', 'weak', 'new schedule'] ev=[None, None, None, None, None] tgt ex 2/8 (ex|part 2) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.9826 t=103.97s
- D4 V2 run2: ['add up to', 'pick up', 'fade', 'new schedule', 'teamwork'] ev=[None, None, None, None, None] tgt ex 2/8 (ex|part 2) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.7806 t=87.67s
- D5 V0 run1: ['walk away', 'community center', 'bus route', 'bus stop', 'next to'] ev=[None, None, None, None, None] tgt ex 0/0 (ex|part 0) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_INVALID', 'CANONICALIZATION_REVIEW_REQUIRED'] srcmiss=[[]] cost=1.4255 t=168.74s
- D5 V2 run1: ['new bus route', 'fifteen minutes', 'rider', 'nearest', 'community center'] ev=[None, None, None, None, None] tgt ex 0/0 (ex|part 0) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.8094 t=95.29s
- D5 V2 run2: ['bus route', 'walk away', 'fifteen minutes', 'community center', 'rider'] ev=[None, None, None, None, None] tgt ex 0/0 (ex|part 0) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_INVALID', 'CANONICALIZATION_REVIEW_REQUIRED'] srcmiss=[[]] cost=1.5142 t=186.26s
- D6 V0 run1: ['make up', 'installation costs', 'turn into', 'come from', 'coating'] ev=[None, None, None, None, None] tgt ex 0/0 (ex|part 0) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.8103 t=91.49s
- D6 V2 run1: ['make up', 'caution', 'installation costs', 'stack', 'humidity'] ev=[None, None, None, None, None] tgt ex 0/0 (ex|part 0) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.8171 t=94.39s
- D6 V2 run2: ['make up', 'permit', 'coating', 'stack', 'Installation costs'] ev=[None, None, None, None, None] tgt ex 0/0 (ex|part 0) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.7497 t=92.52s
- N1 V0 run1: ['freeze', 'break the ice', 'spill', 'come down', 'school pond'] ev=[None, None, None, None, None] tgt ex 1/5 (ex|part 1) llm/ph=0 reserved=[] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.6986 t=78.39s
- N1 V2 run1: ['freeze', 'break the ice', 'centimeter', 'spill', 'school pond'] ev=[None, None, None, None, None] tgt ex 1/5 (ex|part 1) llm/ph=0 reserved=['bit her tongue', 'opened his eyes'] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.7874 t=103.12s
- N1 V2 run2: ['freeze', 'break the ice', 'centimeter', 'school pond', 'spill'] ev=[None, None, None, None, None] tgt ex 1/5 (ex|part 1) llm/ph=0 reserved=['bit her tongue', 'opened his eyes'] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.77 t=90.49s
- R3 V2 run1: ['get the first word', 'sleep inertia', 'minute-perfect', 'slow-wave sleep', 'time-isolation'] ev=['llm_noncompositional', None, None, None, None] tgt ex 0/1 (ex|part 0) llm/ph=1 reserved=['gets the first word', 'open your eyes'] red=REDUNDANCY_PASS->REDUNDANCY_PASS canon=['CANONICALIZATION_PASS'] srcmiss=[[]] cost=0.923 t=96.93s

## J. 受入基準の判定
- 陰性対照(最終5件のllm/placeholder由来件数、run単位): {'N1': [0, 0], 'D6': [0, 0], 'D5': [0, 0], 'R3': [1]} -> FAIL
- D2 shortlist exact: V0 2/6, V1+d 5/6, V2_run1 5/6, V2_run2 5/6
- D2 final (>= 2件, partial可): V2 [4, 4] V0 [2]
- D3 final (>= 2件, partial可): V2 [3, 3] V0 [2]
- D4 final (>= 2件, partial可): V2 [2, 2] V0 [3]
- D3 shortlist V2_run1: b1only回復 ['d3_loan', 'd3_whisper']
- D3 shortlist V2_run2: b1only回復 []
- D4 V0 CD件数 = 2
- D4 V2 CD件数 = 2
- D4 V2 CD件数 = 2
