# KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01

**管理ID**: KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01
**Lane**: Lane A / Key Phrase。種別: 隔離Trial(ユーザー承認2026-09-06)。**Production変更なし**(既存Cascade/Validator/ASR routing/TTS呼び出しをすべてread-onlyで再利用し、Trial module内だけで追加の再判定ロジックを実装した)。
**到達Status**: (a) VALIDATED-but-insufficient-alone、(b) VALIDATED、(c) VALIDATED。**いずれもProduction採用は`USER_DECISION_REQUIRED`(自動でProduction採用へは進めない)**。
**コード基準**: 全読み取りは作業ツリー(`git status --porcelain`でHEADと同一、無変更を確認済み)。

---

## 1. 事実確認(既存Production実装の再確認)

`KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01_REPORT.md`で確定した「`new normal`の英語音声はTTSが正しく英語で発話しているが、OpenAI Primary ASR(`gpt-4o-mini-transcribe`、`language="en"`)が「新常態」という漢字表記へ意味変換する」という事実を踏まえ、コードを追って**なぜCascadeが発動しないか**を特定した。

- `er006_preprod_hardening_01_validation.tokenize()`は`normalize_text()`内の`re.sub(r"[^a-z0-9]+", " ", t)`でASCII英数字以外(CJK含む)をすべて空白化するため、ASR出力が「新常態」のような非ASCII文字列のみだと`tokenize()`後は空リストになる。
- `classify_asr_match()`は`canon_tokens=["new","normal"]` vs `asr_tokens=[]`のratioがほぼ0となり、`ratio < tts_failure_threshold(0.4)`の分岐で**`TTS_FAILURE`**に分類される(`TRUE_CONTENT_MISMATCH`でも`ASR_VALIDATION_UNCERTAIN`でもない)。
- `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail()`のCascade発動条件は`is_entity_like_mismatch(cls) or is_homophone_candidate_mismatch(cls)`であり、両関数とも`cls.classification != "ASR_VALIDATION_UNCERTAIN"`なら即`False`を返す。`TTS_FAILURE`はこの条件に該当しないため、**Cascade(Primary#2→Secondary Azure等)は一度も発動しない**。
- 結果として、`new normal`の4attemptはOpenAI Primary ASR単体の判定だけで4回ともblind TTS retryへ回され、Azure Secondaryには一度も到達していない(Root Cause確定)。

---

## 2. 実装(Trial限定、Production非導入)

新規ファイル: `er011_kp_en_asr_false_rejection_cascade_trial_01.py`(root)

- **非ラテン文字主体判定**: ASR出力中のラテン文字(基本ラテン+主要発音区別符号)数とCJK/かな/ハングル文字数を数え、`CJK数/(ラテン数+CJK数) >= 0.5`(両方0ならFalse)を「非ラテン文字主体」と判定。**適用範囲はKey Phrase Component呼び出し(独立した短い英語segment)のASR出力全体**であり、部分文字列やFull Story等の他segment種別には適用しない(このTrialのスコープに合わせた限定)。
- **条件(a)**: 現行の`classify_asr_match()`結果が`should_pass=False`かつ上記の非ラテン文字主体に該当する場合(`TTS_FAILURE`/`TRUE_CONTENT_MISMATCH`いずれも対象、既存Cascadeの`entity_like`/`homophone_candidate`限定条件は変更しない)、既存の`er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list()`(Production Secondary ASR関数そのもの)を1回呼び、その結果を`classify_asr_match()`で再判定する。
- **条件(b)**: OpenAI ASR呼び出し(`client.audio.transcriptions.create`)へ`prompt`引数を追加する専用関数を新設(`routing.transcribe()`自体は無変更)。prompt文言:
  > "The audio is spoken in English. Transcribe it verbatim in English, exactly as spoken, using English spelling. Do not translate it, and do not write it in Japanese, Chinese, or any other language or script."
- **条件(c)**: (b)のprompt付きPrimary結果に対して(a)と同じ非ラテン文字判定+Secondary Cascadeを適用(コスト削減のため、(a)で既にSecondary Azureを呼んでいれば同じ音声への同一呼び出しを再利用)。

---

## 3. テストセット

**陽性(7件、既存資産再利用2件+新規TTS5件、Standard同期TTS)**:
| # | canonical | 音声出所 |
|---|---|---|
| 1 | new normal | 既存保全音声(KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01) |
| 2 | new normal | 新規1回生成 |
| 3 | default | 既存資産(ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINITRIAL-20-R2 attempt1) |
| 4 | work-life balance | 新規1回生成 |
| 5 | remote work | 新規1回生成 |
| 6 | subscription | 新規1回生成 |
| 7 | cashless | 新規1回生成 |

**陰性対照(3件、新規TTS)**:
| # | canonical | 実際の発話 |
|---|---|---|
| i-1 | new normal | 日本語TTSで「新常態」 |
| i-2 | default | 日本語TTSで「デフォルト」 |
| ii | new normal | 英語TTSで別の語「new formal」 |

Production同一のvoice/model/Key Phrase instruction(`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`)・trim margin(`KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS`)を英語音声生成に使用。日本語陰性対照は`generate_narration_snippet()`のja分岐(Production同一のJapanese instruction/model)をそのまま使用。

---

## 4. 結果表(false rejection率・false accept)

| 条件 | 陽性 false rejection率 | 陰性 false accept件数 |
|---|---|---|
| 現行(baseline) | 4/7 = 57.1%(new normal×2、default、cashless) | 0/3 |
| (a) 非ラテン文字判定+Secondary Cascade | 1/7 = 14.3%(cashlessのみ残存) | 0/3 |
| (b) prompt付きPrimary ASR | 0/7 = 0.0% | 0/3 |
| (c) (a)+(b)併用 | 0/7 = 0.0% | 0/3 |

**cashlessの詳細**: Primary ASR raw出力`"Káslis"`はラテン文字のみ(発音区別符号込み)で構成されており、本Trialの非ラテン文字主体判定(CJK文字比率)には該当しないため、条件(a)は不発動のままREJECTが継続する。条件(b)(prompt)は`"Cashless"`へ正しく修正され、条件(c)も(b)がPASSした時点でCascade不要のためPASS。**これは(a)単独では「英語canonicalに対しラテン文字だが誤表記(garbled Latin)」の失敗モードを救えないという、設計上のスコープの限界であり、バグではない**(非ラテン文字検出という定義上の対象外)。

**陰性対照の詳細(false accept 0件の根拠)**:
- i-1「新常態」: baseline ASR「新状態」(TTS_FAILURE)→(a) Secondary Azure `"Xinjio Tai."` → `classify_asr_match("new normal", "Xinjio Tai.")` = TTS_FAILURE(should_pass=False)→REJECT維持。(b) prompt付きPrimary `"心状態"` → 依然非ラテン・TTS_FAILURE→REJECT維持。
- i-2「デフォルト」: baseline ASR「デフォルト」(TTS_FAILURE)→(a) Secondary Azure `"Defaulto."` → `classify_asr_match("default", "Defaulto.")` = TTS_FAILURE(token級ratio≈0、should_pass=False)→REJECT維持。(b) prompt付きPrimary `"デフォルト"`→依然REJECT。
- ii「new formal」: baseline ASR `"new formal"`(TRUE_CONTENT_MISMATCH、内容語差検出)→非ラテン文字でないため(a)不発動→REJECT維持。(b) prompt付きPrimary `"New formal."`→依然TRUE_CONTENT_MISMATCH→REJECT維持。

いずれの条件・いずれの陰性対照でも**false acceptは0件**(必須条件を満たす)。

全raw ASR出力・分類理由の詳細は `er011_output/kp_en_asr_false_rejection_cascade_trial_01/trial_results.json` 参照。試聴用player: `file:///C:/Users/tensh/eigo-radio/er011_output/kp_en_asr_false_rejection_cascade_trial_01/player.html`

---

## 5. 既存機構との非干渉確認

- 数字ゲート・否定ゲート・homophone/entity_like判定・Connected Speech Validator・disfluency QAは、`classify_asr_match()`/`protected_check()`をそのまま呼んでいるだけで一切変更していない。
- 既存Cascade(`evaluate_attempt_with_cascade_detail`)の`entity_like`/`homophone_candidate`限定発動条件そのものは無変更(このTrialは既存条件に「非ラテン文字主体」という**別の**発動条件を追加する候補を試しただけで、既存条件を置き換えたり緩めたりはしていない)。
- retry上限(`KEY_PHRASE_TOTAL_MAX_ATTEMPTS`=4等)・review lock・Human Review Queueはいずれも呼び出していない(本Trialは単発生成+単発ASR再判定のみで、Production retry loop自体を経由しない)。
- Secondary ASR呼び出し(`get_full_text_via_azure_stt_with_phrase_list`)はProduction関数をそのまま呼んでいるため、Cost Loggerへの記録も既存の仕組みと同一形式(`cl.install()`経由)。

---

## 6. 推奨・分類

- **(a) 非ラテン文字判定+既存Cascade拡張**: `VALIDATED-but-insufficient-alone`。安全(false accept 0件)だが、単独では「非ラテン文字ではないが誤表記」の失敗モード(cashless例)を救えない。既存Cascadeへの追加発動条件としては安全に組み込める設計だが、単独案としては不採用推奨。
- **(b) prompt付きPrimary ASR**: `VALIDATED`。本Trialのサンプル(陽性7件)では単独で false rejection率を57.1%→0%に改善し、追加API呼び出しコストがほぼゼロ(既存の1回のPrimary呼び出しに`prompt`引数を足すだけ)。ただし後述のサンプルサイズ・非決定性の限界に注意。
- **(c) (a)+(b)併用**: `VALIDATED`。(b)を主軸に(a)を「(b)でも非ラテン文字が残った場合の追加安全網」として重ねる構成であり、本Trialのサンプルでは(b)だけで全件解決したため(a)は実際には発動しなかったが、構造的には(b)が効かない将来ケースへの多層防御として機能しうる。

**総合推奨(実装しない、ユーザー判断事項)**: (c)(prompt主軸+非ラテン文字Cascade拡張を安全網として併用)を候補として提示する。(a)単独は不採用、(b)単独は最小変更で効果が高いが多層防御の観点では(c)がより保守的。

---

## 7. 既知の限界(正直に記録)

1. **サンプルサイズ**: 陽性7件・陰性3件、各1attemptのみ(new normalのみ2attempt)。OPEN-103の記録では同じ`default`が過去の別Trialで「デフォルト」(日本語)・「默认」(中国語)・「Dieselt」(英語だが誤スペル)と**試行ごとに異なる失敗モード**を示しており、OpenAI ASRの非決定性が既知である。本Trialの「(b)で0%」という結果は今回のattemptに対しては事実だが、繰り返し試行しても常に0%になるとは断定できない。
2. **prompt引数の効果範囲**: OpenAI `gpt-4o-mini-transcribe`の`prompt`引数は公式には「スタイル誘導・文脈ヒント」用途であり、厳密な指示追従を保証する仕様ではない(prompt injection的な強制ではない)。本Trialでは効果が観測されたが、内部メカニズムは未解明(Provider側のブラックボックス)。
3. **cashless系の失敗モード**: ラテン文字だが誤表記("Káslis")という、非ラテン文字判定の対象外の失敗モードが実在することを本Trialではじめて確認した。この種の失敗モードに対する一般的なセーフティネットは(a)の対象外であり、(b)(prompt)または既存のTRUE_CONTENT_MISMATCH経由のblind retryに依存する。
4. **陰性対照3件のみ**: false accept 0件は心強いが、対照群がまだ小さい。

---

## 8. Production採用に必要な変更一覧(実装しない、ユーザー判断事項)

1. `er006_asr_provider_routing_01.py`の`_transcribe_openai_mini()`/`transcribe()`へ、English routeのみ`prompt`引数を追加するかどうか(全English ASR呼び出しに影響するため、Key Phrase限定にするなら新しい呼び出し経路の分岐が必要)。
2. `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail()`の`cascade_eligible`条件へ「非ラテン文字主体」を追加するかどうか、追加する場合の正式な閾値・適用範囲(Key Phrase限定か英語segment全体か)をユーザー承認事項として確定。
3. prompt文言の正式版(本Trialの文言をそのまま採用するか、追加検証するか)をユーザー承認事項として確定。
4. 非決定性を踏まえた追加検証(同一Key Phraseでの複数回attempt比較)の実施要否。
5. DECISION_LOG.md/CURRENT_SPEC.mdへの正式記録(採用が決定した場合のみ)。

---

## 9. UNKNOWN

- OpenAI `gpt-4o-mini-transcribe`が`language="en"`指定でも意味変換した非英語文字列を返す内部メカニズム(Provider側のブラックボックス、特定不能)。
- `prompt`引数の効果が他のKey Phrase・他のTTS take・将来のモデルバージョンでも同程度に安定するか。

---

## 10. cost

`er011_output/kp_en_asr_false_rejection_cascade_trial_01/raw_usage_log.jsonl`実測:
- Gemini TTS: 8回(英語6回`gemini-2.5-pro-preview-tts`+日本語陰性対照2回`gemini-3.1-flash-tts-preview`、いずれもProduction同一モデル・1〜2秒の短い音声、各300〜500トークン程度)。
- OpenAI ASR(`gpt-4o-mini-transcribe`): 20回(baseline 10回+prompt付き10回、いずれも数秒未満の短い音声、入力トークン最大64)。
- Azure Speech STT: 5回(1〜1.5秒の短い音声)。

いずれも既存のKey Phrase Component生成・ASR呼び出しと同水準の単価(数十秒あたり1円未満、短いTTSは1回あたり数円程度)であり、実測トークン数・音声長から合計は**¥50未満と見積もる**(STOP閾値¥500を大きく下回る)。正確な円換算はraw_usage_log.jsonlのtoken/duration実測値を参照。

---

## 11. Production変更なし確認

- `er006_asr_provider_routing_01.py`(`transcribe`/`_transcribe_openai_mini`)、`er006_preprod_hardening_01_validation.py`(`classify_asr_match`等)、`er006_secondary_asr_01.py`(`evaluate_attempt_with_cascade_detail`等)、`er003_v1_repro01_main_generate.py`(`generate_key_phrase_component_verified`等)はいずれも無変更(read-onlyで呼び出しただけ)。
- Prompt文言・retry上限・review lock・Human Review Queueの実装はいずれも変更していない。
- 書き込みは本Report(root)、`er011_kp_en_asr_false_rejection_cascade_trial_01.py`(root、Trial専用新規ファイル)、`er011_output/kp_en_asr_false_rejection_cascade_trial_01/`(新規、既存ディレクトリへの書き込みなし)のみ。
- `docs/pm/ACTIVE_TASK.md`は並行タスク(OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01)が使用中のため触れていない。`docs/pm/RESULT_PACKET.md`のみ本タスク用に更新する。
