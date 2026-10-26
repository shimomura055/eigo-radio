# -*- coding: utf-8 -*-
"""FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02: Family X(Advanced本文3 part、段落単位+0.2秒) / Family Z(Advanced narrator 100語超、
B_r1+0.2秒) の「chunk分割TTS」共通module(APPROVED_FOR_PRODUCTION、ユーザー正式決定2026-10-25)。

方針(正本=docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/WIRING_DESIGN_01.md):
  * chunkは通常のsegment/clip entryと同じ型の1 entryにする(Gate・HR Lock・ASR telemetry・sha stale検知・resumeが共有コード無変更でchunk単位に効く)。
  * 親(part/clip)は『生chunkを0.2秒無音で連結したwav』(PCM16バイト一致)+親集約entryとして残す。組立時のみchunk別gainで再合成する。
  * 本moduleはnumpy+標準libのみ(p9a等の重いmoduleはimportしない)。rms/peak/gain/status判定は呼出側が関数を渡す(式の再実装をしない=I2)。
  * 規則(閾値・最小語数・優先順・分割数式)を変えたら CHUNK_PLANNER_VERSION を必ず更新する(reuse/resume/整合検査が版で旧chunkを拒否する)。
Trialとの対応: X=er113 build_chunk_plan(段落単位) / Z=er114 plan_clip_chunks(B_r1)。planner出力一致はtest fixtureで凍結。

CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01(ユーザー正式承認2026-10-26 APPROVED_FOR_PRODUCTION: Std/Adv双方。Standard除外は認めない):
  * X/Yの分割規則(plan_x_part/plan_x_parts)はレベル非依存(元からレベル条件を持たない)。planner規則・版・Advの出力は不変(golden一致test)。
  * Standardの6%減速との合成方式 = 『chunkごとに既存の減速処理(n3_tts.generate_a2_segment_with_slowdown=TTS→atempo→減速後ASR再検証)をそのまま適用
    → 減速後のchunk wavを0.2秒の無音(減速対象外)で連結』。ポーズは減速の影響を受けず0.2秒のまま。連結後に減速はかけない。
    本moduleは減速自体を実装しない(既存関数を呼出側が適用)。ここでは(a)Std chunk entryの減速証跡を要求する検査 (b)親集約entryの減速集約
    (c)減速証跡の無い旧cacheの再利用拒否 だけを共通化する(X/Yが共用、Zは次委任)。
  * Z向けのレベル条件(plan_z_clip の level != "b1b")は本委任では撤去しない(Z側の減速合成配線=er063は次委任。未配線のまま発火させない)。
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import wave

import numpy as np

CHUNK_PLANNER_VERSION = "chunk_tts_v1_x_paragraph_z_r1_20261025"
EXTRA_PAUSE_SECONDS = 0.2            # ユーザー正式決定(2026-10-25): chunk間追加ポーズ(固定、変更禁止)
SR24 = 24000
Z_SPLIT_THRESHOLD_WORDS = 100        # Z: narrator clipがこれを超えたら分割対象
Z_TARGET_WORDS = 100                 # k = ceil(語数 / 100)
Z_MIN_CHUNK_WORDS = 25
X_MIN_PARAGRAPHS_FOR_CHUNKING = 2    # 段落が1つしか無いpartは分割しない(従来と同じ1 call)
STD_LEVEL = "a2"                     # Standard。chunk entryに減速証跡(slowdown_applied)を要求する
STD_SLOWDOWN_COMPOSITION = "per_chunk_slowdown_then_pad_0.2s"   # 合成方式の記録名(chunk別減速→0.2秒無音挿入→連結。連結後減速は採らない)
# 既存Gate(er003_v1_n3_01_assemble._A2_SLOWDOWN_ORIGINAL_RATIO_MIN/MAX)と同一レンジ。値は複製であり変更しない(testで一致を固定)。
STD_SLOWDOWN_RATIO_MIN = 1.03
STD_SLOWDOWN_RATIO_MAX = 1.09

# chunk ID形(er020.resolve_narrative_role の追加正規表現と同形。test_idsで一致を固定)
X_CHUNK_ID_RE = re.compile(r"(full_story_part([1-3]))_k([1-9][0-9]*)")
Z_CHUNK_ID_RE = re.compile(r"(full_story_part([1-3])_c([0-9]+))_k([1-9][0-9]*)")

_SENT_END = re.compile(r"(?<=[.!?])[\"']?\s+")
_PARA_SPLIT = re.compile(r"\n[ \t]*\n+")

PARENT_STATUS_OK = "OK"
PARENT_STATUS_NOT_ALL_VALIDATED = "CHUNKS_NOT_ALL_VALIDATED"   # 共有Gateの承認照会対象外status(親idへの人間承認で迂回されない)
_OK_GATE_STATUSES = ("VALIDATED", "HUMAN_APPROVED")


class ChunkIntegrityError(RuntimeError):
    """欠落・重複・順序変更・版不整合の検知(fail-closed)。"""


# ------------------------------------------------------------------ 共通ユーティリティ
def normalize_for_tts(raw: str) -> str:
    """er013_family_c_production.normalize_for_tts と同一(語数定義の一致用)。"""
    t = raw.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("**", "")
    return re.sub(r"\s+", " ", t).strip()


def wc(text: str) -> int:
    return len(normalize_for_tts(text).split())


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def parse_chunk_id(segment_id: str):
    """chunk idなら (parent_id, index, family) を返す。chunkでなければ None。"""
    m = Z_CHUNK_ID_RE.fullmatch(segment_id or "")
    if m:
        return m.group(1), int(m.group(4)), "Z"
    m = X_CHUNK_ID_RE.fullmatch(segment_id or "")
    if m:
        return m.group(1), int(m.group(3)), "X"
    return None


def pad_samples() -> int:
    return int(round(EXTRA_PAUSE_SECONDS * SR24))


def chunk_ids(plan: dict) -> list:
    return [c["chunk_id"] for c in plan.get("chunks") or []]


# ------------------------------------------------------------------ (a) Family X: 段落planner
def split_x_paragraphs(part_text: str) -> list:
    return [p.strip() for p in _PARA_SPLIT.split(part_text.strip()) if p.strip()]


def plan_x_part(part_text: str, part_name: str) -> dict:
    """本文part(空行区切りの段落)を段落単位chunkへ。段落1つ以下なら chunked=False(従来の1 call)。"""
    paras = split_x_paragraphs(part_text)
    if re.sub(r"\s+", " ", " ".join(paras)) != re.sub(r"\s+", " ", part_text).strip():
        raise ChunkIntegrityError(f"{part_name}: 段落分割が非可逆(空白正規化後の一致で検証。TTS入力整形が改行を空白へ畳むため等価)")
    base = {"parent_id": part_name, "family": "X", "planner_version": CHUNK_PLANNER_VERSION,
            "parent_text_sha256": sha256_text(part_text)}
    if len(paras) < X_MIN_PARAGRAPHS_FOR_CHUNKING:
        return {**base, "chunked": False, "reason": f"paragraphs={len(paras)}<{X_MIN_PARAGRAPHS_FOR_CHUNKING}", "chunks": []}
    chunks = [{"chunk_id": f"{part_name}_k{i}", "index": i, "text": p, "words": wc(p), "boundary_kind": "paragraph"}
              for i, p in enumerate(paras, start=1)]
    if " ".join(c["text"] for c in chunks) != " ".join(paras) or sum(c["words"] for c in chunks) != wc(part_text):
        raise ChunkIntegrityError(f"{part_name}: X chunk結合/語数合計がpartと一致しない(欠落/重複/順序)")
    return {**base, "chunked": True, "extra_pause_seconds": EXTRA_PAUSE_SECONDS, "parent_words": wc(part_text), "chunks": chunks}


def plan_x_parts(parts: dict) -> dict:
    """parts.json(part1/part2/part3)→ {full_story_partN: plan}。"""
    return {f"full_story_part{n}": plan_x_part(parts[f"part{n}"], f"full_story_part{n}") for n in (1, 2, 3)}


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
    cid = clip["id"]
    n = clip.get("word_count") or wc(clip["text"])
    base = {"parent_id": cid, "family": "Z", "planner_version": CHUNK_PLANNER_VERSION, "chunks": [], "chunked": False,
            "parent_text_sha256": sha256_text(clip["text"])}
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


def paragraph_texts_for_clip(clip: dict, paras: list):
    """clipが由来する段落テキスト列。段落結合がclip.textと一致しない(段落途中でnarratorとdialogueが切り替わる等)場合は
    [clip.text](=文境界のみ)に落とし paragraph_info_lost=True を返す(黙って落とさない)。戻り値=(texts, lost)。"""
    idxs = clip.get("source_paragraph_indices")
    try:
        pt = [paras[i] for i in idxs]
    except (TypeError, IndexError):
        return [clip["text"]], True
    if normalize_for_tts(" ".join(pt)) != normalize_for_tts(clip["text"]):
        return [clip["text"]], True
    return pt, False


def plan_z_level(story_clips: list, paras: list, level: str = "b1b") -> dict:
    """story clips → {clip_id: plan}(全clip。chunked=Falseのclipも含む)。Adv以外は全clip chunked=False。"""
    out = {}
    for c in story_clips:
        texts, lost = paragraph_texts_for_clip(c, paras)
        p = plan_z_clip(c, texts, level)
        p["paragraph_info_lost"] = lost
        out[c["id"]] = p
    return out


# ------------------------------------------------------------------ (c) PCM I/O と親wav合成
def read_pcm16(path: str):
    with wave.open(path, "rb") as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw != 2 or ch != 1 or sr != SR24:
        raise ChunkIntegrityError(f"{path}: 24kHz mono 16bit 以外(ch={ch} sw={sw} sr={sr})")
    return np.frombuffer(raw, dtype=np.int16)


def write_pcm16(path: str, pcm: np.ndarray) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR24)
        w.writeframes(np.asarray(pcm, dtype=np.int16).tobytes())


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def compose_raw_pcm(chunks_pcm: list) -> np.ndarray:
    """生chunk(int16)を0.2秒無音で連結。親wav(narration/<parent>.wav)の中身。gainは掛けない。"""
    seq = []
    for i, c in enumerate(chunks_pcm):
        if i > 0:
            seq.append(np.zeros(pad_samples(), dtype=np.int16))
        seq.append(np.asarray(c, dtype=np.int16))
    return np.concatenate(seq)


def expected_raw_samples(chunk_lengths: list) -> int:
    return int(sum(chunk_lengths) + pad_samples() * max(len(chunk_lengths) - 1, 0))


def verify_composed_samples(chunk_lengths: list, composed_len: int) -> None:
    """合成長 == Σchunk長 + pad×(n−1) を整数サンプル数で厳密に検査(I8。重複・欠落の機械検知)。"""
    want = expected_raw_samples(chunk_lengths)
    if want != int(composed_len):
        raise ChunkIntegrityError(f"合成長不一致(整数サンプル) want={want} got={int(composed_len)}")


def write_raw_parent(parent_path: str, chunk_paths: list) -> dict:
    """ディスク上のchunk wavを生連結して親wavを書く(PCM16のバイト一致。float往復による1LSBのずれを作らない)。"""
    pcms = [read_pcm16(p) for p in chunk_paths]
    raw = compose_raw_pcm(pcms)
    verify_composed_samples([len(p) for p in pcms], len(raw))
    write_pcm16(parent_path, raw)
    return {"sha256": sha256_file(parent_path), "samples": int(len(raw)), "chunk_samples": [int(len(p)) for p in pcms],
            "duration_seconds": round(len(raw) / SR24, 4)}


def verify_raw_parent(parent_path: str, chunk_paths: list) -> dict:
    """親wav == ディスク上のchunk wavの生連結(整数サンプル完全一致)を確認(I8)。組立でtarget_rmsの基準に使う前に必ず呼ぶ。"""
    if not os.path.exists(parent_path):
        raise ChunkIntegrityError(f"親wavがありません: {parent_path}")
    pcms = [read_pcm16(p) for p in chunk_paths]
    want = compose_raw_pcm(pcms)
    got = read_pcm16(parent_path)
    if len(got) != len(want) or not np.array_equal(got, want):
        raise ChunkIntegrityError(f"親wavがchunk wavの生連結と一致しません(欠落/重複/古い親wav): {parent_path}")
    return {"ok": True, "samples": int(len(got))}


def compose_gained_parent(chunks_mono: list, target_rms: float, *, gain_fn, rms_fn, peak_fn) -> tuple:
    """組立用: chunkごとに gain_fn(chunk, target_rms)(=p9a.compute_gain_for_target_rms。式を再実装しない=I2)でscalar gain →
    0.2秒無音 → concat(24k mono)。戻り値=(mono, report)。stereo48k化は呼出側が既存 mono_24k_to_stereo_target で行う。
    report: gains/pre_rms/post_rms/peak_after/peak_capped(RMSがtargetに届かずpeak頭打ちになったchunk)/boundary_offsets_s(各0.2秒無音の開始・終了)。"""
    pieces, rep, pos = [], {"gains": [], "pre_rms": [], "post_rms": [], "peak_after": [], "peak_capped": [], "boundary_offsets_s": [],
                            "chunk_samples": [], "pad_samples": pad_samples()}, 0
    for i, c in enumerate(chunks_mono):
        g = float(gain_fn(c, target_rms))
        c2 = c * g
        if i > 0:
            pieces.append(np.zeros(pad_samples(), dtype=c2.dtype))
            rep["boundary_offsets_s"].append([round(pos / SR24, 4), round((pos + pad_samples()) / SR24, 4)])
            pos += pad_samples()
        pieces.append(c2)
        pos += len(c2)
        r = float(rms_fn(c))
        rep["gains"].append(round(g, 4))
        rep["pre_rms"].append(round(r, 5))
        rep["post_rms"].append(round(float(rms_fn(c2)), 5))
        rep["peak_after"].append(round(float(peak_fn(c2)), 5))
        rep["peak_capped"].append(bool(r > 1e-9 and g < target_rms / r - 1e-9))
        rep["chunk_samples"].append(int(len(c)))
    mono = np.concatenate(pieces)
    verify_composed_samples(rep["chunk_samples"], len(mono))
    rep["total_samples"] = int(len(mono))
    return mono, rep


# ------------------------------------------------------------------ (d) chunk entry meta / 親集約entry
def attach_chunk_meta(entry: dict, parent_id: str, chunk: dict, n_chunks: int, level: str | None = None) -> dict:
    """chunk entryに『どのplanのchunkか』を記録する(整合検査・evidence・resume用)。
    level="a2"(Standard)のときだけ、減速合成方式の記録(level/std_slowdown_composition)を追加する。levelを渡さない(Adv)場合は従来とバイト同一。"""
    entry["chunk_tts"] = {"planner_version": CHUNK_PLANNER_VERSION, "parent_id": parent_id, "index": chunk["index"], "count": n_chunks,
                          "words": chunk["words"], "boundary_kind": chunk["boundary_kind"], "extra_pause_s": EXTRA_PAUSE_SECONDS}
    if level == STD_LEVEL:
        entry["chunk_tts"]["level"] = STD_LEVEL
        entry["chunk_tts"]["std_slowdown_composition"] = STD_SLOWDOWN_COMPOSITION
    return entry


# ------------------------------------------------------------------ (d2) Standard: chunk別6%減速の証跡検査(X/Y共用。Zは次委任)
def std_chunk_slowdown_violations(plan: dict, segments: dict) -> list:
    """Std(a2)でchunk化された親について、planの全chunk entryが『chunk単位で』6%減速済みであることを要求する(共有Gateは
    A2_SLOWDOWN_TARGET_SEGMENTSにchunk idを持たないため、chunk entryの減速欠落を検知できない=ここで補う)。
    違反: entry欠落 / slowdown_applied is not True / 記録された減速前後長の比が[STD_SLOWDOWN_RATIO_MIN, MAX]外。
    減速後ASR再検証の合否は共有Gate(VALIDATED/HUMAN_APPROVED)の責務でありここでは見ない(人間承認済みchunkを減速証跡の有無だけで判定するため)。
    戻り値=[{"segment": chunk_id, "violations": [...]}]。chunk化されていないplanは[]。"""
    out = []
    if not plan.get("chunked"):
        return out
    for cid in chunk_ids(plan):
        e = (segments or {}).get(cid)
        v = []
        if e is None:
            v.append("NO_SEGMENT_RECORD")
        else:
            if e.get("slowdown_applied") is not True:
                v.append("STD_CHUNK_MISSING_MANDATORY_A2_SLOWDOWN")
            else:
                info = e.get("slowdown_info") or {}
                src, dst = info.get("src_duration_seconds"), info.get("dst_duration_seconds")
                if src and dst and not (STD_SLOWDOWN_RATIO_MIN <= dst / src <= STD_SLOWDOWN_RATIO_MAX):
                    v.append(f"STD_CHUNK_SLOWDOWN_RATIO_OUT_OF_RANGE({dst / src:.4f})")
        if v:
            out.append({"segment": cid, "violations": v})
    return out


def std_parent_slowdown_fields(plan: dict, segments: dict) -> dict:
    """Std親集約entryの減速集約(表示/Gate用)。親wav=減速後chunk wavの生連結なので、全chunkが減速済みの場合に限り slowdown_applied=True。
    1つでも欠ければ False(親は共有Gateの _segment_missing_mandatory_a2_slowdown で止まる)。根拠は slowdown_basis に残す。"""
    bad = std_chunk_slowdown_violations(plan, segments)
    return {"slowdown_applied": not bad, "slowdown_basis": "all_chunks_slowdown_applied(parent wav = post-slowdown chunk wavs + 0.2s silence)",
            "std_slowdown_composition": STD_SLOWDOWN_COMPOSITION, "std_chunk_slowdown_violations": [b["segment"] for b in bad]}


def drop_cached_std_chunks_without_slowdown(cached: dict | None, is_chunk_id=None) -> dict | None:
    """Std(a2)の前回resultsのうち、chunk idのentryで slowdown_applied is True でないものは再利用しない(減速証跡のないchunk wavを
    Stdへ流用しない=fail-closed)。chunkでないentryは不変。is_chunk_id: key→bool。既定はX/Z形式(parse_chunk_id)。
    Yはchunk id形式が異なる(y_voice_2_k1等)ため、呼出側(er121)が自分の判定関数を渡す。"""
    if not cached:
        return cached
    is_chunk_id = is_chunk_id or (lambda k: parse_chunk_id(k) is not None)
    segs = cached.get("segments") or {}
    kept = {k: v for k, v in segs.items() if not is_chunk_id(k) or (v or {}).get("slowdown_applied") is True}
    if len(kept) == len(segs):
        return cached
    out = dict(cached)
    out["segments"] = kept
    return out


def chunk_reuse_key_fields(parent_id: str, chunk: dict, n_chunks: int) -> dict:
    """既存reuse_key(canonical_text_sha256/role_style_version/voice/style_prefix_sha256/tts_backend)へ『追加』する部品。
    chunkでないclipには付けない(既存keyはバイト同一のまま=従来の再利用を壊さない)。"""
    return {"chunk_tts": {"planner_version": CHUNK_PLANNER_VERSION, "parent_id": parent_id, "index": chunk["index"],
                          "count": n_chunks, "extra_pause_s": EXTRA_PAUSE_SECONDS}}


def drop_stale_chunk_entries(cached: dict | None) -> dict | None:
    """I1: 前回resultsのうち chunk id のentryで planner_version が現行と異なる(または無い)ものを除いた浅いコピーを返す
    (版を上げた後に旧chunkが再利用されて verify_parent_integrity で手作業STOPになるのを防ぐ=版が違えば再生成)。chunkでないentryは不変。"""
    if not cached:
        return cached
    segs = cached.get("segments") or {}
    kept = {k: v for k, v in segs.items()
            if parse_chunk_id(k) is None or ((v or {}).get("chunk_tts") or {}).get("planner_version") == CHUNK_PLANNER_VERSION}
    if len(kept) == len(segs):
        return cached
    out = dict(cached)
    out["segments"] = kept
    return out


def derive_parent_status(plan: dict, segments: dict, approvals: dict, status_fn) -> dict:
    """M2(a): 親statusは『planのchunk id一覧』から導出する(entryが無いchunkは status_fn(None)=UNVALIDATED。失敗・未生成でも親を常に書ける)。
    status_fn=共有Gateの asm._segment_gate_status(entry, segment_key, approvals)。全chunkがVALIDATED/HUMAN_APPROVEDなら 'OK'、
    それ以外は 'CHUNKS_NOT_ALL_VALIDATED'(共有Gateで必ずブロック。親idへの人間承認で迂回できない status)。"""
    per = {cid: status_fn(segments.get(cid), cid, approvals) for cid in chunk_ids(plan)}
    ok = all(s in _OK_GATE_STATUSES for s in per.values())
    worst = None
    if not ok:
        worst = next((s for s in per.values() if s not in _OK_GATE_STATUSES), None)
        raw = [(segments.get(cid) or {}).get("status") for cid, s in per.items() if s not in _OK_GATE_STATUSES]
        worst = {"gate_status": worst, "chunk_raw_statuses": raw}
    return {"status": PARENT_STATUS_OK if ok else PARENT_STATUS_NOT_ALL_VALIDATED, "per_chunk": per,
            "human_approved_chunks": [cid for cid, s in per.items() if s == "HUMAN_APPROVED"], "worst": worst}


def refresh_parent_status(plan: dict, segments: dict, approvals: dict, status_fn, *, narration_dir: str, parent_text: str,
                          display: dict | None = None) -> dict:
    """親集約entryを(再)構築して segments[parent_id] に書く(冪等)。M2:
      (a) 失敗・未生成でも常に書く(statusはplanのchunk id一覧から導出)
      (b) 全chunk wavが存在すれば親wav(生連結)を再合成しshaを更新(人間承認後に親wavが無い/古いまま、を防ぐ)。一部欠けなら親wavは触らずsha=None
      (d) human_approved_chunks を記録(statusがOKに丸められて人間承認の事実が消えない)
      I7: 表示用の voice/style/canonical_text 等は display(呼出側が渡す)から。gain_reportの親keyには値を書かない(組立側の責務)。
    chunked=False のplanは何もしない(None)。"""
    if not plan.get("chunked"):
        return None
    pid = plan["parent_id"]
    d = derive_parent_status(plan, segments, approvals, status_fn)
    wavs = [f"{narration_dir}/{cid}.wav" for cid in chunk_ids(plan)]
    parent_path = f"{narration_dir}/{pid}.wav"
    sha = dur = None
    raw_info = None
    if all(os.path.exists(p) for p in wavs):
        pcms_len = None
        try:
            ok_existing = os.path.exists(parent_path)
            if ok_existing:
                try:
                    verify_raw_parent(parent_path, wavs)
                except ChunkIntegrityError:
                    ok_existing = False
            if not ok_existing:
                raw_info = write_raw_parent(parent_path, wavs)
            else:
                pcms_len = [len(read_pcm16(p)) for p in wavs]
                raw_info = {"sha256": sha256_file(parent_path), "samples": expected_raw_samples(pcms_len), "chunk_samples": pcms_len,
                            "duration_seconds": round(expected_raw_samples(pcms_len) / SR24, 4)}
            sha, dur = raw_info["sha256"], raw_info["duration_seconds"]
        except ChunkIntegrityError:
            sha = dur = None
    entry = {
        "segment_id": pid, "status": d["status"], "canonical_text": parent_text, "path": parent_path.replace("\\", "/"),
        "sha256": sha, "duration_seconds": dur,
        "chunk_tts": {
            "planner_version": CHUNK_PLANNER_VERSION, "family": plan.get("family"), "chunk_ids": chunk_ids(plan),
            "words": [c["words"] for c in plan["chunks"]], "boundary_kinds": [c["boundary_kind"] for c in plan["chunks"]],
            "extra_pause_seconds": EXTRA_PAUSE_SECONDS, "raw_parent_sha256": sha, "raw_parent_samples": (raw_info or {}).get("samples"),
            "chunk_gate_statuses": d["per_chunk"], "human_approved_chunks": d["human_approved_chunks"],
            "deviation_chunks": [cid for cid in chunk_ids(plan) if (segments.get(cid) or {}).get("audio_text_deviation")],
            "not_validated_detail": d["worst"], "paragraph_info_lost": plan.get("paragraph_info_lost"),
        },
    }
    entry.update(display or {})
    segments[pid] = entry
    return entry


# ------------------------------------------------------------------ (e) 整合性検査
def verify_parent_integrity(plan: dict, parent_text: str, chunk_entries: list, parent_entry: dict | None) -> dict:
    """欠落・重複・順序変更・版不整合を検知(fail-closed)。plan=再計算したplan(決定論)。
    chunk_entries={chunk_id: entry}(またはsegment_idを持つentryのlist。順不同可)。parent_entry=親集約entry。音声を読む前に実行すること。"""
    if not plan.get("chunked"):
        if parent_entry and parent_entry.get("chunk_tts"):
            raise ChunkIntegrityError("planはchunk無しだが親entryがchunk方式(本文変更後の再計画漏れ)")
        return {"ok": True, "chunked": False}
    want = chunk_ids(plan)
    by_id = dict(chunk_entries) if isinstance(chunk_entries, dict) else {e["segment_id"]: e for e in chunk_entries}
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
        if ct.get("planner_version") != CHUNK_PLANNER_VERSION:
            raise ChunkIntegrityError("親entryのplanner_version不一致")
    if normalize_for_tts(" ".join(c["text"] for c in plan["chunks"])) != normalize_for_tts(parent_text):
        raise ChunkIntegrityError("計画chunkの結合が親本文と一致しない")
    if sum(c["words"] for c in plan["chunks"]) != wc(parent_text):
        raise ChunkIntegrityError("sum(chunk words) != parent words")
    return {"ok": True, "chunked": True, "chunks": len(want)}


def reconcile_saved_plan(path: str, plans: dict) -> dict:
    """resume時の再計画禁止: planは(本文・段落構造・版)の純関数。保存済みplan(audit/chunk_plan_*.json)と、同一本文・同一版で
    chunk構成が食い違えばSTOP(黙って別分割にしない)。本文が変わった親・版が違う親は再計画として許す。最後に現行planを保存。"""
    saved = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                saved = (json.load(f) or {}).get("plans") or {}
        except Exception:
            saved = {}
    for pid, p in plans.items():
        s = saved.get(pid)
        if not s or s.get("planner_version") != p.get("planner_version") or s.get("parent_text_sha256") != p.get("parent_text_sha256"):
            continue
        if [(c["chunk_id"], c["text"]) for c in s.get("chunks") or []] != [(c["chunk_id"], c["text"]) for c in p.get("chunks") or []]:
            raise ChunkIntegrityError(f"{pid}: 同一本文・同一planner_versionで保存済みplanと分割が一致しません(resume時の再計画禁止)")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"planner_version": CHUNK_PLANNER_VERSION, "plans": plans}, f, ensure_ascii=False, indent=2)
    return {"path": path, "parents": sorted(plans)}


def evidence_record(plan: dict, segments: dict, compose_report: dict | None = None) -> dict:
    """C7: 親ごとのevidence(分割位置と種別・chunk数・0.2秒offset・gain/RMS/peak・attempts/fallback/Local Rewrite・ASR判定)。"""
    rows = []
    for c in plan.get("chunks") or []:
        e = segments.get(c["chunk_id"]) or {}
        style = e.get("style") or {}
        rows.append({
            "chunk_id": c["chunk_id"], "index": c["index"], "words": c["words"], "boundary_kind": c["boundary_kind"],
            "status": e.get("status"), "voice": e.get("voice"), "model_ids_measured": e.get("model_ids_measured"),
            "style_prefix_sha256": style.get("style_prefix_sha256"), "instruction_type": e.get("instruction_type") or style.get("instruction_type"),
            "attempt_count": len(e.get("attempts") or []), "local_rewrite_recovery": e.get("local_rewrite_recovery"),
            "audio_text_deviation": bool(e.get("audio_text_deviation")), "asr_judgement": e.get("asr_judgement"),
            "reused": bool(e.get("reused_from_previous_run")), "cost_jpy": e.get("cost_jpy"),
        })
        if "slowdown_applied" in e:      # Std(a2)のchunkのみ(Advのchunkには無いkey=Advのevidence形式は不変)
            si = e.get("slowdown_info") or {}
            rows[-1].update({"slowdown_applied": e.get("slowdown_applied"), "slowdown_pct_actual": si.get("slowdown_pct_actual"),
                             "slowdown_src_duration_s": si.get("src_duration_seconds"), "slowdown_dst_duration_s": si.get("dst_duration_seconds"),
                             "post_slowdown_classification": e.get("post_slowdown_final_classification") or e.get("post_slowdown_classification"),
                             "tts_generations_used": e.get("tts_generations_used")})
    return {"parent_id": plan.get("parent_id"), "family": plan.get("family"), "planner_version": CHUNK_PLANNER_VERSION,
            "chunk_count": len(rows), "extra_pause_seconds": EXTRA_PAUSE_SECONDS, "chunks": rows, "assembly": compose_report}


# ------------------------------------------------------------------ (f) 旧(非chunk)結果との互換
def is_legacy_unchunked(plan: dict, segments: dict) -> bool:
    """本module導入前に生成された結果か: 親entryが存在し(chunk_ttsなし)、かつ同親のchunk idのentryが1件も無い。
    gate/assemble/pagesの再実行(既存run・公開済みepisodeの再組立)を従来経路のままにする判定に使う。TTS(生成)stageでは使わない
    (生成は常にplanどおりchunk化する)。chunk entryが1件でもあれば新方式とみなし、欠落はfail-closed(Gate/整合検査が止める)。"""
    pid = plan.get("parent_id")
    parent = (segments or {}).get(pid)
    if not parent or parent.get("chunk_tts") is not None:
        return False
    prefix = f"{pid}_k"
    return not any(k.startswith(prefix) and parse_chunk_id(k) for k in (segments or {}))


def effective_plan(plan: dict, segments: dict) -> dict:
    """legacy結果なら chunked=False のplan(従来経路)に差し替える。それ以外は元のplan。"""
    if plan.get("chunked") and is_legacy_unchunked(plan, segments):
        return {**plan, "chunked": False, "chunks": [], "legacy_unchunked": True,
                "reason": "legacy(本方式導入前に生成された親entry。chunk entryなし)→従来経路"}
    return plan
