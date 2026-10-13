# FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_01 (委任文全文、2026-10-13)

## 管理ID

FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_01(初回: 配線設計のみ、¥0、Production code無変更。実装はOpus条件Aレビュー後の委任_02)。並行タスク(同時稼働、いずれも触らない): ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01(`er068_*`、SSOT編集中の可能性)、FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_02(`er069_*`)、FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01(`er070_*`、OPEN-338/DECISION_LOG編集)。本委任は**SSOT編集権なし**(SSOT追記文案はRESULT_PACKETに記載のみ)。一時ファイル: `docs/pm/ACTIVE_TASK_XZW.md`/`docs/pm/RESULT_PACKET_XZW.md`。出力: `er071_output/m2p0_n01_production_wiring_01/`。git: `.git/index.lock`存在時は30秒待ち×3回、commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(M2P0・N01を`APPROVED_FOR_PRODUCTION`、Family X/Z両方)に基づくProduction配線の**設計**(配線点の特定、差分設計、回帰・runtime evidence計画、費用見積)。本委任ではProduction codeを変更しない。
- 到達上限Status: 設計=`WIRING_DESIGN_DRAFT(Opus条件A待ち)`。`PRODUCTION_WIRED`宣言禁止(委任_02以降、Checklist全充足時のみ)。
- 費用: 上限¥0(有料API禁止。Family X音声化の費用見積は出典付き単価で算出し、未確認単価は「未確認」)。
- 禁止: Production code・Prompt・Validator・Gateの編集、ユーザー未承認の仕様変更、新Prompt探索・追加Trial、M2P0以外のKP選定方式/N01以外のメイン音声Promptへの変更、Validatorの緩和、Family Z Previewの先行採用、Family Zの記事再生成・音声化、未承認の連結発音改善ロジック(er065/er068系)の混入、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`のsource・値表示、秘密値の出力、`*.wav`・telemetry・log・`words/`のadd、`ACTIVE_TASK*.md`/`RESULT_PACKET*.md`のcommit、Melos run_e2e_02配下・Master Store・HR queue・attempt_history・telemetryへの書込、外部停止プロセスの再起動、監督ループ/`timeout`ラッパ。
- STOP条件: 承認範囲を超える仕様変更が必要と判明(例: N01をFamily Zへ適用するには文言変更が要る、M2がFamily Z KP経路に構造上載らない、既存GateやSlowdown仕様の変更が必要)→その箇所を設計書に`USER_DECISION_REQUIRED候補`として明記しFableへ報告(設計自体は継続してよい)。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。Family Zの記事再生成・音声化STOPは本委任でも厳守(読取のみ)。
- Opus独立技術レビューGate判定: **条件A該当**(Production初回経路・retry/fallback/regenerationに関わる処理フロー変更の実装前)+**条件C**(重要変更のProduction採用。ユーザー採用判断は済みのため、レビューは技術品質のみ)。本委任完了後にFableがOpusレビューを起動する。
- 時間見込み: 60〜90分(KP経路調査25/TTS style経路調査20/差分設計20/計画・見積15)。並列化: 他3agentと並列。本委任内のKP調査とTTS調査は独立(順不同)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**委任文は要旨ではなく本文全文を保存すること。**
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSなし。委任_02のFamily X音声化では`TTS_EXECUTION_MODE=STANDARD`を明示する前提で設計(差分再生成の可否・音声再利用キャッシュ・`--budget-jpy`の有無も設計書に記載)。
T-3: 本委任は¥0のためCap継続条件は適用しない。

## ユーザー指示(原文)

(2026-10-13、管理ID FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01。全文)
「## 1. ユーザー正式決定 以下の2仕様を正式Production採用する。Key Phrase: M2P0/メイン音声Prompt: N01。適用対象はFamily X・Family Zの両方。両仕様のStatusを`APPROVED_FOR_PRODUCTION`として扱い、Production正式経路への反映を進める。ただし、Familyごとに記事再生成・音声化の実行許可が異なる。
## 2. Family別の実行範囲 | 項目 | Family X | Family Z | M2P0 Production実装 GO/GO | N01 Production実装 GO/GO | 必要なRegression・配線確認 GO/GO | 記事再生成 必要に応じてGO/STOP | 音声化 GO/STOP | 完成記事の生成 GO/STOP。Family X: M2P0・N01をProduction正式経路へ実装し、必要な品質検査・再生成を含めて、音声化まで進める。Family Z: M2P0・N01のProduction実装と、記事再生成・音声化を伴わない検証のみ進める。Standard Previewの仕様が正式に決定するまでは、記事再生成・音声化を実施しない。PreviewのTrial成功だけではGOとしない。ユーザーの正式採用判断および必要なProduction反映が完了した段階で、Family Zの記事再生成・音声化を再開する。
## 3. Production Wiring要件 M2P0・N01について、Family X/Zそれぞれで以下を確認する。1.Production正式初回経路に実装されていること 2.retry/fallback/regenerationとの整合が取れていること 3.DEV・Trial専用scriptだけに存在する状態ではないこと 4.必要なRegression/Validator/integration testがPASSすること 5.Production正式経路でruntime発火を確認すること 6.必要なactual model_id・routing等のruntime evidenceを確認すること 7.CURRENT_SPECを更新すること 8.DECISION_LOGを更新すること 9.OPEN_ITEMSをclose/updateすること 10.必要なcommit/push/merge等のGit反映を確認すること 11.ユーザーの承認内容と実際のProduction挙動が一致すること。Family Zは記事再生成・音声化STOPを優先する。そのため、Family Zで必要なruntime evidenceをSTOP条件に抵触せず取得できない場合、未確認として残すこと。推測やDEV/Trial結果で代替せず、`PRODUCTION_WIRED`と判定しない。
## 4. 音声品質とN01の取り扱い N01は正式採用するが、品質判定条件の緩和は承認していない。既存のASR品質判定を維持/既存の速度・ポーズ等の品質基準を維持/不合格時は既存のretry/fallback/STOP条件に従う/Standardの6%減速仕様を維持/Standardの減速後再検証も維持。既存品質Gateを無効化したり、合格するまで無制限に再生成したりしないこと。
## 5. 連結発音・ASR改善との関係 `Melos said`を契機とした連結発音・ASR発音同等性の一般化は、別管理IDで並行進行中。今回のProduction反映作業には、その未承認の改善ロジックを混ぜないこと。既存の承認済みASR品質判定は維持する。連結発音の改善作業を理由にFamily Xの音声化を停止しない。一方、Family Zの記事再生成・音声化STOPは引き続き厳守する。
## 6. 変更範囲・禁止事項 今回の作業は、M2P0・N01のProduction採用と、Family Xの音声化に必要な範囲に限定する。禁止: ユーザー未承認の仕様変更/新Promptの探索・追加Trial/M2P0以外のKey Phrase選定方式への変更/N01以外の新しいメイン音声Promptへの変更/Validatorの独自緩和・変更/Family Z Previewの先行採用/Family Zの記事再生成・音声化/関係のないFamily・工程への変更。必要な実装上の判断は既存仕様・正式経路に従う。承認範囲を超える仕様変更が必要になった場合は、独自判断せずSTOPして報告すること。
## 7. Status・STOP条件 現在: M2P0 `APPROVED_FOR_PRODUCTION`/N01 `APPROVED_FOR_PRODUCTION`/Family Z Standard Preview: Trial結果の採否・正式仕様未確定/連結発音一般化: 別管理IDで進行中。目標: Family X: M2P0・N01の`PRODUCTION_WIRED`と音声化/Family Z: Production配線可能な範囲まで実施し、記事再生成・音声化はSTOP維持。`PRODUCTION_WIRED`はProduction Wiring Checklistをすべて満たした場合のみ使用する。必要なruntime evidenceが不足する場合は、未完了として明示すること。USER_DECISION_REQUIREDが生じた場合、または未承認の仕様変更が必要な場合は、その時点でSTOPする。
## 8. 最終報告 1.M2P0・N01のFamily X/Z別Production反映状況 2.初回・retry・fallback・regeneration経路の整合確認 3.Regression・Validator・integration test結果 4.runtime evidence(actual model_id、routing等) 5.Family Xの音声化結果・品質・試聴URL 6.Family ZのSTOP維持状況 7.CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSの更新内容 8.commit/push等のGit反映結果 9.Dangling Referenceの有無 10.未完了項目とUSER_DECISION_REQUIREDの有無。最重要: M2P0・N01はFamily X/Z両方への正式採用。Family Xは音声化までGO、Family ZはPreview確定まで記事再生成・音声化STOP。この範囲を超える独自の仕様変更・追加検証・改善作業は行わないこと。」

## KPI provenance欄

該当なし(設計のみ。委任_02でのruntime evidenceは`production_formal_path`/`fresh`を計画に明記)。

## Opus台帳更新

該当なし(委任_01はレビュー前)。

## 事前指定Read一覧

**M2P0側**
1. Trial実装: `er064_kp_int_01_machine.py` 全体構造(M2=(a)placeholder照合+(b2)ルール所有格3-gram+(c)予約枠cap3の関数名・入出力。`Grep -n "^def |placeholder|possessive|reserved|cap"`→該当範囲)。`er064_kp_int_01_run.py`の「M2 shortlist組立→選定P0→canonicalization→Redundancy QA」の呼出順(`Grep -n "M2|shortlist|select|canonical|redundan"`)。
2. Round 1報告 `er064_output/kp_integrated_opt_01/round1/ROUND1_REPORT_01.md` §2(M2定義・候補数・token・Wiktionary照会時間約43秒/記事の件)と、Round 3報告 §7-C/「Production化に必要な前提」。
3. Production KP経路(Family X): `Grep -rn "def .*key_?phrase|def .*shortlist|wiktionary_multiword_targeted_lookup|cap15|MAX_PRODUCTION_RETRY_ATTEMPTS" --include=er003_*.py --include=er00*_*.py --include=er01*_*.py` → 候補抽出(n-gram+Idiom DB→Wiktionary→shortlist)と選定(P0 Prompt定数の所在、`SUPPORT_MODEL`/routing契約 `er006_model_routing_contract_01.py`)の関数と行を特定し該当範囲のみRead。Family X記事生成runner(Coffee v5を生成した正式経路: `Grep -rn "coffee" --include=*.py -l | head`、および`docs/pm/delegation_log/2026-10-12_FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01_02.md`で使用runnerを確認)。
4. Production KP経路(Family Z): `er062_family_z_writer_01.py`/`er026_family_z_fiction_production_runner_01.py`の`kp` stage(`Grep -n "kp|key_phrase|KeyPhrase"`)→Family Xと同じモジュールを共有しているか、別実装か、M1(照会予算拡大)前提が成立するかを特定。
5. OPEN-310/325/336/337の行(`Grep -n "\*\*OPEN-(310|325|336|337)\b" OPEN_ITEMS.md`)。M2配線で影響する前提(Wiktionary照会時間、Rule7整合)を設計に反映。

**N01側**
6. N01の正式文言: `Grep -rn "A cheerful, kind storyteller" er057_output/ --include=*.json -l`→該当prompts jsonの該当エントリ(sha256 `d1956c91…`で確認)。逐語で設計書に転記(改変禁止)。
7. 現行Production TTS style(P8)の所在: `Grep -rn "Warm, bright, cozy storytelling" --include=*.py -l`→定数名・ファイル・行。P8がFamily X Full Story Std/Adv、Family Z narrator(Aoede)、Family Zのdialogue voices、Comment/Preview/KP等のどの経路でどう使われるか(`speech_metadata.style`の組立関数: `Grep -rn "speech_metadata|style=" --include=*.py`→`news_tail_fix.generate_news_narration_wide_margin`、`er063_family_z_audio_01.py real_generators().narrator`、`bvoices.generate_voice_body_wide_margin`等)。
8. Std 6%減速・減速後再検証: `er003_v1_n3_01_tts_generate.py` `Grep -n "def apply_a2_slowdown|def _post_slowdown_cascade_rescue|generate_a2_segment_with_slowdown"`→該当範囲(N01差替で経路が変わらないことの確認)。
9. retry/fallback(minimal instruction fallback `gemini-2.5-pro-preview-tts`等)のstyle扱い: `Grep -rn "fallback.*style|minimal_instruction|FALLBACK_STYLE" --include=*.py`→該当範囲(fallback takeにもN01を使うか、既存仕様どおり無styleか、を事実として記載)。
10. Trial時のN01生成条件: `er057_coffee_tts_style_h_speed_05_gen04.py`(model `gemini-3.8-flash-lite-tts`、voice Aoede、style渡し方)→Production経路のmodel/voiceと一致するか。
11. `docs/pm/PM_GOVERNANCE.md` 「Production Wiring Checklist」(`Grep -n "Wiring Checklist|PRODUCTION_WIRED"`→該当節)。
12. 費用根拠: `er057_tone_trial_final_build_03.py` PRICE_IN/PRICE_OUT(`Grep -n "PRICE_"`)、`docs/pm/delegation_log/2026-10-12_FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01_02.md`(Coffee 1記事音声化の実績費用)、PM_GOVERNANCE 15-8(1生成セット総原価の形式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

SSOT編集なし。上記Read一覧のGrepのみ。

## 作業内容(出力はすべて`er071_output/m2p0_n01_production_wiring_01/`)

### 1. `WIRING_DESIGN_01.md`(Opus条件A/Cレビュー用)
A. **M2P0**: (i)Family X Production候補抽出の関数Xに対し、Trial `er064_kp_int_01_machine.py`のM2関数をどう移植するか(Trial scriptからのimportは不可=Production moduleへ移設。Checklist 3「DEV/Trial専用scriptだけに存在する状態ではない」)。(a)(b2)(c)それぞれの挿入点・入出力・cap15との関係(予約枠cap3は外側)・候補行形式(`match:`注釈は付けない=M3ではない)。(ii)M1前提(照会予算拡大・precision guard・U2包含整理・U3断片注釈)がM2に含まれる点を明記し、Wiktionary照会時間約43秒/記事(429待ち)のProduction影響と、OPEN-337(オフライン索引)未実装のまま配線する場合の運用上の注意(timeout/retry設定の既存値)。(iii)選定Prompt=P0は現行Production逐語で**無変更**であることの確認方法(sha256)。(iv)canonicalization・Redundancy QA・`MAX_PRODUCTION_RETRY_ATTEMPTS=2`との整合。(v)Family Z: 同じmoduleを通るなら配線は共通、別なら差分設計。Family ZはKP再生成を伴う検証不可(STOP)→Checklist 5/6はFamily Zで「未確認」として残す設計。(vi)既存記事(Coffee v5等)の再生成要否: Family Xは「必要に応じてGO」なので、Coffee記事でKPをM2P0で再生成し音声化まで行う計画を立てる(KP再生成→KP音声(Std/Adv)→組立)。
B. **N01**: (i)P8定数の差替点(Family X Full Story Std/Adv、Family Z narrator)。N01は逐語(sha256一致)で、Std/Adv共通に同一文言。(ii)Family Zのdialogue voices・Comment/Preview/KP読み上げのstyleは**対象外**(メイン音声=Full Story narrationのみ)と解釈し、その解釈を明記。別解釈が必要ならUSER_DECISION_REQUIRED候補。(iii)N01の文言「sharing a true story」はFamily Z(Fiction)に対して意味上のズレがある可能性→**文言は変更しない**(N01以外への変更禁止)が、USER_DECISION_REQUIRED候補として記載。(iv)Std 6%減速・減速後再検証・ASR Gate・retry/fallback/STOP条件は無変更であることを経路ごとに表で確認(fallback takeのstyle扱いは既存仕様どおり)。(v)Trial(gen04)とProductionのmodel/voice/呼出方式の一致確認。(vi)既存のTrial知見(N01 Std減速後中央値≈148 WPM、破綻2/92はASR gateで捕捉)を「仕様変更なし」の注記として記載。
C. **回帰・テスト計画**: 既存test一覧(KP: `er003_key_words_*_test*.py`、`er064_kp_int_0*_test_01.py`等/TTS: `er003_v1_n3_01*_test*.py`、`er026_*_test*.py`、`er011_*_test*.py`)+新規test(M2関数のProduction module化のunit test、P0無変更sha test、N01 sha test、Family Z経路でN01/M2が読まれることのmock test)。実行コマンド全文(`.venv\Scripts\python.exe`)。
D. **runtime evidence計画**: Family X=Coffee記事でKP M2P0再生成(actual model_id、routing、候補数、予約枠の有無をログ)+Full Story Std/Adv音声化(N01 style sha、model_version、ASR Gate結果、Std減速後再検証結果、WPM/文末ポーズ実測)+試聴ページ(GitHub Pages `user_test/`+Playwright実再生evidence)。Family Z=mock/dry-run(課金なし・生成なし)でstyle/候補経路の到達を確認するにとどめ、Checklist 5/6は「未確認」。
E. **費用見積**(出典付き): Coffee KP再生成(gpt-6-luna job数×単価)、TTS(part数×Std/Adv×想定retry、単価出典)、ASR(OpenAI/Azure)、合計と上限提案。未確認単価は「未確認」。
F. **Dangling Reference / SSOT計画**: CURRENT_SPEC更新箇所(KP仕様節・TTS style節の行番号)、DECISION_LOG、OPEN-325/336/337/310/332の更新方針、USER_DECISION_REGISTER更新、Trial Status(VALIDATED)→APPROVED_FOR_PRODUCTION→PRODUCTION_WIREDの遷移記録。
G. **Opusに問う論点**(5件以内)。
H. **USER_DECISION_REQUIRED候補**一覧(あれば)。

### 2. `PATH_MAP_01.md`
M2P0・N01それぞれについて、Family X/Z × 初回/retry/fallback/regeneration/減速後再検証 の経路×配線点マトリクス(ファイル:行、現状値、変更後値、変更要否)。

### 3. `TEST_PLAN_01.md`、`EVIDENCE_PLAN_01.md`、`COST_ESTIMATE_01.md`(1と重複しない範囲で詳細)

## 実行コマンド全文

```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01_01.md --json-out docs\pm\delegation_log\2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01_01_check.json
set PYTHONUTF8=1
.venv\Scripts\python.exe -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <P0 Prompt定数を含むProductionファイルの絶対パス>
.venv\Scripts\python.exe tools\secret_scan_01.py --staged
```
(sha計算はN01文言・P0定数それぞれについて実際のパス・文字列で実行し、結果を設計書に記録。他の実行はなし。)

## SSOT追記文

編集せず、RESULT_PACKET_XZW.mdに「委任_02で使うSSOT追記文案」(DECISION_LOG: ユーザー正式決定の記録[原文要旨]、OPEN-325/336/337/310/332更新案、CURRENT_SPEC更新案[配線完了後に反映する文面])を記載。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: なし。明示add: `er071_output/m2p0_n01_production_wiring_01/*.md`、`docs/pm/delegation_log/2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01_01.md`(+`_check.json`)。コミット: 「FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_01: M2P0/N01 Production配線設計(JPY0、code無変更、Opus条件A/C待ち)」trailer `Managed-ID: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01`。push。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_XZW.md`に: (0)check結果(全文保存)、STOP確認、(1)M2P0配線点の要約(Family X/Z、共有moduleか)、(2)N01配線点の要約(P8定数の所在、Family Zのnarrator/dialogue区分)、(3)初回/retry/fallback/regeneration/減速後の整合表の要約、(4)テスト計画・evidence計画の要約、(5)費用見積(出典付き)と上限提案、(6)USER_DECISION_REQUIRED候補(「true story」文言、その他)、(7)Opus論点、(8)SSOT追記文案、(9)commit hash+raw URL。`docs/pm/ACTIVE_TASK_XZW.md`に固定ヘッダ。
