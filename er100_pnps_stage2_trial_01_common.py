# -*- coding: utf-8 -*-
"""PNPS Stage 2 Trial 第1巡 共通部品(Trial専用。Production経路をimportしない/書き換えない)。"""
import difflib, json, os, re

TARGETS = ["toteme", "khaite", "altuzarra", "zabelina", "canele", "meink", "melos"]
HRQ = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
OUT = "er100_output/pnps_stage2_trial_01"
_TOK = re.compile(r"[a-zà-ÿ0-9']+")


def load_rows():
    return [json.loads(l) for l in open(HRQ, encoding="utf-8") if l.strip()]


def norm_tokens(text):
    t = (text or "").lower().replace("é", "e").replace("è", "e")
    return [re.sub(r"'s$", "", x) for x in _TOK.findall(t)]


def step_text(row, prefix, nth=0):
    xs = [s.get("text") or "" for s in row.get("steps", []) if str(s.get("step", "")).startswith(prefix)]
    return xs[nth] if len(xs) > nth else None   # 無いstepは未観測(None)であり空応答('')ではない


def asr_span(canon_text, asr_text, target, ctx=0):
    """canonical中のtarget tokenに対応するASR側token列(difflib整列)。見つからなければ None。"""
    if asr_text is None:
        return None
    c = norm_tokens(canon_text)
    a = norm_tokens(asr_text)
    if target not in c:
        return None
    ci = c.index(target)
    sm = difflib.SequenceMatcher(a=c, b=a, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if i1 <= ci < i2:
            if tag == "equal":
                return [target]
            return a[max(0, j1 - ctx):j2 + ctx]
    return None


def unresolved_spans(row):
    return sorted((row.get("pronunciation_lookups") or {}).keys())
