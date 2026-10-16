# -*- coding: utf-8 -*-
"""AUW 委任_13: A3是正の最小実音声 runtime evidence(Azure STTのみ。TTS生成0・OpenAI ASR 0=Primary転写はmock)。

Production コードは無編集。共有 state は evidence_13/<part> 配下へ隔離(06b begin/finish を再利用)。有料APIは --execute 指定時のみ。
監督ループ・自動再試行なし。1 part 1 回のみ実行(再起動しない)。STOP: <out>/STOP と stop_scope_check_01。

  a3_pos : 既存の合格wav(EN 1本・JA 1本)+ Primary転写を「原稿+max_len超の尾部」へ差し替えたmock -> 実Azure -> Production adapter
           (evaluate_attempt_with_cascade_detail / evaluate_attempt_ja_with_cascade_detail, attempt_ctx={'max_len':...})。
           期待: Secondary救済(PASS_WITH_WARNING)、audit.length.adopted_from=secondary・adopted_ok=True、final_length_ok=True、
           PRIMARY_LENGTH_EXCESS付与。
  a3_neg : 既存wav 2本をローカル連結した音声 + 片方の原稿 + Primary転写=連結内容(mock) -> 実Azure。期待: NG_BOTH(品質維持)。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_13.py <a3_pos|a3_neg> --out <dir> --budget-jpy 2 [--execute]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import wave

import er078_auw_runtime_evidence_06 as e6
import er078_auw_runtime_evidence_06b as b6

ROOT = e6.ROOT
EV = "er058_output/unified_all_roles_production_wiring_01/evidence_13"
b6.EV = EV
b6.LEDGER = f"{EV}/cost/spend_ledger.jsonl"
b6.CAP_JPY = 2.0   # 委任_13 Guardrail(累計)。T-3: 到達・接近時は理由を記録して判断(自動継続しない)
e6.MANAGED_IDS[:] = ["AUW-06", "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01", "AUW-13"]

# 既存の合格wav(main dir の evidence_06 出力。gitignore済み*.wav)。状態=PASS、原稿は tts_generation_results.json の text。
SRC_ROOT = os.environ.get("AUW13_WAV_SRC_ROOT", r"C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\evidence_06")
EN_SRC = ("z_prod_path", "full_story_part1_c2")        # "Why did you wait twenty minutes?" (PASS)
EN_SRC2 = ("z_prod_path", "full_story_part1_c1")       # 連結用の別clip(PASS)。初回a3_negは数値(nine/twenty)差でP1停止しSecondary不呼出だったため、数値・否定の無いclip(NEG_*)へ差替
NEG_CANON = ("../evidence_06b/lega/theme/a2", "point_one_heading")   # "Why prices change slowly"(PASS)
NEG_OTHER = ("../evidence_06b/lega/theme/a2", "topic_intro")          # "Today's topic is Cheaper Beans, Same Price Tag."(PASS)
JA_SRC = ("z_ja_prod_path", "japanese_title")          # PASS(Secondaryが『9か月』を『9カ月』と転写しJA許容集合外=NG_BOTH。長さとは無関係の既存挙動を観測、evidence_13/a3_pos 参照)
JA_SRC2 = ("../evidence_06b/lega/theme/a2", "comment_4")  # PASS。a3_pos_ja で使用(初回は preview[お話しします→お話します の送り仮名差でJA許容集合外]。長さと無関係のためclipを差替)
TAIL_EN = " and so on and so forth and so on and so forth"
TAIL_JA = "そしてさらにまたまたたくさんの余計なことばが続きます"


def _text_and_wav(src):
    run, seg = src
    base = f"{SRC_ROOT}/{run}" if run.startswith("..") else f"{SRC_ROOT}/{run}/run/a2"
    d = json.load(open(f"{base}/audit/tts_generation_results.json", encoding="utf-8"))
    node = d["segments"][seg]
    assert node.get("status") == "OK" and (node.get("asr_judgement") or {}).get("state") == "PASS", (src, node.get("status"))
    wav = f"{base}/narration/{seg}.wav"
    assert os.path.exists(wav), wav
    return node["text"], wav


def _concat_wavs(a, b, dst):
    with wave.open(a, "rb") as wa, wave.open(b, "rb") as wb:
        assert wa.getparams()[:3] == wb.getparams()[:3], (wa.getparams(), wb.getparams())
        params = wa.getparams()
        frames = wa.readframes(wa.getnframes()) + wb.readframes(wb.getnframes())
    with wave.open(dst, "wb") as w:
        w.setparams(params)
        w.writeframes(frames)


def _summ(d, final_fn):
    aj = d.get("asr_judgement") or {}
    sec = aj.get("secondary") or {}
    return {"verified": d.get("verified"), "state": aj.get("state"), "reason": aj.get("reason_code"),
            "warnings": aj.get("warnings"), "length": aj.get("length"),
            "primary_text": (aj.get("primary") or {}).get("text"), "secondary_called": sec.get("called"),
            "secondary_text": sec.get("text"), "secondary_accepted": sec.get("accepted"),
            "exclusion_rule": aj.get("exclusion_rule"), "final_length_ok": final_fn(d),
            "cost": aj.get("cost")}


def _run_guarded(res, key, fn):
    try:
        res.setdefault("stage_result", {})[key] = "OK"
        return fn()
    except SystemExit as e_:
        res["stage_result"][key] = f"SystemExit({e_.code})"
    except Exception as e_:  # noqa: BLE001
        import traceback
        res["stage_result"][key] = f"{type(e_).__name__}: {str(e_)[:500]}"
        res["traceback"] = traceback.format_exc()[-2000:]
    return None


def _prepare_inputs(out):
    os.makedirs(f"{out}/input", exist_ok=True)


def run_part(part, execute, budget):
    out, r77, before, snap0, res, meter, ok = b6.begin(part, budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er006_secondary_asr_01 as sec
    import er007_ja_secondary_asr_01 as ja
    import er078_asr_unified_judge_01 as uj
    import er078_secondary_run_scope_01 as scope
    res["a3_reeval_const"] = uj.A3_SECONDARY_LENGTH_REEVAL
    _prepare_inputs(out)
    plan = []
    if part == "a3_pos_ja":
        ja_text, ja_src = _text_and_wav(JA_SRC2)
        ja_wav = f"{out}/input/ja_pos2.wav"
        shutil.copyfile(ja_src, ja_wav)
        cases = [("ja_pos2", "ja", ja_text, ja_wav, ja_text + TAIL_JA, len(ja_text) + 15)]
    elif part == "a3_pos":
        en_text, en_src = _text_and_wav(EN_SRC)
        ja_text, ja_src = _text_and_wav(JA_SRC)
        en_wav, ja_wav = f"{out}/input/en_pos.wav", f"{out}/input/ja_pos.wav"
        shutil.copyfile(en_src, en_wav)
        shutil.copyfile(ja_src, ja_wav)
        cases = [("en_pos", "en", en_text, en_wav, en_text + TAIL_EN, len(en_text) + 15),
                 ("ja_pos", "ja", ja_text, ja_wav, ja_text + TAIL_JA, len(ja_text) + 15)]
    else:
        en_text, en_src = _text_and_wav(NEG_CANON)
        other_text, other_src = _text_and_wav(NEG_OTHER)
        cat = f"{out}/input/en_neg_concat.wav"
        _concat_wavs(other_src, en_src, cat)
        # canonical=片方(c2)の原稿。Primary転写は連結内容そのもの(mock)=実ASRなら出る転写の想定
        cases = [("en_neg", "en", en_text, cat, other_text + " " + en_text, len(en_text) + 15)]
    for cid, lang, text, wav, primary_mock, mx in cases:
        plan.append({"id": cid, "lang": lang, "canonical": text, "wav": wav, "primary_mock": primary_mock,
                     "primary_len": len(primary_mock), "max_len": mx})
    res["plan"] = plan
    if ok:
        @scope.with_secondary_run
        def go():
            rows = []
            for cid, lang, text, wav, primary_mock, mx in cases:
                actx = {"is_last_slot": True, "max_len": mx, "segment_key": f"a3evidence/{cid}"}
                if lang == "en":
                    d = {}
                    sec.evaluate_attempt_with_cascade(text, primary_mock, [], wav, language="en-US", ledger_phrases=[],
                                                      cascade_enabled=True, detail_out=d, attempt_ctx=actx)
                    length_ok = len(primary_mock) <= mx
                else:
                    d = {}
                    length_ok = len(primary_mock) <= mx
                    ja.evaluate_attempt_ja_with_cascade(text, primary_mock, wav, cascade_enabled=True, length_ok=length_ok,
                                                       attempt_ctx=actx, detail_out=d)
                s = _summ(d, lambda x: uj.final_length_ok(length_ok, x))
                s.update(id=cid, lang=lang, caller_primary_length_ok=length_ok, max_len=mx)
                s["caller_verified_after_and"] = bool(d.get("verified")) and s["final_length_ok"]
                rows.append(s)
            return rows
        rows = _run_guarded(res, part, go)
        res["rows"] = rows
    b6.finish(out, r77, before, snap0, res, meter, extra_print=("rows", "a3_reeval_const"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["a3_pos", "a3_pos_ja", "a3_neg"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--cap-jpy", type=float, default=2.0)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    b6.CAP_JPY = a.cap_jpy
    assert a.out.replace("\\", "/").rstrip("/") == f"{EV}/{a.part}", f"--out must be {EV}/{a.part}"
    run_part(a.part, a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()
