# ============================================================
# er111_ukus_trial_cases_01.py -- ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り UKUS 委任_02 の検証ケース(データのみ。DEV/Trial専用)。
# V1 正常系 / V2 異常系 / V3 境界。test(er111_ukus_spelling_trial_01_test_01.py)と評価script(er111_ukus_trial_eval_01.py)が共用する。
# ============================================================
CARRIER = "She said the {w} was very important to them."

# ---- V1: 代表的な英米対(UK, US)。(UK, US, クラス)。AMB対(一方向)は V1_AMB に分ける。
V1_PAIRS = [
    # -ise/-ize
    ("organise", "organize", "ise"), ("realise", "realize", "ise"), ("recognise", "recognize", "ise"), ("apologise", "apologize", "ise"),
    ("analyse", "analyze", "ise"), ("criticise", "criticize", "ise"), ("specialise", "specialize", "ise"), ("authorise", "authorize", "ise"),
    ("civilisation", "civilization", "ise"), ("organisation", "organization", "ise"), ("summarise", "summarize", "ise"), ("emphasise", "emphasize", "ise"),
    ("modernised", "modernized", "ise"), ("capitalise", "capitalize", "ise"),
    # -our/-or
    ("colour", "color", "our"), ("favour", "favor", "our"), ("honour", "honor", "our"), ("neighbour", "neighbor", "our"), ("behaviour", "behavior", "our"),
    ("flavour", "flavor", "our"), ("labour", "labor", "our"), ("humour", "humor", "our"), ("harbour", "harbor", "our"), ("rumour", "rumor", "our"),
    ("saviour", "savior", "our"), ("vapour", "vapor", "our"), ("endeavour", "endeavor", "our"), ("colourful", "colorful", "our"), ("favourite", "favorite", "our"),
    # -re/-er
    ("centre", "center", "re"), ("theatre", "theater", "re"), ("litre", "liter", "re"), ("fibre", "fiber", "re"), ("kilometre", "kilometer", "re"),
    ("calibre", "caliber", "re"), ("sombre", "somber", "re"), ("lustre", "luster", "re"),
    # -ll-/-l-
    ("travelled", "traveled", "ll"), ("cancelled", "canceled", "ll"), ("labelled", "labeled", "ll"), ("modelling", "modeling", "ll"), ("jewellery", "jewelry", "ll"),
    ("counsellor", "counselor", "ll"), ("fulfil", "fulfill", "ll"), ("enrol", "enroll", "ll"), ("skilful", "skillful", "ll"), ("signalling", "signaling", "ll"),
    # -ogue / -ence
    ("catalogue", "catalog", "ogue"), ("defence", "defense", "ence"), ("offence", "offense", "ence"), ("pretence", "pretense", "ence"),
    # ae/oe
    ("paediatric", "pediatric", "ae"), ("encyclopaedia", "encyclopedia", "ae"), ("oestrogen", "estrogen", "ae"), ("manoeuvre", "maneuver", "ae"),
    ("anaemia", "anemia", "ae"), ("haemoglobin", "hemoglobin", "ae"), ("foetus", "fetus", "ae"),
    # 不規則
    ("speciality", "specialty", "irr"), ("aluminium", "aluminum", "irr"), ("grey", "gray", "irr"), ("mould", "mold", "irr"), ("plough", "plow", "irr"),
    ("pyjamas", "pajamas", "irr"), ("sceptic", "skeptic", "irr"), ("aeroplane", "airplane", "irr"), ("ageing", "aging", "irr"), ("judgement", "judgment", "irr"),
    ("acknowledgement", "acknowledgment", "irr"), ("artefact", "artifact", "irr"), ("moustache", "mustache", "irr"), ("sulphur", "sulfur", "irr"),
    ("learnt", "learned", "irr"), ("spilt", "spilled", "irr"), ("enquire", "inquire", "irr"), ("axe", "ax", "irr"), ("cosy", "cozy", "irr"),
    ("storey", "story", "irr"), ("tonne", "ton", "irr"),
]
# AMB(用法依存)=canonical=UK形 -> ASR=US形 のみ許可。逆方向は意図的に非同値(ベースラインが既にPASSなら可)。
V1_AMB = [
    ("licence", "license"), ("practise", "practice"), ("programme", "program"), ("tyre", "tire"), ("kerb", "curb"), ("cheque", "check"),
    ("metre", "meter"), ("analogue", "analog"), ("whisky", "whiskey"), ("flyer", "flier"), ("dependant", "dependent"),
]
# 活用・所有・ハイフン複合 (canonical, asr, 期待=True)
V1_FORMS = [
    ("The neighbour's dog barked.", "The neighbor's dog barked."), ("Both neighbours agreed.", "Both neighbors agreed."),
    ("Her jewellery-making kit arrived.", "Her jewelry-making kit arrived."), ("He is colour-blind.", "He is color-blind."),
    ("The organisation's staff left.", "The organization's staff left."), ("The colours are bright.", "The colors are bright."),
    ("They were behaving with great humour.", "They were behaving with great humor."), ("The theatres were closed.", "The theaters were closed."),
    ("The labourers' tools were old.", "The laborers' tools were old."), ("She is the manager of a speciality shop.", "She is the manager of a specialty shop."),
    ("It was a fanciful speciality-coffee bar.", "It was a fanciful specialty-coffee bar."),
    ("Inventing convincing stories at a moment's notice was Vera's speciality.", "Inventing convincing stories at a moment's notice was Vera's specialty."),
]

# ---- V2: 異常系 (cw, aw)。意味/語義/発音が異なる対。新規PASSしてはならない(ベースラインがPASSの同音語は本層の責任外として別表記録)。
V2_PAIRS = [
    ("advice", "advise"), ("ensure", "insure"), ("complement", "compliment"), ("principal", "principle"), ("stationary", "stationery"),
    ("affect", "effect"), ("discreet", "discrete"), ("canon", "cannon"), ("device", "devise"), ("prophecy", "prophesy"), ("practical", "practise"),
    ("specialty", "special"), ("speciality", "specially"), ("colour", "collar"), ("grey", "great"), ("centre", "central"), ("hour", "our"), ("four", "for"),
    ("pour", "poor"), ("tour", "tore"), ("flour", "floor"), ("story", "stir"), ("program", "progress"), ("jewellery", "jewel"), ("cheque", "cheek"),
    ("licence", "lioness"), ("honour", "hammer"), ("organise", "organs"), ("realise", "relies"), ("analyse", "analysis"), ("storey", "stir"),
    ("metre", "mother"), ("tire", "tyre"), ("labour", "lab"), ("favour", "fever"), ("theatre", "theme"), ("neighbour", "neighbourhood"),
    ("mould", "mild"), ("plough", "plot"), ("sulphur", "sulk"), ("axe", "ask"), ("catalogue", "category"), ("defence", "deference"),
    ("aluminium", "alumni"), ("grey", "grew"), ("enquire", "require"), ("mum", "mom"), ("mom", "mum"), ("learnt", "learn"), ("recognise", "reckon"),
]
# 同一語の変異綴り(意味差なし)で新規PASSしてよい対(誤PASSではない): 評価時は『正当』として別集計
V2_LEGIT_NEW = {("surprise", "surprize"), ("surprize", "surprise")}
V2_EXTRA_PAIRS = [("surprise", "surprize"), ("surprize", "surprise")]

# V2追加(OF-10): 文頭大文字一般語・所有格・ハイフン複合語。(canonical, asr, 期待verdict) True=PASS False=NG
V2_CASES = [
    ("Mum said hello to us.", "Mom said hello to us.", False),                     # mum->mom: OF-04除外(発音が違う別語義)
    ("Speciality coffee is popular here.", "Specialty coffee is popular here.", True),    # 文頭大文字の一般語(次は小文字)
    ("Speciality Coffee Roasters opened here.", "Specialty Coffee Roasters opened here.", False),  # 文頭だが次も大文字=固有名詞らしい
    ("The speciality's price rose.", "The specialty's price rose.", True),
    ("The jewellery-making class began.", "The jewelry-making class began.", True),
    ("The jewellery-making class began.", "The jewel-making class began.", False),
    ("He bought a tyre for it.", "He bought a tire for it.", True),               # AMB uk->us
    ("He bought a tire for it.", "He bought a tyre for it.", False),               # AMB us->uk は不可
    ("They will advise us soon.", "They will advice us soon.", False),
]

# ---- V3: 境界。(canonical, asr, 期待)
V3_CASES = [
    # 固有名詞(文中大文字)はUKUSで同値化しない(ベースライン非同値の対で検査)
    ("She joined the Speciality Foods Group in May.", "She joined the Specialty Foods Group in May.", False),
    ("He visited Aluminium City last year.", "He visited Aluminum City last year.", False),
    ("The Jewellery Quarter is famous.", "The Jewelry Quarter is famous.", False),
    ("He lives near Rockefeller Center today.", "He lives near Rockefeller Centre today.", True),   # ベースライン既PASS(同音)=維持
    ("We saw Earl Grey in the shop.", "We saw Earl Gray in the shop.", True),                     # ベースライン既PASS(同音)=維持
    ("The Labour Party won the vote.", "The Labor Party won the vote.", True),                    # 同音のため既PASS
    ("He joined the Aluminum Company of America.", "He joined the Aluminium Company of America.", False),
    ("Learnt Academy is in Leeds.", "Learned Academy is in Leeds.", False),
    # 綴り差+実誤読が同居 -> NG維持
    ("The speciality is cooking.", "The specialty is cooling.", False),
    ("Her jewellery was lost.", "His jewelry was lost.", False),
    ("The colour and the flavour were great.", "The color and the flavour were poor.", False),
    ("We organise the theatre tour.", "We organize the theatre tore.", False),
    # 語の欠落・付加
    ("It was her speciality.", "It was specialty.", False),
    ("It was her speciality.", "It was her very specialty.", False),
    ("The jewellery shop opened.", "The jewelry opened.", False),
    # 同音語置換(UKUS無関係)
    ("They went to the colour fair.", "They went to the collar fair.", False),
    # 数/記号spanを含む文に綴り差
    ("The speciality costs 3 pounds.", "The specialty costs 3 pounds.", True),
    ("The speciality costs 3 pounds.", "The specialty costs 4 pounds.", False),
    ("The speciality costs 30%.", "The specialty costs 30 percent.", True),
    # 既知の限界(fail-closed): 語数が違うspan(ハイフン複合<->分かち書き)+綴り差の同居は本層で同値化しない
    ("Her jewellery-making kit arrived.", "Her jewelry making kit arrived.", False),
    # 同語反復文の整列
    ("The speciality is a speciality of the house.", "The specialty is a specialty of the house.", True),
    ("The speciality is a speciality of the house.", "The specialty is a speciality of the house.", True),
    ("The speciality is a speciality of the house.", "The specialty is a specialty of the home.", False),
    # 文末・大文字・複数位置
    ("The aluminium tin and the jewellery box.", "The aluminum tin and the jewelry box.", True),
    ("ALUMINIUM prices rose.", "ALUMINUM prices rose.", False),
    ("They trained at the Centre for Defence.", "They trained at the Center for Defense.", True),
    # 長い文でUKUS2か所+正しい他語
    ("Our neighbour's speciality is baking, and the neighbours love her colourful cakes.", "Our neighbor's specialty is baking, and the neighbors love her colorful cakes.", True),
    # US形canonical -> UK形ASR (逆方向)
    ("The specialty is hers.", "The speciality is hers.", True),
    ("Their jewelry is old.", "Their jewellery is old.", True),
]
