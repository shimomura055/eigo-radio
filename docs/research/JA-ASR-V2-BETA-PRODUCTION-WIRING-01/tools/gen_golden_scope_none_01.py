# -*- coding: utf-8 -*-
# JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: scope外(=Family A/B/C・単体呼出)出力byte同一の金型(golden)生成。
# 使い方: 配線前HEAD(git worktree)とカレントの両方で同じscriptを実行し、出力JSONを比較する(API 0・socket guard・Reading Resolver無効)。
#   cd <repo or worktree> && PYTHONUTF8=1 <repo>/.venv/Scripts/python.exe -X utf8 <this script> <out.json>
# 入力: docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_03.out.json の rows(2103行: 正例/負例/不明)から決定的に抽出 + 月6本の決定対。
import hashlib, json, os, socket, sys, tempfile, wave

sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
import er007_ja_secondary_asr_01 as sec

MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
MOON_PAIRS = [
    ("月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。", "月野市は8900本越え。その奥に潜む岩の上着の秘密。"),
    ("月の死は八千九百本超。その奥に潜む岩の上着の秘密。", "月の詩は8900本超。その奥に潜む岩の上着の秘密。"),
    ("月の氏は8000900本超。その奥に潜む岩の上着の秘密。", "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"),
    ("月野氏は8,900本超。その奥に潜む岩の上着の秘密", "月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。"),
    ("月の詩は八千九百本超。その奥に潜む岩の上着の秘密", "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。"),
    ("スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。", "Sukino氏は8900本超。その奥に潜む岩の上着の秘密。"),
]
VOLATILE = {"timing", "timestamp", "wall_seconds", "total_ms", "secondary_ms", "ms", "created_at"}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def wav():
    p = os.path.join(tempfile.gettempdir(), "ja_v2beta_golden_dummy.wav")
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b"\x00\x00" * 16000 * 3); w.close()
    return p


def main(out):
    rows = json.load(open("docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_03.out.json", encoding="utf-8"))["rows"]
    items = [(MOON, p, s) for p, s in MOON_PAIRS]
    for i, r in enumerate(rows):
        if i % 11 == 0 and r["canon"] and r["primary"]:
            items.append((r["canon"], r["primary"], r["secondary"]))
    w = wav()
    real = socket.socket.connect
    socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("API0 violation"))
    res = []
    orig = sec._azure_stt_strict
    try:
        for canon, prim, sc in items:
            sec._azure_stt_strict = (lambda p, language="ja-JP", timeout_seconds=90, _s=sc: (_s, None)) if sc is not None else \
                (lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_secondary"))
            for ctx in ({"max_len": 400}, {"max_len": 400, "is_last_slot": True}):
                r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, w, cascade_enabled=True, attempt_ctx=dict(ctx))
                res.append({"canon": canon, "primary": prim, "secondary": sc, "ctx": ctx,
                            "verified": r["verified"], "stop_retrying": r["stop_retrying"], "final_status": r["final_status"],
                            "human_review_required": r["human_review_required"], "cascade_invoked": r["cascade_invoked"],
                            "classification": r["classification"].classification, "steps": strip(r["steps"]), "asr_judgement": strip(r["asr_judgement"])})
    finally:
        sec._azure_stt_strict = orig
        socket.socket.connect = real
    s = json.dumps(res, ensure_ascii=False, sort_keys=True, indent=1, default=str)
    open(out, "w", encoding="utf-8", newline="\n").write(s)
    print("rows", len(res), "sha256", hashlib.sha256(s.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main(sys.argv[1])
