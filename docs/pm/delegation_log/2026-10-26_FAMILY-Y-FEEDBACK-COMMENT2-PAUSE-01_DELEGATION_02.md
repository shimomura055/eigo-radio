## 管理ID
FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02(Lane B、2026-10-26 JST): read-only調査。(1)『宅配』E-1 Full Story Voice 1(Std/Adv)の不自然なポーズ過多の原因切り分け(既存音声・生成記録の計測)、(2)Family Yの「段落分割+0.2秒ポーズ」仕様が正式初回Production経路でStd/Adv両方に**実際に**適用されたかの検証(コード存在ではなくruntime記録と完成音声の照合)、(3)試聴ページ改修(分割位置・0.2秒ポーズ表示・Chunk個別再生)の要件整理。**並行**: 同管理ID 委任_01(Lane A)がComment 2削除の実装・SSOT編集中。Lane Aの所有=`er121_*.py`・`er121_prompts/`・共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)・`docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/{DESIGN_01,SPEC_CHECK_01}.md`。**本委任はProductionコードと共有SSOTを編集しない。** 本委任の所有=`docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/{INVESTIGATION_01,PAUSE_MEASUREMENT_01,CHUNK_WIRING_CHECK_01,LISTENING_PAGE_REQ_01}.md`、解析script `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/*.py`(新規、Production経路から独立したread-only解析専用)、`docs/pm/RESULT_PACKET_YFB2.md`。`er121_output/`は**読取のみ**(wavの複製が必要なら`docs/research/.../tools/`配下ではなくscratch `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\yfb2\`へ)。

## 性質/到達上限Status/禁止事項
- 性質: 調査(read-only)。到達上限: 原因の確定または切り分け結果+是正案(承認済み仕様内か新仕様判断かの分類)。有料API 0・TTS生成0(既存データで確定できない場合は「追加生成が必要な最小構成と見積」を報告するのみ、実行しない)。
- 禁止: Production file/Prompt/閾値/Gateの編集、`er121_output/`・`user_test/`の変更、Voice変更・速度/ポーズ基準変更の提案を「採用」として書くこと(提案はQCD影響付きのユーザー判断候補として)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- Opus独立技術レビューGate: 非該当(調査)。
- 時間見込み: 全体60〜90分(記録収集20、計測30、照合・文書20)。並列化: Lane Aと並行(所有分離)。
- 費用/日次: JPY0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2: TTS実行なし(非該当)。T-3: Capなし(JPY0)。

## ユーザー指示(原文)
Lane Aが `docs/pm/delegation_log/2026-10-26_FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01_USER.md` へ逐語保存する(数分以内に存在する。無ければ待たずに下記引用で開始し、後で照合)。本委任に関わる原文§2・§3・§4の要点(逐語):
- §2「『宅配』のStandard／Advancedとも、Full StoryのVoice 1に不自然なポーズが多い。まず既存音声と生成記録を用いて原因を調査する。以下を切り分けること。1. Voice固有の発話特性 2. TTS Prompt・Style・速度指定の影響 3. 段落分割による影響 4. 追加0.2秒ポーズによる影響 5. 音声結合・組立処理の影響 6. Standard／Advancedで共通する原因 可能な限りポーズの発生位置・長さを計測し、実際の台本位置と照合する。単に「Voice固有の問題と思われる」と推測するのではなく、既存音声や生成条件を比較して根拠を示すこと。既存データで原因が確定できる場合は追加TTS生成不要。」
- §3「ユーザーは、Family Yにも段落分割＋0.2秒ポーズを適用するよう以前から指示している。したがって、今回の確認は新規採用判断ではない。指示済み仕様が実際にProductionへ正しく配線されているかを確認すること。以下を確認する。1. 過去のユーザー指示・承認記録・CURRENT_SPEC・DECISION_LOGとの整合。2. Family Yの正式初回Production経路に段落分割と0.2秒ポーズが存在するか。3. Standard／Advanced両方で発動しているか。4. 『宅配』のVoice 1を含む各Voiceで、実際にどこで分割されたか。5. 0.2秒ポーズが指示どおり挿入されているか。6. retry／resume／regenerationでも同じ仕様が維持されるか。7. 今回の不自然なポーズとの因果関係。コードの存在だけで適用済みと判断しないこと。正式runtimeの生成記録と完成音声を照合する。」
- §4「段落分割位置がユーザーに明確に分かるようにする。台本上で、実際のTTS分割位置を表示。各分割位置に追加0.2秒ポーズの有無を明示。可能であれば各Chunkの個別再生に対応。分割位置と不自然なポーズの発生位置を比較しやすくする。本文の見た目上の段落区切りと、TTSで実際に分割した位置を混同しないこと。今回の『宅配』試聴ページに反映する。不要に複雑なUIは作らず、必要十分な表示とする。」

## KPI provenance欄
計測値=既存Production成果物(reuse、run_01の完成wav/mp3と生成記録)に対するread-only解析。E2E自己確認: No。

## Opus台帳更新
該当なし。

## 事前指定Read一覧
- 承認履歴: `CURRENT_SPEC.md` Grep `Chunk X方式|chunk_tts|applied_X_method|段落.{0,6}分割|0\.2秒|200ms|inter_chunk|Family Y Closing品質Gate` → 該当行±10。`DECISION_LOG.md` Grep `Chunk X方式|段落分割|0\.2秒|FAMILY-Y-PRODUCTION-LAUNCH-01 委任_0[3-9]` → 該当エントリ。ユーザー原文: `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md`・`_USER_03.md`(Grep `Chunk|分割|0\.2|ポーズ|X方式` → 該当行)。X側の正本: `docs/pm/delegation_log/2026-10-23_FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01_委任_03_MERGE.md`等ではなくX Chunk方式の採用記録(CURRENT_SPEC Grep `X2p|段落ごと別Chunk|Chunk TTS` → 該当節)。
- 実装(読取のみ): `er121_family_y_runner_01.py` Grep `chunk_tts|applied_X_method|split|paragraph|pause|0\.2|silence|concat|assemble` → 該当関数。`er121_family_y_audio_01.py` 同Grep。`er117_chunk_tts_production_01.py` Grep `def |pause|silence|0\.2|200|split` → 分割規則・無音長の定義行。`er121_family_y_structure_01.py` Grep `pages|chunk|segment`。
- runtime記録(読取のみ): `er121_output/family_y_production_01/redelivery_fee/run_01/{a2,b1b}/` 配下のmanifest/`*chunk*`/`*tts*`/`*assemble*`/`attempt*`/JSON(Glob→Grep `chunk|split|pause|silence|duration|voice_1|y_voice_1`)。完成音声: `<run>/pages/audio/*.mp3`と`<run>/{a2,b1b}/narration/*.wav`(Voice 1〜3・導入・Closing)。`a2/hr_adopt_prep/y_voice_1_slowed_asr_recheck.json`(a2 Voice 1は6%減速版が採用。減速処理=`er008 apply_a2_slowdown`相当の有無をGrep)。
- 比較対象(Voice固有特性の切り分け用): 同一Voice名で生成された他のY/X音声(E-3 SNS `er121_output/family_y_production_01/sns_age_limit/run_01/`のVoice 1〜3、Round 1/2 closing trial `er110_output/`配下)と、E-1のVoice 2/3。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 承認履歴(`CHUNK_WIRING_CHECK_01.md` §1): 「Family Yにも段落分割+0.2秒ポーズ」のユーザー指示・承認の出所(原文path:行、DECISION_LOGエントリ、CURRENT_SPEC行)を逐語で引用。X側の採用仕様(分割規則=何を境に分けるか、無音長=0.2秒の定義、適用対象=本文のみ/Lead含むか)を実装行で確定。
2. 配線確認(同§2): Y正式経路(runner→audio→er117)で、分割関数と無音挿入がStd(a2)/Adv(b1b)両方・全Voice・導入/Closingに対して呼ばれるかをコード経路で追跡(行番号)。retry(ER-011/ER-020 Local Rewrite)・resume・`--regenerate-stage`・HR採用(`er121_e1_hr_adopt_r0_01.py`の`.pre_ypl7_adopt.wav`差替)・a2減速処理の各経路で分割/無音が維持されるか(減速処理がchunk結合後のwavに掛かるか、無音長も6%伸びるか等)。
3. runtime照合(同§3、最重要): run_01の生成記録から、各Voice(Std/Adv × Voice 1〜3、可能なら導入・Closing)について「実際のchunk境界(台本上の文字位置・chunk数)」「各chunkのTTS attempt・wav長」「結合時に挿入された無音長」「完成wav長=Σchunk+Σ無音 か」を表にする。記録が無い項目は「記録なし」と明記し、完成音声の無音区間計測(下記4)から逆算して推定(推定は推定と明記)。
4. ポーズ計測(`PAUSE_MEASUREMENT_01.md`): 完成音声(Std/Adv Voice 1、比較用にVoice 2/3とE-3 Voice 1)に対し、無音区間(例: −40dBFS以下が≥150ms)を検出し、位置(秒)・長さを一覧化。各無音をASR語タイムスタンプ(既存ASR記録にword timestampがあればそれを使う。無ければ`py`で無料のアライメントは不可→無音位置と台本の文・句読点・chunk境界を長さ比例で対応付け、精度の限界を明記)で台本位置へ対応付け、分類: (a)chunk境界の追加0.2秒 (b)文末/句読点の自然ポーズ (c)文中の不自然ポーズ (d)chunk境界+TTS側の文末ポーズの重複(0.2秒+TTS末尾無音+次chunk先頭無音)。Voice別・レベル別の統計(ポーズ数/分、平均長、最大長、文中ポーズ比率)を比較し、§2の切り分け1〜6に回答。特に「chunk末尾/先頭の無音(TTSが生成する前後の空白)+0.2秒」の合計が長くなっていないか、chunkが短すぎて境界が多すぎないかを定量化。
5. 原因判定: 切り分け結果を「承認済み仕様内の不具合(例: 無音の二重挿入・chunk末尾無音の未トリム・分割が細かすぎる実装誤り)」と「新仕様判断(Voice変更・速度/ポーズ基準変更・分割規則変更)」に分類し、前者は是正案(変更箇所・影響範囲・X/Zへの影響有無・検証方法・費用0か)を、後者はQCD影響付きの判断候補を記載。**実装はしない。**
6. 試聴ページ要件(`LISTENING_PAGE_REQ_01.md`): §4を満たす最小仕様(台本上にchunk境界マーカー+0.2秒有無、chunk個別再生用にchunk wav→mp3の所在、無音検出結果のマーカー表示案、見た目の段落と実分割の区別)。既存pages生成(`er121_family_y_structure_01.py`)への追加点を行番号で示す(実装は委任_03)。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01_DELEGATION_02.md`(Nは620前後、`--index -1`不可、「FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02(Lane B」を含むもの)。

## 実行コマンド全文
- 無音検出(新規script、read-only): `py -I docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/yfb_silence_scan_01.py --wav <絶対path> --threshold-dbfs -40 --min-ms 150 --out docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/measure/<name>.json`(標準library `wave`+`audioop`または既存の依存のみ。mp3は`ffmpeg`が無ければwavを使う)
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-26_FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01_DELEGATION_02.md --json-out docs/pm/delegation_log/2026-10-26_FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01_DELEGATION_02.md_check.json`
- secret grep: `git grep -n -I -E "(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|BEGIN (RSA|OPENSSH) PRIVATE KEY)" -- docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01`

## SSOT追記文
本委任はSSOTを編集しない。OPEN行追記文案(ポーズ原因・配線確認結果の要約)をRESULT_PACKETに記載(Lane A/委任_03が反映)。

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/{INVESTIGATION_01,PAUSE_MEASUREMENT_01,CHUNK_WIRING_CHECK_01,LISTENING_PAGE_REQ_01}.md`、`docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/*.py`、`docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/measure/*.json`(小さければ)、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01_DELEGATION_02.md`(+_check.json)。wav不追跡。`git commit --only <paths>`(index.lock競合時は30秒待って再試行、3回失敗なら未commitで報告)。
- メッセージ案: 「FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02: 『宅配』Voice 1ポーズ過多の計測・原因切り分けと段落分割+0.2秒ポーズのY実適用検証(read-only、API 0)」
- `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。SSOT編集権: なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_YFB2.md`。「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+RESULT_PACKET 4行+判定整合行。必ず含める: §3の1〜7への回答(各々「確認済み/記録なし/推定」を明記)、Std/Adv各Voiceの実分割位置表と0.2秒挿入位置、ポーズ計測統計(Voice 1 vs 2/3 vs E-3 Voice 1)と分類(a〜d)、§2の切り分け1〜6への回答と根拠、原因の分類(仕様内不具合/新仕様判断)と是正案(費用・X/Z影響)、試聴ページ要件、追加TTSが必要な場合の最小構成と見積、commit/push・raw URL、check結果。