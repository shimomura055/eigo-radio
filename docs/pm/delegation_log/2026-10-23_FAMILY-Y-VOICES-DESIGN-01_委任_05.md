FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_05-PHASE3-AUDIO-20261023

# 委任_05: Family Y 統合Trial Phase 3(音声・試聴ページ、DEV/Trial経路のみ)+8項目成果物の材料整備

前提読込: `docs/pm/RESULT_PACKET_FYT1.md`、`docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_01/PHASE3_PLAN_01.md`、ユーザー原文 `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_02.md`(成果物8項目・上限250円・固定Voice Algieba/Zephyr/Schedar)。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_05.md`(N≈343〜353、MARKER一致確認)。
2. ACTIVE_TASK.md: 並行agent 2本(FAMILY-Z-SOURCE-FIDELITY 委任_06=『開いた窓』TTSあり、FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_02=記事A TTSあり)。編集直前に再読込・自分の行のみ。**TTS開始前に他行「有料run(TTS)進行中」を確認、あれば5分間隔・最大30分待機**。自分のTTS開始/終了を記す。

## 1. Fable判定(Phase 3の範囲)
- 音声化対象: **主候補 R2g(Std+Adv)と比較候補 R0g(Std+Adv)の両方**を承認(ユーザーがR0/R2採用を試聴で判断できるようにする。PHASE3_PLAN見積50〜76円、通算≤222円で上限250円内)。実行直前に再見積し、**通算250円を超える見込みなら比較候補R0gを落として主候補のみ**(開始前に判断・記録、超過後の停止ではなく)。
- Voice固定: Voice1=Algieba/Voice2=Zephyr/Voice3=Schedar、Preview/Comment等の共通部はFamily X Std/Advの既定話者に準拠(PHASE3_PLANどおり)。自動割当は使わない。
- Std Voice partの減速: **既定はX準拠**(Family X Stdの減速後処理と同じ適用)で生成する。追加で、**API費用0の後処理のみで「Voice part減速なし」版Stdを作り、試聴ページに比較として併置**(Family Zでは会話減速なしが採用済みのため、同種の判断材料を無料で得る)。TTS呼出は増やさない。
- Gate判定器 gpt-6-luna の継続使用(25節例外・M7で検出同等・費用1/7)を Trial範囲で承認。報告に使用モデル名/最新か/理由を明記。
- Pro系TTS不使用。X/Z Production .py・Prompt・flag・閾値の変更0。Family Y機能はProduction到達経路に入れない(既存test `test_no_production_reference` 等を維持)。

## 2. 実施
- DEV runner(er110系)でTTS→ASR検証(既存のX相当の音声QA: segment PASS/HR Lock/retry/fallback/KP3V相当があれば適用、無ければ適用しなかった検査名を列挙)→assemble(Std/Adv全編)。Master Audio Store manifestを使う場合はTrial名前空間を分け、Production reuse_keyと衝突させない(方法を報告)。
- 試聴ページ `user_test/family_y_trial_01/index.html`(新規): 候補R2g/R0g×Std/Adv切替、全編通し再生、パート別(5パート)再生、全スクリプト、KP(あれば)と意味・解説、Voice Cardの要約(人物設定)表示、Std「減速あり/なし」比較、開発者向け情報非表示。「Trial(未採用)」の明示。commit/push後にHTTP 200+Playwright全audio実再生+ページ標準検査。
- 品質確認(Fable受入資料): 一人称保持・5パート構造が音声でも成立(パート境界、話者切替の明瞭さ)、Voice別F0/話速の実測(3Voiceの聞き分け可能性の数値材料)、Std/Advの長さ、ASR不一致箇所、PASS_WITH_WARNING相当の列挙。
- 費用: run毎の raw_usage_log 等を出典に記事セット単価(text+audio、R0/R2別)と、Xの直近実績(87.87円/セット、FAMILY-X-NEWS-2ARTICLES-E2E-02 記事B)との比較。

## 3. 成果物8項目の材料整理
`docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_01/TRIAL_SUMMARY_01.md` に、ユーザー原文の成果物8項目へ1対1で対応する節を作り、各節に該当資料へのパス・要点・数値を置く(新規評価はせず既存資料の集約)。Fableが独立評価するための読取対象(R2g/R0gの日本語完成稿・英語Std/Advのパス)を先頭に列挙。

## 4. SSOT・Git
- OPEN-463 Status=`TRIAL_PHASE3_DONE_PENDING_FABLE`(費用通算)、REPORT_LEDGER、DECISION_LOG(Phase 3範囲のFable判断)。UDR登録はしない(Fableが最終報告時に起票)。
- 明示add(mp3のみ)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。
- 全回帰は最後に単独実行し、failedを分類(`er019_family_x_fx_20261016_wiring_01_test_01 ...do_not_read_kp_english_entries` の readers集合に他委任の新規file `er019_nws2_eval_01.py`/`er063_family_z_audio_01_smoke_01.py` が入る件は既知・他委任由来。自分の新規fileが入ったら自分で対処)。

## 5. 禁止
- `VALIDATED`/採用の自己宣言、Production配線、Voice変更、Prompt/設計の変更(発見した設計課題は記録のみ)、追加の本文生成(R0g/R2gの既存稿を使う。Gate未通過稿は音声化しない)、有料run再起動(TTSは候補ごとに起動1回。失敗時は原因・証跡・選択肢を報告して終了)、250円超過。

## 6. 報告(docs/pm/RESULT_PACKET_FYT2.md、同内容を最終報告)
(1)音声化した候補と費用(通算/250) (2)音声QA結果 (3)試聴URL+再生検証 (4)Voice別実測(F0/話速)・長さ (5)Std減速あり/なしの差 (6)TRIAL_SUMMARY_01の場所と8項目対応表 (7)残課題(委任_04の10項目の残課題を引継ぎ、設計課題=M1衝突/背景fact 0件化/語り口同質性/B3偏り/Gateが台帳Factを消す点)の現状 (8)commit・raw URL・SSOT・全回帰 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。