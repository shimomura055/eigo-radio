# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_04(ユーザー正式判断2026-10-21: Std comment_2 Human Review承認(PASS)→承認記録→HR Lock正規解除→Std差分resume→assemble→player→正式試聴ページ公開→SSOT/Git)。並行agentなし。

## 性質/到達上限Status/禁止事項
- 性質: 承認済みProduction経路の続行。到達Status: `AUDIO_COMPLETED_PAGES_PUBLISHED → USER_LISTENING_PENDING`(ユーザー試聴PASSは別Status)。
- 費用/日次: 本日2026-10-21(JST)既使用=未取得(S0で`daily_dev_cost_01.py --date 2026-10-21`を実行して記録)/見積JPY0〜数円(resumeはcomment_2がlock経由0 API・他segmentはreuse。assemble/playerはAPIなし想定)/承認区分C。T-3: 上限¥20(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。**特にresumeが「全segment再生成」や「comment_2の新規TTS」を起こす見込みと判明したらAPI実行前にSTOP**(ユーザー§2-2「不要なTTS再生成を行わない」、7-5(4))。
- 禁止: コード・Prompt・閾値・Variant Layer・ASR許容条件の変更/記事本文・Std補助文の再生成/`--regenerate-stage`/`approve_regenerate`/review_lock_stateの直接編集(正規関数経由のみ)/新規Open Item/Batch TTS/`git add -A`/`-u`/stash/amend/rebase/force push/branch操作。
- Opus独立技術レビューGate: 非該当。11-8: 範囲外=受理面・閾値・方式の新設/拡大、範囲内=承認済み仕様との矛盾の是正(本委任で必要になった場合は是正前にRESULT_PACKETに理由を記し、Production挙動の意味的変更を伴うならSTOP)。
- 時間見込み: 40分(S0 5/承認記録+resume 5/assemble 5/player+ページ+Playwright 15/SSOT+git 10)。並列化: assemble実行中に`er019_mey_page_02.py`の最終調整とE2E_PLAN_02 §10下書きを並行。TTS/assembleはrun state競合のため直列。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_委任_04.md`へ逐語保存(打ち直し禁止。`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <上記path>`、N=本委任文[「E2E-02 委任_04」を含む最新、直前188は委任_03])し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <上記path> --json-out <上記path>_check.json`を実行、結果をRESULT_PACKETへ1行。
T-2: TTSを伴う(resume)ため全runnerコマンドに`TTS_EXECUTION_MODE=STANDARD`を明示。実行前に(1)差分再生成が可能か(comment_2=lock経由0 API、他segment=reuse)をコードとrun stateで確認、(2)既存音声再利用の有無を確認、(3)`--budget-jpy 70`を明示、(4)想定外の全再生成が判明したらAPI実行前にSTOP。

## ユーザー指示(原文・2026-10-21)
以下を `docs/pm/delegation_log/2026-10-21_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_HR-APPROVAL_USER.md` へ逐語保存(先頭に `# ユーザー指示原文(2026-10-21)` と `管理ID: FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_04 / REGISTER #128` の2行を付け、原文は一字一句変えない。文字数・sha256をRESULT_PACKETへ)。
--- 原文ここから ---
# 中東記事 E2E-02 — Human Review承認・音声完成指示

## 1. ユーザー正式判断

**Standard Comment 2のHuman Reviewを承認（PASS）する。**

ユーザーが実際に試聴し、「タイフーン機」と正しく発音されていることを確認済み。

- ASRの「台風機／台風期」は今回の特殊な認識誤りとして扱う。
- 発音判定仕様・Variant Layer・ASR許容条件は変更しない。
- 追加Trial・再発防止策・新規Open Itemは不要。
- 同種問題が頻発した場合のみ、ユーザーが対策の要否を判断する。

## 2. 実施作業

1. ユーザーの明示承認を記録し、Comment 2のHR Lockを既存の正式手順で解除する。
2. 承認済みの既存takeを採用する。不要なTTS再生成は行わない。
3. Standardの差分resumeを実行する。
4. 音声組立・Audio QA・必須Validator／Regressionを完了する。
5. Standard／Advanced両レベルの完成音声、全スクリプト、Key Phrasesを確認できる正式試聴ページを公開する。
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／必要なGit反映を整合させる。

**既存の承認済みProduction経路を使用し、新たな仕様変更や記事本文の再生成は行わないこと。**

## 3. 受入条件

- Comment 2の承認が正式記録されている。
- Standard／Advancedの音声が完成している。
- 既存の必須品質GateがPASSしている。
- retry／fallback／resumeの整合が確認できる。
- 正式Production runtime evidenceが残っている。
- Fableが実行結果を照合し、完了可否を独立判定している。

既存仕様・承認範囲内の不具合は自律的に修正・検証する。

重大な品質問題、予算超過、未承認仕様変更が必要な場合のみSTOPする。

## 4. QCD

品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用。

- 不要なTTS再生成・LLM呼出・検索を行わない。
- 既存成果物を再利用して差分処理する。
- 独立作業は並列化し、不要な待機を避ける。
- 承認済み予算枠と日次1,000円（JST）を遵守する。

## 5. 完了報告

以下を簡潔に報告する。

1. **中東記事完成の可否と正式試聴URL**
2. Standard／AdvancedのAudio QA結果
3. HR Lock解除・差分resume・正式runtime evidence
4. 実費、所要時間、追加再生成の有無
5. SSOT／Git反映状況とFable最終受入判定
6. 残るユーザー判断（ある場合のみ）

**今回の目的は、ユーザー承認済みの音声を使い、最短・最小費用で中東記事を完成させること。追加の改善Trialや仕様変更は行わない。**
--- 原文ここまで ---

## KPI provenance欄
Audio QA/Gate値=production_formal_path(fresh、run_mey_02の既存run stateをresume)。comment_2=human_approved(ユーザー試聴承認、REGISTER #128)。E2E自己確認: Yes(fresh Production初回pathを含む)。

## 作業
### S0(JPY0)
- `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-21` 記録。`git status --porcelain | Measure-Object -Line`記録。`.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 --run-dir er019_output\middle_east_yemen_saudi\run_mey_02 --out er019_output\middle_east_yemen_saudi\run_mey_02\audit\stop_scope_hr_resume.json`(rc=3なら中止)。
- 現在のcanonical `comment_2.wav`(attempt3 minimal_fallback、sha 8a05886b…)がassemble対象であることを再確認(E2E_PLAN_02 §9-5)。ユーザーが試聴したページの3テイクのうち、採用されるのはこのcanonical takeである旨を記録(他takeへの差替え経路は使わない=「承認済みの既存take」=canonical)。
### S1 承認記録(正規手順のみ)
- `er019_family_x_audio_production_runner_01.py`/`er019_family_x_style_profile_01.py`/`er011_human_review_lock_01.py`で、Family X Std segmentの人間承認を記録する正規関数(委任_02報告: `record_human_approval(a2 out_dir, "comment_2", 台本comment_2, approved_by="user")`、実装`er003_v1_n3_01_assemble.py:96`相当)を再確認し、**その関数経由で**承認を記録(approved_by="user", note="REGISTER #128 ユーザー試聴承認 2026-10-21、原文=<USERファイル名>")。review_lock_state等のjsonを手編集しない。記録先ファイル(path:キー)と、lock状態の遷移(`HUMAN_REVIEW_REQUIRED`→承認後の値)をRESULT_PACKETへ。
### S2 Std差分resume
- 事前確認(T-2 4点)の結果を記録してから `$env:TTS_EXECUTION_MODE="STANDARD"; $env:PYTHONIOENCODING="utf-8"; .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug middle_east_yemen_saudi --run run_mey_02 --level a2 --stage tts --budget-jpy 70`(console→`.../middle_east_yemen_saudi__run_mey_02/console_tts_a2_resume_04.txt`)。API呼出数・費用(raw_usage_log差分)・各segmentのstatus(reuse/lock/human_approved)を記録。comment_2に新規TTSが走った場合はその事実と理由を必ず報告(承認済みtakeが置換されていないかsha比較)。
- 承認だけでassembleへ進める実装なら、tts resumeを省略してよい(理由を記録)。
### S3 assemble/player
- 同環境で `--stage assemble --level both` → `--stage player`。Audio Validation Gate/M3 style gate/key_phrase_source_gateの結果、Std assembled秒数・peak、Std Full Story 6%減速実測、PASS_WITH_WARNING一覧(事後試聴リスト)を記録。BLOCK/HRが再発したら迂回せずSTOP報告。
### S4 正式試聴ページ
- `er019_mey_page_02.py`で `user_test/middle_east_yemen_saudi_e2e_02/index.html` 生成(完成音声Std/Adv[mp3変換は委任_02と同方式]・全スクリプト[Std: Preview/Full Story/Comment1〜4/KP、Adv: 同]・Key Phrases[英語+Std日本語意味/Adv英語解説])。HR用ページ(`hr_comment_2/`)はそのまま残し、indexからリンク。commit/push後 `https://shimomura055.github.io/eigo-radio/user_test/middle_east_yemen_saudi_e2e_02/index.html` HTTP200+`er019_mey_play_verify_02.py`で全再生・seek・console error 0・秒数一致、evidence=`docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/pages_play_evidence_04.json`。
### S5 記録・SSOT
- `E2E_PLAN_02.md` §10(承認記録・resume・assemble・ページ・費用[15節5区分: 本記事総コスト=E2E-02新規支出合計/Standard同期/Batch換算/異常retry由来=comment_2再試行分/Trial特有=なし。案件累計=E2E-01 text 79.881+E2E-02]・所要時間・runtime evidence一覧)。
- `OPEN_ITEMS.md` OPEN-416行: Status角括弧を `[AUDIO_COMPLETED_PAGES_PUBLISHED・USER_LISTENING_PENDING(E2E-02 run_mey_02、comment_2=ユーザーHR承認2026-10-21 #128)]` へ置換し、行末に完成URL・費用・承認記録path・E2E_PLAN_02 §10参照を追記。
- `docs/pm/USER_DECISION_REGISTER_01.md` #128: 「判断済み 2026-10-21((ア)承認。ASR誤りは今回限りの扱い、仕様不変・新規Open Item不要)」へ更新。
- `DECISION_LOG.md` 末尾箇条書き1件(HR承認・完成・Production変更0・原文ファイル名+sha)。`docs/pm/REPORT_LEDGER.md` 1行。CURRENT_SPEC.mdは仕様不変のため編集なし(記事登録節が存在する場合のみ報告)。
- `docs/pm/ACTIVE_TASK.md` 先頭ヘッダ更新(Status=AUDIO_COMPLETED_PAGES_PUBLISHED_PENDING_FABLE)。

## 事前指定Read/Grep一覧
- `docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/E2E_PLAN_02.md` §9(Grep `^## ` で位置特定→§9のみ)。
- `docs/pm/RESULT_PACKET_MEY3.md` 5節(手順書)。
- `er003_v1_n3_01_assemble.py` L90-130(record_human_approval)。`er011_human_review_lock_01.py` Grep `def record_human_approval|human_approved|def .*approve` → 該当関数±30行、L320-345、L655-715。`er019_family_x_style_profile_01.py` L680-700。`er019_family_x_audio_production_runner_01.py` Grep `human_approved|review_lock|reuse` → 該当箇所±10。
- `er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02/a2/audit/` Glob `*review_lock*`・`*comment_2*`。
- `er019_mey_page_02.py`、`er019_mey_play_verify_02.py`(前委任で作成、全文可)。
- `OPEN_ITEMS.md` Grep `^OPEN-416 \|`。`docs/pm/USER_DECISION_REGISTER_01.md` Grep `^- #128\(`。`DECISION_LOG.md` Grep `^- 2026-10-2` 末尾3行。`docs/pm/REPORT_LEDGER.md` 末尾10行。`docs/pm/ACTIVE_TASK.md` 先頭10行。

## 実行コマンド全文
上記S0〜S4のとおり(python=`.venv\Scripts\python.exe`、runner引数は実行前に`--help`で実在確認)。secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`(hits=0必須)。

## Git
明示add: T-0 2ファイル+USER原文+E2E_PLAN_02.md+evidence json+`user_test/middle_east_yemen_saudi_e2e_02/`(index.html・mp3)+`er019_mey_page_02.py`(変更時)+run_mey_02配下のjson/md/txt(wav/大容量・他runの既存差分ファイル[manifest.json/reuse_telemetry.jsonl/human_review_queue.jsonl等]はstageしない)+SSOT4ファイル。commit最低2回((1)承認記録+resume+assemble+ページ、(2)SSOT)。メッセージに事実を含める(例 `FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_04: comment_2 HR承認記録(#128)→Std resume(API n回/JPY x)→assemble→正式試聴ページ公開`)。**push先は`git push origin HEAD:main`**(force禁止、現origin/main=86d9f2476からfast-forward)。raw URL列挙。

## 報告(docs/pm/RESULT_PACKET_MEY5.md 上書き。ユーザー§5の1〜6の順)
1. 完成可否・正式試聴URL(HTTP200・Playwright結果)。2. Std/Adv Audio QA結果(PASS/PASS_WITH_WARNING/NG件数、style gate、KP source gate、6%減速、assembled秒数)。3. HR承認記録(path:キー、lock遷移)・差分resume(API呼出数、reuse/lock/human_approved内訳、comment_2のsha不変確認)・runtime evidence(model/backend/profile sha)。4. 実費(工程別・出典・本日累計・案件累計・Batch換算・70円目標差)・所要時間・追加再生成の有無。5. SSOT編集行の新旧・commit hash・raw URL・T-0結果。6. 判断候補(PASS_WITH_WARNING事後試聴リスト等。USER_DECISION_REQUIREDラベルは付けない)。加えて26節(再起動)該当の有無・判定整合行。