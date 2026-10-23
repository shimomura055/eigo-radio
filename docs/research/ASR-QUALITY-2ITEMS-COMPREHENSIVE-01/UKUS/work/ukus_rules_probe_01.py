# ukus_rules_probe_01.py -- 規則(接尾辞変換)の再現率/誤同値(false friend)を VarCon で測る(API 0)。設計の根拠データ。
import sys, os, re, json, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ukus_lexicon_01 as lex
from wordfreq import zipf_frequency, top_n_list
UK2US, US2UK, AMB = lex.build_pair_index()
RULES = [  # (UK suffix, US suffix)  ※語末だけでなく活用語尾込みで定義
 ("isation","ization"),("isations","izations"),("ise","ize"),("ised","ized"),("ises","izes"),("ising","izing"),("iser","izer"),("isers","izers"),("isable","izable"),("isably","izably"),
 ("yse","yze"),("ysed","yzed"),("yses","yzes"),("ysing","yzing"),
 ("our","or"),("ours","ors"),("oured","ored"),("ouring","oring"),("ourful","orful"),("ourite","orite"),("ourites","orites"),("ourable","orable"),("ourably","orably"),("ourless","orless"),("oury","ory"),
 ("tre","ter"),("tres","ters"),("bre","ber"),("bres","bers"),("cre","cer"),("cres","cers"),("gre","ger"),
 ("lled","led"),("lling","ling"),("ller","ler"),("llers","lers"),("llor","lor"),
 ("ence","ense"),("ences","enses"),("ogue","og"),("ogues","ogs"),("ogued","ogged"),
 ("ae","e"),("oe","e"),("ement","ment"),("eing","ing"),("ie","y"),("ity","ty"),
]
def apply_rules(w):
    out = set()
    for u, a in RULES:
        if w.endswith(u) and len(w) > len(u) + 2:
            out.add(w[: -len(u)] + a)
        # 語中 ae/oe
        if u in ("ae","oe") and u in w[1:]:
            out.add(w.replace(u, "e"))
    return out
pairs = [(k, u) for k, us in UK2US.items() for u in us]
expl = [(k, u) for k, u in pairs if u in apply_rules(k)]
print("VarCon+breame UK->US pairs", len(pairs), "explained by rules", len(expl), "recall %.3f" % (len(expl) / len(pairs)))
# holdout: 20%をlexiconから隠したときの規則再現率(規則出力が実在語であることを条件)
random.seed(1); random.shuffle(pairs)
hold = pairs[: len(pairs)//5]
ok = sum(1 for k, u in hold if u in apply_rules(k) and zipf_frequency(u, "en") > 0)
print("holdout pairs", len(hold), "rule recovered", ok, "%.3f" % (ok/len(hold)))
# false friend: 上位語彙で、規則を適用して『別の実在語』になるが英米対応表に無い(=誤同値になる)もの
vocab = [w for w in top_n_list("en", 60000) if w.isalpha() and len(w) >= 4]
bad = []
for w in vocab:
    if w in UK2US: continue
    for t in apply_rules(w):
        if t != w and zipf_frequency(t, "en") >= 2.0 and w not in US2UK.get(t, ()):
            bad.append((w, t, round(zipf_frequency(w, "en"),1), round(zipf_frequency(t, "en"),1)))
print("rule false-friend candidates (vocab 60k):", len(bad))
bad.sort(key=lambda x: -x[2])
print(bad[:60])
json.dump({"pairs": len(pairs), "rule_explained": len(expl), "holdout_n": len(hold), "holdout_recovered": ok, "false_friends_top200": bad[:200], "false_friends_n": len(bad)},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ukus_rules_probe_01.json"), "w"), indent=1)

# ---- 制限規則(ise/ize系・our/or系・yse/yze のみ、語幹4字以上)の評価
R2 = [r for r in RULES if r[0].startswith(("is","ys")) or r[0].startswith("our")]
def apply2(w):
    return {w[:-len(u)] + a for u, a in R2 if w.endswith(u) and len(w) - len(u) >= 4}
expl2 = [(k, u) for k, u in pairs if u in apply2(k)]
bad2 = []
for w in vocab:
    if w in UK2US: continue
    for t in apply2(w):
        if t != w and zipf_frequency(t, "en") >= 1.5 and w not in US2UK.get(t, ()):
            bad2.append((w, t))
print("restricted rules: explained", len(expl2), "/", len(pairs), "false friends", len(bad2), bad2[:30])
