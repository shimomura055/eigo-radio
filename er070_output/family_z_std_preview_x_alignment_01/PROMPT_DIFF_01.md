# PROMPT_DIFF_01 (Family X Std `PREVIEW_ROLE` -> Family Z Std Preview, Trial)

STOP判定(News⇔物語起因でない差分の数): **0** -> PASS(Trial実行可)

## 1. Family Xから置換した全差分(これで全て。他は逐語一致)

| # | Family X原文 | Family Z変更後 | 変更理由 | News⇔物語起因 |
|---|---|---|---|---|
| 1 | このエピソードのニュース本文(Preview・Key Phrasesに続いてMain Story・Points・<br>In One Line、英語)を聞きます。 | このエピソードの物語本文(Preview・Key Phrasesに続いてMain Story、英語)を聞きます。 | (a)「ニュース本文」->「物語本文」(対象がニュースでなく物語)。(b)「Points・In One Line」を削除: Family Z StdにはPoint One/Two・In One Lineが存在しない(CURRENT_SPEC 2026-10-12決定「In One Lineなし・Comment4なし」、Point構造なし)ため、そのまま残すと存在しない構成要素を指す虚偽の記述になる。 | Yes |
| 2 | 役割: このニュースの<br> | 役割: この物語の<br> | 対象が物語。 | Yes |
| 3 | problem(何が問題・論点か) | problem(主人公が直面する問題・対立は何か) | 「論点」はニュース固有概念。ユーザー指示の置換例(ニュースの論点->主人公が直面する問題・対立)に従う。 | Yes |
| 4 | 記事の内容により | 物語の内容により | 「記事」はニュース記事を指す語。対象が物語。 | Yes |

## 2. 逐語維持の重要箇所(theme/problem/value/question、分量、禁止条件、Comment 1・2重複回避)

| # | 逐語維持(Family X原文=Family Z) | 備考 |
|---|---|---|
| K1 | theme(何についての話か) | 変更なし(Family X指示を省略していない) |
| K2 | value(なぜ聞く価値があるか) | 変更なし(Family X指示を省略していない) |
| K3 | 4要素すべてを律儀に別の文で書き並べる必要はありません(question=聞き終える<br>頃に何が分かるようになるか、を無理に独立した一文にしなくてよい)。 | 変更なし(Family X指示を省略していない) |
| K4 | 2文程度、80〜110字程度を目安にしてください | 変更なし(Family X指示を省略していない) |
| K5 | 4文・150字を超えるような長いPreviewにはしない | 変更なし(Family X指示を省略していない) |
| K6 | - 答えを先に言う | 変更なし(Family X指示を省略していない) |
| K7 | - 重要な数字を先出しする | 変更なし(Family X指示を省略していない) |
| K8 | - 結論を先に言う | 変更なし(Family X指示を省略していない) |
| K9 | - turning point(展開の転換点)を先に明かす | 変更なし(Family X指示を省略していない) |
| K10 | - 後で流れるComment 1・Comment 2と内容が重複する | 変更なし(Family X指示を省略していない) |
| K11 | Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。<br>【Comment 1】<br>{comment_1}<br><br>【Comment 2】<br>{comment_2} | 変更なし(Family X指示を省略していない) |

## 3. Family Z現行Promptにのみあった要素(Family X基準への統一で含めないもの)

| # | Family Z現行Promptにのみ存在 | 扱い |
|---|---|---|
| D1 | 「A2レベル、Public Domain文学のリライト」の説明 | Family Xに対応物なし。物語/Newsの差で必須とは説明できないため含めない |
| D2 | 状況設定(誰が・どんな状況か)を2〜3文で紹介 | Family Xにない(theme/problem/valueの別構成)。Family X基準へ統一 |
| D3 | fam_c._BANNED_PHRASES_INSTRUCTION(聞いてみましょう等の禁止・無内容予告/結末先出し/Story外事実/長文化) | Family X PREVIEW_ROLEに無い。News/物語の差による必要性を説明できないため、roleへは含めない。ただしProduction lint(lint_support_text 'ja')のLISTEN_INSTRUCTION検査は呼出側共通の機械処理として不変(retry1->FamilyZLintStop) |
| D4 | 「本文にない設定・事実を追加しないでください」 | Family Xのrole本文にはなく、context見出し「新しいFactの追加禁止」で担保。Family X方式に統一 |
| D5 | 「結末や物語の山場には触れない」 | Family Xの『答え/結論/turning pointを先に言わない』に包含される(Family X逐語維持) |

## 4. context・埋込

| 項目 | Family X | Family Z(Trial) | 理由 | News⇔物語起因 |
|---|---|---|---|---|
| context見出し | `【エピソード全文(参考、新しいFactの追加禁止)】` | 同一(Family X逐語) | 「エピソード全文」はNews/物語共通で置換不要。現行Z Production(`【物語全文(参考、新しい設定・事実の追加禁止)】`)からはFamily X逐語へ寄せる。呼出側1行の変更として`WIRING_DESIGN_01.md`に記載 | N/A(置換せず逐語維持) |
| Comment埋込 | `PREVIEW_ROLE.format(comment_1=, comment_2=)` | 同一方式 | Family X逐語 | N/A |

## 5. Family X原文(逐語)

```
あなたはPodcastの冒頭を担当するナビゲーターです。これからリスナーは、
このエピソードのニュース本文(Preview・Key Phrasesに続いてMain Story・Points・
In One Line、英語)を聞きます。エピソードの一番最初に流すPreviewを日本語で
書いてください。

役割: このニュースの
- theme(何についての話か)
- problem(何が問題・論点か)
- value(なぜ聞く価値があるか)
を、リスナーの関心を引くために必要十分な範囲でごく短く提示します。
4要素すべてを律儀に別の文で書き並べる必要はありません(question=聞き終える
頃に何が分かるようになるか、を無理に独立した一文にしなくてよい)。

【重要・分量】2文程度、80〜110字程度を目安にしてください(記事の内容により
多少の増減は許容しますが、4文・150字を超えるような長いPreviewにはしない
でください)。短く聞きやすいことを優先し、theme/problem/valueを尽くそうと
して冗長にならないよう注意してください。

以下は避けてください:
- 答えを先に言う
- 重要な数字を先出しする
- 結論を先に言う
- turning point(展開の転換点)を先に明かす
- 後で流れるComment 1・Comment 2と内容が重複する

Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。
【Comment 1】
{comment_1}

【Comment 2】
{comment_2}
```

## 6. Family Z Trial Prompt(テンプレート、プレースホルダ付き)

```
あなたはPodcastの冒頭を担当するナビゲーターです。これからリスナーは、
このエピソードの物語本文(Preview・Key Phrasesに続いてMain Story、英語)を聞きます。エピソードの一番最初に流すPreviewを日本語で
書いてください。

役割: この物語の
- theme(何についての話か)
- problem(主人公が直面する問題・対立は何か)
- value(なぜ聞く価値があるか)
を、リスナーの関心を引くために必要十分な範囲でごく短く提示します。
4要素すべてを律儀に別の文で書き並べる必要はありません(question=聞き終える
頃に何が分かるようになるか、を無理に独立した一文にしなくてよい)。

【重要・分量】2文程度、80〜110字程度を目安にしてください(物語の内容により
多少の増減は許容しますが、4文・150字を超えるような長いPreviewにはしない
でください)。短く聞きやすいことを優先し、theme/problem/valueを尽くそうと
して冗長にならないよう注意してください。

以下は避けてください:
- 答えを先に言う
- 重要な数字を先出しする
- 結論を先に言う
- turning point(展開の転換点)を先に明かす
- 後で流れるComment 1・Comment 2と内容が重複する

Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。
【Comment 1】
{comment_1}

【Comment 2】
{comment_2}
```
