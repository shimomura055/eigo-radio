# OPEN333_PREREGISTERED_02.md §5 の E4(便乗PASS)負例・対照。評価script実行前に凍結。
# E4 = Candidate Eが non-cascade 差分(乗り物)を救済したとき、別の場所に残った cascade_eligible 差分(entity_like=カタカナ/略語同士の差、
#      phonetic_uncertain=濁点/半濁点のみの差)が検査されないままPASSになる経路。承認済みの『entity_like/濁点差はCascade(Azure再確認)へ』を迂回する。
# 乗り物(vehicle)= Candidate Eで救済される同音差。KIND: neg=固有名詞/語の読み違い(本来NG/Cascadeが妥当) / cost=等価表記(正常。E4でCascade費用がかかる側) / ctrl=便乗差分なし(E4で不変であるべき)。
VEHICLES = [("封鎖", "風さ"), ("今日", "こんにち"), ("市場", "いちば"), ("間", "目"), ("超", "長")]
# (名, 変形名, kind, label)
NAME_PAIRS = [
    ("メロス", "メラス", "neg", "kata_vowel(ロ→ラ)"),
    ("メロス", "ムロス", "neg", "kata_vowel(メ→ム)"),
    ("ディオニス", "ディオネス", "neg", "kata_vowel(ニ→ネ)"),
    ("セリヌンティウス", "セリヌンティアス", "neg", "kata_vowel(ウ→ア)"),
    ("ミューズ", "ミーザ", "neg", "kata_shape(ミューズ→ミーザ)"),
    ("ベラ", "ボラ", "neg", "kata_vowel(ベ→ボ)"),
    ("ガーデン", "ガーデル", "neg", "kata_consonant(ン→ル)"),
    ("NASA", "ナイキ", "neg", "acronym_vs_other_name"),
    ("IBM", "アイビーエル", "neg", "acronym_misread"),
    ("テスト", "デスト", "neg", "voicing_only_kata(テ→デ)"),
    ("クリーム", "グリーム", "neg", "voicing_only_kata(ク→グ)"),
    ("ヴェラ", "ベラ", "cost", "ヴェ↔ベ(等価表記)"),
    ("ヴァイオリン", "バイオリン", "cost", "ヴァ↔バ(等価表記)"),
    ("NASA", "ナサ", "cost", "acronym_reading(NASA→ナサ)"),
    ("IBM", "アイビーエム", "cost", "acronym_reading(IBM→アイビーエム)"),
    ("muse", "ミューズ", "cost", "latin→kata(muse→ミューズ)"),
]
TEMPLATES = {"txt": ("{n}の{v}について話します", "{n}の{v}について話します"),
             "num": ("{n}は8,900本で、{v}です", "{n}は八千九百本で、{v}です")}


def build():
    rows = []
    for (vc, va) in VEHICLES:
        for entry, (tc, ta) in TEMPLATES.items():
            # 対照: 名は同一(便乗差分なし)。乗り物の差分のみ
            n0 = "メロス"
            rows.append(dict(kind="ctrl", label="same_name", entry=entry, vehicle=f"{vc}/{va}",
                             canon=tc.format(n=n0, v=vc), asr=ta.format(n=n0, v=va)))
            for (n, n2, kind, label) in NAME_PAIRS:
                rows.append(dict(kind=kind, label=label, entry=entry, vehicle=f"{vc}/{va}",
                                 canon=tc.format(n=n, v=vc), asr=ta.format(n=n2, v=va)))
    return rows
