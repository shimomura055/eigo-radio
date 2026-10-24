# OPUS_REVIEW_REQUEST_01 (条件A: 新しい構造・処理フローの設計) — FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_01

依頼元: sonnet-worker(Fable経由で送付)/日付: 2026-10-25/読み取り専用レビュー。Opusは実装・Production採用可否の宣言をしない(`docs/pm/PM_GOVERNANCE.md` 11-3)。

## A. 依頼の背景(要点)
Family X『月は少しずつ縮んでいる?』(`er019_output/moon_shrinking/run_ms_01/02`)で、B3が【中核数値】を指定したのにWriterが本文に数値を入れず、記事の主題に不可欠な「月が約42〜46m縮んだ」まで脱落した。ユーザーは2026-10-25に改善Trialを承認(`docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER.md`)。ただし**(1)中核数値を全部必須にする方式は禁止、(2)必要十分な数値だけを残し、不要な数値を増やさない、(3)重要数値選定システムの重複構築は禁止**。月の記事の要件: 約42〜46mは必須、約4億年前からの推定は必要(前提・期間を正確に、継続的同速度と誤解させない)、約11cm/100万年・750m〜1.1kmは不要。Production採用はユーザーの明示承認まで不可。

## B. 読んでほしいもの(この順)
1. `docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/ROOT_CAUSE_02.md`(根本原因と実測)
2. `docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/DESIGN_01.md`(推奨方式O3と比較案O1〜O6、Trial設計、QCD)
3. `er114_output/fx_numeric_trace_01/TRACE_TABLE_01.md`・`trace_aggregate.json`(段別実測。再現: `.venv\Scripts\python.exe er114_fx_numeric_trace_01.py`、API 0円)
4. コード: `er053_family_x_factlock_ja_writer_01.py`(:64 USER_TMPL、:68-94 規則5、:265 build_r0_prompt、:321- run_w1_writer、記号QA再生成 :368-:381 / R2再実行 :428-:447)、`er053_b3_deterministic_producer_01.py`(:450 cap_of、:479-551 derive_ranks)、`er019_family_x_ja_writer_o_r1_r2_01.py`(:49-62 R0_PROMPT、:80-92 記号予防)、`er019_family_x_storyline_b3_fact_selection_01.py`(:40-95 B3 Prompt)、`er003_audio_tts_asr_safety.py`(:872-905 波ダッシュ規則)、`er095_b3_core_number_rounding_01.py`(:414 news_field_for_writer = 入力変換の前例)
5. 既存仕様: `CURRENT_SPEC.md`:915-921(ユーザー正式思想「本当に必要な数字だけ最小限」)、:2238(波ダッシュ)、:2878-(中核数値丸め)

## C. 特に独立に見てほしい論点
(a) 既存B3の役割(中核数値=上限つき許可リスト、Storyline優先)を活かせているか。新しい重要数値選定システムを実質的に作っていないか(O3のE=core∩Storylineは既存機構の再利用と言えるか、O5との線引き)。
(b) 「全部必須」になっていないか。必須集合E(≤2)の過剰掲載リスクと、Eが空/不正確なときの挙動。Storylineに数値を入れさせることで別のFailure(Storylineの不自然化、前提の誤結合、B3のFact選定が数値偏重になる)を生まないか。
(c) 数値保持と事実正確性(推定条件・期間)の両立。「約4億年前から」を継続的同速度と誤解させない担保(制約ブロック+ソフトWARN+人手/Risk Flagger)で十分か。台帳F06 notesとの整合。
(d) 決定論Gate+段限定再生成の設計妥当性: R0再生成を記号QA再生成の枠に合流(R0 call最大2回)する設計、R1/R2の再実行、STOP時の最終成果物(`ja_writer/audit/rejected_w1_r0_numeric.md`)、Human Review/STOP既存枠との整合、「本文を自動書換えしない」方針。誤判定(FP/FN)時の安全側。
(e) 量産単価増分の妥当性(DESIGN_01 §8: 追加LLM call 0、期待+0〜2円、最悪15.8円)。R0 Prompt/B3 Promptの文言追加の影響(非決定性が増えないか)。より安い/より単純な代替は無いか。
(f) 過去Trial・不採用方式の再導入が無いか(DECISION_LOG:20362 数値規則(c)中核のみ上限3件タグ付き転記可、:21990 丸め、FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01、AN3「数字を0にしない」)。
(g) 波ダッシュ矛盾(C4)の評価: 相関0/4(n小)に基づく入力正規化(「〜」→「から」)をTrialに含める判断の妥当性。承認済み規則同士の矛盾の是正として扱うか。
(h) 評価設計: 事前登録のN1〜N3、月の合格基準、Phase 2の対象3記事(ig_nobel/coffee/semiconductor)と過剰掲載の合否閾値(基準比+1/+2)は妥当か。標本n(アームあたりR0 3回)で十分か。
(i) Phase 1の費用見積(約79円、最大約91円)とPhase 2(約113円)、案件上限200円、1日1,000円内の運用。

## D. 求める出力形式
結論を「必要/不要」「推奨構造」「リスク」「代替案」の順で簡潔に。上記(a)〜(i)に番号で回答し、12観点のうち問題がある観点は明示。設計の修正案があれば具体的に(どのファイル/関数/Prompt文言か)。

## E. 12観点(固定ブロック。`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` から逐語)
---
【Opus独立技術レビューの目的】
あなたの役割は「重要な技術設計に対する独立レビュー」である。Claude/Fableの案を
追認することが目的ではない。必ず次を独立に評価すること。
- そもそもその設計が必要か
- より単純な方法がないか
- 既存処理をそのまま利用できないか
- 不要な複雑化をしていないか
- 根本原因に対する対策になっているか
- 別のFailureを生まないか

【最低限、独立してレビューする12観点】
1. そもそもこの変更・設計は必要か
2. より単純な構造にできないか
3. 既存処理・既存データを利用できないか
4. 前段で取得済みの情報を後段で失ったり再探索したりしていないか
5. 不要なLLM処理を追加していないか
6. 非決定性を増やさないか
7. Human Reviewを増やさないか
8. 不要Rewriteを増やさないか
9. コストを不必要に増やさないか
10. retry / fallback / regenerationと矛盾しないか
11. Failure時に安全側へ倒れるか(安全側=最終成果物が目的要件を満たす側。「止まる/何も変えない」が常に安全側とは限らない。2026-10-15 U4(c))
12. 個別パッチではなく再発防止になっているか

【追加観点(発火条件別)】
- 条件B(同じ問題へ2回修正しても再発): 「個別バグの連続なのか、根本設計に問題があるのか」を
  必ず明示的に判定すること。
- 条件C(Production採用候補の最終レビュー): 次の6点も必ず確認すること。
  Trial専用実装になっていないか / Production全体で矛盾しないか /
  初回・retry・fallback間で仕様が一致しているか / Dangling Referenceがないか /
  Failure時に安全側へ倒れるか / QCD上の新しい問題を生まないか。
  これはユーザーのProduction採用判断を代替するものではない(採用可否は
  人間ユーザーのみが決める。あなたは採用可否を宣言しない)。

【レビューの姿勢】
Claude/Fableの案を前提として追認しない。代替案の方が良い場合は、その代替案を
明確に提案すること。結論は「必要/不要」「推奨構造」「リスク」「代替案」の順で
簡潔に返す。
---

(条件Aのため、条件B/Cの追加観点は適用しない。)
