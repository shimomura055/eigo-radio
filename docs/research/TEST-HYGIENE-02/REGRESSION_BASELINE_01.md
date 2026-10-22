# TEST-HYGIENE-02 REGRESSION_BASELINE_01(OPEN-456 F6)

2026-10-22〜23、費用0(API呼出なし。有料資格情報はダミー値のみ使用)。Production .py・Prompt・fixture本体は無変更(変更はtest fileと、test必須の未追跡fixture2件のgit追加のみ)。

## 1. 結論

- 清浄なHEAD(`70ed348f8`/`d1062c1bf`、他agent差分なし)に**開発環境と同じ前提**(未追跡データ資産・EOL状態・資格情報の有無・mfa_tool)を再現して `run_project_regression.py` を単独実行した結果、**failed 13 / errors 24(計37件)**。全37件を分類し、**(d)Production不具合の疑い=0件**。
- test/fixture/allowlistのみを最小修正した後、同じ前提で再実行して **collected 6,882 / passed 6,872 / failed 0 / errors 0 / skipped 10**(rc=0)。
- pytest群(er078*/er103/er104*/er105/er106/er108/er109、`run_project_regression.py`の対象外)も同じ隔離worktreeで **899 passed**。
- 重要な注記(§5): `git clone`直後(未追跡資産・.env・mfa_tool・LF/CRLF状態が開発treeと異なる)では、修正後も別系統の環境依存138件が残る。これはtest不具合ではなく『開発treeがgit管理外の資産に依存している』という再現性の限界で、OPEN-456 F6の範囲外として別途記録した(§5)。

## 2. 実行条件と前後の数値

| run | 対象 | 前提 | collected | passed | failed | errors | skipped |
|---|---|---|---|---|---|---|---|
| R1 | `4977bfd39`(純HEAD) | `git worktree add`直後。.env無し・未追跡資産無し・autocrlf=true・mfa_tool無し | 6,882 | 6,632 | 45 | 124 | 41 |
| R4(修正前の基準) | `70ed348f8` | 開発tree同等: 未追跡の非.py資産30,296件をoverlay、tracked textのEOLを開発treeと同一(w/crlf 42,882・w/mixed 247を再現)、ダミー資格情報(`OPENAI/GEMINI/SPEECH_KEY`等=`dummy`)、`PYTHONIOENCODING=utf-8` | 6,882 | 6,829 | **13** | **24** | 8 |
| R5(修正後) | `70ed348f8`+本commit内容 | R4同条件(PYTHONIOENCODINGなし、`mfa_tool`はjunction、`git add -u`でindex stat更新) | 6,882 | **6,872** | **0** | **0** | 10 |
| R6(参考:clone直後) | `d1062c1bf`+本commit内容 | R1同条件(clean clone相当) | 6,882 | 6,666 | 36 | 102 | 46 |

- R2/R3は環境同等化の試行(CRLF/未追跡資産が原因で、開発treeの再現として不正確だったため破棄)。R4で開発treeと同じ収集件数6,882・既知の失敗集合(下記37件)に一致した。
- 開発tree自身の直近基準(RUNTIME_EVIDENCE_01 §2: 6,872件中failed 14/errors 18)と、R4(6,882件中13/24)は、未コミット差分(er109)・並行実行・環境条件の違いにより母集団が異なる。件数の直接比較は不可。
- `er003_test_bad`のFAILは本番失敗ではない: `er003_test_*`が起動する入れ子のunittest(意図的に失敗するfixture)の出力が親ログに混ざるだけで、集計(failed/errors)には含まれない(R5ログでも同行が出るがfailed=0)。
- `run_project_regression.py`の`--pattern`は**単一glob**のみ対応(複数patternの併記・ORは不可、改修はしていない)。pytest形式のtest(er078*/er103/er104*/er105/er106/er108/er109の関数test)はunittestでは収集されず、別途`pytest`で実行する必要がある(本baselineでは899 passedを別枠で確認)。

## 3. 分類表(R4の37件。分類: (a)承認済み変更にtest/fixtureが未追従 (b)環境依存 (c)並行/共有state・順序依存 (d)Production不具合の疑い (e)Trial資産のtestで撤去済み経路を参照)

| # | 件 | test(file:行) | 分類 | 原因の根拠 | 対処 |
|---|---|---|---|---|---|
| 1 | 1E | `er003_test_b1_p4d_audio.SudachiTokenizeIntegrationTests...full_pipeline`(:253) | (b) | `er003_b1_p4d_audio.py:80`が`mfa_tool`の`micromamba`をsubprocess起動。mfa_toolは開発treeにだけあるgit未追跡の隔離環境でworktreeに無く`FileNotFoundError`。開発treeには存在(確認済み) | test無変更。検証worktreeへmfa_toolをjunctionで接続しPASS |
| 2 | 1E | `er003_test_b1_p5a_audio.AsrReadingNormalizeTests...sudachi`(:96) | (b) | #1と同一(`p5a`→`p4d.sudachi_tokenize`) | 同上 |
| 3 | 1E | `er003_test_b1_p5a_audio.AzureTtsCallFnIntegrationTests`(:83) | (b) | **実Azure Speech APIを毎回呼ぶ有料test**。ダミー鍵で認証401。既定の全回帰が『API費用0』でない状態だった | 既定skip、`EIGO_RUN_PAID_INTEGRATION_TESTS=1`でのみ実行(opt-in) |
| 4 | 1E+3F | `er003_test_p2j_investigate`(:82,:99,:119,:128) | (a)+(e) | (4a)`:82`: prefix別pattern`{p}_test_*.py`は旧命名しか数えない(現行`er0NN_<name>_test_NN.py`を数え漏らし、6,882 != 2,203)。(4b)`:119/:128`: P2H/P2I era listの`research10`(+2、`652e71e62`)・`min_unit`(+3、`678f38e45`/`0e6744e0b`)へ承認済み変更がtestを追加(1037/665 vs 凍結値1032/660、差はちょうど5)。(4c)`:99`: `per_file_counts`が#8のimport guardでRuntimeError | pattern→`{p}*_test_*.py`、既知増分5を定数化して凍結値との整合を維持(未説明の増減は検出)、`er003_v1_p2j_investigate.per_file_counts`はSkipTest時に1件扱い(discoveryと同じ数え方) |
| 5 | 1E | `er011_open146...Trial15ConditionFReproductionTest`(:256) | (b) | `er011_news_ledger_enrichment_leaveout_trial_12b_run.py`がgit履歴に一度も無い未追跡file(開発treeにだけ存在、`er011_...disambiguation_trial_14_run.py:200`がimport) | 未追跡の当該Trial script(24.6KB、2026-09-11作成、変更なし)をgit追加 |
| 6 | 3E | `er012_b_family_voices_variable_voice_count_test_01`(:41,:47,:337,:521,:532) | (b) | testが`er014_output/.../voices/writer_generic_before.py`(改修前snapshot fixture、`git show HEAD:`で保存済み)をimportするが未追跡 | 当該fixture(89KB、2026-09-14作成、変更なし)をgit追加 |
| 7 | 2E | `er012_e_...two_level_runner_test_01`(:394,:444) | (b) | 子processのstderr(utf-8/cp932)と親`text=True`のlocale復号が不一致だとstderrがNone。`PYTHONIOENCODING`有無で挙動が変わる | 子env=`PYTHONIOENCODING=utf-8`、親=`encoding="utf-8",errors="replace"`に固定(env非依存) |
| 8 | 1E | `unittest.loader._FailedTest.er015_standard_a2_6000_generation_first_trial_01_test_01` | (e) | Trial moduleの`import`時guard(`er015_...py:205`、旧語彙段落が`STANDARD_A2_PROMPT_V5`に無ければ停止)が設計どおり発動。当該語彙段落はユーザー採用でProduction v5へ取込済み(`ed7362a21`、`er003_v1_n3_01_standard_a2_generate.py:109`) | import guard発動時(のみ)`unittest.SkipTest`(他のimport失敗は握りつぶさない) |
| 9 | 5E | `_FailedTest`: `er064_kp_opt_01_fix_test_02`/`er064_kp_opt_01_upstream_test_01`/`er069_attribution_clip_split_trial_01_test_01`/`er070_family_z_std_preview_x_alignment_01_test_01`/`er074_family_z_std_preview_comment_dependency_01_test_01` | (e) | 5件ともstandalone script形式(`python <file>`、末尾`sys.exit`)でunittest discoveryがSystemExitを受けてerror(`er069:64`/`er070:79`/`er074:49`/`kp_opt_fix:118`/`kp_opt_upstream:106`)。各scriptを実行すると全check PASS(27/23/18/64/34)。 | `sys.exit`を`if __name__=="__main__"`へ移し、読込時に実行済みのcheck結果を1件の`TestCase`で検証(script実行方法は不変。回帰としては新規に有効化される) |
| 10 | 1E | `er025_...FamilyXRunnerKwargWiringTests`(:688) | (a) | fixtureが旧構造(heading1/body2等)。承認済みW1(`8d9064083`)で新構造=part1/part2/part3に変わり`er019_family_x_audio_production_runner_01.py:999`が`parts["part2"]`を読む | fixtureをpart1/part2/part3へ |
| 11 | 2E | `er040...:108/110`, `er043...:104` | (a) | `_make_english_key`が承認済みW2(`2ecb0c647`)でphrase名`name`を第1引数に追加(`er006_audio_cost_pilot_02_shared_narration.py:170`)。welcomeは現行Master(v2)継続 | 呼出に`"welcome"`を追加(testの意図a:v1/b:v2は不変) |
| 12 | 1E | `er053_c3_audio_guard_test_01.MainStageTests`(:264) | (a) | 承認済みKPMP-03 fail-closed(`75f52edff`、`er019...py:355-362,2698-2712`)でcanonicalization statusがPASS系(`CANONICALIZATION_PASS`等)でないとrc=3。fakeが`"OK"`を返していた | fakeを`CANONICALIZATION_PASS`へ |
| 13 | 2E | `er064_kp_int_01/02 ...test_tokens_*`(`er064_kp_int_01_prompts.py:194`) | (b) | `tiktoken`は本体.venv非導入(隔離環境のTIKTOKEN_PATH運用) | tiktoken/TIKTOKEN_PATH無しのときskip |
| 14 | 1F | `er064_kp_int_01_test_01.RunnerRules.test_constants`(:171) | (c) | `er064_kp_int_02_run.py:22`/`03_run.py:38`がimport時に共有`RUN.HARD_STOP`を書き換える。同一process(全回帰)では65.0、単独実行では95.0でPASS(順序依存) | Round1 moduleを別名で独立loadして95.0を検証 |
| 15 | 1F | `er064_kp_int_03_test_01.AssetsUnchanged.test_state_guard_if_present`(:191) | (e) | Round3開始時のstate hash(ledger/telemetry/master store等7件)を『現在も同一』と要求。stateはProduction runで正当に更新され続ける(時間経過で必ず陳腐化) | 記録済みguardの内部整合(`unchanged_after_stage0`と`before==after_stage0`)で検証 |
| 16 | 2E+1F | `er073...RunnerTests`(:39,:52,:64) | (a)+(e) | Trial runnerの`check_stop()`(`er073..._run.py:32-37,96`)が`er026_output/.../melos/run_e2e_02/STOP`を検出。これはFable決定B1(2026-10-17、`fb01f125f`)で凍結された正規のSTOP sentinel(削除・回避しない) | 凍結STOPのみ許容として明示。guard/mock runのtestは`check_stop`を固定(STOPファイルには触れない) |
| 17 | 2F | `er008_n8_cost_compute_pricing_fix_24_test_01`(:37,:48) | (a) | `gpt-5.6-sol`の公式単価更新(2026-10-09、`52194b768`、入力$4/出力$20、旧値は`price_history`、promotional〜2026-11-21)に未追従($5+$30を直書き) | `pricing_snapshot.json`のsol単価を独立に読んで期待値化(再更新にも追従) |
| 18 | 1F | `er020...RegressionCorpusTest`(:185) | (e)+(b) | 対象corpusに、現行ruleで記録された『旧False』(Family Z E2E `run_e2e_01/02`・`run_kgcpw_z_e2e_01`の19候補、現行ruleが正当に拒否した過剰改変)が混在し『旧False→PASS救済』前提が崩れる。corpusの大半は未追跡で、clean cloneでは件数閾値(70/14)で失敗 | 現行rule導入後の3 runを除外(除外後も旧True91/旧False14)、corpus不足の環境ではskip |
| 19 | 1F | `er066_...TestExistingSpecClosedCounterList.test_production_does_not_import_trial`(:44) | (a) | 部分文字列一致のため、Productionの『移設元』コメント(`er078_asr_value_guard_01.py:23,109`)に反応。禁止対象は実import | import文のみ検出、parity test(`er078_asr_value_guard_01_test_01.py`、test側のみTrialをimportする設計)は対象外 |
| 20 | 2F | `er068_...`(:44,:180) | (a) | (20a)recorded holeだった`cats->dogs`はユーザー承認のF1是正(ASR-PHONETIC-EQUIVALENCE-M1-F1 委任_03、DECISION_LOG当該節)でProductionが閉じた(現行は非PASS=期待された改善)。(20b)全er0*.pyの`er068_`部分文字列走査が後続の研究script(er075/er077)とtestに反応 | (20a)期待を『非PASS』へ(穴が塞がれた記録)、(20b)実import文のみ・testと研究script4件を明示allowlist |
| 21 | 1F | `er086_writer_detective_avoidance_trial_01_test_01`(:54) | (c) | 検証用worktree固有: `git status --porcelain`が、EOL調整後のindex stat未更新で5つのProduction fileを`M`表示(`git diff`は空)。内容差はなし | test無変更。`git add -u`(隔離worktreeのindexのみ)後にPASS |
| (計) | 13F+24E=37 | | | | |

(d)Production不具合の疑い: **0件**。#12は承認済みfail-closedの意図どおり、#20aは期待された改善、#16は正規STOPの尊重であり、いずれもProduction側は無変更。

## 4. 修正一覧(commit内容)

- test変更21 file: `er003_test_b1_p5a_audio.py` / `er003_test_p2j_investigate.py` / `er008_n8_cost_compute_pricing_fix_24_test_01.py` / `er012_e_..._test_01.py` / `er015_..._test_01.py` / `er020_..._fullseg_test_01.py` / `er025_..._test_01.py` / `er040_..._test_01.py` / `er043_..._test_01.py` / `er053_c3_audio_guard_test_01.py` / `er064_kp_int_01_test_01.py` / `er064_kp_int_02_test_01.py` / `er064_kp_int_03_test_01.py` / `er064_kp_opt_01_fix_test_02.py` / `er064_kp_opt_01_upstream_test_01.py` / `er066_..._test_01.py` / `er068_..._test_01.py` / `er069_..._test_01.py` / `er070_..._test_01.py` / `er073_..._test_01.py` / `er074_..._test_01.py`。test補助script 1 file: `er003_v1_p2j_investigate.py`(`per_file_counts`のSkipTest扱い。Production外の調査script)。
- 未追跡fixtureのgit追加2件(内容変更なし): `er011_news_ledger_enrichment_leaveout_trial_12b_run.py`、`er014_output/four_type_observation_01/voices/writer_generic_before.py`(secret_scan hits=0)。
- Production .py・Prompt・fixture本体・`run_project_regression.py`は無変更(`git diff --name-only`で確認)。fixtureの『再生成』は不要だった。

## 5. 残る限界(clean clone再現性。(d)ではない・test不具合でもない)

R6(`git worktree add`直後の素の状態)では修正後も138件が残る。原因はすべて環境条件であることを再確認した:

| 区分 | 件 | 内容 |
|---|---|---|
| A | 44 | `.env`が無く資格情報が未設定(Gemini/OpenAIクライアント生成が失敗)。ダミー値で解消(R4/R5はダミー設定) |
| B | 約40 | hash固定fixture(`primary_text_excerpt.md`のsha等)が、autocrlf=trueのcheckout(CRLF)と開発tree(LFで保存されたfile)で不一致 |
| C | 12 | 資格情報が無い経路で『REAL API PATH CALLED』guardが発火(Aの副作用) |
| D | 約27 | 未追跡のdata資産(`er003_output/p1b/A01/translated_en_raw.md`等)・`mfa_tool`が無い |
| E | 数件 | 上記の派生(hash/knock-on) |

- 『開発treeがgit管理外のdata資産・EOL状態・.envに依存する』という構造的事実であり、全回帰の信頼できる基準は『開発tree(または本baselineと同条件)』である。clone直後で全回帰を回す運用は現状想定されていない。
- 必要なら別Scopeで、(i)hash固定fixtureに`.gitattributes -text`を付す、(ii)data資産の追跡化または`skipTest`化、を検討できる(件数と容量が大きいため本委任では実施しない)。OPEN-456 F6の記録に残した。

## 6. 検証手順(再現)

1. `git worktree add <scratch>/wtN HEAD`(`-c core.autocrlf=false`推奨)。2. 開発treeの未追跡・非.pyの資産(`git ls-files -o`から`.venv*`/`__pycache__`/`mfa_tool`/`.env`/`docs`を除く30,296件)を同位置へコピー。3. 開発treeで`w/crlf`/`w/mixed`のtracked textを同じEOLに揃える。4. `mfa_tool`をjunction。5. ダミー資格情報(`OPENAI_API_KEY=dummy`等)を環境変数に設定(.envは使わない)。6. `.venv\Scripts\python.exe run_project_regression.py --json-summary <out>`を単独で実行。7. 終了後`git worktree remove`。
