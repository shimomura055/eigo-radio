# OPUS_REVIEW_REQUEST_01(条件A: 新しい処理フローのProduction導入 — Part 2 文法解説+Trial-08選定方式)

管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01 / 日付: 2026-10-25 / 依頼元: Sonnet(実行層)→Fable経由でOpus独立レビュー
レビュー対象(いずれも読み取り): `DESIGN_01.md`、`EXISTING_SPEC_CHECK_01.md`(同dir)、`er120_part2_grammar_production_01.py`、`er120_part2_grammar_production_01_test_01.py`(77 PASS・API 0)。
前提(変更しない): ユーザー正式決定(`docs/pm/delegation_log/2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md`): Part 2・Trial-08選定方式はAPPROVED_FOR_PRODUCTION。Tier内順位・HIGH判定・OTHER分類は承認対象外(レビュー対象外。指摘しても本案件では変更しない)。
状態: module実装済み・runner/er119/ページ未配線(次委任)。レビュー目的=配線前に設計の欠陥を潰す。判定は「実装へ進んでよい/修正後/不可」と必須修正(M)・推奨(R)で。

## O-1 Trial規則の移植忠実性(最重要)
主張: 承認済み規則は逐語で移植され、差分は安全側の6点(EXISTING_SPEC_CHECK_01 §5 D-1〜D-6)のみ。
証拠: (a)`STEPA_PROMPT`/`STEPB_PROMPT`がTrialとbyte一致(`test_A1`)、(b)Trial-08有料5作品の実送信prompt shaを再現(`test_A2`)、(c)Trial-07有料Step B 7件のprompt shaを再現(`test_A3`)、(d)Trial-07/08全29標本のraw応答を本moduleでparseし`select_tiered`の選定・tier・Tier表・features(逐語解決/連結再解決/prev/next)がTrialの保存結果と完全一致(`test_B2`。順位反転の変異でFAILすることを確認済み)。
観点: ①移植漏れ(`resolve7`境界・`_tn`の正規化・`strip_quotes`)の有無 ②D-1(parse不能を0件にせずSTOP)・D-3(Step B構造検査。実出力7/7通過)・D-4(T1訳を`ref_ja`としてStep Bへ渡す=Trial-07は未使用)がTrial規則からの逸脱として許容範囲か ③Step B参考訳の追加がTrial-07 USER出力の品質(特に【日本語訳】)を変えるリスク(Part 1との訳の一貫性という利点との比較) ④Trial-08で再抽出していない3作品(開いた窓・イグ・退屈)は、Production(STEPA8)では再抽出されるため結果が変わりうる点(承認範囲内か)。

## O-2 Human Review接続面(kind="grammar")
主張: `review_request()`/`select_from_candidates()`/`reselect_candidates()`が、KP HR DESIGN_01 §kの接続面(TOP1/TOP2=select_tiered順の先頭2件・追加LLM callなし・AUTO=TOP1・0件=省略)を満たす。
観点: ①`mode`(`wait`既定/`auto`は明示宣言のみ)とer119の`mode_declaration`の整合 ②`candidates_sha256`でstale reviewを拒否する方式の妥当性、再選定(API 0)と枯渇時の再抽出(`rejected_ids`)の組合せに穴(同一候補の再浮上・ID不安定)がないか ③0件を「待機しない」(ZERO)とする扱い(Humanが「本当は構文がある」と判断する余地がない)の妥当性 ④HR記録(修正内容・理由)の持ち場所(er119 history)と本moduleの`selection.source`/`rejected_ids`の役割分担 ⑤Human choiceが`top2`のとき他候補を「却下」と扱わない(NGではない)設計の確認。

## O-3 retry / regeneration / resume
主張: 技術retry1回→fail-closed。resumeは本文sha+label+Prompt sha+modelで候補・結果をAPI 0再利用。本文変更は再抽出+旧結果を`require_fresh_part2`が拒否。KP再選定はPart 2へ影響しない。
観点: ①`explain_signature`が材料欄(`construct_ja/points_ja/context_ja/prev/next`)込みで、再抽出のたびに(同じ候補IDでも材料が揺れて)Step B+訳が再生成される費用的リスク ②Zの`DEPENDENTS`(`er062:64`)へ`part2_b1b`を`r2`の従属に加える設計(Part 1は不要としたがPart 2は本文入力)と`--regenerate-stage`の整合 ③`incomplete`応答を構造失敗(retry対象)にする扱い ④Part 2失敗でKP/TTSを止めるか(fail-closed)・TTS前に配置する妥当性 ⑤外側retry(KP選定最大3回)との独立性。

## O-4 描画・組立・一致検証
主張: 保存artifactを使う側(TTS/Gate/Assembly入口・pages・X player/公開ページ)で`require_fresh_part2`を確認し、描画はPart 1ブロック直後に`include_css=False`で連結。選定文は本文の単一段落の逐語span。
観点: ①`require_fresh_part2`の検査項目(本文sha・signature・単一span・解説非空・候補ID)の過不足。Step B解説中の英文引用の逐語性は**検査しない**(Trialにない新Validatorを避けた)判断 ②0件時に`ZERO_P2`文面を表示する(Trial実出力に合わせる)vs KP HR DESIGN §kの「コーナーなし」の整合(Fable照合事項) ③Part番号を出さない(Dangling防止)方針 ④X旧構造記事(`###`見出し混在 2/26件)で見出し段落が本文段落として扱われる点(Trial同一挙動)の実害 ⑤`_paragraphs_html`(Part 1 moduleの私的関数)の再利用。

## O-5 レベル・Family適用範囲
主張: Production適用レベル=Advancedのみ(Step A''/Step Bの全Trial実績がAdvanced)。Standard(a2)へ広げない(新仕様)。A/B/C(strategy_l)非適用。
観点: ユーザー決定の『X/Y/Z共通仕様』との関係で、Standardを含めないことが「承認範囲の不当な縮小」にならないか(Part 1がAdvのみで承認された前例と整合) / 逆にAdvのみで十分とする根拠。

## O-6 Yの到達性
主張: Yには正式Production入口がなく(`production_reachable=False`、OPEN-484)、安全に配線できる部分は『module自体がFamily非依存で呼べる』ことのみ。Y Trial scaffoldへ配線しない。OPEN-484にY要件を追記する。
観点: これでPRODUCTION_WIRED(Yは対象外=入口新設時の受入条件)の扱いが適切か。

## 追加観点(任意)
- 新2 process(`STUDY_TEXT_GRAMMAR_EXTRACT/EXPLAIN`)の分離が原価監査に有効か、Part 1の`KEY_PHRASE_GENERAL_EXPLANATION`再利用で足りるか。
- 費用(`BUDGET_PLAN_01.md`): 0.43〜0.48円/セット(Trial実測)と、HR込みの上振れ(TOP2選択+0.11円・再選定枯渇+0.32円)の見積。
