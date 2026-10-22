FABLE-DELEGATION-MARKER: KPMG-TRIAL-RUN-委任_01-20261022

# 委任(FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_01: Trial①=最小化Promptで5モデル×14本文の選定比較、Trial②=Luna選定結果への一般化工程分離Before/After。前回Trial(KP6M)の本文・検証・評価・Excel処理を再利用。ユーザー承認済みTrial。Production採用未承認・Production無変更)

## 管理ID
FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_01(新規。前回=FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01[OPEN-445、VALIDATED、推奨Luna維持・ユーザー判断#145は未回答]。並行: 別agentが`PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_07`(Stage 2 Trial、`er100_*`、`user_test/pnps_stage2_hr7_listen_01/`)を実行中で`OPEN_ITEMS.md`(OPEN-441行)・`docs/pm/REPORT_LEDGER.md`末尾・`docs/pm/USER_DECISION_REGISTER_01.md`(#142行)を編集する。共有ファイル編集前に`git status`→該当行再Grep→自分の行だけ→即add+commit。`index.lock`は30秒待って再試行。新規OPEN番号は編集直前にGrepで最新+1)。

## 性質/到達上限Status/禁止事項
- 性質: 比較Trial(Trial専用実装)。到達Status: 本委任は`TRIAL_DONE_PENDING_FABLE`まで(最終分類`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`はFable)。Opus Gate: 非該当(Trial専用。Production変更なし)。
- 修正範囲(11-8): Production側(`er030_*`、Prompt template、`er006_model_routing_contract_01.py`、Validator、KP Store)の編集は範囲外。範囲内=Trial専用script `er101_kp_prompt_min_gen_trial_02_*.py`(前回`er098_kp_six_model_trial_01_*.py`からのimport/コピー流用可。er098側は無改変)、`docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/`、`er101_output/kp_prompt_min_gen_trial_02/`。
- 時間見込み(8-X): 全体約3〜4時間。流用セットアップ30分 / Trial①選定70回(5モデル並列)15分 / 機械検証15分 / Trial②一般化(Luna確定記事から順次開始)20分 / 独立評価(①と②、並列)45分 / Excel+RESULT 60分 / SSOT・commit 20分。直列理由: 有料呼出は見積確認後、Trial②はLuna出力依存(記事単位で先行可)。
- 費用/日次: 当日(JST 2026-10-22)既使用 約JPY482(出典: RESULT_PACKET_B3RD8 275.35+KP6M1 206.60)+Stage 2 Trial進行中(Guardrail 150、未確定)。本委任見積(前回実測ベース): 選定≈53円(前回71.7からSol 18.7を除く)+一般化≈5円+独立評価≈135〜170円(前回134.9+Trial②分)=**約200〜230円**。Guardrail(T-3) **Cap JPY300**: 到達だけで自動STOPしないが、**実トークンでの事前見積が300円を超える見込みなら有料呼出前に報告**(7-7)。実行中に累計Cap超過見込みなら有料呼出停止・途中保存・報告。承認区分: C(承認済みTrial・300円以下前提)。評価費を抑える工夫(評価rubric・評価者・粒度は前回と同一に保つ。同一性を崩す節約はしない)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。commit前`.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore(force-add禁止)。SSOT全文読込禁止。他agentの未commit差分を混ぜない。STOPセンチネル確認後に開始。記事・本文の再生成禁止。品質理由の再生成禁止(1モデル1本文1回、技術的失敗のみ同一入力で最大2回再試行し記録)。不合格結果の修正掲載禁止。既存Production KPの再生成禁止。指定モデルが呼べない場合は無断置換せずSTOP報告。Trial②で一般化LLMにKey Phraseを再選定させない。

## ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_USER.md`へ本文無改変で保存、文字数・sha256を記録)
---
# Claude Code指示：Key Phrase選定Prompt改善＋一般化分離Trial

## 1. 目的・承認範囲

Family XのKey Phrase選定品質を改善するため、以下2つのTrialを実施する。

**Trial ①：選定Prompt改善・5モデル比較**

学習ポイントが明確で、不要な語を含まない最小限のKey Phraseを選定できるか検証する。

**Trial ②：一般化工程の分離**

Trial ①のGPT-6 Luna選定結果に対して、別LLMで一般化を実施し、Before／Afterの品質を比較する。

共通条件：

- 既存Productionのモデル・Prompt・コード・選定方式は変更しない。
- Trial成果をProductionへ自動採用しない。
- 到達可能Status：`VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED`
- 前回Trialの成果物・評価方法を最大限再利用する。
- 品質（Q）＞速度（D）＞量産単価（C）の原則を遵守する。

## 2. 対象記事

前回6モデル比較Trialと同一の7記事、Standard／Advancedの14本文を使用する。

1. コーヒー価格の高騰
2. 給料が上がると、性格も変わる？
3. 漫画のキャラクターとAIで会話（byUs）
4. 退屈と攻撃性の関係
5. Meta関連の記事
6. 中東情勢（イエメン・サウジアラビア）
7. ホルムズ海峡関連（旧記事）

前回Trialで使用した本文をそのまま再利用し、記事・本文の再生成は行わない。

比較に使用した本文のバージョン・ハッシュが前回と一致することを確認する。

## 3. Trial ①：選定Prompt改善

### 3-1. 比較モデル

前回6モデルからGPT-6.1 Solを除外し、以下5モデルを使用する。

| No. | モデル | API model ID |
|---|---|---|
| 1 | GPT-6 Luna | `gpt-6-luna` |
| 2 | Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite` |
| 3 | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` |
| 4 | Claude Haiku 5.5 | `claude-haiku-5-5` |
| 5 | Claude Sonnet 5.5 | `claude-sonnet-5-5` |

**5モデル×14本文＝70回の選定。**

指定したモデルを実際に使用したことをAPI返却model IDで確認する。

モデル別のPrompt最適化や、品質不良を理由とする再生成は行わない。

### 3-2. 選定Prompt（固定）

以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを5つ選んでください。

**以下の順序で処理し、上位条件を優先してください。**

1. **本文一致（絶対条件）**：本文中の連続した語句だけを抜き出す。変更・言い換え・追加・創作は禁止。
2. **5語以内（絶対条件）**：スペース区切りで正確に数える。6語以上は出力禁止。
3. **学習ポイントの明確化と最小化（必須）**：学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。不要な目的語・修飾語・文脈は除く。5語は上限であり、目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。
4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。
5. **易しい表現の除外**：基本語だけで構成され、字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。
6. **5件選定**：条件を満たす候補から5件選ぶ。適切な候補が不足する場合のみ5件未満とし、数合わせはしない。

**出力直前に各候補を本文と照合し、改変がないこと、5語以内であることを再確認してください。語数も併記してください。**

---

上記Promptの選定条件は変更禁止。

前回同様、記事本文の区切りやAPI入力形式への軽微な調整のみ許可する。調整した場合は変更前後・理由を事後報告すること。

### 3-3. 品質評価

前回Trialと同じ評価基準・評価者を可能な限り維持し、比較可能性を確保する。

特に以下を追加・重視する。

- 学習ポイントが明確か
- 不要な目的語・修飾語が残っていないか
- 学習価値を保った最短形になっているか
- 短縮によって不自然・不完全なフレーズになっていないか
- 5語以内・本文一致を守っているか
- 上級者向けの学習価値があるか

前回の品質スコアと比較する際は、評価方法を変更した部分を明示し、同一尺度でない数値をそのまま優劣比較しない。

特に以下のような改善が確認できるか検証する。

| 前回の長すぎる表現 | 期待する改善方向 |
|---|---|
| think up what happens next | think up |
| formal agreements with their creators | formal agreements |
| alone caused the different results | caused different results |

※Trial ①では本文一致が絶対条件なので、原形化はしない。`agreements → agreement`、`caused → cause`はTrial ②の対象とする。

## 4. Trial ②：一般化工程の分離

### 4-1. 対象

**Trial ①で得られたLunaの選定結果のみ**を対象とする。

14本文のLuna出力をそのままBeforeとして使用し、選定をやり直さない。

一般化担当は低コストLLMを1モデル選定する。

モデルID・選定理由・料金を記録し、品質不足が確認された場合のみ他モデルの比較を検討する。

### 4-2. 一般化専用Prompt

以下を初期Promptとする。

「以下のKey Phraseを、英語学習者が他の場面でも使える汎用的な形に整えてください。

固有名詞や特定の人物・物事への依存を取り除き、必要に応じて原形化、単複変換、someone/something等への置換を行ってください。

元の学習ポイント・意味・文法・自然さを維持し、不要な語句は追加しないでください。一般化が不要な表現は変更しないでください。

各表現は5語以内とし、変更前・変更後・変更理由を示してください。」

一般化LLMに別のKey Phraseを再選定させないこと。

一般化後も元の選定表現との対応を追跡できるようにする。

### 4-3. Before／After評価

各Key Phraseについて次を比較する。

| 項目 | 内容 |
|---|---|
| Before | Lunaが選定した表現 |
| After | 一般化LLMによる表現 |
| 変更内容 | 原形化・単複変換・対象の置換など |
| 一般化の適切さ | PASS／NG |
| 学習ポイント維持 | PASS／NG |
| 英語の自然さ | PASS／NG |
| 5語以内 | PASS／NG |

一般化の適用漏れ、不必要な変更、意味の変化、文法上の不自然さを検出する。

**単に変更件数が多いことを高評価にしない。**

変更すべき表現を適切に変更し、変更不要なものを維持できることを評価する。

## 5. 成果物：Excel比較ファイル

前回のExcel形式を踏襲し、ダウンロードしてすぐ比較できる状態にする。

**Sheet 1：Trial ① モデル比較**

記事別・Standard／Advanced別に5モデルのKey Phraseを横並び表示。前回Trialの選定結果も比較可能にする。

**Sheet 2：Trial ① 品質評価**

各モデルの指示遵守率、最小化品質、学習価値、選定件数、費用。

**Sheet 3：Trial ② 一般化Before／After**

Lunaの選定結果と一般化後の結果を横並び表示し、変更内容と評価を掲載。

**Sheet 4：検証詳細**

本文根拠、語数、違反内容、一般化の妥当性、評価結果。

**Sheet 5：費用・実行条件**

モデルID、Prompt、使用トークン、実費、記事セット単価、実行条件。

シート構成は見やすさを優先して調整してよい。

## 6. 費用・実行効率

Trial ①と②を一連の検証として実施する。

- 前回の記事本文・評価プログラム・Excel生成処理を再利用する。
- 5モデルの選定は独立して並列実行する。
- Lunaの出力が確定した記事からTrial ②を開始してよい。
- 不要な再生成・重複評価を行わない。
- 選定費用と一般化費用、独立評価費用を分けて記録する。
- 追加費用を含む1記事セット当たりの量産原価を算出する。

開発費は既存の日次上限1,000円（JST）と本Trialの承認済み枠を遵守する。新たな個別Trial費用枠が未設定の場合は、前回と同程度の規模を目安に事前見積を行い、超過の見込みがある場合のみ承認境界を確認する。

品質を守りながら最速で完了すること。

## 7. Closeout・報告

最終報告は以下の順序とする。

1. **Trial ①：新Promptで学習ポイントの最小化が改善したか**
2. モデル別の品質・指示遵守率・記事セット単価
3. **Trial ②：Luna＋一般化工程でどの程度改善したか**
4. 代表的なBefore／Afterの具体例
5. 一般化の失敗・過剰変更・適用漏れ
6. 既存Productionとの品質・費用比較
7. Fable独立評価とTrial終了Status
8. 次に必要なユーザー判断

特に「モデルを変更すべきか」と「選定・一般化の2工程方式を正式採用すべきか」は別の判断として整理する。

Trial結果が`VALIDATED`でもProduction変更は行わない。

Trial成果物・評価証拠・費用・Prompt・model IDをRepoに記録し、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSとの整合を確認する。

**今回のゴールは、長く焦点のぼやけたKey Phraseを減らし、学習価値の高い表現を簡潔かつ汎用的な形で安定して提供できるかを判断すること。**
---

## Fableの事前確認(再照合し、ズレがあれば開始前に報告)
- 本文: 前回`er098_output/kp_six_model_trial_01/inputs/manifest.json`の14本文(path・sha256)をそのまま使い、現在のファイルsha256が一致することをassertで確認(不一致なら前回manifestに記録された内容を正とし、不一致を報告)。
- Trial①のPrompt: 上記§3-2を一字一句固定。前回と同じ受け渡し調整(本文の直後に`\n\n---\n\n【記事本文】\n`+本文)のみ。prompt_sha256を全70runで同一に。新Promptでは一般化条項が無い(`~`等のplaceholderは出ないはず)ため、機械検証は「厳密本文一致(大小文字・末尾句読点の正規化のみ)+5語以内+自己申告語数一致」。placeholderが出た場合は「Prompt逸脱」として別記録(前回のwildcard照合は使わない)。
- 評価者: 前回と同じ(`gpt-6.1-sol`+`claude-sonnet-5-5`、選定元と異系統を主評価、同系統は参考)。rubric: 前回5観点を維持し、ユーザー§3-3の重視項目(学習ポイント明確/不要な目的語・修飾語なし/最短形/短縮で不自然になっていない)を**追加観点**として別スコアで採点(前回スコアと合算しない)。前回比較は「同一観点の部分のみ」で行い、変更点を`TRIAL_RESULT`に明記。
- 最小化の機械指標(0円): 平均語数/モデル、前回(KP6M、同モデル)との語数分布比較、ユーザー例示3件(think up what happens next/formal agreements with their creators/alone caused the different results)が今回どう変わったか(該当記事・モデルで追跡)。
- Trial②: Before=Trial①のLuna出力(14本文、再選定なし)。一般化モデル=低コスト1モデル。候補は前回遵守100%かつ安価の`gpt-6-luna`(0.35円/セット)または`claude-haiku-5-5`(0.40円/セット)。**Luna自身の出力をLunaで一般化すると同系統になる**ため、第1候補=`claude-haiku-5-5`(理由: 前回遵守100%・安価・選定元と別系統)。単価の出典(`pricing_snapshot.json`等)を記録。一般化Promptは§4-2を固定(受け渡し調整のみ可、事後報告)。入力はKey Phraseだけでなく「元の文脈文(本文中の該当文)」も渡してよいか→**Promptの意味を変えない範囲で、文脈文を参考情報として付ける場合は全件同一形式で付け、その事実を報告**(付けない場合も理由を記録)。出力は変更前/変更後/理由をパースし、Before→Afterの対応表を保持(再選定・件数変化があればNG記録)。
- Trial②の評価: 機械=5語以内・対応追跡・追加語の検出(Afterに元表現にも許容置換語[someone/something/one's/~等・原形/単複]にも無い語が入れば「追加」)。LLM評価=評価者2者(Haiku出力なのでSol・Sonnet両方が異系統、平均を主評価)で§4-3の4項目PASS/NG+「変更すべきだったか(要/不要)」の判定を取り、適用漏れ(要なのに未変更)・不必要な変更(不要なのに変更)・意味変化・不自然を集計。**変更件数の多さを加点しない。**
- 既存Productionとの比較(§7-6): 前回Trialの既存Production行(KP・費用1.83円/セット)を再掲し、今回の「Luna新Prompt+Haiku一般化」の品質(遵守・評価)と費用(選定+一般化)を並べる。方式差(全文渡し vs DB hybrid)の注記を維持。
- 「モデル変更」と「2工程方式採用」は別の判断として、事実材料を分けて整理(推奨はFable)。

## 実行内容
1. 開始前チェック(22節): §1〜§7の要求列挙→設計書`TRIAL_DESIGN_02.md`の対応表。STOPセンチネル・予算・本文sha一致確認。実トークンで見積(300円以下なら続行)。
2. Trial①: `er101_..._run.py`(er098 runの流用)。70回、provider並列。request/response全文・返却model ID・usage・設定・時間・失敗を保存。
3. 機械検証(0円)+最小化指標。
4. Trial②: Lunaの出力が揃った記事から順次一般化→機械検証。
5. 独立評価(①と②を並列)。評価費を選定費・一般化費と分離して記録。
6. Excel `KP_PROMPT_MIN_GEN_COMPARISON_02.xlsx`(Sheet1 Trial①モデル比較[前回KP6M同モデルの結果も並記]、Sheet2 Trial①品質評価、Sheet3 Trial②Before/After、Sheet4 検証詳細、Sheet5 費用・実行条件[Prompt全文・調整Before/After・model ID・token・単価出典・実費・記事セット単価・量産原価(選定+一般化)])。
7. `TRIAL_RESULT_02.md`: ユーザー§7の1〜8順(7・8はFable欄。6は事実)。加えて開始前チェック対応表/Prompt調整の事後報告/評価方法の変更点明示/例示3件の追跡/技術的失敗/費用実測(出典・為替)と日次累計/分類候補と根拠。
8. SSOT: `OPEN_ITEMS.md`新規OPEN(最新+1)「FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02」`TRIAL_DONE_PENDING_FABLE`。`docs/pm/REPORT_LEDGER.md`1行。DECISION_LOG/CURRENT_SPEC/UDRは編集しない(整合確認のみ: CURRENT_SPEC のKP選定節[Grep `KP選定優先順位|Key Phrase選定(A2)`]とOPEN-445を読み、矛盾がないことを1行で記録)。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: KPMG-TRIAL-RUN-委任_01-20261022`を含むAgent tool_useの通番、267前後。先頭行で一致確認)。
9. 段階commit→push→到達確認。`docs/pm/ACTIVE_TASK.md`固定ヘッダ。`docs/pm/RESULT_PACKET_KPMG1.md`。

## 事前指定Read/Grep
- Read: `docs/research/FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01/TRIAL_DESIGN_01.md`(rubric・検証規則)、`TRIAL_RESULT_01.md` §2〜§4・§8(前回の数値・例示3件の出所)、`er098_kp_six_model_trial_01_{common,run,validate,eval,excel}.py`(流用元)、`er098_output/kp_six_model_trial_01/inputs/manifest.json`、`summary.json`。
- Grep: `think up what happens next|formal agreements with their creators|alone caused the different results` in `er098_output/kp_six_model_trial_01/`(前回どのモデル・記事の出力か)。`OPEN-44[0-9]|OPEN-45[0-9]` in `OPEN_ITEMS.md`。

## 実行コマンド全文
実行した全コマンドを実値で記録(例 `.venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_run.py --out er101_output/kp_prompt_min_gen_trial_02 --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 300`)。secret scan `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`。

## SSOT追記文
- OPEN_ITEMS新規行: `| OPEN-4xx | FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 | 2026-10-22 | TRIAL_DONE_PENDING_FABLE | Trial①最小化Prompt×5モデル×14本文(前回と同一本文sha)、Trial②Luna選定→<一般化モデル>一般化Before/After。結果要約<1行>。Excel=docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/KP_PROMPT_MIN_GEN_COMPARISON_02.xlsx。Production無変更、費用JPY<x>。Fable評価待ち。 |`
- REPORT_LEDGER: `- 2026-10-22 | FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_01 | Trial①70選定+Trial②一般化+独立評価、Excel 5シート、費用JPY<x>(選定/一般化/評価内訳)。TRIAL_DONE_PENDING_FABLE。`

## Git
- SSOT編集権: `OPEN_ITEMS.md`(自分の新規行のみ)・`docs/pm/REPORT_LEDGER.md`。他SSOT不可。
- 明示add: `er101_kp_prompt_min_gen_trial_02_*.py`、`er101_output/kp_prompt_min_gen_trial_02/**`、`docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/**`、`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_*`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`。
- commit例: `KPMG 委任_01: KP最小化Prompt 5モデル比較(70選定)+Luna選定の一般化分離Before/After、独立評価、Excel 5シート、費用JPY<x>、Production無変更、TRIAL_DONE_PENDING_FABLE`。

## 報告(RESULT_PACKET_KPMG1.md)
ユーザー§7の1〜8順(7・8はFable欄)。加えて: 開始前チェック対応表/本文sha一致/返却model ID/Prompt調整事後報告(①②)/評価方法の変更点/例示3件追跡/一般化モデルの選定理由・単価出典/Trial②の適用漏れ・過剰変更・意味変化・不自然の件数と例/費用実測(選定・一般化・評価を分離、出典・為替)と日次累計/量産原価(選定+一般化)/技術的失敗/分類候補/RESULT_PACKET 4行/実行コマンド/raw URL。`判断候補`表記。