# ER-006-AUDIO-COST-PILOT-02 完了報告

Gemini Batch A/B・OpenAI mini ASR Pilot・Validation残課題修正・全工程原価再計算。前回(ER-006-AUDIO-COST-OPTIMIZATION-01)の調査結果を、実際にコードへ実装し、Public Benches(Luna版)の同一トピックでProduction Pilotとして実行した。

---

## 0. §25 質問への回答(先にまとめて回答)

| # | 質問 | 回答 |
|---|---|---|
| 1 | Gemini Batch A/B Artifact | 作成済み。5segmentのStandard/Batch聴き比べ(ブラウザで再生可能) |
| 2 | Standard vs Batchの機械的差 | 長さの差: -3.7%〜+15.1%(生成ごとの通常のブレの範囲内)。音量(RMS/peak)はStandard側が本番のtrim/gain処理済み・Batch側が未処理のため単純比較不可(Artifact内に明記) |
| 3 | Human Review待ち項目 | 上記5件の主観品質判定(voice一貫性・抑揚・自然さ・発音・pacing・音量感・聞きやすさ・長文安定感)はユーザー試聴待ち |
| 4 | OpenAI mini ASR Pilot結果 | 英語Primary ASRとして実際に47segment・Public Benches B1+A2ペア全体で稼働。Azure比で明確にPASS率向上、コストも実測で35%減 |
| 5 | Azure比でPASS率どう変わったか | STOPPED数: 7件→3件(実測、同一トピック)。attempt総数: 110→79(-28%) |
| 6 | true error誤PASS有無 | **今回のPilot実測では0件**。STOPPEDになった3件はいずれも正当な理由(2件はvalidatorの正規化漏れ、1件は固有名詞の真正なASR限界)であり、誤って通した内容誤りは確認されていない |
| 7 | STOPPED before/after | Before(Luna, Azure全言語): 7件STOPPED+1件UNCERTAIN。After(Pilot-02, 英語OpenAI mini+日本語Azure): **3件STOPPED+0件UNCERTAIN** |
| 8 | UNCERTAIN before/after | 1件→0件(A2 point_two、Malmö/Triangelnの難しい用例が解消) |
| 9 | retry回数 before/after | 110attempts/47segments(2.34倍)→79attempts/47segments(1.68倍) |
| 10 | Audio Waste円 before/after | 実測: Historical Actual ¥306/pair(audio) → Pilot Actual ¥199/pair(audio)、-35.1% |
| 11 | canonical placeholder bug修正結果 | 修正済み・regression test 7件PASS。Public Benches B1 kp5(「associate with」)は「〜を…と結びつける」から「関連づける」へ修正し、今回のPilotで一発PASS |
| 12 | residual validation問題の内訳 | 5件を全数フォレンジック(詳細は§8)。B: ASR認識誤り(1件、street/St.型は既に解消済み確認)、C: Validator側の正規化漏れ(2件、今回修正)、D: 真正なASR限界・要Human Review(2件、Ottoni固有名詞) |
| 13 | Master Audio reuse件数 | 実測25件reuse(B1で9件生成→A2で9件+Key Phrase重複0件は今回のトピックでは重複なし。ただし2回実行[後述]により9件×2回reuse相当を含む) |
| 14 | Master Audio削減秒数/円 | 定型segment(9種)は初回生成後、以後恒久的に0円・0秒(TTS呼び出しゼロ)。今回のPilotで実際にwelcome/preview_intro等9種がB1→A2間で完全reuseされたことを実測確認 |
| 15 | Writer Cost | 変更なし(Luna既存成果物を再利用、新規Writer呼び出し0件)。参考値: ¥1.64/pair(既存実測) |
| 16 | Support Cost | 同上、Writer Costに含む |
| 17 | Prompt Cache hit率 | 既存実測を継続参照(今回Writerは実行していないため新規測定なし): writer_b1 2.4%、writer_a2 4.3%(理論上限より低い、伸びしろあり) |
| 18 | TTS Cost | 実測 ¥183.9/pair(Gemini分、Standard、Pilot Actual内訳) |
| 19 | ASR Cost | 実測 ¥14.9/pair(OpenAI-mini+Azure合算、Pilot Actual内訳) |
| 20 | B1 Full Clean Cost | (Batch+Master Audio込み、モデル化)約¥28/episode相当(音声部分、下記§10参照) |
| 21 | A2 Full Clean Cost | 同上、約¥33/episode相当 |
| 22 | B1+A2 Pair Full Clean Cost | **¥64.9/pair**(音声部分)+ Writer/Research ¥4.07 = **¥69.0/pair**(全工程) |
| 23 | Expected Production Cost | **¥106.4/pair**(全工程、実測waste比1.68倍を反映) |
| 24 | 20 Topic/day月額 | **¥63,816**(全工程、Expected Production Cost基準) |
| 25 | 30 Topic/day月額 | **¥95,724**(同上) |
| — | 100/300/500/1000 users参考収支 | §11参照(20t/dayで100人だと原価が売上を上回る、500人で黒字転換の目安) |
| — | 次に量産へ進める状態か | **いいえ、量産はまだ推奨しない**。理由は§13参照(Batch音声のHuman Review未完了、Ottoni型固有名詞対応方針が未決) |
| — | 残存Open Item | §13・OPEN_ITEMSへ追記予定 |
| — | 新規API Cost | 合計 約¥204(Pilot Standard TTS+ASR ¥198.8 + Batch A/B比較 ¥5.16) |

---

## 1. 対象・前提

- トピック: **"Why Are More Cities Rethinking Public Benches?"**(pool_benches)、Luna版の既存Research(Evidence Pack/VFL/Verification/Ledger)・Writer・Support・Key Phrase選定成果物をそのまま再利用(新規LLM呼び出しは0件)。
- 新規に実行したのはAudio(TTS+ASR+Assembly)段階のみ。出力先は新しいtheme_id `pool_benches_pilot_02`(既存のLuna版出力とは別ディレクトリ、before/after比較のため意図的に分離)。
- kp5(B1)のjapanese_glossのみ、後述のcanonical placeholder bugの実例修正として手動補正(「〜を…と結びつける」→「関連づける」)。

---

## 2. 実装した変更(コード)

**実装はすべて完了・regression test全PASS。詳細ファイル一覧は§14。**

1. **ER-006-KP5-CANONICAL-BUG-01**: `er003_audio_tts_asr_safety.py`に`detect_gloss_placeholder_notation()`を追加。Key Phrase日本語gloss(B1: `generate_charon_japanese_with_reading_safety`、A2: `generate_a2_japanese_with_reading_safety`)の両経路に、TTS呼び出し前のゲートとして配線。プレースホルダ記号(「〜」「～」「…」)がgloss中に残っている場合、TTS/ASRへは一切進まずSTOPPEDで停止する。`tts_safe_ja()`もU+FF5E/U+301Cの両tilde文字種を先頭stripできるよう修正。
2. **ER-006-ASR-OPENAI-PILOT-01 / ASR Provider Routing**: 新モジュール`er006_asr_provider_routing_01.py`。`ASR_ROUTING = {"en": openai_asr, "ja": azure}`のSSOT。`require_asr_route()`は未登録言語でFail-closed例外を送出(暗黙fallback禁止)。本番のASR呼び出し全9箇所(`er003_v1_n3_01_tts_generate.py`・`er003_v1_crosslevel_audio_02_common.py`・`er003_v1_repro01_main_generate.py`・`er003_v1_sing01_news_tail_fix.py`・`er003_v1_sing01_point_headings_aoede.py`・`er003_v1_sing01_voice01_generate.py`)を、直接のAzure呼び出しからこのSSOT経由へ置き換えた。`er005_cost_logger.py`に`_patch_openai_asr()`を追加し、Gemini/Azureと同じ形でOpenAI ASRのprovider/model/usageをtelemetryへ記録。
3. **ER-006-ASR-VALIDATION-RESIDUAL-02 / Validator修正**: `er006_preprod_hardening_01_validation.py`の`normalize_text()`へ2件の一般対策を追加。(a) 通り種別略語(street/avenue/road等、USPS標準の閉じた既知集合)をcanonical側の完全形へ吸収(street→St.を安全に判定、Saint/Streetの曖昧性はcanonical側テキストで自動的に解消)。(b) 小さな数(2〜12)の綴り⇔算用数字の表記差を吸収(OpenAI-mini ASRがAzureと逆方向の数字表記をすることを実際に発見したため)。個別記事・個別語のwhitelistは作らず、いずれも一般的な既知集合による対策。「three→3:00」のような桁が変わる誤りは引き続きTRUE_CONTENT_MISMATCHのまま(regression testで確認)。
4. **ER-006-MASTER-AUDIO-STORE-01**: 新モジュール`er006_master_audio_store_01.py`。`MasterAudioKey`(language/level/speaker_voice/tts_model_id/style/instruction_path/canonical_text_hash/audio_processing_version/sample_rate/channels)のsha256ハッシュを`master_audio_id`とする。`get_or_generate(key, out_path, generate_fn)`が、既存masterがあればTTS呼び出しなしでコピー、無ければ生成してStoreへ登録する(失敗した生成はキャッシュされない)。`er006_audio_cost_pilot_02_shared_narration.py`が、welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five(+A2のpoint_explanation)とKey Phrase英語Componentをこのstoreへ配線。`er003_v1_n3_01_tts_generate.py`のB1/A2生成関数の先頭で自動的に呼ばれる。

---

## 3. ER-006-TTS-BATCH-HUMAN-AB-01: 実コンテンツA/B

代表5segment(英語: 長尺Story・Point・Key Phrase、日本語: Support・短いKey Phrase meaning)を、本番と完全に同一のprompt構築(`p4c.build_tts_prompt`)・voice・style instructionでStandard/Batch両方生成した。

Artifactで実際に聴き比べ可能: **[Standard vs Batch Listening Review](https://claude.ai/code/artifact/3553b782-cf0a-47e4-9528-0748a6a2a5b3)**

機械的な差(実測):

| Segment | Standard長さ | Batch長さ | 差 |
|---|---|---|---|
| English long story | 56.25s | 54.17s | -3.7% |
| English point | 25.08s | 26.73s | +6.6% |
| English key phrase | 1.85s | 2.01s | +8.6% |
| Japanese support preview | 27.61s | 27.88s | +1.0% |
| Japanese key phrase meaning | 3.51s | 4.04s | +15.1% |

**新たに発見した事実**: 最初のEnglish long story向けBatchジョブは、ジョブ自体はSUCCEEDEDしたが個別レスポンスが`code=13 Internal error`で失敗した(前回報告で確認した「ジョブ作成成功≠音声生成成功」の懸念が実際に発生した実例)。同一リクエストを再送したところ2回目は成功した。**Batch APIは単発の内部エラーが起こり得るため、本番導入時はBatch側にも個別アイテム単位のretry機構が必要**(単純にStandard相当の信頼性とみなしてはならない)。

Claudeは「同一モデルだから品質同一」だけでPASS判定していない。音量(RMS/peak)はStandard側が本番のtrim/gain処理済み・Batch側が未処理のraw出力のため単純比較できないことをArtifact内に明記した上で、**最終判断はユーザーの試聴に委ねる**。

---

## 4. ER-006-ASR-OPENAI-PILOT-01 / Provider Routing: 実行結果

英語=OpenAI gpt-4o-mini-transcribe、日本語=Azure Speech STTの言語別構成で、Public Benches B1+A2ペア全体(47segment)を実際に生成した。Providerへの暗黙fallbackは実装上発生しない(§2-2のFail-closed設計、regression testで検証済み)。

### 4.1 Before/After比較(同一トピック、実測)

| 指標 | Before(Luna、Azure全言語) | After(Pilot-02、英語OpenAI mini) | 差 |
|---|---|---|---|
| STOPPED | 7件 | 3件 | -57% |
| ASR_VALIDATION_UNCERTAIN | 1件 | 0件 | -100% |
| 総TTS+ASR attempt数 | 110 | 79 | -28% |
| waste比(attempt/segment) | 2.34倍 | 1.68倍 | -28% |
| Audio実費(TTS+ASR、B1+A2ペア) | ¥306.1 | ¥198.8 | -35.1% |

### 4.2 true error誤PASS・false negative確認

47segment全体のattempts_logを確認した限り、**OpenAI-mini ASRが実際には誤っているTTS音声を誤ってPASSさせたケースは0件**。逆に、正しい音声をASR側の癖で不要に足止めした既知パターン(前回報告で確認した"hostile"→"hustle"型の新しいASR誤り)も、今回のPilot実行では発生しなかった(観測範囲内での実測。今回のPilotは1トピックのみのため、大規模運用でのfalse positive率は別途大規模計測が必要、§9参照)。

---

## 5. ER-006-KP5-CANONICAL-BUG-01: 修正結果

Public Benches B1 kp5(英語Key Phrase "associate with")のjapanese_glossが、辞書的な項変数記法「〜を…と結びつける」のまま残っていた問題を修正した。

- **一般対策**: `detect_gloss_placeholder_notation()`により、今後同種の記法がどのKey Phraseで発生しても、TTS呼び出し前に検出・ブロックする(B1・A2両経路に配線)。
- **今回のPilotでの実例修正**: gloss自体を「関連づける」(自然な単独動詞形、他の4件のgloss(例:「その場を立ち去る」)と同じパターン)へ手動補正。今回のPilotで**1回目の試行で即PASS**した(修正前は12回全attemptがTRUE_CONTENT_MISMATCH/ASR_VALIDATION_UNCERTAINだった)。
- **Regression test**(`er006_kp5_canonical_bug_01_test.py`、7件PASS): placeholderありのテキストがTTS呼び出し前にブロックされること(TTS呼び出し回数0を実際にmonkeypatchで確認)、先頭のみのplaceholderは安全にstripされて通過すること、通常のellipsis等を誤って過検出しないこと、を確認済み。

---

## 6. ER-006-ASR-VALIDATION-RESIDUAL-02: 残存課題の全数調査

前回報告で指摘した7項目について、全件を再調査した。

| ケース | 分類 | 結論 |
|---|---|---|
| street / St. | B→吸収済み | `normalize_text()`の通り種別略語吸収により解消(既にPilotで実証: B1 point_two・A2 full_story_part1がOK) |
| Malmö / Triangeln | 主にB(ASR起因) | OpenAI-mini ASRへの切替でA2 point_two(最も難しい用例)が今回のPilotでOKに転じた |
| reported / put in | C(前回はValidator側の言い換え検出の厳格さ) | 今回のPilotでは該当segment自体がOKで通過、再現せず(様子見) |
| punctuation結合(St. furniture等) | B→吸収済み | 通り種別略語吸収が同時に解決 |
| smart quote | 影響なし | `normalize_text()`が既にcurly quoteをstraight化しており問題化していない |
| three / 3:00 | 意図的に未吸収(D、TTS/ASR限界) | 数字化で意味が変わるケースとして、修正後もTRUE_CONTENT_MISMATCHのまま(regression testで明示的に確認、絶対にPASSさせない) |
| 固有名詞Ottoni | **D(真正なASR限界、未解決)** | B1 point_one・A2 full_story_part1で12回全attempt、"Atoni"/"A Tony"/"O'Tooney"等、一貫して誤認識。TTS自体は"three"を正しく発話できているが(§7で別途確認)、"Ottoni"という珍しいポルトガル語系学術者名固有の認識限界。**ASRプロバイダの選択だけでは解決しない**、今後Human Review継続扱いとする |

**今回新たに発見した残存課題(2件、両方とも修正済み)**:

| セグメント | 症状 | 分類 | 原因 | 対応 |
|---|---|---|---|---|
| B1 comment_3 | 全6回attemptがTRUE_CONTENT_MISMATCH | C(Validator正規化漏れ) | `tts_safe_number_words_en()`がTTS入力側だけ"two"→"2"へ変換(Azureが口頭の小さい数を算用数字で書き起こす前提の対策)。OpenAI-miniは逆に綴りのまま"two"と書き起こし、canonical側の"2"と不一致 | `normalize_text()`へ2〜12の綴り⇔算用数字の一般吸収を追加(§2-3参照)。修正後、この実テキストでNORMALIZED_MATCHになることを確認済み |
| B1/A2 num_three(固定shell segment) | 全6回attemptがTRUE_CONTENT_MISMATCH | C(同上) | 同じ原因("Three."→OpenAI ASRが"3"と書き起こし、旧Validatorが数字/綴りの差を吸収できなかった) | 同上の修正で解消(実際に再生成し1回目でPASSしたことを確認、Master Audio Storeへ正しいmasterとして登録済み) |

**残存する既知の限界(未解決、Human Review対象)**: Ottoni固有名詞のみ。ASRプロバイダに依らない限界であり、対応方針(発音辞書登録・Writer側での引用形式見直し等)はこのPilotのスコープ外として次アクションへ記録する。

---

## 7. Production Retry Policy(実装済み、既存Guardrailをそのまま使用)

新規の変更は行っていない。既存の`should_stop_retrying()`(同一signatureがmax_same_signature回連続でASR_VALIDATION_UNCERTAIN)をそのまま使用し、TRUE_CONTENT_MISMATCH/TTS_FAILUREのみがTTS再生成の対象になる設計は維持した。Secondary ASR(Azure併用)は今回もProduction導入していない(§13で評価継続の位置づけを記録)。

---

## 8. ER-006-MASTER-AUDIO-STORE-01: 実行結果・reuse実測

### 8.1 Reuse実測(telemetryログより)

| イベント | 件数 |
|---|---|
| generated(新規TTS) | 19件 |
| reused(TTS呼び出しなし) | 25件 |
| generate_failed(生成失敗、キャッシュされず) | 3件(num_threeの2回分の失敗+1、後に手動再生成で解消) |

実際に確認できた効果: B1で生成された9種の完全固定segment(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five)は、A2生成時に**全て新規TTS呼び出しゼロでreuse**された(実測、`er006_audio_cost_pilot_02_shared_narration_test.py`のunit testでも同じ挙動を再現済み)。今回のトピックではB1↔A2で完全一致するKey Phraseは無かった(前回監査の3トピックでは4件見つかっていたが、今回のPublic Benchesトピック単体では該当なし)。

### 8.2 Welcome drift解消

既知の問題(`welcome.wav`がB1向け/A2向けで別録音・別長さだった)は、`level=None`の共通Master Audio Keyにより、**構造的に発生しなくなった**(同じmaster_audio_idの同じ物理ファイルを両レベルが参照する)。既存の完成episode(過去のhanshin/health/household等)は書き換えていない。今後、Master Audio Store経由で生成される新規テーマから順次この恩恵を受ける。

### 8.3 削減効果(定性)

完全固定segmentは「初回だけ課金・以後は恒久的に0円」という性質のため、今回1トピックのみのPilotでは金額換算の絶対値は小さい(9segment×1回分のTTS+ASRコストのみ)。ただし前回監査の推計(セグメント数ベースで29〜33%削減)通り、**トピック数が増えるほど相対的な効果が増す**設計であることは変わらない。

---

## 9. Secondary ASR: 今回も未採用(評価継続)

前回報告の結論を維持。今回のPilotでOpenAI-mini Primaryのみでの実測結果(STOPPED 7→3、UNCERTAIN 1→0、false positive 0件)が得られたため、**Secondary ASR(Azure併用)の緊急性は前回よりさらに下がった**と判断する。今後、より大きなサンプル(複数トピック)でfalse positive率を継続観測した上で要否を再判断する方針を維持する。

---

## 10. Full Production Cost 再計算

### 10.1 コスト定義(混同しないよう明示)

- **Historical Actual**: 過去に実際に支払った額(Luna版、Azure全言語ASR、Standard TTS)
- **Pilot Actual**: 今回実際に支払った額(Standard TTS + 新ASR構成、Master Audio Store一部適用)
- **Full Clean Production Cost**: 新規トピックを一発成功でB1+A2作る標準想定(Batch TTS + 新ASR構成 + Master Audio Store適用、waste=1.0倍)
- **Expected Production Cost**: 実測waste比(1.68倍)を含めた現実的予測

### 10.2 実測ベースのコスト構成比(Pilot Actual、B1+A2ペア、audio部分のみ)

Gemini TTS 92.5% / OpenAI-mini ASR + Azure ASR 7.5%(実測トークン数・秒数から算出。旧Azure全言語構成時はGemini 65.9%/Azure 34.1%だったため、**ASRコスト構成比が大幅に縮小**したことも実測で確認)。

### 10.3 最終比較表(B1+A2ペア、JPY)

| | Clean(音声) | Expected(音声) | +Writer/Research | Full Clean(全工程) | Expected(全工程) |
|---|---|---|---|---|---|
| **Historical**(Azure全言語、Standard) | — | ¥306 | +¥4.1 | — | ¥310 |
| **Pilot Actual**(実測、Standard TTS+新ASR) | ¥118 | ¥199(実測) | +¥4.1 | ¥122 | ¥203(実測相当) |
| **ASR切替+Master Audio**(Batch未採用の場合) | ¥113 | ¥190 | +¥4.1 | ¥117 | ¥194 |
| **ASR切替+Batch**(Master Audio未適用) | ¥64 | ¥107 | +¥4.1 | ¥68 | ¥111 |
| **ASR切替+Batch+Master Audio**(推奨最終形) | ¥61 | ¥102 | +¥4.1 | **¥65** | **¥106** |

Pilot Actualの数値は、ディレクトリ設定ミスによる1回の中断・再実行を含む実測値のため、単一のクリーンな実行より若干高め(保守的な上限値)である旨を開示する。

### 10.4 月次コスト(Expected Production Cost基準、全工程)

| | 20 Topic/day | 30 Topic/day |
|---|---|---|
| Search/Research | ¥1,458 | ¥2,187 |
| Writer/Support | ¥984 | ¥1,476 |
| TTS(Gemini, Batch) | ¥54,900程度 | ¥82,350程度 |
| ASR(OpenAI mini+Azure) | ¥6,474程度 | ¥9,711程度 |
| **Total(Expected)** | **¥63,816** | **¥95,724** |

参考: 何も変更しなかった場合(Historical基準)は20t/day ¥186,120、30t/day ¥279,180。**今回の変更一式で月額を約66%削減できる見込み**(実測+モデル化の組み合わせ)。

---

## 11. 490円プランに対する参考収支

決済手数料・infra・CS・marketingは含まない。AI content原価のみの参考値。

| Topic/day | 月額原価 | 100 users(¥49,000) | 300 users(¥147,000) | 500 users(¥245,000) | 1,000 users(¥490,000) |
|---|---|---|---|---|---|
| 20 | ¥63,816 | **130.2%**(赤字) | 43.4% | 26.0% | 13.0% |
| 30 | ¥95,724 | **195.4%**(赤字) | 65.1% | 39.1% | 19.5% |

100ユーザー規模ではAI content原価だけで売上を上回る。300ユーザーで原価比率が40〜65%まで下がり、500ユーザー以上で原価比率が30%を切る。

---

## 12. Gemini BatchがHuman Review NGだった場合

Batch音声がユーザー試聴でStandardより明確に劣ると判断された場合、**Batchは採用しない**。その場合の代替コストは§10.3の「ASR切替+Master Audio(Batch未採用の場合)」行の通り: Full Clean ¥117/pair、Expected ¥194/pair(月額20t/day ¥116,241、30t/day ¥174,361)。Historical比でも約37〜38%の削減効果は、Batch抜きでも維持される。

---

## 13. 次に量産へ進める状態か / 残存Open Item

**現時点では量産推奨ではない**。理由:

1. **Gemini Batch音声のHuman Review未完了** — Artifactでの聴き比べはユーザー判断待ち。
2. **Ottoni型固有名詞のASR限界が未解決** — 今後Pool Topicに同種の珍しい人名・地名が含まれた場合、同じ問題が再発する可能性がある。対応方針(発音辞書・Writer側の引用形式見直し等)は今回検討していない。
3. **今回のPilotは1トピックのみ** — false positive率・waste比の改善が他トピックでも同程度に再現するかは、複数トピックでの追加検証が必要。
4. **Prompt Cache活用の伸びしろ**(Writer側)は依然未着手(プロンプト構築順序の変更が必要、今回も実装せず)。

Open Itemとして`OPEN_ITEMS.md`へ追記する(§14参照)。

---

## 14. 変更ファイル一覧・Regression Test

**新規ファイル**:
- `er006_asr_provider_routing_01.py` / `_test.py`
- `er006_master_audio_store_01.py` / `_test.py`
- `er006_audio_cost_pilot_02_shared_narration.py` / `_test.py`
- `er006_kp5_canonical_bug_01_test.py`
- `er006_audio_cost_pilot_02_run.py`(Pilot実行スクリプト)
- `er006_batch_ab_01_generate.py`(Batch A/B生成スクリプト)

**変更ファイル**:
- `er003_audio_tts_asr_safety.py`(placeholder検出関数追加)
- `er003_v1_n3_01_tts_generate.py`(canonical gate配線、ASR routing配線、Master Audio Store配線)
- `er003_v1_crosslevel_audio_02_common.py`(ASR routing配線、Master Audio local narration_dir優先読み込み)
- `er003_v1_repro01_main_generate.py`(ASR routing配線)
- `er003_v1_sing01_news_tail_fix.py`(ASR routing配線)
- `er003_v1_sing01_point_headings_aoede.py`(ASR routing配線)
- `er003_v1_sing01_voice01_generate.py`(ASR routing配線)
- `er005_cost_logger.py`(OpenAI ASR用patch追加)
- `er006_preprod_hardening_01_validation.py`(街路略語吸収・数字表記吸収追加)
- `er006_preprod_hardening_01_validation_test.py`(新規fixture3件追加)
- `er006_model_routing_contract_01.py`(コメントのみ、ASR routingの実体を明記)

**Regression test結果**: 9スイート全PASS(既存の6スイート含む、後方互換破壊なし)。

---

## 15. 制約の遵守確認

- サービス仕様(エピソード構成・B1/A2仕様・Support内容・声質・トーン・pacing・TTS話者・料金プラン)は変更していない。
- Sol call: 0件(実測確認済み)。
- 残りPool Topicの量産には進んでいない(Public Benches 1トピックのみ)。
- 新規有料API支出: 合計 約¥204(Pilot Standard TTS+ASR ¥198.8、Batch A/B比較5件+1回retry ¥5.16)。不要なFull Episode再生成は行っていない(1回の中断・再実行は、こちらのディレクトリ設定ミスによるもので、内容規模としては1トピック分のまま)。

---

完了後STOP。残りPool Topic量産には進まない。
