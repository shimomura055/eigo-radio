# -*- coding: utf-8 -*-
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
D = json.load(open("er052_output/open233_kpi_recovery_02_offline_01/d_type_dump_01.json", encoding="utf-8"))
def sents(text):
    out = []
    pos = 0
    for para in re.split(r"\n\s*\n", text):
        pass
    return re.split(r"(?<=[.!?”])\s+", text)
for i, r in enumerate(D, 1):
    art = r["article"]
    print("=" * 20, i, r["instance"])
    heads = [l for l in art.split("\n") if l.startswith("#")]
    print("headings:", heads)
    for fr in (r["fragments"] or []):
        n = art.count(fr)
        idx = art.find(fr)
        # paragraph containing it
        paras = re.split(r"\n\s*\n", art)
        ph = [p for p in paras if fr in p]
        print("FRAG count=%d :: %s" % (n, fr[:120]))
        for p in ph[:2]:
            # section: last heading before
            before = art[:art.find(p)]
            hs = [l for l in before.split("\n") if l.startswith("#")]
            print("   in section:", hs[-1] if hs else None)
            print("   para:", p[:500].replace("\n", " "))
    # key-term search
    keys = {1: ["luggage crew", "visual"], 2: ["believ", "thought", "from an AI", "AI"], 3: ["Oil prices", "oil prices", "Brent"], 4: ["backup", "back-up", "fallback"]}.get(i, [])
    for k in keys:
        hits = [s.strip().replace("\n", " ") for s in sents(art) if k in s]
        print("  term %r hits=%d" % (k, len(hits)))
        for h in hits[:6]:
            print("     -", h[:240])
