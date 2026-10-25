# ②B-light API 0 評価 (委任_07B)。事前登録=B_LIGHT_PREREGISTERED_01.md。保存済み転写のみ(socket guard)・LLM/ASR/TTS呼出0。
# Production比較基準は pin commit のtop-level *.pyスナップショット(07A並行編集の影響を受けない)。
# 再現: リポジトリrootで  PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_b_light_api0_01.py
#   → スナップショットを用意して自分自身を cwd=スナップショットで再実行し、標準出力と eval_b_light_api0_01.out.json を書く。決定的(タイムスタンプなし)。
import collections, hashlib, io, json, os, subprocess, sys, tarfile, tempfile

PIN = "89b630bd1086a638b2fec1f00d69bfae8722b665"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def ensure_snapshot() -> str:
    d = os.path.join(tempfile.gettempdir(), "blight_snap_" + PIN[:10])
    if not os.path.exists(os.path.join(d, "er007_ja_secondary_asr_01.py")):
        os.makedirs(d, exist_ok=True)
        data = subprocess.run(["git", "archive", PIN, ":(glob)*.py", ":(glob)*.json", ":(glob)*.txt"], cwd=REPO, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            t.extractall(d)
    return d


if os.environ.get("BLIGHT_INNER") != "1":
    snap = ensure_snapshot()
    env = dict(os.environ, BLIGHT_INNER="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.abspath(__file__)], cwd=snap, env=env)
    sys.exit(r.returncode)

# ---------------- inner (cwd = Production snapshot) ----------------
sys.path.insert(0, HERE)
sys.path.insert(0, ".")
import eval_common_02 as E
import proto_value_gate_fix_04 as F4
import b_light_proto_01 as B
import n1_pairs_01 as N1
import er078_asr_value_guard_01 as vg

assert os.path.abspath(".").lower() == os.path.abspath(os.path.join(tempfile.gettempdir(), "blight_snap_" + PIN[:10])).lower()
assert not hasattr(vg, "value_guard_kana_unified"), "snapshot must be pre-F2 Production"

E.api0_guard_on()
PASSING = E.uj.PASSING_STATES
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
AZ_COST = 0.2667   # 5.96s の月題titleの実測見積(usage記録)。1回あたり円
out = {"pin": PIN, "proto_sha256": hashlib.sha256(open(B.__file__, "rb").read()).hexdigest()}
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); lines.append(s)


def stage(canon, ptext, mode):
    if mode == "base":
        return E.primary_stage(canon, ptext, False)
    if mode == "v2":
        return E.primary_stage(canon, ptext, True)
    if mode == "F":
        with F4.apply_in_process():
            return E.primary_stage(canon, ptext, True)
    raise ValueError(mode)


ELIG = ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch", "secondary_not_accepted")


def final(canon, ptext, stext, mode):
    """mode in base/v2/F/B。戻り: dict(pass, reason, kind)  kind='primary'|'secondary'|'composite'|'ng'"""
    m = "F" if mode == "B" else mode
    st = stage(canon, ptext, m)
    if st["state"] in PASSING:
        return {"pass": True, "reason": st["reason"], "kind": "primary", "label": st["label"], "warn": sorted(st["warnings"])}
    reason = st["reason"] or ""
    res = {"pass": False, "reason": reason, "kind": "ng", "label": st["label"], "warn": []}
    if st["state"] == "NG_SECONDARY_UNAVAILABLE" and stext:      # P3到達=Secondaryを呼ぶ段。保存転写で許容集合を判定
        sb, a4a, a4b, _ = E.secondary_accept_kind(canon, stext)
        if sb or (m in ("v2", "F") and a4a):
            return {"pass": True, "reason": "secondary_accept", "kind": "secondary", "label": "SECONDARY", "warn": []}
        res["reason"] = "secondary_not_accepted"
    if mode == "B" and stext and any(res["reason"].startswith(e) for e in ELIG):
        r = B.composite_judge(canon, ptext, stext)
        res["composite"] = {"equal": r.equal, "why": r.why[:160], "blocked_by": r.blocked_by}
        if r.equal:
            return {"pass": True, "reason": "composite", "kind": "composite", "label": r.label, "warn": list(r.warnings),
                    "needs_new_azure_call": res["reason"] in ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch")}
    return res


def row(canon, ptext, stext, **extra):
    d = {"canon": canon, "primary": ptext, "secondary": stext}
    for m in ("base", "v2", "F", "B"):
        r = final(canon, ptext, stext, m)
        d[m] = {k: r[k] for k in ("pass", "reason", "kind") if k in r}
        if r.get("composite"):
            d[m]["composite"] = r["composite"]
        if m == "B" and r.get("needs_new_azure_call"):
            d["needs_new_azure_call"] = True
    d.update(extra)
    return d


def n_pass(rows, m):
    return sum(1 for r in rows if r[m]["pass"])


# ================= A. 月題 12転写 =================
log = [json.loads(l) for l in open(os.path.join(HERE, "phase3_run/usage_log.jsonl"), encoding="utf8")]
stored = {1: "月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。", 2: "月の死は八千九百本超。その奥に潜む岩の上着の秘密。",
          3: "月の氏は8000900本超。その奥に潜む岩の上着の秘密。"}
az = {}
for r in log:
    if r["stage"] in ("A1_azure_moon", "A3_azure_flip") and r["item"].startswith("japanese_title"):
        az[int(r["item"].split("attempt")[1][0])] = r["text"]
redraw = collections.defaultdict(list)
for r in log:
    if r["stage"] == "A2_openai_moon_x3":
        redraw[int(r["item"].split("attempt")[1][0])].append(r["text"])
moon = []
for k in (1, 2, 3):
    for tag, ptxt in [("stored", stored[k])] + [(f"redraw{i}", t) for i, t in enumerate(redraw[k])]:
        moon.append(row(MOON, ptxt, az[k], attempt=k, draw=tag))
out["moon"] = moon
P("== A. 月題(12転写: attempt1-3 x {保存転写+OpenAI再転写3}) ==")
for r in moon:
    P(f" a{r['attempt']} {r['draw']:8s} P={r['primary'][:20]:22s} base={int(r['base']['pass'])} v2={int(r['v2']['pass'])} F={int(r['F']['pass'])} "
      f"B={int(r['B']['pass'])} [{r['F']['reason'][:24]} -> {r['B'].get('composite', {}).get('blocked_by') or r['B']['kind']}]")
P(f" PASS数: base={n_pass(moon,'base')} v2={n_pass(moon,'v2')} F={n_pass(moon,'F')} B={n_pass(moon,'B')} / {len(moon)}")
for k in (1, 2, 3):
    rs = [r for r in moon if r["attempt"] == k]
    P(f"  attempt{k}: F={n_pass(rs,'F')}/{len(rs)} B={n_pass(rs,'B')}/{len(rs)} (安定救済=全転写PASS: F={n_pass(rs,'F')==len(rs)} B={n_pass(rs,'B')==len(rs)})")

# ================= B. N-3 30 clip =================
clips = {c["id"]: c for c in json.load(open(os.path.join(HERE, "n3_clips_01.json"), encoding="utf8"))}
n3 = []
for r in log:
    if r["stage"] == "N3_asr":
        c = clips[r["item"]]
        n3.append(row(c["canonical"], r["openai_text"], r["azure_text"], id=r["item"], type=c["type"], tts_input=c["tts_input"]))
out["n3"] = n3
P("== B. N-3 30 clip (実TTS→実OpenAI+実Azure。音声は意図的な誤読=正解は全てNG) ==")
P(f" PASS数(=誤PASS): base={n_pass(n3,'base')} v2={n_pass(n3,'v2')} F={n_pass(n3,'F')} B={n_pass(n3,'B')} / {len(n3)}")
inc_b = [r["id"] for r in n3 if r["B"]["pass"] and not r["F"]["pass"]]
inc_f = [r["id"] for r in n3 if r["F"]["pass"] and not r["base"]["pass"]]
P(" 基準1a 増分誤PASS(+F→+B):", inc_b, "/ (参考)+v2/+F が base に対し増えた:", inc_f)
P(" 基準2 回帰(+F PASS → +B NG):", [r["id"] for r in n3 if r["F"]["pass"] and not r["B"]["pass"]])
P(" 参考 composite が評価対象になった件:", [(r["id"], r["B"].get("composite", {}).get("blocked_by")) for r in n3 if r["B"].get("composite")])

# ================= C. Melos preview =================
p4 = json.load(open(os.path.join(HERE, "eval_api0_v1_01.out.json"), encoding="utf8"))["p4"]["flips"]
mel_a = [r for r in log if r["stage"] == "A3_azure_flip" and r["item"].startswith("preview")][0]["text"]
mc = [f for f in p4 if "preview_attempt2" in f["file"]][0]
melos = row(mc["canon"], mc["text"], mel_a, id="melos_preview_attempt2")
out["melos"] = melos
P("== C. Melos preview ==", melos["canon"][:30], "| P:", melos["primary"][:30], "| S:", mel_a[:30])
P(f" base={melos['base']} v2={melos['v2']['pass']} F={melos['F']['pass']} B={melos['B']['pass']} B.kind={melos['B']['kind']} composite={melos['B'].get('composite')}")
P(" 基準4 Melos副作用(+F と +B の判定が同一か):", melos["F"]["pass"] == melos["B"]["pass"] and melos["F"]["kind"] == melos["B"]["kind"])

# ================= D. 実Production履歴のP-S対 =================
pool = json.load(open(os.path.join(HERE, "ng_pool_cases_01.json"), encoding="utf8"))
hist, hist_skip = [], 0
for x in pool:
    if x.get("secondary") and x.get("primary") and x.get("canon"):
        hist.append(row(x["canon"], x["primary"], x["secondary"], file=x["file"], seg=x["seg"], prod_state=x.get("cls")))
    else:
        hist_skip += 1
out["hist"] = hist
P("== D. 実Production履歴のP-S対 (ng_pool_cases_01 Secondary記録あり) ==")
P(f" 対={len(hist)} / 評価不能(Secondary記録なし等)={hist_skip}")
P(f" PASS数: base={n_pass(hist,'base')} v2={n_pass(hist,'v2')} F={n_pass(hist,'F')} B={n_pass(hist,'B')}")
inc_h = [r for r in hist if r["B"]["pass"] and not r["F"]["pass"]]
P(" 基準1d composite による増分PASS(全件列挙):", len(inc_h))
for r in inc_h:
    P("   ", r["canon"][:40], "|", r["primary"][:40], "|", r["secondary"][:40])
P(" 基準2 回帰(+F PASS → +B NG):", [r["file"][-40:] for r in hist if r["F"]["pass"] and not r["B"]["pass"]])
P(" composite が評価対象になった件の内訳:", dict(collections.Counter(r["B"]["composite"]["blocked_by"] for r in hist if r["B"].get("composite"))))

# ================= E. N-1 150 最悪ケース露出 =================
n1 = N1.all_pairs()
expo, n1_stats = [], collections.Counter()
for p in n1:
    c, a = p["canon"], p["asr"]
    fr = final(c, a, c, "F")                       # Secondary=原稿そのもの(最悪)
    br = B.composite_judge(c, a, c)
    n1_stats["total"] += 1
    if br.equal and not fr["pass"]:
        expo.append({"id": p["id"], "type": p["type"], "canon": c, "asr": a, "F_reason": fr["reason"], "warn": list(br.warnings)})
    if br.equal:
        n1_stats["composite_equal_any"] += 1
out["n1_exposure"] = expo
P("== E. N-1 確定負例150 x 最悪ケース(Secondary=原稿そのもの) ==")
P(f" 対={len(n1)} / composite がPASS候補にした(+Fで既にPASSの件を含む)={n1_stats['composite_equal_any']} / うち +F がNGなのに composite がPASS(=露出)={len(expo)}")
for e in expo:
    P("   露出:", e["id"], e["type"], "|", e["canon"][:30], "|", e["asr"][:30], "|", e["F_reason"], e["warn"])
P(" 露出の型内訳:", dict(collections.Counter(e["type"] for e in expo)))

# ================= F. 合成負例マトリクス =================
S_OK = "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"   # 月題の実Azure転写(値は正しいが読みは原稿と違う)
TAIL = "。その奥に潜む岩の上着の秘密。"
vals = ["8,800", "89,000", "8,090", "9,900", "千九百", "八万九千", "8000800", "8000句800", "8万9千", "890"]
reads = ["すわ", "しば", "し", "巣は", "しわし"]
syn_rows = []   # (type, canon, primary, secondary)
for v in vals:
    p_v = f"月のしわ、{v}本超{TAIL}"
    syn_rows.append(("value_wrong:Primary(Secondary=原稿値)", MOON, p_v, S_OK))
    syn_rows.append(("value_wrong:Both(同じ値違い)", MOON, p_v, p_v))
    syn_rows.append(("value_wrong:Secondary_only", MOON, "月のしわ、8,900本超" + TAIL, p_v))
for rd in reads:
    for pv in ("8000900", "8,900", "8000九百"):
        syn_rows.append(("reading_wrong:Primary(Secondary=原稿値)", MOON, f"月の{rd}、{pv}本超{TAIL}", S_OK))
for c, p, s, t in [("三日待った", "3日待った。", "3日待った。", "irregular"), ("三日待った", "三日間待った。", "3日待った。", "irregular"),
                   ("二十歳になった", "20歳になった", "20歳になった", "irregular"), ("十月一日に会う", "10月1日に会う", "10月1日に会う", "irregular"),
                   ("三人は行かない", "3人は行く", "3人は行かない", "negation"), ("三人は行かない", "3人は行かない", "3人は行く", "negation"),
                   ("犬が三匹いる", "犬が三頭いる", "犬が三匹いる", "counter"), ("本を三冊買う", "本を三本買う", "本を3冊買う", "counter"),
                   ("売上は1,200円です", "売上は1,300円です", "売上は1,200円です", "value"), ("売上は1,200円です", "売上は12,000円です", "売上は1,200円です", "value")]:
    syn_rows.append((t, c, p, s))
syn_eval = []
for t, c, p, s in syn_rows:
    fr = final(c, p, s, "F")
    br = B.composite_judge(c, p, s)
    br_a = B.composite_judge(c, p, s, allow_explained_garble=False)
    syn_eval.append({"type": t, "canon": c, "primary": p, "secondary": s, "F_pass": fr["pass"], "composite": br.equal, "composite_alpha": br_a.equal,
                     "blocked_by": br.blocked_by, "incremental_pass": bool(br.equal and not fr["pass"])})
out["synthetic_negative"] = syn_eval
P("== F. 合成負例マトリクス(正解は全てNG) ==")
P(f" 件数={len(syn_eval)} / composite(β)がPASSにした={sum(1 for r in syn_eval if r['composite'])} / 案αがPASSにした={sum(1 for r in syn_eval if r['composite_alpha'])} "
  f"/ 増分誤PASS(+F NG→composite PASS)={sum(1 for r in syn_eval if r['incremental_pass'])}")
P(" 型別:", dict(collections.Counter((r["type"], r["composite"]) for r in syn_eval)))
for r in syn_eval:
    if r["composite"]:
        P("   composite PASS:", r["type"], "|", r["primary"][:40], "|", r["secondary"][:40])

# ---- 正例(合成。設計の対象型を示すだけ。実頻度の証拠ではない) ----
pos = [("売上は1,200円です", "売上は1000200円です", "売上は1200円です"), ("参加者は3,500人です", "参加者は3000五百人です", "参加者は3500人です"),
       ("価格は12,000円です", "価格は10000二千円です", "価格は12000円です"), ("価格は12,000円です", "価格は12,000円です", "価格は12000円です")]
pos_eval = []
for c, p, s in pos:
    br = B.composite_judge(c, p, s)
    pos_eval.append({"canon": c, "primary": p, "secondary": s, "composite": br.equal, "why": br.why[:80], "F_pass": final(c, p, s, "F")["pass"]})
out["synthetic_positive"] = pos_eval
P("== G. 合成の正例(設計対象型の動作確認のみ。実頻度の証拠ではない) ==")
for r in pos_eval:
    P("  ", r["canon"], "|", r["primary"], "|", r["secondary"], "| composite=", r["composite"], "| +F=", r["F_pass"], r["why"])

# ================= H. 追加Azure呼出の見積・評価不能 =================
needs = [r for grp in (moon, n3, hist) for r in grp if r.get("needs_new_azure_call")]
P("== H. 追加Azure呼出 / 評価不能 ==")
P(f" composite が新たにAzure呼出を要した対(現行はP1/最終ゲートでAzure不呼出)={len(needs)} (見積 {len(needs)*AZ_COST:.2f}円/評価母集団ぶん)")
att = json.load(open(os.path.join(HERE, "attempt_pool_01.json"), encoding="utf8"))
unk = json.load(open(os.path.join(HERE, "unknown_pool_02.json"), encoding="utf8"))
P(f" 評価不能: P-4 実attempt={len(att)} 件(うちSecondary記録あり={sum(1 for x in att if x.get('secondary'))})、未知データ(Primary転写のみ)={len(unk)} 件、N-1=150 対(音声・Secondary実転写なし=最悪ケース被覆のみ)")

# ================= 判定(事前登録の機械写像) =================
c1a = len(inc_b) == 0
c1b_types = collections.Counter(e["type"] for e in expo)
c1b = all(("garble" in t or "断片" in t) for t in c1b_types)       # 型内のみ許容(値garble型)
c1c = sum(1 for r in syn_eval if r["incremental_pass"]) == 0
c1d_listed = len(inc_h)
c2 = (not [r for r in n3 if r["F"]["pass"] and not r["B"]["pass"]] and not [r for r in moon if r["F"]["pass"] and not r["B"]["pass"]]
      and not [r for r in hist if r["F"]["pass"] and not r["B"]["pass"]] and melos["F"]["pass"] <= melos["B"]["pass"])
c4 = melos["F"]["pass"] == melos["B"]["pass"] and melos["F"]["kind"] == melos["B"]["kind"]
moon_inc = n_pass(moon, "B") - n_pass(moon, "F")
P("== 事前登録基準の機械判定 ==")
P(f" 1a N-3増分誤PASS=0: {c1a} | 1b N-1露出が値garble型のみ: {c1b} (型={dict(c1b_types)}) | 1c 合成負例増分誤PASS=0: {c1c} | 1d 履歴対の増分PASS件数(要個別審査)={c1d_listed}")
P(f" 2 回帰0: {c2} | 4 Melos副作用0: {c4} | 3 月題の増分(+F→+B)={moon_inc}")
status = "REJECTED" if not (c1a and c1b and c1c and c2 and c4) else ("VALIDATED(限定)候補" if moon_inc >= 1 else "NOT_EFFECTIVE")
P(" Status候補(機械写像。1dの個別審査結果は別途。最終はFable):", status)
out["verdict"] = {"c1a": c1a, "c1b": c1b, "c1b_types": dict(c1b_types), "c1c": c1c, "c1d_listed": c1d_listed, "c2": c2, "c4": c4,
                  "moon_increment": moon_inc, "status_candidate": status}
E.api0_guard_off()
json.dump(out, open(os.path.join(HERE, "eval_b_light_api0_01.out.json"), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1, sort_keys=True, default=str)
open(os.path.join(HERE, "eval_b_light_api0_01.out.txt"), "w", encoding="utf8", newline="\n").write("\n".join(lines) + "\n")
