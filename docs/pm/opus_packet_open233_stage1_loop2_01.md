# Opus Context Packet: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_10(Opus#17、条件A: 新しい構造・処理フローの設計)

作成: 委任_10(2026-10-05、Sonnet)。雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。正本: `docs/pm/design_open233_stage1_loop2_01.md`(以下「設計書」)、`er052_output/open233_kpi_recovery_02_offline_01/loop2_cost_structure_01.{md,json}`(以下「試算」)。

## (a) 管理ID・性質・到達上限・禁止事項・予算枠

- 管理ID: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_10、改善ループ2/3の「RCA・設計」段)。性質: ¥0、既存出力の再集計と設計のみ。到達上限Status: Trial、最大`VALIDATED`(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`と混同しない)。
- KPI(不変): Human Review 0 / 重大Fact見逃し0 / 平均追加+¥2/記事(基準点は未確定、設計書§5・論点④)。重大に甘くするのは禁止、過剰検出の抑制は可。Safety-critical定義(`SAFETY_CRITICAL_CLAIM_DEFS`のBLOCKING 6件)・gold・母数は変更禁止。HF-011は監視のみ。
- 禁止: 「LLMは揺れるから仕方ない」、Prompt文言のみの小修正で終わる案、Opusによる実装・Production採用可否の宣言。
- 予算: 枠¥238-使用¥64.20=残約¥174。限定Trial計画は設計書§6(約¥144)。
- 使い方: (a)〜(e)で診断できない場合のみ追加ファイルを読んでよい。読む前に理由と対象を1行宣言し、結果末尾に追加Read一覧を付ける。**全文読み禁止**(下記の範囲のみ)。

## (b) ユーザー指示(要旨。全文は`DECISION_LOG.md`の`STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`節をGrep)

「重大に対して甘くするのは禁止。重大でないものへの過剰検出削減は可」「Safety-criticalの定義・gold・母数を都合よく変更禁止」「『LLMは揺れるから仕方ない』で終わらせない」。改善ループは Opus→Fable評価→実装→Fable再確認→Trial(最大3回自律、`PM_GOVERNANCE.md` 11-4)。

## (c) ループ1の結果と本ループの診断(要点。詳細は設計書§0〜§3)

- 段階A(42 run fresh): SC 6/6が3/3(∪)、hold-out 9/9、欠落ID 0%。しかしNORMAL候補24.0/記事で、Stage 2外挿込みの平均追加は同一instance照合のrep30比で線形+3.0(NORMAL +4.4)。委任_09でCost KPI見込み【No】(rep24基準)。
- 費用主因【確認】: output token(reasoning含む)が約9割。reasoning 57%(r5は68%、平均7.7k tok、¥0.88/call)、可視出力33%、入力10%。r3可視出力の53%はSUPPORTED単位(1単位約179tok)。reasoning effortは全Stage 1共通`high`。
- **r3単独の見かけの18/18は偽**【確認】: A4-0のr3経路はs1/s2が決定論の否定検査(誤発火)でのみ候補化。モデル判定由来はr3 16/18・r5 17/18・∪18/18。
- 否定検査是正案a: 旧149件→9件(unique 6)。真の可能性あり(cannot型)は残る。「全行照合」案bは合成否定反転の決定論感度を失う。
- SC/hold-out候補は全て旧schemaのproxyで「fact実在+具体要素フラグ」。ただしNORMALの「迷って候補」20件のうち10件も同proxyでは具体側=flagsだけでは分離不十分。
- Stage 2は既にbatch call(候補1件¥0.064)。(C)束ねの節約は入力分の上限¥0.39/記事。

## (d) 設計案比較と推奨(設計書§4〜§6)

案: (A)2層化(CANDIDATE=fact_id+要素+記事側値+fact側値/「無い」を必須、不能=UNSURE→小batch triage、自動DISMISS禁止・全件監査ログ)、(B)否定検査是正(案a)、(C)Stage 2束ね、(D)r5廃止/縮小、(E)SUPPORTED引用省略、(G)reasoning effort引下げ(新)。推奨F=B+A+2経路維持(+Gは実験アーム)。見込み(rep30基準 NORMAL): F +3.55、F+G(未検証)+2.94、(A+B+D)+2.28【Safety不可】。基準点別: rep24基準ならNo、Production 2.77基準ならYes見込み。Human Review 0は不明(NORMAL追加BLOCKING約1.1/記事)。Trial計画: ¥0 offline→小規模fresh 33 run約¥63→(任意)G arm約¥20→E2E 16 run約¥61。

## (e) Opusへの必須の問い(追認せず独立に評価すること)

① (A)2層化はSafetyを緩めていないか。UNSURE triage(責務再配分)の妥当性、triageの独立性、DISMISS誤りの検出法、absence型(B3/B4-a/neg5)を「具体」に含める定義の妥当性、新schemaで具体化できないgold(HF-011型の意味的scope)の扱い。
② (D)r5廃止・縮小と(E)引用省略の費用削減は、Safety冗長性(2経路の独立性、3'-Rの網羅強制)を損なうか。r3単独16/18の解釈、A4-0型の救済策は別機構で可能か。
③ (B)是正案aの妥当性。残FP(only型)、真の可能性あり2件の扱い、決定論検査の役割(LLMのOKを覆す最終網)として十分か。案b/cの却下は妥当か。
④ 費用見込みの前提の穴: 候補をrep30のBLOCKING率(NORMAL 0.10/全体0.289)で外挿する妥当性、triage 1 call=¥0.26の仮定、Stage 2線形fit(候補0〜10)の外挿、KPI基準点(rep24 0.44 vs Production 2.77)、E2E 1 run総費用。
⑤ **追認させない**ため、Fable/Workerの推奨(F)とは別の案も必ず出すこと(例: Stage 1の構造を根本から変える案、経路のreasoning/出力設計の別案、r5の役割再定義、Stage 2側の吸収設計)。Fable/Workerが見落としている構造上の原因があれば追加すること。
⑥ 委任_09の「NORMAL先頭30件のラベル(推測)」(真の逸脱4/自然6/迷って候補20)の抜き取り妥当性を確認すること。`er052_output/open233_kpi_recovery_02_offline_01/stageA_candidate_composition_01.py`の`SAMPLE_LABELS`と、`er052_output/open233_stage1_stageA_01/runs/s1/`の該当候補を照合し、ラベル誤りがあれば指摘する(ラベルはgold変更ではなくStage 2負荷の推定用)。
⑦ 限定Trial計画(設計書§6)とSTOP条件(§7、特に「構造的両立不能」の判定基準)は妥当か。

## (f) 出力形式(この順で返すこと)

1. 結論(必要/不要、推奨構造、リスク、代替案を簡潔に) 2. 案別判定: (A)(B)(C)(D)(E)(G)(F)それぞれ[採用/不採用/修正採用]と一行理由+追加の別案 3. Safety hole 4. 残る穴 5. STOP条件該当有無(`docs/pm/PM_GOVERNANCE.md` 11-3節) 6. 追加Read(読んだファイルと理由) 7. 答えられなかった点。採用可否は宣言しない。実装・修正を開始しない。

## (h) 読み先(範囲限定・全文読み禁止)とGrep語

- 設計書`docs/pm/design_open233_stage1_loop2_01.md`(§0〜§8、本packetの正本。全文可)。試算`loop2_cost_structure_01.md`(全文可、約10k字)。
- Grep語(該当範囲のみRead): `er052_open233_stage1_coverage_checker_01.py` = `negation_mismatch|NEGATION_MARKERS_JA|verify_supported|quote_not_in_ledger|R3_PROMPT_TEMPLATE`。`er052_open233_stage1_stageA_01.py` = `claim_matches_def|SC_IDS|HOLDOUT_IDS`。`er052_open233_self_recovery_flow_runner_01.py` = `SAFETY_CRITICAL_CLAIM_DEFS|def run_stage2|stage2_second_judge|HOOK_ONLY_STAGE2`。`er003_v1_en_direct_vfl_01_generate.py` = `REASONING_EFFORT`(L58)。`DECISION_LOG.md` = `STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`。`docs/pm/opus_l2_review_open233_stage1_redesign_16.md`(Opus#16の条件・懸念、§1-§6のみ)。
- 段階A保存出力: `er052_output/open233_stage1_stageA_01/runs/s1|s2|s3/*.json`(`audit.per_route.r3|r5.unit_status/candidates`、`call_log`のusage)。rep30: `er052_output/open233_self_recovery_flow_runner_01_rep30/instances_s*/*.json`(`call_log`、`cycles[0].stage2_results`)。
## (g) Opus独立技術レビューの固定ブロック(`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`の`---`内を逐語貼付)

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
11. Failure時に安全側へ倒れるか
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
