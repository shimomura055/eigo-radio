# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 M6: 実音声E3(委任_03)用のNG注入ハーネス(test/evidence専用。Productionのどのmoduleからも参照しない)。

目的: 実TTS・実ASR経路は変えずに、指定clipの指定attempt番号(通算n)だけ『ASR内容不一致NG』として扱い、
LR境界(③まで3回NG→LR→④⑤⑥)を実音声で通す。注入した事実は全て `INJECTED` と明記してjsonlに残す(実NGと混同しない・成果物の根拠にしない)。

仕組み(Productionコードは1行も変更しない。実行時のmonkeypatchのみ):
  * `DialogueAttemptPolicy.before_attempt` を包み、clipごとの現在の通算attempt番号 n を知る。
  * `asr_routing.transcribe`  : 注入対象(clip, n)では実Whisperを呼ばず、doctored転写(canonicalから1語を壊した文)を返す(ASR費用も出ない)。
  * `secondary_asr.evaluate_attempt_with_cascade` : 注入対象では実判定を呼ばず『TRUE_CONTENT_MISMATCH・stop_retrying=False・asr_judgement.injected=True』を返す。
    対象外attemptは実関数へそのまま委譲する(通常のASR判定)。
使い方: `with NgInjector(...).patched(): <runnerを同一process内で起動>`。単独起動はしない(`--help`のみ)。
隔離保証: `er122_fz_ctx_policy_lr2_test_01.py::test_m6_*` が、Production `er*.py` がこのファイル名・INJECTEDマーカーを参照しないことをAST/Grepで確認する。
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
import time
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

MARKER = "INJECTED"
REASON = "INJECTED_NG"


class _InjectedCls:
    """val.ClassificationResult 互換の最小オブジェクト(呼出側が読む属性だけ)。"""

    def __init__(self):
        self.classification = "TRUE_CONTENT_MISMATCH"
        self.connected_speech_info = None
        self.should_pass = False
        self.should_retry = True
        self.reason = REASON
        self.normalized_ratio = 0.0
        self.protected = None


def doctor_text(canonical: str, word: str | None = None) -> str:
    """canonical から1語を『別の実在しそうな語』へ壊した転写を作る(LR入力=NG span用)。wordが無ければ最初の5文字以上の語。"""
    toks = canonical.split(" ")
    idx = next((i for i, t in enumerate(toks) if (word and t.strip(".,?!").lower() == word.lower()) or (not word and len(t.strip(".,?!")) >= 5)), 0)
    core = toks[idx].strip(".,?!")
    swapped = core[:-1] + ("e" if not core.endswith("e") else "a")
    toks[idx] = toks[idx].replace(core, swapped)
    return " ".join(toks)


class NgInjector:
    """clip_id と {通算attempt番号: doctored転写(None=doctor_textで自動)} を受け取る。"""

    def __init__(self, clip_id: str, ng_attempts: dict, log_path: str, manifest_path: str | None = None, canonical_text: str | None = None):
        self.clip_id = clip_id
        self.ng_attempts = {int(k): v for k, v in ng_attempts.items()}
        self.log_path = log_path
        self.manifest_path = manifest_path or (log_path + ".manifest.json")
        self.canonical_text = canonical_text
        self.current_n: dict = {}          # wav_path -> 通算n(before_attemptが更新)
        self.records: list = []

    # ---- 内部 ----
    def _is_target(self, path: str) -> bool:
        return str(path).replace("\\", "/").endswith(f"/{self.clip_id}.wav") or os.path.basename(str(path)) == f"{self.clip_id}.wav"

    def _n_of(self, path: str):
        return self.current_n.get(str(path).replace("\\", "/"))

    def _log(self, rec: dict) -> None:
        rec = {MARKER: True, "clip_id": self.clip_id, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), **rec}
        self.records.append(rec)
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def write_manifest(self) -> None:
        os.makedirs(os.path.dirname(self.manifest_path) or ".", exist_ok=True)
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump({MARKER: True, "note": "この実行はNG注入ハーネスを使用。注入されたNG判定は実NGではなく、成果物の品質根拠にしない。",
                       "clip_id": self.clip_id, "ng_attempts": sorted(self.ng_attempts), "log": self.log_path, "records": len(self.records)}, f, ensure_ascii=False, indent=2)

    # ---- patch ----
    @contextlib.contextmanager
    def patched(self):
        import er006_asr_provider_routing_01 as asr_routing
        import er006_secondary_asr_01 as secondary_asr
        import er122_fz_ctx_policy_01 as pol

        real_before = pol.DialogueAttemptPolicy.before_attempt
        real_transcribe = asr_routing.transcribe
        real_eval = secondary_asr.evaluate_attempt_with_cascade
        inj = self

        def before_attempt(policy, attempt, max_attempts, out_path):
            r = real_before(policy, attempt, max_attempts, out_path)
            if isinstance(r, dict) and not r.get("stop"):
                inj.current_n[str(out_path).replace("\\", "/")] = int(policy.st["n_started"])
            return r

        def transcribe(path, language="en-US"):
            n = inj._n_of(path)
            if inj._is_target(path) and n in inj.ng_attempts:
                text = inj.ng_attempts[n] or doctor_text(inj.canonical_text or "")
                inj._log({"kind": "transcribe", "n": n, "doctored_text": text, "real_asr_called": False})
                return (text, None)
            return real_transcribe(path, language=language)

        def evaluate(canonical_text, asr_text, prior_results, wav_path, *a, **k):
            n = inj._n_of(wav_path)
            if inj._is_target(wav_path) and n in inj.ng_attempts:
                d = k.get("detail_out")
                if isinstance(d, dict):
                    d["asr_judgement"] = {"state": "NG_BOTH", "injected": True, "reason": REASON}
                    d["verified"] = False
                inj._log({"kind": "evaluate", "n": n, "forced": "TRUE_CONTENT_MISMATCH", "asr_text": asr_text})
                return False, False, _InjectedCls()
            return real_eval(canonical_text, asr_text, prior_results, wav_path, *a, **k)

        with contextlib.ExitStack() as st:
            st.enter_context(mock.patch.object(pol.DialogueAttemptPolicy, "before_attempt", before_attempt))
            st.enter_context(mock.patch.object(asr_routing, "transcribe", transcribe))
            st.enter_context(mock.patch.object(secondary_asr, "evaluate_attempt_with_cascade", evaluate))
            try:
                yield self
            finally:
                self.write_manifest()


if __name__ == "__main__":
    print(__doc__)
