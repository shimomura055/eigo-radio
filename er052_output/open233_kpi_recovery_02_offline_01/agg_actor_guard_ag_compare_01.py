# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_07 作業3(¥0、実装しない): actor_guard是正案AG1の決定論部分のreplay。
# 入力: agg_actor_guard_01.json(全ログの actor_guard_rejected 7試行)。
# AG1(Ledger照合型, 設計のみ): 新主体語が (i)元文の主体 / (ii)関連fact(または同Ledger内のfact)に記載の主体(日英同義語表で正規化)
#   / (iii)Checker issue・explanationが名指しした主体 のいずれかに一致すれば許容、なければ拒否。
#   - AG1-strict : (i)+(ii: 関連factのみ)+(iii)
#   - AG1-ledger : (i)+(ii: 同Ledger全fact)+(iii)
# 「正当拒否を維持」の測定: 全ログに正当拒否が0件のため、実拒否案の新主体語を、Ledger・issueに無い主体語(合成)へ差し替えた
# 合成対照(synthetic、推測ベース)で拒否が維持されるかを確認する。
import json, os, re, sys
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
# 日英同義語表(設計素材。AG1実装時は全25主体語分を整備し、Ledger言語[JA/EN]の両方を持つ)
SYN = {
    "user": ["user", "利用者", "ユーザー", "使用者"],
    "customer": ["customer", "client", "顧客", "お客", "消費者", "客"],
    "passenger": ["passenger", "乗客", "rider"],
    "contractor": ["contractor", "contract worker", "contract staff", "契約スタッフ", "契約労働者", "契約社員", "請負", "業務委託"],
    "worker": ["worker", "contract worker", "contract staff", "労働者", "従業員", "契約スタッフ", "作業員"],
    "staff": ["staff", "スタッフ", "職員", "従業員", "契約スタッフ"],
    "employee": ["employee", "従業員", "社員"],
    "agent": ["agent", "エージェント"],
    "executive": ["executive", "経営", "幹部", "役員"],
    "client": ["client", "顧客", "依頼"],
    "engineer": ["engineer", "エンジニア", "技術者"],
    "manager": ["manager", "管理者", "マネージャー"],
    "official": ["official", "当局", "政府関係者", "当局者"],
    "analyst": ["analyst", "アナリスト"],
    "trader": ["trader", "トレーダー"],
    "investor": ["investor", "投資家"],
    "driver": ["driver", "運転手", "ドライバー"],
}
def lem(a):
    a = a.lower()
    if a in SYN: return a
    return a[:-1] if a.endswith("s") and a[:-1] in SYN else a
def terms(a): return SYN.get(lem(a), [lem(a)])
def present(a, text):
    t = (text or "").lower()
    return any(x.lower() in t for x in terms(a))
rows = json.load(open(f"{OUT}/agg_actor_guard_01.json", encoding="utf-8"))
ins = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
def fact_block(led, fid):
    m = re.search(r"(?:\[" + re.escape(fid) + r"\]|\] " + re.escape(fid) + r":).*?(?=\n\n|\n===|\Z)", led or "", re.S) if fid else None
    return m.group(0) if m else ""
def ag1(row, mode, new_actors=None, issue_text=None):
    led = ins.get(row["instance"].replace("(repro)", ""), "")
    fb = fact_block(led, row["related_fact_id"])
    issue = issue_text if issue_text is not None else row["issue"]
    na = new_actors if new_actors is not None else row["new_actors"]
    res = {}
    for a in na:
        src = []
        if present(a, issue): src.append("issue")
        if present(a, fb): src.append("related_fact")
        if mode == "ledger" and present(a, led): src.append("ledger")
        res[a] = src
    return bool(na) and all(res.values()), res
full_issue = {}
for r in rows:
    # issueは切り詰め保存(400字)のため、元JSONから全文を取り直す
    pass
print("=== A: 実拒否7試行に対する判定(現行guard=全件拒否)")
tab = []
for r in rows:
    ok_s, rs = ag1(r, "strict"); ok_l, rl = ag1(r, "ledger")
    tab.append((r["run"], r["instance"], r["cycle"], r["level"], r["new_actors"], ok_s, rs, ok_l, rl))
    print(r["run"], r["instance"], "c", r["cycle"], r["level"], r["new_actors"], "| AG1-strict allow:", ok_s, rs, "| AG1-ledger allow:", ok_l, rl)
print("AG1-strict 許容(=過剰拒否解消):", sum(1 for t in tab if t[5]), "/", len(tab), " AG1-ledger:", sum(1 for t in tab if t[7]), "/", len(tab))
print("record単位(同record内で1試行でも許容されれば解消): ")
by = {}
for t, r in zip(tab, rows): by.setdefault((r["run"], r["instance"], r["cycle"], r["rec_idx"]), []).append(t)
for k, v in by.items(): print(" ", k, "strict解消:", any(x[5] for x in v), "ledger解消:", any(x[7] for x in v))
print()
print("=== B: 合成対照(正当拒否の維持): 実案の新主体語を、Ledger・issueに無い主体語へ差し替え(synthetic)")
SYNTH = ["executives", "analysts", "investors", "drivers", "shareholders", "engineers"]
kept = {"strict": 0, "ledger": 0}; n = 0
for r in rows:
    led = ins.get(r["instance"].replace("(repro)", ""), "")
    for a in SYNTH:
        # Ledger全体にも、そのissueにも同義語が存在しない主体語だけを対照にする
        if present(a, led) or present(a, r["issue"]): continue
        n += 1
        for mode in ("strict", "ledger"):
            ok, _ = ag1(r, mode, new_actors=[a])
            kept[mode] += (0 if ok else 1)
print("合成対照ケース数:", n, " 拒否維持 strict:", kept["strict"], " ledger:", kept["ledger"])
json.dump({"A": [{"run": t[0], "instance": t[1], "cycle": t[2], "level": t[3], "new_actors": t[4], "ag1_strict": t[5], "ag1_ledger": t[7]} for t in tab],
           "B": {"cases": n, "kept_strict": kept["strict"], "kept_ledger": kept["ledger"]}}, open(f"{OUT}/agg_actor_guard_ag_compare_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
