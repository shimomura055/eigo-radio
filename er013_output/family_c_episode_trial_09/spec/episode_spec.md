# Family C Future — Home Robots 完成episode仕様(Trial-09)

管理ID: `EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09`
対象記事: `er013_output/family_c_future_trial_08/home_robots/reader_facing_article.txt`
(Trial-08採用、本文固定・本タスクでは再生成しない)

本ドキュメントは、Family C(Future)の完成episode化に必要な仕様を、
既存A/B-Family Production部品の再利用可否を先に確認したうえで、最小限
だけ新規設計したものである(仕様を増やしすぎない方針)。

---

## 1. 既存部品の再利用表

| 仕組み | 既存Production実装 | 再利用可否 | Family Cでの扱い |
|---|---|---|---|
| ナレーターTTS(EN/JA、ASR検証・disfluency QA・retry込み) | `er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()` | そのまま再利用 | topic_intro/preview/support/story narratorの全EN/JA音声に使用(voice=Aoede、model routingは既存関数内部の既定のまま) |
| Charon voice TTS | `er003_v1_sing01_voice01_generate.py::generate_charon_english()` | そのまま再利用 | ロボット直接発話専用voiceとして転用 |
| Key Phrase英語Component(Primary+Fallback retry構成) | `er003_v1_repro01_main_generate.py::generate_key_phrase_component_verified()` | そのまま再利用 | 5 Key Phraseの英語音声生成 |
| Key Phrase選定→canonicalization→Redundancy QA | `er003_v1_n3_01_scaffold_generate.py::run_key_phrases()` | そのまま再利用 | Home robots記事から実際に5件選定・canonicalization・冗長性QA |
| 日本語gloss 表示用/TTS用分離 | `er003_key_words_canonicalization.py`(`japanese_gloss`/`japanese_gloss_tts`) | そのまま再利用 | Key Phrase日本語音声はTTS用フィールドを使用 |
| Preview/Support LLM呼び出し基盤 | `er003_v1_iran01_a2_generate.py::run_support_text()` | そのまま再利用(role_instruction文言のみTrial新規) | Preview・Support 1/2の3本のJA文言生成 |
| Gain(RMSベース、scalar) | `er003_b1_p9a_audio.py::compute_gain_for_target_rms()`/`rms()`/`peak()` | そのまま再利用 | 全segmentの音量統一 |
| Mono24kHz→Stereo48kHz変換 | `er003_b1_p9a_audio.py::mono_24k_to_stereo_target()` | そのまま再利用 | 全segment |
| 無音(pause) | `er003_b1_p9a_audio.py::silence_stereo()` | そのまま再利用 | segment間の間 |
| Key Phraseブロック組立(番号→EN→JA→EN repeat) | `er003_b1_p9a_audio.py::build_key_phrase_block()` | そのまま再利用 | B1 Key Phrase仕様(English→Japanese→English)と同一順序 |
| Assembly(timeline結合) | `er003_v1_n3_01_assemble.py::assemble_with_timeline()` | そのまま再利用 | Family C固有の物理構造(A2/B1とは異なる)をseqとして渡すだけ |
| ヘッドルーム安全弁 | `er003_v1_n3_01_assemble.py::apply_headroom_safety_valve()` | そのまま再利用 | 完成ミックスのpeak超過防止 |
| Audio Validation Gate(共有) | `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()` | そのまま再利用(新規level文字列`"FAMILY_C_TRIAL_09"`を渡すのみ、既存level辞書は無変更) | tts_generation_results.jsonを本Trialで作成し、既存Gateへそのまま渡す |
| player(標準フォーマット) | `audio_review_player.py`(PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11) | そのまま再利用 | Seek/Segment・voice/Script/個別音声の標準テーブル |
| wav I/O | `er002_common.py::read_wav_float()`/`write_wav_float()` | そのまま再利用 | 全segment |

**確認できたこと**: A/B-Familyの「仕組み」(TTS retry構成・Gain・Assembly
primitive・Audio Validation Gate・player)は、いずれも記事の物理構造
(A2の11パート、B1の5区切り等)に依存しない粒度で共通部品化されており、
Family Cの全く異なる物理構造(ひと続きのStory、Point One/Two無し)でも
そのまま呼び出せた。「Family Cだから新しい仕組みが必要」という仮定は
再確認の結果あたらなかった。

新規に必要だったのは、(1)これらprimitiveを束ねるorchestration
コード(Family C固有の物理構造を持つため、A2/B1の`load_a2_sources`/
`apply_a2_gain`/`build_a2_timeline`等の記事構造依存コードはそのまま
使えず、Trial専用に新規記述)、(2)本文からのsegment分割ロジック(引用符
検出による2-voice分割)、(3)Preview/Support 1/2のrole instruction文言、
の3点のみ(下記2節以降)。

---

## 2. 最小episode構造(1案)

A-FamilyのMain Story/Point One/Point Two/In One Line構造は持ち込まない。
本文はひと続きのStoryとして扱い、リスナーに分析構造を聞かせない。

| # | セグメント | 内容 | voice |
|---|---|---|---|
| 1 | topic_intro_en | "Home Robots"(英語タイトル) | Aoede(narrator) |
| 2 | topic_intro_ja | "ホームロボット"(直訳) | Aoede(narrator) |
| 3 | preview_ja | 短い日本語Preview(2文程度) | Aoede(narrator) |
| 4 | key_phrase_1〜5 | 番号→英語→日本語gloss→英語(repeat) ×5 | 番号=Charon(既存共有資産)、英語/日本語gloss=Aoede(narrator) |
| 5 | story(前半) | 本文冒頭〜「made life easy」まで(段落0〜9、ロボットの日常的な発話2箇所を含む) | Aoede(narrator) / Charon(robot) |
| 6 | support_1_ja | 転換点直前のListening Focus(短い日本語コメント) | Aoede(narrator) |
| 7 | story(後半) | 母親来訪〜物語終了まで(段落10〜33、UI表示文+ロボット発話2箇所を含む) | Aoede(narrator) / Charon(robot、UI含む) |
| 8 | support_2_ja | 物語終了直後の短い余韻コメント | Aoede(narrator) |

Key Phrase intro等の口頭ブランディング文言(「それでは、Key Phrasesです」
等)は新設しない(仕組みを増やしすぎない方針、Preview→Key Phraseへ
pause 0.7秒で直接つなぐ)。番号読み上げ("One."〜"Five.")は、**設計修正
(runtime実測を受けて)**: 当初Aoede(narrator)で新規生成する計画だったが、
実際にHome robotsで生成した結果、短い単語単独の発話("Three."/"Five.")で
ASRが非英語スクリプトへ誤って書き起こすTRUE_CONTENT_MISMATCHが3回とも
発生した(CURRENT_SPEC.md「`default`[No.9 A2 kp2_en]個別例外」と同種の
既知の短小語不安定性)。番号読み上げは記事非依存の定型文言であるため、
既存B1/A2 Production共有資産(Charon、`num_one_charon.wav`〜
`num_five_charon.wav`、`er003_v1_n3_01_assemble.py::B1_SHARED_NAMES`が
参照する既存資産と同一ファイル)をそのまま再利用する方式へ修正した
(追加TTS/ASR不要、追加費用¥0)。Key Phrase本体(英語Component/日本語
gloss)は引き続きAoede新規生成のまま無変更。番号=Charon(Navigator役)・
本体=Aoedeという分担は、既存B1 Voice構成(「Navigator/Support[Charon]:
Key phrases intro/番号」)にも実は近く、物語本文の2-voice設計
(narrator=Aoede/robot=Charon)とは独立した層(episodeのNavigation要素)
として整理できる。

---

## 3. Preview仕様

既存Preview仕様(A2: 日本語、2文程度・80〜110字目安、先出し禁止)の
編集原則をそのまま踏襲する(技術仕様[model=`gemini-3.1-flash-tts-preview`
相当、voice=Aoede]は`generate_narration_snippet_verified_strict()`が
`language="ja"`で自動的に使う値へ一本化)。role_instruction文言は
Trial専用の新規文言(A2 PREVIEW_ROLEはcomment_1/comment_2前提のnews
構造向けのため、そのままの流用はしない。「結末・中心の問いの答えを
先に明かさない」「具体的出来事を先出ししない」という原則は同じ)。

生成された実際のPreview文は本REPORT/RESULT_PACKETに記載する(実行
結果、runtime evidence)。

---

## 4. Key Phrase仕様

既存A/B-Family正式仕様をそのまま採用する。

- 個数: 5件/記事(既存と同じ)
- 選定方式: Strategy L(Listening Blocker Ranking)+ Canonicalization(既存関数`run_key_phrases()`をそのまま呼ぶ)
- 提示順序: English → Japanese → English(反復)(B1 Key Phrase仕様と同一、`build_key_phrase_block()`をそのまま使用)
- 日本語gloss: 表示用(`japanese_gloss`)とTTS用(`japanese_gloss_tts`)を分離する既存仕様をそのまま使用
- 英語Component生成: Primary(Minimal instruction、最大2回)→Fallback(English lock、最大2回)、合計最大4回のProduction正式retry構成(`generate_key_phrase_component_verified()`)
- disfluency QA: 既存どおり英語Componentへ適用(`disfluency_qa=True`)

Home robotsで実際に生成した5件(英語/日本語gloss/位置)はRESULT_PACKETに記載する。

---

## 5. 日本語support/Comment仕様

既存Comment 1〜4(A2)をそのまま4つ全部持ち込まない。小説的な記事の
余韻を解説で壊さないため、ユーザー検証に最低限必要な2箇所だけへ絞る。

| Support | 位置 | 役割 | 長さ目安 |
|---|---|---|---|
| support_1 | 段落9(「made life easy」)の直後、段落10(母親来訪)の直前 | 転換点直前のListening Focus(次に何が起きるかへ軽く注意を向ける、結末は明かさない) | 1文程度・40〜70字 |
| support_2 | 物語終了直後 | 短い余韻コメント(意味の説明・結論の言い換えをしない、聞き手が自分で考えたくなる短い問いかけ/一言のみ) | 1文程度・30〜60字 |

Fact解説・現在技術解説・Current Fact・研究統計は一切含めない(この記事は
CURRENT FACT 0件のフィクションであり、そもそも解説すべきFactが無い)。
生成された実際のsupport textは本REPORT/RESULT_PACKETに記載する。

---

## 6. Voice/TTS仕様

### 6-1. 候補比較

| 候補 | 「誰が話しているか分かる」 | 小説として自然 | リスニングで混乱しない | 制作コスト | 量産性 |
|---|---|---|---|---|---|
| A: 全文single narrator | △(台詞も地の文も同じ声、区別は文脈のみ) | ○ | ○ | 最小 | 最大 |
| B: narrator+dialogueのみ声変更(全会話が1声) | △(Maya/mother/robotが同一声で頻繁に交代する場面[段落15〜38]で混同しうる) | △ | △ | 小 | 高 |
| C: narrator+Maya・mother・robot分離(3声) | ◎ | ○ | ○ | 中(新規voice資産3種) | 中 |
| **D(採用): narrator(Maya・mother含む)+robotのみ声変更(2声)** | ◎(人間か機械かが即座に分かる、本作のCore Provocationと一致) | ◎ | ◎(ロボット発話は全6箇所[段落3×2、6×2、16、18]+UI 1箇所のみで頻度が低く混乱しない) | 小(既存Charon/Aoedeのみ、新規voice資産0) | 高 |

### 6-2. 採用理由(D: 2-voice設計)

- 既存B-Family Voicesの3声/2声可変Writer基盤とは別に、Family Cは
  「小説」であり登場人物の心理的分担よりも「便利さが人間から選択を
  奪っていく」という中心の問い(human vs machine)が主題である。
  robotの声だけを区別することが、この主題と直接一致する。
- 記事本文を通読した結果、ロボットの直接引用発話は6箇所+UI表示1箇所
  のみで、Maya/motherの発話はナレーターがそのまま読んでも文脈
  (「Maya said」「her mother said」等の地の文)で話者を追いやすい。
- 新規voice資産(3声候補で必要になる3人目のvoice)を増やさず、
  既存Aoede(A2/B1本編ナレーター)・Charon(B1 Navigator)をそのまま
  転用でき、制作コスト増加が最小。
- ロボットの発話は物語前半(親しみやすいサービス)で2回、後半の
  重大な選択の場面でわずか2回(「Both plans have advantages.」
  「I need your preference.」)のみに減り、その後は完全に沈黙する。
  声の切り替え自体が「ロボットが人間の問いに答えられなくなっていく」
  という物語の展開を音で表現する効果を持つ(装飾的な多声化ではなく、
  Core Provocationと結びついた最小限の音声差別化)。

---

## 7. UI表示文の読み上げ仕様

対象: `**CARE HOUSE: more sleep for Maya.**` / `**HOME: more time with
her mother.**`(壁に表示される2行、記事本文中のMarkdown太字)。

| 候補 | 意味の保持 | 自然さ | 採用 |
|---|---|---|---|
| narratorがそのまま読む | ○ | △(地の文と区別がつかず、UI表示だという性質が伝わらない) | |
| 一部を音声では省く | ×(意味欠落、禁止事項に抵触) | - | 不採用(禁止) |
| **system/robot voiceとして読む(採用)** | ○ | ◎(壁に表示された内容だと直感的に伝わる、ロボットが提示した2つの選択肢という物語上の意味とも一致) | ✓ |

採用方式: 6節のrobot voice(Charon)で読む。TTS入力はMarkdown太字記号
`**`を除去し、2行を1文相当として自然に読む(`normalize_for_tts()`、
意味・語順は変更しない)。「CARE HOUSE: more sleep for Maya. HOME:
more time with her mother.」という完全な文言をそのまま読み上げ、
一切省略しない。

---

## 8. 人物名ルール(妥当性確認)

暫定案: 主人公は固有名可/その他の人間は関係性表現/AI・robotは理解に
有益なら固有名可/不要な固有名を増やさない。

Home robots記事での実測: 主人公"Maya"(固有名、主人公)、"her mother"
(関係性表現、固有名なし)、"the robot"(固有名なし、"it"で受ける)。
新規固有名詞は0件のまま。暫定案はこの記事に対して**そのまま妥当**
であり、新しいValidatorは不要と判断する(既存本文を追認するのみで、
本文を変更する必要のある不一致は見つからなかった)。

---

## 9. A2/B1の扱い(QCD表、USER_DECISION_REQUIRED)

### 9-1. 現在の契約(事実確認)

`er013_family_c_future_writer_08.py`(Trial-08 Writer)のprompt本文
(`[Length and level]`節)を確認した結果、Home robots記事は**A2レベル
のみ**で生成されている("Write for an A2-level English learner"、
target length ≈350語[許容300〜420語]、B1相当の別本文は生成されて
いない)。`word_count.json`実測は429語で、acceptable_range[300,420]
を**外れている**(`within_acceptable_range: false`)ことも確認した
(Trial-08時点の既知事実、本タスクでは記事本文を変更しないため語数超過
は未修正のまま)。

### 9-2. B1追加のQCD概算

| 項目 | 内容 |
|---|---|
| Quality | B1は「B2本文+Support」ではなく、Verified Fact Ledgerから独立生成するのがA-Family正式仕様(CURRENT_SPEC.md「B1(独立生成Natural Spoken News English)」節)。Family Cのフィクション記事にはVerified Fact Ledgerが存在しないため、この既存B1生成経路をそのまま使えない。B1相当を作るなら「同じStory Coreから、A2より自然な大人向け英語で独立再生成する」という新しいWriter手順が必要(Core Provocation・結末は変えない前提でも、文章自体を新規生成する点でスコープ外[Writer改善禁止]に抵触しうる) |
| Cost | 独立Writer 1回(LLM)+Key Phrase独自選定+TTS/Assembly一式で、A2一式とほぼ同額(本Trialの実測総額の概ね2倍)が必要 |
| Delivery | 本タスクのスコープ(記事本文固定・Writer改善禁止)と直接に矛盾するため、今回は実施していない |

### 9-3. 提案(USER_DECISION_REQUIRED)

Family Cは、まずA2 1レベルのみでユーザー検証を進め、Home robots/The
future of memory/Digital twins of ourselvesの3本をA2で揃えてから、
ユーザー評価(「未来を題材にした小説になっている」等の指摘への反応)を
踏まえてB1追加要否を判断することを提案する。理由: (1)3本並べての
ユーザー評価が優先度として先にあるべき、(2)B1追加はWriter改善([禁止
事項]に抵触しうる新規スコープ)を伴う可能性が高く、今回のTrialの
「本文は変更しない」原則と両立しない。

---

## 10. Fact Safety構成

- Reader-facing本文のCURRENT FACT=0件を維持する(Trial-08時点で既に
  0件、`word_count.json`の`current_fact_marker_count: 0`で確認済み、
  本タスクでは本文を一切変更しないためこの状態は不変)。
- 本Trialが新規に生成するのはPreview/Key Phrase gloss/Support 1・2の
  4種のみで、いずれも「新しい設定・事実を追加しない」という制約を
  role_instructionへ明記した(既存Support生成仕様の「Supportは新しい
  Factを追加しない」原則の踏襲)。
- 既存の3層Fact Safety(CURRENT FACT/PLAUSIBILITY BRIDGE/IMAGINED
  FUTURE)・Fact Checker・Ledger Deviation Checkerは、本文を再生成しない
  ため今回は発火対象がない(Trial-08時点で既に完了済みの工程であり、
  本Trialで重複実行する必要はないと判断、Production変更はしていない)。
  Ledger自体も存在しない(Family Cフィクションには当初からVerified
  Fact Ledgerが無い設計)ため、「不要なCheckerを形式的に回していないか」
  という論点について、本Trialでは新たにCheckerを追加呼び出ししていない
  ことをもって整理とする(Production変更なし、Open Item候補として
  REPORTへ記載)。
