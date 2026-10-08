# -*- coding: utf-8 -*-
"""文体指標(決定論、API呼び出しなし、¥0)。FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_04b。
対象: JA最終稿 ja_writer/revision2.md(タグ除去済み)。タイトル行(1行目)は文数・字数から除く。
実行: .venv/Scripts/python.exe -X utf8 er052_output/factlock_writer_trial_01/sweep_01/tools/style_metrics.py
"""
import glob, json, os, re, statistics, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
SW = "er052_output/factlock_writer_trial_01/sweep_01"
# DIAGNOSIS_01 (c) の比喩語リスト(本文から多出語を抽出して定義されたもの)を再利用
METAPHOR = ["舞台", "幕", "探偵", "衣装", "主役", "配役", "ドラマ", "映画", "ショー", "劇", "手がかり", "犯人", "謎",
            "ゲーム", "カード", "小道具", "せりふ", "代役", "お色直し", "着替え", "衣替え", "箱", "札", "登場", "退場", "筋書き"]
SPEC = ["かもしれ", "もし", "だろう", "はず", "ようだ"]
NEG = ["ではありません", "ではない"]
POLITE = re.compile(r"(です|ます|ました|でした|ません|でしょう|ください|ましょう)(か|ね|よ|ょ)?[」』）)]*$")
TAGS = re.compile(r"【事実[^】]*】")


def split_sentences(body):
    parts = re.split(r"(?<=[。！？!?])", body)
    return [p.strip() for p in parts if p.strip()]


def metrics(text):
    text = TAGS.sub("", text).strip()
    lines = text.split("\n")
    body = "\n".join(lines[1:]) if len(lines) > 1 else text
    sents = split_sentences(body.replace("\n", ""))
    polite = sum(1 for s in sents if POLITE.search(re.sub(r"[。！？!?]+$", "", s)))
    flat = body.replace("\n", "").replace(" ", "")
    meta_hit = {w: flat.count(w) for w in METAPHOR if flat.count(w)}
    return {
        "polite_ratio": round(polite / len(sents), 3) if sents else 0.0,
        "sentences": len(sents),
        "arabic_numbers": len(re.findall(r"[0-9]+(?:[.,][0-9]+)*", body)),
        "speculation": sum(flat.count(w) for w in SPEC),
        "questions": flat.count("?") + flat.count("？"),
        "metaphor_distinct": len(meta_hit),
        "metaphor_total": sum(meta_hit.values()),
        "chars": len(flat),
        "negation_dewa_arimasen": sum(flat.count(w) for w in NEG),
    }


def collect():
    v = json.load(open(f"{SW}/variants.json", encoding="utf-8"))
    rows = []
    for r in v["references"]:
        for slug, b in v["briefs"]:
            rep = r.get("rep_override", {}).get(f"{slug}/b{b}", r["rep_default"])
            rows.append((r["id"], slug, b, r["path_template"].format(slug=slug, b=b, rep=rep)))
    for p in sorted(glob.glob(f"{SW}/runs/*/control/b*__S*__r1")):
        q = p.replace("\\", "/")
        m = re.search(r"runs/(.+?)/control/b(\d+)__(S\d+)__r1$", q)
        if m:
            rows.append((m.group(3), m.group(1), int(m.group(2)), q))
    return rows


KEYS = ["polite_ratio", "arabic_numbers", "speculation", "questions", "metaphor_distinct", "metaphor_total", "chars", "negation_dewa_arimasen"]


def main():
    out, per = {}, []
    for vid, slug, b, d in collect():
        f = f"{d}/ja_writer/revision2.md"
        if not os.path.exists(f):
            per.append({"variant": vid, "slug": slug, "b": b, "missing": True}); continue
        m = metrics(open(f, encoding="utf-8").read())
        m.update(variant=vid, slug=slug, b=b, path=f.replace("\\", "/"))
        per.append(m)
    by = {}
    for m in per:
        if not m.get("missing"):
            by.setdefault(m["variant"], []).append(m)
    order = sorted(by, key=lambda x: (0, int(x[1:])))
    lines = ["# STYLE_METRICS(JA最終稿 ja_writer/revision2.md、決定論の機械集計、委任_04b)", "",
             "対象: タグ除去済みJA最終稿。S0/S5は既存R2本文(再生成なし)。1変種=3記事(meta b2/hormuz b4/space_weapons b3)の平均。N=3で有意性は主張しない。", "",
             "定義: polite_ratio=です・ます系で終わる文の割合(タイトル除く) / arabic_numbers=半角数字の塊の個数 / speculation=かもしれ・もし・だろう・はず・ようだ の出現数 / questions=?・？の数 / metaphor_distinct=DIAGNOSIS_01 (c)の比喩語リスト(26語)の異なり数 / metaphor_total=その出現数 / chars=空白改行除く字数(タイトル除く) / negation=「ではありません」「ではない」の出現数。", "",
             "| 変種 | n | です・ます文の割合 | 半角数字 | 推量・仮定語 | 問い | 比喩異なり | 比喩出現 | 字数 | 否定「ではありません」型 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for vid in order:
        rs = by[vid]
        mean = lambda k: round(statistics.mean(r[k] for r in rs), 2)
        lines.append(f"| {vid} | {len(rs)} | {mean('polite_ratio')} | {mean('arabic_numbers')} | {mean('speculation')} | {mean('questions')} | {mean('metaphor_distinct')} | {mean('metaphor_total')} | {mean('chars')} | {mean('negation_dewa_arimasen')} |")
    lines += ["", "## 記事別", "", "| 変種 | slug/b | です・ます | 数字 | 推量 | 問い | 比喩異なり | 比喩出現 | 字数 | 否定 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for m in sorted([x for x in per if not x.get("missing")], key=lambda x: (int(x["variant"][1:]), x["slug"])):
        lines.append(f"| {m['variant']} | {m['slug']}/b{m['b']} | {m['polite_ratio']} | {m['arabic_numbers']} | {m['speculation']} | {m['questions']} | {m['metaphor_distinct']} | {m['metaphor_total']} | {m['chars']} | {m['negation_dewa_arimasen']} |")
    miss = [x for x in per if x.get("missing")]
    if miss:
        lines += ["", "## 本文なし(STOP等)", ""] + [f"- {x['variant']} {x['slug']}/b{x['b']}" for x in miss]
    os.makedirs(f"{SW}/eval", exist_ok=True)
    open(f"{SW}/eval/STYLE_METRICS.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(per, open(f"{SW}/eval/STYLE_METRICS.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(lines[:30]))


if __name__ == "__main__":
    main()
