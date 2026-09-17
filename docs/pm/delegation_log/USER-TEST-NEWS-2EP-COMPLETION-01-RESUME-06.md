## 管理ID

`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06`(親: `USER-TEST-NEWS-2EP-COMPLETION-01`。前段RESUME-05 `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md`[player配置修正・E2E手順、既読扱い可])。現在main=`5740f747`以降。報告は`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME6.md`(新規、累積Full形式)へ。

**並行タスクあり(衝突回避ルール)**: (a)`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`(AI Control音声stage→player→SSOT→commit、`ai_control/`配下+`build_web_player_common.py`使用)、(b)`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`(er012配下、(a)完了marker待ち→TTS→assemble→player→commit)が実行中。ルール: (1)**本タスクのTTS/ASR/Assembly(共有store書き込み)は、marker `docs/pm/RESULT_PACKET_PN_A2_PHASE_B_FIX1.md` が存在するまで開始しない**(5分間隔で最大150分。超過時はB1表示修正まで完了させて報告、A2タイトルは「TTS待ち」として明記)。(2)B1表示修正(`user_test/unified.html`および/または`space_weapons/b1b/player.html`の表示部分)は即実行可。ただし`build_web_player_common.py`は(a)が使用中のため**変更しない**(表示区切りが生成テンプレート由来で共通module変更が最善の場合でも、本タスクではunified.html側または対象player.htmlへの直接最小修正で対応し、共通module側の恒久反映はRESULT_PACKETに「後続で反映推奨」と記録)。(3)SSOT編集(DECISION_LOG)・git操作は最後にまとめ、`git status --porcelain DECISION_LOG.md OPEN_ITEMS.md CURRENT_SPEC.md docs/pm/PM_GOVERNANCE.md`で自分以外の未commit変更が無いことを確認(あれば5分間隔で最大30分待つ)。commit前に`git fetch origin`→`git merge origin/main --no-edit`(rebase/force push禁止、競合時STOP)。全文Write禁止(unified.htmlはEditで局所修正)。`docs/pm/ACTIVE_TASK.md`は最後に1回だけ固定ヘッダで上書き(他タスク状態保持)。(4)`ai_control/`・er012・root `er0*.py`は変更しない。

## 性質/到達Status/禁止事項

- 性質: ユーザー試聴Feedback(2026-09-17)の反映。**A2**=タイトル読み上げの区切り修正(topic_introのタイトルTTS segmentのみ再生成、text shapingによるマニュアル調整可)。**B1**=視聴ページのComment/本文の視覚的区切り修正(表示のみ)。
- 到達Status: A2=「タイトルTTS修正・技術的再生確認済み/ユーザー再試聴待ち」。B1=「内容OK済み(ユーザー明示)/表示修正済みURL提示」。**B1を試聴待ちに戻さない**。
- 変更範囲(厳守): A2=タイトルTTS segment(+必要なAssembly/Gate/player/web mp3更新)。B1=user-test viewing pageの表示フォーマットのみ。**非対象**: 記事本文再生成、Fact/Ledger再実行、Key Phrase変更、Comment内容変更、Full Story再生成、他segmentのTTS再生成、音声内容の変更(B1)。
- 禁止: 過度なUI改修、既存記事の表示を壊す変更、Gate緩和、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。

## 1. A2 — タイトル読み上げの区切り修正(ユーザー指示原文要旨)

現状「Today's topic is The New Space Question: Is the Weapon in Orbit?」がTTSで「The New Space / Question: Is the Weapon in Orbit?」のように区切られ不自然。期待: 「The New Space Question / Is the Weapon in Orbit?」の意味まとまり。colon自体の読み上げは不要。目的は「New Space Question」を1まとまりとして自然に読ませること。今回はマニュアル調整でよい: タイトルTTS segmentのみ再生成/必要ならSSML・punctuation・pause・text shaping等で自然な区切りを作る/本文や他segmentは再生成しない/既存記事内容は変更しない/修正後、実音声で区切りを確認/**ASRだけでなくタイトル冒頭の実際のprosody・phrase boundaryを確認**。修正後Assembly/Gate/playerまで必要範囲を更新しURL再提示。
**実装指針**: 既存Production経路の「TTS入力テキストとcanonical(ASR照合)テキストを分離できる仕組み」(例: `tts_input`/`text`と`canonical_text`の分離、reading transform、`custom`instruction route)を確認して使う。記事タイトル文字列(表示・script・canonical)は不変のまま、TTS入力のみ「Today's topic is The New Space Question. Is the Weapon in Orbit?」等(colonをピリオド/ダッシュ/明示pauseへ置換)に整形する。既存機構で不可能な場合のみ、当該segmentの生成呼び出しに限定したTTS入力整形を`space_weapons/run_pipeline.py`(自作driver)側で行い、Production moduleは変更しない。ASR照合はcanonical(原文)で行い、句読点差はNORMALIZED_MATCH許容範囲で通す(Gate緩和はしない)。
**prosody確認**: 既存disfluency QAが使うword-level timestamp(`faster_whisper` verbatim、`disfluency_evidence.transcript`と同方式)または同等のローカル手段で、"Space"→"Question"間のgapと"Question"→"Is"間のgapを計測し、**後者が前者より明確に大きい(かつ"Space"直後に不自然な間が無い)**ことをevidence JSON(`.../a2/audit/title_prosody_evidence.json`: 各wordのstart/end、gap値、修正前/修正後の比較)として保存。修正前音声(現行`topic_intro.wav`)も同計測して対比。修正候補が期待どおりにならない場合は最大3案(punctuation/pause/表記)まで試し、いずれも不可ならSTOPして計測結果と選択肢を報告(闇雲に試行しない)。
再生成後: 当該segmentの通常ASR検証→Assembly→Audio Validation Gate→player/web mp3更新(A2 player.htmlは記事dir直下配置を維持)→E2E再生確認。

## 2. B1 — 視聴ページの表示フォーマット修正(ユーザー指示原文要旨)

内容自体は問題なし。ただし**Commentと本文が視覚的に引っ付いておりCommentの区切りが分かりにくい**。対応: Commentと本文の間に明確な視覚的区切り(spacing/divider/section heading/box・margin等の最小限)。既存のシンプルなuser-test page方針維持、過度なUI改修不要。コンテンツ本文・Comment文言・音声は変更しない。**同じpage templateを使う他記事にも影響する場合は既存記事の表示を壊さないことを確認**(household等の既存URLで表示回帰チェック)。
**実装指針**: まず`user_test/unified.html`がplayer.htmlの`table.timeline`をどう表示しているか(行のrole/labelでComment行を識別できるか)を確認。Comment行(label/roleに"Comment"を含む行)の前後にCSSでmargin/border-top/背景色/小見出しを付ける等、unified.html側の最小CSS/JS変更で対応するのが望ましい(全記事に一貫適用され、既存表示を壊さない範囲)。player.html側だけの修正で済む場合も可。A2 playerにも同じ区切りが適用されることを確認(A2 Commentは日本語)。

## 3. 回帰確認(最低限)

A2 title audioが「The New Space Question / Is the Weapon in Orbit?」と聞こえる(prosody evidence)/A2全体再生可能/B1 Commentと本文が視覚的に分離(修正後スクリーンショット)/B1全体再生可能/script・Key Phrase・seek表示が壊れていない/A2・B1ともuser-test URL(最終SHA)でE2E再生確認(RESUME-05と同手順: Playwright、`currentTime`進行・`paused=false`・`error=null`・seek・表示要素、evidence JSON+png)/既存記事(household)の表示・再生回帰なし。

## 4. SSOT・Git

- DECISION_LOG: 本IDエントリ(ユーザー試聴Feedback: A2タイトル区切り/B1内容OK・表示区切り、対応内容、prosody evidence、E2E結果、Status)。OPEN_ITEMS/CURRENT_SPEC/PM_GOVERNANCE: 無変更(表示区切りの共通template恒久反映が必要なら「後続推奨」としてRESULT_PACKETに記載、Open Item化はしない)。
- Git: 成果物commit(明示add: topic_intro関連json/mp3/player.html/unified.html/evidence、wav除外)→push→最終SHAでURL 2本→到達・E2E確認→RESULT_PACKET/ACTIVE_TASK/DECISION_LOG commit→push。メッセージ`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06: Space Weapons A2タイトルTTS区切り修正+B1視聴ページComment区切り表示修正(試聴Feedback反映)`、trailer `Task-ID: USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06`。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)
E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read(unified.html・run_pipeline.pyの該当部は全文可)。G-1: git出力最小化。F-1: transcript退避不要。T-1: 事前指定外Readは理由をRESULT_PACKETに1行記録。T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。

## 事前指定Read/Grep一覧
- `user_test/unified.html`全文(表示構造・CSS)、`.../space_weapons/b1b/player.html`(timeline行のlabel/role、Comment行の識別子)、`.../space_weapons/a2/player.html`(同)
- `.../space_weapons/run_pipeline.py`: Grep `topic_intro|title|tts_input|canonical|custom|instruction`→タイトルsegment生成箇所
- `er003_v1_n3_01_tts_generate.py`: Grep `topic_intro|def generate_topic_intro|tts_input|canonical_text|reading|transform|instruction_type`→TTS入力とcanonicalの分離機構の有無(変更しない)
- `.../space_weapons/a2/audit/tts_generation_results.json`: Grep `topic_intro`→現行segmentの記録、`.../a2/narration/attempts/topic_intro_attempt*.json`
- `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md` 2-4節(E2E手順・evidence形式)
- `er011_output/household_unified_final_candidate_01/`のplayer.html(表示回帰確認用URL: 既存Sheet掲載形式)
- `DECISION_LOG.md`: Grep `^## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05`(直近書式)、`docs/pm/PM_BRIEF.md` L135-159

## 報告(`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME6.md`、★★★★報告ここから/ここまで★★★★、累積Full形式=RESUME-05までの親タスク全体状況[Space Weapons完成経緯・AI Control進捗・OPEN-159〜162・cost]を統合)
0. T-0 1. A2タイトル修正内容(TTS入力整形の方法、canonical不変の証跡、採用案/試行案) 2. prosody evidence(修正前/後のword timestampとgap、判定) 3. A2 ASR/Assembly/Gate(duration)・player/web更新 4. B1表示修正内容(ファイル・差分要旨、他記事への影響と回帰確認結果、修正後スクリーンショットpath) 5. E2E再生evidence(A2/B1、数値・path) 6. 新URL 2本(最終SHA) 7. AI Control進捗(RESUME-04/FIX-01のRESULT_PACKET存在時は要旨1行) 8. cost(本タスク+親累計) 9. Git SHA 10. DECISION_LOG行/無変更証跡 11. 現在Status(A2=タイトル修正後の再試聴待ち/B1=内容OK済み・表示修正URL提示) 12. ユーザー判断(A: なし/B: A2再試聴待ち、B1は内容OK済みで表示修正後URL提示のみ) 13. 未決事項 14. 無変更証跡(`git status --porcelain er0*.py CURRENT_SPEC.md OPEN_ITEMS.md`が空)/事前指定外Read(理由付き)。ユーザー向け表記は「B1」に統一。
