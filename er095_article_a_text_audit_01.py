# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_06 C-2 Phase 4(API 0、費用0円): 記事A text再制作runの決定論検査。
入力: 新run dir(例: er019_output/paycheck_personality/run_pp_02)と旧run dir(Before/After用)。
検査(Opus P-10/P-11/P-05、Trial_02の決定論数値監査 er090_..._trial_02_audit を再利用。Productionへは配線しない=読取専用検査):
  (1) 数値監査: JA最終(ja_writer/revision2.md)・Advanced(b1b/article.md)・Standard(a2/article.md)の全数値が
      台帳の厳密値(EXACT_CORE)かoverlay指定概数(DESIGNATED_APPROX)のいずれかか(UNDESIGNATED_ROUNDING/PERIPHERAL_USED/UNAUTHORIZED=逸脱候補)
  (2) 指定概数の使用状況(JA逐語使用/数字のみ/厳密形/未使用)
  (3) タグ漏れ(TAG_LEAK_RE)・R0書き写し(marks_echoed / approx_marks_echoed)
  (4) Before/After(実際に使われた丸めのみ): 旧完成候補 vs 新text の該当文
  (5) 50%/100%境界をまたぐ丸めの有無(新基準候補。実装しない。有無の報告のみ)
出力: <新run>/audit/rounding_text_audit_01.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from decimal import Decimal

import er053_family_x_factlock_ja_writer_01 as w1
import er090_b3_core_number_rounding_trial_02_audit as au
import er095_b3_core_number_rounding_01 as m


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def sentences_with(text: str, needle: str, lang: str) -> list:
    t = au.nfkc(text)
    n = au.nfkc(needle)
    if lang == "ja":
        parts = re.split(r"(?<=[。！？\n])", t)
    else:
        parts = re.split(r"(?<=[.!?])\s+|\n", t)
    return [p.strip() for p in parts if n in p and p.strip()]


def main(new_dir: str, old_dir: str):
    sidecar = json.load(open(f"{new_dir}/storyline_b3/annotation.json", encoding="utf-8"))
    ovp = f"{new_dir}/storyline_b3/rounding_overlay.json"
    overlay = json.load(open(ovp, encoding="utf-8")) if os.path.exists(ovp) else None
    ov_ok = overlay if overlay and overlay.get("status") == "OK" else None
    allowed = au.build_allowed(sidecar, ov_ok)
    texts = {"ja": rd(f"{new_dir}/ja_writer/revision2.md"), "en_advanced": rd(f"{new_dir}/b1b/article.md"),
             "en_standard": rd(f"{new_dir}/a2/article.md")}
    jv = au.ja_value_set(texts["ja"])
    audit = {"new_dir": new_dir, "old_dir": old_dir, "overlay_status": (overlay or {}).get("status"),
             "overlay_sha256": (overlay or {}).get("overlay_sha256"), "n_approximate_ok": (overlay or {}).get("n_approximate_ok"),
             "numeric_audit": {}, "designated_usage": {}, "tag_leak": {}, "before_after": [], "boundary_crossing": []}
    for k, t in texts.items():
        r = au.classify(t, allowed, "ja" if k == "ja" else "en", None if k == "ja" else jv)
        audit["numeric_audit"][k] = r
        audit["designated_usage"][k] = au.designated_surface_check(t, ov_ok)
        audit["tag_leak"][k] = {"TAG_LEAK_RE_hits": w1.TAG_LEAK_RE.findall(t), "MARK_RE_hits": w1.MARK_RE.findall(t), "TAG_RE_hits": w1.TAG_RE.findall(t)}
    r0m = json.load(open(f"{new_dir}/ja_writer/factlock/r0_meta.json", encoding="utf-8"))
    audit["r0_meta"] = {"marks_echoed": r0m.get("marks_echoed"), "approx_marks_echoed": r0m.get("approx_marks_echoed"), "tags_used": r0m.get("tags_used")}
    audit["rule5_exception_only_designated"] = all(not audit["numeric_audit"][k]["UNDESIGNATED_ROUNDING"] for k in texts)
    # Before/After: 実際に使われた丸め(新JA/Advanced/Standardのいずれかに指定概数が数字として現れたもの)のみ
    old = {"ja": rd(f"{old_dir}/ja_writer/revision2.md"), "en_advanced": rd(f"{old_dir}/b1b/article.md"), "en_standard": rd(f"{old_dir}/a2/article.md")}
    for e in (ov_ok or {}).get("entries", []):
        if e["final_decision"] != m.DECISION_APPROX:
            continue
        for s in e["surfaces"]:
            apv = au.surface_values(s["approx"])
            exv = au.surface_values(s["surface"])
            used_in = {}
            for k, t in texts.items():
                hits = [tok["raw"] for tok in au.tokens(t) if tok["value"] in apv and tok["value"] not in exv]
                if k != "ja":   # EN: 表示形差(14.3万 -> 143 thousand等)も拾うため値が丸め値に有効桁一致するものを追加
                    hits += [tok["raw"] for tok in au.tokens(t) if any(a > 0 and au.round_sig(a, tok["displayed_sig"]) == tok["value"] for a in apv)
                             and tok["value"] not in exv and tok["raw"] not in hits]
                if hits:
                    used_in[k] = {"tokens": hits, "sentences": sentences_with(t, hits[0], "ja" if k == "ja" else "en")[:2]}
            if used_in:
                old_exact = {k: sentences_with(old[k], s["surface"].replace("最大", "").replace("約", ""), "ja" if k == "ja" else "en")[:2] for k in ("ja",)}
                audit["before_after"].append({"concept": e["concept"], "exact_surface": s["surface"], "designated_approx": s["approx"],
                                              "after_used_in": used_in, "before_old_ja_sentences": old_exact["ja"],
                                              "before_old_en_has_exact": {k: bool(re.search(re.escape(s["surface"].split("人")[0].split("台")[0].replace("最大", "")),
                                                                                              au.nfkc(old[k]))) for k in ("en_advanced", "en_standard")}})
            # 50%/100%境界をまたぐ丸め(%のみ)
            if "%" in au.nfkc(s["surface"]) or "％" in s["surface"] or "パーセント" in s["surface"]:
                ev_, av_ = m.parse_surface(s["surface"])["value"], m.parse_surface(s["approx"])["value"]
                if ev_ is not None and av_ is not None:
                    for b in (Decimal(50), Decimal(100)):
                        if (ev_ < b <= av_) or (av_ < b <= ev_):
                            audit["boundary_crossing"].append({"surface": s["surface"], "approx": s["approx"], "boundary": str(b), "used": bool(used_in)})
    os.makedirs(f"{new_dir}/audit", exist_ok=True)
    out = f"{new_dir}/audit/rounding_text_audit_01.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(audit, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: audit[k] for k in ("overlay_status", "n_approximate_ok", "rule5_exception_only_designated", "r0_meta", "boundary_crossing")}, ensure_ascii=False))
    for k in texts:
        r = audit["numeric_audit"][k]
        print(k, "n_tokens", r["n_tokens"], "violations", r["violations"], {c: r[c] for c in ("DESIGNATED_APPROX", "UNDESIGNATED_ROUNDING", "PERIPHERAL_USED", "UNAUTHORIZED")})
    print("before_after_n", len(audit["before_after"]), "->", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
