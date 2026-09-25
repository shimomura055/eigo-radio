## 管理ID
`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01`(er016_*、`ACTIVE_TASK_TD`/`RESULT_PACKET_TD`)を実行中。本タスクは標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`を使い、er016_*・SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)に触らない。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。Production変更・SSOT変更禁止。**追加LLM call・新Validator・新LLM QA・再生成工程の追加禁止**(生成は原則1 call)。Variation禁止(v4候補1本のみ、対象はMeta記事のみ。Meta v2は実行不要)。Web Search禁止。費用上限¥100(暴走防止、数円単位でSTOPしない)。`git add -A`/`stash`/`amend`禁止。
- STOP条件(ユーザー指定): 追加callが必要/Promptだけでは解決不能と判断/Story・意味が崩れる/新Validatorが必要/Production変更が必要/¥100超過見込み。STOP時`stop_reason.json`、そこまでcommit(`STOP:`接頭)。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read、全文Readは逐語入力の記事・Promptファイルのみ。G-1: git出力は`--short`/`--stat`。F-1: transcript退避不要。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## ユーザー指示要点(全文は末尾【ユーザー指示全文】としてdelegation_logへ保存)
語彙簡略化を「2,000語優先」ではなく頻度帯で扱いを変える設計(〜3,000位: 原則許容/3,000〜5,000: 自然で明確に簡単な代替があれば置換/5,000〜10,000: 原則置換寄り、意味・自然さを損なうなら例外的に残す/10,000超: 固有名詞・不可欠な専門語を除き強く置換)。頻度順位だけで機械的に書き換えない。不自然化対策の思想「Do not replace a difficult word if the replacement sounds less natural or is not clearly easier. Prefer natural, simple English over forced simplification.」「When simplifying vocabulary, prefer a common natural phrase over an awkward one-word replacement.」をPromptに追加(過剰に長くしない)。目的: installation→putting in / collects→gathers / distant→faraway のような「簡略化したつもりで改善していない・不自然」を減らす。比較: Sewer v3 vs Meta v4(別Topicでも同方針が機能するか)。

## 事前指定Read一覧
- `er015_output/news_standard_a2_vocab_effectiveness_trial_01/prompt_standard_v3.txt`(v3逐語)、`a2v3_standard_sewer.md`(Sewer v3逐語)、`frequency_top2000.json`・`vocab_reference.md`(wordfreq設定・lemma化方法)。
- `er015_output/news_natural_advanced_standard_a2_trial_01/comparison_meta.md`(Meta Advanced Baseline逐語、sha256 `20b7ac01…3481`を`sources.json`と照合)、`comparison_sewer.md`(Sewer Advanced、参考)。
- `er015_news_standard_a2_vocab_effectiveness_trial_01.py`: Grep `def |import`→wordfreq読込・lemma化・content word抽出・Level指標・Fact diff・API呼び出しをimport流用(変更禁止)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna単価。

## 実行手順
### STEP 1 頻度帯測定器(既存wordfreqローカル計算を拡張、LLM不使用)
`wordfreq.top_n_list("en", 20000)`で順位表を作り、lemma化後の各content wordに順位を付与(表外=20,000超として「10,000超」帯)。帯: A ≤3,000 / B 3,001–5,000 / C 5,001–10,000 / D >10,000。固有名詞(記事内の大文字語で文頭以外、Meta/Muse/Reuters等)は別枠。出力は帯別の異なり語一覧+延べ数。これを **Sewer v3 / Meta Advanced / Meta v4** に適用。

### STEP 2 v4 Prompt(v3の語彙5行を下記7行に置換。developer・他の行は一字も変えない。機械assertで確認。記事固有語は入れない)
```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Think about how common a word is: very common words are fine; fairly common words may stay if they sound natural; uncommon words should usually be replaced when a clearly simpler natural choice exists; rare words should be replaced unless they are names, essential technical terms, or a key metaphor.
Do not replace a difficult word if the replacement sounds less natural or is not clearly easier. Prefer natural, simple English over forced simplification.
When simplifying vocabulary, prefer a common natural phrase over an awkward one-word replacement.
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft. Replace it only if a clearly simpler and natural choice exists.
```
`prompt_standard_v4.txt`、`prompt_diff_v3_v4.md`を保存。

### STEP 3 生成(1 call)
Meta Advanced Baseline→v4→`b1v4_standard_meta.md`。`gpt-5.6-luna` effort high、`response.model`実値・tokens・latency・JPY・retry→`cost.json`。空出力・API失敗時はSTOP(再試行は1回まで、理由記録)。

### STEP 4 評価(LLM不使用)
- 帯別残存語(Sewer v3 / Meta Advanced / Meta v4)、Meta Advanced→v4で「消えた語/残った語/新出語」と帯。
- Sonnet目視(参考): (a)明らかに置換可能なのに残った難語、(b)無理な置換による不自然表現(Sewer v3の installation→putting in 型が再発したか)、(c)比喩語(stage/backstage/lead role/curtain/understudy/piano)の保持、(d)"some parts of the calls"の維持(修正禁止)。
- Level指標(同一関数)、Fact diff(Advanced→v4)、structure_map(段落対応・Reveal/比喩/Ending位置)。
- 追加LLM call数=1であることを明記。
- `comparison_meta_v4.md`(Advanced→v1→v4全文)、`comparison_sewer_v3_meta_v4.md`(方針の横断比較表)。

### STEP 5 REPORT `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`
§1 頻度帯の定義と測定方法/§2 帯別残存語(Sewer v3・Meta Advanced・Meta v4)/§3 v4 Prompt全文+v3差分/§4 Meta v4全文(+Advanced全文並置)/§5 明らかに置換可能で残った難語・無理な置換の不自然表現(目視)/§6 Level指標/§7 Story・比喩・Reveal・Ending/§8 Fact drift/§9 追加LLM call数・cost・latency・tokens/§10 Fable参考評価`[Fable記入]`/§11 分類`[Fable記入]`/§12 USER_DECISION_REQUIRED`[Fable記入]`/§13 未解決。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_standard_a2_vocab_banding_trial_01.py --out-dir er015_output\news_standard_a2_vocab_banding_trial_01 --step bands-baseline
.venv\Scripts\python.exe er015_news_standard_a2_vocab_banding_trial_01.py --out-dir er015_output\news_standard_a2_vocab_banding_trial_01 --step generate-v4 --budget-jpy 100
.venv\Scripts\python.exe er015_news_standard_a2_vocab_banding_trial_01.py --out-dir er015_output\news_standard_a2_vocab_banding_trial_01 --step evaluate
.venv\Scripts\python.exe er015_news_standard_a2_vocab_banding_trial_01.py --out-dir er015_output\news_standard_a2_vocab_banding_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01.md --json-out docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er015_news_standard_a2_vocab_banding_trial_01.py`、`er015_output/news_standard_a2_vocab_banding_trial_01/`配下、`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01: 頻度帯別の語彙方針+自然さ優先をStandard A2 Prompt v4に組み込みMeta記事で1本生成、帯別残存語・不自然表現・Story維持をSewer v3と横断比較(Luna 1 call、Production変更なし)`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`

## 報告(RESULT_PACKET)
0. T-0 1. Baseline sha256一致 2. 帯別残存語(3記事、異なり語数/延べ) 3. v4の`response.model`実値/tokens/latency/JPY/retry、追加LLM call数 4. 消えた/残った/新出語(帯付き)、目視の(a)(b)(c)(d) 5. Level指標表 6. structure_map要約 7. Fact drift 8. STOP該当有無 9. `git status --short`・commit SHA・push 10. 一覧外Read/Grep理由、Open Item候補(事実列挙)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)
① NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01
目的: Standard A2の語彙簡略化について、単純な「最頻出約2,000語を優先」ではなく、頻度帯によって扱いを変える設計をTrialする。前Trialで、v2:「約2,000語を優先」だけでは語彙簡略化にほぼ効果なし/v3:「簡単に言えるなら置換」「最終自己点検」で圏外語36→28/ただし難語→別の難語、不自然な言い換えが発生、まで確認済み。今回の目的は、追加LLM call・新Validator・新QA工程を増やさず、1回のStandard生成内で語彙と自然さを両立すること。
現在Status: Standard A2 v1: REJECTED/Standard A2 v2: 旧Trial、v3により実質superseded/Standard A2 vocab v3: VALIDATED/今回: TRIAL/最大到達Status: VALIDATED。Production変更禁止。
採用する語彙設計仮説: 頻度順位は絶対的なCEFR判定ではなく、LLMの語彙選択ガイドとして使う。暫定方針: 〜3,000位 原則許容・無理に置き換えない/3,000〜5,000位 自然で明確に簡単な代替があれば置換・不自然になるなら残してよい/5,000〜10,000位 原則置換寄り・ただし意味・自然さを損なうなら例外的に残してよい/10,000位超 固有名詞・不可欠な専門語等を除き強く置換を優先。重要: 頻度順位が高い/低いだけで機械的に書き換えない。例: facility: 2000外でも比較的高頻度、自然なら残してよい/municipalities: より低頻度で towns/local governments 等へ自然に置換できるなら優先置換/installation・inspections: 難しいが無理な言い換えで英語が崩れるなら残す選択肢あり/artery: かなり低頻度、比喩上不可欠かを厳しく判断/septic・wastewater: 専門語として本当に必要かを見る。
不自然化対策: 新しい品質チェック工程は作らない。Prompt内に最低限「Do not replace a difficult word if the replacement sounds less natural or is not clearly easier. Prefer natural, simple English over forced simplification.」必要なら加えて「When simplifying vocabulary, prefer a common natural phrase over an awkward one-word replacement.」ただしPromptを過剰に長くしない。目的は installation→putting in / collects→gathers / distant→faraway のような「簡略化したつもりだが実際には改善していない/不自然」を減らすこと。
Trial: まずMeta記事1本で実行。前回未実行だったMeta v2は実行不要。現行v3をベースに、今回の頻度帯+自然さ方針を入れたv4候補1本だけ生成。Variationは禁止。比較対象: Sewer v3/Meta v4。目的は別Topicでも同じ方針が機能するかを見ること。
評価: 語彙頻度帯別の残存語(〜3000/3000〜5000/5000〜10000/10000超)/明らかに置換可能なのに残った難語/無理な置換による不自然表現/平均語/文/FK/Story structure/metaphor・reveal・ending/Fact drift/Advancedとの差分/追加LLM call数。頻度測定は既存wordfreqのローカル計算を利用してよい。新しいValidator・新しいLLM QA・再生成工程は追加禁止。
コスト: 追加LLM callは原則1回。暴走防止上限¥100。数円単位では停止しない。
STOP条件: 追加callが必要/Promptだけでは解決不能と判断/Story・意味が崩れる/新Validatorが必要になる/Production変更が必要/¥100超過見込み。その場合はSTOPして報告。
Closeout: 必ずREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれか。良好でもProduction採用しない。ユーザー正式採用までAPPROVED_FOR_PRODUCTIONにしない。
PM上の注意: 今回の2件はいずれもTrial。ユーザーが「この方向で良い」と言っているのはTrial実施方針への合意であり、まだProduction正式採用ではない。良好でも最大VALIDATED。APPROVED_FOR_PRODUCTIONへの変更はユーザーがTrial結果を確認して正式採用を判断した後のみ。過去のUSER_DECISION_REQUIREDが新方針でsuperseded/deferredになった場合は整理してよいが、未決の重要事項を黙ってcloseしないこと。
