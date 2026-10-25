# -*- coding: utf-8 -*-
"""er115_fx_numeric_r5_score_01.py (DEV/Trial専用、Production非接続)
FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_04: 最終本文の数値を事前登録の3分類(必須/任意/不要)で決定論に集計し、Before/Afterを比較する。
これは今回のTrial評価のための計測であり、恒久的な数値選定機構ではない(ユーザー原文§5)。LLM/APIなし。
分類規則(PREREGISTERED_CRITERIA_03.md): 記事別の表(下記TABLES)に載る数値=表のとおり / 表に載らない大きさ・範囲の数値=不要(未分類) /
年・日付・序数・単位なし小整数(<=31)=文脈数値(別集計・不要数にはまず数えないが増減は記録)。
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er053_b3_deterministic_producer_01 as P   # noqa: E402
import er115_fx_numeric_retention_trial_01 as t   # noqa: E402

# 事前登録(生成前commit)の3分類表。値=表記のリスト。
TABLES = {
    "ig_nobel_2026": {
        "must": ["3倍超"],
        "optional": [],
        "unneeded": ["1.2 Å", "60試行", "31試行", "7試行", "22試行", "16.5%", "21.5%", "2,000着", "12,000個", "1,000人", "1.4%", "235人", "367人", "約2,150万～1,690万年", "約1,690万年"],
    },
    "moon_shrinking": {
        "must": ["約42〜46 m"],
        "optional": ["約3〜4億年", "約4億年", "約8億年"],
        "unneeded": ["約750 m", "約1.1 km", "約11 cm", "約6 cm", "約44 m", "約45 m", "25〜35度", "8,900本", "5,470本", "127,800", "0.0048〜0.0053%", "13件", "28件", "90 km"],
    },
    "coffee_prices": {
        "must": ["4.30米ドル", "41%"],
        "optional": ["約9か月"],
        "unneeded": ["9.14米ドル", "3%", "8.87米ドル", "8.7%", "15%", "262.18米セント", "3.3545米ドル", "3.1805米ドル", "71%", "18.9%", "7.1%", "3.54米ドル", "3.45米ドル", "1,791万袋"],
    },
    "semiconductor_earnings": {
        "must": ["167億ドル", "約348億ドル"],
        "optional": ["295億9,100万ドル", "221%", "54%"],
        "unneeded": ["93%", "217億ドル", "236%", "10億ドル"],
    },
}
CTX_KINDS = ("year", "date_time", "ordinal", "name_embedded")
_STRIP_TAIL = re.compile(r"(?:超|以上|以下|ほど|程度)$")


def norm_unit(u: str) -> str:
    return _STRIP_TAIL.sub("", P.nfkc(u or "").strip())


def skey(s: str):
    s = P.nfkc(s)
    k = P.surface_kind(s)
    return (k, P.main_numbers(s, k), norm_unit(P.unit_of(s) or ""))


def _table_index(article: str):
    idx = {}
    for cls in ("must", "optional", "unneeded"):
        for s in TABLES[article][cls]:
            idx[skey(s)] = (cls, s)
            idx.setdefault(skey(s)[:2] + ("*",), None)
    return idx


def _lookup(idx, s):
    k = skey(s)
    if k in idx and idx[k]:
        return idx[k]
    # 単位の取り方の差(『ドル』『米ドル』など)を許す: 種別+値が一致し、かつ表側の単位がどちらかの末尾/先頭に含まれる
    for kk, v in idx.items():
        if v and kk[:2] == k[:2] and (kk[2] == k[2] or not k[2] or (kk[2] and k[2] and (kk[2] in k[2] or k[2] in kk[2]))):
            return v   # 本文側が単位を伴わない表記(例『4.30』+後続の『ドル』)は種別+値で照合
    return None


def is_ctx(s: str) -> bool:
    k = P.surface_kind(P.nfkc(s))
    return k in CTX_KINDS or t.T_is_ambiguous(s)


def classify_ja(text: str, article: str) -> dict:
    idx = _table_index(article)
    t2 = re.sub(r"(\d)\s*から\s*(\d)", r"\g<1>〜\g<2>", text or "")
    out = {"must": [], "optional": [], "unneeded_listed": [], "unneeded_unlisted": [], "context": []}
    seen = set()
    for s in P.extract_surfaces(t2):
        k = skey(s)
        if k in seen:
            continue
        seen.add(k)
        if is_ctx(s):
            out["context"].append(s)
            continue
        hit = _lookup(idx, s)
        if hit is None:
            out["unneeded_unlisted"].append(s)
        else:
            out[{"must": "must", "optional": "optional", "unneeded": "unneeded_listed"}[hit[0]]].append(s)
    out["unneeded_total"] = len(out["unneeded_listed"]) + len(out["unneeded_unlisted"])
    out["unique_numeric_surfaces"] = len(out["must"]) + len(out["optional"]) + out["unneeded_total"]
    return out


_EN_NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?!(?-i:[A-Z])\b)\s*(?:%|percent|times|x|billion|million|trillion|meters?|m|km|cm|kg|years?)?", re.I)


def en_tokens(text: str) -> list:
    return [m.group(0).strip() for m in _EN_NUM.finditer(text or "")]


# 委任_06: 数字直後の大文字1字(3D/5G)は数値トークンにしない(上の_EN_NUMの先読み)。
# 英訳側の必須数値の存在判定(決定論の正規表現。ig『3倍超』は較正済みen_presentが偽陽性[three dimensions]を出すため使わない)
EN_MUST_PATTERNS = {
    "3倍超": r"(?:\b(?:three|3)[\s-]*(?:times|x\b|fold)|\btriple|\bthreefold)",
    "約42〜46 m": r"42\D{0,12}46",
    "4.30米ドル": r"4\.30",
    "41%": r"41\s*(?:%|percent)",
    "167億ドル": r"16\.7\s*billion|\$16\.7",
    "約348億ドル": r"34\.8\s*billion|\$34\.8",
}

STAGE_FILES = (("R0", "ja_writer/factlock/r0.md"), ("R1", "ja_writer/revision1.md"), ("R2", "ja_writer/revision2.md"),
               ("EN_Std", "a2/article.md"), ("EN_Adv", "b1b/article.md"))


def rdt(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def score_dir(out_dir: str, article: str, news_unit_hints: dict | None = None) -> dict:
    res = {"dir": os.path.relpath(out_dir, ROOT).replace("\\", "/"), "stages": {}}
    must = TABLES[article]["must"]
    for st, rel in STAGE_FILES:
        text = rdt(os.path.join(out_dir, rel))
        if text is None:
            res["stages"][st] = None
            continue
        if st.startswith("EN"):
            ent = {"en_tokens": en_tokens(text), "must_present": {}}
            for m in must:
                ent["must_present"][m] = bool(re.search(EN_MUST_PATTERNS[m], text, re.I))
            res["stages"][st] = ent
        else:
            c = classify_ja(text, article)
            c["must_present"] = {m: bool(t.match_core(m, text, "", [])["present"]) if True else None for m in must}
            res["stages"][st] = c
    return res


def diff_before_after(before: dict, after: dict) -> dict:
    out = {}
    for cls in ("must", "optional", "unneeded_listed", "unneeded_unlisted", "context"):
        b = {skey(x): x for x in before.get(cls, [])}
        a = {skey(x): x for x in after.get(cls, [])}
        out[cls] = {"added": [a[k] for k in a if k not in b], "removed": [b[k] for k in b if k not in a]}
    out["unneeded_total_before"] = before.get("unneeded_total")
    out["unneeded_total_after"] = after.get("unneeded_total")
    out["unneeded_delta"] = (after.get("unneeded_total") or 0) - (before.get("unneeded_total") or 0)
    out["unique_before"] = before.get("unique_numeric_surfaces")
    out["unique_after"] = after.get("unique_numeric_surfaces")
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", required=True, choices=sorted(TABLES))
    ap.add_argument("--dir", required=True)
    ap.add_argument("--before", default=None, help="Before側のdir(相対可)。指定時は R2 の差分も出す")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = a.dir if os.path.isabs(a.dir) else os.path.join(ROOT, a.dir)
    res = score_dir(d, a.article)
    if a.before:
        b = a.before if os.path.isabs(a.before) else os.path.join(ROOT, a.before)
        rb = score_dir(b, a.article)
        res["before"] = rb
        if rb["stages"].get("R2") and res["stages"].get("R2"):
            res["diff_R2"] = diff_before_after(rb["stages"]["R2"], res["stages"]["R2"])
    outp = a.out or os.path.join(d, "trial_metrics_r5.json")
    json.dump(res, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in res.items() if k in ("diff_R2",)} or res["stages"].get("R2"), ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()


# ---------------- COMPARISON_04.md 生成(Fable読み用: 数値に印を付けた一覧+R2本文) ----------------
def _fmt_cls(c: dict) -> str:
    def j(x):
        return "、".join(x) if x else "なし"
    return (f"必須[{j(c['must'])}] / 任意[{j(c['optional'])}] / 不要(表)[{j(c['unneeded_listed'])}] / 不要(未分類)[{j(c['unneeded_unlisted'])}] / 文脈[{j(c['context'])}]"
            f" / 不要数={c['unneeded_total']} ユニーク数値表記数={c['unique_numeric_surfaces']}")


def render_block(label: str, d: str, article: str) -> str:
    dd = d if os.path.isabs(d) else os.path.join(ROOT, d)
    sc = score_dir(dd, article)
    lines = [f"### {label}", f"- dir: `{sc['dir']}`"]
    for st in ("R0", "R1", "R2"):
        c = sc["stages"].get(st)
        lines.append(f"- {st}: " + (_fmt_cls(c) + f" / 必須の存在={c['must_present']}" if c else "(なし)"))
    for st in ("EN_Std", "EN_Adv"):
        c = sc["stages"].get(st)
        lines.append(f"- {st}: " + (f"必須の存在={c['must_present']} / 数値トークン={c['en_tokens']}" if c else "(なし)"))
    r2 = rdt(os.path.join(dd, "ja_writer/revision2.md"))
    lines += ["", "日本語最終(R2)本文:", "", "```", (r2 or "(なし)").strip(), "```", ""]
    return "\n".join(lines), sc


def render_comparison(spec: list, out_path: str):
    """spec = [(article, [(label, dir), ...], after_label)]"""
    md = ["# COMPARISON_04 (FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_04、R5)", "",
          "数値の分類は`PREREGISTERED_CRITERIA_03.md` §1の表(生成前固定)による決定論の機械分類。『文脈』=年・日付・序数・単位なし小整数。Fableが本文を読んで妥当性を判断する。", ""]
    for article, items, after_label in spec:
        md.append(f"## {article}")
        scs = {}
        for label, d in items:
            blk, sc = render_block(label, d, article)
            md.append(blk)
            scs[label] = sc
        if after_label in scs:
            a2 = scs[after_label]["stages"].get("R2")
            for label, sc in scs.items():
                if label == after_label or not sc["stages"].get("R2") or not a2:
                    continue
                df = diff_before_after(sc["stages"]["R2"], a2)
                md.append(f"**{label} → {after_label}(R2)**: 必須 追加{df['must']['added']}/削除{df['must']['removed']}、任意 追加{df['optional']['added']}/削除{df['optional']['removed']}、"
                          f"不要(表) 追加{df['unneeded_listed']['added']}/削除{df['unneeded_listed']['removed']}、不要(未分類) 追加{df['unneeded_unlisted']['added']}/削除{df['unneeded_unlisted']['removed']}、"
                          f"文脈 追加{df['context']['added']}/削除{df['context']['removed']}、不要数 {df['unneeded_total_before']}→{df['unneeded_total_after']}(増減{df['unneeded_delta']:+d})、"
                          f"ユニーク数値表記数 {df['unique_before']}→{df['unique_after']}")
                md.append("")
    open(out_path, "w", encoding="utf-8").write("\n".join(md))
