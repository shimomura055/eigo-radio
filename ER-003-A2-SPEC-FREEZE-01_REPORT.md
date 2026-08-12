# ER-003-A2-SPEC-FREEZE-01 実行報告(A2仕様固定 + Cross-level横展開整理)

**管理ID: ER-003-A2-SPEC-FREEZE-01**
**実施日: 2026-08-12**
**ステータス: `SPEC FREEZE COMPLETE`(仕様固定・文書整理のみ。新規音声生成・再assemble・pushは実施していない)**

## 1. 何をDECIDEDへ昇格したか

[CURRENT_SPEC.md](CURRENT_SPEC.md)の「CEFR(A2/B1/B2比較)」表を全項目
`TBD`から`DECIDED`へ更新し、新規節「CEFR-A2 構造・音声仕様」を追加した。

- A2言語方針: Natural English Source独立生成、総語数を削らない、
  平均文長11語以下・最長18語以下、1文1メッセージ、SVO中心・関係詞節/
  分詞構文/複雑な受動態を避ける、Spoken-first、Simple AND Natural要件
- A2構造: 11パート構造、Comment1〜4の役割、Full Story分割優先順位
  (①意味上の転換点②時系列③問題→例外④発表→反応⑤What happened→Why it matters)、
  In One Line=中心1文+補足2文
- A2音声速度: 約135 WPMを目安として採用(hard constraintではない、
  B1/B2は現状維持)
- Naturalness QAフロー: 生成と独立したQA(6観点、PASS/REVISE/HUMAN_REVIEW)

## 2. Cross-levelへ何を横展開したか

新規節「Cross-level仕様(A2/B1/B2共通)」を追加し、以下をA2固有ではなく
番組全体の仕様として正式化した。

- Preview原則(具体的答え・数字・結論の先出しをしない)
- Key Phrase発音品質3条件(Meaning/contextual prosody・Phoneme integrity・Phrase grouping)
- 英語見出しのTTS方式(見出しテキストを実際にinputへ含める)
- ポーズ(ポイント解説後0.7秒、Point One→Two・In One Line→Outro 0.8秒)
- Outro音量(心理音響ベースの段階的減衰)

いずれも既存B1/B2完成音声は今回遡って再生成していない。今後の新規
生成・再assemble時から適用する。

## 3. 何をREJECTEDのまま維持したか

以下は過去の検証で不採用と確定済みであり、今回も再導入しない
([CURRENT_SPEC.md](CURRENT_SPEC.md) CEFR表・[DECISION_LOG.md](DECISION_LOG.md)に理由とともに記録済み)。

- A2超一般語 最大5語の数値制限
- 抽象語→具体的行動表現への一律変換
- 固有名詞密度低減の数値目標
- 1文1新情報(1文1メッセージより厳格なルール)
- 重要語の機械的反復
- 使用文型の限定
- B1情報量の70〜80%への削減

## 4. 何がまだOPENか

[OPEN_ITEMS.md](OPEN_ITEMS.md)に2件を残した。

- **OPEN-31**: A2英文のnaturalness。A01の"added more time"→"added
  time"修正はDECISION_LOGで方針確定済みだが、台本への反映(および
  他記事の残りのSHOULD_REVISE候補4件の判断)はまだ
- **OPEN-34**(新規): A01・ADD03の完成音声が、今回DECIDEDへ昇格した
  Cross-level最新仕様(Pause 0.8秒・Outro最新減衰・Key Phrase 3条件
  発音・In One Line見出し修正・約135 WPM)をまだ反映していない
  (ER-003-CROSSLEVEL-AUDIO-02時点のバージョンのまま)。次回のA01/ADD03
  assemble時に反映する

その他、Cross-levelとは無関係の既存の技術的負債(CI manifest未登録
ファイル=OPEN-27、Canonicalizationグロスのナレーション不安定パターン=
OPEN-28等)は今回のスコープ外のため変更していない。

## 5. Source of Truth更新一覧

| ファイル | 変更内容 |
|---|---|
| [CURRENT_SPEC.md](CURRENT_SPEC.md) | CEFR表のA2列を全面更新、新規節「CEFR-A2 構造・音声仕様」「Cross-level仕様(A2/B1/B2共通)」を追加 |
| [DECISION_LOG.md](DECISION_LOG.md) | 今回の8件の決定(A2言語・構造仕様昇格、速度135WPM、Preview原則、Key Phrase3条件、英語見出しTTS方式、Pause、Outro、A01 added time修正)を追加 |
| [OPEN_ITEMS.md](OPEN_ITEMS.md) | 解決済み項目(OPEN-01/02/13/16/21/23〜26/29/30/32/33)をDECIDED/CLOSEDへ整理。新規OPEN-34を追加。残るOPENはOPEN-31・OPEN-34のみ(Cross-level関連) |
| [A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md) | ステータスを`PROTOTYPE`→`HISTORICAL`へ変更、CURRENT_SPECへの移管を明記。検証履歴としては保持(削除しない) |
| [PROJECT_INDEX.md](PROJECT_INDEX.md) | A2/Cross-level仕様の参照先をCURRENT_SPEC.mdへ更新 |
| [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) | A01/A02/ADD03のCEFR-A2行を最新化。A02は全列PASS(ER-003-A2-AUDIO-AB-01でユーザー承認)、A01/ADD03は「再assemble要」を明記 |

## 6. 即答可能性20問の結果

Git history・handoff・個別reportを検索せず、CURRENT_SPEC/DECISION_LOG/
OPEN_ITEMS/ARTIFACT_REGISTRY/PROJECT_INDEXのみで全問回答可能なことを
確認した。

| # | 質問 | 回答 | 参照元 |
|---|---|---|---|
| 1 | A2平均文長上限は？ | 11語以下 | CURRENT_SPEC |
| 2 | A2最長文は？ | 18語以下 | CURRENT_SPEC |
| 3 | A2の音声速度目安は？ | 約135 WPM(目安、hard constraintではない) | CURRENT_SPEC |
| 4 | A2 Full Storyは何分割？ | 原則2ブロック | CURRENT_SPEC |
| 5 | A2 Commentは何個・役割は？ | 4個。Listening Focus/Mid-story Recovery+Next Question/Story Meaning+Bridge to Points/Point Recovery+Bridge to In One Line | CURRENT_SPEC |
| 6 | A2 In One Lineは何文構成？ | 中心1文+補足2文程度 | CURRENT_SPEC |
| 7 | A2のPreviewの役割は？ | テーマ・問題意識・聞く価値・問いを示す。答えの先出しはしない | CURRENT_SPEC |
| 8 | A2で不採用の簡略化ルールは？ | 超一般語5語制限・抽象語一律変換・固有名詞密度低減・1文1新情報・重要語反復・使用文型限定・情報量70-80%削減 | CURRENT_SPEC、DECISION_LOG |
| 9 | Key Phrase発音品質の3条件は？ | Meaning/contextual prosody・Phoneme integrity・Phrase grouping | CURRENT_SPEC |
| 10 | Point One→Point Twoのpauseは？ | 0.8秒 | CURRENT_SPEC |
| 11 | In One Line→Outroのpauseは？ | 0.8秒 | CURRENT_SPEC |
| 12 | A2 Comment前後のpauseは？ | 英→日1.0秒、日→英0.8秒 | CURRENT_SPEC |
| 13 | B1/B2の速度は変更したか？ | 変更なし、現状維持 | CURRENT_SPEC |
| 14 | Outro音量方針はA2固有かCross-levelか？ | Cross-level(A2/B1/B2共通) | CURRENT_SPEC |
| 15 | Naturalness QAは今後どう入る？ | 生成→独立QA(6観点)→修正→re-QA、PASS/REVISE/HUMAN_REVIEW | CURRENT_SPEC |
| 16 | In One Lineは読み上げるか？ | 読み上げる(見出しテキストを実際にTTS inputへ含める) | CURRENT_SPEC |
| 17 | A2 Key PhraseはB1から流用するか？ | 流用しない、A2本文から改めて選定 | CURRENT_SPEC |
| 18 | A01のadded more timeはどうするか？ | "The game went into added time."へ修正方針確定、台本反映は未実施 | DECISION_LOG、OPEN_ITEMS(OPEN-31) |
| 19 | A2で未解決の項目は？ | OPEN-31(script naturalness残り)、OPEN-34(A01/ADD03再assemble) | OPEN_ITEMS |
| 20 | A2の現在仕様の一次参照先は？ | CURRENT_SPEC.md | PROJECT_INDEX |

**20問全PASS。**

## 7. 今回行っていないこと

- B1/B2既存完成音声の一括再生成
- A01/A02/ADD03の完成音声再assemble
- 新規音声生成
- 新しい仕様検証
- push

## Git / push

コード変更なし、ドキュメントのみ変更してcommit済み。**pushは実行していません。**
