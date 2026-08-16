# IRAN01 A2: Key Phrase Component生成 + Full Audio組み立て(継続実行)
import json

import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_a2_audio_generate as a2audio


def main():
    r2 = c.generate_key_phrase_components(a2audio.CONFIG)
    print("[IRAN01_A2] generate_key_phrase_components status:", r2["status"])
    if r2["status"] != "OK":
        failed = [k for k, v in r2["results"].items()
                  if v["standard"].get("status") != "OK" or v.get("trial", {}).get("status", "OK") != "OK"]
        print("[IRAN01_A2] 失敗:", failed)
        return

    r3 = a2audio.stage_assemble_local(a2audio.CONFIG)
    print("[IRAN01_A2] stage_assemble status:", r3["status"], "duration:", r3["duration_seconds"],
          "peak:", r3["peak"], "clipping:", r3["clipping_detected"])

    with open(f"{a2audio.OUT_DIR}/run_summary_audio.json", "w", encoding="utf-8") as f:
        json.dump({"key_phrase_components": r2["status"], "assemble": r3}, f, ensure_ascii=False, indent=2, default=str)
    print("[IRAN01_A2] 完了。")


if __name__ == "__main__":
    main()
