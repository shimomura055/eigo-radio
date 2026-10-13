# -*- coding: utf-8 -*-
"""FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01 (Trial専用、Production経路非接続)。
A=er072既存3 take(再利用、新規生成なし) / B=Comment1のみ / C=短縮Comment1・2(各第1文、決定論) /
D=重複回避優先順位変更(Comment1厳格・Comment2軽微許容) / E=Comment非参照(placeholder・指示文除去のみ)。
全条件で本文std.md全文・developer message・build_support_prompt・model/effortはProduction同一。
--mode design  : API呼出なし。prompts/{cond}_full.txt+sha、CONDITIONS_01.md
--mode generate: B,C,D,E 各3 take直列(max_attempts=1、再生成なし)
--mode evaluate: API呼出なし。takes_table_01.md(全15件の全文・字数・文数・lint)"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import sys

import er070_family_z_std_preview_x_alignment_01 as e70

RUN = e70.RUN
ER72 = "er072_output/melos_preview_std_adv_3take_01"
STOP_FILES = [f"{RUN}/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL"]

# Trial専用の最小置換(Prompt本文のうち重複回避に関する2箇所のみ)
BULLET_ORIG = "- 後で流れるComment 1・Comment 2と内容が重複する"
INTRO_ORIG = "Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。\n"
BLOCK_ORIG = INTRO_ORIG + "【Comment 1】\n{comment_1}\n\n【Comment 2】\n{comment_2}"
BULLET_D = "- 後で流れるComment 1と内容が重複する(Comment 2との軽微な重複は許容する)"
INTRO_D = "Comment 1・Comment 2は以下の通りです。Comment 1とは内容を厳格に重複させないでください。Comment 2との軽微な重複は許容します。\n"
B_COMMENT2 = "(生成失敗)"   # Family X既存挙動(er003_v1_iran01_a2_generate.py L343: comment_2=...or "(生成失敗)")


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def charlen(t):
    return len(t.replace("\n", ""))


def sents_ja(t):
    return len([s for s in t.replace("。", "。\n").split("\n") if s.strip()])


def first_sentence(t):
    i = t.index("。") + 1
    return t[:i]


def load():
    sa = json.load(open(f"{RUN}/support/a2_support.json", encoding="utf-8"))
    import er062_family_z_writer_01 as w62
    std_text = w62.rd(w62.level_text_path(RUN, "a2"))
    return sa["comments"]["1"], sa["comments"]["2"], std_text, sa


def build_roles(c1, c2):
    T = e70.Z_ROLE_TEMPLATE
    assert T.count(BULLET_ORIG) == 1 and T.count(BLOCK_ORIG) == 1
    roles = {}
    roles["A"] = T.format(comment_1=c1, comment_2=c2)
    roles["B"] = T.format(comment_1=c1, comment_2=B_COMMENT2)
    roles["C"] = T.format(comment_1=first_sentence(c1), comment_2=first_sentence(c2))
    TD = T.replace(BULLET_ORIG, BULLET_D).replace(INTRO_ORIG, INTRO_D)
    roles["D"] = TD.format(comment_1=c1, comment_2=c2)
    # E: 重複回避の箇条書き1行と、Comment 1・2の指示+埋込ブロック全体を除去(新規文言は追加しない)
    TE = T.replace(BULLET_ORIG + "\n", "").replace("\n\n" + BLOCK_ORIG, "")
    assert BULLET_ORIG not in TE and "{comment" not in TE
    roles["E"] = TE
    return roles


def build_prompts():
    import er003_v1_iran01_a2_generate as a2gen
    c1, c2, std_text, sa = load()
    roles = build_roles(c1, c2)
    ctx = f"{e70.CONTEXT_HEAD_X}\n{std_text}"
    return {k: (r, ctx, a2gen.build_support_prompt(r, ctx)) for k, r in roles.items()}, a2gen, (c1, c2, std_text)


def design(out):
    P, _a, (c1, c2, _t) = build_prompts()
    os.makedirs(f"{out}/prompts", exist_ok=True)
    shas = {}
    for k, (_r, _c, p) in P.items():
        open(f"{out}/prompts/{k}_full.txt", "w", encoding="utf-8").write(p)
        shas[k] = sha_text(p)
    er72 = open(f"{ER72}/prompt_std_full_01.txt", encoding="utf-8").read()
    shas["A_matches_er072"] = P["A"][2] == er72
    shas["er072_sha"] = sha_text(er72)
    json.dump(shas, open(f"{out}/prompt_sha_01.json", "w", encoding="utf-8"), indent=1)
    rows = ["# CONDITIONS_01 条件定義と差分表(生成前に作成)", "",
            "基準A=現行Std統一Prompt(er070)+Comment 1・2全文(er072既存3 take再利用、新規生成なし)。",
            "全条件共通: 本文std.md全文(`【エピソード全文(参考、新しいFactの追加禁止)】`以下)、SUPPORT_JA_PRINCIPLE、SUPPORT_PROHIBITIONS、出力形式、"
            "developer message、`build_support_prompt`、model(Production同一 gpt-6-luna)、reasoning effort high、max_attempts=1。", "",
            "| 条件 | 内容 | Comment 1として渡す文字列 | Comment 2として渡す文字列 | Prompt本文の変更 |", "|---|---|---|---|---|",
            "| A | 現行+C1・C2全文(基準) | 全文 | 全文 | なし |",
            f"| B | C1のみ | 全文 | `{B_COMMENT2}`(Family X既存の欠落時埋め値) | なし(逐語) |",
            "| C | 短縮C1・C2(決定論=各Commentの第1文のみ、LLM要約なし) | 第1文 | 第1文 | なし(逐語) |",
            "| D | 重複回避優先順位変更 | 全文 | 全文 | 下記2箇所の文言置換のみ |",
            "| E | Comment非参照 | なし | なし | 下記3箇所の除去のみ(新規文言なし) |", "",
            "## C: 短縮前後", f"- Comment 1 全文: {c1}", f"- Comment 1 短縮: {first_sentence(c1)}",
            f"- Comment 2 全文: {c2}", f"- Comment 2 短縮: {first_sentence(c2)}", "",
            "## D: 置換(Trial専用)",
            f"1. 箇条書き `{BULLET_ORIG}` -> `{BULLET_D}`",
            f"2. 導入文 `{INTRO_ORIG.strip()}` -> `{INTRO_D.strip()}`", "(新しい構成指針・抽象化禁止等の追加指示は足していない。)", "",
            "## E: 除去(Trial専用、入力調整)",
            f"1. 箇条書き `{BULLET_ORIG}` を行ごと除去", "2. `Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。` を除去",
            "3. `【Comment 1】{comment_1}` `【Comment 2】{comment_2}` 埋込ブロック(プレースホルダ含む)を除去",
            "除去後、Promptに`Comment`の語・placeholder・参照指示は残らない(testで機械確認)。", "",
            "## 送信prompt sha256", *[f"- {k}: `{shas[k]}`" for k in "ABCDE"],
            f"- A送信prompt == er072 prompt_std_full_01.txt: {shas['A_matches_er072']}", "",
            "## 条件別 unified diff(A -> 各条件)"]
    for k in "BCDE":
        d = difflib.unified_diff(P["A"][2].splitlines(), P[k][2].splitlines(), "A", k, lineterm="", n=0)
        rows += [f"### A -> {k}", "```diff", *list(d), "```", ""]
    open(f"{out}/CONDITIONS_01.md", "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print(json.dumps(shas, indent=1))
    return 0 if shas["A_matches_er072"] else 4


def generate(out, conds, budget):
    sent = [p for p in STOP_FILES if os.path.exists(p)]
    if sent:
        print("STOP sentinel present:", sent)
        return 3
    P, a2gen, _ = build_prompts()
    import er006_model_routing_contract_01 as routing
    import er062_family_z_structure_01 as st
    import er003_v1_en_direct_vfl_01_generate as vfl01
    m = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    est = lambda p: ((len(p) + 100) * e70.PRICE["input"] + 3000 * e70.PRICE["output"]) / 1e6 * e70.USD_JPY  # noqa: E731
    est_total = sum(3 * est(P[c][2]) for c in conds)
    assert est_total < budget, est_total
    os.makedirs(f"{out}/takes", exist_ok=True)
    before = e70.state_snapshot()
    client = vfl01.get_client()
    cap = {}
    orig = client.responses.create

    def create(*aa, **k):
        r = orig(*aa, **k)
        cap.update(usage=r.usage, model=r.model, id=r.id, effort=k.get("reasoning"))
        return r
    client.responses.create = create
    calls, takes, total = [], [], 0.0
    for c in conds:
        for i in (1, 2, 3):
            if any(os.path.exists(p) for p in STOP_FILES):
                print("STOP sentinel appeared; abort")
                break
            cap.clear()
            role, ctx, prompt = P[c]
            res = a2gen.run_support_text(client, role, ctx, max_attempts=1, model=m)
            u = cap.get("usage")
            ui, uo = getattr(u, "input_tokens", None), getattr(u, "output_tokens", None)
            rt = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None)
            act = ((ui or 0) * e70.PRICE["input"] + (uo or 0) * e70.PRICE["output"]) / 1e6 * e70.USD_JPY
            total += act
            calls.append({"cond": c, "take": i, "status": res["status"], "sent_prompt_sha": sha_text(res.get("prompt", prompt)),
                          "prompt_sha_matches_design": sha_text(res.get("prompt", prompt)) == sha_text(prompt),
                          "input_tokens": ui, "output_tokens": uo, "reasoning_tokens": rt, "jpy": round(act, 4),
                          "response_model_id": cap.get("model"), "response_id": cap.get("id"),
                          "reasoning": str(cap.get("effort")), "requested_model": m})
            if res["status"] != "OK":
                takes.append({"cond": c, "take": i, "status": res["status"], "attempts": res["attempts"]})
                print("FAILED", c, i, res["attempts"])
                continue
            t = res["text"].strip()
            open(f"{out}/takes/{c}_take{i}.txt", "w", encoding="utf-8").write(t + "\n")
            lint = st.lint_support_text(t, "ja", "melos")
            takes.append({"cond": c, "take": i, "status": "OK", "text": t, "lint": lint, "chars": charlen(t), "sentences": sents_ja(t)})
            print(c, i, "lint", lint, "jpy", round(act, 4), flush=True)
            print(t, flush=True)
    json.dump({"price_usd_per_1M": e70.PRICE, "usd_jpy": e70.USD_JPY, "estimate_total_jpy": round(est_total, 4), "calls": calls,
               "n_calls": len(calls), "total_jpy": round(total, 4), "budget_jpy": budget},
              open(f"{out}/cost_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(takes, open(f"{out}/takes_result_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    after = e70.state_snapshot()
    changed = [p for p in before if before[p] != after.get(p)]
    json.dump({"files_checked": len(before), "changed": changed, "unchanged_all": not changed,
               "generated_at": dt.datetime.now().isoformat(), "before_sha256": before, "after_sha256": after},
              open(f"{out}/state_guard_01.json", "w", encoding="utf-8"), indent=1)
    print("total JPY", round(total, 4), "state changed", changed)
    return 0


def evaluate(out):
    from er062_family_z_structure_01 import lint_support_text
    c1, c2, _t, _sa = load()
    rows = ["# takes_table_01 全15件のPreview全文", "", "| 条件 | take | 字数 | 文数 | lint | 全文 |", "|---|---|---|---|---|---|"]
    paths = {}
    for c in "ABCDE":
        for i in (1, 2, 3):
            p = f"{ER72}/std_take{i}.txt" if c == "A" else f"{out}/takes/{c}_take{i}.txt"
            if not os.path.exists(p):
                rows.append(f"| {c} | {i} | - | - | 未生成/失敗 | - |")
                continue
            paths[(c, i)] = p
            t = open(p, encoding="utf-8").read().strip()
            rows.append(f"| {c} | {i} | {charlen(t)} | {sents_ja(t)} | {lint_support_text(t, 'ja', 'melos') or 'OK'} | {t} |")

    def grams(s, n=4):
        s = re.sub(r"[、。\s]", "", s)
        return {s[i:i + n] for i in range(len(s) - n + 1)}
    g1, g2 = grams(c1), grams(c2)
    rows += ["", "## 機械補助(重複の判定ではない): 共通4-gram数(Preview側4-gram総数に対する)", "",
             "| 条件 | take | C1共通 | C2共通 |", "|---|---|---|---|"]
    for (c, i), p in paths.items():
        g = grams(open(p, encoding="utf-8").read().strip())
        rows.append(f"| {c} | {i} | {len(g & g1)}/{len(g)} | {len(g & g2)}/{len(g)} |")
    open(f"{out}/takes_table_01.md", "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print("\n".join(rows))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["design", "generate", "evaluate"], required=True)
    ap.add_argument("--conditions", default="B,C,D,E")
    ap.add_argument("--takes", type=int, default=3)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, default=100.0)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    if a.mode == "design":
        return design(a.out_dir)
    if a.mode == "evaluate":
        return evaluate(a.out_dir)
    if a.takes != 3:
        print("takes must be 3")
        return 4
    conds = a.conditions.split(",")
    assert all(c in "BCDE" for c in conds)
    return generate(a.out_dir, conds, a.budget_jpy)


if __name__ == "__main__":
    sys.exit(main())
