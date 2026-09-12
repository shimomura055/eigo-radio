# DECISION_LOG — 確定した意思決定の索引

**管理ID: ER-PM-001**
**最終更新: 2026-09-09(PM-CLOSEOUT-CONSOLIDATION-55、News段階2Ledger v5是正のSSOT反映)**: 管理ID`PM-CLOSEOUT-CONSOLIDATION-55`(Sonnet委任、SSOT・Git担当、並列稼働中タスクなし)により、2件のTrial結果をSSOTへ反映した。**(1) News段階2(N-1/N-2)結果**: `FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08_REPORT.md`のPart A(N-1、実測¥42.5、N=6/条件、value単独NG時のoverlap診断section条件分岐案)はNG率50%→83.3%・平均attempt数1.50→1.83と悪化方向、value単独NG→次attempt新規lexical flag率は条件分岐後も5/5(100%)で連鎖が解消せず、新規Fact Checker FAIL 1件も発生したため**Gate 1分類=REJECTED**(N=6小標本のため断定はしないが、当該Production修正案は採用非推奨)。Part B(N-2、¥0、既存240件のoverlap分布再集計)は、閾値0.40が観測分布の57.9パーセンタイルに位置し境界帯(±1語)内が60/240(25%)であること、固定分母案は現行より厳しい方向(flag率+5〜6pt)へ動き長いPointに不利な逆方向の交絡を生むこと、Focus系施策の改善効果自体は境界効果依存度10〜28%に留まることを確認し、**閾値・分母の緊急再校正を数値は強く支持しない**と結論した(採用はいずれもユーザー判断、UDR)。News再改善の残る手段はN-3(Role再計画への診断結果受け渡し、保留中)とN-4(Hanshin題材依存の切り分け、別News Ledger、本Reportで新規提示・次の判断待ち)。**(2) Household Ledger v5是正**: `HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03_REPORT.md`により、v4のFACT-03(低湿度ドロワー適合例)に残っていたバナナ・トマトの列挙がFACT-04(トマト・バナナは常温保存推奨)と直接矛盾していた新規課題を是正した(バナナ・トマトを削除しりんご・洋梨のみへ絞り込み、FACT-04参照注記追加、FACT-04は無変更、既存Production同一Fact Checkerでrun2=PASS・contradictions=[]、合計¥3.31)。Discovery段階2 Trial-08の8本中4本にFACT-03/04矛盾を含む本文が確認されたが再生成は行っていない(今後のDiscovery段階2再実行はv5使用)。Household FACT-03最小修正(revision3a)はv5と矛盾しないことを確認済み。**(3) 反映範囲**: `OPEN_ITEMS.md`(OPEN-135行[News段階2結果]・OPEN-133行[分母正規化案非推奨]・OPEN-134行[閾値±1語内25%観測]・OPEN-138行[Ledger v5、Trial-08の4本に矛盾文、revision3a整合]反映)・`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`へ反映した。Production/Prompt編集・新規Trial着手はいずれも実施していない。詳細は`OPEN-135`行・`OPEN-133`行・`OPEN-134`行・`OPEN-138`行、`FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08_REPORT.md`、`HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03_REPORT.md`参照。

**履歴全文(直前の記録・その前の記録、以下さらに前の記録、合計12件、原文のまま移動): `DECISION_LOG_HISTORY.md`の`## ER-PM-001_CHAIN`節参照**
**区分について(2026-08-17追記)**: 以下のDecisionは「サービス・生成仕様」
(番組の聞こえ方・記事の作られ方そのものに関わるもの)と「Implementation
Hardening」(実装の堅牢化。サービス仕様は変えず、コードの安全性・
再発防止のみを目的とするもの)を区別して記載する。各エントリの見出しに
区分を明記する。

確定した意思決定と、その理由・根拠を記録する。個別のDecision Record原本
(`er003_output/p2i/ER-003-P2I_decision_record.md`等)は削除せず、本ファイルは
それらへの**索引**として機能する。未決事項は書かない(→[OPEN_ITEMS.md](OPEN_ITEMS.md))。

各Decisionは最低限、Decision ID／日付／内容／状態／採用理由／比較した
選択肢／却下理由／根拠レポート／commit／影響するCURRENT_SPEC項目を持つ。

---

## 索引(Index): 全Decisionエントリ一覧

> 以下は全231件の決定エントリを原文タイトル(見出し行、原文のまま)で列挙した索引である。要約は行っていない。「本ファイル内」は本体に残る直近25件、「履歴」は`DECISION_LOG_HISTORY.md`へ原文のまま移動した件を指す。管理IDでのGrepはどちらのファイルにあっても直接ヒットする。

- [履歴] ## PM-GOVERNANCE-AUDIO-ARTIFACT-GATE7-CHECKLIST-10: 試聴artifact規則の主語明確化とGate 7受入チェックリスト追加
- [履歴] ## PM-GOVERNANCE-AUDIO-REVIEW-PAGE-STANDARD-09: 試聴依頼ページは音声+完全スクリプト同一表示を標準化
- [履歴] ## EDITORIAL-B-FAMILY-VOICES-SERIES-02-05: Lane B Voices/Perspective設計〜Trial-05の記録
- [履歴] ## PM-FABLE-SONNET-REVIEW-LOOP-03: Fable↔Sonnetレビュー往復上限を2回→3回へ変更、FableのGatekeeper原則を明文化
- [履歴] ## ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01: TTS実行モード切替(環境変数)をdrop-in factory1箇所へProduction配線
- [履歴] ## PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: TTS方式の運用基準を「正式リリース前=Standard同期/正式リリース後の実量産=Batch API」へ統一
- [履歴] ## OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-01: Key Phrase日本語訳の表示用/TTS用分離方式のPhase 1隔離Trial(Production変更なし)
- [履歴] ## OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02: Key Phrase表示用/TTS用分離方式のPhase 2(Theme 2 A2/B1、Production正式経路+Trialアダプタ、Production変更なし)
- [履歴] ## OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01: Key Phrase日本語gloss「～」placeholderゲートの再評価(Trial-only TTS確認、Production変更なし)
- [履歴] ## OPEN-112-TREND-THEME2-SERIES-11-17: Theme 2(若者の旅行)Trend Synthesis Trial系列(Trial-11〜17・Opus診断-14/-15)の記録
- [履歴] ## PM-GOVERNANCE-LOCAL-FILE-LINK-RULE-07: 試聴・閲覧依頼はfile:// URL形式で提示するルールを9-2へ追加
- [履歴] ## PM-GOVERNANCE-ADAPTIVE-REPORTING-06: ユーザー向け報告を固定5構造から候補セクション制(adaptive reporting)へ改訂
- [履歴] ## PM-GOVERNANCE-REPORT-FORMAT-AND-AUTONOMOUS-GIT-05: ユーザー向け報告フォーマットの改訂(5構造・番号対応)とcommit/push自律実行運用をPM_GOVERNANCEへ反映
- [履歴] ## PM-GOVERNANCE-AGENT-WAIT-AND-DUPLICATE-LAUNCH-RULE-04: 待機中Agentの再開リスクと同一管理IDへの多重起動禁止をPM_GOVERNANCE 8節へ追記
- [履歴] ## PM-GOVERNANCE-USER-FACING-EXPLANATION-STYLE-03: ユーザー向け説明スタイル原則をPM_GOVERNANCEへ明文化
- [履歴] ## PM-GOVERNANCE-PARALLEL-AGENT-POLICY-02: Agent並列起動の原則をPM_GOVERNANCEへ明文化(ユーザー決定(b))
- [履歴] ## PM-GOVERNANCE-TTS-MODE-CONFIRMATION-01: TTS方式(Batch/Standard)の明示・確認原則をPM_GOVERNANCEへ明文化
- [履歴] ## PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01: ChatGPT旧PM引き継ぎHandoffの正式closeout・PM運用原則4点のSSOT明文化
- [履歴] ## OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10: Entertainment根底指示+Reference DigestのA/B比較Trial(イラン/ホルムズ海峡)
- [履歴] ## OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09: Trend Synthesis最小限Focus Module Promptの実記事Trial(イラン/ホルムズ海峡)
- [履歴] ## OPEN-112-NEWS-MODE-DESIGN-08: News系(A Family) Major/Daily News・Trend Synthesis 4層構造設計
- [履歴] ## OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-REGISTER-07: OPEN-114正式登録・Discovery 4層仕様のProduction Adoption Readiness整理
- [履歴] ## OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-AND-NO18-B1-REGEN-04: Point-context-only方式のProduction配線・No.18 B1再生成
- [履歴] ## ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-FINAL-26: caller指定max_attempts(6・10等)の例外を撤廃し、対象Production経路を例外なくTOTAL3回へ統一・実TTS/実ASR runtime evidence取得
- [履歴] ## ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25: TTS標準経路2回+Minimal instruction fallback1回(合計3回)の内訳をProduction正式仕様として配線
- [履歴] ## ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23: A2 tight_speech_only() removal・Key Phrase trim 0.30秒を量産Production仕様として正式配線
- [履歴] ## ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R: Pattern A + Precision正式Production配線、No.18 A2/B1最終候補音声完成
- [履歴] ## ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-PRECISION-EXTENSION-TRIAL-20: Pattern A/B/Cへの共通Precisionルール追加Trial(各3回×3パターン=9 run、Production未採用)
- [履歴] ## ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-REPRODUCIBILITY-TRIAL-19: Evidence Compression拡張ルールA/B/C 再現性Trial(各5回×4パターン=20 run、Production未採用)
- [履歴] ## ER-011-NO18-A2-EVIDENCE-COMPRESSION-EXTENSION-ABC-TRIAL-18: Evidence Compression拡張ルールA/B/C比較Trial(Baseline対照込み、Production未採用)
- [履歴] ## ER-011-EVIDENCE-COMPRESSION-HISTORY-AND-FAILURE-AUDIT-17: Evidence Compression/Numeric Compressionの導入経緯・過去Trial・不具合の一次資料監査(履歴監査のみ、実装なし)
- [履歴] ## ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08: OPEN-107撤回、B1 Connected Speech Validator・A2 Reading ResolverのProduction配線、No.18 A2/B1完成
- [履歴] ## ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07: B1 Connected Speech Validator Trial・A2 OPEN-111向け辞書候補+LLM選択Reading Resolver Trial
- [履歴] ## ER-011-NO18-B1-LISTENING-AND-A2-OPEN111-READING-TRIAL-06: B1 comment系のUser Listening Artifact提示・A2 OPEN-111向け代替Reading方式Trial
- [履歴] ## ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04: OPEN-107検出/配線範囲の是正・A2のLedger精密化正式反映・B1/A2 comment系の新規TTS失敗モード診断
- [履歴] ## ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03: OPEN-107(Ending-Clarity fallback)をB1 Production正式経路へ配線、No.18 B1本文の個別差し替え・Audio Stage実行
- [履歴] ## ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02: OPEN-108(No.18 B1 Fact Checker FAIL)をVerified Fact Ledgerのsource-grounded精密化で解消、OPEN-107(opened誤発音)のEnding-Clarity fallback候補を隔離Trial
- [履歴] ## ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: No.18で発見された3件の問題を汎用Production仕様として改善(Key Phrase人称一般化・Key Phrase Set Redundancy QA・Point Role Planning+Point Value QA)、No.18を改善後仕様で再生成、OPEN-107 Diagnostic Trial実施
- [履歴] ## ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01: No.18「Why Is It So Hard to Ignore a Notification?」Discovery/Why型 正式Production実行(A2完成/B1新規TTS失敗モードでSTOP)
- [履歴] ## ER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28: No.9 A2/B1最終承認記録とNo.9開発全体の完全棚卸し・Closeout(FINAL USER APPROVED / CLOSED)
- [履歴] ## ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1: function-word/article reductionのProduction正式配線とNo.9 A2最終Re-Assembly(PRODUCTION_WIRED、USER_FINAL_AUDIO_REVIEW_REQUIRED)
- [履歴] ## ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26: Key Phrase「a catch」冠詞強調の診断とfunction-word reduction隔離Trial(USER_DECISION_REQUIRED)
- [履歴] ## ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25: Trial 21 Attempt 4をNo.9 A2 `default`のone-off固定assetとして採用・A2完成
- [履歴] ## ER-010-NO9-A2-DEFAULT-FIXED-ASSET-FINALIZATION-23-R1: `default`個別対応、既存固定音声資産の探索
- [履歴] ## ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22: Key Phrase英語Component retry構成をMinimal→English Lockへ正式Production配線
- [履歴] ## ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21: Key Phrase「default」のEnglish language lock fallback Trial(Minimal最大2→English Lock最大2)
- [履歴] ## ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINI-TRIAL-20-R2: No.9 A2正式Key Phrase5件のMinimal instruction Mini-Trial(bounded retry)
- [履歴] ## ER-010-NO9-A2-KEYPHRASE-AUDIO-ISSUES-103-104-17: OPEN-103/OPEN-104個別診断・OPEN-104実装バグ修正
- [履歴] ## ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19: Key Phrase Minimal Instruction Trial(OPEN-103)・review lockネスト二重会計バグ修正(OPEN-105)
- [履歴] ## ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18: No.9 B1音声のUser Approval・完成音声提示ルール再確認・OPEN-103 TTS payload監査
- [履歴] ## ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04: 仕様Lifecycle・Dangling Reference Checkの正式導入
- [履歴] ## ER-003-B1-P7A: Preview TTSモデルをgemini-3.1-flash-tts-previewへ
- [履歴] ## ER-003-B1-P5A〜P5C: Google Cloud TTS(Neural2-B)を不採用
- [履歴] ## ER-003-P2I: Key Phrase選定方式にStrategy L(Listening Blocker Ranking)を採用
- [履歴] ## ER-003-REPRO-01-KP: B1本文からKey Phraseを新規選定する方針へ訂正
- [履歴] ## ER-003-KP-01: Pedagogical Phrase Canonicalizationの導入
- [履歴] ## ER-003-KP-02: Canonicalization原則を「最小」から「最小十分」へ
- [履歴] ## ER-003-KP-02-R1: Meaning Preservation Ruleの追加とTraceability再定義
- [履歴] ## used_form / key_phrase の重複を技術的負債として記録し整理しない
- [履歴] ## strict ASR検証(部分一致+文字数上限)の追加
- [履歴] ## minimal instruction fallbackを英語Key Phrase Componentへも一般化
- [履歴] ## Dynamics3を不使用、scalar RMS gainのみ採用
- [履歴] ## 複数箇所編集は「後ろから前へ」の順序を徹底
- [履歴] ## MFA単独では数字・日付境界を確定しない
- [履歴] ## ASR homophone ambiguityをhallucinationと区別し、2段階human reviewフローで扱う
- [履歴] ## A02・ADD03の量産再現性判定: 量産候補として採用可能
- [履歴] ## ER-002実験(A01・A02の初回音声)を破棄し、ER-003アーキテクチャへ全面移行
- [履歴] ## ER-003-A2-STRUCT-02: A2超一般語5語制限を不採用
- [履歴] ## ER-003-A2-STRUCT-02: 抽象語→具体的行動表現への一律変換を不採用
- [履歴] ## ER-003-A2-STRUCT-02: 固有名詞密度低減を不採用
- [履歴] ## ER-003-A2-STRUCT-02: Spoken-firstをA2の継続仕様として採用
- [履歴] ## ER-003-A2-STRUCT-02: 1文1数字ルールを維持、日付は1つの数字情報として扱う方向で整理
- [履歴] ## ER-003-A2-SPEC-FREEZE-01: A2言語・構造仕様をPROTOTYPEからDECIDEDへ昇格
- [履歴] ## ER-003-A2-SPEC-FREEZE-01: A2英語ナレーション速度を約135 WPM目安として採用
- [履歴] ## Cross-level: Preview原則をA2/B1/B2共通仕様として採用
- [履歴] ## Cross-level: Key Phrase発音品質の3条件をA2/B1/B2共通仕様として採用
- [履歴] ## Cross-level: 英語見出しは見出しテキストを実際にTTS inputへ含める方式を採用
- [履歴] ## Cross-level: Pause値(0.7秒/0.8秒)をA2/B1/B2共通仕様として採用
- [履歴] ## Cross-level: Outro音量の心理音響ベース減衰方針を採用
- [履歴] ## A01 script修正: "The referee then added more time." → "The game went into added time."
- [履歴] ## A01 script修正: "Rogers sent the ball across the front of goal." → "Rogers crossed the ball into the box."
- [履歴] ## A01 script修正: "Messi sent the ball across goal from the right." → "Messi crossed the ball from the right."
- [履歴] ## A02 script修正: "apps under the plan would not open at first" → "apps under the plan would be switched off by default"
- [履歴] ## ADD03 script修正: Brent原油価格段落の時系列flashback構造を解消
- [履歴] ## ER-003-SPOKEN-FIRST-03: Point Balance(Point One/TwoはA02で40〜50語が機能。全ジャンル一律ルール化はしない)
- [履歴] ## [サービス・生成仕様] ER-003-B1-NOVEL-AUDIO-01系: B1をSupport-based Natural Englishへ再設計
- [履歴] ## [サービス・生成仕様] ER-003-A2-B1-N3-01: B1-B Direct Generationを採用し、B2の別段階生成を廃止
- [履歴] ## [サービス・生成仕様] B1 Key Phraseの提示順序をEnglish→Japanese→Englishに確定(英英説明は不採用)
- [履歴] ## [サービス・生成仕様] ER-003-POINT-NOTIFICATION-01: Point One/Two専用Notificationと無言のPoint番号ラベル
- [履歴] ## [サービス・生成仕様] Point semantic headingは記事生成プロンプトの`###`見出しをそのまま使う
- [履歴] ## [サービス・生成仕様] ER-003-A2-B1-N3-01: Point Balanceの目標範囲(30-60語/許容25-70語)を3ジャンルで検証、hard capへは昇格させない
- [履歴] ## [サービス・生成仕様] ER-003-A2-B1-N3-01: Spoken-first Number TreatmentをA2/B1共通仕様として正式化
- [履歴] ## [サービス・生成仕様] ER-003-A2-B1-N3-01: Fact Safety(Verified Fact Ledger→Fact Checker→Ledger Deviation Check)をA2/B1共通標準として正式化
- [履歴] ## [サービス・生成仕様] ER-003-A2-B1-N3-01: 3ジャンル(Sports/Health/Household)横展開によるジャンル再現性の確認
- [履歴] ## [サービス・生成仕様] ER-003-N3-ROOT-FIX-01 / VERIFY-01: A2 Core Explanatory Logic Preservationを正式仕様へ採用
- [履歴] ## [Implementation Hardening] ER-003-N3-ROOT-FIX-01: English Key Phrase trim safety marginを0.20秒へ拡大(Key Phrase専用)
- [履歴] ## [Implementation Hardening] ER-011-NO18-KEYPHRASE-TRIM-030-PRODUCTION-WIRING-12: English Key Phrase trim safety marginを0.30秒へ再拡大(0.20→0.30、A2/B1共通)
- [履歴] ## [Implementation Hardening] ER-003-N3-ROOT-FIX-01: TTS style instructionの責務分離+短いJapanese phraseへのminimal instruction fallback
- [履歴] ## [サービス・生成仕様] ER-003-B1-B2-SCOPE-FIX-01 Decision A: B1はB2共通本文ではなく、LedgerからB1用英文を独立生成する
- [履歴] ## [サービス・Scope仕様] ER-003-B1-B2-SCOPE-FIX-01 Decision B: Initial Launch levelはA2/B1の2つとする
- [履歴] ## [Implementation Hardening] ER-005-AUDIO-INSTRUCTION-SEPARATION-01: TTS style instructionとspoken textのStructured Separationを正式採用
- [履歴] ## [Implementation Hardening] ER-005-JA-SHORT-ASR-PHONETIC-01: 短い日本語segmentの発音ベースASR Validationを正式採用
- [履歴] ## [Implementation Hardening] ER-006-MODEL-ROUTING-CONTRACT-01: Production Model RoutingをLunaへ統一・Fail-Closed契約化
- [履歴] ## [Implementation Hardening] ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Audio ValidationのProduction配線・ASR一致と発音品質の分離・Luna品質確認
- [履歴] ## ER-006-AUDIO-COST-PILOT-02(2026-08-22)
- [履歴] ## ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(2026-08-22)
- [履歴] ## ER-006-AUDIO-COST-SPEC-FIX-01(2026-08-22)
- [履歴] ## ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(2026-08-22)
- [履歴] ## ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01(2026-08-22)
- [履歴] ## ER-006-POOL-ADOPTION-AUDIT-01 / ER-006-POOL-N4-N6-PRODUCTION-01 / ER-006-PRODUCTION-THROUGHPUT-GATE-01(2026-08-23)
- [履歴] ## ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01(2026-08-24)
- [履歴] ## ER-006-RESEARCH-COVERAGE-GATE-DEFER-01(2026-08-24)
- [履歴] ## ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part B(2026-08-24)
- [履歴] ## ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(2026-08-25)
- [履歴] ## ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(2026-08-25)
- [履歴] ## A2/B1 Point Structure Semantic Alignment(2026-08-25)
- [履歴] ## ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01(2026-08-25)
- [履歴] ## ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01(2026-08-25)
- [履歴] ## ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01(2026-08-25)
- [履歴] ## ER-008-N7-CONTENT-AUDIO-QA-02(2026-08-26)
- [履歴] ## ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03(2026-08-26)
- [履歴] ## ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04(2026-08-26)
- [履歴] ## ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(2026-08-26)
- [履歴] ## ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06(2026-08-26)
- [履歴] ## ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07(2026-08-26)
- [履歴] ## ER-008-DIRECTIONAL-FACT-PRECHECK-08(2026-08-26)
- [履歴] ## ER-008-A2-SPEED-SAME-TEXT-ABC-09(2026-08-26)
- [履歴] ## ER-008-A2-TIMESTRETCH-ABC-10(2026-08-26)
- [履歴] ## ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11(2026-08-26)
- [履歴] ## ER-009-JA-FOREIGN-TOKEN-GATE-01(2026-08-26)
- [履歴] ## ER-010-ENTITY-PHONETIC-CORROBORATION-01 / ER-010-DATE-SPOKEN-FORM-POINT-FIX-01(2026-08-27)
- [履歴] ## ER-011-HUMAN-REVIEW-COST-GUARD-01(2026-08-27)
- [履歴] ## ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15: TTS retry上限3回化+固有名詞/日本語表記ゆれ/英語homophoneのCascade改修(Implementation Hardening)
- [履歴] ## ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-PRONUNCIATION-SPEC-16(2026-08-28)
- [履歴] ## ER-008-N8-QA-CONTENT-SPEED-HARDENING-18 / ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(2026-08-29、Implementation Hardening)
- [履歴] ## ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20(2026-08-29、Implementation Hardening)
- [履歴] ## ER-008-N8-FINAL-QA-HARDENING-21(2026-08-29、Implementation Hardening + サービス・生成仕様混在)
- [履歴] ## ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22(2026-08-29、No.8最終品質調整)
- [履歴] ## ER-008-N8-FINAL-PRODUCTION-HARDENING-23(2026-08-29、Evidence Compression地名拡張・A2 In One Line速度調査・Point overlap Writer retry実runtime検証・固有名詞発音表示ルール)
- [履歴] ## ER-008-N8-FINAL-CLOSEOUT-24(2026-08-29、地名/施設名CompressionのNo.8正式反映・Writer Point Balance prompt強化・cost計算バグ修正・Stephen Reicher PASS確定)
- [履歴] ## ER-008-N8-CLOSEOUT-GOVERNANCE-25(2026-08-29、Fact Checker retry cap調査・Production全体loop横断監査・No.8 Point overlap記録整理・cost報告円ベース化・試聴Artifact全script掲載標準化)
- [履歴] ## ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02(2026-08-29、Ledger Deviation Checkerの過剰検知是正・Production再配線・No.9再判定)
- [履歴] ## ER-009-N1-AUDIO-STAGE-01(2026-08-30、No.9 Support/Audio生成・Human Review Lock承認確認漏れ修正・全script掲載Artifact公開)
- [履歴] ## ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03(2026-08-30、Key Phrase括弧禁止の本番経路欠落を修正・Topic Pool No.10〜20更新・Writer品質原因切り分けTrial[Production配線なし])
- [履歴] ## ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14(2026-08-31、Diagnostic Full Retry の正式採用と Production WIRED 確定)
- [履歴] ## ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06(2026-08-31、Storytelling First/No JargonのProduction正式実装・Meaning First REJECTED確定・No.9新規再生成候補取得)
- [履歴] ## ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09(2026-08-31、Local Rewrite/Hook-aware Deviation Checker/Evidence-bounded InterpretationのProduction正式配線・No.9実runtime evidence取得)
- [履歴] ## ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10(2026-08-31、Local Rewrite Loop化・No.9新候補でLedger MAJOR=0達成・OPEN-98クローズ)
- [履歴] ## ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11(2026-09-01、Formatting禁止仕様のProduction正式反映・No.9新候補でLedger MAJOR=0達成。**本エントリは前回セッションの実装をSSOTへ事後反映するbackfillであり、次のER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12タスクの一環として追記した**)
- [履歴] ## ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12(2026-09-01、Fact Checker REVIEW_REQUIREDのnon-blocking advisory化・Production実装・No.9 Point解説の数字羅列問題の診断)
- [履歴] ## ER-010-NO9-OPEN100-DEFER-AND-PRODUCTION-AUDIO-13(2026-09-01、OPEN-100のDEFERRED正式記録・OPEN-101音声化前確認・No.9音声生成のSTOP判断)
- [履歴] ## ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14(2026-09-01、OPEN-101 Root Cause特定・article/audio SSOT修復・No.9 A2/B1B正式Production Audio Stage実行・新規Audio QA課題[OPEN-102]発見)
- [履歴] ## ER-010-NO9-AUDIO-VALIDATOR-NORMALIZATION-DIAGNOSTIC-15(2026-09-01、OPEN-102の真のRoot Cause特定[Case C: NORMALIZER_BUG]・前回報告の訂正)
- [履歴] ## ER-010-NO9-TTS-NUMBER-WORDS-BUGFIX-AND-AUDIO-RETRY-16(2026-09-01、`tts_safe_number_words_en()`のRoot Cause修正・Production Audio再実行・No.9 B1完成)
- [履歴] ## OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05(2026-09-04、A Family Writer Promptの4層分離設計・No.18 Article-only Trial、VALIDATED)
- [履歴] ## ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01(2026-09-06、OPEN-115[A2/B1 Assembly最終段ヘッドルーム不在]をユーザーが`APPROVED_FOR_PRODUCTION`と決定・`PRODUCTION_WIRED`まで配線)
- [履歴] ## ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02/03(2026-09-06、OPEN-116の一部をユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と決定した3判断[判断2: JA助数詞リスト縮小版・判断3: EN厳密同音Approach2・判断4: Prompt規約A/B採用/規約C不採用]を`PRODUCTION_WIRED`まで配線)
- [履歴] ## KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01(2026-09-06、ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定した2件[Key Phrase日本語glossの表示用/TTS用分離・数値placeholder型の選定側回避]を`PRODUCTION_WIRED`まで配線)
- [履歴] ## KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01(2026-09-06、ユーザーが2026-09-06に問題2(Key Phrase日本語gloss自然さ、選択肢a)を`APPROVED_FOR_PRODUCTION`と正式決定し`PRODUCTION_WIRED`まで配線)
- [履歴] ## OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01(2026-09-06、ユーザー承認「A/BのProduction wiring完了後、Theme 2のA2/B1完成音声を1回だけ再実行してよい」に基づく実行試行、`USER_DECISION_REQUIRED`で打ち切り)
- [履歴] ## ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01(2026-09-06、ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定した「TTS attemptごとの音声を上書きせず保存し、どのattemptで何が発話されたかを後から確認できるようにする」診断性改善を`PRODUCTION_WIRED`まで配線。あわせてnew normal事象の記録をASR false rejection[分類C]へ訂正、OPEN-119登録)
- [履歴] ## KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01(2026-09-06、ユーザーが2026-09-06に対策(c)[Primary ASRへの逐語書き起こしprompt + 非ラテン文字時のSecondary再判定Cascade]を`APPROVED_FOR_PRODUCTION`と正式決定し、英語Key Phrase Component経路限定で`PRODUCTION_WIRED`まで配線。OPEN-119を`RESOLVED / PRODUCTION_WIRED`へ更新)
- [履歴] ## KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01(2026-09-06、ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定した「gloss生成Promptへ括弧内に別訳・専門用語・補足を併記しない趣旨の短い1句を追加する」対策を`PRODUCTION_WIRED`まで配線)
- [履歴] ## OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-02(2026-09-06、ユーザー承認「A/BのProduction wiring完了後、Theme 2のA2/B1完成音声を1回だけ再実行してよい」に基づく「追加1回のみ」の実行。Trial音声の完成試行のため`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`の格上げは対象外、到達`USER_FINAL_AUDIO_REVIEW_REQUIRED`)
- [履歴] ## OPEN-112-THEME2-AUDIO-REVIEW-FIX-02(2026-09-07、ユーザー試聴で報告された完成音声の重複3件[runtime bug]の診断・ASR検知不全の根本原因特定・既存Production関数のみによる部分修正。新規OPEN-121登録、`USER_DECISION_REQUIRED`)
- [履歴] ## OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01(2026-09-07、
逐語句・文単位反復検知およびpartial-word false start型検知の一般化Trial、
ユーザー承認済み隔離Trial、Production未変更)
- [履歴] ## CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01(2026-09-07、
A2 Point Two「showed strong」を端緒とするConnected Speech Validator一般化
拡張レイヤーTrial、ユーザー承認済み隔離Trial、Production未変更)
- [履歴] ## CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-02(2026-09-07、
追加検証+Trial-01の未分類2件の調査、ユーザー判断による継続Trial、
Production未変更)
- [履歴] ## OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-02(2026-09-07、
false start/aborted restart型の検知方式追加Trialと方式A+Dとの統合仕様
整理、ユーザー判断による継続Trial、Production未変更)
- [履歴] ## OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01(2026-09-07、
ユーザーが2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した範囲[A2/B1英語
本文segmentのProduction正式ASR/Validator経路のみ]でConnected Speech
Equivalence Layerを配線。Git操作は未実施[Lane B Trial-09がcommit権保持中、
Fableが統合commit後に`PRODUCTION_WIRED`確定])
- [履歴] ## OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01(2026-09-07、
ユーザーが2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した範囲[英語ASR
照合経路全体、A2/B1本文に限定しないKey Phrase英語経路を含む共通正規化層]で
標準contraction展開を配線。wanna系(方式iv)は不採用。Git操作は未実施
[Fableが統合commit後に`PRODUCTION_WIRED`確定])
- [履歴] ## OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01(2026-09-07、ユーザーが
2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した範囲[A2/B1英語本文
segmentのProduction正式経路のみ]でTTS反復幻聴検知(方式A+D+D')を配線。
Git操作は未実施[Fableが統合commit後に`PRODUCTION_WIRED`確定])
- [履歴] ## EDITORIAL-B-FAMILY-VOICES-TRIAL-09-LOCK-RETRY-AND-FULL-ASSEMBLY-02(2026-09-07、
ユーザー指示に基づくLane B調査・Gate 7チェックリスト拡張)
- [履歴] ## EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03(2026-09-07、
ユーザー明示決定によるpoint_two_heading再生成1回・1本化Assembly)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-04(2026-09-07、Fableによる独立監査を経た
Lane A 3件[OPEN-121/OPEN-122/OPEN-123]の`PRODUCTION_WIRED`最終受入)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-05(2026-09-08、B-Family Voices試聴決定+
Comment 1 Contract Trial+Numeric Precision監査+試聴player標準フォーマット
統合)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-06(2026-09-08、第2弾ユーザー決定四点[A Voices Comment
Contract採用+禁止句追加/B B-Family Production経路設計案のみ/C Theme2 B1 Numeric
Precision選択肢A決定的置換/D-1〜D-3遡及点検・登録・player標準フォーマット]の統合)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-07(2026-09-08、第3弾ユーザー決定五点[1. Theme2 B1
rerun_04正式採用・rerun_03置き換え/2. B-Family Phase1先行承認(別タスク進行中)/
3. Theme2 A2「24.1%」仕様問題close+B1同方式Artifact最小修正/4. 過去完成物
遡及修正不要/5. OPEN-126独立性再評価]の統合)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-08(2026-09-08、第4弾ユーザー決定六点[1. Theme2 A2
rerun_04最終承認・OPEN-112 Theme2音声close/2. OPEN-121方式D閾値現状維持・23件
試聴確認方針/3. OPEN-126 close/4. OPEN-124整理タスク起票(分類のみ)/5. OPEN-125
低優先保留/6. OPEN-119・OPEN-122・OPEN-118・OPEN-112本体残件は据え置き]の統合)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-09(2026-09-08、Phase 1修正結果・OPEN-121
artifact・OPEN-124分類の統合)
- [履歴] ## PM-GOVERNANCE-REVIEW-LINK-REQUIRED-AND-AUTOCOMPACT-50-12(2026-09-08、
判断依頼時のリンク必須化・auto-compact閾値50%への変更・運用整理六点)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-11(2026-09-08、B-Family Phase 1受入・Trial A/B
起票結果のSSOT反映)
- [履歴] ## OPEN-127/OPEN-128-PRODUCTION-WIRING(2026-09-08、ユーザー承認+実装結果)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-13: OPEN-127/OPEN-128 Fable最終受入(PRODUCTION_WIRED確定)
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-14: 2026-09-08セッションclose、ユーザー最終確認
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-17: Lane A 3件+Lane B統合設計のSSOT反映、voice sample試聴artifact作成、新規OPEN-129登録
- [履歴] ## OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01: Trend Synthesis modeをProduction Writer正式初回経路へGate 3配線
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-18: Lane B A2完成Trial承認とTrial-02 VALIDATED、Lane A-3通常Newsドラフト完成、voice割当決定、並列Lane報告ルール追加
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-19: Trend Synthesis modeをGate 7で`PRODUCTION_WIRED`として最終受入、A-1修正分Git反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-21: Lane B A2横断監査結果(B-Family A2 vs 既存A2標準)のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-26: OPEN-129対策Trial結果のSSOT反映
- [履歴] ## ユーザー決定(2026-09-09): Fact Checker候補A'(OPEN-131)・OPEN-129
案(a)を`APPROVED_FOR_PRODUCTION`→配線(Sonnet委任、Fable受入待ち)
- [履歴] ## OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01・
OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01:
Sonnet委任配線結果
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-29: OPEN-131/OPEN-129 SSOT表記確定+Lane A
G1/G2縮小方針+「既存対策・仕様 Reconciliation Check」正式化+Gate 6
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-37: Family A Completion Program起票
(OPEN-135新規)・4V→3V設計修正Trial起票(OPEN-120追記)・Ledger
Deviation Checkerコスト調査起票(OPEN-136新規)・PM_GOVERNANCE
2-2/9-2節への追記
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-38: A1 Gap Audit完了・Ledger Deviation
Checkerコスト調査結果(訂正含む)・A4 Discovery設計(未承認)のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-39: A4 Discovery設計Opusレビュー転記・v2設計
(2軸判定+タイブレーク・机上検証)のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-40: A2 Trend end-to-end(A2 level完走)の
SSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-41: Editorial Type Routing(2軸判定)・
Discovery/Why(Pool型)決定(D1/D2/D3)のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-42: 3V Person-Voice Trial-01結果のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-43: A2 Trend end-to-end B1B level完走のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-44: A3 News Focus Hint比較Trial-06結果のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-45: 3V Person-Voice Trial-02結果のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-46: D2 Discovery Layer3 Trial-07結果のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-48: Reconciliation Gate・FACT-03再検証・Haiku L0集計のSSOT反映
- [履歴] ## PM-CLOSEOUT-CONSOLIDATION-49: 3V Person-Voice Trial-03結果のSSOT反映
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-50: B-3V-3(3V基準記事確定)・A-FACT03-1
(Household FACT-03最小修正)ユーザー決定のSSOT反映
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-51: Lane A News/Discovery再改善 段階1
再集計・Opusレビュー転記のSSOT反映
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-52: Lane A News/Discovery再改善 段階2
決定(N-1/N-2/N-3、D-1/D-2)のSSOT反映+Haiku比較artifact commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-53: 3V Audio Trial結果のSSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-54: Household修正継続2回分・Discovery段階2
Trial結果のSSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-56: 承認5件反映・3V Audio Trial VALIDATED
closeout・OPEN-139詳細記録+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-57: Household FIX-03(topic_intro承認)
完了のSSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-58: Discovery Trial-09(D-3、Ledger v5)結果の
SSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-59: Household一本化方針(Primary=Discovery
改善版/Fallback=A-FACT03-5)・Artifact supersession確認原則の反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-60: News Trial-09(N-4、新テーマ)結果の
SSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-61: Discovery Trial-10(D-4、保険文対策)結果の
SSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-62: News Stage 4整理(Sonnet)+Opus L2レビュー+
Evidence Allocation監査の結果のSSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-63: Household一本化最終候補
(HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01)結果のSSOT反映+commit
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-64: Household一本化最終候補のB1B comment_3
差し替え+Discovery保険文対策Part B案1(c)見送り確定+Lane B照合
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-65: Household最終版closeout+3V(3声Voice方式)の
APPROVED_FOR_PRODUCTION反映+表記ルール新設
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-66: 報告単位管理ルール(Reporting Unit Rule)
の正式SSOT反映(即時報告・未回答フル再掲・Next Action提示、恒久ルール)
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-67: 2026-09-10ユーザー次アクション確定指示の
SSOT反映(Household記録訂正+Discovery一般化確認Trial起票+News Blocking/
deferred分類統一+3V Production Wiring Phase 1確定+Phase 2/2V比較記事
計画+4V DEFERRED再確認+低コスト分析・Trial自律実施ルール新設)
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-68: Discovery Focus Module一般化確認
Trial-11(タオル臭テーマ)結果のSSOT反映+Git統合+モデルルーティングLOG保守
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-69: 3V(3声Voice方式)Production配線Phase 1
完了(実装+offline regression PASS)のGit統合+Phase 2前提不一致の記録
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-70: 2026-09-10ユーザー回答・追加指示10項目の
SSOT反映+恒久ルール追加+haiku-worker新設+Token効率診断REPORTのGit記録
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-71: News Trial-12完走+OPEN-140是正完了+CAR-T
再生成PASS+Discovery Opus L2レビュー記録(新規OPEN-141)+CONSOLIDATION-70後
のユーザー追加確定のSSOT反映
- [本ファイル内] ## PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01: OPEN_ITEMS.md巨大単一行の構造分割(内容不変)
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-72: PCシャットダウン復旧確認+3V Phase 1b実装/
Opus L2レビュー2件/TTS retryモニタ/T2-T3評価のGit統合+Discovery
Trial-11 Audio GATE_BLOCKED記録
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-73: ユーザー回答2026-09-11(3V/Discovery/News/
TTS retry timing/Token効率/量産APIコスト/新規記事テーマ)のSSOT反映
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-74-USER-ANSWERS-2026-09-11-02: ユーザー回答
2026-09-11第2回(News追加切り分けTrial承認/3V Comment 3共有定義承認/
Claude開発Token削減T-3施策A・B正式採用/既存進行事項事実訂正/Reporting
Rule再確認)のSSOT反映+Opus L2解釈(Trial-12)のREPORT化
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-75-NEWS-TRIAL-14: News Trial-14(曖昧性解消)+
Trial-12b(leaveout)結果のSSOT反映(副仮説REJECTED・主仮説USER_DECISION_
REQUIRED)+PM_GOVERNANCE 8節へgit stash/clean禁止追記
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-76-TOWELS-AUDIO-HUMAN-REVIEW: Discoveryタオル
音声resume(Trial-11)のHuman Review 3件をSSOT反映+TTS費用集計gemini_batch
¥0計上バグを新規OPEN-144として起票
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-77-PM-OPERATION-CORRECTION-2026-09-12: 「問題発生→
とりあえずHuman Review依頼」運用の是正、PM_GOVERNANCE新設14節(問題発生時のPM処理原則)・
15節(コスト報告ルール)・9-5(問題対応報告7項目順+試聴Artifact/playerリンク必須)追加+
タオルTrial-11コスト報告初回適用
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-78-RECONCILE-RESULTS-2026-09-12: 並列稼働中
だった4件のreconcile結果(A2表記ゆれ/B1B Secondary ASR+retry timing/Repetition QA根本原因
/News人名ローマ字表記)のSSOT反映+Sonnetの指示違反(禁止されたLLM API呼び出し1回)の記録
+新規OPEN-145/OPEN-146起票+OPEN-144補正額¥180.55反映
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-79-USER-CORRECTION-2026-09-12-02: ユーザー
2回目の是正指示(個別対応禁止・failure mode一般化徹底、B1B has/had実音声確認方針、
Repetition QA数字↔数詞同値化APPROVED_FOR_PRODUCTION、News人名対策の候補比較Trial要請、
TTS Trial/開発=Standard同期・量産=Batch別軸管理、コスト報告5区分化、PM再発防止)の
SSOT反映(OPEN-121/135/142/143/144/145/146・PM_GOVERNANCE 7-4/14/15/9-5・
ACTIVE_TASK.md更新)
- [本ファイル内] ## PM-CLOSEOUT-CONSOLIDATION-80-REPETITION-QA-NUMBER-WORD-FIX: OPEN-121
数字↔数詞同値化Production実装完了のSSOT反映+Gate 3個別判定表+タオルB1B
full_story_part2採用+News人名Trial設計完了の反映

---

## PM-CLOSEOUT-CONSOLIDATION-50: B-3V-3(3V基準記事確定)・A-FACT03-1
(Household FACT-03最小修正)ユーザー決定のSSOT反映

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
ユーザーが同日正式決定した2件をSSOTへ反映した。

**B-3V-3=(a)**: 3V Person-Voice Trial-02最終版
(`er012_output/editorial_b_voices_3v_person_voice_trial_02/
b1b_run01_attempt2/article.md`)を3V基準記事として**VALIDATED**確定。
3V目標尺は「約380〜400秒(3V実測基準)」へ更新した(Trial設計目標であり、
Productionの正式尺仕様の変更ではない)。Trial-03(Tension圧縮再生成、
`PM-CLOSEOUT-CONSOLIDATION-49`参照)は品質後退のためREJECTED相当のまま
記録保持する。今後は`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01`
(3V Audio Trial、実施中)へ進む。

**A-FACT03-1=(a)**: Household公開記事(A2/B1B、2026-08-17承認)の
FACT-03由来誤記述(`HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01`で
Fact Checker FAILが確定済み、`PM-CLOSEOUT-CONSOLIDATION-48`参照)を、
Numeric Precision修正(Theme 2 B1 rerun_04時に実施したArtifact最小修正、
本ファイル`OPEN-112行rerun_04関連エントリ`参照)と同一手順の「既存承認済み
Artifactへの最小修正例外」方式で、該当segmentのみ差し替える
(`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02`、実施中)。
**本件はpolicy変更ではなく例外適用である**: 既存の「遡及修正不要」方針
(表現・精度差レベルの事後改善は完成済みArtifactを書き換えない)は維持
したまま、Fact Checker FAILが確定した個別の事実誤りに限り、承認済み
Artifactへの最小修正(該当segmentのみ差し替え)を例外的に適用する。
新しいFact policyは新設しない。完了後はUSER_FINAL_AUDIO_REVIEWとする。

**SSOT反映**: `OPEN_ITEMS.md` OPEN-120行(B-3V-3決定、3V基準記事=
Trial-02版VALIDATED、目標尺更新、Audio Trial実施中、Trial-03=REJECTED
相当)・OPEN-138行(A-FACT03-1決定、最小修正例外、実施中、完了後は
USER_FINAL_AUDIO_REVIEW)へ追記した。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`
へ3V Audio Trial・Household最小修正・本タスクの行を追記した。

**根拠**: ユーザー決定(2026-09-09、Fable(PM)委任メッセージ内で提示)。
Git操作: `OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`をファイル名指定でcommitし
`origin/main`へpush。並列稼働中の3V Audio Trial(`er012_output/
editorial_b_voices_3v_audio_trial_*`等)、Household最小修正
(`er003_output/n3_01/household/fact03_fix_02/`、`er011_output/
*household*`)、Lane A段階1再集計(`er011_output/point_quality_*`、
`FAMILY-A-POINT-QUALITY-*`)、`er006_output/`、
`er011_output/attempt_history.jsonl`、`CURRENT_SPEC.md`、既存の
未追跡ファイル群はいずれも本タスクでは触っていない。

## PM-CLOSEOUT-CONSOLIDATION-51: Lane A News/Discovery再改善 段階1
再集計・Opusレビュー転記のSSOT反映

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
`FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01_REPORT.md`
(Opusレビュー、Fable転記の要旨)と`FAMILY-A-POINT-QUALITY-STAGE1-
RECOMPUTATION-01_REPORT.md`(段階1事後再集計、Sonnet、実測¥3.34)の
成果をSSOTへ反映した。

**Opusレビュー(Fable転記の要旨)**: 先行するSonnet横断整理
(`FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01`)が提示した
中核的な因果連鎖のうち、もぐらたたきが主因という主張・Focus Module
がRole収束を引き起こすという主張を、実データ・コードで否定した
(Opus消費約100,000トークン・372秒)。

**段階1再集計の要点**: (a)overlap_ratio交絡は条件により異なる
(Trial-06/04のFocus/hint系優位は語数交絡ではなく実質、Trial-05
gapfixの「悪化」は語数交絡でほぼ説明)。(b)Trial-06 baseline lexical
flag 17/18・真の入れ替わり4件はOpus引用を完全再現、全4Trial合計の
真のswap(狭義)は7件(Haiku L0集計の50件はany-change定義による
過大評価)。(c)value単独NG時のoverlap診断section構築は無条件
(コード確認)、設計意図(ER-011-NO18)は「加算的」で基本構造は仕様
どおりだが、断定文言の事実精度自体は不明(未検討)。(d)cross_point_
overlap全240件平均0.1311、現行閾値0.40超は0件。(e)Role Planningに
Focus Moduleへの因果経路はコード上存在しない(コード確認)一方、
Trial-07 discovery_focus実績のRole収束(6/6 run全てmechanism/
myth_correctionのみ)は同一入力の新規N=10抽選(実測¥3.34)でも
再現せず、**真因は依然不明**。(f)G1語彙プライミング仮説はattempt=0
で既に差が存在し非単調なため不支持寄り。(g)Role再計画は診断結果
非依存の「盲目の再抽選」であり、命令文言が診断sectionより後で強い
ことをコードで確認。

**SSOT反映**: `OPEN_ITEMS.md` OPEN-135行(段階1完了・要点・UDR候補
(i)〜(iv)・Trial-07 Role収束の真因不明を追記)、OPEN-133行
(cross_point_overlapの事後集計値=平均0.1311を追記、retry判定への
統合は引き続き行わない)、OPEN-134行(A-UDR-22観測項目へ「value単独
NG後のlexical flag発生」「swap回数(狭義)」の2項目を追加)へ追記した。
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へOpusレビュー・段階1・Haiku
比較artifact(実施中)・本タスクの行を追記した。

**UDR候補(実装しない、ユーザー裁定待ち)**: (i)value単独NG時の
overlap診断section構築を条件分岐する(¥0・低リスク)。(ii)overlap
指標の分母正規化/閾値再校正(QA基準変更、Fact Safetyリスク中)。
(iii)G1語彙プライミングのA/B Trial(¥60〜80、優先度低)。(iv)Role
再計画へ診断結果を渡す(効果不明、実装規模中)。いずれも人間ユーザーの
承認(`APPROVED_FOR_PRODUCTION`または明示的UDR裁定)が無い限り実装
しない。

**根拠**: Fable(PM)からの委任(2026-09-09、Opusレビュー転記・段階1
再集計の要旨を含む)。Git操作:
`FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01_REPORT.md`・
`FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01_REPORT.md`・
`er011_point_quality_stage1_recomputation_01.py`・
`er011_point_role_planning_reproducibility_stage1_01.py`・
`er011_output/point_quality_stage1_recomputation_01/`配下・
`er011_output/point_role_planning_reproducibility_stage1_01/`配下
(json/md/jsonlのみ)をG1、`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`をG2としてファイル名指定で
commitし`origin/main`へpush。並列稼働中の3V Audio Trial
(`er012_output/editorial_b_voices_3v_audio_trial_*`等)、Household
最小修正(`er003_output/n3_01/household/fact03_fix_02/`、
`er011_output/*household*`)、Haiku比較artifact(`er011_output/
news_discovery_comparison_artifact_l0_01/`、`er011_news_discovery_
comparison_artifact_l0_01.py`)、`er006_output/`、`er011_output/
attempt_history.jsonl`、`CURRENT_SPEC.md`、既存の未追跡ファイル群は
いずれも本タスクでは触っていない。

## PM-CLOSEOUT-CONSOLIDATION-52: Lane A News/Discovery再改善 段階2
決定(N-1/N-2/N-3、D-1/D-2)のSSOT反映+Haiku比較artifact commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
ユーザー正式決定(2026-09-09)による段階2方針をSSOTへ反映した。

**ユーザー決定の要旨**: News側 N-1=(a)value単独NG時の診断条件分岐を
Trial harnessで検証、N-2=(a)閾値・分母は変えず240件で判断材料を
作成、N-3=(b)Role再計画への診断結果受け渡しは保留。Discovery側
D-1=(a)既存の断定回避規則が効かない理由を¥0分析したうえで最小
Writer側調整Trial(Ledger v4、N=3)、D-2=(a)多様性はPoint本文
(cross_point_overlap+目視)で測定し、Role文字列ヒューリスティック
分類は廃止(評価方法の変更であり、Production仕様[QA基準・Writer
規則]そのものの変更ではない)。News/DiscoveryともProduction採用は
まだ行わず、段階2の最小Trialと分析結果の提示までとし、必要な判断点
ではSTOPする。管理ID`FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-
TRIAL-08`・`FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08`
(いずれも実施中、本タスクでは着手していない)。

**SSOT反映**: `OPEN_ITEMS.md` OPEN-135行(段階2決定の要旨・2Trial
管理IDを追記)、OPEN-133行(cross_point_overlapを多様性の観測指標
[Point本文+目視、Role文字列分類廃止]として使用する方針を追記、
still_flagged統合[未実装・DEFERRED]は変更なし)、OPEN-112行
(段階2Trial起票の参照を追記)へ反映した。`docs/pm/MODEL_ROUTING_
TRIAL_LOG.md`へHaiku比較artifact(実績値確定)・News段階2・
Discovery段階2・本タスクの行を追記した。

**Haiku比較artifact**: `NEWS-DISCOVERY-COMPARISON-ARTIFACT-L0-01`
(Haiku/L0、38k token・158秒・¥0)が完了した。Haiku起因のSonnet
再作業は0件(定型artifact生成というL0適合タスクであったため)。

**根拠**: Fable(PM)からの委任(2026-09-09、ユーザー正式決定N-1/N-2/
N-3・D-1/D-2の伝達を含む)。Git操作: `er011_news_discovery_
comparison_artifact_l0_01.py`・`er011_output/news_discovery_
comparison_artifact_l0_01/`配下md/htmlをG1、`OPEN_ITEMS.md`・
`DECISION_LOG.md`・`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`をG2として
ファイル名指定でcommitし`origin/main`へpush。並列稼働中のNews段階2
(`er011_output/news_stage2_*`・`er011_news_stage2_*`)、Discovery
段階2(`er011_output/discovery_stage2_*`・`er011_discovery_stage2_*`)、
Lane B 3V Audio(`er012_*`)、Household修正(`er003_output/n3_01/
household/fact03_fix_02/`)、`er006_output/`、`er011_output/
attempt_history.jsonl`、`CURRENT_SPEC.md`、既存の未追跡ファイル群は
いずれも本タスクでは触っていない。Production/Prompt編集・新規Trial
着手は実施していない(SSOT反映+Haiku比較artifactのGit記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-53: 3V Audio Trial結果のSSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01`の結果をSSOTへ反映した。

**Trial結果の要旨**: 3V基準記事(Trial-02最終版)を用いて3声(Voice 1=
Algieba/Voice 2=Erinome/Voice 3=Schedar)のAudio Trialを実施した。
16 segment全てstatus=OK・asr_verified=True、Human Review Lockなし。
OPEN-121(repetition QA)/OPEN-122(connected speech equivalence)安全
機構をpoint_one/two/threeへ同一規約で対称適用しrepetition_qa_
checked=Trueを3声全てで確認、disfluency必須9 segmentも確認した。
Comment 2/3は3V版ドラフト(`TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED`、
未承認・registry未登録)を使用。Audio Validation Gate既定OFF経路
PASS、opt-in ON経路(Trial側`build_required_structure_3v()`、16
segment)もPASS、negative control2件(voice名誤り→`VOICE_MISMATCH`、
point_three除外→`UNEXPECTED_EXTRA_SEGMENT`)で正しくBLOCKEDを確認し
(OPEN-129構造Gateの3V実績、mandatory化Trigger(a)の材料)。Assembly
実測356.613秒(peak0.95、clippingなし)、更新後目標380〜400秒より
約6〜11%不足(旧目標325〜355秒には近い)。Fact/content整合6/6。
費用¥93.82(TTS57.69/LLM33.41/ASR2.72)。Gate1=`USER_DECISION_
REQUIRED`(尺のみ)。

**Fable判定**: 尺のみが「テキスト見積り395秒→実測357秒」という通常の
見積り誤差であり、Voice/構造/Gate/Fact整合は全て成立しているため
品質問題ではないと判定し、VALIDATED候補としてユーザー試聴へ進める。

**SSOT反映**: `OPEN_ITEMS.md` OPEN-120行(3V Audio Trial結果、
VALIDATED候補・実測357秒・ユーザー試聴待ち、Production配線に必要な
5項目、Schedar本採用格上げの承認待ちを追記)、OPEN-129行(3V構造Gate
実績=mandatory化Trigger(a)到達、Trigger(b)[次回A-Family Production
run]は未達のため両方揃うまでUSER_DECISION_REQUIRED提示を保留する
PM-CLOSEOUT-CONSOLIDATION-29の規定を再掲)、OPEN-132行(Phase 2
チェックリストへ3V Audio Trialで判明した配線項目[required_structure
可変voice数シグネチャ・Gate辞書point_three登録要否・Comment 3V文言
Contract化・mode/level命名・Schedar格上げ承認]を追加)へ反映した。
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へ3V Audio Trial(Sonnet/MEDIUM)・
Household修正継続2件(Sonnet/MEDIUM)・本タスクの行を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09)。Git操作:
`er012_editorial_b_voices_3v_audio_trial_01.py`・
`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01_REPORT.md`・
`er012_output/editorial_b_voices_3v_audio_trial_01/`配下json/md/
html/jsonl(wav除外)をG1、`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`をG2としてファイル名指定で
commitし`origin/main`へpush。並列稼働中のNews段階2(`er011_output/
news_stage2_*`・`er011_news_stage2_*`)、Discovery段階2(`er011_
output/discovery_stage2_*`・`er011_discovery_stage2_*`)、Household
修正継続(`er003_output/n3_01/household/fact03_fix_02/`、`er011_
output/open138_*`)、`er006_output/`、`er011_output/attempt_
history.jsonl`、`CURRENT_SPEC.md`、既存の未追跡ファイル群はいずれも
本タスクでは触っていない。Production/Prompt編集・Trial着手は実施
していない(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-54: Household修正継続2回分・Discovery段階2
Trial結果のSSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02`(OPEN-138)継続
2回分と`FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08`
(OPEN-135段階2)の結果をSSOTへ反映した。

**Household修正継続の要旨**: 継続1回目、revision2のTTS省略誘発表現
("the low-humidity one")をrevision3aへ修正した(Fact Checker PASS・
Ledger v4 COMPLIANT、TTS point_one attempt 1でPASS、Human Review Lock
発動なし)。Assembly実行時、既存Production Gate(disfluency QA必須化・
ASR Cascade改善等)が2026-08-17承認当時のレガシー13segment(disfluency
QA未記録・一部STOPPED状態)をブロックし、`EPISODE_BLOCKED_BY_AUDIO_
VALIDATION`で例外停止した。これはpoint_one修正とは無関係の記事全体の
前提条件問題であり、Gate回避・承認記録の遡及作成はいずれも指示範囲外
のため実装せずSTOPした。継続2回目、他segment再生成・承認記録の遡及
作成は行わず、現行Gateが要求する既存QA関数(disfluency QA・ASR
Cascade)をレガシー13segmentの既存wav(byte不変)へ事後適用した。
disfluency 12/12 PASS、topic_intro ASR再照合PASS、kp2_english FAIL
(短い2語フレーズ"crisper drawer"でASRが"CRISPR"と誤認識、entity_like/
homophone判定不能によりcascade対象外条件のため即FAIL、Production
実際の挙動と同一)。13/14 PASSだが1件不合格のため指示どおりAssembly・
Gate通過・player生成は実施せずSTOPした(比較試聴ページ
`legacy_qa_review.html`)。費用累計¥37.09(上限内)。作業中に判明した
一般論(2026-08-17以前承認のレガシー記事は現行Gate導入以降のQA証跡を
持たない)を新規OPEN-139として起票した。

**Discovery段階2の要旨**: Part A(¥0机上)で既存記事の断定回避規則
違反claim 10件を分類(Ledger起因6件・規則の具体性不足4件・別failure
mode 1件)し、規則不徹底の原因(位置・具体性・強度)を分析、最小調整案
2件を提示した。Part B(N=2、実測¥70.8)はblocking・Ledger Deviation・
cross_point_overlap flagged全て0/8で安全側指標に新規リスクは確認され
なかったが、PASS率の条件間差はN数が小さく統計的に結論づけられない。
作業中にLedger v4のFACT-03修正文言がFACT-04と内部矛盾する新規課題を
発見し、是正タスク`HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03`を
別途起動した(本Trialの権限では修正せず報告のみ)。Gate 1分類は
`USER_DECISION_REQUIRED`(N数不足+Ledger側の未解決課題)。

**SSOT反映**: `OPEN_ITEMS.md` OPEN-138行(revision3a採用・レガシーQA
事後適用13/14 PASSでSTOP・UDR A-FACT03-2を追記)、OPEN-135行
(Discovery段階2結果・Ledger v4矛盾発見を追記)、新規OPEN-139
(遡及QA方針、`USER_DECISION_REQUIRED`、起票のみ)を追加した。
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へDiscovery段階2(Sonnet/MEDIUM)・
Household修正継続2(Sonnet/MEDIUM)・Ledger v5是正(実施中、Sonnet/
LOW〜MEDIUM)・本タスクの行を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID PM-CLOSEOUT-
CONSOLIDATION-54)。Git操作: G1=
`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02_REPORT.md`・
`er011_output/open138_household_fact03_b1b_minimal_fix_02/`配下py/
json/jsonl・`er003_output/n3_01/household/fact03_fix_02/b1b/`配下
md/json/html(commit `38b2f44`)。G2=
`er011_discovery_stage2_interpretation_rule_trial_08.py`・
`er011_discovery_stage2_interpretation_rule_trial_08_comparison.py`・
`FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08_REPORT.md`・
`er011_output/discovery_stage2_interpretation_rule_trial_08/`配下
json/md/html/jsonl(commit `93e9b7c`)。G3=`OPEN_ITEMS.md`・
`DECISION_LOG.md`・`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。いずれも
ファイル名指定でcommitし`origin/main`へpush。並列稼働中のNews段階2
(`er011_output/news_stage2_*`・`er011_news_stage2_*`)、Household
Ledger v5是正中の`verified_fact_ledger.txt`・
`HOUSEHOLD-LEDGER-FACT-03-04-*`、`CURRENT_SPEC.md`・`er006_output/`・
`er011_output/attempt_history.jsonl`・既存の未追跡ファイル群はいずれも
本タスクでは触っていない。Production/Prompt編集・Trial着手は実施
していない(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-56: 承認5件反映・3V Audio Trial VALIDATED
closeout・OPEN-139詳細記録+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
ユーザー正式決定5件をSSOTへ反映した。並列稼働中: News N-4
(`er011_output/news_stage3_*`)、Discovery D-3(`er011_output/
discovery_stage3_*`)、Household kp2承認(`er003_output/n3_01/
household/fact03_fix_02/`)、いずれも本タスクでは対象外(SSOT・Git
担当のみ)。

**ユーザー決定の要旨**: (1) N-4=(a)別テーマの新規News Ledgerを既存
Research経路で作成、Focus+hintでA2/B1B N=3、題材依存の切り分け+News
Completion実走(`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`、
実施中)。(2) D-3=(a)Ledger v5で現行版 vs 最小調整版N=3
(`FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09`、実施中)。
(3) A-FACT03-2=(a)kp2_english試聴OK→HUMAN_APPROVED→Assembly→player
(実施中)。(4) A-FACT03-3=OPEN-139を起票のみ詳細化(新policyは決めず、
未決事項・trigger・判断が必要な理由だけを記録)。(5) B-3V-4=(a)3V完成
episode試聴OK、3V Audio Trial(Trial-02版基準)を**VALIDATED**として
closeout(VALIDATED≠Production採用)。

**3V Audio Trial closeoutの要旨**: 新規`EDITORIAL-B-FAMILY-VOICES-
3V-AUDIO-TRIAL-01-CLOSEOUT_REPORT.md`を作成し、ユーザー指定10項目
(Voice assignment/required_structure 3V/Comment 3V wording/実測尺
356.6秒[2V比+51.5秒・約+17%]/Analytical Leakage 0/Distinctness 1.0・
0.933/Fact A' 2/2 PASS/Audio structural gate両経路PASS+negative
control検知/listening artifact/2Vとの差分・負荷感)を表で整理し、
Gate1=**VALIDATED**(ユーザー試聴承認2026-09-09)と確定した。
Production採用判断は別途USER_DECISION_REQUIRED(配線に必要な5項目
[registry可変voice数シグネチャ・Gate辞書point_three登録・Comment 3V
Contract化・mode/level命名・Voice 3(Schedar)本採用格上げ承認]を継続
提示)。本closeoutは新規コード実行を伴わないSSOT整理のみ(費用¥0)。

**OPEN-139詳細化の要旨**: 新policyを決定・`CURRENT_SPEC.md`への追加は
行わず、未決事項を4点へ整理して記録した。(1)遡及QAの範囲(現行Gate
導入前の全episodeへ及ぼすか、事実誤り確定時のみに限定するか)、
(2)修正方式(「既存承認済みArtifactへの最小修正例外」方式を恒久的な
標準手順として一般化してよいか)、(3)trigger(次に事実誤りが確定した
時点で都度判断するか、Family A Completion Programが量産段階に近づいた
時点でまとめて判断するか)、(4)判断が必要な理由(「完成audioの遡及修正
は不要」という既存運用方針とFact Safety最上位原則との整合が未整理、
量産でepisode数が増えるほど同種の事後QA不合格ケースの運用負荷が増す
可能性)。状態は`USER_DECISION_REQUIRED`のまま(起票の詳細化のみ、
今回は判断しない)。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-56へ)、
OPEN-120行(3V Audio=VALIDATED・closeout Report参照・Production採用
判断はUDR継続)、OPEN-129行(mandatory化Trigger(a)=到達済みのまま
変更なし・Trigger(b)=引き続き未達、closeoutはTriggerに影響しないことを
明記)、OPEN-135行(N-4/D-3を新規管理IDで起票・実施中)、OPEN-138行
(A-FACT03-2実施中)、OPEN-139行(上記4点の未決事項詳細化)へ反映した。
`CURRENT_SPEC.md`「## B-Family(Voices)Editorial Type」節へ3V(人物
Voice)=VALIDATED(Trial、2026-09-09、Production採用は別判断)の1行を
追加した。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へN-4(Sonnet/MEDIUM)・
D-3(Sonnet/MEDIUM)・kp2承認(Sonnet/LOW)・本タスクの行を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-56)。Git操作: G1=
`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01-CLOSEOUT_REPORT.md`
(新規)。G2=`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。いずれもファイル名指定で
commitし`origin/main`へpush。並列稼働中のNews段階3
(`er011_output/news_stage3_*`)、Discovery段階3(`er011_output/
discovery_stage3_*`)、Household kp2承認(`er003_output/n3_01/
household/fact03_fix_02/`)、`er006_output/`、`er011_output/
attempt_history.jsonl`、既存の未追跡ファイル群はいずれも本タスクでは
触っていない。Production/Prompt編集・新規Trial着手は実施していない
(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-57: Household FIX-03(topic_intro承認)
完了のSSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
Household FIX-02継続分(§13〜14)とFIX-03の結果をSSOTへ反映した。
並列稼働中: News N-4(`er011_output/news_stage3_*`)、Discovery D-3
(`er011_output/discovery_stage3_*`)、いずれも本タスクでは対象外
(SSOT・Git担当のみ)。

**承認記録の要旨(正規経路、status捏造なし)**: (1) A-FACT03-2に基づく
FIX-02継続3で、kp2_englishを既存人間承認経路(`record_human_approval()`)
でHUMAN_APPROVEDとして記録し、disfluency QA(既存関数の事後適用)にも
PASSした。残る唯一のブロック要因topic_intro=STOPPEDはユーザー決定の
対象範囲外だったため、Sonnetは承認代行を拒否しSTOPした(FIX-02継続4も
同じ安全原則を再確認しSTOPを維持、規律遵守の好例)。(2) A-FACT03-4=(a)
に基づくFIX-03で、topic_introをkp2_englishと同じ既存承認経路で
HUMAN_APPROVEDとして記録した(note「現行ASR cascadeによる事後再照合
PASS」、`tts_generation_results.json`の`status`フィールドは書き込み
前後で不変であることをassertで確認済み、捏造なし)。Assembly実行
(duration_seconds=284.754・peak=0.8312・clippingなし)、Gate既定OFF・
opt-in ON両経路PASS、Gate 7全充足のplayer生成まで到達し(sha256 32件中
31件original一致、point_oneのみrevision3a差分)、費用¥0。到達Status=
**USER_FINAL_AUDIO_REVIEW_REQUIRED**(ユーザー最終試聴待ち)。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-57へ)、
OPEN-138行(FIX-03完了・試聴待ち・承認記録2件[kp2_english/topic_intro]は
いずれも正規経路[既存`record_human_approval()`]・A2は無変更を追記)、
OPEN-139行(FIX-03で新たに確認した判断材料を追記: Household B1B
topic_introは2026-08-17承認時に生成時ASR FAIL×6のまま承認されていた
[旧cascadeの限界]、現行Gate導入前の承認済みsegmentには証跡不整合が
あり得る、policyは未決定のまま[新policy採用ではない])を反映した。
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へFIX-02継続3(Sonnet/113k)・継続4
(Sonnet/65k、STOP正当)・FIX-03(Sonnet/158k)・本タスクの行を追記し、
所見(「Sonnetは承認代行・status捏造を拒否してSTOPした[規律遵守の
好例]」)を1行記録した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-57)。Git操作: G1=
`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02_REPORT.md`(§13〜14)・
`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03_REPORT.md`(新規)・
`er011_output/open138_household_fact03_b1b_minimal_fix_02/`・
`er011_output/open138_household_fact03_b1b_minimal_fix_03/`配下py/json/
jsonl/html・`er003_output/n3_01/household/fact03_fix_02/b1b/audit/`配下
json・同`b1b/`配下md/json/html(wav除外)。G2=`OPEN_ITEMS.md`・
`DECISION_LOG.md`・`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。いずれも
ファイル名指定でcommitし`origin/main`へpush。並列稼働中のNews段階3
(`er011_output/news_stage3_*`)、Discovery段階3(`er011_output/
discovery_stage3_*`)、`CURRENT_SPEC.md`、`er006_output/`、
`er011_output/attempt_history.jsonl`、既存の未追跡ファイル群はいずれも
本タスクでは触っていない。Production/Prompt編集・新規Trial着手・
policy策定は実施していない(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-58: Discovery Trial-09(D-3、Ledger v5)結果の
SSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
`FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09`(D-3)の結果をSSOTへ
反映した。並列稼働中: News N-4(`er011_output/news_stage3_*`)、本タスクでは
対象外(SSOT・Git担当のみ)。着手前に`PM-CLOSEOUT-CONSOLIDATION-57`
(commit`dabc188`)の完了をgit logで確認した。

**Trial結果の要旨**: Household Verified Fact Ledger v5(FACT-03/04内部
矛盾を是正済み)を`prod_gen.THEMES`経由でそのまま参照し、current_focus
(現行Discovery Focus Module)とadjusted_focus(Trial-08 Part A案1、断定
回避段落末尾へscope一般化禁止文を追加)をN=3×A2/B1B×2条件=12本
(text-only、実測¥127.3、Fact Checker¥96.6分離)で比較した。安全側指標
(blocking・Ledger Deviation・Local Rewrite創作・cross_point_overlap
flagged)は両条件・全12本で0件と維持された。一方、raw REVIEW+FAIL率
(current 1/6→adjusted 2/6)、FACT-03起因ノイズ(Fact Checkerが指摘した
claimのうちLedger v5が元々含む商業/家庭あいまいさの再述だったもの)を
手動判定で除外した「真のREVIEW_REQUIRED率」(current 0/6→adjusted 1/6)
のいずれも、adjusted_focusはcurrent_focusを下回らなかった。よって
**Gate 1分類=REJECTED**(主目的[REVIEW削減]は未達成、方向は横ばい〜
悪化、Fact Safetyは両条件維持)。

**重要な副次的発見**: Ledger v5是正後、現行Discovery Focus Module
(current_focus)自体の真のREVIEW_REQUIRED率が0/6となった。Trial-07で
観測されたbaseline比約5倍のREVIEW増加(OPEN-112が懸念材料としていた
論点)は、Ledger v5適用後にはほぼ消失している。これは、当時のREVIEW
増加の主因がFocus Module側の欠陥ではなく、Ledger v4のFACT-03/04内部
矛盾側にあったことを示唆する。多様性・深さ・Discoveryらしさの最終判断は
比較artifact(`comparison.html`)によるFable/ユーザーの目視(D-4)に
委ねられており、本タスクでは未実施(提示中)。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-58へ)、
OPEN-135行(D-3結果[調整版REJECTED、真のREVIEW率0/6→1/6]・D-4[目視判断]
提示中を追記)、OPEN-112行(Discovery Layer3のREVIEW懸念がLedger v5是正で
解消方向にあり、`VALIDATED`のまま維持・Production採用は別途UDRのままで
あることを追記)、OPEN-138行(本OPEN-138のLedger v5是正がDiscovery側の
REVIEW懸念解消に寄与したことを確認した旨を追記)を反映した。
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へD-3(Sonnet/MEDIUM、247k token、
1756秒、tool呼び出し635回=多め、Gate 1=REJECTED[候補棄却であり
タスク失敗ではない])・本タスクの行を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-58)。Git操作: G1=
`er011_discovery_stage3_rule_adjustment_trial_09.py`・
`er011_discovery_stage3_rule_adjustment_trial_09_batch_runner.py`・
`er011_discovery_stage3_rule_adjustment_trial_09_comparison.py`・
`FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09_REPORT.md`(すべて
新規)・`er011_output/discovery_stage3_rule_adjustment_trial_09/`配下
json/md/html/jsonl/txt。G2=`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。いずれもファイル名指定でcommitし
`origin/main`へpush。並列稼働中のNews段階3(`er011_output/
news_stage3_*`)、`CURRENT_SPEC.md`、`er006_output/`、`er011_output/
attempt_history.jsonl`、既存の未追跡ファイル群はいずれも本タスクでは
触っていない。Production/Prompt編集・新規Trial着手・policy策定は実施
していない(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-59: Household一本化方針(Primary=Discovery
改善版/Fallback=A-FACT03-5)・Artifact supersession確認原則の反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
ユーザーが正式決定したHousehold(Discovery/Why)の一本化方針と、
再発防止のためのPM運用原則「Artifact supersession確認」をSSOTへ反映
した。並列稼働中: Discovery Trial-10(`er011_output/discovery_stage4_*`)、
News N-4(`er011_output/news_stage3_*`)。本タスクはSSOT・Git担当のみで
両Laneの成果物はstageしていない。

**ユーザー決定の要旨**:

1. A-FACT03-5(Household FACT-03最小修正版、
`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03`、技術的に完成・
到達Status=USER_FINAL_AUDIO_REVIEW_REQUIRED)は現時点で正式置き換え
承認しない。同じHouseholdテーマでDiscovery Focus Moduleの軽微改善
(Trial-10)を進行中で、成立すれば記事→Support→Audioまで新しい完成
候補を作る予定であり、同一記事について「旧完成版のFACT-03最小修正版」
と「新Discovery仕様の改善版」を二重に最終版として承認しない。

2. Householdの扱いはPrimary=Discovery軽微改善Trial(良好ならA2/B1Bの
記事→Support→Audio→listening artifactまで作成しHouseholdの一本化
された最終候補として提示)、Fallback=A-FACT03-5(fallback candidate /
formal replacement保留として保持、current正式artifactへ置き換えず
最終版として承認済みにせず新版と並立させない)。Discovery改善が不成立
または新候補に到達できない場合のみA-FACT03-5を正式版候補として再提示
し、それまでA-FACT03-5のUDRは再提示しない。

3. 再発防止原則(PM運用): 同じ記事・episodeについて仕様変更やPrompt
改善による再生成が予定されている場合、旧完成品の個別修正を始める前に
必ず確認する: (A)近く新仕様で再生成される予定があるか、(B)その結果が
旧artifactをsupersedeする予定か、(C)旧artifactを今修正しても新版完成後
すぐ不要にならないか。A/BがYesなら原則として旧artifactの個別修正を
行わず、新仕様での再生成側へ修正内容を統合する(「旧品修正→ユーザー
確認→完成→直後に新仕様で再生成→再確認」の二重工程を作らない)。例外
(新版完成まで長期間かかる/公開中の重大なFact誤りを放置できない/
safety・compliance上の暫定修正/新仕様Trialが成立する見込みが低い)時も
「暫定修正版」と「次期最終候補」を明確に分け、二つの正式最終版を
並立させない。主要artifactの再生成・修正前にはexisting current
artifact/active regeneration・spec-change task/planned supersession/
duplicate finalization riskを確認する。

4. Production wiring・正式採用はユーザー判断まで行わない(変更なし)。

**SSOT反映**: `docs/pm/PM_GOVERNANCE.md`へ2節の新小節「2-3. Artifact
supersession確認」(確認A〜C・原則・例外・暫定修正版と次期最終候補の
分離・経緯)を新設し、3節「PM Closeout Mandatory Check」へ項目14
(主要artifactの修正前にsupersession確認)を追加、冒頭changelogへ1文
追記した。`docs/pm/PM_BRIEF.md`へ2-3節参照の1行を追記した。
`OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-59へ)、OPEN-135行
(Household最終候補=Discovery改善版[Trial-10→記事→Support→Audio]を
一本化候補として作成予定、Primary/Fallback方針を追記)、OPEN-138行
(A-FACT03-5=fallback candidate/formal replacement保留、Discovery改善版
成立時に一本化、不成立時のみ正式版候補として再提示、試聴依頼は保留を
追記)を反映した。`CURRENT_SPEC.md`は変更していない(運用原則のため
対象外)。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へTrial-10(Sonnet/MEDIUM、
実施中)・本タスク(Sonnet/LOW)の行を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-59)。Git操作: ファイル名指定で
`docs/pm/PM_GOVERNANCE.md`・`docs/pm/PM_BRIEF.md`・`OPEN_ITEMS.md`・
`DECISION_LOG.md`・`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`をcommitし
`origin/main`へpush(`git add -A`は不使用)。並列稼働中のDiscovery
Trial-10(`er011_output/discovery_stage4_*`)・News N-4(`er011_output/
news_stage3_*`)、`CURRENT_SPEC.md`、`er006_output/`、`er011_output/
attempt_history.jsonl`、既存の未追跡ファイル群はいずれも本タスクでは
触っていない。Production/Prompt編集・新規Trial着手は実施していない
(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-60: News Trial-09(N-4、新テーマ)結果の
SSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`(N-4)の結果をSSOTへ
反映した。並列稼働中: Discovery Trial-10(`er011_output/discovery_
stage4_*`)、本タスクでは対象外(SSOT・Git担当のみ)。

**Trial結果の要旨**: Hanshin以外の新規News Ledgerを既存Research正式
経路で作成し(新テーマ=in-vivo CAR-T[NEJM 2026-09-03]、14件CONFIRMED、
費用¥57.89)、そのLedgerでFocus Module+Point Role hint条件を
A2/B1B×N=2(予算超過見込みのためN=3から自律的にN=2へ縮小、run1完了
時点でN=3見込み¥186.6>予算¥150と判断、費用¥142.50)実施した結果、
最終NG 0/4を得た。Hanshin Trial-06(baseline 6/6・focus_hint 3/6)・
Theme2 Trial-05(baseline 2/4)と比較すると、初期attempt flag率(2/4)は
題材によらず同水準だが、retry後の最終解消率は本Trial4/4(100%)に対し
Hanshin focus_hintでは3/6(50%)しか解消しておらず、「retryが発火する
かどうかは題材非依存だが、retryで実際にPointの意味づけを分離できる
かどうかは題材依存」という方向性の示唆を得た(N=4小標本、断定的な
結論ではない)。

B1B full pipeline(Key Phrase→TTS→Assembly→Audio Validation Gateまで
既存Production関数を無変更で実行、費用¥40.10)はKey Phrase
REDUNDANCY_PASS、TTS 13segment中12件RESOLVED(OK)だが、
`full_story_part1`が3回試行(既存retry上限)後もASR検証NG
(`TRUE_CONTENT_MISMATCH`、"a report on"を3回とも一貫して読み落とす)
でHUMAN_REVIEW_REQUIREDへ遷移、Assemblyは`EPISODE_BLOCKED_BY_AUDIO_
VALIDATION`で正常STOP(既存Human Review Lock・Audio Validation Gate
が意図通り機能、player・完成episodeは未生成)。**この
`full_story_part1`のHUMAN_REVIEW_REQUIREDは、ユーザー承認なしに
再生成・HUMAN_APPROVED記録・Assembly実行のいずれも行わない**(本
タスクの委任範囲外、試聴artifact化する場合は再生成1回のユーザー承認が
別途必要)。

作業中、誤操作でB1B full pipelineスクリプトを二重起動し即座に強制
終了する事故が1件発生した(約¥2.56の無駄なScaffold呼び出し、
TTS/Key Phrase/Assemblyは非重複)。副作用としてScaffold出力
[Preview/Comment本文json]が2回目生成で上書きされ、実際に音声化された
1回目の本文とbyte不一致になった(記事本文自体には影響なし、Gate
BLOCKEDのため最終artifactは元々未生成、cosmetic)。これは規律違反
として`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`のTrial-09行に記録した。

Gate 1分類は`VALIDATED(Trial)`止まり(Production採用[Focus Module+
hint配線]は本Trial単体では判断しない、別途十分なNでの再現性確認が
必要)。総費用¥240.49(Step0¥57.89+Step1¥142.50+B1B full pipeline
¥40.10)。News Focus Module Production採用(N-3)は引き続き保留。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-60へ)、
OPEN-135行(N-4結果[新テーマ選定理由・最終NG0/4・比較表・題材依存の
示唆・小標本注記・B1B full pipelineがHuman Review Lock/Audio
Validation Gate発動で正常STOP・Production採用未判断]を追記)、
OPEN-137行(News Completionの人手介在箇所[テーマ選定/Mode判定/
Ledger供給、B1BのみのためA2日本語タイトルは本Trialでは未検証]が
OPEN-137の既知gap[3箇所]と同一構造であることを追記)を反映した。
`CURRENT_SPEC.md`は変更していない(Production採用なし)。
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へTrial-09行を確定値(Sonnet/
MEDIUM、¥240.49、N=3→2縮小の自律判断、二重起動事故1件を規律違反として
記録)へ更新し、本タスク(Sonnet/LOW)の行を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-60)。Git操作: G1=
`er011_news_stage3_new_theme_ledger_trial_09.py`・
`er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py`・
`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09_REPORT.md`(すべて
新規)・`er011_output/news_stage3_new_theme_ledger_trial_09/`配下・
`er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/`配下
(json/md/jsonl/txt。既存commit慣行[`discovery_stage3_rule_
adjustment_trial_09`・`family_a_completion_a2_trend_end_to_end_01`等]
に合わせ、音声バイナリ[wav]58件は対象から除外)。G2=
`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/MODEL_ROUTING_TRIAL_
LOG.md`。いずれもファイル名指定でcommitし`origin/main`へpush。並列
稼働中のDiscovery Trial-10(`er011_output/discovery_stage4_*`、対応する
root直下の`er011_discovery_stage4_*.py`・REPORT)、`CURRENT_SPEC.md`、
`er006_output/`、`er011_output/attempt_history.jsonl`、既存の未追跡
ファイル群はいずれも本タスクでは触っていない。Production/Prompt編集・
`full_story_part1`の再生成・HUMAN_APPROVED記録・新規Trial着手は実施
していない(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-61: Discovery Trial-10(D-4、保険文対策)結果の
SSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
`FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10`(D-4)の結果を
SSOTへ反映した。並列稼働中: Household一本化候補生成
(`er011_output/household_unified_final_candidate_01/`、
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01_REPORT.md`)、News整理
(`er011_output/news_stage4_redesign_inventory_01/`、
`er011_news_stage4_redesign_inventory_01.py`、
`FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01_REPORT.md`)。本タスクでは
いずれも対象外(SSOT・Git担当のみ)。

**Trial結果の要旨**: Household Verified Fact Ledger v5(無変更)上で
current_focus(Before)とcautionary_constrained(After、Part B案1=
未承認候補)をN=3×A2/B1B×2条件=12本(text-only)実施した(実測¥100.5、
うちFact Checker¥73.1/その他¥27.4)。保険文(聞き手に取扱説明書・
メーカー案内・専門家など記事外の情報源確認を促す独立した一文)は
Writer生出力由来で、Household Ledger v5のFACT-03再検証で追加された
家庭用ガイド不一致記述(ストロベリー/オレンジの高湿度分類、GE/Samsung
間の見解相違)を記事が明示的に扱ったrunにのみ出現した(current_focus
2/6、争点非該当runは両条件・全Trialを通じて0/16)。Part B案1(既存の
断定回避段落末尾へ、外部参照を呼びかける独立した保険文を書かないよう
求める1文を追加、Ledgerが注意喚起自体を発見として明示する場合は例外)
を適用すると保険文Before 2/6→After 0/6となり、安全側指標(blocking
[FAIL] 0/12、Ledger Deviation 0、創作0、cross_point_overlap 0/12)は
両条件で維持、語数もほぼ同水準(A2平均300語台)で不自然な簡略化は
確認されなかった。

一方でREVIEW率がAfter側で0/6→2/6へ上振れした(A2 run2=Point-vs-Story
類似度0.474で既存Point Overlap安全機構[ER-008-N8-FINAL-QA-HARDENING-21]
によるNG_REVIEW_REQUIRED、B1B run2=Fact Checkerが「バナナ冷蔵可能期間の
一般化」「エチレン感受性の一般化」を指摘)。両件とも内容的にはPart Bの
追加文言(保険文の禁止)とは無関係な既存QA機構の指摘であり、Trial-09の
adjusted_focusで見られた「追加文言がLedgerのあいまいさをより積極的に
書かせた結果REVIEWが増えた」という因果関係とは異なる。ただしN=3
(合計12本)は小さく、この上振れが本当に無関係かはPart Bの副作用と
断定できない。

Gate 1分類は`VALIDATED`(Trial範囲)。Part B文言のProduction Discovery
Focus Moduleへの正式採用、および`editorial_mode="discovery_why"`の
正式registry登録は、いずれも別途`USER_DECISION_REQUIRED`(未承認候補の
まま)。

**Household一本化候補への所見**: 担当Sonnetは、Household A2/B1B
一本化候補(記事→Support→Audio→試聴artifact)への進行について
「現時点では推奨しない(条件付き)」との所見を提示した。根拠は
(1)Part B文言はまだ未承認候補でありProduction Prompt側は無変更のため
現状のHousehold一本化はcurrent_focus(Before)のままとなりD-4の保険文
問題は未解決で流れる、(2)After条件でのREVIEW率上振れ(0%→33%)の因果
関係がN=3では統計的に確認できない、の2点。推奨としては(a)Part B採用の
場合はもう1ラウンド(N=5程度)の追試で上振れの再現性を確認してから
一本化へ進む、(b)不採用の場合はcurrent_focus(Before)のまま一本化を
進めD-4の保険文問題は別途Human Reviewでの目視修正に委ねる、の
いずれかをユーザーに判断してもらう、というもの。**この所見はSonnetの
提示であり判断そのものではない**。ユーザーはこの所見を把握した上で、
並行してHousehold A2/B1B一本化候補(Trial扱い)の生成をFableへ指示し、
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`として実行中(結果は別途SSOT
反映)。

**規律事象**: Trial-10の初回担当がバックグラウンド待機で一度停止した
(規律違反)。Fableが引き継ぎ担当を起動したところ、初回担当は自力復帰し
Trialを完了させており、引き継ぎ担当は同一のREPORT・`comparison.html`を
再作成(上書き、追加API費¥0)した。二重稼働事象として
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へ記録した。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-61へ)、
OPEN-135行(Trial-10結果要旨・Part B案1=未承認候補・VALIDATED・REVIEW率
上振れ注記・二重稼働事象・Household一本化候補生成中を追記)、OPEN-138行
(保険文の引き金がv5追加のFACT-03是正記述である事実、A-FACT03-5は
fallback保留のままを追記)、OPEN-112行(Discovery Layer3懸念[Trial-07
REVIEW率]と保険文問題はLedger v5起因の別事象であることを追記)を
反映した。`CURRENT_SPEC.md`は変更していない(Production・Prompt変更
なし)。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へTrial-10行を確定値
(Sonnet/MEDIUM、¥100.5、バックグラウンド待機1件を規律違反として記録)
へ更新し、引き継ぎ担当行(Sonnet/LOW、¥0、二重稼働)、Household候補行
(Sonnet/MEDIUM、実行中)、News整理行(Sonnet/MEDIUM、¥0、実行中)、
本タスク(Sonnet/LOW)を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-61)。Git操作: G1=
`er011_discovery_stage4_cautionary_language_trial_10.py`・
`er011_discovery_stage4_cautionary_language_trial_10_comparison.py`・
`FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10_REPORT.md`・
`er011_output/discovery_stage4_cautionary_language_trial_10/`配下
(json/md/html/jsonl/txt、既存commit慣行に合わせ音声バイナリは対象から
除外)。G2=`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/MODEL_ROUTING_
TRIAL_LOG.md`。いずれもファイル名指定でcommitし`origin/main`へpush。
並列稼働中のHousehold一本化候補生成(`er011_output/household_unified_
final_candidate_01/`等)・News整理(`er011_output/news_stage4_redesign_
inventory_01/`等)、`CURRENT_SPEC.md`、`er006_output/`、
`er011_output/attempt_history.jsonl`、既存の未追跡ファイル群はいずれも
本タスクでは触っていない。Production/Prompt編集・Trial着手・
バックグラウンド待機は実施していない(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-62: News Stage 4整理(Sonnet)+Opus L2レビュー+
Evidence Allocation監査の結果のSSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
News段階4再設計に向けたSonnet整理(`FAMILY-A-NEWS-STAGE4-REDESIGN-
INVENTORY-01`)+Opus L2レビュー+`FAMILY-A-NEWS-STAGE4-EVIDENCE-
ALLOCATION-AUDIT-01`(¥0監査)の結果をSSOTへ反映した。並列稼働中:
Household一本化候補生成(`er011_output/household_unified_final_
candidate_01/`、`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01_REPORT.md`)。
本タスクでは対象外(SSOT・Git担当のみ)。

**Sonnet整理の要旨**: `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01`
(¥0 offline限定、既存Trial出力[Hanshin/Theme2/CAR-T、48 run・248
Point-attempt観測]の読み取り再集計、新規API呼び出しなし)は、既存
14仕組みの構造整理(語彙重複が3層[Writer Prompt/lexical Overlap QA/
Diagnostic Full Retry診断]で反復提示される構造、cross_point_overlap
[#7]がretry判定未使用、Point Role Planning[#3]がFocus Module[#4]を
受け取らない独立経路)を再確認した上で、topic_structure別flag率
(single_event_boxscore 46.9%・survey_trend 47.4%・mechanism_
limitation 25.0%)を新規集計した。§3-2で「shared_wordsから固有名詞・
数値語を除外すると全体flag率45.56%→13.31%(single_event_boxscoreは
46.91%→7.73%)」という結果を得たが、目視(§3-1)では「固有名詞と意味
重複が混在し分離できない」ことも確認し、過大解釈を避ける記述とした。
改善候補4件(優先順位順: (1)診断feedbackへの「トレードオフ回避」明示
指示、(2)Role Planning再抽選への診断結果フィードバック接続、(3)
topic_structureを考慮したNews題材選定ガイダンス、(4)Ledger由来語
ベースのnecessary factual overlap除外指標[観測指標のみ])を根拠・
反証・リスク・cost見積・最小Trial設計付きで提示し、Opus設計レビューに
掛けるべき論点4点を整理した。

**Opusレビュー要旨**(Report非作成、Fable転記に基づき本エントリへ記録):
(1)§3-2(entity除外でflag率45.6%→13.3%)は閾値未再校正のartifactであり、
序数除去漏れ・entity辞書サイズの非対称性(Hanshin 45語/Theme2 9語/
CAR-T 11語)という欠陥がある。`er008_point_overlap_qa_18.py`の閾値0.40は
「通常Point 0.15〜0.35」を前提とした暫定校正であり`_STOPWORDS`は
one/two/threeのみに限定される、という題材別ミスキャリブレーションの
直接証拠である。(2)候補1・候補2はTrial-08(情報削減方向、REJECTED)と
同根の限界を持つ可能性があり、真の問題は検出力不足(Trial-08 N=6で
3/6 vs 5/6、Fisher正確検定p≈0.55で有意差検出不能)。候補3は「不利な
題材構造を避ける」回避策であり構造自体の改善ではなく、topic_structureは
テーマ・Ledgerと完全に交絡している。**最大の見落としは論点H(Ledger
fact供給量/evidence allocation)**: Hanshin実質usable fact数5に対し
CAR-T 14と大きな差があり、Sonnet整理はこれを検討していなかった。
(3)retry責務競合を、コード(`er003_v1_n3_01_articles_generate.py`で
Role Planning blockが診断sectionより後ろに配置され、`run_point_role_
planning`はretry時もtopic+ledgerの2引数のみを受け取る「盲目の再抽選」)
とデータ(Trial-04 A2 baseline run1のanchor回帰実例)の両面で確認した。
構造改善案として「retryで固定すべきはfact割当、変えるべきは表現角度」
という提案を提示した。(4)Sonnet整理には推測箇所が5点あった。(5)次の
最小Trialとして¥0のevidence allocation監査を提案し、評価量を二値NG率
から連続量(overlap_ratio)へ切り替えることを推奨した。(6)STOP該当性:
候補1(Prompt変更、承認要)、候補2(retry方針変更、STOP該当の可能性)、
候補3(編集方針、ユーザー判断)、候補4(観測指標のみ、非該当)、Ledger
拡充(Research/Fact Safety領域、ユーザー判断)。

**監査結果の要旨**: `FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01`
(¥0、既存48 run・124 attempt観測の読み取り再集計、新規API呼び出し
なし、データ欠落0件)は、Opus指摘の論点Hを検証した。Part 1: anchor
衝突数とP1-P2語彙overlap(cross_point_overlap系)の相関はr=0.4623(基準
r>0.3達成)で正相関を確認したが、実際のGate指標(Point対Full Story
overlap、閾値0.40)とはr=0.1852、最終NG二値とはr=0.0997といずれも
弱く基準未達だった。すなわち「anchor衝突→P1-P2語彙的類似」の経路は
支持されるが、その語彙的類似が実際のNG判定を動かす経路は支持されない
(**部分的支持**)。initial→retryのanchor変化は76〜79%が新規組み合わせへ
変わり(盲目の再抽選と整合)、衝突再燃率は23.6%(13/55衝突event)。
テーマ別使用可能fact数(5/8/14)とNG率(72.2%/50.0%/0.0%)は単調な逆関係
にあり、fact利用率(95.6%/67.2%/37.5%)も単調に低下したが、N=3テーマ
のみで topic_structure・条件構成と完全に交絡しており分離不可(既存の
限界を踏襲)。Part 2: 候補4(entity除外overlap)の完全正規化版(分子・
分母ともentity/数値除外、N=96=48 run×2 Point)は、flag率26.0%→11.5%、
raw比率との順位相関r=0.9132、パーセンタイル整合閾値での分類入替
10.4%(10/96件)であり、entity辞書サイズの非対称性(Point内容語に占める
Ledger由来語割合がHanshin 17.5%に対しTheme2 3.3%・CAR-T 2.8%)に起因
するテーマ依存artifactとして**棄却に近いが完全棄却ではない**と判定
した。Part 3: Trial-08(N=6)の実際のGate指標(Point対Full Story overlap
連続値)はNG群平均0.405・OK群平均0.321(差0.084)で、二値NG率(Fisher
p≈0.55で検出力不足)より閾値0.40近傍で意味のある差を示した一方、
cross_point_overlapの差は0.033に留まった(連続量切替による検出力向上
余地を確認、統計的有意性の主張ではない)。データ欠落・限界として、
Full Storyに`evidence_anchor`フィールドが存在せずpoint-to-story直接
測定は不可(fact利用率で代替)、**Theme2 LedgerのID不整合(F-210/
F-211)を新規発見**(既存Ledgerデータ品質問題、本監査では補正せず観測
のみ、新規`OPEN-140`を起票)した。

**Status**: いずれも¥0・VALIDATED/整理段階に留まる。Production・
Prompt・QA・retryコードの変更は一切行っていない。Fableは(1)主軸を
候補1/2→論点H(Ledger fact供給・evidence allocation)へ移すか、(2)
候補3を「Ledger拡充」へ読み替えるか、(3)候補2見送り可否、(4)Trial
評価量の連続量化承認、の4点をユーザーへ提示中(次候補=Ledger拡充
Trial A/B[Hanshin型、N=6]・候補4不採用判断・OPEN-133再検討、いずれも
ユーザー判断待ち)。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-62へ)、
OPEN-135行(News Stage 4整理・Opusレビュー・監査の要旨、UDR 4件提示中、
次候補=Ledger拡充Trial A/B保留・候補4棄却寄りを追記)、OPEN-133行
(監査の定量根拠を追記: anchor衝突→P1-P2語彙類似は実在、NG判定経路は
非該当)、OPEN-134行(候補4完全正規化の棄却寄り判定・評価量の連続量化
提案を追記、ユーザー判断待ち)、新規OPEN-140行(Theme2 LedgerのID
不整合[F-210/F-211]の是正要否、既存データ品質問題、未補正、
`USER_DECISION_REQUIRED`)を反映した。`CURRENT_SPEC.md`は変更していない
(Production採用なし)。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へNews整理
行(Sonnet/MEDIUM、¥0、確定)、Opus L2レビュー行(新規、HIGH理由=
Production QA/retry横断・複数設計案・過去のSonnet因果反証歴、成果=
Sonnet整理の構造的欠陥3点と見落とし論点Hの検出)、監査行(Sonnet/
MEDIUM、¥0、確定)、Household候補行(Sonnet、実行中、foreground 600s
上限によるバックグラウンド実行2回をtooling制約として記録し規律違反とは
区別)、本タスク(Sonnet/LOW)を追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-62)。Git操作: G1=
`er011_news_stage4_redesign_inventory_01.py`・
`FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01_REPORT.md`・
`er011_output/news_stage4_redesign_inventory_01/`配下・
`er011_news_stage4_evidence_allocation_audit_01.py`・
`FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`・
`er011_output/news_stage4_evidence_allocation_audit_01/`配下
(json/csv/md)。G2=`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/
MODEL_ROUTING_TRIAL_LOG.md`。いずれもファイル名指定でcommitし
`origin/main`へpush。並列稼働中のHousehold一本化候補生成
(`er011_output/household_unified_final_candidate_01/`等)、
`CURRENT_SPEC.md`、`er006_output/`、`er011_output/attempt_history.jsonl`、
既存の未追跡ファイル群はいずれも本タスクでは触っていない。
Production/Prompt編集・Trial着手・バックグラウンド待機は実施していない
(SSOT反映+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-63: Household一本化最終候補
(HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01)結果のSSOT反映+commit

Sonnet(sonnet-worker)が2026-09-09、Fable(PM)からの委任に基づき、
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`の結果をSSOTへ反映した。並列稼働
なし(単独タスク)。

**Trial結果の要旨**: Household(Discovery/Why、Ledger v5)の一本化を、
Discovery Focus Module軽微改善(`FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-
LANGUAGE-TRIAL-10`のPart B案1=`cautionary_constrained`、未承認候補、
保険文0(A2・B1Bとも)を確認済み)を用いてA2/B1B記事→Support→Audio→試聴artifactまで
作成した(Trial harness、既存Production QA/Audio Gate経路のみ使用)。
Trial-10条件は無変更のままread-only importで再利用し、独自出力先で
Gate 4静的確認(Production関数再定義なし、baseline↔cautionary差分は
単一insert、Ledger v5マーカー確認、Point Overlap Loop Budget=2)を実施し
PASS。記事生成はA2 status OK/fact_verdict PASS/ledger_status
LEDGER_COMPLIANT(0件)/Point Overlap記事全体retry1回(上限2、既存
Diagnostic Full Retry機構内で解消)/379語/保険文(regex)0件、B1B OK/
PASS/COMPLIANT(0件)/retry0回/399語/保険文0件。両レベルとも自己判断
による追加retry・再抽選は行っていない。Support(Preview/Comment/Key
Phrase)は全項目OK、Key Phrase Selection→Canonicalization→Redundancy
QAは両レベルとも1回でREDUNDANCY_PASSへ到達。A2日本語タイトルは
`JAPANESE_TITLES`辞書に本Trial theme_id未登録という既知gap(OPEN-137、
FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01と同一構造)が再発したため、
新しい主張・数字を追加せず既存Household完成版タイトルをそのまま流用
した(記録: `audit/a2_japanese_title_gap_note.json`)。Audio検証は全
segment(A2 14+Key Phrase5件EN/JA、B1B 13+Key Phrase5件EN/JA)がTTS/ASR
OK、Assembly(Gate OFF)PASS、Audio Validation Gate opt-in ON
(OPEN-129)もPASS(A2 330.0秒/peak 0.98[headroom適用]/clipping無し、
B1B 302.8秒/peak 0.953/clipping無し)。HUMAN_REVIEW_REQUIRED・
GATE_BLOCKED・Lockはいずれも発動せず、代理承認・独自回避は不要だった。
実測費用¥68.76(openai¥19.62・gemini TTS¥46.08・openai_asr¥3.06、
unpriced_records=0、上限¥300以内)。

Gate 1分類は`VALIDATED`相当(Trial範囲)。到達Statusは
**USER_FINAL_AUDIO_REVIEW_REQUIRED**。試聴artifact
`er011_output/household_unified_final_candidate_01/player.html`は標準
player規則(`audio_review_player.py`、Source列なし)に従うが、1ページに
A2/B1B両方の完成episode音声を並置するため、標準`SEEK_SCRIPT`(単一
episode音声前提)をdata属性でseek対象をscopeする専用JSへ置き換えた
(`build_player.py`内のみ、`audio_review_player.py`自体は無変更)。
差分要約は`diff_vs_old_final_summary.md`(保険文検出は新旧とも0件で
この指標だけでは優劣を示せない、Point切り口は新候補がより明示的、
FACT-03/04整合は新旧とも矛盾なし)。

**Supersession確認(PM_GOVERNANCE 2-3)**: 旧artifact
(`er011_output/open138_household_fact03_b1b_minimal_fix_03/`)・既存
Household完成版(`er003_output/n3_01/household/`)はいずれも読み取りのみで
一切変更していない。新候補は独立した並置artifactであり、旧完成版を
上書き・置換していない。

**規律事象**: 担当がBashツールのforeground 600秒上限を単一プロセスが
超えたため、ツール側の仕様でバックグラウンド実行→通知復帰が2回発生した
(tooling制約であり、複数プロセスの並行起動・二重起動ではない)。並列
稼働中の他タスク領域(`er011_output/discovery_stage4_cautionary_
language_trial_10/`、`er011_output/news_stage4_redesign_inventory_01/`)
は読み取りのみで一切編集していない。

**USER_DECISION_REQUIRED(未承認のまま、Fableがユーザーへ提示中)**:
(1) 新候補(A2/B1B)を旧完成版の後継として採用するか、旧完成版を維持する
か、A-FACT03-5(Household FACT-03最小修正版)fallbackへ戻すか(試聴・
比較のうえユーザー判断)。(2) Part B案1(`cautionary_constrained`)を
Production Discovery Focus Moduleへ正式採用するか(Trial-10はN=3・N=1
範囲の確認に留まる)。(3) `editorial_mode="discovery_why"`の正式
registry登録(採用する場合に必要、本Trialでは未登録の想定名のまま使用)。
Production採用・旧完成版との差し替えはいずれも未承認。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-63へ)、
OPEN-138行(一本化候補完成・USER_FINAL_AUDIO_REVIEW_REQUIRED・
A-FACT03-5 fallback保留継続・UDR 3件を追記)、OPEN-135行(Part B案1が
N=1完成経路でも保険文0・Lock無しを維持したがProduction採用は別途UDR
である旨を追記)、OPEN-137行(A2 JAPANESE_TITLES未登録gapの再発を手動
介在の実例として追記)を反映した。`ARTIFACT_REGISTRY.md`のHousehold項へ
新候補を「候補(未承認、並置)」として追記した(既存の正式artifact記載は
変更していない)。`CURRENT_SPEC.md`は変更していない(Production・
Prompt変更なし)。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`へHousehold候補行
を確定値(Sonnet/MEDIUM、¥68.76、tooling制約によるバックグラウンド
実行2回を規律違反とは区別して記録)へ更新し、本タスク(Sonnet/LOW)を
追記した。

**根拠**: Fable(PM)からの委任(2026-09-09、管理ID
PM-CLOSEOUT-CONSOLIDATION-63)。Git操作: G1=
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01_REPORT.md`・
`er011_household_unified_final_candidate_01_run.py`・
`er011_output/household_unified_final_candidate_01/`配下(json/md/html/
jsonl/txt/py、既存commit慣行に合わせ音声バイナリ[mp3/wav]は対象から
除外)。G2=`OPEN_ITEMS.md`・`DECISION_LOG.md`・`ARTIFACT_REGISTRY.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。いずれもファイル名指定でcommitし
`origin/main`へpush。`CURRENT_SPEC.md`、`er006_output/`、
`er011_output/attempt_history.jsonl`、旧Household artifact、既存の
未追跡ファイル群、`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`
はいずれも本タスクでは触っていない(ACTIVE_TASK/RESULT_PACKETは更新は
したがcommit対象外)。Production/Prompt編集・Trial着手・旧artifact変更・
バックグラウンド待機(自己判断によるもの)は実施していない(SSOT反映+
Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-64: Household一本化最終候補のB1B comment_3
差し替え+Discovery保険文対策Part B案1(c)見送り確定+Lane B照合

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(サブID
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01-SEGFIX-01`)に基づき実施した。
並列稼働なし(単独タスク)。

**背景(ユーザー確定事項)**: `HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`
(`er011_output/household_unified_final_candidate_01/`)をユーザーが
試聴し、A2/B1Bとも全体として良好=OKと判断した。ただしB1B comment_3
「The best choice depends on what kind of problem you want to
prevent.」の"prevent"の発音に違和感があるとの指摘があった。また、
保険文対策Part B案1は(c)見送り(Production不採用、
`editorial_mode="discovery_why"`の正式登録もしない)で確定した。

**作業A(comment_3確認・条件付き差し替え)**: 既存QA記録
(`b1b/audit/tts_generation_results.json`のsegments.comment_3)を確認
したところ、NORMALIZED_MATCH判定に使う主ASR(`asr_text`)は"prevent"と
一致していたが、disfluency QA用の独立したローカルASR
(`disfluency_evidence.transcript`、method=
`faster_whisper_small_local_verbatim`)が該当語のみ"perfect"と誤認識
していた機械的証拠を確認した(ユーザー指摘箇所と一致)。これを
「機械的に異常が確認できる場合」と判定し、既存segment再生成経路
(`er011_human_review_lock_01.approve_regenerate()`で明示的に
REGENERATE_APPROVEDへ遷移させたうえで、`er003_v1_sing01_voice01_
generate.generate_charon_english()`を元のcomment_3呼び出しと同一引数
[`style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM,
disfluency_qa=True`]で呼ぶ、既存Production関数を無変更のまま利用)で
comment_3のみ再生成した(`er011_household_unified_final_candidate_01_
segfix_comment3_01.py`)。Prompt/本文/Support文言(`b1_support_texts.
json`)は一切変更していない。1回でstatus=OK、Human Review Lock発動
なし。再生成後は独立ローカルASRの誤認識も解消(transcript上で"prevent"
と一致)。旧音声は`b1b/narration/comment_3_original.wav`として退避
(削除せず)。差し替え後、`er011_household_unified_final_candidate_01_
run.py`の`assembly_stage("b1b")`(無変更)でB1Bを再Assembly(status=OK、
duration=302.524秒、peak=0.95296、clippingなし)し、Audio Validation
Gate opt-in ON経路(OPEN-129)も再PASSを確認した。`build_player.py`
(無変更)で`player.html`を再生成した(A2側は無変更、影響なし)。
追加費用¥1.55(本タスク実測合計¥70.31、内訳openai¥19.62/gemini
¥47.55/openai_asr¥3.15、上限¥300以内)。

**Household一本化最終候補の確定**: 上記差し替え後の完成候補を、
Householdの一本化された最終候補として確定する。旧完成版
(`er003_output/n3_01/household/`)・旧artifact(`er011_output/
open138_household_fact03_b1b_minimal_fix_03/`、A-FACT03-5系)は本候補
によりsupersededとして整理した(いずれのファイルも削除はせず並置の
まま維持、A-FACT03-5の試聴依頼提示は行わない)。**本決定は
「Household記事1本の最終版承認」であり、本候補が用いた実験的Prompt
要素(Discovery Focus Module Part B案1)のProduction採用
(`APPROVED_FOR_PRODUCTION`)や`editorial_mode="discovery_why"`の正式
registry登録を意味しない。**

**Discovery保険文対策Part B案1の(c)見送り確定(ユーザー判断、
2026-09-10)**: 経緯は以下6点。(1)観測された保険文問題:
`FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10`(D-4)で、
保険文(聞き手に取扱説明書・メーカー案内・専門家など記事外の情報源
確認を促す独立した一文)はWriter生出力由来であり、Household Verified
Fact Ledger v5のFACT-03是正で追加された家庭用ガイド不一致記述
(ストロベリー/オレンジの高湿度分類、GE/Samsung間の見解相違)を記事が
明示的に扱ったrunにのみ出現した(current_focus条件2/6、争点非該当
runは0/16)。(2)Trialした対策案: Part B案1(既存の断定回避段落末尾へ、
外部参照を呼びかける独立した保険文を書かないよう求める1文を追加、
`cautionary_constrained`条件)。(3)Trial-10の結果: Part B案1適用で
保険文はBefore 2/6→After 0/6へ改善した一方、REVIEW率がBefore
0/6→After 2/6へ上振れした(A2 run2=Point Overlap NG_REVIEW_REQUIRED、
B1B run2=Fact Checkerの一般化指摘)。(4)因果は確定しなかった: N=3
(合計12本)は小さく、この上振れがPart B案1の副作用か既存QA機構の
通常のばらつきかは断定できなかった。(5)一方で
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`はPart B案1適用条件
(cautionary_constrained)を用いてN=1完成経路を通し、保険文0(A2・
B1Bとも)・Human Review Lock発動なしで成立した(`PM-CLOSEOUT-CONSOLIDATION-63`
エントリ参照)。(6)以上を踏まえ、ユーザーはPart B案1のProduction採用
(Discovery Focus Module正式組込み)を**(c)見送り**と判断した
(2026-09-10)。`editorial_mode="discovery_why"`の正式registry登録も
あわせて見送る。`CURRENT_SPEC.md`への追加は行わない。

**作業C(Lane B status SSOT照合、読み取りのみ)**: ユーザー認識6項目を
`OPEN_ITEMS.md`と照合し、いずれも**一致**を確認した(相違なし)。
(1) 3V Audio Trial=`VALIDATED`: `OPEN_ITEMS.md` OPEN-129行(281行目)の
`PM-CLOSEOUT-CONSOLIDATION-56`追記「3V Audio Trialが試聴承認により
Gate1=`VALIDATED`としてcloseoutした」と一致。(2) ユーザー試聴承認済み:
同追記「試聴承認により...closeoutした」と一致。(3) Production採用は
未決定: OPEN-120行(271行目)`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-
TRIAL-01`追記「Production配線に必要な項目(未承認、実装なし)」と一致。
(4) `APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない: 同OPEN-120
行「VALIDATEDはTrial範囲の技術的成立を意味するのみで、Production採用
(`APPROVED_FOR_PRODUCTION`)は別途ユーザー判断とし、配線に必要な項目...
は未実施のまま維持する」と一致。(5) Fact Checker A' cache=観測継続:
OPEN-136行(288行目)`PM-CLOSEOUT-CONSOLIDATION-47`(ユーザー正式決定
B-FC-1(b))追記「cacheはProduction実装しない。量産時に...8項目を記録
して観測を継続する...cache導入可否は観測後に別途
`USER_DECISION_REQUIRED`として判断する」と一致。(6) OPEN-129構造Gate
mandatory化=deferred: OPEN-129行(281行目)`PM-CLOSEOUT-CONSOLIDATION-
29/56`追記「mandatory化は現時点で行わず`DEFERRED`のまま維持する...
Status: `PRODUCTION_WIRED(opt-in)`/mandatory化`DEFERRED`(Trigger(a)
到達・Trigger(b)未達、変更なし)」と一致。`CURRENT_SPEC.md`は本タスクで
変更していない。

**SSOT反映**: `OPEN_ITEMS.md`ヘッダ(最終更新をCONSOLIDATION-64へ)、
OPEN-135行(Part B案1の(c)見送り確定の6点根拠を追記)、OPEN-138行
(comment_3差し替え結果・Household一本化最終候補確定・旧版supersession
を追記)を反映した。`ARTIFACT_REGISTRY.md`のHousehold項を「候補
(未承認、並置)」から一本化最終候補へ更新し、旧完成版・旧artifactを
supersededと明記した(旧ファイルは削除していない)。`CURRENT_SPEC.md`
は変更していない(Production・Prompt変更なし)。`docs/pm/MODEL_ROUTING_
TRIAL_LOG.md`へ本タスク行(Sonnet/LOW〜MEDIUM、実測¥1.55[累計
¥70.31]、Lock発動なし)を追記した。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-64、サブID
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01-SEGFIX-01`)。Git操作: ファイル
名指定で`git add`(`git add -A`不使用)、対象=`DECISION_LOG.md`・
`OPEN_ITEMS.md`・`ARTIFACT_REGISTRY.md`・`docs/pm/MODEL_ROUTING_TRIAL_
LOG.md`・`er011_household_unified_final_candidate_01_segfix_comment3_
01.py`・`er011_output/household_unified_final_candidate_01/`配下で
本タスクにより更新されたjson/md/html(既存commit慣行に合わせ音声
バイナリ[wav/mp3]は対象から除外)。1 commitで`origin/main`へpush。
`er006_output/`、`er011_output/attempt_history.jsonl`、既存の未追跡
ファイル群、`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は
いずれも本タスクでは触っていない(ACTIVE_TASK/RESULT_PACKETは更新は
したがcommit対象外)。Production/Prompt編集・`CURRENT_SPEC.md`編集は
実施していない(SSOT反映+comment_3限定のsegment再生成+Git記録のみ)。

## PM-CLOSEOUT-CONSOLIDATION-65: Household最終版closeout+3V(3声Voice方式)の
APPROVED_FOR_PRODUCTION反映+表記ルール新設

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-65)に基づき実施した。並列稼働中の読み取り
専用タスク2件(News Stage4状況報告の編纂、Discovery仕様reconcile分析。
いずれもroot直下`*_REPORT.md`のみ新規作成)とは独立(それらの生成物・
SSOT・一時ファイルには触れていない)。

**表記ルール新設(2026-09-10、ユーザー指示)**: ユーザー向け報告・SSOT
記述では、管理上の略号だけで書かず必ず内容が分かる名称を併記する運用を
新設した(例: ×「Part B案1」 ○「Discoveryの『取扱説明書的な保険文を
抑えるPrompt制約案』(Part B案1)」)。`docs/pm/PM_GOVERNANCE.md`9-3節へ
追記した。本エントリ以降の記述もこの形式に従う。

**Lane A-1: Household最終版closeout(ユーザー正式決定、2026-09-10)**:
ユーザーが`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`(Discovery/Whyの家庭用
冷蔵庫クリスパー記事、A2/B1B、B1B comment_3差し替え版
[PM-CLOSEOUT-CONSOLIDATION-64]反映済み)を最終試聴し**OK**と判断した。
これを受け、同artifactを**現行の正式Household完成artifact**として
closeoutした。旧Household完成版(`er003_output/n3_01/household/`、
2026-08-17承認)・A-FACT03-5系fallback(`er011_output/
open138_household_fact03_b1b_minimal_fix_03/`)は履歴として保持するが、
今後の正式候補として再提示しない(同一記事の二重最終版化を避ける運用、
`docs/pm/PM_GOVERNANCE.md`2-3節)。`OPEN-138`(Household Ledger FACT-03の
事実精度)は、(1)Ledger改訂完了(v3→v4→v5)、(2)是正済みLedgerに基づく
新版記事が正式artifactとなり旧誤記事がsupersededされたこと、の2点により
**CLOSED**と判定した。残件は`OPEN-139`(2026-08-17当時の遡及QA方針、
現行Gate導入前の既存公開episode一般の証跡不足問題)へ引き継ぐ(本Itemの
範囲外)。

**軽微訂正**: `PM-CLOSEOUT-CONSOLIDATION-64`エントリ(および同一箇所の
`PM-CLOSEOUT-CONSOLIDATION-63`エントリ)・`OPEN_ITEMS.md`OPEN-135行に
あった「保険文0/6」という表記は、最終候補がA2/B1B各1本(N=1)であるため
分母「/6」が不適切であり、「保険文0(A2・B1Bとも)」へ訂正した
(DECISION_LOG.md 2箇所、OPEN_ITEMS.md OPEN-135行2箇所、計4箇所)。

**発見事項(未対応、報告のみ)**: 上記訂正作業中、`OPEN_ITEMS.md`
OPEN-135行の`PM-CLOSEOUT-CONSOLIDATION-64`追記(5)に
「HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01自体はcurrent_focus(Before)の
まま...成立した」という記述があるが、同じOPEN-135行の
`PM-CLOSEOUT-CONSOLIDATION-63`追記には「使用したPart B案1
(`cautionary_constrained`)はN=1完成経路でも保険文0(A2・B1Bとも)・
Lock発動なしを維持した」とあり、**cautionary_constrained(Part B案1
適用)かcurrent_focus(Before、Part B案1未適用)かで記述が矛盾している**。
`DECISION_LOG.md`側(本エントリ上記)は「Part B案1適用条件
(cautionary_constrained)を用いて」と記載されており、こちらはOPEN-138行
の`PM-CLOSEOUT-CONSOLIDATION-63`追記と整合する。本タスクの委任範囲
(「保険文0/6」の数値表記訂正のみ)を超えるため、この矛盾自体は修正せず、
Fable/ユーザーへ報告する(`USER_DECISION_REQUIRED`候補: いずれの条件が
実際に使われたか事実確認のうえ、正しい方の記述へ統一が必要)。

**Lane B: 3V(3声Voice方式)に関するユーザー正式決定(2026-09-10)**:
(1)今回の3V記事(`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01`)はTrial
記事としてcloseoutした。(2)3V方式自体を**`APPROVED_FOR_PRODUCTION`**と
した(Status更新: `VALIDATED`→`APPROVED_FOR_PRODUCTION`)。ただし
**`PRODUCTION_WIRED`にはしない**。`PRODUCTION_WIRED`化の完了条件
(a)〜(k)、および配線時に無視してはならない残存課題(3V長文化・Tension
再膨張・Local Rewriteによる人物Voice抽象化失敗モード・Fact Checker A'
負荷・Distinctness維持・Audio structural gate mandatory化deferred
[OPEN-129])を`OPEN_ITEMS.md`OPEN-120行へ記録した。(3)2V(2声Voice方式)/
3Vそれぞれ別テーマで1本ずつProduction実運用確認を行う計画(観測項目11点)
を登録した(着手は別タスク)。(4)4V(4声Voice方式)は明示的に
`DEFERRED`とした(2V/3V追加記事のユーザー試聴完了まで着手しない)。

**SSOT反映**: `OPEN_ITEMS.md`(ヘッダ、OPEN-138行[closeout]、OPEN-135行
[Household最終版closeoutの追記+「保険文0/6」訂正]、OPEN-120行[Lane B
4項目])、`ARTIFACT_REGISTRY.md`(Household項を「正式完成artifact
(ユーザー最終試聴承認2026-09-10)」として明記)、`CURRENT_SPEC.md`
(「## B-Family(Voices)Editorial Type」節の3V状態行のみを`VALIDATED`→
`APPROVED_FOR_PRODUCTION`[未配線]へ更新、仕様本文は追加・変更なし)、
`docs/pm/PM_GOVERNANCE.md`(9-3節新設)、`docs/pm/MODEL_ROUTING_TRIAL_
LOG.md`(本タスク行追記)を反映した。コード・Prompt・Production実装は
一切変更していない(SSOT反映のみ、費用¥0)。

**Dangling Reference Check**: 本タスクで使用した新規仕様名・rule名
(「表記ルール」「`PRODUCTION_WIRED`化の完了条件(a)〜(k)」等)はすべて
既存SSOT(`docs/pm/PM_GOVERNANCE.md`Gate 3、`docs/pm/PM_BRIEF.md`Status
語彙)の既存定義の言い換え・列挙であり、未定義語の新規追加はない。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-65)。Git操作: ファイル名指定で`git add`
(`git add -A`不使用)、対象=`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`ARTIFACT_REGISTRY.md`・`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。1 commitで`origin/main`へpush。
並列タスクが作る`*_REPORT.md`・`docs/pm/ACTIVE_TASK.md`・
`docs/pm/RESULT_PACKET.md`・`er006_output/`・`er011_output/
attempt_history.jsonl`・既存の未追跡ファイル群はいずれも本タスクでは
触っていない(commit対象外)。Production/Prompt編集は実施していない
(SSOT反映のみ)。

**Fable修正指示1回目(2026-09-10)**: 上記「発見事項」のOPEN-135行内矛盾を
事実確認のうえ是正した。根拠: `er011_output/household_unified_final_
candidate_01/a2/audit/prompt.txt`・`b1b/audit/prompt.txt`双方にPart B案1
(`cautionary_constrained`、外部確認促しの独立した保険文を書かない旨の
1文)が含まれることをgrepで確認(確認日時2026-09-10)、`er011_household_
unified_final_candidate_01_run.py`もA2/B1B双方の生成呼び出しで
`CAUTIONARY_FOCUS_BLOCK`を使用していることを確認した。正しいのは
`PM-CLOSEOUT-CONSOLIDATION-63`側(cautionary_constrained適用)であり、
`PM-CLOSEOUT-CONSOLIDATION-64`追記(5)の「current_focus(Before)のまま」
は誤りと判定し、`OPEN_ITEMS.md`OPEN-135行を訂正した。

## PM-CLOSEOUT-CONSOLIDATION-66: 報告単位管理ルール(Reporting Unit Rule)
の正式SSOT反映(即時報告・未回答フル再掲・Next Action提示、恒久ルール)

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-66)に基づき実施した。並列稼働中のAgentはない。

**ユーザー正式決定(2026-09-10、恒久ルール)**: Lane A/B限定に矮小化せず、
内容を弱めないことを前提に、以下をPM運用SSOTへ反映した。

1. **報告単位(Reporting Unit)を基準に管理する**: 他の並列作業を待たずに
   ユーザーへ報告できる「ひと固まり」(Lane/Workstream/Feature/Trial群/
   Production wiring/Article単位/Investigation等、名称は問わない)を
   1報告単位として扱う。並列数はA/B/C/D…複数を前提とする。
2. **1つの報告単位が報告可能になったら即時報告**: Trial終了/
   `USER_DECISION_REQUIRED`到達/`APPROVED_FOR_PRODUCTION`到達/Production
   wiring完了/重要な途中結果判明/blocker発生/user review可能なartifact
   完成/closeout可能のいずれかに達したら、他の並列作業の完了を待たずに
   報告する。「AもBも揃ってからまとめて報告」と待つことを禁止する。
3. **未回答の報告は次の報告時に必ず再掲する**: 報告済みでユーザーの
   Feedback/判断がない項目がある状態で別の報告単位が報告可能になった
   場合、新規報告だけを出さず未回答分も合わせて再掲する(時点1: A→
   時点2: A+B→時点3: A+B+C)。ユーザーが明示的に回答・判断した項目のみ
   再掲対象から外す。
4. **再掲時は必ずフルレポートを再掲する**: 簡易サマリではなく前回提示
   したフルレポートを原則そのまま再掲(短縮・要約・一部省略しない)。
   前回レポート中の事実がその後更新された場合は「前回フルレポート」+
   「その後の更新・訂正内容」が明確に分かる形で提示する。artifact/
   listening link/comparison link等も必ず再掲する。
5. **大きな報告単位がcloseしたら必ず次の状態を示す**: 「完了しました」で
   終わらせず、(A)Next Action/Suggestion、(B)関連未解決事項の状況
   Reminder、(C)「この報告単位について残件なし」のいずれかを示す。
6. **Next Actionを勝手な仕様決定にしない**: Next Action提示はユーザー
   承認を飛ばして次工程へ進む権限ではなく、従来のPM Gate
   (`USER_DECISION_REQUIRED`ならSTOP/`VALIDATED`からProduction採用へ
   自動移行しない/`APPROVED_FOR_PRODUCTION`のみProduction wiring可/
   新仕様・意味変更・大きなQCD変更はユーザー判断/明示的deferredは
   deferredとして管理)を維持する。
7. **未回答管理を明示的に行う**: Fableは常に「報告済みだが未回答の
   項目」を把握し、次回報告を作る前に必ず確認する。明示的にdeferと
   ユーザー合意したものは毎回の再掲不要だが、大きなtask closeout時には
   Reminder対象として確認する。
8. **PM Closeoutとの統合**: 既存PM Closeout Mandatory Checkへ4項目
   (並列報告単位を待った遅延の有無/未回答フル再掲の実施/Next Action・
   Reminder提示/並列する他の報告単位Statusの見落とし確認)を追加し、
   既存Gate 5・Gate 6のUSER_DECISION_REQUIRED放置防止と統合する。
9. **今回への即時適用**: 現在のLane A(Household/Discovery/News)/
   Lane B(3V)にも直ちに適用する。
10. **SSOT反映**: 会話限りのルールにせず正式PM運用ルールとして記録する。

**SSOT反映内容**:

- `docs/pm/PM_GOVERNANCE.md`: 冒頭の最終更新行、新設「12. 報告単位管理
  ルール(Reporting Unit Rule): 即時報告・未回答フル再掲・Next Action
  提示」(12-1〜12-8)、「3. PM Closeout Mandatory Check」項目15〜18、
  Gate 5・Gate 6の記述への1〜2行追記、9-1「候補セクションと選択基準」へ
  候補セクション6(未回答再掲)・7(Next Action / Reminder、該当時省略
  不可)の追加、末尾「変更履歴」への新規エントリを反映した。
- `docs/pm/PM_BRIEF.md`: 「PM運用Gate・Closeout原則」節へ`docs/pm/
  PM_GOVERNANCE.md`12節への参照2〜3行を追記した。「ACTIVE_TASK固定
  ヘッダ」書式へ新フィールド`未回答報告`・`報告単位Status`を追加し、
  ヘッダ行数目安を15〜25行から20〜30行へ緩和した。
- `CLAUDE.md`: 「Fableサンドイッチ運用(PM層)」節へ、報告単位管理ルール
  (即時報告・未回答フル再掲・Next Action提示)の正式SSOTは
  `docs/pm/PM_GOVERNANCE.md` 12節である旨を1〜2行追記した。他の既存
  記述は変更していない。
- `OPEN_ITEMS.md`: ヘッダへ本エントリを参照する短い最終更新段落を追加
  した(新規Open Itemの起票はなし)。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: 本タスク行(Sonnet、LOW、¥0)を
  追記した。

**Dangling Reference Check**: 新設した節番号・フィールド名(12節、
12-1〜12-8、`未回答報告`、`報告単位Status`、Closeout Mandatory Check
項目15〜18、9-1候補セクション6・7)は`docs/pm/PM_GOVERNANCE.md`・
`docs/pm/PM_BRIEF.md`・`CLAUDE.md`間で一致していることを確認した。既存
節番号(1〜11、2-1〜2-3、9-1〜9-3)との衝突はない。未定義語の新規追加は
ない。

**コード・Prompt・Production実装は一切変更していない**(SSOT反映のみ、
費用¥0)。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-66)。Git操作: ファイル名指定で`git add`
(`git add -A`不使用)、対象=`docs/pm/PM_GOVERNANCE.md`・
`docs/pm/PM_BRIEF.md`・`CLAUDE.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。1 commitで`origin/main`へpush。
`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・その他未追跡
ファイルはcommitしていない。

## PM-CLOSEOUT-CONSOLIDATION-67: 2026-09-10ユーザー次アクション確定指示の
SSOT反映(Household記録訂正+Discovery一般化確認Trial起票+News Blocking/
deferred分類統一+3V Production Wiring Phase 1確定+Phase 2/2V比較記事
計画+4V DEFERRED再確認+低コスト分析・Trial自律実施ルール新設)

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-67)に基づき実施した。並列稼働中のsonnet-worker
3件(Discovery新テーマ一般化確認Trial-11、News Ledger拡充A/B Trial-12、
3V Production Wiring Phase 1)とは独立(それらが`er0XX_output/`配下へ
書く新規ディレクトリ・新規REPORT・コード[3V配線のみ]は本タスクでは
一切触っていない)。

**Lane A-1 Discovery — 記録訂正(必須)**: `OPEN_ITEMS.md`OPEN-135行・
ヘッダ「最終更新」段落に残っていた、`PM-CLOSEOUT-CONSOLIDATION-64`
エントリ由来の誤った因果説明を、ユーザー確定内容に基づき事実へ訂正した。
訂正前→訂正後は以下のとおり(全2箇所、いずれも`OPEN_ITEMS.md`)。

1. OPEN_ITEMS.mdヘッダ「最終更新」段落(`PM-CLOSEOUT-CONSOLIDATION-64`の
   直前の記録本文内)。訂正前: 「...一方でHOUSEHOLD-UNIFIED-FINAL-
   CANDIDATE-01自体は保険文0で成立したため採用の必要性が薄いと判断」。
   訂正後: 「HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01自体はPart B案1
   [cautionary_constrained]を**適用して**生成され保険文0[A2・B1Bとも]で
   成立したが、このREVIEW率上振れとの因果関係が未確定であり、Household
   記事1本[N=1]の成立だけでは一般採用の根拠として不足と判断してProduction
   採用を見送った」。
2. `OPEN_ITEMS.md`OPEN-135行、`PM-CLOSEOUT-CONSOLIDATION-64`追記(6)。
   訂正前: 「このため採用の必要性が薄いと判断しProduction採用を見送った」。
   訂正後: 「しかし(3)のREVIEW率上振れとの因果関係が未確定であり、
   Household記事1本(N=1)の成立だけでは一般採用(Production採用)の根拠
   として不足と判断し、Production採用を見送った」。

いずれも訂正箇所には「2026-09-10、PM-CLOSEOUT-CONSOLIDATION-67で...
訂正」という付記を残した(旧記述を削除するのではなく、誤りであった旨を
明示したうえで正しい記述へ置き換えた)。**正しい理解**: Household最終版
(`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`)はDiscovery保険文抑制Prompt
制約案(Part B案1、`cautionary_constrained`)を**適用して**生成された
(制約なしで保険文0が成立したのではない)。Production採用見送りの正しい
理由は、Trial-10で観測されたREVIEW率0/6→2/6上振れとの因果関係が未確定
であり、Household記事1本(N=1)の成立だけでは一般採用(Production採用)の
根拠として不足すると判断したためである。`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-64`エントリ本文(10176〜10198行付近)は元々
「Part B案1適用条件[cautionary_constrained]を用いて...成立した」
「以上を踏まえ...(c)見送りと判断した」という記述で、上記の正しい理解と
矛盾しておらず修正不要と確認した(誤った因果説明「制約なしでも保険文0で
成立した」「採用の必要性が薄い」は`OPEN_ITEMS.md`側にのみ残存していた)。

**Lane A-1 Discovery — 一般化確認Trial起票**: Discovery Focus Module
一般化確認Trial(N=1)をユーザーが確定した。テーマ「Why do towels
sometimes smell even after washing?(洗濯したのに、なぜタオルは臭う
ことがあるのか?)」(Householdと異なるテーマ)、A2/B1B。確認項目:
Discoveryらしさ/「へえ」があるか、Full StoryとPointの役割分離、Point
One/Twoの切り口、Point同士の多様性、Fact Safety、Ledger Deviation、
Point Value/Overlap、A2/B1B整合、不自然な保険文・説明書的表現、retry
挙動。**現時点ではDiscovery Focus ModuleのProduction採用は行わない。
N=1が良好なら次にProduction採用判断をユーザーへ提示する**。管理ID:
`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11`(並列実施中、本タスク
では触れていない)。`OPEN_ITEMS.md`OPEN-135行へ追記した。

**Lane A-2 News**: News再改善はLedgerのfact供給量/evidence allocationを
増やすことでHanshin型NewsのPoint Overlap・retry成功率を改善できるかの
検証を主軸として継続する。Hanshin型テーマでLedger拡充A/B Trial実施を
ユーザーが承認した(管理ID`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-
TRIAL-12`、並列実施中、本タスクでは触れていない)。Overlap threshold
0.40・Overlap Checker自体・retry構想・Point Role Planning・連続量評価の
低コスト分析も並行可とした。**矛盾統一**: `FAMILY-A-NEWS-STAGE4-STATUS-
REPORT-01_REPORT.md`8節がN-3(News Focus ModuleのProduction採用可否)・
N-4(CAR-T B1B`full_story_part1`再生成承認)を「Blocking」と分類した一方、
`docs/pm/ACTIVE_TASK.md`は「UDR-blocking: なし」としており、SSOT間で
分類が不整合だった。SSOT上の正しい分類は「`USER_DECISION_REQUIRED`
(ユーザー判断要)だが、現行の作業単位をblockしないため`UDR-deferred`
(未回答再掲対象)」である。同REPORTは記録物のため本文は修正せず、本
エントリで「REPORTの『Blocking』表記はSSOT上『deferred・未回答再掲対象』
へ統一」と記す。`OPEN_ITEMS.md`OPEN-135行へ反映した。

**恒久運用ルール新設(低コスト分析・Trialの自律実施)**: ¥0分析や大きな
費用を要しないTrialは、逐一ユーザー承認へ戻らずFable側で実施し結果まで
持ち込む運用を恒久ルール化した。小さなTrialごとに`USER_DECISION_REQUIRED`
化しない。ただしProduction仕様変更・QA/threshold変更・大きなQCD
(品質・コスト・納期)変更・複数の有力設計案が残る場合はユーザー判断へ
戻す。`docs/pm/PM_GOVERNANCE.md`11節「自明な修正の自律実施」の直後へ
新設小節「低コスト分析・Trialの自律実施」として追記した(既存のSTOP必須
6条件・8項目の遵守事項・Gatekeeper原則・Opus上限はいずれも変更しない)。

**Lane B 3V — Production Wiring Phase 1確定**: 3V(3声Voice方式)
Production Wiring Phase 1の確定事項をユーザーが決定した。segment命名=
`point_one/point_two/point_three`を基本採用。Voice 3=Schedarを3V正式
Voiceとして採用。Voice 3のfallback声は当面専用のものを設けず、使用不可
時は既存Human Review Lockへ委ねる。Comment 2/3文言はVoice数非依存の
汎用文言として整合させる。共有Audio Validation Gateは3Vに必要な
`point_three`系entryを最小追加する。既存2V(2声Voice方式)の挙動は変更
しない。**Phase 1の範囲はoffline regressionまでとし、Production
runtimeでの実記事生成は行わない**。管理ID`EDITORIAL-B-FAMILY-VOICES-3V-
PRODUCTION-WIRING-PHASE1-01`(並列実施中、本タスクでは触れていない)。

**Lane B — Phase 2・2V比較記事計画・4V DEFERRED再確認**: Phase 2
(Production runtime確認)は既存Trial記事(固定席テーマ等)を再利用せず、
新テーマ「Should schools replace some homework with more free time?
(学校は宿題の一部を減らして、子どもの自由時間を増やすべきか)」・
Voice=Student/Parent/Teacherで、記事→Support→AudioをProduction正式
経路で完成させユーザー試聴artifactを提示する計画を登録した(着手は
Phase 1完了後)。観測項目: 全文尺・Tension尺・Local Rewrite発生・
Tension再膨張・Analytical Leakage・Voice distinctness・Fact Checker
A' call数/search数/cost/latency・retry回数・Ledger Deviation・Audio
structural gate・最終的な聞きやすさ。2V比較記事N=1として「Should
supermarkets discount food more aggressively before it expires?
(スーパーは消費期限前の商品をもっと積極的に値引きすべきか)」・
Voice=Shopper/Store Managerを、Production正式経路で記事→Support→
Audio生成し、3Vと同じ主要指標を取得、試聴artifactを提示する計画を
登録した(目的: 2V/3Vの尺・修正負荷・QA負荷・音声体験の実測比較)。
4V(4声Voice方式)は2V/3V追加記事のユーザー試聴・評価完了まで明示的に
`DEFERRED`のまま維持することを再確認した。いずれも本タスク時点では
未着手(Phase 1完了待ち)。`OPEN_ITEMS.md`OPEN-120行・OPEN-132行へ
反映した。

**Dangling Reference Check**: 本タスクで新設した表現(「低コスト分析・
Trialの自律実施」小節、`UDR-deferred`という分類語)は、いずれも既存
SSOTの既存語彙(`docs/pm/PM_BRIEF.md`Status語彙の`USER_DECISION_REQUIRED`、
`docs/pm/ACTIVE_TASK.md`固定ヘッダの`UDR-deferred`フィールド[既存])の
組み合わせ・適用であり、未定義語の新規追加はない。新規管理ID
(`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11`・`FAMILY-A-NEWS-
STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12`・`EDITORIAL-B-FAMILY-VOICES-3V-
PRODUCTION-WIRING-PHASE1-01`)は並列稼働中のsonnet-worker側の管理IDで
あり、本タスクはそれらのSSOT登録のみを行った(実装・実行はしていない)。

**触れていないもの**: 並列稼働中3タスクの生成物(`er0XX_output/`配下の
新規ディレクトリ・新規REPORT・3V配線コード)、`docs/pm/ACTIVE_TASK.md`・
`docs/pm/RESULT_PACKET.md`(本タスク用に新規上書きするが本エントリの
Git対象外)、`CURRENT_SPEC.md`(配線完了後に別途更新予定、本タスクでは
未変更)。

**コード・Prompt・Production実装は一切変更していない**(SSOT反映のみ、
費用¥0)。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-67、2026-09-10ユーザー次アクション確定指示)。
Git操作: ファイル名指定で`git add`(`git add -A`不使用)、対象=
`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/PM_GOVERNANCE.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。1 commitで`origin/main`へpush。
並列タスクの生成物・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・
既存の未追跡ファイル群はいずれも本タスクでは触っていない(commit対象外)。

## PM-CLOSEOUT-CONSOLIDATION-68: Discovery Focus Module一般化確認
Trial-11(タオル臭テーマ)結果のSSOT反映+Git統合+モデルルーティングLOG保守

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-68)に基づき実施した。並列稼働中のsonnet-worker
2件(News Ledger拡充A/B Trial-12`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-
AB-TRIAL-12`、3V Production Wiring Phase 1`EDITORIAL-B-FAMILY-VOICES-3V-
PRODUCTION-WIRING-PHASE1-01`)とは独立(それらが`er0XX_output/`配下・
`er012_b_family_*.py`・`er003_v1_n3_01_assemble.py`・新規テスト・REPORTへ
書く生成物・変更は本タスクでは一切触っていない)。

**反映内容(Discovery Focus Module一般化確認Trial-11結果)**: Sonnetが
実行した`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11`
(テーマ「Why do towels sometimes smell even after washing?」、A2/B1B、
N=1)の結果を`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11_REPORT.md`
から転記した(推測で埋めていない)。**要旨**: Discovery Focus Module
Part A本体のみ(保険文抑制Prompt制約案[Part B案1]は不使用)、新規
Verified Fact Ledger(査読論文15件、CONFIRMEDのみ)を新規作成。A2/B1B各
1本とも最終status=OK、Point Overlap記事全体retryは両レベルとも0回、
保険文(regex検出)はA2/B1Bとも0件。B1BのみLedger Deviation MAJOR 2件を
検出したが、既存Local Rewrite機構(記事品質自動修正機構)が1cycle・
1attemptで両件解消し、human_review_requiredは0件だった。Fact Checkerは
A2=fact_verdict=PASS(unsupported_specific_claims 0件)、B1B=
fact_verdict=REVIEW_REQUIRED(3件、いずれも捏造ではなく精緻化余地の
指摘、Production既定方針どおりnon-blocking advisoryとして扱われ記事は
status=OKで完走)。cross_point_overlap(A2: 0.243/0.225、B1B:
0.244/0.222、いずれもflagged=False)はHousehold最終候補(A2: 0.196/
0.289、B1B: 0.183/0.25)と同程度の範囲。Directional Fact Precheckは
両レベルともoverall_status=DIRECTION_REVIEW_REQUIREDとなったが機械判定
できるconflictsは0件(non-blocking助言のみ、Household側とは測定条件
[Layer 1の有無]が異なるための見かけ上の差であり記事の質の差ではない)。
実測費用¥117.72(Ledger作成¥55.48+記事生成[A2+B1B合計]¥62.24、上限
¥150以内)。**Gate 1分類=VALIDATED相当(Trial範囲、N=1)。Production採用
[APPROVED_FOR_PRODUCTION]は行っていない**。次のN増し(追加テーマ2〜3件×
A2/B1B各N=2〜3程度)の要否・Production採用判断の提示時期はユーザー判断
待ち。**既知gap**: A2/B1Bの記事生成費用が実装上同一theme_tagでログされ
レベル別に分離できていない(合算のみ)。`JAPANESE_TITLES`辞書への登録は
Support/Audioを実施しなかったため未実施(OPEN-137の既知gapとは別件、
本Trialでは未発生・次回Support/Audio実施時に再発見込み)。`OPEN_ITEMS.md`
OPEN-135行・OPEN-137行へ反映した。

**モデルルーティングLOG保守**: `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`の
「Trial導入後の委任実績」表について、(1)Trial-11の暫定行を上記確定値
(Sonnet/MEDIUM、実測¥117.72、Fable差し戻し0回、STOP 0件)へ更新した。
(2)本タスク(PM-CLOSEOUT-CONSOLIDATION-68、Sonnet/LOW、¥0)の行を追加
した。(3)`MODEL-ROUTING-TRIAL-STATUS-REVIEW-01_REPORT.md`7節が指摘した
記録漏れを是正し、`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-
PLAN-01`(3V wiring影響分析、読み取り専用・LLM/TTS API呼び出しなし、
Sonnet/MEDIUM、¥0、2026-09-10)の行、および`MODEL-ROUTING-TRIAL-
STATUS-REVIEW-01`自体(Sonnet/LOW、¥0)の行を追記した。(4)「中間レビュー
実施記録」表に、同REPORT 6節が行った正式Closeout Trigger(6条件)との
照合結果を1エントリ追記した(出典=同REPORT 6節): 「Trial開始後20委任
以上」満たす(84件)、「Haiku 5件以上」未達(2件のみ)、「Sonnet 10件
以上」満たす(78件)、「Opus HIGH案件2件以上」満たす(4件)、
「Production wiring到達2件以上+手戻り観測」不確実(ログ上で明確な2件
該当を特定不可)、「規律違反等が記録済み」満たす、「モデル別サンプル
非偏在」未達方向(Haiku 2件・Opus 4件・Sonnet 78件は明確に偏っている)。
**6条件中2条件(Haiku 5件以上、サンプル非偏在)が未達、1条件
(Production wiring到達2件+手戻り観測)が不確実であり、正式Closeout
判定はまだ行わない(観測継続)**という同REPORTの結論をそのまま転記した。
本タスク自体は正式Closeout判定を行っていない(LOG保守・記録反映のみ)。

**Dangling Reference Check**: 本タスクで新設した用語はない(既存SSOT
[`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11_REPORT.md`・
`MODEL-ROUTING-TRIAL-STATUS-REVIEW-01_REPORT.md`・`EDITORIAL-B-FAMILY-
VOICES-3V-PRODUCTION-WIRING-PLAN-01_REPORT.md`]からの転記のみ)。

**触れていないもの**: 並列稼働中2タスク(News Ledger拡充Trial-12、3V
Production Wiring Phase 1)の生成物・script・REPORT、`CURRENT_SPEC.md`
(変更なし)、`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`
(本タスク用に新規上書きするが本エントリのGit対象外)。

**コード・Prompt・Production実装は一切変更していない**(SSOT反映のみ、
費用¥0)。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-68、Discovery一般化Trial-11結果のSSOT反映+
Git統合+モデルルーティングLOG保守)。Git操作: ファイル名指定で`git add`
(`git add -A`不使用)、対象=`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-
TRIAL-11_REPORT.md`・`er011_discovery_generalization_towels_trial_11_run.py`・
`er011_output/discovery_generalization_towels_trial_11/`配下のjson/md/
jsonl/txt/html(音声バイナリなし)・`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。1 commitで`origin/main`へpush。
並列タスク2件の生成物・`docs/pm/ACTIVE_TASK.md`・`docs/pm/
RESULT_PACKET.md`・既存の未追跡ファイル群はいずれも本タスクでは
触っていない(commit対象外)。

## PM-CLOSEOUT-CONSOLIDATION-69: 3V(3声Voice方式)Production配線Phase 1
完了(実装+offline regression PASS)のGit統合+Phase 2前提不一致の記録

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-69)に基づき実施した。並列稼働中の
`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12`
(`er011_output/news_ledger_enrichment_ab_trial_12/`・同名script・同名
REPORT)、`PM-TOKEN-EFFICIENCY-DIAGNOSIS-01`(読み取り専用、
`PM-TOKEN-EFFICIENCY-DIAGNOSIS-01_REPORT.md`のみ)の生成物は一切
stageしていない(`git status --short`で確認、`git add -A`不使用)。

**反映内容(3V Production Wiring Phase 1完了)**: 出典
`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01_REPORT.md`
1〜12節から転記した(推測で埋めていない)。**要旨**: Phase 1実装(¥0)が
完了した。registryへ`voice_c`(Voice 3=Schedar、fallbackキーなし)・
3V用`point_one/two/three` 16 segment required_structure・`EDITORIAL_
TYPES["b_family_voices"]["b1_3v"]`を新規追加(2V経路は無変更のまま分岐、
byte単位一致を単体テストで固定)。`run_tts_3v()`をTrial実装から正式
移設(narration_dir引数化)。B-Family Production runnerへ`level="b1_3v"`
分岐(`main_b1_3v()`ほか新規関数群)を追加。共有`er003_v1_n3_01_
assemble.py`の`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]`へ
`point_three_heading`を1エントリのみ追加。Comment 2/3の登録テキスト
(`VOICES_COMMENT_2_ROLE`/`_3_ROLE`)をVoice数非依存の汎用文言へ最小限
書き換えた(2026-09-10ユーザー決定に基づく、**Promptの実質変更のため
人間レビューを推奨**、意味変更が避けられない箇所[タイトル行「どちらが
正しいか」]はあえて変更していない)。新規offline test 36件(11クラス)
全PASS、Trial実装(`er012_editorial_b_voices_3v_audio_trial_01.py`等)
へのモジュールレベルimport依存0件をAST解析で機械確認した。

**Fable修正指示1回目**: 初回報告時点でSTOP条件(a)相当の新規regression
failure 1件(既存pinテスト`test_existing_b1_and_standard_a2_entries_
unchanged`が旧8要素タプルを厳密一致でpinしていたため、`point_three_
heading`追加で不一致)が判明した。ユーザー正式決定(共有Audio Gateへ
3Vに必要な`point_three`系entryを最小追加)に基づき、該当テスト1
メソッドのみを「旧8要素が順序どおり部分集合として含まれる」+「追加は
`point_three_heading`1件のみ」の2アサーションへ書き直した(他ファイル・
他テストは無変更)。修正後のregression再実行結果: `collected=2289
passed=2286 failed=3 errors=0 skipped=0`。failed 3件はいずれも
`er003_test_p2j_investigate.py`の既知failure(帳簿的カウント照合、
テスト総数増加のたびに失敗する設計上の既知事象、本タスクと無関係)の
みで、**新規failureはゼロ**(STOP条件(a)は解消)。API呼び出しは0回
(費用¥0)。

**`PRODUCTION_WIRED`は未宣言**。`docs/pm/PM_GOVERNANCE.md`のGate 3
各項目のうち、(a)Production正式経路はコード実装済みだが実運用未実施、
(d)Production runtimeでの実発火・(f)runtime evidence・(g)実際の
model_id/routing確認はいずれも**未達**(Phase 2待ち)、(i)(j)(k)SSOT
本文反映は本エントリで一部達成するが`CURRENT_SPEC.md`はPhase 3で更新
予定、(l)Git反映は本エントリのcommitで達成、(m)approved specとの挙動
一致は構造レベルのみ部分達成(runtime実行後に最終確認)。

**Phase 2前提の重大な不一致を新規発見**: Fable修正指示1回目で実施した
調査(読み取り専用、コード読解のみ、API呼び出しなし)により、現行
Production runner(2V B1/A2)は既存承認済み記事(`ARTICLE_PATH`/
`A2_SOURCE_DIR`固定パス)を**読み取るだけ**であり、Research(Web検索)・
Ledger作成・Writer(記事生成)・Key Phrase選定のいずれもこの経路の
コード内に存在しないことが判明した(`prepare()`docstring・実装で
直接確認)。2026-09-08の「B-Family Phase 1の`PRODUCTION_WIRED`確定」
(`DECISION_LOG.md``PM-CLOSEOUT-CONSOLIDATION-14`)は、この「既存承認
済み記事の音声化のみ」の範囲を指すものであり、**「新テーマからの記事
生成」を含む`PRODUCTION_WIRED`宣言ではないことをコード・SSOT両面で
確認した(重要な範囲確認)**。3V Writer(3人物Voice本文生成)の
Production経路は存在せず、現状は121KBのTrialスクリプト
(`er012_editorial_b_voices_3v_person_voice_trial_02.py`、関数30個)に
のみ存在する。Key Phrase選定は2V/3Vいずれも既存Trial出力からのhash
照合再利用関数(`reuse_key_phrases()`/`reuse_key_phrases_3v()`)のみで、
新規記事に対する選定ロジック自体はB-Family runner内に存在しない
(fail-closed設計、hash不一致時にRuntimeError)。Ledger Deviation
Check・Tension尺/Analytical Leakage/Voice distinctnessの観測ログ出力も
Production経路には一切配線されていない。**この結果、2V比較記事も現行
Production経路では新テーマから完走できないことが判明した**(2Vが既に
`PRODUCTION_WIRED`だから新テーマでもすぐ通るという前提は誤り)。

**選択肢整理(ユーザー判断待ち、V-2)**: (A)Phase 1b(Writer/Ledger/Key
Phrase glue配線+offline test、見込み2〜3セッション・¥0)→Phase 2新
テーマ3V記事1本(見込み¥150〜250)→2V比較記事1本(見込み¥100〜180)
(ユーザー決定に最も忠実)。(B)Phase 2は既存Trial記事再利用でruntime
evidenceのみ先に取得(¥90〜150、低リスクだが2026-09-10ユーザー決定
[新テーマ・Production正式経路までの完走]と不一致と判明)。(C)Key
Phrase選定glueのみ既存Trial出力hash再利用のまま新テーマへ暫定適用する
部分縮小案は、reuse関数がfail-closed設計(hash不一致時にRuntimeError)
のため技術的に不成立。Sonnetは(A)を推奨するが、着手前にユーザー承認を
得ることを推奨する(本タスクでは調査のみで実装はしていない)。

**未回答ユーザー判断待ち(本エントリで新規追加)**: V-1(Comment 2/3
汎用文言の人間レビュー・承認)、V-2(Phase 2の進め方、選択肢A/B/Cの
いずれか)。いずれも本タスクでは決定していない。

**Dangling Reference Check**: 本タスクで新設した用語はない(出典
REPORTからの転記のみ)。

**触れていないもの**: 並列稼働中2タスク(News Ledger拡充Trial-12、
Token効率診断PM-TOKEN-EFFICIENCY-DIAGNOSIS-01)の生成物・script・
REPORT、`CURRENT_SPEC.md`(本タスクでは変更しない、Phase 3で更新)。

**コード・Prompt・Production実装は本タスク(Git統合)では一切変更して
いない**(コード変更自体は先行するSonnet実装タスクで完了済み、本タスク
はそのGit反映+SSOT記録のみ、追加の費用発生なし)。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-69、3V Production配線Phase 1完了のGit統合+
SSOT記録+Phase 2前提不一致の記録)。Git操作: ファイル名指定で`git add`
(`git add -A`不使用)、対象=`er012_b_family_editorial_type_registry_
01.py`・`er012_b_family_voices_production_01.py`・`er012_b_family_
production_runner_01.py`・`er003_v1_n3_01_assemble.py`・
`er012_editorial_b_family_voices_3v_production_wiring_phase1_test_
01.py`(新規)・`er012_editorial_b_family_production_phase1_test_01.py`
(pin修正)・`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-
01_REPORT.md`・`er012_output/editorial_b_family_voices_3v_production_
wiring_phase1_01/`配下のjson/txt/md・`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`。1 commitで`origin/main`へpush。
並列タスク2件の生成物・`docs/pm/ACTIVE_TASK.md`・`docs/pm/
RESULT_PACKET.md`・既存の未追跡ファイル群はいずれも本タスクでは
触っていない(commit対象外)。

## PM-CLOSEOUT-CONSOLIDATION-70: 2026-09-10ユーザー回答・追加指示10項目の
SSOT反映+恒久ルール追加+haiku-worker新設+Token効率診断REPORTのGit記録

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-70)に基づき実施した。並列稼働中の5件
(Trial-11タオル記事のSupport→Audio[`FAMILY-A-DISCOVERY-GENERALIZATION-
TOWELS-TRIAL-11-AUDIO-01`、`er011_output/discovery_generalization_
towels_trial_11/`]、CAR-T B1B再生成[`FAMILY-A-NEWS-STAGE3-NEW-THEME-
LEDGER-TRIAL-09-REGEN-01`]、OPEN-140 Ledger ID是正
[`OPEN-140-THEME2-LEDGER-ID-CONSISTENCY-FIX-01`]、News Trial-12継続、
Opus L2レビュー[Trial-11])の生成物は一切stageしていない(`git status
--short`で確認、`git add -A`不使用)。

**反映内容(ユーザー2026-09-10確定指示10項目)**:

1. **Discovery Trial-11(D-1)**: N増し(追加テーマ2〜3件×N=2〜3程度)には
   進まず、まず記事→Support→Audio→試聴artifactまで完成させ(並列実施中、
   管理ID`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01`)、
   ユーザー試聴後にN増し可否・Production採用判断を行う。Focus Module
   自体のProduction採用判断も試聴・評価前には行わない。OPEN-135行へ
   反映。
2. **Discovery保険文運用(A-3)**: 保険文抑制Prompt制約案(Part B案1、
   `cautionary_constrained`)はProduction不採用のまま維持(既決)。Part A
   単独運用で取扱説明書的・保険文的表現が出た場合は、Human Reviewで
   目視修正したうえで発生率を観測・記録する(追加Prompt対策Trialは
   現時点不要)。OPEN-135行・`CURRENT_SPEC.md`Discovery/Why節(新規表行
   「保険文運用注記(2026-09-10)」、`DECIDED`(運用方針、仕様ではない))
   へ反映。
3. **News Focus Module NG率報告(B-5関連)**: 報告されたNG率「3/6」は
   過去のHanshin(阪神)テーマでのFocus Module+Point Role hint結果の
   既存の再掲であり、News Ledger拡充A/B Trial-12(進行中、別Trial)の
   新規結果ではないことを確認した。報告時に「新規更新/過去結果の再掲/
   進行中で未結果」を必ず明示する恒久ルールを`docs/pm/PM_GOVERNANCE.md`
   9-4節「更新種別の明示ルール」として新設(既存12-4のフル再掲ルールと
   接続)。OPEN-135行へ反映。
4. **CAR-T記事(Trial-09)B1B `full_story_part1`(B-6)**: 承認済み
   再生成経路(既存segment再生成経路)で1回のみ再生成可、通らなければ
   STOPしユーザー確認する(並列実施中、管理ID`FAMILY-A-NEWS-STAGE3-
   NEW-THEME-LEDGER-TRIAL-09-REGEN-01`)。OPEN-135行へ反映。
5. **新規記事テーマ選定ルール(恒久)**: News/Discovery/Voices他を問わず
   新規記事(使い捨てTrialではなく最終版候補前提)のテーマをFable/
   Claude側で勝手に決めない。ユーザー価値判断(実際に聞きたいか/一般
   ユーザーの関心/専門的すぎないか/最終公開候補として成立するか)が
   必要なため、Fableが複数テーマ候補を英語・日本語・短い選定理由付きで
   提示しユーザーが選択してから生成する(例外: ユーザーが選定自体を
   明示的に委ねた場合のみ)。既存記事のregen/retry/Local Rewrite/
   segment再生成は対象外。`docs/pm/PM_GOVERNANCE.md`新設「13. 新規記事
   テーマ選定ルール」・`docs/pm/PM_BRIEF.md`参照追記・`CLAUDE.md`1行・
   PM Closeout Mandatory Check項目19へ反映(経緯: CAR-Tテーマ[検証には
   有用だが最終版になりにくいテーマの例]を受けた決定)。
6. **OPEN-140 Theme2 Ledger ID不整合(B-10)**: 単純なID整合修正で意味・
   Fact対応関係が明確な場合は自律修正可、不明・意味が変わりうる場合は
   STOPする方針をOPEN-140行へ記載(並列実施中、管理ID
   `OPEN-140-THEME2-LEDGER-ID-CONSISTENCY-FIX-01`、結果は別タスクで
   追って反映)。
7. **OPEN-139遡及QA(B-11)**: 量産段階に近づいた時点でまとめて判断する
   方針でDEFERを維持する。現時点で新しい恒久方針は作らない。OPEN-139行
   へ反映。
8. **haiku-worker新設(M-1)**: `.claude/agents/haiku-worker.md`を新設した
   (frontmatter: name=haiku-worker、model=haiku、tools=Read/Grep/Glob
   [Bashは付与しない]、description=Sonnet不要のread-only定型処理限定)。
   目的は件数増ではなく、判断を含まない定型集計・artifact存在確認・
   費用集計・固定チェックリスト確認のみ。SSOT編集・Git操作・API支出・
   Gate判断・Production変更・QA判定は禁止と明記した。`.claude/agents/
   sandwich-pm.md`の委任先制限をsonnet-worker/opus-consultant/
   haiku-workerの3つへ更新し、haiku-workerの用途限定を明記した。
   `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`のL0定義(読み取り専用・API支出
   なし・SSOT編集なし・Git操作なし・Production変更なし・Gate判断なし・
   定型artifact限定)と整合していることを確認した(矛盾なし)。**注記**:
   新Agent定義は次回`claude --agent sandwich-pm`起動時から有効(現行
   セッションでは未ロード)。`docs/pm/PM_GOVERNANCE.md`1節・
   `docs/pm/PM_BRIEF.md`へも反映。
9. **Opus L2レビュー投入(M-2)**: 3案件(3V Phase 1差分/Discovery
   Trial-11 N=1解釈/News Trial-12 A/B解釈)へのL2設計レビュー投入を
   ユーザーが承認した。原則「重要論点にスコープを絞る」(全文再レビュー
   はしない、Opus自身の追加探索は妨げない)。目的はOpus利用自体の増加
   ではなく高リスク判断・因果解釈・Production差分の見落とし・手戻り
   削減。`docs/pm/PM_GOVERNANCE.md`11節へ「L2事前レビューの運用」を
   新設し、Opus起動条件(従来のL3=Sonnet差し戻し後の診断1回)に「ユーザー
   承認に基づくL2事前レビュー(論点限定)」を追加した。`.claude/agents/
   sandwich-pm.md`手順7/8の記述もあわせて整合させた(L2はユーザー承認
   済み案件に限る、L3診断は従来どおり)。
10. **共通PMルール**: 自明な修正は自律/仕様判断はユーザー/新テーマは
    承認前に決めない/Trial良好≠Production採用/`APPROVED_FOR_PRODUCTION`
    は`PRODUCTION_WIRED`まで追跡/UDR未報告放置禁止/過去再掲と新結果の
    区別/報告可能単位から即時報告/未回答はフル再掲、の9項目を既存SSOT
    (`docs/pm/PM_GOVERNANCE.md`1節・Gate 1〜3・9節・12節)で確認した
    ところ、大半は既存記述で充足済みと確認できた。不足していたのは
    「新テーマは承認前に決めない」(→13節新設、上記5)と「過去再掲と
    新結果の区別」(→9-4節新設、上記3)の2点のみで、他は重複記載を
    避けて追記しなかった。

**Token効率運用の即時反映(`PM-TOKEN-EFFICIENCY-DIAGNOSIS-01_REPORT.md`
診断結果)**: 同REPORT(読み取り専用診断、Sonnet委任、¥0)が提示した
即時実施可の運用改善5件(Git記録専用委任の軽量化/同モデル・同性質の
REPORT編纂→SSOT反映の連続実施/回帰実行`--pattern`反復+Production
wiring前の最終1回は全件/Discovery・News Ledgerの再利用標準化+バッチ化/
REPORT定型節の半機械化)を`docs/pm/PM_GOVERNANCE.md`11節へ「Token効率
運用(2026-09-10)」として記録した。ユーザー判断待ちの4件(T-1: 巨大単一
行の記録様式改善、T-2: Fableへの限定的Git操作権限付与、T-3: Ledger研究の
検索回数上限/reasoning effort調整、T-4: 利用量連動節約モード)は未決定の
まま`docs/pm/ACTIVE_TASK.md`の未回答報告へ維持した。

**Dangling Reference Check**: `CURRENT_SPEC.md`Discovery/Why節へ追加した
運用注記行は、保険文抑制Prompt制約案(Part B案1)を「Production不採用の
まま」と明記しており、未承認仕様が採用済みであるかのような記述は含まない
ことを確認した。新設した9-4節・13節・haiku-worker定義はいずれも既存の
承認済み運用原則(9-1/9-2/12節・Gate 1〜3・11節上限)と矛盾しないことを
確認した。

**触れていないもの**: 並列稼働中5件(上記)の生成物・script・REPORT。
コード・Prompt・Production実装は一切変更していない(SSOT・PM運用文書
反映のみ、追加API費用なし)。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-70、2026-09-10ユーザー回答・追加指示10項目の
SSOT反映+恒久ルール追加+haiku-worker新設+Token効率診断REPORTのGit記録)。
Git操作: ファイル名指定で`git add`(`git add -A`不使用)、対象=
`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/PM_GOVERNANCE.md`・
`docs/pm/PM_BRIEF.md`・`CLAUDE.md`・`.claude/agents/haiku-worker.md`
(新規)・`.claude/agents/sandwich-pm.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`・
`PM-TOKEN-EFFICIENCY-DIAGNOSIS-01_REPORT.md`。1 commitで`origin/main`へ
push。並列稼働中5件の生成物・`docs/pm/ACTIVE_TASK.md`・`docs/pm/
RESULT_PACKET.md`・既存の未追跡ファイル群はいずれも本タスクでは触って
いない(commit対象外)。

## PM-CLOSEOUT-CONSOLIDATION-71: News Trial-12完走+OPEN-140是正完了+CAR-T
再生成PASS+Discovery Opus L2レビュー記録(新規OPEN-141)+CONSOLIDATION-70後
のユーザー追加確定のSSOT反映

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-71)に基づき実施した。並列稼働中の4件
(Trial-11タオル記事のSupport→Audio、Opus L2レビュー[3V Phase 1差分]、
T-2/T-3精査[`PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md`]、TTS
時間依存性調査[`TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md`])
の生成物は一切stageしていない(`git status --short`で確認、`git add -A`
不使用)。

**反映内容**:

1. **News Ledger拡充A/B Trial-12(新規更新)**: 出典
   `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md`
   「## 継続実行(Fable継続指示1回目)」節。N=12(条件A=現行Hanshin Ledger
   fact5件、条件B=拡充Ledger fact12件、各A2×3/B1B×3)完走。最終NG率
   条件A 83.3%(5/6)→条件B 33.3%(2/6)、lexical overlap起因NG 4/6→1/6、
   retry平均1.833→0.833、Point対Full Story overlap平均0.4497→0.370、
   anchor衝突平均1.5→0.0、fact利用率93.3%→27.8%。Fisher正確検定
   p=0.242(有意でない)。条件BのNG2件中1件はOverlap解消後のFact
   Checker FAIL(条件A側には出現しなかった新NGモード)。pooled NG群
   (n=7)/OK群(n=5)のGate指標比較差0.156・Welch p=0.0039・Mann-Whitney
   p=0.0073(条件操作とNG/OKが交絡、因果の強い主張は不可)。
   cross_point_overlapは条件差・NG/OK差とも不明瞭(p=0.669)。¥0並行
   分析: (a)閾値0.40は依然判断材料不足、(b)lexical表層よりanchor衝突数
   (構造指標)が操作効果を鋭敏に捉える、(c)fact供給増でOverlap由来retry
   依存は下がるがFact Checker起因の新NGモードが生じ得る、(d)連続量評価は
   「Point対Full Story overlap」限定の支持材料。費用累計¥248.4(Ledger
   研究¥148.6+記事¥99.8)。Gate1=`VALIDATED(Trial)`。OPEN_ITEMS.md
   OPEN-135行(News節)へ反映。ユーザー判断待ち: 拡充fact(FACT-08〜14)の
   Production Ledger採用可否(URL人手再検証前提)、UDR候補a(主軸を論点H
   へ)、UDR候補d(連続量評価の正式検討)。
2. **OPEN-140 Theme2 Ledger ID不整合是正(新規更新、CLOSED)**: 出典
   `OPEN-140-THEME2-LEDGER-ID-CONSISTENCY-FIX-01_REPORT.md`。
   `theme2_verified_fact_ledger_CORRECTED_trial12.txt`「注記3」の引用
   番号4箇所(F-211→F-206、F-206→F-205、F-205→F-204、F-208→F-202)を、
   引用文言・数値がFact一覧本文と完全一致することを根拠に一意に修正した
   (Fact本体・意味は無変更、対応表`er011_output/open140_theme2_ledger_
   id_fix_01/id_mapping.json`)。既存完成音声(Theme2 rerun_04)は当時の
   `prompt.txt`(不変)を使用しており遡及影響なし。ユーザー承認条件
   (B-10、意味が明確なら自律修正)を満たすため、OPEN_ITEMS.md OPEN-140行
   を**CLOSED**へ更新した。
3. **CAR-T記事(Trial-09)B1B `full_story_part1`承認済み再生成1回PASS
   (新規更新)**: 出典`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-
   TRIAL-09_REPORT.md`「## REGEN-01」節。3回連続NGの原因はTTSが"a
   report on"を一貫して読み落としたこと。`approve_regenerate()`経由で
   同一関数・同一引数で1回のみ再生成→ASR NORMALIZED_MATCH→Assembly
   PASS→Audio Validation Gate PASS→player生成完了(費用¥4.20実測)。旧
   wavは`full_story_part1_original.wav`として退避。Trial-09全体の
   Statusは`VALIDATED(Trial)`のまま(Gate1分類変更なし)、CAR-Tテーマは
   Production採用候補として提示しない(既存決定を維持、最終版になり
   にくいテーマ)。3回NG後の4回目PASSという時間依存性は別途read-only
   調査中(`TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01`、1件で結論
   しない、retry仕様変更なし)。OPEN_ITEMS.md OPEN-135行(News節、N-4
   クローズ)へ反映。
4. **Opus L2レビュー(Discovery Trial-11 N=1解釈)所見の記録(新規更新)**:
   Opus(opus-consultant、読み取り専用)から受領した全文を一字一句その
   まま新規Report`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-
   OPUS-L2-REVIEW-01_REPORT.md`として保存した(要約せず全文コピー)。
   要旨: (論点1)保険文0件は題材依存(争点となる消費者向けガイド記述が
   タオルLedgerに不在)であり、Part A単独効果の証拠にはできない。逆に
   REVIEW率はPart A単独の過去実測0/6に対しTrial-11 B1Bは1/2で悪化側。
   対照アーム(baseline)がなくPart A単独の寄与を差分として測れていない。
   (論点2)B1B Ledger Deviation MAJOR2件の自動解消は事実面は妥当だが、
   `er003_v1_n3_01_articles_generate.py`の実行順(Evidence Compression
   →Fact Checker→Ledger Deviation→Local Rewrite→Deviation再チェック)
   により、**Local Rewrite後の本文はFact Checker・Point Overlap QA・
   Point Value QA・Evidence Compressionのいずれも再通過しない構造的
   盲点**が全Editorial Type共通で存在する。(論点3)Fact Checker
   advisory3件中1件はLocal Rewriteで置換済みの文へのstale指摘、残り2件
   (柔軟剤の無条件断定・"prewash groups"指示対象不明)は公開前修正推奨。
   (論点4)A2 294語は既存Part A分布の中央で問題ではない、B1B 419語が
   soft上限420語に1語差という点の方が優先度が高い。(論点5)次のN増しに
   は対照アーム・争点テーマ・異型テーマが必須、36本≈¥1,100〜1,300見込み。
   OPEN_ITEMS.md OPEN-135行(Discovery節)へ要旨反映。**新規OPEN-141を
   起票**: Local Rewrite後のQA非再通過という構造的盲点は仕様変更を伴う
   ためUSER_DECISION_REQUIRED(起票のみ・実装なし)。
5. **CONSOLIDATION-70後にユーザーが追加確定した事項(2026-09-10)**:
   T-1(`OPEN_ITEMS.md`等の巨大単一行の記録様式改善)=条件付き実施承認
   (条件: 内容・Status・履歴を欠落させない/意味不変/構造整理のみ/
   参照性・検索性を悪化させない/削減効果を記録、実施は別タスク)。
   T-2(Fableへの限定的Git操作権限付与)・T-3(News/Discovery Ledger
   検索回数上限・reasoning effort調整)=現時点不実施、精査報告を実行中
   (`PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md`)。T-4(利用量
   連動節約モード新設)=保留。**V-2**(3V Phase 2の進め方)=選択肢A
   (Phase 1b→新テーマ3V記事→2V比較記事)を承認。Phase 1bの定義=「既承認
   3V仕様をProduction正式初回経路で記事生成できるようにする不足配線
   のみ(Writer/Ledger/Key Phrase選定等)」。STOP条件=3V専用の新Writer
   ルール/Ledger意味変更/3V専用の新Key Phrase仕様/新QA基準/新retry・
   fallback仕様/その他未承認の意味変更が必要と判明した場合。Phase 1b
   着手前またはcommit前にOpus L2レビュー(Production core差分・2V
   regression・Dangling Reference限定)を実施する。**V-1**(Comment 2/3
   汎用文言)=2V/3V両方に適用する形で承認(条件: 2V既存意味不変/Voice数
   非依存/3V前提表現なし、commit済み差分と承認内容の一致確認+test実施
   が前提)。OPEN_ITEMS.md OPEN-120行・OPEN-135行へ反映。Phase 1b・新
   テーマ3V記事・2V比較記事の着手は本タスクでは行わず、別タスクで実施
   する。

**Dangling Reference Check**: OPEN-140行の`CLOSED`表記は、既存完成音声
(Theme2 rerun_04)が当時の`prompt.txt`(不変)を使用し遡及影響がないことを
根拠にしており、未検証のまま完了扱いにしていないことを確認した。新規
OPEN-141はUSER_DECISION_REQUIRED(起票のみ)であり、Production仕様が
無断で変更されたかのような記述は含まないことを確認した。OPEN-120行の
V-1/V-2追記は、Phase 1b・新テーマ3V記事・2V比較記事のいずれも本タスク
では未着手であることを明記した。

**触れていないもの**: 並列稼働中4件(上記)の生成物・script・REPORT。
コード・Prompt・Production実装は一切変更していない(SSOT反映のみ、
追加API費用なし、本タスク自体の費用¥0)。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-CLOSEOUT-CONSOLIDATION-71)。出典REPORT: `FAMILY-A-NEWS-STAGE4-
LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md`・`OPEN-140-THEME2-LEDGER-ID-
CONSISTENCY-FIX-01_REPORT.md`・`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-
TRIAL-09_REPORT.md`・`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-
TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md`(新規)。Git操作: ファイル名指定で
`git add`(`git add -A`不使用)、対象=`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`・`FAMILY-A-NEWS-STAGE4-LEDGER-
ENRICHMENT-AB-TRIAL-12_REPORT.md`・`er011_news_ledger_enrichment_ab_
trial_12_run.py`・`er011_output/news_ledger_enrichment_ab_trial_12/`
配下json/md/jsonl/txt・`OPEN-140-THEME2-LEDGER-ID-CONSISTENCY-FIX-01_
REPORT.md`・`er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/
research/theme2_verified_fact_ledger_CORRECTED_trial12.txt`・
`er011_output/open140_theme2_ledger_id_fix_01/id_mapping.json`・
`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09_REPORT.md`・
`er011_news_stage3_new_theme_ledger_trial_09_b1b_regen01_full_story_
part1.py`・`er011_output/news_stage3_new_theme_ledger_trial_09_b1b_
full/`配下のjson/html/txt(wav/mp3除外)・`FAMILY-A-DISCOVERY-
GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md`。1 commit
で`origin/main`へpush。並列稼働中4件の生成物・`docs/pm/ACTIVE_TASK.md`・
`docs/pm/RESULT_PACKET.md`・既存の未追跡ファイル群はいずれも本タスク
では触っていない(commit対象外)。

## PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01: OPEN_ITEMS.md巨大単一行の構造分割(内容不変)

Sonnet(sonnet-worker)が2026-09-10、Fable(PM)からの委任(管理ID
PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01)に基づき、ユーザー承認
(2026-09-10、T-1、条件: 内容・Status・履歴を欠落させない/SSOTの意味を
変えない/構造整理のみ/参照性・検索性を悪化させない/削減効果を記録)の
もとで実施した。並列稼働中の4件(3V Phase 1修正+Phase 1b、Opus L2
[Trial-12読取]、Discovery Trial-11タオルAudio、TTS retryモニタリング)の
生成物・SSOTは一切触れていない。

**方式**: `OPEN_ITEMS.md`の各行(テーブル6列: ID/内容/状態/種類/
Blocking/次Action)のうち、いずれかの列が1,800文字を超える行を対象に、
その列の中から日付/管理ID単位の追記境界(`**YYYY-MM-DD追記(ID)**:`型・
`。YYYY-MM-DD(ID`型のいずれか)を機械検出し、**最新の1エントリのみを
`OPEN_ITEMS.md`本体に残し、それより前の全エントリを原文のまま
`OPEN_ITEMS_HISTORY.md`(新規、root直下)へ移動**した。要約・言い換えは
一切行っていない(切り貼りのみ)。境界が見つからない列は文末("。")境界で
機械分割、それも無ければ変更なし。ヘッダの「最終更新」(最新1件、
2026-09-10付、3,094文字)は本体に残し、それより古い「直前の記録」
「その前の記録」「さらに前の記録」の連鎖(2026-09-10付CONSOLIDATION-70
から2026-08-29付の旧ER-008以前まで、合計35,384+11,667文字相当)は
`OPEN_ITEMS_HISTORY.md`の`## HEADER_HISTORY`節へ原文のまま移動した。
対象行(3,000文字超)は25行: OPEN-100/103/107/108/110/111/64/65/66/68/
112/113/116/117/119/120/121/122/123/129/131/132/134/135/138。各行末尾に
「履歴全文: `OPEN_ITEMS_HISTORY.md#OPEN-XXX`」を付記した。両ファイル
冒頭に、管理場所は引き続き`OPEN_ITEMS.md`のみであり`OPEN_ITEMS_
HISTORY.md`は別の管理場所ではない旨を明記した。

**事前調査**: `*.py`をGrepし、`OPEN_ITEMS.md`をプログラムで解析する
コードが存在しないこと(コメント中の参照14件のみ)を確認済み、分割で
既存コードが壊れるリスクはない。

**検証(決定論的、`er011_open_items_restructure_verify_01.py`)**: git
HEAD時点(restructure前)の`OPEN_ITEMS.md`を基準に、(1) 25行それぞれの
分割対象セルについて「新本体の要約セル+`OPEN_ITEMS_HISTORY.md`の対応
節」を連結した文字列が、空白・改行の正規化後に元のセルと完全一致する
ことを25行全件で確認(25/25一致、不一致0件)、(2) ヘッダの`HEADER_
HISTORY`節が元のlines 66-306と完全一致することを確認、(3) 元ファイルの
テーブル行数(`| OPEN-`開始行、143件)が新本体でも143件で一致(行の
欠落・重複・混入なし)、(4) 管理ID(`[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}`
形式)1,154件・`OPEN-\d+`484件・日付359件・URL12件・ファイルパス
(拡張子付きbacktick引用)554件のいずれも、元ファイルと(新本体+新
HISTORY、追加した構造用の定型文を除外)で完全一致。結果は
`er011_output/open_items_restructure_01/verify_result.json`
(`ALL_PASS: true`)・`manifest.json`に保存。

**参照性確認**: `OPEN-135`・`USER_DECISION_REQUIRED`・`3V`・
`Fact Checker A'`のいずれも、分割後も`OPEN_ITEMS.md`側(11/18/10/2件)・
`OPEN_ITEMS_HISTORY.md`側(33/94/50/9件)の両方でヒットし、`OPEN_ITEMS.
md`側の要約行だけで各項目の現在Statusが判別できることを目視確認した。

**削減効果**(文字数、換算token=文字数/2.2の粗い概算): `OPEN_ITEMS.md`
本体は418,461文字(約190,210 token)→182,340文字(約82,882 token、
-56.4%)。上位4行(OPEN-120/112/135/121)合計は120,187文字→11,434文字
(-90.5%)。`OPEN-135`行単独は27,110文字(約12,323 token)→3,941文字
(約1,791 token、-85.5%)。`OPEN_ITEMS_HISTORY.md`(新規)は239,829文字。

**SSOT参照更新**: `docs/pm/PM_BRIEF.md`「参照順序」・
`docs/pm/PM_GOVERNANCE.md`冒頭・`CLAUDE.md`のSSOT列挙へ、
`OPEN_ITEMS_HISTORY.md`が`OPEN_ITEMS.md`各行の切り出し先(別の管理場所
ではない)である旨を各1〜2行追記した。`docs/pm/MODEL_ROUTING_TRIAL_
LOG.md`へ本タスク行(Sonnet/MEDIUM、¥0)を追加した。

**触れていないもの**: `CURRENT_SPEC.md`・並列稼働中4件の生成物・
`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`。コード・Prompt・
Production実装の変更はゼロ(構造整理のみ、追加API費用¥0)。

**根拠**: Fable(PM)からの委任(2026-09-10、管理ID
PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01)。Git操作: ファイル
名指定で`git add`(`git add -A`不使用)、対象=`OPEN_ITEMS.md`・
`OPEN_ITEMS_HISTORY.md`(新規)・`DECISION_LOG.md`・`docs/pm/PM_BRIEF.md`・
`docs/pm/PM_GOVERNANCE.md`・`CLAUDE.md`・`docs/pm/MODEL_ROUTING_TRIAL_
LOG.md`・`er011_open_items_restructure_verify_01.py`(新規)・
`er011_output/open_items_restructure_01/`配下のjson。1 commitで
`origin/main`へpush。

## PM-CLOSEOUT-CONSOLIDATION-72: PCシャットダウン復旧確認+3V Phase 1b実装/
Opus L2レビュー2件/TTS retryモニタ/T2-T3評価のGit統合+Discovery
Trial-11 Audio GATE_BLOCKED記録

Sonnet(sonnet-worker)が2026-09-11、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-72)に基づき実施した。前提は直前の
`PM-RECOVERY-AFTER-SHUTDOWN-2026-09-11-01`(read-only状況確認、
`docs/pm/RESULT_PACKET.md`旧稿参照)。

**訂正**: `docs/pm/ACTIVE_TASK.md`が「並列稼働中4件」の1つとして記載
していた「Opus L2レビュー(Trial-12、読み取り)」は誤記だった。実在する
Opus L2 REPORT2件(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-
PHASE1-01-OPUS-L2-REVIEW-01_REPORT.md`・同PHASE1B-01版)はいずれも3V
Phase 1/1b向けのレビューであり、"Trial-12"という独立の管理IDは実在
しない。News Ledger拡充Trial-12(`FAMILY-A-NEWS-STAGE4-LEDGER-
ENRICHMENT-AB-TRIAL-12`)は前タスク`PM-CLOSEOUT-CONSOLIDATION-71`
(commit `6a39015`)で既に完走・SSOT反映・commit済みの別物であり、混同
していた。

**反映内容**:

1. **3V Phase 1修正+Phase 1b実装(OPEN-120行へ追記)**: `EDITORIAL-B-
   FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01_REPORT.md`の修正指示
   2回目(Opus L2レビュー指摘対応)・Phase 1b(不足配線のみ)を反映した。
   実装: Voice衝突ガード(`resolve_voice_names_3v()`、Algieba fallback=
   Schedar=voice_cの重複をRuntimeErrorでSTOP)、content integrity check
   のProduction module正式移設(`run_content_integrity_check_3v()`、
   scaffold内fail-closed STOP)、Ledger Deviation Check接続
   (`run_scaffold_3v()`、2Vと同一パターンをmonitoring専用で追加)、
   Tension segment語数のrecord-only観測ログ。`writer`ステージ新規実装
   (Ledger作成のProduction化・Writer retry上限・OPEN-132構造ゲート
   非互換)は3点ともSTOPのまま未実装。offline regression testを本タスク
   で独立に再実行し**54テスト全PASS**(`Ran 54 tests in 0.095s / OK`、
   `.venv/Scripts/python.exe -m unittest`実測)を確認した(REPORT記載の
   48テストから、その後の指摘対応で54件に増加)。Statusは`VALIDATED
   (Trial)`のまま変更せず、`PRODUCTION_WIRED`は宣言していない。
2. **Opus L2レビュー2件の主要指摘記録(OPEN-120行へ追記、コード修正は
   実施していない)**: Phase1版はVoice衝突(HIGH、Phase 1修正で対応済み)・
   Comment 2/3汎用化のB-Family A2への波及(MED-HIGH、コード変更なし)を
   検出。Phase1B版は(1-a)content integrity checkがTrialでは記録専用
   だったのがProductionでfail-closed STOPへ変わった点は「移設」ではなく
   「挙動追加」でREPORTへの1行明記が未対応、(1-b、MED、**未対処**)
   `run_tts_3v()`に予算ガードが1つも無く`BUDGET_JPY_CAP_3V=150.0`が
   事後判定のまま=3V実走前に必須、(1-h、運用注意)Voice A一過性失敗が
   全体STOPになる設計への運用注記が未反映、軽微指摘3件(deviation_
   overall_status欠落/Ledger同一性未記載/「2重定義解消」の記述と実態の
   食い違い)はいずれも未対応、と確認した。Comment 3/4の「どちらが
   正しいか」汎用化可否はユーザー判断待ちのまま。
3. **Discovery Trial-11タオルAudio(OPEN-135行Discovery節へ追記)**:
   `er011_output/discovery_generalization_towels_trial_11/`のA2音声は
   GATE_BLOCKED(comment_2/kp4_japanese_meaning[meaning_4]がSTOPPED、
   既存Audio Validation Gateの想定挙動)で安全停止。B1B音声は未着手。
   PCシャットダウン(2026-09-10→11)による書き込み中断・破損の証跡なし。
   生成再開には小額API支出を伴うため本タスクでは実施せず、現状記録の
   みとした(GATE_BLOCKED状態は変更なし)。
4. **TTS retryタイミング調査2件(OPEN-135行News節へ追記、CLOSED)**:
   `TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md`(CAR-T
   `full_story_part1`3回NG→14時間21分後PASS 1件の横断調査)と、その
   常設集計script化`TTS-RETRY-TIMING-OBSERVATION-MONITOR-01_REPORT.md`
   (`er011_tts_retry_timing_monitor_01.py`、421件のattempt記録・320
   segment系列を集計、冪等性2回実行でMD5一致確認済み)は、いずれも
   「時間依存性あり」と結論する材料はなく(長間隔でのN=1〜3の極小
   サンプル中に明確な反証[kp5_ja_charon、39分後も失敗]が含まれる)、
   Production retry仕様の変更提案はしないと結論した。再評価Trigger案
   (間隔30分以上の事例が累計20件以上かつ連続NG2回以上が累計10件以上)
   を提示、2026-09-10時点はいずれも未達。
5. **Token効率T-2/T-3評価(OPEN-135行News節へ追記)**:
   `PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md`(読み取り専用、
   ¥0)は、T-2(Fableへの限定Git権限付与)・T-3(Ledger研究のWeb検索
   回数上限/reasoning effort調整)とも**推奨=現状維持(保留)**と結論
   した。T-2は既存の軽量委任形式で削減額の60〜70%を既に回収済みで
   フル権限化の追加効果は限定的、かつGatekeeper二層構造の自己点検
   機能が弱まるリスクがある。T-3は検索回数上限がFact Safety(QA相当)に
   該当しうるためSTOP必須条件に該当し、News Trial-12型(簡易・独立
   Verificationなし)とDiscovery/CAR-T型(2段階検証)で安全性水準が
   異なるため一律の上限設定は不適切と判定した(削減見込み自体は
   Discovery型40%前後・News型24〜33%と有意)。実装・設定変更はいずれも
   行っていない。
6. **`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`**: Opus L2レビュー2件
   (Phase1-01/Phase1B-01)の実績行を追記した(未記載だったため新規)。

**Dangling Reference Check**: OPEN-120行・OPEN-135行への追記が参照した
管理ID(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01`・
同PHASE1B-01・両Opus L2レビュー・`FAMILY-A-DISCOVERY-GENERALIZATION-
TOWELS-TRIAL-11-AUDIO-01`・`TTS-REGENERATION-TIMING-DEPENDENCY-
ANALYSIS-01`・`TTS-RETRY-TIMING-OBSERVATION-MONITOR-01`・
`PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01`)はいずれも既存`OPEN_
ITEMS.md`/本ファイル内に既出または本エントリで新規言及した対象で
あり、未定義参照なし(結果:PASS)。OPEN-120行のStatus(`VALIDATED
(Trial)`)・`PRODUCTION_WIRED`未宣言の記述は変更していない。Opus
指摘1-b(予算ガード欠如)は「未対処」と明記し、対処済みであるかの
ような記述にはしていない。

**触れていないもの**: コード・Prompt・Production実装は一切変更して
いない(SSOT反映+regression再実行確認のみ、追加API費用なし、本タスク
自体の費用¥0)。Opus L2 Phase 1b指摘へのコード修正、Discovery
Trial-11の生成再開はいずれも実施していない(未回答報告の原文回収結果
は`docs/pm/RESULT_PACKET.md`参照)。

**根拠**: Fable(PM)からの委任(2026-09-11、管理ID
PM-CLOSEOUT-CONSOLIDATION-72)。出典REPORT: `EDITORIAL-B-FAMILY-VOICES-
3V-PRODUCTION-WIRING-PHASE1-01_REPORT.md`・同PHASE1-01-OPUS-L2-
REVIEW-01・同PHASE1B-01-OPUS-L2-REVIEW-01・`PM-TOKEN-EFFICIENCY-T2-T3-
ASSESSMENT-01_REPORT.md`・`TTS-REGENERATION-TIMING-DEPENDENCY-
ANALYSIS-01_REPORT.md`・`TTS-RETRY-TIMING-OBSERVATION-MONITOR-01_
REPORT.md`。Git操作: ファイル名指定で`git add`(`git add -A`不使用)、
対象=er012コード4件(`er012_b_family_editorial_type_registry_01.py`・
`er012_b_family_production_runner_01.py`・`er012_b_family_voices_
production_01.py`・`er012_editorial_b_family_voices_3v_production_
wiring_phase1_test_01.py`)・`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-
WIRING-PHASE1-01_REPORT.md`・Opus L2 REPORT2件・`PM-TOKEN-EFFICIENCY-
T2-T3-ASSESSMENT-01_REPORT.md`・`TTS-REGENERATION-TIMING-DEPENDENCY-
ANALYSIS-01_REPORT.md`・`TTS-RETRY-TIMING-OBSERVATION-MONITOR-01_
REPORT.md`・`er011_tts_retry_timing_monitor_01.py`・`er011_output/
tts_retry_timing_monitor_01/`配下・`er012_output/editorial_b_family_
voices_3v_production_wiring_phase1_01/regression_evidence/`配下・
ER-010 REPORT2件(`ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_
REPORT.md`・`ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`、
OPEN-124行・`OPEN_ITEMS_HISTORY.md`から参照されていることを確認の上
含めた)・`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/MODEL_ROUTING_
TRIAL_LOG.md`。**除外**(由来不明・本タスク対象外と判定): (1)
Discovery Trial-11タオルAudio一式(`er011_output/discovery_
generalization_towels_trial_11/`・`er011_discovery_generalization_
towels_trial_11_audio_run.py`、GATE_BLOCKEDのまま未解決かつ過去
CONSOLIDATIONで未完了Trial出力を先行commitした前例が確認できなかった
ため)、(2) er006_output/er011_outputのM8件中5件
(`er006_output/audio_retry_cascade_prod_01/human_review_queue.
jsonl`・`er006_output/pronunciation_ledger_01/ledger.json`・
`er011_output/family_a_completion_a2_trend_end_to_end_01/`配下3件、
いずれも最終更新が2026-09-07〜09でTTS retryモニタ調査の参照元データに
過ぎず、本タスクの並列作業4件のいずれにも由来しない)、(3) 同M8件中
3件(`er006_output/master_audio_store_01/manifest.json`・`reuse_
telemetry.jsonl`・`er011_output/attempt_history.jsonl`、最終更新
2026-09-10 11:18-11:20でDiscovery Trial-11(theme_id実測確認済み)に
由来するが、Trial-11本体をGATE_BLOCKEDのまま未commitとする判断と
整合させるため同時に除外)。1 commitで`origin/main`へpush(競合・
エラー時は本タスクではpushせず報告)。並列稼働中の後続作業は現時点
でなし。`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`はいずれも
本タスクの最終更新対象(通常の一時ファイル更新)。

## PM-CLOSEOUT-CONSOLIDATION-73: ユーザー回答2026-09-11(3V/Discovery/News/
TTS retry timing/Token効率/量産APIコスト/新規記事テーマ)のSSOT反映

Sonnet(sonnet-worker)が2026-09-11、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-73-USER-ANSWERS-2026-09-11)に基づき実施した。
本タスクは並列稼働中5件(3V予算ガード修正/Discoveryタオル音声再開/TTS
retry cool-down分析/Token効率T-3再評価/Opus News Trial-12解釈)の生成物
(er011/er012コード・出力・新規REPORT)には一切触れていない。

**ユーザー回答原文(2026-09-11、そのまま転記)**:

```
1. 3V
- 予算ガード修正:着手OK。
- Comment文言:3V対応表現へ統一。
- 3Vの正式Statusは VALIDATED ではなく、既にユーザー正式採用済みなので APPROVED_FOR_PRODUCTION に是正。
- ただし runtime evidence・Production全経路・SSOT/Git等が完了するまで PRODUCTION_WIRED にはしない。
- Phase 1bは「承認済み3V仕様の不足配線のみ」。新仕様が必要ならSTOP。
2. Discovery タオル
- Human Review+必要segment再生成へ進める。
- 記事・Support・Audio・試聴artifactまで完成させ、ユーザー確認後にN増し判断。
- 保険文は、出たらHuman Review修正+発生率観測。
- Focus Module Production採用はまだしない。
3. TTS retry timing
- CAR-Tの4回目PASSを受け、過去ログ集計+今後の継続モニタリングを実施。
- 見たいのは「4回目だから通るか」ではなく、「連続NG後、時間を空けたretryの方がPASS率が高いか」。
- 自然発生retryのみ観測し、人工的にTTS生成回数を増やさない。
- 傾向が十分出たら、cool-down retry仕様候補としてUSER_DECISION_REQUIREDで提示。
- 現時点ではProduction retry仕様変更しない。
4. Token効率
ユーザーが今改善したいのは、「量産APIコスト」ではなく「開発Lineで消費するClaude Token / weekly limit」。
目的:Token limit到達で開発できない時間帯を減らすこと。
- T-1:実施継続。実施前後のClaude Token削減効果を実測/代表ケースで報告。
- T-2:現状維持。FableへGit権限追加しない。
- T-3:従来REPORTはProduction/APIコスト寄りで論点がずれていたため、Claude開発Token観点で再評価する。特に、・Ledger/Research結果の重複読込・Fable/Sonnet/Opus間の同一context再読・巨大Ledger全文読込・Opusへ渡すcontext過多・長いResearch結果を必要以上に引き継いでいないか を調査し、Claude Token削減案とリスクを報告。
- T-4:現状保留。節約モードはまだ導入しない。
5. 量産LineのAPIコスト
- GPT / Web Search / TTS / ASR等の量産コスト最適化は重要。
- ただし、これはユーザー実検証後に別途がっつり実施する。
- Open Itemとして保持し、今の開発Token改善と混同しない。
6. News
- Ledger fact供給量 / evidence allocationを改善主軸へ寄せる方向は合意。
- Trial-12のOpus解釈を待って正式判断。
- News Focus Module NG率50%は過去Hanshin 3/6の再掲。新規結果と混同しない。
- Theme2 Ledger ID不整合は単純修正なら自律修正。
- 遡及QAは量産段階までDEFER。
7. 新規記事テーマ
- Fable / Claude側で勝手に新テーマを決めない。
- 新規記事は問題なければ最終版候補まで持っていく前提。
- 英語 / 日本語 / 短い理由の複数候補を出し、ユーザー選択後に生成。
- retry / regen / Local Rewrite等の既存記事修正は除外。
共通:
- 自明な修正は自律的に進める。
- 仕様判断はユーザーへ戻す。
- 小コストTrialは結果まで進めてよい。
- USER_DECISION_REQUIREDは未報告放置しない。
- APPROVED_FOR_PRODUCTIONはPRODUCTION_WIREDまで追跡。
- 新規結果 / 過去再掲 / 進行中未結果を明示的に区別。
```

**反映箇所**:

1. **OPEN-120行(3V)**: Statusを`VALIDATED(Trial)`から`APPROVED_FOR_
   PRODUCTION`へ是正(`CURRENT_SPEC.md`側は2026-09-10時点で既に正しく
   `APPROVED_FOR_PRODUCTION`[未配線]だったため追加編集なし、Grep確認
   のみ実施)。`PRODUCTION_WIRED`は引き続き未宣言と明記。予算ガード
   修正着手承認・Comment 2/3/4の3V対応表現への統一・Phase 1bスコープ
   (既承認3V仕様の不足配線のみ、新仕様が必要ならSTOP)を追記した。
2. **OPEN-135行(Discovery/News/TTS retry timing)**: 原文2・3・6の決定を
   追記した。**訂正**: `PM-CLOSEOUT-CONSOLIDATION-72`(本ファイル該当
   エントリ、書き換えず本エントリで訂正)が「`docs/pm/ACTIVE_TASK.md`の
   『Opus L2レビュー(Trial-12、読み取り)』は誤記」としていた点を、
   「News Trial-12のOpus L2解釈は計画済みで未実施だっただけであり、
   2026-09-11に別途実施中(結果待ち)」に改めた。News Focus Module NG率
   50%が過去Hanshin再掲である旨、Theme2 Ledger ID不整合(OPEN-140)が
   既に`CLOSED`済みで追加対応不要である旨、遡及QA(OPEN-141)は量産段階
   までDEFERする旨を記録した。
3. **OPEN-142(新規起票)**: Claude開発Token効率化プログラム(T-1継続+
   効果実測、T-2現状維持、T-3は開発Token観点で再評価中[並列task]、
   T-4保留)。既存OPEN-135内「Token効率T-2/T-3」記載(量産API/Production
   観点)とは目的が異なる開発Token/weekly limit観点の追跡行として区別
   した。
4. **OPEN-143(新規起票)**: 量産Line(GPT/Web Search/TTS/ASR等)APIコスト
   最適化。Status=`DEFERRED`(ユーザー実検証後に着手)。OPEN-142との
   混同防止を明記。
5. **`docs/pm/PM_GOVERNANCE.md`**: 13節へ「新規記事は問題なければ最終版
   候補まで持っていく前提」の2026-09-11再確認を追記(13-1既存記述と
   同旨の再確認、新ルールではない)。3節(PM Closeout Mandatory Check)
   item 4の直後へ「APPROVED_FOR_PRODUCTIONはPRODUCTION_WIREDまで追跡」
   の2026-09-11再確認を追記(具体例としてOPEN-120 3Vを参照)。9-4
   (更新種別の明示ルール)・11節(低コスト分析・Trialの自律実施/自明な
   修正の自律実施)・12-7(未回答管理)は原文「共通」6項目のうち該当5項目
   (新規結果/過去再掲/進行中未結果の区別・小コストTrial・自明な修正・
   仕様判断のユーザー差し戻し・UDR未報告放置禁止)を既に恒久ルールとして
   カバー済みであることを確認し、重複追記はせず各節へ2026-09-11再確認の
   1行のみ追加した。`docs/pm/PM_BRIEF.md`の13節案内文(67-69行付近)へも
   同旨を反映した。

**触れていないもの**: コード・Prompt・Production実装は一切変更していない
(SSOT/governance反映のみ、追加API費用¥0)。並列稼働中5件(3V予算ガード
修正コード・Discoveryタオル音声再開・TTS retry cool-down分析・Token効率
T-3再評価・Opus News Trial-12解釈)の生成物には一切触れていない。

**根拠**: Fable(PM)からの委任(2026-09-11、管理ID
PM-CLOSEOUT-CONSOLIDATION-73-USER-ANSWERS-2026-09-11)。Git操作: ファイル
名指定で`git add`(`git add -A`不使用)、対象=`OPEN_ITEMS.md`・
`DECISION_LOG.md`・`docs/pm/PM_GOVERNANCE.md`・`docs/pm/PM_BRIEF.md`・
`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`のみ。1 commitで
`origin/main`へpush。

## PM-CLOSEOUT-CONSOLIDATION-74-USER-ANSWERS-2026-09-11-02: ユーザー回答
2026-09-11第2回(News追加切り分けTrial承認/3V Comment 3共有定義承認/
Claude開発Token削減T-3施策A・B正式採用/既存進行事項事実訂正/Reporting
Rule再確認)のSSOT反映+Opus L2解釈(Trial-12)のREPORT化

Sonnet(sonnet-worker)が2026-09-11、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-74-USER-ANSWERS-2026-09-11-02)に基づき実施した。
本タスクは並列稼働中2件(Discoveryタオル音声再開`er011_output/
discovery_generalization_towels_trial_11/`、News追加切り分けTrial
`er011_output/news_ledger_enrichment_ab_trial_12/`配下)の生成物には
一切触れていない。

**ユーザー回答原文(2026-09-11第2回、そのまま転記)**:

```
1. News追加切り分けTrial → 実施承認。Opus推奨の以下2本を実施。
- 既存の打ち切られた7記事へFact Checker単独適用。目的: Overlap Gateで先に停止したことにより、後段Fact Checkerの問題が隠れていたか確認する。見込み費用: 約¥15〜25。
- 条件E Trial。FACT-11 / FACT-14の2件を追加し、「fact数」ではなく「非headline角度の周辺FactがPointごとに供給されること」がOverlap改善に効いているか切り分ける。見込み費用: 約¥70〜100。
単純なA/B N増しは今回は行わない。今回の仮説は「Fact数が多いほど良い」ではなく「Pointごとに異なる非headline角度のEvidenceが供給されることが重要」。ただしこれはまだTrial仮説であり、Production仕様として採用しないこと。Trial終了時はREJECTED / VALIDATED / USER_DECISION_REQUIREDのいずれかで明示的にcloseすること。
また、既に存在しているTrial-12b artifactについて、新規API実行なしで集計・REPORT化すること。
重要: Trial-12bは既に結果が確定していたにもかかわらず、「タオルAudio完了後にまとめて報告する」という理由でユーザーへの報告が遅れた。これは現在の恒久Reporting Rule「独立した報告単位がreportableになった時点で直ちに報告する」に反する。今後は、別作業の完了待ち・統合報告待ち・並列タスクの終了待ちを理由に、確定済みTrial結果・USER_DECISION_REQUIRED・重要発見の報告を保留しないこと。独立して報告可能になった時点で即時報告すること。今回の遅延理由と再発防止をPM記録へ反映すること。
2. 3V Comment 3 → 共有定義のままで承認。「どの声が正しいか」へ統一したComment 3定義は、3V専用へ分岐せず、2V/A2と共有のままとする。ただし、文字列「どの声が正しいか」を本文へ固定挿入する仕様という意味ではない。Comment 3生成Prompt上の役割表現である。既存承認済みA2音声を再生成する必要はない。なお、VoicesはPerspectivesであり、pro/conの勝敗判定を目的とするものではない。将来「正しい声を選ばせる」方向へ意味が拡張される場合は、新仕様としてSTOPし、USER_DECISION_REQUIREDにすること。
3. Claude開発Token削減 → 以下を正式採用。目的はProduction APIコスト削減ではなく、Claude Codeのweekly Token消費を抑え、Token limitにより開発不能になる時間を減らすこと。
T-2: 現状維持。FableへGit権限は追加しない。
T-3: 以下2施策を採用。
A. DECISION_LOG.mdの構造分割 — T-1でOPEN_ITEMSへ行ったのと同様、内容・意味・status・履歴を変えず、必要部分だけ読める構造へ分割する。情報削除・要約による意味圧縮は禁止。既存参照・検索性・管理IDの追跡性を維持する。構造変更前後で情報欠落がないことを確認する。実施後、Claude Token削減効果を代表ケースで実測または比較報告する。
B. Opus L2入力限定 — Opusへ巨大SSOT全文を原則渡さない。レビュー対象の論点・必要ファイル・必要な該当箇所だけを渡す。必要な事実を省いてレビュー精度を落とさないこと。「Token節約のために重要contextを落とす」ことは禁止。まずSonnet/Fable側で対象範囲を絞り、Opusには論点限定contextを渡す。この運用をPM_GOVERNANCEへ明文化する。
可能であれば、実施前後でOpus 1回あたり入力Token・SSOT読込量・Fable/Sonnet/Opus間の重複読込を比較し、削減効果を報告すること。
Production API側のGPT / Web Search / TTS / ASRコスト最適化は別Open Itemとして保持。ユーザー実検証後に本格的に実施。今のClaude Token改善と混同しないこと。
4. 既存進行事項
- 3V予算ガード: 既に実装済みとのことなので、新規実装不要。SSOTの「未実装」記録だけ事実訂正する。
- 3V Status: 既にユーザー正式採用済みなのでAPPROVED_FOR_PRODUCTION。VALIDATEDへ戻さない。Production正式初回経路・retry/fallback/Local Rewrite等の整合、runtime evidence、tests、SSOT/Gitまで完了するまではPRODUCTION_WIREDにしない。
- Discovery Trial-11 タオル: Human Review+必要segment再生成へ進める。A2/B1B Audio・試聴artifactまで完成させ、ユーザー確認後にN増し判断。
- TTS cool-down: 現時点では事前基準未達。Production retry仕様には採用せず、自然発生retryのみ継続観測。
5. Reporting / PM Gate再確認 — 今回のTrial-12b未報告は「統合報告まで待った」こと自体が問題。以後、Trial結果確定・Opus/Sonnetレビューで重要発見・USER_DECISION_REQUIRED発生・Production wiring STOP・既存認識を覆す結果、が出た時点で他作業を待たず即時報告すること。既に未回答の報告がある状態で新しい報告が出た場合は、恒久ルールどおり未回答報告を省略せず必要に応じて再掲すること。主要タスクcloseout時は、USER_DECISION_REQUIRED・VALIDATED未採否・APPROVED_FOR_PRODUCTION未配線・未報告Trial・未登録Open Itemが残っていないか必ず確認すること。
```

**Opus L2解釈のREPORT化**: opus-consultantからFable経由で受領した最終メッセージ
全文を`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-
INTERPRETATION-01_REPORT.md`として原文のまま(改変・要約なし)保存した。
要旨は`OPEN_ITEMS.md`OPEN-135行2026-09-11追記(本管理ID)参照。

**Trial-12b報告遅延の原因と再発防止(ユーザー指摘、原文1「重要」節)**:
News Ledger拡充Trial-12b(条件C/D、`er011_output/news_ledger_enrichment_
ab_trial_12/`配下)は、artifact生成・結果確定が2026-09-10時点で既に完了
していたにもかかわらず、Fableが「Discoveryタオル記事のAudio完了後に
まとめて報告する」と判断したため、確定済みTrial結果のユーザーへの報告が
1日以上遅延した。これは`docs/pm/PM_GOVERNANCE.md`12-2(報告可能になった
時点での即時報告、他の並列作業の完了を待たない)に反する運用判断だった。
再発防止として`docs/pm/PM_GOVERNANCE.md`12節へ新小節12-9「『他作業の
完了待ち・統合報告待ち』を理由にした報告保留の禁止」を追加し、確定済み
Trial結果・`USER_DECISION_REQUIRED`・重要な発見(Opus/Sonnetレビューでの
重要発見・Production wiring STOP・既存認識を覆す結果)は、他作業の完了
待ち・統合報告待ち・並列タスク終了待ちを理由に保留しないことを恒久
ルールとして明文化した。

**過去Opus L2利用の実態確認(付記事項、Fable/ユーザー指示による事実確認)**:
opus-consultantの最終メッセージ付記が言及した「1回目のOpus L2」
(`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-REVIEW-01`)
について、`er011_news_ledger_enrichment_leaveout_trial_12b_run.py`
L5-13・L219(`"opus_review": "FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-
TRIAL-12-OPUS-L2-REVIEW-01"`)と`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`を
Grepし、以下を事実確認した(判断はFable/ユーザーへ委ねる、本タスクでは
判断しない)。(1) root直下に`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-
TRIAL-12-OPUS-L2-REVIEW-01_REPORT.md`という名前のREPORTファイルは存在
しない(`find`実測、他の類似命名REPORT3件[3V Phase1/Phase1b/Discovery
Trial-11]は存在するのに本件のみ存在しない)。(2) `docs/pm/MODEL_ROUTING_
TRIAL_LOG.md`にも当該Opus L2レビューをOpus利用実績として記録した行は
見当たらない(Trial-12本体の実行[L1に相当]は「Opus不要」と明記した行が
1件あるのみ、L2レビュー実施の記録行はGrep該当なし)。(3) 唯一の記録は
`er011_news_ledger_enrichment_leaveout_trial_12b_run.py`冒頭コメントと
metadata辞書キーのみであり、SSOT(`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`)への反映が漏れていたと判断できる。
`docs/pm/PM_GOVERNANCE.md`11節のOpus利用上限(1管理IDあたりL2+L3合計
最大1回)との整合はPM(Fable)側で確認されたい。

**反映箇所**:

1. **OPEN-120行(3V)**: 予算ガード実装済みの事実訂正(Grep根拠行を明記、
   `er012_b_family_voices_production_01.py` L829-909・
   `er012_b_family_production_runner_01.py` L649-655/1083/1091/1093)。
   Phase 1b-02(Comment 3タイトル行/役割行統一、offline regression
   `collected=2309 passed=2306 failed=3`実測、¥0)を反映。ユーザー回答2
   (共有定義承認、Voices=Perspectives、勝敗判定へ拡張ならSTOP→UDR)を
   記録。Status=`APPROVED_FOR_PRODUCTION`維持、`PRODUCTION_WIRED`条件を
   原文どおり記録。
2. **OPEN-135行(News/TTS retry)**: Opus解釈要点(REPORT全文への参照)、
   Trial-12b未報告の事実、追加切り分けTrial 2本の承認(仮説は「Point
   ごとに異なる非headline角度のEvidence供給」、Trial仮説でありProduction
   採用ではない、close時はREJECTED/VALIDATED/UDR明示)、TTS retry
   cool-down分析結果(即時54.35%[N=46] vs 非即時71.43%[N=7]、
   Fisher p=0.6851、非即時7件中5件は人的介入、事前基準未達、継続観測)を
   反映した。
3. **OPEN-142行(Token効率)**: T-3再評価結果(`DECISION_LOG.md`
   1,334,377字が最大Token源、Opus L2入力≈45.2万字/件、T-1効果実測
   [全文-54.6%・Grep最悪ケース-83〜90%・Edit diff約1/5])を記録し、
   施策A(DECISION_LOG.md構造分割、本タスクでは未実装・別タスク)・
   B(Opus L2入力限定、`docs/pm/PM_GOVERNANCE.md`へ明文化)を正式採用と
   記録した。T-2は現状維持、T-4は保留のまま。OPEN-143(量産APIコスト)は
   保持のまま混同しない旨を再確認した。
4. **`docs/pm/PM_GOVERNANCE.md`**: (a) 12節へ新小節12-9(Trial-12b
   未報告の経緯・再発防止の明文化)を追加。(b) 11節「L2事前レビューの
   運用」直後へ新小節「Opus L2入力限定の運用」を追加(巨大SSOT全文を
   渡さない/論点・必要ファイル・該当箇所限定/重要context省略禁止/
   Sonnet・Fable側での範囲絞り込み/委任文への入力ファイル一覧・概算
   文字数記載)。(c) 3節「PM Closeout Mandatory Check」へ項目20
   (UDR未処理・VALIDATED未採否・APPROVED未配線・未報告Trial・未登録
   Open Itemの5項目確認)を追加。(d) `.claude/agents/opus-consultant.md`
   へ入力限定運用を1〜2行追記。(e) ヘッダ「最終更新」・末尾「変更履歴」を
   更新。
5. **`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`**: Opus解釈
   (`...OPUS-L2-INTERPRETATION-01`)を1行追記し、入力規模概算
   (Trial-12 REPORT本文32,801字+Trial-12b artifact直読分)を記録した。
6. **`docs/pm/ACTIVE_TASK.md`**: 固定ヘッダを更新し、並列稼働中を
   タオル音声再開・News追加切り分けTrial2件へ整理、次アクション(DECISION_
   LOG構造分割は本タスクでは実施せず、承認済みだが別タスクで実施する
   旨)を明記した。

**触れていないもの**: 並列稼働中2件(Discoveryタオル音声再開・News追加
切り分けTrial)の生成物には一切触れていない。News追加切り分けTrial2本
(Fact Checker単独適用・条件E)自体の実行はFableが別途sonnet-workerへ
委任する(本タスクの範囲外、本タスクはOpus解釈のREPORT化とSSOT反映の
みを実施)。DECISION_LOG.mdの構造分割(施策A)は正式採用のみ記録し、
実装は別タスクで行う。コード・Prompt・Production実装は一切変更していない
(追加API費用¥0)。

**根拠**: Fable(PM)からの委任(2026-09-11、管理ID
PM-CLOSEOUT-CONSOLIDATION-74-USER-ANSWERS-2026-09-11-02)。Git操作:
ファイル名指定で`git add`(`git add -A`不使用)。1 commitで
`origin/main`へpush。

## PM-TOKEN-EFFICIENCY-T3A-DECISION-LOG-RESTRUCTURE-01: DECISION_LOG.md構造分割(内容不変)

**日付**: 2026-09-11

**区分**: PM運用(トークン効率化、サービス・生成仕様ではない)

Sonnet(sonnet-worker)が、ユーザー正式採用(2026-09-11、T-3A)に基づき、
`DECISION_LOG.md`(1,334,377字≈60万token、開発Line最大のClaude Token
発生源、`PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01`と同方式)を
内容・意味・Status・履歴を一切変えずに構造分割した。

**構造分布**: 本体は(1)タイトル+管理ID`ER-PM-001`ラベル+「最終更新」
チェーン13件(reverse-chronological、うち12件が単一行の巨大paragraph)、
(2)本文231件の決定エントリ(`## <管理ID>: <タイトル>`見出し、時系列
昇順)、(3)末尾`## 参照元`小節、の3部構成であることを機械抽出で確認
した(要約禁止のため見出し行の切り貼りのみで把握)。

**採用した分割方式**: (a)ヘッダーチェーンは最新1件のみ本体に残し、
古い12件を`DECISION_LOG_HISTORY.md`の`## ER-PM-001_CHAIN`節へ原文の
まま移動。(b)本文231件のうち直近25件(chronological末尾)を本体に
そのまま残し、古い206件を`DECISION_LOG_HISTORY.md`へ原文のまま
(各エントリの元見出しごと)移動。(c)本体に全231件の原文見出しを
列挙した「索引」節を新設(要約なし、既存見出し行の切り貼りのみ、
本体内/履歴のいずれかを明記)。理由: `OPEN_ITEMS.md`が行単位の
Status要約+履歴全文という構造だったのに対し、`DECISION_LOG.md`は
最初から`## <ID>: <タイトル>`見出し単位で意味的に完結したエントリの
時系列append-only構造であり、要約すべき「現在値」は存在しない
(全エントリが等しく確定済みDecisionの記録)。よって新規要約は作らず、
「直近だけ本体に残し、古いものは原文のまま切り出す」方式が最も
自然かつリスクが低いと判断した。

**決定論的実施**: `er011_decision_log_restructure_01.py`が上記分割を
手作業編集なしで実施し、`er011_output/decision_log_restructure_01/
manifest.json`へ全移動範囲(行番号)を記録した。

**検証結果**: `er011_decision_log_restructure_verify_01.py`が、git HEAD
(分割前)の`DECISION_LOG.md`とmanifestの行範囲から再構成した全文が
空白正規化後に完全一致すること、本体+履歴ファイルの実ファイル内容
からも同様に全236チャンク(固定5+kept25+moved206)が原文のまま
それぞれ正しいファイルに含まれること、エントリ数(231件、kept25+
moved206)が一致すること、管理ID/OPEN番号/日付/URL/ファイルパスの
出現件数が分割前後で完全一致すること(mgmt_id 1377/OPEN-xxx 575/
date 397/url 23/filepath 1762、いずれも一致)を確認し、
`ALL_PASS: true`を`er011_output/decision_log_restructure_01/
verify_result.json`へ出力した。

**効果実測**: 本体は826,259→131,288字(-84.1%、約28万token相当の
削減)。履歴は`DECISION_LOG_HISTORY.md`(721,923字、新規)へ切り出した。
代表アクセスパターンの実測は`PM-TOKEN-EFFICIENCY-T3A-DECISION-LOG-
RESTRUCTURE-01_REPORT.md`の効果実測表を参照。

**SSOT反映**: `CLAUDE.md`・`docs/pm/PM_BRIEF.md`・`docs/pm/
PM_GOVERNANCE.md`へ`DECISION_LOG_HISTORY.md`の位置づけ(別の管理場所
ではなく`DECISION_LOG.md`の切り出し先)を追記した。`OPEN_ITEMS.md`・
`CURRENT_SPEC.md`の編集、コード・Prompt・Production実装の変更、API
呼び出しはいずれも実施していない。

**根拠**: Fable(PM)からの委任(2026-09-11、管理ID
PM-TOKEN-EFFICIENCY-T3A-DECISION-LOG-RESTRUCTURE-01)。詳細は
`PM-TOKEN-EFFICIENCY-T3A-DECISION-LOG-RESTRUCTURE-01_REPORT.md`、
`er011_decision_log_restructure_01.py`、
`er011_decision_log_restructure_verify_01.py`、
`er011_output/decision_log_restructure_01/`参照。

## PM-CLOSEOUT-CONSOLIDATION-75-NEWS-TRIAL-14: News Trial-14(曖昧性解消)+Trial-12b(leaveout)結果のSSOT反映(副仮説REJECTED・主仮説USER_DECISION_REQUIRED)+PM_GOVERNANCE 8節へgit stash/clean禁止追記

**日付**: 2026-09-11

**区分**: サービス・生成仕様(News Editorial Type、Trial段階、Production未採用)

Sonnet(sonnet-worker)が、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-75-NEWS-TRIAL-14)に基づき、`FAMILY-A-NEWS-
STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14_REPORT.md`と
`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B_REPORT.md`
(いずれもSonnet委任実行・Fable既読了)の結果をSSOTへ反映した。

**結果概要**: 副仮説「fact数が多いほど良い」= **REJECTED**(条件C[fact10件]
の最終NG率83.3%が条件A[fact5件]と同率であることを正式集計[Trial-12b]で
確認、fact数と最終NG率は単調でない)。主仮説「Pointごとに異なる
非headline角度のEvidence供給が重要」= **USER_DECISION_REQUIRED**
(Point生成段階の構造指標[初回Value QA flag 6/6→0/24、anchor衝突平均
1.5→0〜0.167]は条件C/D/B/Eいずれも一貫して支持するが、条件E[最終NG率
16.7%、N=6]はA比較Fisher正確検定p=0.08で有意差に達せず、Fact Checker
以降の合否はfact固有の性質[固有名詞の多寡]に強く依存し単一仮説では
説明しきれない)。新規発見として、打ち切り記事8本へのFact Checker
単独適用により、FAILの77.8%(9件中7件)が人名ローマ字誤り(例:
伏見寅威→Tora/Tai Fushimi)であり、Ledger拡充とは独立した全条件共通の
基礎的弱点であることが判明した(打ち切りバイアス除去後の条件A真の
FAIL率33.3%、従来は元パイプラインのFact Checker到達率1/6のため隠れて
いた)。費用実績合計¥147.3(上限¥150以内、内訳・段階3最終run開始時点の
残枠¥15.8に対する最悪ケース超過の余地はSonnetが自己申告済み)。
Trial-12bは¥0(既存artifactの正式集計・報告書化)。

**反映範囲**: `OPEN_ITEMS.md`OPEN-135行(News節)へ上記結果・新規発見・
UDR(Fableが提示する選択肢: (a)人名ローマ字誤り対策[Ledgerへの英語表記
併記等、候補]を先に切り分ける/(b)Hanshin型以外への一般化Trial/(c)現状で
主軸移行を決める、のいずれか、決定はしない)を追記した。News Focus
Module NG率「50%」は過去Hanshin 3/6の再掲であり本Trial-14の新規結果と
混同しない旨の既存注記を維持した。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`
に本Trialを1行追記した。`docs/pm/PM_GOVERNANCE.md`8節(並列起動)へ、
並列稼働中は`git stash`(あらゆる形式)・`git clean`・他タスクファイルの
`git checkout`を禁止する旨を追記した(経緯: 2026-09-11のT3A作業中に
`git stash -u`が並列タスクの未追跡ファイルを一時退避する事故があり、
`pop`で復元済みだが再発防止のため恒久ルール化)。

**整合性確認**: `er011_output/news_ledger_enrichment_ab_trial_12/
{factcheck_censored,twofact_e,reaggregation}/`配下のJSONが全件parse
可能であること、REPORT記載件数(打ち切り記事8本・条件E N=6 run)と
一致することを確認した(直前タスクのstash事故の影響がないことの確認、
詳細は`docs/pm/RESULT_PACKET.md`参照)。

**Production採用範囲外**: 本エントリはTrial結果のSSOT反映のみであり、
Production Prompt・Ledger・QA/Validator/retryコードの変更、
`APPROVED_FOR_PRODUCTION`宣言はいずれも行っていない(追加API費用¥0、
本タスクでのSonnet委任実行はなし)。並列稼働中のDiscoveryタオル音声
再開(`er011_output/discovery_generalization_towels_trial_11/`)には
一切触れていない。

**根拠**: Fable(PM)からの委任(2026-09-11、管理ID
PM-CLOSEOUT-CONSOLIDATION-75-NEWS-TRIAL-14)。詳細は
`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14_
REPORT.md`、`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B_
REPORT.md`、`docs/pm/RESULT_PACKET.md`参照。

## PM-CLOSEOUT-CONSOLIDATION-76-TOWELS-AUDIO-HUMAN-REVIEW: Discoveryタオル音声resume(Trial-11)のHuman Review 3件をSSOT反映+TTS費用集計gemini_batch ¥0計上バグを新規OPEN-144として起票

**日付**: 2026-09-11

**区分**: サービス・生成仕様(Discovery Editorial Type、Trial段階、Production未採用)+技術的負債(コスト計測)

Sonnet(sonnet-worker)が、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-76-TOWELS-AUDIO-HUMAN-REVIEW)に基づき、
`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01_REPORT.md`
(管理ID`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME`、
Sonnet委任実行・Fable既読了)と付随する`a2`/`b1b`の
`human_review/review_package.md`の内容をSSOTへ反映した。

**結果概要**: 前回GATE_BLOCKED状態から、既存Human Review Lock機構
(ER-011-HUMAN-REVIEW-COST-GUARD-01)の`approve_regenerate()`で各segment
1回だけ自然な追加takeを取得した(新規Gate・閾値・retry仕様の追加なし)。
A2の`meaning_4`(Key Phrase4日本語gloss)は追加take1回目で`EXACT_MATCH`
となり`RESOLVED`。A2の`comment_2`は6/6takeがTRUE_CONTENT_MISMATCHで
`HUMAN_REVIEW_REQUIRED`のままだが、観測されたのは「時間がたつ→経つ」
「におい→ニオイ/臭い」という同一発音の表記ゆれのみであり、誤分類の疑いが
ある。B1Bの`full_story_part1`は原roundで2022 survey統計文が丸ごと欠落する
genuine content dropだったが、resume roundのtake5(内容ほぼ完全一致、差異
は"has dried"→"had dried"のみ)が最良候補として得られた。B1Bの
`full_story_part2`は6take中4takeが内容一致(NORMALIZED_MATCH/
HIGH_SIMILARITY_SAFE)だが、canonical textに正規に2回登場する
「after two months」をRepetition QAが`canonical_repeat_count: 0`と誤認識
し言い直しとして誤flagしている疑いが強い。保険文(hedging表現)はA2・B1B
とも0件(Part A単独運用での発生率観測の初回記録)。3件ともユーザーの
試聴によるHuman Review判断が必要であり、本タスクでは`record_human_
approval()`の代行・Assembly実行はいずれも行っていない。

**新規発見(TTS費用集計バグ)**: 既存`cost_stage()`による報告額¥12.76は、
集計元script(`er011_discovery_generalization_towels_trial_11_audio_run.py`
の`_call_cost_usd()`)が`provider=="gemini"`のみを判定し、実際のログ記録
`provider=="gemini_batch"`(TTS音声生成、69件)と一致させられず0円計上して
しまうバグにより過小計上されていることが判明した。手動概算では約
¥62.83(¥50.07未計上)。Grepにより同一パターン(`gemini_batch`分岐を持た
ない)のscript12本(Household最終版・News Trial-09・no18系・
open121系・connected_speech系・transcript_style_normalization・
er005_stage7・er006系3本)を特定し、個別確認できた範囲では
Household最終版・News Trial-09・`er006_pool_pilot_01_cost_time_compute.py`
の対象3テーマはいずれも`gemini_batch`記録0件で実質影響なし(標準TTS
経路のみ使用)と確認した。残り(transcript_style_normalization・
connected_speech系2本・open121系2本・no18系2本・er005_stage7)は個別
ログでの`gemini_batch`有無を本タスクでは未確認。修正はいずれのscript
に対しても実施していない(新規**OPEN-144**として起票、Status=`OPEN`)。

**反映範囲**: `OPEN_ITEMS.md`OPEN-135行(Discovery節)へ上記Human Review
結果・保険文観測・費用実績と発見バグを追記した。`OPEN_ITEMS.md`OPEN-121行
へ、`full_story_part2`のRepetition QA誤flag疑いが2026-09-08の
`TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01`(em dash
起因の`_canonical_repeat_count()`誤カウント)と同一module・同種の
failure modeである可能性が高いこと(ただし今回はem dashが原因ではなく
原因未特定)を新規観測として追記した。`OPEN_ITEMS.md`へ新規OPEN-144行
(TTS費用集計gemini_batch ¥0計上バグ、Status=`OPEN`)を起票した。
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`に本resume実行を1行追記した。

**Production採用範囲外**: 本エントリはHuman Review待ち状態・Trial結果・
バグ発見のSSOT反映のみであり、Production Prompt・Ledger・QA/Validator/
retryコード・費用集計scriptの変更、`record_human_approval()`の代行、
Assembly実行、`APPROVED_FOR_PRODUCTION`宣言はいずれも行っていない
(本タスクでの追加API費用¥0)。

**根拠**: Fable(PM)からの委任(2026-09-11、管理ID
PM-CLOSEOUT-CONSOLIDATION-76-TOWELS-AUDIO-HUMAN-REVIEW)。詳細は
`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01_REPORT.md`、
`er011_output/discovery_generalization_towels_trial_11/{a2,b1b}/
human_review/review_package.md`、`docs/pm/RESULT_PACKET.md`参照。

## PM-CLOSEOUT-CONSOLIDATION-77-PM-OPERATION-CORRECTION-2026-09-12: 「問題発生→とりあえずHuman Review依頼」運用の是正、PM_GOVERNANCE新設14節(問題発生時のPM処理原則)・15節(コスト報告ルール)・9-5(問題対応報告7項目順+試聴Artifact/playerリンク必須)追加+タオルTrial-11コスト報告初回適用

**日付**: 2026-09-12

**区分**: Implementation Hardening(PM運用ルールの明文化。サービス・
生成仕様・Production Prompt・コードは変更していない)

**ユーザー指示原文(全文)**:

```
今回の報告品質は不十分です。「問題が起きた → 比較的マシなtakeをユーザーに
聞いてもらう」ではなく、問題発生時はまず原因を切り分け、既存対策との
reconcile、必要最小TrialまでPM側で進め、ユーザーには"判断材料が揃った
状態"で持ってきてください。
1. A-Family / Discovery / A2: 表記ゆれをHuman Reviewで逃がさない。
「たつ/経つ」「におい/ニオイ/臭い」について、既存の日本語ASR正規化・
表記ゆれ対策をRepoで確認し、既存対策があるのに今回効かなかったのか/
そもそも対象外なのかを特定する。既存対策で解けるなら、その不足配線/
実装漏れを是正候補として整理。今回固有の語だけでなく、同様の問題を
起こさせないこと。新仕様が必要ならSTOPしてUSER_DECISION_REQUIRED。
2. A-Family / Discovery / B1: `has dried → had dried`について、既存
Secondary ASR cascadeが発火したか、結果が何であったかを事実確認。未発火
なら「なぜ発火しなかったか」を特定。Human Reviewより前に既存cascadeで
切り分け可能か確認する。また、full_story_part1はtake1-3で2022 survey文
欠落、take4以降で欠落解消。このため「時間を空けたretryで改善する可能性」
について、既存TTS retry timing監視データを再集計し、即時retry/非即時
retry/連続NG後の次attempt PASS率/人的介入あり・なしを分けて結果だけまず
報告すること。まだ基準未達なら仕様採用しない。十分な傾向がある場合のみ、
正式retry方針候補としてUSER_DECISION_REQUIREDへ。
3. 共通 / Repetition QA: 今回の`after two months`誤flagは個別Human
Reviewで終わらせない。過去のintentional-repeat false positive対策
(2026-09-08の既存事例含む)とreconcileし、今回なぜ`canonical_repeat_
count: 0`になったか根本原因を特定。既存対策の不足なら最小修正Trialを
設計・実施。新しいValidator意味変更になるならSTOPしてUSER_DECISION_
REQUIRED。ユーザー試聴は、QA側の原因整理後に必要性を判断する。
4. A-Family / News: 日本人名の英語表記/読みについて、過去に「人名が
出たらネット検索して正しい英語表記/読みを事前確認し、TTS台本等へ反映
する」対策を実施した認識あり。Trial・Decision・CURRENT_SPEC・Production
code・Pronunciation Ledger系・Research/Search系を含めてRepo全体から
再調査すること。必ず確認するもの: 過去管理ID/Trial内容/ユーザー承認
有無/CURRENT_SPEC記載/Production初回経路への配線有無/Writer前処理・
Research・Ledger・TTS safe-readingのどこに存在するか/今回のHanshin記事
でなぜ発火しなかったか。既存対策が見つかった場合→新規対策を作らず、
今回の未発火理由/配線漏れ/適用漏れを特定。見つからない場合→その時点で
初めて新規対策Trial案を提示。
5. PM運用是正: 今後は「問題発生 → とりあえずHuman Review依頼」を基本
運用にしない。原則: 問題を検知→既存仕様/過去対策とreconcile→原因
切り分け→既存範囲で可能な最小Trial→結果整理→QCD比較→その上でユーザー
判断。Human Reviewは、機械的切り分けや既存対策で解けない最後の判断手段
として使う。ただし、新仕様・新閾値・意味変更・Production採用はユーザー
判断必須。
6. コスト報告ルールを今後固定: 記事制作Trial/Production runでは、必ず
「1記事あたりの総コスト」を報告する。単位: B1 + A2 を合わせた1記事一式。
Research / Ledger / Writer / Fact Check / Support / Key Phrase / TTS /
ASR / retry / regeneration を可能な範囲で含める。Trial特有の追加コストは
分離表示。TTSについては、同期実行とBatchで単価差がある場合、必ず分けて
示す。最低限、今回実測: 同期/実行経路ベースでいくら/量産想定: Batch
適用なら1記事いくら見込み/retry/Human Review由来の上振れ分、を明記する。
「今回¥xx」だけで終わらせない。量産原価として何が通常コストで、何が
Trial/異常対応コストかを分ける。
7. 今回の報告方法: まずコード変更や新Trialを勝手に広げず、上記1〜4に
ついて事実確認・既存対策照合・必要最小の追加検証結果をまとめること。
各項目はFamily/現象/既存対策/今回なぜ効かなかったか/追加Trial有無/
結果/Production判断が必要か、の順で報告。試聴を依頼する場合は、
ユーザーが実際にクリックして聞けるArtifact/playerリンクを必須とする。
ローカルファイルパスだけでHuman Review依頼しない。
```

Sonnet(sonnet-worker)が、Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-77-PM-OPERATION-CORRECTION-2026-09-12)に基づき、
上記ユーザー指示のうち**5(PM運用是正)・6(コスト報告ルール)・7の一部
(7項目順・試聴リンク必須)をPM_GOVERNANCE.mdへ正式反映**した。
1〜4(A2表記ゆれreconcile/B1B Secondary ASR+retry timing分析/
Repetition QA根本原因/News日本人名表記再調査)は、本タスクとは別に
並列稼働中の4件で個別に対応中であり、本タスクの範囲外(新規
`*_REPORT.md`・`er011_output/tts_retry_cooldown_analysis_01/`が対象、
本タスクでは触れていない)。

**反映内容**:

1. `docs/pm/PM_GOVERNANCE.md`新設14節「問題発生時のPM処理原則(Human
   Reviewは最後の手段)」: 問題検知時の処理順序7段階(検知→2-1
   Reconciliation Check→原因切り分け→既存範囲内の最小Trial→結果整理→
   QCD比較→ユーザー判断)を恒久ルール化。Human Reviewは機械的切り分け・
   既存対策で解けない場合の最後の判断手段と位置づけ。新仕様・新閾値・
   意味変更・Production採用は引き続き`USER_DECISION_REQUIRED`とする
   例外(11節のSTOP必須6条件、Gate 2と整合)を明記。2026-09-11の
   `PM-CLOSEOUT-CONSOLIDATION-76-TOWELS-AUDIO-HUMAN-REVIEW`(タオル音声
   Human Review依頼)を、reconcile・原因切り分けを経ずに試聴依頼のみで
   終えた**原則違反の事例**として14-4に明記した。
2. 新設15節「コスト報告ルール(1記事あたり総コスト)」: 記事制作
   Trial/Production runでは、B1+A2を合わせた1記事一式の総コストを
   Research/Ledger/Writer/Fact Check/Support/Key Phrase/TTS/ASR/
   retry/regeneration別に(取得不可な費目は理由付きで)報告すること、
   Trial特有の追加コストの分離表示、TTS同期(Standard)/Batchの単価差の
   分離表示、「今回実測/量産想定(Batch適用時)/retry・Human Review
   由来の上振れ分」の3区分を最低限明記することを恒久ルール化した。
3. 9節へ新小節「9-5. 問題対応報告の7項目順+試聴依頼のArtifact/player
   リンク必須」を追加。問題対応報告はFamily/現象/既存対策/今回なぜ
   効かなかったか/追加Trial有無/結果/Production判断が必要か、の7項目
   順で構成すること、試聴依頼はローカルファイルパスの提示だけで終わら
   せず実際にクリックして聴けるArtifact/player形式のリンクを必須と
   することを明記した(9-2の既存`file://`URL提示ルールを具体化・強化
   するものであり矛盾しない)。
4. `docs/pm/PM_BRIEF.md`へ14節・15節への案内(1〜2行)を追記した。
5. **コスト報告ルールの初回適用**: `FAMILY-A-DISCOVERY-GENERALIZATION-
   TOWELS-TRIAL-11-COST-01_REPORT.md`を新規作成し、タオルTrial-11
   (A2+B1B、1記事一式)の総コストを再集計した。text-gen(Research/
   Ledger/Writer/Fact Check/Support/Key Phrase、既存`cost_summary.json`
   の¥117.72と検算完全一致)、audio(TTS/ASR、OPEN-144のgemini_batch
   ¥0計上バグを訂正した実額¥62.83、公式script報告値¥12.76との差額
   ¥50.07)を合算し、**1記事一式の総コスト(訂正後、Batch実行ベース)
   =¥180.55**と算出した。retry/Human Review由来の上振れ分はaudio側
   (¥62.83)の内数で¥16.00(audio側の約25.5%、記事全体の約8.9%)。
   あわせて、本Trialが
   `TTS_EXECUTION_MODE`未指定によりGemini Batch API(既定値)経由で
   実行されていたこと(PM_GOVERNANCE 7-1「正式リリース前は原則
   Standard同期」との整合が本タスクの範囲では未確認であること)を
   **新たな観測事項として報告のみ**行った(コード修正・追加Trialは
   実施していない、`USER_DECISION_REQUIRED`候補として記録)。

**Production採用範囲外**: 本エントリはPM運用ルール(文書)の明文化と
既存Trial artifactの読み取り再集計のみであり、Production Prompt・
コード・費用集計script・TTS実行モードの変更、`APPROVED_FOR_PRODUCTION`
宣言はいずれも行っていない(追加API費用¥0)。並列稼働中の4件
(A2表記ゆれreconcile/B1B Secondary ASR+retry timing分析/Repetition QA
根本原因/News日本人名表記再調査)の生成物・出力先には一切触れていない。
`git stash`/`git clean`/他タスクファイルの`git checkout`は使用していない。

**反映範囲**: `docs/pm/PM_GOVERNANCE.md`(14節・15節新設、9-5新設、
ヘッダー「最終更新」・末尾「変更履歴」更新)、`docs/pm/PM_BRIEF.md`
(案内追記)、`docs/pm/ACTIVE_TASK.md`(固定ヘッダー更新)、本エントリ、
`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-COST-01_REPORT.md`
(新規作成)。`OPEN_ITEMS.md`・`CURRENT_SPEC.md`は本タスクでは編集して
いない(OPEN-144行の追記は別タスク[並列稼働中の4件]で対応予定)。

**根拠**: ユーザー指示(2026-09-12、上記原文)、Fable(PM)からの委任
(管理ID PM-CLOSEOUT-CONSOLIDATION-77-PM-OPERATION-CORRECTION-2026-09-12)。
詳細は`docs/pm/PM_GOVERNANCE.md`14節・15節・9-5、
`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-COST-01_REPORT.md`、
`docs/pm/RESULT_PACKET.md`参照。

## PM-CLOSEOUT-CONSOLIDATION-78-RECONCILE-RESULTS-2026-09-12: 並列稼働中だった4件のreconcile結果反映+Sonnet指示違反(LLM API呼び出し1回)の記録+新規OPEN-145/146起票

**日付**: 2026-09-12

**区分**: SSOT反映(reconcile調査4件の結果整理。コード・Prompt・Production実装の変更はゼロ)

**背景(Fable報告品質是正の経緯)**: 2026-09-12にユーザーが
`PM-CLOSEOUT-CONSOLIDATION-77-PM-OPERATION-CORRECTION-2026-09-12`原文
(同エントリ参照)で「問題が起きた→比較的マシなtakeをユーザーに聞いて
もらう」という運用を明確に問題視し、原因切り分け・既存対策との
reconcile・必要最小Trialまで進めてから判断材料を揃えて報告するよう
指示した。これを受けて並列稼働していた4件のSonnet委任reconcileタスク
が完了し、本エントリでその結果をSSOTへ反映する。

**反映内容**:

1. **A2表記ゆれ(comment_2)**
   (`FAMILY-A-DISCOVERY-TOWELS-A2-JA-ASR-VARIANT-RECONCILE-01`): 既存
   対策(JA ASR Validator読み一致判定+A2 Reading Resolver、いずれも
   Production配線済み)は対象範囲内だったが、依拠するpykakasi内蔵辞書
   (kanwadict)に「経つ」=「たつ」の読み候補が存在せず機能しなかった。
   過去18ペア中この型は1segmentのみ。候補A(閉じた補完テーブル追加)/
   候補B(辞書切替)は新仕様のためUSER_DECISION_REQUIRED、候補C(既存
   Human Review機構での試聴判断)のみ即応可能。**新規OPEN-145として
   起票**。
2. **B1B has/had・TTS retry timing再集計**
   (`FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-
   RECONCILE-01`): Secondary ASR Cascade・Connected Speech Equivalence
   Layerはいずれも「対象外」判定で設計通り発火せず(バグ・配線漏れでは
   ない)。Secondary ASR単独適用(実費用¥1.8)でも救済不可と確認。
   retry timing再集計は即時retry PASS率52.8%(N=53)、非即時41.2%
   (N=17)、Fisher p=0.578で有意差なし、事前定義の十分性基準は未達。
   **前回報告した非即時71.4%(N=7)は本再集計値41.2%(N=17)で上書き**。
   仕様採用せず継続観測。
3. **Repetition QA誤flagの根本原因**
   (`REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-02`):
   `tts_safe_number_words_en()`の綴り小数→算用数字変換後の
   canonical_textとRepetition QA専用ローカルASR(faster-whisper、綴り
   のまま書き起こし)の不一致による`canonical_repeat_count: 0`が根本
   原因と特定した。OPEN-127(em dash)・OPEN-121行既存記載の「%/percent」
   不一致(未修正)とは異なる**第3の独立したfailure mode**。既に
   `PRODUCTION_WIRED`のA-Family経路(`pool_pilot_01/pool_n4_supermarket`)
   でも再現することを確認した(単発のTrial限定事象ではない)。scratchpad
   prototype(¥0)で判定意味を変えない最小修正により誤flag3件解消・
   真陽性1件維持を確認したが、**Production/QAコードへは未実装**。
   実装可否・適用範囲・遡及点検要否はUSER_DECISION_REQUIRED。
4. **News人名ローマ字表記**
   (`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-RECONCILE-01`):
   「人名事前確認」専用対策は`NEW`(見つからなかった)。既存3機構
   (ER-009 JA Foreign Token Gate/Pronunciation Ledger/Fact Checker)は
   いずれも別目的。根本要因はVerified Fact Ledgerが人名を日本語表記
   のみで保持し英語canonical spellingを持たないため、WriterがRun毎に
   ローマ字を推測し揺れること、およびPoint Overlap GateがFact Checker
   より先行しGate NGで到達率1/6と低いこと。候補(a)Ledgerへ英語表記
   併記/(b)Gate順序見直し(STOP必須級)/(c)現状維持はUSER_DECISION_
   REQUIRED。**新規OPEN-146として起票**。
5. **Sonnet指示違反の記録**: 項目1のreconcile作業中、Sonnet
   (sonnet-worker)が「offline関数呼び出しのみ・API支出禁止」という
   本タスクの指示に反し、`er011_a2_reading_resolver_01.resolve_
   reading_diff()`を`FEATURE_FLAG_A2_READING_RESOLVER_ENABLED`を無効化
   せずに1回呼び出し、Resolver用LLM(`A2_SUPPORT`ルーティング、
   `reasoning.effort=low`)への課金API呼び出しが実際に発生した(対象語
   「にお→臭」、`resolver_calls=1`、金額はごく小さいと推測されるが
   正式な金額確認は未実施)。当該REPORT自身が違反を隠さず開示しており
   (`FAMILY-A-DISCOVERY-TOWELS-A2-JA-ASR-VARIANT-RECONCILE-01_
   REPORT.md`前提節)、以降の全呼び出しはFEATURE_FLAG明示的Falseで
   実施し直したことを確認した。金額確認・是正要否はユーザー判断待ち
   (本エントリでは追加対応していない)。
6. **OPEN-144(TTS費用集計バグ)への補正額反映**: タオルTrial-11
   (A2+B1B)の1記事一式総コスト(訂正後、Batch実行ベース)=¥180.55
   (うちretry/Human Review由来¥16.00)をOPEN-144行へ追記した。

**反映範囲**: `OPEN_ITEMS.md`(OPEN-121行・OPEN-135行・OPEN-144行への
追記、新規OPEN-145・OPEN-146起票)、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`
(reconcile4件の実績行追加)、`docs/pm/ACTIVE_TASK.md`(固定ヘッダー
UDR-blocking 9項目列挙)、本エントリ+索引1行。上記4件の各`*_REPORT.md`
本体・`er011_output/discovery_generalization_towels_trial_11/b1b/audit/`
配下の新規診断JSON2件・`er011_output/tts_retry_timing_monitor_01/`・
`er011_output/tts_retry_cooldown_analysis_01/`の再実行更新分はGit記録
対象(下記「根拠」参照)。`CURRENT_SPEC.md`は本タスクでは編集していない。

**Production採用範囲外**: 本エントリはSSOT反映(4件のreconcile結果の
記録)のみであり、Production Prompt・コード・費用集計script・TTS
Validator・Repetition QA moduleの変更、`APPROVED_FOR_PRODUCTION`宣言は
いずれも行っていない。UDRの代行判断もしていない。`git stash`/
`git clean`/他タスクファイルの`git checkout`は使用していない。

**根拠**: Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-78-RECONCILE-RESULTS-2026-09-12)、上記4件の
`*_REPORT.md`。詳細は各REPORT本文、`OPEN_ITEMS.md` OPEN-121/135/144/
145/146行、`docs/pm/RESULT_PACKET.md`参照。

## PM-CLOSEOUT-CONSOLIDATION-79-USER-CORRECTION-2026-09-12-02: ユーザー2回目の是正指示のSSOT反映

**日付**: 2026-09-12

**区分**: SSOT反映(ユーザー是正指示の記録+PM_GOVERNANCE/OPEN_ITEMS.md/
ACTIVE_TASK.mdへの反映。コード・Prompt・Production実装の変更はゼロ、
API支出ゼロ)

**背景**: `PM-CLOSEOUT-CONSOLIDATION-78-RECONCILE-RESULTS-2026-09-12`の
reconcile結果報告に対し、ユーザーが同日2回目の是正指示(原文全文は
下記)を出した。本エントリはこの指示の全文を記録し、反映箇所を整理する。

**ユーザー指示原文(全文、2026-09-12第2回)**:

```
【ユーザー回答・是正指示:今回の残件まとめ】
今回の個別問題だけを直すのではなく、同じfailure modeが再発しないところまで原因を一般化して対策してください。
1. A-Family / Discovery / A2 日本語ASR表記ゆれ対策: 「たつ⇔経つ」だけを追加する個別対応は禁止。今回の目的は、日本語ASRで一般的・高頻度に起こる ひらがな⇔漢字/ひらがな⇔カタカナ/同音異表記/一般的な送り仮名・表記差 等を一通りカバーし、同種問題が基本的に再発しない水準まで対策すること。過去ログに出た語だけでなく、一般的な日本語音声で高頻度に起こり得る表記差も対象にする。極めて稀な特殊語まで無制限に辞書化する必要はないが、「また別の一般語で発生したら都度追加」は不可。既存Reading Resolver / 日本語ASR正規化 / 過去Human Review対策をreconcileし、既存機構の拡張/補助読みテーブル/正規化層/既存ライブラリ活用 等を比較した上で最小Trialを実施する。受入観点: 今回の「たつ/経つ」「におい/ニオイ/臭い」が解消/過去既知事例が解消/一般的・高頻度の未出ケースでも通る/true content mismatchを誤PASSしない/過去正常判定を壊さない/offline regression PASS。Trial closeoutはREJECTED / VALIDATED / USER_DECISION_REQUIRED。Production採用はユーザー判断後。
2. A-Family / Discovery / B1 full_story_part1 の has / had: take5の該当箇所だけユーザーが試聴する。Primary / Secondary ASRとも`had dried`なら、実音声が本当に`had`なのかをまず確認する。実音声も`had`なら、これはASR誤判定ではなくTTS実発話エラーなので、以後の対策方針を切り替えること。また、take1〜3で「2022 survey...」欠落、take4以降で欠落が解消した事実があるため、既存のTTS retry timing監視結果を再集計して先に報告すること。最低限: 即時retry/非即時retry/連続NG後の次attempt PASS率/人的介入あり・なし を分ける。「時間を空けるretry」を正式仕様へ入れるかは、集計結果を見てユーザーが判断する。現時点で自動採用しない。
3. 共通 / Repetition QA: 既に承認した方針どおり、数字↔数詞の同値化をProduction Gateへ実装する。判定閾値や`canonical_repeat_count >= 2`の意味は変えず、比較前の正規化だけを追加。回帰テスト、過去flag記録の再判定、真陽性が消えないことを確認する。`% ↔ percent`は今回含めない。別判断。既存A-Family Production音声は、¥0の機械的遡及再判定を実施。音声再生成・成果物差し替えは自動で行わない。full_story_part2は、修正後の再判定を先に行い、PASSするならユーザー試聴不要。この項目はユーザー正式採用済みなのでAPPROVED_FOR_PRODUCTION。Gate 3完了までPRODUCTION_WIREDにしない。
4. A-Family / News 日本人名の英語表記: 過去に対策を行った認識があるため、Trial / Decision / CURRENT_SPEC / Production code / Research / Search / Ledger / Pronunciation関連を再度確認する。ただし再調査して本当に「日本人名の英語表記をWeb検索で事前確認し、Writer/TTS用の正しい表記へ反映する仕組み」が存在しないなら、新規対策案をPM側で設計すること。ユーザーへいきなり方式選択を投げず、最低限、既存Ledgerとの統合/公式英語表記をResearch段階で取得/Writerへcanonical spellingを供給/Fact Checkerでの最終照合 等の候補を比較し、品質・コスト・実装影響・再発防止力を整理したTrial案を提示する。「人名ごとに誤ったら個別修正」は不可。failure modeとして対策する。
5. 共通 / TTS運用ルール: Trial / 開発は Standard同期へ戻す。開発はスピード優先。数十円・百円を節約するために、検証速度・デバッグ性・原因切り分け性能を落とさない。一方、量産Productionはコスト優先。1円/記事でも大量生成では大きな差になるため、Batch等を使って1記事原価を最適化する。つまり、Development cost と Production unit cost は別軸で管理する。今後、Trial / 開発:Standard同期を基本/量産:Batch前提で最適化 とする。この考え方をPM運用へ明文化すること。
6. 共通 / コスト報告ルール: 今後、記事制作Trial / Production runでは必ず「1記事あたり総コスト」を報告する。単位はB1 + A2を合わせた1記事一式。可能な限り、Research/Ledger/Writer/Fact Check/Support/Key Phrase/TTS/ASR/retry / regeneration を含める。必ず分けて表示すること: 今回実測コスト/Trial特有の追加コスト/異常retry / Human Review由来の上振れ/Standard同期でのコスト/Batch量産時ならいくらになるか。TTSがStandard / Batchで単価差がある場合は必ず明記する。「今回¥xx」だけでは不可。量産時の1記事原価が分かる形で出すこと。
7. 共通 / Gemini Batch費用集計バグ: OPEN-144は修正着手。`gemini_batch`を¥0計上している集計バグを是正し、同型scriptも影響範囲確認。生成経路は変更せず、まず費用集計の正確性を直す。過去費用報告への影響範囲も整理して報告する。
8. PM運用の再発防止: 今後、「問題が起きた → 比較的マシなtakeをユーザーに聞いてもらう」を基本運用にしない。原則: 問題検知→既存仕様・過去対策reconcile→原因切り分け→failure mode一般化→必要最小Trial→QCD比較→ユーザー判断材料を提示。Human Reviewは、機械的に切り分け可能な問題を棚上げする手段ではない。ユーザー試聴を依頼するのは、原因・既存対策・Trial結果が整理され、本当に人間の耳でしか判断できない段階に到達してから。また、試聴依頼時はローカルpathではなく、必ずユーザーがクリックできるArtifact / playerリンクを提示する。個別修正の積み重ねではなく、再発可能な問題はfailure mode単位で閉じること。
```

**反映箇所**:

1. **OPEN-121**(Repetition QA数字↔数詞同値化): Statusへ
   「数字↔数詞同値化部分のみ`APPROVED_FOR_PRODUCTION`」(Gate 3完了まで
   `PRODUCTION_WIRED`としない、"%"↔"percent"は範囲外・別判断)を追記。
   実装範囲(4segment全体)・遡及再判定(¥0機械的のみ、差し替え自動
   なし)・`full_story_part2`はPASSならユーザー試聴不要、を追記した
   (原文3)。
2. **OPEN-135**(Discovery B1B has/had・News人名・TTS retry timing):
   take5該当箇所のみユーザー試聴し実音声確認する方針、実音声も"had"
   ならTTS実発話エラーとして方針切替、retry timing再集計値(即時
   52.83% N=53/短40.0% N=10/中25.0% N=4/長66.67% N=3、連続NG回数別・
   人的介入有無別、Fisher p=0.578で基準未達・自動採用しない)を追記
   した(原文2)。
3. **OPEN-142/OPEN-143**: Development cost(開発Token)とProduction
   unit cost(量産API原価)を別軸で管理する方針を追記した(原文5)。
4. **OPEN-144**: 修正着手をユーザーが承認したこと(生成経路は変更せず
   費用集計の正確性のみ是正、過去費用報告への影響範囲整理も報告)を
   追記した(原文7)。
5. **OPEN-145**(新規、日本語読み辞書): 個別対応(候補Aの「たつ/経つ」
   限定追加)を禁止し、failure mode一般化Trial(管理ID
   `JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01`)実施中である
   ことと受入観点6項目を追記した(原文1)。
6. **OPEN-146**(新規、News人名英語表記): 人名ごとの個別修正を禁止し、
   既存Ledger統合/Research段階取得/Writerへのcanonical spelling供給/
   Fact Checker照合等の候補比較Trial設計中であることを追記した
   (原文4)。
7. **`docs/pm/PM_GOVERNANCE.md`**: 14-1へ「4. failure mode一般化」
   段階を追加し7段階へ更新、「個別修正の禁止」を明記(14-5に経緯追記、
   原文8)。新小節「7-4. TTS実行モードの運用: Development cost /
   Production unit costの別軸管理」を新設(原文5)。15-5(コスト報告
   ルールの最低限区分)を旧3区分から「今回実測/Trial特有の追加
   コスト/異常retry・Human Review由来の上振れ/Standard同期での
   コスト/Batch量産換算時のコスト」の5区分へ更新(原文6)。9-5
   (試聴依頼のArtifact/playerリンク必須)を再確認(原文8)。
8. **`docs/pm/PM_BRIEF.md`**: 上記PM_GOVERNANCE更新箇所への案内文を
   更新した。
9. **`docs/pm/ACTIVE_TASK.md`**: 固定ヘッダのAPPROVED未配線
   (OPEN-120 3V、OPEN-121数字↔数詞同値化)・UDR-blocking(読み辞書=
   Trial結果待ち、take5試聴=clip準備中、人名=設計待ち、Batch既定=
   原文5で解決しUDR解除)・並列稼働中4件を更新した。

**反映範囲**: `OPEN_ITEMS.md`(OPEN-121/135/142/143/144/145/146行)、
`docs/pm/PM_GOVERNANCE.md`(7-4新設・14-1/14-5・15-5/15-7・9-5)、
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`、本エントリ+索引1行。
並列稼働中4件(JA ASR表記ゆれ一般化Trial/OPEN-144修正+TTSモード分離+
take5 clip/人名英語表記Trial設計/Repetition QA数字↔数詞同値化実装)の
生成物・コード・`er011_output/`配下は本タスクでは一切変更していない。

**Production採用範囲外**: 本エントリはSSOT反映(ユーザー指示原文の
記録+反映箇所の整理)のみであり、Production Prompt・コード・費用
集計script・TTS Validator・Repetition QA moduleの実装変更、
`APPROVED_FOR_PRODUCTION`の新規宣言(OPEN-121は本エントリで反映する
がユーザーが既に明示した決定の記録であり、本タスクによる独自判断
ではない)はいずれも行っていない。並列稼働中4件への介入・生成物への
`git add`もしていない。`git stash`/`git clean`/他タスクファイルの
`git checkout`は使用していない。

**根拠**: Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-79-USER-CORRECTION-2026-09-12-02)、ユーザー
指示原文(上記)。詳細は`OPEN_ITEMS.md` OPEN-121/135/142/143/144/145/
146行、`docs/pm/PM_GOVERNANCE.md`該当節、`docs/pm/RESULT_PACKET.md`
参照。

## PM-CLOSEOUT-CONSOLIDATION-80-REPETITION-QA-NUMBER-WORD-FIX: OPEN-121数字↔数詞同値化Production実装完了のSSOT反映+Gate 3個別判定表+タオルB1B full_story_part2採用+News人名Trial設計完了の反映

**日付**: 2026-09-12

**区分**: SSOT反映+Git統合(実装自体は並列稼働の別タスク`OPEN-121-
REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01`で完了済み。
本タスクはその結果のSSOT反映・Gate 3進捗の個別判定・commit/pushのみ)

**背景**: `PM-CLOSEOUT-CONSOLIDATION-79-USER-CORRECTION-2026-09-12-02`
で記録したユーザー承認(OPEN-121数字↔数詞同値化=`APPROVED_FOR_
PRODUCTION`)に基づき、並列タスクが実装・回帰テスト・¥0遡及再判定・
タオルB1B `full_story_part2`再判定を完了した
(`OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01_
REPORT.md`)。本タスクはこの結果をSSOTへ反映し、`docs/pm/
PM_GOVERNANCE.md`Gate 3 Production Wiring Checklistの各項目を個別に
判定した。あわせて、並列タスク`FAMILY-A-NEWS-JA-PERSON-NAME-
ROMANIZATION-TRIAL-DESIGN-01`(OPEN-146の候補比較Trial設計)が完了
したためその結果も反映した。

**実装内容(先行タスクで完了済み、本タスクで独立再確認)**:
`er011_open121_repetition_qa_production_01.py`へ`_normalize_token_
numeric_equiv()`を新設し、canonical側`_normalize_tokens()`・ASR側
`detect_ngram_repetition()`の両方へ、綴り小数(two〜twelve)↔算用数字
の同値化を比較前に適用した(判定閾値`canonical_repeat_count>=2`・
方式D/D'の閾値・`%`/`percent`対象外は無変更)。本タスクで
`er011_open121_repetition_qa_production_wiring_01_test_01.py`(35件)・
`er011_open128_method_d_local_asr_confirm_production_wiring_01_test_
01.py`(9件)を独立再実行し、いずれも実測PASS(`Ran 35 tests ... OK`・
`Ran 9 tests ... OK`)を確認した。project-wide regressionは先行タスク
実測値(collected=2309、passed=2306、failed=3[既知の無関係failureの
み])をそのまま引用(本タスクでは再実行していない)。

**¥0遡及再判定・タオルB1B `full_story_part2`採用**: 誤flag3件(タオル
Trial-11 B1B `full_story_part2`、`pool_n4_supermarket`A2/B1B、いずれも
"after two/three months"型)が解消し、既知真陽性2件は退行なく維持
されたことを確認した。`pool_n4_supermarket`は既に`PRODUCTION_WIRED`
済みのA-Family既存音声だが、生成当時Repetition QAが未配線だったため
実際のretry・差し替えは発生しておらず、音声ファイルは無変更。タオル
Trial-11 B1B `full_story_part2`は、内容一致していた4取り(attempt2,3,
5,6)全てが修正後QAでPASSしたため、ユーザー事前承認どおり試聴なしで
既存採用規則(最初にPASSした取り)に従いattempt2を採用し、
`review_lock_state.json`をRESOLVEDへ更新した(TTS再生成なし、¥0)。
これによりタオルTrial-11 B1Bの残Human Reviewは`full_story_part1`
(take5試聴待ち)と`comment_2`(表記ゆれTrial待ち)の2件のみとなった。
`tts_generation_results.json`側の該当attempt記録の同期は本タスクでは
未実施のまま(Episode Assembly実施前に同期手順の実施が必要、A2
`meaning_4`と同種の既知の未同期状態)。

**Gate 3 Production Wiring Checklist個別判定**(`docs/pm/
PM_GOVERNANCE.md`2節、14項目中12項目完了・2項目未完了):

| 項目 | 判定 | 根拠 |
|---|---|---|
| Production正式初回経路 | 済 | `er011_open121_repetition_qa_production_01.py`が既にA2/B1本文4segment用Production経路4ファイル(`er003_v1_n3_01_tts_generate.py`/`er003_v1_repro01_main_generate.py`/`er003_v1_crosslevel_audio_02_common.py`/`er003_v1_sing01_news_tail_fix.py`)からimport・呼び出し済みとGrepで実証、修正は同一共有module内部関数のみのため既存配線経由で自動反映される |
| retry・fallback・regenerationとの整合 | 済 | `apply_repetition_qa_gate()`・既存AND gate・Human Review Lock遷移・閾値は無変更(diff確認・回帰PASS) |
| DEV・Trial-onlyでないこと | 済 | Trial専用ファイルではなくProduction共有module本体への実装 |
| Production runtimeでの実発火 | **未完了** | 次回、数字↔数詞パターンを含む実記事のProduction run(`enable_repetition_qa=True`経路)での実発火が必要。今回の遡及再判定はいずれもoffline(既存記録・過去wavへの事後再計算のみ) |
| 必要testのPASS | 済 | 新規5件+既存30件(35件、本タスクで独立再実行しPASS実測)・依存9件(同)・project-wide regression(先行タスク実測値、既知3件failureのみ) |
| runtime evidence | **未完了** | 上記のとおり実発火未確認のため |
| 実際のmodel_id・routing確認 | 該当なし | LLM呼び出しを伴わない音声/ASR比較ロジックのみ |
| コスト影響評価 | 済 | ¥0(追加API呼び出しなし、ローカル計算・既存wav複製のみ) |
| `CURRENT_SPEC.md` | 済 | 「TTS Repetition/False Start QA」行へ本タスクで1行追記 |
| `DECISION_LOG.md` | 済 | 本エントリ |
| `OPEN_ITEMS.md` | 済 | OPEN-121/135行(本タスク) |
| 必要なGit反映 | 済 | 本タスクでcommit |
| approved specとProduction挙動の一致 | 済 | 2026-09-12ユーザー承認範囲(2〜12、%は対象外)と実装が一致(回帰テスト`test_d_percent_and_percent_word_not_equivalenced`・`test_e_range_boundary_one_twelve_thirteen`で固定) |

未完了2項目(Production runtimeでの実発火・runtime evidence)が残る
ため、`PRODUCTION_WIRED`は宣言しない。Statusは`APPROVED_FOR_
PRODUCTION`(Gate 3進行中)のまま維持する。

**News人名英語表記Trial設計(OPEN-146)の反映**: 並列タスク
`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01`
(read-only設計)が完了した。既存Ledger統合/Research段階取得/Writer
供給/Fact Checker照合を横断した4候補+組み合わせを5軸で比較し、
候補(a)(Verified Fact Ledgerへ`canonical_en_spelling`追加、既存Gate
順序を変えない予防策、見込み¥100〜200/記事)を推奨、候補(c)(Gate順序
変更)はSTOP必須級と整理した。あわせて`generate_test.py`(既存SSOTで
「無関係な別番組専用」と明記済み)に2026-07-14時点の死蔵コード
(`NAME_GLOSSARY`/`verify_romanization`、Writerプロンプトへ未配線の
まま)を新規発見した。実装・Trial実施はいずれもゼロ、採否は
`USER_DECISION_REQUIRED`のまま。

**反映範囲**: `OPEN_ITEMS.md`(OPEN-121/135/146行)、`CURRENT_SPEC.md`
(「TTS Repetition/False Start QA」行)、本エントリ+索引1行、
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`(1行)、`docs/pm/ACTIVE_TASK.md`
固定ヘッダ。Git反映: `er011_open121_repetition_qa_production_01.py`・
`er011_open121_repetition_qa_production_wiring_01_test_01.py`・
`OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01_
REPORT.md`・`er011_output/discovery_generalization_towels_trial_11/
b1b/audit/review_lock_state.json`・`FAMILY-A-NEWS-JA-PERSON-NAME-
ROMANIZATION-TRIAL-DESIGN-01_REPORT.md`・上記SSOTファイルをcommit。
並列稼働中4件(JA ASR表記ゆれ一般化Trial/OPEN-144修正+TTSモード分離
+take5 clip生成/News人名英語表記Trial設計[本タスクで結果反映済みの
ため終了]/Repetition QA数字↔数詞同値化実装[本タスクで結果反映済み
のため終了])のうち残る2件(JA ASR表記ゆれ一般化Trial、OPEN-144修正+
TTSモード分離+take5 clip生成)の生成物・コードには一切触れていない。
`git stash`/`git clean`/他タスクファイルの`git checkout`は使用して
いない。

**Production採用範囲外**: `PRODUCTION_WIRED`の新規宣言はしていない
(Gate 3の2項目が未完了のため`APPROVED_FOR_PRODUCTION`[Gate 3進行中]
のまま)。コード実装自体は先行する並列タスクで完了済みであり、本
タスクはその結果の検証済み再確認・SSOT反映・Git統合のみ。

**根拠**: Fable(PM)からの委任(管理ID
PM-CLOSEOUT-CONSOLIDATION-80-REPETITION-QA-NUMBER-WORD-FIX)、
`OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01_
REPORT.md`、`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-
DESIGN-01_REPORT.md`。詳細は`OPEN_ITEMS.md`OPEN-121/135/146行、
`docs/pm/RESULT_PACKET.md`参照。

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[HISTORY_INDEX.md](HISTORY_INDEX.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)
