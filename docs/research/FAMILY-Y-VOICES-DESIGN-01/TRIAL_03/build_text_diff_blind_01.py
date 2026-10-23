# -*- coding: utf-8 -*-
"""TRIAL_03 T-2: TEXT_DIFF_01.md / BLIND_PAIRS_02.md / BLIND_KEY_02.json を生成する(API 0、決定論。乱数seed固定)。"""
import difflib
import json
import random
import re
import sys

sys.path.insert(0, "C:/Users/tensh/eigo-radio")
B = "er110_output/family_y_persona_trial_01/school_phone_ban"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_03"


STRENGTHS_MD = """## 0. 保持する長所と修正の方針
### 保持する長所(根拠: TRIAL_02_RESULT_01 §5 E2/E4/E5、Fable評価[DECISION_LOG 2026-10-23 委任_09「具体的出来事・感情・明確な主張が立ち3人の語り口差が明確」]、ユーザーのV1高評価)
※Opus blind対比較の結果ファイルは本リポジトリ内に見当たらず未入手(BLIND_PAIRS_01に回答が残っていない)。長所リストは上記の記録から導出。
1. V1: 「俺だけが悪者にならずに済む」の主張 → 居間の充電カゴ・取り上げた翌朝の食卓の沈黙 → 「私だけ返事が遅れると外される」に言い返せなかった → 「楽になりたいだけな気もする」の自己矛盾 → 「家じゃ段取りも組めない現場監督だ、俺は。」の自嘲の締め。短い断言の連続。
2. V2: 「眠い、って。頭が痛い、って。」の断片、枕元で光る画面、昼間に取り上げられて来なくなった子、「来ないのと、つらくないのは同じなんだろうか」、最後の問いかけ。
3. V3: 休み時間に来るシフト連絡 → 返事が遅いと仕事が回される → 授業中の着信が続いて減らされかけた → 「仕事か学校かなんて、選びたくない」 → 約束(授業中は鞄の奥)+要求(決める前に聞いてほしい)の締め。
4. 3人の聞き分け: 一人称(俺/私/僕)・語り出し(主張/場面/主張)・締めの型(自嘲的断言/問い/約束+要求)。
5. 数字・調査説明・「！」・役割語を持ち込まない(Researchは裏方)。
### 修正対象と理由
| # | 修正 | 理由 |
|---|---|---|
| 1 | 規則の文言(V1冒頭、V2の「学校が…預かって」、V3冒頭・末尾、Tension、タイトル) | 世界設定の再設計(WORLD_SETTING_01.md: 朝回収・下校返却→休み時間・昼休みも含む校内使用の範囲) |
| 2 | V1「居間の充電カゴに入れると決めたのに守られず、…取り上げた翌朝の食卓では、娘と口をききづらかった」を2文に分けて主語を明確化。「取り上げた翌朝の食卓で、娘と口をききづらかった」 | ねじれた文(主語の切り替わり)。内容は不変 |
| 3 | V1「親父みたいに」→「うちの親父みたいに」 | 誰の親か不明確 |
| 4 | V1「ただ、昼間預けさせても夜の家は変わらないのに、学校に頼んで…」→2文に分割 | 逆接「のに」の長いねじれ。「それでも楽になりたいだけ」という自己矛盾はそのまま |
| 5 | V3「休憩中に」→「授業の合間の休み時間に」、長い1文(約45字)を2文に分割(「だから、」で受ける) | 仕事の休憩と学校の休み時間の曖昧さ除去、V3の中程度の短文リズムの回復 |
| 6 | V2に「先生に『スマホを禁止にしたら、保健室に来る子は減る？』と聞かれて、私は答えに詰まった」を1文追加 | なぜ養護教諭がこの件で発言するのか(職務・先生との関係)を自然に示す。回収の担当ではない |
| 7 | Tension+Closing全面差替(it2の具体的な構成[3つの具体物・「？」で終わる具体的な問い]を新設定に合わせて作成) | 初回稿のTensionは「暮らしや通学が苦しくなる」など抽象語が先行(ITERATION_LOG_01 it1原因分析3) |
| 8 | 英語: LLM訳の意味ずれ・誤用を手修正(「規則が既にある」と読める誤訳、「each other」「stop talking to us」等) | llm_original/との差分。Std/Advの文長・語彙差は維持 |
"""


def rd(p):
    return open(p, encoding="utf-8").read()


def ja_paras(it):
    t = rd(f"{B}/{it}/article_ja.md").strip().split("\n\n")
    return t[1:5]      # [title, v1, v2, v3, tension]


def en_split(it, lvl):
    import er110_family_y_persona_text_trial_01 as p
    s = p.split_en_article(rd(f"{B}/{it}/english/{lvl}/article.md"))
    return s["title"], s["paragraphs"], s["in_one_line"]


def sents(t, lang):
    if lang == "ja":
        return [x for x in re.split(r"(?<=[。？！])(?!」)", t) if x.strip()]
    return [x for x in re.split(r"(?<=[.!?])\s+", t.strip()) if x.strip()]


def diff_block(a, b, lang):
    sa, sb = sents(a, lang), sents(b, lang)
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    lines = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag in ("replace", "delete"):
            for x in sa[i1:i2]:
                lines.append(f"- (初回稿) {x}")
        if tag in ("replace", "insert"):
            for x in sb[j1:j2]:
                lines.append(f"+ (修正稿) {x}")
    kept = sum(i2 - i1 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag == "equal")
    return lines, kept, len(sa), len(sb)


def main():
    old_ja, new_ja = ja_paras("it1"), ja_paras("it3")
    labels = ["V1(父・Algieba)", "V2(養護教諭・Zephyr)", "V3(定時制の生徒・Schedar)", "Tension+Closing(Narrator)"]
    md = ["# TEXT_DIFF_01: 初回稿(it1)→修正稿(it3)の差分(日本語/Standard/Advanced)\n",
          "Status: DEV/Trial。LLM Writerを呼ばず手修正(初回稿を基準、世界設定整合・ねじれた文の是正)。Tension+Closingのみ、it2の具体的な構成を新設定へ合わせて作成。",
          "凡例: `-`=初回稿のみ、`+`=修正稿のみ(文単位。同一文は省略)。「維持文数」=同一のまま残った文の数。\n"]
    md.append(STRENGTHS_MD)
    md.append("## 1. 日本語\n")
    for i, lab in enumerate(labels):
        lines, kept, na, nb = diff_block(old_ja[i], new_ja[i], "ja")
        md.append(f"### {lab}: 初回稿{na}文 → 修正稿{nb}文、維持文数 {kept}\n")
        md.append("```\n" + "\n".join(lines) + "\n```\n")
    for lvl, name in (("a2", "Standard"), ("b1b", "Advanced")):
        t0, p0, i0 = en_split("it1", lvl)
        t1, p1, i1 = en_split("it3", lvl)
        md.append(f"## {'2' if lvl == 'a2' else '3'}. {name}(英語)\n")
        md.append(f"- タイトル: 初回稿 `{t0}` → 修正稿 `{t1}`\n")
        for i, lab in enumerate(labels):
            lines, kept, na, nb = diff_block(p0[i], p1[i], "en")
            md.append(f"### {lab}: 初回稿{na}文 → 修正稿{nb}文、維持文数 {kept}\n")
            md.append("```\n" + "\n".join(lines) + "\n```\n")
        md.append(f"### In one line\n```\n- (初回稿) {i0}\n+ (修正稿) {i1}\n```\n")
    open(f"{OUT}/TEXT_DIFF_01.md", "w", encoding="utf-8", newline="\n").write("\n".join(md))

    # ---------------- blind pairs
    rng = random.Random(20261023)
    pairs = {}
    def add(pid, desc, first, final):
        order = ["first", "final"]
        rng.shuffle(order)
        pairs[pid] = {"description": desc, "Text 1": order[0], "Text 2": order[1], "_text": {"first": first, "final": final}}

    add("P1", "日本語・3人の語り(Voice部分のみ)", "\n\n".join(old_ja[:3]), "\n\n".join(new_ja[:3]))
    for lvl, name, pid in (("a2", "英語(Standard)", "P2"), ("b1b", "英語(Advanced)", "P3")):
        _, p0, _ = en_split("it1", lvl)
        _, p1, _ = en_split("it3", lvl)
        add(pid, f"{name}・3人の語り(Voice部分のみ)", "\n\n".join(p0[:3]), "\n\n".join(p1[:3]))
    add("P4", "日本語・最後のまとめ(1パート)※初回稿のまとめは抽象語が多い版(it1)、修正稿はit2の具体的な構成を新設定に合わせた版", old_ja[3], new_ja[3])
    _, p0, _ = en_split("it1", "a2")
    _, p1, _ = en_split("it3", "a2")
    add("P5", "英語(Standard)・最後のまとめ(1パート)", p0[3], p1[3])

    out = ["# BLIND_PAIRS_02: 順序ランダム・ラベルなしの対比較(初回稿 vs 修正稿、本文のみ)\n",
           "各対の2つの文章(Text 1 / Text 2)を読み、次の問いに答えてください。どちらが修正されたものかは伏せてあります。設計意図・人物設定・世界設定の議論は渡していません。\n",
           "- Q1. どちらのほうが「実在の人が自分の生活から語っている」と感じるか(個性・感情・具体性・主張の明確さ)",
           "- Q2. どちらのほうが「優等生が丁寧に説明している」感が強いか",
           "- Q3(まとめの対 P4/P5 のみ). 耳で一度聞いて分かりやすいのはどちらか",
           "- Q4. 日本の高校の話として、制度・生活の描写に不自然な点があるのはどちらか(あれば該当箇所)",
           "- 回答形式: 対ごとに Q1/Q2(/Q3)/Q4: Text 1 か Text 2、理由1〜2文\n"]
    for pid, d in pairs.items():
        out.append(f"\n---\n\n## {pid}({d['description']})\n")
        for tx in ("Text 1", "Text 2"):
            out.append(f"### {tx}\n\n{d['_text'][d[tx]]}\n")
    open(f"{OUT}/BLIND_PAIRS_02.md", "w", encoding="utf-8", newline="\n").write("\n".join(out))
    key = {"note": "正解キー(Opus/Fable評価者には渡さない)。Text 1/Text 2の正体。first=初回稿(it1)、final=修正稿(it3)", "seed": 20261023,
           "key": {pid: {"description": d["description"], "Text 1": d["Text 1"], "Text 2": d["Text 2"]} for pid, d in pairs.items()}}
    json.dump(key, open(f"{OUT}/BLIND_KEY_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", {k: (v["Text 1"], v["Text 2"]) for k, v in pairs.items()})


if __name__ == "__main__":
    main()
