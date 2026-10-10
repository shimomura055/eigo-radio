# -*- coding: utf-8 -*-
"""POST-EN-TRIAL-01 共通: 入力ロード(完全台帳方式)・A3/A4 prompt(ANTENNA-TRIAL-01の事前登録定義をimportのみ。意味変更なし)。
detectors/ と antenna_trial_01/ は変更しない(import only)。"""
import json, os, re, sys, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DET = os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "detectors")
ANT = os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "antenna_trial_01")
sys.path.insert(0, DET); sys.path.insert(0, ANT)
import flagger_lib as L
import run_flagger_01 as R
import ledger_restore_01 as LR
import prompts_flagger as P
import antenna_prompts as A
HDR = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")
LR._HDR = HDR   # process内のみ(FIX01/FIX02/ANTENNAと同一)
FLAGGER_MODEL, EFFORT = "gpt-6.1-sol", "medium"
def sha_b(b): return hashlib.sha256(b).hexdigest()
def load_manifest(): return json.load(open(os.path.join(HERE, "manifest_post_en_01.json"), encoding="utf-8"))
def build_unit(u, man):
    """入力sha・台帳件数(expected=見出し行数 == parsed == manifest)を検証し unit を返す。不一致はAssertionError(API前に止まる)。"""
    ip = os.path.join(REPO, u["input_path"])
    assert sha_b(open(ip, "rb").read()) == u["input_sha256"], "input sha mismatch " + u["unit"]
    lg = man["ledgers"][u["ledger"]]
    lp = os.path.join(REPO, lg["path"])
    txt = open(lp, encoding="utf-8").read()
    assert sha_b(txt.encode("utf-8")) == lg["sha256"], "ledger sha mismatch " + u["unit"]
    lines = txt.splitlines()
    n_broad = sum(1 for ln in lines if ln.startswith("["))
    n_hdr = sum(1 for ln in lines if HDR.match(ln))
    facts = LR.parse_ledger_text(txt)
    assert n_broad == n_hdr == len(facts) == lg["parsed_facts"] == len(lg["ids"]), (n_broad, n_hdr, len(facts), lg["parsed_facts"])
    assert [f["fact_id"] for f in facts] == lg["ids"]
    sents = R._split_sentences(open(ip, encoding="utf-8").read())
    ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)]
    return dict(unit_id=u["unit"], mode="article", facts=facts, sentences=ss, ledger_complete=True, article_path=ip), facts, ss
