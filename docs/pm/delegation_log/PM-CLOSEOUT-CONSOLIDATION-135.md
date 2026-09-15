## 管理ID

PM-CLOSEOUT-CONSOLIDATION-135(USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03 成果物のGit記録・Web到達確認・SSOT反映・Closeout確認・最終REPORT)
並行タスク衝突確認: 並行タスクなし。本タスクがGit・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを扱う唯一のタスク。

## 性質/到達上限Status/禁止事項

- 性質: Git記録・Web到達確認・SSOT反映・REPORT作成のみ。**API呼び出し禁止、費用¥0**。Production/Trialコード変更禁止。
- 反映する事実(Fable照合済み。各RESULT_PACKETの実値を使う):
  - **Discovery**(`docs/pm/RESULT_PACKET_FU03_DISCOVERY.md`): B1 Human Review player完成(`discovery/audio/b1b/human_review_player.html`、attempt1/3は文ブロック欠落・attempt2は内容完備で語差のみ、ユーザー試聴承認待ち、¥0)。A2再生成: S2正式path・同一Ledger・Prompt無変更、attempt1=**530語**採用(No Jargon修正込み、QA PASS)、attempt2は予算ガード中断。**Word-count報告ルール該当: 530語≥500語**。旧604語版は`a2_before_regeneration_604w/`へ履歴保持、**旧604語版player/音声は最新候補として提示しない**(index.html・REPORTで「旧版・不採用」表記)。A2音声は未実施(予算超過見込みSTOP、ユーザー判断)。Part B実費¥155.06。総原価は`discovery/production_set_cost.json`の`fu03_*`値に従い、「Production 1生成セット総原価(新A2生成+QA分を加算)」と「開発・Trial/検証費(不採用604語版・中断attempt2)」を分離して表記(推定合算禁止)。
  - **Family C A2 v2**(`RESULT_PACKET_FU03_FAMILYC_A2.md`): Comment 3をユーザー指定文へ差し替え(ASR一致・表示一致)、Comment 4除去(pause→Outro)、Gate PASS、Story sha256不変、テスト18件PASS、¥0.90。**Family C B1**(`RESULT_PACKET_FU03_FAMILYC_B1.md`、`_2.md`): B1 Trial記事597語(Trial目安≈400語を24%超過=報告義務)、Story core維持、CURRENT FACT 0、Comment 1〜3(Comment 4なし)、Comment 3主語明確化済み、Mother=Erinome/Robot=Charon、Gate PASS、約6分24秒、テスト24件PASS、¥85.20+¥0.90。Status: A2 v2・B1ともVALIDATED候補(試聴待ち)。Family C累計=¥235.50(予算枠¥133.99を¥101.51超過)。**Family C全体はProduction正式path未承認**(Comment 4なしはユーザー正式Decisionとして記録するがPRODUCTION_WIRED昇格しない)。
  - **Trend**(`RESULT_PACKET_FU03_TREND_NAMING.md`、`docs/pm/b1b_naming_investigation.md`): A2/B1試聴OK・追加作業なし。B1Bは旧B1-A/B1-B比較の名残(historical naming)、内部ID `b1b`は多数ファイルに組み込みのため維持、ユーザー向け表示は「B1」へ。Trend player表示更新済み。置換箇所一覧(REPORT/CURRENT_SPEC/index.html、行番号付き)は同文書に記載→**本タスクで反映**(履歴記述・内部IDは残す。CURRENT_SPECは「ユーザー向け名称=B1、内部ID=b1b」の命名ルール1段落を追加し、既存の定義行は保持)。Alexa+時間差PASSはOPEN-153 evidenceとして保持。
  - **Voices 2V v2**: Preview以外OK。Previewは3文/約65語で長めだが**ユーザーが今回のみ個別特別承認**(再生成なし・音声再作成なし・将来の前例にしない)。OPEN-151はPARTIAL / USER TEST READY維持、PRODUCTION_WIRED禁止。
  - **OPEN-154**(`docs/pm/spec_traceability_audit_03.md`の登録行案を使用): B1 Preview長さ仕様、USER_DECISION_REQUIRED、MEDIUM。実績67語/4文→38語/2文→46語/2文(ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01、2026-09-07)、現Prompt`er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE`は「2〜3文程度」のみ(A2 PREVIEW_ROLEは80〜110字目安+150字上限あり)、Voices v2は3文/65語(個別例外)。**具体的word-count正式値は決めない**。
  - **OPEN-155**(同文書の登録行案): User Decision→Formal Spec反映漏れ、USER_DECISION_REQUIRED(Open Item管理自体は承認済み)、HIGH、PM Governance/Specification lifecycle/Production wiring traceability。限定監査結果(明確な反映漏れ: Discovery A2 length soft target未配線・未採番/対照例: Point-only regeneration除外は完結/Family CのCURRENT_SPEC不在は未確認扱い)と再発防止案5件(4件は新Gate該当→案提示のみ、STOP)。**PM_GOVERNANCEへ新Gateは追加しない**。
  - **Word-count報告ルール(ユーザー正式決定)**: A2記事が280語以下または500語以上の場合、完成報告時に必ず明示。hard gateではない、生成停止しない、報告義務のみ。→`docs/pm/PM_GOVERNANCE.md`の報告ルール節(9節「ユーザー向け報告」または15節コスト/報告の適切な位置。既存節構成をGrepで確認し、新Gateではなく報告義務として追記)+DECISION_LOG。
  - **OPEN-153**: 内容維持(標準=Gemini 2.5 Flash TTS、NG時の将来retry候補=3.1 Flash TTS[単価約2倍、retry込み総原価で評価]、run-to-run variance/時間依存仮説保持、Production routing変更なし)。
- **Closeout必須確認(ユーザー指定10項目)**: (1) Discovery A2旧604語版が最新候補として残っていないか(index.html/REPORT/ACTIVE_TASK)、(2) Family C Comment 4が新規B1に混入していないか(`home_robots_b1/segments.json`・player.htmlをGrep)、(3) Family C Comment 3修正済みか(A2 v2・B1両方)、(4) Discovery B1 Human Review playerが分かりやすいか(構成要素の存在確認: canonical/ASR/diff/seek/attempt再生)、(5) Voices Previewが「個別例外」と記録され正式前例化していないか(DECISION_LOG/OPEN-151/154の文言)、(6) Trend B1表示がB1へ整理されたか(player・REPORT・index.html・CURRENT_SPEC)、(7) OPEN-154/155登録済みか、(8) 280語以下/500語以上報告ルールが正式記録されたか、(9) ユーザー承認事項がCURRENT_SPEC/DECISION_LOG/OPEN_ITEMSのどこにも落ちていない項目がないか(本指示の全決定事項: Comment 4なし・Comment位置原則・Word-count報告ルール・Voices Preview個別例外・B1命名・OPEN-154/155・Discovery A2不採用と再生成・B1人間承認方式・OPEN-153維持 の各反映先を表にする)、(10) APPROVED_FOR_PRODUCTION未配線項目が残っていないか(`OPEN_ITEMS.md`をGrep `APPROVED_FOR_PRODUCTION`し、各行のStatusがPRODUCTION_WIRED/PARTIAL/DEFERRED等どれかを表にし、未配線があれば列挙)。結果を`docs/pm/closeout_check_FU03.md`に記録し、REPORTにも掲載。
- 禁止: `git add -A`/`.`/`stash`/`clean`/`amend`/`rebase`/`force push`、API呼び出し、Production/Trialコード変更、`.gitignore`変更、`*.wav`のadd、gitignore対象のadd、SSOT全文Read、新Gate追加、Preview word-count正式値の決定。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文・要点)

> 各作業について「開発・Trial/検証費」と「Production 1生成セット総原価」を分けて報告。追加費用は既存累計に加算。不明費用を推定で合算しない。STOP条件: 新Production仕様/既存Gate変更・緩和/retry上限変更/Promptの意味変更/Family C全体のProduction採用判断/B1 Previewの具体的word-count正式値決定/OPEN-155対策として新PM強制Gate追加/想定外の大幅コスト増。Closeout必須確認10項目(上記)。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FU03_DISCOVERY.md`、`RESULT_PACKET_FU03_FAMILYC_A2.md`、`RESULT_PACKET_FU03_FAMILYC_B1.md`、`RESULT_PACKET_FU03_FAMILYC_B1_2.md`、`RESULT_PACKET_FU03_TREND_NAMING.md`、`RESULT_PACKET_FU03_SPEC_AUDIT.md` 各全文。`docs/pm/spec_traceability_audit_03.md` 全文(登録行案・DECISION_LOG追記案)。`docs/pm/b1b_naming_investigation.md` 全文(置換箇所一覧)。
2. `OPEN_ITEMS.md`: Grep `^\| OPEN-(120|135|147|151|152|153) \|` → 該当行のみ。Grep `APPROVED_FOR_PRODUCTION` → 該当行の先頭200字(Closeout(10)用)。最終行番号(OPEN-154/155追加位置)。
3. `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-134` → 直近エントリ位置と索引行。
4. `CURRENT_SPEC.md`: Grep `B1B|B1-B` → 置換候補行(定義・履歴は保持)。Grep `Preview` → B1 Preview仕様行(OPEN-154参照行の特定のみ、変更しない)。
5. `docs/pm/PM_GOVERNANCE.md`: Grep `^## |^### ` → 節構成(Word-count報告ルールの追記位置)。
6. `USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`: Grep `^## |^### ` → 章立て(FU-03 REPORTの構成を揃える)。
7. `er014_output/four_type_observation_01/index.html`: Grep `player|<tr|href=|B1B|604` → 更新位置。
8. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- (a) 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"`(v2 18件+B1 24件)。
- (b) Git 1回目: 各RESULT_PACKETのcommit対象候補に従い明示add(discovery/ human_review_player・review mp3・a2新版・a2_before_regeneration_604w/・driver、home_robots_v2/更新分、home_robots_b1/一式[mp3・player・JSON・md]、`er013_family_c_future_writer_08_b1.py`、`er013_family_c_episode_trial_09b_b1_run.py`、`_b1_test_01.py`、`er013_family_c_episode_trial_09b_run.py`、`_09b_test_01.py`、trend/player.html・build_player_b1_label.py、docs/pm調査文書2件、delegation_log、RESULT_PACKET_FU03_*。wav除外)→commit(`USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03: Discovery A2再生成(530語)+B1 Human Review player+Family C A2 Comment修正・B1 Trial episode+Trend B1表示`+trailer)→push。
- (c) Web到達確認(push後、`docs/pm/web_playback_check_FU03.json`): 直接mp3=Family C v2(実ファイル名)、Family C B1、Discovery B1 review attempt2 mp3。player=Family C v2、Family C B1、Discovery B1 human_review_player、Trend B1(表示更新版)。GET/HEADで200・Content-Type、player内相対参照(episode+先頭3 segment、Human Review playerはattempt mp3 3件)を解決。CDN遅延時60秒待ち最大3回。
- (d) SSOT: `OPEN_ITEMS.md`(OPEN-135/147/151/152/153/120末尾追記、OPEN-154/155新規行[監査文書の案、Status USER_DECISION_REQUIRED])、`DECISION_LOG.md`(`## PM-CLOSEOUT-CONSOLIDATION-135`: Family C Comment 4なし恒久Decision+Comment位置原則+Family C未採用注記、Word-count報告ルール、Voices Preview個別例外、B1命名ルール、Discovery A2 604語版不採用→530語版採用(≥500語flag)、B1人間承認方式、OPEN-154/155登録、費用、commit。+索引1行)、`CURRENT_SPEC.md`(B1命名ルール1段落。他は変更しない)、`docs/pm/PM_GOVERNANCE.md`(Word-count報告ルールを報告義務として追記、新Gateではない旨明記)、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`(Discovery A2 regen/Family C B1 の行)。
- (e) 最終REPORT `USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03_REPORT.md`(新規root): 対象別(修正内容/修正前後/runtime evidence/Audio Validation/player URL/direct audio URL/duration/追加費用[開発・Trial費とProduction総原価を分離]/unresolved/final status)、OPEN-154/155要約、Closeout 10項目表、費用表(15-8)、**「今ユーザーが試聴すべきURL」再掲**(Family C A2 v2/Family C B1/Discovery B1 Human Review/Trend A2/Trend B1/Voices v2。Discovery A2は音声未完成のため「記事のみ・音声はユーザー判断待ち」と明記し旧604語playerは載せない)。
- (f) `index.html`更新(B1B→B1表示、Discovery A2旧版を「旧版・不採用」、Family C B1行追加、Human Review playerリンク、費用表更新)。
- (g) ACTIVE_TASK固定ヘッダ更新(管理ID=CONS-135、UDR: Discovery A2音声化可否/Discovery B1人間承認/OPEN-154/OPEN-155/Family C試聴、APPROVED未配線: Closeout(10)の結果)。
- (h) Git 2回目(`PM-CLOSEOUT-CONSOLIDATION-135: FU-03 SSOT反映+OPEN-154/155登録+Word-count報告ルール+B1命名+最終REPORT+Web到達確認`+trailer)→push。`git log --oneline -3`、`git status --porcelain | Measure-Object -Line`。
- trailer(両commit末尾、空行の後): `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` / `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-135.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-135_check.json`
2. (a)→(b)→(c)→(d)(e)(f)(g)→(h) の順。

## SSOT追記文

上記(d)に従い実値で記載。PARTIAL/VALIDATED候補を格上げしない。未完成をREADYと書かない。Preview word-count正式値を書かない。

## Git(明示add対象・コミットメッセージ・trailer)

上記(b)(h)のとおり。無関係な既存差分(er006_output/er011_output等)、`er014_output/.../voices/writer_generic_before*.py`はaddしない。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`(上書き)に: 1) commit hash 2件(full)・push結果、2) Web到達確認表、3) 最終REPORTパス、4) SSOT追記位置(OPEN-154/155の行番号含む)、5) 回帰結果、6) Closeout 10項目結果(各✓/✗+根拠)、7) 費用表(15-8、開発・Trial費/Production総原価分離)、8) 試聴URL一覧、9) T-0結果・事前指定外Read、10) push後残差分要約、11) ACTIVE_TASK更新済み。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(単独)
