# DESIGN_01: Key Phrase 一般化・文脈意味・意味説明の包括対策 — 設計(Opusレビュー前)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 委任_01(2026-10-23) / 根拠=`ROOT_CAUSE_01.md`
状態: 設計案(未実装)。Production/Prompt/flag/閾値は無変更。実装はOpusレビュー反映後、DEV/Trial経路(`er112_*`、既定OFF、Production非到達)のみ。正式配線は未承認(Trial成功=`VALIDATED`止まり、採用はユーザー判断)。

## 0. 推奨案(1行)
**新規LLM callを追加せず、既存3段(canonicalization / gloss / Adv英語説明)の規則を精密化し、決定論validatorの許可表を1つだけ拡張する(案A)。** 共通の『語義方針』を2つのPromptに同文で入れ、Std/Advの解釈を揃える。推定費用 +0.01〜0.05円/記事セット(Trialで実測)。

## 1. ユーザー要求①〜⑥の充足方式

| 要求 | 方式(既存の何を、どう変えるか) | 根拠 |
|---|---|---|
| ① 一般化(冠詞・代名詞・時制・指示語) | canonicalizationに**規則5『参照語の不定化』**を追加。this/that→a/an、目的格 him/her→someone。決定論validatorの許可表(1対1トークン置換、既存の人称表と同型)を拡張。語数は不変(置換のみ)なので5語上限は自動で保たれる | ROOT_CAUSE (a): 許可変換が閉集合 |
| ① 続き:本文存在ルールとの両立 | 選定はPrompt 2逐語のまま(本文surface)。`source_span`は不変で、source gate(`er003_key_phrase_source_gate_01.py:85-109`)はsource_spanで照合するため無影響。表示・音声は `used_form`(一般化形)。既存の `reach for one's wallet` と同じ扱い | ROOT_CAUSE §1 |
| ② 本文の意味を捉える | gloss Promptの新規生成ブロック(`er003_key_words_gloss_alignment.py:315-321`)に『語義方針』を追記:本文(記事本文は既に入力済み)に即した語義を選ぶ | gloss callは記事全文を既に受け取る |
| ③ 汎用性・⑥ 簡潔(中心義1つ) | 同『語義方針』:記事固有の状況・固有名詞を含めず、中心的な意味を1つだけ書く。Adv説明Promptにも同趣旨(条件を足さない・中心義1つ)を追記 | ROOT_CAUSE (b): 狭い下位語義を既定に選ぶ |
| ④ 慣用表現 | 同『語義方針』:慣用句・比喩は語ごとの直訳でなくフレーズ全体の意味。既存の『key_phrase全体のすべての語を反映』との衝突を、慣用句のときは語対応を要求しない旨で解消 | ROOT_CAUSE (c) probe-02: 逐語gloss 3/3 |
| ⑤ Std/Adv整合 | **データ共有の新設はしない。** (i)両Promptに**同一の語義方針文**を入れる (ii)Advは既存どおりAdv glossを参照して説明を書く(『同じ中心義で書く』を明記) (iii)両レベルが同じ一般化形を受け取る(要求①の効果) | ROOT_CAUSE (d)。共有KPは21%と少なく、機構新設の費用対効果が低い |
| 既存仕様維持 | Std=日本語意味、Adv=英語説明、5語、本文由来、CMU、ASRは変更しない | — |

## 2. 変更点の具体(案A)

### A-1 canonicalization(`b1_p2_keywords_canonicalization_fulltext_prompt_template.txt` + `er003_key_words_canonicalization.py`)
- 追加規則(案文):
  『5. 参照語の不定化: display_phraseに含まれる指示語(this/that)や目的格の人称代名詞(him/her)が、この記事の特定の対象を指しているだけの場合、学習用の一般形へ**置換**してください(this/that→a/an、him/her→someone。削除はしない)。例: "draw that line"→"draw a line"、"pulled him under"→"pull someone under"。固定表現として指示語が意味の一部であるもの(that said, at that point, in that case, this time, like that 等)は変更しない。置換するときは normalization_reason="generalize_reference_word" を使い、置換する語以外は(規則4の語形以外)変更しない。』
  対象外(明示): them/it/me/us/these/those(複数・曖昧な指示)は従来どおり不変。
- 自問文(template:7)に『ただし規則5に該当する語を含む場合は"そのまま"とみなさない』を追記(自問がYESに倒れる主因の除去)。
- validator: `_PERSON_DEPENDENT_TO_GENERIC`(:431-449)と同型の閉じた表 `_REFERENCE_TO_GENERIC = {that:{a,an}, this:{a,an}, him:{someone,somebody}, her:{someone,somebody}}` を追加し、`_is_valid_person_generalization`(:452)と `er105._token_pair_ok`(:670)の**両方が同じ表を参照**(再実装しない)。語数不変・1対1置換の制約は既存のまま。a/anは直後の語頭音との一致をvalidatorでは見ない(LLM+test、Opusレビュー論点)。
- 撤去(不要になる旧規則): JRE委任_02(commit 1d501f74d)でtemplate:11へ追記した『him/her(目的格)/them/me/us/it等は一般形へ置換せず、そのまま残してください』のうち**him/herの部分**。them/me/us/itは残す。`qa_person_reference_generalized`の文言を人称・参照語に拡張。
- 大文字残り(`Carry the Load`等 6/78)は対象外。templateが大小文字の変更を禁止しており(template:14)、音声・TTSには無影響、表示のみの軽微事項。**設計判断:本件に含めない**(含めると仕様変更の範囲が広がるため。Opusに是非を確認、含めるなら決定論の先頭小文字化のみで固有名詞判定が必要=リスク)。

### A-2 gloss(`er003_key_words_gloss_alignment.py` の `NEW_GENERATION_TEXT`:315-321)
追記案(『語義方針』、gloss/説明で共通の中核文を同一にする):
- 『慣用句・比喩・定型表現は、語ごとの直訳ではなく、フレーズ全体の中心的な意味を書く(例: break the ice→「場の緊張をほぐす」であり「氷を割る」ではない)。』
- 『どの語義かは本文(source_sentenceと記事本文)で判断するが、記事固有の状況・固有名詞は入れず、別の場面でも通用する簡潔な言い方にする。意味は原則1つで、訳語を並べない。』
- 『key_phraseに含まれる冠詞・指示語を「その」「ある」などと逐語的に訳出しない。』
- 『上の「すべての語の意味を反映する」は、慣用句ではフレーズ全体の意味が表れていれば満たす。』
例示語はtest集合に含めない語(break the ice等)を使い、過適合を避ける。

### A-3 Adv英語説明(`er019_family_x_kp_explanation_01.py` の `USER_TEMPLATE_HEADER`:69-82)
追記案(Trial-02 B候補の逐語に**追加**する形で、既存の文は不変):
- 『Explain the core meaning of the phrase in its most general use that fits the source sentence. Give ONE meaning; do not add conditions or details that belong only to this news story.』
- 『It must express the same central sense as the Japanese reference meaning.』
注意:この変更でPROMPT_SHA256(Trial-02逐語性の機械証拠)が変わる。これはユーザー承認済みB候補仕様への**変更**に当たるため、Trial→VALIDATED→ユーザー採用のルートで扱う(Trial中はDEV用overrideで、本番定数は無変更)。
任意armとして、説明callの入力に**前後1文**を追加する案(現在は1文のみ)をTrialで比較(probe-01では文脈不足が主因ではなかったため、既定は追加しない)。

### A-4 検査(新規検査は増やさない)
- 決定論の『逐語訳警告』は作らない(辞書が無く偽陽性が多い)。Trialの**評価側**(Production外)で2系統Judgeにより測る。
- 既存検査(source gate, validator, 5語, CMU, redundancy QA, KP3V)はそのまま。validator表の拡張のみ。

## 3. 代替案との比較

| 案 | 内容 | 要求①〜⑥ | 新規LLM call | 費用Δ/セット | 既存仕様・承認 | 実装規模 | リスク/結論 |
|---|---|---|---|---|---|---|---|
| **A(推奨)** 既存3段の規則精密化+validator表1つ拡張 | 上記 | ①②③④⑥充足見込み、⑤はPrompt原則共有 | なし | +0.01〜0.05円(推定) | Prompt2不変。canon規則・gloss・説明Promptの内容変更=Trial→採用判断 | 小(Prompt3箇所、表1、test) | 過剰一般化(固定表現のthat等)・retry増。Trialで検出 |
| B canon+gloss統合(1callでkey_phrase・日本語意味・中心義を出力、gloss段廃止) | 構造化出力化 | 整合は最良 | -1 call/level | -0.1〜-0.2円 | gloss alignmentの検査・HR経路・person constraintの再設計が必要。新構造=Opus条件A | 大 | 既存gate破壊の回帰リスク大。Aが不達なら再検討 |
| C 決定論の逐語訳検出+慣用句辞書 | 辞書照合で警告/再生成 | ④のみ部分 | なし | 辞書整備コスト | 新検査の追加(ユーザー方針に反する) | 中 | 辞書の網羅性が低く偽陽性・偽陰性。却下 |
| D 一般化・意味の専用LLM工程を新設 | 選定後に別call | ①②③④ | +1 call/level | +0.2〜0.4円 | Trial-02で一般化専用工程はREJECTED(Haiku、適用漏れ22/70)。ユーザー方針に反する | 中 | 却下(上位modelで再試するとしても費用方針に反する) |
| E 選定Promptに一般化を戻す | Prompt 2変更 | ① | なし | 0 | Prompt 2は逐語固定、『本文一致は絶対条件』と矛盾。要ユーザー承認 | 小 | 却下(承認済み仕様と矛盾) |

## 4. 音声・ASR側への影響(X/Z共通)
- 一般化形 `draw a line` が `used_form` として **TTS入力・ASR期待文・試聴ページ表示**になる(`er019_family_x_audio_production_runner_01.py:1159-1170,1491-1502,2175-2180`)。`reach for one's wallet` と同じ経路で、`a`/`someone` はいずれも一般語。
- KP3V / kp_vote_check: 期待文=used_formでありsource_spanではない→整合。数値・否定保護は解除済み(OPEN-458①)で影響なし。
- CMU gate: 選定surface(`that`/`him`を含む)で判定済み。置換後の語(a, someone, line)はCMU登録語。置換が増やす未登録語リスクは無い(Trialで機械確認)。
- 5語: 置換のみで語数不変。
- Store reuse_key: **未確認(推定のみ)**。keyがテキスト由来(`er063_family_z_audio_01.py:726 build_reuse_key`等)であれば `draw a line` は新規生成扱いとなり、記事Bの既存音声は保全され新仕様採用後にのみ再生成対象になる。実装前にX/Z各storeのkey構成を確認する(配線委任の確認項目)。HR: 変更なし。
- Source gate: source_spanは不変のためPASS(`present`判定が `draw a line` を見ない設計)。
- ASR-QUALITY並行Trial(OPEN-471英米綴り/OPEN-472固有名詞)とは別module。本件のused_form変更は両者の入力テキストを変えるが、ファイルは触らない(`er111_*`・`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/` は未編集)。**統合時の競合確認はFable/配線委任で行う**。
- X/Z共通部分=3段すべて(同module)。Family固有=本文種別による発生率差のみ(Zは目的格`him`が多い: 6/30)。Zの対話型では`he/she`が記事固有人物を指すため、表の拡張は`him/her`目的格のみ(主語代名詞は既存表)。

## 5. 検証計画(Trial、Opus反映後に実施)

### 5-1. 方式
Production経路は呼ばない。**記録済み入力の再生(replay)**:各記事の `selected items`(source_span・source_sentence)と記事本文を使い、(i)canonicalization (ii)決定論validator (iii)gloss (iv)Adv説明 の4段を、本番builderをimportしつつ**DEV用override Prompt**(案A)で再実行。比較: 現行baseline vs 案A(各3回で揺れを測る)。選定は再実行しない(Prompt 2不変、費用0)。スクリプト=`er112_kp_gm_trial_01.py`(新設、DEV専用、既定OFF)。

### 5-2. 検証セット
- **難例(≥15、実際は20件を予定)**: `draw that line`(記事B)、`reach for one's wallet`、`shine a light on`、`fire the starting gun`、`turn on its head`、`on the throne`、`Carry the Load`、`pulled him under`、`sentenced him to death`、`earn/win such trust`、`rise above the other voices`、`hold out`、`give way`、`kept you company`、`jump to that conclusion`(旧path)、`use its results`、`none other than`、`the grass is greener`系、`all the same`、`take the wheel`(X/Z計8記事超から)。
- **正常KP(≥30、副作用0確認)**: census内で一般化・意味に問題のないKP(`on a regular basis`、`in stock`、`push prices up`、`a sense of occasion`、`division of labor`、`articles of incorporation`、`letter of introduction`、`go out of one's way` 等)。
- **固定表現ネガティブコントロール(≥10、合成)**: `that said`、`at that point`、`in that case`、`this time`、`like that`、`all that`、`who is that`型など、指示語が意味の一部の表現を、実本文の1文に埋め込んだ合成itemで確認(過剰一般化の検出)。合成であることをレポートに明記。

### 5-3. 検証項目(ユーザー§5の1〜8)と成功基準(数値)
| # | 項目 | 測定 | 成功基準 |
|---|---|---|---|
| 1 | 本文由来 | validator(Rule7+新表)+source gate | 全件PASS(100%)。validator却下→外側retry増が baseline比で増えない |
| 2 | 5語以下 | 機械 | 100% |
| 3 | 一般化の過不足 | 難例の指示語/目的格残り=0。正常KPと固定表現でkey_phrase不変 | 難例の残り0/対象、正常+固定表現の不要変更 0 |
| 4 | 本文での意味 | 2系統Judge(独立モデル)+Opus抜取り | 難例のgloss/説明の語義適合 ≥90%(2者PASS)、`draw a line`は3/3回 |
| 5 | 記事固有に偏らない | Judge | 難例・正常合計で記事固有混入 ≤5% |
| 6 | 逐語訳回避 | Judge(慣用句の中心義に着地) | 慣用句難例の逐語gloss ≤10%(現行baseline: 確定4/78〜境界例込み10/78、慣用難例では高率) |
| 7 | Std/Adv整合 | 同一KPの Std gloss と Adv 説明の語義一致をJudge | 難例の共有KPで不整合0 |
| 8 | 正常KP副作用 | key_phrase完全一致率・gloss意味同値率 | key_phrase一致 ≥98%、意味同値 ≥95%(baseline再生成の揺れ幅を差し引いて評価) |
| 付 | 運用 | retry回数・API失敗・費用 | retry/失敗が baseline を超えない。費用Δ ≤ +0.1円/セット |
記事Bの例(`draw a line`/境界線を設ける系/`establish a clear boundary or limit`系)は**検証例の1つ**であり、文字列一致ではなく語義適合で判定(過適合を避ける)。

### 5-4. Judge・モデル(開発・評価の最新モデル原則、25節)
- 生成: `gpt-6-luna`(Productionと同一、`routing.SUPPORT_MODEL`。本番変更候補の検証なので本番ライン同一modelで測る。「最新か」: 本番ライン固定のため評価対象modelであり、最新系列の上位とは別)。
- Judge: 前回Trial-02と同系統の2系統(OpenAI上位=Sol系、Anthropic=Sonnet系最新)を予定。実際のmodel IDと最新性は実行時に確認して記録する(今回は未実行)。
- 反復: baseline・案A 各3回。結果が悪ければ失敗箇所別に再設計(同一方向の漫然反復はしない)。

### 5-5. 費用見込み(推定。実行前に再見積)
生成replay: 約8記事×2レベル×(canon+gloss)+説明、baseline+案A×3回で約 8〜15円。Judge: 難例20+正常30+対照10=60 item×2系統×2条件で約 40〜90円(前回Trial-02の評価費用143円/140 itemを参考に縮小)。**合計 50〜110円見込み、案件上限300円(7-7)内**。再設計1ループ追加でも上限内。日次1,000円の消化状況は着手時にFableが確認(同日他taskの費用が大きい)。

## 6. 70円目標への影響
KP関連の記事セット費用は現状約1.4円(scaffold実測1.195円+gloss 0.2円、uk_train run)。案Aの増分は入力Prompt数百token×4call分で**+0.01〜0.05円(0.07%以下)**。外側retryが増えた場合のみ増加(Trialで検出)。新LLM call 0、削減要素なし。Dは+0.2〜0.4円で却下、Bは-0.1〜-0.2円だが回帰リスクが大。

## 7. 撤去・整理の候補(旧ルールGrep結果は実装時に再確認)
- template:11の『him/her…そのまま残す』部分(置換)。`qa_person_reference_generalized` の定義文。validator関連コメントの『人称代名詞・所有格』限定表現。
- 残置:規則1(限定語の先頭・末尾除去)、Meaning Preservation Rule、source_span制約(`draw a line`は新表の1対1置換で許容、非連続の自由生成は引き続き禁止)。
- Grep済み:OPEN-458 ①②はASR/CMUであり本件の一般化規則を含まない(競合なし)。KPQ関連のtest(CMU/vote)は無関係。

## 8. リスクと未解決
1. **過剰一般化**: 固定表現のthat(that said等)を壊す。→ ネガティブコントロール10件とtemplateの例外記述で検出。
2. **a/an一致**: `that apple→an apple`をvalidatorは音声で判定しない。→ 表は{a,an}を許容、LLM+testで確認。
3. **Std/Adv整合はPrompt原則共有に依存**: 機構的保証ではない。→ Trial項目7で測り、不足なら『a2 glossをb1b currentとして渡す』既存機構の利用(新call不要)を再設計候補とする。
4. **Adv説明の変更はユーザー承認済みB仕様への変更**: 採用はユーザー判断。Trialでは本番定数を変えずDEV overrideで測る。
5. **大文字残り(6/78)・記事固有KP(11/78)**: 本件の範囲外(前者は仕様上禁止の維持、後者は選定の性質)。開示のみ。
6. probe-01/02は小標本(各3〜5回)。因果の方向(一般化でStd逐語化が解消)は5/5で明確だが、Adv説明の改善はPrompt追記なしでは確認できていない。

## 9. 実施順序(並列化)
Opusレビュー(並行して)→ [並列] ①validator表拡張+test(API 0) ②Trial replay harness+Judgeスクリプト(API 0で先行作成) ③検証セット確定(API 0) → baseline再生成(並列3回) → 案A再生成 → Judge(2系統を並列) → 集計→再設計判断。クリティカルパス=Judge待ち。
