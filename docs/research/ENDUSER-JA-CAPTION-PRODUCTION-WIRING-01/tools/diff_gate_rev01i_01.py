"""ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01: 既公開dirの再produce前後の差分Gate(rev01-h->rev01-i。API 0想定。tools/ech02_diff_gate_01.pyの派生)。基準=git HEAD。
許可: enduser/app.js・style.css(rev01-iと一致)・index.html(旧index.htmlにbuild_rev01i_01.patch_htmlを適用した結果と一致)・build_info.json(API 0の証拠を検査)。data/article.jsonはbyte一致必須(改行差のみ許容。翻訳・ja_align・英文の変化はNG。Opus M-2)。
不可(あればNG): dev index.html・音声・enduser/data/sync_*.json・その他。
使い方: python diff_gate_rev01i_01.py <公開dir(repo相対)> ...  (終了コード0=全dir OK)"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[4]
_sp = importlib.util.spec_from_file_location('b', ROOT / 'enduser_page_assets' / 'build_rev01i_01.py')
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
    allowed = {f"{d}/enduser/{n}" for n in ("app.js", "style.css", "index.html", "build_info.json")}
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
    # article.json: byte一致必須(改行差のみ許容。Opus M-2)。差があれば内容を診断情報に付けてNG(翻訳の新規生成・ja_align変化も検出)
    oa, na = show(f"{d}/enduser/data/article.json"), (ROOT / d / "enduser" / "data" / "article.json").read_bytes()
    if oa is None or NL(oa) != NL(na):
        bad("data/article.json が旧版とbyte不一致(改行差以外の変化=翻訳/ja_align/英文の変化。再produceは文面不変でなければならない)")
        if oa is not None:
            o, n = json.loads(oa.decode("utf-8")), json.loads(na.decode("utf-8"))
            for lv in sorted(set(o["levels"]) | set(n["levels"])):
                op = {p_.get("key", p_.get("idx")): p_ for p_ in o["levels"].get(lv, {}).get("parts", [])}
                for p_ in n["levels"].get(lv, {}).get("parts", []):
                    q = op.get(p_.get("key", p_.get("idx")))
                    if q != p_:
                        res["translation_changes"].append(dict(level=lv, part=p_.get("key"), keys=sorted(k for k in set(p_) | set(q or {}) if p_.get(k) != (q or {}).get(k))))
    # API 0の証拠(build_info。Opus M-2): 翻訳・judge・埋め込みの呼出0、費用0
    bi = json.loads((ROOT / d / "enduser" / "build_info.json").read_text(encoding="utf-8"))
    c, ja = bi.get("cost", {}), bi.get("ja_align", {})
    emb = ja.get("embedding", {}) if isinstance(ja, dict) else {}
    res["api0"] = dict(asset_build=bi.get("asset_build"), api_calls=c.get("api_calls"), translate_api_calls=c.get("translate_api_calls"), translate_cost_jpy=c.get("translate_cost_jpy"),
                       embedding_api_calls=c.get("embedding_api_calls"), embedding_tokens=c.get("embedding_tokens"), embedding_cost_jpy=c.get("embedding_cost_jpy"),
                       judge_calls=(bi.get("judge") or {}).get("calls"), judge_cache_hits=(bi.get("judge") or {}).get("cache_hits"), embedding_cached_hits=emb.get("cached_hits"))
    for k in ("api_calls", "translate_api_calls", "embedding_api_calls", "embedding_tokens", "translate_cost_jpy", "embedding_cost_jpy"):
        if c.get(k) != 0:
            bad(f"build_info.cost.{k}={c.get(k)} (API 0でない)")
    if (bi.get("judge") or {}).get("calls") != 0:
        bad(f"build_info.judge.calls={(bi.get('judge') or {}).get('calls')} (API 0でない)")
    if bi.get("asset_build") != "rev01-i":
        bad(f"build_info.asset_build={bi.get('asset_build')}")
    return res


if __name__ == "__main__":
    allok = True
    for d in sys.argv[1:]:
        r = gate(d)
        allok = allok and r["ok"]
        print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if allok else 3)
