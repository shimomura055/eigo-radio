# -*- coding: utf-8 -*-
"""WRITER-DEV-RISK-FLAGGER-DESIGN-01 harness(DEV専用・Production経路とは無関係)。委任_01B骨格 -> 委任_02 P0で改修。

Risk Flagger: 合否判定しない/Productionを止めない/Rewriteしない/自動修正しない。Flagを立てるだけ。

入力(2方式)
  A) ケース集合 casebank_01_<split>_blind.json  (`make_blind_01.py` が casebank_01.json から生成。ラベル・出典を除去済み)
     実スキーマ: {"cases":[{case_id, lang, fact{id,text[,src]}, sentence, context{before,after[,source]},
                            ledger[{fact_id,text}] (=当該記事の全台帳、無ければfact.srcから復元)}]}
     LLMへ渡すのは facts(=全台帳: fact_id,text) と sentences(対象文+before/after)のみ。src/source/notes等は渡さない。
  B) 記事: --ledger ledger.json か verified_fact_ledger.txt と --article article.md
     記事モードは全文を渡す。見出しも文として残す(削除しない)。
評価時にラベルを読まない: このファイルはラベルファイルを開かない。ラベル列(flagger_lib.LABEL_KEYS)を含む入力は拒否する(終了コード2)。
出力: detectors/results/<detector>_<model>_<set>.jsonl  (既存ファイルは上書きしない)
検出器: d0(決定論) / d1full(タイプ別専用Prompt、台帳全体を渡す。D1mapは廃止) / d2(万能) / d2rank(記事モード: 上位3文を必ず列挙)
        d3は --union で既存results同士を和集合(API呼び出しなし)。D0の和集合投入は rollback反転 のみ(gate_only除外)。
D1のタイプ別適用先はラベルで選ばない: 既定=全5タイプ。--gate d0 でD0のラベル不使用ゲート(d0_directional.gate_types)で絞れる。
費用ガード: --max-yen(LLM検出器は必須) + 全検出器合算台帳 cost_ledger.jsonl の累計が --total-cap-yen を超えたら停止。
  注意(費用台帳の限界): 上限判定は『呼び出し前』に行うため、最後の1呼び出し分だけ上限を超え得る。また課金後に
  タイムアウト等で応答を受け取れなかった呼び出しはusageが取れず台帳に載らない(過少計上)。実費は台帳×登録単価の概算。
再試行: 一時障害2回 / JSON・検証違反は1回だけ再呼び出し(上限を増やさない)。
使い方例:
  python run_flagger_01.py --input ../casebank/casebank_01_dev_blind.json --set dev --detector d0
  python run_flagger_01.py --input ../casebank/casebank_01_dev_blind.json --set dev --detector d1full --dry-run
  python run_flagger_01.py --input ../casebank/casebank_01_dev_blind.json --set dev_rep1 --detector d2 --max-yen 20
  python run_flagger_01.py --ledger L.txt --article a.md --set art1 --detector d2rank --max-yen 5
  python run_flagger_01.py --union d0,d1full --model gpt-6.1-sol --set dev --out-name d3_d0_d1full
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d0_directional as D0  # noqa: E402
import flagger_lib as L  # noqa: E402
import ledger_restore_01 as LR  # noqa: E402
import prompts_flagger as P  # noqa: E402

RESULTS_DIR = os.path.join(HERE, "results")
LOGS_DIR = os.path.join(HERE, "logs")
# 評価対象の入力に含まれてはいけないキー(含む入力は拒否)。make_blind_01.pyと共有(flagger_lib.LABEL_KEYS)。
FORBIDDEN_KEYS = set(L.LABEL_KEYS)
VALID_SEVERITY = ("重大", "非重大")
VALID_TYPES = tuple(P.TYPES) + (P.CAUSAL_TYPE, "その他")
TRANSIENT_RETRIES = 2
FORMAT_RETRIES = 1
LLM_DETECTORS = ("d1full", "d1v2", "d2", "d2rank")
ALL_DETECTORS = ("d0",) + LLM_DETECTORS
NO_CAUSAL = False  # --no-causal: d1v2から因果創作を外す(レイアウト回帰確認用)
OUT_LOW, OUT_HIGH = 400, 3000  # dry-run見積の出力token幅(推論込み)。P1実測後に detectors/COST_UPDATE_01.md で更新する。


# ---------------------------------------------------------------- 入力
def _split_sentences(text):
    """見出し行も文として残す(委任_02 P0: 見出しを削除しない)。空行・改行・文末記号で分割。"""
    parts = re.split(r"(?<=[.!?])\s+|(?<=[。！？])(?![」』）)\s])\s*|\n+", text)  # 委任_03: 日本語は『。』の直後(空白なし)でも分割
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
            for i, v in enumerate(o[:5000]):
                walk(v, path + "[%d]" % i)

    walk(obj, where)
    return bad


def case_to_unit(c):
    """casebank実スキーマ -> unit。LLMに渡るのは facts(fact_id,text) と sentences(sid,text,before,after) のみ。
    fact.src / context.source / notes 等は読まない(渡さない)。台帳は c['ledger'] があればそれ、無ければ fact.srcから復元、
    それも無理ならfact単体。"""
    fact = c.get("fact")
    ctx = c.get("context") or {}
    if isinstance(fact, str):  # 旧フラット形式(互換)
        fact = dict(id=c.get("fact_id", "F"), text=fact)
    fact = fact or {}
    ledger = c.get("ledger")
    complete = bool(c.get("ledger_complete", bool(ledger)))
    if not ledger:
        r = LR.restore_for_cases([c]).get(c["case_id"])
        ledger, complete = (r["ledger"], r["ledger_complete"]) if r else ([], False)
    facts = [dict(fact_id=f["fact_id"], text=f["text"]) for f in ledger]
    if not facts and fact.get("text"):
        facts = [dict(fact_id=fact.get("id") or "F", text=LR.strip_prefix(fact["text"]))]
    before = ctx.get("before", "") or c.get("context_before", "")
    after = ctx.get("after", "") or c.get("context_after", "")
    return dict(unit_id=c["case_id"], mode="case", facts=facts, ledger_complete=complete,
                sentences=[dict(sid="s1", text=c["sentence"], before=before, after=after)])


def load_ledger(path):
    if path.lower().endswith(".txt"):
        facts = LR.parse_ledger_file(path)
    else:
        with open(path, encoding="utf-8") as f:
            ld = json.load(f)
        bad = check_no_labels(ld, "ledger")
        if bad:
            raise ValueError("台帳にラベル列が含まれています: %s" % bad[:5])
        facts = ld["facts"] if isinstance(ld, dict) else ld
        facts = [dict(fact_id=x.get("fact_id") or x.get("id"), text=x["text"]) for x in facts]
    return facts


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
        facts = load_ledger(ledger)
        with open(article, encoding="utf-8") as f:
            sents = _split_sentences(f.read())
        # 記事モードは全文を渡すため before/after は空(トークン重複を避ける)
        ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)]
        return [dict(unit_id=os.path.splitext(os.path.basename(article))[0], mode="article", facts=facts, sentences=ss,
                     ledger_complete=True, article_path=article)]
    raise ValueError("--input か (--ledger と --article) が必要です")


# ---------------------------------------------------------------- 検証
def validate_flags(text, unit, allowed_types=None, max_flags=None, rank_n=None):
    """戻り値 (flags_or_None, violations)。max_flags: D1の上限(超過分は確信度順で切り捨てて採用、違反にしない)。
    rank_n: d2rank用。ちょうどrank_n件・sentence_id重複なしを要求。"""
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
        mt = fl.get("mismatch_terms", [])
        if rank_n and (not isinstance(mt, list) or any(not isinstance(x, str) for x in mt)):
            v.append("flag%d_mismatch_terms_invalid" % i)
        if not v:
            sent = next(s for s in unit["sentences"] if s["sid"] == fl["sentence_id"])
            row = dict(unit_id=unit["unit_id"], sentence_id=fl["sentence_id"], sentence=sent["text"], type=typ,
                       fact_ids=fi, confidence=round(float(c), 2), severity=fl["severity"], question=q.strip())
            if rank_n:
                row["mismatch_terms"] = mt
                row["rank"] = fl.get("rank")
            out.append(row)
    if rank_n and not v:
        if len(out) != rank_n:
            v.append("rank_count_%d_expected_%d" % (len(out), rank_n))
        elif len({x["sentence_id"] for x in out}) != len(out):
            v.append("rank_duplicate_sentence_id")
    if v:
        return None, v
    if max_flags and len(out) > max_flags:
        out = sorted(out, key=lambda x: -x["confidence"])[:max_flags]
        for x in out:
            x["truncated_to_max"] = True
    return out, []


# ---------------------------------------------------------------- 計画(呼び出し一覧)
def d1_types(unit, types=None, gate=None):
    ts = list(types or P.TYPES)
    if gate == "d0":
        g = D0.gate_types(unit)
        ts = [t for t in ts if t in g]
    return ts


def plan_calls(detector, unit, types=None, gate=None):
    """[(label, system, user, allowed_types, max_flags, rank_n)] を返す。d0は空。"""
    user = P.build_user(unit)
    if detector == "d2":
        return [("d2", P.d2_system(), user, None, None, None)]
    if detector == "d2rank":
        n = min(P.D2RANK_N, len(unit["sentences"]))
        return [("d2rank", P.d2rank_system(len(unit["sentences"])), user, None, None, n)]
    if detector == "d1full":
        return [("d1:" + t, P.d1_system(t), user, (t,), P.D1_MAX_FLAGS, None) for t in d1_types(unit, types, gate)]
    if detector == "d1v2":
        # 委任_03: レイアウトv2(台帳+文を先頭・タイプ別指示を末尾)。既定=D0ゲートの対象タイプ + 因果創作(ゲートなしで常に呼ぶ)。
        # --types を指定した場合はその通り(因果創作を含めたければ明示する)。
        if types:
            ts = list(types)
        else:
            ts = d1_types(unit, None, gate) if gate else list(P.TYPES)
            ts = [t for t in P.TYPES if t in ts] + ([] if NO_CAUSAL else [P.CAUSAL_TYPE])
        return [("d1:" + t, P.d1v2_system(), P.d1v2_user(t, unit), (t,), P.D1_MAX_FLAGS, None) for t in ts]
    return []


def dry_run(units, detector, model, max_yen, types=None, gate=None):
    print("[DRY-RUN] detector=%s model=%s units=%d gate=%s (API非呼び出し)" % (detector, model, len(units), gate))
    if detector == "d0":
        print("  費用 JPY 0 (決定論)")
        return 0
    prices = L.load_prices(model)
    n_calls, in_tok = 0, 0
    for u in units:
        for call in plan_calls(detector, u, types, gate):
            n_calls += 1
            in_tok += L.estimate_tokens(call[1]) + L.estimate_tokens(call[2])
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
def run_llm(units, detector, model, set_name, max_yen, total_cap_yen, types=None, effort="medium", gate=None, resume=False):
    prices = L.load_prices(model)
    if not prices:
        print("[REFUSED] %s は単価未登録。" % model)
        return 2
    out_path, raw_path = result_paths(detector, model, set_name)
    done_ids = set()
    if os.path.exists(out_path):
        if not resume:
            print("既存の結果ファイルがあるため中止(上書き禁止): %s" % out_path)
            return 3
        # resume: 完了済みunit_id(valid_json=True)はスキップ。追記のみで、既存行は書き換えない。
        with open(out_path, encoding="utf-8") as f0:
            done_ids = {json.loads(x)["unit_id"] for x in f0 if x.strip()}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    client = L.client_for(L.MODELS[model])
    spent = 0.0
    with open(out_path, "a", encoding="utf-8") as fres, open(raw_path, "a", encoding="utf-8") as fraw:
        for unit in units:
            if unit["unit_id"] in done_ids:
                continue
            unit_flags, unit_cost, attempts_total, ok_all, called = [], 0.0, 0, True, []
            for label, sysm, user, allowed, max_flags, rank_n in plan_calls(detector, unit, types, gate):
                called.append(label)
                adopted, fmt_used, trans_used = None, 0, 0
                while True:
                    if spent >= max_yen or L.ledger_total() >= total_cap_yen:
                        print("費用上限に到達したため停止(run累計 %.3f / max-yen %s / 台帳累計 %.3f / cap %s)"
                              % (spent, max_yen, L.ledger_total(), total_cap_yen))
                        return 4
                    attempts_total += 1
                    ts = datetime.datetime.now().isoformat(timespec="seconds")
                    try:
                        text, usage, rid, mid = L.call_model(client, model, sysm, user, effort=effort, cache_key="rf-%s-%s" % (detector, hashlib.md5(json.dumps(unit["facts"], ensure_ascii=False).encode("utf-8")).hexdigest()[:10]))
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
                    flags, viol = validate_flags(text, unit, allowed, max_flags, rank_n)
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
                                       cost_jpy=unit_cost, calls=called, gate=gate), ensure_ascii=False) + "\n")
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
def union_flags(flag_lists, include_gate_only=False):
    """flag_lists: [(source_name, [flag,...]), ...]。重複除去規則:
    (unit_id, sentence_id, type) が同じFlagは1件に統合し、confidence=最大、sources=検出元の和集合、
    fact_ids=和集合、questionは最大confidenceのものを採用。typeが違えば別Flag(同一文でも残す)。
    D0のgate_only Flag(不在断定・数量時系列・増減/許可反転)は和集合に入れない(include_gate_only=Trueの時のみ)。"""
    merged = {}
    for src, flags in flag_lists:
        for fl in flags:
            if fl.get("gate_only") and not include_gate_only:
                continue
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


def run_union(parts, model, set_name, out_name, include_gate_only=False):
    """parts: 'd0','d1full' など。d0はmodel=none、他は--model。"""
    out_path = os.path.join(RESULTS_DIR, "%s_%s_%s.jsonl" % (out_name, model, set_name))
    if os.path.exists(out_path):
        print("既存の結果ファイルがあるため中止(上書き禁止): %s" % out_path)
        return 3
    per = {}
    for part in parts:
        p, _, pset = part.partition(":")  # 'd1full:dev_gate' のように検出器ごとに別set名を指定可(省略時は --set)
        m = "none" if p == "d0" else model
        path = result_paths(p, m, pset or set_name)[0]
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    r = json.loads(ln)
                    per.setdefault(r["unit_id"], []).append((p, r))
    with open(out_path, "w", encoding="utf-8") as f:
        for uid, lst in per.items():
            flags = union_flags([(p, r["flags"]) for p, r in lst], include_gate_only)
            f.write(json.dumps(dict(unit_id=uid, detector=out_name, model=model, set=set_name, flags=flags,
                                    valid_json=all(r["valid_json"] for _p, r in lst), attempts=sum(r["attempts"] for _p, r in lst),
                                    cost_jpy=sum(r["cost_jpy"] or 0 for _p, r in lst)), ensure_ascii=False) + "\n")
    print("完了: union %s -> %s" % (parts, out_path))
    return 0


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="盲検ケース集合json(make_blind_01.pyの出力 casebank_01_<split>_blind.json)")
    ap.add_argument("--ledger", help="台帳(json または verified_fact_ledger.txt)")
    ap.add_argument("--article")
    ap.add_argument("--set", default="adhoc", dest="set_name")
    ap.add_argument("--detector", choices=ALL_DETECTORS)
    ap.add_argument("--model", default="gpt-6.1-sol", choices=sorted(L.MODELS))
    ap.add_argument("--types", help="d1fullで実行するタイプ(カンマ区切り、既定=全5タイプ。ラベルで選ばないこと)")
    ap.add_argument("--gate", choices=["d0"], help="d1fullのタイプ絞り込み: D0のラベル不使用ゲート(d0_directional.gate_types)")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-causal", action="store_true", help="d1v2の既定に含まれる因果創作を外す")
    ap.add_argument("--resume", action="store_true", help="既存結果の完了済みunitをスキップして追記(上書きはしない)")
    ap.add_argument("--max-yen", type=float, default=None)
    ap.add_argument("--total-cap-yen", type=float, default=900.0, help="cost_ledger.jsonl累計の停止上限(総予算1000円の安全側)")
    ap.add_argument("--union", help="例: d0,d1full または d0:dev,d1full:dev_gate (和集合。API呼び出しなし。D0はrollback反転のみ)")
    ap.add_argument("--include-gate-only", action="store_true", help="--union時にD0のgate_only Flagも含める(既定は含めない)")
    ap.add_argument("--out-name", help="--union の出力検出器名(例 d3_d0_d1full)")
    a = ap.parse_args(argv)
    global NO_CAUSAL
    NO_CAUSAL = a.no_causal
    if a.union:
        if not a.out_name:
            print("[REFUSED] --out-name が必要")
            return 2
        return run_union(a.union.split(","), a.model, a.set_name, a.out_name, a.include_gate_only)
    if not a.detector:
        print("[REFUSED] --detector か --union が必要")
        return 2
    try:
        units = load_units(a.input, a.ledger, a.article)
    except ValueError as e:
        print("[REFUSED] %s" % e)
        return 2
    if a.detector == "d2rank" and any(u["mode"] != "article" for u in units):
        print("[REFUSED] d2rank は記事モード(--ledger と --article)専用です。")
        return 2
    types = a.types.split(",") if a.types else None
    if a.dry_run:
        return dry_run(units, a.detector, a.model, a.max_yen, types, a.gate)
    if a.detector == "d0":
        return run_d0(units, a.set_name)
    if a.max_yen is None:
        print("[REFUSED] LLM検出器は --max-yen が必須です。")
        return 2
    return run_llm(units, a.detector, a.model, a.set_name, a.max_yen, a.total_cap_yen, types, a.effort, a.gate, a.resume)


if __name__ == "__main__":
    sys.exit(main())
