# OPEN333_E4_PREREGISTERED_01.md の追加負例・対照。評価script実行前に凍結。sweep_cases_open333_e4_01.py(凍結)に加える。
# (1) ひらがなのみの濁点差(phonetic_uncertainのみ、entity_likeではない): 前回E4評価では未検証。E4(cascade_eligible全般)とE4E(entity_like限定)の差が出る類。kind=neg_hira
# (2) 乗り物なし・数値entryの純粋な cascade 差(E分岐に到達しない): E4/E4-Nの対象外であることの確認(不変であるべき)。kind=out_of_scope
# (3) 非cascade差が混ざる数値entry(E4-Nが拒否のままであるべき): 名の差(cascade)+しわ->すわ型(非cascade・説明不能)。kind=e4n_keep_reject
import sweep_cases_open333_e4_01 as C1

VEHICLES = C1.VEHICLES
HIRA_NAMES = [("さくら", "ざくら", "hira_voicing(さ→ざ)"), ("ひとり", "びとり", "hira_voicing(ひ→び)"), ("たいこ", "だいこ", "hira_voicing(た→だ)"),
              ("はなし", "ばなし", "hira_voicing(は→ば)"), ("かさ", "がさ", "hira_voicing(か→が)")]


def build():
    rows = []
    for (vc, va) in VEHICLES:
        for entry, (tc, ta) in C1.TEMPLATES.items():
            for (n, n2, label) in HIRA_NAMES:
                rows.append(dict(kind="neg_hira", label=label, entry=entry, vehicle=f"{vc}/{va}",
                                 canon=tc.format(n=n, v=vc), asr=ta.format(n=n2, v=va)))
    # (2) 乗り物なし(Eに到達しない)の数値entry cascade差: 名の差のみ
    for (n, n2, kind, label) in C1.NAME_PAIRS:
        rows.append(dict(kind="out_of_scope", label=label, entry="num", vehicle="-",
                         canon=f"{n}は8,900本です", asr=f"{n2}は八千九百本です"))
    # (3) 数値entry: 名の差(cascade) + 説明不能な非cascade差(しわ->すわ型, 助詞付き)
    for (n, n2, kind, label) in C1.NAME_PAIRS[:6]:
        rows.append(dict(kind="e4n_keep_reject", label="cascade差+しわ→すわ型(説明不能)", entry="num", vehicle="しわ/すわ",
                         canon=f"{n}の月のしわ、8,900本超", asr=f"{n2}の月のすわ、八千九百本超"))
    return rows
