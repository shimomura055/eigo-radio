# ユーザー原文(逐語) KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 (2026-10-22、委任_01 §9から見出し〜末尾を逐語保存。Status=APPROVED_FOR_PRODUCTION)

# Claude Code／Fableへの指示
## Family X／Z共通 — Key Phrase品質改善2項目 Production Wiring

### 1. 目的・承認Status

以下2項目はユーザーが正式採用を承認済み。

**Status：APPROVED_FOR_PRODUCTION**

Family X／Zの両方について、現行Production経路への実装・検証・SSOT/Git反映を完了し、**PRODUCTION_WIRED**まで進めてください。

新たな採用判断や追加Trialの承認は不要です。

### 2. 変更① Key Phrase音声の数値・否定保護を解除

**対象：Family X／Z共通**

Key Phrase英語音声に対して、既存の「数値・否定の不一致を多数決より優先してNGにする保護機能」を解除してください。

承認済みの3-ASR判定ルールを例外なく適用します。

| OpenAI（Primary） | Azure（Secondary） | 最終処理 |
|---|---|---|
| PASS | PASS | PASS |
| PASS | NG | Whisperを実行し、多数決 |
| NG | PASS | Whisperを実行し、多数決 |
| NG | NG | NG |

- Whisperは3番目の判定者として使用。
- 2/3がPASSなら最終PASS。
- Key Phrase英語音声以外は、既存の数値・否定保護を維持。
- TTS・ASRモデルやVoiceの変更は不要。

**今回の確認済み事実：**

ユーザーは `pump one's fist` の対象音声を試聴し、正しい発音であることを確認済み。

Azureの `one's → 1's` という表記整形が数値保護に引っかかり、Whisperが実行されずHuman Reviewになった。

これは正常音声の不要なNGと判明しているため、同様の停止を防止すること。

### 3. 変更② CMU発音辞書への登録をKey Phrase選定の必須条件にする

**対象：Family X／Z共通**

Key Phraseの選定に以下を追加します。

**CMU発音辞書に登録されていない単語を含むKey Phraseは選定不可。**

実現方法はClaude／Fableに委任します。

ただし、次の要件を満たすこと。

- Key Phrase全体ではなく、構成する英単語ごとにCMU登録有無を確認する。
- 大文字・小文字や句読点等によって登録語が誤って除外されないようにする。
- 未登録単語がある候補は、選定時点で除外し、既存選定基準に基づき別候補を選ぶ。
- CMU辞書に登録されていない語を、LLMの推測や外部辞書の発音で代替して合格扱いしない。
- CMU登録条件を満たす候補が不足する場合は、既存の候補不足・例外処理との整合を確認する。条件を緩和して無理に5件を埋めない。
- 既存の選定品質基準、本文中に存在する表現を選ぶ条件、レベル別基準を維持する。

**選定段階で未登録語を確実に防ぐことが重要です。**

生成後の検査だけでなく、必要なら候補の再選定まで自動化してください。

### 4. 実装範囲と共通仕様の整合

両変更ともFamily X／Z共通仕様。

以下を確認し、必要な場所へ反映してください。

- 正式初回Production経路
- Key Phrase選定・検証・再選定
- TTS／ASR判定
- retry／fallback／regeneration／resume
- 保存済みデータの再利用時の適合性
- Validatorおよび既存テスト
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS
- Git commit／push

DEV／Trial専用経路への実装だけでは完了としない。

旧仕様の不要な分岐・検査は整理し、Dangling Referenceを残さないこと。

既存の完成記事や保存音声について、今回の変更だけを理由とする一括再生成は不要です。

### 5. テスト・Production Wiring Gate

最低限、以下を検証すること。

**変更①**

- Key Phraseで片側PASSの場合、数値・否定差があってもWhisperが呼ばれる。
- Whisperを含む2/3 PASSで最終PASSになる。
- 両NGの場合は従来どおりNG。
- Key Phrase以外では既存の保護機能が維持される。
- Family X／Z双方で正常動作する。

可能なら今回の保存音声を再利用し、`pump one's fist` の偽NGが回避されることを検証する。

**変更②**

- CMU未登録単語を含む候補が除外される。
- 登録済み単語だけで構成される候補は正常に選定できる。
- `minaudière` のような未登録語がKey Phraseに採用されない。
- 候補不足・再選定・retry経路でも制約が維持される。
- Family X／Z双方の正式経路で正常動作する。

**PRODUCTION_WIRED判定には、正式runtimeでの発火証拠、必須Regression／integration test PASS、両Familyへの配線、SSOT・Git反映が必要です。**

コード実装や単体テストだけでPRODUCTION_WIREDとは判定しないこと。

### 6. QCD・自律実行

優先順位：

**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 必要十分な品質に到達したら追加検証を増やさず完了する。
- 独立工程は原則並列化し、不要な待機・日付分割を行わない。
- 保存済み成果・既存テストを最大限再利用する。
- 量産単価70円／記事セットを目標に、追加API・再生成コストを最小化する。
- 承認済み範囲の不具合は自律的に原因究明・修正・再検証する。
- 既存予算・個別承認枠・STOP条件を守る。
- 新たな仕様変更が必要な場合のみユーザー判断に回す。

### 7. 最終報告

FableはClaudeの完了報告を独立検証したうえで、以下を簡潔に報告すること。

1. 変更①・②それぞれのFamily X／Z別Status（PRODUCTION_WIRED可否）
2. 正式Production runtime evidence
3. ASR多数決とCMU制約のテスト結果
4. retry／fallback等の整合確認
5. 既存記事・音声への影響
6. 実費と量産単価への影響
7. commit hash／push結果／SSOT反映
8. 未解決Open Itemとユーザー判断要否

**両Family・両項目ともPRODUCTION_WIREDを目指し、承認範囲内で一括完了させてください。**