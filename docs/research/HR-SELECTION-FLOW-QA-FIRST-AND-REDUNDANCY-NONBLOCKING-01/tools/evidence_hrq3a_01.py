# -*- coding: utf-8 -*-
"""HR-SELECTION-FLOW 委任_03A runtime evidence harness(使い捨て・copy-run方式。正式runを汚さない)。

X/Y/Zの正式経路は共通関数 er119_kp_wiring_01.run_kp_with_review(候補生成->QA->presentable_filter->Human Review待ち / resume->finalize)。
本toolはその共通関数をrunnerと同じ引数形(Zのみ src_fn)で、evidence配下の新しいkp_dirに対して実LLMで呼ぶ。runner本体は実行/編集しない。
  gen      --family x|y|z --level a2|b1b   : 本文(既存copy-runから。review.text_sha256で照合)で候補生成->PENDING
  select   --family --level --kp RANKS --vocab RANKS : CLI相当(rv.op_select)で人間選定を再現
  finalize --family --level                  : 同じ共通関数をresume(最終Redundancy QA=実LLM->ALARMなら記録して続行)
  summary  --family --level                  : presentable_filter/redundancy_alarm/telemetryを要約
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ROOT = "C:/Users/tensh/eigo-radio"
sys.path.insert(0, ROOT)
os.chdir(ROOT)
EV = "C:/Users/tensh/eigo-radio-evidence/hrq3a"
NX = "C:/Users/tensh/eigo-radio-evidence/NXW02C"

SRC = {   # (family, level) -> (本文取得法, 照合用review)
    ("x", "a2"): (f"{NX}/x_in/moon_shrinking/run_nxm1/a2/article.md", f"{NX}/x/moon_shrinking__run_nxm1/a2/key_phrases/kp_human_review.json"),
    ("x", "b1b"): (f"{NX}/x_in/moon_shrinking/run_nxm1/b1b/article.md", f"{NX}/x/moon_shrinking__run_nxm1/b1b/key_phrases/kp_human_review.json"),
    ("y", "a2"): (f"{NX}/y/run_nxw_a/translate/a2.md", f"{NX}/y/run_nxw_a/key_phrases/a2/kp_human_review.json"),
    ("y", "b1b"): (f"{NX}/y/run_nxw_a/translate/b1b.md", f"{NX}/y/run_nxw_a/key_phrases/b1b/kp_human_review.json"),
    ("z", "a2"): (f"{NX}/z/run_nxw_a/writer/std.md", None),
    ("z", "b1b"): (f"{NX}/z/run_nxw_a/writer/r2.md", f"{NX}/z/run_nxw_a/key_phrases/b1b/kp_human_review.json"),
}


TAG = os.environ.get("HRQ3A_TAG", "")           # 追加run用(例: Zの別作品)。run_dir=<EV>/<family><TAG>
TEXT_OVERRIDE = os.environ.get("HRQ3A_TEXT")    # 本文path上書き(照合reviewなし)


def text_of(fam, lv):
    path, rev = SRC[(fam, lv)]
    if TEXT_OVERRIDE:
        path, rev = TEXT_OVERRIDE, None
    raw = open(path, encoding="utf-8").read()
    if fam == "x":
        t = raw
    elif fam == "y":
        import er121_family_y_structure_01 as ys
        t = ys.canonical_body(raw)
    else:
        import er026_family_z_fiction_production_runner_01 as z
        t = z.canonical_article_text(raw)
    sha = None
    if rev:
        want = json.load(open(rev, encoding="utf-8")).get("text_sha256")
        import er119_kp_human_review_01 as rv
        sha = rv.sha256_text(t)
        if sha != want:
            raise SystemExit(f"text sha mismatch fam={fam} lv={lv}: {sha} != {want}")
    return t, sha


def run_dir(fam):
    return f"{EV}/{fam}{TAG}"


def kp_dir(fam, lv):
    return f"{run_dir(fam)}/key_phrases/{lv}"


def call(fam, lv):
    import er005_cost_logger as cl
    import er119_kp_wiring_01 as kw
    import er119_kp_candidates_01 as kcand
    os.makedirs(run_dir(fam), exist_ok=True)
    cl.install(f"{run_dir(fam)}/raw_usage_log.jsonl")
    text, sha = text_of(fam, lv)
    src_fn = kcand.make_z_src_fn(text, lv) if fam == "z" else None
    with cl.logging_context(f"HRQ3A_{fam}_{lv}", f"kp_{lv}"):
        return kw.run_kp_with_review(text=text, kp_dir=kp_dir(fam, lv), run_dir=run_dir(fam), family=fam, slug=f"hrq3a_{fam}", level=lv,
                                     article_id=f"hrq3a_{fam}_{lv}", stop_run_dir=run_dir(fam), src_fn=src_fn, run_hint=run_dir(fam))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("gen", "select", "finalize", "summary"))
    ap.add_argument("--family", required=True)
    ap.add_argument("--level", required=True)
    ap.add_argument("--kp", default="")
    ap.add_argument("--vocab", default="")
    ap.add_argument("--by", default="hrq3a_evidence")
    a = ap.parse_args(argv)
    fam, lv = a.family, a.level
    import er119_kp_human_review_01 as rv
    if a.cmd in ("gen", "finalize"):
        out = call(fam, lv)
        print(json.dumps({"kp_review": out.get("kp_review"), "status": out.get("status")}, ensure_ascii=False, default=str)[:1500])
    elif a.cmd == "select":
        kp = [int(x) for x in a.kp.split(",") if x]       # ai_rank
        vo = [int(x) for x in a.vocab.split(",") if x]
        r = rv.op_select(kp_dir(fam, lv), kp_ranks=kp, vocab_ranks=vo, by=a.by)
        print(json.dumps(r, ensure_ascii=False, default=str)[:1500])
    else:
        d = kp_dir(fam, lv)
        c = rv.load_candidates(d) or {}
        print(json.dumps({"presentable_filter": c.get("presentable_filter"), "n_candidates": len(c.get("candidates") or []),
                          "alarm_file": json.load(open(f"{d}/redundancy_alarm.json", encoding="utf-8")) if os.path.exists(f"{d}/redundancy_alarm.json") else None},
                         ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
