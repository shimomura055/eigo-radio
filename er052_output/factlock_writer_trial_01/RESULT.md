# RESULT: FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_02b(Status=MEASURED、Trial、Production変更なし)

3セル同一パック・セル非開示の盲検採点(72本 = baseline[5.6現行] 24 / all6[6現行] 24 / factlock[6+Fact Lock] 24。各評価者に各セル12本ずつ)。評価はLLM単独判定(gpt-5.6-luna / gpt-6-luna、rubric適用)、人間確認前。しきい値なし・有意性は主張しない。

## 1. 主指標(JA R2・EN、`eval/SUMMARY_FL.md`)
| 区分 | 指標 | baseline | all6 | factlock | FL-all6 | FL-base |
|---|---|---|---|---|---|---|
| JA R2 | 重大(件) | 0 | 1 | 0 | -1 | 0 |
| JA R2 | 軽微(件) / 記事(分母=R2本文あり 22/22/24) | 12 / 0.55 | 7 / 0.32 | 5 / 0.21 | -2 / -0.11 | -7 / -0.34 |
| EN | 重大(件) | 1 | 1 | 0 | -1 | -1 |
| EN | 軽微(件) / 記事(分母=EN本文あり 21/19/19) | 17 / 0.81 | 13 / 0.68 | 6 / 0.32 | -7 / -0.37 | -11 / -0.49 |
| R0 | 重大 / 軽微(件) | 1 / 11 | 1 / 8 | 1 / 4 | 0 / -4 | 0 / -7 |
| 全体 | 保留/記事 | 0.46 | 0.33 | 0.21 | -0.12 | -0.25 |
重大は「ユニーク項目」では baseline 1(EN)、all6 1(JA R2+ENの同一項目)、factlock 0(R2・ENとも。R0にのみ1件=hormuz/b3/r2の因果断定、R2で解消)。
軽微NGを含む記事数: JA R2 11/6/5、EN 12/11/5(baseline/all6/factlock、各24本)。テーマ別・評価者別・型分布は SUMMARY_FL.md。軽微の方向は3テーマ・2評価者の双方でFLが最少(ただし重大の差は0〜2件で判断不能)。

## 2. 悪化項目
- 面白さ pairwise(副指標、6-luna LLM判定、同brief対24対x順序入替2回=48判定): factlock 13 勝 / all6 35 勝 / tie 0。brief対単位で2回とも同方向: all6一貫14、factlock一貫3、割れ7。理由は「比喩が重なり作り込みすぎ・窮屈」が factlock 側への批判として多い(理由文のA/B帰属を機械割付した概算で、factlock側への批判語 35/48、all6側 6/48。目視確認は未実施)。
- 費用/本: factlock ¥4.94 vs all6 ¥3.91(+¥1.03)。baseline ¥9.27。所要時間/本: 410秒 vs 313秒(all6)、458秒(baseline)。
- STOP率: 3セルとも 5/24(factlock: EN deviation 4 + JA再確認 1)で差なし。
- 形式: R2のタグ付き文が JA recheck(案B)経路の2run(hormuz/b3/r1、space_weapons/b4/r2)で ja_writer/*.md に未除去タグが残った(harness側の欠陥、下記3)。
- 照合(i)の不整合はR2で13文/189(6.9%)。うち space_weapons/b3/r2 の1runに偏在(Writerが存在しない番号 F11/F13/F16 を付与、unsupported主張13件。判定artifactの可能性)。

## 3. harness欠陥の所見(測定のみ。修正なし)
phase2 のJA再確認(案B、ja_source由来のEN MAJOR時)で JA R0/R1/R2 が再生成され、`ja_writer/original.md / revision1.md / revision2.md` が**タグ付きのまま**上書きされる(hormuz/b3/r1 は completed でも発生)。postprocess_phase1(照合・除去)は phase1 後1回のみなので、この再生成分は除去・照合されない。本Trialでは該当2本を盲検コピー作成時に harness の strip_tags で追加除去(セル漏洩防止、MAPに `blind_tags_stripped` 記録)。2本とも factlock_check_*.json は再生成前の本文に対する値。Production採用検討時は要修正点。

## 4. 照合指標(`eval/FACTLOCK_CHECK_SUMMARY.md`、24本)
| 段 | タグ付き文 | 整合/不整合/判定不能 | 主張 supp/unsupp/undec | タグなし文 neutral/brief事実/推量/一般/新規具体 |
|---|---|---|---|---|
| R0 | 195 | 171/13/11 | 335/21/8 | 122/109/31/6/7 |
| R1 | 192 | 174/14/4 | 346/23/2 | 152/127/26/5/4 |
| R2 | 189 | 169/13/7 | 338/24/3 | 187/122/17/1/4 |
数値(iii): 不一致 R0 1 / R1 1 / R2 5(R2の4件は漢数字「一件」「一人」の誤検出で実質は約2.6%の約の脱落1件のみ)。core_used_without_tag 26/11/12、marks_echoed 0、数量語 3/1/4。タグ除去後の残存「【」: 全72段で0、広め除去のみで消えた変形タグ 0。R0→R2のタグ付き文: 維持77/改変61/削除57/added51/number_changed 1。照合はWriterと同系列モデルの自己判定で、盲検rubricの代替ではない。

## 5. 案A(名称内番号を省く)所見 / 文体
space_weapons 8本のR2目視: COSMOS 1408 は「衛星」「自国の衛星」へ、Outer Space Treaty 第4条は「宇宙条約」へ(いずれも番号なし)。5例(b1r1・b1r2・b2r1・b4r1・b4r2)で日本語として不自然な省略は見当たらず(特定性が下がり、聞き手が衛星名を検索できない点は損失)。hormuz は「同日」「翌日」で日付を代替し自然。文体: 比喩の重なり(舞台・探偵・衣装替え等)で窮屈と評された記事が多い(pairwise理由)。原因が Fact Lock かR0 prompt か、brief注記の影響かは分離不可。

## 6. 費用(raw_usage_log再計算、USD/JPY=160)
生成24本(smoke含む) ¥118.5(うち照合LLM ¥30.3、Checker ¥39.3)+ 盲検採点72本 ¥52.5 + pairwise 48 ¥2.2 = **¥173.2 / 上限¥150**(超過¥23.2)。超過は盲検採点で5.6-lunaジャッジ(¥1.5/call、36呼出)を使う運用(all6側と同一)と、所定の同一パック72本が原因で、承認済みscope内・原因把握済み・異常retryなし・残作業なしのため記録して継続。

## 7. 限界(PREREG 5a「言えないこと」再掲)
- 5要素のどれが効いたか(同時変更で分離不可)。
- 3テーマを超えた一般化(反復はbrief内で相関)。
- 重大件数の差(0〜2件程度で判断不能)。
- B3が中核数値を選んだ場合の性能(中核数値の注記は実装者の手付け)。
- 照合(i)(ii)がWriterと同系列モデルの自己判定。
- 名称内番号を省く(案A)ことの読みやすさの良否(目視のみ)。
実施上: 評価はLLM単独判定(人間確認前)で、評価者実体の違い(5.6/6)・all6側評価との再採点差(別パックの評価とは独立)あり。STOPで未生成の段はNG0として現れる(R2本文あり 22/22/24、EN本文あり 21/19/19)。pairwiseの理由帰属は概算。
