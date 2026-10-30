# ONE-STEP-FURTHER-CORNER-TRIAL-01 委任_03: DEV/Trial専用ライブラリ。Production code/Promptを編集しない。
# 読取専用importのみ: osf01_gen(入力データ取得・単価)、er003_key_phrase_source_gate_01.normalize_text(KP本文照合の正規化)
import sys, os, re, json, time, threading, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf01_gen as g1
from er003_key_phrase_source_gate_01 import normalize_text as nt
OUT = os.path.join(ROOT, "docs", "research", "ONE-STEP-FURTHER-CORNER-TRIAL-01", "out", "osf03"); os.makedirs(OUT, exist_ok=True)
USAGE = os.path.join(OUT, "usage_log_03.jsonl")
SOFT_CAP = 50.0; HARD_CAP = 70.0   # 委任文: 上限50円、到達見込みでも70円まで理由記録で継続
USD_JPY = 160.0
# 単価(USD/1M tokens: input, cached, output)。OpenAIはer009単価表(osf01_gen.PRICE)。Geminiは公開単価がrepo内に無いため【推定・保守的】(実請求と異なる可能性あり)
PRICE = dict(g1.PRICE); PRICE["gemini-4-argon"] = (5.0, 0.5, 25.0); PRICE["gemini-3.1-pro-preview"] = (2.0, 0.2, 12.0)
_lock = threading.Lock()
def spent():
    if not os.path.exists(USAGE): return 0.0
    return sum((json.loads(l).get("cost_jpy") or 0) for l in open(USAGE, encoding="utf-8") if l.strip())
def cost(model, u):
    ip, cp, op = PRICE[model]; i = u.get("input_tokens") or 0; c = u.get("cached_input_tokens") or 0; o = (u.get("output_tokens") or 0) + (u.get("thoughts_tokens") or 0)
    return round(((max(i - c, 0) * ip + c * cp + o * op) / 1e6) * USD_JPY, 4)
def _log(rec):
    with _lock, open(USAGE, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
def _guard():
    with _lock:
        if spent() > HARD_CAP: raise RuntimeError("HARD CAP refused")
_oai = None; _gem = None
def call_openai(model, prompt, tag, max_out=9000, effort=None):
    global _oai
    assert os.environ.get("OSF_PAID") == "1"; _guard()
    if _oai is None: _oai = g1.get_client()
    kw = {"reasoning": {"effort": effort}} if effort else {}
    t0 = time.time(); r = _oai.responses.create(model=model, input=[{"role": "user", "content": prompt}], max_output_tokens=max_out, **kw); el = round(time.time() - t0, 2)
    u = r.usage; ud = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None)}
    d = getattr(u, "input_tokens_details", None); ud["cached_input_tokens"] = getattr(d, "cached_tokens", 0) if d else 0
    text = getattr(r, "output_text", None) or ""; c = cost(model, ud)
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True); open(os.path.join(OUT, "raw", tag + ".txt"), "w", encoding="utf-8", newline="\n").write(text)
    _log({"tag": tag, "vendor": "openai", "model": r.model, "requested": model, "usage": ud, "cost_jpy": c, "elapsed_sec": el, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()})
    return text, c, el
def init_gemini():
    global _gem
    with _lock:
        if _gem is None:
            from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env")); from google import genai
            _gem = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _gem
def call_gemini(model, prompt, tag, think="LOW"):
    assert os.environ.get("OSF_PAID") == "1"; _guard(); init_gemini()
    from google.genai import types
    cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2, thinking_config=types.ThinkingConfig(thinking_level=think))
    t0 = time.time(); r = _gem.models.generate_content(model=model, contents=prompt, config=cfg); el = round(time.time() - t0, 2)
    um = r.usage_metadata; ud = {"input_tokens": um.prompt_token_count, "output_tokens": um.candidates_token_count, "thoughts_tokens": um.thoughts_token_count or 0, "cached_input_tokens": um.cached_content_token_count or 0}
    text = r.text or ""; c = cost(model, ud)
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True); open(os.path.join(OUT, "raw", tag + ".txt"), "w", encoding="utf-8", newline="\n").write(text)
    _log({"tag": tag, "vendor": "google", "model": model, "requested": model, "usage": ud, "cost_jpy": c, "elapsed_sec": el, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "price_is_estimate": True})
    return text, c, el
def parse(text):
    a, b = text.find("{"), text.rfind("}")
    return json.loads(text[a:b + 1])
# ---------------- 機械検査 ----------------
SLOTS = {"someone", "something", "somebody", "one's", "oneself", "someone's", "somewhere", "a", "an", "the", "to", "do", "doing", "sth", "sb", "one", "it", "of", "for", "on", "in", "at", "with", "by", "up", "out", "about", "be", "have", "get", "make", "take", "give", "put", "go"}
NEG = {"not", "no", "never", "n't", "cannot", "can't", "won't", "don't", "didn't", "couldn't", "wouldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't", "doesn't", "nobody", "nothing", "neither", "nor"}
MODAL = {"can", "could", "should", "must", "may", "might", "will", "would", "shall", "cannot", "can't", "couldn't", "won't", "wouldn't", "shouldn't", "need", "ought"}
def toks(s): return re.findall(r"[a-z]+(?:'[a-z]+)?", nt(s).replace("’", "'"))
IRREG = {"felt": "feel", "did": "do", "done": "do", "went": "go", "gone": "go", "made": "make", "took": "take", "taken": "take", "gave": "give", "given": "give", "got": "get", "gotten": "get", "said": "say", "told": "tell", "thought": "think", "knew": "know", "known": "know", "saw": "see", "seen": "see", "came": "come", "found": "find", "left": "leave", "kept": "keep", "held": "hold", "ran": "run", "put": "put", "let": "let", "met": "meet", "brought": "bring", "began": "begin", "begun": "begin", "heard": "hear", "meant": "mean", "stood": "stand", "lost": "lose", "paid": "pay", "sat": "sit", "was": "be", "were": "be", "been": "be", "is": "be", "are": "be", "am": "be", "had": "have", "has": "have", "wrote": "write", "written": "write", "spoke": "speak", "spoken": "speak", "chose": "choose", "chosen": "choose", "broke": "break", "broken": "break", "fell": "fall", "fallen": "fall", "grew": "grow", "grown": "grow", "drew": "draw", "drawn": "draw", "wore": "wear", "worn": "wear", "won": "win", "sent": "send", "built": "build", "spent": "spend", "understood": "understand", "sought": "seek", "slept": "sleep", "taught": "teach", "caught": "catch", "bought": "buy", "fought": "fight", "dealt": "deal"}
def stem(w):
    w = IRREG.get(w, w)
    w = re.sub(r"(ing|ed|es|s|d)$", "", w)
    return w[:5]
def numbered_sentences(body):
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    sents = []
    pat = re.compile("(?<=[.!?])[\"”’']?\\s+(?=[A-Z\"“‘'])")
    for p in paras:
        for s in pat.split(p.replace("\n", " ")):
            s = s.strip()
            if s: sents.append(s)
    return sents
def content_set(s): return {stem(w) for w in toks(s) if w not in SLOTS and len(w) > 2}
def check_extraction(c, body, kp_exprs, gram_texts):
    """Step1機械検査(KPの本文照合normalize_text流儀 / 表層形と原型の対応)。返り値: 不合格理由のリスト"""
    r = []
    q, ts, pr = c.get("quote", ""), c.get("target_span", ""), c.get("prototype", "")
    if not q or nt(q) not in nt(body): r.append("quote_not_in_body")
    if not ts or nt(ts) not in nt(q): r.append("target_span_not_in_quote")
    if ts and q and nt(ts) == nt(q) and len(toks(q)) > 8: r.append("whole_sentence_target")
    n = len(toks(pr))
    if n < 2 or n > 8: r.append(f"prototype_len_{n}")
    ts_stems = {stem(w) for w in toks(ts)}
    ok_slot = {"someone", "something", "somebody", "one's", "oneself", "someone's", "somewhere", "sth", "sb", "one", "a", "an", "the", "to", "do", "doing", "it"}
    stray = [w for w in toks(pr) if w not in ok_slot and w not in NEG and stem(w) not in ts_stems and not any(len(stem(w)) >= 3 and stem(w)[:3] == st[:3] for st in ts_stems)]
    if stray: r.append("prototype_has_words_not_in_span:" + ",".join(stray))
    tt, pt = set(toks(ts)), set(toks(pr))
    if (tt & NEG) and not (pt & NEG): r.append("negation_lost")
    if (tt & MODAL) and not (pt & MODAL): r.append("modal_lost")
    cs = content_set(pr)
    for e in kp_exprs:
        ce = content_set(e)
        if ce and cs and (ce <= cs or cs <= ce) and len(cs & ce) >= min(len(cs), len(ce)): r.append("overlap_kp:" + e); break
    for gt in gram_texts:
        if nt(pr) in nt(gt) and len(toks(pr)) >= 3: r.append("overlap_grammar"); break
    return r
def is_subseq(a, b):
    it = iter(b); return all(x in it for x in a)
def check_candidate(base_frame, further_frame, base_expr, further_expr, kp_exprs):
    """Step2/3の機械検査(NG3長文化のみ/NG5単語1つ置換/語順並べ替えのみ/KP重複)。返り値: 理由リスト"""
    r = []; bt, ft = toks(base_frame), toks(further_frame)
    if len(ft) - len(bt) > 4: r.append("further_frame_much_longer")
    if len(ft) > len(bt) + 2 and is_subseq(bt, ft): r.append("NG3_base_kept_and_extended")
    # 単語1つだけの差は、良例(make progress -> make headway)も該当するため機械では棄却せず、フラグとして監査(コロケーション拘束か自由な同義語置換か)へ渡す
    if len(bt) == len(ft) and sum(1 for x, y in zip(bt, ft) if x != y) == 1: r.append("FLAG_single_word_diff")
    if sorted(bt) == sorted(ft) and bt != ft: r.append("reorder_only")
    be, fe = toks(base_expr), toks(further_expr)
    if be and fe and sorted(be) == sorted(fe): r.append("expr_reorder_only")
    cs = content_set(further_expr)
    for e in kp_exprs:
        ce = content_set(e)
        if ce and cs and (ce <= cs or cs <= ce) and len(cs & ce) >= min(len(cs), len(ce)): r.append("overlap_kp:" + e); break
    if nt(further_expr) == nt(base_expr): r.append("same_as_base")
    return r
