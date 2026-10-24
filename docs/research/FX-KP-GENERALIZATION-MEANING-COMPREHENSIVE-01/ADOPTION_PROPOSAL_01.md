# ADOPTION_PROPOSAL_01: 課題① 日本語意味の字義訳対策(X2p)のユーザー採否判断資料

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_29 / 2026-10-24 / 作成=Sonnet実行層(Fableがユーザーへ提示する資料の素案。**VALIDATED判定・採用推奨はFable/ユーザーが決める。本書は事実と影響の整理**)
状態: X2pは**DEV/Trial専用**(`er112_kp_gm_trial_05.py`)。Production変更0。採用は人間ユーザーの `APPROVED_FOR_PRODUCTION` のみ。Opus条件C独立レビュー(`OPUS_REVIEW_REQUEST_08.md`)は未実施(Fableが起動)。
根拠データ: `TRIAL_05/TRIAL_RESULT_05.md`(確定版)・`TRIAL_05/report_05_fable_labels_05_withcde.md`・`TRIAL_05/FABLE_BLIND_RESULT_05.md`・`WIRING_DESIGN_06.md`。評価条件: gpt-6-luna effort=high、1 rep、Fable単独盲検(判定の揺れ 7/10、緩い方向)。

## 結論(先頭)
1. 字義訳NGの出方は「ランダム」ではなく、**特定の型のKPで系統的に出る**(下記1)。現行Promptは「本文での意味を確定する段」を持たず、さらに文脈の使用を制限する句がある。
2. 採用候補X2pは、**追加callなし**で、hard-core 4KPの字義訳NG 10/12 → 0/12にした(held-out悪化0、Stage 2の通常54KPで PASS→FAIL 0・PASS→THIN 2)。残る弱い点(THIN)は85出力中5件。
3. 代償は(a)1call単価 約0.059円 → 約0.159円(記事あたり+約0.1〜0.3円)、(b)出力tokenが約3.5倍で1callあたり数秒〜十数秒の増(粗い見積)、(c)**gloss規則の設計原則「key_phrase単体で他の文脈でも再利用できる訳」を「本文での用法に合わせた訳」へ変える**こと(**ユーザー承認事項**)。

## 1. 根本原因(`ROOT_CAUSE_04.md` 0-R)
- **主因**: 意味生成call(gloss)に「本文でその表現が実際に何を意味するかを確定する段」が無い。翻訳モードでglossを直接1本書く形になっており、Cp(自己監査欄)・G2/G3・Cなど「意味の計算を強いた」armは制約句の有無と無関係に効いた。
- **増悪因子(未検証→X1で差は有意でなかった)**: gloss Promptの文脈限定句(「key_phrase単体で他の文脈でも再利用できる自然な訳に」「source_sentenceは語義を選ぶためだけに」等)。H5(X1対M)はFAIL系 6→5で単独では有意差なし = 句の置換だけでは足りない。
- **型**: 具体名詞を含み、字義どおり読んでも文法が成立し、直訳した日本語では比喩の意味が運ばれない、新造または断片化した比喩(`an unseen clock`・`question shaped like a trophy`・`greener grass`・`draw a line`)。日本語でも通じる慣用(光を当てる、舞台裏等)は字義訳でも正解になり外れない。
- 上流の暴露原因(選定規則5が新造比喩を選びやすい、規則3が慣用を断片化)は今回の対象外(選定Prompt 2はユーザー逐語固定)。

## 2. 採用候補の仕組み(X2p。`TRIAL_DESIGN_06.md` §1・§9、`er112_kp_gm_trial_05.py` `X2P_MEANING`)
- 同一call内で、`japanese_gloss` を書く**前**に3欄を出力させる: `meaning_in_text_en`(本文でkey_phrase全体が表す意味を平易な英語1文。比喩は「その比喩が指す一般的意味」、一側面だけに絞らない)→ `naive_ja`(英単語を日本語対応語に置換しただけの訳)→ `naive_ja_conveys`(yes/partly/no: naive_jaだけで意味が伝わるか)。
- `japanese_gloss`: yesなら定訳・慣用を優先(naive_jaの写しにしない)、partly/noなら字義の像を使わず意味**全体**を慣用か短い言い換えで表す(一部だけを取り出さない。動作主・動詞の意味をずらさない)。同品詞・同程度の長さ、説明文・定義文にしない。
- 文脈限定句の置換: 「他の文脈でも再利用できる訳」→「このkey_phraseが本文のこの箇所で実際に表している意味を表す」(固有名詞・数値・この記事だけの出来事は入れない)。「source_sentenceは語義選択専用」→「語義と用法[字義か比喩か]を決めるために使う」。
- **追加call 0**。Production必須欄(`rank`/`current_gloss_consistent`/`japanese_gloss`/`qa_reflects_all_key_phrase_words`/`reasoning`/`added_word_mappings`)は維持(validate互換 85/85)。承認済みgloss規則(`b1_p2_keywords_l_prompt_template.txt`の抽出文)は不変。

## 3. Before/After(確定。詳細=`TRIAL_RESULT_05.md` §A〜§E)
| 段 | B0(現行) | X2p |
|---|---|---|
| R hard-core 12出力 | FAIL系 **10** / PASS 2(2rep以上失敗KP 3) | FAIL系 **0** / PASS 11 / THIN 1(2rep以上失敗KP 0) |
| R co-KP 9出力 | 9 PASS | 8 PASS / THIN 1(`sound no one asked for` rep1) |
| held-out 10KP | PASS 8 / THIN 2 | PASS 9 / THIN 1。B0=PASSからの悪化 **0** |
| Stage 2 通常54KP(strict: B0良い方rep基準) | - | PASS→FAIL **0** / PASS→THIN **2** / 変化なし 52 |
| Stage 2 lenient(B0悪い方rep基準) | - | PASS→FAIL 0 / PASS→THIN 2 / THIN→PASS 1 / FAIL→PASS 2 / 変化なし 49 |
- 事前宣言のStage 2基準(strict PASS→FAIL 0、PASS→THIN≦2)に**適合**(0 / 2、上限ちょうど)。gating基準(R FAIL系0・THIN≦2・held-out悪化0)も満たす(ただしこの基準はX2p確定値を見た後にFableが是正したもの[`TRIAL_DESIGN_06.md` 4-追記]である点を開示)。
- 比較arm: X2(THIN 4)・Cp(R 9/1/2、FAIL系2)に対し、X2pはR hard-coreで最良。Stage 2でCp_t4(PASS 53/THIN 1)よりX2pが劣るKP 1・優るKP 0。
- 代表例(B0 → X2p): `an unseen clock` 目に見えない時計 → 値札に隠れた独自のタイミング / `question shaped like a trophy` トロフィーの形をした質問 → 賞という形で投げかける問い / `greener grass` より青々とした芝生 → 自分より恵まれて見える他人の暮らし / `reach for someone's wallet` 人の財布に手を伸ばす(FAIL) → 財布を出してお金を払おうとする / `settle at` ～で落ち着く(FAIL) → ～で取引を終える。
- 通常54KPの文字列は **35/54が変化**(19/54はB0のいずれかのrepと同一)。変化後もstrict基準で52/54がPASS以上。「通常表現が変わる」こと自体は確認済み(実質的な悪化はTHIN 2件)。

## 4. 残存NG・新規悪化(性質)
| KP | 区分 | X2p文字列 | 性質 |
|---|---|---|---|
| an unseen clock rep2 | R | 値札に隠れた時間のずれ | 「独自のタイミング」より狭い(THIN。FAIL_LITではない) |
| sound no one asked for rep1 | R co-KP悪化 | 誰も聞きたくない音 | asked for の意味が移動(頼む→聞きたくない)。同一文字列はX2でも出た |
| move in the other direction | Stage 2悪化 | 売れ行きは逆に下がった | 文脈の補足で意味が狭い・方向を断定 = **説明文化/文脈の取り込み過ぎ型** |
| supply chain | Stage 2悪化 | 商品が作られて店に届くまでの流れ | 「店」に限定(Cp_t4でも同文字列でTHIN)= 文脈の取り込み過ぎ型 |
| a door inside the pain | held-out(悪化ではない) | 悲しみの中に見つけた、思い出と向き合い直す道 | 物語解釈を含み説明的。B0もTHIN |
- FAIL系(字義訳・意味不一致)の残存は **0**。残るのは「文脈を取り込み過ぎて意味が狭くなる」型のTHIN(新規悪化3件はすべてこの型または意味移動)。これは**設計トレードオフの徴候**(下記5)。
- 観察: 否定・対象・場面が見出し語より具体化したPASS文字列がある(`add up`→「つじつまが合わない」[本文は doesn't add up]、`step out`→「人が姿を現す」、`carry the load`→「必要な荷物を運ぶ役目を担う」、`run on`→「別々の時間軸で動いている」)。現行Fable水準ではPASSだが、**key_phrase単体で他の文脈でも使える訳ではない**(再利用性は下がる)。

## 5. X/Y/Z共通仕様への影響
- **gloss生成は共通module**: `er003_key_words_gloss_alignment.py`(`align_glosses`)を X(`er003_v1_n3_01_scaffold_generate.py:539`)・Z・Y が共有。
- **新規生成経路のみが対象**: `is_fulltext_gloss_missing`(`er003_key_words_gloss_alignment.py:270-273`)が真のitem(`fulltext_source_ref`付き=全文選定由来、current gloss=null)。
- **Zのrepair/再整合経路**(`er026_family_z_fiction_production_runner_01.py:1552` `align_glosses(... only_ranks=ranks)`)はcurrent glossありの人称修復で、**現状は未適用**(X2pは新規生成専用)。採用時の扱いは `WIRING_DESIGN_06.md` §3で選択(推奨=非適用 = 現行Promptのまま)。
- **A/B/C旧ライン**は新規生成経路を通らない(`fulltext_source_ref`の設定側は `er105_kp_fulltext_selector_01.py`・`er003_key_words_canonicalization.py` のみ。Grep済、`TRIAL_RESULT_05.md` 旧§4)。A/B/C itemは `is_fulltext_gloss_missing` が偽 → 現行Promptのまま変更なし。
- **Y**: 共通module経由で自動適用されるが、Yの量産Production経路は未存在(DEV/Trial)。Yへの別途配線は不要。
- **後続工程**: Adv説明(b1b)・TTS・assembleはgloss文字列を受け取るのみ。gloss変化は既存のsignature機構で吸収(追加call 0)。既存記事は自動再生成しない。

## 6. 量産単価・速度への影響
- 1callあたり実測: X2p **0.1593円**(範囲0.09〜0.23円、reasoning_tokens平均1,343)対 B0 **0.0585円**(304)。差 +約0.10円/call(**約2.7倍**)。X2pの費用はCp(0.1566円)と同程度で、「Cpの約半額」という当初見込みは成立しなかった。
- 記事あたり: gloss callは1 call最大3KP、Stage 2実績は54KP/29 job(約1.9KP/call)。記事あたり1〜3 callの想定で **+約0.1〜0.3円/記事**(70円/記事セット目標に対し約+0.14〜0.43%)。**call数は不変**(1 call/グループ。retryの上限2は不変だが、retry発生時は単価分だけ増える)。
- 速度: 出力tokenは約3.5倍(447→1,561/call)。wall-clockの精密実測は未実施(粗い見積: 約+8〜9秒/call、1,000出力token増あたり)。記事あたり数秒〜十数秒の増、gloss段は直列で記事生成全体の所要時間に対し小さい(runtime evidence計画で再測定)。
- 60円台後半の原価目標への影響: 増額は避けられない(増分の主因は推論token)。**「増加が本当に必要か」の代替**: (a)対象を字義訳リスクが高い型のKPに限る(判別器が必要で別設計・今回未検証)、(b)Cp最適化版(単価はX2pと同程度のため利得小)。現時点で品質を維持したままより安い代替は未確認。

## 7. ユーザーに判断を求める事項(判断候補)
1. **gloss設計原則の変更(承認事項)**: 「key_phrase単体で他の文脈でも再利用できる訳」→「本文での用法に合わせた意味を表す訳」。新造比喩に再利用できる訳は原理的に存在しないため両立せず、現行ゴールド(字義訳=FAIL)は後者を示す。採否はユーザー。
2. **X/Z(+共通module経由でY)の新規生成glossへのProduction配線**(Prompt変更を伴う。単価+約0.1〜0.3円/記事)。
3. Zのrepair経路への適用可否(推奨=非適用。`WIRING_DESIGN_06.md` §3)。
4. 評価の十分性の受容: 1 rep・Fable単独・揺れ7/10(緩い方向)・held-out10KP。追加rep/追加KP(約数円)で補強するか、現状で採否判断するか。
本書自体はVALIDATED判定・Production承認の根拠ではない。
