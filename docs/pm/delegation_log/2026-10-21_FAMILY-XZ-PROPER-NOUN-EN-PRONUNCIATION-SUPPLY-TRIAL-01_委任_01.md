# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_01(**設計のみ・実行なし**: 未登録の英語固有名詞・ブランド名・造語[例 byUs]を検出→信頼できる情報源で正しい英語発音を確認→根拠付きでPronunciation Ledgerへ英語発音情報を登録→Azure Phrase List/TTSヒント/ASR工程へ供給する、Family X/Z共通仕様候補のOffline Trial設計書を作成する。実行(API呼出・Ledger書込)は委任_02[Opus条件Aレビュー後]。API 0・費用JPY0)。
並行agent: `FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01`(①不具合是正。`er006_preprod_hardening_01_validation.py`等の判定関数を修正中。**本委任はProduction codeを一切触らない**)。ユーザー原文は①agentが`docs/pm/delegation_log/2026-10-21_FAMILY-XZ-ASR-MULTI-DIFF-FIX-AND-PROPER-NOUN-EN-PRONUNCIATION_USER.md`へ保存する(存在しsha一致ならskip、無ければ自分で保存し報告)。SSOT編集はOPEN_ITEMS新規行1件+REPORT_LEDGER 1行+ACTIVE_TASKのみ(共有プロトコル: 編集直前`git status --porcelain`+末尾再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち)。

## 性質/到達上限Status/禁止事項
- 性質: 新仕様候補の設計(Trial専用経路前提)。到達上限=設計書完成(`TRIAL_DESIGN_01.md`)→Opus条件A(新しい処理フロー)独立レビュー→Fable照合→委任_02で実行。Production配線しない。Trial結果の上限は`VALIDATED`、採用はユーザー。
- 禁止: API呼出、Ledger/Phrase List/Production code/Prompt/設定の変更、判定基準・同音等価ルールの拡張、カタカナ読みからの英語発音の機械的推定・確定、`git add -A`等。
- 共通Charter: 既存資産の最大再利用(新規実装は最小)、X/Z共通設計、安全(読みが確定できない語は登録しない・既存の安全な判定経路維持)。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_01」を含む最新index)。check結果1行。T-2: TTSなし。

## ユーザー指示(原文)
①agentが保存する上記pathを参照(§3「固有名詞の英語発音供給」1〜7、§4必須再現ケース表、§5検証範囲A/B/C、§6「②はTrial専用経路、VALIDATEDにとどめる」)。保存が間に合わない場合は、Fableからの要約ではなく、同pathが出来るまで待つ(最大10分)か、自分で原文保存を担当する(①agentと重複した場合はsha一致を確認して片方を残す)。

## 事前調査(Grep→該当行Read、API 0)
- 既存資産: `er006_pronunciation_ledger_01.py`(entry構造: canonical/ja_reading_katakana/pronunciation_hint/IPA/source/confidence/`get_hint_for_text` L164-206)、`er006_pronunciation_research_01.py`(Perplexity調査Prompt、confidence基準=本人音声sourceのみhigh、CURRENT_SPEC.md:1829)、`er025_entity_pronunciation_resolver_core_01.py:439-531`(EN resolverはLedger cache専用)、`er006_preprod_hardening_01_validation.py:467-489,525`(entity_like=先頭大文字条件、Ledger登録語のentity_like化は2026-09-28判断でOFF)、`er006_secondary_asr_01.py:75,106-111,350-354`(Phrase List構築・setWeight)、`er003_v1_repro01_main_generate.py:~357`(Phrase List構築元)、Family Z側のPhrase List供給(`FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01`のwire evidence、Zで何をPhrase Listに入れているか)、TTSヒント(pronunciation hintをTTS promptへ渡す既存経路の有無)、JA側の固有名詞抽出(今回byusをカタカナ登録した工程=telemetry 13:11:24)。
- 前調査: `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md`、同`ADV_FULLSTORY_RETRY_ANALYSIS_01.md`。
- 既存の関連決定(Existing Spec/Prior Trial Check Gate、21節): CURRENT_SPEC.md:1829(自動PASS条件A/B、IPA→ARPAbet近似PASS禁止、OPEN-83)、2026-09-28「Ledger登録語をentity_likeに使う経路OFF」の原文、2026-10-13「辞書未収録語は既存Ledgerや利用可能な発音情報から合理的な候補を取得する」(`er006_secondary_asr_01.py:350-354`コメント、原文file:lineを特定)。A(既存仕様あり)/B(過去Trialあり・未採用)/C(本当に新規)に分類。

## 設計書に含める内容(`docs/research/FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/TRIAL_DESIGN_01.md`)
1. 目的・ユーザー原文の該当条文の逐語引用。
2. 既存資産の棚卸し(上記)と再利用方針、21節A/B/C分類。
3. 処理フロー案(Trial専用経路、Productionと同じ関数をimportして読み取り・Trial用Ledger[本物のledger.jsonを**コピー**したTrial用path]へ書き込み): (a)固有名詞候補検出: 先頭大文字に加え、文脈手がかり(引用符付き/「called」「named」「pronounced」等の前後/CamelCase/本文中の読み明示文/Research LedgerのFact内の固有名詞・サービス名)を使う候補抽出。LLM使用の要否と使う場合のモデル(最新上位系、25節)・Prompt案・費用。(b)未登録判定(Ledger lookup、英語hint有無)。(c)発音調査: 既存Perplexity研究Promptを再利用し「公式サイト・公式発表・本人/公式動画で確認できる**英語発音**」を要求、カタカナからの推定禁止を明記、confidence基準は既存(高=音声source)。(d)登録: 根拠URL・confidence・取得日時・英語hint(綴り/IPA/許容発音集合)。確定不能なら**登録しない**(安全側)。(e)供給: Phrase Listへ(canonical綴り+許容綴り?=既存Phrase List構築関数の入力形式に合わせる)、TTSヒント(既存経路があれば)、ASR同音判定(既存CMU層に対し、Ledgerの許容発音集合をどう渡すか=**判定基準の拡張にならない範囲**で設計。拡張が必要ならユーザー判断事項として分離)。(f)実投入証拠: Phrase Listの内容・setWeight(2.0)実行を各Azure呼出で記録するログ項目(現行は記録機構なし→Trial harnessで記録、Production側の記録追加は提案のみ)。
4. 必須再現ケース(ユーザー§4表)の各ケースについて、Trialでの入力(既存wav/既存転写/canonical)、期待結果、判定に使う関数、PASS/NGの根拠を事前固定。特に`LINE→Lion`は「実音声が異なる場合は誤PASSさせない」=実音声の判定根拠(既存wav+ASR)を明記。「実音声の誤発音とASR誤記の区別」の方法(複数ASR一致・ローカルwhisper・試聴ground truthの有無)。
5. 検証計画(§5 A/B/C): 既存wav(記事B第1部/第3部の各attempt wavが残っていれば)にPhrase List有/無でAzureを再実行し認識差を測る(費用見積、回数)、誤NG/誤PASSの評価データ(既存PASS済み音声の再実行)、Family Z側での検証対象(メロス/開いた窓の固有名詞: Melos/Selinuntius/Dionysius/Framton/Sappleton等が既にどう扱われているか)、QCD見積(検索費用/呼出回数/時間/70円への影響)。
6. 安全・境界: Production非配線、Trial用Ledgerコピー、既存Ledgerへの書込禁止、判定基準不変、STOP条件、費用上限案(Fableが確定)。
7. Opus条件Aレビュー観点案(新しい処理フロー: 検出→調査→登録→供給の各段の失敗モード、誤登録の伝播リスク、X/Z共通化の落とし穴)。
8. 委任_02(実行)の作業分解と見積時間・費用。

## 手順
S0. `git status`件数、T-0。S1. 事前調査。S2. 設計書作成。S3. OPEN_ITEMS新規行(Status `DESIGN_READY_PENDING_OPUS_REVIEW`)、REPORT_LEDGER 1行、ACTIVE_TASK。S4. secret scan→明示add(設計書・delegation_log)→commit(`FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_01: 設計書(実行前、Opusレビュー待ち)`)→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_PNEP1.md 上書き)
1.設計の要点(フロー図を文章で、再利用資産と新規実装の境界) 2.21節A/B/C分類と既存決定との関係(拡張が必要な箇所=ユーザー判断候補を明示) 3.必須ケースの事前固定表 4.検証計画と費用・時間見積(出典) 5.Opusレビュー観点案 6.commit・raw URL 7.判断候補 8.4行判定。