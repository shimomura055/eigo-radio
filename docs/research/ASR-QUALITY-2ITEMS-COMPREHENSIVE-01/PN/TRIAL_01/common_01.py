# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS PN 委任_02 Trial共通部品(read-only、API 0)。HR queue / 保存pair のreplayを er103(原本)と trial版で行う。"""
import json, os, sys, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import er006_preprod_hardening_01_validation as val
import er103_proper_noun_alarm_policy_01 as pol
import er020_tts_retry_local_rewrite_01 as rw
import er111_pn_entity_table_trial_01 as ret
import er111_pn_trial_evaluate_01 as ev

HERE = os.path.dirname(os.path.abspath(__file__))
Q = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
LEDGER_JSON = "er006_output/pronunciation_ledger_01/ledger.json"


def ledger_tokens(exclude_all=False):
    if exclude_all:
        return frozenset()
    L = json.load(open(LEDGER_JSON, encoding="utf-8"))
    s = set()
    for e in L.values():
        if e.get("ledger_disabled") or e.get("entity_type") == "ja_reading_katakana":
            continue
        for t in pol._fold(e["surface"]).split():
            s.add(t.strip("'"))
    return frozenset(s)


def load_hr_rows():
    rows = [json.loads(l) for l in open(Q, encoding="utf-8") if l.strip()]
    out = []
    for i, r in enumerate(rows):
        wp = r.get("wav_path", "").replace("\\", "/")
        contaminated = ("er026_pscr_outer" in wp) or ("/Temp/" in wp) or wp.startswith("C:")
        out.append((i, r, contaminated))
    return out


def inputs_for(r):
    steps = r.get("steps") or []
    prim = next((s for s in steps if s.get("step") == "primary_1"), None)
    sec = [s for s in steps if s.get("provider") == "azure" and s.get("text")]
    if not prim or prim.get("text") is None:
        return None
    canon = r["canonical_text"]
    sec_text = sec[-1]["text"] if sec else None
    cp = val.classify_asr_match(canon, prim["text"])
    cs = val.classify_asr_match(canon, sec_text) if sec_text else None
    try:
        role = rw.resolve_narrative_role(r.get("segment_id")) if r.get("segment_id") else "FULL_STORY"
    except Exception:
        role = "FULL_STORY"
    return dict(canonical_text=canon, primary_cls=cp, secondary_cls=cs, primary_text=prim["text"], secondary_text=sec_text,
                judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role=role or "FULL_STORY",
                p3_entry=("p3_primary_ng" if not cp.should_pass else "force_secondary"))


def dec_sig(d, strip_diag=False):
    det = dict(d.detail) if isinstance(d.detail, dict) else d.detail
    if strip_diag and isinstance(det, dict):
        det.pop("ret3_rejected", None)
    return (d.accept, d.reason, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence, x.similarity_primary, x.similarity_secondary) for x in d.diffs],
            json.dumps(det, sort_keys=True, default=str))


def run_orig(kw, ledger):
    return pol.evaluate_alarm_eligibility(enabled=True, ledger_surfaces=ledger, **kw)


def run_trial(kw, ledger, table=None, ret3=True):
    return ev.evaluate_alarm_eligibility_pn(enabled=True, ledger_surfaces=ledger, table=table, ret3=ret3, **kw)


# ---------------------------------------------------------------- 本文loader・LLM cache(再現性・費用節約)
import hashlib, re as _re
USAGE_LOG = os.path.join(HERE, "usage_log.jsonl")
CACHE = os.path.join(HERE, "llm_cache.jsonl")


def d3_files():
    d = json.load(open(os.path.join(HERE, "..", "ner_probe_01_result.json"), encoding="utf-8"))
    return [f for f in d["entities"] if os.path.exists(f)]


def load_segments(path):
    """記事/脚本本文を段落単位の Seg 列にする(KP/見出し除外=実TTS対象roleの代理。見出し行`#`は除く)。"""
    txt = open(path, encoding="utf-8").read()
    segs = []
    for para in _re.split(r"\n\s*\n", txt):
        p = para.strip()
        if not p or p.startswith("#") or p.startswith("---"):
            continue
        p = _re.sub(r"^[*_>\-\s]+", "", p)
        segs.append(ret.Seg(text=p, role="FULL_STORY"))
    return segs


def cached_llm(replicate=0, usage_log=USAGE_LOG):
    cache = {}
    if os.path.exists(CACHE):
        for l in open(CACHE, encoding="utf-8"):
            l = l.strip()
            if l:
                o = json.loads(l)
                cache[o["key"]] = o["result"]

    def call(text, pid):
        key = hashlib.sha256(("%s|%s|%s" % (pid, replicate, text)).encode("utf-8")).hexdigest()
        if key in cache:
            r = dict(cache[key])
            r["usage"] = dict(r.get("usage") or {}, cached=True)
            return r
        r = ret.llm_ner_real(text, pid, usage_log=usage_log, tag="rep%s" % replicate)
        with open(CACHE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, "result": r}, ensure_ascii=False) + "\n")
        cache[key] = r
        return r
    return call


def group_key_and_segments(row):
    """HR queue行 -> (group_key, [Seg...])。同じ記事/脚本のStd/Adv(a2,b1b)のTTS canonical text和集合(audit/tts_generation_results.json。対象role[英語ナレーション5 role]のみ)。
    audit が無い行は同じ wav 親ディレクトリのHR canonical を代用(coverage に記録)。"""
    wp = row["wav_path"].replace("\\", "/")
    parts = wp.split("/")
    if "narration" in parts:
        lvl_dir = "/".join(parts[:parts.index("narration")])
        run_dir = "/".join(parts[:parts.index("narration") - 1])
        segs, used = [], []
        for lv in ("a2", "b1b"):
            f = "%s/%s/audit/tts_generation_results.json" % (run_dir, lv)
            if os.path.exists(f):
                try:
                    d = json.load(open(f, encoding="utf-8"))
                except Exception:
                    continue
                used.append(f)
                for sid, v in (d.get("segments") or {}).items():
                    if not isinstance(v, dict):
                        continue
                    role = v.get("role")
                    if not role:
                        try:
                            role = rw.resolve_narrative_role(sid)
                        except Exception:
                            role = None
                    txt = v.get("canonical_text") or v.get("text")
                    if txt and role in pol.APPLICABLE_ROLES:
                        segs.append(ret.Seg(text=txt, role=role, segment_id=sid))
        if segs:
            return run_dir, segs, "audit"
    return os.path.dirname(wp), None, "hr_only"
