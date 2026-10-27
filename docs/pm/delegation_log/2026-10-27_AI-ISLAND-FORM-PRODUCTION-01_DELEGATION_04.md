## 管理ID

AI-ISLAND-FORM-PRODUCTION-01 委任_04(不具合候補のread-only診断。委任_03(d05729316)の所見: X Standardで`full_story_part1_k2`(本文「The AIs sent to the island …」)が生成直後は二次ASR確認(OpenAI→Azure)で通るのに、6%減速(slowdown)後処理後の再検証では3回とも`ASR_VALIDATION_UNCERTAIN`で不一致となり、retry→fallback→Local Rewrite(`AIs`→`AI agents`)→M3 Gate BLOCKまで連鎖した(TTS費用¥32.72のうち本件retryが主因)。疑い=減速後再検証経路で二次ASR確認(`EXACT_MATCH`/`NORMALIZED_MATCH`救済)が適用されていない。API 0・JPY0、Productionコード編集禁止、run dir編集禁止)。並行Agent: GPG委任_05C(Y run)、SLOT-23設計。あなたの所有=`docs/research/AI-ISLAND-FORM-PRODUCTION-01/DIAG_SLOWDOWN_ASR_01.md`、`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_04.md`(+check.json)、`docs/pm/RESULT_PACKET_AIF4.md`(gitignore)。pathspec付きcommit、`git push origin HEAD:main`。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。時間見込み: 約45分。

## 実施事項

1. 証拠読取(読むのは当該segmentのentryのみ): `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/{a2,b1b}/audit/tts_generation_results.json`の`segments.full_story_part1_k2`(`standard_attempts_log`/`slowdown_attempts_log`/`local_rewrite_recovery`/二次ASRの有無・判定コード)、`human_review_queue`相当、raw_usage_logの該当行(Azure ASR呼出の有無と時刻)。
2. コード経路の照合(Grep ±15): X runner/TTS module(`er019_*`、`er117_chunk_tts_production_01.py`、`er1xx`のslowdown/`speed`/`post_process`/`revalidate`/`secondary_asr`/`NORMALIZED_MATCH`)で、(a)生成直後の検証関数、(b)減速後の再検証関数、(c)両者で二次ASR・救済規則の呼出有無・判定条件の差、(d)Y/Zの同等経路(`er121`/`er063`)に同じ差があるか。
3. CURRENT_SPECの二次ASR受理規則(Grep `NORMALIZED_MATCH|二次ASR|slowdown|減速`)と照合し、「仕様どおり」か「実装差(不具合)」かを判定。不具合なら: 原因(file:line)、再現条件、影響範囲(X/Y/Z・Std/Adv・費用への影響=本runの retry回数と費用内訳)、修正案(最小差分、Gate緩和にならないこと、test案)、11-8分類。仕様どおりなら: その根拠と、仕様上「AIs→AI」を救済できない理由、改善提案(仕様変更=ユーザー判断事項として整理、実装しない)。
4. 併せて、M3 Gateの`STD_FALLBACK_USED_OR_UNKNOWN`がStdのみに付いた理由(fallback経路使用の記録)を1段落で説明。
5. `DIAG_SLOWDOWN_ASR_01.md`に上記をまとめcommit: `AI-ISLAND-FORM-PRODUCTION-01 委任_04: X Std 減速後再検証の二次ASR適用差の診断(read-only、API 0)`、trailer `Delegation: AI-ISLAND-FORM-PRODUCTION-01/04`。Secret grep 0件。

## 報告

`RESULT_PACKET_AIF4.md`: (0)T-0、(1)判定(不具合/仕様どおり)と根拠、(2)影響範囲・費用、(3)修正案(実装せず)、(4)判断候補、(5)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。