# 3(b) 文脈依存文の機械抽出(手順固定 v1。裁定の後に適用=裁定者に旗を見せない)。入力=pool JSON、出力=各文の旗。
# 旗: POLY=多義語リスト / PHRV=句動詞・比喩標識 / DEIX=指示語・代名詞(it/its/them/their/that、文頭のThis/That/These/Those/It/They/Such/Another/Both/Then) / FRAG=4語以下の断片
import json, re, sys, collections
POLY = set("""left set play run point line bank board case charge fine light mean order plan right rest state story stand spot turn work kind mind bear fall miss
hold cover count check cut draw drop face figure fit lead leave make pick pass serve show stick take tell tie watch still could might sister master bar sound
absence source label share""".split())
PHRV = re.compile(r"\b(left out|give up|giving up|put away|putting away|take shelter|talked? (her|him|them) into|bring \w+ ?\w* together|held out|set a lower limit|"
                  r"\w+ed out|\w+ over|\w+ off|\w+ away)\b|\b(like|as if|as though|melted into|cold as)\b", re.I)
DEIX = re.compile(r"^\W*(This|That|These|Those|It|Its|They|Such|Another|Both|Then)\b|\b(it|its|them|their|that)\b", re.I)
def flags(en):
    w = set(re.findall(r"[a-z']+", en.lower()))
    f = []
    if w & POLY: f.append("POLY")
    if PHRV.search(en): f.append("PHRV")
    if DEIX.search(en): f.append("DEIX")
    if len(en.split()) <= 4: f.append("FRAG")
    return f
if __name__ == "__main__":
    pool = json.load(open(sys.argv[1], encoding="utf-8")); out = {r["n"]: flags(r["en"]) for r in pool}
    json.dump(out, open(sys.argv[2], "w"), indent=0)
    c = collections.Counter(len(v) > 0 for v in out.values()); print(len(pool), "flagged", c[True], "unflagged", c[False])
