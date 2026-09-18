## 管理ID

KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01(Fable差し戻し1回目: Gate (a)(b)の「silentlyスキップ/既定無効」がユーザー要件『1件でも不在ならFAILで停止』『供給元本文sha256一致を必須化、不一致なら流用せずFAIL』を満たしていないため、fail-closed化と実経路での再検証を行う)。並行Agentなし。音声stageなし、lock不要。`docs/pm/ACTIVE_TASK.md`の固定ヘッダを「修正1回目」で更新してから開始。

## 性質/到達上限Status/禁止事項

- 性質: Production修正(APPROVED_FOR_PRODUCTION済み範囲内、仕様拡大なし)。到達してよい最大Status: `PRODUCTION_WIRED`(下記全完了時のみ)。
- 費用: 外部API支出禁止(¥0)。記事本文・音声・Key Phrase asset・player・`user_test/`配下の変更禁止。`git add -A`/`stash`/`amend`/`rebase`/`force push`禁止。「Claude判断で追加仕様を広げない」: 修正は下記F-1〜F-5に限定。
- STOP条件: (1)fail-closed化により既存Production driverのいずれかが現行canonical out_dirでGate (a)を通過できず、かつ当該driverへ`article_text`明示渡しを追加しても解決しない、(2)既存テスト(本タスク以外)がfail-closed化で壊れ、下記の「KP segmentを含むepisodeのみ適用」ルールでも解決できない、(3)新Product仕様判断が必要。該当時は修正せず報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任の保存先: `docs/pm/delegation_log/KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01_fix01.md`)

## ユーザー指示(原文)

「(a) Assembly直前に keywords_canonicalized.json の source_span が現行本文に実在するかを機械確認する。1件でも不在ならFAILで停止すること。(b) 他記事からKey Phraseを流用する経路では、供給元本文sha256一致を必須化する。不一致なら流用せずFAILで停止すること。」「retry / fallback / regeneration等、関連する後続経路でも同じ不整合を起こさないことを確認する。」

## Fable差し戻し理由(事実)

1. `er003_v1_n3_01_assemble.py::verify_key_phrase_source_gate()` L399-414: `out_dir/key_phrases/keywords_canonicalized.json`が無い場合、または`article_text`未指定かつ`out_dir/article.md`/`article_normalized.txt`が無い場合に`return None`でsilentlyスキップ。Production episodeがKey Phrase音声を含むのに検証がスキップされ得る(バイパス)。また、runtime evidence`gate_a_canonical20.json`はCLI側の独自解決(`_resolve_article_text_climb`祖先探索)で20/20 PASSを得ており、**実際のAssembly経路`verify_episode_audio_validation_gate(out_dir, level)`が各Production driverの引数でGate (a)を実行できるか(スキップにならないか)は未証明**。
2. `er012_b_family_voices_a2_production_01.py::reuse_key_phrases_a2()` L566-591: `target_article_text`既定`None`でGate (b)無効。将来の呼び出しがこの引数を省略すればGateを迂回できるため「必須化」を満たさない。

## 事前指定Read一覧

1. `er003_v1_n3_01_assemble.py` L385-500(`verify_key_phrase_source_gate`/`verify_episode_audio_validation_gate`全体、`tts_generation_results.json`読込と`blocked`判定の位置)
2. `er012_b_family_voices_a2_production_01.py` L565-640(`reuse_key_phrases_a2`)、Grep `reuse_key_phrases_a2\(` in `*.py` → 全呼び出し元(Production/Trial問わず列挙)
3. `er003_test_key_phrase_source_gate_01.py` 全文(修正対象テスト)
4. `er008_audio_validation_gate_05_test.py` L20-60、`er008_a2_slowdown_invariant_19_test_01.py` L120-170、`er008_n8_qa_hardening_21_gate_test_01.py` L110-130、`er011_open129_structural_completeness_production_wiring_01_test_01.py` L95-125(fixtureにkey_phrasesが無い既存テストの構成把握。これらを壊さない設計判断のため)
5. `user_test/translations/index.json` 全文(20 canonical srcから各Production out_dirを特定: srcのplayer.htmlの親ディレクトリ=Assembly out_dir。wake_before_alarmは`player_std/`の親でlevel別ディレクトリを確認、young_travelers B1は`kp5_regen_and_completion_01/`)
6. Production driverのGate呼び出し引数: `er012_b_family_production_runner_01.py` Grep `verify_episode_audio_validation_gate|asm\.` → run_assembly系が渡す`out_dir`/`level`、`er012_b_family_voices_production_01.py` L692、`er012_b_family_voices_a2_production_01.py` L742、`er012_b_voices_3v_a2_user_test_01.py` L522、`er013_family_c_production_runner_01.py` L916、`er011_family_a_completion_a2_trend_end_to_end_01_run.py` L225/L316/L601、`er011_discovery_generalization_wake_before_alarm_trial_12_audio_run.py` L440、`er014_output/user_test_news_convenience_ai_01/convenience_ai/run_pipeline.py`・`er014_output/user_test_news_light_01/tiny_bags/run_pipeline.py` Grep `verify_episode_audio_validation_gate` → 各呼び出しの`out_dir`実体と、その時点で`out_dir/article.md`または`article_text`が利用可能かを確認
7. `docs/pm/RESULT_PACKET_KEY_PHRASE_SOURCE_GATE_01.md` 全文、`DECISION_LOG.md` L9105-9215(修正対象エントリ)

## 事前指定Grep一覧+追記位置・更新位置の手順

F-1 Gate (a) fail-closed化(`verify_key_phrase_source_gate`):
- 適用条件を「当該episodeがKey Phrase segmentを含む場合」に定義する: `out_dir/tts_generation_results.json`(既存Gateが読む結果)にKey Phrase segment(既存命名`kp{n}_en`/`kp{n}_ja`等。実際のキー名はGrep `kp1_en|kp\d+_` in `er003_v1_n3_01_assemble.py`/`er003_v1_n3_01_tts_generate.py`で確認)が1件以上存在する、または`out_dir/key_phrases/keywords_canonicalized.json`が存在する、のいずれかならGate (a)は**必須**。
- 必須時: (i)`keywords_canonicalized.json`が無い→`RuntimeError("KEY_PHRASE_SOURCE_GATE_ASSET_MISSING: ...")`、(ii)`article_text`未指定かつ`article.md`/`article_normalized.txt`が無い→`RuntimeError("KEY_PHRASE_SOURCE_GATE_ARTICLE_TEXT_UNAVAILABLE: 呼び出し側でarticle_textを明示してください")`、(iii)source不在→既存どおり`KEY_PHRASE_SOURCE_MISSING`。
- 非該当時(KP segmentもKP assetも無いfixture/episode): `audit/key_phrase_source_gate.json`に`{"status":"NOT_APPLICABLE","reason":"no key phrase segments/asset"}`を記録して続行(silent skipではなく理由を残す)。
F-2 実経路での再検証: 20 canonical out_dir(index.jsonから特定)について、各Production driverが実際に渡す引数と同じ形(`verify_key_phrase_source_gate(out_dir, level)`、Family Cは`article_text=`明示)で**実関数を直接呼び**、20/20 PASS(NOT_APPLICABLE 0件)を`gate_a_canonical20_via_wrapper.json`に記録。`article.md`が無い等で(ii)になるdriverがあれば、そのProduction driverの呼び出しに`article_text=<当該driverが保持する本文変数>`を追加して解決し、修正箇所を報告(該当なしならその旨)。旧Free-Address A2/旧AI Hiring A2 out_dirでも同ラッパー経由でFAIL(true positive)を再記録。
F-3 Gate (b) 必須化(`reuse_key_phrases_a2`): `target_article_text`を必須に近い扱いへ変更——`None`の場合は`narration_dir`/`kp_dir`の親ディレクトリ配下の`article.md`から流用先本文を解決し、解決できなければ`RuntimeError("KEY_PHRASE_REUSE_TARGET_TEXT_UNAVAILABLE: ...")`で流用しない(fail-closed)。Gate (b)を無効化する経路を残さない。全呼び出し元(Read一覧2)がProduction経路なら`target_article_text`明示渡しを確認、Trial/履歴driverは変更せず一覧報告。`er012_b_family_production_runner_01.py`の`reuse_key_phrases`/`_3v`の`[TEXT_HASH_MISMATCH]`が例外送出(ログのみでない)であることをコードで確認し、確認結果(行番号)を報告。他にKey Phrase asset(`keywords_canonicalized.json`)を別ディレクトリからコピーするProduction経路がないかGrep `copyfile.*keywords|copy.*key_phrases|kp_source_dir` in `*.py`で確認し、あれば同様にfail-closed化(Trial/履歴は一覧のみ)。
F-4 テスト更新: `er003_test_key_phrase_source_gate_01.py`の「KP asset不在時はsilentlyスキップ」を「KP segmentありでKP asset不在→RuntimeError」「KP segmentなし・asset なし→NOT_APPLICABLE記録」「article_text解決不能→RuntimeError」「reuse_key_phrases_a2で target未指定かつ解決不能→RuntimeError」「同一本文→流用成功(TTS部分はmock/skip)」へ置換・追加。既存テスト(Read一覧4)が壊れないことを確認。
F-5 SSOT訂正: `CURRENT_SPEC.md`のGate行から「既定None=無効」「silentlyスキップ」相当の記述を除去しfail-closed仕様へ更新。`DECISION_LOG.md`の`## KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`末尾に「### FIX-01(Fable差し戻し1回目)」節を追記(差し戻し理由・修正内容・再検証evidence)。`OPEN_ITEMS.md` OPEN-170はCLOSEDのまま(記述にsilent skipがあれば訂正)。`docs/pm/RESULT_PACKET_KEY_PHRASE_SOURCE_GATE_01.md`に`## FIX-01`節追記。

## 実行コマンド全文

- 委任文検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01_fix01.md --json-out docs\pm\delegation_log\KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01_fix01.md_check.json`
- 実経路再検証: `.venv\Scripts\python.exe docs\pm\tools\kp_gate_wrapper_evidence_01.py --index user_test\translations\index.json --out docs\pm\closeout_136_e2e\key_phrase_source_gate_01\gate_a_canonical20_via_wrapper.json --old-dirs er012_output\editorial_b_family_voices_a2_production_wiring_01\a2,er012_output\user_test_voices_a2_minimal_01\ai_hiring_3v_a2\a2`(新規。`er003_v1_n3_01_assemble.verify_key_phrase_source_gate`を直接importして各out_dirに対し実行。Family Cはout_dirに`article.md`が無い場合、当該driverと同じ方法で本文を解決して`article_text=`を渡し、その解決方法を結果JSONに記録。旧2 dirの実pathはGlobで確認して置換)
- 単体テスト: `.venv\Scripts\python.exe -m pytest er003_test_key_phrase_source_gate_01.py er008_audio_validation_gate_05_test.py er008_a2_slowdown_invariant_19_test_01.py er008_n8_qa_hardening_21_gate_test_01.py er011_open129_structural_completeness_production_wiring_01_test_01.py -q`
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er0*_test_*.py"`(既知3件以外の新規失敗なし)
- import確認: `.venv\Scripts\python.exe -c "import er003_v1_n3_01_assemble, er012_b_family_voices_a2_production_01, er012_b_family_voices_production_01, er012_b_family_production_runner_01, er013_family_c_production_runner_01; print('ok')"`

## SSOT追記文

CURRENT_SPEC Gate行(訂正後の要旨): 「Gate (a)はKey Phrase segment/assetを持つepisodeに必須(asset不在・本文解決不能・source不在はいずれもRuntimeErrorで停止。KP無しepisodeのみNOT_APPLICABLEを記録)。Gate (b)は`reuse_key_phrases_a2`および他のKey Phrase流用経路で常時有効(流用先本文が解決できない場合も流用不可)。既存`reuse_key_phrases`/`_3v`の`TEXT_HASH_MISMATCH`例外を同等Gateとして位置付け。」

## Git(明示add対象・コミットメッセージ・trailer)

- commit 1: 明示add `er003_v1_n3_01_assemble.py`、`er012_b_family_voices_a2_production_01.py`、`er003_key_phrase_source_gate_01.py`(変更時)、`er003_test_key_phrase_source_gate_01.py`、Gate引数を追加したProduction driver(変更時のみ列挙)、`docs/pm/tools/kp_gate_wrapper_evidence_01.py`、`docs/pm/closeout_136_e2e/key_phrase_source_gate_01/gate_a_canonical20_via_wrapper.json`ほか本修正のevidence。メッセージ: `KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01 FIX-01: Gate(a)(b)をfail-closed化(silent skip/既定無効を廃止)+実Assembly経路で20 canonical再検証`
- commit 2: 明示add `CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`(変更時)、`docs/pm/RESULT_PACKET_KEY_PHRASE_SOURCE_GATE_01.md`、`docs/pm/delegation_log/KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01_fix01.md`(+`_check.json`)。メッセージ: `KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01 FIX-01: SSOT訂正(fail-closed仕様)`
- trailer: `Task-ID: KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`。push前後`git fetch origin`、main=origin/main確認、混入なし確認。

## 報告(RESULT_PACKET項目)

`## FIX-01`節に:
1. 最終Status(`PRODUCTION_WIRED`/`USER_DECISION_REQUIRED`/`STOPPED`+理由)
2. Gate (a)適用条件の実装(KP segment検出方法・判定分岐・エラー名)と非該当時の記録方式
3. 実経路再検証結果表(20 canonical out_dir: article_source[caller/article.md/…]・status、NOT_APPLICABLE 0件、旧2 dir FAIL)
4. Production driverへ`article_text`明示渡しを追加した箇所(あれば)
5. Gate (b)必須化の実装(流用先本文の解決方法・fail-closed)、`reuse_key_phrases_a2`全呼び出し元一覧と扱い、`reuse_key_phrases`/`_3v`の例外送出確認(行番号)、その他コピー経路の有無
6. テスト結果(新規/更新件数、既存Gateテスト4ファイルPASS)
7. 回帰結果
8. SSOT訂正内容(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)
9. Git commit SHA、main=origin/main
10. 費用¥0確認、一覧外Read(理由1行)、check_delegation_prompt結果
11. USER_DECISION_REQUIRED候補(あれば)
