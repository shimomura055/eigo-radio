# -*- coding: utf-8 -*-
"""Trial専用の決定論検査(API 0): 本文一致・語数・display_formの核語がsource_span由来か・プレースホルダ規則。WordNet複合語signal。"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
import nltk
nltk.data.path.insert(0, os.path.join(HERE, "nltk_data"))
from nltk.corpus import wordnet as wn
PLACE = {"something", "someone", "somebody", "one's", "someone's", "somebody's", "oneself", "somewhere", "one", "sth", "sb"}

def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("—", " ").replace("–", "-")
    return s

def toks(s):
    s = norm(s).lower()
    return [t.strip(".,;:!?\"()[]*#") for t in re.split(r"\s+", s) if t.strip(".,;:!?\"()[]*#")]

def span_in_text(span, text):
    ts, tt = toks(span), toks(text)
    n = len(ts)
    if n == 0: return False
    return any(tt[i:i + n] == ts for i in range(len(tt) - n + 1))

def sentence_in_text(sent, text):
    a = re.sub(r"\s+", " ", norm(sent)).strip().strip('"').lower()
    b = re.sub(r"\s+", " ", norm(text)).lower()
    return a[:60] in b

def lemmas(tok):
    t = tok.lower().replace("'s", "")
    out = {t}
    for pos in ("v", "n", "a", "r"):
        m = wn.morphy(t, pos)
        if m: out.add(m)
    if t.endswith("ing") and len(t) > 5: out.add(t[:-3]); out.add(t[:-3] + "e")
    return out

def same_word(a, b):
    if {a.lower(), b.lower()} == {"a", "an"}:    # 冠詞a/anの音韻的交替は同一語とみなす
        return True
    return bool(lemmas(a) & lemmas(b))

def display_check(display, span):
    """returns (ok, reasons)。displayの非プレースホルダ語がspanの語の語形違いで、かつ順序どおり(部分列)。"""
    reasons = []
    d, s = toks(display), toks(span)
    if not (1 <= len(d) <= 5): reasons.append(f"display語数{len(d)}")
    core = [t for t in d if t not in PLACE]
    if not core: reasons.append("核語なし")
    j = 0
    for t in core:
        found = False
        while j < len(s):
            if same_word(t, s[j]): found = True; j += 1; break
            j += 1
        if not found:
            reasons.append(f"核語'{t}'がsource_span由来でない/順序違い")
            break
    npl = sum(1 for t in d if t in PLACE)
    if npl > 2: reasons.append("プレースホルダ3個以上")
    unmatched = [t for t in s if t not in ("a", "an", "the") and not any(same_word(t, c) for c in core)]
    # 本文に目的語が現れない(受動・省略)句動詞等のため、表現の途中(先頭・末尾でない位置)に限りプレースホルダを1個まで追加できる
    internal_extra = 0
    if npl > len(unmatched):
        idx = [i for i, t in enumerate(d) if t in PLACE]
        internal_extra = sum(1 for i in idx if 0 < i < len(d) - 1)
    if len(d) >= 3 and d[-1] in PLACE and d[-2] in PREPS: reasons.append("前置詞の後ろに末尾プレースホルダが残る")
    if npl > len(unmatched) + min(1, internal_extra): reasons.append(f"プレースホルダ{npl}個が本文の置換語{len(unmatched)}個を超える")
    if re.search(r"[~〜…　-鿿]", display): reasons.append("記号/日本語混入")
    return (not reasons), reasons

def wn_multiword(display):
    """WordNetに複合語見出しがあるか(冠詞除去/the,a挿入/末尾前置詞除去の変形を試す)。supporting signalのみ(None=単語/判定不能)。"""
    core = [t for t in toks(display) if t not in PLACE and t not in ("a", "an", "the")]
    if len(core) < 2: return None
    preps = {"for", "of", "to", "from", "with", "on", "in", "at", "by", "into", "as"}
    variants = [core]
    if core[-1] in preps and len(core) > 2: variants.append(core[:-1])
    for v in list(variants):
        for pos in ("v", "n"):
            m = wn.morphy("_".join(v), pos)
            if m and wn.synsets(m): return True
        if wn.synsets("_".join(v)): return True
        for art in ("the", "a"):
            for i in range(1, len(v)):
                if wn.synsets("_".join(v[:i] + [art] + v[i:])): return True
        # 動詞語形
        for i, t in enumerate(v[:1]):
            for l in lemmas(t):
                if wn.synsets("_".join([l] + v[1:])): return True
    return False


PREPS = {"for", "of", "to", "from", "with", "on", "in", "at", "by", "into", "as", "about", "over", "up", "down", "out", "off", "through", "around", "away", "back"}

def strip_trailing_slot(display):
    """末尾のプレースホルダを決定論で除去(直前が前置詞/粒子の場合のみ)。例: 'make room for something' -> 'make room for'。"""
    t = display.split()
    if len(t) >= 3 and t[-1].lower() in PLACE and t[-2].lower() in PREPS:
        return " ".join(t[:-1])
    return display
