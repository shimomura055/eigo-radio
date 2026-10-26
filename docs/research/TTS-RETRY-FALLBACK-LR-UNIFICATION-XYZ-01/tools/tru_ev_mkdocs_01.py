# -*- coding: utf-8 -*-
"""EVIDENCE_{X,Y,Z}_01 / EVIDENCE_01 / COST_01 / HR_IMPACT_01 を生成する(API 0。evidence JSONからの機械集計+固定の解説文)。"""
import glob, json, os, re, sys, collections, statistics, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ROOT = os.path.abspath(f"{BASE}/../../..")
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
os.chdir(ROOT)
import tru_ev_aggregate_01 as agg
import tru_ev_report_01 as rep
import tru_ev_docs_01 as D
import tru_ev_core_01 as core

data, res = D.load()
CASES = agg.CASES
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M JST")


def verdict_counts(fam):
    c = collections.Counter()
    for cid in data:
        if cid in CASES and CASES[cid]["family"] == fam:
            c[res[cid]["verdict"]] += 1
    return dict(c)


def scen_matrix(fam):
    """policy × シナリオ種別 → case一覧(判定付き)。"""
    m = collections.defaultdict(lambda: collections.defaultdict(list))
    for cid in data:
        if cid in CASES and CASES[cid]["family"] == fam:
            c = CASES[cid]
            sc = re.split(r"[(+]", c["scenario"])[0]
            m[c["policy"].split("+")[0] + "/" + c["level"]][sc].append(f"{cid}[{res[cid]['verdict'][:4]}]")
    return m


SC_ORDER = ["E-N", "E-S0", "E-S1", "E-S2a", "E-S2b", "E-S3", "E-S4", "E-S6", "E-S7", "E-STOP", "E-C1", "E-X5"]


def matrix_table(fam):
    m = scen_matrix(fam)
    cols = [s for s in SC_ORDER if any(s in v for v in m.values())]
    out = ["| 方針/Lv | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for pol in sorted(m):
        out.append(f"| {pol} | " + " | ".join(", ".join(m[pol].get(s, [])) or "未観測" for s in cols) + " |")
    return "\n".join(out)


def model_table(fam):
    mu = collections.Counter()
    for cid, d in data.items():
        if cid in CASES and CASES[cid]["family"] == fam:
            rd = (d.get("resume") or d.get("main"))["run_dir"]
            for m in agg.model_usage(rd):
                mu[(m["provider"], m["model_id"], m["api"])] += m["calls"]
    out = ["| provider | model_id(実測) | API | 呼出回数 |", "|---|---|---|---|"]
    for k, v in sorted(mu.items(), key=lambda kv: str(kv[0])):
        out.append(f"| {k[0]} | {k[1]} | {k[2]} | {v} |")
    return "\n".join(out)


HEAD = """管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: {now} / API実費を伴う実走evidence(実TTS・実ASR・実180秒待機・実LR[gpt-6-luna]・実Gate)

## 方式(全Family共通)

- driver: `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_run_01.py`(+`tru_ev_core_01.py`/`tru_ev_cases_01.py`/`tru_ev_aggregate_01.py`)。**正式のleaf生成関数・scope(`er109 run_scope`/`with_secondary_run`/`guarded_generate`)を直接呼ぶ**。実TTS・実ASR・実180秒`time.sleep`(`cooldown_core`)・実LR・実Gateは本物のまま。
- 強制NG: driver側monkeypatchで**判定結果のNG方向にだけ**上書き(Style・Prompt・Voice・速度・model・待機・回数・Gateは触らない)。上書きは`injected_override_count`と`injected_overrides[]`に全件記録。LR経路はPrimary転写の1語置換(NG方向のみ)で`identify_ng_span`を成立させた。正常系(E-N)は上書き0をassert。
- 環境: `TTS_EXECUTION_MODE=STANDARD`を環境変数とCLI引数の両方で明示。`TTS_BACKEND=speech_metadata_flash_lite` / `STYLE_PROFILE=fx_20261017`(X/Y/Z共通の承認済み)。
- 各case開始前に`tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01`を実行(63ファイル`stop_check_*.json`、いずれもrc=3[停止]でない)。STOP/STOP_ALLは作成・削除していない(E-STOPはrun専用sentinel `<run>/STOP`のみ)。
- 強制NG由来のHRQ行・attempt_history・Master Audio Store・telemetryは各run dirの`_evidence_ledgers/`へ隔離(本番台帳を汚さない)。evidence専用・対応不要・開発費。
- 判定: `_aggregate_01.json`(case別の機械判定[check名・期待・実測])。PASS=期待どおり/DEVIATION_NATURAL=③等で本物のASRが自然にNGになり期待と異なる経路(フロー自体の検査は通過)/FAIL=不整合。
- 表の読み方: TTS=対象clipの実TTS回数、待機=実測秒(`+`区切り、E-S6はkill前+再開後)、Style列=attempt毎のStyle種別(A=元Style、B=Fallback Style、`[..]`=該当ラベル)、方針Gate=M3(X)/Y Style Gate/Z該当/Gate(当該segmentのみ。未生成の他segmentのNO_SEGMENT_RECORDは対象外)、共有Audio Gate=`asm._segment_gate_status`等のper-segment関数を当該segmentにだけ適用(API 0)。
"""


def write_family(fam, name, notes):
    tbl = D.family_table(fam, data, res)
    vc = verdict_counts(fam)
    txt = f"# EVIDENCE_{fam}_01 — Family {fam} runtime evidence(委任_03)\n\n" + HEAD.format(now=NOW)
    txt += f"\n## {fam}の判定集計\n\n" + ", ".join(f"{k}={v}" for k, v in sorted(vc.items())) + f"(case数={sum(vc.values())}。supersededは含まない)\n"
    txt += f"\n## 方針×シナリオの観測マトリクス({fam})\n\n未観測=本委任で実走していない(Lean計画で除外/代表で固定)。\n\n" + matrix_table(fam) + "\n"
    txt += f"\n## case別観測表({fam})\n\n" + tbl + "\n"
    txt += f"\n## 実測モデル(raw_usage_log。{fam}のrun dir合算)\n\n" + model_table(fam) + "\n"
    txt += notes
    open(f"{BASE}/EVIDENCE_{fam}_01.md", "w", encoding="utf-8").write(txt)


if __name__ == "__main__":
    notes = {}
    exec(open(f"{HERE}/tru_ev_notes_01.py", encoding="utf-8").read())
    for fam in "XYZ":
        write_family(fam, fam, notes[fam])
    print("ok")
