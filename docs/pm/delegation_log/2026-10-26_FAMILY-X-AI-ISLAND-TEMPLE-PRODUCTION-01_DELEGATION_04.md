## 管理ID
FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_04(2026-10-26 JST、read-only調査: Key Phrase Human Review候補数の仕様確認。ユーザー認識「Std/Advとも8件提示」に対し実際はStd 5件(+Gate除外2)/Adv 7件)。並行: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_01(Lane A、`er121_*`+共有SSOT所有)・FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01(`er118_*`/FZ docs所有)が稼働中。**本委任は共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)・Productionコード・`er019_output/`を編集しない。** 所有=`docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/KP_CANDIDATE_COUNT_CHECK_01.md`、`docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_{USER_02,USER_03,DELEGATION_04}.md`、`docs/pm/RESULT_PACKET_XAIT4.md`。gitは`git commit --only <paths>`。

## 性質/到達上限Status/禁止事項
- 性質: 調査(read-only)。到達上限: 判定(1)承認済み仕様に反する実装不具合/(2)仕様自体の認識違い/(3)承認済み仕様に曖昧さ・記録漏れ、のいずれかと根拠、最小修正案(実装しない)。
- 禁止: 候補の再生成・Prompt変更・Production修正、HR候補の確定(selectコマンド実行禁止)、既存候補・本文・生成結果の変更、有料API(JPY0)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- Opus独立技術レビューGate: 非該当。時間見込み: 40〜60分、直列(単一調査)。費用/日次: JPY0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2: TTSなし(非該当)。T-3: Capなし(JPY0)。

## ユーザー指示(原文)
2件を**一字も変えず**保存する(先頭に「ユーザー指示原文(2026-10-26、Fable経由で逐語保存)」の1行を付けてよい)。
(a) `docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER_02.md`:
```
# Family X「AI島」記事｜現行版採用・Human Review実走指示

## 1. ユーザー決定

**切り口は①現行版を採用します。記事の再生成は不要です。**

今回の目的は、記事の面白さをさらに改善することではなく、**Key Phrase・文法Human Reviewシステムが正式Production経路で正しく機能することの検証**です。

- 現行R2本文・Standard／Advanced英訳を維持。
- B3・Writerの再実行は行わない。
- 記事の切り口を理由とした追加修正・Trialは不要。
- OPEN-526の切り口判断はユーザー決定済みとして記録。

## 2. Human Reviewの実施

以下の3項目について、既存の承認済みHuman Reviewシステムを使用してください。

1. Standard Key Phrase
2. Advanced Key Phrase
3. Advanced Part 2 文法・構文解説

**今回はHuman Reviewの実動作確認が主目的なので、AI推奨候補の自動確定で済ませず、人間による選択・確定経路を実走させます。**

現在の候補・AI推奨順位・選定理由を既存仕様どおり提示し、ユーザーによる選択を待ってください。

ユーザーの候補選定をClaudeやFableが代行してはいけません。

## 3. Human Review確定後のProduction継続

ユーザーが3項目を確定したら、正式Production経路から制作を再開してください。

以下を必ず確認します。

- Human Review候補の提示・選択・確定・保存が正常に動作する。
- AI推奨と異なる選択でも正しく反映される。
- 確定済みのKey PhraseがPart 1・TTS・公開ページまで一貫して反映される。
- 確定済み文法解説がAdvancedのPart 2に反映される。
- 再開時にResearch・B3・Writer等の不要な再生成が発生しない。
- retry／fallback／resumeとの整合が維持される。

その後、TTS・ASR・品質検査・組立を実施し、Standard／Advancedの完成版試聴ページを作成してください。

## 4. 品質・費用・進行管理

- 既存の承認済み品質基準・Production仕様を維持する。
- 新仕様の追加やPrompt変更は行わない。
- 不具合は委任範囲内で原因究明・修正・検証まで自律的に対応する。
- API費用は案件上限200円以内。
- 不要な待機・逐次処理を避け、独立作業は並列化する。
- 品質 ＞ 完成速度 ＞ 量産単価の優先順位を遵守する。

## 5. 完了条件

次の証拠を取得してください。

1. 3項目のHuman Review操作・確定記録
2. 確定結果と後続成果物の一致
3. 正式Production経路でのruntime evidence
4. 必須Regression／Integration／ASR検査PASS
5. Fable独立受入
6. CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Git反映
7. Standard／Advanced完成版試聴URL
8. 実費・量産単価への影響・未解決事項

Human Reviewシステムの検証成功と、記事自体のユーザー最終試聴承認は区別してください。

**まず3項目のHuman Review候補をユーザーが選択できる状態で提示してください。確定後は、不要な再承認を求めず完成版まで進めてください。**
```
(b) `docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER_03.md`:
```
# Family X｜Key Phrase Human Review候補数の仕様確認

## 1. 調査目的

Family X「AI島」記事のHuman Review候補が、以下の件数で提示されました。

- Standard：5件（別途Gate除外2件）
- Advanced：7件

しかし、ユーザーの認識では、**Standard／Advancedともに8件の候補を提示し、その中からHuman Reviewで選択する仕様**だったはずです。

この食い違いの原因を調査してください。

**今回は調査のみ。候補の再生成・Prompt変更・Production修正は行わないでください。**

## 2. 確認事項

### ① 承認済み仕様の確認

CURRENT_SPEC、DECISION_LOG、過去のHuman Review設計・Trial・ユーザー承認記録を確認し、以下を明らかにしてください。

- 各レベル8件という指定が存在するか。
- 8件はAIの初期抽出数か、Gate通過後にユーザーへ提示する件数か。
- Gate除外で8件未満になった場合、候補を補充する仕様か。
- StandardとAdvancedで候補数に異なる規則があるか。
- 仕様が途中で変更された場合、いつ、誰が承認したか。

### ② 今回の実際の動作

「AI島」記事の生成ログ・候補JSON・Gate判定・HR依頼書を照合してください。

- AIが最初に抽出した候補数
- 各Gateで除外された候補と理由
- Gate通過後の候補数
- 補充処理の有無
- 最終的にStandard 5件／Advanced 7件になった直接原因

特に、Standardの2件が除外された後に補充されなかった理由を確認してください。

### ③ 仕様と実装の一致

正式仕様が8件だった場合、現行Productionが仕様どおり動作しているか確認してください。

仕様違反があれば、その原因と最小限の修正案を示してください。

## 3. 報告形式

以下を簡潔に報告してください。

| 項目 | Standard | Advanced |
|---|---|---|
| 承認済み候補数 | | |
| 初期抽出数 | | |
| Gate除外数 | | |
| 補充数 | | |
| 最終提示数 | 5 | 7 |
| 仕様との一致 | | |

併せて、根拠となる承認記録・CURRENT_SPECの該当箇所・実装箇所を明示してください。

結論として、次のどれに該当するか判定してください。

1. 承認済み仕様に反する実装不具合
2. 仕様自体の認識違い
3. 承認済み仕様に曖昧さ・記録漏れがある

## 4. STOP・次工程

調査完了まで「AI島」記事のHuman Review候補は確定しないでください。

既存の候補・本文・生成結果は保全してください。

**調査結果を先に報告し、必要なユーザー判断を受けてから修正・再生成を行うこと。**

費用0円を原則とし、Production仕様は変更しないでください。
```

## KPI provenance欄 / Opus台帳更新
該当なし。

## 事前指定Read一覧
- 承認記録: `CURRENT_SPEC.md` Grep `候補.{0,6}8件|8件|Trial-08|KP候補|Key Phrase候補|候補数|上位8|top_k|k=8` → 該当行±5。`DECISION_LOG.md`・`DECISION_LOG_HISTORY.md` 同Grep。`OPEN_ITEMS.md` Grep `OPEN-518|OPEN-519|OPEN-484|KP-SELECTION-SIX-MODEL|Trial-08` → 該当行。
- Trial/設計: `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{DESIGN_02,OPUS_REVIEW_01,EVIDENCE_01}.md` Grep `8|候補数|max_candidates|候補を|補充|top` → 該当範囲。`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01_USER.md`・`_PROMPT-ADJUST_USER.md`・`2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01*USER*.md`・`2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01*USER*.md`(Glob後、Grep `8|候補`)。Trial-08の正本docs(Glob `docs/research/*KP*SELECTION*/**/*.md`、Grep `8件|候補数|k=`)。
- 実装: `er119_kp_human_review_01.py`・`er119_kp_human_review_cli_01.py`・KP候補生成module(Grep `max_candidates|top_k|CANDIDATE|8|limit|slice|\[:` → 候補数決定箇所)、Gate(validate/canonicalization)の実装行、補充(refill/backfill/reselect/再抽出)の有無。
- 実動作: `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/{a2,b1b}/key_phrases/`配下(候補JSON・Gate判定・request.md・LLM生raw出力があればそれ)、`docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/{EVIDENCE_01,HR_REVIEW_REQUEST_01}.md`。比較用: 直近X記事(WORD-GACHA/MOON-SHRINKING/Z melos R3)のKP候補数(同dir構造をGlob)。
- 付随: HR依頼書でAI推奨行(KP 1〜3)の「AI理由」欄が空欄になる原因(仕様か不具合か)も同じ資料で確認。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 原文2件を保存。
2. ①承認済み仕様: 「8件」の出所を逐語で引用(ユーザー発言/DECISION_LOG/CURRENT_SPEC/Trial設計のどれに、どの意味[初期抽出数/Gate後提示数/選択上限]で書かれているか)。Std/Advで規則差があるか。変更履歴(いつ・誰の承認)。
3. ②実動作: 初期抽出数(LLM出力件数)→各Gate除外(候補名・理由)→Gate後件数→補充処理の有無→提示件数、をStd/Adv別に。Std除外2件後に補充がない理由(補充仕様の不在か、実装漏れか)。他記事の候補数実績も1行表に(仕様のばらつき確認)。
4. ③判定: (1)/(2)/(3)のどれかと根拠。(1)または(3)なら最小修正案(変更箇所・影響範囲・X/Z・費用)。**実装しない。**
5. 付随のAI理由空欄の原因。
6. `KP_CANDIDATE_COUNT_CHECK_01.md`にユーザー指定の表形式(承認済み候補数/初期抽出数/Gate除外数/補充数/最終提示数/仕様との一致)で記載。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_DELEGATION_04.md`(Nは622前後、`--index -1`不可、「FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_04」を含むもの)。

## 実行コマンド全文
- `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`(読取のみ)
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_DELEGATION_04.md --json-out docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_DELEGATION_04.md_check.json`
- secret grep: `git grep -n -I -E "(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|BEGIN (RSA|OPENSSH) PRIVATE KEY)" -- docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/KP_CANDIDATE_COUNT_CHECK_01.md docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER_02.md docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER_03.md docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_DELEGATION_04.md`

## SSOT追記文
本委任は編集しない。OPEN-526追記文案(切り口=ユーザー決定済み①現行版、候補数調査結果)をRESULT_PACKETへ。

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/KP_CANDIDATE_COUNT_CHECK_01.md`、`docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_{USER_02,USER_03,DELEGATION_04}.md`(+_check.json)。
- メッセージ案: 「FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_04: KP Human Review候補数(8件認識 vs Std5/Adv7)の仕様・実装・実動作の照合(read-only、API 0)+ユーザー原文2件保存」
- `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。SSOT編集権: なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XAIT4.md`。「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+RESULT_PACKET 4行+判定整合行。必ず含める: ユーザー指定の表、根拠(承認記録:行・CURRENT_SPEC:行・実装:行・候補JSON path)、判定(1)/(2)/(3)と理由、最小修正案(該当時)、AI理由空欄の原因、他記事の候補数実績、commit/push・raw URL、check結果。