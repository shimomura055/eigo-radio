# -*- coding: utf-8 -*-
"""別系列モデルによる独立評価(Rubric v2、2軸分離)と、評価器の感度の事前確認(委任_02 手順2)。Trial専用。
評価器の位置づけ: 判定は無条件に正としない(原文§5)。割れた例は根拠を確認(Sonnet実読+必要時sol調停)。
感度確認: 事前登録したNG形(probeのng+過去の実際の誤り)とOK形(probeのok+過去の正しい形)を混ぜて通し、NG検出率>=90%・OK誤NG<=10%を満たした評価器だけを主評価に使う。
使い方: KPG4_CAP=180 python kpg04_eval.py --calib --model deepseek-v4-pro --phase-cap 8
        KPG4_CAP=180 python kpg04_eval.py --arms N2,N4 --cases ALL14 --model deepseek-v4-pro --phase-cap 10"""
import os, sys, re, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L
import kpg04_methods as M
import kpg01_gen2 as G

EVAL_DIR = os.path.join(L.WORK, "eval"); os.makedirs(EVAL_DIR, exist_ok=True)
OLD1 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
OLD2 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02")
VERDICTS = ["OK", "SENSE_SHIFT", "ARG_TYPE", "FRAME_SHIFT", "MOD_SHIFT", "GLOSS_MISMATCH", "GLOSS_SENSE"]

EVAL_RULES = """あなたは英語学習教材の独立審査員です。学習者には『学習用の形(見出し形)』と『日本語の意味』を、本文の語句の根拠つきで提示します。学習者は提示内容が正しいかを自分では判断できません。
各項目について、**本文でその語句が使われている意味・用法**と、**提示された形・日本語の意味**が一致しているかだけを審査してください。次の順に考えること:
(1) 本文の文脈で、語句は何を意味しているか(語義)。(2) 提示された形は、学習者用英英辞書で『本文と同じ語義・同じ構文』の見出しか。(3) 日本語の意味は、提示された形の語義であり、かつ本文の語義と同じか。
verdict(最も主要な1つ):
 OK = 本文と同じ語義・用法の見出し形で、日本語の意味も合っている。
 SENSE_SHIFT = 提示形が別の語義・別の見出しになっている(例: take points away from[減点する] -> take away from[損なう、別見出し])。
 ARG_TYPE = someone/something(one's/someone's)の選択が、**その見出し形の辞書上の標準的な用法**に合わない。判断基準は『本文の目的語が人か物か』ではなく『見出し形の標準用法』
            (例: hear it out[itは擬人化された物] -> 標準は人を取るのでhear someone outが正しくhear something outは誤り。put someone up[泊める]とput something up[建てる]のように語義が分かれる句動詞は本文の語義に合う方が正しい)。
            慣用表現に固定されたit(take it out on / call it a day / lose it / go for it)をsomethingに置き換えるのは誤り。
 FRAME_SHIFT = 構文の枠が変わって語義が不定・別語義になる(目的語・前置詞/粒子の脱落。例: took up space -> take up、looked down on -> look down、came to terms with -> come to terms)。
 MOD_SHIFT = 修飾語の除去で語義が変わる(例: break new ground -> break ground[着工]、give someone a big hand[拍手] -> give someone a hand[手伝う]、take a back seat -> take a seat)。
 GLOSS_MISMATCH = 形は妥当だが日本語の意味が形と対応しない(除いた修飾語・目的語の意味を含む、品詞が合わない等)。
 GLOSS_SENSE = **形は本文と同じで妥当だが、日本語の意味だけが本文と別の語義**(例: take something away from に『価値や効果を損なう』を付ける)。
**意味を損なわない修飾語・冠詞の除去はNGにしない**(set a lower limit -> set a limit、took an unexpected turn -> take a turn、take good care of -> take care of。ただし日本語の意味に除いた修飾語の意味が残っていればGLOSS_MISMATCH)。
活用形の原形化(took -> take)、受動形の能動化なども問題にしない。英語として自然か、自由な組合せか、易しいか難しいかは審査しない(意味・用法の同一性だけ)。迷う場合は、辞書の見出し・用例を根拠にreason_jaへ書く。
各項目: id、verdict、reason_ja(40字以内。OKなら空文字可)のみ返す。"""

EVAL_SCHEMA = {"name": "kp_eval6", "schema": {"type": "object", "additionalProperties": False, "required": ["evals"], "properties": {
    "evals": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["id", "verdict", "reason_ja"],
        "properties": {"id": {"type": "integer"}, "verdict": {"type": "string", "enum": VERDICTS}, "reason_ja": {"type": "string"}}}}}}}


def prompt_eval(items):
    lines = [f"{i}. 本文の語句: {x['span']}\n   文脈: {x['context']}\n   提示された形: {x['display_form']}\n   日本語の意味: {x['gloss']}" for i, x in enumerate(items, 1)]
    return EVAL_RULES + "\n\n【審査対象】\n" + "\n".join(lines)


def run_eval(items, model, *, tag, batch=40):
    """items: [{span, context, display_form, gloss, ...}] -> 同順の [{verdict, reason_ja}]。ds=非thinking JSON mode、その他(sol)=schema強制+effort low。"""
    out = []
    for bi in range(0, len(items), batch):
        chunk = items[bi:bi + batch]
        if model.startswith("deepseek"):
            hint = ("\n\n出力はJSONのみ: " + json.dumps({"evals": [{"id": 1, "verdict": "OK", "reason_ja": ""}]}, ensure_ascii=False)
                    + " の形で全項目分。verdictは" + "/".join(VERDICTS) + "のいずれか。説明文は書かない。")
            o, m = L.call_ds(model, prompt_eval(chunk) + hint, tag=f"{tag}:{bi // batch}:EVAL", max_tokens=4500, mock_name="kp_eval6")
        else:
            o, m = L.call(model, prompt_eval(chunk), EVAL_SCHEMA, effort="low", tag=f"{tag}:{bi // batch}:EVAL", max_out=7000)
        em = {x["id"]: x for x in o.get("evals", [])}
        for i in range(1, len(chunk) + 1):
            x = em.get(i) or {}
            v = x.get("verdict") if x.get("verdict") in VERDICTS else "MISSING"
            out.append({"verdict": v, "reason_ja": x.get("reason_ja", ""), "cost_batch": m.get("cost_jpy")})
    return out


# ---------------- 感度確認用の事前登録セット(probeのok/ngと過去の実例) ----------------
def build_calibration():
    probes = [p for p in json.load(open(os.path.join(HERE, "kpg04_probes.json"), encoding="utf-8")) if p["type"] != "FREE_COMBINATION"]
    items = []
    for p in probes:
        base = dict(span=p["span"], context=p["context"], pid=p["id"], type=p["type"])
        items.append(dict(base, display_form=p["ok"][0], gloss=p["ok_gloss"], expected="OK"))
        for k, ng in enumerate(p["ng"][:1]):
            items.append(dict(base, display_form=ng, gloss=p["ng_gloss"], expected="NG"))
    # 過去の実際の誤り(TRIAL-02 untidi_a2)と、対になる正しい形
    ctx_h = "Before you bring out the storage box, hear it out. A lawyer speaks for the 'put it away' side. That supplement may be taking its job quite seriously."
    ctx_t = "A scorecard might say, 'The fewer things you can see, the better.' But that could take points away from the ways each home has found to make life work."
    real = [("hear it out", ctx_h, "hear something out", "最後まで聞く", "NG", "REAL_hear_E1L"),
            ("hear it out", ctx_h, "hear someone out", "(人)の言い分を最後まで聞く", "OK", "REAL_hear_E2"),
            ("take points away from", ctx_t, "take away from", "〜の価値や効果を損なう", "NG", "REAL_take_E1L"),
            ("take points away from", ctx_t, "take something away from", "〜から評価を差し引く", "OK", "REAL_take_E4"),
            ("take points away from", ctx_t, "take something away from", "〜の価値や効果を損なう", "NG", "REAL_take_formOK_glossNG"),
            ("took an unexpected turn", "The story took an unexpected turn.", "take a turn", "展開が変わる", "OK", "REAL_turn"),
            ("set a lower limit", "The team set a lower limit for the signal.", "set a limit", "限界を設定する", "OK", "REAL_limit"),
            ("set a lower limit", "The team set a lower limit for the signal.", "set a limit", "下限を設定する", "NG", "REAL_limit_gloss_keeps_modifier")]
    for sp, cx, df, gl, ex, pid in real:
        items.append(dict(span=sp, context=cx, display_form=df, gloss=gl, expected=ex, pid=pid, type="REAL"))
    return items


def calib(model, tag):
    items = build_calibration()
    res = run_eval(items, model, tag=f"calib:{tag}")
    ng = [(x, r) for x, r in zip(items, res) if x["expected"] == "NG"]
    ok = [(x, r) for x, r in zip(items, res) if x["expected"] == "OK"]
    det = sum(1 for x, r in ng if r["verdict"] not in ("OK", "MISSING"))
    fals = sum(1 for x, r in ok if r["verdict"] not in ("OK", "MISSING"))
    miss = sum(1 for r in res if r["verdict"] == "MISSING")
    summ = dict(model=model, n=len(items), ng_n=len(ng), ok_n=len(ok), detected=det, detect_rate=round(det / len(ng), 3), false_ng=fals, false_ng_rate=round(fals / len(ok), 3),
                missing=miss, pass_=(det / len(ng) >= 0.9 and fals / len(ok) <= 0.1),
                missed=[(x["pid"], x["display_form"], x["gloss"], r["verdict"]) for x, r in ng if r["verdict"] in ("OK", "MISSING")],
                false=[(x["pid"], x["display_form"], x["gloss"], r["verdict"], r["reason_ja"]) for x, r in ok if r["verdict"] not in ("OK", "MISSING")])
    json.dump(dict(summary=summ, items=[dict(x, **r) for x, r in zip(items, res)]), open(os.path.join(EVAL_DIR, f"calib_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return summ


# ---------------- arm出力の評価対象抽出 ----------------
def changed(it):
    """変化があった項目: 形が本文と異なる/戻した/訳を後段で修正した。"""
    a = " ".join(M._norm_hw(it["display_form"]))
    b = " ".join(M._norm_hw(M.src_form(it["source_span"])))
    return a != b or it.get("reverted") or bool(it.get("gloss_pre_revert") or it.get("gloss_pre_check") or (it.get("gloss_pre_ver") and it["gloss_ja"] != it["gloss_pre_ver"])) \
        or bool((it.get("verify") or {}).get("fix_gloss_ja"))


def load_arm_items(arm, cid, corpus=None):
    if arm == "PROD":
        b = (corpus[cid].get("before") or {}).get("candidates") or []
        return [dict(source_span=x["selection_phrase"], source_sentence=x.get("sentence", ""), display_form=x.get("used_form") or x["selection_phrase"], gloss_ja=x.get("gloss") or "") for x in b if x.get("kind") == "phrase"]
    if arm.startswith("N"):
        p = os.path.join(L.WORK, "results", f"{cid}__{arm}.json")
    elif arm == "D":
        p = os.path.join(OLD1, "kpg01_work", "results", f"{cid}__D_luna.json")
    else:
        p = os.path.join(OLD2, "kpg03_work", "results", f"{cid}__{arm}.json")
        if not os.path.exists(p):                                   # held-outで本Trialが実行したE1L等
            p = os.path.join(L.WORK, "results", f"{cid}__{arm}.json")
    return json.load(open(p, encoding="utf-8"))["items"] if os.path.exists(p) else None


def case_text(corpus, cid):
    return corpus[cid]["text"]


def eval_items_for(arm, cases, corpus, only_changed=True):
    out = []
    for cid in cases:
        its = load_arm_items(arm, cid, corpus)
        if its is None:
            continue
        for it in its:
            if only_changed and arm != "PROD" and not changed(it):
                continue
            out.append(dict(arm=arm, case=cid, span=it["source_span"], display_form=it["display_form"], gloss=it["gloss_ja"],
                            context=M.local_context(case_text(corpus, cid), it.get("source_sentence") or "")))
    return out


if __name__ == "__main__":
    import kpg04_run as R
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", action="store_true"); ap.add_argument("--model", default="deepseek-v4-pro"); ap.add_argument("--tag", default="")
    ap.add_argument("--arms"); ap.add_argument("--cases", default="ALL14"); ap.add_argument("--all-items", action="store_true", help="変化の有無によらず全項目(PRODは常に全項目)")
    ap.add_argument("--phase", default=""); ap.add_argument("--phase-cap", type=float, default=0); ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    L.set_mock(a.mock)
    try:
        if a.phase:
            L.enter_phase(a.phase)
        if a.phase_cap and not a.mock:
            L.set_phase_cap(a.phase_cap)
        tag = a.tag or a.model.replace("deepseek-", "ds-").replace("gpt-6.1-", "")
        if a.calib:
            s = calib(a.model, tag)
            print(json.dumps(s, ensure_ascii=False, indent=1))
        if a.arms:
            corpus = R.load_corpus()
            cases = {"ALL14": R.ALL14, "HELDOUT": R.HELDOUT, "HARD6": R.HARD6}.get(a.cases) or a.cases.split(",")
            for arm in a.arms.split(","):
                items = eval_items_for(arm, cases, corpus, only_changed=not a.all_items)
                res = run_eval(items, a.model, tag=f"eval:{arm}:{tag}") if items else []
                json.dump([dict(x, **r) for x, r in zip(items, res)], open(os.path.join(EVAL_DIR, f"{arm}__{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                bad = [(x["case"], x["display_form"], r["verdict"]) for x, r in zip(items, res) if r["verdict"] != "OK"]
                print(arm, "eval items", len(items), "non-OK", len(bad), bad[:12], flush=True)
    except L.CapReached as e:
        print("CAP_REACHED", e, flush=True)
        sys.exit(3)
    print("TOTAL ¥", round(L.total_cost(), 2))
