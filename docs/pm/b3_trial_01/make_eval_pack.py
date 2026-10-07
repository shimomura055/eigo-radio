# -*- coding: utf-8 -*-
"""make_eval_pack.py: B3段階2 評価パック生成(決定論・標準ライブラリのみ・API/生成なし、¥0)。
入力: eval/_private/MAP_stage2.json(評価者に渡さない)、eval_rubric.md、unprovided_checklist_*.md、article_schema.json
出力: eval/eval_pack_stage2/ (README_EVALUATOR.md[rubric全文含む], unprovided_checklist_*.md, article_schema.json,
      articles_index.md, assignment_<slug>_<A|B>.md, scores_template.json) と eval/_private/assignment_balance.json(条件配分の記録、評価者非公開)
割当: テーマ別に2評価者(A/B)へ、条件ごとに seed固定シャッフルした順で交互に配る(条件が評価者間で偏らないようにする。条件ラベルは出力に書かない)。
      各評価者内の評価順は seed固定シャッフル(条件順にならない)。
usage: python make_eval_pack.py [--seed 20261007]
"""
import argparse, hashlib, json, os, random, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EV = "er052_output/open233_b3_trial_01/eval"
PACK = EV + "/eval_pack_stage2"
THEMES = ["meta", "hormuz", "space_weapons"]
DOC = "docs/pm/b3_trial_01"


def main():
    os.chdir(ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="20261007")
    ns = ap.parse_args()
    mp = json.load(open(EV + "/_private/MAP_stage2.json", encoding="utf-8"))
    arts = mp["articles"]
    os.makedirs(PACK, exist_ok=True)
    bal, assign = {}, {}
    for t in THEMES:
        keys = sorted(k for k in arts if k.startswith(t + "/"))
        byv = {}
        for k in keys:
            byv.setdefault(arts[k]["variant"], []).append(k)
        halves = {"A": [], "B": []}
        n = 0
        for v in sorted(byv):
            lst = sorted(byv[v])
            random.Random("%s|deal|%s|%s" % (ns.seed, t, v)).shuffle(lst)
            for k in lst:
                halves["AB"[n % 2]].append(k)
                n += 1
        for h in "AB":
            lst = sorted(halves[h])
            random.Random("%s|order|%s|%s" % (ns.seed, t, h)).shuffle(lst)
            assign["%s_%s" % (t, h)] = [k.split("/", 1)[1] for k in lst]
            c = {}
            for k in lst:
                c[arts[k]["variant"]] = c.get(arts[k]["variant"], 0) + 1
            bal["%s_%s" % (t, h)] = {"n": len(lst), "by_variant": c}
    # 重複・漏れ検算
    flat = [(k.split("_")[0] if not k.startswith("space") else "space_weapons", c) for k, v in assign.items() for c in v]
    assert len(flat) == len(set(flat)) == len(arts), (len(flat), len(set(flat)), len(arts))
    # rubric(全文) + 段階2適用メモ
    rub = open(DOC + "/eval_rubric.md", encoding="utf-8").read()
    memo = """# 評価者向け README(B3段階2、OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01)

あなたは記事評価者(1インスタンス)です。API呼び出し・記事生成・SSOT編集・git操作・記事本文の編集は禁止です。条件(どの生成方法の記事か)は開示されていません。推測もしないでください。

## 段階2適用メモ(下のrubric全文の読み替え。判定基準そのものは変更なし)
- rubric内の「24匿名記事(計72)」は読み替え: あなたの担当は `assignment_<slug>_<A|B>.md` に列挙された記事コードのみ。
- rubric 7節の記事パス `eval/blind/<slug>/<code>/` は **`er052_output/open233_b3_trial_01/eval/blind_stage2/<slug>/<code>/`** に読み替える。各コードの下に `ja_writer/original.md`(R0), `ja_writer/revision1.md`(R1), `ja_writer/revision2.md`(R2), `b1b/article.md`(EN)。
- 記事は **Writer1本のみ**(w1)。出力JSONの slug と code だけ記入(variant・brief番号・writer番号は書かない)。
- 読んでよいもの: 担当コードの記事4ファイル、台帳 `er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt`、★fact一覧 `docs/pm/allfact_e2e_02/theme_fact_watchlist.md`、このパック内のファイル(rubric・`unprovided_checklist_<slug>.md`・`article_schema.json`・`scores_template.json`)。
- 未提示事項チェックリスト(`unprovided_checklist_<slug>.md`)は、台帳が「示されていない/不明」としている事項の一覧。記事がそれらを具体的に断定していれば、台帳にない事実の断定(added_fact、軽微以上)の判断材料にする(新たな基準は作らない。rubricの重大/軽微定義に従う)。
- **読んではいけないもの**: `er052_output/open233_b3_trial_01/runs/`、`eval/_private/`、`eval/blind/`(段階1)、`eval/blind_stage2/_briefs_for_brief_review/`、`eval/brief_features*.json`、`eval/writer_gate_stop_summary.md`、`eval/STAGE*_*.md`、`eval/inventory_*`、`docs/pm/b3_trial_01/design_01.md`、`docs/pm/b3_trial_01/aggregate_b3.py`、`docs/pm/b3_trial_01/blinding.md`、`PLAN.md`、`docs/pm/opus_l2_review_*`、`docs/pm/ACTIVE_TASK.md`。これらは条件を推測させる情報を含む。
- 評価順は assignment ファイルの順(seed固定シャッフル済み。条件順にならない)。
- 出力(1記事=1ファイル): `er052_output/open233_b3_trial_01/eval/articles/<slug>_<code>.json`(`scores_template.json` を雛形にし article_schema.json 準拠、ID形式 `<slug>-<code>-NN`)。任意の根拠メモ: `er052_output/open233_b3_trial_01/eval/notes/<slug>_<A|B>.md`。
- 自己検算: 担当全ファイルについて、JSONが読めること、IDが形式どおりで重複しないこと、stages件数=ng_items件数(s0/s1/s2それぞれ重大・軽微)、regressions件数=ng_itemsのregression=true件数であることを確認する。(`aggregate_b3.py` は全員分が揃うまでFAILが正常なので使わない。)
- 報告(8行以内): 作成ファイルの有無と件数、重大NG件数と各ID、判定保留件数、rubricで解釈に迷った点。単独評価で人間確認なしと明記。条件別の集計・推測は報告しない。

---

# rubric全文(`docs/pm/b3_trial_01/eval_rubric.md` の逐語コピー)

"""
    open(PACK + "/README_EVALUATOR.md", "w", encoding="utf-8", newline="\n").write(memo + rub)
    for t in THEMES:
        shutil.copyfile("%s/unprovided_checklist_%s.md" % (DOC, t), "%s/unprovided_checklist_%s.md" % (PACK, t))
    shutil.copyfile(DOC + "/article_schema.json", PACK + "/article_schema.json")
    # assignment
    idx = ["# 匿名記事の一覧(段階2、条件ラベルなし)", "", "記事は `er052_output/open233_b3_trial_01/eval/blind_stage2/<slug>/<code>/` 配下。各評価者は自分の assignment_*.md のコードのみ評価する。", ""]
    for t in THEMES:
        idx.append("## %s (計 %d 記事)" % (t, sum(len(v) for k, v in assign.items() if k.startswith(t + "_"))))
        for h in "AB":
            lst = assign["%s_%s" % (t, h)]
            idx.append("- 評価者 %s_%s (%d 記事、評価順): %s" % (t, h, len(lst), ", ".join(lst)))
            body = ["# 評価割当 %s_%s(%d 記事)" % (t, h, len(lst)), "",
                    "テーマ: %s。条件は開示されない。README_EVALUATOR.md と同パックの rubric に従う。下の順に評価する(順序はseed固定シャッフル済み)。" % t, "",
                    "| 順 | code | 記事ディレクトリ | 出力JSON |", "|---|---|---|---|"]
            for n, c in enumerate(lst, 1):
                body.append("| %d | %s | er052_output/open233_b3_trial_01/eval/blind_stage2/%s/%s/ | er052_output/open233_b3_trial_01/eval/articles/%s_%s.json |" % (n, c, t, c, t, c))
            body += ["", "台帳: er052_output/open233_polysemy_trial_02/ledgers/%s/control/research_ledger/verified_fact_ledger.txt" % t,
                     "未提示チェックリスト: er052_output/open233_b3_trial_01/eval/eval_pack_stage2/unprovided_checklist_%s.md" % t,
                     "根拠メモ(任意): er052_output/open233_b3_trial_01/eval/notes/%s_%s.md" % (t, h)]
            open("%s/assignment_%s_%s.md" % (PACK, t, h), "w", encoding="utf-8", newline="\n").write("\n".join(body) + "\n")
        idx.append("")
    open(PACK + "/articles_index.md", "w", encoding="utf-8", newline="\n").write("\n".join(idx))
    tmpl = {"slug": "<meta|hormuz|space_weapons>", "code": "<匿名記事コード>",
            "stages": {"s0_r0": {"major": 0, "minor": 0}, "s1_ja": {"major": 0, "minor": 0}, "s2_en": {"major": 0, "minor": 0}},
            "regressions": {"major": 0, "minor": 0},
            "direction_facts": [{"fact_id": "<例 HC-012>", "label": "correct|ambiguous|misread|not_selected"}],
            "ng_items": [{"id": "<slug>-<code>-01", "text": "<該当文>", "fact_id": "<例 HF-003>", "severity": "major|minor",
                          "stage": {"s0": False, "s1": True, "s2": True}, "cross_fact": False, "regression": False,
                          "kind": "subject|object|scope|time|negation|causal|added_fact"}],
            "pending": [], "notes": "<単独評価、人間確認なし。解釈に迷った点>"}
    json.dump(tmpl, open(PACK + "/scores_template.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    json.dump({"seed": ns.seed, "assign_balance": bal, "note": "評価者非公開(条件配分の記録)"}, open(EV + "/_private/assignment_balance.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2, sort_keys=True)
    print("assign:", {k: len(v) for k, v in assign.items()})
    print("balance:", json.dumps(bal, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
