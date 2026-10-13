# -*- coding: utf-8 -*-
"""委任_02 事前登録plan生成(JPY0、API呼出なし)。python ... --out-dir <dir>
設計: 動詞交絡の分離。名前{Melos,Brontes} x 動詞{s始まり: said/says/sighed ; 非s: replied/answered/asked} x L2固定 x level{std,adv} x take。
Melos 4take / Brontes 3take。Phrase Listなし追加条件(Azure)はMelos x said/replied のみ(nophrase=True)。"""
import os, json, argparse, hashlib

VERBS = {"s": ["said", "says", "sighed"], "ns": ["replied", "answered", "asked"]}
NAMES = {"Melos": 4, "Brontes": 3}
LEVELS = ("std", "adv")


def build():
    tasks = []
    for name, nt in NAMES.items():
        for vg, vs in VERBS.items():
            for v in vs:
                text = f"{name} {v}."
                for level in LEVELS:
                    for take in range(1, nt + 1):
                        tasks.append({"id": f"{name}_{v}_L2_{level}_t{take}", "name": name, "verb": v, "vgroup": vg,
                                      "boundary": "ss" if vg == "s" else "nss", "length": "L2", "level": level, "take": take,
                                      "text": text, "word_count": 2, "nophrase": bool(name == "Melos" and v in ("said", "replied")),
                                      "text_sha256": hashlib.sha256(text.encode()).hexdigest()})
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    t = build()
    plan = {"managed_id": "FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_02", "n_tasks": len(t),
            "tts_model": "gemini-3.8-flash-lite-tts", "voice": "Aoede", "tts_execution_mode": "STANDARD(sync)", "budget_jpy_guardrail": 25, "tasks": t}
    json.dump(plan, open(f"{a.out_dir}/plan_02.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(len(t), "tasks")


if __name__ == "__main__":
    main()
