# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_02 Phase 2 集計(API 0)。probe_02/results.jsonl + probe_02b/results.jsonl -> voice_probe_02.json / VOICE_PROBE_02.md
# 実行: PYTHONUTF8=1 <venv python> docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools/flapt_probe_analyze_02.py
import collections, json, os, re, sys

BASE = "docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01"
SHARDS = [f"{BASE}/probe_02", f"{BASE}/probe_02b"]
OBSERVABLE = ["latter", "metal", "betting", "atom", "waiting", "coating", "the latter one"]   # d綴り対応語があり、d綴り転写でflapが可視化できる項目
ER_ITEMS = ["latter", "writer", "better", "water", "the latter one"]
STORED_EVIDENCE = {("Aoede", "fl"): "FX4 vocab latter->Ladder(flash-lite)", ("Zephyr", "pro"): "FZ Bertie->Birdie(2.5-pro)", ("Schedar", "pro"): "FZ Bertie->Birdie(2.5-pro)"}
SYSTEMS = ["openai", "azure", "whisper"]


def load():
    rows = []
    for d in SHARDS:
        p = f"{d}/results.jsonl"
        if os.path.exists(p):
            for line in open(p, encoding="utf8"):
                rows.append(json.loads(line))
    return rows


def nonrhotic_hint(canon, text):
    toks = re.findall(r"[A-Za-z']+", text or "")
    ctoks = re.findall(r"[A-Za-z']+", canon)
    if not toks:
        return False
    last = toks[-1].lower() if canon.split()[-1].lower().endswith("er") else None
    if canon == "the latter one":
        return False
    return bool(last) and not last.endswith(("er", "or", "ar", "re")) and last.endswith(("a", "ah", "uh", "o"))


def main():
    rows = [r for r in load() if r.get("status") == "OK"]
    bad = [r for r in load() if r.get("status") != "OK"]
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["voice"], r["path"], r["variant"])].append(r)
    out = {"voices": {}, "slow6": {}, "failed_clips": [{k: b.get(k) for k in ("clip_key", "status", "reason")} for b in bad]}
    tbl = []
    for (voice, path, variant), rs in sorted(by.items()):
        items = {r["item"]: r for r in rs}
        obs = {}
        exact_clean = 0
        for it in OBSERVABLE:
            r = items.get(it)
            if not r:
                continue
            cls = r["class"]
            n_d = sum(1 for s in SYSTEMS if cls.get(s) == "FLAP_D")
            n_ex = sum(1 for s in SYSTEMS if cls.get(s) == "EXACT")
            obs[it] = {"flap_d_systems": n_d, "exact_systems": n_ex, "class": cls, "asr": {s: r["asr"][s]["text"] for s in SYSTEMS}, "clip_sha256": r["clip_sha256"]}
            if n_ex >= 2:
                exact_clean += 1
        observed_items = [it for it, o in obs.items() if o["flap_d_systems"] >= 2]
        any_d_items = [it for it, o in obs.items() if o["flap_d_systems"] >= 1]
        if len(observed_items) >= 2:
            verdict = "FLAP_DEMONSTRATED"
        elif not any_d_items and exact_clean >= 5:
            verdict = "T_SPELLED"
        else:
            verdict = "INDETERMINATE"
        nr = sum(1 for it in ER_ITEMS if it in items for s in SYSTEMS if nonrhotic_hint(it, items[it]["asr"][s]["text"]))
        ay = items.get("writer")
        rec = {"voice": voice, "path": path, "variant": variant, "model": rs[0]["model"], "voice_sent": rs[0]["voice_sent"], "clips": len(rs),
               "observable_items_run": len(obs), "observed_flap_items(>=2 systems)": observed_items, "any_flap_items(>=1 system)": any_d_items,
               "exact_clean_items(>=2 systems)": exact_clean, "verdict": verdict, "nonrhotic_hint_count": nr,
               "writer_asr": {s: ay["asr"][s]["text"] for s in SYSTEMS} if ay else None, "items": obs,
               "cost_asr_jpy": round(sum(r.get("asr_cost_jpy", 0) for r in rs), 3)}
        if variant == "normal":
            out["voices"][f"{voice}|{path}"] = rec
        else:
            out["slow6"][f"{voice}|{path}"] = rec
    # (Voice, TTS path)別の最終判定。許可は(Voice,path)単位=probeでFLAP_DEMONSTRATED、または保存記録で実証済みのpathのみ。未検証の組合せは不適用(fail-closed)。
    final = {}
    for key, rec in out["voices"].items():
        final[key] = {"probe_verdict": rec["verdict"], "clips": rec["clips"], "stored_evidence": STORED_EVIDENCE.get((rec["voice"], rec["path"]))}
    for (v, pth), ev in STORED_EVIDENCE.items():
        final.setdefault(f"{v}|{pth}", {"probe_verdict": "NOT_PROBED_PATH", "clips": 0, "stored_evidence": ev})
    for key, f in final.items():
        probe_ok = f["probe_verdict"] == "FLAP_DEMONSTRATED"
        f["allow"] = probe_ok or bool(f["stored_evidence"])
        f["basis"] = "probe+stored" if probe_ok and f["stored_evidence"] else "probe" if probe_ok else "stored" if f["stored_evidence"] else "none"
    out["final_by_voice_path"] = final
    out["allowlist_proposal"] = sorted(k for k, f in final.items() if f["allow"])
    out["not_applicable_tested"] = sorted(k for k, f in final.items() if not f["allow"])
    tested_voices = {k.split("|")[0] for k in final}
    allv = ["Aoede", "Zephyr", "Schedar", "Charon", "Algieba", "Fenrir", "Orus", "Puck", "Kore", "Erinome", "Leda", "Sulafat", "Iapetus"]
    out["untested_voices"] = [v for v in allv if v not in tested_voices]
    out["untested_voice_paths_note"] = "許可リストに無い(Voice,path)組合せ=未検証=不適用。例: Algieba|pro(Z本番で使用)・Charon|pro・Puck|pro・Fenrir|pro・Aoede|pro は未probe"
    json.dump(out, open(f"{BASE}/voice_probe_02.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    # markdown用表
    print(json.dumps({"allowlist": out["allowlist_proposal"], "na": out["not_applicable_tested"], "untested": out["untested_voices"],
                      "table": {k: (r["verdict"], len(r["observed_flap_items(>=2 systems)"]), len(r["any_flap_items(>=1 system)"]), r["exact_clean_items(>=2 systems)"], r["clips"], r["nonrhotic_hint_count"]) for k, r in out["voices"].items()},
                      "slow": {k: (r["verdict"], len(r["observed_flap_items(>=2 systems)"]), len(r["any_flap_items(>=1 system)"]), r["clips"]) for k, r in out["slow6"].items()}}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
