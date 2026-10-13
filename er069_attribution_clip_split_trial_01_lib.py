# -*- coding: utf-8 -*-
"""FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 共通ライブラリ(Trial隔離。Production非変更)。
共有telemetry/Master Store/HR/ledgerへは一切書かない。出力は er069_output/ 配下のみ。"""
import re, json, hashlib, os

SIB_END = re.compile(r"(s|z|x|sh|ch|ce|se|ze|ge)$", re.I)          # 語末歯擦音(綴り近似)
SIB_START = re.compile(r"^(s|z|sh|ch|j|x|c[eiy])", re.I)            # 語頭歯擦音(綴り近似)
SPEECH_VERB = re.compile(r"\b(said|says|say|asked|asks|replied|answered|whispered|shouted|cried|called|told|"
                         r"added|continued|murmured|laughed|spoke|begged|pleaded|demanded)\b", re.I)
STOP_WORDS_CAP = {"I", "The", "A", "An", "He", "She", "They", "We", "It", "His", "Her", "Their", "Then", "But",
                  "And", "So", "If", "At", "In", "On", "For", "When", "As", "One", "Now", "No", "Yes", "Please",
                  "That", "This", "There", "What", "Why", "How", "You", "Your", "My", "Let", "Do", "Is", "Are"}


def sha256_file(p):
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def line_count(p):
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return sum(1 for _ in f)


def words(text):
    return re.findall(r"[A-Za-z][A-Za-z'’\-]*", text)


def bucket(n):
    return "<=2" if n <= 2 else ("3" if n == 3 else ("4-5" if n <= 5 else ">=6"))


def find_names(text):
    """文中(直前が文末記号・引用符でない位置)で大文字始まりの語 = 固有名詞候補。"""
    names = set()
    for pre, w in re.findall(r"([.!?“\"”]?\s*)([A-Za-z][A-Za-z'’\-]*)", text):
        if w[0].isupper() and w not in STOP_WORDS_CAP and pre != "" and not re.search(r"[.!?“\"”]", pre):
            names.add(re.sub(r"['’]s$", "", w))
    return names


def sib_boundaries(clip_text, names):
    """clip内の語境界で 語末歯擦音+次語頭歯擦音 を列挙。"""
    ws = words(clip_text)
    out = []
    for a, b in zip(ws, ws[1:]):
        if SIB_END.search(a) and SIB_START.search(b):
            proper = re.sub(r"['’]s$", "", a) in names
            out.append({"w1": a, "w2": b, "proper_noun": proper})
    return out


def tag_info(clips):
    """narrator clipについて、隣接clipに非narratorがあるか/話法動詞を含むか。"""
    res = []
    for i, c in enumerate(clips):
        if c["voice"] != "narrator":
            continue
        prev_v = clips[i - 1]["voice"] if i > 0 else None
        next_v = clips[i + 1]["voice"] if i + 1 < len(clips) else None
        adj_q = (prev_v not in (None, "narrator")) or (next_v not in (None, "narrator"))
        both_q = (prev_v not in (None, "narrator")) and (next_v not in (None, "narrator"))
        res.append({"idx": i, "id": c["id"], "text": c["text"], "wc": c["word_count"],
                    "adjacent_to_quote": adj_q, "between_quotes": both_q,
                    "has_speech_verb": bool(SPEECH_VERB.search(c["text"])),
                    "prev_voice": prev_v, "next_voice": next_v})
    return res
