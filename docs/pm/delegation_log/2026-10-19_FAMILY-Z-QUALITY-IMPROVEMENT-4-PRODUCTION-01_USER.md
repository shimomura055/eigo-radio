# Claude Code／Fableへの指示
## Family Z 品質改善4項目・Production反映

### 1. 目的と基本方針

「走れメロス」のユーザー試聴で明らかになった課題を改善し、Family Zの正式Production仕様へ反映する。

**今回の4項目はユーザー正式決定済み。Status＝APPROVED_FOR_PRODUCTION。**

品質（Q）＞Delivery（D）＞量産単価（C）≫開発費用の優先順位と、改訂済み行動大原則8項目を遵守する。

既存仕様・過去Trial・Production実経路を確認し、必要な変更だけを実施する。独立作業は並列化し、問題は承認範囲内で自律解決する。不要な再生成・追加Trial・日付分割・少額費用の都度承認は行わない。

### 2. 改善項目

#### ① Key Phrase日本語訳の恒久改善

**目的は「in someone's place」の個別修正ではなく、同種の誤訳を量産時に発生させないことである。**

今回、`in someone's place` に対し「あなたの代わりに」という日本語訳が生成された。英語表現に存在しない二人称を補った不適切な訳である。

対応内容：

- 既存のKey Phrase選定、canonicalization、日本語意味生成、検査・retryの経路を調査し、誤訳を生んだ原因と既存対策の不足を特定する。
- 英語Key Phraseと日本語意味の間で、人称・所有格・指示対象・意味関係が不当に変わらないよう、**記事や特定表現に依存しない共通仕様**として改善する。
- `someone's` → `your` のような指示対象の変更だけでなく、文脈による「立場／代わり」などの意味選択も適切に扱う。
- 機械的な逐語訳を強制せず、自然な日本語と原文の意味の両方を守る。
- Family X／Z／将来のYで共通化すべき仕様かを判断し、既存の承認済み共通仕様と整合させる。
- 改善したProduction経路を使用して、今回のメロスの該当Key Phraseを再処理し、正しい日本語意味に修正されることを確認する。
- 同種の誤訳を使ったRegressionを実施する。特定表現だけを置換するhardcodeは不可。

**受入条件：仕様自体が改善され、その正式経路からメロスの正しい日本語訳が生成されること。手動修正のみでは未達。**

なお、新たな品質基準・生成方式を承認済み範囲を超えて導入する必要が生じる場合は、候補を検証した上でUSER_DECISION_REQUIREDとして報告し、未承認のままProductionに採用しない。

#### ② Standard Preview／Comment生成方式の変更

**Advancedで採用しているPreview／Comment生成方式を、日本語版としてStandardに適用する。**

目的は、事前に物語の展開を説明することではなく、リスナーが何に注目して聴けばよいかを示し、続きへの興味を引き出すこと。

対応内容：

- Advancedの正式Production Prompt・生成経路を確認する。
- その構成・役割・情報開示方針をStandardの日本語生成へ適用する。
- 本文中の出来事・障害・結末を不必要に先取りしない。
- Standardとして理解に必要な平易さは維持するが、旧方式の詳細なあらすじ説明を無条件に残さない。
- PreviewとComment1〜3の重複や情報の先取りを確認する。
- 新仕様をFamily Zの正式生成経路、retry／regenerationへ反映する。

既存Advanced方式の日本語適用がユーザー承認範囲であり、別の独自方式への変更は含まれない。

#### ③ Standard Dialogue音声速度の改善

**Standardの登場人物のセリフは、Advancedと同じDialogue Styleで生成し、生成後に6％減速する。**

現行Standardの「生成時の減速指示＋生成後6％減速」は廃止する。

対応内容：

- `A2_ENGLISH_STYLE_PREFIX_SLOWER` 等、Dialogueに追加されている生成時減速指示を取り除く。
- Advancedと同一のDialogue Styleを使用する。既存の登場人物別Voice割当は維持する。
- Standardの生成後6％減速、既存ASR／音声QA／retry／fallbackは維持する。
- narratorのPD06や、Standard本文ナレーションの6％減速仕様は変更しない。
- 問題が顕著だった王のセリフを含め、変更後の速度・自然さと6％減速の実施を検証する。

対象例：

`Your friend must stay here. Return late, and he will die in your place.`

セリフの速度改善のために、ユーザー未承認の数値WPM基準や追加品質Gateを新設しない。

#### ④ Family Z本文語数の変更

**Family Zの本文語数目標を350語から400語へ変更する。**

- Standard／Advanced共通
- **目標400語、目安範囲330〜470語（400±70）**
- 従来の「センター値±70語」をそのまま踏襲
- ハードキャップではない
- 範囲外はWARNのみ
- 語数だけを理由とした自動再生成・STOPは行わない
- 不自然な加筆・削除による語数合わせは禁止

Writer Prompt、定数、Guardrail、文書、必要なテストを整合させる。

今回のメロスは既存本文がStandard約408語／Advanced約387語で新しい目安範囲内にあるため、**語数変更のみを理由とした本文再生成は不要**。

### 3. 実施順序と効率化

①②④の仕様調査・修正・テストは、依存関係と競合を考慮して可能な限り並列化する。

③の音声修正は、必要な本文・話者割当が確定していれば先行可能。

既存の承認済み成果物・音声は再利用し、変更が必要なPreview／Comment、該当Key Phrase日本語意味、Standard Dialogueのみを必要に応じて再生成する。

ただし、最終Assemblyは変更後の正式仕様と原稿の整合が取れた状態で行う。

開発費は原則1,000円／日（JST）と既存個別Capの双方を管理する。承認済み範囲内の少額Trial・修正のたびにユーザー承認を求めない。個別Cap超過、新規Trial範囲、重大な仕様変更は承認境界を遵守する。

### 4. Production反映とGate

各変更について以下を確認する。

- 正式初回Production経路に反映済み
- retry／fallback／regeneration／resumeへの反映
- DEV／Trial専用の変更ではない
- 正式runtimeで変更が発火した証拠
- 必須Validator／Regression／integration test PASS
- 実際のPrompt、Style、Voice、model_id、routingの記録
- Family X／Z共通仕様との整合、および各Familyの配線確認
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- Git commit／push完了
- 承認された仕様と実動作が一致

各項目は個別にStatus管理し、条件を満たしたものだけをPRODUCTION_WIREDとする。

特に①について、改善仕様の実装範囲がFamily Zのみにとどまる場合は、Family Xの未配線を見落とさずOPEN_ITEMSに記録する。

### 5. 完成物・ユーザー試聴

「走れメロス」のStandard／Advancedについて、変更箇所を反映した完成音声と既存標準フォーマットの試聴ページを更新する。

- 全編再生
- 再生順の全スクリプト
- Preview／Comment／Dialogue
- Key Phrasesと日本語意味
- 既存のユーザー向け表示仕様

変更対象外のAdvanced音声・既存本文などは可能な限り再利用する。

**最終的な音声の自然さ・Previewの良し悪しはユーザー試聴で判断する。** Production技術検証PASSとユーザー試聴PASSを混同しない。

### 6. Fable独立受入・最終報告

FableはClaudeの完了宣言をそのまま受け入れず、4項目について独立して承認内容・実装・runtime evidence・テスト・QCD・SSOTを照合する。

最終報告は次の順序で簡潔にまとめる。

1. 4項目それぞれのStatusと完了／未完了
2. ①誤訳の根本原因、変更した共通仕様、再発防止テスト、メロスへの適用結果
3. ②Preview／Commentの修正前後
4. ③DialogueのStyle・速度・実測結果
5. ④400±70語への仕様変更・実装確認
6. 実費・量産単価への影響・所要時間
7. Git／SSOT／runtime evidence
8. Standard／Advanced試聴ページURLと残るユーザー判断

既存の明示STOP、安全STOP、予算上限、未承認Production仕様の採用禁止を遵守する。

**目標は4件を個別に直すことではなく、承認された品質が以後のFamily Z量産でも再現される正式Production仕様にすることである。**
