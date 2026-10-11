# OPUS_REVIEW_01 (OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01)

Opus独立技術レビュー(条件C: 重要変更のProduction採用提案前)の結果。以下はFable(PM層)から委任_02へ渡された要旨の転記であり、Opusレビュー本文の逐語録ではない。Fable照合済み。

## Fable判断で実施する項目(本委任で実装)
- 必須1(C1) 固有名詞除外の欠落: `_scg_exclusion_reason`で、Primary判定のcontent_diffsに`entity_like`・`reading_dictionary_mismatch`・原稿側差分のラテン文字のいずれかが1件でもあればSCG不実行(NOT_APPLIED、理由code付き)。
- 必須2 Azure途中キャンセルの厳密化: Production共通関数`p4.get_full_text_via_azure_stt_continuous`は`canceled`と`session_stopped`を同じハンドラで扱い、途中のError cancelでも部分転写をerror=Noneで返す。共通関数は変えず、SCG専用ラッパーでCancellationReason.ErrorをUNAVAILABLE扱いにする。
- 必須3 Phase 0回帰を本番条件で: Reading Resolver ON(LLM mock)・expected_readings指定・除外判定をfixtureに頼らず実装関数で算出する版を追加。救済・C群NGの結果を確認。
- 推奨5 Secondary判定でReading Resolver(LLM)を呼ばない(PASSはEXACT/NORMALIZEDのみで判定不変、費用・遅延の無駄の除去)。
- 推奨6 呼出元でlength_ok=Falseの場合はSCGを呼ばない(設計書§2(c))。
- 推奨7 master store保存時にaudio_classification/scg_resultを併記(既存キー不変、追加のみ)。
- 推奨8 RESULT文書にSCG PASSのNORMALIZEDには既存承認済み正規化(variant layer Candidate C: カタカナ語末長音省略4文字以上、D-1: 位取り漢数字)が含まれることを明記。
- runtime evidenceにOpus追加(c)n3経路・(d)voice01・(e)kill switchを含める。

## ユーザー判断待ちのため実装しない項目
- C2: 同形異音語ガード(設計案・影響は`OPUS_REVIEW_FOLLOWUP_01.md`)。
- 推奨4: SCG除外への否定マーカー追加(「ず/ません/ぬ/ざる/まい」)(同上)。
