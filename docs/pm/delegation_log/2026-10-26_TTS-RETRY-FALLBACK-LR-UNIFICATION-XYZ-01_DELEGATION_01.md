## 管理ID

TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01(設計: ユーザー正式承認 APPROVED_FOR_PRODUCTION 2026-10-26「Family XYZ TTS Retry・Fallback・Local Rewrite統一」の実装設計・差分一覧・撤去一覧・test計画・runtime evidence計画と費用見積。API 0。実装はOpusレビュー[条件A]後の委任_02以降)。並行タスク衝突確認: 並行Agent 1件(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02=`er125_*`・`er105_kp_fulltext_selector_01.py`・`er119_kp_candidates_01.py`・`er003_v1_n3_01_scaffold_generate.py`・`data/kp_idiom_lexicon_01/`・KP evidence run dirを編集中)。あなたは本委任ではコードを一切編集しない(read-only+設計文書)。所有=`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/**`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_TRU1.md`。SSOT編集権なし。git index.lock競合時は10秒待って再実行(最大3回)。pathspec付きcommit。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様の実装設計(Production変更はしない)。到達上限Status=DESIGN_READY(Opusレビュー待ち)。
- **Opus独立技術レビューGate(11-3): 条件A該当**(X/Y/Z共通核のretry/fallback/LRフロー変更=新しい処理フロー)。あなたは`OPUS_REVIEW_REQUEST_01.md`(重要論点のみ)を作成し、Fableが依頼する。
- 禁止: コード・Prompt・SSOT・run dir編集、有料API、新Style・新Promptの開発(ユーザー原文§3「不要な新Style・新Promptの開発は行わない」)、LR対象の新規拡張(Z冒頭英語の是正のみ可)、Voice既定Styleの変更、モデル/Voice変更、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用/日次: JPY0(本委任)。当日既使用約552円+KP救済evidence≤40円進行中。**実装後のruntime evidence見積を本委任で算出**(7-7: 案件見積300円超なら事前費用承認が必要=Fableがユーザーへ提示。300円以下ならFable自律)。
- 修正範囲の線引き(11-8): 範囲内=承認表(ユーザー原文§2・§3)の実装、旧条件(600秒・旧回数・LR後1回・Adv技術エラー時のみStyle切替)の撤去、OPEN-376(LR再入)・OPEN-312(Style脱落)・U-06(Z topic_intro_en未分類)の是正、必要なtest・evidence。範囲外=LR対象の新設(日本語・KP英語・Zセリフ等)、新Style/新Prompt、Voice/モデル変更、Y Style profile(OPEN-537、別途ユーザー判断)。
- 時間見込み: 約3h(49行→新仕様の対応表60分/共通核の設計[er020/er003 n3_tts/er012_b/er122/Family runner]70分/撤去一覧・test計画・evidence計画・費用見積40分/Opus依頼文10分)。並列化: 本委任は設計のため直列。実装(委任_02)はFamily別test・evidence driverの並列化を計画に含める。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし。evidence計画に`TTS_EXECUTION_MODE=STANDARD`を明記)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_01.md` をN=668から順に試し、先頭が「## 管理ID」+「TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01」で始まるものを採用(`--index -1`不可)。ユーザー指示原文(下記全文)を`..._USER.md`へ逐語保存。

## ユーザー指示(原文)

# Claude Codeへの指示｜Family XYZ TTS Retry・Fallback・Local Rewrite統一・Production Wiring

## 1. 目的・Status・到達目標

Family X／Y／Z、Standard／AdvancedのTTS再試行・Fallback・Local Rewrite（以下LR）を、ユーザーが正式承認した共通仕様へ統一する。

**Status：APPROVED_FOR_PRODUCTION**
**到達目標：対象Family・音声部位すべてでPRODUCTION_WIRED**

最優先順位は、品質（Q）＞完成速度（D）＞量産単価（C）。

既存の49行の音声部位別星取表と関連する承認済み仕様を起点とし、共通処理の活用によって不要なFamily別分岐・重複実装を減らすこと。

## 2. 正式採用する基本フロー

原則として、品質NG時は次の順序とする。

1. 通常StyleでTTS① → NG
2. 同じStyleでTTS② → NG
3. **180秒（3分）待機**
4. Fallback Styleに切り替えてTTS③ → NG
5. LRありの場合：問題箇所を1回だけ書き換え、①〜④と同じ3回構成で再生成する
6. LR後もNGならHuman Review／STOP
7. LRなしの場合：最初のTTS③がNGならHuman Review／STOP

**重要条件**

- 1回目または2回目がPASSすれば、待機も後続の生成も実施しない。
- 180秒待機は、各3回構成において2回目NG後、3回目を実行する直前にのみ発生する。
- LRあり：最大6回の品質再生成、待機最大2回＝計360秒。
- LRなし：最大3回の品質再生成、待機最大1回＝180秒。
- LRは最大1回。LR後に再度LRへ入る再帰処理は禁止。
- LR後の原稿に対しても、元の品質Gate・ASR・音声QAを適用する。
- 技術的エラーに対する既存の即時再試行は、品質NGによる上記回数とは別枠で維持する。安全上限・STOP条件も維持する。
- 3分待機の目的は、連続したTTS生成を避けて間隔を空けること。品質基準の緩和は行わない。

今後、実績を観測して単純なRetryの効果が乏しいと確認できた場合は回数削減を検討するが、今回は変更しない。

## 3. 音声部位別の正式仕様

| 対象 | 3回目のFallback | LR | 最大TTS |
|---|---|---|---|
| XYZ Standard 英語本文・Comment等 | 既存の短文Style | あり | 6回 |
| XYZ Advanced 英語本文・Comment等 | **短文Styleを新たに適用** | あり | 6回 |
| Z Standard／Advanced セリフ（文脈・感情方式） | 承認済みの従来Dialogue Style | 現状なし | 3回 |
| XYZ Standard 日本語音声 | 既存の日本語短文Style | なし | 3回 |
| XYZ Standard／Advanced Key Phrase英語 | ENGLISH_LOCK | なし | **4回維持** |
| XYZ Advanced KP英語解説（音声が存在する経路） | 既存短文Styleの適合性を確認。不可なら同一Style | 現状なし | 3回 |
| Z Standard／Advanced 冒頭英語 | 短文Style | あり | 6回 |

**Key Phrase英語は正式承認済みの「通常2回＋ENGLISH_LOCK 2回」を維持する唯一の回数例外。**

この4回構成でもFallback移行前、すなわち通常2回NG後に180秒待機を適用する。後段のENGLISH_LOCKは既存どおり最大2回実行する。

### 部位・Familyの整合確認

既存49行を必ず再照合し、Preview、Comment、Full Story、chunk、In One Line、Topic Intro、Family Yの各Voice、Key Phrase、日本語等の適用漏れがないようにする。

特に以下を確認すること。

- **Family YのVoice音声**：英語本文と同一の共通処理が適用できるか確認し、承認済みの再試行仕様に整合させる。ただし、Voiceの既定Styleそのものを無断変更しない。
- **Family Zのセリフ**：文脈・感情Styleを2回、3分待機後に従来Dialogue Styleを1回。LRは今回追加しない。
- **Family Zの冒頭英語**：未分類によるFallback・LR未適用を解消し、共通仕様を適用する。
- **Advanced英語**：従来の「品質NGではStyleを変えず、技術エラー時のみ切替」を改め、3回目には短文Styleへ切り替える。
- **Advanced KP英語解説**：適用対象に実際のTTS音声が存在するか正式経路を確認する。存在する場合のみ本仕様を適用し、存在しない学習テキストを新たに音声化しない。

KP英語解説の短文Styleが適さない場合は、この部位のみ「同一Style2回→180秒待機→同一Style3回目→HR」とする。適合性確認はClaude/Fableが自律的に行い、不要な新Style・新Promptの開発は行わないこと。

## 4. LRの扱い・安全条件

LRの**有無は現行を基本とし、今回はLR対象の新規拡張を目的としない**。

ただし、Z冒頭英語のように、承認済み対象でありながら部位判定の不備で適用されていなかったものは、今回の統一対象として是正する。

- LRで書き換えるのはNGに関係する局所部分に限定。
- 既存の意味保持・書換え品質Gate・本文整合の安全条件を維持。
- LR後の再TTSは最大3回。再LRなし。
- 話者・Voice・速度・承認済みStyle・chunk構造を保持。
- 書換えによる音声と表示本文の関係、HR Lock、regeneration／resumeとの整合を確認。
- 既存のLR再入（OPEN-376）とStyle脱落（OPEN-312等）を、今回の共通化で解消する。
- ASR一致でも繰り返し・言い淀みQAでNGとなるケースを適切に扱い、LRが適用不可能な場合の無益な後続処理を避ける。ただし、品質NGの再試行フローや180秒待機を勝手に省略しない。

日本語・Key Phrase英語・Zセリフ等、今回LRなしとした部位へ独断でLRを追加しないこと。

## 5. QCD・実装上の方針

1. **品質**：承認済みのASR判定、自然な発話、繰り返し・言い淀み検査、Human Review Lock等を維持する。
2. **速度**：独立作業は並列化し、不要な待機・日付分割を行わない。仕様上必要な180秒待機のみ実施する。
3. **量産原価**：目標70円／記事セットを維持するため、再試行・LR・ASR増加による原価影響を計測する。失敗時のみ追加処理を実行し、PASS済み音声を無駄に再生成しない。
4. **実装の簡素化**：既存の共通関数を再利用し、Familyごとに別ロジックを増殖させない。
5. **既存仕様との整合**：旧10分待機、旧3回／4回の数え方、旧LR後1回、Advの技術エラー時のみのStyle切替など、今回置換された条件が正式経路やValidatorに残らないよう確認する。
6. **旧仕様の撤去**：新仕様と矛盾する不要なPrompt・分岐・検査・文書を整理し、Dangling Referenceを残さない。

モデルやVoiceそのものの変更は今回のScopeに含めない。

## 6. Production Wiring・受入条件

Family X／Y／Zの正式Production初回経路および以下を対象とする。

- Retry／Fallback／LR／Human Review
- regeneration／resume／既存音声の再利用
- Standard／Advanced
- chunk経路
- STOP・予算上限・技術エラー時の処理

**必須検証**

- TTS①でPASS → 追加生成・待機なし
- TTS②でPASS → 待機なし
- TTS①② NG → 180秒待機 → Fallback③
- LRなし → ③NG後にHuman Review
- LRあり → ③NG後にLRを1回 → 書換え後の3回構成 → 最終NGならHR
- LR再入なし、最大回数を超えない
- KP英語のみ4回構成と180秒待機の整合
- Std／AdvのStyle、Voice、速度保持
- LR後のQA・ASR・採用判定
- runtimeでのFallback Style切替と実際の待機時間の証拠
- Human Review Lock／キュー／Assemble BLOCK／STOP
- retry／regeneration／resumeでの重複生成・重複待機防止

既存テストを再利用し、必要十分なRegression・Validator・integration testを追加すること。

本番相当の正式runtime evidenceをFamily・レベル別に取得し、単なるDEVテスト成功で完了扱いにしない。

actual model_id、routing、Style／Prompt、試行回数、待機時間、LR実行回数、最終判定を検証可能にする。

Fable独立受入を実施し、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／必要なGit反映を完了する。

**全条件の確認後に限り、Family別にPRODUCTION_WIREDと判定する。**

## 7. 自律判断・STOP条件

承認済み仕様・品質・予算・Scope・Gate内の技術問題は、Claude/Fableが原因究明から修正・検証まで自律的に実施すること。

ユーザー判断を求めるのは、重要な品質・仕様変更、重大なQCDトレードオフ、予算・Scope超過、解決不能なblocker、新仕様の追加等に限る。

今回の共通化について、軽微な技術事項を逐一ユーザーへ転送しない。

既存案件別予算と、開発費原則1,000円／日（JST）を遵守する。必要な正式runtime検証の費用は、既存承認枠内で効率的に配分する。

安全上限・Human Review Lock・STOP条件は維持する。承認範囲外の新たなProduction仕様を発見した場合、無断で採用しないこと。

## 8. 最終報告

ユーザーが全体を把握できるよう、以下を簡潔に提示すること。

1. **統一後の星取表**：Family・Std/Adv・音声部位ごとに、①②③・Fallback・180秒待機・LR・HR・最大回数を表示
2. **変更前後の差分**：統一によって何が変わったか
3. **Family別のProduction Wiring Status**
4. **Fallback／LRの実走証拠とテスト結果**
5. **量産原価・制作時間への影響**
6. **Fable独立受入結果**
7. **残る未完了事項・判断待ち事項**

**目標は、例外の少ない共通仕様に整理し、品質を守りながら最速でProduction Wiringを完成させること。**

ユーザーが決定済みの仕様について、再承認を求めないこと。

(原文ここまで)

## Fableの設計指示

1. **SPEC_LEDGER_01.md**: ユーザー原文§2・§3・§4・§6を要件IDに分解(例: F-01 ①②同一Style、F-02 180秒待機位置、F-03 Fallback③、F-04 LR 1回+3回構成、F-05 最大6/3/4、F-06 LR再入禁止、F-07 LR後も同じGate、F-08 技術エラー別枠、S-01〜S-07 部位別表、L-01〜 LR安全条件、V-01〜V-12 必須検証)。各要件に「現行実装(棚卸し`REPORT_01.md`/`consolidated_01.json`のU-ID・P1〜P8・ファイル:行)」「新仕様」「差分の種類(回数/待機/Style/LR構成/分類是正/撤去)」を付ける。
2. **49行対応表(`ROW_MAPPING_01.md`+json)**: `consolidated_01.json`の49行それぞれに新仕様(①②③Style・待機・LR有無・最大回数・HR終端)と、実装上どの共通関数の変更で実現されるかを対応付ける。Yの各Voice・chunk・Topic Intro・In One Line・Preview・Comment・KP英語・KP解説・日本語・Zセリフ(ctx/legacy)・Z冒頭英語の漏れを機械的に確認(49行全部に新仕様の行があること)。**Adv KP英語解説**は正式経路でTTS音声が実在するか(X/Y/Zの正式runner・公開ページ・run dir成果物)を確認し、実在する部位のみ対象(存在しない学習テキストは音声化しない)。既存短文Style(minimal)の適合性を、X Std本文で使っているminimal instructionの文面とKP解説文の性質(複数文・説明調)から判断し、適さなければ「同一Style2回→180秒→同一Style3回目→HR」に確定(新Style/新Prompt不可)。
3. **共通核の設計(`DESIGN_01.md`)**: 現行の共通核(`COMMON_CORE_01.md` L1〜L8、`er020_tts_retry_local_rewrite_01.py` cooldown 600/LR、`er003_v1_n3_01_tts_generate.py`[voice01/news_tail_fix/crosslevel/n3_tts/repro01]、`er012_b_family_voices_production_01.py:483 generate_voice_body_wide_margin`+`attempt_hook`、`er122_fz_ctx_policy_01.py:282-338`[Z ctx cooldown別実装]、KP英語4回構成、日本語関数L7)に対し、**単一の「3回構成ブロック」抽象**(①②同一Style→180秒→③Fallback Style[部位別に注入: Std=minimal、Adv=minimal[新規適用]、Z dialogue ctx=legacy Dialogue Style、日本語=JA minimal、KP英語=ENGLISH_LOCK[後段2回]、KP解説=minimal or 同一])と**LRラッパ**(最大1回、LR後に同じ3回構成ブロックを1回だけ実行、再入禁止=深さカウンタ、LRが適用不可[NO_NG_SPAN等]なら即HR)を設計。Family別分岐を減らす方針で、どの関数を残し・統合し・撤去するかを表に。Z ctxの`attempt_hook`別実装cooldownを共通ブロックへ統合できるか(できない場合の理由)。cooldown定数600→180は1箇所定義(`COOLDOWN_SECONDS`)へ集約し、Z ctxの5秒刻みSTOP確認を共通化(U-12是正を兼ねる)。OPEN-312(LR再TTSのStyle脱落=news_tail脱落/Std minimal/voice01維持)を「LR後の3回構成は元の①②Style→③Fallback」に統一して解消。OPEN-376(再入)を深さカウンタで解消、HR queue登録契機(U-04)をLR後の最終NG時に一本化。U-03(非ASR起因NG): ③NG後にLR適用可否を判定し、不可なら即HR(待機・③は省略しない)。
4. **Y固有**: `er121_family_y_audio_01.py`はcs引数1本で共通核を呼ぶ(FAMILY_Y_01.md §5)。Voice既定Styleは不変。Y GateのLR成功/Std fallback BLOCK(U-16、OPEN-312派生)が新仕様と矛盾しないか(LR成功音声を人間承認なしでBLOCKし続けるのは「LR後もNGならHR」の新仕様と整合するか)を分析し、整合する最小変更を提案(承認済み仕様の範囲内で)。
5. **Z固有**: dialogue ctx=ctx①②→180秒→legacy③→HR/STOP(LRなし、cooldown 600→180)、`er122_fz_ctx_policy_01.py`の変更点。Z `topic_intro_en`の役割解決是正(`resolve_narrative_role`→TOPIC_INTRO)でcooldown・LR適用。Z narrator Std chunk経路(`er063`/`er117`)での3回構成+LR+減速後再検証の整合。
6. **撤去一覧(`REMOVAL_01.md`)**: 600秒定数・旧回数の数え方(総4/総3の文言)・LR後1回の分岐・Adv技術エラー時のみStyle切替・`stop_retrying`(cascade OFF専用)・`max_attempts=6`クランプ・旧記述(CURRENT_SPEC:2873/2954/2963、er121_audio:17、er019:1212-1213)・旧testで固定されている条件(600秒、LR後1回、Adv Style不変)の一覧(ファイル:行)。残す安全上限(ER-011 3回上限・累積15回・RESTART_STORM・RUN_LOCK・予算guard)を明記。
7. **test計画(`TEST_PLAN_01.md`)**: 既存test再利用(er020/er003/er012_b/er122/er019/er121/er063/er117/er026)+新規(①PASS無待機/②PASS無待機/①②NG→180秒→③Fallback Style/LRなし③NG→HR/LRあり→LR 1回→3回構成→HR/再入なし/最大回数/KP 4回+180秒/Std・Adv Style・Voice・速度保持/LR後QA・ASR/HR Lock・queue・Assemble BLOCK・STOP/resume重複生成・重複待機防止)。待機はtestでclock注入(実sleepしない)。
8. **evidence計画+費用見積(`EVIDENCE_PLAN_01.md`/`BUDGET_PLAN_01.md`)**: Family×レベル×シナリオ(V-01〜V-12)の正式runtime計画。強制NG注入はFZ evidence driver(`er122_fzcw_runtime_evidence_01.py`、NG方向のみ上書き)の方式を流用し、実TTS・実ASR・実180秒待機・実LR(LLM)を伴う。各Family/レベルで最低限: (a)①PASS、(b)①②NG→180秒→③PASS、(c)LRあり部位で③NG→LR→3回構成→最終判定(PASSとHRの両方を1回ずつ)、(d)LRなし部位で③NG→HR、(e)KP英語4回、(f)Zセリフctx②NG→180秒→legacy③、(g)resume重複なし。TTS単価(Trial実績2.34円/take、ASR・LR LLM費用)から**Family別・合計の見積**を出し、300円超なら分割案(Family別に日を分ける等)と、evidenceの重複排除(同一共通核を通る部位は代表部位で取り、残りはoffline testで固定する「代表+固定」方式)の案を提示。日次1,000円との関係(本日残約400円)を明記。
9. **Opus依頼文(`OPUS_REVIEW_REQUEST_01.md`)**: 重要論点のみ(3回構成ブロック抽象の正しさ/LRラッパの再入禁止と最大回数/Z ctx統合/U-03扱い/Y Gate BLOCKとの整合/撤去による副作用/KP 4回+180秒の位置/evidence計画の十分性)。
10. **時間見込み**: 実装(委任_02)・evidence(委任_03)の工程別見込みと並列化案。

## KPI provenance欄

該当なし(設計のみ。evidence計画にprovenance区分を明記)。

## Opus台帳更新

該当なし(台帳文案は不要。Fableがレビュー後に起票)。

## 事前指定Read一覧

- `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/REPORT_01.md` 全文、`consolidated_01.json` 全文、`COMMON_CORE_01.md` 全文、`FAMILY_X_01.md`/`FAMILY_Y_01.md`/`FAMILY_Z_01.md`: 各§4フロー・§5 LR有効化・§8不一致のみ
- `er020_tts_retry_local_rewrite_01.py`: Grep `COOLDOWN_SECONDS|def maybe_cooldown_before_attempt|def |NO_NG_SPAN|__wrapped__|enable_connected_speech_equivalence_layer` → 各±30
- `er003_v1_n3_01_tts_generate.py`: Grep `def generate|max_attempts|minimal|ENGLISH_LOCK|attempt_hook|prior_generations|style_prefix|fallback|cooldown` → 各±25(全文Read禁止)
- `er012_b_family_voices_production_01.py:470-560`
- `er122_fz_ctx_policy_01.py:270-345`、`er122_fz_ctx_notes_01.py`: Grep `cooldown|600|attempt` → ±10
- `er063_family_z_audio_01.py`: Grep `resolve_narrative_role|topic_intro_en|generate_a2_segment_with_slowdown|enable_connected_speech` → ±15
- `er121_family_y_audio_01.py:380-500,690-720`(cs呼出し・Y Gate BLOCK)
- `er019_family_x_audio_production_runner_01.py:1200-1220`、Grep `KP_EXPLANATION_MAX_ATTEMPTS|kp_explanation` → ±10(Adv KP解説の音声実在確認)
- `er121_family_y_runner_01.py`・`er026_family_z_fiction_production_runner_01.py`: Grep `kp_explanation|explanation` → ±10(同上)
- `er122_fzcw_runtime_evidence_01.py`: Grep `def |force|NG|ordinal` → 構造把握(evidence driver流用)
- `CURRENT_SPEC.md`: Grep `cooldown|10分|600|Local Rewrite|minimal|ENGLISH_LOCK|Fallback機構|1857|2873` → 該当行±8のみ(全文読込禁止)
- `OPEN_ITEMS.md`: Grep `OPEN-376|OPEN-312|OPEN-274|OPEN-528|OPEN-536|OPEN-537|OPEN-538|OPEN-525` → 該当行のみ
- `docs/pm/delegation_log/2026-09-26_*`(Glob)でcooldown 600秒・LR決定の原文: Grep `10分|600|cooldown|Local Rewrite` → ±3(撤去対象の承認履歴)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `600` `COOLDOWN` 全repo(`*.py`) → 600秒定数の定義・参照箇所一覧(撤去一覧へ)
- Grep `max_attempts=|MAX_ATTEMPTS` 全repo(`*.py`) → 回数定数一覧
- Grep `ENGLISH_LOCK` 全repo(`*.py`) → KP英語4回構成の実装箇所
- Grep `kp_explanation|explanation_en` in `er019_*.py`,`er121_*.py`,`er026_*.py`,`er063_*.py` と `user_test/**/index.html`(代表1件ずつ) → Adv KP解説音声の実在
- 成果物は`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/`に新規作成

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_01.md_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_TRU1.md`(9)にCURRENT_SPEC新節案(統一仕様の表)・OPEN新規(「TTS Retry統一 APPROVED_FOR_PRODUCTION・設計中」)・OPEN-376/312/528/536/538の統合先の文案(Fableが転記)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/`配下、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_{USER,DELEGATION_01}.md`(+check.json)。pathspec付きcommit。
- commit message: `TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01: Retry/Fallback/LR統一仕様の実装設計(49行対応表・共通3回構成ブロック・撤去一覧・test/evidence計画・費用見積、read-only)`
- trailer: `Delegation: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_TRU1.md`: (0)T-0、(1)要件ID一覧と現行→新仕様の差分表(変更前後の差分=ユーザー§8-2の素案)、(2)49行対応表の要約(漏れ0の確認、Adv KP解説の音声実在結果と確定仕様)、(3)共通核設計の要点(残す/統合/撤去する関数、Family別分岐の削減数)、(4)Y/Z固有の設計と整合分析(Y Gate BLOCK)、(5)撤去一覧、(6)test計画の件数、(7)evidence計画と費用見積(Family別・合計、300円超なら分割案と「代表+固定」案、日次との関係)、(8)Opus依頼文の論点、(9)SSOT文案、(10)判断候補(新仕様・トレードオフが必要と判明した場合のみ)、(11)必須4行+「判定整合: 重大NG=<なし|あり>」、(12)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。