# 残NG原因分析の数値化(API 0・保存転写のみ)。出力=residual_analysis_01.out.txt。再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/residual_analysis_01.py
import collections, json, sys
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02")
import eval_unified_01 as U
E = U.E; vg = U.vg
E.api0_guard_on()
OUT = U.OUT
lines = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)
pos = U.load_positives()
reasr = json.load(open(U.FXD + "ja_title_reasr_01.out.json", encoding="utf8"))
M = U.MOON
def vok(t): return vg.value_guard(M, t, "ja").kind == vg.EQUAL
def prim_only(t, wav, mode):   # Azure不呼出でPrimary単独の判定
    return U.adapter(M, t, None, wav, mode)["cat"]

P("== 1. OpenAI転写の変動(同一wav・複数draw)  [stored=当時記録 / redraw=後日の再転写] ==")
tot = collections.Counter()
for p in pos:
    xs = [t for _, t in p["openai"]]
    n, nd = len(xs), len(set(xs))
    ok = sum(vok(t) for t in xs)
    rd1 = sum(prim_only(t, p["wav"], "v2") != "NG" for t in xs)
    P(f" {p['run']} a{p['attempt']}: draws={n} distinct={nd} 値EQUAL={ok}/{n} v2 Primary単独PASS_W={rd1}/{n}  stored値EQUAL={vok(xs[0])}")
    tot["n"] += n; tot["distinct"] += nd; tot["ok"] += ok; tot["rd1"] += rd1
P(f" 合計(6音声): draws={tot['n']} 値EQUAL={tot['ok']} ({tot['ok']/tot['n']:.0%}) v2 Primary単独PASS_W={tot['rd1']} ({tot['rd1']/tot['n']:.0%})")
rs = [o["text"] for r in reasr for o in r["openai"]]
P(f" 再ASR12転写(reselect 3wav x 4 draw): 値EQUAL={sum(vok(t) for t in rs)}/12 異なる転写={len(set(rs))}/12; wav別distinct=" + str([len(set(o['text'] for o in r['openai'])) for r in reasr]))
P(" Azure: reselect 3wavで『当時記録』と『再ASR』が完全一致=" + str(sum(1 for p in pos if p['run'] == 'run_reselect_01' and len(set(t for _, t in p['azure'])) == 1)) + "/3 (Azure変動0/3)。ms_03 a2は当時記録とPhase3再転写が一致。")
P("")
P("== 2. 6音声のローカルWhisper(第三証人・参考。Production不使用)をPrimary代わりに置いた場合 ==")
for p in pos:
    for k, t in sorted(p["whisper_local"].items()):
        P(f" {p['run']} a{p['attempt']} whisper-{k}: 値EQUAL={vok(t)} v2 Primary単独={prim_only(t, p['wav'], 'v2')} M0 Primary単独={prim_only(t, p['wav'], None)} | {t}")
P("")
P("== 3. 残NG音声の what-if(方式ではなく診断。『何が最後の障害か』の特定) ==")
a1 = [p for p in pos if p["run"] == "run_ms_03" and p["attempt"] == 1][0]
az = a1["azure"][0][1]
cand = [t for _, t in a1["openai"] if vok(t)]
for t in cand:
    base = U.all_methods(M, t, az, a1["wav"])
    t2 = t.replace("超え", "超"); az2 = az.replace("越え", "超")
    wi = U.all_methods(M, t2, az2, a1["wav"])
    P(f" ms_03 a1 値正OpenAI draw『{t}』×Azure『{az}』 実判定 M0/M1/M4=" + "/".join(base[m]["cat"] + "(" + base[m]["reason"][:22] + ")" for m in ("M0", "M1", "M4")) + f" || what-if(超え→超, 越え→超) M0/M1/M4=" + "/".join(wi[m]["cat"] for m in ("M0", "M1", "M4")))
P("   (超の読み候補[Production辞書]=" + str(__import__('er008_asr_variant_hardening_15_ja_kanji_readings').reading_candidates_for_span('超')) + " / 超え=" + str(__import__('er008_asr_variant_hardening_15_ja_kanji_readings').reading_candidates_for_span('超え')) + ")")
a3 = [p for p in pos if p["run"] == "run_reselect_01" and p["attempt"] == 3][0]
P(" reselect a3: OpenAI全draw=" + str([t[:14] for _, t in a3["openai"]]) + " Azure=" + a3["azure"][0][1][:14])
P("   → 『スギノ/杉の/Sukino』=Production2エンジン中の stored OpenAI と Azure が一致(同じ誤認識方向)。ローカルWhisper small/medium は『月の詩は/死は』=しわ互換。")
E.api0_guard_off()
open(OUT + "residual_analysis_01.out.txt", "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
