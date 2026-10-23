# FAMILY-X-NEWS-2ARTICLES-E2E-02 RESULT_01 (委任_01, 2026-10-23 JST、途中報告: 記事B完成候補 / 記事A STOP)

性質: 現行Production正式経路でのE2E(新Trial・新仕様・コード/flag/Prompt/閾値変更0)。最終ユーザー試聴PASSはユーザー本人の判断。
管理: run id run_nws_02、TTS_EXECUTION_MODE=STANDARD、STOP確認rc=0(stop_check_*.json)。

## 1. 記事B uk_train_speaker_playback(完成候補)
- JAタイトル: その動画、車内で勝手にプレミア上映していませんか(ユーザー記載タイトルは「テーマ名」扱い、Writer出力を採用)
- Status: Std(a2) 306.68秒 / Adv(b1b) 279.82秒 とも USER_LISTENING_PENDING(完成候補)。segment Std 11/11 OK・Adv 10/10 OK、TTS retry 0、HR Lock全RESOLVED(17/14)、fallback 0。
- 試聴URL: https://shimomura055.github.io/eigo-radio/user_test/uk_train_speaker_playback_e2e_02/index.html (HTTP200、Playwright plays_ok 47/47・seek全OK・console error 0=pages_play_evidence_uk_train.json)
- ページ標準検査(tools/user_test_page_standard_check_01.py): **FAIL 1項目**(Standard:no_internal_info_in_script)。原因=チェッカー`_INTERNAL_RE`(er_user_listening_page_common_01.py:125-127)が記事本文の正当な語「音楽」(Std comment_2の台本「音楽や動画を楽しむことと…」)を内部情報(BGM/効果音用語)と誤検知。台本は本文そのもの・開発者情報の漏れではない(誤検知)。チェッカー改修は未実施(Fable判断)。他16項目PASS。
- Ledger: VERIFIED 13 / AMBIGUOUS 1(F001 Byelawsの適用範囲) / REJECTED 1。B3採用 F002(Byelaw 7(1)音規定)・F004(罰金上限£1,000は上限額)・F011(DfT 2026-10-19全国キャンペーン開始)。
- 事実の区別(合否はFable): 本文は「新たな一律禁止ルールではない」「既存規則は不快にさせる音のみ対象・書面許可で例外」「最大£1,000の『最大』『可能性』」「キャンペーン(啓発)と既存Byelawsを分離」「ポスター・案内放送は『予定』」と記述。バスByelaw権限等の提案段階施策はB3で不採用=本文に混入せず。
- KP: Std = sound no one asked for / reach for one's wallet / draw that line。Adv = a blanket ban / reach for one's wallet / draw that line。KP3-ASR投票=全6件PASS_DUAL(Whisper発動0)、kp_backend=fulltext_p2、key_phrase_source_gate 3/3 PASS。
- 固有名詞アラーム(PNAP)0件・HR残0。er109(同音・異表記救済)は`er109_orthographic_equivalence_v1_proto_aho02`が判定記録に付与(Std 6/Adv 8記録)、PASS_WITH_WARNING化した箇所はStd comment_2のみ(SECONDARY_CONFIRMED、耳確認推奨=comment_2「英国が始めたのは、音をすべて禁じる新しい法律ではなく…」)。Adv 0件。Adv preview=TIER1_NUMERIC_EQUIVALENCE承認同値でPASS(「£1,000」読み)。Std japanese_title=READING_MATCH承認同値(ASR「社内」・台本「車内」、同音異義の既存救済)。
- 警告: a2_derived_from_advanced_sha_mismatch(観測のみ、前回と同じ既存警告)。headroom valve未発動、style_profile_gate PASS(fx_20261017)。
- evidence: er019_output/uk_train_speaker_playback/run_nws_02/、er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/{entry_point,raw_usage_log,{a2,b1b}/audit/*}、docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-02/eval_uk_train_speaker_playback.json。

## 2. 記事A ig_nobel_2026(STOP: B3注記生成の決定論Gate)
- Research/Ledger完了: VERIFIED 10 / AMBIGUOUS 1(IG2026-03: エネルギー3倍超の比較対象の曖昧さ) / REJECTED 0。ユーザー提示タイトルの「ゴキブリのミルク」「鼻のかみ方」は2026年の公式受賞者ページに実在(ゴキブリ=2016年論文の栄養結晶Lili-Mip構造研究、鼻かみ=1977年論文、受賞年と研究年を区別するLedger注記あり)。その他キス進化・下着分解・小便器飛沫・赤ちゃん/10代の匂い・撤回済み毒ヘビ論文(IG2026-11、確立知見としない注記)。
- B3(storyline_b3)は2回(初回+`--regenerate-stage storyline_b3`)ともLedger IG2026-01採用で`AnnotationProducerError: internal check c_core_peripheral: core '2026年' has never-core kind year`により、Writer到達前にSTOP(runner標準のannotation producer内部検査。Gate迂回なし)。
- 根本原因(再現済み、API 0): er053_b3_deterministic_producer_01.py `derive_ranks`が、同一Fact内の'2026年'(kind=year)と'2026年9月3日'(kind=date_time)を概念結合(contains一致、:518)し、概念の種類=最長表記(date_time)で中核にした際、年表記itemへroleを継承(:544 `it["role"] = "core" if it["_root"] in core ...`)。一方、内部検査(:798)は年/序数/名前埋込のcoreを禁止(never-core)=同一モジュール内の不変条件違反。IG2026-01のみをderive_ranksに通すだけで再現(`2026年 year core` / `2026年9月3日 date_time core`)。授賞日付とその年が同じFact内に現れる記事で系統的に再発しうる。
- 修正案(未適用、Production .py変更は委任禁止): :544を `it["role"] = "core" if (it["_root"] in core and it["kind"] not in ("year","ordinal","name_embedded")) else "peripheral"` とする1行。scratch複製(コード未コミット)でIG2026-01入りのrun_nws_02に`produce_annotated_b3`を実行しc_core_peripheral含む内部検査が通ることを確認済み(scratchpad/fx/、本番ファイル無変更)。既存回帰test(er053系)での確認は未実施。
- 証拠: er019_output/ig_nobel_2026/run_nws_02/(storyline_b3_attempt1_annot_fail/=初回、storyline_b3/=2回目)、console_text_01.txt、docs/research/.../stop_check_ig_nobel_2026.json。
- 費用(A、Research〜B3のみ): 約50円(初回49.82円)+B3再生成約9円。音声・Writer未実行。

## 3. 費用・時間(B)
text 63.65円(research 23.31/ledger 16.29/B3 8.86/丸め0.09/Writer R0-R2 12.62/Adv英訳0.27/Std 0.30/RF 約2.4) + audio 24.22円(scaffold 1.39、TTS gemini 13.58、ASR openai 3.79・azure 5.44、他openai 0.03) = **87.87円/記事セット**(1回限りの日本語読み調査費は発生せず)。記事Aは上記約59円消費・未完。当日累計(daily_dev_cost_01 256円[開始時点])+本案件約147円=約403円見込み(1,000円内)。所要: B text 約8分、scaffold 約5分、TTS 約9分、assemble〜ページ約5分。
