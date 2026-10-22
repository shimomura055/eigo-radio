# -*- coding: utf-8 -*-
"""FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01: Trial専用 共通部(Productionは一切import/変更しない)。
モデル表・単価・各provider呼出・費用台帳・STOP確認・出力パーサ。"""
import json, os, re, time, hashlib, threading
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "er098_output" / "kp_six_model_trial_01"
load_dotenv(ROOT / ".env")
USD_JPY = 160.0   # er009_n1_routing_governance_10_actual_model_cost.py:20 USD_TO_JPY(プロジェクト既定。実為替ではない)
MAX_OUT = 16000   # 全モデル同一(推論token込みで切れない十分な値)
TIMEOUT = 900

MODELS = {
 "m1_gpt-6-luna":            dict(no=1, label="GPT-6 Luna(現行)", provider="openai", model_id="gpt-6-luna"),
 "m2_gpt-6.1-sol":           dict(no=2, label="GPT-6.1 Sol", provider="openai", model_id="gpt-6.1-sol"),
 "m3_gemini-3.1-flash-lite": dict(no=3, label="Gemini 3.1 Flash-Lite", provider="gemini", model_id="gemini-3.1-flash-lite"),
 "m4_gemini-3.5-flash-lite": dict(no=4, label="Gemini 3.5 Flash-Lite", provider="gemini", model_id="gemini-3.5-flash-lite"),
 "m5_claude-haiku-5-5":      dict(no=5, label="Claude Haiku 5.5", provider="anthropic", model_id="claude-haiku-5-5"),
 "m6_claude-sonnet-5-5":     dict(no=6, label="Claude Sonnet 5.5", provider="anthropic", model_id="claude-sonnet-5-5"),
}
# USD/1M tokens (input, cached_input, output[thinking込み]) と出典(公式pricingページ取得2026-10-22)
PRICES = {
 "gpt-6-luna":   (0.10, 0.01, 0.50, "er005_output/cost_baseline_01/pricing_snapshot.json / er009_n1_routing_governance_10_actual_model_cost.py:30(既存登録・公式転記)"),
 "gpt-6.1-sol":  (2.00, 0.10, 10.00, "pricing_snapshot.json(OFFICIAL_PRICING_PAGE_FETCHED 2026-10-09) / er009:34"),
 "gemini-3.1-flash-lite": (0.25, 0.025, 1.50, "https://ai.google.dev/gemini-api/docs/pricing 取得2026-10-22 HTTP200 raw html sha256=15c317ac3da417c91bae88cbe4d82080e46bbb0c14a28a817464c93550a8b84a(text入力$0.25/出力thinking込み$1.50)"),
 "gemini-3.5-flash-lite": (0.30, 0.03, 2.50, "https://ai.google.dev/gemini-api/docs/pricing 取得2026-10-22(同上sha)。pricing_snapshot.json登録値と一致"),
 "claude-haiku-5-5": (0.10, 0.01, 0.50, "https://platform.claude.com/docs/en/about-claude/pricing 取得2026-10-22 HTTP200 raw html sha256=09841544bbd5c051838ad021fa78df5b05baae6037015c433a8718d72c59e18b(prompt<=100kの単価)"),
 "claude-sonnet-5-5": (2.00, 0.10, 10.00, "https://platform.claude.com/docs/en/about-claude/pricing 取得2026-10-22(同上sha)"),
}

def sha_text(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def key(name):
    k = os.environ.get(name)
    if not k: raise RuntimeError("env %s 未設定(値は出力しない)" % name)
    return k

def stop_present(run_dir=OUT):
    """STOP/STOP_ALLセンチネル(run dir・リポジトリ既定位置)"""
    for p in (Path(run_dir) / "STOP", Path(run_dir) / "STOP_ALL", ROOT / "er026_output" / "family_z_production_e2e_01" / "STOP_ALL"):
        if p.exists(): return str(p)
    return None

_LOCK = threading.Lock()
LEDGER = OUT / "paid_calls.jsonl"
def cost_usd(model_id, usage):
    p = PRICES[model_id]
    it = usage.get("input_tokens") or 0; ct = usage.get("cached_tokens") or 0; ot = usage.get("output_tokens") or 0
    return (max(it - ct, 0) * p[0] + ct * p[1] + ot * p[2]) / 1e6
def ledger_add(rec):
    with _LOCK:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with open(LEDGER, "a", encoding="utf8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
def ledger_total_jpy():
    if not LEDGER.exists(): return 0.0
    t = 0.0
    for ln in LEDGER.read_text(encoding="utf8").splitlines():
        if ln.strip(): t += json.loads(ln).get("cost_jpy") or 0
    return t

class TechnicalError(Exception): pass

def build_body(provider, model_id, user, system=None, extra=None):
    """Provider既定: 温度・推論設定・thinkingConfigは送らない。max tokensのみ全モデル同一。"""
    if provider == "openai":
        b = dict(model=model_id, input=user, max_output_tokens=MAX_OUT)
        if system: b["instructions"] = system
    elif provider == "anthropic":
        b = dict(model=model_id, max_tokens=MAX_OUT, messages=[{"role": "user", "content": user}])
        if system: b["system"] = system
    elif provider == "gemini":
        b = dict(contents=[{"role": "user", "parts": [{"text": user}]}], generationConfig={"maxOutputTokens": MAX_OUT})
        if system: b["systemInstruction"] = {"parts": [{"text": system}]}
    else: raise ValueError(provider)
    if extra: b.update(extra)
    return b

def call_once(provider, model_id, body):
    """-> (text, usage, response_id, model_returned, raw, finish)"""
    if provider == "openai":
        from openai import OpenAI
        try:
            resp = OpenAI(api_key=key("OPENAI_API_KEY"), timeout=TIMEOUT, max_retries=0).responses.create(**body)
        except Exception as e:
            raise TechnicalError("openai:%s:%s" % (type(e).__name__, str(e)[:300]))
        u = resp.usage
        usage = dict(input_tokens=getattr(u, "input_tokens", None), output_tokens=getattr(u, "output_tokens", None),
                     reasoning_tokens=getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                     cached_tokens=getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0)
        raw = resp.model_dump()
        return resp.output_text, usage, resp.id, getattr(resp, "model", None), raw, raw.get("status")
    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        h = {"anthropic-version": "2023-06-01", "content-type": "application/json", "x-api-key": key("ANTHROPIC_API_KEY")}
    else:
        url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model_id
        h = {"content-type": "application/json", "x-goog-api-key": key("GEMINI_API_KEY")}
    try:
        r = requests.post(url, headers=h, json=body, timeout=TIMEOUT)
    except Exception as e:
        raise TechnicalError("net:%s:%s" % (type(e).__name__, str(e)[:200]))
    try: j = r.json()
    except Exception: j = {"_non_json": r.text[:500]}
    if r.status_code != 200:
        raise TechnicalError("HTTP%s:%s" % (r.status_code, json.dumps(j, ensure_ascii=False)[:300]))
    if provider == "anthropic":
        txt = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
        u = j.get("usage", {}); cr = u.get("cache_read_input_tokens", 0) or 0; cc = u.get("cache_creation_input_tokens", 0) or 0
        usage = dict(input_tokens=(u.get("input_tokens", 0) or 0) + cr + cc, output_tokens=u.get("output_tokens", 0), reasoning_tokens=None, cached_tokens=cr,
                     cache_creation_tokens=cc, thinking_blocks=sum(1 for b in j.get("content", []) if b.get("type") in ("thinking", "redacted_thinking")))
        return txt, usage, j.get("id"), j.get("model"), j, j.get("stop_reason")
    cands = j.get("candidates") or [{}]
    parts = (cands[0].get("content") or {}).get("parts", [])
    txt = "".join(x.get("text", "") for x in parts if not x.get("thought"))
    u = j.get("usageMetadata", {}); th = u.get("thoughtsTokenCount", 0) or 0
    usage = dict(input_tokens=u.get("promptTokenCount", 0), output_tokens=(u.get("candidatesTokenCount", 0) or 0) + th, reasoning_tokens=th,
                 cached_tokens=u.get("cachedContentTokenCount", 0) or 0)
    return txt, usage, j.get("responseId"), j.get("modelVersion"), j, cands[0].get("finishReason")

def call_with_retry(provider, model_id, body, max_tech_retries=2):
    """技術的失敗(timeout/5xx/429/net)のみ同一入力で最大2回再試行。品質理由の再生成はしない。"""
    attempts = []
    for i in range(1 + max_tech_retries):
        t0 = time.time()
        try:
            txt, usage, rid, mret, raw, fin = call_once(provider, model_id, body)
            attempts.append(dict(attempt=i + 1, ok=True, elapsed_s=round(time.time() - t0, 2)))
            return dict(ok=True, text=txt, usage=usage, response_id=rid, model_returned=mret, raw=raw, finish=fin, attempts=attempts)
        except TechnicalError as e:
            msg = str(e); attempts.append(dict(attempt=i + 1, ok=False, error=msg, elapsed_s=round(time.time() - t0, 2)))
            retryable = bool(re.search(r"HTTP(429|5\d\d)|net:|[Tt]imeout|RateLimit|APIConnection|InternalServer|[Oo]verloaded|rate", msg))
            if not retryable or i == max_tech_retries: break
            time.sleep(5 * (i + 1))
    return dict(ok=False, attempts=attempts)

# ---------------- 出力パーサ(Trial専用。Promptには形式指示を足さず、出力テキストから抽出)
_CNT = re.compile(r"[（(\[]\s*(\d+)\s*(?:語|words?|w)\s*[)）\]]|[:：,，/]\s*(\d+)\s*(?:語|words?)|(?:^|\s)(\d+)\s*(?:語|words?)", re.I)
_REJECT = re.compile(r"不採用|除外|本文外|差し替え|見つから|修正候補|変形|対象外")
def _strip_md(s): return s.replace("**", "").replace("__", "").replace("`", "")
def _phrase_of(body):
    body = body.strip()
    cm = _CNT.search(body)
    self_count = int([g for g in cm.groups() if g][0]) if cm else None
    cut = re.split(r"\s*[（(\[]|\s+[—–―]\s+|\s+-\s+|\s*→\s*|\s*：|:(?=\s|[^\x00-\x7f])|\s*\|\s*|\s{2,}", body, maxsplit=1)[0]
    cut = cut.strip().strip("「」『』“”\"'‘’").strip()
    cut = re.sub(r"[\s,;:]+$", "", cut)
    return cut, self_count

def parse_groups(text):
    """出力テキストを番号付きリスト/表/箇条書きのグループに分ける。-> list of groups(list of dict(phrase,self_count,line,rejected))"""
    groups = []; cur = None; last_n = None; kind = None
    bullets = []
    for ln in text.splitlines():
        s = _strip_md(ln.rstrip())
        if not s.strip():
            continue
        st = s.lstrip()
        if st.startswith("|"):
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            item = None
            if len(cells) >= 2 and re.match(r"^\d+\s*(?:語|words?)?$", cells[1]):
                item = "%s (%s語)" % (cells[0], re.match(r"\d+", cells[1]).group(0))
            elif len(cells) >= 2 and re.match(r"^\d+\s*$", cells[0]):
                item = cells[1] + (" (%s語)" % re.match(r"\d+", cells[2]).group(0) if len(cells) > 2 and re.match(r"^\d+", cells[2]) else "")
            if item is not None and not re.match(r"^[-:\s]+$", cells[0]):
                if kind != "table" or cur is None:
                    cur = []; groups.append(cur); kind = "table"
                cur.append(item); last_n = None
            continue
        if kind == "table": kind = None; cur = None
        m = re.match(r"^\s{0,3}(?:#+\s*)?(?:\(?(\d{1,2})[.)）:：、]\s*|(?:No\.?|Key Phrase)\s*(\d+)[.:：]\s*)(.+)$", s, re.I)
        if m:
            n = int(m.group(1) or m.group(2) or 0)
            if cur is None or kind != "num" or (last_n is not None and n <= last_n):
                cur = []; groups.append(cur); kind = "num"
            cur.append(m.group(3)); last_n = n
            continue
        m = re.match(r"^\s{0,3}[-*•・]\s+(.+)$", s)
        if m and not s.startswith("    "):
            bullets.append(m.group(1))
    out = []
    for g in groups:
        items = []
        for body in g:
            ph, sc = _phrase_of(body)
            items.append(dict(phrase=ph, self_count=sc, line=body.strip(), rejected=bool(_REJECT.search(body)) or not re.search(r"[A-Za-z]", ph)))
        out.append(items)
    if not out and bullets:
        out.append([dict(zip(("phrase", "self_count"), _phrase_of(b)), line=b, rejected=False) for b in bullets])
    return out

def parse_candidates(text, info=None, force_group=None):
    """最終提示リスト=最後の(有効3件以上の)グループ。無ければ有効件数最大のグループ(同数は後方)。却下表記・英字なし項目は除外。
    自己申告語数が無い項目は、同一phraseを持つ他グループの申告値を補完。infoにグループ構成を返す。"""
    groups = parse_groups(text)
    valid = [[c for c in g if not c["rejected"]] for g in groups]
    pick = None
    if force_group is not None and force_group < len(valid): pick = force_group
    for gi in range(len(valid) - 1, -1, -1):
        if pick is not None: break
        if len(valid[gi]) >= 3: pick = gi; break
    if pick is None and valid:
        mx = max(len(v) for v in valid)
        if mx > 0: pick = max(i for i, v in enumerate(valid) if len(v) == mx)
    if pick is None:
        if info is not None: info.update(n_groups=len(groups), picked=None, multi_draft=False)
        return []
    res = [dict(c) for c in valid[pick]]
    lookup = {}
    for g in groups:
        for c in g:
            if c["self_count"] is not None: lookup.setdefault(c["phrase"].lower(), c["self_count"])
    for c in res:
        if c["self_count"] is None: c["self_count"] = lookup.get(c["phrase"].lower())
    if info is not None:
        sizes = [len(v) for v in valid]
        phr = [tuple(x["phrase"].lower() for x in v) for v in valid if v]
        info.update(n_groups=len(groups), picked=pick, group_valid_sizes=sizes, multi_draft=len(set(phr)) > 1)
    return res
