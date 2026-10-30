# -*- coding: utf-8 -*-
"""別系列モデル独立評価(選定・一般化に使っていない系列。非thinking・出力上限明示)。
 ds    : deepseek-flash(非thinking, max_tokens=1500)。全arm共通の一次独立判定(安価)。
 dspro : deepseek-v4-pro(非thinking, max_tokens=1500)。finalist armのみ(品質確認用、費用約10倍)。
 gem   : gemini-3.8-flash(非thinking, max_out=1500)。ゲートを使わないarm(E1L/E1S/E2)のみに使う。E3/E4はgeminiがゲートに入っているため循環になるので使わない。
判定は『修正せずそのまま選べるか』= 自由な組合せでない(C) かつ 一般化が適切 かつ 意味・用法が正確 かつ 英語として自然。易しい表現は不可の理由にしない。"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg03_llm as L
import kpg03_methods as M

JD = os.path.join(L.WORK, "judge"); os.makedirs(JD, exist_ok=True)
CODES = ["OK", "FREE_COMBINATION", "WORD_ONLY", "NOT_GENERALIZED", "OVER_GENERALIZED", "MEANING_CHANGED", "UNNATURAL", "OTHER"]
SCHEMA = {"name": "kp_judge3", "schema": {"type": "object", "additionalProperties": False, "required": ["judgements"], "properties": {
    "judgements": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "cls", "free_combo", "generalization_ok", "meaning_ok", "selectable", "code"],
        "properties": {"id": {"type": "integer"}, "cls": {"type": "string", "enum": ["W", "F", "C"]}, "free_combo": {"type": "boolean"},
                       "generalization_ok": {"type": "boolean"}, "meaning_ok": {"type": "boolean"}, "selectable": {"type": "boolean"},
                       "code": {"type": "string", "enum": CODES}}}}}}}
RUBRIC = ("あなたは英語学習教材の独立審査員です。各候補(学習者に提示する形・日本語の意味・本文の語句・本文の文)を審査してください。\n"
          "ユーザーは提示された形を修正せずにそのまま選びます。次を判定:\n"
          "- cls: W/F/C(下記定義)。free_combo: 自由な組合せ(F)ならtrue。\n"
          "- generalization_ok: 提示形が適切に一般化されているか(本文固有の名詞・修飾語・時制が残っていない、逆に必要な前置詞・語が欠けたり過度に削られて別の表現になっていない、somethingとsomeoneの使い分けが本文の指す対象に合う)。\n"
          "- meaning_ok: 提示形と日本語の意味が本文での語義・用法を正しく表しているか。\n"
          "- selectable: cls=C かつ generalization_ok かつ meaning_ok かつ英語として自然ならtrue。\n"
          "- code: 不合格の最も主要な理由1つ(OK=合格)。**易しい表現であることは不合格の理由にしない**(基本語の句動詞でも辞書の見出しならC)。\n\n"
          + M.CHUNK_DEFS_V3 + "\n\n出力はJSONのみ: {\"judgements\":[{\"id\":1,\"cls\":\"C\",\"free_combo\":false,\"generalization_ok\":true,\"meaning_ok\":true,\"selectable\":true,\"code\":\"OK\"}, ...]}。説明文は書かない。")


BATCH = 40     # 1 callで審査する最大候補数(rubricの重複課金を避ける。出力はmax_tokens 2600)


def judge_arm(arm, cases, who, results_dir):
    """arm全体を、ケース横断でBATCH件ずつ1 callにまとめて審査する(rubric重複課金の削減)。"""
    rows = []
    for cid in cases:
        p = os.path.join(results_dir, f"{cid}__{arm}.json")
        if os.path.exists(p):
            for i in json.load(open(p, encoding="utf-8"))["items"]:
                rows.append((cid, i))
    out_rows, cost = [], 0.0
    for b0 in range(0, len(rows), BATCH):
        chunk = rows[b0:b0 + BATCH]
        lines = [f"{n}. 表示形: {i['display_form']} / 意味: {i['gloss_ja']} / 本文の語句: {i['source_span']} / 本文の文: {i['source_sentence']}" for n, (c, i) in enumerate(chunk, 1)]
        user = RUBRIC + "\n\n【候補】\n" + "\n".join(lines)
        tag = f"judge3:{who}:{arm}:b{b0 // BATCH}"
        if who == "gem":
            o, m = L.call(M.GEM, user, SCHEMA, tag=tag, think_budget=0, max_out=2600)
        else:
            o, m = L.call_ds("deepseek-flash" if who == "ds" else "deepseek-v4-pro", user, tag=tag, max_tokens=2600)
        cost += m["cost_jpy"]
        jm = {x["id"]: x for x in o["judgements"]}
        for n, (c, i) in enumerate(chunk, 1):
            out_rows.append(dict(case=c, display_form=i["display_form"], span=i["source_span"], j=jm.get(n)))
    out = {"arm": arm, "who": who, "cost": round(cost, 4), "n": len(rows), "rows": out_rows}
    json.dump(out, open(os.path.join(JD, f"{arm}__{who}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--who", required=True, choices=["ds", "dspro", "gem"]); ap.add_argument("--arms", required=True)
    ap.add_argument("--cases", required=True); ap.add_argument("--mock", action="store_true"); ap.add_argument("--phase-cap", type=float, default=0)
    a = ap.parse_args()
    L.set_mock(a.mock)
    if a.phase_cap and not a.mock:
        L.set_phase_cap(a.phase_cap)
    import kpg03_run as R
    cases = R.GROUPS.get(a.cases) or (R.ALL14 if a.cases == "ALL14" else a.cases.split(","))
    rd = os.path.join(L.WORK, "mock_results" if a.mock else "results")
    for arm in a.arms.split(","):
        if a.who == "gem" and arm in ("E3", "E4"):
            print(f"skip {arm}: geminiゲート使用armのgemini独立判定は循環のため実施しない"); continue
        try:
            o = judge_arm(arm, cases, a.who, rd)
        except L.CapReached as e:
            print("CAP_REACHED", e); sys.exit(3)
        bad = [r for r in o["rows"] if not (r["j"] or {}).get("selectable", False)]
        print(arm, a.who, f"n={o['n']} 費用¥{o['cost']} selectable={o['n'] - len(bad)}/{o['n']}", flush=True)
    print(("MOCK " if a.mock else "") + "TOTAL ¥", round(L.total_cost(), 2))
