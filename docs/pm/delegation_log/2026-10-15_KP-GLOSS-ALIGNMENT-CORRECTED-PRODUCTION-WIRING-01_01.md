# 委任文(全文保存): KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_01(2026-10-15)

## 管理ID

`KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01`(略称KGCPW)委任_01(初回)。並行タスク衝突確認: 本セッションで他に走行中のAgentなし。前管理ID `KP-GLOSS-ALIGNMENT-PRODUCTION-01`(KGA、既定OFF安全措置=PRODUCTION_WIRED済)と`KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01`(KGDC、Trial VALIDATED)はCLOSE扱いとし、本管理IDが後継。`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day2はユーザー設計承認待ちでSTOP中(本委任で一切触らない)。

## 性質/到達上限Status/禁止事項

- 性質: **Production採用後の配線「設計」+ユーザー正式採用のSSOT記録**。本委任ではProductionコード・Prompt・flag既定値・test・runnerを**一切変更しない**(設計文書・SSOT・一時ファイルのみ編集)。配線実装はOpus条件Cレビュー後の委任_02で行う。
- 現在Status: `APPROVED_FOR_PRODUCTION`(2026-10-15ユーザー正式決定、下記原文)。本委任の到達上限: 設計完了+SSOT記録(`PRODUCTION_WIRED`は宣言しない。到達判定は管理ID全体の最終でFableが行う)。
- Opus独立技術レビューGate: 条件C該当(Production採用提案前→今回はユーザー採用済みのため「承認済み修正版がProductionへ安全に実装できるか」の実装前レビュー)。Fableが本委任の成果物を材料に依頼する。本委任ではOpusを呼ばない。
- 禁止: 有料API呼出(LLM/TTS/ASR/Web Search)0。費用上限=JPY0(本委任)。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。`er003_key_words_gloss_alignment.py`/`er003_v1_n3_01_scaffold_generate.py`/`er019_*`/`er026_*`/Prompt template/`.env`/testの編集禁止。Day2成果物(`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/`)・`CLAUDE.md`・Agent定義・`PM_GOVERNANCE.md`の編集禁止。新Validator/新Hook/新管理機構の増設提案は、既存機構で代替できないことを示した場合のみ可。採用範囲(ユーザー原文§1〜§3)を広げない。
- 時間見込み: 本委任 約1.5h(設計1.0h/SSOT0.3h/報告0.2h)。管理ID全体: 委任_01 1.5h→Opus条件C 0.5h→委任_02(実装+evidence)3〜4h→委任_03(是正・SSOT確定)1h。並列化: 本委任は単一Sonnet直列(同一設計文書への集約が必要なため)。委任_02ではFamily X evidenceとFamily Z evidenceを別run dirで並列実行する前提で設計せよ(共有state干渉の有無を本委任で特定すること。KGDC Regressionで共有state並列干渉が実際に起きた: VALIDATION_03 §3-2)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

- E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は最小化。F-1: transcript退避は不要。
- T-0: 受領した委任文を本ファイルへ保存し、`check_delegation_prompt.py`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
- T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示(本委任はTTS実行なし。委任_02のevidence計画に織り込む)。
- T-3: 本委任は費用上限JPY0のためGuardrail文は委任_02で記載する。

## ユーザー指示(原文、2026-10-15、ユーザー正式指示。全文)

# Claude Code／Fableへの正式指示
## KP gloss再整合工程：Production採用・E2E完成
**管理対象：KGDC修正Trial → Production正式採用・Wiring** / **現在Status：APPROVED_FOR_PRODUCTION** / **今回の到達目標：PRODUCTION_WIRED**

### 1. ユーザー正式決定
修正版gloss再整合工程を、**正式Production仕様として採用する**。以下の付随事項も承認する。
1. **追加語→日本語span機械検査**：強制NG Gateにはせず、記録・観測のみ継続する。
2. **Human Review例外の通知先**：HR報告書、run summary event、最終stdout、runのSTOP statusを利用する。既存の音声Human Review queueには混在させない。
3. **規則15行型（数値穴埋め句）の検出責任**：従来どおりKP選定段が担当し、再整合工程へ重複実装しない。
今回の採用対象は**修正版（corrected）**であり、旧legacy方式ではない。

### 2. Productionで実現する動作
KPの最終確定後、TTSおよびglossを利用する後続処理の前に、日本語glossと英語KPの意味整合を確認・必要に応じて修正する。
- 最終英語KPに対応した日本語glossを生成・確認する。
- 意味が既に一致しているglossは、不必要に書き換えない。
- 承認済みgloss規則を維持し、「〜」という表記自体を機械的なNG条件にしない。
- 修正に失敗した場合は最大2回まで試み、失敗後はHuman Review例外として報告する。
- Human Review待ちの不整合KPがTTS、Advanced B1英語解説、完成音声、公開ページへ流れないようにする。
- 解決後の再開経路も既存Production設計と整合させる。
既存Human Review Lockを、適合しない用途に無理に流用しない。

### 3. Production Wiring
**A. 初回Production経路** 修正版correctedを正式経路へ配線する。Production既定ONへ切り替える。旧legacy方式を撤去し、correctedと誤って共存しないようにする。Standard／Advanced、Family X／Zの対象経路へ適用する。DEV／Trial専用scriptだけに存在する状態を解消する。
**B. 後続経路** retry、fallback、regeneration、cache再利用、Human Review後の再開も含めて整合を確認する。失敗時に古いglossへfail-openしない。再整合が必要なKPだけを正しく対象にする。対象外KPのglossは変更しない。
**C. 異常時の完成禁止** 2回失敗時に非OK statusを返す。既存Audio Validation Gateで完成を禁止する。Family Zは既存FamilyZE2EStopを使用する。Advanced B1英語解説とページ表示への流出も防ぐ。HR報告書、run summary、stdout、STOP statusで例外を追跡できるようにする。
**D. Dangling Reference Check** 新しい仕様・Prompt・Validatorの参照先が、承認済みProduction仕様および正式初回経路に存在することを確認する。retry／fallbackだけに存在する仕様や、Trial専用定義への暗黙依存を認めない。

### 4. Opusレビュー
Production配線前に、前回報告の**Opus条件C（採用提案前レビュー）**に対応する独立レビューを実施する。※今回はユーザー採用判断が既に完了しているため、Opusは採用可否を再決定するのではなく、**承認済み修正版がProductionに安全に実装できるか**をレビューする。最低限、以下を確認する。既存承認済みgloss規則との整合/旧legacy方式の撤去範囲/正しいglossの不要な書換え/失敗時の完成禁止とHuman Review通知/Standard／Advanced・Family X／Zの後続工程/retry／fallback／regeneration/QDCと量産単価/`OPEN-359`のFamily X NG_REVIEW_REQUIRED素通り疑いが今回の完成禁止Gateを迂回しないか。Opusレビュー原文を保存し、所見ごとの対応・残存リスクを記録すること。**BLOCKERが出たら是正・必要な差分再レビューを行う。重大な仕様変更が必要になった場合は、勝手に採用範囲を広げずSTOPして報告する。**

### 5. 必須検証とruntime evidence
単なるUnit test PASSやTrial script成功では完了にしない。修正版のUnit／Regression／Validator／integration test/Family X／Zの正式Production runnerでの実LLM発火確認/Standard／Advancedの適用確認/初回・retry・fallback／regeneration経路の整合/実際のgloss修正と不要な書換えがないこと/異常時のHR例外、TTS・英語解説・assemble・公開ページの完成禁止/HR解決後の再開/actual model_id、routing、API使用量、量産費・追加時間/Production正式経路でのE2E完成確認。異常経路は、必要に応じて制御された失敗注入を利用すること。実LLMが自然に2回失敗するまで無益なTrialを繰り返さない。mock／失敗注入と実LLM evidenceは区別して報告すること。**重要：OPEN-359が未解決のまま、Family Xで不整合KPが完成版に流出しうる場合、PRODUCTION_WIREDを宣言しない。**

### 6. QDC・実行方針
Q：意味整合と完成禁止を優先する。ただし過剰な誤NGや不要なHuman Reviewを増やさない。D：既存実装・検証成果を再利用し、無益なTrial、重複レビュー、全記事再生成を避ける。並列化できる独立作業は並列化する。C：追加量産単価のTrial見込み（通常0.014〜0.08円／記事セット）とProduction実測を比較する。70円目標への影響を確認する。費用は既存承認済みの予算・停止規則を守る。予算超過や重要な仕様変更を独断で承認しない。

### 7. SSOT・Git
CURRENT_SPEC：corrected正式仕様、適用条件、失敗時動作/DECISION_LOG：今回のユーザー正式採用と付随事項3件/OPEN_ITEMS：該当項目の更新・close、OPEN-359との関係/OPUS_FINDINGS_LEDGER：所見原文との整合・対応状況/必要なRegression／runtime evidence/commit／push／必要なmergeの証拠。OPEN-359など別件の不具合については、影響が今回の受入条件に及ぶ範囲で対応する。独断で大幅な仕様変更へ発展させない。

### 8. 完了判定
FableがSonnet／Opusの報告を独立評価すること。`PRODUCTION_WIRED`には、以下の全条件を必要とする。1.承認済みcorrected仕様が正式初回Production経路で動作。2.retry／fallback／regenerationと整合。3.DEV／Trial専用実装ではない。4.Family X／Z、Standard／Advancedで必要なruntime evidenceを取得。5.必要テストPASS、既存failureの影響を評価。6.失敗時の完成禁止とHuman Review通知を確認。7.QDC上の重大な悪化なし。8.CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS反映。9.Git反映完了。10.ユーザーの承認内容と実際のProduction挙動が一致。一つでも未確認なら`APPROVED_FOR_PRODUCTION`のまま管理し、未完了項目と理由を報告する。

### 9. STOP条件
Opusが重大な仕様矛盾・安全性BLOCKERを発見した/ユーザー承認外の仕様変更が必要/不整合glossが完成物に流れる可能性が解消できない/明示STOP／予算上限／承認境界に抵触/既存Production機能に重大なRegressionが発生。技術的に自律解決可能な問題は、承認済み範囲・予算内で原因調査、修正、再検証する。小さな改善のたびにユーザーへ判断を求めない。

### 10. 報告形式 (略: 超サマリ→現在Status/実装経路/Opus所見と対応/X・Z・Std・Adv runtime/異常系/Regression・QDC・費用/SSOT・Git/未解決・残存リスク/ユーザー判断の有無)
**目標は、承認済み仕様を本当に量産運用できる状態へ完成させること。コード変更やTrial成功だけで完了としないこと。**

## KPI provenance欄

本委任は設計のみ(KPI測定なし)=該当なし。ただし設計文書§7(evidence計画)では、委任_02で取得する各evidenceのprovenance区分(fresh/reuse/synthetic[mock・失敗注入]/production_formal_path)と「E2E自己確認=fresh Production初回pathを含むか」を計画段階で明記すること。

## Opus台帳更新

OF-225〜235(KGA)・OF-KGDC-01〜12(KGDC)は本管理IDで`EVIDENCED→CLOSEOUT_CONFIRMED`へ進む候補。本委任では遷移させず、設計文書§9に「各所見の現在状態と、委任_02で何を確認すればCLOSEOUT_CONFIRMEDにできるか」の表を作るのみ(台帳本体は編集しない)。OF-KGDC-11=OPEN-359は本管理IDの受入条件に直結(ユーザー§5)。

## 事前指定Read一覧
(下記Read一覧)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Read: ACTIVE_TASK.md:1-12、DESIGN_DRAFT_01.md、VALIDATION_03.md、INVESTIGATION_01.md(§7/NG_REVIEW_REQUIRED)、HR_RESOLVE_PROCEDURE_01.md、OPUS_REVIEW_01_VERBATIM.md(BLOCKER|Lock|fail-open|legacy)、VALIDATION_OFF_01.md §1〜§8、OPEN_ITEMS.md:861-868、CURRENT_SPEC.md:2630-2636、DECISION_LOG.md(gloss再整合|GLOSS_ALIGNMENT)、OPUS_FINDINGS_LEDGER.md:252-262+OF-KGDC-、PM_GOVERNANCE 26節/11-5、USER_DECISION_REGISTER_01.md(gloss|OPEN-359|OPEN-356)。
- Grep(読取のみ・編集禁止): er003_key_words_gloss_alignment.py、er003_v1_n3_01_scaffold_generate.py(入口L734付近)、er019 runner、er026 runner、gloss消費側全列挙rg、Trial専用定義洗い出し、既存Audio Validation Gate、HR通知先。
- 追記位置: DECISION_LOG.md(既存2026-10-15 glossエントリ群の直後+索引1行)/OPEN_ITEMS.md OPEN-356(要約更新、3,000字超なら履歴はOPEN_ITEMS_HISTORY.md)・OPEN-359(受入条件直結を追記)/CURRENT_SPEC.md:2635付近に事実行1行/docs/pm/USER_DECISION_REGISTER_01.md gloss採用UDR行を判断済み区分へ/docs/pm/REPORT_LEDGER.md末尾1行/docs/pm/ACTIVE_TASK.md冒頭固定ヘッダ上書き(旧ヘッダは「前タスク群(保持)」へ1ブロック退避)。

## 実行コマンド全文

- T-0検証: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_01_check.json`
- STOP確認: `.venv\Scripts\python.exe tools/stop_scope_check_01.py --json`(引数が異なる場合は`--help`で確認して実行し、実コマンドを報告)
- test件数把握(収集のみ)、`git status --porcelain`(作業前後)、`git log --oneline -3`
- 有料API・TTS・runner実行は本委任では行わない。

## 設計文書の必須構成

`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/PRODUCTION_WIRING_DESIGN_01.md`(新規)。§0超サマリ(10行以内)/§1現状配線図/§2 legacy撤去範囲(撤去残置検出Grepパターン固定、GLOSS_ALIGNMENT_MODE廃止推奨)/§3既定ON設計(kill switch残置の是非)/§4後続経路整合表/§5完成禁止経路の実装対応表/§6 OPEN-359実コード確認/§7 Runtime evidence計画(失敗注入方式の比較、X/Z並列と共有state干渉)/§8 Dangling Reference Check/§9 Opus台帳対応表/§10 QDC見込み/§11 Opus条件Cレビュー用論点(8項目以内)/§12 委任_02作業分解/§13 確認できなかった事項。

## SSOT追記文

DECISION_LOG.md: 「2026-10-15 | KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 | ユーザー正式決定: 修正版(corrected)KP gloss再整合工程を正式Production仕様として採用(`APPROVED_FOR_PRODUCTION`)。付随事項3件を承認: (1)追加語→日本語span機械検査は強制NG Gateにせず記録・観測のみ継続 (2)Human Review例外の通知先はHR報告書・run summary event・最終stdout・runのSTOP status(既存音声Human Review queueへ混在させない) (3)規則15行型(数値穴埋め句)の検出責任は従来どおりKP選定段、再整合工程へ重複実装しない。採用対象はcorrectedであり旧legacyではない(legacy撤去)。Production既定ONへ切替・Family X/Z・Standard/Advanced配線・retry/fallback/regeneration/cache再利用/HR再開の整合・異常時完成禁止(Audio Validation Gate/FamilyZE2EStop/B1解説・ページ流出防止)を到達目標`PRODUCTION_WIRED`の条件(10条件)とする。配線前にOpus条件C(実装安全性)レビュー必須。OPEN-359未解決でFamily Xから不整合KPが完成版へ流出しうる場合はPRODUCTION_WIREDを宣言しない。Status: APPROVED_FOR_PRODUCTION(配線中、本エントリ時点ではコード無変更・既定OFF継続)。出典: ユーザー指示原文(本ファイル「ユーザー指示(原文)」)。」
CURRENT_SPEC事実行: 「【2026-10-15追記(KGCPW 委任_01)】修正版(corrected)gloss再整合工程はユーザー正式採用`APPROVED_FOR_PRODUCTION`(付随事項3件: 機械検査=記録のみ/HR通知先=報告書+run summary+stdout+STOP status、音声HR queue不使用/規則15行型=選定段責務)。配線は委任_02以降。本行時点ではProduction既定OFF・legacy既定のまま(未配線)。」
OPEN_ITEMS: OPEN-356=「`APPROVED_FOR_PRODUCTION`(2026-10-15ユーザー正式採用、修正版corrected)・配線中(KGCPW)・既定OFF継続(配線完了まで)」。OPEN-359=「KGCPWの受入条件(ユーザー§5: 未解決のまま流出しうる場合PRODUCTION_WIRED不可)に直結。本管理IDで影響範囲に限り対応」。

## Git

SSOT編集権: あり(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/docs/pm/REPORT_LEDGER。PM_GOVERNANCEはなし)。単一Sonnet直列のため8-Y衝突なし。明示add: 設計文書、DECISION_LOG.md、OPEN_ITEMS.md(必要なら OPEN_ITEMS_HISTORY.md)、CURRENT_SPEC.md、docs/pm/USER_DECISION_REGISTER_01.md、docs/pm/REPORT_LEDGER.md、docs/pm/ACTIVE_TASK.md、docs/pm/RESULT_PACKET_KGCPW1.md、本ファイル(+_check.json)。作業ツリーの既存未コミット変更(er0XX_output配下のtelemetry等多数)は触らない・addしない。
コミットメッセージ: 「KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_01: ユーザー正式採用(corrected、付随事項3件)をSSOT記録+Production配線設計(legacy撤去範囲・既定ON・後続経路整合表・完成禁止対応表・OPEN-359実コード確認・evidence計画・Dangling Ref)。コード/Prompt/flag無変更、JPY0」。push to origin/main。conflict時はSTOPして報告。

## 報告(RESULT_PACKET_KGCPW1.md項目)

(1)T-0結果 (2)STOP確認結果(実コマンド) (3)設計文書§0超サマリ転記 (4)OPEN-359の結論(事実/事実でない、流出経路の有無、最小修正案と行数) (5)legacy撤去範囲の要約(関数/分岐/test/Trial参照の件数) (6)後続経路整合表で委任_02追加実装が必要なセル一覧 (7)完成禁止の既存で満たす/追加必要の件数 (8)evidence計画の総費用見積り(出典付き、未確認は未確認)と推奨失敗注入方式 (9)Dangling Reference検出有無 (10)Opus条件C用重要論点(§11転記) (11)SSOT変更差分(ファイル:行、追記文) (12)commit hash・push結果・raw URL(設計文書・RESULT_PACKET) (13)確認できなかった事項・推定と事実の区別 (14)委任文からの逸脱と理由。
本委任の受入はFableが行う(受領≠受入)。Fableは設計文書§1・§2・§6・§7を自分で読んで照合する前提で、行番号・関数名・観測値を省略せず書くこと。

(注: 本ファイルは委任文の全文保存。事前指定Read/Grep一覧と固定ブロックの詳細列挙は要約形で保存した。ユーザー指示原文とSSOT追記文・Git・報告項目は原文どおり。)
