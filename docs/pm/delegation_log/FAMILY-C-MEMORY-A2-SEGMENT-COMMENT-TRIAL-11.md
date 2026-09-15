## 管理ID

`FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11`
並行タスクなし(直近commit `88e4e05d`)。報告は`docs/pm/RESULT_PACKET.md`(上書き)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: Family C「The future of memory」A2限定の**仕様変更Trial**(ユーザー承認済み)。目的2点: (1) Story TTS segmentの細切れによる音色・tone・声の強さの不連続を減らす、(2) A2 Commentをメタナレーション(「聞いてみましょう」型)から英文理解ガイドへ変更。加えて兄の台詞Voiceを男性的な既存承認Voiceへ変更。
- 到達上限Status: `VALIDATED候補 / USER_LISTENING_PENDING`。結果が良くてもFamily C Production仕様へ自動採用しない(Production反映はユーザー別途判断)。
- **旧成果物保存**: 既存Trial-10成果物(`er013_output/family_c_episode_trial_10/memory_a2/`配下、`er013_family_c_episode_trial_10_memory_run.py`)は**一切上書き・編集しない**。新出力先`er013_output/family_c_episode_trial_11/memory_a2/`と新スクリプト`er013_family_c_episode_trial_11_memory_run.py`(trial_10 memory版の複製)を作る。旧Comment Prompt(`COMMENT_*_ROLE_JA`)は新スクリプト内に`_TRIAL10_PREV`接尾辞等で残し比較可能にする。
- **本文固定**: `er013_output/family_c_future_trial_08/memory/reader_facing_article.txt`固定。Story本文の再生成・変更禁止、Writer再実行禁止。本文sha256=`a9a646a798bfe44b632038c790d58680a3b278979ac39473339cace2733b2ea2`(Trial-10記録値)と一致することを検証・報告。
- 対象外: Digital Twins、Memory B1、Home robots、Discovery、B1 Comment、Production正式Prompt(`er003_*`/`er012_*`)、`CURRENT_SPEC.md`。
- 禁止: Opus使用、Writer再生成、新規A/B大量比較、複数候補Commentの大量生成(Comment 1〜3は各1回生成。品質不足時のみ同一Promptで最大1回再生成)、新Validator設計、Production-wide segmenter実装、hard capのValidator実装、不要な全音声再生成(Intro/Outro/SFX/Welcome/Key Phrase/Preview/日本語タイトル/topic_intro等の既存正常assetはTrial-10からコピーして再利用、再TTSしない)、無関係なRepo監査、新Voice探索・大規模Voice比較Trial、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: ¥50(Story再segment TTS+Comment LLM/TTS+ASR)。超過見込みならSTOP。
- STOP条件(ユーザー指定): Story本文変更が必要/既存承認Voice候補に男性的Voiceがない/新segmentationでもTTSの重大欠落が繰り返す/120語以内程度に収めてもなお重大なTTS不安定が繰り返す(既存cascade 標準2+fallback1を超える)/大幅な追加コスト/Production正式仕様変更が必要。それ以外の軽微な問題はMemory A2範囲で最小個別修正して完成音声まで進める。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

ユーザー原文(2026-09-16)を要約せず引用:

---
目的: Family C / Memory A2について、ユーザー試聴で顕著だった以下2点を改善し、新しい試聴用音声まで作成する。Story内でTTS segmentごとに音色・tone・声の強さが変わり、不自然に聞こえる/A2 Commentが英文理解の助けにならず、「聞いてみましょう」「耳を澄ませて」のようなメタナレーションが多い。今回はMemory A2のみを対象に仕様変更Trialを行う。Digital Twins、Memory B1にはまだ展開しない。今回到達してよい上限: VALIDATED候補 / USER_LISTENING_PENDING。今回の結果が良くても、Family C Production仕様へ自動採用しない。

1. 既存成果物を必ず保存: 現在のMemory A2音声・player・segment・Comment等は、比較可能な旧版として保持する。既存Trial-10成果物を上書きしない。新しい出力先を作り、旧版と新版の両方を残す。本文 er013_output/family_c_future_trial_08/memory/reader_facing_article.txt は固定。Story本文は再生成・変更しない。Writerを再実行しない。

2. Story TTS segmentation仕様を変更する: 今回の主目的は、TTSを細かく分割しすぎることで生じる音色・tone・声の強さの不連続を減らすこと。現状のstory_xxx設計をそのまま使わず、Memory A2について分割を見直す。新Trial方針: Story segmentは、できるだけ自然な連続発話としてまとめ、必要な理由がある場所だけ分割する。分割してよい主な理由: 話者Voiceが変わる/Comment挿入位置/長すぎてTTS安定性が落ちる可能性が高い/scene / semantic boundaryとして自然に切る必要がある。避けること: 1文だけ、数語だけ、1単語だけの独立TTS/単純に段落が変わったという理由だけで毎回分割/同じVoiceが連続するのに細かく分割/引用符があるという理由だけで、同一Voiceの短い台詞を単独TTSにする/前後とつながる短い発話を切り離す。特に、同じAoedeが連続して読む部分は可能な限り同一TTSにまとめる。

3. Segment長のTrial用安全ガイド: 正式な「○語以上はNG」というProduction閾値はまだ存在しない。経験則: 約188〜198語の長segmentで語置換・後半block omissionなどの不安定事例あり/約270語級ではretryコストも大きい/Family Cでは60〜100語程度のsegmentは運用実績あり/数語〜1文だけの短segmentは音色・tone変化が目立ちやすい。したがって今回のTrialでは、概ね100語以内を基本目安とし、120語を大きく超えないようにする。150〜200語級のsegmentにはしない。これはProduction正式仕様ではなく今回のMemory A2 Trial用安全ガイド。固定のhard capとしてValidatorへ実装しない。分割時は、単純なword countだけでなく、同一Voiceの連続性/scene / semantic boundary/前後の流れ/Comment挿入位置/不自然に短いsegment回避/TTS安定性を総合して決める。

4. Lenaの兄のVoice: 「Do not make my last day your whole life,」はLenaの兄のVoice。現在のVoiceはユーザー評価で男性らしく聞こえない。既存承認済みVoice候補の中から、明確に男性的に聞こえるVoiceを選ぶ。新規Voice探索・大規模Voice比較Trialはしない。既存候補だけで決める。適切な男性Voiceが既存候補にない場合のみSTOPして報告。

5. A2 Comment仕様変更: 現在のCommentは「静かに聞いてみましょう」「耳を澄ませてみましょう」「耳を傾けてください」のような、聞く行為自体を促す文が多く、英文理解への実質的な助けが弱い。新しい役割: 次に聞く英文を理解しやすくするために、状況・人物関係・場面転換・重要な選択肢のうち、本当に必要な情報だけを短く日本語で整理する。Commentは「雰囲気作り」ではなく英文理解のためのガイドとする。良い方向性の例: 「扉が開き、マラはピアノの前へ進みます。エコーに任せるかどうか、緊張の高まる場面です。」このように、今どこにいるか/誰が何をしているか/次の英文理解で重要な状況/何が選択・対立点なのか、を簡潔に示す。禁止(原則使わない): 聞いてみましょう/耳を傾けて/耳を澄ませて/注目してみましょう/これからどうなるでしょう/雰囲気だけの抽象的な誘導/Story本文を聞けば分かるだけの無内容な予告。また、結末を先に言わない/新しいFactを加えない/不要な解説をしない/長文化しない。

6. Comment 1も同じ基準: Comment 1を単なる「これからレナの物語を聞きましょう」にしない。Story開始時点で理解に必要な具体的状況を簡潔に整理する。Comment 2 / 3も同様。今回はComment 1〜3すべて再生成する。B1 Commentは変更しない。

7. Comment Prompt自体をTrial用に更新: Memory A2 Trial用Promptを修正し、上記思想を反映する。ただし、Production正式Promptにはまだ反映しない。今回のMemory A2 Trial内だけで使用。旧Promptも残し、比較可能にする。

8. 音声化: 新segmentation + 新CommentでMemory A2を完成音声まで作る。必要工程: Story segment再構成/Brother Voice変更/Comment 1〜3再生成/必要segmentのみTTS/Assembly/Audio Validation/player生成。既存正常asset(Intro/Outro/SFX/Welcome/Key Phrase/Preview/その他変更不要音声)は最大限reuse。Story Writer / Key Phrase / Previewは再実行しない。

9. Token / Cost Guard: Claude週間利用枠は約91%使用済み。禁止: Opus使用/Writer再生成/新規A/B大量比較/Digital Twinsへの展開/Memory B1への展開/新Validator設計/Production-wide segmenter実装/不要な全音声再生成/無関係なRepo監査/複数候補Commentの大量生成。必要最小限のSonnet作業で完了させる。

10. 今回は恒久実装しない: TTS segment最小/最大長/automatic segment balancing/同一Voice連結ルール/Dialogue segmentation/Family C全体のComment Prompt の正式Production仕様化は、今回しない。必要ならOpen Itemとして候補だけ記録。

11. 受入条件: 旧Memory A2成果物が保存されている/Story本文shaが旧版と一致/Writer再実行なし/新segmentationで極端な短segmentが削減されている/同一Voice連続部分の不要な細切れが減っている/Trial安全ガイドとして概ね100語以内、120語を大きく超えず、150〜200語級を作っていない/Brotherの台詞が男性的Voiceになっている/Comment 1〜3が新しい理解補助方針になっている/「耳を澄ませる」「聞いてみる」型Commentがない/Assembly成功/Audio Validation実施/新player公開/実際に使用したVoice / model / routing証跡あり/API費用報告あり。

12. 完了報告: Segmentation(旧segment数/新segment数/旧最短・最長word count/新最短・最長word count/各新segmentのおおよそのword count/どの短segmentを統合したか/どの境界を残したかと理由/100語目安・120語超回避が実際にどう適用されたか)、Comment(旧Comment 1〜3→新Comment 1〜3を並べて提示)、Voice(Brother旧Voice/新Voice)、Audio(duration/Audio Validation/新player URL/direct audio URL/今回追加費用)、PM(StatusはUSER_LISTENING_PENDING/Production採用はしていない/今回発見した恒久課題・Open Item候補)。

STOP条件: Story本文変更が必要になる/既存Voice候補に男性的Voiceがない/新segmentationでもTTSの重大欠落が繰り返す/120語以内程度に収めてもなお重大なTTS不安定が繰り返す/大幅な追加コストが必要/Production正式仕様変更が必要になる。それ以外の軽微な問題は、今回のMemory A2範囲で最小個別修正して完成音声まで進める。
---

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_UT06_B.md`: 12-21行(Trial-10 memory A2の構成: 15 story segment[narrator11/device2/brother2]、Voice割当、Comment位置C2=段落8/9境界・C3=段落23/24境界、旧Comment全文は`memory_a2/comments_ja.md`)
- `er013_output/family_c_episode_trial_10/memory_a2/comments_ja.md`: 全文(旧Comment 1〜3、報告で並記)
- `er013_output/family_c_episode_trial_10/memory_a2/segments.json`: 全文(旧15 segmentのid/voice/raw_text/word count算出元。旧最短/最長word countはここから算出)
- `er013_output/family_c_future_trial_08/memory/reader_facing_article.txt`: 全文(29段落、384語。新segment設計の対象)
- `er013_family_c_episode_trial_10_memory_run.py`: Grepで`def build_all_story_segments|def split_paragraph|def classify_quote_voice|kind|"split"|story_%03d|story_` →story segment構築ロジック範囲Read(新segmentation実装の差し替え箇所)、Grepで`COMMENT_1_ROLE_JA|COMMENT_2_ROLE_JA|COMMENT_3_ROLE_JA|COMMENT_ROLES|PREVIEW_ROLE_JA`→Comment Prompt定数範囲、Grepで`BROTHER_VOICE|DEVICE_VOICE|MOTHER_VOICE|VOICE_NAME|tts_narrator|tts_device|tts_brother|generate_.*_english`→Voice割当・TTS関数範囲、Grepで`comment_placement|def place_comments|C2|C3|story_007|story_013`→Comment挿入位置ロジック範囲、Grepで`OUT_DIR|ARTICLE_ID|V1_DIR|reuse|\.ok`→出力先・resumable/reuse機構範囲(全文Readは構造変更に必要な場合のみ許可、理由をRESULT_PACKETに記録)
- `CURRENT_SPEC.md`: Grepで`承認Voice|Voice候補|Approved Voice|Aoede|Charon|Erinome|Fenrir|Puck|Orus|Kore|Zephyr`→既存承認Voice候補一覧の該当行のみRead(男性的Voiceの特定。候補が見つからない場合はDECISION_LOGを同Grep)。
- `docs/pm/PM_GOVERNANCE.md`: Grepで`15-8`→該当節(費用報告)
- `docs/pm/PM_BRIEF.md`: 135-159行(ACTIVE_TASK固定ヘッダ)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 承認Voice候補の特定: 上記CURRENT_SPEC Grepで既存承認Voice(Aoede/Charon/Erinome+他)を列挙し、各Voiceの既存用途(narrator/Support/装置/母)と性別印象の記録があれば引用。**兄Voice選定**: 明確に男性的に聞こえる既存承認Voiceを選ぶ。Charonは本記事で装置(記憶保管screen、2発話)に使用中のため、兄にCharonを使う場合は装置Voiceを別の承認Voiceへ変更するか、装置2発話が短く文脈で識別可能として共用を許容するかを判断し理由を記録(共用する場合は報告で明示)。Charon以外に男性的な承認Voiceがあればそれを優先。候補がなければSTOP条件該当として報告。
2. 新segmentation設計: `reader_facing_article.txt`の29段落を、Voice変化点(装置2発話・兄1発話)・Comment挿入位置(C2=段落8/9境界・C3=段落23/24境界はTrial-10の意味的判断を維持)・scene/semantic boundaryのみで区切り、同一Voice(Aoede)連続部分は概ね100語以内・120語を大きく超えない範囲で統合。1文・数語の独立segmentを作らない。短い装置発話("Return date?"/"Are you sure?")は別Voiceのため分割不可避だが、その前後のAoede部分は統合する。設計表(segment id/voice/段落範囲/word count/分割理由)を`er013_output/family_c_episode_trial_11/memory_a2/segmentation_plan.json`へ保存し、TTS実行前に設計を確定(TTS前のドライランで語数分布を確認・報告)。
3. Comment Trial Prompt: 新スクリプト内に`COMMENT_1_ROLE_JA_TRIAL11`/`_2_`/`_3_`を新設(旧`COMMENT_*_ROLE_JA`は`_TRIAL10_PREV`として残置し比較可能に)。役割: 「次に聞く英文を理解しやすくするため、今どこにいるか/誰が何をしているか/次の英文理解で重要な状況/何が選択・対立点か、のうち本当に必要な情報だけを短い日本語(目安2〜3文、80〜110字)で整理する」。禁止語句を明記(聞いてみましょう/耳を傾けて/耳を澄ませて/注目してみましょう/これからどうなるでしょう)。結末先出し禁止・新Fact追加禁止。Comment 1はStory開始時点の具体的状況(レナが小さな銀の箱を持ち、中には兄の最期の記憶が入っている等、本文にある事実のみ)。生成後、禁止語句のGrep検証(`聞いてみましょう|耳を傾け|耳を澄ま|注目して|どうなるでしょう`)で0件を確認。品質不足時のみ同一Promptで最大1回再生成。
4. 既存asset reuse: Trial-10 `memory_a2/`から`audio/`配下のIntro/Outro/SFX/Welcome/topic_intro_en/japanese_title/preview_ja/kp_*(Key Phrase英語5件・日本語5件)等の非Story・非Comment wav/mp3と`key_phrases/`・`preview.txt`を新OUT_DIRへコピー(`.ok`マーカーも含め再TTSされない状態にする)。再TTS対象=新Story segment全件+Comment 1〜3の3件のみ。
5. SSOT追記位置: `Grep pattern="^## USER-TEST-FINAL-AUDIO-BATCH-06(委任D" path=DECISION_LOG.md`→そのエントリ末尾直後に新エントリ追加(索引1行も)。`OPEN_ITEMS.md`はpythonで行末追記: OPEN-147(Family C)にTrial-11の結果を1行。恒久課題候補(segment最小/最大長・同一Voice連結ルール・Dialogue segmentation・Family C Comment Prompt)は新番号を起票せず、OPEN-147追記文中に「候補」として列挙。
6. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾にComment再生成(model/routing)の行を既存形式で追加。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11.md --json-out docs\pm\delegation_log\FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11_check.json
```

本文sha256検証:
```
.venv\Scripts\python.exe -c "import hashlib;print(hashlib.sha256(open('er013_output/family_c_future_trial_08/memory/reader_facing_article.txt','rb').read()).hexdigest())"
```
(=`a9a646a798bfe44b632038c790d58680a3b278979ac39473339cace2733b2ea2`であること。)

ドライラン(TTSなし、segmentation_plan.json生成+語数分布表示):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_11_memory_run.py --plan-only
```
(語数分布: 最短/最長/各segment。150語以上が0件、120語超が原則0件[やむを得ず超える場合は理由付きで報告]、10語未満の独立segmentが装置発話以外に0件、であることを確認してから本実行。)

本実行(上限¥50):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_11_memory_run.py --budget-jpy 50
```
(複製元のargparseに合わせて実引数を確定し全文報告。工程: asset copy→新Story segment TTS[narrator=Aoede/装置/兄=選定Voice]→現物ASR→Comment 1〜3再生成[Trial-11 Prompt]→TTS→ASR→Comment位置→Assembly→Audio Validation→player→web_delivery.json。)

禁止語句検証:
```
.venv\Scripts\python.exe -c "import re;t=open('er013_output/family_c_episode_trial_11/memory_a2/comments_ja.md',encoding='utf-8').read();m=re.findall(r'聞いてみましょう|耳を傾け|耳を澄ま|注目して|どうなるでしょう',t);print('BANNED_HITS=',len(m),m)"
```

回帰: `er013_family_c_episode_trial_10_memory_test_01.py`を複製して`er013_family_c_episode_trial_11_memory_test_01.py`(Trial-11用: 本文sha一致・Comment 4不在・禁止語句0件・新segmentに150語以上なし・兄segmentのvoiceが選定Voice、5件程度)を作成し:
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_11*_test_*.py"
```
Trial-10テストは無変更のため再実行不要(Trial-10成果物を触っていないことは`git status --porcelain er013_output/family_c_episode_trial_10/`が空であることで確認・報告)。

Web到達確認(push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_11/memory_a2/player.html']]"
```
episode mp3 direct URL(`web_delivery.json`の実ファイル名)も同様にGET確認、計2件のstatusを報告。

## SSOT追記文

`DECISION_LOG.md`(委任Dエントリ末尾直後):
```
## FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11

- 日付: 2026-09-16
- 種別: Family C Memory A2限定の仕様変更Trial(ユーザー承認)。Production仕様へ自動採用しない。Status=VALIDATED候補/USER_LISTENING_PENDING。
- 本文: Trial-08正本固定(sha256一致確認)、Writer再実行なし。旧Trial-10成果物は`family_c_episode_trial_10/memory_a2/`に無変更で保存、新版は`family_c_episode_trial_11/memory_a2/`。
- Segmentation: 旧15 segment(最短<n>語/最長<n>語)→新<n> segment(最短<n>語/最長<n>語)。Trial安全ガイド(概ね100語以内、120語を大きく超えない、150〜200語級なし)を適用。統合した短segment<要約>、残した境界<Voice変化/Comment位置/scene boundary>。hard cap実装なし。
- Comment: Trial-11 Prompt(英文理解ガイド役割、メタナレーション禁止語句あり)で1〜3再生成。禁止語句0件。旧Promptは`_TRIAL10_PREV`として残置。Production正式Promptは未変更。
- Voice: 兄=<旧Voice>→<新Voice>(既存承認候補内、理由<1行>)。装置=<Voice、変更有無>。
- Audio: Audio Validation <PASS/FAIL>、duration <秒>(旧290.593秒)。再生成回数<n>。費用¥<実測>(LLM/TTS/ASR)。Family C累計¥578.10+¥<実測>=¥<合計>。
- 恒久課題候補(defer、起票せず記録のみ): TTS segment最小/最大長、同一Voice連結ルール、Dialogue segmentation、Family C全体のComment Prompt。ユーザー試聴後に判断。
- 参照: `docs/pm/RESULT_PACKET.md`、commit <hash>
```
索引1行。`OPEN_ITEMS.md` OPEN-147行末: ` 2026-09-16追記(TRIAL-11): Memory A2でsegmentation見直し(旧15→新<n>、最長<n>語)+Comment理解ガイド化+兄Voice<新Voice>のTrial版を新出力先に作成(旧版保存)。Audio Validation <結果>、費用¥<実測>、Family C累計¥<合計>。Status=VALIDATED候補/USER_LISTENING_PENDING、Production未採用。恒久課題候補: segment長/同一Voice連結/Dialogue segmentation/Comment Prompt(defer)。`
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(UDR-deferred: Discovery B1/A2の個別対応可否[UT-06 D報告済み]、OPEN-154/155、Family C 4 episode+Trial-11の試聴)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象(wav除外、mp3必須): `er013_family_c_episode_trial_11_memory_run.py`、`er013_family_c_episode_trial_11_memory_test_01.py`、`er013_output/family_c_episode_trial_11/memory_a2/`配下(player.html、web/**/*.mp3、segments.json、segmentation_plan.json、speaker_map.json、comment_placement.json、comments_ja.md、audit/*.json、各consistency/validation/cost json、web_delivery.json、key_phrases/**・preview.txt等のコピー)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11.md`、同`_check.json`、`docs/pm/RESULT_PACKET.md`は.gitignore対象なら追加不要。
- `family_c_episode_trial_10/`配下・`er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11: Memory A2 segmentation統合+Comment理解ガイド化+兄Voice変更のTrial版(旧版保存)`
- trailer: `Task-ID: FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11`
- push: `git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`(上書き)に、ユーザー指示12の項目をそのまま:
1. T-0結果、本文sha256一致、Trial-10無変更確認(`git status`空)
2. Segmentation: 旧segment数/新segment数、旧最短・最長word count/新最短・最長word count、各新segmentのおおよそのword count(表: id/voice/段落範囲/語数/分割理由)、統合した短segment一覧、残した境界と理由、100語目安・120語超回避の実適用(超えた場合は理由)
3. Comment: 旧Comment 1〜3→新Comment 1〜3の並記、Trial-11 Promptの要点、禁止語句検証結果、使用model/routing
4. Voice: 兄旧Voice/新Voice(選定理由、承認候補一覧の出典行)、装置Voiceの変更有無、runtime evidence(`tts_generation_results.json`のvoice記録・TTS関数名)
5. Audio: TTS segment数と失敗/retry内訳、ASR 4者一致結果(表記揺れは列挙)、Audio Validation(PASS/FAIL)、duration(旧290.593秒との差)、新player URL、direct audio URL、Web到達確認、今回追加費用(LLM/TTS/ASR/その他)
6. PM: Status=USER_LISTENING_PENDING、Production採用なし、恒久課題/Open Item候補(4点形式)、STOP該当有無
7. 回帰結果、commit hash・push結果・残差分要約
8. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用)。
</content>
