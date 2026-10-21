# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_04(読み取りのみ: Advanced(b1b) `full_story_part1`/`full_story_part3` のTTS→ASR再試行3回の具体内容をrun証拠から抽出。API 0・ファイル変更なし・Git操作なし[T-0保存のみ可])。並行agent: 記事A 委任_03(`paycheck_personality__run_pp_01`配下を調査中。別run dir、触らない)。

## 性質/禁止
- 調査のみ。TTS/ASR/LLM呼出0。state/wav/SSOT変更なし。
- T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_04.md`へ逐語保存(extract tool、N=「BYUS-PRODUCTION-E2E-01 委任_04」を含む最新index)。commitは最後にこのfileのみ明示add(`git push origin HEAD:main`)。

## 対象
`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/audit/tts_generation_results.json`(`segments.full_story_part1` と `segments.full_story_part3`: `standard_attempts_log[*]`、`fallback_attempts_log`、`cascade_steps`)、必要なら`raw_usage_log.jsonl`(model/voice)、`er011_output/attempt_history.jsonl`該当行、`b1b/audit/style_profile_gate.json`、run dir直下`console_audio_01.txt`(cooldown 600秒の記録箇所)。

## 抽出項目(各segment、attemptごとに表)
1. attempt番号/経路(standard|fallback)/生成時刻/model/voice/style文言sha(N01 `d1956c91…`との一致)/wav duration
2. 一次ASR(model名、転写全文)と canonical との差分語(canonical側の語→ASR側の語、位置が分かるよう前後3語)
3. 二次ASR(Azure等、転写全文)と差分語
4. 統一judgeの結果コード(例 NG_BOTH/TRUE_CONTENT_MISMATCH/primary_pass)と理由テキスト(原文引用)、semantic_equivalence結果
5. 最終採用attemptと、採用attemptのASR結果
6. 差分語の分類: (a)同音・活用/縮約 (b)句読点・抑揚 (c)固有名詞・造語の誤認識(byUs→bias/by us 等) (d)語の脱落/追加 (e)その他。**音声の良否は未試聴=未確定**と明記、断定しない。
7. 600秒cooldownが入った箇所(どのattemptの後、理由コード)。
8. 3回のattemptはすべて承認Style(N01)の標準経路か、fallbackへ落ちたか(記事A第2部との違い)。

## 報告(docs/pm/RESULT_PACKET_FXBY4.md 上書き、簡潔に)
part1/part3それぞれ: 表(attempt×項目1-5)+差分語の要約3〜5点+分類+採用attempt。末尾に「ユーザーが聞きどころを把握するための要約(日本語3〜6行)」と、判断候補があれば「判断候補」表記(なければ「なし」)。