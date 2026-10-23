# INVENTORY_OLD_B_VOICES_01: 旧Family B(Voices)固有仕様・品質NG履歴の棚卸し

管理ID: FAMILY-Y-VOICES-DESIGN-01 / 委任_01B(2026-10-23)
性質: DESIGN/RESEARCH ONLY(read-only、API費用0、Production/Prompt/SSOT変更なし、Trialなし)。
本書は調査記録であり、仕様採用・Production採用の記録ではない(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`への移行なし)。
ユーザー指示原文: `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER.md`(01A保存)。

## 0. 読み方・凡例

- 「承認」欄の根拠は、(a)ユーザー原文/正式決定がSSOTに記録されているもの、(b)Claude/Fable/Opusの内部判断・提案、を区別した。(b)のみのものは「内部判断」と明記し、承認済みとは扱わない。
- Status表記は旧Bの記録上の語(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`/`VALIDATED`/`DECIDED`/`USER_DECISION_REQUIRED`/Trialのみ)をそのまま写した。
- 継承分類案は、ユーザー4分類(A=X/Z共通、B=旧B承認済みVoices固有、C=継承しない、D=Y固有新設計=ユーザー判断)のうち、**旧B由来項目をB(継承)かC(不継承)かで仮置き**したもの。Dに当たる論点は各節末尾と第11節に集約した。確定はFable/ユーザー。
- 旧Bのコード実体: `er012_b_family_voices_writer_generic_01.py`(Writer/Leakage/pipeline)、`er012_b_family_editorial_type_registry_01.py`(構造・Comment・Gate設定)、`er012_b_family_production_runner_01.py`(入口 `main_b1_2v`/`main_b1_3v`/`main_a2_2v`)、`er012_b_family_voices_a2_production_01.py`(A2 TTS/timeline)、テーマ別 `er012_b_family_voices_theme_*.py`。これらは**読取のみ**(§27-3)。
- 旧Bは2026-10-12時点でLegacy/Backup(新規実装・最新仕様追従なし、`CURRENT_SPEC.md:1640-1652`付近)。Family Yは「将来Voices系」(`CURRENT_SPEC.md:1472-1479`)。

---

## 1. 旧Bの記事構造の変遷と最終承認版

### 1-1. 変遷表

| 時期 | 構造 | Status・出典 | 備考 |
|---|---|---|---|
| 2026-09-06 | 設計: Hook / Voice×N(可変)/ Tension / Closing。Closingは「In One Lineと別役割(Meaning/Close)」 | 設計案 `EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md` §5,§7,§13 | Reference Example(カフェ・リモートワーク)の構造分析が起点。原文全文はリポジトリ内に無い(`...TRIAL-05..._REPORT.md` §1注記) |
| 2026-09-06〜07 | Trial-03: 2V。A-Family骨格に載せるため、Tensionは`###`見出しを増やさずVoice 2末尾の無ラベル段落、Closingは`## In one line`枠 | `EDITORIAL-B-FAMILY-VOICES-TRIAL-03_REPORT.md` §2 | Trialのみ。Point QAが`###`ちょうど2つ前提のため。のちに独立見出しへ |
| 2026-09-07〜08 | Trial-07/09: 5区切り Hook / One Voice / Another Voice / Tension / Closing。Tension・Closing・Compactness(約350語soft)の役割をContract化 | Trial-07 `VALIDATED`(Trial範囲内)、Trial-09 音声化。`...TRIAL-07-CONTRACT-REFINEMENT-01_REPORT.md` §0,§1 | 一人称はWriterの自発選択で、promptには未明記だった(`...4V-ARTICLE-TRIAL-02_REPORT.md` §1) |
| 2026-09-08 | ユーザー試聴で4項目 `APPROVED_FOR_PRODUCTION`: (1)Voice A=Algieba/B=Erinome/Narrator見出し=Aoede、(2)Tension slot「Where the Difference Comes From」を正式構造へ、(3)Key Phrase位置=Preview直後(現状維持)、(4)Voice A/Bの一人称"I" | `DECISION_LOG_HISTORY.md:7388-7460`(PM-CLOSEOUT-CONSOLIDATION-05)。コード定数: `registry.py:45-72` | Comment 1のみ修正要。Comment Contract全体は後日確定 |
| 2026-09-08〜09 | B1/A2 Phase1 Production配線(2V、5区切り)。Comment 1〜4+Preview。A2は日本語Comment/Preview・日本語タイトル・6%slowdown | `PRODUCTION_WIRED`(`CURRENT_SPEC.md:667-690`の節。B1=PHASE1-WIRING-01、A2=A2-PRODUCTION-WIRING-01、2026-09-09) | 物理構造は`registry.py:69` `SECTION_LABELS=("hook","voice_a","voice_b","tension","closing")` |
| 2026-09-08〜09 | 4V設計(Axis Trial-01/Structure Trial-02/統合Trial-03)→4V本文Trial-01/02。7区切り案 | 設計 `VALIDATED`(Trial)、本文はLeakageが3 attemptsで解消せず(`...4V-ARTICLE-TRIAL-02_REPORT.md` §3) | 4Vは不採用方向へ(下記) |
| 2026-09-09 | ユーザー決定: 4V→3V(人物Voice)へ設計修正。Voice=「論点でなく、その立場から"I"で語れる具体的な人物」 | `DECISION_LOG_HISTORY.md:8530-8552`(PM-CLOSEOUT-CONSOLIDATION-37 (2))。**原則自体は「B-Family設計原則の候補(未承認)」と記録**(同:8549-8551) | 3V Person-Voice Trial-01/02/03 |
| 2026-09-09〜10 | 3V 6区切り Hook / Voice1-3 / Tension / Closing。3V Audio Trial `VALIDATED`(09-09)→`APPROVED_FOR_PRODUCTION`(09-10) | `CURRENT_SPEC.md:690`、`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01-CLOSEOUT_REPORT.md` | 実測356.6秒(2V比+約17%) |
| 2026-09-14 | Production Writerを2V/3V可変に一般化(OPEN-151)。Status訂正でPARTIAL | `CURRENT_SPEC.md:691` | 2V/3Vテンプレートが別コピー→のち不整合発生(§4) |
| 2026-09-17 | Voice立場境界(A/C/E/F)+`leak_position_blur`+Acceptance Gate | `APPROVED_FOR_PRODUCTION`→Voices基盤`PRODUCTION_WIRED`確定(`CURRENT_SPEC.md:693`、`DECISION_LOG.md:8235-`) | PN B1は別管理(OPEN-166) |
| 2026-10-12 | 17記事構成に「Family Y(Voices)3記事」。ただしY自体は未着手(`CURRENT_SPEC.md:2797`、`:1640-1646`) | ユーザー正式決定 | |
| 2026-10-16〜23 | Family A/B/C = Legacy。Y設計開始。Yは**3 Voices固定・5パート・Tension+Closing統合** | 本タスクのユーザー指示 | 旧B最終版からの構造変更は「Closing独立の廃止」「3V固定化」 |

### 1-2. 旧B最終承認版(3V、Production wiring対象の形)

- 区切り: `# Title` / `## The Question`(Hook、目安<70語)/ `###`×3(Voice 1〜3)/ `## <Tension見出し>` / `## <Closing見出し>`(`writer_generic_01.py:159-216`、見出しは合計ちょうど6つ・`## In one line`追加禁止)。
- 学習支援: Preview+Comment 1〜4(Comment 1=Hook前のListening Focus、2=Hook→Voicesの橋渡し、3=Voices後・Tension前の「なぜ違って感じるか」への視点移動、4=Tension後・Closing前の「表面対立から一段深い問い」)。Key Phrase=Preview直後。出典 `registry.py:76-200`。
- **In One Lineは旧Bに独立して存在しない**。Closingがその位置を占め、Assembly上のsegment名は`in_one_line`(Closing)と`tension_reflection`(Tension)(`er012_b_family_voices_a2_production_01.py:793,883`、`registry.py:73`)。命名の名残がGate辞書に残る(`er003_v1_n3_01_assemble.py:193` `"B_FAMILY_A2": ("in_one_line","point_one_heading","point_two_heading")`)。
- 3Vは**B1(英語B1相当)レベルのみProduction構造対応**。`registry.build_required_structure(level="a2", voice_c=...)` は `ValueError`(`registry.py:577-581`相当、「3VはB1のみ」)。3V×A2は`USER-TEST-VOICES-A2-MINIMAL-01`のドライバ(Trial、2026-09-16)のみで、Production未配線(`DECISION_LOG.md:7920-7925`)。
- 語数・尺: 3V soft target 410〜450語(Hook45-55/Voice各70-85/Tension75-90/Closing45-55)(`writer_generic_01.py:346-354`)。実績はTrial-02 497語/395秒(超過)、Trial-03 483語/388秒、PN 2V A2 331秒。尺目標は325〜355秒→3V更新後380〜400秒(`3V-AUDIO-TRIAL-01-CLOSEOUT` 項目4)。

| 項目 | 最終承認仕様 | Trialのみ/不採用 | 実装の所在 | Y継承分類案 |
|---|---|---|---|---|
| Voices数 | 2V/3V(可変一般化はPARTIAL) | 4V(Trialで解消せず、3Vへ設計修正) | `writer_generic_01.py:62-66`,`:2039-` | **C**(Yは3V固定。可変構造は不要=ユーザー決定) |
| 5区切り(2V) | `PRODUCTION_WIRED` | Trial-03の「Tensionを無ラベル段落」案 | `registry.py:69` | **C** |
| 6区切り(3V、Closing独立) | `APPROVED_FOR_PRODUCTION`+基盤`PRODUCTION_WIRED` | 7区切り(4V) | `writer_generic_01.py:62` | Voice×3+Tension部分は**B**、Closing独立は**C**(ユーザー決定) |
| Preview/Comment 1-4/Key Phrase位置 | Preview直後=承認(2026-09-08)、Comment Contract=確定 | Comment 1の旧文言(修正Trial-10/11) | `registry.py:76-200` | 構造はXの最新仕様を**A**で継承。**Comment 4の位置(Tension後・Closing前)はYでは消える→D**(§11) |
| In One Line | 旧Bに独立なし(Closingが兼ねる) | — | `a2_production_01.py:793` | Y側はXのIn One Line仕様を**A**。TensionとIn One Lineの関係は**D** |
| Hook(The Question) | 「3立場を簡潔に提示、結論を先取りしない」、Imagine系・企業名・統計禁止 | — | `writer_generic_01.py:295-301` | Yの「リード文」へ**B**(役割整合を要確認) |

---

## 2. 3 Voicesの人物・視点設計方法

### 2-1. 旧Bで実際に行われた方法

1. **人物の決め方(旧B)**: テーマ固有モジュール(`er012_b_family_voices_theme_*.py`)に**Voice Cardが人手で書かれている**。自動生成primitiveは存在しない(Opus所見 `...3V-4V-WRITER-DESIGN-OPUS-REVIEW-01_REPORT.md` §0-B「VOICE_n_EVIDENCEタグ付きLedgerを自動生成するprimitiveは存在しない」。本調査でも`voice_cards`生成関数をGrepして該当なし=Writer内で`make_voice_card`を受けて整形するのみ、`writer_generic_01.py:79-96`)。新規topicでは「Verified Fact Ledgerは既存を再利用、Voice Cardはテーマ定義側で供給」という運用(PN A2: `theme_personalized_news_a2_01.py:39-67`)。
2. **Voice Cardのフィールド(14)**: voice_key, stakeholder_label, role_description_ja, reference_phrase, person, situation, need, concern, protect, why, constraint, concrete_scene, supporting_evidence, stake(`writer_generic_01.py:72-77`)。Writerは「Voice Cardの具体的状況から書き始める」。supporting_evidenceは「裏付け専用、本文の主役にしない」(`:430-447`)。
3. **視点選定の基準の変遷**:
   - Trial-04/05: 「2人は好みの結果が違うだけか」(Diversity Check)。責任の重さ・立場の違いで多様性を作る案(実名のワークプレイス責任者を採用)→ Trial-05は3 attemptsでflagged(narrator_analysis/unknowable_analysis)、Evidence Compression Editorによる分析文の挿入・実名匿名化も観測(`...TRIAL-05..._REPORT.md` §0)。
   - Trial-06: **ユーザー判断で基準を切替**: 「同じStakeholder群(社員)の中の主要な意見の違いを、理由・経験・守りたいものまで掘り下げる」「一般視聴者が認識しやすい主要な意見から順に採用」(`...TRIAL-06..._REPORT.md` §1.1-1.4)。このTrial-06基準は同Reportでは`VALIDATED`(Trial範囲内)、正式採用は別途UDRとされた。**現行CURRENT_SPECに明文の恒久規則としては見当たらない(未確認)**。
   - 4V設計(Axis Trial-01): Applicant/Recruiter・HM/Business/Fairness・Legal・Governanceの抽象軸 → 本文Trialで抽象軸(Business/Legal)が数値・制度解説に戻り失敗。
   - 3V人物Voice(ユーザー決定2026-09-09): 「Voice=論点ではなく、その立場から"I"で語れる具体的な人物(得る・失う・責任を負う人物)」。AI採用テーマは Applicant / Recruiter・Hiring Manager / Business Owner。Fairness/Legal/HR Governanceは**Voiceから外し、Tensionの外部制約として統合**(`DECISION_LOG_HISTORY.md:8530-8552`)。**この「Voice=具体的人物」はSSOT上は「設計原則の候補(未承認)」と記録されたまま(`:8549-8551`)で、CURRENT_SPECの恒久規則欄には無い(Grep: `CURRENT_SPEC.md`に「具体的人物」該当なし)。ただし3V方式そのものは2026-09-10に`APPROVED_FOR_PRODUCTION`**。今回のY指示§2.3が、この原則を事実上ユーザーが再確認している形(Y側でA/B整理上はユーザー指示を根拠にする)。
4. **賛否以外の軸**: 統合設計Trial-03の3V-c推奨は「個人的経験/経済的動機/制度的責任」(質的に異なる3利害、`design.md` §1-2)。ただし実際にユーザーが採ったのは Applicant/Recruiter・HM/Business Owner(design.mdが「2対1陣営化リスク高」とした3V-a型)で、リスクは外部制約のTension統合で緩和する設計(`...PERSON-VOICE-TRIAL-01_REPORT.md` §1)。Trial-02/03で`leak_binary_camp_split`は2/2 PASS。
5. **ペルソナ生成Prompt**: 専用の「ペルソナ生成Prompt」は存在しない。Voice Cardをテーマごとに人手(Fable/Sonnet)で作成し、Writer templateへ注入する(`writer_generic_01.py:450-`の`build_focus_module_block_3v`)。見出しは「One Voice:/Another Voice:/A Third Voice:」または人物を示す語(`reference_phrase`)で、「Voice 1」「賛成/反対」型ラベルは禁止(`:177-181`)。
6. **Voice間の割り当て**: Voice順は「当事者→経営→監督」と距離が遠ざかる順(Structure Trial-02の隣接対比、`design.md` B-3)。TTS声は Voice1=Algieba/Voice2=Erinome/Voice3=Schedar、Narrator=Aoede、Comment/Preview=Charon(B1)(`registry.py:45-62`)。**TTS声の最新方針はX/Z側(A)に従うべきで、旧Bの声割当は不継承が妥当**(声はFamily Z共通Voice選定Trial等で更新されている旨は未確認、委任01Aの範囲)。
7. **Ledger側の割当**: Ledgerに`[VOICE_n_EVIDENCE]`タグを付け、Voice Cardの`concrete_scene`/`supporting_evidence`がそのタグを引用(Fact Checker A'免除の前提、`registry.py:399-460`)。
8. **Y既存Trial**(旧B後の参考): `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01`(2026-09-28、¥5.90)は、Family X「Storyline決定+B3 Fact選定」でVoiceごとにfact_id/Angleを割り当てる前段を試し、Voice間fact_id重複0件を確認した。一方でFamily X R1→R2 RevisionをVoice文脈へ適用すると旧B Leakageのfail-field数が 2→3→11 と悪化し、LLM rubric評価との乖離が出た(`FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md` §3-4、`OPEN-217/218/219`)。Y判定は`USER_DECISION_REQUIRED`のまま。**これはYの設計材料だが、旧B仕様ではないため分類はD側(Y設計の前提Trial)**。

### 2-2. 継承分類案

| 項目 | 分類案 | 理由 |
|---|---|---|
| Voice Card方式(人物の状況・必要・心配・守りたいもの・具体場面から書き始める) | **B** | 品質NG(解説者化)を最も直接抑えた構成要素。Y指示の「独立した人物」と整合 |
| 14項目フルセットのCard | **要検討(B簡素化はD)** | 項目数が多くテーマごとの人手作業(費用・時間)。Yで項目を絞るかはD |
| Voice Cardを人手で作る運用 | **D** | 量産(Y 3記事/17記事構成)での工数・品質。自動化案は旧Bに実装なし。ユーザー判断事項候補 |
| 賛否・陣営の機械割当をしない | **B**(ユーザーが2.2で再確認済み) | |
| 4V/可変Voice数/抽象軸Voice | **C** | |
| Trial-06基準(主要な意見から順、同じStakeholder群内の違い) | **B候補(正式規則ではなくTrial基準。Yの3視点設計でどう使うかはD)** | 未確認: CURRENT_SPEC恒久規則化の有無 |
| TTS声割当(Algieba/Erinome/Schedar/Aoede) | **C** | X/Z共通方針に合わせる(A) |

---

## 3. Voice間の独自性・立場境界

| 項目 | 最終承認仕様(Status・日付・出典) | Trial・不採用 | 実装 | 性能・履歴 | Y分類 |
|---|---|---|---|---|---|
| 単純2対1陣営化の禁止 | 3V template【賛否2対1を作らないこと】(`writer_generic_01.py:232-235`)、Tension側`leak_binary_camp_split` | 3V-d(統合Voice)非推奨 | `:970-973`,`:1055-1056` | Trial-02/03で2/2 PASS。実害は未観測 | **B** |
| Voiceは自分の経験・立場に徹する(候補A) | `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`、ユーザー正式承認2026-09-17(`CURRENT_SPEC.md:693`) | 候補B(Narrator/Evidenceレイヤー新設)不採用 | `writer_generic_01.py:280-286` | PN A2新版 attempt1でLeakage 0件 | **B** |
| 迷い・葛藤(nuance)は許容、相手側の中心論点は抱え込まない(候補E) | 同上 | 候補D(1 Voice=1 Primary Positionの恒久ルール化)不採用 | 同上、`:370-372`(禁止事項) | **境界はOPEN-167で未決**(下記) | **B(+D)** |
| 相手側の中心懸念はTension(または別Voice)が引き受ける(候補F) | 同上。Tension役割文言に明記(`:315-317`) | — | `:315-317` | — | **B**(YのTension+Closing統合後も役割は維持。位置づけはD) |
| `leak_position_blur`(立場越境検知) | 同上、Voice数非依存の7番目field(`:965-969`,`:1039-1041`) | — | Leakage schema/prompt/是正メモ | 既存5記事offline再評価: AI hiring B1=0 FAIL、free_address B1/A2=0 FAIL(誤検知なし)、AI hiring A2=voice_2/3他でFAIL(`position_blur`自体は全PASS)(`docs/pm/RESULT_PACKET_VOICES_SPEC_01.md` §6) | **B** |
| Voice間lexical overlap | monitoring専用(合否判定に使わない)。有向ペア6+vs Hook 3の9値(`:888-915`) | 閾値0.40は包含関係用で不適(Opus、`...OPUS-REVIEW-01` §2-§3) | `er008_point_overlap_qa_18`流用 | 語彙ベースで「推論構造が同一」を検知できない(Opus HIGH指摘)。実測Point Overlap最大0.16(Opus L3) | **C**(gate化せず、語彙指標に依存しない設計) |
| Pairwise Voice Distinctness Check(5軸: 立場/制約/責任/守るもの/推論) | **Trial限定**。正式採用は別途UDRのまま(`DECISION_LOG_HISTORY.md:8545-8546`)。CURRENT_SPECに採用記録なし | 実績: direction一致率1.0/0.933(Trial-02)→0.933/0.867(Trial-03、本文同一でLLM判定ノイズ) | Trialスクリプトのみ | 判定ノイズあり | **D候補**(使うならYで新規採用判断。Charter上、新Validator増設の目的化は避ける) |
| Diversity Check(Perspective選定時) | 人手+Prompt埋込(自動QAではない)。Opus MED指摘 | Trial-05基準→Trial-06基準へ変更 | `perspective_map.md`(人手) | — | **B**(手順)/D(Yでの具体化) |
| Voice同士の主張取り込み | OPEN-167(`OPEN_ITEMS.md:348`)が論点7つを整理して`OPEN/DEFERRED`。ユーザーはPN A2新版の「I still worry an important story could be left out.」を許容(再生成せず) | OK寄り例"Personalization is useful when I can still choose what to follow."/NG寄り例"...but I worry I may miss important stories."(**提案であり未承認**) | `leak_position_blur`の`nuance allowed`範囲 | Validatorは当該文をPASS(PN A2新版でLeakage 0件)。ユーザー知覚との乖離が残る | **D**(Y指示§2.3「他Voiceが担う反論まで抱え込まない」は方針、境界の厳密さは未決) |

**境界Validatorの性能まとめ**: Analytical Leakage Check(LLM判定、PASS/FAIL×7項目)は、ユーザーが問題視した統計文2件を**両方機械検知していた**(`RESULT_PACKET_VOICES_SPEC_REVIEW_01.md` §3)。検知できなかったのは立場越境(当時項目なし)で、新設の`leak_position_blur`も、ユーザーが後に指摘した「肯定派Voiceが相手側の懸念を語る」例を**PASSした**(`DECISION_LOG.md:8235-`)。つまり**項目の定義範囲(nuance許容)と、ユーザーの期待する純度の間にギャップが残る**。AI hiring 3V Owner Voiceの"But news of a tool that rated women lower makes me look twice at my own choice"はSPEC-REVIEWで「中リスク」と指摘されたが、新Validatorはvoice_3他でも`leak_position_blur`をPASSした(offline再評価)。

---

## 4. 一人称表現・主観的意見の扱い

| 項目 | 最終承認仕様 | Trial・不採用 | 実装 | Y分類 |
|---|---|---|---|---|
| Voice本文は一人称"I"(Hook/Tension/Closingは語り手・三人称) | ユーザー正式決定2026-09-08(`APPROVED_FOR_PRODUCTION`(4))(`DECISION_LOG_HISTORY.md:7388-`)。Production template【人称】(`writer_generic_01.py:255-262`)、禁止事項(`:361-362`) | Trial-07の2V promptには一人称指示は無く、Writerの自発選択だった(`...4V-ARTICLE-TRIAL-02_REPORT.md` §1)。4V Trial-02で初めて明文化 | template 3V:`:255-262`。2V templateは**当初欠落**(Production不整合として2026-09-15修正、commit `ccf43e8c`、`CURRENT_SPEC.md:700-708`付近) | **B**(Y指示と一致) |
| 外から要約・分析する語り手文の禁止(Narrator analysis) | template【Narrator(語り手)がVoiceの人物を外側から要約…】(`:264-268`) | — | 同、`leak_narrator_analysis` | **B** |
| 書き始めは"For an applicant who..."型の外側紹介ではなく具体状況から | `:248-253` | — | — | **B** |
| 友人に話すようなlight/conversationalトーン | `:290-293`、レポート調禁止 | — | — | **B**(Xの最新Writer仕様と整合要確認=A/B接点) |
| 同じ意味を2回言わない | `:343-344` | — | — | **B** |
| 解決策・コンサル提案の禁止 | `:303-306`,`:356-373` | — | — | **B** |
| 一人称の機械的保証(Gate化) | OPEN-132(2)で「`editorial_type_module`による機械保証」が課題として登録。2026-09-15修正時に`pov_check`の機械確認は実施(`USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md` 4節) | — | 常設Gateかどうかは未確認 | **D**(Yで一人称をGate化するかは新規判断) |

**承認された言い回し境界の根拠**: 具体的なNG/OK例文集(承認済み)は旧Bには存在しない。例示は、体験claim根拠付けの例"if that ever came out, it would be my name on it, not anyone else's"(OK)対"my reputation would be destroyed"(NG)(`writer_generic_01.py:389-391`、`CURRENT_SPEC.md:692`)のみ。OPEN-167の例文は提案段階。
**構造的教訓**: 2V/3Vで別テンプレートが重複して存在したため、片方に承認済み仕様が欠落する不整合が起きた(2026-09-15)。→ Yは単一テンプレート前提とすべき(分類: 重複テンプレート構造は**C**)。

---

## 5. Fact Safety・Fact Attribution

| 項目 | 最終承認仕様 | Trial・不採用 | 実装 | Y分類 |
|---|---|---|---|---|
| 体験claimの根拠付け(数値・制度・他者の具体的行動はLedgerに直接evidenceがあるものに限る。無根拠の未来結果は断定せず感情・判断として書く) | `DECIDED`、恒久Writer原則、ユーザー決定2026-09-12(`CURRENT_SPEC.md:692`) | — | `writer_generic_01.py:382-392` | **B**(Y指示の「検証可能な数値・制度・他者行動を創作しない」と一致) |
| Voice内数字の扱い(候補C): 本人の経験に属する数値のみ、最大1つ、外部統計を論証に使わない | `PRODUCTION_WIRED`、2026-09-17ユーザー承認(`CURRENT_SPEC.md:693`)。2026-09-13に「数字必須」要求は撤廃済み(2-D、同:690内追記) | 旧: Voice Cardが「数字を織り込め」と命令→Evidence主語禁止と二律背反(Opus L3) | `:270-278`,`:430-447` | **B** |
| Verified Fact Ledger(`[VOICE_n_EVIDENCE]`タグ付き)+Fact Checker A'(Web検索)+Ledger Deviation Checker+Local Rewrite | writer_generic pipelineは常時実行(`run_voices_pattern_3v/2v`、`:1691-1790`)。Fact Attribution A'(Voice本文は出典明記不要のopt-in)は`PRODUCTION_WIRED(opt-in)`、`fact_attribution_mode`既定False(`registry.py:373`) | A'候補は小規模Trial(N=5、false accept 0)のみで検証。実在人物引用・数値改変は5/5検出(`...MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-02_REPORT.md` §2) | `registry.py:399-460` | Fact Checker/Ledger/Local Rewrite = X/Zの最新(A)を使うため旧B固有は**C**。A'は**C候補**(下記) |
| A'と候補C(統計をVoiceに語らせない)の方向性不一致 | 「A'は既定OFF据え置き、将来ONにする場合の両立条件は別途設計(未設計)」(`CURRENT_SPEC.md:693`) | — | — | **C**(YはC方針=外部統計をVoiceに語らせない。A'をYに持ち込まない、という整理が自然。ただし判断はFable) |
| 保守版Fact Safetyゲート(`voice_fact_safety_gate_mode`): 一人称・certainty系のみ等の条件でMAJOR→MINOR再分類 | `APPROVED_FOR_PRODUCTION`、既定ON(B-Family限定)(`CURRENT_SPEC.md:695`、`registry.py:464`)。runtime evidence(Production実発火)は未取得 | 段階1は実データ21件中0件適用(Stage1は効果なし)、段階2はTension 6/6適用(`...FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md` A節) | `writer_generic_01.py:1352-1500` | **C**(テーマ依存辞書`_VOICE_GATE_INSTITUTIONS`の汎用性限界、Stage1の効果なし。Yは別構成を設計) |
| Directional Fact Precheck | 記録のみ(retry/gateに関与せず) | — | `:1756-1764` | A/C判断はX側仕様に従う |
| 構造的衝突: Tensionの「3人の役割・権限差を1文で断定」vs Ledger Deviation Checkerの`changed_actor`/`unsupported_new_claim` | 4個体全てで同一スロット(Tension非対称性文)でMAJOR化。hedge増量では収束しない(9箇所でも不合格)(`...FACT-SAFETY-STRENGTH-DESIGN-01_REPORT.md` 要点1-2、Opus L3 論点3) | Local Rewriteのhedge方式 | — | **D**(Yのaccepted Tension設計は、この衝突を前提に書き方を決める必要あり) |

**Fact Attributionの書き方**: 旧Bでの「Attribution」はVoice本文に出典を書くことではなく、(a)Ledgerタグで「この証拠はこのVoiceの持ち物」と紐付け、(b)Fact Checkerに「Voice本文は出典明記不要(事実誤り・実在人物引用は従来どおり検証)」と指示するrule(`registry.py:399-460`)。候補C採用後は、Voice本文に外部証拠の出典を書く場面自体が減る。

---

## 6. Analytical Leakage Check

- **目的**: Voiceが「調査結果の説明」に戻っていないかをLLM(Writerと同一モデル)でPASS/FAIL判定。Trial-05で導入、Trial-07で拡張、3V/2Vへ一般化(`writer_generic_01.py:953-1115`)。
- **項目**: Voice 7(`leak_evidence_subject`/`leak_numbers_foreground`/`leak_narrator_analysis`/`leak_unknowable_analysis`/`leak_discovery_syntax`/`leak_evidence_memorable`/`leak_position_blur`)、Tension 6(+外部制約統合時1: `leak_tension_reverts_to_research`/`leak_binary_camp_split`等)、Closing 1(`leak_closing_simple_summary`)(`:965-975`)。
- **判定規則・閾値**: 項目ごとPASS/FAIL(数値閾値なし)。FAILなら`quoted_evidence`引用必須。any flaggedで是正メモ付き全文再生成、`MAX_WRITER_ATTEMPTS=3`(初回+是正2回)(`:67`,`:1885-1947`)。
- **Status**: Analytical Leakageの「正式化可否」は当初USER_DECISION_REQUIRED(`registry.py`のPHASE2_PENDING_NOTES)。実質は2026-09-17のユーザー承認(A/C/E/F+`leak_position_blur`+Acceptance Gate)でProduction配線済み(`CURRENT_SPEC.md:693`、`DECISION_LOG.md:8235-`)。
- **Acceptance Gate**: 3 attempts後も残存flagならstatus=`LEAKAGE_RESIDUAL_STOP`で後続stageへ進めない(旧「前例踏襲でPARTIAL扱いし試聴へ進める」運用は廃止、`writer_generic_01.py:1930-1946`、`RESULT_PACKET_VOICES_SPEC_01.md` §4)。

| 履歴(代表) | 結果 | 出典 |
|---|---|---|
| Trial-05(2V) | 3 attemptsとも flagged(narrator_analysis/unknowable_analysis) | `...TRIAL-05..._REPORT.md` §0 |
| Trial-06(2V、一人称化) | attempt3で全PASS。一人称化で narrator_analysis/unknowable_analysis が一度もFAILしなくなった | `...TRIAL-06..._REPORT.md` §0 |
| Trial-07(2V) | attempt2で0件(Tension/Closing役割の追加が機能)。ただし語数453 | `...TRIAL-07..._REPORT.md` §0 |
| 4V Trial-01/02 | 3 attemptsでvoice_3/4のDiscovery構文が解消せず | `...4V-ARTICLE-TRIAL-02_REPORT.md` §3 |
| 3V Person-Voice Trial-01 | 最終attempt3がNG_REVIEW_REQUIRED(Voice 3は人物化でattempt1/2 0件) | `...PERSON-VOICE-TRIAL-01_REPORT.md` §2 |
| 3V Trial-02 | attempt2で0件(2 attempts) | `...TRIAL-02_REPORT.md` §1 |
| 3V汎用化Regression(2回) | 6/6 attempt flagged(旧は1/2)。Fisher片側p=0.25。Opusは「whack-a-mole」(直した箇所の代わりに別Voiceで再発)を指摘 | `...OPUS-L3-DIAGNOSIS-01_REPORT.md` 論点1 |
| PN A2旧版 | 3 attempts後に voice_a/voice_b残存→ユーザー試聴NG(統計引用・立場曖昧) | `RESULT_PACKET_VOICES_SPEC_REVIEW_01.md` §2-3 |
| PN B1 | voice_b 5/6項目FAIL+tension 2/5項目FAILのまま音声化済み。新Validatorで再評価してもFAIL。再生成はLedger鮮度問題(OPEN-166)でSTOP | `RESULT_PACKET_VOICES_SPEC_01.md` §6 |
| PN A2新版(2026-09-17、候補A/C/E/F後) | attempt1で7項目全PASS、ユーザー承認。試聴で「相手側懸念の取り込み」を指摘されたが許容 | 同、`DECISION_LOG.md:8235-` |

- **誤検知・見逃し**: 誤検知=free_address B1/A2の再評価で0件FAIL(誤検知なし)(`RESULT_PACKET_VOICES_SPEC_01.md` §6)。見逃し=立場越境(spec gap)、nuance許容範囲の見逃し(OPEN-167)。また、any_flaggedトリガーが「主語位置のみの形式的指摘」でも3 attempts全消費を招く(Opus L3の(D)案=severity階層、未採用)。
- **コスト特性**: 1 attemptに Writer+Overlap+Fact Checker A'(Web検索)+Ledger Deviation+Leakage Checkが全て含まれ、flagged時は**全文書き直し**(Opus L3(C): Ledger側のLocal Rewriteと同様の局所書き換えをLeakageにも適用すれば費用削減の見込み、未採用)。
- **Y分類**: Leakage Check項目群(特に`leak_evidence_subject`/`leak_numbers_foreground`/`leak_narrator_analysis`/`leak_position_blur`)とAcceptance Gateの考え方は**B**。ただし「全文書き直し×3」というretry方式は**C**(Opus L3(C)の局所書き換えをYで採るかは**D**)。Closing項目(`leak_closing_simple_summary`)はTension統合に伴い**C**(Tension項目へ吸収の要否は**D**)。

---

## 7. Tensionの役割とClosingの履歴

### 7-1. Tension(承認済み)

- **原文の構造**: 「共通前提→分岐点→非対称性」(design.md B-7、`writer_generic_01.py:308-333`)。
  1. 共通前提: 3人とも本当は同じこと(`{tension_common_ground_value}`)を望んでいる。誰も間違っていない。
  2. 分岐点: 答えを要約せず「何を賭けているか」の違いとして示す。各人の賭け金(`stake_n`)。**3人の発言内容の再掲・時系列の反復はしない**。
  3. 非対称性: プロセス上の力関係の非対称(`{tension_asymmetry_value}`)。
  4. (任意) 外部制約統合(3b): 規制・監査等が3人の選択肢をどう制約するか。3V共通の必須規則にはせず、Fableが任意適用(`CURRENT_SPEC.md:694`、`DECIDED`2026-09-12)。
- 禁止: 「どの立場が正しいか」を決める/Evidence(survey等)を主語にする/Tensionをdataの説明へ戻す/2対1陣営化/解決策提案/Ledgerにない因果の創作(`:309-333`)。**Tensionは各Voiceが抱えきれなかった相手側の中心的懸念も公平に受け止める場所**(候補F、2026-09-17、`:315-317`)。
- スロット名: 「Where the Difference Comes From」(2026-09-08承認、`registry.py:72`)。2V時代の4軸(測定基準/優先する利害/価値観/問いの立て方、Trial-07)は3Vでは上記3段へ置換。
- 長さ: 目標75〜90語。実測はTrial-02で132語、Trial-03で圧縮直後90語→Local Rewrite後118語(`...PERSON-VOICE-TRIAL-03_REPORT.md` §1)。「60語未満に削って3段の要素を省略することは避ける」(`:353-354`)。
- **履歴上の弱点**: (i)Tensionは4個体すべてでLedger Deviation(非対称性文)が集中するスロット(§5の構造的衝突)。(ii)Trial-03の短縮再生成では Local Rewrite が非対称性文を曖昧化し、禁止していた抽象軸表現"business-efficiency concerns"を再導入、外部制約統合も一般論へ後退した(`...TRIAL-03_REPORT.md` §1)。

### 7-2. Closing(履歴)

| 時期 | Closingの扱い | 出典 |
|---|---|---|
| DESIGN-02 | In One Line(静かな要約)とは別の「Meaning/Close」。勝者を決めず「新しい問い」または「判断基準の転換」を提示。Fact Safetyの「Evidence-bounded Interpretation」との緊張を認識しつつ「Ledgerの構造的違いを言い換える形にとどめる」 | `...DESIGN-02_REPORT.md` §13 |
| Trial-03 | `## In one line`枠にClosingを置く | `...TRIAL-03_REPORT.md` §3 |
| Trial-07 | Contractに追加:「人による」で終わらせない、問題が実は何についてかを一段深く見せる。表面対立軸の組替えは可能ならVoice CardとTensionから自然に導く(どの軸かは決め打ちしない) | `...TRIAL-07..._REPORT.md` §1 B |
| 3V template | 「要約でもIn One Lineの言い換えでもない。Hook時点から問題の見え方がどう変わったかを再定義する。前段の要約から書き始めない」。Closing 45〜55語。`## In one line`見出しの追加は禁止 | `writer_generic_01.py:209-210`,`:335-341` |
| Opus L3 | 4個体全て Closingが同一修辞骨格(「Xは単に〜かという問いではない。それは誰がA、誰がB、誰がCかという問いだ」)。記事間類似を測るQAは存在せず、次テーマで判別すべきと指摘 | `...OPUS-L3-DIAGNOSIS-01_REPORT.md` 論点6 |
| Y(ユーザー決定) | 独立Closingを廃止し、Tensionへ統合 | `FAMILY-Y-VOICES-DESIGN-01_USER.md` §2.4 |

**分類案**: 「共通前提→分岐点→非対称性」の基本構造と、「再要約・時系列反復を避け、違いを浮き彫りにする」原則は**B**(ユーザー指示と整合)。Closingの独立役割・`leak_closing_simple_summary`・Closing語数配分・Comment 4(Closing直前)は**C**。Tensionに「問題の見え方の再定義」を吸収するか、どこで自然に締めるか、語数・尺の再配分は**D**。

---

## 8. 旧Bで品質NGを生んだ構造的原因・承認済み改善策・残存リスク

### 8-1. 事例とfailure mode

| ID | 事例 | failure mode | 頻度 | 原因分析 | 出典 |
|---|---|---|---|---|---|
| F1 | Trial-04: 調査報告調で数字が連続("reported"/"showed the same pattern") | 解説者化(Voice=調査要約) | 初回Trial | Voice Cardなし、Evidence主役 | `...TRIAL-05..._REPORT.md` §0 |
| F2 | Trial-05: narrator_analysis/unknowable_analysis | 語り手がVoiceを外側から要約 | 6/6 Voice-instance | 三人称・分析文。Evidence Compression Editorが分析的要約文を挿入し、実名を匿名化 | 同 |
| F3 | 4V Trial-01/02: Business/Legal Voiceの Leakage解消せず | 抽象的分析軸(効率・法)のVoiceが数値・制度解説へ逆戻り | 3 attempts全て | 人物でなく「抽象的な軸」だった | `...3V-PERSON-VOICE-TRIAL-01_REPORT.md` §0 |
| F4 | 3V汎用化Regression: 統計主語文・数字前景化 | Voice Cardの「数字を織り込め」命令とEvidence主語禁止の**二律背反** | 新2本とも非収束 | theme側supporting evidenceが集計統計のみ(49%/79%/90%)。retryは全文書き直しで別Voiceに再発(whack-a-mole) | `...OPUS-L3-DIAGNOSIS-01_REPORT.md` 要点1-3,論点4 |
| F5 | Tension非対称性文のLedger逸脱 | 構造要求(役割・権限差の断定)とLedger Deviationの衝突 | 4個体で同一スロット、hedge9箇所でも不合格 | 要求と検査の構造的矛盾 | `...FACT-SAFETY-STRENGTH-DESIGN-01_REPORT.md` 要点1-2 |
| F6 | PN A2旧版(ユーザー試聴NG 2026-09-17) | (問題A)VoiceがSurvey/統計を引用、(問題B)各Voiceの立場が曖昧 | 当該1本 | 旧規則は統計主語・複数数字の禁止はあったが、立場境界の規則と検知項目なし。MAX_ATTEMPTS後に前例踏襲でPARTIALとして試聴へ進めていた | `RESULT_PACKET_VOICES_SPEC_REVIEW_01.md` §2-3 |
| F7 | PN A2新版(承認済み)の残存 | 肯定派Voiceが相手側中心懸念を語る | 当該1本、ユーザー許容 | nuance許容範囲がValidatorとユーザー期待でずれ | `DECISION_LOG.md:8235-`、OPEN-167 |
| F8 | Closing修辞骨格の4/4同型化 | テンプレート固着(記事間自己類似) | 同一テーマ4個体 | 記事間類似を測るQAなし | Opus L3 論点6 |
| F9 | PN B1: Ledgerの内容が新しい外部研究と矛盾 | Ledger鮮度 | 1件 | 時間経過 | OPEN-166(`RESULT_PACKET_VOICES_SPEC_01.md` §6) |
| F10 | 2V templateに【人称】指示と禁止事項が欠落 | 重複テンプレートによる承認済み仕様の取りこぼし | 1件 | 2V/3V別コピー | `CURRENT_SPEC.md:700-708`付近 |
| F11 | 音声: Narrator見出し"One Voice:"/"Another Voice:"がASRで欠落し Human Review Lock | 見出し接続句のASR不一致 | PN A2旧版で2件 | 旧`generate_narrator_heading_with_a2_slowdown`がstandard/fallbackの独立予算を持たず、承認済みfree_address経路と不整合。是正済み | `CURRENT_SPEC.md:684`付近(新規topic行追記) |
| F12 | 語数・尺の超過 | soft target超過(3V 497語/395秒) | Trial-02〜03 | Tensionが主因(132語)。是正再生成は語数目標を再強化しない設計 | `...TRIAL-07..._REPORT.md` §0,`...PERSON-VOICE-TRIAL-02/03` |

### 8-2. 後期にユーザーが承認した改善策

| 日付 | 承認内容(原文要旨) | 効果の実測 | 出典 |
|---|---|---|---|
| 2026-09-08 | 一人称"I"・Voice割当・Tension slot・Key Phrase位置 | Trial-06以降 narrator_analysis系FAILが消失 | `DECISION_LOG_HISTORY.md:7388-` |
| 2026-09-09 | 4V→3V、Voice=具体的人物、Fairness/LegalはTension統合 | 3V Trial-02で2 attemptsで0件 | `DECISION_LOG_HISTORY.md:8530-8552` |
| 2026-09-12 | 体験claimの根拠付け(DECIDED)、外部制約統合は任意パターン | — | `CURRENT_SPEC.md:692,694` |
| 2026-09-13 | Voice内「数字必須」の撤廃(2-D)、3V Fact Safety保守版ゲート既定ON(「追加Trialは不要、次の実記事で自然発火したらruntime evidence取得」原文要旨) | 実生成1本ではゲート未発火でGate1は`USER_DECISION_REQUIRED`のまま、Stage1は実データで0件適用 | `CURRENT_SPEC.md:690,695` |
| 2026-09-17 | 候補A/C/E/F(Voiceは経験・立場に徹する/数字は本人経験のみ/迷いは許容、相手の中心論点は抱え込まない/相手の懸念はTension)、`leak_position_blur`新設、Acceptance Gate。候補B(Evidenceレイヤー新設)・D(1 Voice=1 Primary Position恒久化)は不採用 | PN A2新版 attempt1でLeakage 0件・14 segment OK・331秒・¥73.94。offline再評価で誤検知0 | `CURRENT_SPEC.md:693`、`RESULT_PACKET_VOICES_SPEC_01.md` |

### 8-3. 残存する構造的リスク(誰が指摘したか)と、Y指示§6(1)〜(6)への対応

| Y§6 | 旧Bの原因 | 承認済み対策 | 残存リスク(指摘者) |
|---|---|---|---|
| (1) Voiceが解説者化 | F1/F2/F3/F4:Evidence主役、三人称、抽象軸Voice、数字命令とEvidence主語禁止の二律背反 | 一人称"I"(09-08)、Voice Card起点、Evidence脇役、候補C(本人経験の数値のみ・最大1つ)、`leak_evidence_subject`他、具体的人物Voice(3V) | Leakage再発(PN A2旧版)。theme側evidenceが集計統計のみの粒度問題(Opus L3(B)、テーマ設計の恒久策として提案のみ)。Voice Cardが人手作成で品質がCard次第(内部所見、Opus §0-B) |
| (2) 3 Voicesの立場・論点が重複 | 4Vで特に問題。語彙overlapでは推論構造の同一性を測れない | Voice Card/Diversity Checkの人手判定、`leak_binary_camp_split`(Tension)、overlap monitoring(非gate) | Pairwise Distinctnessは Trial限定で未採用。意味レベル重複の承認済みgateなし(Opus HIGH) |
| (3) 他Voiceの中心主張を取り込む | F7:PN A2新版、AI hiring Owner Voice | A/E/F、`leak_position_blur` | **OPEN-167未決**(nuance境界。ユーザー提案例の許容/不許容の線引き)。Validatorのnuance許容はユーザー知覚より緩い(DECISION_LOG:8235) |
| (4) VoiceとTension+Closingの論点重複 | Closing4/4同型、Closingがdata・要約へ戻る危険 | Tensionは「再掲・時系列反復をしない」「Evidence主語禁止」「公平に相手懸念を受ける」、Closingは「要約でなく再定義」 | **overlap monitoringにTension/Closing対Voiceの比較が含まれない**(`:888-915`はVoice対Voice+Voice対Hookのみ)。Tension対Voiceの重複は記事内で機械検知されていない(本調査での確認事実)。Closing同型化は記事間QA欠如(Opus L3) |
| (5) 体験談内の事実創作 | 「自分の評判が確定的に破壊される」等の無根拠な断定。Voice内の個人体験をFact Checkerが事実主張として拾う | 体験claim根拠付け原則(DECIDED)、Fact Checker A'+Ledger Deviation+Local Rewrite、保守版ゲート | Fact Checker REVIEW_REQUIREDが慢性的(PN A2新版でもnon-blocking)。保守版ゲートの効果は実発火で未確認。`_VOICE_GATE_INSTITUTIONS`はテーマ依存ハードコード。Tension非対称性文のLedger衝突(F5)が構造的に残る(Sonnet/Opus所見) |
| (6) 検査・書き直しでも構造起因NGが解消しない | F4/F5:同型修正の反復で収束せず(whack-a-mole、hedge増量で収束せず) | Acceptance Gate(LEAKAGE_RESIDUAL_STOP: 残存flag記事を後続へ流さない)、2-D/候補C(二律背反の除去) | Gateは「流出防止」であり原因解消ではない。retry方式(全文書き直し)の見直し案(局所書き換え、severity階層)は**提案のみで未採用**(Opus L3 (C)(D))。次テーマ1本での再現性判別が未実施 |

---

## 9. 旧Bの費用・尺・retry実績(出典付き。無ければ「未確認」)

| 項目 | 値 | 出典 |
|---|---|---|
| 2V新規topic Voices 1生成セット総原価(TTS未実行) | ¥99.01(Research/Ledger ¥46.98+Writer/QA/Gate/retry ¥52.03) | `CURRENT_SPEC.md:691` |
| 3V Writer 1 attemptあたり | ¥24.3〜28.3(最良ケース1 attempt確定 ¥25.5、3 attempt上限 約¥78) | `...PRODUCTION-WIRING-PHASE1B-04_REPORT.md` §5,§9-5 |
| 3V Regression 1回 | ¥110.1(NG破棄run¥32.1+採用run ¥78.0。Trial特有の上振れ ¥84.7) | 同 §5 |
| 3V Person-Voice Trial-02/03 | ¥20.57 / ¥19.49 | `...TRIAL-02/03_REPORT.md` |
| 4V Trial-02 Ledger Deviation Web検索 | 27回・¥76.6 | `DECISION_LOG_HISTORY.md:8554-8556` |
| PN A2新版(Ledger再利用、attempt1確定、14 segment TTS) | ¥73.94(duration 331.2秒) | `RESULT_PACKET_VOICES_SPEC_01.md` §6,§11 |
| PN B1再生成試行(Fact Checker FAIL停止) | ¥12.32 | 同 |
| 旧Bの量産単価 | 70円/セット目標に対し「過去測定は約99〜840円とばらつき、70円超の可能性」(Family横断の記述でVoices単独の確定値ではない) | `OPEN_ITEMS.md` OPEN-366 |
| 3V実測尺 | 356.6秒(2V 305.1秒比+17%)、Trial-02 497語の推定395秒、PN 2V A2 331.2秒 | 各Report |
| 生成回数・retry率 | Trial数本の観測のみ: 3V Trial-01=3 attempts(NG)、Trial-02=2、汎用化Regression=3(非収束)、PN A2新版=1、PN B1=2+Fact Checker FAIL停止。**統計的な再試行率・Human Review率は未確認**(Voices専用の集計なし。N≈10記事程度で意味のある率にならない) | 各Report |
| HR(Human Review Lock)率 | 3V音声Trial 16 segment全OK・Lock発動なし、PN A2新版14 segment全OK。PN A2旧版でNarrator見出し2件がLock(是正済み)。母集団の率は**未確認** | `3V-AUDIO-TRIAL-01-CLOSEOUT`、`RESULT_PACKET_VOICES_SPEC_01.md` §6 |

**費用増加要因(設計時の注意)**: (i)Fact Checker A'のWeb検索+Ledger Deviation Check(1 attemptごとに全実行)、(ii)Leakage flaggedによる全文書き直し×3、(iii)Voice Cardの人手作成工数(API費用外)、(iv)3 Voices化による本文・TTS・尺の増加(+約17%)、(v)Ledger鮮度問題による再Research。

---

## 10. 旧B固有の複雑な仕組みで、Yに不要と考えられるもの(C分類候補)

| # | 仕組み | 理由 | 所在 |
|---|---|---|---|
| C1 | 2V/4V/可変Voice数対応(`make_theme_config`の2/3可変、2V専用pipeline、4V構造案) | Yは3V固定(ユーザー決定) | `writer_generic_01.py:121-,721-,1788-,1960-` |
| C2 | 2V/3Vで別テンプレート・別Leakage schema・別pipeline(`run_pipeline_2v/3v`等の重複) | 重複が不整合の温床(F10)。Yは単一定義でよい | 同 |
| C3 | 独立Closing section・`leak_closing_simple_summary`・Closing語数配分・Comment 4(Tension後・Closing前)の位置 | ユーザー決定(Closing廃止) | `:335-341`,`:975`,`registry.py:128-` |
| C4 | `voice_fact_safety_gate_mode`(段階1/2、テーマ依存の`_VOICE_GATE_INSTITUTIONS`辞書) | Stage1は実データで効果0、辞書はテーマ依存ハードコード、runtime evidence未取得。Y側はX/Zの最新Fact Safety(A)を基盤にする | `:1352-1500` |
| C5 | Fact Attribution A'(`fact_attribution_mode`、`[VOICE_n_EVIDENCE]`の出典免除rule) | 候補C(Voiceに外部統計を語らせない)と設計思想が逆。YはC方針を採る前提(判断はFable) | `registry.py:373,399-460` |
| C6 | `leak_tension_constraint_integration`/外部制約統合の4段目(任意パターン) | 「恒久ルール化しない任意パターン」と決定済み。Yでは必須でない。必要ならテーマ側の任意適用 | `:397-427` |
| C7 | 語彙overlap monitoring(0.40閾値前提、Voice対Voice+Hook) | 語彙指標では「推論構造の同一性」を測れない。monitoringのみでgateでない | `:888-950` |
| C8 | Pairwise Voice Distinctness Check(Trial) | Trial限定・UDRのまま。Charter上、新Validatorの目的化を避ける(採用するならD) | Trialスクリプト |
| C9 | B-Family専用の入口群(`main_b1_2v/main_b1_3v/main_a2_2v`)、B専用registry・Voice割当、B_FAMILY_A2 Gate level、`tension_reflection`/`in_one_line`の名残命名 | Yは旧B経路の改修・転用でなく、X基盤へ新設(ユーザー決定) | `er012_b_family_*` |
| C10 | Evidence Compression Editor(Production既存機構のVoices適用) | Trial-05で分析文挿入・実名匿名化の副作用。Trial-06では無害だったがn=1(`...TRIAL-06..._REPORT.md` §0) | Production共有機構(A/Xの現行仕様に従う) |
| C11 | MAX_WRITER_ATTEMPTS=3の「全文再生成」型retry方式そのもの | whack-a-mole、費用上振れ(Opus L3)。ただし3回上限は安全装置でありYで独自に外さない。局所書き換え化はD | `:67`,`:1885-` |
| C12 | PN B1/AI hiring等のテーマ固有の `er012_b_family_voices_theme_*.py`・Ledger | 旧テーマ固有資産。Yは新テーマ(ユーザー選定)で設計 | 同 |

---

## 11. D候補(Y固有の新設計・ユーザー判断になりうる論点)の整理(本調査の範囲での列挙のみ)

各項目はFable/ユーザー判断前の整理であり、案Aの正式採用ではない。

1. **Tension+Closing統合の中身**: 「共通前提→分岐点→非対称性」の後に「問題の見え方の再定義」を何文入れるか/入れないか、語数・尺の再配分。Closingの同型化(F8)を避けつつ「自然に締める」方法。
2. **Comment 4の廃止・移動**: Comment 4は「結びのまとめ」前の橋渡し。Tension+Closing統合でその位置が消える。Comment 3のみにするか、Xの最新Comment構造に合わせるか。
3. **Voice Card(人物設計)の作成方式**: 人手作成(旧B)のままか、X基盤の「Storyline決定+B3 Fact選定」でVoiceごとにAngle/fact_idを割当てる方式(Y Trial-01で前段のみ実測済み)か。量産(Y 3記事)の工数・費用に直結。
4. **nuance許容範囲(OPEN-167の7論点)**: 相手側懸念をVoiceに言わせない度合い。Y指示は「他Voiceが担う反論まで無理に抱え込まない」だが、境界の厳密さは未決。
5. **Fact Safetyの構造衝突(F5)への対処**: Tension非対称性文をどう書くか(hedge増量では収束しない)。X/Zの最新Fact Safetyと旧Bのどちらの流儀に寄せるか。
6. **R1→R2 Revision等のX機能をVoice文脈でどう扱うか**: Y Trial-01で旧Leakageが悪化(OPEN-217)。評価はrubric単独でなく決定論的チェック併用(OPEN-218)。
7. **TTS/声・Gate構造**: 3 Voice用のVoice割当をXの最新方針に合わせる、Assembly/Gateの`required_structure`をY用に新設(旧B_FAMILY_*の命名は不継承)。
8. **レベル**: 旧Bは3VがB1のみProduction構造対応。YでX基盤(Standard/Advanced等)のどのレベルを対象とするか(委任01Aの領域のため、ここでは事実のみ)。

---

## 12. 未確認事項(出典のない主張を避けるための一覧)

- Trial-06基準(主要な意見から順に、同じStakeholder群内の違い)の恒久規則化の有無(CURRENT_SPEC恒久欄では見当たらない。DECISION_LOG上の正式採用日は未確認)。
- 旧Bのユーザー原文逐語(「Voice=具体的人物」の原文引用)は`DECISION_LOG_HISTORY.md:8530-8552`の要約のみ参照。`docs/pm/delegation_log/`個別ファイルの逐語は未読。
- Voices専用の再試行率・HR率・量産単価の確定値(母数不足)。
- 一人称の機械保証(pov_check)が常設Gateか否か。
- 3V保守版Fact Safetyゲートのruntime evidence(Production実発火)取得状況の最新(2026-09-14以降)。
- TTSの声割当(Algieba等)がX/Zの最新方針と一致するか(01Aの範囲)。
- `B_FAMILY_A2`の`in_one_line`必須segmentがClosingを指すこと自体は`a2_production_01.py:793,883`から確認したが、Gate辞書の命名意図の一次資料は未確認。
- Perspective選定を既存Exception Search拡張で行う提案(DESIGN-02 §9)の実装有無は、本調査ではProductionコードに該当実装を発見せず(未実装と推定、確認はGrepのみ)。
- ER-*_REPORTのうち本調査で読んでいないもの: `...TRIAL-04_REPORT.md`(約99KB)、`...PRODUCTION-WIRING-PHASE1-01_REPORT.md`(約73KB)、`...PHASE1B-04_REPORT.md`の全文(§5,§9のみ)、COMMENT1系Report全文。

---

## 13. 主要出典一覧(本調査で実読)

- 仕様: `CURRENT_SPEC.md:667-708`(B-Family(Voices)節)、`:1472-1479`,`:1640-1652`,`:2797`
- 決定: `DECISION_LOG.md:8111-8260`(2026-09-17)、`DECISION_LOG_HISTORY.md:7388-7460`,`:8503-8560`
- OPEN: `OPEN_ITEMS.md` OPEN-120,129,131,132,151,166,167,217,218,219,366
- コード: `er012_b_family_voices_writer_generic_01.py`(`:56-160`,`:159-448`,`:888-1130`,`:1691-1790`,`:1876-1953`)、`er012_b_family_editorial_type_registry_01.py`(`:40-200`,`:373-520`,`:524-640`)、`er012_b_family_voices_theme_ai_screening_01.py`、`...theme_personalized_news_a2_01.py`
- Report: `EDITORIAL-B-FAMILY-VOICES-DESIGN-02`,`TRIAL-03`,`-05`,`-06`,`-07`,`-09-AUDIO-STRUCTURE-REFINEMENT`,`4V-ARTICLE-TRIAL-02`,`3V-PERSON-VOICE-TRIAL-01/02/03`,`3V-4V-WRITER-DESIGN-OPUS-REVIEW-01`,`3V-PHASE1B-04-OPUS-L3-DIAGNOSIS-01`,`FACT-SAFETY-STRENGTH-DESIGN-01`,`FACT-SAFETY-RELAXATION-TRIAL-01`,`MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-02`,`3V-AUDIO-TRIAL-01-CLOSEOUT`、`FAMILY-Y-VOICE-STRUCTURE-TRIAL-01`、`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02`(参照のみ)
- 設計: `er012_output/editorial_b_voices_phase1_5_3v_4v_integrated_trial_03/design.md`
- 運用: `docs/pm/RESULT_PACKET_VOICES_SPEC_REVIEW_01.md`,`docs/pm/RESULT_PACKET_VOICES_SPEC_01.md`
