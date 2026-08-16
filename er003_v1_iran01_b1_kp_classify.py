# IRAN01 B1: kp1(strait/海峡)・kp4(応酬/押収)のASR homophone ambiguity分類
# (ADD03 meaning_3と同種の既知パターン。TTS音声自体は正常と推定されるが、
# 機械QAのみでは確定とせず、最終報告でhuman review=ユーザー試聴を必須とする)
import json

OUT_DIR = "er003_output/novel_audio_02/IRAN01/b1"

with open(f"{OUT_DIR}/audit/key_phrase_generation_results.json", encoding="utf-8") as f:
    results = json.load(f)

classification = {
    "1": {
        "english": {
            "status": "ACCEPTED_PENDING_USER_LISTENING",
            "classification": "ASR_HOMOPHONE_AMBIGUITY",
            "reasoning": ("'strait'と'straight'は完全な同音異義語。標準経路6回・fallback6回とも一貫して"
                          "'Straight.'とASR書き起こしされ、無関係な内容(hallucination)は一度も出現しなかった。"
                          "TTS音声自体は'strait'を正しく発音していると推定されるが、ASRが英語でより一般的な"
                          "綴り'straight'を選んでいるだけと考えられる(ADD03「航行の自由」→「高校の自由」と"
                          "同種のパターン)。ファイルは最終試行(fallback attempt 1、'Straight.'一致)の音声を採用。"),
            "final_used_asr_text": "Straight.",
            "human_review_required": True,
        },
        "japanese": {
            "status": "ACCEPTED_PENDING_USER_LISTENING",
            "classification": "ASR_HOMOPHONE_AMBIGUITY",
            "reasoning": ("計16回の試行すべてで、ASR書き起こしは「海、峡。」(5回)、「改革。」(4回)、"
                          "「改強。」(3回)、その他読点区切りの変形のいずれかとなった。これらは全て"
                          "「かいきょう」という同一の読みに一致する(「改」=かい、「強」=きょう、"
                          "「峡」=きょう等)。無関係な内容やhallucinationは一度も出現しておらず、"
                          "TTSは「海峡」を安定して正しく発音しているが、Azure STTが文脈のない短い2文字語を"
                          "同音の別漢字・読点区切りとして書き起こしていると推定される(ADD03「航行の自由」→"
                          "「高校の自由」と同種のASR homophone ambiguityパターン)。ファイルは最終試行"
                          "(attempt 10、'海、峡。'一致)の音声を採用。"),
            "final_used_asr_text": "海、峡。",
            "human_review_required": True,
        },
    },
    "4": {
        "japanese": {
            "status": "ACCEPTED_PENDING_USER_LISTENING",
            "classification": "ASR_HOMOPHONE_AMBIGUITY",
            "reasoning": ("「応酬」と「押収」はどちらも「おうしゅう」と読む同音異義語。6回の試行すべてで"
                          "一貫して「言葉で押収する。」とASR書き起こしされ、無関係な内容は一度も出現しな"
                          "かった。TTS音声自体は「言葉で応酬する」を正しく発音していると推定されるが、ASRが"
                          "より一般的な法律用語「押収」を選んでいるだけと考えられる(ADD03「航行の自由」→"
                          "「高校の自由」と同種のパターン)。ファイルは最終試行(attempt 6)の音声を採用。"),
            "final_used_asr_text": "言葉で押収する。",
            "human_review_required": True,
        },
    },
}

for rank, langs in classification.items():
    for lang, info in langs.items():
        results[rank][lang]["status"] = info["status"]
        results[rank][lang]["classification"] = info["classification"]
        results[rank][lang]["classification_reasoning"] = info["reasoning"]
        results[rank][lang]["human_review_required"] = info["human_review_required"]

with open(f"{OUT_DIR}/audit/key_phrase_generation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("分類を更新しました。ACCEPTED_PENDING_USER_LISTENING: kp1(en/ja), kp4(ja)")
