# ============================================================
# er006_master_audio_store_01.py
# ER-006-MASTER-AUDIO-STORE-01: 定型音声の最小Production-ready Store
# ============================================================
# ER-006-AUDIO-COST-OPTIMIZATION-01の監査(master_audio_audit.md)で
# 設計したMaster Audio Keyスキーマの最小実装。対象は意図的に:
#   (1) 完全固定segment(Welcome/Preview intro/Key phrases intro/
#       Full story intro/番号語等)
#   (2) B1/A2で完全一致するKey Phrase(voice/model/style-instructionが
#       全て同じ場合のみ)
# の2種類に限定する。可変ナレーション(Story本文・Comment等)には適用
# しない。
#
# 既知のdrift(welcome.wavがB1向け/A2向けで別録音・別長さになっていた
# 問題、ER-006-AUDIO-COST-OPTIMIZATION-01 §2.2)は、このStoreを経由する
# ようになった時点から、同じKeyに対して常に同じmaster_audio_idの音声
# ファイルだけが再利用されることで解消される。既存の完成episodeを
# 書き換える必要はなく、今後の生成分から適用する。

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

STORE_DIR = "er006_output/master_audio_store_01"
AUDIO_DIR = f"{STORE_DIR}/audio"
MANIFEST_PATH = f"{STORE_DIR}/manifest.json"
TELEMETRY_PATH = f"{STORE_DIR}/reuse_telemetry.jsonl"

EQUALITY_FIELDS = (
    "language", "level", "speaker_voice", "tts_model_id",
    "style_instruction_id", "style_instruction_version", "instruction_path",
    "canonical_text_hash", "audio_processing_version", "sample_rate", "channels",
)


@dataclass
class MasterAudioKey:
    language: str
    speaker_voice: str
    tts_model_id: str
    canonical_text: str
    style_instruction_id: str = "default"
    style_instruction_version: str = "v1"
    instruction_path: str = "primary"
    audio_processing_version: str = "v1"
    sample_rate: int = 24000
    channels: int = 1
    level: Optional[str] = None  # None = level非依存(service-level shared)

    def canonical_text_hash(self) -> str:
        return hashlib.sha256(self.canonical_text.encode("utf-8")).hexdigest()[:16]

    def as_dict(self) -> dict:
        d = {
            "language": self.language, "level": self.level,
            "speaker_voice": self.speaker_voice, "tts_model_id": self.tts_model_id,
            "style_instruction_id": self.style_instruction_id,
            "style_instruction_version": self.style_instruction_version,
            "instruction_path": self.instruction_path,
            "canonical_text_hash": self.canonical_text_hash(),
            "audio_processing_version": self.audio_processing_version,
            "sample_rate": self.sample_rate, "channels": self.channels,
        }
        return d

    def master_audio_id(self) -> str:
        d = self.as_dict()
        payload = json.dumps({k: d[k] for k in EQUALITY_FIELDS}, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _load_manifest() -> dict:
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_manifest(manifest: dict) -> None:
    os.makedirs(STORE_DIR, exist_ok=True)
    # TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(Opus M-7): tmp+os.replaceの原子的書込(読込側が書込途中のJSONを見ない)。内容は従来と同一。
    tmp = f"{MANIFEST_PATH}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, MANIFEST_PATH)


def _log_telemetry(record: dict) -> None:
    os.makedirs(STORE_DIR, exist_ok=True)
    record = {"timestamp": time.time(), **record}
    with open(TELEMETRY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def get_or_generate(key: MasterAudioKey, out_path: str,
                     generate_fn: Callable[[str], dict], reuse_gate=None) -> dict:
    """key(MasterAudioKey)に一致するmasterが既にStoreにあれば、それを
    out_pathへコピーして再利用する(TTS/ASR呼び出しは一切行わない)。
    無ければgenerate_fn(out_path)を呼んでTTS生成させ、成功時のみStoreへ
    登録する(STOPPED等の失敗結果はStoreへ入れない)。

    generate_fnは通常のgenerate_charon_english/generate_key_phrase_
    component_verified等と同じ呼び出し規約(out_pathを渡し、statusを
    含むdictを返す)を想定する。

    reuse_gate(KPDUAL-PROD-D2、2026-10-22、既定None=Family A/B/C等の既存呼出は無変更・manifestにも新キーを書かない):
    KP英語phrase「Primary・Secondary両方PASS必須」(UDR #139)のX専用gate。callable(entry, key, master_id) -> dict
    {"action": "reuse"|"regenerate"|"technical_stop", "reason":..., "kp_dual_check": dict|None}。entryがある再利用直前に
    1回だけ呼ぶ。reuse=従来どおり再利用(kp_dual_checkをmanifestへ追記)/regenerate=旧音声を_reuse_blockedへ退避して再生成/
    technical_stop=Azure障害のため再利用も再生成もしない(TECHNICAL_STOP statusを返す)。新規生成成功時は
    reuse_gate.on_generated(r, stored_path, key)の戻り値をentryの`kp_dual_check`へ保存する。

    戻り値のdictには reused(bool)・master_audio_id・cache_miss_reason
    (reused=Falseのときのみ)を追加で含む。"""
    master_id = key.master_audio_id()
    manifest = _load_manifest()
    entry = manifest.get(master_id)

    # AUW 委任_06c(OF-AUW-C-03、ADDENDUM §3-1): 再利用前に保存転写のみ(API 0)を現行の統一judgeへ通し、値ガードDIFF/否定差、
    # または一括再判定が付けた`reuse_blocked` markがあれば再利用せず再生成へ回す(旧資産は削除せず退避して保持)。
    reuse_guard_info = None
    if entry is not None and os.path.exists(entry["audio_path"]):
        import er078_reuse_value_guard_01 as _rvg
        _probe = dict(entry.get("qa_evidence") or {})
        _probe["asr_judgement"] = entry.get("asr_judgement")
        _probe["reuse_blocked"] = entry.get("reuse_blocked")
        reuse_guard_info = _rvg.guard_entry(_probe, label="master:" + str(key.style_instruction_id),
                                            canonical_text=key.canonical_text,
                                            kp_vote_gate_follows=(reuse_gate is not None))   # KP-QUALITY OF-KPQ-P-01: vote gateが後続する呼出のみ保護再判定をskip
        if reuse_guard_info["blocked"]:
            _log_telemetry({"event": "reuse_blocked_by_value_guard", "master_audio_id": master_id, "out_path": out_path,
                            "key": key.as_dict(), "guard": {k: reuse_guard_info.get(k) for k in ("reason", "reason_code", "unified_state")}})
            try:  # 削除しない: 再生成が同じaudio_pathを上書きするため、旧音声を退避して残す
                _bdir = f"{AUDIO_DIR}/_reuse_blocked"
                os.makedirs(_bdir, exist_ok=True)
                shutil.copyfile(entry["audio_path"], f"{_bdir}/{master_id}_{time.strftime('%Y%m%dT%H%M%S')}.wav")
            except OSError:
                pass
    dual_gate_info = None
    if (reuse_gate is not None and entry is not None and os.path.exists(entry["audio_path"])
            and not (reuse_guard_info or {}).get("blocked")):
        dual_gate_info = reuse_gate(entry, key, master_id)
        _act = dual_gate_info.get("action")
        if dual_gate_info.get("kp_dual_check") is not None:
            entry["kp_dual_check"] = dual_gate_info["kp_dual_check"]
            manifest[master_id] = entry
            _save_manifest(manifest)
        if _act == "technical_stop":
            _log_telemetry({"event": "reuse_gate_technical_stop", "master_audio_id": master_id, "out_path": out_path,
                            "key": key.as_dict(), "reason": dual_gate_info.get("reason")})
            return {"status": "TECHNICAL_STOP_SECONDARY_UNAVAILABLE", "technical_stop": True, "restartable": True,
                    "approval_required": False, "human_review_required": False, "asr_verified": False, "reused": False,
                    "master_audio_id": master_id, "master_audio_key": key.as_dict(), "path": out_path,
                    "reason": "KP dual reuse gate: Secondary(Azure)障害のため再利用判定不能(再利用も再生成もしない。再実行で再開可)",
                    "kp_dual_reuse_gate": {k: dual_gate_info.get(k) for k in ("action", "reason")}}
        if _act != "reuse":
            reuse_guard_info = {"blocked": True, "reason": dual_gate_info.get("reason"), "reason_code": "kp_dual_gate",
                                "unified_state": (dual_gate_info.get("kp_dual_check") or {}).get("judge_state")}
            _log_telemetry({"event": "reuse_blocked_by_kp_dual_gate", "master_audio_id": master_id, "out_path": out_path,
                            "key": key.as_dict(), "reason": dual_gate_info.get("reason"),
                            "kp_dual_check": dual_gate_info.get("kp_dual_check")})   # NG時の両Provider転写も証跡として残す
            try:  # 削除しない: 旧音声を退避して残す(再生成が同じaudio_pathを上書きする)
                _bdir = f"{AUDIO_DIR}/_reuse_blocked"
                os.makedirs(_bdir, exist_ok=True)
                shutil.copyfile(entry["audio_path"], f"{_bdir}/{master_id}_{time.strftime('%Y%m%dT%H%M%S')}.wav")
            except OSError:
                pass
    if entry is not None and os.path.exists(entry["audio_path"]) and not (reuse_guard_info or {}).get("blocked"):
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        shutil.copyfile(entry["audio_path"], out_path)
        result = {
            "status": "OK", "path": out_path, "reused": True,
            "master_audio_id": master_id, "cache_miss_reason": None,
            # W5(Opus L2所見N-4是正、2026-09-29): reuse経路の戻り値には
            # 従来model/voice/style_instruction_id/version/canonical_text
            # が含まれず、追跡にはmanifest.jsonとのjoinが必要だった
            # (master_audio_id経由)。key.as_dict()を追加するだけでjoin
            # 不要になる(既存キーは無変更、追加のみ)。
            "master_audio_key": key.as_dict(),
        }
        # ER-008-N8-FINAL-QA-HARDENING-21 Item 1/7: 以前はreused=Trueの
        # 場合、statusとpathだけの最小限dictを返しており、生成時に記録した
        # disfluency_checked等のQA証跡が再利用のたびに失われていた。この
        # ためAssemble Gateの必須QA証跡チェックが、実際にはQA合格済みの
        # 資産まで「証跡が無い」としてblockしてしまう(No.8 kp2の恒久修正
        # 作業中に発見)。manifestに保存したqa_evidenceをここで復元する。
        result.update(entry.get("qa_evidence") or {})
        # AUW 委任_03(additive): 生成時の統一ASR判定record(PASS_WITH_WARNING等)を、再利用音声でも
        # `asr_judgement_inherited`として復元する(元のWARNINGを試聴リストへ継承。OF-AUW-15)。
        if entry.get("asr_judgement") is not None:
            result["asr_judgement_inherited"] = entry["asr_judgement"]
        if entry.get("kp_dual_check") is not None:   # KPDUAL-PROD-D2(additive): KP dual証跡(gate通過済み)を再利用でも復元する
            result["kp_dual_check"] = entry["kp_dual_check"]
        _log_telemetry({
            "event": "reused", "master_audio_id": master_id, "out_path": out_path,
            "key": key.as_dict(),
        })
        return result

    cache_miss_reason = ("no_existing_master" if entry is None else
                         ("kp_dual_gate_blocked" if (reuse_guard_info or {}).get("reason_code") == "kp_dual_gate"
                          else "reuse_value_guard_blocked") if (reuse_guard_info or {}).get("blocked") else "stored_audio_file_missing")
    r = generate_fn(out_path)
    if r.get("status") == "OK":
        os.makedirs(AUDIO_DIR, exist_ok=True)
        stored_path = f"{AUDIO_DIR}/{master_id}.wav"
        shutil.copyfile(out_path, stored_path)
        # TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(Opus M-7): generate_fn内は180秒待機+複数TTSで長い。冒頭で読んだmanifestは古く、
        # 並列process(evidenceは6並列)が待機中に登録した他entryや`reuse_blocked`印を上書き・消去し得る(ブロック済み音声の再利用=品質リスク)。
        # 保存直前に再読込してmergeする(自分のentryだけを追加。従来の単独process結果は不変)。
        manifest = _load_manifest()
        manifest[master_id] = {
            "audio_path": stored_path, "key": key.as_dict(),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            # ER-008-N8-FINAL-QA-HARDENING-21 Item 1/7: 生成時のQA証跡を
            # manifestへ保存し、以降のcache hit再利用でも失われないように
            # する(reused=Trueの結果にも同じ証跡を復元できるようにする)。
            "qa_evidence": {
                "sha256": r.get("sha256"), "asr_verified": r.get("asr_verified"),
                "asr_text": r.get("asr_text"), "disfluency_checked": r.get("disfluency_checked"),
                "disfluency_evidence": r.get("disfluency_evidence"),
            },
        }
        # OPEN-258 SCG(Opus推奨7): 追加のみ(既存キー不変)。SCG PASS(Primary不一致をSecondaryで
        # 救済)したmasterを後から識別できるようにする。SCG非関与(英語等)はNone。
        manifest[master_id]["audio_classification"] = r.get("audio_classification")
        # AUW 委任_03(additive): 統一ASR判定のaudit record。再利用時に`asr_judgement_inherited`として復元する。
        manifest[master_id]["asr_judgement"] = r.get("asr_judgement")
        if reuse_gate is not None and hasattr(reuse_gate, "on_generated"):
            _kdc = reuse_gate.on_generated(r, stored_path, key)   # KPDUAL-PROD-D2: 生成時のdual証跡(両Provider転写・判定)を保存
            if _kdc is not None:
                manifest[master_id]["kp_dual_check"] = _kdc
                r["kp_dual_check"] = _kdc
        _scg = r.get("scg_info")
        manifest[master_id]["scg_result"] = _scg.get("scg_result") if isinstance(_scg, dict) else None
        _save_manifest(manifest)
        _log_telemetry({
            "event": "generated", "master_audio_id": master_id, "out_path": out_path,
            "cache_miss_reason": cache_miss_reason, "key": key.as_dict(),
        })
    else:
        _log_telemetry({
            "event": "generate_failed", "master_audio_id": master_id, "out_path": out_path,
            "cache_miss_reason": cache_miss_reason, "status": r.get("status"), "key": key.as_dict(),
        })
    if dual_gate_info is not None and dual_gate_info.get("action") == "regenerate":
        r["kp_dual_reuse_gate_previous"] = {"reason": dual_gate_info.get("reason"),   # 再生成に回した旧entryの判定理由(additive)
                                            "kp_dual_check": dual_gate_info.get("kp_dual_check")}
    r["reused"] = False
    r["master_audio_id"] = master_id
    r["cache_miss_reason"] = cache_miss_reason
    # W5(N-4是正): 新規生成時もreuse時と同じ形で追跡できるようkeyを含める。
    r["master_audio_key"] = key.as_dict()
    return r


# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29): 既にTrial等
# で生成・ASR検証済みの音声ファイルを、TTS/ASR呼び出しを一切行わずに
# Master Audio Storeへ直接登録するための最小追加関数(既存get_or_generate
# のTTS生成パスは無変更、この関数からは呼ばれない)。固定フレーズ
# Championの正式登録(read-onlyなsource_audio_pathからのコピーのみ)専用。
def register_precomputed(key: MasterAudioKey, source_audio_path: str, qa_evidence: dict) -> dict:
    """key.master_audio_id()が既にmanifestに存在する場合は何もせず
    SKIPPED_ALREADY_EXISTSを返す(既存entryの上書き禁止、idempotent)。
    存在しない場合のみsource_audio_pathをAUDIO_DIRへコピーし、manifestへ
    新entryを追加する(get_or_generateが生成成功時に書き込む形式と同じ
    dict構造、qa_evidenceは呼び出し側が用意した既存ASR結果等を渡す)。"""
    master_id = key.master_audio_id()
    manifest = _load_manifest()
    if master_id in manifest:
        return {
            "status": "SKIPPED_ALREADY_EXISTS", "master_audio_id": master_id,
            "audio_path": manifest[master_id]["audio_path"],
        }
    if not os.path.exists(source_audio_path):
        return {"status": "SOURCE_MISSING", "master_audio_id": master_id, "source_audio_path": source_audio_path}
    os.makedirs(AUDIO_DIR, exist_ok=True)
    stored_path = f"{AUDIO_DIR}/{master_id}.wav"
    shutil.copyfile(source_audio_path, stored_path)
    manifest[master_id] = {
        "audio_path": stored_path, "key": key.as_dict(),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "qa_evidence": qa_evidence,
    }
    _save_manifest(manifest)
    _log_telemetry({
        "event": "registered_precomputed", "master_audio_id": master_id,
        "source_audio_path": source_audio_path, "key": key.as_dict(),
    })
    return {"status": "REGISTERED", "master_audio_id": master_id, "audio_path": stored_path}
