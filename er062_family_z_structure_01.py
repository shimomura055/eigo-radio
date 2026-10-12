# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04B: Family Z 構造処理(LLM呼出なし、純粋関数)。

担当: 段落整形・Story 3分割の候補列挙・Dialogue話者の決定論判定と突合・clip計画(Family C
plan_story_segmentsの全文1回呼出+id改名)・Preview/Comment/KPの決定論lint。
LLM呼出・Writer鎖・CLIは er062_family_z_writer_01.py。本moduleは課金0でtestできる。

Family C(er013)は import のみ(編集しない)。Production正式path(Z)用であり、Trial/他Familyからは使わない。
"""
from __future__ import annotations

import hashlib
import json
import re

import er013_family_c_production_01 as fam_c

SPEAKERS = ("melos", "king", "friend", "other", "narrator")
# Family C keyword窓判定用(挿入順に判定、最初に一致したvoice)。keywordに無い語(he/she等)は
# default=narrator(=「決定論は判定不能」)になり、LLM判定のみで確定する(llm_only)。
Z_VOICE_KEYWORDS = {
    "melos": ["melos"],
    "king": ["ruler", "king", "tyrant"],
    "friend": ["friend"],
}
PART_RATIO_RANGE = (0.20, 0.45)
QUOTE_RE = fam_c.DEFAULT_QUOTE_RE
_EPS = 1e-9


class FamilyZStop(RuntimeError):
    """Family Z工程のSTOP(自動継続しない)基底。"""


class FamilyZSplitStop(FamilyZStop):
    pass


class FamilyZDialogueMismatchStop(FamilyZStop):
    pass


class FamilyZLintStop(FamilyZStop):
    pass


class FamilyZProvenanceMismatchStop(FamilyZStop):
    pass


class FamilyZPlanStop(FamilyZStop):
    pass


# ------------------------------------------------------------
# STOPセンチネル(委任_11 再発防止。Fable/ユーザーが仕様変更等で実行を止めたいときの合図ファイル)
# 各API呼出の直前・各clipの直前に確認し、存在すれば新規API呼出をせず監査記録を書いて停止(runnerはrc=3)。
# ------------------------------------------------------------
STOP_ALL_PATH = "er026_output/family_z_production_e2e_01/STOP_ALL"
STOP_EXIT_CODE = 3
_STOP_RUN_DIR = None


class FamilyZStopSentinel(FamilyZStop):
    """STOPセンチネル検出。自動再開・再試行しない。"""


def set_stop_run_dir(run_dir) -> None:
    global _STOP_RUN_DIR
    _STOP_RUN_DIR = run_dir


def stop_sentinel_hit(run_dir=None):
    """存在するセンチネルのpathを返す(なければNone)。API 0・書込 0。"""
    import os
    rd = run_dir or _STOP_RUN_DIR
    for pth in ([f"{rd}/STOP"] if rd else []) + [STOP_ALL_PATH]:
        if os.path.exists(pth):
            return pth
    return None


def check_stop_sentinel(where: str, run_dir=None) -> None:
    """センチネルがあれば監査記録(<run>/audit_stop_sentinel.jsonl)を書いて FamilyZStopSentinel を送出する。"""
    import datetime
    import os
    hit = stop_sentinel_hit(run_dir)
    if hit is None:
        return
    rd = run_dir or _STOP_RUN_DIR
    if rd and os.path.isdir(rd):
        with open(f"{rd}/audit_stop_sentinel.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": datetime.datetime.now().isoformat(), "where": where, "sentinel": hit},
                               ensure_ascii=False) + "\n")
    raise FamilyZStopSentinel(f"FAMILY_Z_STOP_SENTINEL: {hit} が存在するため {where} の前で停止(新規API呼出なし)。"
                              "自動再開/再試行はしない。Fable/ユーザーの指示を待つこと。")


def sha(s) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s or b"").hexdigest()


# ------------------------------------------------------------
# 1. 段落整形
# ------------------------------------------------------------
_TITLE_RE = re.compile(r"^\s*#\s+(.+?)\s*$")


def split_title_body(text: str) -> tuple:
    """先頭の非空行が `# Title` ならtitleとして分離する。(title|None, body)。"""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines):
        m = _TITLE_RE.match(lines[i])
        if m:
            return m.group(1).strip(), "\n".join(lines[i + 1:]).strip("\n")
    return None, "\n".join(lines).strip("\n")


def clean_body_paragraphs(body: str) -> list:
    """本文を空行区切りの段落listにする。強調記号(*)は音声化に不要なので除去する。
    段落内の改行は空白へ。空段落は捨てる(=全paragraph indexが非空段落を指す)。"""
    body = (body or "").replace("\r\n", "\n").replace("*", "")
    paras = []
    for p in re.split(r"\n\s*\n", body):
        q = " ".join(p.split())
        if q:
            paras.append(q)
    return paras


def para_word_counts(paragraphs) -> list:
    return [len(fam_c.normalize_for_tts(p).split()) for p in paragraphs]


def body_word_count(text: str) -> int:
    """見出し(# 行)を除いた語数。"""
    _t, body = split_title_body(text)
    return sum(para_word_counts(clean_body_paragraphs(body)))


# ------------------------------------------------------------
# 2. Story 3分割: 決定論の候補列挙
# ------------------------------------------------------------
def enumerate_split_candidates(wcs, lo: float = PART_RATIO_RANGE[0], hi: float = PART_RATIO_RANGE[1]) -> list:
    """段落境界ペア(b1<b2)を全列挙。b1=Part2の先頭段落index、b2=Part3の先頭段落index。
    Part1=[0,b1), Part2=[b1,b2), Part3=[b2,n)の各語数比が [lo,hi] (両端含む)。候補が空なら空list。"""
    n = len(wcs)
    total = sum(wcs)
    if n < 3 or total <= 0:
        return []
    pre = [0]
    for w in wcs:
        pre.append(pre[-1] + w)
    out = []
    for b1 in range(1, n - 1):
        r1 = pre[b1] / total
        if r1 < lo - _EPS or r1 > hi + _EPS:
            continue
        for b2 in range(b1 + 1, n):
            r2 = (pre[b2] - pre[b1]) / total
            r3 = (total - pre[b2]) / total
            if lo - _EPS <= r2 <= hi + _EPS and lo - _EPS <= r3 <= hi + _EPS:
                out.append((b1, b2))
    return out


def candidates_as_ranges(cands) -> dict:
    """{b1: [(b2_lo, b2_hi), ...]} 連続区間へ圧縮(LLM Prompt用)。"""
    by = {}
    for b1, b2 in cands:
        by.setdefault(b1, []).append(b2)
    out = {}
    for b1, vals in by.items():
        vals.sort()
        runs = []
        s = p = vals[0]
        for v in vals[1:]:
            if v == p + 1:
                p = v
            else:
                runs.append((s, p))
                s = p = v
        runs.append((s, p))
        out[b1] = runs
    return out


def part_stats(wcs, b1: int, b2: int) -> list:
    total = sum(wcs) or 1
    segs = [(0, b1), (b1, b2), (b2, len(wcs))]
    out = []
    for i, (a, b) in enumerate(segs, start=1):
        w = sum(wcs[a:b])
        out.append({"part": i, "paragraph_range": [a, b - 1], "word_count": w, "ratio": round(w / total, 4)})
    return out


def part_of_paragraph(p_idx: int, b1: int, b2: int) -> int:
    return 1 + (1 if p_idx >= b1 else 0) + (1 if p_idx >= b2 else 0)


def part_texts(paragraphs, b1: int, b2: int) -> dict:
    return {1: "\n\n".join(paragraphs[:b1]), 2: "\n\n".join(paragraphs[b1:b2]), 3: "\n\n".join(paragraphs[b2:])}


def validate_split_choice(choice, cands) -> tuple:
    """(ok, reason)。candsに無いペア(候補外)は拒否する。"""
    try:
        pair = (int(choice[0]), int(choice[1]))
    except Exception:  # noqa: BLE001
        return False, "NOT_A_PAIR"
    if pair not in set(cands):
        return False, f"OUT_OF_CANDIDATES:{pair}"
    return True, "OK"


# ------------------------------------------------------------
# 3. Dialogue話者判定(決定論 + LLM突合)
# ------------------------------------------------------------
def extract_quotes(paragraphs) -> list:
    quotes = []
    for p_idx, para in enumerate(paragraphs):
        for k, m in enumerate(QUOTE_RE.finditer(para), start=1):
            quotes.append({"quote_id": f"q{p_idx}_{k}", "paragraph_index": p_idx, "ordinal": k,
                           "start": m.start(), "end": m.end(), "text": m.group(0)})
    return quotes


def deterministic_attribution(paragraphs, quotes, voice_keywords=None) -> dict:
    """Family C keyword窓判定。{quote_id: speaker or None}。None=キーワード該当なし(判定不能)。"""
    kw = voice_keywords or Z_VOICE_KEYWORDS
    out = {}
    for q in quotes:
        v = fam_c.classify_quote_voice_window(paragraphs[q["paragraph_index"]], q["start"], q["end"], kw,
                                              default_voice="narrator")
        out[q["quote_id"]] = None if v == "narrator" else v
    return out


def reconcile_attribution(paragraphs, quotes, det: dict, llm: dict) -> dict:
    """全引用の突合。LLM結果が全quote_idを過不足なく含むこと、speakerがSPEAKERSであること。
    status: agree / llm_only(決定論=判定不能) / mismatch(決定論とLLMが異なる)。
    mismatchが1件でもあれば呼出側でSTOP(自動採用しない)。"""
    ids = [q["quote_id"] for q in quotes]
    problems = []
    if set(llm) != set(ids):
        problems.append({"missing": sorted(set(ids) - set(llm)), "extra": sorted(set(llm) - set(ids))})
    for k, v in llm.items():
        if v not in SPEAKERS:
            problems.append({"invalid_speaker": {k: v}})
    rows, final, mismatches = [], {}, []
    for q in quotes:
        qid = q["quote_id"]
        d, l = det.get(qid), llm.get(qid)
        para = paragraphs[q["paragraph_index"]]
        ctx = para[max(0, q["start"] - 60):q["end"] + 60]
        if l is None:
            status = "missing_llm"
        elif d is None:
            status = "llm_only"
        elif d == l:
            status = "agree"
        else:
            status = "mismatch"
        row = {"quote_id": qid, "paragraph_index": q["paragraph_index"], "text": q["text"],
               "context": ctx, "deterministic": d, "llm": l, "status": status}
        rows.append(row)
        if status == "mismatch":
            mismatches.append(row)
        elif status in ("agree", "llm_only"):
            final[qid] = l
    return {"rows": rows, "final": final, "mismatches": mismatches, "problems": problems,
            "ok": not mismatches and not problems and len(final) == len(ids)}


# ------------------------------------------------------------
# 4. clip計画(Family C plan_story_segments 全文1回 + id改名)
# ------------------------------------------------------------
def build_flat_chunks(paragraphs, speakers: dict) -> list:
    """(paragraph_index, voice, raw_text)のflat列。引用はspeakers[quote_id]のvoice、地の文はnarrator。
    空白のみのchunk(引用間の空白)は捨てる(単独clip化を防ぐ)。"""
    flat = []
    for p_idx, para in enumerate(paragraphs):
        pos, k = 0, 0
        for m in QUOTE_RE.finditer(para):
            k += 1
            if m.start() > pos and para[pos:m.start()].strip():
                flat.append((p_idx, "narrator", para[pos:m.start()]))
            flat.append((p_idx, speakers[f"q{p_idx}_{k}"], m.group(0)))
            pos = m.end()
        if pos < len(para) and para[pos:].strip():
            flat.append((p_idx, "narrator", para[pos:]))
    return flat


def plan_clips(paragraphs, speakers: dict, b1: int, b2: int, level: str, narration_dir: str) -> list:
    """plan_story_segmentsを全文1回で呼び(force_split_before_paragraphs={b1,b2})、ids を
    full_story_part{n}_c{k} へ改名。Part境界を跨ぐclipがあればSTOP。"""
    flat = build_flat_chunks(paragraphs, speakers)
    segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={b1, b2})
    counters = {1: 0, 2: 0, 3: 0}
    clips = []
    for s in segs:
        parts = {part_of_paragraph(i, b1, b2) for i in s["source_paragraph_indices"]}
        if len(parts) != 1:
            raise FamilyZPlanStop(f"CLIP_CROSSES_PART_BOUNDARY: {s['id']} paragraphs={s['source_paragraph_indices']} "
                                  f"boundaries=({b1},{b2})")
        part = parts.pop()
        counters[part] += 1
        cid = f"full_story_part{part}_c{counters[part]}"
        speaker = s["voice"]
        clips.append({
            "id": cid, "part": part, "voice": speaker, "speaker": speaker,
            "voice_role": "narrator" if speaker == "narrator" else f"dialogue:{speaker}",
            "paragraph_index": s["source_paragraph_indices"][0],
            "source_paragraph_indices": s["source_paragraph_indices"],
            "text": s["tts_text"], "text_sha256": sha(s["tts_text"]), "word_count": s["word_count"],
            "split_reason": s["split_reason"], "warnings": s.get("warnings", []),
            "narration_path": f"{narration_dir.rstrip('/')}/{cid}.wav",
        })
    return clips


def comment_after_segment_ids(clips) -> dict:
    """Comment2=Part1-2間(Part1最後のclipの後)、Comment3=Part2-3間(Part2最後のclipの後)。
    Comment1はStory前(既存Z)なのでここには含めない。"""
    last = {}
    for c in clips:
        last[c["part"]] = c["id"]
    return {"2": last[1], "3": last[2]}


# ------------------------------------------------------------
# 5. Std/Adv 整列・同一本文
# ------------------------------------------------------------
def split_sentences(paragraphs) -> list:
    out = []
    for p in paragraphs:
        for s in re.split(r"(?<=[.!?])[\"”’']?\s+", fam_c.normalize_for_tts(p)):
            if s.strip():
                out.append(s.strip())
    return out


def avg_sentence_len(paragraphs) -> float:
    ss = split_sentences(paragraphs)
    return (sum(len(s.split()) for s in ss) / len(ss)) if ss else 0.0


def _norm_sentence(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def identical_sentence_ratio(std_paragraphs, adv_paragraphs) -> float:
    """Std文のうちAdvの正規化済み文と完全一致する割合(M8「同一本文」判定の式)。"""
    adv = {_norm_sentence(s) for s in split_sentences(adv_paragraphs)}
    ss = [_norm_sentence(s) for s in split_sentences(std_paragraphs)]
    ss = [s for s in ss if s]
    return (sum(1 for s in ss if s in adv) / len(ss)) if ss else 0.0


# ------------------------------------------------------------
# 6. Preview/Comment 決定論lint
# ------------------------------------------------------------
STORY_LINT_CONFIG = {
    "melos": {
        "forbidden_names": ["Selinuntius", "Dionysius", "Dionys", "Phidias",
                            "セリヌンティウス", "ディオニス", "ディオニュシオス", "フィロストラトス"],
        # 過剰ネタバレ語(結末の出来事)。Preview/Comment全てで禁止。
        "spoiler_ja": ["間に合", "救われ", "救い出", "解放され", "解き放", "改心", "心を改め", "処刑を免", "助かる",
                       "助かっ", "結末", "最後には", "最後に"],
        "spoiler_en": ["in the end", "just in time", "is freed", "set free", "set them free", "changes his mind",
                       "saves his friend", "let them both go", "is spared", "turns out", "finally reaches",
                       "arrives just"],
    },
}

_LINT_COMMON = [
    ("NEWS_WORD", re.compile(r"\bnews\b|ニュース|報道|記事", re.I)),
    ("IN_ONE_LINE", re.compile(r"in\s*one\s*line|イン\s*ワン\s*ライン", re.I)),
    ("POINT_LABEL", re.compile(r"\bpoint\s*(one|two|1|2)\b|ポイント", re.I)),
    ("STRUCTURE_LABEL", re.compile(r"\bpart\s*[0-9]|パート\s*[0-9０-９一二三]|full\s*story|key\s*phrases?|"
                                   r"キーフレーズ|\bcomment\s*[0-9]|\bpreview\b|プレビュー", re.I)),
    ("LITERATURE_INTRO_LABEL", re.compile(r"true\s+(crime\s+)?story|real\s+story|実話", re.I)),
]
_LINT_LISTEN_JA = re.compile(r"聞いてみ|聞いてください|お聞き|聞き取|聴いて|耳を|注目して|注意して聞")


def is_japanese_text(text: str) -> bool:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return False
    jp = sum(1 for c in chars if "぀" <= c <= "ヿ" or "一" <= c <= "鿿")
    return jp / len(chars) >= 0.3


def is_english_text(text: str) -> bool:
    chars = [c for c in text if not c.isspace()]
    return bool(chars) and sum(c.isascii() for c in chars) / len(chars) > 0.9


def lint_support_text(text: str, lang: str, story_key: str = "melos") -> list:
    """Preview/Comment出力の決定論lint。違反コードのlist(空=OK)。
    lang='ja'(Std)は聴取指示(Family C banned phrases + 聞いてみ等)も検査。
    lang='en'(Adv)はX B1のListening Focus役割が注目点を示す設計のため聴取指示は検査しない
    (news/In One Line/Point/構造ラベル/ネタバレ/名前/言語のみ)。"""
    if lang not in ("ja", "en"):
        raise ValueError(lang)
    v = []
    t = (text or "").strip()
    if not t:
        return ["EMPTY"]
    if lang == "ja" and not is_japanese_text(t):
        v.append("LANG_NOT_JA")
    if lang == "en" and not is_english_text(t):
        v.append("LANG_NOT_EN")
    for code, rx in _LINT_COMMON:
        if rx.search(t):
            v.append(code)
    if lang == "ja":
        if fam_c.FAMILY_C_A2_COMMENT_BANNED_PATTERNS_RE.search(t) or _LINT_LISTEN_JA.search(t):
            v.append("LISTEN_INSTRUCTION")
    cfg = STORY_LINT_CONFIG.get(story_key, {})
    low = t.lower()
    for nm in cfg.get("forbidden_names", []):
        if nm.lower() in low:
            v.append(f"FORBIDDEN_NAME:{nm}")
    for term in cfg.get("spoiler_" + lang, []):
        if term.lower() in low:
            v.append(f"SPOILER:{term}")
    return v


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
