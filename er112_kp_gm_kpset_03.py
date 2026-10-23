# -*- coding: utf-8 -*-
"""委任_08 Std確認Trial: 新規通常KP集合の候補抽出(DEV専用、API 0)。
Trial_01/02で使っていない既存X/Z記事(Production run由来)のKPのみ。mock/DEV Trial出力は除外。選定は種類(句動詞/慣用句/コロケーション/名詞句)の層化で、
出力(gloss)を見ずに行う。選定結果はer112_output/kp_gm_trial_03/kpset_03.jsonへ凍結。"""
import glob, json, os, random, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import er112_kp_gm_kpset_02 as K2

RECENT = ("er019_output", "er026_output", "er073_output", "er012_output", "er014_output", "er110_output", "er030_output", "er035_output", "er011_output", "er006_output", "er013_output", "er017_output")
EXCL = ("mock", "er112_output", "synth", "attempt0", "node_modules", "dryrun", "default_off", "negative_fixtures", "over_minimization")
APOS = chr(0x2019)


def candidates(used):
    out = {}
    for p in glob.glob(str(ROOT / "**" / "keywords_canonicalized.json"), recursive=True):
        pp = p.replace(chr(92), "/")
        rel = pp.split("eigo-radio/", 1)[-1]
        if not rel.startswith(RECENT) or any(x in rel.lower() for x in EXCL):
            continue
        d = os.path.dirname(pp)
        art = None
        for fn, mk in (("gloss_alignment_prompt.txt", K2.A_MARK1), ("canonicalization_prompt.txt", K2.A_MARK2)):
            f = os.path.join(d, fn)
            if os.path.exists(f):
                t = open(f, encoding="utf-8").read()
                if mk in t:
                    art = t.split(mk, 1)[1].split("\n\n【Key Phrase候補", 1)[0]
                    break
        if not art:
            continue
        try:
            its = json.load(open(p, encoding="utf-8")).get("items") or []
        except Exception:
            continue
        for it in its:
            k = (it.get("used_form") or it.get("key_phrase") or "").strip()
            s = it.get("source_sentence") or ""
            if not k or k.lower() in used or k.lower() in out or not s:
                continue
            if not (s[:40] in art.replace(APOS, "'") or s[:40] in art):
                continue
            fam = "Z" if any(x in rel.lower() for x in ("er026", "family_z", "er073", "melos", "lemon", "open_window")) else "X"   # 小説(Z)系記事
            out[k.lower()] = dict(key=k, display=it.get("display_phrase") or k, sent=s, article=art, family=fam, run=rel.rsplit("/key_phrases/", 1)[0], src="prod_runs")
    return out


# 選定(出力を見る前に確定。種類=P句動詞/I慣用句・定型/C コロケーション/T 名詞句・用語。記事単位に3〜4件ずつ=本番のバッチ形に近づけ費用も抑える)
SELECT = [
    # (key, type)  X 30件
    ("gap between", "T"), ("room for one's own pace", "C"), ("control over time", "C"), ("too broad a label", "T"),
    ("the new normal", "I"), ("not the same picture", "I"), ("room to choose", "C"),
    ("give back gains", "C"), ("take a sharp turn", "I"), ("center stage", "I"), ("settle at", "P"),
    ("pull back", "P"), ("speak for", "P"), ("step out", "P"), ("take off an AI costume", "C"),
    ("price tag", "T"), ("come down", "P"), ("an unseen clock", "T"),
    ("put on hold", "I"), ("behind the curtain", "I"), ("fill in", "P"),
    ("run on", "P"), ("add up", "P"), ("settle down", "P"),
    ("on paper", "I"), ("a place of one's own", "T"), ("change one's surroundings", "C"),
    ("standard deviation", "T"), ("impulse buying", "T"), ("move in the other direction", "C"),
    # Z 10件
    ("give one's word", "I"), ("fall to one's knees", "I"), ("speak against someone", "C"), ("in one's place", "I"),
    ("catch one's breath", "I"), ("grow lighter", "C"), ("walk out", "P"),
    ("lose trust in someone", "C"), ("hold out a hand", "C"), ("far bank", "T"),
]


def select(used):
    c = candidates(used)
    out, miss = {}, []
    for k, ty in SELECT:
        v = c.get(k.lower())
        if v is None:
            miss.append(k)
            continue
        out[k.lower()] = dict(v, type=ty, tier="normal")
    return out, miss


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import collections, hashlib
    import er112_kp_gm_trial_02 as T
    used = set(T.kpset()) | set(T.PRE_A1_DROP)
    sel, miss = select(used)
    print(len(sel), "missing", miss)
    print(collections.Counter((v["family"], v["type"]) for v in sel.values()))
    print("articles", len({hashlib.sha256(v["article"].encode()).hexdigest()[:8] for v in sel.values()}))
    out = ROOT / "er112_output" / "kp_gm_trial_03"
    out.mkdir(parents=True, exist_ok=True)
    json.dump(sel, open(out / "kpset_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in sel.items():
        print(v["family"], v["type"], "|", v["key"], "|", v["sent"][:90], "|", v["run"][-50:])
