# -*- coding: utf-8 -*-
"""Family Y Production runner の mock 部品(--mode mock と test 専用。実APIへは一切出ない)。

- MockApi: API境界(STOPセンチネル確認 + 呼出カウンタ)。
- MockClient: OpenAI clientの偽物(responses.create だけ)。英訳(Adv/Std)・Listening Support を決定論の短い本文で返す。
- FakeTextCore: text core(produce_article)の偽物。Y契約を満たすJA 5パートを返す。
- fake TTS: 低レベルのTTS生成関数(voice01/news_tail_fix/n3_tts/crosslevel_common/shared_narration/X KP生成)を差し替えるcontext manager。
  tone wavとX互換のentry(status=OK等)を返す。実TTS/ASR/Azureへ出ない。
"""
from __future__ import annotations

import contextlib
import json
import os
import re
import time

import er121_family_y_structure_01 as ys

SAMPLE_TITLE_EN = "The Missed Delivery"

EN_ADV = (
    f"# {SAMPLE_TITLE_EN}\n\n"
    "Many of us come home to a slip in the mailbox. Is paying a small fee for another try fair?\n\n"
    "A courier talks about the road.\n"
    "I drive the same route every day, and I leave a note when nobody opens the door.\n\n"
    "A parent talks about waiting.\n"
    "I wait all morning for the bell to ring, but the van never comes at that hour.\n\n"
    "A student talks about money.\n"
    "I do not mind a small fee, but I want to choose when I pick it up.\n\n"
    "So who should carry the cost of a missed delivery, and what could really change it?\n"
)
EN_STD = EN_ADV.replace("Many of us come home to", "Many of us come home and find").replace("fair?", "fair to you?")

KP_SPANS = ["leave a note", "wait all morning", "pick it up", "a small fee", "the same route", "come home", "another try", "carry the cost"]


class MockApi:
    """mock時の『API境界』。呼出ごとに (1) STOPセンチネル確認 (2) 呼出カウンタ追記(<run>/mock_api_calls.jsonl)。"""

    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        self.path = f"{out_dir}/mock_api_calls.jsonl"
        self.n = 0

    def call(self, kind: str, label: str = "") -> int:
        import er062_family_z_structure_01 as st
        st.api_guard(f"mock_api:{kind}:{label}", self.out_dir)
        self.n += 1
        os.makedirs(self.out_dir, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"n": self.n, "kind": kind, "label": label, "ts": time.time(), "pid": os.getpid()}, ensure_ascii=False) + "\n")
        return self.n

    def wrap(self, kind: str, fn):
        def w(*a, **k):
            first = a[0] if a else ""
            self.call(kind, str(first)[:60] if isinstance(first, str) else "")
            return fn(*a, **k)
        return w


class _Resp:
    def __init__(self, text, model):
        self.output_text, self.id, self.model = text, "mock_resp", model
        self.usage = type("U", (), {"input_tokens": 1000, "output_tokens": 500, "input_tokens_details": None, "output_tokens_details": None})()


class _Responses:
    def __init__(self, api):
        self.api, self.calls = api, []

    def create(self, **kw):
        import er003_v1_b1_scaffold_01_generate as b1s
        import er003_v1_iran01_a2_generate as a2gen
        import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
        import er003_v1_n3_01_standard_a2_generate as std_gen
        dev = kw["input"][0]["content"] if kw.get("input") and kw["input"][0].get("role") == "developer" else ""
        self.api.call("llm", dev[:20])
        self.calls.append(kw)
        if dev == adv_gen.FAMILY_X_TRANSLATOR_DEVELOPER:
            return _Resp(EN_ADV, kw["model"])
        if dev == std_gen.STANDARD_A2_DEVELOPER:
            return _Resp(EN_STD, kw["model"])
        if dev == b1s.SUPPORT_DEVELOPER_MESSAGE:
            return _Resp("A short mock support line for the listener.", kw["model"])
        if dev == a2gen.SUPPORT_DEVELOPER_MESSAGE:
            return _Resp("これはモックの短い補助文です。", kw["model"])
        raise AssertionError(f"MockClient: 想定外のLLM呼出(developer先頭={dev[:40]!r})。偽物で埋めずに失敗させる")


class MockClient:
    def __init__(self, api):
        self.responses = _Responses(api)


# ------------------------------------------------------------
# text core(偽)
# ------------------------------------------------------------
class FakeTextCore:
    def __init__(self, api=None):
        self.api, self.calls = api, 0

    def produce_article(self, client, *, slug, theme_package, out_dir, guard=None):
        self.calls += 1
        if guard:
            guard("text_mock")
        if self.api:
            self.api.call("text_core", slug)
        return {"title": "配達の再配達",
                "lead": "不在票が入っていた経験は、誰にでもあるはずです。再配達に料金を取ることは、公平でしょうか。",
                "intros": {"voice_1": "配達する人の話です。", "voice_2": "待つ人の話です。", "voice_3": "学生の話です。"},
                "voices": {"voice_1": "私は毎日同じ道を走り、誰も出なければメモを残します。",
                           "voice_2": "私は午前中ずっと待っていますが、その時間に荷物は来ません。",
                           "voice_3": "私は少しの料金なら払えますが、受け取る時間は自分で選びたいです。"},
                "closing": "では、届かなかった分の負担は誰が持つべきで、何が本当にそれを変えるのでしょうか。",
                "closing_record": {"source": "mock", "general_method_used": False, "routing_key": "FAMILY_Y_CLOSING_GENERATE", "model_id": "mock-model",
                                   "prompt_sha256": "ab" * 32, "final_sha256": "cd" * 32},
                "records": {"voice_generate": {"routing_key": "FAMILY_Y_VOICE_GENERATE", "model_id": "mock-model"}}}


# ------------------------------------------------------------
# KP / 解説(偽)
# ------------------------------------------------------------
def mock_kp_fn(text, kp_dir, article_id, source_level, process=None, n_max=8, **kw):
    spans = [s for s in KP_SPANS if s in text][:n_max]
    if len(spans) < 3:
        raise AssertionError(f"mock KP: 本文に実在する候補が{len(spans)}件しかない")
    os.makedirs(kp_dir, exist_ok=True)
    items = [{"rank": i, "source_span": s, "source_sentence": s, "display_phrase": s, "key_phrase": s, "used_form": s,
              "japanese_gloss": f"意味{i}", "fulltext_source_ref": "fulltext_exact_v1"} for i, s in enumerate(spans, 1)]
    doc = {"items": items, "overall_status": "CANONICALIZATION_PASS", "article_id": article_id, "canonicalization_version": "mock", "source_level": source_level}
    with open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": {"status": "CANONICALIZATION_PASS"},
            "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}


def mock_expl_call_fn(user_message: str):
    import er019_family_x_kp_explanation_01 as kexp
    phrases = re.findall(r'phrase: "(.*?)"', user_message)
    parsed = {"explanations": [{"phrase": p, "english_explanation": "a plain way to say this in everyday life"} for p in phrases]}
    return parsed, kexp.MODEL, {"input_tokens": 100, "cached_input_tokens": 0, "output_tokens": 50}, "mock_expl"


# ------------------------------------------------------------
# 偽TTS
# ------------------------------------------------------------
def _write_tone(path, seconds):
    import numpy as np
    import er002_common as common
    os.makedirs(os.path.dirname(path), exist_ok=True)
    t = np.arange(int(common.SAMPLE_RATE * seconds)) / common.SAMPLE_RATE
    common.write_wav_float(path, (0.2 * np.sin(2 * np.pi * 220 * t)).astype("float32"), common.SAMPLE_RATE, 1)


def _dur(text, ja=False):
    return 0.6 + (len(text) / 7.0 if ja else len(text.split()) / 2.8)


def _entry(text, path, *, ja=False, slow=False, voice=None):
    d = _dur(text, ja)
    _write_tone(path, d * (1.06 if slow else 1.0))
    e = {"status": "OK", "path": path, "text": text, "asr_text": text, "disfluency_checked": True, "fallback_used": False,
         "instruction_type": "english_style_prefix_wide_margin", "style_prefix": "mock style",
         "attempts_log": [{"attempt": 1, "tts_model_id": "mock-tts", "voice": voice or "mock"}]}
    if slow:
        _write_tone(path.replace(".wav", "_original.wav"), d)
        e["slowdown_applied"] = True
        e["slowdown_info"] = {"src_duration_seconds": d, "dst_duration_seconds": d * 1.06, "slowdown_pct_target": 6.0}
    return e


@contextlib.contextmanager
def fake_tts(api: MockApi):
    """低レベルTTS生成関数を偽物に差し替える(終了時に必ず復元)。呼出ごとにAPI境界(STOP確認+カウンタ)を通す。"""
    import er003_v1_crosslevel_audio_02_common as crosslevel_common
    import er003_v1_n3_01_tts_generate as n3_tts
    import er003_v1_sing01_news_tail_fix as news_tail_fix
    import er003_v1_sing01_voice01_generate as voice01
    import er006_audio_cost_pilot_02_shared_narration as shared
    import er019_family_x_audio_production_runner_01 as xr
    import er121_family_y_audio_01 as ya

    def cur_voice():
        import er003_b1_p9a_audio as p9a
        return p9a.VOICE_NAME

    def eng(text, out_path, *a, **k):
        api.call("tts", os.path.basename(out_path))
        return _entry(text, out_path, voice=cur_voice())

    def news(text, out_path, *a, **k):
        api.call("tts", os.path.basename(out_path))
        return _entry(text, out_path, voice=cur_voice())

    def a2_slow(text, out_path, sub, *a, **k):
        api.call("tts", os.path.basename(out_path))
        return _entry(text, out_path, slow=True, voice=cur_voice())

    def a2_ja(text, out_path, sub, *a, **k):
        api.call("tts", os.path.basename(out_path))
        return _entry(text, out_path, ja=True)

    def eng_fb(text, out_path, sub, *a, **k):
        api.call("tts", os.path.basename(out_path))
        return _entry(text, out_path)

    def shared_b1(narration_dir, tts_backend=None, **k):
        out = {}
        for name, t in shared.FIXED_ENGLISH_TEXTS.items():
            api.call("tts_shared", name)
            e = _entry(t, f"{narration_dir}/{name}_charon.wav")
            out[name] = {**e, "reused": False, "master_audio_id": f"mock_{name}"}
        return out

    def shared_a2(narration_dir, tts_backend=None, **k):
        out = {}
        for name, t in shared.FIXED_ENGLISH_TEXTS.items():
            api.call("tts_shared", name)
            out[name] = {**_entry(t, f"{narration_dir}/{name}.wav"), "reused": False, "master_audio_id": f"mock_{name}"}
        for name, t in shared.FIXED_JAPANESE_TEXTS_A2_ONLY.items():
            api.call("tts_shared", name)
            out[name] = {**_entry(t, f"{narration_dir}/{name}.wav", ja=True), "reused": False, "master_audio_id": f"mock_{name}"}
        return out

    def kp_b1(kp, narration_dir, cached=None, tts_backend=None, style_profile="default"):
        res = {}
        for it in sorted(kp["items"], key=lambda x: x["rank"]):
            r = it["rank"]
            api.call("tts_kp", f"kp{r}")
            res[r] = {"english": _entry(it["used_form"], f"{narration_dir}/kp{r}_en.wav"),
                      "explanation": {**_entry("a plain way to say this in everyday life", f"{narration_dir}/kp{r}_explanation_en.wav"),
                                      "explanation_text": "a plain way to say this in everyday life"}}
        return res, {"items": {str(it["rank"]): {"status": "OK", "english_explanation": "a plain way to say this in everyday life"} for it in kp["items"]}}

    def kp_a2(kp, narration_dir, cached=None, tts_backend=None, style_profile="default"):
        res = {}
        for i, it in enumerate(sorted(kp["items"], key=lambda x: x["rank"]), start=1):
            r = it["rank"]
            api.call("tts_kp", f"kp{r}")
            res[r] = {"english": _entry(it["used_form"], f"{narration_dir}/kp{r}_en.wav"),
                      "japanese_meaning": {**_entry(it.get("japanese_gloss", "意味"), f"{narration_dir}/meaning_{i}.wav", ja=True),
                                           "canonical_text": it.get("japanese_gloss", "意味")}}
        return res

    patches = [(voice01, "generate_charon_english", eng), (news_tail_fix, "generate_news_narration_wide_margin", news),
               (n3_tts, "generate_a2_segment_with_slowdown", a2_slow), (n3_tts, "generate_a2_japanese_with_reading_safety", a2_ja),
               (crosslevel_common, "generate_english_segment_with_fallback", eng_fb),
               (shared, "ensure_all_shared_narration_b1", shared_b1), (shared, "ensure_all_shared_narration_a2", shared_a2),
               (xr, "_generate_key_phrase_segments_b1", kp_b1), (xr, "_generate_key_phrase_segments_a2", kp_a2)]
    saved = [(o, n, getattr(o, n)) for o, n, _ in patches]
    for o, n, f in patches:
        setattr(o, n, f)
    try:
        yield
    finally:
        for o, n, f in saved:
            setattr(o, n, f)
    _ = ya


def default_hooks(api: MockApi) -> dict:
    return {"text_core": FakeTextCore(api),
            "kp_fn": api.wrap("kp", lambda *a, **k: mock_kp_fn(*a, n_max=8, **k)),
            "expl_call_fn": api.wrap("kp_expl", mock_expl_call_fn),
            "tts_patch": lambda: fake_tts(api)}
