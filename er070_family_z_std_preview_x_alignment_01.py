# -*- coding: utf-8 -*-
"""FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01 (Trial専用、Production経路非接続)。
Family X Standard `er003_v1_iran01_a2_generate.PREVIEW_ROLE` を逐語の土台とし、News->物語で意味が成立しない箇所のみ
明示的な置換リスト(SUBSTITUTIONS)で置換してFamily Z Std用Preview Promptを構成する。Comment 1・2の両方を
`.format(comment_1=..., comment_2=...)`で埋め込む(Family Xと同方式)。
--mode diff : 差分表・Prompt出力のみ(API呼出なし)
--mode trial: 1 callだけ生成(Production同一条件: gpt-6-luna / effort high / build_support_prompt経由)"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import sys

RUN = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
USD_JPY = 160.0
PRICE = {"input": 0.10, "output": 0.50}   # USD/1M tokens, gpt-6-luna (er006_model_routing_pricing_coverage_test_01.py:50-52)

import er003_v1_iran01_a2_generate as a2gen   # noqa: E402

X_ROLE = a2gen.PREVIEW_ROLE

# (X原文断片, Z置換後, 変更理由, News⇔物語起因か)。X原文断片はX_ROLE中に正確に1回出現しなければならない。
SUBSTITUTIONS = [
    ("このエピソードのニュース本文(Preview・Key Phrasesに続いてMain Story・Points・\nIn One Line、英語)を聞きます。",
     "このエピソードの物語本文(Preview・Key Phrasesに続いてMain Story、英語)を聞きます。",
     "(a)「ニュース本文」->「物語本文」(対象がニュースでなく物語)。(b)「Points・In One Line」を削除: Family Z Stdには"
     "Point One/Two・In One Lineが存在しない(CURRENT_SPEC 2026-10-12決定「In One Lineなし・Comment4なし」、Point構造なし)ため、"
     "そのまま残すと存在しない構成要素を指す虚偽の記述になる。", True),
    ("役割: このニュースの\n", "役割: この物語の\n", "対象が物語。", True),
    ("problem(何が問題・論点か)", "problem(主人公が直面する問題・対立は何か)",
     "「論点」はニュース固有概念。ユーザー指示の置換例(ニュースの論点->主人公が直面する問題・対立)に従う。", True),
    ("記事の内容により", "物語の内容により", "「記事」はニュース記事を指す語。対象が物語。", True),
]

# 置換せず逐語維持する重要箇所(差分表で「維持」と明示する。Family Xの指示省略がないことの確認用)
VERBATIM_KEEP = [
    "theme(何についての話か)", "value(なぜ聞く価値があるか)",
    "4要素すべてを律儀に別の文で書き並べる必要はありません(question=聞き終える\n頃に何が分かるようになるか、を無理に独立した一文にしなくてよい)。",
    "2文程度、80〜110字程度を目安にしてください", "4文・150字を超えるような長いPreviewにはしない",
    "- 答えを先に言う", "- 重要な数字を先出しする", "- 結論を先に言う", "- turning point(展開の転換点)を先に明かす",
    "- 後で流れるComment 1・Comment 2と内容が重複する",
    "Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。\n【Comment 1】\n{comment_1}\n\n【Comment 2】\n{comment_2}",
]

# Family Z現行Promptにあり、Family X原文にないため今回「除去」される要素(Family X基準への統一。追加ではない)
Z_CURRENT_ONLY_DROPPED = [
    ("「A2レベル、Public Domain文学のリライト」の説明", "Family Xに対応物なし。物語/Newsの差で必須とは説明できないため含めない"),
    ("状況設定(誰が・どんな状況か)を2〜3文で紹介", "Family Xにない(theme/problem/valueの別構成)。Family X基準へ統一"),
    ("fam_c._BANNED_PHRASES_INSTRUCTION(聞いてみましょう等の禁止・無内容予告/結末先出し/Story外事実/長文化)",
     "Family X PREVIEW_ROLEに無い。News/物語の差による必要性を説明できないため、roleへは含めない。"
     "ただしProduction lint(lint_support_text 'ja')のLISTEN_INSTRUCTION検査は呼出側共通の機械処理として不変(retry1->FamilyZLintStop)"),
    ("「本文にない設定・事実を追加しないでください」", "Family Xのrole本文にはなく、context見出し「新しいFactの追加禁止」で担保。Family X方式に統一"),
    ("「結末や物語の山場には触れない」", "Family Xの『答え/結論/turning pointを先に言わない』に包含される(Family X逐語維持)"),
]

CONTEXT_HEAD_X = "【エピソード全文(参考、新しいFactの追加禁止)】"   # Family X呼出(er003 L340付近)と同一


def build_z_role_template():
    t = X_ROLE
    for src, dst, _r, _y in SUBSTITUTIONS:
        assert t.count(src) == 1, ("substitution source not unique/absent", src)
        t = t.replace(src, dst)
    for bad in ("ニュース", "記事", "Points", "In One Line"):
        assert bad not in t, ("news-specific token remains", bad)
    return t


Z_ROLE_TEMPLATE = build_z_role_template()


def assemble_role(c1, c2):
    return Z_ROLE_TEMPLATE.format(comment_1=c1, comment_2=c2)


def write_diff(out):
    os.makedirs(out, exist_ok=True)
    rows = ["| # | Family X原文 | Family Z変更後 | 変更理由 | News⇔物語起因 |", "|---|---|---|---|---|"]
    esc = lambda s: s.replace("\n", "<br>").replace("|", "\\|")  # noqa: E731
    for i, (s, d, r, y) in enumerate(SUBSTITUTIONS, 1):
        rows.append(f"| {i} | {esc(s)} | {esc(d)} | {esc(r)} | {'Yes' if y else 'No'} |")
    n_no = sum(1 for x in SUBSTITUTIONS if not x[3])
    keep = ["| # | 逐語維持(Family X原文=Family Z) | 備考 |", "|---|---|---|"]
    for i, k in enumerate(VERBATIM_KEEP, 1):
        assert k in Z_ROLE_TEMPLATE, ("verbatim keep missing", k)
        keep.append(f"| K{i} | {esc(k)} | 変更なし(Family X指示を省略していない) |")
    dropped = ["| # | Family Z現行Promptにのみ存在 | 扱い |", "|---|---|---|"]
    for i, (a, b) in enumerate(Z_CURRENT_ONLY_DROPPED, 1):
        dropped.append(f"| D{i} | {esc(a)} | {esc(b)} |")
    ctx = ["| 項目 | Family X | Family Z(Trial) | 理由 | News⇔物語起因 |", "|---|---|---|---|---|",
           f"| context見出し | `{CONTEXT_HEAD_X}` | 同一(Family X逐語) | 「エピソード全文」はNews/物語共通で置換不要。現行Z Production(`【物語全文(参考、新しい設定・事実の追加禁止)】`)からはFamily X逐語へ寄せる。呼出側1行の変更として`WIRING_DESIGN_01.md`に記載 | N/A(置換せず逐語維持) |",
           "| Comment埋込 | `PREVIEW_ROLE.format(comment_1=, comment_2=)` | 同一方式 | Family X逐語 | N/A |"]
    md = ["# PROMPT_DIFF_01 (Family X Std `PREVIEW_ROLE` -> Family Z Std Preview, Trial)", "",
          f"STOP判定(News⇔物語起因でない差分の数): **{n_no}** -> {'PASS(Trial実行可)' if n_no == 0 else 'STOP'}", "",
          "## 1. Family Xから置換した全差分(これで全て。他は逐語一致)", ""] + rows + ["",
          "## 2. 逐語維持の重要箇所(theme/problem/value/question、分量、禁止条件、Comment 1・2重複回避)", ""] + keep + ["",
          "## 3. Family Z現行Promptにのみあった要素(Family X基準への統一で含めないもの)", ""] + dropped + ["",
          "## 4. context・埋込", ""] + ctx + ["",
          "## 5. Family X原文(逐語)", "", "```", X_ROLE, "```", "",
          "## 6. Family Z Trial Prompt(テンプレート、プレースホルダ付き)", "", "```", Z_ROLE_TEMPLATE, "```", ""]
    open(f"{out}/PROMPT_DIFF_01.md", "w", encoding="utf-8").write("\n".join(md))
    open(f"{out}/prompt_x_original_01.txt", "w", encoding="utf-8").write(X_ROLE + "\n")
    open(f"{out}/prompt_after_template_01.txt", "w", encoding="utf-8").write(Z_ROLE_TEMPLATE + "\n")
    import difflib
    ud = "\n".join(difflib.unified_diff(X_ROLE.splitlines(), Z_ROLE_TEMPLATE.splitlines(), "family_x_PREVIEW_ROLE",
                                        "family_z_aligned_template", lineterm=""))
    open(f"{out}/prompt_unified_diff_01.txt", "w", encoding="utf-8").write(ud + "\n")
    return n_no


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def state_snapshot():
    files = [p for p in glob.glob(f"{RUN}/**/*", recursive=True) if os.path.isfile(p)]
    files += ["er026_family_z_fiction_production_runner_01.py", "er062_family_z_writer_01.py",
              "er062_family_z_structure_01.py", "er003_v1_iran01_a2_generate.py", "er006_model_routing_contract_01.py"]
    return {p.replace("\\", "/"): sha(p) for p in sorted(files)}


def charlen(t):
    return len(t.replace("\n", ""))


def sentences(t):
    return [s for s in t.replace("。", "。\n").split("\n") if s.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["diff", "trial"], required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, default=5.0)
    a = ap.parse_args()
    out = a.out_dir
    n_no = write_diff(out)
    if a.mode == "diff":
        print("diff written; non-news-derived diffs:", n_no)
        return 0 if n_no == 0 else 4
    if n_no:
        print("STOP: non-news-derived diff exists")
        return 4
    sentinels = [p for p in (f"{RUN}/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL") if os.path.exists(p)]
    if sentinels:
        print("STOP sentinel present:", sentinels)
        return 3

    import er006_model_routing_contract_01 as routing
    import er062_family_z_structure_01 as st
    import er062_family_z_writer_01 as w62
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    sup = json.load(open(f"{RUN}/support/a2_support.json", encoding="utf-8"))
    c1, c2, c3 = sup["comments"]["1"], sup["comments"]["2"], sup["comments"]["3"]
    role = assemble_role(c1, c2)
    assert "{comment_" not in role and c1 in role and c2 in role      # Dangling Referenceなし・両Comment入力
    text_a2 = w62.rd(w62.level_text_path(RUN, "a2"))
    ctx = f"{CONTEXT_HEAD_X}\n{text_a2}"
    fp = a2gen.build_support_prompt(role, ctx)
    assert c1 in fp and c2 in fp
    est_in, est_out = len(fp) + 100, 3000
    est_jpy = (est_in * PRICE["input"] + est_out * PRICE["output"]) / 1e6 * USD_JPY
    assert est_jpy < a.budget_jpy, est_jpy
    before_state = state_snapshot()

    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    cap = {}
    orig = client.responses.create

    def create(*aa, **k):
        r = orig(*aa, **k)
        cap.update(usage=r.usage, model=r.model, id=r.id, effort=k.get("reasoning"))
        return r
    client.responses.create = create
    res = a2gen.run_support_text(client, role, ctx, max_attempts=1, model=model)   # 1 call only
    u = cap.get("usage")
    ui, uo = getattr(u, "input_tokens", None), getattr(u, "output_tokens", None)
    rt = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None)
    act = ((ui or 0) * PRICE["input"] + (uo or 0) * PRICE["output"]) / 1e6 * USD_JPY
    json.dump({"estimate_jpy": round(est_jpy, 4), "price_usd_per_1M": PRICE,
               "price_source": "er006_model_routing_pricing_coverage_test_01.py:50-52", "usd_jpy": USD_JPY, "calls": 1,
               "actual_input_tokens": ui, "actual_output_tokens": uo, "reasoning_tokens": rt, "actual_jpy": round(act, 4),
               "budget_jpy": a.budget_jpy, "requested_model": model, "response_model_id": cap.get("model"),
               "response_id": cap.get("id"), "reasoning": str(cap.get("effort")), "status": res["status"]},
              open(f"{out}/cost_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if res["status"] != "OK":
        print("FAILED", res["attempts"])
        return 2
    after = res["text"].strip()
    open(f"{out}/preview_after_01.txt", "w", encoding="utf-8").write(after + "\n")
    open(f"{out}/prompt_after_full_assembled_01.txt", "w", encoding="utf-8").write(fp)
    open(f"{out}/prompt_after_role_assembled_01.txt", "w", encoding="utf-8").write(role + "\n")
    before = sup["preview"].strip()
    prev_trial = open("er067_output/family_z_std_preview_trial_01/preview_after_01.txt", encoding="utf-8").read().strip()
    vr = {}
    for name, t in (("before_production", before), ("prev_trial_er067", prev_trial), ("after_er070", after)):
        vr[name] = {"text": t, "chars": charlen(t), "sentences": len(sentences(t)),
                    "lint_support_text_ja_melos": st.lint_support_text(t, "ja", "melos"),
                    "within_80_110": 80 <= charlen(t) <= 110, "le_150_and_le_3_sentences": charlen(t) <= 150 and len(sentences(t)) <= 3}
    vr["inputs"] = {"comment_1": c1, "comment_2": c2, "comment_3(参考・Previewへは入力しない=Family Xと同じ)": c3}
    json.dump(vr, open(f"{out}/validator_result_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    after_state = state_snapshot()
    changed = [p for p in before_state if before_state[p] != after_state.get(p)]
    json.dump({"files_checked": len(before_state), "changed": changed, "unchanged_all": not changed,
               "generated_at": dt.datetime.now().isoformat(), "before_sha256": before_state, "after_sha256": after_state},
              open(f"{out}/state_guard_01.json", "w", encoding="utf-8"), indent=1)
    print("AFTER:", after)
    print(json.dumps({k: (v if k == "inputs" else {kk: vv for kk, vv in v.items() if kk != "text"}) for k, v in vr.items()},
                     ensure_ascii=False)[:1200])
    print("cost JPY", act, "model", cap.get("model"), "state changed", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
