# Trial-08 新選定文の日本語訳(T1 module er003_kp_source_sentence_ja_01 を読み取り利用。DEV。1 call・約0.03円)
import json, os, sys
BASE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er003_kp_source_sentence_ja_01 as ja
SENTS = ["Inventing convincing stories at a moment’s notice was Vera’s speciality.",
         "Wish him alive again!", "I wish Herbert alive again.",
         "A knock announced an old friend, a retired sergeant-major home from India.",
         "But that pale blue eye, covered by a thin film like a vulture’s, made his blood turn cold."]
res = ja.generate_translations(SENTS)
a = res["audit"]
json.dump({"model": a["model"], "prompt_sha256": a["prompt_sha256"], "response_ids": a["response_ids"], "cost_jpy": a["total_cost_jpy"],
           "pairs": [{"sentence": s, "ja": x["source_sentence_ja"]} for s, x in zip(SENTS, res["items"])]},
          open(os.path.join(BASE, "translations_08.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(a["total_cost_jpy"], [x["source_sentence_ja"] for x in res["items"]])
