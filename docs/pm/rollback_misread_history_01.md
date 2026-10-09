# Rollback誤読(MUSE-HC-012)履歴の一次資料整理(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_17、2026-10-09、API¥0、read-only調査)

凡例: 【確認】=一次資料(記事・ラベルJSON・評価シート・SSOT本文)を今回読んで確認。【推測】=資料から推した解釈(数字は書かない)。要約文書(`conditions_diff.md`等)の数字は孫引きせず、出典の評価シート/ラベルまで当たった。
対象文: ledger MUSE-HC-012「…機能を当面ロールバックしたと社内投稿で説明した」(`er019_output/meta/run_03/ledger/verified_fact_ledger.txt` L74)。誤読=「機能を取り下げた」のに「復元・復活・再提供した」方向に読める/書かれること。

## §1 結論: ユーザーの「Controlで1/5」の正体

【確認】該当する測定は **`open233_prod_e2e_02`(OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01の9/20 run、2026-10-06)の「meta 5 run」で、重大ラベルY=1/5**。
- 5 run = meta記事5本(`meta_run03_advanced`/`meta_run03_standard`/`neg1_meta_b3prod_a2`/`neg2_meta_refresh_a2`/`neg7_meta_prodrunner_b1b`)。分母5は「5テーマ」ではなく「metaの5記事」。
- 重大Y=1は `meta_run03_advanced` のEN「The company also restored the human concierge feature to the way it had been before, at least for now.」。ラベルはSonnet(W2)が一旦UNDECIDABLEとし、Fableが「重大/Y/Y(方向反転、A5-0同型)」に確定(`er052_output/open233_prod_e2e_02/labels/labels_w2_notes.md` L24-L26、`labels/labels_merged.json`該当行 `confirmed_by: fable_2026-10-06`、`report_final/critical_trace.md` L12-L14、`DECISION_LOG.md` L20019)。ユーザー本人の確認ラベルではない(Sonnet推測+Fable突合、L20019に「ユーザー未確認」)。ただしユーザー自身が同件を「今回発見した重大見逃し」と呼んでいる(`DECISION_LOG.md` L20053)。
- 同じ分母5での「復元型3/5」= advanced(restored…to the way it had been before)/standard(restored its human help feature to its earlier form)/neg2(changed the human concierge feature back to how it was before)(`docs/pm/ledger_clarity_p_trial/00c_before_evidence.md` L25-L27、要約 L30)。重大Yはこのうちadvancedのみ。neg2は`labels_merged.json`でSonnet(W3)が「問題なし/N」(同じ"back to how it was before"でも)、standardは候補にならずラベル無し。
- 「Control」という呼称の出どころ【確認】: `er052_output/open233_meta_rollback_minimal_note_01/eval/E_rollback_minimal_note_trial02.md` L74「Control参考(復元候補3/5・重大1/5)」。RB評価シートが prod_e2e_02 の5 runを「Control参考」と呼んでいる。実体は「現行Production経路のBefore記事5本」であり、後述 §2 の「Control rep1」(polysemy_trial_04)とは別物。

## §2 時系列表

列: 日付(git add日基準。記事自体の生成日は不明な場合あり) | 管理ID/Trial | Writer構成 | Checker | 対象文 | 分類 | 重大集計上の扱い | Checker検知 | 出典

| # | 日付 | 管理ID/Trial | Writer構成 | Checker | 対象文(JA/EN逐語) | 分類 | 重大集計上の扱い | Checker検知 | 出典path:行 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-28 | FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01(meta、Trial) | JA完成記事→忠実英訳(Production同等Writer以降、見出し廃止Trial) | Deviation Check(Ledger照合) | JA「元に戻しました」→EN「They also temporarily put back the feature in which humans handled the calls.」(後にgold A5-0の元文) | 意味反転(再有効化と読める)=MAJOR | MAJOR(重大扱い) | v1でMAJOR検出→must-fix retry 1回→LEDGER_COMPLIANT | `docs/pm/investigation_ledger_deviation_check_01_part_b.md` L35(A-5)、`er045_output/family_x_no_heading_segmentation_trial_01/meta/deviation_check_trial.json`(英文確認) |
| 1b | (同系列、日付は同文書参照) | family_x_b3_production_wiring_01 run_01 meta | JA Original | Checker | JA「ロールバックされます」(未来形)→Advanced/Standard英訳が継承 | 時制ドリフト(復元とは別型、MAJOR) | MAJOR | 2回ともCOMPLIANT誤判定、後に手動修正 | 同文書 L31(A-1) 【確認:表の記述。当該jsonまでは未読】 |
| 2 | 2026-09-29(commit日) | er019 run_03(Production相当、Before記事の源) | Luna R0-R2(JA)、brief=B3「当面ロールバックした」(片仮名のまま) | なし(生成時点) | JA R0 `ja_writer/original.md` L13「人間コンシェルジュ機能を当面、以前の状態に戻しました」(revision1 L15、revision2 L17も同旨)/EN b1b `article.md` L17「restored the human concierge feature to the way it had been before, at least for now」/EN a2 L17「changed the human concierge feature back to how it was before, at least for now」 | JA「以前の状態に戻しました」: 後年Sonnetが「誤読はJA R0で既に発生」と記述(`00c_before_evidence.md` L10、ユーザー未確認)。ただし同じ「戻した」系をRB評価は「曖昧」、Opusレビューは「rolled back this featureは導入前の状態へ戻す意味で、'元に戻した'を禁止すると正しい読みまで禁じる」と指摘(`docs/pm/opus_l2_review_pn_design_01.md` L47) | 当時は未集計 | なし | `er019_output/meta/run_03/{ja_writer,b1b,a2}` |
| 3 | 2026-10-06 | OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 旧9 run(`open233_prod_e2e_01/baseline_old9`、旧仕様) | er019 run_03由来を含む5 meta | 旧仕様Checker | 上記と同じ5文(advanced=restored…before、standard=restored its human help feature to its earlier form、neg2=changed…back、neg1=pulled back、neg7=put…back on hold) | 3 runで復元型出現(advanced/standard/neg2)。全て機械検出あり、ACCEPTABLE | **未ラベル(true_critical=UNLABELED)** | 機械検出→LLM/S1がACCEPTABLE | `er052_output/open233_prod_e2e_01/baseline_old9/label_sheet.csv` HC-012行(meta_run03_advanced cycle1-3等)、`00c_before_evidence.md` L30 |
| 4 | 2026-10-06 | **OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 新仕様9 run(prod_e2e_02、ユーザーの「1/5」)** | 同上のBefore記事5本(JA Luna R0-R2済みの既存記事をEN→Checker) | 新Checker(数字floorのみ+再分類) | advanced: 「The company also restored the human concierge feature to the way it had been before, at least for now.」/standard: 「…restored its human help feature to its earlier form…」/neg2: 「…changed…back to how it was before…」/neg1: 「For now, Meta has pulled back the human concierge feature.」/neg7: 「Meta then temporarily put the human-call feature back on hold.」 | advanced=重大(方向反転、A5-0同型)、neg2=問題なし(G-06曖昧型N)、neg1/neg7=忠実、standard=未ラベル | **重大Y 1/5(advancedのみ)**、復元型3/5 | advanced: 機械`negation_polarity_mismatch`で候補化→Stage 1 AI=SUPPORTED/Stage 2=ACCEPTABLE/S1第2意見=ACCEPTABLE=**見逃し**(最終 RESOLVED_STAGE2_DOWNGRADE)。standardは候補にならず | `labels_w2_notes.md` L24-26、`labels_merged.json`、`report_final/critical_trace.md` L12-14、`DECISION_LOG.md` L20019/L20021(訂正)、`00c_before_evidence.md` L25-30 |
| 5 | 2026-10-06 | OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN/TRIAL-01〜03 | 文単位テスト(記事生成なし) | 専用方向Checker案 | G-01=上記advanced文、G-02=A5-0文 | 文単位gold(重大) | 記事の重大集計とは別枠 | TRIAL-02で各3/3、TRIAL-03(構成X/Y)で退行(X1/3・Y0/3、REJECTED) | `DECISION_LOG.md` L20058-20100、`docs/pm/evidence_opus_review_03/02_hc012_a5_fp3.md` L11-12 |
| 6 | 2026-10-06 | OPEN-233-LEDGER-CLARITY-P-TRIAL-01(After n=1) | 台帳をP'に差替え(Rollbackを取り下げ表記)、Luna R0-R2 | あり(`checker_after_01`) | After記事のHC-012: 復元型0段(EN "rolled back a feature"で台帳原語維持) | 復元型0、ただし「予防成功ではなく誤訳を誘発しなかった」 | 重大0(n=1) | 記載なし | `er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01/eval/E2_critical_ng_checker.md` L4-L14、`DECISION_LOG.md` L20114 |
| 7 | 2026-10-07 | OPEN-233-POLYSEMY-NOTE-TRIAL-04 Control rep1(`open233_polysemy_trial_04/runs/meta/control/rep1`、5テーマrep1の1本) | brief→Luna R0/R1/R2、Noteなし | なし(Writer段のみ) | R0 `ja_writer/original.md`「ロールバックしました。Muse全体を停止したわけではありません。」/R1 revision1 L15「人間コンシェルジュ機能をいったん元に戻しました」/R2 revision2 L15「ロールバックしました。…元に戻されたのは、人間スタッフが電話を担当する機能です。」/EN b1b L15「they had rolled back…What was rolled back was the feature in which human staff handled the phone calls.」 | R0=忠実、R1=曖昧(復元型候補)、R2=曖昧(復元型候補・強、要Fable確認) | 3値評価(重大/軽微の区分なし)。逆転型(確定)0 | - | `er052_output/open233_polysemy_trial_04/runs/meta/eval/E_meta_control.md` L6-L18、`docs/pm/polysemy_trial_04/control_labels_summary.md` §3 |
| 8 | 2026-10-07 | OPEN-233-ALLFACT-NOTE-E2E-TRIAL-02(E2E-従来=上記Control rep1を再評価、P2 rep1/rep2) | Control rep1(上記)、P2はNote付き台帳+brief転記 | あり(41スイッチ、cycle1〜3、`RESOLVED_REWRITE_THEN_DOWNGRADE`) | 従来(Control rep1)JA R2「…ロールバックしました。Museという作品そのものを上映中止にしたわけではありません。元に戻されたのは、人間スタッフが電話を担当する機能です。」/EN上記/P2 rep1 JA R2「人間コンシェルジュ機能は当面、元の状態に戻されました。…元に戻されたのは、あくまで人間コンシェルジュの機能です」/EN「The Human Concierge feature was then returned to its original state for the time being.」/P2 rep2 EN「Meta then temporarily rolled back the human concierge feature.」 | **従来=正しい**(同記事を#7とENT(#11)は「曖昧」)、P2 rep1=正しい(「元の状態に戻す」は文脈上ロールバックと読め重大にしない)、P2 rep2=正しい | 重大=0(HC-012は誤読として数えず)。STAGEWISE §2 meta 従来版 rep1は重大0/軽微3〜4 | Checker: Control cycle2、HC-012文は変更なし | `er052_output/open233_allfact_note_e2e_02/eval/E_meta.md` L22(P2 rep1)、L51(P2 rep2)、L78(従来)、`eval/stagewise/STAGEWISE_SUMMARY.md` §2 L29-L31 |
| 9 | 2026-10-07 | OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-01 | 最小Note(brief「注意(多義):」)+Luna R0-R2、rep2〜6(N=5、rep1未完) | なし | R2: rep2「いったん元に戻された」、rep3/4「当面元に戻しました/元に戻されました」、rep5「いったん降板した形」、rep6「当面、元に戻しました」 | R2: 正解1/曖昧4/誤読0。「復活・再提供」と読める明示表現は全run全段0件 | 誤読定義=「復活・再提供」明示のみ。曖昧は重大にも軽微にも未集計(3値のみ) | - | `er052_output/open233_meta_rollback_minimal_note_01/eval/E_rollback_minimal_note.md` L7-L18 |
| 10 | 2026-10-07 | 同TRIAL-02(完了N=7、rep7,8,9,11,12,13,16) | 同上 | なし | rep9 R2「機能は当面、以前の状態に戻されました。」(R0も同文)/rep7「当面のあいだ元に戻されました」(R0は「取りやめ」=正)等 | 正しい2(rep8,13)/曖昧5(rep7,9境界,11,12,16)/重大誤読0。累積N=12=正3/曖9/誤0。**rep9は「重大誤読の境界」と評価シート自身が書き、曖昧扱いで固定** | 0/12(rep9を重大扱いなら1/12) | - | `E_rollback_minimal_note_trial02.md` L21-L25(rep9)、L70-L74(集計) |
| 11 | 2026-10-07 | OPEN-233-META-ALLFACT-NOTE-ENT-TRIAL-01(ENT-P1/P2、N=1) | nb variant | あり(P1 3cycle) | P1 JA「当面ロールバックしました。Muse全体を止めたわけではありません。」EN「Meta had temporarily rolled back…」/P2 JA「…人間が電話を担当する機能をいったん戻したのです」EN「temporarily pulled back」 | P1 JA曖昧・EN曖昧/P2 JA曖昧(復元型候補)・EN正しい寄り(境界)。参考: 同評価でControl rep1 JA R2・ENとも**曖昧**(#8は同じ記事を「正しい」) | 誤読0 | - | `er052_output/open233_meta_allfact_note_ent_01/eval/E_allfact_ent_01.md` L13-L20 |
| 12 | 2026-10-07 | OPEN-233-NOTE-TRANSFER-MATRIX-01(MX、36本、meta12本) | 固定brief+Note転記6条件、Writer R0-R2 | なし | 例 T1M0r2 JA R2「会社は機能をいったん元に戻し、当面は公開を止めます」/T0 JA「機能はいったんロールバックされました。簡単に言えば、元の状態に戻されたのです」/「人間コンシェルジュ機能をいったん元に戻しました。止めたのは…」等 | HC-012 correct 11/ambiguous 1。「元に戻しました」+「止めたのは電話機能全体ではなく…」を**correct**とした | ambiguousは軽微(scope)扱い(L38)。重大(misread)0 | - | `er052_output/open233_note_transfer_matrix_01/eval/E_meta.md` L28/L34/L38-L40/L53/L86/L100、rubric `docs/pm/note_transfer_matrix_01/eval_rubric.md` §4 |
| 13 | 2026-10-07 | OPEN-233-B3-TRIAL-01(meta17記事、Checkerなし) | B3 brief変種V0/V1356 | なし | (記事ごと) | HC-012 `direction_facts`: correct13/ambiguous4/misread0(`eval/articles/meta_*.json`をスクリプトで集計) | 重大0(rubricは#12と同系) | - | `er052_output/open233_b3_trial_01/eval/articles/meta_*.json`、rubric `docs/pm/b3_trial_01/eval_rubric.md` L22-L27 |
| 14 | 2026-10-07 | OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(CCP、meta N=10、本番経路) | 固定最小Note+Luna R0-R2 | あり(本番経路) | 例 jdmu JA R2「人間コンシェルジュ機能を当面ロールバックしました。Muse全体を止めたわけではありません。」 | JA R2 正1/曖9/誤0(評価者A/B/CとrollbackXの不一致0)。EN最終 正2/曖8/誤0。累積(#9+#10+CCP)N=22=正4/曖18/誤0。**ユーザーは10件に異議なし**(曖昧9は人間確認でも維持) | 誤読0/10(累積0/22)。曖昧9件は軽微NG(kind=scope)として別掲(`SUMMARY_CCP.md` L58-L67) | CheckerはHC-012文を変更せず(EN前→最終でラベル変化0) | `er052_output/open233_control_checker_polysemy_trial_01/eval/SUMMARY_CCP.md` L19-L30、`HUMAN_REVIEW_PACK.md` L7(3値定義)、`HUMAN_REVIEW_RESULT.md` L16 |
| 15 | 2026-10-09 | FACTLOCK-ASTRA-E2E-TRIAL-01(今回、meta new arm) | 新Writer(new_writer r0-r2)、brief【事実3】「…機能を当面ロールバックした。これは機能の試験に関する話であり、Muse全体の停止ではない」 | あり(new_check_adv/std) | JA `ja_writer/revision2.md` L15「人間コンシェルジュ機能は当面ロールバックされました」・L17「ロールバックされたのは人間コンシェルジュ機能であり、Muse全体ではありません」/EN b1b L15「The human concierge feature was then rolled back for the time being」 | `labels_merged.jsonl`にはHC-012の3値(正/曖/誤)ラベル無し。JAは「所見なし」(row w1-5)、ENのHC-012各文は「問題なし」(w1-79〜89)。**この評価軸はscope(Muse全体停止でない)で、復元方向は評価項目に含まれていない**【推測:同型の文はCCPでは曖昧】 | 該当ラベルなし | EN Checker候補は`negation_polarity_mismatch`(precheck)だが全て問題なし判定 | `er052_output/factlock_astra_e2e_trial_01/runs/meta/new/…`、`eval/labels_merged.jsonl` row w1-5/79-89。old armはJA Gate STOPで最終記事なし(`runs/meta/theme_summary.json` old_ja=stop) |

## §3 「重大0」と「誤読3/5」「重大1/5」「誤読0/12」の食い違いの説明

### 3-1 そもそも別の分母・別の「E2E_02」を指している【確認】
- 「E2E_02」は名前が衝突している。
  - (a) `open233_prod_e2e_02` = OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01の新仕様9 run。meta5本のBefore記事(`00c_before_evidence.md` L16-L30)。「復元型3/5・重大1/5」「E2E_02(旧)」はこちら。
  - (b) `open233_allfact_note_e2e_02` = OPEN-233-ALLFACT-NOTE-E2E-TRIAL-02。「E2E-従来(control) 5本」=**5テーマ×rep1**(meta/hormuz/sewer/ai_control/space_weapons各1)で、meta分は1本(#7/#8のControl rep1)のみ。`conditions_diff.md` L14「5(各テーマrep1)」、`STAGEWISE_SUMMARY.md` L3。
- (b)の「5本 重大0」には、(a)の復元型3本・重大1本は含まれない。(a)の5本はそもそも(b)の比較対象ではない。

### 3-2 評価rubricの「誤読」の定義が測定ごとに違う【確認】
| 測定 | 「誤読/重大」の定義(一次資料) | 「元に戻した」の扱い | 曖昧の扱い |
|---|---|---|---|
| prod_e2e_02(#4) | claim単位のGold/Fableラベル。「ロールバック(撤回)を復元と記述=方向反転、A5-0同型」を重大(`critical_trace.md` L14) | EN "restored…to the way it had been before"は重大Y、"changed…back to how it was before"は問題なしN(同系の語でも扱いが割れる) | claim単位で重大/軽微/問題なし |
| allfact_note_e2e_02(#8)・MX(#12)・B3(#13) | 台帳watchlist「★MUSE-HC-012 …ロールバック(**サービス全体の停止ではない**)」(`docs/pm/allfact_e2e_02/theme_fact_watchlist.md` L51)。rubric例「HC-012は『サービス全体停止』と読ませれば誤読、『人間コンシェルジュ機能の当面のロールバック』と読めれば正しい」(`note_transfer_matrix_01/eval_rubric.md` §4、`b3_trial_01/eval_rubric.md` L27)。**「復元・復活」方向は誤読の軸として定義されていない** | 「『元に戻した』等の語があるだけで重大にしない」。直後に「止めたのは機能全体でなく…」があれば correct | ambiguous=誤りとは言えないが方向が曖昧→軽微NGに対応。misread=重大NG対応 |
| polysemy_trial_04 Control評価(#7)・RB(#9/#10)・ENT(#11)・CCP(#14) | 正=機能が提供されない側が明確/曖昧=「元に戻した」「ロールバックした」のまま/誤=「機能が復活した/再提供した」と読める(`HUMAN_REVIEW_PACK.md` L7、RB評価シート冒頭) | 「元に戻した」だけで**曖昧**。前後文脈で「止めた」等が出て初めて正 | 曖昧は誤読にも重大にも数えない(3値のみ)。CCPのみ別途軽微NG(kind=scope)としても別掲 |

結果として同一Control rep1記事のHC-012が、#7では「曖昧(復元型候補・強、要Fable確認)」、#8では「正しい」、#11では「曖昧」と分類が割れている【確認:`E_meta_control.md` L11-L12、`E_meta.md` L78、`E_allfact_ent_01.md` L19】。

### 3-3 「重大0」の中でRollbackがどう扱われたか【確認】
- (b)の「E2E-従来 重大0」は、`E_meta.md`等のFact整合7区分件数に基づく。HC-012は★3分類で「正しい」とされ、重大(誤読)に数えられていない。評価者(Sonnet)は復元方向を軸に見ておらず、「Muse全体が止まっていない」ことを正しさの根拠にしている(`E_meta.md` L78、L51)。
- 「曖昧」は軽微に対応(MX L38、CCP SUMMARY L58-L63で軽微NGとして別集計)、またはそもそもNG件数に載らない(RB 3値のみ)。重大に数えた測定は、HC-012方向反転では prod_e2e_02 の advanced 1件のみ【確認】。
- RB「誤読0/12」は rubric上の誤読(復活・再提供の明示)が0というだけで、R2は正3/曖昧9。「rep9を重大扱いなら1/12」は評価シート自身が境界と書いた(`E_rollback_minimal_note_trial02.md` L21-L25)。CCP事前登録でも累積0/22の基準として「rep9は過去判定どおり曖昧扱いで固定」(`docs/pm/control_checker_polysemy_trial_01/preregistration_01.md` L15)。
- 同じ「元に戻された」系の文でも、prod_e2e_02(EN)では1件が重大、RB/CCP(JA)ではほぼ全て曖昧、MXでは文脈付きなら正しい、と三者三様。語の方向性(restoredの方が強い)・ENかJAか・直後の説明の有無が分類を分けている【推測】。

## §4 Fable直前報告の誤り箇所と訂正文

1. 誤り: 「E2E-従来(control) 5本 重大0」を、**Rollback誤読の過去実績としてそのまま引用**した(`conditions_diff.md` §3-4 L73、`preregistration_01.md` L9も同じ並べ方)。
   - 訂正: この「5本」は5テーマ×rep1で、meta分は1本(Control rep1)のみ。Rollback誤読を測る母集団ではない。Rollback誤読の過去実績の分母は、prod_e2e_02のmeta5本(復元型3/5・重大Y 1/5)とRB/ENT/MX/CCP(誤読0/22だが曖昧18/22)で、互いに定義が異なる。
2. 誤り: 「重大0」をRollback誤読が起きていない根拠として扱った。
   - 訂正: 「重大0」の評価rubric(allfact_e2e_02/MX/B3)は復元・復活方向を誤読の軸にしていない。重大Y(復元型)は prod_e2e_02 advanced の1件が別系統のgoldラベル(Fable確定)で残っている。
3. 誤り(要確認): `b3_brief_structure_hypothesis_01.md` L25 meta列「1/5, 1/6」をRollback誤読と並べて扱った可能性。
   - 訂正【確認】: 「1/5, 1/6」は STAGEWISE_SUMMARY §2 L31(meta P2 rep2)の①JA 重大1/軽微5・②EN 重大1/軽微6で、重大1件は開示対象の取り違え(meta-p2r2-02)でありRollback誤読ではない。
4. 誤り: 「復元型誤読3/5」を重大3/5のように読めるまとめ方は不正確(逆に「誤読3/5」を重大0と相殺するのも不正確)。
   - 訂正: 3/5は「復元型表現が出た run 数」、うち重大ラベルYは1(advanced)。残りは standard=未ラベル、neg2=問題なし(N)。
5. 補足: `conditions_diff.md` L38 RB行の「誤読0/12(rep9を重大扱いなら1/12)」は一次資料と一致。Rollback累積0/22も一致。ただし同行は「曖昧9/12」を重大/軽微のどちらにも落としていない点が結論に効く。

## §5 未確認・データ欠落

- advanced/neg1/neg7の最終記事全文は保存されていない(`00c_before_evidence.md` L50の注記)。standard/neg2は最終記事の一部のみ。JA R0-R2側の「戻した」記述は er019 run_03 のみ直接確認。neg1/neg2/neg7のJA R0-R2は今回未読。
- prod_e2e_02 advanced の重大ラベルはユーザー確認なし(Sonnet推測+Fable突合)。ユーザーが「重大見逃し」と呼んだ事実(`DECISION_LOG.md` L20053)はあるが、ラベルJSON自体への人手確認記録は見つけていない。
- 旧9 run(prod_e2e_01 baseline_old9)の復元型3 runはACCEPTABLE判定で未ラベル(`label_sheet.csv`)。
- polysemy_trial_04 Control rep1「復元型候補(強)」は「要Fable確認」のまま、Fable/ユーザーの最終ラベルは見つけていない。
- polysemy_note/A3の「E1で誤読実例」(`A3_polysemy_candidates_and_rules.md` L8)の「E1」が指す実例は今回未特定。
- 時系列#1b(A-1)の個別json、#5の方向Trial詳細(Opusレビュー含む)は表の記述止まり。
- #15(今回E2E)にはHC-012の3値ラベルが無く、CCP基準での分類は【推測】(同型文は曖昧)にとどまる。
- 日付はgit add日であり、記事の実際の生成日とずれる場合がある(#2)。
