# -*- coding: utf-8 -*-
"""build_blind_set_03.py -- 委任_14 T-4: Opus/Fable主評価用の盲検資料(BLIND_SET_03.md + BLIND_KEY_03.json)を、実行済みartifactから決定論で生成する。
arm・run名を伏せ、記事(3 Voiceの組)をラベルなしで混在。校正センチネル=旧V1(良)/旧V2・V3(弱い)。LLM 0 call・費用0。
使い方: py build_blind_set_03.py
"""
import json
import os
import random
import re

TREE = "er110_output/family_y_persona_pipeline_01"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_02"
OLD_SCHOOL_JA = "er110_output/family_y_persona_trial_01/school_phone_ban/it3/article_ja.md"
OLD_SCHOOL_EN = "er110_output/family_y_persona_trial_01/school_phone_ban/it3/english/a2/article.md"
OLD_OFFICE_EN = "er012_output/editorial_b_voices_a2_free_address_04/a2/article.md"
SEED = 20261024


def read(p):
    return open(p, encoding="utf-8").read()


def jap_paras(text):
    return [x.strip() for x in re.split(r"\n\s*\n", text.strip()) if x.strip()]


def old_school_ja():
    ps = jap_paras(read(OLD_SCHOOL_JA))
    return ps[1:4]          # 1行目はタイトル。Voice 3段落(V1,V2,V3)


def old_school_en():
    ps = jap_paras(read(OLD_SCHOOL_EN))
    return ps[1:4]


def old_office_en():
    t = read(OLD_OFFICE_EN)
    v1 = re.search(r"### One Voice:[^\n]*\n\n(.*?)\n\n### Another Voice", t, re.S).group(1).strip()
    v2 = re.search(r"### Another Voice:[^\n]*\n\n(.*?)\n\n## ", t, re.S).group(1).strip()
    return [v1, v2]


def new_voices(theme, run_id):
    p = f"{TREE}/{theme}/{run_id}/s6_voices.json"
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    return [d["final_voices"][s] for s in ("voice_1", "voice_2", "voice_3")]


def new_std_en(theme, run_id):
    p = f"{TREE}/{theme}/{run_id}/english/a2/article.md"
    if not os.path.exists(p):
        return None
    ps = jap_paras(read(p))
    return ps[1:4]


def main():
    rnd = random.Random(SEED)
    articles = []       # (key_source, lang, theme, premise_ja, voices)
    sc = json.load(open(f"{TREE}/school_phone_ban/main/world_frame_used.json", encoding="utf-8"))["world_frame"] if os.path.exists(f"{TREE}/school_phone_ban/main/world_frame_used.json") else None
    of = json.load(open(f"{TREE}/office_seating/main/world_frame_used.json", encoding="utf-8"))["world_frame"] if os.path.exists(f"{TREE}/office_seating/main/world_frame_used.json") else None
    if sc:
        articles += [("school/new_main", "JA", "school", sc, new_voices("school_phone_ban", "main")),
                     ("school/new_repro", "JA", "school", sc, new_voices("school_phone_ban", "repro")),
                     ("school/old_it3 (V1=良,V2/V3=弱い のセンチネル)", "JA", "school", sc, old_school_ja()),
                     ("school/new_main_Std", "EN", "school", sc, new_std_en("school_phone_ban", "main")),
                     ("school/old_it3_Std", "EN", "school", sc, old_school_en())]
    if of:
        articles += [("office/new_main", "JA", "office", of, new_voices("office_seating", "main")),
                     ("office/new_main_Std", "EN", "office", of, new_std_en("office_seating", "main")),
                     ("office/old_2V_A2 (旧B承認の2 Voice)", "EN", "office", of, old_office_en())]
    articles = [a for a in articles if a[4]]
    rnd.shuffle(articles)
    labels = {}
    md = ["# BLIND_SET_03: Opus/Fable主評価用の盲検資料(委任_14 T-4)", "",
          "arm・run名・新旧は伏せています(対応は`BLIND_KEY_03.json`。評価完了までKeyを開かない)。各『記事』は3人(office旧稿のみ2人)のVoice本文です。記事内のVoiceの順序は固定(a,b,c)。",
          "評価は引用に基づいて行い、新しさ・珍しさでは評価しないでください。", "",
          "## 設問(各記事・各Voiceに回答。引用必須)",
          "- A 当事者性: この人物が、この争点について語る自然な理由が本文から分かるか → あり / やや弱い / なし(根拠の引用)",
          "- B 主張の必然性: この人の経験・感情・価値観から、この主張が生まれることに納得できるか → 明確 / やや弱い / 弱い(不自然な箇所の引用)",
          "- 制度の取り違え: 争点の制度・規則を取り違えている箇所があれば引用(なければ『なし』)",
          "- Q: 『実在の人が自分の生活から語っているか』 → はい / どちらとも / いいえ(根拠の引用)",
          "- C(記事ごと): 3人を聞いて、単独では得られない対立・発見・面白さがあるか → あり / やや弱い / なし(具体)",
          "- 同型化: 3人の語りの展開・冒頭・結びが似ていないか → 似ている / 一部 / 似ていない(引用)",
          "- 記事間比較(同じ題材・同じ言語の記事どうし): どの記事が『実在の人が語っている』感が強いか、どの記事が『説明している』感が強いか。", ""]
    key = {"seed": SEED, "articles": {}}
    for i, (src, lang, theme, wf, voices) in enumerate(articles, 1):
        lab = f"記事{chr(64 + i)}"
        key["articles"][lab] = {"source": src, "lang": lang, "theme": theme}
        md += [f"## {lab} (言語: {'日本語' if lang == 'JA' else 'English(Standard)'}、題材: {theme})", ""]
        md += [f"争点: {wf['question_ja']}", f"共通の前提: {wf['shared_premise_ja']}", ""]
        for k, v in enumerate(voices):
            md += [f"### {lab} Voice {'abc'[k]}", "", v, ""]
    open(f"{OUT}/BLIND_SET_03.md", "w", encoding="utf-8").write("\n".join(md))
    json.dump(key, open(f"{OUT}/BLIND_KEY_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("articles:", len(articles), [a[0] for a in articles])


if __name__ == "__main__":
    main()
