# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_02 (M6): 既公開dirの再produce前後の差分Gate(API 0)。

許可する差分 = ja_align / build_info(asset_build・files・assets・ja_align・link_targets・generated_translation・cost・warnings) / asset(app.js・style.css。index.htmlは同一)。
それ以外(dev index.html・音声・sync_*.json・article.jsonのja_align以外・build_infoの上記以外のkey)に差分があればNG。
旧(基準)はgit HEAD。使い方: .venv\\Scripts\\python.exe tools\\ejh02_diff_gate_01.py <公開dir> [<公開dir> ...]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BI_ALLOWED = {"asset_build", "files", "assets", "ja_align", "cost", "warnings", "episode_check", "link_targets", "generated_translation"}
NL = lambda b: b.replace(b"\r\n", b"\n")   # noqa: E731  (git autocrlfの改行差は無視)


def git_show(rel: str) -> bytes | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def strip_align(art: dict) -> dict:
    a = json.loads(json.dumps(art))
    for L in a["levels"].values():
        if not L.get("nuance"):
            L.pop("nuance", None)             # 廃止済みnuanceの空配列(旧snapshot)は無視(NUANCE-CORNER-ABOLITION-01)
        for p in L["parts"]:
            p.pop("ja_align", None)
    return a


def gate(pub: str) -> dict:
    d = Path(pub)
    rel = d.as_posix()
    res = {"dir": rel, "ok": True, "diffs": [], "notes": []}

    def bad(m):
        res["ok"] = False
        res["diffs"].append(m)
    # dev index.html
    old = git_show(f"{rel}/index.html")
    if old is None or NL(old) != NL((ROOT / d / "index.html").read_bytes()):
        bad("dev index.htmlが変化")
    # sync / article / build_info
    for p in sorted((ROOT / d / "enduser" / "data").glob("sync_*.json")):
        o = git_show(f"{rel}/enduser/data/{p.name}")
        if o is None or NL(o) != NL(p.read_bytes()):
            bad(f"{p.name}が変化")
    oa = git_show(f"{rel}/enduser/data/article.json")
    na = json.loads((ROOT / d / "enduser" / "data" / "article.json").read_text(encoding="utf-8"))
    if oa is None:
        bad("旧article.jsonがgit HEADに無い")
    else:
        oj = json.loads(oa.decode("utf-8"))
        if strip_align(na) != strip_align(oj):
            bad("article.jsonにja_align以外の差分")
        n_old = sum(1 for L in oj["levels"].values() for p in L["parts"] if "ja_align" in p)
        n_new = sum(1 for L in na["levels"].values() for p in L["parts"] if "ja_align" in p)
        res["notes"].append(f"ja_alignを持つpart: 旧{n_old} -> 新{n_new}")
        # 訳が表示される部分の本文(paragraphs/ja)が不変であること(strip_alignで確認済み)
    ob = git_show(f"{rel}/enduser/build_info.json")
    nb = json.loads((ROOT / d / "enduser" / "build_info.json").read_text(encoding="utf-8"))
    if ob is None:
        bad("旧build_infoがgit HEADに無い")
    else:
        oj = json.loads(ob.decode("utf-8"))
        def norm(b):
            b = json.loads(json.dumps(b))
            for v in (b.get("sync") or {}).values():
                v.pop("source_sha256", None)           # 同期生出力のcanonical sha(sync_*.json自体の同一性は上で検査)
            return b
        changed = {k for k in set(oj) | set(nb) if norm(oj).get(k) != norm(nb).get(k)}
        extra = changed - BI_ALLOWED
        if extra:
            bad(f"build_infoの想定外の差分key: {sorted(extra)}")
        res["notes"].append(f"build_info変化key: {sorted(changed)}")
    # assets: index.htmlは同一、app.js/style.cssは更新(rev01-f)
    oi = git_show(f"{rel}/enduser/index.html")
    if oi is None or NL(oi) != NL((ROOT / d / "enduser" / "index.html").read_bytes()):
        bad("enduser/index.htmlが変化(assetのindex.htmlは変更しない設計)")
    # 音声参照(audio/ 等)は触っていない: git statusでenduser/外の変更が無いこと
    st = subprocess.run(["git", "status", "--short", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    outside = [ln for ln in st if "/enduser/" not in ln.replace("\\", "/")]
    if outside:
        bad(f"enduser/外の変更: {outside[:3]}")
    res["notes"].append(f"git status(enduser内の変更={len(st) - len(outside)}件)")
    return res


if __name__ == "__main__":
    allok = True
    for pub in sys.argv[1:]:
        r = gate(pub)
        allok = allok and r["ok"]
        print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if allok else 3)
