# LEDGER_AUDIT_01: 過去Risk Flagger Trialへの「台帳パーサ欠落」波及調査(WRITER-R0-MODEL-IMPACT-TRIAL-01-FIX01 項目2・3 = FIX01-B)

性質: read-only調査(API費用 ¥0、Production変更なし、detectors配下無変更、SSOT/git操作なし)。数値は全て `audit_ledger_coverage_01.py` による機械照合値(生データ `ledger_audit_01.json`)。「確認済み事実」と「推測/提案」を分けて書く。**最終判定(有用/誤検知/ラベル変更)はしていない。過去KPI値は書き換えていない。**
Status: 既存の WRITER-DEV-RISK-FLAGGER-DESIGN-01 評価値(FINAL_REPORT_01 §0 の KPI表)は、下記の影響確認と再評価が終わるまで確定値として扱わない(ユーザー指示どおり)。

## 0. 結論(先に)

1. **Disney+以外にも欠落あり**: `semiconductor_earnings`(Broadcom)の F1 も欠落していた。欠落が出た台帳は、調査対象の台帳 28 本中 **2 テーマ(streaming_price、semiconductor_earnings)**。台帳のコピーは各テーマで new / old / shared が同一内容(md5一致)。
2. **欠落の規模(Flaggerが実際に受け取ったFact数と台帳の見出し行数の差)**: streaming_price 5/7(F01・F07欠落)、semiconductor_earnings 5/6(F1欠落)。それ以外の台帳(byd_recall, central_bank_mortgage, hormuz, meta, openai_copyright, small_bag, space_weapons, ai_control 等 26 本)は全件受領(見出し数 = 受領数)。
3. **影響を受けた評価単位**: 文単位ケース 9/78(dev 4、holdout 5。合成 14 件と dev_reg3 3 件は影響なし)、記事 7/38(新旧 JA/EN: streaming 4 + semiconductor 3)。**9ケースは全て「非重大」ラベル**、重大ラベルのケース(および Rollback/K12/合成)は全て完全台帳を受領。
4. **過去KPIへの影響(提案。確定はFable/ユーザー)**: **「一部再計算必要」**。KPI1(Recall)・KPI4 は影響なし。KPI2(FPR_clear の分母 4/18 と分子 1/3、FPR_boundary の分母 1/3、Precision)、KPI3 の中身、KPI5 の人間確認パック(52 Flag 中 10 Flag)が影響対象。「評価自体を再実行すべき」には至らない見込み(影響は特定の 2 テーマ 16 単位に限定。再実行見積り 約¥48、過去記録費用からの推定)。
5. **根本原因**: `ledger_restore_01._HDR` の見出し正規表現 `^\[[A-Z_]+\]\s+...` が、台帳生成コードが決定論で付ける `[AMBIGUOUS - 断定禁止、曖昧さを保持すること]` を許容しない。台帳生成側は「AMBIGUOUS 判定の Fact は必ずこの見出しにする」構造なので、**今後も再発する**(特に AMBIGUOUS Fact が出るテーマで毎回)。かつ失敗が**無音**(エラー・警告なし)。

## 1. 記事一覧と機械照合(項目2-1〜2-5)

### 1-A. 調査対象の確定方法(確認済み事実)
- 実際にFlaggerへ渡した入力 = `casebank/casebank_01_{dev,dev_reg3,holdout,synthetic_dev,synthetic_holdout}_blind.json` の各 case の `ledger[]`(文単位モード)と、`p3_manifest_01.json` の 38 記事(記事モード。台帳は manifest の `ledger_path`、または `ledger_case` 経由で blind ファイルの `ledger[]`)。「受領Fact数」は blind の `ledger[]` 件数(=パーサ出力)。「台帳見出し行数」は台帳ファイル(`casebank_01_ledger_origin.json` の解決先)の `^[タグ] ID:` 形式の全行(タグは任意文字、全角コロン許容の寛容正規表現)。
- 対象: 文単位 78 ケース(dev 24 / dev_reg3 3(devの再掲)/ holdout 37 / 合成dev 7 / 合成holdout 7)、記事 38(新旧 28 + dev既知 3 + holdout既知 7)、台帳ファイル 28 本。P1パイロット(rf_ur5649, rf_7b6trp, rf_apqtyt)・sanity10 は上記ケースの部分集合で、影響ケースを含まない(機械確認)。
- 台帳所在未確認のケース/記事: **なし**(origin 解決は 75 ID(合成14件を含む)で src 37 / pool 38。78 ケース全件が解決済み)。補足: pool 解決(fact_id+本文先頭一致による他ケースからの推定)の 38 件は、受領 Fact ID 集合と解決先台帳の ID 集合が(欠落分を除き)全件一致したことで、解決先が正しいことを確認した。
- 台帳に無い Fact を受領した例(`extra_ids_sent`): 0 件。

### 1-B. 欠落があった台帳(確認済み事実)
| テーマ | 台帳(run) | 見出し行数 | Flagger受領 | 欠落ID | 欠落Factの見出し形式 |
|---|---|---|---|---|---|
| streaming_price(Disney+) | factlock_astra_e2e_trial_01/runs/streaming_price/{new,old,shared} | 7 | 5 | **F01, F07** | `[AMBIGUOUS - 断定禁止、曖昧さを保持すること] F0x:` |
| semiconductor_earnings(Broadcom) | factlock_astra_e2e_trial_01/runs/semiconductor_earnings/{new,old,shared} | 6 | 5 | **F1** | 同上 |

欠落Factの内容(台帳原文、`ambiguity_note` 含む):
- **streaming F01**: 「2026年10月8日までに今回のWeb調査で確認できた主要な米国向け動画ストリーミング価格改定のうち、最も新しい発表としてDisney+の2026年9月23日の改定を選定した。」 ambiguity_note: 全世界・全地域の小規模サービスを網羅した比較ではなく、検索で確認できた主要サービスの発表からの選定。 notes_for_writer: 対象はDisney+の当該発表に限定する。他サービスとの比較はしない。
- **streaming F07**: 「今回確認したDisney+の米国価格ページとReuters報道では、Disneyが今回の値上げ理由を明示した記述は確認できない。Reutersは、DisneyがReutersのコメント要請に直ちには回答しなかったと報じた。」 conditions: 確認対象に含まれない別の顧客通知等で、追加説明が行われた可能性までは否定しない。 ambiguity_note: 確認できた資料の範囲で会社が示した理由は特定できない。価格改定の動機を推測して補わないこと。 notes_for_writer: 一般的な業界要因やDisneyの別時期の説明を、今回の値上げについて会社が述べた理由として転用しない。
- **semiconductor F1**: 「対象企業はBroadcom Inc.。同社は2026年9月2日、2026年度第3四半期の決算を発表した。」 ambiguity_note: 発表自体は確認できたが、テーマの「最も最近の発表」という選定条件は Broadcom の発表日だけでは確認できない(例: 「leading AI chipmaker」に Micron を含めるなら、9月30日に決算を発表した Micron が後)。分類の範囲が曖昧で、Broadcom を選定対象とする前提は確定できない。

欠落Factが他の Fact ブロックに混入していないこと(パーサが前ブロックへ連結する汚染)は機械確認済み(blank行でブロックが切れるため、欠落は純粋な「脱落」。混入 0 件)。

### 1-C. 影響を受けた評価単位の一覧(確認済み事実)
**文単位ケース(9/78。全て「非重大」ラベル)**
| split | case_id | 言語 | テーマ/腕 | 受領/見出し | 欠落ID | ラベル(出所) | 負例区分(aggregateの`_neg_group`) | 過去に立ったFlag |
|---|---|---|---|---|---|---|---|---|
| dev | rf_wfzehu | JA | streaming old | 5/7 | F01,F07 | 非重大/軽微(Sonnet暫定 w3-98、ユーザー未確認) | boundary | なし(全構成0) |
| dev | rf_pdmdt5 | EN | streaming new | 5/7 | F01,F07 | 非重大(機械抽出の弱ラベル) | clear | なし |
| dev | rf_ptrj37 | JA | semiconductor new | 5/6 | F1 | 非重大/軽微(Sonnet暫定 w3-85) | boundary | なし |
| dev | rf_ah9aha | EN | semiconductor old | 5/6 | F1 | 非重大(弱ラベル) | clear | なし |
| holdout | rf_qupkjh | EN | streaming old | 5/7 | F01,F07 | 非重大(弱ラベル) | clear | なし |
| holdout | **rf_5cryu9** | EN | streaming old | 5/7 | F01,F07 | 非重大(弱ラベル) | clear | **あり**: D2(0.85)・D1v2(0.98) が s1「The standalone plan with ads will cost $11.99 a month.」を 数量時系列 で Flag(根拠 F02)。C_main の FPR_clear 誤Flag 3件のうちの 1 件 |
| holdout | rf_g4uegk | EN | streaming new | 5/7 | F01,F07 | 非重大(弱ラベル) | clear | なし |
| holdout | rf_mytfwc | JA | semiconductor new | 5/6 | F1 | 非重大/軽微(Sonnet暫定 w3-86) | boundary | なし |
| holdout | rf_9x3gdn | EN | semiconductor old | 5/6 | F1 | 非重大(弱ラベル) | clear | なし |

**記事モード(7/38)**: semiconductor_earnings_new_ja / old_ja / old_en(5/6、F1)、streaming_price_new_ja / new_en / old_ja / old_en(5/7、F01・F07)。dev既知3記事・holdout既知7記事(重大を含む既知記事)は全件完全受領。

**全体の網羅状況(機械値)**: ケース 78 件中 完全 69 件・欠落 9 件。記事 38 件中 完全 31 件・欠落 7 件。台帳ファイル 28 本中 欠落 4 本(new/old の 2 テーマ分。shared は casebank で未使用)。

## 2. 過去Flagとの突合(項目2-6、2-7)と Disney+ 再判定材料

形式: 過去Flag / 当時の判定根拠 / 欠落Factに根拠あり? / 再判定必要?(候補)。**ここは候補提示のみ。有用/誤検知/ラベルの最終判定はしていない。**「欠落Factに根拠あり?」は、Flag文と欠落Fact本文の内容照合(Sonnetによる読み取り。語彙の重なりも参照)で、確定ではない。

### 2-A. 文単位ケース(C_main/D1v2 などで立ったFlagは 1 ケースのみ)
| 過去Flag | 当時の判定根拠 | 欠落Factに根拠あり? | 再判定必要? |
|---|---|---|---|
| rf_5cryu9 (holdout, EN, streaming old a2) D2 0.85 / D1v2 0.98 「The standalone plan with ads will cost $11.99 a month.」数量時系列、対応 F02 | ラベル=非重大(機械抽出の弱ラベル。数値トークンが台帳の同一Factに全て含まれる文。「Sonnet全文照合で当該文を指す所見なし」、文単位の人間確認ではない)。Flagは旧価格だけを述べて新価格の文脈が落ちる点への指摘で、F02 の数値と整合。 | **根拠は F02(受領済み)にあり。F01/F07 は無関係と見える**(F01=選定、F07=理由/Reuters。この文は価格のみ)。ただし F01/F07 を入れた再実行でFlagが変わるかは**未検証** | 要(確認者: Fable。Flag自体は欠落Factと無関係に見えるが、KPI2の分子に入っているため完全台帳での再計算で確認) |
| 他 8 ケース(rf_wfzehu, rf_pdmdt5, rf_ptrj37, rf_ah9aha, rf_qupkjh, rf_g4uegk, rf_mytfwc, rf_9x3gdn) | 全検出器・全構成でFlagなし(D0, D1full, D1v2, D2 rep1/rep2, D3 派生) | Flagがないので突合対象なし | 再判定不要。ただしKPI2の分母に入る(§3) |

### 2-B. 記事モード(C_main = D2rank上位3 ∪ D0 rollback。D1v2 は新腕JAのみ)
| 過去Flag(記事/文/種類/確信度) | 当時の判定根拠(Flaggerの確認質問の要旨) | 欠落Factに根拠あり? | 再判定必要? |
|---|---|---|---|
| streaming_price_new_en s26 その他 0.30「According to Reuters, Disney did not answer a request for comment right away.」(対応F05,F06) | 「台帳にはReutersによる取材やDisneyの回答状況の記載がない」 | **あり: F07 の第2文がそのまま根拠**(受領した Fact に無いと言っているが、台帳には存在) | 要(確認者: ユーザー) |
| streaming_price_new_en s25 不在断定 0.25「pricing page and the Reuters report that we checked did not clearly state Disney's reason」(F05,F06) | 「台帳は価格と適用条件を示し、理由の記載の有無までは示さない」 | **あり: F07 第1文**(理由を明示した記述は確認できない) | 要(ユーザー) |
| streaming_price_new_en s28 不在断定 0.20「But the sources we checked do not tell us the reason.」(F05,F06) | 「台帳に理由がないことと情報源に理由がないことは別」 | **あり: F07 + ambiguity_note**(確認できた資料の範囲で理由は特定できない) | 要(ユーザー) |
| streaming_price_new_ja s27 不在断定 0.35「…Reutersの報道には、Disneyが今回の改定理由を明示した記述はありませんでした。」(F05) | 「台帳では米国価格ページとReuters報道に改定理由の明示がないことまでは確認できない」 | **あり: F07 第1文** | 要(ユーザー) |
| streaming_price_new_ja s28 その他 0.30「Reutersによると、Disneyはコメント要請に直ちには回答しなかったそうです。」(対応Factなし) | 「台帳にReutersのコメント要請や回答状況の記載がない」 | **あり: F07 第2文** | 要(ユーザー) |
| streaming_price_new_ja s28 数量時系列 0.86 (D1v2、同文) | 「『直ちには回答しなかった』という回答時期の記述は、台帳Factにない時期情報の追加」 | **あり: F07**(同文は上のs28と同一。D1v2 は主集計の対象外=Aと同文のため追加分には出ていない) | 要(ユーザー) |
| streaming_price_new_ja s26 不在断定 0.20「ただし、ここには明快な種明かしがありません。」(F02-F06) | 「台帳に改定理由が記載されていないことだけでは、理由の説明が存在しないとは判断できない」 | **あり: F07**(確認した資料では理由が明示されていない、と台帳が明記) | 要(ユーザー) |
| streaming_price_old_ja s18 / old_en s18 不在断定 0.12「確認した資料からは、…理由を示したとは確認できません」(F02-F06) | 「台帳には値上げ理由の説明の有無の記録がない」 | **あり: F07** | 要(ユーザー)。ただし旧腕の Flag は確認パック(新腕のみ)に含まれていない |
| streaming old/new 他のD2rank: old_ja s10, s14 / old_en s10, s2(時差、年払い、「開始間近」) | 適用日・請求サイクル・プラン範囲(F04/F06)に関する確認質問 | なし(F01/F07 の内容と無関係に見える) | 不要(ただし強制列挙の順位は変わりうる §3) |
| streaming_price_old_ja s12-s15 / old_en s15 D0(数量時系列 0.30、gate_only、台帳にない数値) | 数値(11, 49, 99 等)が台帳に無い、という機械ルール | なし(F01/F07 に価格数値は無い。小数の分割表記による機械ルール由来) | 不要 |
| streaming_price_new_ja s3 D1v2 因果創作 0.68「その一報で、脳内の家計簿に緊迫したBGMが流れた人もいるでしょう。」(F02-F04) | 値上げ報道に対する心理反応の付け足し | なし(F01/F07 は無関係) | 不要(確認パックの「追加分1」) |
| semiconductor_earnings_new_ja s31, s36, s6 / old_ja s11, s16, s15 / old_en s16, s7, s24 D2rank | F4/F5/F3/F6 の範囲・期間・帰属に関する確認質問 | なし。F1 は「Broadcom を選定した前提(最近の発表か)」の曖昧さで、記事にその主張(「最新/直近/leading」)が無く、いずれのFlagとも内容が重ならない(記事本文の語彙検索でも該当なし) | 不要(強制列挙の順位変動の可能性のみ §3) |
| semiconductor_earnings_old_en s4, s5, s6, s15, s16 D0(数量時系列 0.30、gate_only) | 数値(29.591, 16.7, 34.8, 21.7)が台帳に無いという機械ルール | なし(F1 に数値は無い) | 不要 |

### 2-C. 前回Disney+人間判定の再確認(ユーザー指定の観点)
前回の人間判定そのもの(ユーザーが「Fact捏造/要確認」と判断した記録)は、本調査で確認できた範囲のリポジトリ記録(DECISION_LOG, FINAL_REPORT_01, FLAG_LIST_01, RESULT_02, HUMAN_CHECK)には**見つからなかった**(確認パックの回答欄は未記入、KPI5 は「未取得」)。そのため、ユーザー指定4観点に該当する過去Flagを下に集約する。**会話で行われた判定内容がある場合は、Fableからその内容を渡してもらわないと「当時の判定」を照合できない(要確認)。**

| 観点 | 過去Flag(出所) | 当時の判定根拠 | 欠落Factに根拠あり? | 再判定必要? |
|---|---|---|---|---|
| 改定理由が明示されていない | Risk Flagger Trial 確認パック: new_en s25, new_ja s27(D2rank 0.25 / 0.35)。R0 Trial(FLAG_LIST_01): Luna #1 (s17, 0.90), Sol #1 (s7, 0.96) | 台帳(受領分)に理由の有無の記載がない、というFlag理由 | **あり: F07(第1文 + ambiguity_note)** | 要(ユーザー) |
| Reutersのコメント要請への回答状況 | パック: new_en s26(0.30), new_ja s28(0.30、D1v2 0.86)。R0 Trial: Luna #4 (s17, 0.78) | 台帳にReuters/回答状況の記載がない | **あり: F07(第2文)** | 要(ユーザー) |
| 「理由が分からない/説明がない」系 | パック: new_en s28(0.20), new_ja s26(0.20)。old_ja/old_en s18(0.12、パック外)。R0 Trial: Luna #2 (s16, 0.86), Luna #3 (s18, 0.86) | 台帳に理由がないことと資料に理由がないことの同一視、というFlag理由 | **あり: F07(ambiguity_note「確認できた資料の範囲で会社が示した理由は特定できない」)** | 要(ユーザー) |
| 上記のJA/EN版 | パック new_ja(s26/s27/s28)と new_en(s25/s26/s28)は文が対応。R0 Trial はLuna(JA)・Sol・Astra記事 | 同上 | あり(F07) | 要(ユーザー) |

補足(確認済み事実): R0 Trial の Disney+ 5 Flag は、FIX01-A が完全台帳 7 Fact で再実行した結果、全セルで 0 件になった(`FIX01_DISNEY_RERUN_01.md`、本調査では再実行していない)。一方、Risk Flagger Trial 側の記事(factlock_astra_e2e_trial_01 の new/old 記事)は**完全台帳での再実行を未実施**で、上表の「あり」は台帳テキストとFlag文の照合による(Flaggerが完全台帳で同Flagを出さなくなるかは**未検証**)。
確認パック上の見え方: 確認パックの「根拠Fact」表示は F05/F06(または F02/F03)のみで F07 は表示されず、確認質問は「台帳にReuters/理由の記載がない」と書かれている。つまり**人間が回答するとき、台帳には実在する F07 が見えない状態**になっている(パック 3 記事: 52 Flag 中 10 Flag が該当 §3)。

### 2-D. ユーザーが過去に「Fact捏造/要確認」と判断したFlagで、欠落Factに根拠があったもの(項目2-7)
- リポジトリ記録上の該当: **0 件**(ユーザー裁定が記録されたFlagは、本Trialでは S0_USER_CHECK 3 文のみで、いずれも ledger 欠落のない hormuz/meta 系。streaming/semiconductor の人間裁定記録なし)。
- 上記のとおり、会話上の判定が記録外にある可能性があり、その場合はFableから内容の提供が必要(要確認)。

### 2-E. casebankラベルの出所と、評価時に完全台帳を見ていたか(確認事実のみ)
- 9 影響ケースのラベル出所: Sonnet暫定 3 件(rf_wfzehu, rf_ptrj37, rf_mytfwc。EVAL_E2E_01 の B-11/B-09/B-10、`labels_merged.jsonl`、ユーザー未確認)、機械抽出の弱ラベル 6 件(「Sonnet全文照合で該当文を指す所見なし」)。ユーザー確認済みの重大ラベルは影響ケースに**ない**。
- E2E評価(labels w1/w2/w3)の評価者は、`runs/<theme>/shared/ledger.txt`(台帳原文のテキスト)との照合でラベルを付けており(`labels_w3_summary.md` の記述。streaming新Advの「F07関連の修辞1[問題なし、AMBIGUOUS由来]」等、AMBIGUOUS Fact を評価に使った記載あり)、**ledger_restore のパーサ経由ではない**。したがって**ラベル自体はパーサ欠落の影響を受けていない可能性が高い**(評価ワーカーの入力ファイルそのものは本調査で再点検していない = 「記述に基づく」確認)。
- ただし casebank 構築スクリプト `casebank/build_casebank_01.py` の `load_ledger`(L127)も `\[VERIFIED\]` のみを読む別のパーサで、**弱ラベル(機械抽出)の Fact 選定は VERIFIED Fact のみが対象**だった(確認済み事実: L127、L533 周辺)。影響: 弱ラベルの「同一Factに数値が含まれる文」の候補から F01/F07/F1 は除外される(これらは数値をほぼ含まない)。casebank の `articles[].n_facts`(streaming 5、semiconductor 5)も同パーサの値で、台帳の実際の見出し数(7、6)と異なる。
- Flag文と欠落Factの照合・Flagの有用/誤検知の判定は上記のとおり候補提示まで。

## 3. 過去KPIへの影響(項目2-8)

**提案: 「一部再計算必要」**(影響なし ではない。評価自体の全再実行までは不要と見込む。確定はFable/ユーザー)。

| 指標 | 影響の有無と根拠(機械照合) | 分子/分母 | 判定案 |
|---|---|---|---|
| KPI1 Recall_human / Recall_all(保留 casebank 11 重大) | 影響ケース 9 件は全て非重大ラベル。重大ラベルのケース全件で受領 = 見出し数(欠落 0) | 重大ケースの入力は完全 | **影響なし** |
| KPI4 既知事故への強さ(Rollback、K12、6系統) | Rollback/K12/合成/既知事故ケースは影響単位に含まれない | — | **影響なし** |
| KPI2 FPR_clear(保留 C_main 3/18) | 保留 clear 負例 18 件中 **4 件が影響ケース**(rf_qupkjh, rf_5cryu9, rf_g4uegk, rf_9x3gdn)。分子 3 件のうち **1 件(rf_5cryu9)が影響ケース**(他 2 件 rf_c3p892, rf_b2nvsf は hormuz/meta でD0 rollback 語彙の誤爆=影響なし) | 分母 18 のうち 4、分子 3 のうち 1 | **一部再計算必要**。FPR_clear 範囲は 2/18〜(変動なら増減)の可能性。完全台帳での再実行が必要 |
| KPI2 FPR_boundary(1/3) / FPR_hardneg(0/5) | boundary 3 件のうち rf_mytfwc が影響(Flagなし)。分子の rf_6j5x2m(space_weapons)は影響なし。hardneg は影響なし | boundary 分母 3 のうち 1 | 一部再計算必要(分母の1件) |
| Precision_cb(Flag精度) | 負例側のFlag数に rf_5cryu9 のFlagが含まれる | 分母の Flag 数に影響しうる | 一部再計算必要 |
| dev 側(P2 閾値調整、dev FPR) | dev 24 件中 4 件が影響。全構成で Flag 0 件。 | dev clear/boundary 負例の分母のみ | 影響軽微(分母のみ。再計算の優先度は低い) |
| 合成dev/holdout(14 件) | 全て hormuz 台帳、完全受領 | — | 影響なし |
| KPI3 Flag/記事(平均 3.07、新旧 28 記事) | 記事モードは上位3文を強制列挙する構造で、件数は台帳欠落と無関係に約3件(7/28 記事が欠落台帳)。数値は**同じになるが中身(どの文がFlagされるか)は変わりうる** | 28 記事中 7 | 数値は影響なし(構造上)。**内容は一部再計算必要** |
| KPI5 / 人間確認パック(C_main 44 + D1v2追加分 8 = 52 Flag) | パック内の欠落台帳の記事: streaming new EN (3 Flag)、streaming new JA (3 Flag + 追加分 1 Flag)、semiconductor new JA (3 Flag) = **10 Flag(C_main 9 + 追加分 1)**。うち Disney+ の 6 Flag(C_main)+ 追加分 1 のうち F07 に根拠があるのは 6 Flag(s25/s26/s28 EN、s26/s27/s28 JA)。semiconductor 3 Flag と 追加分(因果創作)は F1/F01/F07 と無関係に見える | 52 Flag のうち 10 | **要差し替え・再生成**(3 記事のD2rank/D1v2を完全台帳で再実行。強制列挙のため、F07を入れると別の文が上位3に入りうる)。回答欄が未記入のため、既存回答の無効化は発生しない |
| P3の記事モード調整の結果(Recall@top3 など) | 重大を含む既知記事(dev 3、holdout 7)は完全受領 | — | 影響なし |

再実行する場合の見積り(推定): 影響単位の過去記録費用の合計(重複の派生 d3_* を除く)= D2rank(記事 7)¥12.05 + D1v2(記事 2)¥10.94 + 文単位 D2 holdout 5 ¥3.27 + D2 dev 4×2rep ¥2.57 + D1v2 holdout 5 ¥12.01 + D1 gate dev 4 ¥6.96 ≒ **約¥48**(過去の `cost_jpy` からの推定。実行前に再見積りが必要)。今回はAPIを呼んでいない。

## 4. パーサ不具合の根本原因(項目3)。修正案のみ。実装なし

### 4-A. なぜ読めないか(確認済み事実)
- `detectors/ledger_restore_01.py` L12: `_HDR = ^\[(?P<st>[A-Z_]+)\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$`。タグ部分が `[A-Z_]+`(大文字と下線のみ)かつ直後に `]` を要求する。
- 台帳生成コード `er003_v1_en_direct_vfl_01_generate.py` L292: `tag = "[VERIFIED]" if verdict == "VERIFIED" else "[AMBIGUOUS - 断定禁止、曖昧さを保持すること]"`。タグに空白・ハイフン・日本語が入るため `[A-Z_]+\]` に一致しない。
- 失敗が**無音**: 不一致の見出し行は読み飛ばされ、後続のインデント行(scope/conditions/ambiguity_note 等)も `cur is None` のため捨てられる(L28-31)。エラー・警告・受領数の検証は無い。`run_flagger_01.py` / `make_blind_01.py` / `p3_run_01.py` / `flagger_lib.py` には件数照合が無い(grep で `assert` は `p3_run_01.py` L31 の `ledger_complete` 真偽のみ。件数は見ていない)。同様に `_PREFIX`(L13)も同じ制限(接頭辞除去に失敗するため、仮に見出しだけ拾えても本文に `[AMBIGUOUS...]` が残る別の不具合が起きうる)。
- 混入(欠落Factが前のFactのブロックへ連結する)は起きない(Fact間は空行で区切られ、空行で `cur=None` に戻る。実測で混入 0 件)。

### 4-B. 他の見出し形式にも同じリスクがあるか(機械確認)
**現行パーサ(`_HDR`)に対する見出し形式プローブ(合成。コード無変更)**: 通る = `[VERIFIED] F01:`、`[AMBIGUOUS] F01:`、`[PARTIALLY_SUPPORTED] F01:`(大文字+下線なら任意のタグ)、`[VERIFIED]  F01:`(空白2個)、`[VERIFIED] F-01:`。**落ちる** = `[AMBIGUOUS - …] F01:`(生成器の実形式)、小文字タグ `[verified]`、`[VERIFIED]F01:`(空白なし)、全角コロン `F01：`、ID直後のスペース `F01 :`、全角括弧、先頭空白・箇条書き `- [VERIFIED]`、`[F-001] 本文`(タグ無し・コロン無し)。詳細は `ledger_audit_01.json` の `variant_matrix`。
**リポジトリ全体の台帳 540 ファイルの実測**: 見出し行(寛容正規表現)7,851 行に対し、現行パーサが読むのは 7,728 行で **123 行(37 ファイル)を読み飛ばす**。内訳: AMBIGUOUS タグの Fact(44 行ぶん + 同形式のファイル)、`[VOICE_n_EVIDENCE] 1-01(...)`(Voices 系台帳、g/b-family。ID に括弧を含む)、`[SRC-001] ...`/`[F-001] 本文`(pool_pilot 系、タグ・コロン形式が別規格)、`[Hot-Desking]`等の本文先頭の `[…]`。AMBIGUOUS で落ちる他の台帳: inbound_tourism(F04, F06)、`gpt6_wiring_e2e_01`(MUSE-HC-08)、`e_family_two_level_wiring_01` と `er017_*`(MUSE-014)、`en_direct_vfl_01/A02`(PILOT-04)、`ADD03`(HORMUZ-001, PILOT-001)。**今回のRisk Flagger Trialの入力台帳 28 本については、見出し形式は `[VERIFIED]` と上記 AMBIGUOUS の 2 種類のみ**で、非インデント・非見出し行は 0 行(機械確認)。つまり今回の欠落は AMBIGUOUS 形式の 1 種類に限られる。ただし将来の台帳(別系統の台帳)では他形式でも落ちる。
**同じ種類の脆弱性は他の箇所にもある**(リポジトリ検索の事実。実害の有無は未調査): `casebank/build_casebank_01.py` L127(VERIFIED のみ)、`docs/pm/b3_trial_01/make_unprovided_checklist.py` L11(`[A-Z_]+`)、`er052_output/open233_allfact_note_e2e_02/tools/check_brief_transfer.py` L10(同)、`open233_kpi_recovery_02_offline_01/*.py`(`[VERIFIED]` のみ)、`open233_floor_*_offline_01/*.py` 等。一方、Production系の読取り(`er015_*`, `er019_family_x_storyline_b3_fact_selection_01.py` L129, `er051_*` L316, `er052_open233_self_recovery_precheck_01.py` L57)は `AMBIGUOUS[^\]]*` を許容しており、Flagger側のパーサだけが独自に狭い仕様のまま作られた(推測: 開発時に VERIFIED のみの台帳(Meta/Hormuz)で動作確認したため)。

### 4-C. 今後も再発する構造か(推測を含む)
- **再発する(確実に近い)**: AMBIGUOUS 形式の見出しは、`verdict != VERIFIED` かつ REJECTED でない Fact に対して**決定論で必ず**付与される(生成コード L288-292)。「検証結果が欠落した場合も安全側で AMBIGUOUS」(L282-287)。台帳明確化(ledger clarity)の運用(`docs/pm/ledger_clarity/01_current_pipeline.md` L10, L23)でも同形式が前提。AMBIGUOUS Fact を含むテーマ(今回の 2/9 テーマ、リポジトリ全体では 37 ファイル)では毎回、同じ脱落が起きる。
- 無音失敗であり、結果ファイルの `n_facts` が見出し数と合っているかを誰も照合していなかった(今回は R0 Trial のとき `n_facts`=5 に気づいて発覚)。
- 解析パスが複数ある(ledger_restore のファイル読込、casebank 構築、blind の embedded ledger)が、いずれも件数の検算なし。

### 4-D. 修正案(提示のみ。実装しない。Production/正式Risk Flaggerは未修正)
| 案 | 内容 | 影響範囲 | リスク/注意 |
|---|---|---|---|
| A. 正規表現の拡張(最小) | `_HDR` を `^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):…` に、`_PREFIX` も同様に。FIX01-A の `r0_fix01_driver.py` が同一方向の差替えを process 内で実施済み | `ledger_restore_01.py` を使う全パス(run_flagger, make_blind, p3_run, casebank 復元)。AMBIGUOUS のみ救済 | 将来の別形式(全角コロン、`[VOICE_…]` 系、先頭空白等)は救済されない。`strip_prefix` も同時修正しないと本文に `[AMBIGUOUS…]` が残る。過去結果(blind JSON、results)は更新されないので再実行が必要 |
| B. 見出し行の全件受理 + タグ別フィールド化(推奨の方向) | 見出しを「行頭の `[` から最初の `]` まで = タグ(任意文字列)、続く `ID:`(または `ID：`)」と定義して全件受理し、Fact に `status`(VERIFIED / AMBIGUOUS …)と `ambiguity_note` を保持。Flagger には AMBIGUOUS Fact も渡し、プロンプトで「曖昧さを保持した Fact」であることを明示するか、渡し方を明示的に決める(例: ID, 本文, ambiguity_note) | パーサ + Flagger入力スキーマ(`facts[{fact_id,text,status}]`)+ プロンプト | **入力仕様の変更**に当たる(FIX01-A の再実行は「他5件と同じ扱い」で本文+後続行を渡した=この選択は一例)。AMBIGUOUS Fact を「事実として根拠にしてよいか」はFlaggerの設計判断(Production仕様に関わる)で、ユーザー決定が必要(`USER_DECISION_REQUIRED` 候補) |
| C. 実行時 assert / 警告(併用必須) | 台帳読込直後に「行頭が `[` の非インデント行の数」「寛容正規表現の見出し数」とパーサ出力数を照合し、不一致なら**例外で停止**(または少なくとも警告 + 結果ファイルに `n_facts_expected`/`n_facts_passed` を記録)。blind JSON 生成後・Flagger 呼出前・結果集計時の 3 箇所 | `run_flagger_01.py`, `make_blind_01.py`, `p3_run_01.py`, aggregate | 誤検知(本文中の `[…]` 行)でStopしないよう、非インデント行のみを対象にする。既存の安全装置(費用ガード等)は無変更。**無音失敗を恒久的に防ぐ最重要の再発防止**(A/B 単独では不十分) |
| D. 台帳フォーマットの単一仕様化 | 台帳生成側と読取り側が共有する見出し仕様モジュール(1 か所の正規表現 + 単体テスト + 生成器が出力する全タグ種別を網羅するテスト)を新設し、casebank 構築・チェッカー・各 tools も同モジュールへ寄せる | 横断(多数のスクリプト) | 工数大。Production コードへ波及しうるため、別管理ID・ユーザー承認が必要。まず Trial/DEV 側(A+C)から |
| E. 生成側(台帳タグ)の簡素化 | AMBIGUOUS の理由表記を見出しでなく `status:` 行へ移し、見出しは常に `[VERIFIED]`/`[AMBIGUOUS]` | 台帳生成(Production寄り) | Writer へのプロンプト表現(曖昧さ保持の指示)に影響する Production 変更。本件の範囲外。参考案として記録 |

推奨順(提案、Fable判断): C(assert、仕様を変えず安全) → A または B(B は仕様決定を伴う) → 影響9ケース + 7記事 + 確認パック 3 記事の再実行(約¥48 見積り) → D は別管理IDで検討。

## 5. 未確認事項・限界
- 完全台帳での Risk Flagger **再実行は未実施**(本委任の範囲外)。「欠落Factに根拠あり」は台帳テキストとFlag文の内容照合であり、完全台帳でFlagが消える/残るかは未検証。
- ユーザーの会話上の過去判定(Disney+ について「Fact捏造/要確認」と判断した内容)は、リポジトリ記録から確認できなかった。Fableからの提供が必要。
- E2E評価ワーカーの実入力は再点検していない(`labels_w3_summary.md` の記述による)。
- 寛容正規表現(行頭 `[タグ] ID:`)に合致しない見出し形式は「見出し」としては数えていない。ただし調査対象 28 台帳には非インデント・非見出し行が 0 であることを機械確認済み。リポジトリ全体 540 ファイルの 123 行という数は、本文行頭の `[…]` 等も含む上限的な数で、「全て実害ある欠落」ではない。
- 本調査の `audit_ledger_coverage_01.py` は `ledger_restore_01` を import するのみ(コード変更なし、`__pycache__` 生成のみ)。

## 6. 成果物
- 本報告: `er052_output/writer_dev_risk_flagger_01/fix01_ledger_audit/LEDGER_AUDIT_01.md`
- 機械照合の生データ: `.../fix01_ledger_audit/ledger_audit_01.json`(ケース 78・記事 38・台帳 28・リポジトリ台帳 540 の見出し調査・見出しプローブ・混入検査)
- 照合script: `.../fix01_ledger_audit/audit_ledger_coverage_01.py`(`python -I audit_ledger_coverage_01.py` で再生成。read-only)
