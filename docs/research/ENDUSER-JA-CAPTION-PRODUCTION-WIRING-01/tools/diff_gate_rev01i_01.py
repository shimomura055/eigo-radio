"""ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01: 既公開dirの再produce前後の差分Gate(rev01-h->rev01-i。API 0想定。tools/ech02_diff_gate_01.pyの派生)。基準=git HEAD。
許可: enduser/app.js・style.css(rev01-iと一致)・index.html(旧index.htmlにbuild_rev01i_01.patch_htmlを適用した結果と一致)・build_info.json・data/article.json(英文・承認済み訳・既存ja不変)。
不可(あればNG): dev index.html・音声・enduser/data/sync_*.json・その他。
使い方: python diff_gate_rev01i_01.py <公開dir(repo相対)> ...  (終了コード0=全dir OK)"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[4]
_sp = importlib.util.spec_from_file_location('b', Path(__file__).with_name('build_rev01i_01.py'))
B = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(B)
NL = lambda b: b.replace(b"\r\n", b"\n")   # noqa: E731


def show(rel):
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def changed_files(d):
    out = subprocess.run(["git", "diff", "--ignore-cr-at-eol", "--name-only", "--", d], cwd=ROOT, capture_output=True, text=True).stdout.split()
    un = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", d], cwd=ROOT, capture_output=True, text=True).stdout.split()
    return sorted(set(x.replace("\\", "/") for x in out + un))


def gate(d):
    res = {"dir": d, "ok": True, "ng": [], "translation_changes": []}
    bad = lambda m: (res["ng"].append(m), res.__setitem__("ok", False))   # noqa: E731
    ch = changed_files(d)
    allowed = {f"{d}/enduser/{n}" for n in ("app.js", "style.css", "index.html", "build_info.json", "data/article.json")}
    for f in ch:
        if f not in allowed:
            bad(f"想定外の変更file: {f}")
    res["changed"] = ch
    for n in ("app.js", "style.css"):
        if NL((ROOT / d / "enduser" / n).read_bytes()) != NL((ROOT / "enduser_page_assets" / "rev01-i" / n).read_bytes()):
            bad(f"enduser/{n}がrev01-iと不一致")
    oi, ni = show(f"{d}/enduser/index.html"), (ROOT / d / "enduser" / "index.html").read_bytes()
    if oi is None or B.patch_html(NL(oi).decode("utf-8")).encode("utf-8") != NL(ni):
        bad("enduser/index.htmlが旧index.html+patch_html(rev01-i)と不一致")
    # article.json
    oa, na = show(f"{d}/enduser/data/article.json"), (ROOT / d / "enduser" / "data" / "article.json").read_bytes()
    if oa is not None and NL(oa) != NL(na):
        o, n = json.loads(oa.decode("utf-8")), json.loads(na.decode("utf-8"))
        for lv in sorted(set(o["levels"]) | set(n["levels"])):
            ol, nl = o["levels"].get(lv, {}), n["levels"].get(lv, {})
            for k in set(ol) | set(nl):
                if k != "parts" and ol.get(k) != nl.get(k):
                    bad(f"{lv}.{k}が変化")
            op = {p["key"] if "key" in p else p.get("idx"): p for p in ol.get("parts", [])}
            for p in nl.get("parts", []):
                q = op.get(p["key"] if "key" in p else p.get("idx"))
                if q is None:
                    bad(f"{lv} part追加")
                    continue
                if p == q:
                    continue
                keys = {k for k in set(p) | set(q) if p.get(k) != q.get(k)}
                if p.get("paragraphs") != q.get("paragraphs"):
                    bad(f"{lv} {p.get('key')}: 英文(paragraphs)が変化")
                if q.get("ja_source") != "generated" and (q.get("ja") or p.get("ja")) and p.get("ja") != q.get("ja"):
                    if q.get("ja"):
                        bad(f"{lv} {p.get('key')}: 既存のja(承認済み/生成)が変化")
                res["translation_changes"].append(dict(level=lv, part=p.get("key"), keys=sorted(keys), before_ja=bool(q.get("ja")), after_ja=bool(p.get("ja")), after_source=p.get("ja_source")))
    return res


if __name__ == "__main__":
    allok = True
    for d in sys.argv[1:]:
        r = gate(d)
        allok = allok and r["ok"]
        print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if allok else 3)
