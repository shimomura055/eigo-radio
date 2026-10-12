# REPORT_01(FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-01 委任_02、2026-10-12)
使用モデル: Gemini TTS gemini-3.8-flash-lite-tts(応答model_version実測=同名、Aoede、Standard同期)。ASR=gpt-4o-mini-transcribe(Primary、Production既定ASR)+ local faster-whisper small/medium(費用0、評価用途例外理由=費用最小・既存測定と同一条件)。

## 1. Prompt比較(8候補。共通前半=現行Baseline Style、F5固有の後半1文を方向別の1文へ置換。数値WPM・倍率なし)
| 候補 | 方向 | 文字数(F5=246) | sha256先頭12 | 後半1文(逐語) |
|---|---|---|---|---|
| PC1 | 落ち着いたニュースナレーション | 227 | c2ef66560ec3 | Deliver it like a calm, composed news narrator giving a measured, unhurried report. |
| PC2 | 急がず自然な息継ぎ(文間の間) | 260 | 096cbe099499 | Take your time, with a natural, unhurried breath between sentences, as if talking with a friend and nothing to rush. |
| PC3 | 意味単位で区切る | 235 | ed96f55f0a35 | Phrase the story in meaningful chunks, letting each idea land before moving on to the next. |
| PC4 | 文末を静かに収める | 244 | 5bb1760bf75b | Let each sentence settle softly at its end, with a gentle fall in pitch, before the next one begins. |
| PC5 | 目の前の1人へ語りかける | 247 | 7ad577058548 | Speak as if to one attentive listener sitting across from you, warm and conversational, easy to follow. |
| PC6 | 重要語・数字を際立たせる | 268 | ed79779814ab | Give key words and numbers a little extra weight and clarity, with natural pauses around them, so the main points stand out. |
| PC7 | ゆとりある語り手(余白) | 257 | 335631b34a73 | Tell it like a thoughtful storyteller, relaxed and spacious, with room to breathe between phrases; never hurried. |
| PC8 | 丁寧で滑らかな運び(教材調回避) | 264 | 91d09946b7dc | Speak with a measured, deliberate cadence that lets each point land, yet stays smooth and connected; never word by word. |
全文は `prompts/prompts_pace_01.md`。PC8は初稿が+73字と肥大したため+18字へ短縮してから生成(生成前の調整、生成は1回のみ)。F5 sha 9228209bec75...は既存log(generation_log_03)と一致。

## 2. WPM比較(語数462=tts_safe適用後、Final v2と同一定義。基準F5は既存測定 wpm_results_01.json)
| 候補 | P1 | P2 | P3 | 合計WPM | 発話WPM(500) | 発話WPM(300) | 文間ポーズ(500ms) 数/計s | 最速10s窓 | 窓std | 文最大 | Part差 | 判定 | 警告 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PC8 | 180.3 | 205.4 | 198.3 | **195.4** | 207.1 | 225.0 | 14/8.04 | 252.0 | 21.2 | 351.4 | 25.1 | PASS | window>250 |
| PC1 | 186.5 | 202.0 | 200.9 | **197.0** | 209.5 | 224.6 | 15/8.42 | 252.0 | 19.8 | 322.8 | 15.5 | PASS | window>250 |
| PC4 | 191.5 | 198.9 | 204.3 | **198.4** | 207.0 | 223.8 | 10/5.78 | 252.0 | 17.0 | 331.2 | 12.8 | PASS | window>250 |
| PC6 | 185.9 | 205.9 | 209.8 | **201.0** | 214.8 | 227.8 | 15/8.89 | 258.0 | 18.5 | 323.5 | 23.9 | EXCLUDED | window>250 |
| PC2 | 187.7 | 212.9 | 200.3 | **201.1** | 213.1 | 228.7 | 13/7.79 | 264.0 | 21.2 | 371.4 | 25.2 | EXCLUDED | Part>210,window>250 |
| PC7 | 186.4 | 214.5 | 200.7 | **201.3** | 215.8 | 229.1 | 16/9.23 | 246.0 | 21.9 | 341.8 | 28.1 | EXCLUDED | Part>210 |
| PC3 | 190.7 | 203.3 | 214.5 | **203.0** | 212.2 | 231.0 | 10/5.93 | 252.0 | 18.5 | 323.5 | 23.8 | EXCLUDED | Part>210,window>250 |
| PC5 | 190.4 | 209.1 | 208.0 | **203.1** | 209.5 | 220.6 | 7/4.16 | 240.0 | 15.6 | 317.3 | 18.7 | EXCLUDED | - |
| F5 | 190.0 | 221.5 | 212.0 | **208.6** | 219.0 | 232.5 | 11/6.31 | 264.0 | 19.2 | 339.6 | 31.5 | 基準 | - |
注: 基準F5自体も最速10秒窓264(>250)・Part2 221.5/Part3 212.0(>210)でありスクリプト上は警告条件に該当(表のF5行の警告欄は適用外として空欄)。窓WPMは10秒窓内の語数x6のため6WPM刻み。

## 3. 一次選別(合計WPM 170〜200 = PASS)
- **PASS(3件、Human Review対象)**: PC8 195.4 / PC1 197.0 / PC4 198.4。いずれも Part別は全て<=210(最大205.4)。ただし3件とも最速10秒窓252(>250、閾値を6WPM刻みで超えた)=警告。F5(264)よりは低い。
- **除外(5件)**: PC6 201.0 / PC2 201.1 / PC7 201.3 / PC3 203.0 / PC5 203.1(全て200をわずかに超過=F5 208.6からの減速幅が3〜6 WPMに留まった)。PC2/PC7/PC3はPart>210(Part2 212.9/214.5、Part3 214.5)も該当。
- 重要な発見(参考記録): (1) F5後半文の置換だけでは、Style文のみで170〜200へ届くのは弱く、効いた方向は「落ち着いたニュース調(PC1)・文末を収める(PC4)・丁寧で滑らか(PC8)」。(2) 範囲外でもPC5(語りかけ)はテンポのばらつきが最小(窓std 15.6、Part差18.7、文間ポーズが少なく連続的)で、200超が惜しい候補として聴き比べ価値あり(Fable判断)。(3) 全候補で170未満(=遅すぎ)はゼロ。(4) Part2がどの候補でも最速(原稿が長く情報密度が高い)でPart間差は12.8(PC4)〜28.1(PC7)、F5は31.5。

## 4. 警告・品質確認(機械指標。聴感所見ではない)
- Primary ASR(Trial隔離、NGでも再生成せず記録): 24件中22件OK(NORMALIZED_MATCH/HIGH_SIMILARITY_SAFE)。**NG 2件**: PC2 Part2(TRUE_CONTENT_MISMATCH: `says`->`said`の1語差)、PC3 Part3(`price`->`pricing`の1語差)。いずれも local whisper small/medium では同箇所の差異なし(medium: PC2 Part2は says/said差なし、PC3 Part3は9->nineのみ)=Primary ASR側の聞き取り揺れの可能性が高いが、断定は不可(要試聴)。どちらも範囲外候補。PASS 3件はPrimary ASR全Part OK。
- 発音・明瞭さ(local whisper差): 全候補で差分は表記系(8.7%->8 7 %、US->u s、2->two、9->nine、cafe->caf)が大半で、候補間でほぼ同一=TTS入力側の表記/ASR表記ゆれ。内容語の置換は PC1 Part1 medium `entered->centered`(smallでは正)のみ(PASS候補。要試聴)。
- 反復・言い直し: local whisper差分に反復(同一語列の挿入)は検出なし(small側の挿入 `it/this/thanks for watching` は末尾無音のwhisper幻聴系で候補共通、実音声の言い直しとは判断しない)。
- 異音検知(既存検知器・閾値不変): PASS候補 PC1=6件(medium以上0)、PC4=5件(0)、PC8=7件(medium 1: Part3 23.16秒 click)。F5=6件(0)。範囲外では PC2=12件(medium 3: Part1 26.15/36.97秒、Part3 32.98秒 click)、PC3=9件(medium 1: Part3 27.43秒 click)。他はlowのみ。自動検知のみを根拠とする再生成は行っていない。medium/click候補はユーザー試聴での確認事項。
- 文間ポーズ/テンポ: PASS候補の500ms以上の文間ポーズは PC8 14個/8.0秒、PC1 15個/8.4秒、PC4 10個/5.8秒(F5 11個/6.3秒)。PC4は文間ポーズが最少で全体は詰まって聞こえる可能性(要試聴)。PC8・PC1はポーズが多く落ち着き側。
- 抑揚/F5の良さ維持、学習向け聴きやすさ: **音声を聴取しての評価は未実施(機械指標のみ)**。要ユーザー試聴。

## 5. 実費・条件
- 生成: 24 call(8候補x3Part、各1回、技術失敗0、regeneration 0)、所要65.7秒(6並列)。実費(推定、請求画面未確認): TTS JPY 26.96 + Primary ASR 6.10 = **JPY 33.06**(上限JPY 40に対し82.6%。委任_01概算31.9との差は遅い候補の長尺化)。`cost_actual_01.json`。
- local whisper測定・異音検知・集計・ページ生成・Playwright: 費用0。
- model_version(応答実測): 全24件 gemini-3.8-flash-lite-tts。prompt sha・text sha・wav sha は `generation_log_01.jsonl`。

## 6. Production不変確認
本taskの書込先は `er057_output/pace_trial_01/`・`user_test/coffee_pace_trial_01/`・`er057_pace_trial_01*.py` のみ。Production runner不使用、Master Store/manifest/telemetry/queue/attempt_history書込なし(validator telemetryはプロセス内リストへ差替え)。`production_sha_after_01.txt` を、委任_04時点 `production_sha_before_04.txt` と比較すると8件中6件一致、2件差分(er011 attempt_history.jsonl、er021 telemetry.jsonl)。差分2件のファイル更新時刻は 08:56 / 09:13(TTS-LOCAL-REWRITE-CONNECTED-SPEECH等の別task由来の追記で、本taskの生成開始約09:54より前)、かつPC/pace由来の行は0件(grep確認)=本task起因ではない。CURRENT_SPEC/Prompt/SSOT未編集。
