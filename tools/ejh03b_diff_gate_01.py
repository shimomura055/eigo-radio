# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B: 既公開dirの再produce前後の差分Gate(API 0)。基準=git HEAD。

許可する差分 = (a) ja_align (b) 訳が無かったpartに付いた生成訳(ja/ja_source=generated/ja_align) (c) vocab[].audio と enduser/audio/*.mp3 (d) asset(app.js・style.css・index.htmlのbuild-id)
 (e) 同期の再測定による開始/終了秒の微小な差(sid集合は同一・|差|<=0.25s。E1のASR prompt是正の副作用) (f) build_infoの許可key。
承認済みの訳(approved_*)・英文(paragraphs)・Vocabulary本文・dev index.html・音声(dev audio)に差分があればNG。
使い方: .venv\\Scripts\\python.exe tools\\ejh03b_diff_gate_01.py <公開dir> [<公開dir> ...]  (終了コード0=全dir OK)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BI_ALLOWED = {"asset_build", "files", "assets", "ja_align", "cost", "warnings", "episode_check", "link_targets", "generated_translation", "judge", "vocab_audio",
              "translation_coverage", "sync"}
SYNC_TOL = 0.25
NL = lambda b: b.replace(b"\r\n", b"\n")   # noqa: E731


def git_show(rel: str) -> bytes | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def norm_article(art: dict) -> dict:
    """許可する差分(ja_align・生成訳・vocab音声)を除いた比較用の写し。承認済みの訳は残す。"""
    a = json.loads(json.dumps(art))
    for L in a["levels"].values():
        if not L.get("nuance"):
            L.pop("nuance", None)
        for v in L.get("vocab", []):
            v.pop("audio", None)
        for p in L["parts"]:
            p.pop("ja_align", None)
            if p.get("ja_source") == "generated":
                p.pop("ja", None)
                p.pop("ja_source", None)
    return a


def gate(pub: str) -> dict:
    d = Path(pub)
    rel = d.as_posix()
    res = {"dir": rel, "ok": True, "diffs": [], "notes": []}

    def bad(m):
        res["ok"] = False
        res["diffs"].append(m)
    old = git_show(f"{rel}/index.html")
    if old is None or NL(old) != NL((ROOT / d / "index.html").read_bytes()):
        bad("dev index.htmlが変化")
    maxd, nshift = 0.0, 0
    for p in sorted((ROOT / d / "enduser" / "data").glob("sync_*.json")):
        o = git_show(f"{rel}/enduser/data/{p.name}")
        if o is None:
            bad(f"{p.name}: 旧が無い")
            continue
        if NL(o) == NL(p.read_bytes()):
            continue
        oj, nj = json.loads(o.decode("utf-8")), json.loads(p.read_text(encoding="utf-8"))
        os_, ns_ = oj["sentences"], nj["sentences"]
        if [x["sid"] for x in os_] != [x["sid"] for x in ns_] or {k: v for k, v in oj.items() if k != "sentences"} != {k: v for k, v in nj.items() if k != "sentences"}:
            bad(f"{p.name}: sid集合/メタが変化")
            continue
        for a, b in zip(os_, ns_):
            dd = max(abs(a["start"] - b["start"]), abs(a["end"] - b["end"]))
            if dd > 1e-9:
                nshift += 1
                maxd = max(maxd, dd)
            if dd > SYNC_TOL:
                bad(f"{p.name}: {a['sid']}の秒が{dd:.3f}s変化(許容{SYNC_TOL})")
    res["notes"].append(f"同期の再測定差: {nshift}文・最大{maxd:.3f}s")
    oa = git_show(f"{rel}/enduser/data/article.json")
    na = json.loads((ROOT / d / "enduser" / "data" / "article.json").read_text(encoding="utf-8"))
    if oa is None:
        bad("旧article.jsonがgit HEADに無い(新規dirは別検査)")
    else:
        oj = json.loads(oa.decode("utf-8"))
        if norm_article(na) != norm_article(oj):
            bad("article.jsonに許可外の差分(英文/承認済み訳/Vocabulary本文/メタ等)")
        for lv, L in na["levels"].items():
            for p, po in zip(L["parts"], oj["levels"][lv]["parts"]):
                if po.get("ja_source") in ("approved_ja_manuscript", "approved_ja_original_in_dev_page") and (p.get("ja") != po.get("ja") or p.get("ja_source") != po.get("ja_source")):
                    bad(f"{lv} {p['key']}: 承認済みの訳が変化")
                if p.get("ja_source") == "generated" and po.get("ja_source") is not None:
                    bad(f"{lv} {p['key']}: 訳のあるpartに生成訳が付いた(再生成0の違反)")
        gen = [(lv, p["key"]) for lv, L in na["levels"].items() for p in L["parts"] if p.get("ja_source") == "generated"]
        aud = sum(1 for L in na["levels"].values() for v in L.get("vocab", []) if v.get("audio"))
        voc = sum(len(L.get("vocab", [])) for L in na["levels"].values())
        res["notes"].append(f"生成訳part={len(gen)} / Vocabulary音声={aud}/{voc}")
        if aud != voc:
            bad(f"Vocabulary音声が全件でない: {aud}/{voc}")
    ob = git_show(f"{rel}/enduser/build_info.json")
    nb = json.loads((ROOT / d / "enduser" / "build_info.json").read_text(encoding="utf-8"))
    if ob is None:
        bad("旧build_infoがgit HEADに無い")
    else:
        oj = json.loads(ob.decode("utf-8"))
        changed = {k for k in set(oj) | set(nb) if oj.get(k) != nb.get(k)}
        extra = changed - BI_ALLOWED
        if extra:
            bad(f"build_infoの想定外の差分key: {sorted(extra)}")
        for lv, v in (nb.get("sync") or {}).items():
            o = (oj.get("sync") or {}).get(lv) or {}
            if v.get("gate_status") != "PASS" or any(v.get(k) != o.get(k) for k in ("rows", "sentences", "gate_status", "engine", "model")):
                bad(f"build_info.sync[{lv}]: gate/rows/sentencesが変化 (new={v.get('gate_status')} min_row_ratio {o.get('min_row_ratio')}->{v.get('min_row_ratio')})")
        res["notes"].append("sync min_row_ratio " + str({lv: ((oj.get('sync') or {}).get(lv, {}).get('min_row_ratio'), v.get('min_row_ratio')) for lv, v in (nb.get('sync') or {}).items()}))
        res["notes"].append(f"build_info変化key: {sorted(changed)}")
    oi = git_show(f"{rel}/enduser/index.html")
    ni = (ROOT / d / "enduser" / "index.html").read_bytes()
    if oi is None or NL(oi).replace(b"rev01-e", b"rev01-g").replace(b"rev01-f", b"rev01-g") != NL(ni):
        bad("enduser/index.htmlがbuild-id以外で変化")
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
