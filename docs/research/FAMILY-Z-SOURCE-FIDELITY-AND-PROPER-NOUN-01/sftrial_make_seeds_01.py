# -*- coding: utf-8 -*-
"""U1 Trial(委任_03): 『開いた窓』Seed修正版(T1/T2共通)をTrial dir内へ作る。Production seed.jsonは読むだけで無変更。"""
import json, hashlib, os, copy
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = f"{ROOT}/er026_output/family_z_production_e2e_01/the_open_window/seed"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/sftrial_seeds"
sha = lambda b: hashlib.sha256(b).hexdigest()
seed = json.load(open(f"{SRC}/seed.json", encoding="utf-8"))
new = copy.deepcopy(seed)

# (ii) conversion_plan: 命名の「only」を外し(名前はkey_roles側で指定)、結末定義に原作自身の最終文を明記
old_cp = seed["conversion_plan"]
new_cp = old_cp
rep = [
 ("with a nervous visitor (Framton Nuttel) as the only person with a personal name and role descriptions such as the girl (the niece), her aunt, the aunt's husband and her two brothers for the others.",
  "with a nervous visitor (Framton Nuttel) as the main character and role descriptions such as the girl (the niece), her aunt, the aunt's husband and her two brothers for the other people."),
 ("and the girl's smooth lie about the dog, which reveals that she made up the whole tragedy.",
  "the girl's smooth lie about the dog, which reveals that she made up the whole tragedy; and the narrator's own one-line last sentence of the original, that romance at short notice was her speciality."),
 ("and do not add a moral or an explanation after the last line; the surprise is the point.",
  "and do not add a moral or an explanation of your own after the last line. The original's own final sentence is not such an explanation: it is the closing line of the story and must be kept; the surprise is the point."),
]
for a, b in rep:
    assert a in new_cp, a[:40]
    new_cp = new_cp.replace(a, b)
new["conversion_plan"] = new_cp

# seed_elements[5]: 最終文を本文由来で明示(原作最終文)
new["seed_elements"][5] = ("The men come in, ordinary and muddy; the aunt says the visitor must have seen a ghost, and the girl calmly says "
  "he was afraid of the spaniel, backing it up with a vivid invented tale about his past; the story ends with the narrator's own last line "
  "(\"Romance at short notice was her speciality.\"), which shows that the girl invents stories on the spur of the moment.")

# (iii) discarded_elements: 少女の名前省略を除去
for i, d in enumerate(new["discarded_elements"]):
    if d.startswith("Names of minor people"):
        new["discarded_elements"][i] = ("Names of minor people other than the visitor and the girl (the aunt's name, the brothers' names), "
          "if a shorter version works better with roles such as her aunt, the aunt's husband and her two brothers")

# (i) essentials(修正版Bスキーマ。最大5キー。T1ではPromptが読まないので無効、T2のみ使用)
new["source_essentials"] = {
  "ending_reveal": {
    "meaning": "The story ends by showing that the girl, Vera, is someone who invents convincing stories on the spur of the moment: her last smooth lie about why Framton ran away proves that her tragic ghost story was invented too.",
    "source_quote": "Romance at short notice was her speciality.",
    "withhold_until_end": "Before the ending, do not hint at or explain that Vera's story about the open window is invented."
  },
  "setups_and_payoffs": [
    {"setup": "Vera's sad story: three years ago the aunt's husband and her two young brothers walked out through the open window and were lost in a bog; the aunt still keeps the window open; details are the husband's white coat, the youngest brother's song 'Bertie, why do you bound?' and the brown spaniel.",
     "payoff": "At dusk three figures with guns, a white coat and a spaniel cross the lawn and the song is heard; Framton runs away in terror; the men walk in, ordinary and muddy."}
  ],
  "key_roles": [
    {"name": "Framton", "role": "the nervous visitor and main character, who flees in terror", "keep_name": True},
    {"name": "Vera", "role": "the aunt's fifteen-year-old niece, who tells the false ghost story and then lies smoothly about the dog", "keep_name": True},
    {"role": "the girl's aunt, whose cheerful waiting for the men seems to confirm Vera's story", "keep_name": False}
  ],
  "key_causality": [
    "Vera's invented tragedy makes Framton believe the men are ghosts; the aunt's cheerful behavior seems to confirm it; the men's return makes Framton flee in terror; Vera then invents another story to explain why he ran."
  ],
  "free_to_cut": [
    "the sister's advice and the nerve-cure details, the shooting-trip small talk, the cyclist, and most of Framton's inner thoughts"
  ]
}
for k in ("t1", "t2"):
    os.makedirs(f"{OUT}/{k}", exist_ok=True)
    b = json.dumps(new, ensure_ascii=False, indent=2).encode("utf-8")
    open(f"{OUT}/{k}/seed.json", "wb").write(b)
    prov = {"story_key": "the_open_window", "task": "FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_03 U1 Trial (DEV copy; Production seed unchanged)",
            "arm": k, "derived_from_sha256": sha(open(f"{SRC}/seed.json", "rb").read()),
            "files": {"seed.json": {"sha256": sha(b)}}}
    json.dump(prov, open(f"{OUT}/{k}/SEED_PROVENANCE.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
