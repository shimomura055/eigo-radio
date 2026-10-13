# 読取専用: Wiktionary multiword targeted lookup(既存関数)を少数probeに1回だけ呼ぶ。LLM/TTS/ASRではなく無料の公開API(Production既存経路と同じ関数)。費用0。
import sys, os, json
sys.path.insert(0, os.getcwd())
import er023_key_phrase_db_ingest as ing
probes = ["time lag", "in the ring", "the ring", "raw beans", "raw bean", "price tag", "price measure", "bean prices", "pumps its fist",
          "hidden clock", "behind price", "push prices", "retail prices", "bad weather", "be behind", "time delay", "lead time"]
r = ing.wiktionary_multiword_targeted_lookup(probes)
json.dump({"results": r["results"], "api_calls": r["api_calls"]}, open("er064_output/kp_candidate_selection_design_01/wiktionary_probe_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(r["results"], r["api_calls"])
