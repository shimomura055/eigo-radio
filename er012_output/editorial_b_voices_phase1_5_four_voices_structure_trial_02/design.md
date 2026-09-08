# EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-STRUCTURE-DESIGN-TRIAL-02

固定テーマ: "Should companies use AI to screen job applicants?"
4 Voices(ユーザー承認、案A由来): (1) Applicant、(2) Recruiter / Hiring Manager
(統合)、(3) Business / Efficiency、(4) Fairness / Legal / HR Governance。
範囲: **現行2 Voices前提のB-Family構造を4 Voicesへどう拡張するかの構造設計・
比較のみ**。記事本文・音声は生成していない。Contract/コード編集はしていない
(すべて未承認仕様として提示するのみ)。LLM API呼び出しなし(¥0)。

---

## 0. 現行構造の事実確認(引用のみ、読み取り専用)

出典ファイル(いずれも変更していない):
- `er012_b_family_editorial_type_registry_01.py`(Editorial Type registry、
  APPROVED_FOR_PRODUCTION済み4項目を集約)
- `er012_b_family_voices_production_01.py`(5区切りparser・timeline builder)
- `EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`(Phase 1
  完成episode実測値)
- `EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-AXIS-DESIGN-TRIAL-01_REPORT.md`
  / `er012_output/editorial_b_voices_phase1_5_four_voices_axis_trial_01/design.md`
  (4 Voices選定軸、ユーザー承認案A)

### 0-1. 物理構造(`registry.py` L43-61, 172-184)
- `physical_structure: "five_section"`。`SECTION_LABELS = ("hook", "voice_a",
  "voice_b", "tension", "closing")`。
- `VOICE_ASSIGNMENT = {"voice_a": "Algieba", "voice_b": "Erinome", "narrator":
  "Aoede"}`。`VOICE_FALLBACK = {"voice_a": "Schedar", "voice_b": "Sulafat"}`。
- `TENSION_SLOT_APPROVED_NAME = "Where the Difference Comes From"`、
  `EXTRA_SEGMENT_NAME = "tension_reflection"`。
- `KEY_PHRASE_POSITION = "after_preview"`(現状維持)。

### 0-2. 見出しパーサー(`production_01.py` L73-98)
- `_HEADING_RE = r"^(#{2,3})[ \t]+(.+?)\s*$"`。`split_five_voice_sections()`
  は本文中の`##`/`###`見出しが**厳密に5個**でなければ`None`を返す
  (hook/voice_a/voice_b/tension/closingの5見出し)。見出し数が想定と異なる
  場合は例外的にNone→呼び出し側`build_parts()`が`RuntimeError`。
- 別の関数`split_common_sections_for_point_qa()`(Lane A共有
  `er003_v1_n3_01_articles_generate.py` L499-519)は`###`見出しが
  **厳密に2個**という別のハード制約を持つ(Point Overlap QA用、B-Family
  Voicesの5区切りparserとは別関数だが、前Trial(Axis Trial-01)がPoint
  Overlap QA拡張時の論点として引用済み)。

### 0-3. Assembly timeline(`production_01.py` L381-443
`build_b1_voices_timeline()`)
- 実際の並び: Intro→Welcome→Topic intro→Notification1→Preview intro→
  Preview→Notification2→Key phrases intro→Key Phrase 1..N→Notification3→
  Full story intro→**Comment 1**→Hook Part1/2(Aoede, no heading)→
  **Comment 2**→Point Notification(Voice A cue)→**Narrator: One Voice
  heading(Aoede)**→**Voice A body**→Point Notification(Voice B cue)→
  **Narrator: Another Voice heading(Aoede)**→**Voice B body**→
  **Comment 3**→**Tension(Aoede, no heading)**→**Comment 4**→
  Closing(In One Line)→Outro。
- Comment 1〜4はいずれもCharon(既存Production共通ナレーター)。Voice
  headingはAoede(Narrator)、Voice本体はAlgieba/Erinome。
- segment名は位置ベース(`"Voice A body (Algieba)"`のようなラベル文字列)で
  ありAssembly側は固定11-part(`asm.build_b1_timeline`、無変更)とは別の
  B-Family専用timeline。

### 0-4. Comment Contract確定文言(`registry.py` L72-146、
FINALIZE-11でAPPROVED_FOR_PRODUCTION済み)
- Comment 1: Listening Focus(内容先取り禁止)。
- Comment 2: 「One Voiceの後、続けてAnother Voice」という**単数対の
  言い回しをRole定義文自体に含む**(Voice AI提示前、Hook→Voicesの橋渡し)。
- Comment 3: 「どちらが正しいかではなく、なぜ違って感じるのか」への
  視点移動(2つの声を**両方すでに聞き終えた**ことを前提にした文言)。
- Comment 4: 表面的な対立から一段深い問いへ(結び直前)。

### 0-5. QA(前Trialの引用に基づく、本Trialでは再検証していない)
- Point Overlap QA(lexical overlap閾値)・Perspective Diversity・
  Analytical Leakage Check(6基準)は、いずれも**2 Voice間の1ペア比較**を
  前提にした設計(Trial-06/07 Report)。

### 0-6. 実測尺・語数(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`
L369, 430)
- Phase 1完成episode(2 Voices、SFX込み完全Assembly): `duration=305.135s`
  (約5分5秒)、peak=0.89571、clipping_detected=False。
- Voice A/B本文含む5区切りテキストの語数(Axis Trial-01が前Trialの実測を
  引用): Hook/Voice A/Voice B/Tension/Closing合計419〜490語(Voice A/B
  以外の固定パート(Intro/Welcome/Preview/Key Phrase/Notification/Comment
  1-4/Outro)は別途固定コストとして存在)。

---

## 1. 構造案(2〜3案)

### 案S1: 「4見出し直列」(Four Headings, Straight Line)
Hook→**Voice 1(Applicant)**→**Voice 2(Recruiter/HM)**→**Voice 3
(Business)**→**Voice 4(Legal/Fairness)**→Tension→Closing。

- 物理構造: `SECTION_LABELS = ("hook", "voice_1", "voice_2", "voice_3",
  "voice_4", "tension", "closing")`(7見出し)。`physical_structure`は
  新規値(例: `"seven_section"`)。`split_five_voice_sections()`相当の
  parserは見出し数`== 7`を要求する新関数(既存5固定関数は変更せず、
  B-Family Voices 4版として別関数を追加する案)。
- Voice順序: Applicant→Recruiter/HM→Business→Legal/Fairnessの順(当事者→
  現場→経営→監督、というプロセス上の距離が遠ざかる順)。隣接対比は
  Applicant↔Recruiter/HM(当事者と直接接する現場)、Recruiter/HM↔Business
  (現場と経営の温度差)、Business↔Legal(推進と慎重という会社内部の
  対立)を意図的に隣接させる。
- Comment: 各Voiceの間に既存Comment的な橋渡しコメントを**新設しない**
  (Comment 1〜4の4枠のまま)。Voice1→2、Voice2→3、Voice3→4の間は
  Narrator見出し(Aoede)のみで接続し、Comment的な語りかけを挟まない。
  Comment 2はHook→Voice1直前の1箇所のみ(文言はVoice1本のみを指す形に
  書き換えが必要、「One Voiceの後、続けてAnother Voice」という単数対
  表現の書き換えが必須)。Comment 3はVoice4本体終了後、Tension直前の
  1箇所のみ(4声すべてを聞き終えた前提の文言に書き換え)。
- Tension: 単一のTension区切りのまま、**本文の書き方**として「2軸の
  交差」を使う(構造上の新segmentは追加しない、内容設計のみ)。例:
  縦軸=「この状況に対する当事者性の強さ(直接影響を受けるか/決定する側か)」、
  横軸=「AI活用への態度(推進寄りか慎重寄りか)」。Applicant=当事者性高・
  慎重、Business=当事者性低・推進、Recruiter/HM=当事者性中・両義、
  Legal=当事者性中・慎重、という配置で「賛成/反対の2分割ではなく、
  誰にとって何が賭かっているかが軸によって違う」ことを描く。単純な
  4人要約にしない条件として「4者の発言を時系列で繰り返さない」
  「各Voiceの発言内容ではなく、各Voiceが背負っている責任・制約の
  非対称性を軸として言語化する」を明記する。

### 案S2: 「2ペア構造(影響側ペア→運用側ペア)+統合Tension」
Hook→[Applicant + Recruiter/HM](影響を受け・現場で直接触れる側ペア)→
**新設ペア間ブリッジ**→[Business + Legal/Fairness](会社の中の推進側と
監督側ペア)→Tension(2軸交差、S1と同じ内容設計)→Closing。

- 物理構造: 見出し数はS1と同じ7つだが、意味的に2つの「章」
  (影響側チャプター/運用側チャプター)にグルーピングする。実装上は
  `SECTION_LABELS`に加えて「チャプター境界」の概念が新規に必要
  (現行registryにはチャプターという概念自体が存在しない)。
- Comment: Hook→チャプター1の間はComment 2(書き換え要)。**チャプター1
  →チャプター2の間に新規Comment(Comment 2b相当)が必要**(現行Comment
  1〜4のFINALIZE-11契約に無い、5個目のComment枠の新設)。Comment 3は
  チャプター2終了後、Tension直前(S1と同様、4声完了後の文言に書き換え)。
- Tension: S1と同じ2軸交差の内容設計を使うが、ペア構造という物理配置
  自体が「2軸のうち1軸(影響側/運用側)」をすでに構造で先出ししてしまう
  ため、Tensionセクションでの「軸の提示」がやや冗長になるリスクがある
  (構造がすでに答えの半分を見せている)。
- QA拡張の意味論: 「ペア内の2声」と「ペア間の2声」で比較の重み付けを
  変える(ペア内は密な比較、ペア間は代表ペアのみ比較、等)という設計が
  可能だが、これは**既存Point Overlap QA/Analytical Leakage Checkが
  全ペアを均等に扱う現行の意味論を変更する**ことになり、7節で述べる
  QA拡張の「意味を変えない範囲」を超える。

### 案S3: 「Hook→対立軸提示→4 Voice→Tension→Closing」
Hook→**新設Axis Intro**(2つの軸[当事者性/態度]をナレーターが短く
フレーミング)→Voice1..4(軸に沿った対角順、例: Applicant(当事者性高・
慎重)→Business(当事者性低・推進)→Recruiter/HM(当事者性中・両義)→
Legal(当事者性中・慎重))→Tension(軸の再訪、統合)→Closing。

- 物理構造: 見出し数8つ(hook, axis_intro, voice_1..4, tension, closing)。
  現行の5区切り構造には存在しない**新segment種別(Axis Intro)**を追加
  する必要があり、3案中もっとも物理構造への影響が大きい。
- 原則抵触リスク: タスク指示の設計原則「Research is backstage. People
  are on stage.」「Tensionは4人の意見要約ではなく『なぜ合理的に見方が
  分かれるか』を描く」に対し、Voiceを聞く**前に**軸を解説してしまうと、
  Comment 3の役割(「どちらが正しいかではなく、なぜ違って感じるのか」
  への視点移動を**Voiceを聞いた後に**行う)と機能が重複・先取りして
  しまう。Tensionセクションが「もう説明済みのことの再確認」に感じられる
  リスクが高い。
- Comment: Hook→Axis Introの間、Axis Intro→Voice1の間にそれぞれ新規
  Comment相当の橋渡しが必要になり、S2よりもさらにContract拡張が大きい。

---

## 2. 比較表(タスク指定10影響点 + 実装影響)

| 影響点 | 案S1(4見出し直列) | 案S2(2ペア構造) | 案S3(軸提示先出し) |
|---|---|---|---|
| 1. 見出しブロック数 | 5→7(hook/voice1-4/tension/closing)。Narrator見出しは4個(voice1-4それぞれ)、現行と同型の拡張 | S1と同じ7見出し+チャプター概念(新規)が必要 | 8見出し(Axis Intro追加)、もっとも大きい拡張 |
| 2. five_section骨格維持 | 骨格の形(Hook/Voices/Tension/Closing)は維持、Voices部分だけ2→4に拡張 | 骨格は維持するが「章」という新しい中間層を追加 | 骨格に新segment種別(Axis Intro)を追加、骨格自体を変える |
| 3. TTS voice設計 | 4声を全部別にする案(Algieba/Erinome+新規2声)、narrator Aoedeは不変 | S1と同じ | S1と同じ+Axis Intro読み上げ役(Charon想定、既存流用可) |
| 4. Comment Contract | Comment 2・3のみ文言書き換え、**新規Comment枠なし**(4枠のまま) | Comment 2b(新規5枠目)が必要、Contract拡張が構造的に必須 | 新規Comment枠が複数(Axis Intro前後)必要、もっとも拡張大 |
| 5. Tension設計 | 単一Tension内で2軸交差を「内容設計」として実現(構造変更なし) | 2軸のうち1軸を構造(ペア分け)がすでに先出し、Tensionがやや冗長化するリスク | 軸をVoice前に説明済みのため、Tensionが「答え合わせ」に近づき原則抵触リスク最大 |
| 6. QA拡張 | 6ペア総当たり(既存ペア比較ロジックをループで6回呼ぶのみ、意味論不変) | ペア内/ペア間で重みを変える案が自然だが、既存QAの均等比較の意味論を変更してしまう | S1と同じ6ペア総当たりが必要な点は同じだが、Axis Intro自体のQA対象化が新論点として発生 |
| 7. 語数・尺 | 目標尺を後述(3節)の通り設計、単純倍増を避ける設計と両立しやすい | S1と同じ設計は可能だが、ペア間ブリッジ分のComment増で尺が余分に伸びる | Axis Intro分の尺が追加で必要、目標尺の管理がもっとも難しい |
| 8. Audio Validation Gate | segment名をvoice_a/b→voice_1..4に拡張するのみ、retry/fallback機構(guarded_generate等)はVoiceごとに同一ロジックを4回適用すれば足りる | S1と同じ+チャプター境界という新しいsegment分類が必要になり、既存Gateの「位置ベース2ブロック前提」の見直し範囲がS1より広い | 新segment(Axis Intro)がGateの必須segment一覧に新規追加される必要があり、見直し範囲が最大 |
| 9. 2 Voicesとの差 | 「会社側も一枚岩ではない」(Business↔Legal)が新たに描ける、隣接対比が明確 | 影響側/運用側という大枠の対比が明確に伝わりやすい | 軸自体を明示的に説明できる分かりやすさはあるが、Voiceの語りが軸の後追いに聞こえるリスク |
| 10. 3 Voicesとの関係 | 4者のうち1者を落とすとテーマの一側面が明確に失われる(Axis Trial-01ですでに確認済みの論点をそのまま踏襲可能) | 2ペア構造は3 Voicesにすると非対称なペア(2+1)になり構造の対称性が崩れる、3 Voicesとの相性が悪い | Axis Introは3 Voicesでも成立しうるが、そもそも軸提示自体の是非が3/4 Voices共通の論点として残る |
| 実装影響: Lane B内で閉じるか | 閉じる(B-Family専用ファイル群のみ、`registry.py`/`production_01.py`相当の拡張で完結) | 閉じるが新概念(チャプター)追加分、影響範囲がS1よりやや広い | 閉じない可能性あり(Axis Introの語り口次第でLane A共有Writerの一般的な「導入部設計」原則との整合確認が追加で必要になりうる) |
| 実装影響: Contract変更の要否 | 要(Comment 2・3の文言書き換えのみ、枠数は不変) | 要(Comment 2の書き換え+新規Comment枠1つの追加、FINALIZE-11契約の枠組み自体の変更) | 要(複数の新規Comment枠、FINALIZE-11契約への影響が最大) |

---

## 3. 語数・尺設計(単純倍増を避ける、影響点7)

**基準値**: 2 Voices実測 305.135秒(Phase 1完成episode、SFX込み)。
Voice A/B本文を含む5区切りテキスト合計419〜490語(Hook/Voice A/Voice
B/Tension/Closing、固定パート[Intro/Welcome/Preview/Key Phrase/
Notification/Comment 1-4/Outro]は別途固定コスト)。

**単純倍増した場合の見積り(避けるべき基準線として提示)**: Voice本体を
そのまま4倍(2声→4声、各声の語数を維持)すると、Voice本体だけで
現行の約2倍の音声時間が増加し、固定パートを合わせた総尺はおおよそ
500〜610秒台まで伸びる可能性がある(固定パートの尺が変わらない前提での
概算であり、実測ではなく設計上の見積り)。これはlistening loadの観点で
避けるべき、という前提を本節の設計条件とする。

**目標尺設計(未検証の設計目標、Production適用前に実測での再検証が必要)**:
1. 固定パート(Intro/Welcome/Preview/Key Phrase/Notification/Outro)は
   無変更(既存共通primitiveをそのまま再利用するため、尺は変わらない)。
2. Voice本体の1声あたり語数を、2 Voices時点の1声あたり語数より意図的に
   短縮する(4声で「浅く広く」にならないよう、各Voiceは「立場→責任→
   だからどう見えるか」の核だけに絞り、具体例の量を2 Voices時より
   減らす設計指針)。目標: 4声合計の語数を、2声時点のVoice A+B合計の
   約1.3〜1.5倍程度に収める(4倍にしない)。
3. Tension本体は、4者分の統合が必要になるため2 Voices時より多少長く
   なることを許容するが、2倍化はしない(目標: 2 Voices時点のTension
   本体の約1.3倍程度)。
4. Comment 1〜4はテキスト量として大きな変化を想定しない(文言書き換えの
   範囲、大幅な長文化はしない)。
5. 上記を積み上げた**目標総尺のレンジ: 約380〜430秒**(305秒起点の
   +25%〜+40%程度)を、4 Voicesの設計目標として提示する。この数値は
   本Trialでの音声実測を伴わない設計目標であり、実装・実測段階で
   改めて検証が必要(**未検証の目標値、事実確認ではない**)。

---

## 4. 推奨案

**推奨: 案S1(4見出し直列、Tension内容設計として2軸交差を使う)**

### 推奨理由
1. 比較表(2節)で、実装影響(Lane B内で閉じるか/Contract変更の要否)が
   3案中もっとも小さい。新規Comment枠・新規segment種別を追加せず、
   既存の「Comment 4枠固定・Tension 1区切り」という骨格を維持したまま
   Voices部分だけを2→4に拡張できる。
2. QA拡張(影響点6)が「既存ペア比較ロジックをそのまま6回呼ぶ」だけで
   済み、既存Point Overlap QA/Analytical Leakage Checkの**意味論を
   変更しない**(閾値・判定方式は不変、比較対象ペア数のみ増える)。
   案S2はペア内/ペア間の重み付けという形で意味論変更が必須になり、
   案S3は新segmentのQA対象化という新論点が生じる。
3. 案S3が抱える原則抵触リスク(Voiceを聞く前に軸を説明してしまい、
   Comment 3・Tensionの役割[聞いた後に「なぜ違って見えるか」へ視点を
   移す]と機能重複する)を、S1は「Tensionの中身の書き方」として軸を
   使うことで回避できる(構造上は軸を先出ししない)。
4. 案S2の2ペア構造は、3 Voicesとの関係で非対称(2+1)になり相性が
   悪く、10節の3 Voices論点との整合性がS1より低い。

案S2・S3は**REJECTEDではなく**、テーマや目的(例: 「会社の中の対立」を
強調したい場合はS2、視聴者に軸を先に理解させたい教育的構成が求められる
場合はS3)によっては再検討の価値があるものとして保持する。

### 推奨案(案S1)の、Phase 1構造からの差分一覧(実装はしない、列挙のみ)
1. `er012_b_family_editorial_type_registry_01.py`
   - `SECTION_LABELS`: `("hook", "voice_a", "voice_b", "tension",
     "closing")` → 4 Voices版として新規定数(例:
     `SECTION_LABELS_4V = ("hook", "voice_1", "voice_2", "voice_3",
     "voice_4", "tension", "closing")`)を追加(既存定数は無変更のまま
     残す案、2 Voices経路との後方互換を保つ)。
   - `VOICE_ASSIGNMENT`: 4声版として新規キー(例:
     `VOICE_ASSIGNMENT_4V = {"voice_1": ..., "voice_2": ..., "voice_3":
     ..., "voice_4": ..., "narrator": "Aoede"}`)を追加。候補voice名の
     選定(既存利用可能voice一覧からの選定、音質評価はユーザー主観)は
     未実施、本Trialの範囲外。
   - `VOICE_FALLBACK`: 4声分のfallback voice設定が新規に必要。
   - `EDITORIAL_TYPES`辞書へ新規editorial_type(例:
     `"b_family_voices_4v"`)を追加する案(既存`"b_family_voices"`
     [2 Voices]は無変更のまま残す)。
   - `COMMENT_ROLES`: `VOICES_COMMENT_2_ROLE`・`VOICES_COMMENT_3_ROLE`の
     文言書き換え版(4 Voices用)を新規定数として追加。Comment 1・4は
     文言変更不要と見立てる(内容が2/4 Voices非依存のため)。
2. `er012_b_family_voices_production_01.py`
   - `split_five_voice_sections()`とは別の新関数(例:
     `split_seven_voice_sections()`)を追加し、見出し数`== 7`を要求する
     ガードにする(既存関数は無変更のまま残す)。
   - `build_parts()`とは別の新関数(例: `build_parts_4v()`)を追加。
   - `build_b1_voices_timeline()`とは別の新関数(例:
     `build_b1_voices_timeline_4v()`)を追加し、Voice 1〜4の
     heading→body→Point Notificationブロックを4回分並べる
     (既存関数は無変更のまま残す)。
   - `run_voice_availability_check()`・`resolve_voice_names()`相当の
     4声版(4声分のavailability check・fallback解決)が新規に必要。
3. QA(前Trial引用に基づく想定、本Trialでは実装対象外)
   - Point Overlap QA/Analytical Leakage Checkを呼ぶ側のループを、
     既存1ペア呼び出しから6ペア(C(4,2))呼び出しへ拡張する新関数が
     必要(既存の1ペア判定関数自体は無変更)。
4. Audio Validation Gate
   - REQUIRED_SEGMENTS相当の必須segment一覧に`voice_1`〜`voice_4`の
     4系統を追加する必要(現行の「位置ベース2ブロック前提」の見直しが
     必要かどうかは、本Trialでは未確認のまま論点として残す)。
   - retry/fallback/Human Review Lock自体の仕組み(`guarded_generate`
     等)は無変更のまま、4声それぞれに同一ロジックを適用する案(既存
     安全装置の意味を変えない)。

### 未承認仕様として承認が必要な項目一覧(本Trialでは実装しない)
1. 4 Voices構造そのものの採用可否(この設計Trial自体の採用判断)。
2. Comment 2・Comment 3の文言書き換え版(FINALIZE-11で
   APPROVED_FOR_PRODUCTION済みの確定Contractへの変更)。
3. 4声のTTS voice選定(候補voice名からの4声キャスティング、音質評価は
   ユーザー主観のため実際の音声試聴が必要)。
4. `physical_structure`の新規値・`EDITORIAL_TYPES`への新規editorial_type
   追加方針(既存`"b_family_voices"`[2 Voices]を残すか、置き換えるか)。
5. QA(Point Overlap/Analytical Leakage)の6ペア拡張方式・計算量許容範囲。
6. Audio Validation GateのREQUIRED_SEGMENTS拡張方針、および
   「位置ベース2ブロック前提」の見直し要否。
7. 3節で示した目標尺レンジ(約380〜430秒)の採否(未検証の設計目標)。
8. Tensionの2軸交差という内容設計方針そのもの(記事本文レベルでの
   検証は未実施)。

---

## 5. 3 Voicesとの関係(比較論点、勝手に3へ変更しない)

- **3 Voicesが合理的になりうる条件**(Axis Trial-01 3節の分析を踏襲):
  Applicant/Recruiter-HM/Business/Legalの4者のうち、いずれか1者を落とす
  と「テーマの異なる側面が明確に失われる」ことがすでに確認されている
  (Legal落とし→社会的争点[差別・監査]の当事者消失、Business落とし→
  企業側の動機[なぜAIを使いたいか]の消失、Recruiter/HM落とし→現場の
  実務的葛藤の消失)。したがって**本テーマ・本4者選定においては3
  Voicesへの縮小は推奨しない**。
- 一方、案S1の実装コスト(4声分のTTS・4見出し分の尺増加・QA6ペア化)が
  Production適用のハードルとして大きいと判断された場合、「4者のうち
  どれか1者を落として3声にする」のではなく、「Recruiter/HMとBusinessを
  1つのVoiceへ再統合する(2者→1者)」という**3 Voices版の代替統合案**
  (Applicant/Recruiter-HM+Business統合/Legal)も理論上は成立しうる。
  ただしこれは4 Voicesの選定軸(案A)の「現場と経営を分離することで
  『会社側も一枚岩ではない』ことを描く」という狙い(Axis Trial-01の
  推奨理由3)を打ち消すため、**本Trialでは推奨しない**(比較論点として
  記録するのみ、実装しない)。
- 3 Voicesへの変更は本Trialの委任範囲外であり、採用するかどうかは
  ユーザー判断(USER_DECISION_REQUIRED)。

---

## 6. Gate 1分類

**構造設計としての妥当性: VALIDATED(Trial範囲内)**
- 2〜3案(S1/S2/S3)を提示し、タスク指定10影響点+実装影響の比較表で
  評価した上で1案(S1)を推奨し、理由を明示できた。
- 既存SSOT(Editorial Type registry、5区切りparser、Assembly timeline、
  Comment Contract確定文言、Point Overlap QA等の既存前提)を引用し、
  矛盾なく拡張案を構成できた。既存の`"b_family_voices"`(2 Voices)経路
  自体には触れておらず、新規追加として設計している。
- 新規failure mode: 案S3で「Voiceを聞く前に軸を説明することで
  Comment 3・Tensionの役割と機能重複するリスク」を特定し、S3を推奨から
  除外する根拠とした(STOP=この方向の設計は現時点で進めず、論点として
  記録)。
- 記事本文・音声での実証、Contract文言の実装、QA拡張の実装、目標尺の
  実測検証はいずれも範囲外(未実施)。

**採用判断(どの構造案を選ぶか、4 Voicesへ拡張すること自体・Comment
Contract変更・TTS voice選定・目標尺の採否を含む): USER_DECISION_
REQUIRED**(4節「未承認仕様として承認が必要な項目一覧」を参照)。
