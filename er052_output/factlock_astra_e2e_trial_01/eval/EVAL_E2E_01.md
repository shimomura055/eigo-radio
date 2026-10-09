# EVAL_E2E_01 v2: FACTLOCK-ASTRA-E2E-TRIAL-01 評価文書(委任_15で作成・委任_16でv2、2026-10-09、MEASURED・ラベル暫定・Fable最終判定記入済み)

位置づけ: Trial/DEV(Production変更なし)。VALIDATED/APPROVED_FOR_PRODUCTIONは宣言しない。2節の『機械判定』は事前登録(`PREREGISTRATION_01.md` v2.2+事後注記)の線への**機械的な当てはめ**で、**v2で『Fable最終判定』列と総合判定を記入した**(0節にまとめ)。
ラベル(`labels_w{1,2,3}.jsonl`)は**Sonnet 3 workerの暫定推測**であり、ユーザー確認前。API支出¥0(本委任)。数値の出所: 集計=`runs/final_aggregate/aggregate_final.json`、ラベル=`eval/labels_merged.jsonl`(統合規則は`merge_labels_01.py`冒頭)、機械照合=`eval/judge_table_01.py`→`eval/judge_table_01.json`。
読み替え(事前登録7節の事後注記どおり): 対の数 n=9(旧4+新5、inbound_tourismは注記不能で除外)、予定run各腕18、記事単位の分母9。比率・条件(0.75/1.25、過半数、6対以上、3記事差以上)は変更なし。

## 改訂履歴
| 版 | 日付 | 内容 |
|---|---|---|
| v2(委任_16) | 2026-10-09 | Opus任意レビュー(`docs/pm/opus_a_review_factlock_astra_e2e_01.md`「評価レビュー」節)を全て反映。(1)semiconductor新EN STOPの帰属訂正(B3注記の副作用ではなく、brief内の指示文がFact Lock R0経由で事実扱いされた新腕固有の経路)、§5-11の『B3由来』別集計値を併記 (2)2-2 JA列から未出荷本文(openai新 w3-40)を除外し再計算(新4/旧9、判定「同等」不変) (3)人手介入の感度値(失ったChecker run 新8/旧6)を主表へ格上げ (4)ラベル基準の統一(OC-8、統合ラベルの`qa_note`に記録、原本不変) (5)言い過ぎの訂正(注記起因の過剰ブロック、Checker欠陥耐性、M3) (6)層別逆転の説明を妥当順に改訂(5-7節) (7)**Fable最終判定を2節『Fable最終判定』列と0節に記入** (8)人間確認パックに面白さpairwise 3対を追加 (9)OPEN候補の優先度、Production Checker文分割器の配線確認(7節)、次の選択肢(8節) |
| v1(委任_15) | 2026-10-09 | ラベル3本統合、事前登録の判定線への機械照合、評価文書作成。最終判定は空欄 |

## 0. Fable最終判定(v2、判定線ごと。2026-10-09、Fable判断をSonnetが転記。ラベルはSonnet暫定推測、n=9、各腕n=1生成)

| 判定線 | Fable最終判定 | 根拠(要約) |
|---|---|---|
| 2-1 重大(出荷最終本文の残存) | **判定不能** | 床効果(0対0)。要確認フラグは未確定でB-05(byd新の見出し無留保)の人間回答待ち |
| 2-2 軽微 JA列 | **同等**(検出力不足) | 新4対旧9(対6テーマ: 平均0.67対1.50、新が少ない3対・旧が少ない0対、同点3)。良化線の『新が少ない対6対以上』は有効6対では構造上到達困難。新優位方向の記述的傾向のみ(符号検定 p=0.125、有意でない) |
| 2-2 軽微 EN Adv列 | **同等** | 3対3 |
| 2-2 軽微 EN Std列 | **判定不能** | 床効果(対のある対の総件数5以下) |
| 2-4 EN Adv STOP率 | **同等** | 差2記事は線(3記事差)未満。STOP根拠は全件が軽微または問題なし起因(重大根拠0)。事前登録§5-11を適用(B3由来を別集計)すると新1(semi除外)対旧0 |
| 2-4 EN Std STOP率 | **同等** | 2対2 |
| 2-5 Rewrite率 | **同等** | 新0.111対旧0.167。旧の不要Rewriteの大半はChecker欠陥(小数点文分割)由来でWriter差ではない |
| 2-5 Human Review率 | **判定不能** | 0対0(床効果) |
| 2-5 人手介入必要率(複合主指標) | **同等・混在** | 0.333対0.333。感度(実際に失ったChecker run): 0.444対0.333。層別は逆向き(旧4: 新0.125対旧0.625、新5: 新0.50対旧0.10)、新5では新腕が多い |
| **総合(2-6)** | **同等・混在** | **事実安全の良化は示されなかった(測定力不足を含む)。費用は新約¥43.9対旧約¥7.1/記事(約6倍)。面白さは未測定(人間確認パックにpairwise追加済み)。** |

- **VALIDATED / APPROVED_FOR_PRODUCTION は宣言しない。** 本判定は『方向性の確認』であり、採否はユーザー判断(8節の選択肢)。Production変更なし。


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

**「機械判定」=事前登録の線への機械的な当てはめ。Fable最終判定はv2で右端の列に記入(0節にも一覧)。** 新=新仕様腕(Fact Lock+Astra+B1+M1/M3+B3注記版)、旧=旧仕様腕(Production相当)。層別: 旧4=meta/hormuz/space_weapons/small_bag、新5=byd/central/openai/semiconductor/streaming。

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
| 面白さpairwise | 未実施(AI評価)→ 人間確認パック `HUMAN_CHECK_E2E_01.md` 6節に3対(space_weapons/streaming_price/small_bag、A/B順序を伏せ、MAPは`eval/_private/`)を追加。回答待ち | - | - | - | 副指標 | 未測定 | | | 判定外(未測定) |
| 軽微(JA列)→ 2-Cの2-2を参照 | | | | | | | | | |

### 2-B. 評価対象(2) 翻訳仕様(EN段、M1/M3) — 事前登録2-4
| 指標 | 定義 | 新腕 | 旧腕 | 差 | 判定線 | 機械判定 | 層別 旧4(新/旧) | 層別 新5(新/旧) | Fable最終判定 |
|---|---|---|---|---|---|---|---|---|---|
| EN Advanced STOP率 | STOP記事÷9 | 2/9=0.22(openai,semi) | 0/9=0.00 | +0.22 | 良化: 新≦旧-0.3(3記事差)かつ翻訳由来MAJOR/記事≦旧x0.75かつ軽微EN列が悪化でない。悪化: 新≧旧+0.3かつ翻訳由来MAJOR/記事≧旧x1.25 | **同等**(差2記事<3記事。translation由来MAJORは両腕0) | 0 / 0 | 2 / 0 | **同等**(差2記事は線未満。全件軽微・問題なし起因。§5-11適用で新1) |
| EN Standard STOP率 | 同 | 2/9=0.22(space,byd) | 2/9=0.22(small,byd) | 0 | 同 | **同等**(translation由来MAJOR/記事は新0.22 対 旧0.00だが、STOP率の差が0なので片方のみ=記述指標) | 1 / 1 | 1 / 1 | **同等**(2対2) |
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
| **2-1 重大(出荷最終本文の残存)** | 盲検ラベル=重大 | 0 | 0 | 0 | 良化: 新0かつ新<旧。両腕の総数が2件以下は判定不能(床効果)。新>0かつ同テーマ旧0は要確認フラグ | **判定不能(床効果)。要確認フラグ: なし** | 0 / 0 | 0 / 0 | **判定不能**(床効果0対0)。要確認フラグは未確定: B-05回答待ち |
| 　重大ラベルの所在 | 重大と付いた行 | meta旧のrejected本文1件(+STOP妥当性行)のみ。出荷本文なし | | | | | | | |
| 　境界例(重大/軽微) | 3-3節に11件 | 出荷本文に残る境界: B-02,B-05(,B-04) | B-03,B-11 | | 参考 | **回答次第でフラグが変わる**: B-05(byd新)が重大ならフラグ。B-02/B-03(space両腕)は両腕に同型でフラグにならない | | | |
| **2-2 軽微 JA列** | 出荷最終本文の残存(件/記事、claim単位、JA完走記事。**v2: 未出荷本文のopenai新 w3-40を除外**) | 4件(8記事、対のある6テーマ分4) | 9件(7記事、対6テーマ分9) | 対6テーマの平均 0.67 対 1.50(比0.44) | 良化: 新平均≦旧x0.75かつ新少ない対が同点除き過半数かつ6対以上。悪化: 新平均≧旧x1.25かつ新多い対6対以上 | **同等**(平均比は良化線を満たすが、新が少ない対は3対・旧が少ない対0・同点3で『6対以上』に届かない。総件数13>5で床効果ではない。符号検定 p=0.125) | 1 / 4 | 3 / 5 | **同等**(検出力不足。判定線は構造上到達困難。新優位方向の記述的傾向のみ) |
| **2-2 軽微 EN Advanced列** | 出荷EN Adv本文の残存(JA由来は二重計上しない) | 3件(出荷6) | 3件(出荷7) | 対のある4テーマ: 3 対 3 | 同上 | **同等**(平均比1.00) | 1 / 1 | 2 / 2 | **同等**(3対3) |
| **2-2 軽微 EN Standard列** | 同(EN Std) | 5件(出荷4) | 4件(出荷5) | 対のあるテーマは streaming の1対のみ(2 対 1) | 同上 | **判定不能(床効果: 対のある対の総件数5以下)**。出荷本文単位の総数は新5/4本対旧4/5本 | 3 / 1 | 2 / 3 | **判定不能**(床効果) |
| 　軽微の別枠 | R0冒頭復唱が最終JAに残る | 0 | 0 | 0 | 件数のみ | 件数のみ | | | |
| **2-5 Rewrite率** | Rewrite発生run÷18 | 2/18=0.111 | 3/18=0.167 | -0.056 | 良化: 新≦旧-0.15(3 run差以上)かつ不要Rewriteが増えていない。悪化: 新≧旧+0.15 | **同等**(差<0.15) | 1/8 vs 0/8(+0.125) | 1/10 vs 3/10(-0.20) | **同等**(旧の不要Rewriteの大半はChecker欠陥由来でWriter差でない) |
| 　不要Rewrite(併記) | ラベル上不要 | 1〜2件(byd Adv: 比喩ジョーク削除=不要。space Adv: 単複差=基準次第) | 6〜7件(小数点断片起因6/7、うち軽微劣化2) | 新≦旧(増えていない) | Rewrite率の条件 | 条件は満たすが、Rewrite率が良化線に届かないため良化にならない | | | |
| **2-5 Human Review率** | 出口BLOCKING→Human Review到達run÷18 | 0 | 0 | 0 | 総イベント2件以下は判定不能 | **判定不能(床効果)** | 0 / 0 | 0 / 0 | **判定不能**(0対0) |
| **2-5 人手介入必要率(複合主指標)** | (JA STOP[記事=2 run]+影STOP+EN STOP[1 run]+Human Review)÷18 | 6/18=0.333(JA STOP 2[central]、EN STOP 4) | 6/18=0.333(JA STOP 4[meta,hormuz]、EN STOP 2) | 0 | 良化: 新≦旧-0.15。悪化: 新≧旧+0.15。総イベント4件以下は判定不能 | **同等** | 1/8=0.125 vs 5/8=0.625(-0.50) | 5/10=0.50 vs 1/10=0.10(+0.40) | **同等・混在**(0.333対0.333、感度0.444対0.333、層別逆向き、新5では新腕が多い) |
| **2-5 人手介入必要率(感度、v2で主表へ格上げ)** | 同。ただしAdvanced STOPでStandardのChecker runも失われた(実際に失ったChecker run)とみなす | 8/18=0.444 | 6/18=0.333 | +0.111 | 同上 | **同等**(差+0.111<0.15) | | | 主表の一部(新が不利な側の感度値。判定は不変) |
| 　B3由来の別集計(事前登録§5-11、v2追記) | semiconductor新EN Adv STOP(原因文=brief内の指示文、unmapped_claims qualifier該当)を除く | Adv STOP 新1/9。人手介入 新5/18=0.278 | Adv STOP 旧0/9。人手介入 旧6/18=0.333 | 人手介入 -0.056 | 同上 | 同等(判定不変) | | | 参考(Fact Lock起因に数えない区分の別集計。判定は不変) |
| 　層別の逆向き | 旧4では新が少なく、新5では新が多い | | | | | 層別(参考)の機械当てはめは**反対方向**(旧4=良化方向、新5=悪化方向)。全体では相殺。**説明の妥当順は5-7節** | | | |
| 影STOP(R2後FC MAJOR) | shadow_stop | 0 | 0 | 0 | 記述指標 | 記述のみ | | | |
| B1回復(新のみ) | 発動/成功/拒否 | 発動3(hormuz,space,openai)/**完走1(hormuz)**/拒否2(semiconductor=Trial上限、openaiの2回目=1記事1回上限) | 案B(旧)は発動3(small,byd,openai)/成功1(openai) | | 記述指標 | 記述のみ(B1の純効果は疑問、4-3節) | | | |
| Checker出力の参考(新/旧 run完了) | A 初回候補(延べ) | 82(10 run) | 106(12 run) | | 記述のみ | 記述のみ | 54 / 30 | 28 / 76 | |
| 費用差(判定外) | raw | ¥395.12 | ¥63.92 | +¥331.20(1記事 ¥43.9 対 ¥7.1) | 総合判定の外で併記 | 差額のみ | | | |

### 2-D. 総合(事前登録2-6、参考の機械当てはめ)
- 判定指標群={2-2 JA列、2-2 EN列、2-4(Adv・Std)、Rewrite率、人手介入必要率}。機械当てはめ(v2再計算後も不変): JA列=同等、EN列(Adv+Std合算の対5対)=同等(新5件対旧4件)、2-4 Adv=同等、2-4 Std=同等、Rewrite率=同等、人手介入必要率=同等。**良化0・悪化0 → 「同等/混在」**(良化の条件=2-1が良化または判定不能で、指標群のうち2つ以上が良化、悪化0。悪化の条件=確定した要確認フラグ、または指標群のうち2つ以上が悪化)。
- 費用差(新約¥43.9/記事 対 旧約¥7.1/記事、B1再支出を含む実費)は総合の外。
- **総合のFable最終判定(v2)**: **同等・混在。事実安全の良化は示されなかった(測定力不足を含む)。費用約6倍(新¥43.9対旧¥7.1/記事)。面白さは未測定。** VALIDATED/APPROVED_FOR_PRODUCTIONは宣言しない。

### 2-E. 符号検定(テーマ単位、片側、帰無=腕差なし。有意とは言わない)
| 比較 | 新が良い | 旧が良い | 同点 | p(片側、新優位、同点除外) |
|---|---|---|---|---|
| 人手介入(テーマ別件数) | 3(meta,hormuz,small) | 4(space,central,openai,semi) | 2 | 0.77 |
| Rewrite発生run(テーマ別) | 3(openai,semi,streaming) | 2(space,byd) | 4 | 0.50 |
| 軽微JA(対のある6テーマ、v2: openai新の未出荷本文を除外) | 3(small,byd,semi) | 0 | 3(space,openai,streaming) | 0.125 |
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
- 表: `judge_table_01.json` の `final_minor_item_table`(v2は20行、row_id付き。除外分は `excluded_unshipped_minor_items`)。合計: JA 新4/旧9(v2、openai新の未出荷本文 w3-40を除外。v1は新5)、EN Adv 新3/旧3、EN Std 新5/旧4。**重大の残存: 新0 / 旧0(3 worker一致)。**
- 項目の起源の傾向: JA列は『範囲・確からしさの拡張、一般化、因果の付与、見出しの限定欠落』が中心。EN列はtranslation由来(要約の条件欠落、単複)とChecker Rewrite起因の劣化(旧腕2件)。

### 3-3. 境界例一覧(人間確認候補) — 11件
| ID | テーマ | 腕 | 本文/段 | 該当 | worker暫定 | 出荷 | row_id | HUMAN_CHECK |
|---|---|---|---|---|---|---|---|---|
| B-01 | meta | 旧 | JA R2 attempt2 | 『AIが電話をかけ、相手に切られることもある。そこで人間が電話を担当する。』(因果・設計意図の創作) | **重大(境界)**(w1) | ×(STOPで阻止) | w1-11,w1-14 | 対象外(出荷されず) |
| B-02 | space_weapons | 新 | JA+EN Adv | 不在・秘匿の断定(『必殺技は秘密』『性能表は伏せたまま』『have not been given』等4箇所)。台帳は『補わない』指示のみで非公開とは書かない。**v2: semiconductor新EN Adv STOP文(偽陽性ラベル)と同型(OC-8)** | 軽微(確信0.5、基準(6)字義なら重大) | ○ | w1-49,w1-76 | S-1 |
| B-03 | space_weapons | 旧 | JA+EN Adv/Std | 『名前も…能力も明らかにされていません』(同型。**v2: OC-8の同じ基準で扱う**) | 軽微(同上) | ○ | w1-61,w1-62,w1-73,w1-75 | S-2 |
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
  5. (v2、Opus指摘)semiconductor新EN Adv STOPの帰属: v1は『B3注記のqualifier文由来』と書いたが誤り。原因文『これらの需要評価と業績・見通しの間に、Ledgerで確認されていない因果関係を付け加えないこと』は**注記前のB3 Storyline本文(`runs/semiconductor_earnings/shared/brief_original.md` L7、旧腕briefにも同文)にある指示文**で、注記(`shared/annotation.json`)はこれを`unmapped_claims`(type=qualifier)に記録しただけ。新腕ではFact Lock R0がこの指示文を本文化して【事実1】を付け(`new/new_writer/r0_with_tags.md` L11)、Astra R2が『この発表だけでは、そこをつなぐ説明は埋まらない』と不在断定へ強め(`new/new_writer/r2.raw.md` L13)、EN検査がMAJOR(`new/b1b/audit/deviation_checks/advanced_attempt1.json` L20『発表に両者の関係について説明がないとは確認していません』)。→ 帰属は『brief内の指示文がFact Lock R0経由で事実扱いされ、Astraが不在断定へ強めた**新腕固有の経路**』であり、注記の副作用ではない(箇条書き化が促した可能性は推測)。事前登録§5-11の『B3由来』(unmapped_claims該当)別集計では、Adv STOP 新1/9(旧0)、人手介入 新5対旧6(0.278対0.333)で、判定は不変(`judge_table_01.json` の `b3_origin_separate_5_11`)。

## 4. STOP・B1・案B・M1・M3・Rewrite の妥当性(暫定ラベルによる内訳)

### 4-1. STOP 9記事(新5・旧4)
| 区分 | 件数 | 内訳 |
|---|---|---|
| 真に必要(重大・境界) | 1 | meta旧 JA STOP(『そこで人間が』=因果創作。基準が緩ければ回避可) |
| 軽微起因(過剰ブロック疑い) | 6 | 新: central R0(軽微境界2〜3件)、space Std(単複差=機械floor適用)、byd Std(目的表現→『will stop/prevent』)、openai Adv(見出し一般化、B1後)。旧: small_bag Std(案B後、軽微2)、byd Std(案B後、因果付与) |
| 問題なし(偽陽性) | 2 | 旧hormuz JA STOP(ガソリンの一般論=問題なし)、新semiconductor Adv(brief内の指示文がFact Lock R0で事実扱い→Astraが不在断定へ強めた新腕固有の経路。3-4の5) |
- 出荷された本文に重大を残さずに済んだ、という意味での『安全装置の働き』は確認できないが、**STOP9件中8件は重大でない根拠で人手介入になった**(暫定、確信度はworkerごと)。新旧とも同様で、過剰ブロックの質は両腕で似ている。新腕固有の別経路の候補は、B1・単複floor(機械)と、指示文の本文化(semi、3-4の5)。**注記(B3)起因の過剰ブロックは確認0件**(central新R0の周辺扱いが候補1件、因果は未検証)。

### 4-2. 案B(旧腕)とB1(新腕)
| 腕 | 発動 | 起点の指摘の重さ | 結果 |
|---|---|---|---|
| 旧 案B | small_bag, byd, openai | 全て軽微(2件ずつ) | openai: 完走。small, byd: Advは解消したが**Standardで別の軽微が出てSTOP**(収束せず) |
| 新 B1 | hormuz(軽微)、space(**問題なし**=hookの修辞)、openai(軽微境界=CMI主体) | 軽微/問題なし | hormuz: 完走。space: 起点は解消したが回復後JAの不在断定(軽微)が増え、Std STOPは回復後ENの単複差。openai: 起点は解消、新JA見出しの一般化で再MAJOR→1記事1回でSTOP。semiconductor: Trial上限3/3で拒否→STOP |

### 4-3. B1の費用対効果
- B1 3回の再支出 raw約¥103。完走に至ったのは hormuz の1件のみ(成功率1/3)。回復枠が無ければhormuzはAdv EN STOP(起点は軽微)で終わっていたので、『軽微指摘をSTOPから救った』効果はこの1件。space・openaiは回復後も別の軽微でSTOP/Std STOP。semiconductorは枠切れ。**純効果は疑問(¥103で完走+1)**。枠の消費順(hormuz→space→openai)が後のsemiconductorの拒否を決めた**順序依存**があり、反実仮想は未実行(再実行はcherry-picking禁止)。

### 4-4. M1・M3・Rewrite・Checker
- M1: 発火1(space新Adv、B1前の要約MAJORを解消)。最終本文には残らなかった(3-4の3)。Standardは未実装。効果の一般的評価は不能(n=1)。
- M3: 新腕の保護6(byd5,small1)。保護で拾えた真の問題は3 workerとも0件。旧腕の影5は全て台帳一致の記述で、保護しても救出なし。**v2: 便益・コストとも観測不能(床効果。母数が小さく重大が両腕0のため、M3が守った/害した影響は本Trialでは見えない)**。
- Rewrite(新2/旧7イベント): 新=space Adv 単複修正(軽微境界、有効・副作用小)、byd Adv(不要、比喩ジョークの削除)。旧=openai Std 1(任意改善)、semiconductor Std 2(不要、1件は限定句『not the whole semiconductor segment』を削除する軽微劣化)、streaming Std 4(BLOCKINGは小数点断片、3件は結果として軽微が直る、1件はPremium差額文ごと削除する軽微劣化)。**旧7件中6件は小数点断片(『$29.』等)起因、劣化2件**。
- Checker BLOCKING偽陽性: byd新Adv『現場と広報が連絡していない』(比喩、不要Rewrite)。Stage2指摘の大半は決定論検査(否定・因果・fact_id欠落)や比喩文への反応で、ACCEPTABLEに降格。

## 5. 観察・仮説

### 5-0. Fableの突合メモの検証結果
| メモ | 結果 | 根拠・補足 |
|---|---|---|
| 出荷本文の重大見逃しは両腕0、境界は人間確認 | **一致** | 3 worker一致。出荷本文に残る境界は4〜5件(B-02,03,05,11,B-04のAdv) |
| 新腕はJA段の台帳外主張が大幅に少ない((ii)2対15、R2 FC MAJOR 0対4) | **部分一致** | 数字は一致。ただし(a)旧(ii)15のうち7(small3,byd4)は案B前本文の値、(b)最終JA由来に限ると新2/旧8、(c)ラベル上は旧(ii)の大半が問題なし(semi4件全て台帳内、openai・streamingも問題なし)で実質の軽微はspace旧1+semi旧1、(d)旧FC MAJOR4のうち重大(境界)1(meta)・軽微1・偽陽性2、(e)w1: 新腕space JAには旧腕と同型の不在断定が残るが(ii)=0=検出器の注記依存の疑い(未検証)。軽微JA列の差(5対9)は小さい(符号検定p=0.31) |
| 新腕のEN STOP4件とB1発火3件の根拠はラベル上は軽微または偽陽性、B1の純効果は疑問(¥103) | **一致** | 4-1/4-3。EN STOP: 軽微3(space Std単複、byd Std目的表現、openai Adv見出し)+偽陽性1(semi)。B1: 軽微2+問題なし1 |
| semiconductor新のEN STOPはB3注記のunmapped qualifier由来(AMBIGUOUS由来でない) | **帰属を訂正(v2、Opus指摘)** | v1の『B3注記のqualifier文由来』は誤り。原因文は**注記前のB3 Storyline本文**(`shared/brief_original.md` L7、旧腕briefにも同文)の指示文。新腕でFact Lock R0が本文化→【事実1】タグ(`new_writer/r0_with_tags.md` L11)→Astra R2が不在断定へ強め(`r2.raw.md` L13)→EN検査MAJOR(`b1b/audit/deviation_checks/advanced_attempt1.json` L20)。AMBIGUOUS(F1)由来ではない。unmapped_claims(qualifier)には該当するため§5-11の『B3由来』として別集計(Adv STOP 新1/9、人手介入 5対6、判定不変)。B1はTrial上限で拒否 |
| central_bank新のR0 STOPは『30年固定』の範囲拡張(注記で周辺扱い)が影響した可能性(未検証) | **候補1件(因果は未検証)** | 注記は『30年固定』を`name_embedded`=常に周辺(`shared/annotation.json`)とし、briefに【周辺数値】タグが付く。**注記なしの旧briefと本文は同一**(タグの有無だけが差)。Fact Lockは周辺数値を固定しない設計のため、Writerが言い換えた可能性はある。ただしbrief事実5・6自体が『固定型』『固定住宅ローン』と総称語を使っており、そこから拡張した可能性もある。アブレーションは禁止のため因果は未検証。**注記起因の過剰ブロックとして確認できたのは0件、候補はこの1件のみ** |
| Checker欠陥候補: 旧Standardの小数点文分割断片が独立claimとしてBLOCKING化、不要Rewrite 6/7、軽微な劣化2 | **一致** | w3の集計。さらに新腕でも断片は出る(space Checker Adv、streaming新Adv)が、新腕はQUALITY止まりでRewriteに至らなかった(なぜ違うかは未検証) |
| 旧腕(ii)は案B前本文の値で、small_bag/bydは最終JAを表さない | **一致** | w2確認(sha不一致: small 7275f…≠eac0a2…、byd 684e2c…≠a091e3…) |

### 5-1. Writer段の良化
FC MAJOR(0対4)・(ii)(2対15)はいずれも新腕が良いが、**FCは同系列モデルの自己判定**であり、ラベル上は旧腕の指摘の大半が偽陽性だったため、『実質の良化』は軽微JA列の5対9(対6テーマ)程度にとどまる。JA字数は新931対旧740(新が長く、盲検上も文体差で腕が推測できる)。面白さは未評価。

### 5-2. EN段の過剰ブロック
新腕のEN STOP4件はいずれもja_sourceまたはtranslationの**軽微/偽陽性**でSTOPしており、旧腕のStd STOP2件も案B後の軽微。EN deviation checkはMAJORを『軽微相当』でも付けるため、B1/案B/must-fixが軽微でSTOPに至る構造は両腕共通。新腕固有の要因(候補): 単複差に対する機械floor(changed_number)、brief内の指示文がFact Lock R0で本文化され事実扱いされる経路(semiconductor、3-4の5)、B1の1記事1回/Trial3回上限。**B3注記そのものが原因と確認できた過剰ブロックは0件**(v1の『注記由来』は訂正)。

### 5-3. 注記(周辺扱い・qualifier)の副作用
(a)周辺扱い=central新R0 STOP(因果未検証、**注記起因の候補1件のみ**)。(b)v2訂正: semi新EN Adv偽陽性STOPは注記のqualifier文ではなく、**注記前のbrief内の指示文**がFact Lock R0で事実扱いされた新腕固有の経路(3-4の5。unmapped_claims qualifier該当のため§5-11の別集計に入れた)。(c)注記ありで新腕の(ii)が0に近い一方、space新JAには不在断定が残る=検出器の注記依存の疑い(未検証)。**v1の『新腕のSTOP5件のうち少なくとも1〜2件は注記起因の可能性』は撤回**(確認0件、central 1件が未検証の候補)。B3注記は人手(Sonnet)注記の上限性能であり、自動注記でProduction化した場合の副作用は未測定。

### 5-4. Checkerの文分割欠陥
旧腕Standardで小数点分割の断片が独立claim化→BLOCKING→不要Rewrite(7件中6件)、2件で軽微劣化。Checkerのclaim分割(runner/Stage 1)の欠陥候補。新腕では断片がQUALITYで止まりRewriteに至らなかった(原因は未検証)。**v2訂正: 『新腕はChecker欠陥に強い』とは言えない。新腕のChecker run完了は旧より少なく(10対12、Adv STOPでStdが未実行になる記事を含む)、欠陥に当たる母数が少なかっただけの見かけの可能性が高い。**実装修正は本委任の範囲外。Production Checkerの同型分割器の有無は7節。

### 5-5. B1の費用対効果
4-3節。raw約¥103で完走+1、順序依存あり。Production等価性規定で『1記事1回』『Trial全体3回』としたため、反実仮想(上限なし)は未測定。

### 5-6. Astra実測単価
R1+R2を1生成として raw¥30.6(guard¥45.8)。設計見積¥27〜34の範囲内で、見積の乖離は小さい。新腕1記事(JA完走・B1再支出除外)は raw約¥36対見積約¥42で見積以内。**請求ダッシュボード照合は未実施**(guardはx1.5の安全係数)。

### 5-7. 層別逆転(人手介入必要率: 旧4=新0.125対旧0.625、新5=新0.50対旧0.10)の説明(v2、Opus指摘。妥当順)
1. **B1枠の消費順による移転(事実)**: Trial全体のB1上限3回を旧4が先に2回(hormuz・space)消費し、新5のopenai(3回目)で尽き、semiconductorは拒否されてSTOP。新5の新腕STOPの一部は枠の順序依存。
2. **開発セットへの適合**: 旧4=meta/hormuz/space_weapons/small_bagはFact Lock/Astra matrixの**開発テーマ**、新5は**out-of-sample**。新5の新腕介入5/10対旧1/10は、**汎化性能の正直な推定値**(旧4の良い数字は開発セットへの適合を含む)。
3. **偶然**: n=9、各腕n=1生成、LLMの揺れは推定不能。
4. **B3形式**: 新5の新腕STOP(semi=指示文の本文化、central=周辺扱い候補)にB3の箇条書き化・タグ付けが関与した可能性(推測)。
5. **注記粒度**: 確認できた注記起因はなく、central新R0の周辺扱い(候補1件)のみ。
- 結論: 旧4での新優位は開発セット適合とB1枠の移転で割り引く必要があり、新5の方向(新腕が多い)は汎化性能の目安として重く見る。全体の『同等・混在』判定は両方を足した結果であり、新腕の安全上の良化を示さない。

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
- (v2)ラベル基準の不統一: semi(不在断定=偽陽性)とspace B-02/B-03(軽微)は同型だが別々のworkerが別の基準で付けた。統合ラベルの`qa_note`に同型メモ(OC-8)を残したが、ラベル値は原本のまま。
- (v2)3-3の境界例・重大0は、いずれもSonnet暫定。ユーザー回答(B-05など)で2-1のフラグが変わりうる。
- (v2)面白さは未測定(人間1名のpairwise 3対を追加しただけで、統計的な比較ではない)。
- Production採用提案前には**Opus独立技術レビュー(条件C)**が必要。本書は採用提案ではない。

## 7. OPEN項目候補一覧(起票はFable判断。`OPEN_ITEMS.md`は未編集)
**優先度(v2、Opus推奨)**: 最上位=**OC-1**(Checker小数点文分割、現Productionにも効く、決定論修正・低コスト)。次点=**OC-3**(軽微/重大の線引きによる過剰ブロック是正)、**OC-8**(不在断定の基準)。

| 優先 | 候補 | 内容 | 根拠 |
|---|---|---|---|
| 1 | OC-1 Checker小数点文分割 | 『$29.』等の断片が独立claim化→BLOCKING→不要Rewrite、限定句・差額文の削除という軽微劣化。**Production Checkerにも同型の分割パターンが存在(7-1)** | 旧腕Std 7件中6件、劣化2件(w3)。新腕でも断片は出る |
| 2 | OC-3 EN段ja_source/translation MAJORの過剰ブロック | 軽微相当のMAJORでB1/案B/must-fix→STOPに至る(EN STOP新4/旧2のうち重大の根拠なし)。重大度による回復・STOPの分岐は設計案(実装不可、仕様はユーザー決定要) | 4-1節 |
| 3 | OC-8 不在・非公開の断定、単複差の基準 | 台帳が『補わない』と指示しただけの事柄を『示されていない/秘密/説明がない』と断定(space両腕、semi新ENの偽陽性STOPは同型)。単複差はREPORT 5-3 #2未決 | B-02〜B-04、3-4の5。S系質問で確定 |
| 4 | OC-11 指示文の本文化(新設、v2) | briefに書かれた『〜付け加えないこと』等の指示文を、Fact Lock R0が本文化して事実タグを付け、Astraが不在断定へ強める新腕固有の経路 | semi新、3-4の5。R0プロンプト/brief分離の対策案(8節c) |
| 5 | OC-9 M1のStandard枝・B1後の再出現 | StandardにM1が無い。B1(JA再生成)でM1の効果が上書きされる | 3-4の2・3 |
| 6 | OC-7 FC/EN deviation判定の再現性 | 同一本文でCOMPLIANT/MAJORが割れる(space新shadow、byd旧m1a、small_bag旧Adv/Std) | 5-2節 |
| 7 | OC-4 B1回復の扱い | 純効果が疑問(¥103で完走+1)、Trial上限の順序依存、回復後に別軽微が出る。B1回復は『軽微は局所修正/注記付き出荷、重大のみ回復かSTOP』案(**仕様変更=ユーザー決定**) | 4-3節 |
| 8 | OC-5 B3注記の副作用 | 周辺扱い(30年固定)がcentral新R0 STOPの候補(因果未検証)。**v2訂正: qualifier文の注記由来STOPは確認0件(semiの原因は注記前のbrief内指示文)** | central新R0 |
| 9 | OC-2 B3自動注記 | Production化には自動注記が必要。人手注記は上限性能 | 事前登録3節 |
| 10 | OC-6 集計scriptの帰属誤り | EN STOPのレベル帰属(旧腕Std→Adv)、M1発火=attempt2存在(Stdで誤) | 3-4節。修正は別委任、`AGGREGATE.md`は再生成が必要 |
| 11 | OC-10 面白さの比較 | 新腕の字数・文体差が大きい。pairwise(人間1名・3対)は本委任で追加、AI評価・拡大は未 | 5-1節 |

### 7-1. Production Checker文分割器の配線確認(v2、Grep結果)
- Production経路の実行コード `er052_open233_self_recovery_flow_runner_01.py`(`er052_open233_e2e_acceptance_01.py` が`import ... as runner`で使う。`er052_output/open233_prod_e2e_02`はその出力置き場)に、**小数点で文を割る分割パターンがある**: (a) `split_sentences_generic`(L4591-4598): `re.split(r"(?<=[。！？.!?])\s*", ...)` — 実測で `"The annual price will rise by $25.99 per year. Next sentence."` → `['The annual price will rise by $25.', '99 per year.', 'Next sentence.', '']`(数字の間のピリオドでも割る)。呼出し箇所: 位置比計算(L4687)、precheck対象文特定(L8399)、`ja_fail_open_guard`の非JA分岐(L8015)、同一fact位置展開(L1759)ほか。(b) `locate_best_sentence`(L4434): `re.split(r"(?<=[。.!?])", full_text)`(同型)。(c) `er052_output/open238_precheck_fix_trial_01/tools/precheck_baseline.py` も同ロジック(コメントに『runner.split_sentences_generic と同じ』)。
- **断定できないこと(未検証)**: 旧腕Std Checkerの断片claim(例『The annual price will rise by $25.』)の発生箇所が、上記の分割器か、LLM(Stage 1)によるclaim列挙か。claim_in_articleがStage 1の出力であることは確認したが、断片化の起点は未特定。したがって『Production Checkerに同じ欠陥がある』とは断定せず、『同型の分割パターンが存在し、旧腕(=Production相当)で断片claimが実際に出ている』と記録する。起票時の最初の調査(¥0)は、断片claimが分割器経由かLLM列挙かの切り分け。

## 8. 次の選択肢(ユーザー提示用、Opus推奨順。費用は**推定**であり確定値ではない)
| 順 | 選択肢 | 内容 | 推定費用 |
|---|---|---|---|
| (a) | 人間確認3記事+面白さpairwise → 方向判断 | `HUMAN_CHECK_E2E_01.md` の事実確認3記事(byd/openai/central)+基準質問1+面白さpairwise 3対(6節) | ¥0 |
| (b) | Writer非依存の修正をOPEN化し、凍結JAでEN段+Checkerだけ再実行 | OC-1/OC-3/OC-8を起票→凍結した既存JAを使い、EN段+Checkerのみ再実行(Writer・Astraを再生成しない) | 約¥30〜150 |
| (e) | Fact Lock+Astraの判定基準を組み替えて次Trialを事前登録 | 判定基準を『安全で非劣性+面白さで優越』へ。事前登録のうえ次Trial | 設計は¥0、実行は別途 |
| (c) | 指示文の本文化対策→最小実験→新5再実行 | R0プロンプト/brief分離。最小実験3本(EN検査再現性¥10〜30、R0指示文あり無し¥5〜15、central周辺扱い¥5〜10、合計約¥20〜55、別管理ID)で再現性確認後に新5再実行 | 最小実験約¥20〜55、新5再実行約¥180〜230 |
| (d) | R1止め・モデル変更は保留 | 面白さのデータが出るまで保留 | ¥0 |
- 上記の費用は全て**推定**(実測の裏付けは1-2節の単価のみ)。B1回復の見直し(軽微は局所修正/注記付き出荷、重大のみ回復かSTOP)は**仕様変更でありユーザー決定事項**。

## 9. 付録: 成果物と再現
- `eval/merge_labels_01.py`→`labels_merged.jsonl`(553行、重複グループ46、worker間テーマ重複0。v2: 8行に`qa_note`追記[OC-8同型メモ]、ラベル値は不変)、`labels_merged_stats.json`。原本 `labels_w{1,2,3}.jsonl` は不変。
- `eval/judge_table_01.py`→`judge_table_01.json`(機械判定と根拠数値)。`eval/build_human_check_01.py`→`HUMAN_CHECK_E2E_01.md`(v2: 6節 面白さpairwise 3対、MAPは`eval/_private/PAIRWISE_MAP_01.json`)。
- 再実行: `python merge_labels_01.py && python judge_table_01.py && python build_human_check_01.py`(API不要)。
