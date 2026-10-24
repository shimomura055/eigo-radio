# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-03専用script(DEV。Production非参照)。
# PROMPT_02(Trial-02)をbaseに、Part 1・Part 2ブロックだけ差替え、本文/KP/作品名は作品別に差替える。
# 使い方: py run_trial_03.py build [tag]  /  py run_trial_03.py send <tag> [<tag>...]   tag例: 03_gift 03_ig_nobel 03_open_window 02B_ig_nobel 02B_open_window
import sys, os, json, hashlib, difflib, re, time
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, BASE)
import run_trial_02 as t2
import run_trial_01 as t1

P1_03 = """## Part 1. Vocabulary & Expressions
上のKey Phrase 3件それぞれについて、次を書く: 1 英語表現 / 2 日本語の意味 / 3 本文中の英文(逐語引用) / 4 英文の日本語訳 / 5 実用性を重視した解説。
実用性重視の解説ルール: その表現が、本文以外のどのような場面で実際に使えるか、使うとどんなニュアンスが伝わるかを、具体的かつ簡潔に説明する。学習者が自分の英語表現に取り入れやすい説明にする。
- 日常生活だけでなく、仕事・社会での使用場面にも目を向ける。
- 比喩的・拡張的な用法が自然に存在する場合は、その用法も説明する(物理的な意味から抽象的な意味への広がりなど)。
- 具体的な使用場面を示し、似た表現との使い分けやニュアンスの違いが理解できるようにする。
- すべての表現に、仕事での用途や比喩表現を無理に当てはめない。自然に存在する用法だけを書き、不自然な用途・用法を創作しない。
- 文法の解説(構造・活用・語順など)に脱線せず、実用性を中心にする。文法構造はPart 2に任せる。
- 必要十分な説明量にし、文章の水増しをしない。
- 「ほかの場面で使うと」という独立した追加例文は書かない。実用場面は日本語の解説文で伝える。
"""
P2_03 = """## Part 2. Grammar & Sentence Structure
本文から、Advancedレベルの学習者でも読んで理解しにくい、または構造や意味をつかみにくいと考えられる一文を選び、その読解を助ける文法・構文解説を書く。選ぶ文は0〜2個。無理に2個選ばない。適切な文がなければ0個とし、その旨を一文で書く。
選定方針:
- 「Advancedの学習者でも、なぜその文は理解しにくいか」を基準に選ぶ。
- 基礎的な文法項目は、特殊な用法や重要な表現効果がない限り選ばない。
- 文法の高度さを競わない。判断基準は、解説によってその文の理解がどれだけ深まるか。
各項目で次を書く:
1 本文の英文(逐語引用)と日本語訳
2 学習者がなぜその文を理解しにくいか
3 どの文法・構文が理解を難しくしているか
4 その構文がどのような仕組みで成立しているか
5 通常の語順や別の表現との違い(比較のために本文にない英文を示す場合は「比較用」と明記し、本文の引用と区別する)
6 その違いによって、意味・ニュアンス・表現効果がどう変わるか
- 教科書的な一般説明だけで終わらず、この英文を読み解く助けになる説明にする。
"""

P1_03c = P1_03.replace("- 比喩的・拡張的な用法が自然に存在する場合は、その用法も説明する(物理的な意味から抽象的な意味への広がりなど)。",
 "- 各表現について、字義的・物理的な意味から広がった用法(仕事・社会・感情の場面での比喩的な用法など)が一般に自然に使われているかを確認する。使われている場合は、その用法も必ず説明する。使われていない場合は書かない。")
assert P1_03c != P1_03

P2_03b = """## Part 2. Grammar & Sentence Structure
本文から、Advancedレベルの学習者でも読んで理解しにくい、または構造や意味をつかみにくいと考えられる一文を選び、その読解を助ける文法・構文解説を書く。選ぶ文は0〜2個。無理に2個選ばない。適切な文がなければ0個とし、その旨を一文で書く。
選定方針:
- 本文全体から候補の文を複数検討し(検討過程は出力しない)、「解説によって、その文の理解がどれだけ深まるか」が最も大きい文を選ぶ。文法の高度さを競わない。
- 優先して検討する文: 日本語話者が一度読んだだけでは、主語・動詞・修飾関係・情報のつながりをつかみにくい文。例: 語順が通常と異なる文、長い修飾語句・挿入・省略・並列・比較表現が重なって構造が見えにくい文、字面どおりに読むと意味を取り違えやすく、構文の理解が必要な文。これらは例であり、該当する文が本文になければ無理に選ばない。
- 基礎的な文法項目(命令文、基本的な接続、前置詞句、分詞構文や付帯状況のwithなどの基本形、関係詞の基本用法、基本的な時制・受動態・比較・仮定法など)は、Advancedの学習者がすでに理解できるため、特殊な用法や重要な表現効果がない限り選ばない。
各項目で次を書く:
1 選定理由: この文を選んだ理由(Advancedの学習者でも理解しにくい点と、解説する学習価値)
2 本文の英文(逐語引用)と日本語訳
3 学習者がなぜその文を理解しにくいか
4 どの文法・構文が理解を難しくしているか
5 その構文がどのような仕組みで成立しているか(文の各部分が何の働きをしているかを、英文の部分を示して具体的に)
6 通常の語順や別の表現との違い(比較のために本文にない英文を示す場合は「比較用」と明記し、本文の引用と区別する)
7 その違いによって、情報の提示順序や焦点(何が先に示され、何が際立つか)、意味・ニュアンス・表現効果がどう変わるか。表現効果は、この作品の前後の文脈(対比・伏線・場面の流れなど)と結びつけて説明する。
- 教科書的な一般説明だけで終わらず、この英文を読み解く助けになる説明にする。
"""

def sub_once(s, old, new):
    assert s.count(old) == 1, (s.count(old), old[:60])
    return s.replace(old, new)

def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def paras_of(text, drop_in_one_line=False):
    ps = [p.strip() for p in text.split("\n\n") if p.strip()]
    title = ps[0]; body = ps[1:]
    if drop_in_one_line:
        i = [k for k, p in enumerate(body) if p.startswith("## In one line")]
        assert len(i) == 1
        body = body[:i[0]]
    return title, body

WORKS = {}
# gift: Trial-01/02と同一
WORKS["gift"] = None
OW = "er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/writer/r2.md"
IG = "er019_output/ig_nobel_2026/run_nws_02/b1b/article.md"
WORKS["open_window"] = dict(src=OW, label="The Open Window(『開いた窓』)", title="# The Open Window", dol=False, kp=[
 ("give way", "崩れる", "They tried to cross a bog, but the ground gave way beneath them.", "to break or collapse under pressure"),
 ("at a moment’s notice", "急なことにも即座に", "Inventing convincing stories at a moment’s notice was Vera’s speciality.", "with almost no warning or preparation"),
 ("keep someone company", "人の相手をする", "I hope Vera has kept you company!", "to spend time with someone so they are not alone"),
])
WORKS["ig_nobel"] = dict(src=IG, label="“Cockroach Milk”: Before You Reach for a Cup, Look at How It Stores Food(Family Xの解説記事・イグ・ノーベル賞2026)", title=None, dol=True, kp=[
 ("nutrient-rich crystals", "栄養豊富な結晶", "The Ig Nobel Prize went to research on nutrient-rich crystals that had been published earlier.", "crystals that contain many substances the body needs to stay healthy"),
 ("bound to the protein", "タンパク質に結びついた", "Fats were bound to the protein, and sugars were attached too.", "attached or joined to the protein"),
 ("leap into action", "すぐに行動を起こす", "At this point, the marketing team might be ready to leap into action, but hold on.", "to start doing something quickly and energetically"),
])

def kp_block(kp):
    return "\n".join(f"{i}. 英語表現: {k}\n   日本語gloss: {g}\n   本文の該当文: {s}\n   既存の音声解説(英語・重複回避用): \"{e}\"" for i, (k, g, s, e) in enumerate(kp, 1))

def build(work, ver):
    base = t2.PROMPT
    if work == "gift":
        p = base
        if ver == "03": body_text = t1.TEXT
    else:
        w = WORKS[work]
        text = read(w["src"])
        title, body = paras_of(text, w["dol"])
        for _, _, s, _ in w["kp"]:
            assert s in text, s
        numbered = "\n\n".join(f"[P{i}] {x}" for i, x in enumerate(body, 1))
        p = sub_once(base, "- 作品: The Gift of the Magi(『賢者の贈り物』)", "- 作品: " + w["label"])
        p = sub_once(p, t1.numbered, numbered)
        p = sub_once(p, f"[P1]〜[P{len(t1.body)}]", f"[P1]〜[P{len(body)}]")
        p = sub_once(p, kp_block(t1.KP), kp_block(w["kp"]))
    if ver in ("03", "03b", "03c"):
        s1 = p.index("## Part 1. Vocabulary"); e1 = p.index("\n## Part 2.")
        p = p[:s1] + (P1_03c if ver == "03c" else P1_03) + p[e1:]
        s2 = p.index("## Part 2. Grammar"); e2 = p.index("\n## Part 3.")
        p = p[:s2] + (P2_03 if ver == "03" else P2_03b) + p[e2:]
    return p

def tags():
    return [("03c", "gift"), ("03c", "ig_nobel"), ("03c", "open_window"), ("03b", "gift"), ("03b", "ig_nobel"), ("03b", "open_window"), ("03", "gift"), ("03", "ig_nobel"), ("03", "open_window"), ("02B", "ig_nobel"), ("02B", "open_window")]

def prompt_for(tag):
    ver, work = tag.split("_", 1)
    return build(work, "03c" if ver.startswith("03c") else ("03b" if ver.startswith("03b") else ("03" if ver == "03" else "02")))

def call(tag):
    from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
    from openai import OpenAI
    c = OpenAI(); P = prompt_for(tag); t0 = time.time()
    r = c.responses.create(model="gpt-6-luna", input=[{"role": "user", "content": P}])
    el = time.time() - t0
    open(os.path.join(BASE, f"OUTPUT_{tag.split('_',1)[0]}_{tag.split('_',1)[1]}_RAW.md"), "w", encoding="utf-8", newline="\n").write(r.output_text)
    u = r.usage
    d = {"tag": tag, "model_requested": "gpt-6-luna", "model_actual": r.model, "response_id": r.id, "elapsed_sec": round(el, 1),
         "prompt_sha256": hashlib.sha256(P.encode()).hexdigest(),
         "input_tokens": u.input_tokens, "cached_input_tokens": getattr(u.input_tokens_details, "cached_tokens", 0),
         "output_tokens": u.output_tokens, "reasoning_tokens": getattr(u.output_tokens_details, "reasoning_tokens", None),
         "reasoning_param": "not specified (provider default; same as Trial-01/02)"}
    unc = d["input_tokens"] - d["cached_input_tokens"]
    usd = unc*0.10/1e6 + d["cached_input_tokens"]*0.01/1e6 + d["output_tokens"]*0.50/1e6
    d["cost_usd"] = round(usd, 6); d["cost_jpy_at_160"] = round(usd*160, 4)
    json.dump(d, open(os.path.join(BASE, f"usage_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "build":
        assert build("gift", "02") == t2.PROMPT, "regression: gift/02 must equal PROMPT_02"
        for ver, work in tags():
            tag = f"{ver}_{work}"
            P = prompt_for(tag)
            open(os.path.join(BASE, f"_prompt_{tag}.txt"), "w", encoding="utf-8", newline="\n").write(P)
            print(tag, len(P), hashlib.sha256(P.encode()).hexdigest()[:16])
    elif mode == "send":
        from concurrent.futures import ThreadPoolExecutor
        ts = sys.argv[2:]
        with ThreadPoolExecutor(max_workers=len(ts)) as ex:
            for d in ex.map(call, ts): print(json.dumps(d, ensure_ascii=False))
