# NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01b: ニュアンス解説Prompt品質Trial (DEV/Trial専用。Production非参照・Production/公開物/既存出力は読み取りのみ)
# 使い方:
#   py -3 nuance_trial_01.py dry-run                 # API 0: 対象読込・Prompt生成・sha/長さ
#   NUANCE_TRIAL_PAID=1 py -3 nuance_trial_01.py gen v1      # 有料: 全対象を1回生成(retryなし)+重複検査2段
#   NUANCE_TRIAL_PAID=1 py -3 nuance_trial_01.py gen v2 t1 t2   # v2を指定targetのみ(同一対象の再生成は最大1回)
# 費用: usage_log_01.jsonlに呼出ごとに記録。累計(実績+未決予約)がCAP_JPYを超える見込みの呼出は拒否。
import sys, os, re, json, html, hashlib, time, threading, unicodedata
BASE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", "..", ".."))
CAP_JPY = 10.0; USD_JPY = 160.0
MODEL = "gpt-6-luna"   # 本番ライン既定(er006_model_routing_contract_01.py:50 SUPPORT_MODEL / er003_v1_n3_01_scaffold_generate.py:61 _a2_support_model)
USAGE_LOG = os.path.join(OUT, "usage_log_01.jsonl")

# ---------------- 対象読込 ----------------
def _rd(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def _strip(s):
    s = re.sub(r"<br\s*/?>", "\n", s); s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("⏸", "")
    s = re.sub(r"[ \t]+\n", "\n", s); s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()
def full_story_from_html(htm):
    """公開htmlの行表から Full Story Part N / full_story_partN_* 行のscript(英文)を順に連結"""
    parts = []
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", htm, flags=re.S):
        row = m.group(1)
        nm = re.search(r"<b>([^<]*)</b>", row)
        if not nm or not re.match(r"(?i)full[ _]story[ _]part\s*\d", nm.group(1)): continue
        sc = re.search(r"<div class='script'>(.*?)</div>", row, flags=re.S)
        if sc: parts.append(_strip(sc.group(1)))
    return parts
def kp_from_confirmed(path):
    j = json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    assert j.get("state") == "live"
    return [dict(expr=it["key_phrase"], display=it.get("display_phrase"), gloss=it.get("japanese_gloss"), slot=it.get("slot"), kind=it.get("kind")) for it in j["items"]], j["confirmation_id"]
def kp_from_paycheck_html(htm, level_marker, next_marker):
    # 公開済みpaycheck e2e_02: HR form導入前の公開KP(各レベルのKey Phrase N行の英語KP)
    a = htm.find(level_marker); assert a >= 0
    b = htm.find(next_marker, a + 10) if next_marker else -1
    seg = htm[a:] if b < 0 else htm[a:b]
    items = []
    for m in re.finditer(r"<b>Key Phrase \d</b>.*?<table class='kp'>.*?</tr><tr><td>(.*?)</td><td>(.*?)</td></tr></table>", seg, flags=re.S):
        items.append(dict(expr=_strip(m.group(1)), display=_strip(m.group(1)), gloss=_strip(m.group(2)), slot="kp", kind="phrase"))
    return items
def y_text(level):
    j = json.load(open(os.path.join(ROOT, f"er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01_s23f/{level}/parts.json"), encoding="utf-8"))
    return "\n\n".join(j["segments"][k] for k in j["y_segment_order"]), j["title"]
def sec(htm, start, end=None):
    a = htm.find(start); assert a >= 0, start
    b = htm.find(end, a + 5) if end else -1
    return htm[a:] if b < 0 else htm[a:b]

def load_targets():
    T = {}
    ai = _rd("user_test/family_x_ai_island_form_01/index.html")
    AIB = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"
    for lv, lab, h, nx, cf in [("std", "Standard", "<h2 id='std'>", "<h2 id='adv'>", "a2"), ("adv", "Advanced", "<h2 id='adv'>", "<h2 id='pww'>", "b1b")]:
        body = "\n\n".join(full_story_from_html(sec(ai, h, nx)))
        kp, cid = kp_from_confirmed(f"{AIB}/{cf}/audit/confirmed_selection.json")
        T[f"ai_island_{lv}"] = dict(family="X", article="ai_island_temple", title="The Island Resets! But AI Has “Strategy Notes”", level=lab, body=body, kp=kp,
                                   basis=dict(status="confirmed", source_path=f"{AIB}/{cf}/audit/confirmed_selection.json", confirmation_id=cid, text_source="user_test/family_x_ai_island_form_01/index.html (公開済み、Local Rewrite適用後)"))
    pc = _rd("user_test/paycheck_personality_e2e_02/index.html")
    for lv, lab, h, nx in [("std", "Standard", "<h2>Standard", "<h2>Advanced"), ("adv", "Advanced", "<h2>Advanced", None)]:
        s = sec(pc, h, nx)
        T[f"paycheck_{lv}"] = dict(family="X", article="paycheck_personality", title="Does a Higher Income Make You More Hardworking? Compare Yourself with Who You Were Yesterday", level=lab,
                                   body="\n\n".join(full_story_from_html(s)), kp=kp_from_paycheck_html(pc, h, nx),
                                   basis=dict(status="confirmed", source_path="user_test/paycheck_personality_e2e_02/index.html (公開済みKey Phrase行。HR form導入前の公開確定KP。confirmed_selection.json無し)", text_source="user_test/paycheck_personality_e2e_02/index.html"))
    ZB = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_voice_fenrir_01"
    for lv, lab, f, cf in [("std", "Standard", "standard.html", "a2"), ("adv", "Advanced", "advanced.html", "b1b")]:
        h = _rd(f"user_test/family_z_tell_tale_heart_reselect_01/{f}")
        kp, cid = kp_from_confirmed(f"{ZB}/{cf}/audit/confirmed_selection.json")
        T[f"tth_{lv}"] = dict(family="Z", article="the_tell_tale_heart", title="The Tell-Tale Heart", level=lab, body=" ".join(full_story_from_html(h)).replace("  ", " "), kp=kp,
                              basis=dict(status="confirmed", source_path=f"{ZB}/{cf}/audit/confirmed_selection.json", confirmation_id=cid, text_source=f"user_test/family_z_tell_tale_heart_reselect_01/{f} (公開済み)"))
    YB = "er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01_s23f"
    for lv, lab, cf in [("std", "Standard", "a2"), ("adv", "Advanced", "b1b")]:
        body, ttl = y_text(cf)
        kp, cid = kp_from_confirmed(f"{YB}/{cf}/audit/confirmed_selection.json")
        T[f"y_redelivery_{lv}"] = dict(family="Y", article="redelivery_fee", title=ttl, level=lab, body=body, kp=kp,
                                       basis=dict(status="confirmed", source_path=f"{YB}/{cf}/audit/confirmed_selection.json", confirmation_id=cid, text_source=f"{YB}/{cf}/parts.json (y_segment_order連結。Yは未公開・ユーザー最終試聴待ちの既存完成run)"))
    return T
CONTROL = dict(family="-", article="synthetic_control", title="A Quiet Morning", level="Standard", basis=dict(status="synthetic", source_path="(診断用の人工テキスト。実記事ではない。0件が出せるかの確認用)"),
    body="Mika woke up at seven. She washed her face and made toast. Her cat sat by the window. It looked at the birds. Mika ate her toast and drank some tea. Then she took the bus to school. The bus was full, so she stood. At school, she met her friend Ken. They talked about the homework.",
    kp=[dict(expr="wake up", display="woke up", gloss="目を覚ます", slot="kp", kind="phrase"), dict(expr="by the window", display="by the window", gloss="窓のそば", slot="kp", kind="phrase"),
        dict(expr="take the bus", display="took the bus", gloss="バスに乗る", slot="kp", kind="phrase"), dict(expr="meet", display="met", gloss="会う", slot="vocab", kind="word"), dict(expr="homework", display="homework", gloss="宿題", slot="vocab", kind="word")])

# ---------------- Prompt ----------------
LEVEL_NOTE = {"Standard": "Standard(CEFR A2を目標に書かれた英文。学習者はA2〜B1相当の日本語話者)", "Advanced": "Advanced(CEFR B1を目標に書かれた英文。学習者はB1〜B2相当の日本語話者)"}
PROMPT_V1 = """あなたは英語学習コンテンツの編集者です。下の英語ポッドキャスト台本を読んだ学習者向けに、「ニュアンス解説」を日本語で最大1件だけ作ってください。学習価値のある候補がなければ0件にしてください。

# 記事・レベル
- 記事: {title}
- レベル: {level_note}

# 本文(引用では段落番号を付けない)
{body}

# 選定済みのKey Phrase・Word(別コーナーで解説済み。{n_kp}件)
{kp_block}

# ニュアンス解説とは
英語表現の微妙な意味の違い、語感、文脈による意味や印象の違いなど、日本語話者が辞書の訳語だけでは気づきにくい差を扱う解説です。扱える焦点の例:
(a) 近い表現との使い分け(強さ・丁寧さ・硬さ・肯定的/否定的な含み)
(b) 同じ語・構文でも文脈で意味や印象が変わる点
(c) 語の選択・助動詞・副詞などで変わる、話し手の態度や確信度の違い
(d) 日本語の訳語に引きずられると誤解しやすい点

# 最重要条件: 上のKey Phrase・Wordと重複しないこと
- 解説の「中心的な学習対象・論点(焦点)」が、上のKey Phrase・Wordのどれとも実質的に同じであってはならない。
- 表現の文字列が違っても、実質的に同じ内容を教えるなら重複とみなす(例: あるKey Phraseの類義語との違いを説明する、同じ語の別の用法を説明する)。
- 解説文の中にKey Phrase・Wordが一言登場するだけなら問題ない。ただし主役にしない。
- 本文のKey Phrase・Wordを含む文から選ぶ場合も、焦点が明確に別の語・論点であることを確かめる。

# 選ばないもの(該当する候補しかなければ0件にする)
- 品詞・語形・基礎語の文法的な違いの説明(例: 形容詞と名詞の違いだけ)
- 物語や記事内容の感想・解釈・テーマ論
- 辞書を引けば足りる語義の説明、よくある組み合わせの紹介(Key Phraseコーナーの役割)
- 文の構造・語順の解説(別の「文法・文構造」コーナーの役割)
- 本文に根拠がない一般論、学習者のレベルに見合わない細かすぎる差
- 無理に1件にするための選定。迷うなら0件にする。

# 手順(内部で考え、出力は最後のJSONのみ)
1. 本文から上の焦点に当てはまる候補を最大4つ挙げ、それぞれの焦点を1行で書く。
2. 各候補の焦点をKey Phrase・Word全件と照合し、重複するものを外す。
3. 残った候補から、このレベルの学習者が実際に誤解や使い分けで迷いやすく、学習価値が最も高い1件を選ぶ。価値が明確でなければ選ばず0件にする。

# 出力(JSONのみ。前置き・コードフェンスなし。日本語は読みやすく)
{{
  "rejected_candidates": [{{"expression": "外した候補の英語表現", "focus": "焦点を日本語1行", "reason": "kp_word_overlap または low_value または not_nuance または too_basic または other", "note": "理由を一言"}}],
  "candidate": null または {{
    "expression": "解説の中心的な学習対象の英語表現。比較なら 'A vs B'",
    "focus": "学習上の焦点を日本語1行(40字程度まで)",
    "quote_en": "本文から一字一句そのまま引用した英文(1〜2文。改変・要約・つなぎ合わせ禁止)",
    "quote_ja": "quote_enの日本語訳",
    "explanation_ja": "日本語の解説。120〜260字。比較する表現・場面を最低1つ具体的に示し、何がどう違うか(語感・印象・使い分け)を書く。Key Phrase・Wordの解説の繰り返しにしない",
    "differs_from_kp_word_ja": "Key Phrase・Wordのどれとも焦点が異なる理由を1文",
    "learning_value_self_rating": "high または mid または low(lowなら候補にせず0件にする)",
    "learning_value_reason_ja": "なぜこのレベルの学習者に価値があるかを1文"
  }},
  "no_candidate_reason_ja": "candidateがnullのときだけ理由を1〜2文。候補ありならnull"
}}

# 制約
- quote_enは本文に実在する文字列のみ。本文にない表現・事実・登場人物の言動を作らない。
- 解説の事実(語義・用法)は一般に認められた英語の用法に基づき、断定しすぎない。
- 理解度チェック・クイズ・感想は書かない。
"""

PROMPT_JUDGE = """あなたは英語学習コンテンツの重複検査員です。下の「ニュアンス解説の候補」が、「選定済みKey Phrase・Word」のいずれかと学習上の焦点で重複していないかを判定してください。

# 判定基準(ユーザー承認済みの規則)
- 単語の文字列一致ではなく、解説の学習上の焦点で判定する。
- 候補の解説文中にKey Phrase・Wordが登場すること自体は問題ない。
- ただし、候補の中心的な学習対象・論点が、Key Phrase・Wordのいずれかと同じ場合は不可(fail)。
- 表現が異なっていても、実質的に同じ内容(同じ語義・用法・使い分け)を教える場合は重複(fail)。
- 表現が含まれていても、解説の焦点が明確に別であれば許容(pass)。

# ニュアンス解説の候補
- 表現: {expression}
- 焦点: {focus}
- 本文引用: {quote_en}
- 解説: {explanation_ja}

# 選定済みKey Phrase・Word({n_kp}件)
{kp_block}

# 出力(JSONのみ。前置き・コードフェンスなし)
{{
  "per_item": [{{"item": "Key Phrase/Wordの表現", "same_focus": true または false, "note": "同じ/別と判断した理由を一言"}}],
  "verdict": "pass または fail",
  "reason": "最終判断の理由を日本語1〜2文(failなら、どのKey Phrase・Wordと何が同じ焦点か)"
}}
per_itemは上のKey Phrase・Word全件を同じ順で列挙すること。1件でもsame_focusがtrueならverdictはfail。
"""

def kp_block(kp):
    return "\n".join(f"{i}. {k['expr']}" + (f"(本文中の形: {k['display']})" if k.get("display") and k["display"] != k["expr"] else "") + (f" = {k['gloss']}" if k.get("gloss") else "") + f" [{k.get('slot')}]" for i, k in enumerate(kp, 1))
def build_prompt(tpl, t):
    return tpl.format(title=t["title"], level_note=LEVEL_NOTE[t["level"]], body=t["body"], n_kp=len(t["kp"]), kp_block=kp_block(t["kp"]))

# ---------------- 構造検査(重複検査 段1) ----------------
STOP = set("a an the to of in on at for with from by and or one's ones someone something somebody anyone people person be is are was were been being it its this that".split())
LIGHT = set("make take get go have do come give put let be".split())
def stem(w):
    w = w.lower().replace("’", "'")
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf): return w[: -len(suf)]
    return w
def toks(s):
    s = unicodedata.normalize("NFKC", s).replace("’", "'")
    return {stem(w) for w in re.findall(r"[A-Za-z']+", s) if w.lower() not in STOP and w.lower() not in ("vs", "versus")}
def split_exprs(expr):
    return [p.strip() for p in re.split(r"\s+vs\.?\s+|\s+versus\s+|/|,|\bor\b|↔", expr) if p.strip()]
def structural_check(expression, kp):
    """候補expression(比較なら各側)とKP/Word(expr+display)の content token を比較。片方が他方の部分集合(軽動詞のみ一致は除く)なら一致。"""
    matched = []
    lightstems = {stem(x) for x in LIGHT}
    for part in split_exprs(expression):
        A = toks(part)
        if not A: continue
        for k in kp:
            for ref in {k["expr"], k.get("display") or k["expr"]}:
                B = toks(ref)
                if not B: continue
                inter = A & B
                if not inter or inter <= lightstems: continue
                if A <= B or B <= A:
                    matched.append(dict(candidate_part=part, kp=k["expr"], shared=sorted(inter)))
    seen = set(); out = []
    for m in matched:
        key = (m["candidate_part"], m["kp"])
        if key not in seen: seen.add(key); out.append(m)
    return dict(verdict=("fail" if out else "pass"), matched=out)
def norm_q(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s).replace("’", "'").replace("“", '"').replace("”", '"')).strip()
def quote_ok(q, body):
    return bool(q) and norm_q(q) in norm_q(body)

# ---------------- LLM呼出 + 費用 ----------------
_lock = threading.Lock(); _reserved = [0.0]
def spent():
    if not os.path.exists(USAGE_LOG): return 0.0
    return sum(json.loads(l)["cost_jpy"] for l in open(USAGE_LOG, encoding="utf-8") if l.strip())
def hard_cost(prompt, maxout): return (len(prompt) * 0.10 / 1e6 + maxout * 0.50 / 1e6) * USD_JPY
def call_llm(prompt, tag, maxout):
    assert os.environ.get("NUANCE_TRIAL_PAID") == "1", "paid call refused (NUANCE_TRIAL_PAID=1 required)"
    hard = hard_cost(prompt, maxout)
    with _lock:
        if spent() + _reserved[0] + hard > CAP_JPY: raise RuntimeError(f"CAP refused: spent={spent():.3f} reserved={_reserved[0]:.3f} hard={hard:.3f} cap={CAP_JPY}")
        _reserved[0] += hard
    try:
        from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
        from openai import OpenAI
        c = OpenAI(); t0 = time.time()
        r = c.responses.create(model=MODEL, input=[{"role": "user", "content": prompt}], max_output_tokens=maxout)
        el = time.time() - t0; u = r.usage
        cached = getattr(u.input_tokens_details, "cached_tokens", 0)
        usd = (u.input_tokens - cached) * 0.10 / 1e6 + cached * 0.01 / 1e6 + u.output_tokens * 0.50 / 1e6
        rec = dict(tag=tag, model_requested=MODEL, model_actual=r.model, response_id=r.id, status=getattr(r, "status", None), elapsed_sec=round(el, 1),
                   prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), input_tokens=u.input_tokens, cached_input_tokens=cached, output_tokens=u.output_tokens,
                   reasoning_tokens=getattr(u.output_tokens_details, "reasoning_tokens", None), max_output_tokens=maxout, cost_usd=round(usd, 6), cost_jpy=round(usd * USD_JPY, 4))
        with _lock:
            open(USAGE_LOG, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
        os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)
        open(os.path.join(OUT, "raw", f"{tag}.txt"), "w", encoding="utf-8", newline="\n").write(r.output_text or "")
        return r.output_text or "", rec
    finally:
        with _lock: _reserved[0] -= hard
def parse_json(txt):
    a = txt.find("{"); b = txt.rfind("}")
    return json.loads(txt[a:b + 1])

# ---------------- 実行 ----------------
def run_target(key, t, ver, tpl):
    prompt = build_prompt(tpl, t)
    res = dict(target=key, version=ver, family=t["family"], article=t["article"], level=t["level"], kp_word_basis=dict(t["basis"], items=[k["expr"] for k in t["kp"]]), prompt_sha=hashlib.sha256(tpl.encode()).hexdigest())
    txt, u = call_llm(prompt, f"{ver}_{key}_gen", 9000); res["gen_usage"] = u; res["gen_raw"] = txt
    try: j = parse_json(txt)
    except Exception as e:
        res["error"] = f"gen_parse_error: {e}"; return res
    res["rejected_candidates"] = j.get("rejected_candidates"); res["no_candidate_reason"] = j.get("no_candidate_reason_ja"); cand = j.get("candidate")
    res["candidate_raw"] = cand
    if cand:
        res["quote_verbatim"] = quote_ok(cand.get("quote_en", ""), t["body"]); res["explanation_len"] = len(cand.get("explanation_ja", ""))
        s1 = structural_check(cand["expression"], t["kp"]); res["stage1_structural"] = s1
        jp = PROMPT_JUDGE.format(expression=cand["expression"], focus=cand["focus"], quote_en=cand["quote_en"], explanation_ja=cand["explanation_ja"], n_kp=len(t["kp"]), kp_block=kp_block(t["kp"]))
        jt, ju = call_llm(jp, f"{ver}_{key}_judge", 5000); res["judge_usage"] = ju; res["judge_raw"] = jt
        try:
            jj = parse_json(jt); res["stage2_llm"] = dict(verdict=jj.get("verdict"), reason=jj.get("reason"), per_item=jj.get("per_item"), model=ju["model_actual"])
        except Exception as e:
            res["stage2_llm"] = dict(verdict="error", reason=f"judge_parse_error: {e}", model=ju["model_actual"])
        v = "fail" if (s1["verdict"] == "fail" or res["stage2_llm"]["verdict"] != "pass" or not res["quote_verbatim"]) else "pass"
        res["final_overlap_verdict"] = v
    return res

def main():
    cmd = sys.argv[1]
    T = load_targets()
    if cmd == "dry-run":
        for k, t in T.items():
            p = build_prompt(PROMPT_V1, t)
            print(k, t["level"], "body_chars", len(t["body"]), "kp", [x["expr"] for x in t["kp"]], "prompt_chars", len(p), "est_hard_jpy", round(hard_cost(p, 9000), 3))
        print("prompt_v1_sha", hashlib.sha256(PROMPT_V1.encode()).hexdigest()); return
    if cmd == "dump-body":
        for k, t in T.items(): print("=====", k, t["level"]); print(t["body"]); print()
        return
    if cmd == "judge-probe":
        # 重複検査 段2(LLM)の感度確認: 人工の「重複候補」2件と「非重複候補」1件(いずれも合成。実生成物ではない)
        PROBES = [
            dict(id="probe_overlap_synonym", target="ai_island_std", cand=dict(expression="pass on", focus="情報や経験を次の期間・次の人に引き継ぐ意味", quote_en="the work area with the AI’s notes and programs carried over to the next hour",
                 explanation_ja="pass on は「次に渡す」、carry over は「持ち越す」です。どちらも前の時間の内容が次の時間に残ることを表しますが、pass on は人から人へ渡す場面で、carry over は期間をまたいで残る場面でよく使います。ここでは作業エリアが次の1時間に残ることを述べています。")),
            dict(id="probe_overlap_same_idiom_other_form", target="tth_std", cand=dict(expression="chill someone to the bone", focus="恐怖で体の芯が冷えるような強い衝撃を表す比喩", quote_en="That vulture’s eye made my blood turn cold.",
                 explanation_ja="この文は、目を見て語り手が強い恐怖を感じたことを、血が冷たくなるという体感の比喩で表しています。chill someone to the bone も同じ種類の比喩で、ぞっとする恐怖を表します。どちらも寒さを恐怖の強さにたとえる点が共通です。")),
            dict(id="probe_non_overlap", target="ai_island_std", cand=dict(expression="at least", focus="主張の範囲を限定し一般化を避ける at least", quote_en="For this AI, at least, remembering that way helped it build towers.",
                 explanation_ja="ここでの at least は数の下限ではなく、このAIについて言える範囲に主張を限る表現です。他のAIにも当てはまるとは言っていません。")),
        ]
        out = []
        for pb in PROBES:
            t = T[pb["target"]]; c = pb["cand"]
            s1 = structural_check(c["expression"], t["kp"])
            jp = PROMPT_JUDGE.format(expression=c["expression"], focus=c["focus"], quote_en=c["quote_en"], explanation_ja=c["explanation_ja"], n_kp=len(t["kp"]), kp_block=kp_block(t["kp"]))
            jt, ju = call_llm(jp, f"probe_{pb['id']}_judge", 5000)
            try: jj = parse_json(jt)
            except Exception as e: jj = dict(verdict="error", reason=str(e))
            out.append(dict(id=pb["id"], target=pb["target"], candidate=c, stage1=s1, stage2=jj, usage=ju))
        json.dump(out, open(os.path.join(OUT, "judge_probe_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("saved judge_probe_01.json spent_total_jpy", round(spent(), 4)); return
    if cmd == "gen":
        ver = sys.argv[2]; keys = sys.argv[3:] or list(T)
        T['control_trivial'] = CONTROL
        tpl = {"v1": PROMPT_V1}.get(ver) or __import__("nuance_prompt_v2").PROMPT_V2
        out = {}; ths = []
        def w(k):
            try: out[k] = run_target(k, T[k], ver, tpl)
            except Exception as e: out[k] = dict(target=k, version=ver, error=repr(e))
        for k in keys:
            th = threading.Thread(target=w, args=(k,)); th.start(); ths.append(th)
        for th in ths: th.join()
        p = os.path.join(OUT, f"results_{ver}.json")
        json.dump({k: out[k] for k in keys}, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("saved", p, "spent_total_jpy", round(spent(), 4))
if __name__ == "__main__": main()
