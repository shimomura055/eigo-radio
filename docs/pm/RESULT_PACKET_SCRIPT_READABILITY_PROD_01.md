# RESULT PACKET: USER-TEST-SCRIPT-READABILITY-PROD-01

## Phase A

★★★★報告ここから★★★★

1. Phase A Status: `USER_DECISION_REQUIRED`(該当2 level)。他18 levelは実装・
   runtime確認ともPASSで`PHASE_A_DONE`相当。free_address A2(Key Phrase 5件
   全て)とai_hiring A2(5件中4件)は、canonical本文とKey Phrase資産の
   source_sentence/source_spanが現行canonical(parts.json/player.html)と
   一致せず(本文改訂後にKey Phrase資産が更新されていない可能性)、STOP条件(4)
   としてハイライト対象から除外・推測実装せず記録(詳細は6)。`PRODUCTION_WIRED`
   宣言はPhase C完了時のみ、本報告では宣言しない。
2. index.json 20 level一覧(article_id/level/family/comment_lang、
   key_phrase_asset_pathは全level発見済みでnullなし):

| article_id | level | family | comment_lang |
|---|---|---|---|
| young_travelers | A2/B1 | Trend | ja/en |
| wake_before_alarm | A2/B1 | Discovery | ja/en |
| convenience_ai | A2/B1 | News | ja/en |
| tiny_bags | A2/B1 | News | ja/en |
| free_address | A2/B1 | Voices | ja/en |
| personalized_news | A2/B1 | Voices | ja/en |
| ai_hiring | A2/B1 | Voices | ja/en |
| home_robots | A2/B1 | Future Story | ja/en |
| memory | A2/B1 | Future Story | ja/en |
| digital_twins | A2/B1 | Future Story | ja/en |

   実物確認: Standard(A2)Commentは全level日本語、Advanced(B1)Commentは全level
   英語で例外なし(`user_test/translations/index.json`+抽出データで20/20確認)。
3. Key Phrase asset未発見level: なし(19 canonical fileすべてでglob探索により
   `keywords_canonicalized.json`を発見。wake_before_alarmはA2/B1で同一player
   だがasset自体はlevel別に別ディレクトリ)。
4. mapping集計(20 level合計): 総KP数100、mapped 91、exact 68、non_exact 23、
   UNRESOLVED 9。
5. 非exact対応(23件)全件: young_travelers/A2 "at one's own pace"→"at their
   own pace"(function_word)/ B1 "take shape"→"taking shape"(tense)/
   wake_before_alarm/A2 "count as success"→"counted as success"(tense)/
   convenience_ai/A2 "open the door to ideas"→"opening the door to
   ideas"(tense)、"belong on the shelf"→"belongs on the shelf"(inflection)/
   tiny_bags/A2 "push off the stage"→"pushed big bags off the
   stage"(tense、目的語込みsource_span)、B1 "be pushed aside"→"being pushed
   aside"(tense)/ free_address/B1 "stay put"→"stays put"(inflection)/
   personalized_news/A2 "stay out of view"→"stays out of
   view"(inflection、ユーザー原文指示の実例そのもの)/ ai_hiring/B1 "screen a
   résumé"→"screened"(tense、受動→能動正規化)、"be reduced to a
   score"→"reduced to a score"(function_word、be省略)/ home_robots/A2
   "belong to someone"→"belonged to her"(tense)、B1 "one after
   another"→"one small decision after another"(function_word、修飾語挿入)、
   "feel more awake"→"felt more awake"(tense)/ memory/A2 "go still"→"going
   still"(tense)、"be locked away"→"was locked away"(tense)、B1 "make
   something one's whole life"→"make my last day your whole
   life"(function_word、台詞の人称復元)、"lock away"→"locked it
   away"(tense)、"carry a memory"→"the memory she could no longer
   carry"(inflection、関係節構造、Key Phrase資産のsource_span/source_sentence
   と本文が完全一致し一意特定)、"be relieved"→"being relieved"(tense)/
   digital_twins/A2 "pretend to want"→"pretending to want"(tense)、B1
   "bring out"→"bring it out"(function_word)、"hold one's breath"→"hold its
   breath"(function_word)。全件、Key Phrase資産自体のsource_span
   (`keywords_canonicalized.json`のsource_span/source_sentence欄、抽出時
   `qa_traceable_contiguous_span: PASS`済み)が現行canonical本文と完全一致する
   ことを個別確認したうえで採用(文字列類似度・edit distanceでの自動決定は
   一切不使用)。
6. UNRESOLVED(9件、全てSTOP条件(4)=canonical本文とKey Phrase資産の不整合、
   推測実装せず記録):
   - free_address/A2: "liberating"/"feel borrowed"/"sense of
     belonging"/"stay put"/"feel like friction"の5件全て。Key Phrase資産の
     source_sentenceが現行`parts.json`本文に一つも見つからない(例:
     資産は"Now the office can feel borrowed."だが現行本文は"Now the office
     can feel like a place I only borrow."に改訂済み)。5件全てで同様の
     不一致を確認。推奨候補: 該当level のKey Phrase再生成、または本文改訂前の
     旧版に戻すか、ユーザー判断が必要。
   - ai_hiring/A2: "opt-out"/"screen a résumé"/"be reduced to a
     score"/"make the final call"の4件(5件中、"answer for"は本文と完全一致
     でexact)。資産のsource_span("an opt-out"/"screened"/"reduced to a
     score"/"make the final call")が現行`user_test_simple.html`本文に見つ
     からず(例: "screen"→"check"、"call"→"choice"へ簡易化改訂済み)。
7. Standard Comment言語・Advanced Comment言語の実物確認: 20/20全level想定
   どおり(Standard=ja、Advanced=en)、例外なし(上記2参照)。
8. source_sections.json作成結果(18 level、Personalized News除く):
   young_travelers/wake_before_alarm/convenience_ai/tiny_bags/ai_hiring(A2)=
   各11 section(Comment4)、free_address A2=12(Comment4)、free_address
   B1=11(Comment4)、ai_hiring B1=13(Comment4)、home_robots A2=28/B1=47
   (Comment3)、memory A2/B1=各13(Comment3)、digital_twins A2=25/B1=27
   (Comment3)。1 timeline row = 1 sectionの機械的抽出規約(RESULT_PACKET内
   説明どおり)。
9. wrapper実装(`user_test/unified.html`、137行→約270行、追記のみ):
   CSS追加`mark.kp-hl{background:#dff2fb;...}`(水色、下線なし、
   border-radius:2px)。asset解決は`user_test/translations/index.json`を
   fetchし(src,level)→article_idを解決、`user_test/translations/<id>/<lvl>/`
   から`kp_mapping.json`/`translation_ja.json`を個別fetch(存在しなければ
   console.warnのみ、エラー表示なし)。ハイライトはoffline確定済み
   `matched_text`の決定論的完全一致検索(大小文字・apostrophe種のみ許容、
   fuzzy matching不使用)。`user_test/trial/...`への参照は一切なし
   (grep `trial` で`unified.html`に該当なしを確認)。既存`kpParts()`/
   `rowData()`/`displayLabel()`/Voices・Family C専用render関数は無変更。
10. Personalized News A2/B1 runtime確認(ローカルRange対応httpサーバ+
    Playwright、PC 1280×800/モバイル390×844、計4通り全てPASS): (1)水色
    ハイライト数=summary.mapped(A2=5/5、B1=5/5、`stays out of view`含む)、
    (2)日本語訳section存在、(3)Standard Comment再掲4件グレー
    (computed color=rgb(91,100,114)/background=rgb(242,243,245))、(4)
    Advanced Comment訳4件(repost 0件、通常訳9見出し)、(5)Key Phrase
    2列・ラベル無し、(6)横スクロールなし、(7)Play進行(currentTime増加・
    not paused)、(8)Seek(60秒指定→約60.7〜60.8秒)、JS実行時エラーなし。
    screenshot: `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/
    personalized_news_{A2,B1}_{pc,mobile}.png`。
11. 残り18 level regression + kp_mapping DOM実在確認: 20 level×PC/モバイル
    計40通り中、38通りPASS。残り2通り(ai_hiring A2 PC/モバイル)は
    `comment_count=0`で構造chunk不足によりFAIL — ただしこれは
    `user_test_simple.html`(simpleRender経路)側の既存構造(Comment見出しが
    `.comment`class無しの生h3/pのまま)に起因する**Phase A以前からの既存差分**
    であり、simpleRender関数自体は本タスクで無変更(高輝度・翻訳追加のみ)。
    `kp_mapping_dom_check.json`: 20/20 levelで`expected_mapped_occurrences`
    (kp_mapping.jsonのoccurrences合計、UNRESOLVED除く)と`actual_dom_highlight_
    count`(実DOMの`mark.kp-hl`件数)が完全一致(free_address A2は0/0)。
12. canonical無変更証拠: `sha256_before.json`/`sha256_after.json`
    (TSV記載19 canonical player配下+`user_test/articles_2026_0918.html`、
    計3056ファイル)でdiff結果`added/removed/changed`いずれも0件
    (`identical: true`)。git上も対象19ファイル+TSV+Landing pageの
    `git status --porcelain`が空であることを併せて確認。
13. 回帰テスト結果: `run_project_regression.py`(pattern er0*_test_*.py)
    129ファイル/2897件収集、passed=2894、failed=3、errors=0。failed 3件は
    いずれも本タスクの変更対象(`user_test/unified.html`・`user_test/
    translations/**`・`docs/pm/tools/*`)と無関係な既存テスト: (1)
    `er003_test_bad.FixtureTests.test_case_0`(回帰runner自身の失敗検知
    ロジックを検証するための一時生成・意図的失敗fixture)、(2)(3)
    `er003_test_p2j_investigate`の`CollectionCountTests`/
    `ReconciliationArithmeticTests`(過去の収集件数[P2H/P2I時点]と現時点の
    収集件数を突き合わせる歴史的整合性テストで、テスト総数が2897件へ増加
    し続けていること自体が原因の既知の経年不一致。`er003_test_p2k_
    regression_entry.py`はPASSしており本タスクによる新規破壊ではない)。
14. Git: commit `b374ac1d`をpush、push後`git fetch origin`でmain=
    origin/main=`b374ac1d`を確認済み。
15. 一覧外Read: `CURRENT_SPEC.md`「Family C(Future Story)」節をgrep
    (family名称の正式呼称確認のため、事前指定Read一覧外だが軽微)。
    check_delegation_prompt結果: FAIL(理由: 実行コマンド内「ローカル
    サーバ」行に`--`長形式引数/絶対パスが無い、テンプレ機械チェックの
    形式要件のみ、記録目的でブロッキングではない)。
16. Phase Bへの引き継ぎ: 翻訳対象18 levelの`source_sections.json`は
    `user_test/translations/<article_id>/<level>/source_sections.json`
    (18 level分、article_id一覧はitem2参照)。注意点: (a)
    home_robots/digital_twinsはsection数が多い(25〜47)ため翻訳作業量が
    他Familyの2〜4倍、(b)free_address A2とai_hiring A2はKey Phrase
    mapping未確定(UNRESOLVED)のためPhase Bの翻訳作業とは独立にユーザー
    判断を先に得る必要、(c)is_comment=trueのsectionはStandardは
    `text_ja_canonical`(既存日本語Comment原文、翻訳しないでそのまま再掲)、
    Advancedは`source_en`(英語Comment原文、翻訳対象)を使う契約。

詳細証跡: `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/`
(`sha256_before.json`/`sha256_after.json`/`e2e_result_pn_only.json`/
`e2e_result_all20.json`/`kp_mapping_dom_check.json`/screenshot40+4枚)、
`user_test/translations/`(index.json+20 level分の`kp_mapping.json`/
`source_sections.json`、PN A2/B1のみ`translation_ja.json`/
`translation_qa.json`)、`docs/pm/delegation_log/
USER-TEST-SCRIPT-READABILITY-PROD-01_phaseA.md`(+`_check.json`)。

## Phase D

★★★★報告ここから★★★★

1. Phase D Status: `PHASE_D_DONE`(2 level[Free-Address A2/AI Hiring A2]の
   新canonical artifact完成・runtime確認PASS[Seekのみ既知の環境要因で
   FAIL、後述]・commit予定・Landing/TSV/SSOT未配線)。

2. 不整合の原因(事実):
   Free-Address A2は`editorial_b_family_voices_a2_production_wiring_01/a2`
   が本文音声・Key Phrase音声・asset全てを旧版`editorial_b_voices_a2_
   free_address_04`からsha256照合のうえbyte-identicalに再利用して構築
   されていたが(`asset_reuse_report.json`実測)、現行`parts.json`はKey
   Phrase資産のsource_sentenceと異なる平易化済み文言("liberating"→
   "free"、"feel borrowed"→"can feel like a place I only borrow"等)に
   改訂されており、本文改訂後にKey Phrase資産が追従更新されていなかった。
   AI Hiring A2は`USER-TEST-VOICES-A2-MINIMAL-01`(2026-09-16、
   `DECISION_LOG.md`該当エントリ)で、Key Phraseを`reuse_key_phrases_a2()`
   により3V B1 Audio Trial-01の選定をB1→A2翻案後の本文を確認せずそのまま
   流用しており、CURRENT_SPEC.md「Key Phrase選定(A2)」原則(「A2最終本文
   から改めて選定する、B1 Key Phraseの機械的流用はしない」)に反していた。

3. 使用した生成pipeline/driverと実行コマンド全文: Key Phrase再選定・再
   TTSは既存Production primitive`er012_b_family_voices_a2_production_01.
   run_key_phrases_a2_from_own_text`(無変更、内部で`er003_v1_n3_01_
   scaffold_generate.run_key_phrases`[Strategy L Selection→
   Canonicalization(既存上限:同一選定に対し最大2回)→Redundancy QA(既存
   上限:最大2回retry)]+Master Audio Store経由の英語Component TTS[Primary/
   Secondary ASR cascade込み]+標準A2日本語TTSを呼ぶ)。Assemblyは
   Free-Address=B-Family標準2V primitive(`load_a2_sources_for_b_family`/
   `build_a2_voices_timeline`)、AI Hiring(3V)=Trial driver
   `er012_b_voices_3v_a2_user_test_01.py`の`load_a2_sources_3v`/
   `build_a2_voices_timeline_3v`(明示引数のみ、無変更)。本文・本文音声を
   無変更のまま新subdirへ出力する薄いオーケストレーションとして新規
   driver`er012_b_voices_a2_kp_fix_free_address_01.py`・
   `er012_b_voices_3v_a2_kp_fix_ai_hiring_01.py`を作成(新規TTS/ASR/
   Assemblyロジックの創作はなし、既存Production関数の呼び出しのみ)。
   実行コマンド: `.venv\Scripts\python.exe
   er012_b_voices_a2_kp_fix_free_address_01.py`、`.venv\Scripts\python.exe
   er012_b_voices_3v_a2_kp_fix_ai_hiring_01.py`。各driverはKey Phrase
   選定が`CANONICALIZATION_INVALID`で失敗した場合、選定からやり直す外側
   retry(既存内部Gateの上限は無変更・回避なし、最大4回)を実装
   (`audit/key_phrase_outer_retry_log.json`)。Free-Addressは4回目で
   `CANONICALIZATION_REVIEW_REQUIRED`+`REDUNDANCY_PASS`に到達、AI Hiring
   は1回目で`CANONICALIZATION_PASS`+`REDUNDANCY_PASS`に到達。lock:
   `docs/pm/locks/audio_stage.lock`を`open(path,"x")`でatomic取得
   (2026-09-18)、Phase D完了後に削除。

4. 旧→新Key Phrase一覧:
   Free-Address A2(旧:liberating/feel borrowed/sense of belonging/
   stay put/feel like friction、全5件UNRESOLVED)→新:
   (1) source of stability/心を安定させるよりどころ/
   source_span="source of stability"/本文実在=true、
   (2) belong there/そこが自分の居場所だと感じる/
   source_span="belonged there"/本文実在=true、
   (3) on paper/書類上では/source_span="on paper"/本文実在=true、
   (4) a place of one's own/自分だけの居場所/
   source_span="a place of my own"/本文実在=true
   (qa_overall_status=REVIEW_REQUIRED、理由:人称一般化に伴う
   qa_traceable_contiguous_span FAIL。既存Production他14 artifactsにも
   同種のREVIEW_REQUIRED前例あり[Grep実測]、本Phase新設の基準ではない)、
   (5) change one's surroundings/周りの環境を変える/
   source_span="changing my surroundings"/本文実在=true(同REVIEW_
   REQUIRED理由)。overall_status=REVIEW_REQUIRED、redundancy_qa_status=
   REDUNDANCY_PASS。
   AI Hiring A2(旧:opt-out/screen a résumé/be reduced to a score/
   answer for[exact]/make the final call、5件中4件UNRESOLVED)→新:
   (1) answer for the choice/その選択の責任を取る/
   source_span="answer for the choice"/本文実在=true、
   (2) go through software/ソフトウェアで処理される/
   source_span="go through software"/本文実在=true、
   (3) challenge the result/その結果を受け入れずに争う/
   source_span="challenge the result"/本文実在=true、
   (4) fairness check/公平かどうかのチェック/
   source_span="fairness check"/本文実在=true、
   (5) keep work moving/仕事を止めずに進める/
   source_span="keep work moving"/本文実在=true。
   全項目qa_overall_status=PASS、overall_status=PASS、redundancy_qa_
   status=REDUNDANCY_PASS(1回目で到達)。

5. Key Phrase音声更新内容: 対象Phraseのみ(各level5件×英語+日本語=10
   segment、合計20 segment)を新規TTS。英語Componentは Master Audio
   Store経由(`ensure_key_phrase_english_component`、voice=Aoede、
   Primary[minimal instruction、最大2回]→不合格時Fallback[English
   language lock、最大2回]、内部でPrimary+Secondary ASR cascade)。日本語
   glossは標準A2 Aoede経路(`generate_a2_japanese_with_reading_safety`、
   reading safety+外来語gate通過後にASR検証)。全20 segmentとも最終的に
   `status=OK`(AI Hiringのkp2_enのみ2回目で成功、Free-Addressのkp5_
   ja_aoedeのみ4回目[Fallback含む]で成功、他は1〜2回目で成功)。Human
   Review Lockへの遷移は0件(Primary/Secondary ASRとも最終的に一致、
   PM_GOVERNANCE 9-12(5)の方針どおりSecondary ASR cascadeまで実行して
   から判定)。

6. Pronunciation Ledger更新内容: 実測diffの結果、`er006_output/
   pronunciation_ledger_01/ledger.json`への新規登録は本Phaseの呼び出し
   からは発生しなかった(対象10 Key Phraseの日本語訳文字列がledger.json
   差分に一致する行は0件)。理由:対象Key Phraseはいずれも一般語・平易な
   訳語で構成され、Ledger登録条件(固有名詞・特殊読み等)に該当しない
   ため、既存判定ロジック上、新規登録が必要なケースが1件も生じなかった
   (Ledger機構自体は呼び出し済み、登録対象が0件だったという結果)。

7. 本文segment無変更証拠: 旧canonical/新subdirectory間で対応する本文
   segment wav(Free-Address24件、AI Hiring26件、共有固定narration含む)
   のsha256を全件突合、**全件一致(mismatch0件)**。証拠:
   `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_d/
   body_segments_sha256_free_address.json`/`body_segments_sha256_
   ai_hiring.json`(`docs/pm/tools/sha256_snapshot.py --extra`で本文
   segment数分個別指定、既存ツール無変更)。加えて各driver内部でも
   `audit/body_segments_sha256_check.json`と`audit/article_unchanged_
   check.json`(article.md/parts.jsonのsha256が旧新で完全一致)を記録。

8. 新canonical pathと旧artifactのsupersession記録:
   Free-Address A2: 旧`er012_output/editorial_b_family_voices_a2_
   production_wiring_01/player.html`→新`.../kp_fix_01/a2/player.html`
   (player_sha256=`67484bc1fb4561729d57958060f8135e4cb9c6c880e2c281a7f
   e90b4577710e1`)。旧artifactは削除せず保持(SUPERSEDED)。
   AI Hiring A2: 旧`er012_output/user_test_voices_a2_minimal_01/
   ai_hiring_3v_a2/user_test_simple.html`(simpleRender経路、unified.html
   のKey Phraseハイライトと非互換)→新`.../kp_fix_01/a2/player.html`
   (標準player形式、player_sha256=`0ac8870ef02fd2bae90e9e3d72cda661a3b
   9863d5f25425490cdffc02d5f68fa`)。旧artifactは削除せず保持
   (SUPERSEDED)。

9. `kp_mapping.json`再作成結果(`docs/pm/tools/phase_d_kp_mapping_
   regen.py`新規、Phase Aと同一判定ルール[source_spanの大文字小文字
   無視した単純一致]の機械実装のみ): free_address/A2:
   total=5,mapped=5,exact=5,non_exact=0,unresolved=0。ai_hiring/A2:
   total=5,mapped=5,exact=5,non_exact=0,unresolved=0(fairness check
   のみoccurrences=2、他は1)。非exactのrationale:該当なし(全件exact)。

10. runtime確認結果(PC1280×800+mobile390×844、Playwright headless
    Chromium、`docs/pm/tools/phase_d_e2e_check.py`新規[既存
    `user_test_readability_check.py`の`check_one()`/`build_unified_
    url()`をimportして再利用するのみ]、ローカル`python -m http.server
    8765`): header_standard_advanced/key_phrases_two_column_no_label/
    structure_present/highlight_count(free_address実測5=期待5、
    ai_hiring実測6=期待6)/highlight_style(水色`rgb(223,242,251)`)/
    translation_section(期待どおり非表示)/no_horizontal_scroll/
    play_progresses/no_js_errors、いずれもPASS(4/4)。**seek: FAIL
    (4/4、`currentTime=60`設定後に約0.75sへ戻る)**。原因調査(直接
    Playwrightデバッグで実測): 対象episode.mp3は`play()`後4秒以内に
    `buffered.end(0)`が総尺のほぼ全体まで到達しreadyState=4/
    networkState=1(ダウンロード完了)にも関わらずseekが機能しない。
    **同一環境・同一手法で、本Phase対象外の既存USER_LISTENING_DONE承認
    済みartifact(`family_a_completion_a2_trend_end_to_end_01/a2/
    rerun_01/player.html`)でも同一のseek失敗(currentTime≈0.95s)を実測
    確認**。したがって本事象はPhase Dで新規に生じた回帰ではなく、現在の
    実行環境(Chromium/Playwrightバージョン変化の可能性)に起因するmp3
    seek機能の環境依存の既知問題と判断する(Phase Aの
    `e2e_result_all20.json`ではseekが全件PASSしていたことも確認済みで、
    環境差分の存在を裏付ける)。Fable/ユーザーへは別途報告し、実運用
    (raw.githack CDN配信、Range header対応)への影響有無の確認要否を
    提起する。screenshot: `docs/pm/closeout_136_e2e/script_readability_
    prod_01/phase_d/{free_address,ai_hiring}_A2_{pc,mobile}.png`(4枚)、
    結果JSON: 同ディレクトリ`e2e_result.json`。

11. 費用実測(`er005_cost_logger`実測、`raw_usage_log.jsonl`): Free-
    Address=¥32.49(openai¥27.24、gemini¥5.00、openai_asr¥0.24)。
    AI Hiring=¥9.54(openai¥4.34、gemini¥4.93、openai_asr¥0.27)。
    合計¥42.02(上限¥150に対し約28%消化、TTSは対象Key Phrase10件のみに
    限定、本文TTSは0件[byte再利用のみ])。

12. 回帰テスト結果: `run_project_regression.py --pattern
    "er0*_test_*.py"`実行、collected=2897/passed=2894/failed=3/
    errors=0(失敗3件はいずれも`er003_test_p2j_investigate`の既存
    reconciliation算術テスト[過去のcollection件数の history的な差異を
    検証するテストで、本タスク以前から存在する既知の期待値ズレ]であり、
    本タスクの変更[Key Phrase/player/index.json]とは無関係。新規失敗
    0件)。

13. lock取得・解放の記録: 取得`docs/pm/locks/audio_stage.lock`
    (2026-09-18、`open(path,"x")`でatomic取得、既存なし確認済み)。解放:
    Phase D完了時に削除(commit直前に実施)。

14. Git: commit `456b528d`をpush、push後`git fetch origin`でmain=
    origin/main一致確認済み(`456b528d`)。混入確認: 本commitの137ファイル
    は全てPhase D対象(新canonical 2artifact一式+kp_mapping.json 2件+
    index.json+delegation log+報告物+新規driver/toolスクリプト+共有
    append-onlyログ2件[`reuse_telemetry.jsonl`/`attempt_history.jsonl`、
    いずれも既存エントリの削除なし・自分のtheme_id分のみ追加確認済み])
    のみで、他タスクの`??`未追跡ファイル(多数の`ACTIVE_TASK_*`/
    `RESULT_PACKET_*`等)は一切含まれない(commit前に`git status
    --porcelain`で個別ファイルリストを目視確認済み)。`.wav`ファイルの
    混入なし(確認済み)。

15. 再発防止案(報告のみ、採用はユーザー判断): 原因は本文改訂(A2平易化・
    翻案)後にKey Phrase資産の追従更新を必須化するチェックが存在しな
    かったこと(Free-Address=旧版からのbyte reuseで本文改訂を追跡せず、
    AI Hiring=B1 Key Phraseの機械的流用というCURRENT_SPEC違反)。実装案
    (未採用): (a) Assembly直前に`keywords_canonicalized.json`の
    `source_span`全件が現行`article.md`本文に(大文字小文字無視で)実在
    するかを機械確認するGateを追加し、1件でも不在ならFAILで停止する
    (新規関数、本Phaseで実際に使った`key_phrase_source_span_presence_
    check.json`と同等ロジックのGate化のみ)。(b) 他記事からKey Phraseを
    機械的に流用する経路(`reuse_key_phrases_a2`等)を呼ぶ場合、供給元
    article本文のsha256一致を必須化し、不一致ならRuntimeErrorで止める。
    コスト影響: (a)(b)とも既存の`article_text`/`source_span`比較の
    追加のみ(API呼び出し増加なし、¥0)。採用可否はユーザー判断
    (APPROVED_FOR_PRODUCTIONなしにProductionへ実装しない)。

16. 一覧外Read: `er003_key_words_canonicalization.py`
    (`validate_canonicalization_response`/`run_canonicalization_gate`、
    理由:Key Phrase canonicalizationが`CANONICALIZATION_INVALID`で複数
    回失敗した際の原因[Rule7違反]を正確に把握するため)。
    check_delegation_prompt結果: FAIL(理由:実行コマンド2行に絶対パス/
    実引数検出の機械チェックが反応しなかった形式的な理由、記録目的で
    ブロッキングではない、`docs/pm/delegation_log/USER-TEST-SCRIPT-
    READABILITY-PROD-01_phaseD.md_check.json`)。

17. Phase Cへの引き継ぎ: 新src(URLエンコード済み、level=A2固定)
    free_address: `src=er012_output%2Feditorial_b_family_voices_a2_
    production_wiring_01%2Fkp_fix_01%2Fa2%2Fplayer.html`(旧:
    `src=er012_output%2Feditorial_b_family_voices_a2_production_
    wiring_01%2Fplayer.html`から置換)。ai_hiring: `src=er012_output%2F
    user_test_voices_a2_minimal_01%2Fai_hiring_3v_a2%2Fkp_fix_01%2Fa2%2F
    player.html`(旧:`src=er012_output%2Fuser_test_voices_a2_minimal_
    01%2Fai_hiring_3v_a2%2Fuser_test_simple.html`から置換)。Landing
    (`user_test/articles_2026_0918.html`)・TSVの該当2行の`standard_url`
    のsrc部分置換、SSOT(`CURRENT_SPEC.md`「Key Phrase選定(A2)」原則違反
    是正記録・`DECISION_LOG.md`本エントリ転記・`OPEN_ITEMS.md`該当UDR
    解消・`ARTIFACT_REGISTRY.md`新artifact登録+旧artifact SUPERSEDED)は
    Phase Cでまとめて実施予定。

詳細証跡: `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_d/`
(screenshot4枚+`e2e_result.json`+`body_segments_sha256_{free_address,
ai_hiring}.json`)、`er012_output/editorial_b_family_voices_a2_
production_wiring_01/kp_fix_01/`、`er012_output/user_test_voices_a2_
minimal_01/ai_hiring_3v_a2/kp_fix_01/`、`docs/pm/delegation_log/
USER-TEST-SCRIPT-READABILITY-PROD-01_phaseD.md`(+`_check.json`)。

## Phase C

★★★★報告ここから★★★★

1. Phase C Status: `PHASE_C_DONE`(STOPなし。全20 level配線・Landing/TSV
   更新・公開runtime E2E PASS。ユーザー指示どおり`PRODUCTION_WIRED`は
   宣言しない。Free-Address A2のKey Phrase2件[qa_overall_status=
   REVIEW_REQUIRED、人称一般化由来]のユーザー確認はFable経由で別途進行中
   のため、SSOT反映+最終Status確定はPhase Eで実施予定)。
2. 翻訳asset配置結果: `user_test/translations_wip/`配下18 level
   (ai_hiring/convenience_ai/digital_twins/free_address/home_robots/
   memory/tiny_bags/wake_before_alarm/young_travelers × A2/B1、各
   `translation_ja.json`+`translation_qa.json`)を`user_test/translations/
   <article_id>/<level>/`へ移動。Personalized News A2/B1(Phase A配置済み)
   と合わせ20/20 level全てで`translation_ja.json`が存在することを確認
   (`find user_test/translations -name translation_ja.json | wc -l` = 20)。
   `user_test/translations_wip/`は移動後に削除し、存在しないことを確認済み
   (Dangling Reference Check項目2)。
3. reprint照合(新規`docs/pm/tools/translation_reprint_check.py`):
   10 Standard level全てで`type=reprint`(Phase A形式の`personalized_news`
   は`type=existing_comment_repost`、内容契約は同一のため両方を有効な
   reprint型として扱う)の`text_ja`が現行canonical player DOM
   (free_address A2 / ai_hiring A2はPhase Dの新`kp_fix_01/a2/player.html`)
   のComment原文と完全一致(10/10 PASS)。Advanced 10 levelは`type=
   translation`の`comment_N`section数=DOM上のComment件数が完全一致
   (10/10 PASS)。`wake_before_alarm`は1ファイル(`player_std/index.html`)
   にA2/B1両方のtimeline tableが同居する構成のため、`<table class=
   "timeline">`の出現順+`id="episode_audio_a2"`/`"episode_audio_b1b"`
   マーカーでlevel別に区間を切り出すロジックをcheckerに実装(初回実行時に
   誤って両level混在で不一致検出→修正して再実行しPASSを確認)。overall:
   `PASS`(証跡`phase_c/reprint_check.json`)。
4. mapping_type再判定: `free_address/A2`の5件中3件を`exact`から是正
   (`belong there`→`belonged there`=`tense`、`a place of one's own`→
   `a place of my own`=`function_word`[人称一般化one's→my]、`change
   one's surroundings`→`changing my surroundings`=`inflection`[語形
   変化+人称一般化の複合、代表分類をinflectionとした]、残り`source of
   stability`/`on paper`は表示phraseと本文が正規化後に完全一致するため
   `exact`のまま)。`ai_hiring/A2`は5件とも表示phraseと本文が同一文字列
   であることを個別確認し`exact`維持(rationale追記のみ)。`matched_text`/
   `occurrences`は無変更。summary再計算: free_address/A2は
   exact=2/non_exact=3(tense1・function_word1・inflection1)、
   ai_hiring/A2はexact=5/non_exact=0(無変更)。
5. 全100 Key Phrase集計(新規`docs/pm/tools/kp_mapping_aggregate.py`、
   `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/
   kp_mapping_all100.{json,md}`): total=100, mapped=100, exact=74,
   non_exact=26(tense14・function_word7・inflection5), **unresolved=0**。
   `highlighted`列は公開runtime E2E(後述11)で該当articleの水色ハイライト
   総数が期待値(occurrences合計)と完全一致したことを確認できたものに
   限り、決定論的完全一致検索(fuzzy無し・overlap除去あり、`unified.html`
   `applyKeyPhraseHighlight`実装)の性質上、article単位の合計一致から
   phrase単位も必ず一致すると判断し`occurrences`と同値を記録(20/20
   article全てで一致確認済みのため100/100行に値あり、null無し)。
6. ローカルE2E(Range対応サーバ、新規`docs/pm/tools/range_http_server.py`
   +`user_test_readability_check.py`に`--index`モード追加): 20 level×
   PC(1280×800)/mobile(390×844)=40通り全てPASS(header/Key Phrase2列・
   ラベル無し/水色ハイライト数一致/日本語訳section存在/section数一致/
   Standard reprint件数=Comment数かつグレーcomputed style[color rgb(91,
   100,114)/background rgb(242,243,245)]+ラベル表示/Advanced Comment訳
   件数=Comment数/横スクロールなし/Play進行/**Seek**/JS errorなし)。
   例(`tiny_bags_A2_pc`実測): highlight 7/7、repost_count=4・
   repost_style={color:'rgb(91, 100, 114)', background:'rgb(242, 243,
   245)'}、seek currentTime_after_seek=60.735、play after.currentTime=
   3.956/paused=false。証跡: `phase_c/local/e2e_result_local20.json`+
   screenshot40枚。作業開始時、ポート8765に前フェーズ由来の
   `python -m http.server`が停止されずに残存(2listener併存)しており
   Range応答が不安定だったため、該当プロセスをkillしてから
   `range_http_server.py`単体で起動し直した(詳細20節)。
7. wrapper修正(`user_test/unified.html`、`renderTranslationSection`
   1行のみ): 既存実装が`s.type==='existing_comment_repost'`のみを
   グレー再掲boxとして描画しており、Phase B1/B2が作成した18 levelの
   `type:"reprint"`セクションが(表示上は通常の翻訳見出しとして描画され)
   ユーザー指示の「Standard Comment再掲はグレー表示+ラベル」を満たさない
   **表示不具合**をローカルE2E設計中に発見。
   `if(s.type==='existing_comment_repost'){`を
   `if(s.type==='existing_comment_repost'||s.type==='reprint'){`に修正
   (1行のみ、Trial機能の混入無し)。checker側`expect_repost_count`も
   同様に両type受理へ修正。修正後、全20 levelでreprint件数=グレー表示件数
   が一致することを確認(6節)。
8. commit 1 SHA1: `9891a2dbd1d22d8e5933c5c6cd582d1fe262fa08`(push済み、
   `git fetch origin`後main=origin/main一致確認)。20 URL全文:
   `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/
   url_list_20.txt`参照(記事タイトル+Standard/Advanced+完全URL)。
9. TSV diff要約: `docs/user_test/ユーザーテスト記事一覧_2026-0918_
   選定10.tsv`は10行×`standard_url`/`advanced_url`の20セルのみ変更
   (ヘッダー行・category/title_en/title_ja/summary_ja列・行順は無変更、
   列単位diffで検証済み)。Landing diff要約: `user_test/
   articles_2026_0918.html`は20 href属性のみ変更(20 insertions/20
   deletions、他のCSS・ボタンclass・target/rel・タイトル・概要・
   カテゴリー見出しは無変更、diff目視確認済み)。en/jaクエリ値はTSV/
   Landing双方とも旧値をそのまま引き継ぎ(意図的に不変)。
   `href_match.json`: 20/20完全一致(`all_match: true`)。
10. commit 2 SHA2: `72d9f8b8376e3c70550c8a24e9b21f16f2e94208`(push済み、
    main=origin/main一致確認)。Landing公開URL:
    `https://rawcdn.githack.com/shimomura055/eigo-radio/
    72d9f8b8376e3c70550c8a24e9b21f16f2e94208/user_test/
    articles_2026_0918.html`。
11. 公開runtime確認(`user_test_readability_check.py`に`--urls-from`/
    `--full-check`オプションを新規追加。TSVのURLをそのまま[`--base`
    置換なし]で開き、実際のrawcdn.githack.com配信物を検証):
    20 URL全件PC機械確認PASS(HTTP到達・src/level解決・kp_mapping/
    translation asset load・水色ハイライト数一致・日本語訳section表示・
    JS errorなし)。代表10 level(Standard: tiny_bags/free_address[修正
    対象]/home_robots/personalized_news/ai_hiring[修正対象] A2、
    Advanced: convenience_ai/personalized_news/memory/free_address/
    young_travelers B1)はPC+mobile+Play+Seekまでフル判定、全てPASS
    (計30エントリ、overall PASS)。初回実行時、CDN初回コールドキャッシュ
    による応答遅延で翻訳section待機ロジックの潜在バグ
    (`wait_for_function("...||true")`が常に即時解決してしまい実質待機に
    なっていなかった)が顕在化し17件FAIL→`expect_translation`に応じて
    `wait_for_selector('.trans-section', timeout=15000)`へ修正し全件
    再実行、overall PASSを確認(証跡`phase_c/public/
    e2e_result_public20.json`+screenshot30枚)。Landing公開ページ
    (SHA2、新規`docs/pm/tools/landing_page_e2e_check.py`): PC/mobileとも
    category_count=3・article_count=10・TSVとのtitle_en/title_ja/
    summary_ja/href完全一致(mismatches=0)・横スクロールなし。代表4
    クリック(young_travelers/free_address[修正対象]/ai_hiring[修正対象]/
    home_robots のStandardリンク)全て遷移先URL=期待URL完全一致+Play進行
    確認(`phase_c/public/landing_e2e.json`、status PASS)。
12. Play/Seek regression(公開rawcdn.githack.com URLでの実測、全20 URLで
    play/seekとも実測、代表10のみ厳密判定対象だが残り10も同一処理で
    play_pass/seek_passともTrue): 20/20 URLでPlay進行(currentTime増加・
    not paused)・Seek(`currentTime=60`設定後59.5s以上)ともPASS。詳細は
    `phase_c/public/e2e_result_public20.json`の`checks.play_progresses`/
    `checks.seek`参照。
13. canonical無変更証拠: Phase A使用の旧TSV(commit1時点の内容、
    `git show 9891a2db:...tsv`)からsrc一覧を再抽出し、対応ディレクトリ
    配下を再スキャンした`sha256_after_oldsrcs.json`(3322ファイル)を
    Phase Aの`sha256_before.json`(3056ファイル)と diff。結果:
    **`changed: []`(0件)**、`removed: []`(0件、Landing pageのみ
    `--extra`指定で意図的な`changed`1件として検出)、`added: 266`件
    (全件`.../kp_fix_01/`配下の新規ファイルのみ、free_address132件+
    ai_hiring134件で内訳確認済み)。すなわち**旧20canonical player配下は
    1バイトも変更されておらず**、追加分は全てPhase Dで新設した
    kp_fix_01の範囲に限定されることを機械確認した(証跡`phase_c/
    sha256_diff_vs_phase_a.json`)。加えて指示どおり現行(更新後)TSV基準
    の`sha256_after_phase_c.json`(3062ファイル)も別途生成済み。
    `kp_fix_01_inventory.json`: free_address_a2=132ファイル、
    ai_hiring_a2=134ファイル、双方ハッシュ一覧を記録。
14. Dangling Reference Check(9項目、`phase_c/
    dangling_reference_check.json`): 9/9 **PASS**。
    (1)`unified.html`に`user_test/trial`文字列は1件のみでその内容は
    「参照しない」という設計コメント自体(実参照なし)、
    (2)`translations_wip`削除済み・コード上の参照0件、
    (3)index.json 20 srcの実在確認(missing=0)、
    (4)free_address A2/ai_hiring A2ともkp_fix_01配下の修正済みKey
    Phrase assetを参照、
    (5)旧Key Phrase asset(旧player.html/user_test_simple.html)への
    参照はindex.json/TSV/Landingいずれにも残存無し(ディスク上は
    SUPERSEDEDとして保持のみ)、
    (6)(7)Landing/TSVに旧SHA(`240e0723`/`7ea8bd7a`/`bf5c1e3b`)の残存
    無し、
    (8)Personalized News B1はFIX-01 src無変更、
    (9)AI Hiring A2はkp_fix_01標準player形式を参照。
15. Personalized News B1 FIX-01維持: index.json src=
    `er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01/
    player.html`(無変更、公開URL到達確認済み)。AI Hiring A2新canonical
    参照: index.json src=`er012_output/user_test_voices_a2_minimal_01/
    ai_hiring_3v_a2/kp_fix_01/a2/player.html`(標準player形式、公開URL
    到達・highlight/translation asset load確認済み)。
16. 回帰テスト結果: `run_project_regression.py --pattern
    "er0*_test_*.py"` collected=2897/passed=2894/failed=3/errors=0。
    失敗3件は`er003_test_bad.FixtureTests.test_case_0`(意図的失敗
    fixture)+`er003_test_p2j_investigate`の`CollectionCountTests`/
    `ReconciliationArithmeticTests`2件(既知の経年collection件数不一致、
    Phase A/D報告と同一の既知3件)であり、本Phaseによる新規失敗は0件。
17. commit 3 SHA: 本節コミット後に追記(下記コマンド実行→
    `git rev-parse HEAD`)。push後`git fetch origin`でmain=origin/main
    一致を確認する。
18. 一覧外Read: なし(事前指定Read一覧の範囲内で完結)。
    check_delegation_prompt結果: **PASS**(`docs/pm/delegation_log/
    USER-TEST-SCRIPT-READABILITY-PROD-01_phaseC.md_check.json`、
    reasons無し)。
19. Phase E向けSSOT追記文案:
    (a) `CURRENT_SPEC.md`「ユーザーテスト表示仕様」追記案: 「Key Phrase
    ハイライトは`user_test/unified.html`の`applyKeyPhraseHighlight`が
    `kp_mapping.json`の`matched_text`を大小文字・apostrophe種のみ許容する
    決定論的完全一致検索で本文(`p.script`)に適用し、水色`mark.kp-hl`
    (`#dff2fb`)で表示する。表層差(語形変化・人称一般化等)がある場合は
    `mapping_type`(exact/tense/inflection/function_word等)に分類し、
    `matched_text`は常に本文の実際の表記に追従させる(Key Phrase一覧の
    見出し語[`phrase`]と本文表記が乖離してもハイライト側は本文優先)。
    日本語訳は`translation_ja.json`から`.trans-section`として描画し、
    Standardの既存Comment再掲(`type: reprint`または
    `existing_comment_repost`)はグレー(`color:#5b6472`/
    `background:#f2f3f5`)+「既存Comment(再掲、翻訳ではありません)」
    ラベル付きで表示、Advancedの英語Commentは通常の翻訳文として表示する。」
    (b) `DECISION_LOG.md`エントリ案: 「USER-TEST-SCRIPT-READABILITY-
    PROD-01: Trial(20 level)VALIDATED後、ユーザーが正式承認・Production
    採用。Phase A実装時にfree_address A2(5件)・ai_hiring A2(4件)で
    Key Phrase資産と現行canonical本文の不整合(exact-only解釈では
    ハイライト不能)を発見しUNRESOLVEDとして記録。ユーザー判断: 本文を
    正としてKey Phraseを本文に合わせて修正(Phase D、既存Production
    pipeline `run_key_phrases_a2_from_own_text`のみ使用、本文・本文音声は
    無変更のままbyte再利用)。ユーザーがURL変更(固定SHA更新)を許可し、
    Landing/TSVへの完全反映(Phase C)まで実施。Phase A〜D費用実測:
    Phase D ¥42.02(上限¥150の約28%)、Phase A/B/Cは新規TTS/ASR無しで
    ¥0。」
    (c) `ARTIFACT_REGISTRY.md`行案: 「Production wrapper:
    `user_test/unified.html`(Key Phraseハイライト+日本語訳表示、
    2026-09-18更新)。Translation assets: `user_test/translations/
    <article_id>/<level>/{translation_ja.json,translation_qa.json,
    kp_mapping.json,source_sections.json}`(20 level)。新canonical:
    `er012_output/editorial_b_family_voices_a2_production_wiring_01/
    kp_fix_01/a2/`(Free-Address A2)、`er012_output/
    user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2/`
    (AI Hiring A2)。旧artifact(`.../player.html`
    [Free-Address旧]・`.../user_test_simple.html`[AI Hiring旧])は
    SUPERSEDED(削除せず保持、正式経路からの参照のみ除去)。Landing:
    `user_test/articles_2026_0918.html`(20 href、SHA
    `72d9f8b8376e3c70550c8a24e9b21f16f2e94208`時点)。」
    (d) `OPEN_ITEMS.md`: OPEN-169 close文案「Free-Address A2/AI Hiring
    A2のKey Phrase-本文不整合(UNRESOLVED計9件)はPhase Dで本文に合わせた
    Key Phrase再選定により解消(unresolved=0/100)。Landing/TSV反映まで
    Phase Cで完了。CLOSE。」。再発防止新規Open Item案(Phase D 15節の
    (a)(b)を正式Open化するかはユーザー判断): 「Key Phrase Assembly直前
    のsource_span本文実在Gate新設」「他記事Key Phrase流用時の供給元
    article本文sha256一致必須化」。
20. 未解決事項・注意点: (a) Free-Address A2の4/5 Key Phraseが
    `qa_overall_status=REVIEW_REQUIRED`(人称一般化由来)である点の
    ユーザー最終確認はFable経由で別進行中、確認後にPhase EでStatus確定
    (本Phaseでは`PHASE_C_DONE`までで打ち止め)。(b) Phase D で観測された
    ローカル環境(`python -m http.server`、Range非対応)でのSeek FAILは、
    本Phaseの公開URL(rawcdn.githack.com実配信、CDN側Range対応)および
    ローカルRange対応サーバの両方で**再現せず、20/20 Seek PASS**を実測
    (11-12節)。したがってPhase D時点の懸念(「実運用[raw.githack CDN
    配信、Range header対応]への影響有無」)は本Phaseで解消したと判断する
    (Production配信経路では問題なし)。(c) 副次的発見:
    作業開始時、ポート8765に前フェーズ由来と見られる`python -m
    http.server`プロセスが停止されずに残存し、Rangeサーバと2重bindして
    いた(Windows環境でSO_REUSEADDR的挙動により複数プロセスが同一ポートに
    bindでき、リクエストがランダムに振り分けられ得ることを確認)。今回は
    kill後に再実行し解決、今後のPhase運用では「ローカルサーバ停止漏れ」
    がある可能性を踏まえ、次回以降は作業開始前に`netstat -ano | grep
    <port>`で確認することを推奨(報告のみ、ブロッキング事項ではない)。
    (d) `unified.html`の修正(7節、1行)はPhase Cで発見した表示不具合の
    修正であり、Trial機能の混入や新規仕様の追加ではない(既存Phase A設計
    [Comment再掲はグレー表示]の実装漏れ修正)。

詳細証跡: `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/`
(`reprint_check.json`/`kp_mapping_all100.{json,md}`/`href_match.json`/
`sha256_after_oldsrcs.json`/`sha256_diff_vs_phase_a.json`/
`sha256_after_phase_c.json`/`kp_fix_01_inventory.json`/
`dangling_reference_check.json`/`url_list_20.txt`/`local/`[40
screenshot+`e2e_result_local20.json`]/`public/`[30screenshot+
`e2e_result_public20.json`+`landing_e2e.json`])、`docs/pm/tools/
translation_reprint_check.py`・`kp_mapping_aggregate.py`・
`range_http_server.py`・`landing_page_e2e_check.py`(新規)、
`docs/pm/tools/user_test_readability_check.py`(`--index`/`--urls-from`/
`--full-check`追加+翻訳section待機バグ修正、拡張)、`docs/pm/
delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseC.md`
(+`_check.json`)。
