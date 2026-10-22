FABLE-DELEGATION-MARKER: PNPS-STAGE1-E1-委任_03-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_03 [E-1]: 固有名詞発音取得改善 Stage 1(承認済み)のProduction実装設計書+承認記録+保存データでの効果測定(API 0)+Stage 2計画v3(ユーザー方針の反映)。**Production .pyの編集はまだ行わない**=Opus独立レビュー(11-3条件A)後、かつKP両方PASS配線(D-2、`er006_secondary_asr_01.py`編集中)の完了後にE-2で行う。API 0・JPY0)

## 0. 運用ルール・並列注意
他agent稼働中: (D-2)KP両方PASS=`er078_*`/`er006_secondary_asr_01.py`/`er003_v1_repro01_main_generate.py`/`er019_family_x_kp_en_k2_store_01.py`/`er063_*`/CURRENT_SPEC ASR節、(C-2)B3丸め=`er019_family_x_entertainment_production_runner_01.py`/`er053_*`/`er095_*`。あなたは`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`・新規未配線module/test(`er097_*`)・SSOT行のみ。Production .py編集禁止。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`)編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。有料API/Web取得禁止。コード行番号は`git show HEAD:`基準。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_STAGE1-GO-STAGE2-POLICY_USER.md`へ本文無改変で保存、文字数・sha256記録)
---
# Claude Codeへの指示
## 固有名詞の発音取得改善 — Stage 1実施＋Stage 2計画更新

### 1. 目的とユーザー承認

eigo-radioは**英語学習サービス**であり、固有名詞の公式発音を厳密に調査すること自体が目的ではない。

目標は、英語学習に適した自然で合理的な発音を確保し、不要なHuman ReviewやTTS再生成を減らしながら、低コストで量産できる状態を作ること。

今回、ユーザーは以下を承認した。

1. **Stage 1の実施**：発音のPASS/NG基準を変更せず、不要調査の削減・発音情報管理を改善する。
2. **Stage 2の進め方**：Stage 1の結果を踏まえてTrialを判断する。現時点でTrial実行・Production採用は未承認。
3. **公式発音が不明な場合の方針**：合理的な英語発音であれば、警告付き自動PASSを基本的に許容する。
4. 発音の根拠は、公式情報→英語圏での実際の呼ばれ方→合理的な英語発音の順に優先する。

上記を計画・SSOTへ反映する。

---

### 2. Stage 1：承認済み改善の実施

計画v2のStage 1を実施する。

対象：

- 調査しても発音情報が見つからなかった語の否定記録（計画上60日間再検索を抑止）。
- Ledgerのentity_type違いによる登録情報の取りこぼし解消。
- `main story` など、一般語の誤検出による不要調査の除外。
- Human Review画面での発音情報の信頼度・根拠表示。
- 発音情報登録時の引用実在確認。
- 既存の保存データを使った効果測定。
- 複数発音候補の既存判定との整合確認。

**Stage 1では、発音の合否判定基準・自動PASS条件を変更しないこと。**

承認済みの範囲で、調査→実装→Regression→Production配線→runtime evidence→SSOT/Git反映まで自律的に進める。

Family X/Zの共通経路・retry/fallback等への影響も確認する。

Production実走証拠が不足する場合は、完了と誤認せず残事項を明示する。

### 3. Stage 2：発音判断方針の更新

Stage 2の改善計画に、以下の方針を組み込む。

#### 発音の根拠の優先順位

**第1優先：公式発音**

- 企業・団体・権利者等が公開した英語発音。
- 公式の音声・動画や信頼できる公式資料を使用。

**第2優先：英語圏での実際の呼ばれ方**

- 英語のインタビュー、ニュース、動画、音声等で実際にどう呼ばれているか確認。
- 情報源の信頼性と、その呼び方が対象の固有名詞を指していることを確認。
- 単なる綴りの一致や、別人・別ブランドの発音を根拠としない。

**第3優先：合理的な英語発音**

- 公式情報・実際の使用例が見つからない場合、英語の一般的な発音規則や既存辞書を活用して合理的な発音を推定。
- 複数候補がある場合は、自然さ・発音規則・文脈を考慮する。
- 推定発音を公式発音と偽らず、Ledgerで根拠と信頼度を区別する。

#### 警告付きPASS

公式発音が確認できなくても、合理的な発音とTTS音声が一致する場合は、**警告付き自動PASSを基本的に許容する設計**とする。

- 警告は原則として内部記録用であり、通常の量産を停止させない。
- 「公式発音未確認」と「明確な誤発音」を区別する。
- 発音情報の確からしさと、TTSがその発音を実現しているかは別々に評価する。
- 明らかな誤発音、音素差、脱落等は従来どおりNG。
- 不適切な推定発音がLedgerへ登録・再利用され続けるリスクを防ぐ。
- Human Reviewは、AI側で合理的に判断できない本質的な品質問題に限定する。

なお、これは**Stage 2の設計方針の承認**であり、現行Productionの自動PASS条件を直ちに変更する承認ではない。

### 4. 調査費用の最適化

正しい発音情報の取得は「必要な場合のみ」という原則を維持する。

- CMU辞書・既存Ledgerで解決できる語は原則として再調査しない。ただし、ByUs型の同綴り衝突リスクには対応する。
- 未解決語も、既存の同音救済等で解決すれば追加調査しない。
- 英語圏の実使用例を調査する場合、無料・低コストな方法を優先する。
- 調査が高額、または信頼できる結果を得られる見込みが低い場合、合理的な発音推定へ切り替える。
- 同じ語の調査を何度も繰り返さない。
- 検証済み情報を記事横断で再利用する。

品質を守りつつ、量産単価70円／記事セットへの影響を最小化すること。

特に、公式発音が見つからないことだけを理由に高額な検索を繰り返したり、Human Reviewへ転送したりしない。

### 5. Stage 2の計画・Trial設計

ClaudeはStage 1の結果を踏まえ、Stage 2の改善計画を更新する。

検討事項：

1. 公式発音・英語圏の使用実態・合理的推定をどう区別し、Ledgerへ登録するか。
2. 英語圏での実際の呼ばれ方を、費用を抑えて確認する方法。
3. 合理的発音推定の具体的な判断方法。
4. 警告付きPASSの発動条件と誤PASS防止策。
5. 同音判定Validatorへの発音情報供給方法。
6. 複数発音候補、同綴り衝突、辞書外語の扱い。
7. 既存のPrimary／Secondary合格条件との整合。
8. 誤発音と公式発音未確認を区別するTrialケース。
9. Family X/Z共通配線と将来のFamily Yへの展開。
10. API費用、調査頻度、キャッシュによる量産単価への影響。

Trialでは特に、**公式発音が存在しない・確認できないケースでも、合理的な発音なら不必要に停止せず、実際の誤発音はNGにできるか**を検証すること。

Fableに改善計画を独立レビューさせ、より安全・単純・低コストな代替方式があれば採用する。

ただし、新たな品質基準の変更やProduction実装はユーザーの正式承認を必要とする。

### 6. QCD・実施条件

優先順位は以下。

**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- Stage 1は承認範囲内で自律的に完了させる。
- Stage 2の計画更新はStage 1と並行できる部分を先行する。
- Stage 1の実測結果が必要な部分のみ、結果確定後に反映する。
- 不要な待機・日付分割・逐次処理をしない。
- 既存の仕組みを最大限再利用する。
- 少額費用ごとの不要な承認要求を行わない。
- 既存の予算・STOP条件を厳守する。
- 誤PASSを避けるための仕組みが過剰な費用・Human Review・量産停止を生まないようにする。

### 7. 最終報告

**A：Stage 1**

- 何を改善したか。
- 不要調査がどれだけ減ったか。
- 発音判定基準が変わっていない証拠。
- Family X/Z双方のProduction配線・検証状況。
- QCD効果、SSOT/Git反映、最終Status。

**B：Stage 2**

- 推奨する発音取得・選定方式。
- 英語圏での実際の呼ばれ方をどう調べるか。
- 公式未確認時に、何を根拠として合理的な発音を選ぶか。
- 警告付きPASSの安全条件。
- ByUsを使った具体的な判定例。
- Fableレビュー結果。
- Trial内容・費用・受入条件。
- ユーザー判断が必要な事項。

管理番号だけで報告せず、必ず内容がわかる名称を使用すること。

**Stage 1はProduction改善まで、Stage 2はレビュー済み計画の提出までを今回の完了条件とする。**

Stage 2のTrial・Production採用には無断で進まないこと。
---

## 2. 前提(計画v2、commit 0dd073018)
`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/{PLAN_01.md(v2-0〜9), PLAN_SUMMARY_01.md, DESIGN_OPTIONS_01.md, INVESTIGATION_01.md, REVIEW_POINTS_01.md, fr04_early_trigger_estimate_01.py}`、OPEN-441 `PLAN_V2_PENDING_USER`。Stage 1項目=否定記録/entity_type非依存lookup/一般語誤トリガー除外/HR階層表示/登録時の引用実在確認(V1')。既存機構: `er006_pronunciation_ledger_01.py:77-98,140-191,237-283`、`er006_pronunciation_research_01.py:72-80`、`er006_secondary_asr_01.py:331,341-387,1056-1070`(最終slot調査・HRパッケージ)、`er006_m1_multi_candidate_01.py:91,208-250`(M1、IPA→ARPAbet変換器)、登録validator(PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01、OPEN-436)、HR表示ルール(a)〜(f)(CURRENT_SPEC:1837)。

## 3. 作業
### 3-A 承認記録(SSOT)
`DECISION_LOG.md`へエントリ(原文§1の1〜4逐語: Stage 1実施承認/Stage 2はStage 1結果を踏まえ判断・Trial/Production未承認/公式不明時は合理的英語発音で警告付き自動PASSを基本許容=**Stage 2の設計方針の承認であり現行自動PASS条件の変更承認ではない**/根拠優先順位 公式→英語圏の実際の呼ばれ方→合理的英語発音)。`OPEN_ITEMS.md` OPEN-441→`STAGE1_APPROVED_IMPL_IN_PROGRESS / STAGE2_PLAN_V3_IN_PROGRESS`。`docs/pm/USER_DECISION_REGISTER_01.md`: 新番号で「Stage 1実施」判断済み、「Stage 2方針(警告付きPASS許容・根拠優先順位)」判断済み(設計方針)、#133行に注記。REPORT_LEDGER。

### 3-B Stage 1 実装設計書 `STAGE1_IMPLEMENTATION_DESIGN_01.md`(Opusレビュー用)
各項目について: 配線点(ファイル:行、HEAD基準)/最小diff/Family X/Z共通経路(統一judge・Secondary adapter)とretry/fallback/resumeへの影響/「合否判定基準・自動PASS条件を変えない」ことの保証(判定関数の入出力不変、変わるのは「調査を呼ぶか」「Ledger lookupの命中」「HR表示」「登録validator」のみ)/rollback定数/test計画/runtime evidence計画(費用: 否定記録の実証には最終slot調査1回≈PNEP実測5.4円を上限1回、他はAPI 0の再生で可。合計≈JPY10以内)。
1. **否定記録**: Ledger entryの任意キー(`negative_cache`: 調査日時・TTL60日暫定・理由)。key=正規化token(entity_type非依存)。一時失敗(枠切れ/HTTP/timeout)は保存しない。人間承認・新登録で即無効化。否定記録中はHRパッケージに「調査済み・未取得(日付)」表示。
2. **entity_type非依存lookup**: 同綴りentryのうち最上位(human_approved>high>medium…)を返す統一lookup。現行の取りこぼし事例(melos/muse等)を再現testに。
3. **一般語誤トリガー除外**: `main story`/`plus`/`us`/`mini`等の一般語(CMU収録かつentity_likeでない/stopword)を最終slot調査の対象から除外。除外は「調査を呼ばない」だけで、判定(NG/UNCERTAIN)は不変。OPEN-436隔離との関係を明記。
4. **HR階層表示**: HRパッケージ(CURRENT_SPEC:1837の(a)〜(f))に「根拠階層(公式/英語圏実使用/合理的推定/辞書/未確認)」「出典URL・引用」「否定記録」を追加(表示のみ)。
5. **引用実在確認(V1')**: 登録validatorに「出典URLを取得し引用文が本文に実在するか」を追加(安全条件: 読み取り専用・サイズ上限・timeout・HTMLテキスト抽出のみ・専用dir保存・スクリプト実行なし)。失敗時は登録を`unverified`階層に落とす(拒否ではない)。**Stage 1では階層をPASS根拠にしない(表示・管理のみ)**。
6. **効果測定(API 0)**: 保存HR queue/telemetry/attempt_historyで、Stage 1適用後に省ける調査数・HR表示改善数を再集計(v2のFR-04試算: 24ペア中11ペア46%省略見込みを、実装仕様に合わせて再計算)。
7. **M1整合確認**: M1が同じLedgerを読む箇所で、否定記録・統一lookup・階層キーの追加がM1候補集合を**変えない**ことをreplayで確認(0円)。変わる場合は設計を修正(Stage 1では変えない)。

### 3-C 未配線module先行(API 0)
`er097_pronunciation_supply_stage1_01.py`(純関数: 否定記録の判定・統一lookup・一般語除外判定・V1'のURL取得/照合[テストはモック]・HR表示用の階層整形)+`er097_..._test_01.py`。Production .pyは編集しない(`git diff HEAD`で確認)。

### 3-D Stage 2 計画v3(ユーザー§3〜§5の方針反映。Stage 1実測が必要な箇所は「Stage 1結果で更新」と明示)
`PLAN_01.md`にv3節を追加、`PLAN_SUMMARY_01.md`更新。必須: (1)根拠3階層(公式/英語圏実使用/合理的推定)+辞書+未確認のLedger区別と登録形式/(2)英語圏の実際の呼ばれ方を低コストで確認する方法(無料源優先: Wiktionary/Forvo等の存在確認、YouTube字幕・ニュース音声のASRは費用と信頼性を評価、LLM+Web検索は記事単位1回・Cap、高額/見込み薄なら合理的推定へ切替)/(3)合理的発音推定の判断方法(英語の綴り規則[letter-to-sound]・CMU類似語・複数候補時の自然さ/規則/文脈、推定を公式と偽らない)/(4)警告付きPASSの発動条件と誤PASS防止(「公式未確認」と「明確な誤発音」の区別、発音の確からしさとTTSの実現は別評価、音素差・脱落は従来NG、推定発音のLedger再利用の歯止め[階層・TTL・人間承認で昇格]、HRはAI側で判断不能な本質的問題のみ)/(5)同音判定Validatorへの供給方法(L1 canonical側、採用済み多語同音救済との接続点)/(6)複数候補・同綴り衝突(byUs型)・辞書外語の扱い/(7)Primary/Secondary合格条件(本日承認: KP英語フレーズは両方PASS、他はPrimary)との整合/(8)Trialケース(誤発音 vs 公式未確認の区別、byUsを通した具体例: 公式英語発音なし→英語圏実使用なし→合理的推定=bias/buy-us系の共通読み→TTSが共通読みなら警告付きPASS、`Bi-us`/`bee-us`等の音素差はNG)/(9)X/Z共通配線と将来Y/(10)費用(調査頻度×単価、キャッシュ効果、70円への影響。未確認単価は未確認と明記)。合格基準・Cap案・STOP条件。

### 3-E T-0・commit・報告
T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_03.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNPS-STAGE1-E1-委任_03-20261022` を含むAgent tool_useの0始まり通番、254前後)。`check_delegation_prompt.py`(見出し不一致FAILは既知の偽陽性)。commit(対象のみ)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_PNPS3.md`へ報告: Stage 1設計要約(配線点・不変保証・rollback・test/evidence計画・費用)/効果測定結果/M1整合/er097 test結果/Stage 2 v3要約(§5の10項目)/Opusレビュー論点3〜5個/SSOT・commit/RESULT_PACKET 4行/JPY0/raw URL。

## 4. 禁止
Production .py編集、合否判定基準・自動PASS条件の変更、有料API/Web取得、Trial実行、#133/#134/J7のStatus変更(注記のみ)、D-2/C-2担当ファイルの編集。