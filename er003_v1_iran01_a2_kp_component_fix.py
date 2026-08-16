# IRAN01 A2: Key Phrase Component "US sanctions"/"one-fifth" 個別修正
# (generate_key_phrase_component_verifiedはtext自身をexpected_substring
# として固定使用するため、"US"→"U.S."(ASRの略語正規化)や
# "one-fifth"→"1/5"(ASRの分数正規化)という既知パターンに対応できない。
# 音声内容自体は正しいため、より安定したexpected_substringで直接
# generate_narration_snippet_verified_strictを呼び直す)
import json

import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_a2_audio_generate as a2audio

components_dir = f"{a2audio.OUT_DIR}/key_phrase_components"

jobs = [
    ("Three", "US sanctions", f"{components_dir}/kp_Three_US_sanctions_standard.wav", "sanctions"),
    ("Four", "one-fifth", f"{components_dir}/kp_Four_one-fifth_standard.wav", "1/5"),
]

results = {}
for number, text, out_path, expected_substring in jobs:
    print(f"[IRAN01-A2-KP-FIX] {number}({text!r}) 再検証(expected_substring={expected_substring!r})...")
    r = c.generate_narration_snippet_verified_strict(text, "en", out_path, expected_substring,
                                                       max_attempts=6, max_extra_chars=10)
    results[number] = r
    print(f"[IRAN01-A2-KP-FIX] {number}: status={r.get('status')}")

with open(f"{a2audio.OUT_DIR}/audit/kp_component_fix_result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

with open(f"{a2audio.OUT_DIR}/audit/key_phrase_components_result.json", encoding="utf-8") as f:
    all_results = json.load(f)
for number, r in results.items():
    if r.get("status") == "OK":
        all_results[number]["standard"] = r
with open(f"{a2audio.OUT_DIR}/audit/key_phrase_components_result.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

failed = [k for k, v in results.items() if v.get("status") != "OK"]
print("完了。失敗:" if failed else "完了。全件成功。", failed if failed else "")
