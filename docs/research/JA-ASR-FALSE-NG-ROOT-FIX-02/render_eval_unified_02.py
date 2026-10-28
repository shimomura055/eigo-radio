# eval_unified_02.out.json から EVAL_UNIFIED_02.md を生成(API 0・決定的)。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/render_eval_unified_02.py
import collections, json, sys
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
d = json.load(open(OUT + "eval_unified_02.out.json", encoding="utf8"))
FLS = ["L0", "L1", "L1+L2", "L1+L3", "L1+L2+L3"]
FIN = "L1+L2+L3"
rows = d["rows"]
o = []
w = o.append


def short(r):
    return r["cat"] + (":" + r["route"][:70] if r["cat"] != "NG" else ":" + str(r["reason"]))


def vtype(r):
    t, g = r["tag"], r["group"]
    if "しわ→詩は" in t or g.startswith("UC6_U6"):
        return "T1_同音異表記便乗(音素列が原稿と同一=区別不能)"
    if "garble" in t:
        return "T2_β値garble(Secondary=原稿そのもの最悪露出)"
    if "不規則読み" in t:
        return "T3_不規則読み(Primary側ガード欠陥)"
    return "OTHER(要不合格開示)"


w("# EVAL_UNIFIED_02(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B。eval_unified_02.py の出力から自動生成。API 0)")
w(f"事前登録=PREREGISTERED_02.md。Production HEAD 定数: {json.dumps(d['head_consts'], ensure_ascii=False)}。Production file sha256(先頭16桁・不変確認): {json.dumps(d['production_sha256'], ensure_ascii=False)}。")
w(f"NEG集合(Phase 1と同一): n={d['neg_set']['n']} sha256={d['neg_set']['sha256']}(事前登録値とassert一致)。L0とPhase 1 M0の行ごと一致: 比較{d['parity']['n_compared']}行・不一致{d['parity']['L0_vs_M0_mismatch']}。L1とPhase 1 M1の差: {len(d['parity']['L1_vs_M1_diff'])}行(すべて不規則読みガード由来: {all(x['irregular'] for x in d['parity']['L1_vs_M1_diff'])}、`今日は一日中雨→ついたち中雨` M1=PASS_W→L1=NG)。")
w("PASS_W=警告付きPASS(判定器のPASS_WITH_WARNING、または新層[v2発音救済/β/辞書]経由=試聴必須)。PASSと別集計。")
w("")
w("## 1. 6音声×層: 最終Gate結果(決定対=当時記録のOpenAI転写 × 当該wavのAzure転写)")
w("| 音声 | " + " | ".join(FLS) + " | +L4 N=2 | +L4 N=3 | +L4 N=4(参考) |")
w("|---|" + "---|" * (len(FLS) + 3))
l4 = {(x["run"], x["attempt"]): x for x in d["l4_positive"]}
for p in d["positives"]:
    st = [x for x in p["draws"] if x["openai_tag"] == "stored"][0]
    cells = [short(st["res"][f]) for f in FLS]
    e = l4[(p["run"], p["attempt"])]["per_flag"][FIN]["N"]
    for n in ("2", "3", "4"):
        b = e[n]["stored_order"]
        cells.append(b["cat"] + (f"(draw{b['stopped_at']}で停止/再転写{b['extra_openai_calls']}回)" if b["cat"] != "NG" else f":{b['reason']}"))
    w(f"| {p['run']} a{p['attempt']} | " + " | ".join(cells) + " |")
w("")
w("### 1a. 決定対の転写(OpenAI=記録時、Azure=当該wav)")
w("| 音声 | OpenAI(stored) | Azure |")
w("|---|---|---|")
for p in d["positives"]:
    w(f"| {p['run']} a{p['attempt']} | {p['openai'][0][1]} | {p['azure'][0][1] if p['azure'] else '(なし)'} |")
w("")
w("## 2. 全draw対(OpenAI全draw × Azure[0]): 層別 PASS / PASS_W / NG")
w("| 音声 | draw数 | " + " | ".join(FLS) + " |")
w("|---|---|" + "---|" * len(FLS))
tot = {f: collections.Counter() for f in FLS}
for p in d["positives"]:
    cells = []
    for f in FLS:
        c = collections.Counter(x["res"][f]["cat"] for x in p["draws"])
        tot[f].update(c)
        cells.append(f"{c['PASS']}/{c['PASS_W']}/{c['NG']}")
    w(f"| {p['run']} a{p['attempt']} | {len(p['draws'])} | " + " | ".join(cells) + " |")
w(f"| 合計 | {sum(len(p['draws']) for p in d['positives'])} | " + " | ".join(f"{tot[f]['PASS']}/{tot[f]['PASS_W']}/{tot[f]['NG']}" for f in FLS) + " |")
w("(セルは PASS/PASS_W/NG の件数)")
w("")
w("### 2a. 各draw対の判定(層 L1+L2+L3)と経路(NG理由 or 発火層)")
for p in d["positives"]:
    w(f"- **{p['run']} a{p['attempt']}**: " + " / ".join(f"{x['openai_tag']}→{short(x['res'][FIN])[:90]}" for x in p["draws"]))
w("")
w("### 2b. L4(判定前OpenAI再転写)の到達確率(L1+L2+L3 判定、k draw中m本が非NG)")
w("| 音声 | k | m(非NG) | N=1 | N=2 | N=3 | N=4 |")
w("|---|---|---|---|---|---|---|")
for x in d["l4_positive"]:
    e = x["per_flag"][FIN]
    w(f"| {x['run']} a{x['attempt']} | {e['k']} | {e['m_nonNG']} | " + " | ".join(f"{e['N'][n]['hyper_reach']:.2f}(保存順:{e['N'][n]['stored_order']['cat']})" for n in "1234") + " |")
w("(hyper_reach=draw集合からN個を無作為に選んで少なくとも1本が非NGの確率。保存順=記録された順に最初にPASS/PASS_Wで停止するシミュレーション)")
w("")
w("## 3. 負例: 誤PASS(PASS+PASS_W)と増分(L0比)")
w("### 3a. 層別 総誤PASS / 増分誤PASS(truth==NEG全行、Phase 1の1439行+L3_NEG+N3_redraw)")
neg = [r for r in rows if r["truth"] == "NEG"]
w(f"NEG行数={len(neg)}(Phase 1: 1439 + L3_NEG + N3_redraw)")
w("| 層 | 総誤PASS | うちPASS | うちPASS_W | 増分誤PASS(L0=NG→誤PASS) | 回帰(L0 PASS系→NG, 全truth) |")
w("|---|---|---|---|---|---|")
inc = {}
for f in FLS:
    tp = [r for r in neg if r["res"][f]["cat"] != "NG"]
    ic = [r for r in neg if r["res"]["L0"]["cat"] == "NG" and r["res"][f]["cat"] != "NG"]
    inc[f] = ic
    reg = [r for r in rows if r["res"]["L0"]["cat"] != "NG" and r["res"][f]["cat"] == "NG"]
    w(f"| {f} | {len(tp)} | {sum(1 for r in tp if r['res'][f]['cat']=='PASS')} | {sum(1 for r in tp if r['res'][f]['cat']=='PASS_W')} | {len(ic)} | {len(reg)} |")
w("")
w("### 3b. 増分誤PASSの型別内訳(Phase 1の3型 T1/T2/T3 以外=OTHER があれば当該層は不合格)")
w("| 層 | T1 同音異表記便乗 | T2 β値garble | T3 不規則読み | OTHER |")
w("|---|---|---|---|---|")
for f in FLS[1:]:
    c = collections.Counter(vtype(r).split("_")[0] for r in inc[f])
    w(f"| {f} | {c['T1']} | {c['T2']} | {c['T3']} | {c['OTHER(要不合格開示)'] + c.get('OTHER', 0)} |")
w("")
w("### 3c. 増分誤PASSの全列挙(L1+L2+L3。他層はこの部分集合)")
w("| group | tag | scenario | canon | Primary | Secondary | 型 | 層別cat(L1/L1+L2/L1+L3/L1+L2+L3) | 経路 |")
w("|---|---|---|---|---|---|---|---|---|")
for r in inc[FIN]:
    w(f"| {r['group']} | {r['tag'][:40]} | {r['scenario']} | {r['canon'][:30]} | {r['primary'][:34]} | {(r['secondary'] or '')[:34]} | {vtype(r).split('(')[0]} | {r['res']['L1']['cat']}/{r['res']['L1+L2']['cat']}/{r['res']['L1+L3']['cat']}/{r['res'][FIN]['cat']} | {r['res'][FIN]['route'][:60]} |")
w("")
w("### 3d. 負例の群別 総誤PASS(L0 → L1+L2+L3)")
w("| group | n | L0誤PASS | L1+L2+L3誤PASS |")
w("|---|---|---|---|")
g = collections.defaultdict(lambda: [0, 0, 0])
for r in neg:
    x = g[r["group"]]
    x[0] += 1
    x[1] += r["res"]["L0"]["cat"] != "NG"
    x[2] += r["res"][FIN]["cat"] != "NG"
for k, v in sorted(g.items()):
    w(f"| {k} | {v[0]} | {v[1]} | {v[2]} |")
w("")
w("### 3e. L1不規則読みガードの効果(Phase 1 M1との差)")
for x in d["parity"]["L1_vs_M1_diff"]:
    w(f"- {x['k'][2]} → {x['k'][3]} [{x['k'][4]}]: M1={x['M1']} → L1={x['L1']}(L0={x['L0']})")
w("")
w("## 4. L3(読み候補辞書拡張『数量+超』の接尾)の検証")
w("### 4a. 正例 L3_POS(辞書で救済されるべき)と、シナリオ別 層結果")
w("| tag | scenario | L0 | L1 | L1+L2 | L1+L3 | L1+L2+L3 |")
w("|---|---|---|---|---|---|---|")
for r in rows:
    if r["group"] == "L3_POS":
        w(f"| {r['tag']} | {r['scenario']} | " + " | ".join(r["res"][f]["cat"] for f in FLS) + " |")
w("(P_only=Secondary無し: 発火しない[両engine必須])。S_canon=Secondary:=原稿そのもの[最悪露出]では L0 が既に PASS_W(Production既存のSecondary確認経路)で、L3は変化を与えない。")
w("")
w("### 4b. 負例 L3_NEG(L0 vs 各層。増分=0が条件)")
l3n = [r for r in rows if r["group"] == "L3_NEG"]
w(f"L3_NEG 行数={len(l3n)}。増分誤PASS(L0=NG→L1+L3/L1+L2+L3 で非NG)={sum(1 for r in l3n if r['res']['L0']['cat']=='NG' and r['res']['L1+L3']['cat']!='NG')}/{sum(1 for r in l3n if r['res']['L0']['cat']=='NG' and r['res'][FIN]['cat']!='NG')}。")
w("| tag | scenario | L0 | L1+L3 | L1+L2+L3 |")
w("|---|---|---|---|---|")
for r in l3n:
    if r["scenario"] != "P_only":
        w(f"| {r['tag']} | {r['scenario']} | " + " | ".join(short(r['res'][f]) if False else r["res"][f]["cat"] for f in ("L0", "L1+L3", FIN)) + " |")
w("(指示『本長/本帳/本蝶は不受理』: L3の**増分**としては満たす[増分0・test固定]。ただし本帳/本蝶/本調/本町/本鳥・人長…は **L0=Production既存の読み一致で既にPASS**[PS_same]=同音(ちょう)の異表記を既存仕様が受理している基線事実。L3はこれらを変化させない。本長のみ L0もNG[PS_same]。この基線の扱いはFableへ報告事項)。")
w("")
w("## 5. L4(判定前ASR再転写)のN3 30wav × 新規4 draw: 誤PASS(PASS+PASS_W)率")
n3 = d["l4_n3"]["clips"]
w("対象=N3 30 wav(意図的誤読TTS、真値NEG)。Azure=保存転写(変動0仮定)。『N draw までのいずれかが非NG』のclip数。")
w("| シナリオ | 構成 | N=1 | N=2 | N=3 | N=4 | 順列平均 N=1/2/3/4 |")
w("|---|---|---|---|---|---|---|")
for scn in ("real", "S_canon"):
    for fn in ("L0", FIN):
        k = f"{scn}|{fn}"
        cnt = [sum(1 for c in n3.values() if c["scn"][k]["N_new"][n] != "NG") for n in "1234"]
        hy = [sum(c["scn"][k]["hyper_new"][n] for c in n3.values()) / 30 for n in "1234"]
        w(f"| {scn} | {fn} | " + " | ".join(f"{x}/30" for x in cnt) + " | " + "/".join(f"{h:.3f}" for h in hy) + " |")
w("")
w("参考: 保存済みOpenAI転写を第0drawとして加えた場合(N=1..5)")
w("| シナリオ | 構成 | N=1 | N=2 | N=3 | N=4 | N=5 |")
w("|---|---|---|---|---|---|---|")
for scn in ("real", "S_canon"):
    for fn in ("L0", FIN):
        k = f"{scn}|{fn}"
        w(f"| {scn} | {fn} | " + " | ".join(f"{sum(1 for c in n3.values() if c['scn'][k]['N_with_stored'][n] != 'NG')}/30" for n in "12345") + " |")
w("")
w("(基線: N3の誤PASSの大半はL0でも起きる『表記が同一/等価な誤読』型[Phase 1 §3b、同形異音・助詞・連濁]で、ASRがテキストしか見ないため区別不能。L1+L2+L3はL0に対し増分0。L4は誤PASS率をdraw数に応じて押し上げる: real N=1→3 で +1clip[N3-13]、S_canon[Secondary=原稿の最悪露出]で N=1→3 で +3clip。)")
w("N=1 → N 増加で新たに誤PASSになるclip(real, L1+L2+L3, 新4draw):")
base = {cid: c["scn"][f"real|{FIN}"]["N_new"]["1"] for cid, c in n3.items()}
for n in "234":
    ch = [cid for cid, c in n3.items() if c["scn"][f"real|{FIN}"]["N_new"][n] != "NG" and base[cid] == "NG"]
    w(f"- N={n}: +{len(ch)}件 " + "; ".join(f"{cid}({n3[cid]['type']}/TTS入力={n3[cid]['tts_input']}/新draw={n3[cid]['new_draws']}/Azure={n3[cid]['azure']})" for cid in ch))
w("")
w("L0とL1+L2+L3のN3(新draw)での差(増分): " + str(sum(1 for c in n3.values() for n in "1234" if c["scn"][f"real|{FIN}"]["N_new"][n] != c["scn"]["real|L0"]["N_new"][n])) + " (clip×N組合せ)。")
w("")
w("## 6. 残NG・Human Review条件(iv)")
w("### 6a. 層適用後に残るNG(決定対)")
for p in d["positives"]:
    st = [x for x in p["draws"] if x["openai_tag"] == "stored"][0]["res"]
    if st[FIN]["cat"] == "NG":
        w(f"- {p['run']} a{p['attempt']}: L1+L2+L3 でNG({st[FIN]['reason']})。draw集合の非NG={sum(1 for x in p['draws'] if x['res'][FIN]['cat']!='NG')}/{len(p['draws'])}。L4[N=3]で解消=" + str(l4[(p['run'], p['attempt'])]['per_flag'][FIN]['N']['3']['stored_order']['cat'] != 'NG'))
w("- 原因(RESIDUAL_NG_ANALYSIS_01.md): ms_03 a1=OpenAI数詞崩れ(stored『8000句800』)+TTS読みゆれ『超→こえ』(L3で読みは解消、値はL4/βが必要。L3の発火条件は両engine値一致のため、値崩れdrawでは発火しない)。reselect a3=2engineが『スギノ/Sukino』と一致して原稿と異音=ASR誤認識かTTSの弱い『つ』か**転写のみでは確定不能**(ローカルWhisper 2/2は『月の詩/死』)。")
w("- 機械確定不能の根拠: reselect a3 の決定対では、2つの独立Production engine(OpenAI・Azure)が一致して原稿と異なる音(スギノ)を出し、原稿の音を支持する転写はdrawの偶然(OpenAI 5drawのうち『月野市は』1本)と第三証人(ローカルWhisper、判定不使用)のみ。音声そのものを聞かずに『正常音声がASRに誤認識された』と『TTSが誤読した』は区別できない。")
w("")
w("### 6b. Human Review 機械条件案(hr_candidate)")
w("条件(全層NG後、全draw対のうち1対でも満たせば候補): (a)少なくとも片方のengine転写が原稿との値ガードEQUAL かつ全転写に否定差なし (b)値atomを除いた読み(v2モーラ列)の差分が連続1区間・3モーラ以内 (c)原稿に不規則読み数詞なし。**判定(PASS/NG)は変えない**=人間の試聴キューに付ける証拠。judge関数はhr_candidateを参照しない(test固定)。")
w("| 対象 | HR候補 | 差分/証拠 |")
w("|---|---|---|")
for h in d["hr_positive"]:
    ev = h["hr"].get("evidence", {})
    w(f"| 正例 {h['run']} a{h['attempt']} | {h['hr']['candidate']} | {ev.get('diff')} / {ev.get('engine_text','')[:40]} |")
cand = sum(1 for c in n3.values() if c["hr"]["candidate"])
w(f"| N3負例30wav(全draw対) | 候補{cand}/30 | " + ", ".join(cid for cid, c in n3.items() if c["hr"]["candidate"]) + " |")
w("")
w("負例text行(L1+L2+L3でもNGのもの)の群別HR候補件数: " + json.dumps(d["hr_neg_text"], ensure_ascii=False))
w("- 読み取り: 6正例は(全draw集合基準で)すべて候補になるが、原稿と1モーラ差のみの負例(U1『異なる発音』など)も候補になる=**HR条件は正誤を分離せず、人間が聞くべき対象を絞る(自動PASSにしない)用途に限る**。候補率が高い群はレビュー負荷の見積に使う。")
w("- 既存HR機構との差分: 既存は `er007_ja_secondary_asr_01.py:759-764`(最終slotでNGのとき human_review_required=True)→ `_log_human_review`(同:42-59、`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`)→ review_lock(`er011_human_review_lock_01`)→ 個別採用(`asm.record_human_approval`、例 `er011_..._audio_03_b1b_individual_approval_and_assemble_01.py:step1`)。(iv)案はこれに**上記3条件の証拠欄を追加するだけ(iv-a: 挙動不変)**、または候補ならTTS再生成上限前に早期にキューへ送る(iv-b: 再生成回数が変わる=承認済みretry仕様の変更でユーザー判断事項)。")
w("- 抜け道の有無: hr_candidateは判定関数から呼ばれずPASS/NGを返さない(test_hr_candidate_never_changes_judgement...)。承認は既存の個別採用(sha単位・ユーザー試聴)のまま=Gateの恒久免除になる経路はない。負例が候補になっても人間が不採用にできる。")
w("")
w("## 7. 6合格条件(ユーザー原文§6)への到達度")
fin_dec = {}
for p in d["positives"]:
    fin_dec[(p["run"], p["attempt"])] = [x for x in p["draws"] if x["openai_tag"] == "stored"][0]["res"][FIN]["cat"]
n_pw = sum(1 for v in fin_dec.values() if v != "NG")
l43 = sum(1 for k, v in l4.items() if v["per_flag"][FIN]["N"]["3"]["stored_order"]["cat"] != "NG")
l42 = sum(1 for k, v in l4.items() if v["per_flag"][FIN]["N"]["2"]["stored_order"]["cat"] != "NG")
w("| 条件 | 到達度 | 根拠 |")
w("|---|---|---|")
w(f"| 1. 6音声すべて最終判定でPASS | **部分**: clean PASS 0/6。PASS_W(試聴必須) 決定対 L1+L2+L3 で{n_pw}/6、+L4[N=2]で{l42}/6、+L4[N=3]で{l43}/6 | §1。新方式経由は常にPASS_W(R2/R-1)。『無条件PASS』は構造的に出ない(ユーザー§6『警告付きPASSを無条件PASSと同一視しない』) |")
w(f"| 2. 既知の実誤読・負例を誤PASSしない | **部分**: 増分誤PASSはPhase 1の3型(T1/T2。T3はL1ガードで0)のみで OTHER=0。回帰0。ただし T1(音素列が原稿と同一=区別不能)とT2(β)は構造的に残る | §3b-3c |")
w("| 3. 『月のしわ』固有でない | **達成** | 辞書層はatom位置から導出(月題固有語なし=test固定)、汎用題(100人超/1,200円超 等)でL3_POS救済・L3_NEG増分0 | ")
w("| 4. X/Y/Zの対象範囲・既存仕様影響 | **達成(評価済み)** | Phase 1 EVAL_UNIFIED_01.md §5(Family×Level×Section)を継承。L1〜L3は既存adapter位置への差替で適用範囲は同一。AdvにJA音声なし |")
w("| 5. retry/fallback/resume/再判定整合 | **部分**: 設計整合は記載、実行検証は未配線のためproto内のみ | L0〜L3は保存転写+wav shaで再判定可能(API 0)。**L4は承認済み仕様『同一音声のASR再試行廃止』と衝突**=ユーザー判断事項。L3発火でSecondary未呼出時はAzure追加呼出が要る |")
w("| 6. 費用・量産単価 | **達成(区間提示)** | §8 |")
w("")
w("### Status候補(最終判定はFable): **USER_DECISION_REQUIRED**(VALIDATEDにしない)")
w(f"- 理由: 条件1が『PASS』でなく『PASS_W(試聴必須)』止まり(clean PASS 0/6)、L4なしでは{6-n_pw}本がNG、L4[N=2]で{6-l42}本・L4[N=3]で{6-l43}本がNG(保存順シミュレーション。reselect a3のN=3到達確率は超幾何で0.60=確率的)。条件2も同音異表記(T1)とβ最悪露出(T2)を構造的に許容する。これらを許容して『PASS_W+試聴』を合格と見なすか、L4(ASR再試行)の承認済み仕様変更を認めるかは、ユーザーの品質定義に関わる判断。")
w("- REJECTEDにしない理由: 回帰0・OTHER増分0・汎用性達成・費用は軽微。")
w("")
w("## 8. 単価(採用時の記事あたり増減)")
fin_draws = [x for p in d["positives"] for x in p["draws"]]
na = sum(1 for x in fin_draws if x["res"][FIN]["needs_azure"])
w(f"- L1/L2/L3: 判定ロジックのみ(¥0)。保存Secondary転写を使う場合の追加ASR費は0。Azure追加呼出が要るのは『Primaryだけで受理でき、Secondary未呼出』かつL3/β発火のとき(6音声27draw中 {na}件)。Azure実測 ¥0.27〜0.31/clip(6秒題)。")
w("- L4: OpenAI再転写の実費は BUDGET_LOG_01.md(120呼出)。1clip(約1.7秒)あたり¥0.01程度(公表単価ベースの上限推定。1回あたり TTS再生成 ¥0.92 の約1%)。L4[N=3]の期待追加呼出(6音声の保存順): " + ", ".join(f"{k[0]} a{k[1]}={v['per_flag'][FIN]['N']['3']['stored_order']['extra_openai_calls']}" for k, v in l4.items()) + "。")
w("- 再生成削減: 誤NG1件で TTS再生成1回(¥0.65)+ASR2本(¥0.27)≈¥0.92/clip を避けられる(Phase 3実測)。現行の誤NG率は**未確認**(月題6本は6/6がNGだが題が特殊)。区間: 記事あたり削減 ≈ ¥0.92×(回避できた誤NG再生成数 x) − ¥0.3×(L3/βがSecondary未呼出で発火した回数) − ¥0.01×(L4追加呼出数)。x=0なら削減0(追加費のみ)。例示: 月題級のJA題で再生成1〜2回回避なら ¥0.9〜1.8/記事(70円/記事セット目標比 約1〜3%)。記事あたりのx・JA clip数は現行誤NG率データがなく**未確認**。")
w("- 時間(D): 誤NGによる再生成ループ(各TTS+ASR)が1〜2周減る見込み。")
open(OUT + "EVAL_UNIFIED_02.md", "w", encoding="utf-8", newline="\n").write("\n".join(o) + "\n")
print("ok", len(o))
