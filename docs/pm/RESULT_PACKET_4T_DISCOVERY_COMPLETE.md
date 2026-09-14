# RESULT_PACKET: EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE

## 1. 最終Status
- **A2**: `COMPLETE / canonical確定`。Fact Checker A' = **PASS**、Ledger Deviation = LEDGER_COMPLIANT(MAJOR 0)、No Jargon = 0件。
- **B1B**: `COMPLETE(本文はF002/F011とも修正済み)、ただしFact Checker A' = FAIL(未解決、本タスクの修正対象外の既存問題)`。詳細4節。
- **Key Phrase A2**: `COMPLETE`。CANONICALIZATION_PASS、Redundancy QA=REDUNDANCY_PASS、5件全QA PASS。
- **Key Phrase B1B**: `未解決`。2回試行(初回+手動再実行1回)とも`KEY_WORDS_STRUCTURE_INVALID`(詳細8節)。
- 実行全体はBudgetStopなしで完走(`overall_status=COMPLETE`、実測¥106.08+Key Phrase B1B再試行別途、予算¥170以内)。

## 2. Ledger修正(F002/F011)
限定Verification(既存`vfl01.run_verification`、web_search、対象2 Factのみ)を実行。
- **F002**: 判定=AMBIGUOUS。一次論文(Koudenburg et al. 2011, [pure.rug.nl PDF](https://pure.rug.nl/ws/portalfiles/portal/146971883/Disrupting_the_flow_How_brief_silences_in_group_conversations_affect.pdf))の条件別表は baserate n=23、flow n=18、disrupted-flow n=19(合計60)で、動画視聴者は37名・非視聴23名という区分が確認できた(=委任文の前提どおり)。ただし論文が動画編集に気づいた4名を除外したとの記述もあり、除外後の正確な内訳までは一意確定を避けるべきとの留保付き。旧scope「60 undergraduate participants; randomized across fluent, disrupted-flow, base-rate」→新scope「60名がStudy 2全体、うち37名(18+19)のみ動画視聴、23名は非視聴baseline」に修正。numeric_value/notes_for_writerも「60が動画視聴者数ではない」旨を明記する形へ修正。
- **F011**: 判定=VERIFIED。一次研究([researchgate.net](https://www.researchgate.net/publication/335405273_Increased_relaxation_and_present_orientation_after_a_period_of_silence_in_a_natural_surrounding))は当初60名中14名(不完全回答5名+追跡不能9名)除外後の分析対象46名と明記。「41名」は同研究ではなく後続の別研究(forest対seminar-room)の参加者数であることが確認された([sciencedirect.com](https://www.sciencedirect.com/science/chapter/bookseries/abs/pii/S0079612322002011))。つまり46は完全に正しく、41との不一致は別研究との取り違えだった可能性が高い。**判断**: 既にhedge付きLedger修正(「about 46、一部要約は41と報告」)を適用済みであり、内容として誤りではない(46が主表記のまま)が、この検証結果からは本来hedge不要だった可能性がある。安全側の表現のため据え置いたが、Open Item候補として記録(12節)。
- 差分全文: `er014_output/four_type_observation_01/discovery/research/ledger_fix_diff.md`。旧Ledger保存先: `research/verified_fact_ledger_v1_before_fix.txt`。

## 3. A2/B1B rewrite差分
既存経路`er010_ledger_local_rewrite_09.rewrite_ng_item`+`apply_diff_qa_to_resolved_rewrite`(修正後Ledger基準)。
- A2 F002: 「In one experiment, **60** students watched a six-minute conversation.」→「In one experiment, **37** students watched a six-minute conversation.」
- A2 F011: 「In one study, **46** students spent…」→「In one study, **about 46** students spent…」(resolved=True)
- B1B F002: 「**Sixty** students watched a six-minute conversation.」→「**Thirty-seven** students watched a six-minute conversation.」
- B1B F011: 「In one study of **46** students,…」→「In one study of **roughly 46** students,…」(resolved=True)
- **プロセス上の問題(要開示)**: F002修正2件(A2/B1B)は、内部の診断的diff QA(`apply_diff_qa_to_resolved_rewrite`)が`blocks_acceptance=True`(=不合格)、`resolved=False`、`human_review_required=True`という結果だったにもかかわらず、本タスクのdriver(`fix_fact_blocks()`)が`found`のみでフィルタし`resolved`を見ずに`apply_rewrites`へ渡してしまうバグがあり、未解決のまま記事へ適用された。これは既存の安全Gate(block単位のdiff QA)を意図せず回避した形になる。ただし**上位の独立な安全装置**である記事全体Fact Checker A'では、A2は`PASS`、B1Bも「映像を見た…比較対象は37人だった」という記述自体は`verified_claims_summary`に確認済みとして明記されており(4節参照)、F002修正の内容自体は正確と判定されている。F011(resolved=True)は正常にGateを通過。**このドライバのバグは今後修正が必要(Open Item、12節)**。

## 4. Fact Checker(A2/B1B)
- **A2**: verdict=**PASS**。Ledger Deviation=LEDGER_COMPLIANT(MAJOR 0)。Directional=DIRECTION_REVIEW_REQUIRED(既存運用どおりadvisory・non-blocking)。残指摘なし。
- **B1B**: verdict=**FAIL**。指摘内容は本タスクの修正対象(F002/F011)とは**無関係**: 「Across four studies, actively choosing solitude was associated with relaxation and lower stress」という一文が、Nguyen/Ryan/Deci論文でStudy 4のみの結果を4研究全体に一般化しているという指摘。この一般化は実は**既存Ledger F009自体の記述**(「solitude was associated with relaxation and reduced stress when participants actively chose to be alone」、条件を絞らない表現)をそのまま反映したものであり、本タスクが新たに作ったものではない。本タスクの自動retry機構は「60/Sixty」文字列一致でのみ再修正対象を検出する設計のため、この無関係な指摘には反応せず(委任文の「できないものは記録して進む」に従い)そのまま進行した。F009自体の修正は本タスクの認可範囲(F002/F011限定)外のため未実施。Ledger Deviation=LEDGER_COMPLIANT(MAJOR 0)、Directional=DIRECTION_REVIEW_REQUIRED(advisory)。

## 5. Ledger Deviation・diff QA発火・Directional
- A2/B1BともLedger Deviation Checker(hook-aware)= LEDGER_COMPLIANT、MAJOR 0件。
- diff QA(block単位): F011(A2/B1B)は正常受理(blocks_acceptance=False)。F002(A2/B1B)はblocks_acceptance=True(不合格)のまま適用された(3節のプロセス問題参照)。
- Directional Fact Precheck: A2/B1BともDIRECTION_REVIEW_REQUIRED(前回タスク・既存運用と同じくadvisory、non-blocking)。

## 6. No Jargon確認
jargon scan(前回driverの`JARGON_PATTERNS`を再利用): 本タスク開始時点でA2=0/B1B=0(前タスクで既に0達成)。Fact修正rewrite適用後もA2=0/B1B=0を維持(`jargon_scan_final.json`)。

## 7. Cross-Level Consistency
`er014_output/four_type_observation_01/discovery/cross_level_consistency.md`(決定的チェック、API呼び出しなし)。F002/F011関連の数値マーカーおよびF001/F005/F006/F007/F012を突合し、**直接的な数値矛盾は検出されず**(`Overall consistent: True`)。「60/Sixty students watched」の未修正残存、「46 students」の無ヘッジ残存はいずれも検出されなかった(=修正が両レベルへ正しく反映済み)。

## 8. Key Phrase A2/B1B
**A2**(`key_phrases/a2/`、`CANONICALIZATION_PASS`、Redundancy QA=`REDUNDANCY_PASS`、5件全項目QA全PASS):
| rank | phrase | 日本語gloss | 出典文 |
|---|---|---|---|
| 1 | lowest-arousal state | 体の興奮が最も低い状態 | "…the body's lowest-arousal state." |
| 2 | feel louder than speech | 話し声より大きく感じられる | "…it can feel louder than speech." |
| 3 | outside stimulation | 外からの刺激 | "…without outside stimulation." |
| 4 | thinking for pleasure | 楽しむために考え事をすること | "Enjoyment of thinking for pleasure…" |
| 5 | nothing to do but think | 考える以外にすることがない | "…with nothing to do but think." |

**B1B**: **未解決**。2回とも選定第1位に"have agency"(出典文「…when people have agency and a mental path to follow.」)を選び、既存選定Validatorの有限助動詞ブロックリスト(is/are/was/were/has/**have**/had/will/would/can/could/should/may/might/must)に文字列"have"が一致し`KEY_WORDS_STRUCTURE_INVALID`。実際には所有・経験を表す語彙動詞としての"have"であり助動詞ではないため、既存Validatorのfalse positiveの可能性が高い(Validator自体の修正は本タスクの認可範囲外・未承認実装のため未実施)。2回目再試行では2位候補("occupy their thoughts" vs "a mental path to follow")でRedundancy QA NGも発生し、さらにretry 1巡目の再選定でも再び"have agency"が選ばれ同じ理由で不合格。3回目以降の再試行は行わずSTOP(9節Open Item・14節STOP参照)。

## 9. actual model_id
`gpt-5.6-luna`(本タスク全呼び出し。Verification/rewrite/diff QA/Fact Checker/Ledger Deviation/Key Phrase選定・正規化・Redundancy QAすべて)。

## 10. Discovery Production 1生成セット総原価
**¥367.65**(Research/Ledger初回¥58.37 + A2初回Writer/QA¥45.88 + 前回No Jargon修正+B1B生成+partial QA¥157.32 + 本タスク¥106.08)。
- 本タスク実費内訳: `fact_fix_verification` ¥21.47(1call) / `a2_fact_fix_rewrite+ledger_check+diff_qa` 計¥12.73(8calls) / `b1b_fact_fix_rewrite+ledger_check+diff_qa` 計¥12.65(8calls) / `a2_final_fact_checker+ledger_check` 計¥24.01(2calls) / `b1b_final_fact_checker+ledger_check` 計¥26.27(2calls) / Key Phrase A2 ¥2.47(3calls) / Key Phrase B1B初回 ¥1.30(1call、structure invalidで即終了) / Key Phrase B1B再試行 ¥5.20(4calls、structure invalid+redundancy NGで即終了)。
- Key Phrase B1B未解決のため、**Key Phrase B1B分は「試行コストのみ計上、成果物なし」**。詳細: `production_set_cost.json`、`cost_summary_complete.json`、集計コマンド実測: `observation_complete.json`(`aggregate_usage.py`)= cost_jpy_total=¥367.66(丸め誤差¥0.01)、calls=70。

## 11. API token(本タスク分、Key Phrase B1B再試行4call分は別記)
本体driver: input=497,019 / output=50,289 / cached_input=51,440 / total=547,308、25 calls、¥100.88。Key Phrase B1B再試行: 4 calls、¥5.20(token内訳は`key_phrase_b1b_retry2_result.json`に別途記録なし、raw_usage_log.jsonlのタイムスタンプ末尾4行から再構成可能)。

## 12. Open Item候補
1. **driverバグ(要修正)**: `fix_fact_blocks()`が`resolved`/`human_review_required`を見ずに`apply_rewrites`へ渡しており、block単位のdiff QA Gate(F002、A2/B1B)を意図せず回避した。今回は上位の記事全体Fact Checkerが独立に内容を検証しPASS/verified扱いとなったため実害は確認されていないが、コードとして修正が必要(`applicable = [r for r in block_results if r.get("found") and r.get("resolved")]`等へ)。
2. **既存Key Phrase選定Validatorのfalse positive疑い**: 語彙動詞としての"have"(例: "have agency")を助動詞ブロックリストで一致判定し不合格としている可能性。B1Bで2回連続再現。Validator側の修正はProduction QA変更のため未承認・未実施。人間判断が必要。
3. **B1B Fact Checker FAIL(F009由来、本タスク範囲外)**: 既存Ledger F009「Across four studies, actively choosing solitude was associated with relaxation and lower stress」の一般化が、実際はStudy 4限定の結果である可能性。F002/F011以外のLedger修正が必要になるため、本タスクの認可範囲外として未着手。
4. **F011のhedge要否再検討**: 限定Verificationの結果、46は完全に正しく、41は別研究との取り違えである可能性が高いことが判明。現在の「about/roughly 46」ヘッジ表現は誤りではないが、厳密には不要かもしれない。

## 13. commit対象候補一覧(Git操作は未実施)
- `er014_output/four_type_observation_01/discovery/run_discovery_complete.py`(新規driver)
- `er014_output/four_type_observation_01/discovery/retry_key_phrase_b1b.py`(新規、Key Phrase B1B再試行)
- `er014_output/four_type_observation_01/discovery/research/verified_fact_ledger.txt`(修正版)、`verified_fact_ledger_v1_before_fix.txt`、`ledger_fix_diff.md`、`fact_fix_verification.json`
- `er014_output/four_type_observation_01/discovery/reader_facing_article.txt`、`reader_facing_article_b1b.txt`、`a2/article.md`、`b1b/article.md`
- `er014_output/four_type_observation_01/discovery/a2_before_fact_fix/`、`b1b_before_fact_fix/`(退避)
- `er014_output/four_type_observation_01/discovery/a2/audit/post_fix_fact_qa.json`(+`_before_fact_fix.json`)、`post_fix_ledger_deviation.json`、`post_fix_directional_fact_precheck.json`
- `er014_output/four_type_observation_01/discovery/b1b/audit/`(同上一式)
- `er014_output/four_type_observation_01/discovery/rewrite_log.md`(追記)、`jargon_scan_final.json`、`cross_level_consistency.md`
- `er014_output/four_type_observation_01/discovery/key_phrases/a2/`、`key_phrases/b1b/`
- `er014_output/four_type_observation_01/discovery/cost_summary_complete.json`、`production_set_cost.json`、`observation_complete.json`、`run_result_complete.json`、`key_phrase_b1b_retry2_result.json`、`raw_usage_log.jsonl`、`raw_usage_log_complete_task_only.jsonl`
- `er014_output/four_type_observation_01/progress_log.md`(1行追記)
- `docs/pm/delegation_log/EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE.md`、`..._check.json`

## 14. T-0・事前指定外Read・STOP
- T-0: PASS(`docs/pm/delegation_log/EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE_check.json`)。
- 事前指定外Read: (a) `er003_v1_en_direct_vfl_01_generate.py`の`run_verification`/`VERIFICATION_JSON_SCHEMA`/`VERIFICATION_PROMPT_TEMPLATE`定義箇所(限定Verificationの入出力構造を正確に把握するため)。(b) `er008_directional_fact_precheck_08.py`の関数シグネチャ(API呼び出し有無=費用見積りのため、grep 1回)。(c) `er014_output/four_type_observation_01/discovery/reader_facing_article.txt`・`reader_facing_article_b1b.txt`全文(F002/F011該当文の正確な文字列・前後文脈を特定してrewrite対象substringを決めるため。委任文の事前指定Readには含まれないが、rewrite実行に不可欠)。(d) `er003_v1_n3_01_scaffold_generate.py`の`run_key_phrases`全体(引数・戻り値構造の確認、委任文Grep指定の延長)。
- STOP: **なし**(全体`overall_status=COMPLETE`、予算超過なし)。ただし**未解決2件を記録して進んだ**(委任文「できないものは記録して進む」に従う): (1) B1B Fact Checker FAIL(F009由来、範囲外、4節)、(2) Key Phrase B1B未完成(有限動詞Validator誤検知疑い、8節)。加えて(3) driverバグ(F002 diff QA Gate回避、3節)を透明性のため報告。ユーザーが判断すべき選択肢: A) 現状(A2完全canonical、B1BはFact/Key Phraseとも残課題あり)で一旦区切り、F009修正・Key Phrase Validator改善は別タスクとして扱う。B) F009のLedger修正を追加タスクとして許可する。C) Key Phrase選定Validatorの"have"誤検知を修正する(Production QA変更、要承認)。D) driverの`resolved`フィルタ漏れバグの修正版で本タスクのF002修正を再実行し直す(内容は既に全体Fact Checkerで検証済みのため必須ではないが、Gate整合性のため推奨)。
