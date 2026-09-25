## 管理ID
`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`(er016_*、`_TD`一時ファイル)を実行中。本タスクは標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`、er015_*のみ。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は編集しない(Open Item候補はREPORTに事実列挙、SSOT反映はFableが別途集約)。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作(reset/amend/rebase)禁止。出力先パスはPowerShell/`\`エスケープに注意(前回`er015_outputnews_…`誤ディレクトリが発生。実行前に`--out-dir`の実パスをprintして確認)。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。Production変更禁止。新Validator・新QA工程・生成後の追加LLM修正call・Variation量産禁止。**LLM callは2回のみ**(Sewer/Meta各1)。Web Search禁止。費用上限¥100(暴走防止、数円単位でSTOPしない)。`git add -A`/`stash`禁止。
- STOP条件(ユーザー指定): 追加LLM callが必要/自然さと語彙制御が両立しない/Story・Factが崩れる/¥100超過見込み/Production変更が必要/新しい仕様判断が必要。STOP時`stop_reason.json`、そこまでcommit(`STOP:`接頭)。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## ユーザー指示要点(全文は末尾【ユーザー指示全文】をdelegation_logへ)
語彙制御を簡素化: 頻出上位6,000語以内は原則そのまま残してよい(学習上必要ならKey Words/Phrasesで補足可能)/6,000語超は平易な語への置換を強く優先、ただし自然さを崩さない/固有名詞は別扱い/専門語は意味保持に必要なら例外可。目的: municipalitiesのような不要に難しい語は落としつつ、facility/installation/inspectionsなどは無理に壊さない。v3ベース、追加思想は最低限(5文)。2記事(Sewer/Meta)、Advanced→Standard A2。特に確認: municipalities/facilities/installation/inspections/convenience/artery/wastewater/septic/collects/distant/invisible。

## 事前指定Read一覧
- `er015_output/news_standard_a2_vocab_banding_trial_01/frequency_rank_top20000.json`(wordfreq順位表・lemma化を再利用)、`vocab_transition_sewer_v4.md`(比較用)。
- `er015_output/news_standard_a2_vocab_effectiveness_trial_01/prompt_standard_v3.txt`(v3逐語、ベース)。
- Advanced入力: Sewer=`er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md`、Meta=`er015_output/news_ja_to_en_adaptation_trial_01/arms/arm3/output.md`(sha256を記録、前Trialの`sources.json`と一致確認)。
- 比較用既存出力: Sewer v3(`a2v3_standard_sewer.md`)、Sewer v4(`a2v4_standard_sewer.md`)、Meta v4(`b1v4_standard_meta.md`)。
- `er015_news_standard_a2_vocab_banding_trial_01.py`: Grep `def |import`→API呼び出し・帯測定・Level指標・Fact diff・structure_mapをimport流用(変更禁止)。

## Prompt v5(6000-cutoff)= v3の語彙5行を以下6行に置換。developer・他の行は一字も変えない(機械assert)。記事固有語は入れない。
```
Prefer words within roughly the 6,000 most common English words.
If a word is clearly outside that range, replace it when a simpler natural alternative exists.
Do not force a replacement if it makes the sentence less natural or changes the meaning.
Proper names are excluded from this rule.
Essential technical terms may remain when a simpler equivalent would lose important meaning.
Do not add an explanation for a hard word; make the sentence around it simple instead.
```
`prompt_standard_v5_6000.txt`、`prompt_diff_v3_v5.md`保存。

## 実行手順
1. `--step generate --article sewer` / `--article meta`(各1 call、`gpt-5.6-luna` effort high、`response.model`実値・tokens・latency・JPY・retry=0)→`a2v5_standard_sewer.md`、`b1v5_standard_meta.md`。
2. `--step evaluate`(LLM不使用): 各記事について 6,000位超の残存content word一覧(順位付き、固有名詞別枠)→Sonnet仮分類「必要語(専門語/比喩)/置換可能だった語」/Advanced→v5の置換一覧(消えた語→新語、双方の順位)から「不自然な置換」「難語→別の難語(新語の順位が元語以上)」を判定/Level指標(words/文数/平均語・文/従属詞/FK)/Fact diff(数字・固有名詞・否定・範囲語)/structure_map(段落対応、Reveal/比喩/Ending位置、比喩が比喩のままか)/Advancedとの意味差(Sonnet目視で1行ずつ)。ユーザー指定11語の遷移表(Advanced→v3→v4→v5)。
3. `--step assemble`: `comparison_sewer_v5.md`(Advanced→v3→v5全文)、`comparison_meta_v5.md`(Advanced→v4→v5全文)、`vocab_over6000_sewer.md`/`vocab_over6000_meta.md`、`vocab_transition_11words.md`、`level_metrics.md`、`cost.json`。
4. REPORT `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md`: §1 方針・測定方法(wordfreq順位6,000ライン、lemma化)/§2 v5 Prompt全文+v3差分/§3 Sewer v5全文(+Advanced並置)/§4 Meta v5全文(+Advanced並置)/§5 6,000超残存語一覧と必要/置換可能の仮分類(2記事)/§6 不自然な置換・難語→難語置換の有無/§7 11語遷移表/§8 Level指標/§9 Story・Reveal・比喩・Ending/§10 Fact drift・意味差/§11 cost・latency・tokens・call数=2/§12 Fable参考評価`[Fable記入]`/§13 分類`[Fable記入]`/§14 USER_DECISION_REQUIRED`[Fable記入]`/§15 Open Item候補・未解決。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_standard_a2_vocab_6000_cutoff_trial_01.py --out-dir er015_output\news_standard_a2_vocab_6000_cutoff_trial_01 --step generate --article sewer --budget-jpy 100
.venv\Scripts\python.exe er015_news_standard_a2_vocab_6000_cutoff_trial_01.py --out-dir er015_output\news_standard_a2_vocab_6000_cutoff_trial_01 --step generate --article meta --budget-jpy 100
.venv\Scripts\python.exe er015_news_standard_a2_vocab_6000_cutoff_trial_01.py --out-dir er015_output\news_standard_a2_vocab_6000_cutoff_trial_01 --step evaluate
.venv\Scripts\python.exe er015_news_standard_a2_vocab_6000_cutoff_trial_01.py --out-dir er015_output\news_standard_a2_vocab_6000_cutoff_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er015_news_standard_a2_vocab_6000_cutoff_trial_01.py`、`er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/`配下、`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01: 語彙制御を「上位6,000語ライン+自然さ維持」に簡素化したStandard A2 Prompt v5でSewer/Metaを各1本生成し、6,000超残存語・置換の自然さ・Story維持をv3/v4と比較(Luna 2 call、Production変更なし)`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. Prompt差分・入力sha256 2. 2 callの`response.model`実値/tokens/latency/JPY、合計 3. 6,000超残存語(2記事、必要/置換可能の仮分類) 4. 不自然な置換・難語→難語置換の件数と例 5. 11語遷移表 6. Level指標 7. structure_map・Fact drift・意味差 8. STOP該当有無 9. `git status --short`・commit SHA・push 10. 一覧外Read理由、Open Item候補。

---
【ユーザー指示全文】
NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01。目的: Standard A2の語彙制御を、これまでの複雑な頻度帯設計から簡素化する。新方針: 頻出上位6,000語以内=原則そのまま残してよい、学習上必要ならKey Words/Phrasesで補足可能/6,000語超=平易な語への置換を強く優先、ただし置換によって文章の自然さを崩さない/固有名詞は別扱い/専門語は意味保持に必要なら例外可。目的は、municipalitiesのような不要に難しい語は落としつつ、facility/installation/inspectionsなどは無理に壊さないこと。背景: v3=語彙簡略化は一定効果あり、v4=頻度帯を細かくPromptへ入れたが再現性向上せずREJECTED。今回はルールを簡素化し「6000語ライン+自然さ維持」だけに絞る。対象: Sewer/Meta、Advanced→Standard A2。Prompt設計: v3をベース。追加・変更する思想は最低限: Prefer words within roughly the 6,000 most common English words. / If a word is clearly outside that range, replace it when a simpler natural alternative exists. / Do not force a replacement if it makes the sentence less natural or changes the meaning. / Proper names are excluded from this rule. / Essential technical terms may remain when a simpler equivalent would lose important meaning. 過剰にPromptを増やさない。禁止: 新Validator追加/新QA工程追加/生成後の追加LLM修正call/Variation量産/Production変更。評価: 各記事について 6000語超の残存語一覧/その語が必要語か置換可能だった語か/不自然な置換有無/難語→別の難語への置換有無/平均語/文/FK/Story structure/Reveal・metaphor・Ending/Fact drift/Advancedとの意味差。特に確認したい語: municipalities/facilities/installation/inspections/convenience/artery/wastewater/septic/collects/distant/invisible。コスト: 2記事合計の暴走防止上限¥100。数円単位でSTOPしない。Status: 現在TRIAL、最大到達VALIDATED。良好でもProduction採用しない。STOP条件: 追加LLM callが必要/自然さと語彙制御が両立しない/Story・Factが崩れる/¥100超過見込み/Production変更が必要/新しい仕様判断が必要。Closeout: REJECTED/VALIDATED/USER_DECISION_REQUIRED。結果報告後STOP。共通PM Gate: Trial終了時status分類、UDRがあれば明示してSTOP、勝手に追加Trialへ進まない、Production正式path不変、SSOTはTrial結果として必要な記録のみ、Dangling Reference Check実施、Closeout時に未処理UDR/APPROVED_FOR_PRODUCTION未配線/未報告Trial/新規Open Itemを一覧化。
