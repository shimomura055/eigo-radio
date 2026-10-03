# -*- coding: utf-8 -*-
"""OPEN-233 委任_58: floor整合設計のオフライン再生(標準ライブラリのみ、runner/Production未import、LLM/API呼び出しなし、費用0円)。

入力(すべて既存の記録): er052_output/open233_self_recovery_flow_runner_01*/instances*/*.json の cycles[].stage2_results
(claim_text, dev[Checkerフラグ], llm_materiality, materiality, floor_reason)と、Ledger実ファイル。
やること: 各claimについて、現行floor(post-委任_35=列挙複製は対象外)と案F1の「裏取り付きfloor」の決定論部分を計算する。
やらないこと: Stage 2(LLM)の再実行。LLM部分は「記録済みのllm_materiality」を使う。要実測の箇所はそう明記する。
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "er052_output"
OUT = "er052_output/open233_floor_alignment_offline_01"
FLOOR_FLAGS = ["changed_actor", "changed_number", "changed_negation", "changed_comparison", "changed_time"]

LEDGER_FILES = {
    "meta": "er019_output/family_x_refresh_e2e_01/meta/run_03/ledger/verified_fact_ledger.txt",
    "hormuz": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_01/research_ledger/verified_fact_ledger.txt",
    "tip": "er006_output/pool_pilot_01/pool_n9_tip_screens/research/verified_fact_ledger.txt",
}


def ledger_family(inst: str):
    i = inst.lower()
    if "er009" in i:
        return "tip"
    if any(k in i for k in ("meta", "safety_a4", "safety_a5", "bgroup_b4")):
        return "meta"
    if any(k in i for k in ("hormuz", "a2a3", "bgroup_b3")):
        return "hormuz"
    return None  # smallbag等: Ledger未取得(要実測)


_LEDGERS = {}


def load_ledger(fam):
    if fam not in _LEDGERS:
        text = open(LEDGER_FILES[fam], encoding="utf-8").read()
        blocks, cur = {}, None
        for line in text.splitlines():
            m = re.match(r"^\[(?:VERIFIED\] )?([A-Z]+-[A-Z0-9-]+)[\]:]", line)
            if m:
                cur = m.group(1)
                blocks[cur] = [line]
            elif cur is not None:
                blocks[cur].append(line)
        _LEDGERS[fam] = (text, {k: "\n".join(v) for k, v in blocks.items()})
    return _LEDGERS[fam]


# ---------------- 裏取り(決定論)関数 ----------------
EN_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
          "ten": 10, "twice": 2, "half": 0.5, "dozen": 12}
KANJI = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
SCALE = {"million": 1e6, "billion": 1e9, "thousand": 1e3, "万": 1e4, "億": 1e8, "千": 1e3}


def num_tokens(text: str) -> set:
    out = set()
    for m in re.finditer(r"(\d[\d,]*\.?\d*)\s*(million|billion|thousand|万|億|千)?", text or ""):
        v = float(m.group(1).replace(",", "").rstrip(".") or 0)
        out.add(v * SCALE.get(m.group(2), 1))
    for w in re.findall(r"\b[a-z]+\b", (text or "").lower()):
        if w in EN_NUM:
            out.add(float(EN_NUM[w]))
    for m in re.finditer(r"([一二三四五六七八九十])(割|件|人|回|社|つ|名)", text or ""):
        v = KANJI[m.group(1)] * (10 if m.group(2) == "割" else 1)
        out.add(float(v))
    return out


# 3値: CONFIRMED=決定論で不一致を確認(floor維持) / CLEARED=整合の積極的証拠あり(floor解放可) / UNDETERMINED=決定不能(現行どおりfloor維持=fail-closed)
CONFIRMED, CLEARED, UNDETERMINED = "CONFIRMED", "CLEARED", "UNDETERMINED"


def corr_number(claim, ledger_all, fact):
    c, l = num_tokens(claim), num_tokens(ledger_all)
    if c - l:
        return CONFIRMED, "claimの数値がLedger全文に無い"
    if c:
        return CLEARED, "claimの数値トークンは全てLedgerにある"
    return UNDETERMINED, "claimに数値トークン無し"


NEG_EN = re.compile(r"\b(not|no|never|none|nobody|neither|nor|cannot)\b|n't\b", re.I)
NEG_JA = re.compile(r"(ない|なかっ|せず|ず、|ぬ|なし|ません|否定|ではなく)")


def corr_negation(claim, ledger_all, fact):
    claim_neg = bool(NEG_EN.search(claim)) or bool(NEG_JA.search(claim))
    if fact is None:
        return UNDETERMINED, "related_fact_id無し"
    line = fact.splitlines()[0]
    fact_neg = bool(NEG_JA.search(line)) or bool(NEG_EN.search(line))
    if claim_neg != fact_neg:
        return CONFIRMED, "否定語の有無がLedger事実文と異なる"
    if not claim_neg:
        return CLEARED, "両方とも肯定(否定反転は起き得ない)"
    return UNDETERMINED, "両方に否定語(二重否定・述語違いの可能性)"


UP = re.compile(r"\b(rise|rose|risen|rising|up|higher|more|increase\w*|gain\w*|climb\w*|surge\w*|jump\w*|grew|growth)\b|上昇|上げ|増|高|上回|上が|戻", re.I)
DOWN = re.compile(r"\b(fall|fell|falling|drop\w*|lower|less|fewer|decrease\w*|decline\w*|down|dip\w*|slump\w*|shrink\w*|narrow\w*)\b|下落|下げ|低下|減|縮小|下回|下が|落", re.I)


def dirs(text):
    s = set()
    if UP.search(text or ""):
        s.add("UP")
    if DOWN.search(text or ""):
        s.add("DOWN")
    return s


def corr_comparison(claim, ledger_all, fact):
    if fact is None:
        return UNDETERMINED, "related_fact_id無し"
    ref = chr(10).join(l for l in fact.splitlines() if not l.strip().startswith(("notes_for_writer", "source", "ambiguity")))
    c, f = dirs(claim), dirs(ref)
    if c - f:
        return CONFIRMED, f"claimの方向語{sorted(c - f)}がLedger事実に無い"
    if c:
        return CLEARED, f"claimの方向語{sorted(c)}はLedger事実にある(事実側の方向語={sorted(f)})"
    return UNDETERMINED, "claimに方向語無し"


MONTH = {m: i + 1 for i, m in enumerate("january february march april may june july august september october november december".split())}


def time_tokens(text):
    out = set()
    for y in re.findall(r"\b((?:19|20)\d{2})\b", text or ""):
        out.add(("y", y))
    for y in re.findall(r"((?:19|20)\d{2})年", text or ""):
        out.add(("y", y))
    for m, d in re.findall(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2})\b", text or ""):
        if m.lower() in MONTH:
            out.add(("md", MONTH[m.lower()], int(d)))
    for m, d in re.findall(r"(\d{1,2})月(\d{1,2})日", text or ""):
        out.add(("md", int(m), int(d)))
    return out


def corr_time(claim, ledger_all, fact):
    c, l = time_tokens(claim), time_tokens(ledger_all)
    if c - l:
        return CONFIRMED, "claimの年月日がLedger全文に無い"
    if c:
        return CLEARED, "claimの年月日は全てLedgerにある"
    return UNDETERMINED, "claimに年月日トークン無し(継続/再発のような時間関係の変更は字面で判別不能)"


STOP_CAPS = set("the a an in on at it this that these those they he she we i his her its our their but and or so if when while after before as of to for by with from also however then there here what who which how why".split())


def corr_actor(claim, ledger_all, fact):
    """Ledger全文に一度も現れない固有名詞(英語の語頭大文字列、文頭語は除外)が主張にあれば不一致確認。
    役職・一般名詞(users/employees等)の入れ替え・一般化は文字列比較では判別不能=常にUNDETERMINED(整合の証拠は出せない)。"""
    ledger_l = ledger_all.lower()
    names = set()
    for sent in re.split(r"(?<=[.!?])\s+", re.sub(r"[“”\"]", " ", claim)):
        words = re.findall(r"[A-Za-z][A-Za-z’'-]*", sent)[1:]
        run = []
        for w in words + [""]:
            if w[:1].isupper() and w.lower() not in STOP_CAPS and w.lower() not in MONTH:
                run.append(w)
            else:
                if run:
                    names.add(" ".join(run))
                run = []
    new = {n for n in names if n.lower() not in ledger_l}
    if new:
        return CONFIRMED, f"Ledger全文に無い固有名詞: {sorted(new)}(注: 日本語Ledgerの訳語[United States等]も新規と誤判定し得る=安全側)"
    return UNDETERMINED, "固有名詞の新規なし。役職・一般名詞の入れ替え/一般化は判別不能"


CORR = {"changed_number": corr_number, "changed_negation": corr_negation, "changed_comparison": corr_comparison,
        "changed_time": corr_time, "changed_actor": corr_actor}


def f1_verdict(rec, flags):
    """戻り値: (status, detail)。status: CONFIRMED(floor維持) / CLEARED(全発火フラグが整合確認済み=解放) / UNDETERMINED(floor維持、案F4ならTier2へ) / None(Ledger未取得)。"""
    fam = ledger_family(rec["inst"])
    if fam is None:
        return None, {}
    ledger_all, blocks = load_ledger(fam)
    fact = blocks.get(rec["fact"]) if rec.get("fact") else None
    res = {f: CORR[f](rec["claim"], ledger_all, fact) for f in flags}
    sts = [v[0] for v in res.values()]
    if CONFIRMED in sts:
        st = CONFIRMED
    elif sts and all(x == CLEARED for x in sts):
        st = CLEARED
    else:
        st = UNDETERMINED
    return st, res


# ---------------- 記録の収集 ----------------
def collect():
    recs = []
    for p in sorted(glob.glob(f"{ROOT}/open233_self_recovery_flow_runner_01*/instances*/*.json")):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        run = p.replace("\\", "/").split("flow_runner_01")[-1].split("/")[0] or "_base"
        for c in d.get("cycles", []):
            for r in c.get("stage2_results", []):
                dev = r.get("dev", {})
                recs.append({"run": run, "path": p.replace("\\", "/"), "inst": d["instance_id"], "cyc": c["cycle"],
                             "claim": r["claim_text"], "fact": dev.get("related_fact_id"),
                             "flags": [f for f in FLOOR_FLAGS if dev.get(f)],
                             "enum": bool(dev.get("detected_by_enumeration")), "detected_by": r.get("detected_by"),
                             "llm": r.get("llm_materiality"), "fin": r.get("materiality"), "fr": r.get("floor_reason") or ""})
    return recs


def short(detail):
    return {f: f"{v[0]}: {v[1]}" for f, v in detail.items()}


def main():
    recs = collect()
    out = {"n_records": len(recs)}
    floor_recs = [r for r in recs if r["fr"].startswith("deterministic_floor:")]  # 記録上floorが発火したもの
    out["floor_fired_recorded"] = len(floor_recs)
    for r in floor_recs:
        st, detail = f1_verdict(r, r["flags"]) if r["flags"] else (UNDETERMINED, {})
        r["f1"] = st
        r["f1_detail"] = short(detail)
    unavailable = [r for r in floor_recs if r["f1"] is None]
    out["floor_recs_ledger_unavailable"] = {"n": len(unavailable), "instances": dict(Counter(r["inst"] for r in unavailable))}
    used = [r for r in floor_recs if r["f1"] is not None]
    floor_only = [r for r in used if r["llm"] != "BLOCKING"]
    non_enum_fo = [r for r in floor_only if not r["enum"]]
    out["population"] = {
        "floor_recs_evaluable": len(used),
        "floor_only(llm!=BLOCKING)": len(floor_only),
        "  うち列挙複製(委任_35で是正済み、現行コードではfloor対象外)": sum(r["enum"] for r in floor_only),
        "  うち非列挙(現行コードでも残る)": len(non_enum_fo),
        "非列挙floor_only: F1判定": dict(Counter(r["f1"] for r in non_enum_fo)),
        "floor+LLM_BLOCKING(LLMだけでも止まる)": sum(r["llm"] == "BLOCKING" for r in used),
        "floor+LLM_BLOCKING: F1判定": dict(Counter(r["f1"] for r in used if r["llm"] == "BLOCKING")),
    }
    out["non_enum_floor_only_list"] = [
        {"run": r["run"], "inst": r["inst"], "cyc": r["cyc"], "llm": r["llm"], "flags": r["flags"], "F1": r["f1"],
         "detail": r["f1_detail"], "claim": r["claim"][:90]} for r in non_enum_fo]
    K = {"K04": "some calls needed user", "K08": "a human was speaking instead", "K09": "telling users who was speaking",
         "K11": "executive admitted the mistake", "K12": "might think the exchange", "K13": "contract workers would make the calls",
         "K14": "二割の償還", "K15": "During that period", "K17": "fee plan may be replaced", "K19": "prices began to fall",
         "K16": "events driving oil prices", "K18": "貨物を運ぶ側"}
    krows = []
    for k, sub in K.items():
        for r in recs:
            if sub in r["claim"] and (r["flags"] or k == "K04"):
                st, detail = f1_verdict(r, r["flags"]) if r["flags"] else (None, {})
                krows.append({"K": k, "run": r["run"], "inst": r["inst"], "cyc": r["cyc"], "enum": r["enum"], "flags": r["flags"],
                              "llm": r["llm"], "fin": r["fin"], "floor_recorded": r["fr"],
                              "floor_now(post35)": bool(r["flags"]) and not r["enum"], "F1": st, "F1_detail": short(detail)})
    out["K_rows"] = krows
    kk = defaultdict(list)
    for r in krows:
        kk[r["K"]].append(r)
    out["K_summary"] = {k: {"n_records": len(v), "flags_union": sorted({f for r in v for f in r["flags"]}),
                            "n_enum_copy": sum(r["enum"] for r in v), "n_floor_now(post35)": sum(r["floor_now(post35)"] for r in v),
                            "F1": dict(Counter(r["F1"] for r in v)), "llm_labels": dict(Counter(r["llm"] for r in v)),
                            "F1_detail_example": v[0]["F1_detail"]} for k, v in kk.items()}
    # Safety12
    safety12 = []
    for p in sorted(glob.glob(f"{ROOT}/open233_self_recovery_flow_runner_01/instances/safety_er009_*.json")):
        d = json.load(open(p, encoding="utf-8"))
        flagname = d["instance_id"].replace("safety_er009_", "")
        for r in d["cycles"][0]["stage2_results"]:
            if r.get("detected_by") == "precheck":
                continue
            dev = r["dev"]
            flags = [f for f in FLOOR_FLAGS if dev.get(f)]
            rec = {"inst": d["instance_id"], "claim": r["claim_text"], "fact": dev.get("related_fact_id")}
            st, detail = f1_verdict(rec, flags) if flags else (None, {})
            safety12.append({"er009_flag": flagname, "floor_flags": flags, "llm_recorded": r["llm_materiality"], "F1": st,
                             "detail": short(detail), "note": "" if flags else "floor対象フラグ無し(LLMのみ=floor変更の影響なし)"})
    out["safety12"] = safety12
    SC = {"bgroup_B3": ("HF-007", "flashy 20% plan"), "safety_A2A3": ("HF-003", "repay the money"),
          "safety_A4": ("MUSE-HC-006", "completed the exchanges with users"),
          "safety_A5": ("MUSE-HC-012", "temporarily put back the feature"), "bgroup_B4": ("MUSE-HC-002", "take over when AI alone has trouble")}
    sc_rows = []
    for inst, (fid, sub) in SC.items():
        hit = [r for r in recs if r["inst"] == inst and r["fact"] == fid and sub in r["claim"]]
        flagged = [r for r in hit if r["flags"]]
        f1s = [f1_verdict(r, r["flags"])[0] for r in flagged]
        fo = [r for r in hit if r["flags"] and r["llm"] != "BLOCKING" and not r["enum"]]
        sc_rows.append({"sc": inst, "n_records": len(hit), "llm_labels": dict(Counter(r["llm"] for r in hit)),
                        "n_with_floor_flag": len(flagged), "flag_union": sorted({f for r in flagged for f in r["flags"]}),
                        "F1_of_flagged": dict(Counter(f1s)),
                        "n_held_only_by_floor(llm!=BLOCKING,非列挙)": len(fo),
                        "held_only_by_floor_F1": [f1_verdict(r, r["flags"])[0] for r in fo]})
    out["safety_critical"] = sc_rows
    json.dump(out, open(f"{OUT}/replay_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(f"{OUT}/K_rows.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["K", "run", "inst", "cyc", "enum", "flags", "llm", "fin", "floor_recorded", "floor_now_post35", "F1", "F1_detail"])
        for r in krows:
            w.writerow([r["K"], r["run"], r["inst"], r["cyc"], r["enum"], "|".join(r["flags"]), r["llm"], r["fin"], r["floor_recorded"],
                        r["floor_now(post35)"], r["F1"], json.dumps(r["F1_detail"], ensure_ascii=False)])
    print(json.dumps({k: out[k] for k in ("n_records", "floor_fired_recorded", "floor_recs_ledger_unavailable", "population")}, ensure_ascii=False, indent=1))
    print("--- 非列挙floor_only一覧 ---")
    for r in out["non_enum_floor_only_list"]:
        print(r["run"], r["inst"], r["cyc"], r["llm"], r["flags"], r["F1"], "|", r["claim"])
    print("--- K要約 ---")
    for k, v in out["K_summary"].items():
        print(k, v["flags_union"], "n=", v["n_records"], "enum=", v["n_enum_copy"], "floor_now=", v["n_floor_now(post35)"], "F1=", v["F1"], "llm=", v["llm_labels"])
    print("--- safety12 ---")
    for r in safety12:
        print(r["er009_flag"], r["floor_flags"], r["llm_recorded"], r["F1"], r["note"], r["detail"])
    print("--- safety_critical ---")
    for r in sc_rows:
        print(r)


if __name__ == "__main__":
    main()
