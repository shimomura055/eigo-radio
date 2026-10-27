"""F班(委任_06F) 生成ページの独立検査(API 0)。確定レコード(Std/Adv)とページHTMLを突合し、件数・訳リスト・Part 1・⏸・check_pageを記録する。
用法: verify_page_s23f_01.py --html <page> --a2-kp <kp_dir> --b1b-kp <kp_dir> --audience public|dev --out <json>
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.getcwd())
from bs4 import BeautifulSoup


def rec(kp_dir):
    with open(os.path.join(kp_dir, "confirmed_selection.json"), encoding="utf-8") as f:
        r = json.load(f)
    items = r["items"]
    c1 = [i for i in items if i["category"] == 1]
    c2 = [i for i in items if i["category"] == 2]
    c3 = [u for u in (r.get("unconsumed") or []) if u.get("category") == 3]
    return {"display_spec": r.get("display_spec"), "revision": r.get("revision"), "cat1": c1, "cat2": c2, "cat3": c3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--a2-kp", required=True)
    ap.add_argument("--b1b-kp", required=True)
    ap.add_argument("--audience", default="public")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    html = open(a.html, encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    recs = {"Standard": rec(a.a2_kp), "Advanced": rec(a.b1b_kp)}
    sect = None
    per = {k: {"lk": {"lk1": [], "lk2": [], "lk3": []}, "meaning_ul": [], "p1_h3": 0, "p1_h4": [], "legend": 0} for k in recs}
    for el in soup.descendants:
        if getattr(el, "name", None) is None:
            continue
        if el.name in ("h1", "h2"):
            t = el.get_text(" ", strip=True)
            for k in recs:
                if t.startswith(k):
                    sect = k
        if sect is None:
            continue
        cls = el.get("class") or []
        if el.has_attr("data-hl"):
            for k in ("lk1", "lk2", "lk3"):
                if k in cls:
                    per[sect]["lk"][k].append({"id": el["data-hl"], "text": el.get_text(), "tag": el.name, "title": el.get("title")})
        if el.name == "ul" and "lk-meaning" in cls:
            per[sect]["meaning_ul"].append([li.get_text() for li in el.find_all("li")])
        if el.name == "p" and "lk-legend" in cls:
            per[sect]["legend"] += 1
        if el.name == "h3" and "Vocabulary" in el.get_text():
            per[sect]["p1_h3"] += 1
        if el.name == "h4" and per[sect]["p1_h3"] and not per[sect].get("p1_closed"):
            per[sect]["p1_h4"].append(el.get_text(" ", strip=True))
        if el.name == "h3" and "Grammar" in el.get_text():
            per[sect]["p1_closed"] = True
    out = {"html": a.html, "audience": a.audience, "sections": {}}
    for k, r in recs.items():
        p = per[k]
        ids = {kk: sorted({x["id"] for x in v}) for kk, v in p["lk"].items()}
        want = {"lk1": sorted(i["candidate_id"] for i in r["cat1"]), "lk2": sorted(i["candidate_id"] for i in r["cat2"]), "lk3": sorted(u["candidate_id"] for u in r["cat3"])}
        gloss_want = [f'{u["used_form"]} ＝ {u["japanese_gloss"]}' for u in r["cat3"]]
        gloss_got = [g for ul in p["meaning_ul"] for g in ul]
        out["sections"][k] = {
            "display_spec": r["display_spec"], "record_revision": r["revision"],
            "confirmed_counts": {kk: len(v) for kk, v in want.items()},
            "data_hl_elements": {kk: len(v) for kk, v in p["lk"].items()},
            "data_hl_distinct_ids": {kk: len(v) for kk, v in ids.items()},
            "data_hl_ids_equal_confirmed": {kk: ids[kk] == want[kk] for kk in want},
            "lk3_title_attr_present": any(x["title"] for x in p["lk"]["lk3"]),
            "meaning_ul_count": len(p["meaning_ul"]),
            "meaning_li": gloss_got,
            "meaning_equals_confirmed_japanese_gloss_verbatim": sorted(gloss_got) == sorted(gloss_want),
            "legend_count": p["legend"],
            "part1_h3_count": p["p1_h3"],
            "part1_h4_terms": p["p1_h4"],
            "part1_expected_terms": [i["used_form"] for i in r["cat1"] + r["cat2"]],
            "part1_items_equal_cat12": len(p["p1_h4"]) == len(r["cat1"]) + len(r["cat2"]),
        }
    body_text = soup.get_text()
    out["legend_total_in_page"] = len(soup.select("p.lk-legend"))
    out["pause_total_in_html"] = html.count("⏸") + len(re.findall(r"&#(?:9208|x23f8);", html, re.I))
    out["pause_inside_data_hl"] = sum(1 for e in soup.find_all(attrs={"data-hl": True}) if "⏸" in e.get_text() or e.select(".chunk-mark"))
    out["chunk_mark_spans"] = len(soup.select(".chunk-mark"))
    out["public_pause_zero_ok"] = (out["pause_total_in_html"] == 0) if a.audience == "public" else None
    out["dev_pause_outside_decoration_ok"] = (out["pause_total_in_html"] > 0 and out["pause_inside_data_hl"] == 0) if a.audience == "dev" else None
    try:
        import er_user_listening_page_common_01 as cp
        base = os.path.dirname(os.path.abspath(a.html))
        res = cp.check_page(html, base_dir=base, levels=("Standard", "Advanced"), audience=("dev" if a.audience == "dev" else cp.AUDIENCE_PUBLIC))
        out["check_page"] = {"overall": res.get("overall"), "failed_checks": {k: v.get("detail") for k, v in (res.get("checks") or {}).items() if not v.get("ok")}} if isinstance(res, dict) else str(res)
    except Exception as e:  # noqa
        out["check_page"] = f"ERROR {type(e).__name__}: {e}"
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "sections"}, ensure_ascii=False)[:600])
    for k, s in out["sections"].items():
        print(k, json.dumps({kk: s[kk] for kk in ("confirmed_counts", "data_hl_elements", "data_hl_ids_equal_confirmed", "meaning_equals_confirmed_japanese_gloss_verbatim", "part1_h3_count", "part1_items_equal_cat12", "legend_count")}, ensure_ascii=False))


main()
