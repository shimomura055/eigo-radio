# RLCT 委任_13: Stage 1b ブラインド鍵+伏せ packet 生成(LLM呼出なし、read-only)。
# 鍵は --key-out に保存(評価記録が終わるまで開かない)。packet は --packet-dir に記事別 md で保存。
import argparse, json, random, re
from pathlib import Path

MASK = "【独立検証前の編集仮説】"
GREEK = ["α", "β", "γ", "δ"]
BLIND_METHODS = ["M0b", "M1", "M2", "M3"]  # M0=基準(開示)、M0pはB3なし(Ledger検証のみ)で比較対象外


def read(p):
    return Path(p).read_text(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--articles", required=True)
    ap.add_argument("--key-out", required=True)
    ap.add_argument("--packet-dir", required=True)
    ap.add_argument("--seed", type=int, default=20261018)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    root = Path(a.root)
    pd = Path(a.packet_dir)
    pd.mkdir(parents=True, exist_ok=True)
    key = {}
    masked_counts = {}
    for art in a.articles.split(","):
        order = BLIND_METHODS[:]
        rng.shuffle(order)
        key[art] = {GREEK[i]: m for i, m in enumerate(order)}

        def block(method):
            d = root / art / method
            res = json.loads(read(d / "result.json"))
            brief = read(d / "storyline_b3" / "selected_brief.md")
            story = res.get("selected_storyline") or ""
            n = brief.count(MASK) + story.count(MASK)
            brief = brief.replace(MASK, "")
            story = story.replace(MASK, "")
            fv = {k: v.get("verdict") for k, v in (res.get("final_verdicts") or {}).items()}
            sel = res.get("selected_fact_ids")
            return n, f"selected_fact_ids: {sel}\nfinal_verdicts(selected): { {k: fv.get(k) for k in (sel or [])} }\n\n### selected_storyline\n{story}\n\n### selected_brief.md\n{brief}\n"

        out = [f"# {art}  (blind packet; M0=REF open, others label-masked)\n"]
        _, ref = block("M0")
        out.append("## REF = M0\n" + ref)
        masked_counts[art] = {}
        for g in GREEK:
            n, txt = block(key[art][g])
            masked_counts[art][key[art][g]] = n
            out.append(f"## LABEL {g}\n" + txt)
        (pd / f"{art}.md").write_text("\n".join(out), encoding="utf-8")
    Path(a.key_out).write_text(
        json.dumps({"seed": a.seed, "key": key, "mask_string": MASK, "masked_occurrences": masked_counts}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("packets written:", pd)


if __name__ == "__main__":
    main()
