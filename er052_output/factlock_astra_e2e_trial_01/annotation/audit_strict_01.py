# -*- coding: utf-8 -*-
"""注記者transcriptの厳格監査(b3_annotator_audit_01.py の audit() を呼び、さらに『許可パス以外のtool_use』も違反にする)。
決定論・API支出0・既存スクリプト非編集。CLI: --transcript <jsonl> --annotator A|B --out <json> [--max-reads N]
終了コード: PASS=0 / VIOLATION=1"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import b3_annotator_audit_01 as base  # noqa: E402

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True); ap.add_argument("--annotator", required=True, choices=["A", "B"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = json.load(open(os.path.join(HERE, "audit_config.json"), encoding="utf-8"))["annotators"][a.annotator]
    allow = cfg["allow_substrings"]
    allow_both = allow + [x.replace("/", chr(92)) for x in allow]  # Windowsの区切りも許可語に含める
    text = open(a.transcript, encoding="utf-8").read()
    res = base.audit(text, allow_both)
    # 基底スクリプトは解釈できない行を黙って捨てるため、ここで検出して違反扱いにする(監査の見逃し防止)
    unparsed = 0
    try:
        json.loads(text.strip())
    except ValueError:
        for ln in text.splitlines():
            if ln.strip():
                try:
                    json.loads(ln)
                except ValueError:
                    unparsed += 1
    res["unparseable_lines"] = unparsed
    norm = lambda p: p.replace("\\", "/")
    extra = []
    for r in res["tool_uses"]:
        ok = r["tool"] == "Read" and r["targets"] and all(any(norm(t).endswith(x) for x in allow) for t in r["targets"])
        if not ok:
            extra.append({"tool": r["tool"], "targets": r["targets"], "reason": "許可パス(自分のプロンプトのRead)以外"})
    res["strict_violations"] = extra
    res["verdict"] = "VIOLATION" if (res["violations"] or extra or unparsed) else ("PASS_NO_TOOL_USE" if not res["tool_use_count"] else "PASS_ONLY_ALLOWED_READS")
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(res["verdict"], res["tool_use_count"])
    return 1 if res["verdict"] == "VIOLATION" else 0

if __name__ == "__main__":
    sys.exit(main())
