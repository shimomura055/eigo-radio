# -*- coding: utf-8 -*-
"""FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 委任_01: Family X Standard(A2)のComment 3 Z方式(APPROVED_FOR_PRODUCTION、ユーザー正式決定2026-10-28)。

本moduleは新関数・定数のみ。**委任_01時点ではProduction経路(er019_family_x_audio_production_runner_01)から呼ばれていない(未配線)**。
配線は委任_02(Opus条件Aレビュー後)で`run_family_x_a2_scaffold`のComment 3行だけを本moduleの`run_comment3_z_method`へ差し替える。
対象外(変更禁止): Comment 1・2・4、Preview、X Advanced(b1b)、Y、Z。LLM呼出は呼び出し側が渡すcallable経由のみ(本module自体はAPIを持たない)。

設計: docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/WIRING_DESIGN_01.md
Trial基準: docs/research/FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01/(METHOD_DIFF_01.md / generate_after_01.py)
"""
from __future__ import annotations

import hashlib
import re
import unicodedata

import er003_v1_iran01_a2_generate as a2gen

COMMENT3_Z_METHOD_VERSION = "FX-STD-COMMENT3-Z-V1"

# (a) Comment 3役割文 = Family Zが使う既存定数をそのまま流用(新Prompt文は作らない。Trial generate_after_01.py:ROLE[3]と同一)。
COMMENT3_Z_ROLE = a2gen.COMMENT_2_ROLE
COMMENT3_Z_ROLE_SHA256 = hashlib.sha256(a2gen.COMMENT_2_ROLE.encode("utf-8")).hexdigest()

# ---- (b) 参照範囲制御(決定論・LLM不使用) ----
MAX_EXCERPT_PARAGRAPHS = 2     # Part 3先頭から高々2段落まで
MAX_EXCERPT_SENTENCES = 3      # 渡す文は高々3文
MAX_EXCERPT_WORDS = 70         # 渡す語数の上限
MIN_EXCERPT_WORDS = 8          # これ未満(情報が薄い)は渡さずPart1+Part2のみ

# 結論・留保・まとめの目印(文単位。Trialの段落単位markerを文単位へ拡張し、however/in other words等を追加)
CONCLUSION_MARKER_RE = re.compile(
    r"\b(even so|still,|in short|overall|in conclusion|in other words|in the end|after all|too soon|"
    r"do(?:es)? not show|proof|however|as a result|this means|that means|for now|in fact)\b", re.I)
# 結果文の目印(数値・比較・結果動詞・因果/結論動詞・否定的結果)。該当文の手前で打ち切る。
RESULT_SENTENCE_RE = re.compile(
    r"\b(found|finds?|showed|shows?|shown|turned out|revealed?|rose|rises?|fell|falls?|dropped|drops?|"
    r"increased?|decreased?|declined?|grew|grows?|went (?:up|down)|go(?:es)? (?:up|down)|did better|did worse|"
    r"better than|worse than|more than|less than|fewer|lower(?:ed)?|higher|raised|reached|times|percent|"
    r"averages?|scores?|scored|results?|resulted|led to|caused?|because|due to|suggests?|suggested|"
    r"thinks?|believes?|concluded|explains?|reasons?|improved?|worsened|solved|proved?|"
    r"stayed the same|no longer|(?:had|has|have|did|does|do|was|were|is|are) not|never|"
    r"twice|double|triple|half|dozen|hundreds?|thousands?|millions?|billions?|"
    r"two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b|\d|%", re.I)
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?”\"’])\s+(?=[\"“‘]?[A-Z0-9])")
_ABBREV_RE = re.compile(r"\b(Mr|Mrs|Ms|Dr|St|U\.S|U\.K|vs|etc|No)\.$")


def split_sentences(paragraph: str) -> list[str]:
    raw = [s.strip() for s in _SENT_SPLIT_RE.split(paragraph.strip()) if s.strip()]
    out: list[str] = []
    for s in raw:   # 略語(Mr. 等)で誤分割した場合は次の文へ結合
        if out and _ABBREV_RE.search(out[-1]):
            out[-1] = out[-1] + " " + s
        else:
            out.append(s)
    return out


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9’']+", text))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_part3_excerpt(part3: str) -> dict:
    """Part 3から、Comment 3へ渡してよい先頭部分を決定論で切り出す。
    先頭の文から順に、(1)結論・留保の目印を含む文 (2)結果文(数値・比較・結果/因果動詞等) (3)段落/文/語数の上限 のいずれかに
    達した時点で打ち切る(その文自体は渡さない)。渡す語数がMIN_EXCERPT_WORDS未満なら空(=Part1+Part2のみへフォールバック)。
    Part 3の一定割合を無条件に渡す実装ではない。"""
    paras = [p for p in re.split(r"\n\s*\n", part3.strip()) if p.strip()]
    sentences: list[tuple[int, str]] = []
    for pi, p in enumerate(paras):
        for s in split_sentences(p):
            sentences.append((pi, s))
    passed: list[tuple[int, str]] = []
    words = 0
    cut_reason = "END_OF_PART3"
    cut_sentence = None
    for pi, s in sentences:
        if pi >= MAX_EXCERPT_PARAGRAPHS:
            cut_reason, cut_sentence = "MAX_PARAGRAPHS", s
            break
        if len(passed) >= MAX_EXCERPT_SENTENCES:
            cut_reason, cut_sentence = "MAX_SENTENCES", s
            break
        if CONCLUSION_MARKER_RE.search(s):
            cut_reason, cut_sentence = "CONCLUSION_MARKER", s
            break
        if RESULT_SENTENCE_RE.search(s):
            cut_reason, cut_sentence = "RESULT_SENTENCE", s
            break
        wc = _word_count(s)
        if words + wc > MAX_EXCERPT_WORDS:
            cut_reason, cut_sentence = "MAX_WORDS", s
            break
        passed.append((pi, s))
        words += wc
    fallback = words < MIN_EXCERPT_WORDS
    if fallback:
        cut_reason = f"{cut_reason}+EXCERPT_TOO_SHORT"
        passed = []
        words = 0
    text_parts: list[str] = []
    last_pi = None
    for pi, s in passed:
        if last_pi is not None:
            text_parts.append("\n\n" if pi != last_pi else " ")
        text_parts.append(s)
        last_pi = pi
    excerpt = "".join(text_parts)
    passed_sentences = {s for _, s in passed}
    withheld_sentences = [s for _, s in sentences if s not in passed_sentences]
    return {
        "excerpt": excerpt,
        "fallback_no_excerpt": fallback,
        "cut_reason": cut_reason,
        "cut_sentence": cut_sentence,
        "paragraph_count": len(paras),
        "sentence_count": len(sentences),
        "passed_sentence_count": len(passed),
        "passed_paragraph_indices": sorted({pi for pi, _ in passed}),
        "passed_word_count": words,
        "passed_excerpt_sha256": _sha(excerpt),
        "withheld_text": " ".join(withheld_sentences),
        "withheld_sentence_count": len(withheld_sentences),
        "part3_sha256": _sha(part3),
    }


def build_comment3_context_x_std(parts: dict, excerpt_info: dict | None = None) -> str:
    """Comment 3のcontext。Trial(generate_after_01.py CTX[3])と同一ラベル。渡すPart 3が空ならPart1+Part2のみ。"""
    info = excerpt_info if excerpt_info is not None else build_part3_excerpt(parts["part3"])
    heard = f"【すでに聞いた本文(前半)】\n{parts['part1']}\n\n{parts['part2']}"
    if info["excerpt"]:
        return f"{heard}\n\n【これから聞く本文(後半)】\n{info['excerpt']}"
    return heard


# ---- (c) 先取り検査(事後lint、決定論) ----
_EN_NUM_WORDS = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8",
                 "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "dozen": "12"}
_JA_NUM = {"二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}
_JA_COUNTER = "つ人個回倍割本枚台件年月日時間分度種"
JA_CONCLUSION_WORDS = ("結論", "結局", "最終的", "答えは", "判明", "証明", "突き止め", "正体は", "明らかになり")
STRUCT_LABEL_RE = re.compile(r"(Part\s*\d|Full\s*Story|第\s*\d\s*部|本文\s*\d)", re.I)


def _numbers_en(text: str) -> set[str]:
    t = unicodedata.normalize("NFKC", text).replace(",", "")
    nums = set(re.findall(r"\d+(?:\.\d+)?", t))
    nums |= {_EN_NUM_WORDS[w.lower()] for w in re.findall(r"[A-Za-z]+", t) if w.lower() in _EN_NUM_WORDS}
    return nums


def _numbers_ja(text: str) -> set[str]:
    t = unicodedata.normalize("NFKC", text).replace(",", "")
    nums = set(re.findall(r"\d+(?:\.\d+)?", t))
    for m in re.finditer(rf"([二三四五六七八九])(?=[{_JA_COUNTER}])", t):
        nums.add(_JA_NUM[m.group(1)])
    return nums


def _terms_en(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text)}


def comment3_spoiler_lint(comment_text: str, *, part1: str, part2: str, excerpt: str, withheld_text: str) -> list[dict]:
    """生成されたComment 3の事後検査。blocking違反のlistを返す(空=合格)。
    WITHHELD_NUMBER: 渡さなかったPart 3部分にだけ現れる数値(Part1/2/excerptに無い数値)がCommentにある
    WITHHELD_TERM: 渡さなかったPart 3部分にだけ現れる英語語(4字以上)がCommentにそのまま現れる
    CONCLUSION_WORD: 結論の先取りを示す日本語語(JA_CONCLUSION_WORDS)
    STRUCT_LABEL: 制作内部の構造ラベル(Part N / Full Story / 第N部 / 本文N)
    Zの物語語彙lint(『記事』『ニュース』禁止等)は適用しない(Xの正規文言と矛盾するため)。"""
    v: list[dict] = []
    visible = f"{part1}\n{part2}\n{excerpt}"
    leaked = sorted(_numbers_ja(comment_text) & (_numbers_en(withheld_text) - _numbers_en(visible)))
    if leaked:
        v.append({"code": "WITHHELD_NUMBER", "detail": leaked})
    leaked_t = sorted((_terms_en(withheld_text) - _terms_en(visible)) & _terms_en(comment_text))
    if leaked_t:
        v.append({"code": "WITHHELD_TERM", "detail": leaked_t})
    hit = [w for w in JA_CONCLUSION_WORDS if w in comment_text]
    if hit:
        v.append({"code": "CONCLUSION_WORD", "detail": hit})
    m = STRUCT_LABEL_RE.search(comment_text)
    if m:
        v.append({"code": "STRUCT_LABEL", "detail": m.group(0)})
    return v


def run_comment3_z_method(run_support, parts: dict) -> dict:
    """Comment 3生成の唯一の入口(委任_02でProduction `run_family_x_a2_scaffold`のComment 3行から呼ぶ)。
    run_support(role, context)->`a2gen.run_support_text`互換dict(status/text/prompt/attempts)。ProductionではJ2適用済みの
    `_a2_run_support_text_j2`をclient/model束縛で渡す。本関数はAPIを直接呼ばない。
    流れ: excerpt構築 → 生成 → lint → 違反なら1回retry(同一入力) → なお違反ならPart1+Part2のみで生成(excerptが既に空なら省略) → lint。
    戻り値は`run_support_text`互換dict+`comment3_z_audit`。最終lint不合格時はstatus=COMMENT3_SPOILER_LINT_FAILED・text=None(下流は停止/HR)。"""
    info = build_part3_excerpt(parts["part3"])
    mode0 = "PART12_ONLY_NO_SAFE_EXCERPT" if info["fallback_no_excerpt"] else "Z_EXCERPT"
    audit = {
        "method_version": COMMENT3_Z_METHOD_VERSION, "role_const": "er003_v1_iran01_a2_generate.COMMENT_2_ROLE",
        "role_sha256": COMMENT3_Z_ROLE_SHA256,
        "excerpt": {k: info[k] for k in ("fallback_no_excerpt", "cut_reason", "paragraph_count", "sentence_count",
                                         "passed_sentence_count", "passed_paragraph_indices", "passed_word_count",
                                         "passed_excerpt_sha256", "withheld_sentence_count", "part3_sha256")},
        "mode": mode0, "attempts": [], "lint_retry_count": 0, "final_context_mode": None,
    }
    ctx0 = build_comment3_context_x_std(parts, info)
    plans = [(info["excerpt"], info["withheld_text"], ctx0, mode0),
             (info["excerpt"], info["withheld_text"], ctx0, mode0)]   # 2本目=lint違反時の1回retry(同一入力)
    if not info["fallback_no_excerpt"]:   # excerptがある場合だけ、Part1+Part2のみへの縮退が意味を持つ
        plans.append(("", parts["part3"], build_comment3_context_x_std(parts, dict(info, excerpt="")), "PART12_ONLY_LINT_FALLBACK"))
    last = None
    for i, (exc, wh, ctx, mode) in enumerate(plans):
        r = run_support(COMMENT3_Z_ROLE, ctx)
        last = r
        entry = {"attempt": i + 1, "mode": mode, "context_sha256": _sha(ctx), "status": r.get("status")}
        audit["attempts"].append(entry)
        if r.get("status") != "OK" or not isinstance(r.get("text"), str):
            audit["final_status"] = r.get("status")   # 技術失敗(run_support_text自身が2回retry済み)は既存の失敗扱いに委ねる
            r["comment3_z_audit"] = audit
            return r
        viol = comment3_spoiler_lint(r["text"], part1=parts["part1"], part2=parts["part2"], excerpt=exc, withheld_text=wh)
        entry["lint_violations"] = viol
        if not viol:
            audit.update(final_context_mode=mode, lint_retry_count=i, final_status="OK")
            r["comment3_z_audit"] = audit
            return r
    audit.update(lint_retry_count=len(plans) - 1, final_status="COMMENT3_SPOILER_LINT_FAILED", final_context_mode=plans[-1][3])
    out = dict(last)
    out["rejected_text"] = out.get("text")
    out["text"] = None
    out["status"] = "COMMENT3_SPOILER_LINT_FAILED"
    out["comment3_z_audit"] = audit
    return out
