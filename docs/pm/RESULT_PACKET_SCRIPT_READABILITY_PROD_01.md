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
