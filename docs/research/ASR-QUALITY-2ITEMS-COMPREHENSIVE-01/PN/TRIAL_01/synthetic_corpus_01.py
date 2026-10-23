# -*- coding: utf-8 -*-
"""D4 合成コーパス(カテゴリ person/place/organization/brand_product/work_title × 位置[文頭/引用直後/呼びかけ/所有格/複合名/イニシャル/ハイフン/非ASCII] ×
語彙性[CMU収録の非一般語=Bertie型 / OOV / 一般語同形=Bill,Mark,Rose,Will]) と負例(偽候補・題名中の低頻度一般語)。
gold は構成上確定(人手adjudication不要)。expect:
  "evidence"        表が証拠を付けるべき(recall対象)。
  "blocked_general" 全tokenが一般語。証拠を付けない(R_GENERAL_WORD維持。Iran/Mark型)
  "oov_only"        work_title/other_named: CMU未収録tokenのみ証拠可(それ以外のtokenに証拠を付けない)
neg: 本文中の通常語(固有名詞ではない)。表に証拠付与されたら誤り(SC-3)。"""

P = []


def add(id_, text, gold, neg=()):
    P.append({"id": id_, "text": text, "gold": [dict(zip(("surface", "category", "expect"), g)) for g in gold], "neg": list(neg)})


# --- Bertie型: CMU収録の人名が文頭/引用直後/呼びかけにだけ現れる(歌詞・台詞)
add("fic_01", "Nigel carried the lamp up the stairs. \"Tilly, why do you hide?\" he called. Tilly did not answer. Hattie laughed from the kitchen, "
    "and Winnie, her little sister, ran past with a spoon. Percy waited at the gate.",
    [("Nigel", "person", "evidence"), ("Tilly", "person", "evidence"), ("Hattie", "person", "evidence"), ("Winnie", "person", "evidence"), ("Percy", "person", "evidence")])
add("fic_02", "Ronnie sang an old song in the garden: 'Dora, Dora, where have you gone?' Dora was not there. Wendell came out of the shed and said nothing. "
    "Ethel, the neighbor, watched the whole thing from her window.",
    [("Ronnie", "person", "evidence"), ("Dora", "person", "evidence"), ("Wendell", "person", "evidence"), ("Ethel", "person", "evidence")])
add("fic_03", "Cecil opened the letter slowly. Mabel had written it, and Gwen had signed it too. 'Oswald will know what to do,' Cecil whispered. "
    "Agatha, standing by the door, did not move. Hugo was already gone.",
    [("Cecil", "person", "evidence"), ("Mabel", "person", "evidence"), ("Gwen", "person", "evidence"), ("Oswald", "person", "evidence"),
     ("Agatha", "person", "evidence"), ("Hugo", "person", "evidence")])
# --- 一般語同形の人名(Bill/Mark/Rose/Will): 証拠を付けない(ブロック維持)
add("gen_01", "Mark told Rose that Will had paid the bill. Bill laughed and said he would mark the date. Rose said the rose in the vase was fading.",
    [("Mark", "person", "blocked_general"), ("Rose", "person", "blocked_general"), ("Will", "person", "blocked_general"), ("Bill", "person", "blocked_general")],
    neg=["bill", "mark", "rose", "will"])
# --- 複数語名(姓が一般語/名が一般語)とイニシャル
add("multi_01", "Stephen Reicher studies crowds at the University of St Andrews. Kristie Tse runs a small lab, and L. Mimoun joined last spring. "
    "Reicher says the results are clear. Mimoun disagrees.",
    [("Stephen Reicher", "person", "evidence"), ("University of St Andrews", "organization", "evidence"), ("Kristie Tse", "person", "evidence"), ("L. Mimoun", "person", "evidence")],
    neg=["says", "studies"])
add("multi_02", "Will Smith met Mark Rowan at the Cardiff Museum. Nora Jean-Baptiste joined them later, and Felix O'Connell brought the maps.",
    [("Will Smith", "person", "blocked_general"), ("Mark Rowan", "person", "evidence"), ("Cardiff Museum", "organization", "evidence"),
     ("Nora Jean-Baptiste", "person", "evidence"), ("Felix O'Connell", "person", "evidence")], neg=["will", "mark"])
# --- 地名(CMU収録の非一般語 / OOV / 一般語)
add("place_01", "Leeds was cold that week. Reykjavik was colder. The train from Cardiff to Perth takes a long time, and Nairobi feels far away. "
    "Tbilisi is quiet in winter. Malmö has a famous bridge. Iran, Japan and France were also mentioned.",
    [("Leeds", "place", "evidence"), ("Reykjavik", "place", "evidence"), ("Cardiff", "place", "evidence"), ("Perth", "place", "evidence"), ("Nairobi", "place", "evidence"),
     ("Tbilisi", "place", "evidence"), ("Malmö", "place", "evidence"), ("Iran", "place", "blocked_general"), ("Japan", "place", "blocked_general"), ("France", "place", "blocked_general")])
# --- 組織名
add("org_01", "Oxfam said food prices rose again. Unicef and Greenpeace agreed. Reuters reported the numbers, and Bisnow added a local angle. "
    "The Brookings Institution published a long study. Unesco declined to comment.",
    [("Oxfam", "organization", "evidence"), ("Unicef", "organization", "evidence"), ("Greenpeace", "organization", "evidence"), ("Reuters", "organization", "evidence"),
     ("Bisnow", "organization", "evidence"), ("Brookings Institution", "organization", "evidence"), ("Unesco", "organization", "evidence")])
# --- ブランド/商品
add("brand_01", "Vogue named the coat of the year. Zara copied it within a week. Dyson launched a new dryer, and Gucci stayed quiet. "
    "Lego built a bridge from toy bricks. Fitbit announced a new band, and Nokia reissued an old phone.",
    [("Vogue", "brand_product", "evidence"), ("Zara", "brand_product", "evidence"), ("Dyson", "brand_product", "evidence"), ("Gucci", "brand_product", "evidence"),
     ("Lego", "brand_product", "evidence"), ("Fitbit", "brand_product", "evidence"), ("Nokia", "brand_product", "evidence")])
# --- 作品名(CMU収録の低頻度一般語を含む題名: petal/crimson 等に証拠を付けない = OF-PN2-04)
add("work_01", "She was reading The Crimson Petal and the White on the train. Later she watched Middlemarch on television, then a film called Moby Dick. "
    "A petal fell from the vase. The pedal on the old bike was loose.",
    [("The Crimson Petal and the White", "work_title", "oov_only"), ("Middlemarch", "work_title", "oov_only"), ("Moby Dick", "work_title", "oov_only")],
    neg=["petal", "pedal", "crimson"])
add("work_02", "The slogan Share the journey, not the noise appeared on every poster. The report, called Muddy Waters Ahead, was long. "
    "The farther they walked, the muddier the road became.",
    [("Share the journey, not the noise", "work_title", "oov_only"), ("Muddy Waters Ahead", "work_title", "oov_only")], neg=["journey", "noise", "muddy", "waters", "farther"])
# --- 負例: 文頭/見出しの通常語(固有名詞ではない)
add("neg_01", "Inventing new tools takes time. Canceling the trip was hard. Roasting beans at home is easy. Unwanted noise filled the room. "
    "Fats and oils are part of the story. Withdrawn from the race, he went home. Muddy boots stood by the door.",
    [], neg=["inventing", "canceling", "roasting", "unwanted", "fats", "withdrawn", "muddy"])
# --- 所有格/ハイフン/呼びかけ/非ASCII
add("pos_01", "Bertie's umbrella was red. 'Bertie, wait!' she cried. Elsie's brother and Lottie's cat were there. Jean-Luc greeted Zoë warmly. "
    "'Beatrice,' said Clara, 'come in.'",
    [("Bertie", "person", "evidence"), ("Elsie", "person", "evidence"), ("Lottie", "person", "evidence"), ("Jean-Luc", "person", "evidence"),
     ("Zoë", "person", "evidence"), ("Beatrice", "person", "evidence"), ("Clara", "person", "evidence")])
add("mix_01", "Reuters said Hanshin won 8-1 in Osaka. Altuzarra and Toteme showed new bags in Milan, while ELLE and Vogue covered Kyoto Fashion Week. "
    "Alta Zara is a different brand. Khaite stayed in New York.",
    [("Reuters", "organization", "evidence"), ("Hanshin", "organization", "evidence"), ("Osaka", "place", "evidence"), ("Altuzarra", "brand_product", "evidence"),
     ("Toteme", "brand_product", "evidence"), ("Milan", "place", "evidence"), ("ELLE", "brand_product", "evidence"), ("Vogue", "brand_product", "evidence"),
     ("Kyoto Fashion Week", "other_named", "oov_only"), ("Khaite", "brand_product", "evidence"), ("New York", "place", "blocked_general"),
     ("Alta Zara", "brand_product", "evidence")])
add("mix_02", "Melos ran through the night. Selinuntius waited in the city of Syracuse. Dionysius laughed. Phininius, an old friend, held the rope. "
    "Melos did not stop until he reached the gate.",
    [("Melos", "person", "evidence"), ("Selinuntius", "person", "evidence"), ("Syracuse", "place", "evidence"), ("Dionysius", "person", "evidence"),
     ("Phininius", "person", "evidence")])
add("mix_03", "Framton Nuttel visited the country house. Mrs. Sappleton greeted him, and her niece Vera told a long story. 'Vera, is that true?' asked Framton. "
    "The hunters returned from Devon at dusk.",
    [("Framton Nuttel", "person", "evidence"), ("Sappleton", "person", "evidence"), ("Vera", "person", "evidence"), ("Devon", "place", "evidence")])
add("mix_04", "Tesla and SpaceX are both run by Musk. Broadcom reported earnings on Thursday. Meta released Muse in the United States. "
    "Ig Nobel prizes were handed out in Boston. The Typhoon jets flew from Riyadh to Yemen.",
    [("Tesla", "brand_product", "evidence"), ("SpaceX", "organization", "evidence"), ("Musk", "person", "evidence"), ("Broadcom", "organization", "evidence"),
     ("Meta", "organization", "evidence"), ("Muse", "brand_product", "evidence"), ("United States", "place", "blocked_general"), ("Boston", "place", "evidence"),
     ("Ig Nobel", "other_named", "oov_only"), ("Typhoon", "brand_product", "evidence"),
     ("Riyadh", "place", "evidence"), ("Yemen", "place", "evidence")])
