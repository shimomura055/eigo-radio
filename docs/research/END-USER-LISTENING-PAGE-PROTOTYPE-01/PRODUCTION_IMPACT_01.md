# PRODUCTION_IMPACT_01(量産時の追加処理時間・費用、X/Y/Z展開課題。委任_01a D項、2026-10-29)

前提: 本書は試作(DEV/Trial)の測定に基づく見積であり、Production採用・配線の提案ではない(未承認。採用判断はユーザー)。

## 1. 1記事セット(Std+Adv)あたりの追加費用・時間
| 項目 | 見積 | 根拠 |
|---|---|---|
| API費用(採用案 c'=ローカルASR+無音スナップ) | **¥0**(API呼出0、音声再生成0)。70円/セットへの影響 **0%** | 本委任の実費も0円(下記) |
| 文を持つsegmentの音声長 | Std 262.5秒(11 segment・55文)+Adv 239.4秒(10 segment・48文)=**約8.4分/セット**(KP・定型音声は同期対象外) | `sync/*/index.json`、`VERIFY.json` |
| CPU時間(1プロセス・8スレッド・他に負荷なし、AI島Std Part 1=56.3秒の実測) | small: 転写9.6秒(RTF 0.17)→セット全体で**約85秒**。medium: 転写26.7秒(RTF 0.47)→**約4分**。モデルロード 1.5秒/5.5秒 | `scratchpad/bench.py`実測(2026-10-29) |
| 本委任での並列実行 | 3プロセス同時(各4スレッド)でmediumを回し、全31 segmentのASRに約17分(競合込み) | asr_*.log |
| 文分割・整列・無音スナップ・検証 | 数秒/segment(numpy) | - |
| (参考)有料ASRにした場合 | whisper-1: 約¥8.1/セット(+11.6%)、Azure Speech: 約¥22/セット(+32%)(いずれも公式価格に基づく概算、未検証。USD_JPY=160) | `daily_dev_cost_01.py:22` |

→ 量産単価70円への影響: 採用案ではAPI費用0。CPU時間のみ(Pagesビルド+約1.5〜4分/セット、segment単位で並列化可能)。「量産単価を継続的に最適化」(Charter 3)の観点では**有料ASRは不採用が妥当**。

## 2. 開発負荷(Productionへ載せる場合の概算。未承認・参考)
- 新規: (a)同期生成module(本試作の`sync_build_01.py`を昇格、約250行)、(b)`pages` stage(X/Y/Z)への接続と`sync/*.json`出力、(c)ページ側JS(01b/02で試作)、(d)再計算キー(mp3 sha256+台本sha256)のキャッシュ、(e)test(分割・整列・スナップ・欠損時fail-closed方針の決定)。**Productionの既存コード・Prompt・閾値は変更不要**(同期生成はページ生成の下流の追加処理)。
- 新規依存: `faster-whisper`はProduction runnerでは現在未使用(`--exclude-dir=docs` のgrepで0件。docs/researchの調査scriptのみ)。採用時はProduction環境への導入(モデル約0.5〜1.5GBのDL)が追加判断。
- 失敗時方針は仕様判断(ユーザー): 同期データ生成が失敗/低信頼の場合に「ハイライトなしで公開」(推奨・音声と本文は無傷)か「ページ公開を止める」かは仕様の選択。試作では前者を前提(ハイライトは補助機能であり、学習コンテンツ本体ではない)。

## 3. 再生成・更新時の保守性
- 同期データの依存: 該当segmentのmp3(=assembled wavの切出し)と台本。**他segmentが再生成されても、そのsegmentのmp3内容が不変なら同期データは不変**(時刻はsegment先頭基準。エピソード内位置`part_start_in_episode_s`だけ`timeline.json`から更新)。→再計算対象は変更segmentのみ(resume時はキー一致でASR 0)。
- LR(Local Rewrite)・Fallback・ゲイン変更でmp3が変わる場合は当該segmentのみ再計算。台本(表示本文)が変わった場合は文分割の件数一致検査(`sync_attach_display_01.py`)で不一致を検出しfail-closedにできる(試作: 31/31 segmentで一致)。

## 4. X/Y/Z展開時の課題(試験済み/未試験を区別)
| 課題 | 状態 | 内容 |
|---|---|---|
| X Std/Adv(本試作) | **試験済み**(AI島Std/Adv・月Adv、計31 segment・151文、日本語Std 5 segmentを含む) | 全segmentでASR転写と台本が一致(token match 96〜100%)、境界はすべて無音区間にスナップ(wide/短ポーズ4境界は低信頼度タグ) |
| Y: 3 Voice切替 | **未試験**(構造のみ調査) | Voiceごとにsegmentが分かれる(Lead/Voice 1〜3/Closing+各Introduction)ため、同期データはsegmentごとに独立生成でき追加仕組みは不要の見込み。ただしYは各segment「TTS 1回/分割なし(段落=1)」でChunk間の0.2秒パッドが無い→**文間ポーズが短い可能性**(月Advで0.08〜0.15秒の文間を確認。AI島Std/Advは最小0.25秒)。短ポーズでは無音スナップの精度がASR境界に依存し低下しうる。Yの実音声で検証が必要 |
| Z: 話者切替・紹介文 | **未試験** | Part長尺audio(57〜71秒)内で話者(Fenrir/Algieba等)が切り替わり、台本に話者ラベル・紹介文が混在する。TTS入力文と表示本文の文数一致検査(`display_match`)で検出できるが、対話の引用符・会話文の文分割規則(`"..." he said.`)の追加が必要。Z Part 1の1文が長い(文学テキスト)ので文あたりの無音は少なく、カンマ・セミコロンの長ポーズが誤スナップ候補になる |
| 日本語セクション | **試験済み**(Std Preview/Comment 1〜4/日本語タイトル) | whisper(ja)は漢字を誤認することがあるが(例「島」→「死」)、文字レベル整列+無音スナップで文境界は正しく決まった(token match 97〜100%)。`japanese_title`は記事タイトルを内包するため1単位扱い。Zの日本語紹介文等は同様に可 |
| KP/定型音声 | 対象外 | KPは1語句、定型(Welcome/Intro/通知音/Outro)は台本なし。ブロック単位の強調はtimeline.jsonのsegment時刻のみで可能(API 0・追加処理なし) |
| Part 1(Vocabulary & Expressions)等の学習ブロック | 対象外 | 音声と対応しない学習テキスト |
