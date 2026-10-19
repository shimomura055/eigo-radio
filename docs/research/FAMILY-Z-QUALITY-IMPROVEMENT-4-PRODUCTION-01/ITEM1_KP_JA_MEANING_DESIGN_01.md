# ITEM1 Key Phrase日本語意味の恒久改善: 経路マップ・根本原因・設計案(Phase 1、read-only、JPY0)

管理ID: FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_01 / 日付: 2026-10-19(JST) / Status: `ITEM1_ROOT_CAUSE_AND_DESIGN_READY_PENDING_OPUS_A`
ユーザー原文: `docs/pm/delegation_log/2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_USER.md`(4078文字、sha256 `add5c25c9170f2e2ef889cb819841f1dc9c6098cf4a22f290713e4681751970d`)
性質: コード変更0・有料API呼出0・Production/Prompt/Style変更0。以下の「実証」はartifact/コードを直接読んだ観測、「推測」は未実証の解釈。

## 結論(先出し)
- **「あなたの代わりに」は日本語訳そのものの誤りというより、「英語表現が後から変わったのに日本語意味が追従しなかった」構造欠陥(stale gloss)が原因**(実証)。日本語意味は選定段で表示候補`in your place`に対して1回だけ生成され(「あなたの代わりに」は`in your place`の訳としては正しい)、後段canonicalizationが`your`→`someone's`へ一般化した後、日本語意味は再生成されず、その整合を検査する仕組みも無かった。
- 既存の「gloss再整合」(KGCPW、`APPROVED_FOR_PRODUCTION`)は、この変化(人称の一般化)を**意図的に対象外**にしていた(`_GENERIC_TOKENS`を「語の追加」に数えない)。日本語意味に人称語が無いケースが大半のため問題化しなかったが、日本語意味側に人称語が含まれると素通りする。
- X/Zは日本語意味の生成・正規化・整合の全工程で**同一の共有module**を通る。修正を共有module内で行えばX/Z/将来Yに同時に効く(Z限定の外側retry層は日本語意味に関与しない)。
- 推奨=案III(LLM再整合の対象拡張+決定論的検証を既存のretry/HRに接続)。ユーザー原文§2①が「検査・retryの改善」を明示承認しているため承認済み範囲内と判断(最終判断はFable/Opus条件A)。確認論点は§6。

## §1 経路マップ(日本語意味を生成・変更・検査する箇所)

### 1-1 Family Z正式KP経路(a2=Standard、b1b=Advanced)
| 工程 | 関数:行 | 日本語意味との関係 |
|---|---|---|
| runner `stage_kp` | `er026_family_z_fiction_production_runner_01.py:1239` | 入口。`ga.preflight()`:1243 → `w62.run_kp_stage`:1259 → `_gloss_hr_gate`:1263 → `collect_unevaluated`:1275(STOP) → `_src_gate`:1278 → `install_kp_assets`:1279 |
| KP関数の解決 | `_kp_fn_for_ctx` :1161 → `er062_family_z_writer_01.run_kp_with_outer_retry` :971(Z限定・暫定、OPEN-310回避策)。`run_kp_stage` :931 | 日本語意味には関与しない(selection→canonicalization→redundancyの外側retryのみ) |
| (1) 選定(**日本語意味の唯一の生成点**) | `er003_v1_n3_01_scaffold_generate.run_key_phrase_selection` :294(Strategy L: `_run_key_phrase_selection_strategy_l` :351)。Prompt=`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt` :15-23(「短く自然な日本語グロス」「自然で平易な現代日本語」「括弧禁止」「『～』可」「漢数字」)。出力schemaの`ja_gloss` | LLM(gpt-6-luna、実Prompt=`key_phrases/a2/keywords_selector_prompt.txt`)。**人称・指示対象に関する規則は無い** |
| (2) canonicalization | `run_key_phrase_canonicalization` :683(shared)、Prompt=`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt`、`er003_key_words_canonicalization.py`(`PROMPT_TEMPLATE_PATH`:68) | **入力にja_glossを渡さない**(`canonicalization_view_items` :273。実Prompt `canonicalization_prompt.txt`のcandidate JSONはrank/display_phrase/source_span/source_sentenceのみ)。ルール3(人称一般化)で英語のみ変更。出力にglossなし |
| (3) merge | `merge_canonicalization_result` `er003_key_words_canonicalization.py:707`(gloss持越し :726 `original.get("ja_gloss")`、:742 `japanese_gloss`、:746 `japanese_gloss_tts=convert_display_gloss_to_tts_text`:187) | **選定時のglossを無改変で最終KPに付ける**(英語が変わっても追従しない) |
| (4) gloss再整合(KGCPW) | `scaffold.run_key_phrase_canonicalization`内 :724-732 → `er003_key_words_gloss_alignment.align_glosses` :580。対象=`select_alignment_targets` :147(`kp_extends_beyond_candidate`または`kp_adds_words_beyond_display` :141) | 対象外ならAPI呼出0・`NO_TARGETS`。再整合Prompt=`build_user_message_corrected` :364(+承認済みgloss規則`load_approved_gloss_rules` :160)、検証=`validate_item_corrected` :406、retry上限`MAX_GLOSS_ALIGNMENT_ATTEMPTS=2` :39、失敗→HR(`FAILED_HUMAN_REVIEW_REQUIRED`、`emit_human_review_notice` :748)、消費側関所`collect_unresolved` :619 / `collect_unevaluated` :629 |
| (5) Redundancy QA | `run_key_phrase_redundancy_qa` :748(`er011_key_phrase_set_redundancy_qa_01`) | 5件相互の意味重複のみ。gloss人称は見ない |
| (6) SRC D1 | runner `_src_gate` :1226(`z_sentence_id_posthoc_v1`) | source_sentence復元のみ。glossは見ない |
| (7) install / TTS | `install_kp_assets` :1150 → `load_level_inputs` :1330 → `stage_tts` :1383(P8-KP Style。`er063_family_z_audio_01.generate_or_reuse_z` :720の再利用キー=canonical_text等) | glossテキストをそのまま読み上げ。ASRは「読み上げ=テキスト」の一致検査 |
| (8) Adv KP英語解説 | runner :1303-1316(`er019_family_x_kp_explanation_01`、入力にjapanese_gloss) | b1bのみ。署名にgloss含む(:1295) |

### 1-2 Family X正式KP経路
- 入口`er003_v1_n3_01_scaffold_generate.run_key_phrases` :802 → `_run_key_phrases_impl` :835。選定は`kp_backend`(strategy_l / db_hybrid、:326-333)で、**db_hybridの選定も同じ承認済みPrompt template(gloss規則込み)を使う**(`er030_key_phrase_db_hybrid_selector_01.py:543` `bk.load_prompt_template()`)。選定以降は(2)〜(5)が**Zと同一関数**(`run_key_phrase_canonicalization` :683、`run_key_phrase_redundancy_qa` :748)。X runner(`er019_family_x_audio_production_runner_01.py:429-437,528-582`)も`gloss_alignment_status`/HR関所をZと同じ`er003_key_words_gloss_alignment`で扱う。
- Z固有は外側retry層(`er062:971`)とSRC D1(`_src_gate`)のみ。X固有はdb_hybrid選定とM2P0+A。**日本語意味の生成(1)・変更(3)・整合(4)は完全に共通module**。

### 1-3 共通/別実装の判定
日本語意味に関わる全工程((1)(2)(3)(4))はX/Z共通module(`er003_*`)。runner側(関所・resume・install)はX/Zで別実装だが、いずれも`er003_key_words_gloss_alignment`の同一関数(`collect_unresolved`/`collect_unevaluated`)を呼ぶ。→ 修正の主座=`er003_key_words_gloss_alignment.py`(必要なら`scaffold:724-732`)。将来Yも同module経由なら自動継承。

## §2 根本原因(run_e2e_03 a2 rank2)

### 2-1 実証した事実(artifact直接読み)
1. **選定時**(`key_phrases/a2/keywords_runtime_metadata.json` attempts_detail.parsed.items[1]): `display_phrase="in your place"`, `source_span="in your place"`, `normalization_type=none`, **`ja_gloss="あなたの代わりに"`**, `key_phrase_role=topic`。選定Promptは記事全文(Melos本文)を渡す(`keywords_selector_prompt.txt`)。→ 選定時点で「英語表現`in your place`の訳」としての「あなたの代わりに」は**正しい**(友人が"あなたの"=Melosの代わりに死ぬ)。人称・指示対象の規則が選定Promptに無い点は§3 #1。
2. **canonicalization時**(`canonicalization_prompt.txt`): candidate JSONは`rank/display_phrase/source_span/source_sentence`のみで**ja_glossを渡していない**。ルール3(人称一般化)に従い`in your place`→`in someone's place`(reason=`generalize_person_dependent_reference`)。出力schemaにglossは無い。
3. **merge時**(`er003_key_words_canonicalization.py:726,742`): 選定時の`ja_gloss`を`japanese_gloss`に無改変コピー。最終artifact(`a2/key_phrases/keywords_canonicalized.json`)= `key_phrase="in someone's place"`, `japanese_gloss="あなたの代わりに"`, `japanese_gloss_tts="あなたの代わりに"`, **`gloss_alignment_status`フィールド無し**(=gloss再整合に1度も入っていない)。
4. **gloss再整合が働かなかった理由**: `select_alignment_targets`(`er003_key_words_gloss_alignment.py:147-151`)は`kp_extends_beyond_candidate`(false)か`kp_adds_words_beyond_display`(:141→`_extra_tokens`:126-139)で対象を決める。`_extra_tokens`は`_GENERIC_TOKENS`(:119、one's/someone's/somebody's/someone/somebody/one/oneself)を「追加語」から**明示的に除外**(`kp_adds_words_beyond_display`のdocstring「人称代名詞の一般化(their->one's)…は『語の追加』に数えない」)。→ `in your place`→`in someone's place`は追加語0→対象0→API呼出なし(`NO_TARGETS`。a2ディレクトリに`gloss_alignment_*`ファイル無し)。
5. **通過した検査と見ていない観点**: canonicalizationのqa 12項目(`qa_person_reference_generalized`含む)は**英語KPのみ**を評価(全PASS)。Redundancy QAは5件の意味重複のみ(`keyphrase_redundancy_qa.json`)。SRC D1(`audit/src_z_posthoc_01.json`: S8 unique_containment、quote_boundary_truncated=true)はsource_sentenceの復元のみ。TTS ASRは「読み上げ=gloss文字列」の一致を見るのでglossが誤っていても通る。**日本語意味と最終英語KPの人称・指示対象の整合を見る検査は、どの工程にも存在しない**。
6. **再発性**(read-only census、全`keywords_canonicalized.json`のユニーク(key,gloss)対769件): 不定生成形(someone/one's等)を含むKPは44件。うち日本語意味に具体人称語(あなた/私/彼/彼女…)を含む不整合は**このMelos `in your place`のみ**(run_e2e_02/03/KGCPW系で全て同一glossが再出現)。他3件は`one's own`→「自分の」(再帰として正当)。X Coffeeの`shock your wallet→shock someone's wallet`(「財布に響く」)や`pump its fist→pump one's fist`は日本語意味に人称語が無く整合。→ 同種の不整合は人称一般化KPの約2%(1/44)だが、Melosは`in your place`がtopic KPに毎回選ばれるため確実に再現。

### 2-2 仮説の検証結果
- 仮説A「Promptが文脈優先で`your`を保持させた」: **一部棄却**。選定時glossは`in your place`への正しい訳で、文脈起因の人称補完ではない(英語に`your`が実在)。ただし選定Promptに「不定/所有格は具体人称に固定しない」規則が無いのは事実(§3 #1)。
- 仮説B「検査が人称・所有格の不整合を見ていない」: **実証**(上記5)。
- 追加の実証的主因: 順序依存の構造欠陥。gloss生成(選定)→英語変更(canonicalization)→gloss追従なし。OPEN-352(2026-10-13、`KP-JA-GLOSS-CONSISTENCY-FOR-EXTENDED-KP-01`)と同じ根本原因クラスで、KGCPWは「語の追加」しか是正しなかった。
- 推測(未実証): 「立場／代わり」の多義性(`in someone's place`は辞書義として(1)〜の代わりに (2)〜の立場で)。今回は文脈が(1)で語義は結果的に正しかった。人称が固定されても、再整合LLMが語義を文脈で選ぶ設計にしないと別文脈の同表現で誤る恐れ(Regressionで確認する)。

## §3 既存対策の不足(日本語意味の検査・HR・retry、人称・指示対象整合の有無)
| # | 既存対策 | 場所 | 人称・所有格・指示対象・意味関係の整合を見るか |
|---|---|---|---|
| 1 | 選定Promptのgloss規則(自然さ・括弧禁止・数値placeholder・漢数字) | `b1_p2_keywords_l_prompt_template.txt:15-23` | 見ない(規則に人称の記述なし) |
| 2 | 選定時の汎用note「所有格を含むphraseは避ける」 | `er062` `Z_KP_GENERIC_NOTE` | 英語選定への依頼であり強制ではない(今回も`your`を含むphraseが選定された) |
| 3 | canonicalization qa 12項目 | `er003_key_words_canonicalization.py` | 英語のみ。glossを入力にすら受けない |
| 4 | gloss再整合(KGCPW) | `er003_key_words_gloss_alignment.py` | **追加語の整合のみ**。人称一般化を対象外(:119,:126-139)。対象内でもPromptは「欠けている・誤っている場合のみ書換え」で人称の一般形保持を要求しない |
| 5 | 表示用/TTS用gloss分離 | `convert_display_gloss_to_tts_text` | 「～」の読み替えのみ |
| 6 | 機械検査 `validate_item_corrected` | `:406` | 括弧・算用数字・…・音声化禁止記号・mapping(記録のみ)。人称検査なし |
| 7 | gloss HR・関所(`collect_unresolved`/`collect_unevaluated`) | `:619,:629` | HR対象は再整合失敗のみ。unevaluatedは`select_alignment_targets`と同じ対象定義なので人称一般化は永久に「評価不要」 |
| 8 | Redundancy QA / SRC D1 / P8-KP Style / ASR | 各所 | 対象外(見ない) |
| 9 | 人間の最終確認 | 運用 | 今回はユーザー試聴で発見(検査では捕捉できていない) |
→ 「人称・指示対象の整合を検査する仕組み」は**存在しない**。

## §4 共通仕様の設計案(hardcode不可。特定表現の置換は不採用)
共通の前提: 修正点は(a)どのitemを再整合の対象にするか(b)再整合Promptへ何を要求するか(c)結果を決定論的にどう検証するか、の3つ。いずれも英語表現・記事に依存しない。人称語は既存の閉じた語彙表`_PERSON_DEPENDENT_TO_GENERIC`(`er003_key_words_canonicalization.py:397`)のトークン対と、日本語の人称代名詞の閉じた語彙で扱い、個別フレーズは一切持たない。

### 案I: LLM再整合の対象拡張+指示対象保持の汎用制約(Prompt中心)
- 変更: (a)`select_alignment_targets`に「人称一般化で英語が変わったitem」(`normalization_reason=="generalize_person_dependent_reference"`、または`display_phrase`のトークンが`_PERSON_DEPENDENT_TO_GENERIC`で`key_phrase`の一般形に置換されたもの)を追加。(b)`build_user_message_corrected`の項目へ`person_generalization`(例 `[{"from":"your","to":"someone's"}]`、汎用トークン対)を追加し、汎用制約を追記: 「`key_phrase`の不定の人称(someone's/one's/someone等)は日本語でも不定のまま(『誰かの』『人の』『人を』、再帰のone's/oneselfは『自分の』)表現し、`display_phrase_before_canonicalization`や`source_sentence`の具体的人称(あなた・私・彼・彼女・彼ら等)を日本語に残さない。`source_sentence`は意味の選択(例: 代わり/立場)にだけ使い、指示対象の決定には使わない。逐語訳は求めず、不定語を訳出すると不自然になる場合は人称を明示しない自然な表現にしてよい」。Promptに例示を載せる場合も、記事・特定表現に依存しない別型の表現(catch someone's attention型等)にする。(c)なし。
- 構造化(Fable例の`meaning_general`/`usage_in_text`分離): `japanese_gloss`は表示・TTS・Adv英語解説・HR・消費側(runner/page/test)多数が参照する。フィールド追加・分離は**新しい出力契約=新生成方式**に近く、全消費側の改修とP8-KP読み上げ対象の定義変更を伴う。→ 本案では`japanese_gloss`は辞書形(一般形)の1本のまま、`usage_in_text`相当は**auditログ(`gloss_alignment_runtime_metadata.json` item_log)にのみ**記録する軽量版に留める(消費側無変更)。
- 変更箇所: 共有module `er003_key_words_gloss_alignment.py`のみ(`scaffold:724-732`の呼出は無変更)。X/Z/Y共通(呼出が同一)。
- 既存承認仕様との整合: KGCPW再整合工程の対象と指示文の拡張(同工程は`APPROVED_FOR_PRODUCTION`、ユーザー原文§2①が検査・retryの改善を明示承認)。gloss HR・SRC・P8-KP Style・選定/canonicalization Promptは**無変更**。承認済みgloss規則は`load_approved_gloss_rules`が抽出して再利用するので無改変(追記は再整合固有のuser message部分のみ)。
- retry/regeneration/resume: 既存の`run_alignment_gate_corrected`のretry(最大2)とHR経路をそのまま使う。初回/redundancy retry/fallback/regenerationは全て`run_key_phrase_canonicalization`内を通る(scaffold:715のコメント)ので追加配線不要。
- 副作用: LLM判定のみなので、人称語を残しつつ`current_gloss_consistent=true`と返す取りこぼしが残り得る(検証なし)。自然さ低下は「逐語強制しない」文言で抑制。HR増は再整合失敗時のみ。
- 費用: 人称一般化itemがある記事でのみ+1回の再整合呼出。実測=1回JPY 0.0558(`er071_output/m2p0_n01_production_wiring_01/completion_04/inline_runtime_04/gloss_alignment_runtime_metadata.json`)、最悪retry込みで約JPY 0.11/記事(該当記事のみ)。census上、人称一般化itemは約6%(44/769 item)。
- 区分: **承認済み範囲内の改善**(既存工程の対象・指示の拡張)。

### 案II: 生成後の決定論的整合check(検出のみ)
- 変更: `validate_item_corrected`(または独立関数)に、英語KPに不定生成形(someone/somebody/one/one's/oneself系)があり、かつ英語KPに具体人称語が無いとき、日本語意味に日本語の具体人称語(閉じた語彙: あなた/あなたたち/君/きみ/お前/私/わたし/僕/俺/私たち/我々/彼/彼女/彼ら/彼女ら 等)が含まれれば不整合として判定。再帰(one's/oneself)は「自分/自身」を許容、someone系は「自分」も不整合。LLM呼出なし。
- 検出後: retry(再整合LLM=案Iの経路)またはHR。**検出のみでは日本語意味を修正できない**ため、単独ではretry先が無い。
- 既存整合: 新しい決定論的blocking理由の追加(既存`validate_item_corrected`のreason機構内)。
- 副作用: 閉じた語彙の取りこぼし(「その人」「相手」など具体人称語でない指示語は検出不能)、false positive(自然な「自分」の誤判定は上記の再帰許容表で抑制)。指示対象が変わっても人称語が無い訳は通る点が主な限界。
- 費用: token増0。
- 区分: 範囲内だが**単独では不十分**(修正手段が無い)。

### 案III(推奨): 案I+案II(LLM再整合+決定論的検証を既存retry/HRに接続)
- 変更: 案Iの対象拡張・指示文に加え、案IIの決定論checkを`validate_item_corrected`の検証理由として追加。LLMが人称語を残したまま返した場合は`INVALID`→既存retry(上限2)→失敗でHR(`FAILED_HUMAN_REVIEW_REQUIRED`)。
- 対象範囲の2段構え(重要): (i)**新規生成時**(`run_key_phrase_canonicalization`内): 人称一般化itemを全て再整合LLMの対象にする(語義選択と指示対象を最終KPで確認。約JPY 0.056/記事、該当記事のみ)。(ii)**永続化済みartifactの再利用・resume時**(`collect_unevaluated`、Z `stage_kp`:1275、X runner関所): 人称一般化item全件を「未評価」としてSTOPさせると、Coffee等の既存の健全artifact(`shock your wallet`等、日本語意味に人称語なし)が一斉にSTOPになる。→ (ii)は決定論check(案II)で不整合と判定されたitemだけを未評価/再整合の対象とする(健全artifactは無影響・API呼出0)。この2段はOpus確認論点(§6 #2)。
- X/Z/Y共通: 変更主座=`er003_key_words_gloss_alignment.py`。呼出元`scaffold.run_key_phrase_canonicalization`は共有。X runner関所(`er019...:528-582`)もZ `stage_kp`も同じ`collect_*`を呼ぶので追加配線は最小。
- 既存承認仕様との整合: 案Iと同じ。新規の品質観点=「最終英語KPと日本語意味の人称・指示対象の整合」は、ユーザー指示(OPEN-352委任_04: 最終英語KPとglossの意味的整合は基本品質要件)とユーザー原文§2①の明示範囲内。数値基準・新Gateは追加しない(既存のvalidate/retry/HR機構内)。
- retry/regeneration/resume: 新規生成=初回/外側retry/redundancy retry/fallbackの全経路が`run_key_phrase_canonicalization`を通るため自動反映。resume=`_load_gloss_hr_resume`(snapshot)は復元後の関所で同じ検査を通す。reuse=`stage_kp`:1275で決定論checkにより検出→メロスの再処理経路(§5)。
- 副作用: 過剰HR(正当な「あなた」を含む日本語意味)。ただし英語KPが具体人称を保持する場合は検査対象外(英語側に具体人称がある場合は検査しない)。自然さ低下は「逐語強制しない」+「人称を明示しない自然表現可」で抑制。
- 費用: 案Iと同じ(該当記事のみ約JPY 0.06〜0.11)。永続artifact再利用時は不整合itemがある場合のみ。
- 区分: **承認済み範囲内の改善(推奨)**。

### 不採用/保留案(参考、USER_DECISION_REQUIRED候補)
- 案IV: glossの生成点を選定からcanonicalization後へ移す(工程順序の変更)。選定の日本語意味規則(承認済みPrompt)の適用位置が変わる=**新生成方式**。工程全体・Prompt・Redundancy QA入力が変わるため不採用。候補として記録のみ。
- 案V: canonicalization Promptへja_glossを渡し同時に再生成させる。承認済みPrompt(canonicalization/ER-011-NO18)本文の直接編集となり、Rule7/QA 12項目との整合再検証が必要=承認範囲超過の恐れ。不採用。
- `meaning_general`/`usage_in_text`の本格的な2フィールド化: 上記のとおり消費側全体の契約変更=**新生成方式**。必要性が試聴で示されれば別判断(USER_DECISION_REQUIRED候補)。
- 選定Promptへの人称規則追加: 承認済み選定Promptの直接編集。保険として有効だが、再整合でカバーできるため今回は不採用(CURRENT_SPEC:1947等の承認済みA/B規約との整合再確認が必要)。

### Regression設計(記事・特定表現に依存しない、offline mock/決定論)
1. **決定論check(案II)の単体test**: 閉じた語彙の組合せを網羅するparametrized fixture(英語KP, 日本語意味, 期待)。例=(`catch someone's attention`/「あなたの注意を引く」→不整合)、(同/「人の注意を引く」→整合)、(`take someone's place`/「私の代わりになる」→不整合)、(`give one's word`/「約束する」→整合)、(`at one's own pace`/「自分のペースで」→整合[再帰許容])、(`stand in someone's place`型で「自分の」→不整合[someone系の再帰])、(`tell someone off`/「彼を叱る」→不整合)、(`keep an eye on someone`/「彼女を見守る」→不整合)。英語KPが具体人称を保持する場合(`each other`、`thank you`型)は検査対象外であることのtest。**個別フレーズの分岐を持たない**ことをtestで担保(fixtureを入れ替えても同一コードパスで判定される、実装コードに特定フレーズ文字列が出現しないGrepテストを含める)。
2. **対象選定のtest**: `select_alignment_targets`が、`display→key`が`_PERSON_DEPENDENT_TO_GENERIC`のトークン置換で変わったitemを対象に含み、無関係itemを含まないこと。既存の`kp_adds_words_beyond_display`の挙動(their->one'sは追加語に数えない)は変更されず、既存`er003_test_key_words_gloss_alignment.py`(70 test)が全PASSのままであること。
3. **再整合Prompt生成のtest**: `person_generalization`欄と汎用制約文がuser messageに入ること、承認済みgloss規則(`load_approved_gloss_rules`)が無改変で入ること(sha一致)。
4. **retry/HR経路のmock integration**: mock LLMが(a)初回不整合→2回目整合 (b)2回とも不整合→`FAILED_HUMAN_REVIEW_REQUIRED`となり関所がSTOPする (c)`current_gloss_consistent=true`で人称語を残した応答が`INVALID`になること。
5. **resume/reuseのtest**: 人称語を含む既存artifact(fixture)を決定論checkが検出し、健全artifact(Coffee実artifactのコピーをfixture)は検出しないこと=過剰STOPがない回帰。
6. **語義選択のtest(mock)**: 同一の英語KPに対し、文脈文が「代わり」義と「立場」義の2種類のとき、再整合Promptに`source_sentence`が渡り、検証側は人称語のみを拘束(語義は拘束しない)こと。実LLMでの語義選択は§5の実走時evidenceで確認。
7. **runtime evidence**: メロス再処理(§5)でgloss再整合が自然発火し`gloss_alignment_status`が付与されること。

## §5 メロス適用計画(改善後の正式経路で該当KP=a2 rank2を再処理)

### 5-1 既存手段の評価
- `--regenerate-stage kp_a2`: `ensure_stage`の`regenerate=True`で`w62.run_kp_stage`(選定から)を再実行する(runner:1255-1259)。**選定がLLM非決定的に再実行され、5件のKP全体が入れ替わり得る**(メロスはrun_e2e_02/03でSRC/canon retry込みで選ばれた現行5件を維持したい)。下流のTTS/Gate/Assemblyもstale化。→ 不採用(最終手段)。
- 手動でjson書換え・`resolve_gloss`(人間確定値、`er003_key_words_gloss_alignment.py:803`): ユーザー原文「手動修正のみでは未達」。不採用。

### 5-2 推奨手順(正式経路に載せる)
改善実装(委任_03以降)後、`stage_kp`の「再利用経路」にも、既存の`_src_gate`(:1278)・`collect_unevaluated`(:1275)と同じ位置(全経路共通・install_kp_assets前)で**人称整合の関所**を通す: 永続化済み`key_phrases/a2/keywords_canonicalized.json`を読み、決定論check(案II)で不整合のitemが見つかれば、**選定・canonicalizationの結果は保持したまま**既存`align_glosses`(対象=当該item)を呼んでglossのみ再生成→artifact(`keywords_canonicalized.json`と`a2_result.json`のcanonicalization.merged)を更新→`install_kp_assets`→`prov.mark_stale_descendants("kp_a2")`。これは`_load_gloss_hr_resume`(選定を再実行しない既存の復元経路、:1173)と同じ思想で、**新CLIフラグは不要**。通常の`--stage kp`(または`--stage all`)で自然発火する。
- 実走(Phase 3以降の予定): 作業dir=`C:\Users\tensh\eigo-radio`、run_e2e_03を引継ぐ別名runで`--stage kp`→関所発火→`--stage tts_a2 --only-clips kp2_ja`でP8-KP再生成。
- SRC Gate: 選定結果(source_sentence_id=S8、unique_containment)は不変で、`_src_gate`は決定論的に同一結果。
- kp_expl署名(Adv b1b専用): a2には無関係。b1bのKPは不整合なし(census)なのでb1b側のgloss不変・署名不変・再生成なし。
- P8-KP TTS: `generate_or_reuse_z`(`er063:720`)の再利用キー=canonical_text等なので、gloss文字列が変わった`kp2_ja`だけが再生成され、他clipは再利用される。`kp2_en`/他KPは不変。
- 派生物の更新: assembly(Std)・試聴ページ(Key Phrasesと日本語意味、再生順script)は通常の下流再実行。Advは不変。

### 5-3 費用見積(F-1、出典=実測)
| 項目 | 見積 | 出典 |
|---|---|---|
| 再整合LLM 1〜2回(対象1 item) | JPY 0.06〜0.11 | 実測1回0.0558(`er071_output/m2p0_n01_production_wiring_01/completion_04/inline_runtime_04/gloss_alignment_runtime_metadata.json`)。参考=run_e2e_03 `cost_log.jsonl`の`stage=kp`1呼出(578in/292out)=JPY 0.0326 |
| `kp2_ja` TTS 1 clip再生成(Gemini flash-lite+ASR) | JPY 0.1未満 | run_e2e_03 `cost_log.jsonl`の`tts_a2/kp2_ja`: gemini-3.8-flash-lite-tts 3in/43out、gpt-4o-mini-transcribe 17in/8out。`audit/cost_by_stage_17.json`のtts_a2全体=JPY 22.45/119呼出(うちClip単位の実単価は実走で確認) |
| 合計(最小経路) | **約JPY 0.1〜0.2** | 上記合算 |
| (参考)全KP再生成を選んだ場合 | LLM約JPY 3〜4+全KP TTS再生成 | run_e2e_02 `cost_log.jsonl` stage=kpの13呼出(入力33,423/出力61,862 token)を、run_e2e_03 kp 1呼出の単価0.0326/870tokで外挿(概算) |
開発費: 日次JPY 1,000枠に対し無視できる規模。個別Capは実走委任で再確認。

### 5-4 受入の見え方(予告)
改善後の正式経路で`in someone's place`の日本語意味が人称不定(例「誰かの代わりに」相当、語義=代わり)になり、`gloss_alignment_status=ALIGNED`、`japanese_gloss_tts`同値、`kp2_ja`のみ再生成、ASR判定OK、Std/Adv試聴ページのKey Phrasesが更新されること。ユーザー試聴の合否は別(技術PASS≠ユーザー試聴PASS)。

## §6 Opus独立レビュー(条件A)で確認すべき論点(5件)
1. **根本原因の捉え方**: 「誤訳」ではなく「英語変更後の日本語意味のstale化」と捉える診断は妥当か。canonicalizationへgloss入力を足す案V、生成点移動の案IVを退けてよいか。
2. **対象範囲の2段構え**: 新規生成時=人称一般化item全件を再整合、再利用/resume時=決定論checkで不整合のitemのみ、という非対称で、legacy artifactの一斉STOPを避けつつ品質を担保できるか(`collect_unevaluated`の定義変更の影響を含む)。
3. **決定論checkの語彙設計**: 日本語の閉じた人称語彙(再帰「自分」の扱い、someone系 vs one's系)は言語学的に妥当か。取りこぼし(「その人」「相手」)と過検出の許容は適切か。数値基準・新Gateを増やさず既存validate/retry/HRに収まっているか。
4. **承認境界の判断**: 再整合の指示文拡張と決定論reasonの追加は「承認済みKGCPW工程内の改善(ユーザー原文§2①)」と言えるか、「Gate/QA blocking条件の変更」としてユーザー判断が必要か。
5. **語義選択(代わり/立場)の担保とX未配線の見落とし防止**: 人称を固定しても語義を誤る恐れを、Regressionで実LLM検証する必要はあるか(費用最小のTrial設計案を含む)。X runner関所(`er019...:528-582`)への人称整合関所の配線要否、OPEN_ITEMS記録要否。

## §7 E-1分類(既存仕様・過去Trial照合)
Grep対象: `CURRENT_SPEC.md`(P8-KP|KP日本語|日本語意味|gloss HR|Source Consistency|canonicaliz|gloss再整合|人称.*一般化|共通仕様のFamily別配線)、`OPEN_ITEMS.md`(gloss|日本語意味|KP.*訳)。いずれも編集せず参照のみ。
- **A(既存仕様あり)**:
  - 共通仕様のFamily別配線Status表 `CURRENT_SPEC.md:1656-1670`(P8-KP :1666=X/Zとも`PRODUCTION_WIRED`、Style=Std KP日本語意味の**読み上げ**。テキスト生成の仕様ではない)。
  - Key Phrase日本語glossの自然さ/括弧禁止/数値placeholder回避/A・B規約/表示用TTS用分離: `CURRENT_SPEC.md:1947-1951`。
  - 人称代名詞・所有格の一般化(Canonicalization): `CURRENT_SPEC.md:1945`(閉じた語彙1対1置換、`qa_person_reference_generalized`。**日本語意味の更新は規定なし**)。
  - Source Reference Contract / SRC D1: `CURRENT_SPEC.md:1953,1956`、Source整合Gate :589。4+1構成 :1954。M2P0 :1961。
  - KP gloss再整合(KGCPW): `CURRENT_SPEC.md:2751-2759`、`OPEN-356`(`APPROVED_FOR_PRODUCTION`、PRODUCTION_WIRED判定保留)。ユーザー指示「最終英語KPとglossの意味的整合は基本品質要件」(`OPEN-352` OPEN_ITEMS.md:861)。
  - Std KP日本語意味の定義: `CURRENT_SPEC.md:1216`(P8)、:1975(英語Phrase→日本語意味(J3)→英語Phrase)、:1829-1832(W5、J3適用)。
- **B(過去Trialあり未採用)**:
  - `OPEN-352`のG2案(gloss再生成工程の新設)は標準対策とせず、KGCPW(語の追加のみ)で是正。人称一般化gloss整合は**当時のスコープ外(`_GENERIC_TOKENS`で明示除外)**で、今回の対象は本質的にその空白。
  - `OPEN-357`(目的格me/him/herが一般化されない問題)は記録のみ・開発しない(別論点)。
  - `OPEN-349`(Rule7 span外補完)・`OPEN-310`(Z KP外側retry、Rule7×人称一般化の頻発)は英語側の問題で別論点。
  - `OPEN-360`(Adv英語解説の入力phraseとgloss不整合)は英語解説側。b1bでは不整合0件(census)。
- **C(真に新規)**: 「最終英語KPの不定生成形と日本語意味の具体人称語の不整合」を決定論的に検査する閉じた語彙check、および人称一般化itemを再整合の対象に含める定義。既存仕様・過去Trialに該当記載なし(上記Grep結果に人称一般化後のgloss整合の記述は無い)。ユーザー原文§2①は「検査・retryの改善」を明示承認しているので、新規だが承認範囲内と整理(根拠=§4案III)。案IV/V/2フィールド化は範囲外=USER_DECISION_REQUIRED候補(採用しない)。
- 関連OPEN: 上記のほかOPEN-28/90/104/116/117/118/233系(gloss品質の履歴)。新規=`OPEN-419`(親、Status=PHASE1_INVESTIGATION)。X未配線の見落とし防止: 実装は共有moduleに入るためXへ自動波及するが、**X runner関所(`er019...:528-582`)の人称整合関所は未配線のため実装時に配線する**(未配線のまま完了としない)。
