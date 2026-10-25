# -*- coding: utf-8 -*-
"""er121_family_y_calibration_02.py
FAMILY-Y-PRODUCTION-LAUNCH-01 委任_05: `leak_discovery_syntax` 判定定義の補足(ユーザー正式承認 USER_03 §2)の較正 evidence runner(DEV/証跡用。
Production runnerではない・どのProduction経路からも参照されない)。判定のみ(生成・書換えなし)。

  run   : 補足後のTension判定prompt(`er121_family_y_text_core_01.build_leak_prompt('tension')`)で、過去のClosing本文(Round1/2の10本・案A初回/A/B/C)
          + 手書きの合成負例3本・合成正例1本を各3回判定する。『変更前』(補足なし=M-1)は、委任_02Aの較正データ(calibration_01)を最大限再利用し、
          calibration_01に無い本文(案A最終・案C・合成)だけ補足なしpromptで3回判定する。結果は calibration_02/ に保存。
  table : 判定ファイルから前後比較表(calibration_table_02.json)を作る(API 0)。

有料runは --paid と --cap-jpy が必要。起動前と一定call数ごとに tools/stop_scope_check_01.py を実行(rc=3で停止)し、実費累計+見積>capで予約停止する。
er006へのY routing key登録は02Bが済ませた前提だが、未登録の場合に限り本processの中だけでPROCESS_MODEL_MAPへ期待値を一時登録する(calibration_01と同じ。記録する)。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import threading

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er121_family_y_calibration_01 as k1
import er121_family_y_text_core_01 as c

OUT = "er110_output/family_y_production_launch_01"
CAL1 = f"{OUT}/calibration_01"
CAL2 = f"{OUT}/calibration_02"
MID = "FAMILY-Y-PRODUCTION-LAUNCH-01"
REV = k1.REV
N_RUNS = 3
# 補足文言の候補。v1=委任文の文言(補足+「ただし…」)、v2=ユーザー承認原文(USER_03 §2)の補足一文のみ(Production採用)。
# 較正の結果(GATE_CALIBRATION_02)でv1は案Bの救済条件と衝突したため、v2を比較する。variantはpromptの当該補足文だけを差し替える(他は同一)。
VARIANTS = {"v1": "Prompt指示に基づく『〜から見えてくる』という提示表現は解釈語と見なさない。ただし、3人の語りに根拠がない解釈、不要な一般化、研究・調査の説明への逆戻りは引き続きFAIL。",
            "v2": "Prompt指示に基づく『〜から見えてくる』という提示表現は解釈語と見なさない。"}   # v2=ユーザー承認原文の一文(Production採用)
# v0=対照(補足なし=変更前のM-1 prompt)を今回あらためて同時期に再判定する。before(calibration_01)は別日時の判定で、判定器の揺らぎ・選択バイアス(前回0 FAILの本文を選ぶと再測定で増えて見える)と補足の効果を分けるため。
VARIANTS["v0"] = None
EST_PER_CALL_JPY = 0.5
STOP_CHECK_EVERY = 6

# 手書きの合成本文(生成していない)。テーマは『宅配の再配達』風の最終パート(Tension)形。judgeはClosing本文だけを見る(Voice本文は渡さない=本番と同じ)。
SYNTHETIC = {
    # 負例: 『見えてくる』を使うが、3人の語りに根拠のない解釈・不要な一般化(社会全体への飛躍)
    "SYN_N1_ungrounded_generalization": (
        "三人の話を並べてみると、今の日本の社会全体が、人と人との信頼をすっかり失ってしまっていることが見えてくる。"
        "結局のところ、人は自分の都合を優先する生き物で、料金を取るかどうかはその表れにすぎない。"
        "あなたは、誰かを信頼して荷物を預けたことがあるだろうか？"),
    # 負例: 『見えてくる』を使うが、研究・調査の説明への逆戻り(割合・地域比較・報告)
    "SYN_N2_research_reversion": (
        "各社の調査を比べると、再配達の割合は荷物全体の約一割で、都市部ほど高いという傾向が見えてくる。"
        "さらに、料金を導入した地域では再配達が減ったという結果も報告されている。"
        "この数字は、あなたの暮らしにどう関わっているだろうか？"),
    # 負例: 『見えてくる』なし。発見・傾向を報じる文構造(従来から禁止の型。補足で緩んでいないことの確認)
    "SYN_N3_discovery_report": (
        "三人の発言を分析した結果、受け取る側の事情が配達の遅れを生む最大の要因であることが明らかになった。"
        "つまり、料金は負担を公平にするための手段だという傾向がある。"
        "あなたは、この結論をどう受け止めるだろうか？"),
    # 正例(合成): Prompt 02が求める『3人の語りに根拠のある見え方』を『見えてくる』で示す(根拠=人物の経験)
    "SYN_P1_grounded_presentation": (
        "三人の話を聞き終えると、午前を指定したのに不在票が入っていた人の戸惑いと、料金を受け取る人にだけ求めることへの違和感が、"
        "どちらも「選べなかった」という同じ言葉から見えてくる。"
        "あなたが最後に荷物を待った日、受け取り方は選べただろうか？"),
}
SYNTH_KIND = {"SYN_N1_ungrounded_generalization": "negative", "SYN_N2_research_reversion": "negative", "SYN_N3_discovery_report": "negative", "SYN_P1_grounded_presentation": "positive"}


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _t(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def targets() -> list:
    """[(name, text, source_path)]。calibration_01の12本 + 案A最終 + 案C + 合成4本。"""
    t = [(n, _t(tp).strip(), tp) for n, tp, _op in k1.targets()]
    t.append(("A_final", _t(f"{REV}/closing_A/closing_final.txt").strip(), f"{REV}/closing_A/closing_final.txt"))
    t.append(("C_final", _t(f"{REV}/closing_C/closing_final.txt").strip(), f"{REV}/closing_C/closing_final.txt"))
    for n, text in SYNTHETIC.items():
        t.append((n, text, "synthetic(handwritten)"))
    return t


def _fails(chk) -> list:
    return sorted({ff for it in chk["flagged_items"] for ff in it["fail_fields"]})


def stop_check(tag: str):
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MID, "--run-dir", CAL2, "--out", f"{CAL2}/stop_check_{tag}.json"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 3:
        raise SystemExit(f"[STOP] stop_scope_check rc=3 ({tag}): 新規API呼出をしない")
    if r.returncode != 0:
        raise SystemExit(f"[STOP] stop_scope_check rc={r.returncode} ({tag}): {r.stderr[:200]}")


def spent_jpy() -> float:
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{CAL2}/raw_usage_log*.jsonl")), 3)


def register_routing_if_needed() -> dict:
    reg = {}
    for key, v in c.ROUTE.items():
        if key not in routing.PROCESS_MODEL_MAP:
            routing.PROCESS_MODEL_MAP[key] = v["model"]
            reg[key] = v["model"]
    return reg


def jdir(variant: str) -> str:
    return f"{CAL2}/judgements" if variant == "v1" else f"{CAL2}/judgements_{variant}"


def install_variant(variant: str):
    """build_leak_prompt(Closing=補足あり版)の補足文だけをvariantの文言へ差し替える(process内のみ。Production moduleのファイルは変えない)。"""
    new, cur = VARIANTS[variant], c.DISCOVERY_SYNTAX_SUPPLEMENT
    if new is None or new == cur:                 # v0(補足なし)は run_leak に discovery_supplement=False を渡して実現する
        return
    orig = c.build_leak_prompt

    def patched(kind, sections, language_note="日本語", discovery_supplement=True):
        pr = orig(kind, sections, language_note, discovery_supplement)
        if kind == "tension" and discovery_supplement:
            assert cur in pr
            pr = pr.replace(cur, new)
        return pr
    c.build_leak_prompt = patched


def build_jobs(variant: str = "v1") -> list:
    """[(name, variant, i)]。after(補足あり)=全本文×3。before(補足なし)=calibration_01に無い本文だけ×3。"""
    have_before = {r["name"] for r in _j(f"{CAL1}/calibration_table.json")["rows"]}
    jobs = []
    for name, _text, _src in targets():
        for i in range(N_RUNS):
            jobs.append((name, "after", i))
        if variant == "v1" and name not in have_before:
            for i in range(N_RUNS):
                jobs.append((name, "before", i))
    return jobs


def cmd_run(a, client):
    os.makedirs(jdir(a.variant), exist_ok=True)
    install_variant(a.variant)
    texts = {n: t for n, t, _s in targets()}
    all_jobs = build_jobs(a.variant)
    if a.job_range:                                          # 並列実行用: 全job一覧のうち [lo:hi) だけを担当(別processで別範囲を同時に流す。同一jobを二重に流さない)
        lo, hi = (int(x) for x in a.job_range.split(":"))
        all_jobs = all_jobs[lo:hi]
    jobs = [j for j in all_jobs if not os.path.exists(f"{jdir(a.variant)}/{j[0]}__{j[1]}_{j[2]}.json")]       # 既存の判定は再課金しない(再開用)
    est = len(jobs) * EST_PER_CALL_JPY
    if spent_jpy() + est > a.cap_jpy:
        raise SystemExit(f"[BUDGET_RESERVE_STOP] spent {spent_jpy()} + est {est} > cap {a.cap_jpy}")
    print(f"[PLAN] jobs={len(jobs)} est_jpy<={est}")
    lock = threading.Lock()
    done = [0]

    def one(job):
        name, variant, i = job
        chk = c.run_leak(client, "tension", {"tension": texts[name]}, stage=f"cal02_{name}_{variant}{i}", discovery_supplement=(variant == "after" and a.variant != "v0"))
        row = {"name": name, "variant": variant, "i": i, "text_sha256": c.w1.sha_text(texts[name]), "fails": _fails(chk), "flagged_items": chk["flagged_items"],
               "prompt_sha256": chk["prompt_sha256"], "model": chk["model"], "effort": chk["effort"], "model_id": chk["meta"].get("model") if isinstance(chk.get("meta"), dict) else None,
               "parsed": chk["parsed"], "supplement_variant": a.variant}
        c.w1.wj(f"{jdir(a.variant)}/{name}__{variant}_{i}.json", row)
        with lock:
            done[0] += 1
            print(f"[CAL02] {name} {variant}{i}: fails={row['fails']}")
        return row

    for s in range(0, len(jobs), STOP_CHECK_EVERY * 2):
        stop_check(f"batch{s // (STOP_CHECK_EVERY * 2)}")
        if spent_jpy() + (len(jobs) - s) * EST_PER_CALL_JPY * 0 > a.cap_jpy:
            raise SystemExit("[BUDGET_STOP] cap exceeded")
        for job in jobs[s:s + STOP_CHECK_EVERY * 2]:          # 逐次(er005 cost loggerのcontextはprocess globalでthread安全でないため並列化しない)
            one(job)
    print("[DONE]", done[0], "spent", spent_jpy())


def cmd_table(a):
    """前後比較表。before=補足なし(M-1)、v1=委任文の文言、v2=ユーザー承認原文の一文のみ(判定ファイルがあるvariantだけ)。"""
    cal1 = {r["name"]: r for r in _j(f"{CAL1}/calibration_table.json")["rows"]}
    rep1 = {r["name"]: r for r in _j(f"{CAL1}/repeat_table.json")["rows"]}
    variants = [v for v in ("v0", "v1", "v2") if os.path.isdir(jdir(v))]
    rows = []
    for name, text, src in targets():
        if name in cal1:
            before = [cal1[name]["new_fails"]] + list(rep1[name]["new_prompt_fails"])
            before_src = "calibration_01 (M-1 prompt; 判定器=gpt-6-luna high)"
        else:
            before = [_j(f"{CAL2}/judgements/{name}__before_{i}.json")["fails"] for i in range(N_RUNS)]
            before_src = "calibration_02 (補足なしprompt; 今回判定)"
        row = {"name": name, "kind": SYNTH_KIND.get(name, "past"), "src": src, "chars": len(text), "has_miete": "見えて" in text, "text_sha256": c.w1.sha_text(text),
               "before_source": before_src, "before_runs": before, "before_n_runs": len(before), "before_any_fail": sum(1 for x in before if x),
               "before_discovery_fail": sum(1 for x in before if "leak_discovery_syntax" in x)}
        for v in variants:
            after = [_j(f"{jdir(v)}/{name}__after_{i}.json")["fails"] for i in range(N_RUNS)]
            row[f"{v}_runs"] = after
            row[f"{v}_any_fail"] = sum(1 for x in after if x)
            row[f"{v}_discovery_fail"] = sum(1 for x in after if "leak_discovery_syntax" in x)
            row[f"{v}_n_runs"] = len(after)
        rows.append(row)
    spent = spent_jpy()
    c.w1.wj(f"{CAL2}/calibration_table_02.json", {"rows": rows, "spent_jpy": spent, "n_runs": N_RUNS, "variants": {v: (VARIANTS[v] if VARIANTS[v] is not None else "(補足なし=変更前のM-1 prompt、今回の対照再測定)") for v in variants}, "production_supplement": c.DISCOVERY_SYNTAX_SUPPLEMENT})
    for r in rows:
        line = f"{r['name']:34s} {r['kind']:8s} miete={int(r['has_miete'])} any_fail before {r['before_any_fail']}/{r['before_n_runs']}"
        for v in variants:
            line += f" | {v} {r[v + '_any_fail']}/{r[v + '_n_runs']} (disc {r[v + '_discovery_fail']})"
        print(line + f" | disc_before {r['before_discovery_fail']}")
    print("spent_jpy", spent)


def main():
    ap = argparse.ArgumentParser(description="Family Y leak_discovery_syntax補足の較正(証跡用)")
    ap.add_argument("cmd", choices=("run", "table"))
    ap.add_argument("--paid", action="store_true")
    ap.add_argument("--cap-jpy", type=float, default=0)
    ap.add_argument("--variant", default="v1", choices=tuple(VARIANTS))
    ap.add_argument("--job-range", default="", help="lo:hi (build_jobs()の添字範囲。並列実行用)")
    ap.add_argument("--log-suffix", default="", help="raw_usage_logのsuffix(並列processごとに別file。集計はraw_usage_log*.jsonlを合算)")
    a = ap.parse_args()
    if a.cmd == "table":
        return cmd_table(a)
    if not a.paid or a.cap_jpy <= 0:
        raise SystemExit("[NO_PAID_FLAG] --paid と --cap-jpy が無いため有料runを起動しません")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    os.makedirs(CAL2, exist_ok=True)
    cl.install(f"{CAL2}/raw_usage_log{a.log_suffix}.jsonl")
    reg = register_routing_if_needed()
    c.w1.wj(f"{CAL2}/entry_point_run{a.log_suffix}.json", {"runner": "er121_family_y_calibration_02.py", "cmd": a.cmd, "management_id": MID, "production_reachable": False, "cap_jpy": a.cap_jpy,
                                            "routing_registered_in_process": reg, "prompt_02_sha256": c.PROMPT_SHA256, "supplement": c.DISCOVERY_SYNTAX_SUPPLEMENT})
    client = vfl01.get_client()
    cmd_run(a, client)


if __name__ == "__main__":
    main()
