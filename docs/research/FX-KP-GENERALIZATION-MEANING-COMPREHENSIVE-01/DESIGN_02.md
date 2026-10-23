# DESIGN_02: Key Phrase 一般化・文脈意味・意味説明 — Opus条件Aレビュー反映後の設計(DEV/Trial実装の仕様)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 委任_02(2026-10-23) / 前版=`DESIGN_01.md` / レビュー=`OPUS_REVIEW_01.md`(Fable転記)
状態: Trial実装用の確定版。実装=`er112_kp_gm_trial_01.py`(DEV専用・既定OFF・Production非到達)。正式配線は未承認(Trial成功=`VALIDATED`止まり、採用はユーザー判断)。

## 0. 骨格(変更なし)
新規LLM callを追加せず、既存3段(canonicalization / gloss / Adv英語説明)の規則を精密化し、決定論validatorの許可を拡張する案A。Prompt 2(選定)は逐語固定のまま不変。source gateは`source_span`照合のため無影響。

## 1. Opus所見の反映表

| ID | 区分 | 反映(DESIGN_02での扱い) | 実装箇所 |
|---|---|---|---|
| OF-01 | 必須 | validator表・判定関数をProduction moduleに触れず`er112`内でDEV注入。`install_dev_patches()`を明示呼出するまで何も差し替えない。arm設定はスレッドローカルで、baseline/設定なしでは元の関数へ素通し。Production module・template・gloss規則templateのsha256をTrial開始時・終了時に記録し不一致なら失敗終了(`production_hash_start/end.json`) | `er112_kp_gm_trial_01.py: prod_hashes / install_dev_patches` |
| OF-02 | 必須 | him/her/me/us→someone は**既存reason `generalize_person_dependent_reference`を流用**(schema変更不要、gloss側`PERSON_NORMALIZATION_REASON`も通る)。新reason `generalize_reference_word`はthis/that置換のみ。DEV側でschema enum(`NORMALIZATION_REASONS_FULLTEXT`)・reason gate(`_is_valid_fulltext_normalization`。`_qa_field_effective_verdict`と`validate_canonicalization_item`はこれを呼ぶだけなので自動的に新reasonを通る)・templateのreason列挙を同時更新。Production関数の複製は`_is_valid_fulltext_normalization`と`er105.is_valid_inflection_normalization`の2つだけで、元関数のsource hashを固定するdrift guard testを置く | 同上 + test |
| OF-03 | 必須 | 規則5本文(下記§2)。表は`{a, an, the}`許容。置換条件=this/thatが単数可算名詞前の限定詞のときのみ。validatorの機械条件: 句末不可、直後がmuch/many/is/was/said…・time/point/case等の談話名詞・前置詞/不変化詞・不可算名詞(advice等)・複数形なら不可。a/anはCMU辞書で直後語の語頭音素が母音かを決定論判定(API 0)。Prompt側は「既定a/an、標準見出し形がtheの慣用句のみthe」 | `_ref_pair_ok / starts_with_vowel_sound` |
| OF-04 | 推奨 | OPEN-357(`close around me`のme残り)を本件に関連付け、`me`・`us`→someoneを対象に含める(DEV validatorとtemplate規則5(b))。`them/it`は対象外(複数・曖昧、Opus同意)。`her`は所有格/目的格の両義: validatorは直後が限定詞/前置詞/不変化詞/句末のときだけ目的格とみなし`someone`を許可(`lose her job→lose someone job`を機械で防ぐ)。残るリスクは合成test(下記)で測る | `_ref_pair_ok`、合成negative |
| OF-05 | 必須 | A-3の「日本語参考と同じ中心義」を差替え: "Use the sense the phrase has in the source sentence; the Japanese reference is only a hint for which sense." + 「ONE meaning, no story-specific conditions」維持(§3) | `A3_EXTRA` |
| OF-06 | 推奨 | Std/Adv整合は決定論共有armを最初から入れる: 同一run内でa2とb1bに同じused_formが出たとき、b1bのgloss(=説明call入力のJapanese reference)をa2のglossで置換(新call 0)。成功基準=語義の不一致0。a2→b1bの順に逐次処理する(runner確認: 本番はa2/b1bが別runであり、共有を採用する場合は実行順序の変更が必要=配線前確認事項) | `_apply_share`(arm `a123s`) |
| OF-07 | 必須(評価) | 「逐語gloss」の定義を更新: 日本語でも同じ比喩が同じ意味で自然に通じる表現(例: 光を当てる、一線を引く)は逐語に数えない。Judge基準=「本文での語義が日本語学習者に正しく伝わるか」。A-2にも同旨を追加。baseline逐語率を新定義で数え直す(Judgeで測定) | `A2_EXTRA`、Judge prompt |
| OF-08 | 推奨 | gloss gate/HR副作用: `_person_mismatch_reason`がhim→someone itemに効く。retry回数・HR件数・canonicalization INVALID件数を全armで記録しbaseline(記録済みprod+再生成)と比較 | result.jsonのcanon_attempts/gloss_alignment_status |
| OF-09 | 推奨 | 1回のTrialで多arm: base / A-1 / A-1+A-2 / A-1+A-2+A-3+共有。A0(validatorのみ)は無効(template:11がhim/her置換を禁止)のため最小単位=A-1。前後1文armは難例のみ・条件付き(`a123c`) | `ARMS` |
| OF-10 | 推奨 | 合成肯定7(take that step / cross that line[the確認] / float that idea[an] / told her the truth / gave him a hand / close around me[OF-04] / make that call)・合成否定10(take that advice / cost that much / so that everyone could hear / lose her job / that said / at that point / in that case / this time / between you and me / not that bad)。`turn on its head`は実データ(its→one's禁止の確認)。98%/90%は方向判断(最終は実測の信頼区間つきで報告) | `SYN_UNITS` |
| OF-11 | 情報 | 正常セットは文字列一致で機械判定しbaseline(記録済みprod)から変わったitemだけJudge | eval |
| OF-12 | 情報 | 大文字残り(`Carry the Load`等6/78)は範囲外。別OPEN起票(逐語glossを含む) | OPEN_ITEMS |
| OF-13 | 情報 | Trial-02整合/Prompt 2不変/source gate無影響/変更はすべてTrial→VALIDATED→ユーザー採用。Store reuse_key・説明signature(`er019_family_x_audio_production_runner_01.py:1077-1081`はused_form基準で再生成)・OPEN-471/472統合は配線前確認事項 | RESULT_PACKET |

## 2. 規則5(canonicalization template追加。`build_a1_template`が元templateへ6箇所のanchor置換、各anchorは元template内にちょうど1回であることをdrift guardで検査)

- 自問文(template:7)へ「ただし規則5に該当する参照語を含む場合は『そのまま』とみなさず規則5を先に検討」を追記。
- 規則3末尾の「him/her(目的格)…はそのまま残してください」を「目的格のhim/her/me/usは規則5(b)で扱う。them/it等は残す」へ置換(旧ルール撤去。them/it/these/thoseの禁止は維持)。
- 規則5(a): this/that→a/an(慣用句の標準見出し形が定冠詞のときのみthe)。単数可算名詞の限定詞のときのみ。例 draw that line→draw a line / float that idea→float an idea。reason=`generalize_reference_word`。
- 規則5(b): him/her(目的格)/me/us→someone。例 pulled him under→pull someone under / told her the truth→tell someone the truth。reason=`generalize_person_dependent_reference`(OF-02)。
- 例外(置換しない): 代名詞/副詞/接続詞のthat(句末that, that much, not that bad, so that)、不可算名詞前(that advice)、固定表現(that said, at that point, in that case, this time, like that, between you and me, all that)、it/them/these/those。迷えば置換しない。
- QA定義(qa_traceable_contiguous_span / qa_person_reference_generalized)とreason一覧も規則5に合わせて更新(「新規QA項目・検査は増やさない」)。

## 3. A-2(gloss語義方針)・A-3(説明追加規則)最終文言

A-2(gloss `NEW_GENERATION_TEXT`の直後へ追記、既存文は不変。例は検証セットに含まない語を使用): 慣用句・比喩・定型表現はフレーズ全体の意味(cut corners→手を抜く)。日本語でも同じ比喩が同じ意味で自然に通じる場合はその表現でよい(bridge the gap→溝を埋める)、通じない場合はフレーズ全体の意味、本文で字義どおりなら字義どおり。どの語義かは本文で判断し、記事固有の状況・固有名詞を入れず別場面でも通用する簡潔な言い方、意味は原則1つ、訳語を並べない。冠詞・指示語を「その」「ある」と逐語訳しない。「すべての語を反映」は慣用句ではフレーズ全体の意味が表れていれば満たす。

A-3(説明Promptの"Additional rules"末尾へ2行追加、既存文は不変): (1) "Use the sense the phrase has in the source sentence; the Japanese reference is only a hint for which sense." (2) "Explain the core meaning of the phrase in its most general use that fits the source sentence. Give ONE meaning; do not add conditions or details that belong only to this text."
→ PROMPT_SHA256はTrial-02逐語性の機械証拠のため、採用時はB仕様変更(ユーザー判断)。Trial中は本番定数を変えずDEV dispatcherでのみ付加。

## 4. 検証設計の更新(DESIGN_01 §5 からの差分)

- **replayの再利用構造(費用最適化)**: canonicalization結果を`a1`で1回生成し、`a12`は同じunit・同じrepのcanonicalization結果を再利用してgloss(A-2)のみ再実行、`a123s`は`a12`のitemsを再利用して説明(A-3)+共有のみ再実行。これにより『A-2/A-3の効果は同一KP入力下の比較』になる(KP揺れ起因の差を排除)。baselineは(1)記録済みProduction出力(2026-10-22/23の正式run、API 0)を1標本、(2)再生成(`base`/`base_c`)で揺れ幅を測る。
- **成功基準(DESIGN_01 §5-3をOF-07の逐語定義で更新、数値は方向判断)**: 本文由来100%・5語以下100%・難例の指示語/目的格残り0・正常KP+固定表現の不要変更0(合成negative全件保持)・難例gloss/説明の語義適合 ≥90%(2者PASS)・`draw a line`は文字列一致3/3+gloss/説明を語義判定・記事固有混入 ≤5%・逐語gloss(新定義) ≤10%・共有KPでStd/Adv語義不一致0・正常KP key_phrase一致 ≥98%/意味同値 ≥95%(baseline再生成揺れを差し引く)・retry/HR/INVALIDがbaselineを超えない。
- **Judge**: 2系統(`claude-sonnet-5-5`と`gpt-6.1-sol`、いずれも2026-10-22時点の各社最新世代の評価系、前回Trial-02と同系統)。生成は本番と同じ`gpt-6-luna`(本番ライン同一modelでの検証が目的。最新性は『本番ライン固定のため評価対象』)。評価対象行は重複排除し、正常itemは文字列一致/glossペア比較で機械絞り込み後にJudge。Fable抜取り用に全判定一覧を保存。
- **費用**: 上限80円(Trial全体)。超過見込みなら開始前停止。

## 5. 旧ルール撤去・残置(Trial採用時の変更案。本委任ではProductionを変更しない)
- 撤去候補: template規則3末尾の「him/her(目的格)…そのまま残す」(JRE委任_02追記分、規則5(b)へ置換)。残置: them/me以外のit/them/these/those不変、規則1(限定語の先頭・末尾除去)、Meaning Preservation Rule、source_span制約。
- 新reason `generalize_reference_word`は採用時にProductionの`NORMALIZATION_REASONS_FULLTEXT`・fulltext schema enum・template reason列挙・validatorへ同時追加が必要(Trialは同等をDEV注入)。

## 6. Trial中の設計変更(ITERATION_LOG_01参照、Opus所見からの差分と理由)
- OF-03(1)『the許容』を**a/anのみ**へ変更: v1で`draw that line`→`draw the line`となりユーザー明示例(`draw a line`)と不一致。標準見出し形がtheの慣用句は本文でも通常`the`で書かれ置換対象にならないため、a/an限定の実害は小さい(validator表も`{a, an}`)。
- 規則5に『置換しない判断は規則5の対象語だけに適用。規則3は従来基準』を追加(規則3の控えめ化を防ぐ)。validatorに接続詞のthat(直後が主語代名詞・限定詞)を追加。
- A-2(gloss語義方針)とStd/Adv決定論共有: Trialで利得が実証できず撤去推奨(A-1で『その』混入は消え、P判定は共有なしで100%)。
- A-3: v1(OF-05)→v2→v3と具体化。ユーザー例は直るが汎用効果は未実証=採用はユーザー判断。
- 費用最適化のためreplayの再利用構造(canon→gloss→説明の段別再利用)と、baselineを記録済みProduction+`base_c`(canonicalizationのみ)に変更。各3回はcore 8 unitのみ(他は1回)、予算上限80円による。
