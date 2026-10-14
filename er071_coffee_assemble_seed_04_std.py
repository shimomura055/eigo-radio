"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04: Std正式assemble用の固定Master phrase seed(sha256 provenance記録、API呼出なし)。
runner `--stage assemble --level a2` は a2/narration に welcome/preview_intro/key_phrases_intro/full_story_intro/num_one..five を要求する
(Adv委任_03のseedと同じ設計)。welcome=A5/preview_intro=B5(Coffee承認済みIntro、Trial生成)、残りは既存Production承認済み(tone worktree
run_e_tone_01/a2/narration、Trial assembler std_sources()の『既存承認(変更なし)』と同一ファイル)をコピーする。再生成なし。
コピーしたsegmentはtts_generation_results.jsonに載らないためAudio Validation Gateの走査対象外(Adv seedと同じ限界、CHECKLIST_05に明記)。"""
import hashlib, json, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_m2p0_n01_01")
AEF = os.path.join(ROOT, "er057_output", "coffee_final_listening_tone_trial_01", "part_AEF", "raw")
TONE = "C:/Users/tensh/eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/a2/narration"
SRC = {"welcome": (f"{AEF}/A5.wav", "T"), "preview_intro": (f"{AEF}/B5.wav", "T")}
for n in ("key_phrases_intro", "full_story_intro", "num_one", "num_two", "num_three", "num_four", "num_five"):
    SRC[n] = (f"{TONE}/{n}.wav", "P")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    dst_dir = os.path.join(RUN, "a2", "narration")
    rec = {}
    for role, (src, origin) in SRC.items():
        dst = os.path.join(dst_dir, role + ".wav")
        if os.path.exists(dst):
            assert sha(dst) == sha(src), f"既存{dst}がsrcと不一致"
        else:
            shutil.copyfile(src, dst)
        rec[role] = {"src": src, "origin": origin, "sha256": sha(dst)}
    out = os.path.join(RUN, "audit", "seed_provenance_04_std_assemble.json")
    json.dump({"purpose": "Std正式assemble用 固定Master phrase seed(再生成なし)", "roles": rec}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("seeded", len(rec), "->", out)


if __name__ == "__main__":
    main()
