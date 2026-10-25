# ============================================================
# er003_kp_source_sentence_ja_01.py
# FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16(2026-10-25)
# 学習テキスト Part 1「Vocabulary & Expressions」T1: 本文引用英文の日本語訳(専用翻訳工程、Family X/Z共通)
# ============================================================
# 承認: ユーザー2026-10-25 T1正式承認(原文 docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_07.md)。
#   - 入力は本文から引用した英文(source_sentence)だけ。gloss・解説・本文全体・KP英語表現・作品名は一切LLMへ渡さない。
#   - 解説LLM(er003_kp_general_explanation_01)とは独立(別module・別call・別保存file・別stage・別routing key)。
#   - 1 call/setでKP数分の文を訳す(出力はJSON id->訳)。技術retry1回→fail-closed(旧方式なし・空欄続行なし)。
#   - 再生成キー=引用英文(rank昇順)+Prompt sha+model。gloss・KP表現・解説の変更では再生成しない。
# このmoduleはdocs/researchのTrial資産をimportしない。
# ============================================================
from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata

import er006_model_routing_contract_01 as routing

MANAGEMENT_ID = "FAMILY-Z-STUDY-TEXT-TRIAL-01"
MODEL_ROUTING_PROCESS = "KEY_PHRASE_SOURCE_SENTENCE_JA"
MODEL = routing.SUPPORT_MODEL
SCHEMA_VERSION = "kp_source_sentence_ja_v1"
TRANSLATIONS_FILENAME = "kp_source_sentence_ja.json"

PROMPT_HEAD = """あなたは英日翻訳者です。英語学習者(日本語話者、B1〜B2相当)が読む学習ページに載せるため、下の英文それぞれを自然な日本語に訳してください。

# 訳し方
- 英文の意味を正確に訳す。意訳しすぎず、情報の追加・省略をしない。
- 日本語として自然で読みやすい文にする。
- 英文1つにつき、訳を1文(元の文が複数文なら対応する文数)で書く。解説・注釈・補足・前置きは書かない。

# 英文
"""
PROMPT_BODY = """
# 出力形式
JSONのみ(前後に文章やコードブロックを付けない)。各英文の番号をそのまま使う。
{"translations": [{"id": 1, "ja": "(1番の英文の日本語訳)"}, {"id": 2, "ja": "..."}]}
"""
PROMPT_TEMPLATE_SHA256 = hashlib.sha256((PROMPT_HEAD + "␟" + PROMPT_BODY).encode("utf-8")).hexdigest()

MAX_SENTENCES = 5
MAX_SENTENCE_CHARS = 400
MIN_JA_CHARS = 4

_CJK_RE = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿豈-﫿＀-￯]")
_KANA_RE = re.compile(r"[぀-ヿ]")
_CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")
# 既存ページ規則の前倒し適用(新しい品質判定ではない): er003_kp_general_explanation_01.PAGE_FORBIDDEN_REと同一パターン
PAGE_FORBIDDEN_RE = re.compile(r"\(A2\)|\(B1\)|B1B|English:|英語:|EN:|日本語:|JA:")
_ENUM_LINE_RE = re.compile(r"^(\d+)\. (.*)$")


class KpSourceSentenceJaError(RuntimeError):
    pass


class KpSourceSentenceJaInputError(ValueError):
    pass


class KpSourceSentenceJaIsolationViolation(KpSourceSentenceJaError):
    pass


class KpSourceSentenceJaStale(KpSourceSentenceJaError):
    pass


def _norm_match(s: str) -> str:
    n = unicodedata.normalize("NFKC", s or "").translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    return re.sub(r"\s+", " ", n).strip().lower()


# ------------------------------------------------------------
# 入力(引用英文のみ)
# ------------------------------------------------------------
def sorted_items(items: list) -> list:
    return sorted(items, key=lambda x: x["rank"])


def strict_sentence(item: dict) -> str:
    """itemから読むのはsource_sentenceだけ(gloss/used_form/display_phrase等は参照しない)。"""
    if not isinstance(item, dict):
        raise KpSourceSentenceJaInputError("KP itemがdictではありません")
    s = item.get("source_sentence")
    if not isinstance(s, str) or not s.strip():
        raise KpSourceSentenceJaInputError(f"rank={item.get('rank')}: source_sentence(本文引用英文)が空です")
    return s.strip()


def strict_sentences(items: list) -> list:
    if not items:
        raise KpSourceSentenceJaInputError("KP itemが0件です")
    return [strict_sentence(it) for it in sorted_items(items)]


def validate_sentences(sentences: list) -> None:
    if not isinstance(sentences, (list, tuple)) or not sentences:
        raise ValueError("sentencesが空です")
    if len(sentences) > MAX_SENTENCES:
        raise ValueError(f"sentencesが{MAX_SENTENCES}件を超えています: {len(sentences)}")
    for s in sentences:
        if not isinstance(s, str) or not s.strip():
            raise ValueError(f"空の英文: {s!r}")
        if _CJK_RE.search(s):
            raise ValueError(f"日本語(CJK)を含む英文は入力にできません: {s[:40]!r}")
        if _CTRL_RE.search(s):
            raise ValueError(f"改行・制御文字を含む英文: {s[:40]!r}")
        if len(s) > MAX_SENTENCE_CHARS:
            raise ValueError(f"長すぎる英文({len(s)}字): {s[:40]!r}")


def build_prompt(sentences: list) -> str:
    """引数は引用英文のみ(gloss・解説・本文・KP表現を受け取れない)。"""
    validate_sentences(sentences)
    return PROMPT_HEAD + "\n".join(f"{i}. {s}" for i, s in enumerate(sentences, 1)) + "\n" + PROMPT_BODY


def _variable_part(prompt: str) -> list:
    if not (prompt.startswith(PROMPT_HEAD) and prompt.endswith("\n" + PROMPT_BODY)):
        raise KpSourceSentenceJaIsolationViolation("Promptが固定HEAD/BODYの構造ではありません")
    enum = prompt[len(PROMPT_HEAD): -(len(PROMPT_BODY) + 1)]
    out = []
    for i, line in enumerate(enum.split("\n"), 1):
        m = _ENUM_LINE_RE.match(line)
        if not m or int(m.group(1)) != i:
            raise KpSourceSentenceJaIsolationViolation(f"列挙部に想定外の行があります: {line[:40]!r}")
        out.append(m.group(2))
    return out


def _collect_strings(obj, out=None) -> list:
    out = [] if out is None else out
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_strings(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _collect_strings(v, out)
    return out


def check_prompt_isolation(prompt: str, sentences: list, items: list | None = None) -> None:
    """送信直前のfail-closed検査。(1)Promptが HEAD+列挙+BODY の決定論再構成と一致 (2)可変部(英文)にCJKが無い
    (3)可変部が引用英文そのものだけ (4)item内の引用英文以外の文字列値(gloss・used_form・解説等、入れ子含む)が可変部に含まれない。"""
    if prompt != build_prompt(sentences):
        raise KpSourceSentenceJaIsolationViolation("Promptが決定論再構成(HEAD+列挙+BODY)と一致しません")
    var = _variable_part(prompt)
    if var != list(sentences):
        raise KpSourceSentenceJaIsolationViolation("Promptの可変部が引用英文と一致しません")
    if any(_CJK_RE.search(v) for v in var):
        raise KpSourceSentenceJaIsolationViolation("Promptの可変部に日本語が含まれています")
    if items:
        nvar = _norm_match("\n".join(var))
        nsent = [_norm_match(it.get("source_sentence") or "") for it in items]   # 正当な内容=各itemのsource_sentence(とその部分文字列)だけ
        for it in items:
            for s in _collect_strings(it):
                ns = _norm_match(s)
                if len(ns) < 4 or any(ns in x for x in nsent):
                    continue   # 引用英文そのもの(の部分文字列=例えばKP表現)は正常
                if ns in nvar:
                    raise KpSourceSentenceJaIsolationViolation(f"itemの文字列値が可変部に含まれています: {s[:40]!r}")


# ------------------------------------------------------------
# signature(再生成キー): 引用英文(rank昇順)・Prompt sha・model。gloss/解説/KP表現は含めない
# ------------------------------------------------------------
def translations_signature(items: list, *, model: str | None = None) -> str:
    payload = {"sentences": strict_sentences(items), "prompt_sha256": PROMPT_TEMPLATE_SHA256, "model": model or MODEL}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# 応答parse・構造検査
# ------------------------------------------------------------
def _strip_fence(text: str) -> str:
    t = (text or "").strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S)
    return m.group(1) if m else t


def check_ja(ja: str, sentence: str) -> None:
    """構造検査(新しい品質判定ではない): 空・短すぎ・改行/制御文字・英語のまま(CJK不在/英字優位)・禁止パターン。"""
    if not isinstance(ja, str) or not ja.strip():
        raise ValueError("空の訳")
    ja = ja.strip()
    if _CTRL_RE.search(ja):
        raise ValueError("訳に改行・制御文字が含まれます")
    if len(ja) < MIN_JA_CHARS or not _CJK_RE.search(ja) or not _KANA_RE.search(ja):
        raise ValueError(f"日本語の訳になっていません(長さ{len(ja)}): {ja[:30]!r}")
    letters = sum(c.isascii() and c.isalpha() for c in ja)
    cjk = len(_CJK_RE.findall(ja))
    if letters > cjk:
        raise ValueError(f"英字が日本語より多い(英語のまま残っている疑い): {ja[:40]!r}")
    if _norm_match(ja) == _norm_match(sentence):
        raise ValueError("訳が英文と同一です")
    if len(ja) > max(200, 3 * len(sentence)):
        raise ValueError(f"訳が長すぎます({len(ja)}字)")
    if PAGE_FORBIDDEN_RE.search(ja):
        raise ValueError(f"訳がページ禁止パターン({PAGE_FORBIDDEN_RE.pattern})に該当")


def parse_response(text: str, sentences: list) -> list:
    """戻り値=[{rank_index, source_sentence, source_sentence_ja}]。失敗は ValueError(技術retry対象)。"""
    if not text or not text.strip():
        raise ValueError("空の応答")
    try:
        d = json.loads(_strip_fence(text))
    except ValueError as e:
        raise ValueError(f"JSONとして読めません: {e}") from e
    tr = d.get("translations") if isinstance(d, dict) else None
    if not isinstance(tr, list):
        raise ValueError("translations配列がありません")
    if len(tr) != len(sentences):
        raise ValueError(f"件数が不一致(期待{len(sentences)}/実際{len(tr)})")
    ids = []
    for e in tr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), int) or isinstance(e.get("id"), bool):
            raise ValueError(f"idが整数ではありません: {str(e)[:100]}")
        ids.append(e["id"])
    if ids != list(range(1, len(sentences) + 1)):
        raise ValueError(f"idが1..{len(sentences)}の順に一致しません: {ids}")
    out = []
    for i, e in enumerate(tr):
        check_ja(e.get("ja"), sentences[i])
        out.append({"rank_index": i + 1, "source_sentence": sentences[i], "source_sentence_ja": e["ja"].strip()})
    return out


# ------------------------------------------------------------
# 生成
# ------------------------------------------------------------
def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    d = {"input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)}
    det = getattr(usage, "input_tokens_details", None)
    if det is not None:
        d["cached_input_tokens"] = getattr(det, "cached_tokens", None)
    odet = getattr(usage, "output_tokens_details", None)
    if odet is not None:
        d["reasoning_tokens"] = getattr(odet, "reasoning_tokens", None)
    return d


def _default_call_fn_factory(client, model: str):
    def call_fn(prompt: str):
        r = client.responses.create(model=model, input=[{"role": "user", "content": prompt}])
        return (getattr(r, "output_text", None) or ""), r.model, _usage_dict(getattr(r, "usage", None)), r.id
    return call_fn


def _cost_jpy(model: str, usage: dict):
    try:
        import er009_n1_routing_governance_10_actual_model_cost as pricing
        return pricing.cost_jpy_for_call("openai", model, usage.get("input_tokens"), usage.get("cached_input_tokens"), usage.get("output_tokens"))
    except Exception:
        return None


def generate_translations(sentences: list, *, call_fn=None, client=None, _items_for_isolation: list | None = None) -> dict:
    """sentences(引用英文のみ)→1 call→構造検査→失敗なら技術retry1回→なお失敗でKpSourceSentenceJaError。
    応答modelが期待modelと違えばretryもfallbackもせずSTOP。"""
    validate_sentences(sentences)
    model = routing.require_model(MODEL_ROUTING_PROCESS, MODEL)
    prompt = build_prompt(sentences)
    check_prompt_isolation(prompt, sentences, _items_for_isolation)
    if call_fn is None:
        if client is None:
            import er003_v1_b1_scaffold_01_generate as b1s
            client = b1s.get_client()
        call_fn = _default_call_fn_factory(client, model)
    calls = []
    last_err = None
    for attempt_no in (1, 2):   # 初回+技術retry1回(上限厳守)
        t0 = time.time()
        text, response_model, usage, response_id = call_fn(prompt)
        rec = {"attempt": attempt_no, "response_model": response_model, "usage": usage, "response_id": response_id,
               "elapsed_sec": round(time.time() - t0, 2), "cost_jpy": _cost_jpy(response_model, usage or {})}
        calls.append(rec)
        if response_model != model:
            rec["model_contract_violation"] = True
            raise KpSourceSentenceJaError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response_model})。fallbackせずSTOPします(ER-006-MODEL-ROUTING-CONTRACT-01)。")
        try:
            rows = parse_response(text, list(sentences))
        except ValueError as e:
            last_err = str(e)
            rec["structure_error"] = last_err
            continue
        costs = [c["cost_jpy"] for c in calls if c.get("cost_jpy") is not None]
        audit = {"management_id": MANAGEMENT_ID, "process": MODEL_ROUTING_PROCESS, "model": model, "requested_model": model,
                 "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "prompt_template_sha256": PROMPT_TEMPLATE_SHA256,
                 "input_sha256": hashlib.sha256(json.dumps(list(sentences), ensure_ascii=False).encode("utf-8")).hexdigest(),
                 "response_ids": [c["response_id"] for c in calls], "calls": calls,
                 "retried_for_parse": attempt_no == 2, "reused_from_previous_run": False,
                 "total_cost_jpy": round(sum(costs), 4) if costs else None,
                 "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        return {"items": rows, "audit": audit}
    raise KpSourceSentenceJaError(f"Part 1 訳生成が2回(初回+技術retry1回)とも構造検査に失敗しました: {last_err}")


def check_sentences_in_article(items: list, article_text: str) -> None:
    """課金前の逐語照合(既存基準と同じ正規化)。本文に無い引用英文は訳さない(fail-closed)。"""
    na = _norm_match(article_text)
    for it in sorted_items(items):
        s = strict_sentence(it)
        if _norm_match(s) not in na:
            raise KpSourceSentenceJaInputError(f"KP_PART1_QUOTE_NOT_IN_ARTICLE: rank={it.get('rank')} {s[:50]!r}(本文に逐語実在しない。訳さない)")


def generate_for_kp_items(items: list, *, call_fn=None, client=None, article_text: str | None = None) -> dict:
    """呼出側用wrapper。item dictに触れるのは strict_sentence()(source_sentence)と rank だけ。"""
    sitems = sorted_items(items)
    sentences = strict_sentences(sitems)
    if article_text is not None:
        check_sentences_in_article(sitems, article_text)
    res = generate_translations(sentences, call_fn=call_fn, client=client, _items_for_isolation=sitems)
    return {"schema": SCHEMA_VERSION, "translations_signature": translations_signature(sitems), "sentences": sentences,
            "ranks": [it["rank"] for it in sitems], "items": res["items"], "audit": res["audit"]}


def resolve_translations(items: list, cached: dict | None, *, call_fn=None, client=None, article_text: str | None = None) -> dict:
    """X用のresume resolver: signature一致ならAPI 0で再利用、不一致/無しなら再生成。"""
    sig = translations_signature(items)
    if cached and cached.get("schema") == SCHEMA_VERSION and cached.get("translations_signature") == sig:
        out = json.loads(json.dumps(cached))
        out["reused_from_previous_run"] = True
        out.setdefault("audit", {})["reused_from_previous_run"] = True
        return out
    out = generate_for_kp_items(items, call_fn=call_fn, client=client, article_text=article_text)
    out["reused_from_previous_run"] = False
    return out


def require_fresh_translations(items: list, doc: dict | None, *, next_command: str, where: str = "") -> None:
    """使う側(TTS/assembly/pages/player)の確認。無い/古いならKpSourceSentenceJaStale(次コマンド付き)。"""
    w = f"({where})" if where else ""
    if not doc or doc.get("schema") != SCHEMA_VERSION:
        raise KpSourceSentenceJaStale(
            f"KP_PART1_TRANSLATIONS_MISSING{w}: {TRANSLATIONS_FILENAME}が無い/形式不明(T1導入前のrunか未生成)。次の一手: {next_command}")
    try:
        cur = translations_signature(items)
    except KpSourceSentenceJaInputError as e:
        raise KpSourceSentenceJaStale(f"KP_PART1_TRANSLATIONS_INPUT_INVALID{w}: {e}") from e
    if doc.get("translations_signature") != cur:
        raise KpSourceSentenceJaStale(
            f"KP_PART1_TRANSLATIONS_STALE{w}: 保存済みsignature={str(doc.get('translations_signature'))[:12]} 現在={cur[:12]}"
            f"(引用英文・順序・Prompt・modelのいずれかが変わった)。次の一手: {next_command}")
    if len(doc.get("items") or []) != len(items):
        raise KpSourceSentenceJaStale(f"KP_PART1_TRANSLATIONS_COUNT_MISMATCH{w}: 次の一手: {next_command}")


def translations_by_rank(doc: dict) -> dict:
    """assemble_part1(translations=)用の {rank: 日本語訳}。"""
    return {rk: it["source_sentence_ja"] for rk, it in zip(doc["ranks"], doc["items"])}
