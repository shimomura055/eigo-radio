# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_06(ユーザー決定2026-10-21: Fallback機構は現行仕様維持+記事A Std Full Story第2部のfallback takeを**個別承認**→正規の承認記録経路でM3 Gateを通し、Std/Advを**正式Production組立経路**で組立→最終試聴ページ(Std/Adv切替・通し再生・全スクリプト・KP)公開→SSOT反映。最終Status=`PRODUCTION_TECH_COMPLETE_USER_LISTENING_PENDING`[正式完成候補・ユーザー試聴待ち]。ユーザー試聴PASSを先取りしない)。
並行agent: `FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01 委任_01`(er088、run_byus_01読取、OPEN_ITEMS新規行・REPORT_LEDGER・ACTIVE_TASKを編集)。**共有プロトコル**(編集直前`git status --porcelain`+末尾再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち、他agent分は`git restore --staged`)。記事Bのrun dir・ページは触らない。

## 性質/到達上限Status/禁止事項
- 性質: Production完成(既存承認仕様の再利用)。到達上限=`PRODUCTION_TECH_COMPLETE_USER_LISTENING_PENDING`。
- 費用: 新規TTS/LLM生成**禁止**(見積JPY0〜数円: tts差分resumeはAPI 0見込み、assemble/player/ページはAPI 0)。日次累計はS0で実測。Guardrail: 記事A累計(現87.73)+本委任≤JPY100。想定外の課金(再生成発火等)が見えたら開始前にSTOP。
- 禁止: Gateの無効化・無条件PASS化・Gate/Validator/Style/組立コードの変更、第2部以外の再生成、state/wavの手編集、プレビュー連結(`er019_pp_std_preview_01.py`)での代用、新品質基準の追加、`git add -A`等。
- 承認記録の正規経路: `record_human_approval`(`er003_v1_n3_01_assemble.py:96-117`)のみ。`approved_by="user"`、理由にユーザー決定原文pathを記録。canonical_textは**`a2/audit/tts_generation_results.json`の`segments.full_story_part2.canonical_text`**(sha256 a8c9329aada814ba885c61205c4663b19b844645ef1742c55e9ba559d50d8742。E2E_PLAN_01.md §5-3のとおり。review_lock_stateのshaではない)。実行前にM3 `_approved`(`er019_family_x_style_profile_01.py:628-633`)が照合するshaと一致することをdry確認。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_委任_06.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_06」を含む最新index)。check結果1行。T-1: `TTS_EXECUTION_MODE=STANDARD`。T-2: TTS新規生成なし(resumeのみ)。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_06(Fallback維持決定・第2部個別承認・正式組立)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Claude Code／Fableへの指示
## Family X「給料が上がると、性格も変わる？」最終完成候補の組立・報告

### 1. ユーザー最新決定

従前のFallback廃止方針を撤回する。

**① Fallback機構は現行仕様を維持する。**

- Minimal Fallbackおよび既存のENGLISH_LOCK経路を廃止しない。
- FallbackのPrompt・Style・発動条件・再試行回数は変更しない。
- Family X／Zとも現行仕様を維持する。

**② 記事A Standard Full Story第2部のFallback音声を採用する。**

ユーザーは試聴の結果、今回のStyle差を許容すると明示判断した。

したがって、当該音声についてはStyle差を理由とする採用保留を解除する。

ただし、これは今回の音声に対する個別承認であり、今後すべてのFallback音声を無条件に自動採用してよいという共通仕様変更ではない。

**③ 記事全体のユーザー試聴PASSは未取得。**

Standard／Advancedとも、細部を含む最終品質評価はこれから行う。

### 2. 作業目的

記事A「給料が上がると、性格も変わる？」について、Standard／Advanced双方の**正式な完成候補版**を用意し、ユーザーが最終試聴・確認できる状態にする。

従来のStandardプレビューは効果音や音量正規化を省いた仮組立版だったため、最終確認には使用しない。

### 3. 実施内容

**A. Standard／Advancedの正式組立**

- 承認済みProduction仕様に基づいて、各レベルの全音声を組み立てる。
- 承認済みの効果音、無音間隔、音量正規化、音声の順序、速度調整等を適用する。
- Standard第2部には今回ユーザーが承認したFallback Takeを使用する。
- 他の既存PASS音声は原則として再利用し、不要な再生成を行わない。
- 既存の正式Production組立経路を使用し、DEV／プレビュー専用の簡易連結で代用しない。
- Fallback音声の個別承認を正式組立へ反映する際は、既存Gateの正規の承認記録・経路を利用する。Gateの無効化や無条件PASSへの改変は禁止。

**B. 品質確認**

Standard／Advancedそれぞれについて、以下を確認する。

- 全パートの欠落・重複・順序誤りがない
- スクリプトと採用音声が一致する
- 効果音・音量・無音間隔・速度調整が承認仕様どおり
- Key Phraseを含む既存の必須QAがPASS
- retry／fallback／regeneration／resume経路との整合
- 実際のProduction組立・runtime evidence・使用Style・モデルIDを確認

新しい品質基準を独断で追加しない。

**C. 最終試聴ページ**

Standard／Advancedの両方について、ユーザー向け最終試聴ページを用意する。

必須要件：

- 各レベルの全体通し再生
- 正式組立音声をそのまま再生できること
- Preview、Comment、Full Story、Key Phrase等を含む全スクリプト
- Key Phraseの英語・意味／解説
- 必要に応じたパート別再生
- Standard／Advancedの分かりやすい切替

ASR差分や内部Gateの詳細など、開発者向け情報を画面の中心に置かない。

**ユーザーが記事の完成品質を確認するためのページ**とする。

### 4. Fable独立受入評価

Fableは、単にページが公開されたことではなく、正式Production経路で組み立てられた完成候補であることを確認する。

特に以下を照合する。

- Standard第2部の承認済みFallback Takeが正しく使用されている
- 他のパートが意図せず再生成・変更されていない
- 正式仕様の効果音・音量処理が適用されている
- Standard／Advanced双方のQA・組立が合格している
- 試聴ページと最終出力音声が一致している

不具合が見つかった場合は既存承認範囲・予算内で修正、再検証する。

### 5. QCD・STOP条件

品質を最優先としつつ、既存成果物を最大限再利用して完成までの時間・追加原価を抑える。

- 不要なTTS・LLM再生成や追加Trialは禁止
- 独立作業は並列化
- 開発費は既存承認枠および原則1,000円／日（JST）を遵守
- 未承認の仕様変更・品質基準変更は行わない
- 真のblockerや重大な品質問題は報告する

### 6. 最終報告

以下の順に簡潔に報告する。

1. **Standard／Advancedの最終試聴URL**
2. 正式組立・品質検査の結果（各レベル）
3. Standard第2部Fallback音声の採用反映証拠
4. 未解決の品質問題の有無
5. 今回の追加費用と記事A累計原価
6. Fable独立受入評価
7. ユーザーが最終試聴で判断すべき事項

CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS等には、今回のFallback維持決定、記事Aでの個別採用承認、ユーザー最終試聴待ちの状態を正確に反映し、必要なGit反映を行う。

**最終Statusは「正式完成候補・ユーザー試聴待ち」。ユーザー試聴PASSを先取りしない。**

記事Aの最終試聴ページが準備できた時点で報告すること。新しい記事制作や追加Trialへ無断で移行しない。
--- 原文ここまで ---

## 手順(E2E_PLAN_01.md §5-3の手順書+MEY E2E-02 委任_04[`docs/pm/delegation_log/2026-10-21_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_委任_04.md`、E2E_PLAN_02.md §10]に準拠)
S0. daily cost・`git status`件数・T-0・原文保存。`stop_scope_check_01.py`実行(rc)。承認前のstate snapshot: `a2/audit/tts_generation_results.json`の全segment(status/wav sha256)と`b1b`同を`docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/pre_approval_snapshot_01.json`に保存(後で「他パート未変更」の証明に使う)。
S1. 承認記録: `record_human_approval(a2 out_dir, "full_story_part2", canonical_text, approved_by="user", reason="FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md §1②(個別承認、共通仕様変更ではない)")`相当(関数シグネチャに合わせる)。`a2/audit/human_approved_segments.json`の内容とsha一致を記録。
S2. `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug paycheck_personality --run run_pp_01 --level a2 --stage tts --budget-jpy 70`(差分resume、API 0見込み。raw_usage_log行数の前後比較で呼出0を証明。呼出が発生しそうなら直前にSTOP)。
S3. `--stage assemble --level both`→`--stage player`。Audio Validation Gate/M3 style_profile_gate(Std: part2=人間承認によりPASS、他=承認Style)/key_phrase_source_gate/AUW結果、尺(秒)、peak/clipping、SFX・無音・RMS正規化が正式経路で適用されたことをrun_summary/assemble auditから記録。Adv(b1b)は既存完成版の再組立(内容が変わらないことをsha/尺で確認、変わる場合は理由)。
S4. 他パート未変更の証明: S0 snapshotと組立後のtts_generation_resultsを比較(全segmentのwav sha256同一、part2のみ承認フラグ付き)。
S5. 最終試聴ページ: `er019_pp_page_01.py`(委任_01で作成済み、MEY版複製)で`user_test/paycheck_personality_e2e_01/index.html`を生成。要件: Std/Advの切替(タブ or 2セクション)、各レベルの正式組立音声の通し再生、全スクリプト(Preview/Comment/Full Story/Key Phrase/In One Line)、KP英語+意味/解説、必要に応じたパート別再生(既存機構にあれば)。ASR差分・Gate詳細は載せない。既存の`std_preview/`・`hr_full_story_part2/`は残すが、index.htmlから「正式完成候補はこちら」と分かるよう、両サブページの冒頭に「このページは確認用。正式完成候補は ../index.html」の1行を追記。
S6. commit/push→Pages反映(最大10分)→`er019_pp_play_verify_01.py`で再生evidence(`docs/research/.../pages_play_evidence_01.json`、Std/Adv通し+パート別)。URL=`https://shimomura055.github.io/eigo-radio/user_test/paycheck_personality_e2e_01/index.html`。
S7. 費用(本委任実測・記事A累計=87.73+今回、15節5区分・1生成セット総原価)、所要時間、runtime evidence一覧をE2E_PLAN_01.md §6〜§8へ。
S8. SSOT(共有プロトコル): (a)`OPEN_ITEMS.md` OPEN-432行頭Statusを`PRODUCTION_TECH_COMPLETE_USER_LISTENING_PENDING(正式完成候補・ユーザー試聴待ち。Std第2部=fallback take個別承認[ユーザー2026-10-21]、Fallback機構=現行維持)`へ更新(旧Status保持)。(b)`docs/pm/USER_DECISION_REGISTER_01.md` #132を「判断済み 2026-10-21((ア)個別承認。Fallback機構は現行仕様維持[Minimal/ENGLISH_LOCK廃止せず、Prompt・Style・発動条件・回数不変、X/Z共通]。共通仕様変更ではない。原文path+sha256)」へ(既存行は書き換えず追記節に判断済み行を追加)。#5にも「2026-10-21ユーザー決定: Fallback機構現行維持(#132参照)。fallback takeの処置は個別承認(今回)、共通ルール化はしない」注記。(c)`DECISION_LOG.md`末尾に1件(①Fallback機構現行維持[従前の廃止方針撤回]②記事A Std第2部fallback take個別承認(Style差許容、共通仕様変更ではない)③記事全体の試聴PASSは未取得、正式組立結果、原文path+sha)。(d)`CURRENT_SPEC.md:2756`の既存注記の直後に「【2026-10-21ユーザー決定】Fallback機構(Minimal/ENGLISH_LOCK、Prompt・Style・発動条件・回数)は現行仕様維持、Family X/Z共通。fallback takeの採用はM3 Gateの正規承認記録(`record_human_approval`)による個別判断(記事A Std第2部=個別承認、REGISTER #132)。共通の自動採用ルールは設けない」を追記(本文無変更)。(e)REPORT_LEDGER 1行、ACTIVE_TASK先頭追記。
S9. secret scan→明示add→commit(`FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_06: Std第2部fallback take個別承認(正規経路)→正式組立Std/Adv→最終試聴ページ公開+SSOT(Fallback現行維持決定・#132判断済み)`)→`git push origin HEAD:main`→到達確認。

## 報告(docs/pm/RESULT_PACKET_FXPP6.md 上書き。ユーザー§6の1〜7の順。6はFable用の材料[Sonnetは判定しない])
1.URL(Std/Adv) 2.正式組立・QA結果(各level: Gate結果、尺、peak、SFX/正規化/無音/減速の適用証拠path) 3.第2部採用反映証拠(human_approved_segments.json内容、M3 gate jsonのpart2判定、assembled wav内でpart2のsha/相関) 4.未解決品質問題(PASS_WITH_WARNING等の事後試聴リスト含む) 5.費用(本委任実測+記事A累計)と当日累計 6.Fable評価用材料(他パート未変更の証明、スクリプト一致、ページ=最終出力一致のsha) 7.ユーザー試聴の確認ポイント候補(第2部の調子、PASS_WITH_WARNING箇所、KP "jump to that conclusion")+commit hash・raw URL+4行判定。