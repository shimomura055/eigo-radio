# USER_04 (AI-ISLAND-FORM-PRODUCTION-01 / LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_09)

出典: 委任文(subagents/agent-a6dc245fbeb4e6f92.jsonl index0)の「## ユーザー原文(逐語)」以下を一字一句保存。ユーザー指示2026-10-27「①②③学習仕様の整合・フォーム送信確認・AI島Human Review原因調査」。

## ユーザー原文(逐語)

# Claude Code指示｜①②③学習仕様の整合・フォーム送信確認・AI島Human Review原因調査

## 1. 目的と基本方針

以下3件を実施してください。

1. ①②③の学習項目表示・解説仕様について、ユーザー承認内容との整合を確認し、進行中のProduction Wiringへ反映する。
2. 「猿の手」Advancedのフォームテスト送信を評価する。
3. Family X「AIの仮想の島」のHuman Review発生理由を根本調査し、承認済み自動処理で解決可能なら自律的に解消する。

既存の承認済み仕様・品質Gateを変更せず、必要十分な検証を実施する。

## 2. 学習項目①②③の正式仕様【重要】

対象：Family X/Y/Z × Standard/Advanced。

| 区分 | 解説コーナー | 音声 | 本文表示 |
|---|---|---|---|
| ① Key Phrase | 詳細な日本語解説 | あり | 太字＋二重下線 |
| ② 追加解説 | ①と同じ詳細な日本語解説 | なし | 太字＋通常下線 |
| ③ 本文意味表示 | 詳細解説なし・短い日本語訳のみ | なし | 通常下線 |

**①と②は解説コーナーにおいて同等の扱いとする。**

①と②の違いは、①がKey Phraseとして音声化対象にもなることです。

- ①②の詳細解説は日本語。
- Standard／Advancedともに同じ機能を提供する。
- 解説内容の品質基準は同等。
- ③には詳細解説を生成しない。
- ①②③のユーザー確定内容を後続工程で変更しない。
- 本文表示は承認済みの二重下線／通常下線方式を使用。
- 色分け・背景マーカーは使用しない。
- 過去公開記事への遡及は不要。

**以前の委任文にあった「Standardの②を英語で解説する」という記述は誤りなので撤回します。**

「英語表現について日本語で詳しく説明する」が正しい仕様です。

旧仕様の「Advancedのみ」などを根拠として、今回承認されたStandardの②詳細解説を無効化しないこと。

進行中のSLOT-23実装、Part 1解説生成、公開ページ、Validator、SSOTとの整合を確認する。

既に正しく実装されている部分は重複作業せず、誤り・不足分だけ修正してください。

## 3. フォーム送信結果の確認

以下のテスト送信をユーザーから受領しています。

対象：Family Z「猿の手」Advanced。

### ① Key Phrase

- accept no responsibility：責任を負わない
- interfere with fate：運命を変えようとする
- pulled free：振りほどく

### ② 追加解説

- caught in the machinery：機械に巻き込まれる
- wail of loss：失った悲しみを表す叫び声

### ③ 本文意味表示

- shake one's husband awake：自分の夫を揺すって起こす
- compensation：補償金
- snatch：さっとつかみ取る
- deserted：人けのない
- burial：埋葬

文法：0件  
自由コメント：テスト送信

照合コード：

`AIF1-monkeys_paw__b1b-00eb90-00000000-8388280a-e45da6b337-0-8d5a3093-a269`

### 評価・確認事項

- ①3件、②2件、③5件の区分が正しく読み取れる。
- 文法0件・自由コメントが保持される。
- 照合コードが省略・改変されない。
- ユーザー向けコピーに不要なJSON・内部コードが混入しない。
- 受信した内容とフォームの保存済み候補データを照合できる。

**本件はフォーム送信のテストであり、「猿の手」の制作内容を正式確定したものではありません。**

すべての日本語訳は仮訳・未確定であるため、正式採用・Production反映しないこと。

テストのための追加API実行や音声生成は不要です。

## 4. AI島Human Review発生理由の調査【優先】

対象：Family X「AIの仮想の島」Standard／Advanced。

現在Claudeから以下のHuman Reviewが提示されています。

- Standard：`AI agents`
- Advanced：`AI systems`

確認ページ：

https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01/hr_01.html

しかし、ユーザーが提供したStandard／Advanced本文では、これらの表現がそのまま対応していません。

特にAdvanced末尾には `AI agents` が存在しますが、`AI systems` は確認できません。

**現時点では、原稿の書換え・Local Rewriteの発動・Human Reviewが必要になった理由を確認できていません。**

### 調査事項

以下を実際のProduction runtime・ログ・保存データに基づいて明確にしてください。

1. **問題となった元の英語原稿は何か。**
   - 該当する全文または文。
   - 該当セグメント・Role・Level。
   - ユーザーが確認済みの本文との一致・不一致。

2. **実際に原稿の置換・書換えが行われたか。**
   - 変更前と変更後の英文を逐語提示。
   - 変更がない場合は「変更なし」と明示。
   - 書換えがあった場合は、発動した工程・理由・承認済み根拠を示す。

3. **TTS retry／Local Rewriteの発動状況。**
   - 各工程が発動したか。
   - 発動回数・結果。
   - 発動しなかった場合は、その理由。

4. **ASR判定結果。**
   - Primary（OpenAI）の認識結果。
   - Secondary（Azure）の認識結果。
   - 原稿との具体的な差分。
   - 同音救済・既存Phrase List等の承認済み対策が適用されたか。

5. **なぜHuman Reviewになったのか。**
   - 正式Gateのどの条件に該当したか。
   - 自動処理で解消できなかった理由。
   - 現在のHR対象音声が、何を確認するためのものか。
   - 音声の品質問題なのか、原稿の整合問題なのか、ASRの認識差なのかを区別。

### 調査・修正の原則

- **Local Rewriteで正式品質Gateを通過済みなら、不要なHuman Reviewを求めない。**
- ただし、正式仕様が明示的にHuman Reviewを要求する場合は省略しない。
- Human Reviewを省くためにGateを緩和しない。
- 承認済みのLocal Rewrite、retry、同音救済、ASR判定を正しく適用する。
- 自動処理の不具合や配線漏れが原因なら、既存仕様・予算内で原因究明→修正→検証まで自律実施する。
- 原稿の未承認変更があれば、変更内容と影響を明確にする。
- 無関係な本文の再生成や、新しい原稿への無断差替えを行わない。

過去の既知不具合、Production経路、確定内容保護、retry／fallback／resumeとの整合も確認してください。

### 必要なHuman Reviewが残った場合

調査後も正式仕様上Human Reviewが必要な場合のみ、次をセットで提示してください。

- 該当する元原稿
- 書換え前後の英文（変更がある場合）
- 推奨音声1件
- OpenAI／AzureのASR結果
- 具体的な不一致箇所
- 自動処理では解消できなかった理由
- AIの評価とユーザーに確認してほしい内容

不要な複数Take比較や、技術的判断の丸投げをしないこと。

## 5. Production Wiring・SSOT整合

①②③の表示機能については、別途指示済みのSLOT-23 Production Wiringを継続してください。

特に以下を確認する。

- ①②の日本語詳細解説が両レベルで表示される。
- ①のKey Phrase音声が維持される。
- ③は短い日本語訳のみ。
- 本文表示の強調仕様が一致する。
- ユーザー確定内容が改変されない。
- X/Y/Z全6経路で正式Productionへ接続される。
- 必須テスト・runtime evidence・Fable受入を満たす。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitへ正しく反映する。

既存のフォームProduction Wiring、文法事前生成、確定内容保護など、すでにPRODUCTION_WIREDと確認された機能については、無関係な再検証・再実装を行わない。

## 6. QCD・STOP条件

優先順位：品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用。

- 既存成果とruntime evidenceを優先して再利用。
- 独立して進められる①②③実装整合とAI島HR調査は並列化。
- 不要な再生成・追加Trialを実施しない。
- 開発費1,000円／日（JST）および個別承認枠を遵守。
- 既存仕様内の問題は自律的に解決。
- 新たな仕様変更、品質基準変更、重大なblocker、予算超過はSTOPして報告。

## 7. 報告事項

判断への重要度順に以下を報告してください。

1. **AI島Human Reviewの真因**
   - 書換え有無
   - Before／After
   - TTS retry／Local Rewrite履歴
   - Primary／Secondary ASR結果
   - HRが本当に必要か
2. 既存仕様内での修正・再検証結果
3. ①②③の日本語解説・表示仕様の整合結果
4. SLOT-23のProduction Wiring状況
5. 「猿の手」フォームテスト送信の照合結果
6. Fable受入、SSOT／Git更新、QCD、残Open Item

**最重要：AI島のHuman Reviewを単に再提示するのではなく、まず発生理由を証拠に基づいて説明し、承認済みの自動処理で解決可能なものは自律的に解決してください。**

そのうえで、AI島Standard／Advancedの完成記事制作を、品質を守りながら最速で進めてください。