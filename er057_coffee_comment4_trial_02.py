# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-COMMENT4-SHORT-BRIDGE-RETRIAL-02 Trial専用(Production非経由、Prompt/定数不変、文章のみ)。
modes: prompts <round> / gen <round> / metrics"""
import os, sys, json, re, hashlib, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = f"{ROOT}/er057_output/coffee_comment4_trial_02"
TONE = r"C:\Users\tensh\eigo-radio-tone\er019_output\family_x_audio_production_wiring_01\coffee_prices__run_e_tone_01\a2"
import er019_family_x_audio_plan_01 as plan

C0 = plan.FAMILY_X_A2_COMMENT_4_ROLE
OLD_ROLE = """役割: 記事全体の意味を軽く回収し、In One Lineへつなぎます。本文を再説明し
すぎないでください。2〜3文にしてください。"""
assert OLD_ROLE in C0
LIMIT = 67
N = 3

# ラウンド別 候補定義: id -> (設計特徴, 役割文)。役割文のみ差替(前後の共通枠・禁止事項・構造ラベル禁止・sentence数断定禁止注記はC0逐語)
ROUNDS = {}
ROUNDS[1] = {
 "D1": ("核心1文回収→英語まとめへ(2文固定・各文を短く)",
  "役割: 次の2文だけで書いてください。1文目は、記事の核心を一つだけ短く言い直します。2文目は、そのことを英語でまとめて聞く流れへつなぎます。各文は短くしてください。"),
 "D2": ("1文構成(回収と橋渡しを1文に合体)",
  "役割: 1文だけで書いてください。その1文の中で、記事の核心を軽く振り返りながら、このあと英語でまとめを聞く流れへ自然につなぎます。短く言い切ってください。"),
 "D3": ("流れを一息で短く振り返り→英語の結びへ(2文、振り返りは述べるだけ)",
  "役割: 2文で書いてください。1文目は、ここまでの話の流れを一息で短く振り返ります。2文目は、英語による結びのまとめ(In One Line)に自然につなぎます。本文の中身は繰り返さず、流れの感触だけを伝えてください。"),
 "D4": ("着地点提示→英語要約へ(「この話の着地点」を一つ示す)",
  "役割: 2文以内で書いてください。この記事が行き着いた点(着地点)を一つだけ短く示し、そのうえで、その着地点を英語の短いまとめ(In One Line)で確かめる流れにしてください。"),
 "D5": ("終盤を示す言葉を使わず、文脈だけで締めを示す(1〜2文)",
  "役割: 1〜2文で書いてください。「最後に」「終わり」「聞き終えた」など、終わりや進行を直接示す言葉は使わず、記事の核心を軽く言い当てることで、話が一区切りついた感じを出します。そのうえで、英語で要点を聞く流れに自然につなぎます。"),
 "D6": ("問いかけ型(聞き手が抱く疑問を一つ→英語のまとめが答える)",
  "役割: 2文以内で書いてください。この記事を聞き終えた人が抱きそうな素朴な疑問を一つだけ短く置き、その答えを英語の短いまとめ(In One Line)で確かめる流れにつなぎます。本文の中身は繰り返さないでください。"),
 "D7": ("聞き手視点の気づき共有(「つまり〜でしたね」型の共感+英語で確認)",
  "役割: 2文以内で書いてください。記事を聞いた人が持ち帰る気づきを、「つまり〜ということですね」のような親しい言い方で一つだけ短く示し、それを英語のまとめで確かめる流れにつなぎます。"),
 "D8": ("文字数ターゲット明示(全体で50字前後、2文)",
  "役割: 全体で50字前後、2文で書いてください。1文目で記事の核心を軽く回収し、2文目で英語による結びのまとめ(In One Line)へ自然につなぎます。余計な説明は入れないでください。"),
 "D9": ("事務的つなぎ禁止リスト型(核心1点のみ、1〜2文)",
  "役割: 1〜2文で書いてください。記事の核心を一つだけ軽く回収し、英語による結びのまとめ(In One Line)へつなぎます。「続いて」「ここからは」「本文を聞き終えました」のような単なる進行の言葉だけで終わらせず、本文の再説明もしないでください。"),
 "D10": ("対比1つだけを軸にする(記事の中心の対比を短く拾い、英語で短くまとめる)",
  "役割: 2文以内で書いてください。記事の中心にある対比やズレを一つだけ短く拾い、それを英語の短いまとめ(In One Line)で確かめる流れにします。全体を短く、軽くしてください。"),
}
for r in ROUNDS.values():
    for k, (d, role) in r.items(): assert "\n" not in role

# Round1分析: 事務的つなぎ(続いて/では)が多発、3文要求・核心+時間差等の説明で67字超過、結論をそのまま言い切るとIn One Lineと重複。
# Round2は 開始語禁止・結論を言い切らず焦点だけ示す・文字数を役割文内で絞る 方向で構成を変える。
ROUNDS[2] = {
 "E1": ("問いかけ型の改良: 焦点を問いで示し結論は言い切らない+「続いて」「では」で文を始めない+英語の結びが答えと分かる",
  "役割: 2文で書いてください。1文目は、記事の焦点を素朴な問いとして短く置きます(結論は言い切らない)。2文目は、その答えが、このあとの英語の結びのまとめ(In One Line)にあると伝えます。「続いて」「では」「それでは」で文を始めないでください。全体で55字以内を目安にしてください。"),
 "E2": ("着地点型の改良: 着地点を名詞句で一つ示し、英語の結びのまとめで整理すると伝える(2文・短く)",
  "役割: 2文で書いてください。1文目は、この記事が行き着いた点を一つだけ短く示します。2文目は、それを英語の結びのまとめ(In One Line)で整理すると伝えます。「続いて」「では」で始めないでください。全体で55字以内を目安にしてください。"),
 "E3": ("文字数目標+開始語禁止の2文(核心回収→英語の結びへ)",
  "役割: 全体で50字前後、2文で書いてください。1文目で記事の核心を軽く回収し、2文目で英語の結びのまとめ(In One Line)へ自然につなぎます。「続いて」「では」「それでは」「ここからは」「聞き終えました」は使わないでください。"),
 "E4": ("整理型: 軽い実感→「英語の短い結びで整理する」と言い切る(「聞いてみましょう」型を避ける)",
  "役割: 2文以内で書いてください。記事を聞いた実感を一言で軽く伝え、そのあと、英語の短い結びのまとめ(In One Line)で整理する、という流れにつなぎます。「聞いてみましょう」「続いて」「では」は使わないでください。"),
 "E5": ("超短1文型: 記事の焦点の名詞句+英語の結びで整理(1文・40字以内目安)",
  "役割: 1文だけで書いてください。40字以内を目安に、記事の焦点を名詞で短く示し、英語の結びのまとめ(In One Line)でそれを整理する、と伝えてください。"),
 "E6": ("振り返り型の改良: 話の流れを振り返る→英語の結びで締めくくる(「続いて」「では」禁止、内容の重複説明なし)",
  "役割: 2文で書いてください。1文目は、ここまでの話の大きな流れを一息で振り返ります(結論は言い切らない)。2文目は、その流れを英語の結びのまとめ(In One Line)で締めくくると伝えます。「続いて」「では」「それでは」は使わないでください。全体で55字以内を目安にしてください。"),
 "E7": ("対比の焦点型の改良: 記事の対比を『AとBのずれ』の形で短く拾い、英語の結びで確かめる(2文)",
  "役割: 2文で書いてください。1文目は、記事の中心にある対比を「〜と〜のずれ」のような短い形で一つだけ拾います(具体的な期間や数字は出さない)。2文目は、そのずれを英語の結びのまとめ(In One Line)で確かめると伝えます。「続いて」「では」で始めないでください。"),
 "E8": ("読み上げ重視の1文型: 読点で区切り、1文を短く言い切る(核心+英語の結び)",
  "役割: 1文だけで書いてください。読み上げやすいよう読点で区切り、記事の核心を軽く振り返ったうえで、英語の結びのまとめ(In One Line)を聞く流れを自然に含めてください。長くなりすぎないよう、50字前後にしてください。"),
 "E9": ("気づき共有型の改良: 「〜のですね」型の共感を1つ+英語の結びで確認(開始語禁止、短く)",
  "役割: 2文で書いてください。1文目は、記事から分かったことを「〜のですね」のような柔らかい言い方で一つだけ短く示します。2文目は、英語の結びのまとめ(In One Line)で確認すると伝えます。「つまり」「では」「続いて」で始めないでください。全体で55字以内を目安にしてください。"),
 "E10": ("条件付き核心型: 結論は言い切らず『〜かどうか』の観点だけ示し、英語の結びが明らかにすると伝える(2文)",
  "役割: 2文で書いてください。1文目は、記事が扱った大事な観点を「〜かどうか」「〜の関係」のように短く示します(結論は言い切らない)。2文目は、その観点を英語の結びのまとめ(In One Line)で整理すると伝えます。「続いて」「では」「それでは」で始めないでください。"),
}
for r in ROUNDS.values():
    for k, (d, role) in r.items(): assert chr(10) not in role


def role_full(rd, k): return C0.replace(OLD_ROLE, ROUNDS[rd][k][1])
def sha_s(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def nchars(t): return len(re.sub(r"\s+", "", t))  # 改行・空白除去後の文字数(全角日本語主体のため1文字=1。ASCII混在は別途flag)


def prompts(rd):
    md = f"# Comment 4 Prompt候補 Round{rd}(共通枠=現行 FAMILY_X_A2_COMMENT_4_ROLE 逐語、役割文のみ差替)\n\n"
    for k, (d, role) in ROUNDS[rd].items():
        full = role_full(rd, k)
        md += f"## {k} {d}\n- 全文字数 {len(full)} / sha256 {sha_s(full)}\n\n```\n{full}\n```\n\n"
    open(f"{OUT}/prompts/prompts_round{rd}.md", "w", encoding="utf-8").write(md)
    print("ok")


def ctx():
    p = json.load(open(f"{TONE}/parts.json", encoding="utf-8"))
    return f"【本文1】\n{p['part1']}\n\n【本文2】\n{p['part2']}\n\n【本文3】\n{p['part3']}"


def gen(rd):
    for p in (f"{OUT}/STOP", f"{ROOT}/er026_output/family_z_production_e2e_01/STOP_ALL"):
        assert not os.path.exists(p), "STOP sentinel"
    import er003_v1_iran01_a2_generate as a2gen
    import er006_model_routing_contract_01 as routing
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    client = a2gen.vfl01.get_client()
    usages = []
    orig = client.responses.create
    def wrapped(**kw):
        r = orig(**kw); u = getattr(r, "usage", None)
        usages.append({"model": r.model, "in": getattr(u, "input_tokens", 0), "out": getattr(u, "output_tokens", 0)})
        return r
    client.responses.create = wrapped
    c = ctx()
    jobs = [(k, i) for k in ROUNDS[rd] for i in range(1, N + 1)]
    def one(j):
        k, i = j
        r = a2gen.run_support_text(client, role_full(rd, k), c, model=model)
        return {"round": rd, "cand": k, "run": i, "status": r["status"], "text": r["text"], "model_id": r["attempts"][-1].get("model"), "attempts": len(r["attempts"])}
    with cf.ThreadPoolExecutor(5) as ex: res = list(ex.map(one, jobs))
    with open(f"{OUT}/generations.jsonl", "a", encoding="utf-8") as f:
        for r in res: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    inp = sum(u["in"] or 0 for u in usages); out = sum(u["out"] or 0 for u in usages)
    jpy = (inp * 0.10 + out * 0.50) / 1e6 * 160
    cp = f"{OUT}/cost_llm.json"
    cost = json.load(open(cp)) if os.path.exists(cp) else {"rounds": {}}
    cost["rounds"][str(rd)] = {"routing_model": model, "response_models": sorted({u["model"] for u in usages}), "calls": len(usages), "in_tokens": inp, "out_tokens": out, "est_jpy": round(jpy, 4)}
    cost["total"] = {"calls": sum(v["calls"] for v in cost["rounds"].values()), "in_tokens": sum(v["in_tokens"] for v in cost["rounds"].values()),
                     "out_tokens": sum(v["out_tokens"] for v in cost["rounds"].values()), "est_jpy": round(sum(v["est_jpy"] for v in cost["rounds"].values()), 4)}
    cost["basis"] = "pricing_snapshot gpt-6-luna in0.10/out0.50 USD per M x USD/JPY160(trial_01と同一)"
    json.dump(cost, open(cp, "w"), indent=1, ensure_ascii=False)
    for r in res: print(r["cand"], r["run"], r["status"], nchars(r["text"] or ""), r["text"])
    print("jpy", jpy, model)


BAD = {"事務的つなぎ": r"続いて|ここからは|次は|それでは|では、", "聞き終え宣言": r"聞き終|すべて聞|全部聞", "番組終了挨拶": r"ありがとうございました|さようなら|またお会い|また次回|お別れ",
       "構造ラベル": r"Part ?\d|Full Story|第\d部|本文\d", "文数断定": r"一文で|ひとことで|一言で|one sentence", "数字/ASCII": r"[0-9０-９A-Za-z]"}


def sents(t): return [s for s in re.split(r"(?<=[。!?!?])", t) if s.strip()]


def det(t):
    ss = sents(t)
    d = {"chars": nchars(t), "within_67": nchars(t) <= LIMIT, "sentences": len(ss)}
    d["英語言及"] = "英語" in t
    d["bad"] = [k for k, rx in BAD.items() if re.search(rx, t)]
    return d


def metrics():
    rows = [json.loads(l) for l in open(f"{OUT}/generations.jsonl", encoding="utf-8")]
    for r in rows: r["det"] = det(r["text"] or "")
    json.dump(rows, open(f"{OUT}/metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in rows:
        d = r["det"]; print(r["round"], r["cand"], r["run"], d["chars"], "OK" if d["within_67"] else "OVER", d["sentences"], "EN" if d["英語言及"] else "--", d["bad"])


if __name__ == "__main__":
    m = sys.argv[1]
    {"prompts": lambda: prompts(int(sys.argv[2])), "gen": lambda: gen(int(sys.argv[2])), "metrics": metrics}[m]()
