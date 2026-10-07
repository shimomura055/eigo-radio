# -*- coding: utf-8 -*-
"""make_eval_pack_ccp.py: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 盲検評価パック生成(決定論・標準ライブラリのみ・API/生成なし、0円)。

流用元: docs/pm/b3_trial_01/make_eval_pack.py(README逐語流用)と er052_output/open233_ng_root_cause_01/tools/make_rca_pack.py(Checker最終EN抽出・匿名コード)。
入力: <runs-root>/<slug>/<variant>/rep<k>/ (meta=nb 10本、hormuz/space_weapons/sewer/ai_control=control 各2本=計18)
出力: <eval-root>/blind/<slug>/<code>/{ja_writer/{original,revision1,revision2}.md, b1b/article.md(=Checker最終EN), b1b/pre_checker.md(=Checker前EN)}
      <eval-root>/eval_pack/ (README_EVALUATOR.md, assignment_ccp_<A|B|C>.md, assignment_rollback_X.md, article_schema.json, scores_template.json,
      rollback_label_template.json, unprovided_checklist_*.md, articles_index.md)
      <eval-root>/_private/{MAP_ccp.json, run_facts.json, assignment_balance_ccp.json} (評価者に渡さない)
usage: python make_eval_pack_ccp.py [--runs-root R] [--eval-root E] [--seed S] [--expect 18]
"""
import argparse, glob, hashlib, json, os, random, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
TRIAL = "er052_output/open233_control_checker_polysemy_trial_01"
DOC = "docs/pm/b3_trial_01"
CCP = "docs/pm/control_checker_polysemy_trial_01"
THEMES = ["meta", "hormuz", "space_weapons", "sewer", "ai_control"]
VARIANT = {"meta": "nb", "hormuz": "control", "space_weapons": "control", "sewer": "control", "ai_control": "control"}
ALPHA = "abcdefghjkmnpqrstuvwxyz23456789"
JA = ["original.md", "revision1.md", "revision2.md"]
EVALS = "ABC"


def code_for(seed, key, taken):
    h = hashlib.sha256(("%s|%s" % (seed, key)).encode()).digest()
    n = 4
    while True:
        c = "".join(ALPHA[b % len(ALPHA)] for b in h[:n])
        if c not in taken:
            return c
        n += 1
        h = hashlib.sha256(h).digest()


def read(p):
    return open(p, encoding="utf-8", newline="").read()


def checker_result(run_dir):
    fs = glob.glob(run_dir + "/checker/runs/*.json")
    assert len(fs) == 1, ("checker result not unique", run_dir, fs)
    return json.load(open(fs[0], encoding="utf-8"))


def final_en(run_dir, d):
    """Checker最終出力(ユーザーに届くEN)=最後にen_text_after_rewriteが非空のcycle。無ければb1b/article.md(Rewriteなし=同一)。"""
    pre = read(run_dir + "/b1b/article.md")
    txt = None
    for c in d["cycles"]:
        v = c.get("en_text_after_rewrite")
        if v:
            txt = v
    return (txt if txt is not None else pre), pre


def run_facts(run_dir, d):
    cyc = d.get("cycles") or []
    nrw = sum(len(c.get("rewrite_records") or []) for c in cyc)
    fired = any((c.get("blocking_count") or 0) > 0 or (c.get("rewrite_records") or []) for c in cyc)
    cost = {}
    try:
        cost["pipeline_total_jpy"] = json.load(open(run_dir + "/cost.json", encoding="utf-8")).get("total_jpy")
    except Exception:
        cost["pipeline_total_jpy"] = None
    cost["checker_jpy"] = d.get("run_cost_jpy")
    return {"final_state": d.get("final_state"), "n_cycles": len(cyc), "n_rewrite_records": nrw,
            "checker_fired": fired, "cost": cost}


def enumerate_runs(runs_root):
    out = []
    for s in THEMES:
        base = "%s/%s/%s" % (runs_root, s, VARIANT[s])
        for rd in sorted(glob.glob(base + "/rep*"), key=lambda x: int(x.rsplit("rep", 1)[1])):
            need = [rd + "/ja_writer/revision2.md", rd + "/b1b/article.md"]
            if all(os.path.exists(p) for p in need) and glob.glob(rd + "/checker/runs/*.json"):
                out.append((s, os.path.basename(rd), rd))
    return out


MEMO = """# 評価者向け README(OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01、B3段階2のREADMEを流用)

あなたは記事評価者(1インスタンス)です。API呼び出し・記事生成・SSOT編集・git操作・記事本文の編集は禁止です。条件(どの生成方法の記事か)は開示されていません。推測もしないでください。

## 適用メモ(下のrubric全文の読み替え。判定基準そのものは変更なし)
- rubric内の「24匿名記事(計72)」は読み替え: あなたの担当は `assignment_ccp_<A|B|C>.md` に列挙された記事コードのみ(テーマは記事ごとに異なる: meta/hormuz/space_weapons/sewer/ai_control)。
- rubric 7節の記事パス `eval/blind/<slug>/<code>/` は **`%(BP)s/<slug>/<code>/`** に読み替える。各コードの下に `ja_writer/original.md`(R0), `ja_writer/revision1.md`(R1), `ja_writer/revision2.md`(R2), `b1b/article.md`(EN最終), `b1b/pre_checker.md`(ENのChecker前)。
- rubric 1節の「Checkerなし(ENのb1bが最終)」は読み替え: **`b1b/article.md` が最終EN(Checker通過後。ユーザーに届くEN)**。stage s2_en は `b1b/article.md` を対象とする。`b1b/pre_checker.md` は『Checkerが何を直したか』の判定にだけ使う(下記)。両者が同一なら『Checkerは直していない』。
- 追加の任意フィールド(スキーマ追加): `checker_rewrites`。`b1b/pre_checker.md` と `b1b/article.md` を比べ、変更された文ごとに {before, after, before_was_ng: true|false|unclear(変更前の文が台帳に照らしNGだったか), after_new_ng: none|minor|major(変更後の文に新たなNGが生じたか。変更前の誤りが残っただけなら none)} を記す。変更が無ければ空配列。
- 追加の任意フィールド(スキーマ追加、metaのみ): `rollback_labels`。fact MUSE-HC-012(「ロールバック」)を記事が扱っている場合、ja_r2 / en_pre_checker / en_final の3箇所を `correct|ambiguous|misread|not_selected` の3値で判定し、根拠の1文を引用する。判定基準は `rollback_label_template.json` の `criteria`(逐語)に従う。他テーマでは省略。
- 出力JSONの slug と code だけ記入する(variant・出所・rep番号は書かない)。
- 読んでよいもの: 担当コードの記事ファイル、台帳 `er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt`(担当記事のテーマのもの)、★fact一覧 `docs/pm/allfact_e2e_02/theme_fact_watchlist.md`、このパック内のファイル(rubric・`unprovided_checklist_<slug>.md`・`article_schema.json`・`scores_template.json`・`rollback_label_template.json`)。
- 未提示事項チェックリスト(`unprovided_checklist_<slug>.md`)は、台帳が「示されていない/不明」としている事項の一覧。meta/hormuz/space_weapons のみ作成済みで、sewer/ai_control は台帳のみで判定する。記事がそれらを具体的に断定していれば、台帳にない事実の断定(added_fact、軽微以上)の判断材料にする(新たな基準は作らない)。
- rubricの7節にある「書式例: .../eval/stagewise/NG_meta.md」「定義: .../STAGEWISE_SUMMARY.md」は **読まない**(過去の採点結果)。定義はrubric本文の2節を使う。
- **読んではいけないもの**: `%(EV)s/_private/`、`%(TR)s/runs/`、`er052_output/open233_allfact_note_e2e_02/`(全体)、`er052_output/open233_polysemy_trial_04/`、`er052_output/open233_meta_rollback_minimal_note_01/`、`er052_output/open233_b3_trial_01/`、`er052_output/open233_ng_root_cause_01/`、`docs/pm/control_checker_polysemy_trial_01/`(plan/preregistration含む)、`docs/pm/ACTIVE_TASK.md`、`docs/pm/opus_l2_review_*`、`docs/pm/b3_trial_01/design_01.md`。これらは条件を推測させる情報を含む。
- 評価順は assignment ファイルの順(seed固定シャッフル済み)。
- 出力(1記事=1ファイル): `%(EV)s/articles/<slug>_<code>.json`(`scores_template.json` を雛形にし article_schema.json 準拠、ID形式 `<slug>-<code>-NN`)。任意の根拠メモ: `%(EV)s/notes/ccp_<A|B|C>.md`。
- 自己検算: 担当全ファイルについて、JSONが読めること、IDが形式どおりで重複しないこと、stages件数=ng_items件数(s0/s1/s2それぞれ重大・軽微)、regressions件数=ng_itemsのregression=true件数であることを確認する。
- 報告(8行以内): 作成ファイルの有無と件数、重大NG件数と各ID、判定保留件数、metaのrollback_labels、rubricで解釈に迷った点。単独評価で人間確認前と明記。条件別の集計・推測は報告しない。

---

# rubric全文(`docs/pm/b3_trial_01/eval_rubric.md` の逐語コピー)

"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", default=TRIAL + "/runs")
    ap.add_argument("--eval-root", default=TRIAL + "/eval")
    ap.add_argument("--seed", default="20261007ccp")
    ap.add_argument("--expect", type=int, default=18)
    ns = ap.parse_args(argv)
    os.chdir(ROOT)
    runs = enumerate_runs(ns.runs_root)
    if len(runs) != ns.expect:
        raise SystemExit("完了run数が想定(%d)と一致しない: %d(STOP。未完run/Gate STOPを確認してから再実行)" % (ns.expect, len(runs)))
    EV = ns.eval_root
    BP, PK, PV = EV + "/blind", EV + "/eval_pack", EV + "/_private"
    taken, mp, facts, recs = set(), {}, {}, []
    for s, rep, rd in runs:
        code = code_for(ns.seed, "%s|%s" % (s, rep), taken)
        taken.add(code)
        d = checker_result(rd)
        txt, pre = final_en(rd, d)
        dst = "%s/%s/%s" % (BP, s, code)
        os.makedirs(dst + "/ja_writer", exist_ok=True)
        os.makedirs(dst + "/b1b", exist_ok=True)
        for f in JA:
            shutil.copyfile("%s/ja_writer/%s" % (rd, f), "%s/ja_writer/%s" % (dst, f))
        open(dst + "/b1b/article.md", "w", encoding="utf-8", newline="").write(txt)
        open(dst + "/b1b/pre_checker.md", "w", encoding="utf-8", newline="").write(pre)
        rf = run_facts(rd, d)
        rf["en_differs_from_pre_checker"] = (txt != pre)
        mp["%s/%s" % (s, code)] = {"slug": s, "variant": VARIANT[s], "rep": rep, "src": rd, "polysemy_note": (s == "meta")}
        facts["%s/%s" % (s, code)] = rf
        recs.append((s, code))
    os.makedirs(PV, exist_ok=True)
    json.dump({"seed": ns.seed, "articles": mp, "note": "評価者に渡さない"}, open(PV + "/MAP_ccp.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2, sort_keys=True)
    json.dump({"run_facts": facts, "note": "評価者に渡さない(Checker発火・費用等)"}, open(PV + "/run_facts.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2, sort_keys=True)
    # 3評価者へ割当: テーマ別にseed固定シャッフル後、通しカウンタで巡回(テーマが評価者間で偏らない。条件は出力に書かない)
    assign = {e: [] for e in EVALS}
    n = 0
    for s in THEMES:
        lst = sorted(c for ss, c in recs if ss == s)
        random.Random("%s|deal|%s" % (ns.seed, s)).shuffle(lst)
        for c in lst:
            assign[EVALS[n % 3]].append((s, c))
            n += 1
    bal = {}
    for e in EVALS:
        lst = sorted(assign[e])
        random.Random("%s|order|%s" % (ns.seed, e)).shuffle(lst)
        assign[e] = lst
        b = {}
        for s, c in lst:
            b[s] = b.get(s, 0) + 1
        bal[e] = {"n": len(lst), "by_theme": b}
    flat = [x for e in EVALS for x in assign[e]]
    assert len(flat) == len(set(flat)) == len(recs)
    meta_codes = sorted(c for s, c in recs if s == "meta")
    random.Random("%s|order|X" % ns.seed).shuffle(meta_codes)
    os.makedirs(PK, exist_ok=True)
    rub = read(DOC + "/eval_rubric.md")
    open(PK + "/README_EVALUATOR.md", "w", encoding="utf-8", newline="").write(MEMO % {"BP": BP, "EV": EV, "TR": TRIAL} + rub)
    for t in ("meta", "hormuz", "space_weapons"):
        shutil.copyfile("%s/unprovided_checklist_%s.md" % (DOC, t), "%s/unprovided_checklist_%s.md" % (PK, t))
    for t in ("sewer", "ai_control"):
        open("%s/unprovided_checklist_%s.md" % (PK, t), "w", encoding="utf-8", newline="\n").write(
            "# unprovided_checklist_%s: 該当なし\n\nB3 Trialに本テーマのチェックリストが無いため、新規作成していない。台帳のみで判定する。\n" % t)
    sch = json.load(open(DOC + "/article_schema.json", encoding="utf-8"))
    sch["properties"]["slug"]["enum"] = THEMES
    sch["title"] = "ccp_trial article record (1 article, 匿名コード方式; slug enum拡張と任意フィールドchecker_rewrites/rollback_labels追加以外はB3 schemaと同一)"
    sch["description"] = "評価者は slug と code(%s/<slug>/<code>/ の匿名コード)だけを書く。出所・variantは書かない。" % BP
    sch["properties"]["checker_rewrites"] = {"type": "array", "items": {"type": "object", "required": ["before", "after", "before_was_ng", "after_new_ng"], "properties": {
        "before": {"type": "string"}, "after": {"type": "string"},
        "before_was_ng": {"enum": ["true", "false", "unclear"]}, "after_new_ng": {"enum": ["none", "minor", "major"]}}}}
    sch["properties"]["rollback_labels"] = {"type": "object", "description": "metaのみ。MUSE-HC-012の3値", "properties": {
        k: {"type": "object", "properties": {"label": {"enum": ["correct", "ambiguous", "misread", "not_selected"]}, "quote": {"type": "string"}}}
        for k in ("ja_r2", "en_pre_checker", "en_final")}}
    json.dump(sch, open(PK + "/article_schema.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    shutil.copyfile(CCP + "/rollback_label_template.json", PK + "/rollback_label_template.json")
    idx = ["# 匿名記事の一覧(条件ラベルなし)", "", "記事は `%s/<slug>/<code>/` 配下。各評価者は自分の assignment_ccp_*.md のコードのみ評価する。" % BP, ""]
    for e in EVALS:
        lst = assign[e]
        idx.append("- 評価者 ccp_%s (%d 記事、評価順): %s" % (e, len(lst), ", ".join("%s/%s" % x for x in lst)))
        body = ["# 評価割当 ccp_%s(%d 記事)" % (e, len(lst)), "",
                "条件は開示されない。README_EVALUATOR.md と同パックの rubric に従う。下の順に評価する(順序はseed固定シャッフル済み)。", "",
                "| 順 | テーマ | code | 記事ディレクトリ | 台帳 | 出力JSON |", "|---|---|---|---|---|---|"]
        for i, (s, c) in enumerate(lst, 1):
            body.append("| %d | %s | %s | %s/%s/%s/ | er052_output/open233_polysemy_trial_02/ledgers/%s/control/research_ledger/verified_fact_ledger.txt | %s/articles/%s_%s.json |" % (i, s, c, BP, s, c, s, EV, s, c))
        body += ["", "未提示チェックリスト: %s/unprovided_checklist_<slug>.md(sewer/ai_controlは該当なし)" % PK,
                 "根拠メモ(任意): %s/notes/ccp_%s.md" % (EV, e)]
        open("%s/assignment_ccp_%s.md" % (PK, e), "w", encoding="utf-8", newline="\n").write("\n".join(body) + "\n")
    bx = ["# 評価割当 rollback_X(label-only、metaの全記事 %d 本)" % len(meta_codes), "",
          "あなたは別インスタンスの第2評価者です。fact MUSE-HC-012(「ロールバック」)の3値ラベルだけを、JA R2 / EN Checker前 / EN最終 の3箇所について判定します。重大/軽微のrubric評価は行いません。他の評価者の結果・条件は読みません。", "",
          "基準: `rollback_label_template.json` の criteria(逐語)。出力: `%s/rollback_x/meta_<code>.json`(rollback_label_template.json の形式)。" % EV, "",
          "| 順 | code | 記事ディレクトリ |", "|---|---|---|"]
    for i, c in enumerate(meta_codes, 1):
        bx.append("| %d | %s | %s/meta/%s/ |" % (i, c, BP, c))
    open(PK + "/assignment_rollback_X.md", "w", encoding="utf-8", newline="\n").write("\n".join(bx) + "\n")
    idx.append("- 評価者 rollback_X (label-only, %d 記事、評価順): %s" % (len(meta_codes), ", ".join("meta/" + c for c in meta_codes)))
    open(PK + "/articles_index.md", "w", encoding="utf-8", newline="\n").write("\n".join(idx) + "\n")
    tmpl = {"slug": "<meta|hormuz|space_weapons|sewer|ai_control>", "code": "<匿名記事コード>",
            "stages": {"s0_r0": {"major": 0, "minor": 0}, "s1_ja": {"major": 0, "minor": 0}, "s2_en": {"major": 0, "minor": 0}},
            "regressions": {"major": 0, "minor": 0},
            "direction_facts": [{"fact_id": "<例 HC-012>", "label": "correct|ambiguous|misread|not_selected"}],
            "ng_items": [{"id": "<slug>-<code>-01", "text": "<該当文>", "fact_id": "<例 HF-003>", "severity": "major|minor",
                          "stage": {"s0": False, "s1": True, "s2": True}, "cross_fact": False, "regression": False,
                          "kind": "subject|object|scope|time|negation|causal|added_fact"}],
            "pending": [],
            "checker_rewrites": [{"before": "<Checker前の文>", "after": "<Checker後の文>", "before_was_ng": "true|false|unclear", "after_new_ng": "none|minor|major"}],
            "rollback_labels": {"ja_r2": {"label": "correct|ambiguous|misread|not_selected", "quote": ""}, "en_pre_checker": {"label": "", "quote": ""}, "en_final": {"label": "", "quote": ""}},
            "notes": "<単独評価、人間確認前。解釈に迷った点>"}
    json.dump(tmpl, open(PK + "/scores_template.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    json.dump({"seed": ns.seed, "assign_balance": bal, "assign": {e: ["%s/%s" % x for x in assign[e]] for e in EVALS},
               "rollback_x_meta": meta_codes, "note": "評価者非公開"},
              open(PV + "/assignment_balance_ccp.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2, sort_keys=True)
    print(len(recs), json.dumps(bal, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
