## 管理ID

KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02(Opus条件Aレビュー反映の設計確定A'・Trial専用モードでの実装・オフライン検証T3・有料Trial T1(+P7)/T2・Regression・SSOT反映・Opusレビュー全文保存。2026-10-15)。
並行タスク: KP-GLOSS-OPUS-REVIEW-ROOT-CAUSE-AUDIT-01 委任_01(read-only調査、`er071_output/m2p0_n01_production_wiring_01/opus_review_root_cause_audit_01/`と`docs/pm/*_KGORA.md`のみ書く)が実行中。あなたはそこへ触れない。git commit時に`.git/index.lock`があれば30秒待って再試行(最大5回)。SSOT編集権は本委任のみが持つ(KGORAは持たない)。

## 性質/到達上限Status/禁止事項

性質: Trial(DEV/Trial専用モードでの実装・検証)。到達上限Status: `VALIDATED`(Trial)/`REJECTED`/`USER_DECISION_REQUIRED`のいずれか。**`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`は宣言しない。** 新仕様の正式Production採用・Production既定挙動の変更は不可。
Opus独立技術レビューGate判定: 条件A実施済み(2026-10-15、本委任文末尾に全文)。本委任はそのレビュー反映と実装・Trial。実装後に設計が大きく変わる場合はSTOPしてFableへ(再レビュー要否はFable判断)。
時間見込み: 全体150〜210分(設計確定・撤去一覧20分/実装60分/unit+T3 mock 40分/有料T1・T2 20分/Regression 20分/SSOT・証跡・commit 20分)。並列化: KGORAと並列。本委任内は実装→検証→Trialの順序依存で直列。Regression suiteは複数process並列実行可。
費用: T-3定型に従う。上限JPY10(Guardrail。T1約1.14+P7約0.3+T2約1.5=約3円見込み、出典cost_01.json実測単価。T2単価は想定値のため実測で更新)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。日次上限JPY1,000は本日の他支出(本日ここまでJPY0)と合算して守る。
禁止: 承認済みPrompt(選定/canonicalization)・Rule7・Audio Validation Gate(`er003_v1_n3_01_assemble.py`)・Human Review Lock(`er011_human_review_lock_01.py`)・`human_review_queue.jsonl`・承認済みgloss規則本文の変更、**Production既定挙動の変更**(後述のモード既定=legacy厳守)、量産run(Coffee/Melos等の正式runner実行)、Coffee完成物run dirの再生成、`git add -A`/`-f`/amend/rebase/force push/stash/clean/reset --hard/checkout -f、STOPセンチネル編集、.env使用、KGORA領域への書込、SSOTの事実に反する更新(Production採用済みのような記述)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01_委任_02.md`へ**全文**保存し(要点保存でFAILになった前回の反省。末尾のOpusレビュー全文も含めて保存)、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01_委任_02.md --json-out docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01_委任_02_check.json`を実行し結果をRESULT_PACKETへ1行記録。
T-2: 本委任はTTSを**実行しない**(T3のTTS停止検証はmock。実TTS呼出禁止)。`TTS_EXECUTION_MODE=STANDARD`はmock経路でも明示。
T-3: 上記費用欄のとおり(上限JPY10 Guardrail)。

## ユーザー指示(原文)

(2026-10-15 KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01、逐語要旨。委任_01A委任文にも同内容)
A. 「〜」一律禁止を撤回。承認済みgloss規則維持。`based on`→「〜をもとにした」許容/`based on interviews`→「〜をもとにした」NG/「インタビューをもとにした」整合。「〜」の有無を合否条件にしない。最終KPの具体的な目的語・補語・修飾語を日本語が反映しているかで判断。既存の正当な辞書表現を不当に拒否する新ルールを作らない。
B. 工程順: 選定・初期gloss→英語KP最終確定→再整合→必要な品質判定→TTS。不整合が残ったitemを正常なTTS入力・正常完成として扱わない。
C. 2回失敗時: Human Reviewへ例外報告(英語KP・現在gloss・失敗理由・試行結果・再生成候補)、対象の後続TTS・正常完成を停止、最終KPを安易に短い候補へ戻さない。Human Reviewは例外の最終対応。
D. 十分な追加Trial。パターン拡充、通常運用でHuman Reviewが頻発しないことを確認。
§4: 機械的に確認できる事項と言語的判断を区別、誤NG・誤PASS双方検証、既存の自然なglossが不必要に変更されない保証、新品質条件を独断でProductionに追加しない。FAILED→HR通知→対象工程停止が確実に成立。通知ファイル生成だけで届いたとみなさない。正常完成扱いされない/後続TTSへ進まない/既存STOP・安全機構と矛盾しない/独立工程を不必要に止めない。
§5: オフライン→有料Trial。独立パターンはまとめて検証。件数は情報価値で。既存承認済み予算・日次1,000円。
§8: 許可=DEV/Trial専用経路での試作・検証、既存記録Regression、承認済み予算内Trial。不許可=未承認仕様のProduction正式採用、既定flag・正式Prompt・Gateの無承認変更、安全機構の緩和、未承認仕様を含む新量産run、HR方針の独断変更、無関係な追加Trial。STOP条件=新Production仕様の正式採用が必要/承認済み品質ライン・Gate変更が必要/予算抵触/改善見込み喪失/HR例外対応が技術的に成立しない/重大な副作用・安全上の問題。Trial結果はREJECTED/VALIDATED/USER_DECISION_REQUIRED。
§9 報告11項目(後述RESULT_PACKETに対応)。

## Fableの設計確定(Opus所見OF-KGDC-01〜12への採否。これに従う)

- **構造=案A'(Opus推奨)を採用**: Human Review Lock・`human_review_queue.jsonl`は**使わない**。停止は(1)Family X `er019`の`_generate_or_reuse_kp`相当の関所で`_only_segments_skip`前例と同型の非OK status `STOPPED_GLOSS_ALIGNMENT_FAILED`(reason付き)を返し0 API call、B1の解説LLM入力組み立て箇所でもFAILED itemを除外し解説segmentを同statusに(OF-KGDC-01/02 採用)。(2)Family Z `stage_kp`で既存`FamilyZE2EStop`送出。(3)runnerはKP段の後に**最終artifact**に対して`collect_unresolved`を1回実行し、HR報告書(`GLOSS_ALIGNMENT_HUMAN_REVIEW_01.json`+.md、必須項目: article/level/rank・英語KP・現在gloss・失敗理由・試行結果全attempt・再生成候補[提案gloss/欠落語一覧/参考:候補表現+旧gloss「KPを短くすると意味が失われる、人間判断でのみ採用」/KP再生成])・run summary `gloss_alignment_human_review_events`・最終stdout専用1行を出す(OF-KGDC-04 採用: canonicalization内ではなく`run_key_phrases`戻りに対して1回)。
- **「届いた」の定義=4条件**(OF-KGDC-05 採用): ①HR報告書をその場で再読しスキーマ検証(必須項目非空)②run summaryにevent③最終stdout専用行+runの終了statusが非OK(STOP/BLOCKED)④下流停止のmock実証。いずれかの書込失敗はfail-closed(例外で当該stage停止、「通知失敗だが継続」禁止)。queueへは載せない。
- **停止粒度**(OF-KGDC (h) 採用): Family Xは当該levelのKP segment全体(5 rank分の日本語+B1解説)を保留、本文・support・他levelは継続。Family Zはstage単位停止(既存前例)。
- **HR解消手段**(OF-KGDC-03 採用): `resolve_gloss(kp_json_path, rank, gloss, resolved_by)`小関数1つ(`japanese_gloss`/`japanese_gloss_tts`を書き`gloss_alignment_status="HUMAN_RESOLVED"`+記録者・時刻、既存記号チェック`detect_prohibited_symbols`等を再利用して違反なら拒否)+手順書1ページ。Zは`ensure_stage`再開経路を実証(T3)し、解説(kp_expl_b1b)のsigにglossを含める(SHOULD→採用、ただし既存Melos完成物のsig互換を壊す場合は`regenerate_stage`手順の明記で代替し理由を記録)。
- **機械検査の最小形**(OF-KGDC-06 採用): `added_word_mappings`は多対一・重複可・`english_word`に句可/機能語(前置詞・不変化詞・助動詞・代名詞の一般化・冠詞)は必須対象外/NFKC正規化+空白除去後の部分文字列一致/判定=「必須内容語すべてが記号以外のspanのいずれかで覆われる」。**Trial中はgate判定と記録のみ(record-only)の両方を集計**し、gate化は後日ユーザー判断(Production品質条件追加はユーザー承認事項)。**本委任のTrial経路での既定はrecord-only+LLM判定を合否とし、gate判定結果は並記**(誤NG・誤PASSの採否材料)。
- **課題指示文**(OF-KGDC (b) 採用): DESIGN_DRAFT_01 3.3の文面に、「複数の英語語が一つの日本語表現でまとめて表されている場合は、同じ部分を複数の語に対応させてかまいません」を指示3へ追加。承認規則本文は無変更・実行時抽出(sha256 447e07cb…維持)。
- **item単位retry**(OF-KGDC-09 採用): 2回目は未解決itemのみで再構築、各itemは最初の有効出力を採用。
- **真なら不変の比較**(OF-KGDC-10 採用): 正規化範囲は空白と～/〜のみ、採用値は常にcurrent原文。
- **Trial修正**(OF-KGDC-07/08 採用): `put solo travel at`(承認規則15行「～％」型)はP3から外し期待NG側へ。census 28/29の推定ラベルを再点検。P7「追加語あり×自然な慣用的訳が正解」(5〜6件×2rep)を追加。item単位で「1回目INVALID率」「2回とも失敗した率」を報告。VALIDATED条件に「機械検査(record-only)の誤NG 0(慣用句パターン)」「直訳化の目視評価」を追加。量産判断は決定論部分(O1/O3/T3)+誤NG・HR率の点推定と95%上限の併記。
- **撤去一覧**(OF-KGDC (g) 採用): `SLOT_TOKENS`/`kp_has_slot_word`/`gloss_has_unjustified_slot`/fallback(i)/`revert_to_candidate_allowed`/`GLOSS_ALIGNMENT_FALLBACK_MODE`と定数群/`apply_alignment`の`fallback_mode`引数とdocstring/冒頭コメント20-22・46行/`build_gloss_alignment_fallback_record`のnote/`write_failed_notice`の出力先/不整合出力をassertするtest(`test_failed_alignment_keeps_kp_flags_failed_not_human_review`等)と「～」禁止固定test。**ただし撤去はcorrectedモード側で行い、legacyモードの挙動は本委任では変更しない**(下記モード設計)。証跡スクリプト(`er071_gloss_alignment_01_replay.py`/`_census.py`/`er071_gloss_alignment_correction_01_offline_audit.py`)は改修せず、import破綻しないことをテストで確認(破綻するなら最小shimで旧版固定、注記)。
- **OF-KGDC-11(Family X `NG_REVIEW_REQUIRED`素通り)**: 本委任では実装しない(ユーザー「無関係な追加Trial禁止」)。OPEN_ITEMSへ新規OPEN起票のみ(同じ関所で塞げる旨を記載)。
- **OF-KGDC-12 / flag運用(Fable決定、承認境界内)**: Production既定値は変更しない。代わりに**モード切替**を導入: `GLOSS_ALIGNMENT_MODE`(既定`legacy`=現行挙動そのまま/`corrected`=本委任の新設計)。envではなく`align_glosses(..., mode=...)`/`run_key_phrases(..., gloss_alignment_mode=...)`の明示引数で渡し、Trial runnerは`mode="corrected"`を明示、Production runnerは引数を渡さず既定legacy。これにより承認前の新設計がProduction経路で動かないことをコードで担保し、既定ON/OFFはユーザー判断(別UDR)に残す。legacyが既定である限り既存Regressionは無変更でPASSするはず(PASSしなければ設計誤り、STOP)。
- 案B(外側retry先行)は採らない(ユーザー方針C)。案Eは採らない。

## KPI provenance欄

T1/T2/P7の合否・率: fresh(本委任の実API)。O1(対象外item差分0・呼出0)・O3・T3: synthetic/mock(決定論)。census由来の率: reuse(census_01.json)。E2E自己確認: No(fresh Production初回pathは含まない。Trial専用modeでの実行)。混在時は件数内訳をVALIDATION_02.mdに書く。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`へOF-KGDC-01〜12を新規行として追加(列はヘッダ10列に合わせる。前回OF-225〜235は7列でヘッダ不一致と判明しているので、同形式に揃えつつOF-225〜235の行も10列へ補完)。状態: OF-KGDC-01〜10,12=FABLE_DECIDED→本委任でIMPLEMENTED/TRIALED、OF-KGDC-11=FABLE_DECIDED(別OPEN)。既存OF-227=「(i)廃止・(ii)はHR+停止へ(correctedモード)」/OF-228=「一部撤回: Human Review送りなし・下流継続を撤回」/OF-230=「置換: 『～』記号条件撤回、追加内容語→span対応(record-only、gate化は要承認)」/OF-226=「課題指示文から矛盾文削除で解消(承認は要)」と**提案者/採用者/独自具体化**の区別を備考に記す。

## 事前指定Read一覧

- `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/DESIGN_DRAFT_01.md`: 全文(161行)
- 同 `TRIAL_PLAN_01.md`: 全文
- 同 `INVESTIGATION_01.md`: 5〜8節
- 同 `OFFLINE_AUDIT_01.md`: 全文
- `er003_key_words_gloss_alignment.py`: 全文(構造変更のため1回許可)
- `er003_test_key_words_gloss_alignment.py`: 全文(改訂対象)
- `er003_v1_n3_01_scaffold_generate.py`: 700〜830行(`run_key_phrase_canonicalization`/外側retryループ/`run_key_phrases`戻り)
- `er019_family_x_audio_production_runner_01.py`: 400〜420、560〜610(`_only_segments_skip`前例)、890〜1000(B1解説入力・display_gloss)、1220〜1280(A2 meaning wav)、1880〜1900(page)
- `er026_family_z_fiction_production_runner_01.py`: 1140〜1210(`stage_kp`/`FamilyZE2EStop`/install_kp_assets/kp_expl_b1b sig)
- `er003_v1_n3_01_assemble.py`: 95〜134、466〜515(Gateの非許可status扱い、`tts_generation_results.json`欠落時のreturn)
- `er062_*`(w62)の`ensure_stage`/`run_kp_stage`: Grep「def ensure_stage|def run_kp_stage」→該当関数全体(Opus未確認領域。再開挙動を確定)
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`: 15・17・19・21・23行
- `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/cost_01.json`: 全文(単価出典)
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: 1〜20行、252〜262行
- `OPEN_ITEMS.md`: Grep「OPEN-356|OPEN-357|OPEN-358」ヒット行、および末尾の最新OPEN番号(新規起票番号の決定)
- `DECISION_LOG.md`: 先頭40行(追記書式)
- `docs/pm/REPORT_LEDGER.md`: 末尾5行

## 事前指定Grep一覧+追記位置・更新位置の手順

1. gloss消費元の全数(Opus未確認事項1): `rg -n "japanese_gloss_tts|japanese_gloss\b|ja_gloss" --glob "*.py" -l` → Family X/Z/その他(Legacy A/B/Cは対象外・一覧のみ)のTTS・LLM・表示の呼出元一覧をVALIDATION_02.md §0に表で記載。関所を経由しない呼出元があれば明記(Production Family X/Zの経路に素通りがあればSTOP)。
2. page/player生成がGate後にしか実行されないか(未確認事項3): `rg -n "def .*page|build_player|write_player|_check_structural_completeness" er019_family_x_audio_production_runner_01.py er026_family_z_fiction_production_runner_01.py` → 呼出順序を確認し記載。
3. `tts_generation_results.json`欠落でassembleへ進む経路(未確認事項4): `rg -n "tts_generation_results" --glob "*.py"` → 生成/参照箇所、欠落時挙動。T3(h)で検証。
4. 撤去対象の参照: `rg -n "SLOT_TOKENS|kp_has_slot_word|gloss_has_unjustified_slot|revert_to_candidate_allowed|GLOSS_ALIGNMENT_FALLBACK_MODE|write_failed_notice|build_gloss_alignment_fallback_record" --glob "*.py"` → 一覧をFIX_02.md §撤去に記載(legacyモードで残す/correctedで不使用の区別)。
5. 既存test群の位置: `rg -ln "gloss_alignment" --glob "*_test_*.py" --glob "*test*.py"`。
更新位置: 新規成果物は `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/` 配下(`FIX_02.md`/`VALIDATION_02.md`/`TRIAL_PLAN_02.md`/`OPUS_REVIEW_01_VERBATIM.md`/`HR_RESOLVE_PROCEDURE_01.md`/`trial_t1/`/`trial_t2/`/`trial_t3/`/`regression/`)。SSOT追記位置: OPEN_ITEMS.md=OPEN-356行のStatus要約更新+新規OPEN(末尾採番)、DECISION_LOG.md=先頭の最新エントリ位置、OPUS_FINDINGS_LEDGER.md=OF-235行の直後、REPORT_LEDGER.md=末尾。

## 実行コマンド全文

- Opusレビュー全文保存: 本委任文末尾「## Opus条件Aレビュー全文(2026-10-15)」以下を一字一句そのまま `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/OPUS_REVIEW_01_VERBATIM.md` へ保存(先頭に「保存者: sonnet-worker 委任_02、出典: Fable経由のopus-consultant報告、改変なし」を付す)。
- unit test: `.venv\Scripts\python.exe -m pytest er003_test_key_words_gloss_alignment.py -q`
- T3 mock統合(新規 `er071_gloss_alignment_correction_01_t3_mock.py`): `.venv\Scripts\python.exe er071_gloss_alignment_correction_01_t3_mock.py --out er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/trial_t3/ --tts-execution-mode STANDARD --mock-all` — パターン: TRIAL_PLAN_01 T3(a)〜(m)+Opus追加(外側redundancy retry後にHR孤児が残らない/`tts_generation_results.json`欠落時のGate挙動/HR解消→再開で選定を再実行しない[X・Z]/B1解説が生成されない/page・playerにFAILED glossが出ない/attempt_history・queueを汚染しない/legacyモードの挙動が現行と同一)。各パターンでAPI呼出0をassert。
- O1(対象外item差分0・呼出0、決定論): `.venv\Scripts\python.exe er071_gloss_alignment_correction_01_offline_audit.py --mode corrected --census er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/census_01.json --out er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/OFFLINE_AUDIT_02.json`(既存スクリプトは改修せず、新オプションが必要なら別スクリプト `er071_gloss_alignment_correction_01_offline_audit_02.py` を作る)
- T1/P7/T2 有料Trial(gpt-6-luna、現行と同一モデル・effort。開発評価用最新モデル原則に従い最新か否かをVALIDATION_02に記載): `.venv\Scripts\python.exe er071_gloss_alignment_correction_01_trial.py --mode corrected --plan er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/TRIAL_PLAN_02.md --patterns P1,P2,P3,P4,P5,P6,P7 --reps 2 --budget-jpy 10 --out er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/trial_t1/` と `--patterns T2 --out .../trial_t2/`。実行前にSTOPセンチネル確認 `.venv\Scripts\python.exe tools/stop_scope_check_01.py`。usage/cost_jpyを全呼出で記録。
- Regression(並列可): `.venv\Scripts\python.exe run_project_regression.py --pattern "er003*_test_*.py"` / `--pattern "er019*_test_*.py"` / `--pattern "er030*_test_*.py"` / `--pattern "er063*_test_*.py"` / `--pattern "er011*_test_*.py"` / `--pattern "er008_audio_validation_gate*_test*.py"` / `--pattern "er026*_test_*.py"`。legacy既定で既存件数(366/421/108/59等)が全PASSであること。新規failure 0。
- PATH上の素のpythonは使わない。

## SSOT追記文

- OPEN_ITEMS.md OPEN-356 Status要約更新案: 「2026-10-15 ユーザー判定: 現行案(a337d8acc)は欠陥①『～』機械FAIL・欠陥②FAILED素通りで採用保留。KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01でA'設計(関所status+stage停止+HR報告書、Lock/queue不使用、『～』条件撤回、追加語span対応はrecord-only)をTrial専用mode=correctedで実装・検証中/済(結果: <VALIDATED/REJECTED/UDR>)。Production既定=legacy(現行挙動)のまま。既定ON/OFFはUDR。PRODUCTION_WIRED未。」
- 新規OPEN(採番): 「Family X runnerで`NG_REVIEW_REQUIRED`を参照せず素通りする疑い(INVESTIGATION_01 7節a、Opus OF-KGDC-11)。KP関所と同位置で塞げる。実走未確認。別承認。」
- DECISION_LOG追記案: 「2026-10-15 ユーザー決定(KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01): gloss再整合の方針A(『～』一律禁止撤回・意味反映で判定)/B(TTS前に整合保証、不整合itemを正常完成扱いしない)/C(2回失敗→Human Review例外報告+対象停止、KPを短縮候補へ戻さない)/D(十分な追加Trial)。現行案(KP-GLOSS-ALIGNMENT-PRODUCTION-01)はProduction採用保留。Fable決定: Opus条件Aレビュー(OF-KGDC-01〜12)を踏まえA'構造を採用、Trial専用mode=correctedで実装、Production既定legacy。Production採用はTrial結果確認後のユーザー判断。」
- REPORT_LEDGER追記: 本委任行(費用実績・Status・証跡パス)。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: **あり**(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/`docs/pm/REPORT_LEDGER.md`。`CURRENT_SPEC.md`は事実記載のみ可=「Trial中・Production既定legacy」、`PM_GOVERNANCE.md`は不可)。
commitは2段階: (1)実装+test+T3+Opus全文保存、(2)有料Trial結果+SSOT。明示add対象: 変更した`.py`(`er003_key_words_gloss_alignment.py`/`er003_test_key_words_gloss_alignment.py`/`er003_v1_n3_01_scaffold_generate.py`/`er019_family_x_audio_production_runner_01.py`/`er026_family_z_fiction_production_runner_01.py`/新規`er071_gloss_alignment_correction_01_t3_mock.py`/`er071_gloss_alignment_correction_01_trial.py`/必要なら`_offline_audit_02.py`)、`gloss_alignment_correction_01/`配下の新規md/json(wav・大容量ログは不可、trial出力はjson/mdのみ)、SSOT 4ファイル、delegation_log 2ファイル。`ACTIVE_TASK_KGDC.md`/`RESULT_PACKET_KGDC.md`はgitignored確認のうえaddしない。commit前にstaged差分を `rg -n "sk-|api_key|AIza|Bearer " ` で簡易secret確認。
コミットメッセージ(1): `KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02: Opus条件A反映(A'構造: 関所status+stage停止+HR報告書、Lock/queue不使用)、mode=corrected実装(既定legacy無変更)、『～』条件撤回、追加語span対応record-only、resolve_gloss、unit/T3 mock PASS、Opusレビュー全文保存`。(2): `KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02: 有料Trial T1/P7/T2(JPY<実績>)結果+Regression+SSOT/OF台帳(OF-KGDC-01〜12)反映、Status=<VALIDATED/REJECTED/UDR>(PRODUCTION未採用・既定legacy)`。trailer `Managed-ID: KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/ACTIVE_TASK_KGDC.md`を固定ヘッダ書式で更新(Status/UDR-blocking/UDR-deferred/APPROVED未配線/STOP条件/次アクション/未回答報告/報告単位Status。「量産run凍結: 承認前はKP段を含む量産runを出さない」を明記)。`docs/pm/RESULT_PACKET_KGDC.md`(50行以内)にユーザー§9の11項目へ1対1で: 1 二欠陥の根本原因/2 修正前後の設計・動作差分/3「～」辞書的使用と意味欠落の判定結果(誤NG・誤PASS件数、分母)/4 追加Trial件数・分母・品質結果(T1/P7/T2、1回目INVALID率・2回失敗率、95%上限)/5 失敗時HR通知とTTS停止の検証証拠(T3各パターンのPASS、API呼出0)/6 誤PASS・誤NGと既存gloss副作用(O1差分0、対照不変率、直訳化目視)/7 追加量産費・実行時間・HR見込み頻度(実測出典)/8 (01B・KGORAへの参照のみ、本委任では再調査しない)/9 Production正式経路・retry/fallback/regeneration整合の確認結果(外側retry・M2 fallback・Z resume)/10 SSOT/Gitの変更範囲と未解決OPEN/11 Trial Closeout Status(VALIDATED/REJECTED/UDR)と本当にユーザー判断が必要な事項(例: 機械検査のgate化、既定ON/OFF、Production採用)。加えてT-0結果/費用実績(T1/P7/T2別、合計、上限10)/使用モデルと最新か/一覧外Read理由/commit hash。

## Opus条件Aレビュー全文(2026-10-15)

(以下、opus-consultantの報告を改変なしで掲載。`OPUS_REVIEW_01_VERBATIM.md`へそのまま保存すること)

# Opus独立技術レビュー: KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 / DESIGN_DRAFT_01(条件A、2026-10-15、read-only)

このレビューでは実装・修正を行っていない。Production採用可否も判断していない。「安全側」は依頼文の定義に従い、「学習者に届く最終成果物(KP英語+日本語gloss+音声/表示)が目的要件を満たす側、または満たさないものが完成扱いされない側」とした。

## 1. 総評

- **必要/不要**: 必要。欠陥①(「～」記号を合否条件にしていた)と欠陥②(FAILEDでも下流を素通り)はどちらも実在する。コード読解で確認済み(`er003_key_words_gloss_alignment.py:223-226,257-258`、`er003_v1_n3_01_scaffold_generate.py:802-808`、INVESTIGATION_01 5節)。工程目的・プロンプト修正方針・fallback(i)の廃止・item単位の検証という骨格は妥当。
- **推奨構造**: 「停止」は既存の`_only_segments_skip`前例(`er019…:589-598`、非OK statusを返してAudio Validation Gateにassemblyを止めさせる)と、`stage_kp`の`FamilyZE2EStop`で実装する。Human Review Lockと音声用`human_review_queue.jsonl`は流用しない。HR登録は外側retryループが確定した後の最終artifactに対して1回だけ行う。
- **最大リスク(BLOCKER)**: 草案4.2のLock流用は**fail-open(異常時に止まらず通過する)**になる。
  - 実際のA2 KP日本語のwavは`narration/meaning_{i}.wav`(iはrank順のindex)で、Lockのcanonical_textは`ja_gloss_tts`(`er019…:1259-1268`)。草案の`kp{rank}_japanese_meaning.wav`/`text=現在gloss`で記録すると、Lockのkey・text hashと一致しない。そのためLockは「新version」としてTTSを通し、OK→VALIDATED→assemble完了となる。
  - B1ではglossがKP解説LLMの入力(`er019…:898`)になっている。まだ存在しない解説テキストに対してLockをかけることは原理的にできない。
- **次点リスク**: 停止後の「HR解消→再開」の手段が無い(Family Zは再開時に選定から再実行される可能性が高く、人間が確定したglossは上書きされる)。また、新しい機械検査(追加語→日本語span対応)が慣用句的な自然なglossを誤NGにする、または直訳調への書換えを誘発するリスクを、Trial計画が測っていない。

## 2. 12観点の判定(1行ずつ)

1. 必要性: 必要。根拠はINVESTIGATION_01:29-41(FAILEDの素通り)、gloss_alignment.py:223-226(「～」ルール)。
2. より単純な構造: 単純化できる。Lock+queue+Gate+report+summaryの5点セットは過剰。単一の関所(`_generate_or_reuse_kp`の前例+`stage_kp`)+HR報告書+run summaryで足りる(er019…:589-598、er026…:1175-1178)。
3. 既存処理の利用: 方針は良い。ただし選んだ既存機構が誤っている。Lockは「wav生成後のASR結果記録」が前提で(er011:355-358 docstring「generate関数の実行完了後に必ず呼ぶ」)、queueは音声segment単位(er006:321-336)。
4. 前段情報の喪失・再探索: 一部懸念あり。追加語は`kp_adds_words_beyond_display`の算出を再利用しており良い(gloss_alignment.py:90-103)。一方、Family Zの解説はdisplay_phrase+旧/新glossを入力にし、sigにglossを含めない(er026…:1188-1196)。このためgloss確定後も解説が古いまま再利用されうる。
5. 不要なLLM処理: 追加なし(call数は不変、出力フィールド1つ増)。妥当。代替案E(独立verifier)を保留したのも妥当。
6. 非決定性: 微増。item単位retryの仕様が未定義(2回目に全件を再送するのか未解決分だけか、2回目で結果が変わった既成立itemをどう扱うか)。DESIGN_DRAFT_01:28,50。
7. Human Review: 増える方向。ただし例外対応としては正当。増加量は機械検査の誤NG率に依存し、未測定(TRIAL_PLAN_01にその型のパターンが無い。後述j)。
8. 不要なRewrite: 懸念あり。対照10件中1件で誤書換えが実測されている(DESIGN_DRAFT_01:83、`drop the fee`)。さらに語ごとのspan要求は、慣用的なglossを直訳調へ書き換える圧力になる(承認規則19行「直訳調…は避けて」に反する方向)。
9. コスト: 問題なし。追加出力は対象item(全体の0.6〜1.4%)に限られ、1記事セットあたり恒久増は概ね0.01円未満のオーダー(推定、T1で実測)。
10. retry/fallback/regenerationとの整合: 不整合あり。再整合は外側Redundancy retryループの内側(scaffold:715-733)にある。草案7節はHR登録を`run_key_phrase_canonicalization`内に置いており、外側retryで選定し直した場合に、存在しなくなったKPのHR/Lockが孤児として残る。
11. Failure時に安全側へ倒れるか: 設計意図は安全側。ただし実装方式(Lock)がfail-openで、B1の解説経路は未停止。現状のままでは安全側にならない(BLOCKER)。
12. 再発防止: 部分的。「消費側が状態を参照する」という構造化は再発防止になる。ただし同型の抜け道(INVESTIGATION_01 7節a: Family XのNG_REVIEW_REQUIRED素通り)を同じ関所で塞げるのに、対象外にしている。

## 3. 追加観点(a)〜(k)

**(a) 正常系・異常系の最終成果物**
- 正常系: 最終KP+再整合gloss(または不変)→TTS→Gate→完成。要件を満たす。残るリスクは、span自体は存在するが意味が誤る誤PASS(LLM依存)と、整合済みglossの誤書換え(実測1/10)。
- 異常系(草案どおり実装した場合の実際の挙動):
  - A2: Lockのkey/textが一致しないためLockは発動しない。TTS段で`STOPPED_…` statusを記録する実装も別途必要で、それが無ければ、旧glossを読み上げた`meaning_i.wav`がVALIDATEDになりassembleされる。成果物=不整合のまま完成。要件違反。
  - B1: glossが解説LLMへ流れ、解説音声が生成される。表示(page)にも旧glossが出る(`er019…:1890`、display_gloss:994)。
  - Z: `stage_kp`で停止するので成果物は無い(要件を満たす)。
- 推奨構造での異常系: 当該levelのKP segmentは`STOPPED_GLOSS_ALIGNMENT_FAILED`を返して0 API callとなり、B1の解説生成もしない。Gateが`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`を出し、完成物は無い。HR報告書・run summary・stdoutで報告される。
- MUST: 異常系の成果物を実データで1例観測する(T3を拡張)。

**(b) 承認済み仕様との整合**
- 3.3の課題指示文: 「スロット語に限り許可」は削除済みで、承認規則との矛盾は解消している。
- 残る緊張は「すべての語」「過不足なく」と承認規則17/19行「短く自然」「直訳調を避ける」の間。指示3(各追加語に対応するspanを切り出す)は、慣用的な訳(例: 句全体を1語で訳す)を禁止する意図ではないことを1文で明記するべき(SHOULD)。例:「複数の英語語が一つの日本語表現でまとめて表されている場合は、同じ部分を複数の語に対応させてかまいません」。
- 判定例2行: どちらも`based on`系。モデルが「～をもとにした」型へ寄る偏りは小さいと見る。ただし例1(`based on`)は追加語なしで再整合対象にならないため、例としての情報価値は「～可」のシグナルだけ。偏りの懸念はT1で、例と無関係な語彙での出力を見れば足りる(MAY)。
- 承認規則15行(数値の穴埋めを要する句・gloss「ソロ旅行を～％とする」は選ばない)に対し、TRIAL_PLAN_01 P3は`put solo travel at`を「正当な辞書的『～』」として扱っており、承認規則と矛盾している(MAJOR、OF-KGDC-07)。census 28/29「正当」の推定にも同型が含まれていないか、再確認が必要。
- 選定/canonicalization Prompt・Rule7・Gateには触れていない。整合している。

**(c) 既存機構との整合**
- Lock: 流用不可(MUST)。理由は4点。
  1. 前提(生成後の記録、attempts_logの集計)と合わない(er011:355-386)。
  2. key/textの不一致でfail-open(meaning_{i}.wav / `ja_gloss_tts`)。
  3. `attempt_history.jsonl`へ`action=PROCEED, human_review_reached=True`が追記され、HR統計とtelemetryを汚染する(er011:450-468)。
  4. 人間が「現glossで良い」と判断した場合の解除(`approve_regenerate`)と、artifact側の`FAILED`という二重の状態源ができる。
- queue: 流用は非推奨(SHOULD NOT)。`human_review_queue.jsonl`はリポジトリ共通の単一ファイル(er006:321)で、参照元は33ファイル(state guard、census、HRページ生成`tools/build_family_z_hr_review_page.py`等)。消費側でsteps無しentryを許容するかの確認は「build_review 1本」では済まない。音声を持たない種別のentryを混ぜると、既存のHR集計やstate guardの比較を壊すおそれがある。
- Gate: 新status文字列で確実にblockされる(assemble.py:111-134で非許可statusはUNVALIDATED、482/495でblocked)。ただし`tts_generation_results.json`が無い場合はGateが即return(assemble.py:472-473、既存のfail-open)。TTS段を飛ばしてassembleする経路が存在しないことをT3で確認する(MUST)。
- FamilyZE2EStop: 整合する。外側retryとM2 fallbackは、HR登録を外側ループ確定後に置けば整合する(MUST、OF-KGDC-04)。

**(d) E2E整合**
- HR解消の手段が無いと詰む(MUST)。
  - Family X: artifactの`FAILED`が残る限り、関所が永久にTTSを拒否する。
  - Family Z: `stage_kp`の例外はrunner内で送出されるため、`ensure_stage`に結果が保存されず、再開時に選定から再実行される可能性が高い(`w62.ensure_stage`は未精読のため推定)。そうなると人間の確定glossはsrc→dstの上書き(er026…:1150-1158)でも失われる。また再選定は事実上「案B」になる。
  - 最小手段: `resolve_gloss(kp_json_path, rank, gloss, resolved_by)`の小関数1つ。glossと`japanese_gloss_tts`を書き、`gloss_alignment_status="HUMAN_RESOLVED"`と記録者・時刻を残す。ZではsrcとZの段結果の両方を対象にする。あわせて「HR解消後の再開は選定を再実行しない」ことをT3で検証する。
- Zの解説(kp_expl_b1b)はsigにglossを含まないため、gloss確定後も旧glossを入力にした解説が再利用される(er026…:1188)。sigにglossを含めるか、HR解消時に`regenerate_stage=kp_expl_b1b`を必須手順にする(SHOULD)。

**(e) 新しい機械検査(追加内容語→日本語span)**
- 必要性: 同じLLMの自己申告を構造化したもの(span実在の検査は幻覚検出にのみ独立性がある)。効果は主に「LLMに追加語を必ず意識させる」ことで、捕捉力は「LLM自身が対応を見つけられない」場合に限られる。意味が誤ったspan(prices→コーヒー豆)は通る。
- 誤NGの経路:
  1. 1:1対応を要求している(草案3.1「1:1か」)ため、慣用句・複合語(raw-bean→「生豆」を1span、bring in a human helper→「人の手を借りる」)が不一致になる。
  2. 機能語(around、in等の前置詞・不変化詞)が追加語に入る(`_TOKEN_RE`は冠詞のみ除外、gloss_alignment.py:97-102)。
  3. 表記ゆれ(全角/半角、～/〜、活用形でspanを書いた場合)、英語語の綴り(' / ')。
  4. 日本語での主語・目的語の省略(close around me→自然な訳で「私」を省く)。
- 最小形(MUSTとして提案。Production追加はユーザー承認事項):
  - mappingは多対一・重複を許可し、`english_word`に句も可とする。
  - 機能語(前置詞・不変化詞・助動詞・代名詞の一般化)は必須対象から外す。
  - 比較はNFKC正規化と空白除去の後の部分文字列一致とする。
  - 判定は「必須の内容語すべてが、記号以外のspanにどれかの対応で覆われている」こと。
- 新しい品質条件として、Trial中は「gateとして判定する場合」と「記録のみの場合」の両方を集計し、gateが追加で何件捕捉し何件誤NGを出したかを、ユーザーの採否判断材料にする。

**(f) Q/D/量産C**
- 出力増分: 1対象itemあたり数十トークン程度(推定)。reasoning tokenの方が支配的なので、1 batchあたり+数%〜十数%(推定、未測定)。対象は全item中0.6〜1.4%なので、1記事セットあたりの恒久増は0.01円未満のオーダーで、70円・1〜2円基準のいずれにも影響しないと見る(T1で実測確定)。
- HR到達率: 対象記事率(約7%)×2回失敗率。現行の観測は0/16。新しい機械検査の誤NG率次第で、これが支配的になる。Q/Dへの影響(ユーザーの時間)の方がCより大きい。T1で「1回目のINVALID率」と「2回とも失敗した率」をitem単位で報告させる(MUST)。

**(g) 撤去対象の列挙漏れ**
草案7節に載っているもの: `SLOT_TOKENS`/`kp_has_slot_word`/`gloss_has_unjustified_slot`/fallback(i)/`revert_to_candidate_allowed`。漏れていると見るもの:
- `GLOSS_ALIGNMENT_FALLBACK_MODE`と定数群(gloss_alignment.py:42-45)、`apply_alignment`の`fallback_mode`引数
- モジュール冒頭コメント20-22行(OF-227(i)の説明)と46行
- `build_gloss_alignment_fallback_record`のnote「人間確認Queueへは送らない」(:397)
- `apply_alignment` docstring(:323-329)
- `write_failed_notice`の出力先(key_phrases/配下)とファイル名の扱い
- テスト(`er003_test_key_words_gloss_alignment.py`の該当12箇所。特に不整合出力をassertする`test_failed_alignment_keeps_kp_flags_failed_not_human_review`と「～」禁止を固定するtest)
- 参照スクリプト(`er071_gloss_alignment_01_replay.py`/`_census.py`/`_correction_01_offline_audit.py`。これらは証跡なので、改修ではなく旧版固定のまま保存し、import破綻を避ける注記が必要)
- SSOT・台帳側のOF-227/228/230の文言、OPEN-356の運用文言

(SHOULD: 撤去対象をGrepで再列挙した一覧を実装委任文に含める)

**(h) 停止粒度**
- Family Xでitem単位の保留は技術的に可能。ただしHR解決策の一つが「KP再生成」(5件全体と相互重複判定が変わる)なので、当該levelのKP segment全体(5 rank)を保留し、本文・support・他levelは継続するのが、無駄TTSと複雑度のバランスとして良い(SHOULD)。
- B1では解説LLMの生成も同じ粒度で止める(MUST)。
- Zのstage停止は既存前例に合致し妥当。ただしb1bで停止するとa2も止まる(ループ順、er026…:1166)。独立工程を止めることにはなるが、KP段は安価なので許容範囲。

**(i) 案Bの技術的得失(判断はユーザー)**
- 得: HR到達率が下がる。既存ループ(`KEY_PHRASE_REDUNDANCY_RETRY_MAX`)の再利用なので新機構が無い。
- 失:
  - 問題のない他4件のKPまで入れ替わる(観点8、不要なRewrite)。
  - 同じ記事・同じPromptなので同一句が再選定されやすく、同じ失敗を繰り返しうる(実効性は未測定)。
  - 再選定とcanonicalizationの費用が増える。
- 方針Cとの関係: 「再整合2回失敗→HR」を文字どおり読めば、HRの前に再選定を挟むのは文言と異なる。「再整合段の2回」とは別の上位retryと解釈することは技術的には可能だが、その解釈を採るかはユーザーの判断。
- 注記: Zの現行再開挙動は事実上、案Bを暗黙に実行する可能性がある((d)参照)。

**(j) TRIAL_PLAN_01の十分性**
- 有効な点: O1(対象外itemの差分0・呼出0)は決定論的で、非劣化の強い証拠になる。T3の(a)〜(m)は網羅的。
- 不足しているパターン:
  1. 追加語を持つ拡張KPで、自然な慣用的glossが正解のもの(機械検査の誤NGと直訳化の測定。P3は追加語が空になり機械検査を素通りするので、この検証にならない)。
  2. ハイフン複合語、多語→1span、機能語の追加(bring in、close around)。
  3. 表記ゆれ・活用形のspan。
  4. 承認規則15行違反の`put solo travel at`をP3から外し、規則違反の検出側(期待NG)へ移す。
  5. T3への追加: 外側redundancy retry後にHR孤児が残らないこと/`tts_generation_results.json`欠落時のGate/HR解消→再開で選定を再実行しないこと/B1解説が生成されないこと/page・playerにFAILED glossが出ないこと/HR統計(attempt_history・queue)を汚染しないこと。
- 件数の根拠(パターン×2rep)は情報価値の観点で妥当。ただし0/20の95%上限が約14%であることは、量産判断に十分ではない。量産判断は決定論部分(O1/O3/T3)と、誤NG・HR率の点推定+上限の併記で行う、と明記する(SHOULD)。
- 合否基準: VALIDATED条件に「機械検査の誤NG 0(慣用句パターン)」と「直訳化の目視評価」を追加する(SHOULD)。

**(k) 既定ONのリスクと既定OFF化**
- INVESTIGATION_01 8節は「S3 既定OFF化が必要」とするが、技術的には条件付きで異論がある。
  - OFFにすると再整合前の挙動に戻る。過去実測では対象itemの6/8が不整合のまま無検出で通過しており、これは定義上「安全側」ではない。
  - 現行ONでは、欠陥①②があっても成功経路は16/16整合で、失敗時は旧glossに戻る(=OFFと同等)。つまりitem単位ではON≧OFFの品質になる。
- 量産を再開する前の技術的推奨:
  - (1) 量産runの運用凍結をFable側で明示的に管理する。
  - (2) 実装中・Trial中は、環境変数ではなく`align_glosses(enabled=True)`をTrial runnerから明示的に渡す(import時評価のenvに依存しない)。
  - (3) 既定値は、新設計のfail-closed(停止)部分が入るまでは現行ONのまま、または量産そのものを止める。OFF化は「承認境界」上は安全だが「品質」上は後退する、とユーザーに得失を並べて提示する。
- 採否はユーザー。

## 4. 所見一覧

- **OF-KGDC-01 / BLOCKER**: Human Review Lockの流用がfail-openになる。
  - 内容: 草案4.2のLock流用はfail-openで、TTS停止として機能しない。
  - 根拠: KP日本語wavは`narration/meaning_{i}.wav`、canonical_textは`ja_gloss_tts`(er019…:1259-1268)。Lockはパス由来のkeyとtext hashが一致しないと「新version」としてproceedする(er011:327-331)。`record_outcome`は生成後の記録が前提(er011:355-386)。
  - 推奨: Lockを使わない。`_generate_or_reuse_kp`の`_only_segments_skip`前例と同型で、itemの`gloss_alignment_status in {FAILED}`なら`{"status":"STOPPED_GLOSS_ALIGNMENT_FAILED"}`を返す(0 API call)。Gateは無変更でblockする。
  - 採用時に生じ得るFailure: 関所を経由しない別のTTS呼出元(他Familyや旧runner)で素通りが起きる。呼出元をGrepで全数確認すること。
- **OF-KGDC-02 / BLOCKER**: B1の解説経路が止まらない。
  - 内容: B1ではglossが英語解説LLMの入力とページ表示に流れ、草案の停止範囲(TTS)では止まらない。
  - 根拠: er019…:898,994,1890。Zはer026…:1194-1196。
  - 推奨: 解説生成の入力を組み立てる箇所でもFAILED itemを除外し、解説segmentを非OK statusにする。page/player生成がGateの後にしか実行されないことを確認する。
  - 採用時に生じ得るFailure: 解説が欠けたlevelの構造完全性チェック(`_check_structural_completeness`)が別の理由でblockし、停止理由が分かりにくくなる。statusにreasonを必ず載せること。
- **OF-KGDC-03 / MAJOR**: HR解消後に再開する手段が無い。
  - 内容: Family Xはartifactの`FAILED`が永久にblockし、Zは再開時に選定から再実行して人間確定値を失う可能性がある。
  - 根拠: 草案8節3は未決。er026…:1150-1182(install_kp_assetsの上書き、runner内の例外)。
  - 推奨: `HUMAN_RESOLVED`を書く小関数1つ+手順書。Zでは段結果の保存先と再開経路をT3(l)で実証する。Zの解説sigにglossを含める。
  - 採用時に生じ得るFailure: 人手で書いたglossが承認規則(括弧・算用数字・…)に違反する。resolve関数内で既存の記号チェックを再利用すること。
- **OF-KGDC-04 / MAJOR**: HR登録の位置が外側retryと矛盾する。
  - 内容: HR登録(report/summary)を`run_key_phrase_canonicalization`内で行うと、外側redundancy/記号QAのretryで捨てられたattemptのHRが孤児として残る。
  - 根拠: scaffold:715-733(canonicalization内)、:812以降のループ。草案7節。
  - 推奨: HR報告とeventの生成は`run_key_phrases`の戻り(最終artifact)に対して1回だけ行う。
  - 採用時に生じ得るFailure: 途中attemptのFAILED履歴が失われる。attempts_detailは監査用に残すこと。
- **OF-KGDC-05 / MAJOR**: 音声用HR queueへの非音声entry混入。
  - 内容: `human_review_queue.jsonl`は全体共通の音声segment用ファイルで、参照元が33ファイルある。非音声entryの混入は既存のHR集計やstate guardに影響しうる。
  - 根拠: er006:321-336、Grepの結果。
  - 推奨: queueへは載せない。「届いた」の5条件を、①HR報告書のスキーマ再読検証、②run summaryのevent、③最終stdout行と非ゼロ終了またはSTOP status、④下流停止のmock実証、の4条件に置き換える。
  - 採用時に生じ得るFailure: 既存HRページで一覧化されず見落とされる。PM報告の必須項目(run summaryのevent)で担保すること。
- **OF-KGDC-06 / MAJOR**: 新しい機械検査の誤NG・直訳化を誘発する仕様。
  - 内容: 1:1対応、機能語の算入、正規化なし、という仕様が慣用的な自然なglossの誤NGと直訳化(承認規則19行と逆方向)を誘発する。
  - 根拠: 草案3.1「1:1か」、gloss_alignment.py:97-102。
  - 推奨: (e)の最小形(多対一・重複可、機能語除外、NFKC比較)。gateと記録のみの両方で集計する。Production追加はユーザー承認とする。
  - 採用時に生じ得るFailure: 判定が緩くなり、欠落の一部を見逃す(誤PASS)。T1のP1/P4で検出率を確認すること。
- **OF-KGDC-07 / MAJOR**: Trialのラベルが承認規則と矛盾。
  - 内容: TRIAL_PLAN_01 P3が`put solo travel at`(承認規則15行で禁止されている「～％」型)を正当な対照として扱っている。
  - 根拠: b1_p2…template.txt:15、TRIAL_PLAN_01:26。
  - 推奨: P3から外し、期待NGのケースへ移す。census 28/29の推定ラベルを再点検する。
  - 採用時に生じ得るFailure: 対照の数が減り、統計上の上限がさらに広がる。代わりに辞書的な「～」の正当例を追加すること。
- **OF-KGDC-08 / MAJOR**: Trialに慣用句パターンが無い。
  - 内容: 「追加語あり×自然な慣用的訳が正解」のパターンが無く、機械検査の誤NGとHR到達率を量産判断できない。
  - 根拠: TRIAL_PLAN_01:21-30(P3は追加語なし)。
  - 推奨: P7(5〜6件×2rep、約0.3円)を追加。「1回目のINVALID率」と「2回とも失敗した率」をitem単位で報告する。
  - 採用時に生じ得るFailure: Trial費用が微増する(JPY5の上限内)。
- **OF-KGDC-09 / MINOR**: item単位retryの仕様が未定義。
  - 内容: 2回目の入力が未解決itemのみか、既成立itemの結果をどちらで採用するかが決まっていない。
  - 根拠: 草案2節:28、3.2:50。
  - 推奨: 2回目は未解決itemのみで`build_user_message`を再構築し、各itemは最初の有効出力を採用する。
  - 採用時に生じ得るFailure: 1 batchが2 callに分かれ、費用がわずかに増える(上限は不変)。
- **OF-KGDC-10 / MINOR**: 「真なら不変」の厳密比較が表記差でもINVALIDになる。
  - 内容: `current_gloss_consistent=true`でgloss==currentの厳密比較を行うと、空白や～/〜の表記差でもINVALIDになり、HRへ進む。
  - 推奨: NFKCと空白除去の後に比較する。真の場合は、比較で一致を確認したうえで、採用値は常にcurrent(元の文字列)にする。
  - 採用時に生じ得るFailure: 正規化で同一とみなした実質的な書換えを見逃す。正規化の範囲を空白と～/〜に限定すること。
- **OF-KGDC-11 / MINOR**: 同型の抜け道を同じ関所で塞いでいない。
  - 内容: Family Xの`NG_REVIEW_REQUIRED`素通り(INVESTIGATION_01 7節a)を、今回の関所(runnerのKP後チェック)で同時に塞げるのに対象外にしている。
  - 推奨: 別OPENとして起票し、実装は同じ委任内で行うのが効率的。ただし別仕様なので、承認を分けて扱う。
  - 採用時に生じ得るFailure: 既存のFamily X runで、これまで黙って通っていた記事が停止するようになる。
- **OF-KGDC-12 / MINOR**: 既定OFF化の判定が品質面の後退を考慮していない。
  - 内容: INVESTIGATION 8節の「S3 既定OFF化が必要」は、品質面での後退(OFFでは対象itemの6/8が不整合のまま無検出)を考慮していない。
  - 推奨: (k)のとおり得失を並べてユーザーに提示する。Trialは`enabled=True`を明示的に渡す。
  - 採用時に生じ得るFailure: OFFを採らない場合、承認前の仕様が量産経路で動き続ける。運用凍結の明示管理が必須。

## 5. 代替案

**案A'(推奨。Aを修正したもの)**:
- Aの「Lock+queue」を外し、停止は次の3箇所で行う。
  - (1) Family Xの`_generate_or_reuse_kp`と解説入力の組み立て箇所で、`_only_segments_skip`と同型の非OK statusを返す。
  - (2) Zの`stage_kp`で既存の`FamilyZE2EStop`を送出する。
  - (3) runner側では、KP段の後に最終artifactから`collect_unresolved`を1回実行し、HR報告書・run summary event・stdoutを出す。
- 新機構はstatus文字列1つ、`collect_unresolved`関数1つ、`resolve_gloss`関数1つのみ。
- 機械検査は(e)の最小形とし、gate化はTrialデータを見てユーザーが判断する。
- Aより単純で、fail-openの経路が無く、既存HR統計を汚さない。

案B・C・D・Eの扱いは草案どおりでよい(Bの判断は(i)参照)。

## 6. 実装前に解消すべき未確認事項

1. Family X/Z/その他KP経路で、gloss(`japanese_gloss`/`japanese_gloss_tts`)を読むTTS・LLM・表示の呼出元の全数(Grep一覧)。
2. `w62.ensure_stage`の再開挙動(runnerが例外を送出した後の再実行で選定が再実行されるか)と、`w62.run_kp_stage`内部。
3. page/player生成がAudio Validation Gate(assemble)を通った後にしか実行されないか。
4. `tts_generation_results.json`が無いままassembleへ進む経路の有無(assemble.py:472-473のfail-open)。
5. HR報告の届け先(PM報告に載せる経路)の確定。queueを使わない場合に既存のHRページで見えなくなることを、ユーザーが許容するか。
6. 新しい機械検査(span対応)をProductionの品質条件として追加することへのユーザー承認(Trialの後)。
7. 量産再開までのflag運用(凍結/ON維持/OFF化)についてのユーザー判断。

## 7. 確認した範囲 / 確認していない範囲

**確認した範囲**:
- DESIGN_DRAFT_01(全文)、INVESTIGATION_01(全文)、OFFLINE_AUDIT_01(全文)、TRIAL_PLAN_01(全文)、REVIEW_AUDIT_01 §2・§4
- `er003_key_words_gloss_alignment.py` 37-48、80-439
- `er011_human_review_lock_01.py` 130-499、590-720
- `er019_family_x_audio_production_runner_01.py` 該当行(406-416、570-609、898、994、1228-1272、1890)
- `er003_v1_n3_01_tts_generate.py` 560-590
- `er003_v1_n3_01_assemble.py` 95-134、466-515
- `er006_secondary_asr_01.py` 315-336
- `er026_family_z_fiction_production_runner_01.py` 1140-1205
- `er003_v1_n3_01_scaffold_generate.py` 715-814
- 承認規則テンプレートの「日本語グロス」該当行(15、17、19、21、23)
- OPUS_FINDINGS_LEDGER 252-262
- `human_review_queue.jsonl`の参照ファイル数(33)、撤去対象シンボルの参照数(6ファイル)

**確認していない範囲**:
- `w62`(er062)内部と`ensure_stage`
- `er003_test_key_words_gloss_alignment.py`の本文
- `er003_key_words_canonicalization.py`
- B1のKP段全体(`_generate_key_phrase_segments_b1`の全体)
- page/player生成コード
- `tools/build_family_z_hr_review_page.py`と他のqueue消費側の実装
- `n3_tts.resolve_key_phrase_ja_gloss_tts`
- `gloss_alignment_01/`配下の証跡(VALIDATION_01、cost_01.json等)の実数値
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS本体
- 実行による検証は一切行っていない(すべて読解に基づく)
