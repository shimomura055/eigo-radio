# PREREGISTRATION_01(案。Fable/ユーザー確認後に確定。確定後は結果を見ての基準変更・Prompt修正・再実行を禁止、技術retryのみ可)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 Phase 2案。作成 2026-10-10(Phase 1、API 0件)。Production code/Prompt/CURRENT_SPEC は変更しない。後段AI(新Checker・二重チェック・A-B統合・多数決・補正AI)は追加しない。
**未確定事項(Fable判断)は`[要判断]`**。

## 1. 使用モデル(PM_GOVERNANCE 25節)
- B3系・Separate-call・R0 = `gpt-6-luna`(effort=high。Production B3/R0と同一条件。gpt-6世代の最新だが最上位系かは未確認。例外理由=本Trialの目的がProductionと同一条件での比較であるため)。応答model不一致はSTOP。
- 条件付き: Separate-call `gpt-6.1-sol`(Luna基準不達時のみ、6 call。登録単価 in$2/out$10)。最上位系(Opus級)比較は行わない(理由=数値ランクは規則適用タスクで、本番ラインはLuna前提)。
- 使用モデル/最新か/例外理由はRESULT_01.mdに必ず記載。

## 2. 腕・入力・call数(凍結入力=ROOTFIX-01と同一: 正式9テーマ、台帳・topicはsha256照合、Research/Ledgerは再実行しない)
テーマ: 問題5(semiconductor_earnings, small_bag, space_weapons, hormuz, central_bank_mortgage)+正常系4(meta, byd_recall, openai_copyright, streaming_price)。
| 腕 | 入力 | 新規call | 備考 |
|---|---|---|---|
| D-base | C0 9本+C1 18本(ROOTFIX-01出力を再利用)、案D(Dmin既定 `[要判断: D-min/D-full]`)で決定論組立 | 0 | 比較基準 |
| D-plus | 台帳(整形版)+topic、`b3r2_b3_dplus_01.py`(PROMPT_DIFF_01) | 9×2rep=18 | 本線Trial A |
| Sep | C0の採用ID+C0 Storyline+Fact抜粋、`b3r2_sepcall_01.py` | 9×2rep=18(Luna)+条件付きSol 6 | 本線Trial B。同一入力2反復=純粋な数値ランク再現性 |
| D-det | C0の採用ID+C0 Storyline、claim正規表現+規則 | 0 | `[要判断]` 推奨追加腕(DESIGN_REVIEW 観点1) |
| D-plus-min | 同上・整形なし | 18 | `[要判断]` 任意。推奨しない(DESIGN_REVIEW 5節3) |
反復2回の理由: B3の選択はノイズが大きい(C1 rep1 vs rep2の選択Fact Jaccard平均0.698、完全一致2/9)ため、1回では腕差とノイズを区別できない。2反復で「腕間差 vs 腕内ノイズ(rep1 vs rep2)」を比較する。それ以上は費用対効果が低い(3回目は結果を見て追加しない)。
実行順序(依存関係・並列性): ①最初のD-plus 1 call(hormuz rep1)のみ直列=実測単価でcap再見積(継続条件: 見積が変わらなければ続行) ②D-plus 17 callとSep 18 callは**独立**(入力が凍結済みで条件同一)→テーマ群単位の複数process並列、process別ログ→親が合算。直列化の理由なし(rate limit・予算確認は①の再見積で担保)。③E9(R0)はD-plusの出力に依存→直列。決定論評価(D-det含む)・人手目視表の作成は①と並行して準備(クリティカルパスは「D-plus 18 call実行→評価→E9→目視」)。見込み: B3系36 call並列約15〜20分、E9 12 call約10分、評価・目視準備を含め実行〜報告まで約半日。直列実行比で約40%短縮(Trial_01の36 call並列実績: 実行約30分)。

## 3. 評価指標と合格基準(決定論スクリプト`b3r2_eval_01.py`[Phase 2で作成、LLM判定なし]+人手目視。基準値はベースライン実測から設定済み)
共通: NFKC正規化。ベースラインはD-base/C1の既存出力。
- **M1 Fact選択精度**: (a)採用件数が3〜5の率 (b)選択Fact集合のJaccard: D-plus rep1 vs rep2、D-plus vs C0、D-plus vs C1。**合格(D-plus)**: 平均Jaccard(rep1 vs rep2)≥ C1の0.698−0.15=**0.55**、かつ平均Jaccard(vs C0)≥ C1 vs C0の0.648−0.15=**0.50**、かつ採用3〜5件率が C1(測定済み)以上−2/18。ノイズ床は`baseline_selection_noise_floor_01.json`。
- **M2 Storyline品質**: 決定論=長さ(C1は75〜155字)/Fact被覆(内容語の採用Fact claim含有率)/`IMP`該当文数/notes共通12字以上/限定表現率(C1 5/18)/Storyline内数字⊆採用Fact。人手=D-baseのStoryline(C1 18+必要時C0)とD-plus 18を腕名を伏せたblind表で9テーマごとにペア比較(事実の正確さ・一本化・読みやすさ)。**合格**: IMP該当 0、notes共通12字以上がC1(1/18)+1以内、新数字(Storyline内の採用Factに無い数字)0、人手ペア比較でD-plusが明確に劣る(事実誤り・主題ずれ)テーマ数が9テーマ中2以下。
- **M3 Storylineへの注意文混入 / Fact・注意の分離**: ベースラインC1・C0は0/27(IMP)のため天井。D-plusでIMP 0かつ人手目視で注意書き由来の文言をStorylineに転記したものが0。Fact行側(決定論組立)のIMP該当は構成上0。(情報量が低いことを結果に明記する。)
- **M4 注意書き継承(E2)**: 採用Factの`notes_for_writer`/`ambiguity_note`が制約ブロックに文字列完全一致で存在する割合=100%(D-plus、Dの決定論組立による)。
- **M5 中核・周辺ランク精度**:
  - 規則整合: LLM宣言roleが規則導出と一致する率(`ROLE_DISAGREES_WITH_RULE`; D-plus/Sep)。**合格**: 数値単位で≥90%、かつ中核0件(`NO_CORE`)は「規則上の適格概念が0件」の場合のみ許容。
  - GT比較(Sep・D-det、C0の採用IDで同一条件): GTの主数字キーで対応付け、(i)対応付け済みの中核/周辺一致率 (ii)GT中核の再現率 (iii)GT中核の適合率。参考指標(GTは人間正解ではない=Lane B旧Trialの同一Sonnet系2回の決定論統合)。**合格**: (i)≥0.90、(ii)≥0.80。D-detの予備プローブ値(参考・事前登録の基準作りには使っていない): (i)36/38=0.95、(ii)20/25=0.80。
  - **人手目視(最終判断)**: 腕名を伏せ、9テーマ×{Sep, D-det, D-plus rep1}のcore集合を並べ、意味上の誤り(Storylineの主役数値が周辺に落ちる、無関係な数値が中核)を数える。危険な誤り(主役数値の中核落ち)の件数を報告。合否: 危険な誤り 0〜1(9テーマ内)。
- **M6 数値欠落 / 新数字混入 / Fact取り違え**: 欠落=claim数字の`MISSING_SURFACES`(regex抽出との差を人手で確定。regex誤検出は除く)、新数字=`SURFACE_NOT_IN_FACT`、取り違え=他Factの表記を別Factに紐付け(hard)。**合格**: 最終(retry後)の新数字・取り違え=0。欠落(人手確定)≤5%(数値単位)。retry前の発生は報告。
- **M7 Fact ID整合**: UNKNOWN_FACT_ID/FACT_NOT_SELECTED最終0。技術retry率≤2/18(D-plus)、STOP 0。number_ranks追加によるoutput切れ(incomplete)発生数を報告。
- **M8 再現性**: Sep=同一入力のrep1 vs rep2で(fact_id, surface, role)集合のJaccard平均≥0.90。D-plus=両repで共通に採用されたFactについて同じ集合比較(参考。Fact選択ノイズと分離して報告)。D-det=決定論なので1.0(確認のみ)。
- **M9 コスト/latency/実装複雑性**: 実測JPY/call(cost logger+`row_cost_usd`と同じ単価表)、latency。**合格**: D-plus per call ≤ C1実測平均0.455の1.5倍(**JPY0.68**)、latency ≤ C1平均43.6秒の1.5倍(65.4秒)。Sepは1記事あたり追加費用を実測(Luna)で報告。比較: Sonnet注記約JPY15.7/記事。実装複雑性=追加module LOC/追加call数/追加retry経路。
- **M10 Writer R0影響(E9相当、有料12 call)**: 6テーマ(問題5+byd_recall)×{D-plus(rep1の出力から決定論組立+`insert_marks`)、対照=D-base(C0 id)+D-detの決定論印}×R0 1回=12 call。R0のみ(R1/R2/Astraなし、`full_ledger_text=None`)、Fact Lock R0 Prompt=Production同一(`fl.apply_factlock_patches`)。測定=Trial_01 E9の9項目(制約行への【事実N】付与/制約文の逐語転記/台帳ID・内部語の漏出/AMBIGUOUS限定/BYD型/音声化禁止記号/自己検証PASS率/R0冒頭復唱/HF-007型逐語)+**【中核数値】【周辺数値】タグの記事への漏出(`TAG_LEAK_RE`)**。**合格**: Trial_01 E9の目安合格と同じ(タグ漏出0・ID漏出0・自己検証100%・禁止記号がC0以下)。R0単価はTrial_01実測JPY0.45/call(ユーザー提示 JPY1.24/callは保守的上限として費用見積に使用)。
- **M11 既存注記検査との互換**(JPY0): D-plus/D-detの決定論assembler出力(`selected_brief_factlock.md`+annotation.json相当)に既存`b3_annotation_check_01.py`を適用し合否を報告(新Checkerは作らない)。`role`説明文・`unmapped_claims`等、既存検査が要求する欄の不足を一覧化。合否判定の対象外(報告)。
- **M12 問題テーマ+正常系**: 全指標を問題5と正常系4で分けて報告。

## 4. Closeout分類規則(3方式別。Production実装はしない。結果を見ての基準変更禁止)
| 方式 | VALIDATED(Trial限定) | REJECTED | USER_DECISION_REQUIRED |
|---|---|---|---|
| **数値ランク方式(同一call=D-plus)** | M1・M2・M3・M4・M5(規則整合・人手)・M6・M7・M9・M10 を全て満たす | M1またはM2に不合格(B3本来性能の悪化)、またはM6の最終新数字/取り違え>0、またはM7でSTOP | 一部のみ不合格(例: M9のみ超過、M5の規則整合80〜90%) |
| **数値ランク方式(決定論=D-det)**[要判断で腕に追加した場合] | M5(GT比較)・M6(欠落)・M8・M10 を満たす(LLM不要・追加費用0) | M5(i)<0.80 または人手で危険な誤り≥3 | 中間 |
| **別call方式(Sep、Luna)** | M5・M6・M7・M8を満たし、1記事追加費用(実測)≤JPY1.0 | M5/M6/M8不合格かつSol(条件付き6 call)でも不合格 | Lunaは不合格でSolは合格(1記事 JPY2〜8)、または+1 call分のlatency/複雑性の価値判断が必要 |
| **Storyline制約方式(役割宣言+欄ラベル分離)** | M1・M2・M3を悪化なく満たす(ベースライン天井のため「悪化させない」ことのみを確認、効果は判定不能と注記) | M2不合格、または注意文のStoryline転記>0 | 効果の有無が天井で判定不能と明記し、ユーザー判断へ(推奨はVALIDATED[no-harm]) |
- 3方式のうち複数がVALIDATEDなら、最も単純な構成(D-det > D-plus > Sep の順)を第一候補として併記し、**採否はユーザーに戻す**。いずれもVALIDATEDでも`APPROVED_FOR_PRODUCTION`ではない。
- STOP条件: cap超過見込み/凍結入力sha不一致/新LLM工程が必要/Research・Ledger仕様変更が必要/評価script不具合/危険な結果を見てPrompt修正したくなった場合/model不一致/Lane A C2の編集中ファイルに触れる必要が生じた場合。

## 5. Blind目視(人手が最終)
D-base(C1)/D-plus/Sep/D-detの該当出力(Storyline、core集合、Fact行のタグ位置)を乱数IDで混ぜ、対応表は別ファイル。目視担当=Claude側(Fable)全件+重要差分はユーザーに提示。E9の記事は全文目視(Trial_01と同様)。

## 6. 費用・Cap(見積。ESTIMATE_01.json。JPY1=$1/160)
| 項目 | call | low | mid | high |
|---|---|---|---|---|
| D-plus B3(per call 0.50/0.59/0.71) | 18 | 9.0 | 10.6 | 12.7 |
| Sep Luna(per article 0.09/0.18/0.38) | 18 | 1.6 | 3.3 | 6.9 |
| E9 R0(0.45実測〜1.24保守) | 12 | 5.4 | ~9.6 | 14.9 |
| **本線合計** | 48 | **16.0** | **23.5** | **34.5** |
| 任意: D-plus-min 18 | 18 | 9.0 | 10.6 | 12.7 |
| 条件付き: Sep Sol 6 | 6 | 10.5 | 22.0 | 46.0 |
| 任意+条件付き込み合計 | 72 | 35.5 | 56.1 | 93.3 |
- **Cap案: 本線 JPY50(high 34.5に再試行余裕+約45%)**。任意/条件付きを実施する場合はFable/ユーザー承認後に総額JPY100へ引上げ。最初のD-plus 1 call実測後に再見積、超過見込みならSTOP。低・中・高の差はD-plusの追加reasoningとSepの出力量の仮定による(見積。実測は未取得)。
- 単価: gpt-6-luna in$0.10/out$0.50、gpt-6.1-sol in$2/out$10 per 1M tokens(`er006_model_routing_pricing_coverage_test_01.py`の登録値)。cached割引なし(安全側)。

## 7. 成果物保存先
`er052_output/b3_rootfix_trial_02/`: runs/<arm>/<theme>/rep<n>/、eval/、cost_ledger_b3r2_01.jsonl、HUMAN_CHECK_B3R2_01.md、RESULT_01.md、PROMPT_DIFF_01.md、DESIGN_REVIEW_01.md、dry_run/。Phase 2のドライバは`b3r2_driver_01.py`に有料実行サブコマンド(b3/sep/e9)を追加して作る(本Phaseでは未実装=有料コードを含めない)。

## 8. Lane A C2への interface 影響(再掲・DESIGN_REVIEW 6節)
B3出力契約(number_ranks追加)/R0入力契約(Facts+制約ブロック+数値印)/annotated B3 producer(Sonnet注記→決定論assembler+insert_marks)/number rank情報の運搬(`fact_selection_evidence_*.json`にnumbers)/Writer制約欄(D-baseと不変)。Lane A編集中ファイルは未読。
