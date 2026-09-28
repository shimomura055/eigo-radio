# design_tts_fixed_shell_master_champion_trial_01.md

管理ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01(Trial、Production実装なし)

## 1. 既存Master Audio Store仕様の確認(§1)

### 1-1. Store構造(`er006_master_audio_store_01.py`、読み取りのみ・無変更)
`MasterAudioKey`のフィールドと、cache一致判定に使う`EQUALITY_FIELDS`:

| フィールド | level依存/非依存 | 備考 |
|---|---|---|
| `language` | 非依存(値そのものがkey) | en/ja |
| `level` | **level非依存として明示的に`None`固定**(共有narration用) | `Optional[str]`、`None`=B1/A2共通 |
| `speaker_voice` | 非依存 | Charon固定(対象10 phraseすべて) |
| `tts_model_id` | 非依存(値がkey) | `gemini-2.5-pro-preview-tts`(structured_separation EN)/`gemini-3.1-flash-tts-preview`(structured_separation JA)/`gemini-3.8-flash-lite-tts`(flash_lite EN/JA共通) |
| `style_instruction_id` | 非依存(値がkey) | `charon_english_fixed_shell`/`charon_japanese_fixed_shell`(Production)、本Trialは`trial_ch1_role_style`を新設 |
| `style_instruction_version` | 非依存(値がkey) | Production: `v1`(既定)/`v2_flash_lite_short_style`(EN flash-lite shell)。本Trialは`trial_ch1_role_style_v1`を新設 |
| `instruction_path` | 非依存(既定"primary"、対象10 phraseすべて未変更) | |
| `canonical_text_hash`(text由来) | 非依存(textが変われば自動的に別key) | sha256[:16] |
| `audio_processing_version` | 非依存(既定"v1") | |
| `sample_rate`/`channels` | 非依存(既定24000/1) | |

`master_audio_id()`は上記`EQUALITY_FIELDS`のみのsha256[:24]。**style_instruction_id/versionが
異なれば別entryになる**(実際のstyle文字列の中身そのものはkeyに含まれないため、内容を変える場合は
必ずid/versionも変える運用規約、既存コードコメントでも明記されている「BL-1」「KEY_PHRASE_TRIM_
POLICY_VERSION」の教訓と同じ)。本Trialでも新Champion候補(Role style)を`trial_ch1_role_style`/
`trial_ch1_role_style_v1`という専用id/versionで区別し、Production既存の`charon_*_fixed_shell`/
`v1`/`v2_flash_lite_short_style`と衝突しない設計にする。

`get_or_generate(key, out_path, generate_fn)`は`STORE_DIR`/`AUDIO_DIR`/`MANIFEST_PATH`/
`TELEMETRY_PATH`をモジュールレベル定数として保持し、呼び出し時に動的解決される(TTS-ALL-SPOKEN-
ROLE-STYLE-TRIAL-01設計書§1-5と同じ既存事実、本Trialでも同じ既承認パターンでTrial Store隔離に使う、
§1-2参照)。`asr_verified=True`のentryのみが`qa_evidence`へ保存され、reuse時も復元される。

### 1-2. Store隔離方式(既承認パターンの踏襲)
`er006_master_audio_store_01.py`自体は無変更。実行時に`store.STORE_DIR`等4定数を本Trial専用
`er040_output/tts_fixed_shell_master_champion_trial_01/master_store/`へ上書きし、終了後に復元する
(`trial_master_audio_store()`context manager、TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01の
`trial_master_audio_store()`と同一パターン)。Production Store
(`er006_output/master_audio_store_01/`)は一切書き込まない。

### 1-3. 新Role Style導入後の誤reuse防止の確認
Production側は既に`v1`(既定/2.5 Pro系構成)と`v2_flash_lite_short_style`(Flash-Lite shell shortstyle、
修正3回目で全9 EN phrase合格)を`style_instruction_version`で区別済み(実manifest確認、後述§1-4)。
本TrialのCandidate Bは、さらに別の`trial_ch1_role_style_v1`を使うため、(a) Production既存2種と、
(b) 本Trialの新style候補、が three-way で衝突しないことを`er040_..._test_01.py::
test_master_audio_key_distinguishes_style_versions()`で機械的に検証する(3つの`MasterAudioKey`の
`master_audio_id()`が互いに異なることをassertする、実API呼び出し無し)。

### 1-4. 既存Production manifest実測(read-only確認、`er006_output/master_audio_store_01/
manifest.json`)
対象10 phrase(EN 9 + JA 1)について、`canonical_text_hash`を突合した結果:

| phrase | v1(2.5 Pro系/structured_separation) | v1 flash-lite(古style) | v2_flash_lite_short_style(現行Production Flash-Lite Baseline) |
|---|---|---|---|
| welcome | 登録あり(`asr_verified`未記録) | 登録あり・`asr_verified=True` | 登録あり・`asr_verified=True` |
| preview_intro | 同上 | 同上 | 同上 |
| key_phrases_intro | 同上 | 同上 | 同上 |
| full_story_intro | 同上 | 同上 | 同上 |
| num_one | 同上 | 同上 | 同上 |
| num_two | 同上 | 同上 | **登録あり・`asr_verified=True`**(修正3回目で解消済み) |
| num_three | 同上 | 同上 | **登録あり・`asr_verified=True`**(修正3回目で解消済み) |
| num_four | 同上 | 同上 | 同上 |
| num_five | 同上 | 同上 | 同上 |
| point_explanation(JA) | 登録あり(`asr_verified`未記録) | 登録あり・`asr_verified=True` | (JA側は現状override機構が無いため`v2_...`は存在せず、`v1` flash-liteのみ) |

**重要な既存事実**: num_two/num_threeはProduction現行Baseline
(`v2_flash_lite_short_style`=FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]="natural, clear, conversational")
では既に`asr_verified=True`。一方、TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(Task B)が**別のstyle文言**
(NUMBER_LABEL="brief, clear, neutral"、Flash-Lite・Charon・B1B経路)で同じnum_two/num_threeを
生成したところ、3 attempt全てCJK文字への言語ドリフト(`'Tu'`→`'二'`→`'二'`等)でHuman Review Lockへ
到達した(`OPEN-222`、`er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/audit/
review_lock_state.json`)。**つまり同じFlash-Liteモデル・同じ極短単語でも、styleの文言次第で成否が
分かれる可能性がある**(Task Bの考察では「A2側は同テキストで成功しておりstyle文言そのものの問題
ではなく一般的なFlash-Lite短文脈限界の可能性」としているが、B1B/A2差か style差かは未分離)。

### 1-5. 本Trialの対応方針(num_two/num_three固有)
無意味な再生成禁止(delegation)を踏まえ、num_two/num_threeについては:
- **Candidate A/Baseline**: Production既存`v2_flash_lite_short_style`master(既にasr_verified=True)
  をそのまま読み取り専用で再利用する(新規TTS/ASR呼び出しなし)。
- **Candidate B(Role style)**: 既にTask Bが同一style文言・同一Flash-Liteモデル・同一voice(Charon)
  で検証済みかつ失敗(Human Review Lock)しているため、**本Trialでは再生成しない**(同じ失敗を
  再現するだけのAPI消費を避ける、delegation「無意味な大量生成禁止」に従う判断)。既存evidence
  (`er038_output/.../review_lock_state.json`、`OPEN-222`)を比較ページ・REPORTへ引用する。
- **Candidate C(2.5 Pro系/structured_separation)**: 新規に生成する(Flash-Lite自体を使わないため
  言語ドリフト問題の根本回避になりうるかを確認する、genuinely new data point)。

num_one/num_four/num_fiveおよびEN 4 phrase(welcome/preview_intro/key_phrases_intro/
full_story_intro)・JA point_explanationは、既知の失敗が無いためA(reuse)/B(新規)/C(新規)の
3候補を揃える。

## 2. 対象固定segment棚卸し(§2)

`er019_family_x_audio_production_runner_01.py`の`generate_family_x_b1_segments`/
`generate_family_x_a2_segments`は共有narrationを`shared_narration.ensure_all_shared_narration_b1/
a2(narration_dir, tts_backend=tts_backend)`経由で取得しており(l.515/726)、これらの実装
(`ensure_all_shared_narration_b1/a2`)は`FIXED_ENGLISH_TEXTS`(9件)+`FIXED_JAPANESE_TEXTS_A2_ONLY`
(1件)の**計10件**のみを対象としている。Family X runner全体をGrepした限り、これ以外に「全記事共通
かつ文言固定」のTTS呼び出しは見つからなかった(topic_intro/preview/comment等は記事ごとに文言が
変わる可変narrationであり対象外)。

| segment_id | 言語 | 固定文言 | Production既定voice/model | 備考 |
|---|---|---|---|---|
| welcome | EN | "Welcome to English Your Way." | Charon / Flash-Lite(v2_short_style)or 2.5 Pro | PROGRAM_SECTION_INTRO |
| preview_intro | EN | "Here's a quick preview." | 同上 | PROGRAM_SECTION_INTRO |
| key_phrases_intro | EN | "Here are today's key phrases." | 同上 | KEY_PHRASE_INTRO |
| full_story_intro | EN | "Now, the full story." | 同上 | FULL_STORY_INTRO |
| num_one〜five | EN | "One."〜"Five." | 同上 | NUMBER_LABEL |
| point_explanation | JA | "ポイント解説" | Charon / Flash-Lite or 3.1-flash(structured) | NUMBER_LABEL(JA)、A2のみ |

## 3. Candidate設計(§3)

Role style文言は`docs/pm/design_tts_all_spoken_role_style_trial_01.md`§3のTrial Role style表を
**そのまま流用**(新規文言は考案しない、ユーザー承認済みFallback[0]と同じ「既存Trial実測済み文言を
使う」方針)。

| Candidate | 定義 | 生成方法 | 対象10 phrase中の適用範囲 |
|---|---|---|---|
| A(Baseline) | Production現行既存Master(既にasr_verified=True) | **新規TTS/ASR呼び出しなし**。Production manifest(read-only)から該当`master_audio_id`のwavをそのままコピーし比較ページに掲載 | 10/10(全件、既存masterが存在するため) |
| B(Role style) | Flash-Lite + Task B設計のRole style短文(PROGRAM_SECTION_INTRO/KEY_PHRASE_INTRO/FULL_STORY_INTRO/NUMBER_LABEL) | `voice01.generate_charon_english(style_prefix_override=...)` / JA側は`voice01.p9a.JAPANESE_STYLE_PREFIX`を一時的にRole style短文へ差し替えて`voice01.generate_charon_japanese`を呼ぶ(既存関数に引数が無いため、precedent`er011_final26_runtime_evidence_01.py`と同じモジュール属性モンキーパッチ手法、生成後に必ず復元) | 8/10(num_two/num_threeは§1-5の理由で新規生成せず既存Task B evidenceを引用) |
| C(2.5 Pro系) | `tts_backend="structured_separation"`(既定・既存2.5 Pro/3.1-flash構成、style override無し=Production既定`charon_*_fixed_shell`/`v1`) | `shared_narration.ensure_fixed_english_segment`/`ensure_fixed_japanese_segment`をそのままTrial Store経由で呼ぶ | 10/10(num_two/num_threeも含め全件新規生成、Flash-Lite自体を使わないため言語ドリフト回避の可否を確認する主目的) |

Candidate B/CともにASR検証はProduction既定のcascade(`review_lock.guarded_generate`decorator
経由、EN=Tier1/Tier3 role gating、JA=`ja_secondary.evaluate_attempt_ja_with_cascade`)をそのまま
通す(独自の緩い判定基準を作らない)。

### 3-1. One〜Fiveの統一感評価
候補ごとにOne〜Fiveをセットで生成し、以下を定量比較する:
- duration_seconds(`er002_common.measure_metrics`)のセット内ばらつき(max-min)
- rms_dbfs(音量)のセット内ばらつき
- ASR一致(asr_text==canonical_text、drift有無)
- attempt数(1回で合格したか、retry/fallbackが発生したか)

## 4. 試聴ページ構成(§4)
`user_test/fixed_shell_champion_trial_01/index.html`。phraseごとにBaseline(=Candidate A)/
Candidate B/Candidate Cの音声・model・voice・style・durationを表で提示。One〜Fiveは個別再生に加え、
候補セットごとにOne→Five連結mp3を用意し連続再生比較できるようにする。

## 5. コスト効果概算の算出方法(§5)
Family X 1記事(B1B+A2)あたりの固定phrase呼び出し回数は、`ensure_all_shared_narration_b1`
(9回)+`ensure_all_shared_narration_a2`(9+1=10回、ただしlevel非依存keyのためB1B側で生成済みなら
A2側は追加TTS呼び出し0でreuseされる)。既にMaster Store運用中のため、Champion化そのものによる
追加削減効果は「新テーマ立ち上げ時の初回生成コストの有無」ではなく、**将来Role style更新等で
style_instruction_versionを変える度に、現在は10件×lang分regenerateが必要になる想定コスト**を
基準に概算する(実測値は本体REPORTへ記載)。
