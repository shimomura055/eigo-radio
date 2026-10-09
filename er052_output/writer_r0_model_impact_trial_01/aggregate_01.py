# -*- coding: utf-8 -*-
"""WRITER-R0-MODEL-IMPACT-TRIAL-01 Phase 3 集計(API非呼び出し、費用0円)。RESULT_01.md/FLAG_LIST_01.md/RUN_LOG_01.md/cost_ledger_01.jsonl を生成。
Flagの有用/誤検知は確定しない。『Sonnet暫定分類(未確定)』は理由欄からの後付け。"""
import glob, hashlib, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "detectors"))
sys.dont_write_bytecode = True
import flagger_lib as L  # noqa: E402

THEMES = [("streaming_price", "Disney+"), ("space_weapons", "宇宙兵器"), ("byd_recall", "BYD")]
MODELS = ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"]
SHORT = {"gpt-6-luna": "Luna", "gpt-6.1-sol": "Sol", "gpt-6-astra": "Astra"}
LEDGER = lambda t: os.path.join(REPO, "er052_output", "factlock_astra_e2e_trial_01", "runs", t, "new", "research_ledger", "verified_fact_ledger.txt")
J = lambda p: json.load(open(p, encoding="utf-8"))
sha = lambda b: hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()

CLASSES = ["Factに根拠がない新事実", "不在断定", "数字そのものの誤り", "数字の対象・範囲・単数複数の誤り", "主体・対象の入替", "因果・方向の捏造", "その他Fact逸脱"]


def prov_class(fl, src):
    """Sonnet暫定分類(未確定): 理由欄/typeからの後付け。Flaggerは変更していない。"""
    q = fl.get("question", "")
    if src == "d0":
        return "因果・方向の捏造(D0方向語ルール由来)"
    if fl["type"] == "不在断定":
        return "不在断定"
    if "台帳には記載されておらず" in q or "台帳にない" in q:
        return "Factに根拠がない新事実"
    return "その他Fact逸脱"


def ledger_facts(t):
    import ledger_restore_01 as LR
    all_lines = {}
    cur = None
    for ln in open(LEDGER(t), encoding="utf-8").read().splitlines():
        import re
        m = re.match(r"^\[(?P<st>[^\]]+)\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$", ln)
        if m:
            all_lines[m.group("id")] = m.group("text")
    return all_lines


def main():
    r0, fg, rows = {}, {}, []
    for t, _ in THEMES:
        for m in MODELS:
            r0[(t, m)] = J(os.path.join(HERE, "r0", t, m + ".json"))
            fg[(t, m)] = J(os.path.join(HERE, "flags", t, m + ".json"))
    # ---- 費用台帳
    P = {m: L.load_prices(m) for m in MODELS}
    out = open(os.path.join(HERE, "cost_ledger_01.jsonl"), "w", encoding="utf-8")
    r0cost, flcost = {}, {}
    for (t, m), r in r0.items():
        a = r["attempts"][-1]
        c = L.cost_yen(P[m], a["input_tokens"], a["output_tokens"], a.get("cached_tokens") or 0)
        r0cost[(t, m)] = c
        out.write(json.dumps(dict(purpose="r0", theme=t, model=m, model_id=a["model_id"], cost_jpy=round(c, 4), input_tokens=a["input_tokens"], output_tokens=a["output_tokens"],
                                  reasoning_tokens=a["reasoning_tokens"], cached_tokens=a.get("cached_tokens"), elapsed_s=a["elapsed_s"], attempts=len(r["attempts"]), response_id=a["response_id"]), ensure_ascii=False) + "\n")
    for (t, m), f in fg.items():
        flcost[(t, m)] = f["d2_cost_jpy"]
        for ln in open(os.path.join(HERE, "logs", "flagger_ledger_%s__%s.jsonl" % (t, m)), encoding="utf-8"):
            e = json.loads(ln)
            out.write(json.dumps(dict(purpose="flagger_d2", theme=t, r0_model=m, model=e["model"], cost_jpy=round(e["cost_jpy"], 4), usage=e["usage"], response_id=e["response_id"]), ensure_ascii=False) + "\n")
    out.close()
    tot_r0, tot_fl = sum(r0cost.values()), sum(flcost.values())

    # ---- 集計
    def cell_counts(t, m):
        f = fg[(t, m)]
        d0n = [x for x in f["d0_flags"] if not x.get("gate_only")]
        d0g = [x for x in f["d0_flags"] if x.get("gate_only")]
        return dict(d2=len(f["d2_flags"]), d0=len(d0n), d0g=len(d0g), union=len(f["union_flags"]))
    cc = {(t, m): cell_counts(t, m) for t, _ in THEMES for m in MODELS}

    def model_stats(m):
        d2c = [x["confidence"] for t, _ in THEMES for x in fg[(t, m)]["d2_flags"]]
        d0c = [x["confidence"] for t, _ in THEMES for x in fg[(t, m)]["d0_flags"]]
        tp = {}
        for t, _ in THEMES:
            for x in fg[(t, m)]["d2_flags"]:
                tp["D2:" + x["type"]] = tp.get("D2:" + x["type"], 0) + 1
            for x in fg[(t, m)]["d0_flags"]:
                k = "D0%s:%s" % ("(gate_only)" if x.get("gate_only") else "", x["type"] + "/" + x["basis"].split()[0].replace("dir:", ""))
                tp[k] = tp.get(k, 0) + 1
        return d2c, d0c, tp
    S = ["# RESULT_01: WRITER-R0-MODEL-IMPACT-TRIAL-01 結果(R0 3テーマ x 3モデル + 既存Risk Flagger、2026-10-10)\n"]
    S.append("性質: Trial/DEV。Production変更なし、採用判断なし、モデル優劣は確定しない。有用/誤検知の最終確定はユーザー(人間確認)。『Sonnet暫定分類』は理由欄・本文からの後付けで未確定。数値は特記なき限り実測(usage x 登録単価、USD/JPY=160)。\n")
    S.append("**重要所見(要Fable判断、STOP候補)**: streaming_price の台帳(`verified_fact_ledger.txt`)の F01・F07 は見出しが `[AMBIGUOUS - 断定禁止、曖昧さを保持すること]` 形式のため、既存Flaggerの台帳パーサ(`ledger_restore_01.py` の正規表現 `^\\[[A-Z_]+\\]\\s+...`)が**読み飛ばし、Flaggerは5件(F02〜F06)しか受け取っていない**(機械確認、flags/streaming_price/*.json の `n_facts`=5、台帳の見出し行は7件)。F07は『Disneyが理由を明示した記述は確認できない/Reutersのコメント要請に直ちには回答せず』を台帳として明記している。つまり Disney+ の4Flag(Luna)+1Flag(Sol)は、いずれも**F07が入力から欠落したことによる台帳外判定**である可能性が高い(Sonnet暫定・未確定)。space_weapons(22件、AMBIGUOUS見出し0)・byd_recall(11件、同0)は全件入力済み。パーサ修正はRisk Flagger側の変更に当たるため、本Trialでは実施していない(STOP条件『Risk Flagger仕様変更が必要』に該当しうる)。補足再実行案は末尾。\n")
    S.append("## 1. 比較表(ユーザー指定形式: Flag総数 = D0rb(方向語rollback) ∪ D2 の文単位ユニーク件数、事前登録定義)\n")
    S.append("| テーマ | Luna Flag総数 | Sol Flag総数 | Astra Flag総数 |\n|---|---|---|---|")
    for t, jn in THEMES:
        S.append("| %s | %d | %d | %d |" % (jn, *[cc[(t, m)]["union"] for m in MODELS]))
    S.append("| **合計** | **%d** | **%d** | **%d** |\n" % tuple(sum(cc[(t, m)]["union"] for t, _ in THEMES) for m in MODELS))
    S.append("### 1b. 内訳(D2 / D0rb / D0 gate_only[既存規約で総数に含めない参考]; 全件は FLAG_LIST_01.md)\n")
    S.append("| テーマ | モデル | D2 | D0rb | D0 gate_only(許可禁止反転) | 総数(D0rb∪D2) | 入力Fact数(Flagger受領/台帳見出し) |\n|---|---|---|---|---|---|---|")
    heads = {"streaming_price": 7, "space_weapons": 22, "byd_recall": 11}
    for t, jn in THEMES:
        for m in MODELS:
            c = cc[(t, m)]
            S.append("| %s | %s | %d | %d | %d | %d | %d/%d |" % (jn, SHORT[m], c["d2"], c["d0"], c["d0g"], c["union"], fg[(t, m)]["n_facts"], heads[t]))
    S.append("\n参考: D0 gate_only を含む全Flag件数(= D0全件 ∪ D2 の素の合計) = " + " / ".join("%s %d" % (SHORT[m], sum(cc[(t, m)]["d2"] + cc[(t, m)]["d0"] + cc[(t, m)]["d0g"] for t, _ in THEMES)) for m in MODELS) + "\n")
    S.append("## 2. モデル別統計(R0モデル別。confidence統計はD2のみ[D0は決定論ルールの固定値]。『confidenceは絶対評価に使わない』)\n")
    S.append("| 項目 | Luna | Sol | Astra |\n|---|---|---|---|")
    st = {m: model_stats(m) for m in MODELS}

    def fmt(v):
        return "-" if v is None else ("%.2f" % v)
    def stat(m, fn):
        d2c = st[m][0]
        return fn(d2c) if d2c else None
    S.append("| Flag総数(D0rb∪D2) | " + " | ".join(str(sum(cc[(t, m)]["union"] for t, _ in THEMES)) for m in MODELS) + " |")
    S.append("| D2 Flag数 / D0rb / D0 gate_only | " + " | ".join("%d / %d / %d" % (sum(cc[(t, m)]["d2"] for t, _ in THEMES), sum(cc[(t, m)]["d0"] for t, _ in THEMES), sum(cc[(t, m)]["d0g"] for t, _ in THEMES)) for m in MODELS) + " |")
    for lab, fn in (("D2 confidence 最小", min), ("D2 confidence 最大", max), ("D2 confidence 平均", statistics.mean), ("D2 confidence 中央値", statistics.median)):
        S.append("| %s | " % lab + " | ".join(fmt(stat(m, fn)) for m in MODELS) + " |")
    S.append("| D2 confidence 全値 | " + " | ".join(", ".join("%.2f" % c for c in sorted(st[m][0], reverse=True)) or "(Flagなし)" for m in MODELS) + " |")
    S.append("| D0 Flag confidence(固定値) | " + " | ".join(", ".join(sorted({"%.2f" % c for c in st[m][1]})) or "-" for m in MODELS) + " |")
    S.append("| Flag種類別件数(Flaggerの既存type) | " + " | ".join("; ".join("%s=%d" % kv for kv in sorted(st[m][2].items())) or "なし" for m in MODELS) + " |")
    S.append("| R0生成費用 合計(円、実測usage x 登録単価) | " + " | ".join("%.2f" % sum(r0cost[(t, m)] for t, _ in THEMES) for m in MODELS) + " |")
    S.append("| R0処理時間 合計/最小〜最大(秒、wall、9本同時並列実行下の実測) | " + " | ".join("%.1f / %.1f〜%.1f" % (sum(r0[(t, m)]["attempts"][-1]["elapsed_s"] for t, _ in THEMES), min(r0[(t, m)]["attempts"][-1]["elapsed_s"] for t, _ in THEMES), max(r0[(t, m)]["attempts"][-1]["elapsed_s"] for t, _ in THEMES)) for m in MODELS) + " |")
    S.append("| R0 出力tokens(reasoning含む) 合計 | " + " | ".join(str(sum(r0[(t, m)]["attempts"][-1]["output_tokens"] for t, _ in THEMES)) for m in MODELS) + " |")
    S.append("| R0 本文文字数(合計) | " + " | ".join(str(sum(r0[(t, m)]["chars"] for t, _ in THEMES)) for m in MODELS) + " |")
    S.append("| 実測model_id(API応答`model`) | " + " | ".join(", ".join(sorted({r0[(t, m)]["attempts"][-1]["model_id"] for t, _ in THEMES})) for m in MODELS) + " |")
    S.append("\n### 2b. セル別R0実測(テーマ x モデル)\n")
    S.append("| テーマ | モデル | model_id | in tok | out tok(reasoning) | 秒 | 費用円 | 文字数 | 試行数 | tag残存 |\n|---|---|---|---|---|---|---|---|---|---|")
    for t, jn in THEMES:
        for m in MODELS:
            a = r0[(t, m)]["attempts"][-1]
            S.append("| %s | %s | %s | %d | %d(%s) | %.1f | %.2f | %d | %d | %s |" % (jn, SHORT[m], a["model_id"], a["input_tokens"], a["output_tokens"], a["reasoning_tokens"], a["elapsed_s"], r0cost[(t, m)], r0[(t, m)]["chars"], len(r0[(t, m)]["attempts"]), r0[(t, m)]["tag_leak_error"] or "なし"))
    S.append("\nFlagger(D2, gpt-6.1-sol, effort=medium)の実費: 合計 ¥%.2f(9本)。**累計 ¥%.2f(R0 ¥%.2f + Flagger ¥%.2f)**、事前見積 約¥295・上限¥500・停止ライン¥354 のいずれも未到達。\n" % (tot_fl, tot_r0 + tot_fl, tot_r0, tot_fl))
    # ---- 既知例
    S.append("## 3. 既知例チェック(ユーザー列挙: Sonnetが本文を読んだ暫定判定・未確定。Flagger検出は機械的事実)\n")
    S.append("| # | 既知例 | Luna | Sol | Astra |\n|---|---|---|---|---|")
    S.append("| 1 | Disney+ 改定理由が明示されていないという台帳外断定 | 本文に出現(s16・s17・s18「理由は確認できない」)。**ただし台帳F07に同趣旨の記載あり**(Flaggerへの入力ではF07欠落)。Flagger: D2が3Flag(0.86/0.90/0.86) | 本文に出現(s7)。台帳F07に根拠あり。Flagger: D2 1Flag(0.96) | 本文に出現せず(理由への言及なし)。Flagなし |")
    S.append("| 2 | Disney+ Reutersコメント要請・回答状況という台帳外情報 | 本文に出現(s17)。台帳F07に根拠あり(Flagger入力からは欠落)。Flagger: D2 1Flag(0.78、その他) | 本文に出現せず | 本文に出現せず |")
    S.append("| 3 | 宇宙兵器 能力が秘密/非公表という台帳外断定 | 「秘密・非公表」の語は本文に出現せず(Sonnet暫定: 再発なし) | 「具体的な兵器の名前や攻撃能力は、この情報には出てきません」(s3)。『秘密』『非公表』ではないが、情報に出ていないという不在の述べ方(人間確認候補)。Flagなし | 「兵器の名前や具体的な攻撃能力は、今回の情報だけでは分かりません」(終盤)。同上(人間確認候補)。Flagなし |")
    S.append("| 4 | 宇宙兵器 1衛星→satellites複数化 | 「地上から発射した対衛星ミサイルで衛星を破壊したことがある」。日本語は単複が明示されず、複数化の明確な記述なし(Sonnet暫定: 再発なし、判断困難) | 「衛星攻撃ミサイルの試験で、衛星を破壊しています」同上 | 「ミサイルを発射して衛星を壊す試験」同上 |")
    S.append("| 5 | BYD 2件公告合計183,211台→1件公告化 | 「公告の対象は、BYDの唐系と秦系です。唐系142,895台、秦系40,316台で、合わせて183,211台」。『公告』が単数的に読める(Sonnet暫定: 1件公告化の疑い、人間確認候補)。Flagなし | 183,211台・公告件数の記述なし。『規制当局の発表』。再発なし | 183,211台・公告件数の記述なし。再発なし |")
    S.append("| 6 | BYD 数字・対象範囲の取り違え | 数値は台帳と一致(142,895/40,316/183,211)。取り違えなし(暫定) | 142,895/40,316のみ記載、一致(暫定) | 同左 |")
    S.append("| 7 | 新規Fact逸脱 | 下記 4.・FLAG_LIST_01.md | 同左 | 同左 |")
    S.append("\n(Flagger検出の機械的事実: BYD 9セルはD2/D0とも0Flag。宇宙兵器3セルはD2が0Flagで、D0 gate_onlyのみ(ルール由来)。D2がFlagを出したのはDisney+のLuna・Solのみ。)\n")
    S.append("## 4. 新規に見えたFact逸脱候補(未確定。有用/誤検知の確定はしない。ユーザーのピックアップ待ち)\n")
    S.append("Flaggerが出したFlag(全件はFLAG_LIST_01.md):\n- Disney+ Luna 4件 / Sol 1件: いずれも『理由の不在』『Reutersの回答状況』を台帳外とする指摘。F07欠落が原因の可能性が高い(上記)。\n- 宇宙兵器 D0 gate_only 7件(Luna 2 / Sol 2 / Astra 3): 『認めた』『禁止』の方向語ルールに基づく『許可禁止反転』。文中の『禁止』は条約が『禁じる/禁止するものではない』と述べる文脈で、Sonnet暫定では語彙一致由来に見えるが未確定。\n\nSonnetが本文を読んで見つけた人間確認候補(Flaggerは未検出。未確定):\n- Luna BYD: 『制動灯は、運転する人がブレーキを踏んだことを後続車に伝える合図です』『「ブレーキを踏んだのかな」という合図に見えるはずです』は台帳(BYD-RECALL-06〜08)に無い一般説明(新事実の可能性、軽微の可能性あり)。\n- Sol 宇宙兵器 s3 / Astra 宇宙兵器終盤: 既知例3に近い不在系記述(上表)。\n- Luna BYD: 『公告の対象は』の単数的表現(既知例5)。\n")
    S.append("## 5. 使用モデル名 / 最新か / 最新でない場合の理由(最新モデル原則 PM_GOVERNANCE 25節)\n")
    S.append("| 用途 | モデル | 最新系か | 理由 |\n|---|---|---|---|\n| R0 Writer | gpt-6.1-sol | 最新世代の上位系(登録単価・FLAGGER MODELSに最新世代として登録) | ユーザー指定 |\n| R0 Writer | gpt-6-astra | 最新世代の最上位系 | ユーザー指定 |\n| R0 Writer | gpt-6-luna | 最新世代だが効率系(flagger_lib.pyコメントは『予算上の参考のみ』扱い) | **ユーザー指定による比較対象**(現Production R0 Writerのモデルで比較基準) |\n| Risk Flagger(D2) | gpt-6.1-sol, effort=medium | 最新世代の上位系 | 既存Risk Flagger構成のまま(P3/P4と同一、変更なし)。D0は決定論でモデルなし |\n")
    S.append("## 6. Closeout項目(ユーザー指定11点)\n")
    S.append("1. 3テーマ x 3モデル完走: **9/9 R0完走、9/9 Flagger完走**(欠損なし)。ただしFlagger入力に既存パーサ由来の欠落あり(streaming_priceのF01・F07、上記)。\n2. 実測model_id: R0=`gpt-6-luna`/`gpt-6.1-sol`/`gpt-6-astra`(各API応答`model`欄が要求名と一致)、Flagger=`gpt-6.1-sol`。\n3. Flag総数: 表1。\n4. confidence分布: 表2(D2のみ。D2が出したFlagは全て Luna×Disney+ と Sol×Disney+ の5件)。\n5. Flag種類別件数: 表2。\n6. 費用: R0 ¥%.2f、Flagger ¥%.2f、累計 ¥%.2f(実測usage x 登録単価、見積約¥295・上限¥500以内)。\n7. 処理時間: 表2/2b(9本同時並列)。\n8. 実行失敗・再試行: R0 9本とも1試行で成功(再試行0回)。Flagger 9本とも1試行(形式再呼び出し0回)。詳細はRUN_LOG_01.md。\n9. 比較条件の差異: モデル以外の差異なし(RUN_LOG_01.mdの機械照合)。ただし(a)E2E R0 stageのFact Check・must-fixを全セルで行わなかった(全セル共通、事前登録済み)、(b)Flaggerは全セル共通でF01・F07が入力に無い(既存パーサの仕様、全セル共通なのでモデル間比較条件は同一だが絶対的な意味は損なわれる)。\n10. 未解決: 末尾。\n11. USER_DECISION_REQUIRED: あり(下記提案分類)。\n" % (tot_r0, tot_fl, tot_r0 + tot_fl))
    S.append("## 7. Closeout分類提案(Sonnet提案、Fable確定): USER_DECISION_REQUIRED\n理由: 全セル実行済み・モデル以外の条件は同一で、人間確認用のFlag一覧を出す設計どおり、ユーザーのFlagピックアップ待ち。優劣は書かない。ただし Disney+ はFlagger入力欠落(F07)により比較の意味が限定される。\n")
    S.append("## 8. 未解決・Fable確認事項\n1. **Flagger台帳パーサの欠落(F01・F07)**: 既存`ledger_restore_01.py`が`[AMBIGUOUS - ...]`見出しを読まない。他の既存結果(P3/P4新腕のDisney+記事など)にも同じ欠落が及んでいる可能性がある(未確認)。本Trialでは修正せず。補足案: Disney+ 3セルだけをdriver側でAMBIGUOUS行を含む台帳入力で再実行(D2のみ、見積 約¥4〜5)し『補足(条件変更あり)』として別掲。実施にはFable/ユーザー承認が必要(『Risk Flagger仕様変更』に該当しうるため未実施)。\n2. D2記事モードは過去Trialでは主にD2rankが使われ、D2(全件)の記事モード実績は無かった(コード無変更で実行)。9セル中D2がFlagを出したのはDisney+の2セルのみで、多くのセルが0Flag(D2は重大のみ列挙する設計)。件数を比較材料とするには、D2rank(上位3強制)等の補助実行を別途するか否かの判断が必要(本Trialでは使わない指示のため未実施)。\n3. E2E R0 stageのFact Check/must-fix省略の解釈(PREREGISTRATION_01.md 2節)の承認確認。\n4. 9本並列実行のため処理時間はAPI側負荷・並列の影響を含む(各モデルの純粋な速度比較ではない)。\n")
    open(os.path.join(HERE, "RESULT_01.md"), "w", encoding="utf-8").write("\n".join(S))

    # ---- FLAG_LIST
    F = ["# FLAG_LIST_01: 人間確認用Flag一覧(テーマ → モデル → confidence降順。Claude側で有用/誤検知を確定しない)\n",
         "読み方: 『Flag種類』はFlagger既存のtype。『Sonnet暫定分類』はユーザー指定7分類への後付け(理由欄から、未確定)。D0はルール由来で固定confidence(0.65)。D0 gate_onlyは既存規約で総数に含めない参考Flag。streaming_priceはFlagger入力にF01・F07が無い点に注意(RESULT_01.md冒頭)。\n"]
    for t, jn in THEMES:
        facts = ledger_facts(t)
        F.append("\n## %s (%s)\n" % (jn, t))
        for m in MODELS:
            f = fg[(t, m)]
            flags = [(x, "d2") for x in f["d2_flags"]] + [(x, "d0") for x in f["d0_flags"]]
            flags.sort(key=lambda p: -p[0]["confidence"])
            F.append("\n### %s / %s (Flag: D2 %d, D0 %d[うちgate_only %d]; 総数 %d)\n" % (jn, SHORT[m], len(f["d2_flags"]), len(f["d0_flags"]), sum(1 for x in f["d0_flags"] if x.get("gate_only")), len(f["union_flags"])))
            if not flags:
                F.append("(Flagなし)\n")
            for i, (x, src) in enumerate(flags, 1):
                F.append("**[%s %s #%d]** confidence=%.2f / 検出器=%s%s / Flag種類=%s / Sonnet暫定分類(未確定)=%s\n- 該当文(%s): %s\n- 対応Fact: %s\n- Flag理由: %s\n" % (
                    SHORT[m], jn, i, x["confidence"], src.upper(), "(gate_only参考)" if x.get("gate_only") else "", x["type"], prov_class(x, src), x["sentence_id"], x["sentence"],
                    " / ".join("%s: %s" % (fid, facts.get(fid, "(台帳に無いID)")[:200]) for fid in x.get("fact_ids", [])) or "(なし)", x["question"]))
    open(os.path.join(HERE, "FLAG_LIST_01.md"), "w", encoding="utf-8").write("\n".join(F))
    print("done; r0 cost %.2f flagger %.2f total %.2f" % (tot_r0, tot_fl, tot_r0 + tot_fl))
    return r0, fg


if __name__ == "__main__":
    main()
