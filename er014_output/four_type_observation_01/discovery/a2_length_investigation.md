# Discovery A2 長さ調査(USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY Part 2)
生成日時: 2026-09-15T00:08:46.222648+00:00

## 1. 現在のA2記事word count(正確な値)
- 公式ロジック(`er003_v1_en_direct_ab_01_generate.py::compute_word_count`、見出し[`#`行]を除外した本文のみ、`er003_v1_n3_01_articles_generate.py::compute_metrics`が内部で使うのと完全同一のロジック)で算出: **604語**
- 参考(素朴な空白区切り、見出し込み全文): 637語
- 記事生成時点(`a2/run_summary.json`、Stage 1-3完了直後、F002/F009等のLocal Rewrite適用前)の記録値: 569語(その後のLocal Rewrite[F002 operator escalation等]で本文がわずかに変化し、現在値604語との差が生じている)

## 2. 既存仕様上の根拠(soft target/hard capの有無)
### 2-1. CEFR-A2一般仕様(CURRENT_SPEC.md 541行目、ER-003-A2-SPEC-FREEZE-01、`DECIDED`)
> 全体語数 | 上限なし。**総語数を意図的に削らない**(B1と同等程度の主要情報量を保持) | 上限なし(明示的にhard limitを設けない設計) | 上限なし(記録のみ、gateなし)

この行は「全体語数に上限を設けない」ことを**意図的な設計**として明記した正式`DECIDED`仕様であり、実装漏れやバグではない。A2 Writer prompt本体(`er003_v1_n3_01_articles_generate.py`の`A2_KAI1_INSTRUCTION`)にも、総語数を積極的に削らない旨の指示が含まれる。
### 2-2. `TOTAL_SOFT_LOWER`/`TOTAL_SOFT_UPPER`(`er003_v1_n3_01_articles_generate.py` 62-63行目)
コード上には`TOTAL_SOFT_LOWER = 280`・`TOTAL_SOFT_UPPER = 420`という定数が存在し、非staged `run_one_pattern()`(同ファイル1018-1031行目、1197-1204行目の2箇所)では`length_report.json`へ`total_within_soft_range`(bool)として記録される。**ただしこれはgate/retryトリガーではなく、記録のみの診断フィールドであり、超過時にコンソール警告や完成報告への明示を行う実装は無い**(この2箇所とも、計算後に`print`されるのは`metrics`/`sections`の値のみで、`total_within_soft_range`がFalseであることを理由にした追加のprint/警告分岐は存在しない)。
### 2-3. Discovery Focus S2(staged production、本タスクのA2生成経路)の扱い
`er003_discovery_focus_staged_production_01.py::run_one_pattern_staged_discovery_focus()`は、Stage 1(Main Story)を`prod_gen.build_prompt(common_block, meta["instruction"])`(=`A2_KAI1_INSTRUCTION`、非staged経路と同一命令文、総語数の上限指示なし)で生成し、Stage 3でPoint One/Point Two各30-60語(許容25-70語、`POINT_TARGET_LOWER/UPPER`)の目標のみを課す。**Main Story本文(記事の大半を占める部分)には長さの目標が一切設定されていない。**さらに、`run_one_pattern_staged_discovery_focus()`内の最終結果構築(770-789行目)では`metrics = prod_gen.compute_metrics(article_text)`のみを呼び、非staged経路にある`length_report`(`total_within_soft_range`込み)の計算・保存(`metrics.json`/`length_report.json`書き出し)を一切行わない。実際、`discovery/a2/`ディレクトリには`metrics.json`も`length_report.json`も存在しない(`run_summary.json`にword_countのみ記録)。

## 3. なぜ600語超級が「完成」と報告できたか(原因・gap)
1. **A2の全体語数には、そもそも公式のsoft target/hard capが存在しない**(2-1、`DECIDED`かつ意図的な設計)。したがって「上限を超えた」という判定自体が既存仕様上は成立しない。
2. コード内に`TOTAL_SOFT_LOWER/UPPER`(280-420語)という診断定数は存在するが、(a)Discovery Focus S2のstaged生成経路では計算・記録すらされておらず、(b)計算される非staged経路でもrecord-onlyであり、超過時にconsole警告や完成報告への反映を行うコードが存在しない。
3. 上記2点の結果、Stage 1-3完走・Fact Checker PASS・Ledger Deviation PASS・Point Overlap QA PASSという既存の各QAが全てPASSした時点で`status="OK"`が返り、word_countはそのまま`run_summary.json`へ記録されるだけで、どのQAも「これは長い」という判定・警告を一切出さない。そのため、Fact/Ledger/Overlap各QAの観点では正当に「完成」であり、"長さ"という別軸のチェックが既存仕様に存在しないまま完成報告に至った。

## 4. 「大幅超過時にユーザーへ明示」運用の既存仕様との整合判定
**未規定。** CURRENT_SPEC.mdのA2「全体語数」行(2-1)は「上限なし」を明記するのみで、超過時(あるいは非常に長い場合)にユーザーへ明示する運用契約は記載が無い。コード側にも(2-2/2-3で確認した通り)超過検知→警告print→完成報告への反映、という経路は存在しない。したがって「目安を大幅超過した場合は完成報告時に必ずユーザーへ明示する」という運用は、**既存仕様と矛盾はしないが、既存仕様として規定されてもいない**(新規の運用ルールとして追加する場合はユーザー判断が必要、Prompt/Validator変更は本タスクの禁止事項のため未実装)。

## 5. 既存仕様内での自然な短縮可能性の判断
現在の公式word count=604語は、コード内`TOTAL_SOFT_UPPER`(420語)の約1.438倍(184語超過)。しかし、この`TOTAL_SOFT_UPPER`はDiscovery Focus S2の生成経路(Main Story Writer prompt=`A2_KAI1_INSTRUCTION`)には一切配線されておらず、Writer promptは逆に「総語数を意図的に削らない」と明記している(2-1)。すなわち、Discovery Focus S2には「既存の生成が実際に目指している/収束しやすいMain Story総語数のtarget」自体が存在しない。委任文の短縮候補生成条件(「既定のlength targetが存在し、同一Ledgerで再生成すれば目安内に収まる見込みがあるなら」)を満たす根拠が無い。既存経路を無変更のまま同一Ledgerで再実行しても、Main Story Writer promptに短縮を指示する仕組みが無いため、長さが目安内に収まる保証・見込みは無く(むしろ現状のprompt設計は非決定的な単なる再ロールに過ぎない)、これを「既存仕様内での自然な短縮」として実行するのは根拠薄弱と判断する。
**結論: 短縮候補は生成しない(STOP)。** 新しいlength仕様(Main Story本文へのsoft target配線、またはrigid hard cap)を追加すればDiscovery Focus S2でも短縮を狙えるが、これは本タスクの禁止事項(新Validator/新length仕様の追加、Prompt変更)に該当するため、本タスクでは実装しない。選択肢はユーザー判断に委ねる: (a) 現状の「A2全体語数には上限を設けない」既存`DECIDED`仕様を維持し、今回の604語はこの仕様の正常な結果として受け入れる、(b) Discovery Focus S2のMain Story Writerへも`TOTAL_SOFT_LOWER/UPPER`相当のsoft target(diagnostic、hard gateにはしない)を新規に配線するようProduction変更を正式検討する(要`APPROVED_FOR_PRODUCTION`)、(c) 完成報告の運用ルールとして「word countが目安を大幅超過した場合は完成報告時に明示する」を新たに追加する(Prompt/Validator変更を伴わない運用ルールのみの追加として、ユーザー承認があれば低リスク)。

## 6. 根拠ファイル・行番号一覧
- `CURRENT_SPEC.md` 541行目(A2全体語数=上限なし、`DECIDED`)
- `er003_v1_n3_01_articles_generate.py` 62-63行目(`TOTAL_SOFT_LOWER/UPPER`定義)、1018-1031行目・1197-1204行目(非staged経路のlength_report計算・保存、record-only)、606-615行目(`compute_metrics`)
- `er003_v1_en_direct_ab_01_generate.py` 77-80行目(`compute_word_count`公式ロジック)
- `er003_discovery_focus_staged_production_01.py` 92-94行目(`LEVELS`、A2は`A2_KAI1_INSTRUCTION`をそのまま使用)、156-165行目(Stage 1 Main Story Writer、length_report相当の計算なし)、461-462行目(Stage 3 Point One/Twoのみtargetがある)、770-789行目(`run_one_pattern_staged_discovery_focus`最終結果構築、`length_report`/`metrics.json`/`length_report.json`を生成しない)
- 実測: `er014_output/four_type_observation_01/discovery/a2/article.md`(現在の公式word_count=604)、`er014_output/four_type_observation_01/discovery/a2/run_summary.json`(生成時点word_count=569)、`discovery/a2/metrics.json`・`discovery/a2/length_report.json`は存在しない(staged経路が生成しないため)
