# AUDIT_01 共通loader(読み取り専用。API 0。既存script不変)
import json, hashlib, re
from pathlib import Path
ROOT = Path(r"C:\Users\tensh\eigo-radio")
T2 = ROOT / "er112_output" / "kp_gm_trial_02"
T3 = ROOT / "er112_output" / "kp_gm_trial_03"

def load_jsonl(p):
    rows, bad = [], []
    for i, l in enumerate(open(p, encoding="utf-8"), 1):
        try:
            d = json.loads(l); d["_line"] = i; rows.append(d)
        except Exception:
            bad.append(i)
    return rows, bad

def rid(kind, *parts):
    return kind + "_" + hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:12]

def load_cache(p):
    c = {}
    for l in open(p, encoding="utf-8"):
        try:
            d = json.loads(l); c[d["id"]] = d
        except Exception:
            pass
    return c

HARD20 = ["draw a line","pull someone under","shine a light on","brace yourself for","sentence someone to death","execution bell","fire the starting gun","turn on its head","reach for someone's wallet","leap into action","hold on","letter of introduction","bring in","carry the load","on the throne","refueling support","take the wheel","apply one's findings","off the hook","jump to conclusions"]
NORMAL6_T2 = ["think up","behind the scenes","a sense of occasion","give way","keep someone company","pump one's fist"]
