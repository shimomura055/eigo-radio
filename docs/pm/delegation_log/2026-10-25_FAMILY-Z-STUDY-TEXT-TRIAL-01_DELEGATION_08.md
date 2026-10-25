# 委任文(Fable→sonnet-worker)
管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_08(Trial-04 Phase 0: 上流設計改善[Part 1=本文背景なし別LLM、Part 2=選定/執筆分離]の設計+DEV実装準備[有料呼出なし]+Opus条件Aレビュー依頼書。**API 0円**。有料生成はOpusレビュー後のFable Goで委任_09)
Status: TRIAL_APPROVED(ユーザー2026-10-25、UDR #196はこの指示で上書き=「(b)相当の上流設計改善Trialを承認」) / Production採用・配線: 未承認

## 0. ユーザー原文(2026-10-25、逐語。まず `docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_04.md` に以下を一字一句そのまま保存すること)

```
# Claude Code指示｜英語学習解説 Part 1・2 上流設計改善Trial-04

## 1. 目的・承認範囲

英語学習解説について、Part 1・2の品質改善Trialを実施してください。

**ユーザーは今回のTrialを正式承認しています。Production採用・配線は未承認です。**

目的は以下の2点です。

- Part 1：本文の文脈に引っ張られず、英語表現本来の意味と実用的な使い方を説明できること。
- Part 2：学習価値の高い英文・構文を選び、学習者が理解しやすい自然な解説を生成できること。

既存Trial-03（Prompt 03d）を比較基準とします。

## 2. 対象作品

前回と同じ3作品、いずれもAdvancedです。

1. Family Z『賢者の贈り物』
2. Family X『イグ・ノーベル賞2026』
3. Family Z『開いた窓』

各作品の正式本文・Key Phraseを使用し、前回Trialと入力条件を揃えてください。

Part 3・4は改善対象外で、既存仕様・Promptを維持します。

## 3. Part 1｜Key Phrase解説の改善

### 現状の問題

現行方式は本文背景に引っ張られ、本文での意味を英語表現の代表的な意味のように説明する傾向があります。

例：

- `nutrient-rich crystals`：本文固有の専門的表現を、一般的な定型表現のように扱う。
- `give way`：地面が崩れる用法から説明を始め、広範な意味が伝わりにくい。
- `at a moment's notice`：即応できることに説明が偏り、予告・通知がほとんどないという核となる意味が弱い。

### 改善方式

**本文背景を持たない別LLMに、Key Phraseの一般的な解説を担当させてください。**

既存工程では次を確定します。

- Key Phrase
- 日本語意味（本文中）
- 本文引用英文
- その日本語訳

別LLMは、原則として記事全文・あらすじ・物語背景を受け取らず、Key Phraseそのものの解説を担当します。

既存の本文中の意味と、一般的な解説を明確に分離してください。

解説の観点：

1. 表現の核となる意味
2. 主要な用法と使用場面
3. よく使われるコロケーション
4. 重要な類義語・近似表現との違い
5. 自然な比喩的・拡張的用法

ただし、すべての項目を機械的に列挙する必要はありません。学習価値の高い内容を必要十分な分量で、自然な文章として説明してください。

複合表現では、必要に応じて学習価値の中心となる語句を説明してください。例えば `nutrient-rich crystals` では `nutrient-rich` の一般的な使い方を説明する方が有益です。

使用頻度の順位は、根拠なく断定しないこと。類義語の違いも過度に断定せず、自然な英語として正確に説明してください。

**表示名を「実用性を重視した解説」から「解説」へ変更してください。**

## 4. Part 2｜Grammar & Sentence Structureの改善

### 現状の問題

従来の一括生成では、英文選定・構文分析・解説執筆を同じ工程で行っているため、次の問題が発生しています。

- 基本的すぎる文法を選ぶ。
- より学習価値の高い構文を見落とす。
- 説明が形式的・冗長になる。
- 開発者向けの選定理由とユーザー向け解説が混在する。

### 改善方式

**工程を「選定」と「解説執筆」に分離してください。**

#### Step A：英文・構文の選定

Advanced本文全体から、読解上の難所となり、解説によって理解が深まる英文・構文を選びます。

選定観点：

- 文法・構文の難しさ
- 文の構造を誤解しやすいか
- 通常の語順・構造との違い
- 構文によって生じる意味やニュアンス
- 解説による学習価値

文法用語の難しさそのものを評価しないこと。

基本的な文法を説明するだけの選定は避けてください。

解説価値の高い文がない場合は、0件を認めます。

選定工程の内部では候補を比較して構いませんが、ユーザー向けの文章にはその評価過程を混ぜないでください。

#### Step B：ユーザー向け解説の執筆

Step Aで確定した英文と構文を受け取り、解説文の作成に専念させてください。

ユーザー向け表示は、以下の順序を基本とします。

1. **対象となる本文英文**
2. 日本語訳
3. 文法・構文の仕組み
4. 必要に応じた通常表現・語順との比較
5. 意味・ニュアンス・表現効果

解説は自然で分かりやすい日本語とし、開発者向けの選定理由・難易度評価・品質判定を含めないでください。

### 品質参考例

『賢者の贈り物』の以下の文：

"One was Jim's gold watch, handed down from his grandfather to his father, and then to him."

これについて、過去分詞による後置修飾を説明し、非制限用法の関係代名詞節 `which had been handed down ...` との関係、コンマの役割、本文での意味を自然な流れで説明できることを品質参考例とします。

ただし、この構文を必ず選ぶという指示ではありません。

『賢者の贈り物』では倒置も有力候補です。どちらを選ぶかも含め、学習価値に基づいて判断してください。

過去のTrialで問題となった、基本的な `whose` だけの解説へ戻らないこと。

## 5. 上流設計による品質改善

**後段のCheckerやValidatorを新設して品質問題を検出する方式は、原則採用しません。**

Part 1はLLMへの入力情報を切り分け、Part 2は選定と執筆の責務を分離することで、生成段階から品質を改善してください。

既存のTrial・Prompt・処理機構を確認し、不要な重複処理を作らないこと。

新たなLLM呼出による品質改善と、呼出回数・処理時間・費用の増加を比較してください。

## 6. Trial実行・評価

同じ3作品でTrial-03との比較を実施してください。

### Part 1

- 本文固有の用法に偏らず、核となる意味を説明できているか。
- 主要な使用場面・コロケーションを適切に紹介できているか。
- 類義語の違いや拡張用法が正確か。
- 本文中の意味との矛盾がないか。
- 不自然な用法の創作や説明の水増しがないか。

### Part 2

- Advancedにふさわしい英文を選定できているか。
- より価値の高い構文を見落としていないか。
- ユーザー向け解説が分かりやすいか。
- 文法の仕組みと意味・効果を正しく説明できているか。
- 開発者向け情報がユーザー向け本文に混入していないか。
- 解説対象がない場合に、無理に作らず0件とできるか。

特に『イグ・ノーベル賞2026』『開いた窓』では、従来の文法選定の不安定さが改善されるか確認してください。

同一条件での再現性も必要十分な範囲で確認してください。

## 7. 自律的改善・QCD

初回結果が不十分でも、承認された範囲・予算内で原因分析、設計修正、再検証を自律的に行ってください。

同じ方向のPrompt修正を無益に繰り返さず、改善見込みが低い場合は工程設計から見直してください。

- 独立作業は並列化
- 既存成果物を最大限再利用
- 不要なWeb検索・全文再生成を回避
- 品質を維持した最速の進行
- 量産単価70円／記事セットを意識
- 必須のOpusレビュー・Fable独立評価を実施
- 承認済み予算・Scope・STOP条件を遵守

今回の改善が成立したら、追加の磨き込みを行わずTrialを終了してください。

## 8. 最終成果物・報告

以下を提出してください。

1. **3作品のPart 1・2完成出力全文（無編集）**
2. ユーザー向け解説と開発者向け評価を明確に分離した表示
3. Trial-03とのBefore／After比較
4. Part 1の意味・用法・コロケーションの品質評価
5. Part 2の候補選定と解説品質の評価
6. 以前の問題が改善したか、具体例による説明
7. Part 3・4への影響確認
8. 処理時間・LLM呼出回数・費用・量産単価の比較
9. Fable独立評価・Trial Closeout Status
10. SSOT／Git反映状況と残存Open Item

Trial終了Statusは、REJECTED／VALIDATED／USER_DECISION_REQUIREDのいずれかとしてください。

**Production採用・配線はユーザーの明示承認があるまで行わないこと。**

### 最終目標

Part 1では、本文の意味だけに縛られず、実際に使える英語表現の知識を習得できること。

Part 2では、読解が難しい英文について、文法・構文の仕組みと意味を自然な日本語で理解できること。

**いずれも開発者向けの評価文章ではなく、学習者がそのまま読んで価値を感じられる完成解説を作ることを重視してください。**
```

## 1. 前提
- Trial-03資産: `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{run_trial_03.py,PROMPT_03.md,PROMPT_DIFF_03d.md,OUTPUT_03d_*_RAW.md,COMPARISON_03.md,EVAL_03.md,FABLE_EVAL_03.md,INPUT_CHECK_03.md,BUDGET_LOG_01.md}`。Before=03d(第1標本・第2標本)。
- 3作品のAdv本文・KP・本文中の意味(日本語)・引用英文・その日本語訳は、Trial-03の出力/入力から確定済みのものを再利用(INPUT_CHECK_03.mdの出典・sha)。「本文中の意味」はProduction正式KP gloss(X2p'配線後のgloss)があればそれを正とし、なければTrial-03出力のPart 1項目2〜4を使う(どちらを使ったか記録)。
- モデル=gpt-6-luna(Trial-01〜03と同一、最新世代)。Part 3/4はTrial-03の現行Prompt・一括生成のまま。
- 既存機構の確認: Production側にKP解説生成(X2p' `er003_key_words_gloss_alignment.py`の`meaning_in_text_en`等、Family X/Z KP gloss)があるため、Part 1「本文中の意味」との重複を作らないこと、Trial-04の別LLM(一般解説)が将来どこに置かれうるかを設計書で言及(Production配線は未承認)。

## 2. Phase 0作業(API 0)
A. `DESIGN_04.md`:
   - Part 1: 工程分離。入力=KP(+複合表現なら学習価値の中心語句の指定方法)、本文中の意味・引用・訳は**既存工程の確定値として表示にそのまま使い、別LLMには渡さない**(原則)。別LLM Prompt(一般解説: 核となる意味/主要用法と場面/コロケーション/類義語との違い/比喩・拡張用法を、機械的列挙でなく必要十分な自然文で。頻度順位の無根拠断定・類義語差の過度な断定を禁止)。表示=「解説」。本文中の意味と一般解説の分離表示。本文中の意味との矛盾を防ぐために別LLMに最小限何を渡すか(KPと本文中の日本語意味のみ渡す/何も渡さない)の2案を比較し推奨を決める。
   - Part 2: Step A(選定、本文全体入力、候補比較は内部、出力=選定英文+構文の名前+選定理由[開発者向け、ユーザー表示には出さない]、0件可、上限2)→Step B(執筆、入力=選定英文+構文のみ、出力=対象英文/日本語訳/仕組み/必要に応じ通常表現との比較/意味・ニュアンス・効果、開発者向け情報禁止)。Step Aに本文全体を渡すことで倒置・後置修飾など見落としを減らす設計。Step Aの出力schema(JSON)と、Step Bへの受け渡し。
   - 呼出構成と費用比較: Trial-03=1 call/記事セット(約0.28円)。Trial-04=Part 1別LLM(KP3個まとめて1 call or 3 call)+Step A 1 call+Step B 1 call(0〜2件)+Part 3/4(既存一括の残り)=合計3〜4 call/記事セット。見積(出典=usage_03d)と処理時間。
   - 評価計画: ユーザー原文§6の観点、Before=03d。N=2/作品(再現性)。開発者向け評価とユーザー向け表示の分離形式(出力ファイルを `OUTPUT_04_<work>_USER.md`[学習者向け完成形]と `OUTPUT_04_<work>_DEV.md`[Step A候補・選定理由・usage]に分ける)。
   - Validator新設なし。引用逐語照合は既存の決定論スクリプト(check_quotes_03流用)のみ。
   - 予算: Fable上限20円(自律枠)。
B. DEV実装準備(有料呼出なし): `run_trial_04.py`(03の`build`流用、`--dry-run`でPrompt全文を `_prompt_04_*.txt` に書き出す)、Prompt `PROMPT_04.md`(Part 1別LLM / Step A / Step B / 残Part 3-4の各全文)。dry-runで3作品分のPromptを生成し、本文背景がPart 1別LLM Promptに混入していないことをgrepで確認。
C. `OPUS_REVIEW_REQUEST_02.md`(条件A): 論点=(a)Part 1の入力切り分け(何を渡し何を渡さないか)が「本文に引っ張られない」と「本文中の意味との矛盾なし」を両立するか、(b)Step A/Bの責務分離とschemaが基礎文法選定・見落とし・開発者情報混入を上流で防ぐ設計か、0件判定の置き場、(c)既存Production KP gloss(X2p')との重複・将来の配線位置、(d)呼出増(1→3〜4)の費用対効果と量産単価、(e)再現性評価N=2で何が言えるか、(f)Validator新設なし・既存Trial資産再利用の確認。
D. SSOT: UDR #196を「判断済み(2026-10-25、ユーザー指示=上流設計改善Trial-04を承認、原文path)」に更新、OPEN-497 Status=`TRIAL04_DESIGN_PENDING_OPUS_A`、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 該当行更新。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。`py`使用。
E. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 512 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_08.md`。冒頭が「管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_08」と一致するか確認、不一致なら index 510〜515 を順に試す(`--index -1`不可)。
F. Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0) → `git commit --only -- <path…>` → `git push origin HEAD:main`。
G. 報告 `docs/pm/RESULT_PACKET_FZST8.md`: 設計要点、呼出構成と費用見積、dry-run確認結果、OPUS_REVIEW_REQUEST_02.mdの所在、変更ファイル・commit、`check_delegation_prompt.py`結果、問題点。**有料生成は開始しない。**

## 3. 禁止
Production code/Prompt/flag変更、KP追加選定、音声生成、Web検索、Part 3/4 Promptの変更、Checker/Validator新設、有料API呼出、`.venv\Scripts\python.exe`以外の使用、自PID以外のprocess終了。