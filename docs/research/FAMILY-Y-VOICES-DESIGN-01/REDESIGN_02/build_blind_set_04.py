# -*- coding: utf-8 -*-
"""build_blind_set_04.py -- 委任_15 C: school main と repro の日本語3 Voiceを混ぜた盲検資料(BLIND_SET_04.md + BLIND_KEY_04.json)。LLM 0 call・費用0。
reproはtext-only run(Tension・英語なし)のため英語Stdは存在しない(追加実行は本委任の費用上限70円・有料run起動1回の制約で不可)。"""
import json
import random

TREE = "er110_output/family_y_persona_pipeline_01/school_phone_ban"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_02"
SEED = 20261025


def voices(run):
    d = json.load(open(f"{TREE}/{run}/s6_voices.json", encoding="utf-8"))
    return [d["final_voices"][s] for s in ("voice_1", "voice_2", "voice_3")]


def main():
    wf = json.load(open(f"{TREE}/main/world_frame_used.json", encoding="utf-8"))["world_frame"]
    wf2 = json.load(open(f"{TREE}/repro/world_frame_used.json", encoding="utf-8"))["world_frame"]
    assert wf == wf2, "world_frameがmain/reproで異なる"
    arts = [("school/new_main", voices("main")), ("school/new_repro", voices("repro"))]
    rnd = random.Random(SEED)
    rnd.shuffle(arts)
    md = ["# BLIND_SET_04: school_phone_ban 日本語Voice 盲検資料(委任_15 C)", "",
          "arm・run名は伏せています(対応は`BLIND_KEY_04.json`。評価完了までKeyを開かない)。各『記事』は3人のVoice本文(順序固定a,b,c)。",
          "評価は引用に基づいて行い、新しさ・珍しさでは評価しないでください。",
          "注記(事実): 2記事とも同じ題材・同じ世界設定のパイプライン出力。片方は先行のBLIND_SET_03で評価済みの文章と同一の可能性があります(再識別可能性は排除できない)。reproは text-only run のため英語Stdは含まれません。", "",
          "## 設問(各記事・各Voiceに回答。引用必須。BLIND_SET_03と同一)",
          "- A 当事者性: この人物が、この争点について語る自然な理由が本文から分かるか → あり / やや弱い / なし(根拠の引用)",
          "- B 主張の必然性: この人の経験・感情・価値観から、この主張が生まれることに納得できるか → 明確 / やや弱い / 弱い(不自然な箇所の引用)",
          "- 制度の取り違え: 争点の制度・規則を取り違えている箇所があれば引用(なければ『なし』)",
          "- Q: 『実在の人が自分の生活から語っているか』 → はい / どちらとも / いいえ(根拠の引用)",
          "- C(記事ごと): 3人を聞いて、単独では得られない対立・発見・面白さがあるか → あり / やや弱い / なし(具体)",
          "- 同型化: 3人の語りの展開・冒頭・結びが似ていないか → 似ている / 一部 / 似ていない(引用)",
          "- 記事間比較: どの記事が『実在の人が語っている』感が強いか、どの記事が『説明している』感が強いか。", ""]
    key = {"seed": SEED, "articles": {}}
    for i, (src, vs) in enumerate(arts, 1):
        lab = f"記事{chr(64 + i)}"
        key["articles"][lab] = {"source": src, "lang": "JA", "theme": "school"}
        md += [f"## {lab} (言語: 日本語、題材: school)", "", f"争点: {wf['question_ja']}", f"共通の前提: {wf['shared_premise_ja']}", ""]
        for k, v in enumerate(vs):
            md += [f"### {lab} Voice {'abc'[k]}", "", v, ""]
    open(f"{OUT}/BLIND_SET_04.md", "w", encoding="utf-8").write("\n".join(md))
    json.dump(key, open(f"{OUT}/BLIND_KEY_04.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK", [a[0] for a in arts])


if __name__ == "__main__":
    main()
