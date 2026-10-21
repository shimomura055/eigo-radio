# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_02(Fable判定のSSOT記録のみ。API 0、コード変更なし)+FAMILY-X-MANGA-AI-CHAT-BYUS-KP4-TAKE-PART-REMEDIATION-01 委任_02(同、Fable判定記録のみ)。
並行agent `ASR-THREE-WAY-COMPARISON-TRIAL-01` がOPEN_ITEMS/REPORT_LEDGERに行を追加しうる。編集直前に`git status --porcelain`+再Grep→自分の行だけ編集→即`git add <file>`+commit、index.lock 30秒待ち。`git add -f`/`-A`/`-u`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止。対象行はGrepで特定)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_委任_02.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_02」を含む最新index)。T-2: TTSなし。

## Fable判定(逐語で記録すること)
### A. OPEN-437(FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01)
Status: `TRIAL_DONE_PENDING_FABLE` → **`USER_DECISION_REQUIRED`**。
Fable判定文(2026-10-21): 「機構(選定済み中核数値の丸め判断→Writerへの【概数表記】伝達)はn=1(記事A)で期待どおり動作し、B3選定・中核数値・注記/sidecar・Writer入力の不変は構造的に証明済み(事前ラベル9/9一致、LDC changed_number=0)。ただし(1)承認済みのFact Lock Writer数字規則(5)『丸め・「約」追加禁止』(er053_family_x_factlock_ja_writer_01.py:86-88、DECISION_LOG:20533)への例外化が必須=承認済み仕様の変更、(2)概数の粒度(13万/13万5千、ユーザー期待例は about 135,000)が未規定で判断LLMの粒度が揺れる、(3)量産単価+JPY2.95〜4.30/記事(70円比+4.2〜6.1%)、(4)Writer出力レベルの『数値以外の変化なし』は再生成揺れと分離できず未証明、により VALIDATED ではなく USER_DECISION_REQUIRED。VALIDATED相当なのは機構の動作証明(n=1)のみ。Production採用・配線なし。Production実装に進む場合はOpus必須レビュー(11-3条件A)を実装前に実施。」
### B. OPEN-431(記事B)のKP4是正
Fable判定文(2026-10-21): 「KP4『take part』是正(委任_01、commit 5a92f9c73)=是正完了(PRODUCTION_WIRED相当: Production KP経路で再生成・Store整合・resume整合・Regression 159件PASS・secret scan 0・費用JPY0.4)。観測3方式9/9『Take part』。発音の最終確認はユーザー試聴待ち(聞き比べURL user_test/kp4_take_part_compare_01/)。記事B全体の最終試聴PASSとは別。TTS実行モードは既定BATCH(CURRENT_SPEC:1785の既定、仕様内)。manifest.jsonのcommitに既存未commit entry 5,252行が同梱(Production成果物、secret scan 0、履歴書換えなし)。」

## 作業
1. OPEN_ITEMS.md: OPEN-437行(L950付近、再Grep)のStatusを`USER_DECISION_REQUIRED`へ更新し、上記A判定文を同行末尾に「Fable判定(2026-10-21):…」として追記。OPEN-431行に上記B判定文を追記。行の他の内容は変えない。
2. `docs/pm/USER_DECISIONS_REGISTER.md`(または既存のユーザー判断レジスタ。#134が最新。ファイル名はGrep `#134`で特定)に **#135** を追加: 件名「B3 中核数値 丸め判断(FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01)のProduction採用可否」、判断事項D1〜D4(D1 規則(5)への【概数表記】例外の承認/D2 原価+2.95〜4.30円の許容 or 削減Trial先行/D3 粒度規定[有効2桁=13万 か 期待例の13万5千 か/既に概数のFactの再丸め可否]/D4 価値判断[記事A 1箇所、音声聞き取り評価未実施])、Fable推奨=「(ア)今は採用せず保留。理由: 効果が記事A 1箇所の聞き取りやすさに限られる一方、承認済み規則(5)の例外化+単価+4〜6%+粒度未規定の3つの新判断を要し、Q>D>Cの観点で費用対効果が現時点では低い。採用するなら先にD3粒度規定とD2削減Trial(effort low・出力削減)を条件にする」、Status 未決、出典 `docs/research/FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01/TRIAL_RESULT_01.md`。既存#133/#134の書式に合わせる。
3. REPORT_LEDGERに1行(両管理ID、Fable判定記録)。ACTIVE_TASKローカル更新(Status: B3=USER_DECISION_REQUIRED、KP4=是正完了・試聴待ち)。
4. secret scan→明示add(OPEN_ITEMS.md、レジスタ、REPORT_LEDGER、delegation_log)→commit→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_B3RD2.md 上書き、短く): 変更行(file:行)、commit hash、push確認、#135の実ファイル名。