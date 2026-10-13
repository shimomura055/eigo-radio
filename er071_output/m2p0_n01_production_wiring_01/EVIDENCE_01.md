# EVIDENCE_01 (FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02、2026-10-13)

機械可読版: `evidence_01.json` / `cost_02.json` / `coffee_evidence_02/*`。run dir: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01`(wavは.gitignore、json/log/attemptsは追跡)。

## 0. 使用モデル(開発・評価最新モデル原則への記載)
KP: gpt-6-luna(本番既定)/TTS: gemini-3.8-flash-lite-tts(承認済みProduction backend `speech_metadata_flash_lite`)/ASR: 既存cascade(openai_asr+azure)。本番ラインのモデルをそのまま使用。旧/下位モデルの評価目的使用なし。

## 1. 実行コマンド(すべて `TTS_EXECUTION_MODE=STANDARD`、`--budget-jpy 80`、開始前にSTOP/STOP_ALL/STOP_NOTICE確認済み=本件適用なし)
1. plan(¥0): `--stage plan --style-profile coffee_n01_r2_p3 --tts-backend speech_metadata_flash_lite`(新out_dir、`audit/style_profile.json`にsha固定記録)
2. seed(¥0): `er071_coffee_m2p0_n01_seed_01.py support|r2`(承認済みsupport文面+R2 Preview/Comment音声をsha照合copy、`audit/seed_provenance_02.json`)
3. KP: `--stage scaffold --scaffold-only kp --level both`(Std->Adv直列、各1回)
4. TTS Std: `--stage tts --level a2 --only-segments full_story_part1,2,3`
5. TTS Adv: `--stage tts --level b1b --only-segments full_story_part1-3,kp1-5_english,kp1-5_explanation`
6. 再起動なし(外部停止0、原因不明rc!=0 0回)。有料run再起動0回。

## 2. Key Phrase(M2P0)
| Level | status | kp_backend_used / kp_supply | 最終5件 |
|---|---|---|---|
| Std(a2) | **CANONICALIZATION_INVALID**(既存retry 2回とも不合格) | db_hybrid / m2 | (selection)raw bean / pump one's fist / roasting / right away / based on。canonicalizationがrank5を"based on interviews"にしsource_span"based on"と不一致(Rule7)。M2供給自体は発火(demoted_allow 1、予約枠2、選択された予約枠候補=pumps its fist、fragment_risk選択0、M2所要15.85秒) |
| Adv(b1b) | CANONICALIZATION_PASS | db_hybrid / m2 | time lag / show up / come down / pump one's fist / hold on(v5=lag / price tag / show up / come down / come with)。予約枠(pumps its fist)選択、fragment_risk選択0、M2所要17.35秒 |

- 原因判断: INVALIDは共有の既存canonicalization(LLM)段で発生。M2のbug(candidate/span不整合)ではない(selection段は`KEY_WORDS_STRUCTURE_PASS`、source_span="based on"はC1の原文どおり)。ただし"based on"のような機能語寄りfragment選択はM2P0配線後も起こり得る(OPEN-310の監視対象)。
- 委任文の上限(KP再生成は1レベル1回、=今回の1回で使用済み)により**Std KPは再実行していない**(上限回避をしない)。Std KP音声は生成不可。
- Opus 9: KP LLM費用は`raw_usage_log.jsonl`に記録(stage=scaffold、gpt-6-luna、6 call、¥2.02)=予算Guardが捕捉。

## 3. Full Story(N01)音声
全segmentの`style_profile`: profile_id=coffee_n01_r2_p3、expected/style_base sha256=d1956c91c925…(N01、202文字、attempt JSONの`instruction_text`でsha再計算一致)。

| Part | 結果(合格経路) |
|---|---|
| Std part1 | N01 attempt1、NORMALIZED_MATCH、6%減速(5.966%)、減速後 NUMERIC_EQUIVALENCE_MATCH(1生成) |
| Std part2 | N01 attempt1 ASR不合格(ASR_VALIDATION_UNCERTAIN、"costs 6.1% more...the year earlier"誤り)→既存Standard fallback(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、=N01ではない)で600秒cooldown後attempt3合格(NUMERIC_EQUIVALENCE_MATCH)、6%減速(5.98%)、減速後 NORMALIZED_MATCH。生成3回、Azure ASR cascade 4 call(¥8.84) |
| Std part3 | N01 attempt1、NORMALIZED_MATCH、減速(5.969%)、減速後 NORMALIZED_MATCH |
| Adv part1 | N01(style_prefix一致)attempt1 TRUE_CONTENT_MISMATCH -> attempt2 NORMALIZED_MATCH |
| Adv part2 | attempt1 NORMALIZED_MATCH |
| Adv part3 | attempt1 HIGH_SIMILARITY_SAFE |

- retry/fallback/regeneration/減速/再検証/ASR判定は一切無変更(コード差分なし。今回の合格経路はすべて既存機構の通常動作)。Std part2は既存のStandard fallback経路に乗った(Production既定どおり)。
- Adv KP音声(kp1-5_en/explanation): 全OK。kp4_en attempt1 TRUE_CONTENT_MISMATCH("Pump one fist")->attempt2合格。

## 4. 速度・ポーズ(`coffee_evidence_02/speed_pause_02.json`、既存測定手順、ローカルfaster-whisper small)
Production側に自動の速度/ポーズ合否基準は無い(CURRENT_SPEC: A2約135WPMは目安、B1以上は目標なし、ポーズ基準なし)。**新Gateは作らず**、Trial参照値(Std 157±6 / Adv 167±6 WPM、文末ポーズ平均 Std<=498ms・Adv<=593ms、800ms以上無音<=1)を参考併記のみ:
| | 全体WPM(参考値) | part別WPM | 文末ポーズ平均/最大 | 800ms以上の無音 |
|---|---|---|---|---|
| Std(6%減速後) | 168.1(参考157±6の外) | 146.3 / 198.2 / 159.7 | 572 / 830ms | 5 |
| Adv | 178.2(参考167±6の外) | 159.5 / 186.5 / 187.2 | 572 / 790ms | 0 |
Std part2(fallback take)が198WPMと速い。判断はFable/ユーザー試聴に委ねる(Production基準での合否判定はしていない)。

## 5. M3 Gate(オフライン、`m3_gate_offline_02.json`)
- Adv: **PASS**(Full Story 3 part + KP解説5件)
- Std: **BLOCK**(part2 fallback_used=True/FINAL_STYLE_SHA_MISMATCH=N01でないtake。人間承認なしでは組立不可=既存仕様どおり)。さらに`--only-segments`実行がseedしたPreview/Comment1-4のresults entryを`SKIPPED_NOT_SELECTED`へ上書きしたためSTYLE_BASE_SHA_MISMATCH_OR_MISSING(wavは無傷)。後者は既存`--only-segments`の挙動(V5委任でも同様)で、今回修正していない。

## 6. 組立・試聴ページ
- runner `--stage assemble`は通していない(v5 out_dirと同様に新out_dirがrunner生成segmentの一部のみを保持するため)。Trial assembler(`er057_tone_trial_final_build_03_asm`、無改変)+`er071_coffee_m2p0_n01_build_01.py`でAdvanced完成版のみ組立: 322.77秒(v5 315.71秒)、peak 0.959、clipping 0、QA(`coffee_build_02/qa_m2p0_n01_02.json`)通過。差替えrole13(Full Story3+KP英語5+KP解説5)、他はv5音声再利用(sha記録)。
- **Standardは完成版なし**(KP INVALIDのため)。参考としてStd Full Story N01 3 partのみ掲載。
- 公開: https://shimomura055.github.io/eigo-radio/user_test/coffee_m2p0_n01_01/index.html
- Playwright実再生(`coffee_evidence_02/pages_play_evidence_02.json`): 28 audio全て再生進行OK、seek OK、全編322.77秒(期待322.77秒)、console error 0、HTTP>=400 0、file:///なし。

## 7. 費用(`cost_02.json`)
合計 **JPY 25.70**(openai 2.06[KP LLM 2.02+他] / gemini 11.50 / openai_asr 3.30 / azure 8.84)。Guardrail 80、soft 60に未到達。

## 8. Family Z mock(課金0、記事再生成・音声化なし、`z_mock_check_02.json`)
NARRATOR_FULL_STORY_STD/ADVともstyle_label=N01、sha=d1956c91…、StdにA2減速指示の追記なし。Melos run_e2e_02の既存記録(旧PD8系13/14 entry)は読み取りのみでLEGACY_NARRATOR_ENTRIES_MISMATCH(=run level style label不一致でSTOPする仕様の確認)。`audit/narrator_style_record.json`機構あり。**Zのruntime発火(Checklist 5/6)は未確認**。

## 9. Parity / 回帰
- Parity Gate(Opus 3、`parity_02.json`): 10記事でrows sha・final prompt sha(6記事)・demoted_allow一致。
- 回帰(変更前->変更後、すべて失敗0): er030 71->102、er019 337->357、er063 47->59、er026 107->107、er062 64->64、er003_test_key 322、er011_kp 11、er033 64。
- er064(Trial)テスト: 130件中121 PASS。失敗9件はいずれも今回の変更起因でない/想定内: tiktoken未導入(2 ERROR)、module import時sys.exit(3 ERROR)、HARD_STOP定数・cost_run_02.json存在チェック(3 FAIL、過去Trial固有の状態)、`state_guard_r3`(Production file shaを固定する旧Trial記録: er030 core等を承認済みProduction変更したため不一致=想定内)。要確認としてFable判断に委ねる。
