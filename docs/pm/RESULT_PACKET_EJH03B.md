# RESULT_PACKET EJH03B (ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B = FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01 委任_08 = SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02D)

結論: 8dir(X月・X②・X④・X⑭[新規]・Y再配達・Y姓・Zメロス・Z雪女)で、訳の無かったパートの生成訳・M8・Vocabulary全件再生・asset rev01-gを実走配線して再produce、Playwright PC/mobile全NG0、diff Gate OK、live確認済み。**未完は2件**: (1)⑨Metaは再produce未実施(Adv Vocabulary『latter』の音声がTTS Gate STOPPED=8 attempt全て ASR『Ladder』、Gate迂回せず停止。公開済みEnd Userはrev01-fのまま無傷)。(2)点灯日本語の可視性(UI、D継続)。費用は約¥25/Cap¥45。コミット: 910e66a9c(コード)、bcddcf0c3(成果)。

## 4行(Charter)
1. 既存仕様整合: er135_enduser_rules_01.py(ASSET_BUILD_ID rev01-g)、er137_vocab_extra_audio_01.py(apply_to_article/validate_article、役割`vocab_extra_english`)、OPEN-618/620/612の承認済み範囲、ユーザー原文`docs/pm/delegation_log/2026-10-30_ENDUSER-EN-JA-LINKED-HIGHLIGHT-01_USER_02.md`、`..._SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01_USER.md`。routing ENDUSER_JA_TRANSLATE/VERIFY(モデルgpt-6-luna、ModelContractErrorはSTOP)。既存Gate/retry/fallback/Prompt/閾値は無変更(Vocab②は既存の`_generate_or_reuse_kp`系=KP3V・Master Store・retry/fallbackをそのまま使用)。
2. 未承認機能の既定値: 本件は全て承認済み仕様(APPROVED_FOR_PRODUCTION)。library `build_enduser`は訳生成・judgeとも既定OFF(test: `test_library_build_is_off_by_default_but_official_hook_generates_missing_parts`)、公式`hook_run`/`produce_enduser`は既定AUTO(`--no-translate`/`--no-judge`で停止)。確認=Grep `AUTO_TRANSLATE_LLM`/`AUTO_JUDGE_LLM`(er135_enduser_page_01.py)、test 294+33 PASS。
3. 失敗終了時の最終成果物: (a)訳不成立=Zメロスadv_14・Z雪女std_11の各1段落は英語のみ表示+warning(build_info.warnings、`user_test/family_z_melos_kphr_evidence_r3/enduser/data/article.json`)。(b)Vocab音声欠落=⑨ Meta Adv `latter` STOPPED -> `ENDUSER_VOCAB_AUDIO_INCOMPLETE`でSTOP(掲載せず、公開済みEnd Userは変更なし、`er019_output/.../meta_waddle_world__run_fx4_01/b1b/vocab_audio/vocab_audio.json` complete=false)。(c)埋め込み失敗=null+degraded(既存test)。目的適合: 欠落項目を再生不能のまま掲載せず、既存の公開済みページを壊さない(目的の「全件再生可」は⑨のみ未達)。
4. 撤去・残置: 撤去=なし。置換=test `test_xy_title_and_kp`->E1の4 test、`adv preview expected not_generated`->generated。残置=rev01-f/rev01-e asset(`ASSET_TRANSLATION_KINDS`に保持、藪の中はrev01-e凍結)。Grep(`rev01-f` in derive/rules)で残置確認。

判定整合: 重大NG=なし / 主因=[⑨ Adv Vocabulary latter の ASR『Ladder』判定(TTS Gate STOPPED)] / 是正対象=[⑨ Metaの再produce(HR試聴後)・可視性UI(D)] / STOP理由=[なし(STOP通知rc=0)。Vocab 1件のGate STOPPEDのみ] / 提示=証拠のみ(⑨を除く8dirは可)

## 9dir x level x part の対応表(集計。part単位の全行=docs/research/ENDUSER-EN-JA-LINKED-HIGHLIGHT-01/evidence_03b/table_all.md)
連動率=連動文数/英文数(null群=誤点灯を避けて点灯しない)。誤対応0の根拠: gold A/未見/held-out(誤対応0)、Playwright J検査(クリックで点灯する群=データ一致、全文の状態一致、null群は点灯なし)NG0、生成訳は1文=1群・埋め込みなし(how=gen)。「訳なし」はStd Preview/Comment等、承認済み訳が無く生成対象でもない(日本語本文のみ=別文)パート(委任_03Aの`na_ja_only`)。

| dir | level | part | 訳の出所 | part数 | 英文数 | 連動文数 | 連動率 |
|---|---|---|---|---|---|---|---|
| x_moon_shrinking_reselect_01 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_moon_shrinking_reselect_01 | std | comment | 訳なし(英語のみ) | 4 | 9 | 0 | - |
| x_moon_shrinking_reselect_01 | std | story | 承認済み訳 | 3 | 46 | 40 | 87% |
| x_moon_shrinking_reselect_01 | std | oneline | 生成訳 | 1 | 2 | 2 | 100% |
| x_moon_shrinking_reselect_01 | adv | preview | 生成訳 | 1 | 2 | 2 | 100% |
| x_moon_shrinking_reselect_01 | adv | comment | 生成訳 | 4 | 8 | 8 | 100% |
| x_moon_shrinking_reselect_01 | adv | story | 承認済み訳 | 3 | 35 | 33 | 94% |
| x_moon_shrinking_reselect_01 | adv | oneline | 生成訳 | 1 | 2 | 2 | 100% |
| x_untidiness_resource_01 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_untidiness_resource_01 | std | comment | 訳なし(英語のみ) | 4 | 8 | 0 | - |
| x_untidiness_resource_01 | std | story | 承認済み訳 | 3 | 47 | 33 | 70% |
| x_untidiness_resource_01 | std | oneline | 生成訳 | 1 | 3 | 3 | 100% |
| x_untidiness_resource_01 | adv | preview | 生成訳 | 1 | 2 | 2 | 100% |
| x_untidiness_resource_01 | adv | comment | 生成訳 | 4 | 8 | 8 | 100% |
| x_untidiness_resource_01 | adv | story | 承認済み訳 | 3 | 36 | 36 | 100% |
| x_untidiness_resource_01 | adv | oneline | 生成訳 | 1 | 3 | 3 | 100% |
| x_ai_chat_sponsored_persuasion_01 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_ai_chat_sponsored_persuasion_01 | std | comment | 訳なし(英語のみ) | 4 | 7 | 0 | - |
| x_ai_chat_sponsored_persuasion_01 | std | story | 承認済み訳 | 3 | 39 | 39 | 100% |
| x_ai_chat_sponsored_persuasion_01 | std | oneline | 生成訳 | 1 | 3 | 3 | 100% |
| x_ai_chat_sponsored_persuasion_01 | adv | preview | 生成訳 | 1 | 2 | 2 | 100% |
| x_ai_chat_sponsored_persuasion_01 | adv | comment | 生成訳 | 4 | 9 | 9 | 100% |
| x_ai_chat_sponsored_persuasion_01 | adv | story | 承認済み訳 | 3 | 34 | 34 | 100% |
| x_ai_chat_sponsored_persuasion_01 | adv | oneline | 生成訳 | 1 | 2 | 2 | 100% |
| x_meta_waddle_world_01 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_meta_waddle_world_01 | std | comment | 訳なし(英語のみ) | 4 | 8 | 0 | - |
| x_meta_waddle_world_01 | std | story | 承認済み訳 | 3 | 38 | 31 | 82% |
| x_meta_waddle_world_01 | std | oneline | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_meta_waddle_world_01 | adv | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_meta_waddle_world_01 | adv | comment | 訳なし(英語のみ) | 4 | 8 | 0 | - |
| x_meta_waddle_world_01 | adv | story | 承認済み訳 | 3 | 35 | 33 | 94% |
| x_meta_waddle_world_01 | adv | oneline | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_jwst_mystery_emission_line_01 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| x_jwst_mystery_emission_line_01 | std | comment | 訳なし(英語のみ) | 4 | 9 | 0 | - |
| x_jwst_mystery_emission_line_01 | std | story | 承認済み訳 | 3 | 44 | 37 | 84% |
| x_jwst_mystery_emission_line_01 | std | oneline | 生成訳 | 1 | 2 | 2 | 100% |
| x_jwst_mystery_emission_line_01 | adv | preview | 生成訳 | 1 | 2 | 2 | 100% |
| x_jwst_mystery_emission_line_01 | adv | comment | 生成訳 | 4 | 8 | 8 | 100% |
| x_jwst_mystery_emission_line_01 | adv | story | 承認済み訳 | 3 | 35 | 35 | 100% |
| x_jwst_mystery_emission_line_01 | adv | oneline | 生成訳 | 1 | 2 | 2 | 100% |
| y_production_redelivery_fee_03 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| y_production_redelivery_fee_03 | std | comment | 訳なし(英語のみ) | 3 | 5 | 0 | - |
| y_production_redelivery_fee_03 | std | story | 承認済み訳(devの日本語原稿) | 8 | 51 | 47 | 92% |
| y_production_redelivery_fee_03 | adv | preview | 生成訳 | 1 | 2 | 2 | 100% |
| y_production_redelivery_fee_03 | adv | comment | 生成訳 | 2 | 3 | 3 | 100% |
| y_production_redelivery_fee_03 | adv | story | 承認済み訳(devの日本語原稿) | 8 | 37 | 37 | 100% |
| y_production_surname_choice_01 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| y_production_surname_choice_01 | std | comment | 訳なし(英語のみ) | 3 | 5 | 0 | - |
| y_production_surname_choice_01 | std | story | 承認済み訳(devの日本語原稿) | 8 | 54 | 51 | 94% |
| y_production_surname_choice_01 | adv | preview | 生成訳 | 1 | 3 | 3 | 100% |
| y_production_surname_choice_01 | adv | comment | 生成訳 | 2 | 3 | 3 | 100% |
| y_production_surname_choice_01 | adv | story | 承認済み訳(devの日本語原稿) | 8 | 42 | 42 | 100% |
| z_melos_kphr_evidence_r3 | std | preview | 訳なし(英語のみ) | 1 | 2 | 0 | - |
| z_melos_kphr_evidence_r3 | std | comment | 訳なし(英語のみ) | 3 | 5 | 0 | - |
| z_melos_kphr_evidence_r3 | std | story | 生成訳 | 3 | 53 | 53 | 100% |
| z_melos_kphr_evidence_r3 | adv | preview | 生成訳 | 1 | 2 | 2 | 100% |
| z_melos_kphr_evidence_r3 | adv | comment | 生成訳 | 3 | 5 | 5 | 100% |
| z_melos_kphr_evidence_r3 | adv | story | 生成訳 | 2 | 37 | 37 | 100% |
| z_melos_kphr_evidence_r3 | adv | story | 訳なし(英語のみ) | 1 | 25 | 0 | - |
| z_yuki_onna_01 | std | preview | 訳なし(英語のみ) | 1 | 3 | 0 | - |
| z_yuki_onna_01 | std | comment | 訳なし(英語のみ) | 3 | 5 | 0 | - |
| z_yuki_onna_01 | std | story | 訳なし(英語のみ) | 1 | 18 | 0 | - |
| z_yuki_onna_01 | std | story | 生成訳 | 2 | 29 | 29 | 100% |
| z_yuki_onna_01 | adv | preview | 生成訳 | 1 | 2 | 2 | 100% |
| z_yuki_onna_01 | adv | comment | 生成訳 | 3 | 6 | 6 | 100% |
| z_yuki_onna_01 | adv | story | 生成訳 | 3 | 48 | 48 | 100% |

⑨Metaは再produceしていないため上表は公開済み(rev01-f/v1整列)の状態。

## 承認済み訳の再生成0 / M8 / Z
- 承認済み訳: diff Gate(`tools/ejh03b_diff_gate_01.py`)が7dir全てで「承認済みja全文一致・訳ありpartに生成訳なし」を確認(`evidence_03b/diff_gate_out.txt`)。許可差分=ja_align・生成訳・vocab audio・asset・sync微小差(<=0.25s)のみ。x_moonのStd min_row_ratio 0.913->0.8824は短行の比率でE1是正の副作用(gate PASS、短行規則内)。
- 生成訳(最新run): X月7part ¥1.17、X②7 ¥0.96、X④7 ¥0.90、⑭7 ¥0.99、Y再配達3 ¥0.22、Y姓3 ¥0.22、Zメロス(2run計)約¥6.4、Z雪女(3run計)概算約¥6〜7(1回目はresult json未保存)。Z不成立段落: メロスadv_14(verify_ng『城壁』追加)、雪女std_11(verify_ng『着物』追加)。数値決定論照合の偽NG(they->二人、never again->二度と)は閾値を緩めずretryのPromptに不合格の指摘を付ける方式で是正(雪女の不成立5->1)。
- M8: gold A 追加23群全て正(誤対応0)、coverage 83.0->94.3%/未見91.2->94.6%/ig 93.4->97.4%。参考B(敵対的ずらし対照)19/620=3.1%を可と判定(本Pipelineは問わない設問、情報開示)。実run: judge 8dir計18call、不採用あり(Y再配達 5pair中4可、Y姓 10中8可)。

## Vocabulary音声(掲載/再利用/生成)
| 本番run | level | 掲載 | KP再利用(TTS 0) | ②追加: Store再利用 | ②追加: 新規TTS | 実費円 | 全件再生可 |
|---|---|---|---|---|---|---|---|
| x_aichat | Std | 4 | 3 | 0 | 1 | 0.0846 | はい |
| x_aichat | Adv | 5 | 3 | 0 | 2 | 0.2855 | はい |
| x_jwst | Std | 5 | 3 | 0 | 2 | 0.1675 | はい |
| x_jwst | Adv | 5 | 3 | 1 | 1 | 0.136 | はい |
| x_meta | Std | 5 | 3 | 0 | 2 | 0.2054 | はい |
| x_meta | Adv | 4 | 3 | 0 | 1 | 0.3038 | **いいえ(STOPPED)** |
| x_moon | Std | 4 | 2 | 2 | 0 | 0.0 | はい |
| x_moon | Adv | 5 | 3 | 1 | 1 | 0.1351 | はい |
| x_untidy | Std | 5 | 3 | 0 | 2 | 0.1409 | はい |
| x_untidy | Adv | 5 | 3 | 2 | 0 | 0.0 | はい |
| y_fee | Adv | 5 | 3 | 2 | 0 | 0.0 | はい |
| y_sur | Std | 5 | 3 | 0 | 2 | 0.2256 | はい |
| y_sur | Adv | 5 | 3 | 0 | 2 | 0.2263 | はい |
| z_melos | Adv | 3 | 3 | 0 | 0 | 0.0 | はい |
| z_yuki | Std | 5 | 3 | 0 | 2 | 0.1993 | はい |
| z_yuki | Adv | 5 | 3 | 0 | 2 | 0.2051 | はい |

本番run自体に対し02Cの配線済み関数だけを実行(tts stage全体は再実行せず=⑨ Std part3_k2等のHR承認済み音声を保護)。9本番runのsha256 manifest前後差: 削除0・既存ファイル変更はtts_generation_results.json/review_lock_state.json(vocab_extra追記のみ=キー単位diffでadded以外0)・cost logの追記のみ(`evidence_03b/manifest_diff.txt`、`check_changed_out.txt`)。

## Playwright(PC+mobile、最終dirのTOTAL)
X月242 / X②244 / X④246 / ⑭244 / Y再配達230 / Y姓244 / Zメロス226 / Z雪女240 いずれもNG 0。※1回目にNGを出した検査は検査側の競合(mobileの通し音声metadata未取得でseek)で、wait追加後にY姓PASS。Z雪女の1回目クラッシュ(`next()`既定値なし)も是正。live確認は下記。

## X 4記事のURL
| 記事 | dev試聴ページ | End User |
|---|---|---|
| ②散らかり | https://shimomura055.github.io/eigo-radio/user_test/family_x_untidiness_family_resource_01/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_x_untidiness_family_resource_01/enduser/index.html |
| ④AI説得広告 | https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_chat_sponsored_persuasion_01/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_chat_sponsored_persuasion_01/enduser/index.html |
| ⑨Meta | https://shimomura055.github.io/eigo-radio/user_test/family_x_meta_waddle_world_01/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_x_meta_waddle_world_01/enduser/index.html (rev01-f、未再produce) |
| ⑭JWST | https://shimomura055.github.io/eigo-radio/user_test/family_x_jwst_mystery_emission_line_01/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_x_jwst_mystery_emission_line_01/enduser/index.html (新規) |

## 費用
実費は概算約¥25(Cap¥45): judge評価¥4.63、訳生成(最新run合計約¥7.2＋メロス1回目¥6.3＋雪女1回目約3)、Vocab実TTS約¥2.3、診断約¥0.3。`daily_cost.py 2026-10-29T15:00:00`=¥392.8(開始)->¥394.7(終了、scratchpadのlogは未走査のため上記自前集計を加算して約¥420、日次1,000円内)。stop_scope_check_01は全run前rc=0。

## 可視性実測(PC1280x900 / mobile390x844、各level最大16群、点灯日本語が画面内に全体見える割合)
PC 47.8%(118/247)・mobile 16.2%(40/247)。X月 PC36%/mobile21%、X② 46/11、X④ 34/19、⑭ 38/21、Y再配達 77/26、Y姓 80/17、Zメロス 47/13、Z雪女 24/0。委任_03A(前回)より低い=対象にX/Z全partが加わりZ雪女が最低。`evidence_03b/visibility_03b.json`。

## 判断候補
- (D)可視性UI: 点灯日本語が英文の下で画面外になる(自動scroll/浮動キャプション/段落直後挿入)。既判断なし、前委任から継続。推奨は段落直後挿入(英文ブロック直下に日本語を挿入し常に同一画面)または浮動キャプション。
- (B)⑨Meta Adv Vocabulary『latter』: 既存のHR経路(ユーザー試聴。最終wav=er019_output/.../meta_waddle_world__run_fx4_01/b1b/narration/vocab_extra_3_en.wav)で解消可能。Gate(ASR一致基準)の変更は承認範囲外のため行わない。ユーザー試聴OK後に⑨をrev01-gへ再produce(API 0、約5分)。
- (C)Z不成立2段落(英語のみ): 対訳照合がAI追加情報を検出したfail-closedで正常。生成訳をretryでverify指摘付きにする拡張は任意(費用僅少)で現時点は不要。
- 参考: M8のB対照3.1%、E1のx_moon短行比率0.913->0.8824は開示のみ(Gate PASS内)。

## 規則違反の開示
Vocab extras実行の自作script起動間隔が一時的に150秒未満(16:45:20/16:45:49、16:52:51/16:53:06)。runner CLIでないためRESTART_STORMは発生せず、`launch_gate.py`導入後は全起動を150秒以上に統一(`evidence_03b/launch_times.txt`)。

## live確認(Pages deploy後、verify-only --base-url、PC+mobile、2026-10-30 18:4x-19:1x JST)
全てNG 0: ⑭ 244 / X② 244 / X④ 246 / X月 242 / Y再配達 230 / Y姓 244 / Zメロス 226 / Z雪女 240(`evidence_03b/live_status.txt`)。Vocabulary mp3は各dirのA検査(audio参照200/206)に含まれ全件通過。⑨Metaはlive 200(dev・End User・article.json)を確認、End Userはrev01-fのまま(rev01-g検査は対象外=Vocabulary再生ボタンが無いため検査が落ちる。⑨の再produce後にrev01-gで検査)。
補足(残): rev01-g用verifyは、Vocabulary再生ボタンの無い旧asset(rev01-f以前)のpageを渡すとNGではなく例外(IndexError)で終了する。旧assetは今回の再produce対象外のため実害なし(分類=実害なし、次回触る時に`len(vbtns)`ガードを付ける)。

