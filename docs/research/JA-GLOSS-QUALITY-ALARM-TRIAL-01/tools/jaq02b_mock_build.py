# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02B: DEV警告表示試作の構築(API 0・決定論)。
user_test/selection_form_v3/ (Production, 無変更) を複製して user_test/dev_ja_alarm_mock_01/ を作る。
差分は index.html の (a)CSS (b)常時DEVバナー (c)qaHtml関数と呼出1か所 (d)localStorageキーの接頭辞 のみ。form_logic.js はバイト同一コピー。
データ: Trialの保存済み出力(final rep1, 規則=frozen_config.rule)から quality_alarm を決定論的に付与。表示時のAPI呼出0。
使い方: jaq02b_mock_build.py <frozen_config.json> <final_run_name>
"""
import json, os, sys, shutil, re, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, HERE)
import jaq02b_score as S

SRC = os.path.join(ROOT, "user_test", "selection_form_v3"); DST = os.path.join(ROOT, "user_test", "dev_ja_alarm_mock_01")
J = lambda p: json.load(open(p, encoding="utf-8"))

CSS = (".qa-dev-banner{background:#b3261e;color:#fff;font-weight:700;padding:10px 12px;border-radius:8px;margin:8px 0;font-size:15px;text-align:center}"
       ".qa-alarm{margin:6px 0 2px;padding:7px 10px;border:1px solid #e3b4ac;background:#fdf0ee;border-radius:8px;font-size:13px;line-height:1.55;overflow-wrap:anywhere;white-space:normal}"
       ".qa-alarm .qa-h{color:#ad4938;font-weight:700}.qa-alarm .qa-r{color:#3d4852;margin-top:2px}.qa-alarm .qa-sug{color:#1f3b57;margin-top:2px;font-weight:600}")
JS_FN = ("function qaHtml(it){\n"
         "  if(/[?&]qa=off/.test(location.search))return '';\n"
         "  var q=it&&it.quality_alarm;if(!q||!q.warn)return '';\n"
         "  var sg=(q.suggestion||'').trim(),cur=(it.ja_gloss||'').trim();\n"
         "  var s=(sg&&sg!==cur)?'<div class=\"qa-sug\">改善候補：'+esc(sg)+'</div>':'';\n"
         "  return '<div class=\"qa-alarm\" role=\"note\" data-qa=\"warn\"><div class=\"qa-h\"><span aria-hidden=\"true\">\U0001F534</span> 訳語の確認を推奨</div><div class=\"qa-r\">'+esc(q.reason_ja||'')+'</div>'+s+'</div>';\n"
         "}\n")
BANNER = '<div class="qa-dev-banner" role="alert">DEV試作・ここから選定結果を送らない</div>'


def patch_index(h):
    def rep(old, new):
        nonlocal h
        assert h.count(old) == 1, (old[:50], h.count(old))
        h = h.replace(old, new, 1)
    rep("</style>", CSS + "</style>")
    rep("<main class=\"panel\"><h1>", "<main class=\"panel\">" + BANNER + "<h1>")
    rep("function jumpTo(key){", JS_FN + "function jumpTo(key){")
    rep("<span class=\"muted\">（日本語訳は未生成です。仮訳は表示しません）</span>')+'</div>'+", "<span class=\"muted\">（日本語訳は未生成です。仮訳は表示しません）</span>')+'</div>'+qaHtml(it)+")
    rep("STORE_KEY=FL.storeKey(null,true);$('devBanner').hidden=false;", "STORE_KEY='DEVMOCK_QA|'+FL.storeKey(null,true);$('devBanner').hidden=false;")
    return h


def main():
    cfg = J(sys.argv[1]); run = sys.argv[2]
    rule = cfg["rule"]; method = cfg["method"]
    U = J(os.path.join(S.TRIAL, "units.json"))
    res, _, _ = S.load_run(run, U)
    pool = J(os.path.join(BASE, "adjudication/pool.json"))
    pid_of = {(q["file"], q["candidate_id"]): q["pid"] for q in pool}
    if os.path.exists(DST): shutil.rmtree(DST)
    os.makedirs(os.path.join(DST, "data"))
    shutil.copyfile(os.path.join(SRC, "form_logic.js"), os.path.join(DST, "form_logic.js"))   # バイト同一
    h = open(os.path.join(SRC, "index.html"), "rb").read().decode("utf-8")
    open(os.path.join(DST, "index.html"), "wb").write(patch_index(h).encode("utf-8"))
    idx = J(os.path.join(SRC, "data", "articles.json"))
    files = sorted({q["file"] for q in pool})
    arts = [a for a in idx["articles"] if os.path.basename(a.get("data") or "") in files]
    stats = {"files": 0, "candidates": 0, "warn": 0, "unchecked": 0, "reason_over60": 0, "sug_same_hidden": 0, "per_level": {}}
    for f in files:
        d = J(os.path.join(SRC, "data", f)); unchecked = 0; nwarn = 0; ncand = 0
        for it in d["phrases"] + d["words"]:
            pid = pid_of.get((f, it["candidate_id"]))
            b = res.get(pid); ncand += 1
            if b is None or b.get("res") is None:
                unchecked += 1; it["quality_alarm"] = {"warn": False, "unchecked": True}; continue
            r = b["res"]; w = S.rule_warn(r, rule, method)
            q = {"warn": bool(w), "rule": rule, "run": run}
            if w:
                nwarn += 1; q.update({"reason_ja": r["reason_ja"], "suggestion": r["suggestion"], "severity": r["severity"], "category": r["category"], "confidence": r["confidence"]})
                if len(r["reason_ja"]) > 60: stats["reason_over60"] += 1
                if r["suggestion"].strip() and r["suggestion"].strip() == (it.get("ja_gloss") or "").strip(): stats["sug_same_hidden"] += 1
            it["quality_alarm"] = q
        if unchecked:
            d.setdefault("data_warnings", []).append({"code": "ja_gloss_check_unrun", "message_ja": f"訳語チェック未実施({unchecked}件)"})
        json.dump(d, open(os.path.join(DST, "data", f), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        stats["files"] += 1; stats["candidates"] += ncand; stats["warn"] += nwarn; stats["unchecked"] += unchecked
        stats["per_level"][f] = {"n": ncand, "warn": nwarn, "unchecked": unchecked}
    out_idx = {"schema": idx["schema"], "note_ja": "DEV試作(JA-GLOSS-QUALITY-ALARM-TRIAL-01)。Production候補データの複製+quality_alarm付与。ここから選定結果を送らない。", "default": arts[0]["slug"] + "__" + arts[0]["level"], "articles": arts}
    json.dump(out_idx, open(os.path.join(DST, "data", "articles.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    stats["form_logic_sha256_prod"] = sha(os.path.join(SRC, "form_logic.js")); stats["form_logic_sha256_dev"] = sha(os.path.join(DST, "form_logic.js"))
    stats["n_articles_in_index"] = len(arts)
    json.dump(stats, open(os.path.join(BASE, "trial", "mock_build_stats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in stats.items() if k != "per_level"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
