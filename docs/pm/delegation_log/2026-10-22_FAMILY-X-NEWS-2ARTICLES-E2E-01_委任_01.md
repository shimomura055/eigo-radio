FABLE-DELEGATION-MARKER: FX-NEWS-2ARTICLES-E2E-委任_01-20261022

管理ID: FAMILY-X-NEWS-2ARTICLES-E2E-01(新規OPEN採番)。目的: ユーザー選定の新規ニュース2記事を、Family Xの**現行正式Production経路**(本日PRODUCTION_WIREDになったKP全文選定3件化・3-ASR多数決・固有名詞アラーム方針を含む最新の承認済み仕様)で、Standard(a2)/Advanced(b1b)の2レベル制作→音声化→品質検査→試聴ページ公開まで完了させる。**新規Trial・新仕様・DEV/Trial経路の代替・未承認の改善案の採用は禁止。** 本案件の費用上限=**300円**(7-7自律枠。見込み約100〜160円。超過見込み時は実行前にSTOPして報告)。本日(2026-10-22 JST)の日次上限は1,500円(ユーザー例外、現在累計≈971円)。

## 0. 最初に読む・保存する
- `docs/pm/PM_BRIEF.md`、`.claude/agents/sonnet-worker.md`、PM_GOVERNANCE 26節(有料runの再起動禁止・STOPセンチネル)・8節・7-7
- 前例(正式E2Eの手順と試聴ページ形式): 記事A paycheck_personality e2e_02(`user_test/paycheck_personality_e2e_02/index.html`、その生成に使ったrunner/pageスクリプト、`docs/pm/delegation_log/`のB3RD 委任_06〜08、`docs/pm/RESULT_PACKET_B3RD*.md`があれば)。合同検証の手順書 `docs/research/JOINT-RUNTIME-EVIDENCE-01/PROCEDURE_01.md`(X起動コマンド・Store競合の注意)、`RESULT_01.md`。
- ユーザー原文を `docs/pm/delegation_log/2026-10-22_FAMILY-X-NEWS-2ARTICLES-E2E-01_USER.md` へ見出しから末尾まで**逐語**保存(下記§7)。T-0保存 `..._委任_01.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: FX-NEWS-2ARTICLES-E2E-委任_01-20261022` 一致で確定)。

## 1. Fableの解釈(そのまま適用。報告に明記)
- ユーザー原文§2の「Primary/Secondary両方PASS必須ルールを含め、最新の承認済み仕様に従う」は、**最新の承認済み仕様=本日PRODUCTION_WIREDの3-ASR多数決**(両PASS→PASS、片側NG→Whisper決選、両NG→NG。OPEN-451、CURRENT_SPEC KP節)として適用する。コードの切替・flag変更は一切行わない(現行Production既定のまま)。
- 固有名詞アラーム方針(OPEN-450、X=PRODUCTION_WIRED)・KP全文選定3件化(OPEN-454)も現行既定のまま。
- 記事テーマはユーザー選定済み(テーマ選定ルールの例外不要)。

## 2. 記事の入力(topic/source brief。正式経路のWriter入力形式に合わせる。文言の創作はWriterに任せ、事実制約は厳守)
記事A: 「AIと一緒に書いた小説に、文学賞が誕生」— フランスで、AIと人間が共同執筆したフランス語フィクション対象の新文学賞「Prix Pascal」が設立。参考: RTÉ/AFP 2026-10-21 https://www.rte.ie/news/newslens/2026/1021/1596348-ai-literary-prize-france/ 。**事実制約**: 賞は新設されただけで受賞作は未決定。審査員・賞金は未確定として扱う。
記事B: 「TeslaとSpaceXが合併？ イーロン・マスクの巨大構想」— マスクが合併に前向きな姿勢を表明、両社が特別委員会を設け可能性を検討。参考: Reuters 2026-10-21 https://www.marketscreener.com/news/tesla-spacex-deal-wall-st-says-inevitable-but-musk-says-it-s-not-certain-ce785cd8d081f227 、補足 Reuters 2026-10-22 https://www.marketscreener.com/news/musk-s-public-endorsement-of-spacex-tesla-deal-may-throw-a-wrench-in-talks-ce785cd9df8ef622 。**事実制約**: 合併は未決定・検討段階、株主承認等のハードルを正しく伝える。
- 制作開始時点の最新情報確認と既存のResearch・Fact検証仕様(B3、Fact管理)は正式経路の工程で実施(参考URLは出典として渡す。取得はread-onlyで、取得物は専用dirに置き実行しない)。
- slugは短い英語(例 `prix_pascal_ai_novel_prize`、`tesla_spacex_merger_talks`)。run dirは正式経路の既定配置、style profileは正式既定(`fx_20261017`)。

## 3. 実行方針
- 事前: `git status`でProduction .pyの未commit差分が無いこと、STOPセンチネル(`tools/stop_scope_check_01.py`等)rc=0、`TTS_EXECUTION_MODE=STANDARD`、HEADに45a73d118(Closeout)が含まれること。
- 並列化: 2記事の本文生成・KP段(選定〜gloss〜解説)は並列可。**TTS/assemble段はMaster Audio Store manifestの非atomic書込のため2記事間で直列**(A→B)。RESTART_STORM・自己timeoutの短縮設定はしない(長時間runはバックグラウンド+ログpolling)。
- 不具合時: 承認範囲内の技術不具合は原因切り分け→最小修正→test→commit→失敗部分のみ再実行(走行中の有料runの再起動禁止)。**HR Lock・STOP・Gateの迂回禁止、人工entry禁止**。KP音声や本文がHR/STOPに至った場合は、それ以上の再生成を独断で行わず、該当run・attempt・ASR転写・音声pathを証拠として整理し「完成候補(HR待ち)」として報告(OPEN-456 F3のAzure数値整形問題が既知。該当した場合はその旨を記録)。KP選定の外側retry枯渇(`kp_stage_failed.json`)も同様に証拠を残して報告。
- 仕様変更が必要/安全問題/300円超・日次1,500円超の見込み/自律解決不能は即STOP報告。

## 4. 完了条件(記事×レベルごと)
(1)正式経路で本文・KP・音声を生成 (2)必須Validator・ASR・品質検査PASS (3)retry/fallback整合の確認 (4)runtime evidence保存(entry_point/raw_usage_log/attempts/audit/kp vote記録/pronunciation alarm報告) (5)全編通し再生・パート別再生が可能な試聴ページを公開(GitHub Pages、`user_test/<slug>_e2e_01/index.html`。従来ページと同形式、新機能開発不要。`tools/user_test_page_standard_check_01.py`でPASS、再生検証scriptでplays_ok全件) (6)Preview/Comment/Full Story/In One Line等の全スクリプトとKP(英語・日本語意味[Std]・英語解説[Adv])を掲載 (7)SSOT・Git。
- 試聴ページbuilderは前例(e2e_02)の記事固有scriptを新slug用に複製・最小修正してよい(Production経路のファイルは触らない)。

## 5. 費用・評価の記録
- 実費は各runの`raw_usage_log.jsonl`/cost_logから記事ごと・stage別(本文/Research・Fact/KP chain/TTS/ASR/解説/その他)に集計し、記事セット(2レベル)あたりの量産単価見込みを出す(出典付き。単価未登録の呼出は「未計上」と明記)。
- 使用モデル・Voice・主要routing(Writer/QA/KP選定=gpt-6-luna/gloss/解説/TTS=gemini-3.8-flash-lite-tts等/Primary・Secondary・Whisper ASR)を記録。
- 固有名詞アラーム・KP投票の発火記録があれば件数と内容を記録(Musk/Tesla/SpaceX/Prix Pascal等)。

## 6. SSOT・成果物・報告
- 新OPEN(採番は直前Grep、Status=`E2E_COMPLETE_CANDIDATE_PENDING_USER_LISTEN` または `E2E_PARTIAL_HR_PENDING`)、`docs/pm/REPORT_LEDGER.md`1行(費用出典付き)、DECISION_LOGは不要(仕様変更なし)。
- `docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/RESULT_01.md`: 記事ごとに Std/Adv Status・試聴URL・品質検査結果と未解決・runtime evidence path・モデル/Voice/routing・実費と単価見込み・commit。
- commit(自分のファイルのみ `git add <file>`、`-A/-u/-f`禁止)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。試聴ページ公開後にHTTP 200を確認。
- `docs/pm/RESULT_PACKET_FXN2.md`に4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去・残置)+判定整合行。ACTIVE_TASK固定ヘッダ更新。最終ユーザー試聴PASSはユーザー本人の判断(AIが代行しない)と明記。

## 7. ユーザー原文(逐語保存用)
# Family X 新規ニュース2記事 — 正式Production E2E制作指示

## 1. 目的・対象

以下のニュース2件を、Family Xの現行正式Production経路で制作してください。

各記事ともStandard／Advancedの2レベルを作成し、音声化・品質検査・最終試聴ページ公開まで完了させること。

### 記事A：AIと一緒に書いた小説に、文学賞が誕生

- 内容：フランスで、AIと人間が共同執筆したフランス語のフィクションを対象とする「Prix Pascal」という新しい文学賞が設立された。
- 参考記事：[RTÉ / AFP（2026年10月21日）](https://www.rte.ie/news/newslens/2026/1021/1596348-ai-literary-prize-france/)
- 注意：文学賞が新設されたのであり、すでに受賞作が決まったわけではない。審査員や賞金が未確定である点も正確に扱う。

### 記事B：TeslaとSpaceXが合併？ イーロン・マスクの巨大構想

- 内容：イーロン・マスクがTeslaとSpaceXの合併に前向きな姿勢を表明。両社が特別委員会を設け、合併の可能性を検討している。
- 参考記事：[Reuters（2026年10月21日）](https://www.marketscreener.com/news/tesla-spacex-deal-wall-st-says-inevitable-but-musk-says-it-s-not-certain-ce785cd8d081f227)
- 最新補足：[Reuters（2026年10月22日）](https://www.marketscreener.com/news/musk-s-public-endorsement-of-spacex-tesla-deal-may-throw-a-wrench-in-talks-ce785cd9df8ef622)
- 注意：合併は未決定。検討段階であること、株主承認などのハードルを正しく伝える。

両記事とも制作開始時点の最新情報を確認し、既存のResearch・Fact検証仕様を遵守すること。

## 2. 実行方針

- 新規Trialではなく、**現行承認済みProduction仕様をそのまま使用**する。
- 現行の正式初回Production経路から実行する。DEV／Trial専用経路で代替しない。
- 記事構成、B3、Fact管理、英語レベル、Key Phrase選定、音声Role、Voice、速度、TTS、ASR等はすべて現行仕様を適用する。
- Key Phrase音声は直近承認したPrimary（OpenAI）／Secondary（Azure）の両方PASS必須ルールを含め、最新の承認済み仕様に従う。
- retry／fallback／regeneration／resumeも正式経路の仕様を適用する。
- 新仕様や未承認の改善案を独断で採用しない。

## 3. QCD・実行効率

優先順位は **品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用**。

- 2記事および各レベルの独立工程は可能な限り並列実行。
- 共通リソースの競合がある工程のみ適切に直列化する。
- 不要な再調査、再生成、追加Trial、日付分割、待機を行わない。
- 承認済みの品質水準を満たしたら追加の磨き込みをせず完成させる。
- 量産単価70円／記事セットを目標に、品質を犠牲にしない範囲でコストを最適化する。
- 既存承認範囲内の技術的不具合はFable／Claudeで自律解決する。

既存の日次予算・個別承認枠・STOP条件を遵守すること。予算や承認範囲を超える場合は停止して報告する。

## 4. 完了条件

各記事・各レベルについて、以下を満たすこと。

1. 正式Production経路で本文・Key Phrase・音声を生成。
2. 必須Validator・ASR・品質検査がPASS。
3. 必要なretry／fallback処理との整合を確認。
4. 実際のProduction runtime evidenceを保存。
5. 全編通し再生・パート別再生が可能な試聴ページを公開。
6. Preview／Comment／Full Story／In One Line等の全スクリプトとKey Phrase（英語・意味・解説）を掲載。
7. 必要なSSOT・Git反映を実施。

試聴ページは従来のユーザー試聴ページと同等のシンプルな形式でよい。不要な装飾・新機能の開発は不要。

## 5. 最終報告

記事ごとに以下を簡潔に報告すること。

- Standard／Advancedそれぞれの完成Status
- 最終試聴URL
- 品質検査結果と未解決事項
- Production runtime evidenceの有無
- 実際に使用したモデル・Voice・主要routing
- 実費と記事セット当たりの量産単価見込み
- Git commit／SSOT反映状況

Fableは実装報告を独立検証し、Production Wiring Gateの充足を評価すること。

**最終ユーザー試聴PASSはユーザー本人の判断とし、AI側で代行しない。**

新たなユーザー判断が不要であれば、途中報告による停止を挟まず、2記事とも完成候補まで進めてください。