# -*- coding: utf-8 -*-
"""Phase 2 事前登録plan生成(JPY0、API呼出なし)。python er069_..._mkplan.py --out-dir <dir>
設計: 3長さ(2/4/7語) x 2境界(s+sあり=said / なし=replied) x 4名前 x 2レベル(std/adv) x 3take = 144 task。
優先順(削る順の逆): P1=OOV3名 x {L2,L7} / P2=+L4 / P3=+CMU収録対照名(Kallis)。"""
import sys, os, json, argparse, hashlib

NAMES_OOV = ["Melos", "Brontes", "Pelias"]       # CMU未収録(cmudict実測)・語末s
NAME_CONTROL = "Kallis"                           # CMU収録の語末s名(OOV寄与の分離用対照)
VERB = {"ss": "said", "nss": "replied"}          # ss=名前語末s + said語頭s / nss=replied(語頭r)
LENGTHS = {"L2": "{n} {v}.", "L4": "{n} {v} to him.", "L7": "{n} {v}, looking straight at the ruler."}
TAKES = 3
LEVELS = ("std", "adv")


def build():
    tasks = []
    def add(name, L, prio):
        for bd in ("ss", "nss"):
            text = LENGTHS[L].format(n=name, v=VERB[bd])
            for level in LEVELS:
                for take in range(1, TAKES + 1):
                    tasks.append({"id": f"{name}_{bd}_{L}_{level}_t{take}", "name": name, "boundary": bd, "length": L,
                                  "level": level, "take": take, "text": text, "word_count": len(text.split()),
                                  "priority": prio, "text_sha256": hashlib.sha256(text.encode()).hexdigest()})
    for n in NAMES_OOV:
        for L in ("L2", "L7"):
            add(n, L, 1)
    for n in NAMES_OOV:
        add(n, "L4", 2)
    for L in ("L2", "L4", "L7"):
        add(NAME_CONTROL, L, 3)
    tasks.sort(key=lambda t: t["priority"])
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    tasks = build()
    plan = {"managed_id": "FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01", "n_tasks": len(tasks),
            "tts_model": "gemini-3.8-flash-lite-tts", "voice": "Aoede", "tts_execution_mode": "STANDARD(sync)",
            "std_style": "PD8+A2_SLOWER (er063 NARRATOR_FULL_STORY_STD) + 6%減速(er008)", "adv_style": "PD8 (er063 NARRATOR_FULL_STORY_ADV)",
            "budget_jpy_guardrail": 100, "tasks": tasks}
    json.dump(plan, open(f"{a.out_dir}/plan_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(len(tasks), "tasks")
    for p in (1, 2, 3):
        print(p, sum(1 for t in tasks if t["priority"] == p))


if __name__ == "__main__":
    main()
