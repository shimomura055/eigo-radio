# ukus_lexicon_01.py -- ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 UKUS 委任_01 (DEV/Trial・read-only、Production未配線)
# 英米綴り対応表のローダ(調査用)。VarCon 2020.12.07(Kevin Atkinson, 寛容license=SCOWL Copyright) と breame 0.1.2 (Apache-2.0) を読む。
import re, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
_LINE = re.compile(r"^(?P<grp>[^|#]+?)(?:\s*\|\s*(?P<usage>[^#]*?))?\s*(?:#.*)?$")
_HDR = re.compile(r"^# (\S+)(?: (<verified>))? \(level (\d+)\)")


def _parse_group(g):
    tags, _, word = g.partition(":")
    return tags.split(), word.strip()


def load_varcon():
    """list of dict(us=[words], uk=[words], usage=str|None, level=int, verified=bool)。同一行の A推奨 / 非A推奨 をペア化。"""
    out = []
    path = os.path.join(HERE, "varcon_2020.12.07.txt")
    level, verified = 99, False
    for raw in open(path, encoding="latin-1"):
        raw = raw.rstrip("\n")
        if raw.startswith("# "):
            mh = _HDR.match(raw)
            if mh:
                level, verified = int(mh.group(3)), bool(mh.group(2))
            continue
        if not raw or raw.startswith("#"):
            continue
        m = _LINE.match(raw)
        if not m:
            continue
        usage = (m.group("usage") or "").strip() or None
        us, uk = [], []
        for g in m.group("grp").split(" / "):
            tags, w = _parse_group(g)
            if not w or " " in w:
                continue
            good = [t for t in tags if t and not re.search(r"[x\-]", t)]   # 'x'=誤綴り '-'=非推奨 は許容形に使わない
            if not good:
                continue
            plain = {re.sub(r"[.\d]", "", t) for t in good}                 # 変異印(v/V)なし=その地域の推奨綴り
            (us if "A" in plain else uk).append(w)                          # 推奨AでなければUK側(Av=米でも使われる非推奨形を含む)
        if us and uk:
            out.append({"us": us, "uk": uk, "usage": usage, "level": level, "verified": verified})
    return out


def load_breame():
    ns = {}
    exec(compile(open(os.path.join(HERE, "breame_0.1.2_spelling_constants.py"), encoding="utf-8").read(), "b", "exec"), ns)
    return ns["BRITISH_ENGLISH_SPELLINGS"]


def build_pair_index(max_level=999, only_verified=False, with_breame=True):
    """uk2us: UK語 -> {US語}, us2uk: 逆引き, amb: 用法(名詞/動詞等)で綴りが分かれる(usage付き)ペア。固有名詞(大文字始まり)は除外。"""
    uk2us = collections.defaultdict(set); us2uk = collections.defaultdict(set); amb = set()
    for e in load_varcon():
        if e["level"] > max_level or (only_verified and not e["verified"]):
            continue
        if any(w[:1].isupper() for w in e["us"] + e["uk"]):
            continue
        for u in e["us"]:
            for k in e["uk"]:
                if u == k:
                    continue
                uk2us[k].add(u); us2uk[u].add(k)
                if e["usage"]:
                    amb.add((k, u))
    if with_breame:
        for k, u in load_breame().items():
            if k != u:
                uk2us[k].add(u); us2uk[u].add(k)
    return uk2us, us2uk, amb


if __name__ == "__main__":
    a, b, amb = build_pair_index()
    print("uk words", len(a), "us words", len(b), "usage-qualified pairs", len(amb))
