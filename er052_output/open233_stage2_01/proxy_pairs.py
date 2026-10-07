# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 測定(6): 面白さ代理指標(EN版)とユーザー盲検読み比べ用ペア。API無し。非劣性は未確認。
- `docs/pm/stage0_01/narrative_count.py`のJA正規表現はCheckerが触るEN本文に適用できない(JA本文はEN-onlyのCheckerでは不変)ため、同ファイルの
  `align`(文の対応付け: 完全一致=unchanged/類似度0.6以上=modified/他=deleted)を再利用し、変更文比率・削除文比率・文数差と、
  EN版の要素(Hook=疑問符/意外性語、問いかけ、語り手の枠[I/we/you])の保持を、前(Checker前)→後(新構成ON / 現行相当OFF)で算出する。
- ペア: タイトル・Hook(・一行要約)が変わった対象を、ON/OFFの出力を匿名A/Bで eval/pairs_for_user/ に出す(対応表は eval/_private/PAIRS_MAP.json)。"""
import glob
import importlib.util
import json
import pathlib
import random
import re

import replay_lib as L

OUT = L.OUT
sp = importlib.util.spec_from_file_location("narrative_count", L.ROOT / "docs/pm/stage0_01/narrative_count.py")
nc = importlib.util.module_from_spec(sp)
sp.loader.exec_module(nc)

SENT = re.compile(r"(?<=[.!?])\s+")
HOOK_Q = re.compile(r"\?|\b(imagine|picture|what if|suppose|ever)\b", re.I)
SURPRISE = re.compile(r"\b(surpris|unexpected|twist|secret|actually|really|behind the scenes|mystery|who is)\b", re.I)
FRAME = re.compile(r"\b(I|we|you|your|our)\b")


def sents(md):
    out = []
    for p in re.split(r"\n\s*\n", md.strip()):
        p = p.strip()
        if not p or p.startswith("#"):
            continue
        out += [s.strip() for s in SENT.split(p) if s.strip()]
    return out


def elements(md):
    paras = [p.strip() for p in re.split(r"\n\s*\n", md.strip()) if p.strip()]
    title = paras[0].lstrip("# ").strip() if paras else ""
    body = [p for p in paras[1:] if not p.startswith("#")]
    hook = body[0] if body else ""
    return {"hook_question": bool(HOOK_Q.search(hook)), "hook_surprise": bool(SURPRISE.search(title + " " + hook)),
            "title_frame_first_second_person": bool(FRAME.search(title)), "hook_frame_first_second_person": bool(FRAME.search(hook)),
            "n_questions": len(re.findall(r"\?", md)), "title": title, "hook": hook[:200]}


def retention(before, after):
    sb, sa = sents(before), sents(after)
    al = nc.align(sb, sa)
    eb, ea = elements(before), elements(after)
    kept = {k: (None if not eb[k] else bool(ea[k])) for k in ("hook_question", "hook_surprise", "title_frame_first_second_person",
                                                             "hook_frame_first_second_person")}
    return {"n_sent_before": len(sb), "n_sent_after": len(sa), "sent_diff": len(sa) - len(sb),
            "changed_ratio": round(sum(v == "modified" for v in al.values()) / max(1, len(sb)), 3),
            "deleted_ratio": round(sum(v == "deleted" for v in al.values()) / max(1, len(sb)), 3),
            "elements_kept": kept, "n_questions_before": eb["n_questions"], "n_questions_after": ea["n_questions"]}


def main():
    rows = {}
    for f in sorted(glob.glob(str(OUT / "replay_dev" / "stage3_rewrite" / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if "guard_ok" not in d:
            continue
        rows[(d["claim"], d["run"], d["rep"], d["rules_on"])] = d
    targets = json.loads((OUT / "eval" / "stage3_targets.json").read_text(encoding="utf-8"))
    rng = random.Random(20261007)
    results, pairs, private = [], [], []
    pdir = OUT / "eval" / "pairs_for_user"
    pdir.mkdir(parents=True, exist_ok=True)
    for t in targets:
        run, ledger, art = L.load_run(t["run"])
        for rep in range(3):
            on = rows.get((t["claim"], t["run"], rep, True))
            off = rows.get((t["claim"], t["run"], rep, False))
            if not on or not off:
                continue
            tx_on = on["updated_text"] if on["guard_ok"] else art
            tx_off = off["updated_text"] if off["guard_ok"] else art
            rec = {"target": t["i"], "run": t["run"], "section_type": t["section_type"], "rep": rep,
                   "on_guard_ok": on["guard_ok"], "off_guard_ok": off["guard_ok"], "outputs_differ": tx_on != tx_off,
                   "retention_on": retention(art, tx_on), "retention_off": retention(art, tx_off)}
            results.append(rec)
            if rep == 0 and tx_on != tx_off and t["section_type"] in ("title", "hook"):
                pairs.append((t, art, tx_on, tx_off))
    for k, (t, art, tx_on, tx_off) in enumerate(pairs, 1):
        a_is_on = rng.random() < 0.5
        A, B = (tx_on, tx_off) if a_is_on else (tx_off, tx_on)
        (pdir / f"pair_{k:02d}_A.md").write_text(A, encoding="utf-8")
        (pdir / f"pair_{k:02d}_B.md").write_text(B, encoding="utf-8")
        private.append({"pair": f"pair_{k:02d}", "A_is": "新構成(ON)" if a_is_on else "現行相当(OFF)", "target": t["i"], "run": t["run"],
                        "section_type": t["section_type"]})
    (pdir / "README.md").write_text(
        "# ユーザー盲検読み比べ用ペア(STAGE2-01 段階2)\n\n"
        "- 各ペア pair_NN_A.md / pair_NN_B.md はCheckerを通した後の英語記事全文(どちらが新構成かは非公開)。\n"
        "- 質問(案): 「続きを聞きたいのはどちらか」(面白さ)と、気になった事実関係の違い。\n"
        "- **非劣性は未確認**。代理指標(eval/narrative_proxy.json)だけでは面白さの非劣性は言えない。ユーザーの時間が必要な段階3の入力。\n"
        f"- ペア数: {len(pairs)}(タイトル・Hookが変わり、新構成と現行相当で出力が分かれた対象のみ。小標本)。\n", encoding="utf-8")
    (OUT / "eval" / "_private").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / "_private" / "PAIRS_MAP.json").write_text(json.dumps(private, ensure_ascii=False, indent=1), encoding="utf-8")
    agg = {}
    for side in ("on", "off"):
        rs = [r[f"retention_{side}"] for r in results]
        agg[side] = {"n": len(rs), "mean_changed_ratio": round(sum(r["changed_ratio"] for r in rs) / max(1, len(rs)), 4),
                     "mean_deleted_ratio": round(sum(r["deleted_ratio"] for r in rs) / max(1, len(rs)), 4),
                     "mean_sent_diff": round(sum(r["sent_diff"] for r in rs) / max(1, len(rs)), 3),
                     "elements_lost": {k: sum(1 for r in rs if r["elements_kept"][k] is False) for k in
                                       ("hook_question", "hook_surprise", "title_frame_first_second_person", "hook_frame_first_second_person")}}
    (OUT / "eval" / "narrative_proxy.json").write_text(json.dumps({"note": "非劣性未確認。EN版の代理指標(正規表現)。", "aggregate": agg, "rows": results},
                                                                ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"n_rows": len(results), "n_pairs": len(pairs), "aggregate": agg}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
