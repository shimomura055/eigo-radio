# -*- coding: utf-8 -*-
"""FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 (DEV/Trial専用、Family X『英国の電車マナー』Advanced=b1bのみ)。

目的: 本文1・2・3を「各1 TTS Chunk」(A=承認済みProduction完成音声)ではなく「段落ごとに別Chunk」(B)で生成し、
      音質・発話速度・接続/音量・QCDをA/B比較する。Production変更なし・Production出力dirへの書込みなし。

設計正本: docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/DESIGN_01.md
Phase 1(本ファイルの無料部分): 段落分割・A側計測・結合/音量(既存方式の再利用のみ)・B全体の組立・費用/ガード・ページ生成。
Phase 2(有料、Opus条件Aレビュー後のFable Goまで開始禁止): `gen`サブコマンド。`PHASE2_GO.json`が無ければ起動拒否。

新しい音声加工は導入しない。再利用するもの(全て既存Production関数をimportして呼ぶ):
  - er003_b1_p3u_audio.trim_english_keyword_silence (各TTS生成関数の内部。news_tail_fix経由で自動適用)
  - er003_b1_p9a_audio.compute_gain_for_target_rms(max_peak=0.95) / mono_24k_to_stereo_target / silence_stereo
  - er019 runner apply_family_x_b1_gain / build_family_x_b1_timeline / er003_v1_n3_01_assemble.assemble_with_timeline
    / apply_headroom_safety_valve  (B全体=A全体の同一組立のうち本文3 segmentだけB版へ差替え)
  - er057 measure_wpm_01 の語数/ポーズ計測定義(転記。importするとmain()が走るため。FAMILY-X-COFFEE-ADVANCED-FULLSTORY-WPM-MEASUREMENT-01)
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

OUT_DIR = "er113_output/fx_paragraph_chunk_trial_01"
# A側(承認済みProduction完成音声)。読み取り専用。このdir配下へは一切書かない。
A_THEME_DIR = "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02"
A_LEVEL_DIR = f"{A_THEME_DIR}/b1b"  # Advanced = b1b (Standard = a2)。ユーザー公開ページのAdvanced(281秒)=b1b(280.84秒)で確認済み
PARTS = (1, 2, 3)
SR24 = 24000
SR48 = 48000
PHASE2_GO_FILE = f"{OUT_DIR}/PHASE2_GO.json"
MANAGED_ID = "FX-PARAGRAPH-CHUNK-TTS-TRIAL-01"

# ---- Production書込み先のうち、本Trialの生成連鎖(news_tail_fix→ASR cascade→review lock)が触りうるもの ----
# Phase 2ではこれらをDEV dirへ向ける(プロセス内override、Productionファイルは編集しない)。(module, 属性名)
SINK_CONSTANTS = (
    ("er011_human_review_lock_01", "ATTEMPT_HISTORY_PATH"),
    ("er006_secondary_asr_01", "HUMAN_REVIEW_LOG_PATH"),
    ("er021_en_asr_semantic_equivalence_production_01", "TELEMETRY_LOG_PATH"),
    ("er025_entity_pronunciation_resolver_core_01", "TELEMETRY_PATH"),
)
# before/afterのsha256で不変を確認するProduction store(変化したらSTOPして報告)。
PROTECTED_STORES = (
    "er011_output/attempt_history.jsonl",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
    "er006_output/master_audio_store_01/manifest.json",
    "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
    "er006_output/pronunciation_ledger_01/ledger.json",
    "er005_output/cost_baseline_01/cost_summary.json",
)
PROTECTED_TREES = (A_THEME_DIR, "user_test/uk_train_speaker_playback_e2e_02")


# ============================================================
# 共通ユーティリティ
# ============================================================
def load_json(path: str):
    with open(os.path.join(ROOT, path) if not os.path.isabs(path) else path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    ap = os.path.join(ROOT, path) if not os.path.isabs(path) else path
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    with open(ap, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def sha256_file(path: str) -> str | None:
    ap = os.path.join(ROOT, path) if not os.path.isabs(path) else path
    if not os.path.exists(ap):
        return None
    h = hashlib.sha256()
    with open(ap, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def tree_digest(path: str) -> str:
    """dir配下の全ファイル(相対path+sha256)のdigest。A側/公開ページ不変の確認用。"""
    ap = os.path.join(ROOT, path)
    h = hashlib.sha256()
    for dp, dn, fns in os.walk(ap):
        dn.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            h.update(os.path.relpath(p, ap).replace("\\", "/").encode())
            h.update((sha256_file(p) or "").encode())
    return h.hexdigest()


def snapshot_protected() -> dict:
    snap = {p: sha256_file(p) for p in PROTECTED_STORES}
    snap.update({f"tree:{t}": tree_digest(t) for t in PROTECTED_TREES})
    return snap


def diff_snapshots(before: dict, after: dict) -> list:
    return [k for k in before if before[k] != after.get(k)]


class _MW:
    """既存計測 er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py の
    count_primary / frame_rms_db / find_pauses と同一定義(FRAME 20ms・HOP 10ms・-40dB)。
    そのscriptはimportするとmain()が走りファイルを書く(末尾の無条件main()呼出)ため、importせず定義を転記し、
    test_measure_defs_match_original_source で転記元ソースとの定数一致を機械確認する。"""
    FRAME_MS, HOP_MS, THRESH_DB = 20, 10, -40.0

    @staticmethod
    def count_primary(text):
        return sum(1 for tk in text.split() if re.search(r"[A-Za-z0-9]", tk))

    def frame_rms_db(self, x, sr):
        f, h = int(sr * self.FRAME_MS / 1000), int(sr * self.HOP_MS / 1000)
        n = max(0, (len(x) - f) // h + 1)
        if n == 0:
            return np.zeros(0)
        idx = np.arange(n)[:, None] * h + np.arange(f)[None, :]
        r = np.sqrt(np.mean(x[idx] ** 2, axis=1))
        return 20 * np.log10(np.maximum(r, 1e-10))

    def find_pauses(self, db, min_ms, dur):
        sil = db < self.THRESH_DB
        res, i, n = [], 0, len(sil)
        while i < n:
            if sil[i]:
                j = i
                while j < n and sil[j]:
                    j += 1
                s, e = i * self.HOP_MS / 1000, min(dur, (j - 1) * self.HOP_MS / 1000 + self.FRAME_MS / 1000)
                if (e - s) * 1000 >= min_ms:
                    res.append({"start": round(s, 3), "end": round(e, 3), "dur": round(e - s, 3),
                                "edge": "head" if i == 0 else ("tail" if j >= n else "mid")})
                i = j
            else:
                i += 1
        return res


def _mw():
    return _MW()


# ============================================================
# 段落分割(Phase 1で実装・unit test済み。TTSは呼ばない)
# ============================================================
_PARA_SPLIT = re.compile(r"\n[ \t]*\n+")


def split_paragraphs(part_text: str) -> list:
    """本文partを空行区切りの段落へ分割する。根拠: parts.json は paragraph_count=10 / boundary_i=4 / boundary_j=7 で
    part1=4段落・part2=3段落・part3=3段落に『段落境界で決定論的に3分割』済みで、各partの段落間は空行(\\n\\n)。
    分割後に'\\n\\n'で再結合して元textと一致すること(情報の欠落・追加なし)を呼出側で検証する。"""
    paras = [p.strip() for p in _PARA_SPLIT.split(part_text.strip()) if p.strip()]
    return paras


def verify_split_lossless(part_text: str, paras: list) -> bool:
    return "\n\n".join(paras) == part_text.strip()


def build_chunk_plan(parts_json: dict) -> list:
    """全chunk計画: [{chunk_id, part, index, text, words}]。chunk_id例 p1_1(part1の段落1)。"""
    mw = _mw()
    plan = []
    for n in PARTS:
        text = parts_json[f"part{n}"]
        paras = split_paragraphs(text)
        if not verify_split_lossless(text, paras):
            raise RuntimeError(f"part{n}: 段落分割が非可逆")
        for i, ptxt in enumerate(paras, start=1):
            plan.append({"chunk_id": f"p{n}_{i}", "part": n, "index": i, "text": ptxt, "words": mw.count_primary(ptxt)})
    total = sum(1 for _ in plan)
    if total != parts_json.get("paragraph_count"):
        raise RuntimeError(f"chunk数{total} != paragraph_count {parts_json.get('paragraph_count')}")
    return plan


# ============================================================
# 計測(A/B共通。ローカル処理のみ、API 0)
# ============================================================
def measure_wav(mono: np.ndarray, sr: int, words: int) -> dict:
    """発話速度とポーズの分離計測。既存mwの-40dB/20ms frame計測を再利用。
    total_wpm       = words / 全長(両端margin・段落間ポーズ込み。聴感上の『見かけの速度』)
    articulation_wpm_500 = words / (全長 - ≥500msの無音合計)  (既存speech_wpm500と同定義。実発話速度に近い)
    articulation_wpm_300 = 同(≥300ms)
    mid_pause_*: 両端(head/tail)を除く≥Nms無音の個数/合計秒(段落間・文間ポーズの増減を見る)"""
    mw = _mw()
    dur = len(mono) / sr
    db = mw.frame_rms_db(mono.astype(np.float64), sr)
    out = {"duration_s": round(dur, 3), "words": words, "total_wpm": round(words / dur * 60, 2)}
    for thr in (300, 500):
        ps = mw.find_pauses(db, thr, dur)
        sp = dur - sum(q["dur"] for q in ps)
        mid = [q for q in ps if q["edge"] == "mid"]
        out[f"articulation_wpm_{thr}"] = round(words / sp * 60, 2) if sp > 0 else None
        out[f"pause_{thr}"] = {"n_all": len(ps), "sum_all_s": round(sum(q["dur"] for q in ps), 3),
                               "n_mid": len(mid), "sum_mid_s": round(sum(q["dur"] for q in mid), 3),
                               "mean_mid_s": round(sum(q["dur"] for q in mid) / len(mid), 3) if mid else 0.0,
                               "max_mid_s": round(max((q["dur"] for q in mid), default=0.0), 3)}
    out["pauses_300_detail"] = mw.find_pauses(db, 300, dur)
    return out


def measure_a_side() -> dict:
    """A(承認済みAdvanced本文3 segment)のWPM・ポーズを実測する(ローカル、API 0)。"""
    import soundfile as sf
    parts = load_json(f"{A_LEVEL_DIR}/parts.json")
    mw = _mw()
    res = {"source": A_LEVEL_DIR, "parts": {}}
    tot_w = tot_d = tot_sp5 = 0.0
    for n in PARTS:
        x, sr = sf.read(os.path.join(ROOT, f"{A_LEVEL_DIR}/narration/full_story_part{n}.wav"), dtype="float64")
        x = x if x.ndim == 1 else x[:, 0]
        w = mw.count_primary(parts[f"part{n}"])
        m = measure_wav(x, sr, w)
        res["parts"][f"part{n}"] = m
        tot_w += w
        tot_d += m["duration_s"]
        tot_sp5 += w / m["articulation_wpm_500"] * 60
    res["total"] = {"words": int(tot_w), "duration_s": round(tot_d, 3), "total_wpm": round(tot_w / tot_d * 60, 2),
                    "articulation_wpm_500": round(tot_w / tot_sp5 * 60, 2)}
    return res



# ============================================================
# A側の『段落境界で実際にどれだけ間があるか』(ローカルfaster-whisper、API 0、Production store非接触)
# ============================================================
def _norm_tok(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def measure_a_boundary_gaps(model_name: str = "small") -> dict:
    """Aの本文partを単語タイムスタンプ付きASRにかけ、(1)段落境界 (2)段落内の文境界(. ? ! の直後)で
    『直前語endから次語startまで』のgapを測る。A(1 TTS call)がTTS内部で作った段落間/文間の自然な間を知り、
    Bの段落間(trim marginの残置分)と比較する基準にする。語対応はdifflibでASR語列↔台本語列を整列。"""
    import difflib
    from faster_whisper import WhisperModel
    parts = load_json(f"{A_LEVEL_DIR}/parts.json")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    out = {"model": f"faster-whisper-{model_name}", "parts": {}}
    for n in PARTS:
        text = parts[f"part{n}"]
        paras = split_paragraphs(text)
        ref_tokens, kind = [], []   # kind[i]: 次語との境界種別 'para'|'sentence'|None
        for pi, para in enumerate(paras):
            toks = para.split()
            for ti, tk in enumerate(toks):
                ref_tokens.append(_norm_tok(tk))
                last = ti == len(toks) - 1
                if last and pi < len(paras) - 1:
                    kind.append("para")
                elif re.search(r"[.?!][\"')”]*$", tk) and not last:
                    kind.append("sentence")
                else:
                    kind.append(None)
        segs, _ = model.transcribe(os.path.join(ROOT, f"{A_LEVEL_DIR}/narration/full_story_part{n}.wav"), language="en",
                                   word_timestamps=True, beam_size=5, vad_filter=False, condition_on_previous_text=False)
        words = [(_norm_tok(w.word), w.start, w.end) for sg in segs for w in sg.words if _norm_tok(w.word)]
        a_tok = [w[0] for w in words]
        sm = difflib.SequenceMatcher(a=ref_tokens, b=a_tok, autojunk=False)
        ref2asr = {}
        for blk in sm.get_matching_blocks():
            for k in range(blk.size):
                ref2asr[blk.a + k] = blk.b + k
        gaps = {"para": [], "sentence": []}
        for i, kd in enumerate(kind):
            if kd and i in ref2asr and (i + 1) in ref2asr and ref2asr[i + 1] == ref2asr[i] + 1:
                gaps[kd].append(round(words[ref2asr[i + 1]][1] - words[ref2asr[i]][2], 3))
        out["parts"][f"part{n}"] = {"matched_ref_tokens": len(ref2asr), "ref_tokens": len(ref_tokens), **gaps}
    allp = [g for v in out["parts"].values() for g in v["para"]]
    alls = [g for v in out["parts"].values() for g in v["sentence"]]
    out["summary"] = {"para_n": len(allp), "para_mean_s": round(float(np.mean(allp)), 3) if allp else None,
                      "sentence_n": len(alls), "sentence_mean_s": round(float(np.mean(alls)), 3) if alls else None}
    return out


# ============================================================
# 接続・音量: 既存方式の再利用のみ
# ============================================================
def normalize_chunk_to_target(mono: np.ndarray, target_rms: float) -> tuple:
    """承認済み方式(Family A/X共通): scalar RMS正規化 compute_gain_for_target_rms(max_peak=0.95)。
    適用単位は『独立にTTS生成された音声1本』(既存仕様は全ての独立TTS出力[comment/preview/本文partなど]に対し同一target_rmsへ
    個別適用)。Bでは独立TTS出力=段落chunkなので段落chunkごとに適用する。EQ/コンプ/クロスフェードは導入しない。"""
    import er003_b1_p9a_audio as p9a
    g = p9a.compute_gain_for_target_rms(mono, target_rms)
    return mono * g, float(g)


def join_chunks(chunks_mono24: list, target_rms: float, pause_seconds: float = 0.0, per_chunk_gain: bool = True) -> dict:
    """段落chunk(各: 24kHz mono、TTS生成関数内部でsilence trim済み[前後~0.24-0.35s残置])を結合して1 partにする。
    pause_seconds=0.5 が本命B(承認済みFamily C/Z story clip接続 er013_family_c_production_runner_01.py:670 の narrator→narrator gap)。
    0.0 は参考B0(追加無音なし=各chunkのtrim margin残置分のみ。見かけの減速の切り分け用、TTS追加費用0)。
    per_chunk_gain=False は診断用(結合後に1つのgainを掛ける=segment単位適用の場合の音量差を比較するため)。
    crossfade・重ね合わせはしない(既存のassemble_with_timelineもnp.concatenateのみ)。"""
    import er003_b1_p9a_audio as p9a
    pieces, gains, pre_rms, post_rms = [], [], [], []
    for c in chunks_mono24:
        pre_rms.append(p9a.rms(c))
        if per_chunk_gain:
            c2, g = normalize_chunk_to_target(c, target_rms)
        else:
            c2, g = c, 1.0
        gains.append(round(g, 4))
        post_rms.append(p9a.rms(c2))
        pieces.append(c2)
    seq = []
    for i, c in enumerate(pieces):
        if i > 0 and pause_seconds > 0:
            seq.append(np.zeros(int(round(pause_seconds * SR24)), dtype=c.dtype))
        seq.append(c)
    joined = np.concatenate(seq) if seq else np.zeros(0)
    if not per_chunk_gain:
        g = p9a.compute_gain_for_target_rms(joined, target_rms)
        joined = joined * g
        gains = [round(float(g), 4)]
        post_rms = [p9a.rms(joined)]
    return {"mono24": joined, "gains": gains, "rms_before": [round(float(x), 5) for x in pre_rms],
            "rms_after": [round(float(x), 5) for x in post_rms], "pause_seconds": pause_seconds}


def boundary_jump_db(chunks_mono24: list, window_s: float = 1.0) -> list:
    """隣接chunk境界の音量差(dB): 前chunk末尾の発話最後window_sのRMS vs 次chunk先頭の発話最初window_sのRMS。
    発話区間はmwの-40dB frame基準ではなく、既存find_speech_bounds(trim_english_keyword_silenceと同一)を使う。"""
    import er003_b1_p3u_audio as p3u
    out = []
    w = int(window_s * SR24)

    def _rms(a):
        return float(np.sqrt(np.mean(a.astype(np.float64) ** 2))) if len(a) else 0.0
    for a, b in zip(chunks_mono24[:-1], chunks_mono24[1:]):
        ba, bb = p3u.find_speech_bounds(a, SR24), p3u.find_speech_bounds(b, SR24)
        ra = _rms(a[max(0, ba[1] - w):ba[1]]) if ba else 0.0
        rb = _rms(b[bb[0]:bb[0] + w]) if bb else 0.0
        out.append(round(float(20 * np.log10(max(rb, 1e-10) / max(ra, 1e-10))), 2))
    return out


# ============================================================
# B全体 = A全体と同一の組立のうち本文3 segmentだけB版へ差替え(既存runner関数の再利用)
# ============================================================
def rebuild_full_episode(b_part_stereo: dict | None) -> dict:
    """b_part_stereo: {1: stereo48k, 2:..., 3:...} or None(None=A自身を再構築。A完成wavとのbit一致検証用)。
    A全体の再構築に使うgain targetはAの値(target_rms=(preview+part1)/2、A側のpart1から算出)を使う=B差替え後も
    他segmentのgainが変わらない。"""
    import er019_family_x_audio_production_runner_01 as runner
    src_dir = load_json(f"{A_THEME_DIR}/entry_point.json")["source_dir"]  # 記事本文の正規ソース(Key Phrase source Gateの入力)
    sources = runner.load_family_x_b1_sources(A_THEME_DIR, source_dir=src_dir)  # 読み取りのみ(Gate検証含む)
    gained = runner.apply_family_x_b1_gain(sources)
    if b_part_stereo:
        for n, st in b_part_stereo.items():
            gained["b1_segments"][f"full_story_part{n}"] = st
    seq = runner.build_family_x_b1_timeline(gained)
    import er003_v1_n3_01_assemble as asm
    res = asm.assemble_with_timeline(seq)
    hr = asm.apply_headroom_safety_valve(res["assembled"], seq)
    return {"assembled": hr["assembled"], "timeline": res["timeline"], "headroom": hr["report"],
            "gain_report": gained["gain_report"]}


def a_target_rms() -> float:
    return float(load_json(f"{A_LEVEL_DIR}/audit/gain_report.json")["target_rms"])



# ============================================================
# B成果物の組立・計測・ページ(Phase 2生成後に実行。chunk wavが揃っていればAPI 0)
# ============================================================
def _read_mono(path: str):
    import soundfile as sf
    x, sr = sf.read(os.path.join(ROOT, path), dtype="float64")
    return (x if x.ndim == 1 else x[:, 0]), sr


def _write_mp3(stereo48: np.ndarray, out_path: str, br: str = "96k") -> None:
    import imageio_ffmpeg
    import soundfile as sf
    ap = os.path.join(ROOT, out_path)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    tmp = ap + ".tmp.wav"
    sf.write(tmp, stereo48.astype("float32"), SR48)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, ap], check=True)
    os.remove(tmp)


def compute_b_artifacts(chunk_wav_dir_fmt: str, out_sub: str, pause_seconds: float = 0.5) -> dict:
    """chunk wav(<chunk_wav_dir_fmt>.format(chunk_id=..., part=...))から B の本文part・本文全体・Advanced通しを組み立て、計測する。
    gainの基準はA側 gain_report の target_rms(他segmentのgainは不変)。"""
    import er003_b1_p9a_audio as p9a
    parts = load_json(f"{A_LEVEL_DIR}/parts.json")
    plan = build_chunk_plan(parts)
    target = a_target_rms()
    res = {"target_rms": target, "pause_seconds": pause_seconds, "parts": {}, "chunks": {}}
    b_stereo, b_mono_final = {}, {}
    for n in PARTS:
        chs = [c for c in plan if c["part"] == n]
        monos = []
        for c in chs:
            x, sr = _read_mono(chunk_wav_dir_fmt.format(chunk_id=c["chunk_id"], part=n))
            assert sr == SR24
            monos.append(x)
            res["chunks"][c["chunk_id"]] = {"duration_s": round(len(x) / sr, 3), **measure_wav(x, sr, c["words"])}
        j = join_chunks(monos, target, pause_seconds, per_chunk_gain=True)
        jseg = join_chunks(monos, target, pause_seconds, per_chunk_gain=False)  # 診断: segment単位1gainの場合
        b_mono_final[n] = j["mono24"]
        b_stereo[n] = p9a.mono_24k_to_stereo_target(j["mono24"])
        words = sum(c["words"] for c in chs)
        res["parts"][f"part{n}"] = {
            "n_chunks": len(chs), "gains_per_chunk": j["gains"], "rms_before": j["rms_before"], "rms_after": j["rms_after"],
            "boundary_jump_db_after_gain": boundary_jump_db([m * g for m, g in zip(monos, j["gains"])]),
            "boundary_jump_db_if_segment_gain": boundary_jump_db(monos),
            "segment_gain_alt": {"gain": jseg["gains"][0], "chunk_rms_after": [round(float(np.sqrt(np.mean((m * jseg['gains'][0]) ** 2))), 5) for m in monos]},
            "measure": measure_wav(j["mono24"], SR24, words)}
    # 本文全体(part1+1.0s+part2+1.0s+part3。A/Bとも同一の接続)
    gap = p9a.silence_stereo(1.0)
    body_b = np.concatenate([b_stereo[1], gap, b_stereo[2], gap, b_stereo[3]])
    full_b = rebuild_full_episode(b_stereo)
    os.makedirs(os.path.join(ROOT, out_sub), exist_ok=True)
    res["full_episode_b"] = {"duration_s": round(len(full_b["assembled"]) / SR48, 2), "headroom": full_b["headroom"]}
    res["_stereo"] = {"parts": b_stereo, "body": body_b, "full": full_b["assembled"], "timeline": full_b["timeline"]}
    return res


def a_artifacts() -> dict:
    """A(承認済み)側の本文part/本文全体/通しを、Bと同じ組立経路(rebuild_full_episode(None)=完成wavとbit近似一致を検証済み)で作る。"""
    import er003_b1_p9a_audio as p9a
    full_a = rebuild_full_episode(None)
    tl = {e["part"]: e for e in full_a["timeline"]}
    def sl(label):
        e = tl[label]
        return full_a["assembled"][int(round(e["start_seconds"] * SR48)):int(round((e["start_seconds"] + e["duration_seconds"]) * SR48))]
    parts = {1: sl("Full Story Part 1 (Aoede)"), 2: sl("Full Story Part 2 (Aoede)"), 3: sl("Full Story Part 3 (Aoede)")}
    gap = p9a.silence_stereo(1.0)
    return {"parts": parts, "body": np.concatenate([parts[1], gap, parts[2], gap, parts[3]]), "full": full_a["assembled"]}



PAGE_DIR = "user_test/fx_paragraph_chunk_trial_01"
_PAGE_CSS = ("body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin:.5em 0 1.5em}"
             "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:300px}audio{width:100%}.sec{color:#666;font-size:.85em}"
             ".script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}"
             ".note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}.na{color:#a00}")


def build_page(a_art: dict, b_art: dict | None, report: dict | None, b0_art: dict | None = None, out_dir: str = PAGE_DIR) -> str:
    """A/B試聴ページ(既存Family X試聴ページのCSS・audio table構造を再利用)。b_art=None なら B欄は『Phase 2で生成』表示のテンプレート。
    B  = 段落chunk + 承認済みFamily C/Z story clip接続(chunkごとRMS gain + narrator→narrator 0.5秒 gap)
    B0 = 同じchunkを追加無音なし(各chunkのtrim margin残置分のみ)で結合した参考(TTS追加費用0。見かけの減速の切り分け用)
    mp3は out_dir/audio/ に出力(user_test/配下のみ追跡可)。reportは比較表(WPM・ポーズ・音量・費用・Gate)のhtml断片。"""
    import html as H
    aud = f"{out_dir}/audio"
    rows = [("part1", "本文1 (Full Story Part 1)", 1), ("part2", "本文2 (Full Story Part 2)", 2), ("part3", "本文3 (Full Story Part 3)", 3)]

    def mp3(tag, which, arr, br="96k"):
        fn = f"{which}_{tag}.mp3"
        _write_mp3(arr, f"{aud}/{fn}", br=br)
        return f"audio/{fn}"

    def cell(src):
        return f"<audio controls preload='none' src='{src}'></audio>" if src else "<span class='na'>Phase 2で生成</span>"
    parts_json = load_json(f"{A_LEVEL_DIR}/parts.json")
    trs = []
    for tag, label, n in rows:
        a = mp3(tag, "A", a_art["parts"][n])
        b = mp3(tag, "B", b_art["parts"][n]) if b_art else None
        b0 = mp3(tag, "B0", b0_art["parts"][n]) if b0_art else None
        trs.append(f"<tr><td><b>{label}</b></td><td class='play'>A 現行(1 Chunk)<br>{cell(a)}</td><td class='play'>B 段落Chunk<br>{cell(b)}</td>"
                   f"<td class='play'>B0 参考(追加無音なし)<br>{cell(b0)}</td>"
                   f"<td><div class='script'>{H.escape(parts_json[f'part{n}']).replace(chr(10), '<br>')}</div></td></tr>")
    a_body = mp3("body", "A", a_art["body"])
    b_body = mp3("body", "B", b_art["body"]) if b_art else None
    b0_body = mp3("body", "B0", b0_art["body"]) if b0_art else None
    a_full = mp3("full", "A", a_art["full"], "128k")
    b_full = mp3("full", "B", b_art["full"], "128k") if b_art else None
    trs.append(f"<tr><td><b>本文全体</b><br><span class='sec'>本文1+本文2+本文3(間1.0秒、A/B同一接続)</span></td><td class='play'>A<br>{cell(a_body)}</td>"
               f"<td class='play'>B<br>{cell(b_body)}</td><td class='play'>B0<br>{cell(b0_body)}</td><td></td></tr>")
    trs.append(f"<tr><td><b>Advanced通し</b><br><span class='sec'>同一組立(Intro〜Outro)。本文3 segmentのみB版へ差替え</span></td><td class='play'>A<br>{cell(a_full)}</td>"
               f"<td class='play'>B<br>{cell(b_full)}</td><td></td><td></td></tr>")
    rep_html = ("<h2>比較結果</h2>" + report.get("html", "")) if report else ""
    html_doc = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Family X 段落Chunk Trial A/B試聴</title>"
                f"<meta name='viewport' content='width=device-width, initial-scale=1'><style>{_PAGE_CSS}</style></head><body>"
                "<h1>Family X『英国の電車マナー』Advanced 段落単位TTS Chunk A/B試聴(Trial)</h1>"
                "<div class='note'><b>状態: Trial(Production採用ではありません)</b>。A=ユーザー承認済みの現行完成音声(本文1・2・3を各1 TTS Chunk)、"
                "B=本文内の段落ごとに別TTS Chunk(承認済みFamily C/Z接続方式)。B0=Bと同じ音声を追加無音なしで結合した参考。"
                "元文章・Voice(Aoede)・モデル・Style・既存の品質Gate・音量正規化(RMS)は同一。Production・公開済み完成ページは変更していません。</div>"
                f"<table><thead><tr><th>パート</th><th>A 現行</th><th>B 段落Chunk</th><th>B0 参考</th><th>Script</th></tr></thead><tbody>{''.join(trs)}</tbody></table>"
                f"{rep_html}</body></html>")
    ap = os.path.join(ROOT, out_dir, "index.html")
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    with open(ap, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return ap


# ============================================================
# 費用(出典: er005_output/cost_baseline_01/pricing_snapshot.json。USD_JPY=160は既存runnerと同一)
# ============================================================
USD_JPY = 160.0
TTS_STD_IN_USD_PER_M = 0.5     # gemini-3.8-flash-lite-tts Standard input_tokens
TTS_STD_OUT_USD_PER_M = 6.0    # 同 output_tokens (audio 25 tokens/sec)
ASR_IN_USD_PER_M = 1.25        # gpt-4o-mini-transcribe input_tokens
ASR_OUT_USD_PER_M = 5.0        # 同 output_tokens


def estimate_tts_jpy(audio_seconds: float, input_tokens: int) -> float:
    return (audio_seconds * 25 * TTS_STD_OUT_USD_PER_M / 1e6 + input_tokens * TTS_STD_IN_USD_PER_M / 1e6) * USD_JPY


def estimate_asr_jpy(n_calls: int, in_tokens_each: int = 530, out_tokens_each: int = 180) -> float:
    return n_calls * (in_tokens_each * ASR_IN_USD_PER_M / 1e6 + out_tokens_each * ASR_OUT_USD_PER_M / 1e6) * USD_JPY


# ============================================================
# Production sink隔離(Phase 2で使用。プロセス内override。Productionファイルは編集しない)
# ============================================================
@contextlib.contextmanager
def redirect_production_sinks(dev_dir: str):
    """Production書込み先4種をDEV dirへ向ける。終了時に必ず元へ戻す。
    er021のappend_telemetry_log は path 既定引数が定義時束縛のため、定数差替えでは効かない→関数自体をpath固定のwrapperに差替える。"""
    import importlib
    saved, patched_fn = [], []
    os.makedirs(os.path.join(ROOT, dev_dir), exist_ok=True)
    try:
        for modname, attr in SINK_CONSTANTS:
            mod = importlib.import_module(modname)
            old = getattr(mod, attr)
            saved.append((mod, attr, old))
            setattr(mod, attr, f"{dev_dir}/sink_{modname}_{attr}.jsonl")
        m21 = importlib.import_module("er021_en_asr_semantic_equivalence_production_01")
        orig_fn = m21.append_telemetry_log
        patched_fn.append((m21, "append_telemetry_log", orig_fn))
        dev_tel = f"{dev_dir}/sink_er021_telemetry_fn.jsonl"

        def _wrapped(record, path=None, _orig=orig_fn):
            return _orig(record, path=dev_tel)
        m21.append_telemetry_log = _wrapped
        yield
    finally:
        for mod, attr, old in saved:
            setattr(mod, attr, old)
        for mod, attr, old in patched_fn:
            setattr(mod, attr, old)


# ============================================================
# Phase 2: 生成(有料)。PHASE2_GO.json が無ければ起動しない。
# ============================================================
def _require_go() -> dict:
    ap = os.path.join(ROOT, PHASE2_GO_FILE)
    if not os.path.exists(ap):
        raise SystemExit(f"[STOP] {PHASE2_GO_FILE} が無い。Phase 2(有料生成)はOpus条件Aレビュー後のFable Goまで開始禁止。")
    go = load_json(PHASE2_GO_FILE)
    if go.get("managed_id") != MANAGED_ID or not go.get("cap_jpy"):
        raise SystemExit("[STOP] PHASE2_GO.json の managed_id / cap_jpy が不正")
    return go


def _stop_check() -> None:
    out = f"{OUT_DIR}/stop_check.json"
    py = sys.executable
    r = subprocess.run([py, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", OUT_DIR, "--out", out],
                       cwd=ROOT)
    if r.returncode == 3:
        raise SystemExit("[STOP] stop_scope_check rc=3")
    if r.returncode != 0:
        raise SystemExit(f"[STOP] stop_scope_check 異常 rc={r.returncode}")


def a_style_prefix() -> str:
    """A側の本文segmentが実際に使ったstyle文字列(tts_generation_results.json記録)。sha256がstyle_base_sha256と一致することを確認。"""
    rec = load_json(f"{A_LEVEL_DIR}/audit/tts_generation_results.json")["segments"]["full_story_part1"]
    style = rec["style_prefix"]
    want = rec["style_profile"]["style_base_sha256"]
    if hashlib.sha256(style.encode("utf-8")).hexdigest() != want:
        raise RuntimeError("A側style_prefixのsha256がstyle_base_sha256と不一致")
    return style


def build_whole_part_plan(parts_json: dict) -> list:
    """A_r2(Aの現行方式=本文part全体を1 TTS callで再生成する分散基準arm)用の計画。Production関数・入力整形はA本番と同一。"""
    mw = _mw()
    return [{"chunk_id": f"A_p{n}", "part": n, "index": 1, "text": parts_json[f"part{n}"], "words": mw.count_primary(parts_json[f"part{n}"])} for n in PARTS]


def arm_plan(arm: str, parts_json: dict) -> list:
    if arm in ("B_r1", "B_r2"):
        return [dict(c, chunk_id=f"{arm}_{c['chunk_id']}") for c in build_chunk_plan(parts_json)]
    if arm == "A_r2":
        return build_whole_part_plan(parts_json)
    raise SystemExit(f"[STOP] unknown arm {arm}")


def generate_chunks_phase2(plan: list, only: list | None = None, tts_generate_fn=None) -> dict:
    """段落chunkを1つずつ(直列)、Production関数 news_tail_fix.generate_news_narration_wide_margin で生成する。
    各chunkは out_path=<OUT>/gen/<chunk_id>/b1b/narration/full_story_part<n>.wav に出力
    → segment_id='full_story_part<n>'(role=FULL_STORY=A側と同一のGate適用)、review-lock storeは<OUT>/gen/<chunk_id>/b1b/audit内(Production非接触)。
    tts_generate_fn: test用のinjection(本番はNone=Production関数)。"""
    import er003_v1_n3_01_tts_generate as n3_tts
    import er003_v1_sing01_news_tail_fix as news_tail_fix
    import er020_tts_retry_local_rewrite_01 as retry_primitive
    import er005_cost_logger as cl
    import er019_family_x_audio_production_runner_01 as runner
    import er078_secondary_run_scope_01 as secondary_run_scope
    import er109_xz_scope_01 as er109_scope
    import er081_family_x_in_one_line_01 as fx_iol
    import er103_pnap_runner_hooks_01 as pnap_hooks

    go = None if tts_generate_fn else _require_go()
    cap = float(go["cap_jpy"]) if go else 1e9
    style = a_style_prefix()
    gen = tts_generate_fn or news_tail_fix.generate_news_narration_wide_margin
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not tts_generate_fn:
        cl.install(os.path.join(ROOT, log_path))

    results = {}

    @secondary_run_scope.with_secondary_run
    @fx_iol.family_x_in_one_line_scope()
    @pnap_hooks.family_scope("X", "b1b")
    @er109_scope.family_scope("X")
    def _run(theme_out_dir: str):
        for ch in plan:
            if only and ch["chunk_id"] not in only:
                continue
            spent, _ = runner.compute_cost_jpy_so_far(os.path.join(ROOT, log_path))
            if spent >= cap:
                raise SystemExit(f"[STOP] 個別Cap {cap}円到達(実績{spent:.2f}円)")
            seg = f"full_story_part{ch['part']}"
            wav = f"{OUT_DIR}/gen/{ch['chunk_id']}/b1b/narration/{seg}.wav"
            os.makedirs(os.path.dirname(os.path.join(ROOT, wav)), exist_ok=True)
            tts_input = runner._pnap_supply(ch["text"], n3_tts.tts_safe_news_en(ch["text"]))  # A側と同じ整形(tts_safe_news_en→pnap_supply)
            with cl.segment_context(ch["chunk_id"]):
                res = gen(tts_input, os.path.join(ROOT, wav), disfluency_qa=False,
                          enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(seg),
                          enable_repetition_qa=True, enable_pronunciation_resolver=True,
                          style_prefix_override=style, tts_backend="speech_metadata_flash_lite")
            results[ch["chunk_id"]] = {"status": res.get("status"), "path": wav, "tts_input_sha256": hashlib.sha256(tts_input.encode()).hexdigest(),
                                       "attempts": len(res.get("attempts_log") or []), "audio_classification": res.get("audio_classification"),
                                       "repetition_qa_checked": res.get("repetition_qa_checked"), "trim_info": res.get("trim_info")}
            if res.get("status") != "OK":
                break  # 自動再実行しない。Fableへ報告(既存retry/Gateの上限=PRODUCTION_MAX_TTS_ATTEMPTSは関数内で消化済み)
    _run(f"{OUT_DIR}/gen")
    return results


# ============================================================
# CLI
# ============================================================
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "measure_a", "a_boundaries", "verify_rebuild", "gen"])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--arms", nargs="*", default=["B_r1"], help="gen: B_r1(必須) / A_r2(分散基準: Aの方式で再生成) / B_r2(Bの再take)。1 launchで直列実行")
    a = ap.parse_args()
    if a.cmd == "plan":
        plan = build_chunk_plan(load_json(f"{A_LEVEL_DIR}/parts.json"))
        save_json(f"{OUT_DIR}/chunk_plan_01.json", plan)
        print(json.dumps([{k: v for k, v in c.items() if k != "text"} for c in plan], ensure_ascii=False))
    elif a.cmd == "measure_a":
        res = measure_a_side()
        save_json(f"{OUT_DIR}/a_side_measure_01.json", res)
        print(json.dumps({k: res[k] for k in ("total",)}, ensure_ascii=False))
    elif a.cmd == "a_boundaries":
        res = measure_a_boundary_gaps()
        save_json(f"{OUT_DIR}/a_boundary_gaps_01.json", res)
        print(json.dumps(res, ensure_ascii=False))
    elif a.cmd == "verify_rebuild":
        import soundfile as sf
        before = snapshot_protected()
        r = rebuild_full_episode(None)
        x, sr = sf.read(os.path.join(ROOT, f"{A_LEVEL_DIR}/assembled/Family_X_Audio_B1_UK_TRAIN_SPEAKER_PLAYBACK.wav"), dtype="float32")
        y = r["assembled"].astype("float32")
        n = min(len(x), len(y))
        out = {"len_ref": len(x), "len_rebuilt": len(y), "max_abs_diff": float(np.max(np.abs(x[:n] - y[:n]))) if n else None,
               "protected_changed": diff_snapshots(before, snapshot_protected())}
        save_json(f"{OUT_DIR}/rebuild_check_01.json", out)
        print(json.dumps(out))
    elif a.cmd == "gen":
        _require_go()
        _stop_check()
        before = snapshot_protected()
        parts_json = load_json(f"{A_LEVEL_DIR}/parts.json")
        res = {}
        with redirect_production_sinks(f"{OUT_DIR}/sinks"):
            for arm in a.arms:
                r = generate_chunks_phase2(arm_plan(arm, parts_json), only=a.only)
                res.update(r)
                if any(v["status"] != "OK" for v in r.values()):
                    break  # 失敗したら後続armへ進まず停止・報告(自動再実行しない)
        changed = diff_snapshots(before, snapshot_protected())
        save_json(f"{OUT_DIR}/gen_result_01.json", {"results": res, "protected_changed": changed})
        print(json.dumps({"results": {k: v["status"] for k, v in res.items()}, "protected_changed": changed}))
        if changed:
            raise SystemExit(f"[STOP] Production storeが変化: {changed}")


if __name__ == "__main__":
    main()
