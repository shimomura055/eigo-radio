# Opus Context Packet: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_03(Opus#16、条件A+条件B相当)

作成: 委任_03(2026-10-05、Sonnet)。雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。正本: `docs/pm/design_open233_stage1_redesign_01.md`(以下「設計書」)、`er052_output/open233_kpi_recovery_02_offline_01/stage1_redesign_offline_eval_01.md`(以下「事前評価」)、`docs/pm/rca_open233_stage1_checker_01.md`(以下「RCA」)。

## (a) 管理ID・性質・到達上限・禁止事項・予算枠

- 管理ID: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_03、改善ループ1/3の「設計」段)。性質: ¥0、設計比較と既存データの事前評価のみ(コード変更・有料API・Prompt修正なし)。
- 到達上限Status: Trial、最大`VALIDATED`。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`と混同しない。後段のProduction wiring設計(Opus#15)とは別。
- KPI(不変): Human Review 0 / 重大Fact見逃し0 / 平均追加+¥2/記事。E2E(fresh Stage 1→最終出口)で判定。重大に甘くするのは禁止、過剰検出の抑制は可。Safety-critical定義・gold・母数は変更禁止。
- 禁止: 「LLMは揺れるから仕方ない」、Prompt文言変更のみで終わる案、Opusによる実装・Production採用可否の宣言。
- 予算枠(参考): Phase残約¥138+本管理ID追加+¥100(ユーザー決定2026-10-05)。E2E 1 run≈¥0.93(RCA §7)。
- 本packetの使い方: (a)〜(e)で診断できない場合のみ追加ファイルを読んでよい。読む前に理由と対象(ファイル・行範囲)を1行宣言し、結果の最後に追加Read一覧として列挙すること。

## (b) ユーザー指示原文(該当部分。全文は`DECISION_LOG.md` 2026-10-05エントリ)

````
4. 根本設計も検討対象
…例として、
- deterministicな候補抽出との役割分担
- 重大カテゴリごとの機械的pre-check
- 複数候補を漏れなくStage 2へ渡す構造
- Stage 1の複数回実行・和集合
- 最終PASS前の安全確認
- 既存Checkerと補完層の役割分担
等は検討対象になり得る。ただし上記をそのまま採用せよという意味ではない。
QCD・単純性・既存資産再利用・非決定性・Production運用性を比較して、最も合理的な構造を設計すること。
5. Opusレビュー
…Opusには追認させず、最低限以下を問うこと。
- 単一Checker方式を維持する必要があるか
- より単純で堅牢な方法はないか
- 重大見逃し0に対して構造的な穴がないか
- 過剰検出・Rewrite・Human Review・費用を増やしすぎないか
- deterministic / LLMの責務分担は適切か
- retry / fallback / regenerationを含めProductionで成立するか
- Stage 1だけでなくE2E KPIとして成立するか
````
§2〜§3(小修正ありき禁止、fresh E2E必須、provenance記録)、§7〜§9(E2E評価要件)は`DECISION_LOG.md`を参照(RCA §7に要件の要約あり)。

## (c) RCA要点(正本: RCA。全文は不要)

| 項目 | 内容 | 出典 |
|---|---|---|
| 非決定性と設計問題の分離 | 同一prompt sha・同一入力でrun間に検出が変わる【確認】が主因ではない。findings件数とreasoning tokensの相関r=0.74(n=32)=1 callが全逸脱の一部しか列挙しない。網羅要求なし、検出+10フラグ分類+重大度+引用+related_fact_idを1 callが担う | RCA §0,§4 |
| F3 | Stage 1非検出の記事では決定論層(precheck/floor)もStage 2も走らない(runner L8203早期return、precheckはL8263以降)【確認】 | RCA §4(vi) |
| 過適合の疑い | V4Aはn=1+changed_actor n=5、失敗fixtureを直接狙った差分で「良好」と判定。n=20で85%は第二段階扱いでブロッカー化されず【推測+確認】 | RCA §1,§2 |
| HF-011系統的miss疑い | V4A 0/3(frozen1+fresh2)、V0記録は検出(n=1)。否定・影響なし型の系統的missの疑い【推測】 | RCA §0 |
| fresh再現失敗 | A構成fresh: neg5 B3-same 0/2、HF-011 0/2、A4-0 2/4、B4非SC 4件 0/2(frozen10件 vs fresh 3/1件)。復元差ではなくfrozenが「多く列挙した単発サンプル」 | RCA §4 |
| 現状の負例MAJOR率 | A単発58.3%(7/12)、2回∪66.7%、frozen54.5% | agg_stage1_variance_impact_01.md |

## (d) 設計案比較と推奨組合せ、¥0事前評価の結果

設計書 §2〜§4が正本。要約(推測を含む):

| 案 | 要旨 | 費用/記事(円) | 判定(Fable案) |
|---|---|---|---|
| 1 V4A単発+Prompt改善 | 基準線 | 0.357 | 単独不採用 |
| 2 複数回∪ | 同Prompt複製 | 0.714(n=2) | 単独不採用(neg5/HF-011は∪でも未検出【確認】) |
| 3 決定論alignment対+LLM分類 | 文×factの対を機械列挙 | 0.73〜1.67(仮定) | alignment精度が低く不採用寄り |
| 3' 文ID強制分類 | 全文IDに判定を強制、欠落を機械検査 | 0.48〜0.62(仮定) | **採用提案(主軸)** |
| 4 カテゴリ別pre-check | 6カテゴリ機械照合 | 0 | 検出には不適。ヒント止まり |
| 5 fact単位の網羅問い合わせ | fact群ごとに対応文を列挙 | 0.57〜0.84(仮定) | 3'が不足した場合の代替/第2経路 |
| 6 PASS前の独立安全確認 | SC限定の別prompt 1 call | +0.18〜0.36(仮定) | 3'単独の結果次第で追加(ループ2想定) |
| 7' 組合せ | F3配線+3'+6 | 0.66〜0.98 | 推奨最終形。ループ1は3'+F3配線のみ |

推奨ループ1最小構成: F3配線(precheck/floorを非検出でも実行)+案3'単独。段階1(Stage 1のみfresh)15 instance×n=3=45 call≈¥22〜28、段階2(E2E)約26 run≈¥24〜31。

¥0事前評価の結果【確認: 事前評価md/json】:
- 案4模擬: Safety-critical gold文7件のうち候補に入るのは L0(カテゴリ語のみ)6/7、L1(緩いalignment+不一致)0/7、L2(厳格alignment+不一致)1/7。L0は負例/NORMAL平均26.7文中20.3文(76%)が候補で選別にならない。
- 既存`run_precheck`は24 fixture(A15+er009合成9)で候補合計1件(er009_changed_numberのみ)。
- gold文の関連factへのalignment: 緩い6/7、厳格5/7(B4-a失敗)。
- A2A3-0(主体差替え)はカテゴリ語を持たずL0でも落ちる。B3は`causal_strength=CAUSAL_STATED_BY_SOURCE`のため因果語の有無では不一致にならない。
- Stage 2費用fit(rep30、n=30): 0.099+0.073×MAJOR件数(円、r=0.78)。負例/NORMAL 1記事のStage 2費用: 現行0.107、L2候補全件投入0.722、L0全件投入1.59(外挿)。→候補は全件Stage 2へ渡さず、LLMが指摘した文のみ渡す案。
- 案2: 2回∪でneg5 B3-sameとHF-011は見逃し、A4-0は検出、負例MAJOR率58.3→66.7%【確認: RCA既出】。
限界【推測】: 案4模擬は日英約40語の小辞書で、精度は本実装の上限ではない。案3'/5/6の検出率は未測定(構造上の見込みのみ)。出力tokensは仮定。

## (e) Opusへの必須の問い

ユーザー§5の7点(追認せず独立に評価すること):
1. 単一Checker方式を維持する必要があるか。
2. より単純で堅牢な方法はないか。
3. 重大見逃し0に対して構造的な穴がないか。
4. 過剰検出・Rewrite・Human Review・費用を増やしすぎないか。
5. deterministic / LLMの責務分担は適切か。
6. retry / fallback / regenerationを含めProductionで成立するか。
7. Stage 1だけでなくE2E KPIとして成立するか。
Fable追加:
- ① neg5型(同一文が兄弟箇所に出る)・HF-011型(意味的scope変化)を構造的に拾う最も単純な方法は何か。案3'(全文ID強制)は構造的に有効か、それとも判定誤りの系統性により不十分か。
- ② 候補をStage 2へ渡す範囲(全件/LLM指摘のみ)に伴う過剰検出・費用・Human Review影響。Stage 2(V7b+S1+floor)はそれを吸収できるか(降格誤りリスク、Opus#10)。
- ③ 決定論の日英alignmentの精度リスクと、失敗時のfail-closed設計(案3'は欠落IDを再実行1回→なお欠落ならStage 2へ)が妥当か。
- ④ retry/regeneration時の再実行コスト(Recheck/再生成で全文再列挙か、変更文のみか)。
- ⑤ ループ1で最小限何を検証すればKPI見込みが立つか(E2E run数・費用)。提案: 段階1=45 call(¥22〜28)→段階2=約26 run(¥24〜31)。採用基準案は設計書 §4。
- ⑥ 後段`APPROVED_FOR_PRODUCTION`設計(Opus#15)との接続点。Stage 1が置換された場合、Production初回・retry・fallback・regenの全経路へ同一仕様を反映する必要があるか。

## (f) 出力形式(この順で返すこと)

1. 結論(必要/不要、推奨構造、リスク、代替案を簡潔に)
2. 案別判定: 案1/2/3/3'/4/5/6/7'それぞれ[採用/不採用/修正採用]と一行理由
3. Safety hole(重大見逃し0に対する構造的な穴)
4. 残る穴
5. STOP条件該当有無(`docs/pm/PM_GOVERNANCE.md` 11-3節)
6. 追加Read(読んだファイルと理由)
7. 答えられなかった点
採用可否の宣言はしない(採用は人間ユーザーのみ)。実装・修正を開始しない。

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
