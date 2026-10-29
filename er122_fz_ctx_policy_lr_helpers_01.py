# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_02: ZセリフLR(最大TTS6回+LR1回+待機2回)のoffline test用helper(Production codeではない。API 0)。

正式経路 `er063._run_tts_stage_impl` -> `prepare_dialogue_ctx` -> 実の `real_generators()["dialogue"]`(=generate_dialogue_ctx) -> 共有ループ/Adv外側ループを、
fake TTS/ASR(er122_fz_ctx_fakes_01.World)・fake LLM(notes)・fake LR候補(er020のLuna呼出だけ差替え。候補の7 Gate・局所性・全文性・candidate_filterは実コード)で駆動する。
"""
from __future__ import annotations

import contextlib
import json
import os

import er122_fz_ctx_fakes_01 as fk

STORY = "the_monkeys_paw"
C3_ID = "full_story_part1_c3"
C3_TEXT = ("Are you really sure that you want to open the door so late tonight, Mr. White, after everything that happened to us here in this quiet house?")
C3_ASR_NG = C3_TEXT.replace("sure", "shore")            # LR入力になるASR転写(NG span: sure -> shore)
C2_TEXT = "I am here."
OK = (True, False, "EXACT_MATCH")
NG = (False, False, "TRUE_CONTENT_MISMATCH")
STOPRETRY = (False, True, "TRUE_CONTENT_MISMATCH")


class TWorld(fk.World):
    """World + 判定ごとのasr_judgement.state指定(技術STOP・反復検査のみNG等の再現)とNG時の転写指定。

    eval spec = (verified_content, stop_retrying, classification[, state[, asr_text]])。state既定: verified->PASS / NG->NG_BOTH。"""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.asr_by_eval = {}          # eval index -> asr_text
        self.eval_log = []

    def evaluate(self, text, asr_text, classification_history, out_path, **kw):
        i = self.eval_i
        spec = self.eval_script[i] if i < len(self.eval_script) else (False, False, "X")
        r = super().evaluate(text, asr_text, classification_history, out_path, **kw)
        d = kw.get("detail_out")
        if isinstance(d, dict):
            state = spec[3] if len(spec) > 3 else ("PASS" if spec[0] else "NG_BOTH")
            d["asr_judgement"] = {"state": state, "fake": True}
        self.eval_log.append({"i": i, "text": text, "asr_text": asr_text, "slot": (kw.get("attempt_ctx") or {}).get("slot"), "verified": spec[0]})
        return r

    @contextlib.contextmanager
    def patched(self):
        import er006_asr_provider_routing_01 as asr_routing
        with super().patched():
            real = asr_routing.transcribe

            def transcribe(path, language="en-US"):
                # eval_iは『これから行う判定の通番』。直前のTTSに対応する転写を返す(NG判定の試行は差分を持つ転写)
                t = self.asr_by_eval.get(self.eval_i, self.asr_text)
                return (t, None)
            asr_routing.transcribe = transcribe
            try:
                yield self
            finally:
                asr_routing.transcribe = real


class FakeLR:
    """er020のLuna呼出(候補生成・局所QA)だけを差し替える。候補の全文性/7 Gate/局所性/candidate_filter/選定は実コード。"""

    def __init__(self, candidates_fn=None, qa_fail_ids=()):
        self.gen_calls = []
        self.qa_calls = []
        self.candidates_fn = candidates_fn or self.default_candidates
        self.qa_fail_ids = set(qa_fail_ids)

    @staticmethod
    def default_candidates(canonical, ng_span):
        # NG span(sure)を言い換える最小書換え
        return [{"id": "c1", "rewritten_segment": canonical.replace("really sure", "really certain"), "changed_span_before": "sure", "changed_span_after": "certain",
                 "rewrite_type": "single_word_swap", "rationale": "synonym"},
                {"id": "c2", "rewritten_segment": canonical.replace("really sure", "quite sure"), "changed_span_before": "really sure", "changed_span_after": "quite sure",
                 "rewrite_type": "phrase", "rationale": "phrase"}]

    def install(self, monkeypatch):
        import er020_tts_retry_local_rewrite_01 as er020

        def gen(client, role, canonical, ng_span, cb, ca, n=5):
            self.gen_calls.append({"canonical": canonical, "ng_span": ng_span, "role": role})
            return {"candidates": self.candidates_fn(canonical, ng_span), "_model_id": "fake-luna"}

        def qa(client, role, canonical, candidates, cb, ca):
            self.qa_calls.append([c["id"] for c in candidates])
            keys = ("meaning_preserved", "role_preserved", "fact_non_contradiction", "context_connection", "natural_english")
            return {"evaluations": [{"candidate_id": c["id"], **{k: {"pass": c["id"] not in self.qa_fail_ids, "reason": "fake"} for k in keys}} for c in candidates],
                    "_model_id": "fake-luna"}
        monkeypatch.setattr(er020, "call_luna_candidate_gen", gen)
        monkeypatch.setattr(er020, "call_luna_local_qa", qa)
        monkeypatch.setattr(er020.b1s, "get_client", lambda: object())
        # LR成果物(er011_output/local_rewrite_recovery)・履歴はtmpへ(リポジトリに書かない)
        return self


def load_state(run_dir: str, level: str, clip: str = C3_ID) -> dict:
    return json.load(open(f"{run_dir}/{level}/audit/dialogue_ctx_attempt_state.json", encoding="utf-8"))["clips"][clip]


def load_lock(run_dir: str, level: str, clip: str = C3_ID) -> dict:
    return json.load(open(f"{run_dir}/{level}/audit/review_lock_state.json", encoding="utf-8"))[clip]


def results(run_dir: str, level: str) -> dict:
    return json.load(open(f"{run_dir}/{level}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]


def history_events(history_path: str, action: str | None = None) -> list:
    if not os.path.exists(history_path):
        return []
    out = []
    for line in open(history_path, encoding="utf-8"):
        line = line.strip()
        if line:
            d = json.loads(line)
            if action is None or d.get("action") == action:
                out.append(d)
    return out
