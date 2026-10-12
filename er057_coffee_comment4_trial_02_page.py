# -*- coding: utf-8 -*-
"""Trial-02 評価表(EVAL_02.md)・REPORT_02.md・公開ページ(index/all_runs)生成。文章のみ、Production不変。"""
import os, sys, json, html, shutil
sys.path.insert(0, os.getcwd())
import er057_coffee_comment4_trial_02 as T
from er057_coffee_comment4_trial_02_eval import EV
ROOT = T.ROOT; OUT = T.OUT; WEB = f"{ROOT}/user_test/coffee_comment4_trial_02"
esc = html.escape
rows = [json.loads(l) for l in open(f"{OUT}/generations.jsonl", encoding="utf-8")]
cost = json.load(open(f"{OUT}/cost_llm.json", encoding="utf-8"))
BASE_V4 = "コーヒー豆の値段が下がっても、店の値札がすぐに変わるとは限りません。値段が変わる時期には、豆以外の費用も関わります。続いて、記事の要点を英語で聞いていきましょう。"
t1 = [json.loads(l) for l in open(f"{ROOT}/er057_output/coffee_comment4_trial_01/generations.jsonl", encoding="utf-8")]
base_t1 = [r for r in t1 if r["cand"] == "C0"]
IOL = json.load(open(f"{ROOT}/er057_output/coffee_final_audio_assembly_01/iol_final_text_01.json", encoding="utf-8"))["std"]
TOP = ["E1", "D4", "E9"]
INFO = {
 "E1": ("問いかけ型(改良)", "1文目で記事の焦点を素朴な問いとして置き(結論は言い切らない)、2文目で『答えはこのあとの英語のまとめにある』と伝える。「続いて」「では」「それでは」で文を始めない・全体55字以内目安を役割文に明記。",
        "3回とも51〜55字(基準1クリア)、事務的な進行語なし。問い→英語のまとめが答えを出す、という流れでIn One Lineが最後の英語要約だと自然に分かる。結論を先取りしないのでIn One Lineと内容が重ならない。",
        "問いかけ形式がやや『クイズ風』。In One Lineの内容は『答え』というより要約なので、『答えは〜にあります』は少し強い言い方(事実としては整合)。run2が全角『？』を使う表記ゆれがある。『最後』という終盤語は使わず『このあと』なので、ラスト感は文脈頼み。"),
 "D4": ("着地点提示型(Round1)", "2文以内で、記事の着地点を一つだけ短く示し、その点を英語の短いまとめ(In One Line)で確かめる流れにする。",
        "3回とも54〜59字、全Runで基準2〜5が○。核心を1文で軽く回収したうえで『続く英語のまとめで確認しましょう』へつなぐ構成が最も素直で、日本語も自然。",
        "着地点(結論)をそのまま言い切るため、In One Lineの内容(豆価格は下がったが店は遅れる)と重複する。回収は軽いが『新しい情報』は無く、聞き手によっては冗長。『確かめましょう』『確認しましょう』の語尾が3回で似通う。"),
 "E9": ("気づき共有型(改良)", "1文目で『〜のですね』という柔らかい言い方で記事から分かったことを一つだけ示し、2文目で『英語の結びのまとめで確認する』と伝える。「つまり」「では」「続いて」で始めない・全体55字以内目安を役割文に明記。",
        "3回とも47〜54字(基準1クリア)。『英語の結びのまとめ』と明示するため、最後の英語要約だと自然に伝わる。親しみのある口調で読み上げにも合う。事務的な進行語なし。",
        "run1『見てきたのですね』は聞き手の発話のようで不自然(△)。『〜のですね』口調はシリーズ全体の語りのトーンと合うか要判断。run2は結論に近い内容を述べるためIn One Lineと重なりうる。"),
}
for r in rows: r["det"] = T.det(r["text"] or "")
C = {}
for r in rows: C.setdefault(r["cand"], []).append(r)
assert len(EV) == len(rows) == 60


def c6(cand):
    good = ok = 0
    for r in C[cand]:
        codes = EV[(cand, r["run"])][:4]
        w = r["det"]["within_67"]; nx = "×" in codes; nt = sum(1 for x in codes if x == "△")
        if w and not nx and nt <= 1: good += 1
        if w and not nx: ok += 1
    return "○" if good == 3 else ("△" if ok >= 2 else "×")


def design(cand):
    for rd, d in T.ROUNDS.items():
        if cand in d: return rd, d[cand][0]


md = "# EVAL_02: 全候補×全Run 評価表(Sonnet自身が各Runを読んで採点)\n\n"
md += "- 基準1: 67字以下か。**文字数=改行・空白を除いた文字数(Python len、日本語は全角1文字=1。英字・数字が混在する場合は別途フラグ)**。機械計測(`er057_coffee_comment4_trial_02.py metrics`)。\n"
md += "- 基準2: In One Lineが最後の英語要約だと自然に伝わる / 基準3: 日本語として自然で読み上げ向き / 基準4: 核心を過不足なく軽く回収 / 基準5: 余計な説明・事務的表現がない(○良/△可/×不可)\n"
md += "- 基準6: 候補単位。○=3回とも67字以下かつ×なしかつ△が1つ以下 / △=3回中2回以上が67字以下かつ×なし / ×=それ未満\n\n"
md += "| Round | 候補 | Run | 文字数 | 基準1 | 基準2 | 基準3 | 基準4 | 基準5 | 基準6(候補) | 本文 | 根拠 |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
for cand in C:
    rd, _ = design(cand)
    for r in C[cand]:
        ev = EV[(cand, r["run"])]; d = r["det"]
        md += f"| {rd} | {cand} | {r['run']} | {d['chars']} | {'○' if d['within_67'] else '×'} | {ev[0]} | {ev[1]} | {ev[2]} | {ev[3]} | {c6(cand) if r['run'] == 1 else ''} | {r['text']} | {ev[4]} |\n"
open(f"{OUT}/EVAL_02.md", "w", encoding="utf-8").write(md)
summ = {c: {"round": design(c)[0], "design": design(c)[1], "chars": [r["det"]["chars"] for r in C[c]], "c6": c6(c)} for c in C}
json.dump(summ, open(f"{OUT}/eval_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def cand_block(c, h="h3"):
    rd, dsg = design(c)
    s = f"<{h}>{c} (Round{rd}) {esc(dsg)} / 基準6(安定性): {c6(c)}</{h}><table><tr><th>Run</th><th>文字数</th><th>基準1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>本文</th><th>評価根拠</th></tr>"
    for r in C[c]:
        ev = EV[(c, r["run"])]; d = r["det"]
        s += f"<tr><td>{r['run']}</td><td>{d['chars']}</td><td>{'○' if d['within_67'] else '×'}</td><td>{ev[0]}</td><td>{ev[1]}</td><td>{ev[2]}</td><td>{ev[3]}</td><td class='t'>{esc(r['text'])}</td><td>{esc(ev[4])}</td></tr>"
    return s + "</table>"


CSS = ("<style>body{font-family:sans-serif;max-width:1200px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin-bottom:1em}th,td{border:1px solid #ccc;padding:5px;vertical-align:top;text-align:left;font-size:.92em}"
       "td.t{min-width:340px;background:#f6f6f6}.s{color:#666;font-size:.88em}</style>")
os.makedirs(WEB, exist_ok=True)
base_md = "# 現行Production Comment 4 Prompt(基準、逐語)\n\n```\n" + T.C0 + "\n```\n"
open(f"{OUT}/prompts/prompt_baseline_current.md", "w", encoding="utf-8").write(base_md)
for f in os.listdir(f"{OUT}/prompts"): shutil.copy(f"{OUT}/prompts/{f}", f"{WEB}/{f}")
avg = sum(T.nchars(r["text"]) for r in base_t1) / 3
base_html = ("<h2>Baseline(現行)</h2><p class='s'>現行Production Comment 4。v4に使用中の音声原稿は" f"{T.nchars(BASE_V4)}字。前回Trial-01の現行Prompt再生成3回は" + "/".join(str(T.nchars(r['text'])) for r in base_t1) + f"字(平均{avg:.0f}字=ユーザー指定の『67字』)。現行Prompt全文: <a href='prompt_baseline_current.md'>prompt_baseline_current.md</a></p><ul>"
             f"<li>v4使用中({T.nchars(BASE_V4)}字): {esc(BASE_V4)}</li>" + "".join(f"<li>Trial-01 C0 run{r['run']}({T.nchars(r['text'])}字): {esc(r['text'])}</li>" for r in base_t1) + "</ul>")
iol_html = f"<p><b>直後に流れるIn One Line(固定):</b> {esc(IOL)}</p>"
head = "<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
idx = head + "<title>Coffee Comment 4 短縮橋渡しTrial-02 上位3</title>" + CSS + "</head><body><h1>Coffee Standard Comment 4 短縮橋渡し Trial-02(上位3パターン)</h1>"
idx += "<p class='s'>Trial専用(Production Promptではありません、採否は未決=USER_DECISION_REQUIRED)。文章のみ(音声なし)。文字数は改行・空白を除いた文字数。基準1=67字以下、2=In One Lineへの橋渡し、3=日本語の自然さ、4=核心の軽い回収、5=事務的表現なし、6=3回の安定性。全候補・全Runは <a href='all_runs.html'>all_runs.html</a>。</p>" + iol_html + base_html
for i, c in enumerate(TOP, 1):
    nm, feat, why, weak = INFO[c]
    idx += f"<h2>推薦{i}位: {c} {esc(nm)}</h2><p><b>Prompt設計:</b> {esc(feat)}</p>" + cand_block(c) + f"<p><b>推薦理由:</b> {esc(why)}</p><p><b>弱点:</b> {esc(weak)}</p>"
idx += "</body></html>"
open(f"{WEB}/index.html", "w", encoding="utf-8").write(idx)
al = head + "<title>Coffee Comment 4 Trial-02 全候補全Run</title>" + CSS + "</head><body><h1>Trial-02 全候補・全Run・全ラウンド(60 Run)</h1>"
al += "<p class='s'>Prompt全文: <a href='prompts_round1.md'>Round1</a> / <a href='prompts_round2.md'>Round2</a> / <a href='prompt_baseline_current.md'>現行Baseline</a>。評価はEVAL_02.mdと同内容。</p>" + iol_html + base_html
for c in C: al += cand_block(c)
al += "</body></html>"
open(f"{WEB}/all_runs.html", "w", encoding="utf-8").write(al)
for p in (idx, al): assert "file:///" not in p and "C:\\" not in p

tot = cost["total"]
rp = "# REPORT_02: FAMILY-X-COFFEE-COMMENT4-SHORT-BRIDGE-RETRIAL-02\n\n"
rp += "Status: **VALIDATED(Trial上限)**。採用はUSER_DECISION_REQUIRED(Production Prompt未変更・未配線)。\n\n"
rp += "## 結論\n67字以下で安定した候補が得られた(2ラウンド)。Round1は10候補中、D4・D6が3回とも基準内で良好(2件)だったため3件に満たず、失敗原因を分析してRound2を実施。Round2でE1・E9・E7が追加で3回とも67字以下かつ良好。上位3=E1・D4・E9。\n\n"
rp += f"## 前提・Baseline\n前回Trial-01(C0〜C4)は全候補REJECTED(C1/C2は長すぎる)で、今回C1/C2は不採用扱い。文字数=改行・空白除去後の`len`(全角1文字=1)。現行のv4使用中原稿は{T.nchars(BASE_V4)}字、Trial-01の現行Prompt再生成3回は" + "/".join(str(T.nchars(r['text'])) for r in base_t1) + "字(平均67字=基準値)。\n\n"
rp += f"- v4使用中: {BASE_V4}\n" + "".join(f"- Trial-01 C0 run{r['run']}({T.nchars(r['text'])}字): {r['text']}\n" for r in base_t1)
rp += "\n入力: Coffee Standard v4原稿(parts.json)、現行Prompt枠(FAMILY_X_A2_COMMENT_4_ROLE、役割文のみ差替)、生成経路・モデルはTrial-01踏襲(run_support_text、routing gpt-6-luna=最新世代系)。In One Line本文は生成入力に含めない(Production同様)。\n\n"
rp += "## ラウンド履歴\n- Round1(10候補×3=30call): 構成が異なる10設計(D1核心回収→英語/D2 1文/D3流れ振り返り/D4着地点/D5終盤語なし/D6問いかけ/D7気づき共有/D8文字数目標/D9禁止リスト/D10対比軸)。\n  - 失敗原因: (a)『続いて』『では』が自然発生し事務的になる(D1,D3,D7,D8,D10)、(b)核心+補足を求めると67字超過(D5,D7,D9)、(c)1文構成は読点が少なく長く読み上げに不向き(D2)、(d)核心を言い切るとIn One Lineと重複(D4)。\n  - 良好: D4・D6(3回とも基準内で○)。\n"
rp += "- Round2(10候補×3=30call): 同じ失敗を避けるため、開始語(続いて/では/つまり)の禁止、全体55字以内目安、結論を言い切らず焦点だけ示す、『英語の結びのまとめ』と明示、を役割文へ導入。構成もE1問い/E2着地点/E3文字数+禁止語/E4整理型/E5超短1文/E6振り返り/E7ずれ/E8読み上げ1文/E9気づき共有/E10観点 と変更。\n  - 良好: E1・E9・E7(E3も2/3良好)。E5・E6・E10は基準6(安定性)は○だが基準2〜3の品質で劣り上位から除外。E2・E6・E7は『In One Line』英字が混じる傾向(読み上げ不自然)、E8は文が破綻、E4は核心なし、E5は短すぎて宣言調、E10は硬い。\n- 追加ラウンドは不要(良好な候補が3件以上)。\n\n"
rp += "## 上位3(推薦順)\n"
for i, c in enumerate(TOP, 1):
    nm, feat, why, weak = INFO[c]
    rd, _ = design(c)
    rp += f"\n### 推薦{i}位 {c}(Round{rd}) {nm} / 基準6(安定性)={c6(c)}\n- Prompt設計の特徴: {feat}\n- Prompt全文: `prompts/prompts_round{rd}.md` の {c}\n\n"
    rp += "| Run | 文字数 | 基準1 | 2 | 3 | 4 | 5 | 本文 | 根拠 |\n|---|---|---|---|---|---|---|---|---|\n"
    for r in C[c]:
        ev = EV[(c, r['run'])]; d = r["det"]
        rp += f"| {r['run']} | {d['chars']} | {'○' if d['within_67'] else '×'} | {ev[0]} | {ev[1]} | {ev[2]} | {ev[3]} | {r['text']} | {ev[4]} |\n"
    rp += f"\n- 推薦理由: {why}\n- 弱点: {weak}\n"
rp += "\n## 全候補サマリ(詳細は EVAL_02.md)\n| 候補 | Round | 設計 | 文字数(3Run) | 基準6 |\n|---|---|---|---|---|\n"
for c, v in summ.items(): rp += f"| {c} | {v['round']} | {v['design']} | {'/'.join(map(str, v['chars']))} | {v['c6']} |\n"
rp += f"\n## 費用\nLLMのみ(TTS/ASR/Playwright無し)。{tot['calls']} call、入力{tot['in_tokens']}・出力{tot['out_tokens']}tokens、**JPY{tot['est_jpy']}**(gpt-6-luna in0.10/out0.50 USD per M x 160、実測usage)。上限JPY10以内。詳細 `cost_llm.json`。\n\n"
rp += "## 採否判断事項(USER_DECISION_REQUIRED)\n1. 推薦1〜3位のどれを採用候補とするか(または追加検証)。2. 採用する場合の次工程(Production Prompt変更はユーザー承認後、別タスクで音声再生成・v5組立)。3. 『結論を先取りしない(問い・焦点型)』と『着地点を示す型』のどちらを好むか(IOLとの重複許容度)。4. 他Family/Roleへの展開の要否。\n"
open(f"{OUT}/REPORT_02.md", "w", encoding="utf-8").write(rp)
print({c: v["c6"] for c, v in summ.items()})
