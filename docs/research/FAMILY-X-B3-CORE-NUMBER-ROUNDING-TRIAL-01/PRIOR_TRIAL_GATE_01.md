# 事前Gate(過去Trial・承認仕様調査) PRIOR_TRIAL_GATE_01

管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_01 / 調査日 2026-10-21 / 有料API 0
ユーザー原文: `docs/pm/delegation_log/2026-10-21_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_USER.md` §2

## 結論
**STOP該当の否定的検証結果: なし**(今回の方式=「選定済み中核数値について、厳密値維持か概数化かを判断しWriterへ伝える」を直接否定するREJECTED案・Fact NG・誤検知・意図しない文章変更の記録は見つからなかった)。
ただし下記「注意事項」3点はTrial設計・仕様変更案に織り込む(いずれもSTOPではなく設計制約)。

## 1. 承認済みの丸め仕様(今回の判断基準の正本。新基準は足さない)
| 仕様 | 出典 | 丸めの許容/禁止条件 |
|---|---|---|
| Spoken-first Number Treatment(DECIDED) | CURRENT_SPEC.md:1730 | Ledgerはexact保持。spoken側は精度自体に意味がない数字を丸め/概数化/方向化してよい。2軸=Importance(ANCHOR/SUPPORTING/DISPENSABLE)×Exactness(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)。スコア・日付・記録・健康研究の結果・安全閾値など精度自体が意味を持つ数字はEXACT_REQUIRED維持 |
| Listener-Friendly Numeric Precision(PRODUCTION_WIRED、Trial-18/19/20検証) | CURRENT_SPEC.md:2096、文言原本=`er011_output/no18_a2_evidence_compression_abc_precision_extension_trial_20/trial_summary.json` precision_rule_text | 意味(比較方向・storyの大きさ・閾値・解釈・値同士の区別)が変わらない場合のみ単純な概数を優先。小数の機械的削除禁止。丸めが意味ある差・閾値・小規模測定・解釈・区別を損なう場合は保持。**丸めは異なるFact・指標・group・time point・質問・実験結果の統合を許可しない(元Factへ追跡可能)** |
| NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK(2026-09-07追記) | CURRENT_SPEC.md:2096末尾 | 聞き取りやすさ優先、意味を損なわない範囲では概数が既定。精度自体が記事の意味・比較・判断に必要な場合のみ保持。レベル(A2/B1/B2)非依存 |
| 丸めはChecker側でNGにしない(ユーザー指示) | DECISION_LOG.md:14388 | 「数値丸めはChecker側の通常四捨五入判定でNG誤検出を防ぐ(B3の丸め戻しRewriteは不要Rewrite)」。実装=`er052_open233_self_recovery_precheck_01.py:231-304`(整数/小数1位/0.5刻みの四捨五入近似を許容) |
| LDC v2: 丸めはchanged_numberで誤検知されない実データ | CURRENT_SPEC.md:2096末尾(Theme2 B1=LEDGER_COMPLIANT、A2=MINOR1件[丸め無関係])、:2073(changed_number等は常時検査) | 丸め自体の誤検知なしを実データで確認済み |

## 2. ユーザー§2 確認事項1〜4への回答
1. **過去に同様の方式を検証していないか**: 「丸め判断」自体はTrial-18/19/20(A-Family Evidence Compression Editor、Writer出力後のLLM判断)で検証済みで採用済み(21節分類=**B: 判断基準は過去Trial・承認済み**)。しかし**Family X・B3出力段・中核数値マーキング後・Writerへ伝達する位置での丸め判断は過去に検証されていない**(Family Xの Fact Lock 系TrialはWriterに丸めを禁止して厳密転記させる方向のみ。DESIGN_01(c)、DESIGN_02:41)。位置・目的が違うため再検証が必要(分類=**C: 本当に新規**=この位置のみ)。
2. **丸めによるFact NG・意味変化・誤検知・意図しない文章変更**: 次の既知事例のみ。いずれも今回の方式(明示的に判断された概数のみ許可)を否定しない。
   - Trial-20(`er011_output/no18_a2_evidence_compression_abc_precision_extension_trial_20/trial_summary.json`): Pattern A/Cで99.71/108.95→about 100/about 109に概数化、fact_separation_check=possible_fact_merge_risk false。Pattern B(Numeric Necessity Test)では保持。**Fact NG・統合の発生なし**。Pattern B/Cは`DEFERRED CANDIDATE / NOT REJECTED`(CURRENT_SPEC.md:2096)。
   - Hormuz(OPEN-233、Writer非制御の丸め): HF-007「約24時間48分後」→「一日で」を軽微(C=直接証拠なし)と分類(`er052_output/open233_allfact_note_e2e_02/eval/stagewise/notes_to_error_trace.md:43,55`)。**Writerが無統制に行った丸め**であり、のちにユーザーが「数値丸めはChecker側でNG扱いしない」と決定(DECISION_LOG.md:14388)。今回は丸めを明示統制するため、この型の逸脱を減らす側。方式の否定ではない。
   - Fact Lock Trialの決定論数値照合(`er052_factlock_writer_trial_01_run.py`、DESIGN_01.md:57)は「hedge_changed(約/およそ追加削除)・not_core(丸め等)」を不一致として**測定のみ**(STOP・再生成なし)。この照合はProduction経路に移植されていない(`er053_c2_old_checker_removal_test_01.py`でFact Checker撤去、Production writer `er053_family_x_factlock_ja_writer_01.py`にcore照合Gateなし、grep確認済み)。DECISION_LOG.md:20547「周辺数値Gate化は新仕様化しない」。
3. **過去の否定的結果は今回に当てはまるか**: 当てはまるREJECTED/NG記録なし。
4. **既存正式仕様と矛盾しないか**: 下記注意事項1の1点を除き矛盾なし。

## 3. 注意事項(STOPではなく設計制約)
1. **Fact Lock Writer数字規則(5)は「丸め・『約』『およそ』の追加削除をしない」(ユーザー承認[DESIGN_01.md:26]、`er053_family_x_factlock_ja_writer_01.py:86-93`、W-1正式採用DECISION_LOG.md:20533、PRODUCTION_WIRED)**。今回の機能は規則(5)に対する狭い例外(B3が指定した概数表記のみ許可、Writer自身の丸めは引き続き禁止)になる。Writerへの追記は「【概数可】が付いた数字だけ、指定表記で書く。それ以外は従来どおり」の例外節とし、規則(5)本文は変更しない(CLAUDE.md/21節6項: 同一文面内の矛盾確認)。→Production適用時は規則(5)の例外化なので**ユーザー承認が必要な仕様変更**(Trialでは隔離)。
2. **Production検査の現状**: Family X Productionには旧Fact Checker/LDCが無い(RISK-FLAGGER-PRODUCTION-WIRING-01 C2で撤去、`er019_family_x_entertainment_production_runner_01.py` 全体にrun_deviation_check呼出なし、`er053_c2_wiring_test_01.py`でspy確認)。Production検査=Risk Flagger(事後、非Blocking、`er053_risk_flagger_production_01.py`:87-94は「範囲の広げ縮め」「数値・日付…一致を確認しきれない文」を低確信で出す設計)。→Fact Safety評価は(a)Trial専用にLDC(`er003_v1_en_direct_vfl_01_generate.run_deviation_check`、既存関数)を実行、(b)Production検査であるRF 4条件を実行し、丸めがflagされるか(advisory)を測定する。
3. **契約sha**: `er053_b3_annotation_contract_01.py`は注記md/sidecarのsha整合を検証(V3/V9)。注記ファイルを改変するとProduction契約検証が壊れる。→注記・sidecar・manifestは**無改変**とし、丸め情報は別ファイル(overlay)+Trial wrapperによるPrompt差込で伝える。

## 4. 関連OPEN(非ブロッキング)
- OPEN-126(A2/B1で数字粒度が偶然割れる、`OPEN_ITEMS.md:301`、選択肢1〜3未決): 丸めをB3判断として一元化すれば粒度のレベル間ズレを抑える方向。今回の対象外(A-Family)。
- OPEN-100(No.9 3設問survey numeric羅列): Family X無関係、今回対象外。

## 5. 判定
否定的結果なし→STOPせずS2設計へ進む(ユーザー§2「否定的結果がなければ追加承認を待たず次工程へ」)。
