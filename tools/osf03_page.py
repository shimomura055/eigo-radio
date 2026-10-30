# ONE-STEP-FURTHER-CORNER-TRIAL-01 委任_03: 比較ページ(v3)生成。index.html=学習コンテンツ(原文§8形式)、dev_log.html=Gate/監査/費用(分離)。API呼出なし。
import sys, os, json, html, shutil, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf03_run as R
import osf03_lib as L
E = html.escape
DEST = os.path.join(L.ROOT, "user_test", "one_step_further_trial_01")
ARTICLE = {"y": "Family Y「夫が妻の姓を選ぶとき、それぞれの声」(姓記事)", "x": "Family X「AIの島」(The Island Resets! But AI Has “Strategy Notes”)", "z": "Family Z「告げ口心臓」(The Tell-Tale Heart)"}
LV = {"std": "Standard", "adv": "Advanced"}
PREV_TAG = {  # 前回(委任_02)の主候補 -> NG類型ラベル(ユーザー実例確認[原文§4]に対応するものは明記。他は今回の独立監査の検出内容)
    "P01": "NG: 意味・対象の変更(助言→自分の権限の否定。主語と肯否が変わる)[今回の監査=主語・肯否・意味の変更]",
    "P02": "NG②: 心理・状況の創作(元にない感情・意思を追加)[ユーザー指摘]",
    "P03": "NG①: 意味・対象の変更(人が助ける→メモが作業の材料)[ユーザー指摘]",
    "P04": "NG: 意味の変更・情報の追加(進展した→成果がある)[今回の監査]",
    "P05": "意味が完全には対応しない(「試す」→「成り行きを見る」。原文§3③の注意点)[今回の監査=意味の変化]",
    "P06": "NG③: 文章の追加だけ(元の表現を残して別の行動を足した)[ユーザー指摘]",
    "P07": "NG④: 意味の異なる別表現への飛躍(理由の推測→深読みの留保)[ユーザー指摘]",
}
CSS = """body{font-family:'Hiragino Sans','Yu Gothic',sans-serif;max-width:900px;margin:1em auto;padding:0 1em;line-height:1.7;color:#222}h1{font-size:1.35em}h2{border-bottom:3px solid #35a;padding-bottom:4px;margin-top:2em}h3{background:#eef;padding:6px 10px;border-radius:4px}
.note{background:#fff8e0;border:1px solid #cb8;padding:10px;margin:1em 0;font-size:.95em}.card{border:1px solid #ccd;border-radius:8px;padding:10px 14px;margin:12px 0;background:#fcfcff}
.lab{font-size:.78em;color:#555;font-weight:bold;margin-top:.6em;display:block}.q{background:#f1f1f1;padding:6px 10px;border-radius:4px}.q mark{background:#ffe27a}.base{background:#f2f2f2;padding:6px 10px;border-radius:4px}.further{background:#e6f4e6;border:2px solid #4a4;padding:6px 10px;border-radius:4px}
.en{font-size:1.12em;font-weight:bold}.ja{color:#444}.diff{color:#555;font-size:.88em;margin-top:.3em}.pt{margin-top:.5em}.sec{color:#666;font-size:.88em}details{margin:8px 0}summary{cursor:pointer;color:#036}
.prev{background:#fff0f0;border:1px solid #d99;border-radius:6px;padding:6px 10px;margin:6px 0;font-size:.92em}.tag{color:#a00;font-weight:bold;font-size:.85em}table{border-collapse:collapse;margin:6px 0}td,th{border:1px solid #bbb;padding:3px 7px;font-size:.85em;vertical-align:top}
.none{background:#eee;padding:8px;border-radius:4px;color:#555}"""
def hl(q, span):
    i = L.nt(q).find(L.nt(span))
    # 単純: 原文中でspanを大小文字無視で検索
    m = re.search(re.escape(span), q, re.I)
    if not m: return E(q)
    return E(q[:m.start()]) + "<mark>" + E(q[m.start():m.end()]) + "</mark>" + E(q[m.end():])
def load_all():
    sel = R.jload("select.json"); gens = {}
    for f in "yxz":
        for c in R.jload(f"gen__{f}.json")["candidates"]: gens[c["cid"]] = c
    for c in R.jload("gen_r3.json")["candidates"]: gens[c["cid"]] = c
    return sel, gens
def prev_by_cell():
    reg = R.jload("regress__result.json")["items"]; out = {}
    for r in reg:
        if r["id"].startswith("P"): out.setdefault(r["cell"], []).append(r)
    return out
def card(c):
    b = c["base"]; s = f"<div class=card><span class=lab>本文からの引用</span><div class=q>{hl(b['quote'], b['target_span'])}</div>"
    s += f"<span class=lab>基本表現(原型)</span><div class=base><div class=en>{E(b['prototype'])}</div><div class=ja>{E(b['meaning_ja'])}</div></div>"
    s += f"<span class=lab>One Step Further</span><div class=further><div class=en>{E(c['further_expression'])}</div><div class=ja>{E(c['further_meaning_ja'])}</div>"
    if c.get("diff_ja"): s += f"<div class=diff>基本との違い: {E(c['diff_ja'])}</div>"
    s += f"</div><span class=lab>学習ポイント</span><div class=pt>{E(c['point_ja'])}</div></div>"
    return s
def page_index():
    sel, gens = load_all(); prev = prev_by_cell()
    H = [f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>One Step Further 最終再設計Trial 比較ページ(v3)</title><style>{CSS}</style></head><body>",
         "<h1>One Step Further｜もう一歩進んだ英語表現 最終再設計Trial(v3)</h1>",
         "<div class=note><b>これはTrialの試作です。正式採用ではありません。</b>前回(v2)は意味の対応を満たさない例が多く、今回は工程を作り直しました(本文から基本表現を抽出→基本表現の意味だけを入力して発展表現を生成→意味の対応・学習価値を別会社のモデルで検査)。品質を満たす候補がないレベルは無理に埋めていません。採否はユーザーが判断します。検査の詳細は<a href='dev_log.html'>開発ログ</a>、前回版は<a href='index_v2_archive.html'>index_v2_archive.html</a>。</div>",
         "<ul>" + "".join(f"<li><a href='#{f}'>{E(ARTICLE[f])}</a></li>" for f in "yxz") + "</ul>"]
    for f in "yxz":
        H.append(f"<h2 id='{f}'>{E(ARTICLE[f])}</h2>")
        for lv in ("std", "adv"):
            cell = f"{f}_{lv}"; H.append(f"<h3>{LV[lv]}</h3>")
            ids = sel["selected"][cell]
            if not ids: H.append("<div class=none>品質を満たす候補がなかったため、このレベルは掲載しません。</div>")
            for i in ids: H.append(card(gens[i]))
            pv = prev.get(cell, [])
            if pv:
                H.append("<details><summary>前回Trial(v2)の対応候補を見る(NG類型ラベル付き)</summary>")
                for r in pv:
                    it = r["prev_item"]
                    H.append(f"<div class=prev><span class=tag>{E(PREV_TAG[r['id']])}</span><br>基本: {E(it['basic_en'])}({E(it['basic_ja'])})<br>前回の発展: <b>{E(it['further_en'])}</b>({E(it['further_ja'])})</div>")
                H.append("</details>")
    H.append("</body></html>")
    return "\n".join(H)
def tbl(head, rows):
    return "<table><tr>" + "".join(f"<th>{E(str(h))}</th>" for h in head) + "</tr>" + "".join("<tr>" + "".join(f"<td>{E(str(x))}</td>" for x in r) + "</tr>" for r in rows) + "</table>"
def page_dev():
    sel, gens = load_all(); fin = R.jload("final.json"); selj = R.jload("select.json"); reg = R.jload("regress__result.json")
    usage = [json.loads(l) for l in open(L.USAGE, encoding="utf-8") if l.strip()]
    total = sum(u["cost_jpy"] for u in usage)
    H = [f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>One Step Further 最終再設計Trial 開発ログ(v3)</title><style>{CSS}</style></head><body>",
         "<h1>開発ログ・内部評価(委任_03)</h1><p><a href='index.html'>学習コンテンツ(比較ページ)へ</a> / <a href='dev_log_v2_archive.html'>前回(v2)の開発ログ</a></p>",
         "<div class=note><b>注意</b>: 以下はAIによる監査です。前回はAI監査が高得点でも実例でNGでした。この監査が「正しくNGを検出できるか」は回帰セットで確認していますが、最終判断はFable・ユーザーの目視です。</div>"]
    H.append("<h2>A. 工程(原文§5のStep1〜5)</h2><ol><li>Step1 抽出(gpt-6-luna、第3ラウンドのみgpt-6.1-sol): 本文を文番号付きで入力し、引用文・ターゲット範囲・原型・意味・保持要素を出力。機械検査=引用の本文実在(KPの本文照合normalize_textを再利用)、範囲が引用内にあるか、原型の語がターゲットに由来するか、否定・法助動詞の保持、KP/文法との核重複。</li><li>Step2 生成(gpt-6.1-sol・推論low): 入力=原型・意味・保持要素・レベル・選定基準のみ(記事全文・人物心理は渡さない)。各基本表現に最大2候補+同一場面の置換文(frame)。機械検査=長文化のみ・元の文を残して延長・語順入替のみ・KP重複。</li><li>Step3 Gate A(gemini-4-argon、別ベンダー): 欠陥コード8種+置換可能性+差の記録。</li><li>Step4 Gate B(gemini-4-argon): 新しい発見・使いたい・場面の広さ・レベル・説明の分かりやすさ(1-5)+旗。閾値=発見/使いたい/レベル/説明≥4、広さ≥3、旗なし。</li><li>Step5 最終確認(gemini-4-argon、本文参照): 引用の実在・範囲・原型・意味・本文の文へ置換した文の自然さ/同義性。PASS+Gate B閾値を満たす候補を各レベル最大2件。満たさなければ0件。</li></ol>")
    H.append("<h2>B. 回帰セット(前回NG5類型+前回主候補7件+良例3件)の判定</h2><p class=sec>監査Promptの欠陥例は回帰セットと別の例(答えの漏洩防止)。argon=gemini-4-argon、3.1pro=gemini-3.1-pro-preview。</p>")
    rows = []
    for r in reg["items"]:
        a1 = reg["A"]["gemini-4-argon"].get(r["id"], {}); a2 = reg["A"]["gemini-3.1-pro-preview"].get(r["id"], {})
        rows.append([r["id"], r["src"], r["base_expression"][:48] + " → " + r["further_expression"][:60], r["expect"], f"{a1.get('v')} {a1.get('f')}", f"{a2.get('v')} {a2.get('f')}", (a1.get("diff") or "") + " " + (a1.get("why") or "")])
    H.append(tbl(["ID", "出典", "基本→発展", "期待", "argon", "3.1pro", "argonの根拠"], rows))
    H.append("<p>結果: argon=NG5類型5/5・前回主候補7/7をFAIL、良例①をPASS_WITH_DIFF、②をPASS_WITH_DIFF(差を記録)、③をFAIL(意味の変化を検出)。3.1proは前回主候補P03・P05をPASS_WITH_DIFFとして見逃したため、Gate Aの決定にはargonを使用(3.1proは参考)。初回プロンプト(v1)の3.1pro結果もraw保存(regress_v1__A__gemini-3.1-pro-preview.txt)。v1→v2でプロンプトを1回改良(コンパクト出力化+「何を言うかが変わる差はPASS_WITH_DIFFにしない」規則)。</p>")
    H.append("<h2>C. Step1 抽出結果(基本表現)</h2>")
    for cell in R.CELLS:
        for t, lab in (("", "R1(luna)"), ("_r2", "R2(luna)"), ("_r3", "R3(sol)")):
            try: d = R.jload(f"extract{t}__{cell}.json")
            except Exception: continue
            H.append(f"<h3>{cell} {lab}</h3>" + tbl(["状態", "原型", "ターゲット範囲", "意味", "機械検査"], [["採用", k["prototype"], k["target_span"], k["meaning_ja"], ""] for k in d["kept"]] + [["棄却", k["prototype"], k["target_span"], k["meaning_ja"], ",".join(k["mech"])] for k in d["dropped"]]))
    H.append("<h2>D. 候補と判定(全候補)</h2>")
    ga = {}; gb = {}
    for f in "yxz": ga.update(R.jload(f"gateA__{f}__A.json")["results"]); gb.update(R.jload(f"gateB__{f}__B.json")["results"])
    sel_ids = {i for v in selj["selected"].values() for i in v}; fr = fin["results"]
    rows = []
    for cid, c in gens.items():
        a = ga.get(cid, {}); b = gb.get(cid, {}); x = fr.get(cid, {})
        mech = [m for m in c["mech"]]
        rows.append([("★選定 " if cid in sel_ids else "") + cid, c["base"]["prototype"] + " → " + c["further_expression"], ",".join(mech), (a.get("v") or "-") + (" " + str(a.get("f")) if a.get("f") else "") + " " + (a.get("diff") or "") + (a.get("why") or ""),
                     "/".join(str(b.get(k)) for k in "dwblc") if b else "-", (",".join(b.get("bf") or []) + " " + (b.get("wk") or "")) if b else "", (x.get("v") or "-") + " " + (x.get("why") or "") + " " + (x.get("diff") or "")])
    H.append(tbl(["候補", "基本→発展", "機械", "Gate A(argon)", "B(d/w/b/l/c)", "B旗・弱点", "最終確認(本文参照)"], rows))
    H.append("<p class=sec>第3ラウンド候補(:r3_)は費用制約のため、枠組みGate A(frame比較)を省き、本文参照の最終確認(欠陥コード・同義性を含む)+Gate Bスコアを同一呼出で実施。B欄は最終確認呼出内のスコア。</p>")
    H.append("<h3>最終確認の本文置換文(選定候補)</h3><ul>" + "".join(f"<li>{E(i)}: {E(fr[i].get('sub',''))}</li>" for i in sel_ids) + "</ul>")
    H.append("<h2>E. 費用・時間</h2>")
    grp = {}
    for u in usage:
        k = u["tag"].split("__")[0].replace("_retry", ""); g = grp.setdefault(k, [0, 0, 0.0, u["model"]]); g[0] += u["cost_jpy"]; g[1] += 1; g[2] += u["elapsed_sec"]
    H.append(tbl(["段階", "モデル", "呼出", "円", "秒(合計)"], [[k, v[3], v[1], round(v[0], 2), round(v[2], 1)] for k, v in grp.items()]))
    H.append(f"<p>合計 ¥{total:.2f}(Gemini単価はrepo内に公開単価が無いため【推定】: argon $5/$25、3.1pro $2/$12 per 1M tokens。実請求は異なる可能性)。<b>上限超過の記録</b>: 委任文の上限¥50、理由記録で¥70まで。最終確認呼出(1回¥13.3)の実費を事前見積(約¥5〜6)より過小評価した結果、合計が¥70を超過した。以降の有料呼出は行っていない。</p>")
    H.append("</body></html>")
    return "\n".join(H)
if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    idx = os.path.join(DEST, "index.html"); dev = os.path.join(DEST, "dev_log.html")
    if not os.path.exists(os.path.join(DEST, "index_v2_archive.html")): shutil.copy(idx, os.path.join(DEST, "index_v2_archive.html"))
    if not os.path.exists(os.path.join(DEST, "dev_log_v2_archive.html")): shutil.copy(dev, os.path.join(DEST, "dev_log_v2_archive.html"))
    open(idx, "w", encoding="utf-8", newline="\n").write(page_index()); open(dev, "w", encoding="utf-8", newline="\n").write(page_dev())
    print("written", idx, dev)
