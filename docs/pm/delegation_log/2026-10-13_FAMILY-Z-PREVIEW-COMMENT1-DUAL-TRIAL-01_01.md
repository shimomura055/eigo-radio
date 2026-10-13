# 委任_01 FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01(保存: 要点保存。ユーザー指示のみ逐語)

## 管理ID
FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01 委任_01(初回。Trialのみ、Production採用・変更は未承認)。並行: FAMILY-Z-KP-STRATEGY-L-DECISION-CLOSEOUT-01(SSOT編集中の可能性)、ASR M1/F1 Opusレビュー(read-only)。出力領域=`er076_output/family_z_preview_comment1_dual_trial_01/`、`er076_family_z_preview_comment1_dual_trial_01.py`、`docs/pm/ACTIVE_TASK_FZPD.md`/`RESULT_PACKET_FZPD.md`(commitしない)。SSOT編集は作業最後にまとめ、直前に`git status --porcelain`で他agent未commit変更を確認(60秒x5待ち)。`.git/index.lock`待ち30秒x3、commit前fetch→ff-only。全commitに`Managed-ID: FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01` trailer。

## 性質/到達上限Status/禁止事項
性質=Trial(A/B x3 Take x2要素=12生成)+read-only Production影響調査。到達上限=VALIDATED/REJECTED/USER_DECISION_REQUIRED(APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDは付与しない)。費用上限JPY20(ハードストップ22)、gpt-6-luna $0.10/$0.50 per 1M、USD/JPY160。禁止=Production code/Prompt/Validator/Gate/DB変更、Family Z記事再生成・音声化(TTSゼロ)、Family X・Z Advanced変更、追加Prompt探索・追加Round・修正Trial、生成後の恣意的修正・選別、`git add -A`/`-f`、amend/rebase/force push、stash/clean/reset --hard/checkout -f、.env source/秘密値出力、wav/telemetry/log add、ACTIVE_TASK/RESULT_PACKET commit、共有ファイル追記test実行、外部プロセス再起動、監督ループ/timeoutラッパ、`er026_output/family_z_production_e2e_01/`配下書込み。STOP条件=新たな仕様判断/追加Trial必要と判明→報告。開始時にSTOP_NOTICE/STOP/STOP_ALL確認。Opus Gate非該当。最新モデル原則=Production同一gpt-6-luna(例外理由=現行Production出力との比較可能性)。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2(TTSなし)/T-3(LLM12回、上限JPY20)。

## Fable補足(設計固定事項)の要点
- 事前指定Read: run_e2e_02の`writer/std.md`・`support/a2_support.json`(現行Std)・`support/b1b_support.json`(現行Adv)、`er062 run_support_std` L844-890、`run_support_adv` L893-928、`er013.generate_family_c_a2_comment`、`b1s.COMMENT_1_ROLE`、er074条件E+`takes_table_01.md`、er070統一Prompt。
- 共通: gpt-6-luna、effort high、developer message=`日本語のListening Support原稿を作成してください。`、`a2gen.run_support_text`経由。lint=`lint_support_text(text,"ja","melos")`を記録(NGでも再生成しない)。
- Trial A: A1=er074条件E逐語(3 take)。A2=Production Std Comment1経路にart末尾へ「【直前に流れるPreview…】+【Previewとの役割分担】…」ブロックを追加するだけ(role・content_facts不変)。同TakeのPreviewを参照。
- Trial B: B1=Production Std Comment1経路、content_factsのみ固定文へ差替(Advanced版Comment 1と同じ性格・1〜2文の短い聴取ガイド等)。role矛盾は報告し固定文で実施。B2=er070統一Prompt+er074条件A組立、Comment 1のみ同TakeのB1生成物。完成セットはPreview→Comment 1の順。
- 成果物: plan_01.md、prompt_*_full_01.txt、takes_01.json、SETS_01.md(ユーザー指示§6の形式)、PRODUCTION_IMPACT_01.md、cost_01.json、state_guard_01.json。評価は事実ベース(4-gram補助は判定ではない)。分類案はA/B別に。
- Regression: `er062*_test*.py`、`er026_family_z_fiction*_test*.py`(stop_sentinel除外)。state_guard changed=[]。
- SSOT追記(最後): OPEN-338追記、DECISION_LOG末尾、CURRENT_SPEC 1行、UDR新規行(#51想定)+集計+REPORT_LEDGER行。
- Git: 明示addのみ、commit2回(Trial成果物/SSOT)、secret_scan、push。
- 報告: `docs/pm/RESULT_PACKET_FZPD.md`に(0)〜(11)(6セット全文を省略せず含める)。

## ユーザー指示(原文)
(2026-10-13、管理ID FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01、全文)

# Claude Codeへの指示(確定版)

**管理ID: FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01**

## 1. 目的

Family Z Standardにおいて、次の2方式を独立してTrialし、PreviewとComment 1の最適な役割分担を比較する。

- **Trial A: Preview先行・Comment 1補足方式**
- **Trial B: Advanced準拠のComment 1先行・Preview生成方式**

最終的な比較対象は、**PreviewとComment 1を連続して読んだときの品質**とする。

今回はTrialのみ。Production採用・変更は未承認。

現在Status: `USER_DECISION_REQUIRED`

今回到達可能なStatus: `VALIDATED` / `REJECTED` / `USER_DECISION_REQUIRED`

## 2. Trial A: Preview → Comment 1

### Step A1: Previewを先に生成

既存のE方式を基本とする。

- Comment 1・2は参照しない。
- 物語の具体的な状況や対立から入り、興味を引く。
- 抽象的なテーマ紹介・評論調を避ける。
- あらすじの羅列やネタバレを避ける。
- 原稿にない事実を追加しない。

### Step A2: Comment 1を生成

生成済みPreviewを参照する。

- Previewにない背景・理由・条件などを補足する。
- Previewと同じ事実を説明し直さない。
- 英語本文の理解に必要な情報を提供する。
- 単なる言い換えや説明不足にならない。
- Comment 1から英語本文へ自然につなぐ。

**狙い: Previewで興味を引き、Comment 1で理解を深める。**

## 3. Trial B: Comment 1 → Preview

### Step B1: AdvancedのセンスでComment 1を先に生成

まず既存のFamily Z Advanced Comment 1の正式Prompt・役割・既存出力を確認し、その特徴をStandardへ適用する。

Advanced既存例:

> Listen for what Melos promises before he leaves.

重要なのは、英語を日本語へ直訳することではなく、**AdvancedのComment 1が持つ構成・情報量・語り口をStandardでも再現すること**。

- 簡潔で自然な聴取ガイドにする。
- 物語の前提を長々と説明しない。
- 聞く際の具体的な注目点を示す。
- 先の展開を説明しすぎない。
- Standardの学習者にも分かりやすい日本語にする。
- 抽象的な教訓・評論調にしない。
- 必要な理解支援を失わない。

### Step B2: Comment 1を参照してPreviewを生成

- **Trial Bで新たに生成したComment 1を使用する。**
- Trial AのPreviewは使用しない。
- Family X準拠のStandard Preview Promptを基本とする。
- 先行するComment 1との内容重複を避ける。
- 具体的な出来事・状況・対立から興味を引く。
- 抽象的なテーマ紹介・評論調や、あらすじの羅列を避ける。
- 結末・重要な転換点を先出ししない。

**狙い: Advanced同様、短いComment 1を先に設計することで、Previewに具体的な導入を書く余地を確保する。**

なお、**生成順序と聴取順序は別**である。Trial Bも完成したセットは必ず「Preview → Comment 1」の順に提示する。

## 4. Trial設計

対象: 既存の『走れメロス』Standard原稿。

同一の原稿、同一モデル・設定を用いる。

| | Trial A | Trial B |
|---|---|---|
| 先に生成 | Preview | Comment 1 |
| 後に生成 | Comment 1 | Preview |
| 独立Take数 | 3 | 3 |
| 生成回数 | 6 | 6 |

**合計12生成(2方式×3 Take×2要素)。**

各Takeは独立生成し、生成後の恣意的な修正・選別をしない。

AとBは並列実施してよい。ただし、各方式内の依存順序は必ず守る。

既存のE方式・現行Standard・現行Advancedの成果物は比較用に再利用し、不要な再生成をしない。

## 5. 評価基準

### ① Previewの品質
- 具体的で興味を引くか
- 物語の問題や対立が分かるか
- 自然で聞きやすいか
- あらすじ化・評論調・ネタバレがないか

### ② Comment 1の品質
- 物語理解や英語聴取に役立つか
- 不必要な前提説明がないか
- 簡潔で自然か
- Previewにない価値を提供しているか

### ③ セットの品質【最重要】
- PreviewとComment 1に実質的な重複がないか
- 単なる言い換えになっていないか
- 情報が自然に積み重なるか
- Previewで興味を持ち、Comment 1で聞く準備が整うか
- Comment 1から本文へ自然につながるか
- Standardの学習者にとって説明不足にならないか

### ④ 正確性・安定性
- 原稿にない事実の追加
- 人物・関係・時系列・条件の誤り
- 既存の文数・長さ・禁止表現・その他品質Gateへの適合
- 3 Take間の品質ばらつき

A/Bの優劣は、短さや表面的な重複率だけでは決めない。

**意味上の重複、導入の面白さ、理解支援の3点を重視する。**

## 6. 報告形式【必須】

以下の構成で、**6セットすべての全文を省略せず提示**すること。

### Trial A
**Take 1**
Preview:(全文)
Comment 1:(全文)
評価:
- Previewの魅力
- Comment 1の追加価値
- 重複の具体箇所
- 問題点
Take 2、Take 3も同様。

### Trial B
(Trial Aと同一構成。Take 1〜3)

その後、A/Bを以下の観点で比較する。
1. Previewの具体性・面白さ
2. Comment 1の自然さ・聴取ガイドとしての価値
3. PreviewとComment 1の重複
4. Standard学習者への適合性
5. 既存方式との比較
6. 安定性・事実正確性

**ユーザーが6セットを読んで判断できる報告を最優先すること。**

## 7. 費用・QCD
- API費用上限: **¥20**
- 既存原稿・成果物を再利用
- 不要な記事再生成・音声生成は禁止
- A/B間は可能な範囲で並列化
- 追加Prompt探索・追加Roundは禁止
- 事実誤りや構造問題が出ても、独自に修正Trialを繰り返さず報告する

## 8. Productionへの影響調査

Trialとは別にread-onlyで以下を確認する。
- 現行のPreview・Comment 1生成順序
- Advanced / StandardのComment 1 Prompt・役割差分
- A方式のPreview先行依存
- B方式のComment 1先行依存
- retry / fallback / prior再利用 / regeneration
- Family Xの共通処理への影響
- 旧Phase 1経路のDangling Reference
- 必要なValidator・Regressionの変更点

Production実装が必要となる場合の技術リスク・QCDを整理する。

ただし、**Productionコード・Prompt・Validator・Gateを変更しない。**

## 9. STOP条件・PM Gate
- Family Zの記事再生成・音声化STOPを維持する。
- Family X・Family Z Advancedは変更しない。
- 新たな仕様判断が必要ならSTOP。
- 追加Trial・仕様開発を独自に進めない。
- Trial結果は`VALIDATED` / `REJECTED` / `USER_DECISION_REQUIRED`で分類する。
- `VALIDATED`でもProduction採用へは進めない。
- CURRENT_SPEC / DECISION_LOG / OPEN_ITEMSにはTrial結果と未決事項を区別して記録する。
- 必要なTrial成果物・Git反映を報告する。
- Dangling Referenceを確認する。
- Closeout時には未処理のUSER_DECISION_REQUIREDとAPPROVED_FOR_PRODUCTION未配線項目を明示する。

**今回の到達点は、A/B各3セットの実物比較とユーザーへの判断材料の提示まで。Production採用判断はユーザーが行う。**

(ユーザー指示 原文ここまで)

## 事前指定Grep一覧+追記位置・更新位置の手順
(要点) Grep: `generate_family_c_a2_comment`、`COMMENT_1_ROLE`、`build_family_z_preview_prompt`。追記位置: OPEN_ITEMS.md OPEN-338行末、DECISION_LOG.md末尾、CURRENT_SPEC.md Family Z Std Preview仕様行(1行のみ)、USER_DECISION_REGISTER_01.md新規行(最大番号+1)と集計、REPORT_LEDGER.md末尾行。

## 実行コマンド全文
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-13_FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01_01.md --json-out docs\pm\delegation_log\2026-10-13_FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01_01_check.json
.venv\Scripts\python.exe er076_family_z_preview_comment1_dual_trial_01.py --plan-only --out er076_output\family_z_preview_comment1_dual_trial_01
.venv\Scripts\python.exe er076_family_z_preview_comment1_dual_trial_01.py --run --takes 3 --budget-jpy 20 --out er076_output\family_z_preview_comment1_dual_trial_01
.venv\Scripts\python.exe run_project_regression.py --pattern "er062*_test*.py"
.venv\Scripts\python.exe run_project_regression.py --pattern "er026_family_z_fiction*_test*.py"
.venv\Scripts\python.exe tools\secret_scan_01.py --staged

## SSOT追記文
(要点) OPEN-338追記(Trial結果と未決を区別)、DECISION_LOG末尾に本IDエントリ、CURRENT_SPECにTrial記録1行(仕様不変)、UDR新規行、REPORT_LEDGER行。TTSなし。
