# eval_unified_01.out.json -> EVAL_UNIFIED_01.md (決定的。API 0)。再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/render_eval_unified_01.py
import collections, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import er078_asr_value_guard_01 as vg
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
d = json.load(open(OUT + "eval_unified_01.out.json", encoding="utf8"))
Ms = ["M0", "M1", "M2", "M3", "M4"]
L = []
def w(*a): L.append(" ".join(str(x) for x in a))
def esc(s): return (s or "-").replace("|", "\\|")

w("# EVAL_UNIFIED_01(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01B。eval_unified_01.py の出力から自動生成。API 0・費用0円)")
w("事前登録=PREREGISTERED_01.md。Production HEAD 定数:", json.dumps(d["head_consts"]), "。PASS_W=警告付きPASS(判定器のPASS_WITH_WARNING、または新方式[v2発音救済・β]経由=試聴必須)。PASSと別集計。")
w("方式: M0=現行Production最終判定 / M1=v2(Primary+Secondary値等価層) / M2=M0+β / M3=P-1(M1の部分集合: 助詞は→わ/へ→え救済のみ) / M4=M1+β。M5(再転写best-of-N)は§2dに集計。\n")

w("## 1. 6音声の転写全文(保存済み全転写。wav sha256先頭16桁で紐付け)")
for p in d["positives"]:
    w(f"### {p['run']} attempt{p['attempt']}  sha256={p['sha16']}…  `{p['wav'].split('narration/')[1]}`")
    w("| engine | 出所 | 転写 |\n|---|---|---|")
    for t, x in p["openai"]: w(f"| OpenAI(gpt-4o-mini-transcribe) | {t} | {esc(x)} |")
    for t, x in p["azure"]: w(f"| Azure | {t} | {esc(x)} |")
    for k, x in sorted(p["whisper_local"].items()): w(f"| ローカルWhisper(参考・判定不使用) | {k} | {esc(x)} |")
    w("")

w("## 2a. 6音声×方式: 最終Gate結果(決定対=当時記録のOpenAI転写 × 当該wavのAzure転写)")
w("| 音声 | M0 現行Production | M1 v2 | M2 β | M3 P-1 | M4 v2+β | 決定条件(M4の経路 / M0のNG理由) |\n|---|---|---|---|---|---|---|")
for p in d["positives"]:
    q = [x for x in p["pairs"] if x["stored"]][0]
    r = q["res"]
    w(f"| {p['run']} a{p['attempt']} | " + " | ".join(f"{r[m]['cat']}" for m in Ms) + f" | M4={esc(r['M4']['route'])} / M0={esc(r['M0']['reason'])} |")
w("\n決定対のOpenAI/Azure: ")
for p in d["positives"]:
    q = [x for x in p["pairs"] if x["stored"]][0]
    w(f"- {p['run']} a{p['attempt']}: OpenAI=`{q['openai']}` / Azure=`{q['azure']}`")
n_pw = {m: sum(1 for p in d["positives"] if [x for x in p["pairs"] if x["stored"]][0]["res"][m]["cat"] == "PASS_W") for m in Ms}
n_p = {m: sum(1 for p in d["positives"] if [x for x in p["pairs"] if x["stored"]][0]["res"][m]["cat"] == "PASS") for m in Ms}
w("\n決定対の集計(6音声): " + " / ".join(f"{m}: PASS={n_p[m]} PASS_W={n_pw[m]} NG={6-n_p[m]-n_pw[m]}" for m in Ms))

w("\n## 2b. 同一wavの転写変動(draw集合): OpenAI draw × Azure(2種以上あれば全て)の判定分布")
w("| 音声 | OpenAI draw数 / 異なる転写数 | 値が正しい転写(値ガードEQUAL) | Azure転写数(異なる) | 判定対数 | " + " | ".join(f"{m} PASS+PASS_W" for m in Ms) + " | Primary単独(Azure不呼出) M0/M1 |\n|---|---|---|---|---|" + "---|" * 6)
for p in d["positives"]:
    ot = [x for _, x in p["openai"]]
    vok = sum(1 for x in ot if vg.value_guard(MOON, x, "ja").kind == vg.EQUAL)
    prs = [x for x in p["pairs"] if not x.get("p_only")]
    po = [x for x in p["pairs"] if x.get("p_only")]
    cnt = {m: sum(1 for x in prs if x["res"][m]["cat"] != "NG") for m in Ms}
    po0 = sum(1 for x in po if x["res"]["M0"]["cat"] != "NG"); po1 = sum(1 for x in po if x["res"]["M1"]["cat"] != "NG")
    w(f"| {p['run']} a{p['attempt']} | {len(ot)} / {len(set(ot))} | {vok}/{len(ot)} | {len(set(x for _, x in p['azure']))} | {len(prs)} | " + " | ".join(f"{cnt[m]}/{len(prs)}" for m in Ms) + f" | {po0}/{len(po)} , {po1}/{len(po)} |")

w("\n## 2c. 6音声×方式×全draw対の判定(全行)")
w("| 音声 | OpenAI(出所) | Azure(出所) | " + " | ".join(Ms) + " | M0 NG理由 | M4経路 |\n|---|---|---|---|---|---|---|---|---|---|")
for p in d["positives"]:
    for x in p["pairs"]:
        if x.get("p_only"): continue
        r = x["res"]
        w(f"| {p['run'][4:]} a{p['attempt']} | {x['openai_tag']}: {esc(x['openai'])} | {x['azure_tag']}: {esc(x['azure'])} | " + " | ".join(r[m]["cat"] for m in Ms) + f" | {esc(r['M0']['reason'])} | {esc(r['M4']['route'])} |")

w("\n## 2d. M5 判定前のASR再試行(best-of-N): 同一wavのOpenAI draw をN本まで許し、いずれか1本でPASS(+PASS_W)ならPASS扱い(決定対のAzure固定)")
w("| 音声 | draws | M0 best-of-N | M4 best-of-N | M4 draw別(上から順) |\n|---|---|---|---|---|")
for p in d["positives"]:
    az0 = p["azure"][0][0]
    xs = [x for x in p["pairs"] if not x.get("p_only") and x["azure_tag"] == az0]
    b0 = any(x["res"]["M0"]["cat"] != "NG" for x in xs); b4 = any(x["res"]["M4"]["cat"] != "NG" for x in xs)
    w(f"| {p['run'][4:]} a{p['attempt']} | {len(xs)} | {'PASS' if b0 else 'NG'} | {'PASS_W' if b4 else 'NG'} | {''.join('o' if x['res']['M4']['cat'] != 'NG' else '.' for x in xs)} |")
w("\n注: 負例側のbest-of-N誤PASSは実測不能(再転写が無い)。理論上、同一wavへのN回再転写でいずれか1本が誤PASSすれば誤PASSになる=誤PASS率は最大N倍(各draw独立でない場合は小さい)。設計案で扱う。")

# ---- 負例 ----
rows = d["rows"]
w("\n## 3. 負例・対照の誤PASS件数(群×シナリオ×方式。PASS/PASS_W別。増分=M0がNG→当該方式がPASS/PASS_W)")
w("真値 NEG=誤PASSしてはならない / POS=救済されうる対照 / UNL=真値不明(増分は列挙して個別審査、誤PASS率に算入しない)")
agg = collections.OrderedDict()
for r in rows:
    k = (r["truth"], r["group"], r["scenario"])
    a = agg.setdefault(k, collections.Counter()); a["n"] += 1
    for m in Ms:
        c = r["res"][m]["cat"]
        if c != "NG": a[m + "|" + c] += 1
        if c != "NG" and r["res"]["M0"]["cat"] == "NG": a[m + "|inc"] += 1
        if c == "NG" and r["res"]["M0"]["cat"] != "NG": a[m + "|REG"] += 1
w("| 真値 | 群 | シナリオ | n | " + " | ".join(f"{m} PASS/PASS_W (増分)" for m in Ms) + " |\n|---|---|---|---|" + "---|" * 5)
for k, a in sorted(agg.items()):
    w(f"| {k[0]} | {k[1]} | {k[2]} | {a['n']} | " + " | ".join(f"{a[m+'|PASS']}/{a[m+'|PASS_W']} (+{a[m+'|inc']})" for m in Ms) + " |")
tot = {m: collections.Counter() for m in Ms}
for r in rows:
    for m in Ms:
        c = r["res"][m]["cat"]
        if r["truth"] == "NEG":
            if c != "NG": tot[m]["fp"] += 1
            if c != "NG" and r["res"]["M0"]["cat"] == "NG": tot[m]["inc"] += 1
        if c == "NG" and r["res"]["M0"]["cat"] != "NG": tot[m]["reg"] += 1
w("\nNEG全体(全シナリオ合算 " + str(sum(1 for r in rows if r['truth'] == 'NEG')) + "行): " + " / ".join(f"{m}: 誤PASS={tot[m]['fp']} 増分={tot[m]['inc']} 回帰(M0 PASS→NG)={tot[m]['reg']}" for m in Ms))
w("\n### 3a. 増分(M0がNGで、いずれかの方式がPASS/PASS_Wにした行)の全件(NEG/UNL。POS対照は§3c)")
w("| 真値 | 群 | シナリオ | 原稿 | Primary | Secondary | 増分を出した方式 | 経路 | 分類(事後) |\n|---|---|---|---|---|---|---|---|---|")
def cls_inc(r, ms):
    rt = r["res"][ms[0]]["route"]
    if rt.startswith("beta_composite"): return "β: 数値garble断片(Secondaryが原稿値を返した場合のみ)=設計対象型"
    if "v2_pron" in rt and ("詩は" in r["primary"] or "死は" in r["primary"] or "氏は" in r["primary"] or "野氏は" in r["primary"] or r["primary"] == "月の詩は"): return "v2: 音素列が原稿と同一(ツキノシワ)=ASRテキストから区別不能な同音(by-design)"
    if "IRREGULAR" in rt: return "v2層のVALUE_ONLY経路が不規則読み(一日→ついたち)をwarning付きで受理(Production既存のwarning挙動と同系)"
    return "要審査"
for r in rows:
    ms = [m for m in Ms[1:] if r["res"][m]["cat"] != "NG" and r["res"]["M0"]["cat"] == "NG"]
    if ms and r["truth"] != "POS":
        w(f"| {r['truth']} | {r['group']} | {r['scenario']} | {esc(r['canon'][:30])} | {esc(r['primary'][:34])} | {esc((r['secondary'] or '')[:22])} | {','.join(ms)} | {esc(r['res'][ms[0]]['route'][:60])} | {cls_inc(r, ms)} |")
w("\n### 3b. 既存Production(M0)の誤PASS(NEG・S_canon以外=Primary/両エンジン同一誤り)=新方式と無関係の基準線")
base = collections.Counter(); ex = collections.defaultdict(list)
for r in rows:
    if r["truth"] == "NEG" and r["scenario"] != "S_canon" and r["res"]["M0"]["cat"] != "NG":
        key = (r["group"], r["scenario"], r["res"]["M0"]["cat"]); base[key] += 1
        if len(ex[key]) < 2: ex[key].append(f"{r['canon'][:14]}→{r['primary'][:14]}")
w("| 群 | シナリオ | M0カテゴリ | 件 | 例 |\n|---|---|---|---|---|")
for k in sorted(base): w(f"| {k[0]} | {k[1]} | {k[2]} | {base[k]} | {esc('; '.join(ex[k]))} |")
w("\n(上の基準線は『原稿とASR転写の表層が同一または既存規則で等価』なため機械では区別不能な型[同形異音・助詞誤読・桁区切り] と BLIGHT value_wrong:S_only[Primaryが原稿通りでSecondaryだけ誤り=either-engine設計]。方式による増減なし。)")
w("\n### 3c. POS対照(救済されうる正例): M0がNGで救済された件と回帰")
for r in rows:
    if r["truth"] == "POS":
        ms = [m for m in Ms[1:] if r["res"][m]["cat"] != "NG" and r["res"]["M0"]["cat"] == "NG"]
        if ms: w(f"- 救済: {r['group']}/{r['scenario']} {r['canon'][:24]} | {r['primary'][:28]} → {','.join(ms)} ({r['res'][ms[0]]['route'][:50]})")
w("- POS回帰(M0 PASS→NG)件数: " + str(sum(1 for r in rows if r["truth"] == "POS" for m in Ms if r["res"][m]["cat"] == "NG" and r["res"]["M0"]["cat"] != "NG")))
w("- 全行の回帰(M0 PASS/PASS_W→NG)件数: " + str(sum(1 for r in rows for m in Ms if r["res"][m]["cat"] == "NG" and r["res"]["M0"]["cat"] != "NG")) + " (M1⊇M0, M3⊇M0, M2⊇M0, M4⊇M1 の確認)")

w("\n## 4. §4-3 の6分類の被覆(各分類>=3件のテキスト負例。UC6は新規合成、他群と合わせた誤PASS)")
w("| 分類 | 件数(シナリオ別行数) | M0誤PASS | M4誤PASS | M4増分 |\n|---|---|---|---|---|")
for cat in sorted(set(r["group"] for r in rows if r["group"].startswith("UC6_"))):
    rr = [r for r in rows if r["group"] == cat]
    w(f"| {cat[4:]} | {len({r['canon']+r['primary'] for r in rr})}件×{len({r['scenario'] for r in rr})}シナリオ | {sum(1 for r in rr if r['res']['M0']['cat']!='NG')} | {sum(1 for r in rr if r['res']['M4']['cat']!='NG')} | {sum(1 for r in rr if r['res']['M4']['cat']!='NG' and r['res']['M0']['cat']=='NG')} |")
w("(S_canonシナリオ[Secondary=原稿]のM0 PASS_Wは『either-engine: Secondaryが原稿と完全一致なら受理』の既存設計。P_only/PS_same[両エンジン同じ誤り]が実際の誤PASSの評価面。)")
w("U1-U6の P_only/PS_same で M0 が PASS となるのは『橋→箸』『今日→京』=表層差が同音の同形異音(機械では区別不能・基準線)のみ。値/助数詞/脱落/意味変化の誤りはM0・M4とも誤PASS 0。")

w("\n## 5. X/Y/Z Standard 日本語音声の適用範囲(ja_asr_wiring_matrix_scan_01.out.json 再利用)")
m = json.load(open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_asr_wiring_matrix_scan_01.out.json", encoding="utf8"))
w("| Family | Level | Section | JA segment数 | R5 telemetry付き | NG_BOTH | PASS | PASS_WITH_WARNING |\n|---|---|---|---|---|---|---|---|")
for k in sorted(m):
    f, lv, sc = k.split("|"); c = m[k]
    w(f"| {f} | {lv}({'Std' if lv=='a2' else 'Adv'}) | {sc} | {c['n']} | {c.get('r5',0)} | {c.get('state_NG_BOTH',0)} | {c.get('state_PASS',0)} | {c.get('state_PASS_WITH_WARNING',0)} |")
w("\n注: Y/preview は n=5 のうち4件が NG_BOTH(R5付き4件)。本委任の評価対象(月題)とは別の事象で、原因は未調査(OPEN候補として報告)。")
w("\nAdv(b1b)の日本語音声行は0(スキャン対象にb1bを含めたが JA segment が存在しない=実run記録上の除外。Advは英語本文[CURRENT_SPEC.md:838 Natural English Adaptation 等]で日本語音声(題・Preview・Comment・KP日本語意味)を持たない)。")
w("\n## 6. v2・β・P-1 それぞれの効果とリスク(本評価の観測値)")
prs = [x for p in d["positives"] for x in p["pairs"] if not x.get("p_only")]
w(f"- 6音声の全draw×Azure対 {len(prs)} 本の PASS+PASS_W: " + " / ".join(f"{m}={sum(1 for x in prs if x['res'][m]['cat']!='NG')}" for m in Ms) + f"。うち clean PASS(警告なし)= " + " / ".join(f"{m}={sum(1 for x in prs if x['res'][m]['cat']=='PASS')}" for m in Ms))
st_ = [[x for x in p["pairs"] if x["stored"]][0] for p in d["positives"]]
w("- 決定対(stored)の PASS_W: " + " / ".join(f"{m}={sum(1 for x in st_ if x['res'][m]['cat']=='PASS_W')}/6" for m in Ms) + "、clean PASS: すべて0/6(新方式の救済はすべて試聴必須の警告付き)。")
diff13 = sum(1 for r in rows if r["res"]["M1"]["cat"] != r["res"]["M3"]["cat"]) + sum(1 for x in prs if x["res"]["M1"]["cat"] != x["res"]["M3"]["cat"])
w(f"- **P-1(M3)とv2(M1)の差**: 全{len(rows)}行+{len(prs)}正例対で判定が異なる件数={diff13}。本コーパスではv2が余分に出す救済(同形別読み ENGINE_reading_difference / A3_value+pron)は発火せず、v2の実効はほぼP-1(助詞は→わ/へ→え)+桁区切り/値形一致。→ v2とP-1は別方式ではなく **P-1 ⊂ v2** で、評価上は同一機能(二重評価しない)。")
w("- **β(M2)の追加効果**: Primaryの数値garble(8000900/8000句800等の『d×10^k断片+残り』)を、Azureが原稿値を返したときだけ救済(試聴必須)。決定対(stored)でβ固有の増は ms_03 a3 の1本のみ(garble型)。ms_03 a2・reselect a1/a2はβの読み規則=v2読み(Secondary受理経路)による救済でM1と同一。リスク: M0に対するβの増分は、(i)値garble型2行[Secondary=原稿そのもの=最悪露出シナリオのみ]、(ii)音素列が原稿と同一の『詩は/死は+正しい値』3行[PS_same、βがv2読みを内包するため]。両エンジンが同じ値違い・桁違い・助数詞違い・脱落・意味変化を出す場合、片側のみ誤りの場合の増分は0。βは新たにAzure呼出が要る場合がある(p1_value_diffでSecondary未呼出のとき=1clipあたりAzure概算¥0.27〜0.31)。")
w("- **v2(M1)のリスク**: (1) 『月の詩は/死は/氏は/市は + 正しい値』=音素列が原稿と同一のため増分誤PASS扱いの行が出る(事前登録ではNGラベルだったが、音声としては原稿と同一音であり区別不能=by-design。事後分類として開示)。 (2) **真の増分1型**: 『今日は一日中雨→ついたち中雨』(M1/M3/M4)。v2層のVALUE_ONLY経路がPrimary側で不規則読み(一日→ついたち)のガード(V2-1はSecondary側のみ)を持たず、warning付きで受理。Production既存のIRREGULAR_READINGは『一日で→ついたちで』等を既にPASS_Wにする(基準線3b)が、『一日中』は現行NG→新たにPASS_W。実装時はPrimary側にも不規則読みガードを入れて現行判定へフォールバックさせる必要がある(設計案に記載)。")
w("- **共通の限界**: 原稿と表層が同一または既存規則で等価な誤読(橋→箸、今日→京、同形異音、助詞誤読[月はをつきハ等])は、どの方式でもテキストから区別できない(§3b基準線、M0で既に存在)。これは『ASR転写が原稿と同一表記になる音声誤り』であり、ASR Gateの原理的限界(音声の音素列を見ない)。")
open(OUT + "EVAL_UNIFIED_01.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("written", len(L), "lines")
