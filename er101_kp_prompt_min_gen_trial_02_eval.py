# -*- coding: utf-8 -*-
r"""KPMG 独立評価(有料)。Trial①(5モデルの匿名セットをrubric採点)とTrial②(Luna Before→Haiku After)を同一評価者2系統(gpt-6.1-sol, claude-sonnet-5-5)で評価。
KP6Mと同じ評価者・同じ匿名化方式。Trial①rubricはV/E/Nの文言をKP6Mと同一に保ち、G(一般化)を除外、最小化4観点(C,U,S,X)を追加。
使い方: .venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_eval.py --phase t1|t2|both --cap-jpy 300 [--dry-run]。既存eval結果はスキップ。"""
import argparse, json, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import er101_kp_prompt_min_gen_trial_02_common as K
C = K.C
EVALUATORS = {"sol": dict(provider="openai", model_id="gpt-6.1-sol"), "sonnet": dict(provider="anthropic", model_id="claude-sonnet-5-5")}

RUBRIC_T1 = """あなたは英語学習コンテンツの独立評価者です。以下の英語記事から「英語上級者が学ぶ価値のあるKey Phrase」を選ぶ課題があり、
複数の匿名の選定結果(セット S1〜Sn、各5件以内)があります。各候補を下記rubricで採点してください。どのセットがどのモデルの結果かは不明です。

【選定時に参加者へ与えられた条件(参考)】
1. 本文中の連続した語句だけを抜き出す(変更・言い換え・追加・創作は禁止。原形化や一般化は行わない)。
2. 5語以内。
3. 学習ポイントの明確化と最小化: 学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。不要な目的語・修飾語・文脈は除く。5語は上限であり目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。
4. 上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。
5. 基本語だけで構成され字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。
6. 条件を満たす候補から5件選ぶ。適切な候補が不足する場合のみ5件未満とし、数合わせはしない。

【採点rubric(各候補、各0〜2の整数)】
(以下V,E,Nは前回(6モデル比較)と同一の定義)
- V 上級者向け学習価値: 2=上級者でも学ぶ価値が明確(句動詞・イディオム・コロケーション・語法・語彙として) / 1=価値はあるが中程度、または一部平易 / 0=学習価値がほぼない。
- E 易しさの排除: 2=易しい表現ではない(意味が字面から自明でない) / 1=やや易しいが慣用的な意味や語法の学びはある / 0=基本語のみで字面どおり、上級者なら当然知っている。
- N 単位の自然さ: 2=自然で完結した学習単位 / 1=余分な語または不足があるが許容 / 0=中途半端に切られている・不自然。
(以下は今回追加した最小化観点。前回スコアとは別尺度として採点)
- C 学習ポイントの明確さ: 2=何を学ぶ表現かが一目で明確 / 1=やや曖昧(学習点が複数に分散・焦点がぼやける) / 0=何が学習点か不明確。
- U 不要語の除去: 2=不要な目的語・修飾語・文脈語が残っていない / 1=軽微な余分語が残る / 0=学習点に不要な目的語・修飾語・文脈が明らかに残り長い。
- S 最短形: 2=学習価値を保った最短形になっている / 1=もう少し短くできる、または短くしすぎの兆候 / 0=明らかにもっと短くできる(または必要語を欠く)。
- X 短縮の不自然さのなさ: 2=不自然・不完全な形になっていない / 1=やや不自然だが許容 / 0=短縮によって不自然・不完全なフレーズになっている。
セット単位: padding = 5件を埋めるために学習価値の低い候補(V<=0またはE<=0)を入れていると判断するか(true/false)。

【注意】
- 本文との一致・語数は別途機械検証するため、ここでは採点対象外。ただし本文に明らかに存在しない表現と気付いた場合のみ noteに "not_in_text" と書く。
- 候補の優劣を、セットの並び順やセットIDから推測しない。各候補を独立に採点する。
- 候補が0件のセットは candidates を空配列にする。

【出力】JSONのみ(説明文・コードフェンス不要)。noteは通常は空文字、本文に存在しない表現と気付いた場合のみ "not_in_text"。形式:
{"sets":[{"set_id":"S1","padding":false,"candidates":[{"idx":1,"V":2,"E":1,"N":2,"C":2,"U":2,"S":1,"X":2,"note":""}]}]}
"""

RUBRIC_T2 = """あなたは英語学習コンテンツの独立評価者です。英語学習者向けKey Phrase(上級者向けに選定済み)を、別のLLMが『他の場面でも使える汎用的な形』へ整えた結果(Before→After)を評価してください。
一般化担当への指示は次のとおりです: 「固有名詞や特定の人物・物事への依存を取り除き、必要に応じて原形化、単複変換、someone/something等への置換を行う。元の学習ポイント・意味・文法・自然さを維持し、不要な語句は追加しない。一般化が不要な表現は変更しない。各表現は5語以内。」
※Key Phraseの再選定は禁止されており、Beforeと対応するAfterを評価します。変更件数が多いことを高評価としないでください。変更すべきものを適切に変更し、変更不要なものを維持できているかを評価します。

【各項目(Before→After 1組ごと)の判定】
- needs_change: Beforeに、汎用化のために変更すべき要素(固有名詞・特定の人物/物事への依存、学習上は原形で示すのが自然な活用形[過去形/三単現/-ing等]、単複、this/its/youなど文脈依存の指示語・所有格など)が実際にあったか(true=変更すべきだった/false=そのままでよかった)。判断は『学習用の汎用形として』で、Beforeの本文中の文脈文(参考情報)も考慮してよい。
- changed_ok(一般化の適切さ): PASS/NG。needs_change=trueなら、必要な変更が適切に行われているか(適用漏れ・不十分・過剰ならNG)。needs_change=falseなら、変更されていない(または無害な変更)ならPASS、不必要な変更をしていればNG。
- keep_point(学習ポイント維持): PASS/NG。Afterが元の学習ポイント(語彙・語法・イディオム)と意味・文法を維持しているか。
- natural(英語の自然さ): PASS/NG。Afterが自然で文法的な英語表現か(someone/something等の置換で文法が崩れていないか)。
- meaning_change: true/false。Beforeから意味が変わっている、または学習ポイントが別物になっているか。
- over_change: true/false。不必要な変更、または変更しすぎ(学習ポイントを削る/追加語を入れる)があるか。
- missed: true/false。変更すべきだったのに変更していない(適用漏れ)か。
- added_words: true/false。Afterに、Beforeにも許容置換語(someone/something/one's/原形/単複)にもない語が追加されているか。
- note: 問題があれば短く(日本語可)。なければ空文字。

【出力】JSONのみ(説明文・コードフェンス不要)。items配列は入力と同じ順序・件数。形式:
{"items":[{"no":1,"needs_change":true,"changed_ok":"PASS","keep_point":"PASS","natural":"PASS","meaning_change":false,"over_change":false,"missed":false,"added_words":false,"note":""}]}
"""

def extract_json(text):
    s = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(s[s.find("{"):s.rfind("}") + 1])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", default="both"); ap.add_argument("--cap-jpy", type=float, default=300.0)
    ap.add_argument("--evaluators", default="sol,sonnet"); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    out = K.OUT; man = json.loads((out / "inputs" / "manifest_from_kp6m.json").read_text(encoding="utf8"))
    val = json.loads((out / "validation.json").read_text(encoding="utf8"))
    if K.stop_present(): print("STOP"); return 3
    (out / "eval").mkdir(parents=True, exist_ok=True)
    bmap = {}; bm = out / "eval" / "blind_map.json"
    if bm.exists(): bmap = json.loads(bm.read_text(encoding="utf8"))
    jobs = []
    for u in man["units"]:
        uid = u["unit_id"]; art = (C.ROOT / u["copy_path"]).read_text(encoding="utf8")
        if a.phase in ("t1", "both"):
            srcs = [s for s in val["sets"] if s["unit_id"] == uid and s["status"] == "OK"]
            if uid not in bmap:
                order = [s["source"] for s in srcs]; random.Random("er101:" + uid).shuffle(order); bmap[uid] = {("S%d" % (i + 1)): o for i, o in enumerate(order)}
            lines = [RUBRIC_T1, "\n【記事】\n", art, "\n\n【匿名の選定結果】\n"]
            for sid, src in bmap[uid].items():
                s = next(x for x in srcs if x["source"] == src); lines.append("%s:" % sid)
                if not s["candidates"]: lines.append("  (候補なし)")
                for i, c in enumerate(s["candidates"]): lines.append("  %d. %s" % (i + 1, c["phrase"]))
                lines.append("")
            for ev in a.evaluators.split(","):
                rp = out / "eval" / "t1" / ev / ("%s.json" % uid)
                if not rp.exists(): jobs.append(("t1", ev, uid, "\n".join(lines), rp))
        if a.phase in ("t2", "both"):
            g = json.loads((out / "gen" / ("%s.json" % uid)).read_text(encoding="utf8"))
            ctxs = re.findall(r"^(\d+)\. (.+)\n   本文中の該当文\(参考情報\): (.+)$", g["user_message"], flags=re.M)
            assert len(ctxs) == len(g["parsed"]) == 5, uid
            lines = [RUBRIC_T2, "\n【Before→After一覧(入力順)】\n"]
            for (no, before, sent), p in zip(ctxs, g["parsed"]):
                lines.append("%s. Before: %s\n   After: %s\n   変更理由(一般化担当の記述): %s\n   本文中の文脈文(参考情報): %s\n" % (no, before, p["after"], p["reason"], sent))
            for ev in a.evaluators.split(","):
                rp = out / "eval" / "t2" / ev / ("%s.json" % uid)
                if not rp.exists(): jobs.append(("t2", ev, uid, "\n".join(lines), rp))
    bm.write_text(json.dumps(bmap, ensure_ascii=False, indent=1), encoding="utf8")
    print("eval jobs", len(jobs))
    if a.dry_run:
        for j in (jobs[0], [x for x in jobs if x[0] == "t2"][0]): print(j[3][-2500:]); print("=========")
        return 0
    def run(job):
        ph, ev, uid, user, rp = job
        if K.stop_present(): return (ph, ev, uid, "STOPPED", 0)
        if C.ledger_total_jpy() >= a.cap_jpy: return (ph, ev, uid, "CAP_REACHED", 0)
        e = EVALUATORS[ev]; body = C.build_body(e["provider"], e["model_id"], user)
        t0 = time.time(); r = C.call_with_retry(e["provider"], e["model_id"], body)
        rec = dict(phase=ph, evaluator=ev, requested_model_id=e["model_id"], unit_id=uid, user_message_sha256=C.sha_text(user), user_message=user, request_body=body,
                   attempts=r["attempts"], ok=r["ok"], elapsed_s_total=round(time.time() - t0, 2))
        cost = 0.0
        if r["ok"]:
            cost = C.cost_usd(e["model_id"], r["usage"]) * C.USD_JPY
            try: parsed = extract_json(r["text"])
            except Exception as ex: parsed = None; rec["parse_error"] = str(ex)
            rec.update(response_text=r["text"], parsed=parsed, usage=r["usage"], response_id=r["response_id"], model_returned=r["model_returned"], finish=r["finish"], cost_jpy=round(cost, 5), raw_response=r["raw"])
            C.ledger_add(dict(phase="eval_" + ph, evaluator=ev, unit_id=uid, requested=e["model_id"], returned=r["model_returned"], usage=r["usage"], cost_jpy=round(cost, 5), response_id=r["response_id"], ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        rp.parent.mkdir(parents=True, exist_ok=True); rp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf8")
        return (ph, ev, uid, "OK" if r["ok"] else "TECH_FAIL", cost)
    with ThreadPoolExecutor(max_workers=a.workers * 2) as ex:
        for f in as_completed([ex.submit(run, j) for j in jobs]): print(f.result(), "cum_jpy=%.3f" % C.ledger_total_jpy(), flush=True)
    return 0
if __name__ == "__main__": sys.exit(main())
