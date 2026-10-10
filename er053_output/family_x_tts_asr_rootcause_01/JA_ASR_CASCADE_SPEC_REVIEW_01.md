# JA ASR Cascade 仕様整理 (read-only) JA_ASR_CASCADE_SPEC_REVIEW_01

管理ID: FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_20 (B)。課金API呼び出し・コード/SSOT変更なし。判定の再現はローカルの純粋関数(`classify_ja_asr_match`、Resolver flag OFF)のみ。
対象: META Standard(A2) japanese_title (run: `er019_output/family_x_audio_production_wiring_01/meta__run_regen_01/a2/`)。
原稿: 「AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした」

## 1. 現行仕様とProductionコードの一致、今回の判定経路

呼び出し経路(Production): `er003_v1_repro01_main_generate.py` L361-368(日本語分岐)が `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade()` を呼ぶ。標準経路は2回、不合格なら fallback(minimal)1回、合計 `review_lock.PRODUCTION_MAX_TTS_ATTEMPTS=3`(`er011_human_review_lock_01.py` L80)。`stop_retrying` なら同ファイル L434 で打ち切り(ASR_VALIDATION_UNCERTAIN)、それ以外で尽きれば L441 の STOPPED。

判定(`er007_ja_asr_validator_01.classify_ja_asr_match`、CURRENT_SPEC「Validator(日本語)」項 L1989 と一致):
1. 完全一致 -> EXACT_MATCH / 句読点・全角半角等の正規化後一致 -> NORMALIZED_MATCH。
2. 文字単位 `SequenceMatcher` の各 opcode を `protected_check_ja` が個別判定。数字差・否定差 -> 保護落ち -> TRUE_CONTENT_MISMATCH(`should_retry=True`)。読み(pykakasi)が一致する差は許容。
3. 残る差分の分類基準:
   - entity_like = 差分の両側が「カタカナ率50%以上、または英大文字略語を含む」(`_is_katakana_or_acronym`、L127)かつ opcode が `replace`。
   - phonetic_uncertain = 読みが濁点/半濁点の有無だけ異なる(`_reading_equal_allowing_voicing`、L172)かつ `replace`。
   - どちらかなら `cascade_eligible` -> ASR_VALIDATION_UNCERTAIN(`should_retry=False`)。
4. cascade_eligible でない差が残る場合: 全文読み一致/濁点差の救済 -> variant layer(OPEN-145、形態素解析)-> A2 Reading Resolver(辞書候補+LLM、flag既定ON)の順に救済を試み、全て不成立なら TRUE_CONTENT_MISMATCH(`should_retry=True`、L476-484)。
5. ASR_VALIDATION_UNCERTAIN かつ全diffが cascade_eligible のときのみ `evaluate_attempt_ja_with_cascade_detail` が Primary#2 -> Secondary(Azure)#1 -> #2 を実行(同一音声、TTS再生成なし)、全て不一致なら Human Review。

今回の具体的理由(ローカル再現で確認、3 attempt とも同一): 差分は `replace` 「演」->「現」1文字のみ。数字/否定なし。読み `しゅつえん` vs `しゅつげん`(kakasi: shutsuen / shutsugen)は不一致、濁点除去後も `しゅつえん` vs `しゅつけん` で不一致(`_reading_equal` False、`_reading_equal_allowing_voicing` False)。カタカナ/略語でもない(entity_like False)。よって cascade_eligible=False -> TRUE_CONTENT_MISMATCH(reason「固有名詞・略語・濁点ゆれ以外の内容に差がある」)。Secondary ASR には構造上進まない。
補足: raw_usage_log に各attempt直後の gpt-6-luna 呼び出し2回(計6回)があり、A2 Reading Resolver(`er011_a2_reading_resolver_01.py` L62 `A2_SUPPORT` ルーティング)が呼ばれて未解決に終わった(推定。resolver内部ログは attempt JSON に残っていない)。attempt JSON の `cascade_invoked` は null(=Cascade未起動)。

CURRENT_SPEC/実コード: 一致。ただし日本語には Semantic Equivalence Tier 3 は存在しない(er021 は English 専用、`er021_en_asr_semantic_equivalence_*`。JA validator/secondary は er021 を import していない)。依頼文の「ASR_VALIDATION_UNCERTAIN -> Secondary ASR・Semantic Equivalence Tier 3」のうち、日本語は Secondary ASR(Azure)のみ。

## 2. この分岐が採用された当時の理由

- ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(2026-08-25、`DECISION_LOG_HISTORY.md` L4456、`DECISION_LOG.md` L148): 旧「文頭2文字prefix+文字数」方式は30文字超segmentの内容誤り(欠落・置換・数字誤り・否定反転)を全て素通りさせると実証(blind-spot testing)。英語と同じ思想の全文Validator+Primary OpenAI gpt-4o-mini-transcribe/Secondary Azure Cascade へ置換。受容済みの限界: kakasi の異読み(頃 goro/koro 等)は常に false positive(安全側、不要retryのみ)。
- ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(同日、`DECISION_LOG_HISTORY.md` L4495): 濁点差のみの読みゆれ(ころ/頃)を TRUE_CONTENT_MISMATCH から ASR_VALIDATION_UNCERTAIN(Cascade対象)へ移す。phonetic_uncertain は `should_pass` を直接 True にしないため誤PASSは構造的に起きない。
- ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08(DECISION_LOG L66)、OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01(2026-09-12、CURRENT_SPEC L2005): TRUE_CONTENT_MISMATCH 直前に機械的/辞書+LLM救済を追加(fail-safe)。
- 方針の本質: 「読みで説明できない実質的な差=TTSの内容誤りとして再生成」「固有名詞・濁点差=ASR側の不確実性として同一音声を再確認」。

## 3. TTS誤発音 vs ASR誤認識を区別できない構造的問題

- Primary NG(読み不一致)は「TTSが実際に『出現』と発話した」と「TTSは『出演』と発話したがASRが『出現』と誤認」を区別しない。どちらも ASR 1本の文字列だけが根拠。
- 「出演/出現」は読みが1音異なる(えん/げん)ため、同音異字(例: 後半/公判)のような Reading 一致では救済できず、ASRの音響誤認(え/げ)なのか TTS の実発音なのかは文字列から判別不能。
- TRUE_CONTENT_MISMATCH 経路は同一音声へのASR再確認(Primary#2/Secondary)を行わず、TTSを再生成する。ASR誤認なら再生成しても同じ誤認が再現しうる(今回3回とも「出現」)ため、標準2+fallback1を消費して STOPPED になる。
- entity_like の基準(カタカナ率/略語)は漢字語に適用されないため、漢字1文字差は常に「TTS内容誤り」側へ落ちる。
- 3 attempt が同一の誤り(「出現」)を返したこと自体は、(a) TTSが本当に「出現」と読んでいる、(b) 同一音声特性でASRが毎回「出現」と認識、のどちらとも整合する。決定にはユーザー試聴が必要(試聴ページ参照)。

## 4. Secondary ASR を先に使う / 同音語比較を入れる場合

利点: ASR誤認なら誤再生成と STOPPED/Human Review を避けられる。2エンジン(OpenAI/Azure)が独立に同じ語を返せば TTS 実発音の証拠が強まる。TTS再生成は BATCH で1回約120-170秒(今回 172/123/122 秒)かかるが、ASR再確認は約1-5秒。
リスク: (a) 誤PASSリスク: 異なる語を2エンジンが一致して誤認する場合、またはAzureが正解寄りに寄せた場合に内容誤りを通す可能性。数字/否定は現行どおり先に保護する前提が必須。(b) 漢字語1文字差を広く「不確実」へ送ると、真のTTS誤りも Human Review へ回り件数が増える。(c) 同音語比較は「えん/げん」のような音差には効かない。
費用(登録単価、`er005_output/cost_baseline_01/pricing_snapshot.json`): OpenAI gpt-4o-mini-transcribe input $1.25/M tokens・output $5.0/M tokens(OFFICIAL_SOURCE)、今回 ASR 3回の実測合計 約$0.00055(入力180/出力65 tokens)。Azure Speech STT $1.0/hour(japanwest、OFFICIAL_SOURCE)、6秒音声1回で約$0.0017(秒換算の概算、実請求は未確認)。Gemini TTS(Flash Lite、BATCH)実測 約$0.00045/回(約0.073円)。gpt-6-luna $0.1/M input・$0.5/M output、今回6回(Resolver推定)の合計 約$0.00028。いずれもこの1segmentでは極小で、課題は費用より所要時間とHuman Review/STOPPED発生。

## 5. 改善候補(提案のみ、仕様変更なし、既存資産優先)

- 候補A(既存資産で最小): 漢字1文字replaceのみ・数字/否定なし・長さ正常・同一誤り文字列が2 attempt以上で再現、なら TTS再生成を続ける前に既存の Secondary ASR(Azure、`p4.get_full_text_via_azure_stt_continuous`)で同一音声を1回確認する(既存 `evaluate_attempt_ja_with_cascade_detail` の Secondary 部分を再利用)。2エンジンとも「出現」なら TTS誤りと確定、Azureが「出演」ならASR誤認の救済候補。
- 候補B: Reading Resolver の同音語/近音語辞書を拡張(今回は音が異なるため効果限定)。
- 候補C: TTS入力へ読み(しゅつえん)を明示して再生成(Reading Safety 既存機構の活用、TTS挙動変更のTrialが必要)。
- 候補D: STOPPED/Human Review へ回す際、全attempt音声とASR文字列を試聴ページで提示する運用の定型化(今回の試聴ページと同形式)。
- いずれも仕様変更でありTrial・ユーザー承認が必要。この報告は提案のみ。

## 6. 今回の3 attemptの実測ログ

| attempt | 種別 | route | 保存音声 | 長さ | ASR(gpt-4o-mini-transcribe, ja) | 判定 | TTS時間 | TTS費用 |
|---|---|---|---|---|---|---|---|---|
| 1 | 標準 | custom_b8f0ff16 | japanese_title_attempt1_customb8f0ff16.wav | 6.12s | AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。 | TRUE_CONTENT_MISMATCH | 172.4s | $0.000463 (0.074円) |
| 2 | 標準 | custom_b8f0ff16 | japanese_title_attempt2_customb8f0ff16.wav | 6.00s | 同上 | TRUE_CONTENT_MISMATCH | 122.8s | $0.000454 (0.073円) |
| 3 | fallback | minimal_fallback | japanese_title_attempt3_minimalfallback.wav | 5.96s | AIの電話に人間が出現、問題はキャスト変更のお知らせでした。 | TRUE_CONTENT_MISMATCH | 122.3s | $0.000451 (0.072円) |

共通: TTS = gemini-3.8-flash-lite-tts、voice Aoede、backend speech_metadata_flash_lite、BATCH、language ja。ASR呼び出し所要 1.30/2.76/0.73秒。Primary ASR のみ実行、Secondary ASR 未実行(`cascade_invoked` null)、最終 status STOPPED(「標準経路2回+fallback経路1回(合計上限3回)とも不合格」)。
音声保存: 3本とも `narration/attempts/`(`er011_human_review_lock_01.save_tts_attempt_audio`、L489。上書きせず個別コピー)に残存。`narration/japanese_title.wav` は最終attempt(=attempt3)で上書きされるが attempts/ に全保存。欠落なし。
証跡: 試聴ページ `user_test/meta_regen_01_asr_check/index.html`、Play証跡 `er053_output/family_x_tts_asr_rootcause_01/asr_check_play_evidence_01.json`。
