# -*- coding: utf-8 -*-
"""ローカルWhisper遅延ロード(Trial専用)。"""
_M = {}


def whisper(size, wav):
    from faster_whisper import WhisperModel
    if size not in _M:
        _M[size] = WhisperModel(size, device="cpu", compute_type="int8", local_files_only=True)
    segs, _ = _M[size].transcribe(wav, language="en", beam_size=5, vad_filter=False)
    return " ".join(s.text.strip() for s in segs)
