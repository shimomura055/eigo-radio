# Opus Context Packet: OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01 委任_03(Opus#15、条件A+条件C)

作成: 委任_03(2026-10-05、Sonnet)。雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。正本: `docs/pm/production_wiring_gap_open233_01.md`(以下「Gap文書」、§6が委任_03の追加確認)。ユーザー決定: `DECISION_LOG.md` L18785〜(2026-10-05エントリ、`### ユーザー指示全文`)。

## (a) 管理ID・性質・到達上限・禁止事項

- 管理ID: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_03)。性質: ¥0・調査と文書のみ(コード変更なし)。Gap棚卸し(委任_02)に、Checker差・モデル差・K1/K4/K8の事実確認(委任_03)を加え、Opus#15(条件A=新しい構造・処理フロー[自己修復機構のProduction化]、条件C=Production採用提案前)へ渡す。
- 到達上限Status: 対象仕様=`APPROVED_FOR_PRODUCTION`のまま。`PRODUCTION_WIRED`にしない(ユーザー完了条件1〜12が全部揃うまで)。Trial=`VALIDATED`(rep30)。
- ユーザー決定の要旨(2026-10-05): rep30の有効構成(Stage 2/materiality V7b、S1、因果floor・floor_verify[時期のみ]、位置オブジェクト・ladder・判定専用cycle・T・許可リスト4理由、AG1-strict、構造要素、B′、N1′、句読点差L0〜L6、説明文混入分離、兄弟列挙、非BLOCKING判定再利用等)を`APPROVED_FOR_PRODUCTION`。Production化は「Trial runnerだけを移植して完了としてはならない」。Trial専用`er052_*`をProductionから暗黙参照する構造は禁止。+¥3単発Capは撤回(¥3超はmonitor/report)。改善ループ最大3回、4回目以降は毎回ユーザーGate。
- 禁止(本委任): コード変更(Production・Trial)、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`PM_GOVERNANCE.md`の編集、`PRODUCTION_WIRED`宣言、OFF/REJECTED候補の混入、新規記事テーマの単独決定。費用: ¥0。
- 本packetの使い方: (a)〜(f)で診断できない場合のみ追加ファイルを読んでよい。読む前に理由と対象(ファイル・行範囲)を1行宣言し、結果の最後に追加で読んだファイル一覧と概算文字数を自己申告すること。**Opusは採用可否を宣言しない**(採用は人間ユーザーのみ)。

## (b) ユーザー指示原文(該当部分。全文は`DECISION_LOG.md` L18785〜)

````
最終rep30構成とProduction実装の1対1対応表を先に作ること。
Production Wiring必須範囲
Trial runnerだけを移植して完了としてはならない。
確認対象：
- Production正式初回Checker経路
- Rewrite経路
- Recheck
- retry
- fallback
- regeneration
- cycle上限到達時
- span取得失敗時
- API failure時
- Standard / Advanced等、Productionで対象となる全経路
Trial専用er052_*をProductionから暗黙参照する構造は禁止。
Production正式実装として整理すること。
Dangling Reference Check
今回の仕様名・原則・Safety ruleをProduction Prompt/codeへ追加する際、
- CURRENT_SPECに正式仕様があるか
- ユーザー承認済みか
- 初回Production経路にも存在するか
- retry/fallbackだけに孤立していないか
- Trial専用定義へ依存していないか
を全件確認すること。
不足があれば配線前にSSOTを整える。
Runtime evidence
静的コード変更やunit testだけではPRODUCTION_WIREDとしない。
最低限、Production正式pathで実際に発火させ、
- actual model_id
- routing
- Checker
- Stage 2/materiality
- Rewrite
- Recheck
- 必要なSafety guard
- 最終PASS/STOP
- 実費
を確認する。
すべての稀な分岐を実LLMで再現する必要はないが、主要Production flowはruntime evidence必須。稀なSafety分岐はunit/integration fixtureで補完してよい。
受入条件
Production正式pathで以下を確認する。
- Trial最終rep30の採用仕様とProduction挙動が一致
- Human Reviewを安易な出口にしていない
- 重大違反を後段1回の揺らぎで解除しない
- retry/fallback/regenerationでも仕様不整合なし
- 日本語本文を不要に変更しない
- 不要Rewriteが大幅増加しない
- Regression PASS
- integration test PASS
- runtime evidenceあり
- ProductionコードがTrial専用runnerへ依存していない
- ¥3超runがあれば報告
- 平均費用を記録
STOP条件
以下の場合はSTOPして報告。
- Trial最終構成とProduction正式経路に構造的な競合がある
- APPROVED仕様をProduction初回pathへ安全に入れられない
- retry/fallbackとの仕様矛盾
- 新しいProduct判断が必要
- Production runtimeで重大見逃し/Human Reviewが発生
- 平均費用が大きく悪化
- 既存Production品質を明確に悪化させる
- Opus/Fable改善ループが4回目へ入る必要がある
通常の実装バグ・テスト修正・SSOT整合はユーザー判断にせず自律的に解決すること。
完了条件
コードに入れただけでは完了ではない。
以下すべて完了時のみ PRODUCTION_WIRED：
1. Production正式初回path配線
2. retry/fallback/regeneration整合
3. Trial専用依存なし
4. Production runtime evidence
5. Regression / integration PASS
6. actual routing/model確認
7. CURRENT_SPEC更新
8. DECISION_LOG更新
9. OPEN_ITEMS更新/close
10. Git commit/push
11. ユーザー承認内容とProduction挙動一致
12. Dangling Referenceなし
1つでも欠ければ APPROVED_FOR_PRODUCTION のままとする。
````

## (c) Gap文書の要点(`docs/pm/production_wiring_gap_open233_01.md`、全415行)

- **§1(L21〜125)rep30有効構成の正本**: スイッチ22個(`KPI_TRIAL_SWITCHES` runner L418〜452+rep30スクリプトの上書き3個)+常時有効機構10種+rubric V7b。rep30の実績: 29 instance・38 instance-run・STAGE4 0・Human Review 0・費用総額¥21.7866(平均¥0.573/run、worst ¥4.14)。**rep30の入力はTrial fixture(合成注入を含む)でProduction正式経路の実flowではない**。rep30は`gpt-6-luna`のみで成立。
- **§2(L127〜175)Production現状**: 経路P1(Family X Advanced、`er012_e_family_entertainment_two_level_runner_01.py` L340〜432)、P2(Family X Standard、同L478〜523)、P3(`er003_discovery_focus_staged_production_01.py` `run_ledger_local_rewrite_loop`@195)、P4(`er003_v1_n3_01_articles_generate.py` L1142〜1320、P3の複製)、P5(`er012_b_family_voices_writer_generic_01.py` `run_ledger_deviation_and_local_rewrite`@1499、3つ目の複製)、P6(その他、MAJOR時挙動は要確認)。**Local Rewriteループが3箇所に複製**。現行は「Checker(`vfl01.run_deviation_check`)→MAJOR→`er010`文単位Local Rewrite(`MAX_REWRITE_ATTEMPTS=3`×`MAX_REWRITE_CYCLES=3`)→尽きたら`NG_REVIEW_REQUIRED`/STOP」。Stage 2/V7b/S1/floor/位置オブジェクト/ladder/許可リスト出口に相当する経路なし。`er052_open233_self_recovery_stage2_production_01.py`はTrial側module(名前は"production"だが`MATERIALITY_RUBRIC_V7B`@L74はrep30が使うV7b[`s2c`@L612]とは別物。誤配線の注意)。runnerは7 Trial moduleに依存(§2-7、約4,000行超)。
- **§3(L177〜222)1対1対応表の集計**: ユーザー列挙24項目(U1〜U24)。Production側実装済み0件。Gap種別: A=3(純移植可能な関数群)、B=5、C=16、D=0。
- **§4(L224〜297)推奨方針**: 案M(新規Production module+各familyは薄いアダプタ、`er052_*`/`er050`/`er051`を一切importしない、`git grep`で機械検証)を推奨、案D(各ファイルへ分散)は不一致リスク大で非推奨。部分配線は`PRODUCTION_WIRED`にしない。推奨配線順序: SSOT整備→共通基盤→Safety系(Stage 2/floor/S1/BLOCKING固定を同時に)→許可リスト+ladder→費用系→各stepでP1→P2→P3〜P5。**K1〜K13**(L250〜266)と§4-4(`blocking_structural_after_ladder`未検証経路の是正)。
- **§5(L301〜324)Fableへの論点**と、**§6(L333〜415)委任_03の追加確認**(下記(d)に要約):
  - 6-1 Checker差: Trial Stage 1 Checker = Production `vfl01`の上に「prompt+33行、developer message+15行、schema+6フィールド、post-hoc昇格ルール」を**追加のみ**で構築(削除0)。Production vfl01本体は不変。rep30のStage 1は**35/38が過去Trial出力の再利用(frozen)、新規実行は3**。Production正式経路でCheckerが新規実行された例は0。
  - 6-2 モデル: Trial=`gpt-6-luna`(ハードコード、routing非経由)、Production全経路(Checker/Rewrite/Recheck/Fact Check/Family X)=`gpt-5.6-luna`(`routing.WRITER_MODEL`)。`CURRENT_SPEC.md` L2323〜は「`gpt-6-luna`は採用候補、Routing変更は別途ユーザー判断」と明記。価格 `gpt-6-luna` $0.10/0.01/0.50、`gpt-5.6-luna` $0.20/0.02/1.20 per 1M(CURRENT_SPEC L2330〜)。
  - 6-3 K8: 不採用は`violation_spans`(`claim_in_article`置換型)。`same_fact_id_locations`は加算フィールドで委任_20 W2から採用済み。rep30有効の`STAGE2_SIBLING_LOCATIONS_CYCLE1`は決定論fallback(Checker出力非依存)。K8は競合でなく吸収可能(決定論のみの場合)。
  - 6-4 K1: Rewrite cycle最大3は両者同じ。Trialは2+条件付き1+判定専用cycle(Rewriteなし)+T。rep30の費用・Human Review 0はTrial定義で得た値。
  - 6-5 K4: P1/P2の「1回だけ全文再生成→再検査→なおMAJORなら`RuntimeError` STOP」(`er012_e` L401〜432)と、Trialのladder④(段落Rewrite)・T・許可リストの順序・存廃が未定義。
  - 6-6 K13: 「解放claimの2-of-2降格除外」はrunner `checker_major_downgraded_target`(L3326〜3337)が既に除外。読替で足りる。
  - 新規K14: Production初回CheckerはTrial V4A版でない(rep30では未検証)。

主要引用(逐語、Opusが追加探索なしで判断できるよう抜粋):

1. `er052_..._flow_runner_01.py` L278〜283: `MODEL = "gpt-6-luna"` / `MAX_CYCLES = 2` / `HARD_MAX_CYCLES = MAX_CYCLES + 1`。
2. `er010_ledger_local_rewrite_09.py` L38: `MAX_REWRITE_CYCLES = MAX_REWRITE_ATTEMPTS`(=3)。
3. `er003_v1_en_direct_vfl_01_generate.py` L57: `MODEL = routing.WRITER_MODEL  # "gpt-5.6-luna"`。
4. `er051_open233_checker_trial_variant_01.py` L239〜243: V4A = `vfl01.DEVIATION_PROMPT_TEMPLATE + TRIAL_PROMPT_DIFF_BLOCK_V01 + TRIAL_PROMPT_DIFF_BLOCK_V4A`。
5. runner L8296〜8314: `STAGE2_SIBLING_LOCATIONS_CYCLE1`は`deterministic_same_fact_id_location_fallback`+逐語実在確認で兄弟箇所を得る。
6. runner L3326〜3337: `checker_major_downgraded_target`は`floor_verify_rec.released`を降格対象から除外。
7. `er012_e_family_entertainment_two_level_runner_01.py` L401〜432(P1): MAJOR→「must-fixで1回だけ再生成」→段落数<3なら`RuntimeError`→再検査でMAJOR/prior未解消なら`RuntimeError("[STOP] ...")`。
8. 許可リスト4理由(`DECISION_LOG.md` L19018、I-2): `blocking_confirmed_unlocatable_after_cap`/`blocking_structural_after_ladder`/`post_T_new_blocking`/`api_failure`。既存の廃止出口は6種(同一claim再BLOCKING、cycle_limit_exhausted系、violation_span_unverified、target_not_locatable、ladder_exhausted_without_full_rewrite等、Opus#14指摘)。

## (d) Fableの前提と、特に判定を求める論点

**Fableの前提**: ユーザー決定のSTOP条件「Trial最終構成とProduction正式経路に構造的な競合がある」「APPROVED仕様をProduction初回pathへ安全に入れられない」「retry/fallbackとの仕様矛盾」に該当しうる候補(K1/K4/K8、Checker・モデル差)があるため、Fableは**Opus#15レビュー→Fable評価の後、Production実装に入らずユーザーへSTOP報告(`USER_DECISION_REQUIRED`候補)**する方針。Opusには「競合が本物か、設計で吸収できるか、ユーザー判断が必要か」の切り分けを求める。SSOT整備(DRC①: CURRENT_SPECへの正式仕様化)は、競合の解決方針が決まる前に書くと手戻りになるため本委任では着手しない。

**論点**(Opusは各論点に判定を付ける):

1. **K1/K4/K8・Checker差(K14)・モデル差(K7)のそれぞれが「本物の構造的競合(ユーザー判断必要)」「設計で吸収可能(自律)」「競合でない」のどれか**。Sonnet見立て(Gap文書§6-7、推測): K1=吸収可能寄り(判定専用cycleの上限扱いのみ確認候補)、K4=競合の可能性が残る、K7=要ユーザー判断の可能性高、K8=競合でない、K14=要設計+最小追加検証。批判してほしい。
2. **新module+薄いアダプタ構成(案M)と`er010`置換/併存の妥当性**。6経路(P1〜P6)・Local Rewriteループ3重複への配線で、「初回path・retry・fallback・regenerationの整合」を保つ**最も単純な構造**は何か(併存=新module側に新関数を作り`er010`は触らない案、Family Xは全文再生成を残す/廃止、等)。
3. **Production Gate(MAJOR→STOP/NG_REVIEW)からmateriality降格(V7b+S1+floor)へ替えること**のSafety(「AI1回で重大→問題なし」禁止の維持)。Safety holeはないか。
4. **許可リスト4理由への出口集約と既存6出口の対応**(P1/P2のSTOP、P3/P4の`NG_REVIEW_REQUIRED`、P5の返却、Stage 1 QA再生成との関係[K5])。
5. **Trial Checker/モデルで検証された結果がProduction Checker/モデルへ移る際の妥当性担保**: runtime evidenceで何を見れば「一致」と言えるか。差がある場合(Checker差・モデル差)の最小の追加検証(例: Production Checker×既存fixture記事で新規Stage 1とfrozen出力を比較、`gpt-5.6-luna`でStage 2/S1/Rewriteを再検証する規模)。**rep30の35/38がStage 1再利用であった事実**をどう評価するか。
6. **配線順序と部分配線の扱い**(rep30は構成全体で検証、部分配線は`PRODUCTION_WIRED`にしない)。Standard/Advanced・P1〜P5の順序。
7. **runtime evidence最小セット(既存記事+fixture、8〜10 run、¥10〜20、モデルが`gpt-5.6-luna`なら≈¥20〜40、いずれも推定)の十分性**(Gap文書§4-5、§6-2)。TTSは使わない。
8. **SSOT整備(DRC①で0件)の最小範囲**: 正式仕様化が必要な項目、`OPEN-233-A1-PROD`必須確認9項目の更新(2-of-2読替は§6-6)。
9. (追加、Sonnet判断で挿入)**Production初回経路ではStage 1再利用がない点**、`blocking_structural_after_ladder`未検証経路の是正(§4-4)、`issue_focus_absent_recheck_only`・「and」版ACCEPTABLE(Closeout未解決3点)の扱い。

### 論点と材料の対応チェック(必須)

| 論点 | 必要な材料 | 所在 | 不足時の扱い |
|---|---|---|---|
| 1 | K1/K4/K8/K14/K7の事実 | Gap文書§4-3(L250)、§6-1〜§6-5 | 不足なし(ユーザー逐語の「出力形式不採用」は未特定=要確認) |
| 2 | 経路・複製・er010依存 | Gap文書§2-1(L131)、§2-3(L150)、§4-1(L226) | Opusが追加探索可(`git grep -n "local_rewrite\.\|er010" -- 'er0*.py'`) |
| 3 | 現行Gate、V7b+S1+floorの構造 | Gap文書§1-2/§1-3、§2-2、`CURRENT_SPEC.md` OPEN-233 Closeout節 | 不足なし(Production Stage 2不在は確認済み) |
| 4 | 許可リスト・既存出口 | (c)引用8、Gap文書§4-2(L235)、`DECISION_LOG.md` L19018 | 不足なし |
| 5 | Checker差・モデル差・rep30のreuse比率 | Gap文書§6-1/§6-2 | 不足(Production Checker×Trial fixtureの実比較は未実施。再利用元fixtureのvariantは要確認) |
| 6 | 推奨配線順序 | Gap文書§4-8(L290) | 不足なし |
| 7 | runtime evidence案・費用推定 | Gap文書§4-5(L273)、§6-2 | 不足(モデル確定前の推定) |
| 8 | DRC対象一覧 | Gap文書§3、§5-4 | 不足なし |

## (e) 配線しない項目一覧(Productionへ混ぜない。正本はGap文書§1-5 L105〜123)

F1(品質regen条件変更)、確認役`STAGE2_DOWNGRADE_VERIFY`、N3′`RECHECK_BEFORE_AFTER_PAIRS`、G_L`TIER0_G_L_ENABLED`、NORMAL群2-of-2`STAGE2_NORMAL_TWO_OF_TWO`、`CAUSAL_FLOOR_VOCAB=inventory`(known6のみ)、A1主体語残存チェック、C(actor時の最小levelを③から)、E1(複数claimを1 Rewriteへ)、E2(同fact全箇所一括・Recheck結果へのenum適用。S22[cycle 1のStage 2 batchへの兄弟列挙、Rewriteへ渡さない]とは別物)、F2(MAX_CYCLES増)、A3、`CHECKER_SPANS_MODE=violation_spans`、`HANDOFF_MODE=legacy`/`JA_MODE=paired`、Trial計測専用(`CORRECT_LABEL_OVERRIDES`、`SAFETY_CRITICAL_CLAIM_DEFS`、`derive_safety_critical_from_labels`、`NORMAL_GROUP_INSTANCE_IDS`、g6/step3cmp fixture、Trial予算)。

## (f) Opusへの出力形式

結論 → 論点別判定(各論点について「競合(ユーザー判断必要)/吸収可能(自律)/非競合」、および設計案への「採用/不採用/修正採用」) → Safety hole → ユーザー判断が必要な点(あれば、選択肢と推奨) → STOP条件(ユーザー決定の8項目)に該当するかどうか(該当する/しない・根拠)。最後に、追加で読んだファイル一覧と概算文字数、十分に答えられなかった論点を自己申告すること。

## (g) 発火条件と独立レビューブロック

- 発火条件: **条件A**(自己修復機構という新しい構造・処理フローのProduction化: 新module・6経路への配線・出口の許可リスト集約)+**条件C**(重要変更のProduction採用提案前。ユーザー決定でAPPROVEDだが、Production配線は新しい配線設計を伴う)。条件B/Dは今回は非該当(個別バグの再発ではない。QCD悪化なし)。
- 重複レビューの確認: Opus#8〜#14はいずれもTrial設計(Checker後段・位置・出口)のレビューであり、**Production正式経路への配線設計・Trial Checker/モデルとProduction Checker/モデルの差・Family X全文再生成との整合は未レビュー**。再レビューではなく初回。

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
---
