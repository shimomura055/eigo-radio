# EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-TRIAL-03

固定テーマ: "Should companies use AI to screen job applicants?"
範囲: **3 Voices・4 Voicesを同時に設計する統合設計Trial**。既存2 Voices
Production(`b_family_voices`、`APPROVED_FOR_PRODUCTION`済み4項目、
`PRODUCTION_WIRED`)は一切変更しない。記事本文・音声は生成していない。
Production/Prompt/Contract/コード編集はしていない。LLM API呼び出しなし
(¥0)。

---

## 0. 前提確認(既存資産、Grep+該当箇所読込、引用のみ・変更なし)

- `EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-AXIS-DESIGN-TRIAL-01_REPORT.md`
  / 同`design.md`: 4 Voices選定軸、案A(Applicant/Recruiter・HM統合/
  Business・Efficiency/Fairness・Legal・Governance)を推奨、
  `USER_DECISION_REQUIRED`のまま。3 Voicesへ縮小する場合の3パターン
  (Legal落とし/Business落とし/Recruiter・HM落とし)の損失分析が既に
  §3にあり、本Trialの3V設計はこれを踏まえて実施した(単純な繰り返しでは
  なく、損失分析を前提に「どれが最も合理的か」を判断)。
- `EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-STRUCTURE-DESIGN-TRIAL-02_REPORT.md`
  / 同`design.md`: 4 Voices構造案3案(S1/S2/S3)比較、S1(4見出し直列+
  Tension内で2軸交差)を推奨。本Trialの4V設計はS1をそのまま踏襲し、
  再設計・再比較はしていない(ユーザー指示どおり「前Trialの推奨S1を
  ベース」)。
- `er012_b_family_editorial_type_registry_01.py`(現物読込): 2 Voices
  正式構造の実体。`VOICE_ASSIGNMENT={"voice_a":"Algieba","voice_b":
  "Erinome","narrator":"Aoede"}`、`VOICE_FALLBACK={"voice_a":"Schedar",
  "voice_b":"Sulafat"}`、`SECTION_LABELS=("hook","voice_a","voice_b",
  "tension","closing")`、Comment 1〜4確定文言全文(`APPROVED_FOR_PRODUCTION`
  済み)。
- `er012_b_family_voices_production_01.py`(現物読込): `split_five_voice_
  sections()`(見出し数`!=5`ならNone)、`build_parts()`、
  `build_b1_voices_timeline()`、`run_voice_availability_check()`/
  `resolve_voice_names()`(fallback解決ロジック)。
- `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`
  (現物読込): Gateは**segment名のハードコードされた必須一覧を持たず**、
  `tts_generation_results.json`の`segments`辞書に**存在するもの全て**を
  `VALIDATED`/`HUMAN_APPROVED`か判定するだけの構造だった(新規事実確認、
  下記B-5で詳述)。
- `EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03_REPORT.md`
  L76-109: 2V完成episodeの実測segment別duration一覧(pause除く)。本Trial
  のB-6目標尺設計の実測基準として使用。
- `er012_output/editorial_b_family_production_phase1_02/b1b/
  b1_support_texts.json`(現物読込): 2V本番採用済みComment 1〜4の**実際の
  生成テキスト**(以下引用)。B-1のドラフト作成の土台として使用。
  - Comment 1: "As you listen, notice the contrast between two different
    reactions to the same setting."
  - Comment 2: "Now, you will hear two different voices. Each person
    will share their own view on the question you just heard."
  - Comment 3: "You have heard two different ways of experiencing the
    same situation. Instead of deciding which view is right, let us ask
    why the situation feels different to each person. Next, we will
    look more closely at where that difference comes from."
  - Comment 4: "Instead of asking which person is right, let's ask a
    deeper question. What is it about this situation that makes it feel
    different for each person?"
- Gemini TTS voice候補の事実確認(現物読込、`er012_editorial_b_voices_
  trial_09_audio.py` L104-108): `VOICE_A_CANDIDATE="Algieba"`,
  `VOICE_B_CANDIDATE="Erinome"`, `VOICE_A_FALLBACK="Schedar"`,
  `VOICE_B_FALLBACK="Sulafat"`, `NARRATOR_VOICE="Aoede"`,
  `COMPARISON_VOICES=("Algieba","Erinome","Schedar","Sulafat","Aoede")`。
  **技術的に利用可能・ユーザー試聴済みでネガティブ評価なし、と記録に残る
  voiceはこの5つ + Comment/共通ナレーター用Charonのみ**(OPEN_ITEMS.md
  OPEN-120行「候補voice(Algieba/Erinome/Schedar/Sulafat/Aoede)はいずれも
  音質面で問題なし・ネガティブ評価なし」)。**性別的印象(男性的/女性的)を
  記載した箇所はSSOT全体で見つからなかった**(下記B-2で詳述)。

---

## 1. 3 Voices構成の推奨(最優先の結論)

### 1-1. 選択肢の比較(4案、すべて案Aの4者[Applicant/Recruiter・HM/
Business・Efficiency/Fairness・Legal・Governance]からの縮小案)

| 案 | 残る3者 | 失われるもの(Axis Trial-01 §3を継承) | 弁論の偏り(単純賛否分割リスク) | 「会社側も一枚岩ではない」原則の維持 |
|---|---|---|---|---|
| 3V-a: Legalを落とす | Applicant / Recruiter・HM / Business | 差別・監査・訴訟という社会的争点の当事者が消失 | **高リスク**: Applicant(個人・慎重)1 vs Recruiter・HM+Business(会社側・効率)2、という2対1の陣営に見えやすい | 失われる(Recruiter・HMとBusinessはどちらも「効率」寄りで、会社側内部の対立が消える) |
| 3V-b: Businessを落とす | Applicant / Recruiter・HM / Legal | 「なぜ企業がそもそもAIを使いたいか」という動機側の当事者が消失 | **中〜高リスク**: Applicant(慎重)+Legal(慎重)2 vs Recruiter・HM(両義)1、で「AIは危険」という一方的トーンに傾く懸念(Axis Trial-01が明記) | 部分的に維持(Recruiter・HMは効率寄りだが単独では推進側の代表として弱い) |
| **3V-c: Recruiter・HMを落とす(推奨)** | **Applicant / Business・Efficiency / Fairness・Legal・Governance** | 現場の実務的葛藤(効率と精度のジレンマ)という、当事者と経営の「中間」の声が消失 | **低〜中リスク**: Business(推進)とLegalが(慎重)は会社の中で互いに対立しており、Applicantは第三の「個人・当事者」軸。3者の性質が経済的動機/制度的責任/個人的経験と質的に異なり、2対1に集約されにくい | **維持**(Business↔Legalの対立がそのまま残るため、「会社側も一枚岩ではない」という4V設計の狙いを3Vでも保てる) |
| 3V-d: Recruiter・HM+Businessを統合(Axis/Structure Trial既出、非推奨) | Applicant / Recruiter・HM+Business(統合) / Legal | 現場と経営を分離した狙い自体を打ち消す(Structure Trial-02 §5がすでに非推奨と明記) | 中リスク: 統合された「会社側」1 vs Legal 1 vs Applicant 1で対称に見えるが、統合Voiceの内部に「現場↔経営」の温度差を書き込む必要があり、Voice=1 stakeholderという設計原則(単一の立場・責任・制約)に反しやすい | 統合したVoiceの中でしか表現できず、対話としての対立が薄れる |

### 1-2. 推奨: 3V-c(Recruiter/Hiring Managerを落とす)

**推奨構成: Applicant / Business・Efficiency / Fairness・Legal・HR
Governance**

**理由**
1. 3V-a・3V-bはいずれもAxis Trial-01が明示的に警告した失敗モード(単純な
   2対1の陣営化、または一方的トーン)に該当する。3V-cはこのリスクが
   相対的に最も低い。
2. 3V-cは「Business(推進)↔Legal(慎重)」という**会社内部の対立**を
   保持するため、4 Voices設計の中核原則「会社側も一枚岩ではない」を
   3 Voicesでも維持できる(3V-a/bはこの対立構造ごと失われる)。
3. 残る3者は「個人的経験(Applicant)」「経済的動機(Business)」
   「制度的責任(Legal)」という**質的に異なる3種類の利害**であり、
   Tensionを「賛成/反対」ではなく「何を背負っているかの違い」として
   自然に設計できる(B-7参照)。
4. 失うもの(現場の実務的葛藤)は実在するトレードオフであり、
   **REJECTEDではなくコストとして認識する**べき: Recruiter/HMは
   Applicantに最も近い「現場」の視点であり、これが無いと記事全体が
   やや制度的・大局的な語りに寄るリスクがある。この点はGate 4観点・
   未承認仕様一覧に明記し、Writer設計時にApplicant側の描写を具体的な
   場面(実際に落とされた経験等)で補う必要がある、という設計指針として
   記録する。

3V-a・3V-bは**REJECTEDではなく**、テーマ設定を変える場合(例:
「差別是正 vs 経済合理性」を主題化したい場合は3V-a寄り、「個人の権利
擁護」を主題化したい場合は3V-b寄り)に再検討の余地があるものとして保持。
3V-dはStructure Trial-02の既存判断(非推奨)を踏襲し、本Trialでも
推奨しない。

**採用可否はUSER_DECISION_REQUIRED。**

---

## B-1. Comment 2/3(3V版・4V版)

### 現行Contractの位置・機能(登録済み定義、`registry.py`から引用)
- Comment 1: Listening Focus(内容先取り禁止、"the question"禁止句あり)。
- **Comment 2**: Hookの問いから「ここから異なるVoiceを聞く」への橋渡し。
  具体的内容・見出し文言の先取り禁止、"Point One/Two"禁止。
- **Comment 3**: 全Voiceを聞き終えた後、「どちらが正しいか」ではなく
  「なぜ違って見えるか」への視点移動。答えの先出し禁止、評価禁止。
- Comment 4: 表面的対立から一段深い問いへ。要約・解決策提案禁止。

3V/4Vで変更が必要なのはComment 2(人数・複数の声への言及)とComment 3
(「全Voiceを聞き終えた」という前提の書き方)のみ。Comment 1・4は人数に
依存しない文言のため変更不要という前Trial(Structure Trial-02)の判断を
踏襲。

### ドラフト文言(英語、設計例。**LLM再生成はしていないため、2V実採用
文言["Now, you will hear two different voices...."]の語彙・構文を手動で
人数分だけ書き換えた例示であり、Production最終文言ではない**)

| | 2V実採用(参考) | 3V案(ドラフト) | 4V案(ドラフト) |
|---|---|---|---|
| Comment 2 | "Now, you will hear two different voices. Each person will share their own view on the question you just heard." | "Now, you will hear three different voices, one after another. Each person will share their own view on what you just heard." | "Now, you will hear four different voices, one after another. Each person will share their own view on what you just heard." |
| Comment 3 | "You have heard two different ways of experiencing the same situation. Instead of deciding which view is right, let us ask why the situation feels different to each person. Next, we will look more closely at where that difference comes from." | "You have heard three different ways of experiencing the same situation. Instead of deciding which view is right, let us ask why the situation feels different to each person. Next, we will look more closely at where that difference comes from." | "You have heard four different ways of experiencing the same situation. Instead of deciding which view is right, let us ask why the situation feels different to each person. Next, we will look more closely at where that difference comes from." |

### Contract適合性チェック表(禁止事項別)

| 禁止事項 | 3V案 | 4V案 |
|---|---|---|
| 要約しない(内容の先取り) | 適合(誰が何を言うかへ触れていない) | 適合(同左) |
| 答えを先取りしない | 適合(Comment 3は「なぜ違うか」の答え自体を出していない) | 適合(同左) |
| 評価しない(正しい/間違いの判定) | 適合("which view is right"を判定ではなく問いかけとして提示、2V文言と同型) | 適合(同左) |
| "the question"禁止句(Comment 1限定) | 該当なし(Comment 2/4はこの禁止句の対象外、2V実採用文言も"the question"を使用) | 該当なし(同左) |
| "Point One/Two"等の内部ラベル | 適合(使用なし) | 適合(使用なし) |
| 見出し文言の先取り禁止(Comment 2) | 適合(Voiceの内容・見出しに触れていない) | 適合(同左) |

**Gate 4観点(未承認仕様への依存の明示)**: 上記ドラフトは**手動書き換え
であり、実際のProduction用途では既存の`b1s.run_support_text()`
(LLM呼び出し)経由でContract定義文(Role prompt)から再生成する必要が
ある。本Trialでは費用ゼロ制約のためLLM呼び出しをしておらず、Role
prompt自体の3V/4V版(`VOICES_COMMENT_2_ROLE`/`VOICES_COMMENT_3_ROLE`の
人数言及部分の書き換え)も未作成**(下記「未承認仕様一覧」に記録)。
Comment 1〜4はFINALIZE-11で`APPROVED_FOR_PRODUCTION`済みの確定Contract
であり、その変更(Role prompt文言の書き換え)自体に改めてユーザー承認が
必要。

---

## B-2. TTS voice設計

### 事実確認結果(SSOT/過去管理IDのみを根拠、新規voice名の作成なし)

**承認済み・技術的に利用可能と記録されている候補は以下のみ**:

| voice名 | 現在の役割 | 出典 | 性別的印象の記載 |
|---|---|---|---|
| Algieba | Voice A(本文、正式`APPROVED_FOR_PRODUCTION`) | `registry.py` L44 | **記載なし** |
| Erinome | Voice B(本文、正式`APPROVED_FOR_PRODUCTION`) | `registry.py` L45 | **記載なし** |
| Schedar | Voice A fallback(技術的availability確認済み、本採用ではない) | `registry.py` L50、Trial-09 | **記載なし** |
| Sulafat | Voice B fallback(技術的availability確認済み、本採用ではない) | `registry.py` L51、Trial-09 | **記載なし** |
| Aoede | Narrator(見出し読み上げ、正式`APPROVED_FOR_PRODUCTION`) | `registry.py` L46 | **記載なし** |
| Charon | 既存共通Production narrator(Comment/Preview/Key Phrase等) | Trial-09 Report | **記載なし** |

OPEN_ITEMS.md OPEN-120行の記載は「候補voice(Algieba/Erinome/Schedar/
Sulafat/Aoede)はいずれも**音質面**で問題なし・ネガティブ評価なし、正式
固定は完成episode通し試聴後に判断する」であり、**男性的/女性的という
性別的印象を評価・記載した箇所はSSOT全体で見つからなかった**。したがって
「男性的→女性的→男性的→女性的(またはその逆順)」というユーザー希望の
並び順を、記録に基づいて確定することは**現時点で不可能**。

**新しいvoice候補は作成していない**(候補は上記6つのみ、これ以外の
Gemini TTS voice名を勝手に提示することはしていない)。

### 3V/4V声候補の割当案(名前・並び順のみ、性別印象は未確認のまま提示)

4V(声本体に使えるのはAlgieba/Erinome/Schedar/Sulafatの4つで**ちょうど
過不足なし**、Narrator=Aoede/Comment=Charonは据え置き):

| Voice位置 | Stakeholder(案A) | 候補voice名 |
|---|---|---|
| Voice 1 | Applicant | Algieba(既存Voice A、実績あり) |
| Voice 2 | Recruiter/Hiring Manager | Erinome(既存Voice B、実績あり) |
| Voice 3 | Business/Efficiency | Schedar(既存fallback、technical availability確認済みだが**本採用としては新規**) |
| Voice 4 | Fairness/Legal/Governance | Sulafat(既存fallback、同上) |

3V(3V-c、声本体3つが必要):

| Voice位置 | Stakeholder(3V-c) | 候補voice名 |
|---|---|---|
| Voice 1 | Applicant | Algieba(既存Voice A、実績あり) |
| Voice 2 | Business/Efficiency | Erinome(既存Voice B、実績あり) |
| Voice 3 | Fairness/Legal/Governance | Schedar または Sulafat(いずれも本採用としては新規) |

**男性的→女性的→…の交互配置**: 上記の並び順はstakeholderの提示順序
(当事者→[現場→]経営→監督、Structure Trial-02の隣接対比設計を踏襲)を
優先して決めたものであり、**性別交互配置の要件は反映できていない**
(反映するための性別印象データが存在しないため)。既存
`er012_output/editorial_b_voices_trial_09_audio/audit/voice_samples/`
配下に5voice(Algieba/Erinome/Schedar/Sulafat/Aoede)の比較sample wavが
既に存在する(新規TTS生成不要、追加費用ゼロ)。**ユーザーがこれを試聴し
男性的/女性的の印象を判定した上で、上記の役割割当と交互配置の両立可否を
改めて確認する必要がある**(未承認仕様、下記一覧に記録)。

Schedar/Sulafatを「fallbackから3V/4Vの本採用voiceへ格上げする」こと
自体も、現行Contractでは「fallback」という役割定義であり、本採用への
格上げは新しい割当であるため、技術的availabilityの実績はあるが
**別途ユーザー承認が必要**(新規voice名の発明ではないが、役割変更として
記録)。

---

## B-3. physical_structure

### 既存2V構造(無変更、参考)
`SECTION_LABELS=("hook","voice_a","voice_b","tension","closing")`
(5見出し)、`physical_structure="five_section"`。

### 4V構造(Structure Trial-02 案S1を継承、変更なし)
`SECTION_LABELS_4V=("hook","voice_1","voice_2","voice_3","voice_4",
"tension","closing")`(7見出し)、`physical_structure`新規値(例:
`"seven_section"`)。Tensionは単一区切りのまま、内容設計として2軸交差
(当事者性×態度)を使う(Structure Trial-02 §1 案S1のまま、再設計なし)。

### 3V構造(新規設計、案S1と同型で見出し数のみ縮小)
`SECTION_LABELS_3V=("hook","voice_1","voice_2","voice_3","tension",
"closing")`(6見出し)、`physical_structure`新規値(例:
`"six_section"`)。Voice順序はB-1の割当表と同じ
(Applicant→Business→Legal、当事者→経営→監督という距離の遠ざかる順、
Structure Trial-02の隣接対比設計を踏襲)。Tensionは単一区切りのまま、
内容設計は2軸交差ではなく新規のB-7設計(下記)を使う。

### 構造定義の集約案(retry/fallback/regeneration/assembly/QA全経路で
崩れない設計、実装しない・列挙のみ)
- 現状の2V実装は`SECTION_LABELS`・`VOICE_ASSIGNMENT`・
  `TENSION_SLOT_APPROVED_NAME`等を`registry.py`の1箇所に定数集約し、
  `production_01.py`側の`split_five_voice_sections()`/`build_parts()`/
  `build_b1_voices_timeline()`が**すべてこのregistry定数を参照する**
  設計になっている(現物確認済み)。3V/4V版もこの設計原則をそのまま
  踏襲し、`SECTION_LABELS_3V`/`SECTION_LABELS_4V`・
  `VOICE_ASSIGNMENT_3V`/`VOICE_ASSIGNMENT_4V`をregistryに追加し、
  対応する`split_six_voice_sections()`/`split_seven_voice_sections()`・
  `build_parts_3v()`/`build_parts_4v()`・
  `build_b1_voices_timeline_3v()`/`_4v()`がすべてこれらの定数のみを
  参照する(見出し数・voice数をコード内にリテラルで埋め込まない)、と
  いう設計方針を提案する(実装はしない)。
- retry/fallback(`resolve_voice_names()`相当)・regeneration
  (`review_lock.approve_regenerate()`)・assembly
  (`build_b1_voices_timeline_Nv()`)・QA(B-4)のいずれも、上記の
  registry定数を参照する限り「V数」を変える際の変更箇所は
  registry定数の追加のみで済み、各処理ロジック自体はV数に対して
  ループ処理(Nboice分繰り返す)として一般化できる、という設計方針
  (現時点は3V/4V個別関数として提案しているが、将来的にN汎用の1関数へ
  統合する余地もある、という論点のみ記録)。

### Phase 1経路との差分一覧(ファイル・関数・設定キー名レベル、実装しない)
1. `er012_b_family_editorial_type_registry_01.py`: `SECTION_LABELS_3V`/
   `_4V`、`VOICE_ASSIGNMENT_3V`/`_4V`、`VOICE_FALLBACK_3V`/`_4V`、
   `EDITORIAL_TYPES`への`"b_family_voices_3v"`/`"b_family_voices_4v"`
   新規追加、`COMMENT_ROLES`の3V/4V版(Comment 2・3文言差し替え)。
2. `er012_b_family_voices_production_01.py`: `split_six_voice_sections()`
   /`split_seven_voice_sections()`(既存`split_five_voice_sections()`は
   無変更)、`build_parts_3v()`/`_4v()`、
   `build_b1_voices_timeline_3v()`/`_4v()`、`run_voice_availability_
   check()`/`resolve_voice_names()`の3声/4声版。
3. QA呼び出し側: B-4の6ペア/3ペア総当たりループ関数(新規、既存ペア
   判定関数自体は無変更)。
4. Audio Validation Gate: B-5参照(Gate本体は無変更で足りる可能性が
   高いという新規知見、下記詳述)。

---

## B-4. QA — Voice間重複確認

### 対象ペア
- 3V: 3ペア(Voice1-2, Voice1-3, Voice2-3)。
- 4V: 6ペア(C(4,2)、Voice1-2/1-3/1-4/2-3/2-4/3-4)。

### 目的の再確認
複数Voiceが「ほぼ同じ役割・理由・主張」になっていないかの検出。**同じ
テーマ・共通語・同一事実参照だけでNGにしない**。見るべきは stakeholder
position / constraint / responsibility / what they protect / reasoning
の違い。

### 既存2V用閾値のそのまま適用可否: **未検証**

既存Point Overlap QAは**lexical overlap ratio、閾値0.40**
(`EDITORIAL-B-FAMILY-VOICES-TRIAL-07-CONTRACT-REFINEMENT-01_REPORT.md`
L564実測: 2V実測ペアはoverlap_ratio 0.14〜0.2、閾値0.4未満でPASS)。
Analytical Leakage Checkは現状Voice A/B限定6基準
(`leak_evidence_subject`/`leak_numbers_foreground`/
`leak_discovery_syntax`/`leak_evidence_memorable`/
`leak_narrator_analysis`/`leak_unknowable_analysis`)+Tension用5基準+
Closing用1基準(Trial-07現物)。いずれも**2 Voice・1ペア比較**を前提に
設計されており、3V/4Vのペア数増加時に同じ意味論・同じ閾値が成立するかは
**本Trialでは検証していない**(未検証のまま検証Trial設計のみ提示)。

### 検証Trial設計(正式採用しない、設計のみ)

**Positive control(検出できるべきケース)**:
2V実採用済みのVoice A本文(Algieba)テキストを、語彙・言い回しだけ最小限
変えて複製し、「別のstakeholderのふりをした実質同一Voice」を人工的に
作る(例: 一人称の主語・固有の立場言及だけ置換し、reasoning構造は
同一のまま)。このペアで overlap_ratio が閾値0.40を上回る、または
Analytical Leakage Check相当のルーブリック判定が「diversity不足」を
検出できるか確認する。**新規LLM生成なしで既存承認済みテキストの手作業
複製で作成可能**(¥0で実施できる設計)。

**Negative control(誤検出してはいけないケース)**:
2V実採用済みのVoice A/B(Algieba/Erinome)ペア(overlap_ratio
0.14〜0.2、実測PASS)を、3V/4Vの6ペア/3ペア判定ロジックにそのまま
1ペアとして通し、既存の閾値・判定が変わらずPASSすることを確認する
(既存実測値の再利用、追加コストなし)。あわせて、**「テーマ語彙の
共有」による偽陽性リスク**を確認するため、AI審査というテーマに固有の
頻出語("AI"/"screening"/"applicant"/"algorithm"等)を意図的に多く含む
架空の短文ペア(実在の記事から借用しない、設計上のダミー文)で
overlap_ratioがテーマ語彙の共有だけで閾値へ近づかないかを確認する項目
も設計に含める。

**成功基準(案、未実装)**:
1. Positive controlのoverlap_ratioが、2V実測の負例ペア(0.14〜0.2)より
   明確に高く、かつ閾値0.40近傍またはそれ以上になること。
2. Negative control(2V実測ペア)が3V/4Vループでも同じ値を再現し、誤って
   閾値を超えないこと。
3. テーマ語彙共有ダミー文が、閾値付近まで overlap_ratio を押し上げない
   こと(押し上げる場合は閾値のみの判定では不十分と判断し、
   stakeholder position/constraint/responsibility/protects/reasoningの
   質的な違いを見るルーブリック型チェック[既存Analytical Leakage
   Check型の拡張]の要否を論点として残す)。
4. ペア数が3→6に増えることに伴う計算量・生成コストの許容範囲確認
   (Trial-02 Structure design §2で既出の論点、再確認)。

上記はいずれも**検証Trialの設計のみ**であり、本Trialでは実施・採用して
いない。

---

## B-5. Audio Validation Gate

### 新規事実確認: Gate本体はsegment数をハードコードしていない

`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`
(現物読込)は、`REQUIRED_SEGMENTS`のような固定必須segment一覧を持たず、
`tts_generation_results.json`の`segments`辞書に**実際に記録されている
segmentすべて**についてstatus(`VALIDATED`/`HUMAN_APPROVED`等)・
post-process evidence(disfluency QA・asset hash一致)を検証する構造
だった。つまりGate自体は「N Voice構造」に対して**汎用**であり、
3V/4Vでも「今回生成されたsegmentがすべて正しい状態か」はそのまま
機能する見込みが高い(前Trial[Structure Trial-02]が懸念していた
「REQUIRED_SEGMENTS拡張の要否」は、Gate本体レベルでは**不要である
可能性が高い**という新しい知見)。

### 新しいfailure mode(未検出だったリスク、Gate 1「新規failure mode」該当)

上記の裏返しとして、Gateは「**記録されているsegmentの状態**」しか
検証せず、「**構造上あるべきsegmentがすべて記録されたか**」自体は
検証しない。つまり、3V/4V用timeline builder(`build_b1_voices_
timeline_3v()`/`_4v()`)に**実装バグでVoice 3・Voice 4いずれかの
segmentを書き漏らす**ようなことが起きた場合、Gateはそれを検出できず、
episodeが本来より少ない声のまま完成してしまうリスクがある(2Vでは
Voice数が固定2のため表面化しにくかった failure mode)。**この完全性
チェック(構造が期待するsegment数と実際に記録されたsegment数の一致
確認)は現状どこにも存在せず、3V/4V対応で新規に必要になる可能性が
高い**(未承認仕様、下記一覧に記録)。

### 3V/4V双方で確認すべき項目(設計のみ、実装しない)
- 必要segment数: 3V=Voice本体3+Voice見出し3+Point Notification3
  (+固定parts)、4V=Voice本体4+Voice見出し4+Point Notification4
  (+固定parts)。
- voice assignment: B-2の割当がtimeline builder内で正しく
  Voice位置↔TTS voice名に対応しているか(既存`resolve_voice_names()`
  相当の3声/4声版が必要、B-3参照)。
- segment順序: hook→(voice_1見出し→body→...)→voice_N→tension→closing
  という順序が、Assembly側`build_b1_voices_timeline_Nv()`で崩れずに
  維持されるか。
- 欠落検知: 上記「新しいfailure mode」への対応として、完全性チェックを
  Gate本体とは別関数として追加する設計(未実装)。
- assembly前必須条件: 既存2Vと同じくGate→Assembly実行という順序を維持
  する(既存`load_b1_sources()`が`verify_episode_audio_validation_
  gate()`を呼んでから組み立てる構造、無変更のまま3V/4Vへ流用可能と
  見立てる)。
- retry/fallback後の整合: 既存`review_lock`(Human Review Lock)・
  `guarded_generate`相当の安全装置は、Voice数に対する意味論変更が
  不要(1つ1つのsegment生成に対して同じロジックを3回/4回適用するだけ)
  という設計方針(Structure Trial-02 §4を踏襲)。

---

## B-6. 目標尺

### 実測基準値(2V、Trial-09 HEADING-REGEN-AND-FULL-EPISODE-03実測、
pause除くsegment内訳)
合計301.795秒(別バージョンのphase1_02実測は305.135秒、両者は僅差)。
固定parts(Intro〜Comment 1 + Outro、Voice数に依存しない部分)の実測
合計: 約95.5秒。可変parts(Hook+Comment2-4+Voice A/B見出し・本体+
Tension+Closing、pause除く)の実測合計: 約193.2秒
(差分約13秒はsegment間のpause/gapで、pause除く表には含まれない)。

### 4V目標(Structure Trial-02から再掲、本Trialでは再設計していない)
約380〜430秒(305秒起点+25%〜+40%、未検証の設計目標)。

### 3V目標(新規提案)

単純な比例(2V→3Vは声を1つ追加するだけなので、各Voiceの尺をそのまま
維持すると仮定した場合の素朴な見積り: 可変parts 193.2秒に、2V実測の
Voice本体1声あたり平均尺(見出し3.8秒+notification1.78秒+本体平均
36.4秒≒42秒)をもう1声分足すと約235秒、固定parts+pauseを合わせて
総尺は約340〜350秒程度になる見込み)を出発点としつつ、4V設計と同様に
「浅く広くならないよう、各Voiceの発話量を意図的にやや絞る」設計指針を
適用する。

**設計条件**:
1. 固定parts(Intro〜Comment1+Outro)は無変更(約95.5秒、既存共通
   primitiveの再利用)。
2. Hookは無変更〜微増(約21〜23秒、3声への言及は増えないためほぼ現状
   維持)。
3. Voice本体1声あたりの語数を、2V時点の1声あたり語数よりやや短縮する
   (4V設計ほど大胆な短縮はしない。声の追加数が2V→3Vでは+1、2V→4Vでは
   +2のため、圧縮の必要性は4Vより小さいという判断)。目標: 3声合計の
   Voice本体語数を、2V時点のVoice A+B合計の**約1.15〜1.3倍程度**に
   収める(3倍にしない、単純追加[約1.5倍相当]よりは絞る)。
4. Tension本体は3者統合のため2V時点よりやや長くなることを許容するが、
   4V(約1.3倍目標)よりは短い**約1.15〜1.25倍程度**を目標とする。
5. Comment 2〜4はテキスト量として大きな変化を想定しない(人数言及の
   書き換えのみ)。
6. 上記を積み上げた**目標総尺のレンジ: 約325〜355秒**(305秒起点の
   +7%〜+16%程度)を、3 Voicesの設計目標として提案する。4V目標
   (+25%〜+40%)より伸び幅を小さく設定しているのは、声の追加数が
   4Vの半分(+1 vs +2)であることに対応させたため。この数値は
   本Trialでの音声実測を伴わない設計目標であり、**未検証**(事実確認
   ではない)。

### 区分別の目安(3V、設計目標・未検証)

| 区分 | 2V実測(参考) | 3V目標 |
|---|---|---|
| 固定parts(Intro〜Comment1+Outro) | 約95.5秒 | 約95.5秒(無変更) |
| Hook | 約21.1秒 | 約21〜23秒 |
| Comment 2〜4合計 | 約35.6秒 | 約35〜38秒 |
| Voice本体×N(見出し+notification+body) | 約84.1秒(2声) | 約100〜112秒(3声、1声平均約33〜37秒) |
| Tension | 約30.7秒 | 約35〜38秒 |
| Closing | 約21.8秒 | 約22〜25秒 |
| pause等 | 約13秒 | 約15〜17秒(segment数増に比例) |
| **合計目安** | **約301.8〜305.1秒(実測)** | **約325〜355秒(目標、未検証)** |

---

## B-7. Tension設計

### 4V: 「2軸交差」ベース(Structure Trial-02から再掲、変更なし)
縦軸=「当事者性の強さ(直接影響を受けるか/決定する側か)」、横軸=
「AI活用への態度(推進寄りか慎重寄りか)」。Applicant=当事者性高・慎重、
Business=当事者性低・推進、Recruiter/HM=当事者性中・両義、Legal=
当事者性中・慎重、という配置。単純な4人要約にしない条件(時系列の
繰り返し禁止、責任・制約の非対称性を軸として言語化)を維持。

### 3V: 別途最適構造(新規設計、2軸交差を無理に流用しない)

3V-c(Applicant/Business/Legal)は「個人的経験」「経済的動機」
「制度的責任」という質的に異なる3種類の利害であり、2軸のマトリクスに
自然に収まらない(3者を2×2に配置しようとすると1マスが空くか、
どちらかの軸で2者が同居して差が薄まる)。代わりに、以下の
「共通前提→分岐点→非対称性」という3段構造を提案する。

1. **共通前提の提示**(要約ではなく、3者が本当は同じことを望んでいる
   という事実の指摘): 3者とも「適切な人が適切な仕事に就く」こと自体を
   望んでいる点では一致している、という共通の出発点を示す(この時点
   では誰も間違っていない、という前提の共有)。
2. **分岐点**(なぜそこから別れるか、答えを要約せず「何が賭かって
   いるか」の違いとして示す): Applicantにとっての賭け金は「一度も
   人に見てもらえないまま機会を失うこと」、Businessにとっての賭け金は
   「大量の応募を裁ける仕組みを持てるかどうか」、Legalにとっての賭け
   金は「その仕組みが誰かを不当に排除していないと証明できるか」。
   同じ状況が、背負っているものによって全く違う重みで感じられる、と
   いう描き方(3者の発言内容の再掲・時系列の反復はしない)。
3. **非対称性**(責任と制約の非対称、プロセスへの発言力の違い):
   Applicantはプロセスに対する発言権を持たない(判断される側)、
   Businessは導入するかどうかを決める側、Legalは事後に線引きをする側、
   という**プロセス上の力関係の非対称**を明示する。これが「なぜ合理的
   な人がここで意見が分かれるか」の核心であり、単なる3人の主張の要約
   ではなく構造的な理由付けとして機能させる。

「Research is backstage. People are on stage.」原則の遵守: 上記いずれの
段も、統計・調査結果を主語にした文(leak_evidence_subject相当)を避け、
3者それぞれの立場・賭け金・力関係という「人」の言葉で語ることを設計上
の条件とする(記事本文レベルでの実証は本Trialの範囲外、未検証)。

---

## Gate 4観点: 未承認仕様・Trial-only定義への依存箇所(明示)

以下はすべて、本Trialでは実装せず**未承認仕様**として一覧化する
(採用にはユーザー判断が必要)。

1. 3 Voices構成そのものの採用可否(1節、3V-c推奨)。
2. 4 Voices構成そのものの採用可否(Axis Trial-01由来、既存
   USER_DECISION_REQUIREDの継続)。
3. Comment 2・Comment 3の3V/4V版文言(B-1、手動ドラフトのみ、
   Role prompt自体の書き換え・LLM再生成は未実施)。FINALIZE-11で
   `APPROVED_FOR_PRODUCTION`済みの確定Contractへの変更のため、
   改めてユーザー承認が必要。
4. TTS voice割当(B-2): Schedar/Sulafatをfallbackから3V/4Vの本採用へ
   格上げすること自体、および性別的印象に基づく交互配置(SSOTに性別
   印象の記載が一切なくユーザー試聴が必須、既存比較sample wavの再利用
   で追加コストなし)。
5. `physical_structure`の新規値(`"six_section"`/`"seven_section"`)・
   `EDITORIAL_TYPES`への新規editorial_type追加方針(B-3)。
6. Registry集約設計(3V/4V用`SECTION_LABELS_3V`/`_4V`・
   `VOICE_ASSIGNMENT_3V`/`_4V`等の新規定数追加、B-3)。
7. QA(Point Overlap/Analytical Leakage)の3ペア/6ペア拡張方式、
   既存閾値0.40の3V/4Vへの適用可否(B-4、検証Trial設計のみ提示・
   未実施)。
8. Audio Validation Gateの完全性チェック新規追加(B-5で新規発見した
   failure mode: 期待segment数と実記録segment数の一致確認機構が
   現状存在しない)。
9. 3V目標尺(約325〜355秒)・4V目標尺(約380〜430秒)の採否(B-6、
   いずれも未検証の設計目標)。
10. Tensionの3段構造(共通前提→分岐点→非対称性、B-7)・4Vの2軸交差
    (Structure Trial-02由来)という内容設計方針そのもの(記事本文
    レベルでの検証は未実施)。

---

## Gate 1分類

**統合設計としての妥当性: VALIDATED(Trial範囲内)**
- 3V/4V双方について、B-1〜B-7の設計項目をすべて既存SSOT(registry.py・
  production_01.py・assemble.py現物、Comment Contract確定文言、2V実測
  duration、Trial-06/07 QA閾値実測値)の引用に基づいて設計・比較できた。
- 3 Voices構成について、既存Axis Trial-01の損失分析を踏まえた4案比較
  (3V-a/b/c/d)を行い、根拠を明示して1案(3V-c)を推奨できた。
- 新規failure mode: Audio Validation Gateが「記録されたsegmentの状態」
  のみを検証し「構造上あるべきsegment数との一致」を検証しない構造で
  あることを、Gate本体のコード現物確認により新規発見した(B-5)。これは
  2Vでは表面化しにくかったリスクであり、3V/4V対応時に完全性チェックの
  追加が必要になる可能性が高いという未承認仕様として記録した。
- TTS voice設計について、SSOT上に性別的印象の記載が一切存在しないこと
  を確認し、ユーザー希望(男性的/女性的交互配置)を現時点の記録だけでは
  満たせないことを明示した(新規voice名の発明はしていない)。
- 記事本文・音声での実証、Contract文言の実際のLLM再生成、QA拡張の実装、
  目標尺の実測検証はいずれも範囲外(未実施)。

**採用判断(3V構成・4V構成・各設計項目の採否を含む): USER_DECISION_
REQUIRED**(上記「未承認仕様・Trial-only定義への依存箇所」10項目参照)。

---

## 禁止事項の遵守

記事本文・音声生成なし、Production/Prompt/Contract/コード編集なし、
SSOT編集なし、Git操作なし、Lane A参照なし(`docs/pm/*`・`er011_*`・
`OPEN-1xx-*`成果物への変更なし、既存OPEN_ITEMS.md/DECISION_LOG.mdは
読み取り専用で引用のみ)、Phase 2配線なし、LLM API呼び出しなし(¥0、
既存録音済みsample wav・既存Reportの引用のみ)、バックグラウンド待機
なし。
