# preregistration_01: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 事前登録

登録時刻: 2026-10-07 19:10 JST(委任_01作成時。18本の生成・評価は未実施。実行・評価結果を見た後に本書の基準を変更しない。変更が要る場合は実行前にFableが差し替え、版を残す)。
範囲: Trial(DEV)。Production変更なし。結果は `VALIDATED`/`NOT_SUPPORTED` 等のTrial判定にとどめ、`APPROVED_FOR_PRODUCTION` は人間ユーザーのみ。
物差し: B3 rubric(`docs/pm/b3_trial_01/eval_rubric.md`、fact単位・盲検・判定保留区分)。Rollbackは正/曖/誤の3値(`rollback_label_template.json`、META-ROLLBACK TRIAL-01/02と同一基準)。読み替え: s2_en=Checker通過後の最終EN(`plan_01.md` §2判断6)。

## 1. 比較対象と設計の事実
- 対象18本: Meta 10(variant=nb+HC-012固定最小Note)+ hormuz/space_weapons/sewer/ai_control 各2(variant=control、Noteなし)。いずれも Checker=承認スイッチ41キー不変(OPEN-238配線後)。
- 参照値: Rollback過去実績(Meta、JA R2): TRIAL-01 N=5(正1/曖4/誤0)+TRIAL-02 N=7(正2/曖5/誤0、rep9境界=曖昧扱い)=累積N=12、誤読0/12(§92-3)。B3 V0(Checkerなし、EN Checker前): 重大0/55、Gate STOP 0/12(§100-3/4)。E2E_02従来版 Control(5本、Checkerあり): 重大0/5、Checker誤許容等は§94-3/§95。
- 統計の注意: N=18/10は小標本。「0件」は安全の証明ではなく上限の提示にとどめる(Clopper-Pearson片側95%上限、実計算): 0/10=25.9%、0/22=12.7%、0/18=15.3%、1/18=23.8%、2/18=31.0%、(参考)V0 0/55=5.3%。1/18 対 0/55のFisher片側p=0.25、2/18対0/55はp=0.058。

## 2. 主要指標(合否に使う)
### ① Rollback誤読(Metaのみ)
- 定義: Meta各記事のMUSE-HC-012について3値(正/曖/誤)。**主指標①a=JA R2**(過去12本と同じ段で比較可能)。**併記①b=JA R2 / EN Checker前 / EN最終 の3箇所のうち悪い方**(rubric 4節)。分母=HC-012が選択されたMeta run(not_selectedは除外し別記。目標10。不足時の補充は実行委任時にFable判断)。
- 合格: ①a で誤読 **0/10**(累積0/22、過去12本+新10本。過去の rep9 境界は過去判定どおり曖昧扱いで固定)。上限表記: 0/10=25.9%、0/22=12.7%(片側95%)。曖昧の件数は参考記録(Note効果の有無の記述用。効果は合否に使わない)。
- 不合格(当該指標): ①a で人間確認後に誤読が1件でも確定。確定時は k/22 を報告し、Note有でも誤読が出たことを原因工程(Writer R2/Checker Rewrite等)付きで記す。
- ①bで誤読が1件でも出た場合: 合否は①aで判定し、①b件数は必ず併記して人間確認(H2/H4)へ回す(Checker Rewriteが方向を逆転した可能性を見落とさないため)。

### ② 重大NG率(18本全体、B3 rubric)
- 定義: 1記事が JA R2 または EN最終 のいずれかに重大NG(rubric 2節)を1件以上含めば「重大あり記事」。基準参照=B3 V0 0/55。
- 合格: 重大あり記事 **0/18**。1/18=**条件付き**(人間確認で重大確定なら、原因工程と同型がV0/E2E_02に無いかを記述。Fisher p=0.25のため有意な悪化とは言えないが採用は不可、追加Trial判断はFable/ユーザー)。**2/18以上=不合格**(p=0.058、上限31.0%)。
- 上限表記を必ず併記: 0/18→15.3%、1/18→23.8%(片側95%)。V0 0/55(5.3%)との比較は「Checkerあり・Meta Note混入・N=18」の別条件であり同一条件比較ではない旨を併記。

## 3. 副次指標
- ③ **Gate STOP/生成不能率**: 1回目のWriter内部Gate STOP(JA_FACT_CHECK_STOP/LEDGER_DEVIATION/Advanced deviation等)run数/18、および1回再実行後も生成不能のrun数。基準: 1回目STOP **≤2/18=懸念なし**、**3〜4/18=要注意**(Fable報告)、**≥5/18=不合格**(B3 V5の4/12=33%相当を悪化水準として参照、V0 0/12・E2E_02 P2 1/10と比較)。再実行後の生成不能が1件でもあれば別途報告。Gate回避・上限超えの独自変更はしない。
- ④ **不要Rewrite率**: 分母=Checkerが実際に書き換えた文(評価者の `checker_rewrites` 1件=1単位。run_facts.jsonのrewrite_records件数と突合)、分子=評価者が before_was_ng=false と判定した件数。記事単位(Rewriteが入った記事のうち全件が不要だった記事の割合)も併記。unclearは分子に含めず別掲。合否基準なし(記述。ただし不要率>50%は「要注意」としてFableへ報告)。
- ⑤ **Rewrite由来の新規NG件数**: `checker_rewrites` の after_new_ng(major/minor)の件数と、Checker前ENに無く最終ENで新規に生じたNG(ng_itemsのstage.s2=true かつ pre_checkerに無いもの)の件数。基準: **重大(major)新規=0を合格**、≥1は不合格(OPEN-238 Rewrite無関係文置換と同型の事故が再発したことになるため)。minorは1記事あたり件数と総数を記述(合否に使わない)。
- ⑥ **1記事原価(TTSなし)**: 全18本の phase1+EN+Checker の実費。基準: **平均≤¥13.0かつ最大≤¥25かつ総額≤¥500**(参照=TRIAL-04 Control平均¥9.28/E2E_02 P2平均¥11.04、最大¥16.74)。再実行・失敗試行分は総額に含め、平均は完了18本の1記事あたりで別掲。
- ⑦ **JAのみ残存NG件数(OPEN-239関連)**: ng_itemsのうち stage.s1=true かつ s2=false(JA最終稿にのみ残り、EN最終には無い)の件数(major/minor)。CheckerがENのみ書換えるため、JAの誤りは残る。合否基準なし(記述)。重大が含まれる場合は②の対象でもあり人間確認(H1)へ。

## 4. 総合判定規則(Trial判定。Production採用判断はしない)
- **PASS(本番経路でネガ見当たらず)**: ①合格 かつ ②=0/18 かつ ③≤2/18 かつ ⑤major=0 かつ ⑥合格。この場合も「N=18の範囲で検出されなかった」を意味し、安全の証明ではない旨を併記。
- **CONDITIONAL**: ②=1/18(人間確認で確定)、または③=3〜4/18、または④>50%等の要注意のみ。追加Trial/判断はFable→ユーザー。
- **FAIL**: ①不合格 / ②≥2 / ③≥5 / ⑤major≥1 / ⑥基準超過 のいずれか。
- 評価不能(生成不能多数・評価未完)は PASS としない(`INCOMPLETE`)。
- 目的(1)=Rollback N増し: 累積0/22の達成可否(①)と、曖昧残存数を事実として記述。目的(2)=本番経路のネガ有無: ②③④⑤⑥の記述。
- 禁止: 結果を見た後の基準・分母・「誤読」「重大」の定義変更、事後の除外(除外は定義の「not_selected」「生成不能」のみで、理由を記録)。

## 5. 評価手順(盲検)
- 記事評価: 評価者3インスタンス(A/B/C、各6記事、出所テーマ混在・seed `20261007ccp` 固定、`tools/make_eval_pack_ccp.py`)。各評価者は担当記事のみ、条件(Note有無・variant)を知らない。出力は article JSON(schema)。MAP(匿名コード→run)は全員分の評価提出後にのみ開封。
- Rollback: 評価者A/B/Cが自記事のmeta分の `rollback_labels` を記入。別インスタンス rollback_X が **Meta全10記事のlabel-only**(JA R2/EN Checker前/EN最終)を独立に判定(第2評価者)。
- 重大の第2評価: 評価者が重大(major、または pending leaning=major)とした記事は、別インスタンスが同記事のrubric評価を再実施(盲検、別評価者)して不一致を検出。

## 6. 人間確認が必要な件の定義(ユーザー確認パック=`human_review_pack_template.md`、1件1ブロック)
- (H1) 重大NGと判定された全件(評価者のmajor、pendingでleaning=major)。
- (H2) Metaの Rollback(MUSE-HC-012)判定の全件(3箇所x該当記事。not_selectedは除外)。誤読=0でも全件。
- (H3) 評価者間不一致: 評価者とrollback_Xの3値ラベル不一致、または重大の第2評価との不一致(重大の有無/severity)。
- (H4) Checker Rewrite由来の新規NG(after_new_ng=major の全件。minorは件数のみ)。
- 評価インスタンスの判定は「確認前の単独判定」と明記し、ユーザー回答後に①②⑤の確定値を更新する。人間確認は台帳該当fact・記事該当文・質問を原文のまま提示する(要約しない)。

## 7. 実行・記録の事前固定(結果で変えない)
- 18本構成・台帳sha・env・スイッチ(承認スイッチ41キー不変)・guard(累計¥480見込み/1 run ¥25/infra連続失敗3/メモリ降格4→2→1/並列4/再実行は同枠1回・全体4回)は `plan_01.md` のとおり。
- 記録項目: 各runのtransfer_block_sha256、Note到達(Metaのbrief転記)、research_calls=0、各stage費用、Checker final_state/cycle数/rewrite_records、retry/fallback/例外の有無、起動・終了時刻、承認スイッチdump。
- 本Trialで見つかった新しい仕様候補・改善案は実装せず報告する(`USER_DECISION_REQUIRED`文化を踏襲)。
