# -*- coding: utf-8 -*-
"""OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 A1: 盲検再採点パック生成(決定論・標準ライブラリのみ・API/生成なし、0円)。"""
import glob, hashlib, json, os, random, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = "er052_output/open233_ng_root_cause_01"
B3 = "er052_output/open233_b3_trial_01/eval"
E2 = "er052_output/open233_allfact_note_e2e_02/runs"
T4 = "er052_output/open233_polysemy_trial_04/runs"
DOC = "docs/pm/b3_trial_01"
SEED = "20261007rca"
THEMES = ["meta", "hormuz", "space_weapons", "sewer", "ai_control"]
ALPHA = "abcdefghjkmnpqrstuvwxyz23456789"
JA = ["original.md", "revision1.md", "revision2.md"]
EVALS = "ABC"


def code_for(key, taken):
    h = hashlib.sha256(("%s|%s" % (SEED, key)).encode()).digest()
    n = 4
    while True:
        c = "".join(ALPHA[b % len(ALPHA)] for b in h[:n])
        if c not in taken:
            return c
        n += 1
        h = hashlib.sha256(h).digest()


def final_en(run_dir):
    """Checker最終出力(ユーザーに届くEN)=最後にen_text_after_rewriteが非空のcycle。無ければb1b/article.md(Rewriteなし=同一)。"""
    pre = open(run_dir + "/b1b/article.md", encoding="utf-8", newline="").read()
    fs = glob.glob(run_dir + "/checker/runs/*.json")
    assert len(fs) == 1, run_dir
    d = json.load(open(fs[0], encoding="utf-8"))
    txt, cyc = None, None
    for c in d["cycles"]:
        v = c.get("en_text_after_rewrite")
        if v:
            txt, cyc = v, c["cycle"]
    if txt is None:
        return pre, pre, "b1b(Rewriteなし)", d["final_state"]
    return txt, pre, "checker cycle%d en_text_after_rewrite" % cyc, d["final_state"]


def main():
    os.chdir(ROOT)
    taken = set()
    for pat in (B3 + "/blind/*/*", B3 + "/blind_stage2/*/*"):
        for p in glob.glob(pat):
            taken.add(os.path.basename(p))
    mp_b3 = json.load(open(B3 + "/_private/MAP_stage2.json", encoding="utf-8"))["articles"]
    items = []
    for s in THEMES:
        items.append(("E2E02_control", s, "%s|control" % s, "%s/%s/control/rep1" % (T4, s)))
        for r in (1, 2):
            items.append(("E2E02_P2", s, "%s|p2|rep%d" % (s, r), "%s/%s/nb/p2/rep%d" % (E2, s, r)))
    for k, e in sorted(mp_b3.items()):
        if e["variant"] == "V0":
            s, c = k.split("/")
            items.append(("B3_V0", s, "%s|v0|%s" % (s, c), "%s/blind_stage2/%s/%s" % (B3, s, c)))
    mp = {}
    recs = []
    for origin, s, key, src in items:
        code = code_for(key, taken)
        taken.add(code)
        dst = "%s/blind/%s/%s" % (OUT, s, code)
        os.makedirs(dst + "/ja_writer", exist_ok=True)
        os.makedirs(dst + "/b1b", exist_ok=True)
        for f in JA:
            shutil.copyfile("%s/ja_writer/%s" % (src, f), "%s/ja_writer/%s" % (dst, f))
        differs = False
        if origin == "B3_V0":
            shutil.copyfile(src + "/b1b/article.md", dst + "/b1b/article.md")
            en_src, st = "B3 blind_stage2 b1b/article.md(Checkerなし)", None
        else:
            txt, pre, en_src, st = final_en(src)
            open(dst + "/b1b/article.md", "w", encoding="utf-8", newline="").write(txt)
            pdir = "%s/_private/pre_checker_en/%s" % (OUT, s)
            os.makedirs(pdir, exist_ok=True)
            open("%s/%s.md" % (pdir, code), "w", encoding="utf-8", newline="").write(pre)
            differs = pre != txt
        mp["%s/%s" % (s, code)] = {"origin": origin, "src": src, "en_adopted": en_src,
                                   "checker_final_state": st, "en_differs_from_b1b": differs}
        recs.append((origin, s, code))
    os.makedirs(OUT + "/_private", exist_ok=True)
    json.dump({"seed": SEED, "articles": mp, "note": "評価者に渡さない"},
              open(OUT + "/_private/MAP_rca.json", "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=2, sort_keys=True)
    assign = {e: [] for e in EVALS}
    n = 0
    for o in ("E2E02_control", "E2E02_P2", "B3_V0"):
        lst = sorted([(s, c) for oo, s, c in recs if oo == o])
        random.Random("%s|deal|%s" % (SEED, o)).shuffle(lst)
        for it in lst:
            assign[EVALS[n % 3]].append(it)
            n += 1
    bal = {}
    for e in EVALS:
        lst = sorted(assign[e])
        random.Random("%s|order|%s" % (SEED, e)).shuffle(lst)
        assign[e] = lst
        b = {}
        for s, c in lst:
            o = mp["%s/%s" % (s, c)]["origin"]
            b[o] = b.get(o, 0) + 1
        bal[e] = {"n": len(lst), "by_origin": b}
    flat = [x for e in EVALS for x in assign[e]]
    assert len(flat) == len(set(flat)) == len(recs)
    P = OUT + "/eval_pack"
    os.makedirs(P, exist_ok=True)
    rub = open(DOC + "/eval_rubric.md", encoding="utf-8", newline="").read()
    BP = OUT + "/blind"
    memo = """# 評価者向け README(OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 再採点、B3段階2のREADMEを流用)

あなたは記事評価者(1インスタンス)です。API呼び出し・記事生成・SSOT編集・git操作・記事本文の編集は禁止です。条件(どの生成方法の記事か)は開示されていません。推測もしないでください。

## 適用メモ(下のrubric全文の読み替え。判定基準そのものは変更なし)
- rubric内の「24匿名記事(計72)」は読み替え: あなたの担当は `assignment_rca_<A|B|C>.md` に列挙された記事コードのみ(テーマは記事ごとに異なる: meta/hormuz/space_weapons/sewer/ai_control)。
- rubric 7節の記事パス `eval/blind/<slug>/<code>/` は **`%(BP)s/<slug>/<code>/`** に読み替える。各コードの下に `ja_writer/original.md`(R0), `ja_writer/revision1.md`(R1), `ja_writer/revision2.md`(R2), `b1b/article.md`(EN。最終EN)。
- rubric 1節の「Checkerなし(ENのb1bが最終)」は読み替え: 各コード下の `b1b/article.md` を最終ENとして扱う(追加の工程はない)。
- 出力JSONの slug と code だけ記入する(variant・出所・rep番号は書かない)。
- 読んでよいもの: 担当コードの記事4ファイル、台帳 `er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt`(担当記事のテーマのもの)、★fact一覧 `docs/pm/allfact_e2e_02/theme_fact_watchlist.md`、このパック内のファイル(rubric・`unprovided_checklist_<slug>.md`・`article_schema.json`・`scores_template.json`)。
- 未提示事項チェックリスト(`unprovided_checklist_<slug>.md`)は、台帳が「示されていない/不明」としている事項の一覧。meta/hormuz/space_weapons のみ作成済みで、sewer/ai_control は「該当なし」(未作成。判断材料に使えないだけで、台帳にない事実の断定は通常どおりrubricで判定する)。記事がチェックリストの事項を具体的に断定していれば、台帳にない事実の断定(added_fact、軽微以上)の判断材料にする(新たな基準は作らない。rubricの重大/軽微定義に従う)。
- rubricの7節にある「書式例: .../eval/stagewise/NG_meta.md」「定義: .../STAGEWISE_SUMMARY.md」は **読まない**(過去の採点結果なので読み替え不可。定義はrubric本文の2節のみを使う)。
- **読んではいけないもの**: `%(OUT)s/_private/`、`%(OUT)s/tools/`、`%(OUT)s/PREP_NOTE.md`、`er052_output/open233_allfact_note_e2e_02/`(全体)、`er052_output/open233_polysemy_trial_04/`、`er052_output/open233_b3_trial_01/`(全体。runs/・eval/・blind類・過去の採点JSON含む)、`docs/pm/allfact_e2e_02/` のうち theme_fact_watchlist.md 以外、`docs/pm/b3_trial_01/` 全体、`docs/pm/ng_root_cause_01/`、`docs/pm/opus_l2_review_*`、`docs/pm/ACTIVE_TASK.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、過去の評価シート(`E_*.md`、`NG_*.md`、`STAGEWISE_SUMMARY.md`、`SUMMARY*.md`)。これらは条件や過去の採点結果を推測させる情報を含む。
- 評価順は assignment ファイルの順(seed固定シャッフル済み。条件順にならない)。
- 出力(1記事=1ファイル): `%(OUT)s/eval/articles/<slug>_<code>.json`(`scores_template.json` を雛形にし article_schema.json 準拠、ID形式 `<slug>-<code>-NN`)。任意の根拠メモ: `%(OUT)s/eval/notes/rca_<A|B|C>.md`。
- 自己検算: 担当全ファイルについて、JSONが読めること、IDが形式どおりで重複しないこと、stages件数=ng_items件数(s0/s1/s2それぞれ重大・軽微)、regressions件数=ng_itemsのregression=true件数であることを確認する。
- 報告(8行以内): 作成ファイルの有無と件数、重大NG件数と各ID、判定保留件数、rubricで解釈に迷った点。単独評価で人間確認なしと明記。条件別の集計・推測は報告しない。

---

# rubric全文(`docs/pm/b3_trial_01/eval_rubric.md` の逐語コピー)

""" % {"BP": BP, "OUT": OUT}
    open(P + "/README_EVALUATOR.md", "w", encoding="utf-8", newline="").write(memo + rub)
    for t in ("meta", "hormuz", "space_weapons"):
        shutil.copyfile("%s/unprovided_checklist_%s.md" % (DOC, t), "%s/unprovided_checklist_%s.md" % (P, t))
    for t in ("sewer", "ai_control"):
        open("%s/unprovided_checklist_%s.md" % (P, t), "w", encoding="utf-8", newline="\n").write(
            "# unprovided_checklist_%s: 該当なし\n\nB3 Trialに本テーマのチェックリストが無いため、新規作成していない。台帳のみで判定する。\n" % t)
    sch = json.load(open(DOC + "/article_schema.json", encoding="utf-8"))
    sch["properties"]["slug"]["enum"] = THEMES
    sch["title"] = "ng_root_cause_01 article record (1 article, 匿名コード方式; slug enumにsewer/ai_controlを追加した以外はB3 schemaと同一)"
    sch["description"] = "評価者は slug と code(%s/<slug>/<code>/ の匿名コード)だけを書く。出所・variantは書かない。" % BP
    json.dump(sch, open(P + "/article_schema.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    idx = ["# 匿名記事の一覧(条件ラベルなし)", "",
           "記事は `%s/<slug>/<code>/` 配下。各評価者は自分の assignment_rca_*.md のコードのみ評価する。" % BP, ""]
    for e in EVALS:
        lst = assign[e]
        idx.append("- 評価者 rca_%s (%d 記事、評価順): %s" % (e, len(lst), ", ".join("%s/%s" % x for x in lst)))
        body = ["# 評価割当 rca_%s(%d 記事)" % (e, len(lst)), "",
                "条件は開示されない。README_EVALUATOR.md と同パックの rubric に従う。下の順に評価する(順序はseed固定シャッフル済み)。", "",
                "| 順 | テーマ | code | 記事ディレクトリ | 台帳 | 出力JSON |", "|---|---|---|---|---|---|"]
        for i, (s, c) in enumerate(lst, 1):
            body.append("| %d | %s | %s | %s/%s/%s/ | er052_output/open233_polysemy_trial_02/ledgers/%s/control/research_ledger/verified_fact_ledger.txt | %s/eval/articles/%s_%s.json |" % (i, s, c, BP, s, c, s, OUT, s, c))
        body += ["", "未提示チェックリスト: %s/unprovided_checklist_<slug>.md(sewer/ai_controlは該当なし)" % P,
                 "根拠メモ(任意): %s/eval/notes/rca_%s.md" % (OUT, e)]
        open("%s/assignment_rca_%s.md" % (P, e), "w", encoding="utf-8", newline="\n").write("\n".join(body) + "\n")
    open(P + "/articles_index.md", "w", encoding="utf-8", newline="\n").write("\n".join(idx) + "\n")
    tm = json.load(open(B3 + "/eval_pack_stage2/scores_template.json", encoding="utf-8"))
    tm["slug"] = "<meta|hormuz|space_weapons|sewer|ai_control>"
    json.dump(tm, open(P + "/scores_template.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    json.dump({"seed": SEED, "assign_balance": bal, "assign": {e: ["%s/%s" % x for x in assign[e]] for e in EVALS},
               "note": "評価者非公開"},
              open(OUT + "/_private/assignment_balance_rca.json", "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=2, sort_keys=True)
    print(len(recs), json.dumps(bal, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
