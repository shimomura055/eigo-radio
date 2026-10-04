## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_08)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: Opus批判レビュー#13(本委任文末尾に全文)に対するFableの評価(下記)に基づき、Step 7再ループ3回目の後半を実行する: actor_guard是正(AG1-strict+2条件AND補助)の実装・負例テスト・差分0確認→件数一致是正の修正→構造要素書き換えの補強→残存指標の是正→¥0集計→影響instance限定確認(rep29a、有料≈¥4)→Step 6再確認(rep29: Safety-critical群+29件、同一構成、有料≈¥20)→KPI判定(`VALIDATED`/未達ならFableへ)。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。
- 到達上限Status: Step 6のKPI判定まで。4つ同時達成→`VALIDATED`(Trial評価、Production採用ではない)。未達→`IN_PROGRESS`のままFableへ報告(ユーザーへKPI緩和を提案しない)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- Fableの評価(Opus#13の採否。SSOTへ逐語記録。変更しない):
  1. **AG1-strictを採用(修正付き)**: 「緩める」ではなく「本来のguard意図(関連factにある主体なら許容)に戻す」是正。同義語表は**細粒度の同値クラス**(employee/contractor/staff、customer/user/passenger/clientは別クラスを原則。「契約スタッフ」↔{contractor, contract worker}、「クレジットカード利用者」↔{credit-card user(s)}のように1エントリずつ根拠[Ledger逐語・辞書的対応]をコメントに書く)。英語側の照合は単語境界、日本語側は語の境界に相当する前後文字の検査(部分文字列誤ヒット[「利用者」が別語に含まれる等]を排除)。`related_fact_id`欠落・誤りはfail-closed(拒否)。guardがscope(限定・一般化)を守るものではないことを設計書と報告に明記(scopeはRecheck担保)。
  2. **2条件AND補助を採用**: 関連factに無い新主体でも、「Ledgerのどこか(他fact)に同義語表で一致」∧「Checker `issue`/`explanation`がその主体を単語境界で名指し」の両方を満たすときのみ許容(rep22型の残余)。issue単独・Ledger単独では許容しない。
  3. **負例テスト(a)〜(e)と差分0確認を必須化**: (a)近接クラスの取り違え(contractor→employee、users→customers/passengers、staff→executives)、(b)別factの主体の持ち込み(issue名指しなし)、(c)`related_fact_id`欠落・誤り、(d)日本語部分一致の誤ヒット、(e)複数新主体語の一部のみ一致→拒否。加えて全ログの**許容された**Rewrite全件に新guardを当て、許容→拒否に変わる件が0であること(差分0)。
  4. **件数一致是正の修正**: Opus指摘の3点を反映。式=「全項目の`resolved is True` ∧ {0..n-1} ⊆ 返却indexの集合」。範囲外index・非dict項目・`resolved`が`True`以外(文字列"false"等)が1つでもあればFalse。
  5. **構造要素書き換えの補強**: 構造要素を書き換えた場合、before/afterの対をRecheckへ渡す(N3′の対ブロックを**構造要素の場合に限定して**流用、追加call 0、`RECHECK_BEFORE_AFTER_PAIRS`とは独立のスイッチ`STRUCTURAL_PAIRS_TO_RECHECK`、KPI構成ON)。title判定の位置ずれをProduction記事フォーマット(`#`付きtitle・メタ行・`## In one line`の位置。`er019_output`/`er012_output`配下の実記事`article.md`/`parts.json`を3本以上サンプル)で¥0テスト。
  6. **残存指標の是正**(計測): `SAFETY_CRITICAL_CLAIM_DEFS`の`text_substring`に、因果型は「因果接続語+目印」のパターン(例: `so the flashy 20% plan`/`because`…)を使えるよう`text_pattern`(regex)を追加し、B3/neg5は`\b(so|because|therefore|as a result|led to)\b[^.]{0,40}flashy 20% plan`相当へ。旧`text_substring`も残し旧新並記。
  7. **¥0集計**: 全ログの`LEDGER_COMPLIANT∧all_prior=False` 37件の再確認最終結果(PASS以外の件数)。0件なら「取りこぼし経路なし」と記録、>0なら各件の中身を列挙。
  8. **不採用/保留**: guard廃止(不採用)、guard違反の「Recheck注記化」(保留)、AG2/AG3(不採用)、Rewrite promptでの主体指定(劣後)。
  9. **Production整合**: 件数一致式はer003 vfl01 L827と共有関数化が必要(配線時)、actor_guardはguard本体・同義語表・負例テストを一体で移す、構造要素判定はProductionフォーマットのテストを前提 — `OPEN-233-A1-PROD`へ記録。
- 禁止事項: Production正式path変更禁止(編集は`er052_open233_*`のみ。実記事ファイルはread-only)。Checker本体Prompt・Schema・判定規則・V7b不変。新しいretry loopを作らない。Human Reviewへ倒す新経路を作らない。Step 6の母数・nは固定(29 instance・38 run)、再実行・n増しなし。採否基準を結果を見て変えない。同義語表は実装前に確定しcommit(語彙確定の証跡)、差分0確認・負例テスト後に変更しない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: 上限¥32(Guardrail。内訳の目安: rep29a[`safety_er009_changed_scope`・`safety_er009_unsupported_new_claim`・`meta_run03_advanced`×n=2=6 run]≈¥4、rep29≈¥21)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥667.19、上限¥900、残¥232.81。有料実行前に費用概算を出し実測と並記。
- 即時STOP(有料run中): JA変更/例外2 instance以上/1 instance-run費用>¥7。重大見逃し・STAGE4は止めずに完走し、件数と原因を特定して報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1/T-0/T-2/T-3は委任元の定型文のとおり(本委任はTTSを伴わない)。T-0: 本ファイル保存+`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

Step 6
Safety-critical群＋既存29件を再確認。
ここで最低限、
- Human Review 0件
- 重大見逃し 0件
を同じ構成で同時に確認すること。
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。

## 作業1: Opus#13の保存とFable評価(¥0)

`docs/pm/opus_l2_review_open233_kpi_recovery_02_13.md`(依頼文要旨、Opus#13全文、Fable評価1〜9逐語、11-3の8項目照合、STOP条件非該当)。設計書`docs/pm/design_open233_kpi_recovery_02.md` §15「Opus#13後の採否と実装仕様」。

## 作業2: 同義語表の確定(先にcommit)

`ACTOR_SYNONYM_CLASSES`(runner定数): 現行25主体語を細粒度クラスに分け、各クラスに日本語表現(Ledger逐語から。全Ledgerの主体表現をGrepで棚卸しして根拠付け)と英語語形(単数/複数/ハイフン有無)を列挙。クラス分割の原則(Fable評価1)をコメントに記載。**この時点で1回目commit**(語彙確定の証跡。以後、差分0確認・負例テストの結果を見て変更しない)。

## 作業3: 実装(runner、KPI構成ON)

- 3-1 `actor_rewrite_guard_ok`の是正(AG1-strict+2条件AND): 新主体語=after−before(単語境界、クラス単位で比較)。許容条件: 各新主体語について (i)元文に同クラスがある、または(ii)関連fact(`related_fact_id`、複数可)の日本語本文に同クラスの日本語表現が語境界付きで存在、または(iii)[2条件AND]Ledgerの他factに同クラス表現が存在∧Checker `issue`/`explanation`がその英語語形を単語境界で名指し。いずれも満たさない新主体語が1つでもあれば拒否。`related_fact_id`が空・Ledgerに無い→(ii)不成立(fail-closed、(i)(iii)のみ)。記録: `actor_guard_decision`(新主体語ごとの判定根拠)。スイッチ`ACTOR_GUARD_MODE`(`legacy`既定/`ag1_strict`、KPI構成ON)。
- 3-2 件数一致是正の修正(Fable評価4)。
- 3-3 構造要素書き換えの補強(Fable評価5): `STRUCTURAL_PAIRS_TO_RECHECK`。
- 3-4 残存指標の是正(Fable評価6): `text_pattern`追加、B3/neg5を因果パターンへ、旧新並記集計。
- テスト: 負例(a)〜(e)各≥3ケース→全拒否/正例(rep28の6試行・rep22型[2条件AND])→許容/`legacy`不変/件数一致の3穴(文字列"false"・範囲外index・非dict)→False/構造要素の対がRecheck promptに入る・非構造要素では入らない/title判定のProductionフォーマット(実記事3本以上、read-only)/`text_pattern`。runner単体・er052回帰・全体回帰(基準11件以外新規なし)。
- ¥0差分確認`agg_actor_guard_diff_01.py`: 全ログの許容済みRewrite全件に新guardを適用→許容→拒否の件数(0必須。>0なら全件列挙しFableへ報告、Step 5以降へ進まない)。拒否済み7試行→許容件数。
- ¥0集計`agg_compliant_allprior_false_01.py`(Fable評価7)。

## 作業4: rep29a 影響instance限定確認(有料≈¥4)

instance=`safety_er009_changed_scope`、`safety_er009_unsupported_new_claim`、`meta_run03_advanced`、n=2、KPI構成(AG1-strict・件数一致修正・構造要素補強・N1′・因果floor known6・S1・L6・prior_issues現行本文・NORMAL群OFF・P+Q/U-2(1)・VS_MATCH_EXT・english_only・V7b・time_only)。出力`er052_output/open233_self_recovery_flow_runner_01_rep29a/`。
- 確認: STAGE4 0/見逃し0(旧新)/actor_guard判定の逐語(許容根拠)/構造要素書き換えの実LLM品質(タイトルが記事内容に沿い、Ledger不支持要素[男女差・2倍]が除去され、空・一般論でないか目視相当)/Recheck自己矛盾の有無/費用/JA 0。
- 判定: STAGE4 0∧見逃し0∧構造要素の書き換えが劣化でない→Step 6へ。問題があれば原因特定、技術是正可能なら是正→同instance再実行1回のみ。設計変更が必要ならFableへ。

## 作業5: Step 6再確認 rep29(有料≈¥21、1回)

rep28複製、KPI構成。29 instance・38 run。出力`er052_output/open233_self_recovery_flow_runner_01_rep29/`。
- 集計(rep28・rep24・iter7比): Human Review(統一定義)件数・理由/重大見逃し(旧・新定義・`text_pattern`版、`residual_at_pass`全件仮ラベル)/Safety-critical 6件の検出・経路/各機構(Tier 0・S1・L6・N1′・actor_guard判定・構造要素・件数一致)の発火/Recheck自己矛盾率と再確認call数(rep28比)/不要Rewrite/過剰Major/cycle分布/JA 0/費用(合計・平均追加/記事[rep24比・iter7比]・worst・Cap超)/モデル・構成。
- **KPI判定**: Human Review 0∧重大見逃し0∧平均追加≤+¥2∧worst追加≤+¥3 → `VALIDATED`。未達→原因分析をREPORTに書きFableへ。

## 作業6: SSOT

- `OPEN_ITEMS.md` KPI-RECOVERY-02行Status: 「委任_08: Opus#13→Fable評価、AG1-strict+2条件AND・件数一致修正・構造要素補強・残存指標是正を実装、差分0確認【x件】、rep29a【…】、rep29【Human Review d・見逃しe・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】。次: 【Closeout(委任_09)/再ループ】」。`OPEN-233-A1-PROD`行にFable評価9を追記。`docs/pm/REPORT_LEDGER.md`、REPORT §58、`docs/pm/ACTIVE_TASK.md`(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない。

## 事前指定Read一覧 / Grep一覧 / 実行コマンド

(委任文のとおり。runnerはGrepで該当範囲のみRead、全文Read禁止。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`で0件確認。)
実行: `python -m unittest er052_open233_self_recovery_flow_runner_01_test_01` / `run_project_regression.py --pattern "er052*_test_*.py"` / `run_project_regression.py` / ¥0集計 `agg_actor_guard_diff_01.py`・`agg_compliant_allprior_false_01.py` / rep29a `er052_open233_self_recovery_flow_runner_01_rep29a_affected_01.py --stage main --n 2 --budget-jpy 8` + `--stage agg` / rep29 `er052_open233_self_recovery_flow_runner_01_rep29_full_01.py --stage main --budget-jpy 24` + `--stage agg`。
順序: T-0 → 作業1 → 2(1回目commit/push) → 3(テスト・差分0・集計) → 2回目commit/push → 4 → [判定OK]5 → 6 → 3回目commit/push → 報告。

## Git

- SSOT編集権: `OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行、REPORT。
- 1回目commit: runner(同義語表のみ)、委任ログ。`OPEN-233-KPI-RECOVERY-REDESIGN-02: actor_guard用の細粒度日英同義語表を確定(評価前の証跡)(委任_08)`
- 2回目commit: Opus#13保存、設計書§15、runner、テスト、¥0集計。
- 3回目commit: rep29a/rep29スクリプトと出力、SSOT。

## 報告(RESULT_PACKET項目)

(1)結論10行以内(KPI 4つの実測値、VALIDATED/未達)、(2)同義語表の確定証跡と実装箇所・テスト・差分0結果・負例結果、(3)¥0集計(37件の再確認最終結果)、(4)rep29a結果表、(5)rep29結果表(rep28/24/iter7比、Safety-critical 6件、機構発火、自己矛盾率、費用、モデル・構成)、`residual_at_pass`全件仮ラベル、(6)未達なら原因分析と再ループ案、(7)費用、(8)SSOT、(9)T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(10)Fableへの論点。

## Opus独立レビュー#13 全文

Opus#13の全文は、`docs/pm/opus_l2_review_open233_kpi_recovery_02_13.md`に保存する(作業1)。本ログでは重複保存せず、要旨のみ記す(結論: actor_guard是正=必要・AG1-strict妥当だが同義語表の粒度がSafety上の要/構造要素delete禁止=必要・実LLM品質とtitle判定の位置ずれ未検証/件数一致是正=必要・実装に偽Trueの穴3点[`bool("false")`、範囲外index、非dict項目]、推奨式「全項目resolved is True ∧ {0..n-1}⊆返却index」/guard廃止は非推奨、Recheck注記化は保留/Production整合: 件数一致は共有関数、actor_guardはguard+同義語表+負例テスト一体、構造要素判定はProductionフォーマットテスト前提)。
