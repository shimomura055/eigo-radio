"""FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01: 保存済みCoffee full_story_part2各attempt wavを
ローカルfaster-whisper(無料、API課金0)で独立再文字起こしし、既存Validator(classify_asr_match)で
再判定する。read-only(evidence_snapshotを読むだけ、Production codeは呼ぶだけで変更しない)。
さらにattempt1の6%減速(ffmpeg、無料)を再現し、減速後の音声もローカルASRで確認する。
"""
import io, json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import er006_preprod_hardening_01_validation as val
import er003_v1_n3_01_tts_generate as n3
import er008_a2_postprocess_slowdown_01 as slow
import er008_disfluency_qa_18 as dq

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er056_output", "en_asr_confirm_retry_redesign_01")
S = os.path.join(OUT, "evidence_snapshot")


def local_text(path, size):
    # 本番のword-level join(" ".join)は "6.1%" を "6. 1%" 等に分割しうるため、検証ではsegment text
    # (faster-whisperのsegment.text、連結済み)を使う。モデルはProductionのCS Layerと同じfaster-whisper。
    model = dq._get_model(size)
    segments, _info = model.transcribe(path, language="en", condition_on_previous_text=False, vad_filter=False)
    t = " ".join(seg.text.strip() for seg in segments).strip()
    # "6.1%"/"U.S."が "6 .1 %"/"U .S." と分かち書きされることがあるため、句読点・%直前の空白だけ除去する
    # (語の内容は変えない、検証用の表記整形のみ)。
    return re.sub(r"\s+([.%,?!])", lambda m: m.group(1), t)  # noqa


def main(sizes=("small", "medium")):
    parts = json.load(open(os.path.join(S, "a2_parts.json"), encoding="utf-8"))
    tts_input = n3.tts_safe_news_en(parts["part2"])
    targets = {
        "attempt1_orig(15:13)": os.path.join(S, "a2_attempts", "full_story_part2_attempt1_customf1837a73.wav"),
        "attempt2(15:16)": os.path.join(S, "a2_attempts", "full_story_part2_attempt2_customf1837a73.wav"),
        "attempt3(15:18)": os.path.join(S, "a2_attempts", "full_story_part2_attempt3_customf1837a73.wav"),
        "attempt4_minimal_fallback(15:31)": os.path.join(S, "a2_attempts", "full_story_part2_attempt4_minimalfallback.wav"),
        "final_LR(15:35)": os.path.join(S, "a2_final", "full_story_part2.wav"),
    }
    tmpdir = tempfile.mkdtemp(prefix="er056_stretch_")
    stretched = os.path.join(tmpdir, "attempt1_stretched.wav")
    info = slow.apply_a2_slowdown(targets["attempt1_orig(15:13)"], stretched)
    targets["attempt1_stretched6pct(local-reproduction)"] = stretched
    results = {"stretch_info": info, "rows": []}
    for name, path in targets.items():
        for size in sizes:
            t = local_text(path, size)
            canon = tts_input
            if name.startswith("final_LR"):
                # LR後は原稿が書き換わっている(canonical_text_before_local_rewriteと別)
                lr = json.load(open(os.path.join(S, "local_rewrite_recovery_full_story_part2.json"), encoding="utf-8"))
                canon = lr["selection"]["selected"]["rewritten_segment"]
            c = val.classify_asr_match(canon, t, segment_id="full_story_part2")
            diffs = [(d["canonical"], d["asr"]) for d in c.protected.content_word_diffs]
            results["rows"].append({"audio": name, "local_model": size, "classification": c.classification,
                                    "should_pass": c.should_pass, "ratio": round(c.normalized_ratio, 4),
                                    "diffs": diffs, "text": t})
            print(name, size, c.classification, round(c.normalized_ratio, 4), diffs[:6], flush=True)
    json.dump(results, open(os.path.join(OUT, "local_wav_check_01.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
