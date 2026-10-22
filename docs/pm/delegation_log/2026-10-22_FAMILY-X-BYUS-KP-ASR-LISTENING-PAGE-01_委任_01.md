FABLE-DELEGATION-MARKER: BYUS-KP-ASR-LISTEN-PAGE-委任_01-20261022

# 委任(FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01 委任_01: byUs記事Key Phrase音声7件のASR比較表(Primary/Secondary/Whisper)+試聴、take part合格音声と「Take tart」問題音声の聞き比べを、1つの試聴ページ(GitHub Pages)にまとめる。既存音声の再生成・変更禁止。Production仕様無変更)

## 管理ID
FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01 委任_01(新規。関連=OPEN-431[byUs正式E2E、ユーザー受入済み]・OPEN-440[KP両方PASS、PRODUCTION_WIRED]。並行: 別agentが`FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01`を実行中で`OPEN_ITEMS.md`(新規OPEN行)・`docs/pm/REPORT_LEDGER.md`末尾を編集する。共有ファイル編集前に必ず`git status`→該当行を再Grep→自分の行だけ編集→即`git add <file>`+commit。`index.lock`は30秒待って再試行。新規OPEN番号は編集直前にGrepで最新+1を取る[相手が先に取っていれば次番号])。

## 性質/到達上限Status/禁止事項
- 性質: 試聴ページ作成+既存ASR結果の整理+Whisper追加判定(保存音声に対する判定のみ)。到達Status: `USER_LISTENING_PENDING`。Opus Gate: 非該当(Production変更なし)。
- 費用/日次: 当日既使用 JPY275.35(出典RESULT_PACKET_B3RD8)+KP6M Trial進行中(Cap 300)。本委任見積 **JPY0〜5**(Whisperはローカル=0。Primary/Secondaryは既存結果の再利用が原則。既存結果が無い音声に限り再ASR可、OpenAI/Azure各1回/音声まで)。Cap JPY20(T-3: 到達だけで自動STOPしないが超過見込みで有料呼出停止・報告)。承認区分: C。
- 禁止: 既存音声(Store wav/mp3、run成果物)の再生成・編集・移動禁止(ページ用に**コピー**するのは可)。TTS呼出禁止。Production経路・Store manifest・Validator・仕様の変更禁止。推測で発音の正否を断定しない(認識文字列は事実として並べるだけ)。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。commit前`.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore(force-add禁止)。SSOT全文読込禁止。他agentの未commit差分を混ぜない。STOPセンチネル確認後に開始。

## ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01_USER.md`へ本文無改変で保存、文字数とsha256を記録)
---
# Claude Codeへの修正指示：ASR検証と実音声確認

## 目的

ASRの判定結果だけでなく、**実際の音声をユーザーが試聴し、発音の正否を判断できる状態にする。**

以下2項目を実施する。

### 1. byUs記事：7件のASR比較＋音声提示

既存のKey Phrase音声7件について、次の比較表を作成する。

| 正しい表現 | Primary認識結果 | Secondary認識結果 | Whisper認識結果 | 音声再生 |
|---|---|---|---|---|

- Primary／Secondary／Whisperそれぞれの実際の認識文字列とPASS／NGを記載。
- Whisperの既存結果がなければ、保存済みの同一音声で追加判定を実施。
- PrimaryとWhisperが同一モデルか、別モデルかも確認。
- **7件すべての既存音声を再生できる試聴ページを作成する。**
- 特に新基準で不合格となった`think up`、`blurt`を明確に表示する。
- 既存音声を再生成・変更しない。

### 2. take part：問題音声の実際の発音を確認

以下を並べて再生できるようにする。

1. **byUs記事の合格済み`take part`音声**（Primary／SecondaryともPASS）
2. **今回「Take tart」と認識された問題音声**（Primary／SecondaryともNG）

問題音声が複数ある場合は、今回のNG判定に使われた音声を漏れなく提示する。

それぞれについて、期待する表現・Primary／Secondary／Whisperの認識結果を表示する。

**重要：ASRの認識文字列だけから発音の正否を推測・断定しないこと。**

ユーザーが実際に聞き比べ、正しい発音か誤発音かを判断できるようにする。

### 3. 成果物・報告

**1つの試聴ページにまとめること。**

- byUsの7件：ASR比較表＋音声再生
- take part：合格音声と問題音声の比較再生
- スマートフォン・PCからアクセスできるURLを提示
- 音声ファイルとASR結果の対応を確認し、リンク切れ・再生不良がないことを検証
- Productionの仕様・保存音声は変更しない

報告は簡潔に、**試聴URL、ASR比較表、確認できた事実、ユーザー試聴で判断が必要な音声**だけを提示すること。

音声確認前に推測に基づく品質リスクや新たな改善案を列挙しない。

## 4. 完了条件

ユーザーが試聴ページを開き、問題音声を実際に聴いて判断できる状態まで完成させる。

既存の仕組みを再利用し、不要なTrial・TTS再生成は行わない。新仕様の採用やProduction変更は対象外。
---

## Fableの事前確認(再照合し、ズレがあれば報告)
- 「既存のKey Phrase音声7件」= byUs記事(`manga_ai_chat_byus__run_byus_01`)のKP英語音声をMaster Audio Store基準でKP両方PASSで再調査した7件(D-2 `er096_output/kp_dual_prod_01/survey_article_b.json`: 5 PASS=can't wait/fan stories/take part/story-maker/bring in、2 NG(新基準)=think up/blurt)。Primary/Secondaryの認識文字列はこのsurveyと`er096_output/kp_dual_prod_01/evidence_summary.json`、Store manifest(`er006_output/master_audio_store_01/manifest.json`の`kp_dual_check`)にある想定。無ければ所在を探し、どうしても無い音声だけ再ASR(費用計上)。
- 「今回『Take tart』と認識された問題音声(Primary/SecondaryともNG)」= D-2の「take part型拒否確認 10/10」で使った音声(`er096_output/kp_dual_prod_01/`配下の証跡・`er096_kp_dual_runtime_evidence_01.py`の入力)および、それ以前の記事B take part再生成時にNGになった音声(`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/`配下のretry履歴・`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`・`er011_output/attempt_history.jsonl`の該当行)。**NG判定に使われた音声ファイルを全て特定し漏れなく載せる**(特定できないものは「音声ファイル未保存」と明示、推測で代替しない)。合格済みtake part音声=Storeの現行PASSエントリ(記事Bの正式版に使われたもの)。
- Whisper: ASR 3方式比較Trial(`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/`、ローカルWhisper runner)の既存実装・モデル(モデル名・サイズを記録)を再利用し、同一音声でローカル判定(費用0)。PrimaryはOpenAI API `gpt-4o-mini-transcribe`(`er078_asr_unified_judge_01.py`/ASR3W TRIAL_RESULT_01.md §で確認)であり、ローカルWhisperとは別モデル。両者の関係(別モデル/同系統か)を根拠付きで1行記載。Whisperの文字列に対するPASS/NGは、既存の判定関数(正規化・同音救済を含む現行Validator)に通した結果と、生文字列の両方を出す(新しい判定基準を作らない)。
- 新基準=KP英語フレーズはPrimary・Secondary両方PASS必須(2026-10-22ユーザー採用、OPEN-440)。表のPASS/NGは「各Provider単独の判定」と「新基準の総合判定」を分けて表示。
- ページ: `user_test/byus_kp_asr_listen_01/index.html`(GitHub Pages: https://shimomura055.github.io/eigo-radio/user_test/byus_kp_asr_listen_01/index.html )。既存の試聴ページ生成script(例`er019_pp_final_page_02.py`、`user_test/kp4_take_part_compare_01/`の作り)を参考に、Production経路外の新規script `er099_byus_kp_asr_listen_page_01.py`で生成。音声はページdirへコピー(mp3/wav、サイズ小)。構成: §1 byUs 7件表(正しい表現/Primary文字列+判定/Secondary文字列+判定/Whisper文字列+判定/新基準総合/音声player)、think up・blurtを強調表示。§2 take part: 合格音声と問題音声(複数)を並べ、各行に期待表現・Primary/Secondary/Whisper結果。スマホで見られる簡素なレイアウト。`user_test/kp4_take_part_compare_01/`が既に同種なら中身を確認して再利用・統合(重複ページを増やさず、本ページを正とする)。
- 検証(Gate 7): push後にPagesで200確認、Playwrightで全playerの再生・seek・console error 0・HTTP≥400 0を確認し、証跡jsonを`docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/pages_play_evidence_01.json`へ。音声ファイルとASR結果行の対応(ファイル名・sha256・出典path)を`mapping_01.json`に保存。

## 事前指定Read/Grep
- Read: `er096_output/kp_dual_prod_01/survey_article_b.json`、`er096_output/kp_dual_prod_01/evidence_summary.json`、`docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/IMPLEMENTATION_DESIGN_01.md`(take part型拒否の節のみGrep `take part`)、`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/TRIAL_RESULT_01.md`(Whisperモデル名の節のみGrep `whisper`)、`user_test/kp4_take_part_compare_01/index.html`。
- Grep: `take part|Take tart` in `er096_output/kp_dual_prod_01/**`, `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`, `er011_output/attempt_history.jsonl`(該当行のみ); `think up|blurt` in `er006_output/master_audio_store_01/manifest.json`; Whisper runner: Glob `er08*whisper*.py`/`er0*asr_three_way*.py`。
- OPEN番号: Grep `OPEN-44[0-9]` in `OPEN_ITEMS.md` → 最新+1。

## 実行コマンド全文
- ページ生成: `.venv\Scripts\python.exe er099_byus_kp_asr_listen_page_01.py --out user_test/byus_kp_asr_listen_01 --mapping docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/mapping_01.json`(引数名は実装に合わせ、実行コマンドを実値で報告)
- Whisper判定: 既存runnerのコマンドを実値で(モデル名を含める)
- secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`
- T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: BYUS-KP-ASR-LISTEN-PAGE-委任_01-20261022`を含むAgent tool_useの0始まり通番、264前後。先頭行で一致確認)

## SSOT追記文
- `OPEN_ITEMS.md`新規行: `| OPEN-4xx | FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01 | 2026-10-22 | USER_LISTENING_PENDING | byUs記事KP音声7件のASR比較(Primary/Secondary/Whisper)+take part合格音声と「Take tart」問題音声の聞き比べページ=user_test/byus_kp_asr_listen_01(Pages確認済み)。既存音声無変更・Production無変更・費用JPY<x>。ユーザー試聴判断待ち。 |`
- `docs/pm/REPORT_LEDGER.md`末尾1行。DECISION_LOG/CURRENT_SPEC/UDRは編集しない。

## Git
- 明示add: `er099_byus_kp_asr_listen_page_01.py`、`user_test/byus_kp_asr_listen_01/**`、`docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/**`、`docs/pm/delegation_log/2026-10-22_FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01_*`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`。
- commit: `BYUS-KP-LISTEN 委任_01: byUs KP音声7件ASR比較(Primary/Secondary/Whisper)+take part合格/問題音声聞き比べ試聴ページ user_test/byus_kp_asr_listen_01、既存音声・Production無変更、費用JPY<x>`。push→Pages 200確認。

## 報告(RESULT_PACKET_BYUSKP1.md)
ユーザー§3の指定どおり簡潔に: 試聴URL/ASR比較表(7件: 正しい表現・Primary文字列+判定・Secondary文字列+判定・Whisper文字列+判定・新基準総合)/take part表(合格1+問題音声n件、各認識結果)/確認できた事実(Primary≠Whisperの根拠、使用Whisperモデル、音声の出典path・NG判定に使われた音声の特定結果と未保存分)/ユーザー試聴で判断が必要な音声の一覧/費用実測/Gate 7検証結果/RESULT_PACKET 4行/実行コマンド/raw URL。推測に基づく品質リスク・改善案は書かない。