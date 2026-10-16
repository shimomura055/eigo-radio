2026-10-16 ユーザー指示原文(Fable受領、09:00 JST時点の最終ユーザー判断)

# Claude Code／Fableへの追加指示
## Family X 最終ユーザー判断のSSOT記録

**管理ID：FAMILY-X-20261016-0900-USER-DECISION-RECORD-01**

### 1. 目的

以下を**2026-10-16 09:00 JST時点の最終ユーザー判断**として正式記録する。

これはCoffeeを代表記事として、Family X全体のProduction仕様を確定するための判断であり、Coffee限定仕様ではない。

過去のTrial記録や旧決定と矛盾する場合は、承認の履歴を残しつつ、今回の判断を最新版として明確に管理する。

### 2. 正式採用仕様

| 対象 | 最終ユーザー判断 |
|---|---|
| B3・日本語Writer R0→R1→R2 | すべて `gpt-6.1-sol`。既存`PRODUCTION_WIRED`を維持 |
| Full Story TTS（Std／Adv） | **PD06** |
| Key Phrase英語音声（Std／Adv） | **K2** |
| Key Phrase日本語意味（Std） | **P8**。旧M2を置換 |
| Key Phrase英語解説（Adv） | **P7**。旧P3を置換 |
| KP候補供給 | **M2P0** |
| KP選定優先順位 | **A方式（現行）を正式採用**。B／C方式は不採用 |
| In One Line（Std／Adv） | **基本2文、必要な場合のみ3文**。旧1文Promptを改修する |

これらは採用判断済みであり、再度ユーザーへ採否を求めない。

### 3. 適用範囲

- 対象Family：**Family X全体**
- 代表検証記事：Coffee
- Coffeeはテーマのみ維持し、**Researchから音声完成まで全面新規生成**
- 旧Coffee記事の原稿・KP・音声を完成品として流用する前提にはしない
- Family Zなど他Familyへの自動展開は対象外

### 4. Status管理

- 既にWired済みのB3→R2 Sol統一：`PRODUCTION_WIRED`を維持。ただし実装・runtime証拠との整合を監査する。
- 新規採用・変更した仕様：`APPROVED_FOR_PRODUCTION`。
- `PRODUCTION_WIRED`への変更は、正式初回経路・retry／fallback／regeneration・runtime evidence・test・SSOT・Git反映の全項目を確認した後のみ。
- 旧仕様は履歴として保持し、現行仕様と取り違えないようにする。

### 5. SSOT更新

以下を更新する。

1. `CURRENT_SPEC.md`：Family Xの最新承認仕様、適用範囲、Status。
2. `DECISION_LOG.md`：2026-10-16 09:00 JSTのユーザー判断として逐語的に追跡可能な形で記録。
3. `OPEN_ITEMS.md`：対応する既存Open Itemを今回の判断に合わせて更新。ただしProduction未配線項目はcloseしない。
4. ユーザー判断台帳：判断済みと未配線状態を区別。
5. 必要な監査・委任記録：次のWriter監査およびCoffee制作の前提資料として参照できるようにする。

**既存の正式仕様・今回の採用判断・Trial候補を混同しないこと。**

PD06・K2・P8・P7のPrompt文字列は、必ず元Trialの正本と照合する。推測で補完・改変しない。

### 6. 監査との関係

先に依頼したFamily X Writer採用漏れ・Production反映漏れ監査では、**本決定記録を最新の承認基準**として扱う。

今回のSSOT記録だけで、未実装仕様を`PRODUCTION_WIRED`と判定してはならない。

また、監査中に発見した未承認の良好なTrial成果は、ユーザー判断事項として別途提示すること。

### 7. 今回の作業範囲とSTOP条件

今回は**記録・管理状態の更新のみ**実施する。

- Productionコード・Promptの変更は禁止。
- 新規Trial・有料API呼出は禁止。
- Coffeeの再生成は開始しない。
- 既存Open Itemを単に記録済みという理由でcloseしない。
- 更新後、変更ファイル・commit hash・push結果を報告する。

記録完了後はSTOPし、先行するFamily X Writer監査の結果と合わせて、Production Wiringへ進む前の未解決事項を整理すること。

(ユーザー指示原文ここまで)
