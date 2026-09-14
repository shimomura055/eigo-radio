# RESULT PACKET — EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事4/4: Voices 2 Voices)

## 1. Status / 使用path

**status=STOP(生成未着手。実装変更なし。仕様Status変更なし)。**

理由: `er012_b_family_production_runner_01.py`(2 Voices Production Wiring対象、
level="a2"/level="b1")には、**新規トピックのCore本文(Hook/Voice A/Voice B/
Tension/Closing)を書き起こすWriter機能が存在しない**。

- `main_a2()`(level="a2")の`prepare_a2()`は固定パス
  `er012_output/editorial_b_voices_a2_free_address_04/a2/article.md`を読むのみ。
  `reuse_approved_a2_assets()`は入力記事textのsha256を承認済み記事(_04)と
  照合し、不一致なら`[TEXT_HASH_MISMATCH]`でRuntimeError(fail-closed、
  L1224-1227)。Voice A/B以外の全segmentは承認済みbyteのsha256照合コピー、
  Voice A/B本文のみTTS再発火するが**本文テキスト自体は書き換えない**。
- `main()`(level="b1")の`prepare()`も同様に固定パス
  `er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`
  (=Trial成果物)を読むのみ(L64/161)。`run_scaffold()`はComment1-4/Preview
  のみ生成し、Core本文Writerは呼ばない。
- 唯一の汎用「新規トピックWriter」入口は`write_new_theme`stage
  (`main_b1_3v()`内、L1047-1059、`writer_generic.run_writer_stage_generic()`
  呼び出し)だが、これは**level="b1_3v"専用**(3V)であり、
  `er012_b_family_voices_writer_generic_01.py::make_theme_config()`が
  `if len(voice_cards) != 3: raise ValueError("本モジュールは3V(3 Voice)
  専用です。voice_cardsは3件である必要があります。")`(L121-122)で
  2件のvoice_cardsを明示的に拒否する設計。

結論: 2 Voicesは記事タイプとして`PRODUCTION_WIRED`(CURRENT_SPEC.md L637-658、
音声化・QA・Assembly配線)だが、**「新規トピックについて2 Voices記事を
書き起こす」正式Production pathは現状存在しない**(既存2 Voices Production
runnerは固定の承認済み既存記事の音声再配線専用。新規トピックWriterは3V専用
コードのみ)。これを実行するには、(a) 3V専用writer_genericを2V対応へ改造する、
または(b) Trial-07相当の新規Writerスクリプトを新規実装する、のいずれかが
必要であり、いずれも本タスクの権限外の実装変更(仕様変更禁止/新しい
Production仕様を勝手に実装しない)に該当するため、**実装せずSTOP**した
(委任文のSTOP条件「2 Voices正式pathの実行に未承認の実装変更が必要と判明
した場合は実装せずSTOP」に合致)。

## 2〜7. 記事/Ledger/QA/model_id/費用/token

該当なし(生成未着手のため)。API呼び出し・費用発生ゼロ(¥0、Research/
Writer/QA等いずれも未実行)。

## 8. Step 0(Claude Code側集計、Discovery行)

`er014_output/four_type_observation_01/claude_usage_log.md`へDiscovery行
(taskId `a7fead3da74d3b08e`)を追加済み: cumulative_usage=5,855,428/
final_context_size=140,229/tool_uses=57/turns=68/duration_seconds=1313.484
(`measure_delegation_task.py`実測)。Fable通知の最終ターン値(tokens
141,324・tool_uses 69・1,314秒)も参考併記済み。transcript退避は
`docs/pm/transcripts/a7fead3da74d3b08e_recovered.jsonl`(0.90MB、
subagents jsonlから復元、tasks側output was zero-byte)。

## 9. Open Item候補

1. **2 Voices新規トピックWriterの正式Production path不在**
   (本タスクの主発見)。今回のような「既存2 Voices記事タイプで新しい
   トピックの記事を書く」要求に応える正式Production経路がない。対応方針
   (3V専用writer_genericを2V対応へ一般化する/2V専用の新規Writerを設計する
   /当面は対象外とする)はユーザー判断が必要(`USER_DECISION_REQUIRED`)。
2. **3V保守版Fact Safetyゲート(OPEN-120)runtime evidence**: 本タスクでは
   生成自体を行っていないため、発火有無の新規実データは取得できず
   (**未取得、OPEN-120は引き続き未充足**)。
3. 事前指定Read一覧(#5 news driver / #6 aggregate_usage.py / #7
   RESULT_PACKET_4T_DISCOVERY.md書式)は、STOP判定確定後は生成・集計作業へ
   進まなかったため実施していない(理由: 生成自体を行わないため書式流用・
   集計スクリプトが不要と判断)。

## 10. Commit対象候補一覧(本タスクではGit操作なし)

- `docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_VOICES.md`(新規)
- `docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_VOICES_check.json`(新規)
- `er014_output/four_type_observation_01/claude_usage_log.md`(編集、Discovery行追加)
- `er014_output/four_type_observation_01/progress_log.md`(編集、Voices STOP行追加)
- `docs/pm/transcripts/a7fead3da74d3b08e_recovered.jsonl`(新規、Step 0退避)
- `docs/pm/RESULT_PACKET_4T_VOICES.md`(新規、本ファイル)

## 11. T-0結果・事前指定外Read・STOP有無

- T-0: `check_delegation_prompt.py`実行結果=**PASS**
  (`docs/pm/delegation_log/..._VOICES_check.json`)。
- 事前指定外Read(理由付き): 委任文の事前指定Read一覧は「2 Voicesが
  正式pathでそのまま生成できる」前提だったが、調査の結果その前提が
  成立しないと判明したため、以下を追加で確認した(いずれも
  `er012_b_family_production_runner_01.py`の構造理解に不可欠と判断):
  - 同ファイルの`import`一覧(L45-62、`writer_generic`モジュールの存在発見)
  - `main_b1_3v()`の`write_new_theme`stage定義(L1034-1059)
  - `er012_b_family_voices_writer_generic_01.py`の関数一覧・
    `make_theme_config()`3V専用ガード(L117-123)
  - `er012_b_family_voices_a2_production_01.py`の`run_writer_adapt`/
    `run_scaffold_a2`等の関数シグネチャ(L147-753、CEFR-A2適応用であり
    新規トピックWriterではないことの確認)
  - `ls er012_*.py`によるTrialスクリプト一覧確認(`er012_editorial_b_voices_
    trial_07.py`が固定ARTICLE_PATHの出所であることの確認)
- STOP: あり(本パケット1節のとおり)。SSOT編集なし、Git操作なし、
  API呼び出しなし(費用¥0)。
