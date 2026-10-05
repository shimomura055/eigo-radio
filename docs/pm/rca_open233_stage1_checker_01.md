# Stage 1 Checker 技術RCA(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_01、¥0)

Status: IN_PROGRESS(Trial管理ID、最大VALIDATED。後段`APPROVED_FOR_PRODUCTION`とは別)。ループ0/3(RCAのみ、改善・Prompt修正・設計確定は行わない)。
範囲: 既存Evidenceの整理のみ(API 0・コード変更0)。PM運営のRCAは別文書(委任_02)。表記: 【確認】=ファイル/コードで直接確認、【推測】=推論。行番号は2026-10-05時点。

## 0. 主結論(10行)

1. 純粋な非決定性は【確認】で存在する(同一prompt sha・同一入力でrun間の検出が変わる: B2_hormuz 1/2、neg5 1/2、A4 検出2/4、n=20でhormuz V4A 17/20)。ただし「それだけ」ではない。
2. 非決定性の中身は「確率的に当たり外れ」ではなく「1 callが全逸脱の一部しか列挙しない」性質(findings件数とreasoning tokensの相関r=0.74、n=32【確認・本委任で集計】)。run毎に拾う部分集合が変わる=網羅性を保証する構造がない。
3. 現Prompt/schemaは網羅を要求していない【確認】(「該当するdeviationがなければ空配列」、迷えば「ほぼ同じ意味」を最優先、MAJORは「明確にtrue」のみ)。1 callが検出+10フラグ分類+重大度+引用+related_fact_idを同時に担う。
4. 決定論層(precheck・floor)はStage 1が非検出の記事では走らない【確認: runner L8203早期return、precheckはL8263以降】。F3(Stage 1非検出時の安全網ゼロ)は構造的な穴。
5. V4Aが「良好」に見えたのは、n=1(+changed_actor n=5)の評価かつV4A差分が失敗fixtureを直接狙った設計のため(過適合の疑い【推測】)。n=20で85%は【確認】済みだったが「Self-Recovery Flowの責任範囲外/第二段階」と整理され、ブロッカー化されなかった。
6. rep30のStage 1は38 runのうちfresh 3 call(4 run)のみ。残りはfrozen 31+V0差替え3【確認】。後段検証としては有効だがStage 1/E2E KPIの根拠にはならない。
7. 「LLM単発Checkerのみ」で重大見逃し0を保証する設計は成立しない(§5)。新設計は複数独立経路+決定論補完+候補の過不足なき受渡しを論点とする。
8. 今回のfresh復元失敗は復元差(sha 26/26一致)ではなく、frozen出力が「たまたま多く列挙した単発サンプル」だったこと(B4: frozen 10件 vs fresh 3/1件)が主因【確認+推測】。
9. HF-011(B2_hormuz)は V4A 0/3(frozen1+fresh2)で、非決定性よりも系統的miss(否定・影響なし型)の疑い【推測、未確定】。V0記録は検出(n=1)。
10. 次委任: 設計案比較+Opus packet(§5・§9の論点)。残予算約¥138に対しE2E 1 run≈¥0.93なので試行回数の制約は小さい(§7)。

## 1. V4A採用の経緯と「良好に見えた」理由

| 段階 | 内容 | 母数・条件 | 出典 |
|---|---|---|---|
| gpt-6-luna比較 | Step1でer009_changed_actorをgpt-6-luna・gpt-5.6-luna(baseline)とも同時に見逃し(n=1)。その後n=5で50% vs 0% | Safety群+ER-009危険fixture 9種+A群3、新旧各1回 | DECISION_LOG L12830-12850、L12905-12925【確認】 |
| 採用候補化 | ユーザー決定「gpt-6-lunaはChecker正式採用候補として次工程へ(APPROVED_FOR_PRODUCTIONにはしない)」、Fable判定VALIDATED | 重大検出優位・新規重大見逃し0・gold一致90% vs 70% | L12913-12925【確認】 |
| V4A実装 | V0(Prompt無変更)はer009_changed_actorをn=6中3回見逃し。V4A=カテゴリ境界明確化(changed_actorとunsupported_new_claim同時true許容)。changed_actor 5/5、Safety群12/12 | n=1(12 fixture)+changed_actor n=5。fixtureは見逃しfixtureそのもの | design_open233_checker_redesign_trial_01.md L44、DECISION_LOG L13146-13160・L13436-13445【確認】 |
| Stage 1採用 | 「V0のままでは重大見逃し0を満たせない」とFableがV4AをSelf-Recovery Stage 1に採用(S1-A〜D比較) | 同上(新規評価なし) | L13436-13450【確認】 |
| Stability | n=20: hormuz_run03_standard V0 20/20・V4A 17/20(85%)、Meta V0 18/20・V4A 20/20。Fisher有意差なし | 2 fixture×2 variant×20=80 call、¥23.56 | L13216-13222【確認】 |

「良好に見えた」理由(【確認】+【推測】):
- 評価がn=1中心で、Safety 12/12は「12 fixtureを各1回」。run間変動(§4)を測っていない【確認】。
- V4Aの差分ブロックは、失敗した具体カテゴリ(changed_actor/unsupported_new_claim境界)を狙って作成され、同じfixtureで成功を確認した。未知fixtureへの汎化は検証されていない【推測=過適合の疑い】。
- 母数は「既知の重大fixture」で、Safety-critical claimの網羅(同一記事内の他の逸脱、別記事)ではない。negative群・B群はfrozen/reuse(§3)。
- 評価はStage 1単体のSafety判定(fresh API実行だが単発)。fresh Stage 1→最終出口のE2Eではない。

## 2. 既観測の見逃し(85%等)と処理経緯

| 時点 | 観測 | 構成 | 当時の処理 | 出典 |
|---|---|---|---|---|
| 2026-09-29 | er009_changed_actor V0 3/6見逃し(50%) | V0(gpt-5.6-luna)n=6 | V4A採用の動機に | design_..._trial_01.md L44【確認】 |
| 2026-09-29 | hormuz V4A 17/20(85%)、非検出3回は同一prompt sha(同一入力) | V4A gpt-6-luna n=20 | 独立Stage 2診断が3/3で補完できると確認(Stage 1非検出後の診断特例、通常設計では発火しない) | DECISION_LOG L13216-13222、L13625-13645【確認】 |
| 2026-09-29 | 設計書§11/§14に「Stage 1非検出はStage 2対象外のまま残る。Self-Recovery Flowでは解決されない既存のrecall問題、スコープ外」と明記 | - | スコープ外として明記(Opusへの別論点とする) | design_open233_self_recovery_flow_01.md L5382【確認】 |
| 2026-09-30 | 統合dry-run: V4A n=1でB2_hormuz・B3・hormuz_run02_advanced(現行Production STOP実例)が重大見逃し(Stage 1 recall miss) | 29 instance | 「Stage 1自体の検出漏れは本設計の範囲外であり未解決」と記録。S1-U(PASS時にS1-D 1 call追加)をTrial variantとして実測 | L13859-13870、L13965-13970【確認】 |
| 2026-09-30 | fresh 3 instanceをn=2で実行: 全てsample1↔sample2でfinal_state不一致。hormuz_run02_advancedはsample1でV4A+S1-U双方見逃し | n=2 | S1-U安価代替3案は採否基準未達で不採用、S1-U(high)維持 | L14040-14095【確認】 |
| 2026-10-04 | Opus#10: 「支配的リスクはStage 2ではなくStage 1のrecall」「条件付き値と代替なし通し値を分けて報告」「S1とは別の管理事項として明示的に残す」 | - | Fableは「Stage 1 recall欠落はS1と別の管理事項」として記録(L18504)。ユーザー指示「Stage 1見逃しは第二段階」(L18637)、Fable採用「Stage 1 recallは第二段階」(L19062) | opus_l2_review_..._10.md L45・L104-109【確認】 |

要点: 見逃し率は2026-09-29(n=20 85%)から継続して観測・記録されていたが、毎回「後段の設計範囲外」「第二段階」と位置づけられ、KPI(重大Fact見逃し0)の分母には反映されなかった(PM側の経緯は委任_02で扱う)。S1-Uは費用14.6%で既知見逃し2件を捕捉する効果が記録された(L14198-14205)が、その後のrep30構成の正本には含まれず、Stage 1 recall対策は未実装のまま残った【確認: runner既定`enable_s1u=False`(L8093)、rep30実行体も`enable_s1u=False`(er052_..._rep30_full_01.py L96)】。

## 3. frozen / reuse / V0差替えの導入理由

| 仕組み | 導入時の目的 | 判断主体 | 出典 |
|---|---|---|---|
| `stage1_mode="reuse"`(既存V4A出力を0 callで読む) | 「既存fixtureに同一入力のV4A出力が既にあれば再利用(0 call)、無ければ新規実行」。29 instance dry-runの費用節約と同一入力比較。runner初版(commit 5e8ff545、委任_09)から存在 | Fable(委任文「委任文どおり」とコメント。ユーザー明示指示ではない) | runner初版L35、L193-195、L623-648(`git show 5e8ff545`)【確認】 |
| `substitute_baseline_on_stage1_miss`(B2_hormuz/B3) | V4A単発がSafety既知BLOCKINGを非検出(recall miss)のとき、「Stage 2/3経路自体を検証する目的」で現行Production V0記録へ差替え。コメント: 「代替した事実は結果へ明記しStage 1 recall missとして別途報告。V4Aが検出したと偽装しない」 | Fable(委任文) | runner L7680-7686、L8192-8200【確認】 |
| iter8 cycle1 frozen(`stage1_mode=reuse`で固定) | 「Stage1自体の揺れはSelf-Recovery Flowの責任範囲外だが、出たものを人間確認なしに正しく処理できるかは責任範囲内」という整理で、後段を同一入力で再現可能にする | Fable設計判断 | design_open233_self_recovery_flow_01.md L3238-3246【確認】 |
| `deterministic_same_fact_id_location_fallback`(reuseの同箇所列挙補完) | reuse出力にsame_fact_id_locationsが無いため決定論で補う | Fable | runner L8102-8117、design L2945-2952【確認】 |

評価: 目的は「後段の検証を安定化し費用を節約する」ことで、Stage 1を測る手段ではなかった【確認】。問題はそれらの区分(fresh/frozen/V0差替え)が、後段のKPI集計・Closeoutで「E2E Safety KPI」の根拠として混同されたこと(委任_06で3 call/38 run、rep30_stage1_provenance_01.md §3【確認】)。コード側は差替えを`stage1_recall_miss_substituted=True`で記録していた【確認】が、KPI分母から除外する処理は確認できていない【run_instance L8199-8230は差替え後も通常のinstanceとして処理する点のみ確認。集計コード全体は未精査=推測】。
ユーザー決定との関係: reuse/V0差替えをユーザーが明示承認した記録は見つかっていない(本委任のGrep範囲[DECISION_LOG「V4A再利用|Stage1.*再利用|代替」等]では該当なし。全文網羅ではない)【確認(Grep範囲内)】。

## 4. fresh再現失敗の原因候補(i)〜(vii)

実測データ(fresh A構成、n=2、A4はn=4。出典 `er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01/agg_a_frozen.json`、`er052_output/open233_kpi_recovery_02_offline_01/agg_stage1_variance_impact_01.json`):

| claim | fresh検出 | frozen(rep30) | V0記録(n=1) | V4A通算 |
|---|---|---|---|---|
| B3 / B4-a / A2A3-0 / A5-0 | 各2/2 | 検出 | 検出 | 安定 |
| A4-0 | 2/4(x,o,x,o) | 検出 | 検出 | 3/5(frozen込み) |
| neg5 B3-same(HF-007) | 0/2 | 検出 | なし(V0記録がない) | 1/3 |
| B2_hormuz HF-011 | 0/2 | 0/1(V0差替え) | 検出 | 0/3 |
| B4非SC 4件(MUSE-HC-004/010等) | 0/2 | 検出(frozen 10件) | - | 1/3 |

各runの指摘件数(32 run、【確認・本委任で集計】): B4 frozen 10件 vs fresh 3/1、B1 frozen 5件 vs fresh 3/1、B2_hormuz 1/0、neg5 1/0。claim一致率の平均0.658。入力tokenは5,611〜6,462でrun間の差は小さい。findings件数とreasoning tokensの相関r=0.74。

| 候補 | 判定 | 根拠 |
|---|---|---|
| (i)純粋な非決定性 | 支持(部分的)。ただし単独では説明不足 | 同一prompt sha・同一入力で結果が変わる【確認】(A4 2/4、n=20 85%、sha 26/26一致=復元差なし)。一方でneg5/HF-011は0/2、0/3で「確率的に半々」ではなく偏り(系統性)の示唆【推測】。n=2〜4で統計的確定不可 |
| (ii)Prompt設計 | 支持(弱〜中) | 網羅要求なし、「判断に迷えば『ほぼ同じ意味』最優先」「MAJORは明確にtrueのみ」(er003 L502-548【確認】)=見逃し方向のバイアスが内在【推測】。V4A差分は境界明確化のみで網羅性の追加なし(er051 L216-230【確認】) |
| (iii)入力(長さ・構造) | 不支持〜未確定 | run間のinput tokens差が小さい【確認】。instance間差(B4/B1は列挙多、neg5は少)はあるが因果は未検証 |
| (iv)schema(1 callで全列挙、related_fact_id要求) | 支持(中) | 件数がreasoning tokensと強く連動=出力量・思考量の枠が列挙数を決める構造【確認(相関)+推測(因果)】。related_fact_id要求の負荷は未測定(未確定) |
| (v)candidate generation | 支持(中) | 候補(claim単位の抽出)をLLM自身が毎回生成。fresh-only MAJORがA4/B1/neg5で出る=候補集合がrun毎に変わる【確認】。決定論の候補列挙は存在しない |
| (vi)決定論処理の欠如 | 支持(強) | precheck/floor/兄弟列挙はStage 1非検出(ACCEPTABLE_STAGE1)で走らない(L8203-8230早期return、precheckはL8263以降)【確認】。precheck対象はactor/number/date/negation/comparisonのみで、HF-011型の意味的逸脱は対象外(precheck冒頭注記【確認】)。rep30でprecheck由来が入ったのは1 runのみ【確認】 |
| (vii)役割分担 | 支持(中) | 1 callが検出+10フラグ分類+MAJOR/MINOR+引用+関連fact特定を同時に担う【確認(schema/prompt)】。分離すれば網羅性を別経路で担保可能【推測】 |

分離結果: 「LLMは揺れる」だけでは終わらず、(1)網羅性を保証する構造がない(ii,iv,v,vii)、(2)非検出時に安全網が走らない(vi)、の設計問題が主。非決定性(i)はこの構造の上で顕在化した症状であり、設計で吸収すべき対象。

## 5. 「LLM単発Checkerのみ」設計の妥当性と、次委任の設計案比較の論点(設計は確定しない)

結論: LLM単発Checkerのみで「重大Fact見逃し0」を保証する設計は妥当でない。根拠【確認】: (a)同一入力でrun間に検出が変わる、(b)列挙数がreasoning量に依存し網羅要求がない、(c)Stage 1非検出時は後段の決定論層・Stage 2が一切走らない(L8203)。Opus#10も「決定論で0を保証することは原理的に不可能。Stage 1がLLMで取りこぼしがある」と指摘済み(opus_l2_review_..._10.md L43)。したがって目標は「0を確率的に極小化する多層構造」であり、E2Eで測る(下記§7)。

構造的要件(重大見逃し0に必要な性質):
1. 複数の独立した検出経路(LLM同士の同一promptの重複ではなく、観点・入力・方式が異なる経路)。
2. 決定論補完: LLM非検出時にも走る機械的pre-check(主体・数値・否定・比較・時期・因果は既存資産あり、意味的scope変化は対象外)。
3. 候補の過不足なき受渡し: Stage 1が拾った候補を全てStage 2へ渡し(兄弟箇所列挙含む)、Stage 2が降格しても重大カテゴリは固定BLOCKINGにできる。
4. 最終PASS前の安全確認(Stage 1非検出=PASSの場合も走る検査)。ただし過剰MAJOR・費用・Rewrite増を測る。
5. 過剰検出抑制はStage 2側(既存R2 rubric+floor)に責務を持たせ、Stage 1は「再現率優先」へ寄せる役割分担の可否。

次委任で比較すべき設計案(ユーザー§4の例、長短のみ。採用判断はしない):

| 案 | 長所 | 短所・要確認 |
|---|---|---|
| A 決定論候補抽出+LLM分類 | 候補がrun間で不変。網羅性を機械で担保。LLMは分類のみ(責務が単純) | 文/fact単位の抽出ルール設計が必要。意味的逸脱(HF-011型)の候補化方法。LLM call数(候補数)増による費用 |
| B カテゴリ別機械pre-check | 既存precheck(5種)を再利用、¥0 | 対象カテゴリが限られ、単独では意味逸脱を拾えない。非検出時にも走らせる配線が必要(現在は早期return) |
| C Stage 1複数回実行の和集合 | 実装が単純、既存資産のまま | 実測: 2回和集合でA4は検出、neg5 B3-sameとHF-011は未検出(n=2)。費用x2(¥0.357→0.714/記事)、過剰MAJOR 58→67%(実測)、「単発prompt複製」で独立性が弱い |
| D 最終PASS前の安全確認(既存S1-U/S1-D相当、Recheck強化) | 既にコードあり(stage1_union_screen)、既知見逃し2件捕捉の記録(L14198-14205) | 追加call固定費(約14.6%)、過剰BLOCK(S1-U false_positive計上あり)。Opus#10はRecheck MAJOR 3/8を提示(L108) |
| E 既存Checker+補完層(Safety系Factだけ別promptで軽量検査) | 重大カテゴリに限定=過剰検出抑制しやすい。観点が異なり独立性が高い | 新promptの設計・評価が必要。カテゴリの取りこぼし |
| F Stage 1を「列挙専用(再現率優先)」に再定義しStage 2へ全件渡す | 責務分離。Stage 2資産を活用 | Stage 2の呼び出し数・費用・誤降格が増える(Opus#10の降格リスクと一体で評価) |

論点: (1)単独案ではなく「C/D/E+A/Bの組合せ」が有力かの比較(QCD)、(2)Stage 1非検出時に決定論層を必ず走らせる配線(早期returnの扱い)、(3)負例MAJOR率(現状58%台)と重大0のトレードオフの測り方、(4)E2E測定でfresh必須(§7)、(5)Opus必須レビュー(単一方式維持の要否・構造的穴)。

## 6. 既存資産の棚卸し(Stage 1非検出時にも走らせる場合の前提条件)

| 資産 | 場所(runner = er052_open233_self_recovery_flow_runner_01.py) | 現状の動作【確認】 | 「非検出時にも走らせる」前提条件 |
|---|---|---|---|
| 決定論floor(5フラグ `FLOOR_FLAGS`=actor/number/negation/comparison/time) | L757-760 | Checkerが付けたflagがtrueのMAJOR指摘にだけ適用(Stage 2降格を阻止) | 入力はStage 1の指摘。非検出時はflag自体が無いので、決定論の候補抽出(案A/B)でflagを立てる前段が必要 |
| 因果floor `causal_floor_guard`(known6語彙+ヘッジ語) / `issue_actor_guard` | L3126-3133、L3170、L3226 | `CAUSAL_FLOOR=False`(既定OFF)。rep30のKPI構成との関係は本委任で未精査 | 既存指摘の降格阻止用。候補生成には使えない。ON/OFF構成の確認が別途必要 |
| `causal_strength`(Ledger構造化欄) | runner L3049、L3189-3207(G_L) | `TIER0_G_L_ENABLED=False`。Ledgerのcausal_strengthとChecker flagの照合 | Checker flagに依存。非検出時に使うにはLedger側のみで「記事の因果表現」を機械抽出する別ルールが必要 |
| `SAFETY_CRITICAL_CLAIM_DEFS` | L9313〜 | KPI測定用の固定gold(instance・fact_id・逐語核心句)。判定ロジックではなく**計測ラベル** | 本番には持ち込めない(gold依存)。E2E検証セットとしてのみ使用。定義・母数は変更禁止 |
| precheck(`er052_open233_self_recovery_precheck_01.py` `run_precheck`) | precheck L648、runner L7831、L8263-8317 | actor_missing/number_mismatch/date_mismatch/negation_marker/comparison_markerをLedger×記事で機械照合(¥0)。Stage 1がLEDGER_DEVIATIONのときのみ実行(ACCEPTABLE_STAGE1はL8203で早期return) | 早期returnの前でも実行する配線変更(Trial)。FP抑制(複数数値fact除外等)を現状維持。意味scope変化は対象外 |
| Ledger構造(fact_id、日本語本文、scope/numeric_value/causal_strength/notes) | `parse_ledger_text`(precheck L65) | factごとに構造化済み | 候補抽出(案A)・Safety系軽量検査(案E)の入力として再利用可能。Ledgerの質に依存 |
| `expand_same_fact_id_locations` / `deterministic_same_fact_id_location_fallback` | L1529、L1622 | 同fact_idの兄弟箇所を決定論で補う(fail-closed、逐語実在確認) | 指摘が1件でもあれば機能。非検出時は無力 |
| Stage 2 batch(R2 rubric) | L2271〜、`run_stage2` L3554 | instance単位でStage 1のMAJORだけを受け、非BLOCKING(QUALITY/ACCEPTABLE)へ降格可 | 案Fのように件数増になる場合は降格誤り・費用の再評価必須(Opus#10 S1と一体) |
| S1-U(`stage1_union_screen`) | L1828〜、`enable_s1u`既定False | Stage 1がPASSのとき追加call。rep30は`enable_s1u=False` | 既存コードはTrial用、費用約14.6%増。Production化は未決 |
| 重大誤解原則(developer message) | er051 L39-62、runner `ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT=True`(L501) | fresh Stage 1に配線。frozen reuse出力には無い(推測) | 新方式でも維持を検討(frozenと条件が異なる点に注意) |

## 7. E2E評価の設計要件(ユーザー§7〜9)と費用見込み

要件:
1. 正式KPI判定はfresh Stage 1→最終出口(Stage 2〜Recheck〜PASS/STOP/Human Review)をProduction相当で通したrunのみ。frozen/reuse/手動差替え(V0差替え含む)runはE2E分母に入れず「条件付き」と明記する。
2. 各KPIにprovenance(fresh/frozen/reuse/manual substitution/synthetic/Production formal path)を記録する(ユーザー§11 A)。
3. Safety検証セット: §8の9カテゴリ(主体取り違え・数字・否定・比較/方向・時期・因果創作・相手方取り違え・neg5 B3-same・Hormuz既知実例)を既存Safety-critical/Majorパターンで網羅。既存の対応資産: er009合成9種(changed_actor/number/negation/comparison/time/causality/certainty/scope/unsupported_new_claim)、A2A3/A4/A5/B3/B4、neg5(HF-007)、B2_hormuz(HF-011)、hormuz_run01/02(Production STOP実例)【確認: rep30 provenance §2】。gold・Safety-critical定義・母数は変更しない。
4. 測定項目(§9): 正常/負例MAJOR誤検出率、Stage 2発動率、Rewrite率、cycle数、Human Review/USER_DECISION_REQUIRED件数、平均追加費用、worst run、runtime、単発¥3超の報告。
5. fresh n数: 各instance最低n=2(A4のようにn=4も)。同一構成でrun間変動が出る前提で、Safety claimは「n回中全回検出」ではなく設計上の独立経路で担保される構造かも併せて評価する【推測】。

費用見込み(推定、委任文記載値と既存集計):
- Stage 1 fresh 1 call=約¥0.357/記事(n=32実測、agg_stage1_variance_impact_01.md (c)【確認】)。rep30平均追加費用約¥0.57(委任文記載値、本委任では再集計せず)。1 E2E run≈¥0.93。
- 残予算約¥138(委任文記載値)÷¥0.93≈148 run(理論値)。安全率20%を見て約118 run、worst run(¥3)基準で最悪約46 run。
- 目安の段階: ①¥0分析(本委任・次委任の設計比較)→②小規模Safety/normal確認(約15 instance×n=2=30 run≈¥28)→③KPI見込み確認(負例/NORMAL 7 instance×n=2=14 run≈¥13)→④広いE2E(約40〜60 run≈¥37〜56)。①〜④合計はおよそ¥80〜100で収まる見込みだが、構成変更でStage 1が複数callや追加検査を含む場合は+30〜100%(案C/D/Eにより)なので、案確定後に再見積りが必要【推測】。
- ループ上限3回の各ループで②〜③を実施すると残予算を圧迫するため、ループごとに¥0 replay(既存fresh 32 run・frozen記録で和集合・追加検査の事前評価)を先行すること。

## 8. 確認/推測の区別と本委任の限界

- 確認: 本文【確認】欄の項目(ファイル・行番号付き)。本委任で追加集計: 32 runの指摘件数×reasoning tokens相関(r=0.744)、input tokens範囲(5,611〜6,462)、run別指摘件数。
- 推測: 過適合の疑い(V4A)、非検出時の系統性(HF-011)、schema負荷・Prompt偏りの因果、費用の増減幅。
- 未精査: KPI集計コードにおける差替えrunの扱い、rep30平均費用の再集計、CAUSAL_FLOOR等のスイッチのrep30実行時の値(rep30は`CAUSAL_FLOOR=False`既定かスイッチ上書きか未確認)。
- 範囲外: 設計案の確定・Prompt修正・実装・API実行(次委任)。PM運営Failure RCAは委任_02の別文書。
