# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_02 Phase 3: offline再判定(API 0・Production無変更・読取専用)。
# 保存済みattempt記録(main working treeのer019_output/er026_output)のASR転写を、Flap層(Trial prototype)ON/OFFで再判定し、
# RESCUE候補attemptの音声(mp3)+転写の試聴ページを user_test/asr_flap_t_trial_01/ に出力する。
# 実行: PYTHONUTF8=1 <venv python> docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools/flapt_phase3_rejudge_02.py [--census <json>] [--allowlist <voice_probe_02.json>]
import argparse, glob, html, json, os, shutil, subprocess, sys, tempfile

sys.path.insert(0, "."); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flapt_equivalence_proto_01 as fl

BASE = "docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01"
MAIN = "C:/Users/tensh/eigo-radio"          # 保存wav/attemptはmain working tree(未commit)
PAGE = "user_test/asr_flap_t_trial_01"


def level_dir_of(src):
    return src.replace("\\", "/").rsplit("/audit/", 1)[0]


def find_canon(results_path, seg):
    d = json.load(open(results_path, encoding="utf-8"))
    tail = seg.split("/")[-1]
    found = []

    def rec(o, trail):
        if isinstance(o, dict):
            if (trail and trail[-1] == tail) and isinstance(o.get("canonical_text"), str):
                found.append(o["canonical_text"])
            for k, v in o.items():
                rec(v, trail + [str(k)])
        elif isinstance(o, list):
            for v in o:
                rec(v, trail)
    rec(d, [])
    return found[0] if found else None


def attempt_files(level_dir, seg):
    tail = seg.split("/")[-1]
    if tail == "vocab_extra_english":
        pat = "vocab_extra_3_en_attempt*.json"
    else:
        pat = f"{tail}_attempt*.json"
    return sorted(glob.glob(f"{MAIN}/{level_dir}/narration/attempts/{pat}"))


def mp3_from_wav(wav, mp3):
    import imageio_ffmpeg
    os.makedirs(os.path.dirname(mp3), exist_ok=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-b:a", "64k", mp3], check=True)


def pricing_cost(lines):
    import er019_family_x_audio_production_runner_01 as xr
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        p = f.name
    try:
        return xr.compute_cost_jpy_so_far(p)[0]
    finally:
        os.unlink(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", default=f"{BASE}/stored_census_02.json")
    ap.add_argument("--allowlist", default=f"{BASE}/voice_probe_02.json")
    a = ap.parse_args()
    census = json.load(open(a.census, encoding="utf-8"))
    allow = set(json.load(open(a.allowlist, encoding="utf-8"))["allowlist_proposal"]) if os.path.exists(a.allowlist) else set()
    groups = {}
    for r in census["RESCUE_examples"]:
        groups.setdefault((level_dir_of(r["src"]), r["seg"]), set()).add(r["attempt"])
    report = {"census": a.census, "allowlist_used": sorted(allow), "segments": [], "audio_candidates": []}
    cost_note = {}
    for (ldir, seg), _atts in sorted(groups.items()):
        results_path = f"{MAIN}/{ldir}/audit/tts_generation_results.json"
        canon = find_canon(results_path, seg)
        seg_rec = {"level_dir": ldir, "seg": seg, "canonical_head": (canon or "")[:100], "attempts": []}
        files = attempt_files(ldir, seg)
        for f in files:
            d = json.load(open(f, encoding="utf-8"))
            texts = {"openai": d.get("asr_text")}
            for st in d.get("cascade_steps") or []:
                if st.get("text"):
                    pv = str(st.get("provider", "?"))
                    texts["azure" if pv.startswith("azure") else ("openai" if pv.startswith("openai") else pv)] = st["text"]
            decs = {k: (fl.evaluate(canon, t) if canon and t else None) for k, t in texts.items()}
            dec_names = {k: (v.decision if v else None) for k, v in decs.items()}
            off_pass = bool(d.get("verified"))
            flap_votes = [k for k, v in dec_names.items() if v == "RESCUE"]
            other_ng = [k for k, v in dec_names.items() if v not in (None, "RESCUE", "NOT_APPLICABLE")]
            voice = d.get("voice")
            vkey = f"{voice}|{'fl' if 'flash-lite' in str(d.get('model')) else 'pro'}"
            on_pass = (not off_pass) and bool(flap_votes) and not other_ng and (vkey in allow)
            wav = f.replace(".json", ".wav")
            rec = {"attempt_file": os.path.relpath(f, MAIN).replace("\\", "/"), "attempt": d.get("attempt_number"), "voice": voice, "model": d.get("model"),
                   "asr": texts, "flap_decisions": dec_names, "off_verified": off_pass, "voice_path": vkey, "voice_in_allowlist": vkey in allow, "on_would_pass_with_warning": on_pass,
                   "wav_exists": os.path.exists(wav), "audio_sha256": d.get("sha256")}
            seg_rec["attempts"].append(rec)
            if on_pass and os.path.exists(wav):
                name = os.path.basename(wav).replace(".wav", ".mp3")
                key = ("X_" if "family_x" in ldir else "Z_") + ldir.replace("/", "_")[-40:] + "_" + name
                mp3_from_wav(wav, f"{PAGE}/audio/{key}")
                report["audio_candidates"].append({"mp3": f"audio/{key}", "canonical": canon, "seg": seg, "level_dir": ldir, "attempt": d.get("attempt_number"), "voice": voice,
                                                   "asr": texts, "decision": dec_names, "on_would_pass": on_pass})
        report["segments"].append(seg_rec)
    json.dump(report, open(f"{BASE}/phase3_rejudge_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # --- 費用突合(上限見積。attempt費用=telemetryのTTS+ASR実額/attempt数、救済で不要になるattempt数=最初のON通過attempt以降)---
    costs = {"segments": []}
    for seg_rec in report["segments"]:
        ldir, seg = seg_rec["level_dir"], seg_rec["seg"]
        atts = seg_rec["attempts"]
        first_on = next((i + 1 for i, x in enumerate(atts) if x["on_would_pass_with_warning"] or x["off_verified"]), None)
        n_att = len(atts)
        avoid_n = (n_att - first_on) if first_on else 0
        fam = "X" if "er019_output" in ldir else "Z"
        per_attempt = None
        src = None
        if fam == "X":
            theme_dir = ldir.rsplit("/", 1)[0]
            log = f"{MAIN}/{theme_dir}/raw_usage_log.jsonl"
            import re
            m = re.search(r"vocab_extra_(\d+)_en_attempt", atts[0]["attempt_file"]) if atts else None
            tag = f'"vocab_extra{m.group(1)}_english"' if m else None
            if tag and os.path.exists(log):
                ls = [l.strip() for l in open(log, encoding="utf-8") if tag in l]
                n_tts = max(sum(1 for l in ls if "gemini" in l and "tts" in l.lower() and "azure" not in l and "openai_asr" not in l), 1)
                tot = pricing_cost(ls) if ls else 0.0
                per_attempt, src = tot / n_tts, f"{theme_dir}/raw_usage_log.jsonl[{tag}]: {len(ls)} rec, {n_tts} tts, total {tot:.4f}"
        else:
            log = f"{MAIN}/{ldir.rsplit('/', 1)[0]}/cost_log.jsonl"
            tail = seg.split("/")[-1]
            if os.path.exists(log):
                ls = [l.strip() for l in open(log, encoding="utf-8") if f'"{tail}"' in l and '"perplexity"' not in l]
                n_tts = max(sum(1 for l in ls if "gemini-2.5-pro-preview-tts" in l), 1)
                tot = pricing_cost(ls) if ls else 0.0
                per_attempt, src = tot / n_tts, f"{ldir.rsplit('/', 1)[0]}/cost_log.jsonl[{tail}]: {len(ls)} rec, {n_tts} tts, total {tot:.4f}"
        costs["segments"].append({"family": fam, "level_dir": ldir, "seg": seg, "attempts": n_att, "first_on_pass_or_ok_attempt": first_on, "avoidable_attempts_upper": avoid_n,
                                  "per_attempt_jpy": round(per_attempt, 4) if per_attempt is not None else None,
                                  "avoidable_jpy_upper": round(avoid_n * per_attempt, 3) if per_attempt is not None else None, "cost_source": src})
    for fam in ("X", "Z"):
        costs[f"total_avoidable_jpy_upper_{fam}"] = round(sum(c["avoidable_jpy_upper"] or 0 for c in costs["segments"] if c["family"] == fam), 3)
    report["cost_reconciliation"] = costs
    json.dump(report, open(f"{BASE}/phase3_rejudge_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # --- 試聴ページ(判断対象=救済候補音声のみ)---
    rows = []
    for c in report["audio_candidates"]:
        asr = "<br>".join(f"{html.escape(k)}: <b>{html.escape(str(v))}</b>" for k, v in c["asr"].items() if v)
        rows.append(f"<tr><td><audio controls preload='none' src='{html.escape(c['mp3'])}'></audio></td><td>{html.escape(str(c['canonical'])[:160])}</td><td>{asr}</td>"
                    f"<td>{html.escape(str(c['voice']))}</td><td>{'PASS_WITH_WARNING(FLAP_T_EQUIVALENT)' if c['on_would_pass'] else '救済条件外(NG維持)'}</td></tr>")
    page = ("<!doctype html><meta charset='utf-8'><title>Flap-T救済 Trial 試聴</title>"
            "<style>body{font-family:sans-serif;margin:16px}td,th{border:1px solid #ccc;padding:6px;vertical-align:top}table{border-collapse:collapse}</style>"
            "<h2>Flap-T救済 Trial 確認(判断対象=救済候補の音声のみ)</h2>"
            "<p>確認していただきたいこと: 各音声が<b>想定した語を正しく発話しているか</b>(latter / Bertie など)。ASRが別の綴り(Ladder / Birdie)で書いても、耳で想定語に聞こえれば救済は正しい。"
            "別の語(ladder / Birdie)に聞こえる音声があれば、誤救済の例として教えてください。</p>"
            "<table><tr><th>音声</th><th>想定テキスト</th><th>ASR転写</th><th>Voice</th><th>Flap層ON時</th></tr>" + "".join(rows) + "</table>")
    os.makedirs(PAGE, exist_ok=True)
    open(f"{PAGE}/index.html", "w", encoding="utf-8").write(page)
    print(json.dumps({"segments": len(report["segments"]), "audio_candidates": len(report["audio_candidates"]), "cost": costs}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
