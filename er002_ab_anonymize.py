# ============================================================
# er002_ab_anonymize.py
# ER-002: A/B比較用のラベル匿名化(A04・A05向け)
# ============================================================
# 話者そのものを聞き分け不能にするものではない。ファイル名・提示順・
# WAVメタデータから話者名を事前に読み取れないようにする「ラベル匿名化」で、
# 話者名による先入観(バイアス)を減らすことが目的。
#
# 内部の対応表(どのsampleラベルが実際にどの話者か)は別ファイルへ保存し、
# Git追跡対象外とする。評価確定後に開示する運用を前提とする。

from __future__ import annotations

import io
import json
import random
import wave
from dataclasses import dataclass, field


def anonymized_filename(article_id: str, sample_index: int) -> str:
    """記事IDのみを含み、話者名・題材の詳細を含まないファイル名を返す。
    例: anonymized_filename("a04", 1) -> "er002_a04_sample_1.wav" """
    return f"er002_{article_id}_sample_{sample_index}.wav"


def strip_wav_metadata(wav_bytes: bytes) -> bytes:
    """WAVをfmt/dataチャンクのみで作り直し、LIST/INFO等のメタデータチャンク
    (アプリ名・作成者タグ等)が残らない最小構成にする。"""
    with wave.open(io.BytesIO(wav_bytes), "rb") as r:
        params = r.getparams()
        frames = r.readframes(r.getnframes())
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(params.nchannels)
        w.setsampwidth(params.sampwidth)
        w.setframerate(params.framerate)
        w.writeframes(frames)
    return buf.getvalue()


@dataclass
class ABPresentation:
    article_id: str
    order: list = field(default_factory=list)   # ["sample_1", "sample_2", ...] (匿名ラベルの列挙)
    mapping: dict = field(default_factory=dict)  # {"sample_1": {実際の話者情報...}, ...}


def build_ab_presentation(article_id: str, entries: list[dict], seed: int | None = None) -> ABPresentation:
    """entries: 実際の話者データのリスト(例: [{"voice": "Aoede", ...}, {"voice": "Charon", ...}])。
    どのentryがsample_1になるかを記事ごとにランダム化して割り当てる
    (同じ記事を複数回呼んでも、毎回異なる割り当てにしたい場合はseedを固定しない)。"""
    rng = random.Random(seed)
    shuffled = list(entries)
    rng.shuffle(shuffled)

    mapping = {}
    order = []
    for i, entry in enumerate(shuffled, start=1):
        label = f"sample_{i}"
        mapping[label] = dict(entry)
        order.append(label)

    return ABPresentation(article_id=article_id, order=order, mapping=mapping)


def filename_reveals_speaker(filename: str, speaker_names: list[str]) -> bool:
    """ファイル名から話者名を直接判別できないことを確認するためのチェック関数。
    (完全な匿名性を保証するものではなく、直接的な文字列一致のみを検出する)"""
    lowered = filename.lower()
    return any(name.lower() in lowered for name in speaker_names)


def metadata_reveals_speaker(wav_bytes: bytes, speaker_names: list[str]) -> bool:
    """WAVバイト列全体(RIFFヘッダ含む)に話者名の文字列がそのまま埋め込まれていないかを
    簡易チェックする(strip_wav_metadata適用後の確認用)。"""
    try:
        text_view = wav_bytes.decode("latin-1", errors="ignore").lower()
    except Exception:
        return False
    return any(name.lower() in text_view for name in speaker_names)


def save_mapping_table(mapping: dict, path: str) -> None:
    """対応表を保存する。呼び出し側は、このpathが.gitignoreで除外されている
    パターン(er002_*_ab_mapping.json)に一致することを保証すること。"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def load_mapping_table(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class ABFilenameConsistencyError(ValueError):
    pass


def validate_ab_bundle_filename_consistency(bundle: dict, article_id: str, expected_sample_count: int) -> None:
    """ER-002-S2-C2で発生した大文字小文字不一致(手動リネームにより実ファイルと
    対応表のarticle_idの大文字小文字がずれた)の再発防止。

    - files / filename_mapping / user_evaluations のキー集合が文字列として
      完全一致すること(大文字小文字含む)
    - filesの各キーが、article_id・1..expected_sample_countから機械的に
      導出したファイル名(anonymized_filename)と過不足なく一致すること
      (sample_1・sample_2それぞれちょうど1つずつ存在することを含む)
    いずれかが崩れていれば例外を送出する(fail-closed。不一致のまま
    ファイルを書き出させない)。"""
    files_keys = set(bundle["files"].keys())
    mapping_keys = set(bundle["filename_mapping"].keys())
    eval_keys = set(bundle["user_evaluations"].keys())

    if not (files_keys == mapping_keys == eval_keys):
        raise ABFilenameConsistencyError(
            "A/Bバンドルのファイル名(files/filename_mapping/user_evaluations)が"
            f"一致していません: files={sorted(files_keys)}, "
            f"filename_mapping={sorted(mapping_keys)}, user_evaluations={sorted(eval_keys)}"
        )

    expected_filenames = {anonymized_filename(article_id, n) for n in range(1, expected_sample_count + 1)}
    if files_keys != expected_filenames:
        raise ABFilenameConsistencyError(
            f"A/Bバンドルのファイル名がsample_1..sample_{expected_sample_count}と"
            f"一致していません: 実際={sorted(files_keys)}, 期待={sorted(expected_filenames)}"
        )
