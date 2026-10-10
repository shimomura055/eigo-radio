# PREREGISTRATION_02(確定版。確定後は結果を見ての基準変更・Prompt修正・再実行を禁止、技術retryのみ可)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 委任_02 Phase 2a。確定日 2026-10-10。Production code/Prompt/CURRENT_SPECは変更しない。後段AI(新Checker・二重チェック・A-B統合・多数決・補正AI)は追加しない。
確定の担保: `b3r2_driver_01.py frozen` が本ファイルのsha256・Trial module群のsha256・凍結入力のshaを `frozen_b3r2_02.json` に記録し、有料サブコマンドは実行のたびに照合する(不一致=STOP)。

## 0. 位置づけ(Fable決定、Opusレビュー 2026-10-10 反映)
- Trialの主役は **D-det(決定論、call 0)**。比較対象が **D-plus-single-call**(同一callで数値ランク)と **Separate-call**(別call)。「役割宣言のみ」腕はStoryline混入対策(問題2)の単独効果を見る。
- **最終roleは常に規則(仕様3-5)で導出する**。LLMが宣言したroleは「規則との一致率」を報告するだけで、最終判定に使わない。LLMの価値は**表記(surface)の抽出**に限定して評価する(正規表現抽出で足りない部分を補えるか)。`kind`(LLM出力)も導出には使わず(表記からkindを再導出)、一致率のみ報告する。
- D-base = D-full(ROOTFIX-01の事前登録規則で選択済み)。Fact行=決定論組立(`assemble_D` の `Dfull`)、制約は別ブロック。
- 本委任では **E9(R0影響確認)を実行しない**(Lane A C2が編集中の jaw/er012_e/er019 entertainment runner/audio runner を読まないため)。E9は **Phase 2b** で別途実施し、その結果が出るまでD-detの最終Closeout(VALIDATED)は出さない。

## 1. 使用モデル(PM_GOVERNANCE 25節)
- B3系(D-plus・役割宣言のみ)・Separate-call = `gpt-6-luna`(effort=high、Production B3と同一条件。gpt-6世代の最新だが最上位系かは未確認。例外理由=本TrialはProduction同一条件での比較が目的)。応答modelが違えばSTOP。
- 条件付き: `gpt-6.1-sol`。**Separate-callでLunaが不達(API到達不可・両attempt失敗が複数テーマで継続)のときのみ**発動。累計JPY100(下記cap)内。発動前の個別報告は不要だが結果に必ず記載。
- 使用モデル名・最新か・例外理由はRESULT_2A_01.mdに記載。

## 2. 腕・call数(凍結入力=ROOTFIX-01と同一: 正式9テーマ、台帳・topic・C0採用ID・C0 Storylineはsha256照合)
| 腕 | 入力 | 新規call | 備考 |
|---|---|---|---|
| D-base | ROOTFIX-01のC0 9本+C1 18本(再利用)、`Dfull`で決定論組立 | 0 | 比較基準 |
| **D-det** | C0の採用ID+C0 Storyline、正規表現抽出+仕様3-5規則 | 0 | 主役。規則+抽出は`b3r2_rank_01.py`。Storyline側の表記も抽出対象 |
| D-plus-single-call | 台帳(欄ラベル整形版)+topic、`b3r2_b3_dplus_01.py`(PROMPT_DIFF_02) | 9×2rep=18 | 同一callで`number_ranks`出力 |
| Separate-call(Luna) | C0の採用ID+C0 Storyline+Fact抜粋(制約欄なし)、`b3r2_sepcall_01.py` | 9×2rep=18 | 同一入力2反復=純粋な再現性。Solは上記条件のみ |
| 役割宣言のみ | 台帳(欄ラベル整形版)+topic、`b3r2_b3_roleonly_01.py`(PROMPT_DIFF_ROLEONLY_02) | 9×2rep=18 | 役割宣言+欄ラベル分離のみ、number_ranksなし(旧D-plus-minの置換、A7) |
2反復の理由: B3のFact選択はノイズが大きい(C1 rep1 vs rep2のJaccard平均0.698、完全一致2/9)。腕間差と腕内ノイズを区別するため2反復。3回目は追加しない。

## 3. ROOTFIX-01事前登録案(PREREGISTRATION_01)からの変更点(Opusレビュー是正)
- **U1**: 役割宣言の「制約をFact選択の慎重さの参考にしてよい」を**削除**(ユーザー確定範囲外・保守化誘導)。D-plus・役割宣言のみの両Promptから除去済み(driver dry-runがassert)。
- **A1**: `validate_number_ranks`と`insert_marks`の一致判定に数字境界条件(直前に数字・`.`・`,`が無い、直後に数字(`.数字`/`,数字`を含む)が無い)。NFKC正規化。selftestに「1.5%と5%」「13日と3日」「19月と9月」「2,300件と300」「5.5と5」の位置検査。
- **A2**: 抽出に 月のみ(`9月`)、日のみ(`翌14日`の`14日`、ただし`日間`・`1日あたり`は除く)、第N四半期、時刻、合成数(`1万5000`・`2億5,000万`)、ISO日付、日付範囲(`10月27~28日`)、票数(`12対0`)、事件番号(`1:26-cv-08892`=name_embedded)、名称内番号(`Fall 2026`=name_embedded)、通貨記号前置を追加。**漢数字(三千人)・「数百」「数千」は対象外**(仕様どおり。数字を含まず抽出されない。annotation_notes相当に記録すべき対象)。四半期・時刻・日のみは`date_time`だが常に不適格(周辺)で、数える概念nには入る(仕様3-2の運用上の解釈。GT側のkind判定とずれる可能性)。
- **A3**: 仕様3-5-2の代替規則を反映: **台帳全体にnumeric_value欄が1件も無い場合に限り**Fact本文(ID行)の数字で比べる。date_or_period欄が台帳に1件も無い場合に限りFact本文の最初の日付表現で比べる(D-detの`eligible`とStep6文言の**両方**)。9テーマ中この代替が発動するのは small_bag(numeric_value欄0件)のみ。概念は仕様3-3に従い「同じ表記(NFKC)は全Factで1概念」「同じFactで主数字・単位が同じ/一方が他方に境界つきで含まれる表記は1概念」。概念キー(M8比較用)は `Fact ID|種類|主数字|単位`。DESIGN_REVIEW_01の「欄が無ければ常にperipheral」は訂正済み(同ファイル)。
- **A4**: D-detのGT比較は「既知値」(D-detの抽出規則は、C0 9テーマに対する既存注記検査`b3_annotation_check_01.py`の判定と見比べて修正した=GTとも近い値になる。独立な予測値ではない)。**D-detの合否はGT一致率ではなく、Blind人手目視の「危険な誤り」とM10(R0への影響、Phase 2b)で決める**。M5(ii)(GT中核再現率0.80)の基準値の由来: Lane Bの旧Trialの同一Sonnet系2回の決定論統合(GT)に対する、D-det予備プローブ(委任_01時点で20/25=0.80)の水準を参考値として置いたもの。独立した必要水準ではないため合否には使わず参考表示にする。GT中核25件は偏りがある(central_bank 6、hormuz 4、semiconductor 3、byd 3、openai 3、streaming 4、small_bag 1、space 1、meta 0。上位2テーマで10/25=40%)。
- **A5**: D-plusの各rep出力(選択ID+Storyline)にも同一入力でD-det(Fact本文のみ範囲)を適用し、LLM抽出表記 vs 正規表現抽出表記を概念キーで比較(M8)。
- **A6**: M1に 平均採用件数・AMBIGUOUS Fact採用率・制約付きFact採用率(C1比)を追加。M2の限定表現率に上限(C1の2/18+2以内。定義は下記、ROOTFIX-01時の5/18とは別の固定regexでC1を再計算した値を基準にする)。**NUMBER_RANKS系エラーだけが原因のretry/STOPを別集計**(Trialでは記事停止させず、`selection_failed.json`として記録して次へ進む)。driverにStep6文言のsha assert(D-plusとSeparate-callのPromptに`STEP6_RULES`が逐語で含まれること)を実装済み。
- **A7**: 任意腕 D-plus-min を「役割宣言のみ・number_ranksなし」腕に置換(上表)。
- **U2/U3**: Production採用時のユーザー判断としてRESULT_2A_01.mdの「残るユーザー判断」に記載する。**内容は委任文に具体記載が無く、Opusレビュー原文を本委任は入手していない**ため、本ファイルには推測で書かない(Fableから内容を受領後に追記が必要=RESULT_PACKETで要確認事項として報告)。

## 4. 評価指標と合格基準(決定論スクリプト`b3r2_eval_01.py`、LLM判定なし+人手目視。ベースライン値は既存C1出力の¥0実測)
共通: NFKC正規化。ベースライン=C1(rep1/2 計18出力)。出力は`eval/eval_results_02.json`。
- **M1 Fact選択精度**(D-plus・役割宣言のみ): (a)採用件数3〜5件の出力数(C1=11/18)(b)選択Fact集合のJaccard rep1 vs rep2(C1=0.698)・vs C0(C1=0.649)(c)平均採用件数(C1=3.28、C0=4.67)(d)AMBIGUOUS Fact採用率(C1=3/59=5.1%)(e)制約付きFact採用率(C1=100%。全Factが制約欄を持つため情報量は低い)。
 **合格**: Jaccard(rep1 vs rep2)平均 ≥ 0.55、Jaccard(vs C0)平均 ≥ 0.50、3〜5件の出力数 ≥ C1−2 = 9/18。**保守化の疑い**(合否ではなく報告し、ユーザー判断へ): 平均採用件数が C1−1.0(=2.28)以下、またはAMBIGUOUS採用が0件。
- **M2 Storyline品質**(各腕のStoryline): 決定論=長さ(75〜155字の率)/Fact被覆(Storylineの3字以上内容語が採用Factのclaimに含まれる率)/指示調検出`IMP`(`b3sep_build_01.IMP`)該当出力数/notes共通12字以上の出力数/限定表現率(`LIMIT_RE`: 断定・確定していない・確認されていない・明らかでない・とは限らない・不明・未確定・可能性・とみられ・とされ・と報じ・にとどま・にすぎ、をNFKC後に検索)/Storyline内数字⊆採用Fact(`STORYLINE_NUMBER_NOT_IN_SELECTED_FACTS`)。ベースラインC1: IMP 0/18、notes共通12字以上 1/18、限定表現 2/18、Storyline新数字 4/18(いずれも日付を年なしで書いた等の表記差。人手確認)。
 **合格**: IMP該当 0、notes共通12字以上 ≤ C1+1 = 2、限定表現 ≤ C1+2 = 4/18、Storyline新数字の出力数 ≤ C1+2 = 6/18 かつ人手で「真の新数字」が無い、Blind目視でStorylineが明確に劣る(事実誤り・主題ずれ)テーマが9中2以下。
- **M3 Storylineへの注意文混入 / Fact・注意の分離**: ベースラインのStoryline混入は 0/27(IMP)・notes共通12字以上 3/27 で天井(**効果は判定不能。「悪化させない」確認が中心**と結果に明記する)。D-plus・役割宣言のみでIMP 0かつBlind目視で注意書き由来の文言転記が0。Fact行側(決定論組立)のIMP該当数も報告(構成上0に近いはずだが、claim自体が指示調になる例の有無)。
- **M4 注意書き継承**: 採用Factの`notes_for_writer`/`ambiguity_note`が制約ブロックに文字列完全一致で存在する割合=100%(D-base組立`Dfull`、D-plus・役割宣言のみの選択結果に対して)。
- **M5 中核・周辺ランク精度**: (a)規則整合: LLM宣言roleが規則導出と一致する率(数値単位、D-plus・Sep)。**合格**: ≥90%、かつ「規則上の適格概念が1つ以上ある出力で中核0件(NO_CORE)」=0。**ただし最終roleは規則導出なので、不合格でも方式の成否は決めない(LLMにroleを任せる場合のみ必要な条件として報告)**。(b)kind一致率(報告のみ)。(c)GT比較(参考のみ): Sep(LLM role / LLM表記+規則)とD-detについて、GTの主数字キーで対応付け、対応付け済みの中核/周辺一致率・GT中核の再現率・適合率。(d)**Blind人手目視(D-detの合否)**: 9テーマ×{D-det, Sep rep1, D-plus rep1}のcore集合を腕名を伏せて並べ、「危険な誤り」(Storylineの主役数値が周辺に落ちる、無関係な数値が中核)を数える。D-det合格=危険な誤り 0〜1(9テーマ内)、不合格=3以上。
- **M6 数値欠落 / 新数字 / 取り違え**(D-plus・Sep): 欠落=claim内の正規表現抽出表記のうちLLMのsurfaceが覆わないもの(`MISSING_SURFACES`)。人手で「正規表現の誤検出」を除いて確定する。新数字・取り違え=`SURFACE_NOT_IN_FACT`(数字境界つき)。**合格**: 最終(retry後)の新数字・取り違え=0。欠落(人手確定)≤5%(分母=D-detのFact本文抽出表記数)。retry前の発生は別途報告。
- **M7 Fact ID整合・retry**(D-plus・役割宣言のみ・Sep): UNKNOWN_FACT_ID/FACT_NOT_SELECTED最終0、技術retry出力数 ≤2/18、STOP 0。`NUMBER_RANKS_`系エラーだけが原因のretry/STOPを別集計。output切れ(incomplete)発生数を報告。
- **M8 再現性**: Sep = 同一入力rep1 vs rep2で(fact_id, surface, role)集合のJaccard平均 ≥0.90。D-plus = 両repで共通に採用されたFactについての同集合比較(参考)。D-det = 決定論なので再実行一致を確認(1.0)。A5: 同一入力でLLM抽出 vs 正規表現抽出の概念キーJaccard・LLM限定/正規表現限定の表記一覧(内容分析の入力)。
- **M9 コスト/latency/実装複雑性**: 実測JPY/call(`usage_rows`の入出力tokenと登録単価gpt-6-luna in$0.10/out$0.50, JPY1=$1/160, cachedなし)。**合格**: D-plus・役割宣言のみのper call ≤ JPY0.68(C1実測0.455の1.5倍)、latency平均 ≤65.4秒(C1平均43.6秒の1.5倍)。Sepは1記事あたり追加費用(+1 call分)を実測で報告し、Sonnet注記約JPY15.7/記事と比較。実装複雑性=追加module LOC・追加call数・追加retry経路。
- **M10(E9: R0への影響)**: **本委任では実施しない。Phase 2bで実施**(Lane A C2の編集が落ち着いた後、またはFable指示で別runner経由)。
- **M11 既存注記検査との互換**(JPY0): D-det(C0の採用ID+C0 Storyline)・D-plus rep1・D-det(D-plus rep1の入力)の決定論assembler出力(D-fullのFact行+Storylineに`【事実N】`と`【中核数値】`/`【周辺数値】`を決定論付与+annotation.json相当)に、既存`b3_annotation_check_01.py`を**そのまま**適用(新Checkerは作らない)。合否の対象外(報告): 欠ける欄(`annotator`値・`spec_sha256`・`unmapped_claims`/`annotation_notes`)と、規則の不一致を問題種別で一覧化。
- **M12**: 問題5テーマと正常系4テーマを分けて報告。

## 5. Closeout分類規則(腕別。Production実装はしない。結果を見ての基準変更禁止)
| 腕 | VALIDATED(Trial限定) | REJECTED | USER_DECISION_REQUIRED |
|---|---|---|---|
| **D-det** | M5(d)危険な誤り0〜1、M6相当(抽出の漏れ・誤検出を人手確認し、LLM追加抽出で補えない致命的漏れが無い)、M8再現1.0、M11が`meta`欠落以外PASS。**ただしPhase 2bのM10合格まで最終VALIDATEDは出さない(本委任の分類は`VALIDATED_PENDING_M10`止まり)** | 危険な誤り≥3、またはM11で規則不一致が多数 | 中間。漢数字等の表記漏れの実害判断が必要 |
| **D-plus-single-call** | M1・M2・M3・M4・M6・M7・M9を満たす(M5(a)は報告) | M1またはM2不合格(B3本来性能の悪化)、M6の最終新数字/取り違え>0、M7でSTOP | 一部のみ不合格(M9のみ超過、M5(a)80〜90%、保守化の疑い) |
| **Separate-call(Luna)** | M5(a)・M6・M7・M8を満たし、1記事追加費用(実測)≤JPY1.0 | M6/M8不合格かつ(Sol発動時)Solでも不合格 | Lunaは不合格でSolは合格、または+1 callのlatency/複雑性の価値判断 |
| **役割宣言のみ(Storyline混入対策)** | M1・M2・M3を悪化なく満たす(ベースライン天井のため「悪化させない」確認のみ、効果は判定不能と注記) | M2不合格、または注意文のStoryline転記>0 | 効果が天井で判定不能と明記しユーザー判断へ(推奨はVALIDATED[no-harm]) |
- 複数腕がVALIDATEDなら最も単純な構成(D-det > D-plus > Sep)を第一候補として併記し、**採否はユーザーに戻す**。いずれもVALIDATEDでも`APPROVED_FOR_PRODUCTION`ではない。
- LLM追加抽出(D-plus・Sep)の価値は「D-detが落とした実在の表記をどれだけ拾ったか(人手確定)」と「誤って付けた数」で評価し、価値が小さければD-detに一本化できる旨を結論にする。

## 6. Blind目視(人手が最終)
`eval/blind_sheet_02.md`: Storyline(C0・C1 rep1・D-plus rep1・役割宣言のみ rep1)と core集合(D-det・D-plus rep1・Sep rep1)を乱数IDで混ぜ、対応表は`blind_key_02.json`。目視担当=Claude側(判定時は対応表を開く前に判定を記録)。判定結果は`HUMAN_CHECK_B3R2_01.md`に残す。

## 7. 費用・実行計画・STOP
- cap: 本線(D-plus 18 + Separate-call 18 + 役割宣言のみ 18)累計 **JPY60**。Sol条件付き発動時は全体累計JPY100まで。E9(Phase 2b)は別枠。見積(`ESTIMATE_01.json`の単価式、役割宣言のみは入力+約250token程度でC1並み): low 19 / mid 23 / high 30 程度。
- 実行順(依存関係): ①各腕の最初の1 call(hormuz rep1、3腕並列)→実測で各腕の総額を再見積。**高位見積(D-plus 12.7 / Sep 6.9 / 役割宣言のみ約10)の2倍超ならSTOP**。②残りは各腕内のrepが独立のため複数processで並列(テーマ群を分割、process別ログ→cost_ledger_b3r2_01.jsonlへ合算)。③評価・Blind目視は①の後、実行と並行して準備済み。④E9はPhase 2b。直列化の理由は①の再見積のみ。
- 技術retry: B3系はProduction同一機構(1回のみ、`validation`不整合・JSON不正・API例外が対象)。Sepも同一方針(1回)。**結果を見ての再実行・Prompt修正・追加反復は禁止**。API例外のみで出力が全く得られなかった(`selection_failed.json`のattempts_logが全てerror)runに限り、同一入力で再実行できる(結果の内容を見て判断しない)。
- STOP条件: cap超過見込み / 評価script不具合 / 新LLM工程が必要 / 結果を見てPrompt修正したくなった場合 / 応答model不一致 / 凍結入力・module・本ファイルのsha不一致 / Sol発動が累計JPY100を超える見込み。

## 8. 成果物保存先
`er052_output/b3_rootfix_trial_02/`: runs/<arm>/<theme>/rep<n>/、eval/(eval_results_02.json, blind_sheet_02.md, blind_key_02.json, content_dump_02.json, m11/)、cost_ledger_b3r2_01.jsonl、frozen_b3r2_02.json、PROMPT_DIFF_02.md・PROMPT_DIFF_ROLEONLY_02.md、RESULT_2A_01.md、HUMAN_CHECK_B3R2_01.md、selftest_result_01.json、dry_run/。
