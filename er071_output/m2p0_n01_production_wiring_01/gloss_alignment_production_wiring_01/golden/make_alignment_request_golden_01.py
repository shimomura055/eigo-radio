"""KGCPW OF-KGCPW-01: corrected gloss-alignment API request golden (撤去前HEADで先に固定し、撤去後に同じshaを要求する)。
fake clientで responses.create の全kwargs(model/reasoning/text.format全体/input)を捕捉し、
json.dumps(ensure_ascii=False)(sort_keysなし=順序込み)のsha256を取る。API 0・TTS 0。
撤去前/後どちらのモジュール形でも動くよう、modeやschema名の有無はgetattr/inspectで吸収する。"""
import argparse
import hashlib
import inspect
import json
import os
import sys
from types import SimpleNamespace

os.environ["EIGO_KP_GLOSS_ALIGNMENT"] = "1"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 4)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er003_key_words_gloss_alignment as ga  # noqa: E402

MODEL = "golden-fixed-model"
ARTICLES = {
    "std_a2": "Reporters said the film was based on interviews with local farmers. The team did not give up easily.",
    "adv_b1b": "The documentary, which was based on interviews with former employees, showed how managers fall into a pattern.",
}


def _items():
    # P1型(不整合gloss) + P2型(整合済みgloss)を同一callに含む固定item集合
    return {"items": [
        {"rank": 1, "display_phrase": "based on", "key_phrase": "based on interviews",
         "japanese_gloss": "～をもとにした", "source_sentence": "the film was based on interviews with local farmers.",
         "kp_extends_beyond_candidate": True},
        {"rank": 2, "display_phrase": "give up", "key_phrase": "give up easily",
         "japanese_gloss": "簡単にあきらめる", "source_sentence": "The team did not give up easily.",
         "kp_extends_beyond_candidate": True},
        {"rank": 3, "display_phrase": "take part", "key_phrase": "take part",
         "japanese_gloss": "参加する", "source_sentence": "x", "kp_extends_beyond_candidate": False},
    ]}


def _fake_client(captured):
    class _Resp:
        def __init__(self, text):
            self.model = MODEL
            self.output_text = text
            self.id = "resp_golden"
            self.usage = SimpleNamespace(input_tokens=1, output_tokens=1,
                                         input_tokens_details=SimpleNamespace(cached_tokens=0))

    class _Responses:
        def create(self, **kwargs):
            captured.append(kwargs)
            payload = {"items": [
                {"rank": 1, "current_gloss_consistent": False, "japanese_gloss": "インタビューをもとにした",
                 "added_word_mappings": [{"english_word": "interviews", "japanese_span": "インタビュー"}],
                 "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "r1"},
                {"rank": 2, "current_gloss_consistent": True, "japanese_gloss": "簡単にあきらめる",
                 "added_word_mappings": [{"english_word": "easily", "japanese_span": "簡単に"}],
                 "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "r2"},
            ]}
            return _Resp(json.dumps(payload, ensure_ascii=False))

    return SimpleNamespace(responses=_Responses())


def capture():
    out = {}
    for label, article in ARTICLES.items():
        captured = []
        client = _fake_client(captured)
        schema = getattr(ga, "GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED", None) or ga.GLOSS_ALIGNMENT_JSON_SCHEMA

        def factory(msg, _c=client, _s=schema):
            return ga.make_alignment_fn(msg, client=_c, model=MODEL, schema=_s)

        kw = {"enabled": True}
        if "mode" in inspect.signature(ga.align_glosses).parameters:
            kw["mode"] = "corrected"
        r = ga.align_glosses(_items(), article, factory, **kw)
        assert r["status"] == "ALIGN_PASS", r["status"]
        assert len(captured) == 1, len(captured)
        blob = json.dumps(captured[0], ensure_ascii=False)
        out[label] = {"kwargs": captured[0], "sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest()}
    out["combined_sha256"] = hashlib.sha256(
        "".join(out[k]["sha256"] for k in ARTICLES).encode("utf-8")).hexdigest()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = capture()
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("combined_sha256", res["combined_sha256"])
