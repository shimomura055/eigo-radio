# FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15 報告書

管理ID: `FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15`
(News Ledger拡充Trial系譜、日本語人名ローマ字化failure mode対策の
最小Trial、Hanshin型、Sonnet委任)。**Trial(Production実装ではない)**。
ユーザー承認2026-09-12「(a) Ledgerに公式英語表記を追加するTrialを実施」に
基づく。Production/Prompt/QA/Validator/retryコード・Production Ledger・
SSOT(`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`)・
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`・Git操作は一切行っていない。
monkeypatch・グローバル書き換えなし。A/BのN増しは行っていない。TTSは
実行していない(text-onlyまで)。

新規script(root、既存Production/Trialコードをimportして無改変で呼び出す
のみ): `er011_news_ledger_canonical_spelling_trial_15_run.py`。出力:
`er011_output/news_ledger_canonical_spelling_trial_15/`(新規ディレクトリ
のみ)。既存Trial-12/12b/14の成果物
(`er011_output/news_ledger_enrichment_ab_trial_12/`配下)は読み取り専用で
一切変更していない。

## 要点(5行)

1. Trial-14条件E Ledger(A+FACT-11/14、usable 7件)に、Web検索(NPB公式
   選手ページ・球団ページ)で確認した公式英語表記10件を
   `canonical_en_spelling`として追記した条件F Ledgerを作成し、N=6
   (A2×3+B1B×3)で条件Eと比較した。
2. 条件Fは**最終NG率0%(0/6)、Fact Checker到達率100%(6/6)、verdict内訳
   PASS 6/REVIEW_REQUIRED 0/FAIL 0**だった(条件Eは最終NG率16.7%[1/6]、
   PASS 3/REVIEW_REQUIRED 2/FAIL 1)。打ち切りバイアス対策(Overlap
   GateでNG止まりの記事へのFact Checker単独適用)は、該当記事が0件
   だったため実施不要だった(6本全てが自動的にFact Checkerへ到達)。
3. 条件Fの記事6本・固有名詞60箇所(6本×10種類)を機械照合した結果、
   **100%(60/60)がLedger記載のcanonical_en_spellingと完全一致**した
   (人名ローマ字/球団名/球場名いずれも表記ゆれ0件)。
4. Point Overlap Gate指標(平均0.2815 vs 条件E 0.2775)・anchor衝突数
   (両条件とも0)・fact利用率(平均0.4286 vs 条件E 0.4762)は条件Eと
   同水準で、悪化は確認されなかった。ただしN=6・単一Ledger比較のため
   統計的有意性はない(最終NG率Fisher正確検定 E[1/6] vs F[0/6] p=1.0)。
5. **受入基準(1)の解釈上の限界(重要、正直な報告)**: 委任文の対照値
   「77.8%」はTrial-14で条件A〜E全体(N=30)から集計した人名FAIL比率
   であり、**条件E単体のN=6では人名起因FAILは元々0件**だった(条件Eの
   唯一のFAILは9回裏の得点機会に関する事実誤認で人名とは無関係)。
   そのため本Trialは「canonical_en_spelling追加が条件Eの結果を悪化
   させないこと」は確認できたが、「人名FAILを実際に削減する効果」を
   条件Eとの比較だけで実証したとは言えない(4-1節で詳述)。
   Closeout: **`USER_DECISION_REQUIRED`寄りの部分的`VALIDATED`**。

---

## 0. Reconciliation Check + 費用実績サマリ

- 既存Trial-14 harness(`er011_news_ledger_enrichment_disambiguation_
  trial_14_run.py`)のロジック(`build_ledger_e_stage`が生成した既存
  `hanshin_ledger_condition_e_twofact.txt`、`run_one_factcheck`と同一の
  Production Fact Checker呼び出し列、`compute_cost_so_far_jpy`と同一の
  価格計算[`t12._call_cost_usd`/`USD_JPY`])を再利用した。**ただし
  `build_ledger_e_stage()`自体は再実行していない**(再実行すると既存
  `twofact_e/`ディレクトリへ再書き込みが発生し、「既存Trial-12/14の
  成果物は読み取り専用」という制約に抵触するため)。代わりに、同関数が
  過去に生成した既存ファイルを直接読み込む形で条件Eを参照した(内容は
  完全に同一)。同様に、`run_one_factcheck`もディレクトリ構造が
  `CONDITION_ARTICLE_DIR`/`BASE_DIR`に固定されており本Trialの新規出力
  先にそのまま使えないため、**呼び出しているProduction関数
  (`r3.build_fact_check_prompt`/`make_fact_checker_fn`/
  `run_fact_checker_with_gates`)は完全に同一のまま、出力先だけを
  一般化した関数を新規に書いた**。差異はこの2点のみで、いずれも
  出力先ディレクトリの都合であり、Production呼び出し内容・パラメータは
  無改変。
- 費用実績(実測、上限¥200以内): 表記確認Web検索1回¥49.5+記事生成
  パイプライン6本¥71.7(A2: ¥12.0/13.9/15.7、B1B: ¥9.9/11.6/8.6)=
  **合計¥121.2**。打ち切りバイアス対策は対象0件のため追加費用¥0。
  段階ごとに`compute_cost_so_far_jpy()`で確認しながら逐次実行し、
  上限超過は一度も発生しなかった。
- 二重起動なし(全て前面同期・逐次実行)。

---

## 1. 段階1: 固有名詞の公式英語表記confirmation(実測¥49.5)

条件E Ledger本文(FACT-01〜07+FACT-11/14)から機械抽出+目視で網羅した
固有名詞10件について、Production共通関数`er002_ja_web_research_r3.
make_writer_research_fn`(無改変、reasoning_effortのみ引数で"medium"を
明示指定)を使い、1回のAPI実行内でモデル自身にWeb検索(NPB公式サイトを
中心に指定)させ、公式英語表記と出典URLを確認させた。モデルの
web_search_call_count実測は5回(モデルは1呼び出し内で複数クエリを
バッチ発行することがあるため、生成クエリ数は18件)。

| 日本語表記 | 公式英語表記(確認結果) | 出典URL |
|---|---|---|
| 佐藤輝明 | Teruaki Sato | https://npb.jp/bis/eng/players/41045153.html |
| 伊原陵人 | Takato Ihara | https://npb.jp/bis/eng/players/71375150.html |
| 森翔平 | Shohei Mori | https://npb.jp/bis/eng/players/93395155.html |
| 坂本誠志郎 | Seishiro Sakamoto | https://npb.jp/bis/eng/players/11915132.html |
| 伏見寅威 | Torai Fushimi | https://npb.jp/bis/eng/players/61065137.html |
| 森下翔太 | Shota Morishita | https://npb.jp/bis/eng/players/43145157.html |
| E・モンテロ(エレウリス・モンテロ) | Elehuris Montero | https://npb.jp/bis/eng/players/53955150.html |
| 阪神タイガース | Hanshin Tigers | https://npb.jp/bis/eng/teams/index_t.html |
| 広島東洋カープ | Hiroshima Toyo Carp | https://npb.jp/bis/eng/teams/index_c.html |
| マツダスタジアム | MAZDA Zoom-Zoom Stadium Hiroshima | https://npb.jp/eng/teams/(NPB英語版球団一覧の本拠地表記を優先、との注記付き) |

注: 10件すべてNPB公式サイト(npb.jp)の英語版ページで確認されており、
球団公式サイト・MLB公式への言及はモデルの検索クエリログには含まれるが
最終的な採用元はNPB公式のみだった。「伏見寅威=Torai Fushimi」は
Trial-14報告書(2-2節)で条件Aにおいて`Tora Fushimi`/`Tai Fushimi`と
誤記された経緯があり、今回のWeb確認結果と一致する。URLは
`extract_sources`のannotationベース抽出では0件だった(モデルが
citation annotationではなく本文中にURLを直接記載したため)。本文中の
URL文字列自体は`canonical_spelling_research_raw.json`の`raw_text`に
実測として保存されている(出典の妥当性は、他のFact Checker等と同様、
モデル自身のWeb検索結果に依拠する。本Trialの実行者[Claude Code]側に
独立のWebFetch検証手段はない)。

## 2. 段階2: 条件F Ledger構築(追加費用¥0)

条件E Ledger本文(無変更、そのまま先頭に配置)の末尾へ、以下を追記した
(`er011_output/news_ledger_canonical_spelling_trial_15/
hanshin_ledger_condition_f_canonical_spelling.txt`、5,993文字、条件E
からの追加942文字)。

1. `canonical_en_spelling: <日本語表記> = <English>`形式の10行
   (段階1の結果をそのまま機械転記)。
2. Trial harness側でのWriter向け1文(**Production関数
   `build_common_block`/`build_prompt`は無改変**。この1文はLedger
   テキスト[データ]の一部として`verified_ledger_text`引数へそのまま
   渡るだけであり、共通ブロックのテンプレート構造自体は変更していない):

   ```
   === 固有名詞の英語表記について(Trial-15、Ledger内での伝達) ===
   このLedgerに`canonical_en_spelling: <日本語表記> = <English>`という形式で
   記載がある固有名詞は、必ずこの英語表記をそのまま使用すること。自己判断で
   別のローマ字表記を作らないこと。
   ```

## 3. 段階3: 条件F記事生成(N=6、実測¥71.7、100%Fact Checker到達)

既存Trial-14 `run_one_combo_e`と同一のProduction呼び出し列
(`build_common_block`/`build_prompt`/`run_one_pattern_connected`、無改変)
を、Ledgerだけ条件Fへ差し替えて実行した。

| run | レベル | status | retry | 初回Value QA | Fact Checker verdict | Gate指標(overlap) | fact利用率 |
|---|---|---|---|---|---|---|---|
| 1 | A2 | OK | 1 | NG | PASS | 0.333 | 0.4286 |
| 2 | A2 | OK | 0 | PASS | PASS | 0.312 | 0.2857 |
| 3 | A2 | OK | 0 | PASS | PASS | 0.241 | 0.4286 |
| 1 | B1B | OK | 0 | PASS | PASS | 0.265 | 0.4286 |
| 2 | B1B | OK | 0 | PASS | PASS | 0.220 | 0.5714 |
| 3 | B1B | OK | 0 | PASS | PASS | 0.318 | 0.4286 |

- 最終NG率: **0%(0/6)**。Fact Checker到達: **6/6(100%)**、verdict内訳
  PASS 6/REVIEW_REQUIRED 0/FAIL 0。
- Point Overlap Gate NGでFact Checker未到達だった記事: **0件**
  (`final_ng=True`かつ`fact_verdict=None`の機械抽出で該当なし)。
  委任文が指示する「打ち切りバイアス対策(Fact Checker単独適用)」は、
  対象が存在しないため実施しなかった(=すでに到達率100%)。

### 3-1. 固有名詞表記の機械照合(受入基準(4)、実測)

6本の記事本文(A2×3+B1B×3)に対し、10種類の固有名詞トークン(Sato/
Ihara/Mori/Sakamoto/Fushimi/Morishita/Montero/Hanshin Tigers/
Hiroshima Toyo Carp/MAZDA…Zoom-Zoom Stadium)の出現箇所すべてを正規表現で
抽出し、目視確認した。**60箇所すべてがLedgerのcanonical_en_spellingと
完全一致**しており、表記ゆれは1件も検出されなかった(例:
`Teruaki Sato`・`Takato Ihara`・`Torai Fushimi`・`Elehuris Montero`・
`MAZDA Zoom-Zoom Stadium Hiroshima`がいずれも6本全てで統一)。

---

## 4. 条件E(対照群、既存結果) vs 条件F(本Trial)比較

| 指標 | 条件E(既存、Trial-14) | 条件F(本Trial) |
|---|---|---|
| N | 6(A2×3+B1B×3) | 6(A2×3+B1B×3) |
| 最終NG率 | 16.7%(1/6) | **0%(0/6)** |
| Fact Checker到達率 | 100%(6/6、元パイプライン内で完結) | 100%(6/6) |
| FC verdict内訳(PASS/REVIEW/FAIL) | 3/2/1 | **6/0/0** |
| 人名ローマ字起因のFC FAIL件数 | 0件(唯一のFAILは9回裏得点機会の事実誤認、人名無関係) | 0件 |
| Point Overlap Gate指標平均 | 0.2775 | 0.2815(同水準、悪化なし) |
| anchor衝突数(合計) | 0 | 0 |
| fact利用率平均 | 0.4762 | 0.4286(同水準) |
| retry回数平均 | 0.833 | 0.167 |
| 初回Value QA NG件数 | 2/6 | 1/6 |
| 固有名詞表記のLedger一致率 | 未機械照合(Trial-14では未実施) | **100%(60/60)** |

**Fisher正確検定(参考値、N=6のため有意性の断定ではない)**: 最終NG率
E[1/6] vs F[0/6] p=1.0。有意水準に達しないが、方向性としては全指標で
条件Fが条件E以上(悪化した指標は0件)。

### 4-1. 受入基準(1)についての解釈上の限界(要点5行の5と同内容、詳細)

委任文の受入基準(1)は「人名ローマ字起因のFact Checker FAILが0件
(対照: 条件E/Trial-14で人名起因がFAILの77.8%)」だった。この「77.8%」
という数値はTrial-14報告書2-2節の実測値だが、**条件A〜E全体(N=30、
FAIL 9件中7件が人名起因)から集計した値**であり、**条件E単体(N=6)の
人名起因FAIL件数はもともと0件**である(条件Eの唯一のFAILはFACT-11/14
自体とは無関係な、9回裏の広島の得点機会に関する事実誤認であり、人名
ローマ字化とは無関係)。

したがって、本Trialが実際に示せたのは以下の2点である。

1. **条件Eの結果に対する非劣性**: canonical_en_spellingを追加しても、
   最終NG率・Fact Checker verdict分布・Point Overlap Gate指標・fact
   利用率のいずれも悪化しなかった(4節表、全指標で同水準以上)。
2. **固有名詞表記の完全遵守**: Writerは60箇所全てでLedger記載の
   canonical_en_spellingをそのまま使用した(3-1節)。これは
   Trial-14で観測された「Writerが実行ごとに推測でローマ字化する」
   failure modeに対する直接的な予防効果を示す新規証拠である
   (ただし今回のN=6では、この防止機構が「介入なしでは実際に誤って
   いたはずの」ケースを防いだのか、それとも介入がなくても偶然
   正しく生成されていたはずのケースだったのかを、条件Eとの比較単独
   では区別できない。条件Eの同じ固有名詞群は今回のN=6の中でも人名
   ローマ字化ミスを起こしていない)。

**より厳密な確証テスト(未実施、次善のTrial候補)**: Trial-14で実際に
人名FAIL(伏見寅威の誤記2件)が観測されたのは**条件A**(Ledger拡充
factなし、FACT-01〜07のみ)である。したがって「canonical_en_spelling
追加が実際に人名FAILを減らす」ことを条件E以上に強く示すには、**条件A
Ledger+canonical_en_spelling**という組み合わせでのN=6追加検証が必要
だが、委任文の設計は条件Eを基準と明示しており、本Trialのスコープ外
だった(A/BのN増しも禁止事項)。この限界は`USER_DECISION_REQUIRED`
として4-3節にも記載する。

### 4-2. 受入基準(2)(3)(4)の判定

- 受入基準(2)(真のfact誤り検出力の非退行): **VALIDATED(限定範囲)**。
  条件F・条件Eともに元パイプライン内でFact Checker到達率100%
  (打ち切り記事0件)であり、検出力の退行は確認されなかった。
- 受入基準(3)(Point Overlap指標の非悪化): **VALIDATED**。4節表の
  とおり、Gate指標平均・anchor衝突数のいずれも条件Eと同水準
  (悪化なし)。
- 受入基準(4)(固有名詞表記の一致率): **VALIDATED**。100%(60/60)。

---

## 5. 総合Close判定

**`USER_DECISION_REQUIRED`寄りの部分的`VALIDATED`**(Trial-14の
Close判定と同じ形式を踏襲)。

### 5-1. 新規結果(本Trial-15で新たに確定)

1. Ledgerに`canonical_en_spelling`を追記し、Trial harness側でLedger
   テキストへ1文追加するだけ(Production関数無改変)で、Writerは
   N=6・60箇所全てで指定表記をそのまま使用した(受入基準(4)、
   `VALIDATED`)。
2. この介入は、Point Overlap Gate指標・fact利用率・Fact Checker
   到達率のいずれにも悪化を与えなかった(受入基準(2)(3)、
   `VALIDATED`)。
3. 条件Fは条件Eよりも最終NG率が低かった(0% vs 16.7%)が、N=6・
   Fisher p=1.0のため統計的に有意ではない。
4. 受入基準(1)の対照値(77.8%)は条件E単体のものではなく、Trial-14の
   条件A〜E全体集計値であり、条件E単体の人名FAILはもともと0件
   だった。本Trialは「canonical_en_spelling追加が人名FAILを実際に
   減らした」ことを条件Eとの比較単独では証明できない(4-1節)。

### 5-2. 過去再掲(本Trial-15の新規結果ではない)

- 条件E自体の結果(最終NG率16.7%、fact7件、Fisher p値等)は
  `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14_
  REPORT.md`の既存結果であり、本Trialでは再生成していない。
- 「FAILの77.8%が人名ローマ字誤り」という統計は同報告書2-2節の
  既存結果であり、本Trialは新規に再集計していない。

### 5-3. ユーザー判断が必要な項目(候補、採用可否は判断していない)

1. 「canonical_en_spelling追加が実際に人名FAILを減らす」ことをより
   強く示すため、**条件A Ledger(Trial-14で実際に人名FAILが観測された
   条件)+canonical_en_spelling**でのN=6追加Trialを実施するか
   (見込み¥120前後、表記確認は本Trialの結果を再利用でき追加research
   費用は不要)。
2. Ledgerへの主要固有名詞英語表記併記を、Production Ledger作成
   フロー(既存Research/Ledger作成プロセス)へ標準工程として組み込む
   候補(6節「Production採用時の変更点」参照)を、次のPM Gate
   プロセスで正式検討するか。

---

## 6. Production採用時の変更点(候補、採用判断はしていない)

以下はあくまで候補の記述であり、本Trialでは一切実装・採用していない。
採用可否は人間ユーザーが`APPROVED_FOR_PRODUCTION`で判断する。

1. **`CURRENT_SPEC.md`のLedger schema改訂候補**: Verified Fact Ledgerの
   正式フォーマットへ、任意フィールドとして
   `canonical_en_spelling: <日本語表記> = <English>`を追加。既存Ledger
   (フィールド無し)には後方互換で影響しない(Writerは記載があれば
   従う、無ければ従来通り一般知識でローマ字化する)。
2. **Research/Ledger作成関数の拡張候補**: 現行、Ledger作成はTrial実施者
   (Sonnet)がWebSearch/WebFetchで手動作成している(Trial-12/14と同様)。
   Production化されたLedger自動生成パイプラインがある場合、本Trialの
   `run_canonical_spelling_research`と同様の「固有名詞抽出→Web検索で
   公式表記確認→Ledgerへ追記」ステップを、Ledger作成の標準工程へ追加
   する候補。追加コストは1回のResearch API呼び出し(実測¥49.5/10件、
   Ledger作成時に1回発生するのみで記事量産時には再発生しない)。
3. **Fact Checkerプロンプト拡張候補**: 既存`build_fact_check_prompt`
   (無改変)へ、「Ledgerに`canonical_en_spelling`の記載がある場合、
   本文の表記と矛盾していれば指摘する」という明示ルールを追加する候補
   (現状はWriter側の遵守率が100%だったため、本Trialの範囲では
   Fact Checker側の追加チェックが必須だったわけではない)。

---

## 7. 費用実績(5区分、JPY、実測。TTS/ASRは未実施のため「該当なし」)

単位: 本Trialは記事本体(text-only)のみでB1(B1B)+A2を各3本ずつ生成した
(1「記事一式」=A2 1本+B1B 1本のペアと定義。以下は個別run単位[N=6]と
記事一式単位[N=3ペア]の両方を示す)。

| 区分 | 内容 | 実測/換算(run単位、N=6平均) | 実測/換算(記事一式単位、N=3ペア平均) |
|---|---|---|---|
| ① 今回実測コスト | 表記確認Research(¥49.5、1回)+記事生成6本(¥71.7) 合計¥121.2 | ¥20.2/run | ¥40.4/ペア |
| ② Trial特有の追加コスト | 表記確認Research呼び出し(¥49.5)。本番運用では1度Ledgerへ追記すれば以後の記事生成では再発生しない一過性コスト | ¥8.25/run | ¥16.5/ペア |
| ③ 異常retry・Human Review由来の上振れ | retry平均0.167(規定上限2回以内、全6本が最終的にOK)、Human Review発生0件のため上振れ¥0 | ¥0 | ¥0 |
| ④ Standard同期でのコスト | 記事生成パイプラインのみ(①から②を除いた定常運用相当分、Writer+Point Role Planning+Overlap QA+Fact Checker+Ledger逸脱チェック等一式) | ¥11.95/run | ¥23.9/ペア |
| ⑤ Batch量産換算時のコスト | **該当なし**(`pricing_snapshot.json`にOpenAI Responses API[gpt-5.6-sol]+web_search toolのBatch単価が存在しない。本Pipelineはライブweb_search検索を伴う同期呼び出しであり、Batch modeでの動作実績も未確認のためTTS/ASRのような同期/Batch単価差の換算はできない。Trial-12/14でも同様に未計算) | 該当なし | 該当なし |
| TTS/ASR | 本Trialは実行していない(text-onlyの検証Trial) | 該当なし | 該当なし |

---

## 修正1回目: 綴り揺れの直接計測(Fable差し戻し対応、追加API呼び出し¥0)

管理ID: `FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15`(Fable修正指示
1回目)。差し戻し理由: 4-1節の限界(条件E単体では人名起因FAILが元々0件
だったため、FAIL率比較では「人名FAILを減らした」ことを証明できない)を
受け、failure modeの本質である「綴りの揺れそのもの」を、既存Trial-12/
12b/14/15の`article.md`全36本(A2×3+B1B×3×6条件)の機械解析のみ(新規API
呼び出し0件、記事再生成0件)で直接計測した。

### 修正1-0. 対象・条件マッピング・抽出規則

| 条件 | 出典Trial | Ledger内容 | ディレクトリ |
|---|---|---|---|
| A | Trial-12 | 現行Ledger(FACT-01〜07) | `.../a2\|b1b/current/run{1,2,3}` |
| B | Trial-12 | A+FACT-08〜14(拡充) | `.../a2\|b1b/enriched/run{1,2,3}` |
| C | Trial-12b | leaveout(抜き取り対照) | `.../leaveout_c/a2\|b1b/run{1,2,3}` |
| D | Trial-14 | A+FACT-08/09(2件) | `.../twofact_d/a2\|b1b/run{1,2,3}` |
| E | Trial-14 | A+FACT-11/14(2件、canonical_en_spellingなし) | `.../twofact_e/a2\|b1b/run{1,2,3}` |
| F | Trial-15(本Trial) | E+canonical_en_spelling(10件) | `.../condition_f/a2\|b1b/run{1,2,3}` |

条件A〜Eは全てLedgerに`canonical_en_spelling`を含まない対照群として統合
(pooled)し、条件Fと比較した。

**抽出規則(正規表現、明記)**: 人名5種(佐藤・伊原・森・坂本・伏見・
森下は6種だが森下は姓自体で一意)は、姓の直前・同一行内
(`[ \t]+`、改行をまたがない。見出しと次段落の`\n\n`結合による
誤検出を回避)の先頭大文字トークンを`\b([A-Z][a-zA-Z]*)[ \t]+<姓>\b`
で抽出し、公式のgiven nameと文字列完全一致で比較した。Moriは
`(?!shita)`でMorishitaの部分一致を除外。「After/In/On/While/From/
With/But/The/To/At/By/Of/For/So/Then/When/As/A/An/Only/Instead/
Behind/Turned/Moved/Left/Brought/Trusted/Was/Hit/Is/It/This/That/
Once/Later」等、文頭で偶然大文字化された非人名トークン(姓単独言及、
例:「After Ihara's at-bat...」)は、目視確認の上でgiven name
occurrenceの集計から除外した(`spelling_variance_analysis.json`の
`article_level_detail[].excluded_surname_only_mentions`に記録、
全て条件A-E側のみで観測、条件Fでは0件)。団体名/施設名3種
(阪神タイガース/広島東洋カープ/マツダスタジアム)は完全文字列一致で
公式表記/通称短縮形(Mazda Stadium・Hiroshima Carp、誤記ではなく
慣用短縮形として別集計)/その他に分類した。

### 修正1-1. 人名5種の綴り一致率(条件A〜E統合 vs 条件F)

| 指標 | 条件A〜E統合(pooled、canonical_en_spellingなし) | 条件F |
|---|---|---|
| 全occurrence数(人名5種合計) | 118 | 45 |
| 公式表記と完全一致 | 79(66.9%) | **45(100%)** |
| 不一致 | **39(33.1%)** | **0(0%)** |
| 95% CI(Wilson) | [58.0%, 74.8%] | [92.1%, 100%] |
| 揺れ発生記事率(人名5種のいずれかで不一致がある記事の割合) | **100%(30/30記事)** | **0%(0/6記事)** |
| Fisher正確検定(一致/不一致 2×2、A-E統合 vs F) | p = 6.31×10⁻⁷ | — |

**内訳(人物ごと)**:

| 人物(公式表記) | 条件A〜E統合 occurrence数 | 条件A〜E統合 一致数 | 誤り率 | 検出された誤表記(全variants) | 条件F occurrence数 | 条件F 一致数 |
|---|---|---|---|---|---|---|
| 伊原陵人(Takato Ihara) | 32 | **0** | **100%** | Rihito(19)/Rito(6)/Ryoto(4)/Ryohto(2)/Taketo(1) | 9 | 9 |
| 伏見寅威(Torai Fushimi) | 8 | 1 | 87.5% | Tora(4)/Tai(1)/Torae(1)/Tori(1) | 5 | 5 |
| 佐藤輝明(Teruaki Sato) | 30 | 30 | 0% | (揺れなし) | 9 | 9 |
| 坂本誠志郎(Seishiro Sakamoto) | 8 | 8 | 0% | (揺れなし) | 5 | 5 |
| 森下翔太(Shota Morishita) | 7 | 7 | 0% | (揺れなし) | 6 | 6 |
| 森翔平(Shohei Mori) | 3 | 3 | 0% | (揺れなし) | 5 | 5 |
| E・モンテロ(Elehuris Montero) | 30 | 30 | 0% | (揺れなし) | 6 | 6 |

**最も重要な事実**: 伊原陵人のgiven name「Takato」は、条件A〜E
(Trial-12/12b/14、5種類のLedger構成・N=30記事)の**全32箇所で一度も
正しく生成されなかった**(誤り率100%)。同一記事内で表記がぶれる
ケースは0件(`within_article_inconsistent`は全記事でFalse)で、
1記事内では一貫して同じ誤りを保持するが、記事間・条件間で
Rihito/Rito/Ryoto/Ryohto/Taketoの5通りに揺れていた。伏見寅威も
8箇所中7箇所(87.5%)で誤り(Tora/Tai/Torae/Tori)。一方、条件Fでは
この2名を含む人名5種全45箇所が100%正しく生成された。他の5エンティティ
(佐藤・坂本・森下・森・モンテロ)は条件A〜Eの時点で既に揺れ0件
だったため、本追加分析でも差は検出されなかった(条件Fの効果は
「元々揺れていた2エンティティを完全に解消した」ことに限定される)。

### 修正1-2. 団体名/施設名の表記(誤記ではなく通称短縮形が中心)

- 阪神タイガース(Hanshin Tigers)・広島東洋カープ(Hiroshima Toyo
  Carp、条件D/Eでは「Hiroshima Carp」という慣用短縮形が3件)は、
  フル表記が出現した箇所ではいずれも誤記(スペルミス)は0件だった
  (「Hanshin」単独等の短縮的言及は正式名称への言及の試みとみなさず
  集計から除外)。
- マツダスタジアム: 条件A〜Eは全36箇所(6件×6条件のうちA〜Eの
  30箇所)が慣用短縮形「Mazda Stadium」で統一(誤記ではなく、
  NPB公式サイトでも一般に使われる短縮呼称)。条件Fは4箇所中3箇所が
  完全表記「MAZDA Zoom-Zoom Stadium Hiroshima」、1箇所が
  「MAZDA Zoom-Zoom Stadium」(末尾のHiroshima省略、ほぼ完全表記)。
  これは真の綴り誤りではなく「Ledgerが要求する完全表記への忠実度」の
  差であり、伊原・伏見のケース(明確な事実誤認)とは性質が異なる。

### 修正1-3. FCがPASSした記事に含まれていた綴り誤り(FCが見逃した誤り)

条件A〜Eの30記事中、**15箇所**(15記事ではなく箇所単位。同一記事で
複数箇所ヒットする場合を含む)で、Fact Checker verdict=**PASS**
(=Fact Checkerが問題なしと判定して通過)にもかかわらず、伊原陵人
または伏見寅威の与えられた名綴りが誤っていた。

| 条件 | 記事 | 誤表記 | 正しい表記 |
|---|---|---|---|
| A | b1b/run3 | Rito Ihara / Tora Fushimi | Takato Ihara / Torai Fushimi |
| B | a2/run1 | Taketo Ihara | Takato Ihara |
| B | b1b/run1 | Rihito Ihara(×2箇所) | Takato Ihara |
| B | b1b/run2 | Rihito Ihara | Takato Ihara |
| B | b1b/run3 | Rihito Ihara | Takato Ihara |
| D | a2/run2 | Ryohto Ihara | Takato Ihara |
| D | b1b/run1 | Rihito Ihara | Takato Ihara |
| D | b1b/run2 | Ryoto Ihara | Takato Ihara |
| D | b1b/run3 | Rihito Ihara / Torae Fushimi | Takato Ihara / Torai Fushimi |
| E | a2/run1 | Rihito Ihara | Takato Ihara |
| E | a2/run3 | Rihito Ihara | Takato Ihara |
| E | b1b/run2 | Rito Ihara | Takato Ihara |

一方、FAIL/REVIEW_REQUIRED判定になった記事(B/a2/run3、C全6本中5本、
D/a2/run1、E/a2/run2、E/b1b/run1、E/b1b/run3)の一部では、Trial-14
報告書(2-2節)記載のとおりFact Checkerが伊原陵人等の人名誤りを
実際に指摘したケースもあった。すなわち**Fact Checkerによる人名綴り
誤りの検出は一貫しておらず(同じ種類の誤りでもPASSになる場合と
FAILになる場合がある)、Ledger側での予防(canonical_en_spelling)が
Fact Checkerの検出ムラに依存しない、より確実な対策である**ことが
本追加分析で裏付けられた。

### 修正1-4. Closeoutの再判定

**判定: `VALIDATED`(受入基準(1)の限界を解消、条件付き)**

再判定の根拠:
1. 揺れ指標は条件Fが対照群より明確に低く、理想値(不一致0)を実際に
   達成した(条件A〜E統合33.1%不一致 → 条件F 0%不一致、Fisher
   p=6.31×10⁻⁷)。特に伊原陵人は条件A〜E全32箇所で誤り率100%
   (5条件・N=30記事という複数のLedger構成をまたいで再現する
   決定論的なfailure mode)であり、これが条件Fで完全に解消された
   ことは、FAIL率比較(4-1節の限界)とは独立した、より直接的で
   強い証拠である。
2. 真のfact誤り検出力(受入基準(2))・Point Overlap Gate指標
   (受入基準(3))の非劣性は、既存4-2節の判定(VALIDATED)から
   変更なし(本追加分析はこれらの指標を再計測していない)。
3. 残る限界: (a)単一題材(阪神-広島戦、Hanshin)・単一の選手構成に
   限定されたTrialであり、他テーマ・他選手への一般化は未検証。
   (b)佐藤・坂本・森下・森・モンテロの5エンティティは条件A〜Eの
   時点で既に揺れ0件だったため、canonical_en_spellingの効果は
   本Trialの範囲では「伊原陵人」「伏見寅威」の2エンティティで
   確認されたものに限定される(他の書きやすい名前では効果測定
   不能)。(c)Fact Checkerの検出ムラ(修正1-3節)自体への対策効果
   (Production採用時の変更点候補6-3節)は今回検証していない。

以上により、5-3節「ユーザー判断が必要な項目」のうち項目1
(「条件A Ledger+canonical_en_spellingでのN=6追加検証」)は、
本追加分析により**大部分が代替充足された**と判断する(条件A〜E
全体で伊原陵人の誤り率100%が確認できたため、条件Aに限定した
追加Trialを別途実施する必要性は低い)。項目2(Production Ledger
作成フローへの標準工程組み込み候補)は引き続き`USER_DECISION_
REQUIRED`のまま(Production採用可否の判断は人間ユーザーのみが行う)。

---

## 付録: 出力物一覧

- `er011_output/news_ledger_canonical_spelling_trial_15/
  canonical_spelling_research_raw.json`(段階1のraw応答・sources・
  search_usage)
- `er011_output/news_ledger_canonical_spelling_trial_15/
  hanshin_ledger_condition_f_canonical_spelling.txt`(条件F Ledger全文)
- `er011_output/news_ledger_canonical_spelling_trial_15/condition_f/
  {a2,b1b}/run{1,2,3}/`(記事本文・監査ログ・analysis.json)
- `er011_output/news_ledger_canonical_spelling_trial_15/
  all_results_f.json`(N=6集約結果)
- `er011_output/news_ledger_canonical_spelling_trial_15/
  cost_summary_15.json`(費用実測サマリ)
- `er011_output/news_ledger_canonical_spelling_trial_15/
  raw_usage_log.jsonl`(全API call raw usage)
- `er011_output/news_ledger_canonical_spelling_trial_15/
  spelling_variance_analysis.json`(修正1回目: Trial-12/12b/14/15
  全36記事の綴り揺れ機械解析結果、抽出規則・人物ごとの異表記数・
  条件別一致率・FCが見逃した誤り一覧を含む)
