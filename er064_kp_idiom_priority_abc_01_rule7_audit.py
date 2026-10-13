# FAMILY-X-KP-IDIOM-PRIORITY-ABC-TRIAL-01 項目4: Rule7(所有格・活用形の一般化)の決定論的監査(費用JPY0、API呼出なし、Production関数を読むだけ)
import json

import er003_key_words_canonicalization as kc

GEN = "generalize_person_dependent_reference"
# (label, key_phrase, display_phrase, source_span, normalization_reason)
CASES = [
    ("pump_its_fist: display=pump its fist -> key=pump one's fist (reason=generalize)", "pump one's fist", "pump its fist", "your wallet pumps its fist", GEN),
    ("pump_its_fist: display=pump its fist -> key=pump someone's fist (its->someone's)", "pump someone's fist", "pump its fist", "your wallet pumps its fist", GEN),
    ("pump_its_fist: display=pumps its fist -> key=pump one's fist (活用形+its同時変更)", "pump one's fist", "pumps its fist", "pumps its fist", GEN),
    ("pump_its_fist: display=pumps its fist -> key=pumps one's fist (活用形保持)", "pumps one's fist", "pumps its fist", "pumps its fist", GEN),
    ("pump_its_fist: display=pump its fist -> key=pump its fist (無変更)", "pump its fist", "pump its fist", "pumps its fist", None),
    ("pump_its_fist: display=pump its fist -> key=pump one's fist (reasonがgeneralize以外)", "pump one's fist", "pump its fist", "pumps its fist", "other"),
    ("hold_breath: display=hold one's breath(無変更, src=holding its breath)", "hold one's breath", "hold one's breath", "holding its breath", None),
    ("his->someone's: display=lose his temper -> key=lose someone's temper", "lose someone's temper", "lose his temper", "lose his temper", GEN),
    ("her->one's: display=bite her tongue -> key=bite one's tongue", "bite one's tongue", "bite her tongue", "bit her tongue", GEN),
    ("their->someone's: display=catch their attention -> key=catch someone's attention", "catch someone's attention", "catch their attention", "catch their attention", GEN),
    ("my->someone's: display=take my place -> key=take someone's place (OPEN-310)", "take someone's place", "take my place", "take my place", GEN),
    ("my->one's: display=take my place -> key=take one's place", "take one's place", "take my place", "take my place", GEN),
    ("its->someone's: display=in its own right -> key=in someone's own right", "in someone's own right", "in its own right", "in its own right", GEN),
    ("hidden_clock: display=its own hidden clock -> key=one's own hidden clock", "one's own hidden clock", "its own hidden clock", "its own hidden clock", GEN),
    ("hidden_clock: display=own hidden clock -> key=one's own hidden clock (語追加、語数不一致)", "one's own hidden clock", "own hidden clock", "its own hidden clock", GEN),
    ("loan_future: display=take out against the future -> key=loan against the future (辞書外の名詞追加)", "loan against the future", "take out against the future", "taken out against the future", "other"),
    ("loan_future: display=take out against the future -> key=a loan against the future", "a loan against the future", "take out against the future", "taken out against the future", "other"),
]
out = []
for label, key, disp, src, reason in CASES:
    v = kc.validate_canonicalization_item(key, disp, src, reason)
    out.append({"case": label, "key_phrase": key, "display_phrase": disp, "source_span": src, "normalization_reason": reason,
                "ok": v["ok"], "reasons": [r[:160] for r in v.get("reasons", [])],
                "person_generalization_valid": kc._is_valid_person_generalization(key, disp)})
    print(("OK     " if v["ok"] else "INVALID"), label)
json.dump({"cost_jpy": 0, "note": "Production関数kc.validate_canonicalization_itemを呼ぶのみ(修正なし)", "cases": out},
          open("er064_output/kp_idiom_priority_abc_01/rule7_audit_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
