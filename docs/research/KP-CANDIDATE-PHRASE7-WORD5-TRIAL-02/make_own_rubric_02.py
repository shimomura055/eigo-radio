# -*- coding: utf-8 -*-
"""自ルーブリック(前回DESIGN_01 §7のR2〜R5・Y/B/Nを変更せず適用)。own_rubric_01.json を引き継ぎ、Trial-02で新規に現れた形だけを追加評価する。
judge(gpt-6.1-sol)の出力を見る前に確定(judge出力は未参照)。③④適合列(adv_fit)は note の機械規則で導出(下記)。"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(HERE, "..", "KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01", "own_rubric_01.json")

NEW = {
    "monkeys_paw:a2": {
        "pulling free": ("B", "pull freeの現在分詞形のまま(切り出しがやや不自然)"),
        "funeral": ("B", "基本寄り(R4やや易)"),
        "drag": ("Y", "B2動詞。汎用"),
    },
    "monkeys_paw:b1b": {
        "accept no responsibility": ("Y", "定番のコロケーション"),
        "pulled free": ("B", "pull freeの過去形のまま(切り出しがやや不自然)"),
    },
    "uk_train_speaker_playback:a2": {
        "given written permission": ("B", "過去分詞givenが余剰。written permissionが核"),
        "campaign": ("B", "基本寄り(R4やや易)"),
        "entertainment": ("B", "基本寄り(R4やや易)"),
    },
    "uk_train_speaker_playback:b1b": {
        "nationwide": ("Y", "B2形容詞/副詞。汎用"),
        "recommendations": ("B", "基本寄り(R4やや易)。複数形"),
        "carriage": ("B", "基本寄り・英国寄りの意味"),
    },
}

if __name__ == "__main__":
    prev = json.load(open(PREV, encoding="utf-8"))
    out = {k: dict(v) for k, v in prev.items()}
    for k, d in NEW.items():
        for f, (v, n) in d.items():
            assert f not in out[k] and f.lower() not in {x.lower() for x in out[k]}, (k, f)
            out[k][f] = {"verdict": v, "note": n, "new_in_trial02": True}
    json.dump(out, open(os.path.join(HERE, "own_rubric_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({k: len(v) for k, v in out.items()})
