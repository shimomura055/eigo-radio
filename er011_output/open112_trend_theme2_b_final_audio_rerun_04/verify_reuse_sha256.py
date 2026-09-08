import hashlib
import json
import os

SRC = "er011_output/open112_trend_theme2_b_final_audio_rerun_03/b1b"
DST = "er011_output/open112_trend_theme2_b_final_audio_rerun_04/b1b"
SKIP_PREFIXES = ("narration/point_one", "narration/point_two")
SKIP_EXACT = ("audit/tts_generation_results.json",)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    matches = []
    mismatches = []
    for root, _dirs, files in os.walk(SRC):
        for fn in files:
            full_src = os.path.join(root, fn)
            rel = os.path.relpath(full_src, SRC).replace("\\", "/")
            full_dst = os.path.join(DST, rel)
            if not os.path.exists(full_dst):
                mismatches.append((rel, "MISSING_IN_DST"))
                continue
            if rel.startswith(SKIP_PREFIXES) or rel in SKIP_EXACT:
                continue
            h1 = sha(full_src)
            h2 = sha(full_dst)
            if h1 == h2:
                matches.append(rel)
            else:
                mismatches.append((rel, "HASH_MISMATCH"))

    print("matches:", len(matches))
    print("mismatches:", mismatches)
    with open("er011_output/open112_trend_theme2_b_final_audio_rerun_04/reuse_sha256_verification.json",
              "w", encoding="utf-8") as f:
        json.dump({"matches": matches, "mismatches": mismatches}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
