# Opus条件Aレビュー (OPUS_REVIEW_01) -- 逐語保存

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / 委任_02A(Fable委任文から逐語転記、2026-10-31)。以下は「=====OPUS REVIEW=====」〜「=====END=====」の逐語。

=====OPUS REVIEW=====
### 1. 検証セットの妥当性(問題あり)
- **M-1 T2の再ラベルが片側だけで、結果が有利側に偏る。** TRIAL_PLAN_01.md:56 / EVAL_SET_01.md:40 では、警告が出たT2だけを裁定し、problemなら付け替える。警告が出なかったT2はproblemに変わる機会がない。「警告した=当たり」にだけ寄り、PrecisionもRecallも上振れする(discrepant analysisのバイアス)。修正案: T2全71件(とT4の14件)を、Trial実行前に、警告情報なしでブラインド裁定し、ラベルを確定・凍結する。実行後の付け替えは禁止。
- **M-2 held-outの「重大誤訳」が合成T3だけになっている。** T1のmajor 4件(verdict×2、things left out、charge)はすべてdev(EVAL_SET_01.md:26-29)。held-outのT1は4件すべてminor、うち2件は同じ表現(equivalent width)(:30-33)。held-outでの重大誤訳ガード(TRIAL_PLAN_01.md:33)は見つけやすいT3(反意・別義・別概念=6類型の1だけ、build_eval_set_01.py:91-96、EVAL_SET_01.md:44)で測ることになり実質素通り。修正案: 実行前に「巧妙型の合成T3'」を、6類型のうち2〜5について各3件以上作り、記事単位でdevとheld-outに振り分けてラベルを凍結。巧妙型の例=文脈上の意味→辞書第一義への一般化、比喩→字義・平板化、定訳→定義文への言い換え、不自然・冗長な訳。作成手順(類型ごとの作り方)を文書に固定し、特定の語を狙って作らない。重大誤訳ガードは「T1+T3'(巧妙型)」と「T3(易しい型)」に分けて判定。
- **R-1** T1は6表現で、すべてFamily X。verdictのStd/Advは同じ文で結果が連動。表現単位の件数でも報告。Y/Zの実誤訳でのRecallはM-4の全数ラベルで初めて得られる。
- **R-2** things left out(build_eval_set_01.py:194-205)は`comment_translation`で、HRで確認するKP/KW訳とは対象が違う。集計では区別して表示。
- **R-3 評価バッチの構成が本番とずれている。** view Aは公開項目だけで5件前後/level、view BはT3比率が高い(build_eval_set_01.py:231-247)。本番入力は12候補/level。修正案: 各バッチを同じ記事・levelの運用プール候補で12件まで埋める。埋めた候補は採点しないか、M-4のラベルで採点。
### 2. 基準率・P-a(問題あり)
- **M-3 運用プールの半分以上がdevで使った記事と重なる。** 261件中、ai_chat_sponsored・in_a_grove・melos・meta_waddle・redelivery_fee・untidinessはdev記事。dev項目そのもの(untidiness b1bのverdict「結論」、検察官)も含まれる。修正案: P-aは「dev評価セット項目を除いた集計」を主とし全体値も併記。どちらを主とするかを事前登録。
- **M-4 運用での見逃し(Recall)を推定する方法がない。有病率3〜10%に根拠がない(TRIAL_PLAN_01.md:27)。** 修正案(推奨): 261件全件をTrial実行前にブラインド裁定(API 0)。有病率・P-a・運用Recall・Y/Zの実誤訳が同時に得られ、§5-2の「警告項目と非警告項目を混ぜる」設計(TRIAL_PLAN_01.md:56)が不要になる。代替: 非警告項目から事前に決めた数(60件以上)を無作為抽出して裁定。
- **M-5 裁定の基準が事前に固定されていない。** problem定義表(6類型で「ユーザーが修正を指示する水準か」、好み水準はnormal)を事前登録。exclude(TRIAL_PLAN_01.md:57)は「FPに数えた下限」と「除外した値」の両方を報告。TP=項目がproblemかつreason_jaが実際の問題を指す。厳格TPと寛容TPを併記。
- **R-4 件数が少なく信頼区間が広い。** 有病率5%なら問題約13件、警告10件前後。8/10のWilson 95%区間は約0.49〜0.94。区間併記に加え、P-c(held-out)とP-a(dev除外)を事前に決めた規則で統合した値も副次として出す。良い方を後から選ばない。
### 3. 方式比較の設計
- **M-6 R_strict/R_default/R_looseから1つを選ぶ基準がない**(TRIAL_PLAN_01.md:34、DESIGN_OPTIONS_01.md:77-81)。修正案: 「dev重大誤訳ガード≥85%を満たす規則のうちdev P-c(なければP-b)が最大、同点ならRecall高」。effort(:7)も同形で固定(例: 上位effortより全指標が5pt以上悪化しない最も低いeffort。Q>Cなので判別できなければmedium以上を既定)。
- **M-7 held-out評価の扱いが未確定。** 「凍結構成 最大2つ」(TRIAL_PLAN_01.md:48)はheld-outの結果を見て選べてしまう。主構成を凍結時点で1つ指名、2つ目は参考。「各3回」の集計=主指標は1回ごとの指標の平均(と最小値)、多数決にしない。
- **R-5 M5の段2の掛け方。** 段2を「確信がhighでない/minor」に限ると、probeでhighと出た好み的な誤警告(clutter、DESIGN_OPTIONS_01.md:108)が素通り。段2を全警告に掛ける案を比較(約¥0.06/level)。suggestionの質が悪い場合(判決 vs 評決)「同等」と判定され正しい警告が取り消される。段2で取り消された警告のうちラベルがproblemだった件数を記録。
- **R-6 M6の「独立性」は限定的。** 生成も同じLuna(effort high)で同系統の誤読を再現しやすい。報告で限界を明記。代案: M2/M3のschemaに`context_sense_en`/`figurative(bool)`/`established_term`を先に書かせてから判定させる「分析→判定」型の変種(特定語に依存しない)。
- **R-7 M7の制約。** 運用プールに生成時メタ情報があるか未確認(DESIGN_OPTIONS_01.md:57)。M7はablationのみ、主構成候補にしない旨を事前登録。
- **R-8** R1bのeffort比較はM2だけ(TRIAL_PLAN_01.md:44)。R2で残った上位2方式についてもeffort 2水準を測る。
### 4. 一般化
- **M-8 Promptに特定語が入っていないことを機械的に確認。** Prompt変更時、評価セット115件のexpressionとcurrent_jaがPromptに入っていないことを機械照合しPASS時のみ`frozen_config.json`に記録。現在のprobe Prompt(probe_01.py:36-43)は適合。
- **R-9 類型6「記事内不整合」を検出する入力がない。** 入力は1 levelの項目だけ(probe_01.py:53-58)。probe Prompt(:40-41)は類型1〜5のみ列挙、schema(:29)の`inconsistent`を説明していない。修正案: (a)同じ記事のもう一方のlevelで同じ表現に付いた訳を参考入力に加える、または(b)HR段階では解説未生成のため類型6は対象外と明記(CURRENT_STATE_01.md:58)。R_defaultがunnatural_ja/inconsistentのminorを警告しない設計(DESIGN_OPTIONS_01.md:79)は類型5/6のRecallを設計上ゼロ近くにする。類型別Recallを必ず報告。
### 5. HR警告表示試作
- **M-9 DEVページから送った結果が本番として取り込まれる恐れ。** 署名・コピー文はProductionとバイト同一(HR_UI_MOCK_DESIGN_01.md:24-27)のため、DEVページからコピーして貼るとrestore/confirmに本番回答として通る可能性(未検証)。データも古いsnapshot。修正案: index.htmlに「DEV試作・ここから選定結果を送らない」常時バナー(form_logic.jsは変えない)。差分検証(3)に「DEVのコピー文をrestoreに通したときの挙動」を追加。
- **M-10 改善候補の表示が正しい訳を悪化させる恐れ。** 誤警告の改善候補を採用すると正しい訳が悪化(B3不採用と同型のリスク)。修正案: 「改善候補が妥当だった率(TPのうち)」「誤警告に有害な改善候補が付いた件数」を測定項目に追加。suggestionが現訳と同じなら表示しない。
- **R-10 「未検査」を区別して表示。** 検査失敗(API error・JSON破損・resultsに抜けたid)が警告なしと区別できないと見逃しが隠れる。項目単位では表示を足さず、level単位の既存status行(data_warnings、CURRENT_STATE_01.md:41)に「訳語チェック未実施(N件)」。probe_01.py:91はid集合照合・再試行・失敗扱いを未実装。Trialでは失敗・欠落を「警告なし」に数えず件数報告。警告ゼロ記事は表示なし(:39)。
- **R-11 重大度は2段に分けない。** 🔴/🟡は表示件数増。規則通過の警告だけを1種類で出す現設計(DESIGN_OPTIONS_01.md:82)が妥当。
### 6. QCD
- 費用見積はprobe実測と整合。運用+¥0.35〜0.6/セットも妥当な桁。
- **R-12 Capの見直し。** M-2、R-3、R-5、R-8採用で概算+¥8〜15。Cap ¥55〜60程度(¥300以下で自律範囲)。M-1/M-4の事前裁定はAPI 0だが作業時間増。並列化するなら裁定基準を共有して分担。
- 既存工程との重複: validate_item_correctedは形式チェックのみで意味検査と重複しない。生成呼出に検査を同居させる案はユーザー決定2に反し不可、という整理は正しい(DESIGN_OPTIONS_01.md:93)。
### 7. 事前登録の固定度
- (a) 合格判定の母集団が食い違う。TRIAL_PLAN_01.md:32「held-outおよびプール」、:29とFable(i)「P-a主」。一本化(M-11、必須)。
- (b) 重大誤訳ガード未達の扱いが食い違う。:33「不採用」、Fable(ii)「USER_DECISION_REQUIRED」。統一(M-12、必須)。
- (c) 規則・effort・主構成の選び方→M-6/M-7。(d) exclude・TP定義→M-5。(e) severityがagent案のまま(EVAL_SET_01.md:37)→実行前に確定・凍結。(f) T4のdev分はdev実行前に裁定(:55は「held-out前」のみ)。
### 総評
方式設計は堅実。最大の弱点は測り方: (1)片側裁定、(2)held-outの重大誤訳が易しい合成のみ、(3)P-aがdev記事と重なり見逃しも推定できない。対策=Trial実行前にAPI 0でラベル凍結(T2・T4・運用プールのブラインド全数裁定、巧妙型T3'追加)。合格母集団・規則選択・ガード未達時の扱いを一本化。UIはDEV送信防止・「未検査」可視化・改善候補の副作用測定で十分。
=====END=====
