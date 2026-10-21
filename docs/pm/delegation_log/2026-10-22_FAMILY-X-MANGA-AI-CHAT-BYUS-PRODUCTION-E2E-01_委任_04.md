FABLE-DELEGATION-MARKER: FXBY-USER-ACCEPT-委任_04-20261022

# 委任(FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_04: ユーザー正式承認(試聴PASS)の記録のみ。API 0・JPY0・音声/コード無変更)

## 0. 運用ルール・並列注意
他agent稼働中: (D-2)KP両方PASS配線=`er078_*`/`er006_secondary_asr_01.py`/`er003_v1_repro01_main_generate.py`/`er019_family_x_kp_en_k2_store_01.py`/`er063_*`/CURRENT_SPEC ASR節、(C-2)B3丸め実装=`er019_family_x_entertainment_production_runner_01.py`/`er053_*`/`er095_*`。あなたはSSOT行とdocsのみ。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`)編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分を混ぜない。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_USER-ACCEPT_USER.md`へ保存、文字数・sha256記録)
---
「漫画のキャラクターとAIで会話(byUs)」正式E2E-01を承認します。
---

## 2. 作業
1. 対象の確認: 管理ID FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01、run=`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/`、試聴ページ=`user_test/manga_ai_chat_byus_e2e_01/index.html`(KP4 take part是正後の版、`KP4_REMEDIATION_01.md`、新KP4 sha `e440550160713cf8cb80e0b5598393e0bb3148f74c74ff33a5d643943b70466f`)。現在公開中の音声・ページのsha/構成を記録し、「承認対象の版」を特定(Std/Adv結合ファイルのsha256、index.htmlのsha256、commit)。
2. 記録: 過去の記事ユーザー承認の記録方法(例: OPEN-4xxの`USER_LISTENING_PASS`/`USER_ACCEPTED`、`docs/pm/REPORT_LEDGER.md`、runの`audit/`配下の承認記録)をGrepで確認し、同じ方式で記録する。最低限: `OPEN_ITEMS.md` OPEN-431(記事B ユーザー試聴待ち)→`CLOSED_USER_ACCEPTED`(2026-10-22、承認対象版のsha・URL・原文出典)、`DECISION_LOG.md`に承認エントリ(逐語)、`docs/pm/USER_DECISION_REGISTER_01.md`の該当行(記事B試聴)を判断済みへ、runの`audit/`に`user_acceptance_20261022.json`(承認版sha・URL・原文sha・記録者Fable/sonnet-worker)を追加(音声・text・manifestは無変更)。`docs/pm/REPORT_LEDGER.md`行追加。`docs/pm/ACTIVE_TASK.md`の該当ヘッダStatusを更新。
3. 注記: 本記事のKP1-3,5(Std/Adv)はPrimary単独PASSで採用された版であり、本日承認のKey Phrase両方PASS仕様に基づくAzure追加確認(S1)が進行中(D-2)。ユーザー承認は人間の試聴に基づく最終判断として優先し、S1で不成立があっても本承認版は差し替えない(結果は情報としてユーザーへ報告)旨をOPEN-431履歴に1行記す。
4. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_04.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: FXBY-USER-ACCEPT-委任_04-20261022` を含むAgent tool_useの0始まり通番、253前後)。
5. commit(対象のみ)→push→到達確認。`docs/pm/RESULT_PACKET_FXBY4.md`へ短い報告(承認版の特定情報・変更ファイル・commit・RESULT_PACKET 4行・JPY0)。