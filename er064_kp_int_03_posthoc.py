# Round3 事後(非登録)観察 ¥0: Stage0保存済みLLM生出力に対し、縮約ガードの代替案C(tail-preserving)を決定論で再適用して差を見る。
# Go/No-Go判定には使わない(判定は事前登録のとおり)。API呼出なし。出力: round3/posthoc_r3.json
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_03_b1 as B  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402

EX = B.EX
OUT = B.OUT


def guard_c(parsed):
    """案C: core_spanによる縮約は、縮約後spanがLLM spanの末尾tokenを保つ場合のみ(末尾の目的語・補語を切り落とす縮約は行わない)。"""
    out, hits = {"items": []}, []
    for it in parsed.get("items") or []:
        it2 = dict(it)
        nar = EX.narrow_to_core_span(it.get("span", ""), it.get("core_span", ""))
        if nar["narrowed"]:
            orig = EX.ext._WORD_TOKEN_RE.findall(EX._norm_text(it.get("span", "")))
            nt = EX.ext._WORD_TOKEN_RE.findall(EX._norm_text(nar["span"]))
            closed_start = nt[0].lower() in EX.core._CLOSED
            tail_cut = nt[-1].lower() != orig[-1].lower()
            if closed_start or tail_cut:
                hits.append({"span": it.get("span"), "core_span": it.get("core_span"), "would_narrow_to": nar["span"], "closed_start": closed_start, "tail_cut": tail_cut})
                it2["core_span"] = it.get("span", "")
        out["items"].append(it2)
    return out, hits


AUX_LEAD = {"had", "has", "have", "is", "are", "was", "were", "will", "would", "can", "could", "do", "does", "did"}


def guard_d(parsed):
    """案D: 案C + LLM spanの先頭が有限助動詞なら、その1語を除いたspanを使う(`had been behind ...`→`been behind ...`)。"""
    gp, hits = guard_c(parsed)
    for it in gp["items"]:
        toks = EX.ext._WORD_TOKEN_RE.findall(EX._norm_text(it.get("span", "")))
        if len(toks) >= 3 and toks[0].lower() in AUX_LEAD:
            it["span"] = " ".join(toks[1:])
            if it.get("core_span", "").lower().startswith(toks[0].lower() + " "):
                it["core_span"] = it["span"]
            if len(EX.ext._WORD_TOKEN_RE.findall(EX._norm_text(it.get("core_span", "")))) >= len(toks) - 1:
                it["core_span"] = it["span"]
    return gp, hits


def main():
    R._init()
    res = {"purpose": "事後(非登録)観察: 縮約ガードC(閉クラス始まり or 末尾切落としは縮約しない)を保存済み抽出に再適用。Go/No-Goには使わない", "runs": []}
    for f in sorted(glob.glob(f"{B.B1DIR}/*/run*.json")):
        rec = json.load(open(f, encoding="utf-8"))
        aid = rec["id"]
        if aid in B.NEG_CONTROLS:
            continue
        base, st0, ex = B.existing_for(aid)
        gp, hits = guard_c(rec["parsed"])
        built = EX.build_llm_candidates(gp, st0["sentence_units"], set(ex), cap=8)
        art = B.article_text(aid)
        acc = sorted(built["accepted"], key=lambda c: (c.get("llm_rank") if isinstance(c.get("llm_rank"), int) else 10 ** 6, B.first_pos(c["surface_form"], art)))[:B.ROUND3_CAP]
        gd, _ = guard_d(rec["parsed"])
        bd = EX.build_llm_candidates(gd, st0["sentence_units"], set(ex), cap=8)
        accd = sorted(bd["accepted"], key=lambda c: (c.get("llm_rank") if isinstance(c.get("llm_rank"), int) else 10 ** 6, B.first_pos(c["surface_form"], art)))[:B.ROUND3_CAP]
        res["runs"].append({"guardD_accepted": [c["surface_form"] for c in accd], "id": aid, "run": rec["run"], "registered_accepted": [c["surface_form"] for c in rec["built"]["accepted"]],
                            "guardC_accepted": [c["surface_form"] for c in acc], "guardC_hits": hits,
                            "guardC_rejected": [(x.get("span"), x.get("reason")) for x in built["rejected"]]})
    json.dump(res, open(f"{OUT}/posthoc_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in res["runs"]:
        if r["registered_accepted"] != r["guardC_accepted"] or r["registered_accepted"] != r["guardD_accepted"]:
            print(r["id"], r["run"], r["registered_accepted"], "->C", r["guardC_accepted"], "->D", r["guardD_accepted"])


if __name__ == "__main__":
    main()
