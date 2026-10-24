# OPUS_REVIEW_REQUEST_08: 課題① X2pのProduction配線設計案の独立レビュー依頼(条件C: Production採用提案前)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_29 / 2026-10-24 / 依頼元: Fable(本書は実行層Sonnetが作成した依頼文案。起動はFable)
レビュー対象: `WIRING_DESIGN_06.md`(配線設計)・`ADOPTION_PROPOSAL_01.md`(採否資料)。根拠データ: `TRIAL_05/TRIAL_RESULT_05.md`(確定版)・`TRIAL_05/report_05_fable_labels_05_withcde.md`・`TRIAL_05/FABLE_BLIND_RESULT_05.md`・`TRIAL_DESIGN_06.md`・`ROOT_CAUSE_04.md`・`OPUS_REVIEW_07.md`(前回条件Aレビュー)。実装は`er112_kp_gm_trial_05.py`(DEV)。Production変更0・API 0。判断基準は`docs/pm/PM_GOVERNANCE.md` 11-3(条件C)。
結果の要点(事実): R hard-core 12出力でFAIL系 B0 10 → X2p 0(THIN 1)、held-out 10KPでB0=PASSからの悪化 0、Stage 2通常54KPで strict PASS→FAIL 0 / PASS→THIN 2(事前宣言基準適合)、単価 0.0585 → 0.1593円/call、追加call 0。Fable盲検の揺れ 7/10(緩い方向)、1 rep、Fable単独評価。

## 依頼する論点(それぞれ「妥当/要修正/不採用推奨」と理由を)
### 論点1: Prompt変更の副作用(N層の説明文化・直訳調・再利用性)
1. 通常54KPで35/54の文字列が変化し、THIN 2件は「文脈を取り込み過ぎて意味が狭くなる」型(`move in the other direction`→「売れ行きは逆に下がった」、`supply chain`→「…店に届く…」)。PASS文字列にも否定・場面の具体化(`add up`→「つじつまが合わない」等)が見られる。この副作用の大きさ・許容性は妥当か。key_phrase単体の再利用性という設計原則を捨てる(ユーザー承認事項)ことの帰結を、見落としなく列挙できているか。
2. 「同品詞・同程度の長さ、説明文にしない」規則と`naive_ja_conveys`の条件分岐は、説明文化(G2/G3で観測)を防ぐのに十分か。conveysの確証バイアス(yesが多いと形骸化)は`gloss==naive_ja` 0/85、conveys yes/partly/no=11/12/62 の分布からどう評価するか。
3. 文脈限定句の置換3箇所(WIRING_DESIGN_06 G-2)と few-shot「fall into」の扱い(新builderでは除外、既存builderには残置)は適切か。

### 論点2: Z repair経路・混在batch・A/B/C隔離
1. Z repair(`er026:1552`、current glossあり)を**非適用**とする推奨は妥当か。repair時に現行builderの字義寄りfew-shot・文脈限定句が残り、生成済みglossを字義寄りに書き戻す理論的リスクの評価。代替(repairにも意味欄を足す)を今回検討すべきか。
2. 混在batchを「call全体を現行builder、記録のみ」とする設計(分岐条件=pending全件が`is_fulltext_gloss_missing`)は安全か。実際に発生しうる状況の見落としは無いか(resume、HR解決後の再整合、partial失敗後のretry)。
3. A/B/C隔離の担保(`is_fulltext_gloss_missing`が偽 → 分岐に入らない、`fulltext_source_ref`の設定側がer105/canonicalizationのみ、WC-01/WC-05のtest)は十分か。共有module・共有`align_glosses`で見落としはあるか。

### 論点3: schema互換と実装方式
1. 新schema(Production必須欄維持、新3欄を`japanese_gloss`の前に挿入、`strict: true`)の互換性。下流(`apply_alignment_corrected`、`validate_item_corrected`、監査artifact、HR報告、Adv説明のsignature機構)への影響の見落とし。
2. 選択肢P(`make_alignment_fn`がmessage冒頭マーカーでschema/developerを切替、factory契約不変)対 選択肢Q(factory契約に`variant`を追加)。暗黙結合のリスク対 改修範囲の比較。推奨はどちらか。
3. validatorの新欄検査(欠落/enum外のみ不合格、`gloss==naive_ja`等はrecord-only)の設計は適切か。HR率を増やさない方針の妥当性。
4. 緊急退避flag(新経路のみOFF)を置くべきか。既存kill switch `EIGO_KP_GLOSS_ALIGNMENT` のみで足りるか。revert単位(単一commit)の妥当性。

### 論点4: 評価の十分性
1. 1 rep・Fable単独評価・判定の揺れ7/10(緩い方向)・held-out 10KP・X2pがR結果を見た後に調整された点・gating基準がX2p確定値を見た後に是正された点(開示済み)を踏まえ、採用提案の根拠として十分か。追加で必要な検証(追加rep、独立評価者、held-out拡大、developer文の因子分離、`rules_fulltext`での実測)と、その費用対効果(各数円)。
2. 因子の交絡: developer文(M_DEVELOPER対DEVELOPER_MESSAGE)・文脈限定句の置換・欄追加・規則追加(X2→X2p)が同時に変わっている。採用判断上、因子分離は必要か。
3. 過学習: X2pの規則追加は`sound no one asked for`型(意味移動)・一側面型への対策。Rのhard-core 4KPに最適化された可能性を、held-out/Stage 2の独立性でどこまで否定できるか。

### 論点5: 単価・速度
1. 単価 0.0585 → 0.1593円/call(約2.7倍、記事あたり+約0.1〜0.3円、70円目標に対し約+0.14〜0.43%)は、効果(hard-core字義訳NG 10/12 → 0/12)に見合うか。Cpとほぼ同単価である点(「Cpの約半額」想定の不成立)の含意。
2. 出力token約3.5倍・wall-clock増(粗見積+約8〜9秒/call)の記事全体への影響。timeout・rate limit・失敗率への懸念。
3. より安い代替(字義訳リスク型KPのみ新経路に回す選別、reasoning effortの調整)の有無と、今回検討しなかった理由の妥当性。

## 期待する出力
各論点について「妥当/要修正/不採用推奨」と理由、**見落とし**、**既存Trial/既存レビュー(OPUS_REVIEW_07等)との重複・矛盾の指摘**、WIRING_DESIGN_06への必須修正/推奨修正の別。Opusレビュー後はFableが11-3に従い照合し、STOP条件に該当しなければ次工程(ユーザー採否判断資料の提示)へ進む(Opusレビュー自体はユーザー承認Gateではない)。Production採用は人間ユーザーのみが承認する。
