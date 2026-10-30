# ユーザー指示原文(逐語、2026-10-30受領。Trial 03 方式B(N5) APPROVED_FOR_PRODUCTION→PRODUCTION_WIRED、全6経路)
<<<USER>>>
# Claude Codeへの正式指示｜Key Phrase一般化 N5方式 Production採用・全Family配線

## 1. ユーザー正式決定

**採用方式：Trial 03 方式B（N5）**

**Status：APPROVED_FOR_PRODUCTION**

**最終到達目標：PRODUCTION_WIRED**

対象は以下の全6経路。

- Family X：Standard／Advanced
- Family Y：Standard／Advanced
- Family Z：Standard／Advanced

ユーザーは、Trial 03の品質結果、良質候補の脱落、残存する境界例、量産単価への影響を確認したうえで、**N5の正式Production採用を承認した。**

D・E1L・E4・N2について、改めて採用判断を求めないこと。

## 2. 採用する仕様

Trial 03でVALIDATEDとなったN5方式を、正式ProductionのKey Phrase／Word候補生成・一般化工程に実装する。

特に以下を忠実に反映する。

### ① 本文の意味・用法に基づく一般化

- 本文中での意味・用法を優先する。
- someone／somethingは本文の文脈・指示対象から判断する。
- 選定理由の文章に引きずられて、別の語義へ一般化しない。
- 自然で汎用的な基本表現への一般化は維持する。
- 修飾語の削除だけを理由にNGとしない。

### ② 一般化による意味変化の防止

- 一般化によって本文と異なる意味・用法になる場合は、安全な本文形への復元等、Trial 03で検証されたN5の処理を適用する。
- 復元時は英語表現と日本語訳の整合性を保つ。
- 一般化後の表示形と、本文中の根拠表現を区別して管理する。
- 英語として自然でも、本文と異なる語義の日本語訳を付けない。

### ③ N5の追加確認

N5固有の別系列AIによる意味・用法・日本語訳の整合確認を、Trial成功版に従って実装する。

単に誤りを検出するだけでなく、検出後の修正・復元・候補取扱いがTrialで検証した動作と一致することを確認する。

### ④ 既存仕様の維持

- 易しい表現を機械的に除外しない。
- 難易度4段階表示はそのまま維持する。
- 本文に根拠のない候補を生成しない。
- 5語以下など既存の承認済み制約を維持する。
- 候補数を満たすために不適切な表現を補充しない。
- ユーザーによる最終選定の役割は変更しない。

**N5採用を理由に、未承認の新しい品質GateやPrompt改善を追加しないこと。**

## 3. Production配線

Claudeは既存の正式Production経路とTrial 03の実装を照合し、最も効率的な方法でN5を正式配線すること。

必須範囲：

1. 全Family・全レベルの正式初回候補生成経路
2. retry／fallback／regeneration／resume
3. 候補生成後の品質検査・Human Review
4. 英語表現・日本語訳・本文根拠表現のデータ受渡し
5. 既存のKey Phrase救済仕様・gloss整合仕様
6. 候補確定後の学習項目生成・音声化など後続工程

共通仕様は原則として全Familyへ同時配線する。

特に、DEV／Trial専用経路にしか適用されない状態や、retry時だけ旧方式へ戻る状態を防ぐこと。

旧D／E1L等の不要なProduction参照・検査が残る場合は、承認済み仕様との整合を確認し、必要十分な範囲で整理する。

## 4. 検証・受入条件

### A. Trial 03との一致

N5のPrompt、モデル、工程順序、判定条件、修正・復元処理をTrial 03の確定版と照合する。

既存Trialデータを回帰テストに活用し、少なくとも以下を確認する。

- `hear it out` の一般化
- `take points away from` の一般化と日本語訳
- `keep one's eye on` のような境界例
- `set a lower limit` → `set a limit` 型の許容可能な一般化
- `take an unexpected turn` → `take a turn` 型の許容可能な一般化
- 日本語訳が旧語義のまま残る問題の防止
- 既存の良質候補を不必要に失わないこと

ここでの目的は、新しい基準でTrialをやり直すことではなく、**承認されたN5の挙動を正式経路でも再現すること**である。

### B. 正式Production実証

Family X／Y／Z × Standard／Advancedについて、正式runnerからN5が発火することを確認する。

証拠として以下を残す。

- actual model_id
- Prompt／設定version・hash
- routing
- N5各工程の実行・判定記録
- 英語候補・日本語訳・本文根拠の一致
- retry／fallback／regeneration／resumeの挙動
- 必須Regression／Validator／Integration test結果

既存runを安全に再利用できる箇所は再利用し、本文・TTS等の不要な再生成を避ける。

ただし、費用節約のために正式runtime証拠を省略しないこと。

### C. Fable独立受入

FableはClaudeの完了報告をそのまま承認せず、ユーザー採用仕様、Trial 03結果、正式Production経路、runtime evidence、後続工程との整合を独立に照合する。

全6経路で必要条件が満たされた場合のみPRODUCTION_WIREDとする。

## 5. QCD・予算・STOP

優先順位：

**品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費**

N5の量産単価は、Trial報告値で**約6.28円／記事セット（Std＋Adv）**。

正式実装後に実測し、Trial見積もりとの差異を報告する。

品質を維持したまま削減できる無駄なAPI呼出や重複処理は最適化してよい。ただし、承認済みN5の品質機能を独断で省略しないこと。

開発費は既存の個別承認枠・原則1,000円／日（JST）の範囲で管理する。予算超過が見込まれる場合は、事前に理由と必要額を提示する。

**不要な日付分割・待機・追加Trial・少額費用ごとの承認要求は行わない。**

承認範囲内の不具合は、原因究明→修正→検証まで自律的に進める。

新たな仕様変更、品質基準変更、重要なQCDトレードオフ、予算・Scope超過が必要な場合のみSTOPしてユーザー判断を求める。

## 6. SSOT・Closeout

正式配線後、以下を更新する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- 必要なPM Governance・委任記録
- Git commit／push

特に以下を確認すること。

- Trial 03のVALIDATEDからN5のAPPROVED_FOR_PRODUCTIONへの正式採用記録
- 旧#228の採用判断待ちの解消
- N5のFamily別Production Wiring Status
- 旧方式・未承認仕様へのDangling Referenceがないこと
- Trial専用実装と正式Production経路が混同されていないこと
- 未完了項目がある場合はOPEN_ITEMSに明示されていること

## 7. 完了報告

中間報告は不要。完了後、次の順に簡潔に報告すること。

1. **結論：PRODUCTION_WIRED達成可否、Fable受入結果**
2. Family X／Y／Z × Standard／AdvancedのStatus一覧
3. Trial 03 N5との一致・意味／用法品質の回帰結果
4. 正式runtime evidence・モデル／Prompt／routing
5. retry／fallback／regeneration／resumeと後続工程の整合
6. 実測量産単価・開発実費
7. SSOT／Git反映結果
8. 残存Open Item・ユーザー判断が必要な事項のみ

**最終目標：ユーザーが正式採用したN5方式が、全Family・全レベルの正式Production経路で確実に動作し、意味・用法・日本語訳の正確性を維持した状態でPRODUCTION_WIREDに到達すること。**
<<<END>>>
