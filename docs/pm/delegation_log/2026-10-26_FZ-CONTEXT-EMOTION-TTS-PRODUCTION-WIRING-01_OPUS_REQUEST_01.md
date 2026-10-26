## 管理ID
FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A: Family Z正式経路のセリフTTS retry/fallback構造に新処理フロー[文脈・感情付きTTS→同再試行→10分cooldown→従来方式fallback→HR/STOP]を加える設計、実装前)。read-only。

## 性質/到達上限Status/禁止事項
レビューのみ(編集・実行なし)。JPY0。所見はFableが照合しPM判断する(Opus所見は自動採用しない)。ユーザーは本仕様をAPPROVED_FOR_PRODUCTIONとして決定済み(仕様の是非ではなく、設計が仕様を正しく・安全に実装するかをレビューする)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: read-onlyのため委任文保存・checkはFable側で扱う。T-2: TTSなし。T-3: Capなし(JPY0)。

## レビュー依頼
正本=`C:\Users\tensh\eigo-radio\docs\research\FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01\OPUS_REVIEW_REQUEST_01.md`(全文Read、その論点に限定。検証に必要な追加探索は可)。
Fableが特に重点確認を求める3点: (1)共有関数へ既定None `attempt_hook`を追加する案A(Family B/C呼出がバイト同一に保てるか、`carried_log()`/`record_outcome`累積と外側ループ`count_tts_generations_in_result`の二重計上、Adv「ASR OK→減速後NG」のNG化、ASR OK確定直後〜checkpoint前クラッシュの窓)の安全性と、案B(複製)/案Cとの優劣 (2)感情情報の自動受理(Trial `validate_emotion_items`逐語移植、決定済み77件でFable目視と100%一致)でFable目視を外してよいか、LLM失敗時「全clip中立で続行」か「技術STOP」か、Trial未検証storyのfallback表示名 (3)強制NG注入=evidence driverがGate出力をNG方向のみ上書き(Production code に注入口なし)がGate迂回に当たらないか、共有store/公開page汚染、ctx attempt内の`minimal_fallback`許容可否。
加えて: J-1(現行Zセリフ経路にLocal Rewriteが未配線のため、3回NG→STOPPED→HR Lock→STOPを既定としLRは新設しない)の判断が、ユーザー原文「NG → 既存のLocal Rewrite処理へ。Local Rewriteで解決できなければ、既存のHuman Review／STOP規則に従う」「Local Rewriteも既存の回数上限・安全条件を維持し」と整合するか(=既存LRが無い以上「既存のHR/STOP規則」へ直行するのが忠実か、それとも新設が必要か)の意見。

## 事前指定Read一覧
1. `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/OPUS_REVIEW_REQUEST_01.md` 全文。
2. `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/DESIGN_01.md` 全文(状態機械・hook案A/B/C・自動受理・fallback除外・強制NG・§E Trial問題・§J CURRENT_SPEC文案)。
3. `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/EXISTING_SPEC_CHECK_01.md` §3差分表、`TEST_PLAN_01.md` 全文、`BUDGET_PLAN_01.md` §区分2〜3。
4. コード(Grep→該当範囲): `er012_b_family_voices_production_01.py` :500-560(`generate_voice_body_wide_margin`、style_prefix_override)、`er003_v1_n3_01_tts_generate.py` :290-330, :430-480(外側ループ・count_tts_generations_in_result・LR未配線docstring)、`er011_*`(attempt上限・record_outcome・HR Lock)、`er020_*`(`COOLDOWN_SECONDS`、`maybe_cooldown_before_attempt`)、`er063_family_z_audio_01.py`(dialogue生成とcheckpoint)、`er118_fz_dialogue_context_tts_trial_01.py`(`validate_emotion_items`、CONTEXT block合成)。
5. ユーザー原文: `docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md` §2・§3・§6。

## 報告(出力形式)
依頼文の論点ごとに「問題なし/要修正(修正案)/ユーザー判断要」+根拠(ファイル:行)。Fable重点3点+J-1への意見。M(必須修正)/R(推奨)の番号付き一覧(12件以内)。X/Y/B/Cへの無影響の確認方法、PRODUCTION_WIRED判定に必要なevidenceの過不足。最終行に5行以内の要約。