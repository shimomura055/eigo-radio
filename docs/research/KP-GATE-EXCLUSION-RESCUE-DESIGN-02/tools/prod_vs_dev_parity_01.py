# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03: DEV(er123 RulePatch[aux+adverb+past]を『変更前Production=git HEAD』へ当てた判定)と
Production新コード(現worktree、パッチ無し)の判定が完全一致することを確認する。API 0(socket遮断)。
  - DEV側: git HEADのer105/er003_key_words_canonicalizationを一時dirに復元してsys.modulesへ先読み込み→er123をimport→RulePatch(aux,adverb,past)
  - Prod側: 現worktreeのer105/kc(パッチ無し)
比較対象: (1)adversarial_01.json 85件(conversions 22/have_roles 40/past 8/idiom 15) (2)実データ(X/Y/Z全KP出力)の表示句x全位置x全語形候補の変換判定
         (3)have_probe 72窓+227窓 (4)過去形表(2表のdict)全体。
使い方: .venv\\Scripts\\python.exe tools/prod_vs_dev_parity_01.py --out parity_01.json   (内部で自分自身を--side dev/prodで2回起動する)
"""
import argparse
import glob
import json
import os
import socket
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RD = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02")


def _blocked(*a, **k):
    raise RuntimeError("network blocked: parity tool is API-0")


socket.socket.connect = _blocked            # type: ignore[assignment]
socket.create_connection = _blocked         # type: ignore[assignment]

_IRR_LEMMAS_BY_FORM = {}


def _items():
    adv = json.load(open(os.path.join(RD, "adversarial_01.json"), encoding="utf-8"))
    hp = json.load(open(os.path.join(RD, "have_probe_02.json"), encoding="utf-8"))
    return adv, hp


def _real_displays():
    displays, pairs = set(), set()
    for pat in ("er019_output", "er026_output", "er121_output"):
        for f in glob.glob(os.path.join(ROOT, pat, "**", "keywords_canonicalized.json"), recursive=True):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception:   # noqa: BLE001
                continue
            for it in d.get("items", []):
                dp, kp = it.get("display_phrase"), it.get("key_phrase") or it.get("used_form")
                if dp:
                    displays.add(dp)
                    if kp:
                        pairs.add((dp, kp))
        for f in glob.glob(os.path.join(ROOT, pat, "**", "kp_candidates.json"), recursive=True):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception:   # noqa: BLE001
                continue
            for c in d.get("candidates", []):
                displays.add(c["selection_phrase"])
                pairs.add((c["selection_phrase"], c["used_form"]))
            for c in d.get("dropped", []):
                displays.add(c["phrase"])
    return sorted(displays), sorted(pairs)


def _candidate_keys(ft, displays):
    """表示句の先頭/to直後の動詞tokenについて、規則活用の基本形候補(CMU/前方一致で絞らない)と不規則lemmaを全て並べる(両側同一の候補集合)。"""
    out = []
    for disp in displays:
        toks = ft._norm_tokens(disp)
        if not toks:
            continue
        pos = [0] + [i + 1 for i, t in enumerate(toks[:-1]) if t.lower() == "to"]
        for i in pos:
            d = toks[i].lower()
            cands = set(ft._verb_base_candidates(d)) | _IRR_LEMMAS_BY_FORM.get(d, set())
            for lem in sorted(cands):
                out.append((disp, " ".join(toks[:i] + [lem] + toks[i + 1:])))
    return out


def compute(side: str) -> dict:
    sys.path.insert(0, ROOT)
    if side == "dev":
        tmp = tempfile.mkdtemp(prefix="parity_head_")
        for name in ("er105_kp_fulltext_selector_01.py", "er003_key_words_canonicalization.py"):
            blob = subprocess.run(["git", "show", "HEAD:" + name], cwd=ROOT, capture_output=True, check=True).stdout
            open(os.path.join(tmp, name), "wb").write(blob)
        sys.path.insert(0, tmp)
        import importlib
        for mod in ("er003_key_words_canonicalization", "er105_kp_fulltext_selector_01"):
            importlib.import_module(mod)
        assert os.path.dirname(sys.modules["er105_kp_fulltext_selector_01"].__file__) == tmp
        import er123_kp_rescue_dev_01 as m
        assert m.ft is sys.modules["er105_kp_fulltext_selector_01"]
        ft, kc = m.ft, m.kc
        for k, v in m.IRR.items():
            for f in v:
                _IRR_LEMMAS_BY_FORM.setdefault(f, set()).add(k)
        patch = m.RulePatch(aux=True, adverb=True, past=True)
        aux_fn = lambda ph: [(t, r) for t, r in m.finite_aux_roles(ph) if t in m._HAVE]            # noqa: E731
        blocked_fn = lambda ph: kc._contains_finite_auxiliary(ph)                                    # noqa: E731
    else:
        import contextlib
        import er003_key_words_canonicalization as kc
        import er105_kp_fulltext_selector_01 as ft
        for k, v in ft.IRR.items():
            for f in v:
                _IRR_LEMMAS_BY_FORM.setdefault(f, set()).add(k)
        patch = contextlib.nullcontext()
        aux_fn = lambda ph: [(t, r) for t, r in ft.finite_aux_roles(ph) if t in ft._HAVE]           # noqa: E731
        blocked_fn = lambda ph: ft.contains_finite_aux_role_based(ph)                                # noqa: E731
    adv, hp = _items()
    res = {}
    with patch:
        res["past_tables"] = {"past_only": sorted(ft._PAST_ONLY_IRREGULAR.items()), "ambiguous": sorted(ft._AMBIGUOUS_IRREGULAR.items())}
        res["adv_conversions"] = {c["display"] + "->" + c["key"]: ft.find_inflection_window(c["key"], c["display"]) is not None
                                  for c in adv["conversions"]}
        res["adv_have_roles"] = {c["phrase"]: aux_fn(c["phrase"]) for c in adv["have_roles"]}
        res["adv_past_forms"] = {w: (w in ft._PAST_ONLY_IRREGULAR or w in ft._AMBIGUOUS_IRREGULAR)
                                 for w in adv["past_forms_must_not_be_added"] + adv["past_forms_must_be_added"]}
        res["adv_idiom_blocked_noidiom"] = {c["phrase"]: bool(blocked_fn(c["phrase"])) for c in adv["idiom"]}
        wins = sorted(set(hp["newly_unblocked_windows"]) | set(hp["still_blocked_windows"]))
        res["have_windows"] = {w: [bool(blocked_fn(w)), aux_fn(w)] for w in wins}
        displays, pairs = _real_displays()
        res["n_displays"], res["n_pairs"] = len(displays), len(pairs)
        res["real_pairs"] = {d + "->" + k: ft.find_inflection_window(k, d) is not None for d, k in pairs if k and k.lower() != d.lower()}
        cand = _candidate_keys(ft, displays)
        res["real_candidates"] = {d + "->" + k: ft.find_inflection_window(k, d) is not None for d, k in cand}
        res["real_candidates_validator"] = {d + "->" + k: kc.validate_canonicalization_item(
            k, d, d, normalization_reason="lemma_normalization", original_span=d, allow_inflection_normalization=True)["ok"]
            for d, k in cand}
        res["have_windows_validator"] = {w: kc.validate_canonicalization_item(
            w, w, w, original_span=w, allow_inflection_normalization=True)["reasons"] for w in wins}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--side", choices=["dev", "prod"])
    ap.add_argument("--side-out")
    a = ap.parse_args()
    if a.side:
        json.dump(compute(a.side), open(a.side_out, "w", encoding="utf-8"), ensure_ascii=False)
        return 0
    tmpd = tempfile.mkdtemp(prefix="parity_")
    outs = {}
    for side in ("dev", "prod"):
        outs[side] = os.path.join(tmpd, side + ".json")
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--side", side, "--side-out", outs[side]], cwd=ROOT)
        if r.returncode != 0:
            print("side failed:", side, r.returncode)
            return 2
    dev, prod = (json.load(open(outs[s], encoding="utf-8")) for s in ("dev", "prod"))
    mism = []
    summary = {}
    for k in dev:
        if k in ("n_displays", "n_pairs"):
            summary[k] = [dev[k], prod[k]]
            if dev[k] != prod[k]:
                mism.append((k, dev[k], prod[k]))
            continue
        d, p = dev[k], prod[k]
        if k != "past_tables":
            keys = set(d) | set(p)
            bad = [x for x in sorted(keys) if d.get(x) != p.get(x)]
            summary[k] = {"n": len(keys), "mismatch": len(bad),
                          "true_count": sum(1 for v in d.values() if v is True) if k.startswith("real") or k == "adv_conversions" else None}
            mism += [(k, x, d.get(x), p.get(x)) for x in bad]
        else:
            summary[k] = {"n_dev": {t: len(v) for t, v in d.items()}, "n_prod": {t: len(v) for t, v in p.items()}}
            if d != p:
                mism.append((k, "table differs"))
    res = {"summary": summary, "mismatches": mism, "parity": not mism,
           "dev_setup": "er123 RulePatch(aux=True, adverb=True, past=True) applied to git HEAD er105/er003_key_words_canonicalization",
           "prod_setup": "current worktree er105/er003_key_words_canonicalization, no patch"}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"parity": res["parity"], "summary": summary, "n_mismatch": len(mism)}, ensure_ascii=False))
    return 0 if res["parity"] else 1


if __name__ == "__main__":
    sys.exit(main())
