# SYNC_METHOD_01(1文単位ハイライトの同期データ方式 比較・確定、委任_01a、2026-10-29)

## 結論(Fable判断を待たず採用した1案)
**案(c') = ローカルASR(faster-whisper)のword timestamps + 台本の決定論的文分割との整列 + 音声の無音区間(RMS<-40dBFS)への境界スナップ。** 費用はAPI 0(ASR呼出なし・音声再生成なし)。生成物 `sync/{std,adv,moon_adv}/<part>.sentences.json`。

理由: (1)既存データに文のtimestampは無く(PHASE1_SURVEY_01 (7))、(2)有料ASRは量産単価に直接加算される(下表。¥8〜22/セット=70円目標の12〜32%)のに対し、本案は¥0、(3)精度は「ASRが文の位置を概略特定→TTSが必ず入れる文末ポーズの無音区間に境界を置く」ことでASRのword timestampの滲み(0.2〜0.6秒)に依存せず、10ms単位の音声実測で決まる。(4)Chunk境界(既存の正確なデータ)を独立な正解として検証に使える。

## 方式比較表
| 案 | 精度見込み | 費用(1記事セット=Std+Adv、文を持つsegment計約8.4分[Std 262.5秒+Adv 239.4秒]) | 量産負荷 | 保守性(音声再生成時の再計算) | 判定 |
|---|---|---|---|---|---|
| (a) 既存ASR audit timestampを整列 | **不可**: auditは転写テキストのみ。timestamp/offset未保存(PHASE1_SURVEY_01 (7)) | ¥0 | - | - | 不採用(データ無し) |
| (b1) OpenAI `whisper-1`(word timestamps) | word滲み0.2〜0.6秒程度(ローカルwhisperと同等と推定。未検証) | $0.006/分×8.4分≒$0.050≒**¥8.1/セット**(USD_JPY=160、`docs/pm/tools/daily_dev_cost_01.py:22`)=70円目標の**+11.6%** | API呼出(ネットワーク・rate limit) | 再生成ごとに再課金 | 不採用(費用)。※OpenAIの`gpt-4o-transcribe`/`gpt-4o-mini-transcribe`(本番ASR)は`timestamp_granularities`非対応(公式仕様に基づく認識。本委任では実呼出で未検証) |
| (b2) Azure Speech(word offsets) | 良好(推定。未検証) | 標準STT $1/時間≒$0.14≒**¥22/セット**(公式価格に基づく概算、未検証)=**+32%** | Azure依存・キー管理 | 再生成ごとに再課金 | 不採用(費用) |
| **(c') ローカルfaster-whisper + 無音スナップ(採用)** | **文境界を10ms単位の音声実測で決定**(下記検証: 3記事31segment・151文、全境界が実測の無音区間にスナップ、Chunk既知ギャップ16件の包含誤差0.0秒、medium/small二重モデルでfinal境界の差0.0秒) | **¥0**(API 0)。CPU時間のみ(下記) | CPU約4〜5分/セット(medium・本PC 16コア・同時3〜4並列時の実測。単独だと概ね半分以下)。smallなら約1/3。GPU/並列で短縮可 | **容易**: 入力=segment mp3(またはassemble後の波形)と台本のみ。再生成後に`pages`stage内で再実行(キー=mp3 sha256+台本sha256。一致なら再利用でASR 0) | **採用** |
| (c) 純粋なforced alignment(wav2vec2等) | 同等〜やや良い(推定) | ¥0 | 追加ライブラリ導入(torch/torchaudio等、本環境に未導入)・日本語は別モデル | 導入・保守コスト大 | 不採用(導入コストに見合う優位なし) |
| (d) 無音検出+文字数比のみ(ASRなし) | 不可: `silence_only_probe_01.py`の実測で、境界120件中82件が±50ms内だが**最大5.5秒ずれ**(カンマ位置の無音を誤選択し以降連鎖) | ¥0・ASR不要 | 最小 | 容易 | 不採用(精度。成功扱い不可) |

## アルゴリズム(`sync_build_01.py`)
1. 文分割(決定論): 台本=**TTS入力テキスト**(`audit/tts_generation_results.json`の`segments[*].text`、Full Story Partは`chunk_plan`のk1..kn順連結)。`. ! ?`+閉じ引用符の後に空白+大文字/数字/開き引用符が続く箇所で分割。略語(Mr/Dr/U.S./e.g.等)・1文字イニシャルは除外。日本語は`。！？`で分割。`topic_intro`と`japanese_title`は記事タイトルを内包するため1単位。
2. ASR: 公開済み**segment mp3そのもの**にローカル`faster-whisper`(medium・int8・CPU・word_timestamps)。英語=en、Std日本語(Preview/Comment)=ja。
3. 整列: 台本トークン列(英語=正規化単語、数字は`eight`↔`8`統一/日本語=文字)とASRトークン列を`difflib.SequenceMatcher`で整列。未対応トークンは前後のアンカー間で線形補間。
4. 境界スナップ: 文境界ごとに、ASR境界±0.2秒の窓内で**≥0.18秒の無音(RMS<-40dBFS、0.10秒以下のブリップは結合)**のうち最長を採用(段階2=窓外±0.7秒で≥0.20秒、段階3=短い無音は低信頼度タグ)。`end_i`=無音開始、`start_{i+1}`=無音終了。先頭=音声開始(無音終了)、末尾=最終無音の開始。
5. 出力: `sentence_id/chunk_id/text/display_text(Chunk planの表示本文と文数が一致する場合)/start/end/confidence/source/asr_raw`+ファイル先頭に`audio`(segment mp3)・`part_start_in_episode_s`・`chunk_gaps_in_part_s`。**時刻はsegment mp3先頭からの秒**(全編再生中は`part_start_in_episode_s+start`)。

## 再生UIへの引継ぎ(01b/02向け)
- 現在文 = `start_i <= t` を満たす最後の文。文間の無音(0.2〜1.1秒、中央値0.45秒)は直前の文のハイライトを保持し、次文の`start`で切替(ちらつき防止)。Partの最終文`end`+0.5秒で消灯。シーク時は二分探索で即時決定。
- 全編(通し)再生: segmentの`part_start_in_episode_s`を加算。この対応は全segmentで相互相関により検証済み(`VERIFY.json`の`episode_offset_check`: 差0.0秒、相関≥0.998)。

## 自己検証の結果(`sync_verify_01.py` / `VERIFY.json`、3記事・31 segment・151文。issue 0件)
| 検証 | 結果 |
|---|---|
| 単調増加・重なりなし・segment音声長内 | **全31 segment・151文で違反0**(`start<end<=音声長`、`start_{i+1}>=end_i`)。mp3長とtimeline長の差も0.15秒以内 |
| ASR転写と台本の一致 | 文字レベル一致率(正規化後): 平均**99.7%**・最小97.6%(31 segment)。単語/文字トークン整列の一致: 最小92.3%(月Topic intro 18/19)、他は96〜100% |
| 全編mp3内のsegment位置(全編再生で`part_start_in_episode_s+start`が使えるか) | 全31 segmentで全編mp3との相互相関ずれ**0.000秒**、相関≥0.998 |
| **独立な正解との照合**(Chunk境界。組立時に確定した既知ギャップ16件=AI島Std 5・Adv 5・月Adv 6) | 各ギャップ(0.2秒)が「Chunk内最終文のend」と「次Chunk先頭文のstart」の間に**全件完全に収まる(包含誤差 最大0.0秒)**。ASR・無音検出とは独立な検証 |
| 二重モデル(medium vs small、同一パイプライン) | 最終境界(スナップ後)の差: **最大0.00秒・中央値0.00秒(151文)**。生のASR境界(スナップ前)は最大0.62秒ずれる=ASR単独では不十分でスナップが効いている証拠 |
| 外れ値(生のASR境界と最終境界の差) | >1.5秒: **0件**。>0.5秒: 4文(AI島Std Part1-08/Part3-07、月Adv Part1-12/Part3-06。いずれもASRが文頭を0.5〜0.7秒早く出したケースで、最終境界は実測の無音に補正済み) |
| 無音にスナップできなかった境界 | **0件**。ただし「広窓または短いポーズ(<0.18秒)」で低信頼度タグを付けたもの4文(月Adv Part1-04/05/11/12、confidence 0.87〜0.89、文間0.08〜0.14秒のTTS自然ポーズ) |
| 文間ポーズ(出力のstart_{i+1}-end_i) | 最小0.08秒・中央値0.52秒・最大1.20秒(AI島Std/Advは最小0.25秒) |
| 表示本文との文数一致(`sync_attach_display_01.py`) | 公開ページの台本テキスト(タグ除去)を同じ分割規則で割った文数が**31/31 segmentで同期データの文数と一致**。`display_text`に表示本文(例: `eight blocks`・`“the Cathedral.”`)を格納 |

### 未確認(明示)
- **実ブラウザでの再生中ハイライト切替の体感精度**(音を聴いての確認)は本委任の範囲外(02で実機検証)。本検証は音声波形・ASR・既知Chunk境界に対する計測であり、「ユーザーが聴いて違和感がない」ことの代替ではない。
- 文末ポーズが0.1秒前後と短い境界(月Adv 4件)の厳密な位置は±0.05秒程度の不確かさがある(波形上は-65dBまで落ちる区間に置いたが、聴感との照合は未実施)。
- Y(3 Voice・分割なしTTS)、Z(話者切替・長尺)は未試験(PRODUCTION_IMPACT_01.md §4)。
- `whisper-1`/Azureの精度・価格、OpenAI `gpt-4o-transcribe`系のtimestamp非対応は公式仕様に基づく認識で、本委任では実呼出していない(採用案は有料呼出なしのため結論に影響しない)。
