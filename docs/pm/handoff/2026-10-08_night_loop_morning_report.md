正本: 2026-10-08 夜間自律ループ統合報告。新チャットで『朝の報告を出して』等の指示があれば、Fableはこのファイルを★★★報告ここから★★★〜★★★報告ここまで★★★ブロックで逐語再掲する(要約・省略禁止、PM_GOVERNANCE 12-4-1)。

★★★報告ここから★★★(夜間自律ループ 統合報告)

**1. 現在の状態**
- 夜間ループ終了。Status=**USER_DECISION_REQUIRED**(朝の判断6点)。夜間実費 **≈¥248/¥1000**(残≈¥750は使わず終了。追加テストの期待情報量が低いためOpusも終了に賛成)。
- Production変更なし。新規挙動は全てスイッチ既定OFF。全成果物commit・push済み(最終 `78e83126`)。Opusレビュー4回(戦略/条件A/条件D診断/総括)。

**2. 何をやったか(時系列)**
- 段階0(¥21): 既知NG 140件の再分類、危険文規則の検出率/負荷、関係抽出の反復安定性(2回)。
- 設計v1→Opus条件A→v2、W1/W2バグ修正、Stage1候補化率測定(¥0)。
- 段階2(¥158、うち≈¥68は二重起動と規則修正の再実行による無駄=開示): ①構造要素Rewrite規則v2+②読者信念テストのoffline replay(dev→held-out 1回)。
- Opus条件D診断→T1 決定論の反転型検出(¥0)/T2 ①v3(¥18)/T3 文→factリンク精度(¥25)/T4 狭い対判定×モデル比較(¥26)。
- Opus総括レビューで私の結論の言い過ぎ7点を訂正(以下は訂正後)。

**3. 何が分かったか**
- **有効(限定付き)**: **①v3**=構造要素(タイトル・見出し・一行要約・Hook)の書換えを「役割クラス(人/AI/組織/利用者)の部分集合」で照合し、語り枠(I/you/問いかけ)を保持。事前登録6ライン全PASS(21試行: 違反0・STOP 7→1・盲点2種解消・削除0)。限定: N=21、cycle1のみ、再Recheckで15/20がDEVIATION(cycle2未検証)、`someone`型の穴、面白さ未確認。**W1/W2**(タイトル記法の喪失・構造要素Recheck未配線)はバグとして修正済み(テスト1071件PASS)。
- **無効(今夜の条件下)**: ②Stage2への「読者信念テスト」追記=狙った誤判定12件中1件しか直らず、無関係な候補のBLOCKINGが+237%・削除+0.59/記事→**打ち止め**。決定論の反転型検出=再現率1/6・0/3、記事の85%に印。関係抽出の中核化=述語・限定語が不安定。規則ベース危険文=検出80%/負荷40%不成立。狭い対判定(現行/上位モデル)=8/21でr3(11/21)を下回り、Aの反復一致76%で差は識別不能(「上位化しても無効」とまでは言えない)。
- **学び**: Checkerは「文がどのfactの話か」の近傍候補をかなり持っている(support∪relatedで19/21・14/14。ただし事前登録指標ではFAIL=厳密一致42.9%、正解表は人間未確認)。弱点は「整合しているか」の判断で、今夜試した2形式(rubric追記/周辺文なし1文×1fact)では改善しなかった。重大2件(jb9k・89wf)は狭い対判定の`asserts_unstated`(未提示なのに不在と断定)で両モデル検出(N=2、held-out誤検出4/14と同ラベル、負荷未測定)。既知軽微NGのラベルはLLM単独評価で人間確認は2件のみ(軽微の一部はラベル誤りの可能性)。
- 未検証のレバー: Checker側=周辺文を渡す判定・CANDIDATE側リンクの活用/台帳側=多義語正規化(OPEN-237 P'、方向型は既知NG最大の塊6/21)/Writer側=モデル・温度(決定Aに触れない)、最小禁止事項(決定Aに触れる)。
- 新たな潜在欠陥: r3が返すfact IDの略記(E009等、5.1%)が決定論検査を素通りしている可能性(¥0で要確認)。

**4. 何が残ったか**
- (1) ユーザー判定(クリティカルパス): 人間確認パック上位10件+盲検ペア3組+「どの条件でも検出されなかった軽微8件」の許容可否。
- (2) ¥0調査: ID略記の素通り確認、OPEN-240(過去Trialのテーマ入力バグ)の範囲確定。
- (3) 限定範囲(r3がCANDIDATE化しStage2が格下げした文のみ)で狭い対判定を「格下げ拒否信号」に使うTrial(負荷測定、少額)。
- (4) ①v3+W1/W2でcycle2込みのE2E小N+面白さ盲検(Checker候補構成化と条件Cの前提)。
- (5) 台帳の多義語正規化の設計。
- SSOT反映(REPORT §103〜、DECISION_LOG)は判断後に実施。

**5. ユーザー判断**
- **判断1**: ②(Stage2 rubric追記)の打ち止め・スイッチOFF維持の確認。推奨: 確認。
- **判断2**: ①v3+W1/W2をChecker候補構成へ組み込む(Trial採用。Production配線は別途条件C)。推奨: 採用(cycle2込みE2E小Nで確認してから)。
- **判断3**: 反転型(未提示→不在断定・事実反転)の扱い=狭い対判定を「格下げ拒否/人間確認の優先信号」に限定して使う(直送はしない)。推奨: 採用(負荷を測ってから)。
- **判断4**: 軽微の関係型の方針。(a1) Writer最小禁止事項(決定Aに触れる・面白さリスク高)/(a2) Writerモデル・温度(決定Aに触れない・盲検読み比べ必須)/(b) 軽微は許容し「重大+人間10%枠」で運用へ/(c) 台帳の多義語正規化(方向型に効く、Writer・Checker不変)。**推奨: (b)を基本に(c)を並行、条件=判断5で軽微サンプルが許容されること・優先信号が10%枠内**。根拠: ユーザー前提(面白さ生命線・重大ゼロは求めない)と整合、Checker側は今夜の範囲で頭打ち、Writer側は面白さリスク未測定。「不安定すぎる」への直接の手当ては①v3のSTOP減少(7→1)。
- **判断5**: 上記(1)の人間判定(約20〜30分)の実施可否。推奨: 実施(次に効く情報は人間のラベルで、API費用では買えない)。
- **判断6**: OPEN-240調査とID略記確認(¥0)の実施可否。推奨: 実施。

**6. 補足**
- 主要URL: 総括レビュー https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/opus_l2_review_night_loop_summary_01.md / 段階2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_stage2_01/eval/STAGE2_RESULT.md / ①v3 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_stage2_01/v3/T2_RESULT.md / T1 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_reversal_detect_01/T1_RESULT.md / T3 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_link_precision_01/T3_RESULT.md / T4 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_pairwise_judge_01/T4_RESULT.md / 人間確認パック https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_stage2_01/eval/HUMAN_REVIEW_PACK_STAGE2.md
- commit履歴(夜間): `d1d59461`→`ae7d069e`→`88558158`→`221180cf`→`c331a079`→`78e83126`。
- 限界: 全てN小・単独LLM評価中心・人間確認は2件。根本設計見直しの条件(a)(b)(c)は未該当/判定不能のままで、現行の枠は維持。
- 用語: 役割クラス=主語を「人/AI・システム/組織/利用者」などの少数の型に写して比較する方法/`asserts_unstated`=台帳が述べていないことを存在・不在として断定している、という判定ラベル。

★★★報告ここまで★★★
