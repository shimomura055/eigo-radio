# -*- coding: utf-8 -*-
"""build_blind_set_05.py -- 委任_18 G: 新稿(実在意見ベース)・旧方式school main・旧it3 の日本語3 Voiceを混ぜた盲検資料(BLIND_SET_05.md + BLIND_KEY_05.json)と、
同一の機械指標(ローカル正規表現)を新旧に当てた表(structure_metrics_05.json)。LLM 0 call・API費用0。
指標の正規表現は本ファイルで固定し、結果を見て調整していない(1回実行)。構造タグ(LLM判定)は、旧main/reproは各runに記録済みの同一判定器(gpt-6-luna)の最終タグ、新稿も同じ判定器の記録、it3は記録が無いためagent判定。"""
import json
import random
import re
import sys

sys.path.insert(0, ".")
import er110_family_y_opinion_based_01 as ob       # event_like を再利用(同じ判定を新旧に適用)

TREE = "er110_output/family_y_persona_pipeline_01/school_phone_ban"
NEW = "er110_output/family_y_opinion_based_01/sns_age_limit/run_01"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01"
B3 = "docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_02/BLIND_SET_03.md"
SEED = 20261026
SLOTS = ("voice_1", "voice_2", "voice_3")

NEG_OPEN_RE = re.compile(r"(けど|けれど|じゃなくて|ではなく|わけじゃ|わけではない|じゃない|ではない|違う|っていうか)")
CONTRAST_RE = re.compile(r"(でも|けど|けれど|ただ|それでも|いや、|とはいえ|かといって|だからって)")
EVENT2_RE = re.compile(r"(ことがある|ことがあった|あった)")
WEAK_RE = re.compile(r"(正直|自分も|私も|俺も|僕も|情けな|楽に|楽を|都合|わがまま|甘い|言い訳)")
STANCE_RE = re.compile(r"(べき|ほしい|ほしくない|賛成|反対|ほうがいい|思う)")


def sents(t):
    return [s.strip() for s in re.split(r"(?<=[。！？!?])", t) if s.strip()]


def metrics(t):
    ss = sents(t)
    first = ss[0] if ss else ""
    contrast = len(CONTRAST_RE.findall(t))
    ev = [i for i, s in enumerate(ss) if ob.event_like(s) or EVENT2_RE.search(s)]
    wk = [i for i, s in enumerate(ss) if WEAK_RE.search(s)]
    ct = [i for i, s in enumerate(ss) if CONTRAST_RE.search(s)]
    st = [i for i, s in enumerate(ss) if STANCE_RE.search(s) and i >= len(ss) - 2]
    typ = False
    for e in ev:
        for w in [x for x in wk if x > e]:
            for c in [x for x in ct if x > w]:
                if [x for x in st if x > c]:
                    typ = True
    return {"opening_negation": bool(NEG_OPEN_RE.search(first)), "first_sentence": first, "contrast_turns": contrast, "event_weak_but_stance_type": typ,
            "chars": len(t), "n_sentences": len(ss)}


def load_run(run):
    d = json.load(open(f"{TREE}/{run}/s6_voices.json", encoding="utf-8"))
    tags = d["structure_tags_after"]["tags"] if d.get("structure_tags_after") else d["structure_tags_before"]["tags"]
    return [d["final_voices"][s] for s in SLOTS], [tags[s] for s in SLOTS]


def load_it3():
    md = open(B3, encoding="utf-8").read()
    sec = md.split("## 記事F (言語: 日本語、題材: school)")[1].split("## 記事G")[0]
    vs = re.findall(r"### 記事F Voice [abc]\n\n(.*?)(?=\n\n### |\n\n## |\Z)", sec, re.S)
    assert len(vs) == 3
    return [v.strip() for v in vs]


# it3のagent判定(記録のないためagentが全文を読んで付与。判定器ではない)
IT3_TAGS_AGENT = [
    {"opening_type": "主張・意見の表明から", "development_type": "自分への突っ込みと本音を行き来する", "closing_type": "自嘲・告白で締める"},
    {"opening_type": "自分の状況・立場の描写から", "development_type": "問いを重ねて考える", "closing_type": "問いを残して締める"},
    {"opening_type": "主張・意見の表明から", "development_type": "主張から具体例へ", "closing_type": "約束・要求で締める"},
]


def main():
    new = json.load(open(f"{NEW}/voices_final.json", encoding="utf-8"))
    st = json.load(open(f"{NEW}/state.json", encoding="utf-8"))
    new_v = [new[s] for s in SLOTS]
    new_tags = [st["structure"]["tags_before"]["tags"][s] for s in SLOTS]
    main_v, main_tags = load_run("main")
    repro_v, repro_tags = load_run("repro")
    it3_v = load_it3()
    arms = {"new_opinion_based": (new_v, new_tags, "luna記録(同一判定器)"), "old_school_main": (main_v, main_tags, "luna記録(同一判定器、再生成後の最終タグ)"),
            "old_school_repro": (repro_v, repro_tags, "luna記録(同一判定器、再生成後の最終タグ)"), "old_it3": (it3_v, IT3_TAGS_AGENT, "agent判定(記録なし)")}
    res = {}
    for k, (vs, tags, how) in arms.items():
        rows = []
        for v, t in zip(vs, tags):
            m = metrics(v)
            m.update({"opening_type": t["opening_type"], "development_type": t["development_type"], "closing_type": t["closing_type"]})
            rows.append(m)
        res[k] = {"tag_source": how, "voices": rows,
                  "n_opening_negation": sum(r["opening_negation"] for r in rows), "n_type_event_weak_but_stance": sum(r["event_weak_but_stance_type"] for r in rows),
                  "mean_contrast_turns": round(sum(r["contrast_turns"] for r in rows) / 3, 2),
                  "same_development_pairs": sum(1 for i in range(3) for j in range(i + 1, 3) if rows[i]["development_type"] == rows[j]["development_type"]),
                  "same_closing_pairs": sum(1 for i in range(3) for j in range(i + 1, 3) if rows[i]["closing_type"] == rows[j]["closing_type"]),
                  "same_opening_pairs": sum(1 for i in range(3) for j in range(i + 1, 3) if rows[i]["opening_type"] == rows[j]["opening_type"])}
    json.dump(res, open(f"{OUT}/structure_metrics_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    wf_school = json.load(open(f"{TREE}/main/world_frame_used.json", encoding="utf-8"))["world_frame"]
    import er110_family_y_opinion_based_01 as o
    topics = {"new_opinion_based": (o.WORLD_FRAME["question_ja"], o.WORLD_FRAME["shared_premise_ja"], "SNS"),
              "old_school_main": (wf_school["question_ja"], wf_school["shared_premise_ja"], "school"), "old_it3": (wf_school["question_ja"], wf_school["shared_premise_ja"], "school")}
    order = ["new_opinion_based", "old_school_main", "old_it3"]
    rnd = random.Random(SEED)
    rnd.shuffle(order)
    md = ["# BLIND_SET_05: 実在意見ベース新稿 vs 旧方式(school main / 旧it3) 日本語Voice 盲検資料(委任_18 G)", "",
          "arm名は伏せています(対応は`BLIND_KEY_05.json`。評価完了までKeyを開かない)。各『記事』は3人のVoice本文(順序固定a,b,c)。評価は引用に基づいて行い、新しさ・珍しさでは評価しないでください。",
          "**注記(盲検の限界。事実)**: (1)記事ごとに**題材が異なる**(子どものSNS年齢制限 / 高校のスマホ使用制限)ため、題材から方式を推定できる。評価者(Fable)は方式を知り得る立場で、**完全な盲検ではない**。(2)題材差があるため、『面白さ』『対立軸の自然さ』『リアリティの一部』は題材差と分けられない。方式差として読めるのは出典忠実性・同型化指標・手作業の有無(`COMPARISON_DESIGN_01.md`で事前区分)。(3)結論は『方式差の示唆』であり、証明ではない。", "",
          "## 設問(各記事・各Voiceに回答。引用必須。BLIND_SET_03/04と同一)",
          "- A 当事者性: この人物が、この争点について語る自然な理由が本文から分かるか → あり / やや弱い / なし(根拠の引用)",
          "- B 主張の必然性: この人の経験・感情・価値観から、この主張が生まれることに納得できるか → 明確 / やや弱い / 弱い(不自然な箇所の引用)",
          "- 制度の取り違え: 争点の制度・規則を取り違えている箇所があれば引用(なければ『なし』)",
          "- Q: 『実在の人が自分の生活から語っているか』 → はい / どちらとも / いいえ(根拠の引用)",
          "- C(記事ごと): 3人を聞いて、単独では得られない対立・発見・面白さがあるか → あり / やや弱い / なし(具体)",
          "- 同型化: 3人の語りの展開・冒頭・結びが似ていないか → 似ている / 一部 / 似ていない(引用)",
          "- 記事間比較: どの記事が『実在の人が語っている』感が強いか、どの記事が『説明している』感が強いか。", ""]
    key = {"seed": SEED, "note": "Fableは方式を知り得る(題材から推定可能)。完全な盲検ではない", "articles": {}}
    for i, a in enumerate(order, 1):
        lab = f"記事{chr(64 + i)}"
        q, prem, th = topics[a]
        vs = arms[a][0]
        key["articles"][lab] = {"source": a, "lang": "JA", "theme": th}
        md += [f"## {lab} (言語: 日本語)", "", f"争点: {q}", f"共通の前提: {prem}", ""]
        for j, v in zip("abc", vs):
            md += [f"### {lab} Voice {j}", "", v.strip(), ""]
    open(f"{OUT}/BLIND_SET_05.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    json.dump(key, open(f"{OUT}/BLIND_KEY_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: {x: v[x] for x in v if x != "voices"} for k, v in res.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
