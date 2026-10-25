# -*- coding: utf-8 -*-
"""FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_01 (Phase 0): Production移植用 共通コア module の「ドラフト」。
これは研究dir内のdraft(Production file ではない)。実装委任で `er117_chunk_tts_production_01.py`(仮称、新規Production module)へ移す。
内容 = (a) X段落planner (b) Z narrator planner(er114 plan_clip_chunksの移植、決定論) (c) chunk合成(raw/gained) (d) 整合性検査 (e) reuse_key部品。
API 0・TTS 0。numpyのみ(+ er003_b1_p9a_audio の rms/peak/compute_gain_for_target_rms を読取importするのはtests側)。
"""
from __future__ import annotations

import hashlib
import math
import re

import numpy as np

# 方式・版。reuse_key / results / timeline へ記録する。planner規則(閾値・最小語数・優先順・分割数式)を変えたら必ず更新する。
CHUNK_PLANNER_VERSION = "chunk_tts_v1_x_paragraph_z_r1_20261025"
EXTRA_PAUSE_SECONDS = 0.2            # ユーザー正式決定(2026-10-25): chunk間追加ポーズ
SR24 = 24000
Z_SPLIT_THRESHOLD_WORDS = 100        # Z: narrator clipがこれを超えたら分割対象 (= Family C/Z target_words)
Z_TARGET_WORDS = 100                 # k = ceil(語数 / 100)  (B_r1 = 約70語目安)
Z_MIN_CHUNK_WORDS = 25
X_MIN_PARAGRAPHS_FOR_CHUNKING = 2    # 段落が1つしか無いpartは分割しない(従来と同じ1 call)

_SENT_END = re.compile(r"(?<=[.!?])[\"']?\s+")
_PARA_SPLIT = re.compile(r"\n[ \t]*\n+")


class ChunkIntegrityError(RuntimeError):
    """欠落・重複・順序変更・版不整合の検知(fail-closed)。"""


def normalize_for_tts(raw: str) -> str:
    """er013_family_c_production_01.normalize_for_tts と同一(語数定義の一致用)。"""
    t = raw.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("**", "")
    return re.sub(r"\s+", " ", t).strip()


def wc(text: str) -> int:
    return len(normalize_for_tts(text).split())


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ (a) Family X: 段落planner
def plan_x_part(part_text: str, part_name: str) -> dict:
    """本文part(空行区切りの段落)を段落単位chunkへ。段落1つ以下なら chunked=False(従来の1 call)。
    可逆性: '\\n\\n'.join(paras) == part_text.strip() を必ず検証(崩れたらChunkIntegrityError)。"""
    paras = [p.strip() for p in _PARA_SPLIT.split(part_text.strip()) if p.strip()]
    if re.sub(r"\s+", " ", " ".join(paras)) != re.sub(r"\s+", " ", part_text).strip():
        raise ChunkIntegrityError(f"{part_name}: 段落分割が非可逆(空白正規化後の一致で検証。TTS入力整形が改行を空白へ畳むため等価)")
    if len(paras) < X_MIN_PARAGRAPHS_FOR_CHUNKING:
        return {"parent_id": part_name, "family": "X", "chunked": False, "reason": f"paragraphs={len(paras)}<{X_MIN_PARAGRAPHS_FOR_CHUNKING}",
                "planner_version": CHUNK_PLANNER_VERSION, "chunks": []}
    chunks = [{"chunk_id": f"{part_name}_k{i}", "index": i, "text": p, "words": wc(p), "boundary_kind": "paragraph"}
              for i, p in enumerate(paras, start=1)]
    _assert_lossless_x(part_text, chunks)
    return {"parent_id": part_name, "family": "X", "chunked": True, "planner_version": CHUNK_PLANNER_VERSION,
            "extra_pause_seconds": EXTRA_PAUSE_SECONDS, "parent_words": wc(part_text), "chunks": chunks}


def _assert_lossless_x(part_text: str, chunks: list) -> None:
    if " ".join(c["text"] for c in chunks) != " ".join(p.strip() for p in _PARA_SPLIT.split(part_text.strip()) if p.strip()):
        raise ChunkIntegrityError("X chunk結合がpartと一致しない(欠落/重複/順序)")
    if sum(c["words"] for c in chunks) != wc(part_text):
        raise ChunkIntegrityError("X sum(chunk words) != part words")


# ------------------------------------------------------------------ (b) Family Z: narrator clip planner (er114.plan_clip_chunks と同一規則)
def _sentence_units(para: str) -> list:
    t = normalize_for_tts(para)
    units, start = [], 0
    for m in _SENT_END.finditer(t):
        cut = m.end()
        if t[start:cut].count('"') % 2 == 1:
            continue                       # 引用の途中は切らない
        units.append(t[start:cut].strip())
        start = cut
    if t[start:].strip():
        units.append(t[start:].strip())
    return units


def _candidates(paragraph_texts: list) -> list:
    cands, cum = [], 0
    for pi, para in enumerate(paragraph_texts):
        units = _sentence_units(para)
        for ui, u in enumerate(units):
            cum += wc(u)
            last_unit = ui == len(units) - 1
            if pi == len(paragraph_texts) - 1 and last_unit:
                continue
            cands.append({"priority": 0 if last_unit else 1, "cum_words": cum, "after_paragraph": pi, "after_sentence": ui})
    return cands


def plan_z_clip(clip: dict, paragraph_texts: list, level: str = "b1b") -> dict:
    """clip: {id, voice, word_count, text}。Adv(b1b)のnarratorで語数>100のみ分割。それ以外は不変(chunked=False)。
    k=ceil(語数/100)、段落境界>文境界、最小25語、引用途中禁止、cut目標は残語数の等分。"""
    cid, n = clip["id"], clip["word_count"]
    base = {"parent_id": cid, "family": "Z", "planner_version": CHUNK_PLANNER_VERSION, "chunks": [], "chunked": False}
    if level != "b1b":
        return {**base, "reason": "level!=b1b(Std対象外: 6%減速との相互作用が未検証)"}
    if clip.get("voice") != "narrator":
        return {**base, "reason": "not_narrator(Dialogue/話者切替clipは不変)"}
    if n <= Z_SPLIT_THRESHOLD_WORDS:
        return {**base, "reason": f"words={n}<=閾値{Z_SPLIT_THRESHOLD_WORDS}"}
    joined = normalize_for_tts(" ".join(paragraph_texts))
    if joined != normalize_for_tts(clip["text"]):
        raise ChunkIntegrityError(f"{cid}: clip.textと段落テキストが一致しない")
    k = math.ceil(n / Z_TARGET_WORDS)
    cands = _candidates(paragraph_texts)
    cuts, prev, used = [], 0, set()
    for i in range(1, k):
        target = prev + (n - prev) / (k - i + 1)
        ok = [c for c in cands if c["cum_words"] - prev >= Z_MIN_CHUNK_WORDS and n - c["cum_words"] >= Z_MIN_CHUNK_WORDS * (k - i)
              and c["cum_words"] not in used]
        if not ok:
            return {**base, "reason": "no_valid_cut(最小chunk語数を満たす境界なし→不変)"}
        p0 = [c for c in ok if c["priority"] == 0]
        best = min(p0 if p0 else ok, key=lambda c: (abs(c["cum_words"] - target), c["cum_words"]))
        cuts.append(best)
        used.add(best["cum_words"])
        prev = best["cum_words"]
    sentences = [(pi, ui, u) for pi, para in enumerate(paragraph_texts) for ui, u in enumerate(_sentence_units(para))]
    groups, cur, bi = [], [], 0
    bounds = [(c["after_paragraph"], c["after_sentence"]) for c in cuts]
    for pi, ui, u in sentences:
        cur.append((pi, ui, u))
        if bi < len(bounds) and (pi, ui) == bounds[bi]:
            groups.append(cur)
            cur, bi = [], bi + 1
    if cur:
        groups.append(cur)
    chunks = []
    for j, g in enumerate(groups, start=1):
        text = " ".join(u for _, _, u in g)
        chunks.append({"chunk_id": f"{cid}_k{j}", "index": j, "text": text, "words": wc(text), "first_para": g[0][0], "last_para": g[-1][0],
                       "boundary_kind": ("paragraph" if (j == len(groups) or cuts[j - 1]["priority"] == 0) else "sentence")})
    if normalize_for_tts(" ".join(c["text"] for c in chunks)) != joined or sum(c["words"] for c in chunks) != n:
        raise ChunkIntegrityError(f"{cid}: chunk結合/語数合計がclipと一致しない(欠落/重複)")
    return {**base, "chunked": True, "reason": f"narrator words={n}>{Z_SPLIT_THRESHOLD_WORDS}: {len(chunks)} chunks", "parent_words": n,
            "extra_pause_seconds": EXTRA_PAUSE_SECONDS, "chunks": chunks}


# ------------------------------------------------------------------ (c) 合成
def pad_samples() -> int:
    return int(round(EXTRA_PAUSE_SECONDS * SR24))


def compose_raw_parent(chunks_mono24: list) -> np.ndarray:
    """親wav(narration/<parent>.wav)用: 生chunk(gain前)を0.2秒無音で連結。target_rms基準・既存consumer(player行等)用。"""
    seq = []
    for i, c in enumerate(chunks_mono24):
        if i > 0:
            seq.append(np.zeros(pad_samples(), dtype=c.dtype))
        seq.append(c)
    return np.concatenate(seq)


def compose_gained_parent(chunks_mono24: list, target_rms: float, rms_fn, peak_fn, max_peak: float = 0.95):
    """組立用: chunkごとに compute_gain_for_target_rms 同等のscalar gain → 0.2秒無音 → concat(mono24k)。
    戻り値=(mono, gains, post_rms, boundaries[秒])。stereo48k化は呼出側が既存 mono_24k_to_stereo_target で行う。"""
    pieces, gains, post, bounds, pos = [], [], [], [], 0
    for i, c in enumerate(chunks_mono24):
        r = rms_fn(c)
        g = 1.0 if r <= 1e-9 else target_rms / r
        pk = peak_fn(c)
        if pk > 0:
            g = min(g, max_peak / pk)
        c2 = c * g
        if i > 0:
            pieces.append(np.zeros(pad_samples(), dtype=c.dtype))
            pos += pad_samples()
            bounds.append(round(pos / SR24, 4))
        pieces.append(c2)
        pos += len(c2)
        gains.append(round(float(g), 4))
        post.append(round(float(rms_fn(c2)), 5))
    return np.concatenate(pieces), gains, post, bounds


# ------------------------------------------------------------------ (d) 整合性検査
def verify_parent_integrity(plan: dict, parent_text: str, chunk_entries: list, parent_entry: dict | None) -> dict:
    """欠落・重複・順序変更・版不整合を検知(fail-closed)。
    plan=再計算したplan(決定論)。chunk_entries=results上のchunk entry(順不同可。chunk_idで引く)。parent_entry=親aggregate。"""
    if not plan.get("chunked"):
        if parent_entry and parent_entry.get("chunk_tts"):
            raise ChunkIntegrityError("planはchunk無しだが親entryがchunk方式(本文変更後の再計画漏れ)")
        return {"ok": True, "chunked": False}
    want = [c["chunk_id"] for c in plan["chunks"]]
    by_id = {e["segment_id"]: e for e in chunk_entries}
    if sorted(by_id) != sorted(want):
        raise ChunkIntegrityError(f"chunk集合が計画と不一致 missing={sorted(set(want) - set(by_id))} extra={sorted(set(by_id) - set(want))}")
    for c in plan["chunks"]:
        e = by_id[c["chunk_id"]]
        if e.get("canonical_text_sha256") != sha256_text(c["text"]) and e.get("canonical_text") != c["text"]:
            raise ChunkIntegrityError(f"{c['chunk_id']}: canonical_textが計画と不一致(本文変更/取り違え)")
        if (e.get("chunk_tts") or {}).get("planner_version") != CHUNK_PLANNER_VERSION:
            raise ChunkIntegrityError(f"{c['chunk_id']}: planner_version不一致")
    if parent_entry:
        ct = parent_entry.get("chunk_tts") or {}
        if ct.get("chunk_ids") != want:
            raise ChunkIntegrityError(f"親entryのchunk順序が計画と不一致: {ct.get('chunk_ids')} != {want}")
        if ct.get("words") != [c["words"] for c in plan["chunks"]]:
            raise ChunkIntegrityError("親entryのchunk語数列が計画と不一致")
    if normalize_for_tts(" ".join(c["text"] for c in plan["chunks"])) != normalize_for_tts(parent_text):
        raise ChunkIntegrityError("計画chunkの結合が親本文と一致しない")
    if sum(c["words"] for c in plan["chunks"]) != wc(parent_text):
        raise ChunkIntegrityError("sum(chunk words) != parent words")
    return {"ok": True, "chunked": True, "chunks": len(want)}


def verify_composed_duration(chunk_durations_s: list, composed_duration_s: float, tol_s: float = 2.0 / SR24 * 1000) -> None:
    """親wav長 == Σchunk長 + 0.2×(n-1) を検査(重複・欠落の機械検知)。tolは±2ms目安(サンプル丸め)。"""
    want = sum(chunk_durations_s) + EXTRA_PAUSE_SECONDS * (len(chunk_durations_s) - 1)
    if abs(want - composed_duration_s) > tol_s / 1000 + 1e-3:
        raise ChunkIntegrityError(f"合成長不一致 want={want:.4f}s got={composed_duration_s:.4f}s")


# ------------------------------------------------------------------ (e) reuse_key部品
def chunk_reuse_key_fields(parent_id: str, chunk: dict, n_chunks: int) -> dict:
    """既存reuse_key(canonical_text_sha256/role_style_version/voice/style_prefix_sha256/tts_backend)へ『追加』する部品。
    chunkでないclipには付けない(既存keyはバイト同一のまま=従来の再利用を壊さない)。"""
    return {"chunk_tts": {"planner_version": CHUNK_PLANNER_VERSION, "parent_id": parent_id, "index": chunk["index"],
                          "count": n_chunks, "extra_pause_s": EXTRA_PAUSE_SECONDS}}
