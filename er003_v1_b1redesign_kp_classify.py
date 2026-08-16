# ER-003-B1-REDESIGN-AUDIO-01: kp1(strait/海峡)のASR homophone ambiguity分類
# (IRAN01 B1・ADD03と同種の既知パターン。TTS音声自体は正常と推定されるが、
# 機械的ASR一致検証だけでは確定できない)
import json

import er003_v1_b1redesign_audio_scaffold_generate as scaf

with open(f"{scaf.OUT_DIR}/audit/key_phrase_generation_results.json", encoding="utf-8") as f:
    results = json.load(f)

results["1"]["english"]["status"] = "ACCEPTED_PENDING_USER_LISTENING"
results["1"]["english"]["classification"] = "ASR_HOMOPHONE_AMBIGUITY"
results["1"]["english"]["classification_reasoning"] = (
    "'strait'と'straight'は完全な同音異義語。標準経路6回・fallback6回とも一貫して"
    "'Straight.'/'Street.'とASR書き起こしされ、無関係な内容(hallucination)は一度も"
    "出現しなかった。TTS音声自体は'strait'を正しく発音していると推定されるが、ASRが"
    "英語でより一般的な綴り'straight'を選んでいるだけと考えられる"
    "(ADD03「航行の自由」→「高校の自由」、IRAN01 B1 kp1と同種のパターン)。"
    "ファイルは最終試行(fallback attempt 6、'Street.'一致)の音声を採用。"
)
results["1"]["english"]["human_review_required"] = True

results["1"]["japanese"]["status"] = "ACCEPTED_PENDING_USER_LISTENING"
results["1"]["japanese"]["classification"] = "ASR_HOMOPHONE_AMBIGUITY"
results["1"]["japanese"]["classification_reasoning"] = (
    "計6回の試行すべてで、ASR書き起こしは「改行」「改」「改革」「改響」「改強」の"
    "いずれかとなった。これらは全て「かい」で始まる語で、「海峡(かいきょう)」の"
    "「かい」部分と一致するか、「きょう」に近い音(響・強・行等)を含んでおり、"
    "「かいきょう」という読みに近い音として一貫している。無関係な内容や"
    "hallucinationは一度も出現しておらず、TTSは「海峡」を安定して発音していると"
    "推定されるが、Azure STTが文脈のない短い2文字語を同音・近似音の別漢字として"
    "書き起こしていると考えられる(IRAN01 B1 kp1「海峡」と同一パターン)。"
    "ファイルは最終試行(attempt 6、'改強。')の音声を採用。"
)
results["1"]["japanese"]["human_review_required"] = True

with open(f"{scaf.OUT_DIR}/audit/key_phrase_generation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("分類を更新しました。ACCEPTED_PENDING_USER_LISTENING: kp1(en/ja)")
