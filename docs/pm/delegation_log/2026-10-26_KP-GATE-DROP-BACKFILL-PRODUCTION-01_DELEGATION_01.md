## 管理ID

KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01(ユーザー正式採用[APPROVED_FOR_PRODUCTION]の「GateでNG除外されたフレーズ・単語候補の不足分補完」のProduction実装設計。read-only+設計文書+Opus条件Aレビュー依頼文。API 0・JPY0。実装は委任_02)。並行Agent: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_01(フォームWeb移植、`docs/pm/Phrase_Form/`・`user_test/`・`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/`)、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(`er127_*`・TTS leaf)。あなたは本委任でコードを編集しない。所有=`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/{CURRENT_FLOW_01,DESIGN_01,TEST_PLAN_01,EVIDENCE_PLAN_01,BUDGET_PLAN_01,OPUS_REVIEW_REQUEST_01}.md`、`docs/pm/delegation_log/2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_KBF1.md`。SSOT編集権なし。pathspec付きcommit。index.lock競合は10秒待って再実行(最大3回)。ユーザー原文は並行Agent(フォーム)が`docs/pm/delegation_log/2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER.md`へ逐語保存する(§3が本委任の正本。未作成なら本委任文の下記引用を使う)。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様の新処理フロー設計(PM_GOVERNANCE 11-3 条件A=**Opus必須レビュー対象**。実装前にOpusへ)。到達上限Status=DESIGN_READY。
- 禁止: コード/SSOT編集、有料API、7+5候補生成PromptのProduction採用を前提にした設計(現行Production=call1 Prompt 2[3件]+call2 Prompt 2-V[最大5]、Adv単語解説=`run_vocab_selection`。補完はこの**現行経路**と、将来7+5が採用された場合の両方に矛盾なく適用できる抽象で設計)、Gate緩和・品質基準変更、「初回選定件数が上限未満」での発動、救済済み候補を除外と数える設計、禁止Git操作。
- 費用/日次: JPY0(本委任)。委任_02実装=API 0、委任_03 evidence=Family X/Y/Z×Std/Adv(見積を本委任で算出。1 level≈¥2〜3、除外を確実に起こすためのreplay/既知事例活用で合計≤¥30を目標)。
- 修正範囲の線引き(11-8): 範囲内=承認原文§3-1〜3-3の補完機構(発動条件・件数・重複/同NG防止・Gate再適用・救済との順序・HR/retry/fallback/resume/再生成整合・単語優先順位)。範囲外=候補生成Prompt本体の変更、Gate変更(含有語`duplicate_of_top3`の扱いは現行維持。承認原文「未承認のGate緩和を行わない」)、採用枠。
- 時間見込み: 約2.5h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1: 従来どおり。T-0: 委任文保存+`check_delegation_prompt.py`、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: TTSなし。T-3: 費用なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_01.md` をN=685から順に試し、先頭「## 管理ID」+「KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01」のものを採用(同時刻にフォーム委任あり、先頭一致必須)。

## ユーザー指示(該当部・逐語)

### 3. Gate除外候補の補完機能

#### 3-1. 発動条件（最重要）

**補完は、AIが一度選定した候補が後続GateでNG除外された場合に限る。**

単に初回選定件数が上限未満という理由で発動させないこと。

具体例：

| 初回AI選定 | Gate除外 | 補完 |
|---|---|---|
| フレーズ5件／最大7件 | 0件 | なし |
| フレーズ7件／最大7件 | 2件 | 最大2件 |
| 単語4件／最大5件 | 0件 | なし |
| 単語5件／最大5件 | 1件 | 最大1件 |

**補完件数＝実際にGateで除外された件数。**

対象はフレーズ・単語の両方。

初回に合格した候補は保持し、再生成・入れ替えをしない。

#### 3-2. 補完処理

- 除外件数だけ追加候補を探索する。
- 初回候補・既存合格候補を踏まえ、重複や同じNGの繰り返しを防ぐ。
- 補完候補にも承認済みの品質基準・Gateを適用する。
- 補完候補が不合格でも品質基準を緩和しない。
- 見込みのない同一処理の反復を避ける。
- 補完後も上限未達なら、その結果を許容する。

既存のKP救済方式と処理順序を確認すること。

救済によって正式な候補として残ったものを、誤って「Gate除外」と数えて補完しないこと。

Human Review限定候補、Human NG、retry、fallback、resume、再生成との整合を確認する。

既存の正式な候補生成経路だけでなく、必要な後続経路にも矛盾なく組み込む。

#### 3-3. 単語抽出の優先順位

単語の初回抽出・補完抽出とも、ユーザー指定の優先順位を厳守する。

1. 本文一致（絶対条件）
2. 1語（絶対条件）
3. 上級者向けの学習価値
4. 易しい語の除外
5. 単語単体の学習価値（必須条件ではない）

過去の7＋3 Trialで発生した、条件⑤の必須化・優先順位逆転を再発させないこと。

フレーズに含まれる単語の重複扱いについては、既存Production Gateと承認済み仕様の整合を確認する。未承認のGate緩和を行わない。

### 4.(抜粋)

なお、今回承認されたのは「7＋5方式の候補上限を前提とする選定フォーム」と「Gate除外分の補完」である。過去の7＋5 Trialで判明した数合わせ品質問題を無視して、7＋5候補生成Prompt自体のProduction採用を自動確定してはならない。新しい候補生成Prompt、採用枠、Gate変更が必要になった場合は、既存承認の範囲と区別して報告すること。

### 6. 受入条件(抜粋、補完関連)

2. 正式候補生成経路におけるGate除外・補完の動作証拠 3. Gate除外0件では補完が発動しないこと 4. 初回選定が上限未満でも補完が発動しないこと 5. 補完後のGate再検査と重複防止 6. retry／fallback／resume／Human Review／KP救済との整合 7. 必須Regression／Validator／Integration Test PASS 8. actual model_id、Prompt、routing等のruntime evidence

(引用ここまで)

## Fableの設計指示

1. **現行フロー(`CURRENT_FLOW_01.md`)**: 共通KP経路(`er119_kp_candidates_01.py generate_candidates`: call1 Prompt 2=3件→call2 Prompt 2-V=最大5件→selection gate[validate: 本文連続一致・1〜5語・有限助動詞・数値/CMU/containment]→canonicalization(`er003_key_words_canonicalization`、`run_key_phrase_canonicalization(rescue=)`で**救済**[er125: revert/M1/D1/慣用句核/gloss再整合/QA再判定/`RESCUED`旗/`rescued_not_auto`])→gloss→RQA→HR候補(`KP_CANDIDATE_MAX=8`)→外側retry条件`n_auto<3 and (gate_dropped or 救済済みauto不可あり)`)、Adv単語解説=`run_vocab_selection`(`_containment`、`duplicate_of_top3`)、X/Y/Zの呼出点(`er019`/`er121:572`/`er063`)、HR Lock・Human NG(`match_ng`)・resume(読み戻し)・`--regenerate-stage`。**既存の外側retry(現在のProduction「補完」相当)との関係を精査**: 現行外側retryは「auto候補<3かつ除外あり」で候補生成全体を再実行する=ユーザー原文の「初回合格候補は保持し再生成・入れ替えをしない」と矛盾する可能性。事実を特定し、補完機構導入時の外側retryの扱い(撤去/条件変更/併存)を設計案として提示(**承認済み仕様の変更に当たるか**を11-8で分類。当たるならユーザー判断候補として切り分け)。
2. **設計(`DESIGN_01.md`)**: (a)除外カウント=「AIが選定し、selection gate/CMU/canonicalization[救済不成立]/gloss/RQA等の**後続Gateで最終的に除外**された候補数」。救済成立(auto可・HR限定の双方)は除外に数えない。containment(`duplicate_of_top3`)除外は現行Gateどおり除外に数える(Gate緩和しない)。初回返答が上限未満=発動なし。(b)補完call=区分別(フレーズ/単語)に、除外件数だけを要求する追加Prompt。**新Promptの追加はユーザー原文§4「新しい候補生成Promptが必要になった場合は区別して報告」に該当**するため、既存Prompt 2-V/Prompt 2(およびTrial-02で是正済みのW5順序)を「除外語リスト+既存合格リストを与え、件数Nだけ」の形で再利用できるかを第一候補とし、できなければ新Prompt(最小差分)として区別報告。単語優先順位①〜⑤順を厳守(⑤必須化禁止)。(c)重複・同NG防止=除外候補・既存合格候補・救済済み候補を`already`として渡し、返答の重複は補完せず捨てる。補完候補にも同一Gate(救済含む)を適用。補完は**1回のみ**(反復しない)。補完後も上限未達は許容。(d)順序=初回→Gate(救済含む)→除外確定→補完call→補完候補にGate(救済含む)→HR候補確定。救済済みHR限定候補は保持。(e)HR/Human NG/retry/fallback/resume/再生成整合: `match_ng`はHuman NGを補完候補にも適用、resumeは補完結果を読み戻し(再課金なし)、`--regenerate-stage`では初回から。(f)X/Y/Z共通核への配線点(H1〜H4相当)・kill switch(単一読取関数・既定ON=承認済み仕様のため)・A/B/C不変。(g)現行3+最大5経路と将来7+5経路の両対応(上限は引数)。(h)`KP_CANDIDATE_MAX=8`との関係(補完は上限を超えない)。
3. **test計画(`TEST_PLAN_01.md`)**: 受入条件3〜7の各ケース(除外0→不発動、上限未満→不発動、除外2→最大2、救済成立は数えない、重複は捨てる、Gate再適用、Human NG、resume再課金0、A/B/C golden、X/Y/Z配線静的test)。
4. **evidence計画+見積(`EVIDENCE_PLAN_01.md`/`BUDGET_PLAN_01.md`)**: Family X/Y/Z×Std/Advで「除外あり→補完発動」と「除外0→不発動」を正式経路で観測する方法(既知除外事例の記事=AI島Std[6語/canonicalization除外]、英国Std[数字]、猿の手[過去形]を活用。KP stage限定起動、`--regenerate-stage`、HR候補保全のため**新run dir**)。見積(1 level≈¥2〜3、合計≤¥30目標)。
5. **Opus論点(`OPUS_REVIEW_REQUEST_01.md`)**: 発動条件の判定点(救済との順序・除外の定義)/外側retryとの関係/Prompt再利用vs新Prompt/重複・同NG防止の十分性/resume・regenerate整合/A/B/C不変/evidence十分性。

## 事前指定Read一覧

- `er119_kp_candidates_01.py`: Grep `def generate_candidates|n_auto|gate_dropped|run_vocab_selection|_containment|duplicate_of_top3|KP_CANDIDATE_MAX|already` → ±20
- `er119_kp_prompt_2v_01.py`(構造)、`er119_kp_human_review_01.py:40-60,540-560`
- `er125_kp_rescue_production_01.py`: Grep `def |RESCUED|rescued_not_auto|rescue_enabled` → 関数一覧±5
- `er003_v1_n3_01_scaffold_generate.py:460-490`(`run_key_phrase_canonicalization(rescue=)`)
- `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/{DESIGN_03,EVIDENCE_01}.md`(配線点H1〜H4・順序)
- `docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/{PROMPT_DIFF_01,COMPARISON_02}.md`(W5順序是正Prompt・含有語Gateの食い違い)
- `CURRENT_SPEC.md`: Grep `KP救済|Key Phrase候補|KP_CANDIDATE_MAX|外側retry|n_auto` → ±8
- `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/KP_CANDIDATE_COUNT_CHECK_01.md`(補充機構なしの現状・案A/B/C)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_DELEGATION_01.md_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_KBF1.md`(9)にOPEN新規起票文案(補完機構=APPROVED_FOR_PRODUCTION・DESIGN_READY)、OPEN-526案A/B/Cとの関係(ユーザー採用により案B相当が承認されたか=**原文§3-1は「除外時のみ」であり、AI島のStd5/Adv7[除外2/0]では除外分のみ補完対象。初回返答数不足分は補完しない**ことを明記)、判断候補(外側retryの扱い等)。

## Git

- add対象: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/`、delegation_log。pathspec付きcommit。
- commit message: `KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01: Gate除外候補補完のProduction設計(現行フロー・発動条件・救済順序・外側retry関係・test/evidence計画・Opus依頼、API 0)`
- trailer: `Delegation: KP-GATE-DROP-BACKFILL-PRODUCTION-01/01`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_KBF1.md`: (0)T-0、(1)現行フローと外側retryの事実、(2)設計要点(a)〜(h)、(3)新Prompt要否の判定(既存Prompt再利用可否)、(4)test/evidence/費用計画、(5)Opus論点、(6)判断候補(承認範囲と区別して報告すべき事項)、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、(9)一覧外Read、commit hash、raw URL。末尾10行要約。