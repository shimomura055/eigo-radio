2026-10-16 ユーザー指示原文(ChatGPT経由の実行指示。A=AUW / B=Family C JA TTS / C=DQI)。Fableが受領。
# Claude Code／Fableへの指示
## AUW Production完成・Family C不具合是正・Fable PM判断改善

### 0. 今回の指示の位置づけ

本指示は、これまでのユーザー正式決定に基づく実行指示である。

以下の3案件を明確に分離して管理する。

- **A：AUW統一ASR判定のProduction完成**
- **B：Family C日本語TTSの既存Production不具合是正**
- **C：Fable自律PMの判断品質改善**

A・B・Cを一つの仕様変更として混在させない。

各案件のStatus・受入条件・Open Item・証拠を独立して管理する。

**共通原則：ユーザーがすでに決定した事項を、理由なくUSER_DECISION_REQUIREDに戻さない。**

承認済み仕様の実現に必要な技術調査・修正・テストは、自律的に進める。

新しい仕様判断、承認範囲を超える変更、重大な安全・品質・予算問題が発生した場合のみSTOPする。

---

# A. AUW統一ASR判定のProduction完成

**管理ID：ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01**

**現在Status：APPROVED_FOR_PRODUCTION**

**到達目標：PRODUCTION_WIRED**

## A-1. ユーザー正式決定

mainへのmergeを正式に許可する（REGISTER #87：Go）。

既存branch `feat/auw-unified-asr-01` の実装・テスト・証拠を確認し、最新mainとの整合を取ったうえで、既存Git運用規則に従ってmergeする。

merge後も、必要な是正・Regression・runtime evidence・SSOT反映まで継続する。

**mergeだけでタスク完了としない。**

## A-2. 統一ASR判定の正本

英語・日本語、全Family・全Production Sectionについて以下を基本とする。

1. Primary ASRがPASSなら採用。
2. Primary NGなら、不一致の種類・大きさにかかわらず原則Secondary ASRを実行。
3. Secondary PASSならPASS_WITH_WARNINGとして採用。
4. WARNINGは事後試聴リストに自動登録。事前Human Reviewは不要。
5. 両方NGなら既定のTTS再生成へ進む。
6. 通算3回のTTS生成で不合格なら、承認済みのLocal Rewrite／Human Review経路へ進む。
7. 数値・否定などの明確な重大内容差、独立音声品質QAは維持する。

Melos saidのConnected Speech／M1の合格実績を維持する。

**Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない。**

## A-3. 日本語固有名詞・低類似度の除外を是正

現在のU1（REGISTER #83）は、ユーザー正式承認済み統一仕様との不整合として扱う。

現在の固有名詞差・類似度0.4未満等によるSecondary事前除外を調査し、承認済み共通ルールに合わせて是正する。

実行要件：

- 固有名詞差でもPrimary NGならSecondary確認。
- 低類似度でもPrimary NGならSecondary確認。
- Secondaryが原稿を正当に支持すればWARNING付き採用。
- 数値・否定等の保護差、独立QAは例外として維持。
- 既存日本語ASR Validator・Pronunciation Ledgerとの整合確認。
- 過剰救済・誤受理がないことをRegressionで確認。

これは新仕様Trialではなく、**承認済み仕様への実装修正**である。

新たな仕様判断が本当に必要な場合を除き、同じ採否をユーザーへ問い直さない。

## A-4. Local Rewrite後のforce_secondaryを確認

U2（REGISTER #84）について、A2_ONLYの既存例外の意味・成立経緯・品質上の必要性を確認する。

注意：

- A2は従来のStandard相当の処理経路。
- B1系はAdvanced相当。
- Primary NG→Secondaryは両レベル共通の正式仕様。
- `force_secondary`はPrimary PASS時にもSecondary確認を要求する特殊経路であり、通常のSecondary利用とは別。

実施事項：

1. 既存仕様・承認履歴・Production codeを照合する。
2. なぜA2だけに限定されているのか、品質・安全上の根拠を確認する。
3. 今回の統一仕様と矛盾しないか判定する。
4. 不要な旧例外なら、承認済み共通仕様へ整理する。
5. 例外維持が本当に必要なら、理由・適用範囲・影響を報告する。

**Primary PASS時のSecondary強制照合を、根拠なく全レベルへ拡大してはならない。**

## A-5. 残Sectionの実証

43行マトリクスを次の区分で再整理する。

- 実音声で検証済み
- 新規生成が必要だが未検証
- 既存音声の再利用・複製が仕様どおりで、追加ASR不要
- 正式仕様上のN/A
- 別Production不具合で検証不能

特にFamily B A2 narratorの見出し・Hook・Tension・Closingの必要な実音声確認を実施する。

Family C日本語の既存TTS不具合はB案件で扱い、AUWの実装漏れと混同しない。

ただし、全SectionのProduction Wiring受入条件から未確認項目を黙って除外しない。依存関係・未充足条件を明示する。

## A-6. Secondary障害時の処理

U4（REGISTER #86）については、**現行挙動を当面許容する**。

技術障害でHuman Review Lock／Local Rewriteへ進む非効率は、既知の独立Open Itemとして管理する。

今回、ユーザー承認なしにLock挙動を変更しない。

## A-7. AUW完了条件

- 正式Production初回経路に統一判定を適用
- retry／fallback／regeneration／Local Rewrite後の整合
- 日本語U1不整合の是正
- U2の必要性確認・承認範囲内の整理
- 必要な全Section実音声・runtime evidence
- 数値／否定／Connected Speech／M1／F1のRegression PASS
- WARNING試聴リストが実際に機能
- 二重Secondary呼出・無限retryなし
- actual model_id／routing確認
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- main merge／push／必要なmerge後test
- Dangling Reference Check
- Fableによるユーザー承認内容との独立照合

すべて満たした場合のみPRODUCTION_WIRED。

未充足があれば、達成済み事項と未達事項を区別して報告する。

---

# B. Family C日本語TTSの既存Production不具合是正

**管理ID：FAMILY-C-JA-TTS-PRODUCTION-FIX-01**

**現在Status：既存Production不具合の是正承認**

**到達目標：正式Production経路で日本語音声生成・検証・再利用整合が正常動作すること**

## B-1. 確認済みの不具合

Family CのProduction runner `er013_family_c_production_runner_01.py`で、日本語Comment生成時にも共通のnarrator処理を呼んでおり、その内部でTTSの言語が`"en"`に固定されている。

このため日本語Commentの新規音声生成が失敗した。

また、既存音声のreuse_fromで、原稿変更後にも旧音声が紐づくリスクが確認されている。

**AUWの統一ASRとは別のProduction不具合である。**

## B-2. 是正方針

最初に既存のFamily C正式仕様とProduction経路を確認する。

そのうえで、承認済み仕様の範囲内で必要な修正を実施する。

最低限：

- 日本語Commentを日本語としてTTS生成する。
- 日本語タイトル等、同じ問題が及ぶSectionを調査する。
- 適切な日本語Voice・言語設定・ASR Validatorを使用する。
- 英語Sectionの従来動作を壊さない。
- 日本語の長さ・音声品質・Segment構造を検証する。
- 原稿と音声の対応を保証する。
- reuse_from／metadata／hash等の整合を確認し、変更後の原稿に旧音声が誤って紐づく問題を防ぐ。
- retry／fallback／regenerationとの整合を確認する。
- 必要な実音声をProduction正式経路から生成し、runtime evidenceを取得する。

単なる`"en"`→`"ja"`の置換だけで安全に解決できるなら、過度な改修はしない。

ただし、単一行の修正だけで品質・再利用整合を確認せず完了としない。

## B-3. 自律是正原則

既存仕様に沿った言語設定・配線・metadata等の技術的不具合修正であれば、ユーザーへ再承認を求めず実施する。

新しいVoiceの正式採用、音声品質基準の変更、日本語Commentの内容仕様変更など、新たな仕様判断が必要になった場合のみSTOPする。

不具合がAUW検証中に発見されたことを理由に、AUW仕様と混同しない。

## B-4. 完了条件

- Family C日本語Commentの新規TTS成功
- 必要な日本語Sectionの生成・ASR確認
- 英語Sectionの回帰なし
- 原稿変更時の誤音声再利用なし
- Production実行でruntime evidence取得
- Validator／Regression／integration test PASS
- SSOT／Open Item／Git反映
- Dangling Reference Check
- 実成果物が既存Family C仕様を満たすこと

条件未充足ならPRODUCTION_WIREDとしない。

---

# C. Fable PM判断品質の改善

**管理ID：PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01／DECISION-QUALITY-IMPROVEMENT-01**

**現在Status：既存改善は実装済みだが、目的達成は未検証・未達**

**今回の到達範囲：改善方式の検討・既存規則との整合確認・具体案の提示**

**Day 5〜6：引き続き保留**

## C-1. 解決すべき問題

Fableはこれまでの改善で、ユーザー原文・最終成果物・受入条件の照合を行うようになった。

しかし、次の問題が残る。

1. 承認済み仕様を再びユーザー判断へ戻す。
2. 自己解決可能な技術的不具合をユーザーへ転送する。
3. 発見済みの重大品質NGを最終判定へ正しく反映できない。
4. 本来のタスクと、新規発見した独立問題を混在させる。
5. 検出した不適合に対する是正・STOP・ユーザー提示制限が不適切。

単なる報告形式の問題ではなく、PMの意思決定品質の問題として扱う。

## C-2. 改善案の検討

以下はChatGPTからの参考提案であり、実装方式の指定ではない。

Fable自身が検討し、必要に応じてOpus独立レビューを受けること。

### 提案①：重大品質NGと最終受入の整合強制

成果物に重大な意味反転、Fact欠落、学習内容の不一致等がある場合、別のテストPASSや形式的問題による差戻しで相殺できない仕組みを検討する。

### 提案②：不適合成果物の提示制限

目的を満たしていない成果物を、完成品としてユーザーへ試聴・選定依頼することを防ぐ。

ただし、不完全な候補を比較すること自体が正式目的のTrialは区別する。

### 提案③：最終判定の矛盾検出

受入記録の詳細では重大NGなのに、総合判定ではACCEPTEDとなるなどの矛盾を、Validator・構造化判定・独立レビュー等で防ぐ方式を比較する。

### 提案④：ユーザー判断Gateの適正化

必ず以下を区別する。

- ユーザー承認済みで実施すべき事項
- 承認範囲内で技術的に自己解決可能な事項
- 新たに発見された独立問題
- 本当にユーザー判断が必要な事項

承認済み事項を再びUSER_DECISION_REQUIREDに戻さない。

独立問題はOpen Itemに分離し、重大な依存・阻害関係がない限り、本タスクを不要に停止させない。

## C-3. Fable／Opusに求める検討

以下を比較評価する。

- 現行Prompt／運用規則の改善だけで足りるか
- 構造化した受入判定が必要か
- Validator等の機械的な矛盾チェックが必要か
- Fable自身による独立判断とOpusレビューの適切な役割分担
- 誤STOP・過剰なUSER_DECISION_REQUIREDのリスク
- 実装・運用コスト
- 他Family／案件への再利用性
- 既存Governanceとの重複・競合
- 再発防止効果

Fableは単にOpusの提案を転記するのではなく、自分自身の推奨案・理由・代替案・QDC評価を示す。

## C-4. 今回のSTOP条件

本指示では、新規の大規模改修・追加盲検・Day 5〜6開始は承認していない。

改善案の比較と推奨がまとまった段階でSTOPし、ユーザーへ提示する。

新しい運用仕様を独自にProduction採用してはならない。

---

# D. 横断的なPM運用ルール

今回のA・B作業とCの検討では、以下を徹底する。

1. **正式承認済みの仕様は実装して完了させる。** Trialで止めない。
2. USER_DECISION_REQUIREDは、真に新しいユーザー判断が必要な場合だけ発行する。
3. 技術的な原因調査・是正方法の選定は原則Claude／Fableが担う。
4. 別問題の発見時は、重要度・依存関係・Production影響を確認し、Open Itemへ分離する。
5. 未承認の新仕様をProductionへ反映しない。
6. 既存のHuman Review Lock・費用上限・STOP指示を尊重する。
7. 実装後は、技術的テストだけでなく、ユーザー目的との一致を検証する。
8. retry／fallback／regeneration等の後続経路まで整合する。
9. 重大品質NGを検出した成果物を、無条件にACCEPTEDとしない。
10. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／USER_DECISION_REGISTERを実態に合わせて更新する。

既存の関連Open Item・承認済み未配線事項を確認し、作業範囲外のものは明示して引き継ぐ。

**最終報告では、A・B・Cそれぞれについて「達成・未達・理由・証拠・残る判断事項」を独立して示すこと。**

AとBはProduction実装・実証まで、Cは改善方針の検討までが今回の承認範囲である。

A・Bを無条件に完了扱いせず、Cの改善案をユーザー判断なしにProduction採用しない。
