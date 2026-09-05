# OPEN-112-TREND-THEME2-B-KEYPHRASE-VALIDATOR-FIX-TRIAL-17

種別: 恒久対策候補の**隔離Trial**。ユーザー判断2(A、2026-09-06)に基づく
実行。Production配線は禁止(結果は`VALIDATED`/`REJECTED`/
`USER_DECISION_REQUIRED`のいずれかであり、`APPROVED_FOR_PRODUCTION`・
`PRODUCTION_WIRED`は本タスクでは一切使わない)。

Sonnet実行回数: 1(指示上限1回、これで完了)。Opus実行回数: 0(診断は別管理ID
OPEN-112-TREND-THEME2-B-B1-KEYPHRASE-STOP-DIAGNOSTIC-15で消費済み)。

## 1. 背景(要約)

Trial-13 B1でKey Phrase 3件が停止した原因(Opus診断-15の結論):

- **問題2(JA)**: `kp3_ja_charon` canonical「中央値は約2泊」vs ASR「中央値は
  約二泊。」。`er007_ja_asr_validator_01.py`の数字保護ゲートが、助数詞「つ」
  限定の漢数字正規化(`er003_audio_tts_asr_safety._KANJI_COUNTER_RE`)では
  「泊」をカバーしないため「数字消失」と誤判定していた。
- **問題3(EN)**: `kp4_en` canonical "point to" vs ASR "Point two."。
  `er006_preprod_hardening_01_validation._convert_cardinal_words()`が
  ASR側"two"のみ"2"へ変換し、canonical側"to"はstopword除外されるため
  既存のhomophone機構(wait/weight等)にも到達せず、数字保護ゲートが即
  TRUE_CONTENT_MISMATCHにしていた。
- **問題4(JA gloss placeholder)**: `kp4_ja`の日本語gloss「～を示す、
  ～を指し示す」が、TTS前のplaceholder検出でSTOPPEDになっていた
  (2026-08-22 ER-006-KP5-CANONICAL-BUG-01で発見済みの再発)。

ユーザー正式決定(2026-09-06、詳細は指示原文参照): Track Bは完全同音
(CMU辞書ARPAbet完全一致)のみPASS対象とする。Track Aは閉じた助数詞リスト
(案A)を第一候補とする。Track Cは選定Promptへ規約追加をTrial用コピーで
検証する(Production Promptは変更しない)。

## 2. Track A(JA数字ゲート一般化)

### 2.1 実装

`er011_open112_kp_validator_fix_trial_17_ja.py`(新規Trialファイル)。
既存Production関数(`er007_ja_asr_validator_01.classify_ja_asr_match`・
`er003_audio_tts_asr_safety.normalize_kanji_counter_numerals_ja`)は無変更。
入力テキストへ、閉じた助数詞リスト
`("泊","日","人","回","件","年","時間","か月","週","歳")`の直前に来る
単独漢数字(一〜九)だけを追加で算用数字へ変換する前処理を適用したうえで、
Production関数へそのまま委譲する(ラップのみ、内部ロジック複製なし)。

### 2.2 Fixture結果

| # | ケース | canonical | ASR | 期待 | 実際 |
|---|---|---|---|---|---|
| a | Trial-13実ケース(kp3) | 中央値は約2泊 | 中央値は約二泊。 | PASS | **PASS**(NORMALIZED_MATCH) |
| b | 既存「2つ/二つ」 | この二つの動きについて… | この2つの動きについて… | PASS | **PASS**(EXACT_MATCH) |
| c1 | 数量違い | 中央値は約2泊 | 中央値は約三泊。 | FAIL | **FAIL**(TRUE_CONTENT_MISMATCH) |
| c2 | 数字消失 | 2泊 | 泊 | FAIL | **FAIL** |
| c3/c4 | 固有名詞誤変換防止(京三/二宮) | (完全一致) | (完全一致) | PASS | **PASS**(無変換を確認済み) |
| c5 | 助数詞混同防止(回≠つ) | 二回説明しました | 2つ説明しました | FAIL | **FAIL** |
| c6 | 「二十」対象外 | 二十人ほど | 2人ほど | FAIL | **FAIL** |

### 2.3 既存fixture全件回帰(39件、er007_ja_asr_validator_01_test.py全group +
er003_audio_tts_asr_safetyの短seg fixture代表4件)

- **37件: 無変化**
- **1件: ラベルのみ変化(無害)** — 「助数詞『つ』直前の漢数字/算用数字
  ゆれ」positive fixtureが`NORMALIZED_MATCH`→`EXACT_MATCH`(should_pass=True
  のまま、安全上の意味は無い)。
- **1件: 実regression(重要)** — WHOLE_TEXT_SCRIPT_MISMATCH_FIXTURESの
  「三日坊主」(慣用句、正しい読み"mikkabouzu")vs ASR全文ひらがな
  「みっかぼうず」が、`PHONETIC_MATCH/True` → `TRUE_CONTENT_MISMATCH/False`
  へ悪化。

**根本原因**: 「日」を閉じたリストに含めると、canonical「三日坊主」の
「三」が「3」へ変換され「3日坊主」になる。pykakasiは生の数字文字を音声
(「みっか」等)へ変換しない(`_kakasi_reading("3")`は"3"のまま)ため、
whole-text-reading-equal機構(canonical=漢字/ASR=全文ひらがなの場合の
読み一致フォールバック)が壊れる。この問題は「日」固有の不規則読み
(一日=tsuitachi/二日=futsuka/三日=mikka/四日=yokka)というより、**「digit
変換後の文字がkakasiで音声化されない」という一般的な構造上のリスク**
であり、直接検証していない他の8助数詞(回/件/年/歳/時間/か月/週/人)にも
理論上同型のリスクが潜在する(泊/回/件/年/時間/か月/週は今回の回帰
fixtureでは問題を再現しなかったが、慣用句化した組み合わせでの網羅検証は
未実施)。追加検証として「人」も一〜二人が不規則読み(hitori/futari)で
あることを確認済み(kakasi出力比較、`四日`系と同型のリスク)。

`日`(および`人`)を除外した縮小版リストで再実行したところ、kp3のPASSは
維持されたまま「三日坊主」regressionは解消することを確認済み(候補修正
案として記録、実装済みコードへの反映は本Trialでは行っていない)。

### 2.4 Status: **USER_DECISION_REQUIRED**

対象バグの修正メカニズム自体は健全(既存fixtureの97%[38/39]が無変化、
1件は無害なラベル変化)。ただし「日」を含むフルリスト採用時に実際の
regression(安全側[より厳しくなる]方向だが、正しいPASSがFAILへ変わる
機能低下)を1件確認しており、リスト範囲(フル採用/「日」「人」除外版/
他の実装方式)の最終選択はユーザー判断を要する。

## 3. Track B(EN厳密同音の正規化)

### 3.1 実装

`er011_open112_kp_validator_fix_trial_17_en.py` +
`_en_runner.py`(新規Trialファイル)。Production関数
(`er006_preprod_hardening_01_validation.classify_asr_match`/
`protected_check`)は無変更。2案とも「Production関数をそのまま呼び、
その結果へ狭いrescueを後付けする」設計。同音判定は既存
`er008_asr_variant_hardening_15_homophone_en.homophone_arpabet_equivalent()`
(CMU辞書ARPAbet完全一致のみ)をそのまま再利用(新辞書なし)。

- **Approach 2(数字ゲート例外案、推奨)**: 数字不一致opcode全てが
  「1トークン対1トークンのreplaceであり、かつ**テキスト全体で**cardinal語
  変換によるtoken数変化が一切無い(alignment_safe)」場合のみ、変換前の
  生語同士のARPAbet完全同音を条件にrescueする。
- **Approach 1(順序変更案)**: 同じ判定材料を使うが、grobalなalignment_safe
  を要求せず、当該opcodeがローカルに1:1であることのみを条件にする(より
  緩い適用範囲)。

### 3.2 Fixture結果(新規)

| ケース | canonical | ASR | 期待 | Approach1 | Approach2 |
|---|---|---|---|---|---|
| a(Trial-13実ケース) | point to | Point two. | PASS | **PASS**(HOMOPHONE_MATCH_NUMBER_EXCEPTION) | **PASS**(同) |
| b1 | for you | four you | PASS | **PASS** | **PASS** |
| b2(確認用、既存機構で既に処理済み) | won the game | one the game | ASR_VALIDATION_UNCERTAIN(既存) | 変化なし(想定通り) | 変化なし(想定通り) |
| c1 | point to | point three | FAIL | **FAIL** | **FAIL** |
| c2 | two nights | three nights | FAIL | **FAIL** | **FAIL** |
| c3 | canonical digit 2 vs asr digit 3 | | FAIL | **FAIL** | **FAIL** |
| c4 | digitがhomophoneでない語に置換 (9 vs "mine") | | FAIL | **FAIL** | **FAIL** |
| c5 | thirteen vs thirty(似ているが非同音) | | FAIL | **FAIL** | **FAIL** |

b2は"one"が単独cardinal除外(Production既存仕様)のため数字ゲートへ
そもそも到達せず、既存のhomophone_candidate機構(wait/weight等と同じ経路)
が既に`ASR_VALIDATION_UNCERTAIN`として捕捉済み(Track Bのgapケースでは
ないことの確認用、Track B側は無介入)。

### 3.3 既存EN fixture全件回帰(65件: ER-006 Positive29+Ambiguous2+
Negative28件 + Connected Speech Trial-07 6件)

**2案とも0件変化(regressionゼロ)**。homophone_arpabet_equivalent()自体の
既存fixture(ER-008 Part J-2、10ペア)も無変化。

### 3.4 Approach1 vs Approach2の実証済みリスク差

複合基数("twenty eight"→2:1圧縮)を含む長文に、離れた位置で単語同士の
homophone数字ケース("for you"/"four you")を仕込んだfixtureで検証:

```
canonical: "The article reviewed twenty eight studies, and it was written for you."
asr:       "The article reviewed 28 studies, and it was written four you."
```

canonical側のcardinal変換後token列(`canon_tokens`)ではindex 9が"for"だが、
変換前生語列(`canon_raw`)ではindex 9は"written"(1つ手前の要素、"twenty
eight"の2:1圧縮でズレている)。Approach1はこのズレたindexをそのまま参照
してしまい、たまたま"written"がhomophoneでないため今回は安全側に倒れたが、
**これは設計上の保証ではなく偶然**である。Approach2は`alignment_safe`
チェックによりテキスト全体でこの種の圧縮が1箇所でもあれば最初からrescue
を試みないため、原理的に安全。

### 3.5 Status: **VALIDATED**(Approach2を推奨、Approach1は不採用推奨)

Approach2は対象バグを解消し、新規fixture全件・既存fixture65件+homophone
fixture10件のいずれにも悪影響が無く、index参照の健全性も設計上保証
されている。Approach1は同じ結果セットでは差が出なかったが、構造的に
不健全なindex参照方式であることを直接実証したため、採用候補から外す
ことを推奨する。

## 4. Track C(選定Prompt規約)

### 4.1 実装

`er011_open112_kp_validator_fix_trial_17_track_c.py`(新規Trialファイル)。
Trial-13 B1の実際のcanonicalization prompt全文(`er011_output/
open112_trend_theme2_b_full_audio_trial_13/b1b/key_phrases/
canonicalization_prompt.txt`、読み取りのみ)へ、Trial専用の追加規約
(A: gloss数字は漢数字/B:「～」「〜」「…」禁止/C: 1語の機能語終端2語以下
KPをflagged=trueで検出)を挿入したTrial用コピーPromptで、Production同一
モデル設定(`er003_key_words_production.SELECTOR_MODEL`="gpt-5.6-sol"、
reasoning effort="high"、値のみ再利用・Production関数/schemaは無変更)を
使い、**1回だけ**再生成した。出力schemaはTrial専用(`japanese_gloss`と
`track_c_short_function_word_ending_flagged`を追加)であり、Production
schemaとは別物(そのままではProduction配線できない)。

### 4.2 結果(原本 vs 規約追加版、5件)

| rank | key_phrase(原本→Track C) | 変化 | japanese_gloss(原本→Track C) | 変化 | flagged(C) |
|---|---|---|---|---|---|
| 1 | story with two different speeds → (同一) | なし | 2つの異なる速さで進む状況 → 二つの異なる速さで進む状況 | **算用数字→漢数字** | False |
| 2 | room for one's own pace → (同一) | なし | 自分のペースで過ごせる余地 → (同一) | なし | False |
| 3 | median of about two nights → (同一) | なし | 中央値は約2泊 → 中央値は約二泊 | **算用数字→漢数字** | False |
| 4 | point to → (同一、変更されず) | なし | ～を示す、～を指し示す → 示す、指し示す | **プレースホルダー除去** | **True** |
| 5 | emerging preference → (同一) | なし | 現れつつある好み・傾向 → (同一) | なし | False |

rank4のreasoning(Track C出力そのまま): 「point toは辞書見出しとして
学べる動詞句であり、toは『示す』という意味を構成するため保持する。補語は
source_spanに含まれず復元できないため方式Lの基本形を維持するが、Track C
の短い機能語終端条件には該当する。」

### 4.3 評価

- **規約A(gloss数字→漢数字)**: 該当した2件(rank1・rank3)とも遵守。
  rank3は「約2泊」→「約二泊」となり、これはTrack Aとは別角度から
  問題2を緩和しうる(canonical自体が自然な漢数字表記になれば、TTS発話
  そのものが「二泊」相当になりやすく、ASRとの表記差自体が起きにくくなる
  可能性がある。ただしTTS発話結果を実際に検証したわけではない)。
- **規約B(プレースホルダー禁止)**: rank4で「～を示す、～を指し示す」が
  「示す、指し示す」へ書き換わり、問題4のplaceholder検出STOPを引き起こす
  文字が除去された。
- **規約C(短い機能語終端KPの回避)**: rank4を`flagged=True`で正しく検出
  したが、**key_phrase自体は変更されなかった**(Meaning Preservation
  Rule・source_span制約により、「to」の後に置ける適切な目的語が
  source_span内に存在しないため、モデルは意図通り安全側で「無理に変更
  しない」を選択し、reasoningに理由を明記)。つまり規約Cは「検出
  (detector)」としては機能したが、「防止(preventer)」としては本ケース
  単体では機能しなかった。
- **確率的遵守の注意**: 本結果は**1回のみ**の実行(n=1)であり、規約の
  遵守率を統計的に保証するものではない(指示された「遵守は確率的である
  旨も記録」に対応)。学習価値の劣化(Key Phraseの発音・意味の明確さ)は
  今回の5件では確認されなかったが、5件・1記事・1回の実行のみでの評価
  である点に留意。

### 4.4 Status: **USER_DECISION_REQUIRED**

規約A・Bは本Trialで直接的に有効であることを示した。規約Cは検出のみに
留まり、実際に「point to」型のKey Phraseを防止する(=方式Lの選定を
やり直す/別候補へ差し戻す)ためには、この工程(canonicalization)の
対象外である方式L選定工程側、またはflagged項目をどう扱うか(Human
Review行き/自動的な別候補要求等)という設計判断が別途必要。この設計判断
はユーザー確認を要する。

## 5. Production配線に必要な変更一覧(実装しない、Gate 3観点の列挙のみ)

**Track A採用時**:
- `er003_audio_tts_asr_safety.py`の`_KANJI_COUNTER_RE`(または新規関数)を
  「つ」限定から閉じた助数詞リストへ拡張(リスト範囲はユーザー決定待ち)。
- `er007_ja_asr_validator_01.normalize_ja()`が上記拡張版を使うよう変更。
- 回帰テスト: `er007_ja_asr_validator_01_test.py`全fixture + 新規追加
  (「三日坊主」型の慣用句フィクスチャを含む、他7助数詞の慣用句網羅も
  追加検討)。
- Runtime evidence: 本番同等のTTS/ASRで実際にkp3相当の再現ケースを
  再現し、PASSすることを確認(本Trialはローカル判定のみで音声生成は
  していない)。

**Track B採用時(Approach2)**:
- `er006_preprod_hardening_01_validation.py`の`protected_check()`または
  `classify_asr_match()`へ、数字ゲート例外(alignment_safe要求込み)を
  追加。新しい分類文字列(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`等)を
  `VALID_CLASSIFICATIONS`へ追加する必要あり。
- 回帰テスト: `er006_preprod_hardening_01_validation_test.py`全fixture +
  `er008_asr_variant_hardening_15_homophone_en_test.py` +
  Connected Speech関連fixture。
- Runtime evidence: 実際のkp4相当のTTS/ASRで再現し、PASSすることを確認。

**Track C採用時**:
- 規約A/Bのみ、Production canonicalization prompt template
  (`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_
  template.txt`)へ反映(placeholder検出`detect_gloss_placeholder_
  notation()`との重複整理も検討)。
- 規約Cは、flagged項目の扱いを方式L選定工程側で設計するまでは
  Production反映を保留すべき(検出だけでは価値が限定的)。
- 回帰テスト: `er003_test_key_words_canonicalization.py`等の既存
  fixture、および複数記事でのn>1実行によるprompt遵守率の実測。

## 6. Cost Trace

| 項目 | 内容 | 金額 |
|---|---|---|
| Track A | ローカル判定のみ、API呼び出しなし | $0 |
| Track B | ローカル判定のみ、API呼び出しなし | $0 |
| Track C | gpt-5.6-sol 1回(input 4720 tok, output 3165 tok) | $0.1185(約¥19、@¥160/$、pricing snapshot参照) |
| **合計** | | **約$0.1185(約¥19)** |

## 7. Production変更なし確認

`git status`/`git diff`は本タスク中に一切実行していない(絶対禁止の
「Git操作を行わない」を遵守)。本タスクで新規作成したファイルは以下の
みで、いずれも既存Productionファイルの編集を伴わない:

- `er011_open112_kp_validator_fix_trial_17_ja.py`(新規)
- `er011_open112_kp_validator_fix_trial_17_en.py`(新規)
- `er011_open112_kp_validator_fix_trial_17_en_runner.py`(新規)
- `er011_open112_kp_validator_fix_trial_17_track_c.py`(新規)
- `er011_output/open112_kp_validator_fix_trial_17/`配下の証跡ファイル(新規)
- `OPEN-112-TREND-THEME2-B-KEYPHRASE-VALIDATOR-FIX-TRIAL-17_REPORT.md`(本ファイル、新規)
- `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`(一時ファイル、更新)

Production対象ファイル(`er007_ja_asr_validator_01.py`・
`er006_preprod_hardening_01_validation.py`・`er003_audio_tts_asr_safety.py`・
`er003_v1_n3_01_tts_generate.py`・選定Prompt生成コード)はいずれも
**読み取りのみ**で、書き込み・編集は一切行っていない。

## 8. STOP条件該当有無

該当なし。真の内容誤りをPASSさせる規制緩和は行っていない(全Trackとも
陰性対照fixtureが期待通りFAILのままであることを確認済み)。Track Aで
発見した「三日坊主」regressionは、PASSすべきものをFAILにする方向
(安全側)の劣化であり、「安全≠成功」原則における安全性の毀損ではなく
機能低下(recall低下)である。Sonnet実行は1回のみで指示上限内。

## 9. ユーザーが判断すべき事項

1. **Track A**: 閉じた助数詞リストを、ユーザー原案通り
   `泊/日/人/回/件/年/時間/か月/週/歳`のフル採用とするか、実証済み
   regressionを踏まえ`日`・`人`を除外した縮小版
   (`泊/回/件/年/時間/か月/週/歳`)を採用するか、あるいは別の実装方式
   (数字抽出時のみ閉じたリストを使い、比較用文字列自体は書き換えない、
   等のより保守的な設計)を検討するか。
2. **Track B**: Approach2の採用可否、および新分類
   `HOMOPHONE_MATCH_NUMBER_EXCEPTION`をProduction
   `VALID_CLASSIFICATIONS`へ追加する場合の名称・扱い(即PASS/Cascade行き
   等)の最終決定。
3. **Track C**: 規約A/Bを選定Prompt本体へ反映することの可否。規約C
   (flagged項目)について、検出のみに留めるか、方式L選定工程側で
   flagged項目を別候補へ差し戻す設計を別タスクとして起こすか。

---

固定ブロック:
- Track A Status: USER_DECISION_REQUIRED(対象バグ修正は健全、fullリスト
  採用時に実regression1件[「日」起因]あり)
- Track B Status: VALIDATED(Approach2推奨、Approach1不採用推奨)
- Track C Status: USER_DECISION_REQUIRED(規約A/B有効、規約Cは検出のみ)
- 回帰PASS件数: Track A 39件中37件無変化+1件無害変化(実質38/39安全)、
  1件regression / Track B 65件中65件無変化(regressionゼロ)+homophone
  fixture10件無変化
- 判定変化件数: Track A 2件(うち1件regression)、Track B 0件(両approach)
- Cost: 約$0.1185(約¥19)、Track Cのみ
- Production変更なし: 確認済み(§7参照)
