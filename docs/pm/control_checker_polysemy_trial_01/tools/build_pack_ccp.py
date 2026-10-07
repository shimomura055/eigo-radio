# -*- coding: utf-8 -*-
"""HUMAN_REVIEW_PACK.md 生成(決定論・API無し)。台帳fact・記事該当文は原文のまま抽出(要約・加工しない)。"""
import json, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
B = "er052_output/open233_control_checker_polysemy_trial_01"
EV = B + "/eval"
RAW = "https://raw.githubusercontent.com/shimomura055/eigo-radio/main/"
MAP = json.load(open(EV + "/_private/MAP_ccp.json", encoding="utf-8"))["articles"]
AGG = json.load(open(EV + "/aggregate_ccp.json", encoding="utf-8"))


def rd(p):
    return open(p, encoding="utf-8").read()


def art(slug, code):
    return json.load(open("%s/articles/%s_%s.json" % (EV, slug, code), encoding="utf-8"))


def rundir(slug, code):
    return MAP["%s/%s" % (slug, code)]["src"].replace("\\", "/")


def ledger(slug, code, fid):
    t = rd(rundir(slug, code) + "/research_ledger/verified_fact_ledger.txt")
    m = re.search(r"\[VERIFIED\] " + re.escape(fid) + r":.*?(?=\n\n|\Z)", t, re.S)
    return m.group(0).strip() if m else "(台帳に %s なし)" % fid


def paths(slug, code):
    b = "%s/blind/%s/%s" % (EV, slug, code)
    return {"ja": b + "/ja_writer/revision2.md", "pre": b + "/b1b/pre_checker.md", "en": b + "/b1b/article.md"}


def sents(text):
    t = text.replace("\n", "\n\u0000")
    parts = re.split(r"(?<=[。!?！？])|(?<=[.!?])\s+", t)
    return [p.replace("\u0000", "").strip() for p in parts if p.replace("\u0000", "").strip()]


def find(text, kws, ctx=1):
    """kwを含む文(と直前ctx文)を返す。無ければ空文字。"""
    ss = sents(text)
    out = []
    for i, s in enumerate(ss):
        if any(k in s for k in kws):
            seg = ss[max(0, i - ctx):i + 1]
            out.append(" ".join(seg))
    return out[0] if out else ""


def para(text, key):
    for p in re.split(r"\n\s*\n", text):
        if key in p:
            return p.strip()
    return "(該当段落を特定できず)"


def url(path):
    return RAW + path


def quote_check(text, q):
    return q in text


L = []
w = L.append
rb = {r["code"]: r for r in AGG["rollback_rows"]}
order = sorted(rb.values(), key=lambda r: int(r["rep"].replace("rep", "")))
ha = len(order)
w("# HUMAN_REVIEW_PACK: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(委任_03、2026-10-07)")
w("")
w("**注意: ここにある『正/曖/誤』『重大/軽微』『改善/悪化』の判定は評価インスタンス(盲検、単独判定)の確認前判定です。あなたの回答で確定します。**")
w("目安15〜20分。各ブロックの `ユーザー回答欄` に記入してください(原文は要約・加工せず抜粋。URLはcommit・push済み、記事全文)。Production変更なし/API費用¥0。")
w("")
w("## 回答の仕方(先に読む)")
w("- (a) Rollback10件: 『人間コンシェルジュ機能』を当面取りやめた/止めた事実を読者が正しく受け取れるか。**正**=『機能が提供されない』と読める。**曖**=どちらにも読める(『元に戻した』『ロールバックした』のまま)。**誤**=『機能が復活した/再提供した』と読める。")
w("- (b) 重大候補5件: その文は読者に誤った理解を与えるか。**重大**(意味が変わる)/**軽微**(曖昧・過剰断定)/**問題なし**。")
w("- (c) Checkerの書換え4件(+参考4件): 変更後は変更前より**改善**/**中立**/**悪化**。")
w("- (d) rep10のNote位置: 判定への影響の確認(1件、記入は任意)。")
w("")
w("## 収録件数")
w("- (a) H2: 10件(Meta全10、評価者とrollback_Xの不一致は0件のためH3該当なし)。 (b) H1相当(重大は0件のため、評価者が『重大寄りの境界』『境界』とした候補): 5件。 (c) H4(重大の新規NGは0件のため、Checker Rewriteの前後比較): 詳細4件+参考4件。 (d) 1件。")
w("- 重大と評価された記事: 0/18。確認結果で重大が出た場合のみ preregistration の②・⑤を更新します。")
w("")
# ---------------- (a)
sel = ledger("meta", order[0]["code"], "MUSE-HC-012")
note_line = [ln for ln in rd(rundir("meta", order[0]["code"]) + "/storyline_b3/selected_brief.md").splitlines() if ln.startswith("注意(多義)")][0]
w("## (a) Rollback(MUSE-HC-012)10件 [H2]")
w("### 全件共通: 台帳HC-012原文(Meta10本とも同一台帳)")
w("```")
w(sel)
w("```")
w("### 全件共通: 固定最小Note本文(briefへ逐語転記、全10本で転記を確認)")
w("```")
w(note_line)
w("```")
w("(注: 台帳HC-012の notes_for_writer にある『「サービス全体を停止した」とは書かない』は、旧規則では転記されない(仕様どおり、0/12当時と同一条件)。)")
w("")
for i, r in enumerate(order, 1):
    a = art("meta", r["code"])
    p = paths("meta", r["code"])
    ja, pre, en = rd(p["ja"]), rd(p["pre"]), rd(p["en"])
    q = {k: a["rollback_labels"][k]["quote"] for k in ("ja_r2", "en_pre_checker", "en_final")}
    ok = [quote_check(ja, q["ja_r2"]), quote_check(pre, q["en_pre_checker"]), quote_check(en, q["en_final"])]
    lab = {"correct": "正", "ambiguous": "曖", "misread": "誤", "not_selected": "対象外"}
    w("### #a-%02d meta %s (%s) (種別: rollback)" % (i, r["code"], r["rep"]))
    w("- 台帳該当fact: MUSE-HC-012(共通、上掲)")
    w("- 記事該当文(原文):")
    w("  - JA R2: 「%s」%s" % (q["ja_r2"], "" if ok[0] else "(評価者引用が原文と完全一致しないため前後文を再抽出: " + find(ja, ["元に戻", "ロールバック", "取りやめ", "取り下げ", "止め"], 0) + ")"))
    w("  - EN Checker前: 「%s」%s" % (q["en_pre_checker"], "" if ok[1] else "(引用不一致)"))
    w("  - EN最終: 「%s」%s" % (q["en_final"], "" if ok[2] else "(引用不一致)") + ("(Checker前と同一)" if q["en_pre_checker"] == q["en_final"] else ""))
    w("- 評価インスタンスの判定(確認前): JA R2=%s / EN前=%s / EN最終=%s。rollback_X(別インスタンス)= %s / %s / %s(不一致なし)。" % (lab[r["ja_r2"]], lab[r["en_pre_checker"]], lab[r["en_final"]], lab[r["ja_r2_X"]], lab[r["en_pre_checker_X"]], lab[r["en_final_X"]]))
    ns = [x for x in a["notes"].replace("人間確認前。", "").split("。") if x.strip() and not x.startswith("単独評価")]
    w("- 評価者メモ(抜粋): %s" % ("。".join(ns[:2]) + "。"))
    w("- 記事全文URL: JA R2 %s / EN最終 %s" % (url(p["ja"]), url(p["en"])))
    w("- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**")
    w("- ユーザー回答欄: JA R2 (  )  EN最終 (  )")
    w("")
# ---------------- (b)
w("## (b) 重大候補(評価者が『重大寄りの境界』『境界』と書いた件)5件 [H1相当、重大確定は0件]")
specs = [
    ("b-01", "ai_control", "jb9k", ["EVID-008", "CONTROL-003"], ["流れ出"], ["got out of the test"],
     "評価C: item3『重大寄りだが軽微に倒す』。台帳は『モデルは自己持ち出しなし・意図的な脱出の試みなし』。記事は直前に外部到達・PyPI公開・外部サイト到達を述べており、この否定文が矛盾して読めるか。"),
    ("b-02", "ai_control", "s9dk", ["EVID-009"], ["流出"], ["login information"],
     "評価B: 『認証情報の流出は実際のセキュリティスキャナーから』という限定が落ち、15システムの実行と流出の対応が曖昧(境界、軽微に計上)。"),
    ("b-03", "ai_control", "jb9k", ["EVID-009"], ["ログインに使う情報"], ["information used for logging in"],
     "評価C pending(軽微か問題なしか確信なし): 台帳の『実在のセキュリティスキャナーからの認証情報流出』という限定が落ちている。"),
    ("b-04", "hormuz", "cv85", ["HF-003", "HF-007"], ["集められ"], ["collected"],
     "評価B pending(『NGにしない(軽微寄りの境界)』): 『まだ実際に集められていません』は台帳に直接の記載はないが提案段階からの帰結。"),
    ("b-05", "meta", "249j", ["MUSE-HC-006"], ["一行"], ["In one line"],
     "評価B pending(『軽微寄りだが本文で限定済みのため非計上』): 1行要約で『一部の電話』の限定が落ち、『entire calls』と読める余地。"),
]
for bid, slug, code, fids, jak, enk, why in specs:
    p = paths(slug, code)
    ja, pre, en = rd(p["ja"]), rd(p["pre"]), rd(p["en"])
    js = find(ja, jak) if bid != "b-05" else para(ja, "一言")
    if bid == "b-05":
        js = "(JA R2には1行要約行なし。本文の該当) " + find(ja, ["一部の電話"], 0)
    es = find(en, enk, 1) if bid != "b-05" else para(en, "In one line")
    pes = find(pre, enk, 1) if bid != "b-05" else para(pre, "In one line")
    w("### #%s %s %s (種別: major候補[境界])" % (bid, slug, code))
    w("- 台帳該当fact(原文):")
    for fid in fids:
        w("```")
        w(ledger(slug, code, fid))
        w("```")
    w("- 記事該当文(原文): JA R2「%s」 / EN Checker前「%s」 / EN最終「%s」%s" % (js, pes, es, "(Checker前と同一)" if pes == es else ""))
    w("- 評価インスタンスの判定(確認前): 軽微/保留(重大とはしていない)。%s" % why)
    w("- 記事全文URL: JA %s / EN最終 %s" % (url(p["ja"]), url(p["en"])))
    w("- **質問**: その文は読者に誤った理解を与えますか? 重大(意味が変わる) / 軽微(曖昧・過剰断定) / 問題なし")
    w("- ユーザー回答欄: (  )")
    w("")
# ---------------- (c)
w("## (c) Checker Rewrite由来の変更 [H4相当。重大の新規NGは0件、軽微の新規NGは1件(c-04)]")
rws = [("c-01", "meta", "gj99", "評価B: Checker変更前NGか=境界(unclear)。『without users being told』を台帳外の具体化(開示先をユーザーに限定)として『without proper disclosure』へ。新規NGなし。"),
       ("c-02", "space_weapons", "4mjq", "評価B: 『four different faces』文を削除。文章の飾りで事実NGなし(before_was_ng=false)、新規NGなし。"),
       ("c-03", "space_weapons", "kfuf", "評価A: 台帳に沿った限定文(名前・攻撃能力・標的は未公表)を削除。新規NGは生じないが情報の欠落+二重スペース(before_was_ng=false)。"),
       ("c-04", "meta", "qvqc", "評価C: タイトル変更。before_was_ng=false、after_new_ng=minor(主体の曖昧化、item3として軽微計上)。")]
for cid, slug, code, why in rws:
    a = art(slug, code)
    p = paths(slug, code)
    pre, en = rd(p["pre"]), rd(p["en"])
    if cid == "c-04":
        rec = a["checker_rewrites"][0]
        bf, af = pre.splitlines()[0], en.splitlines()[0]
    elif cid == "c-01":
        rec = a["checker_rewrites"][0]
        bf, af = para(pre, "In one line"), para(en, "In one line")
    elif cid == "c-02":
        rec = a["checker_rewrites"][0]
        bf = para(pre, "four different faces")
        af = para(en, "When we hear that")
    else:
        rec = a["checker_rewrites"][0]
        bf = para(pre, "But the details are still hidden")
        af = para(en, "But the details are still hidden")
    lbl = {"true": "変更前もNG", "false": "変更前はNGでない", "unclear": "変更前NGか境界"}[str(rec["before_was_ng"]).lower()]
    w("### #%s %s %s (種別: rewrite、変更前判定=%s、新規NG=%s)" % (cid, slug, code, lbl, rec["after_new_ng"]))
    w("- 評価インスタンスの判定(確認前): %s" % why)
    if cid == "c-02":
        w("- 補足: この run(4mjq)は Checker final_state=STAGE4_ESCALATION(cycle3で blocking を位置特定できず上限到達)。下記は評価対象のEN最終。")
    w("- Checker変更前→変更後(原文):")
    w("  - 評価者記録: 「%s」 → 「%s」" % (rec["before"], rec["after"]))
    w("  - 変更前の段落(EN Checker前): %s" % bf)
    w("  - 変更後の段落(EN最終): %s" % af)
    w("- 記事全文URL: EN Checker前 %s / EN最終 %s" % (url(p["pre"]), url(p["en"])))
    w("- **質問**: 変更後は変更前より読者にとって 改善 / 中立 / 悪化 のどれですか?")
    w("- ユーザー回答欄: (  )")
    w("")
w("### 参考(質問は任意。評価者記録のうち上記以外の4件)")
ref = [("meta", "qvqc", 1), ("meta", "qvqc", 2), ("meta", "jdmu", 0), ("ai_control", "jb9k", 0)]
for slug, code, idx in ref:
    a = art(slug, code)
    r = a["checker_rewrites"][idx]
    w("- %s/%s: 「%s」 → 「%s」(変更前判定=%s、新規NG=%s)。回答欄 (  ) 改善/中立/悪化" % (slug, code, r["before"], r["after"], r["before_was_ng"], r["after_new_ng"]))
w("")
w("(注: Checker側のRewrite記録は10件。評価者記録は8件で、space_weapons 4mjq・kfufの各2記録のうち1記録ずつは評価者の記録対象外。詳細は SUMMARY_CCP.md ④。)")
w("")
# ---------------- (d)
code = "249j"
r = rb[code]
p = paths("meta", code)
w("## (d) rep10(249j)のNote位置不良がRollback判定に影響したか [1件、記入は任意]")
w("### #d-01 meta 249j (rep10) (種別: note_position)")
w("- 事実: Note(『注意(多義)…』)は brief 8行目(冒頭『Storyline』行の直前)にあり、HC-012 factの直後(11行目)ではない(他9本はHC-012 factの直後)。Note自体のbrief到達は10/10。")
w("- 記事該当文: JA R2「Metaはこの機能を、当面はいったん元の状態に戻します。」 / EN前=EN最終「For now, Meta will put this feature back the way it was.」(評価者・rollback_Xとも JA/EN前/EN最終=曖昧、一致)。時制が未来形になっている点も評価者が同一項目に統合。")
w("- 評価インスタンスの判定(確認前): 曖昧(誤読の文脈なし)。位置不良が結果を悪化させた形跡は見えない(同条件の他9本でもJA R2は曖昧8・正1)。")
w("- 記事全文URL: JA R2 %s / EN最終 %s" % (url(p["ja"]), url(p["en"])))
w("- **質問**: この記事の判定は、Noteが隣接していた他9本と同じ(曖昧)と見てよいですか? はい / いいえ(理由)")
w("- ユーザー回答欄: (  )")
w("")
w("## 末尾(PM記入)")
w("- 総件数: (a)H2=10、(b)H1相当=5(重大確定0)、(c)H4相当=詳細4+参考4、(d)1。H3(評価者間不一致)=0件。")
w("- ユーザー回答後に preregistration の指標①(Rollback)・②(重大)・⑤(Rewrite由来の新規NG)を確定値に更新する。④不要Rewrite率の裁定(事前登録文言50.0% / 委任文定義75.0%)はFable。")
w("- Production変更: なし / API費用: ¥0(評価のみ)。")
open(EV + "/HUMAN_REVIEW_PACK.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ok", len(L))
