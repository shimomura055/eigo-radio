# ============================================================
# er003_kp_general_explanation_01.py
# FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14(2026-10-25)
# 学習テキスト Part 1「Vocabulary & Expressions」案α Production配線(Family X/Z共通)
# ============================================================
# 承認: ユーザー2026-10-25 APPROVED_FOR_PRODUCTION(原文 docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md)。
# 設計: docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/PART1_WIRING_DESIGN_01.md(§13〜§17がOpus条件A反映後の正)。
#
# 入力は確定KPの英語表現(used_form)だけ。本文・gloss・引用文・作品名は一切LLMへ渡さない。
# 1 call(gpt-6-luna=routing.SUPPORT_MODEL)で全KP(1〜3件)の日本語一般解説を生成する。
# 失敗=技術retry1回→fail-closed(旧方式なし・空欄続行なし)。fallbackしない。
#
# 訳欄(source_sentence_ja)は専用翻訳工程T1(er003_kp_source_sentence_ja_01.py、2026-10-25ユーザー正式承認、UDR #197判断済み)で生成する。
# 描画の有効化は判断記録docs/pm/decisions/part1_translation_decision.json(translation_decision_record()が唯一の入口)。記録が無い間は描画しない。
#
# このmoduleは docs/research のTrial資産をimportしない(Prompt定数は逐語コピー、byte一致をtestで固定)。
# ============================================================
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import time
import unicodedata

import er006_model_routing_contract_01 as routing

MANAGEMENT_ID = "FAMILY-Z-STUDY-TEXT-TRIAL-01"
MODEL_ROUTING_PROCESS = "KEY_PHRASE_GENERAL_EXPLANATION"
MODEL = routing.SUPPORT_MODEL
SCHEMA_VERSION = "kp_general_explanation_v1"
EXPLANATIONS_FILENAME = "kp_general_explanations.json"
PART1_FILE_STEM = "part1_vocabulary_expressions"
TRANSLATION_PENDING = "PENDING_USER_DECISION"

# ---- Prompt(Trial-04 案α。run_trial_04.py P1_HEAD/P1_BODYの逐語コピー。byte一致はtestで固定) ----
PROMPT_HEAD = """あなたは英語表現の解説を書く英語教育の専門家です。日本語話者の英語学習者(B1〜B2相当)向けに、下の英語表現それぞれの「一般的な解説」を日本語で書いてください。

# 前提
- 解説の対象は、英語表現そのものです。特定の文章・場面・物語には依存せず、その表現が英語で一般にどう使われるか、学習者が実際に使えるようになる知識を説明します。
- この依頼では、表現が使われていた記事・文脈は共有されていません。文脈を想像・推測して解説に織り込まないでください。
"""
PROMPT_ENUM_MARKER = "\n# 解説する英語表現\n"
PROMPT_BODY = """
# 解説の書き方
各表現について、学習者が自分の英語に取り入れられるように、次の観点から学習価値の高い内容を、必要十分な量の自然な日本語の文章で説明してください。すべての観点を機械的に列挙する必要はありません。
- 表現の核となる意味
- 主要な用法と、使われる場面
- よく使われるコロケーション(語の組み合わせ)
- 重要な類義語・近似表現との違い
- 自然に存在する比喩的・拡張的な用法
- 複合表現(語が組み合わさってできた語句)では、学習価値の中心となる語句(その語の一般的な使い方を知ると応用がきく部分)を中心に説明してよい。
- 使用頻度の順位(「最も一般的」「よく使われる順に」など)を、根拠なく断定しない。類義語との違いも、過度に断定せず、自然な英語として正確に説明する。
- 自然に存在する用法だけを書き、不自然な用法・用例を創作しない。すべての観点を無理に当てはめない。
- 文法の解説(構造・活用・語順など)には脱線しない。
- 説明の水増しをしない。「ほかの場面で使うと」という独立した追加例文は書かない(語句の組み合わせを示すコロケーションの表記は可)。

# 出力形式
Markdownのみ。表現ごとに次の形式で、前置き・後書きは付けない。
### 1. (英語表現)
(解説文。自然な日本語の文章。箇条書きは必要な場合のみ)
### 2. ...
"""
PROMPT_TEMPLATE_SHA256 = hashlib.sha256((PROMPT_HEAD + "␟" + PROMPT_BODY).encode("utf-8")).hexdigest()

MAX_PHRASES = 5            # Productionは最大3件。旧5件artifactも許容(上限)
MAX_PHRASE_CHARS = 60
MAX_PHRASE_WORDS = 10
MIN_BODY_CHARS = 30        # Trial-04実出力6件で較正(最短の本文でも約60字)

_CJK_RE = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿豈-﫿＀-￯]")
_CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")
# 既存ページ規則の前倒し適用(新しい品質判定ではない): er063 _FORBIDDEN_LABEL_RE + lint kp_label_leak と同一パターン
PAGE_FORBIDDEN_RE = re.compile(r"\(A2\)|\(B1\)|B1B|English:|英語:|EN:|日本語:|JA:")
_HEADING_RE = re.compile(r"^###[ \t]*(\d+)[.．)][ \t]*(.*?)[ \t]*$", re.M)


class KpGeneralExplanationError(RuntimeError):
    """Part 1生成の失敗(技術retry後・契約違反を含む)。fail-closedでSTOPする。"""


class KpGeneralExplanationInputError(ValueError):
    """入力不正(課金前に拒否)。"""


class KpIsolationViolation(KpGeneralExplanationError):
    """入力隔離違反(Promptの可変部にKP表現以外が混入)。API呼出前にSTOP。"""


class KpGeneralExplanationStale(KpGeneralExplanationError):
    """使う側の確認: Part 1が無い/古い(KP表現・順序・Prompt・modelが変わった)。"""


# ------------------------------------------------------------
# 入力(厳格版。explanation_phrase()のdisplay_phrase fallbackは使わない=Opus M4)
# ------------------------------------------------------------
def strict_phrase(item: dict) -> str:
    if not isinstance(item, dict):
        raise KpGeneralExplanationInputError("KP itemがdictではありません")
    if not item.get("fulltext_source_ref"):
        raise KpGeneralExplanationInputError(
            f"rank={item.get('rank')}: fulltext_source_refがありません(旧strategy_l等のKPはPart 1の入力にしない。display_phraseへfallbackしない)")
    uf = item.get("used_form")
    if not isinstance(uf, str) or not uf.strip():
        raise KpGeneralExplanationInputError(f"rank={item.get('rank')}: used_formが空です(display_phraseへfallbackしない)")
    return uf.strip()


def sorted_items(items: list) -> list:
    return sorted(items, key=lambda x: x["rank"])


def strict_phrases(items: list) -> list:
    if not items:
        raise KpGeneralExplanationInputError("KP itemが0件です")
    return [strict_phrase(it) for it in sorted_items(items)]


def validate_phrases(phrases: list) -> None:
    """課金前の入力検証。拒否=空・CJK・改行/制御文字・長さ/語数超過・列挙の区切り(#)始まり。許可文字は実データ(全KPのused_form)で較正。"""
    if not isinstance(phrases, (list, tuple)) or not phrases:
        raise ValueError("phrasesが空です")
    if len(phrases) > MAX_PHRASES:
        raise ValueError(f"phrasesが{MAX_PHRASES}件を超えています: {len(phrases)}")
    for p in phrases:
        if not isinstance(p, str) or not p.strip():
            raise ValueError(f"空の表現: {p!r}")
        if _CJK_RE.search(p):
            raise ValueError(f"日本語(CJK)を含む表現は入力にできません: {p!r}")
        if _CTRL_RE.search(p):
            raise ValueError(f"改行・制御文字を含む表現: {p!r}")
        if len(p) > MAX_PHRASE_CHARS or len(p.split()) > MAX_PHRASE_WORDS:
            raise ValueError(f"長すぎる表現({len(p)}字/{len(p.split())}語): {p[:40]!r}")
        if p.lstrip().startswith("#"):
            raise ValueError(f"'#'始まりの表現は入力にできません: {p!r}")


def build_prompt(phrases: list) -> str:
    """引数は英語表現のみ(本文・gloss・引用文を受け取れない)。Trial-04 p1_prompt(arm='alpha')とbyte一致。"""
    validate_phrases(phrases)
    items = "\n".join(f"{i}. 英語表現: {k}" for i, k in enumerate(phrases, 1))
    return PROMPT_HEAD + PROMPT_ENUM_MARKER + items + "\n" + PROMPT_BODY


_ENUM_LINE_RE = re.compile(r"^(\d+)\. 英語表現: (.*)$")


def _variable_part(prompt: str) -> str:
    """Promptの可変部=列挙行の「表現」部分だけ(固定HEAD/BODY・列挙ラベル「N. 英語表現: 」を除く)。"""
    if not (prompt.startswith(PROMPT_HEAD + PROMPT_ENUM_MARKER) and prompt.endswith("\n" + PROMPT_BODY)):
        raise KpIsolationViolation("Promptが固定HEAD/BODYの構造ではありません")
    enum = prompt[len(PROMPT_HEAD) + len(PROMPT_ENUM_MARKER): -(len(PROMPT_BODY) + 1)]
    tails = []
    for i, line in enumerate(enum.split("\n"), 1):
        m = _ENUM_LINE_RE.match(line)
        if not m or int(m.group(1)) != i:
            raise KpIsolationViolation(f"列挙部に想定外の行があります: {line[:40]!r}")
        tails.append(m.group(2))
    return "\n".join(tails)


def _norm_match(s: str) -> str:
    n = unicodedata.normalize("NFKC", s or "").translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    return re.sub(r"\s+", " ", n).strip().lower()


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


def check_prompt_isolation(prompt: str, phrases: list, items: list | None = None) -> None:
    """送信直前のfail-closed検査(Opus実装時必須2)。
    (1) Promptが HEAD+列挙+BODY の決定論再構成と一致、(2) 可変部(列挙部)にCJKが無い、
    (3) itemのあらゆる文字列値(入れ子含む)が可変部に含まれない。表現そのもの(各phraseの部分文字列)は正常として除外。"""
    if prompt != build_prompt(phrases):
        raise KpIsolationViolation("Promptが決定論再構成(HEAD+列挙+BODY)と一致しません")
    var = _variable_part(prompt)
    if _CJK_RE.search(var):
        raise KpIsolationViolation("Promptの可変部(列挙部)に日本語が含まれています")
    if items:
        nvar = _norm_match(var)
        nphr = [_norm_match(p) for p in phrases]
        for it in items:
            for s in _collect_strings(it):
                ns = _norm_match(s)
                if len(ns) < 4 or any(ns in p for p in nphr):
                    continue
                if ns in nvar:
                    raise KpIsolationViolation(f"itemの文字列値が可変部に含まれています: {s[:40]!r}")


# ------------------------------------------------------------
# signature(再生成キー): 表現・順序(rank昇順)・Prompt sha・model。gloss/引用文/本文は含めない
# ------------------------------------------------------------
def phrases_signature(items: list, *, model: str | None = None) -> str:
    payload = {"phrases": strict_phrases(items), "prompt_sha256": PROMPT_TEMPLATE_SHA256, "model": model or MODEL}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# 応答parse・構造検査
# ------------------------------------------------------------
def normalize_heading(s: str) -> str:
    n = unicodedata.normalize("NFKC", s or "")
    n = n.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    n = re.sub(r"[*_`()\[\]\"“”]", " ", n)
    return re.sub(r"\s+", " ", n).strip().lower()


def parse_response(text: str, phrases: list) -> list:
    """構造検査。戻り値=[{rank_index, phrase, explanation_ja}]。失敗は ValueError(技術retry対象)。"""
    if not text or not text.strip():
        raise ValueError("空の応答")
    ms = list(_HEADING_RE.finditer(text))
    if len(ms) != len(phrases):
        raise ValueError(f"見出し数が不一致(期待{len(phrases)}/実際{len(ms)})")
    out = []
    for i, m in enumerate(ms):
        if int(m.group(1)) != i + 1:
            raise ValueError(f"見出し番号が連続していません: {m.group(1)}")
        if normalize_heading(m.group(2)) != normalize_heading(phrases[i]):
            raise ValueError(f"見出しの表現が入力と一致しません: {m.group(2)!r} != {phrases[i]!r}")
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.end():end].strip()
        if not _CJK_RE.search(body) or len(body) < MIN_BODY_CHARS:
            raise ValueError(f"{i + 1}番の解説が日本語の本文になっていません(長さ{len(body)})")
        if PAGE_FORBIDDEN_RE.search(body):
            raise ValueError(f"{i + 1}番の解説がページ禁止パターン({PAGE_FORBIDDEN_RE.pattern})に該当")
        out.append({"rank_index": i + 1, "phrase": phrases[i], "explanation_ja": body})
    if text[:ms[0].start()].strip():
        raise ValueError("最初の見出しの前に前置きがあります")
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
    except Exception:   # 単価表に無い等。費用は監査に残らないだけで生成は止めない(cost loggerが別途記録)
        return None


def generate_general_explanations(phrases: list, *, call_fn=None, client=None, _items_for_isolation: list | None = None) -> dict:
    """phrases(英語表現のみ)→1 call→構造検査→失敗なら技術retry1回→なお失敗でKpGeneralExplanationError。
    応答modelが期待modelと違えばretryもfallbackもせずSTOP。"""
    validate_phrases(phrases)
    model = routing.require_model(MODEL_ROUTING_PROCESS, MODEL)
    prompt = build_prompt(phrases)
    check_prompt_isolation(prompt, phrases, _items_for_isolation)
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
            raise KpGeneralExplanationError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response_model})。fallbackせずSTOPします(ER-006-MODEL-ROUTING-CONTRACT-01)。")
        try:
            rows = parse_response(text, list(phrases))
        except ValueError as e:
            last_err = str(e)
            rec["structure_error"] = last_err
            continue
        costs = [c["cost_jpy"] for c in calls if c.get("cost_jpy") is not None]
        audit = {"management_id": MANAGEMENT_ID, "process": MODEL_ROUTING_PROCESS, "model": model, "requested_model": model,
                 "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "prompt_template_sha256": PROMPT_TEMPLATE_SHA256,
                 "input_sha256": hashlib.sha256(json.dumps(list(phrases), ensure_ascii=False).encode("utf-8")).hexdigest(),
                 "phrases": list(phrases), "response_ids": [c["response_id"] for c in calls], "calls": calls,
                 "retried_for_parse": attempt_no == 2, "reused_from_previous_run": False,
                 "total_cost_jpy": round(sum(costs), 4) if costs else None,
                 "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        return {"items": rows, "audit": audit}
    raise KpGeneralExplanationError(f"Part 1解説生成が2回(初回+技術retry1回)とも構造検査に失敗しました: {last_err}")


def generate_for_kp_items(items: list, *, call_fn=None, client=None) -> dict:
    """呼出側用wrapper。item dictに触れるのは strict_phrase() だけ(gloss/source_sentence/meaning等は参照しない)。
    戻り値は保存形式(phrases_signature・ranks付き)。"""
    sitems = sorted_items(items)
    phrases = strict_phrases(sitems)
    res = generate_general_explanations(phrases, call_fn=call_fn, client=client, _items_for_isolation=sitems)
    return {"schema": SCHEMA_VERSION, "phrases_signature": phrases_signature(sitems), "phrases": phrases,
            "ranks": [it["rank"] for it in sitems], "items": res["items"], "audit": res["audit"]}


def resolve_general_explanations(items: list, cached: dict | None, *, call_fn=None, client=None) -> dict:
    """X用のresume resolver: signature一致ならAPI 0で再利用、不一致/無しなら再生成。"""
    sig = phrases_signature(items)
    if cached and cached.get("schema") == SCHEMA_VERSION and cached.get("phrases_signature") == sig:
        out = json.loads(json.dumps(cached))
        out["reused_from_previous_run"] = True
        out.setdefault("audit", {})["reused_from_previous_run"] = True
        return out
    out = generate_for_kp_items(items, call_fn=call_fn, client=client)
    out["reused_from_previous_run"] = False
    return out


def require_fresh_general_explanations(items: list, doc: dict | None, *, next_command: str, where: str = "") -> None:
    """使う側(TTS/assembly/pages/player)の確認(Opus M2)。無い/古いならKpGeneralExplanationStale(次コマンド付き)。"""
    if not doc or doc.get("schema") != SCHEMA_VERSION:
        raise KpGeneralExplanationStale(
            f"KP_PART1_EXPLANATIONS_MISSING{('(' + where + ')') if where else ''}: {EXPLANATIONS_FILENAME}が無い/形式不明 "
            f"(Part 1導入前のrunか未生成)。次の一手: {next_command}")
    try:
        cur = phrases_signature(items)
    except KpGeneralExplanationInputError as e:
        raise KpGeneralExplanationStale(f"KP_PART1_INPUT_INVALID{('(' + where + ')') if where else ''}: {e}") from e
    if doc.get("phrases_signature") != cur:
        raise KpGeneralExplanationStale(
            f"KP_PART1_EXPLANATIONS_STALE{('(' + where + ')') if where else ''}: 保存済みsignature={str(doc.get('phrases_signature'))[:12]} "
            f"現在KP={cur[:12]}(KP表現・順序・Prompt・modelのいずれかが変わった)。次の一手: {next_command}")
    if len(doc.get("items") or []) != len(items):
        raise KpGeneralExplanationStale(f"KP_PART1_EXPLANATIONS_COUNT_MISMATCH: 次の一手: {next_command}")


# ------------------------------------------------------------
# 組立(決定論・LLMなし)
# ------------------------------------------------------------
def assemble_part1(kp_items: list, explanations: dict, translations: dict | None, article_text: str) -> list:
    """ユーザー原文§2の並び: 英語表現 / 本文中の意味 / 本文引用英文 / 英文の日本語訳 / 解説。
    - gloss: HR待ち・未評価・空はSTOP。引用英文: 既存正規化で本文に逐語実在しなければSTOP。
    - 訳: translations[rank]が無ければ source_sentence_ja=None・translation_status=PENDING_USER_DECISION(暗黙の空欄にしない)。
    - explanationsは最新性(signature)を確認する。"""
    import er003_key_words_gloss_alignment as ga
    sitems = sorted_items(kp_items)
    hr = ga.collect_unresolved({"items": sitems})
    if hr:
        raise KpGeneralExplanationError(f"KP_PART1_GLOSS_HUMAN_REVIEW_REQUIRED: rank={[x.get('rank') for x in hr]}(HR解決後に再実行)")
    unev = ga.collect_unevaluated({"items": sitems})
    if unev:
        raise KpGeneralExplanationError(f"KP_PART1_GLOSS_UNEVALUATED: rank={[x.get('rank') for x in unev]}")
    require_fresh_general_explanations(sitems, explanations, next_command="Part 1を再生成してください", where="assemble")
    by_idx = {r["rank_index"]: r for r in explanations["items"]}
    norm_article = _norm_match(article_text)
    translations = translations or {}
    rows = []
    for i, it in enumerate(sitems, 1):
        phrase = strict_phrase(it)
        gloss = (it.get("japanese_gloss") or "").strip()
        if not gloss:
            raise KpGeneralExplanationError(f"KP_PART1_GLOSS_EMPTY: rank={it.get('rank')}")
        sent = (it.get("source_sentence") or "").strip()
        if not sent or _norm_match(sent) not in norm_article:
            raise KpGeneralExplanationError(f"KP_PART1_QUOTE_NOT_IN_ARTICLE: rank={it.get('rank')} {sent[:50]!r}(本文に逐語実在しない)")
        ex = by_idx.get(i)
        if not ex or normalize_heading(ex["phrase"]) != normalize_heading(phrase):
            raise KpGeneralExplanationError(f"KP_PART1_EXPLANATION_PHRASE_MISMATCH: rank={it.get('rank')}")
        ja = translations.get(it["rank"]) or translations.get(str(it["rank"]))
        rows.append({"english_expression": phrase, "meaning_in_text_ja": gloss, "source_sentence": sent,
                     "source_sentence_ja": ja if ja else None, "explanation_ja": ex["explanation_ja"],
                     "translation_status": "PROVIDED" if ja else TRANSLATION_PENDING, "rank": it["rank"]})
    return rows


# ------------------------------------------------------------
# 出力(保存)
# ------------------------------------------------------------
def render_markdown(rows: list) -> str:
    L = ["# Vocabulary & Expressions", "", f"(translation_status: {', '.join(sorted({r['translation_status'] for r in rows}))})", ""]
    for i, r in enumerate(rows, 1):
        L += [f"## {i}. {r['english_expression']}", "", f"- 本文中の意味: {r['meaning_in_text_ja']}", f"- 本文の英文: {r['source_sentence']}",
              f"- 日本語訳: {r['source_sentence_ja'] if r['source_sentence_ja'] else 'null(PENDING_USER_DECISION)'}", "", "### 解説", "", r["explanation_ja"], ""]
    return "\n".join(L)


def write_study_text(dir_path: str, rows: list) -> dict:
    os.makedirs(dir_path, exist_ok=True)
    jp, mp = f"{dir_path}/{PART1_FILE_STEM}.json", f"{dir_path}/{PART1_FILE_STEM}.md"
    with open(jp, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"schema": SCHEMA_VERSION, "level": "Advanced", "rows": rows}, f, ensure_ascii=False, indent=2)
    with open(mp, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_markdown(rows))
    return {"json": jp, "md": mp}


# ------------------------------------------------------------
# ページ描画(M3(ii): 訳欄の判断記録が出るまで描画しない)
# ------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
TRANSLATION_DECISION_RECORD = os.path.join(_REPO_ROOT, "docs", "pm", "decisions", "part1_translation_decision.json")
_VALID_DECISIONS = ("T1", "T2")


def translation_decision_record() -> dict | None:
    """訳欄(T1/T2)のユーザー判断記録。唯一の入口。環境変数・flag・引数では上書きできない。
    記録が無い/不正なら None(=描画しない)。"""
    p = TRANSLATION_DECISION_RECORD
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or d.get("decision") not in _VALID_DECISIONS or not d.get("source"):
        return None
    return d


def study_text_render_enabled() -> bool:
    return translation_decision_record() is not None


def _inline_md(s: str) -> str:
    e = html.escape(s or "", quote=False)
    e = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e)
    e = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", e)
    return e


_BULLET_RE = re.compile(r"^\s*[-・]\s+")


def _paragraphs_html(text: str) -> str:
    out = []
    for blk in re.split(r"\n\s*\n", (text or "").strip()):
        lines = [x.rstrip() for x in blk.split("\n") if x.strip()]
        if lines and all(_BULLET_RE.match(x) for x in lines):
            out.append("<ul>" + "".join("<li>" + _inline_md(_BULLET_RE.sub("", x)) + "</li>" for x in lines) + "</ul>")
        elif lines:
            out.append("<p>" + _inline_md(" ".join(x.strip() for x in lines)) + "</p>")
    return "".join(out)


STUDY_CSS = ("<style>.study{margin:24px 0;padding:12px 16px;border:1px solid #ddd;border-radius:8px}"
             ".study h3{margin:0 0 8px}.study h4{margin:16px 0 4px}.study dt{font-weight:bold;margin-top:8px}"
             ".study dd{margin:2px 0 0 0}.study p{margin:4px 0}</style>")


def render_html_block(rows: list) -> str:
    """ページ用のstudy block(<section class='study'>、<h3>+<div>/<dl>のみ。<table>/<h2>不使用=標準適合checkを壊さない)。
    判断記録が無い間は空文字(描画しない)。T1は全行に日本語訳が必要(欠落時は描画せずSTOP=fail-closed)。"""
    rec = translation_decision_record()
    if rec is None:
        return ""
    if rec["decision"] == "T1":
        missing = [r["rank"] for r in rows if not r.get("source_sentence_ja")]
        if missing:
            raise KpGeneralExplanationError(f"KP_PART1_TRANSLATION_REQUIRED_BY_T1: rank={missing}(T1決定済みだが訳が未生成。表示しない)")
    parts = ["<section class='study'><h3>Vocabulary &amp; Expressions</h3>"]
    for r in rows:
        dl = [f"<dt>本文中の意味</dt><dd>{html.escape(r['meaning_in_text_ja'], quote=False)}</dd>",
              f"<dt>本文の英文</dt><dd>{html.escape(r['source_sentence'], quote=False)}</dd>"]
        if rec["decision"] == "T1":
            dl.append(f"<dt>日本語訳</dt><dd>{html.escape(r['source_sentence_ja'], quote=False)}</dd>")
        dl.append(f"<dt>解説</dt><dd>{_paragraphs_html(r['explanation_ja'])}</dd>")
        parts.append(f"<div class='study-item'><h4>{html.escape(r['english_expression'], quote=False)}</h4><dl>{''.join(dl)}</dl></div>")
    parts.append("</section>")
    return STUDY_CSS + "".join(parts)


# ------------------------------------------------------------
# Family X 公開ページ(per-article script)用の共通builder(委任_16、API 0)
# ------------------------------------------------------------
def study_html_for_audio_dir(audio_dir: str) -> str:
    """Xの試聴/公開ページ生成script(例 er019_nws2_final_page_01.py)が1行で呼ぶ共通関数。
    入力=Production runnerのaudio出力dir(`<audio_dir>/b1b/{key_phrases,study_text}`)。保存済みstudy_text(組立時に本文との逐語照合済み)が、
    現在のKP・解説・訳(いずれもsignature最新)・gloss現在値と一致することを確認してから描画する。
    判断記録なし→空文字(従来とバイト同一)。Part 1未生成/古い/不一致→KpGeneralExplanationError(ページを作らない)。"""
    import er003_kp_source_sentence_ja_01 as ja
    b = f"{audio_dir}/b1b"
    kp_path = f"{b}/key_phrases/keywords_canonicalized.json"
    try:
        with open(kp_path, encoding="utf-8") as f:
            items = sorted_items(json.load(f).get("items") or [])
        with open(f"{b}/key_phrases/{EXPLANATIONS_FILENAME}", encoding="utf-8") as f:
            ex = json.load(f)
        with open(f"{b}/key_phrases/{ja.TRANSLATIONS_FILENAME}", encoding="utf-8") as f:
            tr = json.load(f)
        with open(f"{b}/study_text/{PART1_FILE_STEM}.json", encoding="utf-8") as f:
            saved = json.load(f)
    except (OSError, ValueError) as e:
        raise KpGeneralExplanationError(f"KP_PART1_PAGE_INPUT_MISSING: {e}(次の一手: --stage study_text の後に --stage assemble/player)") from e
    try:
        require_fresh_general_explanations(items, ex, next_command="--stage study_text", where="x_page")
        ja.require_fresh_translations(items, tr, next_command="--stage study_text", where="x_page")
    except (KpGeneralExplanationStale, ja.KpSourceSentenceJaStale) as e:
        raise KpGeneralExplanationError(str(e)) from e
    rows = saved.get("rows") or []
    if len(rows) != len(items):
        raise KpGeneralExplanationError("KP_PART1_PAGE_STUDY_TEXT_COUNT_MISMATCH: 保存済みstudy_textとKPの件数が不一致(--stage assembleで再保存)")
    by_idx = {r["rank_index"]: r for r in ex["items"]}
    trs = ja.translations_by_rank(tr)
    for i, (it, r) in enumerate(zip(items, rows), 1):
        exp = (by_idx.get(i) or {}).get("explanation_ja")
        want = (strict_phrase(it), (it.get("japanese_gloss") or "").strip(), (it.get("source_sentence") or "").strip(), trs.get(it["rank"]), exp)
        got = (r.get("english_expression"), r.get("meaning_in_text_ja"), r.get("source_sentence"), r.get("source_sentence_ja"), r.get("explanation_ja"))
        if want != got:
            raise KpGeneralExplanationError(f"KP_PART1_PAGE_STUDY_TEXT_STALE: rank={it['rank']} 保存済みstudy_textが現在のKP/解説/訳と不一致(--stage assembleで再保存)")
    return render_html_block(rows)
