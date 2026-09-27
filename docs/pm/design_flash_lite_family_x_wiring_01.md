# Flash-Lite Family X Production配線設計書(Phase 0)

管理ID: `TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01`
性質: **設計のみ**。¥0、API呼び出し0件、Production code変更0件、SDK更新0件。
本書の実装は次Phase(下記§k参照)。

前提: Gemini 3.8 Flash-Lite TTS(`gemini-3.8-flash-lite-tts`、
`speech_metadata`方式)は2026-09-27にユーザーが`APPROVED_FOR_PRODUCTION`
(Family X先行段階導入)を正式決定した(`CURRENT_SPEC.md`「Gemini 3.8
Flash-Lite TTS」行、`DECISION_LOG.md`本管理ID冒頭エントリ参照)。
`PRODUCTION_WIRED`ではない。

---

## (a) Family X初回pathの実関数チェーンと置換点

### a-1 呼び出しチェーン(read-only確認、行番号は確認時点)

`er019_family_x_audio_production_runner_01.py`が実際に呼ぶ低レベル生成
関数(Family X B1B/A2共通):

| Role(既存plan_role、`er019_family_x_audio_plan_01.FAMILY_X_B1_SEGMENT_
ORDER`/`FAMILY_X_A2_SEGMENT_ORDER`で定義済み) | Voice | 呼び出し元(er019、行) | 実際のTTS関数 | 内部が最終的に呼ぶ低レベルcall_fn生成 |
|---|---|---|---|---|
| TOPIC_INTRO(B1) | Charon | `generate_family_x_b1_segments()` L410-420 | `voice01.generate_charon_english()` | `er003_b1_p9a_audio._make_english_call_fn()`→`er002_gemini_client.make_tts_call_fn("Charon")` |
| PREVIEW/COMMENT(B1) | Charon | 同L423-434 | `voice01.generate_charon_english(style_prefix_override=n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM)` | 同上 |
| FULL_STORY(part1、B1) / IN_ONE_LINE(B1) | Aoede | L437-453 | `news_tail_fix.generate_news_narration_wide_margin()` | 内部で`p9a`系Aoede call_fn(要追加確認、既存Production未編集方針のため本Phaseでは関数シグネチャのみ確認、内部実装の行特定は次Phaseで実施) |
| HEADING_READOUT(part2/3見出し、B1) | Aoede | L460-471 | `point_headings.generate()` | 同上 |
| FULL_STORY(part2/3本文、B1) | Aoede | L473-484 | `news_tail_fix.generate_news_narration_wide_margin()` | 同上 |
| TOPIC_INTRO(A2、英語) | Aoede(単一Voice) | `generate_family_x_a2_segments()` L547-554 | `crosslevel_common.generate_english_segment_with_fallback()` | `er003_v1_crosslevel_audio_02_common.py` L60〜、標準経路`generate_narration_snippet_verified_strict`→`repro01`系→Aoede call_fn |
| PREVIEW/COMMENT・japanese_title・KP meaning(A2、日本語) | Aoede/Charon(要素により異なる) | L557-570 | `n3_tts.generate_a2_japanese_with_reading_safety()` | `er003_v1_n3_01_tts_generate.py` L520〜 → `generate_a2_japanese_with_fallback()` L419〜 → 標準経路`c.generate_narration_snippet_verified_strict`、fallback`_generate_a2_japanese_minimal_instruction()`(L386、`p4c.build_tts_prompt()`使用) |
| FULL_STORY/HEADING_READOUT(A2、英語、6%減速対象) | Aoede | L572-618 | `n3_tts.generate_a2_segment_with_slowdown(style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER)` | L196〜、内部で`c.generate_english_segment_with_fallback()`→6% time-stretch post-process(`apply_a2_slowdown_postprocess`) |
| Key Phrase(英語Component/日本語gloss) | 共有 | `_generate_key_phrase_segments_b1/a2()` | `shared_narration.ensure_key_phrase_english_component()`/`n3_tts.generate_charon_japanese_with_reading_safety()`/`generate_a2_japanese_with_reading_safety()` | Master Audio Store経由(§e参照) |

### a-2 実際のAPI呼び出し構築(現行、共通の単一choke point)

`er002_gemini_client.py`(英語Charon等の主経路):

```python
def make_tts_call_fn(voice_name, client=None):
    speech_config = build_speech_config(voice_name)  # SpeechConfig(voice_config=...)
    def tts_call_fn(prompt: str) -> bytes:
        response = client.models.generate_content(
            model=common.MODEL_NAME,                 # "gemini-2.5-pro-preview-tts"
            contents=prompt,                          # ← build_tts_prompt()で組んだ単一文字列
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config,
                http_options=types.HttpOptions(timeout=TTS_TIMEOUT_MS)),
        )
        ...
    return tts_call_fn
```

`prompt`は`er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)`
(Structured Separation、`=== STYLE INSTRUCTIONS ===`/`=== TEXT TO SPEAK
===`の単一文字列)で組み立てられる。日本語側(`p7a.make_tts_call_fn_for_
model()`)も同型(model名のみ`JAPANESE_MODEL_NAME`="gemini-3.1-flash-tts-
preview")。

Trial実装(`er022_..._stage3.py` L311-339)の呼び出し形状:

```python
def tts_call_fn(text: str, style: str) -> bytes:
    parts_kwargs = {"text": text}
    if style:
        parts_kwargs["speech_metadata"] = types.SpeechMetadata(style=style)
    content = types.Content(parts=[types.Part(**parts_kwargs)], role="user")
    response = client.models.generate_content(
        model=model_name,                              # "gemini-3.8-flash-lite-tts"
        contents=content,                               # ← 構造化Part(text単体+speech_metadata)
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(voice_config=...)),
    )
```

### a-3 置換点(結論)

置換が必要なのは「`prompt`という単一文字列を組み立てて渡す」層
(`build_tts_prompt()`呼び出し+`contents=prompt`)であり、それより上位
(retry回数管理・ASR検証・Human Review Lock・pronunciation resolver・
A2 slowdown post-process・cost logger)は**一切変更不要**(`text`/
`style_prefix`という同じ2つの入力値をそのまま使い、渡し方だけを変える
設計のため)。

**重大な設計制約(本Phaseで新規に発見、実装前に必ず解決が必要)**:
`generate_charon_english`/`generate_english_segment_with_fallback`/
`generate_a2_japanese_with_fallback`/`generate_charon_japanese`は、
Family Xだけでなく**Family A/B/C(legacy)からも呼ばれる共有関数**
である。これらの関数内部で無条件にspeech_metadata方式・Flash-Liteへ
置き換えると、ユーザー決定(「Family A/B/Cは新規配線対象外」)に反して
legacy Familyの挙動まで変わってしまう。したがって、これらの関数へ
**新しいoptイン引数(例: `tts_backend: str = "structured_separation"`、
既定値は現行のまま無変更)を追加し、Family X runnerだけが明示的に
`tts_backend="speech_metadata_flash_lite"`を渡す**設計にする(既存の
`enable_pronunciation_resolver=True`をFamily X runnerのみが渡す、という
既に確立済みのパターン[`er019...` L420/L433/L452/L483]と同型)。関数内部
は`tts_backend`の値に応じて、(1)`build_tts_prompt()`+`contents=prompt`+
`model=ENGLISH_MODEL_NAME/JAPANESE_MODEL_NAME`(既定・無変更)、
(2)`types.Content(parts=[types.Part(text=text, speech_metadata=...)])`+
`model=FLASH_LITE_MODEL_NAME`(Family X opt-in)、のいずれかを選ぶ分岐を
`p9a._make_english_call_fn()`/`p7a.make_tts_call_fn_for_model()`相当の
call_fn生成層に追加する。

---

## (b) retry/fallback/regenerationが同一関数を通ることの確認

- **retry(標準2回+fallback1回、TOTAL3回上限)**: 全て`generate_charon_
  english`/`generate_english_segment_with_fallback`/`generate_a2_
  japanese_with_fallback`/`generate_charon_japanese`の内部ループが
  `call_fn`を複数回呼ぶ形で実装されている(`er011_human_review_lock_01.
  PRODUCTION_MAX_TTS_ATTEMPTS`/`PRODUCTION_STANDARD_TTS_ATTEMPTS`を
  参照)。§(a-3)のopt-in設計であれば、fallback attempt(minimal
  instruction経路含む)も同じ`tts_backend`分岐を通るため、**retry/
  fallbackとも同一実装経由になる**(確認済み、追加の配線漏れなし)。
- **regeneration(Human Review Lock `approve_regenerate()`経由)**:
  `er011_human_review_lock_01.approve_regenerate()`(L370)はLock解除後、
  呼び出し元(`er019...`の`_generate_or_reuse()`経由で同じ`generate_fn`)
  を再度呼ぶ設計であり、**新規の別経路を持たない**(既存の`generate_
  charon_english`等をもう一度呼ぶだけ)。したがって(a-3)のopt-in引数が
  一度Family X runner側で設定されていれば、regeneration時も自動的に
  同じ`tts_backend`を使う(regeneration専用の別実装を新設する必要は
  ない)。
- **通らない経路の有無**: `_generate_a2_japanese_minimal_instruction()`
  (L386、fallback専用ヘルパー)は`p4c.build_tts_prompt()`を直接呼んで
  おり、上記4関数のいずれとも異なる独立コードパスである。Family Xの
  A2日本語segment(preview/comment/japanese_title等)はこの経路を通る
  ため、**(a-3)のopt-in分岐をこのヘルパーにも個別に追加する必要がある**
  (見落としやすい箇所、実装時に必ず対応)。

---

## (c) Pronunciation/Reading Resolverとの統合設計

### c-1 英語(style prefixへのhint注入)

現行: `er006_pronunciation_tts_injection_01.augment_style_prefix_with_
pronunciation(style_prefix, text)`が、Ledger登録済み固有名詞があれば
`style_prefix`の末尾へ発音hintを追記して返す(`text`自体は一切変更
しない、`er006_pronunciation_tts_injection_01_test.py::test_spoken_
text_never_modified`で確認済み)。呼び出し元は`build_tts_prompt(text,
augmented_prefix)`へそのまま渡している(`er006_pronunciation_ab_01_
run.py` L68-70が参考実装、Family X本経路は`er025_entity_pronunciation_
resolver_core_01.py`経由で同関数を呼ぶ)。

**speech_metadata方式との整合(矛盾しない、根拠引用)**: Trial§0/§14が
明記する原則は「本文(text)はverbatim、styleは話し方の指示であり読み
上げ対象ではない」。`augment_style_prefix_with_pronunciation()`が返す
拡張済み`style_prefix`はまさに「話し方の指示」であり、`text`(spoken
content)には一切触れない設計のため、**そのまま`speech_metadata.style`
フィールドへ渡せば足りる**(`build_tts_prompt()`のSTYLE INSTRUCTIONS
セクションへ埋め込む代わりに、構造化フィールドへ渡すだけ)。むしろ
speech_metadata方式は「styleは発話されない」ことをAPI構造レベルで保証
するため、Structured Separationのdelimiter方式より矛盾が少ない
(delimiter方式はモデルがdelimiterを誤読するリスクの回避策だった
[ER-005-AUDIO-INSTRUCTION-SEPARATION-01]。詳細はTrial REPORT§0)。
**推奨案**: 既存`augment_style_prefix_with_pronunciation()`の戻り値を
そのまま`speech_metadata.style`へ渡す(新規ロジック不要、既存関数の
呼び出し先を変えるだけ)。

### c-2 日本語(reading resolver、text自体への置換)

現行: 日本語側の発音解決は英語側と異なり、`style_prefix`ではなく**`text`
自体の書き換え**(`safety.to_tts_safe_japanese_fraction_reading()`、
`pron_resolver_core.resolve_unknown_ja_tokens()`が返す`reading_
dictionary`を使った表記置換等)+ASR側`expected_readings`辞書として
`classify_ja_asr_match()`へ渡す設計である(`er003_v1_n3_01_tts_
generate.py` L354-370/L572-589)。これはspeech_metadata方式の`style`
フィールドとは無関係な層(`text`そのもの)であるため、**speech_metadata
方式への移行によるJA側の追加設計・変更は不要**(現状のまま流用可能)。

### c-3 結論

矛盾は無い(英語: style_prefixをそのままspeech_metadata.styleへ渡す。
日本語: 無変更)。**USER_DECISION候補ではなく技術判断として上記を推奨**。

---

## (d) 6-role style定数の定数化位置(Dangling Reference Check)

Trial(Stage3)が新規実装した6-role分類は、実は**既存Production概念と
一致する**ことを確認した:`er019_family_x_audio_plan_01.
FAMILY_X_B1_SEGMENT_ORDER`/`FAMILY_X_A2_SEGMENT_ORDER`のplan_role文字列
(`"TOPIC_INTRO"`/`"PREVIEW"`/`"COMMENT"`/`"FULL_STORY"`/
`"HEADING_READOUT"`/`"IN_ONE_LINE"`)は、既に`er020_tts_retry_local_
rewrite_01.resolve_narrative_role()`や`er006_preprod_hardening_01_
validation.classify_asr_match(segment_id=...)`のrole gatingで実際に
Production参照されている既存の役割分類である(Trialが独自に発明した
分類ではなく、既存分類にstyle文字列を対応させただけ)。

**推奨案**: 新規モジュール`er019_family_x_flash_lite_style_01.py`(仮称)
を新設し、`FAMILY_X_ROLE_STYLE = {"TOPIC_INTRO": "...", "PREVIEW": "...",
"COMMENT": "...", "FULL_STORY": "...", "HEADING_READOUT": "...",
"IN_ONE_LINE": "..."}`という辞書定数として、Trial実測済みの最小style
文字列(Stage3、REPORT§22.3)をそのまま格納する。既存`ENGLISH_STYLE_
PREFIX`/`B1_PREVIEW_STYLE_PREFIX_CALM`/`A2_ENGLISH_STYLE_PREFIX_SLOWER`
(Structured Separation方式専用、`p9a.py`/`n3_tts.py`)とは**別ファイル・
別定数名**で管理し、(a-3)のopt-in分岐で`tts_backend=="speech_metadata_
flash_lite"`の場合のみこの辞書を参照する。Family A/B/C(legacy)の
呼び出し元コードは、この新モジュールを一切importしない(Dangling
Reference Check: 新モジュールは呼ばれない限り何の副作用も持たない
定数辞書のみで構成し、Production共通コードのimport文へ紛れ込ませない)。

---

## (e) voice指定・A2 6% slowdown・ASR validation・cost logger/telemetry

- **voice指定**: 既存Voice名(Charon/Aoede/Erinome)をそのまま使用
  (Trial確認済み、モデル間で共通動作)。追加作業なし。
- **A2 6% slowdown post-process**: `apply_a2_slowdown_postprocess()`
  (`er003_v1_n3_01_tts_generate.py` L116)は「TTS生成→time-stretch→ASR
  再検証」という後段処理であり、TTS呼び出し自体の構築方式
  (Structured Separation/speech_metadata)とは独立している。**推奨案**:
  post-process自体は変更せず、まず新モデルの素の出力へそのまま適用し、
  B/A duration比(Trial実測: pace指示なしでもB側79-85%)を踏まえて
  「6%減速のまま適用するか、減速率を再調整するか」を**実測後に判断する**
  (Trial範囲はFamily X B1BのみでA2 6% slowdown対象segmentの実測が無い
  ため、本Phaseでは判断材料が無い。次PhaseでA2記事1本の実測が必要)。
- **ASR validation**: `en_validator.classify_asr_match()`/`ja_secondary.
  evaluate_attempt_ja_with_cascade()`等の既存Production関数をそのまま
  流用(Trialで結果整合性を確認済み、`docs/pm/flash_lite_production_
  adoption_packet_01.md` §E-2)。追加作業なし。
- **cost logger/telemetry**: `cl.segment_context(segment_id)`(`er005_
  cost_logger.py`)は既にFamily X runner全経路で使われており、call_fn
  差し替え後も同じcontext managerの中でTTS呼び出しが発生する限り、
  既存の`raw_usage_log.jsonl`へ自動的に記録される(Trial実装が独自の
  ローカルcost trackingを持っていたのは、Trial scriptがcost_logger.
  install()を呼ぶ独立実行だったためであり、Production配線後は自動的に
  共有storeへ記録される。追加の配線コード不要)。`pricing_snapshot.
  json`には`gemini-3.8-flash-lite-tts`のStandard input/output単価が
  既に登録済み(2026-09-27取得、`er005_output/cost_baseline_01/pricing_
  snapshot.json`)。Batch Mode単価も登録済みだが、本Phaseの対象は
  Standard呼び出しのみ(Batch移行は別スコープ、`OPEN-50`参照)。

---

## (f) SDK 2.25.0導入計画

- **現状3系統**: Production `.venv`(google-genai 2.11.0、`requirements
  *.txt`にPin無し、pip freezeで手動管理と推定)/`.venv-ci`
  (`requirements-ci.txt`、2.14.0、テスト専用で本番コード全体の依存を
  代表しない)/`.venv_trial_genai225`(2.25.0、Trial専用)。
- **導入手順案**: (1) Production `.venv`を汚さないまま、まず`.venv`の
  複製(例: `.venv_flash_lite_staging`)を作り2.25.0を導入、(2)`er003_
  test_*`/`er002_test_common`等TTS関連unit test(Trialが確認済みの9
  ファイル)をこの複製venvで実行、(3)`run_project_regression.py`の
  フル回帰(collected 3300+件規模)をこの複製venvで実行、(4)結果が既知
  failure(既存6件)と一致することを確認できた場合のみ、Production
  `.venv`本体への導入に進む(複製venvが不要になった時点で削除、
  Production `.venv`を直接2.25.0へ書き換えるのは最終ステップのみ)。
- **他Gemini利用箇所のcompatibility確認**(`docs/pm/flash_lite_
  production_adoption_packet_01.md` §D-3の一覧、本Phaseでは個別コード
  レビュー未実施): `er002_gemini_client.py`(最優先、影響範囲最大)、
  `er003_b1_p7a_audio.py`、`er006_batch_tts_wiring_01.py`(Batch Mode)、
  `er006_model_routing_contract_01.py`は型定義依存なしのため影響小、
  他は次Phaseで個別確認。
- **rollback手順**: `pip install google-genai==2.11.0`で即座に戻せる
  (Trialで`pip check`依存衝突なし確認済み)。加えて、(a-3)のopt-in設計
  により、Family X runner側の呼び出しフラグ(`tts_backend`引数)を
  `"structured_separation"`へ戻すだけで、SDKロールバックとは独立に
  Flash-Lite経路だけを即座に無効化できる(2段階のrollback手段を持つ
  設計、SDK起因の問題かprompt構造起因の問題かを切り分けやすい)。

---

## (g) model routing

- **重大な発見(read-only確認)**: `er006_model_routing_contract_01.
  require_provider("TTS", TTS_MODEL)`は、**現状どのProduction call
  siteからも呼ばれていない**(パッケージ§D-3のGrep結果、および本Phase
  でのGrep再確認[`require_provider\(.TTS.`にマッチ0件]で確定)。
  `ASR_PROVIDER`と同様、TTS routing contractは定義されているが未配線
  である(コード上のfail-closed強制は実際には効いていない、モデル名は
  各call_fn生成関数[`p9a.ENGLISH_MODEL_NAME`/`JAPANESE_MODEL_NAME`]が
  それぞれ個別に保持するハードコード定数)。
- **登録方法(推奨案)**: `PROCESS_MODEL_MAP`/`PROCESS_PROVIDER_MAP`の
  汎用単一値契約(process→1モデル)は、Family別に異なるモデルを許容する
  設計になっていない(現状Structured Separation側もこの契約に未加入
  のため、Flash-Lite追加のために契約の構造自体を変える必要はない)。
  代わりに、(d)の新モジュール内に`FAMILY_X_FLASH_LITE_MODEL_NAME =
  "gemini-3.8-flash-lite-tts"`という専用定数を持ち、call_fn生成時に
  actual model_idをresultへ明示的に記録する(既存`generate_charon_
  english`等が返す`result["model"]`フィールド[`p9a.py` L249確認済み]
  と同じパターンを踏襲、新規スキーマ不要)。
- **runtime evidence取得方法**: 生成結果dict(`tts_generation_results.
  json`)の`model`フィールドに実際に使われたmodel_id文字列がそのまま
  記録される(既存の仕組みをそのまま使うだけ、追加ログ不要)。

---

## (h) regression fixture化(Act One/Two/Three digit読み)

Trial Stage3で実測した唯一のretryケース(canonical本文の章見出し表現
"Act One/Two/Three"をFlash-Liteがattempt1でdigit読みし、既存ASR数値
検証が正しくSTOPさせた事例)を、既存の英語ASR数値検証テストスイート
(`er006_preprod_hardening_01_validation`関連test、または`er003_test_
v1_n3_01_tts_generate.py`)へ**text-onlyのregression fixture**として
追加する案。**注意**: 現行のASR数値検証テストは基本的に「canonical
text」対「ASR書き起こしtext」のペア比較(音声合成を伴わない静的
fixture)であるため、TTS音声を実際に生成せずとも「digit読みされた
ASR文字列を人工的に用意し、`classify_asr_match`がTRUE_CONTENT_MISMATCH
と正しく判定する」ことをfixture化できる(追加API呼び出し不要、¥0)。
実装は次Phase。

---

## (i) 公平な1回完成cost比較の測定計画

`docs/pm/flash_lite_production_adoption_packet_01.md` §B-5で、既存
Hormuz B1B実測(¥87.7、36 attempt)は複数run分のretry履歴混入の可能性
があり「1回完成コスト」として厳密ではないことが判明済み。**推奨案**:
次Phaseで、Family X新規記事(1本)を(1)現行モデル(Structured
Separation、gemini-2.5-pro-preview-tts)で最初から最後まで1回通しで
完成させ、(2)同じ記事本文をFlash-Lite(speech_metadata方式)で1回通しで
完成させる、という**同一記事・両モデルでの新規1回完成コスト実測**を
行う(既存artifactからの遡及抽出ではなく、新規実測でのみ公平比較が
可能。実施はPhase分割案[§k]のPhase 2以降、記事1本分の実費用が発生)。

---

## (j) rate limit/concurrency確認計画

Gemini公式rate-limitページがJS動的レンダリングのため静的取得不可
(Trial既知の制約)。**推奨案**: (1) Production側の記事生成頻度(1日
あたりのFamily X記事数、現状の実運用ペースをPMが把握している数値から
確認)を基準に、実際に想定される最大同時TTS呼び出し数を定義する、
(2) その数を超えない範囲で、Flash-Lite導入直後の最初の数記事は
意図的に逐次実行(並列化しない)にとどめ、429エラー等のrate limit
兆候が出ないことを運用しながら確認する、(3) 有料の負荷試験(意図的な
高頻度並列呼び出し)は別途ユーザー承認を得てから実施する(本Phaseでは
提案のみ、実施しない)。

---

## (k) 実装Phase分割案と費用見積・Guardrail

| Phase | 内容 | 費用目安 | Guardrail |
|---|---|---|---|
| Phase 1 | (a-3)opt-in`tts_backend`引数の追加(4関数+`_generate_a2_japanese_minimal_instruction`ヘルパー)、(d)新モジュール(role別style定数)新設、(g)model_id記録。**API呼び出しなし**(コード追加のみ、既定値は現行のまま無変更なのでオフラインunit testで検証可能) | ¥0 | 既存unit test全件PASS必須、既定値(Structured Separation)の既存呼び出しに一切影響しないことをオフラインで確認してからPhase 2へ進む |
| Phase 2 | Family X 1記事(新規)を(a-3)の新backendで実際にend-to-endTTS生成(§i公平cost比較を兼ねる)、SDK 2.25.0を複製venv(§f)へ導入して回帰実行 | 記事1本分の実TTS/ASR費用(Trial実測¥8.72/12segment相当が目安、記事全体では追加segment[Key Phrase等]を含めやや増額想定) | 1回のみ、記事全体を止めるBLOCKERが出た場合は都度Fable報告、STOP基準は既存Human Review Lock/ASR Gateをそのまま適用(独自の緩和なし) |
| Phase 3 | SDK 2.25.0のProduction `.venv`本体への導入、フル回帰(3300+件規模)、rate limit確認(§j、逐次運用のまま数記事分観測) | ¥0(回帰自体はAPI呼び出しを伴わない既存test中心)+数記事分の通常運用費用 | フル回帰で新規failureが既知6件を超えたら即STOP、rollback(§f)を実行 |
| Phase 4 | Mandatory Opus L2レビュー(Productionモデル/SDK切替)、Gate 3チェックリスト全項目確認、Fable判定で`PRODUCTION_WIRED`宣言 | Opus L2 1回分 | BLOCKER検出時はSTOP、Sonnet修正→再Opus確認のループ上限(既存ガバナンス、最大3回)を適用 |

---

## USER_DECISION候補(本Phaseで新たに判明した、新規仕様判断が必要な論点)

1. **A2 6% slowdown post-processの適用方針**(§e): 「そのまま6%を適用し
   B/A比を実測してから判断する」という素案でよいか、それとも「A2記事
   実測が揃うまでFlash-LiteをA2へは適用しない(Family X B1B先行のみで
   十分、A2は別Phase)」という、より保守的な範囲限定にするか。
   ※現状のユーザー決定は「Family Xから段階導入」であり、Family X内に
   A2/B1B両方が含まれるため、A2 6% slowdown対象segmentの扱いは追加の
   確認が必要。
2. **公平な1回完成cost比較(§i)の実施タイミング**: 新規記事を使った
   実測(有料)をPhase 2の一部として今回のuser承認済み範囲内で実施して
   よいか、それとも実測実施自体を都度個別承認とするか。
3. **rate limit確認(§j)の運用**: 「意図的な逐次運用での様子見」を
   Phase 3の一部として自動継続してよいか、それとも記事ごとに個別
   報告を求めるか。

(c)(e)の残りの論点は、上記本文中に「技術判断として推奨案を明記」した
とおり、新規ユーザー判断は不要と考える(既存原則との矛盾なし)。
