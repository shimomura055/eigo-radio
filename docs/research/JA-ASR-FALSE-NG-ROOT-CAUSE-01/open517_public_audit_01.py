# OPEN-517 R-2 過去公開物の監査抽出(API 0 / read-only。Production fileも出力も変更しない)。
# 抽出条件: 全run dirの tts_generation_results*.json の attempts_log[*].asr_judgement のうち
#   final_gate.skipped == "approved_equivalence:READING_MATCH" かつ value_guard.primary.kind == DIFF (判定はPASS = 採用された転写)
# 追加(参考): 同条件でvalue_guard kindがUNKNOWN/AMBIGUOUSのもの(F1後はUNKNOWNはPASSのまま、AMBIGUOUSはP3降格)。
# 追加(B節): 監査recordが無い旧run(統一judge導入前=2026-10-16以前、legacy A/B/C含む)も対象に、保存された(canonical, Primary転写)で
#   audio_classification in {PHONETIC_MATCH, READING_RESOLVED_MATCH} かつ verified の attempt を v4(F1+F2)の純関数 reading_match_final_gate で再判定し、PASS以外になる件を抽出(『もしF1+F2があれば止まった』件)。
# 公開物判定: そのsegmentの最終音声(segments[key].path / sha256)が user_test/ 配下のmp3/wavとsha256一致 -> 『公開物該当』。
#             sha不一致でも同run名・同segmentファイル名が user_test に存在すれば『名称一致(参考)』として別掲。
# 出力: open517_public_audit_01.out.json + 標準出力。再現: リポジトリrootで PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_public_audit_01.py
import collections, glob, hashlib, json, os, sys
sys.path.insert(0, ".")
D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
PASSING = ("PASS", "PASS_WITH_WARNING")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# user_test の全音声sha256 -> 相対path
ut = {}
ut_names = collections.defaultdict(list)
for p in glob.glob("user_test/**/*", recursive=True):
    if os.path.isfile(p) and p.lower().endswith((".mp3", ".wav", ".m4a")):
        pp = p.replace("\\", "/")
        ut[sha(p)] = pp
        ut_names[os.path.basename(pp)].append(pp)
print(f"user_test audio files: {sum(len(v) for v in ut_names.values())} (unique sha {len(ut)})")

files = sorted(set(glob.glob("er*_output/**/tts_generation_results*.json", recursive=True)))
hits, scanned, kinds = [], 0, collections.Counter()
nfiles_with_audit = 0
for p in files:
    try:
        d = json.load(open(p, encoding="utf8"))
    except Exception:
        continue
    segs = d.get("segments") if isinstance(d, dict) else None
    if not isinstance(segs, dict):
        continue
    had = False
    for key, s in segs.items():
        if not isinstance(s, dict):
            continue
        for a in s.get("attempts_log") or []:
            j = a.get("asr_judgement")
            if not isinstance(j, dict):
                continue
            had = True
            scanned += 1
            fg = j.get("final_gate") or {}
            sk = fg.get("skipped") or ""
            if j.get("state") not in PASSING or sk != "approved_equivalence:READING_MATCH":
                continue
            vk = ((j.get("value_guard") or {}).get("primary") or {}).get("kind")
            kinds[vk] += 1
            if vk in ("DIFF", "UNKNOWN", "AMBIGUOUS"):
                pr = j.get("primary") or {}
                final_sha = s.get("sha256")
                apath = a.get("attempt_audio_path")
                asha = j.get("audio_sha256")
                pub = ut.get(final_sha) or ut.get(asha)
                nm = []
                for cand in (s.get("path"), apath):
                    if cand:
                        nm += ut_names.get(os.path.basename(cand), [])
                hits.append({"file": p.replace("\\", "/"), "segment": key, "attempt": a.get("attempt"), "kind": vk,
                             "canon": s.get("canonical_text") or s.get("text"), "asr": pr.get("text"), "state": j.get("state"),
                             "reason": j.get("reason_code"), "pairs": [q for q in ((j.get("value_guard") or {}).get("primary") or {}).get("pairs", []) if q.get("verdict") != "EQUAL"],
                             "is_final_audio": bool(final_sha and asha and final_sha == asha),
                             "final_sha256": final_sha, "audio_sha256": asha, "public_sha_match": pub, "name_match_ref": sorted(set(nm))[:3]})
    nfiles_with_audit += had
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import proto_value_gate_fix_04 as F4
hitsB, scannedB = [], 0
for p in files:
    try:
        d = json.load(open(p, encoding="utf8"))
    except Exception:
        continue
    segs = d.get("segments") if isinstance(d, dict) else None
    if not isinstance(segs, dict):
        continue
    for key, s in segs.items():
        if not isinstance(s, dict) or s.get("language") != "ja":
            continue
        canon = s.get("canonical_text") or s.get("text")
        for a in s.get("attempts_log") or []:
            if a.get("audio_classification") not in ("PHONETIC_MATCH", "READING_RESOLVED_MATCH") or not a.get("verified") or not a.get("asr_text") or not canon:
                continue
            scannedB += 1
            j = a.get("asr_judgement") or {}
            asr = (j.get("primary") or {}).get("text") or a.get("asr_text")
            v = F4.reading_match_final_gate(canon, asr)
            if v.state == "PASS":
                continue
            final_sha, asha = s.get("sha256"), j.get("audio_sha256")
            pub = ut.get(final_sha) or (ut.get(asha) if asha else None)
            nm = []
            for cand in (s.get("path"), a.get("attempt_audio_path")):
                if cand:
                    nm += ut_names.get(os.path.basename(cand), [])
            hitsB.append({"file": p.replace("\\", "/"), "segment": key, "attempt": a.get("attempt"), "canon": canon, "asr": asr, "v4_state": v.state, "v4_reason": v.reason,
                          "had_judge_audit": bool(j), "judge_state": j.get("state"), "judge_skip": (j.get("final_gate") or {}).get("skipped"),
                          "is_final_audio": bool(final_sha and asha and final_sha == asha), "public_sha_match": pub, "name_match_ref": sorted(set(nm))[:3]})
print(f"[B節] 旧run含む PHONETIC_MATCH/READING_RESOLVED_MATCH verified attempt {scannedB}件をv4で再判定 -> PASS以外 {len(hitsB)}件")
for h in hitsB:
    print(f"  [B] {h['file']}#{h['segment']} att{h['attempt']} v4={h['v4_state']}/{h['v4_reason']} judge_audit={h['had_judge_audit']} final={h['is_final_audio']} public={h['public_sha_match']} names={h['name_match_ref']}")
    print(f"      canon={str(h['canon'])[:70]!r}")
    print(f"      asr  ={str(h['asr'])[:70]!r}")
print(f"tts_generation_results files: {len(files)} / with judge audit: {nfiles_with_audit} / judged attempts scanned: {scanned}")
print("READING_MATCH-skipped PASS by value_guard.primary kind:", dict(kinds))
diff = [h for h in hits if h["kind"] == "DIFF"]
print(f"DIFF hits: {len(diff)} (is_final_audio: {sum(1 for h in diff if h['is_final_audio'])}, public sha match: {sum(1 for h in diff if h['public_sha_match'])}, name-match only: {sum(1 for h in diff if h['name_match_ref'] and not h['public_sha_match'])})")
for h in hits:
    print(f" [{h['kind']}] {h['file']}#{h['segment']} att{h['attempt']} final={h['is_final_audio']} public={h['public_sha_match']} names={h['name_match_ref']}\n    canon={str(h['canon'])[:60]!r}\n    asr  ={str(h['asr'])[:60]!r}\n    pairs={h['pairs']}")
json.dump({"hitsB": hitsB, "scannedB": scannedB, "hits": hits, "kinds": dict(kinds), "scanned": scanned, "files": len(files), "files_with_audit": nfiles_with_audit}, open(D + "open517_public_audit_01.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
