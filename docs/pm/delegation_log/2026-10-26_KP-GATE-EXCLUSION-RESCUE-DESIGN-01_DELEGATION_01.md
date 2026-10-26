## 管理ID

KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_01(新規案件。ユーザーGoあり=本日のユーザー指示原文を下記「ユーザー指示(原文)」に逐語掲載)。並行タスク: なし(他Agentは全停止。X AI島 run_ai_01 はHR待機中で**候補未確定のまま保全**、Y/Zはユーザー判断待ち)。本委任が所有するファイル=`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/**`、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_*`、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET_KPRS1.md`のみ。

## 性質/到達上限Status/禁止事項

- 性質: **調査・設計のみ**(Production変更なし・有料API 0・新規Trial 0)。Family X/Y/Z共通のKey Phrase候補Gate(語数・canonicalization等)で除外された候補を「修正→再検査→Human Review候補へ残す」救済方式を、既存データのみで分析・設計する。
- 到達上限Status: `USER_DECISION_REQUIRED`(Sonnetは`判断候補`と表記。ラベル付与はFable)。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDには到達しない。
- 禁止事項(ユーザー明示): Productionコード・Prompt・Gate(`er119_*.py`、`er003_key_words_canonicalization.py`、`er119_kp_prompt_2v_01.py`、各runner)の変更禁止/新規有料Trial禁止(有料API呼出0。`.venv\Scripts\python.exe`での有料run起動禁止、分析scriptは`py`で実行し、LLM/TTS clientをimportしない)/AI島 run_ai_01 のHR候補を確定しない(`select`/`reselect`/`grammar-select`/`declare-absent`を実行しない。`status`のみ可)/`er0XX_output/`配下へ書き込まない(読取のみ)/新たな品質基準・候補選定規則を独断で追加しない(設計案として提示し採用はユーザー判断)/`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・`docs/pm/REPORT_LEDGER.md`・`docs/pm/USER_DECISION_REGISTER_01.md`は編集しない(追記文案のみRESULT_PACKETへ)/Git禁止操作: `git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`。
- 修正範囲の線引き(PM_GOVERNANCE 11-8): 今回は実装しないが、設計上「範囲内=承認済み仕様(5語以下・本文対応・正規化規則・数合わせ禁止・最大8件)と実装の乖離の是正」と「範囲外=受理面・閾値・方式の新設/拡大(例: 新しい一般化規則の追加、語数上限変更、Prompt 2-V変更)」を各救済案ごとに明示分類すること。範囲外に当たる案は「ユーザー承認が必要な新規則」と必ず明記する。
- Opus独立技術レビューGate(11-3): **条件A候補**(X/Y/Z共通核に新しい処理フロー「違反検出→修正→再検査→HR登録」を加える設計)。Opus依頼はFableが設計受領後に行う。本委任では`OPUS_REVIEW_REQUEST_01.md`(重要論点に絞った依頼文案)を作成するのみ。
- 時間見込み: 全体60〜90分(SSOT/コード照合20、既存データ棚卸し+分析script 25、設計・報告25)。並列化: 単一Agent(同一コード・同一データの読取で分割効果が小さく、SSOT編集なし)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約123(出典: docs/pm/ACTIVE_TASK.md固定ヘッダ/RESULT_PACKET_SSOTSYNC2.md)/残JPY約877/本委任見積JPY0/改善見込み高/承認区分: C(承認済みscope内・JPY0)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 本委任は費用上限[Cap]を伴わない(JPY0)。有料API呼出が1件でも必要と判明した場合は実行せずSTOPして報告する(ユーザー明示「新規有料Trialは禁止」)。

委任文保存(T-0の具体手順): 
```
py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 629 --out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_DELEGATION_01.md
```
`--index -1`は使えない。629で抽出した本文の先頭が「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_01」でなければ630, 631…と1つずつ増やして再抽出し(上限640)、一致したindexをRESULT_PACKETに記録する。続けて`py docs/pm/tools/check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_DELEGATION_01.md_check.json`。
さらに、下記「ユーザー指示(原文)」節の本文(見出し「# Family XYZ共通｜…」から最終行「この違いを設計の中心に置いてください。」まで)を**一字も変えず**`docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_USER.md`へ保存する(先頭に1行だけ `<!-- ユーザー指示原文(2026-10-26)。逐語。Fable委任_01に同梱された写しから転記 -->` を付けてよい)。

## ユーザー指示(原文)

# Family XYZ共通｜Key Phrase候補のGate除外パターン調査・修正救済方式の設計

## 1. 背景・目的

Family X「AI島」記事のKey Phrase Human Reviewで、Standardの候補2件がGate違反により除外された。

- `too soon to wave a flag`：6語のため除外
- `studied separately`：原形への正規化規則違反で除外

しかし、いずれも候補として救済できる可能性がある。

例：
- `too soon to wave a flag` → `too soon to do` のように5語以下へ一般化
- `studied separately` → 文脈を確認して適切な原形へ正規化

**今回の目的は、既存候補を安易に捨てず、修正可能なものをHuman Review候補として残す方式を設計すること。**

候補数8件を機械的に達成することが目的ではない。

また、ユーザーはHuman Reviewで学習価値を最終判断するため、AIが学習価値の主観的評価だけを理由に、修正可能な候補を過度に除外しないこと。

## 2. 調査範囲

既存の承認済み仕様、CURRENT_SPEC、DECISION_LOG、過去のTrial、Production実装、候補生成ログ、Gate除外記録を確認する。

Family X/Y/Z共通の仕様として整理し、Family固有の例外があれば区別する。

### ① Gate除外理由の網羅的な整理

実際に存在する除外パターンを洗い出す。

少なくとも以下の観点を確認する。

- 5語上限の超過
- 動詞の原形・辞書形への正規化不足
- 活用形、受動態、時制などの形態変化
- 本文との対応不備
- 一般化の不足・過剰
- 重複候補
- その他、実際のGateで除外される条件

上記は調査観点であり、すべてが現行Gateの実在する除外条件だと決めつけないこと。

各パターンについて、承認済み規則と実装の対応を確認する。

### ② パターン別の修正方法

除外理由ごとに、候補を修正して救済できるか検討する。

基本処理：

候補抽出 → Gate検査 → 違反検出 → 修正可能性の判断 → 修正 → 再検査 → Human Review候補へ登録

修正できないものだけを除外する。

検討する修正例：

**A. 語数超過**

`too soon to wave a flag` → `too soon to do`

のように、表現の核を残して一般化・短縮できるか確認する。

ただし、元の本文との対応関係を失わないこと。

**B. 正規化不足**

`studied separately` → `study separately`

のように、文脈に即して適切な基本形へ修正する。

単純な文字置換だけで意味や構文が変わる場合は、適切に判断すること。

**C. その他**

実際の除外パターンについて、同様に救済方式を立案する。

修正困難な候補は、無理に救済せず除外を認める。

## 3. 設計原則

以下を必ず守ること。

1. **修正による救済を、新しい候補の追加抽出より優先する。**
2. 既存の承認済み品質条件（5語以下、本文との対応、正規化など）は維持する。
3. 一般化によって、元の本文にない意味や不自然な英語を作らない。
4. 修正前・修正後・修正理由を記録できるようにする。
5. 修正後は既存Gateで再検査する。
6. 修正不能な候補の除外は許容する。
7. 学習価値の最終選択はHuman Reviewのユーザー判断に委ねる。
8. 不要なLLM呼び出し・再生成を避け、可能な修正は低コストで実施する。
9. 既存の候補順位・重複排除・選定数・Human Review仕様との整合を維持する。

AIによる候補修正が必要な場合と、機械的な修正で十分な場合を区別すること。

## 4. 検証・設計評価

まず既存の候補・除外ログを利用して、追加API費用0円で分析する。

過去の実例を用いて、各除外パターンについて以下を評価する。

- 救済可能件数
- 救済困難件数
- 修正の正確性・自然さ
- 元の本文との対応
- Gate通過可能性
- 重複候補が生じる可能性
- 量産単価への影響

特に今回のAI島記事の2件について、具体的な修正案を提示すること。

必要な場合は複数案を比較するが、意味のないTrial反復は行わない。

## 5. QCD

優先順位は品質 ＞ 完成速度 ＞ 量産単価。

- 承認済み品質規則は変更しない。
- 必要十分な設計ができた時点で止める。
- 既存データを再利用して調査する。
- Family XYZの共通化を前提とする。
- 量産単価70円／記事セットに対する追加コストを見積もる。
- 実装を過度に複雑化しない。

## 6. 報告形式

次の表を作成すること。

| 除外パターン | 実例 | 現行の除外理由 | 修正方法 | 救済可否 | 追加コスト |
|---|---|---|---|---|---|

加えて以下を報告する。

1. 現行Gateの除外パターン一覧と発生実績。
2. 今回のAI島記事2件の修正案。
3. 機械的な修正とAI判断が必要な修正の区別。
4. 救済後のGate再検査方式。
5. Human Review候補への反映方法。
6. Family XYZの既存Production仕様・過去Trialとの整合。
7. 救済率・品質リスク・量産単価・制作速度への影響。
8. 推奨する必要十分な実装案と残るOpen Item。

Fableによる独立レビューを実施し、見落とし・過剰な制約・既存仕様との矛盾を確認すること。

## 7. 承認境界・STOP条件

**今回は調査・設計のみ承認。**

- Productionコード・Prompt・Gateの変更は禁止。
- 新規有料Trialは禁止。
- 現行のAI島記事のHuman Review候補は未確定のまま保全する。
- 設計案の採用・Production Wiringはユーザー判断後に行う。
- 新たな品質基準や候補選定規則を独断で追加しない。

完了時のStatusはUSER_DECISION_REQUIREDとし、ユーザーが修正救済方式の正式採用を判断できる状態で報告してください。

**重要：今回解決したいのは「8件に届かないこと」そのものではなく、「適切に修正できる候補まで捨ててしまうこと」です。**

この違いを設計の中心に置いてください。

## KPI provenance欄

該当なし(数値はすべて既存ログの再集計=reuse。新規測定なし)。

## Opus台帳更新

該当なし(本委任ではOpus指摘の状態遷移なし。関連する既存指摘: `docs/pm/OPUS_FINDINGS_LEDGER.md`のKP HR R-1「vocabのshortfall受容・数合わせretryなし」をGrepで確認し、設計との関係をDESIGN_01に1行記す)。

## Fableからの前提・既知事実(重複調査を避けるため)

直前の調査`docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/KP_CANDIDATE_COUNT_CHECK_01.md`(全文Read必須、約60行)で確定済み:
- 承認済み候補数規則=「TOP 8まで(上限)・数合わせ禁止」。補充機構なし(Opus R-1由来のFable設計判断、CURRENT_SPEC未記載)。
- 実装: `er119_kp_human_review_01.py:49` KP_CANDIDATE_MAX=8。`er119_kp_candidates_01.py` :94(5件超overflow除外)、:180-204(call1=Prompt 2無変更3件・reason_ja=""固定、call2=Prompt 2-V最大5件)、:334(外側retry条件=AUTO可<3 かつGate除外あり)、:353(shortfall記録)。`er119_kp_prompt_2v_01.py:19,26-29`。
- AI島 run_ai_01 の除外2件(`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/a2/key_phrases/kp_candidates.json`と`work/outer_retry_log.json`): (1) `too soon to wave a flag`=validate「語数が1〜5語でない(実際: 6語)」(2) `studied separately`=canonicalization「key_phrase('study separately')がdisplay_phraseと一致せず、source_span('studied separately')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)」。
- 他記事実績(§4表): EV R1/R2(X)、EV R3/R4(Z melos)、Y 再配達(a2除外2・b1b除外1)、Y SNS年齢(b1b除外2)。
- **重要な照合点(必ず確認)**: `CURRENT_SPEC.md:1997`付近(Z本文選定の後段)に「基本形化=活用形→基本形の1対1トークン置換のみ許す決定論validator[先頭または`to`直後の動詞・最終語の複数形、除外表あり]。Rule7の例外であり人物一般化と同型のX/Z限定例外」という**承認済みの活用形→基本形例外**がある。にもかかわらず`studied separately`→`study separately`(先頭動詞の過去形→原形、1対1トークン置換)がer119 HR候補経路でINVALIDになった。この例外が(a)どの管理IDでいつ承認され(b)どのコード(`er003_key_words_canonicalization.py`のどの関数)に実装され(c)er119候補経路(X/Y/Zのどれ)で適用されているか/されていないかを、コードと実ログで確定すること。もし「承認済み例外がer119経路に未適用」なら、それは11-8の**範囲内(仕様と実装の乖離)**であり、救済設計以前の是正候補として最優先で報告する(ただし今回は実装しない)。逆に例外の適用条件(X/Z限定、`to`直後、除外表等)により正当に除外されたなら、その根拠行を示す。
- 関連DECISION_LOG: `:87`(KP-OUTER-RETRY-SAME-PHRASE-FIX-01、OPEN-456 F1、INVALID句の累積除外)、`:10193-10200`(人称代名詞・所有格一般化の例外 `_is_valid_person_generalization`、PRODUCTION_WIRED)、`:50`(長行。canonicalization関連の可能性、Grepで確認)。

## 事前指定Read一覧

1. `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/KP_CANDIDATE_COUNT_CHECK_01.md` 全文。
2. `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/HR_REVIEW_REQUEST_01.md` :1-58(候補表と除外表示)。
3. `er119_kp_candidates_01.py`: Grepで`def `一覧→validate/gate/canonicaliz/dedup/overflow/shortfall/outer_retry/excluded/reason に関係する関数の該当範囲のみRead(全文Read禁止。ただし除外理由文字列の生成箇所はすべて特定する)。
4. `er119_kp_human_review_01.py` :40-60(定数)と`render_request`(Grep→該当範囲)。
5. `er119_kp_wiring_01.py`: X/Y/Zのどのrunnerからどう呼ばれるか(Grep `er119_kp_wiring`を`er019_*runner*.py`/`er026_*`/`er062_*`/`er121_family_y_runner_01.py`で確認→該当行±10)。
6. `er003_key_words_canonicalization.py`: Grep `Rule7|_is_valid_person_generalization|基本形|inflect|lemma|base_form|連続部分文字列`→該当関数のみRead。
7. `er119_kp_prompt_2v_01.py` 全文(短い)。
8. `CURRENT_SPEC.md` :1990-2001 と Grep `Key Phrase|KP Human Review|canonicalization`で見つかるX/Y共通KP節(該当行±15のみ)。
9. `DECISION_LOG.md` :50, :87, :10185-10205(行範囲Read)。
10. `docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/F1_FIX_EVIDENCE_01.md` 全文(短いはず。長ければ§見出しとINVALID理由の列挙部分のみ)。
11. `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/DESIGN_02.md` Grep `shortfall|除外|Gate|validate`→該当範囲、`OPUS_REVIEW_01.md:50-60`。
12. 実データ(読取のみ): 以下の各run配下の`*/key_phrases/kp_candidates.json`と`*/key_phrases/work/outer_retry_log.json`、存在すれば`keywords_canonicalized.STALE_attempt*.json`:
    - `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/{a2,b1b}`
    - KP_CANDIDATE_COUNT_CHECK_01 §4に挙がるEV R1/R2(X)・EV R3/R4(Z melos)・Y 再配達・Y SNS年齢の各run(pathはGlob `**/key_phrases/kp_candidates.json`で特定し、一覧をEXCLUSION_PATTERNS_01に記録)。
    - 加えてHR導入前の共通canonicalization経路の除外実績: Glob `er019_output/**/keywords_canonicalized*.json`、`er026_output/**/keywords_canonicalized*.json`、`er121_output/**/keywords_canonicalized*.json`、`er011_output/**/keywords_canonicalized*.json`(件数が多い場合はINVALID/FAILを含むものだけ集計)。
13. `docs/pm/PM_GOVERNANCE.md` Grep `11-8`→該当節(分類語彙)、Grep `21\. |Existing Spec`→A/B/C分類の節。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `OPEN-526` in `OPEN_ITEMS.md`(行番号のみ。追記文案で参照)。
- Grep `OPEN-5(2[0-9]|3[0-9])` in `OPEN_ITEMS.md`で最大番号を確認→新規OPEN番号=最大+1(現時点でOPEN-528が最新)。新規OPEN行は**文案のみ**RESULT_PACKETへ(11-8分類=「受理面・方式の新設/拡大(ユーザー判断)」+範囲内是正候補があればそれを別項で)。
- Grep `KP HR|R-1` in `docs/pm/OPUS_FINDINGS_LEDGER.md`→指摘ID確認(更新はしない)。
- `docs/pm/ACTIVE_TASK.md`: ファイル全体を上書き(固定ヘッダ書式は`docs/pm/PM_BRIEF.md`「ACTIVE_TASK固定ヘッダ」節どおり。管理ID=KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_01、Status=設計完了・判断候補提示、UDR-blocking=OPEN-526(X HR選択・候補数案A/B/C)・OPEN-527・OPEN-528を維持し本件を追加、当日費用=2026-10-26 約123/1,000)。

## 実行コマンド全文

保全確認(作業前後に各1回、出力をRESULT_PACKETへ貼る):
```
py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01
```
sha確認(前後で不変であること):
```
py -c "import hashlib,sys;[print(p,hashlib.sha256(open(p,'rb').read()).hexdigest()) for p in ['er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/a2/key_phrases/kp_candidates.json','er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/b1b/key_phrases/kp_candidates.json']]"
```
(期待: a2=b030652528b022874940a788abc0cdc187686aacfffe076f5da903c32d6121df、b1b=b3c5f901bddced091650fa22e5cf9910fa0f84e396f783caf2034fbfdca3b4ab。異なれば即STOPして報告)

棚卸しscript(新規・read-only・API 0、`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/tools/kp_exclusion_inventory_01.py`に作成。LLM/TTS clientをimportしない。`er003_key_words_canonicalization.py`の**決定論validator関数のみ**をimportして「修正後候補がGateを通るか」を机上再検査してよい[それがネットワークに触れないことをGrepで確認してから]):
```
py docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\tools\kp_exclusion_inventory_01.py --out docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\inventory_01.json --md docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\EXCLUSION_PATTERNS_01.md
```
出力: 除外パターン別(validate語数/canonicalization Rule7/人称一般化不一致/overflow/重複/本文不一致/その他=理由文字列をそのまま分類)の件数・実例(run・level・句・理由原文)・Family別内訳。

修正案の机上再検査(同scriptに`--recheck <json>`等のサブ機能として実装可。修正候補リストはRESCUE_ANALYSIS_01で人手作成し、既存validator関数に通して通過/不通過と理由を記録):
```
py docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\tools\kp_exclusion_inventory_01.py --recheck docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\rescue_candidates_01.json --out docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\recheck_01.json
```
Production不変確認(作業後):
```
git status --short -- er119_kp_candidates_01.py er119_kp_human_review_01.py er119_kp_human_review_cli_01.py er119_kp_wiring_01.py er119_kp_prompt_2v_01.py er003_key_words_canonicalization.py er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01
```
(期待: 出力なし。作業前にも同コマンドを実行し、既存のdirtyがあればその差分が増えていないことで判定)
secret grep(commit前):
```
git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"
```
(期待: 0件)

## 設計要求(成果物の中身)

`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/`に以下を作成:
1. `SPEC_CHECK_01.md`: PM_GOVERNANCE 21節 A/B/C分類(救済方式は既存仕様あり/過去Trialあり未採用/新規のどれか)。承認済み規則の出典行(5語以下・本文対応・Rule7・人称一般化例外・活用形→基本形例外・数合わせ禁止・最大8・NG復活禁止・重複排除)を「規則/出典(ファイル:行)/実装箇所/X・Y・Zでの適用有無」の表で。**活用形→基本形例外のer119経路適用状況**を独立節で結論(上記「重要な照合点」)。
2. `EXCLUSION_PATTERNS_01.md`(script出力+手直し): ユーザー指定の表「除外パターン/実例/現行の除外理由/修正方法/救済可否/追加コスト」。ユーザーが挙げた観点(5語超過・原形正規化不足・活用/受動/時制・本文対応不備・一般化不足/過剰・重複・その他)の各々について「現行Gateに実在する/実在しない(=LLM側や別段で処理)/発生実績N件」を明記し、実在しないものを実在するかのように書かない。
3. `RESCUE_ANALYSIS_01.md`: 既存データの全除外例について、修正案(機械的/AI判断要)・修正後句・既存validatorでの机上再検査結果・本文対応の保持・重複発生可能性・自然さの所見。集計=救済可能/救済困難/要新規則(ユーザー承認)の3区分件数と救済率。AI島2件は具体案を複数提示: 
   - `too soon to wave a flag`: 例「too soon to wave a flag」を5語以下に切る案(どの部分列が本文対応を保つか: `too soon to`/`wave a flag`/`soon to wave a flag`等、各案の語数・意味の保持・学習価値の違い)、ユーザー例`too soon to do`(動詞を`do`へ一般化=source_spanに無い語を生成するためRule7との関係を明示。現行規則で通るか/新規則が必要か)。
   - `studied separately`: `study separately`(活用形→基本形例外が適用できるか)、`separately`単独、`looked at separately`(b1b側の表現との整合)等。
   どの案を「推奨候補(HR提示)」とするかはAIが決めず、Gate通過可否と理由だけを記す(学習価値の最終選択はユーザー)。
4. `DESIGN_01.md`: 救済フロー(候補抽出→Gate検査→違反検出→修正可能性判断→修正→再検査→HR候補登録)の設計。必須項目: (a)機械的修正で足りるパターンとAI判断(追加LLM call)が必要なパターンの区別と、後者の呼出条件・回数上限・費用見積(単価は出典のある確認済み値のみ。未確認なら「未確認」) (b)再検査=既存Gate関数を同一条件で再適用(新Gateを作らない) (c)記録形式(修正前/修正後/理由/方式[mechanical|llm]/再検査結果)を`kp_candidates.json`とHR依頼書にどう出すか(救済候補はHR表で「修正済み(元: …)」と明示し、ユーザーが元形も見られること) (d)順位・重複排除・最大8・AUTO/NG・外側retry・OPEN-456 F1累積除外との整合(救済候補を累積除外リストと矛盾させない) (e)X/Y/Z共通核での位置(er119候補経路)とFamily固有差(Z全文選定経路の決定論validator等)の整理 (f)70円/セットへの追加コスト見積(機械的のみ案/LLM併用案を分けて) (g)制作速度影響 (h)品質リスク(不自然な英語・本文対応喪失・意味変化)とその歯止め(既存Gate再適用+HR人間選択) (i)**推奨する必要十分な実装案**(段階化: 第1段=承認済み規則内の機械的救済のみ/第2段=新規則[要ユーザー承認]を伴う救済、の2段構成を基本とし、ユーザーが段階ごとに採否を決められる形) (j)残るOpen Item。
   既存仕様と矛盾する案・過剰な制約は書かず、矛盾が避けられない場合は「ユーザー判断事項」として明示。
5. `OPUS_REVIEW_REQUEST_01.md`: 条件A向けの依頼文案(重要論点のみ: 本文対応の定義、Rule7との整合、重複/順位/NG復活禁止との整合、LLM修正の必要最小範囲、X/Y/Z共通核での副作用)。
6. `docs/pm/RESULT_PACKET_KPRS1.md`: 下記「報告」項目。

## SSOT追記文

本委任はSSOTを編集しない。RESULT_PACKETへ以下の**文案**を記す: (1)`OPEN_ITEMS.md`新規行(番号=最大+1、11-8分類付き、Status=DESIGN_DONE_USER_DECISION_PENDING、関連OPEN-526・OPEN-456) (2)範囲内是正候補(活用形→基本形例外のer119経路未適用等)が見つかった場合の別OPEN行文案 (3)`DECISION_LOG.md`は決定なしのため文案不要(Fable判断後に別委任で転記)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **なし**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/USER_DECISION_REGISTER_01.md`は編集・addしない)。
- 明示add対象(pathごとに`git add <path>`、`-A`不可): `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/`配下の作成ファイル(`.md`/`.json`/`tools/*.py`)、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_USER.md`、`..._DELEGATION_01.md`、`..._DELEGATION_01.md_check.json`。`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET_*`はgitignoredのためaddしない。
- commit: `git commit --only <上記path…> -m "KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_01: KP候補Gate除外パターン棚卸し+修正救済方式の設計(X/Y/Z共通、調査・設計のみ、API 0、Production変更0)"`
- push: `git push origin HEAD:main`。non-fast-forwardなら`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は解決せず両方残してSTOP報告。
- commit前にsecret grep 0件を確認。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KPRS1.md`に、(0)T-0結果(抽出index・check PASS/FAIL・reasons) (1)結論1段落(救済可能な除外がどれだけあり、承認済み規則内で救済できる件数と新規則が必要な件数) (2)ユーザー指定表(EXCLUSION_PATTERNS_01の表を転記) (3)ユーザー§6の1〜8を番号対応で各3〜8行 (4)AI島2件の修正案(案ごとに: 修正後句/語数/Gate机上再検査結果/本文対応/自然さ所見/現行規則内か新規則か) (5)活用形→基本形例外のer119経路適用状況の結論(範囲内是正候補か否か、根拠=ファイル:行+ログ) (6)判断候補(Fableが`USER_DECISION_REQUIRED`化する材料: 段階1/段階2の採否、新規則候補の一覧、AI島HR候補へ救済分を今回追加するか[追加する場合に必要な手順と、候補sha再固定・HR round再発行の要否])  (7)保全証拠(status前後・sha前後・`git status --short`結果) (8)API呼出0・費用JPY0の確認(有料clientのimport有無をGrepで示す) (9)commit hash・push結果・変更ファイル一覧とraw.githubusercontent.com URL (10)事前指定Read一覧外の追加Readとその理由 (11)ACTIVE_TASK.md上書き済みの確認 (12)Fable向けの懸念・推奨(1〜3行)。
最終行に `SubagentHandback` 相当の要約(10行以内)を置く。