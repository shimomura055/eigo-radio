# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B: 実Part 2成果物(コピーdir)に対する M6 evidence(API 0)。
Part 2の抽出モデル(g.MODEL。extract/explain signatureに入る)を差替えても、確定済み文法は再抽出・再解説(LLM)せず凍結した解説全文を使うことを示す。
対照: 保護OFF(kill switch)で同じ差替えをすると、凍結が無ければ再抽出に進む(=凍結が効いている証明)。

  kcp2b_ev_part2_01.py --family x|z --run <copy> --text <path|canon:z:path> --study-dir <dir> --out <json>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)

import er120_part2_grammar_production_01 as g2  # noqa: E402
import er120_part2_wiring_01 as p2w  # noqa: E402
import er128_kp_confirmed_content_01 as cc  # noqa: E402

CALLS = {"extract": 0, "explain": 0}


def boom_extract(prompt):
    CALLS["extract"] += 1
    raise AssertionError("Step A''(再抽出LLM)が呼ばれた")


def boom_explain(prompt):
    CALLS["explain"] += 1
    raise AssertionError("Step B(再解説LLM)が呼ばれた")


def load_paragraphs(spec):
    if spec.startswith("canon:z:"):
        import er026_family_z_fiction_production_runner_01 as zr
        text = zr.canonical_article_text(open(spec[8:], encoding="utf-8").read())
        return text.split("\n\n"), zr.STORY_REGISTRY["melos"]["topic_title"]
    text = open(spec, encoding="utf-8").read()
    return p2w.g.paragraphs_from_article_md(text), p2w.label_for(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--study-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sd = a.study_dir
    paragraphs, label = load_paragraphs(a.text)
    out = {"family": a.family, "study_dir": sd, "MODEL_actual": g2.MODEL, "MODEL_patched_to": "some-other-model-id-for-evidence"}
    r0 = p2w.require_final(sd, paragraphs, label, next_command="evidence", where="ev-baseline")
    fz = cc.load_frozen_grammar(sd)
    out["frozen"] = {"source": fz["source"], "candidate_id": fz["candidate_id"], "token": cc.frozen_token(fz), "explanation_md_sha16": cc.frozen_sha(fz["candidate_id"], fz["sentence"], fz["explanation_md"], fz.get("translation_ja"))}
    out["baseline_explain_signature"] = r0.get("explain_signature")
    with mock.patch.object(g2, "MODEL", out["MODEL_patched_to"]):
        # 凍結なしの従来検査なら失効する(対照。凍結の前提)
        gdoc, grev = p2w.gr.load_candidates(sd), p2w.gr.load_review(sd)
        try:
            g2.require_fresh_part2(r0, paragraphs, label, next_command="x", candidates_doc=gdoc, grammar_review=grev)
            out["control_without_freeze"] = "PASS(失効しなかった=この前提は成立しない)"
        except g2.Part2Stale as e:
            out["control_without_freeze"] = "Part2Stale(model変更でextract/explain signatureは失効する): " + str(e)[:120]
        # 凍結あり
        res = p2w.require_final(sd, paragraphs, label, next_command="evidence", where="ev-patched")
        st = p2w.candidate_stage(sd, run_dir=a.run, family=a.family, slug="evidence", paragraphs=paragraphs, label=label, extract_call_fn=boom_extract)
        fin = p2w.finalize_stage(sd, paragraphs=paragraphs, label=label, ref_ja_pool=None, explain_call_fn=boom_explain, write=False)
        out["patched"] = {"require_final": "PASS", "candidate_stage_state": st["state"], "candidate_stage_generated": st.get("generated"),
                          "finalize_reused": fin["reused"], "explanation_unchanged": fin["result"]["explanation_md"] == fz["explanation_md"] == res["explanation_md"],
                          "extract_calls": CALLS["extract"], "explain_calls": CALLS["explain"]}
    # 対照(保護OFF)
    # 対照は study_dir の使い捨てコピーで行う(保護OFFの従来経路は既存候補をSUPERSEDEDへ退避してから再抽出に進むため、実コピーdirを壊さない)
    import shutil
    import tempfile
    tdir = os.path.join(tempfile.mkdtemp(prefix="kcp2b_p2ctl_"), "study_text")
    shutil.copytree(sd, tdir)
    with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}), mock.patch.object(g2, "MODEL", out["MODEL_patched_to"]):
        try:
            p2w.candidate_stage(tdir, run_dir=a.run, family=a.family, slug="evidence", paragraphs=paragraphs, label=label, extract_call_fn=boom_extract)
            out["control_protection_off"] = "再抽出に進まなかった"
        except Exception as e:  # noqa: BLE001
            out["control_protection_off"] = f"再抽出に進んだ(止まった例外={type(e).__name__}: {str(e)[:100]})。extract_calls={CALLS['extract']}"
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
