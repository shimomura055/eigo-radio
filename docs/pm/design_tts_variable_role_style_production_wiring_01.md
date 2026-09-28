# design_tts_variable_role_style_production_wiring_01.md

管理ID: `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`(Phase A、設計のみ、
Production code/Prompt/SSOT/Trial scriptは一切変更していない)。

ユーザー正式決定(前提): 日本語=**J3**、英語=**E2**、`APPROVED_FOR_PRODUCTION`
(`TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02`)。本設計書はPhase B実装の
最小diff案を提示するのみで、まだ配線しない。

---

## 1. J3/E2の逐語抽出(`er044_tts_variable_spoken_role_style_trial_02.py`)

### J3(日本語、role非依存の単一style)

```
J3 = "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
     "演技がかった話し方は避けてください。"
```
(L60-63、`J_PATTERN_STYLES["J3"]`。日本語はEN側のような role別辞書ではなく、
J0-J3が単一文字列でJA_SEGMENTS全体[preview/comment_1〜4]へ一律適用される
設計。L58-64参照)

### E2(英語、role別)

```python
E_PATTERN_STYLES = {
    "FULL_STORY": {
        "E2": "calm, steady news narration with natural emphasis at key points and turns; not dramatic.",
    },
    "IN_ONE_LINE": {
        "E2": "concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.",
    },
    "TOPIC_INTRO": {
        "E2": "brief, clear, engaging news topic introduction with natural emphasis on the topic; not "
              "dramatic.",
    },
}
```
(L69-92)

生成結果jsonとの一致確認: `generate_ja_pattern_segment`/`generate_en_pattern_segment`
はいずれも `r["style_prefix_used"] = style` を実TTS呼び出し直前に使った
値そのままセットしており(L163, L192)、上記定数と生成結果audit
(`style_prefix_used`)が同一値になることをコードレベルで確認した(実行はしていない、
コード読解ベースの確認。Phase B runtime evidenceで実測確認する)。

---

## 2. Existing Spec Check(Grep先・行番号付き)

### (a) 英語役割別style機構は既にProduction配線済み(`APPROVED_FOR_PRODUCTION`、
`PRODUCTION_WIRED`は未判定)

- `er033_tts_flash_lite_family_x_styles_01.py`(L36-43)
  `FAMILY_X_ROLE_STYLE_EN = {"TOPIC_INTRO": "brief, clear, engaging news
  topic introduction", "PREVIEW": "calm, conversational", "COMMENT": "calm,
  conversational", "FULL_STORY": "calm, steady news narration",
  "HEADING_READOUT": "brief and clear", "IN_ONE_LINE": "concise, clear"}`。
  これがTrial-02のE0(「Production現状」)と**完全一致**することを確認した
  (TOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3role)。
- `FAMILY_X_ROLE_STYLE_EN_FALLBACK = ["natural, clear, conversational",
  "clear"]`(L55)。fallback(minimal instruction)発動時に使う短い代替style
  (Trial attempt2相当の技術判断、実測に基づくものではない旨コメント明記)。
- `er019_family_x_audio_production_runner_01.py`の`_role_style()`
  (L491-497、A2側L691-694)は **`tts_backend != "speech_metadata_flash_lite"`
  の場合は常に`None`を返す**設計(既定backend=`structured_separation`では
  6-role styleは一切適用されず、`style_prefix_override=None`と同じ=既存
  Family A/B/C挙動と同一)。role→segment対応:
  - Advanced(B1B、`generate_family_x_b1_segments`): topic_intro→TOPIC_INTRO
    (L532)、preview/comment_1-4→PREVIEW/COMMENT(L547、Charon英語)、
    full_story_part1・in_one_line→FULL_STORY/IN_ONE_LINE(L573)、
    full_story_part2/3見出し→HEADING_READOUT(L593)、
    full_story_part2/3本文→FULL_STORY(L608)。
  - Standard(A2、`generate_family_x_a2_segments`): topic_intro→TOPIC_INTRO
    (L740)、full_story_part1・in_one_line→FULL_STORY/IN_ONE_LINE
    (`_role_style_slower`経由でA2_SLOWER_PACE_INSTRUCTIONと連結、L772)、
    full_story_part2/3見出し→HEADING_READOUT(L794)、本文→FULL_STORY(L807)。
    A2のpreview/comment_1-4は**日本語**(`n3_tts.generate_a2_japanese_
    with_reading_safety`、L753-760)であり英語role styleの対象外。
- `n3_tts.A2_SLOWER_PACE_INSTRUCTION`との重畳: `_role_style_slower()`
  (L696-712)が「6-role短style + 既承認減速instruction(逐語)」を`\n`連結
  する設計として**既にProduction実装済み**(`assert_no_wpm_specification`
  で連結後文字列も検査、N-7是正済み)。E2適用時もこの連結構造は無変更で
  そのまま機能する(E0→E2の値置換のみで、連結ロジック自体に変更は不要)。
- **CURRENT_SPEC.md L1502-1555の確認**: `TTS-GEMINI-3.8-FLASH-LITE-
  PRODUCTION-WIRING-FAMILY-X-02`で「B-2(6-role style): Standard(A2)/
  Advanced(B1B)両方の基本仕様」「Fable Gate 3判定: `PRODUCTION_WIRED`
  (2026-09-28、スコープ: `--tts-backend speech_metadata_flash_lite`明示時
  の経路)」と明記されている。**重要**: 6-role EN styleの配線自体は既に
  `PRODUCTION_WIRED`だが、これは`speech_metadata_flash_lite` backend
  選択時のみ有効という条件付きであり、既定backend(`structured_separation`)
  ではFamily Xを含め無変更のまま(Family A/B/Cはこの機構を一切import
  しない、Dangling Reference Check維持)。**本タスクのE2配線は、この
  既存の`APPROVED_FOR_PRODUCTION`+条件付き`PRODUCTION_WIRED`な仕組みの
  「値の中身」をE0→E2へ更新するだけであり、新しい配線経路を作る必要は
  ない**(FULL_STORY/IN_ONE_LINE/TOPIC_INTROの3roleのみ、PREVIEW/COMMENT/
  HEADING_READOUTは対象外=不変のE0のまま)。

### (b) 日本語: style override機構が経路の途中で消える(OPEN-229の技術的実体)

呼び出し連鎖(Standard/A2のJA preview/comment_1-4、japanese_titleも同型):

```
er019.generate_family_x_a2_segments()
  → n3_tts.generate_a2_japanese_with_reading_safety()  [er003_v1_n3_01_tts_generate.py L582]
      ※ style_prefix_override引数が存在しない(OPEN-229記載どおり)
    → n3_tts.generate_a2_japanese_with_fallback()      [同L473]
      ※ こちらも style_prefix_override引数が存在しない
      標準経路(L507-509): c.generate_narration_snippet_verified_strict(
          text, "ja", out_path, expected_substring, ...)  ※style関連引数を渡していない
      fallback経路(L525): _generate_a2_japanese_minimal_instruction(text, out_path, tts_backend=...)
        → 常に _A2_JA_MINIMAL_INSTRUCTION_PREFIX 固定(L426-429、FAMILY-X-02
          D-1のユーザー確定仕様により意図的に無変更、J3化の対象外)
        → repro01.generate_narration_snippet_verified_strict(language="ja", style_prefix_override=...)
          [er003_v1_repro01_main_generate.py L196]
          ※ この関数自体は style_prefix_override 引数を持つ(L206)が、
            L291 `if language == "en":` の分岐内でのみ base_style_prefix
            を解決しており、language=="ja"の場合はstyle_prefix_overrideを
            一切参照せず、そのままL318-321でp9a.generate_narration_snippet
            へ転送するだけ(=呼び出し元がja用に値を渡せば実際にp9aまで
            届く。届かないのはp9a側)。
          → p9a.generate_narration_snippet(language="ja", style_prefix_override=...)
            [er003_b1_p9a_audio.py L199-231]
            ※ L227-229 `elif language == "ja": style_prefix, model_name =
              JAPANESE_STYLE_PREFIX, JAPANESE_MODEL_NAME` — **ここで
              style_prefix_overrideが完全に無視される**(EN分岐L225は
              `style_prefix_override or ENGLISH_STYLE_PREFIX`と対称的な
              形になっているが、JA分岐だけ非対称)。
```

**確定した事実**: OPEN-229が指摘する「style override機構自体が存在しない」
は、(1) `generate_a2_japanese_with_reading_safety`/`with_fallback`の
signatureレベルで引数が存在しない、(2) 仮にその2段を通り抜けても
最終層`p9a.generate_narration_snippet`のja分岐が値を握りつぶす、という
**二重の欠落**であることが分かった。EN側は既に対称な設計
(`style_prefix_override or ENGLISH_STYLE_PREFIX`)が3層すべてに存在するため、
JA側もこの対称性に合わせる形の最小diffが自然(§3参照)。

呼び出し元一覧(`generate_a2_japanese_with_reading_safety`/
`JAPANESE_STYLE_PREFIX`のGrep、Family共有状況):
- `er019_family_x_audio_production_runner_01.py`: Family X A2の
  japanese_title(L748)、preview/comment_1-4(L758)、Key Phrase meaning
  (L853、KP対象外なので本タスク範囲外)。
- `er003_b1_p9a_audio.py`: `JAPANESE_STYLE_PREFIX = p7a.JAPANESE_STYLE_PREFIX`
  (L136、Family共有の実体定義はp7a側、p9aはre-export)。Family A/B/C
  (legacy)はこのモジュールの`generate_narration_snippet`/
  `generate_narration_snippet_verified_strict`(repro01経由)を共有関数
  として使っており、JA分岐の挙動(常にJAPANESE_STYLE_PREFIX)は全Family
  共通(Family Xも含め現状は同じ)。
- 本タスクで`p9a.generate_narration_snippet`のja分岐へ`style_prefix_override
  or JAPANESE_STYLE_PREFIX`という**Noneのとき従来通り**の変更を入れれば、
  Family A/B/Cを含め既存呼び出し元は全員`style_prefix_override=None`
  (未指定)のままなので**挙動は無変化**(EN側で既に採用されているのと
  同じ後方互換パターン)。

### (c) 固定Master phrase(shell)経路は別定数、本タスクの影響を受けない

- `er006_audio_cost_pilot_02_shared_narration.py` L88-149:
  `_resolve_shell_english_style_prefix_override(tts_backend)`という
  **独立した関数**がshell(welcome/preview_intro/key_phrases_intro/
  full_story_intro/num_one〜five)のstyleを解決しており、
  `SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION`
  (`"v2_flash_lite_short_style"`、実体は`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`
  = fallback短styleを流用、CURRENT_SPEC L1531-1539の「修正3回目」決定)を
  参照する。JA shellも`style_instruction_id="charon_japanese_fixed_shell"`
  (L135)という別IDで、Family X A2/B1B可変segmentのJAPANESE_STYLE_PREFIX
  経路とは異なるMaster Audio Store key空間に属する。**本タスクの
  FAMILY_X_ROLE_STYLE_EN更新・JA style override追加は、この
  `_resolve_shell_english_style_prefix_override`関数を一切呼ばず・
  参照しないため、shell系には影響しない**。

### (d) Master Audio Store: 可変segmentはそもそも対象外

- `er006_master_audio_store_01.py` L6-12(モジュール冒頭コメント):
  「対象は意図的に(1)完全固定segment(2)B1/A2完全一致Key Phraseの2種類に
  限定する。**可変ナレーション(Story本文・Comment等)には適用しない**」
  と明記。`EQUALITY_FIELDS`(L35-39)に`style_instruction_id`/
  `style_instruction_version`が含まれるが、これはStore対象(固定shell/
  Key Phrase)のみに使われるフィールドであり、preview/comment/full_story/
  topic_intro/in_one_line(本タスクの対象segment)はStoreの
  `MasterAudioKey`を一切生成しない。**J3/E2配線はMaster Audio Store・
  reuse telemetryに一切影響しない**(manifest不変)。

### (e) retry/fallback/regeneration経路の一貫性

| 経路 | style解決方法 | J3/E2の反映 |
|---|---|---|
| 標準attempt 1・2回目(同一呼び出し内) | `style_prefix_override`は呼び出し元が1回だけ渡す静的値、2回のattemptとも同じ値を使う(`generate_a2_japanese_with_fallback`L507-509、`generate_narration_snippet_verified_strict`のfor loop内で毎回同じ`style_prefix_override`を使用) | 反映される(J3/E2固定) |
| minimal instruction fallback(3回目) | JA: `_A2_JA_MINIMAL_INSTRUCTION_PREFIX`固定(J3化しない、FAMILY-X-02 D-1踏襲)。EN: `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`固定(既存、E2化しない) | 意図的に対象外(fallback短styleは既存のまま) |
| Local Rewrite(`er020_tts_retry_local_rewrite_01`) | canonical textを言い換えるだけでstyle引数には関与しない(`resolve_narrative_role`/`connected_speech_enabled_for`はrole gatingのみ) | J3/E2はLocal Rewrite後の再生成でも同じ値のまま使われる(styleパラメータ自体は書き換わらない) |
| segment単位の再実行(同じrunner関数を再度呼ぶ) | `_role_style()`/(新設予定)`_role_style_ja()`は毎回同じ`tts_backend`引数から同じ値を再計算する決定的関数 | 反映される(実行のたびに同じJ3/E2が使われる、drift無し) |
| `--stage all` | 本タスク・Phase Bとも使用しない(delegation D-1で明記) | 該当なし |

### (f) CURRENT_SPEC/OPEN_ITEMS該当箇所

- `CURRENT_SPEC.md` L1502-1555: `TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-
  WIRING-FAMILY-X-02`のB-2(6-role style)・Fable Gate 3判定(条件付き
  `PRODUCTION_WIRED`)・「JA segmentは既存styleテキストを流用(変更なし)」
  の記載を確認。
- `OPEN_ITEMS.md` OPEN-201(L383、Gate3配線追跡): 末尾に「**2026-09-28
  追記**: JA側はRole Style未配線(OPEN-229)」と明記。
- `OPEN_ITEMS.md` OPEN-229(L412): 「Production のJA音声(Standard
  preview/comment)に役割別Role Style機構が存在せず、常に長文instruction
  `JAPANESE_STYLE_PREFIX`を使用」「短いJA Role Style(J1〜J3の方向)を
  Productionへ新規配線するか、現行の長文instruction路線を維持するかは
  ユーザー判断待ち」とあり、Status欄は`OPEN`のまま(**本タスクの委任文
  ヘッダはこの判断が既に完了しJ3採用で`APPROVED_FOR_PRODUCTION`確定と
  述べており、OPEN-229本体の文言更新は並行稼働中の別Agent
  [「SSOT反映Agent」]が担当中と理解している。本設計書はこの相違を
  矛盾として扱わずそのまま記録するに留め、実際のOPEN-229クローズ・
  DECISION_LOG追記は委任文どおりPhase Bで別途行う)**。
- OPEN-221/222/223/226: 今回のGrep範囲では`FAMILY_X_ROLE_STYLE_EN`/
  fallback短style関連の既存所見(OPEN-222の shell NUMBER_LABEL style
  drift等)であり、本タスクの3role(FULL_STORY/IN_ONE_LINE/TOPIC_INTRO)
  E2化・JA J3新規配線とは別事象(直接の依存なし)。

---

## 3. 最小diff案(逐語)

### 3-1. 英語E2(`er033_tts_flash_lite_family_x_styles_01.py`)

`FAMILY_X_ROLE_STYLE_EN`の3値のみ更新(PREVIEW/COMMENT/HEADING_READOUTは
不変):

```python
FAMILY_X_ROLE_STYLE_EN = {
    "TOPIC_INTRO": "brief, clear, engaging news topic introduction with natural emphasis on the topic; "
                   "not dramatic.",
    "PREVIEW": "calm, conversational",                      # 不変(E2未検証、対象外)
    "COMMENT": "calm, conversational",                      # 不変(E2未検証、対象外)
    "FULL_STORY": "calm, steady news narration with natural emphasis at key points and turns; not dramatic.",
    "HEADING_READOUT": "brief and clear",                   # 不変(E2未検証、対象外)
    "IN_ONE_LINE": "concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.",
}
```
影響ファイル: `er019_family_x_audio_production_runner_01.py`(値を参照する
だけで呼び出し方は無変更)。**新規定数は追加しない**(既存定数の値更新のみ、
version付き新定数への切替は不要と判断: 理由は、この機構自体が既に
`--tts-backend speech_metadata_flash_lite`という明示的opt-inフラグの
配下にあり、既定backend利用者には一切影響しないため。version管理は
Master Audio Store側の`tts_model_id`が既に担っており、style文字列自体の
version管理までは不要)。

既存テストへの影響: `er033_tts_flash_lite_family_x_styles_01_test_01.py`/
`er019_family_x_flash_lite_role_style_wiring_02_test_01.py`が
`FAMILY_X_ROLE_STYLE_EN`のE0文言をリテラルでassertしている可能性が高い
(Grepで参照確認済み、値までは未確認)。Phase Bで該当assertionをE2値へ
更新する(E0→E2は文言追加のみで構造は同じ、破壊的変更ではない)。

### 3-2. 日本語J3

**方針**: Trial-02(`er044`)が実際に使ったのと同じ「置換」方式(J3は
`JAPANESE_STYLE_PREFIX`を完全に**置き換える**独立した短い文字列であり、
長文PREFIXへの**併記・連結ではない**)を踏襲する。根拠:
`er044.J_PATTERN_STYLES`はJ0(=`p9a.JAPANESE_STYLE_PREFIX`そのもの)と
J1-J3(短い独立文字列)を同じ辞書の兄弟キーとして持ち、
`generate_ja_pattern_segment`は選んだ1つの`style`だけを
`t01.generate_ja_role_style(..., style, ...)`へ渡す(L157-165)。
`t01.generate_ja_role_style`内部(`er038_tts_all_spoken_role_style_trial_01.py`
L331-333)は`style_prefix`パラメータを`flw.resolve_tts_call_and_prompt`
経由で**そのままprompt構築に使う**(=Production標準経路の
`JAPANESE_STYLE_PREFIX`と完全に同じ使われ方の場所に、J3を代入している)。
すなわちTrial自体が「置換」方式で実施・ASR検証済みであり、Phase Bも
これと同一の扱いにする(Trial結果との整合性を壊さないため)。

a) `er003_b1_p9a_audio.py` L227-229(EN分岐L225と対称にする、1行差分):

```python
    elif language == "ja":
        style_prefix, model_name = style_prefix_override or JAPANESE_STYLE_PREFIX, JAPANESE_MODEL_NAME
```

既定`style_prefix_override=None`のため、既存全呼び出し元(Family A/B/C/X
問わず)は挙動無変化。

b) `er003_v1_n3_01_tts_generate.py` L473-509
`generate_a2_japanese_with_fallback`へ`style_prefix_override: str | None = None`
引数を追加し、標準経路呼び出し(L507-509)にのみ転送する(fallback経路
L525は既存どおり変更しない=FAMILY-X-02 D-1の「JA minimalは既存テキスト
流用を明記」を踏襲、J3は標準経路のみ):

```python
def generate_a2_japanese_with_fallback(text: str, out_path: str, expected_substring: str,
                                        max_extra_chars: int = 40,
                                        max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
                                        standard_attempts: int = review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS,
                                        expected_readings: dict | None = None,
                                        style_prefix_override: str | None = None,  # 新規、既定Noneで無変更
                                        tts_backend: str = "structured_separation") -> dict:
    ...
    standard = c.generate_narration_snippet_verified_strict(
        text, "ja", out_path, expected_substring, max_attempts=standard_attempts, max_extra_chars=max_extra_chars,
        expected_readings=expected_readings, style_prefix_override=style_prefix_override,
        tts_backend=tts_backend)
```

c) `er003_v1_n3_01_tts_generate.py` L582-589
`generate_a2_japanese_with_reading_safety`へ同じ`style_prefix_override:
str | None = None`引数を追加し、L647の`generate_a2_japanese_with_fallback`
呼び出しへ転送する。

d) `er033_tts_flash_lite_family_x_styles_01.py`へJ3定数を追加(EN側と
同じ「Dangling Reference Check」設計、Family A/B/Cはこのモジュールを
importしないためJA側も追加してよい):

```python
# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B)実装時に追加予定
# TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02 J3をそのまま転記(新規style考案なし)。
FAMILY_X_ROLE_STYLE_JA = (
    "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
    "演技がかった話し方は避けてください。"
)
```
(既存の`FAMILY_X_JA_STYLE_NOTE`(L76-81)は「Phase 1時点ではFamily Xランナー
からは参照しない」という**Phase 1限定**の注記であり、Trial-02でJ3が
ASR実測・ユーザー承認された現在は前提が変わっている。この注記文言自体も
Phase Bで「Phase 2でTrial-02のJ3を採用、実配線」へ更新する必要がある。)

e) `er019_family_x_audio_production_runner_01.py`の
`generate_family_x_a2_segments`(L660-833)へ、EN側`_role_style()`
(L691-694)と対称な`_role_style_ja()`を新設し、preview/comment_1-4の
呼び出し(L753-760)にのみ`style_prefix_override=_role_style_ja()`を渡す
(japanese_title[L745-751]は**Trial-02のJA_SEGMENTS対象外**なので本タスクの
対象外のまま、意図的に据え置く。理由: Trial-02の`JA_SEGMENTS_REQUIRED`/
`OPTIONAL`はpreview/comment_1〜4のみでjapanese_titleを含んでいない
(L97-98)。Trial範囲外への拡張は「新仕様の創作」に当たるため、本タスクの
禁止事項に抵触する):

```python
    def _role_style_ja() -> str | None:
        # Family Xランナーのみが参照する(Dangling Reference Check、EN側
        # _role_style()と対称)。既定backendではNoneを返し、既存
        # generate_a2_japanese_with_reading_safetyのstyle_prefix_override
        # 既定None(=JAPANESE_STYLE_PREFIX)と同じ(既存挙動、他Family無影響)。
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.FAMILY_X_ROLE_STYLE_JA
```

```python
    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav",
                lambda text=text: n3_tts.generate_a2_japanese_with_reading_safety(
                    text, f"{narration_dir}/{name}.wav", n3_tts.expected_substring_ja(text),
                    style_prefix_override=_role_style_ja(),
                    tts_backend=tts_backend), expected_text=text)
```

**ゲート設計の論点(§7で再掲、Fable/Opus L2判断候補)**: EN E2と同じく
`tts_backend == "speech_metadata_flash_lite"`をゲートに使う設計案とした。
理由: (1) 既存6-role EN機構と対称にすることで、Family A/B/C・既定backend
利用者への影響ゼロを機械的に保証できる(このゲート自体が既に
`PRODUCTION_WIRED`判定済みの安全機構)。(2) J3自体はTrial-02で
`speech_metadata`方式(flash-lite)を使って生成・ASR検証されており、
既定backend(`structured_separation`、現行`gemini-2.5-pro-preview-tts`)で
J3が同じ挙動を示すかは未検証。**ただし**、delegationの適用範囲記載
「対象となる可変日本語segmentへ適用」はbackend限定を明記しておらず、
「Family X ではFlash-Liteへ原則統一する」というFAMILY-X-02のC決定が
将来標準になる前提であれば、既定backend(`structured_separation`)にも
J3を適用すべきかは別途ユーザー判断が必要な論点として残す(STOP候補、
§7)。

f) 固定phrase・Key Phrase(KP EN/JA/英語解説)は対象外: japanese_title
(A2)、`_generate_key_phrase_segments_a2`/`_b1`内の
`generate_charon_japanese_with_reading_safety`(KP日本語gloss)・
`ensure_key_phrase_english_component`(KP英語)、
`er006_audio_cost_pilot_02_shared_narration`のshell一式は、いずれも
本タスクのdiffが一切触れない関数・呼び出し経路のまま(§2(c)(d)で確認
済み)。

---

## 4. runtime evidence案

既存の`tts_generation_results.json`(`er019`のL619-621/822-824で保存)は
segmentごとの生成結果dictをそのまま保存しており、Trial-02の
`style_prefix_used`と同じフィールド名を、Production側でも既に持つ
関数(`generate_narration_snippet_verified_strict`等)の戻り値へ追加すれば
実文字列を記録できる。ただし現状のProduction関数群(`generate_narration_
snippet`/`generate_narration_snippet_verified_strict`)の戻り値には
`style_prefix_used`フィールドが**存在しない**(`model`/`voice`/
`tts_backend`は既にL280-284で記録済み)。

**Phase B最小追加案**: `p9a.generate_narration_snippet`の戻り値dict
(L280-285)へ`"style_prefix": style_prefix`を1行追加する(EN/JA両分岐で
共通に使っている変数をそのまま記録するだけ、新規計算なし)。これにより
`tts_generation_results.json`のsegmentごとentryへ、実際に使われたstyle
文字列(J3/E2 or 既存値)・model・voiceが揃って残る。追加は戻り値dictへの
1フィールド追加のみで、既存フィールドの意味・呼び出し契約は変更しない。

---

## 5. Regression計画(Phase B)

- 対象: Hormuz(既存run実績がある記事)の**Standard(A2)JA可変segment**
  (preview/comment_1〜4)+**Advanced(B1B)EN可変segment**
  (topic_intro/full_story_part1〜3[+heading]/in_one_line)を、専用out-dir
  (`er0XX_output/tts_variable_role_style_production_wiring_01/...`のような
  新規ディレクトリ、既存記事artifactは無変更)でTTSのみ再生成する
  (`--stage all`禁止、対象segment明示、`tts_backend=speech_metadata_flash_lite`
  明示指定)。
- ASR/drift確認: 既存`generate_narration_snippet_verified_strict`の
  標準ASR検証(EN: secondary_asr.evaluate_attempt_with_cascade、
  JA: ja_secondary.evaluate_attempt_ja_with_cascade)がそのまま働くため、
  追加の検証ロジックは不要(既存Cascade自体がPASS/FAILを判定する)。
- 費用概算: Trial-02実測¥20.71/24segment(delegation記載の実測値)を
  根拠に、対象segment数(Hormuz Standard 5[JA]+Advanced 5[EN、
  heading2件含む]=概算10segment程度)から¥10前後を見込む(Trial時の
  1segmentあたり平均¥0.86換算、実際はfallback発火頻度により変動)。
  Guardrail予算は別途Phase B委任時にFableが設定する。
- 既存テストへの影響: `er033_tts_flash_lite_family_x_styles_01_test_01.py`/
  `er019_family_x_flash_lite_role_style_wiring_02_test_01.py`/
  `er038_tts_all_spoken_role_style_trial_01_test_01.py`/
  `er044_tts_variable_spoken_role_style_trial_02_test_01.py`のうち、
  `FAMILY_X_ROLE_STYLE_EN`のE0文言をリテラルassertしているテストのみ
  E2値へ更新(Trial系[er038/er044]はTrial専用scriptなので変更不要、
  対象は主にer033/er019のProduction側テスト)。新規テストとして、
  `generate_a2_japanese_with_fallback`/`with_reading_safety`の
  `style_prefix_override`引数追加に対する後方互換テスト(既定Noneで
  従来のJAPANESE_STYLE_PREFIXを使うことの確認)・JA標準経路への
  override実配線テスト・EN側p9a ja分岐の対称性テストを追加する。
- 固定Masterのreuse不変性の確認方法: Regression実行後、
  `er006_output/master_audio_store_01/manifest.json`の
  `git diff`(または実行前後のSHA比較)が空であることを確認する
  (§2(d)の設計根拠どおり、可変segmentはStore対象外のため理論上
  差分ゼロのはずだが、Phase Bで実際にdiffを取ってrun時証跡とする)。

---

## 6. SSOT文案(Phase Bで反映、本Phase Aでは編集しない)

### CURRENT_SPEC.md(Role Style節への追記案)

`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02`のB-2記載
「JA segmentは既存styleテキストを流用(変更なし)」の直後に追記:

> **`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`(Phase B、[日付]、
> `APPROVED_FOR_PRODUCTION`元決定: `TTS-VARIABLE-SPOKEN-ROLE-STYLE-
> TRIAL-02`)で上記「JA変更なし」を更新**: JA可変segment(Standard A2の
> preview/comment_1〜4のみ、japanese_title・Key Phraseは対象外)は
> `--tts-backend speech_metadata_flash_lite`明示時に限り、Trial-02実測
> 確認済みのJ3「落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に
> 応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてくだ
> さい。」を`JAPANESE_STYLE_PREFIX`の代わりに使う(置換、併記ではない)。
> 英語側6-role(`FAMILY_X_ROLE_STYLE_EN`)のうちTOPIC_INTRO/FULL_STORY/
> IN_ONE_LINEの3roleをE0からE2(Trial-02実測値)へ更新、PREVIEW/COMMENT/
> HEADING_READOUTは不変(E2未検証のため対象外)。fallback(minimal
> instruction)経路・固定Master shell・Key Phraseは無変更。既定backend
> (`structured_separation`)・Family A/B/Cは無影響。Fable Gate 3判定:
> [Phase B実装後にPRODUCTION_WIRED判定予定、Mandatory Opus L2レビュー後]。

### DECISION_LOG.md(追記案)

> `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`: `TTS-VARIABLE-SPOKEN-
> ROLE-STYLE-TRIAL-02`でユーザーが正式決定したJ3(JA)/E2(EN)を、既存の
> `PRODUCTION_WIRED`済み6-role style機構(`TTS-GEMINI-3.8-FLASH-LITE-
> PRODUCTION-WIRING-FAMILY-X-02`、`speech_metadata_flash_lite` backend
> 限定)へ配線した。JA側はOPEN-229が指摘した`style_prefix_override`
> パラメータ不在(`generate_a2_japanese_with_reading_safety`/
> `with_fallback`/`p9a.generate_narration_snippet`のja分岐)を、EN側と
> 対称な設計(既定None=従来挙動維持)で解消した。

### OPEN-229追記案

> **Phase B配線完了(`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`)**:
> `generate_a2_japanese_with_reading_safety`/`with_fallback`へ
> `style_prefix_override`引数を追加、`p9a.generate_narration_snippet`の
> ja分岐をEN分岐と対称化(`style_prefix_override or JAPANESE_STYLE_PREFIX`)。
> Standard(A2)のpreview/comment_1〜4のみ、`speech_metadata_flash_lite`
> backend時にJ3を使用。Status: `OPEN`→`CLOSED`(J3採用が正式決定・
> 配線完了のため)。

### OPEN-201追記案

> **追記**: JA側Role Style未配線の指摘(上記2026-09-28追記)は
> `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`で解消(OPEN-229参照)。

### REPORT_LEDGER行案

> `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01` | Phase A: 設計書
> (J3/E2逐語・既存経路確認・最小diff案)。Phase B: [実装後に追記] |
> `APPROVED_FOR_PRODUCTION`(未配線)→[Phase B後の到達Status]

---

## 7. リスク・Opus L2論点候補

1. **共有関数(`p9a.generate_narration_snippet`)変更の後方互換**: JA分岐
   1行変更(`style_prefix_override or JAPANESE_STYLE_PREFIX`)は、既存の
   全呼び出し元が`style_prefix_override=None`(未指定)のままである限り
   byte-identicalである。ただしこの関数はFamily A/B/C(legacy)も共有する
   ため、変更後に他Familyが意図せず`style_prefix_override`を渡している
   箇所がないか、Phase B実装時に`git grep`で全呼び出し元を再確認する
   必要がある(Phase Aでは「現状は誰も渡していない」ことのみ確認済み、
   §2(b))。
2. **Family Aへの無影響の証明方法**: (a) `git diff`後に
   `pytest er019_output`系の既存Family A/B/Cテストが変更なしでPASSする
   ことを実行して示す、(b) Family A/B/Cのrunnerコードが
   `er033_tts_flash_lite_family_x_styles_01`を一切importしていないこと
   (Dangling Reference Check、既存設計)を維持する、の2点をPhase Bの
   検証項目に含める。
3. **J3と長文PREFIXの関係(置換 vs 併記)**: §3-2で「置換」方式を採用する
   設計としたが、これはTrial-02の実装を踏襲した技術判断であり、
   「JAPANESE_STYLE_PREFIXの持つ既存の安全な読み上げ規範(長文
   instruction)を完全に捨ててよいか」はFable/Opus L2が改めて論点化
   すべき(Trial-02のASR結果がPASSしていることは実測済みだが、
   本Phase AはTrialのASR結果の中身[品質]までは再検証していない)。
4. **E2とStandard slower指示の重畳**: `_role_style_slower()`は既に
   Production実装済み(§2(a))で、E0→E2の値変更だけでは連結ロジックに
   触れないため技術的リスクは低いが、E2文言("not dramatic"等の
   感情表現追加)と6%減速post-processの組み合わせが聴感上不自然に
   ならないかはPhase Bの試聴確認が必要。
5. **Master Store側のstyle version混線**: §2(d)で確認したとおり
   可変segmentはStore対象外のため技術的な混線リスクは無いが、将来
   誰かが可変segmentをStore対象に含めようとした場合に備え、Phase Bの
   コードコメントで「本diffの対象segmentはStore対象外」であることを
   明記しておくことを推奨する。
6. **テスト更新の正当性**: `FAMILY_X_ROLE_STYLE_EN`のE0→E2リテラル
   assertion更新は、値の中身が変わるだけで構造(辞書のkey集合・型)は
   不変なので「テストの意図を弱める」類の変更ではない(旧E0値を検証する
   意味がなくなったための正当な更新)。Opus L2レビュー時に diff上で
   E0→E2の変更点のみであることを示せるようにする。
7. **JA J3のbackendゲート論点(§3-2末尾で既出)**: `speech_metadata_
   flash_lite`限定にするか、既定backend(`structured_separation`)にも
   拡張するかはSTOP候補(ユーザー/Fable判断が必要、本Phase Aでは判断
   しない)。

---

## 8. 参照した事前指定Read/Grep(実施記録)

- `er044_tts_variable_spoken_role_style_trial_02.py`: 全文中L1-200
  (J3/E2定義・generate_ja/en_pattern_segment)を確認。
- `er033_tts_flash_lite_family_x_styles_01.py`: 全文(82行)確認。
- `er019_family_x_audio_production_runner_01.py`: L460-860(b1/a2両
  segments関数)確認。
- `er003_b1_p9a_audio.py`: L195-286(`generate_narration_snippet`)確認。
- `er003_v1_n3_01_tts_generate.py`: L400-660(`_generate_a2_japanese_
  minimal_instruction`/`generate_a2_japanese_with_fallback`/
  `generate_a2_japanese_with_reading_safety`)確認。
- `er003_v1_repro01_main_generate.py`: L190-410、L740-780
  (`generate_narration_snippet_verified_strict`/Key Phrase呼び出し)確認。
- `er006_master_audio_store_01.py`: L1-90確認。
- `er006_audio_cost_pilot_02_shared_narration.py`: shell style解決関数
  周辺(L88-149)確認。
- `CURRENT_SPEC.md`: Grep該当行(L1474, L1490-1558)確認。
- `OPEN_ITEMS.md`: OPEN-201(L383)・OPEN-229(L412)確認。
- Trial設計書`docs/pm/design_tts_variable_spoken_role_style_trial_02.md`
  §2/§4: 本Phase Aでは時間配分の都合上、er044本体のコード読解を優先し
  設計書側の§2/§4は個別には未読了(er044本体で同等の情報[J3/E2の値・
  置換方式・JA_SEGMENTS範囲]を直接確認できたため。Phase Bで必要になれば
  追加で読む)。
