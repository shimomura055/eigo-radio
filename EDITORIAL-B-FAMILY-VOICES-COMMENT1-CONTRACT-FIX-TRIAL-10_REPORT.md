# EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10 / EDITORIAL-B-FAMILY-APPROVED-ITEMS-PRODUCTION-WIRING-01 Report

管理ID:
- 作業A: EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10
- 作業B: EDITORIAL-B-FAMILY-APPROVED-ITEMS-PRODUCTION-WIRING-01

日付: 2026-09-08
Lane: Lane B / Voices-Perspective(Comment Contract修正Trial + Production配線状況調査)

---

## 作業A: Comment 1 Contract 最小修正Trial(TRIAL-10)

### A-1. News/Discovery型Comment 1とVoices型Comment 1の役割差(調査結果)

| | News/Discovery(Production、`er003_v1_b1_scaffold_01_generate.py::COMMENT_1_ROLE`) | Voices(Trial-09、`er012_editorial_b_voices_trial_09_audio.py::VOICES_COMMENT_1_ROLE`、修正前) |
|---|---|---|
| 役割名 | Listening Focus | テーマ・場面への自然な導入 |
| 役割記述 | 「リスナーが次に何を聞けばよいか、注目点を示す。答え・結論を先に言ってはいけない」という**聞き方の案内**を明示要求 | 「これから始まるテーマ・場面へ、リスナーの意識を自然に向ける」という曖昧な記述で、聞き方の案内か内容紹介かが未分化 |
| 結果として起きた問題 | (該当なし、Production実績あり) | Trial-09実際の生成文: "Even a familiar workplace can feel very different from one person to another." — The Question(Hookの本文)の主張そのものを一文で先に述べており、MC補足なのか本文の一部なのか曖昧というユーザー指摘と一致 |

結論: Voices Comment 1のみ「役割記述」が News/Discovery の Listening Focus 相当まで明確化されておらず、その結果、内容紹介文とMC補足の中間のような出力になっていた。Comment 2〜4(Voices)は元々「橋渡し」「視点移動」という具体的な役割記述を持っており、この問題は再現していない(ユーザー確認済み、Comment 2〜4は変更対象外)。

### A-2. 修正内容(Voices Comment 1 Contractのみ、Trial定義の範囲内)

新規ファイル `er012_editorial_b_voices_trial_10_comment1.py`(root)内に
`VOICES_COMMENT_1_ROLE_TRIAL10` を定義(Trial-09の`VOICES_COMMENT_1_ROLE`・
Production Prompt本体はいずれも無変更、importして読むのみ)。

**diff要旨**:
- 役割名: 「テーマ・場面への自然な導入」→「Listening Focus」(News/Discovery
  と同じ役割名へ統一)。
- 役割記述: 「これから始まるテーマ・場面へ、リスナーの意識を自然に向けます」
  → 「リスナーがこれから聞くThe Questionに対して、何に注目して聞けばよいかを
  明確に案内します(例: "Listen for ..."/"As you listen, notice ..."のような、
  聞き方を指示する話法)。テーマ・場面についての一般的な説明文や、内容に
  ついての主張・結論めいた文を語ってはいけません(悪い例:「〜は人によって
  違って感じられる」のような、The Questionの内容そのものを述べる文)」。
- 禁止事項へ1項目追加:「テーマ・場面についての一般的な説明・主張文(聞き方の
  案内ではなく、内容そのものを語ってしまう文)」。
- 既存の禁止事項3点(内容先取り禁止/Point要約語法禁止/Discovery的説明口調
  禁止)・構造ラベル非出力制約・「1文程度」の分量指定は無変更で維持(Reference
  Exampleの「要約しない・答えを先取りしない・どちらが正しいか評価しない」
  という既存方向性を壊さないため)。
- Comment 2/3/4のRole(`VOICES_COMMENT_2/3/4_ROLE`)は一切変更していない
  (importで参照すらしていない。今回はComment 1のみ再生成)。

### A-3. 再生成結果

同一記事(`er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`、
Trial-09と同一、再生成なしで読み取り専用参照)・同一Context(The Question本文)
に対し、Production Writer primitive(`er003_v1_b1_scaffold_01_generate.run_support_text`、
Trial-09と同一関数)をそのまま呼び出した。

| | 旧(Trial-09) | 新(Trial-10、修正Contract) |
|---|---|---|
| テキスト | "Even a familiar workplace can feel very different from one person to another." | "As you listen, notice how the question compares different reactions to the same place." |
| 性質 | The Questionの主張を先に述べる説明文(MC補足か本文か曖昧) | Listening Focus文(聞き方の案内、"As you listen, notice..."型)。内容の具体詳細(assigned desks/shared seating等)は先出ししていない |

生成model: `gpt-5.6-luna`(`routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)`、
Trial-09と同一routing)。1回目のattemptでOK(retryなし)。

### A-4. TTS + ASR Gate結果

Standard同期TTS、Production primitive `er003_v1_sing01_voice01_generate.generate_charon_english`
(Trial-09のcomment_1-4生成と同一関数・同一`style_prefix_override`
[`B1_PREVIEW_STYLE_PREFIX_CALM`]・`disfluency_qa=True`)を1 segmentだけ実行。

- `status=OK`、`asr_verified=True`(1回目のattemptでPASS、retryなし)
- `audio_classification=EXACT_MATCH`(ASR文字列がcanonical textと完全一致)
- `disfluency_checked=True`、`disfluency_evidence.flagged=False`(反復検出なし)
- `clipping_detected=False`
- wav: `er012_output/editorial_b_voices_trial_10_comment1/narration/comment_1.wav`
- 詳細JSON: `er012_output/editorial_b_voices_trial_10_comment1/audit/comment1_tts_result.json`

### A-5. コスト

累積¥0.62(内訳: openai[scaffold] ¥0.06 + gemini[TTS] ¥0.54 + openai_asr ¥0.03)。
上限¥100に対し十分な余裕(Comment 1の再生成1件+TTS1 segmentのみのため)。

### A-6. Gate 1 Trial Closeout 分類

**VALIDATED**(Trial範囲: Comment 1 Contract最小修正、ASR Gate 1回で
`EXACT_MATCH`・disfluencyなしでPASS)。

ただし以下は本Trialの範囲外・**USER_DECISION_REQUIRED**のまま:
- 修正版Comment 1テキスト自体の内容・文体をユーザーが試聴確認すること
  (本Trialはwav 1本のみ生成、player.htmlは意図的に作成していない)。
- Voices Comment Contract全体の`APPROVED_FOR_PRODUCTION`(Comment 1修正版の
  ユーザー確認後に判断)。
- n=1(1回の生成・1回のTTS)であり、再現性(同じContractで複数回生成しても
  同様の「Listening Focus型」出力になるか)は未確認。

### A-7. 変更・生成ファイル一覧(作業A)

- 新規: `er012_editorial_b_voices_trial_10_comment1.py`(root)
- 新規: `er012_output/editorial_b_voices_trial_10_comment1/audit/comment1_regeneration.json`
- 新規: `er012_output/editorial_b_voices_trial_10_comment1/audit/comment1_tts_result.json`
- 新規: `er012_output/editorial_b_voices_trial_10_comment1/audit/run_summary.json`
- 新規: `er012_output/editorial_b_voices_trial_10_comment1/audit/raw_usage_log.jsonl`
- 新規: `er012_output/editorial_b_voices_trial_10_comment1/narration/comment_1.wav`
  (+ `narration/attempts/comment_1_attempt1_englishstyleprefix.wav`、
  `er011_human_review_lock_01`の既存attempt保存機構による自動生成物)
- Trial-09本体(`er012_editorial_b_voices_trial_09_audio.py`・
  `er012_output/editorial_b_voices_trial_09_audio/`配下)は無変更(importして
  読むのみ)。player.htmlは作成していない。

---

## 作業B: 採用4項目のProduction配線状況調査・配線(WIRING-01)

### B-1. B-Family ProductionパスがどこまでProductionへ存在するか(調査結果)

Grep調査(`CURRENT_SPEC.md`、`OPEN_ITEMS.md`のOPEN-112/120行、
`ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md`、
`ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`)の結果:

1. **Editorial Type registry自体がProductionコードに存在しない**。
   OPEN-112(Editorial Type Production Wiring Reconciliation)が明記する通り、
   実際のProduction Writer(`er003_v1_n3_01_articles_generate.py`等)には
   「Editorial Type」という概念自体が実装されていない(POOL_TOPIC_MASTER.md上の
   構想のみ)。
2. `CURRENT_SPEC.md`には「Lane B」「B-Family」「Voices」という語が
   一件も存在しない(Grep 0件、見出し行を除く)。
3. `OPEN_ITEMS.md`のOPEN-120は、Trial-03〜Trial-09までの全履歴を
   「**Production変更ゼロ**」「コード・Prompt本体への変更もゼロ」と明記して
   おり、B-Family関連の実装はすべて`er012_editorial_b_voices_trial_0X*.py`
   というTrial番号付きファイル内に閉じている。**「Lane B構造定義」に
   相当する、Trial番号を持たない独立したProduction/canonicalファイルは
   現時点で1つも存在しない。**
4. `ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`は、Discovery/Why用
   Writer Prompt(`COMMON_BLOCK_TEMPLATE`・`COMMENT_1〜4_ROLE`・
   `PREVIEW_ROLE`等)がVoices向けにどう再設計されるべきかを**設計レベルで
   分析したのみ**であり、「Editorial Type Module本体(実装)は次タスク以降の
   スコープ」と明記して終わっている(実装ゼロ)。

**結論**: B-Family(Voices)の「Production正式初回経路」はGate 3の意味で
一切存在しない。存在するのはTrial番号付きスクリプト群のみ。したがって、
Gate 3チェックリストの「Production runtimeでの実発火」という要件は、
そもそもB-Familyを実行する本物のProduction runtime(記事執筆〜音声化〜
配信までの一連の入口)が存在しないため、**この4項目単体では原理的に
満たせない**(Comment Contract未承認の有無に関わらず)。

### B-2. 採用4項目それぞれの現状・配線に必要な変更・retry/fallback整合

#### (1) Voice A=Algieba / Voice B=Erinome / Narrator見出し=Aoede 固定

- **Narrator=Aoede**: `point_headings.generate()`
  (`er003_v1_sing01_point_headings_aoede.py`)は**既存Production関数で
  すでにAoede固定**であり、News/Discovery側の実際のProduction経路
  (`er003_v1_n3_01_tts_generate.py`)でも同一関数が無変更で使われている
  (Grep確認済み: `point_headings.generate(`の呼び出し元8ファイル中、
  `er003_v1_n3_01_tts_generate.py`がProduction本体)。**この部分は追加の
  配線作業が不要**(すでに共有Production関数として存在し、Trial-09も
  この関数を無変更のまま呼んでいるだけ)。
- **Voice A=Algieba/Voice B=Erinome**: 現状、Trial-09スクリプト内の
  `generate_voice_body_wide_margin()`という**Trial専用関数**(Production
  `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`
  のロジックを丸ごとコピーし、声(voice_name)だけ引数化したTrial限定コピー)
  としてのみ存在する。Production側の`news_tail_fix.py`自体は単一固定声
  (`p9a.VOICE_NAME`)のみを想定した設計で、voice引数を持たない。
  - **配線に必要な変更**: 技術的には、この`generate_voice_body_wide_margin`
    相当の関数をTrial番号を持たない独立したLane B専用ファイルへ「昇格」
    させること自体は、Lane A(`news_tail_fix.py`本体)を一切変更せずに
    Lane B側ファイルのみで完結可能(Trial-09で実際に技術検証済み・
    ASR Gate通過実績あり)。
  - **ただし実装を見送った理由**: この関数の唯一の呼び出し元は
    B1 Voices用timeline/Assembly(下記(2))であり、そのAssembly自体が
    Comment Contract未承認により完成しない(作業指示5項)。加えてB-1の
    通り、そもそもB-Family用のProduction runtime(記事執筆〜配信までの
    入口)自体が存在しない。呼び出し元のない関数だけをLane B側へ新規
    ファイルとして複製しても、Gate 3の「Production runtimeでの実発火」
    ・「必要testのPASS」を満たせず、かつGate 4(Dangling Reference
    Check)上、使われないコードの複製を増やすリスクがあるため、**本タスク
    では新規ファイル作成という形の実装は見送った**(判断根拠は本節、
    実装要否はFableへ差し戻す)。
  - **retry/fallback整合**: Trial-09の実装は、Voice A/B候補(Algieba/
    Erinome)がAPI技術的に利用不可の場合のみfallback(Schedar/Sulafat)へ
    切り替える設計(`resolve_voice_names()`)。この設計は既存のTTS技術的
    retry(`common._call_tts_with_retry`、Production既存)・ASR Cascade
    (`er006_secondary_asr_01`、Production既存)とは独立した「声選択」の
    fallbackであり、既存の安全装置(Human Review Lock、`entity_only_diffs`
    はblind retryしない等)を回避・変更するものではないことをTrial-09の
    コードで確認済み。**新たな整合作業は不要**(Trial-09実装をそのまま
    踏襲すれば足りる)。
  - なお、Voice見出し(Title Case、"One Voice:"/"Another Voice:")に関する
    既知の未解決問題(`OPEN-125`: `capitalized_flags()`ヒューリスティクスが
    固有名詞見出しラベルを誤分類しうる、検証Trial起票のみで未実装)が
    存在する。Voice A/B固定を配線する場合、このOPEN-125の解消状況も
    合わせて確認が必要(現状: 未実装のまま)。

#### (2) Tension slot「Where the Difference Comes From」を正式構造へ追加

- **現状**: 既存の11個固定segment名をハードコードしているProduction
  `asm.build_b1_timeline()`(`er003_v1_n3_01_assemble.py`)には対応する
  slotが存在しない。Trial-09は`build_b1_voices_timeline_trial09()`という
  **Trial専用の代替timeline builder**を新設し、Production側の
  `asm.build_b1_timeline()`自体は無変更のまま、他のProduction primitive
  (`apply_b1_gain`/`assemble_with_timeline`/`apply_headroom_safety_valve`/
  `build_b1_key_phrase_blocks`)だけを無変更で呼び出す形でTension slotを
  実現している(ASR Gate込みで音声化実績あり、Trial-09で確認済み)。
- **配線に必要な変更**: (1)と同様、この代替builderをLane B専用の独立
  ファイルへ昇格させること自体はLane A(`asm.build_b1_timeline()`本体)を
  変更せずに完結可能。ただし(1)と同じ理由(呼び出し元となる完成
  Assemblyが存在しない・B-Family用Production runtime自体が不在)により、
  本タスクでは実装を見送った。
- **retry/fallback整合**: Tension segment自体は他segmentと同じ
  `generate_voice_body_wide_margin`等の既存retry/ASR Gateを経由する
  (Trial-09で確認済み)。11-part固定schemaを前提にした既存のGate参照
  コード(`asm.load_b1_sources()`内のGate検証等)がTension slotを
  「未知のsegment」として扱っていないかは、Trial-09では「Trial専用
  timelineのみ差し替え、他は無変更」という設計のため実害は生じていない
  が、正式なslot設計(schemaへ正式追加するか否か)はユーザー決定
  (`USER_DECISION_REQUIRED`、OPEN-120 (h)で既出)としてOPEN_ITEMS.mdに
  記録済み(本タスクでは`OPEN_ITEMS.md`を編集していない)。

#### (3) Key Phrase位置=Preview直後(現状維持)

- **現状**: Trial-09のtimelineは、既存B1 Production構造と同じ配置
  (Preview intro→Preview→Notification→Key phrases intro→Key Phrase群→
  Notification→Full story…)をそのまま踏襲している(Trial-09コード
  コメントに明記: 「Key Phraseの位置のみ既存B1構造どおり据え置いた」)。
- **配線に必要な変更**: **なし**。ユーザー決定は「現状維持」であり、
  Production構造・Trial構造のいずれも既にこの配置のため、変更対象自体が
  存在しない。

#### (4) Voice A/Bの一人称"I"記述採用

- **現状**: Voices記事本文(Trial-07由来)は一人称"I"で書かれているが、
  これはTrial-06でWriterが自発的に選択した結果であり(`OPEN-120 (c-2)`
  記載)、Production Writer Prompt(`er003_v1_n3_01_articles_generate.py`)
  へ一人称記述を指示する仕組みは存在しない。Voices用記事生成は
  `er012_editorial_b_voices_trial_07.py`等のTrialスクリプトが
  Production Writer関数(`gen = er003_v1_n3_01_articles_generate`)を
  **import して呼び出してはいる**が、Discovery/Why固有にハードコードされた
  Common Writing Contract(Main Story役割・Point役割・Preview role等、
  `ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`が詳細に指摘)を
  そのまま使っており、Voices固有の「Perspectiveごとの一人称記述」を
  正式にモジュール化する仕組み(Editorial Type Module)は未実装。
- **配線に必要な変更(Lane A、STOP)**: 一人称記述を正式にProductionへ
  組み込むには、`er003_v1_n3_01_articles_generate.py`(Lane A共有
  Productionコード)へEditorial Type Module機構(Common Writing Contract
  とEditorial Type固有部分の分離)を導入する必要がある。これは
  `ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`が既に設計分析を
  行った範囲そのものであり、同Reportは実装を「次タスク以降のスコープ」
  として明示的に持ち越している。**本タスクの委任範囲(Lane B側ファイルで
  完結する範囲)を超えるため実装せず、ここでSTOPして報告する。**
  Fableへ: Lane A(`er003_v1_n3_01_articles_generate.py`)へのEditorial
  Type Module導入は、別途独立したタスクとして扱うことを推奨する
  (既存ER-010 Reportの設計をベースに実装可否をユーザー判断へ)。

### B-3. 実装状況まとめ

**本タスクではLane B側ファイルへの新規コード実装を行っていない**
(理由: 上記(1)(2)は技術的にはLane B側ファイルのみで完結可能だが、
呼び出し元となるB-Family用Production runtime自体が存在せず、実装しても
Gate 3の「Production runtimeでの実発火」を満たせないダミー実装になる
ため。(3)は変更対象なし。(4)はLane A変更が必要なためSTOP)。
`run_project_regression.py`による回帰実行は、Production/共有コードを
一切変更していないため本タスクでは実施していない。

4項目の配線状態(Sonnet自身は`PRODUCTION_WIRED`/`APPROVED_FOR_PRODUCTION`
を宣言しない、判断はFableへ):

| 項目 | 状態 |
|---|---|
| (1) Narrator=Aoede | 追加配線不要(既存Production関数がすでに満たす) |
| (1) Voice A=Algieba/Voice B=Erinome | **PRODUCTION_WIRED候補(未実装、Fable受入待ち)** — 技術的にLane B側で実装可能なことはTrial-09で検証済みだが、呼び出し元となる完成Production経路が不在のため本タスクでは実装を見送った |
| (2) Tension slot | **PRODUCTION_WIRED候補(未実装、Fable受入待ち)** — (1)と同じ理由 |
| (3) Key Phrase位置 | 変更不要(現状維持がそのままProduction/Trial双方の既存構造と一致) |
| (4) 一人称"I" | **未配線・Lane A変更が必要(STOP)** — `er003_v1_n3_01_articles_generate.py`へのEditorial Type Module導入が前提。本タスクでは実装しない |

補足: B-Family Production経路は、Comment Contract未承認に加え、
そもそもB-Family用のProduction runtime自体が未確立という、より根本的な
理由でも完成しない状態にある。

---

## 未確認事項

- 修正版Comment 1(作業A)の内容・文体についてのユーザー最終確認
  (本Trialではwav 1本のみ生成、試聴用UIは意図的に未作成)。
- Comment 1 Contractの再現性(n=1、複数回生成した場合も同様の
  Listening Focus型出力になるか)。
- OPEN-125(Voice見出しラベル誤分類の可能性)が(1)Voice A/B固定配線に
  実際に影響するかどうかの実測(本タスクでは調査していない)。
- Tension slotの正式schema追加要否(11-part固定か可変schemaにするか)は
  ユーザー未決定のまま(OPEN-120 (h)で既出、本タスクでは新規調査せず)。

---

## 追加委任: Fable修正指示(1回目)への対応(管理ID同一、Comment 1のみ)

Gate 7受入時のFable懸念2点への対応:
(a) 修正版Comment 1文中の"the question"がVoices構造の内部section名
("The Question")の漏出に見えるおそれ。
(b) n=1のみで、Contract修正の再現性が未確認。

Contract本体(`VOICES_COMMENT_1_ROLE_TRIAL10`)は**無変更**。新規ファイル
`er012_editorial_b_voices_trial_10_comment1_reproducibility.py`(root)を
追加し、同一Contract・同一入力(Trial-07記事の`hook_body`、Trial-09/10と
同一)に対しComment 1テキスト生成のみをさらに2回実行(run2/run3)。
TRIAL-10本体の1回目生成(run1、TTS+ASR PASS済み)と合わせて合計n=3。
TTSは実行していない(テキスト生成のみ、LLM費用のみ)。出力先:
`er012_output/editorial_b_voices_trial_10_comment1/reproducibility/`
(新規サブディレクトリ、TRIAL-10本体の既存ファイルは一切上書きしていない)。

### 3本の生成文

| run | テキスト |
|---|---|
| run1(TRIAL-10本体、TTS+ASR `EXACT_MATCH`でPASS済み) | "As you listen, notice how the question compares different reactions to the same place." |
| run2(本追加委任、新規生成) | "As you listen, notice the contrast between the two ways people experience the same place." |
| run3(本追加委任、新規生成) | "As you listen, notice the words that show how people feel about a place." |

### 機械的チェック表

判定は`er012_editorial_b_voices_trial_10_comment1_reproducibility.py::check_text()`
による機械的proxy(正規表現・キーワード一致、人手確認の代替ではない)。

| run | (i) 聞き方の案内型("Listen for"/"As you listen, notice"等) | (ii) 要約・答えの先取り・評価をしていないか | (iii) 内部section名("the question"/"voice a"等)の漏出 |
|---|---|---|---|
| run1 | 該当(marker検出: "as you listen"/"notice") | 該当なし(要約・結論めいた断定文は検出されず) | **漏出あり: "the question"を含む** |
| run2 | 該当(marker検出: "as you listen"/"notice") | 該当なし | 漏出なし |
| run3 | 該当(marker検出: "as you listen"/"notice") | 該当なし | 漏出なし |

結論: (i)(ii)は3本とも安定して「Listening Focus型」(聞き方の案内、内容の
断定的要約なし)を満たしており、Contract修正自体の方向性(News/Discovery型
Listening Focusへの寄せ方)は再現性がある。ただし(iii)は**run1のみ**、
生成文中に小文字の"the question"というフレーズが偶然にも英語として自然な
一般名詞句("the question"=「その問い」という一般的な意味)として出現して
おり、これがFableの懸念(a)である「Voices構造の内部section名"The Question"
の漏出に見える」問題と一致する。run2/run3では同じ懸念に該当するフレーズは
機械的チェック上検出されなかったが、n=3という少ない試行数では「run1のみの
偶然」か「Contractの構造的な弱点(禁止事項に"the question"という語その
ものの出力を明示的に禁止していない)」かを判別できない。Contractの禁止
事項リストには「出力する文章自体に"Part 1"・"Part 2"・"Hook"・"The
Question"のような制作内部の構造ラベルを含めないでください」という記述が
既にあるが、これは大文字表記の固有ラベルを想定した文言であり、"the
question"という小文字・一般名詞句としての出現(文法的には合法だが、
Podcastの構造("The Question"というPart名)と偶然一致してリスナーに紛らわしい
表現)を明示的にはカバーしていない可能性がある。

### Contract追加最小修正案(提案のみ、未実装)

以下はFableまたはユーザーの判断待ちであり、Contract本体・Productionコードへ
一切実装していない:

1. 既存の【重要・出力への制約】段落へ1行追加する案:
   「"the question"という語句自体(大文字・小文字を問わず、番組構成上の
   Part名"The Question"と紛らわしい表現)を出力文中で使わないでください。
   代わりに、話題そのもの(例: "this office question"ではなく単に話題の
   内容を指す一般的な言い回し、または指示語のみ)で言い換えてください。」
2. あるいはより軽量な代替案として、禁止事項の既存項目
   「テーマ・場面についての一般的な説明・主張文(聞き方の案内ではなく、
   内容そのものを語ってしまう文)」の直後に、「"the question"という単語
   そのものの使用」を悪い例として追記する(既存の悪い例文言の拡張のみ、
   新しい禁止カテゴリを増やさない軽量な差分)。

上記いずれもテキストレベルの1〜2行差分であり、本追加委任の範囲(提案のみ)
としてここに記録する。実装・再生成・ASR Gate再実行はFableの次回指示待ち。

### 再現性確認(n=3)

- 合計n=3(run1: TRIAL-10本体、TTS+ASR Gate PASS済み。run2/run3: 本追加
  委任、テキストのみ新規生成、TTS未実行)。
- (i)(ii)は3/3で安定(Listening Focus型の話法・内容の断定的要約なしを
  機械的チェック上維持)。
- (iii)は1/3(run1)で内部section名と紛らわしい語句("the question")の
  漏出が検出された。2/3(run2/run3)では検出されなかったが、n=3という
  試行数では「Contract側の構造的リスク」であることの断定にも「run1のみの
  偶然」であることの断定にも証拠が不十分であり、上記のContract追加修正案
  (未実装)をFableへ提案する。
- 詳細JSON: `er012_output/editorial_b_voices_trial_10_comment1/reproducibility/reproducibility_runs.json`
  (`raw_usage_log.jsonl`含む)。
- 追加LLM費用: ¥0.10(openai、scaffold呼び出し2回分、TTSなし。TRIAL-10本体の
  累積¥0.62と合算しても¥0.72、上限¥100に対し十分な余裕)。
- 使用スクリプト(新規): `er012_editorial_b_voices_trial_10_comment1_reproducibility.py`
  (root)。Contract本体・TRIAL-10本体スクリプト・TRIAL-09出力は無変更
  (importして読むのみ)。
