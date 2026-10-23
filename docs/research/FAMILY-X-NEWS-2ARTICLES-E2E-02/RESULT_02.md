# FAMILY-X-NEWS-2ARTICLES-E2E-02 RESULT_02 (委任_02, 2026-10-23 JST、er053是正→記事A完成候補→記事B検査誤検知対応)

性質: 現行Family X Production正式経路(新Trial・新仕様・Prompt/閾値/flag変更0)。最終ユーザー試聴PASSはユーザー本人の判断(UDR #166)。

## 1. er053不具合の是正(OPEN-468、Fable承認・11-8区分B)
- 修正: er053_b3_deterministic_producer_01.py:544 `it["role"]`を `core かつ kind not in (year, ordinal, name_embedded)` に限定(1行+コメント1行)。:798の内部検査(never-core)を正とした。commit a21f1cfd2。
- 実施前確認: (a) er053 producerのimport元はer019 Xランナー/X B3選定/X factlock writer/契約/DEV Trial(er052/er082/er083/er090/er095/er110)のみ。A/B/C・Z経路の参照0。 (b) ledger・B3 brief・evidenceが残る29 run(er019_output配下: boredom_aggression/coffee_prices x4/hormuz x4/small_bag x2/meta x5/manga_ai_chat_byus/middle_east x2/paycheck x2/prix_pascal/semiconductor/tesla_spacex/uk_train/refresh_e2e/b3_production_wiring x2/ig_nobel)で修正前後の`produce_annotated_b3`出力(annotated brief・sidecar・writer_constraints・manifest。sha類とgenerated_atのみ正規化)を比較(API 0): 差分0=28 run、差分1=ig_nobel_2026のみ(修正前はAnnotationProducerErrorで停止、修正後は注記成功)。core数が仕様下限を割る例なし(ig: core=9月3日/1.2 Å/3倍)。 (c) er053系・er019系 39 test file中38 PASS。残る1 file(er019_family_x_fx_20261016_wiring_01_test_01 `test_fallback_used_consumers_do_not_read_kp_english_entries`)の失敗はFamily Y DEVの`er110_family_y_audio_trial_01.py`が未許可でfallback_usedを読むため(自分起因ではない)。自作`er019_nws2_eval_01.py`は許可リストへ追加済み。
- test変更: RULES_SHA256_BEFOREピン更新(derive_ranksソース変更で不可避、26.10.10と同じ先例)、DOCUMENTED_FUNCTION_DIVERGENCE追加(Trial逐語一致testに役割付与1行の意図的差分を明記)、新規er053_b3_never_core_year_role_test_01.py(2件)。
- 影響: 授賞日付とその年が同一Factに現れる記事で、年表記が日付概念の一部としてcoreになる系統的STOPを解消。既存記事の本文・音声には影響なし(差分0)。

## 2. 記事A ig_nobel_2026(完成候補)
- 再開: 既存Ledger/B3 brief(2回目)を再利用(Research/Ledger/B3 LLM再実行0)、注記producer(LLMなし)成功→core数値丸めjudge 1call→Writer R0/R1/R2→Advanced英訳→Std→RF。有料run起動=1回(text一括)。音声はscaffold→tts→assembleの標準stageを各1回(再起動なし)。
- JAタイトル: 『「ゴキブリのミルク」、コップより先に「収納術」を見てほしい』(Writer出力採用。ユーザー記載の記事名『ゴキブリのミルクに、鼻のかみ方? 今年も珍研究が受賞』はテーマ名扱い)。
- 試聴URL: https://shimomura055.github.io/eigo-radio/user_test/ig_nobel_2026_e2e_02/index.html (HTTP200、Playwright audio 47/47再生・seek全OK・console error 0=pages_play_evidence_ig_nobel.json、ページ標準検査17/17 PASS=page_check_ig_nobel_2026.json)。Std 308.01秒 / Adv 291.93秒。
- 音声QA: segment Std 11/11・Adv 10/10 OK、TTS retry 0、fallback 0、HR Lock RESOLVED 17/16(残0)、KP3V 6/6 PASS_DUAL(Whisper発動0)、kp_backend=fulltext_p2、key_phrase_source_gate 3/3、style_profile_gate PASS(fx_20261017)、headroom valve未発動、PNAP 0件(本文に人名・大学名なし=供給/発火対象なし)、er109同値記録は`er109_orthographic_equivalence_v1_proto_aho02`が付与、PASS_WITH_WARNING 0。承認同値: Std preview/comment_2がREADING_MATCH(preview=『分かる』→ASR『わかる』と鉤括弧の有無、comment_2=『子ども→子供』『おなか→お腹』『分かった→わかった』と読点)。警告: a2_derived_from_advanced_sha_mismatch(観測のみ、既存)。
- KP: Std=jump into action(すぐに行動を起こす)/three times as much energy(三倍のエネルギー)/packed with nutrition(栄養がたっぷり詰まった)。Adv=nutrient-rich crystals/bound to the protein/leap into action。
- 事実性: Ledger VERIFIED 10/AMBIGUOUS 1(IG2026-03)/REJECTED 0。B3採用はIG2026-01・02・03のみ(ゴキブリ栄養結晶研究)。本文に受賞年(2026)・研究年(2016/1977)・鼻のかみ方・撤回済み毒ヘビ論文は出現せず(Grep 0件)=年の混同・撤回論文の確立知見扱いは構造的に発生しない。ただしユーザーのテーマ文言(鼻のかみ方、複数の珍研究)に対する被覆は限定的(B3が1研究に絞った結果)。AMBIGUOUSのIG2026-03は『推定』『複数種の哺乳類の乳と同重量比較』『人が飲めば3倍元気という意味ではない』と曖昧さを保持して採用(断定なし)。「結晶が支える働きは確定していない」と未確定を明記。規則(事実)と演出(カフェ閉店・通販番組などの比喩)は分離されている。RF(非Blocking)はAdv 3件/Std 4件issue(review_queue/post_en/ig_nobel_2026__run_nws_02)。
- 費用: text 72.80円(research 21.60/ledger 19.36/B3 17.24[2回分]/丸め判断0.10/Writer R0-R2 11.68/Adv 0.31/Std 0.46/RF約2.0) + audio 10.91円(scaffold 1.37、TTS gemini_batch 5.82、ASR openai 3.19/azure 0.51) = 83.71円。うち1回目STOPまでで約58円は委任_01で消費済み(再開分は約14.6+10.9=25.5円)。
- 所要(再開分): text 約5分(12:32-12:37)、scaffold 約2分、TTS待機29分(Y Phase 3 TTSが並走中のため委任ルールで最大30分待機)、TTS 58分(13:07-14:05。記事Bは9分。Yの同時TTSとの競合の影響の可能性があるが原因は未検証)、assemble+ページ 約2分、公開・検証 約10分。

## 3. 記事B 残件
- ページ標準検査: `_INTERNAL_RE`の『音楽』を単独/括弧内/ラベル形式のみ検出に絞込(er_user_listening_page_common_01.py:125-129)。user_test配下の全91 index.htmlで修正前後の検査結果を比較(page_cmp): 変化=記事B 1件(Standard:no_internal_info_in_script FAIL→PASS)のみ、新規見逃し0。コーヒー系既存ページの『(音楽・通知音。読み上げなし)』は他語(通知音/読み上げなし)で引き続き検出。記事B 17/17 PASS(page_check_uk_train_speaker_playback_d02.json)。tools/user_test_page_standard_check_01_test_01.py 12 passed。
- Std comment_2 PASS_WITH_WARNING(SECONDARY_CONFIRMED)の機械差分: 台本『…乗客にヘッドホンを使うよう呼びかける…。では、今あるルールは、周りに…』に対し、一次ASR=『ヘッドフォン』(ホ→フォの表記ゆれ)、二次ASR=『ヘッドホン』一致だが『今あるルールは、周りに』の読点が無い(『…ルールは周りに』)。差異は表記/句読点のみで内容語の欠落・誤りなし。耳確認はFable/ユーザー。
