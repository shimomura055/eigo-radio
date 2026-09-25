# NEWS-FAMILY-X-POINTLESS-TRIAL-01_REPORT.md

管理ID: NEWS-FAMILY-X-POINTLESS-TRIAL-01 / Phase B(Sonnet実行、2026-09-26)

Trialのみ。Production Prompt/Validator/Production path/SSOTへは一切実装
していない。Family A(既存Point構造)の全ファイル(`er003_v1_n3_01_*`・
`er012_e_family_entertainment_two_level_runner_01.py`・
`er003_v1_b1_scaffold_01_generate.py`・`er003_v1_iran01_a2_generate.py`
等)は1行も変更していない(§2でgit diff証跡を示す)。新規出力は
`er019_output/family_x_pointless_trial_01/`配下のみ。設計書:
`docs/pm/recon_family_x_pointless_trial_01.md`(Phase A、commit
5abe72b1)。

## §1 実際に生成したFamily X構造

対象: Meta記事、B1(Advanced)レベルのみ。Writer再実行なし(既存
`er012_output/e_family_two_level_wiring_01/meta/b1b/article.md`の
Main Story部分のみを流用、Point節は内容ごと完全に破棄)。

構造(実測segment列、非pause、16件):
```
Intro → Welcome(Charon) → Topic intro(Charon) → Notification 1 →
Preview intro(Charon) → Preview(Charon) → Full story intro(Charon) →
Comment 1(Charon) → Full Story Part 1(Aoede) →
Comment 2(Charon) → Full Story Part 2(Aoede) →
Comment 3(Charon, Bridge to Part 3) → Full Story Part 3(Aoede) →
Comment 4(Charon) → In One Line(Aoede) → Outro(Charon)
```
Point One/Two・Point Notification効果音・Key Phrase(intro/1-5/
Notification 2・3)は一切含まない。Comment数は4のまま。

3分割語数(実測、`parts.json`): part1=39語、part2=40語、part3=48語
(合計127語、最大-最小差=9語=総語数の7.1%、既存2分割[Meta実績で
68/59語、差13.4%]より均等)。

## §2 Family Aとの差分(ファイル・関数・行)

新規作成のみ(既存Family Aファイルへの追記は0件、設計書A-3で検討した
「共有ファイルへの2箇所追記」案は不要と判明したため採用しなかった。
理由: `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]`・
`verify_episode_audio_validation_gate()`は実際に生成されたsegment名
にのみ照合するため、Family Xが生成しないpoint_one_heading等は単に
無視され、Key Phrase Source Gateも`key_phrases`が空dictのため
`NOT_APPLICABLE`になる。既存関数を無変更のままimportして呼ぶだけで
Family Xを成立させられた)。

- `er019_family_x_pointless_scaffold_01.py`(新規): `split_article_
  text_3way()`(2分割ロジックの3分割一般化)、`FAMILY_X_COMMENT_3_ROLE`/
  `FAMILY_X_COMMENT_4_ROLE`(Point前提を除去した新role)、
  `run_family_x_b1_scaffold()`。Comment 1/2 role・`run_support_text`・
  `PREVIEW_ROLE`は`er003_v1_b1_scaffold_01_generate.py`(b1s)から無変更
  のままimport。
- `er019_family_x_pointless_tts_01.py`(新規): `generate_family_x_b1_
  segments()`、`regenerate_family_x_b1_segment()`(単一segment再試行用)。
  低レベル生成関数(`voice01.generate_charon_english`/`news_tail_fix.
  generate_news_narration_wide_margin`/`shared_narration.ensure_fixed_
  english_segment`/`n3_tts.tts_safe_*`)は無変更のままimport。
- `er019_family_x_pointless_assemble_01.py`(新規): `load_family_x_b1_
  sources()`/`apply_family_x_b1_gain()`/`build_family_x_b1_timeline()`/
  `stage_assemble_family_x_b1()`。`asm.verify_episode_audio_validation_
  gate()`/`asm.assemble_with_timeline()`/`asm.apply_headroom_safety_
  valve()`/pause定数/gain定数は`er003_v1_n3_01_assemble.py`(asm)から
  無変更のままimport。
- `er019_family_x_pointless_runner_01.py`(新規): E2E runner(dry-run/
  writer/scaffold/tts/assemble/player stage、`--budget-jpy`/`--tts-mode`/
  `--batch-reason`)。コスト計算(`compute_cost_jpy_so_far`/`assert_
  budget_ok`)は`er012_e_family_entertainment_two_level_runner_01.py`
  から読み取り専用でimport(コピーしない、単一正本を維持)。
- `er019_family_x_pointless_01_test_01.py`(新規、unit test 10件)。

git diff証跡(Family A側12ファイル、実行結果):
```
$ git status --porcelain -- er003_v1_n3_01_scaffold_generate.py er003_v1_n3_01_assemble.py \
  er003_v1_n3_01_tts_generate.py er012_e_family_entertainment_two_level_runner_01.py \
  er003_v1_b1_scaffold_01_generate.py er003_v1_iran01_a2_generate.py audio_review_player.py \
  er006_audio_cost_pilot_02_shared_narration.py er003_v1_sing01_voice01_generate.py \
  er003_v1_sing01_news_tail_fix.py er003_b1_p9a_audio.py er005_cost_logger.py
(出力なし。差分0件)
```

## §3 E2E runtime evidence

実行順: dry-run → writer → scaffold → tts → assemble → player(全stage
実行、`.venv/Scripts/python.exe er019_family_x_pointless_runner_01.py
--slug meta --out-dir er019_output/family_x_pointless_trial_01/meta
--budget-jpy 35`)。TTS_EXECUTION_MODE=STANDARD(既定、BATCH未使用)。

- dry-run: API呼び出しなしでsegment一覧・件数を出力
  (`er019_output/family_x_pointless_trial_01/meta/dry_run_report.json`)。
  planned_llm_text_call_count=5、planned_tts_segment_count=10、
  Key Phrase/Point系0件・Family A既存出力への書き込みなしを事前確認。
- writer: ¥0(既存article.mdの3分割のみ、API呼び出しなし)。
- scaffold: Comment1-4+Preview生成、5 API call、¥0.34(openai)。
- tts: 10 segment TTS生成、9件`OK`(ASR Validated)・1件
  `HUMAN_REVIEW_LOCKED`(comment_4、詳細§6)。
- assemble: `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`(comment_4=
  UNVALIDATED)によりGATE_BLOCKED。既存Audio Validation Gate
  (`asm.verify_episode_audio_validation_gate`、無変更)が正しく作動。
  override無し、`run_summary_assemble.json`へ`GATE_BLOCKED`を記録し
  停止(既存runnerと同一パターン)。
- player: `er019_output/family_x_pointless_trial_01/meta/player.html`
  生成。Full episode audioは未完成のため、個別segment単位(10件、
  comment_4含む)のtable+`<audio>`要素を表示。

累計費用(実測、`raw_usage_log.jsonl`): **¥16.52**
(openai=¥0.34, gemini=¥15.38, openai_asr=¥0.80)、予算上限¥35以内。

## §4 tests/validators

Unit test(`er019_family_x_pointless_01_test_01.py`、API呼び出しなし、
fixtureのみ)、`.venv/Scripts/python.exe -m unittest
er019_family_x_pointless_01_test_01 -v`実行結果: **10 tests, OK
(全件PASS)**。
- `FamilyAUnchangedTest`: Family A 12ファイルのgit working tree差分
  ゼロを確認。
- `SplitArticleText3WayTest`: 3分割Volumeバランス(閾値35%以内)・
  Point節破棄・段落不足時のRuntimeErrorを確認。
- `PointWordingAbsenceTest`: Comment 3/4 role文言にPoint語彙が
  残存しないこと、検出器自体が機能することを確認。
- `TimelineHasNoPointSegmentTest`: timelineにPoint/Key Phrase文字列が
  無いこと、Comment3→Part3→Comment4→In One Lineの順序、
  `assemble_with_timeline`が実際に動作することを確認。

実データ実行結果(実測、API呼び出しあり):
- Audio Validation Gate(`asm.verify_episode_audio_validation_gate`、
  無変更): comment_4以外の9segmentがVALIDATED、comment_4がUNVALIDATED
  (HUMAN_REVIEW_LOCKED、未承認)と正しく判定、assembly全体を正しく
  ブロック。
- disfluency QA: preview/comment_1-4(disfluency_qa=True指定)・
  in_one_line(同)に適用、`disfluency_checked=True`が記録されている
  ことを`tts_generation_results.json`で確認。
- Connected Speech Equivalence Layer/Repetition QA: full_story_part1-3
  に適用(Sonnet判断でpart3にも拡大、§6参照)。
- Human Review Lock(ER-011-HUMAN-REVIEW-COST-GUARD-01、既存無変更
  モジュール): comment_4が3回のTTS/ASR試行(cumulative_tts_
  attempts=3)を使い切った後、自動的にHUMAN_REVIEW_REQUIREDへロックされ、
  以後の自動再試行(2回目の`regenerate_family_x_b1_segment`呼び出し)は
  0 API callでブロックされることを実測確認(既存安全装置が正しく機能、
  Sonnet側で回避・上書きしていない)。
- grep(旧Point誘導表現の残存確認): `grep -rniE "point one|point two|
  point 1|point 2|第一に|第二に"` を`parts.json`/`b1_support_texts.json`
  に対して実行、**0件ヒット**。

## §5 ユーザー試聴リンク

player.html(ローカルpath、gitで追跡・push予定):
`C:\Users\tensh\eigo-radio\er019_output\family_x_pointless_trial_01\meta\player.html`

音声ファイル(`*.wav`)は本リポジトリの`.gitignore`方針
(`*.wav`除外、Family A側と同一方針)によりgit追跡外・push対象外の
ため、raw.githubusercontent.com URLは提供できない。ローカルで
`player.html`をブラウザで開くと、各segmentの実際のscriptテキストと
共に`<audio controls>`要素からその場で再生できる(ローカルfile:///
URL参照、Family A player.htmlと同一の再生方法)。comment_4は3回分の
attempt音声(`narration/attempts/comment_4_attempt{1,2,3}_
englishstyleprefix.wav`)も個別に保存済みで、いずれもASRが
"points"[複数形]と書き起こした実際の音声を試聴できる。

Full episode(1本にassembleされたwav)は§6の理由により未生成。

## §6 発見した問題

1. **comment_4がHuman Review Lockで終端(音声完成物としては未完成)**:
   生成テキスト"...Now, let's bring the main point together."
   (canonical、単数形"point"、"Point One/Two"という構造ラベルではなく
   一般的な英語慣用句)に対し、TTS音声を3回生成したが、ASRは3回とも
   一貫して"points"(複数形)と書き起こした(`asr_text`実測: 3回とも
   "...main points together"に近い形)。既存のASR Validation retry
   (最大3回)を使い切った後、既存のHuman Review Lock(ER-011-HUMAN-
   REVIEW-COST-GUARD-01、無変更モジュール)が正しく作動し、
   `HUMAN_REVIEW_LOCKED`へ終端した。Sonnetはこの安全装置を独自判断で
   回避・上書きしていない(2回目の再生成試行[`regenerate_family_x_
   b1_segment`]はLockにより0 API callで即ブロックされることを実測
   確認)。**Fable/ユーザーが実際に聴取し、(a)このまま承認[record_
   human_approval]するか、(b)Comment 4のテキストを言い換えて
   再生成するかを判断する必要がある**(このためfull episode wavは
   本Trialでは未完成、個別segmentは全10件試聴可能)。Family A側の
   既存Comment 4("...hear the main point.")も同種の"the main point"
   慣用句を使っているが、たまたまASRで問題化しなかった可能性がある
   (Point構造の廃止自体とは無関係な、TTS/ASRの一般的な既知揺れ)。
2. **Point節の情報損失(ユーザー指示どおりの結果、実装ミスではない)**:
   `comparison_meta_b1.md` §4の文単位対照により、Meta記事のPoint One
   (「ピアノの中に隠れた演者」という比喩+「人間の助けは悪いことでは
   ない」という評価的解説)・Point Two(プライバシー懸念、Meta従業員の
   懸念、**Metaが機能を一時停止したという事実そのもの**)は、いずれも
   Main Story(part1〜3)に一切含まれておらず、Family Xでは完全に
   失われることを確認した。特にPoint Twoの「機能一時停止」は記事の
   ニュース価値の一部であり、単なる文体上の重複ではない。ユーザー
   指示「Point節は内容ごと破棄する」に厳密に従った結果であり、設計
   判断の妥当性(この情報損失を許容するか)はユーザー判断が必要。
3. **3分割後の1パートが元のpart1/2より短くなる(設計書A-3で事前予見
   済み、実測で確認)**: part1=12.4秒/part2=15.7秒/part3=20.3秒
   (Family AのPart1=23.0秒/Part2=27.5秒より短い)。極端に不自然な
   短さではないが、音声テンポとしては明確に速くなる(§7-7参照)。
4. **Sonnet判断による1点の裁量拡大(報告のみ、独自実装ではない)**:
   full_story_part3に、既存Production承認済みのConnected Speech
   Equivalence Layer(OPEN-122)・Repetition QA(OPEN-121)を、既存の
   full_story_part1/2と同じ扱いで適用した(既存の承認対象segment名
   リストにfull_story_part3という名前自体は無いため、Sonnetが「同種の
   body segmentである」という判断で適用範囲をこのTrial内でのみ拡大)。
   判定基準自体は無変更、QAをより厳格に適用する方向の判断であり、
   新しい検証ロジックの追加ではない。Fable/ユーザーの確認事項として
   明示する。

## §7 受入条件チェックリスト

(Sonnetがユーザー指示原文から抽出した15項目。Fableが別途正本の
15項目を持つ場合は照合を依頼する。)

| # | 項目 | 判定 |
|---|---|---|
| 1 | Family A側ファイル(共有Production含む)への変更ゼロ | ○(§2 git diff証跡、12ファイル差分0件) |
| 2 | 対象記事=Meta、レベル=B1(Advanced)のみ | ○ |
| 3 | Writer再実行なし、既存article.mdのMain Storyを流用 | ○(writer stage ¥0、API呼び出しなし) |
| 4 | Point節(内容含む)を完全破棄 | ○(§6-2で内容損失を実測・報告) |
| 5 | 3分割ロジックはsplit_article_textのn=3一般化(段落境界・語数差最小化) | ○(実測39/40/48語、差7.1%) |
| 6 | Comment 1・2は無変更で流用 | ○(b1s.COMMENT_1/2_ROLEをそのままimport) |
| 7 | Comment 3・4はPoint前提を除去した新role(Bridge to Part 3/Story Recovery) | ○(実測生成テキスト§2/comparison_meta_b1.md §2) |
| 8 | Comment数は4のまま(増減なし) | ○ |
| 9 | In One Lineは既存流用(新規生成なし) | ○(Family A版と同一テキスト) |
| 10 | Point_*系segment・Point Notification効果音を一切含まない(新規効果音追加もなし) | ○(unit test + timeline実測で確認) |
| 11 | Key Phrase生成を行わない | ○(`key_phrases: {}`、API呼び出し・segment生成とも0件) |
| 12 | 予算上限¥35以内 | ○(実測¥16.52) |
| 13 | TTS_EXECUTION_MODE=STANDARD、BATCH禁止 | ○(BATCH未使用) |
| 14 | 実行前にdry-run(API呼び出しなしのsegment一覧・件数出力)を実施 | ○(§3、dry_run_report.json) |
| 15 | Unit test(3分割Volume・Point文言不在・timeline point_*不在・Family A無変更)全件PASS | ○(10 tests OK) |

補足(上記15項目には含まれないが重要な事実): Full episode(1本の
assembled wav)は**未完成**(comment_4のHuman Review Lockにより
GATE_BLOCKED、§6-1)。これは受入条件の「安全装置を回避しない」という
暗黙の前提には合致しているが、「完成音声の試聴」という意味では
未達であることを明示する。

[Fable注記] 受入条件「E2Eで音声まで完成」は**×**(未達)。comment_4の
canonical "bring the main point together" をASRが3回ともHuman Review
Lock(ER-011、無変更)で正しく終端しGATE_BLOCKEDとなったため。個別
segmentはplayer.htmlで試聴可能だがfull episode wavは未生成。安全装置は
回避していない(正しい挙動)。(Sonnet判定「VALIDATED(条件付き、上限)」は
上記のとおり残す。)

## §8 QCD

- Quality: Comment 1-4/Preview/Full Story Part1-3/In One Lineの
  9segmentはASR Validated(OK)。comment_4のみHuman Review待ち。
  Point内容の損失あり(§6-2)。
- Cost: ¥16.52(予算¥35の47%)。
- Delivery: 実装(新規4モジュール+test)からdry-run/E2E実行/比較資料/
  REPORTまで単一セッションで完了。Full episode audioの完成のみ
  Human Review待ちで持ち越し。

## §9 Sonnet仮分類

**VALIDATED(条件付き、上限)**。判定根拠: 15項目中15項目○(Family A
無変更・Point構造の完全排除・予算・dry-run・unit testいずれも実測で
確認)。ただし以下2点はユーザー/Fable判断が必要であり、これらの判断が
出るまでは「Family Xという設計が有効に機能する」という結論の完全な
確定ではない(USER_DECISION_REQUIRED相当の残課題として明示):
(a) comment_4のHuman Review(承認 or 言い換えて再生成)、
(b) Point節の情報損失(特にPoint Twoの「機能一時停止」という事実)を
Family Xという設計として許容するか。

## §10 Fable評価

(1)Family X構造(Point系0・Key Phrase0・本文3分割39/40/48語・Comment4本・
In One Line維持・効果音/リード/ブリッジ新規追加なし)はユーザー指示どおり
成立。Family A側12ファイル無変更(git status差分0)、共有ファイルへの
追記もゼロ。unit test 10件PASS。費用¥16.52(上限¥35内、STANDARD TTS)。

(2)受入条件のうち「E2Eで音声まで完成」は**未達**: comment_4のcanonical
"bring the main point together" をASRが3回とも "points" と書き起こし、
Human Review Lock(ER-011、無変更)で正しく終端(GATE_BLOCKED)。個別
segmentはplayer.htmlで試聴可能だがfull episode wavは未生成。安全装置は
回避していない(正しい挙動)。

(3)Point文言チェックの弱点: grepは "Point"/"point one/two" を対象と
しており、comment_4の "main point" は検出外。Point構造ラベルではない
慣用句だが、ユーザー要件「旧Pointへの誘導表現が残っていない」の趣旨
からは避けるべき語で、Comment生成時に "point" という語自体を避ける
扱いが必要かはユーザー判断。

(4)**最重要**: 入力選定の誤り(Fable決定に起因)。Family A版Meta記事の
Main Storyのみを流用しPoint節を内容ごと破棄したが、comparison_meta_b1.md
の文単位対照で、Point One/Twoの本文(特に「Metaが機能を一時停止した」
というReuters由来の事実)はMain Storyに含まれない物語本体の情報であり、
Family Xではこの情報が失われた。これはユーザー指示「Point内容を本文3へ
移植しない」の帰結ではなく、Meta記事ではFamily A contractが物語本体の
一部をPoint節へ押し込んでいたことによる。Family Xの本来の入力は
「Point contractなしの元記事全文」(例: NEWS-JA-TO-EN-ADAPTATION-TRIAL-01
arm3のAdvanced Natural adaptation全文、sha256 20b7ac01…)であるべきで、
その3分割ならPoint節への移植ではなく元本文そのものの分割になる。

(5)Sonnet裁量: full_story_part3へOPEN-121/122のConnected Speech
Equivalence/Repetition QAを同種body segmentとして適用範囲拡大。Fable
判定: Trial内では妥当(Production変更なし)。ただしFamily X仕様化時に
明記が必要。

(6)Volume: 3分割は均等(39/40/48)だが記事が127語と短く、1パート約40語は
音声として短い。200語級記事での再確認が望ましい。

## §11 分類

**USER_DECISION_REQUIRED**(構造は成立したが、E2E音声未完成[Human
Review Lock]と入力選定に起因する情報欠落があるため、VALIDATEDにしない)。

ユーザー判断事項:
①入力を「Point contractなしの元記事全文」(arm3 Advanced adaptation)に
差し替えて再実行するか(Comment再生成+TTS、¥20以内見込み。Fable推奨:
**実施**。理由: 現状の比較はFamily A版に対して情報量で不利であり、
Family Xの本来評価にならない)。
②comment_4 "main point" の扱い: Human Review承認で通すか、Comment生成で
"point" という語を避けるか(Fable推奨: ①の再実行で再生成されるため、
再実行時に "point" 語をComment promptの禁止語にせず、結果を観察。ただし
ユーザーが「point という語自体を避ける」を要件にするなら明示)。
③A2レベルも同様に実施するか(¥15〜20、Fable推奨: ①の結果後)。
④200語級のNews記事(hanshin等)でも1本試すか(Fable推奨: ①③後)。
