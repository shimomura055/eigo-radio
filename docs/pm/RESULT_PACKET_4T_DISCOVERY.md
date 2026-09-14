# RESULT PACKET — EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事3/4: Discovery S2)

## 1. Status / 使用path

**status=OK(生成成功、STOPなし、retryなし)。**
使用path: Discovery S2正式Production関数
`er003_discovery_focus_staged_production_01.run_one_pattern_staged_discovery_focus()`
(monkeypatch・再実装なし、`er011_output/discovery_s2_production_runtime_evidence_02/
run_happy_path_a2.py`と同一の呼び出し型)。Research/VerificationはNews/Trend
driverと同一構造(`vfl01.build_researcher_prompt`/`build_verification_prompt`+
`client.responses.create`、web_search tool)をtopicのみ差し替えて再現。
新規driver: `er014_output/four_type_observation_01/discovery/run_discovery_a2.py`。

補足: `run_one_pattern_staged_discovery_focus()`の引数名は`topic_ja`だが、
News/Trend driverの前例(英語TOPIC_ENを同位置の引数へ渡し正常完走した実績)から
言語非依存の単なるtopic文字列であることを確認した上で、英語のTOPIC_ENを
そのまま渡した(仕様変更ではなく、既存引数の実際の性質の確認)。

## 2. 記事

level=A2、word_count=569語(`run_summary.json`の`metrics`実測値。
`wc -w reader_facing_article.txt`では603語[見出し記号等の数え方の違いによる
差異、未調査・推測しない])。section_word_counts: point_one=50語、point_two=67語。
`er014_output/four_type_observation_01/discovery/reader_facing_article.txt`

## 3. Ledger / Verification

Researcher: 15件下書き(web_search 14 calls)。Verification: VERIFIED(CONFIRMED)=15件、
AMBIGUOUS=0件、REJECTED=0件。全件VERIFIEDのみ採用(先例と同一方針)。

## 4. Stage別経過(`a2/audit/stage_trace.json`要約、3エントリ)

- Stage 1(Main Story Writer + Stage 1 QA): 1回で完了(`stage1_regen_attempt=0`、
  blocking=false)。Stage 1 QA内部でもLedger Deviation Check
  (`stage1_ledger_deviation.json`: LEDGER_COMPLIANT、deviations=0件)と
  Directional Fact Precheck(`stage1_directional_fact_precheck.json`:
  DIRECTION_REVIEW_REQUIRED、13件中advisory)を実施済み。escalation(Stage 1
  再生成)は発生なし。
- Stage 2(Point Role Planning)→Stage 3(Points+Evidence Compression): 1回で
  完了(`stage2_3_retry_attempts=0`)。Point Overlap/Value QA:
  attempt0でlexical_flagged=false、value_qa_status=PASS(overlap_ratio最大
  0.289、threshold 0.4未満、evidence_compression_applied=trueだが
  `applied=false`[閾値未満のため未適用])。Point Overlap retryは**発生なし**
  (OPEN-148該当なし、今回のrunでは観測されず)。
- 記事全体Fact Checker: `fact_verdict=PASS`(`fact_status=FACT_CHECK_COMPLETED`)。
- 記事全体Ledger Deviation Check(`final_ledger_deviation.json`):
  LEDGER_COMPLIANT、deviations=0件→Local Rewrite発火なし
  (`final_local_rewrite_cycles.json`=空リスト、stage1側も空リスト)。
- Directional Precheck(記事全体、`final_directional_fact_precheck.json`):
  overall_status=**DIRECTION_REVIEW_REQUIRED**(13件中2件MATCH、残りは
  「片方にのみ方向表現があり機械的に一致/不一致を判定できない」または
  「thresholdカテゴリのみの衝突でFAILへ格上げしない」という設計上の
  advisory・non-blocking判定。News記事でも同種のDIRECTION_REVIEW_REQUIRED
  が観測されており、Production側の既存設計どおりstatus=OKをブロックしない)。

## 5. Actual model_id(provider別)

全11 API call、provider=openai、model_id=gpt-5.6-luna(researcher/verification/
Stage1 writer/Stage1 Fact QA/Stage1 Ledger Deviation/Stage2 role planning/
Stage3 points writer/Stage3 Evidence Compression/Point Value QA/最終Fact
Checker/最終Ledger Deviation、全て同一model_id)。

## 6. 費用(量産時1記事単価、Standard同期、今回実測)

**合計¥104.25**(budget_jpy=140、budget_exceeded=false)。retry追加分=¥0
(下記4のとおりStage 1再生成・Stage 2-3 retryとも0回、`aggregate_usage.py
--stage-trace`実測で`retry_occurred=false`確認済み)。よって全額が
「retryなし部分」。

内訳(raw_usage_log.jsonlの各callをaudit配下JSONのresponse_id突合[7件]+
消去法[response_idが監査JSONに保存されないLedger Deviation Check 2件]で
手動分類、`docs/pm/tools`非改修のscratchpad計算。詳細算出は本タスクの
Bash実行ログ参照):

| 区分 | 費用(¥) |
|---|---|
| Research/Ledger(Researcher+Verification) | 58.37 |
| Stage 1(Writer+Fact QA+Ledger Deviation) | 18.80 |
| Stage 2(Point Role Planning) | 0.53 |
| Stage 3(Points Writer+Evidence Compression) | 0.56 |
| Point Overlap/Value QA | 0.18 |
| 最終Fact Checker(記事全体) | 25.01 |
| 最終Ledger Deviation Check | 0.80 |
| **合計** | **104.25** |

開発・検証費=¥0(本タスク以外の追加API支出なし)。

`aggregate_usage.py`標準出力(response_id自動突合のみ、Discovery用
audit ファイル名パターン未登録のため`writer`/`qa`への自動分類は
「uncategorized」扱い、正直に報告): `research_ledger=58.37`、
`uncategorized=45.88`(=Stage1〜最終まで全て、上表で手動分類済み)。

## 7. API token(provider=openai, model_id=gpt-5.6-luna、通常/retry分離)

全11 calls、retry分はなし(通常分=全量)。
input_tokens=445,091、output_tokens=38,180、cached_input_tokens=18,070、
total_tokens(=input+output)=483,271。calls内訳は上記6区分に対応する
11 API call(Researcher1・Verification1・Stage1 Writer1・Stage1 Fact QA1・
Stage1 Ledger Deviation1・Stage2 Role Planning1・Stage3 Points Writer1・
Stage3 Evidence Compression1・Point Value QA1・最終Fact Checker1・最終
Ledger Deviation1)。

## 8. Step 0: Claude Code側集計(Trend行、taskId a5bdd52c4daad7ab8)

`er014_output/four_type_observation_01/claude_usage_log.md`参照(表全文は
そちら)。要点: Trend単回委任、`measure_delegation_task.py`実測=
cumulative_usage 3,505,070/final_context_size 123,416/tool_uses 41/
turns 47/duration_seconds 1237.992。Fable通知の最終ターン値(tokens
124,254・tool_uses 46・1,238秒)とはtool_uses(41 vs 46)以外ほぼ近似
(duration 1237.992 vs 1238秒)。個別input/output/cache_read/cache_write
内訳は`measure_delegation_task.py`の現行出力に含まれず取得不能
(推定しない、詳細は同ファイル参照)。

## 9. Open Item候補

1. **OPEN-148該当のretry発生有無**: **今回のrunでは発生なし**
   (`stage1_regen_attempts=0`、`stage2_3_retry_attempts=0`、Point Overlap
   retry 0回)。よってOPEN-148(Point Overlap retryによるコスト上振れ)の
   追加事例は観測されなかった。既存Open Item自体は引き続きHIGH・意図的
   deferのまま(本タスクでは変更しない)。
2. **`aggregate_usage.py`のCATEGORY_FILE_PATTERNSがDiscovery S2の
   audit ファイル名(`stage1_writer_attempts.json`/
   `stage2_role_planning_attempt*.json`/`stage3_points_writer_attempt*.json`
   等)を未登録**のため、自動分類が`uncategorized`に落ちる(本タスクでは
   手動計算で代替、ツール本体は無改修)。Fableの判断次第でパターン表拡張が
   必要か検討要(集計ツールの改善であり仕様変更ではない想定だが、念のため
   報告)。
3. **Ledger Deviation Check(response_id非保存)**: `{tag}_ledger_deviation.json`
   保存時に`deviation_result["parsed"]`のみ保存され`response_id`が失われる
   ため、response_id自動突合による分類ができない(本タスクでは消去法で
   手動特定)。既存Production機構の出力仕様であり本タスクでは変更していない。
4. Directional Fact Precheck=DIRECTION_REVIEW_REQUIRED(advisory・
   non-blocking)は既存設計どおりの挙動であり、News記事でも同様の結果が
   観測されている(新規の問題ではない、参考情報として記録)。

## 10. Commit対象候補一覧(本タスクではGit操作を行わない)

- `docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_DISCOVERY.md`(新規)
- `docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_DISCOVERY_check.json`(新規)
- `docs/pm/transcripts/a5bdd52c4daad7ab8_recovered.jsonl`(新規、0.73MB)
- `er014_output/four_type_observation_01/claude_usage_log.md`(更新、Trend行追加)
- `er014_output/four_type_observation_01/progress_log.md`(更新、Discovery行追加)
- `er014_output/four_type_observation_01/aggregate_usage.py`(更新、
  `--stage-trace`オプション追加+`derive_retry_from_stage_trace()`新設。
  既存News/Trend出力への影響は回帰確認済み[追加キー2件のみ、既存値は無変更])
- `er014_output/four_type_observation_01/discovery/`配下一式(新規、
  `run_discovery_a2.py`、`research/*`、`a2/*`、`reader_facing_article.txt`、
  `run_result.json`、`cost_summary.json`、`raw_usage_log.jsonl`、
  `observation.json`)
- `docs/pm/RESULT_PACKET_4T_DISCOVERY.md`(本ファイル、新規)

## 11. T-0結果・事前指定外Read・STOP有無

- **T-0**: `check_delegation_prompt.py`結果=**PASS**(reasons: none)。
- **事前指定外Read(理由付き)**:
  1. `er011_discovery_generalization_wake_before_alarm_trial_12_run.py`の
     `topic_ja`関連箇所(Grep`topic_ja`のみ、4件)。理由: 事前指定Read#1の
     `run_happy_path_a2.py`が`topic_ja`をファイルから読むだけで、その値が
     実際に英語で良いか日本語必須かが同ファイル単体では判断できず、
     引数の実際の性質確認のため参照した(全文Readではなくpinpoint Grep)。
  2. `er003_discovery_focus_staged_production_01.py`の
     `run_one_pattern_staged_discovery_focus()`本体(約200行、
     driver実装に必須の関数シグネチャ・戻り値構造・保存ファイル名を
     正確に把握するため。事前指定Read一覧には同ファイルの明示的な行範囲
     指定がなかったため、Grep→該当関数全体Readで対応[D-1準拠]。
     Production/Trialコードの変更は一切行っていない、読み取りのみ)。
  3. `er014_output/four_type_observation_01/aggregate_usage.py`の
     `aggregate()`関数本体(引数化・カテゴリ判定ロジック全体、事前指定
     Grepでは関数一覧のみだったため、`--stage-trace`追加に必要な最小限の
     範囲としてRead)。
- **STOP有無**: なし(Fact Safety重大問題なし、費用¥104.25で上限¥140内、
  正式関数の実行にコード修正は不要だった)。
