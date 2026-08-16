# IRAN01 B1: Key Phrase Component(英語Aoede)+日本語meaning(Charon)生成
# (先行のsegment生成が一部失敗し中断していたため、Key Phraseのみ継続実行)
import json

import er003_v1_iran01_articles_generate as gen
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = f"{gen.OUT_DIR}/b1"
NARRATION_DIR = f"{OUT_DIR}/narration"


def main():
    with open(f"{OUT_DIR}/key_phrases/keywords_canonicalized.json", encoding="utf-8") as f:
        kp_canon = json.load(f)

    kp_items = sorted(kp_canon["items"], key=lambda it: it["rank"])
    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[IRAN01-B1-KP] Key Phrase {rank} 英語Component生成(Aoede): {used_form!r}...")
        en_path = f"{NARRATION_DIR}/kp{rank}_en.wav"
        en_result = repro01.generate_key_phrase_component_verified(used_form, en_path)
        print(f"[IRAN01-B1-KP] Key Phrase {rank} 日本語meaning生成(Charon): {ja_gloss!r}...")
        ja_path = f"{NARRATION_DIR}/kp{rank}_ja_charon.wav"
        ja_result = voice01.generate_charon_japanese(ja_gloss, ja_path, ja_gloss[:4])
        kp_results[rank] = {"english": en_result, "japanese": ja_result}
        print(f"[IRAN01-B1-KP] Key Phrase {rank}: en={en_result.get('status')} ja={ja_result.get('status')}")

    with open(f"{OUT_DIR}/audit/key_phrase_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(kp_results, f, ensure_ascii=False, indent=2, default=str)

    kp_failed = [r for r, v in kp_results.items()
                 if v["english"].get("status") != "OK" or v["japanese"].get("status") != "OK"]
    print("完了。失敗:" if kp_failed else "完了。全件成功。", kp_failed if kp_failed else "")


if __name__ == "__main__":
    main()
