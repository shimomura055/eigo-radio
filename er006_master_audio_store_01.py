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
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def _log_telemetry(record: dict) -> None:
    os.makedirs(STORE_DIR, exist_ok=True)
    record = {"timestamp": time.time(), **record}
    with open(TELEMETRY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def get_or_generate(key: MasterAudioKey, out_path: str,
                     generate_fn: Callable[[str], dict]) -> dict:
    """key(MasterAudioKey)に一致するmasterが既にStoreにあれば、それを
    out_pathへコピーして再利用する(TTS/ASR呼び出しは一切行わない)。
    無ければgenerate_fn(out_path)を呼んでTTS生成させ、成功時のみStoreへ
    登録する(STOPPED等の失敗結果はStoreへ入れない)。

    generate_fnは通常のgenerate_charon_english/generate_key_phrase_
    component_verified等と同じ呼び出し規約(out_pathを渡し、statusを
    含むdictを返す)を想定する。

    戻り値のdictには reused(bool)・master_audio_id・cache_miss_reason
    (reused=Falseのときのみ)を追加で含む。"""
    master_id = key.master_audio_id()
    manifest = _load_manifest()
    entry = manifest.get(master_id)

    if entry is not None and os.path.exists(entry["audio_path"]):
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        shutil.copyfile(entry["audio_path"], out_path)
        result = {
            "status": "OK", "path": out_path, "reused": True,
            "master_audio_id": master_id, "cache_miss_reason": None,
        }
        # ER-008-N8-FINAL-QA-HARDENING-21 Item 1/7: 以前はreused=Trueの
        # 場合、statusとpathだけの最小限dictを返しており、生成時に記録した
        # disfluency_checked等のQA証跡が再利用のたびに失われていた。この
        # ためAssemble Gateの必須QA証跡チェックが、実際にはQA合格済みの
        # 資産まで「証跡が無い」としてblockしてしまう(No.8 kp2の恒久修正
        # 作業中に発見)。manifestに保存したqa_evidenceをここで復元する。
        result.update(entry.get("qa_evidence") or {})
        _log_telemetry({
            "event": "reused", "master_audio_id": master_id, "out_path": out_path,
            "key": key.as_dict(),
        })
        return result

    cache_miss_reason = "no_existing_master" if entry is None else "stored_audio_file_missing"
    r = generate_fn(out_path)
    if r.get("status") == "OK":
        os.makedirs(AUDIO_DIR, exist_ok=True)
        stored_path = f"{AUDIO_DIR}/{master_id}.wav"
        shutil.copyfile(out_path, stored_path)
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
    r["reused"] = False
    r["master_audio_id"] = master_id
    r["cache_miss_reason"] = cache_miss_reason
    return r
