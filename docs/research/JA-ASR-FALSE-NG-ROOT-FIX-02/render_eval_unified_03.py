# eval_unified_03.out.json から EVAL_UNIFIED_03.md を生成(API 0・決定的)。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/render_eval_unified_03.py
import collections, json, math, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_reading_compare_02 as P
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
d = json.load(open(OUT + "eval_unified_03.out.json", encoding="utf8"))
CF = d["configs"]
ON, OFF = "L1+L2+L3", "L1+L2+L3(R1off)"
PASSCAT = ("PASS", "PASS_W_PROD", "PASS_W_NEW")
LBL = {"PASS": "PASS", "PASS_W_PROD": "PASS_W(既存)", "PASS_W_NEW": "PASS_W(新方式)", "HR": "HR", "NG": "NG"}
o = []
w = o.append
rows = d["rows"]


def cell(r):
    return LBL[r["cat"]] + (":" + r["route"][:46] if r["cat"] in PASSCAT else ":" + str(r["reason"]))


def vtype(r):
    t, g = r["tag"], r["group"]
    if "しわ→詩は" in t or g.startswith("UC6_U6"):
        return "T1"
    if "garble" in t:
        return "T2"
    if "不規則読み" in t:
        return "T3"
    return "OTHER"


def pct(n, tot):
    return f"{100.0 * n / tot:.0f}%" if tot else "-"


def dist_cell(v):
    tot = v["n_combos"]
    c = v["cats"]
    ps = sum(c.get(k, 0) for k in PASSCAT)
    return f"{ps}/{tot}({pct(ps, tot)}) HR{c.get('HR', 0)} NG{c.get('NG', 0)}"


def cp_upper(n, conf=0.95):
    return 1 - (1 - conf) ** (1.0 / n) if n > 0 else 1.0


w("# EVAL_UNIFIED_03(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03。eval_unified_03.py の出力から自動生成。API 0)")
w(f"事前登録=PREREGISTERED_03.md(+補遺§7、評価実行前にcommit済み)。Opus条件Aレビュー=OPUS_REVIEW_01.md(M-1〜M-7/R-1〜R-7全採用)。層版={d['versions']['layer']} / 規則版={d['versions']['rule']}。")
w(f"Production HEAD 定数: {json.dumps(d['head_consts'], ensure_ascii=False)}。Production file sha256(先頭16桁・不変確認): {json.dumps(d['production_sha256'], ensure_ascii=False)}。")
w(f"NEG集合(Phase 1/2と同一): n={d['neg_set']['n']} sha256={d['neg_set']['sha256']}(事前登録値とassert一致)。L0とPhase 1 M0の行ごと一致: 比較{d['parity']['n_compared']}行・不一致{d['parity']['L0_vs_M0_mismatch']}。")
w("**区分(M-2)**: PASS=Production clean PASS / PASS_W(既存)=Productionの警告付きPASS / PASS_W(新方式)=新層[v2発音救済・β・別表L3・合意再試行]経由=専用warning `JA_NEWLAYER_*` 付き・常に試聴リスト別枠(APPROVED_EQUIVALENCE_BASES非登録) / HR=再試行発火後の早期HR(エンジン間の内容矛盾のみが根拠、PASSにしない) / NG。")
w("**主設定=R-1 ON**(PREREGISTERED_03どおり)。R-1 OFF(=Opusの『4/6』想定、Phase 2のv2規則相当)を全表で併記する。R-1は『ASR側差分span内の漢字1字でも読み候補が2つ以上あれば発音救済しない』検査(M-2/R-1、Opus推奨)。")
w("")
# ---------------- 0. 要旨 ----------------
pos = d["positives"]
cnt = {}
for fn in (ON, OFF):
    cnt[fn] = sum(1 for p in pos if p["cons"][f"{fn}|N1|stored_order"]["cat"] in PASSCAT)
w("## 0. 要旨(事実のみ。Statusは§12の候補)")
w(f"- 6音声の決定対(記録済みOpenAI×Azure)の機械判定: **R-1 ON {cnt[ON]}/6 が PASS系**、**R-1 OFF {cnt[OFF]}/6**(いずれもPASS_W(新方式)または既存PASS_W。clean PASSは0)。残りは R-1 OFF でも ms_03 a1・reselect a3 の2本が NG のまま(Opus予測どおり)。")
w("- ASR再試行(合意規則)は6本に**新たなPASSを1本も足さない**(§3、再試行起因PASS 0)。best-of-N(参考)は足す(§3、N3負例で再試行起因の誤PASSも出る=§5)。")
w("- 負例の増分誤PASS: R-1 ON は T2(β最悪露出)1件のみ、R-1 OFF は T1 6件+T2 2件(§4)。回帰0。")
w("- 合意規則のN3負例での再試行起因誤PASSは0(BoNは出る)。ただし分母が小さい(§5の上限を参照)。")
w("")
# ---------------- 1. 6音声 ----------------
w("## 1. 6音声×層: 最終Gate結果(決定対=記録済みOpenAI転写 × 当該wavのAzure転写。合意再試行は記録順[first=記録済み、追加=記録順])")
for fn, title in ((ON, "1A. R-1 ON(主設定)"), (OFF, "1B. R-1 OFF(参考=Opus想定)")):
    w(f"### {title}")
    l1n = "L1" if fn == ON else "L1(R1off)"
    if fn == ON:
        w(f"| 音声 | L0 | {l1n} | L1+L2 | {fn} | +合意N=2 | +合意N=3 | HR候補(最終NGのとき) |")
        w("|---|---|---|---|---|---|---|---|")
    else:
        w(f"| 音声 | L0 | {l1n} | {fn} | +合意N=2 | +合意N=3 | HR候補(最終NGのとき) |")
        w("|---|---|---|---|---|---|---|")
    for p in pos:
        r = p["per_draw"][0]["res"]
        l12 = r["L1+L2"] if fn == ON else None
        c2, c3 = p["cons"][f"{fn}|N2|stored_order"], p["cons"][f"{fn}|N3|stored_order"]

        def cc(c):
            return LBL[c["cat"]] + (f":{c['route']}" if c["cat"] in PASSCAT else (f":{c['reason']}" if c["cat"] != "NG" else "")) + (f"(追加draw{c['extra_draws']}本)" if c["retry_fired"] else "")
        hc = ("あり" if p["hr_cand"]["candidate"] else "なし") if c3["cat"] in ("NG", "HR") else "-"
        mid = f"{cell(r['L1+L2'])} | " if fn == ON else ""
        w(f"| {p['run']} a{p['attempt']} | {cell(r['L0'])} | {cell(r[l1n])} | {mid}{cell(r[fn])} | {cc(c2)} | {cc(c3)} | {hc} |")
    w("")
w("### 1a. 決定対の転写(OpenAI=記録時、Azure=当該wav)と判定の具体的条件")
w("| 音声 | OpenAI(stored) | Azure | R-1 OFF時の決め手 | R-1 ON時の決め手 |")
w("|---|---|---|---|---|")
for p in pos:
    r = p["per_draw"][0]["res"]
    w(f"| {p['run']} a{p['attempt']} | {p['draws'][0]} | {p['azure'][0][1] if p['azure'] else '(なし)'} | {cell(r[OFF])} | {cell(r[ON])} + R-1:{'blocked' if 'R1_blocked' in r[ON]['layers'] or r[ON].get('beta_blocked_by')=='R1_blocked_in_beta' else '-'} |")
w("")
w("### 1b. R-6: Phase 2の表記との差(両方を正直に併記)")
w("| 音声 | Phase 2(L1+L2+L3+L4 best-of-N)の記載 | 今回(合意規則+M-5別表、R-1 OFF=Phase 2相当のv2規則) | 今回(R-1 ON=主設定) |")
w("|---|---|---|---|")
ph2 = {("run_ms_03", 1): "N=2でPASS_W", ("run_ms_03", 2): "PASS_W", ("run_ms_03", 3): "PASS_W", ("run_reselect_01", 1): "PASS_W", ("run_reselect_01", 2): "PASS_W", ("run_reselect_01", 3): "N=3でPASS_W(確率0.60)"}
for p in pos:
    a, b = p["cons"][f"{OFF}|N3|stored_order"], p["cons"][f"{ON}|N3|stored_order"]
    w(f"| {p['run']} a{p['attempt']} | {ph2[(p['run'], p['attempt'])]} | {LBL[a['cat']]}{('('+str(a['reason'])+')') if a['cat']=='HR' else ''} | {LBL[b['cat']]}{('('+str(b['reason'])+')') if b['cat']=='HR' else ''} |")
w("Phase 2の『(ii)併用で5〜6/6』は best-of-N の釣り(多数派の反証を捨てて少数派drawを採る)を含み、合意規則(M-3)では 4/6(R-1 OFF時)+NG/HR 2 に下がる(R-6)。")
w("")
# ---------------- 2. 全draw ----------------
w("## 2. 全draw対(OpenAI全draw × Azure[0]): 層別 PASS系/NG の件数")
w("| 音声 | draw数 | L0 | L1 | L1(R1off) | L1+L2 | L1+L2+L3 | L1+L2+L3(R1off) |")
w("|---|---|---|---|---|---|---|---|")
tot = {f: 0 for f in CF}
ntot = 0
for p in pos:
    cs = []
    for f in CF:
        n = sum(1 for x in p["per_draw"] if x["res"][f]["cat"] != "NG")
        tot[f] += n
        cs.append(f"{n}/{len(p['draws'])}")
    ntot += len(p["draws"])
    w(f"| {p['run']} a{p['attempt']} | {len(p['draws'])} | " + " | ".join(cs) + " |")
w(f"| 合計 | {ntot} | " + " | ".join(f"{tot[f]}/{ntot}" for f in CF) + " |")
w("")
# ---------------- 3. 合意規則の分布 ----------------
w("## 3. ASR再試行: 合意規則(主) vs best-of-N(参考)。全(first, 追加draw部分集合)組合せの等重み平均(出た順に依存しない)")
w("セル=『PASS系 件数/組合せ数(率) HR件数 NG件数』。N=1は再試行なし。BoN列=best-of-N(参考、矛盾無視)のPASS系率。")
for fn, title in ((ON, "3A. R-1 ON(主設定)"), (OFF, "3B. R-1 OFF")):
    w(f"### {title}")
    w("| 音声 | N=1 | 合意N=2 | 合意N=3 | BoN N=2 | BoN N=3 | 合意の再試行起因PASS(N=2/3) | BoNの再試行起因PASS(N=2/3) |")
    w("|---|---|---|---|---|---|---|---|")
    for p in pos:
        v = {n: p["cons"][f"{fn}|N{n}"] for n in (1, 2, 3)}

        def bon(vv):
            t = vv["n_combos"]
            ps = sum(vv["bon"].get(k, 0) for k in PASSCAT)
            return f"{ps}/{t}({pct(ps, t)})"
        w(f"| {p['run']} a{p['attempt']} | {dist_cell(v[1])} | {dist_cell(v[2])} | {dist_cell(v[3])} | {bon(v[2])} | {bon(v[3])} | {len(v[2]['retry_induced_pass'])}/{len(v[3]['retry_induced_pass'])} | {len(v[2]['bon_induced_pass'])}/{len(v[3]['bon_induced_pass'])} |")
    w("")
w("読み取り: 合意規則は『N=1でNGだった組合せ』をPASSにする(再試行起因PASS)ことが**ない**(全音声で0)。追加drawで非NGが見つかっても、他のdrawに値以外の内容食い違い(例 reselect a3 の『スギノ』)があるため HR に回る。best-of-N は同じ組合せをPASS系にする(列『BoNの再試行起因PASS』)=Opusの指摘した釣りが実データで起きる。")
w("")
w("### 3a. reselect a3 の釣り事例(R-1 OFF): どのdrawが非NGで、どのdrawが矛盾か")
p = [x for x in pos if x["run"] == "run_reselect_01" and x["attempt"] == 3][0]
c = p["cons"][f"{OFF}|N3"]
w(f"- draws: " + " / ".join(f"[{i}] {t}" for i, t in enumerate(p["draws"])))
w(f"- Azure: {p['azure'][0][1]}")
w(f"- N=3組合せ {c['n_combos']}件中 HR={c['cats'].get('HR', 0)}・PASS系={sum(c['cats'].get(k, 0) for k in PASSCAT)}(first=月野市のdrawの組合せのみ。再試行なしで単独PASS)・NG={c['cats'].get('NG', 0)}。BoNなら PASS系 {sum(c['bon'].get(k, 0) for k in PASSCAT)}/{c['n_combos']}。")
w("")
# ---------------- 4. 負例(コーパス) ----------------
neg = [r for r in rows if r["truth"] == "NEG"]
w("## 4. 負例・対照の誤PASS(コーパス=Phase 1/2と同一1439行+L3_NEG+N3_redraw。PASS系=PASS/PASS_W(既存)/PASS_W(新方式))")
w(f"NEG行数={len(neg)}。増分=L0がNGで当該構成がPASS系。回帰=L0がPASS系で当該構成がNG(全truth)。")
w("| 構成 | 総誤PASS | 増分誤PASS | T1同音異表記 | T2β最悪露出 | T3不規則読み | OTHER | 回帰 |")
w("|---|---|---|---|---|---|---|---|")
INC = {}
for f in CF:
    inc = [r for r in neg if r["res"][f]["cat"] != "NG" and r["res"]["L0"]["cat"] == "NG"]
    INC[f] = inc
    reg = [r for r in rows if r["res"]["L0"]["cat"] != "NG" and r["res"][f]["cat"] == "NG"]
    c = collections.Counter(vtype(r) for r in inc)
    w(f"| {f} | {sum(1 for r in neg if r['res'][f]['cat'] != 'NG')} | {len(inc)} | {c['T1']} | {c['T2']} | {c['T3']} | {c['OTHER']} | {len(reg)} |")
w("")
w("**R-3(事後再分類の明記)**: 事前登録(PREREGISTERED_01/02)では『増分誤PASS』を型に関わらず全て誤PASSとして数えた(Phase 1 M4=増分11[T1 6+T2 2+T3 3]、Phase 2 L1+L2+L3=増分8[T1 6+T2 2、T3はL1ガードで0])。T1(音素列が原稿と同一=ASRテキストから区別不能)を『by-design』と分類し直したのは**事後**である。今回の数字は、事前登録どおりの数え方(全増分=誤PASS)で: R-1 OFF=8(Phase 2と一致)、R-1 ON=1。T1を区別不能としてby-design扱いにした場合の『設計外増分』は R-1 OFF=2(T2のみ)、R-1 ON=1(T2のみ)。")
w("")
for f in (ON, OFF):
    w(f"### 4a. 増分誤PASSの全列挙({f})")
    w("| 型 | 群 | シナリオ | 原稿 | Primary | Secondary | 経路 |")
    w("|---|---|---|---|---|---|---|")
    for r in INC[f]:
        w(f"| {vtype(r)} | {r['group']} | {r['scenario']} | {r['canon'][:30]} | {r['primary'][:34]} | {(r['secondary'] or '-')[:30]} | {r['res'][f]['route'][:60]} |")
    w("")
posr = [r for r in rows if r["truth"] == "POS"]
unl = [r for r in rows if r["truth"] == "UNL"]
w("### 4b. 対照(POS 正例のコーパス行・UNL 真値不明)のPASS系件数")
w("| 構成 | POS行(" + str(len(posr)) + ") PASS系 | うちL0に対する増分 | UNL行(" + str(len(unl)) + ") PASS系 |")
w("|---|---|---|---|")
for f in CF:
    n = sum(1 for r in posr if r["res"][f]["cat"] != "NG")
    n0 = sum(1 for r in posr if r["res"]["L0"]["cat"] != "NG")
    w(f"| {f} | {n} | +{n - n0} | {sum(1 for r in unl if r['res'][f]['cat'] != 'NG')} |")
w("")
w("### 4c. 負例の群別 総誤PASS(L0 → 主設定 → R-1 OFF)")
w("| group | n | L0 | " + ON + " | " + OFF + " |")
w("|---|---|---|---|---|")
for g in sorted({r["group"] for r in neg}):
    rs = [r for r in neg if r["group"] == g]
    w(f"| {g} | {len(rs)} | {sum(1 for r in rs if r['res']['L0']['cat'] != 'NG')} | {sum(1 for r in rs if r['res'][ON]['cat'] != 'NG')} | {sum(1 for r in rs if r['res'][OFF]['cat'] != 'NG')} |")
w("")
# ---------------- 5. N3 ----------------
n3 = d["n3"]
w("## 5. N3負例(30 wav、意図的誤読TTS=真値NEG)× 5 draw(記録済み1+新4)での再試行の誤PASS")
w("Azure=保存転写(real)、またはSecondary=原稿そのもの(S_canon=最悪露出)。セルは『PASS系率(組合せ平均)』。再試行起因=同じfirst drawでN=1はNGなのにN=2/3の合意でPASS系になった組合せ。")
w("| シナリオ | 構成 | N=1 PASS系率 | 合意N=2 | 合意N=3 | BoN N=2 | BoN N=3 | 再試行発火組合せ(N=2/3) | 合意の再試行起因PASS(N=2/3) | BoNの再試行起因PASS(N=2/3) | 早期HR組合せ(N=2/3) |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
agg = {}
for scn in ("real", "S_canon"):
    for fn in ("L0", ON, OFF):
        a = collections.defaultdict(int)
        for cid, e in n3.items():
            for n in (1, 2, 3):
                v = e["scn"][f"{scn}|{fn}|N{n}"]
                a[f"tot{n}"] += v["n_combos"]
                a[f"ps{n}"] += sum(v["cats"].get(k, 0) for k in PASSCAT)
                a[f"bps{n}"] += sum(v["bon"].get(k, 0) for k in PASSCAT)
                a[f"fired{n}"] += v["retry_fired"]
                a[f"ri{n}"] += len(v["retry_induced_pass"])
                a[f"bi{n}"] += len(v["bon_induced_pass"])
                a[f"hr{n}"] += len(v["hr_combos"])
        agg[(scn, fn)] = a
        w(f"| {scn} | {fn} | {a['ps1']}/{a['tot1']}({pct(a['ps1'], a['tot1'])}) | {a['ps2']}/{a['tot2']}({pct(a['ps2'], a['tot2'])}) | {a['ps3']}/{a['tot3']}({pct(a['ps3'], a['tot3'])}) | {a['bps2']}/{a['tot2']}({pct(a['bps2'], a['tot2'])}) | {a['bps3']}/{a['tot3']}({pct(a['bps3'], a['tot3'])}) | {a['fired2']}/{a['fired3']} | {a['ri2']}/{a['ri3']} | {a['bi2']}/{a['bi3']} | {a['hr2']}/{a['hr3']} |")
w("")
cl = {}
for scn in ("real", "S_canon"):
    for fn in (ON, OFF):
        cl[(scn, fn)] = sum(1 for e in n3.values() if any(e["scn"][f"{scn}|{fn}|N{n}"]["retry_fired"] for n in (2, 3)))
w("### 5a. 再試行起因誤PASS 0 の統計的意味")
for scn in ("real", "S_canon"):
    for fn in (ON, OFF):
        n_clip = cl[(scn, fn)]
        a = agg[(scn, fn)]
        w(f"- {scn} / {fn}: 再試行が1回でも発火したclip={n_clip}/30 → clip単位の誤PASS 0/{n_clip}の95%上限(Clopper-Pearson)={100 * cp_upper(n_clip):.1f}%。組合せ単位(従属)は 0/{a['fired2'] + a['fired3']} で{100 * cp_upper(a['fired2'] + a['fired3']):.2f}%だが、同一clipのdraw間は独立でないため参考値。")
w("- **限界**: 真値NEGとして使える保存wavはN3の30本(うちL0でNGの約16本)のみ。95%上限は大きい誤PASS増加しか否定できない(Opus指摘どおり)。人間NG判定済みの実誤読wavの台帳は他に存在せず(PREREGISTERED_03 §3の探索範囲)、母集団拡大は既知誤値TTS入力の追加生成=TTS呼出が必要で本委任の範囲外(判断候補)。")
w("")
w("### 5b. N3でBoN(参考)が釣る例(N=3、real、R-1 OFF構成)")
fish = []
for cid, e in n3.items():
    v = e["scn"][f"real|{OFF}|N3"]
    if v["bon_induced_pass"]:
        fish.append((cid, len(v["bon_induced_pass"]), e["type"], e["tts_input"]))
for cid, k, ty, tt in fish[:12]:
    w(f"- {cid} ({ty}, TTS入力=`{tt}`): BoN再試行起因PASS {k}組合せ。合意規則では0。")
w("")
# ---------------- 6. 独立性 ----------------
w("## 6. draw独立性と時刻依存(P-5)")
w("| 対象 | wav数 | draw/wav | 異なる転写数(平均) | 同一転写のみ(全draw同一)のwav |")
w("|---|---|---|---|---|")
dd = [len(set(e["draws"])) for e in n3.values()]
dn = [len(set(e["draws"][1:])) for e in n3.values()]
w(f"| N3(記録済み1+新4) | 30 | 5 | {sum(dd) / 30:.2f} | {sum(1 for x in dd if x == 1)} |")
w(f"| N3(新4 drawのみ) | 30 | 4 | {sum(dn) / 30:.2f} | {sum(1 for x in dn if x == 1)} |")
for nm, es in (("6音声", pos), ("拡張4wav", d["pos_ext"])):
    ds = [len(set(e["draws"])) for e in es]
    w(f"| {nm} | {len(es)} | {'4〜5' if nm == '6音声' else '5'} | {sum(ds) / len(ds):.2f} | {sum(1 for x in ds if x == 1)} |")
st_in = sum(1 for e in n3.values() if e["draws"][0] in e["draws"][1:])
new_in = sum(1 for e in n3.values() for i in range(1, 5) if e["draws"][i] in (e["draws"][1:i] + e["draws"][i + 1:]))
r_st, r_new = st_in / 30, new_in / 120
w(f"- 時刻依存の検査(N3): 記録済み(Phase 3、別日の呼出)の転写が新4 drawのいずれかと一致するclip={st_in}/30({100 * r_st:.0f}%)、新draw1本が他の新drawのいずれかと一致する率={new_in}/120({100 * r_new:.0f}%)。差は{100 * abs(r_st - r_new):.0f}ポイントで、記録済みが新draw同士より特に食い違う(=モデル更新等の時刻依存)証拠は無い(n=30、断定はしない)。draw単位の揺らぎが主。新draw取得時刻: {min(min(e['ts']) for e in n3.values())} 〜 {max(max(e['ts']) for e in n3.values())}(約80秒内)。記録済みdrawの呼出時刻はusage_logに無い。")
dist_ms = [(p["run"], p["attempt"], len(set(p["draws"])), len(p["draws"])) for p in pos]
w("- 6音声のdraw多様性(異なる転写数/draw数): " + ", ".join(f"{r} a{a}: {x}/{y}" for r, a, x, y in dist_ms) + "。")
w("- 参考(Opus指摘): ms_03 a2 は再転写3本が同一(月の島は千九百本超)=draw独立性は限定的。再現性メタデータ(モデルID・時刻・draw順)は redraw_03.json / n3_redraw_02.json に保存。")
w("")
# ---------------- 7. 拡張4wav / Y-Preview ----------------
w("## 7. 正例拡張4wav(人間承認済みの日本語a2 attempt、新規4 draw+記録済み1)とY/Preview型")
w("| wav | 長さ | Azure保存転写 | draw別 判定(L0 / " + ON + " / " + OFF + ") |")
w("|---|---|---|---|")
for e in d["pos_ext"]:
    ds = " ; ".join(f"{x['tag']}:{LBL[x['res']['L0']['cat']]}/{LBL[x['res'][ON]['cat']]}/{LBL[x['res'][OFF]['cat']]}" for x in e["per_draw"])
    w(f"| {e['run']}/{e['seg']} (sha {e['sha16']}、同sha: {','.join(e['same_sha_as']) or '-'}) | {e['dur_s']}s | {'あり' if e['azure'] else 'なし(P_only)'} | {ds} |")
w("")
for e in d["pos_ext"]:
    w(f"- **{e['run']}/{e['seg']}**: 原稿 `{e['canonical'][:60]}…` / draws: " + " | ".join(f"{x['tag']}=`{x['text'][:40]}…`" for x in e["per_draw"][:3]) + f" / 合意N=3(R-1 OFF)分布={dist_cell(e['cons'][f'{OFF}|N3'])}。")
w("")
ypc = [e for e in d["pos_ext"] if e["seg"] == "preview"]
w("### 7a. Y/Preview型『思いどおり↔思い通り』: 案R(i)は効くか(P-6)")
for e in ypc:
    for x in e["per_draw"]:
        if "思い通り" in x["text"]:
            import er007_ja_asr_validator_01 as javal
            cls = javal.classify_ja_asr_match(e["canonical"], x["text"], expected_readings=None, allow_reading_resolver=False)
            r = P.pron_value_equivalence(e["canonical"], x["text"], side="primary")
            w(f"- {e['run']}/{e['seg']} {x['tag']}: Production分類=`{cls.classification}`(理由: {cls.reason[:60]})。v2判定 equal={r.equal} why=`{r.why}`。最終(Secondary未保存のstub): L0={LBL[x['res']['L0']['cat']]} / {ON}={LBL[x['res'][ON]['cat']]}。")
            break
w("- 結論: Production既存のVariant Layerは『濁点の有無を除き読みが一致』をCascade対象(ASR_VALIDATION_UNCERTAIN)に分類済みで、案R(i)のv2は**そもそも発火しない**(not_tcm)。判定は Secondary(Azure)が原稿と同じ『思いどおり』を返すか次第(返せば既存の secondary_confirmed=PASS_W(既存)、返さなければ NG_BOTH)。Y/Previewの保存attemptにはAzure転写が無く、ここでは実結果を再現できない(Azure 0)。つまり案R(i)はこの型には**効かない/不要**で、救うには清濁を許容する比較(連濁)が要る=er008冒頭の『ころ/ごろ』問題と同じ危険があるため**別ID・別Opusレビュー**(OPEN新規(a)、分類=修正へ進む)。月題以外の実在誤NGで『案R(i)が効かない』ことの実証(R-5、検証のみ本Phase)。run_01 previewは5 draw中1本(draw4)が原稿と同表記(思いどおり)でProduction既存のPASSになった=draw揺らぎの実例。")
w("- mey_02 comment_2(固有名詞タイフーン機↔台風機/台風期): 全draw・全構成でNG(OOV同音。案Rの対象外=OPEN-498/PN系)。Z melos comment_1(三日間↔3日間): M-1ガード(不規則読み)でL1が不適用、L0で既にPASS_W(既存、`JA_NUMERIC_IRREGULAR_READING`警告)。")
w("")
# ---------------- 8. L3 ----------------
w("## 8. M-5 別表L3(送り仮名省略形の訓読み)の検証")
for g in ("L3_POS", "L3_NEG"):
    rs = [r for r in rows if r["group"] == g]
    for f in ("L0", ON):
        c = collections.Counter((r["scenario"], LBL[r["res"][f]["cat"]]) for r in rs)
        w(f"- {g} {f}: " + ", ".join(f"{k[0]}={k[1]}:{v}" for k, v in sorted(c.items())))
incl3 = [r for r in rows if r["group"] == "L3_NEG" and r["res"][ON]["cat"] != "NG" and r["res"]["L0"]["cat"] == "NG"]
w(f"- L3_NEG 増分誤PASS={len(incl3)}(目標0)。L3_POS PS_same(両engine揃い)で救済: " + str(sum(1 for r in rows if r['group'] == 'L3_POS' and r['scenario'] == 'PS_same' and r['res'][ON]['cat'] == 'PASS_W_NEW')) + "/" + str(sum(1 for r in rows if r['group'] == 'L3_POS' and r['scenario'] == 'PS_same')) + "。救済されない2件=『月野詩は+超え』『月野市は+越え』(発音同一との併用は残差0文字でないため不可。Phase 2のL3より意図的に狭い)。S_canon(Secondary=原稿)はL0が既にPASS_W(既存)でL3は寄与なし。P_only(Secondary無し)は発火しない。")
w("- 汎用辞書 `er008_asr_variant_hardening_15_ja_kanji_readings.py` は不変(test: `reading_candidates_for_span('超')` に『こえ』が無い)。別表は `proto_unified_03.KUNYOMI_OKURIGANA` のみ。")
w("")
# ---------------- 9. ガード ----------------
w("## 9. ガードの効果(M-1/M-6/R-1/R-2)")
bl = [r for r in rows if r["res"][ON]["blocked"]]
w(f"- M-6(E3/E4非空で全新層不適用): コーパス{len(rows)}行中 {len(bl)}行がブロック(E3由来。E4由来は0。群: " + ", ".join(f"{k}:{v}" for k, v in collections.Counter(r['group'] for r in bl).most_common(6)) + ")。ブロック行はL0と同一結果(test固定)。")
w("- M-1(不規則読み): 両側・PRON/VALUE_ONLY両経路でL1不適用。Phase 1 M1で誤PASSだった『一日中→ついたち中』3行はNG(L1⊇L0)。")
r1e = [r for r in rows if r["res"][OFF]["cat"] != "NG" and r["res"][ON]["cat"] == "NG"]
w(f"- R-1の効果(R-1 OFF→ON で PASS系→NG になる行): 全体{len(r1e)}行。内訳 truth=" + ", ".join(f"{k}:{v}" for k, v in collections.Counter(r['truth'] for r in r1e).items()) + "。")
w("- R-1の副作用(重要): 6音声の正例で R-1 ON は ms_03 a2・a3、reselect a1・a2 の4本すべてをNGに戻す(§1)。『月の詩は/死は/氏は/野氏は』の漢字(詩・死・氏・野)が複数の読み候補を持つため。これは負例T1(同音異表記便乗)6件を消す効果と**同じ性質の裏表**(区別不能な同音を受理する/しない)。")
w("- R-2: `ENGINE_reading_difference` 経路は除外(コーパスで発火0=Opus確認どおり)。")
w("")
# ---------------- 10. run単位 ----------------
w("## 10. run単位の実益(参考): 完走までのattempt数・再生成・HR")
w("| run | 構成 | N | 完走/終端 | attempt別判定 | 追加OpenAI draw |")
w("|---|---|---|---|---|---|")
rl = d["run_level"]
for run in ("run_ms_03", "run_reselect_01"):
    w(f"| {run} | L0 | - | 未完走(全attempt NG→既存HR Lock) | " + ", ".join(f"a{x['attempt']}:{LBL[x['cat']]}" for x in rl[f"{run}|L0"]["seq"]) + " | 0 |")
    for fn in (ON, OFF):
        for n in (1, 2, 3):
            v = rl[f"{run}|{fn}|N{n}"]
            dn_ = v["done_at"]
            w(f"| {run} | {fn} | {n} | {'attempt' + str(dn_) + 'で完走' if isinstance(dn_, int) else (dn_ or '未完走(全attempt NG→既存HR Lock)')} | " + ", ".join(f"a{x['attempt']}:{LBL[x['cat']]}" for x in v["seq"]) + f" | {v['extra_openai_draws']} |")
w("")
# ---------------- 11. 残NGとHR ----------------
w("## 11. 残NG 2本の扱い(新状態は作らない=R-4)")
w("残る ms_03 a1・reselect a3 は、安全条件を保つと機械判定で確定できない(a1: 記録済みOpenAIは『月野詩は8000句800本超え』、Azureは『月野市は8900本越え』で、詩/市の食い違いと値garble『8000句800』[explain_garble対象外]があり、別表L3が要求する「両engineとも置換後に原稿と残差0文字」を満たさない/a3: 5 drawのうち『スギノ』『杉の』『月の死は発生900』等、値以外の内容が原稿と食い違うdrawが多数で、PASSできる1本は少数派の釣りになるため合意規則はHR)。扱い=既存の流れそのまま: ASR NG→TTS再生成(上限内)→尽きたらSTOPPED→Human Review Lock(`human_review_queue.jsonl`)→ユーザー試聴で聴取OKなら `record_human_approval(out_dir, segment_key, canonical_text[=元の原稿])` を呼んでsha単位の個別採用→`verify_episode_audio_validation_gate` が HUMAN_APPROVED を許可(Assemblyへ進めるのはVALIDATED/HUMAN_APPROVEDのみ)。今回ユーザーはこの6音声を既に試聴OK済み(ms_03 a2は個別採用済み)。新しい『条件付きPASS』状態は作らない。再試行合意が早期HRを出す条件はエンジン間の内容矛盾のみ(ローカルWhisperの証言は添付情報に留め、機械PASSの根拠にしない)。API 0。")
w("")
# ---------------- 12. 合格条件 ----------------
w("## 12. 6合格条件(ユーザー原文§6)への到達度とStatus候補(最終判定はFable)")
n_on = cnt[ON]
n_off = cnt[OFF]
w("| 条件 | 到達度 | 根拠 |")
w("|---|---|---|")
w(f"| 1. Human OKの6音声すべて最終判定でPASS | **未達**: 機械判定の上限は R-1 OFF {n_off}/6 (PASS_W(新方式)/既存PASS_W)、R-1 ON(Opus R-1採用の主設定) {n_on}/6。clean PASSは0/6。残りはHR Lock→個別採用(HUMAN_APPROVED)が必要 | §1 |")
w("| 2. 既知の実誤読・負例を誤PASSしない | **部分**: 回帰0・OTHER=0。R-1 ON は増分1(T2)、R-1 OFF は増分8(T1 6=区別不能な同音異表記便乗、T2 2)。N3での再試行起因誤PASS 0(分母が小さい=上限は§5a) | §4・§5 |")
w("| 3. 『月のしわ』固有の例外でない | **達成** | atom位置・別表・合意規則はいずれも題固有語なし。汎用題(100人超/1,200円超)で別表L3救済、負例増分0 | §8 |")
w("| 4. X/Y/Zの対象範囲・既存仕様影響 | **達成(評価済み)** | Family×Level×Section影響範囲はEVAL_01 §5を継承(AdvにJA音声なし)。拡張4wavで X(mey)/Z(melos)/Y(preview)を実測。M-6でE3/E4と干渉しない構造 | §7 |")
w("| 5. retry/fallback/resume/再判定整合 | **部分(設計達成・配線未)**: 合意再試行は承認済み仕様『同一音声ASR再試行廃止』の変更を伴う(D-1)。保存drawのみから再現(R-7 test)、flag OFF/scope外を先にblock、Azure再試行なし、COST_GUARD計上は設計案に残置(未配線) | proto test 48件 |")
w("| 6. 実行費用・量産単価 | **達成(区間提示)** | §13 |")
w("")
w("### Status候補: **USER_DECISION_REQUIRED**(VALIDATEDにしない)")
w("- 理由: 条件1が未達(機械上限 R-1 OFF 4/6[PASS_W+試聴]、R-1 ON 0/6)。ユーザー§6『安全基準を緩めて6本を通さない』に従うと、残りは人間承認が必須。ユーザー判断事項: D-1(ASR再試行=承認済み仕様の変更、6本への効果0本)、D-2(超→こえ等の意味等価な非標準読みの受理)、D-3(新方式PASS_Wを事後試聴か公開前試聴必須か)、D-4(HUMAN_APPROVEDを『最終判定PASS』に数えるか)。")
w("- 新規の事実(Opusレビュー採用後に判明): **R-1(漢字1字ごとのC2検査)を採用すると、案R(i)は6本のうち1本も救済しない**(§1・§9)。R-1は『ASRが書いた漢字に他の読みがあるなら、TTSが別の読みで読んだ可能性を排除できない』という安全側の検査で、それ自体は妥当。しかし本件の誤NGの原因である『しわ→詩は/死は/氏は/野氏は』型の同音異表記はすべて該当する。R-1 ONでは誤NG救済をほぼ諦める、R-1 OFFでは負例T1(区別不能な同音異表記便乗)6件を新層が受理する、というトレードオフ。参考事実: Production現行(L0)は既に『本帳/本蝶/本調/本町/本鳥』等の同音異表記(読み一致)を PS_same で PASS にしている(§8のL3_NEG E4/C2同形異音 11行がL0でPASS)=R-1 ONは現行Productionより新層の方が厳しい。これは品質基準の選択(判断候補D-5: 区別不能な同音異表記をどこまで受理するか。分類=D真に新しい判断)であり、私は決めない。")
w("- REJECTEDにしない理由: 回帰0・OTHER増分0・汎用性達成・費用は軽微・合意規則の再試行起因誤PASS 0。")
w("")
# ---------------- 13. 単価 ----------------
w("## 13. 費用・単価")
w("- 本Phase 3の実費: 正例拡張4wav×4draw=OpenAI 16呼出(cost_log: input 2,488 tok / output 1,110 tok)。公表単価[$1.25/$5 per Mtok, ¥150/$]で約¥1.3、分課金[$0.003/min×249秒]で約¥1.9。請求明細は未取得=推定。見積(BUDGET_PLAN_03)¥1.9以内。Azure/TTS 0。負例追加drawなし(N3既出を再利用)。")
w("- 単価への影響(採用した場合): 層L1〜L3は判定ロジックのみ(追加API 0)。Secondary未呼出でβ/L3が発火するときだけAzure追加呼出(約¥0.3/clip)。合意再試行はOpenAI 1本あたり約¥0.01(短題)〜¥0.1(15秒級)で、force_secondaryでもAzureはsha cacheに当たり追加0。6音声への新規PASS追加は0本のため、再生成削減(¥0.92/clip)の効果は『一般的なdrawノイズによる再生成の削減』に限られ、実測は未確認(現行の誤NG率データなし)。70円/記事セット目標に対する影響は軽微(≪1%)で、誤NG率が未知のため区間は『削減0〜¥1.8/記事(月題級の再生成を1〜2回回避した場合)』のまま。")
open(OUT + "EVAL_UNIFIED_03.md", "w", encoding="utf-8", newline="\n").write("\n".join(o) + "\n")
print("written", len(o), "lines")
