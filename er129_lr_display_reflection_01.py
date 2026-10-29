"""LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_07(Phase B / B0+B2): LR/Fallback台帳の導出module(未配線の純module)。

目的(ユーザー正式決定UD-1/UD-3、`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md`):
  LR後の英文を最終表示本文に反映する前提として、保存済みの記録(tts_generation_results.json・BlockProgress・LR記録・人間承認記録)だけから
  clip毎に「採用take・LR前後と変更箇所(anchor位置)・Fallback採用Style・表示/TTS入力/ASR正解の三者一致・確定内容との重なり(T1-T3)」を
  メモリ上で導出する。設計=INTEGRATION_01 §1/F-1/F-3/F-6/F-11、OPUS_REVIEW_01 (b)1-6・M-1〜M-6、W2 §4-§6、W4 §3、W1 §2。

性質(厳守):
  - 純関数・読取専用・LLMなし・API 0。ファイルを書くのは`write_ledger_audit`(監査用出力)だけ。run dirは書き換えない。
  - **未配線**: どのProductionコードからもimportされない(Gate・描画・TTS経路に接続していない)。既定動作は何も変わらない。
  - 分類核(`classify_adopted_take`、B4)は本moduleに作らない。本moduleの出力(ledger)をB4が受け取る。
  - 原稿・parts.json・article.mdは書き換えない(派生overlay方式、F-1)。表示反映は`display_after`(メモリ上の派生文)として返すのみ。
  - `final_adoption`(委任_06が追加する記録)が無い旧entryでも動く(④旧記録導出、無ければUNKNOWN)。
"""
from __future__ import annotations

import difflib
import glob
import hashlib
import json
import os
import re
from typing import Any

import er020_tts_retry_local_rewrite_01 as er020   # resolve_expected_text_after_local_rewrite = ASR正解の唯一の参照点(HR原文復帰もここ)
import er128_kp_confirmed_content_01 as er128      # lr_overlap(T1を純関数として再計算。confirmed_kp_lr_overlap.jsonは読まない=M-3)

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# ENGLISH_LOCK指示文のsha256(er003_v1_repro01_main_generate.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION。driftはtestで検知)
ENGLISH_LOCK_STYLE_SHA = "dcd08dcae5b0ce13fd35da0980d4cf021e0b2c0a33db0cec6c8377444b3bbf30"

KIND_NORMAL = "NORMAL"
KIND_MINIMAL_EN = "FALLBACK_MINIMAL_EN"
KIND_MINIMAL_JA = "FALLBACK_MINIMAL_JA"
KIND_ENGLISH_LOCK = "ENGLISH_LOCK"
KIND_LEGACY_DIALOGUE = "LEGACY_DIALOGUE"
FALLBACK_KINDS = (KIND_MINIMAL_EN, KIND_MINIMAL_JA, KIND_ENGLISH_LOCK, KIND_LEGACY_DIALOGUE)

# clip verdict
V_NO_LR = "NO_LR"
V_PASS = "PASS"
V_PASS_SUPERSEDED = "PASS_SUPERSEDED_BY_HUMAN"
V_UNLOCATABLE = "STOP_UNLOCATABLE"
V_AMBIGUOUS = "STOP_AMBIGUOUS"
V_PARITY = "STOP_PARITY"
V_T1, V_T2, V_T3 = "STOP_T1", "STOP_T2", "STOP_T3"
V_RECORD_INCOMPLETE = "RECORD_INCOMPLETE"
V_RECORD_MISMATCH = "RECORD_MISMATCH"


# ----------------------------------------------------------------------------- 基本部品
class _Unknown:
    """採用takeを確定できない(記録欠落)。推測しない。Gateは停止・報告は「記録なし」(OPUS (b)-1の⑤)。"""
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "UNKNOWN"


UNKNOWN = _Unknown()


def is_unknown(x: Any) -> bool:
    return x is UNKNOWN


class AdoptedTake(dict):
    """最終採用takeの導出結果(dict派生)。キー: source / how / status(OK|RECORD_MISMATCH) / depth / ordinal / slot / style_mode /
    kind / style_name / style_sha / from_style_sha / audio_sha / lr_block / human_superseded_lr / notes。"""

    def __getattr__(self, k: str) -> Any:
        try:
            return self[k]
        except KeyError as e:
            raise AttributeError(k) from e


_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "′": "'"})
_TOK = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)*")
_SENT = re.compile(r"(?<=[.!?])[\"')\]]*\s+")


_NUMWORDS = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
_NUMWORDS.update({"thirty": "30", "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90"})


def tokens(s: str | None) -> list:
    """[(小文字語, start, end)]。曲引用符は直線へ(文字数は不変なのでspanは原文字列に対して有効)。句読点は無視=句読点差はSTOPにしない(M-2)。
    数詞(one〜twenty・tens)は数字へ寄せて比較する(TTS正規化の数字化/語化の向きが表示側と逆でも位置特定・一致判定を偽STOPにしない。M-1)。"""
    t = (s or "").translate(_QUOTES)
    return [(_NUMWORDS.get(m.group(0).lower(), m.group(0).lower()), m.start(), m.end()) for m in _TOK.finditer(t)]


def _lw(s: str | None) -> list:
    return [t[0] for t in tokens(s)]


def _sha(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _file_sha(path: str | None) -> str | None:
    p = _abs(path)
    if not p or not os.path.isfile(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _abs(path: str | None) -> str | None:
    if not path:
        return None
    return path if os.path.isabs(path) else os.path.join(REPO_ROOT, path)


def _jl(path: str) -> Any:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def sentences(text: str | None) -> list:
    return [s for s in _SENT.split((text or "").strip()) if s.strip()]


# ----------------------------------------------------------------------------- 差分(M-1/M-2: 隣接一致語を取り込みreplaceへ正規化)
def compute_ops(before: str, after: str) -> list:
    """before/afterのトークン差分を`replace`のみへ正規化して返す。insert/deleteは隣接する一致語(左優先、無ければ右)を取り込み、
    隣接・重複するopは併合する。各opは `i1,i2,j1,j2`(取り込み後、before/afterのトークン範囲)と
    `core_i1,core_i2,core_j1,core_j2`(実際に変わった範囲。T3/表示置換はcoreで見る)を持つ。"""
    tb, ta = tokens(before), tokens(after)
    lb, la = [t[0] for t in tb], [t[0] for t in ta]
    raw = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, lb, la, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        ci1, ci2, cj1, cj2 = i1, i2, j1, j2
        if i1 == i2 or j1 == j2:                      # insert / delete
            if i1 > 0 and j1 > 0:
                i1, j1 = i1 - 1, j1 - 1
            elif i2 < len(lb) and j2 < len(la):
                i2, j2 = i2 + 1, j2 + 1
        raw.append({"i1": i1, "i2": i2, "j1": j1, "j2": j2, "core_i1": ci1, "core_i2": ci2, "core_j1": cj1, "core_j2": cj2})
    merged: list = []
    for op in raw:
        if merged and op["i1"] <= merged[-1]["i2"]:
            m = merged[-1]
            m["i2"], m["j2"] = max(m["i2"], op["i2"]), max(m["j2"], op["j2"])
            m["core_i2"], m["core_j2"] = max(m["core_i2"], op["core_i2"]), max(m["core_j2"], op["core_j2"])
        else:
            merged.append(dict(op))
    for op in merged:
        op["before_tokens"], op["after_tokens"] = lb[op["i1"]:op["i2"]], la[op["j1"]:op["j2"]]
        op["core_before_tokens"], op["core_after_tokens"] = lb[op["core_i1"]:op["core_i2"]], la[op["core_j1"]:op["core_j2"]]
        op["core_before_text"] = before[tb[op["core_i1"]][1]:tb[op["core_i2"] - 1][2]] if op["core_i2"] > op["core_i1"] else ""
        op["core_after_text"] = after[ta[op["core_j1"]][1]:ta[op["core_j2"] - 1][2]] if op["core_j2"] > op["core_j1"] else ""
        op["kind"] = ("replace" if op["core_i2"] > op["core_i1"] and op["core_j2"] > op["core_j1"]
                      else "delete" if op["core_i2"] > op["core_i1"] else "insert")
    return merged


# ----------------------------------------------------------------------------- anchor位置特定(M-1)
def _find_all(hay: list, needle: list) -> list:
    n = len(needle)
    return [i for i in range(0, len(hay) - n + 1) if hay[i:i + n] == needle] if n else []


def locate_op(display_text: str, op: dict, before_tokens_full: list, ks=(2, 3, 4)) -> dict:
    """変更op(replace正規化済み)の表示文中の一意位置を、前後k語(段階的)のanchorで特定する。TTS正規化(数字語化・人名発音置換・PNAP)に
    依存しないよう、anchor不一致時は片側anchorへ縮退する。戻り値 {status: OK|AMBIGUOUS|UNLOCATABLE, h(opの先頭トークンindex), k, anchor, state(BEFORE|AFTER)}。
    state=AFTER=表示文が既にafter語を含む(反映済み)。"""
    dl = [t[0] for t in tokens(display_text)]
    i1, i2 = op["i1"], op["i2"]
    body = op["before_tokens"]
    if not body:
        return {"status": "UNLOCATABLE", "reason": "op has no before tokens (edge insert)"}

    def attempt(seq_body, left_n, right_n, use_left=True, use_right=True):
        hits_by_k = None
        for k in ks:
            left = before_tokens_full[max(0, i1 - k):i1] if use_left else []
            right = before_tokens_full[i2:i2 + k] if use_right else []
            hits = [h + len(left) for h in _find_all(dl, left + seq_body + right)]
            hits_by_k = (k, hits, len(left), len(right))
            if len(hits) == 1:
                return "OK", hits_by_k
        return ("AMBIGUOUS" if hits_by_k and len(hits_by_k[1]) > 1 else "NONE"), hits_by_k

    for state, seq in (("BEFORE", body), ("AFTER", op["after_tokens"])):
        if state == "AFTER" and not seq:
            continue
        for label, (ul, ur) in (("both", (True, True)), ("left_only", (True, False)), ("right_only", (False, True))):
            st, info = attempt(seq, 0, 0, ul, ur)
            if st == "OK":
                return {"status": "OK", "h": info[1][0], "k": info[0], "anchor": label, "state": state}
            if st == "AMBIGUOUS" and label == "both" and state == "BEFORE":
                # 両側anchorでk=4でも複数 → 片側縮退は更に曖昧になるだけ。曖昧確定(STOP)
                return {"status": "AMBIGUOUS", "hits": info[1], "k": info[0], "state": state}
    return {"status": "UNLOCATABLE", "reason": "anchor not found in display text"}


def apply_overlay(display_text: str, placed: list) -> str:
    """placed=[(op, h, state)]を表示文へ派生適用して返す(原本は不変)。state=AFTERは既反映なので何もしない。
    表示側の元の綴り・引用符・句読点は、取り込み語(変更していない隣接語)について保持する。後ろのopから適用。"""
    dt = tokens(display_text)
    out = display_text
    curly = "’" in display_text
    for op, h, state in sorted(placed, key=lambda x: -x[1]):
        if state == "AFTER":
            continue
        off = op["core_i1"] - op["i1"]
        n_core = op["core_i2"] - op["core_i1"]
        a_text = op["core_after_text"]
        if curly:
            a_text = a_text.replace("'", "’")
        s_idx = h + off
        if op["kind"] == "replace":
            s, e = dt[s_idx][1], dt[s_idx + n_core - 1][2]
            out = out[:s] + a_text + out[e:]
        elif op["kind"] == "delete":
            e = dt[s_idx + n_core - 1][2]
            if s_idx > 0:
                out = out[:dt[s_idx - 1][2]] + out[e:]
            else:
                nxt = dt[s_idx + n_core][1] if s_idx + n_core < len(dt) else e
                out = out[:dt[s_idx][1]] + out[nxt:]
        else:   # insert
            if s_idx > 0:
                p = dt[s_idx - 1][2]
                out = out[:p] + " " + a_text + out[p:]
            else:
                p = dt[s_idx][1]
                out = out[:p] + a_text + " " + out[p:]
    return out


# ----------------------------------------------------------------------------- 三者一致
def _contains(hay: list, needle: list) -> bool:
    return bool(needle) and bool(_find_all(hay, needle))


def _sentence_aligned(display: str, other: str, strict_phrases: list) -> tuple:
    """otherの各文が表示文(display)に対応するか。完全一致 / 連続部分列 / 正規化差(類似度>=0.6、LR変更文以外)。
    戻り値 (ok, normalized_diffs[], detail)。strict_phrases=LR後の語列(opごと)。LR変更文は正規化差を許さない(語列を含み、類似度>=0.8)。"""
    dl = _lw(display)
    d_sents = [_lw(s) for s in sentences(display)]
    o_sent_texts = sentences(other)
    # 位置対応: 文列を整列し、1:1に対応する不一致文(replaceブロック)は正規化差の候補として位置から対にする
    paired: dict = {}
    sm = difflib.SequenceMatcher(None, [" ".join(x) for x in d_sents], [" ".join(_lw(x)) for x in o_sent_texts], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and (i2 - i1) == (j2 - j1):
            for d_i, o_j in zip(range(i1, i2), range(j1, j2)):
                paired[o_j] = d_sents[d_i]
    diffs = []
    for oj, s in enumerate(o_sent_texts):
        ot = _lw(s)
        if not ot or _contains(dl, ot):
            continue
        strict = any(_contains(ot, ph) for ph in strict_phrases if ph)
        best, best_r = None, 0.0
        for ds in d_sents:
            r = difflib.SequenceMatcher(None, ds, ot, autojunk=False).ratio()
            if r > best_r:
                best, best_r = ds, r
        if oj in paired and best_r < 0.6:
            pr = difflib.SequenceMatcher(None, paired[oj], ot, autojunk=False).ratio()
            if pr >= 0.3:
                best, best_r = paired[oj], max(best_r, pr, 0.6) if not strict else pr
        if strict:
            if best is not None and best_r >= 0.8 and any(_contains(best, ph) for ph in strict_phrases if ph and _contains(ot, ph)):
                diffs.append({"sentence": s, "ratio": round(best_r, 3), "strict": True})
                continue
            return False, diffs, {"sentence": s, "ratio": round(best_r, 3), "strict": True}
        if best_r >= 0.6:
            diffs.append({"sentence": s, "ratio": round(best_r, 3), "strict": False})
            continue
        return False, diffs, {"sentence": s, "ratio": round(best_r, 3), "strict": False}
    return True, diffs, {}


def check_text_parity(display_after_overlay: str, tts_input: str, asr_expected: str, strict_phrases: list | None = None) -> dict:
    """三者一致(文単位)。V3: TTS入力==ASR正解(語列) / V2: 表示⊇TTS入力 / V1: 表示⊇ASR正解。表示は大きいunit(part)でもよい(TTS入力が連続部分列か、
    文単位の整列で正規化差のみ)。TTS正規化差(数字語化等)はLR変更文以外ならPASS_NORMALIZEDとする(偽STOPにしない、M-1)。"""
    sp = [p for p in (strict_phrases or []) if p]
    norm = []
    if _lw(tts_input) != _lw(asr_expected):
        # TTS入力は送信前正規化(数字語化・人名発音置換・PNAP等)を受けるため、ASR正解(LR選定文)と語列が完全一致しないことがある。
        # 差がLR変更文の外(正規化差)なら許容し、LR変更文は変更語句を含み類似度>=0.8を要求する(M-1。偽STOPにしない)。
        ok, diffs, detail = _sentence_aligned(asr_expected, tts_input, sp)
        if not ok:
            return {"verdict": "MISMATCH_V3", "detail": detail}
        norm = diffs or [{"sentence": "(token-level normalization difference)", "ratio": None, "strict": False}]
    for verdict, other in (("MISMATCH_V2", tts_input), ("MISMATCH_V1", asr_expected)):
        ok, diffs, detail = _sentence_aligned(display_after_overlay, other, sp)
        if not ok:
            return {"verdict": verdict, "detail": detail}
        norm = norm or diffs
    return {"verdict": "PASS_NORMALIZED" if norm else "PASS", "detail": {"normalized_sentences": norm} if norm else {}}


# ----------------------------------------------------------------------------- 確定内容との重なり T1-T3(M-3/M-6)
def _sentence_index_of_tokens(text: str, tok_idx: int) -> int:
    pos = 0
    for si, s in enumerate(sentences(text)):
        n = len(_lw(s))
        if tok_idx < pos + n:
            return si
        pos += n
    return max(0, len(sentences(text)) - 1)


def _sent_overlap(a: list, b: list) -> bool:
    if not a or not b:
        return False
    return a == b or _contains(a, b) or _contains(b, a) or difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() >= 0.9


def check_confirmed_overlap(ledger_clip: dict, confirmed_selection: dict | None, grammar: list | None, facts: dict | None) -> dict:
    """T1=er128.lr_overlapの純関数再計算(語句交差) / T2=変更箇所を含む**1文**と確定項目・文法の出典文の重なり(M-6) /
    T3=表示側(未正規化)テキストで数字・固有名詞(M-6)。`confirmed_kp_lr_overlap.json`は読まない(M-3)。
    facts={"entities":[..], "level_text":".."}。無い項目は"SKIPPED"を返す(偽STOPにしない)。"""
    lr = ledger_clip.get("lr") or {}
    before, after = lr.get("before") or "", lr.get("after") or ""
    out: dict = {"T1": {"status": "SKIPPED", "reason": "no_confirmed_selection"}, "T2": {"status": "SKIPPED", "reason": "no_confirmed_selection"},
                 "T3": {"status": "SKIPPED", "reason": "no_ops"}}
    ops = ledger_clip.get("_ops") or []
    if not (lr.get("adopted_in_final") and ops):
        out["T1"]["reason"] = out["T2"]["reason"] = out["T3"]["reason"] = "no_adopted_lr"
        return out
    items = (confirmed_selection or {}).get("items") or []
    facts = facts or {}
    level_text = facts.get("level_text") or ""
    if items:
        hits = er128.lr_overlap(items, before, after)
        out["T1"] = {"status": "STOP" if hits else "PASS", "hits": hits}
        changed_sents = {_sentence_index_of_tokens(before, i) for op in ops for i in range(op["core_i1"], max(op["core_i2"], op["core_i1"] + 1))}
        b_sents = sentences(before)
        srcs = []
        for it in items:
            ss = it.get("source_sentence")
            if isinstance(ss, str) and ss.strip():
                srcs.append((it.get("candidate_id"), _lw(ss), "item.source_sentence"))
                continue
            forms = [x for x in (it.get("display_phrase"), it.get("used_form"), it.get("key_phrase")) if x]
            for s in sentences(level_text):
                st = _lw(s)
                if any(_contains(st, _lw(f)) for f in forms):
                    srcs.append((it.get("candidate_id"), st, "level_text_by_phrase"))
        for gi, gs in enumerate(grammar or []):
            srcs.append((f"grammar_{gi}", _lw(gs), "grammar"))
        t2 = []
        for si in sorted(changed_sents):
            cs = _lw(b_sents[si]) if si < len(b_sents) else []
            for cid, st, how in srcs:
                if _sent_overlap(cs, st):
                    t2.append({"candidate_id": cid, "changed_sentence": b_sents[si] if si < len(b_sents) else "", "via": how})
        out["T2"] = {"status": "STOP" if t2 else "PASS", "hits": t2, "source_count": len(srcs)}
    t3: dict = {"status": "PASS", "numbers": [], "entities": [], "flags": []}
    ents = [e for e in (facts.get("entities") or []) if e]
    ent_toks = [(_lw(e), e) for e in ents]
    remaining_text = ledger_clip.get("_level_text_after") or level_text
    for op in ops:
        cb, ca = op["core_before_tokens"], op["core_after_tokens"]
        # 数字は表示側の実文字(0-9)で判定する(数詞語はtokensで数字へ寄せているため、語のまま変わるものは警告に留める)
        num = re.findall(r"\d+", op["core_before_text"] + " " + op["core_after_text"])
        if num:
            t3["numbers"].append({"op": f"{op['core_before_text']} -> {op['core_after_text']}", "tokens": num})
        elif any(c.isdigit() for t in cb + ca for c in t):
            t3.setdefault("warnings", []).append(f"number_word_in_change: {op['core_before_text']} -> {op['core_after_text']}")
        for et, ename in ent_toks:
            if et and (_contains(cb, et) or (len(et) == 1 and et[0] in cb)) and not _contains(ca, et):
                still = _contains(_lw(remaining_text), et)
                t3["entities"].append({"entity": ename, "op": f"{op['core_before_text']} -> {op['core_after_text']}", "remains_elsewhere": still})
                if still:
                    t3["flags"].append("entity_pronoun_substitution")
    if t3["numbers"] or any(not e["remains_elsewhere"] for e in t3["entities"]):
        t3["status"] = "STOP"
    if not ents:
        t3["entity_check"] = "SKIPPED_NO_FACT_TABLE"
    out["T3"] = t3
    return out


# ----------------------------------------------------------------------------- 確定内容の事前保護(FZ-DIALOGUE-LR-ADOPTION-01、加算のみ)
# 台帳(`_clip_ledger`)が事後に使う `check_confirmed_overlap`(T1/T2/T3)を、同一の純関数のまま**LR候補の選定前**とLR入力転写の選択に前倒しする
# (新しいGate・基準ではない。台帳側の判定と不一致を作らないよう再実装しない)。Production(Zセリフ driver)は er063 経由でのみ呼ぶ。
def precheck_candidate_overlap(before: str, after: str, confirmed_selection: dict | None, grammar: list | None = None,
                               facts: dict | None = None) -> dict:
    """LR候補(before->after)が確定内容と重なるかを、台帳と同一のT1-T3で判定する。戻り値 {"stop": bool, "stops": ["T1",..], "overlap": {...}}。
    変更なし(ops空)は重ならない。confirmed_selectionがNone/空なら T1/T2 は SKIPPED(偽STOPにしない)。"""
    ops = compute_ops(before, after)
    clip = {"lr": {"before": before, "after": after, "adopted_in_final": True}, "_ops": ops}
    ov = check_confirmed_overlap(clip, confirmed_selection, grammar, facts)
    stops = [t for t in ("T1", "T2", "T3") if (ov.get(t) or {}).get("status") == "STOP"]
    return {"stop": bool(stops), "stops": stops, "overlap": ov}


def make_candidate_filter(confirmed_selection: dict | None, grammar: list | None = None, facts: dict | None = None):
    """`er020.run_local_rewrite_recovery(candidate_filter=)` 用。確定内容と重なる候補を `adoptable=False` にし理由を付ける(7 Gateのキー・値は不変)。
    重ならない候補・既にadoptable=Falseの候補は変更しない。"""
    def _flt(canonical_text: str, records: list) -> list:
        for r in records:
            if not r.get("adoptable"):
                continue
            pc = precheck_candidate_overlap(canonical_text, r.get("rewritten_segment") or "", confirmed_selection, grammar, facts)
            if pc["stop"]:
                r["adoptable"] = False
                r["candidate_filter_reject"] = {"reason": "LR_OVERLAPS_CONFIRMED_CONTENT", "stops": pc["stops"],
                                                "hits": {t: (pc["overlap"].get(t) or {}).get("hits") for t in pc["stops"]}}
        return records
    return _flt


def _apply_ops_to_text(text: str, ops: list) -> str:
    """compute_opsのop(core範囲)だけを text に適用した文を返す(右から順に置換。insertは該当token直前、deleteは空文字へ)。"""
    tb = tokens(text)
    out = text
    for op in sorted(ops, key=lambda o: o["core_i1"], reverse=True):
        i1, i2 = op["core_i1"], op["core_i2"]
        if i2 > i1:
            s, e = tb[i1][1], tb[i2 - 1][2]
        else:
            s = e = tb[i1][1] if i1 < len(tb) else len(text)
        out = out[:s] + op.get("core_after_text", "") + out[e:]
    return out


def input_overlaps_confirmed(canonical_text: str, ng_span: dict, asr_text: str, confirmed_selection: dict | None,
                             facts: dict | None = None) -> dict:
    """LR入力転写の候補を、NG span(`er020.identify_ng_span`の先頭diff)が確定内容(T1: 語句、T2: 出典文)と重なるかで判定する。
    canonical->ASR転写のdiffのうちNG spanの語を含むopだけを、台帳と同一の `check_confirmed_overlap`(T1/T2のみ使用。T3は入力選択に使わない)へ渡す。
    戻り値 {"protected": bool, "stops": [...], "hits": ...}。確定selectionが無ければ protected=False。"""
    if not ng_span or not ng_span.get("found") or not confirmed_selection:
        return {"protected": False, "stops": [], "hits": {}}
    ops = compute_ops(canonical_text, asr_text)
    ng_words = {str(w).lower() for w in (ng_span.get("canonical_changed_words") or [])}
    ngset = {w for t in ng_words for w in _lw(t)} or ng_words
    sel_ops = [o for o in ops if ngset & set(o.get("core_before_tokens") or [])] or ops[:1]
    # T1(語句交差)は before/after 全文のdiffで再計算される純関数のため、NG span以外の差分(転写の他の表記ゆれ)が混ざらないよう、
    # 選んだopだけをcanonicalへ適用した『仮のafter』を作って判定する(T2はopsを使うので同じopだけ)
    after_sel = _apply_ops_to_text(canonical_text, sel_ops)
    clip = {"lr": {"before": canonical_text, "after": after_sel, "adopted_in_final": True}, "_ops": compute_ops(canonical_text, after_sel)}
    ov = check_confirmed_overlap(clip, confirmed_selection, None, facts)
    stops = [t for t in ("T1", "T2") if (ov.get(t) or {}).get("status") == "STOP"]
    return {"protected": bool(stops), "stops": stops, "hits": {t: (ov.get(t) or {}).get("hits") for t in stops}}


def level_facts(level_dir: str, clip_text: str = "") -> dict:
    """Zセリフの確定保護用 facts({"entities","level_text"})を台帳(`build_lr_ledger`)と同じ出典から組む。取れない項目は空(SKIPPED扱い)。"""
    results = _jl(os.path.join(level_dir, "audit", "tts_generation_results.json")) or {}
    texts = [e.get("canonical_text") for _, e, _ in _iter_entries(results) if isinstance(e.get("canonical_text"), str)]
    level_text = " ".join(texts + ([clip_text] if clip_text else []))
    parts = _jl(os.path.join(level_dir, "parts.json"))
    if isinstance(parts, dict):
        level_text += " " + " ".join(t for _, t in _string_leaves(parts))
    return {"entities": _entities_from_run(level_dir), "level_text": level_text}


def load_confirmed_selection(level_dir: str) -> dict | None:
    """台帳と同じ出典(`<level_dir>/audit/confirmed_selection.json`)。無ければNone。"""
    sel = _jl(os.path.join(level_dir, "audit", "confirmed_selection.json"))
    return sel if isinstance(sel, dict) else None


# ----------------------------------------------------------------------------- 採用take解決(OPUS (b)-1。「記録完全」の定義はここに一本化)
def _style_kind(*, sha: str | None, route: str | None, language: str | None, is_kp_en: bool, legacy_dialogue: bool = False) -> str:
    if legacy_dialogue:
        return KIND_LEGACY_DIALOGUE
    if sha == ENGLISH_LOCK_STYLE_SHA:
        return KIND_ENGLISH_LOCK
    r = (route or "").lower()
    if "minimal" in r or "fallback" in r:
        return KIND_MINIMAL_JA if (language or "").startswith("ja") else KIND_MINIMAL_EN
    return KIND_NORMAL


def _attempt_json_dir_and_prefix(entry: dict) -> tuple:
    p = _abs(entry.get("path") or entry.get("narration_path"))
    if not p:
        return None, None
    return os.path.join(os.path.dirname(p), "attempts"), os.path.splitext(os.path.basename(p))[0]


def _load_attempt_jsons(entry: dict) -> list:
    d, pref = _attempt_json_dir_and_prefix(entry)
    if not d or not os.path.isdir(d):
        return []
    out = []
    for f in sorted(glob.glob(os.path.join(d, f"{pref}_attempt*.json"))):
        j = _jl(f)
        if isinstance(j, dict):
            j["_file"] = f
            out.append(j)
    return out


def _normal_style_sha(entry: dict) -> str | None:
    sp = entry.get("style_profile")
    if isinstance(sp, dict) and sp.get("expected_base_sha256"):
        return sp["expected_base_sha256"]
    st = entry.get("style")
    if isinstance(st, dict) and st.get("style_prefix_sha256"):
        return st["style_prefix_sha256"]
    for key in ("standard_attempts_log", "attempts_log"):
        for r in entry.get(key) or []:
            spx = r.get("style_prefix")
            if isinstance(spx, dict) and spx.get("sha256"):
                return spx["sha256"]
    for r in entry.get("attempts") or []:
        if r.get("phase") == "standard" and r.get("style_prefix_sha256"):
            return r["style_prefix_sha256"]
    return None


_CJK = re.compile(r"[぀-ヿ一-鿿]")


def _lang_of(entry: dict) -> str:
    if entry.get("language"):
        return str(entry["language"])
    txt = (entry.get("text") if isinstance(entry.get("text"), str) else "") or (entry.get("canonical_text") if isinstance(entry.get("canonical_text"), str) else "")
    return "ja" if _CJK.search(txt or "") else "en"


def _is_kp_en(seg_id: str, entry: dict) -> bool:
    return bool(re.search(r"(^|_)kp\d*_?en($|_)|^kp\d+_en$", seg_id or "")) or entry.get("role_style_key", "").startswith("KP_EN") or (entry.get("_component") == "english")


def _take_from_attempt_json(aj: dict, *, entry: dict, seg_id: str, how: str, human: bool, lr_block: bool, real_idx: int | None) -> AdoptedTake:
    instr = aj.get("instruction_text")
    sha = _sha(instr) if isinstance(instr, str) and instr else None
    kind = _style_kind(sha=sha, route=aj.get("route"), language=aj.get("language") or _lang_of(entry), is_kp_en=_is_kp_en(seg_id, entry))
    normal = _normal_style_sha(entry)
    if kind != KIND_NORMAL and sha and normal and sha == normal:
        kind = KIND_NORMAL    # Styleが変わらない再試行はFallback扱いにしない(原文§6-B)
    slot = None   # 旧記録からは①②③を確定しない(file番号は後処理attemptを含み、HR後再試行でblock境界も動くため。ordinalのみ記録)
    return AdoptedTake(source="human_approval" if human else "derived", how=how, status="OK", depth=(None if lr_block is None else (1 if lr_block else 0)),
                       ordinal=aj.get("attempt_number"), slot=slot, style_mode="FALLBACK" if kind in FALLBACK_KINDS else "PRIMARY",
                       kind=kind, style_name=kind if kind != KIND_NORMAL else "ROLE_STYLE", style_sha=sha, from_style_sha=normal,
                       audio_sha=aj.get("sha256"), lr_block=lr_block, human_superseded_lr=False, notes=[f"route={aj.get('route')}"])


def _final_shas(entry: dict) -> set:
    s = {entry.get("sha256"), entry.get("adopted_audio_sha256")}
    sp = entry.get("speed_profile")
    if isinstance(sp, dict):
        s.add(sp.get("original_sha256"))
    op = entry.get("original_path")
    if op:
        s.add(_file_sha(op))
    return {x for x in s if x}


def _derive_from_attempt_files(entry: dict, seg_id: str, lr_adopted: bool, human_path: str | None = None, human: bool = False) -> AdoptedTake | None:
    ajs = _load_attempt_jsons(entry) if not human_path else []
    if not ajs and not human_path:
        return None
    shas = _final_shas(entry)
    if human_path:
        hp = _abs(human_path)
        jp = os.path.splitext(hp)[0] + ".json"
        aj = _jl(jp)
        if isinstance(aj, dict):
            aj["_file"] = jp
            return _take_from_attempt_json(aj, entry=entry, seg_id=seg_id, how="human_attempt_file", human=True, lr_block=False, real_idx=None)
        return None
    matched = [a for a in ajs if a.get("sha256") in shas]
    if not matched:
        return None
    aj = max(matched, key=lambda a: a.get("attempt_number") or 0)
    reals = [a for a in sorted(ajs, key=lambda a: a.get("attempt_number") or 0) if a.get("route") != "post_slowdown"]
    if aj.get("route") == "post_slowdown":
        prev = [a for a in reals if (a.get("attempt_number") or 0) < (aj.get("attempt_number") or 0)]
        if not prev:
            return None
        aj = prev[-1]
    return _take_from_attempt_json(aj, entry=entry, seg_id=seg_id, how="attempt_file_sha_match", human=human, lr_block=None, real_idx=None)


def _derive_from_logs(entry: dict, seg_id: str, lr_adopted: bool) -> AdoptedTake | None:
    normal = _normal_style_sha(entry)
    # Z会話ctx: dialogue_tts
    dt = entry.get("dialogue_tts")
    if isinstance(dt, dict) and dt.get("final_mode"):
        fm = dt.get("final_mode")
        legacy = fm == "legacy_fallback" and str(dt.get("policy") or "").lower() != "legacy"
        return AdoptedTake(source="derived", how="dialogue_tts.final_mode", status="OK", depth=0, ordinal=dt.get("final_attempt_n"),
                           slot=None, style_mode="FALLBACK" if legacy else "PRIMARY", kind=KIND_LEGACY_DIALOGUE if legacy else KIND_NORMAL,
                           style_name="LEGACY_DIALOGUE" if legacy else "DIALOGUE_STYLE", style_sha=None, from_style_sha=None,
                           audio_sha=entry.get("sha256"), lr_block=False, human_superseded_lr=False, notes=[f"final_mode={fm}"])
    kp_en = _is_kp_en(seg_id, entry)
    lang = _lang_of(entry)
    # KP_EN: ENGLISH_LOCK段(english_lock_attempts_log)が実Fallback。fallback_attempts_logは前段(命名逆転、W1 DR-6)なので読まない
    el = [r for r in entry.get("english_lock_attempts_log") or [] if r.get("verified") is True]
    if el:
        return AdoptedTake(source="derived", how="english_lock_attempts_log.verified", status="OK", depth=0, ordinal=el[-1].get("attempt"),
                           slot=None, style_mode="FALLBACK", kind=KIND_ENGLISH_LOCK, style_name="ENGLISH_LOCK", style_sha=ENGLISH_LOCK_STYLE_SHA,
                           from_style_sha=normal, audio_sha=entry.get("sha256"), lr_block=False, human_superseded_lr=False, notes=[])
    rows = None
    if entry.get("attempts_log"):
        rows = [dict(r, _log="attempts_log") for r in entry["attempts_log"]]
    elif entry.get("attempts"):
        rows = [dict(r, _log="attempts") for r in entry["attempts"]]
    if rows:
        ver = [r for r in rows if r.get("verified") is True]
        if len(ver) >= 1 and not (kp_en and entry.get("fallback_used")):
            r = ver[-1]
            spx = r.get("style_prefix")
            sha = spx.get("sha256") if isinstance(spx, dict) else r.get("style_prefix_sha256")
            route = r.get("instruction_type") or r.get("phase")
            kind = _style_kind(sha=sha, route="minimal_fallback" if (r.get("instruction_type") == "minimal_fallback" or r.get("phase") == "fallback") and not kp_en else route,
                               language=lang, is_kp_en=kp_en)
            if kind != KIND_NORMAL and sha and normal and sha == normal:
                kind = KIND_NORMAL
            if kind == KIND_NORMAL and r.get("instruction_type") == "minimal_fallback" and not sha:
                kind = KIND_MINIMAL_JA if (lang or "").startswith("ja") else KIND_MINIMAL_EN
            lr_block = bool(lr_adopted and len(ver) >= 1 and rows.index(r) >= 3)
            return AdoptedTake(source="derived", how=f"{r['_log']}.verified", status="OK", depth=1 if lr_block else 0, ordinal=r.get("attempt") or r.get("n"),
                               slot=None, style_mode="FALLBACK" if kind in FALLBACK_KINDS else "PRIMARY", kind=kind,
                               style_name=kind if kind != KIND_NORMAL else "ROLE_STYLE", style_sha=sha, from_style_sha=normal,
                               audio_sha=entry.get("sha256"), lr_block=lr_block, human_superseded_lr=False,
                               notes=["multiple verified rows; last used"] if len(ver) > 1 else [])
    # 最終手段(LR採用なし): entry直下fallback_used(OPEN-564以降は採用attempt種別に従う)。LR採用entryでは旧runの誤値があるため使わない
    if not lr_adopted and entry.get("status") == "OK" and not kp_en:
        std = entry.get("standard_attempts_log") or []
        fbl = entry.get("fallback_attempts_log") or []
        if entry.get("fallback_used") is True and any(r.get("verified") is True for r in std + fbl):
            kind = KIND_MINIMAL_JA if lang.startswith("ja") else KIND_MINIMAL_EN
            return AdoptedTake(source="derived", how="fallback_used_flag(no LR)+verified row", status="OK", depth=0, ordinal=None, slot=None, style_mode="FALLBACK",
                               kind=kind, style_name=kind, style_sha=None, from_style_sha=normal, audio_sha=entry.get("sha256"), lr_block=False,
                               human_superseded_lr=False, notes=["style sha unavailable in attempt rows"])
        if entry.get("fallback_used") is False and any(r.get("verified") is True for r in std):
            return AdoptedTake(source="derived", how="standard_attempts_log.verified(no fallback)", status="OK", depth=0, ordinal=None, slot=None, style_mode="PRIMARY",
                               kind=KIND_NORMAL, style_name="ROLE_STYLE", style_sha=None, from_style_sha=normal, audio_sha=entry.get("sha256"), lr_block=False,
                               human_superseded_lr=False, notes=[])
    return None


def resolve_adopted_take(entry: dict, block_progress: dict | None, hr_records: dict | None, store_info: dict | None = None, *,
                         seg_id: str = "", lr_adopted: bool = False):
    """最終採用takeを一意に解決する。優先順位(OPUS (b)-1): ①人間承認の採用記録 ②再利用(Store key/`reused`) ③`final_adoption`とBlockProgress
    `verified`(depth,ordinal)の突合(食い違い=RECORD_MISMATCH) ④旧記録からの導出(attempt wavのsha一致→attempts_log/english_lock_attempts_log/
    dialogue_tts等。fallback_attempts_logはKP_ENでは前段=命名逆転を読まない) ⑤UNKNOWN。
    「記録完全」=AdoptedTake(status=OK)が返ること。UNKNOWN/RECORD_MISMATCHは完全ではない(Gateは停止・報告は「記録なし」)。"""
    hr = (hr_records or {}).get(seg_id) or {}
    # ① 人間承認
    flagged = bool(entry.get(er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG)) or bool(entry.get("adopted_attempt_audio_path")) or bool(hr.get("adopted_attempt_wav") or hr.get("adopted_attempt_audio_path"))
    if flagged:
        path = entry.get("adopted_attempt_audio_path") or hr.get("adopted_attempt_wav") or hr.get("adopted_attempt_audio_path")
        t = _derive_from_attempt_files(entry, seg_id, lr_adopted=False, human_path=path, human=True) if path else None
        if t is None:
            return UNKNOWN if not path else AdoptedTake(source="human_approval", how="no_attempt_json", status="OK", depth=0, ordinal=hr.get("adopted_attempt"),
                                                        slot=None, style_mode=None, kind=None, style_name=None, style_sha=None, from_style_sha=_normal_style_sha(entry),
                                                        audio_sha=entry.get("adopted_audio_sha256"), lr_block=False, human_superseded_lr=True,
                                                        notes=["attempt json not found; style unknown"])
        t["human_superseded_lr"] = bool(entry.get(er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG))
        return t
    if entry.get("status") not in (None, "OK") and not entry.get("final_adoption"):
        # 採用なし(STOPPED・ASR NG等の終端NG)。採用take自体が存在しない=UNKNOWN(記録欠落)ではない
        return AdoptedTake(source="not_adopted", how=f"status={entry.get('status')}", status="NOT_ADOPTED", depth=None, ordinal=None, slot=None,
                           style_mode=None, kind=None, style_name=None, style_sha=None, from_style_sha=None, audio_sha=None, lr_block=None,
                           human_superseded_lr=False, notes=["no adopted take (terminal NG / stopped)"])
    fa = entry.get("final_adoption")
    # ② 再利用
    if entry.get("reused") is True or (isinstance(fa, dict) and fa.get("source") == "store_reuse") or (store_info or {}).get("reused"):
        if isinstance(fa, dict):
            mode = fa.get("style_mode")
            sha = fa.get("sent_style_sha")
            kind = KIND_ENGLISH_LOCK if (sha == ENGLISH_LOCK_STYLE_SHA or fa.get("style_name") == "ENGLISH_LOCK") else (KIND_NORMAL if mode == "PRIMARY" else _style_kind(sha=sha, route="fallback", language=entry.get("language"), is_kp_en=_is_kp_en(seg_id, entry)))
            return AdoptedTake(source="store_reuse", how="final_adoption.store_reuse", status="OK", depth=fa.get("depth", 0), ordinal=None, slot=None,
                               style_mode=mode, kind=kind, style_name=fa.get("style_name") or ("ROLE_STYLE" if kind == KIND_NORMAL else kind), style_sha=sha,
                               from_style_sha=_normal_style_sha(entry), audio_sha=fa.get("attempt_audio_sha"), lr_block=False, human_superseded_lr=False,
                               notes=["TTS未実行(Store再利用)"])
        # 固定殻・固定MP3(`existing_master`、TTS生成なし、既存方式維持): 採用takeは「既存資産」。Fallback/LRの対象外
        if entry.get("tts_backend") == "existing_master" and not (entry.get("style") or {}).get("fallback_used"):
            return AdoptedTake(source="fixed_asset", how="existing_master", status="OK", depth=0, ordinal=None, slot=None, style_mode="PRIMARY",
                               kind=KIND_NORMAL, style_name="FIXED_ASSET", style_sha=None, from_style_sha=None, audio_sha=entry.get("sha256"),
                               lr_block=False, human_superseded_lr=False, notes=["固定殻/固定MP3(TTS生成なし)"])
        # 旧entry: 再利用だが採用記録なし。元entryの記録(fallback_used等)から継承できるか
        t = _derive_from_logs(entry, seg_id, lr_adopted)
        if t is not None:
            t["source"], t["notes"] = "store_reuse", t["notes"] + ["旧entry(final_adoptionなし)、元記録を継承"]
            return t
        return UNKNOWN
    # ③ final_adoption と BlockProgress の突合
    if isinstance(fa, dict) and fa.get("style_mode"):
        status, notes = "OK", []
        depth, ordinal = fa.get("depth", 0), fa.get("ordinal")
        blocks = (block_progress or {}).get("blocks") if isinstance(block_progress, dict) else None
        if isinstance(blocks, dict) and ordinal is not None:
            b = blocks.get(str(depth))
            if isinstance(b, dict) and isinstance(b.get("attempts"), dict):
                a = b["attempts"].get(str(ordinal))
                if not (isinstance(a, dict) and a.get("verified") is True):
                    status = V_RECORD_MISMATCH
                    notes.append(f"BlockProgress blocks[{depth}].attempts[{ordinal}].verified is not True")
            else:
                notes.append("BlockProgress block record absent (old/resume); not cross-checked")
        else:
            notes.append("no BlockProgress; not cross-checked")
        sha = fa.get("sent_style_sha")
        mode = fa.get("style_mode")
        lang = entry.get("language")
        if mode == "FALLBACK":
            dt = entry.get("dialogue_tts")
            kind = _style_kind(sha=sha, route="fallback", language=lang, is_kp_en=_is_kp_en(seg_id, entry),
                               legacy_dialogue=isinstance(dt, dict) and "dialogue" in str(entry.get("clip_kind") or "") + str(entry.get("role_style_key") or "").lower() + "dialogue_tts")
            if _is_kp_en(seg_id, entry) and kind in (KIND_MINIMAL_EN,):
                kind = KIND_ENGLISH_LOCK
        else:
            kind = KIND_NORMAL
        return AdoptedTake(source="final_adoption", how="final_adoption", status=status, depth=depth, ordinal=ordinal, slot=fa.get("slot"),
                           style_mode=mode, kind=kind, style_name=fa.get("style_name") or (kind if kind != KIND_NORMAL else "ROLE_STYLE"),
                           style_sha=sha, from_style_sha=_normal_style_sha(entry), audio_sha=fa.get("attempt_audio_sha"), lr_block=bool(depth and depth >= 1),
                           human_superseded_lr=False, notes=notes)
    # ④ 旧記録導出
    dt0 = entry.get("dialogue_tts")
    if isinstance(dt0, dict) and dt0.get("final_mode"):
        t = _derive_from_logs(entry, seg_id, lr_adopted)      # Z会話はdialogue_tts.final_modeが採用modeの直接記録(attempt wav/jsonはmode情報を持たない)
    else:
        t = _derive_from_attempt_files(entry, seg_id, lr_adopted)
        if t is None:
            t = _derive_from_logs(entry, seg_id, lr_adopted)
    if t is not None:
        return t
    # 採用attemptが無いのはFallback/LR証跡も無い通常entryのこともある(呼出側が`_has_event_evidence`で絞る)。確定不能=UNKNOWN
    return UNKNOWN


# ----------------------------------------------------------------------------- LR情報
def _lr_info(entry: dict, canonical_text: str) -> dict | None:
    """LR記録の正規化。X/Y=`local_rewrite_recovery`、Z=`audio_text_deviation`、resume形(`rewritten_segment`のみ)に対応。
    ASR正解/最終音声の文は`er020.resolve_expected_text_after_local_rewrite`を唯一の参照点とする(HR原文復帰もそこで反映)。"""
    rec = entry.get("local_rewrite_recovery")
    dev = entry.get("audio_text_deviation")
    has_x = isinstance(rec, dict) and rec.get("status") == "RESOLVED_BY_LOCAL_REWRITE"
    has_z = isinstance(dev, dict) and isinstance(dev.get("audio_text_after"), str) and dev.get("audio_text_after") != canonical_text
    if not (has_x or has_z):
        return None
    human = bool(entry.get(er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG))
    probe = {k: v for k, v in entry.items() if k != er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG}
    after_lr, src_lr = er020.resolve_expected_text_after_local_rewrite(probe, canonical_text)
    expected, src_exp = er020.resolve_expected_text_after_local_rewrite(entry, canonical_text)
    before = (entry.get("canonical_text_before_local_rewrite") or (dev or {}).get("canonical_text_before_local_rewrite")
              or (rec or {}).get("canonical_text") or canonical_text)
    reason, rsrc, spans = None, "unavailable", None
    if has_x:
        sel = ((rec.get("selection") or {}).get("selected") or {})
        spans = {"before": sel.get("changed_span_before"), "after": sel.get("changed_span_after")}
        cid = sel.get("candidate_id") or sel.get("id")
        rat = sel.get("rationale")
        if not rat:
            for c in ((rec.get("candidate_gen") or {}).get("candidates") or []):
                if str(c.get("id")) == str(cid) or c.get("rewritten_segment") == sel.get("rewritten_segment"):
                    rat = c.get("rationale")
                    break
        if not rat:
            # 委任_15(B10) D4: resume形(LR LLM再実行なし)はBlockProgressから復元した選定根拠`lr_selection_audit_restored`(er127.lr_recover)にだけ理由が残る
            ra = rec.get("lr_selection_audit_restored")
            rsel = (ra.get("selected") or {}) if isinstance(ra, dict) else {}
            rrat = rsel.get("rationale")
            if rrat and (rsel.get("rewritten_segment") in (None, sel.get("rewritten_segment"))):
                reason, rsrc = rrat, "local_rewrite_recovery.lr_selection_audit_restored"
                rat = None
        if rat:
            reason, rsrc = rat, "local_rewrite_recovery"
        elif reason:
            pass
        elif rec.get("resumed_without_llm") or "rewritten_segment" in sel:
            reason, rsrc = None, "resumed(rationale unavailable)"
    else:
        spans = {"diff_summary": dev.get("diff_summary")}
        rsrc = "audio_text_deviation"
    return {"before": before, "after": after_lr, "adopted_in_final": not human, "superseded_by_human": human,
            "asr_expected": expected, "asr_expected_source": src_exp, "after_source": src_lr, "reason": reason, "reason_source": rsrc,
            "recorded_spans": spans, "form": "X/Y" if has_x else "Z"}


def _has_event_evidence(entry: dict) -> bool:
    if entry.get("local_rewrite_recovery") or entry.get("audio_text_deviation") or entry.get("final_adoption"):
        return True
    if entry.get("fallback_used") or entry.get("fallback_attempts_log") or entry.get("english_lock_attempts_log"):
        return True
    if isinstance(entry.get("style"), dict) and (entry["style"].get("fallback_used") or entry["style"].get("fallback_attempts")):
        return True
    dt = entry.get("dialogue_tts")
    if isinstance(dt, dict) and dt.get("final_mode") == "legacy_fallback":
        return True
    if entry.get("adopted_attempt_audio_path"):
        return True
    for key in ("attempts_log", "attempts"):
        for r in entry.get(key) or []:
            if r.get("instruction_type") == "minimal_fallback" or r.get("phase") == "fallback":
                return True
    return False


# ----------------------------------------------------------------------------- 表示本文の取得
def _string_leaves(o: Any, path: str = "") -> list:
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            out += _string_leaves(v, f"{path}.{k}" if path else str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out += _string_leaves(v, f"{path}[{i}]")
    elif isinstance(o, str) and o.strip():
        out.append((path, o))
    return out


def _display_candidates(seg_id: str, entry: dict, level_dir: str) -> list:
    """表示unitの候補(優先順)。[(source, text)]。X: parts.json part*/in_one_line、Y: parts.json segments、support texts、最後にentryのcanonical_text(表示形)。"""
    cands = []
    parts = _jl(os.path.join(level_dir, "parts.json")) if level_dir else None
    parent = (entry.get("chunk_tts") or {}).get("parent_id") or seg_id
    m = re.match(r"^full_story_(part\d+)", parent or "")
    keys = []
    if m:
        keys.append(m.group(1))
    keys += [parent, seg_id, re.sub(r"_(k|c)\d+$", "", seg_id or "")]
    if isinstance(parts, dict):
        segs = parts.get("segments") if isinstance(parts.get("segments"), dict) else {}
        for k in keys:
            if isinstance(parts.get(k), str):
                cands.append((f"parts.json:{k}", parts[k]))
            if isinstance(segs.get(k), str):
                cands.append((f"parts.json:segments.{k}", segs[k]))
    for sp in glob.glob(os.path.join(level_dir or "", "*support_texts.json")):
        d = _jl(sp)
        if isinstance(d, dict):
            for k in keys:
                if isinstance(d.get(k), str):
                    cands.append((f"{os.path.basename(sp)}:{k}", d[k]))
    ct = entry.get("canonical_text")
    if isinstance(ct, str) and ct.strip():
        cands.append(("entry.canonical_text", ct))
    seen, out = set(), []
    for s, t in cands:
        if (s, t) not in seen:
            seen.add((s, t))
            out.append((s, t))
    return out


# ----------------------------------------------------------------------------- 台帳導出
def _hr_records(level_dir: str) -> dict:
    out: dict = {}
    audit = os.path.join(level_dir, "audit")
    rl = _jl(os.path.join(audit, "review_lock_state.json"))
    if isinstance(rl, dict):
        for k, v in rl.items():
            if isinstance(v, dict) and v.get("final_status") == "HUMAN_APPROVED":
                out[k] = {"adopted_attempt_audio_path": v.get("adopted_attempt_audio_path"), "adopted_audio_sha256": v.get("adopted_audio_sha256")}
    for f in glob.glob(os.path.join(audit, "ypl7_user_approval_record_*.json")):
        d = _jl(f)
        if isinstance(d, dict) and d.get("segment"):
            out[d["segment"]] = {"adopted_attempt_wav": d.get("adopted_attempt_wav"), "adopted_attempt": d.get("adopted_attempt"),
                                 "adopted_audio_sha256": d.get("adopted_audio_sha256")}
    return out


def _entities_from_run(level_dir: str) -> list:
    """X: run直下 audit/entity_table.json の surface、Z: run直下 speaker_table.md の話者名。取得できなければ[](T3は偽STOPにしない=SKIPPED)。"""
    run = os.path.dirname(level_dir)
    ents: list = []
    et = _jl(os.path.join(run, "audit", "entity_table.json"))
    if isinstance(et, dict):
        for e in ((et.get("derived_snapshot") or {}).get("entries") or []):
            if isinstance(e, dict) and e.get("surface") and e.get("category") != "work_title":
                ents.append(e["surface"])
    sp = os.path.join(run, "speaker_table.md")
    if os.path.isfile(sp):
        try:
            with open(sp, encoding="utf-8") as f:
                txt = f.read()
            for name in set(re.findall(r"\|\s*([a-z]+)\s*\|\s*([a-z]+)\s*\|\s*(?:agree|llm_only|det_only|disagree)", txt)):
                for n in name:
                    if n not in ("none", "narrator"):
                        ents.append(n.capitalize())
        except OSError:
            pass
    return sorted(set(ents))


def _iter_entries(results: dict):
    for sid, e in (results.get("segments") or {}).items():
        if isinstance(e, dict):
            yield sid, e, None
    for n, comp in (results.get("key_phrases") or {}).items():
        if isinstance(comp, dict):
            for role, e in comp.items():
                if isinstance(e, dict) and (e.get("path") or e.get("sha256")):
                    ee = dict(e)
                    ee["_component"] = role
                    yield f"kp{n}_{'en' if role == 'english' else role}", ee, None


def _clip_ledger(seg_id: str, entry: dict, *, level_dir: str, hr: dict, selection: dict | None, facts: dict, level_text: str) -> dict:
    canonical = entry.get("canonical_text") if isinstance(entry.get("canonical_text"), str) else (entry.get("text") or "")
    bp = _jl(os.path.join(level_dir, "audit", "tts_block_progress", f"{seg_id}.json")) if level_dir else None
    lr = _lr_info(entry, canonical)
    take = resolve_adopted_take(entry, bp, hr, None, seg_id=seg_id, lr_adopted=bool(lr and lr["adopted_in_final"]))
    clip: dict = {"clip_id": seg_id, "role": entry.get("role") or (entry.get("asr_judgement") or {}).get("role") or entry.get("role_style_key") or entry.get("_component") or "",
                  "chunk_parent": (entry.get("chunk_tts") or {}).get("parent_id"), "warnings": [], "text_parity": None,
                  "overlap": None, "display": None}
    # --- 採用take / Fallback
    if is_unknown(take):
        clip["adopted_take"] = None
        clip["fallback"] = {"state": "UNKNOWN", "used": None, "adopted_style": None, "from_style": None, "slot": None}
        clip["warnings"].append("RECORD_INCOMPLETE:adopted_take")
    else:
        clip["adopted_take"] = dict(take)
        used = take.get("kind") in FALLBACK_KINDS
        if take.get("status") == "NOT_ADOPTED":
            clip["fallback"] = {"state": "NOT_ADOPTED", "used": None, "adopted_style": None, "from_style": None, "slot": None}
        elif take.get("kind") is None:
            clip["fallback"] = {"state": "UNKNOWN", "used": None, "adopted_style": None, "from_style": None, "slot": take.get("slot")}
            clip["warnings"].append("RECORD_INCOMPLETE:adopted_style")
        else:
            clip["fallback"] = {"state": "USED" if used else "NOT_USED", "used": used, "adopted_style": take.get("style_name") if used else None,
                                "from_style": ("ROLE_STYLE" + (f"({take['from_style_sha'][:8]})" if take.get("from_style_sha") else "")) if used else None,
                                "slot": take.get("slot"), "kind": take.get("kind")}
        if take.get("status") == V_RECORD_MISMATCH:
            clip["warnings"].append("RECORD_MISMATCH")
    # --- 記録間の矛盾(HR採用後のentry直下instruction/style_prefixは採用前の値が残る。attempt直接記録=送信時のinstruction_textを正とする)
    if not is_unknown(take) and take.get("kind") == KIND_NORMAL and take.get("how") in ("human_attempt_file", "attempt_file_sha_match"):
        top = " ".join(str(entry.get(k) or "") for k in ("instruction", "instruction_label")) + " " + str((entry.get("style_prefix") or {}).get("head200") if isinstance(entry.get("style_prefix"), dict) else "")
        if "FALLBACK" in top.upper() or "minimal" in top.lower():
            clip["warnings"].append("STYLE_RECORD_CONFLICT:entry_top_level_says_fallback_but_adopted_attempt_file_is_role_style")
    # --- LR
    if lr is None:
        clip["lr"] = None
        clip["verdict"] = V_RECORD_MISMATCH if (not is_unknown(take) and take.get("status") == V_RECORD_MISMATCH) else V_NO_LR
        return clip
    ops = compute_ops(lr["before"], lr["after"])
    clip["lr"] = {"before": lr["before"], "after": lr["after"], "ops": [{k: v for k, v in o.items() if k in ("kind", "core_before_text", "core_after_text", "before_tokens", "after_tokens")} for o in ops],
                  "reason": lr["reason"], "source": lr["reason_source"], "adopted_in_final": lr["adopted_in_final"],
                  "superseded_by_human": lr["superseded_by_human"], "recorded_spans": lr["recorded_spans"]}
    clip["_ops"] = ops
    if lr["reason"] is None:
        clip["warnings"].append("LR_REASON_UNAVAILABLE")
    if not lr["adopted_in_final"]:
        # 人間承認で音声は原文。表示は原文のまま(overlayなし)。三者(表示=TTS入力=ASR正解=原文)の一致だけ確認する
        disp_cands = _display_candidates(seg_id, entry, level_dir)
        disp = disp_cands[0][1] if disp_cands else canonical
        par = check_text_parity(disp, entry.get("text") or canonical, lr["asr_expected"], [])
        clip["text_parity"] = {"verdict": par["verdict"], "detail": par["detail"]}
        clip["changed_spans"] = []
        clip["overlap"] = check_confirmed_overlap(clip, selection, None, facts)
        clip["verdict"] = V_PASS_SUPERSEDED if par["verdict"].startswith("PASS") else V_PARITY
        return clip
    # --- anchor位置特定(表示候補を優先順に。一意に決まった最初の候補を採用)
    lb_full = _lw(lr["before"])
    chosen, placed, fail = None, [], None
    for src, text in _display_candidates(seg_id, entry, level_dir):
        res_ops = []
        okall = True
        for op in ops:
            loc = locate_op(text, op, lb_full)
            if loc["status"] != "OK":
                okall = False
                fail = {"status": loc["status"], "source": src, "op": f"{op['core_before_text']}->{op['core_after_text']}", **{k: v for k, v in loc.items() if k not in ("status",)}}
                break
            res_ops.append((op, loc))
        if okall:
            chosen, placed = (src, text), res_ops
            break
    if chosen is None:
        clip["display"] = {"source": None, "failure": fail}
        clip["verdict"] = V_AMBIGUOUS if (fail or {}).get("status") == "AMBIGUOUS" else V_UNLOCATABLE
        clip["changed_spans"] = []
        return clip
    src, text = chosen
    overlay = apply_overlay(text, [(op, loc["h"], loc["state"]) for op, loc in placed])
    clip["display"] = {"source": src, "unit_sha_before": _sha(text), "unit_sha_after": _sha(overlay),
                       "state": sorted({loc["state"] for _, loc in placed}), "anchors": [{"k": loc["k"], "anchor": loc["anchor"]} for _, loc in placed]}
    clip["changed_spans"] = [{"before": op["core_before_text"], "after": op["core_after_text"], "kind": op["kind"],
                              "anchor_left": " ".join(lb_full[max(0, op["i1"] - 3):op["i1"]]), "anchor_right": " ".join(lb_full[op["i2"]:op["i2"] + 3]),
                              "display_token_index": loc["h"], "display_state": loc["state"]} for op, loc in placed]
    clip["_display_after"] = overlay
    strict = [op["after_tokens"] for op in ops if op["after_tokens"]]
    tts_in = (entry.get("text") if lr["form"] == "X/Y" else lr["after"]) or lr["after"]   # Z形のentry["text"]は表示形(canonical)。TTS入力=audio_text_after(OPUS M-1)
    par = check_text_parity(overlay, tts_in, lr["asr_expected"], strict)
    clip["text_parity"] = {"verdict": par["verdict"], "detail": par["detail"]}
    # --- 重なり
    fx = dict(facts)
    clip["_level_text_after"] = level_text.replace(text, overlay) if text in level_text else level_text
    clip["overlap"] = check_confirmed_overlap(clip, selection, None, fx)
    ov = clip["overlap"]
    if not par["verdict"].startswith("PASS"):
        clip["verdict"] = V_PARITY
    elif ov["T1"].get("status") == "STOP":
        clip["verdict"] = V_T1
    elif ov["T2"].get("status") == "STOP":
        clip["verdict"] = V_T2
    elif ov["T3"].get("status") == "STOP":
        clip["verdict"] = V_T3
    elif not is_unknown(take) and take.get("status") == V_RECORD_MISMATCH:
        clip["verdict"] = V_RECORD_MISMATCH
    else:
        clip["verdict"] = V_PASS
    clip.pop("_level_text_after", None)
    return clip


def build_lr_ledger(run_dir: str, level: str, *, results_path: str | None = None, level_dir: str | None = None, only_events: bool = True) -> dict:
    """run×levelのLR/Fallback台帳をメモリ上で導出する(純関数・読取専用)。clip毎: role/segment・chunk id/adopted take/lr{before,after,ops,
    changed_spans(anchor),reason,source}/fallback{used,adopted_style,from_style,slot}/text_parity/overlap{T1,T2,T3}/warnings/verdict。
    results_path/level_dirを渡すと標準layoutでない保存物(snapshot等)も読める。"""
    level_dir = level_dir or (os.path.dirname(os.path.dirname(_abs(results_path))) if results_path else os.path.join(run_dir, level))
    results_path = results_path or os.path.join(level_dir, "audit", "tts_generation_results.json")
    results = _jl(_abs(results_path)) or {}
    hr = _hr_records(level_dir)
    sel = _jl(os.path.join(level_dir, "audit", "confirmed_selection.json"))
    entries = list(_iter_entries(results))
    level_text = " ".join(e.get("canonical_text") for _, e, _ in entries if isinstance(e.get("canonical_text"), str))
    parts = _jl(os.path.join(level_dir, "parts.json"))
    if isinstance(parts, dict):
        level_text += " " + " ".join(t for _, t in _string_leaves(parts))
    facts = {"entities": _entities_from_run(level_dir), "level_text": level_text}
    clips, skipped = [], 0
    for sid, e, _ in entries:
        if only_events and not _has_event_evidence(e):
            skipped += 1
            continue
        clips.append(_clip_ledger(sid, e, level_dir=level_dir, hr=hr, selection=sel, facts=facts, level_text=level_text))
    return {"schema": "lr_fallback_ledger_derived_v0", "run_dir": run_dir, "level": level, "results_path": results_path,
            "results_sha256": _file_sha(_abs(results_path)), "clips": clips, "skipped_no_event": skipped}


def public_view(ledger: dict) -> dict:
    """監査出力用に内部キー(`_`始まり)と長文を落としたコピー。"""
    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items() if not k.startswith("_")}
        if isinstance(o, list):
            return [clean(v) for v in o]
        return o
    return clean(ledger)


def write_ledger_audit(ledger: dict, path: str) -> str:
    """監査用出力(Gate/表示はメモリ導出を使い、このファイルを入力にしない)。手編集不可・毎回全置換。"""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(public_view(ledger), f, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    os.replace(tmp, path)
    return path
