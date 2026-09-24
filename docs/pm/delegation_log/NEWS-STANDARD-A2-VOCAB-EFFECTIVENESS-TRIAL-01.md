## 管理ID
`NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(er016_*、`ACTIVE_TASK_RR`/`RESULT_PACKET_RR`、OPEN_ITEMS.mdを編集)を実行中。本タスクは標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`を使い、er016_*とSSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)に触らない。commit時`index.lock`は10秒待ち再試行(最大3回)。`git status --short`で他タスクのstaged変更が混在していれば、自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。Production変更・SSOT変更禁止。Validator+再生成の多段構成は入れない(Prompt単体)。追加Variation禁止(v3候補は**1本のみ**)。新規有料API・Web Search禁止。費用上限**¥100**(暴走防止目的、数円単位でSTOPしない)。`git add -A`/`stash`/`amend`禁止。
- STOP条件(ユーザー指定): 信頼できる頻度基準を確認できない/語彙簡略化で意味が壊れる/Storyが大きく崩れる/追加Variationが必要/¥100超過見込み/Production変更が必要。STOP時`stop_reason.json`、そこまでをcommit(`STOP:`接頭)。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read、全文Readは逐語入力の記事・Promptファイルのみ。G-1: git出力は`--short`/`--stat`。F-1: transcript退避不要。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## ユーザー指示要点(全文は末尾【ユーザー指示全文】としてdelegation_logへ保存)
Standard A2 v2の「最頻出約2,000語を優先」指示が実際にどの程度効いているか測定(municipalities/artery/combined septic tank等が残存)。その後、単一生成のままPromptで語彙制御を強めたv3候補を1本生成しv2と比較。難語の設計原則A(固有名詞・代替しにくい専門語は残してよい)/B(平易な表現で置換可能なら残さない: municipalities→local governments/towns、artery→pipe network/main line/lifeline等)/C(難語だから説明文を追加、は禁止)。

## 事前指定Read一覧
- `er015_output/news_standard_a2_prompt_v2_trial_01/a2v2_standard_sewer.md`(v2全文、逐語)、`prompt_standard_v2.txt`(v2 Prompt逐語)、`level_metrics.json`。
- `er015_output/news_natural_advanced_standard_a2_trial_01/comparison_sewer.md`(下水道Advanced Baseline逐語、sha256は`sources.json`と照合)。
- `er015_news_standard_a2_prompt_v2_trial_01.py`: Grep `def |import`→API呼び出し・Level指標・Fact diff・sha256をimport流用(変更禁止)。
- 頻度基準の探索(順に確認、最初に得られたものを採用し出典・件数・ライセンスを`vocab_reference.md`に記録): (1) Repo内: `Glob **/*{ngsl,NGSL,oxford,gsl,wordlist,word_list,frequency,cefr}*`、`Grep pattern="ngsl|oxford 3000|wordfreq|cefr" -i glob="*.{py,json,txt,csv,md}" -l`。(2) `.venv`: `pip show wordfreq nltk spacy`(既存ならその語彙頻度を使用: wordfreqなら`top_n_list("en", 2000)`)。(3) いずれも無ければ、無料公開の頻度リスト1件(NGSL 1.2 または wordfreq の`pip install wordfreq`[無料・ローカル、有料APIではない])を1回だけ取得し、出典URL・取得日時・ライセンスを記録。(4) それでも得られなければSTOP。**採用基準は「約2,000語圏」として、リスト上位2,000語(lemma化: 複数形/三単現/過去形/-ing/比較級の簡易正規化、標準ライブラリで実装)を用いる。**
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna単価。

## 実行手順
### STEP 1 v2の実効性測定(修正しない)
- 下水道Standard v2をtokenize→機能語(冠詞/前置詞/代名詞/助動詞/接続詞/be動詞等、固定リスト)を除いたcontent word総数→2,000語圏内/圏外を判定→圏外語の一覧を **固有名詞/専門語/一般語** に分類(機械分類+Sonnet目視、分類根拠を1語ずつ記録)→一般語のうち「平易な語で置換可能(原則B)」「必要(原則A)」をSonnetが仮分類(**参考。最終はFable/ユーザー**)。
- 同じ測定をAdvanced Baselineとv1にも実施(参考、比較用)。
- 出力 `vocab_analysis_v2.json`/`vocab_analysis_v2.md`(content word総数、圏内割合、圏外一覧と分類、圏外の延べ/異なり)。
- 実効性評価: v2 PromptがAdvanced比で圏外語をどれだけ減らしたか(異なり語数と延べ)を数値で示す。

### STEP 2 v3 Prompt(v2からの差分のみ、記事非依存)
v2の次の2行:
```
Prefer common, high-frequency English words (roughly the 2,000 most common words).
Keep harder words only when they are necessary to understand the topic (for example, a technical term or a name). Do not add an explanation for a hard word; make the sentences around it simple instead.
```
を以下(逐語)に置換。それ以外のv2本文は一字も変えない(developer含む):
```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Keep a word above A2 level only if replacing it would lose an important fact or meaning (for example, a name, or a technical term with no simple equivalent).
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft and replace each non-essential one with simpler English.
```
`prompt_standard_v3.txt`と`prompt_diff_v2_v3.md`を保存。

### STEP 3 生成(1 call)
下水道Advanced Baseline→v3 Prompt→`a2v3_standard_sewer.md`。`gpt-5.6-luna` effort high、`response.model`実値・tokens・latency・JPY・retry→`cost.json`。

### STEP 4 比較
- v3にSTEP 1と同じ語彙測定→`vocab_analysis_v3.json/.md`、v2 vs v3の圏外語対照表(消えた語/残った語/新たに出た語、残った語ごとに必要/不要の仮分類)。
- Level指標(v2と同一関数): words/sentences/平均語・文/従属詞/FK。
- Fact diff(Advanced→v3、同一関数)、structure_map(段落対応、Reveal/比喩[main artery・washing machine]/Endingの位置○×、比喩が比喩のまま[like/as if]か事実文化していないか)。
- 意味崩れチェック: 置換語で意味が変わった箇所を事実列挙(例: artery→? が「見えない大動脈」の意味を保つか)。
- `comparison_sewer_v2_v3.md`(Advanced→v2→v3全文)。

### STEP 5 REPORT `NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_REPORT.md`
§1 使用した頻度/語彙基準(出典・件数・lemma化方法・限界)/§2 v2の圏外語一覧と分類(固有名詞/専門語/一般語、必要/不要仮分類)/§3 「2,000語優先」指示の実効性評価(Advanced/v1/v2の数値比較)/§4 v3 Prompt全文+v2差分/§5 v3記事全文/§6 v2 vs v3語彙比較/§7 Level指標/§8 Story・比喩・Ending保持/§9 Fact drift・意味崩れ/§10 model・cost・latency・tokens/§11 Fable参考評価`[Fable記入]`/§12 分類`[Fable記入]`/§13 USER_DECISION_REQUIRED`[Fable記入]`/§14 未解決。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_standard_a2_vocab_effectiveness_trial_01.py --out-dir er015_output\news_standard_a2_vocab_effectiveness_trial_01 --step vocab-ref
.venv\Scripts\python.exe er015_news_standard_a2_vocab_effectiveness_trial_01.py --out-dir er015_output\news_standard_a2_vocab_effectiveness_trial_01 --step analyze-v2
.venv\Scripts\python.exe er015_news_standard_a2_vocab_effectiveness_trial_01.py --out-dir er015_output\news_standard_a2_vocab_effectiveness_trial_01 --step generate-v3 --budget-jpy 100
.venv\Scripts\python.exe er015_news_standard_a2_vocab_effectiveness_trial_01.py --out-dir er015_output\news_standard_a2_vocab_effectiveness_trial_01 --step compare
.venv\Scripts\python.exe er015_news_standard_a2_vocab_effectiveness_trial_01.py --out-dir er015_output\news_standard_a2_vocab_effectiveness_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er015_news_standard_a2_vocab_effectiveness_trial_01.py`、`er015_output/news_standard_a2_vocab_effectiveness_trial_01/`配下(頻度リストを取得した場合はリスト本体もここに保存し、ライセンス表記を同梱)、`NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01.md`、同`_check.json`。`pip install`した場合は`requirements*.txt`があれば追記(無ければRESULT_PACKETに記録のみ)。
メッセージ: `NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01: Standard A2 v2の「2,000語優先」指示の実効性を頻度リストで測定し、語彙制御を強めたv3 Promptで下水道Standardを1本生成しv2と比較(Luna、Production変更なし)`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. 採用した頻度基準(出典・件数・ライセンス・取得方法) 2. v2のcontent word総数/圏内割合/圏外一覧(分類付き)、Advanced・v1との比較 3. v3の`response.model`実値/tokens/latency/JPY/retry 4. v2 vs v3圏外語対照(消えた/残った/新出)、残存難語の必要/不要仮分類 5. Level指標表 6. structure_map要約(比喩が比喩のままか) 7. Fact drift・意味崩れ 8. STOP該当有無 9. `git status --short`・commit SHA・push 10. 一覧外Read/Grep理由、Open Item候補(事実列挙)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)
NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01
目的: Standard A2で入れている「最頻出約2,000語を優先する」という指示が、実際にどの程度効いているかを確認する。現状、文長・文法簡略化はv2で改善したが、municipalities/artery/combined septic tank等、A2として明らかに難しい語が残っている。今回は、まずPrompt指示そのものの実効性を確認し、そのうえでプロセスを増やさず、単一生成のまま語彙制御を強くする方法を検討・Trialする。
現在Status: Advanced Natural=APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE。Standard A2 Prompt v2=USER_DECISION_REQUIRED。今回の最大到達Status=VALIDATED。Production変更禁止。
1. まず現状v2の実効性を確認: 対象=下水道Standard v2(Metaはまだv2未生成なので既存Standard v1/Advancedは参考のみ)。既存の信頼できる英語頻度リストまたはCEFR相当語彙資源をRepo内・既存依存関係から利用可能か確認。新規有料APIは使わない。最低限、下水道Standard v2について content word総数/約2,000語圏内の割合/2,000語圏外候補一覧/固有名詞/専門語/一般語を分ける。重要: ここでは個別修正しない。目的は「Promptで2,000語優先と書いただけで、実際にどれくらい守られているか」を測ること。
2. 難語の設計原則: 原則A 2,000語圏外でも記事理解に本当に必要な語は残してよい(固有名詞/代替しにくい専門用語)。原則B ただし平易な表現で置き換え可能なら難語を残さない(municipalities→local governments/towns等、artery→pipe network/main line/lifeline等、combined septic tank→専門語として必要なら初回のみ残す可能性あり、ただし簡単な説明表現だけでStoryが成立するなら難語依存を避ける)。原則C 「難語だから説明文を追加する」は避ける。Storyを膨らませず、語そのものを簡単にすることを優先。
3. Prompt改善を検討: Validator+再生成の多段構成は今回入れない。まずはPrompt単体でどこまで改善できるかを見る。Claudeはv2 Promptの問題点を分析し「2,000語を優先」より実効性の高い表現を設計する(思想例: Use common words whenever a simpler word can express the same meaning. / Do not keep a difficult word just because it appears in the Advanced version. / Keep a word above A2 level only if replacing it would lose an important fact or meaning. / Before finalizing, review every difficult word and replace any non-essential one with simpler English。)ただしPromptを過剰に長くしない。
4. Trial: 同じ下水道Advanced Naturalを使い、Standard v3候補を1本だけ生成。追加Variation禁止。その後v2/v3で比較。
5. 評価: 平均語/文/FK/2,000語圏外候補数/不要な難語数/必要難語数/Story structure preservation/metaphor preservation/ending preservation/Fact drift/Audioでの理解しやすさ。最重要: 難しい語が減ったか と Storyの面白さが残ったか の両方。
6. コスト: 今回追加費用上限¥100。数円単位でSTOPしない。上限は暴走防止目的。不要なWeb Search・大量Variationは禁止。
7. STOP条件: 信頼できる頻度基準を確認できない/語彙簡略化で意味が壊れる/Storyが大きく崩れる/追加Variationが必要/¥100超過見込み/Production変更が必要。
8. Closeout: REJECTED/VALIDATED/USER_DECISION_REQUIRED。良好でもProduction採用しない。最終判断はユーザー。
9. 最終報告: 使用した頻度/語彙基準/v2で2,000語圏外だった語一覧/そのうち必要語・不要語の分類/「2,000語優先」指示の実効性評価/v3 Prompt全文/v3記事全文/v2 vs v3語彙比較/Story保持/Fact drift/cost/Trial分類/USER_DECISION_REQUIRED/未解決事項。完了後STOP。
