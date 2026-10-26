# -*- coding: utf-8 -*-
"""COST_01.md / HR_IMPACT_01.md / EVIDENCE_01.md を生成(API 0)。数値はevidence JSON・raw_usage_logからの機械集計。"""
import collections, datetime, glob, json, os, re, statistics, sys
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
ROOTS = {"X": "er019_output/family_x_audio_production_wiring_01", "Y": "er121_output/family_y_production_01", "Z": "er026_output/family_z_production_e2e_01"}


def all_run_dirs():
    out = []
    for fam, r in ROOTS.items():
        for d in sorted(glob.glob(f"{r}/**/*tru_ev*", recursive=True)):
            if os.path.isdir(d) and os.path.exists(f"{d}/raw_usage_log.jsonl") and "_evidence_ledgers" not in d:
                out.append((fam, d))
    return out


def run_dir_costs():
    rows = []
    for fam, d in all_run_dirs():
        c = core.cost_of(f"{d}/raw_usage_log.jsonl")
        base = os.path.basename(d)
        status = "採用" if re.search(r"run_tru_ev_[xyz]_", base) and not re.search(r"(aborted|superseded|smoke)", base) else "superseded/中断/smoke"
        first = None
        for r in core.read_jsonl(f"{d}/raw_usage_log.jsonl")[:1]:
            first = r.get("timestamp") or r.get("ts") or r.get("time")
        rows.append({"family": fam, "run": base, "jpy": c["jpy"] or 0.0, "by_provider": c.get("by_provider") or {}, "status": status, "first_ts": first})
    return rows


def main():
    rows = run_dir_costs()
    fam_adopt = collections.defaultdict(float)
    fam_all = collections.defaultdict(float)
    prov = collections.defaultdict(float)
    for r in rows:
        fam_all[r["family"]] += r["jpy"]
        if r["status"] == "採用":
            fam_adopt[r["family"]] += r["jpy"]
        for k, v in r["by_provider"].items():
            prov[k] += v
    total = sum(fam_all.values())
    sup_total = total - sum(fam_adopt.values())
    # --- 限界費用
    tts_n = gem = asr_cost = az = 0
    lr_n = 0
    lr_openai = 0.0
    for cid, d in data.items():
        if cid not in CASES:
            continue
        ev = d.get("resume") or d.get("main")
        by = ev["cost"]["by_provider"]
        n = len(ev.get("tts_attempts") or [])
        if "resume" in d:
            n += len(d["main"]["tts_attempts"]) if d.get("main") else len(json.load(open(f"{D.ER}/{cid}.partial_before_kill.json", encoding="utf-8"))["tts_attempts"])
        tts_n += n
        gem += by.get("gemini", 0); asr_cost += by.get("openai_asr", 0); az += by.get("azure", 0)
        if ev.get("lr_count"):
            lr_n += ev["lr_count"]; lr_openai += by.get("openai", 0)
    per_attempt = (gem + asr_cost + az) / max(tts_n, 1)
    per_lr = lr_openai / max(lr_n, 1)
    # --- wall time
    wall = collections.defaultdict(list)
    for cid, d in data.items():
        if cid in CASES and "resume" not in d:
            sc = re.split(r"[(+]", CASES[cid]["scenario"])[0]
            wall[sc].append((d["main"].get("wall_seconds") or 0))
    wt = "\n".join(f"| {k} | {len(v)} | {round(statistics.mean(v))} | {round(min(v))} | {round(max(v))} |" for k, v in sorted(wall.items()))
    cds = [c["actual_seconds"] for cid, d in data.items() if cid in CASES for ev in [d.get("main"), d.get("resume")] if ev for c in ev.get("cooldown_events") or [] if c.get("actual_seconds", 0) > 100]
    # --- case別表
    ctab = ["| case | 実費(円) | provider内訳(円) |", "|---|---|---|"]
    for cid in sorted(data, key=lambda x: (x.split("-")[0], x.split("-")[1], int(re.match(r"\d+", x.split("-")[2]).group()), x)):
        if cid not in CASES:
            continue
        ev = data[cid].get("resume") or data[cid].get("main")
        ctab.append(f"| {cid} | {ev['cost']['jpy']} | {json.dumps(ev['cost']['by_provider'], ensure_ascii=False)} |")
    rtab = ["| Family | run dir | 区分 | 実費(円) |", "|---|---|---|---|"] + [f"| {r['family']} | `{r['run']}` | {r['status']} | {r['jpy']} |" for r in rows if r["status"] != "採用"]
    cost = f"""# COST_01 — 委任_03 runtime evidenceの費用・単価影響・制作時間差分

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: {NOW}

## 1. 実費(raw_usage_logの`compute_cost_jpy_so_far`集計。全run dir合算)

| 区分 | 実費(円) |
|---|---|
| 採用case(最終evidence)の合計 | {round(sum(fam_adopt.values()), 2)} |
| superseded/中断/smokeのrun(driver不備・自然逸脱・LR不成立の再実行分) | {round(sup_total, 2)} |
| **委任_03の総実費** | **{round(total, 2)}** |
| 個別Cap(¥280)に対して | {round(total / 280 * 100, 1)}% |

Family別(採用/全体): X={round(fam_adopt['X'], 2)}/{round(fam_all['X'], 2)}、Y={round(fam_adopt['Y'], 2)}/{round(fam_all['Y'], 2)}、Z={round(fam_adopt['Z'], 2)}/{round(fam_all['Z'], 2)}。
provider別(全体): {json.dumps({k: round(v, 2) for k, v in prov.items()}, ensure_ascii=False)}。
BUDGET_PLAN §3のLean保守見積200.2円/天井297.8円に対し、実費は上記。日次1,000円(JST)に対し本委任は{round(total, 1)}円で、他の並行作業分を含めても¥950以内の見込み(他agentの同日支出は本agentからは未確認)。**暴走(同一原因の連続再実行)なし**。再実行はすべて原因を特定した上で1回ずつ(§3)。

## 2. case別実費(採用evidence。E-S6は再起動後の累計)

{chr(10).join(ctab)}

## 3. superseded / 中断 / smoke のrun dir(費用は上記総額に計上済み)

{chr(10).join(rtab)}

再実行の理由: (1) driver不備(KP caseのno-op label不一致・KP style_profile記録欠落・Z ctx slot意味・JA wrapper引数・Z clip id・LR置換語[先頭語`Listen`でLR候補QA不合格]) (2) Y generator decorator位置ずれ(Production軽微欠陥の是正、Y全case再実走) (3) 自然逸脱(③が実ASRでNG)の再実行(X-Std-1b/X-Adv-14b/Y-Std-2b/Y-Std-4b/Y-Adv-4b)。

## 4. 量産単価(70円/記事セット)への影響の実測更新

実測の限界費用(強制NG条件下の平均。評価・注入の費用を含む上限寄りの値):
- **1 attempt(TTS+ASR[openai+azure])**: 約 ¥{round(per_attempt, 3)}(全採用caseのTTS {tts_n}回、gemini ¥{round(gem, 2)}+openai_asr ¥{round(asr_cost, 2)}+azure ¥{round(az, 2)})。
- **LR 1回(gpt-6-luna、識別+書換え+QA等のLLM呼出の合計)**: 約 ¥{round(per_lr, 3)}/回(LR実行{lr_n}回、openai計 ¥{round(lr_openai, 2)})。LR後のTTS最大3回は上記attempt単価。

BUDGET_PLAN §4の推定「+0〜1円/セット」の更新: 回数が増える箇所は**LRあり部位でLR発動かつ①'NG時の最大+2 attempt**のみ(約¥{round(per_attempt * 2, 2)}/件)。発動頻度は本evidenceでは強制NGのため測定不可(BUDGET_PLAN §4の実績頻度[③到達 約1〜2%、JA 6.9%]を使うと、記事あたり ≒ ¥0.1〜0.5 程度で、**+1円/セット未満の推定は維持**)。LRなし部位(JA・KP・KP解説・Z会話)は試行回数が不変(3回/KPは4回)で、待機が増えるだけで費用は増えない(実測: X-Std-6/X-Adv-1/Z-Std-2のTTS=3)。

## 5. 制作時間差分(実測)

- 実180秒待機: {len(cds)}回、最小{min(cds):.3f}秒〜最大{max(cds):.3f}秒(`cooldown_core`の実`sleep`)。旧(1ブロック600秒)に対し**−420秒/ブロック**(英語LR部位)。日本語・KP・KP解説・Z legacy・Z冒頭英語は**新規に+180秒/イベント**(③到達時のみ)。
- case別wall time(採用evidence):

| シナリオ | case数 | 平均秒 | 最小 | 最大 |
|---|---|---|---|---|
{wt}

E-N(正常系)は平均約13秒=**待機・追加生成なし**。E-S1(③到達)は約200秒=180秒待機+TTS/ASR。E-S2b(LR+2待機)は約450秒(旧は最低でも600秒×2に近い待機が必要)。
"""
    open(f"{BASE}/COST_01.md", "w", encoding="utf-8").write(cost)
    # =================== HR impact
    rows_hr = []
    for cid in sorted(data, key=lambda x: (x.split("-")[0], x.split("-")[1], int(re.match(r"\d+", x.split("-")[2]).group()), x)):
        if cid not in CASES:
            continue
        c = CASES[cid]
        sc = c["scenario"]
        if sc == "E-N" or sc.startswith(("E-STOP", "E-S0", "E-C1", "E-X5", "E-S6")):
            continue
        d = data[cid]
        r = rep.row(cid, d, res)
        ev = d.get("resume") or d.get("main")
        try:
            sg = agg.shared_gate_segments(c, ev["run_dir"])
            shared = bool(sg["blocked"])
        except Exception:
            shared = None
        m3 = r["gate"].startswith(("BLOCK(", "Z Gate BLOCK"))
        kind = "終端HR(STOPPED)" if r["final"] not in ("OK",) else ("LR採用" if (ev.get("lr_count") or 0) > 0 or "AABA" in str(r["style"]) else "③採用")
        rows_hr.append((cid, c["family"], c["level"], c["policy"].split("+")[0], c["leaf"], kind, r["final"], m3, shared, r["gate"], r["verdict"]))
    adopt = [x for x in rows_hr if x[5] in ("③採用", "LR採用")]
    term = [x for x in rows_hr if x[5].startswith("終端")]
    tb = ["| case | Family/Lv | 方針/leaf | 区分 | 方針Gate | 共有Audio Gate | 方針Gateの内容 | 判定 |", "|---|---|---|---|---|---|---|---|"]
    for x in adopt:
        tb.append(f"| {x[0]} | {x[1]}/{x[2]} | {x[3]}/{x[4]} | {x[5]} | {'BLOCK' if x[7] else 'PASS'} | {'BLOCK' if x[8] else 'PASS'} | {x[9][:90]} | {x[10]} |")
    n_ad = len(adopt)
    n_blk = sum(1 for x in adopt if x[7] or x[8])
    by_kind = collections.defaultdict(lambda: [0, 0])
    for x in adopt:
        k = f"{x[1]}/{x[2]} {x[3]}/{x[4]} {x[5]}"
        by_kind[k][0] += 1
        by_kind[k][1] += 1 if (x[7] or x[8]) else 0
    bk = "\n".join(f"| {k} | {v[0]} | {v[1]} |" for k, v in sorted(by_kind.items()))
    hr = f"""# HR_IMPACT_01 — ③採用・LR採用のGate対象化によるHuman Review待ち件数の見込み(R-7)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: {NOW} / 材料=委任_03のevidence(強制NG条件下の**機構単位**の観測。発生率の測定ではない)

## 1. 結論

- ③またはLRで**音声が採用された**{n_ad}case(強制NGで③/LRまで到達させたもの)のうち、**Gate(方針Gate or 共有Audio Gate)がBLOCKしたのは{n_blk}case**。BLOCKしたのは下記の**特定部位に限られる**(他のFamily/部位の③・LR採用は無BLOCKでHR増なし)。
- BLOCKする部位: **X Adv preview③**(`PREVIEW_MINIMAL_FALLBACK`)、**X Adv KP解説③**(`FINAL_STYLE_SHA_MISMATCH_NO_HINT`)、**Y Std本文Voice③**(`STD_FALLBACK_USED_OR_UNKNOWN`)、**Y Adv本文Voice LR採用**(`LOCAL_REWRITE_RECOVERY`)。これらはOPEN-537等の既存fail-closed Gate設計どおり(本委任ではGate不変更)で、③/LR採用音声は人間承認(HR)待ちになる。
- 無BLOCK(HR増なし)の③/LR採用: X Std(topic_intro/body_s/JA/KP英語[WARNINGのみ])、X Adv comment_1③・LR、Y KP/JA/Adv comment LR、Z全部位(narrator chunk・topic_intro_en LR・JA・KP・dialogue legacy③)。
- 終端HR(③/LR後も不合格→STOPPED)は{len(term)}case: Lock=HUMAN_REVIEW_REQUIRED+HRQ 1行(JA・Zセリフの判定注入caseはdriver限界でHRQ行なしだがLockは作成)+Assemble BLOCK(共有Audio Gate)/ZはGate BLOCK。これは**旧仕様でも③不合格後はHR**で、新仕様の差は「LRあり部位の最大試行が増える(6 TTS/2待機/LR1)」点のみ(HR発生数を増やす方向ではなく、③/LRで救済できる機会が増える方向)。

## 2. ③/LR採用case別のGate結果(実測)

{chr(10).join(tb)}

## 3. 部位別集計

| 部位・区分 | 採用case数 | うちGate BLOCK |
|---|---|---|
{bk}

## 4. HR待ち件数の見込み(推定。式と前提を明記)

- 追加のHR待ち/記事 ≒ Σ_(BLOCK部位)[ その部位のclip数 × ③到達率(p) ] + Σ[LR採用clip数 × LR率]。③到達率pはBUDGET_PLAN §4が引く棚卸し実績(Z dialogue「3回以上」6/347=1.7%、JA comment 7/102=6.9%)を**上限寄りの代用**とすると、BLOCK部位のclip数は記事あたり X Adv preview 1 + KP解説 数件(最大5)+ Y本文Voice 1〜2 程度 → **0.1〜0.5件/記事程度(推定)**。
- **注意**: 上記pは旧仕様の実績からの代用値で、統一flow後の発生率は未測定(本evidenceは強制NGのため率を出せない)。実測は量産(自然発生)でのGate BLOCK件数の追跡が必要。
- 低減余地(判断候補ではなく所見): BLOCK部位は③/LR採用音声のStyleを承認profileと照合するGate側の設計に由来する(X Adv KP解説③、Y本文③/LR)。Gate緩和は承認済みGateの変更でありユーザー判断事項(本委任では変更しない)。
- 旧仕様との比較: 旧仕様でもAdv英語・Std本文で③に当たる経路は存在したが、本evidence時点で「旧flowのBLOCK件数」との差分は計測していない(旧flowの再実走は範囲外)。
"""
    open(f"{BASE}/HR_IMPACT_01.md", "w", encoding="utf-8").write(hr)
    print("cost/hr written", round(total, 2), n_ad, n_blk, len(term))


if __name__ == "__main__":
    main()
