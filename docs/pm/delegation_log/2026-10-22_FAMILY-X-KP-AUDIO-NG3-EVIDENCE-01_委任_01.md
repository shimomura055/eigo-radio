FABLE-DELEGATION-MARKER: KP-AUDIO-NG3-EVIDENCE-委任_01-20261022

管理ID: FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01(OPEN-456 F3の先行証拠、合同検証OPEN-455由来)。**調査・証拠提出のみ。新規TTS生成・追加Trial・仕様変更・Production修正・有料API呼出は禁止(費用0)。** 既存音声・ログだけを使う。不明は「未確認」と書く(推測で埋めない)。発音の正否を音声を聴かずに断定しない。

## ユーザー原文(逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01_USER.md` へ見出しから末尾まで一字一句そのまま保存)
# Family X Key Phrase音声NG 3件 — 証拠提出依頼

今回のProduction合同検証で発生したKey Phrase音声NG 3件について、以下を報告してください。

対象：
- `pump one's fist`：2件
- `novelty minaudière`：1件

## 1. 音声の提示

3件それぞれについて、**実際にNG判定された音声を試聴できるURL**を提示してください。

既存の試聴ページで確認できなければ、3件をまとめた簡易試聴ページを作成してください。

## 2. ASR判定結果

各音声について、以下を一覧表で報告してください。

- 対象記事・レベル
- 正しいKey Phrase
- OpenAI（Primary）の認識全文とPASS/NG
- Azure（Secondary）の認識全文とPASS/NG
- Whisper（第3判定）の認識全文とPASS/NG（実行された場合）
- 最終判定とHuman Reviewに至った理由
- TTS再生成・ASR再判定の履歴（実施されていれば）

## 3. 原因の切り分け

各件について、既存ログと音声証拠から、以下のどれに該当するか整理してください。

1. TTSの実際の発音不良
2. ASRの誤認識・誤判定
3. 現行判定仕様・救済処理の問題
4. 現時点では判断不能

推測と確認済み事実を明確に区別してください。

## 実施条件

- **調査・証拠提出のみ。**
- 新規TTS生成・追加Trial・仕様変更・Production修正は行わない。
- 既存音声・ログを再利用し、費用を最小化する。
- 不明な項目は推測で埋めず「未確認」と記載する。

今回はユーザーが直接音声を聴き、各ASRの判定結果と照合できることを完了条件とします。

## 所在(出発点)
- run dir: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01/{a2,b1b}/`(`pump one's fist`=KP1)、`.../small_bag__run_jre_01/a2/`(`novelty minaudière`=KP1)。各attemptのwav・`audit/`・`tts_checkpoint.json`・ASR判定記録(`kp_dual_check`容器、`version=kp_vote_check_v1`、vote block)・`raw_usage_log.jsonl`、共有`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`の本run由来3行、`er011_output/attempt_history.jsonl`、HR Lock記録。合同検証の集計 `docs/research/JOINT-RUNTIME-EVIDENCE-01/RESULT_01.md`・`run_20261022/`(JRE2報告では「保存wavのoffline再判定(API 0)でWhisperが`Pump Ones Fest`」とある。その記録も探す)。
- 前例ページ(体裁の流用元): `user_test/byus_kp_asr_listen_01/index.html`(`er099_byus_kp_asr_listen_page_01.py`)、`user_test/kp3v_vote_evidence_01/index.html`。再生検証の前例: `er099_byus_kp_asr_listen_play_verify_01.py`。

## 作業
1. 3件について、**NG判定を受けた全attemptのwav**(再生成があれば各attempt)を特定し、`user_test/fx_kp_audio_ng3_listen_01/` に音声をコピーして1ページの簡易試聴ページ(`index.html`)を作る。各行=記事/レベル/KP/attempt番号/再生ボタン/OpenAI転写+判定/Azure転写+判定/Whisper転写+判定(実行時のみ。未実行は「未実行(理由)」)/最終判定/HR理由。音声はコピーで配置し、元runは無変更。ページの再生検証(全音声が0バイトでなく、ブラウザで再生可能=前例scriptの方式)を実施し、結果jsonを保存。GitHub Pages URL `https://shimomura055.github.io/eigo-radio/user_test/fx_kp_audio_ng3_listen_01/index.html` を報告(push後に有効)。
2. 一覧表(§2の7項目)をMarkdownで `docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/EVIDENCE_01.md` に作成。各値の出典path:行(またはjsonキー)を併記。TTS再生成・再判定の履歴(attempt数、各attemptの判定、STOPPED→HR Lockに至った条件、使用model: TTS/Primary/Secondary/Whisper)を含む。
3. 原因切り分け(§3): 各件を1〜4に分類し、「確認済み事実」(ログ・転写の一致/不一致、複数ASRの一致度、保存wavのoffline Whisper再判定結果があればそれ)と「推測」を分けて記す。**音声を聴いた判断はしない**(ユーザーが聴いて照合する)。例: 3系統のASRが揃って同種の崩れ(「once/ones fist」)を転写していれば「TTS発音不良の可能性が高い(推測)、確認済み=3系統一致」、系統間で割れていれば「ASR誤認識の可能性/判断不能」。`one's`形の生成履歴(選定句`pumps its fist`→一般化`pump one's fist`)と、TTSへ渡した実テキスト(`japanese_gloss_tts`/英語KP TTS入力)を出典付きで記す。`minaudière`はTTS入力の文字列(アクセント記号の有無)も記す。
4. SSOT: OPEN-456 F3に「証拠ページ・EVIDENCE_01作成済み」を1行追記、`docs/pm/REPORT_LEDGER.md`1行。T-0保存 `docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01_委任_01.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: KP-AUDIO-NG3-EVIDENCE-委任_01-20261022` 一致で確定)。
5. commit(自分のファイルのみ `git add <file>`、`-A/-u/-f`禁止。音声コピーは前例ページと同じ扱いでcommit)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。

## 報告
`docs/pm/RESULT_PACKET_NG3.md`に4行+判定整合行。本文: 試聴ページURL、§2の一覧表(そのまま転記)、§3の切り分け(確認済み/推測を分離)、再生検証結果、commit hash、raw URL。