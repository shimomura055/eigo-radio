# ============================================================
# er047_tts_fixed_shell_number_three_five_retrial_01.py
# TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01(Trial、Production実装なし)
# ============================================================
# 性質: Trial専用script。Production正式path(er0*.py既存ファイル)は一切
# 変更しない。既決Champion(TRIAL-02、`user_test/fixed_shell_champion_
# trial_02/index.html`)のnum_one(Candidate C系統)/num_two(Candidate B
# 系統)/num_four(Candidate C系統)と同一のmodel(gemini-3.8-flash-lite-tts)
# ・同一voice(Charon)・同一style文言(`er043_tts_fixed_shell_master_
# champion_trial_02.STYLE_TEXT_GROUP3_B`/`STYLE_TEXT_GROUP3_C`を無変更で
# import)を使い、num_three/num_fiveのみ複数take(既定4)を新規生成する。
# 目的はモデル比較ではなく、採用済みOne/Two/Fourと統一感のある
# Three/Fiveの良いtakeを複数提示すること(delegation本文どおり)。
#
# 生成関数は既存Production関数(voice01.generate_charon_english、
# review_lock.guarded_generateのASR検証3attempt cascade+Human Review
# Lockを含む)をそのまま呼ぶ(独自retry追加なし)。Master Audio Storeは
# Trial専用path(--trial-store配下)へ実行時モンキーパッチで隔離する
# (er040の既存trial_master_audio_store()をそのまま流用、独自再実装しない)。
#
# 対象設計書: docs/pm/design_tts_fixed_shell_number_three_five_retrial_01.md
from __future__ import annotations

import argparse
import os

import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er019_family_x_audio_production_runner_01 as fx_runner
import er040_tts_fixed_shell_master_champion_trial_01 as champ1
import er043_tts_fixed_shell_master_champion_trial_02 as champ2

MANAGEMENT_ID = "TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01"

# 再Trial対象(delegationにより num_three/num_five のみ)。
TARGET_PHRASE_NAMES = ["num_three", "num_five"]

# 採用済みOne(C系統)/Two(B系統)/Four(C系統)のスタイル系統。B/C両方とも
# 採用実績があるため、両方で生成する(design doc §3)。style文言そのものは
# er043の既存定数をそのままimportして使う(新規文言は考案しない)。
STYLE_TEXT_BY_CANDIDATE = {
    "B": champ2.STYLE_TEXT_GROUP3_B,
    "C": champ2.STYLE_TEXT_GROUP3_C,
}
# 採用済みOne/Two/Fourがそれぞれどのstyle系統を使ったか(design doc §2、
# 参考ページ表示用の記録のみ、本scriptの生成ロジックには使わない)。
ADOPTED_STYLE_SYSTEM_BY_ADOPTED_PHRASE = {
    "num_one": "C", "num_two": "B", "num_four": "C",
}

STYLE_INSTRUCTION_ID_BY_CANDIDATE = {
    "B": "trial_ch2_num_set_style_b",
    "C": "trial_ch2_num_set_style_c",
}
STYLE_INSTRUCTION_VERSION = "v1"  # champ2と同一version文字列(出自を保つ)


def _take_level(take: int) -> str:
    # Master Audio Keyのcache identityのみをtakeごとに分離する(level
    # フィールド)。style文言・model・voiceは一切変えない(design doc §4)。
    return f"retrial01_take{take}"


def ensure_take(name: str, candidate: str, take: int, out_dir: str) -> dict:
    if name not in shared_narration.FIXED_ENGLISH_TEXTS:
        raise ValueError(f"未知のphrase名: {name}")
    if candidate not in STYLE_TEXT_BY_CANDIDATE:
        raise ValueError(f"未知のstyle系統: {candidate}")
    text = shared_narration.FIXED_ENGLISH_TEXTS[name]
    style_text = STYLE_TEXT_BY_CANDIDATE[candidate]
    style_id = STYLE_INSTRUCTION_ID_BY_CANDIDATE[candidate]
    out_path = (f"{out_dir}/{MANAGEMENT_ID}_{name}_style{candidate}/take{take}"
                f"/narration/{name}.wav")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    key = store.MasterAudioKey(
        language="en", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
        canonical_text=text, level=_take_level(take),
        style_instruction_id=style_id, style_instruction_version=STYLE_INSTRUCTION_VERSION,
    )
    with cl.segment_context(f"take{take}_cand{candidate}_{name}"):
        result = store.get_or_generate(
            key, out_path,
            lambda p: voice01.generate_charon_english(
                text, p, style_prefix_override=style_text, tts_backend="speech_metadata_flash_lite"))
    result["candidate_style_system"] = candidate
    result["style_prefix_used"] = style_text
    result["canonical_text"] = text
    result["take"] = take
    result["role"] = "NUMBER_LABEL"
    result["group"] = "group3_num_set"
    return result


def _load_existing_results(out_dir: str) -> dict:
    path = f"{out_dir}/retrial_results.json"
    if os.path.exists(path):
        return champ1.load_json(path)
    return {"management_id": MANAGEMENT_ID, "phrases": {}}


def run_selected(out_dir: str, trial_store_dir: str, phrases: list[str],
                  styles: list[str], takes: int) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    results = _load_existing_results(out_dir)
    results.setdefault("phrases", {})

    with champ1.trial_master_audio_store(trial_store_dir):
        for name in phrases:
            results["phrases"].setdefault(name, {})
            for candidate in styles:
                results["phrases"][name].setdefault(candidate, {})
                for take in range(1, takes + 1):
                    results["phrases"][name][candidate][str(take)] = \
                        ensure_take(name, candidate, take, out_dir)

    champ1.save_json(f"{out_dir}/retrial_results.json", results)
    return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phrases", default=",".join(TARGET_PHRASE_NAMES),
                         help="comma区切りのphrase名(既定はnum_three,num_five)")
    parser.add_argument("--styles", default="B,C",
                         help="comma区切りのstyle系統candidate ID(既定は採用済み"
                              "One/Two/Fourの両系統B,C)")
    parser.add_argument("--takes", type=int, default=4)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--trial-store", required=True)
    parser.add_argument("--budget-jpy", type=float, required=True)
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    phrases = [p.strip() for p in args.phrases.split(",") if p.strip()]
    for p in phrases:
        if p not in TARGET_PHRASE_NAMES:
            raise ValueError(f"本Trialの対象外のphrase名: {p}(対象={TARGET_PHRASE_NAMES})")
    styles = [c.strip().upper() for c in args.styles.split(",") if c.strip()]
    for c in styles:
        if c not in STYLE_TEXT_BY_CANDIDATE:
            raise ValueError(f"未知のstyle系統: {c}")
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")

    with cl.logging_context(MANAGEMENT_ID, "number_retrial"):
        run_selected(args.out_dir, args.trial_store, phrases, styles, args.takes)

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[ER047-NUMBER-RETRIAL] phrases={phrases} styles={styles} takes={args.takes} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")
    fx_runner.assert_budget_ok(args.out_dir, args.budget_jpy, "after number three/five retrial")


if __name__ == "__main__":
    main()
