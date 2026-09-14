# RESULT_PACKET_UT_TREND_2

管理ID: USER-TEST-AUDIO-COMPLETION-01-TREND-CONT1

## 1. 最終Status
**B1-B: 完成(Assembly PASS、Gate ON PASS、Web player+episode.mp3生成済み)。
A2: 未完成(STOP、片level)。** A2はFableの診断どおりMarkdownリンク除去等の
読み整形で`full_story_part1`/`full_story_part2`は解消したが、`point_two`が
読み整形後の新テキストでも既存Production安全装置(Human Review Cost Guard、
`er011_human_review_lock_01`)により1 attemptで`ASR_VALIDATION_UNCERTAIN`と
判定され自動ロック(以降0 API call)。approve_regenerate()は呼んでいない。

## 2. 読み整形一覧+語の追加削除なしの機械確認
`trend/audio/tts_reading_transforms.json`に集約。ルール3種:
markdown_link_strip(`[text](url)`→`text`)/alexaplus_symbol(`Alexa+`→`Alexa Plus`)/
natural_language_hyphen(`natural-language`→`natural language`)。適用segment:
A2=full_story_part1(link+Alexa+)/full_story_part2(link)/point_two(Alexa+)。
B1B=full_story_part1(link)/full_story_part2(link+Alexa+ +natural-language)/
point_one(Alexa+ +natural-language)。機械確認(SYMBOL_TRANSFORMSを逆適用した
新textの単語トークン列とMarkdownリンク表示テキストのみ残した原文の単語
トークン列が完全一致するかを`difflib`で独立検証)は全6segmentで**match=True**
(語の追加削除なし)。

## 3. B1B(4)原因特定結果
attempts_log突合により特定。`full_story_part1`=Markdownリンクのみが原因
(症状は「TTSがリンク周辺文でフレーズ順を毎回変える」不安定挙動、リンク除去で
即OK)。`full_story_part2`/`point_one`=Markdownリンク(part2のみ)+「Alexa+」→
ASRが「Alexa Plus」と正規化/「natural-language」→ASRがハイフンをスペースへ
正規化、の複合。`comment_4`=TTSは正しく読んでいるがASRが"assistants"を
"assistance"と3回とも同一箇所で誤認(ASR側の同音異義誤認、テキスト読み整形
では解決不可と判断し(d)のScaffold再生成で対応)。

## 4. comment_4再生成
旧(第1世代、診断対象): "Taken together, the points show that assistants may
take on more tasks, while the change itself is arriving at different speeds...
look at what they mean."(ASRが3回とも"assistants"を"assistance"と誤認)。
新(実際にASR検証・採用された音声のテキスト): "We have seen how assistants
may help connect several actions across devices, rather than simply respond on
a screen...bring these ideas together in the closing summary."
既存`er003_v1_b1_scaffold_01_generate.run_support_text`(run_b1_scaffold内部で
comment_4に使うのと同一関数)をcomment_4単体のみに直接呼び出し、
preview/comment_1-3は無変更。QA: scaffold_status=OK(1回で成功)、TTS=1 attempt目で
`verified=True`(ASR一致)。**運用上の不具合と是正**: consistency-check修正後の
再実行で本関数が非冪等(既にOKでも再度LLM呼び出し)だったため、
`b1_support_texts.json`のcomment_4が一時的に第3世代テキストへ上書きされ実際の
音声(第2世代)と食い違った(追加LLM費用¥0.17、追加TTS費用なし、音声[wav/mp3]
自体は一貫して正しい第2世代のまま変更なし)。本タスク内で検出し
`b1_support_texts.json`・`audit/comment_4_regeneration.json`を実音声と一致する
第2世代テキストへ復元、かつ`fix_b1b_comment_4()`へ`status=="OK"`時は
再生成しないresumeガードを追加して再発防止(再実行で0 API call確認済み)。

## 5. TTS(新canonicalでのattempt数・retry/fallback・lock非バイパス)
A2: full_story_part1/full_story_part2=各1 attemptでOK(既存標準+fallback機構は
内部で温存、追加retry不要)。point_two=1 attemptでASR_VALIDATION_UNCERTAIN→
即HUMAN_REVIEW_LOCKED(CONT1_ROUND_MAX=2の2巡目は0 API call、Gateが自動ブロック)。
B1B: full_story_part1/full_story_part2/point_one=各1 attemptでOK。comment_4=
1 attemptでOK。**lock非バイパスの説明**: `er011_human_review_lock_01.
check_before_generation()`はcanonical_text_sha256が前回lockと異なる場合
「canonical_text changed since last lock; treated as new version」として
proceed=Trueを返す仕様(L229-232確認済み)。読み整形により該当segmentの
canonical_textが変わったため、旧lockエントリはそのまま(削除・編集なし)で、
新テキストに対する通常の初回TTS/ASRとして進行した。approve_regenerate()は
一度も呼んでいない。

## 6. Audio Validation Gate結果
B1B: gate_off=PASS(Assembly成功、duration=364.734s peak=0.88541
clipping=False)、gate_on(`verify_episode_audio_validation_gate`、opt-in
必須構造チェック)=PASS。A2: point_two未解決のためAssembly未到達
(gate_off/gate_on とも未実施)。

## 7. 完成episode duration
B1-B: 364.734秒(約6分5秒)。A2: 未算出(未完成)。

## 8. 記事⇔音声一致確認
B1B: `article_audio_consistency.json`の`all_pass=True`(content segment14件+
Key Phrase5件すべてOK/verified、article.md再読込→`split_article_text()`再実行の
結果がparts.jsonとbyte-identical)。加えて本タスクで
`reading_transforms_applied_segments=[full_story_part1, full_story_part2,
point_one]`・`reading_transforms_word_safety_all_pass=True`・
`comment_4_regenerated=True`を追記し、読み整形前原文との差分が
`tts_reading_transforms.json`記載の置換のみであることを機械確認済み。
**base driver(前回タスクの`run_trend_audio_completion.py`)の
`build_consistency_check()`にB1B固有のバグを発見**: `key_phrases`辞書の
Japanese sub-keyがA2は`japanese_meaning`だがB1Bは`japanese`であり、B1B実行時に
`KeyError: 'japanese_meaning'`で例外(base側ファイルは前回タスクの成果物のため
無変更のまま、本タスクの新規ファイル`run_trend_audio_completion_2.py`内に
`build_consistency_check_fixed()`としてロジック同一・キー名解決のみ両対応にした
修正版を実装し使用)。A2: 未到達(未完成のため)。

## 9. mp3一覧・player・URL・gitignore確認
B1B: mp3合計28件(episode 1件+segment 27件)、合計6.49MB、
`all_under_50mb=True`。episode.mp3=4.113MB/364.734s。
`player.html`内`src=`/`href=`属性にfile:///・絶対パス(C:\)は0件
(grep該当1件は本文説明文中の「file:///・絶対パス不使用」という日本語注記のみ、
実リンクではないことを確認)。`git check-ignore`はexit 1(mp3は無視されない、
コミット対象)。予定URL: raw.githubusercontent.com経由でcommit後に確定
(本タスクではcommit未実施)。A2: player/web未生成(0件)。

## 10. 費用
本タスク(CONT1)実費=**¥38.00**(内訳: tts_a2_reading_fix=¥26.22[A2の
full_story_part1/full_story_part2成功分+point_two 1 attempt分]、
scaffold_b1b_comment4_fix=¥0.17[運用不具合による1回分の余分な呼び出し込み]、
tts_b1b_comment4_fix=¥1.77、tts_b1b_reading_fix=¥9.84)。上限¥100以内
(超過なし)。B1Bレベル累計(前回¥122.15の一部+本タスク)=¥160.16
(`cost_summary_audio.json`、前回task失敗のためA2/B1Bとも当時
`update_shared_outputs`未到達=本ファイルは本タスクが初めて生成)。
**Trend Production 1生成セット総原価=¥174.03(本文)+¥160.16(B1B音声化、
Gate PASS済み完成分)=¥334.19**(A2音声化分は未完成のため含まず、完成後に
加算予定)。

## 11. model_id/TTS model
前回runと同一Production経路(model_id変更なし)。テキストLLM(Scaffold):
`gpt-5.6-luna`(openai、SUPPORT_MODEL routing)。ASR: `gpt-4o-mini-transcribe`
(openai_asr、英語)。TTS: `gemini-2.5-pro-preview-tts`系(voice: Aoede英語/
Charon英語、既存A2/B1B構成のまま)。

## 12. Open Item候補
(a)【新規、本タスクで発見】`run_trend_audio_completion.py::
build_consistency_check()`のB1B key_phrases構造(`japanese`キー、A2は
`japanese_meaning`)非対応バグ。今回は新規ファイル内のローカル修正版で回避、
base側ファイルの修正はユーザー判断(このdriver自体を今後も使うか次第)。
(b) A-Family audio completionのTTS入力前処理: Markdownインラインリンク・
記号(+)・ハイフン複合語の読み整形が未実装(driver側で暫定対応、
Production[er003_v1_n3_01_tts_generate.py]側への恒久組み込みは未承認、
既存OPEN-135末尾への追記案: 「Markdownリンク記法・Alexa+等の記号・
natural-language等ハイフン複合語がTTS入力に残ると、ASR照合が構造的/
確率的に不一致になりHuman Review Cost Guardへ到達しやすい。恒久対応は
tts_safe_en()系関数への追加が候補、ユーザー承認要」)。
(c) A2 `point_two`は「Alexa+」→「Alexa Plus」のいずれの表記でもASR側の
書き起こし表記が安定しない(今回はASRが逆に「Alexa+」と書き起こし
`ASR_VALIDATION_UNCERTAIN`)。ブランド名の表記ゆれはtts_safe_en系の
既知パターン(healthspan/lifespan等)と同種だが、今回は双方向に揺れており
単純な一方向置換では解決しない。既存Human Review Cost Guardにより
ロックされたまま(USER_DECISION_REQUIRED: `approve_regenerate()`実行可否、
または辞書拡張方針)。

## 13. commit対象候補一覧(Git操作は本タスクでは未実施)
`er014_output/four_type_observation_01/trend/run_trend_audio_completion.py`
(前回タスク成果物、未コミットのまま残存、約49KB)/
`er014_output/four_type_observation_01/trend/run_trend_audio_completion_2.py`
(本タスク新規driver、約30KB)/
`er014_output/four_type_observation_01/trend/production_set_cost.json`
(更新、1.6KB)/`er014_output/four_type_observation_01/trend/audio/`配下の
JSON・html・mp3成果物(wav除外、非wav合計約7.6MB、うちB1B web mp3が6.6MB)/
`er014_output/four_type_observation_01/progress_log.md`(追記、b1b完了行が
運用不具合の再実行により2行[ほぼ同一内容]追加されている点に留意)/
`docs/pm/delegation_log/USER-TEST-AUDIO-COMPLETION-01-TREND-CONT1.md`+
`_check.json`。A2側成果物は未完成のため今回のcommit候補には含めない
(narration wav以外の中間JSONも中途半端な状態のため、Aユーザー判断でA2完成後に
まとめてcommitすることを推奨)。

## 14. T-0・事前指定外Read・STOP有無
T-0: PASS(`docs/pm/delegation_log/USER-TEST-AUDIO-COMPLETION-01-TREND-CONT1_check.json`)。
事前指定外Read: (1)`er003_v1_n3_01_tts_generate.py`のtts_safe_en/
tts_safe_news_en/generate_a2_segment_with_slowdown/generate_b1_segments近傍
(読み整形をどのTTS入力経路に噛ませるべきか、Markdown除去がProduction側で
既に行われていないことの確認に必要だった)。(2)`er003_v1_n3_01_scaffold_generate.py`
のrun_b1_scaffold/run_support_text近傍(comment_4単体再生成に使う既存関数の
正確な呼び出しシグネチャ確認に必要だった)。(3)`er003_v1_b1_scaffold_01_generate.py`
のCOMMENT_4_ROLE/run_support_text(同上)。
**STOP: あり(A2のみ)**。A2の`point_two`が読み整形後もHuman Review Cost Guardで
ロックされ未完成(ユーザー判断が必要: `approve_regenerate()`実行可否、または
「Alexa+」表記ゆれの恒久対応方針)。B1Bは完成・STOPなし。
