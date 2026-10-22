# ASR包括対策 er109 v1 — 正式Production採用・Wiring指示

## 1. ユーザー正式決定

英語ASRの同一発音・異表記包括対策について、以下2項目を正式採用します。

**Status:APPROVED_FOR_PRODUCTION**

**対象Family:X / Zのみ。**

### ① 包括対策 er109 v1 — 正式採用

既存の数値・同音救済を維持し、今回VALIDATEDとなった追加救済範囲をProductionに採用する。

主な対象:

- `one ↔ 1`:既存で救済できていた経路は維持し、Key Phrase等の未対応経路へ拡張。
- `one's ↔ 1's`:新たに救済。
- `twenty percent ↔ 20%`:既存の救済を維持。重複実装しない。
- 短縮形、同音語、数字表記、スペース差など、er109 v1で検証済みの追加対象。

適用範囲は、**Family X/Zの英語ASR全体**とする。Key Phrase限定ではない。

OpenAI Primary、Azure Secondary、Whisper票、本文・Key Phrase・英語解説、Store再利用・retry・fallback・regeneration・resumeを含む正式経路で、承認済みの判定仕様と整合させること。

安全条件:

- 発音が異なる表現を同値にしない。
- 曖昧略語・同形異音語・危険なoronymは、承認済みの非同値判定を維持。
- 強勢・代表発音の判定はOpus是正後のv1を使用。
- 数値差・否定差の最終保護は全面解除せず、er109が同音と証明した箇所のみ解除する。
- 既存の本当の発音NGを誤PASSにしない。

### ② 否定語 `no ↔ know` — 正式採用

`no` と `know` の発音が一致する場合、表記差だけでNGにしない。

- `PASS_WITH_WARNING` として合格。
- 警告内容・根拠を内部記録。
- 事後試聴の対象として追跡可能にする。
- `can't/can`、`don't/do` など発音が異なるものは救済しない。

対象は①と同じく、Family X/Zの英語ASR全体。

決定的な数値・記号等の表記差は警告不要とし、Opusレビュー済みの警告方針を維持する。

## 2. ③ 開発対象Familyの厳守【重要】

**Family A/B/Cは開発停止中であり、今回の対象に含めない。**

この方針はすでに `docs/pm/PM_GOVERNANCE.md` §27-3に記録済み(2026-10-16ユーザー決定)。

Claude・Fableの双方で再確認し、遵守すること。

- A/B/Cの追加開発・コード修正・Trial・検証run・再生成・独立調査は行わない。
- 共通Validatorを使っていることを理由に、適用Familyを拡張しない。
- 共通コード変更で対象外Familyに挙動の変化が生じないよう、互換性と適用範囲を確保する。
- もし既存構造上、対象外Familyへの変更を避けられない場合は、その変更を実施せずSTOPし、理由と代替案を報告する。
- 対象外Familyへの展開を追加提案・ユーザー判断項目として提示しない。

今回のWiringでは、**X/Zだけに有効化できる構成**を必須とする。

既存の記録が不明瞭であればSSOTを補強する。ただし、新しい調査タスクを不要に増やさない。

## 3. Production Wiring

TrialでVALIDATEDとなったer109 v1を、正式Production経路に配線する。

既存コード・承認済み仕様を再利用し、重複実装や不要な再Trialを避ける。

Opus must-fixのうち設計段階に残っている事項も実装・検証する。

特に以下を確認:

1. Family X/Zの正式初回Production経路。
2. Primary/Secondary/Whisper各票の判定。
3. 最終保護Gateとの整合。
4. retry / fallback / regeneration / resume。
5. Store再利用と既存音声の判定。
6. 既存のKey Phrase多数決仕様との整合。
7. 誤PASSの防止、NG→PASSの改善。
8. 警告付きPASSの内部記録・事後試聴対象管理。
9. 対象Family以外でer109が有効化されないこと。

既存のASR判定条件や品質基準を、本承認範囲外で変更しないこと。

## 4. 検証・受入条件

**X/ZそれぞれでPRODUCTION_WIREDまで到達すること。**

必要な証拠:

- 正式Production経路への配線確認。
- X/Zそれぞれのruntime evidence。
- `one's ↔ 1's`、`no ↔ know` 等の新規救済ケースが期待どおり判定される証拠。
- 数値の実際の違い、否定脱落、異音語、同形異音語等が誤PASSしない証拠。
- 必須Regression / Validator / Integration test PASS。
- retry・fallback・Store・resumeでの判定一貫性。
- actual routing、flag、判定basis、警告記録の証拠。
- 既存Production仕様との整合。
- Dangling Referenceなし。
- CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS更新。
- Git commit・push完了。
- Fable独立受入。

自然発火を得るためだけに不必要な記事生成を繰り返さない。正式runtime経路の実行証拠と、該当ケースの決定的な検証を組み合わせ、必要十分な品質で完了させること。

**単なるコード配線や単体テストPASSだけではPRODUCTION_WIREDとしない。**

## 5. QCD・実行方針

優先順位は **品質 > 完了速度 > 量産単価**。

- 承認済みのer109 v1を利用し、探索Trialをやり直さない。
- 独立作業は並列化し、不要な待機・日付分割をしない。
- 追加API費用は最小限に抑える。
- Wiring費用見込み40円以内を基本とする。
- 承認済み範囲内の不具合は、自律的に原因究明・修正・検証する。
- 新しい仕様変更、品質基準変更、重大な安全リスク、承認範囲外の変更が必要な場合のみSTOPして判断を求める。

## 6. 最終報告

①②についてFamily X/Z別に、APPROVED_FOR_PRODUCTIONからPRODUCTION_WIREDへの到達を報告すること。

実装内容の説明だけでなく、正式runtimeの動作証拠、テスト結果、既存仕様との整合、費用、SSOT/Git反映結果を提示する。

未確認事項を完了扱いにしない。

Fableによる独立受入まで完了し、残件がある場合はOPEN_ITEMSに明示する。

**今回の正式採用について、ユーザーへの再承認要求は不要。Production Wiring完了まで自律的に進めてください。**
