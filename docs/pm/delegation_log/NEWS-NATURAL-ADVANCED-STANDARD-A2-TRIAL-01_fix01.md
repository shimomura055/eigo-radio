## 管理ID
`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`(修正1回目: REPORT §12〜§14の`[Fable記入]`置換のみ)。並行タスクなし。一時ファイル標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はcommitに含めない。

## 性質/禁止
Trial記録の追記のみ。Production/SSOT変更・API支出・記事再生成・他セクション変更禁止。`git add -A`/`stash`/`amend`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## 作業
`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01_REPORT.md`の §12/§13/§14 の各`[Fable記入]`(Grep `\[Fable記入\]`で位置確認、3箇所)を以下で置換。§15にはFable追記ブロックを末尾追加(既存行は変更しない)。

§12:
```
### 12.1 Story構造(両記事とも維持 ○)
下水道9段落・Meta 11段落が1:1対応し、Reveal・中心比喩・Endingは同一位置。要約化・順序変更・見立て削除はなし。仮説の「not the story」側は成立。

### 12.2 簡略化の度合い(不十分 ×)
- Meta: Advanced→Standardの差分は約10箇所の語句置換(convenient→useful / on a person's behalf→for a person / fill in→do / 1文分割)にとどまる。ユーザー指示で簡略化例として示された文「If people learned that contract workers had actually listened and responded to a conversation they thought they had left to AI, it would not be surprising if they were shocked.」は、ほぼそのまま(30語の条件節+過去完了)残っている。指標: 平均文長13.2→12.5語、FK 6.7→6.3。
- 下水道: 差分はさらに小さく(aging→old、large-scale→very large、"municipalities, or town governments"の語注追加、1文分割)、平均文長13.6→13.5語。
- 「Standardは明確に易しくなったか」「A2として理解しやすいか」の観点で、Advancedとの差が聴取者に分かる水準に達していない。

### 12.3 個別観察
- Meta "The lead role was Muse"→"The main part was Muse": 舞台の見立て(主役)の語が弱くなった唯一の負の変更。
- 下水道 "Some municipalities, or town governments": 語注はAdvancedにない説明の追加に当たる(軽微、Fact追加ではない)。
- Fact drift: 数字・固有名詞・否定・範囲語すべて維持。「通話の一部」はAdvanced Baselineの"some parts of the calls"がそのまま維持(解釈固定なし)。Ledger MUSE-006は「一部の電話依頼を人間へ引き渡した」(=一部の通話全体)の読みを示しており、Advanced側の表現とのズレはBaseline由来(本Trial外、Open Item)。

### 12.4 下水道Advanced(A-1)の参考評価
日本語R2の構成(「合併」の勘違い→家庭排水→大動脈→老朽化→浄化槽→洗濯機の比喩→留保→身近な未来)を忠実に保持し、B1相当の自然な英語。ADAPTATION-TRIAL-01のNatural方式が2記事目でも再現した(Adaptation方式の再現性を支持)。

### 12.5 原因仮説(事実からの推定)
(i) AdvancedがすでにFK 7前後・平均13語/文と平易で、モデルが「軽い校正」として処理した。(ii) Prompt内の"Preserve…/Keep every fact exactly/Do not write a flat list of short sentences"の制約が最小編集へ偏らせた。(iii) A2の具体目標(文長・語彙帯・許容される書き換え例)がPromptに無い。
```

§13:
```
**Standard A2: REJECTED(Standard共通Prompt v1)**。理由: Story構造は維持されたが、簡略化が「明確に易しい」水準に達していない(§12.2)。記事自体は不良ではないが、2段階レベルとして成立していない。
Advanced Natural: `APPROVED_FOR_PRODUCTION`のまま維持(下水道A-1で再現性を確認)。Production正式path・retry/fallback・runtime evidence・SSOT記録が未完のため`PRODUCTION_WIRED`ではない。
```

§14:
```
1. Standard Prompt v2 Trialの承認(追加Variationは本Trialでは禁止のため未実施)。Fable案: (a) 具体目標を明記(平均9〜11語/文、1文1メッセージ、最頻出約2,000語を基本とし必要な専門語[septic tank等]は残す)、(b)「語句の置換ではなく全文を書き直す」と明示、(c) ユーザー指示の簡略化例1件をPrompt内に例示、(d) "may be a little longer or shorter"を削除、(e) 中心比喩の語(lead role等)は平易なら保持と明記。対象は同じ2記事、¥1以内。
2. Advanced Natural(arm3)の`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`をDECISION_LOG/CURRENT_SPECへ記録するか(現在未記録)。
3. 「通話の一部」: Advanced Baselineの"some parts of the calls"とLedger MUSE-006の読み(一部の通話全体)のズレを、Baseline修正で解消するか/Reuters原文確認まで保留するか。
```

§15 末尾に追記:
```
### Fable追記
- Standard v1 Promptは簡略化不足(§12.2)。v2はユーザー承認待ち。
- Advanced Baseline(Meta)の"some parts of the calls"とLedgerの読みのズレ(Baseline由来)。
- 下水道Standardの語注追加("or town governments")は説明追加の境界例。
- CEFR推定手段が未導入(機械指標は文長・FKのみ)。
```

## Git
明示add: `NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01_fix01.md`、同`_check.json`。
メッセージ: `NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01: REPORT §12-14 Fable参考評価(Story維持○/簡略化不足×)・Standard v1 REJECTED・USER_DECISION_REQUIRED記入`
trailer: `Management-ID: NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. 置換箇所と`git diff --stat`(対象1ファイルのみ) 2. commit SHA・push 3. 一覧外Read理由。
