# EVAL_E2E_01: FACTLOCK-ASTRA-E2E-TRIAL-01 評価文書(委任_15、2026-10-09、MEASURED・ラベル暫定・Fable判定待ち)

位置づけ: Trial/DEV(Production変更なし)。VALIDATED/APPROVED_FOR_PRODUCTIONは宣言しない。判定線の**最終判定は空欄(Fableが記入)**で、本書は事前登録(`PREREGISTRATION_01.md` v2.2+事後注記)の線への**機械的な当てはめ**のみを書く。
ラベル(`labels_w{1,2,3}.jsonl`)は**Sonnet 3 workerの暫定推測**であり、ユーザー確認前。API支出¥0(本委任)。数値の出所: 集計=`runs/final_aggregate/aggregate_final.json`、ラベル=`eval/labels_merged.jsonl`(統合規則は`merge_labels_01.py`冒頭)、機械照合=`eval/judge_table_01.py`→`eval/judge_table_01.json`。
読み替え(事前登録7節の事後注記どおり): 対の数 n=9(旧4+新5、inbound_tourismは注記不能で除外)、予定run各腕18、記事単位の分母9。比率・条件(0.75/1.25、過半数、6対以上、3記事差以上)は変更なし。

## 1. 到達状態と費用

### 1-1. 到達状態(成果物の有無で再確認した値。`judge_table_01.json` reach)
| テーマ | 層 | 新腕 | 旧腕 |
|---|---|---|---|
| meta | 旧4 | 完走(Adv/Std出荷) | **JA STOP**(R2 attempt2) |
| hormuz | 旧4 | B1 1回→完走 | **JA STOP**(original) |
| space_weapons | 旧4 | B1 1回→Adv出荷(Rewrite)、**Std EN STOP** | 完走 |
| small_bag | 旧4 | 完走 | 案B1回→Adv出荷、**Std EN STOP** |
| byd_recall | 新5 | Adv出荷(Rewrite)、**Std EN STOP** | 案B1回→Adv出荷、**Std EN STOP** |
| central_bank_mortgage | 新5 | **JA R0 STOP** | 完走 |
| openai_copyright | 新5 | B1(Trial 3回目)後も**Adv EN STOP** | 案B1回→完走(Std Rewrite) |
| semiconductor_earnings | 新5 | JA完了後、B1拒否(Trial上限3/3)→**Adv EN STOP** | 完走(R2 FC MAJOR3→must-fix、Std Rewrite) |
| streaming_price | 新5 | 完走 | 完走(Std Rewrite) |

- JA完走記事: 新8/9、旧7/9。EN Advanced出荷: 新6、旧7。EN Standard出荷: 新4、旧5。Checker run完了: 新10、旧12(予定各18)。Human Review到達 0/0。
- **集計scriptとの食い違い(訂正して使用、3-4節)**: `AGGREGATE.md`は旧腕のEN STOP 2件を『Advanced』欄に入れているが、成果物とrunログではsmall_bag旧・byd_recall旧とも**Standard**でSTOP(Advanced本文は出荷済み)。以後の表は成果物ベース。

### 1-2. 費用(raw=登録単価xトークン、guard=Astra分x1.5。請求照合は未実施)
| 項目 | 値 | 備考 |
|---|---|---|
| 本台帳合計(G1+G2) | raw ¥459.04 / guard ¥625.89 | 台帳ts 2026-10-09 09:32:56〜11:14:40 |
| Stage R(研究・台帳・B3)込み Trial累計 | raw ¥638.03(Stage R raw ¥178.99) | guard換算の概算約¥805(Stage Rをraw加算、未確認の概算)。ユーザー上限¥1,000内 |
| 腕別 | 新 raw ¥395.12(guard ¥561.96) / 旧 ¥63.92 | |
| 段別(新) | Astra R1 ¥173.19 / R2 ¥163.52(計¥336.71=総raw73%) / R0 ¥7.84 / (ii) ¥4.81 / EN Adv ¥6.40 / EN Std ¥5.43 / 影 ¥2.83 / Checker Adv ¥20.04 / Std ¥11.05 | |
| 段別(旧) | JA ¥12.08 / Adv ¥9.63 / Std ¥1.98 / (ii) ¥3.46 / 影 ¥2.65 / Checker Adv ¥15.61 / Std ¥18.52 | |
| B1回復の再支出(推定) | raw ¥102.99(guard ¥148.42): hormuz 33.52 / space 36.24 / openai 33.23 | 同テーマ新腕の再実行段の合算(推定) |
| Astra実測(R1+R2を1生成) | **raw ¥30.6/生成**、guard ¥45.8(Astra生成11回=完走8記事+B1再生成3回) | 設計見積¥27〜34(DESIGN 5-2)の範囲内 |
| 1記事あたり(全9記事平均) | 新 raw ¥43.9 / 旧 ¥7.1 | STOP早期終了(新central・旧meta/hormuz)を含む |
| 1記事あたり(JA完走記事のみ) | 新 raw ¥49.2(B1再支出除外で¥36.3)(8記事) / 旧 ¥8.7(7記事) | 見積: 新約¥42(B1含まず)/ 旧約¥9.2 |
| 1記事あたり(新旧ともJA完走の6テーマ) | 新 ¥46.4 / 旧 ¥9.1 | space・byd・small・openai・semi・streaming |
| Checker 1 run | 新 ¥3.11 / 旧 ¥2.84(REPORT §81の新仕様9 runは¥3.50) | |

### 1-3. 所要時間
台帳の最初〜最後のtsは 2026-10-09 09:32:56〜11:14:40(約1時間42分、停止・再開・環境事故の待ち時間を含む)。最終ラウンドの再起動後(10:34:31〜11:14:40)は約40分(最大5プロセス)。委任_14のラベル付けは3 worker並列(所要の個別記録なし)。

## 2. 事前登録の判定線 機械照合表

**「機械判定」=事前登録の線への機械的な当てはめ。Fable最終判定は空欄。** 新=新仕様腕(Fact Lock+Astra+B1+M1/M3+B3注記版)、旧=旧仕様腕(Production相当)。層別: 旧4=meta/hormuz/space_weapons/small_bag、新5=byd/central/openai/semiconductor/streaming。

### 2-A. 評価対象(1) Writer(JA段) — 記述指標が中心(判定に入れない)
| 指標 | 定義 | 新腕 | 旧腕 | 差 | 判定線 | 機械判定 | 層別 旧4(新/旧) | 層別 新5(新/旧) | Fable最終判定 |
|---|---|---|---|---|---|---|---|---|---|
| JA R2 FC(Luna) MAJOR数 | 全記事R2のFC MAJOR合計 | 0(JA完走8記事) | 4(7記事: semiconductor3+meta1) | -4 | 記述指標(総合に入れない) | 記述のみ | 0 / 1 | 0 / 3 | |
| JA R2 FC MINOR | 同 | 0 | 0 | 0 | 記述指標 | 記述のみ | 0 / 0 | 0 / 0 | |
| 台帳外数値・記号Gate | 決定論 | 0 | 0 | 0 | 記述指標 | 記述のみ | 0 / 0 | 0 / 0 | |
| 新規具体主張(ii) 最終JA | 検出器件数 | 2 | 15 | -13 | 記述指標 | 記述のみ | 1 / 5 | 1 / 10 | |
| 　(ii) R0比の増減 | 最終-R0 | 0 | +7 | | 記述指標 | 記述のみ | | | |
| 　注意 | 旧腕small_bag(3)・byd(4)の(ii)は案B前本文の値(最終JAでない)。最終JA由来に限ると新2 / 旧8 | | | | | | | | |
| 初回(回復前)JA_RECHECK率 | EN段のJA_RECHECK捕捉、分母9 | 4/9(hormuz,space,openai,semi) | 3/9(small,byd,openai) | +1 | 記述指標 | 記述のみ | 2 / 1 | 2 / 2 | |
| JA字数(JA完走記事の平均) | | 931(8本) | 740(7本) | +191 | 記述指標 | 記述のみ | | | |
| 面白さpairwise | 未実施(人間確認が優先) | - | - | - | 副指標 | 未測定 | | | |
| 軽微(JA列)→ 2-Cの2-2を参照 | | | | | | | | | |

### 2-B. 評価対象(2) 翻訳仕様(EN段、M1/M3) — 事前登録2-4
| 指標 | 定義 | 新腕 | 旧腕 | 差 | 判定線 | 機械判定 | 層別 旧4(新/旧) | 層別 新5(新/旧) | Fable最終判定 |
|---|---|---|---|---|---|---|---|---|---|
| EN Advanced STOP率 | STOP記事÷9 | 2/9=0.22(openai,semi) | 0/9=0.00 | +0.22 | 良化: 新≦旧-0.3(3記事差)かつ翻訳由来MAJOR/記事≦旧x0.75かつ軽微EN列が悪化でない。悪化: 新≧旧+0.3かつ翻訳由来MAJOR/記事≧旧x1.25 | **同等**(差2記事<3記事。translation由来MAJORは両腕0) | 0 / 0 | 2 / 0 | |
| EN Standard STOP率 | 同 | 2/9=0.22(space,byd) | 2/9=0.22(small,byd) | 0 | 同 | **同等**(translation由来MAJOR/記事は新0.22 対 旧0.00だが、STOP率の差が0なので片方のみ=記述指標) | 1 / 1 | 1 / 1 | |
| EN初回MAJOR(Adv) | 件数(集計script=回復後の最終runのみ) | 2(全てja_source) | 0 | +2 | 記述指標 | 記述のみ | 0 / 0 | 2 / 0 | |
| EN初回MAJOR(Std) | 件数 | 2(全てtranslation) | 3(全てja_source) | -1 | 記述指標 | 記述のみ | 1 / 2 | 1 / 1 | |
| EN Adv 初回(回復前)MAJOR【ラベル行から】 | B1/案B前の本文を含む。集計scriptの値は回復後の最終runのみ | 4(hormuz ja_source、space translation[要約]、openai ja_source、semi ja_source) | 5(small ja_source+translation[要約]、byd ja_source+translation[要約]、openai ja_source) | | 記述指標 | 記述のみ。回復前を含めるとAdvの翻訳由来MAJORは新1/旧2で、旧が少なくない | | | |
| 翻訳由来MAJOR/記事(Adv, Std) | | Adv 0.00 / Std 0.22 | 0.00 / 0.00 | | 判定線の一部 | 上記に含む | | | |
| M1(a) 影の対照(要約入替の再検査) | 腕内で他方の要約規則を当てた判定 | 新6件中、旧入力要約に替えるとLEDGER_DEVIATIONになるもの1(space) | 旧7件中、M1入力要約に替えるとDEVIATION 1(byd) | | 記述のみ(検定しない) | 記述のみ | | | |
| M1(b) 発火 | `[OPEN243_M1]`のrunログ数 | **1**(space新Adv、B1前の本文) | 0 | | 記述のみ | 記述のみ。**Standardは未実装(REPORT §110)**。M1の効果はStandardで未測定 | 1 / 0 | 0 / 0 | |
| M1 解決率 | 発火分の要約MAJOR解消 | 1/1(B1前の要約は解消。**B1後の最終Adv要約に同型の不在断定が再出現**) | - | | 記述のみ | 腕比較をM1単独の効果と書かない | | | |
| M3保護claim | 新: changed_actor保護 | 6(byd 5, small_bag 1) | 影として5(旧腕で保護されたはずの除外claim、全て台帳一致) | | 記述のみ | 保護の便益は確認できず(3 workerとも0件と報告)。コストは未確認 | 1 / 0 | 5 / 5 | |

### 2-C. 評価対象(3) Checker・重大・軽微・複合 — 事前登録2-1/2-2/2-5/2-6
| 指標 | 定義 | 新腕 | 旧腕 | 差 | 判定線 | 機械判定 | 層別 旧4(新/旧) | 層別 新5(新/旧) | Fable最終判定 |
|---|---|---|---|---|---|---|---|---|---|
| **2-1 重大(出荷最終本文の残存)** | 盲検ラベル=重大 | 0 | 0 | 0 | 良化: 新0かつ新<旧。両腕の総数が2件以下は判定不能(床効果)。新>0かつ同テーマ旧0は要確認フラグ | **判定不能(床効果)。要確認フラグ: なし** | 0 / 0 | 0 / 0 | |
| 　重大ラベルの所在 | 重大と付いた行 | meta旧のrejected本文1件(+STOP妥当性行)のみ。出荷本文なし | | | | | | | |
| 　境界例(重大/軽微) | 3-3節に11件 | 出荷本文に残る境界: B-02,B-05(,B-04) | B-03,B-11 | | 参考 | **回答次第でフラグが変わる**: B-05(byd新)が重大ならフラグ。B-02/B-03(space両腕)は両腕に同型でフラグにならない | | | |
| **2-2 軽微 JA列** | 出荷最終本文の残存(件/記事、claim単位、JA完走記事) | 5件(8記事、対のある6テーマ分5) | 9件(7記事、対6テーマ分9) | 対6テーマの平均 0.83 対 1.50(比0.56) | 良化: 新平均≦旧x0.75かつ新少ない対が同点除き過半数かつ6対以上。悪化: 新平均≧旧x1.25かつ新多い対6対以上 | **同等**(平均比は良化線を満たすが、新が少ない対は3対/4対(同点2を除く)で『6対以上』に届かない。総件数14>5で床効果ではない) | 1 / 4 | 4 / 5 | |
| **2-2 軽微 EN Advanced列** | 出荷EN Adv本文の残存(JA由来は二重計上しない) | 3件(出荷6) | 3件(出荷7) | 対のある4テーマ: 3 対 3 | 同上 | **同等**(平均比1.00) | 1 / 1 | 2 / 2 | |
| **2-2 軽微 EN Standard列** | 同(EN Std) | 5件(出荷4) | 4件(出荷5) | 対のあるテーマは streaming の1対のみ(2 対 1) | 同上 | **判定不能(床効果: 対のある対の総件数5以下)**。出荷本文単位の総数は新5/4本対旧4/5本 | 3 / 1 | 2 / 3 | |
| 　軽微の別枠 | R0冒頭復唱が最終JAに残る | 0 | 0 | 0 | 件数のみ | 件数のみ | | | |
| **2-5 Rewrite率** | Rewrite発生run÷18 | 2/18=0.111 | 3/18=0.167 | -0.056 | 良化: 新≦旧-0.15(3 run差以上)かつ不要Rewriteが増えていない。悪化: 新≧旧+0.15 | **同等**(差<0.15) | 1/8 vs 0/8(+0.125) | 1/10 vs 3/10(-0.20) | |
| 　不要Rewrite(併記) | ラベル上不要 | 1〜2件(byd Adv: 比喩ジョーク削除=不要。space Adv: 単複差=基準次第) | 6〜7件(小数点断片起因6/7、うち軽微劣化2) | 新≦旧(増えていない) | Rewrite率の条件 | 条件は満たすが、Rewrite率が良化線に届かないため良化にならない | | | |
| **2-5 Human Review率** | 出口BLOCKING→Human Review到達run÷18 | 0 | 0 | 0 | 総イベント2件以下は判定不能 | **判定不能(床効果)** | 0 / 0 | 0 / 0 | |
| **2-5 人手介入必要率(複合主指標)** | (JA STOP[記事=2 run]+影STOP+EN STOP[1 run]+Human Review)÷18 | 6/18=0.333(JA STOP 2[central]、EN STOP 4) | 6/18=0.333(JA STOP 4[meta,hormuz]、EN STOP 2) | 0 | 良化: 新≦旧-0.15。悪化: 新≧旧+0.15。総イベント4件以下は判定不能 | **同等**。感度: Adv STOPでStd runも失われるとみなす場合、新8(0.444)対旧6(0.333)=差+0.111で線(+0.15)未満=同等のまま | 1/8=0.125 vs 5/8=0.625(-0.50) | 5/10=0.50 vs 1/10=0.10(+0.40) | |
| 　層別の逆向き | 旧4では新が少なく、新5では新が多い | | | | | 層別(参考)の機械当てはめは**反対方向**(旧4=良化方向、新5=悪化方向)。全体では相殺 | | | |
| 影STOP(R2後FC MAJOR) | shadow_stop | 0 | 0 | 0 | 記述指標 | 記述のみ | | | |
| B1回復(新のみ) | 発動/成功/拒否 | 発動3(hormuz,space,openai)/**完走1(hormuz)**/拒否2(semiconductor=Trial上限、openaiの2回目=1記事1回上限) | 案B(旧)は発動3(small,byd,openai)/成功1(openai) | | 記述指標 | 記述のみ(B1の純効果は疑問、4-3節) | | | |
| Checker出力の参考(新/旧 run完了) | A 初回候補(延べ) | 82(10 run) | 106(12 run) | | 記述のみ | 記述のみ | 54 / 30 | 28 / 76 | |
| 費用差(判定外) | raw | ¥395.12 | ¥63.92 | +¥331.20(1記事 ¥43.9 対 ¥7.1) | 総合判定の外で併記 | 差額のみ | | | |

### 2-D. 総合(事前登録2-6、参考の機械当てはめ)
- 判定指標群={2-2 JA列、2-2 EN列、2-4(Adv・Std)、Rewrite率、人手介入必要率}。機械当てはめ: JA列=同等、EN列(Adv+Std合算の対5対)=同等(新5件対旧4件)、2-4 Adv=同等、2-4 Std=同等、Rewrite率=同等、人手介入必要率=同等。**良化0・悪化0 → 「同等/混在」**(良化の条件=2-1が良化または判定不能で、指標群のうち2つ以上が良化、悪化0。悪化の条件=確定した要確認フラグ、または指標群のうち2つ以上が悪化)。
- 費用差(新約¥43.9/記事 対 旧約¥7.1/記事、B1再支出を含む実費)は総合の外。
- **総合のFable最終判定**: ______(空欄)

### 2-E. 符号検定(テーマ単位、片側、帰無=腕差なし。有意とは言わない)
| 比較 | 新が良い | 旧が良い | 同点 | p(片側、新優位、同点除外) |
|---|---|---|---|---|
| 人手介入(テーマ別件数) | 3(meta,hormuz,small) | 4(space,central,openai,semi) | 2 | 0.77 |
| Rewrite発生run(テーマ別) | 3(openai,semi,streaming) | 2(space,byd) | 4 | 0.50 |
| 軽微JA(対のある6テーマ) | 3(small,byd,semi) | 1(openai) | 2 | 0.31 |
- 事前登録3節の通り、n=9の有効nは同点で減る。いずれも有意でない。『7/10以下は有意でない』と同じく、本Trialは**方向性の確認**にとどまる。

## 3. ラベル要約

### 3-1. ラベル件数(行ベース、dup除外、腕×段) — **件数比較には使わない**
ツール指摘(JA FC/EN deviation/(ii)/Checker stage2)と最終本文の全文照合の行を含み、段階・attemptを混ぜている。同一claimの断片重複は`merge_labels_01.py`の規則(接頭辞25文字以上一致)でグループ化し、`dup_primary`のみ数えた。
| 腕 | 段 | 重大 | 軽微 | 問題なし | 判断不能 |
|---|---|---|---|---|---|
| 新 | JA | 0 | 15 | 18 | 0 |
| 新 | EN(Adv) | 0 | 8 | 8 | 0 |
| 新 | EN(Std) | 0 | 7 | 6 | 0 |
| 新 | EN(段未区別) | 0 | 3 | 0 | 0 |
| 新 | Checker(Adv) | 0 | 14 | 79 | 0 |
| 新 | Checker(Std) | 0 | 5 | 40 | 0 |
| 新 | Checker(段未区別)/他 | 0 | 1 | 6 | 2(Checker未実行の対象外) |
| 旧 | JA | 2(meta旧rejected本文の境界1+STOP妥当性行1=同一事象) | 23 | 33 | 0 |
| 旧 | EN(Adv) | 0 | 11 | 9 | 0 |
| 旧 | EN(Std) | 0 | 8 | 6 | 0 |
| 旧 | Checker(Adv) | 0 | 6 | 86 | 0 |
| 旧 | Checker(Std) | 0 | 11 | 48 | 0 |
- (ii)検出に付いたラベル(行ベース、R0・案B前を含む): 新 問題なし9/所見なし2、旧 軽微7/問題なし16。つまり旧腕の(ii)15件(検出器)は、ラベル上は**大半が問題なし**で、実質の軽微は少数(最終JAに限るとspace旧1+semi旧1[低確信])。

### 3-2. 出荷本文に残る軽微(判定線2-2の元データ、claim単位) と 出荷本文の重大見逃し
- 表: `judge_table_01.json` の `final_minor_item_table`(20行、row_id付き)。合計: JA 新5/旧9、EN Adv 新3/旧3、EN Std 新5/旧4。**重大の残存: 新0 / 旧0(3 worker一致)。**
- 項目の起源の傾向: JA列は『範囲・確からしさの拡張、一般化、因果の付与、見出しの限定欠落』が中心。EN列はtranslation由来(要約の条件欠落、単複)とChecker Rewrite起因の劣化(旧腕2件)。

### 3-3. 境界例一覧(人間確認候補) — 11件
| ID | テーマ | 腕 | 本文/段 | 該当 | worker暫定 | 出荷 | row_id | HUMAN_CHECK |
|---|---|---|---|---|---|---|---|---|
| B-01 | meta | 旧 | JA R2 attempt2 | 『AIが電話をかけ、相手に切られることもある。そこで人間が電話を担当する。』(因果・設計意図の創作) | **重大(境界)**(w1) | ×(STOPで阻止) | w1-11,w1-14 | 対象外(出荷されず) |
| B-02 | space_weapons | 新 | JA+EN Adv | 不在・秘匿の断定(『必殺技は秘密』『性能表は伏せたまま』『have not been given』等4箇所)。台帳は『補わない』指示のみで非公開とは書かない | 軽微(確信0.5、基準(6)字義なら重大) | ○ | w1-49,w1-76 | S-1 |
| B-03 | space_weapons | 旧 | JA+EN Adv/Std | 『名前も…能力も明らかにされていません』(同型) | 軽微(同上) | ○ | w1-61,w1-62,w1-73,w1-75 | S-2 |
| B-04 | space_weapons | 新 | EN Adv/Std | 『Russia has destroyed satellites…these were tests』(台帳はCOSMOS 1408の1件、単複差。REPORT 5-3 #2未決)。Advは機械floorのRewriteで修正(missiles複数形が残存)、Stdはこれが原因でSTOP | 軽微(境界) | Advのみ○ | w1-52,w1-53,w1-58,w1-122,w1-129 | 末尾の基準質問に含まず(別途) |
| B-05 | byd_recall | 新 | JA | 見出し・冒頭が無留保で現象を描写(台帳BYD-RECALL-07は『極端な場合…可能性』) | 軽微(境界、w2が人間確認候補) | ○ | w2-195 | B-1 |
| B-06 | central_bank_mortgage | 新 | JA R0 attempt1 | 『固定型の住宅ローン金利』(30年固定の範囲拡張) | 軽微(境界) | ×(R0 STOP) | w2-201 | C-1 |
| B-07 | central_bank_mortgage | 新 | JA R0 attempt2 | 『政策金利の目標を…3.75％から4.00％にしました』(『レンジ』脱落) | 軽微(境界) | × | w2-204(長期固定は w2-203) | C-3(C-2) |
| B-08 | openai_copyright | 新 | JA R2(B1前) | CMI除去の主体が文法上『モデルの出力』 | 軽微(境界) | ×(B1で置換) | w3-39,w3-43 | O-2 |
| B-09 | semiconductor_earnings | 新 | JA R0 | 『次の数字は、AI半導体売上高の予想ではありません』(F5のAI見通しを否定する字面) | 軽微(境界) | ×(R2で解消) | w3-85 | 未掲載(最終前) |
| B-10 | semiconductor_earnings | 新 | JA R1 | 『登場するのは三つ』(網羅性の誤り) | 軽微(境界) | ×(R2で解消) | w3-86 | 未掲載(最終前) |
| B-11 | streaming_price | 旧 | JA/EN | 新規契約者9/23の時制(調査基準日前に開始済みなのに未来形、低確信) | 軽微(低確信) | ○ | w3-98,w3-116 | 未掲載 |
- 出荷本文に残る境界: 4件(B-02,B-03,B-05,B-11)+B-04のAdv側。B-08〜B-10は最終前に解消。**ユーザー確認の優先順**: B-05(新腕のみのフラグ候補)→C系・O系(STOP妥当性)→S系(両腕共通の基準)。

### 3-4. B3由来・AMBIGUOUS由来の別集計(機械候補とラベルの突合) ＋ ラベル/集計の不一致
- 機械候補(`AGGREGATE.md` 6節、Checker cycle1 stage2 MAJORが母集団): AMBIGUOUS 新2(streaming Adv)/旧0、B3 新4(hormuz)/旧4(semiconductor)。
- ラベルとの突合(origin列、dup除外):
  - B3由来(unmapped_claims起因)として『真の問題』とされたもの: **0件**(hormuz新=問題なし1、semiconductor新=問題なし2[うち1つがEN Adv STOPの根拠])。w2のorigin=B3はunmapped_claims空のStoryline由来の意味(注記版briefの表現由来)で、byd新(軽微1)・small_bag旧(軽微4)等。
  - **機械候補は実際のB3由来STOP(semiconductor新EN Adv)を拾えていない**(新腕のChecker未実行のため母集団外)。機械候補の旧semiconductor 4件・新hormuz 4件は、ラベル上は偽陽性/問題なし。
  - AMBIGUOUS由来のNG: ラベル上**0件**(streaming新2、semiconductor新1、streaming旧1、semiconductor旧1、全て問題なし)。
- **不一致(訂正して使用)**:
  1. EN STOPのレベル帰属: 旧腕small_bag・byd_recallは Standard STOP(成果物: `a2/article.md`なし・`b1b/article.md`あり、runログ『Standard deviation MAJOR…JA_RECHECK…STOP』)。`AGGREGATE.md`は旧腕Advanced STOP 2/Standard 0としている。→ 正: 旧 Adv 0 / Std 2。新腕は Adv 2(openai,semi)/Std 2(space,byd)で一致。
  2. M1発火: 集計は新腕Std 2・Adv 0。実際は**Std側の値は『attempt2ファイルの存在』(=must-fix再生成)であってM1ではない**。runログの`[OPEN243_M1]`は space新 Adv の1回のみ(REPORT §110: M1はAdvanced枝のみ)。w2が『byd新StdでM1発火』と書いた行(w2-117,w2-118,w2-197)は、runログと矛盾(`merge_labels_01.py`の`qa_note`に記録、原本は不変)。
  3. M1の効果: w1はspace新で『M1により要約から不在主張が除去』と記述。事実は**B1前の本文**でM1が効き(`b1b_prev_b1`の要約は不在主張なし)、B1後の最終Adv本文の『In one line』には再び『has not disclosed their capabilities』が出ている。M1はB1(JA再生成)で上書きされた。
  4. 旧腕(ii)のsmall_bag 3・byd 4は案B前の本文の値(w2も指摘)。

## 4. STOP・B1・案B・M1・M3・Rewrite の妥当性(暫定ラベルによる内訳)

### 4-1. STOP 9記事(新5・旧4)
| 区分 | 件数 | 内訳 |
|---|---|---|
| 真に必要(重大・境界) | 1 | meta旧 JA STOP(『そこで人間が』=因果創作。基準が緩ければ回避可) |
| 軽微起因(過剰ブロック疑い) | 6 | 新: central R0(軽微境界2〜3件)、space Std(単複差=機械floor適用)、byd Std(目的表現→『will stop/prevent』)、openai Adv(見出し一般化、B1後)。旧: small_bag Std(案B後、軽微2)、byd Std(案B後、因果付与) |
| 問題なし(偽陽性) | 2 | 旧hormuz JA STOP(ガソリンの一般論=問題なし)、新semiconductor Adv(B3のqualifier注記由来の文) |
- 出荷された本文に重大を残さずに済んだ、という意味での『安全装置の働き』は確認できないが、**STOP9件中8件は重大でない根拠で人手介入になった**(暫定、確信度はworkerごと)。新旧とも同様で、過剰ブロックの質は両腕で似ている(新腕は注記・B1・単複floorに由来する別経路が加わる)。

### 4-2. 案B(旧腕)とB1(新腕)
| 腕 | 発動 | 起点の指摘の重さ | 結果 |
|---|---|---|---|
| 旧 案B | small_bag, byd, openai | 全て軽微(2件ずつ) | openai: 完走。small, byd: Advは解消したが**Standardで別の軽微が出てSTOP**(収束せず) |
| 新 B1 | hormuz(軽微)、space(**問題なし**=hookの修辞)、openai(軽微境界=CMI主体) | 軽微/問題なし | hormuz: 完走。space: 起点は解消したが回復後JAの不在断定(軽微)が増え、Std STOPは回復後ENの単複差。openai: 起点は解消、新JA見出しの一般化で再MAJOR→1記事1回でSTOP。semiconductor: Trial上限3/3で拒否→STOP |

### 4-3. B1の費用対効果
- B1 3回の再支出 raw約¥103。完走に至ったのは hormuz の1件のみ(成功率1/3)。回復枠が無ければhormuzはAdv EN STOP(起点は軽微)で終わっていたので、『軽微指摘をSTOPから救った』効果はこの1件。space・openaiは回復後も別の軽微でSTOP/Std STOP。semiconductorは枠切れ。**純効果は疑問(¥103で完走+1)**。枠の消費順(hormuz→space→openai)が後のsemiconductorの拒否を決めた**順序依存**があり、反実仮想は未実行(再実行はcherry-picking禁止)。

### 4-4. M1・M3・Rewrite・Checker
- M1: 発火1(space新Adv、B1前の要約MAJORを解消)。最終本文には残らなかった(3-4の3)。Standardは未実装。効果の一般的評価は不能(n=1)。
- M3: 新腕の保護6(byd5,small1)。保護で拾えた真の問題は3 workerとも0件。旧腕の影5は全て台帳一致の記述で、保護しても救出なし。便益未確認。
- Rewrite(新2/旧7イベント): 新=space Adv 単複修正(軽微境界、有効・副作用小)、byd Adv(不要、比喩ジョークの削除)。旧=openai Std 1(任意改善)、semiconductor Std 2(不要、1件は限定句『not the whole semiconductor segment』を削除する軽微劣化)、streaming Std 4(BLOCKINGは小数点断片、3件は結果として軽微が直る、1件はPremium差額文ごと削除する軽微劣化)。**旧7件中6件は小数点断片(『$29.』等)起因、劣化2件**。
- Checker BLOCKING偽陽性: byd新Adv『現場と広報が連絡していない』(比喩、不要Rewrite)。Stage2指摘の大半は決定論検査(否定・因果・fact_id欠落)や比喩文への反応で、ACCEPTABLEに降格。

## 5. 観察・仮説

### 5-0. Fableの突合メモの検証結果
| メモ | 結果 | 根拠・補足 |
|---|---|---|
| 出荷本文の重大見逃しは両腕0、境界は人間確認 | **一致** | 3 worker一致。出荷本文に残る境界は4〜5件(B-02,03,05,11,B-04のAdv) |
| 新腕はJA段の台帳外主張が大幅に少ない((ii)2対15、R2 FC MAJOR 0対4) | **部分一致** | 数字は一致。ただし(a)旧(ii)15のうち7(small3,byd4)は案B前本文の値、(b)最終JA由来に限ると新2/旧8、(c)ラベル上は旧(ii)の大半が問題なし(semi4件全て台帳内、openai・streamingも問題なし)で実質の軽微はspace旧1+semi旧1、(d)旧FC MAJOR4のうち重大(境界)1(meta)・軽微1・偽陽性2、(e)w1: 新腕space JAには旧腕と同型の不在断定が残るが(ii)=0=検出器の注記依存の疑い(未検証)。軽微JA列の差(5対9)は小さい(符号検定p=0.31) |
| 新腕のEN STOP4件とB1発火3件の根拠はラベル上は軽微または偽陽性、B1の純効果は疑問(¥103) | **一致** | 4-1/4-3。EN STOP: 軽微3(space Std単複、byd Std目的表現、openai Adv見出し)+偽陽性1(semi)。B1: 軽微2+問題なし1 |
| semiconductor新のEN STOPはB3注記のunmapped qualifier由来(AMBIGUOUS由来でない) | **一致(確認済み)** | `semiconductor_earnings/new/storyline_b3/selected_brief.md` 事実1の末尾『これらの需要評価と業績・見通しの間に、Ledgerで確認されていない因果関係を付け加えないこと』。w3: EN MAJOR文=『この発表だけでは両者のつながりは説明されない』はその注記文の言い換え。AMBIGUOUS(F1)由来ではない。B1はTrial上限で拒否 |
| central_bank新のR0 STOPは『30年固定』の範囲拡張(注記で周辺扱い)が影響した可能性(未検証) | **部分的に支持(因果は未検証)** | 注記は『30年固定』を`name_embedded`=常に周辺(`shared/annotation.json`)とし、briefに【周辺数値】タグが付く。**注記なしの旧briefと本文は同一**(タグの有無だけが差)。Fact Lockは周辺数値を固定しない設計のため、Writerが言い換えた可能性はある。ただしbrief事実5・6自体が『固定型』『固定住宅ローン』と総称語を使っており、そこから拡張した可能性もある。アブレーションは禁止のため因果は未検証 |
| Checker欠陥候補: 旧Standardの小数点文分割断片が独立claimとしてBLOCKING化、不要Rewrite 6/7、軽微な劣化2 | **一致** | w3の集計。さらに新腕でも断片は出る(space Checker Adv、streaming新Adv)が、新腕はQUALITY止まりでRewriteに至らなかった(なぜ違うかは未検証) |
| 旧腕(ii)は案B前本文の値で、small_bag/bydは最終JAを表さない | **一致** | w2確認(sha不一致: small 7275f…≠eac0a2…、byd 684e2c…≠a091e3…) |

### 5-1. Writer段の良化
FC MAJOR(0対4)・(ii)(2対15)はいずれも新腕が良いが、**FCは同系列モデルの自己判定**であり、ラベル上は旧腕の指摘の大半が偽陽性だったため、『実質の良化』は軽微JA列の5対9(対6テーマ)程度にとどまる。JA字数は新931対旧740(新が長く、盲検上も文体差で腕が推測できる)。面白さは未評価。

### 5-2. EN段の過剰ブロック
新腕のEN STOP4件はいずれもja_sourceまたはtranslationの**軽微/偽陽性**でSTOPしており、旧腕のStd STOP2件も案B後の軽微。EN deviation checkはMAJORを『軽微相当』でも付けるため、B1/案B/must-fixが軽微でSTOPに至る構造は両腕共通。新腕固有の要因: 単複差に対する機械floor(changed_number)、B3 qualifier注記由来の文、B1の1記事1回/Trial3回上限。

### 5-3. 注記(周辺扱い・qualifier)の副作用
(a)周辺扱い=central新R0 STOP(因果未検証)。(b)qualifier注記文=semi新EN Adv偽陽性STOP(確認済み)。(c)注記ありで新腕の(ii)が0に近い一方、space新JAには不在断定が残る=検出器の注記依存の疑い(未検証)。新腕のSTOP5件のうち少なくとも1〜2件は注記起因の可能性。B3注記は人手(Sonnet)注記の上限性能であり、自動注記でProduction化した場合の副作用は未測定。

### 5-4. Checkerの文分割欠陥
旧腕Standardで小数点分割の断片が独立claim化→BLOCKING→不要Rewrite(7件中6件)、2件で軽微劣化。Checkerのclaim分割(runner/Stage 1)の欠陥候補。新腕では断片がQUALITYで止まりRewriteに至らなかった(原因は未検証)。実装修正は本委任の範囲外。

### 5-5. B1の費用対効果
4-3節。raw約¥103で完走+1、順序依存あり。Production等価性規定で『1記事1回』『Trial全体3回』としたため、反実仮想(上限なし)は未測定。

### 5-6. Astra実測単価
R1+R2を1生成として raw¥30.6(guard¥45.8)。設計見積¥27〜34の範囲内で、見積の乖離は小さい。新腕1記事(JA完走・B1再支出除外)は raw約¥36対見積約¥42で見積以内。**請求ダッシュボード照合は未実施**(guardはx1.5の安全係数)。

## 6. 限界
- n=9(旧4+新5)。同点で有効nは更に小さい。各腕n=1生成、LLMの揺れは推定不能(deviation checkは同一本文でCOMPLIANTとMAJORが割れた事例あり: space新shadow、byd旧m1a)。
- ラベルはSonnet 3 workerの暫定推測(確信度0.35〜0.8)。重大はユーザー確認前(HUMAN_CHECK_E2E_01.md)。workerごとにスキーマ・粒度が異なり、軽微の件数はclaim単位に揃えた手作業の写し(`FINAL_MINOR_ITEMS`)で、境界の取り方に依存する。
- 盲検不完全(JAはAstra/Lunaの文体差と字数差で腕が推測可)。
- 旧腕(ii)15のうち7件は案B前の本文の値。旧腕のJA original/R1の一部本文は保存されておらず、FC引用のみで判断した行は確信度を下げている(w1)。
- M1 Standardは未実装=Standardでの効果は未測定。M1/M3の個別効果はJA本文の違いと交絡(影の対照は記述のみ)。
- 請求照合未実施(Astra単価はTrial/DEV登録、ダッシュボード請求増分と未照合)。
- 人手注記の上限性能(B3はSonnet人手注記、独立二重注記+固定ルール)。自動注記でのProduction化は別検証。
- B1上限(Trial3回)の順序依存でsemiconductor新が拒否されSTOP。新腕のSTOP率・人手介入必要率がこの上限に依存する。
- 集計scriptの帰属誤り(3-4の1・2)があり、本書は成果物ベースに直した。`AGGREGATE.md`自体は編集していない(runs配下の編集禁止)。
- Production採用提案前には**Opus独立技術レビュー(条件C)**が必要。本書は採用提案ではない。

## 7. OPEN項目候補一覧(起票はFable判断。`OPEN_ITEMS.md`は未編集)
| 候補 | 内容 | 根拠 |
|---|---|---|
| OC-1 Checker小数点文分割 | 『$29.』等の断片が独立claim化→BLOCKING→不要Rewrite、限定句・差額文の削除という軽微劣化 | 旧腕Std 7件中6件、劣化2件(w3)。新腕でも断片は出る |
| OC-2 B3自動注記 | Production化には自動注記が必要。人手注記は上限性能 | 事前登録3節。注記の副作用(OC-5)も未測定 |
| OC-3 EN段ja_source/translation MAJORの過剰ブロック | 軽微相当のMAJORでB1/案B/must-fix→STOPに至る(EN STOP新4/旧2のうち重大の根拠なし) | 4-1節。重大度による回復・STOPの分岐は設計案(実装不可、仕様はユーザー決定要) |
| OC-4 B1回復の扱い | 純効果が疑問(¥103で完走+1)、Trial上限の順序依存、回復後に別軽微が出る | 4-3節。Production等価性の見直し論点 |
| OC-5 B3注記の副作用 | 周辺扱い(30年固定)、qualifier文のENへの伝播 | central新R0(因果未検証)、semi新EN Adv(確認済み) |
| OC-6 集計scriptの帰属誤り | EN STOPのレベル帰属(旧腕Std→Adv)、M1発火=attempt2存在(Stdで誤) | 3-4節。修正は別委任、`AGGREGATE.md`は再生成が必要 |
| OC-7 FC/EN deviation判定の再現性 | 同一本文でCOMPLIANT/MAJORが割れる(space新shadow、byd旧m1a、small_bag旧Adv/Std) | 5-2節 |
| OC-8 不在・非公開の断定、単複差の基準 | 台帳が『補わない』と指示しただけの事柄を『示されていない/秘密』と断定。単複差はREPORT 5-3 #2未決 | B-02〜B-04。S系質問で確定 |
| OC-9 M1のStandard枝・B1後の再出現 | StandardにM1が無い。B1(JA再生成)でM1の効果が上書きされる | 3-4の2・3 |
| OC-10 面白さの比較 | 新腕の字数・文体差が大きい。pairwise未実施 | 5-1節 |

## 8. 付録: 成果物と再現
- `eval/merge_labels_01.py`→`labels_merged.jsonl`(553行、重複グループ46、worker間テーマ重複0)、`labels_merged_stats.json`。
- `eval/judge_table_01.py`→`judge_table_01.json`(機械判定と根拠数値)。`eval/build_human_check_01.py`→`HUMAN_CHECK_E2E_01.md`。
- 再実行: `python merge_labels_01.py && python judge_table_01.py && python build_human_check_01.py`(API不要)。
