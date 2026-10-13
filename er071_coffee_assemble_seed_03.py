"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03: Adv正式assemble用のnon-N01 segment seed(sha256 provenance記録、API呼出なし)。

runner `--stage assemble --level b1b` は、新out_dirにrunner生成segmentの一部(Full Story/KP)しか無いため
welcome/preview_intro/key_phrases_intro/full_story_intro/num_*/topic_intro/comment_1-4/preview/in_one_line が不足する。
これらは再生成せず、委任_02のAdv完成版組立(`coffee_build_02/assembly_manifest_m2p0_n01_02.json`)が使った
v5承認済み音声と同一のファイルを新out_dir/b1b/narration/へコピーする(sha256をaudit/seed_provenance_03_assemble.jsonへ記録)。
Gate・判定は一切触らない(コピーしたsegmentはtts_generation_results.jsonに載らないためAudio Validation Gateの走査対象外=
v5時点のvalidationはv5 runの記録に依存する。この限界はEVIDENCE_02に明記)。
"""
import hashlib
import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_m2p0_n01_01")
MANIFEST = os.path.join(ROOT, "er071_output", "m2p0_n01_production_wiring_01", "coffee_build_02", "assembly_manifest_m2p0_n01_02.json")
SEED_ROLES = ["welcome_charon", "preview_intro_charon", "key_phrases_intro_charon", "full_story_intro_charon",
              "num_one_charon", "num_two_charon", "num_three_charon", "num_four_charon", "num_five_charon",
              "topic_intro", "comment_1", "comment_2", "comment_3", "comment_4", "preview", "in_one_line"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    prov = json.load(open(MANIFEST, encoding="utf-8"))["levels"]["adv"]["provenance"]
    dst_dir = os.path.join(RUN, "b1b", "narration")
    rec = {}
    for role in SEED_ROLES:
        src = prov[role]["path"]
        dst = os.path.join(dst_dir, role + ".wav")
        if os.path.exists(dst):
            assert sha(dst) == prov[role]["sha256"], f"既存{dst}のshaがmanifestと不一致"
        else:
            shutil.copyfile(src, dst)
        assert sha(dst) == prov[role]["sha256"], f"{role}: copy後sha不一致"
        rec[role] = {"src": src, "origin": prov[role].get("origin"), "sha256": prov[role]["sha256"]}
    out = os.path.join(RUN, "audit", "seed_provenance_03_assemble.json")
    json.dump({"purpose": "Adv正式assemble用seed(再生成なし、委任_02 Adv完成版と同一sha)", "roles": rec},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("seeded", len(rec), "->", out)


if __name__ == "__main__":
    main()
