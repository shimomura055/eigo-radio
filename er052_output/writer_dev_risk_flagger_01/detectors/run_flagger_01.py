# -*- coding: utf-8 -*-
"""WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01B harness骨格(DEV専用・Production経路とは無関係)。

Risk Flagger: 合否判定しない/Productionを止めない/Rewriteしない/自動修正しない。Flagを立てるだけ。

入力(2方式)
  A) ケース集合 casebank_blind.json  (`make_blind_01.py` で casebank_01.json からラベル列を落として生成)
     スキーマ: {"cases":[{case_id, fact(str) | facts([{fact_id,text}]), sentence, context_before, context_after
                           (または context), article_path}]}
  B) 記事: --ledger ledger.json(list か {"facts":[...]}、各 {fact_id,text}) --article article.md
評価時にラベルを読まない: このファイルはラベルファイルを開かない。ラベル列(label等)を含む入力は拒否する(終了コード2)。
出力: detectors/results/<detector>_<model>_<set>.jsonl  (既存ファイルは上書きしない)
検出器: d0(決定論) / d1map / d1full(タイプ別専用Prompt、Fact対応付け=D0近似 or 台帳全体) / d2(万能)
        d3は --union で既存results同士を和集合(API呼び出しなし)
費用ガード: --max-yen(LLM検出器は必須) + 全検出器合算台帳 cost_ledger.jsonl の累計が --total-cap-yen を超えたら停止。
再試行: 一時障害2回 / JSON・検証違反は1回だけ再呼び出し(上限を増やさない)。
使い方例:
  python run_flagger_01.py --input casebank_blind.json --set cb01 --detector d0
  python run_flagger_01.py --input casebank_blind.json --set cb01 --detector d1map --model gpt-6.1-sol --dry-run
  python run_flagger_01.py --input casebank_blind.json --set cb01 --detector d2 --model gpt-6.1-sol --max-yen 20
  python run_flagger_01.py --union d0,d1map --model gpt-6.1-sol --set cb01 --out-name d3_d0_d1map
"""
import argparse
import datetime
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d0_directional as D0  # noqa: E402
import flagger_lib as L  # noqa: E402
import prompts_flagger as P  # noqa: E402

RESULTS_DIR = os.path.join(HERE, "results")
LOGS_DIR = os.path.join(HERE, "logs")
# 評価対象の入力に含まれてはいけないキー(含む入力は拒否)。ラベルの読み込みは行わない。
FORBIDDEN_KEYS = {"label", "labels", "gold", "expected", "human_label", "human_judgement", "severity_label",
                  "known_incident", "incident_id", "checker_reference", "checker_verdict", "label_note"}
VALID_SEVERITY = ("重大", "非重大")
VALID_TYPES = tuple(P.TYPES) + ("その他",)
TRANSIENT_RETRIES = 2
FORMAT_RETRIES = 1
LLM_DETECTORS = ("d1map", "d1full", "d2")
ALL_DETECTORS = ("d0",) + LLM_DETECTORS
OUT_LOW, OUT_HIGH = 400, 3000  # dry-run見積の出力token幅(推論込み)


# ---------------------------------------------------------------- 入力
def _split_sentences(text):
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    parts = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def check_no_labels(obj, where="input"):
    bad = []

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in FORBIDDEN_KEYS:
                    bad.append(path + "/" + k)
                walk(v, path + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o[:2000]):
                walk(v, path + "[%d]" % i)

    walk(obj, where)
    return bad


def case_to_unit(c):
    facts = c.get("facts")
    if not facts:
        facts = [dict(fact_id=c.get("fact_id", "F"), text=c["fact"])]
    before = c.get("context_before", "")
    after = c.get("context_after", "")
    if not before and not after and c.get("context"):
        before = c["context"]
    return dict(unit_id=c["case_id"], facts=facts,
                sentences=[dict(sid="s1", text=c["sentence"], before=before, after=after)],
                article_path=c.get("article_path", ""))


def load_units(input_path=None, ledger=None, article=None):
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
        bad = check_no_labels(data)
        if bad:
            raise ValueError("入力にラベル列が含まれています(評価時はラベルを読まない。make_blind_01.pyで落としてください): %s" % bad[:5])
        cases = data["cases"] if isinstance(data, dict) else data
        return [case_to_unit(c) for c in cases]
    if ledger and article:
        with open(ledger, encoding="utf-8") as f:
            ld = json.load(f)
        bad = check_no_labels(ld, "ledger")
        if bad:
            raise ValueError("台帳にラベル列が含まれています: %s" % bad[:5])
        facts = ld["facts"] if isinstance(ld, dict) else ld
        facts = [dict(fact_id=x.get("fact_id") or x.get("id"), text=x["text"]) for x in facts]
        with open(article, encoding="utf-8") as f:
            sents = _split_sentences(f.read())
        ss = []
        for i, s in enumerate(sents):
            # 記事モードは全文を渡すため before/after は空(トークン重複を避ける)
            ss.append(dict(sid="s%d" % (i + 1), text=s, before="", after=""))
        return [dict(unit_id=os.path.splitext(os.path.basename(article))[0], facts=facts, sentences=ss,
                     article_path=article)]
    raise ValueError("--input か (--ledger と --article) が必要です")


# ---------------------------------------------------------------- 検証
def validate_flags(text, unit, allowed_types=None):
    """戻り値 (flags_or_None, violations)。"""
    try:
        obj = json.loads(text)
    except Exception as e:  # noqa: BLE001
        m = re.search(r"\{.*\}", text or "", flags=re.S)  # 前後に文が付いた場合の救済(1回だけ)
        if not m:
            return None, ["json_parse_error:%s" % type(e).__name__]
        try:
            obj = json.loads(m.group(0))
        except Exception:  # noqa: BLE001
            return None, ["json_parse_error:%s" % type(e).__name__]
    if not isinstance(obj, dict) or not isinstance(obj.get("flags"), list):
        return None, ["flags_missing"]
    sids = {s["sid"] for s in unit["sentences"]}
    fids = {f["fact_id"] for f in unit["facts"]}
    v, out = [], []
    for i, fl in enumerate(obj["flags"]):
        if not isinstance(fl, dict):
            v.append("flag%d_not_object" % i)
            continue
        if fl.get("sentence_id") not in sids:
            v.append("flag%d_sentence_id_invalid" % i)
        typ = fl.get("type")
        if typ not in VALID_TYPES or (allowed_types and typ not in allowed_types):
            v.append("flag%d_type_invalid" % i)
        if fl.get("severity") not in VALID_SEVERITY:
            v.append("flag%d_severity_invalid" % i)
        c = fl.get("confidence")
        if isinstance(c, bool) or not isinstance(c, (int, float)) or not 0 <= c <= 1:
            v.append("flag%d_confidence_invalid" % i)
        q = fl.get("question")
        if not isinstance(q, str) or not q.strip():
            v.append("flag%d_question_missing" % i)
        fi = fl.get("fact_ids")
        if not isinstance(fi, list) or any(x not in fids for x in fi):
            v.append("flag%d_fact_ids_invalid" % i)
        if not v:
            sent = next(s for s in unit["sentences"] if s["sid"] == fl["sentence_id"])
            out.append(dict(unit_id=unit["unit_id"], sentence_id=fl["sentence_id"], sentence=sent["text"], type=typ,
                            fact_ids=fi, confidence=round(float(c), 2), severity=fl["severity"], question=q.strip()))
    return (out if not v else None), v


# ---------------------------------------------------------------- 計画(呼び出し一覧)
def plan_calls(detector, unit, types=None):
    """[(label, system, user, allowed_types)] を返す。d0は空。"""
    if detector == "d2":
        return [("d2", P.d2_system(), P.build_user(unit), None)]
    types = types or P.TYPES
    calls = []
    if detector == "d1full":
        facts = unit["facts"]
    else:  # d1map: D0の近似対応付け(固有名詞・数値の重なり上位3件)の和集合だけを渡す
        ids, facts = set(), []
        for s in unit["sentences"]:
            for _sc, f in D0.map_facts(s["text"], unit["facts"], top_k=3):
                if f["fact_id"] not in ids:
                    ids.add(f["fact_id"])
                    facts.append(f)
        facts = facts or unit["facts"][:3]
    user = P.build_user(unit, facts_override=facts)
    for t in types:
        calls.append(("d1:" + t, P.d1_system(t), user, (t,)))
    return calls


def dry_run(units, detector, model, max_yen, types=None):
    print("[DRY-RUN] detector=%s model=%s units=%d (API非呼び出し)" % (detector, model, len(units)))
    if detector == "d0":
        print("  費用 JPY 0 (決定論)")
        return 0
    prices = L.load_prices(model)
    n_calls, in_tok = 0, 0
    for u in units:
        for _lab, sysm, user, _a in plan_calls(detector, u, types):
            n_calls += 1
            in_tok += L.estimate_tokens(sysm) + L.estimate_tokens(user)
    print("  呼び出し数(最小)=%d / 最大(形式再呼び出し全件)=%d  見積入力token=%d  出力token/呼び出し=%d-%d"
          % (n_calls, n_calls * (1 + FORMAT_RETRIES), in_tok, OUT_LOW, OUT_HIGH))
    if prices:
        lo = L.cost_yen(prices, in_tok, n_calls * OUT_LOW)
        hi = L.cost_yen(prices, in_tok, n_calls * OUT_HIGH)
        print("  見積費用(登録単価)= JPY %.2f - %.2f / --max-yen=%s / 台帳累計 JPY %.2f" % (lo, hi, max_yen, L.ledger_total()))
    else:
        print("  [REFUSE] %s は pricing_snapshot.json に単価未登録 = 実行不可(fail-closed)" % model)
    return 0


# ---------------------------------------------------------------- 実行
def run_llm(units, detector, model, set_name, max_yen, total_cap_yen, types=None, effort="medium"):
    prices = L.load_prices(model)
    if not prices:
        print("[REFUSED] %s は単価未登録。" % model)
        return 2
    out_path, raw_path = result_paths(detector, model, set_name)
    if os.path.exists(out_path):
        print("既存の結果ファイルがあるため中止(上書き禁止): %s" % out_path)
        return 3
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    client = L.client_for(L.MODELS[model])
    spent = 0.0
    with open(out_path, "a", encoding="utf-8") as fres, open(raw_path, "a", encoding="utf-8") as fraw:
        for unit in units:
            unit_flags, unit_cost, attempts_total, ok_all, usage_sum = [], 0.0, 0, True, 0
            for label, sysm, user, allowed in plan_calls(detector, unit, types):
                adopted, fmt_used, trans_used = None, 0, 0
                while True:
                    if spent >= max_yen or L.ledger_total() >= total_cap_yen:
                        print("費用上限に到達したため停止(run累計 %.3f / max-yen %s / 台帳累計 %.3f / cap %s)"
                              % (spent, max_yen, L.ledger_total(), total_cap_yen))
                        return 4
                    attempts_total += 1
                    ts = datetime.datetime.now().isoformat(timespec="seconds")
                    try:
                        text, usage, rid, mid = L.call_model(client, model, sysm, user, effort=effort)
                    except Exception as e:  # noqa: BLE001
                        fraw.write(json.dumps(dict(unit_id=unit["unit_id"], call=label, ts=ts,
                                                   error=type(e).__name__ + ": " + str(e)[:300]), ensure_ascii=False) + "\n")
                        fraw.flush()
                        if trans_used < TRANSIENT_RETRIES:
                            trans_used += 1
                            time.sleep(2 * trans_used)
                            continue
                        break
                    c = L.cost_yen(prices, usage.get("input_tokens") or 0, usage.get("output_tokens") or 0,
                                   usage.get("cached_tokens") or 0)
                    spent += c
                    unit_cost += c
                    L.ledger_append(dict(purpose="flagger", detector=detector, set=set_name, model=model,
                                         unit_id=unit["unit_id"], call=label, cost_jpy=c, usage=usage, response_id=rid))
                    flags, viol = validate_flags(text, unit, allowed)
                    fraw.write(json.dumps(dict(unit_id=unit["unit_id"], call=label, ts=ts, request=dict(system=sysm, user=user),
                                               response_text=text, usage=usage, response_id=rid, model_id=mid,
                                               violations=viol, cost_jpy=c), ensure_ascii=False) + "\n")
                    fraw.flush()
                    if flags is not None:
                        adopted = flags
                        break
                    if fmt_used < FORMAT_RETRIES:
                        fmt_used += 1
                        continue
                    break
                if adopted is None:
                    ok_all = False
                else:
                    for fl in adopted:
                        fl["detector"] = detector
                        fl["call"] = label
                    unit_flags += adopted
            fres.write(json.dumps(dict(unit_id=unit["unit_id"], detector=detector, model=model, set=set_name,
                                       flags=unit_flags, valid_json=ok_all, attempts=attempts_total,
                                       cost_jpy=unit_cost), ensure_ascii=False) + "\n")
            fres.flush()
    print("完了: %s %s units=%d run費用 JPY %.3f 台帳累計 JPY %.3f" % (detector, model, len(units), spent, L.ledger_total()))
    return 0


def run_d0(units, set_name):
    out_path, _ = result_paths("d0", "none", set_name)
    if os.path.exists(out_path):
        print("既存の結果ファイルがあるため中止(上書き禁止): %s" % out_path)
        return 3
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        for u in units:
            f.write(json.dumps(dict(unit_id=u["unit_id"], detector="d0", model="none", set=set_name,
                                    flags=D0.detect(u), valid_json=True, attempts=0, cost_jpy=0.0), ensure_ascii=False) + "\n")
    print("完了: d0 units=%d -> %s" % (len(units), out_path))
    return 0


def result_paths(detector, model, set_name):
    return (os.path.join(RESULTS_DIR, "%s_%s_%s.jsonl" % (detector, model, set_name)),
            os.path.join(LOGS_DIR, "%s_%s_%s_raw.jsonl" % (detector, model, set_name)))


# ---------------------------------------------------------------- D3 和集合
def union_flags(flag_lists):
    """flag_lists: [(source_name, [flag,...]), ...]。重複除去規則:
    (unit_id, sentence_id, type) が同じFlagは1件に統合し、confidence=最大、sources=検出元の和集合、
    fact_ids=和集合、questionは最大confidenceのものを採用。typeが違えば別Flag(同一文でも残す)。"""
    merged = {}
    for src, flags in flag_lists:
        for fl in flags:
            key = (fl["unit_id"], fl["sentence_id"], fl["type"])
            if key not in merged:
                m = dict(fl)
                m["sources"] = [src]
                m["fact_ids"] = list(fl.get("fact_ids", []))
                merged[key] = m
            else:
                m = merged[key]
                if src not in m["sources"]:
                    m["sources"].append(src)
                for x in fl.get("fact_ids", []):
                    if x not in m["fact_ids"]:
                        m["fact_ids"].append(x)
                if fl["confidence"] > m["confidence"]:
                    m["confidence"] = fl["confidence"]
                    m["question"] = fl["question"]
                if fl.get("severity") == "重大":
                    m["severity"] = "重大"
    return list(merged.values())


def run_union(parts, model, set_name, out_name):
    """parts: 'd0','d1map' など。d0はmodel=none、他は--model。"""
    out_path = os.path.join(RESULTS_DIR, "%s_%s_%s.jsonl" % (out_name, model, set_name))
    if os.path.exists(out_path):
        print("既存の結果ファイルがあるため中止(上書き禁止): %s" % out_path)
        return 3
    per = {}
    for p in parts:
        m = "none" if p == "d0" else model
        path = result_paths(p, m, set_name)[0]
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    r = json.loads(ln)
                    per.setdefault(r["unit_id"], []).append((p, r))
    with open(out_path, "w", encoding="utf-8") as f:
        for uid, lst in per.items():
            flags = union_flags([(p, r["flags"]) for p, r in lst])
            f.write(json.dumps(dict(unit_id=uid, detector=out_name, model=model, set=set_name, flags=flags,
                                    valid_json=all(r["valid_json"] for _p, r in lst), attempts=sum(r["attempts"] for _p, r in lst),
                                    cost_jpy=sum(r["cost_jpy"] or 0 for _p, r in lst)), ensure_ascii=False) + "\n")
    print("完了: union %s -> %s" % (parts, out_path))
    return 0


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="ラベル列を落としたケース集合json(make_blind_01.pyの出力)")
    ap.add_argument("--ledger")
    ap.add_argument("--article")
    ap.add_argument("--set", default="adhoc", dest="set_name")
    ap.add_argument("--detector", choices=ALL_DETECTORS)
    ap.add_argument("--model", default="gpt-6.1-sol", choices=sorted(L.MODELS))
    ap.add_argument("--types", help="d1で実行するタイプ(カンマ区切り、既定=全5タイプ)")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-yen", type=float, default=None)
    ap.add_argument("--total-cap-yen", type=float, default=900.0, help="cost_ledger.jsonl累計の停止上限(総予算1000円の安全側)")
    ap.add_argument("--union", help="例: d0,d1map (和集合。API呼び出しなし)")
    ap.add_argument("--out-name", help="--union の出力検出器名(例 d3_d0_d1map)")
    a = ap.parse_args(argv)
    if a.union:
        if not a.out_name:
            print("[REFUSED] --out-name が必要")
            return 2
        return run_union(a.union.split(","), a.model, a.set_name, a.out_name)
    if not a.detector:
        print("[REFUSED] --detector か --union が必要")
        return 2
    try:
        units = load_units(a.input, a.ledger, a.article)
    except ValueError as e:
        print("[REFUSED] %s" % e)
        return 2
    types = a.types.split(",") if a.types else None
    if a.dry_run:
        return dry_run(units, a.detector, a.model, a.max_yen, types)
    if a.detector == "d0":
        return run_d0(units, a.set_name)
    if a.max_yen is None:
        print("[REFUSED] LLM検出器は --max-yen が必須です。")
        return 2
    return run_llm(units, a.detector, a.model, a.set_name, a.max_yen, a.total_cap_yen, types, a.effort)


if __name__ == "__main__":
    sys.exit(main())
