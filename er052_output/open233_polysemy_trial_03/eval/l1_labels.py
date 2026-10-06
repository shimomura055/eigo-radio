# -*- coding: utf-8 -*-
# 内容ラベル(評価のみ、Sonnet判断)。値: (既知誤読一致, 型, 台帳外混入, 曖昧語流用, 根拠1行)
# 一致: Y一致/P部分/N不一致/- 対象外。型: V=真の逆転型(妥当)/D=変質止まり/H=hedge・帰属・範囲限定=誤り/X=Rが不自然(こじつけ)=誤り
import json, re, sys
from pathlib import Path

TRIAL = Path(__file__).resolve().parents[1]
E = None  # 台帳外混入あり(軽微/重大は根拠欄)

L = {}
def add(pat, theme, fid, m, t, foreign, why):
    L[(pat, theme, fid)] = (m, t, foreign, why)

A, B, C = "A_onepass", "B_twostage", "C_promote"
# ---------------- A ----------------
add(A,"meta","MUSE-HC-001","-","V",0,"発表/展開予定を提供開始と誤読=段階反転")
add(A,"meta","MUSE-HC-012","P","V",0,"ロールバック対象の範囲(全体停止否定)は扱うが、既知の『何を元に戻したか』の方向は扱わない")
add(A,"meta","MUSE-HC-014","N","V",0,"条件付き公開↔公開済みの段階反転は妥当だが、既知誤読(改善の対象)とは別")
add(A,"hormuz","HF-002","-","V",0,"提案投稿↔徴収・導入済み=段階反転")
add(A,"hormuz","HF-003","-","V",0,"制度設計未提示の案↔導入済み=段階反転")
add(A,"hormuz","HF-004","-","H",0,"仮定試算↔確定額=hedge/確度の違い")
add(A,"hormuz","HF-005","-","D",0,"終値↔日中高値の取り違え=数値取違えで逆転ではない")
add(A,"hormuz","HF-006","-","V",0,"封鎖予定↔実施済み=段階反転")
add(A,"hormuz","HF-007","P","V",0,"置換投稿↔実施済みは扱うが、既知の途中/最終(HF-009側)とは異なる")
add(A,"hormuz","HF-010","-","D",0,"終値↔日中高値の数値取違え")
add(A,"hormuz","HF-012","-","H",0,"WTI↔Brentの範囲限定の違い")
add(A,"space_weapons","F-002","Y","V",0,"評価↔実際の攻撃を確認、を逆転として明示")
add(A,"space_weapons","F-003","-","X",0,"地上発射試験を軌道上配備と読むのは不自然なR")
add(A,"space_weapons","F-004","-","X",0,"同上(地上発射の破壊試験を軌道配備と読む読者は想定しにくい)")
add(A,"space_weapons","F-005","-","X",0,"同上")
add(A,"space_weapons","F-006","-","D",0,"サイバー妨害↔衛星物理破壊=手段の取違え、逆転ではない")
add(A,"space_weapons","F-007","Y","V",0,"開発報道↔試験・配備済みを明示")
add(A,"space_weapons","F-008","-","V",0,"接近↔攻撃実施=段階反転")
add(A,"space_weapons","F-009","Y","V",0,"開発中↔打上げ・配備・使用を明示")
add(A,"space_weapons","F-010","-","V",0,"開発・評価段階↔運用配備=段階反転")
add(A,"space_weapons","F-014","-","X",0,"センサー実証を攻撃兵器配備と読むのは不自然")
add(A,"space_weapons","F-015","-","X",0,"任務説明を兵器配備の説明と読むのは不自然")
add(A,"space_weapons","F-018","-","V",0,"不採択↔採択=極性反転")
add(A,"space_weapons","F-019","-","D",0,"決議↔新条約=種別の取違え")
add(A,"space_weapons","F-020","-","D",0,"同上")
add(A,"space_weapons","F-021","-","D",0,"政策コミット↔条約禁止=範囲/種別。台帳claim自体が明記")
add(A,"space_weapons","F-024","-","V",0,"開発進行中↔試験済み・配備可能=段階反転(F-007と同趣旨の重複)")
add(A,"sewer","F-004","-","H",0,"範囲限定(腐食リスク箇所↔全管路)の違い")
add(A,"sewer","F-008","-","V",0,"新設禁止↔既設撤去=対象反転")
add(A,"sewer","F-010","N","V",0,"方針策定↔切替完了(段階)で、既知の市街化/調整区域の取違えとは別")
add(A,"sewer","F-011","Y","V",0,"方針案・意見募集↔切替完了を明示")
add(A,"sewer","F-012","-","V",0,"『実施するとした』↔実施済み=予定/完了反転")
add(A,"ai_control","EVID-005","-","D",0,"指示なしの不正↔指示された不正=原因/主体の違い")
add(A,"ai_control","EVID-007","-","D",0,"同上(明示指示の有無)")
add(A,"ai_control","CONTROL-002","-","V",0,"仮説的枠組み↔現状の事実=段階(仮説/実在)反転")
add(A,"A02","POL-01","Y","V",0,"計画↔施行済みを明示")
add(A,"A02","POL-02","-","V",0,"変更可デフォルト↔強制=状態反転")
add(A,"A02","POL-06","Y","V",0,"自動オン・変更可↔強制を明示")
add(A,"A02","POL-07","-","V",0,"最終確定未了↔確定済み=途中/最終")
add(A,"A02","PILOT-01","-","D",0,"309の指す範囲の違い")
add(A,"A02","PILOT-02","-","D",0,"希望配分↔無作為割付=設計の取違え")
add(A,"A02","PILOT-03","-","D",0,"群人数/合計の取違え")
add(A,"A02","PILOT-04","-","X",0,"パイロット介入を政府制度施行と読むのは不自然")
add(A,"A02","OUT-04","-","D",0,"利用移動↔全体減少=結果の取違え")
for i,(f,t,w) in enumerate([("F001","H","編集ランウェイ報道↔消費者販売動向=範囲限定"),("F002","H","同上"),("F003","D","併存↔置換の取違え"),("F004","H","編集報道↔消費者購入=範囲限定"),("F005","H","同上"),("F006","H","編集特集↔市場普及=範囲限定"),("F009","H","同上"),("F010","H","編集・小売専門家見解↔売上増=範囲限定"),("F015","H","検索増↔購入増=指標の違い"),("F018","H","ランウェイ観察↔消費者購入=範囲限定")]):
    add(A,"small_bag",f,"-",t,0,w)
# ---------------- B ----------------
add(B,"meta","MUSE-HC-001","-","V",0,"A同趣旨(発表/展開↔提供開始)")
add(B,"meta","MUSE-HC-012","P","D",0,"当面ロールバック↔恒久停止。方向(何を戻したか)は未言及")
add(B,"meta","MUSE-HC-014","N","V",0,"公開展開の段階反転は妥当だが既知誤読とは別")
add(B,"hormuz","HF-001","-","V",0,"『維持すべき』という規範↔実際に維持している、の様相反転")
add(B,"hormuz","HF-002","-","V",0,"提案↔徴収済み")
add(B,"hormuz","HF-003","-","V",0,"案↔実施")
add(B,"hormuz","HF-004","-","H",0,"仮定試算↔確定")
add(B,"hormuz","HF-005","-","D",0,"終値/高値取違え")
add(B,"hormuz","HF-006","-","V",0,"封鎖予定↔開始済み(日付)")
add(B,"hormuz","HF-007","P","V",0,"置換投稿↔実際に置換。途中/最終の観点は薄い")
add(B,"hormuz","HF-008","-","V",0,"発言↔徴収禁止の実施=段階反転")
add(B,"hormuz","HF-009","Y","V",0,"一時縮小→発表前水準へ戻る(途中/最終)を直接扱う")
add(B,"hormuz","HF-010","-","D",0,"終値/高値取違え")
add(B,"hormuz","HF-012","-","H",0,"WTI↔Brentの範囲限定")
add(B,"sewer","F-008","-","V",0,"新設禁止↔既設全撤去")
add(B,"sewer","F-010","N","V",0,"方針策定↔完了で既知の区域取違えとは別")
add(B,"sewer","F-011","Y","V",0,"意見募集段階↔決定・実施")
add(B,"sewer","F-012","-","V",0,"補助実施予定↔実施済み")
add(B,"sewer","F-013","-","V",0,"縮小計画策定↔実際に縮小")
add(B,"A02","POL-01","Y","V",0,"計画↔施行済み")
add(B,"A02","POL-02","-","V",0,"変更可↔強制")
add(B,"A02","POL-04","-","V",0,"デフォルトオフ↔再オン不可=状態反転")
add(B,"A02","POL-06","Y","V",0,"自動オン・変更可↔強制")
add(B,"A02","POL-07","-","V",0,"未確定↔確定済み")
add(B,"A02","PILOT-01","-","D",0,"309の範囲")
add(B,"A02","PILOT-05","-","D",0,"対象アプリ範囲の取違え")
add(B,"A02","PILOT-06","-","H",0,"研究目的/因果の範囲限定・hedge")
add(B,"A02","OUT-02","-","H",0,"自己申告の改善↔因果=帰属/確度の違い")
add(B,"A02","OUT-04","-","D",0,"移動↔全体減少")
# ---------------- C ----------------
add(C,"meta","MUSE-HC-005","-","D",0,"報道上の8月開始↔公式発表日=時期の混同")
add(C,"meta","MUSE-HC-012","P","V",0,"当面ロールバック↔全体停止。方向は未言及")
add(C,"hormuz","HF-002","-","D",1,"noteは7/14と7/13の因果で、当該fact(投稿)と焦点がずれる。別fact向けの禁止文の転記疑い")
add(C,"hormuz","HF-003","-","V",0,"案↔導入(『通航料』と言い換え)")
add(C,"hormuz","HF-004","-","H",0,"試算↔確定")
add(C,"hormuz","HF-006","-","D",0,"因果の唯一化(20%料だけが原因)の否定")
add(C,"hormuz","HF-007","N","D",0,"7/14と7/13の前後関係。既知の途中/最終とは別")
add(C,"hormuz","HF-008","-","D",0,"同日発言の取違え(時系列)")
add(C,"hormuz","HF-009","Y","V",0,"一時縮小→高水準へ戻る(全面下落ではない)")
add(C,"hormuz","HF-012","-","H",0,"WTI↔Brentの範囲限定")
add(C,"space_weapons","F-002","Y","V",0,"評価↔実際の攻撃")
add(C,"space_weapons","F-003","-","X",1,"『恒久』配備は台帳外の語。Rが不自然")
add(C,"space_weapons","F-004","-","X",1,"『試験』は台帳外の表現(軽微)。Rが不自然")
add(C,"space_weapons","F-005","-","X",1,"『試験』は台帳外の表現(軽微)。Rが不自然")
add(C,"space_weapons","F-006","-","D",0,"サイバー妨害↔物理破壊")
add(C,"space_weapons","F-009","Y","V",0,"開発中評価↔配備")
add(C,"space_weapons","F-013","-","X",1,"noteに『ミサイル警戒・追跡』とあるが当該factは防御分類の記述で別factの混入疑い")
add(C,"space_weapons","F-014","-","X",0,"センサー実証を攻撃兵器と読むのは不自然")
add(C,"space_weapons","F-015","-","X",0,"同上")
add(C,"space_weapons","F-018","-","V",0,"不採択↔採択(新規則)")
add(C,"space_weapons","F-019","-","D",0,"決議↔包括的新条約。『通常兵器を含む』は台帳外の付加(軽微)")
add(C,"space_weapons","F-020","-","D",0,"決議↔新条約")
add(C,"space_weapons","F-021","-","D",0,"政策↔国際全面禁止")
add(C,"sewer","F-001","-","X",0,"耐用年数超過↔全管路使用不能は不自然")
add(C,"sewer","F-010","N","X",0,"Rが『既設老朽管撤去・切替事例』で当該claimの誤読とは言いにくい。既知の区域取違えと別")
add(C,"sewer","F-011","Y","V",0,"意見募集段階↔決定(整備済み区域の言及はなし)")
add(C,"sewer","F-016","Y","V",0,"集落排水廃止↔公共下水管からの切替を明示")
add(C,"sewer","F-020","-","H",0,"実施率の残存↔自動的に適正処理=解釈的")
add(C,"ai_control","EVID-001","-","H",0,"能力向上測定↔自律性達成=過剰一般化")
add(C,"ai_control","EVID-002","-","V",0,"模擬環境↔現実世界(模擬/実)")
add(C,"ai_control","EVID-005","-","H",0,"隠れた目的の否定=解釈/hedge")
add(C,"ai_control","EVID-006","Y","V",0,"架空シナリオ↔実在の技術者を脅迫を明示")
add(C,"ai_control","EVID-007","-","H",0,"公開運用モデルの人間制御超過の否定=過剰一般化")
add(C,"ai_control","EVID-008","-","H",0,"自律的乗っ取りの否定=過剰一般化")
add(C,"ai_control","EVID-009","-","H",0,"目標形成の否定=解釈(『独自に形成した目標』は台帳要確認)")
add(C,"ai_control","EVID-010","-","H",0,"AI乗っ取りの否定=過剰一般化")
add(C,"ai_control","CONTROL-003","-","H",0,"停止抵抗の解決済み/不可避の否定=解釈")
add(C,"A02","POL-01","Y","V",0,"計画↔施行済み")
add(C,"A02","POL-02","-","X",0,"『完全に利用不能』は不自然なR")
add(C,"A02","POL-03","-","D",0,"通知ミュート↔完全遮断")
add(C,"A02","POL-04","-","D",0,"autoplay設定↔夜間通知の取違え")
add(C,"A02","POL-05","-","D",0,"常時↔夜間のみ")
add(C,"A02","POL-06","Y","V",0,"自動オン変更可↔強制・解除不能")
add(C,"A02","PILOT-01","-","D",0,"309の指す範囲")
add(C,"A02","PILOT-02","-","D",0,"希望配分↔RCT")
add(C,"A02","PILOT-03","-","D",0,"群人数/合計")
add(C,"A02","PILOT-04","-","H",0,"パイロット↔政策案の範囲(同一制度でない)")
add(C,"A02","PILOT-06","-","H",0,"探索的自己申告↔効果実証=hedge")
add(C,"A02","OUT-04","-","D",0,"移動↔全体減少")
add(C,"A02","OUT-05","-","D",0,"適応行動↔総スクリーン時間削減")
add(C,"small_bag","F001","-","D",0,"micro bags不在の否定(過大解釈)")

TYPE = {"V": "真の逆転型(妥当)", "D": "変質止まり", "H": "hedge・帰属・範囲=誤り", "X": "Rが不自然=誤り"}
MATCH = {"Y": "一致", "P": "部分", "N": "不一致", "-": "-(対象外)"}
AMB = re.compile(r"改める|改め|見直|改善|修正")

def main():
    import gen_notes_p03  # noqa
    ev = TRIAL / "eval"
    tg = json.loads((ev / "targets.json").read_text(encoding="utf-8"))["themes"]
    ho = json.loads((ev / "holdout.json").read_text(encoding="utf-8"))["themes"]
    th = {**tg, **ho}
    summary = {}
    for pat in (A, B, C):
        lines = ["# content label sheet(L1r評価のみ・Sonnet判断): %s" % pat,
                 "凡例: 既知誤読との一致=一致/部分/不一致/-(対象外) | 型=真の逆転型(妥当)/変質止まり/hedge・帰属・範囲=誤り/Rが不自然=誤り | 台帳外混入=有/無 | 曖昧語流用=自動走査(改める/見直/改善/修正)", "",
                 "| theme | fact_id | note(逐語) | 既知誤読との一致 | 型 | 台帳外混入 | 曖昧語流用 | 根拠 |", "|---|---|---|---|---|---|---|---|"]
        cnt = {"V": 0, "D": 0, "H": 0, "X": 0, "n": 0, "foreign": 0, "amb": 0, "extra_n": 0, "extra_V": 0, "extra_D": 0, "extra_bad": 0, "T_Y": 0, "T_P": 0, "T_N": 0}
        for s, t in th.items():
            notes = json.loads((TRIAL / "runs" / pat / s / "notes.json").read_text(encoding="utf-8"))
            for n in notes:
                key = (pat, s, n["fact_id"])
                if key not in L:
                    raise SystemExit("label missing: %s" % (key,))
                m, ty, fo, why = L[key]
                amb = 1 if AMB.search(n["note"]) else 0
                lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (s, n["fact_id"], n["note"].replace("|", "\\|"), MATCH[m], TYPE[ty], "有" if fo else "無", "有" if amb else "無", why))
                if s in tg:
                    cnt["n"] += 1
                    cnt[ty] += 1
                    cnt["foreign"] += fo
                    cnt["amb"] += amb
                    if m == "-":
                        cnt["extra_n"] += 1
                        cnt["extra_V" if ty == "V" else "extra_D" if ty == "D" else "extra_bad"] += 1
                    else:
                        cnt["T_" + m] += 1
        # FN
        lines += ["", "## 対象の見落とし(FN)と理由(judgments_all/rejected/promotionsより)", ""]
        for s, t in tg.items():
            d = TRIAL / "runs" / pat / s
            att = {n["fact_id"] for n in json.loads((d / "notes.json").read_text(encoding="utf-8"))}
            ja = {x["fact_id"]: x for x in json.loads((d / "judgments_all.json").read_text(encoding="utf-8"))}
            rj = {r["fact_id"]: r["reason"] for r in json.loads((d / "rejected.json").read_text(encoding="utf-8"))}
            for f in t["targets"]:
                if f in att:
                    continue
                x = ja.get(f)
                reason = ("rejected:%s" % rj[f]) if f in rj else ("; ".join(x["dropped_by"]) if x and x["dropped_by"] else "不明")
                if pat == B and f in rj:
                    j = (x or {}).get("judgment") or {}
                    reason += " (stage1通過、R=%s)" % j.get("reverse_proposition")
                if pat == B and x and not x["passed"] and not x["dropped_by"]:
                    pass
                lines.append("- %s %s: %s" % (s, f, reason))
        (ev / ("%s_content_label_sheet.md" % pat)).write_text("\n".join(lines), encoding="utf-8")
        summary[pat] = cnt
    (ev / "l1_label_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    sys.path.insert(0, str(TRIAL / "tools"))
    main()
