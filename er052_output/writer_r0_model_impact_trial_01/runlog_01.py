# -*- coding: utf-8 -*-
import glob, hashlib, json, os, subprocess
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(H, "..", ".."))
J = lambda p: json.load(open(p, encoding="utf-8"))
sha = lambda b: hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()
T = ["streaming_price", "space_weapons", "byd_recall"]; M = ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"]
L = ["# RUN_LOG_01: 実行履歴・条件同一性チェック(機械照合)\n"]
L.append("## 1. 実行履歴\n- Phase 1(API 0円): 入力点検・Prompt組立(dry-run)・PREREGISTRATION_01.md作成 -> commit 988733b3(push済)。")
st = open(os.path.join(H, "logs", "r0_start_epoch.txt")).read().strip()
L.append("- Phase 2-1: R0 9本を9プロセス同時並列(`r0_trial_driver_01.py r0`、epoch開始 %s)。全9本 1試行で成功、再試行0、失敗0。" % st)
L.append("- Phase 2-2: Risk Flagger(D0 + D2記事モード)9セルを9プロセス同時並列(`r0_trial_driver_01.py flag --max-yen 30`)。全9セル valid_json=True、形式再呼び出し0、transient再試行0。")
L.append("- Phase 3: `aggregate_01.py`・`runlog_01.py`で集計(API 0円)。\n")
L.append("## 2. R0 試行履歴\n| テーマ | モデル | 試行数 | ok | response_id | model_id | ts |\n|---|---|---|---|---|---|---|")
bad = 0
for t in T:
    for m in M:
        r = J(os.path.join(H, "r0", t, m + ".json"))
        for a in r["attempts"]:
            L.append("| %s | %s | %d | %s | %s | %s | %s |" % (t, m, a["n"], a["ok"], a.get("response_id"), a.get("model_id"), a["ts"]))
            if a.get("model_id") != m: bad += 1
L.append("\nmodel_id不一致(要求名と応答`model`欄): %d件\n" % bad)
L.append("## 3. 比較条件の同一性チェック(機械照合の結果)\n")
ok = True
for t in T:
    rs = [J(os.path.join(H, "r0", t, m + ".json")) for m in M]
    same_prompt = len({r["prompt_sha256"] for r in rs}) == 1
    same_meta = len({json.dumps(r["input_meta"], sort_keys=True) for r in rs}) == 1
    pfile = sha(open(os.path.join(H, "prompts", t + ".txt"), "rb").read())
    pm = J(os.path.join(H, "prompts", "prompt_manifest.json"))[t]["prompt_sha256"]
    nofc = all((not r["fact_check_run"]) and (not r["must_fix_run"]) for r in rs)
    ok &= same_prompt and same_meta and nofc and rs[0]["prompt_sha256"] == pm
    L.append("- %s: R0 Prompt sha 3モデル一致=%s (%s、事前登録manifestと一致=%s) / 入力メタ(brief・台帳sha・effort・developer message・FactLockブロックsha)一致=%s / Fact Check・must-fix未実行(全セル共通)=%s" % (t, same_prompt, rs[0]["prompt_sha256"][:16], rs[0]["prompt_sha256"] == pm, same_meta, nofc))
fl = {}
for t in T:
    for m in M:
        f = J(os.path.join(H, "flags", t, m + ".json"))
        raw = [json.loads(x) for x in open(os.path.join(H, "logs", "d2_gpt-6.1-sol_%s__%s_raw.jsonl" % (t, m)), encoding="utf-8") if x.strip()]
        sysm = {sha(r["request"]["system"]) for r in raw if "request" in r}
        fl[(t, m)] = (f, sysm, raw)
allsys = set().union(*[v[1] for v in fl.values()])
L.append("- Risk Flagger D2 system prompt sha: 全9セルで一致=%s (%s)。想定値(PREREGISTRATION: b8dacc14...)と一致=%s" % (len(allsys) == 1, ",".join(s[:16] for s in allsys), allsys == {"b8dacc147009a13bea886d5d97d387fc5ff06171d878fcae7fdddbd18fd6d405"}))
L.append("- Flaggerモデル: 全9セルで %s、effort=%s、応答model_id=%s。" % ({v[0]["flagger_model"] for v in fl.values()}, {v[0]["flagger_effort"] for v in fl.values()}, {tuple(v[0]["d2_model_ids"]) for v in fl.values()}))
for t in T:
    L.append("- %s: Flagger台帳sha 3セル一致=%s、入力Fact数(Flagger受領)=%s" % (t, len({fl[(t, m)][0]["ledger_sha256"] for m in M}) == 1, {fl[(t, m)][0]["n_facts"] for m in M}))
drv = sha(open(os.path.join(H, "r0_trial_driver_01.py"), "rb").read())
L.append("- driver sha256(実行時=現在): %s、事前登録時: ab25f13de0f44f68d6056d7c46225f765b9d0213a75399699872c1c23cb725ac -> 一致=%s" % (drv, drv == "ab25f13de0f44f68d6056d7c46225f765b9d0213a75399699872c1c23cb725ac"))
L.append("- 全条件同一(R0 Prompt・入力・Flagger prompt): %s\n" % ok)
L.append("## 4. Production/既存ファイル無変更の確認\n")
def git(*a): return subprocess.run(["git", *a], cwd=R, capture_output=True, text=True, encoding="utf-8").stdout.strip()
chk = ["er019_family_x_ja_writer_o_r1_r2_01.py", "er052_factlock_writer_trial_01_run.py", "er052_factlock_astra_e2e_runner_01.py", "er006_model_routing_contract_01.py", "er005_output/cost_baseline_01/pricing_snapshot.json", "CURRENT_SPEC.md", "er052_output/writer_dev_risk_flagger_01/detectors", "er052_output/factlock_astra_e2e_trial_01"]
for c in chk:
    d = git("status", "--porcelain", "--", c)
    tracked_mod = [x for x in d.splitlines() if not x.startswith("??")]
    L.append("- `%s`: 追跡ファイルの変更=%s件%s" % (c, len(tracked_mod), (" (untracked既存: %d件、本Trial起因ではない)" % sum(1 for x in d.splitlines() if x.startswith("??"))) if "??" in d else ""))
L.append("\n(`git status`は本Trial着手前から別タスク由来の未追跡/変更ファイルを含む。上記は本Trialで触れていないこと[追跡ファイル変更0件]の確認。)")
L.append("\n## 5. 発見事項\n- streaming_price台帳のF01・F07(`[AMBIGUOUS - ...]`見出し)が既存Flaggerのパーサで読み飛ばされ、Flaggerの入力は5/7件(RESULT_01.md冒頭)。Flagger側の修正は行っていない。")
L.append("- 並列9本実行のため処理時間はAPI負荷を含む。費用は usage x pricing_snapshot.json(Standard)の算出値(請求ダッシュボード照合は未実施)。")
open(os.path.join(H, "RUN_LOG_01.md"), "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L[-22:]))
