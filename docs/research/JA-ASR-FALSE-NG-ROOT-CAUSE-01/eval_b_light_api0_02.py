# ②B-light API 0 評価 v2 (委任_08、Opus M-1是正)。事前登録=B_LIGHT_PREREGISTERED_02.md。保存済み転写のみ(socket guard)・LLM/ASR/TTS呼出0。
# 比較基準列(M-1是正): base / base+F1F2(=07A適用後Productionの代表。proto v4 apply_in_process、v2のPrimary層・A4(a)を含まない) /
#   base+F1F2+β / (参考)base+v2+F1F2 / (参考)base+v2+F1F2+β / (参考)β読みstrict / (参考)β secondary_reading_conflict=veto。
# Production比較基準は pin commit のtop-level *.pyスナップショット(07A並行編集の影響を受けない)。07A commit後は BLIGHT_PROD07A で再現一致確認を別途行う。
# 再現: リポジトリrootで  PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_b_light_api0_02.py
#   → 自分自身を cwd=スナップショットで再実行し、標準出力と eval_b_light_api0_02.out.json/.out.txt を書く。決定的(タイムスタンプなし)。
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
    g = subprocess.run(["git", "grep", "-q", "value_guard_kana_unified", "HEAD", "--", "er078_asr_value_guard_01.py"], cwd=REPO)
    env = dict(os.environ, BLIGHT_INNER="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8", BLIGHT_PROD07A="1" if g.returncode == 0 else "0")
    r = subprocess.run([sys.executable, os.path.abspath(__file__)], cwd=snap, env=env)
    sys.exit(r.returncode)

# ---------------- inner (cwd = Production snapshot) ----------------
sys.path.insert(0, HERE)
sys.path.insert(0, ".")
import eval_common_02 as E
import proto_value_gate_fix_04 as F4
import b_light_proto_02 as B
import n1_pairs_01 as N1
import er078_asr_value_guard_01 as vg

assert os.path.abspath(".").lower() == os.path.abspath(os.path.join(tempfile.gettempdir(), "blight_snap_" + PIN[:10])).lower()
assert not hasattr(vg, "value_guard_kana_unified"), "snapshot must be pre-F2 Production"

E.api0_guard_on()
PASSING = E.uj.PASSING_STATES
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
AZ_COST = 0.2667
META = {"engine": "azure", "wav_sha256": "eval-stored-transcript", "model_id": "eval-stored"}     # 保存転写評価用(実Azure呼出なし)
out = {"pin": PIN, "proto_sha256": hashlib.sha256(open(B.__file__, "rb").read()).hexdigest(), "prod07a_committed_at_eval": os.environ.get("BLIGHT_PROD07A") == "1"}
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); lines.append(s)


_cache = {}


def stage(canon, ptext, mode):
    k = (canon, ptext, mode)
    if k not in _cache:
        if mode == "base":
            _cache[k] = E.primary_stage(canon, ptext, False)
        elif mode == "F12":                       # base + F1F2 (07A後Productionの代表。v2層なし)
            with F4.apply_in_process():
                _cache[k] = E.primary_stage(canon, ptext, False)
        elif mode == "v2F12":                     # (参考) base + v2 + F1F2
            with F4.apply_in_process():
                _cache[k] = E.primary_stage(canon, ptext, True)
        else:
            raise ValueError(mode)
    return _cache[k]


ELIG = ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch", "secondary_not_accepted")
COLS = ("base", "F12", "F12B", "F12B_strict", "F12B_veto", "v2F12", "v2F12B")
BASE_OF = {"base": "base", "F12": "F12", "F12B": "F12", "F12B_strict": "F12", "F12B_veto": "F12", "v2F12": "v2F12", "v2F12B": "v2F12"}
BKW = {"F12B": {}, "F12B_strict": {"reading_rule": "strict"}, "F12B_veto": {"secondary_reading_conflict": "veto"}, "v2F12B": {}}


def final(canon, ptext, stext, col):
    m = BASE_OF[col]
    st = stage(canon, ptext, m)
    if st["state"] in PASSING:
        return {"pass": True, "reason": st["reason"], "kind": "primary", "label": st["label"], "warn": sorted(st["warnings"])}
    reason = st["reason"] or ""
    res = {"pass": False, "reason": reason, "kind": "ng", "label": st["label"], "warn": []}
    if st["state"] == "NG_SECONDARY_UNAVAILABLE" and stext:
        sb, a4a, a4b, _ = E.secondary_accept_kind(canon, stext)
        if sb or (m == "v2F12" and a4a):
            return {"pass": True, "reason": "secondary_accept", "kind": "secondary", "label": "SECONDARY", "warn": []}
        res["reason"] = "secondary_not_accepted"
    if col in BKW and stext:
        if any(res["reason"].startswith(e) for e in ELIG):
            r = B.composite_judge(canon, ptext, stext, META, **BKW[col])
            res["composite"] = {"equal": r.equal, "why": r.why[:160], "blocked_by": r.blocked_by}
            if r.equal:
                return {"pass": True, "reason": "composite", "kind": "composite", "label": r.label, "warn": list(r.warnings), "listen": r.listen_required,
                        "needs_new_azure_call": res["reason"] in ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch")}
        else:
            r = B.composite_judge(canon, ptext, stext, META, **BKW[col])
            if r.equal:
                res["composite_would_pass_but_reason_not_eligible"] = res["reason"]
    return res


def row(canon, ptext, stext, **extra):
    d = {"canon": canon, "primary": ptext, "secondary": stext}
    for c in COLS:
        r = final(canon, ptext, stext, c)
        d[c] = {k: r[k] for k in ("pass", "reason", "kind", "warn", "listen") if k in r}
        if r.get("composite"):
            d[c]["composite"] = r["composite"]
        if r.get("composite_would_pass_but_reason_not_eligible"):
            d[c]["not_eligible_reason"] = r["composite_would_pass_but_reason_not_eligible"]
        if c == "F12B" and r.get("needs_new_azure_call"):
            d["needs_new_azure_call"] = True
    d.update(extra)
    return d


def n_pass(rows, m):
    return sum(1 for r in rows if r[m]["pass"])


def inc(rows, a="F12", b="F12B"):
    return [r for r in rows if r[b]["pass"] and not r[a]["pass"]]


def reg(rows, a="F12", b="F12B"):
    return [r for r in rows if r[a]["pass"] and not r[b]["pass"]]


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
P("== A. 月題(12転写: attempt1-3 x {保存転写+OpenAI再転写3}) ==  列: base / F12(=base+F1F2) / F12B / F12B(strict読み) / F12B(veto) / (参考)v2F12 / (参考)v2F12B")
for r in moon:
    P(f" a{r['attempt']} {r['draw']:8s} P={r['primary'][:20]:22s} " + " ".join(f"{c}={int(r[c]['pass'])}" for c in COLS)
      + f" [F12:{r['F12']['reason'][:26]} -> B:{r['F12B'].get('composite', {}).get('blocked_by') or r['F12B']['kind']}]")
P(" PASS数: " + " ".join(f"{c}={n_pass(moon, c)}" for c in COLS) + f" / {len(moon)}")
for k in (1, 2, 3):
    rs = [r for r in moon if r["attempt"] == k]
    P(f"  attempt{k}: F12={n_pass(rs,'F12')}/{len(rs)} F12B={n_pass(rs,'F12B')}/{len(rs)} strict={n_pass(rs,'F12B_strict')} veto={n_pass(rs,'F12B_veto')} (安定救済=全転写PASS: F12={n_pass(rs,'F12')==len(rs)} F12B={n_pass(rs,'F12B')==len(rs)})")
moon_inc = inc(moon)
P(" β増分(F12→F12B):", [(r["attempt"], r["draw"], r["F12B"]["warn"], r["F12B"].get("listen")) for r in moon_inc])
P("   うちstrict読みでも通る:", [(r["attempt"], r["draw"]) for r in moon_inc if r["F12B_strict"]["pass"]], "/ vetoでも通る:", [(r["attempt"], r["draw"]) for r in moon_inc if r["F12B_veto"]["pass"]])
P(" v2読み規則を除いた場合(F12B_strict)の増分:", len(inc(moon, "F12", "F12B_strict")), "/ F12に対し v2F12 が追加する(=v2部品の効果):", len(inc(moon, "F12", "v2F12")))

# ================= B. N-3 30 clip =================
clips = {c["id"]: c for c in json.load(open(os.path.join(HERE, "n3_clips_01.json"), encoding="utf8"))}
n3 = []
for r in log:
    if r["stage"] == "N3_asr":
        c = clips[r["item"]]
        n3.append(row(c["canonical"], r["openai_text"], r["azure_text"], id=r["item"], type=c["type"], tts_input=c["tts_input"]))
out["n3"] = n3
P("== B. N-3 30 clip (実TTS→実OpenAI+実Azure。音声は意図的な誤読=正解は全てNG) ==")
P(" 誤PASS数: " + " ".join(f"{c}={n_pass(n3, c)}" for c in COLS) + f" / {len(n3)}")
P(" 基準1a 増分誤PASS(F12→F12B):", [r["id"] for r in inc(n3)], "/ strict:", [r["id"] for r in inc(n3, "F12", "F12B_strict")], "/ veto:", [r["id"] for r in inc(n3, "F12", "F12B_veto")])
P(" 基準2 回帰(F12→F12B):", [r["id"] for r in reg(n3)], "/ F12がbaseから新たにNG化(F1の効果):", [(r["id"], r["F12"]["reason"]) for r in reg(n3, "base", "F12")])
P(" 参考 composite が評価対象になった件:", [(r["id"], r["F12B"].get("composite", {}).get("blocked_by")) for r in n3 if r["F12B"].get("composite")])
P(" 参考 eligible reason外でcompositeが通りうる件:", [(r["id"], r["F12B"]["not_eligible_reason"]) for r in n3 if r["F12B"].get("not_eligible_reason")])

# ================= C. Melos preview =================
p4 = json.load(open(os.path.join(HERE, "eval_api0_v1_01.out.json"), encoding="utf8"))["p4"]["flips"]
mel_a = [r for r in log if r["stage"] == "A3_azure_flip" and r["item"].startswith("preview")][0]["text"]
mc = [f for f in p4 if "preview_attempt2" in f["file"]][0]
melos = row(mc["canon"], mc["text"], mel_a, id="melos_preview_attempt2")
out["melos"] = melos
P("== C. Melos preview ==", melos["canon"][:30], "| P:", melos["primary"][:30], "| S:", mel_a[:30])
P(" " + " ".join(f"{c}={melos[c]['pass']}/{melos[c]['kind']}" for c in COLS))
c4 = all(melos["F12"][k] == melos["F12B"][k] for k in ("pass", "kind"))
P(" 基準4 Melos副作用(F12 と F12B が同一):", c4)

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
P(" PASS数: " + " ".join(f"{c}={n_pass(hist, c)}" for c in COLS))
inc_h = inc(hist)
P(" 基準1d composite による増分PASS(全件列挙):", len(inc_h))
for r in inc_h:
    P("   ", r["canon"][:40], "|", r["primary"][:40], "|", r["secondary"][:40])
P(" 基準2 回帰(F12→F12B):", [r["file"][-40:] for r in reg(hist)], "/ F12がbaseから新たにNG化(F1の効果):", len(reg(hist, "base", "F12")))
P(" composite が評価対象になった件の内訳:", dict(collections.Counter(r["F12B"]["composite"]["blocked_by"] for r in hist if r["F12B"].get("composite"))))

# ================= E. N-1 150 最悪ケース露出 =================
n1 = N1.all_pairs()
expo, expo_strict, n1_any = [], [], 0
for p in n1:
    c, a = p["canon"], p["asr"]
    fr = final(c, a, c, "F12")
    br = B.composite_judge(c, a, c, META)
    brs = B.composite_judge(c, a, c, META, reading_rule="strict")
    if br.equal:
        n1_any += 1
    if br.equal and not fr["pass"]:
        expo.append({"id": p["id"], "type": p["type"], "canon": c, "asr": a, "F12_reason": fr["reason"], "warn": list(br.warnings)})
    if brs.equal and not fr["pass"]:
        expo_strict.append(p["id"])
out["n1_exposure"] = expo
P("== E. N-1 確定負例 x 最悪ケース(Secondary=原稿そのもの。比較=F12) ==")
P(f" 対={len(n1)} / composite がPASS候補にした(F12で既にPASSの件を含む)={n1_any} / うちF12がNGなのに composite がPASS(=露出)={len(expo)} / strict読みでの露出={len(expo_strict)}")
for e in expo:
    P("   露出:", e["id"], e["type"], "|", e["canon"][:30], "|", e["asr"][:30], "|", e["F12_reason"], e["warn"])
P(" 露出の型内訳:", dict(collections.Counter(e["type"] for e in expo)))

# ================= F. 合成負例マトリクス =================
S_OK = "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"
TAIL = "。その奥に潜む岩の上着の秘密。"
vals = ["8,800", "89,000", "8,090", "9,900", "千九百", "八万九千", "8000800", "8000句800", "8万9千", "890"]
reads = ["すわ", "しば", "し", "巣は", "しわし"]
syn = []      # (group, type, canon, primary, secondary)  正解は全てNG
for v in vals:
    p_v = f"月のしわ、{v}本超{TAIL}"
    syn.append(("V1", "value_wrong:Primary(Secondary=原稿値)", MOON, p_v, S_OK))
    syn.append(("V1", "value_wrong:Both(同じ値違い)", MOON, p_v, p_v))
    syn.append(("V1", "value_wrong:Secondary_only", MOON, "月のしわ、8,900本超" + TAIL, p_v))
for rd in reads:
    for pv in ("8000900", "8,900", "8000九百"):
        syn.append(("V1", "reading_wrong:Primary(Secondary=原稿値)", MOON, f"月の{rd}、{pv}本超{TAIL}", S_OK))
for c, p, s, t in [("三日待った", "3日待った。", "3日待った。", "irregular"), ("三日待った", "三日間待った。", "3日待った。", "irregular"),
                   ("二十歳になった", "20歳になった", "20歳になった", "irregular"), ("十月一日に会う", "10月1日に会う", "10月1日に会う", "irregular"),
                   ("三人は行かない", "3人は行く", "3人は行かない", "negation"), ("三人は行かない", "3人は行かない", "3人は行く", "negation"),
                   ("犬が三匹いる", "犬が三頭いる", "犬が三匹いる", "counter"), ("本を三冊買う", "本を三本買う", "本を3冊買う", "counter"),
                   ("売上は1,200円です", "売上は1,300円です", "売上は1,200円です", "value"), ("売上は1,200円です", "売上は12,000円です", "売上は1,200円です", "value")]:
    syn.append(("V1", t, c, p, s))
C2 = "売上は1,200円で利益は3,500円です"
S2 = "売上は1200円で利益は3500円です"
C3 = "1,200円と1,200円を払う"
S3 = "1200円と1200円を払う"
# M-3 複数atom (v1に無かった形)
for p, s, t in [
    ("売上は1000200円で利益は4,500円です", S2, "multi:first_explained+second_contradiction"),
    ("売上は1,300円で利益は3000五百円です", S2, "multi:first_contradiction+second_explained"),
    ("売上は1,200円で利益は3000200円です", S2, "multi:second_garble_sum_mismatch"),
    ("売上は1000500円で利益は3,500円です", S2, "multi:first_garble_sum_mismatch"),
    ("売上は1000200円で利益は3,500円です", "売上は3500円で利益は1200円です", "multi:secondary_order_swapped"),
    ("売上は1000200円で利益は3,500円です", "売上は1200円です", "multi:secondary_missing_atom"),
    ("売上は1000200円で利益は3,500円です", "売上は1200円で利益は3500円で費用は100円です", "multi:secondary_extra_atom"),
    ("売上は1000200円で利益は3,500円です", "売上は1200円で利益は3500円と3500円です", "multi:secondary_repeated_atom"),
    ("売上は1000200円で利益は3,500円です", "売上は1200円で利益は3,600円です", "multi:secondary_second_value_wrong"),
    ("利益は3,500円で売上は1000200円です", S2, "multi:primary_order_swapped"),
    ("売上は1000200円で利益は3,500円です。費用は100円", S2, "multi:primary_extra_number"),
    ("売上は1000200円です", S2, "multi:primary_second_atom_missing"),
]:
    syn.append(("M3", t, C2, p, s))
for p, s, t in [
    ("1000200円と1000500円を払う", S3, "same_counter:second_garble_wrong"),
    ("1000500円と1000200円を払う", S3, "same_counter:first_garble_wrong"),
    ("1000200円を払う", S3, "same_counter:primary_second_missing"),
    ("1000200円と1000200円を払う", "1200円を払う", "same_counter:secondary_missing"),
    ("1000200円と1,300円を払う", S3, "same_counter:second_value_wrong"),
]:
    syn.append(("M3", t, C3, p, s))
# F-B・Secondary表記の負例 (Opus 事前登録不足)
for c, p, s, t in [
    ("売上は1,200円です", "売上は1000200円です", "売上はせんにひゃく円です", "FB:secondary_kana_numeral"),
    ("売上は1,200円です", "売上は1000200円です", "売上は千にひゃく円です", "FB:secondary_kana_numeral_mixed"),
    ("売上は8,900円です", "売上は8000900円です", "売上は8000 900円です", "FB:secondary_space_run"),
    ("売上は8,900円です", "売上は8000900円です", "売上は8万900円です", "FB:secondary_man"),
    ("売上は8,900円です", "売上は8000900円です", "売上は8万9千円です", "FB:secondary_man_sen"),
    ("売上は8,900円です", "売上は8000900円です", "売上は８０００　９００円です", "FB:secondary_fullwidth_space_run"),
    ("売上は8,900円です", "売上は8000 900円です", "売上は8900円です", "FB:primary_space_run"),
    ("売上は8,900円です", "売上は８０００　９００円です", "売上は8900円です", "FB:primary_fullwidth_space_run"),
    ("売上は8,900円です", "売上は8000万900円です", "売上は8900円です", "FB:primary_man_in_run"),
    ("売上は8,900円です", "売上は8万900円です", "売上は8900円です", "FB:primary_man_kanji"),
    ("売上は8,900円です", "売上は8000九万円です", "売上は8900円です", "FB:primary_kanji_man"),
    ("売上は8,900円です", "売上は８０００８００円です", "売上は８９００円です", "FB:fullwidth_value_wrong_primary"),
    ("売上は8,900円です", "売上は８０００９００円です", "売上は８８００円です", "FB:fullwidth_value_wrong_secondary"),
    ("売上は12,300円です", "売上は12000300円です", "売上は12300円です", "FB:front_fragment_not_d10k(R-3)"),
    ("売上は12,300円です", "売上は12000三百円です", "売上は12300円です", "FB:front_fragment_not_d10k_kanji(R-3)"),
    ("売上は100,500円です", "売上は100200300円です", "売上は100500円です", "FB:three_fragments(R-3)"),
    ("売上は9,800円です", "売上は80九百円です", "売上は9800円です", "FB:front_fragment_not_d10k_80(R-3)"),
    ("売上は1,200円で犬が3匹います", "売上は1000200円で犬が3匹います", "売上は1200円で犬がさんびきいます", "R4:secondary_kana_numeral_other_atom"),
    ("売上は1,200円で犬が3匹います", "売上は1000200円で犬が3匹います", "売上は1200円で犬がみっつです", "R4:secondary_kana_tsu"),
]:
    syn.append(("FB", t, c, p, s))
syn_eval = []
for g, t, c, p, s in syn:
    fr = final(c, p, s, "F12")
    br = B.composite_judge(c, p, s, META)
    br_a = B.composite_judge(c, p, s, META, allow_explained_garble=False)
    brs = B.composite_judge(c, p, s, META, reading_rule="strict")
    syn_eval.append({"group": g, "type": t, "canon": c, "primary": p, "secondary": s, "F12_pass": fr["pass"], "composite": br.equal, "composite_alpha": br_a.equal,
                     "composite_strict": brs.equal, "blocked_by": br.blocked_by, "incremental_pass": bool(br.equal and not fr["pass"])})
out["synthetic_negative"] = syn_eval
P("== F. 合成負例マトリクス(正解は全てNG)。V1=v1の55件 / M3=複数atom(M-3) / FB=F-B・Secondary表記・R-3・R-4 ==")
for g in ("V1", "M3", "FB"):
    rs = [r for r in syn_eval if r["group"] == g]
    P(f" {g}: 件数={len(rs)} / β(F12B)がPASSにした={sum(1 for r in rs if r['composite'])} / 案αがPASS={sum(1 for r in rs if r['composite_alpha'])} / "
      f"増分誤PASS(F12 NG→composite PASS)={sum(1 for r in rs if r['incremental_pass'])} / F12自体が誤PASS={sum(1 for r in rs if r['F12_pass'])}")
for r in syn_eval:
    if r["composite"] or r["F12_pass"]:
        P("   要確認:", r["group"], r["type"], "| composite=", r["composite"], "| F12=", r["F12_pass"], "|", r["primary"][:40], "|", r["secondary"][:40])
P(" 非通過理由の分布(M3+FB):", dict(collections.Counter(r["blocked_by"] for r in syn_eval if r["group"] != "V1")))

# ---- 正例(合成。設計の対象型を示すだけ。実頻度の証拠ではない) ----
pos = [("売上は1,200円です", "売上は1000200円です", "売上は1200円です"), ("参加者は3,500人です", "参加者は3000五百人です", "参加者は3500人です"),
       ("価格は12,000円です", "価格は10000二千円です", "価格は12000円です"), ("価格は12,000円です", "価格は12,000円です", "価格は12000円です"),
       (C2, "売上は1000200円で利益は3,500円です", S2), (C2, "売上は1000200円で利益は3000五百円です", S2), (C3, "1000200円と1000200円を払う", S3),
       ("売上は8,900円です", "売上は８０００９００円です", "売上は８９００円です")]
pos_eval = []
for c, p, s in pos:
    br = B.composite_judge(c, p, s, META)
    pos_eval.append({"canon": c, "primary": p, "secondary": s, "composite": br.equal, "why": br.why[:80], "F12_pass": final(c, p, s, "F12")["pass"], "listen": br.listen_required})
out["synthetic_positive"] = pos_eval
P("== G. 合成の正例(設計対象型の動作確認のみ。実頻度の証拠ではない) ==")
for r in pos_eval:
    P("  ", r["canon"], "|", r["primary"], "|", r["secondary"], "| composite=", r["composite"], "| F12=", r["F12_pass"], "| listen=", r["listen"], r["why"])

# ================= H. 追加Azure呼出 / 評価不能 =================
needs = [r for grp in (moon, n3, hist) for r in grp if r.get("needs_new_azure_call")]
att = json.load(open(os.path.join(HERE, "attempt_pool_01.json"), encoding="utf8"))
unk = json.load(open(os.path.join(HERE, "unknown_pool_02.json"), encoding="utf8"))
P("== H. 追加Azure呼出 / 評価不能 ==")
P(f" composite が新たにAzure呼出を要した対(現行はP1/最終ゲートでAzure不呼出)={len(needs)} (見積 {len(needs)*AZ_COST:.2f}円/評価母集団ぶん)")
P(f" 評価不能: P-4 実attempt={len(att)} 件(うちSecondary記録あり={sum(1 for x in att if x.get('secondary'))})、未知データ(Primary転写のみ)={len(unk)} 件、N-1=150 対(音声・Secondary実転写なし=最悪ケース被覆のみ)")

# ================= I. R-5 予備集計 (API 0): F1+F2 が新たに作るNG と β対象型の頻度 =================
def r5_scan(name, pairs):
    n, newng, reasons, elig = 0, [], collections.Counter(), collections.Counter()
    for c, p in pairs:
        if not c or not p:
            continue
        n += 1
        b0, f0 = stage(c, p, "base"), stage(c, p, "F12")
        if b0["state"] in PASSING and f0["state"] not in PASSING:
            newng.append((c[:30], p[:30], f0["reason"])); reasons[f0["reason"]] += 1
        if f0["state"] not in PASSING and (f0["reason"] or "") in ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch"):
            elig[f0["reason"]] += 1
    return {"pool": name, "n": n, "f1f2_new_ng": len(newng), "new_ng_reasons": dict(reasons), "value_diff_ng_total": dict(elig), "new_ng_cases": newng}


r5 = [r5_scan("P-4 attempt_pool_01(562)", [(x["canon"], x["primary"]) for x in att]),
      r5_scan("未知データ unknown_pool_02(493)", [(x["canon"], x["asr"]) for x in unk]),
      r5_scan("実履歴P-S対(43)", [(r["canon"], r["primary"]) for r in hist]),
      r5_scan("月題(12)", [(r["canon"], r["primary"]) for r in moon]),
      r5_scan("N-3(30)", [(r["canon"], r["primary"]) for r in n3])]
out["r5_preview"] = r5
P("== I. R-5 予備集計 (API 0): 保存転写でのF1+F2(base→F12)の新規NG と 値差NG(β対象になりうるPrimary NG)の件数 ==")
for x in r5:
    P(f" {x['pool']}: n={x['n']} / F1+F2が新たにNG化={x['f1f2_new_ng']} {x['new_ng_reasons']} / F12のp1_value_diff等NG={x['value_diff_ng_total']}")
    for c in x["new_ng_cases"][:6]:
        P("     新規NG:", c)

# ================= J. 読み規則別内訳 (探索的・初回実行後に追加=事後追加。判定基準には使わない) =================
# βの増分が『Productionが既に受理する読みクラス』で成立するか、『v2の助詞発音等価(pron_hira)』に依存するかを、値atomを除いた残りに対する
# Production `classify_ja_asr_match` の分類で内訳する(proto v2は変更しない)。
import unicodedata as _ud
import er007_ja_asr_validator_01 as _javal
PROD_READ_PASS = ("EXACT_MATCH", "NORMALIZED_MATCH", "PHONETIC_MATCH", "READING_RESOLVED_MATCH")
def _masked(canon, ptext):
    Cn, Pn = _ud.normalize("NFKC", canon), _ud.normalize("NFKC", ptext)
    st, c_atoms = B.analyze_primary_values(Cn, Pn, True)
    if any(x.span is None for x in st):
        return None
    return B._mask(Cn, [(a.start, a.end) for a in c_atoms]), B._mask(Pn, [x.span for x in st])
jrows = []
for grp, rs in (("moon", moon_inc), ("n3", inc(n3)), ("hist", inc_h)):
    for r in rs:
        mk = _masked(r["canon"], r["primary"])
        cls = _javal.classify_ja_asr_match(mk[0], mk[1], allow_reading_resolver=False).classification if mk else None
        jrows.append({"group": grp, "id": r.get("id") or f"a{r.get('attempt')}_{r.get('draw')}", "primary": r["primary"][:30], "masked_class": cls,
                      "prod_read_pass": cls in PROD_READ_PASS, "strict_pass": r["F12B_strict"]["pass"], "veto_pass": r["F12B_veto"]["pass"]})
out["reading_breakdown"] = jrows
P("== J. 読み規則別内訳(探索的・事後追加。値atom除去後の残りに対する Production 分類) ==")
for x in jrows:
    P("  ", x["group"], x["id"], x["primary"], "| masked_class=", x["masked_class"], "| Production読みクラスで成立=", x["prod_read_pass"], "| strict=", x["strict_pass"], "| veto=", x["veto_pass"])
P(f" 増分{len(jrows)}件中: Production既存の読みクラスで成立={sum(1 for x in jrows if x['prod_read_pass'])} / v2の助詞発音等価に依存={sum(1 for x in jrows if not x['prod_read_pass'])}")

# ================= 判定(事前登録の機械写像) =================
c1a = len(inc(n3)) == 0
c1b_types = collections.Counter(e["type"] for e in expo)
c1b = all(("garble" in t or "断片" in t) for t in c1b_types)
c1c = sum(1 for r in syn_eval if r["incremental_pass"]) == 0 and sum(1 for r in syn_eval if r["composite"]) == 0
c1d_listed = len(inc_h)
c2 = not (reg(n3) or reg(moon) or reg(hist)) and melos["F12"]["pass"] <= melos["F12B"]["pass"]
moon_inc_n = len(moon_inc)
P("== 事前登録基準の機械判定 ==")
P(f" 1a N-3増分誤PASS=0: {c1a} | 1b N-1露出が値garble型のみ: {c1b} (型={dict(c1b_types)}) | 1c 合成負例(V1+M3+FB) composite PASS=0: {c1c} | 1d 履歴対の増分PASS件数(要個別審査)={c1d_listed}")
P(f" 2 回帰0: {c2} | 4 Melos副作用0: {c4} | 3 月題の増分(F12→F12B)={moon_inc_n} (strict読み={len(inc(moon, 'F12', 'F12B_strict'))}, veto={len(inc(moon, 'F12', 'F12B_veto'))})")
status = "REJECTED" if not (c1a and c1b and c1c and c2 and c4) else ("VALIDATED(限定)候補[低優先]" if moon_inc_n >= 1 else "NOT_EFFECTIVE")
P(" Status候補(機械写像。1dの個別審査結果は別途。最終はFable):", status)
out["verdict"] = {"c1a": c1a, "c1b": c1b, "c1b_types": dict(c1b_types), "c1c": c1c, "c1d_listed": c1d_listed, "c2": c2, "c4": c4,
                  "moon_increment": moon_inc_n, "moon_increment_strict": len(inc(moon, "F12", "F12B_strict")), "moon_increment_veto": len(inc(moon, "F12", "F12B_veto")),
                  "status_candidate": status}
E.api0_guard_off()
json.dump(out, open(os.path.join(HERE, "eval_b_light_api0_02.out.json"), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1, sort_keys=True, default=str)
open(os.path.join(HERE, "eval_b_light_api0_02.out.txt"), "w", encoding="utf8", newline="\n").write("\n".join(lines) + "\n")
