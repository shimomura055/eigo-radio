# ユーザー指示原文(逐語、2026-10-29受領。人物紹介一般化方式B+E正式採用=APPROVED_FOR_PRODUCTION、Family Y Std/Adv、PRODUCTION_WIRED目標)

<<<USER>>>
# Claude Codeへの指示｜Family Y 人物紹介一般化方式（B+E）正式採用・Production Wiring

## 1. ユーザー正式決定

Family Yの人物紹介一般化方式 **B+E** を正式採用します。

- Status：**APPROVED_FOR_PRODUCTION**
- 対象：**Family Y Standard／Advancedの両レベル**
- 到達目標：**PRODUCTION_WIRED**
- 根拠：`FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01` の追加2記事Trial結果
- 追加Trial：不要

今回の3記事による検証結果を採用根拠とし、正式Production経路への実装を進めてください。

## 2. 採用するB+E方式

人物紹介は、**その人物が今回のテーマとどう関わっているか**を中心に構成してください。

ただし、職業・家族関係・社会的立場などの属性そのものがテーマに対する立場を明確に表している場合は、その具体的な属性を維持します。

### 承認済み原則

1. 人物像にリアリティがあり、紹介文が自然であること。
2. テーマとの関わり・経験・立場が伝わること。
3. 人物の主張と紹介内容が整合していること。
4. 属性の機械的な転記も、不必要な抽象化も避けること。
5. 人物像を自然にする合理的な補完を許容すること。

**情報源に明記されていない事実を追加したという理由だけで、一律NGにしないでください。**

一方で、明確な事実矛盾、不自然な創作、人物の立場や主張との不整合は防止してください。

「元情報にない時期語を含む」という形式的な理由だけでNGにする決定論検査は追加しません。

## 3. Trial結果との一致

以下の3類型を、実装・回帰検証の基準としてください。

| 類型 | 記事 | 期待動作 |
|---|---|---|
| 乖離型 | 夫が妻の姓を選ぶとき | 「父親」という属性より、妻の姓を選んだ経験を中心に紹介 |
| 一致型 | 再配達料 | 「宅配ドライバー」という具体的な職業を維持 |
| 中間型 | SNS年齢制限 | 属性とテーマへの関わり方を自然に組み合わせる |

Trialで不採用とした、属性を過度に抽象化するA方式へ戻さないでください。

採用するB+E方式のPrompt・判断原則・出力構成は、Trialの確定成果物を正本として使用してください。ChatGPTの本指示文から新たに別方式を設計し直す必要はありません。

## 4. Production実装

既存のCURRENT_SPEC、Trial成果物、Family Yの正式Production経路を確認した上で、以下を実施してください。

- 人物紹介生成PromptへB+E方式を反映。
- 紹介生成に「テーマとの接点」の情報を追加。
- 人物の役割・立場を扱う既存パターンを更新。
- Standard／Advancedの双方へ適用。
- 既存のPersona設計、Voice本文、事実確認、英訳工程との整合を維持。
- retry／fallback／regeneration／resumeでも承認済みB+E方式が適用されることを確認。
- 旧Prompt・旧処理との矛盾やDangling Referenceを解消。

既存の承認済み仕様を維持し、今回のB+E採用に必要な範囲だけを変更してください。

Family X／Zの人物紹介仕様には適用しません。

## 5. 品質検証・runtime evidence

### 必須Regression

Trialの3類型について、正式実装後も以下を確認してください。

- 姓記事：テーマとの関わりを優先し、不自然な「父親」紹介へ戻らない。
- 再配達記事：「宅配ドライバー」という重要な属性が維持される。
- SNS記事：属性とテーマへの関わりが適切に組み合わされる。
- 情報源の属性の機械的転記や過度な抽象化が再発しない。
- 合理的な補完を一律NGにしない。
- 明確な事実矛盾や人物設定の不整合は既存品質Gateで適切に扱う。

### 正式runtime確認

**Family Y Standard／Advancedの両レベルで、正式初回Production経路からB+E方式が発火した証拠を取得してください。**

Trial専用スクリプトでの動作や、Promptファイルの更新だけではPRODUCTION_WIREDとしません。

Trialで課題となった英訳の性別表現については、採用後の最初の正式記事で確認してください。

日本語の人物設定、英語の紹介文、本文中のPersonaが自然に整合していることを確認します。

性別表現の確認だけを目的とした追加記事制作や、不要なTTS再生成は行わないでください。

## 6. QCD・作業方針

優先順位は **品質 ＞ 完成速度 ＞ 量産単価** です。

- 既存のTrial成果物・原稿・検証データを最大限再利用する。
- 不要な追加Trial・モデル比較・全記事再生成を行わない。
- 独立作業は並列化し、完成までの時間を最小化する。
- 既存仕様・予算・STOP条件内の不具合は自律的に原因究明、修正、再検証する。
- Production実装に伴う追加費用と、量産時の増分費用を区別して記録する。
- 新たな品質基準や仕様変更を独断で追加しない。

承認済みの品質水準に達した時点で完了とし、それ以上の磨き込みは行わないでください。

## 7. Production Wiring Gate

以下をすべて満たした場合のみ、**PRODUCTION_WIRED**と判定してください。

1. ユーザー承認済みB+E仕様と実装内容の一致。
2. Family Y Standard／Advancedの正式初回Production経路への配線。
3. retry／fallback／regeneration／resumeとの整合。
4. 両レベルでの正式runtime発火証拠。
5. 必須Regression／Validator／integration test PASS。
6. 実際に使用されたmodel_id、Prompt、routing等の証拠。
7. 旧方式との不整合・Dangling Referenceの確認と必要な是正。
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新。
9. 必要なGit反映。
10. Fableによる独立受入評価PASS。

未確認の項目があれば、その内容と理由を明示してください。

## 8. 既存記事への影響

今回の一般化仕様は、今後のFamily Y制作へ適用します。

既存の完成記事・確定済みVoice・音声・学習項目を、今回の共通仕様変更だけを理由に再生成・差し替えないでください。

『夫が妻の姓を選ぶとき、それぞれの声』については、別途承認済みのV1紹介文修正・Leda採用・`take offense` 修正・End User向けページ制作と整合させてください。

既存の進行中タスクを重複実行せず、完成までのDeliveryを最小化してください。

## 9. 完了報告

以下の順番で、簡潔に報告してください。

1. 結論：Family Y Standard／AdvancedそれぞれのProduction Wiring Status。
2. B+E方式の正式実装内容と、Trialで検証した3類型との一致。
3. 両レベルのruntime evidence・実際のPrompt／model_id／routing。
4. 英訳の性別表現の確認結果。
5. 必須Regression・既存仕様への影響。
6. 費用・量産単価への影響。
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git反映状況。
8. Fable独立受入結果と残Open Item。

**最終目標：B+E方式をFamily Y Standard／Advancedの正式Production初回経路に組み込み、両レベルともPRODUCTION_WIREDまで完了すること。**

新たなユーザー判断が不要な範囲は、自律的に最後まで進めてください。
<<<END>>>
