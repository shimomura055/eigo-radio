# -*- coding: utf-8 -*-
"""B3 V0 brief 12本に Fact Lock 用の注記(事実ID【事実1】、数値印【中核数値】/【周辺数値】)を付ける。
原本は読み取りのみ。出力: briefs/<slug>/b<i>/selected_brief_factlock.md, core_numbers.json, briefs/ANNOTATION_LOG.md
実行: .venv/Scripts/python.exe -X utf8 er052_output/factlock_writer_trial_01/tools/annotate_briefs.py
"""
import json, os, re, sys
sys.path.insert(0, ".")
import er052_factlock_writer_trial_01_run as h

SRC = "er052_output/open233_b3_trial_01/runs/{slug}/nb/V0/b{i}/storyline_b3/selected_brief.md"
OUT = "er052_output/factlock_writer_trial_01/briefs"
C, P = "core", "peri"

# 各briefの判断: items = 中核数値の概念(literals=briefに現れる表記、記事あたり最大3), peri = 周辺数値リテラル, why = 1行理由
HORMUZ_WHY = ("中核=20％(提案の中身)、約2.6％と1バレル85ドル(価格が高止まりした根拠)。日付・時刻は『翌日』等の定性語が"
              "台帳側にあり読者に不要なため周辺。")
SPACE_WHY = ("中核=配備発言の日付、ロシアの試験日、1,500個超のデブリ(『軌道上配備との区別』を伝える軸)。"
             "衛星名の番号・2025年framework・条約の条番号は固有名/出典の細部で読者に不要なため周辺。")
SPEC = {}
for i in (1, 2, 3, 4):
    SPEC[("meta", i)] = dict(core=[], peri=[], why="briefに数値なし(ID表記MUSE-HC-nnnは台帳IDで数値ではない)。中核0。")
SPEC[("hormuz", 1)] = dict(core=[("C1", ["20％"], "提案内容"), ("C2", ["約2.6％"], "上げ幅"), ("C3", ["1バレル85ドル"], "価格水準")],
                           peri=["7月13日午前10時16分", "7月14日午前11時4分"], why=HORMUZ_WHY)
SPEC[("hormuz", 2)] = dict(core=[("C1", ["20％"], "提案内容"), ("C2", ["約2.6％"], "上げ幅"), ("C3", ["1バレル85ドル"], "価格水準")],
                           peri=["7月13日午前10時16分", "7月14日午前11時4分", "7月13日", "14日"], why=HORMUZ_WHY + " storyline内の7月13日/14日も周辺。")
SPEC[("hormuz", 3)] = SPEC[("hormuz", 1)]
SPEC[("hormuz", 4)] = dict(core=[("C1", ["20％"], "提案内容"), ("C2", ["約2.6％"], "上げ幅"), ("C3", ["1バレル85ドル"], "価格水準")],
                           peri=["7月13日", "7月14日", "7.29ドル", "9.59％", "83.30ドル"],
                           why=HORMUZ_WHY + " 当日の上昇幅7.29ドル・9.59％・83.30ドルは細かい数値で、翌日以降の話と混ざりやすいため周辺。")
SPEC[("space_weapons", 1)] = dict(core=[("C1", ["2026年9月14日"], "配備発言の日"), ("C2", ["2021年11月15日"], "ロシアASAT試験日"), ("C3", ["1,500個超"], "デブリ数")],
                                  peri=["1408", "2025年", "第4条"], why=SPACE_WHY)
SPEC[("space_weapons", 2)] = dict(core=[("C1", ["2026年9月14日", "2026年9月"], "配備発言の日"), ("C2", ["2021年11月15日"], "ロシアASAT試験日"), ("C3", ["1,500個超"], "デブリ数")],
                                  peri=["1408", "第4条"], why=SPACE_WHY + " storylineの『2026年9月』は発言日(C1)の年月として中核側。")
SPEC[("space_weapons", 3)] = dict(core=[("C1", ["2026年9月14日", "2026年9月"], "配備発言の日"), ("C2", ["2021年11月"], "ロシアASAT試験の年月"), ("C3", ["1,500個超"], "デブリ数")],
                                  peri=["2025年", "第4条"], why=SPACE_WHY + " b3の試験表記は『2021年11月』(日なし)のまま転記。")
SPEC[("space_weapons", 4)] = dict(core=[("C1", ["2026年9月14日"], "配備発言の日"), ("C2", ["2021年11月15日"], "ロシアASAT試験日"), ("C3", ["1,500個超"], "デブリ数")],
                                  peri=["1408", "2025年", "第4条"], why=SPACE_WHY)


def annotate(text, spec):
    lits = {}
    for _, ls, _ in spec["core"]:
        for l in ls:
            lits[l] = h.MARK_RE.pattern and "【中核数値】"
    for l in spec["peri"]:
        lits[l] = "【周辺数値】"
    if lits:
        pat = re.compile("|".join(re.escape(l) for l in sorted(lits, key=len, reverse=True)))
        text = pat.sub(lambda m: m.group(0) + lits[m.group(0)], text)
    # 事実ID付与: ## Selected Facts 配下の箇条書き行のみ
    out, in_facts, n = [], False, 0
    for line in text.split("\n"):
        if line.strip().startswith("## Selected Facts"):
            in_facts = True
        elif in_facts and re.match(r"^\s*(-|・)\s*\S", line):
            n += 1
            mk = re.match(r"^(\s*(?:-|・)\s*)", line).group(1)
            line = mk + f"【事実{n}】" + line[len(mk):]
        out.append(line)
    return "\n".join(out), n, lits


def main():
    log = ["# ANNOTATION_LOG (FACTLOCK-WRITER-REDESIGN-TRIAL-01)\n",
           "原本は変更なし(読取のみ)。注記: 事実行頭に【事実番号】、数値の直後に【中核数値】/【周辺数値】。",
           "事実番号はbrief内ローカル(事実1から連番)。briefに元から入っている台帳ID(MUSE-HC-006、F-001等)は無変更で残る(数値判定から除外)。",
           "Storyline行・『Storyline：』重複行・『素材:』行は事実ではないためタグ番号を振らない(数値印のみ付与)。\n",
           "| brief | 事実数 | 中核 | 周辺 | 判断理由 |", "|---|---|---|---|---|"]
    dist = {}
    for (slug, i), spec in SPEC.items():
        src = SRC.format(slug=slug, i=i)
        text = open(src, encoding="utf-8").read()
        new, nfacts, lits = annotate(text, spec)
        for l in lits:
            assert l in text, (slug, i, l)
        # 検証: 印の付いていない数値が残っていない(ID・タグは除外)
        rest = re.sub("|".join(re.escape(l) + r"【(?:中核|周辺)数値】" for l in sorted(lits, key=len, reverse=True)) or "(?!)", " ", new)
        left = h.extract_numbers(h.TAG_RE.sub(" ", rest))
        assert not left, (slug, i, [t["surface"] for t in left])
        d = f"{OUT}/{slug}/b{i}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/selected_brief_factlock.md", "w", encoding="utf-8", newline="").write(new)
        core_json = {"slug": slug, "brief": f"b{i}", "source_brief": src,
                     "core": [{"id": cid, "literals": ls, "role": role} for cid, ls, role in spec["core"]],
                     "peripheral": spec["peri"], "reason": spec["why"], "max_core_per_article": 3}
        json.dump(core_json, open(f"{d}/core_numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        assert len(spec["core"]) <= 3
        dist[len(spec["core"])] = dist.get(len(spec["core"]), 0) + 1
        log.append(f"| {slug}/b{i} | {nfacts} | {len(spec['core'])} | {len(spec['peri'])} | {spec['why']} |")
    log.append(f"\n中核数値の件数分布(記事あたり→brief数): {dict(sorted(dist.items()))}")
    open(f"{OUT}/ANNOTATION_LOG.md", "w", encoding="utf-8").write("\n".join(log) + "\n")
    print(dist)


main()
