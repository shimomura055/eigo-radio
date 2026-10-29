# JA人名ASR誤認の整理と「かな/漢字人名の読み辞書供給」拡張 設計メモ 01 (2026-10-29)

**本メモは設計案のみ。仕様変更=ユーザー承認事項。実装しない(API 0、Production/台帳/閾値/Prompt変更0)。**

## 1. 現状の確認(file:line)
- `er003_v1_n3_01_tts_generate.py:661-664`(B1B JA、:966-969はA2 JA): `expected_readings`は`foreign_token_findings`のうち`category==FOREIGN_TOKEN_READING_DICTIONARY`(Latin外来語トークンで読み辞書に読みがあるもの)のみから生成。`classify_foreign_tokens_in_japanese_text`(`er003_audio_tts_asr_safety.py:709`)はLatin/数字混じりトークンが対象のため、かな/漢字の人名(タジョマル/真砂/武弘)は入らない。
- `er025_entity_pronunciation_resolver_core_01.py:266 resolve_unknown_ja_tokens`: 未知Latinトークンのみ。`seed_work_canon_reading`(:408)は作品固有の読みをLedgerへseedする既存API(source_context別entry)。
- `er007_ja_asr_validator_01.py:203-241 _reading_dictionary_token_diff`: 「c_span全体がexpected_readingsのキーと完全一致」なら漢字/カタカナ表記も対象(固有名詞をexpected_readingsへ追加するケースを想定済み)。**判定側の受け皿はあり、供給側が無い**。
- `er078_ja_v2beta_01.py`(JA-ASR v2+β、2026-10-29 APPROVED): `begin(..., expected_readings=)`:125、`composite_core`:460-496で`classify_ja_asr_match(..., expected_readings=expected_readings, allow_reading_resolver=False)`へ素通し。新規ロジックは不要(値の供給のみ)。
- 発音台帳(`er006_output/pronunciation_ledger_01/ledger.json:1411` Tajomaru、`:1454` Takehiro)は英語TTS用ローマ字entity。`er007_ja_*.py`/`er078_ja_v2beta_01.py`は台帳(`pronun_ledger`)を参照しない(JA判定には非適用。er007_ja_tts_retry_path_fix_test_01のmock以外ヒットなし)。

## 2. 設計案(最小)
1. 供給元(費用0): Z=Theme Packageの登場人物表/話者表(`<run>/speaker_table.md`)・`seed/seed.json`。作品固有人名の読みは`seed_work_canon_reading(surface, ja_katakana, source_context="family_z_<work>")`で事前seedする既存運用に揃える。X/Yは人名が記事毎に異なり、Fact Pack/entity表からの取得が別設計になる。
2. 追加箇所(案): `er003_v1_n3_01_tts_generate.py:661`と`:966`の`expected_readings`生成直後に、source_contextのLedger seed(`ja_reading_katakana`)のうちcanonical textに現れる表記(かな/漢字)を`{surface.lower(): reading}`で追記する小関数(例 `_collect_work_canon_name_readings(text, source_context)`)を呼ぶ。判定側(:203)は無変更。
3. 限界(重要): 判定は「ASR表記の読み」と「辞書読み」の一致を見るため、ASRが別人名(太郎丸/政子)を出力した場合は不一致でFAILのまま。**辞書供給だけでは今回のcomment_3は救えない可能性が高い**。救済には(i) ASR側の語彙ヒント(faster-whisper initial_prompt等。API仕様・費用要確認)、(ii) 人名スロットのマスク比較(`er078_ja_v2beta_01._mask`:446 に近い考え方)が必要。(ii)は別人名への取り違えを許すため誤PASSリスクが大きい。
4. 誤PASSリスク: マスク/緩和は人物取り違え(タジョマル→マサゴ)を見逃す。入れるなら辞書読み一致のみ許容、かつ人名を含むclipはPASS_WITH_WARNING+試聴リスト(v2+βと同じ非ブロッキング警告)で人手確認を残す案が妥当。
5. 費用: 実装・test・過去資料での再判定ともAPI 0。

## 3. 影響範囲 X/Y/Z
- Z: 登場人物表あり(seed運用あり)。直接の恩恵(藪の中/走れメロス)。
- X: ニュースの人名・組織名(例 フーシ派/タイフーン機)が同型。供給元スキーマが無くZより設計が重い。
- Y: persona会話で人名が少なく影響小。
- scope外(A/B/C)は`er109_xz_scope_01`により不変(27-7)。

## 4. 過去のJA人名起因HR/STOP/ALARM件数(audit JSON走査: `er019/er026/er121_output/**/audit/{tts_generation_results,pronunciation_alarms}.json`)
- JA clip総数(重複run含む): X 245(OK238/STOPPED5/HR_LOCKED2)、Z 252(OK244/STOPPED6/HR_LOCKED2)、Y 44(OK39/STOPPED5)。
- 人名・固有名が主因と判断できる非OK: Z **1**(藪の中comment_3: タジョマル→太郎丸/多助丸/多十丸、真砂→政子/雅子)、X **1**(`middle_east_yemen_saudi__run_mey_02` comment_2: フーシ派→風師波/封死派、タイフーン→台風機/台風期、HUMAN_REVIEW_LOCKED)。
- 人名を含むが主因が別(数字表記/ASR言い換え等)と見られる: Z melos comment_1/3(メロス→メオス1回あり、3日間の表記等。STOPPED 5 run + HR_LOCKED 2)。人名のみでは断定せず除外。
- PASS_WITH_PRONUNCIATION_ALARM(JA、Z): ユニークalarm_id 5件(in_a_grove comment_3 ×2、melos run_e2e_01 comment_2/3 ×2、melos run_sf_prod_01 comment_3 ×1[preserve系は同ID複製])。X/Y のJA alarmは0件。
- 総評: 人名起因のHR/STOPは作品別に1件ずつ(X1/Z1)で頻度は低〜中。現行運用=Human Review(試聴)で処理。辞書供給のみでは今回事例を救えない可能性が高いため優先度は低〜中。推奨=現行運用維持+必要時のみTrialを別途提案。
