# OPUS_REVIEW_REQUEST_07: 課題① 字義訳の原因分析・根本対策案のOpus独立レビュー依頼(条件A: 新しい構造・処理フローの設計)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_21 / 2026-10-24 / 依頼元: Fable(本書は実行層Sonnetが作成した依頼文案。起動はFable)
レビュー対象: `ROOT_CAUSE_04.md`(原因)・`DESIGN_07.md`(対策案)・`TRIAL_DESIGN_05.md`(Trial設計)。Production変更0・API 0の設計段階。判断基準は`docs/pm/PM_GOVERNANCE.md` 11-3(条件A)。
前提資料(読む順): `ROOT_CAUSE_03.md` B節・`TRIAL_RESULT_04.md`(§8 Fable確定)・`TRIAL_04/REPORT_FABLE_04.md`・`TRIAL_03/FABLE_BLIND_RESULT_03.md`・`ROOT_CAUSE_02.md` §3・`DESIGN_06.md` §3-4。再現script=`er112_output/kp_gm_design_07/`(`hardcore_arm_table.py`・`cp_vs_b0.py`・`prompt_dump.py`・`canon_reasoning_census.py`)。実Prompt=`er112_output/kp_gm_design_07/prompt_dump_gloss_ngkp.txt`。
ユーザー要件(2026-10-24、課題①): 検査方式Cは現段階でProduction採用しない。原因究明のやり直し(『LLMが確率的に選ぶ』で終わらせない)/正しい意味を最初から生成する方法を優先/既存call内の改善を優先し追加LLM callを極力抑える/通常表現が悪化しないこと/採用はユーザー判断。

## 依頼する論点(それぞれ「妥当/要修正/不採用推奨」と理由を)

### 論点1: 原因分析の妥当性(ROOT_CAUSE_04)
1. **『確率的ではなく系統的』という再定義**: hard-core 4KPの字義訳がG0/B0で8/11(うち3KPは6/6、`draw a line`のみ2/5)で、他のF層KP37個は0。この集計は事後層別(字義訳が出たKPを選んでいる)で率が過大になる点を開示した。この再定義は妥当か。『KP-型に依存した系統的失敗』の根拠として十分か。他に説明できる要因(KP固有の出現頻度、sentence切れ、rep間のtemperature)の見落としは。
2. **最有力仮説H5(文脈限定句)**: 全armで不変の唯一の共通因子として、gloss messageの『key_phrase単体で他の文脈でも再利用できる自然な訳にし、本文固有の…文脈の追加はしない』(HEAD `er003_key_words_gloss_alignment.py:603`)と『source_sentenceは語義を選ぶためだけに使う』(`:320`、`:309`)を挙げた。この解釈は妥当か。『不変なのでこれが原因』は論理的に弱い(他にも不変因子がある)ため、見落としている不変因子はないか(例: schema順でjapanese_glossがreasoningより前、effort high、1call最大3KP、developer message、ほか)。
3. **Cpの再解釈**: Trial_04でCp(自己監査欄をjapanese_glossの後に足した生成)は検出器としてrecall 0で不採用だったが、**生成方式としてはF層FAIL 0/41(B0 7/82)・hard-core 0/4**だった。『欄がpromptにあることが意味同定を促した』という解釈は妥当か。単なる1 repの揺れ・churnの可能性をどう評価するか(Fisher p≈0.012〜0.026、探索的)。Fableが過去に『Cp不採用』とした根拠(自己監査flag 0/61でrecall未達、DESIGN_06 §3-4)は、生成方式として評価し直す際に再検討が必要か。
4. **『解釈が正しくても日本語化で字義に戻る』**: G2 rep2 `draw a line`(core_sense正解・gloss『はっきりと線を引く』)1例のみで、日本語化段にも判定が要る(H10)とした。1例の一般化は強すぎないか。反証・追加確認の方法は。
5. 『選定時点の意味喪失』(H1)の整理: 選定出力が意味を持たない・規則3の最小化が慣用手がかりを削る(`greener`1語)・canonicalization `reasoning`が比喩/『負担を担う』を認識するがgloss段に渡らない、を『必要条件であって十分原因ではない(記事全文はgloss段にある)』とした。この整理は妥当か。

### 論点2: 対策案の比較(DESIGN_07)
1. **案A(推奨: gloss call内で`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`→gloss、文脈限定句を『本文での用法に合わせる』へ置換)**: 追加call 0。(a)条件付き(yes/partly/no)の構造で、G2/G3の説明文化△を避けられるか。(b)`naive_ja_conveys`が確証バイアスで常にyesになるリスク(Cp audit flag 0/61の前例)に対し、`naive_ja`(英単語の機械的置換を先に書かせる)で対処できるか、それとも物理的分離(別欄を先に出力して次で判定)が必要か。(c)文脈限定句を置換すると、記事固有の固有名詞・出来事がglossに混入しないか(Std glossは再利用性が目的)。
2. **案B(制約句の置換のみ、欄追加なし、原価は現行より低下)**: 因果対照かつ最安の採用候補として並べた。案Bが効いた場合に案Aは不要と判断してよいか。案Bの『解釈が出力に出ない』弱点をどう見るか。
3. **案C(Cpを生成方式として採る)**: 既に近い効果が出ているなら、新規欄を設計する(案A)より、Cpを最適化(英語文2文→1文、使わない`gloss_conveys`欄の削除)する方が確実か。Cpの欄がgloss後で出力に影響しない構造のはずなのに効いた機序の仮説(promptに欄の指示があるだけで推論が変わる)は妥当か。
4. **案D/E(上流の意味引継ぎ)**: E3(中心義を共有して悪化、`ROOT_CAUSE_02.md` §3-2)の前例から次手に回した。ユーザー例示『選定時に把握した意味・用法を引き継ぐ』を重視するなら、hint渡し(誤りの可能性を明示)にはE3と異なる利点があるか。canonicalizationの責務(形の正規化)を増やす副作用の評価は。
5. **見落としている代替案**: 例えば(i)effort/モデル混在(解釈だけ別設定)、(ii)gloss後に『確定glossの逆翻訳(英語)』を同一callで行わせて自己修正する2段出力、(iii)隣接文window(前後各1文)を入力に追加、(iv)few-shot例の追加(例の偏りリスク)、(v)Adv英語説明の流用など、挙げた案に含まれない有効な手段はないか。

### 論点3: 通常表現の非劣化の担保
1. 案Aのyes経路は『現行と同じ目標』だが、promptが変わるため文字列は変わりうる(Cpで14/25KPの文字列が変化)。構造保証でなく実測(Fable盲検・非対象57KP)で担保する設計は十分か。許容基準(PASS→THIN/FAILが≤2/57、PASS→FAIL=0)の妥当性(ユーザー定義水準ではなく案)。
2. G2/G3の説明文化△(標準偏差→説明文など)の原因として『一律の言い換え強制・一般化した中心義・「聞いてすぐ分かる」基準』を挙げた。この診断は妥当か。案Aの『同じ品詞・同程度の長さ、説明文・定義文にしない』という規則は、この問題を防ぐのに十分か。

### 論点4: Trial設計の妥当性(TRIAL_DESIGN_05)
1. arm構成(B0新規/X1/X2、Cpは既存参照)・Stage分け(Stage 1: hard-core 3rep、Stage 2: 非対象57KP 1rep)は、検出力と費用(Trial_04枠残3.43円+rep2枠残4.90円)の制約下で適切か。R 12出力/armで、B0期待≥4/12・X2≤1/12(Fisher p<0.01)という判定は妥当か。regression to the mean(選択バイアス)への対処は。
2. 事前宣言基準(M1〜M6)の過不足。Fable盲検のみ(Sonnet Judgeなし)でよいか。
3. 『Stage 1で有効でなければStage 2を実施しない』停止規則、費用pilot(1記事分で単価確定、上限0.20円/call)、cap検査(発行前累計+見込み)は、Trial_04の見積り超過(計画3円→7円、Judge 1.6→10円)の再発防止として十分か。

### 論点5: 呼出数・既存仕様との整合
1. 追加LLM call 0を維持しているか(案A/B/C)。出力token増に伴う原価(+0.1〜0.24円/記事)と速度(数秒〜十数秒/call)の見積りは妥当か。
2. 承認済みgloss規則(`b1_p2_keywords_l_prompt_template.txt`の日本語グロス段落)は一字も変えず、gloss messageの見出し文・新規生成規則・schemaのみ変更する整理は正しいか。Adv説明(B仕様、PROMPT_SHA256 `c3d3734b…`)・canonicalization・選定は不変で、gloss変化→Adv再生成は既存signature機構で吸収される(追加call 0)という整理は正しいか。
3. 並行の課題②(possessor_roles、canonicalization段)との責務分離と、同一ファイル`er003_key_words_gloss_alignment.py`の併存配線(別flag・別test)の方針は適切か。

## 期待する出力
各論点について「妥当/要修正/不採用推奨」と理由、**見落とし**、**既存Trialとの重複の指摘**(同じ方向の提案を繰り返していないか)、推奨するArm構成の変更(あれば)。Opusレビュー後はFableが11-3に従い照合し、STOP条件に該当しなければ次工程へ進む(ユーザー承認Gateではない)。
